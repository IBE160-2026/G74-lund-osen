# G74 — Ai Ai Ai

[![tester](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml/badge.svg)](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml)

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

**OSE Signal** samler kursutvikling og signalstyrke for omtrent 15 likvide Oslo Børs-aksjer i én oversikt, slik at en vanlig sparer kan se hva som har endret seg og hvorfor. Beregningene gjøres med vanlig programkode, og KI forklarer signalet med ord, ut fra tall regnet av kursene. KI-laget kan slås av, og applikasjonen skal fungere uten det.

Hva som er bygget så langt, står i sprintstatusen, `_bmad-output/implementation-artifacts/sprint-status.yaml`. Børsmeldinger og kommende hendelser er ikke med i v1: Euronext ga ikke tillatelse til automatisert henting innen vår frist 28.09 (plan B); se `docs/kilder-og-rettigheter.md`.

## Medlemmer

- Joakim Lund
- Marian Osen

Vi diskuterer og avgjør arbeidet sammen, og det meste skrives inn på én maskin.
Fra 25.09 har felles commits en linje `Co-authored-by` for den av oss som ikke
committet (regel 20 i `CLAUDE.md`). Skriver Joakim selv på den maskinen, står
han som forfatter og Marian som medforfatter. Commitene før 25.09 står bare på
den som committet.

## Dokumentene

- **Product Brief** — [`_bmad-output/planning-artifacts/product-brief.md`](_bmad-output/planning-artifacts/product-brief.md). Arbeidskrav på 1–2 sider, innleveringsfrist søndag 27.09.2026.
- **PRD med krav, begrunnelser og målinger** — [`_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/`](_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/)
- **Relevanseksperimentet** — [`_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/relevanseksperiment.md`](_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/relevanseksperiment.md), med kriteriene som ble satt før innsamlingen, og innsamlingen 25.09
- **Arkitektur** — [`_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md`](_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md)
- **Epics og stories** — [`_bmad-output/planning-artifacts/epics.md`](_bmad-output/planning-artifacts/epics.md)
- **Designregler** — [`_bmad-output/planning-artifacts/designregler.md`](_bmad-output/planning-artifacts/designregler.md). Hvordan skjermbildene ser ut, begynner med skriften
- **Endringsforslag 28.09: databasen i bruk i Epic 2** — [`_bmad-output/planning-artifacts/sprint-change-proposal-2026-09-28.md`](_bmad-output/planning-artifacts/sprint-change-proposal-2026-09-28.md). Utkast, ikke godkjent
- **Sprintstatus og story-spesifikasjoner** — [`_bmad-output/implementation-artifacts/`](_bmad-output/implementation-artifacts/)
- **Kilder og bruksvilkår** — [`docs/kilder-og-rettigheter.md`](docs/kilder-og-rettigheter.md), med hva hver datakilde tillater og når det sist ble kontrollert. Forespørslene til EODHD og Euronext står i [`docs/epost-til-eodhd.md`](docs/epost-til-eodhd.md) og [`docs/epost-til-euronext.md`](docs/epost-til-euronext.md)
- **Leveranseliste** — [`docs/innlevering.md`](docs/innlevering.md), med hva som skal leveres, og hvor det står
- **Kontrollrapport 22.09** — [`docs/kontroll-2026-09-22.md`](docs/kontroll-2026-09-22.md), med rettingsplanen i [`docs/kontroll-2026-09-22-plan.md`](docs/kontroll-2026-09-22-plan.md)
- **Kontrollrapport 26.09** — [`docs/kontroll-2026-09-26.md`](docs/kontroll-2026-09-26.md), med det som ble rettet samme kveld, og det som står igjen
- **Kvalitetssikring** — [`docs/kvalitetssikring.md`](docs/kvalitetssikring.md), med hva som er testet, mutantene, kontrollene og hva som ikke er testet
- **Refleksjonslogg og lagrede KI-prompts** — [`docs/reflection-log.md`](docs/reflection-log.md) og [`docs/ai-prompts/`](docs/ai-prompts/)

## Mappestruktur

**Vårt arbeid:**

- `src/` — applikasjonen, og `tests/` — testene som hører til
- `docs/` — arbeidsprosessen: refleksjonslogg, KI-prompts og kildekontroll
- `_bmad-output/planning-artifacts/` — produktdokumentene og gjennomgangene av dem
- `_bmad-output/implementation-artifacts/` — sprintstatus, story-spesifikasjoner og utsatt arbeid
- `.github/workflows/` — testkjøringen bak merket øverst, og morgensjekken, som hver morgen legger rapporten i saken «Morgensjekk» (skriptene i `.github/scripts/`)

**Følger med BMAD-rammeverket, ikke skrevet av oss:**

