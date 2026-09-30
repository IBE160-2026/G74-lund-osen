# Epic 8 Context: Tydelig for den som ikke har bygget den

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

En person utenfor gruppen skal forstå begge skjermbildene, markedsoversikten og
aksjedetaljen, uten hjelp, og designet skal være vurdert, ikke bare arvet fra
kravene. Epicen innfrir suksessmålet «Brukerutfall»: minst én person utenfor
gruppen gjennomfører hovedflyten og forklarer uoppfordret hvorfor en aksje
skiller seg ut, på under 5 minutter, før prosjektinnlevering. Hovedflyten er å
åpne oversikten, se hvilke aksjer som skiller seg ut, åpne én og lese hvorfor.
Epicen har ingen nye FR-er, men prøver FR-101–103, FR-201–204 og FR-706 fra
utsiden, under NFR-05 og NFR-06. Den er skilt fra Epic 3 fordi brukertesten ikke
skal vente på Dockerfilen. *Status 30.09:* alle tre storyene står som `backlog`
i sprint-status. 8.0 ble lagt til 29.09.

## Stories

- Story 8.0: De rene feilene i de to skjermbildene
- Story 8.1: Brukertest rett etter Epic 2
- Story 8.2: UX-gjennomgang av de to skjermbildene med `[CU] bmad-ux`

## Requirements & Constraints

- **Tall skrives norsk der de leses** (regel 21): desimalkomma, hardt
  mellomrom som tusenskille og foran %, vanlig bindestrek som minus. Hvor mange
  desimaler hver type tall har, avgjøres i **én funksjon med tester**, ikke i
  hver mal. Avrunding skjer bare ved visning; «-0,00» vises aldri. Endringen i
  oversikten beholder to desimaler, så rekkefølgen etter absolutt endring kan
  leses av. En måling som blir lik grensen etter avrunding uten å være det, får
  så mange desimaler at forskjellen synes.
- **Oversikten har nøyaktig fem kolonner:** selskap, sluttkurs (`close`),
  endring (på `adjusted_close`), signalstyrke og retning. Selskapsnavnet er
  lenken til aksjedetaljen, og aksjedetaljen har en synlig vei tilbake. En
  sjette kolonne er utelukket, også for merking eller navigasjon.
- **Sortering:** styrke fallende, så absolutt endring; aksjer uten gyldig signal
  sist; tidsstempelet påvirker ikke sorteringen. Datoen over tabellen skal ikke
  avhenge av sorteringen. Sidens tidsstempel er det eldste `sist_hentet`, i norsk
  tid.
- **Retningen vises i tre kanaler:** tekst, symbol og farge, med FR-704s ord
  uendret (Positiv, Negativ, Blandet, Ingen). Teksten bærer; symbolet skjules
  for skjermlesere. «Ukjent» er fraværet av en vurdering, ikke en femte retning.
- **En aksje skiller seg ut ved styrke 2 eller høyere** (FR-705), og det skal
  merkes med tekst, ikke bare farge.
- **Aksjedetaljen viser alle tre sjekkene**, også de som ga 0, med navn, verdi
  og målingen bak verdien, slik at brukeren kan regne etter. Uten gyldig signal:
  svar 200, grafen så langt dataene rekker, og en beskjed med grunnen i stedet
  for sjekkene. Tegnforklaringen sier at linjene er utbyttejustert kurs.
- **NFR-05:** all brukervendt tekst er norsk, med æ, ø og å. **NFR-06:** ingen
  formulering skal kunne leses som en anbefaling om kjøp eller salg. Ordlyden
  leses mot begge i hver story.
- **Brukertesten (8.1)** bruker ekte data fra siste henting og begge
  skjermbildene. Tiden måles fra første skjermbilde til forklaringen er gitt,
  forklaringen noteres ordrett, og personen får aldri spørsmålet om hvorfor en
  aksje skiller seg ut. Testen skal også svare på om 15 rader er for tett, ved
  observasjon, ikke ved å spørre. Funnene føres i `docs/` med dato.
- **UX-gjennomgangen (8.2)** er en gjennomgang av skjermbildene som finnes, ikke
  design fra bunnen: ingen nye skjermbilder og ingen ny funksjonalitet. Hver
  forbedring knyttes til et skjermbilde og et krav og blir en egen liten endring
  med test. Den skal også si på papir hvordan et tredje skjermbilde ville passet
  inn i navigasjonen, uten å bygge det.
- **Hver story** har en «ville feilet hvis»-kontroll og tester uten nett.

## Technical Decisions

- **Kjernen er ren logikk** (`markedsoversikt.py`, `aksjedetalj.py`,
  `graf.py`, `signalberegning.py` m.fl.): ingen I/O og ingen HTML. `app.py` og
  malene under `src/templates/` bærer en stor del av visningskravene (blant annet
  FR-103, FR-202, FR-204 og FR-706), så endringer i visningen treffer ofte både
  kjerne og mal.
- **Én formateringsfunksjon** eies av 8.0 og brukes av 2.1c når forklaringen
  lages av `maaling` og `grense`. I kode, base, JSON og CSV er tall punktum uten
  tusenskille, lagret med full presisjon.
- **Plan B (28.09):** meldinger, hendelser og KI over meldinger er ute av v1.
  Aksjedetaljen får i stedet KI-tekst under regelforklaringen (Epic 10) og én
  lenke til selskapets side på NewsWeb. Fotnoten i aksjedetaljen og
  docstringene i `app.py` og `aksjedetalj.py` skal si det som stemmer etter
  plan B (8.0).
- **Låste signalparametre** (terskel 2, volumfaktor 1,5, nøytralsone ±2 %,
  vinduer 20 og MA 50) endres ikke uten ny måling.

## UX & Interaction Patterns

- Det finnes ingen egne UX-DR-er; UX-innholdet ligger i FR-ene over. Designet
  ble bevisst ikke laget på forhånd, og 8.2 er oppfølgingen av det valget.
- Fokus og lenker: selskapsnavnet skal se ut som en lenke og ha synlig fokus, og
  veien tilbake skal være like tydelig.
- To v1.1-idéer bør ifølge PRD-en bygges før 8.1, så testen viser om de brukes:
  «Hjelp bak et spørsmålstegn» og «Lær noe nytt». Begge er fast tekst uten
  nettkall, og tall i teksten hentes fra parametrene i `signalberegning.py`. De
  er ikke stories i Epic 8.

## Cross-Story Dependencies

- **8.0 → 8.1 → 8.2.** 8.0 har ingen avhengigheter og rydder kjente feil, så
  8.1 tester skjermbildene og ikke dem. 8.2 bygger på funnene fra 8.1.
- **8.1 venter på Epic 2**, ikke Epic 3: den trenger ekte data og begge
  skjermbildene, ikke Docker. Etter endringsforslaget 28.09 kan den tas når 2.2
  og 2.7 er ferdige, uten å vente på 2.4 og 2.6. Planlagt tidlig i uke 42, med
  historikk fra uke 40 og 41.
- **2.1c** bruker formateringsfunksjonen fra 8.0.
- **Epic 10.4** (måle KI-bidraget) er en egen brukertest etter 8.1.
- **Kutt:** 8.2 står først i lista over hva som kan kuttes.
