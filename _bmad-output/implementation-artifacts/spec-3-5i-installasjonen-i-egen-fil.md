---
title: 'Story 3.5 (3.5i): installasjonen i docs/installasjon.md, og «Kom i gang» med de fem stegene'
type: 'docs'
created: '2026-11-08'
status: 'draft'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '958c27a3'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-5g-kortere-kom-i-gang.md'
  - '{project-root}/README.md'
  - '{project-root}/docs/hjelp.md'
---

## Intent

README-en ryddes etter gruppens svar 07.11 kl. 23:26 under story 3.3 og «Prioritering» i `epics.md`: README-en beholder hva appen er, de fem stegene for dobbeltklikket og én linje om den ekte versjonen. Docker, uv, Linux, «Står du fast?» og «Mer for den som vil» flyttes uendret til `docs/installasjon.md`, og testene følger med. Rådet anbefalte det. Instruksjonen er kl. 10:36 i `docs/ai-prompts/2026-11-08.md`.

## Slik er det i dag (slått opp 08.11 på `958c27a3`)

- «Kom i gang» er linje 58–471 i README-en: anbefalingen av demoen, «Enklest: dobbeltklikk (anbefalt)» med de fem stegene, linja «Første gang», linja «Ekte kurser», linja «Linux», så pilene «Velg vei», «Du trenger», «Med Docker Desktop», «Demoen», «Den ekte versjonen», advarselen mot `docker compose down -v`, «Uten Docker, med uv», «Slik virker dobbeltklikket», «Står du fast?», og «Mer for den som vil» med fem piler: bytte versjon, variablene i `.env`, den lokale modellen, egen nøkkel og hentingen hver kveld.
- Ankeret `den-ekte-versjonen` står på pila med Docker-stegene 5–9. Lenken i demoen er `EKTE_VERSJONEN_URL` i `src/app.py`, `…/G74-lund-osen#den-ekte-versjonen`.
- Det som viser til delene som flyttes: «Til faglærer» (`#med-docker-desktop`, `#demoen`, `#den-ekte-versjonen`), «Status» («README-en med bilder i «Kom i gang»»), «Mappestruktur» (de tre skjermbildene «i «Kom i gang»»), `docs/hjelp.md` (`../README.md#slik-virker-dobbeltklikket` og `../README.md#hentingen-hver-kveld`), tre meldinger i `src/ki_tekst.py` («se «Den lokale modellen» i README-en» og «se «Egen nøkkel til Gemini, Anthropic eller OpenAI» i README-en») og to kommentarer i `.env.example` som brukeren leser.
- Testene som leser delene: mest `tests/test_docker.py` (135 treff på README), `tests/test_dobbeltklikk.py` (16) og noen få andre. `tests/test_readme.py` sjekker at hver lenke i README-en går til en fil som finnes, men ikke ankeret.
- Avtrykkene bak bildene i `docs/appen/` (`tests/test_docker.py`) har `src/app.py`, men ikke `src/ki_tekst.py` eller `.env.example`. Lenken i demoen er den samme etter ryddingen, så `src/app.py` endres ikke, bildene tas ikke på nytt, og ECH7 og BH16 venter fortsatt (`issues.md`).

## Kontrollpunktene

- a) «Kom i gang» i README-en har bare de fem stegene, linja om første gang og linja om den ekte versjonen, med lenke til `docs/installasjon.md`. **Ville feilet hvis** en pil, Docker, uv, Linux, «Står du fast?» eller «Mer for den som vil» sto igjen i README-en.
- b) `docs/installasjon.md` har resten av «Kom i gang» i samme rekkefølge og ordrett, bare med stiene rettet for den nye mappa. **Ville feilet hvis** en linje var endret utover stiene, eller manglet (en test sammenligner med README-en på `958c27a3`, linje for linje, etter at stiene er rettet tilbake).
- c) Linja om den ekte versjonen har ankeret `den-ekte-versjonen`, så `EKTE_VERSJONEN_URL` går dit. **Ville feilet hvis** ankeret sto på en annen linje eller manglet i README-en.
- d) Hver lenke i README-en og `docs/installasjon.md` går til en fil som finnes og til et anker som finnes i den fila. **Ville feilet hvis** én lenke pekte på et anker som er flyttet.
- e) Lenkene i README-en og `docs/hjelp.md`, meldingene i `src/ki_tekst.py` og kommentarene i `.env.example` viser til `docs/installasjon.md` der delene nå står. **Ville feilet hvis** en melding fortsatt sa «i README-en» om en del som er flyttet.
- f) Testene som leste delene i README-en, leser dem i `docs/installasjon.md`, med de samme kravene. **Ville feilet hvis** en test bare ble slettet, eller sjekket mindre enn før.
- g) «Dokumentene» og «Mappestruktur» i README-en lenker til `docs/installasjon.md` (regel 19).

