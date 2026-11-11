---
title: 'Story 8.26: «Vis meg rundt» spiller av siden, knappene øverst og funnene fra demoprøven'
type: 'feature'
created: '2026-11-11'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '7fd5320c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-9-vis-meg-rundt.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-25-spill-av-omvisningen.md'
---

Skrevet 11.11 i instruksjonen kl. 18:01, etter gruppens svar 11.11 kl. 16:58, 17:06, 17:12 og 17:21, med tilleggene 1–4 (ønskene kl. 17:44, svaret kl. 17:47 og ønskene kl. 17:48 og 17:53). Instruksjonen kl. 18:01 erstatter instruksjonen kl. 16:58 og tilleggene kl. 17:06 og 17:12, som aldri kom til vinduet, og tillegget kl. 17:38, som stoppet i steg 0. 8.25 er brukt, så dette er 8.26. Storyen flettes ikke før gruppens ja. Svarene står ikke i repoet ennå; det som står her om dem, er hentet fra instruksjonen og tilleggene.

## Storyen

Som **bruker i demoen og den ekte versjonen**, vil jeg at «Vis meg rundt» viser meg delene av siden der jeg står, uten at siden hopper, at knappene står sammen med sideknappene, og at funnene fra demoprøven er rettet, så sidene er roligere og sier det de viser.

**Oppfyller:** FR-109, svarene 11.11 kl. 16:58–17:53 · **Begrenses av:** NFR-06, `AD-3`, `AD-10`, regel 22

**Avhenger av:** 8.9, 8.25. **Én økt:** nei, delene bygges etter hverandre.

## Svarene

*Svar 2026-11-11 kl. 16:58 (gruppens svar):* «Vis meg rundt» starter den samme boksen som omvisningen, bare med stegene for siden man står på, og den nummererte lista fra 8.9 tas bort, fordi testpersonen 10.11 gikk seg vill når siden hoppet. Siste steg på en side har «Ferdig» og lenken «Spill av hele omvisningen». Tilbudet første gang står som før.

*Svar 2026-11-11 kl. 17:06 (gruppens svar):* «Vis meg rundt» og «Spill av omvisningen» står i raden øverst etter «Innstillinger», i samme stil som sideknappene og med hvert sitt ikon, og raden under demolinja blir borte. Rådet anbefalte én knapp, men gruppen valgte to. «?» ved Hovedindeksen sier: «OSEBX er hovedindeksen på Oslo Børs. I demoen heter den oppdiktede indeksen DEMIX.»

*Svar 2026-11-11 kl. 17:12 (gruppens svar):* «Dine egne aksjer» i Min liste får samme stil som oversikten og «Følg en aksje», og «Lista er full …» står ikke i rødt, fordi rødt betyr negativ.

*Svar 2026-11-11 kl. 17:21 (gruppens svar):* bryteren «Vis KI-tekst» ved «Børsdagen kort fortalt» og på aksjesiden blir oransje som i Innstillinger, og «Laget av KI» står grått, fordi det er en merkelapp og ikke en knapp. Punktet i `issues.md` (spørsmål 5 i 8.2b) lukkes.

*Ønsket 2026-11-11 kl. 17:44 (tillegg 1 og 2):* fotnoten under tabellen tas bort, og de andre løse tekstene mellom delene får et forslag hver. «uten data» får en forklaring, som «for kort historikk», og «Ukjent» som retning forklares bak «?».

*Svar 2026-11-11 kl. 17:47 (tillegg 3, rådet anbefalte alt):* en aksje som følges, får stjerne og står i Min liste med en gang; aksjene som venter på henting, står nederst i tabellen med «venter på henting»; og der «lista» betyr alle aksjene appen følger, sies det slik.

*Ønskene 2026-11-11 kl. 17:48 og 17:53 (tillegg 4, rådet var enig):* filteret «Alle», «3 av 3 positiv» og «3 av 3 negativ» tas bort, og lenken «Den ekte versjonen» åpnes i en ny fane.

Rådet anbefalte alle unntatt det med to knapper.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Uten skriptet.** *Forslag:* begge knappene er skjult til skriptet er lastet, som «Spill av omvisningen» i 8.25, så de aldri står uten å virke. Uten skriptet er det ingen «Vis meg rundt»; lista fra 8.9 var reserven, og den er tatt bort etter svaret kl. 16:58.
2. **Ikonene.** *Forslag:* et kompass for «Vis meg rundt» og en avspillingsknapp i en sirkel for «Spill av omvisningen», 16 px med strek 2 som de andre ikonene i raden.
3. **«Spill av hele omvisningen».** *Forslag:* lenken står bare på siste steg med «Vis meg rundt». I hele omvisningen går «Neste» videre til neste side som før, og siste steg har «Ferdig».
4. **«Vis meg rundt» og en annen side.** *Forslag:* «Vis meg rundt» lagrer ingenting, så boksen lukkes når man går til en annen side, og en omvisning som er i gang, fortsetter ikke av den.
5. **Ved 390 px.** *Forslag:* knappene brytes over flere linjer som sideknappene i dag, uten rulling.

## Delene

Hver del har tester med «Ville feilet hvis» i `tests/test_vis_meg_rundt_8_26.py`, og én mutant.

### 1) «Vis meg rundt» spiller av siden, og knappene øverst (kl. 16:58 og 17:06)

**Ville feilet hvis:** «Vis meg rundt» hadde andre steg enn sidens egne, et steg sendte brukeren til en annen side, siste steg manglet «Ferdig» eller lenken til hele omvisningen, knappene ikke sto i raden etter «Innstillinger» med hvert sitt ikon, lista fra 8.9 eller raden under demolinja sto igjen, eller det var ulikt i demoen og den ekte versjonen.
