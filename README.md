# OSE Signal

[![tester](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml/badge.svg)](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml)

Gruppe G74 (Ai Ai Ai) i IBE160 Programmering med KI, Høgskolen i Molde, høsten 2026.

OSE Signal samler kursutvikling og signalstyrke for 15 likvide Oslo Børs-aksjer i én oversikt, så en vanlig sparer kan se hva som har endret seg og hvorfor. Beregningene gjøres med vanlig programkode, og KI skal forklare signalet med ord.

## Status

Under arbeid, og ingenting er endelig. Vi jobber med to versjoner samtidig, med samme kode:

- **Den ekte versjonen** henter sluttkurser fra EODHD hver børsdag og lagrer dagens vurdering per aksje. Markedsoversikten og aksjedetaljen leser fra basen. Den krever en egen gratis nøkkel fra EODHD.
- **Demoversjonen** har oppdiktede selskaper og kurser, og kan prøves uten konto og uten nøkkel. Den er den enkleste måten å prøve appen på: `docker compose up --build demo` (se «Kom i gang»).

Børsdagskontrollen (2.3), Docker (3.1 og 3.2), denne oppskriften (3.3) og demoversjonen (3.4) er flettet til `main`. Neste er README-prøven 13.–16.10, så nye forsøk med kallene som er igjen (2.3b), hjelp bak et spørsmålstegn (8.0b) og tydeligere merking (8.0c), og så KI-laget. Det som bygges etter demoen, skal vises i begge versjonene. Børsmeldinger er ikke med i v1, fordi Euronext ikke ga tillatelse til automatisert henting (plan B). Se [sprintstatusen](_bmad-output/implementation-artifacts/sprint-status.yaml).

Til faglærer: leveranselista står i [`docs/innlevering.md`](docs/innlevering.md), og kvalitetssikringen i [`docs/kvalitetssikring.md`](docs/kvalitetssikring.md). Prosessen og valgene våre står i [`docs/reflection-log.md`](docs/reflection-log.md).

## Kom i gang

Docker er hovedmåten: Docker Desktop på Windows og Mac, eller Docker Engine med Compose på Linux. Kommandoene er de samme i PowerShell på Windows og i Terminal på Mac og Linux.

### Før du begynner

- En Windows-maskin eller en Mac. På Linux bruker du Docker Engine med Compose og kommandoene i steg 6 og 8.
- Lov til å installere programmer. På Windows betyr det å være administrator på maskinen, eller å ha en som kan godkjenne.
- Nett. Docker Desktop og den første byggingen laster ned en del.
- Litt tid. Første gang tar installasjonen og byggingen en stund. Neste gang går det raskere.

Demoen trenger verken git, konto eller nøkkel. Du laster ned koden som en ZIP-fil og skriver to kommandoer i et terminalvindu.

### Demoen, steg for steg

