# Utført-linja for UX-statusen

## 2026-11-03 kl. 22:39 — Marian Osen

### Oppgave
Skrive Utført-linja som manglet for instruksjonen kl. 21:49 (status for funnene til 8.2 i UX-loggen). Linja manglet fordi økta ble tømt kl. 22:34, da blokka for 8.2b ble limt inn for tidlig og stoppet i steg 0. Bare dagsfila og sesjonsloggen skulle endres.

### Plan
- Kvoten (regel 15) og steg 0: main, `git pull --ff-only`, ren arbeidskopi, og ingen Utført-linje under kl. 21:49.
- Instruksjonen lagret i dagsfila 03.11 og pushet.
- Slått opp `37390b4d`, `3967bddb`, `dc027575`, tallene i seksjonen «Status for funnene til 8.2, sjekket 03.11» og CI-kjøringen på `dc027575` med `gh`.
- Utført-linja og en datert merknad om 8.2b rett under instruksjonen kl. 21:49.

### Resultat
- Kvoten kl. 22:37 (21:37 GMT): `apiRequests` 20 med `apiRequestsDate` 2026-11-03, så 20 brukt og 0 igjen i dag i GMT, og `extraLimit` 463. Ingen andre kall.
- `67fb4629` (22:37): instruksjonen kl. 22:37 i dagsfila. `e0a25f80` (22:39): Utført-linja for kl. 21:49 og merknaden om at 8.2b limes inn på nytt etter kl. 23:50.
- Tallene i seksjonen: løst 7, delvis 3, står 34, må ses på siden 1, i alt 45.
- CI 41721045399 på `dc027575`: `pytest`, `docker` og Windows er grønne. `dobbeltklikk (macos-latest)` ble avbrutt etter 901 s med 0 steg, så kjøringen er ikke grønn. Den er ikke kjørt på nytt.
- Testene for dokumentene ga 255 bestått før hver push. Kontroll mot HEAD: bare `updated` er fjernet.
- Første forsøk på å sette inn linja havnet inne i kodeblokka og hadde et gjettet nummer på loggfila (984). Det ble rettet med `git checkout` av fila og en ny innsetting før commit. Loggfila er 981.

### Åpne punkter
- Blokka for 8.2b limes inn på nytt etter kl. 23:50.
- macOS-jobben fikk ikke maskin på `dc027575` heller (41721045399), som tidligere 3.11.
