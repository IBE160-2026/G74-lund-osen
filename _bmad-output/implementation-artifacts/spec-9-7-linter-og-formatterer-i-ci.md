---
title: 'Story 9.7: linter og formatterer i CI'
type: 'chore'
created: '2026-10-17'
status: 'done'
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
   *Lagt til 2026-10-17 (gjennomgangen, BH10):* treet er det samme også uten normaliseringen, med docstringene ordrett (`ast.dump` for alle 71 filene mellom `1bd8eaa` og `328161a`), så `__doc__` er uendret.
4. Pyflakes (`F`), med det den finner rettet.
5. Importene (`I`), sortert av `ruff check --fix`.
6. Bugbear (`B`), med det den finner rettet.
7. CI kjører `ruff check` og `ruff format --check` før testene, og `tests/test_ruff.py` kjører det samme.
8. README («Tester»), `docs/kvalitetssikring.md` og `CLAUDE.md` sier at ruff kjøres før en commit.
9. `src/meldinger.py`: docstringen sier at modulen ikke brukes i v1 (plan B), og at den er beholdt med testene.

## Avgjort i spesifikasjonen

- **Linjelengden er 120,** ikke 88 som er standard. Det er nærmest koden slik den er skrevet: 36 linjer i `src/` og `tests/` er lengre enn 120, og 368 lengre enn 100. Med 120 endrer formatteringen 4796 linjer, med 88 endrer den 8707.
  *Rettet 2026-10-17 (gjennomgangen, VG1):* tallene over ble talt med et `grep` som ikke tok med linjer som begynner med `-` eller `+` etter tegnet for diffen. Talt på nytt med `ruff format --diff` på en kopi av `1bd8eaa` er det 4834 linjer med 120 og 8757 med 88. Commiten `328161a` har 2995 nye og 1847 fjernede linjer (`git diff --shortstat`).
