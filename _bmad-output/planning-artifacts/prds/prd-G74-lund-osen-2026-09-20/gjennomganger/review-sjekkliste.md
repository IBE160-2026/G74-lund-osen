# Kvalitetsgjennomgang — PRD OSE Signal

Vurdert 2026-09-20 mot `prd-validation-checklist.md` (syv dimensjoner).
Grunnlag: `prd.md` og `malinger.md`.

**Vurdert på prosjektets egne premisser.** Ambisjonsnivået er «lukk det som
blokkerer koding» for et studentprosjekt med to personer, og kravet til
produktet er forklarbarhet, ikke treffsikkerhet. Følgende er derfor *ikke*
regnet som funn: de ti `[FORELØPIG]`-merkingene, de to `‹fylles inn›`-
plassholderne, de åtte åpne punktene i seksjon 8, og fraværet av
lanseringsmodenhet (drift, skalering, personvern, publisering).

---

## Samlet vurdering

PRD-en er uvanlig godt begrunnet for sin sjanger: nesten hvert tall er sporet
til en måling i `malinger.md`, og de vanskelige valgene (median mot
gjennomsnitt, kroner mot volum, nøytralsone, terskel 2 mot 3) er tatt åpent og
med det som ble gitt opp skrevet ned. Det som ikke holder, er **etterprøvbarhet
på utførelsessiden**: flere krav mangler en betingelse en utvikler kan teste
mot, to krav står i direkte motstrid om når og hvor ofte kurser hentes, ett krav
inneholder en betingelse som i praksis alltid er sann, og ett av de fem
v1-punktene i omfanget har ingen krav i det hele tatt. Analysen er ferdig;
kravspesifikasjonen er det ikke.

| Dimensjon | Vurdering |
|---|---|
| 1. Beslutningsklarhet | tilstrekkelig |
| 2. Substans over staffasje | sterk |
| 3. Strategisk sammenheng | sterk |
| 4. Ferdigkriterier | tynn |
| 5. Omfangsærlighet | sterk |
| 6. Nedstrøms brukbarhet | tynn |
| 7. Formtilpasning | tilstrekkelig |

---

## 1. Beslutningsklarhet — tilstrekkelig

Dokumentet tar stilling. Terskel 2 velges *fordi* terskel 3 gir syv tomme dager
av femten, og kostnaden sies høyt. OSEBX holdes utenfor med et regnestykke, ikke
med en henvisning til tid. Skjevfordelingen mot positiv retning får en
strukturell forklaring og en uttrykkelig beslutning om *ikke* å justeres nå.
Motmålene i seksjon 7 er ekte motmål — særlig «usikkerhetsmerking som aldri slår
til er et varsel» og «relevanseksperimentet skal avgjøre påstanden, ikke
bekrefte den». Dette er ikke et dokument som har glattet alt til nøytralt.

Det som trekker ned er at beslutningene ikke er festet til noen. Sju av åtte
åpne punkter har tom eierkolonne, og tre av dem blokkerer krav som skal
implementeres (FR-603, FR-701–705, FR-502). At punktene *finnes* er villet; at
ingen av dem har en person og de fleste heller ikke en dato, er noe annet.

### Funn

- **medium** Sju åpne punkter uten eier (§ 8) — punkt 2–8 har tom eierkolonne.
  Punkt 2 og 3 blokkerer krav som står i kø for implementasjon. *Fix:* sett
  initialer på punkt 2–8, ikke bare på punkt 1; det koster én linje og gjør
  tabellen til et arbeidsdokument i stedet for en liste.
- **medium** Fristen «før prosjektinnlevering» løser seg ikke opp (§ 7, § 8
  punkt 8, FR-407) — datoen for prosjektinnlevering er ikke fastsatt noe sted,
  og PRD-en erkjenner det selv i punkt 8. Konsekvensen er større enn punktet
  sier: suksessmålene «Brukerutfall» og «Fortsatt bruk» (inkludert terskelen «de
  to siste ukene») og kravet i FR-407 («må være oppfylt før demonstrasjonen») har
  da ingen målbar frist. *Fix:* sett en arbeidsdato med forbehold nå, for
  eksempel «antatt 2026-11-20, justeres når emnet publiserer datoen», slik at «de
  to siste ukene» og «før demonstrasjonen» kan regnes ut.