- `_bmad/` — rammeverket selv, med vårt oppsett i `config.toml`
- `.claude/skills/` og `.agents/skills/` — BMADs ferdigheter, lagt inn av installatøren i to identiske kopier: én som Claude Code leser, én på den verktøynøytrale stien

**Utenfor versjonskontroll, og derfor ikke i repoet:** API-nøkkel (`.env`), hentede
rådata og basen (`data/`: øyeblikksbildene i `data/raa/`, basen i `data/db/ose.db`),
lokale testskript (`local-tests/`) og den private arbeidsmappa (`_privat/`).

## Kom i gang

```
git clone https://github.com/IBE160-2026/G74-lund-osen.git
cd G74-lund-osen
uv sync                                  # installerer avhengighetene fra uv.lock
cp .env.example .env                     # fyll inn EODHD_API_KEY
uv run python src/fetch_prices.py        # henter kurser, bruker 15 API-kall (0 hvis dagens fil finnes)
uv run python src/app.py                 # http://localhost:5000
```

Hentingen skriver først øyeblikksbildet i `data/raa/` og så kursene til basen i
`data/db/ose.db`, med samme tidspunkt. Mappene og basen lages ved første
henting. Etter kursene skriver den dagens vurdering for hver av de 15 aksjene i
tabellen `vurdering`, regnet av seriene den nettopp lagret. Kan en aksje ikke
vurderes, skrives en rad med grunnen. Utskriften sier hvilken børsdag radene
gjelder, og hvilke aksjer som fikk en grunn. En vurdering kan ikke fylles inn
etterpå, så hentingen kjøres for hånd på børsdager mellom kl. 22 og midnatt.
Kjøres hentingen før kursene er publisert, stopper filvakten kveldens kjøring,
og dagen får ingen vurdering. Går kjøringen over midnatt, stopper den før
vurderingene og sier fra. En dag børsen er stengt, gjelder raden forrige
børsdag, og en rad som finnes, står. Er ikke dagene børsen er stengt ført inn
for året i `src/boersdag.py`, stopper hentingen før første kall.

Feiler basen, står fila, og den kan leses inn senere uten API-kall:

```
uv run python src/fetch_prices.py --les-inn data/raa/kurser-raa-ÅÅÅÅ-MM-DD.json
```

Innlesingen skriver bare kursene, aldri en vurdering, og leser ingen nøkkel.
Øyeblikksbilder fra før 2.1b (`data/kurser-raa-*.json`) flyttes til `data/raa/`;
målingsfilene blir liggende i `data/`.

Applikasjonen leser bare øyeblikksbildene i `data/raa/` og gjør aldri API-kall selv, så en
nettleseroppdatering kan ikke bruke av kvoten. `fetch_prices.py` er det eneste
stedet i prosjektet som bruker kvote: 15 kall av de 20 EODHDs gratisnivå gir i
døgnet, altså én full henting per dag. Finnes dagens øyeblikksbilde fra før,
stopper den før første kall, så en kjøring nummer to samme dag bruker ingen kall
og skriver ikke over fila.

Hopper du over hentesteget, starter applikasjonen likevel — med tom oversikt og
beskjed om at det ikke finnes kursdata. Testene under krever verken nøkkel eller data.

## Tester

```
uv run pytest
```

Testene bruker ingen API-kall og rører ikke `data/`: en fixture i
`tests/conftest.py` peker `data/raa/` og `data/db/` mot en midlertidig mappe i
hver test. Testdataene er
kursserier og meldinger vi har skrevet selv, fordi testdata som hentes er
testdata som endrer seg — da tester vi børsen i stedet for koden vår.

**Det er håndhevet, ikke bare lovet.** `tests/conftest.py` sperrer utgående
nettverk i hver test, under `requests` og alt annet som måtte
åpne en forbindelse. Story 4.0 utvider sperren til hele testkjøringen. En test som ved et uhell kaller et ekte endepunkt,
feiler i stedet for å spise av EODHD-kvoten på 20 kall i døgnet — som i CI
ville skjedd på hver eneste push.

Testene kjøres automatisk på hver push til `main` og hver pull request mot `main`, se
merket øverst. Workflowen har ingen hemmeligheter og ingen API-nøkkel.

Hver story leveres med test. Det gjelder fra og med signalberegningen, og
det er også svaret vårt på hvordan KI-generert kode kvalitetssikres.
Hva som er testet, hvordan, og hva som ikke er det, står samlet i
[`docs/kvalitetssikring.md`](docs/kvalitetssikring.md).

Skillet mellom `docs/` og `_bmad-output/` er bevisst. `docs/` viser hvordan vi kom fram til noe og hvilken rolle KI spilte underveis; `_bmad-output/` viser hva vi kom fram til. Vurderinger vi forkastet, og prompter som ledet til en beslutning, hører hjemme i `docs/ai-prompts/` — ikke i produktdokumentene, som skal kunne leses av seg selv.
