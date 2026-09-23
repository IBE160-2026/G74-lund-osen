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
| EODHD `/api/news` | Relevanseksperimentet, én gang | **2026-09-21, med skriftlig svar** | **Svarer for `.OL` på gratisnivå** (testet 21.09). **Språkmodellbruk er klarert med betingelser** — skriftlig godkjenning 21.09, se egen seksjon. Betingelsene er ikke oppfylt før modelltjenestens treningsvilkår er dokumentert. Forkastet for daglig drift: 5 kall per ticker, altså 75 for de 15 mot en dagsgrense på 20. |
| EODHD `/api/calendar` | — (utilgjengelig) | 2026-09-19 | HTTP 403: «Only EOD data allowed for free users». |
| Oslo Børs NewsWeb | Selskapsmeldinger | **2026-09-21, fullstendig** | Åpent JSON-API, ferdig tagget med utsteder. **Euronexts vilkår dekker `newsweb.oslobors.no` ved navn og forbyr automatisert henting uten skriftlig tillatelse.** Se egen seksjon. |
| E24 RSS | — (forkastet) | 2026-09-19 | Forbyr eksplisitt LLM-input. Se under. |
| NRK RSS | — (forkastet) | 2026-09-20 | Avviser automatisert henting med HTTP 403. Generelle nyheter uten finansfokus. |
| Euronext | Finanskalender | **2026-09-21, fullstendig** | Samme vilkår som NewsWeb — `live.euronext.com` står i samme liste i samme dokument. |
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

### Konklusjon på lesningen: uklart — men spørsmålet er nå besvart

**Lesningen alene ga uklart.** Vilkårene forbyr ikke språkmodellbruk, og de
tillater den ikke. Det som måtte til for å gjøre svaret til ja eller nei, var et
skriftlig svar fra `support@eodhistoricaldata.com`.

**Det svaret foreligger nå.** Se «EODHDs skriftlige svar: ja, med betingelser»
under. Avsnittene over står uendret, fordi de dokumenterer hva selve vilkårene
sier — og det er fortsatt ingenting. Godkjenningen er en tillatelse gitt oss,
ikke en endring i vilkårsteksten.

### Spørsmålet er sendt

**E-post sendt 20.09.2026** til `support@eodhistoricaldata.com`, med **ett**
spørsmål: om artikkeltekst fra `/api/news` kan sendes til en tredjeparts
språkmodell for klassifisering, i et ikke-kommersielt studentprosjekt der
resultatet ikke publiseres eller videreformidles.

**Besvart 2026-09-21**, fire dager før fristen 25.09. Svaret er ja, med
betingelser — se seksjonen under.

De tre øvrige spørsmålene i utkastet ble ikke sendt: om «displaying» rammer en
demonstrasjon i undervisning, om aggregert statistikk i et offentlig repo er
Informasjonen «in repackaged form», og om gratisnivået gir tilgang til
`/api/news` for `.OL`-tickere. De to første står fortsatt ubesvart og gjelder
demonstrasjonen og publiseringsskillet. Det tredje er avgjort av nyhetstesten
2026-09-21: gratisnivået dekker `/api/news` for `.OL`.

---

## EODHDs skriftlige svar: ja, med betingelser

**Mottatt 2026-09-21** fra Alejandro C., EOD Support Team,
`support@eodhistoricaldata.com`. Svar på e-posten sendt 20.09.

### Svaret, ordrett

> Hello Marian,
>
> Yes, we approve the limited use you described: sending headlines and article
> text obtained through our News API to a third-party language model solely to
> classify company relevance for your private, non-commercial course project.
>
> This approval is subject to the conditions you outlined: the output stays
> local, the project is not publicly deployed, and the data is not published,
> redistributed, resold, or used to train any model. Please ensure that your
> chosen LLM service does not use the submitted content for training either.
>
> Bien Cordialement,
>
> Alejandro C.
>
> EOD Support Team

### Spørsmålet som ble stilt, ordrett

Fra `docs/epost-til-eodhd.md`, sendt 20.09. E-posten inneholdt **bare dette ene
spørsmålet** — de tre øvrige i utkastet ble holdt tilbake med vilje, fordi
support erfaringsmessig svarer på det letteste når flere stilles samtidig:

> **Language models.** May article content retrieved from the news API
> (`/api/news`) be used as input to a large language model, in order to
> classify how relevant an article is to a given company and to generate a
> short explanation in Norwegian? The output would be shown only inside our
> locally run application. We ask because another provider we evaluated
> prohibits this explicitly in their feed terms, and your Terms and Conditions
> do not mention language models in either direction.

### Hvem svaret kommer fra

**Avsenderen er EOD Support Team, ikke en juridisk avdeling.** Det er verdt å
føre, fordi det avgjør hvor mye vekt svaret tåler:

- Det er **skriftlig**, fra leverandørens egen supportadresse, og det gjengir
  bruken vår presist nok til at det ikke kan misforstås hva som er godkjent.
  Det er belegg, og det er mer enn vi hadde.
- Det er **ikke** en endring i vilkårene, og ikke et juridisk bindende
  dokument. Vilkårsteksten sier fortsatt ingenting om språkmodeller.

Vi behandler det som en tillatelse gitt til dette prosjektet, i dette omfanget,
i dette semesteret. Ikke som en generell regel, og ikke som noe som overlever en
endring i hva vi gjør.

### De fire betingelsene

Svaret er ikke ubetinget. Ordrett er godkjenningen «subject to the conditions
you outlined», og deretter legges én ny til:

| # | Betingelse | Status hos oss |
|---|---|---|
| 1 | «the output stays local» | Oppfylt. Resultatet vises bare i applikasjonen, som kjører lokalt |
| 2 | «the project is not publicly deployed» | Oppfylt. Applikasjonen publiseres ikke |
| 3 | «the data is not published, redistributed, resold, or used to train any model» | Oppfylt. Artiklene selv: `data/` er gitignorert. De utledede tallene: EODHD bekreftet skriftlig samme kveld at egne sammendragstall ikke er deres Informasjon «in repackaged form» — se «Oppfølgingen samme kveld». Forbeholdet som sto her, er dermed innfridd for EODHDs data |
| 4 | «Please ensure that your chosen LLM service does not use the submitted content for training either» | **Ikke oppfylt.** Se under |

**Betingelse 4 er en plikt EODHD har lagt på oss, ikke en de har oppfylt.**
Godkjenningen er ikke innfridd før vi har slått opp modelltjenestens faktiske
vilkår og sitert setningen som sier at innhold sendt gjennom API-et ikke brukes
til trening — med lenke og dato, på samme måte som alt annet i dette dokumentet.

Det kan ikke gjøres ennå, fordi **ingen modelltjeneste er valgt**. Verken
`prd.md`, `begrunnelser.md` eller noe annet dokument navngir en. FR-605 sier at
promptversjon og modell skal lagres med hver vurdering, men ikke hvilken modell.
Valget er dermed første steg, ikke oppslaget.

Ført som oppfølgingspunkt med eier nederst i dokumentet.

### Hva dette betyr for relevanseksperimentet

Beslutningen fra 20.09 sa at eksperimentet kjøres på medieartikler bare hvis
EODHD svarer skriftlig ja innen 25.09 **og** `/api/news` viser seg å dekke
`.OL`. Begge forutsetningene er innfridd 21.09, fire dager før fristen.

**Plan A gjelder.** Plan B — 50 børsmeldinger fra NewsWebs samlekategori —
beholdes som dokumentert alternativ, men er ikke lenger nødvendig. Det er en
vesentlig forbedring av risikobildet: eksperimentet deler ikke lenger kilde med
meldingsdelen, og et negativt svar fra Euronext velter derfor ikke begge deler
samtidig.

---

### Oppfølgingen samme kveld: begge bekreftet

**Mottatt 2026-09-21** fra Lana A., EOD Support Team,
`supportlevel1@eodhistoricaldata.com`. Svar på oppfølgingen sendt samme dag
kl. 19:33, i samme tråd som godkjenningen over.

#### Svaret, ordrett

> Hello,
>
> Yes, we confirm both.
>
> Bien Cordialement,
>
> Lana A.
>
> EOD Support Team

#### De to spørsmålene, ordrett slik de ble sendt

Fra `docs/epost-til-eodhd.md`, oppfølgingen sendt 21.09. Dette er spørsmål 2 og
3 fra det opprinnelige utkastet, holdt tilbake 20.09 til språkmodellspørsmålet
var besvart:

