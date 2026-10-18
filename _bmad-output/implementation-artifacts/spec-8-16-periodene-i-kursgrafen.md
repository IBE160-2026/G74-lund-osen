---
title: 'Story 8.16: regelen for startdagen, og periodene i kursgrafen'
type: 'feature'
created: '2026-10-18'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'efa3224'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
---

## Intent

**Problem:** Kursgrafen på aksjesiden har fast 6 måneder, regnet som 182 kalenderdager (`GRAFVINDU_DAGER`). FR-201 er rettet 08.10: grafen skal ha periodevalget i `designregler.md` §2, med de samme knappene som oversikten får i 8.17, og startdagen skal følge én skriftlig regel.

**Grunnlaget:** kontrollpunktene under story 8.16 i `epics.md`, FR-201 med tillegget 08.10, `designregler.md` §2, gruppens svar 18.10 kl. 21:46, 21:49 og 21:50 (alle åtte knappene; siste børsdag og «Velg dag» viser 6 mnd fram til dagen, med dagen merket, endringen den dagen og signalet som er lagret for den), og instruksjonen 18.10 kl. 22:54.

## Kontrollpunktene

- a) Regelen før koden: §2 i `designregler.md` får regelen for startdagen. 1 uke, 1, 3 og 6 mnd og 1 år regnes bakover fra siste dag i grafen etter kalenderen, og en dato måneden ikke har, blir månedens siste dag. Startdagen er første børsdag på eller etter den datoen. I år starter på årets første børsdag. Én funksjon i en ren modul gir startdagen for hver periode, med tester på faste datoer rundt helger, helligdager og nyttår.
- b) Grafen: knappene i én delmal som 8.17 skal bruke, i rekkefølgen og med navnene i §2, valgt knapp med `aria-current` og synlig fokus. Perioden står i adressen, og grafen åpner med 6 mnd. Kurslinja, MA50 og indekslinja følger perioden, og overskriften og merkene på aksen passer den. MA50 finnes fra første punkt for 6 mnd og kortere, og 1 år viser bare det serien har, og sier det. «Velg dag» er et datofelt i et skjema, uten skript fra nettet, og dagen står på knappen. Signalet for dagen er det som er lagret, ellers «– ikke vurdert», grunnen eller «– ikke børsdag», og det regnes aldri på nytt (AD-7). En feil i adressen gir 6 mnd og en kort beskjed, aldri en feilside. På 390 px bryter knappene linja, og siden ruller ikke sidelengs.
- c) Tekstene (regel 19): hjelpen til grafen, «Status» i README-en og `docs/hjelp.md` der grafen nevnes. Endres en fil bak bildet av oversikten, tas bildet på nytt slik feilmeldingen i testen sier.
- d) Testene, med «Ville feilet hvis»: to perioder som regner startdagen med hver sin regel; knappene og rekkefølgen; 6 mnd når siden åpnes; punktene fra startdagen for hver periode; indekslinja følger perioden; 1 år med kortere serie sier det; «Velg dag» for en dag uten vurdering viser «– ikke vurdert»; feil i adressen (ukjent periode, en dato fram i tid, tekst) gir 6 mnd og ingen feilside; 390 px. Mutanter én om gangen med `-x` og kopi før og sha256 mot HEAD etter: 1 mnd som 30 dager, «Velg dag» som regner signalet, indekslinja fast på 6 mnd, og en ukjent periode som gir en feil.

## Planen, én commit per punkt

1. a) Regelen i `designregler.md` §2, og `src/perioder.py` med `startdag()` og testene i `tests/test_perioder.py`.
2. b) Delmalen `_perioder.html`, adressen og valget i `perioder.py`, punktene fra startdagen i `aksjedetalj.py`, merkene på aksen og den merkede dagen i `graf.py`, lesingen av en lagret vurdering for en dag i porten `Oversiktsleser`, ruten og `aksje.html`.
3. c) Hjelpen til grafen, «Status» i README-en og `docs/hjelp.md`, og bildet av oversikten tatt på nytt, fordi den nye delmalen er en fil bak bildet.
4. d) Testene for grafen og siden.

## Avgjort i spesifikasjonen

