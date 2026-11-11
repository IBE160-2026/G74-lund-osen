---
title: 'Story 8.22: Faste bransjer, «Følg en aksje» med hele lista, og «Din egen liste» som tre steg'
type: 'feature'
created: '2026-11-10'
status: 'done'
route: 'dispatch'
baseline_commit: '53ff012c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/designutdrag-2026-11-08.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-12-velge-og-bytte-aksjer.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-11-ferdige-lister.md'
---

Skrevet 10.11 kl. 16:32 i instruksjonen kl. 16:26 («Del B 10.11», vindu 4). Instruksjonen lagres i dagsfila 10.11 sammen med flettingen, i en egen instruksjon etter gruppens ja (svaret kl. 14:59). Til da står den ordrett i scratchpad-mappa til økta. Storyen er bygget etter forslagene nedenfor, og gruppen svarer før flettingen.

## Svarene storyen bygger på

- **Kl. 13:38:** alle aksjene i børslista kobles til en bransje som gruppen har sjekket, så den som følger en aksje, ikke velger bransjen selv. Det erstatter svaret 08.11 kl. 11:57, der brukeren velger en av de 13. Kilden er instruksjonen kl. 13:41 i vindu 2, som står ordrett i scratchpad-mappa til økta `ff61373f`.
- **Kl. 14:43:** gruppen sjekket lista på en delt side. Alle 195 forslag og usikre er avgjort: 194 som foreslått, og MULTI er tatt ut, fordi en fusjon gjør det usikkert hva som skjer. De 195 er de 210 forslagene minus de 15 aksjene i lista, som har bransjen fra `designregler.md` §4. Kilden er svarene kl. 16:22 og 16:25 i vindu 2, i den samme mappa.
- **Kl. 15:22:** SCOIN er ute, som 08.11 kl. 22:03, fordi selskapet er under avvikling. Kilden er den samme.
- **Kl. 14:59:** ingen fletting. Storyen stopper når PR-en er grønn (steg 3 i instruksjonen).
- **Kl. 22:50 (tillegg 4, instruksjonen kl. 22:52):** steg 2 i «Din egen liste» blir som på designtavla, men uten felt, og AD-10 og svaret 08.11 kl. 12:39 står. Rådet anbefalte det. Svaret føres i `epics.md` med de andre svarene når del B flettes. Se «Tillegg 4: steg 2 som på tavla» nedenfor.
- **Kl. 13:54:** gruppen sa ja til del A og B. Bare feltet i steg 2 bygges ikke, fordi nettsiden aldri skal røre nøkkelen (AD-10, svaret 08.11 kl. 12:39), og resten følger designforslaget. Kilden er instruksjonen 11.11 kl. 11:56, som står ordrett i scratchpad-mappa til økta. Før den sto det her at ordlyden ikke var funnet (regel 11).
- **Kl. 14:53:** gruppen valgte å starte del B i et nytt vindu med en gang. Rådet anbefalte vindu 1 etter del C. Kilden er den samme.
- **Kl. 22:44 (tillegg 3, rådet anbefalte alle fire):** kortet «Mest omsatt» tas bort, og lista får sorteringen «Mest omsatt først», «A–Å» og «Bransje», uten «høyst tre». Flere bransjer kan velges samtidig og kombineres med omsetningen, og det valgte er oransje med et merke i tillegg. Radene får stilen fra tabellen på oversikten. «Start fra en ferdig liste» får én knapp per bransje, én kort setning og en side «Er du sikker?», og knappen i steg 3 heter som delen. Se «Tillegg 3 og 5» nedenfor.
- **Kl. 22:55 (tillegg 5):** to nye bilder fra demoen ved 390 px, «Følg en aksje» og notatene på aksjesiden for BRFE, i README-en etter de andre bildene ved 390 px.
- **11.11 kl. 14:29 (rådet anbefalte alt):** gruppen sa ja til forslagene i spørsmål 1–4, 6, 8–11, 13 og 16–18 som bygget. For spørsmål 12 måles tiden for medianene, og for spørsmål 14 legges testen for et kall som feiler til. Det valgte står i oransje med hakemerket som bygget (spørsmål 15). Del B flettes når svarene er bygget, gjennomgått og CI er grønn, etter at del C er flettet, uten at gruppen ser på den igjen. Kilden er instruksjonen 11.11 kl. 14:31, som står ordrett i scratchpad-mappa til økta. Se «Svaret kl. 14:29» nedenfor.
- Tillegg 3 og 5 ble gitt 10.11 kl. 22:44 og 22:55, men kom aldri fram til vindu 4. De ble gitt på nytt i instruksjonen 11.11 kl. 11:56, etter at Windows Update startet maskinen på nytt kl. 04:29. Svarene kl. 22:44 og 22:55 føres i `epics.md` med de andre svarene når del B flettes.

## Slått opp 10.11 på `53ff012c` (regel 3)

