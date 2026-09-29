---
title: "Kodegjennomgang av Epic 1"
status: done
created: 2026-09-27
updated: 2026-09-29T15:18
---

# Kodegjennomgang av Epic 1

Punkt 22 i `prd.md` §8: `bmad-code-review` etter hver ferdige epic. Gjennomgangen
23.09 tok 1.1–1.3. Denne tar hele Epic 1, med skjøtene mellom storyene, på diffen
for `src/` og `tests/` fra `57a83c5^` (før story 1.1) til `8fa254f`: 38 filer,
5 269 linjer inn og 477 ut. Endringene fra story 2.0 (`4b65a3c`) og 9.0
(`c2c26ba`) er med, og funnene der er merket med storyen. Denne runden finner og
sorterer bare. Ingenting er rettet.

## Slik ble diffen delt

- **Del A, lagringen** (3 309 linjer): `migrering.py`, `migrasjoner/0001–0002`,
  `lagring_sqlite.py`, `vurderingsdata.py`, `boersdag.py` og `tilstand.py`, med
  testene `test_migrering`, `test_lagring_sqlite`, `test_kurslager`,
  `test_vurderingslager`, `test_boersdag`, `test_tilstand` og `test_tidssone`.
- **Del B, lesingen og konsumentene** (3 476 linjer): `kursdata.py`, `eodhd.py`,
  `lagring_fil.py`, `fetch_prices.py`, `app.py`, `aksjedetalj.py`,
  `markedsoversikt.py`, `signalberegning.py`, `graf.py` og malene, med testene
  deres, `conftest.py`, `test_ingen_nettverk` og `test_readme`.

Hver del fikk fire lag: Blind Hunter (BH), bare diffen, Edge Case Hunter (ECH)
og Verification Gap (VG), med tilgang til repoet, og Acceptance Auditor (AA) mot
`epic-1-context.md` og storyene i `epics.md`. Radene har prefikset A- eller B-
for delen. Ingen lag feilet. VG for del A fant ingen hull i verifikasjonen.

Hvert funn er prøvd mot koden på `8fa254f` før dommen. Dommene følger
triagesteget: `high`, `medium` og `low` er virkelige feil, `false` er motbevist.
«Kjent» betyr at funnet alt står i `deferred-work.md`, i en triagelogg eller i en
beslutning, og hvor.

## Sammendrag

61 funn fra åtte lag. 21 er kjent fra før, 7 er samme sak som et annet funn i
denne runden, 1 er `false`, og 18 er avvist. De 14 som står igjen, er samlet i
12 grupper, sortert etter alvor:

| Gruppe | Story | Sak | Dom | Funn | Forslag |
|---|---|---|---|---|---|
| G1 | 2.0 × 1.4a | Hentingen godtar rader som leseren avviser. Symbolet lagres og telles som hentet, og visningen dropper det uten at noe er ført i `feil` | medium | B-BH2, B-BH3, B-ECH3, B-AA1, B-VG1 | egen story |
| G2 | 2.0 | Hardkodet 14 og 15 i testene for `hent_universet` | low | B-BH13 | egen story, sammen med G1 |
| G3 | 2.0 | Testen for URL-kodet nøkkel skiller ikke `quote` fra `quote_plus` | low | B-VG-a | egen story, sammen med G1 |
| G4 | 1.5 / 2.0 | Docstringene i `fetch_prices.py` viser til `SnapshotKilde`, ikke `SnapshotLeser` | low | B-BH8, B-AA5 | egen story, sammen med G1 |
| G5 | 1.6 | Ingen test binder regelen for `styrke` i `Vurdering` til `beregn_signal` | low | A-AA7 | egen story |
| G6 | 1.7 | `tilstand.py` og `test_tilstand.py` heter fortsatt «De tre tilstandene» | low | A-BH5 | egen story |
| G7 | 1.7 | Docstringen i `test_tilstand.py` sier at hver test lager en base | low | A-BH13 | egen story |
| G8 | 1.3 / 1.6 | Testnavnet `…_til_versjon_1_…` krever nå `>= 1` | low | A-BH10 | egen story |
| G9 | nettsperren (`982b216`) | `conftest.py` sier «ingen navneoppslag», men bare `getaddrinfo` er sperret | low | B-BH11 | egen story |
| G10 | 1.3 × 1.6 | `Kurslager` godtar ethvert symbol, `Vurderingslager` bare formen i `AKSJEUNIVERS` | low | A-BH2, A-ECH3, A-AA3 | vent: forutsetning i 2.2 *(merknad 2026-09-29: `epics.md` flyttet porten til 2.1b 28.09. Tatt i 2.1b: `kontroller_skriving` avviser et symbol utenfor `AKSJEUNIVERS` i begge lagrene.)* |
| G11 | 1.3 × 1.6 | `Vurderingslager.skriv` slipper ut rå `sqlite3`-feil, mens `SqliteKurslager` gjør `IntegrityError` om til `ValueError` | low | A-BH1, A-AA2 | vent: avgjøres i 2.5 |
| G12 | 2.0 | `main()`, eneste kaller av `kjoer` i produksjon, har ingen test | low | B-VG2 | vent: tas i 2.3 *(merknad 2026-09-29: `epics.md` la den til 2.1 27.09, i `51f1cf9`. Tatt i 2.1.)* |
| — | | Avvist (se tabellene) | | 18 funn | avvis |

