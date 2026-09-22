# Verifikasjonsgjennomgang — ARCHITECTURE-SPINE.md

**Lense:** verifikasjon — er hver forpliktet beslutning kontrollert mot virkeligheten,
eller påstått fra hukommelsen?
**Dokument:** `_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md`
**Dato for kontrollen:** 2026-09-22
**Kontrollert mot:** `pyproject.toml`, `uv.lock`, `.github/workflows/tester.yml`, `.gitignore`,
`src/`, `tests/`, `docs/kilder-og-rettigheter.md`, git-historikken, en kjøring av testene,
samt web (python.org, Docker Hub, PyPI/prosjektdokumentasjon, sqlite.org).

## Dom

Spinen er uvanlig godt forankret — sitatene finnes ordrett i kilden, alle åtte
commit-referansene eksisterer med riktig dato, konstantene står i koden med
målingen ved siden av, og «166 tester grønne 2026-09-22» ble bekreftet ved å
kjøre dem. Men den har **én påstand om eksisterende kode som ikke stemmer**
(portlaget gjør I/O i dag), og **én versjonstabell som beskriver gulvet i
`pyproject.toml` som om det var virkeligheten** — den låste versjonen av pytest
er 9.1.1, et helt hovedversjonssteg over det tabellen oppgir.

---

## 1. Stack-tabellen mot de faktiske filene

Spinen skriver: *«Versjonene er lest fra `pyproject.toml` og CI-arbeidsflyten,
ikke antatt.»* Det er sant for `pyproject.toml` og CI. Det er **ikke** sant for
`uv.lock`, som tabellen selv navngir i siste rad.

| Spinen sier | `pyproject.toml` | `uv.lock` (faktisk løst) | Dom |
|---|---|---|---|
| Python 3.13 (`requires-python = ">=3.13"`, CI pinner 3.13) | `requires-python = ">=3.13"` ✓ | `requires-python = ">=3.13"` ✓ | **Stemmer.** CI: `python-version: "3.13"` ✓ |
| Flask >= 3.0 | `flask>=3.0` ✓ | **3.1.3** | Gulvet stemmer; kjørende versjon er 3.1.3 |
| requests >= 2.32 | `requests>=2.32` ✓ | **2.34.2** | Gulvet stemmer; kjørende versjon er 2.34.2 |
| python-dotenv >= 1.0 | `python-dotenv>=1.0` ✓ | **1.2.3** | Gulvet stemmer; kjørende versjon er 1.2.3 |
| pytest >= 8.0 | `pytest>=8.0` ✓ | **9.1.1** | **Avvik i praksis** — se F2 |
| sqlite3, standardbiblioteket | — | — | Stemmer (se §3) |
| uv, `uv.lock`, CI kjører `uv sync --locked` | — | — | **Stemmer.** `run: uv sync --locked` ✓ |

Øvrige CI-påstander kontrollert og bekreftet: `permissions: contents: read` ✓,
ingen `secrets:` i arbeidsflyten ✓, kjører på `push` og `pull_request` mot `main` ✓
(AD-8, AD-12).

## 2. Eksisterer og passer hver teknologi fortsatt? (web, 2026-09-22)

| Teknologi | Status i dag | Konsekvens |
|---|---|---|
| **Python 3.13** | Støttet. Bugfix-fasen slutter **2026-10-01** (om ni dager), deretter security-only til EOL **2029-10-31**. Gjeldende stabile er 3.14. | Forsvarlig. Verdt å vite at 3.13 går over i security-only rett etter innlevering — ikke en risiko for v1. |
| **Flask 3.x** | Gjeldende stabile er **3.1.3** (sikkerhetsrettelse, 2026-02-19). Låst versjon = 3.1.3. | Oppdatert. |
| **requests 2.32+** | Gjeldende stabile er **2.34.2** (mai 2026), støtter Python 3.10+. Låst versjon = 2.34.2. Denne utgaven inneholder rettelsen for CVE-2026-25645. | Oppdatert. Gulvet `>=2.32` er derimot lavere enn den rettede utgaven. |
| **python-dotenv 1.x** | Gjeldende stabile er **1.2.3**. Låst versjon = 1.2.3. | Oppdatert. |
| **pytest 8.x** | **pytest 8 er ikke lenger gjeldende linje.** pytest 9.0 kom nov. 2025, 9.1.1 i juni 2026. Låst versjon = 9.1.1. | Se F2. |
| **uv** | Aktivt vedlikeholdt, `uv sync --locked` er gjeldende kommando. | Oppdatert. |

