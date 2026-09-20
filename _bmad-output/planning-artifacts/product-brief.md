# Product Brief: OSE Signal

**Emne:** IBE160 Programmering med KI, Høgskolen i Molde  
**Gruppe:** G74 – Joakim Lund, Marian Osen

## Executive Summary

En vanlig sparer som følger norske aksjer bruker flere tjenester for å finne ut det samme: hva beveget seg i går, hvorfor, og er det noe viktig på vei. OSE Signal er en norsk webapplikasjon for PC som samler dette i én oversikt, slik at spørsmålet kan besvares på omtrent fem minutter om morgenen.

Løsningen følger et fast utvalg likvide Oslo Børs-aksjer og viser kursutvikling, signalstyrke og retning, med mulighet for å se hva som ligger bak. Beregninger og grovsortering av meldinger gjøres med vanlig programkode. KI brukes der språkforståelse gir en reell fordel: å forklare hva en børsmelding betyr, og å vurdere relevans der kategorifeltet ikke strekker til.

Prosjektet er mulig nå fordi KI-assistert utvikling gjør det realistisk for to studenter å bygge en sammensatt applikasjon, samtidig som språkmodeller brukes som en del av produktet. Første versjon er på norsk, kjører lokalt, og prioriterer stabilitet fremfor mange funksjoner.

## The Problem

Den som følger 10–30 norske aksjer ved siden av jobb eller studier har ikke et informasjonsproblem, men et sorteringsproblem. Kursene, meldingene og rapportdatoene finnes, men ligger på ulike steder og i ulikt format, og det meste er irrelevant akkurat i dag.

Støyen er målbar, og den har to former. I vår egen test 17.09 leste vi manuelt de ti siste nyhetstreffene for et utvalg selskaper. For et stort finansselskap handlet flertallet i realiteten om andre selskaper; det var bare ett av mange symboler i artikkelen. For et shippingselskap var bildet motsatt. En løsning kan altså ikke anta at en nyhet knyttet til et symbol handler om det selskapet.

Den andre formen finnes i selskapenes egne børsmeldinger. Et tilfeldig døgn ga 102 meldinger fra 73 utstedere, men 31 av dem var rene rentejusteringer — formelt pliktige, uten betydning for en sparer. Mengden er ikke problemet. Sorteringen er.

I tillegg kommer forklaringsproblemet. Gratis markedsoversikter viser at en aksje er opp 4 %, men ikke hvorfor. Å koble kursbevegelse, meldingsbilde og kommende hendelser er jobben som tar tid en tirsdag morgen.

## The Solution

OSE Signal består av to skjermbilder og ett prinsipp.

**Markedsoversikten** viser omtrent 15 likvide Oslo Børs-aksjer fra flere sektorer, endelig liste fastsettes i PRD, med kursutvikling, signalstyrke og retning. Signalstyrken viser hvor kraftig kriteriene slår ut, retningen om bidragene samlet peker positivt, negativt eller er blandet.

**Aksjedetaljen** svarer på hvorfor: kursgraf, noen få tekniske indikatorer, hvilke faktorer som bidro, relevante børsmeldinger med lenke til originalen, og kommende hendelser. Meldinger kommer ferdig merket med utsteder og kategori, så grovsorteringen gjøres med regler i kode. KI brukes på det som passerer — til å forklare hva meldingen betyr, og til å vurdere relevans der kategorien ikke skiller. Er vurderingen tvilsom, merkes den som usikker.

**Prinsippet** er at KI-laget kan slås av. Applikasjonen skal fungere med den regelbaserte analysen alene. Det gjør KI-bidraget etterprøvbart, og hindrer at en treg modell tar ned hovedflyten.

Signalstyrke er ikke en anbefaling om kjøp eller salg, og presenteres ikke som det.

## Data og kilder

Kursdata hentes fra EODHD, børsmeldinger fra Oslo Børs' NewsWeb der hver melding allerede er knyttet til utsteder og kategori, og finansielle hendelser fra Euronext.

Universet er satt til omtrent 15 aksjer fordi EODHD på gratisnivå gir 20 API-kall i døgnet og kurser koster ett kall per symbol; NewsWeb og Euronext koster ingen kall. Tallet er utledet av kvoten, ikke valgt etter skjønn. Målingene og bruksvilkårene vi har sjekket er dokumentert i `docs/kilder-og-rettigheter.md`. Oppdateringsmekanikk og lagring hører til PRD og arkitektur.

## What Makes This Different