## Del A: lagringen

| # | Story | Funn | Dom | Bevis | Forslag |
|---|---|---|---|---|---|
| A-BH1 | 1.3 × 1.6 | `SqliteVurderingslager.skriv` slipper ut rå `sqlite3.IntegrityError`, mens `SqliteKurslager.erstatt_serie` gjør den om til `ValueError` (`lagring_sqlite.py:102`, `:210`) | low | Riktig. `test_feil_i_basen_rulles_tilbake` låser det. Men porten kontrollerer alt før SQL-en, så `IntegrityError` nås bare med en trigger eller en base som er endret utenom porten. `OperationalError` slipper ut av begge adapterne | G11, vent: 2.5 skriver gjennom begge portene og avgjør hvilke feil den fanger |
| A-BH2 | 1.3 × 1.6 | `SqliteKurslager.erstatt_serie` kontrollerer ikke symbolet mot `AKSJEUNIVERS`, og `EQNR.OL` blir en egen serie | low | Riktig: `_kontroller_noekkel` kalles bare fra `SqliteVurderingslager` (`lagring_sqlite.py:183`, `:219`). Ingen skriver i produksjonskoden ennå: hentingen skriver til fil til 2.2 | G10, vent: forutsetning i 2.2, der hentingen begynner å skrive gjennom `Kurslager` |
| A-BH3 | 1.6 | Tabellen `vurdering` har ingen trigger mot `DELETE` eller `UPDATE`, selv om `grunn` har det | low | Riktig (`0002_vurdering.sql:63–87`). Porten har ingen `slett`, og protokolltesten holder det | avvist: samme som 1.6 ECH3 (porten er eneste skriver). `grunn` har triggere fordi en slettet grunn gjør rader i `vurdering` uleselige (1.6 BH3) |
| A-BH4 | 1.6 | Fra 2027-01-01 reiser `skriv` for alle symboler, også for en grunn, og ingenting varsler før det | — | Kjent | kjent: 1.6 BH2 og BH11 (runde 2), vedtaket i punkt 3 og punkt 25 i `prd.md` §8 |
| A-BH5 | 1.7 | Modulen og testfila heter «De tre tilstandene», men `Art` har fire verdier | low | `tilstand.py:1` og `test_tilstand.py:1`. 1.7 BH5 rettet spinen, ikke modulene | G6, egen story: tekst |
| A-BH6 | 1.7 | `Tilstand` skiller ikke dagens rad som mangler fra et endelig hull | — | Kjent | kjent: 1.7 BH4 og beslutningen 27.09 |
| A-BH7 | 1.7 | Børsdager før første kjøring blir `IKKE_KJOERT` for alltid | — | Kjent | kjent: beslutningen 27.09 i spesifikasjonen for 1.7 |
| A-BH8 | 1.5b | En migrasjonsfil med BOM gir feil hash, og `COMMIT` i første setning slipper forbi forhåndssjekken | — | Kjent | kjent: 1.5b ECH6 (avvist) |
| A-BH9 | 1.6 | Kommentaren i `vurderingsdata.py:111–113` gir feil grunn til omgjøringen til float | false | Kommentaren sier at `float` gir `OverflowError` for et heltall som er for stort for float (10**400), og at 10**20 uten omgjøringen ville feilet i SQLite. Begge deler stemmer med 1.6 ECH1 | avvist |
| A-BH10 | 1.3 / 1.6 | `test_tom_base_migreres_til_versjon_1_med_to_tabeller` krever nå `>= 1` | low | `test_lagring_sqlite.py:51–54`. Navnet stemmer ikke etter `0002` | G8, egen story: nytt navn |
| A-BH11 | 1.6 | «Basen er ikke klar» er testet grundig for `SqliteKurslager`, men for `SqliteVurderingslager` bare versjon 1 og åpen transaksjon | low | Riktig, men begge bruker samme `_krev_siste_versjon`, og VG for del A fant testene for den | avvist: samme funksjon, prøvd for begge adapterne |
| A-BH12 | 1.6 | Ingen test av `skriv` med klokka på en helligdag midt i uka | low | Riktig for `skriv`. `innevaerende_boersdag` er prøvd for hver stengte dag i `test_boersdag.py`, og koblingen til `skriv` er prøvd med lørdag | avvist: dekket av to tester |
| A-BH13 | 1.7 | Docstringen i `test_tilstand.py:7` sier at hver test lager sin egen base | low | Riktig: bare `TestGjennomLageret` bruker en base | G7, egen story: tekst |
| A-ECH1 | 1.6 | En grunn som finnes i tabellen, men ikke i `Grunn`, gir `ValueError` når `les` leser raden | low | Riktig, men docstringen til `Grunn` sier at en ny grunn er en ny verdi i enumen og en `INSERT` i samme migrasjon | avvist: regelen står der den trengs |
| A-ECH2 | 1.6 | `les` validerer radene på nytt, så en rad skrevet utenom porten eller strengere regler senere gjør gamle rader uleselige | — | Kjent | kjent: 1.6 BH4 og ECH3 (runde 2) |
| A-ECH3 | 1.3 × 1.6 | `erstatt_serie` godtar `EQNR.OL` | low | Samme som A-BH2 | G10 |
| A-ECH4 | 1.6 | En tilkobling med `autocommit=False` blir alltid avvist med en misvisende melding | — | Kjent | kjent: 1.6 BH8 (runde 2) |
| A-ECH5 | 1.5b | En migrasjonsfil som endres mellom forhåndssjekken og kjøringen, slipper forbi sjekken | low | Riktig i prinsippet: fila leses to ganger. Krever at noen endrer fila mens `migrer()` kjører | avvist: lite sannsynlig, og rettingen legger til tilstand |
| A-ECH6 | 1.5b | BOM i en migrasjonsfil | — | Kjent | kjent: 1.5b ECH6 |
| A-VG-a | 2.0 / 2.1 | `fetch_prices.py:63, 198, 253` bruker maskinens dato (`date.today()`), ikke `norsk_dato` | — | Kjent | kjent: story 2.1 i `epics.md` (kontrollpunktet om kjøringen 00:30) |
| A-AA1 | 1.7 | Lageret gir fortsatt `None` både for «ikke kjørt» og «ikke børsdag», mens storyen sier «lageret svarte» | low | Riktig etter ordlyden i `epics.md:866`. Tilnærmingen i spesifikasjonen for 1.7 (Intent, godkjent 27.09) er at `tilstand` tolker det `les` gir, og docstringen i `tilstand.py` krever at alle som leser historikken, bevarer skillet | avvist: godkjent tilnærming. Den som leser historikken (punkt 20), må gå gjennom `tilstand` |
| A-AA2 | 1.3 × 1.6 | Adapterne melder feil ulikt, og `sqlite3` lekker gjennom `Vurderingslager` | low | Samme som A-BH1 | G11 |
| A-AA3 | 1.3 × 1.6 | `Kurslager` godtar ethvert symbol | low | Samme som A-BH2 | G10 |
| A-AA4 | 1.6 | Går en aksje ut av universet, kan de gamle radene ikke leses gjennom porten | low | Riktig: `les` kaller `_kontroller_noekkel`. Men universet er fast i v1 (`prd.md` §3), og kontrollen i `les` er valgt i 1.6 BH7 | avvist: tas hvis universet endres |
| A-AA5 | 1.6 × 1.7 | `tilstand` tar `idag` fra kalleren, mens lageret leser klokka selv | low | Riktig, men `tilstand` har ingen kaller ennå, og docstringen ber om `norsk_dato` | avvist: kallerens sak |
| A-AA6 | 1.6 | Fredagens rad kan skrives på lørdag og søndag | — | Kjent | kjent: beslutningen 27.09 i spesifikasjonen for 1.7 og vedtaket i punkt 3 |
| A-AA7 | 1.6 | `Vurdering` krever `styrke == sum(abs(...))`, men ingen test binder det til `beregn_signal` | low | Riktig: for `retning` finnes testen mot `finn_retning` (`test_vurderingslager.py:442`), for `styrke` ikke. Regelen står i `signalberegning.py:211` | G5, egen story: én test |
| A-AA8 | 1.5b | Adapteren sjekker bare versjonsnummeret, ikke filnavn eller hash | — | Kjent | kjent: 1.5b 2-BH3 |

