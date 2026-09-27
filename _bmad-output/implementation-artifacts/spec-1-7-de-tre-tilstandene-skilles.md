---
title: 'Story 1.7: De tre tilstandene skilles'
type: 'feature'
created: '2026-09-27'
status: 'in-review'
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
- [x] `tests/test_tilstand.py` -- matrisen, med `les` fra `SqliteVurderingslager` i minnet for svar, grunn og ikke kjørt, og fire forskjellige verdier for de fire utfallene -- testene først
- [x] `tests/test_boersdag.py` -- `er_boersdag`: hverdag, lørdag, hver dag i `STENGT`, 2026-04-01, 2026-01-01 og år utenfor -- samme liste som 1.6
- [x] `src/boersdag.py` -- `er_boersdag`
- [x] `src/tilstand.py` -- `Art` (StrEnum: `SVAR`, `GRUNN`, `IKKE_KJOERT`, `IKKE_BOERSDAG`), `Tilstand` (frozen dataclass: `art`, `innhold`) og `tilstand`
- [x] `tests/test_konsumentene.py` -- `tilstand.py` i `KJERNEMODULER`
- [x] Spinen -- `tilstand.py` i Kjerne, kantene i grafen og FR-409 i kartet

**Acceptance Criteria:**
- Gitt koden fra `baseline_commit`, når de nye testene kjøres, så feiler de (modulen og `er_boersdag` finnes ikke).
- Gitt hver mutant i Design Notes, lagt inn én om gangen og satt tilbake mellom hver, når hele testsettet kjøres, så feiler testene for det kontrollpunktet.
- Gitt hele testsettet lokalt og i CI, så er det grønt begge steder, og antallet før (614) og etter står i commit-meldingene og squash-meldingen.

## Implementation Notes

**27.09, grenen `1-7`.** Bygget direkte i økta, ikke av en egen implementeringsagent, av samme grunn som i 1.6: testene først og mutantene én om gangen. Mellomcommitene er pushet, som planen sier. Commitene: `aba17c1` (koden og testene), `dfdda5f` (spinen), `c638b72` (testen for en lørdag i morgen), `b3aae85` (rettingene etter gjennomgangen) og `309ea5c` (spinen etter gjennomgangen).

- **Tester:** 614 før. 661 etter `aba17c1`: 26 i `tests/test_tilstand.py`, 18 i `tests/test_boersdag.py` og 3 i `tests/test_konsumentene.py`, fordi `KJERNEMODULER` også går inn i de to vaktene mot EODHDs feltnavn. 662 etter `c638b72`. Matrisesjekken fant at raden «også for en lørdag i morgen» manglet en test. 665 etter rettingene: 4 nye, og testen for første kjøring flyttet inn i lageret.
- **Mot koden uten modulen:** `tests/test_tilstand.py` og `tests/test_boersdag.py` feilet ved innsamlingen med `ImportError` (`er_boersdag` fantes ikke), som ventet.
- **Første kjøring av testene** ga én feil i testen, ikke i koden: julaften 2026-12-24 lå etter `IDAG` (30.09) og ble regnet som fremtid. Testen bruker nå 2026-12-31 som dagens dato.
- **`innevaerende_boersdag` er ikke endret.** Regelen for en børsdag står derfor to steder. En test prøver at de to er enige om hver dag i `DEKKEDE_AAR`, unntatt 1. januar (BH1).
- **Mutanter, én om gangen, mot hele testsettet, med `git checkout` mellom hver.** Første runde, mot `aba17c1`:
  - T1, styrke 0 som fravær: 3 tester feiler, blant dem testen for styrke 0 og testen for fire forskjellige verdier
  - T2, `None` for begge fravær: 14 feiler
  - T3, fraværene byttet: 11 feiler
  - T4, grunn som fravær: 5 feiler, blant dem de tre grunnene
  - T5, egen kalender som bare ser på ukedagen: 4 feiler (langfredag, julaften og de to årene utenfor lista)
  - T6, fremtiden godtas: de 3 testene for fremtid feiler
  - T7, `er_boersdag` gjetter utenfor lista: 4 feiler, i `test_boersdag.py` og `test_tilstand.py`
  - T8, kalenderen før raden: testen for at raden går foran feiler

  Ingen mutant overlevde.
