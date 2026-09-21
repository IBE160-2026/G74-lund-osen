# G74 — Ai Ai Ai

[![tester](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml/badge.svg)](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml)

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

**OSE Signal** samler kursutvikling, signalstyrke og børsmeldinger for omtrent 15
likvide Oslo Børs-aksjer i én oversikt, slik at en vanlig sparer kan se hva som
har endret seg og hvorfor. Beregninger og sortering gjøres med vanlig programkode;
KI brukes til å forklare hva en børsmelding betyr. KI-laget kan slås av, og
applikasjonen skal fungere uten det.

## Medlemmer

- Joakim Lund
- Marian Osen

## Dokumentene

- **Product Brief** — `_bmad-output/planning-artifacts/product-brief.md`
- **PRD med krav, begrunnelser og målinger** — `_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/`
- **Kilder og bruksvilkår** — `docs/kilder-og-rettigheter.md`, med hva hver datakilde tillater og når det sist ble kontrollert
- **Refleksjonslogg og lagrede KI-prompts** — `docs/reflection-log.md` og `docs/ai-prompts/`

## Mappestruktur

**Vårt arbeid:**

- `src/` — applikasjonen, og `tests/` — testene som hører til
- `docs/` — arbeidsprosessen: refleksjonslogg, KI-prompts og kildekontroll
- `_bmad-output/planning-artifacts/` — produktdokumentene og gjennomgangene av dem
- `.github/workflows/` — testkjøringen bak merket øverst

**Følger med BMAD-rammeverket, ikke skrevet av oss:**

- `_bmad/` — rammeverket selv, med vårt oppsett i `config.toml`
- `.claude/skills/` og `.agents/skills/` — BMADs ferdigheter, lagt inn av installatøren i to identiske kopier: én som Claude Code leser, én på den verktøynøytrale stien

**Utenfor versjonskontroll, og derfor ikke i repoet:** API-nøkkel (`.env`), hentede
rådata (`data/`) og lokale testskript (`local-tests/`).

## Kjøre applikasjonen

```
uv sync
uv run python src/app.py
```

Applikasjonen kjører lokalt på `http://localhost:5000` og leser bare fra `data/`.
Den gjør aldri API-kall selv, så en nettleseroppdatering kan ikke bruke av kvoten.
Uten hentede data starter den med tom oversikt.

Nye sluttkurser hentes med `uv run python src/fetch_prices.py`. Det er det eneste
stedet i prosjektet som bruker kvote — 15 kall av de 20 EODHDs gratisnivå gir i
døgnet — og det krever `EODHD_API_KEY` i `.env`.

## Tester

```
uv run pytest
```

Testene bruker ingen API-kall og leser ikke `data/`. Testdataene er
kursserier og meldinger vi har skrevet selv, fordi testdata som hentes er
testdata som endrer seg — da tester vi børsen i stedet for koden vår.

**Det er håndhevet, ikke bare lovet.** `tests/conftest.py` sperrer utgående
nettverk under hele testkjøringen, under `requests` og alt annet som måtte
åpne en forbindelse. En test som ved et uhell kaller et ekte endepunkt,
feiler i stedet for å spise av EODHD-kvoten på 20 kall i døgnet — som i CI
ville skjedd på hver eneste push.

Testene kjøres automatisk på hver push og hver pull request mot `main`, se
merket øverst. Workflowen har ingen hemmeligheter og ingen API-nøkkel.

Hver story leveres med test. Det gjelder fra og med signalberegningen, og
det er også svaret vårt på hvordan KI-generert kode kvalitetssikres.

Skillet mellom `docs/` og `_bmad-output/` er bevisst. `docs/` viser hvordan vi kom fram til noe og hvilken rolle KI spilte underveis; `_bmad-output/` viser hva vi kom fram til. Vurderinger vi forkastet, og prompter som ledet til en beslutning, hører hjemme i `docs/ai-prompts/` — ikke i produktdokumentene, som skal kunne leses av seg selv.