## Del B: lesingen og konsumentene

| # | Story | Funn | Dom | Bevis | Forslag |
|---|---|---|---|---|---|
| B-BH1 | 1.4a | Én ugyldig rad gjør hele aksjen manglende, og ingenting sier hvorfor | — | Kjent | kjent: 1.4a rad 10 (avvist). Blir alvorlig sammen med G1 |
| B-BH2 | 2.0 × 1.4a | `_riktig_form` sjekker bare at de fire feltene finnes og at `date` er tekst. Leseren avviser mye mer | medium | Kjørt: rader med `date` «2026-9-1», `close` `None` og `volume` 1.5 gir `_riktig_form` `True`, mens `kursrad_fra_eodhd` reiser `UgyldigKursrad`. Symbolet lagres, `feil` er tom, og `SnapshotLeser` dropper det (`lagring_fil.py:96–99`). Hentingen melder at alt gikk bra, mens visningen mangler aksjen | G1, egen story: `hent_universet` oversetter hver rad med `kursrad_fra_eodhd` og sjekker like datoer, og «svar med feil form» betyr det samme som for leseren |
| B-BH3 | 2.0 | `FELT` i `fetch_prices.py` er en kopi av det `eodhd.py` leser | low | Riktig: `fetch_prices.py:113`, og en tredje kopi i `test_konsumentene.py` | G1: forsvinner når hentingen bruker oversetteren |
| B-BH4 | 2.0 | Skrivingen er ikke atomisk, og en halvskrevet fil stopper resten av dagens kjøringer | — | Kjent | kjent: 2.0 ECH1 (avvist) |
| B-BH5 | 1.5 | Et ødelagt øyeblikksbilde gir 500 på begge sidene | — | Kjent | kjent: `deferred-work.md` (1.5 rad 1) |
| B-BH6 | 2.0 | `kjoer` kaller `sys.exit(1)`, og kallene som er brukt, kastes når fila dukker opp under kjøringen | low | Riktig. Koden er valgt i 2.0 ECH3, og det krever to kjøringer samme dag | avvist: valgt i 2.0 |
| B-BH7 | 2.0 | For tilkoblingsfeil står bare klassenavnet igjen, så vert og årsak går tapt | low | Riktig (`fetch_prices.py:97`). Valgt med vilje: lag 1 fjerner hele teksten fra `requests`, og lag 2 er reserven | avvist: valgt i 2.0 |
| B-BH8 | 1.5 / 2.0 | Docstringene i `fetch_prices.py:15` og `:180` sier «formatet `SnapshotKilde` leser» | low | Riktig. Visningen leser gjennom `SnapshotLeser`, som er strengere. Det var misforståelsen bak funnet i 9.0 | G4, egen story: tekst |
| B-BH9 | 1.4c | `norsk_tid` godtar en tid uten sone | — | Kjent | kjent: 1.4c rad 3 (avvist) |
| B-BH10 | 1.4c | Datoen i overskriften er `rader[0].dato` | — | Kjent | kjent: `deferred-work.md` (1.4c rad 12) |
| B-BH11 | nettsperren (`982b216`) | `conftest.py` sier at testene ikke gjør navneoppslag, men bare `socket.getaddrinfo` er sperret | low | Riktig (`conftest.py:20–22`, `:88`). `gethostbyname` og de andre er ikke sperret. `connect` er sperret, så ingen trafikk går ut utover selve oppslaget | G9, egen story: sperr de andre oppslagene, eller skriv docstringen om |
| B-BH12 | 1.2 | `kontroller_skriving` reiser både `TypeError` og `ValueError`, ikke `UgyldigKursrad` | low | Riktig, men `UgyldigKursrad` gjelder raden, og `kontroller_skriving` gjelder argumentene til skrivingen. Ingen kaller i produksjonskoden fanger dem | avvist: ingen navngitt skade |
| B-BH13 | 2.0 | `TestSvarMedFeilForm` og tre andre tester har skrevet inn 14 og 15, ikke `len(AKSJEUNIVERS)` | low | `test_fetch_prices.py:203–204, 235–236, 248, 280, 290, 393`. 2.0 BH14 rettet én test | G2, egen story |
| B-BH14 | README-testen (`47a507a`) | `test_readme` ser ikke referanselenker, `<…>`-lenker eller URL-kodede stier | low | Riktig om regex-en, men README-en har ingen slike lenker i dag (0 treff) | avvist: lite sannsynlig, og krever ny kode |
| B-ECH1 | 1.5 | Et ødelagt øyeblikksbilde gir 500 | — | Samme som B-BH5 | kjent |
| B-ECH2 | 2.0 | En halvskrevet fil stopper senere kjøringer | — | Samme som B-BH4 | kjent |
| B-ECH3 | 2.0 × 1.4a | Rader med alle fire feltene, men verdier `Kursrad` avviser | medium | Samme som B-BH2 | G1 |
| B-ECH4 | 2.0 | `raise … from None` beholder den opprinnelige feilen i `__context__`, med adressen og nøkkelen | low | Riktig i Python, men `__suppress_context__` er satt, og ingenting i repoet leser `__context__`. `hent_universet` lagrer bare `str(feil)` | avvist: ingen vei ut i repoet |
| B-ECH5 | 2.0 | En feil fra `requests.get` som ikke er `RequestException`, slipper ut med adressen | low | Mulig i prinsippet, men lag 2 i `hent_universet` bytter nøkkelen, også URL-kodet | avvist: dekket av lag 2 |
| B-ECH6 | — | Skriptene `data/kontrollregning_1_4*.py` og `_1_5.py` importerer navn som er flyttet | low | Riktig, men `data/` spores ikke (regel 10) | avvist: utenfor repoet |
| B-ECH7 | 1.2 | Meldingen til `54696d9` sier `strptime`, men koden bruker `fromisoformat` med kontroll | low | Riktig. `04933f6` beskriver den virkelige oppførselen | avvist: historikken skrives ikke om (regel 7) |
| B-VG1 | 2.0 | Ingen test har en rad som mangler bare ett prisfelt, eller en `date` som er tall eller tom | low | Filet av VG: mutantene som fjerner `adjusted_close` fra `FELT` eller tekstkontrollen, overlever | G1: testene byttes når hentingen bruker oversetteren |
| B-VG2 | 2.0 | `main()` er eneste kaller av `kjoer` i produksjonen, og ingen test kjører den | low | Filet av VG: en `main` som skriver til en annen katalog, består alle tester. VG foreslo å utsette | G12, vent: tas når 2.3 utvider `kjoer` *(merknad 2026-09-29: tatt i 2.1)* |
| B-VG-a | 2.0 | `test_url_kodet_noekkel_fjernes_ogsaa` bruker `ab+c/d=e`, der `quote` og `quote_plus` gir samme tekst | low | Riktig (`test_fetch_prices.py:104`). Å fjerne én av formene fra `_uten_noekkel` gir ingen feil | G3, egen story: en nøkkel med mellomrom |
| B-VG-b | — | Skriptene i `data/` | low | Samme som B-ECH6 | avvist |
| B-AA1 | 2.0 × 1.4a | Hentingen har sin egen, svakere radkontroll | medium | Samme som B-BH2 | G1 |
| B-AA2 | 2.0 × 1.5 | En halvskrevet eller ødelagt fil stopper hentingen og gir 500 på sidene | — | Kjent | kjent: 2.0 ECH1 og `deferred-work.md` (1.5 rad 1) |
| B-AA3 | 1.4c | Datoen i overskriften kommer fra første rad | — | Kjent | kjent: `deferred-work.md` (1.4c rad 12) |
| B-AA4 | 1.5 | `app.py` henter leseren fra en funksjon i adapteren, ikke gjennom en port | low | Riktig, men kriteriet («kaller ikke `nyeste_snapshot()` direkte») er oppfylt, og returtypen er porten `Kursleser` | avvist: `app.py` endres uansett når den leser fra basen i 2.2 |
| B-AA5 | 1.5 / 2.0 | Docstringene lover feil lesekontrakt | low | Samme som B-BH8 | G4 |
| B-AA6 | 1.4a | Et nyeste øyeblikksbilde som ikke kan leses, skjuler et eldre som kan | — | Kjent | kjent: `deferred-work.md` (1.4b, «Ingen kursdata funnet» når `hentet` ikke kan leses), tas i 2.2 |
| B-AA7 | 2.0 / 2.1 | Sjekken for tidlig stopp bruker maskinens dato, ikke Oslo-datoen | — | Kjent | kjent: story 2.1 i `epics.md` |
| B-AA8 | 1.4a | `Kursrad` avviser `volum` som float | low | Riktig, men 3 735 ekte rader ga ingen problemer 23.09. Risikoen er at det skjer uten at noe føres, og det er G1 | avvist: dekket av G1 |

