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
| ECH1, svaret | *Avgjort 2026-10-30 kl. 10:45 (gruppens svar, a):* linja over tabellen, og linja i kursgrafen fra 8.16, sier dagen den første kursen i perioden er fra, ikke en beregnet startdag, så ingen stengt dag nevnes. Børskalenderen får ikke 2025 | – | **rettet** i `16c68b1`: `perioder.foerste_kursdag` gir dagen for linja, «fra» i radene og søylene. Kursgrafen viste allerede første kurs (`graf.forste_dato`), og en test låser det. `TestFoersteKursen` |
| ECH2 | I år på årets første børsdag ga «–» | medium | **rettet**: 0,00 %, `test_hull_i_en_lengre_serie_og_i_aar_paa_aarets_foerste_dag` |
| ECH9 | «I år» med stor I midt i en setning | low | **rettet**: navnet fra `OVERSKRIFT` («i år», «1 måned») |
| VG1 | 390 px var bare prøvd som tekst i stilarket | high | **prøvd for hånd**: oversikten i en iframe på 390 px i Edge uten vindu, siste børsdag, 1 uke, «Velg dag» og I år sortert: `scrollWidth` 390, og bare tabellen er bredere, i sin egen boks som før. Ingen test i settet åpner en nettleser. Står i «Åpent» |
| VG1, svaret | *Avgjort 2026-10-30 kl. 10:45 (gruppens svar, c):* en automatisk test for 390 px | – | **rettet** i `9c8bda2`: `TestSmalSkjerm` åpner oversikten i Edge eller Chrome uten vindu på 390 px, med hjelperen fra `test_hjelpefeltet.py`, og hopper over uten nettleser, men ikke i CI |
| VG2 | Skjermleseren: beskjeden, setningen for søylene og perioden i kolonneraden var ikke prøvd | medium | **rettet** i testene |
| VG3 | Rekkefølgen for en valgt dag var ikke prøvd | medium | **rettet**: `test_dagen_er_en_liste_i_fr_102_rekkefoelgen` |
| VG5 | Søylene bruker indeksens siste dato, tabellen sidens | medium | **står**: som 2.9b, og overskriften over søylene sier fra og til. Spørsmål til gruppen («Åpent») |
| VG5, svaret | *Avgjort 2026-10-30 kl. 10:45 (gruppens svar, b):* søylene og indekslinja følger tabellens dag. Mangler indeksen kurs den dagen, står det over søylene | – | **rettet** i `3aa2d80`: `soeylene_for` får tabellens dag (`slutt`), og `TestTabellensDag` prøver en indeks én dag foran og én dag bak. `test_soeylene_er_for_indeksens_dato` fra 2.9b er skrevet om til `test_soeylene_er_for_tabellens_dag` |
| VG6 | Sluttkursen for en valgt dag var ikke prøvd mot den justerte | low | **rettet**: 105 mot 100 onsdag 07.10 |
| VG7 | Fargen på linja ved en periode var ikke prøvd | low | **rettet** |
| VG8 | Fotnoten for en valgt dag var ikke prøvd | low | **rettet** |
| VG10 | Kanter uten test | low | **delvis rettet**: «Ingen søyler» en lørdag og en dag som ikke er en dato i adressen tilbake |
| VG11 | Svake påstander | low | **rettet** |
| VG12 | Testen for lenkene godtok dag uten «Velg dag» | low | **rettet** |

Hele settet etter rettingene, på samme kode før commiten: 3888 bestått, 24 hoppet over og 6 feilet, alle i porttestene for `start.ps1`, 01:10:19–01:17:19.

Mutantene etter rettingene, 30.10 kl. 01:10:03–01:10:13: M1, M2 og M3 ble fanget av de samme testene, og hver fil var lik kopien etterpå.

*Lagt til 2026-10-30 (svaret kl. 10:45, VG5):* M4, søylene ved indeksens dag (`siste = serie[-1].dato` i `soeylene_for` i `src/hovedindeks.py`, ikke tabellens dag), kjørt med `-x` på `3aa2d80` kl. 11:17:35–11:17:42 mot `tests/test_periodevalget_oversikten.py` og `tests/test_app.py`: fanget av `test_indeksen_en_dag_foran_tabellen`. Fila var lik kopien etterpå (sha256 `d80c1371…`) og lik `HEAD` (`git diff --quiet`).

## Gjennomgangen 30.10 etter svaret kl. 10:45