- **low** § 8 punkt 5 siterer 68 % positiv retning — det er tallet *uten*
  nøytralsone, altså fra konfigurasjonen som ble forkastet i FR-702. Den valgte
  utformingen gir 65,3 %. *Fix:* oppgi 65,3 % som hovedtall og 68 % som
  referanse.

---

## 2. Substans over staffasje — sterk

Det er lite furniture her. Begrunnelsen for KI-laget i § 4.3 er det tydeligste
eksemplet: påstanden «metadata skiller ikke betydning» hviler på tre uavhengige
målinger med konkrete eksempler som kan slås opp, ikke på en generell påstand om
at KI er nyttig. Avgrensningen etterpå — «det brukes ikke til å avgjøre hvilket
selskap en melding gjelder — den jobben gjør `issuerSign` bedre og gratis» — er
den typen selvbegrensning som skiller et reelt designvalg fra KI-staffasje.

NFR-ene er heller ikke boilerplate: de seks første kan alle spores til et krav,
en måling eller et suksessmål annet sted i dokumentet. Det finnes ingen
«systemet skal være skalerbart».

To innvendinger, begge små:

### Funn

- **low** NFR-07 gjentar FR-406 uten å legge til noe (§ 5) — begrunnelsen
  («NewsWeb er udokumentert backend», «står ikke tomhendt», «målinger kan
  etterprøves») er ordrett den samme som står i FR-406. Den *ville* lagt til noe
  hvis den utvidet rådatakravet til NewsWeb — se funnet under § 4 om at FR-406
  bare dekker kursdata. *Fix:* enten slå NFR-07 sammen med FR-406, eller la
  NFR-07 være stedet der NewsWeb-øyeblikksbildene faktisk kreves.
- **low** FR-203 er en innholdsfortegnelse, ikke et krav (§ 4.6) — alle fire
  kulepunktene peker videre til FR-706, FR-602 og § 6. Eneste nye informasjon er
  «med lenke til originalen på NewsWeb». *Fix:* behold lenkekravet som krav, og
  gjør resten til en ren oppsummeringsliste uten FR-nummer.

---

## 3. Strategisk sammenheng — sterk

Tesen er eksplisitt og bærer hele dokumentet: *kode og KI holdes fra hverandre,
regler sorterer, KI forklarer, og grensen er synlig i grensesnittet*. Den er
ikke bare et prinsipp i seksjon 1 — den avgjør FR-502 (regler på
kategorifeltet), FR-601 (bryteren er brukersynlig, ikke et utviklerflagg),
FR-602 (meldingene blir stående merket «ikke vurdert» så kontrasten er ærlig),
FR-706 (de tre sjekkene listes ved navn) og NFR-04. Prioriteringen følger tesen:
favorittmerking og flere tidsperioder er «hvis vi rekker», mens av/på-bryteren
er v1 — selv om favorittmerking er lettere å bygge.

Suksessmålene måler tesen, ikke aktivitet. «KI-bidrag måles i hva laget faktisk
skilte, ikke i hvor mange meldinger det behandlet» er nøyaktig det rubrikken
etterspør, og «Fortsatt bruk» som eget mål med egen terskel er et ærlig grep mot
adopsjonsteater.

Ingen funn som svekker vurderingen.

---

## 4. Ferdigkriterier — tynn

Dette er dimensjonen som avgjør om PRD-en kan bygges fra, og det er her den
svikter. Flertallet av de 34 kravene har en testbar konsekvens — FR-405, FR-501,
FR-701, FR-703, FR-704 og FR-102 er direkte kjørbare. Men et titalls krav mangler
en betingelse en utvikler kan teste mot, og to par av krav motsier hverandre om
noe så grunnleggende som når det hentes data.

### Funn