Ingen av de navngitte teknologiene er EOL, utgått eller erstattet. Ingen
avhengighet i `uv.lock` er eldre enn gjeldende utgivelse.

**Utenfor spinens egne påstander, men i den virkeligheten spinen utnevner til
sannhetskilde:** CI pinner `actions/checkout@v4` (gjeldende hovedversjon er
**v6**) og `astral-sh/setup-uv@v5` (gjeldende er **v10.x**; prosjektet har
sluttet å publisere minor-tagger, og v5 er fem hovedversjoner bak). Se F5.

## 3. SQLite — holder AD-4, AD-5 og AD-16?

**Standardbiblioteket:** bekreftet mot `docs.python.org/3.13/library/sqlite3.html`.
`sqlite3` er del av standardbiblioteket i 3.13, DB-API 2.0 (PEP 249), krever
SQLite 3.15.2 eller nyere. **AD-4s premiss om «ingen ny avhengighet» stemmer.**

**AD-5 — DELETE + INSERT i én transaksjon:** støttet og uproblematisk. Med
standard `isolation_level=""` (alias for `DEFERRED`) åpner driveren implisitt en
transaksjon før DML, og `commit()` lukker den. `erstatt_serie` kan gjøres atomisk
slik AD-5 krever. **Ingen innvending.**

**AD-16 — nummererte migrasjoner: tre fallgruver spinen ikke nevner.**
Ingen av dem gjør AD-16 umulig, men alle tre må håndteres eksplisitt, ellers
oppfører migrasjonene seg annerledes enn AD-16 lover:

1. **`executescript()` committer før den kjører.** Python 3.13 har fortsatt
   `LEGACY_TRANSACTION_CONTROL` som standardverdi for `autocommit`, og
   dokumentasjonen sier ordrett: *«If `autocommit` is `LEGACY_TRANSACTION_CONTROL`
   and there is a pending transaction, an implicit `COMMIT` statement is executed
   first.»* Den nærliggende måten å kjøre en nummerert `.sql`-fil på er nettopp
   `executescript()` — og da er migrasjonen **ikke** atomisk sammen med
   oppdateringen av `skjema_versjon`. En avbrutt kjøring kan etterlate skjemaet
   endret og versjonsraden uendret. Løsningen er `autocommit=False` eller
   eksplisitt `BEGIN`, men det er en beslutning, ikke en standardverdi.
2. **DDL i SQLite *er* transaksjonelt** — det taler for AD-16 — men
   `PRAGMA foreign_keys` kan ikke endres inne i en åpen transaksjon. SQLites egen
   12-stegs oppskrift for tabellombygging krever `PRAGMA foreign_keys=OFF`
   *utenfor* transaksjonen. Med FK-er mellom `aksje`, `kurs`, `melding`,
   `vurdering` og `ki_logg` (ER-diagrammet) treffer dette første gang en tabell
   må bygges om.
