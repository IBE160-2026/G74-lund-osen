---
title: 'Story 10.2, 10.2h: ordstillingen etter «fordi» og rekkefølgen på sjekkene i prompten'
type: 'feature'
created: '2026-10-25'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'd4b6d12'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-2g-ingen-retning.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

## Intent

**Problem:** Fire punkter under «Åpent» i spesifikasjonen 10.2g. Modellen skriver «fordi trenden ga ikke utslag», med feil ordstilling i leddsetningen (BH10), og nevner ikke alltid sjekkene i fast rekkefølge (BH11 i 10.2f, BH13). Kontrollen håndhever ikke regelen for retningen Ingen (BH4, ECH4), og KI-loggen i basen har ikke promptens avtrykk (BH5).

**Beslutningen** (under story 10.2 i `epics.md`, *Avgjort 2026-10-25 kl. 20:54*):
- a) Kontrollen stopper ikke «Signalet er Ingen», fordi teksten er riktig, og regelen ga 0 i §48 (BH4).
- b) KI-loggen i basen får ikke promptens avtrykk (BH5). Fra hentingen mandag 26.10, når basen får tekster med versjon 3, gir enhver endring i prompten en ny versjon.
- c) Prompten får to linjer blant reglene, ordrett: «- Etter «fordi» står «ikke» foran verbet, for eksempel «fordi trenden ikke ga utslag».» og «- Når du nevner flere sjekker, ta dem i rekkefølgen trend, bevegelse og interesse.» (rådets ordlyd).
- d) `PROMPTVERSJON` står som «3» av samme grunn som svaret kl. 18:35 b): ingen tekst i `ose.db` er laget med versjon 3 ennå.

## Approach

**a) Prompten** (`src/ki_prompt.py`): de to linjene fra svaret c) under «Regler for teksten», linja om rekkefølgen etter linja om å bruke navnet på sjekken, og linja om ordstillingen etter linja om «fordi». Avtrykket for versjon 3 i `AVTRYKK` i `tests/test_ki_modell.py` settes på nytt, og docstringen får svarene b) og d).

**b) Demoen:** KI-tekstene i demoen lages på nytt (`uv run python src/demo_ki.py`), med promptens avtrykk i hver rad, og bildet av aksjesiden i README-en tas på nytt med avtrykkene, av en demoaksje der teksten besto.

**c) Prøvekjøringen** (§49 i `malinger.md`), som i §48, mot `data/db/ki-proeve-v3i.db` for børsdagen 23.10, med hver tekst lest mot grunnlaget. Tekstene i §48 og §49 telles for «fordi» med «ikke» etter verbet og for sjekker i en annen rekkefølge. Tabellen sammenligner §34 og §43–§49.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` røres ikke (regel 22). Demobaser lages bare i midlertidige mapper.
- Kontrollen (`ki_kontroll.py`) og KI-loggen (`kilogg.py`) endres ikke (svarene a og b).
- Kopien ble laget med skallet på main kl. 21:36:36, før grenen, med samme sha256 som `ose.db` (`e3184c07…f4a4`). Ingen KI-rad i kopien har `promptversjon` 3: alle 75 har 2.
- Tekstene fra prøvekjøringen føres ikke i en sporet fil (regel 16).
- Stopp før flettingen hvis færre enn 15 tekster i §49 besto, en tekst i §49 sier feil om en sjekk eller nevner dagene, eller sha256 for `ose.db` rett før flettingen ikke er den samme som for kopien.

## Mutanten

Én med `-x`, med kopi før og sha256 mot HEAD etter: linja om rekkefølgen tatt ut av prompten.