- **Adressen:** `?periode=` med kodene `siste`, `1-uke`, `1-mnd`, `3-mnd`, `6-mnd`, `i-aar`, `1-aar` og `velg`, og `&dag=ÅÅÅÅ-MM-DD` for «Velg dag». En `dag` uten `periode` leses som «Velg dag».
- **Utenfor børskalenderen:** `boersdag.DEKKEDE_AAR` er bare 2026, så 1 år fra oktober 2026 havner i 2025. Der er startdagen første hverdag på eller etter datoen, og I år starter på første hverdag etter 1. januar. Grafen starter uansett på første dag serien har fra startdagen, og serien har bare børsdager.
- **«Velg dag»:** vurderingen leses med en ny lesemetode på porten `Oversiktsleser` (`vurdering(symbol, dato)`), som bare leser. Tilstanden og teksten kommer fra `les_tilstand`, som i oversikten. Signalet regnes aldri.
- **Merkene på aksen:** 1 uke har dagene, 1 mnd mandagene (første børsdag i hver uke), 3 og 6 mnd, I år, siste børsdag og «Velg dag» månedene, og 1 år månedene med navn på annenhver, så navnene får plass.

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Bildet tas fra en demobase i en midlertidig mappe.
- Ingen skript fra nettet. 8.17 bygges ikke her, men delmalen skal kunne brukes der.

## Avgjort underveis

- **Merkene for 1 mnd** står ved første dag serien har i hver uke, også i den første, avkortede uka. 09.09 er derfor en onsdag (gjennomgangen, BH5, ECH3 og VG9). Det endrer «mandagene» i linja over. Med flere enn 8 måneder får annenhver måned navn, så I år fra september tynnes som 1 år (BH4).
- **«Velg dag»** går fra andre dag i serien til siste dag i serien. Seriens første dag ville gitt en graf med ett punkt, og en dag etter siste rad en graf som slutter før dagen. Begge gir 6 mnd og en beskjed (BH1, ECH1, BH3, ECH2). En dag i serien uten kurs, som en lørdag, viser grafen fram til dagen før og sier det (BH2).
- **Testen for bildet** feilet på commiten for b (`30783c9`), fordi den nye delmalen er en fil bak bildet. Bildet ble tatt på nytt i c (`7e824e9`), kl. 23:08 (tidspunktet fila ble skrevet), med samme fremgangsmåte og høyde (1280 × 1573). Det fikk samme sha256 som det forrige, `777eee6eab84dfed…`, så PNG-fila er ikke endret, og bare `AVTRYKK_BAK_BILDET` er nytt (VG7).
- **«Status» i README-en:** punktet «Periodene i kursgrafen, og på forsiden …» under «Neste» er erstattet med «På forsiden periodevalget, børsometeret og KI-teksten om dagen», og periodene står på linja om grafen under «Ferdig», fordi «Ferdig» har 8 punkter, som er grensen. Det er den eneste linja som er tatt bort, og punkt c ber om den. `docs/hjelp.md` nevner ikke grafen og er ikke endret.

## Mutantene

Én om gangen med `-x` på `tests/test_perioder.py`, `tests/test_app.py` og `tests/test_oversiktsleser.py` (med `-k` for periodene), i en fersk klon med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver, og `git status` tom etter hver. P1–P4 er fra instruksjonen og ble fanget på `697f459` og på nytt på `25cbf36`. Q1–Q4 er for funnene med dom medium, fanget på `25cbf36`:
- P1, 1 mnd som 30 dager: `test_faste_datoer` (10.03 gir 09.02 i stedet for 10.02).
- P2, «Velg dag» som regner signalet med `vurder`: `test_velg_dag_uten_vurdering_viser_ikke_vurdert`.
- P3, indekslinja fast på 6 mnd: `test_indekslinja_foelger_perioden[i-aar]`.
- P4, en ukjent periode som gir en feil: `test_feil_i_adressen_gir_6_mnd_og_en_kort_beskjed`.
- Q1, en dag etter siste dag i serien godtas (BH1): `test_en_dag_etter_siste_dag_i_serien_gir_6_mnd`.
- Q2, seriens første dag godtas (BH3): `test_seriens_foerste_dag_gir_6_mnd`.
- Q3, I år tynnes ikke (BH4): `test_merkene_paa_aksen_passer_perioden[i-aar]`.
- Q4, «I dag» og «I går» byttet om (VG2): `test_i_dag_i_gaar_eller_ukedagen`.

## Gjennomgangen