## Tellingen

- Del A: 13 (BH) + 6 (ECH) + 1 (VG, annet funn) + 8 (AA) = 28.
- Del B: 14 (BH) + 7 (ECH) + 4 (VG, 2 hull og 2 andre) + 8 (AA) = 33.
- Kjent fra før: A-BH4, A-BH6, A-BH7, A-BH8, A-ECH2, A-ECH4, A-ECH6, A-VG-a,
  A-AA6, A-AA8, B-BH1, B-BH4, B-BH5, B-BH9, B-BH10, B-ECH1, B-ECH2, B-AA2, B-AA3,
  B-AA6 og B-AA7. Det er 21.
- Samme sak som et annet funn i denne runden: A-ECH3, A-AA2, A-AA3, B-ECH3,
  B-AA1, B-AA5 og B-VG-b. Det er 7.
- `false`: A-BH9.
- Avvist: A-BH3, A-BH11, A-BH12, A-ECH1, A-ECH5, A-AA1, A-AA4, A-AA5, B-BH6,
  B-BH7, B-BH12, B-BH14, B-ECH4, B-ECH5, B-ECH6, B-ECH7, B-AA4 og B-AA8. Det er 18.
- Står igjen: A-BH1, A-BH2, A-BH5, A-BH10, A-BH13, A-AA7, B-BH2, B-BH3, B-BH8,
  B-BH11, B-BH13, B-VG1, B-VG2 og B-VG-a. Det er 14, i G1–G12.
