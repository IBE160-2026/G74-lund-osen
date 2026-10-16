---
title: 'Story 10.2, PR H (10.2c): prompten versjon 2'
type: 'feature'
created: '2026-10-16'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'e25beb6'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

## Intent

**Problem:** I prøvekjøringen 16.10 kl. 22:26–22:27 (`malinger.md` §32) stoppet punkt 4 i kontrollen i FR-603 9 av 15 tekster, 8 på «skyldes» og 1 på «indikerer», også der ordet bare forklarte regelen.

**Beslutningen:** *Avgjort 2026-10-16, gruppens beslutning kl. 22:33* (under story 10.2 i `epics.md`, `f124fa7`): prompten får versjon 2, som ber modellen forklare regelen med «fordi» og ikke bruke «skyldes» eller «indikerer». Kontrollen endres ikke. Det bygges med en ny prøvekjøring på en fersk kopi av basen, og flettes før hentingen mandag 19.10. Er det ikke flettet da, går mandagens henting med `OSE_KI_TJENESTE=av`, så ingen dag får tekster med versjon 1.

*Lagt til 2026-10-16:* gruppen sa kl. 23:27 at det bygges og prøvekjøres i kveld, ikke lørdag (instruksjonen kl. 23:35).

**Approach:**
- `src/ki_prompt.py`: `PROMPTVERSJON = "2"`, og én ny linje under «Regler for teksten»: «- Når du forklarer regelen, bruk «fordi». Ikke bruk «skyldes» eller «indikerer».»
- `src/ki_kontroll.py` er uendret.
- `tests/test_ki_modell.py`: avtrykket for versjon 2 i `AVTRYKK`, og versjon 1 står. `test_regelen_forklares_med_fordi` krever linja under «Regler for teksten» og i prompten.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` røres ikke (regel 22).
- Prøvekjøringen går mot `data/db/ki-proeve-v2.db`, kopiert med skallet på main før grenen ble laget.
- Tekstene fra prøvekjøringen føres ikke i en sporet fil.
- Flettes ikke uten ja fra gruppen.

## Mutantene

Én om gangen med `-x`, med kopi før og sha256 mot HEAD etter:
- H1: linja tatt ut av prompten.
- H2: teksten endret uten ny versjon.
- H3: «skyld(?:es|tes)» tatt ut av kontrollen.
