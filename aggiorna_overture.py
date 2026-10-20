#!/usr/bin/env python3
"""
Pets – scarica da Overture Maps (dati aperti, licenza CDLA Permissive 2.0) i veterinari, le cliniche
veterinarie e le pensioni per animali in Italia e li salva in un file JSON che aggiorna_animali.js unisce ai punti
di OpenStreetMap, togliendo quelli che OpenStreetMap ha già.

Su OpenStreetMap mancano molti veterinari e quasi tutte le pensioni; Overture raccoglie anche i dati di Meta,
Microsoft e altri.
Legge solo le parti dei file di Overture che coprono l'Italia (i file sono ordinati per zona).

Uso: python3 aggiorna_overture.py FILE_USCITA     (serve: pip install pyarrow fsspec aiohttp)
"""
import json, os, re, sys, time, urllib.request
import fsspec
import pyarrow.parquet as pq

BASE = "https://overturemaps-us-west-2.s3.us-west-2.amazonaws.com/"
X0, Y0, X1, Y1 = 6.6, 35.4, 18.6, 47.1          # riquadro dell'Italia
# categorie di Overture → tipo dell'app (S pronto soccorso veterinario, V veterinario, B pensione per animali)
CATEGORIE = {"veterinarian": "V", "veterinary_care": "V", "animal_hospital": "V", "emergency_pet_hospital": "S",
             "pet_boarding": "B"}
# Molte pensioni su Overture hanno un'altra categoria (servizi per animali, allevamenti, addestratori, dog sitter,
# a volte perfino veterinari o alberghi): si riconoscono dal nome
RE_PENSIONE = re.compile(r"pension[ei]|\bhotel\b|\bresort\b|asilo (per|e|diurno)|\b(dog|pet|cat)s? ?(village|camp)\b", re.I)
# nomi che dicono chiaramente "pensione per animali", qualunque sia la categoria (anche albergo)
RE_PER_ANIMALI = re.compile(r"\b(pets?|dogs?|cats?|gatto|bau|miao) ?hotel\b|\bper (cani|gatti|animali)\b|"
                            r"pension[ei]\b.*\b(cani|gatti|animali|felin[aei])\b", re.I)
RE_CLINICA = re.compile(r"veterinari|clinica|ambulatorio|ospedale", re.I)
# tra le "pet_boarding" di Overture ci sono anche case vacanze e agenzie: si scartano dal nome
RE_NON_PENSIONE = re.compile(r"casa vacanz|case vacanz|affitt|appartament|holiday|immobiliar|"
                             r"\bno pension", re.I)
GRUPPI_ANIMALI = {"animal_or_pet_service", "animal_and_pet_store"}
# punti segnalati come sbagliati: identificativo dell'app → motivo
ESCLUSI = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "overture_esclusi.json")))["esclusi"]
COLONNE = ["id", "confidence", "websites", "phones", "addresses", "names", "operating_status", "taxonomy", "bbox"]


def elenco(prefisso, delimitatore=True):
    """Chiavi (o sottocartelle) del bucket pubblico di Overture con quel prefisso."""
    url = BASE + "?list-type=2&prefix=" + prefisso + ("&delimiter=/" if delimitatore else "")
    xml = urllib.request.urlopen(url, timeout=60).read().decode()
    return re.findall(r"<Prefix>([^<]+)</Prefix>" if delimitatore else r"<Key>([^<]+)</Key>", xml)


def tipo(tassonomia, nome):
    """Tipo dell'app per un luogo di Overture, oppure None."""
    k = tipo_da_categoria(tassonomia, nome)
    return None if k == "B" and RE_NON_PENSIONE.search(nome) else k


def tipo_da_categoria(tassonomia, nome):
    primaria = tassonomia.get("primary") or ""
    k = CATEGORIE.get(primaria)
    if k == "B" or not RE_PENSIONE.search(nome):
        return k
    if RE_CLINICA.search(nome):
        return k
    if GRUPPI_ANIMALI & set(tassonomia.get("hierarchy") or []) or RE_PER_ANIMALI.search(nome):
        return "B"
    return k


def main():
    uscita = sys.argv[1]
    versioni = sorted(p for p in elenco("release/") if re.match(r"release/\d{4}-\d{2}-\d{2}", p))
    versione = versioni[-1]
    file = [k for k in elenco(versione + "theme=places/type=place/", False) if k.endswith(".parquet")]
    print(f"Overture {versione}: {len(file)} file", flush=True)
    fs = fsspec.filesystem("https", client_kwargs={"trust_env": True})
    punti, gruppi, inizio = [], 0, time.time()
    for chiave in file:
        f = pq.ParquetFile(fs.open(BASE + chiave, block_size=2**22))
        md = f.metadata
        nomi = [md.row_group(0).column(i).path_in_schema for i in range(md.num_columns)]
        ix = {n: nomi.index("bbox." + n) for n in ("xmin", "xmax", "ymin", "ymax")}
        for g in range(md.num_row_groups):
            rg = md.row_group(g)
            st = {n: rg.column(i).statistics for n, i in ix.items()}
            if any(s is None or s.min is None for s in st.values()):
                continue
            if st["xmin"].min > X1 or st["xmax"].max < X0 or st["ymin"].min > Y1 or st["ymax"].max < Y0:
                continue
            gruppi += 1
            for r in f.read_row_group(g, columns=COLONNE).to_pylist():
                k = tipo(r["taxonomy"] or {}, (r["names"] or {}).get("primary") or "")
                if not k or r["operating_status"] == "permanently_closed":
                    continue
                ind = (r["addresses"] or [{}])[0] or {}
                if ind.get("country") != "IT":
                    continue
                if "o" + r["id"][:16] in ESCLUSI:
                    continue
                b = r["bbox"]
                p = {"i": "o" + r["id"][:16], "k": k, "la": round((b["ymin"] + b["ymax"]) / 2, 6),
                     "lo": round((b["xmin"] + b["xmax"]) / 2, 6), "f": "o"}
                for chiave_p, v in (("n", (r["names"] or {}).get("primary")), ("a", ind.get("freeform")),
                                    ("c", ind.get("locality")), ("t", (r["phones"] or [None])[0]),
                                    ("w", (r["websites"] or [None])[0])):
                    if v and v.strip():
                        p[chiave_p] = v.strip()
                punti.append(p)
    with open(uscita, "w") as out:
        json.dump({"versione": versione.split("/")[1], "punti": punti}, out)
    print(f"  {len(punti)} punti ({sum(p['k'] == 'B' for p in punti)} pensioni) da {gruppi} blocchi in {time.time() - inizio:.0f} s", flush=True)


if __name__ == "__main__":
    main()
