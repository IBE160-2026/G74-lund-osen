---
title: 'Story 9.16: flere brukerreiser i PRD-en'
type: 'docs'
created: '2026-11-17'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'ba866204'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd-endringslogg.md'
---

Skrevet 17.11, etter at appen ble bygget, i vinduet som bygde 9.15, etter steg 1
i instruksjonen etter gruppens svar 16.11 kl. 20:22 (design og UX før brukertest
2), ført i `docs/ai-prompts/2026-11-16.md`. Rådet anbefalte det. Instruksjonen
kl. 21:50 om ikonene ble gjort ferdig først, med flettingen av #162 og
ryddingen. Neste ledige nummer i Epic 9 etter 9.15 er 9.16. Worktreen er
`G74-lund-osen-9-16`, på grenen `9-16-flere-brukerreiser`, fra `origin/main`
(`ba866204`).

## Storyen

Som **gruppe** vil vi at §1 i PRD-en har flere brukerreiser enn UJ-1, slik at
brukertest 2 og vurderingen kan se hvem appen er for også utenfor hovedflyten.

**Oppfyller:** steg 1 i instruksjonen etter svaret 16.11 kl. 20:22 ·
**Begrenses av:** regel 3, 11, 19 og 20

**Avhenger av:** 2.18, 8.21, 8.27, 9.11. **Én økt:** ja.

## Svaret

*Svar 2026-11-16 kl. 20:22 (gruppens svar, rådet anbefalte det):* §1 i PRD-en
får én eller to brukerreiser til, i samme form som UJ-1: en person, stegene,
Climax, Edge, kravene reisen hviler på og suksessmålet som måler den. Forslaget
er Min liste med notater for en som kommer tilbake, og KI av og på. Bare det
appen gjør på main tas med, og hvert steg sjekkes mot malene og testene. Det
samlede UX-dokumentet tas senere, med `/goal`, som gruppen starter selv.

## Det som skrives

- **§1 i `prd.md`:** to nye avsnitt under «Brukerreisen UJ-1», UJ-2 (Min liste
  med notater) og UJ-3 (KI av og på), i samme form som UJ-1. Overskriften blir
  «Brukerreisene». Hver reise sier at den er skrevet 17.11, etter at appen ble
  bygget, og beskriver det appen gjør på main.
- **`prd-endringslogg.md`:** én datert linje under «Endringer etter 12.11»
  (regel 19).
- `updated` i begge filene settes fra `date` (regel 4).
- Ingen kode, ingen maler og ingen tester endres. Ingen nye krav: reisene
  hviler på krav som finnes.

## Sjekken mot main

Hvert steg i reisene har en kilde i malene eller `src/app.py`, og en test som
låser det. Tabellen under fylles når reisene er skrevet.

## Grenser

- Bare det appen gjør på main nå. Står noe i PRD-en som malene ikke gjør, eller
  omvendt, blir det et spørsmål med forslag, ikke en endring.
- Ingen kurser, volum eller navn på testpersoner (regel 16). Personene i reisene
  er oppdiktet.
- Reisene skrives ikke som om de var laget før koden.

## Kontroll

- [ ] UJ-2 og UJ-3 i §1, i samme form som UJ-1
- [ ] Hvert steg sjekket mot malene og testene, med kilde i tabellen
- [ ] Linja i endringsloggen
- [ ] Diff mot HEAD etter omskrivingen, uten krav som er borte (regel 13)
- [ ] Gjennomgangen er tatt
- [ ] `--dokumentene` er grønn lokalt
- [ ] CI er grønn i alle jobbene
