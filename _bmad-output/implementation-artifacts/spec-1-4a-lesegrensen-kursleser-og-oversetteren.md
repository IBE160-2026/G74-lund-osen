---
title: 'Story 1.4a: Lesegrensen — Kursleser og oversetteren fra øyeblikksbildet'
type: 'feature'
created: '2026-09-24'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Konsumentene kan ikke få `Kursrad` fra øyeblikksbildet uten at `SnapshotKilde` får en skrivemetode, og EODHDs feltnavn har ikke ett sted der de oversettes. 1.4b har derfor ingenting å lese fra.

**Approach:** Del porten i en leseside (`Kursleser`) og `Kurslager` = `Kursleser` + `erstatt_serie`. Legg til én oversetter `kursrad_fra_eodhd(rad)` og en `SnapshotLeser` som pakker inn `SnapshotKilde` og oppfyller `Kursleser`. Kilde: story 1.4a i `epics.md` slik den står 24.09.

## Boundaries & Constraints

**Always:** Oversetteren fanger bare `UgyldigKursrad` og `KeyError`, og har ingen egen sjekk av verdiene. `adjusted_close` gir `justert_slutt`, `close` gir `slutt`, uten fallback mellom dem (AD-19). En dato godtas bare når `dato.isoformat()` er lik teksten. Et symbol med én rad som ikke kan oversettes, gir tom serie og `sist_hentet` `None`; de andre leses som vanlig (AD-15). `sist_hentet` leveres i UTC (AD-20). Testene telles før og etter.

**Never:** Ingen konsument røres (`app.py`, `markedsoversikt.py`, `aksjedetalj.py`, `signalberegning.py`, `graf.py`). `SnapshotKilde` får ingen skrivemetode. `Kurskilde` og `MinneKilde` blir stående (fjernes i 1.4c). Ingen nettkall, ingen API-kall.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Gyldig rad | `{"date":"2026-09-21","close":…,"adjusted_close":…,"volume":…}` | `Kursrad` med `date` | – |
| Mangler `adjusted_close` | rad uten nøkkelen | Ingen fallback til `close` | `KeyError` → symbolet manglende |
| Ugyldig verdi | NaN, `None`, tekst, ≤ 0, negativt volum, `10**400` | – | `UgyldigKursrad` → symbolet manglende |
| Ugyldig dato | «2026-9-1», «20260921», «2026-W39-1», «2026-09-31», ikke-tekst | – | `UgyldigKursrad` → symbolet manglende |
| Raden er ikke et objekt | liste, tall, `None` | – | `UgyldigKursrad` → symbolet manglende |
| To rader med samme dato | ett symbol | Tom serie, `sist_hentet` `None` | Gjettes ikke |
| Usortert serie | datoer i feil rekkefølge | Sortert, nyeste sist | – |
| Tom eller ukjent serie | `[]` eller symbol som mangler | `[]` og `None` | – |
| `hentet` kan ikke leses | mangler, `None`, ikke ISO 8601, eller uten tidssone | Hele øyeblikksbildet er manglende: `[]` og `None` for alle symboler | Gjettes ikke |

**Beslutninger 2026-09-24 (Marian):**
- `hentet` som ikke kan leses: hele øyeblikksbildet behandles som manglende (alternativ B). Grunnen er lesekontrakten: i `MinneKurslager` og `SqliteKurslager` har en serie alltid en tid, fordi `erstatt_serie` setter begge. Med alternativ A ville `SnapshotLeser` vært det eneste lageret som kan gi en serie uten tid, og 1.4c måtte laget et unntak for det.
- Lesekontrakten for alle tre lagre, i begge retninger: `sist_hentet(s)` er `None` hvis og bare hvis `serie(s)` er tom.
- Spesifikasjonen beholdes hel (omtrent 1 900 tokens). Kontrollpunktet om tre lagre hører til 1.4a.

</frozen-after-approval>

## Code Map

- `src/kursdata.py` -- `Kursrad`/`UgyldigKursrad` (gjenbrukes uendret); `Kurslager` (Protocol, deles i `Kursleser` + `erstatt_serie`); `SnapshotKilde` (`hentet: str | None`, `serier: dict`, `fra_fil`; uendret). Nye symboler legges her, ved siden av `SnapshotKilde`. 1.5 flytter snapshot-delene ut senere
- `src/lagring_sqlite.py`, `MinneKurslager` -- uendret; oppfyller `Kursleser` automatisk
- `src/app.py:37` -- et symbol med tom serie navngis allerede i «Uten data i denne kilden» (`index.html:98–100`). Navngivingen i AD-15 skjer altså når 1.4b kobler appen til `SnapshotLeser`; 1.4a garanterer tom serie og `None`
- `tests/test_kurslager.py` -- fixturen `lager` (minne, sqlite); `TestKurslagerKontrakt`, `TestSistHentet`, `TestAvvisningEndrerIngenting`. `TestKurskildeErPaaVeiUt` røres ikke
- Øyeblikksbildet `kurser-raa-2026-09-23.json`: 15 symboler, 3 735 rader, alle oversettbare med reglene over (sjekket 24.09, bare antall lest)

## Tasks & Acceptance

**Execution:**
- [ ] `src/kursdata.py` -- `Kursleser` (runtime-checkable Protocol: `serie`, `sist_hentet`); `Kurslager(Kursleser, Protocol)` med bare `erstatt_serie` i tillegg; `kursrad_fra_eodhd(rad)`, som parser datoen strengt og pakker dato- og typefeil i raden inn som `UgyldigKursrad`; `SnapshotLeser(kilde)`, som oversetter alt ved oppretting og gir kopier ut -- ett oversettelsessted, AD-3 og AD-19
- [ ] `tests/test_kurslager.py` -- ny fixture `leser` (minne, sqlite, snapshot) med én fyllefunksjon per lager. Lesetestene flyttes til den: samme verdier, kronologisk, ukjent symbol, utlevert serie kan ikke endre lageret, ukjent symbol har ingen tid, tiden for et fylt symbol, UTC. Tester som skriver eller krever ulike tider per symbol blir på `lager`. Nye lesetester: `sist_hentet` er `None` hvis og bare hvis serien er tom (begge retninger, alle tre lagre), og sorterte, unike datoer
- [ ] `tests/test_snapshotleser.py` -- oversetteren og `SnapshotLeser`: hver rad i matrisen over, pluss at ett dårlig symbol ikke rører de andre, at `hentet` som ikke kan leses gjør hele bildet manglende, at en `hentet` med annen sone leveres i UTC, og at `SnapshotLeser` ikke er en `Kurslager`
- [ ] Protokolltester -- `Kursleser` har nøyaktig `serie` og `sist_hentet`; `Kurslager` har de to pluss `erstatt_serie`

**Acceptance Criteria:**
- Given hele testsettet, when det kjøres før og etter, then er begge grønne, og tallene står i commit-meldingen
- Given en mutant der oversetteren faller tilbake fra `adjusted_close` til `close`, when testene kjøres, then feiler minst én test (story 1.4a, «Ville feilet hvis»)
- Given de fem konsumentmodulene, when diffen leses, then er ingen av dem endret

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

To rader med samme dato kan ikke velges mellom uten å gjette, så symbolet blir manglende. En rad som ikke er et objekt, pakkes inn som `UgyldigKursrad` i oversetteren, så `SnapshotLeser` bare trenger å fange de to feiltypene storyen nevner.

## Verification

**Commands:**
- `uv run pytest -q` -- expected: alt grønt; 285 før
- Mutant: `rad.get("adjusted_close", rad["close"])` i `kursrad_fra_eodhd` -- expected: minst én test feiler
