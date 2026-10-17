---
title: 'Story 3.4, tillegg: alle de 10 fargekombinasjonene på siste demodag'
type: 'feature'
created: '2026-10-17'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '43de066'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-4-demoversjonen.md'
---

Dette er et tillegg til story 3.4 (Demoversjonen), ikke story 3.4b (KI-tekstene i demoen).

## Intent

**Problem:** gruppen avgjorde 16.10 kl. 21:49 (under story 2.12 i `epics.md`) at demoen skal vise alle 10 fargekombinasjonene av de tre sjekkene på siste dag, fra 3 grønne til 3 grå, og at en test skal kreve dem. De to aksjene som viser en grunn i stedet for en vurdering, `NYLIG_NOTERT` og `UTEN_KURSER` i `src/demo.py`, blir stående. Arbeidet skulle bygges lørdag 17.10 etter PR 1 og PR 2 for hovedindeksen, og PR #57 ble flettet i `bcac2b5`.

**En kombinasjon** er hvor mange av de tre sjekkene som er grønne (+1), røde (-1) og grå (0). Med tre sjekker og tre farger er det 10. Bevegelse og interesse følger begge fortegnet til dagens endring (`signalberegning.py`), så når begge slår ut, har de samme farge. Kombinasjonen 2 grønne og 1 rød krever derfor rød trend og grønn bevegelse og interesse.

**I dag** gir siste demodag 7 av de 10. De tre som mangler, er 3 grønne, 2 grønne og 1 rød, og 1 grønn og 2 grå.

## Planen

**a) Reglene for siste demodag** står i `SISTE_DAG` i `src/demo.py`, i samme form som regelen for Brattfjell Energi: en fast regel for én aksje på `SLUTTDATO`. Hver regel er en endring fra sluttkursen dagen før og et volum som er en faktor av volumnivået i `START`. *Rettet 2026-10-17 (gjennomgangen, BH4 og ECH4):* her sto bare «i samme form som regelen for Brattfjell Energi». Brattfjell Energi tar 6 % av dagens trukne kurs, så endringen fra dagen før er ikke nøyaktig -6 % (-5,53 %). De nye reglene regner fra gårsdagens avrundede sluttkurs, så endringen blir nøyaktig. De gjelder for tre aksjer som i dag gir en kombinasjon som en annen aksje også gir:
- Kvitstein Mineral: +3,5 % med tre ganger volumet gir 3 grønne. I dag gir den 3 grå, som Sølvbank Petroleum og Lastfjord Container.
- Laksevik Sjømat: +3 % med 2,5 ganger volumet gir 2 grønne og 1 rød. I dag gir den 1 rød og 2 grå, som fire andre.
- Lastfjord Container: +2,5 % med vanlig volum gir 1 grønn og 2 grå. I dag gir den 3 grå.

Tallene fra frøet trekkes også den dagen, så de andre dagene og de andre aksjene er som før. Brattfjell Energi og de to aksjene med en grunn står som før. Forslaget kom fra rådet, prøvd i lesekopien, og er sjekket i en demobase i en midlertidig mappe (tabellen under).

**Testen** bygger demobasen i en midlertidig mappe og leser `vurdering` for `SLUTTDATO` fra basen. Den krever alle 10 kombinasjonene, en grunn for `NYLIG_NOTERT` og `UTEN_KURSER`, og at Brattfjell Energi fortsatt skiller seg ut.

**Følgene:** fingeravtrykket av `kurs` i `tests/test_demo.py` endres, fordi tre rader på `SLUTTDATO` endres, og «5 av 15 aksjer skilte seg ut fredag» blir 7. Demoindeksen følger demoaksjene, så siste dag i indeksen endres også.

**b) Tekstene (regel 19):** en datert linje i spesifikasjonen 3.4 om regelen for kursene, og under «Flettet til main» i «Status» i README-en at demoen viser alle 10 kombinasjonene.

## Kombinasjonen på siste dag, før og etter

