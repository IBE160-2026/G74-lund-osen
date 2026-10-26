---
title: 'Story 8.6b: børsometeret som tavla'
type: 'feature'
created: '2026-10-26'
status: 'in-review'
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
- **Overskriften i feltet** er 24 px høy ved den minste bredden, med symbolet, navnet, snittet og antallet, og kuttes med «…» når feltet er smalt. Tabellen under har de samme tallene.

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter: grensen 0,5 flyttet til 1, og arealet uten vekten.

*Utfallet 26.10 på `4af6efa`:* begge ble fanget, grensen av `test_hvert_trinn_ved_grensene[0.4951-lys-opp]` og arealet av `test_arealet_foelger_volumforholdet_i_tabellen`. Fila var lik HEAD etterpå.

*Utfallet 26.10 kl. 09:25 på `6f5815b`, etter rettelsene i kartet fra gjennomgangen:* begge ble fanget av de samme testene. Arealet uten vekten er `squarify([1.0 for r in bransje.ruter], …)` i `_legg_ut`. Fila var lik HEAD etterpå, med samme sha256 som `git show HEAD:src/boersometer.py` med CRLF.

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

## Åpent

- **BH2, rekkefølgen i kartet (medium, ikke rettet):** fokuset følger §4-rekkefølgen i HTML-en, mens `squarify` legger den største ruta først. Gruppen avgjør om rekkefølgen skal endres.
  *Lukket 2026-10-26 (gruppens svar kl. 13:00, a):* i HTML-en står feltene og rutene i den rekkefølgen `squarify` legger dem, den største først og ved lik vekt i rekkefølgen i §4 (`rekkefoelge` i `src/boersometer.py`), på begge flatene. Tabellen under har fortsatt rekkefølgen i §4. Hjelpen sier at Tab følger kartet.
- **BH5:** høyden på den smale flaten mellom 390 og 760 px.
- **ECH4 og ECH5:** linja «Mål mot børsen» når børsdagen før er mer enn 6 dager før, eller ikke er den samme i kursene og kalenderen.
- **BH7:** typen `faktor` for den lyse grensen i «Hva fargene betyr».
- **BH10:** grunnen til veksten 1,02.

## Det som ikke endres

- Ingen nye kall og ingen ny tabell. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` røres ikke, og demobaser lages bare i midlertidige mapper.
- Oversikten har hovedindeksen med søylene som før, og Min liste og aksjesiden er som før.
- Rammen følger svarene 23.10 kl. 09:24: gult ved 3 av 3 på siste børsdag også en annen dag og en dag uten vurdering, og mørk bare for siste børsdag. Alle ruter lenker til aksjesiden.
- «Velg dag», tabellen under og fotnoten om «ikke vurdert» står.
