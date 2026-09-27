---
title: 'Story 1.6: Vurderingslager med datoavvisning'
type: 'feature'
created: '2026-09-27'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '7dec7410151bc695e6c48e77b4d623d877cec9eb'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** FR-408 krever at dagens vurdering lagres per aksje, og AD-7 at den ikke kan skrives om i ettertid. Det finnes verken tabell, port eller børsdagsfunksjon, og punkt 3 og 24 i `prd.md` §8, som bestemmer formen, ble lukket 27.09.

**Approach:** En ren kjernefunksjon for inneværende børsdag (punkt 3), en port `Vurderingslager` med bare `skriv` og `les`, migrasjon `0002` og en SQLite-adapter som avviser enhver annen dato enn inneværende børsdag i Europe/Oslo, med klokka injisert. En rad har enten vurdering eller grunn (punkt 24). Kilde: story 1.6 i `epics.md` slik den står 27.09.

## Boundaries & Constraints

**Always:**
- AD-1: `boersdag.py` er kjerne, ingen I/O. AD-7: porten har bare `skriv` og `les`. AD-16: tabellen lages bare av `0002`. AD-18: ingen fremmednøkkel til `kurs`. AD-20: datoen regnes i Europe/Oslo.
- Stengte dager står ett sted i koden, med henvisning til `docs/kilder-og-rettigheter.md`, seksjonen Handelskalenderen. En dato som krever en dag utenfor 2026, reiser.
- Regel 6: ingen nett i testene. Hver test lager egen base i minnet eller under `tmp_path`.

**Never:**
- Ingen endring i `0001_kurs.sql`, `Kurslager`, `Kursrad` eller løperen.
- Ingen kaller av `Vurderingslager` i produksjonskoden. Det er story 2.5.
- Ingen avlesning av de tre tilstandene. Det er story 1.7.
- Ingen kolonne for relevante meldinger i `0002` (se Beslutninger).

## Beslutninger (godkjent 27.09 kl. 15:13)

- **Modulen heter `src/boersdag.py`**, i kjernen. Én offentlig funksjon `innevaerende_boersdag(dag: date) -> date`: siste børsdag på eller før `dag`. Lista `STENGT` (ti datoer) står i modulen. `norsk_dato(oeyeblikk: datetime) -> date` gjør omregningen til Europe/Oslo og avviser et tidspunkt uten sone. 1.7 og 2.3 bruker samme funksjon.
- **Porten er `src/vurderingsdata.py`**, en løvnode som `kursdata.py`: `Vurdering` (styrke, retning, trend, bevegelse, interesse, slutt, justert_slutt), `Grunn` (StrEnum med tre verdier) og protokollen `Vurderingslager` med `skriv(symbol, dato, innhold: Vurdering | Grunn) -> bool` og `les(symbol, dato) -> Vurdering | Grunn | None`. Porter importerer ikke kjernen (grafen i spinen), så datokontrollen ligger i adapteren.
- **Ingen `MinneVurderingslager`.** Adapteren tar en `sqlite3.Connection`, så testene og 2.5 bruker `sqlite3.connect(":memory:")`. Da finnes reglene for overskriving ett sted.
- **Grunnene er rader i en egen tabell `grunn`, ikke en `CHECK`.** Triggere på `INSERT` og `UPDATE` avviser en ukjent grunn. En ny grunn er en `INSERT INTO grunn` i en ny migrasjon: ingen `DROP`, ingen ombygging. Prøvd i minnet 27.09.
- **«Relevante meldinger» kommer senere**, som en kolonne som kan være tom (`ALTER TABLE vurdering ADD COLUMN`). `NULL` betyr da «ikke registrert», og holdes adskilt fra «ingen relevante». Prøvd i minnet 27.09: radene står uendret, `integrity_check` er `ok`, og `CHECK` og triggere virker etterpå.
- **En grunn over en vurdering samme dag ignoreres, og `skriv` returnerer `False`.** Den reiser ikke, fordi en kjøring der ett symbol feiler, ikke skal stoppe (AD-15). En vurdering skriver over en grunn og over en vurdering. En grunn skriver over en grunn.
- **`symbol` må stå i `AKSJEUNIVERS`**, så `EQNR.OL` i stedet for `EQNR` stoppes ved skrivingen.
- **Årsgrensen gjelder dagene funksjonen faktisk trenger** (endring 2). En dag i 2026 som selv er børsdag, gis tilbake uten at noe utenfor 2026 slås opp: 2026-01-02 gir 2026-01-02. Den reiser bare når dagen selv, eller en dag den må gå tilbake til, ligger utenfor 2026.
- **`CHECK`-en i `0002` dekker alle vurderingsfeltene** (endring 4): `styrke`, `retning`, `trend`, `bevegelse`, `interesse`, `slutt` og `justert_slutt`. Er `grunn` tom, er alle sju satt. Er `grunn` satt, er alle sju `NULL`, også kursfeltene. En rad med grunn har altså ingen kurs, heller ikke når kjøringen hadde en kurs fra en annen dag.
- **De to testene i `tests/test_lagring_sqlite.py` som legger til en migrasjon** (endring 1), bruker neste ledige nummer, `siste_versjon(MIGRASJONSKATALOG) + 1`, og ikke et fast nummer, så de ikke brekker igjen når 4.3 legger til `ki_logg`. De sjekker det samme som før; bare numrene endres.
- **Lagtabellen i spinen sier hvorfor `Vurderingslager` ikke har noe minnelager** (endring 5): reglene for overskriving skal stå ett sted, og testene bruker SQLite i minnet.
- **Lengden på spesifikasjonen er godtatt.**

