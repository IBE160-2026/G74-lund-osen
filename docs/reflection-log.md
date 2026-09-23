# Refleksjonslogg – IBE160 Programmering med KI

Denne loggen føres kort underveis for å dokumentere arbeidsprosess, valg, KI-bruk, utfordringer og læring. Viktige KI-prompts lagres separat i `docs/ai-prompts/`.

---

## 13.09.2026 – Marian

### Fase
Idémyldring og prosjektvalg

### Hva gjorde jeg?
Vi kom litt sent i gang og brukte dagen til å få oversikt over oppgaven. Appendix A og faglærerens prosjektforslag ble lagt inn i ChatGPT. Vi hadde to svært ulike egne ideer på bordet, en fra hver av oss: et krim-/mordmysterie og en løsning for KI-støttet aksjeanalyse.

### KI-bruk og refleksjon
ChatGPT ble brukt som sparringspartner for å undersøke muligheter, omfang og hva som kunne være realistisk for to personer. Vi bestemte at KI ikke skulle velge prosjektet for oss. Først skulle vi tenke gjennom ideene hver for oss, og deretter sammenligne dem mer systematisk.

Det ble tydelig at vi må vurdere mer enn hvilken idé som virker mest spennende. Gjennomførbarhet, faglig innhold, KI-bruk, motivasjon og nytteverdi må også tas med.

---

## 14.09.2026 – Marian

### Fase
Forberedelse

### Hva gjorde jeg?
Fikk hjelp til å få tilgang til HiMolde-e-postkontoen og begynte å se forelesningsopptak i Panopto for å få bedre oversikt over emnet og prosjektkravene.

### Refleksjon
Siden vi kom sent i gang, var det viktig å få kontroll på kursressursene før vi gikk videre. Forelesningene brukes også som grunnlag når vi vurderer om prosjektideene passer til det faglærer forventer.

---

## 15.09.2026 – Marian

### Fase
Teknisk oppsett og videre prosjektvurdering

### Hva gjorde jeg?
Utviklingsmiljøet ble gjort klart med:
- Git og GitHub
- VS Code
- Node.js og npm
- Python via uv
- Docker Desktop og WSL2
- Claude Code
- GitHub CLI

Gruppens repository `G74-lund-osen` ble klonet, og BMAD ble installert i prosjektet.

Vi valgte:
- BMad Method
- BMad Creative Intelligence Suite som ekstra modul
- Claude Code og Codex som integrasjoner
- norsk som språk i BMAD
- `Lund og Osen` som felles navn i BMAD-oppsettet

Creative Intelligence Suite ble valgt fordi den kan være nyttig i idé- og planleggingsfasen. Codex ble tatt med slik at vi senere kan sammenligne flere KI-verktøy ved behov.

### KI-bruk
ChatGPT ble brukt til stegvis installasjon, feilsøking og hjelp til å avgrense prosjektmulighetene. Claude Code ble først tilgjengelig for oss denne dagen. Planen er derfor å bruke ChatGPT i den tidlige idé- og vurderingsfasen, og Claude Code mer aktivt når vi går videre med BMAD og utvikling. På enkelte viktige punkter kan vi bruke begge og sammenligne forslagene.

### Prosjektvalg
Vi har fortsatt ikke bestemt hvilket prosjekt vi skal gå videre med. Vi står mellom to svært forskjellige ideer, og begge gruppemedlemmene hadde hver sin idé.

Krim-/mordmysterieideen ser ut til å kunne gi en interessant KI-rolle dersom den avgrenses godt. Aksjeideen har mer direkte praktisk nytteverdi for oss. Hvis nytteverdi alene skulle avgjøre, peker aksjeideen seg foreløpig ut.

### Refleksjon
Vi ønsker ikke å velge prosjekt bare fordi en idé virker spennende eller nyttig. Vi må finne ut hvilken idé som er realistisk for to personer, gir nok faglig innhold og er motiverende å arbeide med over tid.

Det tekniske oppsettet viste også at det er en forskjell mellom verktøy som er nødvendige for kurset og ekstra verktøy vi selv velger fordi de kan være nyttige. Dette bør vi kunne begrunne senere.

Neste steg er å vurdere de to prosjektideene nærmere før vi låser valget. Etter prosjektvalget går vi videre med `proposal.md` og BMAD-prosessen.

### Tekniske utfordringer
Under oppsettet oppstod blant annet problemer med npm i PowerShell, WSL2/Docker og innlogging i Claude Code. Problemene ble løst underveis ved hjelp av KI-veiledning og kontroll av installasjonene.


## 16.09.2026 – Marian

### Fase
Prosjektvurdering og testing av datakilder

### Hva gjorde vi?
Vi undersøkte om aksjeideen er realistisk før vi bestemmer prosjektvalg. Målet var å finne ut om vi faktisk kan hente nok data til en løsning som analyserer Oslo Børs og samtidig bruker globale markeder som støtteinformasjon.

Alpha Vantage ble først testet på 10 norske selskaper. Selskapene ble funnet, men Oslo Børs-noteringene kom ikke tydelig frem. Alpha Vantage ble derfor vurdert som lite egnet som hovedkilde for norske aksjer.

EODHD ble deretter testet. Frontline ble testet først, og etter at dette fungerte ble ytterligere ni selskaper testet. Alle 10 Oslo Børs-aksjene ga historiske data med open, high, low, close og volum. Det ble også testet data for OSEBX, Frontline i USA og USD/NOK.

Globale datakilder ble videre testet for Brent, naturgass, Bitcoin, gull og sølv. Gull og sølv fungerte gjennom Alpha Vantage, mens de øvrige ble testet gjennom EODHD. Brent og naturgass hadde historiske data, men lå noen dager etter dagens dato. Det ble derfor sendt en forespørsel til Barchart om tilgang til ferskere futuresdata.

Euronext sin finanskalender ble også undersøkt. En CSV med fremtidige finanshendelser kunne lastes ned og inneholdt blant annet rapportdatoer, selskapsnavn og hendelsestype. Kalenderen kan derfor brukes til å varsle om kommende kvartalsrapporter og andre viktige hendelser.

Det ble sendt forespørsel til EODHD om 50 % studentrabatt på historiske data.

### KI-verktøy brukt
ChatGPT ble brukt til å planlegge testene, lage lokale PowerShell-script, tolke API-resultater og vurdere hvilke datakilder som var egnet.

### Viktige valg eller problemer
Testene ble holdt lokalt og API-nøklene ble lagret i `.env`. Både `.env` og `local-tests/` ble lagt i `.gitignore` slik at API-nøkler og testfiler ikke lastes opp til GitHub.

En viktig erfaring var at det ikke er nok at en dataleverandør sier at den dekker globale aksjer. Dette må testes på de konkrete markedene prosjektet skal bruke. Alpha Vantage fungerte godt for gull og sølv, men EODHD fungerte bedre for Oslo Børs.

Det ble også tydelig at historiske data og ferske markedsdata ikke nødvendigvis bør komme fra samme leverandør.

### Hva fant vi ut / lærte?
Datatilgangen ser foreløpig god nok ut til at aksjeprosjektet fortsatt er realistisk. Vi har bekreftet at EODHD kan hente data for de norske aksjene vi testet, og at globale signaler som valuta, råvarer, Bitcoin og utenlandske noteringer også kan hentes.

Finanskalenderen fra Euronext ser også brukbar ut. Den største datakilden som fortsatt må undersøkes nærmere er selskapsmeldinger og nyheter.

Prosjektet er fortsatt ikke endelig valgt, men datatestene har redusert usikkerheten rundt aksjeideen betydelig.

### Git / dokumentasjon
Testfiler og API-nøkler beholdes foreløpig lokalt og skal ikke lastes opp til GitHub. Resultatene og vurderingene dokumenteres i refleksjonsloggen.




---

## Mal for neste arbeidsøkt

### Dato / deltaker(e)
### Fase
### Hva gjorde vi?
### KI-verktøy brukt
### Viktig valg eller problem
### Hva fant vi ut / lærte?
### Git / dokumentasjon


## 17.09.2026 – ChatGPT sin refleksjon over arbeidet med OSE Signal

**KI-verktøy:** ChatGPT (GPT-5.6 Sol)  
**Tema:** Product Brief, avgrensning, KI-rolle og sammenligning med Claude  
**Status:** Dette er ChatGPT sin egen refleksjon over prosessen. Claude skal skrive en egen refleksjon fra sitt ståsted. Dette er derfor ikke gruppens endelige vurdering eller endelige Product Brief.

### ChatGPT sin refleksjon

I arbeidet med OSE Signal har jeg fungert som sparringspartner for gruppen. Jeg har foreslått funksjoner, vurdert scope, sammenlignet prosjektideen med kursmaterialet og hjulpet til med å formulere flere versjoner av Product Brief.

Prosessen viste tidlig at KI lett kan foreslå mange gode funksjoner som samlet gjør prosjektet for stort. Jeg bidro selv til dette. Selv etter at prosjektet skulle reduseres foreslo jeg blant annet flere visninger, sektoroversikt, flere tidsperioder og favoritter. Claude påpekte senere at dette i praksis kunne gjøre v1 større igjen, selv om forskningsdelen samtidig var blitt redusert. Dette var en relevant korreksjon.

Et viktig trekk ved arbeidet har derfor vært at ChatGPT og Claude ikke alltid har gitt de samme rådene. I stedet for å velge ett KI-verktøy som fasit har gruppen brukt uenighetene til å vurdere argumentene nærmere.

### Forskjeller mellom ChatGPT og Claude

ChatGPT hadde i starten større fokus på selve produktet, brukergrensesnittet og hvilke funksjoner som kunne gjøre OSE Signal nyttig og visuelt interessant. Jeg foreslo blant annet dashboard, sektorvisning, historikk og flere mulige utvidelser.

Claude var gjennom flere runder mer kritisk til omfang, evalueringsmetode og hvilke deler som faktisk ga mest faglig verdi. Claude var blant annet tydelig på at prosjektet ikke burde utvikle seg til et stort forskningsprosjekt om hvorvidt signalene slår markedet.

Et konkret eksempel var antall aksjer. Jeg foreslo først at antall aksjer kunne reduseres dersom KI-behandlingen av nyheter ble for treg eller kostbar. Claude utfordret dette og argumenterte for at kostnaden heller burde kontrolleres gjennom måling av faktisk nyhetsvolum, caching, artikkeltak og forfilter. Etter videre diskusjon vurderte jeg dette som en bedre løsning enn å redusere aksjeuniverset uten å ha målt problemet først.

Claude var også mer kritisk til detaljer i signalmodellen. Signalstyrke alene kunne bli misvisende fordi både sterke positive og sterke negative utslag kan gi høy styrke. Dette førte til en ny løsning med to separate felt: **signalstyrke** og **retning**, der retning kan være positiv, negativ eller blandet.

På andre områder har ChatGPT og Claude gradvis nærmet seg hverandre. Begge endte med å støtte en mindre og tydeligere v1, desktop-first design, et begrenset aksjeunivers, KI-filtrering av finansnyheter, forklarbar signalanalyse, lagring av daglige vurderinger og et tydelig skille mellom vanlig programkode og KI.

### To forskjellige Product Brief-utkast

Som en del av prosessen er det nå laget separate forslag til Product Brief basert på vurderingene fra ChatGPT og Claude.

De to versjonene er ikke helt like. De har utviklet seg fra forskjellige vurderinger av blant annet:

- hvor detaljert Product Brief skal være
- hvordan signalstyrke og retning skal beskrives
- hvilke funksjoner som må være med i v1
- hvilke funksjoner som bør ligge under Vision
- hvor mye evaluering og testing som skal beskrives i Product Brief
- hvordan målgruppe og femminutters-brukerreisen skal formuleres

Dette er bevisst. Gruppen har ikke valgt en av versjonene som endelig ennå.

Neste steg er å sammenligne de to Product Brief-utkastene og vurdere hvilke formuleringer og beslutninger som best følger faglærerens mal, prosjektets tidsramme og det produktet gruppen faktisk ønsker å bygge.

Den endelige Product Brief skal derfor være et resultat av gruppens vurdering av de to KI-forslagene, ikke en direkte kopi av teksten fra enten ChatGPT eller Claude.

### Viktigste lærdom fra ChatGPT sitt ståsted

Den viktigste lærdommen fra prosessen er at KI har vært mest nyttig når den brukes til å lage alternativer, utfordre valg og finne svakheter, ikke når den får definere prosjektet alene.

Flere av de beste beslutningene kom etter at et tidligere KI-forslag ble kritisert av den andre KI-en, kontrollert mot kursmaterialet eller vurdert på nytt av gruppen.

Prosessen har derfor vist en viktig forskjell mellom å **bruke KI til å produsere et svar** og å **bruke KI som del av en utviklingsprosess**.

I dette prosjektet har ChatGPT og Claude gitt forskjellige forslag, argumentert mot hverandres løsninger og bidratt til flere revisjoner. Gruppen må til slutt selv bestemme hvilke råd som skal følges, hvilke som skal forkastes og hvorfor.

Dette er også et viktig læringspunkt for IBE160: KI kan gjøre det mulig å utvikle mer avanserte løsninger med begrenset programmeringserfaring, men kvaliteten på resultatet avhenger fortsatt av at menneskene som bruker KI kan stille presise krav, kontrollere resultatene, oppdage svakheter og ta de endelige beslutningene.



## 17.09.2026 – Claude sin refleksjon over arbeidet med OSE Signal

