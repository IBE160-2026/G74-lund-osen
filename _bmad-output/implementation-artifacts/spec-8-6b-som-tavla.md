---
title: 'Story 8.6b: børsometeret som tavla'
type: 'feature'
created: '2026-10-26'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '9d64d4f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-6-boersometeret.md'
---

## Intent

**Problem:** børsometeret fra 8.6 har ruter i tre faste størrelser som brytes i rader, farge i to trinn, og hovedindeksen med søylene over rutene. Tavla er et fylt kart, og gruppen vil ha det likt tavla.

**Grunnlaget:** story 8.6 i `epics.md`, med «Avgjort 2026-10-24 kl. 11:54 (gruppens svar)»: børsometeret gjøres likt tavla i 8.6b, søylene tas ut av børsometeret og står bare på oversikten, og hovedindeksen står som et tall i linja «Mål mot børsen». «Avgjort 2026-10-25 kl. 21:41 (gruppens svar)»: 8.6b bygges i natt og stopper før flettingen med bilder, og gruppen avgjør flettingen mandag før kl. 21:20. Periodene er 8.17b. Svarene 23.10 kl. 09:24 står. Instruksjonen er den kl. 01:18 i dagsfila 26.10.

## Slik er det i dag (slått opp 26.10 på `9d64d4f`)

- **Rutene** er `<a class="rute stoerrelse-…">` i `ul.ruter` med `flex-wrap`, i tre bredder (96, 120 og 150 px) etter `stoerrelse` i `src/boersometer.py`: under 1, fra 1 til og med `volumfaktor`, og over.
- **Fargen** er to trinn og grått: `--opp-bakgrunn` når endringen slik den vises er over 0, `--ned-bakgrunn` under 0, og `--ingen-bakgrunn` ved 0,00 % eller uten endring.
- **Rammen** er 3 px: `--blekk` ved 2 av 3 og `--gul-symbol` med 2 px hvitt innenfor ved 3 av 3 (VG7 i 8.6).
- **Hovedindeksen** står over rutene gjennom `_hovedindeks.html`, med søylene, for siste børsdag også når «Velg dag» viser en annen dag.
- **Volumforholdet** er `volumforhold` i vurderingen: dagens volum mot medianen av volumet de `VOLUM_VINDU` (20) børsdagene før (`interesse` i `src/signalberegning.py`, `volumer[-(p.volum_vindu + 1) : -1]`).
- **Endringen i indeksen** regnes av `indeksendring` i `src/hovedindeks.py`, mot forrige børsdag etter kalenderen.
- **Tavla** ligger i Claude og ikke i repoet (`spec-8-6-boersometeret.md`, «Utdraget fra tavla»). Det tavla viser, står i instruksjonen og avgjørelsene.
- **Siden** er `main` med høyst 65rem (1040 px) og 16 px på hver side: 1008 px innhold i et vindu 1280 px bredt, og 358 px i et vindu 390 px bredt.

## Kontrollpunktene

- **a) Forklaringen øverst:** «Hver rute er en aksje, samlet etter bransje. Fargen viser endringen fra børsdagen før, og jo større ruta er, jo mer ble aksjen omsatt sammenlignet med vanlig. Klikk på en rute for å se aksjen. Bildet viser hva som skjedde, ikke hva du bør kjøpe eller selge.»
- **b) Linja «Mål mot børsen»:** «Farge · endring fra» ukedagen for børsdagen før, «Størrelse · volum mot medianen for de 20 børsdagene før», og «Hovedindeksen ·» endringen den dagen som tall med fortegn og farge, eller – når den mangler. Søylene og `_hovedindeks.html` tas ut av børsometeret, ikke av oversikten.
- **c) Fem fargetrinn** etter tallet slik det vises: under ±0,5 % `#E9E7E1`, fra 0,5 til 2 % `#B4E2C4` og `#F6C2BB`, 2 % eller mer `--opp` og `--ned` med hvit tekst, som navn i `:root` i `stil.css`. Under kartet «Hva fargene betyr» med de fem trinnene og de to rammene. Rammene som på tavla, tykke med en hvit linje innenfor, i `--blekk` for 2 av 3 og `--gul-symbol` for 3 av 3 (VG7), med minst 3:1 mot ruta.
- **d) Et fylt kart i to nivåer**, regnet i `src/boersometer.py`: bransjene som felt etter summen av volumforholdet, og aksjene inne i feltet, squarified og i prosent. Navnet står på ruter som er store nok, og ingen rute er mindre enn 44 × 44 px i et vindu 390 px bredt. Tabellen under står.
- README-en, `docs/hjelp.md` og hjelpetekstene følger med (regel 19).
- Tester med «Ville feilet hvis»: hvert trinn ved grensene, kartet dekker feltet uten overlapp med areal etter vekten, én rute per aksje, «1 aksje», tallet i linja, og ingen søyler på børsometeret.

