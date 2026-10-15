---
title: 'Story 10.3: Visningen i aksjedetaljen'
type: 'feature'
created: '2026-10-15'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '5586924'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** KI-teksten lagres i `KILogg` (4.3, og PR F når den er flettet), men siden viser den ikke. Story 10.3 krever at regelforklaringen står først, og at KI-teksten står under den som et tillegg, merket som laget av KI, med en bryter brukeren ser (FR-601, FR-602, NFR-06).

**Approach:**
- `src/ki_visning.py` (ren logikk): `bygg_ki_visning` regner hva siden viser av raden og vurderingen. Teksten vises bare når grunnlaget stemmer med vurderingen (FR-602) og ingen av ordene «kjøp», «selg» eller «anbefal» står i den (NFR-06). Ellers viser siden hvorfor dagen er uten KI-tekst.
- `src/app.py`: aksjedetaljen leser raden i `KILogg` med forespørselens tilkobling og viser den bare når bryteren er på. `POST /ki` setter bryteren som en informasjonskapsel og går tilbake til siden (svar 4).
- `src/templates/aksje.html`: «Med KI-ens ord» under regelforklaringen og over grafen, og knappen «Skjul KI-teksten» eller «Vis KI-teksten». Uten vurdering vises ingen av delene.

PR G i planen for KI-laget. Flettes etter at gruppen har sett siden (instruksjonen kl. 22:36).

## Planen

Planen for KI-laget ble vist i chatten 15.10 kl. 15:43 og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-15.md` (`5ce64f6`). Testtallet før: 2037 bestått og 17 hoppet over på main (`5586924`).

## Svarene

*Lagt til 2026-10-15 (gruppens svar på de ti spørsmålene i planen, instruksjonen kl. 15:53):* svarene er beslutninger. Alle ti står under Epic 10 i `epics.md`. De som gjelder denne storyen:

- Svar 3: er vurderingen skrevet på nytt samme dag, og grunnlaget i raden stemmer ikke lenger, vises dagen uten KI-tekst (FR-602).
- Svar 4: bryteren huskes i en informasjonskapsel nå. 8.10b flytter den til innstillingene og bruker samme kapsel (`ose_ki`).
- Svar 7: 3.4b, KI-tekstene i demoen, kommer rett etter 10.3. Til da viser demoen «Ingen KI-tekst for denne dagen.», og siden kaller aldri en modell (AD-10, FR-411).

**Mutantene** (planen kl. 15:43): V1 KI-teksten står før regelforklaringen; V2 teksten vises når grunnlaget ikke stemmer med vurderingen; V3 et tomt felt i stedet for «ingen KI-tekst»; V4 et ord fra vakten vises.

## Boundaries & Constraints

- Webserveren skriver aldri i `KILogg` og importerer ingen modell (AD-10). Ingen API-kall.
- Ingen JavaScript: bryteren er et skjema med `POST`. Fokus i blekk på lys bakgrunn (designreglene).
- Grenen bruker bare testbaser (regel 22). Bildene ligger bare i scratchpad.

## I/O & Edge-Case Matrix

| Inndata | Forventet |
|---|---|
| En rad som besto, med grunnlaget lik vurderingen | teksten under regelforklaringen, merket «Laget av KI · gemma4:e4b, lokal» |
| Ingen rad | «Ingen KI-tekst for denne dagen.» |
| Modellen feilet, eller teksten besto ikke kontrollen | grunnen, uten teksten |
| Grunnlaget stemmer ikke med vurderingen | «… vurderingen er skrevet på nytt …», uten teksten |
| «kjøp», «selg» eller «anbefal» i en tekst som besto | grunnen, uten teksten |
| Bryteren av | ingen KI-del, og siden er lik med og uten rad |
| Ingen vurdering (en grunn) | ingen KI-del og ingen bryter |
| `KILogg` kan ikke leses | «Ingen KI-tekst for denne dagen.» |
| `POST /ki` med en adresse utenfor siden | tilbake til / |

</frozen-after-approval>

## Code Map

- `src/ki_visning.py`: `bygg_ki_visning`, `KIVisning`, `ki_paa`, `KAPSEL`.
- `src/app.py`: `aksjedetalj`, `_ki_visning`, `ki_bryter`.
- `src/templates/aksje.html`: delen «Med KI-ens ord» og bryteren.
- `tests/test_ki_visning.py`.

## Spec Change Log

## Review Triage Log

## Verification