**KI-verktøy:** Claude Code (Opus 5)
**Tema:** Product Brief, testing av nyhetsdata, avgrensning og sammenligning med ChatGPT
**Status:** Dette er Claude sin egen refleksjon fra sitt ståsted. ChatGPT har skrevet sin
egen ovenfor. Ingen av dem er gruppens endelige vurdering eller endelige Product Brief.

### Dato / deltaker(e)

17.09.2026 – Marian, i arbeidsøkt med Claude Code.

En presisering som hører hjemme i en logg om KI-bruk: deler av dagens diskusjon mellom
gruppen, ChatGPT og Claude foregikk i tidligere økter samme dag. I denne økten hadde jeg
ikke tilgang til de samtalene. Der jeg omtaler tidligere Claude-innspill, gjengir jeg
begrunnelsen bak posisjonen, ikke ordrett hva som ble sagt. Det ordrette står i ChatGPT sin
refleksjon og i gruppens egne notater.

### Fase

Planlegging. Avgrensning av v1, testing av nyhetsdata som siste åpne datakilde, og
utarbeidelse av et eget Claude-utkast til Product Brief for sammenligning.

### Hva gjorde vi?

Økten startet med å kartlegge hvor prosjektet faktisk stod: refleksjonsloggen var ført til
og med 16.09, `_bmad-output` var tom, og det nyeste arbeidet lå utenfor repoet i form av
flere Product Brief-versjoner i nedlastingsmappen.

Deretter ble `local-tests/test-news.ps1` kjørt mot EODHD sitt news-API for DNB.OL og
FRO.OL. Dette var den datakilden refleksjonsloggen 16.09 pekte på som den siste store
usikkerheten.

Til slutt ble det skrevet et eget Claude-utkast til Product Brief etter BMAD-malen, slik at
gruppen kan sammenligne to uavhengige utkast i stedet for å redigere ett.

### KI-verktøy brukt

Claude Code (Opus 5) i denne økten, til statuskartlegging, kjøring og tolkning av
nyhetstesten, og til å skrive Product Brief-utkastet. ChatGPT ble brukt parallelt av
gruppen til sin egen versjon av samme dokument.

### Viktig valg eller problem

**Nyhetsstøyen ble målt, ikke antatt.** Begge KI-verktøyene hadde tidligere argumentert for
at KI trengs til å filtrere finansnyheter. Ingen av oss kunne vite hvor stort problemet
faktisk var. Testen ga et konkret svar: for DNB.OL kom det ti nyheter, men flere av dem
handlet i realiteten om Infosys, om europeiske aksjer generelt eller om andre selskaper som
SalMar, Cadeler og OTP Bank, og nevnte DNB bare fordi selskapet var ett av mange symboler
i artikkelen. For FRO.OL var bildet motsatt: nyhetene var i hovedsak faktisk om Frontline
eller om oljemarkedet selskapet opererer i.

Det har to konsekvenser for prosjektet. Relevansvurderingen er ikke en forbedring på toppen
av nyhetsvisningen, den er selve funksjonen. Og nyhetsvolumet varierer kraftig mellom
selskaper, noe som betyr at KI-kostnaden må styres etter faktisk målt volum per ticker.

**Signalstyrke og retning.** Begrunnelsen for å dele signalet i to felt er at styrke alene
slår sammen to motsatte tilstander: et kraftig positivt og et kraftig negativt utslag gir
begge høy styrke. Et tall som ikke skiller disse fra hverandre er verre enn ubrukelig i et
produkt som skal være forklarbart, fordi brukeren vil lese det som et kjøpssignal.

**Mitt eget omfangspress er også en risiko.** Jeg har gjennom prosessen dratt i retning av
mindre v1 og mot å gjøre prosjektet til en større studie av om signalene slår markedet. Det
er riktig for gjennomførbarheten, men det er ikke gratis: når forskningsdelen fjernes, må
det faglige innholdet komme fra et sted, og da må applikasjonen selv være teknisk
substansiell nok. Gruppen bør holde meg ansvarlig for den avveiningen, ikke bare følge
kutteforslagene.

### Hva fant vi ut / lærte?

**Én test slo begge KI-verktøyene.** Spørsmålet om nyhetsstøy hadde vært diskutert av både
ChatGPT og Claude uten at noen av oss kunne avgjøre det. Femten sekunder med et API-kall ga
et bedre svar enn begge argumentasjonsrekkene. Lærdommen er ikke at KI tar feil, men at KI
resonnerer om verden mens tester måler den, og at det alltid er verdt å spørre om en
påstand kan testes i stedet for diskuteres.

**De to verktøyene har hver sin systematiske slagside.** ChatGPT trekker mot å utvide:
flere visninger, flere funksjoner, mer nytte. Claude trekker mot å stramme inn: færre
funksjoner, tydeligere grenser, mindre lovnader. Ingen av delene er riktig i seg selv. Det
er to forskjellige feilmåter, og verdien lå i at de to feilmåtene korrigerte hverandre. Et
prosjekt som bare hadde brukt det ene verktøyet ville fått enten et for stort eller et fortynt prosjekt, og ville ikke merket det.

**KI-påstander må måles, også når KI-en er meg.** Et konkret eksempel fra denne økten: oppgaven var blant annet å korte ned Product Brief. Mitt utkast endte på 1249 ord mot ChatGPT sine 1235 — altså like langt. Jeg hadde flyttet ord, ikke fjernet dem, og ville
trolig beskrevet resultatet som strammere hvis ikke en ordtelling hadde vist noe annet. Dette er et nyttig eksempel til rapporten: KI beskriver gjerne sitt eget arbeid i tråd med intensjonen, ikke i tråd med resultatet, og gruppen må sjekke resultatet.

**Uenighet var mer produktiv enn enighet.** Der ChatGPT og Claude var enige, gikk vi videre
uten å undersøke noe. Der vi var uenige — antall aksjer, kostnadsstyring, evalueringsambisjon — måtte gruppen selv gå inn i argumentene og ta et valg. De valgene er de eneste vi kan begrunne ordentlig i rapporten, nettopp fordi de ikke ble tatt av et verktøy.

---

## 19.09.2026 – Verifisering av datakilder og opprydding i Product Brief

**KI-verktøy:** Claude Code (Opus 5)
**Tema:** Måling av API-kvote, verifisering av datakilder, bruksvilkår, og tilpasning av
Product Brief til BMAD-malen
**Merknad:** Økten startet kvelden 19.09 og fortsatte over midnatt til 20.09.
**Frist:** Ny innleveringsdato for BMAD-leveransen er satt til søndag 27.09.2026 (uke 39).

### Dato / deltaker(e)

19.09.2026 – Marian, i arbeidsøkt med Claude Code.

### Fase

Planlegging, siste del. Verifisering av datagrunnlaget før arkitekturen låses, og
ferdigstilling av Product Brief mot emnets mal.

### Hva gjorde vi?

Økten begynte med et krav om å bruke så få API-kall som mulig, og med at alle kall skulle
telles. Totalt ble det brukt **tre kall** mot EODHD. Alt annet ble avklart gjennom
dokumentasjon, gjennom kall som ble avvist uten å belaste kvoten, eller gjennom kilder som
ikke bruker kvote i det hele tatt.

Fire spørsmål ble besvart:

1. **Kvote.** `/api/user` viste gratisnivå, 20 kall i døgnet og 485 bonuskall som ikke
   fornyes. Endepunktet koster ingenting.
2. **Bulk-endepunkt for sluttkurser.** Dokumentasjonen oppgir 100 kall flatt per kall.
   Testen ble ikke kjørt, fordi kostnaden alene avgjorde saken: 100 kall er fem ganger
   dagsgrensen.
3. **Nyheter med flere symboler.** Avvist med HTTP 422 og teksten «Only one ticker is
   allowed in parameter s». Kostnaden er 5–10 kall per forespørsel.
4. **Kalender.** HTTP 403: «Only EOD data allowed for free users». Calendar API dekkes
   ikke av abonnementet. Euronext er dermed ikke lenger ett av to alternativer for
   finanskalender, men den eneste gratis veien.

Deretter ble norske RSS-kilder testet, uten kvotebruk. Av E24, DN, Finansavisen, Hegnar,
Kapital og NRK var E24 den eneste med fungerende finans-RSS. Til slutt ble Oslo Børs
NewsWeb funnet: et åpent JSON-API som ga 102 meldinger fra 73 utstedere for ett døgn, der
hver melding allerede er knyttet til utsteder og kategori.

Product Brief ble så ryddet: arkitekturstoff flyttet ut, lengden kuttet, og dokumentet
sjekket mot sluttsjekken i emnets mal. `docs/kilder-og-rettigheter.md` og
`_bmad-output/planning-artifacts/prd-notater.md` ble opprettet.

### KI-verktøy brukt

Claude Code (Opus 5) til måling, dokumentasjonssøk, verifisering av bruksvilkår og
redigering. Gruppen styrte prioriteringene og tok beslutningene underveis.

### Viktig valg eller problem

**E24 forbyr bruken vi hadde planlagt.** Feeden fungerte teknisk, men dens eget
`description`-felt forbyr eksplisitt å bruke innholdet som input til språkmodeller. Det
rammet arkitekturen direkte, siden planen var at KI skulle avgjøre hvilket selskap en
artikkel handler om. Kilden ble forkastet på grunn av vilkårene, ikke på grunn av
kvaliteten. Det er verdt å merke seg at gratis og offentlig tilgjengelig ikke er det samme
som tillatt å bruke.

**NewsWeb løste et problem og truet samtidig problemstillingen.** Fordi hver melding
allerede er merket med utsteder, forsvinner attribusjonsproblemet som hele KI-laget var
begrunnet med. Da står KI igjen med oppsummering, og det er nettopp det tynne laget vi
hadde advart mot. Løsningen ble en deling: NewsWeb driver produktet daglig og koster null
kvote, mens de 485 bonuskallene brukes én gang til et avgrenset relevanseksperiment som
dokumenterer påstanden. Problemstillingen overlever fordi den blir målt, ikke fordi den
blir gjentatt.

**Aksjeuniverset ble utledet, ikke valgt.** Med 20 kall i døgnet og ett kall per symbol
ble taket 15 aksjer. Briefen sa tidligere 30–40. Tallet er nå skrevet inn med begrunnelsen
ved siden av, slik at det ikke kan skli tilbake uten at noen aktivt fjerner premisset.

**Arkitektur i feil dokument.** Briefen hadde fått et avsnitt om API-kvoter, bakgrunnsjobb
og caching. Emnets mal er eksplisitt på at The Solution skal beskrive opplevelse og utfall,
ikke implementasjon. Stoffet ble flyttet til `prd-notater.md`, og kvotebegrunnelsen fikk en
egen kort seksjon «Data og kilder».

### Hva fant vi ut / lærte?

**Avviste kall er gratis.** Både 403-svaret fra kalenderen og 422-svaret fra nyhetene lot
kvoten stå urørt. Det betyr at endepunkter kan prøves ut billigere enn vi trodde, og at
usikkerhet om tilgang ikke er en god grunn til å la være å teste.

**Dokumentasjon og virkelighet er ikke det samme, i begge retninger.** EODHDs prisside sier
at gratisnivået ikke har real-time. Kallet fungerte likevel. Konklusjonen ble å ikke bygge
på det: når tilgangen enten er en feil eller knyttet til bonuspakken, kan den forsvinne
uten varsel. Samme forbehold gjelder NewsWeb, som er udokumentert backend for Oslo Børs'
egen nettside. Derfor lagres rådata fra første kjøring.

**Estimater på eget arbeid bommet igjen.** Dette gjentok lærdommen fra 17.09. Kuttlisten
anslo at briefen skulle ned mot 980 ord. Den landet på 1 201. Prosaen var strammere enn
antatt, og det som gjensto bar innhold. Uten ordtelling underveis ville resultatet blitt
beskrevet som «betydelig kortet ned». Ordtelling etter hver runde er billig og bør være
rutine.

**Påstand mot verifisering, også om oss selv.** Refleksjonsloggen slo tidligere fast at
`.env` var lagt i `.gitignore`. Det ble nå kontrollert: nøkkelen finnes ikke i noen commit
i noen branch, og filen har aldri vært sporet. Forskjellen på «vi la den i gitignore» og
«ingen treff i historikken» er den samme forskjellen som gikk igjen hele økten — antatt mot
målt.

**Neste steg er å bygge før vi skriver mer.** Prosjektet har nå fire
planleggingsdokumenter og ingen kjørende kode. Den tynne vertikale skiva — fem aksjer,
kurser fra EODHD, én skjerm, ingen KI — bør bygges før PRD skrives. Fem aksjer er fem kall,
så den kan kjøres flere ganger daglig uten å nærme seg kvoten.

**Fristen strammer dette inn.** BMAD-leveransen er flyttet til søndag 27.09.2026, altså én
uke fra nå. Det gir omtrent sju dager til både den vertikale skiva og det som måtte kreves
av BMAD-artefakter. Vi bør avklare tidlig i uken hvilke av stegene etter Product Brief som
faktisk er innleveringskrav, siden svaret avgjør om tiden går til kode eller til PRD og
arkitekturdokument. Et forhold å merke seg: relevanseksperimentet står oppført til uke 40 i
Product Brief, som begynner 28.09 — altså dagen etter fristen. Enten er eksperimentet
knyttet til en senere innlevering enn BMAD-leveransen, eller så må datoen flyttes.

### Git / dokumentasjon

Nye filer: `docs/kilder-og-rettigheter.md` med kildestatus, siterte bruksvilkår og
sjekkedatoer, og `_bmad-output/planning-artifacts/prd-notater.md` med arkitekturstoffet som
ble flyttet ut av briefen. Product Brief er oppdatert til 1 215 ord og består sluttsjekken
i emnets mal. Duplikatregelen for `.env` i `.gitignore` ble fjernet, og det ble verifisert
at filen fortsatt er ignorert etterpå.

