---
title: 'Story 8.21: Egne notater på aksjesiden'
type: 'feature'
created: '2026-11-10'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '53ff012c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md'
---

Skrevet 10.11 i instruksjonen kl. 16:08, etter gruppens svar kl. 14:32. Instruksjonen lagres i `docs/ai-prompts/2026-11-10.md` etter flettingen (steg 3), og storyen og svaret kl. 14:32 føres da i `epics.md`. Svaret kl. 14:32 står ikke i repoet ennå; det som står her om det, er hentet fra instruksjonen. Gruppen har sagt at Claude Code bygger etter forslagene i spesifikasjonene, og at de gås gjennom før flettingen (svaret 08.11 kl. 12:32).

## Storyen

Som **bruker**, vil jeg skrive et kort notat på aksjesiden og senere se hvordan det gikk etterpå, så jeg kan lære av det jeg selv tenkte, uten at appen sier hva som var riktig.

**Oppfyller:** svaret 10.11 kl. 14:32 · **Begrenses av:** NFR-06, NFR-08, `AD-3`, `AD-7`, `AD-10`, `AD-16`

**Kontroll — hva testen ser etter:**
- Brukeren skriver et kort notat på aksjesiden. Notatet får dagen siden viser: siste børsdag, eller dagen fra «Vis dagen»
- Under hvert notat står hvordan det gikk etterpå: endringen i aksjen og i hovedindeksen fra notatdagen til siste dag med kurser, og signalet som er lagret for de dagene
- Bare fakta: appen sier aldri om noe var riktig eller galt, og gir ingen råd (NFR-06)
- Notatene kan slettes, og lagres i en ny tabell med egen migrasjon (`AD-16`). Webserveren er eneste skriver av tabellen, som for Min liste, ønskene og innstillingene
- Notatene virker i demoen og i den ekte versjonen
- Ingen API-kall (`AD-10`)
- **Ville feilet hvis:** et notat fikk en annen dag enn siden viste, «etterpå» regnet signalet på nytt i stedet for å lese det som er lagret, eller siden brukte et ord som «riktig», «galt», «kjøp» eller «selg» om et notat

**Avhenger av:** 2.7b for siden for dagen, 8.16b for «Vis dagen», 8.17b for endringen fra en dag til siste børsdag. **Én økt:** ja.

## Svaret kl. 14:32, slik instruksjonen gjengir det

