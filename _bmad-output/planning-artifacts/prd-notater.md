# Notater til PRD — OSE Signal

Arkitektur- og implementasjonsstoff flyttet ut av Product Brief 19.09.2026, fordi
briefen skal beskrive opplevelse og utfall, ikke teknologivalg. Innholdet er målt,
ikke antatt, og hører hjemme i PRD-en der det får plass til å være presist.

## Datakilder og kvote

Kursdata og OSEBX hentes fra EODHD. Børsmeldinger hentes fra Oslo Børs' NewsWeb, der
hver melding allerede er knyttet til utsteder og kategori. Kommende finansielle
hendelser hentes fra Euronext sin finanskalender. Kalenderen oppgir ikke ticker
eller ISIN, så hendelser må kobles til selskap via en oppslagstabell vi setter opp
for aksjeuniverset én gang. Alpha Vantage ble testet som alternativ, men
Oslo Børs-symbolene var ikke pålitelige nok til å være hovedkilde.

Universet er satt til omtrent 15 aksjer fordi EODHD på gratisnivå gir 20 API-kall i
døgnet og kurser koster ett kall per symbol; NewsWeb og Euronext koster ingen kall.
Tallet er utledet av kvoten, ikke valgt etter skjønn.

Målte kalltall 19.09.2026: se `docs/kilder-og-rettigheter.md` for kildestatus og
vilkår. Bulk-endepunktet koster 100 kall flatt og er ubrukelig på gratisnivå.
EODHDs nyhets-API tar ett ticker per kall og brukes bare til relevanseksperimentet,
som bruker restkvoten én gang og ikke inngår i den daglige driften.

## Henting og oppdatering

Henting og KI-behandling skjer som en bakgrunnsoppgave, ikke ved hver sidevisning.
Er lagrede data eldre enn siste børsslutt når applikasjonen starter, hentes nye data
da — kurser først, deretter meldinger — mens siste kjente data vises med tidsstempel.
Brukeren venter aldri på en henting.

Den regelbaserte analysen styrer hvor KI-laget arbeider: signalstyrke beregnes for
hele universet lokalt, mens nyheter hentes og KI-vurderes bare for selskapene som
skiller seg ut den dagen. Åpner brukeren en aksje uten utslag, hentes nyhetene for
den ved behov og lagres ut dagen. Det holder datakostnaden nede og retter
vurderingene mot de aksjene brukeren faktisk skal lese om.

Rådata lagres fra første kjøring, slik at prosjektet ikke står tomhendt om en kilde
endres. Dette er en reell risiko: NewsWeb-API-et er udokumentert backend for Oslo
Børs' egen nettside.

### Krav: merking av justert kurs i grensesnittet

Markedsoversikten viser `close`, mens endringen i prosent regnes på `adjusted_close`.
Det er riktig — et ordinært utbytte skal ikke se ut som et kursfall — men det har en
synlig konsekvens: på en utbyttedag stemmer ikke differansen mellom to viste sluttkurser
med den viste prosenten. En bruker som regner etter vil se det som en feil.

Kravet er derfor at utbyttedager merkes i grensesnittet, slik at avviket er forklart
i stedet for å se ut som en bug. Dette må være på plass før demonstrasjonen.
Observert under bygging av den vertikale skiva 20.09.2026.

Historiske sammenligninger bruker utbyttejusterte kurser, slik at et ordinært utbytte
ikke feiltolkes som kursfall.

## Hvorfor kategorifeltet ikke er nok

Grovsorteringen — bort med rentejusteringer og rene formaliteter — gjøres med regler
i vanlig programkode på NewsWebs kategorifelt. KI brukes på det som passerer.

Grensen går ved samlekategorien for ikke-regulatoriske pressemeldinger, der
kategorifeltet ikke skiller en kontraktstildeling fra et sponsorat. Det er det
konkrete tilfellet som begrunner relevansvurderingen med KI; uten det er påstanden
om at regler ikke strekker til udokumentert.

## Usikkerhet i KI-vurderinger

Usikkerhet avledes av observerbare kjennetegn, ikke av en selvrapportert sikkerhetsscore
fra modellen: om selskapet nevnes i overskrift eller ingress, om mange selskaper nevnes
likeverdig i samme sak, og om to kjøringer gir samme klassifisering. Der kjennetegnene
spriker, merkes vurderingen som usikker i stedet for at modellen tvinges til et svar.

Det midterste kriteriet kommer direkte fra testen 17.09: for et stort finansselskap
handlet flertallet av nyhetstreffene i realiteten om andre selskaper, der symbolet bare
var ett av mange i artikkelen.

## Åpne spørsmål

- Hvilke 15 aksjer, og etter hvilke kriterier
- Hvor mange meldinger som skal regnes som «passerer filteret» — kategorihvitliste
  eller KI-terskel. Krever at gruppen ser på et par ukers meldinger først.
