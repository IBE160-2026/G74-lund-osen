---
title: 'Story 2.2b: Sidene leser dagens vurdering'
type: 'feature'
created: '2026-10-03'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'a9b87d591751b32b9382250cdfb0b82fc1bca3d3'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-2-hentekommandoen-som-egen-inngang.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-5-vurderingen-skrives-i-samme-kjoering.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Oversikten og aksjedetaljen regner signalet av kursene ved hver visning, mens hentekommandoen lagrer vurderingen i `vurdering` (2.5). Da finnes to veier til samme tall, og en dag ingen kjørte kommandoen, ser ut som en dag med svar (FR-409).

**Approach:** En egen port som bare leser, `Oversiktsleser`, henter selskapene fra `aksje` sammen med nyeste og forrige kurs, `hentet` og raden i `vurdering` for datoen til nyeste kurs, i én spørring med join. Sidene viser vurderingen gjennom `tilstand()` og regner aldri signalet. Aksjedetaljen tegner grafen av `kurs` og forklarer sjekkene med målingene i raden (FR-706).

## Boundaries & Constraints

**Always:**
- Porten `Oversiktsleser` (Protocol i `src/oversiktsdata.py`) har bare lesemetoder: `oversikt()` og `post(symbol)`. En test krever at den ikke har noen skrivemetode. Adapteren `SqliteOversiktsleser` ligger i `lagring_sqlite.py`. `app.py` har ingen SQL. Merknad under AD-3 i spinen: en port som bare leser og går på tvers av datasettene, uten skriver.
- Sidene leser selskapene fra `aksje` i basen, i `rowid`-rekkefølge, også aksjedetaljen og lista over aksjer som mangler. `app.py` leser ikke `AKSJEUNIVERS`. Koden antar aldri at det er 15.
- Dagens vurdering er raden for datoen til nyeste kurs per aksje. Hver rad går gjennom `tilstand(innhold, dato, idag)`, med `idag` fra en klokke i `app.py` som testene kan bytte ut.
- Tekstene, synlige og små under «–». Retning er «Ukjent» (FR-101):
  - Grunn `symbol_feilet`: «hentingen feilet». `kurs_ikke_fra_dagen`: «ingen kurs fra dagen». `signal_ikke_regnet`: «signalet kunne ikke regnes».
  - Ingen rad på en børsdag: «ikke vurdert». Ingen rad på en dag som ikke er børsdag: «ikke børsdag». `UtenforKalenderen`: «utenfor børskalenderen».
  - Er noen rad «ikke vurdert», sier en fotnote at hentekommandoen ikke har skrevet en vurdering for dagen, for eksempel fordi kursene er lest inn med `--les-inn`. Siden kan ikke vite hvordan kursene kom inn.
- `markedsoversikt.py`, `aksjedetalj.py` og `app.py` importerer verken `beregn_signal` eller `vurder`. Endringen regnes fortsatt av kursene (FR-101). Sortering (FR-102) og «skiller seg ut» bygger på den lagrede styrken. Rader uten vurdering sorteres sist.
- Aksjedetaljen: grafen fra serien i `kurs`, sjekkene og målingene fra raden. Har raden en grunn eller mangler den, er svaret 200 med grafen og tilstandsteksten i stedet for sjekkene (FR-204). 404 bare for et symbol som ikke står i `aksje`, og en aksje uten kursrader.
- SYMBOL_FEILET og KURS_IKKE_FRA_DAGEN skrives for en dag uten ny kurs. Nyeste kurs er da fra dagen før, så raden viser gårsdagens vurdering med sin egen dato (FR-101). Om grunnen skal vises ved siden av, føres i `deferred-work.md` for 8.2.
- `designregler.md` §2: Rettet-merknad om at en dag uten rad viser «– ikke vurdert». Docstringen i `tilstand.py` rettes. `innlevering.md`, `deferred-work.md` (K13 delvis, datoen i overskriften løst i 8.0, det nye punktet for 8.2), README og docstringen i `app.py` følger koden (regel 19).
- Ingen API-kall. `src/fetch_prices.py` kjøres ikke, heller ikke med `--les-inn`.

