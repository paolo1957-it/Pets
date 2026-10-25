# Pets

Web app per il telefono che mostra i servizi per gli animali domestici vicino a te presi da OpenStreetMap:
pronto soccorso veterinari, veterinari e cliniche veterinarie, farmacie e parafarmacie veterinarie, negozi per
animali, toelettature, aree cani, canili e rifugi, pensioni per animali, fontanelle e abbeveratoi e altro (addestramento, allevamenti).
Stesso aspetto e funzionamento di [Distributori](https://github.com/paolo1957-it/Distributori) e
[Salus](https://github.com/paolo1957-it/Salus).

Nella cartella [`trekking/`](trekking/) c'è **Qui-Trekking**, con lo stesso aspetto: sentieri CAI con difficoltà,
lunghezza, dislivello e segnavia, rifugi e fontanelle (pubblicata in `…/Pets/trekking/`).

## Come funziona

- I segnaposto hanno un colore e un simbolo per tipo; un pallino verde o rosso dice se è aperto adesso,
  calcolato dagli orari (`opening_hours`) scritti su OpenStreetMap.
- Il pulsante rosso **PS** porta al pronto soccorso veterinario più vicino, quello verde (la zampa) al veterinario
  più vicino aperto. Un veterinario è "pronto soccorso" se su OpenStreetMap ha `emergency=yes`, "pronto soccorso"
  o "h24" nel nome, oppure orario `24/7`.
- A ogni pubblicazione GitHub esegue `aggiorna_animali.js` (workflow `.github/workflows/pubblica.yml`):
  scarica da Overpass tutti i punti d'Italia e li salva nella cartella `dati/` del sito pubblicato,
  divisi in tessere da 0,25° (circa 28 × 20 km). Per non pesare su Overpass li riscarica al massimo una volta
  ogni 20 ore; nel frattempo ricopia quelli già pubblicati.
- Su OpenStreetMap mancano molti veterinari e quasi tutte le pensioni: quando riscarica i dati, `aggiorna_animali.js` esegue anche
  `aggiorna_overture.py`, che prende da [Overture Maps](https://overturemaps.org) (licenza CDLA Permissive 2.0)
  veterinari, cliniche veterinarie e pensioni per animali in Italia (le pensioni anche dal nome, perché su Overture
  hanno spesso un'altra categoria); si aggiungono solo quelli che non sono già su OpenStreetMap
  (entro 60 m, 300 m con un nome simile o 1 km con lo stesso nome). Se Overture non risponde si usa solo OpenStreetMap.
  I punti di Overture segnalati come sbagliati si tolgono aggiungendo il loro identificativo in `overture_esclusi.json`.
- La cartella `dati/` **non** sta nel repository. Se il sito non ha i dati, l'app li chiede direttamente a Overpass.
- Statistiche d'uso anonime, senza cookie, con [GoatCounter](https://www.goatcounter.com): si vedono su
  https://pets.goatcounter.com (stesso login delle altre app).

## Pubblicazione

Impostazioni del repository → Pages → Source: **GitHub Actions**.
Per riscaricare subito i dati: Actions → *Pubblica sito e aggiorna dati* → *Run workflow*.

## File

- `index.html`, `style.css`: interfaccia
- `core.js`: logica (tipi di punto, orari di apertura, distanze, tessere)
- `app.js`: mappa, GPS, elenco, impostazioni
- `config.js`: impostazioni iniziali e numero di versione
- `aggiorna_animali.js`, `aggiorna_overture.py`, `.github/workflows/pubblica.yml`: scaricamento dei dati e pubblicazione
- `sw.js`, `manifest.webmanifest`: installazione come app
- `icon-192.png`, `icon-512.png`, `favicon-64.png`, `apple-touch-icon.png`, `icon-maskable-512.png`: logo Qui-Pets in PNG

## Notifica sull'iPhone

Alla fine di ogni giro il workflow può mandare una notifica con l'app gratuita **ntfy** (App Store):
✅ dati riscaricati, ❌ aggiornamento fallito (anche solo lo scaricamento), ⚠️ OpenStreetMap non ha risposto e
sono rimasti i dati vecchi. Per attivarla: Settings → Secrets and variables → Actions → *New repository secret*
`NTFY_TOPIC` con il nome del canale, e nell'app ntfy iscriversi allo stesso canale. Senza il secret la notifica viene saltata.

## Fonte dei dati

© OpenStreetMap e chi contribuisce (licenza ODbL). Veterinari e pensioni anche da Overture Maps Foundation (licenza CDLA Permissive 2.0). Le informazioni sono inserite da volontari e possono
essere incomplete o non aggiornate.
