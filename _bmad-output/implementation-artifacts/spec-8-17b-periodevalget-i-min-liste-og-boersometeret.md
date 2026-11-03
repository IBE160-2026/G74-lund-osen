---
title: 'Story 8.17b: periodevalget i Min liste («Sammenlign med») og i børsometeret'
type: 'feature'
created: '2026-11-03'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'dc8a5b0'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-17a-periodevalget-i-oversikten.md'
  - '{project-root}/src/perioder.py'
  - '{project-root}/src/markedsoversikt.py'
  - '{project-root}/src/boersometer.py'
  - '{project-root}/src/app.py'
---

## Intent

Min liste får periodevalget som «Sammenlign med», og børsometeret får samme periodevalg (story 8.17, andre del, gruppens svar 23.10 kl. 12:35, c). Bygget 03.11 etter avgjørelsen kl. 01:06 og instruksjonen kl. 17:42, og stopper før flettingen. Storyen er «Ekstra» og flettes bare ferdig og grønt (svaret 19.10 kl. 14:48).

## Slik er det i dag (slått opp 03.11 på `dc8a5b0`)

- **8.17a** (`spec-8-17a-periodevalget-i-oversikten.md`, flettet i `b2e8b2c`): oversikten har periodevalget fra `_perioder.html`, med siste børsdag valgt når siden åpnes, og perioden og dagen i adressen (`periodeledd`, `side_adresse`). En periode regnes med `periodeendring` fra dagen den første kursen i perioden er fra (`_periodestart`, `foerste_kursdag`), og «Velg dag» med `bygg_rad_for_dag`, som leser vurderingen og aldri regner den (AD-7).
- **8.3** (`spec-8-3-min-liste.md`): Min liste er samme tabell som oversikten (`_tabellsiden`), filtrert etter at den er delt eller sortert. I dag får Min liste ingen serier og ikke periodevalget (`serier = {} if i_lista`, `valg = None if i_lista`).
- **8.6 og 8.6b** (`spec-8-6-boersometeret.md`, `spec-8-6b-som-tavla.md`): børsometeret har sitt eget skjema for «Velg dag» (`velg-dag-boersometer`, `?dag=`), og en dag uten kurs gir børsdagen før. Fargen er endringen fra børsdagen før, størrelsen er volumforholdet i vurderingen (`vekt`), og rammen er signalet: gul ved 3 av 3 siste børsdag, mørk ved 2 av 3 bare siste børsdag.
- **Designforslaget:** tavla ligger i Claude og ikke i repoet. Utdraget (`designutdrag-2026-10-13.md`) har tavlene «Markedsoversikt», «Aksjedetalj – Equinor» og «Bransjer», ikke Min liste. «Sammenlign med» er derfor slik avgjørelsen 08.10 kl. 21:48 beskriver det: «hver rad viser tallene for siste børsdag øverst og dagen man sammenligner med under».
- **FR-101** (tillegget 08.10): periodevalget i §2, endringen over en periode av kursserien på `adjusted_close`, og signalet for en dag bare der det er lagret. **FR-107:** «Sammenlign med» er periodevalget i Min liste, og merket «var 1 mandag» skjules når det er på. 8.12 er ikke bygget, så det er ikke noe merke å skjule.
- **Unntaket under FR-104** (svaret 02.11 kl. 17:40): en aksje uten kurs for sidens dag viser sin egen siste dag i oversikten og i Min liste, og «Raden sier ikke hvilken dag den gjelder». Svaret 03.11 kl. 14:28 endrer det siste.

## Kontrollpunktene

