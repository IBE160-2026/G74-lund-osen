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

## 2026-11-16 kl. 18:52 — Marian Osen

### Oppgave
Beskjeden kl. 15:42 fra rådet, etter gruppens svar kl. 15:41: gruppen flytter selv `local-tests/` til `_privat/local-tests`. Arbeidet stopper ikke. Når ryddingen føres, skal `issues.md` under spørsmål 12 si at gruppen flyttet mappa 16.11, og finnes mappa fortsatt i roten da, føres det, og den står.

### Plan
- Lagre beskjeden ordrett i scratchpad og dagsfila før noe annet.
- Slå opp påstandene i beskjeden uten å lese mappa: `.gitignore` og `tests/test_ryddighet.py`.
- Legge en underlinje under spørsmål 12 i `issues.md`, så beskjeden følger med til ryddingen.

### Resultat
- Beskjeden er lagret ordrett i dagsfila (`64a98576`).
- Påstandene stemmer: `local-tests/` står i `.gitignore` (linje 58), og `tests/test_ryddighet.py` bruker bare tenkte stier som `local-tests/proeve.py` og `local-tests/x.py`. README-en nevner mappa i én linje under «Ikke i repoet», og den står som den er, etter beskjeden.
- Under spørsmål 12 i `issues.md` står en underlinje om beskjeden. Selve føringen tas når ryddingen gjøres, etter at PR #162 er flettet.
- Mappa er ikke lest eller rørt, og om den fortsatt står i roten, er ikke sjekket nå. Det sjekkes ved ryddingen.

### Åpne punkter
- Ved ryddingen: før under spørsmål 12 i `issues.md` at gruppen flyttet `local-tests/` til `_privat/` 16.11, og om mappa fortsatt sto i roten. Står som underlinje under punktet for spørsmål 12.

## 2026-11-17 kl. 11:14 — Marian Osen

### Oppgave
Instruksjonen kl. 21:50 (limt inn 16.11 kl. 21:52, og på nytt kl. 22:16, ordrett lik): svaret kl. 18:51 på spørsmål 1 i 9.15 (BH1, «La dem stå»), flettingen av PR #162, føringen og ryddingen etter steg 3 i instruksjonen kl. 15:39. I tillegg beskjeden fra rådet 17.11 kl. 11:02, med tre fakta fra gruppen til føringen.

### Plan
- Svaret under spørsmål 1 i spesifikasjonen, `issues.md` følger, før pausen kl. 22:10.
- Etter kl. 23:50: main inn i grenen, `--dokumentene`, push, CI, fletting etter kl. 23:58, låst til head-en, og føringen som for 2.18.
- Ryddingen med en ny kartlegging, `local-tests/` uten å lese filene, og alt ført med navn og commit.

### Resultat
- **Steg 1, kl. 21:53–21:54:** svarlinja under spørsmål 1 i spesifikasjonen for 9.15 (`4a1de503` på grenen, med i `9fea9fc8`). Dagsfila har instruksjonen kl. 21:50 og instruksjonen etter svaret kl. 20:22. BH1 er lukket i `issues.md`.
- **Natta:** ventingen til kl. 23:50 ble stoppet, og ingenting ble gjort før kl. 10:40 17.11. Varselet sa «lite minne», og det sto også i vinduet.
  - *Rettet 2026-11-17 (beskjeden fra rådet kl. 11:02):* årsaken var hvilemodus, ikke lite minne. PC-en var i hvilemodus fra 16.11 kl. 23:06:50 til 17.11 kl. 10:40:39, og den ble vekket av USB. Gruppen slår av hvilemodus.
- **Kvoten kl. 10:41:** `apiRequestsDate` sto på 2026-11-16, så 0 av 20 kall er brukt i dag (GMT), og 296 er igjen i bonuskvoten.
- **Steg 2:**
  - `origin/main` ble flettet inn i grenen (`c040f478`), og `--dokumentene` ga 2966 bestått og 7 hoppet over, kl. 10:41–11:00.
  - CI var grønn i alle fire jobbene (run 44060835062, med 5872 bestått og 99 hoppet over).
  - PR #162 ble squash-flettet i `9fea9fc8` kl. 11:07, låst til `c040f478`. Føringen står i `33ef1c20`, og vurderingsmatrisen i `ae9ab77e`.
