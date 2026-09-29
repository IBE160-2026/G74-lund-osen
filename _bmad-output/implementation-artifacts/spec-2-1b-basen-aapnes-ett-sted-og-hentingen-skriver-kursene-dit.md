---
title: 'Story 2.1b: Basen åpnes ett sted, og hentingen skriver kursene dit'
type: 'feature'
created: '2026-09-29'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'b613f698dd9fa4e5e4455309354e573a80037167'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-1-boersdag-i-oslo-tidsstempel-i-utc.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Hentingen skriver bare et øyeblikksbilde i `data/`. Basen brukes ikke av noen inngang, ingen funksjon åpner den, og `migrer()` kalles bare fra testene. Et øyeblikksbilde som alt finnes, kan ikke komme inn i basen uten en ny henting.

**Approach:** To konstanter gir stiene, og én funksjon åpner basen. Hentingen skriver fila først og så kursene til basen med samme `hentet`. En innlesing uten nett tar et øyeblikksbilde som finnes, samme vei. Leseren for sidene ser i `data/raa/`.

## Boundaries & Constraints

**Always:**
- `lagring_fil.RAA_KATALOG = DATA_KATALOG / "raa"` og `lagring_sqlite.BASE_STI = DATA_KATALOG / "db" / "ose.db"`. Ingen annen kode skriver stiene.
- `lagring_sqlite.aapne_base(sti) -> sqlite3.Connection`: lager mappa, kobler til og kjører `migrer(tilkobling, MIGRASJONSKATALOG)`. Feiler migreringen, lukkes tilkoblingen, og feilen går videre. Ingen annen kode i `src/` kaller `sqlite3.connect`.
- Rekkefølgen i `kjoer`: fila skrives først (AD-6), så basen. Hvert symbol i `resultat.serier` får `erstatt_serie(symbol, serie_fra_eodhd(rader), oeyeblikk)`. Et symbol i `feil` rører ikke basen (AD-15).
- Feiler basen etter at fila er skrevet, står fila, kjøringen skriver hva som feilet og hvordan fila leses inn, og avslutter med kode 1. Feiler ett symbol (`ValueError` fra `erstatt_serie`), skrives de andre, og symbolet nevnes.
- Innlesingen går gjennom samme funksjon som hentingen, skriver bare `kurs` og `kursserie`, aldri `vurdering` (AD-7), leser ingen nøkkel og gjør ingen kall.
- Testene rører aldri `data/`: en autouse-fixture i `tests/conftest.py` peker `RAA_KATALOG` og `BASE_STI` mot `tmp_path`.
- Regel 6, 10 og 16: ingen nett, ingen ekte data i CI. `src/fetch_prices.py` kjøres ikke.

**Never:** Webserveren mot basen (2.2). Målingene (2.1c). Vurderingen (2.5). Ingen egen migrasjonskommando. Ingen reserve der leseren også ser i `data/`.

## Beslutninger (godkjent 29.09 kl. 12:04)

- **`kjoer` tar `base_sti` som påkrevd argument**, uten standardverdi, så ingen test kan skrive til `data/db/` ved et uhell. `main` gir `BASE_STI`.
- **Innlesingen er et flagg:** `fetch_prices.py --les-inn <fil>`. Uten flagg er alt som før. Funksjonen `les_inn(fil, base_sti, skriv)` leser med `SnapshotKilde` og `SnapshotLeser`, og `hentet` kommer fra fila.
- **G10: porten sjekker symbolet.** `kontroller_skriving` får symbolet og avviser alt som ikke står i `AKSJEUNIVERS` med `ValueError`, før noe lagres. Da oppfører `MinneKurslager` og `SqliteKurslager` seg likt, og en test mot minnelageret kan ikke godta `EQNR.OL` som basen avviser. Triggerne fra `0003` står som vakten i basen. **G11** (`SqliteVurderingslager.skriv` slipper ut `sqlite3`-feil) står igjen for 2.5, der vurderingen skrives.
- **To migratorer som overlapper:** to tråder, hver med sin tilkobling til samme fil. Den første holder transaksjonen åpen inne i en migrasjon til den andre har startet. Begge skal lykkes, og migrasjonen kjøres én gang.
- **Flyttingen på PC-en,** utenfor git, etter flettingen:
  - Før: `data/kurser-raa-2026-09-22.json`, `…-23.json` og `…-24.json`.
  - Etter: `data/raa/kurser-raa-2026-09-22.json`, `…-23.json` og `…-24.json`.
  - Sjekk: sha256 er lik før og etter. `nyeste_snapshot(RAA_KATALOG)` gir `kurser-raa-2026-09-24.json`, som `nyeste_snapshot(data/)` gir i dag. Seriene for alle 15 er like før og etter, sammenlignet som hash. Ingen kurser skrives ut.
  - Målingsfilene (`gjentak-`, `kall21-`, `newsweb-felter-`, `nyhetstest-`, `relevans-`, `signaltest-`, `volumsjekk-`) blir liggende i `data/`.