> 1. **"Displaying" in an educational setting.** The Personal Use section
>    states that Non-Professional Users are prohibited from "selling, reselling,
>    retransmitting, redistributing, displaying, or granting access to the
>    Information or Services, whether in its original or repackaged form". Does
>    "displaying" cover showing our application, with EODHD price data visible
>    on screen, in a single classroom demonstration to a teacher and fellow
>    students? We read the clause as being about giving others access to the
>    data, but we would rather ask than assume.

> 2. **Aggregated statistics in a public repository.** Our source code and
>    planning documents are in a public GitHub repository, while the downloaded
>    datasets themselves are kept local and excluded from version control. The
>    repository does contain summary statistics we computed from your data — for
>    example the median daily turnover in NOK for a ticker over a three-month
>    period, and the share of exchange announcements falling in a given category.
>    Does such aggregated, derived statistics count as the Information "in
>    repackaged form", or is it outside the scope of the clause?

> To be concrete about the second question: what is published is a table of
> fifteen tickers with one median turnover figure each, computed over 65 trading
> days, plus percentage shares per announcement category. The underlying price
> series and announcements are not published and are excluded from version
> control. If that distinction is not one your terms recognise, we would like to
> know now rather than later.

#### Hva svaret dekker

Svaret er kort, men det er ikke uklart: begge spørsmålene er stilt som ja/nei
med vår egen lesning oppgitt, og «we confirm both» bekrefter den lesningen.
Konkret:

| # | Spørsmål | Bekreftet |
|---|---|---|
| 1 | Demonstrasjonen for lærer og klasse er del av det ikke-kommersielle studieprosjektet, ikke offentlig drift | Ja |
| 2 | Egne sammendragstall i et offentlig kodelager er vårt eget resultat, ikke Informasjonen «in repackaged form» | Ja |

#### Hva svaret ikke dekker

**Det gjelder EODHD og EODHDs data.** Det er den eneste rekkevidden en
leverandør kan gi: de kan si hva de aksepterer med sine egne data, ikke med
andres.

Det har en presis konsekvens her. Spørsmål 2 nevnte **to** typer tall — median
daglig omsetning per symbol, som er utledet av EODHD-kurser, og
kategorifordelinger i meldingsbildet, som er utledet av NewsWeb-meldinger.
Bekreftelsen rekker bare over den første. **Kategorifordelingene i
`malinger.md` §4 ligger under Euronexts vilkår**, og de er ikke avklart av
dette svaret. At begge sto i samme spørsmål, gjør ikke at ett svar dekker
begge.

**Avsenderen er igjen support, ikke en juridisk avdeling** — og en annen person
enn den som svarte om språkmodeller. Samme forbehold gjelder som over: dette er
belegg for hva leverandøren aksepterer, ikke en endring i vilkårsteksten.
Vilkårene sier fortsatt det de sa.

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
Meldingsobjektet har 20 felter — blant dem `issuerSign`, `issuerName`,
`category`, `publishedTime` og `title`, men **ikke noe språkfelt**. Hele
feltlista er målt 2026-09-21 og står i `malinger.md` §7.3.

Tre forbehold, to av dem nå avklart:

1. ~~**Vilkårene er ikke kontrollert.**~~ **Kontrollert 2026-09-21** — se
   seksjonen under. API-et er fortsatt udokumentert og er backend-en til Oslo
   Børs' egen nettside, ikke et publisert utvikler-API, men vilkårene for
   nettstedet dekker det.
2. **Ingen garanti for stabilitet.** Det kan endres eller stenges uten varsel.
   Vi lagrer derfor rådata lokalt fra første henting. *Merk at lagringen selv
   er berørt av vilkårene — se seksjonen under.*
3. ~~**Oslo Børs eies av Euronext.** Vilkårene henger derfor trolig sammen~~ —
   **bekreftet 2026-09-21.** Begge domenene er navngitt i samme dokument.

Meldingene er allerede knyttet til utsteder. Det betyr at KI ikke brukes til å
avgjøre hvilket selskap en melding gjelder — den jobben gjør `issuerSign`. KI
brukes først etter at kategorifiltrering i vanlig programkode har luket bort
støyen, og da til å forklare innholdet på norsk.

---

## Oslo Børs NewsWeb og Euronext: hva vilkårene sier

**Kontrollert 2026-09-21.** To dokumenter er lest i sin helhet, ikke forsidene:

1. `https://newsweb.oslobors.no/disclaimer` — NewsWebs egen ansvarsfraskrivelse
   og rettighetserklæring, på norsk og engelsk.
