---
title: 'Story 9.0: Fem tester sjekker det de lover'
type: 'chore'
created: '2026-09-27'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '6dbfcb6ab2cae2d71192f4f5015dd2256d2ca3f7'
context:
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Kontrollen 26.09 fant fem tester som består uten å sjekke det navnet og docstringen lover («Utsatt», K3 og K4 i `docs/kontroll-2026-09-26.md`). En grønn testkjøring betyr derfor mindre enn vi sier, og 9.1 kan ikke vise til dem.

**Approach:** Hver av de fem skrives om, så den prøver løftet sitt. Koden i `src/` endres ikke. Hver test skal bestå mot `baseline_commit` og feile mot én mutant som bryter løftet. Det er motsatt av de andre storyene, der testene feilet mot baseline. Kilde: story 9.0 i `epics.md` (`b8b50bb`).

## Boundaries & Constraints

**Always:**
- Regel 6 og AD-8: ingen nett i testene. Filer skrives bare i `tmp_path`, aldri i `data/`.
- Tre av testene beholder navnene sine. To får nye navn (se beslutningen under), og det gamle navnet står i commit-meldingen og i «resolved:»-linjen, så et søk på det fortsatt finner dem.
- Forutsetningen i en test sjekkes med `assert`, aldri med `if`.

**Never:**
- Ingen endring i `src/`. Består en omskrevet test ikke mot baseline, stopper vi og avgjør det som egen sak.
- Ingen API-kall, og `src/fetch_prices.py` kjøres ikke (bare `kjoer` med falsk henter og `tmp_path`).

## Beslutninger 27.09

- **Navnet skal si det testen sjekker.** `test_formatet_kan_leses_av_snapshotkilde` leser nå gjennom `nyeste_leser` og `SnapshotLeser`, og heter `test_formatet_kan_leses_av_visningen`. `test_ruta_gjoer_ingen_nettverkskall` prøver begge rutene, og heter `test_rutene_gjoer_ingen_nettverkskall`. Testtallet står (468).

## I/O & Edge-Case Matrix

| Test | Lover | Svakheten i dag | Ny test | Mutant |
|---|---|---|---|---|
| `test_absolutt_endring_avgjoer_ved_lik_styrke` | Ved lik styrke avgjør absolutt endring, så et stort fall ikke havner bakerst (FR-102) | `assert` i en `if` som aldri slår til: styrkene blir 2 og 1 | EQNR +3 % og DNB −6 %: begge får styrke 2. Testen krever lik styrke og at DNB står først | `abs` fjernet i `_sorteringsnokkel` |
| `test_noeyaktig_paa_grensen_gir_null` | Nøyaktig 2,0 % over snittet gir 0 | Avviket blir 0.019999999999999928, så `<=` og `<` gir begge 0 | `[100]*8 + [98, 102]` gir snitt 100,0 og avvik nøyaktig 0,02. Samme nedover, med 102 og 98 byttet | `<=` byttet med `<` i `trend` |
| `test_formatet_kan_leses_av_snapshotkilde` → `test_formatet_kan_leses_av_visningen` | Det hentingen skriver, kan visningen lese | Leser med `SnapshotKilde`. Visningen leser gjennom `SnapshotLeser`, som avviser «naa» og «dag-000» | `kjoer` skriver fila i `tmp_path` med ekte datoer. `lagring_fil.nyeste_leser(tmp_path)` gir `sist_hentet` og 60 rader for hvert symbol | `naa` i `kjoer` uten tidssone |
| `test_kort_serie_viser_kurs_men_sier_at_signalet_mangler` | Kort serie: kursen vises, og siden sier at signalet mangler | Sjekker bare statuskoden og «kunne ikke regnes» | Serien slutter på 123,45. Testen krever `<span class="verdi">123.45</span>` og «kunne ikke regnes» | Linjen med sluttkursen fjernet fra `aksje.html` |
| `test_ruta_gjoer_ingen_nettverkskall` → `test_rutene_gjoer_ingen_nettverkskall` | Visningen gjør ingen nettkall | `monter` bytter ut `hent_leser`, så lesingen kjøres aldri, og bare `/` prøves | `lagring_fil.DATA_KATALOG` pekes mot `tmp_path` med en fil, og ingenting monteres. `/` og `/aksje/EQNR` gir 200 og viser data, med `requests.get` byttet ut | `hent_leser` kaller `requests.get` |

</frozen-after-approval>

## Code Map