- Min liste: «Sammenlign med» er periodevalget, siste børsdag valgt når siden åpnes, og perioden og dagen i adressen, også i «Alle / Min liste», sorteringen, «Standard rekkefølge» og merkingen.
- Hver rad viser siste børsdag øverst som før. Ved en periode eller en valgt dag står en linje under med dagen man sammenligner med: datoen, sluttkursen den dagen, endringen derfra til radens siste børsdag på `adjusted_close` (`periodeendring`, som i 8.17a), og vurderingen som er lagret for dagen, eller «– ikke vurdert», grunnen eller «– ikke børsdag». Signalet regnes aldri (AD-7).
- Gult og 2 av 3 følger §3: øverste linje er siste børsdag og merkes som før. Linja under har styrken som tekst, uten pille og uten 2 av 3-merking.
- En rad med eldre dag enn sidens siste børsdag viser datoen sin, i oversikten og i Min liste (svaret 14:28), og unntaket under FR-104 får en Rettet-linje.
- Børsometeret: samme periodevalg. Ved en periode er rutene like store, fargen og snittet er endringen for perioden, hovedindeksen i «Mål mot børsen» er endringen for perioden, og siden sier at størrelsen gjelder én dag (23.10, b). Siste børsdag og «Velg dag» viser det samme som før.
- **Ville feilet hvis:** linja under var regnet fra dagen før startdagen, signalet var regnet på nytt for sammenligningsdagen, rutene var ulike ved en periode, eller raden viste sidens dato i stedet for sin egen.

## Valg som er gjort her

- **Linja under er dagen man sammenligner med, også for «Velg dag».** Endringen er fra den dagen til radens siste børsdag, både for en periode og for en valgt dag, så «Sammenlign med» betyr det samme for alle knappene. I oversikten viser «Velg dag» endringen den dagen; i Min liste er dagen sammenligningen. Spørsmål til gruppen («Åpent»).
- **Ved en periode** er dagen den første kursen i perioden er fra (`_periodestart`, svaret 30.10 kl. 10:45, a), lik for alle radene. Begynner aksjens serie senere, er linja fra seriens første dag, med «fra» som i 8.17a. **Ved «Velg dag»** er det dagen som er valgt; har aksjen ikke kurs den dagen, står «–» og «ingen kurs fra dagen», som i oversikten. «Velg dag» har ikke unntaket.
- **Rekkefølgen og delene** følger øverste linje, siste børsdag, som i oversikten uten periode. Sortering ved klikk sorterer på øverste linje.
- **Linja under er en egen rad** i tabellen (`tr.sammenligning`) under aksjens rad, med datoen i første celle, så tabellen fortsatt har fem kolonner (FR-101) og skjermleseren leser linja som en rad med dato.
- **Datoen ved en rad med eldre dag** står under navnet, «siste kurs» og datoen, i oversikten og Min liste, også når en periode er valgt. Ikke ved «Velg dag» i oversikten, der hver rad er dagen.
- **Børsometeret bruker makroen fra 8.16**, og skjemaet `velg-dag-boersometer` er borte. `?dag=` leses som før, så en dag uten kurs gir fortsatt børsdagen før. Perioden leses med `les_valg` uten dag.
- **Like store ruter:** `Rute.lik_stoerrelse` gir vekten 1 i kartet. Tabellen under viser fortsatt volumet mot vanlig for siste børsdag, og «Mål mot børsen» sier at størrelsen gjelder én dag.
- **Ingen ny tabell, ingen migrasjon og ingen nettkall.** KI-grunnlaget (`ki_grunnlag.py`) er ikke endret. Slått opp: jobben (`fetch_prices.py`) importerer `ki_tekst`, som importerer `ki_grunnlag`, som importerer `endring_i_prosent` fra `markedsoversikt.py` og `indeksendring` fra `hovedindeks.py`. `markedsoversikt.py` endres her, men ikke `endring_i_prosent`; PR-en sier hva som er endret i fila.

## Planen

1. a) Min liste: periodevalget, linja under, datoen ved en rad med eldre dag, og Rettet-linja under FR-104.
2. b) Børsometeret: periodevalget, like store ruter og teksten, hjelpen, `docs/hjelp.md` og README-en.
3. c) Testene og mutantene.
4. Hele settet, gjennomgangen, triagen her og i PR-en.

## Mutantene

Fire, én om gangen med `-x`, med kopi før og sha256 mot HEAD etter: linja under fra dagen før startdagen, signalet regnet på nytt for sammenligningsdagen, ulike ruter ved en periode, og sidens dato i stedet for radens.

## Utfallet av mutantene

*03.11 kl. 18:12:28–18:12:36 på `7844af6`, mot `tests/test_periodevalget_min_liste_boersometer.py`, én om gangen med `-x`:*