- CSV-fila `bransjeforslag-2026-11-10.csv` har 297 rader: 87 «sjekket 08.11», 157 «forslag» og 53 «forslag, usikker». De 87 er like med `BRANSJE` i `src/ferdige_lister.py` på `53ff012c` (87 ekte og 2 i demoen), ticker for ticker. Uten MULTI og SCOIN er det 295 aksjer, med samme antall per bransje og samme sha256 som instruksjonen.
- Tabellen `boersliste` i `data/db/ose.db` (lest med `mode=ro`, bare antall) har 297 aksjer. 3 ønsker venter, og ingen er tatt i bruk. sha256 for basen var den samme før og etter.
- `valg.Valglager.folg` tar bransjen fra skjemaet, og `/folg` viser en nedtrekksliste med de 13 (`folg.html`). `ta_i_bruk` skriver bransjen fra ønsket i `aksje.sektor`.
- Sidene har ett skript, `src/static/hjelp.js` (8.0f), og `test_ingen_skript_og_ingenting_fra_nettet` sier at ingen side har en adresse til nettet.
- Demobasen har fem oppdiktede selskaper på «Demo Børs» (`DEMOBOERSEN`). To står i `BRANSJE` (HVLK og NRDE). SKRH, TNDT og VKVF har ingen bransje noe sted, og ingen av de fem finnes i CSV-fila.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **En aksje som ikke står i `BRANSJE`.** *Forslag:* bransjen er den i `BRANSJE`. Står aksjen ikke der, brukes bransjen i `aksje`, for en aksje appen følger eller har fulgt. Det gjelder de 15 i demoen og en aksje som er tatt ut. Har den ingen av delene, kan den ikke følges og står ikke på siden. MULTI og SCOIN står derfor ikke, og `/folg` avviser dem med grunnen.
2. **De tre oppdiktede uten bransje i demoen.** *Forslag:* SKRH, TNDT og VKVF får bransjen som står i navnet (Helse, Teknologi og Forbruk) i en egen tabell, `DEMOBRANSJE`, ved siden av `BRANSJE`. Linjene for HVLK og NRDE i `BRANSJE` står som før. Uten tabellen kunne bare to av de fem følges i demoen.
3. **Egne aksjer som alt er lagt inn.** *Forslag:* siden viser bransjen fra `BRANSJE` med en gang. Ved neste henting tar `ta_i_bruk` ønskene i bruk med bransjen derfra, og retter `aksje.sektor` for de egne aksjene i lista der bransjen er en annen. De 15 og en aksje som er tatt ut, røres ikke. Vurderingene står (AD-7). En bransje som er rettet, gjelder også de tidligere dagene i setningen om bransjen, fordi den leses når siden vises. I den ekte basen venter 3 ønsker og ingen er tatt i bruk, så ingen egen aksje er rettet ennå.
4. **«Følg» på hver rad.** *Forslag:* knappen åpner «Følge …?» med omsetningen og kallene, som før, og ønsket lagres der. Bare ett trykk ville hoppet over kallene og «Utenfor målingen» (utdraget §1).
5. **Rekkefølgen i lista.** *Bortfalt med tillegg 3 (svaret kl. 22:44):* lista kan sorteres «Mest omsatt først», «A–Å» eller «Bransje». Se spørsmål 16 og 17.
6. **Filteret på omsetning.** *Forslag:* fire valg: «Alle», «Over 32 MNOK», «Under 32 MNOK» og «Ikke målt ennå». Medianen er den samme som i bransjelistene og merket (8.11c).
7. **De tre forslagene.** *Bortfalt med tillegg 3 (svaret kl. 22:44):* kortet med forslagene er tatt bort, og sorteringen «Mest omsatt først» er i stedet. Det som var foreslått: bare når en bransje er valgt. Forslagene er de tre med høyest median omsetning blant de målte i bransjen som ikke er i lista og ikke venter, med medianen som i bransjelistene. Uten valgt bransje står «Velg en bransje, så står de tre mest omsatte du ikke følger, her.» Ordet er «Mest omsatt», aldri «ukens beste».
8. **Søk mens man skriver.** *Forslag:* teksten filtrerer radene i nettleseren mens man skriver, på ticker og navn. Det ligger i `hjelp.js`, fordi sidene bare har det ene skriptet (8.0f). Uten skript gjør knappen «Vis» det samme på serveren, og bransjen og omsetningen er et vanlig skjema som virker uten skript. Valg av bransje eller omsetning sender skjemaet med en gang når skriptet kjører.
9. **Steg 1 i Min liste.** Utdraget har lenken «Åpne eodhd.com». *Forslag:* adressen står som tekst, som i 2.12, fordi sidene ikke har adresser til nettet (kontrollpunktet i `test_hjelpetekster.py`).
10. **Steg 3 i Min liste.** *Forslag:* kortet har kallene regnet av lista (flyttet fra «Følg flere aksjer») og to knapper: «Start fra en ferdig liste» (het «Velg en bransjeliste» før tillegg 3), som går til delen med samme navn, og «+ Følg en aksje». Når lista er full, står «Lista er full» i stedet for den andre knappen.
11. **Migrasjon.** *Forslag:* ingen. Bransjen står fortsatt i `oenske.sektor` og `aksje.sektor`, og ingen tabell endres. Storyen kan derfor flettes når som helst etter gruppens ja (steg 2 i instruksjonen).

## Delene

### A. Faste bransjer

`BRANSJE` i `src/ferdige_lister.py` får bransjen fra CSV-fila for alle de 295. Linjene for HVLK og NRDE i demoen står som før. `bransjen(tilkobling, kode)` gir bransjen etter spørsmål 1 og 2. `POST /folg` tar bransjen derfra og bryr seg ikke om et felt i skjemaet. `ta_i_bruk` bruker den også (spørsmål 3). «Følge …?» viser bransjen med symbolet i stedet for nedtrekkslista. CSV-fila committes aldri.

**Før commit:** 295 ekte aksjer: Energi 57, Finans 50, Industri 34, Teknologi 32, Shipping 27, Helse 21, Sjømat 20, Materialer 17, Forbruk 15, Kraft 9, Eiendom 7, Konsum 4 og Telekom 2. sha256 av linjene «TICKER;Bransje», sortert og med `\n` etter hver, er `302e28433bf582ec9abad65ffde06c2dbcd533cd6130713990e2fa3ed0c6dec9`. Tallene og sha256 står i en test.

