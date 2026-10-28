---
title: 'Story 2.3d: hentingen går av seg selv hver kveld'
type: 'feature'
created: '2026-10-28'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '85998f6'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/implementation-artifacts/deferred-work.md'
  - '{project-root}/src/fetch_prices.py'
  - '{project-root}/README.md'
  - '{project-root}/docs/hjelp.md'
---

## Intent

**Problem:** hentingen kjøres for hånd hver kveld med en instruksjon. En kveld uten henting er en vurdering som mangler for alltid (AD-7).

**Løsningen:** en jobb i Oppgaveplanlegging på Windows starter `start/kveldshenting.ps1` hver kveld, fra en egen arbeidskopi av main på commiten main hadde ved midnatt. Skriptet gjør det stegene 2–7 i hentingsinstruksjonene gjør, og skriver alt til en logg i `data/`. `start/legg-inn-kveldshentingen.ps1` legger inn jobben, og `start/ta-bort-kveldshentingen.ps1` tar den bort.

**Grunnlaget:** story 2.3d i `epics.md` (`85998f6`): beslutningen 29.09 under FR-401 i `prd.md`, svar 2 og 3 under story 2.3 (05.10 kl. 19:17), kontrollpunktet som ble flyttet ut av 2.3b, og avgjørelsene 26.10 kl. 22:58 og 27.10 kl. 20:58 i dagsfila 28.10 (`0d5e922`): bygges 28.10, første kjøring torsdag 29.10.

## Slik er det i dag (slått opp 28.10 på `85998f6`)

- **FR-401** (`prd.md`): «Avgjort 2026-09-29, gjelder når story 2.3 er bygget»: en planlagt jobb på Marians PC, Oppgaveplanlegging, hverdager kl. 22:15, tapte kjøringer tas ikke igjen, utskriften til en loggfil i `data/`. Kravteksten over står uendret til da. Svar 2 under story 2.3 (05.10) gjorde det til hver dag.
- **Story 2.3, svar 3:** jobben kjører fra en egen arbeidskopi av main, og `data/` og `.env` deles med hovedkopien uten at nøkkelen kopieres, helst uten ny kode.
- **Story 2.3b:** kontrollpunktet «Oppgaveplanlegging gjentar jobben hver halvtime fra 22:15 til 23:45» ble flyttet til et eget steg. Svar 4: ingen nye kall etter kl. 23:50.
- **ECH3 i gjennomgangen av 2.3b** (`deferred-work.md`): to nye forsøk samtidig kan lese samme tall fra `/api/user`; ingen lås mellom kjøringene. «Hører naturlig til steget med Oppgaveplanlegging.»
- **`src/fetch_prices.py`:** `TIDSGRENSE = time(22, 0)`, `KL_23_50 = time(23, 50)` (`_for_sent`), og kodene 0 (alt i orden eller ingenting å gjøre), 1 (noe mangler eller feilet, eller stoppet), 2 (argparse) og 3 (`KODE_BARE_INDEKSEN`). Stiene er faste ut fra prosjektroten (`lagring_fil.PROSJEKTROT`), og nøkkelen leses fra `.env` der (`hent_api_nokkel`). `OSE_KI_TJENESTE` i miljøet går foran `.env`, og `av` gir ingen KI-tekst (`ki_tekst.ki_innstillinger`).
- **Hentingsinstruksjonen 27.10, stegene 2–7:** forhåndskontrollen; Docker Desktop startes og motoren ventes på, Ollama startes med `docker compose --profile ki up -d ollama`, og `ollama list` skal vise `gemma4:e4b`; svarer de ikke, hentes det uten KI-tekst (NFR-04); kopi av basen; `uv run python src/fetch_prices.py` én gang med `OSE_KI_TJENESTE=lokal` og `OSE_KI_OLLAMA_URL=http://127.0.0.1:11434` bare for kommandoen; kode 1 og 3 kjøres ikke igjen; etterkontrollen; en kjøring til som skal gi 0 kall; Ollama stoppes med `docker compose --profile ki stop ollama`.
- **`start/`** har `start.ps1` og `start.sh` (3.5a). `.gitattributes` gir `*.ps1` CRLF. `tests/test_dobbeltklikk.py` kjører `start.ps1` med Windows PowerShell 5.1 i en midlertidig mappe, bare på Windows.

## Kontrollpunktene

- a) Et skript for Windows som jobben kjører, fra en egen arbeidskopi av main på commiten main hadde ved midnatt. Det deler `data/` og `.env` med hovedkopien uten å kopiere nøkkelen, starter Docker Desktop og Ollama med en tidsgrense, og henter uten KI-tekst hvis de ikke svarer (NFR-04). Det kjører hentingen med de samme innstillingene, skriver alt til en logg i `data/`, stopper bare det det selv startet, og avslutter med koden fra hentingen.
- b) Ett skript som legger inn jobben: hver dag kl. 22:15, igjen hver halvtime til 23:45, ingen ny kjøring mens en går (ECH3), tapte kjøringer tas ikke igjen, og første dato som valg. Ett skript som tar den bort. Ingen av dem kjøres nå.
- c) README-en sier hva jobben gjør, hvor loggen er, og hvordan den slås av (regel 19). `docs/hjelp.md` følger med.
- d) Tester med «Ville feilet hvis» skriptene skrev ut nøkkelen eller miljøet, kjørte fra en gren eller fra hovedkopien, brukte en nyere commit enn den fra midnatt, eller hadde andre tider enn i b).

