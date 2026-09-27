---
title: 'Story 1.9: Aksjene i basen, og tabellene peker på dem'
type: 'feature'
created: '2026-09-27'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '72cd401ea12cb1055841f4ed96ada455840506a3'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/kodegjennomgang-epic-1.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** De fire tabellene har ingen koblinger, og ingen spørring henter fra flere av dem. `SqliteKurslager` godtar ethvert symbol, også `EQNR.OL`, og bare porten til `Vurderingslager` stopper et symbol utenfor universet (G10).

**Approach:** `0003_aksje.sql` lager `aksje` med de femten, og triggere, ikke fremmednøkler, gjør at basen selv avviser et ukjent symbol i `kurs`, `kursserie` og `vurdering`, også på en tilkobling som ikke har slått på noe.

## Boundaries & Constraints

**Always:**
- `aksje (symbol TEXT PRIMARY KEY, ticker TEXT NOT NULL UNIQUE, navn TEXT NOT NULL, sektor TEXT NOT NULL)`, fylt i rekkefølgen i `AKSJEUNIVERS`.
- Triggerne bruker `NOT EXISTS (SELECT 1 FROM aksje WHERE symbol = NEW.symbol)`, ikke `NOT IN`, som slipper `NULL` gjennom.
- «Avvises av basen» betyr: en ny `sqlite3.connect` som ikke har slått på noe, og en rå `INSERT` eller `UPDATE`.
- Regel 6: ingen nett i testene. `src/fetch_prices.py` kjøres ikke.

**Never:**
- Ingen fremmednøkkel eller trigger fra `vurdering` til `kurs` (AD-18).
- Ingen ombygging av en tabell som finnes, og ingen endring i `0001` eller `0002`.
- Ingen symbolsjekk i Python i `SqliteKurslager` eller `MinneKurslager` (2.5 avgjør porten). G11 står for 2.5.

## Beslutninger (godkjent 27.09)

- **Trigger, ikke fremmednøkkel:** SQLite håndhever fremmednøkler bare når tilkoblingen har slått dem på (grunnen i `0002`). `PRAGMA foreign_keys = ON` gjør ingenting inne i løperens `BEGIN IMMEDIATE`. `ALTER TABLE` kan ikke legge en fremmednøkkel på en kolonne som finnes, og ombygging av `vurdering` er utelukket (AD-7). Alt tre er prøvd i minnet 27.09.
- **Rader for et ukjent symbol i en base i versjon 2:** `0003` stopper og rulles tilbake, og basen står på versjon 2. Rader i `vurdering` kan verken slettes eller skrives på nytt (AD-7), så en migrasjon som lar dem stå uten aksje, ville brutt det basen nå lover.
- **Sletting:** en aksje med rader i `kurs`, `kursserie` eller `vurdering` kan ikke slettes. En aksje uten rader kan det: `aksje` er oppsett, ikke et uerstattelig lager. Symbolet kan aldri endres. `navn` og `sektor` kan.
- **Rekkefølgen:** testen som holder tabellen og `AKSJEUNIVERS` like, leser med `ORDER BY rowid`, fordi SQLite ikke lover noen rekkefølge uten.
- **Spinen:** ny AD-21, og merknader under AD-16, AD-18, raden «Skjemaendring på et uerstattelig lager» og konvensjonen «Symbol mot ticker».
- **Gjennomgangen** har tre lag: Blind Hunter, Edge Case Hunter og Verification Gap.

## I/O & Edge-Case Matrix

| Scenario | Input | Forventet |
|---|---|---|
| Kjent symbol | rå `INSERT` av `EQNR` i hver tabell | godtas |
| Ukjent symbol | rå `INSERT` av `EQNR.OL`, `eqnr` eller `XXX` i hver tabell | `IntegrityError`, ingen rad |
| `NULL` | `INSERT INTO kursserie` med `symbol` `NULL` | `IntegrityError` |
| Endret symbol | `UPDATE` av `symbol` til `EQNR.OL` i hver tabell | `IntegrityError`, raden er uendret |
| Sletting | `DELETE` av en aksje med rad i bare én av de tre tabellene | `IntegrityError` |
| Sletting | `DELETE` av en aksje uten rader | godtas |
| Adapteren | `erstatt_serie("EQNR.OL", …)` | `ValueError`, ingen rad i `kurs` eller `kursserie` |
| Versjon 2 med ukjent symbol | rad for `EQNR.OL` i `kurs`, `kursserie` eller `vurdering` | `MigrasjonsFeil`, basen står på versjon 2, radene er urørt |

