---
title: 'Story 8.11b: de 15 i bransjelistene'
type: 'feature'
created: '2026-11-09'
status: 'done'
route: 'dispatch'
baseline_commit: 'aec052e0'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-11-ferdige-lister.md'
---

Skrevet 09.11 i instruksjonen kl. 00:30 (`docs/ai-prompts/2026-11-09.md`, steg 5), etter gruppens svar 08.11 kl. 22:06 under story 8.11 i `epics.md`: «8.11b tar de 15 inn i bransjelistene». Storyen står ikke ellers i `epics.md`. Den bygges på grenen for 8.11 (`8-11-ferdige-lister`, `aec052e0`), i worktreen `G74-lund-osen-8-11b`, og stoppes før flettingen. Spørsmålene står åpne til gruppen har svart; forslaget er det som er bygget.

## Spørsmål til gruppen før flettingen

1. **Hvilke aksjer?** Svaret sier «de 15». *Forslag:* alle aksjene i lista den siste dagen med kurser i basen, både de 15 og egne aksjer fra 2.12, fordi 2.13 hopper over alle aksjene i appens liste (docstringen i `src/omsetning.py`), så ingen av dem har en måling.
2. **Vinduet.** *Forslag:* tre måneder til og med den siste dagen med kurser i basen (`vindu` fra 2.13), det samme for alle aksjene.
3. **Utregningen.** *Forslag:* median av volum × sluttkurs per dag, med `regn_ut` fra 2.13 og `slutt` (ujustert) som `close`. `Maaling`, `vindu`, `_tall`, `regn_ut` og `MAANEDER` er flyttet uendret fra `src/omsetning.py` til en ny modul, `src/omsetningsregning.py`, som `omsetning.py` importerer dem fra. Da bruker webserveren dem uten å importere `fetch_prices` (AD-10, `test_webserveren_henter_aldri` i `tests/test_valg.py`).
4. **En eldre måling.** En egen aksje kan ha en rad i `omsetning` fra før den kom i lista. *Forslag:* for en aksje i lista gjelder medianen av kursene.
5. **Bransjen.** *Forslag:* bransjen i `aksje` (`sektor`), ikke `BRANSJE` i `ferdige_lister.py`, som bare har de målte.
6. **Lista over Oslo Børs.** *Forslag:* bare aksjer som står i `boersliste`, som de andre i de ferdige listene (spørsmål 3 i 8.11) og valideringen i `bruk_liste`.
7. **Ingen tall i koden eller repoet (regel 16).** *Forslag:* medianene regnes når siden vises og lagres ikke. Prøven på `ose.db` står bare med antall i spesifikasjonen.
8. **Demoen.** Demobasen har de 15 oppdiktede selskapene i `boersliste` (`lag_demobase` i `src/demo.py`). *Forslag:* demoen får bransjelister også for dem, som den ekte versjonen, og bildet av «Din egen liste» tas på nytt.
9. **«Utenfor målingen».** Merket fra 2.12 leser `omsetning`. *Forslag:* uendret i 8.11b, så de 15 merkes som før; å bruke medianen av kursene også der er en egen endring.

*Svar 2026-11-09 kl. 10:23 (gruppens svar):* forslagene i spørsmål 1–10 er godtatt, også spørsmål 10 under «Spørsmål etter gjennomgangen» og utvidelsen av spørsmål 1 etter ECH1. Spørsmål 9: merket «Utenfor målingen» er uendret i 8.11b, og å bruke medianen av kursene også der er et punkt i `issues.md` til senere. Koden er ikke endret med svaret. Svaret er ført etter instruksjonen kl. 10:28 i `docs/ai-prompts/2026-11-09.md`.

## Intent

**Problem:** De ferdige listene i 8.11 tar bare med aksjer som er målt i `omsetning` (2.13), og 2.13 måler aldri aksjene i appens liste. De 15 står derfor ikke i noen bransjeliste.

**Approach:** `lister()` i `src/ferdige_lister.py` regner medianen for aksjene i lista av kursene i basen når siden vises, med samme utregning som 2.13, og tar dem med i bransjen de har i `aksje`.

## Delene

### A) Aksjene i lista
`_aksjene_i_lista` leser aksjene i lista den siste dagen med kurser (`inn` og `ut`, som `les_lista`), som står i `boersliste`.
- **Ville feilet hvis:** de 15 manglet i bransjelistene, eller en aksje som er tatt ut, var med.

