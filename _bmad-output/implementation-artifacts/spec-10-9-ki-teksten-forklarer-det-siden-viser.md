---
title: 'Story 10.9: KI-teksten forklarer det siden viser, med promptversjon 5 og tre mønstre appen regner ut'
type: 'feature'
created: '2026-11-07'
status: 'draft'
route: 'dispatch'
baseline_commit: 'c411cc5d'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-2i-prompten-versjon-4.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-4-loggdelen.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-1-brukertesten.md'
  - '{project-root}/docs/kilder-og-rettigheter.md'
---

*Svar 2026-11-07 kl. 08:58 (gruppens svar):* forslagene i spørsmål 1–10 under er godtatt, med ordstillingen «minst siden ‹dato›» i spørsmål 2, ikke «siden minst ‹dato›» som i forslaget. Rådet anbefalte det. Svaret står også under story 10.9 i `epics.md`.

Utkast, skrevet 07.11 i instruksjonen kl. 00:20 (`docs/ai-prompts/2026-11-07.md`). Ingenting bygges før gruppen har svart på spørsmålene under (regel 9).

## Spørsmål til gruppen før noe bygges

Hvert spørsmål har et forslag. Forslaget er det utkastet under bygger på, til gruppen har svart.

1. **Hva er «signalet skiftet» i setningen om dagene?** Tellingen i dag er børsdager på rad med samme retning **og** styrke (`tell_dagene` i `src/dagene.py`, svaret 24.10 kl. 16:15 a). Mønster 3 i svaret kl. 22:05 teller skift i **retningen**. *Forslag:* datoen i setningen om dagene følger tellingen som står, retning og styrke, så setningen og antallet dager sier det samme. Mønster 3 teller bare retningen, som svaret sier.
2. **Hva står når datoen ikke er kjent?** Med «minst» (`dager_minst`) er dagen før rekka ikke lagret, så datoen signalet skiftet er ukjent. *Forslag:* «Signalet har vært slik siden minst ‹dato›.», med den første lagrede dagen i rekka, og ingen dato som om den var kjent.
3. **Hvordan teller mønster 1 en dag som er «ikke vurdert»?** *Forslag:* vinduet er de 20 børsdagene til og med dagen. Dager uten lagret vurdering, eller med en grunn, telles ikke med i noen retning, og setningen sier hvor mange dager som er vurdert: «Av de 14 vurderte børsdagene av de siste 20 var signalet positivt 6, …». Med færre enn 10 vurderte dager gis ikke mønsteret.
4. **Hvordan teller mønster 2 en dag der aksjen eller hovedindeksen var uendret, eller en dag med hull?** *Forslag:* som ordlyden om hovedindeksen i versjon 4 (`ordlyd_om_hovedindeksen` i `src/ki_prompt.py`, svaret 6.11 kl. 11:15, 2): en dag telles bare når aksjens forrige rad er forrige børsdag (`Dagsbilde.samme_periode`), og når både aksjen og hovedindeksen steg eller falt. Setningen sier hvor mange av de 5 dagene som kunne telles. Kunne færre enn 3 telles, gis ikke mønsteret.
5. **Hva er «den siste måneden» i mønster 3?** *Forslag:* som perioden «1 mnd» i `src/perioder.py`: fra samme dato én måned før, etter kalenderen. Et skift telles mellom to vurderte børsdager som følger rett etter hverandre. En dag som er «ikke vurdert» bryter rekka, og da sier setningen «minst».
6. **Hva betyr «hvor ofte» i mønster 1 og 2?** *Forslag:* antall, ikke prosent, fordi grunnlaget bare har fortegn, styrke, retning og antall (beslutningen 04.10). «6 av 14», aldri «43 %».
7. **Hvem skriver setningen om mønstrene: appen, modellen, eller begge?** Svaret kl. 20:38 sier at modellen forklarer mønstrene, og svaret kl. 22:05 sier at KI-teksten har én setning om dem. *Forslag:* appen lager tallene, og modellen får dem i grunnlaget og skriver én setning om dem. Kontrollen godtar bare de tallene (del F). Appen skriver ikke en egen setning om mønstrene, så siden ikke sier det samme to ganger.
8. **Hører boblen til investorsiden og bryteren fast øverst (svarene kl. 22:16 og 22:23) til denne storyen?** *Forslag:* rammen «Signalet forklart» med bryteren fast øverst til høyre bygges her (del C), fordi de står i samme ramme. Boblen nederst bygges med 3.4h, fordi lenken i demoen skal gå til siden der (svaret kl. 23:51).
9. **Hvordan klassifiseres tekstene i ny telling for 10.4?** Med versjon 5 forklarer hver tekst sjekkene, så «gjentar» i `spec-10-4-loggdelen.md` passer ikke lenger. *Forslag:* tre nye klasser: «forklarer sjekkene» (hver sjekk med vanlige ord), «forklarer mønstrene» (setningen om mønstrene er med og stemmer) og «usikker». Tellingen gjøres for de første fem kveldene med versjon 5.
10. **Gjelder 60 ord også den nye hjelpeteksten ved rammen?** Svaret kl. 23:07 gjelder hvert hjelpevindu på aksjesiden. Hjelpen for KI-delen i dag, `"ki_kort_fortalt"` i `src/hjelpetekster.py`, er 149 ord (telt med `\w+`, 07.11). *Forslag:* ja, og hjelpen sier bare hva teksten er, hva modellen fikk, og at tallene er sjekket. Resten står i `docs/hjelp.md`.

