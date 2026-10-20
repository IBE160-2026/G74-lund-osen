---
title: 'Story 2.3, tillegg: hentingen tilbake til kl. 22:00 på børsdager'
type: 'feature'
created: '2026-10-20'
status: 'in-review'
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

- **`docs/hjelp.md` får kl. 22 i en Rettet-linje rett under svaret «Når kan jeg hente?»,** ikke i selve svaret. Steg 5 i instruksjonen sier at ingen linje fjernes fra andre dokumenter enn README-en, og svaret er én linje. Rettet-linja sier også at hentingen stopper med 0 kall mellom kl. 21 og 22. PR #60 endret linja direkte; det gjorde ikke denne. Testen krever Rettet-linja med timen fra `TIDSGRENSE`, og at ingen annen linje i hjelpen sier den gamle timen.
- **Testene for grensen fikk nye navn** (`test_grensen_er_kl_22`, `test_kl_22_presis_henter`, `test_boersdag_kl_21_59_59_gir_0_kall_og_nevner_flagget` og `test_kl_21_59_i_oslo_i_november_nekter`). `docs/kvalitetssikring.md` og `docs/vurderingsmatrise.md` nevner de gamle, og ingen linje fjernes der, så de gamle navnene står i `OMDOEPT` i `tests/test_kvalitetssikring.py`, og en datert linje i hvert dokument gir de nye. Vedlegget nevner testene uten fil, så der godtas det gamle navnet alene. En ny test sjekker at hvert nytt navn i `OMDOEPT` finnes.
- **Avtrykkene bak de to bildene endres**, fordi stripa sier «kl. 22.15» i stedet for «kl. 21.15». Bildene ble tatt på nytt med samme høyder, 1630 og 1872 px. Fingeravtrykkene av demobasen endres ikke.
- **PRD-en:** linja under punkt 23 i kravteksten kom i `ddf828f` på main, og linja under tabellen over åpne punkter, der beslutningen 16.10 kl. 21:09 står i raden for punkt 23, kom i rettingene (VG1).
- **`spec-2-3-hentingen-fra-kl-22` har egen merkelapp,** «2.3, kl. 22», i `EGEN_MERKELAPP`, som «2.3, kl. 21».

## Mutantene

Én om gangen med `-x` og `tests/test_fetch_prices.py`, i en fersk klon med `core.autocrlf=false`, med kopi av `src/fetch_prices.py` før og sha256 mot HEAD etter hver, og `git status` tom etterpå. Begge ble fanget på `d5c5cdd`, og igjen på `8781d02` etter rettingene, av hele fila og av testen sin alene:

- G1, grensen tilbake på kl. 21:00: først `test_grensen_er_kl_22` i fila, og alene `test_boersdag_kl_21_59_59_gir_0_kall_og_nevner_flagget`.
- G2, grensen på kl. 22:01: først `TestSkriverIkkeOver::test_tom_katalog_gir_ny_fil_som_kan_leses_og_er_uten_noekkel` i fila, som henter kl. 22:00, og alene `test_kl_22_presis_henter`.

## Gjennomgangen

Gjennomgang 20.10 på diffen `ddf828f..d5c5cdd`. Linsene var Blind Hunter (BH, 11 funn, bare diffen), Edge Case Hunter (ECH, 9 funn, prøver i en fersk klon som ble slettet etterpå, med 2763 bestått og 17 hoppet over der) og Verification Gap (VG, 8 hull, mot instruksjonen, spesifikasjonen, story 2.3 og PRD-en). Edge Case Hunter fant ingen feil ved 22:00:00, 21:59:59.999999 eller rundt 25.10, og ingen annen test som stoppes av grensen enn de fem som skal. Rettingene står i `8781d02`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| VG1 | Raden for punkt 23 i tabellen over åpne punkter i PRD-en, der beslutningen 16.10 kl. 21:09 står, hadde ingen datert linje | medium | rettet: en datert linje under tabellen |
| VG2, ECH1, BH5 | `docs/hjelp.md` åpner svaret med «Hent etter kl. 21», og timen 21–22 var ikke nevnt | medium | rettet: Rettet-linja rett under svaret sier kl. 22 og at timen 21–22 gir 0 kall. Linja over står (steg 5), se «Avgjort underveis» |
| BH4, VG3 | Hjelpen ble bare prøvd for én fast setning | low | rettet: setningen følger `TIDSGRENSE`, og ingen annen linje i hjelpen sier den gamle timen |
| BH1, ECH3, VG5 | Vedlegget i kvalitetssikringen nevner de gamle testnavnene | low | rettet: en datert linje nederst i vedlegget gir de nye |
| BH2, ECH2, VG5 | Vurderingsmatrisen sier grensen kl. 21:00 og det gamle testnavnet | low | rettet: en datert linje |
| ECH6 | Vinduet for nye forsøk var bare holdt til `TIDSGRENSE < KL_23_50` | low | rettet: minst 60 minutter i `test_grensen_er_foer_stoppen_for_nye_forsoek` |
| BH6 | Kommentaren ved `TIDSGRENSE` sa at testene ser docstringene | low | rettet: den sier at ingen test leser dem |
| BH11, ECH5, VG8 | Spesifikasjonen var ikke fylt ut, og radene «2.3, kl. 22» mangler i kvalitetssikringen | low | rettet: denne delen. Radene kommer etter flettingen (steg 4), før `test_hver_ferdige_spesifikasjon_har_en_rad` krever dem |
| BH10 | Kommentaren nevnte ikke at vurderingen for DNO ble den samme | nit | rettet |
| BH8 | Testen for 21:30 sjekket mindre enn de for 21:59 | nit | rettet |
| BH7 | Testen for 22:30 hadde ingen grunn | nit | rettet |
| BH9 | Docstringen i `test_demo.py` sa at ingen fingeravtrykk endres | nit | rettet: den skiller demobasen fra bildene |
| BH3, ECH4 | Unntaket i vedlegget gjelder navnet, ikke klassen | low | avvist: vedlegget nevner testene uten fil og klasse, og hvert nye navn prøves for seg |
| VG4 | Linjene fra 17.10 under story 2.3 sier kl. 21:00 | low | avvist: «Avgjort 2026-10-19 kl. 22:19» og linja under beslutningen 16.10 kl. 21:09 står i samme story |
| VG6 | Ingen test vokter de daterte linjene | low | avvist: dokumentlinjene prøves i gjennomgangen, som før |
| VG7 | Commitene for a og b er røde alene | nit | avvist: én commit per punkt, som PR #60, og head-en er grønn |
| ECH7 | En hovedhenting som starter etter kl. 23:50, kjører | nit | avvist: uendret av denne PR-en |
| ECH8 | Stripa i 8.19 nevner `KL_22` | nit | avvist: ikke bygget, og linja under sier `TIDSGRENSE` |
| ECH9 | Demoen mot grensen | – | ingen endring: 22:15 og 22:30 er etter grensen og prøvd |

Ingen funn med dom medium eller høyere står urettet.
