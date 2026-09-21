# G74 — Ai Ai Ai

[![tester](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml/badge.svg)](https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml)

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

Repoet inneholder gruppens applikasjon og dokumentasjon av utvikling, testing og kvalitetssikring med KI.

## Medlemmer

- Joakim Lund
- Marian Osen

## Mappestruktur

- `src/` — applikasjonen
- `tests/` — automatiske tester, kjøres med `uv run pytest`
- `docs/` — arbeidsprosessen: refleksjonslogg og lagrede KI-prompts
- `_bmad-output/planning-artifacts/` — produktdokumentene: product brief, PRD med begrunnelser og målinger, og gjennomgangene av dem

Utenfor versjonskontroll, og derfor ikke i repoet: API-nøkkel (`.env`), lokale
testskript (`local-tests/`) og hentede rådata (`data/`).

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