Vi har ingen teknisk moat, og skal ikke påstå at vi har det. Datakildene er åpne eller kommersielt tilgjengelige for alle.

| Alternativ i dag | Hvorfor det tolereres | Hvorfor vår løsning er bedre |
|---|---|---|
| Kombinere gratis kilder selv | Gratis og kjent | Koblingen mellom kurs, melding og hendelse er allerede gjort |
| Profesjonelle verktøy | Dekker alt | Dekker det en sparer faktisk bruker, uten å kreve opplæring |
| Bare lese overskrifter | Koster ingen tid | Overskrifter sier ikke hva som gjelder egne aksjer |

Den viktigste forskjellen er at kode og KI holdes fra hverandre: regler sorterer, KI forklarer, og grensen er synlig i grensesnittet — ikke bare i koden. Vi lover ikke bedre signaler enn andre, men at brukeren alltid kan se hva som ga utslaget.

## Who This Serves

Primærbrukeren er en vanlig sparer som følger norske aksjer ved siden av jobb eller studier, har begrenset tid, og vil ha oversikt uten å bli finansanalytiker. Suksess er å åpne løsningen om morgenen, se hva som har endret seg, forstå hvorfor noe skiller seg ut, og finne det viktigste uten å slå opp flere steder.

Vi er selv i målgruppen og bruker løsningen gjennom prosjektperioden. Vi har ikke gjennomført en brukerundersøkelse, og briefen bygger derfor ikke på antakelser om et bredere marked.

## Success Criteria

| Signal | Hva vi måler | Mål | Når |
|---|---|---|---|
| Brukerutfall | Person utenfor gruppen gjennomfører hovedflyten og forklarer uoppfordret hvorfor en aksje skiller seg ut | Minst 1 person, under 5 minutter, uten hjelp | Før innlevering |
| Adopsjon | Gruppen bruker løsningen på egne aksjer og logger feil | Minst 4 av 5 børsdager fra første fungerende versjon | Løpende |
| Kvalitet | Daglig henting fullfører innenfor API-kvoten; ved kildefeil vises siste kjente data med tidsstempel | Ingen manuelle steg, ingen stopp ved manglende data | Ukentlig |
| KI-bidrag i drift | Hvilke meldinger KI-laget forklarte eller omklassifiserte som regelfilteret alene ikke skilte | Dokumentert eksempelsett fra minst én ukes drift | Før demonstrasjon (est. uke 45) |
| Relevanseksperiment | Testsett på 50 medieartikler merket manuelt, kjørt mot både symbolmatching og KI-klassifisering | Eksperimentet gjennomført og tallene dokumentert — ikke at KI kommer best ut | Est. uke 41 |
| Fortsatt bruk | Om vi bruker løsningen frivillig etter at utviklingen er ferdig, ikke bare for å teste den | Brukt minst tre dager i uka de to siste ukene før innlevering, loggført | Ved innlevering |

Relevanseksperimentet er et avgrenset delprosjekt, ikke en del av driften. Viser målingen liten forskjell, er det også et funn: eksperimentet skal avgjøre påstanden, ikke bekrefte den. Vi setter ikke mål for hvor godt signalene treffer markedet. Ukenumrene er planestimater som fastsettes endelig i PRD og sprintplan.

## Scope

**Inne i v1:** markedsoversikt og aksjedetalj for omtrent 15 likvide Oslo Børs-aksjer; signalstyrke og retning med synlig begrunnelse; børsmeldinger sortert av regler og forklart av KI; av/på-bryter for KI-laget; kommende finansielle hendelser.

**Utenfor v1:** brukerkontoer, innlogging og personlig portefølje; varsler, betaling, mobiltilpasning og meglerintegrasjon; flere børser og flere språk; fundamental- og verdimodell, intradag og sanntidsdata; statistisk studie av om signalene slår markedet.

Første versjon kjører lokalt og publiseres ikke. Vurderingen av videreformidlingsrett er derfor utsatt til en eventuell kommersiell versjon.

## Vision

Hvis første versjon fungerer, går veien fra generell oversikt til personlig oppfølging: favorittaksjer, egne lister og mer historikk. Neste steg er brukerens egen portefølje — legger man inn aksjene man faktisk eier, følger løsningen opp nettopp disse selskapene. Da går OSE Signal fra markedsoversikt til personlig markedsassistent.

På lengre sikt kan løsningen dekke flere børser og flere språk. En kommersiell versjon vil kreve egne vurderinger av videreformidlingsrett, personvern og regelverket som gjelder når en tjeneste presenterer finansielle signaler.
