---
title: 'Story 9.9: dokumenttestene i én kommando'
type: 'chore'
created: '2026-11-09'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '78a45186'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/docs/kvalitetssikring.md'
  - '{project-root}/.logs/marian-osen/issues.md'
---

Skrevet 09.11 i ekstravinduet (instruksjonen limt inn kl. 11:00, med tillegget kl. 11:28, som føres i `docs/ai-prompts/2026-11-09.md` i steg 4). Gruppens svar 09.11 kl. 10:47 og 10:53: de fire små tingene fra `issues.md` tas nå. Dette er den første, punktet fra 08.11 om at de seks dokumenttestene ikke dekker alle testene som leser README-en (`test_aksjesiden_8_20a.py` ga rød CI på `00b56821`). Tillegget kl. 11:28: de tre små PR-ene bygges først og flettes i natt av en egen instruksjon. Endringen bygges fra head-en til PR #129 (`78a45186`), på grenen `dokumenttestene`, i worktreen `G74-lund-osen-dokumenttestene`, og stoppes før flettingen. Spørsmålene står åpne til gruppen har svart; forslaget er det som er bygget.

## Spørsmål til gruppen før flettingen

1. **Nummeret.** Endringen står ikke i `epics.md`. *Forslag:* story 9.9 under Epic 9, fordi 9.8 er den siste der, og `test_kvalitetssikring.py` krever navnet `spec-<epic>-<story>-…` når spesifikasjonen er ferdig. Storyen føres i `epics.md` i steg 4 sammen med svarene.
2. **Hva er en dokumenttest?** *Forslag:* en testmodul der en strengkonstant i koden peker på README-en, `docs/` eller `_bmad-output/`, eller som importerer en hjelpemodul i `tests/` som gjør det (som `tests/dokumentene.py`, også i flere ledd). Docstrings og kommentarer teller ikke, fordi de bare nevner dokumentene. Hele modulen er med, ikke enkelttester, fordi testfilene ikke skal endres og en modul kan lese et dokument i en fixture.
3. **Kommandoen.** *Forslag:* `uv run pytest --dokumentene`, et valg i `tests/conftest.py` som hopper over de andre modulene før de importeres.
4. **Vakten.** *Forslag:* en audit-hook i `tests/conftest.py` noterer hvert dokument hver testmodul åpner under kjøringen, også under innsamlingen og i fixturer. `test_ingen_test_som_leser_dokumentene_faller_utenfor` i `tests/test_dokumenttestene.py` kjøres sist og feiler hvis en modul som åpnet et dokument, ikke er med i kommandoen. Den virker i hele settet, lokalt og i CI. Grensen: en underprosess som en test starter, noteres ikke, så der avgjør koden alene.
5. **Antallet.** Kommandoen finner 25 moduler, ikke 6. Mange av dem leser README-en eller hjelpen for å sjekke at sidene og dokumentene sier det samme, og de er også de tregeste (`test_dobbeltklikk.py`, `test_app.py`). *Forslag:* godta det, fordi det er nettopp de testene som kan bli røde når bare et dokument endres. Tiden står under «Bygget».
6. **De seks.** *Forslag:* linja fra 24.10 i `docs/kvalitetssikring.md` blir stående, med en Lagt til-linje under om at «testene for dokumentene» fra nå er kommandoen. README-en får kommandoen under «Tester» (regel 19).

## Intent

**Problem:** «Testene for dokumentene» er seks filer skrevet ned for hånd 24.10. En test som leser README-en uten å stå blant dem, ble ikke kjørt før en commit som bare endret dokumentene, og CI ble rød på `00b56821`.

**Approach:** Modulene finnes i koden når kommandoen kjøres, og en vakt i hele settet feiler når en modul åpner et dokument uten å være funnet.

## Delene

### A) Modulene finnes i koden
`modulene()` i `tests/dokumenttestene.py`.
- **Ville feilet hvis:** en av de seks fra 24.10 eller `test_aksjesiden_8_20a.py` falt utenfor, en docstring gjorde en modul til en dokumenttest, eller en test som leser gjennom en hjelpemodul, ble borte.

### B) Kommandoen
`--dokumentene` i `tests/conftest.py`.
- **Ville feilet hvis:** kommandoen samlet inn moduler som ikke leser dokumentene, eller manglet en som gjør det.

### C) Vakten
Audit-hooken og testen som kjøres sist.
- **Ville feilet hvis:** en modul åpnet README-en, `docs/` eller `_bmad-output/` i hele settet uten å være med, eller lytteren ikke noterte noe, så vakten aldri kunne feile.

## Grenser

Ingen testfil endres, utenom `tests/conftest.py`. Ingen API-kall, `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` røres ikke.