2. `https://www.euronext.com/en/terms-use` — Euronexts «Legal notices and terms
   and conditions of use», sist oppdatert 29. april 2021 ifølge dokumentet selv.

Alt som er sitert under, er ordrett fra de to. Der noe er uthevet i et sitat, er
uthevingen vår og er merket som det.

Funnet er uavhengig verifisert 2026-09-21 mot samme kilde.

### De to kildene deler vilkår — det er ikke lenger en antakelse

Forbeholdet fra 20.09 sa at vilkårene for NewsWeb og for finanskalenderen
«trolig henger sammen» fordi Oslo Børs eies av Euronext. Det er nå bekreftet på
to måter.

Euronexts vilkår lister opp hvilke nettsteder de gjelder for, og begge står der
(uthevingen er vår):

> This website, euronext.com, and the websites connect.euronext.com,
> **live.euronext.com**, ise.ie, interbolsa.pt, corporateservices.euronext.com,
> euronextfx.com, companywebcast.com, webcast.nl, webinar.nl, royalcast.nl,
> insiderlog.se, insiderlog.com, commcise.com, complylog.com, **oslobors.no**,
> **newsweb.oslobors.no**, euronextvps.no, fishpool.eu, vp.dk,
> borsaitaliana.it, mtsmarkets.com, montetitoli.com, ccg.it, gatelab.com and
> elite-network.com are owned and operated by Euronext N.V. and/or its
> subsidiaries and affiliates.

Og Oslo Børs' egen side om ansvar og rettigheter,
`oslobors.no/Oslo-Boers/Om-Oslo-Boers/Ansvar-og-rettigheter`, videresender nå
til nettopp `euronext.com/en/terms-use`. Kontrollert 2026-09-21.

Én vilkårskontroll dekker altså begge kildene, slik oppfølgingspunktet la opp
til.

### De tre klausulene som rammer oss

Dette er ikke en kilde som tier. Tre klausuler, sitert ordrett og uten
utheving.

**1. Automatisert henting — forbudt uten skriftlig tillatelse på forhånd:**

> Except if we give you prior written permission, use of any Web browsers
> (other than generally available third-party browsers), engines, software,
> spiders, robots, avatars, agents, tools or other devices or mechanisms to
> navigate, search or determine the Euronext Website is strictly prohibited.

«Software … or other devices or mechanisms to navigate, search or determine»
beskriver det vi gjør. Vi henter med en programmert forespørsel, ikke med en
alminnelig nettleser, så unntaket i parentesen — «generally available
third-party browsers» — treffer ikke.

**2. Systematisk uttrekk til en samling — forbudt uten skriftlig tillatelse.**
Klausulen står inne i en lengre oppramsing:

> You further acknowledge and agree that, unless Euronext, its applicable
> affiliate, and/or the applicable Third Party Provider give you prior written
> permission, you will not sell, license, rent, modify, print, copy, reproduce,
> download, upload, transmit, distribute, disseminate, publicly display,
> publicly perform, publish, edit, adapt, compile or create derivative works
> from any Content or materials (including, without limitation, through framing
> or systematic retrieval to create collections, compilations, databases or
> directories) or otherwise transfer any of the Content to any third person
> (including, without limitation, others in your company or organisation).

«Systematic retrieval to create collections, compilations, databases or
directories» er en presis beskrivelse av det lokale meldingslageret i FR-406.
Også `download` og `copy` står på lista.

**3. Hva én bruker faktisk har lov til.** Dette er den klausulen en
tillatelsesforespørsel må forholde seg til, fordi den definerer hva som er
tillatt uten avtale — og dermed hvor mye mer vi ber om:

> You may print or download a single, unaltered, permanent copy or one
> temporary copy in a single computer’s memory of any Content for your
> personal, non-commercial use only, provided you keep intact all trademark,
> copyright and other proprietary notices.

Rammen er **én kopi**, til **personlig, ikke-kommersiell** bruk. Et daglig
uttrekk for femten utstedere som bygger seg opp over tid, er noe annet enn én
kopi, uansett hvor privat bruken er. Det er avstanden mellom denne setningen og
det vi gjør, forespørselen til Euronext må dekke.

### Undervisningsunntaket

Unntaket står i avsnittet rett etter klausul 3, og er den eneste åpningen vi
har funnet i noen kilde i dette prosjektet:

