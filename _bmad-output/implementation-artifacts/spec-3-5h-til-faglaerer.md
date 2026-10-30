---
title: 'Story 3.5 (3.5h): «Til faglærer» kortere, og BH4, BH7 og BH9 fra 3.5g'
type: 'docs'
created: '2026-10-30'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'acc5b0e'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-5g-kortere-kom-i-gang.md'
  - '{project-root}/README.md'
  - '{project-root}/docs/hjelp.md'
  - '{project-root}/docs/kvalitetssikring.md'
---

## Intent

«Til faglærer» i README-en kortes ned, og de tre åpne punktene fra 3.5g (BH4, BH7 og BH9) avgjøres, etter gruppens svar 29.10 kl. 19:36 under story 3.5 i `epics.md` (svaret 28.10 kl. 11:23, f). Bare dokumenter og testene for dem.

## Slik er det i dag (slått opp 30.10 på `acc5b0e`)

- «Til faglærer» har ti punkter: dobbeltklikket, Docker med demoen, den ekte versjonen, testene, briefen, PRD-en med arkitekturen og epics, leveranselista, prosessen og vurderingsmatrisen.
- Pila under stegene heter «Demoen og den ekte versjonen», som tabellen øverst.
- Ventingen første gang står i steg 4.
- §9 i `docs/kvalitetssikring.md` har D1–D6. Linja «Linux» har ingen egen rad.

## Avgjørelsene som fortsatt står (regel 3)

- 3.5f: dobbeltklikket står før Docker, og Docker før demoen (`test_til_faglaerer_viser_foerst_til_dobbeltklikket_og_saa_til_docker`).
- 3.3d e (16.10 kl. 21:16, 21:25 og 21:57, og 18.10 kl. 15:37): lenkene til demoen, den ekte versjonen og «Tester» står først, med en kort forklaring, og hvert anker finnes én gang. 3.3i: den ekte versjonen som en invitasjon etter demoen. 3.3e: uv installeres først for testene.
- 12.10 kl. 12:12 og regel 17: briefen med gjeldende tag.
- Regel 19: lenken til «Kort fortalt» i PRD-en står én gang.
- 28.10 kl. 11:23 (e): tabellen står uten pil før «Til faglærer», og «Til faglærer» er siste avsnitt før «Kom i gang».

## Kontrollpunktene

- a) «Til faglærer» er fire korte punkter: prøv appen, testene, dokumentene og prosessen. Alle lenkene fra før står. **Ville feilet hvis** en lenke forsvant, det ble flere enn fire punkter, eller en lenke til et anker brøt.
- b) Pila heter «Velg vei: dobbeltklikk, Docker eller uv», og tabellen øverst beholder «Demoen og den ekte versjonen». **Ville feilet hvis** pila og tabellen fikk samme navn.
- c) Ventingen første gang står i steg 4 som nå (BH4). Ingen endring.
- d) D7 i §9: linja «Linux» og lenkene til Docker og uv (BH9).
- `docs/hjelp.md` følger med (regel 19).

## Planen

1. a) «Til faglærer», med testene.
2. b) Pila, med testene.
3. d) D7.
4. Hele settet, gjennomgang med Blind Hunter og Verification Gap, triagen her og i PR-en, CI, og flettingen hvis alt er grønt før 13:40.
