#!/usr/bin/env node
// Diagnosi temporanea: quante pensioni per animali ci sono su OpenStreetMap in Italia, e con quali tag.
"use strict";
const SERVER = ["https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter",
  "https://maps.mail.ru/osm/tools/overpass/api/interpreter"];
const AREA = '[out:json][timeout:600];area["ISO3166-1"="IT"][admin_level=2]->.zona;';
const NOMI = "pension[ei].*(cani|gatti|animal|felin|amici|4 ?zampe|quattro ?zampe|fido|pet)|(dog|cat|pet|cani|gatti|fido)[ -]?(hotel|resort|house|village|sitter|sitting|club|camp|park|ranch|farm)|hotel per (cani|gatti|animali)|albergo per (cani|gatti|animali)|asilo per cani|(dog|pet|cat)[ -]?sitt|kennel|dog ?daycare|centro cinofilo|allevamento|addestramento";
const QUERY = {
  "amenity=animal_boarding": AREA + "nwr(area.zona)[amenity=animal_boarding];out center tags;",
  "chiave animal_boarding=*": AREA + "nwr(area.zona)[animal_boarding];out center tags;",
  "nome": AREA + `nwr(area.zona)[name~"${NOMI}",i];out center tags;`
};
async function chiedi(q) {
  for (const url of SERVER) {
    try {
      const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Pets/1.0 (diagnosi pensioni)" }, body: "data=" + encodeURIComponent(q), signal: AbortSignal.timeout(11 * 60000) });
      if (!r.ok) throw new Error("HTTP " + r.status);
      const d = await r.json();
      if (d.remark) console.log("  remark:", d.remark);
      return d.elements;
    } catch (e) { console.log(`  ${url}: ${e.message}`); }
  }
  return null;
}
const principale = (t) => ["amenity", "shop", "leisure", "tourism", "office", "craft", "club", "landuse", "building"]
  .filter((k) => t[k]).map((k) => k + "=" + t[k])[0] || "(nessuno)";
(async () => {
  for (const [nome, q] of Object.entries(QUERY)) {
    console.log(`\n===== ${nome} =====`);
    const el = await chiedi(q);
    if (!el) { console.log("  nessuna risposta"); continue; }
    console.log(`  ${el.length} elementi`);
    const conta = {};
    for (const e of el) { const k = principale(e.tags || {}); conta[k] = (conta[k] || 0) + 1; }
    console.log("  per tag principale:", JSON.stringify(Object.entries(conta).sort((a, b) => b[1] - a[1]).slice(0, 40)));
    for (const e of el.slice(0, 400)) {
      const t = e.tags || {};
      console.log(`  ${e.type[0]}${e.id} | ${principale(t)} | ${t.name || "-"} | ${t["addr:city"] || ""} | ` +
        Object.keys(t).filter((k) => /animal|dog|cat|boarding/.test(k)).map((k) => k + "=" + t[k]).join(" "));
    }
  }
})();
