#!/usr/bin/env python3
"""Diagnosi temporanea: categorie di Overture Maps legate agli animali in Italia, con quanti punti e qualche nome."""
import collections, re, sys, time
sys.path.insert(0, ".")
import fsspec, pyarrow.parquet as pq
from aggiorna_overture import BASE, X0, Y0, X1, Y1, elenco

RE_CAT = re.compile(r"pet|animal|dog|cat_|kennel|boarding|veterin|groom|horse|equine", re.I)
RE_NOME = re.compile(r"pension[ei].*(cani|gatti|animal|felin|4 ?zampe|quattro ?zampe)|dog ?hotel|pet ?hotel|cat ?hotel|"
                     r"hotel per (cani|gatti|animali)|(dog|pet|cat) ?sitt|asilo per cani", re.I)
versioni = sorted(p for p in elenco("release/") if re.match(r"release/\d{4}-\d{2}-\d{2}", p))
versione = versioni[-1]
file = [k for k in elenco(versione + "theme=places/type=place/", False) if k.endswith(".parquet")]
print(versione, len(file), "file", flush=True)
fs = fsspec.filesystem("https", client_kwargs={"trust_env": True})
cat, esempi, pernome, gerarchie, inizio = collections.Counter(), collections.defaultdict(list), collections.Counter(), {}, time.time()
nomi_trovati = []
for chiave in file:
    f = pq.ParquetFile(fs.open(BASE + chiave, block_size=2**22))
    md = f.metadata
    nomi = [md.row_group(0).column(i).path_in_schema for i in range(md.num_columns)]
    ix = {n: nomi.index("bbox." + n) for n in ("xmin", "xmax", "ymin", "ymax")}
    for g in range(md.num_row_groups):
        st = {n: md.row_group(g).column(i).statistics for n, i in ix.items()}
        if any(s is None or s.min is None for s in st.values()):
            continue
        if st["xmin"].min > X1 or st["xmax"].max < X0 or st["ymin"].min > Y1 or st["ymax"].max < Y0:
            continue
        for r in f.read_row_group(g, columns=["names", "addresses", "taxonomy", "operating_status"]).to_pylist():
            ind = (r["addresses"] or [{}])[0] or {}
            if ind.get("country") != "IT":
                continue
            tx = r["taxonomy"] or {}
            prim = tx.get("primary") or ""
            nome = (r["names"] or {}).get("primary") or ""
            if RE_CAT.search(prim):
                cat[prim] += 1
                gerarchie[prim] = tx.get("hierarchy")
                if len(esempi[prim]) < 12:
                    esempi[prim].append(f"{nome} ({ind.get('locality')})")
            if RE_NOME.search(nome):
                pernome[prim] += 1
                if len(nomi_trovati) < 300:
                    nomi_trovati.append(f"{prim} | {nome} | {ind.get('locality')}")
print(f"\n===== categorie legate agli animali ({time.time() - inizio:.0f} s) =====")
for c, n in cat.most_common():
    print(f"{n:6d}  {c}  {gerarchie.get(c)}")
    for e in esempi[c]:
        print("          ", e)
print("\n===== nomi da pensione, per categoria =====")
for c, n in pernome.most_common():
    print(f"{n:6d}  {c}")
for x in nomi_trovati:
    print("   ", x)