</frozen-after-approval>

## Code Map

- `src/migrasjoner/0002_vurdering.sql` -- mønsteret: kommentarhodet, triggerne på `grunn` og grunnen til trigger framfor fremmednøkkel. Endres ikke.
- `src/migrering.py` -- `migrer()` kjører hver fil i `BEGIN IMMEDIATE` (`_kjoer`), og en `sqlite3.Error` gir `MigrasjonsFeil` og tilbakerulling. Endres ikke.
- `src/kursdata.py:23–57` -- `Aksje` og `AKSJEUNIVERS`. `navn` har «Vår Energi» og «Sjømat», så fila er UTF-8.
- `src/lagring_sqlite.py` -- `erstatt_serie` gjør `IntegrityError` om til `ValueError` (`:102`). `_kontroller_noekkel` avviser før SQL-en. Ingen endring ventes.
- `tests/test_lagring_sqlite.py:186–215` og `tests/test_vurderingslager.py:322` -- kopierer katalogen eller bygger versjon 1, og tåler en 0003. Ingen eksisterende test skriver et symbol utenfor universet til SQLite.
- `tests/test_kurslager.py:225` -- fixturen kjører kontrakttestene mot begge lagrene. `MinneKurslager` godtar `EQNR.OL`, så adaptertesten er bare for SQLite, og avviket føres i forutsetningen i 2.5.
- `ARCHITECTURE-SPINE.md` -- AD-16 (`:232`), AD-18 (`:292`), konvensjonen (`:321`) og det åpne punktet (`:442`).

## Tasks & Acceptance

**Execution:** én commit per punkt, pushet til grenen `1-9`. 0003 bygges opp på grenen, og hashen låses når grenen flettes.
- [x] `src/migrasjoner/0003_aksje.sql`, `tests/test_aksje.py` -- tabellen og de femten, og testen mot `AKSJEUNIVERS` med `ORDER BY rowid`. Tom base gir versjon 3.
- [x] samme -- triggerne på `kurs`, `kursserie` og `vurdering`, for `INSERT` og `UPDATE OF symbol`, og testene i matrisen på en ny tilkobling.
- [x] samme -- `aksje_slettes_ikke_med_rader` og `aksje_symbol_endres_ikke`, med testene.
- [x] samme -- kontrollen for rader med ukjent symbol, og testene for versjon 2 med og uten slike rader.
- [x] `tests/test_aksje.py` -- adaptertesten, AD-18-testen (ingen fremmednøkkel på `vurdering`, og en vurdering kan skrives uten kursrader) og spørringen med `JOIN aksje` som gir navnet sammen med vurderingen.
- [x] `ARCHITECTURE-SPINE.md` -- AD-21 og merknadene, `updated` fra klokka.
- [x] `epics.md` -- forutsetningen i 2.5: G10 løst i basen, og avviket mellom lagrene.

**Acceptance Criteria:**
- Gitt en tom base, når `migrer` kjøres, så står basen på versjon 3, og `aksje` er lik `AKSJEUNIVERS` felt for felt og i samme rekkefølge.
- Gitt vurderingen for EQNR i dag, når én spørring med `JOIN aksje` kjøres, så gir den vurderingen og «Equinor».
- Gitt hvert kontrollpunkt, når mutanten legges inn alene, så feiler minst én test, og koden settes tilbake fra en kopi, ikke med `git checkout`: MPCC mangler i 0003, feil `navn`, INSERT-triggeren på `kurs` mangler, `kursserie` med `NOT IN`, INSERT-triggeren på `vurdering` mangler, UPDATE-triggerne mangler, slettetriggeren sjekker bare `kurs`, triggeren for endret symbol mangler, en trigger fra `vurdering` til `kurs`, `except IntegrityError` fjernet i `SqliteKurslager`, og kontrollen for versjon 2 mangler.