> Educational institutions may download and reproduce Content on the Euronext
> Website for distribution in the classroom solely for educational purposes.
> Distribution outside the classroom or for other than solely educational
> purposes requires express written permission in accordance with the above
> provisions.

**Tre spenninger som ikke lar seg løse ved å lese videre:**

1. **Unntaket tillater nedlasting, forbudet rammer midlene.** Klausulen sier
   utdanningsinstitusjoner *kan* «download and reproduce Content». Forbudet mot
   software, roboter og verktøy for å navigere nettstedet har intet tilsvarende
   unntak. Den ene setningen tillater resultatet, den andre forbyr veien dit. Vi
   vet ikke hvordan Euronext leser de to sammen.
2. **«Educational institutions» — er det oss?** Klausulen er skrevet om
   institusjoner, ikke om studenter. Høgskolen i Molde er en
   utdanningsinstitusjon; en studentgruppe som kjører et prosjekt lokalt er ikke
   åpenbart det samme, og ikke åpenbart noe annet.
3. **Et offentlig repo er «distribution outside the classroom».** Det vi
   publiserer fra NewsWeb er utledet statistikk — kategorifordelingene i
   `malinger.md` §4 — ikke meldingene. Men unntaket er uttrykkelig avgrenset til
   klasserommet, og alt utenfor krever «express written permission».

### NewsWebs egen rettighetserklæring, i tillegg

`newsweb.oslobors.no/disclaimer` legger et norskrettslig lag oppå. Ordrett fra
den norske versjonen:

> Denne databasen er beskyttet av Åndsverksloven § 43 og Oslo Børs har enerett
> til å råde over hele eller vesentlige deler av databasens innhold.
> Tilgjengeliggjøring av materialet utenfor det private området og
> eksemplarfremstilling som ikke er til privat bruk eller som ellers er hjemlet
> i lov, kan kun skje etter særskilt avtale med Oslo Børs. Som
> eksemplarfremstilling regnes nedlasting og lagring på datamaskin eller på
> annen innretning som kan gjengi materialet. Som tilgjengeliggjøring regnes så
> vel aktiv overføring eller overlatelse av materialet til andre, som det at
> materialet stilles til rådighet for andres tilegnelse på eget initiativ.

Erklæringen definerer sine egne begreper, og definisjonene treffer oss direkte:
**nedlasting og lagring på datamaskin *er* eksemplarfremstilling** etter denne
teksten. Om automatisert henting sier den derimot ingenting — det står bare i
Euronext-vilkårene.

Ansvarsdelen er ren fraskrivelse og sier ingenting om bruk:

> Oslo Børs oppbevarer og distribuerer opplysninger på dette nettstedet iht.
> kravene i verdipapirhandelloven § 5-12. Oslo Børs har ikke ansvar for feil
> eller unøyaktigheter i informasjonen.

### Hvor vi henter fra, og hvorfor det ikke er et forsvar

**Faktum:** hentingen skjer fra `api3.oslo.oslobors.no`, og det vertsnavnet
står **ikke** i vilkårenes liste over nettsteder. Lista navngir
`newsweb.oslobors.no`, som er nettstedet API-et er backend for.

**Dette brukes ikke som forsvar.** Innholdet er det samme — de samme
børsmeldingene, fra den samme databasen. Og klausulen om «systematic retrieval
to create collections, compilations, databases or directories» rammer
*handlingen*, ikke vertsnavnet den utføres mot. Vilkårene definerer dessuten
«the Euronext Website» vidt: «the web pages of Euronext available to the general
public, including any linked pages owned and operated by Euronext».

Vi legger til grunn at API-et er dekket. Å bygge på at det ikke er navngitt,
ville vært å lete etter et smutthull, ikke etter et svar — og et smutthull er
ikke noe vi kan sitere i en innlevering.

### Hva dette betyr for oss

| Spørsmål | Svar i vilkårene |
|---|---|
| Sier de noe om automatisert henting? | **Ja, uttrykkelig.** Forbudt uten skriftlig tillatelse på forhånd |
| Sier de noe om videreformidling? | **Ja, uttrykkelig.** Forbudt uten skriftlig tillatelse, med ett unntak for utdanningsinstitusjoners bruk i klasserommet |
| Hva er tillatt uten avtale? | Én kopi, til personlig og ikke-kommersiell bruk |
| Er undervisningsbruk regulert? | Ja. Dette er den eneste kilden vi har undersøkt som har en uttrykkelig undervisningsklausul |
| Skiller de på kommersiell og ikke-kommersiell bruk? | Ja, i begge klausulene over |

