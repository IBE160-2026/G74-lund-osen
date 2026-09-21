# Kilder og rettigheter

Oversikt over datakildene OSE Signal bruker eller har vurdert, hva vilkårene sier
om bruken vår, og når vi sist kontrollerte det. Formålet er at kildevalgene skal
være etterprøvbare, ikke bare dokumentert som «vi fant data».

**Premiss for v1:** applikasjonen kjøres lokalt i undervisningssammenheng og
publiseres ikke. Vurderingen gjelder derfor ikke-kommersiell, pedagogisk bruk.

**Men repoet er offentlig.** Kildekoden og planleggingsdokumentene ligger i
`IBE160-2026/G74-lund-osen`, som er åpent tilgjengelig. Applikasjonen er altså
ikke publisert, men arbeidet med den er. Skillet mellom hva som deles og hva som
blir liggende lokalt er derfor et valg vi må ta bevisst — se neste avsnitt.

Sist oppdatert: 2026-09-21

---

## Status per kilde

| Kilde | Brukes til | Vilkår kontrollert | Vurdering |
|---|---|---|---|
| EODHD `/api/eod` | Sluttkurser | **2026-09-20, fullstendig** | Gratisnivå dekker EOD for alle tickere, men bare ett år tilbake. 1 kall per symbol. |
| EODHD `/api/real-time` | — (forkastet) | 2026-09-19 | Virker, men prissiden sier gratisnivået ikke har det. Ikke bygg på. |
| EODHD `/api/news` | Relevanseksperimentet, én gang | **2026-09-20, fullstendig** | **Svarer for `.OL` på gratisnivå — testet 2026-09-21.** Forkastet for daglig drift: 5 kall per ticker, altså 75 for de 15 mot en dagsgrense på 20. Språkmodellbruk er **uklart** — se egen seksjon. |
| EODHD `/api/calendar` | — (utilgjengelig) | 2026-09-19 | HTTP 403: «Only EOD data allowed for free users». |
| Oslo Børs NewsWeb | Selskapsmeldinger | **Ikke kontrollert** | Åpent JSON-API, ferdig tagget med utsteder. Vilkår må sjekkes. |
| E24 RSS | — (forkastet) | 2026-09-19 | Forbyr eksplisitt LLM-input. Se under. |
| NRK RSS | — (forkastet) | 2026-09-20 | Avviser automatisert henting med HTTP 403. Generelle nyheter uten finansfokus. |
| Euronext | Finanskalender | Ikke kontrollert | Eneste gratis vei til kalender etter at EODHD falt bort. |
| Alpha Vantage | — (forkastet som hovedkilde) | Ikke kontrollert | Testet mot Oslo Børs, men symbolene var ikke pålitelige nok. Brukt i tidlige tester på gull og sølv. |

Mediekilder vurdert til relevanseksperimentet står i egen seksjon lenger nede, ikke i tabellen over.

---

## E24: forbud mot KI-bruk

E24s RSS-feed inneholder i sitt eget `<description>`-felt en klausul som forbyr
bruk av innholdet som input til språkmodeller. Sitat, hentet 2026-09-19:

> E24 does not permit any unlicensed use of the content referenced in this feed —
> including article headlines, summaries, links, full-text, images, metadata or
> other elements — for the purpose of training, fine-tuning, or evaluating, or
> providing input to large language models (LLMs), generative AI systems, or any
> automated systems that produce derivative or synthetic content.

Dette rammer direkte arkitekturen vi vurderte, der KI skulle avgjøre hvilket
selskap en artikkel faktisk handler om. Kilden er derfor forkastet, ikke fordi den
var teknisk utilstrekkelig, men fordi vilkårene ikke tillater bruken.

Andre norske finansmedier (DN, Finansavisen, Hegnar, Kapital) publiserer ikke
lenger åpen RSS, så spørsmålet om deres vilkår ble ikke aktuelt.

---

## EODHD: hva de fullstendige vilkårene sier

**Kontrollert 2026-09-20.** Kilde: `https://eodhd.com/financial-apis/terms-conditions`,
lest i sin helhet. Utgiver er Unicorn Data Services, 835 149 998 R.C.S. Lyon,
Frankrike — det avgjør hvilken lov som fyller ut det vilkårene ikke sier.

**Spørsmålet:** tillater vilkårene at innhold fra nyhets-API-et brukes som input
til en språkmodell?