- **Beskjeden kl. 11:02:** kontrollen etter kveldsjobben 16.11 er ført i spesifikasjonen for 2.17 og i `epics.md`, og punktet om KI-teksten er lukket (`a0bb9d29`). Kjøringen kl. 22:45 med 0 kall er ført i Prøve 4, og spørsmål 5 i 9.13 er lukket (`342fdf63`). Vinduet leste ikke `data/`, og tallene er gruppens.
- **Steg 3, ryddingen kl. 11:12–11:13:**
  - Kartleggingen er tatt på nytt mot 156 flettede PR-er. Hver worktree var ren og hadde ingen lenker, bare `.venv/` og cachemapper som ignorerte filer. Commiten ble sjekket rett før hver sletting, og git nektet ingenting.
  - Står: main, `G74-lund-osen-jobb`, bildegrenene, og `3-3k-foering` og `8-29-foering` med worktreene sine, fordi de ikke har noen flettet PR.
  - `local-tests/` står ikke i roten. Det er sjekket med en test på stien, og ingen filer er lest.
  - Alt som er fjernet, kan hentes tilbake fra commiten under, så lenge den finnes i git.

#### Worktrees (14), fjernet med `git worktree remove` uten `--force`

- `G74-lund-osen-10-11` (10-11-mest-av-bransjene-med-minst-to-aksjer, `1402fed3`)
- `G74-lund-osen-2-17` (2-17-signalet-i-ettertid, `2d489390`)
- `G74-lund-osen-2-18` (2-18-ki-setningen-i-ettertid, `b1fa8c50`)
- `G74-lund-osen-3-7` (3-7-snarveien-spoer-foer-nettleseren, `816f0be0`)
- `G74-lund-osen-8-19` (8-19-neste-henting-i-stripa, `4f473586`)
- `G74-lund-osen-8-27` (8-27-mine-notater-i-panel, `9244203f`)
- `G74-lund-osen-8-28` (8-28-de-15-mest-omsatte, `baaa5168`)
- `G74-lund-osen-8-30` (8-30-plassstreken-kontrast, `191a682e`)
- `G74-lund-osen-8-31` (8-31-maalene-i-nettleseren, `c45cbb7c`)
- `G74-lund-osen-9-11` (9-11-prd-etter-tilbakemeldingen, `7f2edbce`)
- `G74-lund-osen-9-12` (9-12-raadordene-i-alle-malene, `8cfaef22`)
- `G74-lund-osen-9-13` (9-13-dokumentrunden-etter-v1-1, `ee756c36`)
- `G74-lund-osen-9-14` (9-14-kontrollrunden-etter-v1-1, `930deda1`)
- `G74-lund-osen-9-15` (9-15-meldingene-og-det-som-ikke-brukes, `c040f478`)

#### Lokale grener (90), slettet med `git branch -D`, med commiten og PR-en

