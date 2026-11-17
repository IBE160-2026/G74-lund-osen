---
title: "Teknologi og nøkler"
status: aktiv
created: 2026-11-17
updated: 2026-11-17T22:30
---

# Teknologi og nøkler

Oversikt over OSE Signal, skrevet i samme form som [`technology.md`](technology.md), faglærers mal, som beskriver et annet prosjekt. Den er skrevet for at appen skal kunne settes opp igjen på en annen maskin. **Ingen hemmelige verdier er lest eller gjengitt**, bare navnene på variablene. Alt er sjekket mot filene på grenen: [`pyproject.toml`](../../../pyproject.toml), `uv.lock`, [`.env.example`](../../../.env.example), [`Dockerfile`](../../../Dockerfile), [`compose.yaml`](../../../compose.yaml), `src/` (særlig `app.py`, `fetch_prices.py`, `ki_tekst.py`, `ki_lokal.py`, `ki_gemini.py`, `ki_anthropic.py`, `ki_openai.py`, `lagring_sqlite.py`, `demo.py`), `start/`, `.github/workflows/`, [`README.md`](../../../README.md) og [`docs/installasjon.md`](../../../docs/installasjon.md). Kravene står i [PRD-en](../prds/prd-G74-lund-osen-2026-09-20/prd.md), og beslutningene i [arkitekturen](architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md).

---

## 1. Hva systemet er

En lokal webapp som viser 15 aksjer på Oslo Børs, opptil 18 med «Følg en aksje». Tre sjekker, trend, bevegelse og interesse, gir hver aksje en signalstyrke fra 0 til 3, og KI kan forklare signalet med ord. Appen har to deler: webserveren, som viser sidene fra basen, og hentekommandoen, som henter sluttkursene fra EODHD, regner vurderingene og lager KI-tekstene.

**Prinsippene (verdt å kopiere):**

- **Demoen trenger ingen nøkkel** (FR-411). En egen kommando lager en demobase med oppdiktede selskaper. Den gjør null API-kall, leser ingen nøkkel og virker uten nett. Hver side som viser den, sier «Eksempeltall».
- **Webserveren henter aldri** (FR-401, NFR-02). Den starter uten nøkkel og uten API-kall og viser siste kjente data. Henting er en egen kommando i en egen prosess.
- **KI er valgfritt** (NFR-04, FR-608). Svarer ikke modellen, eller er KI slått av, lages ingen KI-tekst, og kursene og vurderingene hentes som før. Ingen nøkkel følger med appen eller repoet.

---

## 2. Tjenestene

```
Nettleser (bare på maskinen)
   │  http://127.0.0.1:8000
   ▼
┌──────────────────────────┐        ┌──────────────────────────────┐
│ webserveren              │  leser │ SQLite-basen                 │
│ Flask, servert av        │◄──────►│ data/db/ose.db (ekte)        │
│ waitress. Henter aldri,  │ skriver│ data/db/demo.db (demoen)     │
│ ingen nøkkel             │ notater│                              │
└──────────────────────────┘ m.m.   └──────────────▲───────────────┘
                                                   │ skriver
┌──────────────────────────┐                       │
│ hentekommandoen          │───────────────────────┘
│ src/fetch_prices.py      │──► data/raa/ (øyeblikksbildene, skrives én gang)
│ EODHD_API_KEY, OSE_KI_*  │──► EODHD: /api/eod (kursene), /api/user (kvoten)
└──────────┬───────────────┘
           │ én tjeneste per kjøring
           ├──► Ollama med Gemma på maskinen (standard, ingen nøkkel)
           └──► Gemini / Anthropic / OpenAI (valgfritt, egen nøkkel)

Startes av: «Start demoen» / «Start den ekte versjonen» (start/), docker compose,
eller kveldsjobben i Oppgaveplanlegging (start/kveldshenting.ps1).
```

