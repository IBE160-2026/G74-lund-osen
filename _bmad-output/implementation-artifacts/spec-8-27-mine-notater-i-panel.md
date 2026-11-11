---
title: 'Story 8.27: «Mine notater» i et panel fra en knapp øverst'
type: 'feature'
created: '2026-11-11'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'db89c5ba'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-21-egne-notater-paa-aksjesiden.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-24-notatene-to-ting.md'
---

Skrevet 11.11 etter instruksjonen kl. 21:25 og tillegg 1 kl. 21:40, etter gruppens svar 11.11 kl. 21:09–21:20 og kl. 21:36. Rådet foreslo to snarveier først, og gruppen valgte panelet nå, uten mobil. Rådet anbefalte å starte i kveld. Instruksjonene lagres i `docs/ai-prompts/2026-11-11.md` med flettingen. Svarene kl. 21:09–21:20 og 21:36 står ikke i repoet ennå; det som står her om dem, er hentet fra instruksjonene. 8.26 er tatt av vinduet som gjør «Vis meg rundt» (grenen `8-26-vis-meg-rundt-spiller-av-siden`), så dette er 8.27.

## Storyen

Som **bruker**, vil jeg nå notatene mine fra hvilken som helst side, i et panel ved siden av det jeg ser på, så jeg kan skrive og lese notater uten å gå fra siden.

**Oppfyller:** svarene 11.11 kl. 21:09–21:20 og 21:36 · **Begrenses av:** NFR-06, `AD-3`, `AD-10`

**Kontroll — hva testen ser etter:**
- Knappen «Mine notater» står øverst etter «Min liste», med eget ikon, og er borte når bryteren «Notater» er av
- Fra 1056 px åpner knappen et panel fast i kanten, som siden gir plass til, og som kan flyttes til venstre eller høyre; om det er åpent, og hvilken side det står på, huskes i nettleseren
- Panelet har alle notatene, de nyeste først, som i Min liste, og et skjema for et nytt notat: på aksjesiden for aksjen og dagen siden viser, ellers med et valg blant aksjene i lista; etter lagring kommer siden tilbake med panelet åpent
- Smalere enn 1056 px, og uten skript, går knappen til notatene i Min liste
- I demoen sier panelet at notatene står til demoen startes på nytt
- På aksjesiden står «Mine notater» nederst, med skjemaet, de to nyeste notatene og «Vis alle (N)»
- **Ville feilet hvis:** knappen sto med bryteren av, panelet manglet et notat eller hadde en annen rekkefølge, et notat fra panelet fikk en annen aksje eller dag, svaret gikk til en annen side, eller nettsiden skrev noe annet enn notatene

**Avhenger av:** 8.0f, 8.21, 8.24. **Én økt:** ja.

## Det gruppen har avgjort

*Svarene 11.11 kl. 21:09–21:20, slik instruksjonen kl. 21:25 gjengir dem:*
- Knappen «Mine notater» står øverst etter «Min liste», i samme stil som sideknappene og med eget ikon, og er borte når bryteren «Notater» i Innstillinger er av.
- Fra 1056 px åpner knappen et panel på siden man står på, fast i kanten som hjelpen (8.0f), som gir plass til det, og som kan flyttes til venstre eller høyre. Om panelet er åpent, og hvilken side det står på, huskes i nettleseren fra side til side og fra gang til gang.
- Panelet har alle notatene, de nyeste først, med det samme som «Mine notater» i Min liste, og navnet går til aksjesiden. Et skjema skriver et nytt notat: på aksjesiden for den aksjen og dagen siden viser, ellers med et valg blant aksjene i lista. Etter lagring kommer siden tilbake med panelet åpent.
- Smalere enn 1056 px går knappen til notatene i Min liste, uten panel.
- I demoen står det i panelet at notatene står til demoen startes på nytt, fordi demobasen lages på nytt da.
- Nettsiden skriver bare notatene, som før (AD-10), og testene bruker bare testbaser. Alt gjelder demoen og den ekte versjonen likt.

