# Product Brief: OSE Signal

**Emne:** IBE160 Programmering med KI, Høgskolen i Molde
**Gruppe:** G74 – Joakim Lund, Marian Osen
**Versjon:** Claude-utkast 17.09.2026 (til sammenligning med ChatGPT-utkastet)

## Executive Summary

En vanlig sparer som følger norske aksjer bruker i dag flere tjenester for å finne ut det samme: hva beveget seg i går, hvorfor, og er det noe viktig på vei. OSE Signal er en norsk, desktop-first webapplikasjon som samler dette i én oversikt, slik at spørsmålet kan besvares på omtrent fem minutter om morgenen.

Løsningen følger et fast utvalg likvide Oslo Børs-aksjer og viser for hver av dem kursutvikling, en signalstyrke som sier hvor kraftig de definerte kriteriene slår ut, og en retning som sier om bidragene samlet peker positivt, negativt eller er blandet. Brukeren kan alltid åpne en aksje og se hvilke faktorer som ga utslaget. Tekniske beregninger gjøres med vanlig programkode. KI brukes der språkforståelse gir en reell fordel: å skille selskapsrelevante nyheter fra generell markedsstøy, og å lage korte forklaringer med kilde.

Prosjektet er mulig å gjennomføre nå fordi KI-assistert utvikling gjør det realistisk for to studenter med begrenset tradisjonell programmeringserfaring å bygge en sammensatt applikasjon, samtidig som språkmodeller kan brukes som en del av selve produktet. Første versjon er på norsk og prioriterer stabilitet, enkelhet og et gjennomarbeidet grensesnitt fremfor mange funksjoner.

## The Problem

Den som følger 10–30 norske aksjer ved siden av jobb eller studier har ikke et informasjonsproblem, men et sorteringsproblem. Kursene finnes, nyhetene finnes, rapportdatoene finnes — men de ligger på ulike steder og i ulikt format, og det meste er irrelevant akkurat i dag.

Nyhetsstøyen er målbar. I vår egen test av finansnyheter 17.09 hentet vi ti nyheter for DNB. Flere av dem handlet i realiteten om Infosys, om europeiske aksjer generelt eller om helt andre selskaper, og nevnte DNB bare fordi selskapet var ett av mange symboler i artikkelen. For Frontline var bildet motsatt: nyhetene var i hovedsak faktisk om selskapet eller om oljemarkedet det opererer i. En løsning kan altså ikke anta at en nyhet knyttet til et symbol handler om det selskapet.

Det andre problemet er forklaringen. De fleste gratis markedsoversikter viser at en aksje er opp 4 %, men ikke hvorfor den skiller seg ut fra de andre. Brukeren må selv koble kursbevegelse, nyhetsbilde og kommende hendelser, og det er akkurat den jobben som tar tid en tirsdag morgen.

## The Solution

OSE Signal består av to skjermbilder og ett prinsipp.

**Markedsoversikten** viser hele aksjeuniverset — omtrent 30–40 likvide Oslo Børs-aksjer fra flere sektorer, endelig liste fastsettes i PRD — med faktisk kursutvikling, signalstyrke og retning. Brukeren ser på få sekunder hvilke aksjer som skiller seg ut.

**Aksjedetaljen** svarer på hvorfor. Den viser kursgraf, noen få tekniske indikatorer, hvilke faktorer som bidro til signalstyrken, nyheter KI har vurdert som relevante for selskapet, og kommende finansielle hendelser når data finnes. Nyhetene vises med originalkilde og med KI-ens vurdering av relevans: direkte relevant, indirekte relevant eller lite relevant, sammen med type hendelse og en kort forklaring. Der modellen er usikker, vises usikkerheten i stedet for at den gjetter.

**Prinsippet** er at KI-laget kan slås av. Applikasjonen skal fungere uten det, med den regelbaserte analysen alene. Det gjør KI-bidraget synlig og etterprøvbart — vi kan vise nøyaktig hva KI tilfører — og det gjør at en feilende eller treg modell ikke tar ned hovedflyten.

Signalstyrke er ikke en anbefaling om kjøp eller salg, og presenteres ikke som det noe sted i grensesnittet.

Dagens vurderinger lagres automatisk med dato, signalstyrke, retning, bidragende faktorer, relevante nyheter og kurs, slik at de kan hentes frem igjen senere. Historiske sammenligninger bruker utbyttejusterte kurser, slik at et ordinært utbytte ikke feiltolkes som kursfall.