3. **`ALTER TABLE` kan lite.** SQLite støtter bare: rename tabell, rename kolonne,
   add column, drop column (og fra 3.53.0 sette/fjerne NOT NULL). Endre
   kolonnetype, legge til UNIQUE eller PRIMARY KEY, endre CHECK eller legge til /
   fjerne FK er **ikke** støttet — det krever 12-stegs tabellbytte (ny tabell,
   `INSERT … SELECT`, drop, rename, gjenskap indekser/triggere/views,
   `PRAGMA foreign_key_check`). AD-16s formulering *«Ingen `ALTER TABLE` utenfor
   en migrasjonsfil»* er riktig, men underkommuniserer at de fleste reelle
   skjemaendringer i SQLite **ikke er `ALTER TABLE` i det hele tatt**. Dette
   kolliderer direkte med AD-7: tabellbytte for `vurdering` eller `ki_logg`
   innebærer `DROP TABLE` på et lager som er erklært uerstattelig. AD-16 sier
   ikke hvordan de to reglene skal leve sammen.

**AD-4 hviler ikke på SQLite-oppførsel som ikke finnes.** Begrunnelsen er
vilkårsmessig (ingen hostet database), ikke teknisk, og den holder.

## 4. Docker — er utsettelsen forsvarlig?

Kontrollert mot Docker Hub 2026-09-22: **`python:3.13-slim` finnes og ble oppdatert
for tre dager siden**, sammen med `3.13-slim-trixie` og `3.13-slim-bookworm`.
Det finnes altså ingenting som gjør utsettelsen uforsvarlig — tvert imot, det
finnes flere gyldige valg, og valget mellom trixie og bookworm er nettopp et som
bør tas når Dockerfilen skrives.

**Utsettelsen er forsvarlig.** Bindingen spinen faktisk gjør — *«at Python-versjonen
matcher CI (3.13), ikke en bestemt tag»* — er den riktige bindingen, og den kan
oppfylles i dag.

## 5. Sitatene i AD-4 og AD-9 — finnes de der de påstås å stå?

Begge kontrollert ordrett mot `docs/kilder-og-rettigheter.md`. **Begge finnes.**

| Sitat i spinen | Funnet | Kontekst i kilden |
|---|---|---|
| «the output stays local» (AD-4) | **Ja**, linje 271 | Betingelse 1 av fire i EODHDs skriftlige godkjenning av 21.09 |
| «otherwise transfer any of the Content to any third person» (AD-9/AD-4) | **Ja**, linje 559 | Euronext-vilkårene, klausul 2, sitert ordrett i en lengre oppramsing |

AD-9 inneholder ingen ordrette sitater, men gjør en faktapåstand: at EODHDs
godkjenning av 21.09 *«dekker demonstrasjonen for lærer og klasse — den dekker
ikke at vi overleverer et datasett»*. **Begge halvdelene er bekreftet** i kilden:
tabellen på linje 359 fører spørsmål 1 som «Demonstrasjonen for lærer og klasse
er del av det ikke-kommersielle studieprosjektet, ikke offentlig drift — Ja», og
avsnittet «Hva svaret ikke dekker» trekker grensen spinen gjengir.

AD-9s tekniske påstand er også kontrollert: `.gitignore` utelater både `data/`
og `*-raa-*.json` ✓ (begge med begrunnelse i fila).

**Én presisering (F6):** «the output stays local» er betingelse 1 i godkjenningen
av **språkmodellbruken**, ikke en generell lagringsklausul i EODHDs vilkår. AD-4
bruker den til å forby en hostet database. Betingelse 2 — «the project is not
publicly deployed» — bærer den konklusjonen bedre. Sitatet er ekte og riktig
tilskrevet EODHD, men flyttet fra den beslutningen det ble gitt til.

## 6. Øvrige påstander kontrollert mot prosjektet

Alt dette ble kontrollert og **stemmer**:

- **Alle åtte commit-referansene eksisterer** med de datoene spinen oppgir:
  `01af1a5` og `9acb55c` (20.09), `706720f`, `076bb12`, `b6ba9d8`, `352e3a2`,
  `be2ba93`, `266e6d9` (21.09).
- **AD-8:** `tests/conftest.py` monkeypatcher `socket.socket.connect` og
  `connect_ex` med `@pytest.fixture(autouse=True)` ✓. «166 tester grønne
  2026-09-22» — **kjørt på nytt i dag: `166 passed in 0.51s`** ✓.