- **Kontrollregningen,** utenfor git: et skript i scratchpad importerer `les_inn` og leser det nyeste ekte øyeblikksbildet inn i en midlertidig base, ikke `data/db/ose.db`. Det skriver bare antall rader og første og siste dato per symbol.

- **Svar 29.09 kl. 12:04, spørsmål 1 (A):** sammenlignes per symbol, filens `hentet` mot `sist_hentet(symbol)`. Lik tid godtas. Et symbol der fila er eldre, hoppes over med en melding som nevner fila, symbolet og begge tidene. De andre skrives, og kjøringen ender med kode 1.
- **Svar 29.09 kl. 12:04, spørsmål 2 (A):** Claude flytter de tre `kurser-raa-*.json` til `data/raa/` i samme økt rett etter flettingen, med sjekken over, og Utført-linjen fører filnavnene.
- **Storyen bygges samlet** (29.09). Viser det seg underveis at den må deles, stoppes det, og gruppen spørres. Den nye storyen heter da 2.1d.
- **Overlapptesten avhenger ikke av tilfeldig timing:** overlappen tvinges, for eksempel med en pause inne i transaksjonen til den første til den andre har startet. Den kjøres 50 ganger lokalt før pull requesten, og antallet som besto, føres.
- **Standardstiene slås opp ved kallet:** `nyeste_snapshot(katalog=None)` og `nyeste_leser(katalog=None)` bruker `RAA_KATALOG` slik den er når funksjonen kalles, ikke når modulen lastes. En test viser at autouse-fixturen faktisk flytter standardstien.
- **`--les-inn` skriver ingen kurser ut,** bare antall serier, symbolene og datoene (regel 16).
- **`src/fetch_prices.py` kjøres ikke, heller ikke med `--les-inn`.** Kontrollregningen importerer funksjonen fra et skript i scratchpad.

## I/O & Edge-Case Matrix

| Scenario | Tilstand | Forventet |
|---|---|---|
| Første henting | `raa/` og `db/` mangler | begge lages; fil og 15 serier i basen, `sist_hentet` = øyeblikket |
| Ett symbol feilet | `DNB` i `feil` | `DNB` uendret i basen (ny: ingen rad; gammel: gammel serie og tid) |
| Basen kan ikke åpnes | `base_sti` er en mappe | fila står, melding med `--les-inn`, kode 1 |
| Ett symbol avvises av basen | `erstatt_serie` gir `ValueError` | de andre skrives, symbolet nevnes |
| Fire dagers opphold | basen mangler 4 dager | etter neste henting er de der; 15 kall |
| Innlesing | laget øyeblikksbilde, tom base | 15 serier, `vurdering` tom, ingen kall, ingen nøkkel lest |
| Innlesing to ganger | samme fil | samme innhold, ingen feil |
| Eldre øyeblikksbilde | filens `hentet` < `sist_hentet(DNB)` | `DNB` hoppes over med melding (fil, symbol, begge tider), de andre skrives, kode 1 |
| Symbol utenfor universet | `erstatt_serie("EQNR.OL", …)` i begge lagrene | `ValueError`, ingenting lagret |
| To migratorer overlapper | to tilkoblinger, samme fil | begge lykkes, 0001 kjørt én gang |
| Leseren | `kurser-raa-*.json` i `raa/` | sidene viser samme kurser som fra `data/` før |

</frozen-after-approval>

## Code Map

