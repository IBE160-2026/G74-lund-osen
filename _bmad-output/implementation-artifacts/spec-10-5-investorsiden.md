---
title: 'Story 10.5: lenken til selskapets investorside i aksjedetaljen'
type: 'feature'
created: '2026-10-21'
status: 'review'
route: 'dispatch'
review_loop_iteration: 1
baseline_commit: '4baa247'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/docs/kilder-og-rettigheter.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-7a-stilen-i-en-css-fil.md'
---

## Intent

**Problem:** briefen v8 lover lenken til selskapets investorside i v1, og story 10.5 står igjen. Aksjesiden sier i dag bare at børsmeldingene ikke er med.

**Grunnlaget:** story 10.5 i `epics.md`, med utvidelsen 30.09, rettingen 06.10 og gruppens svar 19.10 kl. 16:03 og 19:49, og instruksjonen 21.10 kl. 10:25. `designregler.md` sier at lenken går til selskapets investorside, den norske når den finnes, uten å skrive «på norsk», og at NewsWeb og Oslo Børs nevnes uten lenke. Euronexts vilkår forbyr lenker til `newsweb.oslobors.no`, `oslobors.no` og `live.euronext.com` uten tillatelse (`docs/kilder-og-rettigheter.md`). Ingen kode henter noe fra investorsidene, NewsWeb eller Euronext (AD-2).

## Kontrollpunktene

- a) Adressene: de 15 fra linjene kl. 16:03 og 19:49, ved navn og bransje, knyttet til symbolet fra Oslo Børs (EQNR), ikke til tickeren hos EODHD. Demoselskapene har ingen adresse.
- b) Siden: aksjesiden har lenken til investorsiden for aksjen siden viser, med selskapets navn i lenketeksten, og en kort tekst om at børsmeldingene står på NewsWeb og ofte også på investorsiden, uten lenke til NewsWeb eller Oslo Børs. Lenken henter ingenting, og plasseringen følger designreglene og CSS-fila. I demoen står teksten fra linja kl. 19:49 i stedet. Alt virker på 390 px uten vannrett rulling. Hjelpen, `docs/hjelp.md` og README-en følger med (regel 19), og bildene tas på nytt slik testen sier.
- c) Testene, med «Ville feilet hvis»: hver av de 15 har nøyaktig adressen fra linjene kl. 16:03 og 19:49, og lenken på siden går til aksjen siden viser; ingen mal og ingen side som vises, har en lenke til `newsweb.oslobors.no`, `oslobors.no` eller `live.euronext.com`; demoen viser teksten og ingen lenke; ingen kode i `src/` kaller adressene.

## Planen, én commit per punkt

1. a) Feltet `investorside` i `Aksje` i `src/kursdata.py`, med adressen for hver av de 15 i `AKSJEUNIVERS`, og et oppslag på symbolet.
2. b) Avsnittet på aksjesiden i `src/templates/aksje.html`, ruta i `src/app.py`, `docs/hjelp.md` og bildene.
3. c) Testene i `tests/test_investorsiden.py`, og mutantene.

## Avgjort i spesifikasjonen

- **Adressen står i `Aksje`, ved navn og bransje.** Feltet `investorside` har `None` som standard, så demoselskapene i `src/demo.py` ikke har noen adresse. Siden slår opp adressen på symbolet i `AKSJEUNIVERS`, fordi aksjen siden viser, leses fra `aksje` i basen (story 2.2b), og den tabellen har ingen adresse. Skjemaet i basen endres ikke.
- **Plasseringen:** avsnittet står under grafen, rett etter fotnoten «Signalet bygger bare på kurs og volum. Børsmeldinger og kommende finansielle hendelser er ikke med i denne versjonen.». Det er der siden alt sier hva den ikke viser. Avsnittet bruker klassen `fotnote` fra `src/static/stil.css`, så stilarket endres ikke.
- **Teksten** i den ekte versjonen: «Børsmeldingene står på NewsWeb og ofte også på investorsiden til <navn>.», der «investorsiden til <navn>» er lenken. NewsWeb står uten lenke, og «på norsk» står ikke.
- **Teksten i demoen** (svaret kl. 19:49): «Børsmeldingene står på NewsWeb og ofte også på selskapets investorside. <navn> er oppdiktet og har ingen investorside. I den ekte versjonen står lenken her.» Demoen kjennes på det samme som merket «Eksempeltall».
- **Hjelpen bak «?»** sier ingenting om lenker eller børsmeldinger, så ingen tekst i `src/hjelpetekster.py` blir feil og ingen endres. `docs/hjelp.md` får et spørsmål under «Den ekte versjonen». «Ferdig» i README-en får lenken etter flettingen, fordi «Ferdig» betyr flettet til main.

