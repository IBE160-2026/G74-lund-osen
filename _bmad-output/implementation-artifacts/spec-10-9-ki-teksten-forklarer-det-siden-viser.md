---
title: 'Story 10.9: KI-teksten forklarer det siden viser, med promptversjon 5 og tre mønstre appen regner ut'
type: 'feature'
created: '2026-11-07'
status: 'done'
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

## Bygget 07.11 (instruksjonen kl. 10:38)

Bygget på grenen `10-9-ki-teksten-forklarer-det-siden-viser`, i worktreen `G74-lund-osen-10-9`, fra `7c55913d`. Koden er i `ba685331`. Ingen migrasjon: grunnlaget lagres som et JSON-objekt (`0005_ki_logg.sql`), og mønstrene regnes av lagrede rader.

**Slått opp 07.11, og avvik fra delene over:**
- *Del E, grunnen til versjon 5.* Delen sier at `ose.db` har tekster med versjon 4. Det stemmer ikke: `ki_logg` hadde bare `promptversjon` 3 til og med 06.11 (lest med `mode=ro` 07.11), og de første med versjon 4 kommer med hentingen 09.11 (Utført-linja kl. 00:27 07.11). Versjonen er likevel 5, fordi versjon 4 er flettet, og fra 26.10 gir enhver endring i prompten en ny versjon (svaret 25.10 kl. 20:54 b, i `ki_prompt.py`). Docstringen sier det.
- *Del E, formene for sjekkene.* Prompten gir én form per sjekk og fortegn, med «fordi» etter utslaget, som regelen fra versjon 2. Den første versjonen ga ett eksempel med «så», og 4 av 13 demotekster ble stoppet fordi Gemma skrev begge (§56 i `malinger.md`).
- *Del F, målingen.* Kontrollen leser også ordene om målingen («kursen ligger over snittet», «det ble ikke handlet mye mer enn vanlig») mot fortegnet (`_maalingene`). To demotekster i den første kjøringen besto med feil om handelen.
- *Del F, mønstrene.* Formene i prompten leses med tallet ved feltet sitt, ikke bare som «et av tallene i mønstrene», og tas ut av teksten før resten av kontrollen leser den. Antallene er i `ANTALLENE`, som delen sier. Vinduet 5 er lovlig bare når grunnlaget har mønster 2, og et feltnavn eller en plassholder fra prompten i teksten stoppes.
- *Del D.* Hjelpen er tre setninger og 60 ord med tittelen, telt med `\w+`. Nøkkelen er `signalet_forklart` i stedet for `ki_kort_fortalt`. At teksten ikke gir råd, står i `docs/hjelp.md` (spørsmål 10).
- *Spørsmål 16 i 8.20* sier at de fete navnene på sjekkene i KI-teksten hører til 10.9. Denne spesifikasjonen har dem ikke, og de er ikke bygget. Spørsmål til gruppen under.
- *Testnavn.* `test_ki_delen_heter_navnet_kort_fortalt` og `test_med_ki_av_staar_bare_bryteren` har fått nytt innhold etter del C, men navnet står, fordi `docs/kvalitetssikring.md` og spesifikasjonen 8.2b viser til det første.

**Tester («Ville feilet hvis» i hver):** del A i `tests/test_ki_visning.py` (`TestSetningenOmDagene`, med `test_foerste_dag_i_rekka` og `test_aaret_staar_naar_datoen_er_fra_et_annet_aar`), delene B–H i den nye `tests/test_ki_teksten_forklarer.py`. Testen for 60 ord gjelder vinduet ved rammen; de andre vinduene rettes i 8.20a.

**Hele settet,** alene og uten Ollama: kl. 11:14:27–11:24:19, 4295 bestått, 24 hoppet over, 7 feilet: 3 porttester for `start.ps1` og 4 som ventet den gamle rammen (`test_demoproeven.py`, `test_funnene_8_2b.py` to, og navnet i `test_kvalitetssikring.py`). De ble rettet, og settet kjørt på nytt kl. 11:25:27–11:35:29: 4297 bestått, 24 hoppet over, og bare 5 porttester for `start.ps1` feilet.

## Mutantene

Én per del, på `ba685331`, med kopi før og sha256 mot HEAD etter. Alle åtte ble fanget, og hver fil var lik HEAD etterpå.

