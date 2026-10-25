---
title: 'Story 10.2, 10.2f: grunnen i prompten'
type: 'feature'
created: '2026-10-25'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '448bc60'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-2e-prompten-versjon-3.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

## Intent

**Problem:** Prompten i versjon 3 sier: «Ikke si hvor lenge signalet har vart, om det er nytt, eller om det er første gang. Siden sier det under teksten.» Etter gruppens svar 25.10 kl. 12:12 a) sier ikke siden lenger «for første gang», så grunnen stemmer ikke (punktet fra gjennomgangen 25.10 kl. 13 under «Åpent» i spesifikasjonen 10.2e).

**Beslutningen** (under story 10.2 i `epics.md`, *Avgjort 2026-10-25 kl. 18:34 og 18:35*):
- a) Grunnen i prompten endres i kveld. Linja blir: «Ikke si hvor lenge signalet har vart, om det er nytt, eller om det er første gang. Siden sier under teksten hvor lenge signalet har vart.» Regelen for modellen står.
- b) `PROMPTVERSJON` står som «3», fordi ingen tekst i `ose.db` er laget med versjon 3 ennå. Avtrykket settes på nytt, og demotekstene og prøvekjøringen lages på nytt, så alle tekster med versjon 3 er laget med samme prompt. Det er et unntak fra regelen om ny versjon i docstringen i `ki_prompt.py`, og docstringen sier det.

## Approach

**a) Prompten** (`src/ki_prompt.py`): linja med ordlyden fra svaret a), avtrykket for versjon 3 i `AVTRYKK` i `tests/test_ki_modell.py` satt på nytt, og docstringen med svaret b).

**b) Demoen:** KI-tekstene i demoen lages på nytt (`uv run python src/demo_ki.py`), og bildet av aksjesiden i README-en tas på nytt med avtrykkene. Bildet viser en demoaksje der teksten besto (svaret 24.10 kl. 23:23 b).

*Utfallet:* KI-tekstene i demoen ble laget på nytt 19:15:59–19:16:21: 13 av 13 besto, 0 ble stoppet, og modellen feilet for 0. Alle har `promptversjon` 3. BRFE, SLVP, TRHF og LKSV fikk en annen tekst enn før, og de ni andre er like. Hver er lest mot grunnlaget: alle beskriver hver sjekk slik fortegnet er, og ingen nevner dagene, hovedindeksen, bransjen eller antallet aksjer. Bildet viser fortsatt BRFE, der teksten besto, 1280 × 1934. Bunnen av grafen ble målt i Edge uten vindu og står fortsatt ved 1934. `AVTRYKK_BAK_AKSJESIDEN` er satt på nytt. README-teksten under bildet siterer ikke KI-teksten og er ikke endret.

**c) Prøvekjøringen** (§47 i `malinger.md`), som i §46, mot `data/db/ki-proeve-v3g.db` for børsdagen 23.10, med hver tekst lest mot grunnlaget. Tabellen sammenligner §34 og §43–§47.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` røres ikke (regel 22). Demobaser lages bare i midlertidige mapper.
- Kopien ble laget med skallet på main kl. 19:13:44, før grenen, med samme sha256 som `ose.db` (`e3184c07…f4a4`). Ingen KI-rad i kopien har `promptversjon` 3: alle 75 har 2.
- Tekstene fra prøvekjøringen føres ikke i en sporet fil (regel 16).
- Stopp før flettingen hvis færre enn 15 tekster i §47 besto, eller en tekst i §47 sier feil om en sjekk eller nevner dagene.

## Mutanten

Én med `-x`, med kopi før og sha256 mot HEAD etter: den gamle grunnen, «Siden sier det under teksten.», tilbake i prompten.

## Åpent
