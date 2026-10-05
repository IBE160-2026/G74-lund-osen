# OSE Signal

[![tester](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml/badge.svg)](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml)

Gruppe G74 (Ai Ai Ai) i IBE160 Programmering med KI, Høgskolen i Molde, høsten 2026.

OSE Signal samler kursutvikling og signalstyrke for 15 likvide Oslo Børs-aksjer i én oversikt, så en vanlig sparer kan se hva som har endret seg og hvorfor. Beregningene gjøres med vanlig programkode, og KI skal forklare signalet med ord.

## Status

Under arbeid, og ingenting er endelig. Nå virker hentingen av sluttkurser fra EODHD til en SQLite-base, med dagens vurdering per aksje, og markedsoversikten og aksjedetaljen, som leser fra basen. Neste er børsdagskontrollen (2.3), så Docker og demoversjonen (3.1–3.4), og deretter KI-laget. Børsmeldinger er ikke med i v1, fordi Euronext ikke ga tillatelse til automatisert henting (plan B). Se [sprintstatusen](_bmad-output/implementation-artifacts/sprint-status.yaml).

Til faglærer: leveranselista står i [`docs/innlevering.md`](docs/innlevering.md), og kvalitetssikringen i [`docs/kvalitetssikring.md`](docs/kvalitetssikring.md).

## Kom i gang

```
git clone https://github.com/IBE160-2026/G74-lund-osen.git
cd G74-lund-osen
uv sync                                  # installerer avhengighetene
cp .env.example .env                     # fyll inn EODHD_API_KEY
uv run python src/fetch_prices.py        # henter kurser
uv run python src/app.py                 # http://localhost:5000
```

- Du trenger en egen gratis API-nøkkel fra EODHD. Den gir 20 kall i døgnet, og en henting bruker 15.
- Kjør hentingen på børsdager mellom kl. 22 og midnatt. En vurdering kan ikke fylles inn senere.
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

Mer i [`docs/kvalitetssikring.md`](docs/kvalitetssikring.md).

## Dokumentene

`docs/` viser hvordan vi kom fram til noe og hvilken rolle KI spilte, og `_bmad-output/` viser hva vi kom fram til.

**Plan og krav**

- [Product Brief](_bmad-output/planning-artifacts/product-brief.md), låst i taggen `arbeidskrav-product-brief-v7`
- [PRD](_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/), med begrunnelser og målinger
- [Relevanseksperimentet](_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/relevanseksperiment.md)
- [Arkitektur](_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md)
- [Epics og stories](_bmad-output/planning-artifacts/epics.md)
- [Designregler](_bmad-output/planning-artifacts/designregler.md)
- [Endringsforslag 28.09](_bmad-output/planning-artifacts/sprint-change-proposal-2026-09-28.md), godkjent av gruppen 28.09
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