### B. Kontrollsjekken

`_bmad-output/planning-artifacts/bransjesjekk-2026-11-10.md`: fremgangsmåten, tallene, grunnene til at MULTI og SCOIN er ute, og ticker, bransje og kilde per aksje, uten selskapsnavn. En test sjekker at tabellen er lik `BRANSJE`.

### C. «Følg en aksje»

Hele lista som kan følges, med antallet, søk mens man skriver, filter på bransje (med symbolet) og målt omsetning, «Følg» på hver rad og «?». Tre forslag øverst etter spørsmål 7 (byttet ut med sorteringen i tillegg 3). En aksje uten måling merkes «ikke målt ennå». «Bytt ut» bruker den samme lista.

### D. «Din egen liste» i Min liste

Tre stegkort etter utdraget §2: en gratis nøkkel hos eodhd.com, nøkkelen limes inn ved oppstart og ikke i et felt på siden (AD-10, svaret 08.11 kl. 12:39), og aksjene velges med bransjelistene og «Følg en aksje», med kallene regnet av lista. Samme kort, kant og knapper som resten av siden.

## Grenser

- Webserveren skriver bare `oenske` (AD-3) og henter aldri (AD-10). Ingen kall, og `src/fetch_prices.py` kjøres ikke.
- Ingen rangering etter kursen eller signalet, og ingen anbefaling (NFR-06).
- Ingen kurser, volum eller målte omsetningstall fra kildene i sporede filer (regel 16). Kontrollsjekken har bare ticker, bransje og kilde.
- Tester bare med testbaser og demobaser i midlertidige mapper (regel 22).

## Tilleggene 10.11

- **Kl. 17:16, om demoen (gruppens svar kl. 15:57):** gruppen blir vurdert på demoen, så alt nytt skal kunne ses der uten nøkkel. «Demo Børs» har fått sju oppdiktede selskaper til (`demo.DEMOBOERSEN`), seks av dem med en oppdiktet måling (`DEMOMAALT`), med bransjen i navnet (`DEMOBRANSJE`). I demoen kan derfor 12 aksjer følges: Kraft har tre målte (forslagene) og én som ikke er målt, og alle fire valgene i filteret på omsetning gir treff. Siden sier «Demo Børs» i demoen, og stripa har merket «Eksempeltall». Steg 2 i «Din egen liste» sier i demoen at demoen ikke trenger nøkkel. Demoen har nå 11 bransjelister (var 9). Testene: `TestDemoen` i `test_foelg_en_aksje_8_22.py` og `test_demoen_viser_kortene_og_trenger_ingen_noekkel`. Bildene i PR-en og i `docs/appen/` er tatt fra demoen.
- **Kl. 17:46, om testene i kveld (gruppens svar kl. 17:42):** ingen pytest i dette vinduet før 2.13b er flettet eller klokka er 22:00, og ikke kl. 22:15–23:50.
- **Kl. 17:47:** vindu 4 ble lukket ved en feil. Tilstanden ble sjekket før arbeidet fortsatte (sesjonsloggen).

Spørsmål 7 er bygget med teksten «Velg en bransje, så står de mest omsatte du ikke følger, her, høyst tre.», fordi «de tre» er et ord ordlista har valgt bort (`VALGT_BORT` i `test_hjelpetekster.py`). Spørsmål 8 er endret etter gjennomgangen: et klikk på en bransje eller en omsetning sender skjemaet, men et piltrykk gjør det ikke; med tastaturet sendes valget med «Vis».

## Gjennomgangen 10.11

Gjennomgangen av `53ff012c..59a84ee4` ga 12 funn fra Blind Hunter, 14 fra Edge Case Hunter og 10 fra Verification Gap. Funn som er de samme, står på én rad.

