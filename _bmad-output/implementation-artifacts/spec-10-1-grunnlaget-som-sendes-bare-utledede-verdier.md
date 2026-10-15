---
title: 'Story 10.1: Grunnlaget som sendes — bare utledede verdier'
type: 'feature'
created: '2026-10-15'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'a2f71ae'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/docs/kilder-og-rettigheter.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Det som sendes til modellen, må være bestemt av én ren funksjon, så ingen kan sende rådata ved et uhell (story 10.1 i `epics.md`, betingelse 4 og merknaden 04.10 i 4.1, `prd.md` §4.6).

**Approach:** `ki_grunnlag(kilde)` i `src/ki_grunnlag.py` tar et `Signal` eller en `Vurdering` og gir fortegnet for de tre sjekkene, styrken og retningen, og ingenting annet. En aksje utenfor de 15 (FR-412) får merket «Utenfor målingen». Grunnlaget er det `KIRad.grunnlag` lagrer (4.2). Ingen modell kalles. PR D i planen for KI-laget.

## Planen

Planen for KI-laget ble vist i chatten 15.10 kl. 15:43 og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-15.md` (`5ce64f6`). Testtallet før: 1721 bestått og 17 hoppet over på main (`a2f71ae`).

## Svarene

*Lagt til 2026-10-15 (gruppens svar på de ti spørsmålene i planen, instruksjonen kl. 15:53):* svarene er beslutninger. Alle ti står under Epic 10 i `epics.md`. Det som gjelder denne storyen:

- Svar 10: «antall» gjelder dagsteksten i 10.6, og 10.1 sender ikke antall. Ført også under §4.6 i PRD-en.

**Mutantene** (planen kl. 15:43): G1 `dagens_endring` med; G2 `volumforhold` med; G3 sluttkursen med; G4 styrken som desimaltall.

## Boundaries & Constraints

- Ren logikk: ingen I/O, ingen modell, ingen endring i hentingen. Ingen API-kall.
- Ingen kurser, volumer, prosenter, forholdstall eller målinger, og ingen antall (beslutningen 04.10, svar 10).

## I/O & Edge-Case Matrix

| Inndata | Forventet |
|---|---|
| `Signal` fra `beregn_signal` | `trend`, `bevegelse`, `interesse`, `styrke` og `retning` |
| `Vurdering` fra samme serie | det samme |
| `utenfor_maalingen=True` | de samme verdiene og `merke: «Utenfor målingen»` |
| En sjekk med ukjent navn, eller styrke utenfor 0–3 | `ValueError` |
| Noe annet enn `Signal` eller `Vurdering` | `TypeError` |

</frozen-after-approval>

## Code Map

- `src/ki_grunnlag.py`: `ki_grunnlag`.
- `tests/test_ki_grunnlag.py`: testene for kontrollpunktene.

## Spec Change Log

## Review Triage Log

## Verification
