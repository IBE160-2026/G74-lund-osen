# Avstemming: PRD mot kilder-og-rettigheter.md

Dato: 2026-09-20

**Kilde (fasit):** `docs/kilder-og-rettigheter.md`
**Kontrollert dokument:** `_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md`
**Vedlegg lest:** `malinger.md` (samme mappe)

Gjennomgangen ser bare én vei: hva kildedokumentet slår fast om rettigheter,
forbehold og forkastede kilder, og om det står igjen — like sterkt — i PRD-en.
Alt som er svekket eller borte er notert, fordi et rettighetsproblem her kan
velte datagrunnlaget, ikke bare forsinke det.

---

## Sammendrag

| # | Funn | Alvor |
|---|---|---|
| 1 | Medieartiklene relevanseksperimentet bygger på har ingen lovlig kilde i PRD-en | Kritisk |
| 2 | «Lese EODHDs fullstendige ToS» er falt helt ut av PRD-en | Høy |
| 3 | Alpha Vantage er falt helt ut — både kilden og oppfølgingspunktet | Middels |
| 4 | Ingen åpne punkter har eier; punkt 1 har `‹fylles inn›` | Høy |
| 5 | «Vurder vilkårene på nytt ved publisering» er snevret inn til «kommersiell versjon» og «videreformidlingsrett» | Middels |
| 6 | PRD-en forteller ikke hvilke EODHD-endepunkter som er forkastet, eller hvorfor | Middels |
| 7 | Påstanden «punkt 1 er det eneste som kan velte datagrunnlaget» er ikke dekket av kildedokumentet | Middels |
| 8 | E24-sitatet er korrekt gjengitt, men snevrere enn klausulen | Lav |

Det som **er** i orden: de tre NewsWeb-forbeholdene, konsekvensen av
E24-forbudet, premisset om lokal ikke-kommersiell bruk (men se funn 5), og
kvotebildet for NewsWeb/Euronext.

---

## 1. «Å følge opp»-punktene, punkt for punkt

Kildedokumentet har fire punkter nederst. Kontrollen er om hvert av dem har et
tilsvarende åpent punkt i PRD-en, **med eier og frist**.

| Kildens punkt | Finnes i PRD? | Eier | Frist | Vurdering |
|---|---|---|---|---|
| Euronext samlet: NewsWeb + finanskalender under ett | Ja — seksjon 6 og åpent punkt 1 | `‹fylles inn›` | 2026-09-27 | Innholdet er dekket presist, også begrunnelsen om felles eierskap. **Mangler eier.** |
| Kontrollere Alpha Vantage sine vilkår for ikke-kommersiell bruk | **Nei** | — | — | Ordet «Alpha Vantage» finnes ikke i PRD-en |
| Lese EODHDs fullstendige ToS, ikke bare prissiden | **Nei** | — | — | Ingen spor i PRD eller `malinger.md` |
| Vurdere vilkårene på nytt dersom applikasjonen skal publiseres | Delvis — seksjon 2 | — | — | Snevret inn, og ikke ført som åpent punkt. Se funn 5 |

Ett av fire er ført som åpent punkt. Ingen av de fire har eier.

### Funn 4 — eierkolonnen er tom i hele tabellen

PRD-ens seksjon 8 har en `Eier`-kolonne. Punkt 1 har `*‹fylles inn›*`, punktene
2–8 er blanke. Det gjelder også punktet PRD-en selv kaller det eneste som kan
velte datagrunnlaget, med hard frist om sju dager.

Et rettighetspunkt uten eier og med frist neste uke er i praksis ikke tildelt.
Dette er den letteste og mest lønnsomme rettingen i hele listen.

### Funn 2 — EODHDs fullstendige ToS

Kildedokumentet fører EODHD `/api/eod` som **«2026-09-19, delvis»** kontrollert,
og forklarer hva «delvis» betyr: bare prissiden er lest, ikke vilkårene. Derfor
står «Lese EODHDs fullstendige ToS, ikke bare prissiden» på oppfølgingslisten.

PRD-en presenterer EODHD som en avklart kilde:

- Seksjon 6, tabellen: `EODHD /api/eod | Sluttkurser | 1 kall per symbol, 15 i døgnet` — ingen forbehold
- Seksjon 3: antallet på 15 aksjer er *utledet* av EODHDs kvote
- NFR-01: hele driftsbudsjettet hviler på 20 kall i døgnet

Kvotetallene er hentet fra prissiden — nøyaktig den kilden kildedokumentet sier
ikke er nok. Ordet «delvis» er borte. En leser av PRD-en alene vil tro at
EODHD-vilkårene er kontrollert.

Konsekvensen er større enn for NewsWeb i én forstand: EODHD bærer *kursdataene*,
som er grunnlaget for signalmodellen, aksjeuniverset og markedsoversikten. Sier
ToS-en noe om automatisert henting eller lagring som prissiden ikke nevner, treffer
det mer enn meldingsdelen.

**Forslag:** nytt åpent punkt i seksjon 8 — «Lese EODHDs fullstendige ToS, ikke
bare prissiden», eier, frist før implementasjonen av signalet låses, blokkerer
`NFR-01` og seksjon 3.

### Funn 3 — Alpha Vantage

Kildedokumentet fører Alpha Vantage som «forkastet som hovedkilde», vilkår ikke
kontrollert, med to opplysninger PRD-en ikke har:

1. Den ble **testet mot Oslo Børs, men symbolene var ikke pålitelige nok**
2. Den er **brukt i tidlige tester på gull og sølv**

Punkt 2 er grunnen til at oppfølgingspunktet finnes: kilden er allerede brukt,
ikke bare vurdert. PRD-en nevner den ikke, verken som forkastet alternativ eller
som åpent punkt.

Punkt 1 har dessuten en selvstendig verdi PRD-en mister: det er dokumentasjon på
*hvorfor* EODHD ble valgt for Oslo Børs-symboler. Uten den ser EODHD-valget
ubegrunnet ut.

---

## 2. E24-forbudet mot LLM-input

### Er forbudet gjengitt riktig?

PRD-en, seksjon 6:

> E24 er allerede forkastet på vilkår, ikke på teknikk: feeden forbyr eksplisitt
> bruk av innholdet som input til språkmodeller. Andre norske finansmedier
> publiserer ikke lenger åpen RSS.

Dette er **korrekt så langt det rekker**, og skillet vilkår/teknikk er bevart.

### Er konsekvensen tydelig?

Ja. PRD-en sier rett ut:

> Faller NewsWeb bort, finnes det derfor ingen åpenbar erstatning, og det er
> nettopp derfor kontrollen haster.

Dette er den skarpeste setningen i hele kapittelet, og den er sterkere enn
kildedokumentets egen formulering. Ingen anmerkning.

### Funn 8 — sitatet er snevrere enn klausulen

Klausulen i kildedokumentet forbyr tre ting PRD-ens gjengivelse ikke nevner:

| Klausulen sier | PRD-en sier |
|---|---|
| «training, fine-tuning, or evaluating, or providing input to» | bare «input til» |
| «large language models (LLMs), generative AI systems, **or any automated systems that produce derivative or synthetic content**» | bare «språkmodeller» |
| «article headlines, summaries, links, full-text, images, **metadata** or other elements» | «innholdet» |

Isolert er dette pedanteri. Sammen med funn 1 er det ikke: en snever gjengivelse
gjør det lett å tro at *overskrifter og metadata* kan brukes til symbolmatching
så lenge KI ikke ser brødteksten. Klausulen dekker begge deler, og dekker også
evaluering — altså nøyaktig det et relevanseksperiment gjør.

### Funn 1 (kritisk) — relevanseksperimentet har ingen lovlig mediekilde

Dette er gjennomgangens alvorligste funn, og det følger av å lese de to
dokumentene mot hverandre.

PRD-en forplikter seg tre steder til å bruke medieartikler:

- Suksessmål, seksjon 7: «Testsett på **50 medieartikler** merket manuelt, kjørt mot både symbolmatching og KI-klassifisering», frist uke 41
- Seksjon 4.3, åpent punkt: kjennetegn 1 må «forbeholdes relevanseksperimentet, **som fortsatt bruker medieartikler**»
- Seksjon 4.3, måling 1: medietesten 17.09 leste «de ti siste nyhetstreffene for et utvalg selskaper»