- **kritisk** FR-406 og FR-401 motsier hverandre om hentefrekvens, og
  motsigelsen sprenger kvoten (§ 4.1, NFR-01) — FR-406 sier at
  beregningsgrunnlaget «lastes ned på nytt ved hver kjøring», mens FR-401 sier
  at henting bare skjer «er lagrede data eldre enn siste børsslutt». Lest
  bokstavelig koster hver applikasjonsstart 15 kall. NFR-01 har 20 kall i
  døgnet. Andre oppstart samme dag tømmer kvoten, tredje feiler. Under utvikling
  startes applikasjonen tjue ganger om dagen. *Fix:* skriv om FR-406 til «lastes
  ned på nytt ved hver *henting*, aldri skjøtes på», og la FR-401 være det
  eneste stedet som avgjør *om* det hentes. Legg til en øvre grense for antall
  hentinger per døgn i NFR-01.
- **kritisk** FR-402 utløser gjentatte hentinger uten tak (§ 4.1) — kontrollen
  er riktig tenkt (sjekk `date`, ikke klokka), men konsekvensen er «hentingen
  prøves igjen ved neste oppstart», og kurser hentes *før* kontrollen kan gjøres.
  Starter gruppen applikasjonen kl. 17, 18 og 19 på en dag der EODHD publiserer
  19:20, er det 45 kall brukt på tre mislykkede kontroller. *Fix:* krev at et
  mislykket friskhetsforsøk registreres, at nytt forsøk samme døgn tidligst skjer
  etter et angitt intervall eller klokkeslett, og at det finnes et maksimalt
  antall forsøk per døgn.
- **kritisk** FR-405s siste betingelse er alltid sann (§ 4.1) — «returneres
  meldinger som er nyere enn `fromDate` selv om `overflow` er `false`, behandles
  også det som en ufullstendig henting». *Alle* meldinger i et intervall er
  nyere enn `fromDate`. Implementert bokstavelig regnes hver eneste henting som
  ufullstendig, og delingsløkka i samme krav terminerer aldri. Det som antakelig
  menes er: *er den eldste returnerte meldingen vesentlig nyere enn `fromDate`,
  mistenkes avkorting.* *Fix:* omformuler til «er eldste returnerte melding
  publisert etter `fromDate`, og intervallet inneholder kalenderdager uten
  meldinger foran den, behandles hentingen som ufullstendig», og angi en nedre
  grense for deling (for eksempel ett kalenderdøgn) så løkka terminerer.
- **høy** «Kommende finansielle hendelser» er i v1-omfanget uten et eneste krav
  (§ 2, FR-203, § 6) — funksjonen er ett av fem kulepunkter under «Inne i v1»,
  nevnes som et kulepunkt i FR-203 og som en rad i kildetabellen, men ingen av
  de 34 kravene sier hvilke hendelsestyper som vises, hvor langt fram, hvor ofte
  kalenderen hentes, hva som skjer når Euronext ikke svarer, eller hvor
  oppslagstabellen ticker↔selskap lever. En utvikler kan ikke bygge dette.
  *Fix:* ett krav, FR-204, med hendelsestyper, horisont, oppdateringsfrekvens og
  oppførsel ved manglende kobling.
- **høy** «Forventet børsdag» er udefinert, og ingen kilde gir handelskalenderen
  (FR-402) — hele kravet hviler på begrepet, men ingenting sier hvordan
  applikasjonen vet at 1. mai ikke er børsdag, eller hvordan halve handelsdager
  og norske helligdager håndteres. Euronext-kalenderen i § 6 er finansielle
  hendelser, ikke handelsdager. *Fix:* definer «forventet børsdag» operasjonelt
  — for eksempel «siste dag som ikke er lørdag, søndag eller dato i en fast liste
  over Oslo Børs-stengte dager, vedlikeholdt manuelt for prosjektperioden» — og
  legg lista i repoet.