| Del | Mutant | Fanget av |
|---|---|---|
| A | `foerste_dag_i_rekka` går én børsdag for langt tilbake | 7 tester i `test_ki_visning.py` |
| B | en dag med hull telles i mønster 2 | `test_en_dag_med_hull_telles_ikke` |
| C | appens setninger tatt ut av rammen | 23 tester |
| D | hjelpen ved rammen får en setning til | `test_hjelpen_ved_rammen_har_hoeyst_60_ord` |
| E | linja om én setning per sjekk tatt ut av prompten | 3 tester, også `test_versjonen_foelger_teksten` |
| F | tallet ved feltet sjekkes ikke i mønster 1 | 2 tester i `TestKontrollen` |
| G | demotekstene med versjon 4 tilbake | `test_demotekstene_har_versjon_5_og_moenstrene` |
| H | grunnlaget kontrollerer ikke mønstrene | 6 tester i `TestGrunnlaget` |

## Demotekstene før og etter

Laget på nytt med Gemma kl. 11:03 (13 av 13 besto). Tre av de 13, fra `src/demo_ki_tekster.json` (oppdiktede selskaper):

- **BRFE** (alle tre negative). Før: «Signalet er Negativt fordi trenden ga et negativt utslag, bevegelsen ga et negativt utslag, og interessen ga et negativt utslag. Aksjen gikk samme vei som hovedindeksen.» Etter: «Trenden ga et negativt utslag fordi kursen ligger under snittet for de siste 50 børsdagene. Bevegelsen ga et negativt utslag fordi kursen falt mer i dag enn den vanligvis svinger de siste 20 dagene. Interessen ga et negativt utslag fordi det ble handlet mer enn vanlig på en dag kursen falt. Aksjen gikk samme vei som hovedindeksen. Av de 15 vurderte børsdagene var signalet positivt 10, negativt 2, blandet 2 og uten retning 1. Aksjen gikk samme vei som hovedindeksen 2 av de 5 dagene som kunne telles av de siste 5 børsdagene, og den siste måneden skiftet retningen minst 5 ganger.»
- **SLVP** (retningen Ingen). Før: «Signalet har ingen retning fordi trenden ikke ga utslag, bevegelsen ikke ga utslag og interessen ikke ga utslag. Aksjen gikk motsatt vei av hovedindeksen.» Etter: «Trenden ga ikke utslag fordi kursen ligger nær snittet for de siste 50 børsdagene. Bevegelsen ga ikke utslag fordi dagens endring ikke var stor sammenlignet med de siste 20 dagene. Interessen ga ikke utslag fordi det ikke ble handlet mye mer enn vanlig. Signalet har ingen retning. Av de 15 vurderte børsdagene var signalet positivt 3, negativt 9, blandet 1 og uten retning 2. Aksjen gikk samme vei som hovedindeksen 3 av de 5 dagene som kunne telles av de siste 5 børsdagene, og den siste måneden skiftet retningen minst 8 ganger.»
- **KVST** (alle tre positive). Før: «Signalet er Positivt fordi trenden ga et positivt utslag, bevegelsen ga et positivt utslag, og interessen ga et positivt utslag. Aksjen gikk motsatt vei av hovedindeksen.» Etter: «Trenden ga et positivt utslag fordi kursen ligger over snittet for de siste 50 børsdagene. Bevegelsen ga et positivt utslag fordi kursen steg mer i dag enn den vanligvis svinger de siste 20 dagene. Interessen ga et positivt utslag fordi det ble handlet mer enn vanlig på en dag kursen steg. Aksjen gikk motsatt vei av hovedindeksen. Av de 15 vurderte børsdagene var signalet positivt 3, negativt 5, blandet 1 og uten retning 6, aksjen gikk samme vei som hovedindeksen 1 av de 4 dagene som kunne telles av de siste 5 børsdagene, og den siste måneden skiftet retningen minst 11 ganger.»

I demoen er alle mønster 3 «minst», fordi måneden før 09.10 begynner før vurderingene i demoen (21.09).

**Bildet** av aksjesiden i `docs/appen/` er tatt på nytt, 1280 × 2345, til bunnen av rammen. De seks andre bildene ble tatt på nytt og er byte for byte de samme. Bildene ble tatt med DevTools-protokollen i Edge uten vindu (`Page.captureScreenshot`), som ga de seks byte for byte like.