- `tests/test_markedsoversikt.py:175` -- `serie`, `lager`, `KORT` (5/3/3). Prøvd 27.09: `serie([100.0]*5+[103.0])` mot `[100.0]*5+[94.0]` gir styrke 2 og 2, med DNB først.
- `src/markedsoversikt.py:155–164` -- `_sorteringsnokkel`: `(-styrke, -abs(endring))`. Røres ikke.
- `tests/test_signalberegning.py:194` -- `KORT` (ma_vindu=10), `kurser_med_avvik` står for de andre testene. `src/signalberegning.py:121–125`: `abs(avvik) <= p.noytralsone`, `NOYTRALSONE = 0.02`. Prøvd: `(102-100)/100 == 0.02` er `True`, og `trend` gir 0 både opp og ned.
- `tests/test_fetch_prices.py:322` -- `falsk_serie` har datoer som «dag-000» og står for de andre testene. Den nye testen bruker en egen serie med ISO-datoer. `src/fetch_prices.py:201–249` `kjoer` setter `naa` med UTC (233). `src/lagring_fil.py:56–66, 86–103, 158–166`: `SnapshotLeser` krever ISO med tidssone og rader `kursrad_fra_eodhd` godtar. Prøvd: `kjoer` og så `nyeste_leser` gir tid og 60 rader.
- `tests/test_app.py:342` og `:281` -- `monter`, `snapshot`, `eodhd`, `serie`, `HENTET`. `TestHentLeser` (389) viser hvordan `lagring_fil.DATA_KATALOG` pekes mot `tmp_path`. `src/templates/aksje.html:74` viser sluttkursen med `"%.2f"`, og `:156` viser «kunne ikke regnes». Prøvd: `123.45` står én gang på siden, i spannet.
- `tests/conftest.py` sperrer nettet. Mutanten for K4 fanges uansett av testens egen `requests.get`, siden den byttes ut først.

## Tasks & Acceptance

**Execution:**
- [x] `tests/test_markedsoversikt.py` -- ny serie for EQNR, og `if` byttet med `assert` på lik styrke, så rekkefølgen -- FR-102
- [x] `tests/test_signalberegning.py` -- kurser med nøyaktig avvik, opp og ned, og docstringen sier hvorfor -- grensen
- [x] `tests/test_fetch_prices.py` -- testen går gjennom `kjoer` og `nyeste_leser`, og heter `test_formatet_kan_leses_av_visningen` -- formatet
- [x] `tests/test_app.py` -- K3 krever sluttkursen. K4 bruker `DATA_KATALOG` i stedet for `monter`, ber om begge rutene, og heter `test_rutene_gjoer_ingen_nettverkskall` -- K3, K4

**Acceptance Criteria:**
- Gitt koden i `src/` fra `baseline_commit`, når de fem kjøres, så består de.
- Gitt mutantene i matrisen, lagt inn én om gangen og tilbakestilt mellom hver, så feiler testen for mutanten, med en melding som viser løftet.
- Gitt hele testsettet lokalt og i CI, så er det grønt, og antallet er 468 før og etter, fordi ingen test legges til eller fjernes. To tester har fått nytt navn.

## Implementation Notes

