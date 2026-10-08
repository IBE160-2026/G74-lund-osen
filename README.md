# OSE Signal

[![tester](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml/badge.svg)](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml)

Gruppe G74 (Ai Ai Ai) i IBE160 Programmering med KI, Høgskolen i Molde, høsten 2026.

OSE Signal samler kursutvikling og signalstyrke for 15 likvide Oslo Børs-aksjer i én oversikt, så en vanlig sparer kan se hva som har endret seg og hvorfor. Beregningene gjøres med vanlig programkode, og KI skal forklare signalet med ord.

## Status

Under arbeid, og ingenting er endelig. Vi jobber med to versjoner samtidig, med samme kode:

- **Den ekte versjonen** henter sluttkurser fra EODHD hver børsdag og lagrer dagens vurdering per aksje. Markedsoversikten og aksjedetaljen leser fra basen. Den krever en egen gratis nøkkel fra EODHD.
- **Demoversjonen** får oppdiktede selskaper og kurser, og kan prøves uten konto og uten nøkkel. Den bygges sammen med Docker i 3.1–3.4, og blir den enkleste måten å prøve appen på.

Neste er børsdagskontrollen (2.3), så Docker og demoversjonen, og deretter KI-laget. Det som bygges etter demoen, skal vises i begge versjonene. Børsmeldinger er ikke med i v1, fordi Euronext ikke ga tillatelse til automatisert henting (plan B). Se [sprintstatusen](_bmad-output/implementation-artifacts/sprint-status.yaml).

Til faglærer: leveranselista står i [`docs/innlevering.md`](docs/innlevering.md), og kvalitetssikringen i [`docs/kvalitetssikring.md`](docs/kvalitetssikring.md). Prosessen og valgene våre står i [`docs/reflection-log.md`](docs/reflection-log.md).

## Kom i gang

```
git clone https://github.com/IBE160-2026/G74-lund-osen.git
cd G74-lund-osen
uv sync                                  # installerer avhengighetene
cp .env.example .env                     # fyll inn EODHD_API_KEY
uv run python src/fetch_prices.py        # henter kurser
uv run python src/app.py                 # http://localhost:5000
```

- Du trenger en egen gratis API-nøkkel fra [EODHD](https://eodhd.com/register), fordi vilkårene ikke lar oss dele vår. Den gir 20 kall i døgnet, og en henting bruker 15.
- Kjør hentingen på børsdager mellom kl. 22 og midnatt. En vurdering kan ikke fylles inn senere. Før kl. 22 på en børsdag stopper kommandoen med 0 kall, med mindre du gir `--hent-foer-kl-22`. Har basen alt kursene for børsdagen, bruker den 0 kall. På en dag børsen er stengt henter den bare hvis basen mangler forrige børsdag. Før kallene leser den kvoten med `/api/user`, som er gratis.
- Appen bruker aldri kvote selv. Den leser bare fra basen.
- Uten henting starter appen med tom oversikt og viser kommandoen som henter.

Utskriften fra hentingen sier hvilken børsdag vurderingene gjelder, og hvilke aksjer som fikk en grunn i stedet for en vurdering.

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
- `_bmad/`, `.claude/skills/` og `.agents/skills/` — BMAD-rammeverket, ikke skrevet av oss

Ikke i repoet: API-nøkkelen (`.env`), rådata og basen (`data/`), lokale testskript (`local-tests/`) og den private arbeidsmappa (`_privat/`).

## Medlemmer

Joakim Lund og Marian Osen. Fra 25.09 har felles commits `Co-authored-by` for den av oss som ikke committet (regel 20 i `CLAUDE.md`).
