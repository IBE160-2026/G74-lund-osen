---
title: 'Story 8.0b: Hjelp bak et spørsmålstegn'
type: 'feature'
created: '2026-10-11'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '00a69ceb262e1850e53d9a4320b84772b88b51ba'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-0-de-rene-feilene-i-de-to-skjermbildene.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Sidene forklarer signalstyrken bare i en fotnote, og retningen, sjekkene og grensene ikke i det hele tatt. Den som ikke har bygget appen, må spørre noen (story 8.0b, raden «Hjelp bak et spørsmålstegn» i `prd.md` §8).

**Approach:** Et «?» åpner et lite vindu med fast tekst, uten nettkall, uten skript og uten KI. Tekstene ligger i én kjernemodul, og tallene i dem kommer fra `Parametre`.

## Planen

Planen ble vist i chatten 11.10 og er ført i `docs/ai-prompts/2026-10-11.md` (instruksjonen kl. 11:05 og Utført-linjen). Gruppen sa ja kl. 11:33 med disse svarene, som er beslutninger:

1. **Mekanismen er `popover`**, ren HTML, uten skript.
2. **Plassering:** «?» ved overskriften på begge sidene, og ved Signalstyrke i kolonneraden i oversikten. Det skal ikke stå et «?» ved «Hvorfor signalet ble …». Det kan tas opp etter brukertesten (8.1).
3. **Tekstene** er godkjent med disse endringene:
   - sluttkurs: «kursen ved børsens stengning siste børsdag i dataene, uten utbyttejustering»
   - signalstyrke: styrken teller sjekkene som ga +1 eller -1, så +1 og -1 gir 2. Det står ikke «summen uten fortegn» og ingenting om hvor kraftig sjekkene slår ut, bare at styrken ikke sier hvor sannsynlig en kursbevegelse er
   - trend: «den utbyttejusterte kursen», ikke «sluttkursen»
   - interesse: sjekken gir 0 når kursen var uendret
   - skjevhet og ukjent står som i utkastet
4. **«50-dagers snitt» i `aksje.html`** hentes også fra `Parametre`, både i tegnforklaringen og i `aria-label`.
5. **8.0b venter** til PR #28 (2.3b) er flettet etter hentingen mandag 12.10. Gir det konflikt, hentes main inn i grenen med merge, aldri med rebase eller force-push (regel 7).

## Boundaries & Constraints

**Always:**
- Hver tekst har kilden sin, som en fil og et sted i den. Tekstene sier bare det koden gjør og det kilden sier.
- Tall som er parametre, kommer fra `Parametre` og vises med `tall()` (regel 21). Tall som er målinger (199 børsdager, 15 aksjer, 60,0 % og 29,5 %), er egne konstanter med kilde.
- Retningen forklares med ordene og symbolene i `RETNINGSVISNING` (FR-704, FR-103). «Ingen» og «Ukjent» er to tekster.
- Det er fortsatt fem kolonner (FR-101). Hjelpen er grå, aldri gul (designregler §3).
- Grenen bruker bare testbaser (regel 22).

**Never:**
- Ingen `<script>` og ingenting fra nettet.
- Ingen ord som kan leses som et råd (NFR-06). Bare `ikke_raad` nevner kjøpe og selge.
- `fetch_prices.py`, `signalberegning.py` og basen endres ikke.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Oversikten | base med rader | «?» ved overskriften og ved Signalstyrke, to vinduer | — |
| Tom base | ingen kurser | «?» ved overskriften, og vinduet virker | — |
| Aksjedetaljen | kjent symbol | «?» ved overskriften, og vinduet har grafen og Ga/Målt mot | — |
| Demobasen | `OSE_DEMO=1` | som over, med «Eksempeltall» | — |
| Ukjent nøkkel | malen ber om en tekst som ikke finnes | siden feiler i testen | `KeyError` med nøkkelen |

</frozen-after-approval>

## Code Map

- `src/tallformat.py` -- `DESIMALER` får slag for heltall, faktor, grense og andel.
- `src/hjelpetekster.py` (ny, kjerne) -- `Hjelpetekst(tittel, tekst, kilder)`, `hjelpetekster(p)`, `Hjelp.tekst(noekkel)`. Importerer bare `signalberegning`, `markedsoversikt` (`RETNINGSVISNING`, `UKJENT_RETNING`) og `tallformat`.
- `src/templates/_hjelp.html` (ny) -- makroene `hjelpestil`, `hjelpeknapp` og `hjelpevindu`. Vinduene står sist i `<body>`, fordi en `<th>` ikke kan ha overskrifter.
- `src/app.py` -- context processoren får `hjelp` og `parametre`.
- `src/templates/index.html`, `aksje.html` -- knappene, vinduene og `{{ parametre.ma_vindu }}`.
- `tests/test_konsumentene.py` -- `KJERNEMODULER` får `hjelpetekster.py`.
- Spinen -- mappetreet i Structural Seed.

## Tasks & Acceptance

**Execution:**
- [x] a. `src/tallformat.py`, `tests/test_tallformat.py` -- de nye slagene.
- [x] b. `src/hjelpetekster.py`, `tests/test_hjelpetekster.py` -- tekstene, kildene og testene for kontrollpunktene.
- [x] c. `src/templates/_hjelp.html`, `index.html`, `aksje.html`, `src/app.py` -- «?» og vinduene, og MA-vinduet fra `Parametre`.
- [x] d. `tests/test_demo.py` -- «?» og tekstene med demobasen.
- [x] e. Spinen og `tests/test_konsumentene.py`.
- [x] f. `README.md` (Status) og `sprint-status.yaml`. `docs/kvalitetssikring.md` utgår, se Implementation Notes.