**Svaret er uklart — verken ja eller nei.** Dokumentet har tretten seksjoner
(Definitions, Personal and Commercial Use of Information, Non-Refundable
Payments, Provision of Services, No Warranties, Access to the Services, Use of
Personal Information, Termination, Exclusion of Liability, Indemnity,
Assignment, Severability, Amendments), og **ingen av dem nevner språkmodeller**.
Søk i hele teksten gir null treff på *machine learning*, *artificial
intelligence*, *LLM*, *language model*, *train*, *neural*, *algorithm* og
*automated*. Det finnes heller ingen seksjon om opphavsrett eller
immaterielle rettigheter.

### Det som faktisk står

Den eneste seksjonen som regulerer hva vi kan gjøre med dataene, er *Personal
and Commercial Use of Information*. Sitert ordrett:

> A Non-Professional User is an individual who views or uses EOD Historical Data
> Information solely in a personal capacity for their own personal investment
> activities.

> Non-Professional Users are permitted to store, manipulate, and analyze the
> data for private, non-commercial purposes. However, they are prohibited from:
> Sharing access to their account with others, including within groups.
> Selling, reselling, retransmitting, redistributing, displaying, or granting
> access to the Information or Services, whether in its original or repackaged
> form.

De fire spørsmålene vi stilte, besvart mot denne teksten:

| Spørsmål | Svar i vilkårene |
|---|---|
| Klausul om KI, maskinlæring eller automatisert behandling | **Finnes ikke.** Null treff i hele dokumentet |
| Hva er lov å lagre, og hvor lenge | «store, manipulate, and analyze» er uttrykkelig tillatt for private, ikke-kommersielle formål. **Ingen tidsgrense og ingen cache-regel er oppgitt** |
| Er ikke-kommersiell eller pedagogisk bruk særskilt regulert | Delvis. «Non-Professional User» er definert ved *personal investment activities* — skolearbeid er ikke nevnt, verken som tillatt eller forbudt. Ingen akademisk klausul. «Universities & Academic — research licensing» finnes som eget salgsspor på nettstedet, ikke som vilkår |
| Forskjell på gratisnivå og betalte planer | **Vilkårene skiller ikke.** Samme tekst gjelder alle planer; forskjellen ligger i kvote og endepunktstilgang, ikke i bruksrett |

### Sammenligningen med E24

E24 har en klausul som forbyr bruken eksplisitt, i sitt eget `<description>`-felt.
EODHD har ingen klausul i noen retning. Det er to forskjellige situasjoner, og
de skal ikke føres likt:

| | E24 | EODHD |
|---|---|---|
| Ordlyd om språkmodeller | Eksplisitt forbud, sitert over | Ingen |
| Vår status | **Nei — dokumentert** | **Uklart — udokumentert** |

**Taushet er ikke tillatelse.** Men taushet er heller ikke det nei-et vi lette
etter tilsvarende av. Det vi kan si med belegg, er at vilkårene ikke inneholder
noe forbud som rammer bruken — ikke at de tillater den.

### Den bindende begrensningen er en annen enn den vi lette etter

Forbudet som faktisk står der, treffer noe vi ikke spurte om:

> …prohibited from: Selling, reselling, retransmitting, redistributing,
> **displaying**, or granting access to the Information or Services, whether in
> its original or **repackaged** form.

To konsekvenser:

1. **«Displaying»** er forbudt for Non-Professional Users. Lest strengt rammer
   det å vise EODHD-kurser til andre — altså demonstrasjonen. Lest i
   sammenheng handler seksjonen om å gi andre tilgang til dataene, ikke om å
   vise en skjerm i et klasserom. Vi vet ikke hvilken lesning EODHD står for.
2. **«Repackaged form»** treffer publiseringsskillet i avsnittet over. Vår
   posisjon er at aggregert statistikk ikke er datasettet. Ordet «repackaged» er
   det nærmeste vilkårene kommer å si noe om det, og det trekker motsatt vei.
   Posisjonen er fortsatt forsvarlig — en median er ikke en kursserie — men den
   har nå en ordlyd mot seg, og ikke bare fravær av ordlyd.

Begge deler er argumenter for å spørre EODHD skriftlig, ikke bare for å lese
videre.

### Målt fra dokumentasjonen samtidig

Hentet 2026-09-20 fra `/financial-apis/financial-news-api` og
`/financial-apis/api-limits`:

> Each request consumes 5 API calls and 5 API calls per ticker. E.g: 10 API
> calls for one request with two tickers

**Rettet 2026-09-21 etter måling.** Setningen ble 20.09 lest som «10 kall for
én ticker — 5 for forespørselen og 5 for tickeren». Den lesningen stemmer ikke
med eksempelet i setningen selv, som sier 10 kall for *to* tickere; med 5 pluss
5 per ticker skulle to kostet 15.