- Sum: 21 + 7 + 1 + 18 + 14 = 61.

## Beslutning 2026-09-27

Gruppen sier ja til forslagene, med disse endringene (instruksjonen kl. 22:04 i
dagsfila):

- **G6 (A-BH5) avvises.** Overskriften følger FR-409 og story 1.7, og teksten
  under den sier fire verdier, som spinen gjør.
- **G7 (A-BH13) er false.** Fixturen i `TestGjennomLageret` har funksjonsscope,
  så hver test der lageret er med, får sin egen base, slik docstringen sier.
- **G9 (B-BH11) er kjent** fra story 4.0: «`gethostbyname`, `gethostbyname_ex`
  og `getfqdn` sperres også». 4.0 har fått en merknad om docstringen.
- **G10 (A-BH2) og G11 (A-BH1) venter på 2.5,** fordi innledningen til Epic 2
  («Lagt til 2026-09-25») legger skrivingen til basen der. De står som
  forutsetning i 2.5.
  *2026-09-28:* G10 er løst i basen i story 1.9 (AD-21): `0003` avviser et ukjent
  symbol i `kurs`, `kursserie` og `vurdering`. Om porten til `Kurslager` også
  skal sjekke symbolet, avgjøres fortsatt i 2.5, sammen med G11.
  *2026-09-29:* porten ble flyttet til 2.1b og tatt der: `kontroller_skriving`
  får symbolet og avviser alt utenfor `AKSJEUNIVERS`. G11 venter fortsatt på 2.5.