- **AD-2:** `requests` brukes nøyaktig ett sted i hele `src/` —
  `fetch_prices.py:67`, inne i `hent_ett_symbol` ✓. `hent_universet` tar
  hentefunksjonen som argument ✓.
- **AD-1:** ingen av de fem kjernemodulene importerer `requests`, `sqlite3`,
  `pathlib` eller `flask` ✓. `signalberegning.py` og `meldinger.py` importerer
  ingen prosjektmodul — løvnoder, som påstått ✓.
- **AD-13:** `NOYTRALSONE = 0.02`, `VOLUMFAKTOR = 1.5`, `TERSKEL = 2` står i
  `signalberegning.py` med målingen i kommentaren ved siden av seg ✓.
  `VOLATILITET_VINDU = 20` og `VOLUM_VINDU = 20` er merket `[FORELOEPIG]` med
  teksten «Disse to var ikke med i testen 21.09. De staar til de maales.» ✓
- **AD-6:** filnavnmønsteret `<prefiks>-raa-<ÅÅÅÅ-MM-DD>.json` ✓, og
  `nyeste_snapshot` lar datoen avgjøre alene med `KURSPREFIKS` som vinner ved lik
  dato ✓ — begge deler stemmer ordrett med koden.
- **AD-10s regnestykke:** `AKSJEUNIVERS` har 15 aksjer ✓, så «to `docker run`
  samme dag = 30 kall mot en grense på 20» går opp.
- **AD-12:** `.env.example` finnes, `EODHD_API_KEY` leses med `os.getenv` i
  `fetch_prices.py:53` ✓.
- **Merket `[ny]`:** `Dockerfile`, `lagring_sqlite.py` og `src/migrasjoner/`
  finnes ikke i dag ✓ — riktig merket.

---

## Funn, med alvorlighetsgrad

### F1 — ALVORLIG: portlaget gjør I/O i dag, tvert imot det spinen påstår

Lagtabellen sier om Porter / `kursdata.py`: *«Bare `Protocol`-definisjoner og
verdityper. Ingen implementasjon som rører I/O.»* Og spinen understreker at
paradigmet *«ikke er valgt her»*, men beskriver kode som allerede er bygget.

`src/kursdata.py` importerer `json` og `pathlib`, og inneholder to funksjoner som
rører filsystemet:

- `nyeste_snapshot(katalog: Path = DATA_KATALOG)` — kaller `katalog.is_dir()` og
  `katalog.glob("*-raa-*.json")`.
- `SnapshotKilde.fra_fil(sti)` — `json.loads(sti.read_text(...))`.

`app.py` kaller `nyeste_snapshot()` direkte (linje 25). Regelen er altså brutt av
eksisterende kode fra dag én, og spinen presenterer den som beskrivende.
Dette er den eneste påstanden i dokumentet som motsies av koden den beskriver.

Konsekvensen er ikke kosmetisk: AD-3 sier at lesere går gjennom porten, og AD-4
flytter lagringen til SQLite. Da må det avgjøres om snapshot-lesingen blir
liggende i `kursdata.py` (og regelen endres til å tillate det) eller flytter til
skallet ved siden av `lagring_sqlite.py` (og `app.py` må endres). Spinen tar ikke
det valget, fordi den ikke har sett at det finnes.

**Anbefaling:** enten omformulér Porter-regelen til å beskrive virkeligheten
(«Protocol-definisjoner, verdityper og filbaserte referanseimplementasjoner»),
eller før flyttingen av `nyeste_snapshot`/`SnapshotKilde` som et eksplisitt
punkt. Ikke la regelen stå som om den holder.

### F2 — MEDIUM: Stack-tabellen oppgir gulv, ikke det som faktisk kjører