| Funn | Grad | Utfall |
|---|---|---|
| BH1, ECH1, BH2, BH10, VG7 (forslagene skjules av søket eller filteret på omsetning) | høy | Rettet: forslagene skjules aldri (`rad(a, false)`), og testene teller bare forslag som vises. |
| BH4, ECH2 (hvert piltrykk sender skjemaet) | middels | Rettet: bare et klikk sender skjemaet. Spørsmål 8 er oppdatert. |
| BH3, ECH3, ECH4 (MULTI og SCOIN slipper inn via `aksje.sektor` eller et ønske fra før 8.22) | middels | Rettet: `UTE` i `ferdige_lister.py`. `bransjen`, `foelgbare` og `ta_i_bruk` avviser dem. Den ekte basen (lest med `mode=ro`) har ingen av dem i `aksje` eller blant de 3 ventende ønskene. |
| VG1 (skriptet er bare sjekket som tekst) | middels | Delvis rettet: testen sjekker nå at feltet lytter på `input`, at radene skjules og at bare et klikk sender skjemaet. Skriptet kjøres ikke i en nettleser i testene. Bildene er tatt med skriptet i Edge. |
| VG2 (intet bilde av «Følg en aksje») | middels | Rettet: `docs/appen/folg-en-aksje-demo.png`, i knappen i README-en, med avtrykk. |
| VG3 («aldri ekte navn» bare sjekket på tickere) | middels | Rettet: ingen navn fra `AKSJEUNIVERS` og ingen ekte ticker på seks demosider. Antallet sier «Demo Børs» i demoen. |
| VG4 (kallene i steg 3 er bare sjekket med tom liste) | middels | Rettet: test med én egen aksje (1 kall og 3 i margin). |
| BH5, ECH7 (skriptet og serveren søker ulikt) | lav | Rettet: `data-kode` og `data-navn` hver for seg, som `filtrer`. |
| BH6, BH7, VG7 (grensen på to steder, og 32 skrevet inn) | lav | Rettet: `Foelgbar.utenfor` og `OMSETNINGSFILTER` fra `GRENSE_MNOK`, og test på nøyaktig 32 MNOK. Hjelpeteksten sier 32 MNOK, som `dine_egne_aksjer`. |
| ECH8 (Æ, Ø og Å i feil rekkefølge) | lav | Rettet: `_norsk` i `ferdige_lister.py`, med test. |
| VG5 (en egen aksje som er tatt ut) | lav | Rettet: testen viser at den ikke røres. |
| VG6 (GET `/folg` skriver ikke) | lav | Rettet: `/folg` med filter, søk og bytte i `test_sidene_skriver_aldri`. |
| VG8, VG9 (ordlyden i spørsmål 7, Kilde-kolonnen, 157 og 53) | lav | Rettet: ordlyden står over, Kilde-kolonnen har bare seks kjente verdier, og docstringen forklarer 141 + 15 + MULTI = 157 og 52 + SCOIN = 53. |
| VG10 («Ville feilet hvis» mangler i to tester) | lav | Rettet. Byttet er også sjekket i forslagene og filterskjemaet. |
| ECH5, BH11 (medianene regnes ved hver GET `/folg`) | middels/lav | Står: lista viser omsetningen for alle, så den trengs. Klikkene laster ikke lenger siden ved hvert piltrykk (BH4). Ikke målt; spørsmål til gruppen. | *Besvart 11.11 kl. 14:29, se «Svaret kl. 14:29».*
| ECH14 (full liste viser «Følg» for alle) | lav | Avvist: med full liste og uten bytte viser `/folg` bare «Lista er full …» (den første grenen i `folg.html`). |
| BH8 (`fetchone()[0]` uten rad) | lav | Avvist: `egne_i_lista` velger fra `aksje` med `ut IS NULL`, så raden finnes, og en aksje som er tatt ut, er ikke med. |
| BH9, ECH6, ECH9 (avvisning og tom lista ved feil) | lav | Står: `Valglager.folg` avviser en ukjent kode først, og en base uten `boersliste` viser 0, som før 8.22. |
| ECH10, ECH11 (bransjen skrives om uten historikk) | lav | Står, som spørsmål 3. |
| ECH12 (demotickerne gjelder også i den ekte versjonen) | lav | Står: ingen av dem er på Oslo Børs 10.11. En ny notering med samme ticker vil få en oppdiktet bransje; spørsmål til gruppen. |
| BH12, ECH13 (`maalt` uten tidssone) | lav | Avvist for 8.22: `omsetning.maalt` skrives med tidssone av 2.13, og det samme gjelder `Valglager.omsetning` fra før. |

Ingen funn på middels eller over står åpne uten spørsmål. ECH5 er middels hos Edge Case Hunter og står som spørsmål 12 (regel 25).

## Flettingen av main 10.11

Instruksjonen kl. 20:43: main ble flettet inn da 2.13b var flettet (kl. 21:14), med 2.4, 2.6, 8.14, 8.7, 8.9 og 2.13b. Konfliktene var avtrykkene i `test_docker.py` og bildet av «Din egen liste». Avtrykkene er regnet ut på nytt, og alle bildene er tatt på nytt med DevTools-protokollen. «Følg en aksje» er 1368 px høy med «Vis meg rundt» fra 8.9 (var 1326), og «Din egen liste» er fortsatt 1628 px.

Testene for rettingene etter gjennomgangen ble kjørt først etter flettingen, på grunn av tillegget kl. 17:46. Én feilet: VG3-testen fant ingen kode på bekreftelsen «Følge …?», fordi koden står i det skjulte feltet og ikke i en lenke. Testen leser nå feltet. Bekreftelsen sa også «Aksje på Oslo Børs» i demoen, og sier nå «Demo Børs» som lista. Mutantene for rettingene ble fanget: forslagene skjules av søket igjen (`rad(a)`), ønsker for MULTI og SCOIN tas i bruk, `bransjen` slipper MULTI og SCOIN gjennom, og bekreftelsen sier «Oslo Børs» i demoen.

## Tillegg 4: steg 2 som på tavla

Svaret 10.11 kl. 22:50. Steg 2 er det samme kortet i demoen og i den ekte versjonen, med overskriften og teksten fra `designutdrag-2026-11-08.md` §2: «Lim inn nøkkelen din» og «Nøkkelen står på kontosiden hos EODHD. Den lagres bare på denne maskinen.»

**Avvik fra tavla:** tavla har feltet «API-nøkkel», knappen «Sjekk nøkkelen» og «Nøkkelen virker. 20 kall igjen i dag.». Webserveren rører aldri nøkkelen og henter aldri (AD-10, svaret 08.11 kl. 12:39), så der står i stedet en status regnet av siste henting:

- **Den ekte versjonen, etter en henting:** «Nøkkelen virker: siste henting 10.11 brukte 19 av 20 kall.» `valg.siste_henting` leser bare basen, uten kall og uten `.env`. Dagen er den siste i `kursserie.hentet` og `indeksserie.hentet`, i Europe/Oslo. Kallene er seriene som ble lagret den dagen, ett kall per serie. Et nytt forsøk som feilet, lagret ingen serie og telles ikke, og det gjør heller ikke målingen av omsetningen med bonuskvoten (2.13b). Den ekte basen ga 10.11 kl. 22:57 «10.11» og 19, lest med `mode=ro`, med samme sha256 før og etter.
- **Den ekte versjonen, før første henting:** «Ingen henting har gått ennå. Start den ekte versjonen med startskriptet: første gang spør det etter nøkkelen, og du limer den inn der. Aksjene hentes ved neste henting etter kl. 22.»
- **Demoen:** «Demoen trenger ingen nøkkel. Den viser oppdiktede selskaper og henter aldri.» på samme plass.