**Prøvekjøringen** står i §56 i `malinger.md`: 15 av 15 besto, alle med alle tre mønstrene.

## Gjennomgangen 07.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Tre gjennomganger av `ba685331` og `f3729e38`, kjørt i parallell etter hele settet: Blind Hunter med bare diffen, Edge Case Hunter og Verification Gap med repoet. Edge Case Hunter og Verification Gap kjørte snutter og enkeltfiler, ikke hele settet. Rettingene er i `c7159bb9`. Hvert eksempel fra gjennomgangene er prøvd på nytt med `kontroller` etter rettingen, og tekstene fra prøvekjøringen (15) og demoen (13) består fortsatt.

**Høy**
- *ECH1, ECH2, ECH3 og BH3, rettet.* Mønsterformene ble tatt ut overalt i teksten, før retnings-, dag- og månedskontrollen leste den. Da besto «Signalet er positivt i to av tre sjekker.» med retningen Negativ, og «… de siste 20 børsdagene» og «… den siste måneden» besto, selv om de ble stoppet før 10.9. Nå leses formene bare i setningen om mønstrene, som kjennes igjen på en hel form (`_ANKRENE`). Andre setninger leses som før.
- *BH2 og ECH5, rettet.* Tellingene lå i `ANTALLENE`, som del F sa, og var dermed lovlige tall hvor som helst. «Kursen ligger 14 over snittet.» besto. Nå er tellingene ikke i `ANTALLENE`, og de leses bare i formene, ved feltet sitt. Det er et avvik fra del F (spørsmål 2 under).
- *BH1 og ECH8, rettet.* «Kursen steg ikke mer …» ble lest som at kursen steg mer. Nå leses «ikke».
- *VG1, rettet.* Ingen test viste at ordene om målingen stoppes når de strider mot fortegnet. Det gjør `TestMaalingen` nå.

**Middels**
- *ECH4, ECH6, ECH12 og VG3, rettet.* I setningen om mønstrene besto byttede tall foran ordet, sammenligninger som «oftest positivt» og «færre enn», og «Det stemmer ikke at …». Nå kan resten av den setningen bare være bindeordene «av», «de», «siste», «var», «signalet» og «og». Alt annet stoppes (`_BINDEORD`).
- *ECH7, rettet.* Formen for skiftene ble godtatt uten «den siste måneden». Nå kreves den.
- *BH4 og VG3, rettet.* Ordlista for mønstre modellen finner selv har fått «mønstre», «pleide», «gjentok seg», «oftest», «ofte», «hyppig», «stort sett», «for det meste» og «vanligvis positivt».
- *BH5 og BH6, rettet.* «Kursen ligger ikke nær snittet» og «Dagens endring var ikke liten» ble lest med feil fortegn.
- *BH7, rettet.* To linjer i prompten sa «under teksten», men appens setninger står nå over. Versjonen står som 5, fordi versjon 5 ikke er flettet og ingen tekst i `ose.db` har versjon 5, som i 10.2i. Avtrykket er `822dcd49…8dea`.
- *VG2, VG5 og VG8, rettet.* Det mangler ikke lenger tester for tallet i mønster 3, for at en endring i styrken ikke er et skift (spørsmål 1), eller for en uendret eller manglende hovedindeks i mønster 2.
- *VG4, åpent.* Hjelpen og del E sier «én setning om mønstrene». Kontrollen sjekker ikke antallet setninger. 6 av 13 demotekster deler mønstrene i to setninger, mens ingen av de 15 i prøvekjøringen gjør det. Spørsmål 1 under. Står åpent til gruppen har svart (regel 25).
- *VG4, lukket 2026-11-07 etter gruppens svar kl. 12:32 (regel 25).* Svar 1: kontrollen stopper ikke en tekst som deler mønstrene i to setninger. Prompten ber fortsatt om én, og hjelpen sier nå «en setning eller to» (`docs/hjelp.md`). README-en sier ikke hvor mange setninger teksten har, og er ikke endret.
- *VG6, avvist.* Funnet var at `_grunnlagene` bare var testet med mønster 2. Men `test_grunnlaget_stemmer_med_demodagen` sammenligner demoradene, som lages gjennom `_grunnlagene` i `lag_tekstene`, med `lag_moenstrene` for alle tre mønstrene. Mutant G viser at testen leser fila.

