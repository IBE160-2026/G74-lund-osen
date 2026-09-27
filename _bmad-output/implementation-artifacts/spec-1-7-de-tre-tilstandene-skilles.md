---
title: 'Story 1.7: De tre tilstandene skilles'
type: 'feature'
created: '2026-09-27'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '6c325a2cc90e6cf0e59385dd7735e395f315290d'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** FR-409 krever at en dag uten utslag (styrke 0), en dag vi ikke kjørte og en dag børsen var stengt skilles entydig, og punkt 24 la til en fjerde: en rad med grunn. `Vurderingslager.les` gir `None` både for en børsdag uten rad og en dag som ikke finnes, så skillet finnes ikke i koden i dag.

**Approach:** En ren kjernefunksjon `tilstand(innhold, dato, idag)` i en ny modul `src/tilstand.py` tar imot det `les` gir, datoen og dagens dato i Oslo, og gir én av fire verdier, aldri `None`. Om en dag var børsdag, avgjøres av en ny `er_boersdag` i `src/boersdag.py`, med samme `STENGT` og `DEKKEDE_AAR` som 1.6.

## Boundaries & Constraints

**Always:**
- AD-1: `tilstand.py` er kjerne, ingen I/O, og leser aldri klokka. Den importerer `boersdag` og porten `vurderingsdata`, ikke adapteren.
- Én kalender: `er_boersdag` bruker `STENGT` og `DEKKEDE_AAR` i `boersdag.py`. Ingen ny liste, og ingen egen regel for helg.
- En rad går foran kalenderen: finnes raden, er utfallet raden, uten oppslag i kalenderen.
- Regel 6: ingen nett i testene. Testene som går gjennom lageret, bruker SQLite i minnet.

**Never:**
- Ingen endring i `Vurderingslager`, `SqliteVurderingslager`, `0002` eller `innevaerende_boersdag`.
- Ingen visning, kommando eller spørring mot historikken (punkt 20). Ingen kaller i produksjonskoden.
- Ingen gjetting utenfor `DEKKEDE_AAR`.

## Beslutninger (godkjent 27.09)

- **I dag, børsdag, ingen rad: `IKKE_KJOERT`.** Det er ikke et endelig hull så lenge dagen er inneværende børsdag. Raden kan skrives helt til neste børsdag begynner, så fredagens rad kan komme på lørdag. Et hull er endelig først når dagen ikke lenger er inneværende børsdag (AD-7). Spesifikasjonen og docstringen til `tilstand` sier det.
- **Børsdager før første kjøring: `IKKE_KJOERT`.** Startdatoen lagres ikke. Trenger noen den senere, er den datoen til den første raden i tabellen.
- **`tilstand.py` føres inn** i lagtabellen og grafen i spinen og i `KJERNEMODULER` i `tests/test_konsumentene.py`, slik `boersdag.py` ble i 1.6.
- **Lengden på spesifikasjonen er godtatt.**

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Svar | rad med `Vurdering`, også styrke 0 | `Tilstand(SVAR, vurderingen)` | N/A |
| Grunn | rad med `Grunn` | `Tilstand(GRUNN, grunnen)`, ikke `SVAR` og ikke fravær | N/A |
| Ikke kjørt | ingen rad, børsdag, `dato < idag` | `Tilstand(IKKE_KJOERT)` | N/A |
| Ikke kjørt ennå | ingen rad, `dato == idag`, børsdag | `Tilstand(IKKE_KJOERT)`, ikke endelig før dagen ikke lenger er inneværende børsdag | N/A |
| Før første kjøring | ingen rad, børsdag før første rad | `Tilstand(IKKE_KJOERT)` | N/A |
| Stengt | ingen rad, lørdag, 2026-04-03 eller 2026-12-24 | `Tilstand(IKKE_BOERSDAG)` | N/A |
| Halv dag | ingen rad, 2026-04-01 | `IKKE_KJOERT` | N/A |
| Fremtid | `dato > idag` | ingen tilstand | `ValueError`, også for en lørdag i morgen |
| Utenfor lista | ingen rad, 2025-12-31 eller 2027-01-04 | ingen tilstand | `UtenforKalenderen` fra `er_boersdag` |
| `er_boersdag(2026-01-01)` | stengt, i 2026 | `False`, reiser ikke | N/A |
| Feil type | `dato` eller `idag` er `datetime`, eller `innhold` er noe annet | ingen tilstand | `TypeError` |

</frozen-after-approval>

## Code Map