## Avgjort underveis

- **Adressene står i tabellen `INVESTORSIDER` i `src/kursdata.py`, rett under `AKSJEUNIVERS`, og ikke som et felt i `Aksje`** (`34240ee`). `Aksje` er raden i tabellen `aksje`, og `tests/test_aksje.py` krever at feltene i `Aksje` er kolonnene i tabellen. Et nytt felt ville derfor endret skjemaet. Tabellen er knyttet til symbolet, i samme rekkefølge som `AKSJEUNIVERS`, og `investorside(symbol)` slår opp i den. Det erstatter punkt 1 i planen og første punkt under «Avgjort i spesifikasjonen» (gjennomgangen, BH1, VG1, ECH9 og VG11).
- **Demoteksten** er «Børsmeldingene står på NewsWeb. <navn> er oppdiktet og har ingen investorside. I den ekte versjonen står lenken til selskapets investorside her.» Den første utgaven sa også at børsmeldingene ofte står på selskapets investorside, rett før den sa at selskapet ikke har noen (gjennomgangen, VG9).
- **En aksje i en ekte base uten adresse** får «Børsmeldingene står på NewsWeb og ofte også på selskapets investorside.», uten lenke (gjennomgangen, ECH5).
- **`tests/test_utseende.py`:** `test_ingenting_fra_nettet` og `test_hver_lenke_gaar_til_en_side_som_finnes` godtok ingen adresse utenfor appen, og ble røde med lenken (gjennomgangen, ECH1, med dom høy). Formålet deres er at siden ikke laster noe fra nettet. En `<a href>` til en av de 15 investorsidene laster ingenting, og story 10.5 krever den. Testene godtar nå en slik lenke, og avviser fortsatt `src`, stilark og alle andre adresser utenfra.
- **Bildene** ble tatt på nytt to ganger, etter fremgangsmåten i 3.3b og 3.3f, og var begge gangene byte for byte de samme. Målt i Edge uten vindu: bunnen av grafen på `/aksje/KVST` ligger ved 1872 px, som `HOEYDE_PAA_AKSJESIDEN`, og avsnittet begynner ved 1980 px, under bildet. Oversikten endres ikke synlig og er tatt med 1630 px. Bare avtrykkene, som er av kildefilene, er nye.
- **390 px**, målt i Edge uten vindu med siden i en iframe på 390 px: `scrollWidth` er 390 på `/aksje/KVST`, `/` og `/min-liste` i demoen, og på alle de 15 aksjesidene i den ekte versjonen, med en midlertidig base. Avsnittet slutter ved 374 px (gjennomgangen, VG3 og BH12).
- **Commit a er rød alene** på testene for bildene, fordi `kursdata.py` er med i begge avtrykkene. Avtrykkene ble satt i commit b, og PR-en squash-flettes (gjennomgangen, VG5).

## Mutantene

Én om gangen med `-x` på `tests/test_investorsiden.py`, i en fersk klon med `core.autocrlf=false`, med kopi av fila før og sha256 lik HEAD etter hver, og `git status` tom. M1–M3 er fra instruksjonen, kjørt på `b65427f` og igjen på `18a377c`. N1–N3 er mutantene fra Edge Case Hunter som overlevde, kjørt på `18a377c`.

| # | Mutant | Først i fila | Testen alene |
|---|---|---|---|
| M1 | EQNR og DNB byttet om | `test_hver_av_de_15_har_adressen_fra_svarene` | den samme feiler |
| M2 | En lenke til NewsWeb i malen | `test_lenken_paa_siden_gaar_til_aksjen_siden_viser` | `test_ingen_mal_lenker_til_euronext` feiler |
| M3 | Lenken vist i demoen | `test_en_ekte_aksje_uten_adresse_faar_setningen_uten_lenke` (på `b65427f`: `test_demoen_viser_teksten_og_ingen_lenke`) | `test_demoen_viser_teksten_og_ingen_lenke` feiler |
| N1 | Avsnittet skjult når siden har en vurdering | `test_lenken_paa_siden_gaar_til_aksjen_siden_viser` | den samme feiler |
| N2 | Ingen lenke ved «Velg dag» | `test_lenken_paa_siden_gaar_til_aksjen_siden_viser` | den samme feiler |
| N3 | Demoteksten styrt av adressen, ikke merket | `test_en_ekte_aksje_uten_adresse_faar_setningen_uten_lenke` | den samme feiler |