## Implementation Notes

Bygget 27.09 direkte fra spesifikasjonen, ikke av en subagent, fordi planen krever én commit per punkt og mutantene én om gangen. Commitene på grenen `1-9`: (a) `4b62e39`, (b) `48e9929`, (c) `6201e59`, (d) `f429f0d`, (e) `08cfc01`, (f) `d8c166d` og (g) `3377083`. Alle testene står i `tests/test_aksje.py`, og ingen eksisterende test er endret. Ingen kode i `src/` er endret utenom `0003_aksje.sql`. Tester: 816 før og 871 etter.

- **REPLACE:** under (c) viste det seg i minnet at `INSERT OR REPLACE` med en ticker som finnes, og `UPDATE OR REPLACE` av `ticker`, sletter raden som er i veien uten å kjøre DELETE-triggeren (`recursive_triggers` er av). EQNR forsvant, og kursen ble stående. To triggere til, `aksje_erstattes_ikke_insert` og `aksje_erstattes_ikke_update`, avviser en `INSERT` eller en ny ticker som kolliderer. Det følger av beslutningen om at en aksje med rader ikke kan slettes, og er ingen ny beslutning. En `INSERT` med et symbol eller en ticker som finnes, gir derfor «en aksje erstattes ikke» i stedet for `UNIQUE constraint failed`.
- **Kontrollen i versjon 2** er en `CHECK (rader_uten_aksje = 0)` på hjelpetabellen `kontroll_0003`, som fjernes igjen i samme migrasjon. `RAISE` finnes bare i triggere.
- `UKJENTE` i testene er `EQNR.OL`, `eqnr`, `XXX`, tom streng og ` EQNR`.

**Mutantene**, hver lagt inn alene med `mutant.py` i scratchpad: fila kopieres, mutanten legges inn, hele suiten kjøres, og fila settes tilbake fra kopien og sjekkes mot hashen. Ingen `git checkout`.

| Mutant | Utfall |
|---|---|
| M1: MPCC mangler i 0003 | 1 feil: testen mot `AKSJEUNIVERS` |
| M2: `Var Energi` i stedet for `Vår Energi` | 1 feil: samme |
| M2b: EQNR og DNB byttet om | 1 feil: samme |
| M3: INSERT-triggeren på `kurs` mangler (`WHEN 0`) | 5 feil: alle fem ukjente symboler i `kurs` |
| M4: triggeren på `kursserie` med `NOT IN` | 1 feil: NULL-testen |
| M5: INSERT-triggeren på `vurdering` mangler | 5 feil |
| M6: UPDATE-triggeren mangler, på `kurs`, `kursserie` og `vurdering` hver for seg | 1 feil hver |
| M7: slettetriggeren sjekker bare `kurs` | 2 feil: rad bare i `kursserie`, og bare i `vurdering` |
| M7b: slettetriggeren mangler | 1 feil: rad bare i `kurs` |
| M8: triggeren for endret symbol mangler | 2 feil: med og uten rader |
| M8b: REPLACE-triggeren for INSERT mangler | 4 feil |
| M8c: REPLACE-triggeren for UPDATE mangler | 1 feil |
| M9: en trigger fra `vurdering` til `kurs` | 55 feil, blant dem AD-18-testene og testene i `test_vurderingslager.py` |
| M10: `except IntegrityError` fjernet i `SqliteKurslager` | 4 feil: adaptertesten og tre eksisterende |
| M11: kontrollen i versjon 2 mangler (`CHECK (1)`) | 3 feil: én per tabell |
| M11b: kontrollen teller ikke `kursserie` | 1 feil |

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q` -- expected: alle består. 816 før, og tallet etter føres i commit-meldingen.
