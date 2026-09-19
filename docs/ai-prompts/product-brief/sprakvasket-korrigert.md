# Product Brief: OSE Signal

**Emne:** IBE160 Programmering med KI, Høgskolen i Molde
**Gruppe:** G74 – Joakim Lund, Marian Osen

## Executive Summary

En vanlig sparer som følger norske aksjer bruker ofte flere tjenester for å finne ut det samme: hva beveget seg i går, hvorfor, og er det noe viktig på vei. OSE Signal er en norsk webapplikasjon for PC som samler dette i én oversikt, slik at spørsmålet kan besvares på omtrent fem minutter om morgenen.

Løsningen følger et fast utvalg likvide aksjer på Oslo Børs og viser kursutvikling, signalstyrke og retning, med mulighet for å åpne en aksje og se hvilke faktorer som ligger bak. Tekniske beregninger gjøres med vanlig programkode. KI brukes der språkforståelse er nyttig: å skille relevante selskapsnyheter fra markedsstøy og lage korte forklaringer med kilde.

Prosjektet er mulig å gjennomføre nå fordi KI-assistert utvikling gjør det realistisk for to studenter med begrenset programmeringserfaring å bygge en sammensatt applikasjon, samtidig som språkmodeller brukes som en del av selve produktet. Første versjon er på norsk og prioriterer stabilitet, enkelhet og et ryddig grensesnitt fremfor mange funksjoner.

## The Problem

Den som følger flere norske aksjer ved siden av jobb eller studier har ikke et informasjonsproblem, men et sorteringsproblem. Kursene, nyhetene og rapportdatoene finnes, men de ligger på ulike steder og i ulikt format, og det tar tid å finne frem til det som faktisk er relevant den dagen.

Nyhetsstøyen var tydelig i våre egne innledende tester. For enkelte selskaper fant vi flere nyheter som faktisk handlet om selskapet, mens andre ofte ble nevnt i brede markedsartikler sammen med mange andre selskaper. En nyhet som er knyttet til et aksjesymbol er derfor ikke nødvendigvis relevant for selskapet.

Mange markedsoversikter viser dessuten kursbevegelser uten å forklare hvorfor en aksje skiller seg ut akkurat nå. Brukeren må selv koble kurs, tekniske signaler, nyhetsbilde og kommende hendelser.

## The Solution

OSE Signal består av to hovedvisninger og ett viktig prinsipp.

**Markedsoversikten** viser omtrent 30–40 likvide Oslo Børs-aksjer fra flere sektorer; endelig liste fastsettes i PRD. For hver aksje vises kursutvikling, signalstyrke og retning. Signalstyrken viser hvor kraftig de valgte kriteriene slår ut, retningen om bidragene samlet peker positivt, negativt eller er blandet.

**Aksjedetaljen** forklarer hvorfor. Den viser kursgraf, noen få tekniske indikatorer, hvilke faktorer som bidro til signalet, relevante nyheter og kommende finansielle hendelser når data finnes. KI vurderer nyheter som direkte relevante, indirekte relevante eller lite relevante for selskapet, identifiserer type hendelse og lager en kort forklaring. Originalkilden skal være synlig, og usikkerhet skal vises i stedet for at modellen gjetter.

**Prinsippet** er at KI-laget kan slås av. Applikasjonen skal fortsatt fungere med den regelbaserte analysen alene, slik at det er mulig å se hva KI faktisk tilfører, og slik at en treg eller feilende KI-tjeneste ikke stopper hovedflyten.

Signalstyrke og retning skal være forklarbare og skal ikke presenteres som en anbefaling om kjøp eller salg. Dagens vurderinger lagres automatisk med dato, signalstyrke, retning, bidragende faktorer, relevante nyheter og kurs. Historiske sammenligninger bruker utbyttejusterte kurser, slik at ordinært utbytte ikke feiltolkes som kursfall.

## What Makes This Different

Alternativet i dag er å kombinere flere gratis markedsoversikter og nyhetskilder, eller å bruke profesjonelle verktøy som er mer omfattende enn en vanlig sparer trenger. OSE Signal bygger ikke på unik teknologi. Forskjellen ligger i tre valg:

- **Forklarbarhet før presisjon.** Vi lover ikke bedre signaler enn andre, men at brukeren kan se hva som ligger bak dem.
- **Nyhetsstøy som et eget problem.** KI brukes til å avgjøre om en artikkel faktisk handler om selskapet, noe enkle regler løser dårlig.
- **KI som et lag som kan slås av.** Forskjellen mellom regelbasert analyse og KI-bidrag blir synlig og etterprøvbar.

## Who This Serves

Primærbrukeren er en vanlig sparer som følger norske aksjer ved siden av jobb eller studier, har begrenset tid og ønsker oversikt uten å bruke flere tjenester. Suksess for brukeren er å åpne OSE Signal om morgenen, se hva som har endret seg, forstå hvorfor enkelte aksjer skiller seg ut, og finne de viktigste nyhetene og hendelsene uten å lete flere steder.

Vi er selv i målgruppen og skal bruke løsningen gjennom prosjektperioden. Vi har ikke gjennomført en større brukerundersøkelse, og briefen bygger derfor ikke på antakelser om et bredere marked.

## Success Criteria

Første versjon regnes som vellykket dersom:

- hele aksjeuniverset hentes og vises uten manuelle mellomsteg
- minst én person utenfor gruppen gjennomfører hovedflyten på omtrent fem minutter og kan forklare hvorfor en valgt aksje skiller seg ut
- aksjedetaljen viser hvilke faktorer som bidrar til signalstyrke og retning
- nyheter klassifiseres med originalkilde, og usikre vurderinger markeres som usikre
- KI-laget kan slås av, og applikasjonen fungerer fortsatt uten det
- kommende finansielle hendelser vises der data er tilgjengelig
- dagens vurderinger lagres automatisk med det som trengs for senere historikk
- manglende data, feilende kilder og dager uten tydelige signaler håndteres uten at hovedflyten stopper eller systemet tvinger frem et resultat
- hovedflytene fungerer stabilt og har et ryddig, gjennomarbeidet grensesnitt i en demonstrasjon
- gruppen bruker løsningen jevnlig fra første fungerende versjon og registrerer feil og forbedringspunkter underveis

Vi setter ikke mål for hvor godt signalene treffer markedet. Formålet er en fungerende og forståelig applikasjon, ikke å bevise at den kan forutsi aksjekurser.

## Scope

### In for v1

- norsk webapplikasjon for PC
- omtrent 30–40 likvide Oslo Børs-aksjer fra flere sektorer
- markedsoversikt og aksjedetalj med kursgraf og noen få tekniske indikatorer
- signalstyrke og retning med forklaring
- KI-basert nyhetsfiltrering med kilde og usikkerhet
- av/på-bryter for KI-laget
- kommende finansielle hendelser
- automatisk lagring av daglige vurderinger
- enkelt og gjennomarbeidet brukergrensesnitt

Hvis kjernen står stabilt før fristen: enkel historikkvisning, sektorfilter, flere tidsperioder og lokalt lagrede favoritter.

### Out for v1

- brukerkontoer, innlogging og synkroniserte watchlister
- personlig portefølje og varsler
- betaling og abonnement
- mobiltilpasning
- flere børser og flere språk enn norsk
- automatisk handel og meglerintegrasjon
- fundamental- og verdimodell
- intradag og sanntids futures
- statistisk studie av om signalene slår markedet

## Vision

Hvis første versjon fungerer godt, kan OSE Signal i løpet av de neste 2–3 årene utvikles fra generell markedsoversikt til personlig markedsassistent.

Første steg er mer personlig kontroll: favorittaksjer, egne lister, sektorfilter, lagrede innstillinger og mer historikk over tid. Neste steg er brukerens egen portefølje — legges de eide aksjene inn, kan løsningen følge opp nettopp disse selskapene med relevante nyheter, større kursbevegelser og kommende hendelser.

På lengre sikt kan løsningen dekke flere børser og tilby både norsk og engelsk. Premiumfunksjoner eller abonnement kan vurderes dersom brukere faktisk opplever løsningen som nyttig nok.

En kommersiell versjon vil kreve egne vurderinger av rettigheter til videreformidling av børsdata, personvern dersom porteføljeopplysninger lagres, og regelverket som gjelder når en tjeneste presenterer finansielle signaler eller anbefalingslignende innhold.
