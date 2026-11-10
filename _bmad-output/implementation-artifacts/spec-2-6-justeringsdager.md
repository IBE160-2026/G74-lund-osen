---
title: 'Story 2.6 og 8.14: justeringsdagene, regnet av kursserien alene'
type: 'feature'
created: '2026-11-09'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '1a72810a'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/begrunnelser.md'
---

Skrevet 09.11 i ekstravinduet (instruksjonen limt inn kl. 11:00, med tilleggene kl. 11:28, 12:00 og 15:43, som føres i `docs/ai-prompts/2026-11-09.md` i steg 4). Gruppens svar 09.11 kl. 10:30 og 10:43: 2.4, 2.6 med 8.14, 8.7 og 8.9 bygges i dag og flettes onsdag etter brukertesten. Instruksjonen sier for 2.6 og 8.14: «dagene regnes av kursserien alene, prøvd på ose.db med mode=ro, med bare antallet i repoet.» Bygget fra head-en til PR #126 (`1a72810a`), på grenen `2-6-justeringsdager`, i worktreen `G74-lund-osen-2-6`, og stoppet før flettingen. Spørsmålene står åpne til gruppen har svart; forslaget er det som er bygget.

## Spørsmål til gruppen før flettingen

1. **Navnet.** FR-407 og 2.6 heter «utbyttedager», mens FR-407 (tillegget 08.10) og 8.14 sier at sidene skal si «justeringsdag», fordi metoden ser justeringer og en splitt gir samme utslag (`begrunnelser.md` §11). Navnet skulle avgjøres i planen for 2.6 (epics.md, rekkefølgen 07.10). *Forslag:* sidene sier «justeringsdag» også for 2.6. Navnet på kravet og storyen står til gruppen har svart, og føres i steg 4.
2. **Terskelen.** *Forslag:* en dag er en justeringsdag når endringen i sluttkursen og i den justerte kursen skiller seg med mer enn 0,1 prosentpoeng (`TERSKEL_PP`). Målingen 21.09 fant 38 hendelser fra 0,05 til 0,5 pp. Prøvd på `ose.db` med `mode=ro` 09.11, med sha256 for basen lik før og etter: 40 justeringsdager for de 15 aksjene, minst én for hver. Antallet er det samme fra 0,05 til 0,5 pp, 41 ved 0,01 og 36 ved 1,0. Bare antallene står her.
3. **Hvor 2.6 merkes.** *Forslag:* «justeringsdag» under endringen i oversikten og Min liste, med en forklaring ved musepekeren, og i kortet for endringen på aksjesiden. Merket gjelder endringen for én dag, så det står ved siste børsdag og en dag valgt med datoen, ikke ved en periode. Børsometeret og linja under i «Sammenlign med» får det ikke: rutene har lite plass, og linja under er en endring over flere dager.
4. **Kursgrafen (8.14).** *Forslag:* en kort strek nederst i grafen for hver justeringsdag grafen har, og under grafen hvor mange det var det siste året til dagen siden viser (365 dager, `AARET`), og den siste dagen. Teksten sier ikke «utbytte» og ikke noe om neste justering (NFR-06).
5. **Merket.** Endringsforslaget 13.10 spurte om merket skulle være bokstaven U (spørsmål 6 der). *Forslag:* ordet «justeringsdag», ikke en bokstav, så det leses uten forklaring.
6. **Demoen.** De oppdiktede kursene i demoen har ingen justeringsdager, så bildet av aksjesiden viser bare «Ingen justeringsdager det siste året.» *Forslag:* som bygget. Å legge en justering inn i demodataene endrer tallene på alle sidene i demoen og bildene.
7. **Beløpet.** Endringsforslaget 13.10 nevner utbyttet med beløp fra EODHD (2.15), og 8.18 eks.dato i grafen. 2.15 står ikke i epics.md, og 8.18 er utenfor v1 (svaret kl. 10:43). *Forslag:* utenfor denne storyen; grafen sier bare «justeringsdag».

*Svar 2026-11-10 kl. 11:52 (gruppens svar):* alle sju forslagene er godtatt, så sidene sier «justeringsdag». Rådet anbefalte det. Svaret er ført etter instruksjonen kl. 15:24 i `docs/ai-prompts/2026-11-10.md`.

## Intent

**Problem:** Oversikten viser sluttkursen, mens endringen regnes på den justerte kursen. En dag kilden regner de eldre kursene om, stemmer ikke endringen med de to sluttkursene, og det ser ut som en feil (FR-407).

**Approach:** `src/justeringsdager.py` finner dagene av to kolonner i `kurs`, uten meldinger og uten kall. Oversikten, aksjesiden og grafen bruker den.

## Delene

### A) Regelen (2.6)
`er_justeringsdag` og `justeringsdager` i `src/justeringsdager.py`.
- **Ville feilet hvis:** en vanlig dag ble merket, en dag der de to endringene spriker, ikke ble det, terskelen var en annen, eller dagene ble lest fra en annen kilde enn kursserien.

### B) Oversikten og Min liste (2.6)
`Rad.justeringsdag` i `src/markedsoversikt.py` og `src/templates/index.html`.
- **Ville feilet hvis:** en aksje uten justeringsdag ble merket, merket sto ved en periode, eller en valgt dag fikk merket fra siste børsdag.

