---
title: 'Story 8.17a: periodevalget i oversikten, med søylene og indekslinja'
type: 'feature'
created: '2026-10-30'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'afd08c5'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/src/perioder.py'
  - '{project-root}/src/templates/_perioder.html'
  - '{project-root}/src/markedsoversikt.py'
  - '{project-root}/src/hovedindeks.py'
  - '{project-root}/src/app.py'
---

## Intent

Oversikten får periodevalget fra 8.16 over tabellen, og søylene under hovedindeksen og indekslinja følger samme periode og dag (story 8.17, første del). Min liste og børsometeret er 8.17b (gruppens svar 23.10 kl. 12:35, c). Storyen er «Ekstra» og flettes bare ferdig og grønt (svaret 19.10 kl. 14:48). Bygget 30.10 etter svaret 29.10 kl. 09:20, og stopper før flettingen.

## Slik er det i dag (slått opp 30.10 på `afd08c5`)

- `perioder.py` har kodene, knappene, `startdag` og `les_valg`. `les_valg` gir 6 mnd uten periode i adressen og ved feil, med en beskjed som sier «grafen viser 6 mnd».
- `_perioder.html` har makroen `periodevalg(knapper, valgt, adresse, dag, minst, maks, etikett, anker)`, med lenker og et skjema med `periode=velg` og `dag`.
- Oversikten (`_tabellsiden` i `app.py`) bygger radene med `bygg_oversikt`, der endringen er de to siste kursene (`endring_i_prosent`). Sortering står i adressen som `sorter` og `orden` (`side_adresse`).
- Søylene (`bygg_soeyler` i `hovedindeks.py`) bruker endringen for indeksens dato (`aksjeendring`), og linja indeksens endring for samme dag (`indeksendring`). `tre_av_tre` er symbolene med 3 av 3 på siste børsdag.
- `Oversiktsleser.vurdering(symbol, dato)` leser raden i `vurdering` for en dag uten å regne (8.16).

## Kontrollpunktene

- Siste børsdag er valgt når oversikten åpnes, og perioden og dagen står i adressen, også i lenkene som sorterer og i «Standard rekkefølge».
- For en periode er endringen `adjusted_close` på siste børsdag mot `adjusted_close` på startdagen fra `perioder.startdag`, regnet fra radens siste børsdag. Har serien ikke startdagen, regnes den fra første dag serien har etter den, og raden sier «fra» og datoen.
- Ved en periode gjelder sluttkursen, signalet, «Skilte seg ut», 2 av 3 og gult siste børsdag (svar a kl. 12:35).
- «Velg dag» viser sluttkursen og endringen den dagen og raden i `vurdering` for den, eller «– ikke vurdert», grunnen eller «– ikke børsdag». Signalet regnes aldri (AD-7).
- Gult står ved 3 av 3 på siste børsdag også med en periode og «Velg dag». 2 av 3 merkes bare når siden viser siste børsdag eller en periode (signalet er da siste børsdag), aldri for en valgt dag (designregler §3).
- Søylene og linja følger samme periode og dag, regnet med de samme funksjonene. Bransjesymbolet er gult ved 3 av 3 på siste børsdag, som før.
- **Ville feilet hvis:** «Velg dag» før vurderingene i demoen viste et signal, eller søylene viste dagens endring mens tabellen viste en uke.

## Valg som er gjort her

- **Oversikten åpner med siste børsdag**, ikke 6 mnd som kursgrafen (§2). `les_valg` får derfor en standardperiode og en tekst for hva siden viser ved en feil i adressen: «så oversikten viser siste børsdag». Kursgrafen er uendret.
- **Grensene for «Velg dag»:** første dag og siste dag blant seriene i oversikten, så `les_valg` avviser en dag fram i tid, etter siste kurs eller på eller før første kurs, som på aksjesiden.
- **Endringen for en periode** er ett tall per rad i kolonnen «Endring», som får perioden i kolonneraden. FR-102 og sorteringen på endring bruker tallet som vises.
- **«Velg dag» er én liste uten delene**, fordi «Skilte seg ut» gjelder siste børsdag (svar a). Rekkefølgen er FR-102 på dagens tall, og sortering ved klikk virker som før.
- **Gult ved «Velg dag»:** raden har streken i sterk oransje og teksten «3 av 3 siste børsdag» når aksjen fikk 3 av 3 siste børsdag. Pillen for dagen har ingen ring og ingen 2 av 3-merking.
- **Overskriften og indekstallet** over tabellen gjelder fortsatt siste børsdag. Søylene får en overskrift med perioden eller dagen.
- **Merkingen i Min liste** (stjernen) sender tilbake til oversikten med perioden og dagen.
- Ingen ny tabell, ingen migrasjon og ingen nettkall.