Under står «Slik bytter du nøkkel», med det startskriptet gjør (`start/start.ps1` og `start/start.sh`): «Slett det som står etter `EODHD_API_KEY=` i fila `.env` i mappa til appen. Neste gang den ekte versjonen startes, spør startskriptet etter nøkkelen og lagrer den nye. Siden her har ikke noe felt for nøkkelen.»

**Grense:** statusen sier at nøkkelen virket ved siste henting, ikke at den virker nå. Er nøkkelen slettet eller byttet etter hentingen, ser siden det ikke før neste henting. Dagen står i teksten, så en gammel henting synes.

Testene står i `test_din_egen_liste_8_22.py`. Kallene sammenlignes med kallene hentingen selv talte (`kjoer_23`). Det er også tester for siden uten henting, for at nøkkelen aldri leses, for dagen i Oslo og for demoen.

### Gjennomgangen av tillegg 4

Gjennomgangen av `a251c087..508a3a16` ga 3 funn fra Blind Hunter, 4 fra Edge Case Hunter og 4 fra Verification Gap. Rettingene endrer tekstene over. Det som står på siden nå:

- **Etter en henting:** «Nøkkelen virket ved siste henting 10.11, som brukte minst 19 av 20 kall.»
- **Før første henting:** «Ingen henting har lagret kurser ennå. Startes den ekte versjonen med startskriptet, spør det etter nøkkelen første gang, og hentingen går med en gang. Har den feilet, kan nøkkelen være feil: se «Slik bytter du nøkkel».»
- **«Slik bytter du nøkkel»** har fått en setning til: «Med Docker, eller uten startskriptet, skriver du den nye nøkkelen etter `EODHD_API_KEY=` selv og starter appen på nytt.»

| Funn | Grad | Utfall |
|---|---|---|
| BH1 («virker» i presens, men gjelder siste henting) | middels | Rettet: «Nøkkelen virket ved siste henting …». |
| BH2, ECH3 (seriene er ikke kallene: feilede kall, nye forsøk, bonuskvoten og to hentinger samme dag telles ikke) | middels | Rettet: teksten sier «minst», og `SisteHenting.serier` heter det det er. Test med to hentinger samme dag. |
| BH3, VG3 («20» skrevet i malen) | lav | Rettet: `valg.KVOTE`, med test. |
| ECH1, VG3 (startskriptet finnes ikke med Docker eller uten skriptet) | middels | Rettet: setningen for Docker og uten startskriptet, med test med `OSE_I_DOCKER=1`. |
| ECH2 (teksten uten henting peker feil vei når hentingen ved oppstart har feilet) | middels | Rettet: hentingen går med en gang ved oppstart (`docs/installasjon.md`), og teksten peker på byttet. |
| ECH4 (én verdi som ikke kan leses, gir «ingen henting») | lav | Rettet: verdien hoppes over. En feil i basen går til `_egne_regnet`, som skjuler delen som før. |
| VG1 (testen for AD-10 fanget bare `os.getenv`) | middels | Rettet: `os.environ` byttes med en spion, og testen fanger hver fil som heter `.env` og åpnes med `open` eller `Path.open`. |
| VG2 (`kjoer_23` lar alle kall lykkes) | middels | Delvis rettet: teksten sier «minst», så den stemmer også når et kall feiler, og testen med to hentinger viser at tallet ikke blir for høyt. Ingen test har et kall som feiler. | *Besvart 11.11 kl. 14:29, se «Svaret kl. 14:29».*
| VG4 (avtrykkene viser ikke at bildet viser statusen) | lav | Står: bildene ble tatt på nytt og sett på, som for de andre bildene, og bildet av «Din egen liste» viser demoboksen og byttet. |

VG2 er middels og bare delvis rettet, så den står som spørsmål 14 (regel 25). *Besvart 11.11 kl. 14:29, se «Svaret kl. 14:29».*

## Flettingen av main 11.11

Instruksjonen 11.11 kl. 11:56, steg 1: main ble flettet inn med 8.23, del A (`45111d53`). Konfliktene var `issues.md`, `docs/hjelp.md`, `app.py`, `_egne.html`, avtrykkene i `test_docker.py` og to bilder. Begge sider er beholdt: stegkortene fra 8.22 med kvoten i steg 1 og avsnittet «Følg flere aksjer» fra 8.23 (A7), kvoten fra tillegg 4 og tallene fra 8.23 i `app.py`, og setningen fra 8.23 om radene i hjelpen. Én test for den faste bransjen leste radene som `<li>` og leser nå tabellraden fra 8.23 (A1). Hele settet ga 5206, lik `--collect-only`, med den ene feilen rettet og fila kjørt på nytt. CI var grønn.

## Tillegg 3 og 5

Bygget etter svarene kl. 22:44 og 22:55, i fire deler med tester og mutanter, og så én gjennomgang av alle fire.

