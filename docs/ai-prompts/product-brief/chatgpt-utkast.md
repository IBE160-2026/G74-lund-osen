# Product Brief: OSE Signal

**Emne:** IBE160 Programmering med KI, Høgskolen i Molde  
**Gruppe:** G74 – Joakim Lund, Marian Osen

## Executive Summary

OSE Signal er en norsk, desktop-basert webapplikasjon som skal gi en rask og forståelig oversikt over et utvalg aksjer på Oslo Børs. Målet er at en vanlig sparer som følger norske aksjer skal kunne åpne løsningen om morgenen og på omtrent fem minutter se hva som har skjedd, hvilke aksjer som skiller seg ut, hvorfor de gjør det, og hvilke nyheter eller kommende hendelser som er relevante.

I dag må denne informasjonen ofte hentes fra flere steder. Kursutvikling, nyheter og rapportdatoer kan ligge i ulike tjenester, og nyhetsstrømmen kan inneholde mye som ikke er direkte relevant for selskapet. OSE Signal skal samle dette i én enkel og forklarbar løsning. Tekniske beregninger gjøres med vanlig programkode, mens KI brukes der språkforståelse gir en reell fordel, særlig til å vurdere nyhetsrelevans og lage korte forklaringer.

Prosjektet er mulig å gjennomføre nå fordi KI-assistert utvikling gjør det realistisk for to studenter med begrenset erfaring med tradisjonell programmering å bygge en sammensatt applikasjon. Samtidig kan språkmodeller brukes som en del av selve produktet til å vurdere finansnyheter. Første versjon skal være på norsk og prioritere stabilitet, enkel design og et godt brukergrensesnitt fremfor mange funksjoner.

## The Problem

En privatperson som følger flere norske aksjer må ofte bruke flere nettsider eller tjenester for å få oversikt over kursutvikling, nyheter og kommende rapporter. Det tar tid å finne frem til det som faktisk er viktig, særlig når man bare ønsker en rask oversikt før arbeids- eller studiedagen starter.

I våre egne tester av finansnyheter så vi at noen selskaper fikk tydelige selskapsnyheter, mens andre ofte ble nevnt i brede markedsartikler sammen med mange andre selskaper. Det gjør det vanskeligere å skille relevant informasjon fra generell markedsstøy.

Mange markedsoversikter viser også tall og kursbevegelser uten å forklare hvorfor en aksje skiller seg ut. Brukeren må derfor selv samle og tolke informasjonen.

## The Solution

OSE Signal skal samle den viktigste informasjonen i én desktop-first webapplikasjon.

Første versjon skal følge omtrent 30–40 likvide aksjer på Oslo Børs, fordelt på flere sektorer. Den konkrete listen fastsettes i PRD. Brukeren skal kunne se faktisk kursutvikling, signalstyrke og retning, og åpne en aksje for å se kursgraf, noen få tekniske indikatorer og hvilke faktorer som bidro til signalet.

Signalstyrke skal vise hvor kraftig de definerte kriteriene slår ut, mens retning skal vise om bidragene samlet peker positivt, negativt eller er blandet. Signalstyrke er ikke en anbefaling om kjøp eller salg.

KI skal vurdere finansnyheter som direkte relevante, indirekte relevante eller lite relevante for selskapet. KI skal også kunne identifisere type hendelse og lage en kort forklaring. Originalkilden skal være synlig, og usikkerhet skal vises i stedet for at KI gjetter.

KI-laget skal kunne slås av, og applikasjonen skal fortsatt fungere uten det. Dette gjør det mulig å se hva den regelbaserte løsningen viser alene, og hva KI faktisk tilfører.

Kommende finansielle hendelser skal vises når data finnes. Dagens vurderinger skal lagres med dato, signalstyrke, retning, bidragende faktorer, relevante nyheter og kurs, slik at de senere kan hentes frem igjen. Historiske sammenligninger skal bruke utbyttejusterte kurser slik at ordinære utbytter ikke feiltolkes som kursfall.

## What Makes This Different

Alternativet i dag er ofte å kombinere flere gratis markedsoversikter og nyhetskilder, eller bruke mer avanserte verktøy som kan være unødvendig omfattende for en vanlig sparer.

OSE Signal skal være enklere. Brukeren skal raskt kunne se hva som skiller seg ut og hvorfor. Signalstyrke og retning vises sammen med forklaringen bak, KI brukes til å redusere nyhetsstøy, og originalkilder og usikkerhet er synlige.

