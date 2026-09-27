---
title: 'Story 1.6: Vurderingslager med datoavvisning'
type: 'feature'
created: '2026-09-27'
status: 'in-review'
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
- [x] `src/boersdag.py` -- `STENGT`, `innevaerende_boersdag`, `norsk_dato` og `UtenforKalenderen(ValueError)`.
- [x] `tests/test_boersdag.py` -- matrisen over, med 2026-01-02, pluss at `STENGT` er de ti datoene og at `datetime` avvises som dag. `norsk_dato` prøves 00:30 i både sommertid og vintertid.
- [x] `tests/test_konsumentene.py` -- `boersdag.py` i `KJERNEMODULER`.

**Del 2, lageret:**
- [x] `src/migrasjoner/0002_vurdering.sql` -- `grunn` med tre rader, `vurdering` med `PRIMARY KEY (symbol, dato)`, enten/eller-`CHECK` over alle sju vurderingsfeltene og to triggere.
- [x] `src/vurderingsdata.py` -- `Vurdering`, `Grunn`, `Vurderingslager`, `UgyldigVurdering`.
- [x] `src/lagring_sqlite.py` -- `SqliteVurderingslager(tilkobling, klokke)` med upsert og `WHERE excluded.grunn IS NULL OR vurdering.grunn IS NOT NULL`.
- [x] `tests/test_vurderingslager.py` -- matrisen, protokollen, `grunn` lik `Grunn`, retningene lik `signalberegning`, og validering av `Vurdering`.
- [x] `tests/test_lagring_sqlite.py` -- de to testene over bruker neste ledige nummer.
- [x] Spinen -- `boersdag.py` i Kjerne, `vurderingsdata.py` i Porter med hvorfor det ikke finnes noe minnelager, nye kanter i grafen, og de to Deferred-radene.

**Acceptance Criteria:**
- Gitt koden fra `baseline_commit`, når de nye testene kjøres, så feiler de (modulene finnes ikke).
- Gitt hver mutant i Design Notes, lagt inn én om gangen og satt tilbake mellom hver, når hele testsettet kjøres, så feiler testene for det kontrollpunktet med forventet melding.
- Gitt hele testsettet lokalt og i CI, så er det grønt begge steder, og antallet før (468) og etter står i squash-meldingen.

## Implementation Notes

**Del 1, børsdagene, 27.09.** Bygget direkte i økta, ikke av en egen implementeringsagent, fordi instruksjonen kl. 15:13 krevde at bare del 1 ble bygget, med gjennomgang og stopp etterpå, og at mutantene ble lagt inn én om gangen. Grenen `1-6` fra `b6de297`, commit `d9d31ac`.

- **Tester:** 468 før, 497 etter `d9d31ac`: 26 nye i `tests/test_boersdag.py` og 3 nye i `tests/test_konsumentene.py`, fordi `KJERNEMODULER` også går inn i de to vaktene mot EODHDs feltnavn. *Rettet 27.09 etter gjennomgangen (BH3):* her sto «28 nye … og 1 ny». 501 etter rettingene fra gjennomgangen: 4 nye, 3 for 1. mai, Kristi himmelfart og 2. pinsedag og 1 for en sone uten forskyvning.
- **Mot koden uten modulen:** `tests/test_boersdag.py` feilet ved innsamlingen med `ModuleNotFoundError`, som ventet.
- **Lista i koden og lista i dokumentet:** testen leser linjen «Stengt i 2026 …» i seksjonen Handelskalenderen i `docs/kilder-og-rettigheter.md`. Første versjon talte 11 datoer, fordi neste setning på samme linje nevner halvdagen 2026-04-01. Testen leser nå bare første setning.
- **Mutanter, én om gangen, mot hele testsettet, med `git checkout` mellom hver:**
  - B1, 2026-04-06 fjernet fra `STENGT`: påsketesten for 04-06 og testen mot dokumentet feiler
  - B2, 2026-04-01 lagt til i `STENGT`: halvdagstesten, påsketestene og testen mot dokumentet feiler
  - B3, årsvakten fjernet: 2026-01-01-testen og begge testene for dager utenfor 2026 feiler
  - B4, årsvakten sjekker uka rundt nyttår: 2026-01-02-testen feiler, og 2026-01-01-testen feiler på meldingen
  - B5, lørdag regnes som hverdag: helgetestene, påsketestene for 04-04 til 04-06 og testen for 12-26 feiler
  - B6, datoen regnes i UTC: begge 00:30-testene og testen med tidspunkt i Oslo feiler
  - B7, et tidspunkt godtas som dag: testen for `datetime` feiler

  Ingen mutant overlevde.