### B) Vinduet
Tre måneder til den siste dagen med kurser i basen.
- **Ville feilet hvis:** en kurs eldre enn vinduet var med i medianen.

### C) Kursene foran en eldre måling
- **Ville feilet hvis:** en eldre rad i `omsetning` ble brukt for en aksje i lista.

### D) Lista over Oslo Børs
- **Ville feilet hvis:** en aksje utenfor `boersliste` kom i en ferdig liste.

### E) Samme utregning, uten hentingen
- **Ville feilet hvis:** 2.13 og 8.11b regnet hver sin måte, eller webserveren importerte `fetch_prices`.

## Grenser

Ingen API-kall, `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` leses bare med `mode=ro` (regel 22). Ingen migrasjon. Ingen tall fra kildene i koden, testene eller spesifikasjonen (regel 16).

## Bygget 09.11 (instruksjonen kl. 00:30)

Bygget på grenen `8-11b-de-15-i-bransjelistene`, i worktreen `G74-lund-osen-8-11b`, fra `aec052e0`, med 8.11 flettet inn igjen etter rettingen av hjelpen (`ae003568`).

- **Filene.** `src/omsetningsregning.py` (ny, med `Maaling`, `vindu`, `_tall`, `regn_ut` og `MAANEDER` flyttet uendret fra `src/omsetning.py`, som importerer dem derfra), `_aksjene_i_lista` og `lister` i `src/ferdige_lister.py`, teksten under «Start fra en ferdig liste» i `src/templates/_egne.html`, og «Hva er de ferdige listene og filteret?» i `docs/hjelp.md` (regel 19). Ordlista forbyr «de tre» på sidene, så teksten sier «for tre måneder bakover».
- **Tester («Ville feilet hvis» i hver):** `tests/test_ferdige_lister_8_11b.py`. `test_demoen_har_kraft_og_eiendom` i `tests/test_ferdige_lister.py` krever nå de ni bransjelistene i demoen, i rekkefølgen fra `designregler.md` §4 (spørsmål 8). `omsetningsregning.py` står bak bildene i `tests/test_docker.py`, og bildet av «Din egen liste» er tatt på nytt (1432 px).
- **Prøven på `ose.db`:** basen ble kopiert med SQLite sin backup fra en tilkobling med `mode=ro` til en midlertidig mappe og migrert der, og `boersliste` ble fylt fra `data/proever/symbolliste-OL-2026-10-22.json` med `les_boerslista`, uten kall og uten `fetch_prices.py`. Lista har 15 aksjer. Alle 15 fikk en median av kursene og står i en ferdig liste, og det er 13 bransjelister. Bare antallene står her (regel 16). Den midlertidige mappa er slettet, og sha256 for `data/db/ose.db` var den samme før og etter.

## Mutantene

Én per del på arbeidskopien, med kopi før og sha256 lik etter: A (ingen aksjer fra lista) fanget av `test_en_aksje_i_lista_er_med_med_medianen_av_kursene`, A2 (`ut` ignoreres) av `test_en_aksje_som_er_tatt_ut_er_ikke_med`, C (en eldre måling går foran) av `test_kursene_gaar_foran_en_eldre_maaling`, D (uten `boersliste`) av `test_bare_aksjer_i_boerslista`, og E (`ferdige_lister` importerer `omsetning`) av `TestSammeUtregning`. B (uten `BETWEEN` i SQL-en) overlevde, fordi `regn_ut` selv bare tar med radene i vinduet, så `BETWEEN` bare gjør spørringen mindre. B2 (vinduet fra `date.min`) ble fanget av `test_vinduet_er_tre_maaneder_til_siste_kursdag`.

## Spørsmål etter gjennomgangen

10. **Ulike vinduer (BH2).** De målte medianene er fra vinduet den dagen de ble målt, og medianene regnet av kursene fra vinduet til siste dag med kurser. Begge rangeres sammen. *Forslag:* godta det, fordi målingene i 2.13 er av aksjer som ellers ikke ville vært med, og teksten sier nå hvor hver median kommer fra. Funnet er middels og står åpent til gruppen har svart (regel 25).

*Svar 2026-11-09 kl. 10:23 (gruppens svar):* forslaget er godtatt. BH2 er besvart og lukket, med graden middels som før (regel 25). Svaret er ført etter instruksjonen kl. 10:28 i `docs/ai-prompts/2026-11-09.md`.