## Planen, én commit per punkt

1. a) Forklaringen øverst, med test. `test_ingen_raad_og_ingen_ki` tar setningen ut før den leter etter «kjøp» og «selg», fordi instruksjonen krever den.
2. b) Linja «Mål mot børsen», `indeks_for_dagen` i `src/boersometer.py`, `_hovedindeks.html` ut av `boersometer.html`, hjelpen og testene.
3. c) `fargetrinn` og trinnene i `src/boersometer.py`, navnene i `:root`, rammene, «Hva fargene betyr», hjelpen og testene.
4. d) `kart` og `squarify` i `src/boersometer.py`, kartet i malen og stilen, README-en, hjelpen og testene. Testene for de tre faste størrelsene erstattes av testene for arealet, med grunnen.

## Avgjort i spesifikasjonen

- **«Børsdagen før»** i linja er datoen før dagen som vises blant kursdatoene for aksjene i lista, den samme som endringen i rutene regnes fra. Har dagen ingen dag før, står «Farge · endring fra børsdagen før».
- **Hovedindeksen i linja** er endringen for dagen som vises, ikke for siste børsdag, fordi linja sier «den dagen». Har indeksen ingen rad den dagen, eller ingen rad for børsdagen før etter kalenderen (`indeksendring`), står «–». Kan indeksen ikke leses, står også «–», og kartet vises som vanlig (NFR-03).
- **Trinnene** regnes av `avrundet(endring, "endring")`, to desimaler: under 0,5 i tallverdi nøytral, fra 0,5 til under 2 lys, fra 2 sterk. 0,50 % er lys, og 2,00 % er sterk. En rute uten endring, også «Uten data», er hvit med stiplet kant, så den ikke ligner det nøytrale trinnet.
  *Rettet 2026-10-26 (punkt c):* kanten er grå og heltrukken, ikke stiplet, fordi stiplet er indekslinja på oversikten (2.9b, `test_bare_indekslinja_er_stiplet`).
- **Kontrasten mot ruta:** `--blekk` har 2,88:1 mot `--opp` og 2,70:1 mot `--ned`, og `--gul-symbol` 1,61–3,09:1 mot trinnene (regnet med WCAG-formelen 26.10). Begge har over 3:1 mot hvitt (17,76 og 3,82). Rammen grenser derfor bare mot hvitt: den hvite linja innenfor og den hvite bakgrunnen i kartet utenfor. Det er slik «minst 3:1 mot ruta» er oppfylt. Testen regner kontrasten fra fargene i `:root`.
  *Avgjort 2026-10-26 kl. 08:43 (gruppens svar, a):* rammene måles mot det de grenser mot, den hvite linja innenfor og det hvite rundt ruta, og der har begge minst 3:1.