- **Del 1, sorteringen (`013d1974`):** kortet «Mest omsatt» er borte. `ferdige_lister.sorter` ordner «Mest omsatt først» etter median omsetning, med dem som ikke er målt, sist, «A–Å» etter navnet og «Bransje» etter bransjen i samme rekkefølge som filteret. Sorteringen er brikker i samme skjema som filteret (`sorter=`), og «Mest omsatt først» er valgt fra start. Siden og hjelpen sier at det ikke er en rangering etter kursen eller signalet (NFR-06).
- **Del 2, flere bransjer (`2dbe3a4d`):** bransjene er avkrysning (`bransje=` flere ganger), og omsetningen gjelder i tillegg. «Alle» er en lenke som tar bort bransjene. Det valgte er `--oransje`, som bryterne i Innstillinger og fanen fra 8.23, med tekst i blekk og hakemerket ✓ foran. Gult (`--gul-symbol`) brukes ikke.
- **Del 3, radene (`42ebdc5a`):** en tabell i samme kort med svart kolonnerad som på oversikten, med navnet og så tickeren og bransjeikonet under, omsetningen i en egen kolonne med dagen den ble målt, og «Følg» til høyre. Skriptet skjuler radene i tabellen mens man skriver.
- **Del 4, de ferdige listene (`05b527da`):** én knapp per bransje med ikonet og antallet, og én setning. Knappen går til `GET /ferdig-liste?bransje=…`, siden «Er du sikker?». Den viser aksjene, merket «Utenfor målingen», hvor mange som fjernes og et åpent tenkt kjøp (8.21), og leser bare. Ingenting byttes før «Bruk denne lista», som sender til `POST /ferdig-liste` som før.
- **Tillegg 5 (`66fff077`):** `folg-en-aksje-390-demo.png` (hele siden, 1573 px) og `notatene-brfe-390-demo.png` (bare delen `mine-notater`, 1354 px, fordi hele aksjesiden er for høy). De står i README-en etter de andre bildene ved 390 px og i «Mappestruktur», og avtrykkene er regnet ut på nytt. «Din egen liste» er nå 1454 px (var 1714) og «Følg en aksje» 1252 px (var 1368).

**Mutantene, alle fanget, med filene like HEAD etterpå:** sorteringen er «A–Å» fra start; «Mest omsatt først» med den laveste først; bare den siste bransjen i adressen gjelder; det valgte er gult; skriptet leter etter `li` i stedet for `tr`; «Følg» står i feil celle; `GET /ferdig-liste` bytter lista; «Er du sikker?» sier ikke hvor mange som fjernes; bare «Alle» får hakemerket (VG1).

### Gjennomgangen av tillegg 3

Gjennomgangen av `45111d53..05b527da` ga 14 funn fra Blind Hunter, 12 fra Edge Case Hunter og 12 fra Verification Gap. Rettingene står i `05cd01e4`.

| Funn | Grad | Utfall |
|---|---|---|
| ECH2 (`--oransje` er også fargen for 3 av 3 på oversikten) | middels | Står: svaret kl. 22:44 sa den oransje fargen fra bryterne og fanen, og hakemerket skiller det valgte fra 3 av 3. Funnet følger av svaret, så det står som spørsmål 15 (regel 25). |
| BH3, ECH1, VG8 (hjelpen sa piltastene også for avkrysningsboksene) | middels | Rettet: hjelpen og kommentaren i skriptet sier at bransjene krysses av med mellomrom, med test. |
| BH11, ECH1 («Vis» bare før 14 bokser) | middels/lav | Rettet: «Vis» står også under sorteringen. |
| BH5 (setningen i Min liste sa ikke at lista vises før noe byttes) | middels | Rettet: «Velger du en bransje, ser du lista før noe byttes, og …». NFR-06 står på «Er du sikker?». |
| VG1 (hakemerket var bare testet for «Alle») | høy | Rettet: testen leser hele velgeren, og mutanten ble fanget. |
| VG2, VG7, VG10, VG12 (fokus, tekstfargen, 390 px og høykontrast uten test) | høy/middels/lav | Rettet: tester for fokusrammen, `opacity: 0` uten `display: none`, tekst i blekk, `min-width: 0` og `forced-colors`. |
| VG3, VG4, VG5 (demoen bare sjekket gjennom adressen) | høy/middels | Rettet: demotester for brikkene, avkrysningen, «Alle», linja om omsetningen, de elleve knappene og «Er du sikker?», og tickerne på alle de elleve sidene er oppdiktet. |
| VG6 (`docs/hjelp.md` uten test) | middels | Rettet: test for sorteringen, NFR-06, mellomrom og «Er du sikker?». |
| VG9, BH14, ECH7 (de nye sidene utenfor rammetestene) | middels/lav | Rettet: «Følg en aksje» og «Er du sikker?» i demoen er med i `sidene` i `test_utseende.py`, og lenkene er lagt til i hvitelista. |
| ECH3, BH13 (bildene var ikke tatt på nytt i diffen) | middels | Rettet i `66fff077`. «Elleve bransjer» er sjekket mot demoen i en test. |
| BH1 (`aapne_kjoep` og `eksempeltall` sendes ikke fra ruta) | middels | Avvist: begge kommer fra context processorene, og bildet av siden viser både varselet om KVST og demoboksen. |
| BH2 (skriptet sender ikke for avkrysningsbokser) | middels | Avvist: skriptet lytter på `change` for hvert fieldset, også for avkrysning. Bildene er tatt med skriptet. |
| BH4 (`BRANSJENE.index` ved en ukjent bransje) | middels | Rettet: en ukjent bransje sorteres sist. ECH fant at assertene i `ferdige_lister.py` alt hindrer det. |
| ECH4 («Alle» tok med `feil=` og ukjente parametre) | lav/middels | Rettet: bare `q`, `omsetning`, `sorter` og `bytt`. Et søk som ikke er sendt, følger ikke med (lav, står). |
| ECH5, ECH6 («de 1 mest omsatte», ønskene som venter) | lav | Rettet: entall, egen tekst når ingen fjernes, og setningen om ønskene bare når noen venter, med test. |
| BH8, BH9, BH10, ECH12 (skjermlesere: skilletegn, hakemerket, tittelen, antallet) | lav | Rettet. |
| ECH10 (linja om omsetningen uten målte) | lav | Rettet: bare når minst én rad er målt. |
| ECH11 (gamle navn og tekster) | lav | Rettet. |
| BH6 (lista kan endre seg mellom «Er du sikker?» og POST) | lav | Står: POST regner lista på nytt, som før tillegg 3. Spørsmål 18. |
| BH7 (WAL og sammenligningen av fila) | lav | Står: testbasene bruker samme sjekk som `test_sidene_skriver_aldri` fra før. |
| BH12 (ingen linje for «A–Å» og «Bransje») | lav | Står: brikken som er merket, sier sorteringen. |
| ECH8 (`:has()` i eldre nettlesere) | lav | Står: stilarket brukte `:has()` for brikkene fra før. |
| ECH9 (390 px anslått) | lav | Avvist: bildet ved 390 px viser at tabellen får plass. «Bytt inn» med et langt navn er ikke målt. |
| ECH10 (tom børsliste), ECH12 (alle 13 valgt) | lav | Står. |
| VG11 (byttet med flere bransjer og sorteringen) | lav | Rettet: test. |