*Svaret 11.11 kl. 21:36, slik tillegg 1 kl. 21:40 gjengir det:* på aksjesiden flyttes «Mine notater» nederst, etter «Signalet dag for dag» og knappen til investorsiden, fordi siden ble lang. Delen har skjemaet og de to nyeste notatene for aksjen, og «Vis alle (N)» under, som viser resten på samme side. Lenkene til notatene går fortsatt dit, og bryteren «Notater» skjuler delen som før.

*Svaret 11.11 kl. 22:20, slik tillegg 2 kl. 22:21 gjengir det:* knappen «Mine notater» får et steg i omvisningen: hva panelet er, at det kan flyttes til venstre eller høyre, og at notatene lagres på maskinen, i demoen til den startes på nytt. Steget står i den hele omvisningen og i «Vis meg rundt», helst i delen for Min liste, og bare når bryteren «Notater» er på. Vinduet som gjør «Vis meg rundt» (8.26), bygger om omvisningen, så steget legges inn når 8.26 er flettet og main er flettet inn i grenen. Rådet anbefalte det.

*Svaret 11.11 mellom kl. 21:41 og 21:43 (i økta, klokka lest før og etter):* storyen står under «Ekstra, hvis tiden rekker» bare i `epics.md`, fordi lista ble tatt ut av README-en etter svaret kl. 16:26. Den føres under «Ekstra, ferdig» i README-en når den er flettet, slik 8.25 ble ført.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Hjelpen og panelet samtidig.** *Forslag:* mens panelet er åpent, åpnes hjelpen ved «?» over panelet, på samme side, og knappen «Flytt» i hjelpen er borte. Siden gir da plass til ett felt, ikke to, så den ikke blir smal ved 1280 px. Når hjelpen lukkes, står panelet der igjen.
2. **Knappene ved notatene i panelet.** *Forslag:* de samme som i Min liste, «Noter et tenkt kjøp», «Noter et tenkt salg» og «Slett», med de samme reglene, og svaret går tilbake til siden man står på, med panelet åpent.
3. **Dagen for et notat fra panelet utenfor aksjesiden.** *Forslag:* siste dag med kurs for aksjen man velger, som aksjesiden viser uten «Vis dagen». Skjemaet sier det.
4. **Aksjene i valget.** *Forslag:* aksjene i lista appen følger, som ikke er tatt ut og har kurser, etter navnet. Det er de samme som kan få et notat på aksjesiden.
5. **Valget på aksjesiden.** *Forslag:* på aksjesiden har skjemaet ikke noe valg; notatet får aksjen og dagen siden viser, med de samme reglene som skjemaet i delen nederst (ingen skjema for en dag uten kurs eller for en aksje som er tatt ut).
6. **Hva som huskes.** *Forslag:* om panelet er åpent, og siden det står på, står i `localStorage`, så det huskes fra gang til gang. Hjelpen husker fortsatt siden sin bare mens fanen er åpen (`sessionStorage`, 8.0f), så de to valgene er hver for seg.
7. **Knappen i Min liste.** *Forslag:* knappen åpner panelet også der, selv om notatene står nederst på siden, så den virker likt på alle sidene.
8. **«Vis alle (N)».** *Forslag:* N er alle notatene for aksjen. Knappen er en `<details>`, så den virker uten skript, og den står bare når aksjen har mer enn to notater.
9. **Omvisningen og «Vis meg rundt».** *Forslag:* ingen av dem har et steg for notatene på aksjesiden i dag, så denne storyen endrer dem ikke. Vinduet som gjør «Vis meg rundt», følger den nye rekkefølgen når 8.26 er flettet.
10. **Panelet på smal skjerm.** *Forslag:* smalere enn 1056 px er knappen en lenke til «Mine notater» i Min liste, og et åpent panel lukkes når vinduet blir smalere, men valget huskes, så det åpnes igjen når vinduet blir bredt.
11. **Innholdet i panelet.** *Forslag:* innholdet lages på serveren og står i en `<template>` i hver side, som ikke vises og ikke leses opp, og skriptet setter det inn når panelet åpnes. Skriptet henter da ingenting, som testen fra 8.0f krever (`test_skriptet_henter_ingenting`), og panelet er der med en gang etter lagring. Prisen er at hver side leser alle notatene, som Min liste gjør. Den første utgaven hentet innholdet med `fetch` fra en egen rute, og det ble tatt bort før første commit.
12. **Eldre tester som er endret etter svarene.** *Forslag:* fire tester sa det motsatte av svarene, og er endret med en linje om svaret: at stripa ikke får en knapp for notatene (8.21, del F), at stripa har fire ikoner (8.10), at «Mine notater» står over «Signalet dag for dag» (8.21), og at ingen del står etter boblen til investorsiden (3.4h). Lenketesten godtar `/min-liste#mine-notater`.
13. **Steget for knappen i omvisningen (tillegg 2).** *Forslag:* ett steg i delen for Min liste, rett etter stegene for Min liste og før «Følg en aksje», som peker på knappen øverst, med teksten: «Mine notater åpner et panel i kanten av siden med alle notatene dine, og et skjema for et nytt notat. Panelet kan flyttes til venstre eller høyre. Notatene lagres på denne maskinen.» I demoen kommer «, i demoen til den startes på nytt» før punktumet. Steget står i den hele omvisningen og i «Vis meg rundt» for Min liste, og er borte når «Notater» er av. Det står ikke på de andre sidene, så lista i «Vis meg rundt» ikke blir lengre der.