Gjennomgang 30.10 etter hele settet (3897 bestått, 24 hoppet over, 7 feilet, alle sju i porttestene for `start.ps1` som CI avgjør, 11:31:26–11:40:22 på `c4cc3cd`), av diffen `d355cee..c4cc3cd` uten flettingen av main, med Blind Hunter (BH, 14 funn), Edge Case Hunter (ECH, 6) og Verification Gap (VG, 1). Numrene gjelder denne runden. Dommen i tabellen er vår. Rettet i commiten etter `c4cc3cd`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH2 | Indekstallet og endringen over søylene gjelder indeksens siste dato, mens linja gjelder tabellens dag, så to ulike endringer kan stå i samme del | medium | **står**: «Overskriften og indekstallet over tabellen gjelder fortsatt siste børsdag» (valg i spesifikasjonen), og svaret VG5 gjelder søylene og linja. Indeksens dato står ved tallet når den er en annen enn tabellens (`indeksdato`). Spørsmål til gruppen («Åpent») |
| BH1, ECH2, svaret | *Avgjort 2026-10-30 kl. 12:21 (gruppens svar, e):* hele delen med hovedindeksen følger tabellens dag, også tallet over søylene. Mangler indeksen kurs den dagen, står det der tallet ellers står | – | **rettet** i `a086857`: `bygg_hovedindeks` regner verdien, endringen og «x av N» for tabellens dag eller dagen fra «Velg dag», og `TestTalletOverSoeylene` prøver indeksen én dag foran og bak og en valgt dag. `test_en_indeks_en_dag_bak_tabellen_har_datoen_ved_verdien` fra 2.9 er skrevet om til `test_en_indeks_en_dag_bak_tabellen_sier_at_kursen_mangler` |
| BH2 | Linja kunne tegnes ved en periode når indeksen mangler tabellens dag | medium | **avvist** etter oppslag: `periodeendring` gir None når serien ikke har slutt (`paa_slutt is None`), så det er ingen linje |
| BH3, ECH1 | Siden og søylene regnet første kursdag hver for seg, fra ulike serier | medium | **rettet**: dagen fra `_periodestart` sendes til `soeylene_for` (`start`) |
| BH4 | Mangler alle aksjene kurs på en åpen startdag, begynner perioden senere uten at radene sier det | low | **avvist**: svaret a sier dagen den første kursen er fra, og linja over tabellen sier datoen |
| BH5 | En kurs på en stengt dag gjør den dagen til start | low | **avvist**: har en aksje kurs den dagen, er det den første kursen, og den er ingen stengt dag uten kurs |
| BH6, ECH5 | Reserven `or start` i `_periodestart` kan nevne en stengt dag | low | **står**: siste børsdag er alltid i perioden og har kurs, så reserven brukes bare når ingen serie kunne leses |
| BH7 | «så søylene står uten stiplet linje» kunne stå uten søyler | low | **rettet**: «så det er ingen stiplet linje» |
| BH8 | En vanlig rullefelt i iframen gjør 390 til 375 | low | **avvist**: `_kjoer` bruker `--hide-scrollbars` og krever at bredden er 390, ellers feiler den med egen melding |
| BH9, ECH6 | Skjulte elementer eller elementer klippet av en forelder kan gi falsk feil | low | **står**: ingen i dag. `.tabellboks` selv måles, bare innholdet hoppes over |
| BH10 | I CI uten nettleser feiler testen uten klar melding | low | **avvist**: `_kjoer` har `assert NETTLESER, "… og CI krever det"` |
| BH11 | Modulteksten i `hovedindeks.py` sa startdagen | low | **rettet** |
| BH12 | Hjelpen ved «?» for søylene sa ikke at indeksen kan mangle kurs | low | **rettet**: «borte når indeksen ikke har en kurs eller endring den dagen», innenfor tre setninger (`test_hjelpetekster.py`) |
| BH13 | FR-105 i `prd.md` sier indeksens dato | low | **står**: spørsmål til gruppen («Åpent», VG5) |
| BH13, svaret | *Avgjort 2026-10-30 kl. 12:21 (gruppens svar, f):* «forstår ikke hva blir best i forhold til alle sidene, må være samkjørt», ført som én dag per side, der alt på siden, også indeksen, gjelder den dagen | – | **rettet** i `37b7ed6`: Rettet-linja under FR-105 i `prd.md`, med `test_fr_105_har_rettet_linja_om_en_dag_per_side`. Gruppen ser over tolkningen før flettingen |
| BH14, VG1 | «Velg dag» på en dag indeksen ikke har, var ikke prøvd | medium | **rettet**: `test_en_valgt_dag_indeksen_ikke_har`. En periode der indeksen begynner etter starten og slutter før tabellens dag, er ikke prøvd for seg |
| ECH3 | Overskriften over søylene sa datoen når indeksen var én dag bak, og indeksens dato når den var én dag foran | medium | **rettet**: overskriften sammenligner med tabellens dag (`dato`), og `test_soeylene_er_for_tabellens_dag` og `test_indeksen_en_dag_foran_tabellen` sier «Dagens endring per aksje» |
| ECH4 | Indeksen med et hull på startdagen gir en linje fra en senere dag | low | **avvist**: et hull i en lengre serie er ikke en kortere serie (ECH3 i første runde), som i tabellen |

