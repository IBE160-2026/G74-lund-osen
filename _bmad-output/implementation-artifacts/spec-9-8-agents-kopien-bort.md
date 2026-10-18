---
title: 'Story 9.8: kopien .agents/skills/ tas bort'
type: 'chore'
created: '2026-10-18'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f05e1d7'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/kvalitetssikring.md'
---

## Intent

**Problem:** BMAD ble satt opp for Claude Code og Codex 15.09 (`59a90a2`), så de samme skillene ligger både i `.claude/skills/` og i `.agents/skills/`, 242 filer hver, med likt innhold (sjekket fil for fil med `cmp` 18.10). Gruppen bruker bare Claude Code. I tillegg har `.gitignore` en del for Next.js fra malen, og `.env.example` sier at `EODHD_API_KEY` er den eneste variabelen og at en full henting bruker 15 kall. Story 9.8 i `epics.md` (gruppens svar 18.10 kl. 00:03).

**Grunnlaget:** instruksjonen 18.10 kl. 11:40, steg 2 og 3. PR-en flettes når vilkårene i steg 4 holder.

## Planen, én commit per punkt

1. Storyen i `epics.md` og denne spesifikasjonen.
2. a) `git rm -r .agents/`. Lokalt fantes ingen `__pycache__` under `.agents/`, så mappa er borte etter commiten.
3. b) `- codex` tas ut under `ides` i `_bmad/_config/manifest.yaml`.
4. c) «Mappestruktur» i README-en nevner `_bmad/` og `.claude/skills/`, og `.agents/` tas ut av unntaket for `.csv`, `.json` og `.jsonl` i `.github/scripts/morgensjekk.py`.
5. d) To tester i `tests/test_ryddighet.py`: ingen fil under `.agents/` er sporet i git (hoppes over uten git), og manifestet har bare `claude-code` under `ides`.
6. e) `.gitignore`: delen for Next.js tas bort, utenom `node_modules/`, `dist/` og `build/`, og kommentarene skrives på norsk.
7. f) `.env.example`: tre variabler, og 16 av de 20 kallene.

## Avgjort i spesifikasjonen

- **Tre variabler:** koden leser `EODHD_API_KEY` (`src/fetch_prices.py`), `OSE_KI_TJENESTE` og `OSE_KI_OLLAMA_URL` (`src/ki_tekst.py`). `OSE_DEMO` og `OSE_I_DOCKER` (`I_DEMO` og `I_DOCKER` i `src/app.py`) settes av compose, Dockerfile og demoen, ikke i `.env`.
- **16 kall:** 15 aksjer og hovedindeksen, ett kall hver (docstringen i `src/fetch_prices.py`, story 2.8).
- **Manifestet leses som tekst,** ikke med PyYAML, som ikke er en avhengighet. Testen leser lista under `ides:` til neste nøkkel på toppnivå.

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke. `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22).
- `.claude/skills/` endres ikke.