- **Etter rettingene fra gjennomgangen**, samme mutanter på nytt mot den rettede koden, pluss to nye:
  - B8, sonevakten ser bare på `tzinfo`: testen for en sone uten forskyvning feiler
  - B9, 2027 lagt til i `DEKKEDE_AAR` uten dagene for 2027: testen for 2027-01-04 og testen for at lista og årene stemmer, feiler

  B1–B7 fanges som før, og B5 fanges nå også av testen for 2. pinsedag. Ingen mutant overlevde.
- **Status** står som `in-progress` under gjennomgangen av del 1, ikke `in-review`, fordi del 2 gjenstår.

**Del 2, lageret, 27.09.** Bygget direkte i økta på samme gren, etter instruksjonen kl. 15:44. Commitene: `920b0e0` (0002, porten, adapteren og testene), `0a2f54c` (spinen) og `9e12277` (rettingene etter gjennomgangen).

- **Tester:** 501 før del 2. 578 etter `920b0e0`: 74 nye i `tests/test_vurderingslager.py` og 3 nye i `tests/test_konsumentene.py`, fordi portvakten og de to vaktene mot EODHDs feltnavn også gjelder `vurderingsdata.py`. 614 etter rettingene i `9e12277`: 36 nye, 27 av dem for retningene. Hele storyen: 468 før og 614 etter.
- **Mot koden uten modulene:** `tests/test_vurderingslager.py` feilet ved innsamlingen med `ImportError` (`SqliteVurderingslager` fantes ikke), som ventet.
- **De to testene i `tests/test_lagring_sqlite.py`** feilet med `MigrasjonsFeil: To migrasjoner har nummer 0002` da `0002_vurdering.sql` kom inn, og bare de. Etter omskrivingen bruker de `siste_versjon(MIGRASJONSKATALOG) + 1`.
- **Grunnene** heter `symbol_feilet`, `kurs_ikke_fra_dagen` og `signal_ikke_regnet`, i `Grunn` og i tabellen `grunn`.
- **Verdiene kontrolleres i `Vurdering`, ikke i en `CHECK`.** `CHECK`-en sjekker bare enten/eller, fordi en ny regel i en `CHECK` krever at tabellen bygges om. `Vurdering` krever at styrken er summen av sjekkene og at retningen er den fortegnene gir, og gjør kursene om til float.
- **Mutanter, én om gangen, mot hele testsettet, med `git checkout` mellom hver.** Første runde, mot `920b0e0`:
  - K1, datokontrollen fjernet: 6 tester feiler (i går, i morgen, lørdag, 00:30 i begge tider og at gårsdagens rad ikke kan skrives om neste dag)
  - K1, UTC i stedet for Oslo: begge 00:30-testene feiler, og testen for en klokke uten sone
  - K2, `INSERT` uten `ON CONFLICT`: de fire testene for overskriving feiler
  - K3, `endre` i protokollen: testen for protokollen og testen for at adapteren oppfyller den feiler
  - K4, `erstatt_serie` sletter fra `vurdering`: testen for at vurderingen overlever, feiler
  - K5, tabellen lages av adapteren: 25 tester feiler, 24 i `TestSkjemaet` og testen for en åpen transaksjon hos kalleren
  - K6, `WHERE` fjernet: testen for grunn over vurdering feiler
  - K6, `WHERE` som stopper vurdering over grunn: testene for vurdering over grunn og grunn over grunn feiler
  - K6, triggerne fjernet: de tre testene for ukjent grunn feiler
  - K6, `CHECK` fjernet: 16 tester for enten/eller feiler

  Ingen mutant overlevde.