En viktig forskjell er at KI-laget kan slås av. Det gjør KI-bidraget synlig og etterprøvbart i stedet for å skjule det inne i resten av løsningen.

Forskjellen ligger ikke i en unik teknologi, men i hvordan markedsdata, forklarbar signalanalyse, nyhetsfiltrering og kommende hendelser samles i én enkel norsk markedsoversikt.

## Who This Serves

Primærbrukeren er en vanlig sparer som følger norske aksjer ved siden av jobb eller studier og ønsker en rask oversikt uten å bruke mye tid.

Suksess for brukeren er å kunne åpne OSE Signal om morgenen, se hva som har endret seg, forstå hvorfor enkelte aksjer skiller seg ut, og finne de viktigste nyhetene uten å måtte slå opp informasjon flere steder.

Vi er selv en del av målgruppen og skal bruke løsningen gjennom prosjektperioden. Vi har ikke gjennomført en større brukerundersøkelse og bygger derfor ikke briefen på antakelser om et bredere marked.

## Success Criteria

Første versjon regnes som vellykket dersom:

- applikasjonen henter og viser data for hele det valgte aksjeuniverset uten manuelle mellomsteg
- minst én person utenfor gruppen kan gjennomføre hovedflyten på omtrent fem minutter og forklare hvorfor en valgt aksje skiller seg ut
- brukeren kan åpne en aksje og se hvilke faktorer som bidrar til signalstyrke og retning
- finansnyheter klassifiseres med originalkilde, og usikre vurderinger markeres som usikre
- KI-laget kan slås av, og applikasjonen fungerer fortsatt uten det
- kommende finansielle hendelser vises der data er tilgjengelig
- dagens vurderinger lagres automatisk med informasjonen som trengs for senere historikk
- manglende data, feilende kilder og dager uten tydelige signaler håndteres uten at hovedflyten stopper eller systemet tvinger frem resultater
- de viktigste brukerflytene fungerer stabilt og har et enkelt, ryddig og gjennomarbeidet grensesnitt i en demonstrasjon
- gruppen bruker løsningen jevnlig fra første fungerende versjon og registrerer feil og forbedringspunkter underveis

Vi setter ikke mål for hvor godt signalene treffer markedet. Formålet er å lage en fungerende og forståelig applikasjon, ikke å bevise at den kan forutsi aksjekurser.

## Scope

### In for v1

- norsk desktop-first webapplikasjon
- omtrent 30–40 likvide Oslo Børs-aksjer fra flere sektorer
- enkel markedsoversikt og aksjedetalj
- kursgraf, noen få tekniske indikatorer, signalstyrke og retning
- KI-basert nyhetsfiltrering med kilde og usikkerhet
- av/på-bryter for KI-laget
- kommende finansielle hendelser
- automatisk lagring av daglige vurderinger
- enkelt og gjennomarbeidet brukergrensesnitt

Hvis kjernen fungerer stabilt før fristen, kan enkel historikkvisning, sektorfilter, flere tidsperioder og lokalt lagrede favoritter legges til.

### Out for v1

- brukerkontoer, innlogging og synkroniserte watchlister
- personlig portefølje og varsler
- betaling og abonnement
- mobiltilpasning
- flere børser og flere språk enn norsk
- automatisk handel og meglerintegrasjon
- fundamental- og verdimodell
- intradag og sanntids futures
- omfattende statistisk studie av om signalene slår markedet

## Vision

Hvis første versjon fungerer godt, kan OSE Signal i løpet av de neste 2–3 årene utvikles til å dekke en større del av Oslo Børs og gi brukeren mer personlig kontroll. Brukeren kan velge favorittaksjer, lage egne lister, filtrere på sektorer, lagre innstillinger og få mer historikk og analyse.

På sikt kan brukeren også legge inn sin egen aksjeportefølje og få oppfølging av selskapene hun eller han faktisk eier. Løsningen kan da vise relevante nyheter, større kursbevegelser og andre hendelser knyttet til brukerens egne aksjer. Da går OSE Signal fra å være en generell markedsoversikt til å bli en mer personlig markedsassistent.

Senere kan løsningen støtte flere børser og flere språk. Første versjon skal være på norsk, men en senere versjon kan for eksempel tilby norsk og engelsk. Premiumfunksjoner eller abonnement kan vurderes dersom brukere faktisk opplever løsningen som nyttig nok.

En kommersiell versjon vil kreve egne vurderinger av rettigheter til videreformidling av børsdata, personvern dersom porteføljeopplysninger lagres, og regelverket som gjelder dersom en tjeneste presenterer finansielle signaler eller anbefalingslignende innhold.