- **Vekten** er volumforholdet. En aksje uten volumforhold, uten vurdering eller uten kurs, får vekten 1, det vanlige. Vekten er minst `MINSTE_VEKT` (0,25), så en aksje med nesten ikke noe volum fortsatt får en rute det går an å trykke på. Feltet for en bransje har summen av vektene.
  *Rettet 2026-10-26 (punkt d):* vekten holdes mellom 0,5 og 3 (`MINSTE_VEKT` og `STOERSTE_VEKT`). Målt 26.10 med 200 tilfeldige dager for 15 aksjer i 8 bransjer, med volumforholdet lognormalt fordelt med sigma 0,5 og 0,8: med gulvet 0,25 og uten tak ble den smale flaten 1,86 og 3,64 ganger bredden i median og 4,18 og 11,25 ved 95-persentilen. Med 0,5 og 3 ble den 1,52 og 2,07 i median og 2,70 og 3,43 ved 95-persentilen. Grunnen er at den minste vekten må få 48 × 48 px, og overskriften i hvert felt har fast høyde. En aksje med volum under halvparten eller over tre ganger vanlig får samme størrelse som grensen, og tabellen under har det faktiske tallet. Demoen har volumforhold fra 0,44 til 4,51. Gruppen bør se på dette.
  *Avgjort 2026-10-26 kl. 08:43 (gruppens svar, b):* vekten holdes mellom 0,5 og 3 ganger vanlig volum, og hjelpen sier det: hjelpen ved «?» og `docs/hjelp.md` sier at ruta ikke blir større over tre ganger vanlig volum eller mindre under halvparten, og at tabellen under har tallet (`test_hjelpen_sier_det`).
- **To kart, én rute:** kartet regnes for to flater, bred (vinduer bredere enn 760 px) og smal (760 px og smalere), og hver rute får plassen i begge som egenskaper i `style`. Stilen velger med `@media`. Hver flate regnes ved den minste bredden den brukes på: 729 px (et vindu 761 px bredt) og 288 px (et vindu 320 px bredt). Høyden starter på halve bredden og 1,4 ganger bredden, og økes med 5 % til hver rute er minst 48 × 48 px ved den bredden: 44 px og 2 px hvitt på hver side. Ved 390 px er det da minst 48 × 358/288 ≈ 59,7 px.
  *Rettet 2026-10-26 (punkt d):* den smale flaten regnes ved 358 px, et vindu 390 px bredt, som instruksjonen sier, ikke ved 288 px. Høyden starter på 1,2 ganger bredden og økes med 2 %. Ved 320 px kan en rute derfor være 44 × 288/358 ≈ 35 px, med 2 px hvitt rundt. `squarify` tar også hensyn til minstemålet når den fyller en rad.
  *Avgjort 2026-10-26 kl. 08:43 (gruppens svar, c):* ved 390 px er ingen rute under 44 × 44 px, og ved 320 px ingen under 24 × 24 px (WCAG 2.2, 2.5.8). Ved 320 px er det minst 48 × 288/358 − 4 ≈ 34,6 px, og `test_ingen_rute_under_24_px_i_320_px` sjekker det.
  *Rettet 2026-10-26 (gjennomgangen, ECH):* den brede flaten regnes ved 712 px, ikke 729 px. `@media (min-width: 761px)` regner med rullefeltet, så et vindu 761 px bredt med et rullefelt på 17 px har 712 px innhold, og ved 729 px kunne en rute der bli 48 × 712/729 − 4 ≈ 42,9 px (`test_ingen_rute_under_44_px_i_761_px_med_rullefelt`).