**Never:** Signalet regnet på sidene. Ny metode på `Vurderingslager` eller `Kurslager`. Børsdagskontrollen (2.3), historikken (2.7), indeksen (2.8), Docker (3.1), demoversjonen (3.4).

## Beslutninger (godkjent 03.10 kl. 22:30)

1. **A:** egen port `Oversiktsleser`, merknad under AD-3, test for ingen skrivemetode.
2. Tekstene over, med «ingen kurs fra dagen» og «utenfor børskalenderen».
3. **A:** synlig liten tekst under «–».
- **Tillegg:** gårsdagens vurdering når dagens rad har en grunn, med test. Rader uten vurdering sist, med test og mutant. Fotnoten. Docstringen i `tilstand.py`. Commit etter hver del.

## I/O & Edge-Case Matrix

| Scenario | Tilstand | Forventet |
|---|---|---|
| Vanlig | Kurser og vurdering for nyeste dato | Styrke, retning og sjekker fra raden |
| Styrke 0 | Vurdering med styrke 0 | «0» og «Ingen», ikke «–» |
| Grunn | Rad med grunn for nyeste dato | «–», tekst for grunnen, «Ukjent» |
| Ikke kjørt | Kurser uten rad (`--les-inn`) | «– ikke vurdert», fotnoten |
| Gårsdagens | Dagens rad `symbol_feilet`, nyeste kurs i går med vurdering | Gårsdagens vurdering, med gårsdagens dato |
| Ingen kurser for en aksje | Aksje i `aksje` uten kurs | Navngis under tabellen |
| Færre aksjer | `aksje` har færre enn 15 | Like mange rader som i `aksje` |
| Utenfor kalenderen | Nyeste kurs i et år utenfor `DEKKEDE_AAR`, ingen rad | «– utenfor børskalenderen», ikke 500 |

</frozen-after-approval>

## Code Map

- `src/app.py` -- rutene, `hent_leser`, `AKSJEUNIVERS` l. 191 og 214. Får klokke og `hent_oversiktsleser()`.
- `src/markedsoversikt.py` -- `Rad`, `bygg_rad`, `bygg_oversikt`, `_sorteringsnokkel`, `RETNINGSVISNING`, `UKJENT_RETNING`. `beregn_signal` ut.
- `src/aksjedetalj.py` -- `Detalj`, `SjekkVisning`, `bygg_detalj`, `finn_aksje`, `bygg_punkter` (står). `beregn_signal` og `Detalj.har_ma50` ut.
- `src/signalberegning.py` -- `_trendforklaring`, `_bevegelsesforklaring`, `_interesseforklaring`, `_nodvendige_dager`. Får en offentlig `forklaringer(...)` og `nodvendige_dager(p)`, så tekstene er de samme.
- `src/lagring_sqlite.py` -- `SqliteKurslager`, `VURDERINGSKOLONNER`, `_krev_siste_versjon`. Får `SqliteOversiktsleser`.
- `src/tilstand.py` -- `tilstand`, `Art`. Bare docstringen endres.
- `src/templates/index.html`, `src/templates/aksje.html` -- «–» med tekst, fotnoten.
- `tests/test_app.py` -- `monter`, `monter_lager` og `fyll_basen` skrives om til å fylle basen med kurser og vurderinger. Fast klokke i testene.
- `tests/test_markedsoversikt.py`, `tests/test_aksjedetalj.py` -- skrives om til den nye API-en. K13: `Punkt` og `Rad` importeres uten bruk.

## Tasks & Acceptance