Tabellen lover at versjonene er lest og ikke antatt, men leser bare gulvet i
`pyproject.toml`. Den låste virkeligheten i `uv.lock` — som tabellen selv
navngir — er: Flask **3.1.3**, requests **2.34.2**, python-dotenv **1.2.3**,
pytest **9.1.1**.

For de tre første er avviket ufarlig. For pytest er det ikke det: **`>= 8.0` er
et gulv som slipper igjennom et helt hovedversjonssteg.** pytest 9.0 gjorde
utgåtte API-er til harde feil (nose-stil setup/teardown, `pytest.collect`,
yield-tester, posisjonell `Node`-konstruksjon), og 9.1 fjernet dem endelig.
Testene er grønne på 9.1.1 i dag, så skaden er ikke skjedd — men spinen låser et
gulv som ville tillatt en ny `uv lock` å bytte hovedversjon uten at noen
bestemte det. Tilsvarende er `requests>=2.32` lavere enn utgaven som retter
CVE-2026-25645.

**Anbefaling:** før den låste versjonen ved siden av gulvet i tabellen, og si
hvilken av de to som er bindende. Vurder øvre grenser for pytest.

### F3 — MEDIUM: AD-16 hviler på transaksjonsoppførsel som ikke er standard

Se §3 for detaljene. Kort: `executescript()` committer implisitt før den kjører
(legacy-modus er fortsatt standard i 3.13), `PRAGMA foreign_keys` kan ikke endres
i en transaksjon, og SQLites `ALTER TABLE` dekker ikke typeendringer, nye
UNIQUE/PRIMARY KEY, CHECK eller FK — de krever 12-stegs tabellbytte med
`DROP TABLE`. Det siste kolliderer med AD-7, som gjør `vurdering` og `ki_logg`
udslettelige. AD-16 sier ikke hvordan.

**Anbefaling:** legg til én setning i AD-16 om at migrasjoner kjøres med
eksplisitt transaksjonskontroll (`autocommit=False` eller eksplisitt `BEGIN`),
og ett punkt om hva som gjelder når en uerstattelig tabell må bygges om.

### F4 — MEDIUM: strukturskissen flytter rådataene, uten å si at det er en endring

Skissen viser `data/raa/` for øyeblikksbildene og `data/db/ose.db` for basen.
Koden har `DATA_KATALOG = PROSJEKTROT / "data"`, og `nyeste_snapshot` globber
`data/*-raa-*.json` — altså rett i `data/`, ikke i `data/raa/`. Flyttingen er
fornuftig (den følger AD-11s to volumer), men den er en **kodeendring** som ikke
er merket `[ny]` slik `lagring_sqlite.py`, `migrasjoner/` og `Dockerfile` er.
Leses skissen som beskrivende, vil `nyeste_snapshot` slutte å finne noe.

### F5 — LAV: CI-actions er flere hovedversjoner bak

`actions/checkout@v4` (gjeldende **v6**) og `astral-sh/setup-uv@v5` (gjeldende
**v10.x**). Ikke en påstand spinen gjør — men spinen utnevner CI-arbeidsflyten
til sannhetskilde for stacken, og da er det verdt å vite at to av tre pinninger
der er utdaterte. setup-uv har sluttet å publisere minor-tagger av
forsyningskjedehensyn.

### F6 — LAV: «the output stays local» er flyttet fra den beslutningen den gjaldt

Sitatet er ordrett og riktig tilskrevet EODHD, men det er betingelse 1 i
godkjenningen av **språkmodellbruken** av 21.09 — ikke en vilkårsklausul om
lagring. AD-4 bruker det til å forby en hostet database. Konklusjonen er
sannsynligvis riktig, men den hviler bedre på betingelse 2 («the project is not
publicly deployed») eller på Euronext-klausulen som allerede står der.

### F7 — INFO: Python 3.13 går inn i security-only om ni dager

