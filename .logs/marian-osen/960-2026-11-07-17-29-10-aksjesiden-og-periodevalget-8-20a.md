# Aksjesiden og periodevalget, 8.20a

## 2026-11-07 kl. 17:29 — Marian Osen

### Oppgave
Instruksjonen kl. 15:59 07.11: story 8.20a, aksjesiden og periodevalget med datoen på alle sidene. Den bygges etter spesifikasjonen for 8.20 og gruppens svar 07.11 kl. 10:33, 12:32 og 15:34, på egen gren med PR. PR-en stopper før flettingen.

### Plan
- Steg 0 og kvotesjekken (regel 15), og instruksjonen i dagsfila.
- Oppslag i spesifikasjonen, storyen, skissene i `docs/skisser/2026-11-06/` og koden. Så bygging i worktreen `G74-lund-osen-8-20a`.
- Hele settet alene før hver commit med kode eller tester. Så mutanter, gjennomgang med tre linser, triage, ruff og CI.
- Spesifikasjonen: `_bmad-output/implementation-artifacts/spec-8-20-ux-rettingene-etter-gjennomgangen-06-11.md`, avsnittene «8.20a, bygget 07.11» og «Gjennomgangen av 8.20a».

### Resultat
- **Kvoten kl. 15:59 (14:59 GMT):** `apiRequestsDate` 2026-11-06, så 0 brukt og 20 igjen 07.11 i GMT, og `extraLimit` 463. Ingen andre kall er gjort. `src/fetch_prices.py` er ikke kjørt, og `data/db/ose.db` er ikke rørt. Demobasene lå i midlertidige mapper.
- **Main:** `9351e2fd` (instruksjonen).
- **Grenen `8-20a-aksjesiden-og-periodevalget`, PR #118:**
  - `5bc2689c`: delene A–E, U88, BH10 fra 2.16, J og K. Datoen med pilene og «Vis dagen» på fire sider, lappen ved musepekeren med CSS, høyst 60 ord i hvert vindu på aksjesiden, de fete sjekknavnene, og bildene i `docs/appen/`.
  - `1c11844a`: testen for ringen leser symbolene fra oversikten, etter at mutant A overlevde.
  - `32648845`: spesifikasjonen.
  - `4cfdff78`: rettingene etter gjennomgangen.
  - `fb3cbca1`: triagen.
- **Hele settet:**
  - Første kjøring ga 57 feilet, fordi testene ventet de gamle ordene og fordi klassen `dagene` kolliderte. Den andre ga 2 feilet i `test_hjelpefeltet.py`.
  - Før hver commit med kode eller tester: 4434, 4434 og 4440 bestått, 24 hoppet over og 0 feilet. Ledig minne var 4,3–4,6 GB av 15,7 GB.
- **Mutantene:** åtte, én per del (A–E, U88, BH10 og J), og tre for rettingene (BH11, ECH2, ECH3). Alle ble fanget. A ble først fanget etter `1c11844a`. Hver fil var lik HEAD etterpå.
- **Bildene:** tatt med DevTools-protokollen i Edge uten vindu. `oversikten-topp-demo.png` er byte for byte den samme, og seks er nye. Etter rettingene var alle sju byte for byte like. Ingen side ruller vannrett ved 390 eller 320 px.
- **Gjennomgangen:** Blind Hunter 14 funn, Edge Case Hunter 8, og Verification Gap 1 hull og 2 andre funn. Ingen på høy. BH11/ECH1, ECH2, ECH3 og BH1 (middels) er rettet, og resten er rettet eller avvist med grunn.
- **CI:** grønn på `32648845` (run 42389466402) og `fb3cbca1` (run 42391310531).
- **Docker og Ollama** er ikke startet. Demoserveren og Edge-prosessene som ble startet for bildene, er stoppet.
- Punktet om BH10 i `issues.md` er krysset av.

### Åpne punkter
- PR #118 (8.20a) venter på flettingen. Ingen funn på middels eller over står åpne.
- De avviste lave funnene står i triagen i spesifikasjonen for 8.20, blant annet BH9: den svarte lappen øverst på streken kan dekke toppen av kurslinja den siste dagen. De kan tas opp med 8.20b.
