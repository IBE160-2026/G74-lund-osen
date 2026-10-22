---
title: 'Story 3.4 (3.4d): fotnoten for «ikke vurdert» i demoen og den ekte versjonen'
type: 'feature'
created: '2026-10-22'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f4f0875'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-4c-historikken-i-demoen.md'
---

## Intent

**Problem:** fotnoten for «ikke vurdert» sier at hentekommandoen ikke har skrevet en vurdering, «for eksempel fordi kursene er lest inn med `--les-inn`». I demoen, der vurderingene starter 21.09 (3.4c), stemmer ikke det (ECH2, åpent punkt i spesifikasjonen 3.4c).

**Grunnlaget:** gruppens svar 22.10 kl. 20:11 under story 3.4 i `epics.md`, med tekstene ordrett. Den ekte versjonen: «Ikke vurdert»: signalet lagres bare den kvelden kursene hentes, og regnes aldri ut bakover. Det gjelder dagene før første henting, og dager der kursene er lest inn med --les-inn. Demoen: «Ikke vurdert»: i demoen starter vurderingene mandag 21.09, slik den ekte versjonen har signal fra første henting. Datoen i demoteksten kommer fra `STARTDAG` i `src/demo.py`. Instruksjonen er den kl. 20:13 i dagsfila 22.10.

## Slik er det i dag (slått opp 22.10 på `f4f0875`)

- **Fotnoten står to steder:** `src/templates/aksje.html` (siden for en dag uten vurdering, når dagen har kurs, `detalj.ikke_vurdert`) og `src/templates/index.html` (under tabellen, når en rad er «ikke vurdert»). Begge sier: «Ikke vurdert»: hentekommandoen har ikke skrevet en vurdering for dagen, for eksempel fordi kursene er lest inn med `--les-inn`.
- **Malene vet at det er demoen** gjennom `eksempeltall`, som `_eksempeltall` i `src/app.py` gir hver side (demomerket i basen). `aksje.html` og `index.html` bruker det alt for «Demo Børs».
- **`docs/hjelp.md` og `src/hjelpetekster.py`** sier ikke det fotnoten sier. Hjelpen sier at en dag uten vurdering står med «–» og grunnen, og at demoen starter vurderingene 21.09.

## Kontrollpunktene

- a) Fotnoten begge steder, med den ekte teksten i den ekte versjonen og demoteksten i demoen. Datoen i demoteksten kommer fra `STARTDAG`, gjennom `_eksempeltall` i `app.py`, med ukedagen. Bildene tas på nytt bare hvis testene krever det.
- b) Testene, med «Ville feilet hvis», uten nett, på aksjesiden for en dag før startdagen og på oversikten.

## Planen, én commit per punkt

1. a) `demo_startdag` i `_eksempeltall`, «mandag 21.09» regnet fra `STARTDAG`, og fotnoten i de to malene. Avtrykkene bak bildene følger med, med grunnen, så hver commit er grønn.
2. b) De nye testene.

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter: den ekte teksten i demoen, demoteksten i den ekte versjonen, og en fast dato i stedet for `STARTDAG`.

## Det som ikke endres

- Hentingen, lagrene og demodataene. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` røres ikke, og demobaser lages bare i midlertidige mapper. Grenen for 2.3c røres ikke.
