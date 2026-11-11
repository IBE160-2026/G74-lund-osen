---
title: 'Story 8.25: «Spill av omvisningen» ved «Vis meg rundt»'
type: 'feature'
created: '2026-11-11'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'd6e3b4a3'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-9-vis-meg-rundt.md'
---

Skrevet 11.11 i instruksjonen kl. 23:02 10.11, etter gruppens svar 10.11 kl. 22:59. Rådet anbefalte onsdag, men gruppen valgte i natt. Storyen flettes ikke nå: PR-en stopper når CI er grønn, med bilder av stegene og spørsmålene samlet for gruppen, og flettingen og føringen i dagsfila og `epics.md` kommer i en egen instruksjon etter gruppens ja. Svaret kl. 22:59 står ikke i repoet ennå; det som står her om det, er hentet fra instruksjonen. 8.22, 8.23 og 8.24 er brukt, så dette er 8.25.

Svaret endrer svaret 10.11 kl. 11:52 om 8.9, at rundturen ikke flytter seg fra del til del. Det har fått en Rettet-linje i `spec-8-9-vis-meg-rundt.md` og under 8.9 i `epics.md`.

## Storyen

Som **ny bruker**, vil jeg kunne spille av en omvisning som går side for side gjennom appen og viser hva hver del er, så jeg finner fram uten å lese alt først.

**Oppfyller:** FR-109, svaret 10.11 kl. 22:59 · **Begrenses av:** NFR-06, `AD-10`

**Kontroll — hva testen ser etter:**
- Knappen «Spill av omvisningen» ved «Vis meg rundt» starter en omvisning gjennom oversikten, en aksjeside, børsometeret, Min liste og Innstillinger, i den rekkefølgen
- Hvert steg merker én del av siden og viser en kort tekst fra de samme tekstene som «Vis meg rundt», med «Tilbake», «Neste» og «Lukk»; Esc lukker, fokus flyttes til steget, og skjermleseren får rollen dialog
- Den nummererte lista fra 8.9 står
- Første gang appen åpnes, tilbys omvisningen én gang, og et nei huskes
- Ingen tekst gir råd, og omvisningen er lik i demoen og i den ekte versjonen
- **Ville feilet hvis:** omvisningen gikk i en annen rekkefølge, et steg pekte på en del som ikke finnes, Esc ikke lukket, eller et nei ikke ble husket

**Avhenger av:** 8.9. **Én økt:** ja.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Hvor står knappen?** *Forslag:* ved siden av «Vis meg rundt» øverst, på de samme sidene, og skjult til skriptet er lastet, så den aldri står uten å virke. Med «Vis hjelp» av står den ikke, som «Vis meg rundt».
2. **Hvilken aksjeside?** *Forslag:* den første aksjen i tabellen på oversikten, som omvisningen leser når den går fra oversikten. I demoen er det BRFE. Min liste vises med «Alle», så tabellen har aksjer også uten stjerner.
3. **Hvordan huskes tilbudet første gang og et nei?** *Forslag:* i nettleseren (`localStorage`), ikke i basen, så det trengs ingen migrasjon, og storyen kan flettes når som helst. Tilbudet står øverst på oversikten til det er besvart, med «Spill av omvisningen» og «Nei takk», og begge svarene huskes. Hvor omvisningen er mellom sidene, står i `sessionStorage`. Alternativet er en rad i `innstilling`, som krever en ny migrasjon og fletting kl. 23:50–23:58; da gjelder svaret maskinen, ikke nettleseren.
4. **Skriptet.** *Forslag:* omvisningen ligger i `src/static/hjelp.js`, fordi testene krever at sidene bare har det ene skriptet. Stegene står som data i rammen (`<div id="omvisning" hidden>`), og logikken for neste steg og adressen er rene funksjoner som testene kjører med Node.
5. **Steget og boksen.** *Forslag:* en boks fast nederst til høyre med «Steg N av M», tittelen, teksten og knappene, som `role="dialog"` med `aria-modal="false"`, så siden kan leses og brukes under. Delen steget gjelder, får en oransje ramme og rulles fram. Er ankeret et tomt merke rett foran delen, som `noekkeltallene` fra 8.9, merkes delen etter. Fokus går til boksen, og tilbake dit det var når omvisningen lukkes.
6. **Et steg uten delen.** *Forslag:* hoppes over i samme retning, som når en side ikke viser sjekkene.
7. **Stegene.** *Forslag:* de samme som «Vis meg rundt» på sidene (`rundturer()`), i rekkefølgen sidene står, 21 steg i demoen. «Følg en aksje» er ikke med, fordi den ikke er i rekkefølgen i svaret.
8. **Bildene.** *Forslag:* bildene av stegene fra demoen står i PR-en, fra en egen gren med bare bildene (som for 8.17b). Bildene i `docs/appen/` tas på nytt, med tilbudet besvart, fordi knappen står øverst på sidene.

## Delene

### A) Knappen og rekkefølgen

**Ville feilet hvis:** knappen manglet ved «Vis meg rundt», lista fra 8.9 forsvant, eller sidene kom i en annen rekkefølge.

### B) Stegene, tastaturet og skjermleseren

**Ville feilet hvis:** et steg hadde en annen tekst enn «Vis meg rundt», pekte på en del som ikke finnes, manglet en av knappene, eller Esc, fokuset eller rollen ikke virket.

### C) Første gang

**Ville feilet hvis:** tilbudet kom på en annen side enn oversikten, manglet «Nei takk», eller svaret ikke ble husket, eller storyen trengte en migrasjon.

### D) Ingen råd, og lik i begge versjonene

**Ville feilet hvis:** en tekst ga råd eller sa noe om hva kursen vil gjøre, eller omvisningen var en annen i den ekte versjonen.