**Lav**
- *Rettet:* ECH9 («over eller under» sier ingenting om fortegnet), ECH10 («minst» foran verbet), ECH11 (markdown med `__`), BH10 og VG7 (formen uten mønsteret i grunnlaget), BH11 (høyst 22 skift, og feilmeldingen) og BH12 (docstringen i `test_versjon_4`). VG11 er rettet delvis: med KI av sjekkes også `p.samme-dag`. At bryteren står til høyre, avgjøres av CSS-en og er ikke testet; det godtas som lavt.
- *Avvist:* BH8, fordi lørdag 31.10 i testene kommer fra testdataene, og vurderinger skrives bare for børsdager. BH9, fordi Verification Gap telte vinduet med testens egen splitt og fikk tittelen og teksten, 60 ord.
- *Ført:* BH13. Porttestene for `start.ps1` feilet 3, 5 og 6 ganger i de tre kjøringene av settet. De er ustabile, men de er de eneste som feilet. VG9: testen for 60 ord gjelder vinduet ved rammen, etter instruksjonen kl. 10:38, og de andre vinduene rettes i 8.20a. VG10: tellingen for 10.4 med klassene i spørsmål 9 gjøres etter de første fem kveldene med versjon 5, og står som åpent punkt i `issues.md`.

**Etter rettingen:** hele settet ble kjørt alene kl. 11:55:32–12:06:37: 4330 bestått, 24 hoppet over, og bare 6 porttester for `start.ps1` feilet. Demotekstene og prøvekjøringen ble laget på nytt med avtrykket over (§56). Bildene ble tatt på nytt og er byte for byte de samme, og bare avtrykkene i `tests/test_docker.py` er endret. Mutantene ble kjørt på nytt på `c7159bb9`, med F oppdatert til den nye koden og F2 for bindeordene, «setningen om mønstrene sier mer enn formene»: alle ni ble fanget, med A 7, B 1, C 23, D 1, E 3, F 2, F2 4, G 1 og H 6 tester, og hver fil var lik HEAD etterpå.

## Spørsmål til gruppen før flettingen

*Svar 2026-11-07 kl. 12:32 (gruppens svar):* forslagene i spørsmål 1–4 under er godtatt: 1) kontrollen stopper ikke en tekst som deler mønstrene i to setninger; prompten ber fortsatt om én, og hjelpen sier «en setning eller to» (VG4); 2) tellingene godtas bare i formene, ved feltet sitt, ikke i `ANTALLENE` (BH2, ECH5); 3) de faste formene for sjekkene står til tellingen for 10.4 etter fem kvelder med versjon 5, og tas opp igjen da; 4) de fete navnene på sjekkene bygges i 8.20a. Rådet anbefalte alle fire. Svaret er ført etter instruksjonen kl. 12:47 i `docs/ai-prompts/2026-11-07.md`.

1. **VG4: én setning om mønstrene.** Skal kontrollen stoppe en tekst som deler mønstrene i to setninger? *Forslag:* nei. Kontrollen sjekker hver setning med en form for seg, så to setninger sier ikke mer enn én. Prompten ber fortsatt om én, og «én setning» i hjelpen endres til «en setning eller to». Med ja blir 6 av 13 demotekster stoppet slik de er nå.
2. **BH2 og ECH5: tellingene i `ANTALLENE`.** Del F sa at antallene legges til `ANTALLENE`. Det gjorde tellingene til lovlige tall hvor som helst i teksten. *Forslag:* godta avviket. Tellingene leses bare i formene, ved feltet sitt.
3. **Formene for sjekkene.** Prompten gir én fast form per sjekk og fortegn, fordi én form med «så» ga 4 av 13 stoppede tekster og to feil om handelen (§56). Tekstene blir derfor nesten like for aksjer med de samme fortegnene, og det nye ligger i mønstrene. *Forslag:* behold formene til tellingen for 10.4 etter fem kvelder, og ta det opp igjen da.
4. **Spørsmål 16 i 8.20: de fete navnene på sjekkene i KI-teksten.** Spørsmålet sier at de hører til 10.9, men spesifikasjonen for 10.9 har dem ikke. *Forslag:* bygg dem i 8.20a, med resten av utseendet på aksjesiden.