**Execution:**
- [x] `src/oversiktsdata.py`, `src/lagring_sqlite.py`, tester -- porten, adapteren og spørringen. Commit.
- [x] `src/markedsoversikt.py`, `src/app.py`, `src/templates/index.html`, tester -- oversikten. Commit.
- [x] `src/aksjedetalj.py`, `src/signalberegning.py`, `src/templates/aksje.html`, tester -- aksjedetaljen. Commit.
- [x] Mutantene og kontrollregningen. Spinen, `designregler.md`, `tilstand.py`, `deferred-work.md`, `innlevering.md`, README. Commit.

**Acceptance Criteria:**
- Given en kopi av basen etter hentingen 02.10, when sidene vises på main (signalet regnet) og etter 2.2b (vurderingen lest), then styrke, retning og sjekker er like for alle aksjene. Bare antallet føres.
- Given en rad uten vurdering og en med styrke 0, when oversikten vises, then raden uten vurdering står sist.

## Implementation Notes

- Bygget 03.10 direkte i økta, ikke av en egen implementasjonsagent, som i 2.2. Fire commits på grenen, én per del: porten (`37748ce`), oversikten (`31761ed`), aksjedetaljen (`f9382f8`) og dokumentene.
- **Porten:** `oversiktsdata.py` med `Oversiktspost` og `Oversiktsleser` (`oversikt()`, `post(symbol)`). `SqliteOversiktsleser` i `lagring_sqlite.py` kjører én spørring: `aksje` med `LEFT JOIN` mot `kursserie`, nyeste kurs (`MAX(dato)`), forrige kurs (`MAX(dato) < nyeste`) og `vurdering` for datoen til nyeste kurs, sortert på `aksje.rowid`. `_innhold` gjør raden om til `Vurdering` eller `Grunn`, felles med `SqliteVurderingslager.les`.
- **Oversikten:** `bygg_rad(post, idag, p)` og `bygg_oversikt(poster, idag, p)`. `les_tilstand` gir tilstanden og teksten under «–», og fanger `UtenforKalenderen` og en dato etter i dag. `uten_kurser(poster)` gir lista over aksjer som mangler. `Rad` har `tilstand` og `tekst` i stedet for `signal` og `mangler`, og «skiller seg ut» er den lagrede styrken mot `p.terskel`.
- **Valg som ikke sto i planen:** en nyeste kurs med dato etter dagens dato i Oslo gir teksten «datoen er etter i dag» i stedet for 500. `tilstand()` reiser `ValueError` da. Det skjer bare med en klokke eller en kilde som tar feil.
- **app.py:** `naa()` og `idag()` er klokka testene stiller, og `hent_oversiktsleser()` er kroken for porten. Ingen SQL, og verken `AKSJEUNIVERS`, `beregn_signal` eller `vurder`. Aksjedetaljen slår opp med `normaliser_symbol` (store bokstaver, uten mellomrom) i `aksje`.
- **Aksjedetaljen:** `bygg_detalj(post, rader, idag, p)`. `sjekker_fra(vurdering, p)` i `signalberegning.py` bygger de tre sjekkene av verdiene og målingene i raden med de samme forklaringsfunksjonene, så tekstene er like. For `signal_ikke_regnet` sier siden hvor mange dager signalet trenger (`nodvendige_dager`) og hvor mange serien har, som før. `finn_aksje` og `Detalj.har_ma50` er fjernet.
- **Testene i `test_app.py`** fyller basen i `tmp_path` med kurser og med vurderingen `vurder()` gir for nyeste dag, skrevet med adapterens `_UPSERT` uten datokontrollen i `skriv`, fordi testseriene ikke ligger på inneværende børsdag. Klokka står fast på 31.12.2026. `test_feil_mens_sidene_leser_gir_503` låser nå også `SqliteOversiktsleser.oversikt`, fordi oversikten ikke kaller `SqliteKurslager.serie` lenger.
- **Kontrollregning** uten kall, på to kopier av basen i scratchpad, slettet etterpå. Sidene fra main (`a9b87d5`, signalet regnet, i en egen worktree) mot sidene fra grenen (vurderingen lest) for 02.10. 15 av 15 like i styrke, 15 av 15 i retning, og 15 av 15 i sjekkene med navn, fortegn og «målt mot».
- **Tester:** før 1085 passed og 16 skipped lokalt. Etter porten 1100, etter oversikten 1121 og etter aksjedetaljen 1129 passed og 16 skipped. 44 flere testkjøringer, talt med `--collect-only` per fil på main og på grenen: `test_oversiktsleser.py` 0 til 15, `test_markedsoversikt.py` 38 til 50, `test_aksjedetalj.py` 24 til 27 (de 4 i `TestFinnAksje` er byttet med 2 for `normaliser_symbol`) og `test_app.py` 65 til 79.
- **Mutantene**, én om gangen, hele `tests/` hver gang, satt tilbake fra en kopi i scratchpad med sha256 sjekket:

| Mutant | Feilet | Testen som fanget den |
|---|---:|---|
| M1 siden regner signalet når raden mangler (`vurder` i ruta) | 1 | `test_ikke_vurdert_med_fotnoten` (oversikten) |
| M2 raden leses for nyeste dato i `vurdering`, ikke for nyeste kursdato | 3 | `test_gaarsdagens_vurdering_naar_dagens_rad_har_grunn` i begge filene, `test_ingen_rad_gir_none` |
| M3 forrige kurs blir lik nyeste (`<=`) | 2 | `test_nyeste_og_forrige_kurs_og_hentet`, `test_en_kurs_gir_ingen_forrige` |
| M4 lista over aksjer som mangler, fra `AKSJEUNIVERS` | 2 | `test_selskapene_og_lista_over_manglende_kommer_fra_aksje`, `test_app_har_ingen_sql_og_regner_ikke_signalet` |
| M5 en rad med grunn vises som styrke 0 | 9 | `test_rad_med_grunn_viser_grunnen_ikke_styrke_0` (alle tre grunnene) og seks til |
| M6 styrke 0 vises som «–» (`{% if rad.styrke %}`) | 1 | `test_styrke_0_vises_som_0` |
| M7 aksjedetaljen forklarer med et signal regnet av serien | 2 | `test_sjekkene_og_maalingene_fra_raden_ikke_fra_serien`, `test_sjekkene_fra_raden_ikke_fra_kursene` |
| M8 aksjedetaljen slår opp i `AKSJEUNIVERS` | 2 | `test_aksjen_slaas_opp_i_basen`, `test_app_har_ingen_sql_og_regner_ikke_signalet` |
| M9 `UtenforKalenderen` fanges ikke for seg | 1 | `test_utenfor_boerskalenderen_gir_tekst_ikke_feil` |
| M10 spørringen i `app.py` | 1 | `test_app_har_ingen_sql_og_regner_ikke_signalet` |
| M11 rader uten vurdering sorteres som styrke 0 | 1 | `test_rad_uten_vurdering_staar_bak_styrke_0` |

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q` -- grønn. Før: 1085 passed og 16 skipped lokalt, 1101 i CI på main (kjøring 37149857722).

**Mutantene**, én om gangen, satt tilbake fra en kopi med sha256. Hver føres med testen som fanget den:
1. Siden regner signalet når raden mangler. 2. Raden leses for dagens dato i stedet for nyeste kursdato. 3. Forrige kurs blir lik nyeste. 4. Lista over aksjer som mangler, fra `AKSJEUNIVERS`. 5. En rad med grunn vises som styrke 0. 6. Styrke 0 vises som «–». 7. Aksjedetaljen forklarer med et signal regnet av serien. 8. `finn_aksje` mot `AKSJEUNIVERS`. 9. `UtenforKalenderen` fanges ikke. 10. Spørringen i `app.py`. 11. Rader uten vurdering sorteres som styrke 0.
