---
title: 'Story 8.11: Ferdige lister og filter på signalet'
type: 'feature'
created: '2026-11-08'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'f09e0c6f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/planning-artifacts/designutdrag-2026-11-08.md'
---

Skrevet 08.11 i instruksjonen kl. 14:05 (`docs/ai-prompts/2026-11-08.md`): «8.11: en liste per bransje med de opptil 18 med høyest omsetning etter målingen (2.13), bare målte aksjer. Bransjen for hver aksje er ditt forslag, merket slik i spesifikasjonen, til gruppen har sjekket den.» Gruppen har sagt at Claude Code bygger etter forslagene i spesifikasjonene, og at de gås gjennom før flettingen (svaret 08.11 kl. 12:32). Storyen ble avgjort bygget i dag (svaret kl. 12:46, ført under storyen i `epics.md`). Utdraget 08.11 §2 sier at ferdige lister per bransje er 8.11 og ikke var med i 2.12.

Bygger på grenen for 2.12 (`2-12-velge-og-bytte-aksjer`, `f09e0c6f`), fordi «Bruk denne lista» skriver ønskene fra 2.12.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Bransjen for hver aksje (FORSLAG, IKKE SJEKKET).** *Forslag:* `BRANSJE` i `src/ferdige_lister.py`, laget av Claude Code 08.11 ut fra navnet i lista over Oslo Børs og det som er kjent om selskapet, for de 88 aksjene som har en måling med tall i `omsetning` i `data/db/ose.db` (lest med `mode=ro`, sha256 lik før og etter). De 11 merket `# usikker` er de vi vet minst om: LOKO, VOIM, OCEAN, PLGC, PLCAN, NTG, POLAR, LUMI, ININ, NOSN og HYN. **Gruppen må sjekke hver av dem før flettingen**, for eksempel mot ICB-bransjen hos Euronext. Ingen tall fra målingen står i koden (regel 16).
2. **Hva «Bruk denne lista» gjør.** *Forslag:* den ferdige lista blir lista ved neste henting. Hver aksje i lista som ikke er med, får et ønske om å fjernes, hver ny et ønske om å følges, og ønskene som venter, slettes (de er ikke tatt i bruk). Alt i én transaksjon med skrivelås, så lista aldri får mer enn 18. Ingenting hentes (AD-10), og bare `oenske` skrives (AD-3).
3. **Hvilke aksjer er «målt».** *Forslag:* den siste målingen i `omsetning` (2.13) har et tall, og koden står i `boersliste`. De 15 i lista er målt i `malinger.md`, men ikke i tabellen, så de står ikke i de ferdige listene før kommandoen fra 2.13 har målt dem. En aksje under 32 MNOK er med, med merket «Utenfor målingen», som i 2.12.
4. **Rekkefølgen.** *Forslag:* bransjene i rekkefølgen fra `designregler.md` §4, og i hver liste høyest median omsetning først. Den regnes når siden vises, så en ny måling gir nye lister.
5. **Filteret.** *Forslag:* «Alle», «3 av 3 positiv» og «3 av 3 negativ» over tabellen på oversikten og i Min liste (`?signal=`). Bare aksjene med 3 av 3 i den retningen, etter at radene er delt eller sortert, så rekkefølgen er FR-102. Bare blant aksjene siden viser (i Min liste de merkede). Teksten sier at filteret ikke er et råd. Andre lenker på siden (sortering, perioder) tar ikke med filteret.
6. **Demoen.** *Forslag:* de to målte demoselskapene får bransje (HVLK Kraft, NRDE Eiendom), så demoen viser to ferdige lister. Demoen henter aldri, så valget står som «Venter på henting».

## Intent

**Problem:** den som vil følge andre aksjer, må sette sammen lista selv, og kan ikke se bare aksjene med 3 av 3.

**Avgjørelsene:** story 8.11 i `epics.md`, FR-108, FR-412 (tillegget), og instruksjonen kl. 14:05.

## Delene

### A) De ferdige listene, ett sted i koden

`src/ferdige_lister.py`: `BRANSJE` og `lister()`. Aldri mer enn 18, bare målte.

**Ville feilet hvis:** en ferdig liste hadde 19 aksjer, eller en aksje som ikke er målt.

### B) «Bruk denne lista»

`Valglager.bruk_liste` og ruta `POST /ferdig-liste`, med Origin-sjekken fra 2.12.

**Ville feilet hvis:** lista kunne få mer enn 18, eller ruta skrev noe annet enn ønsker.

### C) Filteret

`?signal=positiv|negativ` på `/` og `/min-liste`.

**Ville feilet hvis:** filteret kunne leses som et råd, viste noe annet enn 3 av 3 i retningen, eller endret rekkefølgen.

### D) Hjelpen, `docs/hjelp.md`, README-en og demoen

«Hva er de ferdige listene og filteret?» i `docs/hjelp.md`, bildeteksten i README-en og bildet av «Din egen liste» (regel 19).
- **Hele settet alene:** først 2 feilet (to tester kjente ikke filterlenkene, som beholder resten av adressen), så kl. 20:51:24–21:01:51: 4658 bestått, 24 hoppet over og 0 feilet.