Målingen avgjorde det: én forespørsel med én ticker flyttet `apiRequests` fra 0
til 5. **5 kall per ticker**, med forespørselen selv som gulv. Målemetode og
tall står i `malinger.md` §7.2.

For åtte selskaper blir det ~40 kall, ikke 80. Anslaget på 80 står fortsatt i
`prd.md` og `begrunnelser.md` og er ikke rettet der — se punktet nederst.
Konklusjonen om daglig drift endres ikke: 15 tickere er 75 kall mot en
dagsgrense på 20.

> Free plan — 20 API calls per day. Enough to try the endpoints out, not to run
> an application.

Og om hva gratisnivået faktisk gir tilgang til:

> Register for the free plan to receive your API key (limited to 20 API calls per
> day) with access to End-Of-Day Historical Stock Market Data API for any ticker,
> but within the past year only.

Alle datatyper er tilgjengelige **bare for seks demo-tickere** (AAPL.US, TSLA.US,
VTI.US, AMZN.US, BTC-USD.CC, EURUSD.FOREX). Sammenholdt med HTTP 403-svaret vi
selv målte på `/api/calendar` — «Only EOD data allowed for free users» — pekte
dette mot at nyhets-API-et ikke svarte for `.OL`-tickere på gratisnivå i det
hele tatt.

**Testet 2026-09-21: det stemte ikke.** Én forespørsel på `DNB.OL` ga HTTP 200
og ti artikler. Gratisnivået gir `/api/news` for norske tickere, og 403-svaret
på `/api/calendar` kan ikke generaliseres til de andre endepunktene. Måling og
rådatareferanse: `malinger.md` §7.2.

### Konklusjon

**Uklart.** Vilkårene forbyr ikke språkmodellbruk, og de tillater den ikke.
Åpent punkt 1 kan ikke lukkes på grunnlag av lesningen alene.

Det som må til for å gjøre svaret til ja eller nei, er et skriftlig svar fra
`support@eodhistoricaldata.com`.

### Spørsmålet er sendt

**E-post sendt 20.09.2026** til `support@eodhistoricaldata.com`, med **ett**
spørsmål: om artikkeltekst fra `/api/news` kan sendes til en tredjeparts
språkmodell for klassifisering, i et ikke-kommersielt studentprosjekt der
resultatet ikke publiseres eller videreformidles.

**Svar avventes. Frist satt til fredag 2026-09-25.**

De tre øvrige spørsmålene i utkastet ble ikke sendt: om «displaying» rammer en
demonstrasjon i undervisning, om aggregert statistikk i et offentlig repo er
Informasjonen «in repackaged form», og om gratisnivået gir tilgang til
`/api/news` for `.OL`-tickere. De to første står fortsatt ubesvart og gjelder
demonstrasjonen og publiseringsskillet. Det tredje er avgjort av nyhetstesten
2026-09-21: gratisnivået dekker `/api/news` for `.OL`.

---

## Mediekilder vurdert for relevanseksperimentet

**Sjekket 20.09.2026.** Relevanseksperimentet skulle måle symbolmatching mot
KI-klassifisering på omtrent 50 medieartikler. Det forutsetter en mediekilde vi
har lov til å sende inn i en språkmodell. Seks kilder er vurdert.

| Kilde | Status | Hvorfor |
|---|---|---|
| E24 | **Avvist** | Åpen RSS med børsstoff, men feeden forbyr eksplisitt bruk som input til språkmodeller |
| Finansavisen / Hegnar | **Avvist** | Ingen lisensvilkår oppgitt, og stoffet ligger i hovedsak bak betalingsmur |
| NRK | **Avvist** | Avviser automatisert henting med HTTP 403 |
| NTB Kommunikasjon | **Avvist** | Ingen vilkår eller API dokumentert, og det er pressemeldinger — ikke medieartikler |
| finans.no | **Avvist** | Åpen RSS uten synlige restriksjoner, men dekker privatøkonomi, ikke børsnoterte selskaper |
| Feedly | **Avvist** | API-vilkårene forbyr masseimport og -eksport uten eksplisitt tillatelse |

### E24

Åpen RSS på `https://e24.no/feed/rss/`, med børsstoff. Feeden inneholder i sitt
eget `<description>`-felt en klausul som forbyr bruk av innholdet — overskrifter,
sammendrag, lenker, fulltekst og metadata — som input til store språkmodeller og
generative KI-systemer. Klausulen er sitert ordrett i seksjonen «E24: forbud mot
KI-bruk» over.

