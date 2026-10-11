---
title: 'Story 8.0b: Hjelp bak et spørsmålstegn'
type: 'feature'
created: '2026-10-11'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '00a69ce'
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
- [ ] a. `src/tallformat.py`, `tests/test_tallformat.py` -- de nye slagene.
- [ ] b. `src/hjelpetekster.py`, `tests/test_hjelpetekster.py` -- tekstene, kildene og testene for kontrollpunktene.
- [ ] c. `src/templates/_hjelp.html`, `index.html`, `aksje.html`, `src/app.py` -- «?» og vinduene, og MA-vinduet fra `Parametre`.
- [ ] d. `tests/test_demo.py` -- «?» og tekstene med demobasen.
- [ ] e. Spinen og `tests/test_konsumentene.py`.
- [ ] f. `README.md` (Status), `sprint-status.yaml`, `docs/kvalitetssikring.md` (§3 og vedlegget).

**Acceptance Criteria:**
- Given andre parametre, when tekstene lages, then står de nye tallene, og ingen av de gamle.
- Given hver side, when den rendres, then har hver `popovertarget` et `id` på samme side, og siden har ingen `<script` og ingen adresse på nettet.
- Given hver tekst, then finnes kildefila, og stedet står i den.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q` -- forventet: alle grønne. Før: 1269 passed og 16 skipped lokalt, 1285 i CI.
- Mutantene, én om gangen, med koden satt tilbake fra en kopi og sha256 kontrollert. Hver mutant skal få minst én test til å feile.