### Plan for neste økt: en tynn vertikal skive

Vi starter med det minste som går hele veien gjennom systemet — fra datakilde til skjerm —
i stedet for å bygge ett lag ferdig om gangen. Motsatsen er å bygge lagvis: først all
datahenting, så logikken, så grensesnittet. Da virker ingenting før helt til slutt, og
integrasjonsfeilene dukker opp altfor sent.

Konkret: hent sluttkurser for fem aksjer fra EODHD, lagre dem lokalt, og vis dem på én
webside med navn, kurs og endring i prosent. Ingen KI, ingen børsmeldinger, ingen kalender,
ingen indikatorer, ingen graf. Fem rader i en tabell.

Det ser for lite ut, og det er poenget. Når den virker, er det bevist at API-nøkkelen
fungerer, at data kan lagres og leses tilbake, at webserveren kjører, og at de tre delene
snakker sammen. Fem aksjer er fem API-kall, så skiva kan kjøres flere ganger daglig uten å
nærme seg kvoten på 20.

Rekkefølgen videre: flere aksjer → kursgraf → indikatorer og signalstyrke → børsmeldinger
fra NewsWeb → KI-laget → kalender. Ett steg om gangen, der hvert steg gir noe som fortsatt
virker.

**Dette er ikke en omvei rundt PRD-en.** BMAD-kjeden går Brief → PRD → UX → Arkitektur, og
emnet lærer bort den metoden; å hoppe over et ledd kan koste ved sensur. Poenget er å ikke
skrive PRD-en blindt. Når skiva er bygget, vet vi hvordan dataene faktisk ser ut når
kravene skal beskrives. Det tar en kveld, og PRD-en blir bedre av det.

---

## 20.09.2026 – Eksport av Product Brief, og et problem som aldri fantes

**KI-verktøy:** Claude Code (Opus 5), i samspill med en annen KI-assistent i en parallell økt
**Tema:** Eksport av Product Brief til Word og PDF, mappestruktur i README, og to feil som
oppsto i arbeidsflyten mellom to KI-assistenter

### Dato / deltaker(e)

20.09.2026 – Marian, i arbeidsøkt med Claude Code.

### Fase

Ferdigstilling av Product Brief før BMAD-leveransen 27.09.

### Hva gjorde vi?

Briefen skulle eksporteres for innsending. Claude Code laget først en PDF på fire sider fra
markdown-filen, med eget oppsett. Den andre økten hadde laget en Word-fil på to sider med
samme tekst. Forskjellen var ren typografi — skrifttype, marger, linjeavstand — men den
betydde noe, fordi BMAD-malens sluttsjekk har «1–2 pages» som eget punkt.

Underveis ble det oppdaget at Word-filen lå én commit bak repoet: den sa fortsatt «ingen
teknisk moat», formuleringen som var byttet ut i commit `aeb667b`. Word-filen ble rettet mot
repoversjonen, og PDF-en bygget fra Word-filen, slik at sideantallet fulgte med.

I README ble det lagt inn et avsnitt om mappestruktur, som forklarer hvorfor `docs/` og
`_bmad-output/` er skilt: prosessen i den ene, produktdokumentene i den andre.

### To feil, begge i arbeidsflyten — ikke i filene

**Den første var et problem som aldri fantes.** Etter README-endringen viste Claude Code
resultatet med `tail -14`, altså bare de siste linjene. Utskriften begynte midt i filen, på
`## Medlemmer`. Den andre økten leste den avkortede utskriften som om den var hele filen,
konkluderte med at overskriften sto to ganger og at en setning var klippet inn i
mappestrukturen, og ba om opprydding. Filen var hel hele tiden. Samme økt meldte også at to
innliminger i Success Criteria hadde feilet; begge lå inne, i commit `59895e6`.

Tre ting ble bedt sjekket. Ingen av dem var feil i filene.

**Den andre feilen var reell, og gikk motsatt vei.** Word-filen skrev «prosjektinnlevering»
tre steder der repoet skrev «innlevering». Claude Code behandlet repoet som fasit og rettet
Word-filen etter det. Men presiseringen var bevisst: briefen har frist 27.09, mens de
kriteriene peker på prosjektets sluttinnlevering. Rettingen fjernet altså en presisering som
var satt med hensikt. Retningen ble snudd: repoet er oppdatert til «prosjektinnlevering», og
Word og PDF er bygget på nytt fra den versjonen.

### Refleksjon

Erfaringen er konkret nok til å ta med videre: to KI-assistenter som leser hverandres
utskrifter i stedet for filene, kan produsere et problem som ikke finnes — og bruke tid på å
fikse det. En `tail`-utskrift ser ut som en fil. Den er det ikke.

Den andre feilen har samme form, men på innholdssiden. «Repoet er kilden» er en god regel,
og den gjelder fortsatt. Men den sier ingenting om hvilken vei et avvik skal rettes. Der
Word-filen var nyere på ett punkt og repoet nyere på et annet, måtte begge avvik vurderes
hver for seg, og det krevde kunnskap ingen av assistentene hadde: at de to fristene er
forskjellige. Den kunnskapen fantes bare hos oss.

Begge feilene ble funnet fordi noe ble etterprøvd mot filene. Det er rutinen som er verdt å
ta med: be om hele filen, ikke referatet av den — og spør før et avvik rettes, når det ikke
er åpenbart hvilken side som har rett.

### Git / dokumentasjon

Product Brief oppdatert til «prosjektinnlevering» tre steder i Success Criteria. README
utvidet med mappestruktur og begrunnelsen for skillet mellom `docs/` og `_bmad-output/`.
Eksportene ligger utenfor repoet, i nedlastingsmappen.

---

## 20.09.2026 – Tilbakemelding fra faglærer, og en uformell inspection gate

### Dato / deltaker(e)

20.09.2026. Joakim Lund og Marian Osen. Tilbakemelding mottatt fra faglærer i IBE160.

### Fase

Overgangen fra Planning til Solutioning. PRD-arbeidet pågikk da tilbakemeldingen kom.

### Hva gjorde vi?

Mottok skriftlig tilbakemelding på Product Brief. Gjengitt ordrett:

> Jeg har sett gjennom briefen, og dette ser veldig bra ut. Dere har en tydelig ide, et
> fornuftig omfang og et godt skille mellom hva som løses med vanlig kode og hva KI faktisk
> skal brukes til.
>
> Når det gjelder Product Brief, trenger dere ikke presse inn alle detaljer der. Malen er
> ment som en fleksibel struktur, så det er helt greit å holde briefen overordnet og legge
> mer tekniske detaljer, datakilder, API-begrensninger og begrunnelser i PRD-en. Den ekstra
> delen deres om data og kilder passer også veldig naturlig inn.
>
> Formatet ser også helt fint ut. Det viktigste er innholdet og at strukturen er tydelig.
>
> Repoet deres er allerede offentlig i IBE160-organisasjonen, så det er også i orden.

### Hva tilbakemeldingen lukker

**Omfanget er bekreftet fornuftig.** Det åpne spørsmålet om ambisjonsnivå er lukket av
faglærer, ikke av oss selv. Det er en forskjell som betyr noe: vi har brukt tid på å
vurdere om universet på 15 aksjer og de to skjermbildene var for lite eller for mye.

**Fordelingen mellom brief og PRD er godkjent eksplisitt**, inkludert vår egen seksjon
«Data og kilder» som ikke står i malen. Det var den beslutningen som kunne kostet mest å ta
feil på — hele skillet mellom briefen som overordnet dokument og PRD-en som bærer tekniske
detaljer, datakilder, API-begrensninger og begrunnelser hviler på den. Hadde den vært feil,
måtte begge dokumentene skrives om.

**Formatkrav: ingen.** Det åpne punktet om forside, sidetall og skrifttype kan lukkes.
Innhold og tydelig struktur er det som teller.

**Repoet er offentlig i IBE160-organisasjonen.** Dette motsa antakelsen vår om et privat
repo under egen konto, og ble derfor kontrollert.

### Kontroll av repo-antakelsen

Antakelsen var feil, men ikke slik vi trodde. Det finnes ikke to repoer.

| Kontroll | Resultat |
|---|---|
| `git remote -v` | Ett remote: `IBE160-2026/G74-lund-osen` |
| GitHub API, uautentisert | `private: false`, `visibility: public` |
| Er `data/` sporet? | Nei — ligger i `.gitignore` |
| Er `.env` sporet? | Nei — ligger i `.gitignore` |
| Er `_bmad-output/` sporet? | Ja |

Rådata fra EODHD og API-nøkler er altså ikke eksponert. Det som er offentlig, er koden og
planleggingsdokumentene.

Men funnet har en konsekvens for PRD-en. Vi skrev inn i går at utløseren for å vurdere
bruksvilkårene på nytt er **publisering, ikke kommersialisering**. Koden er publisert. Selve
applikasjonen kjører fortsatt bare lokalt, og rådata er ikke videreformidlet, så vurderingen
er ikke utløst av datadeling. Men formuleringen i PRD-en forutsetter et repo som ikke er
offentlig, og den forutsetningen holder ikke. Dette må avklares i samme runde som den
øvrige vilkårskontrollen, med frist 27.09.

### Dette var en inspection gate

Det er verdt å kalle tilbakemeldingen det den var: en **inspection gate mellom Planning og
Solutioning**, slik BMAD beskriver dem — bare uformell. Den har alle kjennetegnene. Den kom
mellom to faser. Den ble gitt av noen utenfor arbeidet. Den bekreftet at grunnlaget holder
før neste fase bygger videre på det. Og den lukket fire spørsmål som ellers ville fulgt med
inn i arkitekturarbeidet som antakelser.

Forskjellen fra en formell gate er bare at vi ikke hadde planlagt den, og ikke bedt om den
på et bestemt tidspunkt. Det er tilfeldig at den kom nå.

### Refleksjon

Tre av de fire punktene bekreftet noe vi allerede trodde. Det fjerde motsa oss, og var det
mest verdifulle. Slik er det ofte med bekreftelse utenfra: verdien ligger ikke i de tre som
stemte, men i den ene som ikke gjorde det — og i at den kom før arkitekturarbeidet i stedet
for etter.

Verdt å merke seg at antakelsen om privat repo aldri ble skrevet ned noe sted. Den lå i
hodene våre, og styrte likevel en formulering i PRD-en. En antakelse som ikke er skrevet
ned, kan ikke etterprøves — den kan bare vise seg å være feil på et ubeleilig tidspunkt.

**Dette er speilbildet av de seks tapte kravene.** De seks var innhold som *var* skrevet
ned, og som forsvant i omskriving. Denne var innhold som *aldri ble* skrevet ned, og som
styrte en beslutning likevel. De to feilene ser motsatte ut, men har samme mekanisme:
ingen av dem finnes i en fil noen kan kontrollere. Et krav som er borte fra dokumentet, og
en antakelse som aldri kom inn i det, er begge usynlige for den samme sjekken.

Det har en praktisk konsekvens for tiltaket vi innførte tidligere samme dag. Diff mot
forrige versjon fanger den første typen. Den fanger ikke den andre — en antakelse som
aldri har vært i filen, dukker ikke opp som en forskjell mellom to versjoner. Skal den
fanges, må den skrives ned først, og da er den allerede halvveis løst.

Regelen som følger: når en beslutning hviler på noe vi tror om omgivelsene — at et repo er
privat, at en kilde er stabil, at en frist ligger der vi tror — skrives antakelsen ned
sammen med beslutningen, ikke bare beslutningen. Det er billigere enn å oppdage den når
den ryker.

### Git / dokumentasjon

Ingen filendringer utløst direkte av tilbakemeldingen. Det åpne punktet om formatkrav
lukkes. Spørsmålet om offentlig repo mot publiseringsutløseren tas inn i vilkårskontrollen
med frist 27.09.

---

## 20.09.2026 – Seks krav berget fra utkastmappa, og to måter å miste dem på

### Dato / deltaker(e)

20.09.2026. Joakim Lund og Marian Osen, under arbeidet med PRD-en.

### Fase

Planning, PRD-arbeid.

### Hva gjorde vi?

Under PRD-arbeidet dukket det opp et krav som ikke fantes i den leverte Product
Brief, men som stod i tre av utkastene. Det utløste en systematisk gjennomgang av
hele utkastmappa mot de leverte dokumentene.

### Mønsteret: seks detaljer

Dette var sjette gang substansielt innhold måtte hentes tilbake fra
`docs/ai-prompts/product-brief/`. De fem første ble berget i commit `270026d`:

| # | Detalj | Berget |
|---|---|---|
| 1 | Euronext-kalenderen oppgir ikke ticker eller ISIN — hendelser må kobles via oppslagstabell | `270026d` |
| 2 | Alpha Vantage forkastet som beslutning, ikke bare «brukt i tidlige tester» | `270026d` |
| 3 | Kategorifeltet skiller ikke en kontraktstildeling fra et sponsorat | `270026d` |
| 4 | Relevanseksperimentet bruker restkvoten på nyhets-API-et én gang | `270026d` |
| 5 | Usikkerhet måles også på om mange selskaper nevnes likeverdig i samme sak | `270026d` |
| 6 | «…uten at systemet tvinger frem et resultat» | 20.09 |

Ingen av dem er pynt. Detalj 6 styrer et konkret designvalg — kravet om
nøytralsone i trendsjekken, FR-702. Detalj 3 er hele begrunnelsen for at KI
brukes til relevansvurdering i det hele tatt.

