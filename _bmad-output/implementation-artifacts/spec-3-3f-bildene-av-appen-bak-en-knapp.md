---
title: 'Story 3.3 (3.3f): bildene av appen bak en knapp, i en egen mappe'
type: 'feature'
created: '2026-10-19'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '88b305d'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3b-readme-for-sensor.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3e-bildet-uv-og-variablene.md'
---

## Intent

**Problem:** bildet av oversikten i demoen står under «Til faglærer» i README-en, i `docs/bilder/readme/` sammen med bildene fra «Kom i gang». Appen endres hele tiden, og det kommer flere bilder og senere en video av den.

**Grunnlaget:** gruppens svar 18.10 kl. 23:03 og instruksjonen 19.10 kl. 11:11. Det endrer plassen fra svaret 18.10 kl. 00:20 og svar 4 i spesifikasjonen for 3.4 (11.10).

## Kontrollpunktene

- a) Mappa: `docs/appen/` for bilder og video av appen, bare av demoen (regel 16). `oversikten-demo.png` flyttes dit med `git mv`, og testene og feilmeldingen om hvordan bildet tas, følger med. Bildene fra «Kom i gang» blir i `docs/bilder/readme/`. «Mappestruktur» nevner mappa.
- b) Knappen: rett under beskrivelsen, før «Innhold», en knapp «Bilder av appen (demoen)», lukket som de andre. Den har bildet av oversikten og et nytt bilde av aksjesiden for KVST i demoen, med grafen og KI-teksten, hvert med alt-tekst og en kort tekst under om at det er demoen med oppdiktede tall. Bildet under «Til faglærer» står ikke der lenger. Aksjesiden tas med samme fremgangsmåte, 1280 px bred og så høy at KI-teksten er med, uten sti, brukernavn eller tekstfelt i fila, og får sitt eget avtrykk av filene bak, så testen blir rød når siden endres, til bildet er tatt på nytt.
- c) Testene, med «Ville feilet hvis»: knappen står rett under beskrivelsen og er lukket; begge bildene ligger i `docs/appen/`, med alt-tekst og teksten under; bildene i README-en er de tre i «Kom i gang», disse to og CI-merket, og ingen flere; avtrykket for hvert bilde; mappa har bare bilde- og videofiler. Mutanter én om gangen med `-x` og kopi før og sha256 mot HEAD etter: en endret mal bak aksjesiden uten nytt bilde, knappen åpen som standard, og et bilde av appen utenfor `docs/appen/`.

## Planen, én commit per punkt

1. a) `git mv docs/bilder/readme/oversikten-demo.png docs/appen/`. `SKJERMBILDET` i `tests/test_docker.py` peker dit, så feilmeldingen følger med. Lenken i README-en og «Mappestruktur» får et eget punkt for `docs/appen/`, og testene for antallet punkter og lenker følger med. Bildet blir stående under «Til faglærer» til b.
2. b) Knappen `<details>` med `<summary>Bilder av appen (demoen)</summary>` mellom beskrivelsen og «Innhold», uten `open`, med de to bildene og en tekst under hvert. Bildet av aksjesiden heter `docs/appen/aksjesiden-kvst-demo.png` og tas med fremgangsmåten fra 3.3b: demobasen i en midlertidig mappe, `OSE_DEMO=1`, waitress på en ledig port og Edge uten vindu, 1280 px bred, med høyden målt til bunnen av KI-teksten. Avtrykket regnes som for oversikten, av filene bak aksjesiden: malen, delmalene, skriftene, demodataene med KI-tekstene, og modulene som lager tallene, grafen og tekstene, med hele `src/app.py`, fordi ruta bygger siden der.
3. c) Testene.

## Avgjort i spesifikasjonen

- **Navnet på mappa** er `docs/appen/`, med bilder og video side om side, uten undermapper, så README-en lenker rett til fila.
- **Filtypene i mappa** er bilder (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`) og video (`.mp4`, `.webm`, `.mov`). Thumbs.db og .DS_Store hoppes over, som i `docs/bilder/`.
- **Bildet av aksjesiden** er tatt med KI på, som når siden åpnes første gang (FR-601), og med 6 mnd i grafen, siden slik den åpnes.

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke. Den ekte `.env` leses ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Bildene tas fra en demobase i en midlertidig mappe.
- Bildene viser bare demoen (regel 16).
- PR-en stopper før flettingen.