Bildene av oversikten og aksjesiden er tatt på nytt med høydene 1690 og 1894, målt på nytt, og er byte for byte de samme. Avtrykkene i `tests/test_docker.py` er oppdatert.

Hele settet etter rettingene, på samme kode før commiten: 3898 bestått, 24 hoppet over og 7 feilet, alle sju i porttestene for `start.ps1`, 11:49:31–11:58:43.

*Lagt til 2026-10-30 (svaret kl. 12:21, e):* M5, tallet ved indeksens siste dag (`vist = serie[-1].dato` i `bygg_hovedindeks` i `src/hovedindeks.py`), kjørt med `-x` på `a086857` kl. 13:25:44–13:25:51 mot `tests/test_periodevalget_oversikten.py` og `tests/test_app.py`: fanget av `test_indeksen_en_dag_foran_tabellen` i `TestTalletOverSoeylene`. Fila var lik kopien etterpå (sha256 `836b5ab6…`) og lik `HEAD`.

*Lagt til 2026-10-30 (svaret kl. 12:21, f), slått opp uten endring:* børsometeret har én dag for hele siden, siste børsdag eller dagen fra «Velg dag», og indekstallet i «Mål mot børsen» er for samme dag (`_indeksen_for_dagen(dagen)`). Min liste har ingen hovedindeks og ikke periodevalget ennå (8.17b). Avvik fra regelen: i oversikten og Min liste viser en rad med eldre data enn de andre sin egen siste dag (story 1.4c), og ved en periode regnes endringen til radens egen siste børsdag (`med_perioden`). Aksjesiden følger aksjens egen siste dag eller dagen fra «Velg dag», som kan være en annen enn siste børsdag i oversikten, og den stiplede indekslinja i grafen kan slutte før grafen («Indeksen går bare til …»). Grafen og «Signalet dag for dag» viser flere dager med vilje.

## Gjennomgangen 30.10 etter svaret kl. 12:21