- **høy** FR-705 innfører en driftskonsekvens som ingen andre krav kjenner
  (§ 4.4) — «nyheter hentes og KI-vurderes bare for selskapene som skiller seg
  ut (se 4.1)». Henvisningen løser seg ikke opp: ingenting i § 4.1 sier dette.
  FR-401 og FR-404 henter meldinger for hele universet, og tallene i «Resultat
  av filteret» (~1,3 KI-forklaringer per dag, ~0,5 til relevansvurdering) er
  regnet på alle 15 selskapene over fire uker — ikke på de ~5,4 som passerer
  terskel 2 per dag. Kravet motsier også FR-203, som lover børsmeldinger med
  KI-forklaring i aksjedetaljen for enhver aksje. I tillegg er premissen svak:
  NewsWeb koster ingen kvote, så det er ingen henteinnsparing i å begrense det.
  *Fix:* avgjør om begrensningen gjelder *henting* (bør droppes — gratis) eller
  bare *KI-vurdering* (forsvarlig, men da må anslagene regnes om, og FR-203 må
  si hva aksjedetaljen viser for en aksje som ikke skiller seg ut).
- **høy** FR-407 og FR-503 mangler regelen som kobler eks.dato til en dag
  (§ 4.1, § 4.2) — FR-503 sier at `EKS.DATO`-meldinger «føres til
  utbyttemerkingen», men ingen av kravene sier hvordan selve datoen utledes.
  Publiseringstidspunktet for meldingen er ikke det samme som eks.datoen, og
  datoen står i meldingsteksten. En utvikler har ikke nok til å implementere
  FR-407. *Fix:* angi hvor datoen hentes fra (felt eller tekstuttrekk), og hva
  som skjer når den ikke lar seg lese — merkes dagen da, eller ikke?
- **høy** Ingen av kravene dekker kaldstart (FR-401, NFR-02, NFR-03) — tre krav
  lover at «siste kjente data vises med tidsstempel» mens en henting pågår eller
  feiler. Ved aller første kjøring, og etter at noen har slettet lageret, finnes
  ingen siste kjente data. Ingenting sier hva markedsoversikten viser da.
  *Fix:* ett avsnitt i NFR-03 om tom tilstand: hva vises, og kan brukeren se at
  det ikke er en feil.
- **medium** Ingen krav dekker delvis mislykket henting (FR-406, NFR-03) —
  FR-406 forbyr å skjøte på beregningsgrunnlaget. Hva skjer når 8 av 15 symboler
  er hentet og kvoten tar slutt? Er lageret nå halvt nytt og halvt gammelt — som
  er nettopp skjøting — eller forkastes de 8? *Fix:* krev at en oppdatering av
  beregningsgrunnlaget er alt-eller-ingenting per symbol, og at symboler som
  ikke ble oppdatert beholder sitt forrige tidsstempel synlig i grensesnittet.
- **medium** FR-404 «på samme måte som kurser» peker på en oppførsel som ikke
  kan overføres (§ 4.1) — kurser etterfylles ved å laste ned hele serien på nytt
  (FR-406). Gjøres det samme med meldinger, treffer hver henting resultattaket
  på 557–601 og utløser delingsløkka i FR-405 hver gang. *Fix:* si at meldinger
  etterfylles *inkrementelt* fra siste kjente melding, og at meldinger — i
  motsetning til kurser — ikke skrives om bakover.
- **medium** Hentestrategien mot NewsWeb er ikke bestemt (FR-404, FR-405) —
  endepunktet har en `issuer`-parameter (`malinger.md` § 3), men ingen krav sier
  om det hentes per utsteder (15 kall, overflow treffer nesten aldri) eller for
  hele markedet med etterfiltrering (ett kall, overflow treffer fort). Valget
  avgjør om FR-405 i det hele tatt trengs i normal drift, og alle måletallene
  forutsetter det siste. *Fix:* skriv valget og begrunnelsen inn i FR-404.
- **medium** FR-501 mangler regelen for å kjenne igjen norsk (§ 4.2) — «den
  norske beholdes når begge finnes» forutsetter språkgjenkjenning som ikke er
  spesifisert, og NewsWeb-parameterne i `malinger.md` § 3 nevner ikke noe
  språkfelt. *Fix:* angi metoden — språkfelt hvis det finnes, ellers en enkel
  heuristikk på tittelen — og hva som gjøres når ingen av dem peker ut et språk.