Bugfix-fasen slutter 2026-10-01. EOL er 2029-10-31, og 3.13 er fullt støttet.
Valget er forsvarlig og trenger ingen endring — det er bare verdt å ha ført, i
og med at `requires-python = ">=3.13"` også slipper inn 3.14, mens CI pinner
3.13. Spinen skriver «3.13» der `pyproject.toml` sier «>=3.13»; de to er ikke
det samme, og CI-pinningen er det som faktisk holder dem sammen.

---

## Hva som ikke lot seg verifisere her

- **AD-5s «minst 175 handelsdager»** og **AD-13s «199 handelsdager og 2 985
  aksjedager»** er ført mot `malinger.md`. Tallene er ikke etterregnet i denne
  gjennomgangen — bare at konstantene står i koden med måling ved siden av seg.
- **Euronext-forespørselen** og **spørsmålet til faglærer om SQLite (22.09)** er
  begge ubesvarte i kilden. Spinen fører dem korrekt som utsatte punkter; de kan
  ikke verifiseres, bare ventes på.
- **Betingelse 4 i EODHDs godkjenning** (at modelltjenesten ikke trener på
  innholdet) er ikke oppfylt, fordi ingen modelltjeneste er valgt. Spinen fører
  dette riktig under Deferred, med kravet om at det må føres **før** artikkeltekst
  sendes inn.

## Oppsummering

| # | Funn | Alvorlighet |
|---|---|---|
| F1 | Portlaget (`kursdata.py`) gjør filsystem-I/O, tvert imot lagtabellens regel | **ALVORLIG** |
| F2 | Stack-tabellen oppgir gulv fra `pyproject.toml`; `uv.lock` har pytest **9.1.1** mot oppgitt `>= 8.0` | MEDIUM |
| F3 | AD-16 hviler på transaksjons- og `ALTER TABLE`-oppførsel som må settes eksplisitt; kolliderer med AD-7 ved tabellombygging | MEDIUM |
| F4 | Strukturskissen flytter øyeblikksbildene til `data/raa/` uten å merke det som endring; `nyeste_snapshot` leser `data/` | MEDIUM |
| F5 | CI pinner `checkout@v4` (nå v6) og `setup-uv@v5` (nå v10.x) | LAV |
| F6 | «the output stays local» er betingelse i språkmodellgodkjenningen, brukt som lagringsargument i AD-4 | LAV |
| F7 | Python 3.13 går inn i security-only 2026-10-01; `>=3.13` er ikke «3.13» | INFO |

**Verifisert uten avvik:** begge ordrette sitatene, alle åtte commit-referansene,
166 grønne tester (kjørt på nytt), AD-1s løvnoder, AD-2s ene nettkall, AD-13s
konstanter og `[FORELØPIG]`-merking, AD-6s filnavnmønster og datoregel, AD-9s
`.gitignore`-påstand og godkjenningens rekkevidde, AD-12s miljøvariabel, hele
CI-påstanden, samt at `python:3.13-slim` finnes — Docker-utsettelsen er
forsvarlig.

---

*Kilder for web-kontrollene: [Python 3.13 release schedule](https://versionlog.com/python/3.13/) ·
[Python EOL-oversikt](https://eolrisk.com/python/) ·
[Flask changelog 3.1.x](https://flask.palletsprojects.com/en/stable/changes/) ·
[requests 2.34.2](https://requests.readthedocs.io/) ·
[python-dotenv PyPI](https://pypi.org/project/python-dotenv/) ·
[pytest PyPI](https://pypi.org/project/pytest/) ·
[pytest 9 migrasjon](https://qaskills.sh/blog/pytest-9-new-features-migration-guide-2026) ·
[sqlite3 i Python 3.13](https://docs.python.org/3.13/library/sqlite3.html) ·
[SQLite ALTER TABLE](https://www.sqlite.org/lang_altertable.html) ·
[python:3.13-slim på Docker Hub](https://hub.docker.com/_/python/tags?name=3.13-slim) ·
[actions/checkout releases](https://github.com/actions/checkout/releases) ·
[astral-sh/setup-uv releases](https://github.com/astral-sh/setup-uv/releases)*