| Mutant | Endringen | Fanget av |
|---|---|---|
| M1 | `bygg_sammenligning` i `src/markedsoversikt.py` tar raden før startdagen som grunnlag | `test_1_uke_og_1_mnd_mot_den_haandregnede_serien` |
| M2 | `bygg_sammenligning` regner signalet for dagen med `signalberegning.vurder` i stedet for å lese det | `test_1_uke_og_1_mnd_mot_den_haandregnede_serien` («1 av 3» i stedet for «– ikke vurdert») |
| M3 | `vekt` i `src/boersometer.py` bryr seg ikke om `lik_stoerrelse` (`if False:`) | `test_like_store_ruter_ved_en_periode` |
| M4 | `egne_dager` i `src/markedsoversikt.py` gir sidens siste børsdag i stedet for radens dag | `test_raden_viser_datoen_sin_i_oversikten_og_min_liste` |

Etter hver mutant var fila lik kopien (sha256 `02aa7a6c…` for `markedsoversikt.py`, `0cb72f68…` for `boersometer.py`) og lik `HEAD` (`git diff --quiet`). Kjørt på nytt på `3c8fd27` etter rettingene kl. 18:26:11–18:26:21, med samme utfall.

## Gjennomgangen

Hele settet før gjennomgangen, alene, 03.11 kl. 18:12:56–18:19:59 på `7844af6`: 3929 bestått, 24 hoppet over og 6 feilet, alle seks blant porttestene for `start.ps1` som CI avgjør (svaret 29.10 kl. 21:02). Gjennomgang av diffen `dc8a5b0..7844af6` med Blind Hunter (BH, 17 funn), Edge Case Hunter (ECH, 7) og Verification Gap (VG, 4). Dommen er vår, etter oppslag i koden. Rettet i `3c8fd27`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| ECH1 | Indeksen for perioden i «Mål mot børsen» gjaldt en kortere tid når indeksen begynner etter starten | medium | **rettet**: «–», som indekslinja i oversikten (`utfall[1] is None`), `test_hovedindeksen_for_perioden_i_boersometeret` |
| BH11, VG1 | Indeksen for perioden var ikke prøvd | medium | **rettet**: +10,00 % for 1 uke mot 0,00 % for dagen, og «–» for 1 mnd |
| – | Funnet i bildene til PR-en: kolonneraden i Min liste sa «1 uke» eller dagen under «Endring», men øverste linje er siste børsdag | medium | **rettet**, `test_kolonneraden_i_min_liste_er_siste_boersdag` |
| ECH2, VG2 | Linja under og ruta for en kortere serie: «fra» var ikke prøvd i børsometeret, og linja under har ikke ordet «fra» | medium | **rettet** for børsometeret (`test_en_kortere_serie_i_boersometeret`). I Min liste **står** det: linja under viser datoen den gjelder, 05.10 for AKRBP, så ordet «fra» trengs ikke. Valget i spesifikasjonen sa «med «fra» som i 8.17a»; det er datoen, ikke ordet |
| VG3, BH6, ECH4 | Linja under for en rad med eldre dag var ikke prøvd. Er radens dag før startdagen, står «–» og en dato etter øverste linje | low | **rettet** for testen (`test_linja_under_for_en_rad_med_eldre_dag`, 0,00 % til 08.10). En aksje uten kurs i hele perioden **står**: «–» og «ingen kurs fra dagen» er sant |
| VG4 | Fargen i linja under var ikke prøvd | low | **rettet**: `test_fargen_i_linja_under` |
| BH16 | Datoen i linja under var fet | low | **rettet**: `font-weight: 400` |
| BH13 | Løkkevariabelen `navn` i `_perioder.html` skygget navnet på knappen | low | **rettet**: `felt` |
| BH10 | `docs/hjelp.md` sa indeksen «den dagen» også ved en periode | low | **rettet**. Linja under overskriften sier dagen siden gjelder, siste børsdag, og **står** |
| BH1 | `serier[...]` kunne gi KeyError i børsometeret | – | **avvist** etter oppslag: børsometeret leser en serie for hver post (`serier = {post.aksje.symbol: leser.serie(...) for post in poster}`) |
| BH2 | `egne_dager` kunne få en rad uten dato | – | **avvist**: radene fra `bygg_oversikt` har alltid dato; radene uten data er en egen liste |
| BH3 | Linja under har retningspillen | low | **står**: retningen vises i tre kanaler (FR-103); «uten pille» gjelder pillen for signalstyrken |
| BH4 | Samme dato kan stå flere ganger i lista for fotnoten | low | **avvist**: `_fotnoten` bruker bare `all` og `in`, så antallet betyr ingenting |
| BH5 | «ingen kurs fra dagen» kunne gi fotnoten «ikke vurdert» | – | **avvist**: `ikke_vurdert` leser teksten, som er byttet |
| BH7 | Lesingen av vurderingen per rad uten feilhåndtering | low | **avvist**: `sqlite3.Error` gir siden for basefeil, som «Velg dag» i oversikten (8.17a) |
| BH8 | Fargetrinnene er laget for én dag og brukes for en periode | low | **står**: svaret 23.10 kl. 12:35 (b) sier at fargen er endringen for perioden. Spørsmål til gruppen («Åpent») |
| BH8, svaret | *Avgjort 2026-11-03 kl. 19:25 (gruppens svar, 3):* fargetrinnene er de samme ved en periode | – | **avgjort**: står som bygget, ingen ny kode |
| BH9 | Snittet per bransje blander kortere serier inn | low | **står**: som tabellen i 8.17a, og «fra» står i tabellen |
| BH12, ECH5 | Med både `dag` og en periode i adressen gjelder dagen | low | **står**: `les_valg` gjør det samme i oversikten |
| BH14 | Fargen i linja under regnes med `round(2)` i malen | low | **står**: samme mønster som raden over (story 8.0) |
| BH15 | Tolkningen av «Velg dag» i Min liste er åpen, men bygget og skrevet i hjelpen | medium | **står**: spørsmål til gruppen før flettingen («Åpent»). Svarer gruppen annerledes, rettes `bygg_sammenligning`, hjelpen og testene |
| BH15, svaret | *Avgjort 2026-11-03 kl. 19:25 (gruppens svar, 1 og 2):* tolkningen av f er riktig, og «Velg dag» i Min liste viser endringen fra dagen til siste børsdag | – | **avgjort**: som bygget, så hjelpen, testene og README-en står |
| BH17 | Første valgbare dag i børsometeret er seriens første dag, i oversikten dagen etter | low | **står**: børsometeret beholder regelen fra 8.6, der en dag før første kurs gir første børsdag |
| ECH3 | «til siste børsdag» for skjermleseren når raden har en eldre dag | low | **står**: raden sier «siste kurs» og datoen |
| ECH6 | En serie som ikke kan leses, gir «ingen kurs fra dagen» i linja under | low | **står**: som «Velg dag» i oversikten |
| ECH7 | Datofeltet i børsometeret er ikke fylt ut med siste børsdag lenger | low | **står**: makroen er lik på alle sidene (§2) |

## Åpent

- **Tolkningen av f i Min liste (spørsmål til gruppen):** siste børsdag er sidens dag, og linja under er sammenligningen, så Min liste viser to dager med vilje. Er det riktig? Og skal endringen i linja under for «Velg dag» være fra dagen til siste børsdag (valgt her), eller endringen den dagen, som «Velg dag» i oversikten?
  - *Avgjort 2026-11-03 kl. 19:25 (gruppens svar, 1 og 2):* tolkningen er riktig: siste børsdag er sidens dag, og linja under er sammenligningen. Ved «Velg dag» viser linja under endringen fra dagen til siste børsdag, som bygget. Ingen ny kode.
- **BH8 (spørsmål til gruppen):** fargetrinnene i børsometeret (±0,5 % og 2 %) er laget for én dag. Ved 3 mnd og lenger blir de fleste rutene sterke. Skal trinnene være de samme for en periode, som nå?
  - *Avgjort 2026-11-03 kl. 19:25 (gruppens svar, 3):* fargetrinnene er de samme ved en periode. Ingen ny kode.