Lisenshenvendelser går til `nyhetssjefer@e24.no`. Kilden er altså ikke stengt for
alltid, men den er stengt for oss uten en avtale vi ikke har tid til å inngå før
uke 41.

### Finansavisen / Hegnar

`hegnar.no` omdirigerer til `finansavisen.no`. `robots.txt` har ingen
KI-spesifikke regler og oppgir `crawl-delay` på 10 sekunder. Ingen lisensvilkår
er oppgitt noe sted.

**Fraværet av et forbud er ikke en tillatelse.** `robots.txt` regulerer
høflighet i henting, ikke hva innholdet kan brukes til etterpå, og den er ikke
en lisens. Dette er samme resonnement som ble brukt på EODHD i seksjonen over:
taushet er ikke tillatelse. Stoffet ligger dessuten i hovedsak bak betalingsmur,
så spørsmålet om lovlig henting kommer før spørsmålet om lovlig bruk.

### NRK

Avviser automatisert henting med HTTP 403. Spørsmålet om vilkår ble derfor aldri
aktuelt — kilden svarer ikke.

### NTB Kommunikasjon

Publiserer pressemeldinger åpent, men ingen vilkår og intet API er dokumentert
på nettstedet.

Viktigere er sjangeren: dette er **pressemeldinger, ikke medieartikler**. Det er
samme sjanger som NewsWeb allerede gir oss gratis og med avklart
utstederkobling. Kilden ville ikke gitt eksperimentet det det mangler.

### finans.no

Åpen RSS uten synlige restriksjoner — den eneste av de seks som ikke stoppes av
vilkår. Men den dekker privatøkonomi: lån, sparing og forbruk, ikke
børsnoterte selskaper. Feil type kilde til dette formålet.

### Feedly

API-vilkårene forbyr masseimport eller -eksport av innhold uten eksplisitt
tillatelse, og en innsamling av 50 artikler er nøyaktig det.

Feedly ville dessuten lagt **en andre usikker lisens oppå utgiverens**. En
aggregator gir ikke rettigheter utgiveren ikke har gitt, så vi ville sittet med
to vilkårssett å svare for i stedet for ett.

### Konklusjon

**Det ble ikke funnet noen norsk mediekilde med åpen feed og vilkår som tillater
å sende innholdet inn i en språkmodell.**

De seks kildene faller på fire forskjellige grunner — eksplisitt forbud,
manglende vilkår, teknisk avvisning og feil sjanger — og det er verdt å merke
seg at bare én av dem, E24, faktisk har tatt stilling til spørsmålet. De andre
har ikke sagt nei; de har ikke sagt noe.

---

## Oslo Børs NewsWeb

```
https://api3.oslo.oslobors.no/v1/newsreader/list?category=&issuer=&fromDate=ÅÅÅÅ-MM-DD
```

Offisielle børsmeldinger. Ett døgn (15.09.2026) ga 102 meldinger fra 73 utstedere.
Hver melding har `issuerSign`, `issuerName`, `category`, `publishedTime` og `title`.

Tre forbehold vi må følge opp:

1. **Vilkårene er ikke kontrollert.** API-et er udokumentert og er backend-en til
   Oslo Børs' egen nettside, ikke et publisert utvikler-API.
2. **Ingen garanti for stabilitet.** Det kan endres eller stenges uten varsel.
   Vi lagrer derfor rådata lokalt fra første henting.
3. **Oslo Børs eies av Euronext.** Vilkårene for NewsWeb og for finanskalenderen
   henger derfor trolig sammen, og må kontrolleres under ett.

Meldingene er allerede knyttet til utsteder. Det betyr at KI ikke brukes til å
avgjøre hvilket selskap en melding gjelder — den jobben gjør `issuerSign`. KI
brukes først etter at kategorifiltrering i vanlig programkode har luket bort
støyen, og da til å forklare innholdet på norsk.

---

## Hva vi publiserer, og hva vi ikke publiserer

Besluttet 2026-09-20, da det ble bekreftet at repoet er offentlig i
IBE160-organisasjonen.

Skillet går mellom **aggregert statistikk utledet av en kilde** og **selve
datasettet**.

| Publiseres i repoet | Blir liggende lokalt |
|---|---|
| Median daglig omsetning per symbol | Kursseriene fra EODHD |
| Kategorifordelinger i meldingsbildet | Meldingene fra NewsWeb |
| Kalltall, kvoteforbruk og måleresultater | Alt innhold i `data/` |
| Metodebeskrivelser og konklusjoner | |

