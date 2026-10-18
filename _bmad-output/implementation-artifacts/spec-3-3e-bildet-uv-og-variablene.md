---
title: 'Story 3.3e: bildet av oversikten, uv i «Tester» og variablene i .env'
type: 'docs'
created: '2026-10-18'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'a2965ba'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3b-readme-for-sensor.md'
  - '{project-root}/docs/hjelp.md'
---

## Intent

**Problem:** README-en har ikke lenger bildet av oversikten (tatt ut 16.10 kl. 21:38), «Tester» sier ikke hvordan uv installeres eller hvor lang tid testene tar, og ingenting forklarer variablene i `.env` samlet.

**Grunnlaget:** instruksjonen 18.10 kl. 21:11, gruppens svar 18.10 kl. 00:20 (bildet kommer tilbake etter 3.4b, i en README-PR som stopper før flettingen) og kl. 20:39 («Tester» står der den står, og får installasjonen av uv og tiden). PR-en stopper før flettingen og venter på ja.

## Kontrollpunktene

- a) `docs/bilder/readme/oversikten-demo.png` er tatt etter fremgangsmåten under «Bildet» i spesifikasjonen for 3.3b, på en ledig port, uten å stoppe noen server eller røre åpne Edge-vinduer. Bare demoen, med «Eksempeltall» synlig, uten sti eller brukernavn. Plassen, alt-teksten og teksten under er som i 3.3b. Testene fra 3.3b er tilbake, med avtrykket av alt som endrer det bildet viser, også stilarket, og feilmeldingen sier hvordan bildet tas på nytt. Testene for bildene godtar de tre i «Kom i gang», dette og CI-merket, og ingen flere. «Mappestruktur» nevner det.
- b) «Tester» har installasjonen av uv før `uv sync`: én boks for Windows (PowerShell) og én for Mac (Terminal), fra https://docs.astral.sh/uv/getting-started/installation/, og et nytt vindu i mappa, som i steg 4, hvis uv ikke blir funnet. Etter kommandoene: første `uv sync` laster ned Python og pakkene, og hvor lenge testene tar, i hele minutter. «Uten Docker, med uv» viser til installasjonen i «Tester». `docs/hjelp.md` har spørsmålet om at uv ikke blir funnet, med samme svar.
- c) En knapp «Variablene i .env» under «Mer for den som vil», med en tabell over de tre i `.env.example`: variabelen, hva den gjør, standarden og når den trengs. Én setning om at `OSE_DEMO` og `OSE_I_DOCKER` settes av `compose.yaml` og `Dockerfile` og ikke skal i `.env`. Steg 6 i «Den ekte versjonen» viser dit.
- d) Testene, med «Ville feilet hvis», og mutantene: et bilde til i README-en, en mal endret uten nytt bilde, Mac-boksen tatt ut, og en variabel i `.env.example` som ikke står i tabellen.

## Planen, én commit per punkt

1. a) Bildet, testene for det og «Mappestruktur».
2. b) uv i «Tester», henvisningen fra «Uten Docker, med uv», og spørsmålet i `docs/hjelp.md`.
3. c) Tabellen over variablene og henvisningen fra steg 6.
4. d) Testene for b og c.

## Avgjort i spesifikasjonen

- **Avtrykket bak bildet** dekker malene oversikten bygges av (`index.html`, `_ramme.html` med stilarket i `<style>`, `_brikker.html`, `_bransjer.html` og `_hjelp.html`), skriftene i `src/static/`, demodataene (`src/demo.py`) og modulene som lager det oversikten viser (`markedsoversikt.py`, `oversiktsdata.py`, `hovedindeks.py` og `tallformat.py`). `app.py` er ikke med: den har ruter og logikk for alle sidene, og en endring der ville krevd et nytt bilde hver gang.
- **Tiden for testene** tas fra kjøringene av hele settet på denne maskinen i dag (dagsfila 18.10).

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Bildet tas fra en demobase i en midlertidig mappe. Den ekte `.env` leses ikke.
- Ingen server som kjører, stoppes, og åpne Edge-vinduer røres ikke.