Funnet på middels som står åpent, er ECH2 (spørsmål 15, regel 25). *Besvart 11.11 kl. 14:29, se «Svaret kl. 14:29».*

## Spørsmål etter gjennomgangen

12. **Medianene ved hver visning av «Følg en aksje» (ECH5).** *Forslag:* som bygget. Lista trenger omsetningen for alle, og medianene regnes én gang per forespørsel, som på Min liste. Det er ikke målt hvor lang tid det tar med den ekte basen. *Besvart 11.11 kl. 14:29, se «Svaret kl. 14:29».*
13. **Demotickerne i den ekte versjonen (ECH12).** *Forslag:* som bygget, fordi ingen av dem er på Oslo Børs 10.11. Kommer en av dem på børsen, sjekkes bransjen på nytt.
14. **Et kall som feiler, i testen for statusen i steg 2 (VG2, tillegg 4).** *Forslag:* som bygget. Teksten sier «minst», så den stemmer også når kall feiler. En test med et kall som feiler og et nytt forsøk i `kjoer_23` kan legges til, men tester da hentingen mer enn siden. *Besvart 11.11 kl. 14:29, se «Svaret kl. 14:29».*
15. **Den oransje fargen på det valgte (ECH2, tillegg 3).** `--oransje` er også fargen for 3 av 3 på oversikten. *Forslag:* som bygget, fordi svaret kl. 22:44 sa fargen fra bryterne og fanen, og hakemerket skiller det valgte fra 3 av 3. Alternativet er en egen farge for «valgt». *Besvart 11.11 kl. 14:29, se «Svaret kl. 14:29».*
16. **Sorteringen fra start (tillegg 3).** *Forslag:* «Mest omsatt først», fordi den står først i svaret, med linja om at den ikke er en rangering etter kursen. Alternativet er «A–Å», som før tillegg 3.
17. **Rekkefølgen i «Bransje» (tillegg 3).** *Forslag:* bransjene i samme rekkefølge som brikkene i filteret (`valg.BRANSJENE`), og navnet innen hver bransje.
18. **Lista mellom «Er du sikker?» og «Bruk denne lista» (BH6).** *Forslag:* som bygget: POST regner lista på nytt, som før. Står siden åpen over kveldshentingen, kan lista bli en annen enn den som ble vist.

## Svaret kl. 14:29

| Spørsmål | Svar |
|---|---|
| 1–4, 6, 8–11, 13, 16–18 | Ja, som bygget. |
| 5, 7 | Bortfalt med tillegg 3. |
| 12 (ECH5, middels) | Tiden måles. Tar én visning over ett sekund, regnes medianene én gang per henting og huskes i minnet, uten migrasjon. Se «Spørsmål 12: tiden» nedenfor. |
| 14 (VG2, middels) | Testen for et kall som feiler og prøves igjen, legges til. Se «Spørsmål 14: et kall som feiler» nedenfor. |
| 15 (ECH2, middels) | Ja: det valgte står i oransje med hakemerket, som bygget. |

### Spørsmål 12: tiden

Målt 11.11 kl. 14:41 med koden i worktreen på `c294a1bc`, uten server (Flasks test-klient), mot en kopi av `data/db/ose.db` i en midlertidig mappe som ble slettet etterpå (regel 22). Skriptet ligger i scratchpad-mappa til økta (`maal_folg2.py`, sha256 `ade6a115d3c9d0b4…`):

- Kopien ble laget med SQLite-backup fra en skrivebeskyttet tilkobling, og bare når det ikke fantes noen `-journal`- eller `-wal`-fil.
- Skriptet sjekket med `assert` at appen ble lest fra worktreen og brukte kopien, og at hver visning hadde over 200 rader, like mange som antallet på siden.
- Det skrev bare ut tidene og linja for regel 22, også om noe feilet. Utskriften, ordrett:

```
visningene: 0.046 s, 0.014 s, 0.014 s
sha256 lik før og etter: True | den midlertidige mappa er slettet: True
```

