---
title: 'Story 8.7: sjekk 2 og 3 i kursgrafen'
type: 'feature'
created: '2026-11-09'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '1a72810a'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
---

Skrevet 09.11 i ekstravinduet (instruksjonen limt inn kl. 11:00, med tilleggene kl. 11:28, 12:00 og 15:43, som føres i `docs/ai-prompts/2026-11-09.md` i steg 4). Gruppens svar 09.11 kl. 10:30 og 10:43: 2.4, 2.6 med 8.14, 8.7 og 8.9 bygges i dag og flettes onsdag etter brukertesten. Instruksjonen sier for 8.7: «volumet og bevegelsen i grafen, med de oppdiktede tallene i demoen.» Bygget fra head-en til PR #126 (`1a72810a`), på grenen `8-7-sjekk-2-og-3-i-grafen`, i worktreen `G74-lund-osen-8-7`, og stoppet før flettingen. Spørsmålene står åpne til gruppen har svart; forslaget er det som er bygget.

## Spørsmål til gruppen før flettingen

1. **Båndet for sjekk 2.** FR-202 (tillegget 08.10): «et bånd rundt forrige dags `adjusted_close` med standardavviket fra sjekk 2». *Forslag:* for hver dag fra forrige dags kurs ganger (1 − standardavviket) til forrige dags kurs ganger (1 + standardavviket), med standardavviket sjekk 2 ville regnet den dagen, som en lys flate under linjene. Båndet klippes til grafen, så skalaen er den samme som før.
2. **Volumet.** *Forslag:* søylene i et eget felt under datoene, i samme SVG, med en heltrukken strek for medianvolumet og en stiplet for grensen, `VOLUMFAKTOR` ganger medianen, begge regnet for hver dag med det sjekk 3 ville brukt den dagen. Feltet er like høyt i den brede og den smale grafen (`VOLUMFELT`, 84 px), og den smale har det under forklaringen.
3. **Funksjonene.** *Forslag:* `standardavvik` og `medianvolum` i `signalberegning.py`, som `bevegelse` og `interesse` nå bruker, og grafen også. Da er det én funksjon og ett vindu, og en test bytter vinduet i `Parametre` og ser at streken og båndet følger med.
4. **Dagene uten strek.** De første dagene i serien har ikke nok dager før seg, og en dag der medianvolumet er 0, har ingen strek (NFR-08). *Forslag:* streken brytes der, og teksten under grafen sier hvor mange dager i grafen som mangler den.
5. **Teksten.** *Forslag:* teksten under grafen forklarer båndet og strekene med tallene fra `Parametre`, og «Sjekk 2 og 3 tegnes ikke — de står i kortene over.» er tatt bort. Hjelpen får «Hva er båndet og søylene i kursgrafen?».
6. **Andre grafer.** `bygg_graf` tegner båndet og volumet bare når kalleren gir volumfaktoren. *Forslag:* bare aksjesiden, som instruksjonen sier.
7. **Flettingen med 2.6 og 8.14.** Begge endrer `graf.py`, `aksje.html`, stilarket og avtrykkene. *Forslag:* den som flettes sist, får konfliktene løst og avtrykkene og bildet av aksjesiden laget på nytt.

## Intent

**Problem:** Grafen viser sjekk 1 med snittet, men sjekk 2 og 3 står bare som tall i kortene (FR-202, FR-706).

**Approach:** Punktene i grafen får volumet, medianvolumet, standardavviket og forrige dags kurs for hver dag, regnet med funksjonene sjekkene bruker. `graf.py` tegner båndet og feltet for volumet i samme SVG.

## Delene

### A) Funksjonene
`standardavvik` og `medianvolum` i `src/signalberegning.py`, og `bygg_punkter` i `src/aksjedetalj.py`.
- **Ville feilet hvis:** streken var en median over et annet vindu enn sjekk 3, den siste dagen i grafen ga et annet utslag enn sjekkene, eller en dag før vinduet fikk en median.

### B) Båndet
`_baandet` i `src/graf.py`.
- **Ville feilet hvis:** båndet ikke fulgte standardavviket fra sjekk 2, eller ikke fulgte vinduet i `Parametre`.

### C) Volumet
`_volumet` i `src/graf.py`, og malen.
- **Ville feilet hvis:** søylene sto i en annen SVG enn kursgrafen, grensen ikke var volumfaktoren ganger medianen, eller streken ble tegnet der medianvolumet er 0.

### D) Teksten og hjelpen
`src/templates/aksje.html` og `docs/hjelp.md`.
- **Ville feilet hvis:** teksten ikke forklarte båndet og strekene med tallene fra `Parametre`.

## Grenser

Ingen API-kall, `src/fetch_prices.py` kjøres bare i testene med en falsk henter, og `data/db/ose.db` røres ikke. Ingen migrasjon. Bildet av aksjesiden i demoen er tatt på nytt.