Den umiddelbare lærdommen var at **når man leser for språk, leser man ikke for
hva som mangler.** Tiltaket ble en vane: etter hver omskriving, kjør en diff mot
forrige versjon og se spesifikt etter *krav som er borte*, ikke bare etter
formuleringer som er endret.

### To mekanismer, ikke én

Senere samme dag viste en grundigere gjennomgang at tapene har **to ulike
mekanismer**, og at tiltaket over bare fanger den ene.

**Mekanisme 1 — språkvask.** Kravet stod i alle fire utkast og falt i siste steg,
fra endelig kandidat til levert brief. En omskriving som skulle stramme inn, tok
med seg innhold. Hit hører kravet om dager uten tydelige signaler, kravet om at
dagens vurderinger lagres automatisk, og suksesskriteriet om grensesnitt og
stabilitet.

**Mekanisme 2 — byttet premiss.** Kravet ble ikke strammet bort. Det mistet
konteksten da kilden byttet fra medienyheter til NewsWeb, og ble aldri oversatt
til den nye kilden. Hit hører den tredelte relevansskalaen, kravet om at KI
identifiserer hendelsestype, og rådataene bak medietesten 17.09.

Forskjellen har en praktisk konsekvens: **en diff mot forrige versjon fanger bare
mekanisme 1.** Et krav som mistet premisset sitt, ser i diffen ut som et krav som
med rette ble fjernet — fordi konteksten det hang på, også er borte.

Mekanisme 2 krever et annet tiltak: når et premiss byttes — en datakilde, en
brukergruppe, en plattform — gjennomgås kravene som hang på det gamle premisset
**ett for ett**, og hvert av dem får en eksplisitt avgjørelse: oversatt til det
nye premisset, eller bevisst forkastet. Ingen skal falle ut ved taushet.

**En tredje observasjon, om formen:** de tyngste utelatelsene er setninger som er
kortet **bakfra**. Hovedpoenget overlevde, den kvalifiserende halen ikke.
«For et shippingselskap var bildet motsatt» er en slik hale — og det er nettopp
den som bærer poenget om at symbolstøyen varierer med selskapet, og som styrer
hvordan testsettet på 50 artikler må settes sammen.

### Vanen ble prøvd samme dag

Diff-vanen ble innført og tatt i bruk på den første omskrivingen etter at den ble
vedtatt: splittingen av PRD-en i et kravregister og et begrunnelsesdokument. Av
39 nummererte krav og 66 normative setninger fanget kontrollen **to reelle tap** —
dokumentets egen formålsetning, og en setning om at KI-laget skal behandle noen
få meldinger om dagen. Begge ble gjenopprettet.

To av 66 er ikke mye. Men uten kontrollen ville de vært borte, og ingen ville
merket det før kravet manglet i implementasjonen.

### Refleksjon

«KI-assistert omskriving strammer språket og mister krav» er en presis
observasjon om arbeidsmåten, ikke en generell betraktning om KI. Den har seks
dokumenterte eksempler fra dette prosjektet, hvert med en identifiserbar kilde i
utkastmappa og en identifiserbar konsekvens.

Det mest nyttige er likevel grensen vi fant for vårt eget tiltak: diff-vanen er
riktig, men den dekker bare halvparten av problemet, og vi vet nå hvilken
halvpart. Et tiltak man kjenner grensen til, er bedre enn et tiltak man tror
dekker alt.

Se også oppføringen om faglærertilbakemeldingen samme dag, der speilbildet dukket
opp: en antakelse som aldri ble skrevet ned, men som likevel styrte en
formulering i PRD-en.

### Git / dokumentasjon

Tre korreksjoner utført i Product Brief: rentejusteringseksempelet erstattet med
den målte støyen for vårt eget univers, rad om robusthet på stille dager lagt inn
i Success Criteria, og Scope-setningen om publisering omformulert til å skille
mellom publisering av kode og videreformidling av børsdata. Arbeidsnotatet
`korreksjon-til-brief.md` er slettet etter at alle tre var utført.


## 20.09.2026 – En test som var grønn av feil grunn

### Dato / deltaker(e)

20.09.2026. Joakim Lund og Marian Osen, under arbeidet med signalberegningen.

### Fase

Implementasjon. Første modul som ble bygget med tester ved siden av koden.

### Hva gjorde vi?

Signalberegningen (FR-701 til FR-705) ble skrevet sammen med tester på
håndlagde kursserier — serier der vi vet svaret på forhånd, fordi en feil i
signalet ikke gir en krasj, men et tall som ser plausibelt ut.

Testen for det enkleste tilfellet skulle gi signalstyrke 1: kursen over MA50,
dagens endring innenfor det normale, volum på medianen. Serien var laget slik:
tolv dager som steg nøyaktig 2 % hver dag, og en trettende dag som steg 0,2 %.

Den ga styrke 2. Bevegelsessjekken slo ut på 0,2 %.

### Hvorfor

Bevegelsessjekken måler dagens endring mot standardavviket til de foregående
dagene. En serie som stiger nøyaktig like mye hver dag har **standardavvik
null**. Da er enhver bevegelse større enn null, og sjekken slår ut på
ingenting.

Feilen lå ikke i koden. Koden gjorde nøyaktig det FR-701 beskriver. Feilen lå i
testdataene: de var så regelmessige at de ikke lignet på noe en børs kan
produsere, og de traff en degenerert grensetilstand i stedet for tilfellet
testen het at den testet.

### Hva vi gjorde med det

Vi rettet **dataene, ikke forventningen**. Serien stiger nå ujevnt — 1,5 %,
2,5 %, 1,8 %, 2,2 % — og standardavviket ble 0,4 %. Testen er grønn av riktig
grunn, og forklaringsteksten sjekken gir ut, `+0.2 % mot 0.4 % standardavvik`,
kan leses og kontrolleres.

At vi rettet dataene og ikke forventningen, er poenget. Forventningen kom fra
kravet. Hadde vi justert den til 2, ville testen vært grønn og kravet stille
endret — samme mekanisme som de seks kravene som forsvant i språkvask, bare på
et annet sted i kjeden.

### Refleksjon

**Syntetiske testdata kan være så rene at de tester noe annet enn du tror.**
Et datasett laget for å være enkelt å regne på for hånd, er også et datasett
uten variasjonen den ekte verdenen har, og statistiske sjekker oppfører seg
annerledes i grensetilfellene. Null varians, null volum, to identiske verdier
— alle er lovlige inndata som får terskler til å forsvinne.

Dette er et argument for håndlagde testdata *med* variasjon, ikke for hentede
testdata. Hentede data ville skjult feilen på en annen måte: de ville vært
grønne fordi tallene tilfeldigvis passet den dagen vi hentet dem.

Vi legger til en vane, ikke bare en rettelse: **når en test er grønn, sjekk
hva den faktisk regnet ut, ikke bare at den ble grønn.** Sjekkene i
signalberegningen bærer derfor en forklaringstekst med tallene de sammenlignet
— den er skrevet for grensesnittet (FR-706), men den gjør også testene
etterprøvbare.

### Git / dokumentasjon

`src/signalberegning.py` og `src/meldinger.py` med 41 tester i `tests/`, som er
sporet i git til forskjell fra `local-tests/`. Kjøres med `uv run pytest`, og
bruker ingen API-kall. Kravet om at hver story leveres med test er ført inn som
punkt 14 i PRD §8, slik at det følger med inn i arkitekturfasen.


## 20.09–21.09.2026 – Fem ganger på to døgn: påstander fra en økt uten tilgang til kilden

**KI-verktøy:** Claude Code (Opus 5) med repotilgang, i samspill med en
rådgivningsøkt uten
**Tema:** Hvordan indirekte referanser blir til påstander om tilstand — og i
tilfelle 4 til et sitat som ikke fantes

### Dato / deltaker(e)

20.09.2026. Marian, i arbeidsøkt med Claude Code.
Tilfelle 4 lagt til 21.09.2026, i samme arbeidsform.

### Fase

Ferdigstilling og opprydding, samme kveld som signalberegningen ble bygget.

### Hva gjorde vi?

To oppgaver kom inn fra rådgivningsøkta, begge formulert som tiltak som skulle
settes i gang:

1. **Rådata skulle ryddes ut av det offentlige repoet.**
   `data/volumsjekk-raa-2026-09-20.json` skulle fjernes fra sporing, og det ble
   reist spørsmål om historikken måtte skrives om mens Joakim ennå ikke hadde
   klonet.
2. **En patch skulle ha truffet feil overskrift** i
   `docs/kilder-og-rettigheter.md`, slik at EODHD-tekst lå under E24-overskriften
   og en linje sto to ganger.

### Ingen av dem stemte

`data/` ble gitignorert før den første målingen ble kjørt. Ingen fil under
`data/` har noen gang vært sporet — kontrollert på objektnivå ved å liste alle
blobs i historikken, ikke bare mot filnavn. Det fantes ingenting å fjerne og
ingen historikk å skrive om.

Overskriftene var riktige. Hver overskrift i dokumentet ble listet sammen med
teksten under seg, og ingen identiske nabolinjer finnes i fila. Adressen
`support@eodhistoricaldata.com` står tre steder med ulik tekst rundt, og to av
dem ligger fire linjer fra hverandre med en mellomoverskrift imellom.

### Hva grunnlaget faktisk var

Begge påstandene bygde på en **indirekte referanse**, ikke på filene:

| Påstand | Grunnlag | Hva det faktisk var |
|---|---|---|
| Rådata ligger eksponert | En linje i memloggen om at rådatafila «beholdes som tidsstemplet øyeblikksbilde» | En beslutning om å ikke slette fila lokalt — den sa ingenting om sporing |
| En patch traff feil overskrift | Et avkortet diff-utdrag | Utdraget viste en overskrift og tekst som lå i hver sin del av diffen |

### Dette er sjette gang

*Ført som «tredje gang, ikke andre» 20.09. Tilfelle 4 kom dagen etter,
tilfelle 5 samme kveld, og tilfelle 6 den 22.09. Tellingen er revidert tre
ganger — registeret er ført videre i stedet for å dateres om, fordi et mønster
som telles feil ser mindre ut enn det er.*

| # | Når | Påstanden | Hva kontrollen viste |
|---|---|---|---|
| 1 | Natt til 20.09.2026 | Brief-utkastene «finnes i repoet med historikk» | Seks av sju filer lå ikke der. Kontrollert med md5 |
| 2 | 20.09.2026, formiddag | Overskriften står to ganger, og en setning er klippet inn i mappestrukturen i README | Filen var hel. En `tail -14`-utskrift var lest som hele filen |
| 3 | 20.09.2026, kveld | Rådata ligger eksponert, og en patch traff feil overskrift | Verken rådata eller feilplassert tekst fantes |
| 4 | 21.09.2026, kl. 18:40 | En klausul fra Euronexts vilkår, oppgitt i anførselstegn | Setningen var ikke lest i kilden. Den var rekonstruert fra en avkortet linje i et referat |
| 5 | 21.09.2026, kl. 21:15 | «Joakims perspektiv finnes ikke i loggen» — lest som at han ikke hadde deltatt | Loggen viser hvem som *førte* oppføringene, ikke hvem som bidro. Kilden var et menneske, ikke en fil |
| 6 | 22.09.2026, ettermiddag | «AD-20 har nå to Prevents-punkter som sier det samme» — med instruks om å slette det ene | Det var ett. Kilden var en diff-visning, der den gamle linjen står over den nye. Arbeidsøkta talte punktene i fila i stedet for å gjøre som instruksen sa |

**Datering av tilfelle 1.** Utkastene ble lagt inn i repoet i commit `50d72d1`,
2026-09-20 kl. 00:31. Før den lå det bare `README.md` og
`prompt-log-template.md` i `docs/ai-prompts/`, uendret siden 15.09. Påstanden om
at utkastene fantes «med historikk» kan derfor ikke ha vært sann før `50d72d1`,
og md5-kontrollen hører hjemme i natten mellom 19. og 20. september. Selve
kontrollen er ikke loggført; kilden er at feilen ble erkjent i rådgivningsøkta.

### Den andre delen av funnet: erkjennelsen som ikke ble skrevet ned

Tilfelle 1 ble erkjent i samtalen, men bare muntlig. Det ble aldri ført i
loggen, og derfor førte det ikke til noe tiltak.

Mønsteret var altså **synlig allerede første gang**. Hadde erkjennelsen blitt
skrevet ned den natten, ville tilfelle 2 og 3 vært gjenkjennelige med én gang —
og tiltaket, som koster to kommandoer, ville vært på plass før den første av dem.

Det er verdt å si rett ut, fordi det generaliserer: **en feil som bare innrømmes
i samtalen, forsvinner.** Den etterlater ingen spor noen kan lese, ingen teller
som viser at det er tredje gang, og ingen regel som hindrer fjerde. Det er samme
mekanisme som de seks kravene som falt ut i språkvask, og som antakelsen om et
privat repo som aldri ble skrevet ned — ingen av dem finnes i en fil noen kan
kontrollere.


### Tilfelle 4: et sitat som ikke fantes

**21.09.2026 kl. 18:40.** Rådgivningsøkta oppga denne klausulen i
anførselstegn, til innføring i `docs/kilder-og-rettigheter.md`:

> Distribution outside the classroom or for other than solely educational
> purposes requires written permission.

**Setningen var ikke lest i kilden.** Den var rekonstruert fra en avkortet linje
i arbeidsøktas eget referat, der ordene var klippet midt i.