- **B905 (`zip()` uten `strict=`) er slått av.** Den er en av bugbears meningsregler (B9xx), som flake8-bugbear har av som standard. Av de 19 stedene den fant, er minst to ment for lister med ulik lengde (`zip(kurser, kurser[1:])` i `src/signalberegning.py` og i `tests/test_signalberegning.py`), der `strict=True` ville gitt en feil. I `src/migrering.py` er listen over anvendte migrasjoner kortere enn listen over filer når basen er bak.
- **F811 i `tests/test_utseende.py`** gjelder fikstur som er importert fra `test_demo` og brukt som parameter, slik pytest gjør det. Den får `noqa` på linja, ikke en regel som er slått av for hele fila.

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke mot EODHD. `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22).
- `.github/scripts/` er ikke med. Instruksjonen sier `src/` og `tests/`.

*Lagt til 2026-10-17 kl. 23:40:* PR #62 er squash-flettet i `faaa36c`, låst til head-en `4cf27a9`. CI var grønn på head-en (39071749356) og på main (39071843876). Triagen står som kommentar i PR #62.

## Mutantene

Én om gangen med `-x`, i den ferske klonen med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver. Alle ble fanget på `42a64a2`, og A1 og A2 også på `a54d348`, før gjennomgangen:
- A1, `import os` som ikke brukes, i `src/graf.py`: `test_ruff_check_finner_ingenting`.
- A2, en linje som ikke er formattert (`Path( __file__ )`) i `tests/test_ruff.py`: `test_ruff_format_er_kjoert`.
- A3, `[tool.ruff.format] exclude = ["src/graf.py"]` i `pyproject.toml` (VG2): `test_ruff_format_er_kjoert`, som fikk 71 filer i stedet for 72.
- A4, `continue-on-error: true` på steget `ruff check` i CI (BH6): `test_ci_kjoerer_ruff_foer_testene`.
- A5, `import meldinger` i `src/graf.py` (BH12): `test_ingen_modul_i_src_bruker_meldinger`.

## Gjennomgangen

Gjennomgang 17.10 på diffen `1892a53..1bd8eaa` og `328161a..a54d348`, altså alt utenom formatteringen, som ble sjekket med syntakstreet. Linsene var Blind Hunter (BH, 15 funn), Edge Case Hunter (ECH, 7) og Verification Gap (VG, 4). Verification Gap fant alle tallene og påstandene riktige utenom tallene for linjene som ble endret (VG1). Rettingene står i `7ba4dec`, `4a2639a`, `4eda721` og `42a64a2`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| VG2 | `ruff format --check` kunne gått gjennom uten å lese filene, med en exclude bare for formatteringen | medium | patch: testen krever at formatteringen leser like mange filer som sjekken. A3 |
| BH5, VG3 | En regel for smak kunne kommet inn med `extend-select`, eller en gruppe blitt slått av med `per-file-ignores`, uten at testen for reglene feilet | medium | patch: `[tool.ruff]` og `[tool.ruff.lint]` kan bare ha nøklene som står der nå |
| BH6, ECH5, VG4 | Testen for CI fant teksten, ikke steget: en kommentar, `continue-on-error` eller et vilkår slapp gjennom | medium | patch: stegene leses som steg i jobben `pytest`. A4 |
| BH2, ECH3 | Ingen øvre grense for ruff, så en `uv lock --upgrade` kunne gitt ny formattering | low | patch: `required-version = "==0.17.1"`, og testen krever samme versjon i `uv.lock` |
| BH3, ECH4 | Uten utviklingsgruppen sto bare «No module named ruff» | low | patch: en tydelig melding |
| BH4, ECH2 | En fil som git holder ute, ble telt, men ikke sjekket av ruff | low | patch: filene som er sporet i git, eller alle utenom `__pycache__` uten git |
| BH7 | `ruff format` og så `ruff check` sorterer ikke importene | low | patch: `ruff check --fix` og så `ruff format` i README, kvalitetssikringen og regel 23 |
| BH12 | At ingen modul i `src/` bruker `meldinger.py`, sto bare i docstringen | low | patch: `test_ingen_modul_i_src_bruker_meldinger`. A5 |
| BH14, ECH1 | Feilet ruff i CI, ble testene ikke kjørt | low | patch: `if: success() \|\| failure()` på testene, og testen for CI krever det |
| BH15 | Tidsgrensen var den samme som `faulthandler_timeout` | low | patch: 60 s |
| ECH6 | Et krav som ikke er tekst i utviklingsgruppen, ville gitt AttributeError | low | patch |
| VG1 | Tallene for linjene formatteringen endret, kunne ikke gjenskapes | low | patch: talt på nytt, over |
| BH10 | Normaliseringen av docstringene kunne skjult en endring i `__doc__` | low | patch: sjekket uten normalisering, og treet er det samme |
| BH1 | B905 er slått av for hele repoet | low | avvist: bugbear har B9xx av som standard, og `strict=` på hvert sted er en meningsregel. Minst tre steder er listene ment å ha ulik lengde, og `strict=True` ville gitt en feil der |
| BH8 | Fiksturene importeres fra `test_demo`, så `noqa: F811` trengs | low | avvist: slik var testene før 9.7. Å flytte fiksturene til `conftest.py` er ikke en del av storyen |
| BH9 | Lambdaen i `test_fetch_prices.py` fikk ny signatur | low | avvist: `kjoer` kaller den med posisjonsargumenter i samme runde (ECH og VG sjekket det), så B023 fant ingen feil, som commiten sier |
| BH11 | Radene for 9.7 i §3 og §5 mangler | low | avvist: de føres etter flettingen, når spesifikasjonen settes til done (steg 2) |
| BH13 | `.github/scripts/` og `_bmad/scripts/` er ikke med | low | avvist: instruksjonen sier `src/` og `tests/` (Boundaries) |
| ECH7 | Blandede linjeslutt på Windows kunne gitt et annet svar enn i CI | low | avvist: `ruff format --check` går gjennom i arbeidskopien med CRLF og i CI med LF |