- **Navnet** er symbolet, som i rutene fra 8.6. Det står når ruta er minst 9 px per tegn pluss 10 px bred og 40 px høy, endringen når den i tillegg er minst 74 px bred og 60 px høy, og merket og grunnen når den er minst 96 × 88 px, regnet ved den minste bredden for flaten. En rute som er for liten, har alt i den skjulte teksten, og tabellen under har tallene.
  *Rettet 2026-10-26 (gjennomgangen, VG, ECH og BH):* nivået regnes for den synlige ruta, uten de 2 px hvitt på hver side, ved den minste bredden flaten brukes på: 712 px og 288 px (`Flate.minste`). Før ble den smale flaten regnet ved 358 px og med kanten, så teksten kunne kuttes i et vindu 320 px bredt. Følgen er at de minste rutene i et vindu 390 px bredt ikke viser symbolet; tabellen under har det. To nye tester: nivået i kartet og klassene på siden.
  *Avgjort 2026-10-26 kl. 13:00 (gruppens svar, c) og kl. 13:07 (e):* tekstnivået regnes ved den minste bredden i hvert spenn av vinduer, med 16 px på hver side: fra 1080 px ved 1008 px, full bredde (`bredest`), mellom 761 og 1080 px ved 712 px (`bred`), fra 360 px ved 328 px (`smal`), og under 360 px ved 288 px (`smalest`). `Flate.tekst` har klassen og bredden, hver rute har fire klasser `nivaa-<klasse>-N`, og stilen velger med `@media`. Kartet er det samme; bare teksten i rutene endres. Et vindu 1080 px bredt med et rullefelt på 17 px har 1063 px, og `main` er da fortsatt 1040 px, så 1008 px holder. Et vindu fra 360 px med et rullefelt har mindre enn 328 px innhold, ned til 311 px; der kan teksten i en rute kuttes av `overflow: hidden`, men den står i den skjulte teksten og i tabellen. Mobiler har rullefelt som ikke tar plass.
  *Rettet 2026-10-26 (gjennomgangen av endringene etter `00bd6e1`, BH og ECH):* stilen velger klassen med `@container` på kartet, ikke med `@media` på vinduet: `bredest` når kartet er minst 1008 px og `bred` under, når vinduet er bredere enn 760 px, og `smal` når kartet er minst 328 px og `smalest` under, ellers. Da måles den bredden teksten er regnet ved. Et vindu fra 360 px uten rullefelt gir et kart på 328 px, som svaret kl. 13:00 sier, og med rullefelt gjelder 328 px først når kartet er så bredt, så teksten ikke kuttes. Det samme gjelder fra 1080 px og en rotskrift under 16 px, og det blir ingen hull mellom spennene ved zoom. Avsnittet over om rullefeltet ved 360 px gjelder ikke lenger.
- **Overskriften i feltet** er 24 px høy ved den minste bredden, med symbolet, navnet, snittet og antallet, og kuttes med «…» når feltet er smalt. Tabellen under har de samme tallene.
  *Rettet 2026-10-26 (gjennomgangen av endringene etter `00bd6e1`, BH):* overskriften er 24 px ved bredden flaten regnes ved, 712 og 358 px, og krymper med kartet, ikke 24 px ved den minste bredden. Ved 288 px er den 24 × 288/358 ≈ 19,3 px, og linja med navnet er 16 px, så den har plass (`test_overskriften_har_plass_til_linja`). BH11 i triagen over avviste det samme, med 19,3 px.
  *Avgjort 2026-10-26 kl. 13:00 (gruppens svar, b):* overskriften er som på tavla, navnet og «snitt» med tallet, eller «1 aksje» ved én aksje, og antallet står i tabellen. Tillegget står i samme flex-linje som navnet, og får det ikke plass, brytes det til linje to, som ligger under en `row-gap` høyere enn linja og skjules av `overflow` for øyet, men ikke for skjermleseren. Navnet står da alene og kuttes med «…». Navnet har `min-width: 24px` (`MINSTE_NAVN`), og hvert felt er minst `MINSTE_FELT` (46 px: 2 + 14 + 4 + 24 + 2) bredt ved den minste bredden flaten brukes på, så navnet forsvinner aldri helt. For den smale flaten er det 46 × 358/288 ≈ 57,2 px i kartet; for den brede gjelder 48 px fra rutene.

