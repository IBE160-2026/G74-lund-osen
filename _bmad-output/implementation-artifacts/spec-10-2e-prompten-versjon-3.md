---
title: 'Story 10.2, 10.2e: prompten versjon 3'
type: 'feature'
created: '2026-10-24'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '153aba8'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

## Intent

**Problem:** KI-teksten i versjon 2 får bare fortegnet for de tre sjekkene, styrken og retningen. Den kan ikke si hvor lenge signalet har vært slik, eller hvordan dagen var på børsen.

**Beslutningene** (under story 10.1 og 10.2 i `epics.md`):
- *2026-10-21 kl. 22:57 og 23:51:* den nye promptversjonen får hvor lenge signalet har vært slik, retningen på hovedindeksen og børsometeret, og bare våre egne resultater. Ingen kurser, volumer, prosenter eller forholdstall, heller ikke tallene som står på siden. Teksten kan vise til tallene på siden uten å gjenta dem, og hvert tall i teksten kontrolleres mot grunnlaget.
- *2026-10-24 kl. 15:50:* versjon 3 bygges og flettes i kveld, etter uka med logget drift med versjon 2 (19.–23.10).
- *2026-10-24 kl. 16:15:* a) hvor lenge signalet har vært slik, er børsdager på rad med samme retning og styrke, til og med dagen; b) fra børsometeret: hvor mange aksjer i lista som steg og falt fra børsdagen før, og om bransjen til aksjen steg eller falt i snitt. Begge er fortegn og antall.
- *2026-10-16 kl. 23:51 (2):* en ny promptversjon flettes når den består minst like mange tekster som versjonen før, i en prøvekjøring på samme dags data, og ingen tekst gjetter på en årsak utenfor regelen.

## Approach

**a) Grunnlaget** (`src/ki_grunnlag.py`). `ki_grunnlag` får `dagen=`, et `Dagsbilde`, og grunnlaget får disse feltene i tillegg:
- `dager`: et heltall fra 1. Det er børsdager på rad bakover fra dagen, etter børskalenderen, der den lagrede vurderingen har samme retning og samme styrke. Rekka stopper ved en vurdering med annen retning eller styrke, eller ved en grunn. Den stopper også ved en børsdag uten rad, også før første lagrede vurdering, og der kalenderen slutter. Da får grunnlaget `dager_merke: "minst"`, fordi det ikke er kjent hvordan signalet var før.
- `hovedindeksen`: `steg`, `falt` eller `uendret`, etter fortegnet på endringen slik den vises (`avrundet(..., "endring")`). Endringen er den samme som `indeksendring` i `hovedindeks.py` gir den stiplede linja på forsiden. Feltet mangler når indeksen ikke har en rad for dagen, eller ingen rad for børsdagen før. Indeksen velges som i appen: OSEBX når basen har den, ellers den basen har (DEMIX i demoen). Valget flyttes fra `app.py` til `valgt_indeks` i `hovedindeks.py`, så begge bruker det samme.
- `aksjer_steg` og `aksjer_falt`: aksjene i lista med kurs for dagen og en rad før, som har endring over eller under null slik den vises. Endringen er den samme som i børsometeret (`endring_i_prosent` på de to siste radene). Uendret og uten data telles ikke.
- `bransjen`: `steg`, `falt` eller `uendret` for snittet av endringen til aksjene i lista i samme bransje, som i børsometeret. Fortegnet tas av snittet slik det vises. Feltet mangler når ingen aksje i bransjen har en endring.

Fortsatt ingen kurser, volumer, prosenter eller forholdstall. Grunnlaget har bare heltall og tekst fra lukkede lister, og `_kontroller` sjekker de nye feltene. `ki_tekst.lag_ki_tekster` leser seriene, indeksen og vurderingene fra basen og gir `dagen` for hver aksje. `dagen=None` gir grunnlaget fra versjon 2, slik testene fra 10.1 bruker det.

**b) Prompten** (`src/ki_prompt.py`): `PROMPTVERSJON = "3"`. Reglene forklarer de nye feltene med ord. Teksten kan vise til tallene på siden uten å gjenta dem. Avtrykket for versjon 3 står i `AVTRYKK` i testen, og avtrykkene for versjon 1 og 2 står.

**c) Kontrollen** (`src/ki_kontroll.py`, FR-603):
- Et tall er lov bare når det står i grunnlaget som et antall (`styrke`, `dager`, `aksjer_steg`, `aksjer_falt`), eller er et av regelens faste tall. Fortegnene er ikke antall, som før.
- Sier teksten at hovedindeksen eller bransjen steg, falt eller var uendret, skal det stemme med grunnlaget. Mangler feltet, stoppes et slikt utsagn.

**d) Demoen og prøvekjøringen:**
- KI-tekstene i demoen lages på nytt med versjon 3 (`uv run python src/demo_ki.py`). Bildene og avtrykkene følger med.
- Prøvekjøringen (§43 i `malinger.md`) går som i §34. Bare KI-steget (`lag_ki_tekster`) kjøres mot `data/db/ki-proeve-v3.db` for børsdagen 23.10, med den ekte klokka, fra et skript utenfor repoet.
- Kopien har radene med versjon 2 fra kveldshentingen 23.10. Utfallet av dem føres som sammenligning på samme dags data. Så slettes de i kopien, og bare i kopien, med utløseren `ki_logg_slettes_ikke` tatt bort og satt inn igjen, før KI-steget kjøres.
- sha256 for `data/db/ose.db` er den samme før og etter.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` røres ikke (regel 22).
- Kopien ble laget med skallet på main kl. 20:11, før grenen. sha256 var lik `ose.db`: `e3184c07…f4a4`.
- Tekstene fra prøvekjøringen føres ikke i en sporet fil (regel 16).
- Stopp før flettingen hvis kontrollen stopper tre eller flere av tekstene i §43, eller hvis versjon 3 består færre enn versjon 2 på 23.10 (beslutningen 16.10 kl. 23:51, 2).

## Mutantene

Én om gangen med `-x`, med kopi før og sha256 mot HEAD etter:
- M1: dagene telt bare på retningen.
- M2: kontrollen slipper et tall utenfor grunnlaget.

## Åpent

- `bransjen` for en bransje med bare aksjen selv sier det samme som aksjens egen endring. Børsometeret merker den «1 aksje». Grunnlaget har ikke det merket.