## What Makes This Different

Alternativet i dag er enten å kombinere flere gratis kilder selv, eller å betale for profesjonelle verktøy som er langt mer omfattende enn en vanlig sparer trenger.

Vi har ingen teknisk moat, og skal ikke påstå at vi har det. Datakildene er kommersielle og tilgjengelige for alle. Forskjellen ligger i tre valg:

- **Forklarbarhet før presisjon.** Vi lover ikke bedre signaler enn andre. Vi lover at brukeren alltid kan se hva som ga utslaget.
- **Nyhetsstøy som et eget problem.** KI brukes til den ene oppgaven der den faktisk er bedre enn regler — å avgjøre om en artikkel handler om selskapet.
- **KI som et lag som kan slås av.** Dette er uvanlig i produkter, og det er poenget: det gjør KI-bidraget etterprøvbart.

## Who This Serves

Primærbrukeren er en vanlig sparer som følger norske aksjer ved siden av jobb eller studier, har begrenset tid, og ønsker oversikt uten å bli finansanalytiker.

Suksess for brukeren er å åpne løsningen om morgenen, se hva som har endret seg, forstå hvorfor enkelte aksjer skiller seg ut, og finne de viktigste nyhetene uten å slå opp flere steder.

Vi er selv i målgruppen og skal bruke løsningen gjennom hele prosjektperioden. Vi har ikke gjennomført en større brukerundersøkelse, og briefen bygger derfor ikke på antakelser om et bredere marked.

## Success Criteria

Første versjon er vellykket dersom:

- hele aksjeuniverset hentes og vises uten manuelle mellomsteg
- minst én person utenfor gruppen gjennomfører hovedflyten på omtrent fem minutter og kan forklare hvorfor en valgt aksje skiller seg ut
- aksjedetaljen viser hvilke faktorer som bidrar til signalstyrke og retning
- finansnyheter klassifiseres med originalkilde, og usikre vurderinger markeres som usikre
- KI-laget kan slås av, og applikasjonen fungerer fortsatt uten det
- kommende finansielle hendelser vises der data er tilgjengelig
- dagens vurderinger lagres automatisk med informasjonen som trengs for senere historikk
- manglende data, feilende kilder og dager uten tydelige signaler håndteres uten at hovedflyten stopper eller systemet tvinger frem et resultat
- hovedflytene fungerer stabilt og har et ryddig, gjennomarbeidet grensesnitt i en demonstrasjon
- gruppen bruker løsningen jevnlig fra første fungerende versjon og registrerer feil og forbedringspunkter underveis

Vi setter ikke mål for hvor godt signalene treffer markedet. Formålet er en fungerende og forståelig applikasjon, ikke å bevise at den kan forutsi aksjekurser.

## Scope

### Inne i v1

- norsk desktop-first webapplikasjon
- omtrent 30–40 likvide Oslo Børs-aksjer fra flere sektorer
- markedsoversikt og aksjedetalj
- kursgraf, noen få tekniske indikatorer, signalstyrke og retning
- KI-basert nyhetsfiltrering med kilde og usikkerhet
- av/på-bryter for KI-laget
- kommende finansielle hendelser
- automatisk lagring av daglige vurderinger
- enkelt og gjennomarbeidet brukergrensesnitt

Hvis kjernen står stabilt før fristen: enkel historikkvisning, sektorfilter, flere tidsperioder og lokalt lagrede favoritter.

### Utenfor v1

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

Hvis første versjon fungerer, går veien videre fra generell oversikt til personlig oppfølging. Brukeren kan velge favorittaksjer, lage egne lister, filtrere på sektor, lagre innstillinger og få mer historikk og analyse over tid.

Neste steg er brukerens egen portefølje: legger man inn aksjene man faktisk eier, kan løsningen følge opp nettopp disse selskapene med relevante nyheter, større kursbevegelser og kommende hendelser. Da går OSE Signal fra markedsoversikt til personlig markedsassistent.

På lengre sikt kan løsningen dekke flere børser og tilby både norsk og engelsk. Premiumfunksjoner eller abonnement kan vurderes dersom brukere faktisk opplever løsningen som nyttig nok.

En kommersiell versjon vil kreve egne vurderinger av rettigheter til videreformidling av børsdata, personvern dersom porteføljeopplysninger lagres, og regelverket som gjelder når en tjeneste presenterer finansielle signaler eller anbefalingslignende innhold.
