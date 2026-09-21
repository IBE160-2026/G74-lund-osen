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


## 20.09–21.09.2026 – Fire ganger på to døgn: påstander fra en økt uten tilgang til kilden

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

### Dette er fjerde gang

*Ført som «tredje gang, ikke andre» 20.09. Tilfelle 4 kom dagen etter.*

| # | Når | Påstanden | Hva kontrollen viste |
|---|---|---|---|
| 1 | Natt til 20.09.2026 | Brief-utkastene «finnes i repoet med historikk» | Seks av sju filer lå ikke der. Kontrollert med md5 |
| 2 | 20.09.2026, formiddag | Overskriften står to ganger, og en setning er klippet inn i mappestrukturen i README | Filen var hel. En `tail -14`-utskrift var lest som hele filen |
| 3 | 20.09.2026, kveld | Rådata ligger eksponert, og en patch traff feil overskrift | Verken rådata eller feilplassert tekst fantes |
| 4 | 21.09.2026, kl. 18:40 | En klausul fra Euronexts vilkår, oppgitt i anførselstegn | Setningen var ikke lest i kilden. Den var rekonstruert fra en avkortet linje i et referat |

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

### Refleksjon

**En økt uten tilgang til kilden kan ikke uttale seg om hva kilden inneholder —
bare om det den har blitt fortalt.** Det gjelder repoet i tilfelle 1–3 og et
nettsted i tilfelle 4; mekanismen er den samme. Det er ikke en svakhet ved rådgivningen; en
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