## Intent

**Problem:** KI-teksten forklarer ikke sjekkene. Den gjentar bare navnene på dem (gruppens gjennomgang 06.11 kl. 20:31, U82 i `docs/ux-logg.md`). Loggdelen av 10.4 fant det samme for versjon 3 (`spec-10-4-loggdelen.md`).

**Avgjørelsene** (under story 10.9 i `epics.md`):
- *06.11 kl. 20:35:* KI-teksten forklarer hver sjekk med vanlige ord, og setningen om dagene får datoen signalet skiftet.
- *06.11 kl. 20:38:* i tillegg mønstre som appen regner ut, bare om det som har skjedd, og som modellen forklarer. Modellen finner aldri mønstre selv.
- *06.11 kl. 22:05:* tre mønstre. Én setning per sjekk og én om mønstrene. Storyen bygges før UX-rettingene fra 06.11.
- *06.11 kl. 22:16 og 22:23:* rammen «Signalet forklart», med appens setninger først og bryteren fast øverst til høyre, både med KI på og av.
- *06.11 kl. 23:07* (under story 8.0c): hvert hjelpevindu på aksjesiden har høyst 60 ord.

**Målet:** aksjesiden forstås på første lesning, målt med del B i brukertesten (`docs/brukertest.md`).

## Slått opp 07.11 på `c411cc5d` (regel 3)

- **Setningen om dagene** lages av appen, ikke modellen (svaret 25.10 kl. 00:51): `setning_om_dagene` i `src/dagene.py`, kalt fra `src/app.py` med `tell_dagene`. Den sier antallet børsdager, ikke datoen. `tell_dagene` teller dager på rad med samme retning og styrke. En børsdag uten rad, eller en dag utenfor børskalenderen, gir «minst».
- **Grunnlaget** (`ki_grunnlag` i `src/ki_grunnlag.py`): fortegnet for de tre sjekkene, styrken og retningen, et merke for aksjer utenfor målingen, og med dagen `hovedindeksen` og `aksjen`. Bare heltall og tekst fra lukkede lister. `ANTALLENE` er bare `styrke`.
- **Prompten** (`src/ki_prompt.py`): `PROMPTVERSJON` er «4». Reglene beskriver sjekkene i én linje hver. Ordlyden om hovedindeksen gis som en hel setning av `ordlyd_om_hovedindeksen`, og bare når både aksjen og hovedindeksen steg eller falt over samme periode.
- **Hull i aksjens serie:** aksjen regnes som i tabellen, mot forrige rad, også på en dag med hull (svaret 6.11 kl. 09:55, 1). Hovedindeksen er med i grunnlaget bare når aksjens forrige rad er forrige børsdag (`samme_periode`, svaret 6.11 kl. 11:15, 2).
- **Kontrollen** (`kontroller` i `src/ki_kontroll.py`, FR-603): lovlige tall er de faste tallene i regelen (3, 50, 20 og 2) og antallene i grunnlaget. Den stopper alt om hovedindeksen utenom ordlyden, og alt om bransjen, børsen, markedet og antall aksjer, og «samme vei» og «motsatt vei» utenfor ordlyden. Dager stoppes i enhver form.
- **Visningen** (`src/templates/aksje.html`): delen heter «‹navn› kort fortalt» (svaret 04.11 kl. 22:23, 3), med «Laget av KI · ‹modellen›». Med KI av står bare bryteren, under setningene om dagene og samme dag.
- **Demoen:** tekstene ligger i `src/demo_ki_tekster.json`, laget med `uv run python src/demo_ki.py`, med promptens avtrykk på hver rad. Vurderingene i demoen starter `STARTDAG` 21.09 (`src/demo.py`).