**Bygget 27.09** på grenen `9-0` (PR #7), fra `baseline_commit` `6dbfcb6`. Commitene er `0646b99` og rettingene etter gjennomgangen.

- **Tester:** 468 før og 468 etter. Ingen er lagt til eller fjernet. To har fått nytt navn: `test_formatet_kan_leses_av_snapshotkilde` heter `test_formatet_kan_leses_av_visningen`, og `test_ruta_gjoer_ingen_nettverkskall` heter `test_rutene_gjoer_ingen_nettverkskall`. Det gamle navnet står i docstringen til begge.
- **Mot `baseline_commit`:** `src/` er uendret (`git diff --exit-code 6dbfcb6 -- src/`), og alle 468 består, også de fem omskrevne.
- **Mutantene**, én om gangen mot hele testsettet, med `src/` satt tilbake og kontrollert mellom hver. Kjørt på nytt etter rettingene:
  - `abs` fjernet i `_sorteringsnokkel`: bare `test_absolutt_endring_avgjoer_ved_lik_styrke` feiler, med «ved lik styrke skal stoerst absolutt endring staa foerst».
  - `<=` byttet med `<` i `trend`: bare `test_noeyaktig_paa_grensen_gir_null` feiler, med «noeyaktig +2 % skal ligge i sonen».
  - `naa` i `kjoer` uten tidssone: bare `test_formatet_kan_leses_av_visningen` feiler, med «EQNR: visningen kan ikke lese hentet-tiden i fila».
  - Sluttkursen fjernet fra `aksje.html`: K3-testen feiler med «sluttkursen skal staa noeyaktig ett sted», og `test_rutene_gjoer_ingen_nettverkskall` feiler også, fordi den ser etter sluttkursen på detaljen.
  - `hent_leser` kaller `requests.get`: `test_rutene_gjoer_ingen_nettverkskall` feiler med «Visningen skal aldri gjoere API-kall», fra testens egen utbytting. De to testene i `TestHentLeser` feiler også.
  - Lagt til etter gjennomgangen (BH1): andresortering på navn i stedet for `abs`: bare `test_absolutt_endring_avgjoer_ved_lik_styrke` feiler.
- **Rekkefølgen i K3-testen:** `count` kommer før spannet, så en manglende sluttkurs gir meldingen fra `count`. Den har derfor fått egen melding.

## Spec Change Log

## Review Triage Log
Tre lag gjennomgikk diffen `6dbfcb6..0646b99` den 27.09: Blind Hunter (BH), Edge Case Hunter (ECH) og Verification Gap (VG). VG fant ingen hull.

| # | Funn | Dom | Bevis | Rute |
|---|---|---|---|---|
| BH1 | Forventet rekkefølge `["DNB", "EQNR"]` er også alfabetisk, så en andresortering på navn ville bestått | low | Riktig. Rettingen er direkte: rollene byttes | patch: EQNR faller og DNB stiger. Ny mutant (navn i stedet for `abs`) fanges |
| BH2 | Docstringen sier at en stabil sortering gir EQNR først uten `abs` | low | Uten `abs` er nøkkelen `-endring`, og +3 kommer foran -6 på verdien | patch: setningen skrevet om |
| BH3a | `assert tid.tzinfo is not None` kan ikke feile | low | `_hentet_fra_tekst` gir alltid UTC eller `None` | patch: linjen er fjernet |
| BH3b | Samme serie for alle symboler, tiden sammenlignes ikke, datoene sjekkes ikke, og samme fil sjekkes ikke | low | Løftet er at visningen kan lese fila. Tid og alle 60 rader for hvert symbol sjekkes | avvist: mer enn en direkte retting, og ingen navngitt feil det ville fanget i dag |
| BH4a | Filnavnet i K4-testen er skrevet inn for hånd | low | Samme mønster som `TestHentLeser` fra før | avvist: feiler høylytt hvis navnet endres |
| BH4b | Bare `requests.get` byttes ut, `Session` og `post` fanges bare av `conftest.py` | false | Docstringen sier at sperren i `conftest.py` står i tillegg | avvist |
| BH5 | Docstringen sier at 123.45 bare står ett sted, men det sjekkes ikke | low | Riktig | patch: `assert html.count("123.45") == 1`, med egen melding |
| BH6 | Forutsetningene i grensetesten kopierer formelen i `trend`, og 0.019999999999999928 sjekkes ikke | low | Lista er ti lang, så snittet over hele lista er snittet `trend` bruker | avvist: kosmetisk |
| BH7 | Implementation Notes er tomme, og linjenumrene i Code Map er utdatert | false | Rettingen er å endre spesifikasjonen. Notatene føres her uansett | avvist: gjelder spesifikasjonen |
| BH8 | Det gamle navnet finnes bare i docstringene før flettingen | false | Docstringene har det gamle navnet, og «resolved:»-linjen kommer etter flettingen, som planen sier | avvist |
| ECH1 | `close` er lik `adjusted_close` i testdataene, så en forveksling ses ikke | low | `test_sluttkursen_er_slutt_ikke_justert` (`tests/test_aksjedetalj.py:183`) dekker forvekslingen | avvist: dekket av en annen test |

## Design Notes

**Motsatt vei.** I 1.5b og 2.0 skulle nye tester feile mot baseline og bestå etter endringen. Her endres ikke koden. At en test kan feile, vises med mutanten, og at den er riktig, vises ved at den består mot baseline. Hver mutant kjøres mot hele testsettet, og det føres hvilke tester som feilet. At andre tester også feiler, er greit, men den omskrevne testen skal være blant dem.

**K4 gjennom den ekte lesingen.** Én test ber om begge rutene, så antallet står. `requests.get` byttes ut før kallet, og sperren i `conftest.py` står i tillegg.

**Arbeidsflyt, som 2.0:** grenen `9-0` fra `main`. 9-0 settes til in-progress når planen er godkjent. Mellomcommits pushes. `epic-9-context.md` committes på grenen. PR mot `main`, gjennomgang med tre lag, stopp før flettingen og vent på ja, og squash med `Co-authored-by: Joakim Lund`. Testtallene og mutantene føres i squash-meldingen.

**Etter flettingen:** de tre oppføringene i `deferred-work.md` får «resolved:», med gammelt og nytt navn der navnet er byttet, og `epics.md` får «*Ferdig …*» under 9.0. Spesifikasjonen settes til done, og 9-0 til review.

## Verification

**Commands:**
- `uv run pytest -q` -- forventet: grønt, 468
- `git stash`-fri mutantkjøring: hver mutant legges inn med et skript, testsettet kjøres, og `git diff --exit-code src/` bekrefter at koden er tilbake før neste -- forventet: testen for mutanten feiler, og `src/` er uendret til slutt