- **medium** FR-501 kan slette ekte meldinger (§ 4.2) — nøkkelen «samme
  utsteder, samme kategori, samme publiseringsminutt» skiller ikke mellom en
  språkdublett og to ulike meldinger publisert samtidig. To flaggemeldinger fra
  samme utsteder i samme minutt er ikke usannsynlig. *Fix:* legg til at
  dubletter bare slås sammen når de også har ulikt språk, eller logg hver
  sammenslåing (FR-604 gir allerede loggmekanikken) så tapte meldinger kan
  ettergås.
- **medium** NFR-04 er formulert uten grense (§ 5) — «en treg eller
  utilgjengelig modell skal ikke forsinke eller stoppe markedsoversikten».
  *Treg* er et adjektiv, ikke en betingelse. Dette er den eneste NFR-en i settet
  som ikke kan testes. *Fix:* sett et tall — for eksempel «KI-kall avbrytes
  etter 20 sekunder, og meldingen vises da som uvurdert» — og bruk samme merking
  som FR-602.
- **medium** Hentevinduet for kursserien er ikke angitt (FR-201, FR-403, FR-406)
  — FR-201 krever seks måneders graf, `malinger.md` § 5 krever ~200 handelsdager
  for parameterlåsingen, gratisnivået gir ett år, og FR-406 laster ned serien på
  nytt hver gang. Ingen krav sier hvilken `from` kallene skal bruke. Velger
  utvikleren seks måneder, må parameterlåsingen kjøres som en egen jobb med
  annet vindu. *Fix:* sett `from` til ett år tilbake i FR-403 — det koster
  nøyaktig det samme, og da dekker samme nedlasting både grafen og
  parametertesten.
- **medium** FR-603 kjennetegn 3 dobler KI-kostnaden uten at noe krav rammer den
  inn (§ 4.3) — «om to kjøringer gir samme klassifisering» betyr at hver melding
  klassifiseres to ganger. Ingen NFR setter en ramme for KI-kostnad, antall kall
  eller modellvalg, slik NFR-01 gjør for EODHD. For et studentprosjekt med egen
  regning er det en reell mangel. *Fix:* en NFR-08 som setter et tak for KI-kall
  per døgn og navngir at kjennetegn 3 koster dobbelt.
- **medium** Ingen krav dekker håndtering av API-nøkler (§ 5) — EODHD og
  KI-leverandøren krever begge nøkler, repoet er et innleveringsrepo, og
  ingenting sier at nøkler holdes utenfor versjonskontroll. *Fix:* én NFR om at
  hemmeligheter leses fra miljøvariabel eller lokal fil som ikke sjekkes inn.
- **medium** Ingen krav dekker samme sak publisert av flere utstedere (§ 4.2,
  § 4.3) — PRD-en beskriver selv tilfellet: «den felles letemeldingen fra
  Equinor, Aker BP og Vår Energi, som ble publisert av flere utstedere i
  måleperioden». FR-501 dedupliserer bare innenfor samme utsteder, så saken vises
  tre ganger og forklares tre ganger av KI-laget. *Fix:* enten et krav om
  kryssutsteder-dedup på tittel, eller en uttrykkelig setning om at dette
  aksepteres i v1 — det siste er greit, men det må stå.
- **medium** NFR-07 krever rådatabevaring for NewsWeb, men FR-406 dekker bare
  kurser (§ 4.1, § 5) — FR-406 åpner med «Kursdata lagres i to atskilte lagre»,
  og hele tabellen handler om kursserier. NFR-07 henviser til FR-406 for
  NewsWeb-øyeblikksbilder som FR-406 aldri krever. Ingen krav pålegger altså
  faktisk at meldingssvar lagres rått. *Fix:* utvid FR-406s tabell med en rad
  for meldingssvar, eller gjør NFR-07 til det selvstendige kravet.
- **medium** FR-406 er i motstrid med sin egen begrunnelse (§ 4.1) —
  rådatalageret beskrives som «sikkerhetsnett» i begrunnelsen og i NFR-07, men
  regelen i tabellen sier «ikke beregningskilde». Et sikkerhetsnett som ikke kan
  brukes til å regne på, er ikke et sikkerhetsnett. *Fix:* avklar hva nettet
  faktisk gjør — antakelig «kan brukes til å gjenskape beregningsgrunnlaget
  manuelt, men leses aldri av applikasjonen i drift».
