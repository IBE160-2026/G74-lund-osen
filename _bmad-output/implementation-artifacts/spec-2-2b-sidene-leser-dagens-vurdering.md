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
- [ ] `src/oversiktsdata.py`, `src/lagring_sqlite.py`, tester -- porten, adapteren og spørringen. Commit.
- [ ] `src/markedsoversikt.py`, `src/app.py`, `src/templates/index.html`, tester -- oversikten. Commit.
- [ ] `src/aksjedetalj.py`, `src/signalberegning.py`, `src/templates/aksje.html`, tester -- aksjedetaljen. Commit.
- [ ] Mutantene og kontrollregningen. Spinen, `designregler.md`, `tilstand.py`, `deferred-work.md`, `innlevering.md`, README. Commit.

**Acceptance Criteria:**
- Given en kopi av basen etter hentingen 02.10, when sidene vises på main (signalet regnet) og etter 2.2b (vurderingen lest), then styrke, retning og sjekker er like for alle aksjene. Bare antallet føres.
- Given en rad uten vurdering og en med styrke 0, when oversikten vises, then raden uten vurdering står sist.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q` -- grønn. Før: 1085 passed og 16 skipped lokalt, 1101 i CI på main (kjøring 37149857722).

**Mutantene**, én om gangen, satt tilbake fra en kopi med sha256. Hver føres med testen som fanget den:
1. Siden regner signalet når raden mangler. 2. Raden leses for dagens dato i stedet for nyeste kursdato. 3. Forrige kurs blir lik nyeste. 4. Lista over aksjer som mangler, fra `AKSJEUNIVERS`. 5. En rad med grunn vises som styrke 0. 6. Styrke 0 vises som «–». 7. Aksjedetaljen forklarer med et signal regnet av serien. 8. `finn_aksje` mot `AKSJEUNIVERS`. 9. `UtenforKalenderen` fanges ikke. 10. Spørringen i `app.py`. 11. Rader uten vurdering sorteres som styrke 0.
