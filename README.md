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

**Du trenger** en Windows-maskin eller en Mac, lov til å installere programmer, nett og noen GB ledig plass, men verken konto, nøkkel eller git. På Linux bruker du Docker Engine med Compose i stedet for Docker Desktop. Står du fast, se [Står du fast?](#står-du-fast).

### Demoen på seks steg

1. **Installer og start Docker Desktop** fra [docker.com](https://www.docker.com/products/docker-desktop/). Hopp over innloggingen. Det er klart når det står «Engine running» nederst i vinduet.
2. **Last ned koden.** Trykk den grønne knappen «Code» på [GitHub-siden](https://github.com/IBE160-2026/G74-lund-osen) og «Download ZIP» nederst i menyen. Windows: høyreklikk fila i Nedlastinger og velg «Pakk ut alle». Mac: dobbeltklikk fila.
3. **Åpne PowerShell** (Windows: trykk Start og skriv PowerShell) **eller Terminal** (Mac).
4. **Skriv `cd` og et mellomrom**, dra den innerste mappa `G74-lund-osen-main` inn i vinduet, og trykk Enter.
5. **Kopier kommandoen** med knappen i boksen, lim den inn og trykk Enter. Første gang tar det noen minutter. Demoen er klar når det står `Serving on http://0.0.0.0:5000`.

```
docker compose up --build demo
```

6. **Åpne http://127.0.0.1:5000.** Øverst står «Eksempeltall: oppdiktede selskaper og kurser, ikke data fra Oslo Børs.»

### Stopp

Trykk Ctrl+C i terminalvinduet, også på Mac. Lim så inn denne og trykk Enter. Det er klart når det står at containerne er fjernet (Removed).

```
docker compose --profile demo down
```

### Står du fast?

Klikk på spørsmålet som passer.

<details>
<summary>Må jeg logge inn eller lage konto?</summary>

Nei. Hopp over innloggingen i Docker Desktop. Demoen trenger verken Docker-konto, GitHub-konto eller nøkkel.

</details>

<details>
<summary>Hvilken Docker Desktop skal jeg velge?</summary>

Windows: den vanlige (AMD64), med mindre maskinen har en ARM-prosessor. Mac: «Apple Silicon» hvis Apple-menyen → Om denne maskinen (About This Mac) viser en M-brikke på linja Brikke (Chip), ellers «Intel».

</details>

<details>
<summary>Hva skjer under installasjonen?</summary>

Windows: åpne fila du lastet ned, og behold valgene som er krysset av. Spør Windows om programmet får gjøre endringer, svarer du ja. Ber Windows om omstart, gjør det. Mac: åpne fila og dra Docker til Programmer (Applications). Første gang Docker Desktop starter, godtar du vilkårene, og på Mac kan det be om passordet ditt. Docker Desktop ligger så i Start-menyen (Windows) eller i Programmer (Mac).

</details>

<details>
<summary>Installasjonen ber om administrator.</summary>

Docker Desktop må installeres av en som er administrator på maskinen. Spør den som har ansvar for maskinen, eller bruk en annen maskin.

</details>

<details>
<summary>Docker Desktop sier at virtualisering mangler.</summary>

Virtualisering må være slått på i maskinens oppstartsinnstillinger (BIOS eller UEFI). Hvordan, er forskjellig fra maskin til maskin. Spør den som har ansvar for maskinen, eller søk på maskinmodellen og «enable virtualization».

</details>

<details>
<summary>Docker Desktop ber om å oppdatere WSL (Windows).</summary>

Følg beskjeden, eller lim inn `wsl --update` i PowerShell og start Docker Desktop på nytt.

</details>

<details>
<summary>Det står ikke «Engine running» etter noen minutter.</summary>

Avslutt Docker Desktop helt: høyreklikk hvalen ved klokka (Windows) eller klikk den i menylinja øverst (Mac), og velg «Quit Docker Desktop». Åpne det igjen og vent. Hjelper ikke det, starter du maskinen på nytt.

</details>

<details>
<summary>ZIP-fila ser ut som en vanlig mappe.</summary>

Du må pakke ut. Står det «Komprimert størrelse» (Compressed size) som kolonne og «Pakk ut alle» (Extract All) øverst i vinduet, er du inne i ZIP-fila, og den er ikke pakket ut. Trykk «Pakk ut alle», og bruk mappa som lages. På Windows finner du Nedlastinger (Downloads) i Filutforsker (File Explorer), og etter «Pakk ut alle» trykker du «Pakk ut» (Extract).

</details>

<details>
<summary>Det er to mapper med samme navn.</summary>

Bruk den innerste `G74-lund-osen-main`, den der filene README og compose ligger. Windows viser dem ofte uten filendelsen (.md og .yaml). På Windows har også ZIP-fila samme navn: den har en glidelås på ikonet, og den skal du ikke bruke.

</details>

<details>
<summary>Jeg finner ikke ZIP-fila på Mac.</summary>

Ligger mappa `G74-lund-osen-main` allerede i Nedlastinger (Downloads), har Safari pakket den ut for deg. Bruk den.

</details>

<details>
<summary>Mappa finnes fra før.</summary>

Har du fått koden som mappe eller ZIP-fil fra før, pakker du den ut og går til steg 3. Vil du laste ned på nytt, og det ligger en `.env` med nøkkelen din i den gamle mappa, flytter du den ut først. Slett så den gamle mappa og pakk ut på nytt. Demodataene ligger i Docker, ikke i mappa, så de går ikke tapt. Har du hentet koden med `git clone`, går du heller inn i mappa og skriver `git pull`.

</details>

<details>
<summary>Hvilket vindu skal jeg åpne?</summary>

Et terminalvindu, der du skriver kommandoer i stedet for å klikke. Windows: trykk Start, skriv `PowerShell` og åpne «Windows PowerShell». Ikke velg «Windows PowerShell ISE», som også står i lista. Mac: trykk Cmd+mellomrom, skriv `Terminal` og trykk Enter. Når det har gått bra, ser du et vindu med en linje som venter på at du skriver. Kommandoene er de samme i PowerShell på Windows og i Terminal på Mac og Linux.

</details>

<details>
<summary>Ingenting skjer når jeg limer inn.</summary>

Kommandoene skrives i PowerShell eller Terminal, ikke i Docker Desktop. Docker Desktop skal bare være åpent, og du skriver ingenting i det. Ledetekst (Command Prompt) på Windows virker også for demoen, men stegene er skrevet for PowerShell.

</details>

<details>
<summary>Hva betyr cd, og hvordan ser jeg at det gikk?</summary>

`cd` betyr «gå til mappe», og kommandoen i steg 5 virker bare fra mappa med koden. Når det har gått bra, står `G74-lund-osen-main` rett før `>` (Windows) eller `%` (Mac) på linja som venter.

</details>

<details>
<summary>Mappa lar seg ikke dra inn i vinduet.</summary>

PowerShell er trolig åpnet som administrator, og da sperrer Windows dra og slipp. Lukk vinduet og åpne PowerShell på vanlig måte (steg 3).

</details>

<details>
<summary>Stien har mellomrom og fikk ikke anførselstegn.</summary>

Får du en feil etter `cd` når mappa ligger i en mappe med mellomrom i navnet, skriver du anførselstegn rundt stien, for eksempel `cd "C:\Users\Ola Nordmann\Downloads\G74-lund-osen-main"`. På Mac setter Terminal `\` foran hvert mellomrom, og det virker også.

</details>

<details>
<summary>Terminal spør om tilgang til Nedlastinger (Mac).</summary>

Svar OK. Ellers kan ikke Docker lese mappa.

</details>

<details>
<summary>Hva skal jeg se etter i vinduet?</summary>

Første gang bygger Docker appen, og det kommer mange linjer. Demoen er klar når denne linja kommer. Den skal du ikke kopiere, bare se etter:

```text
demo-1  | INFO:waitress:Serving on http://0.0.0.0:5000
```

Under den kan det komme en linje med valg fra Docker. La terminalvinduet stå åpent mens du bruker demoen. `0.0.0.0` er adressen inne i Docker, og du åpner http://127.0.0.1:5000 i steg 6.

</details>

<details>
<summary>«docker» er ikke gjenkjent, eller «command not found: docker».</summary>

Docker Desktop er ikke installert, eller terminalvinduet ble åpnet før installasjonen. Lukk terminalvinduet og åpne et nytt (steg 3).

</details>

<details>
<summary>«Cannot connect to the Docker daemon», «error during connect» eller «dockerDesktopLinuxEngine».</summary>

Docker Desktop er ikke startet, eller motoren er ikke klar. Start Docker Desktop, vent til det står «Engine running» (steg 1), og prøv kommandoen igjen.

</details>

<details>
<summary>To kommandoer havnet på samme linje.</summary>

For eksempel med feilen «no such service». Lim inn én kommando om gangen, og trykk Enter etter hver. Står det noe på linja fra før, sletter du det først.

</details>

<details>
<summary>«no configuration file provided: not found».</summary>

Terminalvinduet står i feil mappe. Gjør steg 4 på nytt, og dra den mappa der fila compose ligger. Windows viser den uten filendelsen, som compose og ikke compose.yaml.

</details>

<details>
<summary>«toomanyrequests» fra Docker Hub.</summary>

Docker Hub begrenser hvor ofte samme IP-adresse kan laste ned uten innlogging. Prøv igjen senere, eller fra et annet nett. Innlogging i Docker Desktop hever grensen, men trengs ellers ikke.

</details>

<details>
<summary>«port is already allocated», «address already in use» eller «ports are not available».</summary>

Noe annet bruker port 5000. Kjører den ekte versjonen, stopper du den først (se «Bytte mellom demoen og den ekte versjonen»). På Mac bruker AirPlay-mottakeren (AirPlay Receiver) port 5000. Slå den av under Systeminnstillinger (System Settings) → Generelt (General) → AirDrop og Handoff (AirDrop & Handoff), og prøv igjen.

</details>

<details>
<summary>Siden åpnes ikke.</summary>

Vent til linja med «Serving on» har kommet, og sjekk at terminalvinduet fortsatt er åpent. Adressen er http://127.0.0.1:5000, ikke 0.0.0.0.

</details>

<details>
<summary>Hva er demoen?</summary>

Sidene sier «Eksempeltall»: 15 oppdiktede selskaper med kurser til fredag 9. oktober 2026, ikke data fra Oslo Børs. Under merket står en tabell med aksjer, og du klikker på et selskapsnavn for å se aksjen. Demoen trenger verken `.env` eller nøkkel, og gjør ingen kall. Demobasen lages på nytt hver gang demoen starter, i sitt eget volum, `ose-demo`. Den ekte basen røres ikke. Mens demoen kjører, kan demobasen også lages på nytt med `docker compose run --rm demo-lag` i et nytt terminalvindu, fra samme mappe.

</details>

<details>
<summary>Hvordan starter jeg neste gang?</summary>

Start Docker Desktop og vent til det står «Engine running». Gjør så steg 3, 4 og 5, og hopp over steg 2. Det går raskere enn første gang. Etter «Stopp» kan du lukke terminalvinduet og Docker Desktop.

</details>

Resten av «Kom i gang» gjelder den ekte versjonen med egen nøkkel, og trengs ikke for demoen.

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

Begge bruker port 5000, så bare én kan kjøre om gangen. `docker compose down` stopper ikke demoen, fordi demoen ligger i en egen profil. `docker compose --profile demo down` stopper begge.

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

Med Python 3.13 og [uv](https://docs.astral.sh/uv/). Først demoen.

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

Så den ekte versjonen.

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