- `src/lagring_fil.py:25–26, 118, 156–164` -- `DATA_KATALOG`; ny `RAA_KATALOG`; `nyeste_leser` uten argument leser `RAA_KATALOG` når den kalles.
- `src/lagring_sqlite.py:31` -- `MIGRASJONSKATALOG`; ny `BASE_STI` og `aapne_base`. Modulteksten (linje 7–14) sier at story 3.1 avgjør hvem som kaller `migrer()`, og rettes.
- `src/migrering.py:89–139` -- `migrer`, `BEGIN IMMEDIATE` på linje 120. Modulteksten (linje 18–20) rettes på samme måte.
- `src/kursdata.py:162` -- `kontroller_skriving` får `symbol`; begge `erstatt_serie` sender det.
- `src/fetch_prices.py:214, 274` -- `kjoer` (ny `base_sti`, basen etter fila), ny `les_inn`, `main` med `--les-inn`. Bruker `RAA_KATALOG` og `BASE_STI`.
- `src/app.py:28–35` -- `hent_leser` kaller `nyeste_leser()` og følger med uten endring.
- Tester som endres: kallene til `kjoer` i `tests/test_fetch_prices.py` får `base_sti` (ny parameter); G12-testen peker `RAA_KATALOG` og `BASE_STI` i stedet for `DATA_KATALOG`; `tests/test_app.py:303, 427, 435` peker `RAA_KATALOG`; `tests/test_aksje.py:320` venter portens melding, fordi porten nå avviser `EQNR.OL` før SQL-en (triggeren er fortsatt prøvd med rå SQL i samme fil).
- `tests/test_migrering.py:438–470` -- der står grunnen til at overlapptesten ble utsatt. Den nye testen legges ved siden av.
- `_bmad-output/implementation-artifacts/deferred-work.md:17–19` -- punktet om to migratorer får `resolved`.
- `README.md` -- «Kom i gang» og mappestrukturen nevner `data/`; rettes i samme commit som stiene (regel 19).

## Tasks & Acceptance

**Execution:**
- [x] `src/lagring_fil.py`, `src/lagring_sqlite.py` -- konstantene og `aapne_base`.
- [x] `src/kursdata.py`, `src/lagring_sqlite.py` -- symbolet i `kontroller_skriving` (G10).
- [x] `src/fetch_prices.py` -- basen i `kjoer`, `les_inn`, `--les-inn`, eldre-regelen (svar A).
- [x] `tests/conftest.py` -- autouse-fixturen for stiene.
- [x] `tests/test_fetch_prices.py`, `tests/test_lagring_sqlite.py`, `tests/test_migrering.py`, `tests/test_kurslager.py`, `tests/test_app.py`, `tests/test_aksje.py` -- matrisen, overlapptesten og endringene over.
- [x] `tests/test_konsumentene.py` -- vakt: `sqlite3.connect` bare i `lagring_sqlite.aapne_base`.
- [x] `README.md` (linje 53, 66, 74 og 82 nevner `data/`), spinen (AD-16 «Bygget», mappetreet uten `[flyttes hit i 2.1b]`, og en merknad ved AD-21 linje 327, som sier at porten avgjøres i 2.5, mens epics.md flyttet den til 2.1b 28.09), `deferred-work.md`, `kodegjennomgang-epic-1.md` (merknad ved G10).

**Acceptance Criteria (kontrollpunktene i epics.md, hvert med en mutant, én om gangen, satt tilbake fra kopi):**
- K1 Stiene: fila i `raa/`, basen i `db/ose.db`. *M1:* `kjoer` skriver fila i `DATA_KATALOG`.
- K2 Én åpning: gitt en sti uten mappe, når `aapne_base` kalles, så finnes mappa og basen står på siste versjon. *M2:* uten `mkdir`. *M3:* uten `migrer`. *M4:* `fetch_prices` kaller `sqlite3.connect` selv (fanget av vakten).
- K3 `erstatt_serie` for hvert hentet symbol, med samme `hentet`. *M5:* `hentet` fra klokka i stedet for øyeblikket. *M6:* symbolet som feilet, skrives likevel.
- K4 Fila står når basen feiler. *M7:* basen skrives før fila.
- K5 Innlesingen: samme vei, bare `kurs`, ingen kall. *M8:* innlesingen leser nøkkelen.
- K6 Eldre øyeblikksbilde (svar A). *M9:* sammenligningen fjernes.
- K7 G10. *M10:* symbolsjekken fjernes fra `kontroller_skriving`.
- K8 Overlapp. *M11:* `BEGIN IMMEDIATE` blir `BEGIN`.
- K9 Opphold fylt uten ekstra kall. *M12:* `kjoer` skriver bare symboler som ikke finnes i basen.
- K10 Leseren. *M13:* `nyeste_leser` leser `DATA_KATALOG`.

## Design Notes

**Hvorfor fila først:** kallene er brukt når svaret kommer. Fila er rådata som aldri skrives om (AD-6), og den kan alltid leses inn igjen uten kall. Basen er gjenoppbyggbar for `kurs` (AD-7, «Merk»). Omvendt rekkefølge ville latt en feil i basen koste dagens rådata.

