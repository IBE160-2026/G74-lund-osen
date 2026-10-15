# OSE Signal

[![tester](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml/badge.svg)](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml)

Gruppe G74 (Ai Ai Ai) i IBE160 Programmering med KI, Høgskolen i Molde, høsten 2026.

OSE Signal viser 15 aksjer på Oslo Børs som omsettes mye, samlet i én oversikt. Tre enkle sjekker – trend, bevegelse og interesse – gir hver aksje en signalstyrke fra 0 til 3, så en vanlig sparer kan se hva som har endret seg, og hvorfor. Beregningene gjøres med vanlig programkode, og KI skal forklare signalet med ord. Appen gir ikke råd om å kjøpe eller selge. Den er under utvikling og ikke ferdig.

Til faglærer:
- [Product Brief](_bmad-output/planning-artifacts/product-brief.md), arbeidskravet: versjon 8, laget etter [tilbakemeldingen 06.10](_bmad-output/planning-artifacts/tilbakemelding-product-brief.md) og låst i taggen `arbeidskrav-product-brief-v8`
- Plan og krav: [PRD](_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md), [arkitektur](_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md) og [epics og stories](_bmad-output/planning-artifacts/epics.md)
- [Leveranselista](docs/innlevering.md): kravene i emnet, og hvor hvert av dem står
- Prosessen og KI-bruken: [kvalitetssikringen](docs/kvalitetssikring.md), [refleksjonsloggen](docs/reflection-log.md) og [de lagrede KI-promptene](docs/ai-prompts/)

## Kom i gang

Appen finnes i to versjoner, med samme kode. Vi anbefaler den ekte versjonen. Vil du bare se hvordan appen virker, er demoen raskest.

| | Den ekte versjonen (anbefalt) | Demoen |
|---|---|---|
| Kurser | Ekte sluttkurser fra Oslo Børs, hentet fra EODHD hver børsdag. Dagens vurdering lagres per aksje | Oppdiktede selskaper og kurser («Eksempeltall») |
| Trenger | Docker Desktop og en gratis nøkkel fra EODHD | Bare Docker Desktop |
| Klar | Viser kurser etter første henting om kvelden | Med en gang |