- **G12 (B-VG2) venter på 2.1,** som endrer dagen `main()` bruker. Den står som
  kontrollpunkt i 2.1.
- **G1 gjelder alle tilfellene** som ble prøvd 27.09 uten nett og med falsk
  henting: `close` `None`, `close` 0, `volume` 1000.0, `date` «2026-9-24» og en
  dato som går igjen. Hver av dem gir i dag serien i `resultat.serier`, ingenting
  i `feil` og 0 rader i `SnapshotLeser`, mens de andre aksjene leses.
- **A-AA1 står som avvist,** men 1.7 i `epics.md` har fått en merknad om at
  lageret svarer `None` for begge, og at `tilstand` skiller dem.
- **Story 1.8 tar G1–G5 og G8.**

### Tellingen etter beslutningen

Talt fra radene i del A og del B:

- Kjent fra før: de 21 over, og B-BH11 (story 4.0). Det er 22.
- Samme sak som et annet funn i denne runden: A-ECH3, A-AA2, A-AA3, B-ECH3,
  B-AA1, B-AA5 og B-VG-b. Det er 7.
- `false`: A-BH9 og A-BH13. Det er 2.
- Avvist: de 18 over, og A-BH5. Det er 19.
- Story 1.8: B-BH2, B-BH3 og B-VG1 (G1), B-BH13 (G2), B-VG-a (G3), B-BH8 (G4),
  A-AA7 (G5) og A-BH10 (G8). Det er 8.
- Venter: A-BH2 (G10) og A-BH1 (G11) på 2.5, og B-VG2 (G12) på 2.1. Det er 3.
- Sum: 22 + 7 + 2 + 19 + 8 + 3 = 61.

## Etter rettingene

*2026-09-28.* Punkt 22 i `prd.md` §8 er fulgt opp for Epic 1. Story 1.8 (`5c316e8`,
PR #10) rettet G1–G5 og G8, og story 1.9 (`cfe2977`, PR #11) løste G10 i basen
(AD-21). Begge ble gjennomgått i sin egen PR med tre lag: Blind Hunter, Edge
Case Hunter og Verification Gap. Det som venter, står i en story: G9 i 4.0, G11
i 2.5 og G12 i 2.1.

Tellingen etter rettingene, talt fra tellingen etter beslutningen:

- Kjent fra før: 22.
- Samme sak som et annet funn i denne runden: 7.
- `false`: 2.
- Avvist: 19.
- Rettet i 1.8: 8.
- Løst i 1.9: A-BH2 (G10). Det er 1.
- Venter: A-BH1 (G11) på 2.5 og B-VG2 (G12) på 2.1. Det er 2.
- Sum: 22 + 7 + 2 + 19 + 8 + 1 + 2 = 61.