**Antall tester:** før 907 i CI (891 passed og 16 skipped lokalt). Etter om lag 907 + 25 ≈ 932 i CI. De nøyaktige tallene føres i commit-meldingen.

**Én økt:** bygges samlet (29.09). Må den deles, stoppes det og spørres; den nye storyen heter 2.1d.

## Verification

**Commands:**
- `uv run pytest -q` -- lokalt grønn; CI på PR-en grønn, ingen TZ-test hoppet over, med kjørings-ID.
- `grep -rn "sqlite3.connect" src/` -- bare i `aapne_base`.

## Implementation Notes

- **Tester lokalt (Windows):** før 891 passed, 16 skipped (907). Etter 923 passed, 16 skipped (939), `uv run pytest -q`. De 16 som hoppes over, er TZ-testene fra 2.1. Anslaget var om lag 932; det ble 939. CI er ikke kjørt.
- **`kjoer(data_katalog, base_sti, oeyeblikk, api_nokkel, hent, skriv)`:** `base_sti` er andre posisjonsargument, påkrevd. Veien til basen er én funksjon, `skriv_til_basen(base_sti, serier, hentet, fil, skriv) -> bool`, som både `kjoer` og `les_inn` kaller. Den åpner basen med `aapne_base`, sammenligner `hentet` med `sist_hentet` per symbol (svar A), fanger `ValueError` per symbol og `sqlite3.Error`, `OSError`, `MigrasjonsFeil` og `RuntimeError` som «basen feilet».
- **Valg som ikke står i den låste delen:** (1) et symbol basen avviser (`ValueError`), gir også kode 1, som eldre-regelen, fordi kjøringen da ikke skrev alt. (2) `les_inn` går gjennom alle symbolene i fila, ikke bare universet; et ukjent symbol stoppes av porten (G10), nevnes, og gir kode 1. En serie i fila som ikke kan leses, nevnes og hoppes over uten kode 1. (3) Fixturen i `conftest.py` peker i tillegg `DATA_KATALOG` mot `tmp_path/data`, så en feil som bruker den (M1, M13), havner i `tmp_path` og ikke i `data/`. (4) Docstringen til `SqliteVurderingslager` nevnte `sqlite3.connect(":memory:")`; den er omskrevet, så `grep sqlite3.connect src/` bare gir `aapne_base`.
- **Mutantene,** én om gangen, satt tilbake fra kopi (sha256 sjekket), hele `tests/` hver gang, og `data/` uendret etterpå (liste, størrelse og mtime):
  - M1 (`main` gir `DATA_KATALOG`): 1 feilet (G12).
  - M2 (uten `mkdir`): 14 feilet.
  - M3 (uten `migrer`): 52 feilet.
  - M4 (`fetch_prices` kaller `sqlite3.connect` selv, og migrerer selv): 1 feilet (vakten).
  - M5 (`hentet` fra klokka): 6 feilet.
  - M6 (symbolet som feilet, skrives likevel): 2 feilet.
  - M7 (basen før fila): 1 feilet.
  - M8 (innlesingen leser nøkkelen): 2 feilet.
  - M9 (sammenligningen fjernet): 1 feilet.
  - M10 (symbolsjekken fjernet): 9 feilet.
  - M11 (`BEGIN IMMEDIATE` → `BEGIN`): 1 feilet (overlapptesten).
  - M12 (bare symboler som ikke finnes i basen): 3 feilet.
  - M13 (`nyeste_leser` leser `DATA_KATALOG`): 4 feilet.
- **Overlapptesten** kjørt 50 ganger lokalt, hver i sin egen `pytest`-prosess: 50 besto.
- **Kontrollregningen** (skript i scratchpad, ikke `data/db/ose.db`): `les_inn` på `kurser-raa-2026-09-24.json` i en midlertidig base ga 15 serier, 250 rader per symbol, første dato 2025-09-25 og siste 2026-09-24 for alle, 0 vurderingsrader og én felles `sist_hentet`. `data/db/` ble ikke laget.
- **Ikke gjort her:** flyttingen av de tre `kurser-raa-*.json` til `data/raa/` (etter flettingen, svar 2), CI på PR-en, commitene og dagsfila (regel 18). Til flyttingen er gjort, finner siden ingen kursdata, fordi leseren bare ser i `data/raa/`.

## Spec Change Log

## Review Triage Log
