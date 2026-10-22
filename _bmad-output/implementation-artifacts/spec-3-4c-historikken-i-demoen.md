---
title: 'Story 3.4 (3.4c): historikken i demoen som den ekte'
type: 'feature'
created: '2026-10-22'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '5ff304f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/ux-logg.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-7b-signalet-dag-for-dag.md'
---

## Intent

**Problem:** demoen har en vurdering for hver aksje hver børsdag fra 02.01.2026, så «Signalet dag for dag» viser signal hele året. Den ekte versjonen har signal bare fra første henting, og «ikke vurdert» før.

**Grunnlaget:** avgjørelsen 21.10 kl. 23:09 under «Prioritering» og story 3.4 i `epics.md`: «historikken i demoen («Signalet dag for dag», 2.7b) viser det samme bildet som den ekte: signal bare fra en startdag noen uker før siste demodag, og «ikke vurdert» før. Det må passe med de 10 fargekombinasjonene på siste demodag (avgjørelsen 16.10 kl. 21:49, 3.4) og KI-tekstene i demoen (3.4b).» U45 i `docs/ux-logg.md`, og gruppens svar 22.10 kl. 18:20 om å ta den nå, før 8.6. Instruksjonen er den kl. 19:31 i dagsfila 22.10. Bare demoen endres.

## Slik virker det i dag (slått opp 22.10 på `5ff304f`)

- **`_bygg` i `src/demo.py`** skriver kursene for alle 195 handelsdagene fra `FOERSTE_DAG` (02.01) til `SLUTTDATO` (09.10), og så, for hver handelsdag og hver aksje, det `vurder()` gir for serien fram til dagen, med `SqliteVurderingslager` og lagerets klokke stilt på dagen kl. 22:30 (`_klokke_for`, AD-7, merknaden 2026-10-03). KI-radene skrives for `SLUTTDATO` med klokka stilt på den dagen.
- **Den ekte versjonen** skriver en vurdering bare for inneværende børsdag (AD-7), så dagene før første henting har ingen rad. Historikken går gjennom `les_tilstand`, og en dag med kurs uten rad står uten signal. `docs/hjelp.md`: «En dag uten vurdering står med «–» og grunnen, og dagene før første og etter siste kurs står tomme. Det gjelder både demoen og den ekte versjonen.»
- **En demobase fra før** lages på nytt i Docker hver gang demoen starter (`demo-lag` i `compose.yaml` kjører `src/demo.py`). Med uv lages den bare når `uv run python src/demo.py` kjøres, og webserveren lager den aldri (AD-10). En demobase fra før denne endringen kan altså bli vist med den gamle historikken når demoen startes med uv.

## Kontrollpunktene

- a) Demoen: vurderingene skrives bare fra mandag 21.09.2026 (`STARTDAG`), tre uker før siste demodag fredag 09.10. Dagene før står uten signal, slik den ekte viser dagene før første henting. Kursene, de 10 fargekombinasjonene på 09.10 og KI-tekstene for 09.10 er som før. En demobase fra før endringen, med en vurdering før `STARTDAG`, vises ikke: webserveren sier at den er laget av en eldre versjon av demoen, og viser kommandoen som lager den på nytt. README-en, `docs/hjelp.md` og hjelpetekstene følger med der de sier noe om historikken i demoen (regel 19), og bildene tas på nytt bare hvis testene krever det.
- b) Testene, med «Ville feilet hvis», uten nett.

## Planen, én commit per punkt

1. a) `STARTDAG` og løkka i `_bygg`, docstringen i `demo.py`, `gammel_demobase` i `demo.py`, og i `app.py` at en demobase fra før vises som «laget av en eldre versjon», med en egen setning i `index.html`. Fingeravtrykkene av demobasen i `tests/test_demo.py` og avtrykkene bak bildene i `tests/test_docker.py` følger med, med grunnen, i samme commit, så hver commit er grønn. Tekstene.
2. b) De nye testene.

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter:

- **M1:** en vurdering før startdagen.
- **M2:** en børsdag etter startdagen uten vurdering.
- **M3:** startdagen flyttet.

## Det som ikke endres

- Den ekte versjonen, hentingen og lagrene. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` røres ikke (regel 22), og demobaser lages bare i midlertidige mapper.
- Grenen for 2.3c røres ikke.
