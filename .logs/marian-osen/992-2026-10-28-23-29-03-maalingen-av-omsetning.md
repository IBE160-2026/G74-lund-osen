# Målingen av omsetning hver kveld (story 2.13)

## 2026-10-28 kl. 23:29 — Marian Osen

### Oppgave
Instruksjonen kl. 22:38: bygge story 2.13 i natt etter gruppens svar kl. 22:17. Valget `--maal-omsetning` i hentekommandoen skal måle de neste aksjene i lista over Oslo Børs med kallene som er igjen hver kveld, aldri med bonuskvoten. Jobben fra 2.3d skal kjøre det etter hentingen. Arbeidet stopper alltid før flettingen.

### Plan
- Steg 0–1: kvotesjekken, instruksjonen i dagsfila og avgjørelsen kl. 22:17 under 2.13 og 8.17 på main.
- Steg 2: grenen `2-13-maalingen-av-omsetning` i en egen worktree, spesifikasjonen (`_bmad-output/implementation-artifacts/spec-2-13-maalingen-av-omsetning.md`) og PR #105, så koden, testene og dokumentene.
- Steg 3: hele settet alene, mutanten, gjennomgangen med tre lesere, triagen, rettingene og CI.

### Resultat
- **Kvoten** kl. 22:38: 20 av 20 brukt 28.10 i GMT, `extraLimit` 463. Ingen andre kall.
- **Main:** instruksjonen i `a5014747`, avgjørelsen kl. 22:17 under 2.13 og 8.17 i `4e985641`.
- **Grenen**, PR #105 (utkast):
  - Spesifikasjonen i `41d39bc`.
  - Koden i `ab7b9678`: `src/omsetning.py`, `0008_omsetning.sql` (tabellen `omsetning`), valget i `fetch_prices.py`, `start/kveldshenting.ps1`, `tests/test_omsetning.py`, README-en, hjelpen, linja under FR-413 og avtrykket bak bildet av aksjesiden (bildet tatt på nytt, byte for byte likt).
  - Rettingene etter gjennomgangen i `fda73fd8`, og triagen i `e6287bf8`.
- **Minnet:** 4,3 GB ledig av 15,7 GB.
- **Hele settet:** 3849 bestått, 24 hoppet over og 0 feilet (22:57:49–23:05:44). Etter rettingene: 3861 bestått, 24 hoppet over og 0 feilet (23:16:23–23:24:49).
- **Mutanten** (stoppen ved endret `extraLimit` tatt ut) ble fanget begge gangene av `test_stopper_naar_extraLimit_endres_etter_et_kall`, og fila var lik HEAD etterpå.
- **Gjennomgangen:** BH 13, ECH 13 og VG 12 funn. Rettet: VG1 (high), BH3/ECH1, ECH3, BH4, VG3, VG4 og VG5, samt de fleste med dom low. BH2 er avvist etter oppslag.
- **CI** feilet på `ab7b967` (40777327364): Docker svarte på runneren, så testen for hele jobben fikk «Stopper Ollama». Den er grønn på head-en `e6287bf` (40779900164).
- `data/db/ose.db` og `.env` er ikke rørt, utenom lesingen av nøkkelen til kvotesjekken. Demobasen for bildet lå i en midlertidig mappe, som er slettet.

### Åpne punkter
- Gruppen avgjør før flettingen: datoen før første kall (en tidligere `apiRequestsDate` godtas som 0 brukt, så målingen går i helgene).
- Gruppen avgjør før flettingen: vinduet (tre måneder til og med børsdagen, ikke det faste fra §42–§52).
- Gruppen avgjør før flettingen: BH1/ECH2, om valget skal ta en lås mot to kjøringer samtidig.
- Gruppen avgjør før flettingen: ECH4, ingen måling når én av de 15 mangler kursen hele kvelden.
- Hvordan målingene fra tabellen føres i `malinger.md` (forslag: en ny § én gang i uka).
- Flett ikke mens jobben går, kl. 22:15–23:45 (ECH5).
- Testen for hele jobben på Windows kan feile i CI når Docker svarer innen ett sekund (40777327364).