- `src/boersdag.py` -- `STENGT`, `DEKKEDE_AAR`, `UtenforKalenderen`, `innevaerende_boersdag`, `norsk_dato`. Får `er_boersdag(dag) -> bool`, som reiser bare når `dag.year` ikke er i `DEKKEDE_AAR`. `innevaerende_boersdag` endres ikke, men kan bruke den.
- `src/vurderingsdata.py` -- `Vurdering`, `Grunn`. Endres ikke. Kjernen kan importere porten (som `signalberegning` → `kursdata`).
- `src/lagring_sqlite.py` -- `SqliteVurderingslager.les(symbol, dato)`, kontrollerer symbol og dato. Endres ikke.
- `tests/test_vurderingslager.py` -- mønster for klokke og base i minnet.
- `tests/test_konsumentene.py:25` -- `KJERNEMODULER` får `tilstand.py`, og `FORBUDT_I_PORTEN` får den dermed også.
- Spinen -- lagtabellen (Kjerne), grafen (`tilstand --> boersdag`, `tilstand --> vurderingsdata`), og raden for FR-408 i Capability-kartet får FR-409.

## Tasks & Acceptance

**Execution:**
- [ ] `tests/test_tilstand.py` -- matrisen, med `les` fra `SqliteVurderingslager` i minnet for svar, grunn og ikke kjørt, og fire forskjellige verdier for de fire utfallene -- testene først
- [ ] `tests/test_boersdag.py` -- `er_boersdag`: hverdag, lørdag, hver dag i `STENGT`, 2026-04-01, 2026-01-01 og år utenfor -- samme liste som 1.6
- [ ] `src/boersdag.py` -- `er_boersdag`
- [ ] `src/tilstand.py` -- `Art` (StrEnum: `SVAR`, `GRUNN`, `IKKE_KJOERT`, `IKKE_BOERSDAG`), `Tilstand` (frozen dataclass: `art`, `innhold`) og `tilstand`
- [ ] `tests/test_konsumentene.py` -- `tilstand.py` i `KJERNEMODULER`
- [ ] Spinen -- `tilstand.py` i Kjerne, kantene i grafen og FR-409 i kartet

**Acceptance Criteria:**
- Gitt koden fra `baseline_commit`, når de nye testene kjøres, så feiler de (modulen og `er_boersdag` finnes ikke).
- Gitt hver mutant i Design Notes, lagt inn én om gangen og satt tilbake mellom hver, når hele testsettet kjøres, så feiler testene for det kontrollpunktet.
- Gitt hele testsettet lokalt og i CI, så er det grønt begge steder, og antallet før (614) og etter står i commit-meldingene og squash-meldingen.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

**Hvorfor en kjernefunksjon og ikke en lesemetode i adapteren.** Skillet er logikk over to ting som alt finnes: raden (`les`) og kalenderen (`boersdag.py`). I kjernen testes det uten SQLite, og porten forblir `skriv` og `les`, så AD-7 og protokolltesten fra 1.6 står urørt. En lesemetode i adapteren ville lagt kalenderlogikk i skallet og krevd at hver ny adapter gjentok den. `idag` kommer inn som argument, som `dag` i `innevaerende_boersdag`, så funksjonen aldri leser klokka. Kalleren regner den med `norsk_dato`.

**Hvorfor `idag` og ikke inneværende børsdag.** En lørdag er inneværende børsdag fredagen. Med den som grense ville lørdagen selv regnes som fremtid og reise, mens den er en dag som ikke finnes.

**Mutanter, én om gangen:**
- T1, styrke 0 som fravær: `innhold is None or innhold.styrke == 0` gir fravær.
- T2, `None` for begge (storyens «ville feilet hvis»): returner `None` når raden mangler.
- T3, byttet: ingen rad på en børsdag gir `IKKE_BOERSDAG`.
- T4, grunn som fravær: en `Grunn` behandles som ingen rad.
- T5, egen kalender: `er_boersdag` ser bare på ukedagen (langfredag og julaften feiler).
- T6, fremtiden godtas: fjern kontrollen `dato > idag`.
- T7, `er_boersdag` gjetter utenfor lista: fjern årsvakten.
- T8, kalenderen før raden: en rad på en dag `er_boersdag` sier er stengt, gir `IKKE_BOERSDAG`.

**Arbeidsflyt, som 1.6:** grenen `1-7` fra `main`, mellomcommits som pushes, PR mot `main`, gjennomgang med tre lag, stopp før flettingen og vent på ja, squash med `Co-authored-by: Joakim Lund`. Etter flettingen: «Ferdig»-linje under 1.7 i `epics.md`, spesifikasjonen `done` og 1-7 til `review`.

## Verification

**Commands:**
- `uv run pytest -q` -- forventet: grønt, 614 + nye tester, telt
- Mutantene over, én om gangen -- forventet: testene for punktet feiler