Lest fra `vurdering` for `SLUTTDATO`, 2026-10-09, i en demobase bygget i en midlertidig mappe, før og etter reglene. Rekkefølgen er (grønne, røde, grå).

| Aksje | Før | Etter |
|---|---|---|
| Brattfjell Energi | (0, 3, 0) | (0, 3, 0) |
| Havdyp Olje | (1, 1, 1) | (1, 1, 1) |
| Nordlysfeltet | (0, 2, 1) | (0, 2, 1) |
| Sølvbank Petroleum | (0, 0, 3) | (0, 0, 3) |
| Fjellheim Sparebank | (0, 1, 2) | (0, 1, 2) |
| Trygghavn Forsikring | (1, 2, 0) | (1, 2, 0) |
| Varde Systemer | grunn `signal_ikke_regnet` | grunn `signal_ikke_regnet` |
| Kvitstein Mineral | (0, 0, 3) | **(3, 0, 0)** |
| Jordgrøde Gjødsel | (0, 1, 2) | (0, 1, 2) |
| Bølgetopp Tankers | (0, 1, 2) | (0, 1, 2) |
| Lastfjord Container | (0, 0, 3) | **(1, 0, 2)** |
| Signalnett | (0, 1, 2) | (0, 1, 2) |
| Laksevik Sjømat | (0, 1, 2) | **(2, 1, 0)** |
| Tareøy Havbruk | (2, 0, 1) | (2, 0, 1) |
| Matfjord Merkevarer | grunn `kurs_ikke_fra_dagen` | grunn `kurs_ikke_fra_dagen` |

Før: 7 kombinasjoner og 5 som skiller seg ut. Etter: alle 10 og 7 som skiller seg ut.

**Minst 7 av 13 skiller seg ut når alle 10 er med:** 13 av de 15 har en vurdering, og 7 av de 10 kombinasjonene har minst to sjekker som slår ut. Det er de med høyst én grå: (3, 0, 0), (0, 3, 0), (2, 1, 0), (1, 2, 0), (2, 0, 1), (0, 2, 1) og (1, 1, 1). Terskelen er styrke 2 (`TERSKEL`), så hver av dem skiller seg ut. Etter reglene er det nøyaktig 7.

**Marginene** på siste dag, fra målingene i `vurdering`. Lastfjord Container har den minste:
- Lastfjord Container: dagens endring er 2,51 %, mot et standardavvik på 2,23 %. Trendavviket er +0,82 %, innenfor nøytralsonen på ±2 %, og volumforholdet er 1,11.
- Kvitstein Mineral: trendavviket er +3,50 %, og volumforholdet er 2,87.
- Laksevik Sjømat: trendavviket er -6,92 %, og volumforholdet er 2,39.

Testen leser kombinasjonene fra basen, så en endring i parametrene som flytter en av dem, feiler testen.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Demobasene lages bare i midlertidige mapper.
- Frøet, de andre dagene, `NYLIG_NOTERT` og `UTEN_KURSER` står som før.
- Flettes i instruksjonen kl. 18:44 når ingen test feiler, ingen mutant overlever, CI er grønn på head-en, og hvert funn med dom medium eller høyere er rettet (steg 5 i instruksjonen).