## Delene

### A) Knappen øverst

`src/templates/_ramme.html`: «Mine notater» etter «Min liste», med eget ikon, som en lenke til `/min-liste#mine-notater`, bare når `vis_notater` er på.

**Ville feilet hvis:** knappen sto med bryteren av, sto et annet sted i raden, manglet ikonet, eller gikk et annet sted enn til notatene i Min liste.

### B) Panelet

`src/templates/_notatpanel.html` i en `<template>` i rammen, med alle notatene fra `_alle_notatene` i `src/app.py` (`_notatpanelet`), og `src/static/hjelp.js` og `src/static/stil.css`: fra 1056 px åpner knappen panelet fast i kanten, siden gir plass, «Flytt» bytter side, «Lukk» og Esc lukker, og valgene huskes i `localStorage`.

**Ville feilet hvis:** panelet manglet et notat, hadde en annen rekkefølge enn Min liste, sto på en side der bryteren var av, eller ikke ble husket.

### C) Skjemaet i panelet

På aksjesiden skriver skjemaet for aksjen og dagen siden viser; ellers velges aksjen, og notatet får siste dag med kurs. Ruta `skriv_notat_valgt` (`POST /notat`) skriver bare tabellen notat. Svaret går til siden man sto på (`tilbake`, bare en sti i appen, `_panelsiden`), med `#notatpanel`. Knappene ved notatene i panelet sender også `tilbake`.

**Ville feilet hvis:** notatet fikk en annen aksje eller dag, en aksje utenfor lista ble godtatt, svaret gikk til en adresse utenfor appen, eller panelet ikke var åpent etter lagring.

### D) Demoen

Panelet sier i demoen at notatene står til demoen startes på nytt.

**Ville feilet hvis:** linja manglet i demoen eller sto i den ekte versjonen.

### E) Plassen på aksjesiden (tillegg 1)

`src/templates/aksje.html`: «Mine notater» etter boblen til investorsiden, med skjemaet, de to nyeste notatene og «Vis alle (N)».

**Ville feilet hvis:** delen sto over «Signalet dag for dag», viste mer eller mindre enn de to nyeste, eller «Vis alle» manglet et notat.

### F) Steget i omvisningen (tillegg 2)

*Venter:* 8.26 bygger om omvisningen og «Vis meg rundt», og var ikke flettet 11.11 kl. 22:21 (main sto på `db89c5ba`). Steget legges inn når 8.26 er flettet og main er flettet inn i grenen, etter forslaget i spørsmål 13. Er 8.26 ikke flettet når resten av 8.27 er grønn, venter steget, og PR-en sier det.

**Ville feilet hvis:** steget manglet i den hele omvisningen eller i «Vis meg rundt» for Min liste, sto med «Notater» av, eller manglet linja om demoen i demoen.