## Valg som er gjort her

- **«Commiten main hadde ved midnatt»** er siste commit på `origin/main` (første forelder) med committer-dato før midnatt i dag, lokal tid: `git rev-list -1 --first-parent --before=<midnatt> origin/main`, etter `git fetch origin main`. En fletting på GitHub får committer-dato da den ble flettet. Feiler `fetch`, brukes `origin/main` slik den sist ble hentet, og loggen sier det.
- **Arbeidskopien løsrives** på den commiten (`checkout --detach`) før hver kjøring, så den aldri står på en gren. Har den endringer i sporede filer, stopper skriptet.
- **Skriptet selv** kan endres av utsjekken. Da kjøres den nye versjonen én gang (`-EtterUtsjekk`), så det som går i kveld, er det som var på main ved midnatt.
- **Delingen er lenker, uten ny kode i `src/`** (svar 3): `data` i arbeidskopien er en katalogkobling (`mklink /J`) og `.env` en hard lenke til hovedkopiens. Skriptet stopper hvis `data` ikke er en lenke til hovedkopiens `data`, eller `.env` ikke er en lenke til hovedkopiens `.env` (en hard lenke med samme sha256, eller en symbolsk lenke dit). En kopi av `.env` er en kopi av nøkkelen og godtas ikke. `.env` leses bare som avtrykk.
- **Loggen** er `data/logg/kveldshenting-<dato>.log` i hovedkopien, én fil per kveld som alle kjøringene den kvelden legger til. Den skrives dit også når lenkene mangler, så stoppen står i loggen. `*.log` og `data/` er i `.gitignore`.
- **Tidsgrensen** er 240 s for Docker og 240 s for Ollama og modellen (`-Tidsgrense`). Ollama regnes som klar når `docker compose exec -T ollama ollama list` viser `gemma4:e4b`, som i steg 3. Ellers `OSE_KI_TJENESTE=av` for kjøringen, som gir ingen KI-tekst og ingen rader i KI-loggen.
- **Det skriptet startet**, stoppes: Ollama med `docker compose --profile ki stop ollama`, og Docker Desktop med `docker desktop stop`. Kjørte de fra før, røres de ikke. Feiler `docker desktop stop`, kjører Docker Desktop videre, og loggen sier det.
- **Kopien av basen** fra steg 3 i instruksjonene tas ikke: jobben går fire ganger hver kveld, og basen skrives bare gjennom hentingen. Etterkontrollen i steg 5 og kjøringen til i steg 6 gjøres heller ikke; de neste kjøringene samme kveld gir 0 kall når basen har dagens kurser.
- **Jobben** går som brukeren, bare når brukeren er logget inn (`-LogonType Interactive`), fordi Docker Desktop startes som et vanlig program. `MultipleInstances IgnoreNew`, `StartWhenAvailable` av, ingen `WakeToRun`, og `ExecutionTimeLimit` 1 time. Gjentakelsen varer 1 time og 35 minutter, så 23:45 er med og 00:15 ikke.
- **Skriptene for b) testes bare ved å lese dem,** fordi instruksjonen sier at ingen av dem kjøres nå. Tidene regnes ut fra tallene i skriptet.
- **Skriptet i a) kjøres i testene på Windows** i en midlertidig mappe med et lokalt origin, en hovedkopi og en arbeidskopi, uten Docker og med en falsk uv. På Linux og i CI hoppes de fire over, og testene som leser skriptene, står.
- **«Prøve 4: hentingen hver kveld»** i §9 i `docs/kvalitetssikring.md`, fordi `test_readme_proeven_har_hver_kommando` krever en rad for hver kommando i «Kom i gang». Prøven er instruksjonen etter flettingen.
- **ECH3:** jobben starter ingen ny kjøring mens en går. En henting for hånd samtidig med jobben er ikke sperret; hjelpen sier at jobben slås av eller får gjøre seg ferdig først.

## Planen

1. Spesifikasjonen.
2. Skriptene, testene, README-en, `docs/hjelp.md` og Prøve 4 i §9 i samme commit (regel 19).
3. Hele settet, mutanten, gjennomgangen og triagen her og i PR-en.

## Mutanten

Én, med `-x`, med kopi før og sha256 mot HEAD etter: `origin/main` i stedet for commiten fra midnatt.

## Gjennomgangen

## Åpent

- **FR-401** i `prd.md` er ikke endret. Beslutningen 29.09 sier at kravet endres når 2.3 er bygget, og at oppsettet beskrives i README-en. README-en har det fra 2.3d; om kravteksten skal føres nå, avgjør gruppen.
- **Kommandoene i README-en** for arbeidskopien og lenkene er ikke kjørt, fordi instruksjonen sier at ingen arbeidskopi lages nå. De prøves i Prøve 4.
- **`docker desktop stop`** finnes bare i nyere Docker Desktop. Versjonen på PC-en er ikke slått opp her.
- **En commit som er laget før midnatt og pushet etter,** har committer-dato før midnatt og blir med. Flettinger på GitHub gjør ikke det.

## Det som ikke endres

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `.env` i repoet røres ikke (regel 22).
- Ingen jobb legges inn i Oppgaveplanlegging, og ingen arbeidskopi lages for den nå.
- `src/` endres ikke.
