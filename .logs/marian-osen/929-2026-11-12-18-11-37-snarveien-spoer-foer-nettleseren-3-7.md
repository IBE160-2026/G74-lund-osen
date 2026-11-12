# Snarveien spør før nettleseren, og KI-teksten på en ny PC (3.7)

## 2026-11-12 kl. 18:11 — Marian Osen

### Oppgave
Instruksjonen «Ny liten story etter 3.6: snarveien spør før nettleseren åpnes» (limt inn kl. 16:48, etter svaret 11.11 kl. 22:07 og ønsket 12.11 kl. 16:23), med tillegg 1 (KI-teksten står på i en ny installasjon, svaret kl. 16:32), tillegg 2 (startskriptet henter Gemma første gang, kl. 16:41), tillegg 3 (eller egen API-nøkkel, kl. 16:46) og tillegg 4 (fristen på 30 sekunder, rettelsen fra rådet). Bygges på egen gren og worktree, og flettes ikke før gruppens ja, tidligst etter 8.26.

### Plan
- Tillegg 1 ble limt inn først (kl. 16:36), uten grunninstruksjonen. Vinduet stoppet og sa fra, som tillegget krevde. Grunninstruksjonen og tilleggene ble så limt inn, og alle fem er kopiert ordrett til scratchpad med klokkeslettet fra `date`.
- Kvotesjekken (regel 15): `apiRequestsDate` var 2026-11-11, så det er brukt 0 kall i dag, og 20 er igjen. Det er ikke gjort andre API-kall.
- Story 3.7 er neste ledige nummer i Epic 3. Grenen er `3-7-snarveien-spoer-foer-nettleseren`, fra origin/main `a93c668f`, i worktreen `G74-lund-osen-3-7`.
- Spesifikasjonen er `_bmad-output/implementation-artifacts/spec-3-7-snarveien-spoer-foer-nettleseren.md`, med spørsmål 1–26 og forslag.
- Pakkenavnet i winget (`Ollama.Ollama`) er slått opp med `winget search`. Ingenting er installert, ingen modell er hentet, og Ollama og Docker på PC-en er ikke rørt. Alt er prøvd med falske `winget` og `ollama`, en falsk Ollama på 127.0.0.1 og falske nøkler.

### Resultat
- `ad326950`: storyen, spesifikasjonen og svarene. Svar 5 i 10.2a, 10.2b og epics.md har Rettet-linjer, og PRD-en har en datert linje under FR-608, med linja i memloggen.
- `e0d10549`: endringene i koden.
  - `start/snarvei.ps1` (`Snarvei-Og-Nettleser`) og `start/start.ps1`: snarveien spør før nettleseren.
  - `start/frist.ps1`: fristen på 30 sekunder, med falske taster i testene.
  - `start/ki-modell.ps1` (`Tilby-KI`): Gemma, egen nøkkel eller ikke nå.
  - `.env.example` har `lokal`.
  - Linja uten modell står i hentingen og på aksjesiden og forsiden, bare i den ekte versjonen og bare for siste børsdag.
  - README-en, installasjonen og hjelpen følger, og det er et nytt CI-steg på Windows.
  - Testene står i `tests/test_snarveien_foer_nettleseren_3_7.py`.
- Bildene i `docs/appen/` er tatt på nytt to ganger og er like byte for byte. `notatene-brfe-390-demo.png` står som på main, slik det var i 10.10: utklippet ga et annet bilde også på `a93c668f`.
- **Gjennomgangen:** Blind Hunter, Edge Case Hunter og Verification Gap hadde 18, 15 og 15 funn, to høye (VG1 og VG2). Alle høye og middels er rettet før første commit. Triagen står i spesifikasjonen.
- **Hele settet:** åtte deler, én om gangen, kl. 17:40–18:01, etter at pytest i 8.26 var ferdig. Det ga 5462 tester, like mange som `--collect-only`: 5435 bestått, 24 hoppet over og 3 feilet. De tre ble rettet i `d3cbb938`. Testen av start.ps1 i en egen mappe manglet de nye skriptene, og lenketestene godtok ikke lenken til installasjonen. Filene ble kjørt på nytt: 196 bestått og 7 hoppet over.
- **Mutantene:** seks, én per del (A, tillegg 4, B, tillegg 2, tillegg 3 og lesingen av svaret). Alle ble fanget, og hver fil var lik kopien og HEAD etterpå.
- `6594d106`: bildene før og etter av linja, med en testbase uten rader i KI-loggen. Bildene ligger i scratchpad, utenfor repoet, og teksten før og etter står i spesifikasjonen.
- PR #148 er åpnet. På første head var jobben `docker` grønn mens resten kjørte.

### Åpne punkter
- Gruppens svar på spørsmål 1–26 i spesifikasjonen, særlig 11, 17, 20, 22, 23, 24, 25 (middels, regel 25) og 26.
- Flettingen: etter gruppens ja, tidligst etter 8.26 (kl. 23:50–23:58), med main flettet inn i grenen først. Da føres instruksjonen og tilleggene i `docs/ai-prompts/2026-11-12.md` med Utført-linja.
- Raden «KI-tekst» i tabellen «Demoen og den ekte versjonen» i README-en kommer med 8.26 og må følge 3.7 når main med 8.26 er flettet inn (tillegg 1, steg 3).
- De to kommandoene uten Docker (`winget install --id Ollama.Ollama …` og `ollama pull gemma4:e4b`) og framdriften i et ekte vindu er ikke prøvd. De prøves i neste README-prøve på en PC uten Ollama (spørsmål 23, BH9).
- Fargen på lenken «Slik slår du den på» (spørsmål 26): den bygges etter svaret, med bildene tatt på nytt.
