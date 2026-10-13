# Epic 8 Context: Tydelig for den som ikke har bygget den

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

En person utenfor gruppen skal forstå skjermbildene, markedsoversikten og
aksjedetaljen, uten hjelp, og designet skal være vurdert, ikke bare arvet fra
kravene. Epicen innfrir suksessmålet «Brukerutfall»: minst én person utenfor
gruppen gjennomfører hovedflyten og forklarer uoppfordret hvorfor en aksje
skiller seg ut, på under 5 minutter, før prosjektinnlevering. Etter
endringsforslaget 08.10 er Epic 8 den største epicen og oppfyller også FR-106–110,
FR-206, FR-207 og tilleggene til FR-101, FR-102, FR-201, FR-202 og FR-407.
Endringsforslaget 13.10 (godkjent av Marian kl. 12:46) la til 8.0e, 8.10b og
8.19, flere kontrollpunkter i 8.0c, 8.0d, 8.6, 8.9 og 8.15, og ny ordlyd i
FR-701, FR-703 og FR-704. Ingen ny epic: faglærer ba 06.10 om at antall epics
ikke vokser. *Status 13.10:* 8.0 står i review, 8.0b er ferdig (PR #29), 8.0c er
i arbeid, resten er backlog.

## Stories

- Story 8.0: De rene feilene i de to skjermbildene
- Story 8.0b: Hjelp bak et spørsmålstegn
- Story 8.0c: Tydelig merking, ord ved sjekkene og datoer på grafen
- Story 8.0e: Oversikten fra designforslaget
- Story 8.0d: Utseendet fra designforslaget
- Story 8.1: Brukertest rett etter Epic 2
- Story 8.2: UX-gjennomgang av de to skjermbildene med `[CU] bmad-ux`
- Story 8.3: Min liste: eget skjermbilde med stjerne og filter
- Story 8.4: Se nærmere i aksjedetaljen
- Story 8.5: Endring i kroner, og høy og lav i aksjedetaljen
- Story 8.6: Børsometeret
- Story 8.7: Sjekk 2 og 3 i kursgrafen
- Story 8.8: Signaldager i kursgrafen
- Story 8.9: «Vis meg rundt»
- Story 8.10: Innstillinger øverst (med «Vis hjelp»)
- Story 8.10b: «Vis KI-tekst» i Innstillinger
- Story 8.11: Ferdige lister og filter på signalet
- Story 8.12: Endret signalstyrke siden forrige børsdag
- Story 8.13: Lær noe nytt
- Story 8.14: Justeringsdager i kursgrafen
- Story 8.15: Sortering ved klikk i kolonneraden
- Story 8.16: Regelen for startdagen, og periodene i kursgrafen
- Story 8.17: Periodevalget i oversikten, Min liste og børsometeret
- Story 8.18: Kommende eks.dato i kursgrafen
- Story 8.19: Neste henting i stripa øverst

## Requirements & Constraints

- **Oversikten har nøyaktig fem kolonner** (selskap, sluttkurs, endring,
  signalstyrke, retning). Alt nytt i oversikten (T/B/I, kroner, «var 1 mandag»)
  legges i cellene som finnes. Selskapsnavnet er lenken, og aksjedetaljen har en
  synlig vei tilbake.
- **Sortering:** styrke fallende, så absolutt endring; aksjer uten gyldig signal
  sist. Klikksortering (8.15) gjelder innenfor hver del når tabellen er delt.
- **Signalet regnes aldri på nytt.** Alt som viser en vurdering (T/B/I,
  signaldager, «Velg dag», endret styrke), leser den lagrede vurderingen. En
  børsdag uten rad er «ikke vurdert», en rad med grunn viser grunnen, og en dag
  som ikke er børsdag er «ikke børsdag».
- **En aksje skiller seg ut ved styrke på terskelen eller mer** (FR-705, i dag
  2). Terskelen hentes fra `Parametre`, aldri skrevet fast. En dag uten slike
  aksjer står setningen «Ingen aksjer skilte seg ut: ingen fikk 2 av 3 eller
  mer.», men ikke når ingen rad har vurdering.
- **Antall telles alltid** fra radene og lista, aldri fast 15. Lister testes
  også med færre enn 15 aksjer. Grensen for hele lista er 18.
- **Ny kravordlyd 13.10 (koden er fasit):** signalstyrken er hvor mange av de 3
  sjekkene som slo ut, ikke «hvor kraftig». Trend måles på utbyttejustert kurs.
  Retningen: Positiv = alle utslag +1, Negativ = alle -1, Blandet = noen +1 og
  noen -1, Ingen = styrke 0. Fotnoten under oversikten slutter med
  «Signalstyrken sier hvor mange av de 3 sjekkene som slo ut, ikke om du bør
  kjøpe eller selge.» Aksjesiden sier «Signalstyrken er hvor mange sjekker som
  slo ut:».
- **Hjelpetekstene** ligger i én fil (`src/hjelpetekster.py`), er fast tekst uten
  KI og nettkall, og tall i dem kommer fra `Parametre` med tester. Høyst 3
  setninger bak hvert «?», unntatt «Grensene» og «Hvorfor retningen oftere er
  positiv». «Vis meg rundt» har høyst 7 steg. Tekster fra designtavla brukes
  bare etter kontroll mot koden og PRD-en, med rettet ordlyd der endringsforslaget
  13.10 har rettet dem (for eksempel «kurs og volum», ikke «sluttkurs og volum»).
  Råd-ord («bør», «kjøp», «selg») er bare tillatt i «ikke_raad» og i malen.
- **NFR-05:** all brukervendt tekst norsk, med æ, ø og å. **NFR-06:** ingenting
  kan leses som råd om kjøp eller salg, eller som spådom; forbeholdet står synlig.
  **NFR-08:** et tall som mangler eller ikke består kontrollen, vises som «–» med
  grunnen. **FR-411 (fra 8.0c):** alt en visningsstory viser, vises også med
  demobasen, og en test krever det; «Eksempeltall» skal synes.
- **Tall og datoer** (regel 21): desimalkomma, hardt mellomrom som tusenskille og
  foran %, bindestrek som minus, antall desimaler i én funksjon med tester,
  aldri «-0,00». Tall med sifre («de 3 sjekkene»). Datoer som «22.09», med år
  bare når året er et annet. Formen bestemmes ett sted.
- **Ingen API-kall** fra noe i denne epicen, og ingen nettkall i tester. Hver
  story har en «Ville feilet hvis»-kontroll.
- **Brukertesten (8.1):** ekte data, tiden måles, forklaringen noteres ordrett,
  personen spørres aldri om hvorfor. Observeres også: er 15 rader for tett, og
  legger personen merke til indeksen og søylene. Funnene i `docs/` med dato.

## Technical Decisions

- **Kjernen er ren logikk** (`markedsoversikt.py`, `aksjedetalj.py`, `graf.py`,
  `signalberegning.py`), uten I/O og HTML. Malene under `src/templates/` bærer
  mye av visningskravene, så endringer treffer ofte både kjerne og mal.
- **Webserveren skriver bare egne små tabeller** (Min liste i 8.3, valgene i
  8.10/8.10b), hver med egen port og ny migrasjon, og henter aldri.
- **«bransje» der brukeren ser det, `sektor` i koden** (feltet `sektor` står).
  De 13 bransjene står som én konstant, og hver aksje har en av dem.
- **Gult betyr bare 3 av 3:** gul ring rundt pillen «3 av 3» i tabellen, gul
  ramme med hvit kant i børsometeret, gult bransjesymbol over søylen. Gjelder
  også når en annen dag eller periode vises. 2 av 3 merkes tydelig uten gult, og
  bare for siste børsdag. Det viktigste på siden merkes med fet skrift; sjekkede
  tall i KI-teksten har prikket strek i tekstfargen.
- **Skrift:** IBM Plex Sans til tekst og tall med tabelltall, Newsreader bare til
  overskrifter og titler. Hele skriftfiler med lisens (SIL OFL 1.1) i appen,
  ikke IBMs `split`-filer; ingen skrift eller skript fra nettet. Tester: ingen
  mal viser til nettskrift, tallcellene har tabelltall, filene har `tnum`. Tas
  inn i 8.0d.
- **Periodevalg, likt overalt:** første knapp («I går», «I dag» eller ukedagen),
  1 uke, 1 mnd, 3 mnd, 6 mnd, I år, 1 år, «Velg dag». Kursgrafen åpner med 6 mnd.
  Startdagen følger én skriftlig regel i én funksjon, skrevet i `designregler.md`
  §2 før koden (8.16).
- **Kursgrafen:** linja har lik avstand per børsdag, så månedsmerker plasseres på
  punktets x, ikke etter kalenderen. 50-dagers snittet er heltrukket; stiplet er
  bare hovedindeksen.
- **Låste signalparametre** (terskel 2, volumfaktor 1,5, nøytralsone ±2 %,
  vinduer 20, MA 50) endres ikke uten ny måling.

## UX & Interaction Patterns

- **Ordlista** (`designregler.md` §4, rettet 13.10) gjelder alle sider. Ord endres
  der, med dato og grunn. Valgt bort: «peker opp», «peker ned», «alle tre»,
  «kroner» (beløp skrives i NOK); en test leter etter dem i malene og hjelpen.
- **Sjekkene** heter trend (T), bevegelse (B) og interesse (I). I oversikten
  skrives de «T +1»; på aksjesiden står navnet og et ord: positiv ved +1,
  negativ ved -1, ingen utslag ved 0. Retning forklares med tall, ikke «peker
  hver sin vei».
- **Pilene er bare for retning.** Tilbakelenken har tekst uten pil, sortering
  vises med vinkler i den svarte kolonneraden, og «var 1 mandag» har ingen pil.
- **Oversikten etter 8.0e:** overskrift «N av M aksjer skilte seg ut <ukedag>»
  (børsdagen vurderingene gjelder), innledningen fra tavla med rettet ordlyd og
  tellede tall, «3 av 3» med navnene, «Slik leser du tabellen» med 3 punkter, og
  tabellen delt i «Skilte seg ut» og «Øvrige aksjer». «Dine egne aksjer» kommer
  med 2.12.
- **Utseendet (8.0d):** planen skriver reglene inn i `designregler.md` (farger,
  skrift, svart stripe øverst, kolonneraden, avstander, fokus, rekkefølgen av
  delene på hver side og det grå feltet) og gruppen godkjenner før bygging.
  Kontrast minst 4,5:1, og farger som skal skilles, skiller seg også i lyshet.
  Uten farger skal retning, endring og sjekkene stå som tekst, fortegn eller pil.
- **Ikke «v1.1» eller «(idé)»** i tekst brukeren leser. NewsWeb og Oslo Børs
  nevnes uten lenke; lenken går til selskapets investorside.
- **De 13 bransjene** (navn, med aksjene i lista i dag): Energi (EQNR, VAR, AKRBP,
  DNO), Finans (DNB, GJF), Industri (KOG), Materialer (NHY, YAR), Shipping (FRO,
  MPCC), Telekom (TEL), Sjømat (MOWI, SALM), Konsum (ORK), og nye uten aksjer:
  Forbruk, Teknologi, Helse, Eiendom og Kraft. Hver får et symbol (8.0d), brukt
  i børsometeret (8.6). En bransje med én aksje merkes «1 aksje».

## Cross-Story Dependencies

- **Rekkefølgen nå:** 8.0 → 8.0b + 8.0c → 8.0e → 8.0d, før KI-laget. 8.0d
  avhenger av 8.0b, 8.0c og 8.0e, så utseendet legges på den nye oversikten.
  8.19 avhenger av 8.0d for stripa. Plassen til 8.19, 8.10b og resten avgjøres
  etter README-prøven 13.–16.10.
- **8.1** krever 8.0b og 8.0c, og at 2.9 og 2.9b er ferdige. 8.2 kommer etter 8.1;
  8.3 står i dag som bygget etter 8.1 og før 8.2 (om det endres, avgjøres etter
  prøven). Epic 10.4 er en egen brukertest etter 8.1.
- **Epic 2:** 8.5 ← 2.10; 8.6 ← 2.9b; 8.8 og 8.12 ← 2.7; 8.14 ← 2.6; 8.18 ← 2.14
  og 2.6; 8.11 ← 2.12 og 2.13. 2.11 og 2.12 gir bransjen til nye aksjer, og 2.12
  gir «Dine egne aksjer».
- **Innad:** 8.16 → 8.17 (← 8.3 og 8.6) → 8.12 (← 8.3). 8.0b → 8.9 og 8.13; 8.9
  bygges etter sidene den viser. 8.10 ← 8.3 og 8.0b; 8.10b ← 8.10 og 10.3. 8.4 ←
  10.5, FR-104/FR-410 og 2.5; «Hva du kan sjekke selv» hører til 8.4.
- **Utbytte (2.15, N1)** kan endre merket under kursen i 8.14 til «utbytte» når
  EODHD-data har utbytte den dagen, ellers «justeringsdag». Føres etter prøven.