- **Andre runde, mot `9e12277`, etter rettingene:** K1–K6 på nytt, B1–B9 fra del 1 på nytt, og seks nye:
  - R1, triggerne på `grunn` fjernet: de to testene for sletting og endring feiler
  - R2, retningen kontrolleres ikke mot sjekkene: alle 27 retningstestene feiler
  - R3, `les` kontrollerer ikke symbol og dato: de to testene for `les` feiler
  - R4, kursen gjøres ikke om til float: de to testene for store heltall feiler
  - R5, ingen tilbakerulling i `skriv`: testen for tilbakerullingen feiler
  - R6, `bool` godtas som styrke: testen for `styrke=True` feiler

  Alle 25 ble fanget. K5 fanges nå av 28 tester, K6 (triggerne) av 4 og K6 (`CHECK`) av 17, fordi testen for `ADD COLUMN` også ser dem.

## Spec Change Log

## Review Triage Log

Tre lag gjennomgikk del 1 den 27.09: Blind Hunter (BH), Edge Case Hunter (ECH) og Verification Gap (VG), på diffen for `src/` og `tests/` siden `baseline_commit`. Hvert funn har én rad.

| # | Funn | Dom | Bevis | Rute |
|---|---|---|---|---|
| BH1 | Ett år om gangen: flyttes `AAR` til 2027, må 2027-01-01 slå opp 2026-12-31, og da reiser funksjonen | medium | Kommentaren sa «AAR flyttes samtidig». 2026-12-31 og 2026-12-30 ville ligget utenfor | patch: `DEKKEDE_AAR`, et sett der nye år legges til og gamle blir stående |
| BH2 | Ingenting varsler før lista går ut, og `skriv` reiser fra 2027-01-01 | low | Riktig, men det er vedtaket i punkt 3: funksjonen reiser i stedet for å gjette, og Marian fører inn 2027 | avvist: følger av vedtaket. Meldes dere |
| BH3 | Testtallene i Implementation Notes stemmer ikke | low | `--collect-only`: 26 i `test_boersdag.py` og 3 i `test_konsumentene.py`, ikke 28 og 1. Summen 29 stemte | rettet i notatene, med datert rettelse |
| BH4 | Testen mot dokumentet brekker hvis avsnittet brytes over flere linjer | low | Den leste bare linjen som begynner med «Stengt i 2026» | patch: setningen leses med mellomrom slått sammen |
| BH5 | 1. mai, Kristi himmelfart og 2. pinsedag har ingen atferdstest | low | De var bare med i sammenlikningen med dokumentet | patch: tre tilfeller |
| BH6 | Testen for hverdager bruker 2026, ikke konstanten | medium | Samme rot som BH1 | patch: under BH1. Testen sjekker at årene i `STENGT` er `DEKKEDE_AAR` |
| BH7 | `norsk_dato` er ikke prøvd ved sommertidsskiftet eller i en tredje sone | false | En forenkling til `.date()` eller UTC fanges av 00:30-testene (B6). Skiftet håndteres av `zoneinfo`, ikke av egen kode | avvist |
| BH8 | Modulens docstring nevner ikke `norsk_dato`, og testfila har «ført» ved siden av «haand» | low | Spesifikasjonen nevner begge funksjonene i samme punkt, så den delen stemmer ikke. Resten stemmer | patch: docstringen og «foert» |
| ECH1 | Flyttes årstallet før dagene for 2027 er ført inn, telles helligdagene i 2027 som børsdager | medium | Samme rot som BH1 | patch: under BH1. Mutant B9 fanges |
| ECH2 | Testen for hverdager binder ikke `STENGT` til årstallet | medium | Samme som BH6 | patch: under BH1 |
| ECH3 | `OverflowError` slipper ut for et tidspunkt nær `datetime.max` | low | Prøvd: gir `OverflowError`. Krever en klokke i år 9999 | avvist: lite sannsynlig, og krever en ny vakt |
| VG1 | En `tzinfo` som svarer `None` på `utcoffset` er ikke prøvd | low | Prøvd: `astimezone` leser den da som maskinens lokale tid. Mutanten B8 overlevde før testen | patch: ny test |

