---
title: 'Story 2.7 (2.7a): all stilen i én CSS-fil'
type: 'refactor'
created: '2026-10-19'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'a281bfd'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3f-bildene-av-appen-bak-en-knapp.md'
---

## Intent

**Problem:** stilen står i `<style>` i `_ramme.html`, i blokka `stil` i `index.html`, `aksje.html` og `basefeil.html`, og i tre makroer i delmalene (`hjelpestil`, `brikkestil` og `periodestil`). Seks regler står likt i `index.html` og `aksje.html`: `h1.overskrift mark`, `.opp`, `.ned`, `.blandet`, `.ingen, .ukjent` og `p.fotnote`. Tre har samme velger og ulik kropp: `h1.overskrift`, `p.meta` og `.mangler`. Kontrollpunktet i story 2.7 sier at malene deler én layout og én CSS-fil.

**Grunnlaget:** gruppens svar 19.10 kl. 12:06 og instruksjonen 19.10 kl. 13:24. Stilen flyttes nå, som første del av 2.7, før 8.3 og historikken (2.7b). Sidene skal se nøyaktig ut som før.

## Kontrollpunktene

- a) Før noe endres: skjermbilder med fremgangsmåten for bildene, fra en demobase i en midlertidig mappe, av oversikten og aksjesiden i 1280 og 390 px, oversikten sortert, siden for en valgt dag, en dag uten vurdering, et åpent hjelpevindu og feilsiden. De legges i scratchpaden, ikke i repoet.
- b) Fila: én CSS-fil under `src/static/`, lenket fra `_ramme.html` med et avtrykk av fila i adressen, så nettleseren aldri bruker en gammel utgave. All stilen fra rammen, sidene og delmalene flyttes dit, og makroene som bare gir stil, tas bort. De seks like reglene står én gang. Regler med samme velger og ulik kropp avgrenses til siden sin. Ingen mal har `<style>`. Testene som leser stilen fra siden, leser fila, med de samme kravene som før. Fila er med i avtrykkene bak bildene. `designregler.md` og spinen får en datert linje om hvor stilen står.
- c) Kontrollen: de samme skjermbildene fra grenen er like piksel for piksel som i a, og bildene i `docs/appen/` tas på nytt og er like byte for byte. Er noe ulikt, rettes stilen, ikke bildet. Tester med «Ville feilet hvis»: ingen `<style>` i malene, fila svarer 200 fra lenken på hver side, ingen velger står to ganger med samme kropp, og fargene står bare i `:root`. Mutanter én om gangen med `-x` og kopi før og sha256 mot HEAD etter: en `<style>` tilbake i en mal, en regel lagt inn to ganger, og lenken til fila tatt bort.

## Planen, én commit per punkt

1. a) Skjermbildene fra main, før noe endres, i scratchpaden. Ingen commit.
2. b) `src/static/stil.css` med rammen, delmalene, de seks felles reglene og hver side for seg. `_ramme.html` lenker til `/static/stil.css?v=<avtrykk>`, der avtrykket er de første 16 tegnene av sha256 av fila, regnet i `app.py`. `<body>` får klassen til siden. Blokka `stil` og makroene `hjelpestil`, `brikkestil` og `periodestil` tas bort. Hjelperen `_stil` i `tests/test_app.py` leser fila fra lenken og gir reglene som gjelder siden, så testene som leste `<style>`, stiller de samme kravene.
3. c) Skjermbildene fra grenen, bildene i `docs/appen/` på nytt, testene og mutantene.

## Avgjort i spesifikasjonen

- **Navnet på fila** er `src/static/stil.css`, ved siden av skriftene.
- **Avtrykket** er de første 16 tegnene av sha256 av fila, i parameteren `v`. Det regnes ved hver side fra fila som serveres, så en endret fil gir ny adresse uten omstart.
- **Avgrensningen:** hver side har en klasse på `<body>`: `side-oversikt`, `side-aksje` og `side-feil`. Alle reglene som bare sto i én side, avgrenses med `:where(.side-…)`, ikke bare de tre med ulik kropp. Grunnen: en regel fra én side som treffer noe på den andre, endrer den siden, som `figure` og `h2` fra aksjesiden, `table` og `.skjult` fra oversikten. `:where()` gir ingen ekstra spesifisitet, så rekkefølgen og vektene mellom reglene er de samme som før.
- **Rekkefølgen i fila:** skriftene, fargene, rammen, hjelpen, brikkene, periodevalget, de felles reglene, oversikten, aksjesiden og feilsiden. Det er rekkefølgen fra `<style>` i rammen, med blokka `stil` til slutt.
- **Skjermbildene på 390 px:** Edge uten vindu går ikke smalere enn 504 px (målt: `innerWidth` 504 med `--window-size=390,900`). Siden vises derfor i en iframe som er 390 px bred, og skriptet sjekker at `innerWidth` i den er 390.

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Bildene tas fra en demobase i en midlertidig mappe.
- Sidene skal se nøyaktig ut som før.