- **medium** FR-103 krever farge som obligatorisk kanal uten å oppgi farger, og
  mangler «Ingen» (§ 4.5) — tabellen har tre rader, men FR-704 definerer fire
  retninger og FR-101 lister «Opp, Ned, Blandet eller ingen» som kolonneinnhold.
  Hva vises ved styrke 0? Samtidig står det at «alle tre kanalene er
  obligatoriske», mens tabellen bare gir tekst og symbol — ingen farger er
  angitt, og tilgjengelighetsargumentet har ingen kontrastkrav bak seg. *Fix:*
  fjerde rad for «Ingen», og enten konkrete farger eller en nedgradering av
  farge fra obligatorisk kanal til «kan brukes som forsterkning».
- **low** FR-601 sier ikke hva som skjer med forklaringer som allerede er laget
  (§ 4.3) — slås bryteren av etter en kjøring der forklaringer er generert og
  logget (FR-604), skjules de da, eller vises de med et merke? FR-602 beskriver
  bare tilfellet der laget har vært av hele veien. *Fix:* én setning i FR-602.
- **low** FR-101 «nøyaktig fem kolonner» er ikke forsonet med FR-407 (§ 4.5) —
  utbyttemerkingen må vises et sted i markedsoversikten, og «nøyaktig fem»
  utelukker en sjette kolonne. *Fix:* si at merkingen vises inne i
  endringskolonnen.

---

## 5. Omfangsærlighet — sterk

Tredelingen «Inne i v1 / Hvis vi rekker / Utenfor v1» gjør reell jobb, og
listene er spesifikke nok til å være bindende — «brukerkontoer, innlogging og
personlig portefølje» og «statistisk studie av om signalene slår markedet» er
navngitte utelatelser, ikke generelle forbehold. Nedskaleringer gjøres åpent og
med kostnaden nevnt: favorittmerking flyttes ut i FR-102 *med* konsekvensen
skrevet inn («at brukerens egne aksjer havner tilfeldig i lista er akseptert i
v1»), og FR-202 forklarer hvorfor volatilitetsbånd og volumsøyler ikke tegnes.
Punkt 1 i § 8 er et forbilledlig blokkeringspunkt: hard frist, konsekvens ved
brudd («fem uker med bygging bortkastet»), og hvorfor det ikke finnes noen
reserveplan.

Tettheten av åpne punkter er høy, men stakes er lave og punktene er merket — det
er riktig avveining her, ikke en mangel.

### Funn

- **medium** Relevanseksperimentets datakilde er ikke i kildetabellen (§ 6, § 7)
  — målet krever «testsett på 50 medieartikler» innen uke 41, og medietesten
  17.09 brukte «nyhetstreff» fra en kilde som ikke står i § 6. E24 er forkastet
  på vilkår, og PRD-en sier selv at «andre norske finansmedier publiserer ikke
  lenger åpen RSS». Det er altså et suksessmål med frist om to uker som hviler
  på en kilde dokumentet ikke navngir eller har kontrollert vilkårene for.
  *Fix:* navngi kilden i § 6 med samme vilkårsstatus som de tre andre — eller
  før den som nytt åpent punkt med frist foran uke 41.
- **low** Tallet 50 i relevanseksperimentet er ikke begrunnet (§ 7) — motmålet
  sier at eksperimentet «skal avgjøre påstanden», men 50 artikler er ikke
  knyttet til hva som skal kunne avgjøres. *Fix:* enten en linje om hvorfor 50
  holder for prosjektets formål, eller en omformulering av motmålet til at
  eksperimentet skal *belyse*, ikke avgjøre.

---

## 6. Nedstrøms brukbarhet — tynn

PRD-en er en kjedetopp: den skal mate arkitektur og historieskriving, og seksjon
1 sier selv at den fastsetter «beslutningene som må være låst før
arkitekturarbeidet starter». Da teller denne dimensjonen fullt ut.

Seksjonene leses godt hver for seg, og kryssreferansene er stort sett ekte
(FR-702 → FR-703 → FR-101 henger sammen). Men det mangler en ordliste,
ID-rekkene er brutt, og det sentrale begrepet i suksessmålene er aldri definert.

### Funn