Egne notater på aksjesiden bygges i dag og flettes i natt kl. 23:50–23:58, fordi de trenger en ny tabell. Rådet anbefalte onsdag, men gruppen valgte i natt. Nettsiden får også skrive notatene til basen, som ønskene og innstillingene, og det utvider svaret 09.11 kl. 10:23; rådet anbefalte det.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Hvor står notatene?** *Forslag:* en egen del, «Mine notater», nederst på aksjesiden, under «Signalet dag for dag» og over boblen til investorsiden. Skjemaet for et nytt notat står øverst i delen, og notatene under, med den nyeste notatdagen først.
2. **Hvor kort er kort?** *Forslag:* høyst 280 tegn. Et tomt notat, eller et notat med bare mellomrom, lagres ikke. Mellomrom før og etter tas bort, og linjeskift blir mellomrom, så notatet er ett avsnitt.
3. **Hvilken dag får notatet?** *Forslag:* dagen siden viser, og den kan ikke velges for seg. Ved «Siste børsdag» og periodene er det siste dag med kurser for aksjen, og ved «Vis dagen» den valgte dagen. Skjemaet sier dagen: «Notatet får datoen <dag>.» Flere notater samme dag er lov.
4. **Hva står under «Etterpå»?** *Forslag:* én linje med endringen i aksjen og én med endringen i hovedindeksen, fra sluttkursen på notatdagen til siste dag med kurser for aksjen, på justert kurs (FR-101), regnet som «Sammenlign siste børsdag med» i Min liste (8.17b). Så signalet som er lagret for notatdagen og for den siste dagen, med pillen, brikkene og «N av 3» som i «Signalet dag for dag». Signalet leses fra `vurdering` og regnes aldri (`AD-7`). Mangler en kurs eller en vurdering, står «–» med grunnen (NFR-08).
5. **Og når notatdagen er den siste dagen?** *Forslag:* «Ingen børsdager med kurs etter notatdagen ennå.», og signalet for notatdagen.
6. **Hvilke ord?** *Forslag:* bare tall og datoer, med overskriften «Etterpå» og linjene «Aksjen fra <dag> til <dag>: +x %», «Hovedindeksen (<symbol>) samme dager: +y %» og «Signalet <dag>: …». Ingen ord som sier at notatet traff eller bommet, og ingen råd. En test leser siden etter ordene «riktig», «galt», «feil», «traff», «bom», «kjøp», «selg» og «bør» i delen.
7. **Slette.** *Forslag:* knappen «Slett» ved hvert notat sletter raden straks, uten å spørre først, fordi skjemaet virker uten skript. Notatene er ikke et uerstattelig lager som `vurdering` (`AD-7`), som merkingen i Min liste. Et notat kan ikke endres; det slettes og skrives på nytt.
8. **Tabellen.** *Forslag:* `notat` i `0012_notat.sql`, med `id`, `symbol`, `dato`, `tekst` og `laget`. En trigger avviser et symbol som ikke står i `aksje`, som for `min_liste` (0007). `CHECK` holder teksten mellom 1 og 280 tegn og datoen på formen ÅÅÅÅ-MM-DD. Porten heter `Notatlager` (`src/notater.py`) med `MinneNotatlager` og `SqliteNotatlager` i `lagring_sqlite.py`, etter navneregelen (`AD-3`).
9. **Demoen.** *Forslag:* notatene virker i demoen og lagres i demobasen, som merkingen i Min liste. Demokommandoen skriver ingen notater. En demobase fra før 0012 vises ikke, og sidene ber om at den lages på nytt, som etter 0011.
10. **En aksje som er tatt ut av lista.** *Forslag:* notatene står fortsatt på siden for aksjen, og kan slettes, men det kan ikke skrives nye, fordi aksjen ikke har kurser etter at den gikk ut.
11. **Hjelpen.** *Forslag:* ingen «?»-knapp. Én kort linje under overskriften: «Notatene lagres på denne maskinen. Under hvert notat står hva aksjen, hovedindeksen og signalet gjorde etterpå.» `docs/hjelp.md` får «Hva er «Mine notater»?».
12. **Rekkefølgen i natt.** *Forslag:* 0012 er neste ledige nummer, og ingen av grenene for 2.4, 2.6, 8.7 og 8.9 har en ny migrasjon. 8.21 flettes kl. 23:50–23:58, etter de fire som flettes i dag.

## Delene

### A) Tabellen `notat` (`0012_notat.sql`) og porten `Notatlager`

`id`, `symbol`, `dato`, `tekst` og `laget`. Triggeren mot `aksje` og `CHECK` fra spørsmål 8. Porten har `notater(symbol)`, `skriv(symbol, dato, tekst)` og `slett(symbol, id)`.

**Ville feilet hvis:** et notat ikke overlevde en omstart, tabellen godtok et ukjent symbol, en tom tekst eller over 280 tegn, eller `slett` kunne slette et notat for en annen aksje.

### B) Skjemaet og slettingen på aksjesiden

`POST /aksje/<symbol>/notat` lagrer et notat med dagen siden viste, og `POST /aksje/<symbol>/notat/slett` sletter ett. Begge sender tilbake til samme side og samme dag (303) med ankeret `#mine-notater`. Kommer forespørselen med Origin, må den være denne siden, som bryteren og stjernen. Webserveren skriver bare tabellen `notat` her (`AD-3`), og henter aldri noe (`AD-10`).

**Ville feilet hvis:** notatet fikk en annen dag enn siden viste, en dag uten kurs for aksjen ble godtatt, en annen side kunne skrive eller slette, eller en GET endret noe.

### C) «Etterpå» under hvert notat

Endringen i aksjen og hovedindeksen fra notatdagen til siste dag med kurser, og signalet som er lagret for de to dagene (spørsmål 4–6).

**Ville feilet hvis:** endringen var regnet på en annen kurs enn den justerte, signalet ble regnet på nytt, eller delen brukte et av ordene i spørsmål 6.

### D) Demoen, README-en og hjelpen

Notatene virker i demoen. README-en sier at aksjesiden har «Mine notater», og `docs/hjelp.md` har «Hva er «Mine notater»?» (regel 19). Bildene i `docs/appen/` tas på nytt når sidene de viser, er endret.

**Ville feilet hvis:** et notat i demoen ikke ble lagret, eller README-en eller hjelpen ikke nevnte notatene.
