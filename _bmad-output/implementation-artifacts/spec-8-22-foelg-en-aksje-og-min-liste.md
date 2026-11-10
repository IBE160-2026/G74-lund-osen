---
title: 'Story 8.22: Faste bransjer, «Følg en aksje» med hele lista, og «Din egen liste» som tre steg'
type: 'feature'
created: '2026-11-10'
status: 'in-progress'
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
- **Kl. 13:54 og 14:53:** instruksjonen viser til dem, men ordlyden er ikke funnet i repoet eller i scratchpad-mappene 10.11 (regel 11). Storyen bygger på det instruksjonen sier om «Følg en aksje» og Min liste, og siterer dem ikke.

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
5. **Rekkefølgen i lista.** *Forslag:* etter navnet, aldri etter kursen, endringen eller signalet (NFR-06).
6. **Filteret på omsetning.** *Forslag:* fire valg: «Alle», «Over 32 MNOK», «Under 32 MNOK» og «Ikke målt ennå». Medianen er den samme som i bransjelistene og merket (8.11c).
7. **De tre forslagene.** *Forslag:* bare når en bransje er valgt. Forslagene er de tre med høyest median omsetning blant de målte i bransjen som ikke er i lista og ikke venter, med medianen som i bransjelistene. Uten valgt bransje står «Velg en bransje, så står de tre mest omsatte du ikke følger, her.» Ordet er «Mest omsatt», aldri «ukens beste».
8. **Søk mens man skriver.** *Forslag:* teksten filtrerer radene i nettleseren mens man skriver, på ticker og navn. Det ligger i `hjelp.js`, fordi sidene bare har det ene skriptet (8.0f). Uten skript gjør knappen «Vis» det samme på serveren, og bransjen og omsetningen er et vanlig skjema som virker uten skript. Valg av bransje eller omsetning sender skjemaet med en gang når skriptet kjører.
9. **Steg 1 i Min liste.** Utdraget har lenken «Åpne eodhd.com». *Forslag:* adressen står som tekst, som i 2.12, fordi sidene ikke har adresser til nettet (kontrollpunktet i `test_hjelpetekster.py`).
10. **Steg 3 i Min liste.** *Forslag:* kortet har kallene regnet av lista (flyttet fra «Følg flere aksjer») og to knapper: «Velg en bransjeliste», som går til «Start fra en ferdig liste», og «+ Følg en aksje». Når lista er full, står «Lista er full» i stedet for den andre knappen.
11. **Migrasjon.** *Forslag:* ingen. Bransjen står fortsatt i `oenske.sektor` og `aksje.sektor`, og ingen tabell endres. Storyen kan derfor flettes når som helst etter gruppens ja (steg 2 i instruksjonen).

## Delene

### A. Faste bransjer

`BRANSJE` i `src/ferdige_lister.py` får bransjen fra CSV-fila for alle de 295. Linjene for HVLK og NRDE i demoen står som før. `bransjen(tilkobling, kode)` gir bransjen etter spørsmål 1 og 2. `POST /folg` tar bransjen derfra og bryr seg ikke om et felt i skjemaet. `ta_i_bruk` bruker den også (spørsmål 3). «Følge …?» viser bransjen med symbolet i stedet for nedtrekkslista. CSV-fila committes aldri.

**Før commit:** 295 ekte aksjer: Energi 57, Finans 50, Industri 34, Teknologi 32, Shipping 27, Helse 21, Sjømat 20, Materialer 17, Forbruk 15, Kraft 9, Eiendom 7, Konsum 4 og Telekom 2. sha256 av linjene «TICKER;Bransje», sortert og med `\n` etter hver, er `302e28433bf582ec9abad65ffde06c2dbcd533cd6130713990e2fa3ed0c6dec9`. Tallene og sha256 står i en test.

### B. Kontrollsjekken

`_bmad-output/planning-artifacts/bransjesjekk-2026-11-10.md`: fremgangsmåten, tallene, grunnene til at MULTI og SCOIN er ute, og ticker, bransje og kilde per aksje, uten selskapsnavn. En test sjekker at tabellen er lik `BRANSJE`.

### C. «Følg en aksje»

Hele lista som kan følges, med antallet, søk mens man skriver, filter på bransje (med symbolet) og målt omsetning, «Følg» på hver rad og «?». Tre forslag øverst etter spørsmål 7. En aksje uten måling merkes «ikke målt ennå». «Bytt ut» bruker den samme lista.

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
| ECH5, BH11 (medianene regnes ved hver GET `/folg`) | middels/lav | Står: lista viser omsetningen for alle, så den trengs. Klikkene laster ikke lenger siden ved hvert piltrykk (BH4). Ikke målt; spørsmål til gruppen. |
| ECH14 (full liste viser «Følg» for alle) | lav | Avvist: med full liste og uten bytte viser `/folg` bare «Lista er full …» (den første grenen i `folg.html`). |
| BH8 (`fetchone()[0]` uten rad) | lav | Avvist: `egne_i_lista` velger fra `aksje` med `ut IS NULL`, så raden finnes, og en aksje som er tatt ut, er ikke med. |
| BH9, ECH6, ECH9 (avvisning og tom lista ved feil) | lav | Står: `Valglager.folg` avviser en ukjent kode først, og en base uten `boersliste` viser 0, som før 8.22. |
| ECH10, ECH11 (bransjen skrives om uten historikk) | lav | Står, som spørsmål 3. |
| ECH12 (demotickerne gjelder også i den ekte versjonen) | lav | Står: ingen av dem er på Oslo Børs 10.11. En ny notering med samme ticker vil få en oppdiktet bransje; spørsmål til gruppen. |
| BH12, ECH13 (`maalt` uten tidssone) | lav | Avvist for 8.22: `omsetning.maalt` skrives med tidssone av 2.13, og det samme gjelder `Valglager.omsetning` fra før. |

Ingen funn på middels eller over står åpne uten spørsmål. ECH5 er middels hos Edge Case Hunter og står som spørsmål 12 (regel 25).

## Spørsmål etter gjennomgangen

12. **Medianene ved hver visning av «Følg en aksje» (ECH5).** *Forslag:* som bygget. Lista trenger omsetningen for alle, og medianene regnes én gang per forespørsel, som på Min liste. Det er ikke målt hvor lang tid det tar med den ekte basen.
13. **Demotickerne i den ekte versjonen (ECH12).** *Forslag:* som bygget, fordi ingen av dem er på Oslo Børs 10.11. Kommer en av dem på børsen, sjekkes bransjen på nytt.