Gjennomgang 18.10 på diffen `7ae3e3a..697f459`, uten bildet. Linsene var Blind Hunter (BH, 18 funn, bare diffen), Edge Case Hunter (ECH, 7 funn og en liste over det som holdt, prøvd med test_client mot en demobase i en midlertidig mappe) og Verification Gap (VG, 11). Ingen av dem kjørte hele testsettet, en server eller et nettkall. Seks rader har dom medium, og alle er rettet i `25cbf36`, unntatt VG1, som er rettet her. Edge Case Hunter fant ingen vei til en feilside.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH1 | «Velg dag» etter siste rad ga «fram til 15.10» og en graf som sluttet 09.10 | medium | patch: 6 mnd og beskjed, og `max` er siste dag i serien. Q1 |
| BH3, ECH2 | Seriens første dag ga en graf med ett punkt | medium | patch: 6 mnd og beskjed, og `min` er andre dag. Q2 |
| BH4 | I år hadde navn på alle 10 månedene | low–medium | patch: annenhver over 8 måneder. Q3 |
| VG1 | Mutantene var ikke dokumentert | medium | patch: over |
| VG2 | «I dag» og «I går» var ikke testet | medium | patch: `TestDenFoersteKnappen`. Q4 |
| VG3 | «I dag:» i §2 sa at grafen har faste seks måneder | medium | patch: en datert linje under. Linja står, fordi ingen linje fjernes |
| BH2 | En lørdag ga «fram til lørdag 03.10» uten forklaring | low | patch: «03.10 har ingen kurs, så grafen slutter 02.10.» |
| BH5, ECH3, VG9 | «mandagene» for 1 mnd stemte ikke | low | patch: kommentaren og «Avgjort underveis» |
| BH9 | `\d` godtok andre sifre | low | patch: `[0-9]`, og en test |
| BH10 | `idag()` ble lest flere ganger i samme svar | low | patch: én gang i ruten |
| BH11 | Det merkede punktet ble lest fra koordinatstrengen | low | patch: regnet fra indeksen |
| BH12 | Klippingen i `bygg_punkter` var skjør | low | patch: én lengde for alle tre |
| VG4 | Sju tester manglet «Ville feilet hvis» | low | patch |
| VG7 | At bildet var likt, var ikke vist | low | patch: tid og sha256 over |
| VG11 | Lesemetoden var ikke testet mot adapteren | low | patch: `TestVurderingForEnDag` |
| BH13 | Knappen for «Velg dag» heter bare datoen når den er valgt | low | utsatt til 8.17, som bruker delmalen i flere sider |
| BH6 | «Kursserien begynner» kan stå når startdagen utenfor kalenderen er en helligdag | low | avvist: bare utenfor `DEKKEDE_AAR`, og regelen i §2 sier det |
| BH7 | Datoene mangler år over nyttår | low | avvist: `dato` viser året når det er et annet enn i år (designregler §4) |
| BH8, ECH6, VG10 | `dag` i adressen overstyrer `periode` uten beskjed | low | avvist: skjemaet sender alltid `periode=velg`, og en dag er et valg av «Velg dag», som spesifikasjonen sier |
| BH14 | Datofeltet er tomt for siste børsdag | low | avvist: dagen står i overskriften og på den første knappen |
| BH15 | Hjelpen nevner ikke 7 dager og månedens siste dag | low | avvist: høyst tre setninger per hjelpetekst, og regelen står i §2 |
| BH16, VG5 | Testene sammenligner med `startdag`, og 390 px er ikke målt i en nettleser | low | avvist: regelen er testet med faste datoer i `test_perioder.py`, og 390 px testes som før, i stilen |
| BH17 | Andre implementasjoner av porten | low | avvist: bare `SqliteOversiktsleser` implementerer den, og spørringen er den samme som i `SqliteVurderingslager.les` |
| BH18 | «– None» om `les_tilstand` ga tekst None | low | avvist: teksten er None bare for en vurdering, og da vises signalet |
| ECH4 | `startdag` kan gi en stengt dag utenfor kalenderen | low | avvist: står i §2, og 2027 legges inn når Euronext publiserer dagene |
| ECH5 | Mellomrom i `dag` vises ikke i beskjeden | low | avvist: verdien kunne ikke leses slik den sto |
| ECH7 | Den første knappen heter ukedagen også når siste rad er over en uke gammel | low | avvist: følger §2 slik den står |
| VG6 | MA50 for «Velg dag» tidlig i serien er ikke testet | low | avvist: snittet begynner der serien har 50 dager (FR-406), og «Velg dag» er 6 mnd |
| VG8 | «Ferdig» i README-en før flettingen | low | avvist: blir riktig når PR-en flettes, som i README-PR-ene før |