## Gjennomgangen

Gjennomgang 21.10 på diffen `4baa247..b65427f`. Linsene var:
- Blind Hunter (BH, 15 funn, bare diffen)
- Edge Case Hunter (ECH, 10 funn, med mutanter i en fersk klon som ble slettet etterpå)
- Verification Gap (VG, 12 funn)

| # | Funn | Dom | Rute |
|---|---|---|---|
| ECH1 | Grenen gjorde `test_ingenting_fra_nettet` og `test_hver_lenke_gaar_til_en_side_som_finnes` røde | high | rettet: testene godtar en `<a href>` til en av de 15, ført under «Avgjort underveis» |
| BH1, VG1, ECH9, VG11 | Spesifikasjonen sier et felt i `Aksje`, koden har en egen tabell | medium | rettet: ført under «Avgjort underveis» |
| BH2, VG6 | Testen for AD-2 hoppet over hele `kursdata.py` | medium | rettet: importene i `kursdata.py` og bruken av tabellen sjekkes |
| VG2 | Mutantene var ikke ført | medium | uten endring i koden: de var kjørt på `b65427f` før gjennomgangen, og står i «Mutantene» |
| VG3, BH12 | Ingenting viste 390 px | medium | rettet: målt i demoen og på de 15 i den ekte versjonen |
| ECH2 | Siden med en vurdering var ikke testet i den ekte basen | medium | rettet: basen i testen har vurderingen, og N1 fanges |
| ECH3 | «Velg dag» var ikke testet | low | rettet: N2 fanges |
| ECH4 | Demobasen der den ekte skal ligge var ikke testet | low | rettet |
| ECH5, BH5, VG10 | En ekte aksje uten adresse fikk ingen setning | low | rettet: setningen uten lenke, og N3 fanges |
| ECH6 | Escapingen av navnet var ikke testet | low | rettet: avsnittet bruker ikke filteret `safe` |
| ECH7 | `rel` og `target` var ikke testet | nit | rettet |
| ECH8 | Avtrykket i `test_docker.py` fanger alle malmutanter uten å si noe om atferd | nit | uten endring: avtrykket er en lås for bildene, og mutantene er kjørt mot `test_investorsiden.py` |
| ECH10, BH9, VG8 | Demotesten så bare på tre selskaper | low | rettet: alle, med MTFJ som 404 |
| BH6, BH7, VG7 | Sjekken mot Euronext så bare på `<a href>` og noen sider | low | rettet: hele malene, og href, src og action på sidene, med «Velg dag» og 404 |
| BH8 | Demotesten tålte to 404 | low | rettet: MTFJ står for seg |
| BH3 | Testen for `app.py` sammenligner linjene | low | avvist: en endring i linjene skal få testen til å feile, så den blir vurdert |
| BH4 | Fire adresser er engelske sider | low | avvist: gruppen sjekket alle 15 kl. 19:49. EQNR og NHY har bare en norsk side som viser til den engelske, og de andre tolv står |
| BH10 | «Nederst på aksjesiden» i hjelpen | low | avvist: bare skjulte hjelpevinduer står etter avsnittet (VG12) |
| BH11, VG4 | Kommentarene om bildene, og ingen målinger ført | low | rettet: kommentarene sier at avtrykket er av kildefilene, og målingene står under «Avgjort underveis» |
| BH13 | README-en er ikke endret | nit | uten endring: «Ferdig» får lenken etter flettingen |
| BH14 | Navn i testfila | nit | rettet: `EURONEXT`. `newsweb.oslobors.no` står, som i instruksjonen |
| BH15 | Skriver fixturen til den ekte basen? | low | avvist: `tests/conftest.py` peker `BASE_STI` til `tmp_path` |
| VG5 | Commit a er rød alene | low | uten endring: ført under «Avgjort underveis», og PR-en squash-flettes |
| VG9 | Demoteksten motsa seg selv | low | rettet |
| VG12 | README, hjelpen og kontrollpunktet om tickeren | nit | uten endring: ingen feil funnet |

## Det som ikke endres

- Ingen kode henter fra investorsidene, NewsWeb eller Euronext, og ingen test går på nett.
- `data/db/ose.db` og `data/db/demo.db` røres ikke, og skjemaet i basen endres ikke.
- Briefen står.