Faktisk ordlyd, kontrollert mot `https://www.euronext.com/en/terms-use`:

> Distribution outside the classroom or for other than solely educational
> purposes requires **express** written permission **in accordance with the
> above provisions**.

Arbeidsøkta kontrollerte mot kilden og rettet før innføring.

#### Hvorfor dette er verre enn de tre foregående

De tre første var **påstander om repotilstand**. De var etterprøvbare, og de lot
seg motbevise med to kommandoer. Her ble **ordlyden i et rettighetsdokument
oppdiktet, til bruk i et rettighetsdokument** — og den kunne ha endt i et brev
til rettighetshaveren, siden forespørselen til Euronext ble sendt samme dag.

Uten kontrollen ville et oppdiktet sitat stått som belegg. Det er den verste
formen feilen kan ta i dette prosjektet, fordi hele vilkårsarbeidet hviler på at
sitater er sitater: `kilder-og-rettigheter.md` skiller gjennomgående mellom hva
en kilde *sier* og hva vi *slutter*, og skillet er verdiløst hvis sitatsiden ikke
holder.

Det er heller ikke en tilfeldig detalj som forsvant. «Express» er nettopp det
ordet som gjør kravet strengere, og «in accordance with the above provisions»
binder unntaket til klausulene over det. En avkortet gjengivelse gjorde
forpliktelsen mildere enn den er — i vår favør.

#### Mønsteret var forutsagt i denne oppføringen

Avsnittet over, skrevet 20.09, sier at en feil som bare innrømmes i samtalen
etterlater «ingen teller som viser at det er tredje gang, og ingen regel som
hindrer fjerde».

Den fjerde kom under ett døgn senere. Telleren fantes denne gangen — den står i
tabellen over — og det er trolig grunnen til at kontrollen ble gjort før
innføring og ikke etterpå. Tiltaket virket. Det som manglet, var en regel som
dekket *denne* varianten, for tiltaket fra 20.09 gjelder påstander om
repotilstand, og et sitat fra et nettsted er ikke det.

#### Skjerpet tiltak

I tillegg til det som allerede står:

**Rådgivningsøkta skal ikke produsere ordrette sitater fra dokumenter den ikke
har lest selv i samme økt.** Der kilden mangler, skal det sies — ikke fylles.

Det generaliserer tiltaket fra 20.09 fra *repotilstand* til *kildeinnhold*:
påstander om hva en kilde inneholder, verifiseres i økta som har kilden, før de
føres. Et referat er ikke en kilde, og en avkortet linje i et referat er ikke et
sitat.


### Tilfelle 5: en tilstand sluttet av et tomrom, og kilden var et menneske

**21.09.2026, kl. 21:15.** Kartleggingen av refleksjonsrapporten førte opp tre
hull. Hull 3 sa: *«Joakims perspektiv finnes ikke i loggen.»* Formuleringen ble
lest som at han ikke hadde deltatt.

**Det stemmer ikke.** Joakim har bidratt med ideer som har formet prosjektet.
Det har skjedd utenfor de øktene som ble loggført, og derfor finnes bidragene
ikke i noen fil.

Grunnlaget for påstanden var at alle 14 oppføringene i loggen er ført av Marian
eller av en KI-økt. Men **loggen viser hvem som *førte* oppføringene; den viser
ikke hvem som bidro.** Et tomrom i en fil ble lest som en tilstand i verden —
nøyaktig samme feiltype som de fire over, der en avkortet utskrift, en
memlog-linje og et referat ble lest som kilden selv.

**Kilden er her et menneske og ikke en fil, og det gjør feilen verre, ikke
bedre.** De fire første gjaldt repotilstand, og tiltaket ble formulert deretter:
kontroller mot kilden. Dette tilfellet viser at regelen også gjelder slutninger
om mennesker — og at spørsmålet «hvor står det?» ikke er nok når svaret er «det
står ingen steder». Da er neste spørsmål hvem som vet det, ikke hvilken fil som
sier det.

Hullet er skrevet om til det det er: gruppens ene medlem har bidrag som ikke
finnes i noen fil. Det er et **dokumentasjonsproblem**, ikke et
deltakelsesproblem. Forskjellen er hele poenget — det første kan rettes, det
andre ville vært noe helt annet. Tiltaket er en egen seksjon nederst i denne
fila, som Joakim fyller ut selv.

### Refleksjon

**En økt uten tilgang til kilden kan ikke uttale seg om hva kilden inneholder —
bare om det den har blitt fortalt.** Det gjelder repoet i tilfelle 1–3, et
nettsted i tilfelle 4 og et menneske i tilfelle 5; mekanismen er den samme. Det er ikke en svakhet ved rådgivningen; en
memlog-linje om at en fil «beholdes» er en rimelig ting å bli bekymret av. Feilen
oppstår i overgangen, når en rimelig bekymring formuleres som et konstatert
faktum og pakkes som et tiltak.

Kostnaden er ikke bare bortkastet tid. Begge tiltakene var **inngripende**: det
ene ville fjernet filer fra sporing, det andre ville endret tekst under en
overskrift som var riktig. Historikkomskrivingen som ble vurdert, ville gitt nye
SHA-er for hele repoet og tvunget fram en ny kloning — for å fjerne noe som
aldri lå der.

Tiltaket er billig: **påstander om repotilstand verifiseres i økta som har
tilgang, før et tiltak settes i gang.** Det tok to kommandoer å avkrefte begge.

Det motsatte gjelder også, og er verdt å holde fast ved: rådgivningsøkta har
tatt riktige avgjørelser denne dagen som arbeidsøkta ikke ville tatt alene —
plan B for relevanseksperimentet, og at e-posten til EODHD skulle inneholde ett
spørsmål og ikke fire. Det er arbeidsdelingen som virker, med verifisering lagt
der tilgangen er.

### Git / dokumentasjon

Kontrollen av repoet er ført i `docs/kilder-og-rettigheter.md` under regelen om
hva som publiseres, og `.gitignore` er utvidet med mønstre for rådatafiler som
måtte havne utenfor `data/`. Tilfelle 2 er ført i oppføringen «Eksport av
Product Brief, og et problem som aldri fantes» tidligere samme dag. Tilfelle 1
har ingen egen oppføring og er ført her, i ettertid.

Tilfelle 4 er ført her 21.09. Den korrigerte ordlyden står i
`docs/kilder-og-rettigheter.md`, seksjonen «Undervisningsunntaket», og rettingen
er omtalt i commit-meldingen som førte klausulen inn.

Materiale til refleksjonsrapportens avsnitt om å arbeide med to KI-økter i
parallell.

---

## 21.09.2026 – Euronext forbyr det vi gjør, og vi fortsetter mens vi venter på svar

**KI-verktøy:** Claude Code (Opus 5) med repotilgang  
**Tema:** Vilkårskontrollen som gjorde prosjektets kjernekilde til dets største
åpne risiko — og beslutningen om å fortsette i mellomtiden

### Dato / deltaker(e)

21.09.2026, ettermiddag og kveld. Joakim Lund og Marian Osen. Kontrollen kostet
null API-kall.

### Fase

Slutten av planleggingsfasen. Vilkårskontrollen sto som åpent punkt 1 i PRD-en,
med merknad om at et negativt svar velter meldingsdelen.

### Hva ble gjort eller foreslått?

To dokumenter ble lest i sin helhet, ikke forsidene: `newsweb.oslobors.no/disclaimer`
og `euronext.com/en/terms-use`.

**Antakelsen fra 20.09 ble bekreftet:** de to kildene deler vilkår. Euronexts
domeneliste navngir både `oslobors.no`, `newsweb.oslobors.no` og
`live.euronext.com`, og Oslo Børs' egen side om ansvar og rettigheter
videresender nå til `euronext.com/en/terms-use`. Én kontroll dekket altså både
meldingene og finanskalenderen.

**Kilden tier ikke.** Tre klausuler treffer oss direkte, og den første er den
avgjørende:

> Except if we give you prior written permission, use of any Web browsers
> (other than generally available third-party browsers), engines, software,
> spiders, robots, avatars, agents, tools or other devices or mechanisms to
> navigate, search or determine the Euronext Website is strictly prohibited.

Det er en beskrivelse av det vi gjør. Vi henter med en programmert forespørsel,
ikke med en alminnelig nettleser, så unntaket i parentesen treffer ikke. I
tillegg forbys «systematic retrieval to create collections, compilations,
databases or directories» — en presis beskrivelse av meldingslageret i FR-406 —
og det som er tillatt uten avtale er «a single, unaltered, permanent copy» til
personlig, ikke-kommersiell bruk.

NewsWebs egen erklæring legger et norskrettslig lag oppå: databasen er vernet av
Åndsverkloven § 43, og erklæringen definerer selv nedlasting og lagring på
datamaskin som eksemplarfremstilling.

**Undervisningsunntaket** er den eneste åpningen vi har funnet i noen kilde i
hele prosjektet:

> Educational institutions may download and reproduce Content on the Euronext
> Website for distribution in the classroom solely for educational purposes.
> Distribution outside the classroom or for other than solely educational
> purposes requires express written permission in accordance with the above
> provisions.

**Men det er ikke opplagt at det dekker oss**, og det er tre grunner til det,
ikke én. Unntaket tillater nedlasting, mens forbudet rammer *midlene* — det
finnes intet tilsvarende unntak for software og verktøy, så den ene setningen
tillater resultatet og den andre forbyr veien dit. Klausulen er skrevet om
*institusjoner*: Høgskolen i Molde er en utdanningsinstitusjon, en studentgruppe
som kjører et prosjekt lokalt er ikke åpenbart det samme, og ikke åpenbart noe
annet. Og et offentlig repo er «distribution outside the classroom», selv når
det vi publiserer er utledet statistikk og ikke meldingene.

**En forespørsel om skriftlig tillatelse ble sendt samme dag** til
`copyrightpermissionsEurope@euronext.com`, adressen vilkårene selv oppgir. Den
beskriver fire ting med hver sin overskrift — henting, lagring, visning i
undervisning og det offentlige repoet — og spør om samme svar gjelder
finanskalenderen. Brevet er arkivert ordrett i `docs/epost-til-euronext.md`.

### Hva førte det til?

**Risikobildet byttet plass.** Fram til i dag var EODHD den usikre kilden, fordi
vilkårene der tier om språkmodellbruk. Den usikkerheten ble oppklart i dag — ja,
med betingelser. Euronext gikk motsatt vei: fra antatt uproblematisk til
uttrykkelig forbud. Børsmeldinger er kjernen i produktet. Det er dem KI-laget
skal forklare, og det er dem FR-501 til FR-503 og FR-601 til FR-606 handler om.
**Svaret fra Euronext er nå prosjektets største åpne risiko.**

**Beslutningen gruppen tok, ordrett slik den står i `kilder-og-rettigheter.md`:
hentingen fortsetter mens forespørselen er ubesvart, og faglærer varsles ikke.**

Begrunnelsen er todelt. Grunnlaget vi bygger på i mellomtiden er
undervisningsunntaket og det at forespørselen faktisk er sendt — ikke at
vilkårene tillater hentingen. Det gjør de ikke, og det står dokumentert. Og
uttrekket er ett per døgn for femten utstedere i et semesterlangt studieprosjekt;
å stoppe nå ville lammet meldingsdelen i den uken det er tid til å bygge den.

**Det den koster, skal stå like tydelig.** Vi henter fra en kilde som krever
tillatelse *på forhånd*, og vi har ikke fått den. Kommer det et nei 28.09, har
vi hentet i en uke uten hjemmel, og det er en uke vi selv valgte. At faglærer
ikke er spurt, betyr at ingen utenfor gruppen har veid dette — vi har verken
fått medhold eller blitt stoppet, og begge deler hadde vært verdt noe. Ansvaret
ligger dermed helt og holdent hos oss to, og det er ikke en formulering som
mykner hvis svaret blir nei.

Uteblir svaret innen 28.09, er det en ny beslutning som må tas: stoppe
hentingen, fortsette bevisst under undervisningsunntaket, eller bygge
meldingsdelen om. Den er ført som oppfølgingspunkt med eier, nettopp for at den
ikke skal bli tatt ved at ingen tar den opp.

### Refleksjon

**Å lese vilkår er billigere enn å anta dem, og det er ikke i nærheten.**
Kontrollen kostet null API-kall og en kveld. Alternativet var å bygge hele
meldingsdelen ferdig og oppdage forbudet i desember, når det ikke lenger finnes
tid til å bygge om.

**Det ubehagelige funnet er det mest verdifulle.** Fem kilder er nå kontrollert,
og Euronext er den eneste som både forbyr uttrykkelig *og* har et unntak som
kanskje gjelder oss. Et klart nei ville vært enklere å håndtere enn dette, fordi
et nei ikke krever en beslutning hver dag det står ubesvart.

**Vi valgte å skrive ned at vi ikke varsler faglærer.** Det hadde vært lettere å
la det være uskrevet — da ville det ikke vært en beslutning, bare noe som ikke
skjedde. Det er samme mekanisme som de fire tilfellene i oppføringen over: det
som ikke føres, etterlater ingen spor noen kan lese. Forskjellen her er at vi så
den mens den skjedde, og førte den mens den var ubehagelig.

### Git / dokumentasjon

Vilkårskontrollen med alle sitater står i `docs/kilder-og-rettigheter.md`,
seksjonen «Oslo Børs NewsWeb og Euronext: hva vilkårene sier». Brevet er
arkivert ordrett i `docs/epost-til-euronext.md`. Beslutningen står i «Beslutningen
gruppen har tatt i mellomtiden», og oppfølgingspunktet for 28.09 nederst i samme
fil, med eier Gruppen. Hver sin commit.