| Tjeneste | Rolle | Offentlig? |
| --- | --- | --- |
| Webserveren (`src/app.py`) | Flask-appen, servert av waitress. Viser sidene fra basen, henter aldri og har ingen nøkkel. Skriver bare brukerens egne valg, som Min liste, innstillingene og notatene | nei, bare 127.0.0.1 |
| SQLite-basen | `data/db/ose.db` med kursene, vurderingene og KI-tekstene. Demobasen `data/db/demo.db` ligger ved siden av (`lagring_sqlite.py`) | nei |
| Øyeblikksbildene | `data/raa/`, svarene fra EODHD som JSON, skrevet én gang og aldri om (AD-6, NFR-07) | nei |
| Hentekommandoen | `src/fetch_prices.py`: sjekker kvoten, henter kursene og hovedindeksen, skriver vurderingene og så KI-tekstene. Nekter på en børsdag før kl. 22:00, utenom første henting i en tom base (FR-401) | nei |
| Demokommandoen | `src/demo.py` lager demobasen med 15 oppdiktede selskaper. Ferdige KI-tekster følger med i `src/demo_ki_tekster.json` | nei |
| EODHD | Ekstern kilde: `https://eodhd.com/api/eod` for sluttkursene og `https://eodhd.com/api/user` for kvoten (`fetch_prices.py`) | ekstern |
| Ollama med Gemma | Standardmodellen for KI-teksten, `gemma4:e4b` på `http://127.0.0.1:11434` (`ki_lokal.py`) | nei |
| Gemini, Anthropic, OpenAI | Valgfrie, med brukerens egen nøkkel (story 10.7). Grunnlaget sendes da til tjenesten som er valgt | ekstern |
| Kveldsjobben | Oppgaveplanlegging i Windows, valgfri: `start/legg-inn-kveldshentingen.ps1` legger den inn, `start/kveldshenting.ps1` kjører, `start/ta-bort-kveldshentingen.ps1` tar den bort | nei |
| Startskriptene | «Start demoen» og «Start den ekte versjonen» i rota, `.cmd` for Windows (`start/start.ps1`) og `.command` for Mac (`start/start.sh`) | nei |
| Docker (valgfritt) | `Dockerfile` og `compose.yaml` med tjenestene `app`, `hent`, `demo-lag`, `demo` og `ollama`, i tabellen «Docker-tjenestene» | nei, bare 127.0.0.1 |

**Docker-tjenestene** (`compose.yaml`). Alle bygger det samme imaget `ose-signal` fra repoet, utenom `ollama`:

| Tjeneste | Profil | Hva den gjør | Volum |
| --- | --- | --- | --- |
| `app` | ingen | Webserveren, port `127.0.0.1:8000` | `ose-db` |
| `hent` | `hent` | `python src/fetch_prices.py`, med `.env` og `OSE_KI_OLLAMA_URL=http://ollama:11434` | `ose-db`, `ose-raa` |
| `demo-lag` | `demo` | `python src/demo.py`, lager demobasen | `ose-demo` |
| `demo` | `demo` | Webserveren med `OSE_DEMO=1`, starter når `demo-lag` er ferdig | `ose-demo` |
| `ollama` | `ki` | `ollama/ollama:0.35.1` med grafikkort fra NVIDIA, port `127.0.0.1:11434` | `ose-ki-ollama` |

`app`, `hent`, `demo-lag` og `demo` har skrivebeskyttet rotfilsystem med `/tmp` som tmpfs. Bare `hent` får `.env`.

---

## 3. Teknologien

