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