Ingen av stedene navngir kilden til artiklene. Kildedokumentet lister alle
mediekilder som er vurdert, og **hver eneste er utelukket eller uavklart**:

| Mediekilde | Status i kildedokumentet |
|---|---|
| E24 RSS | Forkastet — forbyr LLM-input, inkludert evaluering |
| NRK RSS | Vurdert, vilkår **ikke kontrollert**, generelle nyheter uten finansfokus |
| EODHD `/api/news` | Forkastet — for dyrt i kvote |
| DN, Finansavisen, Hegnar, Kapital | Publiserer ikke lenger åpen RSS |
| Alpha Vantage | Forkastet som hovedkilde, vilkår ikke kontrollert |

Eksperimentet slik PRD-en beskriver det — symbolmatching mot KI-klassifisering
på medieartikler — er *presis den arkitekturen* kildedokumentet sier E24-klausulen
rammer:

> Dette rammer direkte arkitekturen vi vurderte, der KI skulle avgjøre hvilket
> selskap en artikkel faktisk handler om.

Det gjenstår altså en KI-oppgave på medieartikler i PRD-en, etter at kilden til
slike artikler er forkastet på vilkår. `malinger.md` seksjon 6 forsterker
uklarheten: relevanseksperimentet er ført med kostnad «Restkvoten én gang», som
antyder EODHD `/api/news` — endepunktet kildedokumentet erklærer forkastet.

**Dette er ikke dekket av åpent punkt 1.** Vilkårskontrollen for NewsWeb avgjør
meldingsdelen, ikke hvor 50 medieartikler skal komme fra.

**Forslag:** nytt blokkerende åpent punkt — «Kilde og vilkår for de 50
medieartiklene i relevanseksperimentet», eier, frist før uke 41, blokkerer
suksessmålet «Relevanseksperiment» og det åpne punktet om usikkerhetskriteriene.
Avklaringen må si eksplisitt at E24 ikke kan brukes, heller ikke til overskrifter
eller metadata, og heller ikke til evaluering.

---

## 3. De tre NewsWeb-forbeholdene

Alle tre er til stede. Dette er den best avstemte delen av PRD-en.

| Kildens forbehold | Hvor i PRD-en | Vurdering |
|---|---|---|
| **1. Vilkårene er ikke kontrollert.** Udokumentert backend for Oslo Børs' egen nettside, ikke et publisert utvikler-API | Seksjon 6, åpent punkt — nesten ordrett: «udokumentert backend for Oslo Børs' egen nettside, ikke et publisert utvikler-API, og vilkårene er ikke kontrollert» | Fullt gjengitt |
| **2. Ingen garanti for stabilitet.** Kan endres eller stenges uten varsel; rådata lagres lokalt fra første henting | FR-406 (rådatalageret) og NFR-07 | Gjengitt, og **operasjonalisert** som et krav med tilhørende lagringsregel. Sterkere enn kilden |
| **3. Oslo Børs eies av Euronext.** Vilkårene henger trolig sammen og må kontrolleres under ett | Seksjon 6, «Omfang»-raden, og åpent punkt 1: «kontrollert under ett» | Fullt gjengitt, med begrunnelsen intakt |

Én liten observasjon uten alvor: kildedokumentet sier «endres **eller stenges**
uten varsel». PRD-en sier «endres uten varsel» i NFR-07, men dekker stengning
gjennom formuleringen «om en kilde forsvinner». Ingen realitetsforskjell.

Merk også at kildedokumentets siste avsnitt om NewsWeb — at `issuerSign` gjør
symbolkoblingen slik at KI ikke trengs til den jobben — er gjengitt presist i
PRD-ens seksjon 4.3. Ingen anmerkning.

---

## 4. Forkastede EODHD-endepunkter

### Funn 6 — tre forkastelser, null gjengitt

Kildedokumentet forkaster tre endepunkter, hvert med sin egen grunn:

| Endepunkt | Status i kilden | Grunn | I PRD-en? |
|---|---|---|---|
| `/api/real-time` | Forkastet | **Virker teknisk**, men prissiden sier gratisnivået ikke har det. «Ikke bygg på» | Nei |
| `/api/news` | Forkastet | Ett ticker per kall, 5–10 kall per forespørsel — for dyrt i kvote | Nei |
| `/api/calendar` | Utilgjengelig | **HTTP 403: «Only EOD data allowed for free users»** | Nei |

PRD-ens seksjon 6 lister bare `/api/eod`, og sier ingenting om de tre andre.
Det nærmeste er seksjon 2, «Utenfor v1»: `intradag- og sanntidsdata`.

Det er en **omskrivning av årsak til valg**. I kilden er sanntid utelukket fordi
gratisnivået ikke gir tilgang — et tilgangs- og vilkårsspørsmål. I PRD-en
fremstår det som en avgrensning gruppen har valgt. En sensor som leser PRD-en
alene vil tro at sanntid var mulig og ble valgt bort.

To konkrete følger:

1. **Euronext-kalenderen står ubegrunnet.** PRD-en oppgir Euronext som kilde til
   kommende hendelser, men ikke hvorfor. Kilden har svaret: EODHDs kalender gir
   HTTP 403, og Euronext er «eneste gratis vei til kalender etter at EODHD falt
   bort». Uten det ser Euronext ut som et fritt valg, og kostnaden ved
   oppslagstabellen for ticker/ISIN (seksjon 6) fremstår som selvpålagt.
2. **NewsWeb-valget står svakere enn det burde.** At `/api/news` ble forkastet på
   kvotekostnad er en del av begrunnelsen for NewsWeb. PRD-en sier bare at
   NewsWeb ikke koster kvote, ikke at alternativet gjorde det.

Ingenting PRD-en sier om EODHD er **galt**. Men fremstillingen av *hvilke*
endepunkter som er forkastet, og *hvorfor*, mangler i sin helhet.

---

## 5. Premisset om ikke-kommersiell, lokal bruk

Kildedokumentet, øverst:

> **Premiss for v1:** applikasjonen kjøres lokalt i undervisningssammenheng og
> publiseres ikke. Vurderingen gjelder derfor ikke-kommersiell, pedagogisk bruk.

PRD-en har premisset to steder i seksjon 2:

> Første versjon er på norsk, kjører lokalt og publiseres ikke.

> Vurderingen av videreformidlingsrett er utsatt til en eventuell kommersiell
> versjon, fordi v1 kjøres lokalt i undervisningssammenheng og ikke publiseres.

Premisset er altså **gjengitt**. To anmerkninger:

**Plasseringen.** Premisset står i omfangskapittelet, ikke i seksjon 6
(«Datakilder og rettigheter»), som er der en leser går for rettighetsspørsmål.
Hele seksjon 6 hviler på premisset uten å nevne det. Én setning øverst i
seksjon 6 ville lukke dette.

### Funn 5 — den betingede forpliktelsen er snevret inn på to akser

Kildens fjerde oppfølgingspunkt: «Vurdere **vilkårene** på nytt dersom
applikasjonen skal **publiseres**».

PRD-ens formulering: «Vurderingen av **videreformidlingsrett** er utsatt til en
eventuell **kommersiell** versjon».

| Akse | Kilden | PRD-en | Følge |
|---|---|---|---|
| Hva som skal vurderes | vilkårene, i sin helhet | videreformidlingsrett | De øvrige vilkårene — automatisert henting, lagring, KI-bruk — faller utenfor |
| Hva som utløser vurderingen | publisering | kommersialisering | **Ikke-kommersiell publisering utløser ingenting i PRD-en** |

Den andre raden er den som betyr noe. Legges løsningen ut på GitHub, demonstreres
den offentlig, eller deles den utenfor undervisningssammenheng, er premisset for
hele kildedokumentets vurdering brutt — uten at noe i PRD-en fanger det opp.
Dette er et nærliggende scenario for et studentprosjekt, ikke et hypotetisk ett.

I tillegg er punktet ikke ført i seksjon 8, og har derfor verken eier eller
utløsende betingelse noen holder øye med.

