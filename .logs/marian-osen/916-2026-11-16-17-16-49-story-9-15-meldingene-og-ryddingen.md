# Story 9.15: meldingene etter v1.1, det som ikke brukes, og ryddingen

## 2026-11-16 kl. 17:16 — Marian Osen

### Oppgave
Instruksjonen kl. 15:39 i `docs/ai-prompts/2026-11-16.md`, etter gruppens svar 16.11 kl. 15:39: spørsmål 10, 11 og 12 i 9.14 tas nå, og ikke etter innleveringen. Svarene skulle føres på main, og en liten story i Epic 9 skulle rette meldingene (D1–D4) og ta bort det som ikke brukes (D5–D10). Ryddingen av worktrees og grener skulle tas etter at storyen er flettet.

### Plan
- Steg 0: instruksjonen kl. 15:37 ble gjort ferdig først. Se den nye seksjonen i [917-…-svarene-i-9-14-og-fr-601-2-18.md](917-2026-11-16-12-54-49-svarene-i-9-14-og-fr-601-2-18.md).
- Kvoten ble sjekket kl. 15:40. Ingen andre API-kall er gjort, og `src/fetch_prices.py` er ikke kjørt, bare testene.
- Storyen er 9.15. Den bygges i worktreen `G74-lund-osen-9-15`, på grenen `9-15-meldingene-og-det-som-ikke-brukes`, fra `origin/main` (`c2adf7f5`). Spesifikasjonen er første commit, og en leser tar gjennomgangen med bare lesing.

### Resultat
- **Svarene (steg 1):** under spørsmål 10, 11 og 12 i spesifikasjonen for 9.14 står svarlinjer for kl. 15:39, og `issues.md` følger (`c2adf7f5`). Main ble pushet etter `--dokumentene` kl. 16:04–16:22, med 2966 bestått og 7 hoppet over.
- **Story 9.15 (steg 2):**
  - Spesifikasjonen, storyen i `epics.md` og sprintstatusen står i `42730a24`.
  - Rettingen og testene er i `90d93016`. De seks testene i `tests/test_meldingene_9_15.py` feilet alle mot koden før rettingen (kl. 16:25).
  - **D1–D4:** meldingene sier at kveldsraden bare kan skrives så lenge datoen er inneværende børsdag. Etter det regner siste steg i en henting signalet i ettertid, uten KI-tekst, for aksjene i lista som har nok kurser i basen.
  - **D5 og D6:** `MinneNotatlagerMedKjoep` og `RETNINGENE` er tatt bort.
  - **D7–D10 står med grunn:** `nyeste_leser` og konstantene i `hjelpetekster.py` brukes av testene, `src/meldinger.py` er for Epic 6, og ikonfilene lages av `src/ikon.py` og leses av testene.
- **Bildene:** avtrykkene regnes også av `src/dagsgrunnlag.py` og `src/tilstand.py`. Alle 18 bildene ble tatt på nytt fra demobasen kl. 16:37 og 16:50, på portene 62931 og 62933. De er byte for byte de samme, så bare avtrykkene er satt på nytt (`303841a9` og `d2f3f5e3`). Demoserveren er stoppet.
- **Gjennomgangen:** 9 funn.
  - ECH1 (middels) er rettet, og ECH2, VG1, VG2, VG3 og BH2 er rettet (`d2f3f5e3` og `82f97c58`).
  - ECH3 og VG4 står med grunn.
  - BH1 (middels) følger av svaret kl. 15:39 og står åpent (regel 25).
- **Testene og PR-en:** `--dokumentene` på grenen ga 2966 bestått og 7 hoppet over kl. 16:52–17:10. PR #162 er åpnet, og CI var grønn i alle fire jobbene (run 43904623295 på `98d7fc4c`, 5872 bestått og 99 hoppet over). **Den er ikke flettet**, fordi BH1 står åpent.
- **Ryddingen (steg 3):** den er ikke gjort, fordi den tas etter at storyen er flettet. Ingenting er fjernet.
  - Kartleggingen mot `gh pr list --state merged` er gjort, med bare lesing.
  - Kan fjernes etter flettingen, uten 9.15: 13 worktrees med flettet PR (10-11, 2-17, 2-18, 3-7, 8-19, 8-27, 8-28, 8-30, 8-31, 9-11, 9-12, 9-13 og 9-14), 89 lokale grener og 15 eksterne grener som står på head-en PR-en ble flettet fra.
  - Står: `3-3k-foering` og `8-29-foering`, som ikke har noen flettet PR, og bildegrenene, `G74-lund-osen-jobb` og main.
- Ingenting i `data/`, `_privat/` eller `local-tests/` er rørt, og den ekte versjonen er ikke startet.

### Åpne punkter
- BH1 i 9.15 (middels, følger av svaret kl. 15:39): skal ikonfilene `ikon-16`, `-48`, `-192` og `-512` stå eller tas bort? Det står som spørsmål 1 i spesifikasjonen, og PR #162 flettes ikke før gruppen har svart.
- Ryddingen (spørsmål 12) tas etter at PR #162 er flettet, og ikke i pausene om kvelden. Kartleggingen må tas på nytt da.