| Område | Valg |
| --- | --- |
| Språk og runtime | Python 3.13 eller nyere (`requires-python = ">=3.13"`). Imaget bruker `python:3.13.15-slim` |
| Pakkehåndtering | **uv**, med låste versjoner i `uv.lock`. Imaget installerer med `uv sync --locked --no-dev` |
| Web-rammeverk | **Flask** (låst til 3.1.3), med maler i **Jinja** (`src/templates/`) og stilark og skript i `src/static/` |
| Webserver | **waitress** (låst til 3.0.2), 8 tråder, i startskriptene og i Docker. Aldri debug |
| HTTP-klient | **requests**, i hentingen og KI-klientene (`ki_lokal.py`, `ki_sky.py`) |
| Konfigurasjon | **python-dotenv**: `fetch_prices.py` og `ki_tekst.py` leser `.env` i prosjektroten |
| Tidssone | **tzdata**, så `Europe/Oslo` virker også uten tidssonedatabase i imaget (AD-20) |
| Database | **SQLite** gjennom `sqlite3` i standardbiblioteket, én fil per base |
| Migrasjoner | SQL-filer i `src/migrasjoner/` (`0001_kurs.sql` til `0014_regnet.sql`), kjørt av `aapne_base` i `lagring_sqlite.py` |
| Tester | **pytest**, uten nett: `tests/conftest.py` sperrer utgående tilkoblinger (AD-8) |
| Lint og format | **ruff** 0.17.1 med pyflakes, importene og bugbear (`pyproject.toml`) |
| CI | GitHub Actions: `tester.yml` kjører ruff og pytest på Ubuntu med Python 3.13, bygger og prøver imaget, og prøver dobbeltklikket på Windows og macOS. `morgensjekk.yml` er en planlagt sjekk av repoet. Ingen av dem har nøkkelen til EODHD eller KI-tjenestene, og ingen gjør kall mot EODHD |

Avhengighetene er bare de fem i `pyproject.toml`: flask, requests, python-dotenv, tzdata og waitress. pytest og ruff er i dev-gruppen.

---

## 4. Drift

| Del | Valg |
| --- | --- |
| Hvor | Bare lokalt, på maskinen. Webserveren lytter på `127.0.0.1:8000`, også i Docker, der `compose.yaml` binder porten bare til 127.0.0.1 («betingelsen fra EODHD 21.09: lokalt, ikke publisert») |
| Start uten Docker | Dobbeltklikk, eller `uv run python src/app.py` (med `--demo` for demoen), som bruker Flasks egen server uten debug på port 8000. Skriptene starter `waitress-serve --listen=127.0.0.1:8000 --threads=8 app:app` |
| Start med Docker | `docker compose up --build` for den ekte versjonen, `docker compose up --build demo` for demoen. Begge bruker port 8000, så bare én kan kjøre om gangen |
| Henting | Etter kl. 22:00 på en børsdag, med `uv run python src/fetch_prices.py` eller `docker compose run --rm hent` |
| Kveldsjobben | Hver dag kl. 22:15, og igjen kl. 22:45, 23:15 og 23:45. Den kjører fra en egen arbeidskopi av main, der `data/` og `.env` er lenker til hovedmappa, og logger til `data/logg/kveldshenting-<dato>.log`. Den starter Docker Desktop og Ollama hvis de ikke kjører, og henter uten KI-tekst hvis de ikke svarer innen tre minutter |
| Kvoten | 20 kall i døgnet på gratisnivået. En henting koster ett kall per aksje og ett for hovedindeksen, 16 med 15 aksjer (NFR-01). `/api/user` leses før første kall |
| Data | Basen og øyeblikksbildene kan ikke lages på nytt, fordi vurderingene gjelder dagen de ble skrevet (AD-7). Skriv aldri `docker compose down -v`, som sletter volumene `ose-db` og `ose-raa` |

---

## 5. Nøkler og miljøvariabler

Typene: **hemmelig** (står bare i `.env`, som aldri committes), **ikke hemmelig** (innstilling), **valgfri** (appen virker uten). Demoen trenger ingen av dem.

### 5.1 I `.env` (malen er `.env.example`)