## Delene

### A) Datoen signalet skiftet, i setningen om dagene

Setningen får datoen for den første dagen i rekka, i tillegg til antallet: for eksempel «Signalet har vært slik i 4 børsdager på rad, siden tirsdag 03.11.» Datoen vises som de andre datoene på siden. Med «minst» står forslaget i spørsmål 2. For en annen dag enn siste børsdag brukes formene med «Denne dagen». Appen skriver setningen, og modellen får ikke datoen.

**Ville feilet hvis:** datoen var dagen før rekka, eller sto som kjent når rekka er «minst». Da sier siden en dato signalet ikke skiftet.

### B) De tre mønstrene

Appen regner dem ut i en ren funksjon utenfor `ki_*` (som `dagene.py`), av de lagrede vurderingene og kursseriene. De regnes aldri bakover på nytt: de bygger på vurderinger som er lagret (AD-7).

1. **Retningen de siste 20 børsdagene:** hvor mange av de vurderte børsdagene i vinduet signalet var positivt, negativt, blandet og uten retning. En dag som er «ikke vurdert», teller ikke, og antallet vurderte dager står med (spørsmål 3).
2. **Samme vei som hovedindeksen de siste 5 børsdagene:** hvor mange av dagene aksjen og hovedindeksen begge steg eller begge falt. En dag med hull eller med en uendret side telles ikke, som ordlyden om hovedindeksen i versjon 4 (spørsmål 4).
3. **Skift i retningen den siste måneden:** hvor mange ganger retningen var en annen enn dagen før, mellom vurderte børsdager som følger rett etter hverandre (spørsmål 5).

Med færre dager lagret enn vinduet, som i de første ukene etter første henting og i demoen, regnes mønsteret av dagene som finnes, og antallet står. Under grensen i spørsmål 3 og 4 gis mønsteret ikke, og grunnlaget har ikke feltet.

**Ville feilet hvis:** en dag som er «ikke vurdert», ble talt som en retning, en dag med hull ble talt som samme vei, eller et mønster ble gitt med for få dager. Da sier teksten noe om dager signalet ikke har.

### C) Rammen «Signalet forklart»

Rammen erstatter «‹navn› kort fortalt» (svaret kl. 22:23). Øverst i rammen står appens setninger: setningen om dagene med datoen (del A) og setningen om samme dag. Så kommer KI-teksten med merket «Laget av KI», og modellnavnet står som FR-602 krever. Bryteren «KI-tekst» står fast øverst til høyre i rammen, både med KI på og av. Med KI av står rammen med appens setninger og bryteren, uten KI-tekst. Det endrer linja om at bare bryteren står med KI av (8.2b, «Rettet 04.11 kl. 00:48»), etter svaret kl. 22:23. Regelforklaringen står over, som før (FR-602).

**Ville feilet hvis:** bryteren byttet plass når KI slås av (U78), eller KI-teksten sto før appens setninger. Da flytter siden seg under den som leser.

### D) Hjelpeteksten ved rammen

Ett «?» ved tittelen. Høyst 60 ord, telt med `\w+` (svaret kl. 23:07). Den sier hva teksten er, at modellen bare fikk det appen har regnet ut, og at tallene er sjekket før teksten vises. `docs/hjelp.md` og README-en sier det samme (regel 19).

**Ville feilet hvis:** hjelpen hadde mer enn 60 ord, eller sa noe modellen ikke får. En test teller ordene i hver hjelpetekst på aksjesiden.

### E) Promptversjon 5

