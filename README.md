# OSE Signal

[![tester](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml/badge.svg)](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml)

Gruppe G74 (Ai Ai Ai) i IBE160 Programmering med KI, Høgskolen i Molde, høsten 2026.

OSE Signal samler kursutvikling og signalstyrke for 15 likvide Oslo Børs-aksjer i én oversikt, så en vanlig sparer kan se hva som har endret seg og hvorfor. Beregningene gjøres med vanlig programkode, og KI skal forklare signalet med ord.

## Status

Under arbeid, og ingenting er endelig. Vi jobber med to versjoner samtidig, med samme kode:

- **Den ekte versjonen** henter sluttkurser fra EODHD hver børsdag og lagrer dagens vurdering per aksje. Markedsoversikten og aksjedetaljen leser fra basen. Den krever en egen gratis nøkkel fra EODHD.
- **Demoversjonen** får oppdiktede selskaper og kurser, og kan prøves uten konto og uten nøkkel. Den kommer i story 3.4 og blir den enkleste måten å prøve appen på. Til da krever hentingen en egen nøkkel.

Børsdagskontrollen (2.3), Docker (3.1 og 3.2) og denne oppskriften (3.3) er flettet til `main`. Neste er demoversjonen (3.4), og deretter KI-laget. Det som bygges etter demoen, skal vises i begge versjonene. Børsmeldinger er ikke med i v1, fordi Euronext ikke ga tillatelse til automatisert henting (plan B). Se [sprintstatusen](_bmad-output/implementation-artifacts/sprint-status.yaml).

Til faglærer: leveranselista står i [`docs/innlevering.md`](docs/innlevering.md), og kvalitetssikringen i [`docs/kvalitetssikring.md`](docs/kvalitetssikring.md). Prosessen og valgene våre står i [`docs/reflection-log.md`](docs/reflection-log.md).

## Kom i gang

Docker er hovedmåten. Du trenger [Docker Desktop](https://www.docker.com/products/docker-desktop/) (eller Docker Engine med Compose på Linux) og git. Kommandoene er de samme i PowerShell på Windows og i terminalen på macOS og Linux.

```
git clone https://github.com/IBE160-2026/G74-lund-osen.git
cd G74-lund-osen
cp .env.example .env                     # bare første gang: fyll inn EODHD_API_KEY i .env
docker compose up --build                # webserveren på http://127.0.0.1:5000
```

Hent kursene i et nytt vindu, fra samme mappe:

```
docker compose run --rm hent
```

Stopp med `Ctrl+C` i vinduet med webserveren, eller med:

```
docker compose down
```

- **Nøkkelen.** Du trenger en egen gratis API-nøkkel fra [EODHD](https://eodhd.com/register), fordi vilkårene ikke lar oss dele vår. Den gir 20 kall i døgnet, og en henting bruker 15. Åpne `.env` i en teksteditor (`notepad .env` på Windows, `open -e .env` på macOS, `nano .env` på Linux) og lim den inn etter `EODHD_API_KEY=`. `cp` skriver over en `.env` som finnes, så kopier bare første gang. Webserveren starter uten `.env` og bruker aldri kvote: den leser bare fra basen. Bare hentingen trenger nøkkelen, og `docker compose run --rm hent` starter ikke uten `.env`.
- **Når du henter.** Hent etter kl. 22 og før midnatt på en børsdag. Første gang kan du også hente i helgen: da henter den siste børsdag, fordi basen mangler den. På dagtid en børsdag stopper hentingen med 0 kall og sier hvorfor: dagens sluttkurs er ikke klar ennå, og en vurdering kan ikke fylles inn senere. Har basen alt kursene for børsdagen, bruker den også 0 kall. På en dag børsen er stengt henter den bare hvis basen mangler forrige børsdag og fila for den dagen ikke finnes. Før kallene leser den kvoten med `/api/user`, som er gratis.
- **Uten henting** starter appen med tom oversikt og viser kommandoen som henter. Utskriften fra hentingen sier hvilken børsdag vurderingene gjelder, og hvilke aksjer som fikk en grunn i stedet for en vurdering.
- **Dataene** ligger i to Docker-volumer: `ose-db` med basen og `ose-raa` med øyeblikksbildene fra EODHD. De står når containerne stoppes. **Bruk aldri `docker compose down -v`.** `-v` fjerner begge volumene, og verken øyeblikksbildene eller vurderingene kan hentes på nytt. Basen kan heller ikke slettes og bygges opp igjen: kursene kan hentes på nytt, men vurderingene for dagene som har gått, kan ikke lages på nytt.
- **Porten** er bare åpen på maskinen selv (127.0.0.1). Appen kan ikke nås fra nettet.

### Uten Docker, med uv

Med Python 3.13 og [uv](https://docs.astral.sh/uv/):

```
uv sync                                  # installerer avhengighetene
cp .env.example .env                     # bare første gang: fyll inn EODHD_API_KEY
uv run python src/fetch_prices.py        # henter kurser
uv run python src/app.py                 # http://127.0.0.1:5000
```

Basen og øyeblikksbildene ligger da i `data/` i mappa.

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
- `Dockerfile`, `compose.yaml` og `.dockerignore` — imaget og de to tjenestene, webserveren og hentingen
- `_bmad/`, `.claude/skills/` og `.agents/skills/` — BMAD-rammeverket, ikke skrevet av oss

Ikke i repoet: API-nøkkelen (`.env`), rådata og basen (`data/`), lokale testskript (`local-tests/`) og den private arbeidsmappa (`_privat/`).

## Medlemmer

Joakim Lund og Marian Osen. Fra 25.09 har felles commits `Co-authored-by` for den av oss som ikke committet (regel 20 i `CLAUDE.md`).