- **Tabellen under kartet**
  *Avgjort 2026-10-26 kl. 15:21 (gruppens svar, f):* tabellen er lukket som standard, i `<details class="tallene">` bak `<summary>Se tallene som tabell</summary>`. Skjermleseren og Tab finner knappen, og innholdet leses når den er åpnet. Svarene om tabellen kl. 08:43 (b, hjelpen sier at tabellen har tallet) og kl. 13:00 (a, rekkefølgen i §4) står. Fotnoten om «ikke vurdert» står under, utenfor den lukkede delen. Får rutene ikke plass og tabellen står alene (NFR-03), er den åpen.

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter: grensen 0,5 flyttet til 1, og arealet uten vekten.

*Utfallet 26.10 på `4af6efa`:* begge ble fanget, grensen av `test_hvert_trinn_ved_grensene[0.4951-lys-opp]` og arealet av `test_arealet_foelger_volumforholdet_i_tabellen`. Fila var lik HEAD etterpå.

*Utfallet 26.10 kl. 09:25 på `6f5815b`, etter rettelsene i kartet fra gjennomgangen:* begge ble fanget av de samme testene. Arealet uten vekten er `squarify([1.0 for r in bransje.ruter], …)` i `_legg_ut`. Fila var lik HEAD etterpå, med samme sha256 som `git show HEAD:src/boersometer.py` med CRLF.

*Utfallet 26.10 kl. 16:08 på `38cbb3e`, etter punktene a–d og rettelsene fra gjennomgangen av endringene etter `00bd6e1`:* begge ble fanget, grensen av `test_hvert_trinn_ved_grensene[0.4951-lys-opp]` (16:08:06) og arealet av `test_arealet_foelger_volumforholdet_i_tabellen` (16:08:09). Fila var lik HEAD etterpå, med samme sha256 som `git show HEAD:src/boersometer.py` og samme `git hash-object`.

## Gjennomgangen