Dette er motsatt situasjon av EODHD. Der var problemet taushet. Her er problemet
ordlyd.

### Vurderingen av det offentlige repoet står ikke lenger uimotsagt

**Rådgivningsøkta 2026-09-21 kl. 18:28** vurderte de aggregerte tallene i det
offentlige repoet — medianomsetning per symbol, kategorifordelinger, kalltall —
som **lav risiko**.

Den vurderingen var bygget på **EODHDs ordlyd alene**, der det eneste som
trekker mot oss er ordet «repackaged» i en klausul som ellers handler om å gi
andre tilgang.

Etter Euronext-funnet hadde posisjonen «sammendragsstatistikk er ikke
databasen» ordlyd mot seg i **tre** tekster. **Én av dem er nå avklart skriftlig
i vår favør**, de to andre står:

| Kilde | Ordlyden som trekker mot posisjonen | Status |
|---|---|---|
| EODHD | «…whether in its original or repackaged form» | **Avklart 2026-09-21.** EODHD bekrefter skriftlig at egne sammendragstall ikke er Informasjonen «in repackaged form» |
| Euronext | «Distribution outside the classroom … requires express written permission» | **Står.** Forespørselen er ubesvart |
| NewsWeb / Åndsverkloven § 43 | «enerett til å råde over hele eller **vesentlige deler** av databasens innhold» | **Står.** Hva som utgjør en «vesentlig del», er ikke noe vi kan avgjøre selv |

**Avklaringen rekker bare så langt som EODHDs egne data.** Den dekker
medianomsetning per symbol, som er regnet ut av EODHD-kurser. Den dekker ikke
kategorifordelingene i `malinger.md` §4, som er utledet av NewsWeb-meldinger og
ligger under de to tekstene som står igjen. Se «Oppfølgingen samme kveld: begge
bekreftet».

Posisjonen er altså delt i to. For EODHD-tallene er den ikke lenger vår egen
vurdering, men noe leverandøren har bekreftet skriftlig. For NewsWeb-tallene
står den som før: en forsvarlig posisjon med ordlyd mot seg i to tekster, og en
median er fortsatt ikke en kursserie.

**Konsekvensen er praktisk:** brevet til Euronext nevner derfor det offentlige
repoet **eksplisitt**, i stedet for å holde det utenfor og be om tillatelse bare
til hentingen. Å be om tillatelse til én ting mens man gjør to, gir et svar man
ikke kan bruke.

### Forespørsel om skriftlig tillatelse er sendt

**Sendt 2026-09-21** til `copyrightpermissionsEurope@euronext.com` — adressen
vilkårene selv oppgir for slike forespørsler, sammen med postadressen til
Euronext, Legal Department, Copyright Agent, Beursplein 5, 1012 JW Amsterdam.

Forespørselen beskriver det vi faktisk gjør:

- ikke-kommersielt studentprosjekt, høstsemesteret 2026
- **ett uttrekk per døgn** for ca. 15 utstedere
- applikasjonen kjører lokalt og publiseres ikke
- ingen videreformidling av meldingene
- **men kildekode og planleggingsdokumenter ligger i et offentlig repo**, med
  utledet statistikk og uten meldinger — ført eksplisitt, jf. avsnittet over
- samme spørsmål stilt for **finanskalenderen på `live.euronext.com`**, siden
  begge domenene ligger under de samme vilkårene

**Frist: 2026-09-28.** Den er vår egen — brevet ber ikke om svar innen noen dato,
og Euronext har ikke lovet noe.

**Purring sendt 2026-09-22**, i samme tråd. Den spør om forespørselen 21.09 kan
innvilges og om svaret også gjelder finanskalenderen (spørsmål 1). Den stiller
dessuten et spørsmål det første brevet ikke hadde med: om meldingstitler og
-tekst kan sendes til en tredjeparts språkmodell (spørsmål 2). Det er
overføringsklausulen, *«otherwise transfer any of the Content to any third
person»*. Purringen tilbyr også et smalere alternativ: et lite, manuelt innsamlet
utvalg, brukt én gang til et dokumentert klassifiseringseksperiment. Brevet
setter ingen dato, og vår frist 2026-09-28 står uendret internt. Teksten er ført
i `docs/epost-til-euronext.md`, men ingen sendt kopi finnes lokalt, så
ordlyden er slik den ble gjengitt.

