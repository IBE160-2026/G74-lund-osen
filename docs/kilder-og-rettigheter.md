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

Sist oppdatert: 2026-09-20

---

## Status per kilde

| Kilde | Brukes til | Vilkår kontrollert | Vurdering |
|---|---|---|---|
| EODHD `/api/eod` | Sluttkurser | **2026-09-20, fullstendig** | Gratisnivå dekker EOD for alle tickere, men bare ett år tilbake. 1 kall per symbol. |
| EODHD `/api/real-time` | — (forkastet) | 2026-09-19 | Virker, men prissiden sier gratisnivået ikke har det. Ikke bygg på. |
| EODHD `/api/news` | Relevanseksperimentet, én gang | **2026-09-20, fullstendig** | Forkastet for daglig drift: 10 kall for én ticker (5 per forespørsel + 5 per ticker). Språkmodellbruk er **uklart** — se egen seksjon. |
| EODHD `/api/calendar` | — (utilgjengelig) | 2026-09-19 | HTTP 403: «Only EOD data allowed for free users». |
| Oslo Børs NewsWeb | Selskapsmeldinger | **Ikke kontrollert** | Åpent JSON-API, ferdig tagget med utsteder. Vilkår må sjekkes. |
| E24 RSS | — (forkastet) | 2026-09-19 | Forbyr eksplisitt LLM-input. Se under. |
| NRK RSS | — (vurdert) | Ikke kontrollert | Feeder virker, men generelle nyheter uten finansfokus. |
| Euronext | Finanskalender | Ikke kontrollert | Eneste gratis vei til kalender etter at EODHD falt bort. |
| Alpha Vantage | — (forkastet som hovedkilde) | Ikke kontrollert | Testet mot Oslo Børs, men symbolene var ikke pålitelige nok. Brukt i tidlige tester på gull og sølv. |

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

Nyhets-API-et koster altså **10 kall for én ticker** — 5 for forespørselen og 5
for tickeren. Ikke ett kall per ticker, som notatene våre har sagt. For åtte
selskaper blir det 80 kall, som er tallet gruppen anslo, men av en annen grunn
enn den vi trodde.

> Free plan — 20 API calls per day. Enough to try the endpoints out, not to run
> an application.

Og om hva gratisnivået faktisk gir tilgang til:

> Register for the free plan to receive your API key (limited to 20 API calls per
> day) with access to End-Of-Day Historical Stock Market Data API for any ticker,
> but within the past year only.

Alle datatyper er tilgjengelige **bare for seks demo-tickere** (AAPL.US, TSLA.US,
VTI.US, AMZN.US, BTC-USD.CC, EURUSD.FOREX). Sammenholdt med HTTP 403-svaret vi
selv målte på `/api/calendar` — «Only EOD data allowed for free users» — peker
dette mot at nyhets-API-et ikke svarer for `.OL`-tickere på gratisnivå i det
hele tatt. **Det er ikke verifisert.** Én testforespørsel mot en norsk ticker
avgjør det, og koster 10 kall.

### Konklusjon

**Uklart.** Vilkårene forbyr ikke språkmodellbruk, og de tillater den ikke.
Åpent punkt 1 kan ikke lukkes på grunnlag av lesningen alene.

Det som må til for å gjøre svaret til ja eller nei, er et skriftlig svar fra
`support@eodhistoricaldata.com`. Det koster ingen API-kall og bør sendes nå, med
tre spørsmål: om nyhetsinnhold kan brukes som input til en språkmodell i et
ikke-kommersielt studentprosjekt, om «displaying» rammer en demonstrasjon i
undervisning, og om aggregert statistikk utledet av dataene kan ligge i et
offentlig kodelager.

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
- [ ] **Spørre `support@eodhistoricaldata.com` skriftlig** om språkmodellbruk,
      om «displaying» rammer en demonstrasjon i undervisning, og om aggregert
      statistikk kan ligge i et offentlig repo. Eneste vei fra «uklart» til ja
      eller nei. Koster ingen kall. Frist 2026-09-27
- [ ] Verifisere om `/api/news` svarer for `.OL`-tickere på gratisnivå.
      Én testforespørsel, 10 kall
- [ ] Vurdere vilkårene på nytt dersom applikasjonen skal publiseres
- [ ] **Kontrollere at skillet over holder mot EODHDs og NewsWebs faktiske
      vilkår.** Posisjonen «sammendragsstatistikk er ikke databasen» er vår egen
      vurdering, ikke noe kildene har sagt. Tas i samme runde, frist 2026-09-27
