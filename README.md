# Pets

Web app per il telefono che mostra i servizi per gli animali domestici vicino a te presi da OpenStreetMap:
pronto soccorso veterinari, veterinari e cliniche veterinarie, farmacie e parafarmacie veterinarie, negozi per
animali, toelettature, aree cani, canili e rifugi, pensioni per animali, fontanelle e abbeveratoi e altro (addestramento, allevamenti).
Stesso aspetto e funzionamento di [Distributori](https://github.com/paolo1957-it/Distributori) e
[Salus](https://github.com/paolo1957-it/Salus).

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
- Su OpenStreetMap mancano molti veterinari: quando riscarica i dati, `aggiorna_animali.js` esegue anche
  `aggiorna_overture.py`, che prende da [Overture Maps](https://overturemaps.org) (licenza CDLA Permissive 2.0)
  veterinari e cliniche veterinarie in Italia; si aggiungono solo quelli che non sono già su OpenStreetMap
  (entro 60 m, o 300 m con un nome simile). Se Overture non risponde si usa solo OpenStreetMap.
- La cartella `dati/` **non** sta nel repository. Se il sito non ha i dati, l'app li chiede direttamente a Overpass.

## Pubblicazione

Impostazioni del repository → Pages → Source: **GitHub Actions**.
Per riscaricare subito i dati: Actions → *Pubblica sito e aggiorna dati* → *Run workflow*.

## File

- `index.html`, `style.css`: interfaccia
- `core.js`: logica (tipi di punto, orari di apertura, distanze, tessere)
- `app.js`: mappa, GPS, elenco, impostazioni
- `config.js`: impostazioni iniziali e numero di versione
- `aggiorna_animali.js`, `aggiorna_overture.py`, `.github/workflows/pubblica.yml`: scaricamento dei dati e pubblicazione
- `sw.js`, `manifest.webmanifest`, `icon.svg`: installazione come app

## Fonte dei dati

© OpenStreetMap e chi contribuisce (licenza ODbL). Veterinari anche da Overture Maps Foundation (licenza CDLA Permissive 2.0). Le informazioni sono inserite da volontari e possono
essere incomplete o non aggiornate.