### Beslutningen gruppen har tatt i mellomtiden

Hentingen fortsetter mens forespørselen er ubesvart. Det er et valg, ikke en
forglemmelse, og det skal stå som et valg.

**Faglærer er ikke varslet om funnet, og skal ikke varsles.** Det er besluttet
av gruppen 2026-09-21. Vi fører det her fordi det hører til beslutningen: det er
gruppen selv som bærer ansvaret for å fortsette hentingen mens rettighetshaveren
ikke har svart, uten å ha lagt spørsmålet fram for faglærer først.

Grunnlaget vi bygger på i mellomtiden, er undervisningsunntaket og det at
forespørselen faktisk er sendt — ikke at vilkårene tillater hentingen. De gjør
de ikke, og det står dokumentert over.

Uteblir svaret innen 28.09, er det en ny beslutning som må tas. Ført som
oppfølgingspunkt med eier nederst i dokumentet.

### Konklusjon

**Nei — dokumentert, med et unntak som kan gjelde oss, og en forespørsel ute.**
Dette er den første kilden i prosjektet som både forbyr uttrykkelig *og* har en
undervisningsklausul. Spørsmålet er ikke lenger om vilkårene sier noe, men om
unntaket rekker over det vi gjør, og hvem det gjelder for.

Børsmeldinger er kjernen i produktet, og det er denne kilden som leverer dem.
Svaret fra Euronext er derfor prosjektets største åpne risiko.

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

**Oppdatert 2026-09-21.** Vilkårskontrollen er nå gjort, og posisjonen hadde
ordlyd mot seg i tre tekster — «repackaged form» hos EODHD, «distribution
outside the classroom» hos Euronext, og «vesentlige deler» i Åndsverkloven § 43
via NewsWebs egen rettighetserklæring. **EODHD har senere samme dag bekreftet
skriftlig at våre egne sammendragstall ikke er deres Informasjon «in repackaged
form».** Det avklarer EODHD-tallene. De to andre tekstene står, og de gjelder
tallene utledet av NewsWeb. Se «Vurderingen av det offentlige repoet står ikke
lenger uimotsagt» over.

---

## Å følge opp

- [x] ~~**Euronext samlet:** kontrollere bruksvilkårene for NewsWeb-data og for
      finanskalenderen i samme runde~~ — **gjort 2026-09-21.** De deler vilkår;
      begge domenene står navngitt i samme dokument. Se seksjonen «Oslo Børs
      NewsWeb og Euronext: hva vilkårene sier». Svaret er nei, med et
      undervisningsunntak som må avklares
- [x] ~~**Skrive til `copyrightpermissionsEurope@euronext.com`**~~ — **sendt
      2026-09-21.** Programmert henting fra `api3.oslo.oslobors.no`, ett uttrekk
      per døgn for ca. 15 utstedere, lokal kjøring, offentlig repo med utledet
      statistikk, og samme spørsmål for finanskalenderen på
      `live.euronext.com`. **Svar avventes. Egen beslutningsfrist 2026-09-28.**
      **Purret 2026-09-22** i samme tråd, med et nytt spørsmål om overføring
      til en språkmodell og et smalere alternativ. Brevet er
      arkivert ordrett i `docs/epost-til-euronext.md`. Faglærer er *ikke*
      varslet — besluttet av gruppen, se «Beslutningen gruppen har tatt i
      mellomtiden»
