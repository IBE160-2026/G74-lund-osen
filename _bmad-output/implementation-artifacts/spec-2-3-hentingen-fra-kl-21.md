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
- Grensen i tidskontrollen er `TIDSGRENSE = time(21, 0)` i `src/fetch_prices.py`. Navnet har ikke klokkeslettet i seg, så neste endring er én linje. *Rettet 2026-10-17 (gjennomgangen, ECH5):* én linje i koden. Tekstene for brukeren, docstringene og klokkeslettene i demoen står for seg, og testene sier fra når de ikke følger med.
- Flagget heter `--uten-tidskontroll` (`uten_tidskontroll` i `kjoer`), med samme virkning som før. Det gamle navnet godtas ikke lenger: argparse avviser det, og `allow_abbrev=False` står.
- Utskriftene og docstringene leser klokkeslettet fra konstanten, og CI-arbeidsflyten bruker det nye flagget.
- Testene viser at kl. 21:00 er tidsnok, og at kl. 20:59 er for tidlig, også i vintertid.

**b) Tekstene for brukeren (regel 19):** «kl. 22» for hentingen blir «kl. 21» i README-en og `docs/hjelp.md`, og testene som krever teksten, følger med. Testen som holder flagget ute av README-en og hjelpen, gjelder det nye navnet, og det gamle.

**c) Demoen** skal være lik den ekte (beslutningen 16.10 kl. 11:46). Klokkeslettene i `src/demo.py` flyttes: hentingen fra 22:15 til 21:15, og vurderingene fra 22:30 til 21:30. Kursene og vurderingene ellers er uendret. Et fingeravtrykk som endres, forklares i testen. *Lagt til 2026-10-17 (gjennomgangen, BH8):* ingen fingeravtrykk endres, fordi `kurs` og `vurdering` ikke har klokkeslett. `FINGERAVTRYKK_KURS` og `FINGERAVTRYKK_VURDERING_FOER_SISTE_DAG` står, og `TestKlokkeslettetSomDenEkte` i `test_demo.py` sier det.

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

## Mutantene

Én om gangen med `-x` og bare `tests/test_fetch_prices.py`, i den ferske klonen med `core.autocrlf=false`, med kopi før og sha256 mot HEAD etter hver. Alle ble fanget på `e0ab79e`, og igjen på `f93f249` etter rettingene:
- T1, grensen tilbake på 22:00: `test_grensen_er_kl_21`. `test_kl_21_30_henter` prøver det samme gjennom hentingen.
- T2, `<=` i stedet for `<` ved grensen: `test_kl_21_presis_henter`.
- T3, det gamle flaggnavnet godtatt: `test_det_gamle_flaggnavnet_godtas_ikke`.

## Gjennomgangen

Gjennomgang 17.10 på diffen `main...e0ab79e`, med Blind Hunter (BH, 13 funn), Edge Case Hunter (ECH, 6) og Verification Gap (VG, 0). Verification Gap søkte gjennom hele repoet etter det gamle flagget, `KL_22`, «kl. 22», «22:00» og «22:15», og fant ingen bruk i kode, arbeidsflyt, compose, Dockerfile, skript, maler eller hjelpetekster som er glemt. Rettingene står i `f93f249`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH3 | Testen for det gamle flagget godtok enhver `TypeError` og brukte stier i arbeidskopien | low | patch: `match="hent_foer_kl_22"`, signaturen sjekkes, og stiene er midlertidige |
| BH4 | Forbudet mot «kl. 22» i README-en og hjelpen traff alle klokkeslett | low | patch: bare «etter kl. 22» og «før kl. 22» som tidspunkt for hentingen |
| BH5, ECH3 | README-testen så bare på timen | low | patch: grensen må være en hel time, og timen står med ordgrense |
| BH11 | Ingenting holder grensen før stoppen for nye forsøk kl. 23:50 | low | patch: `test_grensen_er_foer_stoppen_for_nye_forsoek` |
| BH12 | Testen for 20:59 så ikke hvorfor det ble 0 kall | low | patch: linja fra tidskontrollen kreves |
| ECH4, BH9 | Bare vurderingene i demoen ble holdt mot grensen | low | patch: hentingen kl. 21:15 også |
| ECH5, ECH6, BH13 | «Neste endring er én linje» og «docstringene leser fra konstanten» stemmer ikke helt | low | patch: kommentaren ved `TIDSGRENSE` og Rettet-linja over. Docstringene sier «kl. 21:00» ved siden av `TIDSGRENSE` |
| BH8 | Spesifikasjonen ventet et fingeravtrykk som endres | low | patch: linja under punkt c |
| ECH2, BH7 | Betingelsen er prøvd for én aksje, EQNR.OL, én dag, men gjelder alle 15 og indeksen. En vurdering fra en foreløpig rad kan ikke rettes (AD-7) | low for PR-en | avvist her: gruppen satte betingelsen slik i beslutningen kl. 21:09, og den holdt (§31). Om flere målinger trengs, er gruppens spørsmål. Det tas opp i svaret til gruppen |
| ECH1 | Indeksen er kanskje ikke publisert kl. 21, og får ingen ny sjanse | low | avvist: kode 3 sier det samme kveld, og neste henting bytter ut hele serien (AD-5), så dagen kommer med da. Indeksen er ikke en vurdering (AD-7) |
| BH6 | Dokumentene sier «fra 19.10», og koden har ingen dato | low | avvist: PR-en flettes lørdag 17.10, og ingen børsdag ligger mellom flettingen og mandag 19.10 |
| BH1, BH2 | Andre som bruker `KL_22` eller det gamle flagget | low | avvist: Verification Gap fant ingen. Stripa «Neste: …» i 8.19 er ikke bygget, og linja under den i `epics.md` sier at konstanten heter `TIDSGRENSE` |
| BH10 | Tabellen i README-prøven sier fortsatt «kl. 22» i steg 4 | low | avvist: ingen linje fjernes (instruksjonen kl. 21:11), og den daterte linja over tabellen sier at det gjelder steg 4 |