| Variabel | Type | Hvor du får den | Hva den gjør |
| --- | --- | --- | --- |
| `EODHD_API_KEY` | hemmelig | Gratiskonto på eodhd.com: «API token» under «Dashboard» | Nøkkelen hentekommandoen bruker mot EODHD. Mangler den, stopper hentingen før første kall. Webserveren og demoen bruker den ikke |
| `OSE_KI_TJENESTE` | ikke hemmelig | Settes selv, eller av startskriptet første gang | `lokal`, `gemini`, `anthropic`, `openai` eller `av`. Uten variabelen gjelder `lokal`; en tom eller ukjent verdi gir ingen KI-tekst (FR-608) |
| `OSE_KI_OLLAMA_URL` | ikke hemmelig, valgfri | Settes selv | Adressen til Ollama. Standard er `http://127.0.0.1:11434`; `compose.yaml` og kveldsjobben setter den selv. Peker den bort fra maskinen, sier hentingen at prompten sendes dit |
| `OSE_KI_GEMINI_NOKKEL` | hemmelig, valgfri | Egen konto hos Google for Gemini API | Brukes bare med `OSE_KI_TJENESTE=gemini`. Modellen er `gemini-3.5-flash-lite` |
| `OSE_KI_ANTHROPIC_NOKKEL` | hemmelig, valgfri | Egen konto hos Anthropic API | Brukes bare med `OSE_KI_TJENESTE=anthropic`. Modellen er `claude-haiku-5-5` |
| `OSE_KI_OPENAI_NOKKEL` | hemmelig, valgfri | Egen konto hos OpenAI API | Brukes bare med `OSE_KI_TJENESTE=openai`. Modellen er `gpt-6-luna` |

`OSE_KI_*` leses fra miljøet først og så fra `.env` (`ki_tekst.py`). Mangler nøkkelen til tjenesten som er valgt, lages ingen KI-tekst, og hentingen sier hvilken variabel det gjelder. Det er én tjeneste per kjøring, uten overgang til en annen.

### 5.2 Satt av skriptene eller Docker, ikke i `.env`

| Variabel | Type | Hvem setter den | Hva den gjør |
| --- | --- | --- | --- |
| `OSE_DEMO` | ikke hemmelig | `start/start.ps1`, `start/start.sh`, tjenesten `demo` i `compose.yaml`, eller flagget `--demo` | `1` får webserveren til å åpne `demo.db` i stedet for `ose.db`. Webserveren lager aldri demobasen selv |
| `OSE_I_DOCKER` | ikke hemmelig | `Dockerfile` | `1` får den tomme siden til å vise Docker-kommandoene for henting og demo i stedet for uv-kommandoene |

### 5.3 Bare for testene og CI (startskriptene)

Startskriptene i `start/` leser noen variabler som lar testene og CI svare på spørsmålene i vinduet. En vanlig bruker setter ingen av dem.

| Variabel | Hva den gjør |
| --- | --- |
| `OSE_START_SVAR_JA` | `1` svarer ja til uv og venter ikke på Enter, og gir verken spørsmålet om snarveien eller om KI |
| `OSE_START_UTEN_NETTLESER` | `1` åpner ingen nettleser |
| `OSE_START_SVAR_FRIST` | Sekundene et spørsmål venter, ellers 30 |
| `OSE_START_SVAR_SNARVEI` | Svaret på spørsmålet om snarveien (`j` eller `n`) |
| `OSE_SKRIVEBORD` | Mappa snarveien lages i; testene gir en midlertidig mappe |
| `OSE_START_SVAR_KI`, `OSE_START_SVAR_KI_TJENESTE`, `OSE_START_SVAR_KI_NOEKKEL` | Svarene på spørsmålet om KI: valg 1, 2 eller 3, tjenesten (`g`, `a` eller `o`) og nøkkelen, bare falske nøkler i testene |
| `OSE_START_OLLAMA_URL`, `OSE_START_OLLAMA_VENT` | Adressen startskriptet prøver Ollama på, og hvor lenge det venter |