- [ ] **Beslutning hvis Euronext ikke svarer innen 2026-09-28.** Vilkårene
      krever tillatelse på forhånd, og vi henter allerede. Alternativene er å
      stoppe hentingen, fortsette bevisst under undervisningsunntaket, eller
      bygge meldingsdelen om. Skal avgjøres og skrives ned, ikke bli stående
      fordi ingen tok det opp. **Eier: Gruppen.** Frist 2026-09-28

      **Huskeregel når svaret kommer** — den gjelder uansett om det kommer før
      eller etter fristen: *les hva brevet faktisk spurte om før du avgjør hvor
      langt svaret rekker.* EODHD-svaret 21.09 viste hvorfor. Spørsmål 2 nevnte
      to typer tall i samme setning — medianomsetning fra EODHD-kurser og
      kategorifordelinger fra NewsWeb-meldinger — og «Yes, we confirm both»
      bekreftet to *spørsmål*, ikke alle tallene nevnt i dem. Rekkevidden var
      tvetydig fordi spørsmålet selv blandet to kilder.

      Brevet til Euronext har samme form, bare større: det ber om tillatelse
      til fire ting i én forespørsel, med hver sin overskrift i brevet —
      **Retrieval** (ett uttrekk per døgn), **Storage** (lokal lagring av
      metadata og titler), **Display** (demonstrasjonen i undervisning) og
      **Source code** (det offentlige repoet med utledede tall og siterte
      titler). I tillegg spør brevet om samme svar gjelder finanskalenderen på
      `live.euronext.com`. Purringen 22.09 la til en femte del: overføring av
      titler og tekst til en tredjeparts språkmodell. Et ja til de fire første
      er ikke et ja til den.

      Kommer det et kort svar, skal det derfor ikke føres som ja eller nei.
      **Før hvilke av de fem delene som er dekket og hvilke som ikke er det**,
      og om kalenderen er besvart. Et ja til «Retrieval» er ikke automatisk et
      ja til «Storage» — det står allerede i `docs/epost-til-euronext.md`,
      seksjonen «En klausul brevet ikke nevner ved navn», og huskeregelen her
      utvider det til alle fire.
- [ ] Kontrollere Alpha Vantage sine vilkår for ikke-kommersiell bruk
- [x] ~~Lese EODHDs fullstendige ToS, ikke bare prissiden~~ — gjort 2026-09-20,
      se seksjonen «EODHD: hva de fullstendige vilkårene sier». Svaret er uklart
- [x] ~~Spørre `support@eodhistoricaldata.com` skriftlig om språkmodellbruk~~ —
      sendt 20.09.2026, **besvart 21.09.2026: ja, med fire betingelser.** Se
      «EODHDs skriftlige svar: ja, med betingelser»
- [x] ~~**De to gjenstående spørsmålene til EODHD ble ikke sendt:** om
      «displaying» rammer en demonstrasjon i undervisning, og om aggregert
      statistikk i et offentlig repo er Informasjonen «in repackaged form»~~ —
      **sendt 2026-09-21 kl. 19:33 og besvart samme kveld: begge bekreftet.**
      Svaret er ført ordrett i «Oppfølgingen samme kveld: begge bekreftet».
      Merk at bekreftelsen gjelder EODHDs egne data; kategorifordelingene
      utledet av NewsWeb ligger fortsatt under Euronexts vilkår
- [x] ~~Verifisere om `/api/news` svarer for `.OL`-tickere på gratisnivå~~ —
      **gjort 2026-09-21. Ja:** HTTP 200 og ti artikler for `DNB.OL`. Testen
      kostet 5 kall, ikke 10. Se `malinger.md` §7.2
- [ ] Rette kalltallet for nyhets-API-et der det er ført videre: `prd.md` og
      `begrunnelser.md` anslår ~80 kall for relevanseksperimentets åtte
      selskaper, bygget på det doble tallet. Med 5 per ticker blir det ~40.
      Målingen dekker bare én ticker; 5 per ticker for flere er utledet av
      EODHDs eget eksempel, ikke målt. Koster ingen kall å rette
- [ ] **Dokumentere at modelltjenesten ikke trener på innholdet.** Betingelse 4
      i EODHDs godkjenning av 21.09, og godkjenningen er ikke oppfylt før den er
      ført. To steg: (a) velge modelltjeneste — ingen er navngitt i noe dokument
      i dag; (b) slå opp tjenestens faktiske vilkår, sitere setningen ordrett og
      føre lenke og dato her. Koster ingen API-kall. **Eier: Gruppen.**
      Frist: før første KI-kall kjøres
- [ ] Vurdere vilkårene på nytt dersom applikasjonen skal publiseres
- [ ] **Kontrollere at skillet over holder mot NewsWebs faktiske vilkår.**
      EODHD-halvdelen er lukket 2026-09-21: leverandøren har skriftlig bekreftet
      at våre sammendragstall ikke er deres Informasjon «in repackaged form».
      For NewsWeb er posisjonen fortsatt vår egen vurdering, med «distribution
      outside the classroom» og «vesentlige deler» mot seg. Henger sammen med
      Euronext-svaret. **Eier: Gruppen.** Frist 2026-09-28