### C) Aksjesiden (2.6)
`Detalj.justeringsdag` i `src/aksjedetalj.py` og kortet i `src/templates/aksje.html`.
- **Ville feilet hvis:** kortet ikke sa at dagen er en justeringsdag, eller sa det for en aksje uten.

### D) Kursgrafen (8.14)
`Graf.justeringsdager` i `src/graf.py`, `justeringer` i `aksjeside` i `src/app.py`, og teksten under grafen.
- **Ville feilet hvis:** grafen ikke merket dagen, antallet og den siste dagen manglet, teksten sa «utbytte» eller noe om neste justering, eller grafen merket andre dager enn regelen i A.

### E) Hjelpen og bildene
«Hva er en justeringsdag?» i `docs/hjelp.md` (regel 19). Bildet av aksjesiden er tatt på nytt, og avtrykkene er regnet ut på nytt med `src/justeringsdager.py` bak begge bildene.

## Grenser

Ingen API-kall, `src/fetch_prices.py` kjøres bare i testene med en falsk henter, og `data/db/ose.db` leses bare med `mode=ro` for antallet. Ingen migrasjon: dagene regnes når siden vises, og lagres ikke.

## Bygget 09.11 (ekstravinduet)

Bygget på grenen `2-6-justeringsdager`, i worktreen `G74-lund-osen-2-6`, fra `1a72810a`. Filene: `src/justeringsdager.py` (ny), `src/markedsoversikt.py`, `src/aksjedetalj.py`, `src/graf.py`, `src/app.py`, `src/templates/index.html`, `src/templates/aksje.html`, `src/static/stil.css`, «Hva er en justeringsdag?» i `docs/hjelp.md` og testene i `tests/test_justeringsdager_2_6_8_14.py`. Bildet av aksjesiden er tatt på nytt med DevTools-protokollen. Det nye er setningen «Ingen justeringsdager det siste året.» under grafen. De åtte andre bildene er byte for byte de samme. `src/justeringsdager.py` står bak begge bildene i `tests/test_docker.py`, og avtrykkene er regnet ut på nytt.

## Mutantene

Én per del på `37468807`, med kopi før og fila lik HEAD etterpå: A (terskelen 1,0) fanget av `test_terskelen`, B (merket står ved en periode) av `test_ikke_for_en_periode`, C (kortet merker hver dag med to rader) av `test_kortet_sier_justeringsdag`, og D (året til siste rad, ikke dagen siden viser) av `test_dagene_er_de_samme_som_2_6_finner`.

## Gjennomgangen 09.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Diffen `1a72810a..37468807`, uten `tests/test_docker.py` og bildet: Blind Hunter med bare diffen (12 funn), og Edge Case Hunter og Verification Gap i samme agent med repoet (4 og 7 funn, med 11 mutanter i en kopi utenfor worktreen). Ingen høye.

**Middels**
- *VG1, VG2 og VG3, rettet.* Testene så bare antallet streker, én justeringsdag og et oppsett der alle radene før siste dag var justert. Nå har EQNR to justeringsdager, 15.09 og 22.09, strekene står ved dagene (`test_strekene_staar_ved_dagene`), den siste dagen er 22.09, og en valgt dag 16.09 er ikke merket. Mutantene M2, M3 og M11, som overlevde, ble fanget.
- *BH1, rettet.* Grafen fikk bare dagene det siste året. Nå får den alle justeringsdagene i serien og merker dem den har. Mutanten der grafen får dagene for året, overlever, fordi serien aldri er lengre enn ett år (`DAGER_TILBAKE`), så de to dekker de samme dagene.
- *BH4, rettet.* Skjermleseren får datoene for strekene, som for signaldagene (8.8).
- *BH2, ikke reelt.* `rader` er hele kursserien, ikke perioden i grafen.
- *BH3, ikke reelt.* Linja under i «Sammenlign med» bygges av `bygg_sammenligning` uten merket, og malen viser det ikke der (Edge Case Hunter kontrollerte det samme).

**Lav**
- *Rettet:* ECH1 og BH11 (året begynner på samme dato året før, som «1 år» i grafen, ikke 365 dager tilbake, `aaret_foer`), ECH2 og VG4 (kortet sier «Justeringsdag» bare når det har en endring), ECH3 (hjelpen sa at en splitt gir samme utslag; det er ikke målt, så hjelpen sier bare «for eksempel etter et utbytte»), ECH4 (hjelpen sier at kortet på aksjesiden alltid gjelder én dag), VG6 (forklaringen ved musepekeren og setningen om strekene er testet).
- *Ført:* BH5 (en rad som mangler: merket følger det samme radparet som endringen, som `endring_med_datoer` viser), BH6 (kortet på aksjesiden gjelder alltid én dag), BH7 og VG5 (en forskjell på nøyaktig 0,1 pp kan ikke lages med flyttall; testen prøver like under og like over), BH8 (testen av importene viser at modulen ikke leser noe annet enn kursradene den får), BH9 (testene leter etter klassen slik malen skriver den), BH10 (bildet og avtrykkene er i commiten `37468807`), BH12 (stilen for merket gjelder tabellene i oversikten og Min liste), VG6 (Min liste er ikke hentet i testene; den bruker samme mal og samme `Rad`), VG7 (grensen for året er testet i `test_det_siste_aaret`).

*Lagt til 2026-11-09 under spørsmål 1 (gjennomgangen, ECH3):* om en splitt gir samme utslag, er en påstand i `begrunnelser.md` §11, forbehold 1, og ikke målt. Det endrer ikke forslaget.