Gjennomgang 30.10 av diffen `4cc2b98..e88d449` (etter flettingen av main med 3.5h), med Blind Hunter (BH, 15 funn), Edge Case Hunter (ECH, 7) og Verification Gap (VG, 3). Hele settet før: 3904 bestått, 24 hoppet over, 7 feilet, alle i porttestene, 13:26:45–13:35:31 på samme kode som `37b7ed6`. Numrene gjelder denne runden. Dommen er vår. Rettet i commiten etter `e88d449`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| ECH1, ECH2 | `dato` i malen er den eldste dagen blant radene (`sidens_dato`), så med en rad med eldre data sto datoen ved tallet og over søylene på siste børsdag | medium | **rettet**: malen sammenligner med `siste_dag` |
| BH4 | FR-104 sa fortsatt indeksens siste børsdag for verdien og «x av N» | medium | **rettet**: Rettet-linje under FR-104, som under FR-105, med `test_fr_104_har_rettet_linja_om_tabellens_dag`. Gruppen ser over tolkningen |
| BH1, VG1 | «x av N» ved «Velg dag» var ikke prøvd | medium | **rettet** i testen: «0 av 3» for 07.10, ikke «3 av 3» for 09.10. `sammenlign` bruker dagen (`aksjeendring(serie, dag)`), slått opp |
| VG2 | Tallet over søylene for en valgt dag indeksen ikke har, var ikke prøvd | low | **rettet** i `test_en_valgt_dag_indeksen_ikke_har` |
| VG3 | Enhetstesten i `test_hovedindeks.py` sier indeksens egen dato | low | **rettet**: ny enhetstest med `slutt`. Den gamle gjelder bare uten `slutt`, som appen ikke bruker |
| BH6 | `if paa_dagen` i stedet for `is not None` | low | **rettet** |
| BH11 | Testen for indeksen én dag bak gjaldt bare 1 uke | low | **rettet**: også `/`, og beskjeden over søylene |
| BH12, ECH5 | `_indekstallet` ga `AttributeError` uten linja | low | **rettet** |
| BH14, ECH6 | Hjelpen kunne leses som at tallet følger perioden | low | **rettet** i `docs/hjelp.md`: tallet er alltid endringen den dagen |
| ECH7 | Kommentaren i malen sa indeksens dato | low | **rettet** |
| BH2, ECH3 | «Velg dag» på en lørdag sier «Indeksen har ingen kurs», mens tabellen sier «ikke børsdag» | low | **står**: det er sant, og søylene sier «ingen aksje har kurs» |
| BH3 | `verdi` kan være None hos andre som leser den | low | **avvist** etter oppslag: bare `_hovedindeks.html` bruker den |
| BH5 | Endringen kan gå over et hull | low | **avvist**: `indeksendring` krever forrige børsdag etter kalenderen |
| BH7 | Datoen ved tallet står bare ved «Velg dag» | low | **står**: den sier dagen tabellen viser |
| BH8 | Beskjeden står to ganger når indeksen mangler kurs | low | **står**: svaret e sier der tallet står, og søylene sier hvorfor linja mangler |
| BH9 | Uten `slutt` gjelder indeksens dato | low | **avvist**: bare oversikten kaller `bygg_hovedindeks`, med `slutt` |
| BH10 | Nyere indekstall skjules når indeksen er foran | low | **står**: én dag per side (f) |
| BH13 | Testen låser ordlyden i tolkningen gruppen skal se over | low | **står**: rettes sammen med linja hvis gruppen vil |
| BH15 | Ingenting viser at bildene er de samme | low | **avvist**: `git status` var ren etter at bildene ble tatt på nytt, med høydene målt til 1690 og 1894 |
| ECH4 | En usortert serie | low | **avvist**: lageret gir seriene sortert på dato |

## Åpent

- **ECH1 (spørsmål til gruppen):** utenfor børskalenderen (`DEKKEDE_AAR`, bare 2026) er startdagen første hverdag, så 1 år eller 3 mnd tidlig i 2026 kan starte på en stengt dag i 2025, som 26.12.2025. Endringen regnes riktig fra første kurs etter den, men linja over tabellen nevner den stengte dagen. Det gjelder også kursgrafen (8.16). Skal kalenderen dekke 2025?
  - *Avgjort 2026-10-30 kl. 10:45 (gruppens svar):* linja over tabellen og i kursgrafen sier dagen den første kursen i perioden er fra, og kalenderen får ikke 2025. Rettet i `16c68b1`.
- **VG5 (spørsmål til gruppen):** søylene og linja bruker indeksens siste dato, som i 2.9b, og tabellen sidens siste børsdag. Er indeksen en dag foran eller bak, gjelder de ulike dager, og overskriften over søylene sier fra og til. Skal søylene følge tabellens dag ved en periode?
  - *Avgjort 2026-10-30 kl. 10:45 (gruppens svar):* søylene og linja følger tabellens dag, og mangler indeksen kurs den dagen, står det over søylene. Rettet i `3aa2d80`. FR-105 i `prd.md` sier fortsatt «En aksje uten kurs for indeksens dato får ingen søyle». PRD-en er ikke endret, fordi instruksjonen 30.10 kl. 10:55 bare førte svaret i `epics.md`. Spørsmål til gruppen: skal FR-105 få en Rettet-linje?
  - *Avgjort 2026-10-30 kl. 12:21 (gruppens svar, f):* FR-105 har fått en Rettet-linje om én dag per side (`37b7ed6`). Gruppen ser over tolkningen før flettingen.
- **VG1:** 390 px er prøvd for hånd i Edge, ikke i en test.
  - *Avgjort 2026-10-30 kl. 10:45 (gruppens svar):* en automatisk test. `TestSmalSkjerm` i `9c8bda2`.
- BH7, BH9 og BH11 står.
- **BH1 og ECH2 i runden 30.10 (spørsmål til gruppen):** indekstallet og endringen over søylene gjelder indeksens siste dato, og linja tabellens dag. Skal tallet også følge tabellens dag?
  - *Avgjort 2026-10-30 kl. 12:21 (gruppens svar, e):* hele delen følger tabellens dag, også tallet. Rettet i `a086857`.