---

## 21.09.2026 – Faglærer om rammene: database, docker, stack og rapportens plass

### Dato / deltaker(e)

21.09.2026. Joakim Lund og Marian Osen. Svar fra faglærer i IBE160 på spørsmål om
rammene for prosjektet.

### Fase

Slutten av planleggingsfasen, dagen før arkitekturarbeidet skal begynne. Samme
dag som vilkårskontrollen og signaltesten ble gjennomført.

### Hva faglærer sa

Fire ting, sitert ordrett der ordlyden betyr noe.

**1. Database er i praksis et krav.**

> Hvis du ikke har behov for en database, så er prosjektet ditt for enkelt, noe
> som vil gjenspeile karakter. Vi har tre nivå: Enkel, Medium, Vanskelig. Alle
> tre nivåene innebærer database, så uten database vil dette påvirke karakteren
> hardt.

Supabase ble nevnt som eksempel, ikke som krav. Valget skal begrunnes i
applikasjonens behov.

**2. Innleveringen er «kildekode og docker fil».** Repoet har ingen Dockerfile.

**3. Teknologistacken er fri, men med en anbefaling.** Gruppen kan velge Python,
TypeScript eller en kombinasjon, men det er «en klar fordel å bruke omtrent
samme teknologistack som Bård Inge bruker i undervisningen», og undervisningen
bruker Node.js.

**4. Refleksjonsrapporten har ingenting med Product Brief å gjøre.**

> refleksjonsrapporten skal dere skrive ETTER dere har gjennomført prosjektet,
> og har ingenting med product brief å gjøre.

### Hvor de tre første er ført

| Punkt | Ført som |
|---|---|
| Database | Åpent punkt 17 i `prd.md`, eier Gruppen, frist ved oppstart av arkitekturfasen. Vurdering av hvilke krav som peker mot relasjonell lagring: `begrunnelser.md` §9 |
| Dockerfile | Åpent punkt 18 i `prd.md`, samme eier og frist |
| Teknologivalget | `begrunnelser.md` §10, skrevet ned som et bevisst avvik med kostnaden ført |

### Punkt 4: hva avklaringen endrer, og hva den ikke endrer

**Den endrer ingenting i det vi har gjort.** `docs/reflection-log.md` — denne
fila — er **råmateriale til rapporten, ikke rapporten**. Den er ført løpende
siden 13.09 fordi materiale som ikke skrives ned mens det skjer, ikke kan
gjenskapes i november. Den påvirkes ikke av avklaringen.

Det som er verdt å merke seg, er at vi hadde bygget en kobling som ikke finnes.
To steder i planleggingsdokumentene står det at en begrunnelse «hører også hjemme
i refleksjonsrapporten» — `begrunnelser.md` §1 og memloggen. Det er fortsatt
riktig som en notis om hva materialet kan brukes til. Men det var på vei til å
bli lest som at rapporten skulle *speile* PRD-en og briefen, og det skal den
ikke. Rapporten handler om **hvordan vi arbeidet**, skrevet i ettertid, ikke om
hva produktet ble.

**Rekkefølgen er dermed presisert:** brief → PRD → arkitektur → implementasjon →
demonstrasjon → *deretter* rapport. Rapporten er ikke et parallellspor som skal
holdes oppdatert underveis, og den er ikke et vedlegg til briefen.

### Refleksjon

Tre av fire punkter var rammer vi ikke hadde spurt om, og to av dem — database og
Dockerfile — er ting som ville blitt oppdaget i arkitekturfasen uansett. Men de
ville blitt oppdaget *da*, med mindre tid til å handle på dem.

Det fjerde er det mest nyttige, selv om det ikke krevde noen handling: **en
kobling vi hadde antatt, fantes ikke.** Ingen hadde bestemt at rapporten hang
sammen med briefen. Det hadde bare vokst fram av at begge er innleveringer i
samme emne, og av at vi skrev «hører hjemme i refleksjonsrapporten» i margen på
ting vi arbeidet med.

Det er samme mekanisme som antakelsen om et privat repo, ført 20.09: **en
antakelse som aldri ble skrevet ned, og som likevel styrte hvordan vi tenkte.**
Forskjellen er at denne ble oppdaget ved å spørre, ikke ved å kontrollere. Begge
veier virker. Den som ikke virker, er å la den stå.

### Git / dokumentasjon

Tilbakemeldingen er ført her ordrett. De tre første punktene er ført i `prd.md`
og `begrunnelser.md` som vist i tabellen over, med hver sin commit. Ingen kode er
endret.

---

## 21.09.2026 – To svar fra EODHD på under ett døgn, for prisen av én e-post

### Dato / deltaker(e)

21.09.2026. Marian Osen. Oppfølging til EODHD sendt kl. 19:33, besvart samme
kveld.

### Hva ble gjort eller foreslått?

Beslutningen 20.09 var å sende **ett** spørsmål til EODHD, ikke fire. Support
svarer erfaringsmessig på det letteste når flere stilles samtidig, og
språkmodellspørsmålet var det som blokkerte mest. De tre andre ble holdt
tilbake med vilje.

Da svaret kom 21.09 — ja, med fire betingelser — ble spørsmål 2 og 3 sendt i
samme tråd. Spørsmål 4 var da allerede avgjort av nyhetstesten, så det ble
aldri sendt.

### Hva førte det til?

Begge ble bekreftet samme kveld: «Yes, we confirm both». **To skriftlige svar
på under ett døgn, begge for prisen av én e-post.**

Det avklarte to ting vi allerede gjorde: demonstrasjonen for lærer og klasse,
og de aggregerte tallene i det offentlige repoet. Posisjonen
«sammendragsstatistikk er ikke databasen» gikk fra å ha ordlyd mot seg i tre
tekster til to.

### Refleksjon

**Bekymringen som ikke slo til.** Argumentet mot å sende en runde til var at
den kunne få EODHD til å tenke seg om og snevre inn det svaret vi allerede
hadde. Det skjedde ikke. Men det var ikke en dum bekymring — den var grunnen
til at spørsmålene ble sendt i riktig rekkefølge, med det viktigste først og
alene. Rekkefølgen var forsiktigheten; å utsette den andre runden i tillegg
ville bare vært utsettelse.

**Det svaret ikke dekker, er verdt like mye som det det dekker.** Spørsmål 2
nevnte to typer tall i samme setning — medianomsetning fra EODHD-kurser, og
kategorifordelinger fra NewsWeb-meldinger. «We confirm both» bekrefter to
*spørsmål*, ikke alle tallene nevnt i dem. EODHD kan uttale seg om sine egne
data og ikke om Euronexts. Hadde vi ført svaret som «de aggregerte tallene er
klarert», ville vi gitt oss selv en tillatelse ingen har gitt oss — og det på
den kilden som er prosjektets største åpne risiko.

**Det som gjenstår, er ikke noe EODHD skal svare på.** Betingelse 4 i
godkjenningen — at modelltjenesten ikke trener på innholdet vi sender inn — er
en plikt de la på oss. Den kan ikke lukkes med en e-post til dem, bare ved å
velge en modelltjeneste og sitere dens vilkår. Den står fortsatt åpen, fordi
ingen modell er valgt ennå.

### Git / dokumentasjon

Svaret er ført ordrett i `docs/kilder-og-rettigheter.md`, seksjonen
«Oppfølgingen samme kveld: begge bekreftet», sammen med begge spørsmålene slik
de ble sendt. De to oppfølgingspunktene om «displaying» og «repackaged form» er
lukket, og `docs/epost-til-eodhd.md` er oppdatert med at spørsmål 2 og 3 er
sendt og besvart. Hver sin commit.

---

## 21.09.2026 – Kvelden: seks rettinger i briefen, repoet som kart, og en dato ingen hadde flyttet

**KI-verktøy:** Claude Code (Opus 5) med repotilgang  
**Tema:** Dokumentene innhentet dagens funn — og to ting som hadde stått uendret
fordi ingen tok dem opp

### Dato / deltaker(e)

21.09.2026, kveld. Marian Osen med Claude Code.

### Fase

Etter at vilkårskontrollen, målingene og EODHD-svarene var i havn. Ingen ny
undersøkelse; arbeidet var å få dokumentene til å si det dagen hadde vist.

### Hva ble gjort eller foreslått?

**Briefen, seks endringer i seks commits.** Scope sa at videreformidlingsretten
var utsatt til eventuell publisering — en setning som forutsatte et privat repo,
og som var uriktig etter at kontrollen faktisk var gjort. NewsWeb sto omtalt som
en avklart kilde. Setningen «Til sammen er over halvparten av meldingene noe
brukeren ikke trenger å lese» summerte to grupper som overlapper, så tallet var
udokumentert selv om begge leddene er målt. Medietesten 17.09, som hele
problemformuleringen hviler på, fikk kjøringen 21.09 som belegg. To
«to-delinger» rett etter hverandre ble skilt fra hverandre. Og av/på-bryteren
for KI-laget, som er den mest uvanlige påstanden i briefen, sto bare i The
Solution og ikke der forskjellene beskrives.

**Repoet ble kjørbart for en som ikke har vært med å bygge det.** README er
skrevet om til et kart: hva prosjektet er, hvor Product Brief og PRD ligger,
hvilke mapper som er våre mot hvilke som fulgte med BMAD-rammeverket, og
oppstart i fem steg. `.env.example` er lagt til, så den som kloner ikke må gjette
hvilke miljøvariabler som mangler — kun `EODHD_API_KEY` leses av koden,
kontrollert med søk over `src/` og `tests/`.

**Oppstartsinstruksjonen ble kontrollert mot et ferskt klon** i en midlertidig
katalog, uten `data/` og uten `.env`. `uv sync` gikk gjennom, tom nøkkel ga
beskjeden «EODHD_API_KEY mangler. Legg den i .env i prosjektroten», appen svarte
200 med «Ingen kursdata funnet i `data/`», og 162 tester passerte uten nøkkel og
uten data. `fetch_prices` ble ikke kjørt — dagskvoten var brukt opp.

**Signaltesten mot 199 handelsdager holdt.** Terskel, volumfaktor og
nøytralsonebredde ble låst mot et vindu tretten ganger større enn de 15 dagene
de opprinnelig ble satt på, og alle tre verdiene sto.

**Relevanseksperimentet ble flyttet fram og delt i to.**

### Hva førte det til?

Briefen sier nå det kildene sier, og den kan leses av en sensor uten at noe må
tas på tro. Repoet kan klones og kjøres av en som ikke har vært med.

Den mest lærerike enkeltendringen er den siste. **Uke 41 ble satt mens
eksperimentet var blokkert av to ting** — om vilkårene tillot språkmodellbruk,
og om `/api/news` svarte for `.OL`. Begge ble avklart 21.09. **Datoen ble aldri
flyttet etterpå.** Den sto igjen i tre uker som en frist ingen lenger hadde
grunn til, helt til noen spurte hvorfor den var der.

Eksperimentet er nå delt: del 1 — utvalgskriterier, innsamling og manuell
merking — kan gjøres nå og er satt som neste oppgave etter arkitekturfasens to
første punkter. Del 2, KI-klassifiseringen, kan ikke: KI-laget finnes ikke som
kode, ingen modelltjeneste er valgt, og betingelse 4 i EODHDs godkjenning er
udokumentert.

### Refleksjon

**En blokkering som forsvinner, flytter ingen dato av seg selv.** Det er den
samme mekanismen som gjorde at hull 3 ble stående feil formulert, og som lå bak
alle fem tilfellene i oppføringen over: en tilstand endrer seg, men teksten som
beskrev den gjør det ikke. Forskjellen her er at ingen tok feil av noe — datoen
var riktig da den ble satt. Den ble bare aldri stilt spørsmål ved etterpå.

Det er verdt å merke seg at det billigste tiltaket mot dette ikke er en regel,
men et spørsmål: *hva var grunnen til denne datoen, og gjelder den fortsatt?*
Det tok ett spørsmål å oppdage at svaret var nei.

**Å merke tidlig er metodisk sterkere enn å merke senere.** Testsettet skal
merkes manuelt før KI-vurderingen sees. Gjøres merkingen uker før KI-laget i det
hele tatt finnes, er den forutsetningen umulig å bryte i stedet for bare lovet.
Det er samme grep som nettsperra i `conftest.py`: gjør påstanden etterprøvbar
der den står, i stedet for å love den.

**Kontrollen mot et ferskt klon er det samme grepet en tredje gang.** README
hadde kunnet si «klon og kjør» uten at noen hadde prøvd det. Det tok noen
minutter å faktisk gjøre det, og forskjellen er mellom en instruksjon som *ser*
riktig ut og en som er kjørt.

### Git / dokumentasjon

Seks commits på briefen, én på README som kart, én på `.env.example`, én på
oppstartsinstruksjonen, og én på relevanseksperimentet som berører
`product-brief.md`, `prd.md`, `malinger.md` og memloggen. Beslutningen om
eksperimentet er ført, ikke utført — utvalgskriteriene er ikke skrevet.

---

# Joakims oppføringer

Denne seksjonen er tom med vilje, og den skal fylles ut av Joakim.

**Hvorfor den finnes.** Oppføringene over er ført av Marian eller av en
KI-økt. Joakim har bidratt med ideer som har formet prosjektet — men det har
skjedd utenfor de øktene som ble loggført, og derfor finnes bidragene ikke i
noen fil. Loggen viser hvem som *førte* oppføringene; den viser ikke hvem som
bidro.

