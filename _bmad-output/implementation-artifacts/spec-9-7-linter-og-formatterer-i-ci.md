---
title: 'Story 9.7: linter og formatterer i CI'
type: 'chore'
created: '2026-10-17'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '1892a53'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/kvalitetssikring.md'
---

## Intent

**Problem:** koden er ikke sjekket av en linter eller formattert på én måte. Formatteringen varierer mellom filene, og ingen test finner en ubrukt import. Story 9.7 i `epics.md` (gruppens svar 17.10 kl. 22:38–22:42).

**Grunnlaget:** instruksjonen 17.10 kl. 23:13, steg 3. PR-en flettes når vilkårene i steg 2 holder.

## Planen, én commit per punkt

1. Storyen i `epics.md` og denne spesifikasjonen.
2. ruff som utviklingsavhengighet (`uv add --dev ruff`, 0.17.1 i `uv.lock`), og `[tool.ruff]` i `pyproject.toml`: bare `src/` og `tests/`, linjelengde 120 og ingen regler ennå.
3. `ruff format` på `src/` og `tests/`. Uten endring i oppførsel: syntakstreet for hver fil er det samme før og etter, med docstringene normalisert som `inspect.cleandoc` gjør.
4. Pyflakes (`F`), med det den finner rettet.
5. Importene (`I`), sortert av `ruff check --fix`.
6. Bugbear (`B`), med det den finner rettet.
7. CI kjører `ruff check` og `ruff format --check` før testene, og `tests/test_ruff.py` kjører det samme.
8. README («Tester»), `docs/kvalitetssikring.md` og `CLAUDE.md` sier at ruff kjøres før en commit.
9. `src/meldinger.py`: docstringen sier at modulen ikke brukes i v1 (plan B), og at den er beholdt med testene.

## Avgjort i spesifikasjonen

- **Linjelengden er 120,** ikke 88 som er standard. Det er nærmest koden slik den er skrevet: 36 linjer i `src/` og `tests/` er lengre enn 120, og 368 lengre enn 100. Med 120 endrer formatteringen 4796 linjer, med 88 endrer den 8707.
- **B905 (`zip()` uten `strict=`) er slått av.** Den er en av bugbears meningsregler (B9xx), som flake8-bugbear har av som standard. Av de 19 stedene den fant, er minst to ment for lister med ulik lengde (`zip(kurser, kurser[1:])` i `src/signalberegning.py` og i `tests/test_signalberegning.py`), der `strict=True` ville gitt en feil. I `src/migrering.py` er listen over anvendte migrasjoner kortere enn listen over filer når basen er bak.
- **F811 i `tests/test_utseende.py`** gjelder fikstur som er importert fra `test_demo` og brukt som parameter, slik pytest gjør det. Den får `noqa` på linja, ikke en regel som er slått av for hele fila.

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke mot EODHD. `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22).
- `.github/scripts/` er ikke med. Instruksjonen sier `src/` og `tests/`.
