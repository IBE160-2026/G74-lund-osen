---
title: 'Story 3.4 (3.4e): fotnoten etter startdagen i demoen, og for i dag'
type: 'bugfix'
created: '2026-10-23'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '651be64'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-4d-fotnoten-ikke-vurdert.md'
---

## Intent

**Problem:** spesifikasjonen 3.4d har to åpne punkter. I demoen forklarer fotnoten en rad «ikke vurdert» med startdagen 21.09, også når raden er fra etter 21.09 (BH3, ECH1 22.10). I den ekte versjonen sier fotnoten at signalet aldri regnes ut bakover, også for dagens børsdag før kveldens henting har skrevet vurderingen (ECH3 23.10).

**Grunnlaget:** gruppens svar 23.10 kl. 15:53 under «Prioritering» og story 3.4: små funn fra en gjennomgang rettes med en gang, først de to åpne punktene i 3.4d. Teksten under er fra instruksjonen 23.10 kl. 16:06 i dagsfila.

## Slik er det i dag (slått opp 23.10 på `651be64`)

- **Fotnoten** står i delmalen `src/templates/_fotnote_ikke_vurdert.html`, og velger demoteksten med `{% if eksempeltall %}`. Aksjesiden (`detalj.ikke_vurdert`), oversikten og Min liste (`ikke_vurdert` fra radene) og børsometeret (`ikke_vurdert` fra rutene) tar den inn.
- **Datoen** for det som er «ikke vurdert»: `detalj.dato` på aksjesiden, `rad.dato` for hver rad på oversikten, og `dagen` på børsometeret. `STARTDAG` kommer fra `src/demo.py`, og `idag()` fra `src/app.py`.
- **Demoen** skriver en vurdering for hver aksje hver børsdag fra `STARTDAG`, så en rad «ikke vurdert» etter 21.09 finnes bare i en base som er endret for hånd, som i testen `test_oversikten_med_en_rad_som_mangler`.

## Kontrollpunktene

- a) Demoteksten står bare for en dag før `STARTDAG`. En dag fra `STARTDAG` og senere uten vurdering får den ekte teksten, også i demoen, slik en kveld uten henting gjør i den ekte versjonen. Testen som sletter en rad 09.10 i demoen, krever da den ekte teksten, med grunnen.
- b) Er dagen som vises, i dag, står det i tillegg i fotnoten: «For i dag kan signalet fortsatt lagres hvis hentingen kjøres ferdig i kveld.» Ellers står den ekte teksten fra kl. 23:19 uendret.
- c) Testene, med «Ville feilet hvis», uten nett: i demoen demoteksten før `STARTDAG` og den ekte teksten etter, på aksjesiden, oversikten og børsometeret; setningen om i dag bare når dagen er i dag, med `idag` satt i testen.
- Hjelpen og `docs/hjelp.md` følger med der de sier det samme (regel 19). Bildene tas på nytt bare hvis testene krever det.

## Planen, én commit per punkt

1. a) `_fotnoten(datoer)` i `app.py` gir malen `fotnote_demo`: sant i demoen når alle datoene som er «ikke vurdert», er før `STARTDAG`. Har oversikten rader både før og etter, står den ekte teksten, fordi den dekker begge. Delmalen bruker `fotnote_demo` i stedet for `eksempeltall`.
2. b) `_fotnoten` gir også `fotnote_i_dag`: sant når en av datoene er `idag()`. Setningen står etter den ekte teksten.
3. c) Testene.

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter: demoteksten for alle dager i demoen, og setningen om i dag for en annen dag.

## Det som ikke endres

- Hentingen, lagrene og demodataene. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` røres ikke (regel 22), og demobaser lages bare i midlertidige mapper.
