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