## Planen

1. a) Periodevalget, radene og adressen.
2. b) Søylene og linja, hjelpen, `docs/hjelp.md` og README-en.
3. c) Testene og mutantene.
4. Hele settet, gjennomgangen, triagen her og i PR-en.

## Mutantene

Tre, én om gangen med `-x`, med kopi før og sha256 mot HEAD etter: endringen fra dagen før i stedet for startdagen, søylene for siste børsdag ved en periode, og gult fra dagen som vises.

*Utfallet 30.10 kl. 00:52:19–00:52:25 på `635205e`, mot `tests/test_periodevalget_oversikten.py`:*

| Mutant | Endringen | Fanget av |
|---|---|---|
| M1 | `periodeendring` i `src/markedsoversikt.py` tar raden før slutt, ikke raden på startdagen | `test_1_uke_og_1_mnd_mot_den_haandregnede_serien` |
| M2 | `soeylene_for` i `src/hovedindeks.py` gir søylene for siste børsdag også ved en periode (`if True:`) | `test_soeylene_og_linja_foelger_perioden` |
| M3 | `bygg_rad_for_dag` i `src/markedsoversikt.py` gir gult fra 3 av 3 den dagen som vises | `test_dagen_viser_det_som_er_lagret` |

Etter hver mutant var fila lik kopien (samme sha256) og lik `HEAD`.

## Gjennomgangen