Gjennomgang 26.10 etter hele settet (3721 bestått, 20 hoppet over, 0 feilet, 09:05:18–09:10:30 på `0deaf5f`), av hele PR-en, diffen `de1cd7d..0deaf5f`, med Blind Hunter (BH, 14 funn), Edge Case Hunter (ECH, 10) og Verification Gap (VG, 3). Rettet i `104b735`, `5cf4244`, `f9ae72c`, `40852ac`, `5eb6de0`, `6f5815b` og her.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH9, ECH1 | `kart()` gir opp med `ValueError`, og ruten fanget den ikke, så siden ville gitt 500 | medium | **rettet** i `104b735`: tabellen står alene (NFR-03), `test_tabellen_staar_naar_rutene_ikke_faar_plass` |
| ECH2, ECH10 | `@media` regner med rullefeltet, så et vindu 761 px bredt har 712 px innhold, og en rute kunne bli om lag 42,9 px | medium | **rettet** i `5cf4244`: den brede flaten regnes ved 712 px |
| VG2, VG3, ECH3, ECH9, BH11 | Tekstnivået ble regnet ved 358 px og med kanten, men den smale flaten brukes ned til 288 px | medium | **rettet** i `f9ae72c`: `Flate.minste`, nivået for den synlige ruta ved 712 og 288 px |
| VG1 | Ingen test leste klassene `nivaa-bred-N` og `nivaa-smal-N` på siden | medium | **rettet** i `f9ae72c`: `test_tekstnivaaet_paa_siden_er_det_kartet_regnet` |
| BH1, ECH8 | Spesifikasjonen sier at overskriften kuttes med «…», men CSS-en hadde bare `overflow: hidden` | medium | **rettet** i `40852ac`: navnet er `.bransjenavn` med `text-overflow: ellipsis` |
| BH4, ECH7 | Fokusringen med `outline-offset: 0` lå inntil den mørke rammen og så ut som en tykkere ramme | medium | **rettet** i `5eb6de0`: 2 px hvitt mellom ruta og ringen |
| ECH6 | `ry - fy - OVERSKRIFT` kunne bli -2,6e-14, som malen skrev «-0.000%» | low | **rettet** i `6f5815b`: målt 109 slike plasser på 300 tilfeldige dager, `test_ingen_plass_er_negativ` |
| BH6 | «Mutantene» hadde ikke utfallet | low | **rettet** her: Utfallet-linjene over |
| BH2 | Tab-rekkefølgen er rekkefølgen i designregler §4, men `squarify` legger den største ruta først, så fokuset hopper i kartet (WCAG 2.4.3) | medium | **under «Åpent»:** rekkefølgen i HTML-en er den samme som i tabellen og overskriftene, og å endre den eller la `squarify` følge §4 er et valg for gruppen. Ikke rettet |
| BH5 | Den smale flaten brukes opp til 760 px, og kartet blir da om lag dobbelt så høyt som den brede flaten ved samme bredde | low | **under «Åpent»:** bare målt ved 390 og 320 px |
| ECH4 | Linja sier bare ukedagen for børsdagen før, også når den er mer enn 6 dager før | low | **under «Åpent»** |
| ECH5 | «Børsdagen før» i linja er fra kursdatoene, men indeksen bruker kalenderen | low | **under «Åpent»:** de er like når kursene er komplette. Spesifikasjonen sier at indeksen står «–» når kalenderen ikke har en rad |
| BH7 | Den lyse grensen formateres som `faktor`, så «Hva fargene betyr» får 0,5 uten % | low | **under «Åpent»:** formatet er valgt så «fra 0,5 til under 2 %» har % én gang, men det bruker en type for et annet tall (regel 21) |
| BH10 | Veksten 1,02 har ingen måling i spesifikasjonen | low | **under «Åpent»:** valgt 26.10 i punkt d, og grunnen er ikke ført |
| BH3 | Tabellen og den skjulte teksten sier lavt, vanlig og høyt etter `volumfaktor` 1,5, mens arealet følger vekten | low | **avvist:** ordet følger interesse-sjekken, som har den samme grensen, og tabellen har tallet. Det beskriver ikke størrelsen |
| BH8 | Hjelpen har «3 ganger» og «halvparten» som tekst, ikke fra konstantene | low | **avvist:** `MINSTE_VEKT = 0.5` og `STOERSTE_VEKT = 3.0` er kilder til hjelpeteksten, så testen feiler når de endres |
| BH11 | Overskriften er om lag 19,3 px høy ved 320 px | low | **avvist:** 24 × 288/358 ≈ 19,3 px rommer symbolet på 14 px og teksten på 13 px med `line-height: 1` |
| BH12 | «(story 8.6)» i `test_demoproeven.py` om avgjørelsen 24.10 kl. 11:54 | low | **avvist:** avgjørelsen står under story 8.6 i `epics.md` |
| BH13 | `--opp-bakgrunn`, `--ned-bakgrunn` og `--ingen-bakgrunn` brukes ikke lenger på børsometeret | low | **avvist:** de brukes fortsatt i `stil.css` for andre sider |
| BH14 | Spesifikasjonen har ikke `updated` | low | **avvist:** ingen av de 83 spesifikasjonene i `implementation-artifacts` har feltet, og regel 4 gjelder `docs/` og `planning-artifacts` |

*Rettet 2026-10-26 (instruksjonen kl. 15:24), BH7:* den lyse grensen i «Hva fargene betyr» formateres som `grense` med én desimal, som de andre grensene i prosent, så teksten er «fra 0,5 % til under 2 %» (`test_hvert_tall_i_forklaringen_er_prosent`).

*Rettet 2026-10-26 (instruksjonen kl. 15:24), ECH4:* linja «Mål mot børsen» sier datoen i stedet for ukedagen når børsdagen før er mer enn 6 dager før dagen som vises (`vis_dagen_foer` og `UKEDAG_INNTIL` i `src/boersometer.py`, `test_datoen_naar_dagen_foer_er_mer_enn_6_dager_foer` og `test_datoen_i_linja_paa_siden`). ECH5 står fortsatt under «Åpent».