**1. Installer Docker Desktop.** Last det ned fra [docker.com](https://www.docker.com/products/docker-desktop/), og kjør installasjonen.

- Windows: åpne fila du lastet ned, og behold valgene som er krysset av. Spør Windows om programmet får gjøre endringer, svarer du ja. Ber Windows om omstart, gjør det.
- Mac: velg «Apple Silicon» hvis Apple-menyen → Om denne maskinen (About This Mac) viser en M-brikke på linja Brikke (Chip), ellers «Intel». Åpne fila og dra Docker til Programmer (Applications).

Når det har gått bra, ligger Docker Desktop i Start-menyen (Windows) eller i Programmer (Mac). Ber installasjonen om administrator, se [Hvis noe går galt](#hvis-noe-går-galt).

**2. Start Docker Desktop, og vent til motoren kjører.** Åpne Docker Desktop fra Start-menyen eller Programmer. Første gang godtar du vilkårene. Du trenger ikke logge inn eller lage konto, så hopp over innloggingen hvis Docker Desktop spør.

Når det har gått bra, står det «Engine running» nederst i vinduet. La Docker Desktop være åpent, men skriv ingenting i det. Står det ikke «Engine running» etter noen minutter, se [Hvis noe går galt](#hvis-noe-går-galt).

**3. Last ned koden.** Gå til [repoet på GitHub](https://github.com/IBE160-2026/G74-lund-osen), trykk den grønne knappen «Code» og så «Download ZIP». Pakk ut fila:

- Windows: åpne Nedlastinger (Downloads) i Filutforsker (File Explorer), høyreklikk ZIP-fila `G74-lund-osen-main` og velg «Pakk ut alle» (Extract All) og så «Pakk ut» (Extract). Du må pakke ut: åpner du ZIP-fila i stedet, ser den ut som en vanlig mappe, men den er ikke pakket ut.
- Mac: dobbeltklikk `G74-lund-osen-main.zip` i Nedlastinger (Downloads).

Når det har gått bra, har du en mappe som heter `G74-lund-osen-main`, med blant annet filene README og compose. Windows viser dem uten filendelsen (.md og .yaml). Ligger det en mappe med samme navn inni den, er det den innerste du skal bruke. Har du fått koden som mappe eller ZIP-fil fra før, pakker du den ut og går til steg 4.

**4. Åpne et terminalvindu.** Et terminalvindu er et vindu der du skriver kommandoer i stedet for å klikke.

- Windows: trykk Start, skriv `PowerShell` og åpne «Windows PowerShell». Ikke velg «Windows PowerShell ISE», som også står i lista.
- Mac: trykk Cmd+mellomrom, skriv `Terminal` og trykk Enter.

Når det har gått bra, ser du et vindu med en linje som venter på at du skriver.

**5. Gå til mappa med koden.** Skriv `cd` og et mellomrom i terminalvinduet, dra mappa `G74-lund-osen-main` fra Filutforsker eller Finder inn i vinduet, og trykk Enter. `cd` betyr «gå til mappe», og kommandoene under virker bare fra mappa med koden.

Når det har gått bra, slutter linja som venter, med `G74-lund-osen-main`.

**6. Start demoen.** Kopier kommandoen under med knappen til høyre i boksen, lim den inn i terminalvinduet og trykk Enter:

```
docker compose up --build demo
```

Første gang bygger Docker appen. Det tar noen minutter, og det kommer mange linjer i vinduet. Når det har gått bra, er den siste linja denne:

```text
demo-1  | INFO:waitress:Serving on http://0.0.0.0:5000
```

La terminalvinduet stå åpent mens du bruker demoen. `0.0.0.0` er adressen inne i Docker, og du åpner adressen i neste steg. Kommer det en feil i stedet, se [Hvis noe går galt](#hvis-noe-går-galt).

**7. Åpne demoen i nettleseren.** Gå til http://127.0.0.1:5000.

Når det har gått bra, står det øverst på siden: «Eksempeltall: oppdiktede selskaper og kurser, ikke data fra Oslo Børs.» Under står en tabell med aksjer. Klikk på et selskapsnavn for å se aksjen.

**8. Stopp demoen.** Gå tilbake til terminalvinduet og trykk Ctrl+C, også på Mac. Lim så inn denne og trykk Enter:

```
docker compose --profile demo down
```

Når det har gått bra, står det at containerne er fjernet (Removed). Nå kan du lukke terminalvinduet og Docker Desktop. Neste gang starter du på steg 2 og hopper over steg 3.

Sidene sier «Eksempeltall»: 15 oppdiktede selskaper med kurser til fredag 9. oktober 2026, ikke data fra Oslo Børs. Demoen trenger verken `.env` eller nøkkel, og gjør ingen kall. Demobasen lages på nytt hver gang demoen starter, i sitt eget volum, `ose-demo`. Den ekte basen røres ikke. Mens demoen kjører, kan demobasen også lages på nytt med `docker compose run --rm demo-lag` i et nytt terminalvindu, fra samme mappe.

### Hvis noe går galt

**Må jeg logge inn eller lage konto?** Nei. Hopp over innloggingen i Docker Desktop. Demoen trenger verken Docker-konto, GitHub-konto eller nøkkel.

**Installasjonen ber om administrator.** Docker Desktop må installeres av en som er administrator på maskinen. Spør den som har ansvar for maskinen, eller bruk en annen maskin.

**Docker Desktop sier at virtualisering mangler.** Virtualisering må være slått på i maskinens oppstartsinnstillinger (BIOS eller UEFI). Hvordan, er forskjellig fra maskin til maskin. Spør den som har ansvar for maskinen, eller søk på maskinmodellen og «enable virtualization».

**Docker Desktop ber om å oppdatere WSL (Windows).** Følg beskjeden, eller lim inn `wsl --update` i PowerShell og start Docker Desktop på nytt.

**Det står ikke «Engine running» etter noen minutter.** Avslutt Docker Desktop helt (Quit Docker Desktop), åpne det igjen og vent. Hjelper ikke det, starter du maskinen på nytt.

**«docker» er ikke gjenkjent, eller «command not found: docker».** Docker Desktop er ikke installert, eller terminalvinduet ble åpnet før installasjonen. Lukk terminalvinduet og åpne et nytt (steg 4).

**«Cannot connect to the Docker daemon», «error during connect» eller «dockerDesktopLinuxEngine».** Docker Desktop er ikke startet, eller motoren er ikke klar. Gjør steg 2, vent til det står «Engine running», og prøv kommandoen igjen.

**Ingenting skjer når jeg limer inn.** Kommandoene skrives i PowerShell eller Terminal, ikke i Docker Desktop. Docker Desktop skal bare være åpent. Ledetekst (Command Prompt) på Windows virker også for demoen, men stegene er skrevet for PowerShell.

**To kommandoer havnet på samme linje**, for eksempel med feilen «no such service». Lim inn én kommando om gangen, og trykk Enter etter hver. Står det noe på linja fra før, sletter du det først.

**Stien har mellomrom og fikk ikke anførselstegn.** Får du en feil etter `cd` når mappa ligger i en mappe med mellomrom i navnet, skriver du anførselstegn rundt stien, for eksempel `cd "C:\Users\Ola Nordmann\Downloads\G74-lund-osen-main"`.

**ZIP-fila ser ut som en vanlig mappe.** Står det «Komprimert størrelse» (Compressed size) som kolonne og «Pakk ut alle» (Extract All) øverst i vinduet, er du inne i ZIP-fila, og den er ikke pakket ut. Trykk «Pakk ut alle», og bruk mappa som lages (steg 3).

**«no configuration file provided: not found».** Terminalvinduet står i feil mappe. Gjør steg 5 på nytt, og dra den mappa der fila compose ligger. Windows viser den uten filendelsen, som compose og ikke compose.yaml.

**«toomanyrequests» fra Docker Hub.** Docker Hub begrenser hvor ofte en nettadresse kan laste ned uten innlogging. Prøv igjen senere, eller fra et annet nett. Innlogging i Docker Desktop hever grensen, men trengs ellers ikke.

**«port is already allocated» eller «address already in use».** Noe annet bruker port 5000. Kjører den ekte versjonen, stopper du den først (se «Bytte mellom demoen og den ekte versjonen»). På Mac bruker AirPlay-mottakeren (AirPlay Receiver) port 5000. Slå den av under Systeminnstillinger (System Settings) → Generelt (General) → AirDrop og Handoff (AirDrop & Handoff), og prøv igjen.

**Mappa finnes fra før.** Ligger det en `.env` med nøkkelen din i den gamle mappa, flytter du den ut først. Slett så den gamle mappa og pakk ut på nytt. Demodataene ligger i Docker, ikke i mappa, så de går ikke tapt. Har du hentet koden med `git clone`, går du heller inn i mappa og skriver `git pull`.

**Siden åpnes ikke.** Vent til linja med «Serving on» har kommet, og sjekk at terminalvinduet fortsatt er åpent. Adressen er http://127.0.0.1:5000, ikke 0.0.0.0.

### Den ekte versjonen, med egen nøkkel

Bare første gang: kopier malen, og fyll inn `EODHD_API_KEY` i `.env` (se «Nøkkelen» under).

```
cp .env.example .env
```

Start webserveren på http://127.0.0.1:5000:

```
docker compose up --build
```

Hent kursene i et nytt vindu, fra samme mappe:

```
docker compose run --rm hent
```

Last siden på nytt når hentingen er ferdig. Stopp med `Ctrl+C` i vinduet med webserveren, eller med:

```
docker compose down
```

- **Nøkkelen.** Du trenger en egen gratis API-nøkkel fra [EODHD](https://eodhd.com/register), fordi vilkårene ikke lar oss dele vår. Den gir 20 kall i døgnet, og en henting bruker 15. Åpne `.env` i en teksteditor (`notepad .env` på Windows, `open -e .env` på macOS, `nano .env` på Linux) og lim den inn etter `EODHD_API_KEY=`. `cp` skriver over en `.env` som finnes, så kopier bare første gang. Webserveren starter uten `.env` og bruker aldri kvote: den leser bare fra basen. Bare hentingen trenger nøkkelen, og `docker compose run --rm hent` starter ikke uten `.env`.
- **Når du henter.** Hent etter kl. 22 og før midnatt på en børsdag. Første gang kan du også hente i helgen: da henter den siste børsdag, fordi basen mangler den. På dagtid en børsdag stopper hentingen med 0 kall og sier hvorfor: dagens sluttkurs er ikke klar ennå, og en vurdering kan ikke fylles inn senere. Har basen alt kursene for børsdagen, bruker den også 0 kall. På en dag børsen er stengt henter den bare hvis basen mangler forrige børsdag og fila for den dagen ikke finnes. Før kallene leser den kvoten med `/api/user`, som er gratis.
- **Uten henting** starter appen med tom oversikt og viser kommandoen som henter. Utskriften fra hentingen sier hvilken børsdag vurderingene gjelder, og hvilke aksjer som fikk en grunn i stedet for en vurdering.
- **Dataene** ligger i to Docker-volumer: `ose-db` med basen og `ose-raa` med øyeblikksbildene fra EODHD. De står når containerne stoppes. **Bruk aldri `docker compose down -v`.** `-v` fjerner begge volumene, og verken øyeblikksbildene eller vurderingene kan hentes på nytt. Basen kan heller ikke slettes og bygges opp igjen: kursene kan hentes på nytt, men vurderingene for dagene som har gått, kan ikke lages på nytt.
- **Porten** er bare åpen på maskinen selv (127.0.0.1). Appen kan ikke nås fra nettet.

### Bytte mellom demoen og den ekte versjonen

Begge bruker port 5000, så bare én kan kjøre om gangen. `docker compose down` stopper ikke demoen, fordi demoen ligger i en egen profil. `docker compose --profile demo down` stopper begge. Start så den du vil bruke:

Stopp demoen og den ekte versjonen:

```
docker compose --profile demo down
```

Start så den ekte versjonen:

```
docker compose up --build
```

eller demoen:

```
docker compose up --build demo
```

Volumene står når du bytter, også basen med vurderingene.

### Uten Docker, med uv

Med Python 3.13 og [uv](https://docs.astral.sh/uv/). Demoen:

Installer avhengighetene:

```
uv sync
```

Lag demobasen, `data/db/demo.db`:

```
uv run python src/demo.py
```

Start demoen på http://127.0.0.1:5000:

```
uv run python src/app.py --demo
```

Den ekte versjonen:

Bare første gang: kopier malen, og fyll inn `EODHD_API_KEY` i `.env`.

```
cp .env.example .env
```

Hent kurser:

```
uv run python src/fetch_prices.py
```

Start webserveren på http://127.0.0.1:5000:

```
uv run python src/app.py
```

Basen, demobasen og øyeblikksbildene ligger da i `data/` i mappa. Uten `--demo` åpner webserveren den ekte basen.

## Tester

```
uv run pytest
```

- Ingen nettkall: `tests/conftest.py` sperrer nettverket i hver test.
- `data/` røres ikke: testene bruker en midlertidig mappe.
- CI kjører på hver push og pull request mot `main`, uten hemmeligheter og uten API-nøkkel.

Hver story som endrer koden, leveres med tester. Det er vårt svar på hvordan KI-generert kode kvalitetssikres, og alt står i [`docs/kvalitetssikring.md`](docs/kvalitetssikring.md).

## Dokumentene

`docs/` viser hvordan vi kom fram til noe og hvilken rolle KI spilte, og `_bmad-output/` viser hva vi kom fram til.

**Plan og krav**

- [Product Brief](_bmad-output/planning-artifacts/product-brief.md), låst i taggen `arbeidskrav-product-brief-v7`, med [tilbakemelding fra faglærer 06.10](_bmad-output/planning-artifacts/tilbakemelding-product-brief.md) *Lagt til 2026-10-06:* versjon 8 er lagt inn etter tilbakemeldingen, med taggen `arbeidskrav-product-brief-v8` og commit `52023c9`.
- [PRD](_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/), med begrunnelser og målinger
- [Relevanseksperimentet](_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/relevanseksperiment.md)
- [Arkitektur](_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md)
- [Epics og stories](_bmad-output/planning-artifacts/epics.md)
- [Designregler](_bmad-output/planning-artifacts/designregler.md)
- [Endringsforslag 28.09](_bmad-output/planning-artifacts/sprint-change-proposal-2026-09-28.md), godkjent av gruppen 28.09
- [Endringsforslag 08.10](_bmad-output/planning-artifacts/sprint-change-proposal-2026-10-08.md): femten idéer inn i v1, godkjent av Marian 08.10
- [Kilder og bruksvilkår](docs/kilder-og-rettigheter.md), med e-postene til [EODHD](docs/epost-til-eodhd.md) og [Euronext](docs/epost-til-euronext.md)
- [Leveranseliste](docs/innlevering.md)

**Arbeidsprosess og kvalitet**

- [Sprintstatus og story-spesifikasjoner](_bmad-output/implementation-artifacts/)
- [Kvalitetssikring](docs/kvalitetssikring.md)
- [Kontrollrapport 22.09](docs/kontroll-2026-09-22.md), med [rettingsplanen](docs/kontroll-2026-09-22-plan.md)
- [Kontrollrapport 26.09](docs/kontroll-2026-09-26.md)
- [Refleksjonslogg](docs/reflection-log.md) og [lagrede KI-prompts](docs/ai-prompts/)

## Mappestruktur

- `src/` og `tests/` — applikasjonen og testene
- `docs/` — arbeidsprosessen
- `_bmad-output/` — plan, krav og sprintstatus
- `.github/` — testkjøringen og morgensjekken
- `Dockerfile`, `compose.yaml` og `.dockerignore` — imaget og tjenestene: webserveren, hentingen og demoen
- `_bmad/`, `.claude/skills/` og `.agents/skills/` — BMAD-rammeverket, ikke skrevet av oss

Ikke i repoet: API-nøkkelen (`.env`), rådata, basen og demobasen (`data/`), lokale testskript (`local-tests/`) og den private arbeidsmappa (`_privat/`).

## Medlemmer

Joakim Lund og Marian Osen. Fra 25.09 har felles commits `Co-authored-by` for den av oss som ikke committet (regel 20 i `CLAUDE.md`).