**Testtallet før:** 2303 bestått og 17 hoppet over (head-en til PR #57, `b4a0721`, samme kode og tester som main på `43de066`).

*Lagt til 2026-10-17 (gjennomgangen, BH13):* `b4a0721` er head-en til PR #57, `bcac2b5` er flettecommiten på main, og `43de066` er main da grenen ble laget. Etter `bcac2b5` har main bare fått dokumenter, så `src` og `tests` er like i alle tre (`git diff b4a0721 main -- src tests` er tom). Testtallet ble målt på `b4a0721` i instruksjonen kl. 12:07.

**Fingeravtrykkene (BH5):** `FINGERAVTRYKK_KURS_UTEN_SISTE_DAG` og `FINGERAVTRYKK_VURDERING_FOER_SISTE_DAG` er regnet med et skript i scratchpad, én gang med `src/demo.py` fra main (`43de066`) og én gang med koden på grenen. Den gamle koden ga det gamle `FINGERAVTRYKK_KURS` (`73c277d2…`), og begge ga de samme to nye fingeravtrykkene.

## Mutantene

Én om gangen med `-x`, i den ferske klonen med `core.autocrlf=false`, med kopi før og sha256 mot HEAD etter hver. Alle ble fanget på `074cd6f`, først med hele `tests/test_demo.py` og så med bare `TestAlleTiKombinasjonene`:
- R1, regelen for Kvitstein Mineral tatt bort
- R2, regelen for Laksevik Sjømat tatt bort
- R3, regelen for Lastfjord Container tatt bort
- R4, reglene ikke brukt

Med hele fila ble alle fire fanget av `test_kursene_har_samme_fingeravtrykk_paa_alle_plattformer`, som kommer først. Med bare klassen ble de fanget av `test_alle_ti_kombinasjonene_paa_sluttdato`.

## Gjennomgangen

Gjennomgang 17.10 på diffen `main...074cd6f`, med Blind Hunter (BH, 15 funn), Edge Case Hunter (ECH, 5) og Verification Gap (VG, 2). Ingen funn med dom medium eller høyere. Rettingene står i `d63d45c` og i denne spesifikasjonen.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH4, ECH4 | «I samme form som Brattfjell Energi» stemmer ikke helt: den regner fra dagens trukne kurs | low | patch: docstringen og Rettet-linja over |
| BH5 | Ingenting viser hvordan fingeravtrykkene fra før ble regnet | low | patch: kommentaren i testen og avsnittet over |
| BH7, VG2 | Testene viser til mutantene R1–R3, men de sto ikke i spesifikasjonen | low | patch: avsnittet over |
| BH8 | Testen for Lastfjord Container så bare at én sjekk var grønn | low | patch: `(0, 1, 0)` |
| BH1, ECH2, ECH3 | En regel for Brattfjell Energi eller en av de to med grunn ville skrevet over eller blitt borte | low | patch: `test_reglene_gjelder_ikke_aksjene_med_egen_regel` |
| VG1 | Docstringen lovet at testen ser et tall mindre fra frøet | low | patch: det kan ingen test se på siste dag |
| BH12 | «Steg 5» var ikke forklart | low | patch: vilkårene står i Boundaries |
| BH13 | Tre commits for grunnlaget uten forklaring | low | patch: avsnittet over |
| BH14 | «frø» med ø midt i ASCII-tekst | low | patch: «froeet» i koden og testene |
| BH2, ECH1 | `rader[-1]` når `SLUTTDATO` er første dag | low | avvist: `handelsdager()` begynner 2026-01-02, og regelen for Brattfjell har samme forutsetning |
| BH3 | Kursen fortsetter fra regelen hvis dagene går forbi `SLUTTDATO` | low | avvist: `SLUTTDATO` er siste dag i `handelsdager()` |
| BH6 | `SELECT *` i fingeravtrykket av `vurdering` | low | avvist: en ny kolonne skal få testen til å feile, så fingeravtrykket regnes på nytt med vilje |
| BH9, ECH5 | `>= 7` i testen og «nøyaktig 7» her | low | avvist: instruksjonen sier minst 7, og «7 av 15 aksjer skilte seg ut fredag» i `test_demo.py` holder tallet |
| BH10 | Marginen for Lastfjord Container er liten | low | avvist: parametrene er låst (§7.4 i `malinger.md`), og testen feiler hvis kombinasjonen flytter seg |
| BH11 | Ingen test av demoindeksen på siste dag | low | avvist: `test_indeksen_foelger_demoaksjene_hver_dag` i `test_indeks.py` regner indeksen fra `demo.serie` for hver dag (VG) |
| BH15 | Setningen i «Status» blir lang | low | avvist: samme form som de andre sakene i lista |