## Mutantene

På `713a5fd6` fem: A (en ferdig liste får 19) 1, B (en aksje målt med feil er med) 1, C (`bruk_liste` skriver ikke fjern) 1 og D (filteret slipper inn 2 av 3) 2 tester. E (filteret uten teksten om råd) OVERLEVDE, fordi testen bare så etter en del av setningen, som også står et annet sted på siden. Testen sjekker nå hele setningen. Hver fil var lik HEAD etterpå.

## Gjennomgangen 08.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Blind Hunter med bare diffen, og Edge Case Hunter og Verification Gap i samme agent, med repoet. Blind Hunter hadde 15 funn, Edge Case Hunter 11 og Verification Gap 11.

**Høy, rettet**
- *ECH1, VG1:* filteret endret overskriften og innledningen: «1 av 15 aksjer skilte seg ut» med filteret, mot 7 uten. Nå regnes overskriften, innledningen og om tabellen vises, av lista før filteret (`test_overskriften_endres_ikke_av_filteret`).
- *VG2:* at filteret bare virker innenfor lista som vises, var ikke dekket, fordi begge med 3 av 3 i demoen er merket. Nå prøves det med de merkede tatt bort (`test_min_liste_viser_bare_de_merkede`).

**Middels**
- *Rettet:* ECH2 og VG8 (Min liste sa «Ingen aksjer i Min liste ennå» med et filter ingen passet), ECH3 (med «Velg dag» kunne tabellen forsvinne uten forklaring; nå står «Ingen av aksjene her fikk det.» når filteret ikke gir noen rader), BH3 og ECH4 (over knappen står nå hvor mange aksjer som fjernes, og hjelpen sier at også de 15 fjernes), BH4 og ECH11 (hjelpen sa «Appen foreslår aldri hvilke aksjer du bør følge»; nå sier den at listene er ordnet etter omsetning og ikke er et råd, og forbeholdet står under filterknappene før et klikk), VG3 (siste måling og bare `boersliste`), VG4 (`test_filteret_med_sortering`), VG5 (ønskene etter POST sjekkes), VG7 (knappene, `aria-current` og adressen), BH9.
- *Ikke reelle:* BH1 (hentingen kan ikke gi 19, fordi `ta_i_bruk` sjekker taket når hver aksje tas inn og avviser ønsket), BH2 (`_laas()` ruller tilbake ved unntak; ECH prøvde det), BH5 (bildet er nytt; diffen var uten `docs/appen`).
- *Ført:* VG6 (valideringen i `bruk_liste` for duplikater, bransje og `boersliste` prøves bare gjennom ruta).

**Lav, ført:** BH6 og ECH8 (hver aksje rangeres etter sin egen siste måling), BH7 (duplikater kan ikke oppstå: begge tabellene har primærnøkkel), BH8 og ECH5 (lista regnes på nytt ved POST), BH10 og ECH10 (filteret forsvinner ved sortering og perioder; hjelpen sier det nå), BH11 (rettet: «med retning positiv»), BH12 (`assert` i modulen, demokodene i samme ordbok, og NORSE og HKY som Forbruk; gruppen sjekker bransjene, spørsmål 1), BH13, BH14, BH15 (Origin som de andre skjemaene), ECH6, ECH7 (bransjen fra den ferdige lista erstatter et ventende valg), ECH9, VG9, VG10 (rettet: demoen har Kraft og Eiendom), VG11.
- **Etter gjennomgangen:** hele settet alene kl. 21:19:15–21:29:21: 4664 bestått, 24 hoppet over og 0 feilet. Bildene av oversikten, Min liste, oversikten ved 390 px og «Din egen liste» er tatt på nytt.
- **Mutantene på nytt** på `48f4b3e3`, med F «overskriften regnes etter filteret» og G «Min liste viser alle med 3 av 3»: A 1, B 2, C 2, D 2, E 2, F 1 og G 1 test. Alle sju ble fanget, og hver fil var lik HEAD etterpå.

## Bygget og ikke flettet

Grenen `8-11-ferdige-lister` er ikke flettet. Den bygger på 2.12 (PR #124) og flettes etter den. Gruppen må sjekke bransjene i `BRANSJE` først (spørsmål 1).

*Svar 2026-11-08 kl. 22:01, 22:03 og 22:06 (gruppens svar):* bransjen Claude Code foreslo for hver av de 88 aksjene er godtatt (spørsmål 1, kl. 22:01). Kl. 22:03 tok gruppen rådets råd for sju: VOIM blir Energi, NOSN, NTG og MVW blir Industri, PLCAN blir Shipping, NORTH blir Finans, og SCOIN tas ut, fordi selskapet er under avvikling. Kl. 22:06: forslagene i spørsmål 2, 4, 5 og 6 er godtatt, og story 8.11b tar de 15 inn i bransjelistene. Rådet anbefalte alt fra kl. 22:03. Bransjene er sjekket av gruppen, og merket «usikker» tas bort. VG6 (middels) rettes med tester av valideringen i `bruk_liste`. Svaret er ført etter instruksjonen kl. 00:30 i `docs/ai-prompts/2026-11-09.md`.