---

## 6. Kontoer som trengs

| # | Tjeneste | Brukes til | Påkrevd? |
| --- | --- | --- | --- |
| 1 | Ingen | Demoen | nei, demoen trenger verken konto eller nøkkel |
| 2 | **EODHD**, gratiskonto | Sluttkursene i den ekte versjonen. 20 kall i døgnet, og en henting bruker 16 med 15 aksjer og 19 med 18 | ja, for den ekte versjonen |
| 3 | **Ollama** med Gemma | Lokal KI-tekst. Ingen konto og ingen nøkkel | valgfritt |
| 4 | **Gemini**, **Anthropic** eller **OpenAI** | KI-teksten med egen nøkkel, i stedet for Ollama. Kan koste hos tjenesten | valgfritt |
| 5 | **Docker Desktop** | Kjøring i Docker, og Ollama i Docker | valgfritt |

Ingen del av v1 krever betaling (NFR-01).

---

## 7. Demoen uten nøkler

Demoen er hovedveien for faglærer og sensor (FR-411). Den bruker `data/db/demo.db` med 15 oppdiktede selskaper, en fast dag (fredag 09.10.2026) og ferdige KI-tekster. Den henter aldri og spør aldri om KI. Tre måter å starte den på:

- **Dobbeltklikk:** pakk ut ZIP-fila og dobbeltklikk «Start demoen». Mangler uv, spør vinduet om det skal installeres. Nettleseren åpner http://127.0.0.1:8000.
- **Docker:** `docker compose up --build demo`, og stopp med `docker compose --profile demo down`.
- **uv:** `uv sync`, så `uv run python src/demo.py`, så `uv run python src/app.py --demo`.

Notatene i demoen står bare til demoen startes på nytt, fordi demobasen lages på nytt ved hver start.

---

## 8. Sjekkliste for å sette opp appen igjen

1. Last ned koden som ZIP og pakk den ut. «Start den ekte versjonen» starter bare i en kopi fra ZIP-fila, ikke i en klon med `.git`.
2. Installer uv (eller la dobbeltklikket gjøre det). uv henter Python 3.13 hvis maskinen ikke har den. Med Docker trengs Docker Desktop i stedet.
3. Prøv demoen først, som i kapittel 7. Den trenger ingen nøkkel.
4. Lag en gratiskonto hos EODHD og kopier «API token» under «Dashboard».
5. Kopier `.env.example` til `.env` og lim inn nøkkelen etter `EODHD_API_KEY=`. Dobbeltklikket gjør dette selv første gang. `.env` committes aldri.
6. Velg KI-tekst: la `OSE_KI_TJENESTE=lokal` stå og hent modellen med `ollama pull gemma4:e4b` (i Docker: `docker compose --profile ki up -d ollama` og `docker compose exec ollama ollama pull gemma4:e4b`), sett en egen nøkkel, eller sett `OSE_KI_TJENESTE=av`.
7. Start webserveren: `docker compose up --build` eller `uv run python src/app.py`, og åpne http://127.0.0.1:8000. Første gang er oversikten tom og viser kommandoen som henter.
8. Hent kursene: `docker compose run --rm hent` eller `uv run python src/fetch_prices.py`. Første gang går det når som helst, og før kl. 22 på en børsdag gir det forrige børsdag. Etterpå hentes det etter kl. 22 på en børsdag.
9. Valgfritt på Windows: legg inn kveldsjobben fra en egen arbeidskopi, som beskrevet under «Hentingen hver kveld med Oppgaveplanlegging» i [installasjonen](../../../docs/installasjon.md).
10. Kontroller med `uv sync` og `uv run pytest` at testene består. De gjør ingen nettkall.
11. Ta vare på `data/`. Basen og øyeblikksbildene kan ikke lages på nytt, så skriv aldri `docker compose down -v`.