## I/O & Edge-Case Matrix

| Tilstand | Forventet |
|---|---|
| `innevaerende_boersdag`: lørdag 2026-09-26 | 2026-09-25 |
| 2026-04-06 (2.påskedag) | 2026-04-01, over hele påsken |
| 2026-12-24 / 2026-12-31 | 2026-12-23 / 2026-12-30 |
| 2026-04-01 (halv dag) | 2026-04-01 |
| 2026-01-01 | Reiser: krever 2025-12-31 |
| 2026-01-02 | 2026-01-02, reiser ikke |
| 2027-01-04 og 2025-12-15 | Reiser: utenfor 2026 |
| `skriv` klokka 2026-09-24T22:30Z (00:30 fredag i Oslo, sommertid) | 25.09 godtas, 24.09 reiser |
| `skriv` klokka 2026-12-10T23:30Z (00:30 fredag i Oslo, vintertid) | 11.12 godtas, 10.12 reiser |
| `skriv` en lørdag | Fredagen godtas, lørdagen reiser |
| `skriv` i går, i morgen, eller et tidspunkt uten sone fra klokka | Reiser |
| To `skriv` med samme `(symbol, dato)` | Én rad, den siste vinner |
| Grunn etter vurdering samme dag | Vurderingen står, `skriv` gir `False` |
| Vurdering etter grunn / grunn etter grunn | Den nye står |
| Rad med både vurdering og grunn, ingen av delene, eller et av de sju vurderingsfeltene mangler eller er satt ved siden av en grunn | `CHECK` stopper den i basen |
| Grunn som ikke står i `grunn` | Triggeren stopper den, også via upsert |
| `erstatt_serie` på symbolet etterpå | Vurderingen og kursen i den er uendret |

</frozen-after-approval>

## Code Map

- `src/migrasjoner/0001_kurs.sql` -- mønster for kommentarhodet. Endres ikke. Semikolon i kommentarer unngås i `0002`.
- `src/migrering.py` -- løperen. `CREATE TRIGGER … BEGIN … END;` er lov (1.5b, b). Endres ikke.
- `src/lagring_sqlite.py` -- `SqliteKurslager`. Versjonskontrollen i `__init__` flyttes til en felles hjelper og brukes av begge adapterne. `erstatt_serie` endres ikke.
- `src/kursdata.py` -- `AKSJEUNIVERS` og mønsteret for verdityper (`Kursrad.__post_init__`, `UgyldigKursrad`). Endres ikke.
- `src/signalberegning.py` -- `POSITIV`, `NEGATIV`, `BLANDET`, `INGEN`. En test binder portens retninger til disse, så de ikke glir fra hverandre.
- `tests/test_lagring_sqlite.py:186` og `:209` -- legger til `0002_ny.sql` ved siden av katalogen, som kolliderer med `0002_vurdering.sql`. Skrives om til neste ledige nummer fra `siste_versjon(MIGRASJONSKATALOG)`, også i de forventede meldingene. Ellers uendret.
- `tests/test_lagring_sqlite.py:51` -- navnet sier «versjon 1 med to tabeller», og testen sjekker `>= 1`. Står.
- `tests/test_konsumentene.py:25` -- `KJERNEMODULER` får `boersdag.py`, og portvakten gjelder også `vurderingsdata.py`.
- `tests/test_tidssone.py` -- tzdata er på plass, og 00:30-tilfellet er alt vist for sonen.
- Spinen -- lagtabellen, grafen, AD-7 og Deferred («Kilde for handelskalenderen», «Skjemaendring på et uerstattelig lager»).