**Acceptance Criteria:**
- Given andre parametre, when tekstene lages, then står de nye tallene, og ingen av de gamle.
- Given hver side, when den rendres, then har hver `popovertarget` et `id` på samme side, og siden har ingen `<script` og ingen adresse på nettet.
- Given hver tekst, then finnes kildefila, og stedet står i den.

## Implementation Notes

- **Commitene:** spesifikasjonen `ad89f84`, a `99c919f`, b `7372203`, c `f79633e`, d `e9a198d`, e `22a3d2d`, testene etter M12 `ccdd7ee`, og så f.
- **Slagene i `tallformat`:** planen hadde bare `faktor`. `heltall`, `grense` og `andel` kom til, så nøytralsonen (2 %), vinduene og de målte andelene (60,0 %) også vises med desimalene bestemt i `tallformat` (regel 21).
- **Avvik fra de godkjente tekstene.** Alle er gjort for at teksten skal si det koden gjør:
  - `ukjent_aksje` er ny. I aksjedetaljen står grunnen under «Hvorfor signalet ble ukjent», ikke under signalstyrken som i oversikten. `ukjent` står uendret i oversikten.
  - `signalstyrke` slutter med «i oversikten», fordi merket «skiller seg ut» bare står der.
  - `retning`, `uten_styrke`, `antall_dager` og `ikke_raad` er hele setninger uten fet tittel, som i utkastet.
  - `ga_og_maalt` ble to tekster, `ga` og `maalt_mot`, med hver sin fete tittel, som i utkastet.
  - `endring` står ikke i aksjedetaljen, fordi siden ikke viser endringen.
- **Kildene** er par av (fil, sted), der stedet står ordrett i fila. Kilden til `endring` siterte først PRD-raden med EODHDs feltnavn `adjusted_close`. Vakten i `test_konsumentene.py` fanget det da modulen kom i `KJERNEMODULER`, og stedet er kortet ned (`22a3d2d`).
- **Malene:** makroene ligger i `_hjelp.html` og importeres `with context`. Teksten hentes med `hjelp.tekst()` og ikke med `hjelp[...]`, fordi Jinja gjør en manglende nøkkel i `[]` om til en tom verdi. Vinduene står sist i `<body>`, fordi en `<th>` ikke kan ha overskrifter.
- **To tester i `test_app.py`** så etter ordene «Signalstyrke» og «Målt mot», som nå også står i hjelpen. De ser nå etter tabellcellen.
- **`docs/kvalitetssikring.md` er ikke endret.** §8 sier at dokumentet oppdateres ved hver epic, og 2.3 og 3.1–3.4 har heller ingen rad ennå. Mutantene står under Verification med testene som fanget dem, som §8 krever fra 03.10.
- **README:** Status-linjen sier at 2.3b og 8.0b er flettet. Det stemmer når 8.0b flettes, fordi 8.0b venter på PR #28 (svar 5).
- **Regel 22:** basene i testene ligger i `tmp_path`. HTML-en ble kontrollert én gang med en demobase i scratch-mappa for økta.

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q` -- forventet: alle grønne. Før: 1269 passed og 16 skipped lokalt, 1285 i CI.
- Mutantene, én om gangen, med koden satt tilbake fra en kopi og sha256 kontrollert. Hver mutant skal få minst én test til å feile.

**Mutantene** (hele testsettet for hver, 11.10):

| # | Mutanten | Fanget av |
|---|---|---|
| M1 | «50» skrevet fast i `trend` | `test_andre_parametre_gir_andre_tall` |
| M2 | «1,5» skrevet fast i `interesse` | `test_andre_parametre_gir_andre_tall` |
| M3 | `faktor` med 0 desimaler | `test_dagens_tall_staar_i_tekstene`, `test_andre_parametre_gir_andre_tall`, `test_tallet_som_vises_er_parameteren[1.5-faktor]`, `test_slagene_i_hjelpetekstene` |
| M4 | nøkkelen `uten_data` fjernet fra fila | 65 tester, blant dem `test_hver_tekst_malene_ber_om_finnes` og `test_hver_tekst_i_fila_brukes_av_en_mal` |
| M5 | Ukjent slått sammen med Ingen | `test_ingen_og_ukjent_forklares_hver_for_seg` |
| M6 | «Opp» i stedet for Positiv | `test_ordet_og_symbolet_er_fr_704_sine[positiv-Positiv]`, `test_ikke_opp_og_ned_som_navn` |
| M7 | «bør» i `hvorfor_tre` | `test_ingen_tekst_kan_leses_som_et_raad` |
| M8 | kilden til `hvorfor_tre` tatt bort | `test_hver_tekst_har_en_kilde_som_finnes` |
| M9 | «?» ved Signalstyrke fjernet | `test_spoersmaalstegn_ved_signalstyrke_i_oversikten`, og etter `ccdd7ee` også `test_hver_knapp_aapner_et_vindu_paa_samme_side` og `test_hjelpen_virker_ogsaa_i_demoen` |
| M10 | `<script src="https://…">` i `index.html` | `test_ingen_skript_og_ingenting_fra_nettet` |
| M11 | `id` som ikke passer med `popovertarget` | 5 tester, blant dem `test_hver_knapp_aapner_et_vindu_paa_samme_side` og `test_hjelpen_virker_ogsaa_i_demoen` |
| M12 | «?» skjult når siden viser «Eksempeltall» | **overlevde først**, fordi lukkeknappen i vinduet også har `popovertarget`. Fanget av `test_hjelpen_virker_ogsaa_i_demoen` etter `ccdd7ee` |
| M13 | «50-dagers snitt» skrevet fast i `aksje.html` | `test_ma_vinduet_kommer_fra_parametre` |