- **Andre runde, mot `b3aae85`:** T1–T8 på nytt, og to nye. Alle ti ble fanget.
  - T9, datoen kontrolleres før typen: testen for feil innhold med en dato etter i dag feiler
  - T10, `tilstand.py` importerer `lagring_sqlite`: vakten mot skallet i `test_konsumentene.py` feiler
## Spec Change Log

## Review Triage Log

Tre lag gjennomgikk diffen for `src/`, `tests/` og spinen siden `baseline_commit` den 27.09: Blind Hunter (BH), bare diffen, Edge Case Hunter (ECH), med spesifikasjonen som påstander, og Verification Gap (VG). VG fant ingen hull i verifikasjonen, men har to andre funn.

| # | Funn | Dom | Bevis | Rute |
|---|---|---|---|---|
| BH1 | Regelen for en børsdag står to steder, og ingen test binder `er_boersdag` til `innevaerende_boersdag` | medium | `innevaerende_boersdag` skulle ikke endres. T5 endrer bare `er_boersdag` | patch: en test over hver dag i `DEKKEDE_AAR` |
| BH2 | Ingen test hindrer at kjernen importerer skallet, selv om spinen sier det for `tilstand.py` | medium | `FORBUDTE_MODULER` var `sqlite3` og `pathlib` | patch: skallet, `requests` og `flask` i `FORBUDTE_MODULER`, og testen har nytt navn. Mutant T10 fanges |
| BH3 | `Tilstand` godtar selvmotsigende verdier, som `Tilstand(Art.SVAR)` | low | Riktig, men bare `tilstand` lager dem, og ingen kaller finnes | avvist: lite sannsynlig, og en vakt legger til greiner |
| BH4 | Kalleren kan ikke se om `IKKE_KJOERT` er et endelig hull | low | Riktig, men det er avgjort 27.09: `IKKE_KJOERT`, med forklaringen i docstringen | avvist: beslutning i den låste blokken |
| BH5 | Spinen sier «tre tilstander», men `Art` har fire | low | Lagtabellen og treet sa tre | patch: «fire utfall» og punkt 24 i spinen |
| BH6 | AD-7-notatet nevner ikke de to feilveiene | low | Riktig | patch: `ValueError` for fremtid, også med rad, og `UtenforKalenderen` |
| BH7 | Datoen kontrolleres før innholdet, så feil innhold med en dato fram i tid gir `ValueError` | low | Kjørt: `tilstand("symbol_feilet", 2026-10-01, 2026-09-30)` ga `ValueError` | patch: innholdet først, og docstringen sier rekkefølgen. Mutant T9 fanges |
| BH8 | Testen for første kjøring går ikke gjennom lageret | low | Den var lik testen for en børsdag uten rad | patch: testen skriver en rad og leser dagen før gjennom lageret |
| BH9 | Lageret er ikke prøvd på en helligdag | low | Bare lørdag gikk gjennom lageret | patch: langfredag gjennom `les` |
| BH10 | Typekontrollen av en dato står tre steder | low | Riktig | avvist: en felles hjelper gir nytt grensesnitt i `boersdag.py` |
| BH11 | AD-20 i kartet, selv om `tilstand.py` ikke regner i Oslo-tid | false | Raden gjelder også FR-408, og `skriv` regner dagen med `norsk_dato` (AD-20) | avvist |
| ECH1 | `Tilstand` godtar selvmotsigende verdier | low | Samme som BH3 | avvist: under BH3 |
| ECH2 | Samme verdi for dagens rad som mangler og et endelig hull | low | Samme som BH4 | avvist: under BH4 |
| ECH3 | `ValueError` om fremtid skjuler `TypeError` | low | Samme som BH7 | patch: under BH7 |
| VG1 | Ingen test hindrer at kjernen importerer skallet | medium | Samme som BH2 | patch: under BH2 |
| VG2 | Ingen test for at `er_boersdag` og `innevaerende_boersdag` er enige | medium | Samme som BH1 | patch: under BH1 |
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
