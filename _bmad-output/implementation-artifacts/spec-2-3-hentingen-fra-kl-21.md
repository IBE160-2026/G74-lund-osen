---
title: 'Story 2.3, tillegg: hentingen fra kl. 21:00 på børsdager'
type: 'feature'
created: '2026-10-17'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'e6ceb34'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-3-boersdagskontroll-foer-kvoten-brukes.md'
---

Dette er et tillegg til story 2.3 (børsdagskontrollen før kvoten brukes), ikke story 2.3b (nye forsøk med kallene som er igjen).

## Intent

**Problem:** tidskontrollen i hentingen nekter en henting på en børsdag før kl. 22:00 i Oslo, med flagget `--hent-foer-kl-22` som unntak. Gruppen avgjorde 16.10 kl. 21:09 (under story 2.3 i `epics.md`, og under punkt 23 i PRD-en) at hentingen på børsdager flyttes til kl. 21:00 fra mandag 19.10, på betingelse av at radene fra prøvene kl. 20:30 og 21:00 er like raden i kursfila etter kveldens henting. Betingelsen holdt for EQNR.OL 16.10, i alle sju feltene (tillegget til §31 i `malinger.md`). Gruppen svarte kl. 21:01 17.10 at PR-en bygges lørdag kveld i stedet for søndag. Ingen henting går før mandag.

## Planen, én commit per punkt

**a) Koden.**
- Grensen i tidskontrollen er `TIDSGRENSE = time(21, 0)` i `src/fetch_prices.py`. Navnet har ikke klokkeslettet i seg, så neste endring er én linje.
- Flagget heter `--uten-tidskontroll` (`uten_tidskontroll` i `kjoer`), med samme virkning som før. Det gamle navnet godtas ikke lenger: argparse avviser det, og `allow_abbrev=False` står.
- Utskriftene og docstringene leser klokkeslettet fra konstanten, og CI-arbeidsflyten bruker det nye flagget.
- Testene viser at kl. 21:00 er tidsnok, og at kl. 20:59 er for tidlig, også i vintertid.

**b) Tekstene for brukeren (regel 19):** «kl. 22» for hentingen blir «kl. 21» i README-en og `docs/hjelp.md`, og testene som krever teksten, følger med. Testen som holder flagget ute av README-en og hjelpen, gjelder det nye navnet, og det gamle.

**c) Demoen** skal være lik den ekte (beslutningen 16.10 kl. 11:46). Klokkeslettene i `src/demo.py` flyttes: hentingen fra 22:15 til 21:15, og vurderingene fra 22:30 til 21:30. Kursene og vurderingene ellers er uendret. Et fingeravtrykk som endres, forklares i testen.

**d) Dokumentene:** der PRD-en, `epics.md` og `docs/kvalitetssikring.md` sier at hentingen eller byggestoppen gjelder fra kl. 22:00, kommer en datert linje om at det er kl. 21:00 fra 19.10 (beslutningen kl. 21:09, §31), der det ikke står fra før. Ingen linje fjernes.

## Det som ikke endres

- Midnatt i Oslo er fortsatt slutten. Et nytt forsøk starter ingen kall fra kl. 23:50 (`KL_23_50`, svar 4 i 2.3b).
- Tidskontrollen gjelder bare på en børsdag. En dag børsen er stengt, har den ingen grense.
- Rekkefølgen før første kall, 16 kall, kvotesjekken og kodene 0, 1, 2 og 3 står som før.
- Når jobben i Oppgaveplanlegging skal kjøre, avgjøres i planen for den, som før.
- Dagsfilene, Utført-linjene, målingene i `malinger.md`, refleksjonsloggen og de eldre spesifikasjonene endres ikke. De beskriver det som gjaldt da.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke mot EODHD, og `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Demobasene lages bare i midlertidige mapper.
- Flettes i instruksjonen kl. 21:11 når ingen test feiler, ingen mutant overlever, CI er grønn på head-en, og hvert funn med dom medium eller høyere er rettet.

**Mutantene**, én om gangen med `-x`:
- grensen tilbake på 22:00
- `<=` i stedet for `<` ved grensen
- det gamle flaggnavnet godtatt

**Testtallet før:** 2358 bestått og 17 hoppet over (head-en til PR #59, `bdfd412`, samme kode og tester som main på `e6ceb34`).