- **høy** «Hovedflyten» er udefinert, men bærer det viktigste suksessmålet
  (§ 7, NFR-03, NFR-04) — begrepet brukes fire ganger. Suksessmål «Brukerutfall»
  lyder «person utenfor gruppen gjennomfører hovedflyten … under 5 minutter,
  uten hjelp». Ingen steder står det hva hovedflyten *er*: hvilke skjermbilder, i
  hvilken rekkefølge, med hvilket startpunkt og sluttpunkt. Det gjør prosjektets
  ene brukerrettede suksessmål umålbart, og det er nøyaktig det en testperson
  skal settes til å gjøre. *Fix:* seks til åtte linjer i § 1 eller § 4.5 som
  beskriver flyten steg for steg — åpne, lese oversikten, klikke en aksje som
  skiller seg ut, lese de tre sjekkene, lese meldingene. Da får både suksessmålet
  og NFR-03/04 noe konkret å peke på.
- **medium** Ingen ordliste, og begreper som bærer krav er udefinerte (hele
  dokumentet) — «aksjedag» brukes i alle fordelingstallene i FR-702/FR-703 uten
  å defineres (symbol × handelsdag, antakelig 225 i testen). «Samlekategorien»
  brukes som et egennavn i FR-602 og § 4.3, men innføres bare i en begrunnelse og
  er aldri definert som `IKKE-INFORMASJONSPLIKTIGE PRESSEMELDINGER` på et sted et
  krav kan hente det fra. «Skiller seg ut» er definert i FR-705, godt, men brukes
  tidligere i § 1 og § 7. *Fix:* en kort ordliste med fem–seks termer: aksjedag,
  samlekategorien, skiller seg ut, hovedflyten, forventet børsdag,
  beregningsgrunnlag.
- **medium** ID-rekkene er brutt og følger ikke seksjonsrekkefølgen (§ 4) —
  blokkene er FR-4xx (§ 4.1), FR-5xx (§ 4.2), FR-6xx (§ 4.3), FR-7xx (§ 4.4),
  FR-1xx (§ 4.5), FR-2xx (§ 4.6). FR-3xx finnes ikke. Numrene teller altså
  nedover i andre halvdel av dokumentet, og et helt hundretall er hoppet over
  uten forklaring. Sorteres historier på ID nedstrøms, kommer markedsoversikten
  sist. *Fix:* enten renummerer i leserekkefølge, eller skriv én setning om at
  FR-1xx/2xx er grensesnittkrav og FR-4xx–7xx er datakrav, og at FR-3xx er
  reservert.
- **low** Ingen brukerreiser med navngitt protagonist (hele dokumentet) — for en
  kapabilitetsspesifikasjon er det forsvarlig (se § 7 nedenfor), men i
  kombinasjon med at «hovedflyten» er udefinert, står produktet uten noen
  sammenhengende beskrivelse av hva en bruker faktisk gjør. *Fix:* dekkes av
  hovedflyt-funnet over; en egen UJ-seksjon trengs ikke.

---

## 7. Formtilpasning — tilstrekkelig

Formen er riktig valgt. Dette er i praksis en kapabilitetsspesifikasjon for et
lite, lokalt verktøy med én brukerrolle, og PRD-en har ikke tvunget seg inn i
konsumentproduktformen med personaer, segmenter og brukerreiser den ikke
trenger. Mengden begrunnelse per krav er høyere enn vanlig, men her er det
riktig: for et studentprosjekt der refleksjonsrapporten er en del av leveransen,
er «hvorfor» selve produktet, og § 4.3 sier det uttrykkelig («denne begrunnelsen
hører også hjemme i refleksjonsrapporten»).

To forbehold. Det ene er at PRD-en *har* et brukerrettet suksessmål og en
demonstrasjon som skal bevitnes — og da trengs minimumet av brukerreise som
funnet under § 6 beskriver, selv om full UJ-formalisme ville vært overkill. Det
andre er at analysetyngden er skjevt fordelt: § 4.1–4.4 er gjennomarbeidet til
minste detalj, mens § 4.5 og § 4.6 — de to seksjonene som faktisk beskriver det
brukeren ser, og som skal demonstreres — er seks korte krav til sammen. Det er
den delen en sensor vil se først.

