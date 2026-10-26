---
title: 'Story 8.0f: hjelpen ved «?» i et fast felt som ikke dekker siden'
type: 'feature'
created: '2026-10-26'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'd0830bb'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-0b-hjelp-bak-et-spoersmaalstegn.md'
---

## Intent

**Problem:** hjelpen ved «?» åpnes i dag midt på siden og dekker det den forklarer (U19), og den lukkes når man klikker utenfor, så den ikke kan stå åpen mens man ser på siden (U28).

**Grunnlaget:** «Prioritering» og story 8.0b i `epics.md`: «Avgjort 2026-10-21 kl. 22:47 (gruppens svar)», «Avgjort 2026-10-24 kl. 11:31 (gruppens svar)» og «Avgjort 2026-10-24 kl. 11:34 (gruppen uten preferanse, rådets forslag)», ført i `d0830bb`. Svarene 24.10 står i repoet bare i instruksjonen 26.10 kl. 17:51 i `docs/ai-prompts/2026-10-26.md`. Instruksjonen er den samme.

## Slik er det i dag (slått opp 26.10 på `d0830bb`)

- **`src/templates/_hjelp.html`** har to makroer. `hjelpeknapp(id, etikett)` er `<button class="hjelpeknapp" popovertarget="…">?</button>`. `hjelpevindu(id, tittel, grupper, vist)` er `<div class="hjelpevindu" popover>` med «Hjelp», «Lukk» (`popovertargetaction="hide"`), tittelen og tekstene fra `hjelp.tekst()`. Ingen skript.
- **`popover`** uten verdi er `auto`: Esc lukker, et klikk utenfor lukker, og et nytt «?» lukker det åpne vinduet og åpner det nye.
- **`src/hjelpetekster.py`** har tekstene. De endres ikke.
- **`src/static/stil.css`:** `.hjelpevindu` er `min(440px, 100vw - 2rem)` bred, høyst 80vh og `margin: auto`, altså midt på skjermen med skygge.
- **«?» brukes** 40 steder i `aksje.html`, `index.html`, `boersometer.html` og `_hovedindeks.html`: i stripa ved «Oppdatert», i kolonneradene i tabellene, i overskrifter og i etikettene i kortene på aksjesiden.
- **Ingen side har skript.** `test_velg_dag_er_et_skjema_uten_skript` i `tests/test_app.py` krever at aksjesiden ikke har `<script`.
- **Bildene** i `docs/appen/` har avtrykk av `_hjelp.html`, `_ramme.html` og stilarket (`MALENE_BAK_BILDET` og `SKRIFTFILER` i `tests/test_docker.py`).

## Kontrollpunktene

- **a) Feltet:** de samme hjelpetekstene, så lite JavaScript som mulig. Feltet får fokus når det åpnes, og fokus går tilbake til «?» når det lukkes. Uten JavaScript virker hjelpen som i dag.
- **b) Knappen** i feltet flytter det til venstre eller høyre, og valget huskes mens man blar. Lagringen i nettleseren tåler å være slått av.
- **c) Testene,** med «Ville feilet hvis», uten nett: feltet dekker ikke teksten ved 1280 og 390 px, prøvd i nettleseren; et nytt «?» bytter innholdet; Esc og «Lukk» lukker; knappen bytter side.

## Avgjort i spesifikasjonen

- **Ett skript, `src/static/hjelp.js`,** lenket fra `_ramme.html` med `defer` og avtrykk som stilarket. Uten skriptet er alt som i dag: vinduene er `popover` (auto) og står midt på skjermen. Skriptet setter klassen `hjelpefelt` på `<html>`, og bare da gjelder stilen for feltet. Det gjør vinduene til `popover="manual"`, så et klikk utenfor ikke lukker, og «?» til `popovertargetaction="show"`, så «?» for det åpne feltet ikke lukker det. Skriptet lukker det åpne feltet før et nytt åpnes, lukker med Esc, gir feltet fokus når det åpnes og fokus tilbake til «?» når det lukkes. Ett felt: bare ett vindu er åpent om gangen, så et nytt «?» bytter innholdet.
- **Bred og smal:** bred er fra 1024 px. Der står feltet fast i høyre kant, 400 px bredt med 16 px luft rundt, og `body` får like mye plass på den siden med `:has(.hjelpevindu:popover-open)`, så siden blir smalere og ingenting ligger under feltet. Under 1024 px står feltet rett under «?»: skriptet setter inn en tom plass i siden like høy som feltet, rett under linja med «?», og legger feltet over plassen. Teksten under flyttes ned. Grensen er valgt så innholdet har minst 600 px ved siden av feltet.
- **«Rett under «?»»** er under den nærmeste blokken med «?» som står alene i bredden: i en tabell en ny rad under kolonneraden, i en overskrift under overskriften, og i et kort i et rutenett med flere kolonner under hele rutenettet.
- **Knappen** heter «Flytt til venstre» eller «Flytt til høyre» og står bare på bred skjerm, fordi feltet på smal skjerm står under «?». Valget lagres i `sessionStorage`, som varer mens fanen er åpen, altså mens man blar. Kan lagringen ikke brukes, flyttes feltet likevel, og valget glemmes på neste side.
- **`test_velg_dag_er_et_skjema_uten_skript`** sier nå at aksjesiden ikke har noe annet skript enn hjelpen. Grunnen er instruksjonen: hjelpen får så lite JavaScript som mulig, og «Velg dag» er fortsatt et skjema uten skript.
- **Nettleseren i testene:** testene skriver siden fra Flasks testklient til en midlertidig mappe med stilarket og skriptet, og kjører Edge eller Chrome uten hode med `--dump-dom` og `file://`. Et testskript på siden trykker på knappene og skriver målingene i siden. Ingen server, ingen port og ingenting fra nettet. Finnes ingen nettleser, hoppes testene over.

## Planen, én commit per punkt

1. Spesifikasjonen.
2. a) `hjelp.js`, lenken i `_ramme.html`, stilen for feltet, `.js` i avtrykket bak bildene, bildene tatt på nytt, `test_velg_dag…` og testene i Python for lenken og at hjelpen uten skript er som før.
3. b) Knappen i `_hjelp.html`, stilen og skriptet.
4. c) Testene i nettleseren, og mutantene. README-en og `docs/hjelp.md` følger med hvis de sier noe om hjelpen.