## Tasks & Acceptance

**Del 1, børsdagene:**
- [ ] `src/boersdag.py` -- `STENGT`, `innevaerende_boersdag`, `norsk_dato` og `UtenforKalenderen(ValueError)`.
- [ ] `tests/test_boersdag.py` -- matrisen over, med 2026-01-02, pluss at `STENGT` er de ti datoene og at `datetime` avvises som dag. `norsk_dato` prøves 00:30 i både sommertid og vintertid.
- [ ] `tests/test_konsumentene.py` -- `boersdag.py` i `KJERNEMODULER`.

**Del 2, lageret:**
- [ ] `src/migrasjoner/0002_vurdering.sql` -- `grunn` med tre rader, `vurdering` med `PRIMARY KEY (symbol, dato)`, enten/eller-`CHECK` over alle sju vurderingsfeltene og to triggere.
- [ ] `src/vurderingsdata.py` -- `Vurdering`, `Grunn`, `Vurderingslager`, `UgyldigVurdering`.
- [ ] `src/lagring_sqlite.py` -- `SqliteVurderingslager(tilkobling, klokke)` med upsert og `WHERE excluded.grunn IS NULL OR vurdering.grunn IS NOT NULL`.
- [ ] `tests/test_vurderingslager.py` -- matrisen, protokollen, `grunn` lik `Grunn`, retningene lik `signalberegning`, og validering av `Vurdering`.
- [ ] `tests/test_lagring_sqlite.py` -- de to testene over bruker neste ledige nummer.
- [ ] Spinen -- `boersdag.py` i Kjerne, `vurderingsdata.py` i Porter med hvorfor det ikke finnes noe minnelager, nye kanter i grafen, og de to Deferred-radene.

**Acceptance Criteria:**
- Gitt koden fra `baseline_commit`, når de nye testene kjøres, så feiler de (modulene finnes ikke).
- Gitt hver mutant i Design Notes, lagt inn én om gangen og satt tilbake mellom hver, når hele testsettet kjøres, så feiler testene for det kontrollpunktet med forventet melding.
- Gitt hele testsettet lokalt og i CI, så er det grønt begge steder, og antallet før (468) og etter står i squash-meldingen.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

**Mutanter, én om gangen:**
- K1, eldre dato reiser: fjern datokontrollen i `skriv`.
- K1/«ville feilet hvis», UTC: bruk `klokke().astimezone(timezone.utc).date()`. 00:30-testene feiler, i sommertid og i vintertid.
- K2, siste vinner: vanlig `INSERT` uten `ON CONFLICT`.
- K3, ingen `slett`/`endre`: legg `endre` til protokollen.
- K4, overlever `erstatt_serie`: la `erstatt_serie` også slette fra `vurdering`.
- K5, laget av `0002`: flytt `CREATE TABLE vurdering` fra `0002` til adapterens `__init__`.
- K6, grunn over vurdering: fjern `WHERE` i upserten. Vurdering over grunn: `WHERE excluded.grunn IS NULL AND vurdering.grunn IS NULL`. Ukjent grunn: fjern triggerne. Enten/eller: fjern `CHECK`.
- Børsdagene: fjern 2026-04-06 fra `STENGT` (påsketesten), legg 2026-04-01 til (halv dag), fjern årsvakten (2026-01-01 gir 2025-12-31), la årsvakten sjekke hele uka rundt nyttår i stedet for dagene som slås opp (2026-01-02-testen), og `weekday() > 5` (lørdagstesten).

**Størrelse.** To nye kildemoduler, én migrasjon, én adapterklasse, og omtrent 40 nye og 2 endrede tester. Storyen er fortsatt én økt, men i to deler som 1.5b: del 1 er ren og liten, del 2 er lageret. Blir funnene etter del 1 mange, tas del 2 i en ny økt på samme gren.

**Arbeidsflyt, som 2.0:** grenen `1-6` fra `main`, mellomcommits som pushes, PR mot `main`, gjennomgang med tre lag, stopp før flettingen og vent på ja, squash med `Co-authored-by: Joakim Lund`. Etter flettingen: «Ferdig»-linje under 1.6 i `epics.md`, spesifikasjonen `done` og 1-6 til `review`.

## Verification

**Commands:**
- `uv run pytest -q` -- forventet: grønt, 468 + nye tester, telt
- Mutantene over, én om gangen -- forventet: akkurat testene for punktet feiler
