# Bildene av appen i README-en (3.3k)

## 2026-11-14 kl. 05:42 — Marian Osen

### Oppgave
Story 3.3k (instruksjonen 12.11 kl. 17:11, gruppens svar kl. 17:09): bildene av appen i README-en skal stå i rekkefølgen fra knapperaden, og bildene ved 390 px skal ligge i `docs/appen/mobil/` og stå i en egen pil. Tilleggene:
- **Tillegg 1:** linja nederst på sidene.
- **Tillegg 2:** «De 15 mest omsatte».
- **Tillegg 3:** fletting uten nytt stopp.
- **Tillegg 4:** ventingen ser også etter done.
- **Tillegg 5:** tabellen «Demoen og den ekte versjonen».
- **Tillegg 6:** 8.29 i ventingen.
- **Det felles tillegget** (13.11 kl. 18:24): hele settet kjøres i CI.
- **Tillegg 7** (14.11 kl. 05:10): start testene på nytt og flett.

### Plan
- Vente til Utført-linjene for de sju storyene sto på origin/main: 8.26, 8.27, 3.7, 10.11, 8.19, 8.28 og 8.29. Så grenen `3-3k-bildene-av-appen-i-readme` fra `21876255`, i egen worktree `G74-lund-osen-3-3k`.
- Spesifikasjonen: `_bmad-output/implementation-artifacts/spec-3-3k-bildene-av-appen-i-readme.md`, med tolv spørsmål og et forslag til hvert. Spørsmålene står som besvart 12.11 kl. 20:44 (tillegg 3).
- Etter det: bildene fra en demobase i en midlertidig mappe og en demoserver på en annen port enn 8000. Så testene, én mutant, Edge Case Hunter og triage, en bildegren, PR, CI og fletting.

### Resultat
- **Commits på grenen:**
  - `f2841975`: spesifikasjonen.
  - `3d581b22`: linja «Versjon 1 er ferdig.».
  - `3c4666af`: bildene og avtrykkene.
  - `a376061c`: rekkefølgen, `mobil/` og testene.
  - `2e454717`: tabellen.
  - `5a33c9bd`: rettingene etter gjennomgangen.
- **Bildene:**
  - Bare de åtte som viser bunnen av siden, er byttet, og forskjellen er linja nederst. De andre var like byte for byte.
  - To bilder er nye: `notatpanelet-demo.png` og `vis-meg-rundt-demo.png`.
  - Bildegrenen `pr-3-3k-bilder` har bildene før og etter.
- **Mutanten M1** ble fanget. README-en var lik HEAD etterpå (`git hash-object`).
- **Edge Case Hunter:** fem funn. ECH1 (middels) og ECH2–ECH4 (lave) er rettet, og ECH5 (lav) står.
- **Testene:**
  - Før rettingene: filene som leser README-en, 1925 bestått og 7 hoppet over.
  - Etter rettingene 14.11: `tests/test_docker.py` 158 bestått, `tests/test_vis_meg_rundt_8_26.py` 190 bestått, og `--dokumentene` 2948 bestått og 7 hoppet over, kl. 05:16–05:33.
  - Hele settet i CI (run 43557292773), etter gruppens svar 13.11 kl. 18:24. Alle fire jobbene var grønne, også Windows.
- **Fletting:** PR #155 squash-flettet i `e8e226ff` kl. 05:41, låst til `5a33c9bd`. Treet er likt head-en.
  - Kveldsjobben sto som Ready kl. 05:40, ikke Disabled. Gruppen skulle slå den på igjen lørdag, og flettingen var utenfor pausene, så pausene gjaldt ikke.
- **Føringen** på grenen `3-3k-foering` fra origin/main, pushet til main:
  - `eea0d7e8`: done i spesifikasjonen, sprint-status og `epics.md`.
  - `9630dbad`: kvalitetssikringen.
  - `72c0b7f8`: dagsfilene 12.11, 13.11 og 14.11.
  - `--dokumentene` på føringen kl. 05:41–05:57: 2948 bestått og 7 hoppet over, før loggen og Utført-linjene.
  - README-en under «Status» er ikke endret. 3.3k endrer bare bildene og ordene nederst, og README-en sa alt at versjon 1 er ferdig.
- **Lukket i issues.md:** punktet fra 8.26 om bunnteksten «Appen er under utvikling og ikke ferdig.».
- **Ikke gjort:** kvotesjekken etter regel 15 ble ikke gjort i økta. Ingen API-kall ble gjort, `data/db/ose.db` ble ikke rørt, og Gemma ble ikke brukt.
- **Avvik:**
  - Natt til 14.11 stoppet lite minne både demoserveren og en kjøring av `--dokumentene` i bakgrunnen. Bildene var alt tatt, så demoserveren ble ikke startet igjen. `--dokumentene` ble ikke startet igjen før gruppens svar kl. 05:10 (tillegg 7), fordi bare ventekommandoer kunne startes igjen uten å spørre. Den nye kjøringen kl. 05:16 gikk gjennom.
  - Én gang ble `rm -f` brukt på en midlertidig indeksfil i scratchpad (`GIT_INDEX_FILE` for bildegrenen), og instruksjonen sier at ingenting slettes med rm. Fila fantes ikke, så ingenting ble slettet.
  - Tillegg 7 ble limt inn to ganger uten sluttmarkøren. Ingenting ble gjort før det kom med markøren (regel 1).
  - To tillegg til KI-teksten (12.11 kl. 17:34 og 17:46) kom til dette vinduet ved en feil. Begge ble stoppet i steg 0, og ingenting ble gjort.

### Åpne punkter
- Spørsmål 11: investorsiden og siden for eodhd.com i demoen har ingen steg i omvisningen, så de har verken «Vis meg rundt» eller «Spill av omvisningen». Om de skal ha det, er en egen sak.
- ECH5 (lav): linja om neste henting står ikke når tidspunktet ikke kan regnes ut, men raden i tabellen beskriver bare det vanlige.
- Bildegrenen `pr-3-3k-bilder` på GitHub kan slettes når gruppen vil.
