---
title: 'Story 2.3, tillegg: hentingen tilbake til kl. 22:00 på børsdager'
type: 'feature'
created: '2026-10-20'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'ddf828f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-3-hentingen-fra-kl-21.md'
---

Dette er et nytt tillegg til story 2.3 (børsdagskontrollen før kvoten brukes). Det snur tillegget i `spec-2-3-hentingen-fra-kl-21.md`, som står urørt.

## Intent

**Problem:** fra 19.10 nekter tidskontrollen i hentingen en henting på en børsdag bare før kl. 21:00 i Oslo (`TIDSGRENSE = time(21, 0)`, PR #60, beslutningen 16.10 kl. 21:09). Målingen 19.10 (`malinger.md` §37) hentet DNO, MOWI, GJF og AKRBP på nytt kl. 22:00. DNO var ulik i `volume`, så raden fra kl. 21 var ikke endelig. En vurdering som er skrevet, kan ikke skrives om (AD-7). Gruppen svarte 19.10 kl. 22:19 at hentingen på børsdager går tilbake til kl. 22:00 fra tirsdag 20.10, og at byggestoppen blir kl. 21:40 («Avgjort 2026-10-19 kl. 22:19» under story 2.3 i `epics.md`).

## Planen, én commit per punkt

**a) Koden.**
- `TIDSGRENSE = time(22, 0)` i `src/fetch_prices.py`, med kommentaren om svaret 19.10 kl. 22:19 og §37.
- Flagget `--uten-tidskontroll` står, med samme virkning.
- Testene viser at kl. 22:00 er tidsnok og kl. 21:59 for tidlig, også i vintertid.

**b) Tekstene for brukeren (regel 19):** klokkeslettet for hentingen blir «kl. 22» i README-en og `docs/hjelp.md`, og testene som krever teksten, følger med.

**c) Demoen** er lik den ekte (beslutningen 16.10 kl. 11:46). Klokkeslettene i `src/demo.py` flyttes tilbake: hentingen til 22:15 og vurderingene til 22:30. Fingeravtrykkene og bildene følger testene.

**d) Dokumentene:** der PRD-en, `epics.md` og `docs/kvalitetssikring.md` sier at hentingen går fra kl. 21:00, kommer en datert linje om kl. 22:00 fra 20.10. Ingen linje fjernes.

## Det som ikke endres

- Midnatt i Oslo er fortsatt slutten, og et nytt forsøk starter ingen kall fra kl. 23:50 (`KL_23_50`).
- Tidskontrollen gjelder bare på en børsdag.
- Rekkefølgen før første kall, kvotesjekken og kodene 0, 1, 2 og 3 står som før.
- Dagsfilene, Utført-linjene, målingene i `malinger.md`, refleksjonsloggen og de eldre spesifikasjonene endres ikke. De beskriver det som gjaldt da.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke mot EODHD, og `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Demobasene lages bare i midlertidige mapper.
- Flettes i instruksjonen kl. 15:11 når ingen test feiler, ingen mutant overlever, CI er grønn på head-en, hvert funn med dom medium eller høyere er rettet, og klokka ikke er over 21:20.

**Mutantene**, én om gangen med `-x`:
- grensen tilbake på kl. 21:00
- grensen på kl. 22:01

**Testtallet før:** 2761 bestått og 17 hoppet over (head-en til PR #78, `dca69d0`, samme kode og tester som main på `ddf828f`).

## Avgjort underveis

## Mutantene

## Gjennomgangen