- `1-4b` `5ab9bf88` #1
- `1-4c` `43790ea4` #2
- `1-5` `fde81b5a` #3
- `1-5b` `373899a7` #5
- `1-6` `9d1b2f2a` #8
- `1-7` `5acca079` #9
- `1-8` `17053e70` #10
- `1-9` `0ce63001` #11
- `10-1-ki-grunnlag` `f11473f6` #47
- `10-11-mest-av-bransjene-med-minst-to-aksjer` `1402fed3` #149
- `10-2a-modell-og-kontroll` `a7971054` #48
- `10-2b-teksten-i-hentingen` `26cf89cf` #49
- `10-2c-prompten-versjon-2` `f3e52bd2` #55
- `10-2d-kontrollen-leser-formene-gemma-skriver` `0bdd2594` #71
- `10-3-ki-visningen` `791b3fae` #50
- `2-0` `726351c1` #6
- `2-1` `141679ed` #13
- `2-17-signalet-i-ettertid` `2d489390` #157
- `2-18-ki-setningen-i-ettertid` `b1fa8c50` #161
- `2-1b` `98cc9d97` #14
- `2-1c` `619a332b` #16
- `2-2` `98a3b86f` #19
- `2-2b` `d08a9c4f` #20
- `2-3` `ded65516` #22
- `2-3-hentingen-fra-kl-21` `f5061332` #60
- `2-3b` `20065ad8` #28
- `2-5` `1a2f38ca` #18
- `2-7a-stilen-i-en-fil` `625d044b` #76
- `2-8-indeks-tabellen-og-porten` `114a380b` #56
- `2-8-indekskallet-i-hentingen` `b4a07219` #57
- `2-9-hovedindeksen-paa-forsiden` `bdfd412c` #59
- `2-9b-soeylene` `dbb6fe62` #63
- `2-9c-indeks-i-kursgrafen` `c41133e1` #64
- `3-1` `4b46e7a5` #23
- `3-2` `99bf693e` #24
- `3-2b-port-8000` `b4eaa7d2` #68
- `3-3` `f4ff7e39` #25
- `3-3c-kom-i-gang-bilder-og-demoen-foerst` `87e4f8ee` #66
- `3-3d-readme-ryddingen` `8ffa9695` #67
- `3-3e-bildet-uv-og-variablene` `084edb14` #70
- `3-3f-bildene-av-appen` `58f91c91` #75
- `3-3g-readme-demoen-anbefales` `9e5b1931` #77
- `3-3k-bildene-av-appen-i-readme` `5a33c9bd` #155
- `3-4` `75b7040d` #26
- `3-4-alle-ti-kombinasjonene` `33ca1339` #58
- `3-4-docker` `da95f40c` #27
- `3-4-hjelp` `0ddb54a5` #31
- `3-4-hjelp-b` `f0cb1495` #32
- `3-4-orden` `17f0de06` #34
- `3-4-readme` `8089c072` #30
- `3-4-utvikling` `e593d2de` #33
- `3-4b-ki-tekstene-i-demoen` `8d632b04` #69
- `3-4d-fotnoten-ikke-vurdert` `3b102671` #90
- `3-4e-fotnoten-etter-startdag` `a1ed96f1` #91
- `3-7-snarveien-spoer-foer-nettleseren` `816f0be0` #148
- `4-0-nettsperren` `ef7774cd` #44
- `4-2-kilogg` `8e2e2964` #45
- `4-3-sqlite-kilogg` `2f42f710` #46
- `8-0` `a6e45655` #15
- `8-0b` `8b72632d` #29
- `8-0c` `5fa73044` #35
- `8-0c-datoer` `5ed2c011` #36
- `8-0d-aksjesiden` `a8a443a4` #42
- `8-0d-antall` `dfc9fa21` #41
- `8-0d-grunnlag` `c96503d1` #39
- `8-0d-oversikten` `0416a856` #40
- `8-0e` `372c9119` #37
- `8-0e-tekst` `34fac32c` #38
- `8-15-sortering` `e61ed40b` #43
- `8-15b-selskap-og-den-sorterte-kolonnen` `a698f71b` #73
- `8-16-periodene-i-kursgrafen` `dca140b9` #72
- `8-16b-dagen-paa-hele-siden` `1c67d187` #74
- `8-17a-periodevalget-i-oversikten` `047f1f7b` #106
- `8-19-neste-henting-i-stripa` `4f473586` #151
- `8-27-mine-notater-i-panel` `9244203f` #147
- `8-28-de-15-mest-omsatte` `baaa5168` #153
- `8-29-din-egen-liste-kom-i-gang` `808044a0` #154
- `8-30-plassstreken-kontrast` `191a682e` #156
- `8-31-maalene-i-nettleseren` `c45cbb7c` #159
- `8-6-boersometeret` `4f5290a7` #89
- `9-0` `cb0d36a0` #7
- `9-1-kvalitetssikringen-oppdateres` `d1a1d0dc` #61
- `9-11-prd-etter-tilbakemeldingen` `7f2edbce` #150
- `9-12-raadordene-i-alle-malene` `8cfaef22` #152
- `9-13-dokumentrunden-etter-v1-1` `ee756c36` #158
- `9-14-kontrollrunden-etter-v1-1` `930deda1` #160
- `9-15-meldingene-og-det-som-ikke-brukes` `c040f478` #162
- `9-7-ruff` `4cf27a91` #62
- `9-8-agents-kopien-bort` `76eae1c1` #65
- `readme-uten-bilde` `cecf94e8` #54

#### Eksterne grener (16), slettet med `git push origin --delete`

- `origin/10-11-mest-av-bransjene-med-minst-to-aksjer` `1402fed3` #149
- `origin/2-17-signalet-i-ettertid` `2d489390` #157
- `origin/2-18-ki-setningen-i-ettertid` `b1fa8c50` #161
- `origin/3-3k-bildene-av-appen-i-readme` `5a33c9bd` #155
- `origin/3-7-snarveien-spoer-foer-nettleseren` `816f0be0` #148
- `origin/8-19-neste-henting-i-stripa` `4f473586` #151
- `origin/8-27-mine-notater-i-panel` `9244203f` #147
- `origin/8-28-de-15-mest-omsatte` `baaa5168` #153
- `origin/8-29-din-egen-liste-kom-i-gang` `808044a0` #154
- `origin/8-30-plassstreken-kontrast` `191a682e` #156
- `origin/8-31-maalene-i-nettleseren` `c45cbb7c` #159
- `origin/9-11-prd-etter-tilbakemeldingen` `7f2edbce` #150
- `origin/9-12-raadordene-i-alle-malene` `8cfaef22` #152
- `origin/9-13-dokumentrunden-etter-v1-1` `ee756c36` #158
- `origin/9-14-kontrollrunden-etter-v1-1` `930deda1` #160
- `origin/9-15-meldingene-og-det-som-ikke-brukes` `c040f478` #162

### Åpne punkter
- Ingen nye. Spørsmål 12 i 9.14 er lukket.
