---
title: 'Story 9.0: Fem tester sjekker det de lover'
type: 'chore'
created: '2026-09-27'
status: 'in-progress'
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

## Spec Change Log

## Review Triage Log

## Design Notes

**Motsatt vei.** I 1.5b og 2.0 skulle nye tester feile mot baseline og bestå etter endringen. Her endres ikke koden. At en test kan feile, vises med mutanten, og at den er riktig, vises ved at den består mot baseline. Hver mutant kjøres mot hele testsettet, og det føres hvilke tester som feilet. At andre tester også feiler, er greit, men den omskrevne testen skal være blant dem.

**K4 gjennom den ekte lesingen.** Én test ber om begge rutene, så antallet står. `requests.get` byttes ut før kallet, og sperren i `conftest.py` står i tillegg.

**Arbeidsflyt, som 2.0:** grenen `9-0` fra `main`. 9-0 settes til in-progress når planen er godkjent. Mellomcommits pushes. `epic-9-context.md` committes på grenen. PR mot `main`, gjennomgang med tre lag, stopp før flettingen og vent på ja, og squash med `Co-authored-by: Joakim Lund`. Testtallene og mutantene føres i squash-meldingen.

**Etter flettingen:** de tre oppføringene i `deferred-work.md` får «resolved:», med gammelt og nytt navn der navnet er byttet, og `epics.md` får «*Ferdig …*» under 9.0. Spesifikasjonen settes til done, og 9-0 til review.

## Verification

**Commands:**
- `uv run pytest -q` -- forventet: grønt, 468
- `git stash`-fri mutantkjøring: hver mutant legges inn med et skript, testsettet kjøres, og `git diff --exit-code src/` bekrefter at koden er tilbake før neste -- forventet: testen for mutanten feiler, og `src/` er uendret til slutt