`data/` ligger i `.gitignore`, sammen med `.env`. Rådata og API-nøkler er derfor
ikke eksponert.

**Kontrollert 20.09.2026.** Hele repoet ble gjennomgått for kildedata som ligger
slik de kom fra leverandøren:

- Ingen fil under `data/` har noen gang vært sporet — ikke i HEAD, og ikke i noen
  commit i historikken. Kontrollert på objektnivå, ikke bare mot filnavn.
- Ingen sporet fil inneholder rålinjer fra EODHD eller NewsWeb: ingen
  `issuerSign`, `publishedTime` eller `adjusted_close`, og ingen JSON-blokker i
  dokumentene.
- Det som ligger offentlig av målinger, er utledede tall med metode og dato —
  medianomsetning per symbol i `malinger.md` §1, kategorifordelinger i §4,
  kalltall i §2.

Det betyr at en historikkomskriving ikke er nødvendig. Det finnes ingenting å
fjerne, og ingen commit å skrive om.

Mønsteret som gjorde dette mulig, er verdt å notere: `data/` ble gitignorert før
den første målingen ble kjørt. Rådata har aldri vært innom en commit, og da
trengs ingen opprydding. `.gitignore` er utvidet med mønstre for rådatafiler som
måtte havne utenfor `data/`.

**Begrunnelsen:** sammendragsstatistikk er ikke databasen. At medianomsetningen
for et symbol var 34,7 MNOK over en gitt periode, er et resultat vi har regnet
ut — det gjenskaper ikke kursserien det er regnet på, og det setter ingen i
stand til å omgå kildens egne vilkår. Det samme gjelder at en kategori utgjorde
28,9 % av meldingene i en måleperiode.

**Dette er en forsvarlig posisjon, men den skal stå som et bevisst valg.**
Slik det er nå, følger skillet av at `data/` tilfeldigvis ble gitignorert tidlig
i prosjektet. Det er ikke godt nok som begrunnelse. Regelen er herved skrevet
ned, og den gjelder også for filer vi lager senere: et måleresultat kan
publiseres, et datasett kan det ikke.

Posisjonen er ikke en erstatning for vilkårskontrollen. Den sier hva vi gjør i
mellomtiden, ikke at vilkårene tillater det.

---

## Å følge opp

- [ ] **Euronext samlet:** kontrollere bruksvilkårene for NewsWeb-data og for
      finanskalenderen i samme runde. Oslo Børs er en del av Euronext, så de to
      kildene deler sannsynligvis vilkår.
- [ ] Kontrollere Alpha Vantage sine vilkår for ikke-kommersiell bruk
- [x] ~~Lese EODHDs fullstendige ToS, ikke bare prissiden~~ — gjort 2026-09-20,
      se seksjonen «EODHD: hva de fullstendige vilkårene sier». Svaret er uklart
- [x] ~~Spørre `support@eodhistoricaldata.com` skriftlig om språkmodellbruk~~ —
      **sendt 20.09.2026**, svar avventes, frist 2026-09-25
- [ ] **De to gjenstående spørsmålene til EODHD ble ikke sendt:** om «displaying»
      rammer en demonstrasjon i undervisning, og om aggregert statistikk i et
      offentlig repo er Informasjonen «in repackaged form». Begge gjelder ting vi
      gjør allerede. Koster ingen kall. Frist 2026-09-27
- [x] ~~Verifisere om `/api/news` svarer for `.OL`-tickere på gratisnivå~~ —
      **gjort 2026-09-21. Ja:** HTTP 200 og ti artikler for `DNB.OL`. Testen
      kostet 5 kall, ikke 10. Se `malinger.md` §7.2
- [ ] Rette kalltallet for nyhets-API-et der det er ført videre: `prd.md` og
      `begrunnelser.md` anslår ~80 kall for relevanseksperimentets åtte
      selskaper, bygget på det doble tallet. Med 5 per ticker blir det ~40.
      Målingen dekker bare én ticker; 5 per ticker for flere er utledet av
      EODHDs eget eksempel, ikke målt. Koster ingen kall å rette
- [ ] Vurdere vilkårene på nytt dersom applikasjonen skal publiseres
- [ ] **Kontrollere at skillet over holder mot EODHDs og NewsWebs faktiske
      vilkår.** Posisjonen «sammendragsstatistikk er ikke databasen» er vår egen
      vurdering, ikke noe kildene har sagt. Tas i samme runde, frist 2026-09-27