**Forslag:** rett formuleringen i seksjon 2 til å speile kilden — *vilkårene*
vurderes på nytt dersom løsningen *publiseres*, kommersielt eller ikke — og før
det som åpent punkt med betingelse i stedet for dato.

---

## 6. Sier PRD-en noe som er i strid med kildedokumentet?

Ingen direkte faktafeil. To utsagn strekker seg lenger enn kilden bærer.

### Funn 7 — «det eneste som kan velte datagrunnlaget»

PRD-ens siste setning, seksjon 8:

> Punkt 1 er det eneste som kan velte datagrunnlaget, og er derfor det eneste med
> hard frist i denne uka.

Kildedokumentet har tre uavklarte rettighetsspørsmål som alle berører
datagrunnlaget: Euronext/NewsWeb (= punkt 1), **EODHDs fullstendige ToS** (bærer
alle kursdata), og **Alpha Vantage** (allerede brukt i tidlige tester). Legger
man til funn 1 — mediekilden til relevanseksperimentet — blir setningen en
undervurdering, ikke en prioritering.

Setningen er ikke gal om vilkårene for de andre viser seg å holde. Men den er
formulert som en konklusjon, ikke som en vurdering, og den hviler på tre
kontroller som ennå ikke er gjort. Den gjør det også lettere å ikke føre de
andre punktene inn i tabellen — slik de faktisk ikke er ført.

**Forslag:** «Punkt 1 er det eneste med hard frist denne uka. De øvrige
vilkårskontrollene — EODHDs fullstendige ToS og kilden til medieartiklene — kan
også velte deler av datagrunnlaget, men har senere frist.»

### «Kildestatus og kontrollerte vilkår er dokumentert i docs/kilder-og-rettigheter.md»

Seksjon 6 innleder slik, og fortsetter: «Dette avsnittet fører bare det som er et
krav eller en åpen forpliktelse i PRD-sammenheng».

Avgrensningen er riktig i prinsippet. Problemet er at tre av kildens fire åpne
forpliktelser *er* åpne forpliktelser, og likevel ikke ført. Setningen lover en
utvelgelse som ikke er gjennomført, og lener seg på at leseren går til
kildedokumentet — noe seksjon 8 ikke inviterer til, siden den presenterer seg som
«Samlet oversikt».

---

## 7. Foreslåtte rettinger, i prioritert rekkefølge

| # | Retning | Hvor |
|---|---|---|
| 1 | Nytt blokkerende åpent punkt: kilde og vilkår for de 50 medieartiklene i relevanseksperimentet. Eier, frist før uke 41 | Seksjon 8 |
| 2 | Nytt åpent punkt: lese EODHDs fullstendige ToS, ikke bare prissiden. Eier, frist før signalparametrene låses | Seksjon 8 |
| 3 | Fyll inn eier på punkt 1 — og på de øvrige punktene | Seksjon 8 |
| 4 | Nytt åpent punkt: kontrollere Alpha Vantage sine vilkår for ikke-kommersiell bruk (kilden er allerede brukt i tidlige tester) | Seksjon 8 |
| 5 | Rett den betingede forpliktelsen: *vilkårene* vurderes på nytt ved *publisering*, ikke bare videreformidlingsrett ved kommersialisering. Før som åpent punkt med betingelse | Seksjon 2 + 8 |
| 6 | Legg inn de tre forkastede EODHD-endepunktene med grunn — særlig HTTP 403 på kalenderen, som er begrunnelsen for Euronext | Seksjon 6 |
| 7 | Gjenta premisset om lokal, ikke-kommersiell bruk øverst i rettighetskapittelet | Seksjon 6 |
| 8 | Nyanser «det eneste som kan velte datagrunnlaget» | Seksjon 8, siste avsnitt |
| 9 | Utvid E24-gjengivelsen: forbudet dekker også trening, finjustering og **evaluering**, og gjelder overskrifter og metadata, ikke bare brødtekst | Seksjon 6 |

Rettingene 1–4 er de som endrer risikobildet. 5–9 gjør PRD-en etterprøvbar for
en leser som ikke har kildedokumentet ved siden av.
