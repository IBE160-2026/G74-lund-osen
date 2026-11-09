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

## Bygget 09.11 (ekstravinduet)

Bygget på grenen `dokumenttestene`, i worktreen `G74-lund-osen-dokumenttestene`, fra `78a45186`.

- **Filene.** `tests/dokumenttestene.py` (ny: `modulene()`, `er_dokument()`, `utenfor()` og `TILLEGG`), `tests/conftest.py` (valget `--dokumentene`, audit-hooken og flyttingen av vakten), `tests/test_dokumenttestene.py` (ny), «Tester» i README-en og en Lagt til-linje under linja fra 24.10 i `docs/kvalitetssikring.md` (regel 19). Ingen annen testfil er endret.
- **Kommandoen** finner 25 moduler, med de seks fra 24.10 og `test_aksjesiden_8_20a.py`. `uv run pytest --dokumentene` tok 7:20 (kl. 11:56:05–12:03:26): 1838 bestått og 7 hoppet over. Hele settet tok 16:39 samme dag.
- **Hele settet alene** kl. 11:37–11:54 på `b47a6bc3`: 4814 bestått, 24 hoppet over og 0 feilet. Vakten fant ingen modul utenfor, så `TILLEGG` er tom.

## Mutantene

Én per del på `b47a6bc3`, med kopi før og fila lik HEAD etterpå (`git hash-object` mot `git rev-parse HEAD:<fil>`, fordi arbeidskopien har CRLF): A (docstringer teller som stier) fanget av `test_bare_koden_teller`, B (`--dokumentene` hopper ikke over noe) av `test_kommandoen_kjoerer_bare_dokumenttestene`, og C (lytteren noterer ingenting) av `test_lytteren_noterer_en_aapning`.

## Gjennomgangen 09.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Diffen `78a45186..b47a6bc3`: Blind Hunter med bare diffen (12 funn), og Edge Case Hunter og Verification Gap i samme agent med repoet (6 og 5 funn). Ingen høye.

**Middels**
- *BH1, rettet.* `"README" in t` gjorde en melding som nevner README-en, til en sti. Nå teller bare stier (`README.md`, `docs`, `_bmad-output`), og delene av en f-streng og meldingen i en assert teller ikke (`test_bare_koden_teller` med `test_melding.py`). Kommandoen fant de samme 25 modulene etterpå.
- *BH2, BH3 og ECH5, rettet.* En modul som leser dokumentene gjennom `src/`, en fixture i `conftest.py` eller en import, kunne ikke tas med uten å endre testfila. Nå føres den i `TILLEGG` i `tests/dokumenttestene.py`, og vaktens melding sier det. Tom i dag.
- *BH5 og ECH1, rettet.* `--ff` og `--nf` sorterte etter conftest-hooken, og med `--lf` kunne vakten kjøre alene og bestå tomt. Nå er hooken en wrapper med `tryfirst`, som flytter vakten etter de andre, og vakten hopper over når ingen andre moduler er med.
- *VG1, rettet.* Ingen test viste at vakten kan feile. Nå er sammenligningen `utenfor()`, testet med en modul som ikke er med (`test_utenfor_finner_en_modul_som_ikke_er_med`).

**Lav**
- *Rettet:* ECH2 (`test_vakten_kjoeres_sist` hopper over når vakten ikke er med), ECH3 (`--dokumentene` tar også ut filer gitt på kommandolinja, `test_kommandoen_tar_ut_en_fil_paa_kommandolinja`), BH7 (en klasse noteres under innsamlingen som modulen sin), BH8 (testen av kommandoen tåler en modul som hoppes over på en maskintype), VG3 (`test_en_test_uten_dokumentene_er_ikke_med`), BH12 og ECH6 (navnet på spesifikasjonen i docstringene).
- *Ført:* BH4 (relative importer og `importlib` følges ikke; ingen i `tests/`), BH6 og ECH4 (bare hendelsen «open» noteres, ikke `stat`, `glob` eller `scandir`, og ikke underprosesser; spørsmål 4), BH9 (undermapper i `tests/`; det er ingen), BH10 (`abspath`, ikke `realpath`; `realpath` på hver åpning koster), BH11 (valget gjelder bare med `tests/conftest.py`, som er der pytest starter fra rota), VG2 (at kommandoen ikke mangler en modul, hviler på vakten i del C), VG4 (innsamlingen er sjekket for hånd av Edge Case Hunter: `test_investorsidene_demo.py` ble notert under `--collect-only`), VG5 (`test_app.py` og `test_kveldshenting.py` er med gjennom en hjelpemodul, ikke ført som kjente).
- **Etter gjennomgangen:** hele settet alene kl. 12:04:24–12:21:02: 4817 bestått, 24 hoppet over og 0 feilet. Vakten fant ingen modul utenfor.