*Lagt til 2026-11-09 (gjennomgangen, ECH1):* spørsmål 1 er utvidet i det som er bygget: medianen regnes for alle aksjene appen følger eller har fulgt som har kurser i vinduet, ikke bare dem i lista, så en aksje som er tatt ut, ikke faller ut av bransjelistene før 2.13 har målt den.

## Gjennomgangen 09.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

To gjennomganger av byggingen før `a08a7f6a`, i parallell med hele settet: Blind Hunter med bare diffen (7 funn), og Edge Case Hunter og Verification Gap i samme agent med repoet (5 og 4 funn). Ingen høye.

**Middels**
- *ECH1, rettet.* En aksje som ble tatt ut av lista, falt ut av alle bransjelister, fordi 2.13 hopper over aksjene i lista. Nå regnes medianen for alle aksjene i `aksje` som står i `boersliste` og har kurser i vinduet, og en målt aksje uten bransje i `BRANSJE` får bransjen i `aksje` (`test_en_aksje_som_er_tatt_ut_er_med_saa_lenge_den_har_kurser`, `test_en_aksje_tatt_ut_uten_kurser_i_vinduet_bruker_maalingen`).
- *BH1 og VG4, rettet.* Hjelpen sa at gruppen har sjekket bransjen for hver aksje, og at listene er de som ble omsatt for mest da omsetningen sist ble målt. Nå sier hjelpen og teksten under «Start fra en ferdig liste» hvor medianen kommer fra, og at bransjen for en aksje brukeren følger selv, er den brukeren valgte.
- *ECH2, åpent* med spørsmål 9 (regel 25): merket «Utenfor målingen» leser `omsetning`, så en egen aksje kan stå som ikke målt i tabellen og med en median i den ferdige lista.
- *BH2, åpent* som spørsmål 10 (regel 25).

- *ECH2, lukket 2026-11-09 med spørsmål 9* (gruppens svar kl. 10:23), middels som før (regel 25): merket er uendret i 8.11b, og endringen er et punkt i `issues.md` til senere. VG3 venter på den samme endringen.
- *BH2, lukket 2026-11-09 med spørsmål 10* (gruppens svar kl. 10:23), middels som før (regel 25): forslaget om å godta ulike vinduer er godtatt.

**Lav**
- *Rettet:* BH3 og VG1 (en aksje i lista uten kurser i vinduet bruker ikke en eldre måling), BH5 (en dato i `kurs` som ikke kan leses, gir ingen lister herfra i stedet for en feil), BH6 (en test for dagen vinduet begynner og dagen før), ECH3 og VG2 (regelen for `inn` og `ut` bestemmer nå bare hvilke aksjer som aldri bruker en eldre måling).
- *Ført:* BH4 og ECH4 (`max(dato)` over hele `kurs` og én spørring per aksje, for hver side med basen), ECH5 (ingen minste antall dager i vinduet, som i 2.13), VG3 (ingen test for merket «Utenfor målingen» for de 15, venter på spørsmål 9), B-mutanten.
- *Ikke reelt:* BH7 (`kode` er primærnøkkel i `boersliste`).

**Mutantene for rettingene:** F1 (bare aksjene i lista regnes), F2 (bare de med median går foran målingen), F3 (ingen bransje fra `aksje` for de målte) og F4 (`ValueError` fanges ikke), hver fanget av sin test, med fila lik etterpå.

*Lagt til 2026-11-10:* 8.11b er flettet med PR #129 i `4d87658d` kl. 00:46, låst til head-en `5fb09223`, etter nattflettingen (kl. 12:00 i `docs/ai-prompts/2026-11-09.md`) og gruppens svar 09.11 kl. 10:55. Main, med squash-flettingen av #128 i `b5e423fe`, ble flettet inn i `5fb09223` uten konflikter, og diffen mot main er endringene grenen hadde mot `a346fd98`. Hele settet alene i fire deler 00:29:50–00:41:44: 4798 bestått, 24 hoppet over og 0 feilet, til sammen de 4822 som `pytest --collect-only` finner. CI var grønn på head-en (run 42722548552). Treet på main etter `git pull --ff-only` er likt treet på `5fb09223`. ECH2 og BH2 er lukket med spørsmål 9 og 10, middels som før (regel 25), og ingen funn på middels eller over sto åpne. 8.11b har fått en egen linje i `sprint-status.yaml`.
