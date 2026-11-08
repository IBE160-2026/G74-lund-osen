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
