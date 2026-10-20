// Diagnosi temporanea: dopo aggiorna_animali.js, conta le pensioni nei dati e ne mostra alcune vicino a città note.
"use strict";
const fs = require("fs"), path = require("path"), PT = require("../core.js");
const dir = path.join(__dirname, "..", "dati");
const indice = JSON.parse(fs.readFileSync(path.join(dir, "indice.json"), "utf8"));
console.log("perTipo:", JSON.stringify(indice.perTipo), "overture:", indice.overture);
const tutti = indice.tessere.flatMap((t) => JSON.parse(fs.readFileSync(path.join(dir, t), "utf8")).d);
const B = tutti.filter((p) => p.k === "B");
console.log(`pensioni: ${B.length} (OSM ${B.filter((p) => p.f !== "o").length}, Overture ${B.filter((p) => p.f === "o").length})`);
const CITTA = { Pavia: [45.1847, 9.1582], Milano: [45.4642, 9.19], Roma: [41.9028, 12.4964], Napoli: [40.8518, 14.2681], Torino: [45.0703, 7.6869], Palermo: [38.1157, 13.3615] };
for (const [c, [la, lo]] of Object.entries(CITTA)) {
  const vicini = B.map((p) => ({ ...p, d: PT.distanza(la, lo, p.la, p.lo) })).filter((p) => p.d < 15000).sort((a, b) => a.d - b.d);
  console.log(`\n${c}: ${vicini.length} pensioni entro 15 km (${vicini.filter((p) => p.d < 5000).length} entro 5 km)`);
  for (const p of vicini.slice(0, 15)) console.log(`  ${(p.d / 1000).toFixed(1)} km  ${p.f === "o" ? "Overture" : "OSM     "}  ${p.n || "-"} | ${p.c || ""}`);
}
// nuova anteprima