Det er et dokumentasjonsproblem, ikke et deltakelsesproblem. Men konsekvensen
er reell: en refleksjonsrapport om gruppens prosess kan ikke vise fram noe som
ikke står skrevet.

**Hva som bør føres.** Samme struktur som de øvrige oppføringene:

## 22.09.2026 – To svar som så gyldige ut og ikke kunne svare

### Dato / deltaker(e)

2026-09-22, formiddag og ettermiddag. Marian, med Claude som arbeidsøkt.

### Fase

Arkitekturfasen: første kurshenting, `nyeste_snapshot`-rettingen, spinen med
gjennomgangsport, og til slutt målingen av de to `[FORELØPIG]`-vinduene.

### Hva ble gjort eller foreslått?

Dagen ga to tilfeller av samme type, ett fra hver side av bordet. Begge ser ut
som gyldige svar. Ingen av dem kunne svare på spørsmålet som ble stilt.

**1. Målingen som ikke kunne svare.** Spørsmålet var om `VOLATILITET_VINDU = 20`
og `VOLUM_VINDU = 20` er et valg eller en tilfeldighet. Målet som ble bestilt
var: *hvor mange av de 2 985 aksjedagene får et annet signal enn med 20?*

Det målet er **0 ved 20 per konstruksjon**. Det måler avstand fra 20 og
forutsetter at 20 er referansen. Det ga tall for ni vindustørrelser, tallene var
riktige, og kurven så informativ ut — den var U-formet rundt 20, noe som ved
første øyekast ser ut som at 20 er et bunnpunkt. Det er det ikke. Det er
nullpunktet til en avstandsmåling.

Feilen ble oppdaget ved å **kjøre målet og se på resultatet**, ikke ved å lese
forslaget. Hverken den som bestilte eller den som skrev koden så det på papiret.

**2. Påstanden om to Prevents-punkter.** Senere samme dag kom instruksen: AD-20
har to Prevents-punkter som sier det samme, slett det ene. Det var ett. Kilden
var en **diff-visning**, der den gamle linjen står over den nye — den var lest
som to levende punkter i fila. Arbeidsøkta talte punktene i fila i stedet for å
gjøre som instruksen sa.

### Hva førte det til?

Målet ble byttet ut med to som er **iboende** og ikke forutsetter noe om 20:

| Metrikk | Egenskap |
|---|---|
| **Utslagsrate** | Hvor ofte sjekken gir noe annet enn 0, ved et gitt vindu. Sier noe om vinduet alene |
| **Nabostabilitet** | Hvor mange aksjedager som skifter verdi mellom *w* og *w*−5. Sier noe om hvor mye valget betyr i det området |
| ~~Avstand fra 20~~ | Relativ til tallet som skulle testes. Kan per konstruksjon ikke si om det tallet er spesielt |

Skillet er hele poenget: **de to første måler en egenskap ved vinduet, den
forkastede målte en egenskap ved forholdet til 20.** Et mål som har svaret
innebygd i referansepunktet sitt, kan ikke brukes til å prøve referansepunktet.

De nye målene ga et svar som det første aldri kunne gitt: utslagsraten er
monoton i begge vinduene, men i **motsatt retning** — bevegelse faller fra
37,0 % til 27,3 %, interesse stiger fra 14,1 % til 17,5 %. Og 20 er ikke et
optimum. Alt mellom 15 og 30 oppfører seg tilnærmet likt. Begrunnelsen for å
låse 20 ble derfor ikke «20 er best», men «20 ligger klar av det ustabile
området under 15». Det er en svakere påstand, og den er sann.

Påstanden om Prevents-punktene førte ikke til noe, nettopp fordi den ble
kontrollert. Den er ført som tilfelle 6 i registeret over.

### Refleksjon

De to henger sammen, og det er derfor de står i samme oppføring.

**Begge har en kilde som ser ut som en tilstand, men er en framstilling av en.**
En diff-visning er en framstilling av en fil — den viser den gamle og den nye
linjen samtidig, og fila har bare den nye. En avstandsmetrikk er en framstilling
av en parameter — den viser hvordan alt annet skiller seg fra 20, og sier
ingenting om 20. I begge tilfellene bærer framstillingen informasjon som ikke
finnes i det den framstiller.

Det er samme mekanisme som tilfelle 2 i registeret, der en `tail -14`-utskrift
ble lest som hele filen. Tiltaket derfra — *les hele filen, ikke utskriften av
den* — viser seg å gjelde bredere enn filer: **les tilstanden, ikke visningen av
den.**

**Men de skiller seg på ett punkt, og det er det nyttigste.** Tilfelle 6 ble
fanget av en kontroll som allerede var innarbeidet: økta sjekket fila. Målingen
ble ikke fanget av noen kontroll — den ble fanget av at noen så på resultatet og
syntes kurven var mistenkelig pen. Vi har en vane for det første og ingen for
det andre.

En metode kan ikke kontrolleres mot en kilde slik en påstand kan. Den må
kontrolleres mot **spørsmålet den skal svare på**, og det finnes ingen fil å
slå opp i. Det nærmeste vi kom en regel i dag var: *hva ville dette målet vist
hvis svaret var det motsatte?* Et mål som gir samme utslag uansett, måler ikke
det vi tror.

**Verdt å merke for rapporten:** det var den som bestilte målingen som stilte
spørsmålet skarpt nok til at feilen ble synlig — «er 20 et valg eller en
tilfeldighet» tåler ikke et svar som forutsetter 20. Et vagere spørsmål, som
«virker 20?», ville den forkastede metrikken besvart utmerket. Og feil.

### Git / dokumentasjon

Målingen: `malinger.md` §9, med det forkastede målet og begrunnelsen for å
forkaste det ført i paragrafen — ikke fjernet. `[FORELØPIG]` fjernet i
`signalberegning.py` og `prd.md` §4.7. PRD-en satt til `status: final` da alle
fire punktene i utgangsbetingelsen var innfridd.

Tilfelle 6 ført i registeret over. Arkitekturspinen `AD-20` står med ett
Prevents-punkt, som den alltid har gjort.

---

## 22.09.2026 – Databasevalget ble godtatt, og det var beskrivelsen som bar det

### Dato / deltaker(e)

2026-09-22, ettermiddag. Marian.

### Hva ble gjort eller foreslått?

SQLite-valget fra arkitekturfasen ble sendt faglærerstaben med spørsmål om det
er innenfor kravet, eller om en klient/server-database forventes. Svar kom samme
dag, fra **assisterende hjelpelærer** — ikke fra emneansvarlig.

### Hva førte det til?

Valget står. Forbeholdet i arkitekturspinen — «sendt faglærer 22.09, ubesvart;
kommer det et nei, byttes motoren» — er bortfalt og erstattet med svaret.

### Refleksjon

**Det som bar svaret var ikke at SQLite er enkelt.** Det var at bruken ble
beskrevet konkret: strukturert lagring over tid, relasjoner mellom data, joins,
migrasjoner og logging av KI-vurderinger.

Hjelpelæreren bruker **den samme oppramsingen tilbake** som begrunnelse for at
det er innenfor — «bruker dere SQLite som en ordentlig database, ikke bare som
enkel fillagring». Spørsmålet ble besvart slik det ble stilt. Hadde vi spurt
«holder det med SQLite?», ville svaret måttet vurdere verktøyet i seg selv. Vi
spurte om bruken, og fikk bruken vurdert.

Det er samme lærdom som EODHD-saken 21.09, fra motsatt kant: der handlet den om
at et svar ikke rekker lenger enn spørsmålet det besvarte. Her rekker svaret
nøyaktig så langt som beskrivelsen — og beskrivelsen var god fordi tallene og
kravene bak den allerede fantes i `malinger.md` og PRD-en.

**To begrensninger som ikke skal skrives bort.** Svaret kom ikke fra
emneansvarlig, og det sier selv «ut fra det vi vet nå». Det er et kvalifisert ja
fra en som ikke er endelig myndighet. Restrisikoen er liten, men den er ikke
null, og den står ført i arkitekturmemloggen.

### Git / dokumentasjon

Spinen `AD-4` har svaret ordrett med begge begrensningene. Deferred-raden «Om
SQLite godtas» er fjernet — den var utsatt, ikke lenger.

---

## 22.09.2026 – NFR-02: et krav som var riktig i utfall og feil i mekanisme

Femte krav truffet av FR-401-omskrivingen, og det eneste som overlevde alt vi
har av kontroller.

NFR-02 het «Brukeren venter aldri på en henting», og det var sant hele veien —
etter omskrivingen er det sannere enn før, siden webserveren nå aldri henter i
det hele tatt. Brødteksten lovet noe annet: *«Henting og KI-behandling skjer som
bakgrunnsoppgave […] Mens en henting pågår, vises siste kjente data.»* Den
mekanismen finnes ikke lenger, og en utvikler som oppfylte kravet ordrett ville
bygget en bakgrunnsjobb i webserveren — som `AD-10` forbyr.

**Kravet overlevde fem gjennomganger, en sjekkliste og en gjennomgangsport
fordi det var riktig i utfall.** Alt som kontrollerte det, kontrollerte
påstanden «venter brukeren?» — og svaret var nei, hver gang. Ingen leste det som
en påstand om *mekanisme* før en nedbryting skulle bygge etter det.

Funnet kom ikke fra en kontroll. Det kom fra å lese kravet med et annet
spørsmål: **hva ville en utvikler faktisk gjøre med denne setningen?** FR-402 og
FR-403 ble funnet ved å greppe på ordet «oppstart»; NFR-02 inneholder ikke det
ordet og ville aldri dukket opp i det søket.

Det er samme form som funnet om målingen tidligere samme dag: en kontroll som
sjekker om noe er sant, fanger ikke at det er sant av feil grunn. Vi har nå tre
eksempler på at riktig svar og riktig resonnement er to forskjellige ting — og
ingen rutine som skiller dem.

---

## 22.09.2026 – Formen var fullstendig, innholdet ikke

Flere innlimte instruksjoner ble kuttet underveis i løpet av dagen. To ble
fanget med én gang. Én ble ikke.

### Hva ble gjort eller foreslått?

De to som ble fanget, stoppet begge **der et nytt punkt skulle begynt** — «fordi
hentingen» midt i en begrunnelse, og et trinn 2 som aldri kom. Da var hullet
synlig: setningen manglet en slutt, og neste overskrift uteble.

Den tredje stoppet **inne i en liste som allerede var halvveis fylt ut.**
Spørsmålet gjaldt tidssone og hadde tre alternativer. Svaret behandlet
alternativ 1 ferdig, forkastet alternativ 2 med full begrunnelse, og endte så på
«Alternativ 3 ble forkastet fordi det gjør filnavn og».

### Hva førte det til?

`AD-20` i arkitekturspinen ble skrevet med ett forkastet alternativ i stedet for
to. Memloggen fikk samme mangel. Ingen av stedene sa at noe manglet — de så
fullstendige ut, fordi et avsnitt med ett forkastelsespunkt ikke *ser* ufullendt
ut.

Forkastelsen er nå ført, 17:14, merket i memloggen som noe som kom etter, med
grunnen til at den kom etter.

### Refleksjon

**Det som gjorde avkortingen usynlig, var at formen var fullstendig selv om
innholdet ikke var det.** De to første kuttene etterlot en setning uten slutt —
en formfeil, som er lett å se. Det tredje etterlot et velformet avsnitt som
manglet ett av tre punkter. Formen bar ingen spor av hullet.

Det er samme lærdom som `NFR-02` ga tidligere samme dag, fra en annen kant: der
var kravet riktig i utfall og feil i mekanisme, og alle kontrollene sjekket
utfallet. Her var teksten riktig i form og ufullstendig i innhold, og det finnes
ingen kontroll som leser form. I begge tilfellene besto noe en prøve som ikke
målte det som var galt.

**Den ble ikke oppdaget av noen kontroll.** Den ble oppdaget av at brukeren sa
fra om at innliming kuttes, og ba om en systematisk gjennomgang av alt som var
skrevet på grunnlag av innlimt tekst. Uten det ville `AD-20` stått med to av tre
alternativer behandlet på ubestemt tid — og forskjellen ville først dukket opp
den dagen noen lurte på hvorfor alternativ 3 ikke var vurdert.

**Tiltaket er en sluttmarkør.** Instruksjoner avsluttes nå med en linje som sier
at instruksjonen er slutt. Ser den ikke ut, er teksten avkortet, og arbeidet
stopper i stedet for å bli delvis utført. Det flytter kontrollen fra *å lese
innholdet og vurdere om det virker helt* — som ikke virket — til *å se etter én
bestemt linje*, som enten er der eller ikke er der.

Det er verdt å merke at tiltaket ikke oppdager hva som mangler. Det oppdager at
noe mangler, og det er nok: et arbeid som stopper, kan gjenopptas. Et arbeid som
fortsetter med et hull, fører hullet videre inn i dokumentene.

### Git / dokumentasjon

`ARCHITECTURE-SPINE.md` `AD-20` har nå begge forkastelsene. Memloggen fører den
sene oppføringen som egen linje med tidsstempel og med grunnen til at den kom
etter — loggen er append-only, så den gamle rekkefølgen står.

---

## 22.09.2026 – Mangelen ble funnet i vårt eget brev, ikke i et svar

Forespørselen til Euronext 21.09 ba om fire ting: Retrieval, Storage, Display og
Source code. Den nevnte ikke at prosjektet sender meldingstitler og -tekst til en
tredjeparts språkmodell — og vilkårene forbyr uttrykkelig å «otherwise transfer
any of the Content to any third person». Purringen 22.09 dekker begge deler.