`PROMPTVERSJON` blir «5», fordi `ose.db` har tekster med versjon 4. Reglene ber om én setning per sjekk, i rekkefølgen trend, bevegelse og interesse, med vanlige ord. Grunnlaget, eller reglene, sier også hva hver sjekk måler, med regelens faste tall: trenden måler kursen mot snittet for de siste 50 børsdagene, bevegelsen dagens endring mot de siste 20 dagene, og interessen handelen mot det vanlige. Så kommer én setning om mønstrene, med tallene fra grunnlaget og uten å si hva som vil skje. Ordlyden om hovedindeksen står som i versjon 4. Alle andre regler står, også at teksten ikke gir råd og ikke gjetter på årsaker (NFR-06, FR-603). Avtrykket settes på nytt.

**Ville feilet hvis:** prompten fikk en annen tekst uten ny versjon, eller manglet linja om én setning per sjekk. Da kan to prompter se ut som én i loggen (FR-605).

### F) Kontrollen

Kontrollen godtar setningene om sjekkene der de stemmer med fortegnene, og setningen om mønstrene der hvert tall er et av tallene i mønstrene i grunnlaget. Antallene i mønstrene legges til `ANTALLENE`. Alt annet stoppes som før, også et mønster modellen finner selv: ord som «mønster», «tendens», «pleier», «gjentar seg» og «oftere» utenfor tallene i grunnlaget, og en sammenligning med hovedindeksen utenfor ordlyden og mønster 2. Et mønster leses som et varsel, nær en anbefaling (svaret kl. 20:38), så ord om hva som vil skje stoppes som før.

**Ville feilet hvis:** en tekst med et tall som ikke er i grunnlaget besto, eller en tekst som sa at aksjen «pleier» å gå opp, besto. Da finner modellen mønstre selv, og kontrollen kan ikke sjekke dem.

### G) Demoen og telling for 10.4

Demotekstene lages på nytt med Gemma (`uv run python src/demo_ki.py`), med versjon 5 og mønstrene for siste demodag. Demoen har vurderinger fra 21.09, så mønster 1 får færre enn 20 vurderte dager, og grensen i spørsmål 3 prøves. En tekst som ikke består kontrollen, vises ikke. Bildene i `docs/appen/` tas på nytt der avtrykkene krever det.

Ny telling for 10.4 etter de første kveldene med versjon 5, med klassene i spørsmål 9, i en ny del av `spec-10-4-loggdelen.md`.

**Ville feilet hvis:** en demotekst med versjon 4 sto igjen, eller tellingen brukte klassene fra versjon 3. Da måles noe annet enn det del B i brukertesten viser.

### H) Grunnlaget og rettighetene

- **Beslutningen 04.10** (`docs/kilder-og-rettigheter.md`, «Betingelse 4 og KI-tjenestene»): modellen får bare våre egne resultater, fortegn, styrke, retning og antall. Mønstrene er antall dager, regnet av våre lagrede vurderinger og av retningen aksjen og hovedindeksen gikk. Ingen kurs, prosent, volum eller forholdstall sendes. Det holder seg innenfor, med forslaget i spørsmål 6.
- **N2** i `sprint-change-proposal-2026-10-13.md` ville ha tall om utbyttet og om aksjen mot hovedindeksen, og krevde at beslutningen 04.10 ble tatt opp igjen. Denne storyen sender ikke utbytte eller prosenter, så den krever ikke det.
- **Godkjenningen fra EODHD** gjelder bare klassifisering av relevans for artikler (lagt til 06.10 i `docs/kilder-og-rettigheter.md`). Plan B sender ikke EODHDs innhold, og 04.10 ble det avgjort at vi ikke spør EODHD, fordi bare våre egne resultater sendes. Mønstrene endrer ikke det.

**Ville feilet hvis:** grunnlaget fikk et desimaltall, en prosent eller en kurs. En test krever heltall og tekst fra lukkede lister, som i dag.

## Grenser

- Ingen kall til EODHD utover kvotesjekken i regel 15. `data/db/ose.db` leses bare, med `mode=ro` (regel 22). Demobaser bare i midlertidige mapper.
- Ingen tekst fra den ekte versjonen ordrett i sporede filer (regel 16).
- Bygges på egen gren og flettes bare ferdig og grønn, før UX-rettingene fra 06.11 (svaret kl. 22:05).
- En mutant per del, med kopi før og sha256 mot HEAD etter.