### Funn

- **medium** Grensesnittkravene er tynnere enn datakravene (§ 4.5, § 4.6) — seks
  krav dekker begge skjermbildene, og flere av hullene over ligger der (FR-103
  uten «Ingen», FR-101 mot FR-407, FR-203 uten eget innhold, ingen krav for
  finansielle hendelser). Ingenting sier hva som skjer ved klikk, hvordan man
  kommer tilbake, eller hva aksjedetaljen viser for en aksje uten meldinger.
  *Fix:* to–tre krav til i § 4.6: navigasjon, tom tilstand for meldingslista, og
  hva finanskalenderdelen viser.
- **low** FR-401, FR-406 og FR-502 beskriver mekanisme der de kunne beskrevet
  kapabilitet — «henting utløses når applikasjonen starter, ikke av en planlagt
  jobb», «to atskilte lagre», «grovsorteringen gjøres med regler i vanlig
  programkode». For FR-502 er dette forsvarlig: skillet kode/KI *er* produktets
  tese og skal være synlig. For FR-401 og FR-406 er det arkitekturvalg som låser
  løsningsrommet før arkitekturdokumentet skrives. *Fix:* behold dem, men flytt
  begrunnelsen om `adjusted_close`-omregning til et notat arkitekturen arver, og
  formuler kravet som «beregningsgrunnlaget skal alltid være en sammenhengende
  serie hentet i én operasjon» — mekanismen følger av seg selv.

---

## Mekaniske merknader

- **Terminologidrift på retning.** FR-704 bruker Positiv / Negativ / Blandet /
  Ingen. FR-101 sier at kolonnen inneholder «Opp, Ned, Blandet eller ingen».
  FR-103 oversetter Positiv → «Opp ↑». Tre navn på samme fire tilstander.
  Foreslått: FR-704 definerer de interne verdiene, FR-103 definerer
  visningstekstene, og FR-101 henviser til FR-103 i stedet for å liste egne ord.
- **Brutt kryssreferanse mellom dokumentene.** `malinger.md` § 4 avslutter
  tilbakekjøpsavsnittet med «Ført som åpent punkt 5 i PRD-en». I `prd.md` § 8 er
  det punkt 4; punkt 5 er skjevfordelingen. Rett i `malinger.md`, eller bytt til
  en henvisning uten nummer.
- **FR-705s «(se 4.1)» løser seg ikke opp.** Se funnet under § 4 — § 4.1 sier
  ingenting om at henting begrenses til aksjer som skiller seg ut.
- **FR-502-tabellens tall er før deduplisering.** Kravet står rett etter FR-501,
  som slår fast at dedupliseringen kjøres *først*. Summen i tabellen er 121,
  altså rådatatallet, mens resultattabellen like under bruker 89 som
  utgangspunkt. Utvikleren som tester filteret mot tabellen vil få andre tall.
  Sett inn en fotnote om at kategoritallene er før dedup.
- **Ingen funn på regnestykkene.** Fordelingene summerer til 100,0 % i begge
  kolonner i `malinger.md` § 5; FR-703 og FR-705 stemmer mot samme tabell;
  kategoritabellen i FR-502 summerer til 121; anslagene ~35 og ~13 lar seg
  utlede av 48 × 0,74 og 18 × 0,74. Sporbarheten fra PRD til målinger er i orden.
- **Tall uten begrunnelse.** To terskler i § 3 bærer vekt uten å være utledet:
  grensen på **25 MNOK** og kravet om **minst åtte sektorer**. Begge er
  etterprøvbare mot lista, men ingen av dem er begrunnet — og siden universet
  dekker nøyaktig åtte sektorer og laveste symbol ligger på 32,3 MNOK, leses
  kriteriene som en beskrivelse av en liste som allerede var valgt, ikke som en
  regel lista ble valgt av. Dokumentet sier heller ikke hvilket kandidatsett de
  15 ble valgt *fra*, så utvelgelsen kan ikke gjenskapes. To linjer retter dette:
  hvilke symboler som ble vurdert, og hvorfor 25 og åtte.