*Rettet 2026-10-26 (instruksjonen kl. 15:24), BH10:* grunnen til veksten 1,02, målt 26.10 på `6d92bbd`, ferdig før kl. 15:48 (`date` rett etter målingen), med 200 tilfeldige dager for 15 aksjer i 8 bransjer, volumforholdet lognormalt fordelt med sigma 0,5 og 0,8 (100 dager hver), og høyden sammenlignet med en vekst på 1,002, som er nær den laveste høyden kartet får plass i. Med 1,05 ble kartet 1,5 % (bred) og 2,3 % (smal) høyere i median og 4,7 og 7,9 % ved 95-persentilen. Med 1,02 ble det 0,6 og 0,9 % i median og 1,9 % ved 95-persentilen, på 1,8 ms per kart. Med 1,01 ble det 0,2 og 0,4 % i median, men på 3,3 ms, og 1,002 tok 15 ms. Høyden kartet får plass i, er ikke alltid stigende med høyden, så enkelte dager ble opptil 28,5 % høyere med 1,02 og 53,9 % med 1,05 enn med 1,002. 1,02 er valgt fordi kartet blir under 2 % høyere enn nødvendig for 95 av 100 dager, på under 2 ms. Grunnen står også ved `VEKST` i `src/boersometer.py`. Ingen test, fordi det er et valg og ikke en regel.

### Gjennomgangen av endringene etter `00bd6e1`

Gjennomgang 26.10 etter hele settet (3760 bestått, 24 hoppet over, 0 feilet, 15:49:34–15:55:08 på `3d9381c`), av diffen `0195544..3d9381c`, det vil si alt etter `00bd6e1` uten det som kom fra main, med Blind Hunter (BH, 14 funn), Edge Case Hunter (ECH, 5) og Verification Gap (VG, 4). Numrene gjelder denne runden. Rettet i `2e8a178`, `22f4035`, `114d7b2`, `94cded1` og `38cbb3e`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH3 | Grensene i `@media` var hele px med hull mellom 359 og 360 og mellom 1079 og 1080, så ingen regel gjaldt ved zoom med desimaler | medium | **rettet** i `2e8a178`: `@container` på kartet med `width >=` og `width <`, uten hull |
| ECH1 | Et vindu 360–376 px bredt med rullefelt har 311–327 px innhold, men teksten ble regnet ved 328 px | medium | **rettet** i `2e8a178`: `smal` gjelder når kartet er minst 328 px, som er et vindu fra 360 px uten rullefelt (svaret kl. 13:00, c) |
| BH2 | Spesifikasjonen sa at overskriften er 24 px ved den minste bredden, men den er 24 px ved `Flate.bredde` og om lag 19,3 px ved 288 px | medium | **rettet** i `22f4035`: spesifikasjonen og kommentaren sier det, og `test_overskriften_har_plass_til_linja` |
| BH4 | Testen for den åpne tabellen byttet ut `kart()`, så veien der kartet virkelig gir opp, var ikke prøvd | medium | **rettet** i `114d7b2`: `test_tabellen_er_aapen_naar_kartet_virkelig_gir_opp` med `MINSTE_RUTE` 1000 px |
| BH3, ECH2, VG3 | 1008 px forutsetter at `main` er 65rem med 16 px på hver side og rotskriften 16 px | low | **rettet** i `2e8a178`: `@container` måler kartet, så nivået følger den bredden kartet faktisk har |
| VG2 | Ingen test sjekket hele lista av elementer som skjules for hvert nivå | low | **rettet** i `2e8a178`: `test_tekstnivaaet_fra_360_og_1080_px` sjekker hver velger og grensene mot `Flate.tekst` |
| BH9 | `docs/hjelp.md` hadde fortsatt «fra 0,5 til under 2 %» etter BH7 | low | **rettet** i `94cded1`, med test |
| ECH4 | Den lyse grensen sto med én fast desimal, så 0,25 ville stått som 0,3 | low | **rettet** i `94cded1`: så mange desimaler som trengs, `test_grensen_staar_noeyaktig` |
| BH7, BH8 | Kommentaren ved `VEKST` nevnte ikke feltbredden, og det var uklart om målingen var gjort med `MINSTE_FELT` | low | **rettet** i `38cbb3e`: målingen er gjort på `6d92bbd`, etter `MINSTE_FELT` i `a7f16fd`, og kommentaren sier det |
| BH5, ECH5, VG4 | En bransje med flere aksjer der ingen har kurs, får bare navnet i overskriften, og ingen test viser den grenen | low | **under «Åpent»:** følger svaret kl. 13:00 (b), og tabellen har antallet |
| BH6 | `dagen_foer` til malen er nå tekst, ikke dato | low | **avvist:** malen bruker den ett sted (`grep` i `src/templates/`) |
| BH10 | Testen for rekkefølgen fanger bare første ord i bransjenavnet | low | **avvist:** alle de 13 navnene i `BRANSJER` er ett ord |
| BH11 | `bred` og `smal` er både flatenavn og klassenavn | low | **avvist:** `plass` og `nivaa` er to ordbøker, og testene sjekker alle fire klassene |
| BH12 | `id="bransje-N"` peker på en annen bransje fra dag til dag | low | **avvist:** id-en brukes bare av `aria-labelledby` på samme side |
| BH13 | Linje to i overskriften skjules med en fast `row-gap` i px | low | **avvist:** zoom skalerer px likt, og høyden og avstanden følger med |
| BH14 | Kommentarene om bildene sier «byte for byte det samme» uten bevis | low | **avvist:** bildene ble tatt på nytt og sammenlignet med `cmp` mot `docs/appen/` før hver commit, og `src/app.py` er blant `FILENE_BAK_AKSJESIDEN` |
| VG1 | Ingen test sjekker rekkefølgen ved lik vekt | low | **avvist:** `squarify` og `kart` bruker samme funksjon, `rekkefoelge` |

