---
title: 'Story 8.0f: hjelpen ved «?» i et fast felt som ikke dekker siden'
type: 'feature'
created: '2026-10-26'
status: 'done'
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
  *Rettet 2026-10-26 (gjennomgangen, BH3 og ECH2):* bred er fra 1056 px, ikke 1024. Feltet tar 432 px med luften, og 1024 − 432 = 592 px. Med 1056 px er det 624 px, og minst 600 px også med et vanlig rullefelt på 17 px.
- **«Rett under «?»»** er under den nærmeste blokken med «?» som står alene i bredden: i en tabell en ny rad under kolonneraden, i en overskrift under overskriften, og i et kort i et rutenett med flere kolonner under hele rutenettet.
  *Rettet 2026-10-26 (punkt a):* blokken er den nærmeste som går over hele bredden, 16 px fra kantene som feltet, målt i nettleseren, ikke den første som står alene i sin forelder. Et kort på aksjesiden sto i en blokk med to kolonner, og feltet over plassen dekket kortet ved siden av ved 390 px.
- **Knappen** heter «Flytt til venstre» eller «Flytt til høyre» og står bare på bred skjerm, fordi feltet på smal skjerm står under «?». Valget lagres i `sessionStorage`, som varer mens fanen er åpen, altså mens man blar. Kan lagringen ikke brukes, flyttes feltet likevel, og valget glemmes på neste side.
- **`test_velg_dag_er_et_skjema_uten_skript`** sier nå at aksjesiden ikke har noe annet skript enn hjelpen. Grunnen er instruksjonen: hjelpen får så lite JavaScript som mulig, og «Velg dag» er fortsatt et skjema uten skript.
- **Nettleseren i testene:** testene skriver siden fra Flasks testklient til en midlertidig mappe med stilarket og skriptet, og kjører Edge eller Chrome uten hode med `--dump-dom` og `file://`. Et testskript på siden trykker på knappene og skriver målingene i siden. Ingen server, ingen port og ingenting fra nettet. Finnes ingen nettleser, hoppes testene over.

## Planen, én commit per punkt

1. Spesifikasjonen.
2. a) `hjelp.js`, lenken i `_ramme.html`, stilen for feltet, `.js` i avtrykket bak bildene, bildene tatt på nytt, `test_velg_dag…` og testene i Python for lenken og at hjelpen uten skript er som før.
3. b) Knappen i `_hjelp.html`, stilen og skriptet.
4. c) Testene i nettleseren, og mutantene. README-en og `docs/hjelp.md` følger med hvis de sier noe om hjelpen.

## Mutantene

Én om gangen med `-x` på `tests/test_hjelpefeltet.py`, med kopi før og fila sammenlignet med HEAD etter (`git hash-object` lik bloben i HEAD).

- **Siden gir ikke plass** (regelen `.hjelpefelt body:has(.hjelpevindu:popover-open)` tatt ut av `stil.css`): fanget på `2889c93` kl. 18:17:23–18:17:25 av `test_ingen_tekst_under_feltet[/aksje/BRFE-1280]`.
- **Esc lukker ikke** (linjen med `Escape` tatt ut av `hjelp.js`): fanget på `2889c93` kl. 18:17:26–18:17:34 av `test_esc_og_lukk_lukker_og_fokus_gaar_tilbake[Esc]`.

## Gjennomgangen

Kjørt 26.10 på `main..2889c93`, etter hele settet: Blind Hunter (BH) 18 funn, Edge Case Hunter (ECH) 8 og Verification Gap (VG) 7. Dommen er vår, ikke linsens.

| Funn | Hva | Dom | Utfall |
|---|---|---|---|
| BH1 | Fokus tilbake til «?» bladde siden tilbake etter at man hadde bladd med feltet åpent | medium | rettet: `focus({ preventScroll: true })`, og testen sjekker at siden ikke blar |
| BH2 | Testene målte med reserveskrifter, fordi `url("/static/` ikke fantes under `file://` | medium | rettet: skriftene ved siden av, og testen krever at IBM Plex Sans er lastet |
| BH3, ECH2 | Ved 1024 px fikk innholdet 592 px, ikke 600 | medium | rettet: grensen er 1056 px |
| BH4, ECH1 | Plassen og feltet fulgte ikke med når siden endret størrelse | medium | rettet: `ResizeObserver` på `body` og feltet |
| BH5, VG1 | `document.body.click()` prøvde ikke at et klikk utenfor ikke lukker | medium | rettet: pekerhendelser, og testen krever `popover === "manual"` |
| BH6, VG6 | Nettleseren kunne nå nettet, og testene kunne hoppes over i CI uten at noen så det | medium | rettet: `--proxy-server` og `--host-resolver-rules`, og testene feiler i CI uten nettleser |
| BH7 | En rad i en tabell fikk plassen uten å sjekke at tabellen går over hele bredden | lav | rettet: `hel()` på tabellen |
| BH8, ECH4 | Løkka som finner blokken, kunne gå forbi `body` | lav | rettet |
| BH9 | Testen godtok 5 «?» og hoppet stille over resten | lav | rettet: hvert «?» på siden, og ingen hoppet over |
| BH10 | Valget ble ikke prøvd over en navigering | lav | rettet: knappen på aksjesiden, så oversikten i samme fane |
| BH11, ECH6 | Esc lukket også når en annen kontroll hadde brukt den | lav | rettet: `!e.defaultPrevented` |
| BH12, VG2 | Testen uten lagring sjekket ikke at lagringen kastet | lav | rettet |
| BH13, VG3 | En sjekk kunne ikke feile, og «Flytt» uten skriptet var ikke prøvd | lav | rettet: reglene uten klassen er en fast liste, og «Flytt» har `hidden` |
| BH14 | Lista over det skriptet ikke skal bruke, var kort | lav | rettet |
| BH15 | «Flytt til venstre» sier ikke hva som flyttes | lav | avvist: knappen står i feltet merket «Hjelp» |
| BH16 | Docstringen i `_stilark` nevnte bare stilarket | lav | rettet; navnet beholdes |
| BH17 | `SKRIFTFILER` har nå `.js` | lav | avvist: kommentaren over settet sier det |
| BH18 | Mutantene sto ikke i diffen | lav | avvist: de står over og i Utført-linja |
| VG4 | Byttet på smal skjerm var ikke prøvd | lav | rettet: 390 px, med én plass etter byttet |
| VG5 | Fokus og Esc var bare prøvd på bred skjerm | lav | rettet: 390 px, og ingen plass etter lukkingen |
| VG7 | Børsometeret var ikke med i nettlesertesten | lav | rettet |
| ECH3 | Nettlesere uten `popover` fikk feltene lagt over siden | lav | rettet: skriptet gjør ingenting da |
| ECH5 | Fokus tilbake til et «?» som ikke vises | lav | rettet |
| ECH7 | En side fra hurtigbufferen ved «Tilbake» leste ikke valget | lav | rettet: `pageshow` |
| ECH8 | Tegnene i resultatet ble gjort om i feil rekkefølge | lav | rettet: `html.unescape` |

25 rader: 22 rettet og 3 avvist. Ingen med dom medium eller høyere står urettet.