**Du trenger** en Windows-maskin eller en Mac, lov til å installere programmer, nett og noen GB ledig plass, men verken git eller Docker-konto. Første gang tar det en stund. På Linux bruker du Docker Engine med Compose i stedet for Docker Desktop. Står du fast, se [«Står du fast?»](#står-du-fast) lenger ned.

### Felles for begge

1. **Installer og start Docker Desktop** fra [docker.com](https://www.docker.com/products/docker-desktop/). Hopp over innloggingen. Det er klart når det står «Engine running» nederst i vinduet. La det være åpent.
2. **Last ned koden.** Trykk den grønne knappen «Code» på [GitHub-siden](https://github.com/IBE160-2026/G74-lund-osen) og «Download ZIP» nederst i menyen. Windows: høyreklikk fila i Nedlastinger (Downloads) og velg «Pakk ut alle» (Extract All). Mac: dobbeltklikk fila. Det er klart når du har en mappe som heter `G74-lund-osen-main`. Har du fått koden som mappe eller ZIP-fil, pakker du den ut og går til steg 3.
3. **Åpne PowerShell** (Windows: trykk Start, skriv PowerShell og velg «Windows PowerShell», ikke ISE) **eller Terminal** (Mac: trykk Cmd+mellomrom og skriv Terminal). Det er klart når et vindu venter på at du skriver.
4. **Skriv `cd` og et mellomrom**, dra mappa `G74-lund-osen-main` der README og compose ligger (den innerste hvis det er to) fra Filutforsker eller Finder inn i vinduet, og trykk Enter. Det er klart når mappenavnet står foran `>` eller `%`. Har mappa et annet navn, drar du den mappa der README og compose ligger.

### Den ekte versjonen (anbefalt)

5. **Hent en nøkkel.** Lag en gratis bruker hos [EODHD](https://eodhd.com/register), og kopier API-nøkkelen din. Det er klart når du har nøkkelen.
6. **Legg inn nøkkelen, bare første gang.** Kopier kommandoene med knappen til høyre i boksen, lim dem inn én om gangen (Ctrl+V eller Cmd+V) og trykk Enter. Den første lager fila `.env`, og den neste åpner den (Windows eller Mac). Lim inn nøkkelen etter `EODHD_API_KEY=`, lagre og lukk. Det er klart når nøkkelen står etter `EODHD_API_KEY=`.

```
cp .env.example .env
```

Windows:

```
notepad .env
```

Mac:

```
open -e .env
```

7. **Start appen.** Lim inn denne og trykk Enter. Første gang tar det noen minutter. Det er klart når det står `Serving on http://0.0.0.0:5000`. Åpne http://127.0.0.1:5000 i en ny fane. Første gang er oversikten tom og viser kommandoen som henter.

```
docker compose up --build
```

8. **Hent kursene** etter kl. 22 og før midnatt på en børsdag. Åpne et nytt terminalvindu i samme mappe (steg 3 og 4), og lim inn denne. Det er klart når utskriften sier hvilken børsdag vurderingene gjelder. Last siden på nytt når hentingen er ferdig.

```
docker compose run --rm hent
```

9. **Stopp** med Ctrl+C i vinduet med appen, og lim så inn denne. Det er klart når det står at containerne er fjernet (Removed).

```
docker compose down
```

**Skriv aldri `docker compose down -v`.** Det sletter kursene og vurderingene, og vurderingene kan ikke lages på nytt.

### Demoen

5. **Start demoen.** Kopier kommandoen med knappen til høyre i boksen, lim den inn (Ctrl+V eller Cmd+V) og trykk Enter. Første gang tar det noen minutter. Demoen er klar når det står `Serving on http://0.0.0.0:5000`. Den adressen skal du ikke åpne.

```
docker compose up --build demo
```

6. **Åpne http://127.0.0.1:5000** i en ny fane. Øverst står «Eksempeltall: oppdiktede selskaper og kurser, ikke data fra Oslo Børs.» Klikk på et selskapsnavn for å se en aksje.
7. **Stopp** med Ctrl+C i terminalvinduet, også på Mac, og lim så inn denne. Det er klart når det står at containerne er fjernet (Removed).

```
docker compose --profile demo down
```

### Står du fast?

Klikk på spørsmålet som passer.

<details>
<summary>Det står ikke «Engine running» etter noen minutter.</summary>

Avslutt Docker Desktop helt: høyreklikk hvalen ved klokka (Windows) eller klikk den i menylinja øverst (Mac), og velg «Quit Docker Desktop». Åpne det igjen og vent. Hjelper ikke det, starter du maskinen på nytt.

</details>

<details>
<summary>ZIP-fila ser ut som en vanlig mappe.</summary>

Du må pakke ut. Står det «Komprimert størrelse» (Compressed size) som kolonne og «Pakk ut alle» (Extract All) øverst i vinduet, er du inne i ZIP-fila, og den er ikke pakket ut. Trykk «Pakk ut alle», og bruk mappa som lages. På Windows finner du Nedlastinger (Downloads) i Filutforsker (File Explorer), og etter «Pakk ut alle» trykker du «Pakk ut» (Extract).

</details>

<details>
<summary>Mappa lar seg ikke dra inn i vinduet.</summary>

PowerShell er trolig åpnet som administrator, og da sperrer Windows dra og slipp. Lukk vinduet og åpne PowerShell på vanlig måte (steg 3).

</details>

<details>
<summary>Ingenting skjer når jeg limer inn.</summary>

Kommandoene skrives i PowerShell eller Terminal, ikke i Docker Desktop. Docker Desktop skal bare være åpent, og du skriver ingenting i det. Ledetekst (Command Prompt) på Windows virker også for demoen, men stegene er skrevet for PowerShell, og den ekte versjonen trenger PowerShell.

</details>

<details>
<summary>«Cannot connect to the Docker daemon», «error during connect» eller «dockerDesktopLinuxEngine».</summary>

Docker Desktop er ikke startet, eller motoren er ikke klar. Start Docker Desktop, vent til det står «Engine running» (steg 1), og prøv kommandoen igjen.

</details>

<details>
<summary>«no configuration file provided: not found».</summary>

Terminalvinduet står i feil mappe. Gjør steg 4 på nytt, og dra den mappa der fila compose ligger. Windows viser den uten filendelsen, som compose og ikke compose.yaml.

</details>

<details>
<summary>«port is already allocated», «address already in use» eller «ports are not available».</summary>

Noe annet bruker port 5000. Kjører den andre versjonen, stopper du den først (se «Bytte mellom demoen og den ekte versjonen» under «Mer for den som vil»). På Mac bruker AirPlay-mottakeren (AirPlay Receiver) port 5000. Slå den av under Systeminnstillinger (System Settings) → Generelt (General) → AirDrop og Handoff (AirDrop & Handoff), og prøv igjen.

</details>

<details>
<summary>Oversikten er tom.</summary>

Uten henting starter appen med tom oversikt og viser kommandoen som henter. Hent kursene med steg 8 i den ekte versjonen, og last siden på nytt.

</details>

Flere spørsmål og svar står i [docs/hjelp.md](docs/hjelp.md).

### Mer for den som vil

<details>
<summary>Bytte mellom demoen og den ekte versjonen</summary>

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

</details>

<details>
<summary>Uten Docker, med uv</summary>

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

</details>

<details>
<summary>Den lokale modellen (KI-teksten)</summary>

Hentingen kan lage en KI-tekst for hver aksje, med en modell som kjører på maskinen: Gemma i Ollama, i Docker, med grafikkortet. Med adressen som står som standard, sendes ingenting ut. KI-teksten er av i `.env.example`, og hentingen går som før uten den.

Det trengs et grafikkort fra NVIDIA med driver, og at Docker Desktop kan bruke det. Uten det starter ikke Ollama, og KI-teksten bør stå av.

Bare første gang: start Ollama, og hent modellen til volumet `ose-ki-ollama`.

```
docker compose --profile ki up -d ollama
```

```
docker compose exec ollama ollama pull gemma4:e4b
```

Slå på KI-teksten: sett `OSE_KI_TJENESTE=lokal` i `.env`. Står variabelen ikke i `.env` i det hele tatt, er den også på.

Før hver henting med KI-tekst må Ollama kjøre:

```
docker compose --profile ki up -d ollama
```

Så hentes det som vanlig. Med uv når hentingen Ollama på http://127.0.0.1:11434, og i Docker på tjenestenavnet. Stopp Ollama etterpå:

```
docker compose --profile ki down
```

Hentingen sjekker først at Ollama svarer og har modellen. Gjør den ikke det, lages ingen KI-tekst, og utskriften sier hvorfor. Start Ollama og kjør samme kommando igjen samme kveld, før midnatt: da lages tekstene. Har basen dagens kurs for alle aksjene, gir det 0 kall til EODHD. Mangler noen aksjer dagens kurs, gjør samme kommando et nytt forsøk for dem, og det bruker kall. Svarer Ollama, men modellen feiler for en aksje, får aksjen en rad om det, og modellen kalles ikke for resten av aksjene den kvelden. De får en rad om at modellen ikke ble kalt. Radene står, så ingen av dem får tekst den dagen (FR-604).

Slå av KI-teksten: sett `OSE_KI_TJENESTE=av` i `.env`.

Modellen ble prøvd på en maskin med 15,7 GB minne og et grafikkort med 8 GB, der Docker Desktop hadde 8,2 GB (`malinger.md` §19).

</details>

## Status

Under arbeid, og ingenting er endelig. Flettet til main: hentingen av kurser med kontroll av børsdagen, nye forsøk med kallene som er igjen etter hentingen, Docker, demoen, denne README-en, hjelp bak «?» på sidene, tydeligere merking i tabellene, datoene og månedsmerkene i grafen, oversikten fra designforslaget, utseendet fra designforslaget, og sortering ved klikk i kolonneraden. Neste: hovedindeksen, Min liste, periodene i kursgrafen, og så KI-laget. Det som bygges etter demoen, skal vises i begge versjonene. Børsmeldinger er ikke med i v1, fordi Euronext ikke ga tillatelse til automatisert henting (plan B). Detaljene står i [sprintstatusen](_bmad-output/implementation-artifacts/sprint-status.yaml) og i [planen](_bmad-output/planning-artifacts/epics.md).

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

- [Product Brief](_bmad-output/planning-artifacts/product-brief.md): versjon 8, laget etter [tilbakemeldingen fra faglærer 06.10](_bmad-output/planning-artifacts/tilbakemelding-product-brief.md) på versjon 7 (taggen `arbeidskrav-product-brief-v7`), og låst i taggen `arbeidskrav-product-brief-v8` (commit `52023c9`)
- [PRD](_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/), med begrunnelser og målinger
- [Relevanseksperimentet](_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/relevanseksperiment.md)
- [Arkitektur](_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md)
- [Epics og stories](_bmad-output/planning-artifacts/epics.md)
- [Designregler](_bmad-output/planning-artifacts/designregler.md)
- [Utdrag fra designtavla 13.10](_bmad-output/planning-artifacts/designutdrag-2026-10-13.md): grunnlaget for planen til story 8.0d
- [Endringsforslag 28.09](_bmad-output/planning-artifacts/sprint-change-proposal-2026-09-28.md), godkjent samme dag
- [Endringsforslag 08.10](_bmad-output/planning-artifacts/sprint-change-proposal-2026-10-08.md): femten idéer inn i v1, godkjent samme dag
- [Endringsforslag 13.10](_bmad-output/planning-artifacts/sprint-change-proposal-2026-10-13.md): den samlede endringen fra samlelista, godkjent samme dag
- [Kilder og bruksvilkår](docs/kilder-og-rettigheter.md), med e-postene til [EODHD](docs/epost-til-eodhd.md) og [Euronext](docs/epost-til-euronext.md)
- [Leveranseliste](docs/innlevering.md)
- [Hjelp til «Kom i gang»](docs/hjelp.md): spørsmål og svar, sortert etter steg

**Arbeidsprosess og kvalitet**

- [Sprintstatus og story-spesifikasjoner](_bmad-output/implementation-artifacts/)
- [Kvalitetssikring](docs/kvalitetssikring.md)
- [Kontrollrapport 22.09](docs/kontroll-2026-09-22.md), med [rettingsplanen](docs/kontroll-2026-09-22-plan.md)
- [Kontrollrapport 26.09](docs/kontroll-2026-09-26.md)
- [Refleksjonslogg](docs/reflection-log.md) og [lagrede KI-prompts](docs/ai-prompts/)

## Mappestruktur

- `src/` og `tests/` — applikasjonen og testene
- `docs/` — arbeidsprosessen, og `docs/hjelp.md` med spørsmål og svar til «Kom i gang»
- `_bmad-output/` — Product Brief, plan, krav og sprintstatus
- `.github/` — testkjøringen og morgensjekken
- `Dockerfile`, `compose.yaml` og `.dockerignore` — imaget og tjenestene: webserveren, hentingen og demoen
- `_bmad/`, `.claude/skills/` og `.agents/skills/` — BMAD-rammeverket, ikke skrevet av oss

Ikke i repoet: API-nøkkelen (`.env`), rådata, basen og demobasen (`data/`), lokale testskript (`local-tests/`) og den private arbeidsmappa (`_privat/`).

## Medlemmer

Joakim Lund og Marian Osen. Vi diskuterer og avgjør arbeidet sammen. Fra 25.09 har felles commits `Co-authored-by` for den av oss som ikke committet (regel 20 i `CLAUDE.md`).
