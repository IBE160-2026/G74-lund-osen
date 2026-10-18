---
title: 'Story 3.3c: tre bilder i «Kom i gang», demoen først og fire rettelser'
type: 'docs'
created: '2026-10-18'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '2e2bcca'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/kvalitetssikring.md'
  - '{project-root}/docs/hjelp.md'
---

## Intent

**Problem:** gruppen gikk selv gjennom «Kom i gang» 16.10 kl. 20:40–21:11 og fant fire ting som ingen test fant: ZIP-fila ble dratt inn i stedet for mappa, mellomrommet etter `cd` manglet, «Cannot find path» hadde ikke noe svar, og det var uklart hvor kommandoen limes inn og hvor kopi-ikonet er. Faglærer prøver demoen, men den står etter den ekte versjonen. Beslutningen 16.10 kl. 21:16, med svarene kl. 21:25 og 21:57, står under story 3.3 i `epics.md`.

**Grunnlaget:** instruksjonen 18.10 kl. 12:23, og svarene kl. 14:48 på to spørsmål om grensene i testene. PR-en stopper før flettingen og venter på ja.

## Planen, én commit per punkt

1. Denne spesifikasjonen, og svarene kl. 14:48 under story 3.3.
2. Bildene: de tre skjermbildene fra gjennomgangen i `docs/bilder/readme/`, i steg 1, 2 og 4 med alt-tekst og en kort tekst under, og «Mappestruktur» nevner dem. Testene for bildene godtar disse tre og CI-merket, og ingen flere.
3. Rekkefølgen: «Demoen» før «Den ekte versjonen (anbefalt)» i README-en, `docs/hjelp.md` og tabellen for Prøve 1, som også får en kolonne for tiden. Testen krever demoen først.
4. a) Steg 4: mappa, ikke ZIP-fila, og hva man gjør når det står `.zip` til slutt.
5. b) «is not recognized as the name of a cmdlet»: mellomrommet etter `cd`.
6. c) «Cannot find path … because it does not exist»: dra mappa på nytt.
7. d) Hvordan en kommando kopieres og limes inn, og hva «Serving on http://0.0.0.0:5000» betyr.

## Avgjort i spesifikasjonen

- **Bildene** er valgt blant de 17 skjermbildene fra 16.10 kl. 20:41–21:03 i `Bilder\Skjermbilder`: `Skjermbilde 2026-10-16 204605.png` («Engine running»), `… 210020.png` (fanen «HTTPS» og «Download ZIP») og `… 205658.png` (`PS C:\prove\G74-lund-osen-main>`). Ingen av de tre viser brukernavn, nøkkel eller kurser, og ingen har tekstfelt i PNG-fila (bare `IHDR`, `gAMA`, `pHYs`, `sRGB`, `IDAT` og `IEND`). De andre bildene fra tidsrommet viser brukernavnet i stien, og brukes ikke. Kopiene ligger i `_privat/bilder/`, som er i `.gitignore`.
- **Spørsmålene under «Står du fast?»:** høyst 10, ikke 8 (svar 1 kl. 14:48). Det endrer grensen fra 11.10 kl. 22:32.
- **Ordgrensen** (svar 2 kl. 14:48): 65 ord per steg står for teksten i steget. Bildet og teksten under det telles for seg, og teksten under har høyst 25 ord. Forklaringen av hvordan en kommando kopieres, står én gang, i et kort avsnitt rett før det første steget med en kommando, og hvert steg med en kommando sier bare at den limes inn i PowerShell-vinduet fra steg 4. Blir et steg fortsatt over 65 ord, flyttes detaljene til `docs/hjelp.md` med en lenke fra steget.
- **Rettelse b** gjelder bare meldingen der `cd` står klistret til stien (`'cdC:\…' is not recognized`). «`docker` er ikke gjenkjent» har sitt eget svar i `docs/hjelp.md`, og står.

## Boundaries

- Bare dokumentene, testene og de tre bildene. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- Ingen linje fjernes fra «Kom i gang» eller `docs/hjelp.md`, bare utvides. Flyttingen endrer verken stegnumrene eller teksten i stegene.
- Bildet av oversikten kommer ikke tilbake her. Det kommer etter 3.4b, i en egen README-PR (gruppens svar 18.10 kl. 00:20).