## Planen

1. `docs/installasjon.md` med frontmatter som `docs/hjelp.md`, og resten av «Kom i gang» flyttet ordrett. Stiene rettes: `docs/bilder/readme/` blir `bilder/readme/`, `docs/hjelp.md` blir `hjelp.md`, `docs/kilder-og-rettigheter.md` blir `kilder-og-rettigheter.md`, `start/` blir `../start/`, og ankrene som står igjen i README-en (`#tester`, `#demoen-og-den-ekte-versjonen`), blir `../README.md#…`.
2. README-en: «Kom i gang» som i a), «Til faglærer», «Status», «Dokumentene» og «Mappestruktur» rettet.
3. `docs/hjelp.md`, `src/ki_tekst.py` og `.env.example` rettet.
4. Testene: en felles leser for `docs/installasjon.md`, de som leser delene, flyttet dit, testen for lenker og ankre (d), og testen for at flyttingen er ordrett (b).

## Spørsmål til gruppen før det bygges

Det er tre ting sensor vil se som svaret kl. 23:26 og instruksjonen ikke avgjør:

1. **Overskriften «Enklest: dobbeltklikk (anbefalt)» og setningen «Vi anbefaler demoen for faglærer og sensor …».** Etter ordlyden flyttes begge, fordi bare stegene og de to linjene står igjen. Da står overskriften i `docs/installasjon.md` over pilene, uten stegene den gjaldt, og ankeret `enklest-dobbeltklikk-uten-docker`, som «Til faglærer» og hjelpen lenker til, havner der. **Forslag:** overskriften og ankeret står over de fem stegene i README-en, og setningen om demoen flyttes først i `docs/installasjon.md`.
2. **«øverst» i en setning som flyttes.** «Velg versjon. Klikk på pila for den versjonen du vil prøve. [Tabellen «Demoen og den ekte versjonen»](#demoen-og-den-ekte-versjonen) øverst viser forskjellen.» i pila «Med Docker Desktop» viser til tabellen øverst i README-en, men står nå i en annen fil. Uendret leses «øverst» som toppen av `docs/installasjon.md`. **Forslag:** «øverst i README-en», og ellers ingen ordendringer.
3. **Er `docs/installasjon.md` et levende dokument, som README-en og `docs/hjelp.md`?** Regel 19 sier at de andre dokumentene får en Rettet-linje. Teksten er README-tekst og leses av brukere. **Forslag:** ja, rettes der den står, med historikken i git, og en linje i regel 19 i `CLAUDE.md` i samme PR.

Linja om den ekte versjonen blir, med forslaget i 1:

> <a name="den-ekte-versjonen"></a>**Ekte kurser:** dobbeltklikk «Start den ekte versjonen» i stedet for «Start demoen». Den spør etter en gratis nøkkel fra EODHD første gang, og starter bare i en kopi fra ZIP-fila, ikke i en klon. Docker, uv, Linux, hjelp når du står fast og mer for den som vil: [Installasjonen](docs/installasjon.md).

Lenken i demoen lander da på denne linja, ikke på Docker-stegene 5–9, som før ryddingen. Dobbeltklikket spør selv etter nøkkelen, så stegene for nøkkelen trengs ikke der.

## Gjennomgangen

Fylles ut etter at det er bygget.