Tre lag gjennomgikk hele storyen den 27.09, del 1 og del 2 sammen, på diffen for `src/` og `tests/` siden `baseline_commit`: Blind Hunter (BH), bare diffen, Edge Case Hunter (ECH) og Verification Gap (VG), med tilgang til repoet. Nummereringen begynner på nytt og gjelder bare denne runden.

| # | Funn | Dom | Bevis | Rute |
|---|---|---|---|---|
| BH1 | Testen for ukjent grunn via upsert prøver ikke `UPDATE`-triggeren | low | SQLite kjører `BEFORE INSERT` før konflikten oppdages. VG7 viste det samme: uten `UPDATE`-triggeren feiler bare testen for vanlig `UPDATE` | patch: docstringen sier hvilken trigger som stopper upserten. Begge triggerne fanges av hver sin test |
| BH2 | En kjøring som går over midnatt i Oslo, feiler halvveis: `skriv` reiser for resten av symbolene | medium | Riktig. Klokka leses ved hvert kall (AD-7), og datoen er fast for kjøringen | avvist her: det er kallerens sak. Ført i `deferred-work.md` for story 2.5 |
| BH3 | Ingenting beskytter tabellen `grunn`. En slettet grunn gjør rader i `vurdering` uleselige | medium | `test_en_grunn_slettes_ikke` og `test_en_grunn_endres_ikke` feilet mot koden fra før rettingene. En rad som peker på en slettet grunn, gir `ValueError` i `Grunn(...)` når `les` leser den | patch: to triggere i `0002` som stopper `DELETE` og `UPDATE` på `grunn`. Mutant R1 fanges |
| BH4 | `les` validerer radene på nytt, så strengere regler senere kan gjøre gamle rader uleselige | low | Riktig i prinsippet. Reglene endres i så fall i en migrasjon, og det avgjøres der (spinen, Deferred) | avvist |
| BH5 | `Vurdering` kontrollerer ikke retningen mot sjekkene | low | `styrke=0, retning="Positiv"` ble godtatt | patch: retningen skal være den fortegnene gir. Testen prøver alle 27 kombinasjonene mot `finn_retning`. Mutant R2 fanges |
| BH6 | Et stort heltall som kurs slipper gjennom `Vurdering` og feiler i SQLite med `OverflowError` | low | Samme som ECH1 | patch: under ECH1 |
| BH7 | `les` kontrollerer ikke symbolet | low | `les("EQNR.OL", …)` ga `None`, som leses som at kommandoen ikke ble kjørt (FR-409) | patch: `les` og `skriv` bruker samme kontroll. Mutant R3 fanges |
| BH8 | Transaksjonen forutsetter Pythons gamle modus, og en feil i `ROLLBACK` skjuler den første feilen | low | ECH7 prøvde `isolation_level=None` og `autocommit=True`: begge virker. `autocommit=False` reiser `RuntimeError`, som i `SqliteKurslager`, og `migrer` avviser samme tilkobling | avvist: samme mønster som `SqliteKurslager` |
| BH9 | Protokolltesten ser ikke en `slett` arvet fra en baseklasse | low | `vars` ser bare klassen selv | patch: `dir` |
| BH10 | `ZoneInfo("Europe/Oslo")` krever tzdata på Windows | false | tzdata står i avhengighetene, og `tests/test_tidssone.py` holder den (spinen, Stack) | avvist |
| BH11 | `skriv` reiser for alle dager fra 2027-01-01 | low | Vedtaket i punkt 3, og punkt 25 i `prd.md` §8 har eier og frist | avvist: følger av vedtaket |
| ECH1 | `Vurdering(..., justert_slutt=10**20)` godtas, og `skriv` reiser `OverflowError` | low | Kjørt: `OverflowError: Python int too large to convert to SQLite INTEGER`. Tilbakerullingen virket | patch: kursene gjøres om til float i `Vurdering`. `10**400` gir `UgyldigVurdering`. Mutant R4 fanges |
| ECH2 | `les` gir ikke en lik `Vurdering` tilbake for heltall over 2**53 | low | Kjørt: `2**53+1` ble lest som `9007199254740992.0` | patch: under ECH1. Testet med `2**53+1` og `10**20` |
| ECH3 | `CHECK` sjekker bare enten/eller, så en rad skrevet utenom porten kan bli uleselig | low | Kjørt: `trend=7` gikk inn i basen, og `les` reiste `UgyldigVurdering` | avvist: valgt med vilje (kommentaren i `0002`), og porten er eneste skriver |
| ECH4 | Meldingen fra `UtenforKalenderen` gjentar datoen når dagen selv er utenfor | low | «2027-01-01 krever 2027-01-01» | patch: meldingen nevner dagen én gang |
| ECH5 | Soner og sommertid | false | 21:59:59Z og 22:00Z rundt midnatt, og nettene der sommertiden skifter, gir riktig dag | ingen endring |
| ECH6 | Upsert og `rowcount` i alle rekkefølger, og triggerne på alle skriveveier | false | Kjørt, også `INSERT OR REPLACE` | ingen endring |
| ECH7 | Tilkoblingsmodusene | false | Se BH8 | ingen endring |
| ECH8 | Underklasser av `str`, `int` og `date` slipper gjennom `isinstance` | false | De leses tilbake like, og `bool` avvises | ingen endring |
| ECH9 | `les` kontrollerer ikke symbolet | low | Samme som BH7 | patch: under BH7 |
| ECH10 | De to omskrevne testene i `tests/test_lagring_sqlite.py` | false | De regner fra `siste_versjon` og tåler en `0003` | ingen endring |
| VG1 | Spinen sier at hvert kontrollpunkt er prøvd med mutant, men notatene hadde bare B1–B9 | medium | Riktig da gjennomgangen ble gjort | patch: K1–K6 og R1–R6 står i Implementation Notes |
| VG2 | Ingen test går gjennom tilbakerullingen i `skriv` | low | Mutanten uten `ROLLBACK` overlevde | patch: en midlertidig trigger stopper `INSERT`, og testen ser at transaksjonen er lukket og lageret virker etterpå. Mutant R5 fanges |
| VG3 | `les` avviser et tidspunkt som dato, men ingen test ser det | low | Mutanten overlevde | patch: under BH7, med egen test |
| VG4 | `styrke=True` ble avvist av summen, ikke av `bool`-kontrollen. Kontrollen av området 0–3 overflødig. `OverflowError` utestet | low | Tre mutanter overlevde. Den for området er ekvivalent | patch: testtilfellet har riktig sum, kontrollen av området er fjernet (summen dekker den), og `10**400` er testet. Mutant R6 fanges |
| VG5 | `0002` og spinen sier at begge endringene er prøvd i minnet, men bare ny grunn har en test | low | Riktig | patch: en test for `ADD COLUMN`, med `integrity_check`, `CHECK` og triggere etterpå |
| VG6 | «logger ikke» i storyen er ikke testet | low | Koden logger ingenting. Testene ser at `skriv` reiser og at ingen rad skrives | avvist |
| VG7 | Upsert-testen prøver `INSERT`-triggeren | false | Samme som BH1 | patch: under BH1 |
| VG8 | «Klokka leses ved hvert kall» | false | `test_eldre_rad_kan_ikke_skrives_om_neste_dag` bytter klokka mellom kallene | ingen endring |

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
