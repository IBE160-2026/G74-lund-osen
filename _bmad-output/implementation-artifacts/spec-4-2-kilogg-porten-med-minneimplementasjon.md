---
title: 'Story 4.2: KILogg-porten med minneimplementasjon'
type: 'feature'
created: '2026-10-15'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'de94bc9'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** KI-laget trenger én logg for det KI la til, før modellen kalles (story 4.2 i `epics.md`, FR-604, FR-605). Uten loggen fra første kjøring finnes ikke uka briefen krever, og en tekst kan ikke knyttes til prompten og modellen som laget den.

**Approach:** `src/kilogg.py` er porten: typene `Emne` og `KIRad` med kontrollene, og protokollen `KILogg` med bare `skriv`, `les` og `les_alle` (AD-3, AD-7). `src/kilogg_minne.py` er `MinneKILogg`, som hele porten prøves mot uten database. SQLite-adapteren er story 4.3. PR B i planen for KI-laget.

## Planen

Planen for KI-laget ble vist i chatten 15.10 kl. 15:43 og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-15.md` (`5ce64f6`). Testtallet før: 1633 bestått og 17 hoppet over på main (`de94bc9`).

## Svarene

*Lagt til 2026-10-15 (gruppens svar på de ti spørsmålene i planen, instruksjonen kl. 15:53):* svarene er beslutninger. Alle ti står under Epic 10 i `epics.md`. De som gjelder denne storyen:

- Svar 2: raden står når den finnes, også når modellen feilet (FR-604). `skriv` gir da `False` uten å reise.
- Svar 6: loggen gir plass til dagsteksten i 10.6, med en dato som eneste emne. Et emne er derfor en aksje og en dato (plan B), en melding (plan A) eller dagen alene. Kontrollpunktet i 4.2 om at en rad med ingen av dem avvises, gjelder aksje og melding. Dagen er et eget slag, så den må velges uttrykkelig (`Emne.dagen`).

**Mutantene** (planen kl. 15:43): K1 promptversjon kan mangle; K2 begge emnene godtas; K3 porten har `slett`; K4 en eldre dato godtas; K5 en rad som finnes, skrives over.

## Boundaries & Constraints

- Porten importerer ikke kjernen (AD-3), som `vurderingsdata.py`. Kontrollen av datoen ligger i implementasjonen.
- Ingen database, ingen migrasjon og ingen endring i hentingen. Ingen API-kall.
- «av» er ikke en tjeneste i raden: med KI av skrives ingen rad (svar 5).

## I/O & Edge-Case Matrix

| Inndata | Forventet |
|---|---|
| En rad uten promptversjon eller modell, eller med tom tekst i dem | `UgyldigKIRad` |
| Et emne med både symbol og melding, eller et felt slaget ikke har | `UgyldigKIRad` |
| `besto=True` uten tekst eller med grunn, eller `besto=False` uten grunn | `UgyldigKIRad` |
| Modellen feilet: ingen tekst, `besto=False` og en grunn | raden godtas |
| `skriv` med en annen dato enn inneværende børsdag | `ValueError`, ingenting skrevet |
| `skriv` for et emne som finnes | `False`, den første raden står |
| `les_alle` | alle slag, ordnet etter dato og så rekkefølgen de ble skrevet i |

</frozen-after-approval>

## Code Map

- `src/kilogg.py`: `Emne`, `KIRad`, `UgyldigKIRad` og protokollen `KILogg`.
- `src/kilogg_minne.py`: `MinneKILogg`.
- `tests/test_kilogg.py`: testene for kontrollpunktene.

## Spec Change Log

## Review Triage Log

## Verification