**Mangelen ble ikke funnet ved å lese et svar.** Svaret er ikke kommet. Den ble
funnet ved å lese vårt eget brev og spørre hva det faktisk ba om — og se at
lista over fire ting ikke inneholdt den ene handlingen vilkårene navngir.

Det er samme huskeregel som EODHD-saken ga 21.09: *et svar rekker ikke lenger
enn spørsmålet det besvarte.* Der ble regelen lært av et svar som dekket mindre
enn vi først leste det som. Her er den brukt **på forhånd** — på vårt eget
spørsmål, før svaret finnes, mens det ennå går an å utvide det.

Verdt å merke: regelen er nyttigst før svaret kommer. Brukt etterpå forteller den
bare hva vi ikke fikk vite. Brukt før, endrer den hva vi spør om.

---

## 22.09.2026 – En beslutning som overlevde at grunnen falt bort

`AD-17` sier at hentekommandoen skriver dagens vurdering i samme kjøring. Den
ble tatt tidlig 22.09 med to begrunnelser. Begge viste seg å ikke holde.

### Hva som falt

**«Kravet sier automatisk.»** Den hvilte på FR-408s ordlyd — «Lagringen skjer
automatisk, fra første kjøring». Men den ordlyden var selv en rest fra modellen
der applikasjonen hentet ved oppstart, og da FR-401 ble skrevet om samme dag,
ble begrunnelsen sirkulær: AD-17 begrunnet seg med et krav som beskrev en
verden FR-401 nettopp hadde avskaffet.

**«En dag ingen åpner siden, blir aldri lagret.»** Denne var verre, og den falt
av en annen grunn: **den rammer AD-17s egen løsning like hardt.** En dag ingen
kjører hentekommandoen, blir heller ikke lagret. Argumentet skilte ikke
alternativene fra hverandre — det beskrev en egenskap alle tre delte, og ble
likevel brukt til å forkaste ett av dem.

### Hvorfor konklusjonen likevel står

Den nye begrunnelsen kommer fra `AD-5`: `erstatt_serie` bytter ut **hele**
symbolets serie ved hver henting. Vurderingen regnes av kursene som lå der da.
Skrives den et annet sted eller på et annet tidspunkt, kan grunnlaget være
byttet ut — og da lagrer den ikke lenger «hva løsningen mente om *disse*
dataene».

Det argumentet **skiller** alternativene, fordi det handler om hvilket grunnlag
vurderingen regnes av, ikke om hvem som må huske noe.

### Forskjellen mellom å overleve og å bli reddet

Dette er poenget som er verdt plass i rapporten.

Den enkle veien var å skrive om FR-408 slik at «automatisk» igjen betydde noe
som passet, og la AD-17 stå urørt. Konklusjonen ville vært den samme, og ingen
ville sett noe. **Det ville vært å redde beslutningen** — å justere premisset
til det bar vekten det allerede var pålagt.

Det som ble gjort i stedet: begrunnelsen ble prøvd på nytt fra en annen kant, og
den holdt. Forskjellen er ikke synlig i resultatet — AD-17 sier det samme nå som
før — men den er synlig i **hvorfor**, og den gamle begrunnelsen står bevart og
datert i spinen så forskjellen kan leses.

En beslutning som overlever at begrunnelsen faller, er sterkere enn før. En
beslutning som får begrunnelsen justert til å passe, er svakere, og ser
identisk ut.

### Hullet som ble avgjort i stedet for å bli lappet

Underveis viste det seg at `AD-7` og `FR-403` er i strid: kursserien etterfylles
etter dager uten kjøring, men `skriv` avviser enhver dato som ikke er
inneværende børsdag, så vurderingene kan ikke.

**Det er ikke en defekt.** En kurs for 12.09 er den samme uansett når den
hentes. En vurdering er det ikke — en vurdering skrevet i dag for 12.09 ville
vært dagens parametres svar, ikke datidens, og det er nettopp det FR-408 finnes
for å hindre. En dag ingen kjørte kommandoen, sa løsningen ingenting.

Det som manglet, var at dette sto noe sted. Nå gjør det det, og `FR-409` krever
at dagen vises som «ingen vurdering — kommandoen ble ikke kjørt denne dagen» i
stedet for som en tom rad. Ellers blir et hull i vår egen drift umulig å skille
fra en dag uten utslag — det første er en mangel, det andre er et funn.

### To rettelser fra samme kontroll

**F8.** `epics.md` sa at søk etter forbeholdstekst ga «null treff».
`src/templates/index.html:108` sier «ikke om aksjen bør kjøpes eller selges».
Søket lette etter fire ordformer, og ingen av dem står der. **Et tomt søk
beviser at ordene ikke er der, ikke at saken ikke er der.**

**F4.** `epics.md` førte FR-103 på commit `706720f`. Den commiten hadde
`Retningsvisning("Opp", "↑", "opp")` — nøyaktig oversettelsen kravet forbyr.
**Det er mulig å føre et krav på commiten som brøt det**, hvis man leser
filnavnet og ikke diffen.

---

## 22.09.2026 – Formiddagen: en teller, et bortkastet kall, og en feil beviset ikke kunne nå

Kvotetelleren sto på 20 av 20, datert i går, klokka 08:32 UTC. Den late
nullstillingen — at telleren ruller ved første betalbare kall og ikke ved
midnatt — sto allerede dokumentert i `malinger.md` §7.1, med sitat fra EODHD.
Jeg brukte likevel et API-kall på å finne det ut. **Forsiktigheten var riktig,
metoden ikke:** svaret var gratis å lese, og kvoten er 20 i døgnet.

Senere samme formiddag ble sorteringsfeilen i `nyeste_snapshot` funnet — ved å
lese koden *etter* at rettingen var bevist mot ekte filer. Beviset holdt: appen
valgte riktig fil. Feilen lå i tiebreaket ved lik dato, som de ekte filene aldri
utløste. **En retting som virker, er ikke det samme som en feil man har
forstått.**

---

## 22.09.2026 – Kontrollen: seks feil som alle var sanne om en delmengde

Fire uavhengige lenser gikk gjennom alt som ble endret i løpet av dagen. 35
funn.

*Rettet 2026-09-23:* 35 er summen av det lensene oppga. Telles samme feil én
gang, også når to lenser fant den, er det **31**. Hvordan det er telt, står i
`docs/kontroll-2026-09-22.md`.

Seks av dem hadde samme form: **en korrekt observasjon av en delmengde, skrevet
ned som en påstand om helheten.** `tags` var tom — i artikkel 1, av ti.
Tegnspennet var 394–3 131 — i de tre første. «Null treff på forbeholdstekst» —
for fire bestemte ordformer.

Ingen av dem ble funnet ved å lese teksten på nytt, for teksten er velformet og
den underliggende observasjonen er sann. Det som fant dem, var å spørre **hva
påstanden ble lest av.** Ikke «stemmer dette?», men «hvor mye ble faktisk sett
på?».

---

## 22.09.2026 – Leveranselista kan ikke kontrolleres mot en kilde

`docs/innlevering.md` ble bygget på kilder i stedet for hukommelse. Underveis
kom funnet som betyr mest: **alt vi vet om hva som skal leveres, kommer fra
e-post og samtaler.** Det finnes ingen eksamenstekst, oppgavetekst eller
Canvas-materiale gjengitt noe sted i repoet.

Konsekvensen er konkret: lista kan ikke etterprøves mot et dokument — bare mot
svar vi ber om. Derfor står seks punkter under «Antatt, ikke bekreftet», blant
dem begge datoene og spørsmålet om PRD og arkitekturdokument i det hele tatt er
innleveringskrav.

---

## 22.09.2026 – Gjennomgangsporten: lesere som ikke hadde skrevet det

Tre uavhengige lenser gikk gjennom arkitekturspinen, hver i sitt eget
kontekstvindu. De fant hver sin ting økta som skrev den, hadde snakket seg forbi:

- en **ambisjon skrevet i beskrivende form** — lagtabellen sa at `kursdata.py`
  ikke rører I/O, mens fila leser fil og globber katalog
- **FR-301..303 som var helt taus** — en tredje nettkilde og et eid datasett
  uten port, ikke i `binds`, ikke i kartet, ikke i Deferred
- **AD-2 som ikke kunne overleve sine egne krav** — «eneste sted `requests`
  brukes» holder ikke sammen med FR-404 og FR-301

Ingen av dem ble funnet ved å lese dokumentet én gang til. De ble funnet av
lesere som ikke hadde skrevet det — og det er hele grunnen til at porten kjøres
i egne kontekstvinduer.

---

## 22.09.2026 – En ren kontroll, og grensen skrevet ned samtidig

`local-tests/` ble kontrollert for lekkede API-nøkler. Utfallet var rent: alle
tre skriptene leser nøkkelen fra `.env`, katalogen er gitignorert, og et søk
gjennom alle 138 commits i alle grener fant **null** stier under `local-tests/`
og ingen treff på nøkkelmønsteret.

**Poenget er ikke at kontrollen var ren. Det er at renheten er avgrenset.**
Søket dekket ett mønster — `api_token=` etterfulgt av en verdi — altså den
formen disse tre skriptene faktisk bruker. En nøkkel som hadde ligget som
`KEY = "..."` eller i en JSON-verdi, ville ikke nødvendigvis truffet. Og
`git rev-list` ser bare dette repoet: en nøkkel limt inn i en chatlogg, et
skjermbilde eller en e-post er usynlig for den.

Det er **samme form som funn F8** tidligere i dag, der «null treff» på fire
søkeord ble skrevet ned som at teksten ikke fantes. Forskjellen er når grensen
kom: F8 ble funnet av en kontroll i etterkant, mens denne står i svaret fra
første stund.

Det er billigere å skrive ned hva et søk *ikke* dekket, enn å oppdage det
senere — og det er den eneste forskjellen mellom de to tilfellene. Metoden er
like begrenset begge steder.

---

## 23.09.2026 – Et anslag som pekte feil vei

Rettingsplanen 22.09 mente at lens 3 hadde overtelt, og anslo «12–13
distinkte» mot lensens 18. Da funnene ble telt 23.09, var alle 18 distinkte.
Dobbelttellingen var reell, men den lå **mellom** lensene, ikke i lens 3.
Totalen ble 31 av 35.

Anslaget var ikke bare unøyaktig, det pekte på feil sted. Det er samme mønster
som kontrollen 22.09 fant seks ganger: en påstand om helheten, skrevet uten å
se på helheten. Denne gangen sto den i selve rettingsplanen.

---

## 23.09.2026 – To «krav» som ikke står på emnesiden

Dockerfile og database har styrt planleggingen i tre dager. De var de to første
beslutningene i arkitekturfasen (åpent punkt 17 og 18), og `docs/innlevering.md`
kalte Dockerfilen «halve innleveringen». Hjelpelærer svarte 23.09: «Det står
derimot ikke på emnesiden jeg har tilgjengelig at Dockerfile eller en bestemt
type database er et eksplisitt leveransekrav.»

Begge kom fra samtaler med faglærer 21.09, og vi førte dem som krav uten å ha
kilden. `innlevering.md` sa det allerede 22.09: alt vi vet om innleveringen,
kommer fra e-post og samtaler. Det var riktig observert og ble likevel ikke
fulgt. Dette er det første svaret som viser hva det kostet.

Begge gjøres likevel. Databasen er begrunnet i kravene selv, og sensor må kunne
kjøre løsningen. Men de er nå ført som det de er: sagt i samtale, ikke
bekreftet på emnesiden. Og den emnesiden vi faktisk hadde tilgang til, sier noe
vi ikke hadde lest: kvalitetssikringen av koden hører til de 70 prosentene.

---

## 23.09.2026 – Prioriteringen etter svaret: samme produkt, annen rekkefølge

To «krav» vi planla etter i tre dager, sto ikke på emnesiden. Det endret ikke
hva vi bygger, men det endret rekkefølgen. Og det viste at «synlig og
dokumentert prosess» er det som faktisk vurderes, og at kontrollrapportene,
mutanttestene og memloggene hører til de 70 prosentene, ikke bare de 30.

Rekkefølgen vi valgte:

1. **Virke først.** Epic 1, 2 og 3: at noen utenfor gruppen kan kjøre
   `docker run`, hente kurser og se begge skjermbildene med ekte data.
2. **Design er ikke etterarbeid.** `[CU] bmad-ux` kjøres sent, som en
   gjennomgang av de to skjermbildene som finnes (story 8.2).
3. **Brukertesten tidlig**, rett etter Epic 2 (story 8.1). Det er den
   billigste tilbakemeldingen på designet som finnes, og den avgjør om FR-706
   faktisk forklarer.
4. **Ingen utvidelse av omfanget.** Sier Euronext nei, er applikasjonen kurser,
   signal og forklaring — et helt produkt, som skal være utmerket, ikke et
   halvferdig større produkt.
5. **Forbedringer ut over v1** tas først når alt over er kontrollert og virker.

---

## DD.MM.2026 – kort tittel

### Dato / deltaker(e)

### Hva ble gjort eller foreslått?

### Hva førte det til?

Hva forslaget endret — i produktet, i en beslutning, eller i retningen
arbeidet tok. Det er koblingen mellom idé og utfall som gjør en oppføring
brukbar i rapporten. Et forslag som ble forkastet, er også verdt å føre; da
hører begrunnelsen med.

### Refleksjon

Valgfritt. Hva som var vanskelig, hva som overrasket, hva du ville gjort
annerledes.

---

*Det er lettere å skrive dette nå enn i desember. Oppføringer som skrives i
ettertid, blir til det man husker — ikke til det som skjedde.*