## Åpent

- **BH2, rekkefølgen i kartet (medium, ikke rettet):** fokuset følger §4-rekkefølgen i HTML-en, mens `squarify` legger den største ruta først. Gruppen avgjør om rekkefølgen skal endres.
  *Lukket 2026-10-26 (gruppens svar kl. 13:00, a):* i HTML-en står feltene og rutene i den rekkefølgen `squarify` legger dem, den største først og ved lik vekt i rekkefølgen i §4 (`rekkefoelge` i `src/boersometer.py`), på begge flatene. Tabellen under har fortsatt rekkefølgen i §4. Hjelpen sier at Tab følger kartet.
- **BH5:** høyden på den smale flaten mellom 390 og 760 px.
- **BH5, ECH5 og VG4 i gjennomgangen av endringene etter `00bd6e1`:** overskriften for en bransje med flere aksjer der ingen har kurs, har bare navnet (svaret kl. 13:00, b), og tabellen har antallet.
- **ECH4 og ECH5:** linja «Mål mot børsen» når børsdagen før er mer enn 6 dager før, eller ikke er den samme i kursene og kalenderen.
  *ECH4 lukket 2026-10-26:* rettet, se linja under triagen. ECH5 er fortsatt åpent.
- **BH7:** typen `faktor` for den lyse grensen i «Hva fargene betyr».
  *Lukket 2026-10-26:* rettet, se linja under triagen.
- **BH10:** grunnen til veksten 1,02.
  *Lukket 2026-10-26:* målt og ført, se linja under triagen.

## Det som ikke endres

- Ingen nye kall og ingen ny tabell. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` røres ikke, og demobaser lages bare i midlertidige mapper.
- Oversikten har hovedindeksen med søylene som før, og Min liste og aksjesiden er som før.
- Rammen følger svarene 23.10 kl. 09:24: gult ved 3 av 3 på siste børsdag også en annen dag og en dag uten vurdering, og mørk bare for siste børsdag. Alle ruter lenker til aksjesiden.
- «Velg dag», tabellen under og fotnoten om «ikke vurdert» står.