Gjennomgang 30.10 etter hele settet (3885 bestått, 24 hoppet over, 3 feilet, alle tre i porttestene for `start.ps1` som CI avgjør, 00:52:47–00:59:57 på `4e40a33`), av diffen `afd08c5..4e40a33`, med Blind Hunter (BH, 12 funn), Edge Case Hunter (ECH, 9) og Verification Gap (VG, 12). Dommen i tabellen er vår. Rettet i commiten etter `4e40a33`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1 | En rad uten sluttkurs ved «Velg dag» kunne gi feilside ved sortering på kurs | high | **avvist** etter oppslag: malen viser «–» (`rad.sluttkurs is not none`), og `sorter` legger rader uten verdi sist. `test_en_boersdag_foer_serien_begynner_og_sortering_paa_kurs` prøver det |
| BH2, ECH7 | En børsdag før serien begynner, sto som «ikke vurdert» | medium | **rettet**: «ingen kurs fra dagen», og dagen telles ikke i fotnoten |
| BH3, ECH5, VG4 | Hver rad fikk startdagen fra sin egen dato, mens linja over tabellen sa en annen | medium | **rettet**: én startdag fra sidens siste børsdag for alle radene (`med_perioden`) |
| BH4, ECH4 | Linja for indeksen kunne gjelde en kortere tid enn søylene uten at siden sa det | medium | **rettet**: ingen linje når indeksen begynner etter startdagen, `test_indeksen_som_begynner_etter_startdagen_gir_ingen_linje` |
| BH5, VG9 | «Velg dag» på siste børsdag merket samme dag på en annen måte enn den første knappen | medium | **rettet**: dagen er siste børsdag, `test_siste_boersdag_valgt_som_dag_er_siste_boersdag` |
| BH6 | Delene kunne blande siste børsdag inn i dagen | low | **avvist**: malen viser lista for dagen, og testen for rekkefølgen sjekker at delene ikke står |
| BH7, ECH8 | Knappene for perioden tar ikke med sorteringen | low | **står**: makroen fra 8.16 er lik på begge sidene (§2) |
| BH8, ECH6 | `min` i datofeltet stemte ikke med det `les_valg` godtar | low | **rettet**: dagen etter seriens første dag |
| BH9 | Kan ingen serie leses, sier beskjeden at serien begynner siste børsdag | low | **står** |
| BH10 | Ved en periode forsvant søylene uten forklaring | low | **rettet**: «Ingen søyler: …» også ved en periode |
| BH11 | Overskriften over søylene sier ikke «valgt dag» | low | **står**: datoen står, og linja over tabellen sier dagen |
| BH12, ECH3 | «fra» sto ved et hull i en lengre serie | low | **rettet**: «fra» bare når serien begynner etter startdagen |
| ECH1 | Utenfor børskalenderen (før 2026) kan startdagen være en stengt dag, og alle radene fikk «fra» | medium | **delvis rettet**: «fra» står ikke lenger. Startdagen følger regelen fra 8.16 (første hverdag utenfor kalenderen), også i kursgrafen, så linja over tabellen kan nevne en stengt dag. Spørsmål til gruppen («Åpent») |
| ECH2 | I år på årets første børsdag ga «–» | medium | **rettet**: 0,00 %, `test_hull_i_en_lengre_serie_og_i_aar_paa_aarets_foerste_dag` |
| ECH9 | «I år» med stor I midt i en setning | low | **rettet**: navnet fra `OVERSKRIFT` («i år», «1 måned») |
| VG1 | 390 px var bare prøvd som tekst i stilarket | high | **prøvd for hånd**: oversikten i en iframe på 390 px i Edge uten vindu, siste børsdag, 1 uke, «Velg dag» og I år sortert: `scrollWidth` 390, og bare tabellen er bredere, i sin egen boks som før. Ingen test i settet åpner en nettleser. Står i «Åpent» |
| VG2 | Skjermleseren: beskjeden, setningen for søylene og perioden i kolonneraden var ikke prøvd | medium | **rettet** i testene |
| VG3 | Rekkefølgen for en valgt dag var ikke prøvd | medium | **rettet**: `test_dagen_er_en_liste_i_fr_102_rekkefoelgen` |
| VG5 | Søylene bruker indeksens siste dato, tabellen sidens | medium | **står**: som 2.9b, og overskriften over søylene sier fra og til. Spørsmål til gruppen («Åpent») |
| VG6 | Sluttkursen for en valgt dag var ikke prøvd mot den justerte | low | **rettet**: 105 mot 100 onsdag 07.10 |
| VG7 | Fargen på linja ved en periode var ikke prøvd | low | **rettet** |
| VG8 | Fotnoten for en valgt dag var ikke prøvd | low | **rettet** |
| VG10 | Kanter uten test | low | **delvis rettet**: «Ingen søyler» en lørdag og en dag som ikke er en dato i adressen tilbake |
| VG11 | Svake påstander | low | **rettet** |
| VG12 | Testen for lenkene godtok dag uten «Velg dag» | low | **rettet** |

Hele settet etter rettingene, på samme kode før commiten: 3888 bestått, 24 hoppet over og 6 feilet, alle i porttestene for `start.ps1`, 01:10:19–01:17:19.

Mutantene etter rettingene, 30.10 kl. 01:10:03–01:10:13: M1, M2 og M3 ble fanget av de samme testene, og hver fil var lik kopien etterpå.

## Åpent

- **ECH1 (spørsmål til gruppen):** utenfor børskalenderen (`DEKKEDE_AAR`, bare 2026) er startdagen første hverdag, så 1 år eller 3 mnd tidlig i 2026 kan starte på en stengt dag i 2025, som 26.12.2025. Endringen regnes riktig fra første kurs etter den, men linja over tabellen nevner den stengte dagen. Det gjelder også kursgrafen (8.16). Skal kalenderen dekke 2025?
- **VG5 (spørsmål til gruppen):** søylene og linja bruker indeksens siste dato, som i 2.9b, og tabellen sidens siste børsdag. Er indeksen en dag foran eller bak, gjelder de ulike dager, og overskriften over søylene sier fra og til. Skal søylene følge tabellens dag ved en periode?
- **VG1:** 390 px er prøvd for hånd i Edge, ikke i en test.
- BH7, BH9 og BH11 står.