- Den ekte lista er full (15 aksjer og 3 ønsker som venter), så `/folg` viser ingen rader, men regner dem likevel (ECH1). «Bytt ut» (`/folg?bytt=…`) gjør det samme arbeidet og viser hele lista, så det er den som er målt.
- Den første visningen tar lengst. Den sjekker også migreringen av kopien, og diskbufferen var varm etter kopieringen (ECH3, VG4). En kald disk etter en omstart er ikke målt.
- Tiden gjelder hele visningen, også at `_aksjene_i_lista` regnes to ganger per forespørsel, i medianene og i de ferdige listene (ECH4).
- Én visning tar langt under ett sekund, så medianene regnes fortsatt én gang per forespørsel, og ingenting huskes i minnet (svaret kl. 14:29). Tiden måles på nytt hvis `ferdige_lister.medianene`, `foelgbare` eller `_egne_regnet` endres (VG5).
- Den første målingen kl. 14:40 (på `8b90fb0f`, med `shutil.copy2`) ga 0,051, 0,016 og 0,017 s.

### Spørsmål 14: et kall som feiler

`test_et_kall_som_feiler_og_proeves_igjen_gir_minst` i `test_din_egen_liste_8_22.py`: DNB feiler i kveldens henting kl. 22:00 og hentes i et nytt forsøk kl. 22:30 samme dag (2.3b). Kallene telles i begge kjøringene: 16 og 1. Etter feilen sier steg 2 «minst 15» (15 serier, mens hentingen brukte 16 kall og lista har 16), og etter forsøket «minst 16» (16 serier, 17 kall).

Mutantene, alle fanget, med filene like HEAD (sha256) etterpå:
- `siste_henting` teller én for mye: fanget av den nye testen, `test_statusen_er_kallene_hentingen_brukte`, `test_to_hentinger_samme_dag_gir_minst` og `test_siste_henting_er_dagen_i_oslo`.
- Malen viser kallene regnet av lista (`egne.kall.sist`) i stedet for seriene (VG1): fanget av den nye testen.
- `siste_henting` mister seriene fra det nye forsøket: fanget av den nye testen og `test_siste_henting_er_dagen_i_oslo`.

### Gjennomgangen av svarene kl. 14:29

Gjennomgangen av `8b90fb0f..c294a1bc` og det første måleskriptet ga 10 funn fra Blind Hunter, 7 fra Edge Case Hunter og 8 fra Verification Gap.

| Funn | Grad | Utfall |
|---|---|---|
| BH1, VG1 (testen skilte ikke seriene fra kallene eller lista: alt var 16) | høy/middels | Rettet: testen sjekker statusen etter feilen (15) og etter forsøket (16), og mutanten der malen viser lista, ble fanget. |
| BH2, VG6, ECH2 (`assert KALL < brukt` var alltid sann, og kallene i første henting ble ikke talt) | middels/lav | Rettet: første henting kjøres i testen, og kallene telles (16 og 1). |
| BH3, ECH7 (kopien bare av hovedfila, og WAL) | middels/lav | Rettet: backup fra en skrivebeskyttet tilkobling, og ingen `-journal` eller `-wal`. Basen bruker vanlig journal (ECH). |
| BH4, ECH6, BH6 (ingen sjekk av at kopien og koden i worktreen ble brukt) | middels/lav | Rettet: `assert` på stien til appen og på `BASE_STI`, og commiten står over. |
| VG2 (skriptet skrev ut mer enn tidene) | middels | Rettet: målt på nytt, med bare tidene og linja for regel 22. Radene sjekkes med `assert`. |
| VG3 (målingen kan ikke etterprøves) | middels | Delvis rettet: utskriften står ordrett over, med navnet og sha256 for skriptet. Skriptet ligger i scratchpad-mappa, ikke i `malinger.md`. |
| BH5 (kilden er i scratchpad, og 14:29 mot 14:31) | middels | Står: 14:29 er svaret, og 14:31 er instruksjonen som ga det videre. Instruksjonen føres i dagsfila 11.11 med flettingen, som de andre. |
| VG8 (gamle tekster sa at ECH5, VG2 og ECH2 sto åpne) | lav | Rettet: «Besvart 11.11 kl. 14:29» ved hver av dem. |
| ECH1, ECH3, ECH4, BH7, VG4 (begrunnelsene for tidene) | lav | Rettet i teksten over. |
| BH8 (sha-sjekken ved feil) | lav | Rettet: i `finally`. |
| BH9 (`TESTING` uten `monkeypatch`) | lav | Rettet i den nye testen. |
| VG7 (mutanten bare som prosa) | lav | Rettet: testene er navngitt over. |
| VG5 (ingen test for grensen på ett sekund) | lav | Står: tiden måles på nytt ved endringer i medianene, som over. |
| BH10, ECH5 (samme kveld; et nytt forsøk etter midnatt fordeler seriene på to dager) | lav | Står: ECH fant at forsøket i testen er samme dag i Oslo og UTC. Etter midnatt sier steg 2 den nye dagen og bare seriene den dagen, og det er sant, men lite. |

Ingen funn på middels eller over står åpne.

## Flettingen

*Lagt til 2026-11-11:* 8.22 er flettet med PR #138 i `dcb0bc6f` kl. 16:04, låst til head-en `6b5b97b6` (main med 3.6 flettet inn), etter instruksjonen kl. 14:31 i `docs/ai-prompts/2026-11-11.md` og gruppens svar 11.11 kl. 14:29. Hele settet lokalt i fem deler før pushen: 5247, lik `--collect-only`, 0 feilet. CI var grønn på head-en (run 43043943092). README-en har del B under «Ekstra, ferdig» (svaret kl. 13:49). Lista «Ekstra, hvis tiden rekker» ble da tom og står ikke, mens setningen om regelen for det ekstra står.
