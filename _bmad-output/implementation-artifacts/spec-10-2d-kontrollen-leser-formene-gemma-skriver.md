---
title: 'Story 10.2 (10.2d): kontrollen i FR-603 leser formene Gemma skriver'
type: 'feature'
created: '2026-10-18'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '52d5107'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-4b-ki-tekstene-i-demoen.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

## Intent

**Problem:** Kontrollen i FR-603 (`src/ki_kontroll.py`) leser retningen bare der teksten sier «retningen er X» eller «X retning». Gemma skriver retningen som «Dette signalet er Negativt» eller «av typen Ingen», og styrken som «av styrke tre». En feil retning eller styrke i de formene slipper gjennom. Hullet ble funnet med mutant K2 i 3.4b og står som åpent punkt i `spec-3-4b-ki-tekstene-i-demoen.md`.

**Grunnlaget:** gruppens svar 18.10 kl. 21:03: hullet rettes før byggestoppen mandag 19.10 kl. 20:40, så uka med logget drift går med den rettede kontrollen. Instruksjonen 18.10 kl. 22:18. Prompten står, versjon 2.

## Kontrollpunktene

- a) Hullet, uten å endre koden: en test med de 13 tekstene i `src/demo_ki_tekster.json`, der retningen i første setning er byttet til en feil retning. Den skal stoppe hver av dem. På main slipper 12 gjennom, så testen er merket `xfail` med `strict=True` og grunnen, til punkt b.
- b) Kontrollen: retningen leses også der teksten sier den om hele signalet: «signalet er X», også med «av typen», med fyllordene og bøyd (positivt, negativt), «retningen på signalet er X», og «et X signal» når det gjelder hele signalet. Styrken leses også i «av styrke N». Det som gjelder én sjekk, som «Trendens retning er positiv» og «Trenden ga et positivt utslag» eller «signal», sjekkes fortsatt ikke. Docstringen i `src/ki_kontroll.py` sier det. `xfail` fra a tas bort i samme commit.
- c) Testene, med «Ville feilet hvis»: hver form i b stoppes med feil retning eller styrke og slipper gjennom med riktig; formene om én sjekk stoppes ikke; de 13 tekstene i demoen består som de er, så de lages ikke på nytt. Den nye kontrollen kjøres også på KI-tekstene som står i sporede filer, som `malinger.md` ved PRD-en, og hver tekst som får et annet svar enn før, står her med grunnen. Mutanter én om gangen med `-x` og kopi før og sha256 mot HEAD etter: mønsteret for «signalet er» tatt bort, «av typen» tatt bort, «av styrke N» tatt bort, og et mønster som også leser «Trenden ga et positivt utslag».

## Planen, én commit per punkt

1. a) Testen for hullet, merket `xfail(strict=True)`.
2. b) Mønstrene i `ki_kontroll.py`, docstringen, og `xfail` tatt bort.
3. c) Testene for hver form og for formene om én sjekk, og kjøringen på tekstene i sporede filer.

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22), og ingen test kaller Ollama.
- Prompten står, versjon 2. Tekstene i demoen lages ikke på nytt.
