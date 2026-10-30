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

- «Til faglærer» har ni punkter: dobbeltklikket, Docker med demoen, den ekte versjonen, testene, briefen, PRD-en med arkitekturen og epics, leveranselista, prosessen og vurderingsmatrisen.
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
- `docs/hjelp.md` følger med (regel 19). Slått opp: hjelpen nevner verken «Til faglærer» eller pila, så den er uendret.

## Planen

1. a) «Til faglærer», med testene.
2. b) Pila, med testene.
3. d) D7.
4. Hele settet, gjennomgang med Blind Hunter og Verification Gap, triagen her og i PR-en, CI, og flettingen hvis alt er grønt før 13:40.

## Gjennomgangen

Gjennomgang 30.10 etter hele settet (3864 bestått, 24 hoppet over, 6 feilet, alle i porttestene for `start.ps1` som CI avgjør, 12:31:39–12:40:28 på `2f4d5ee`), av diffen `acc5b0e..2f4d5ee`, med Blind Hunter (BH, 16 funn) og Verification Gap (VG, 1). Dommen i tabellen er vår. Rettet i commiten etter `2f4d5ee`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1 | Spesifikasjonen sa ti punkter, men lista har ni | low | **rettet**: «ni punkter», talt i `git show acc5b0e:README.md` |
| BH2, VG1 | D6 ender fortsatt med spørsmålet om linja «Linux», og D7 spør om det samme | low | **rettet** med en ny linje: D6 kan ikke kortes, fordi ingen linje fjernes fra kvalitetssikringen. Den daterte linja over tabellen sier at spørsmålet besvares i D7 |
| BH3 | «fra steg 1» i D7 sa ikke hvilken vei (ECH7, 27.10) | low | **rettet**: «fra steg 1 med Docker eller fra uv» |
| BH4 | Testen for D7 sjekker ikke D6 | low | **står**: D6 er uendret med vilje (BH2) |
| BH5, BH6 | Pila begynner med «Velg vei», som overskriften inni, og innholdet begynner med den ekte versjonen | low | **avvist**: navnet er gruppens svar (b), og innholdet står (avtrykket) |
| BH7 | Punktet «Dokumentene» er langt | low | **står**: svaret a sier fire punkter med alle lenkene |
| BH8 | Forklaringene til leveranselista og vurderingsmatrisen, «plan og krav» og «låst i taggen» falt ut | medium | **rettet**: de står igjen, kort |
| BH9 | Invitasjonen til den ekte versjonen fra 3.3i ble svakere | low | **rettet**: «Prøv gjerne ekte kurser etterpå», og testen krever det |
| BH10 | «Testene: de automatiske testene» | low | **rettet**: «Testene: de automatiske» |
| BH11 | Tom forklaring før lenken til demoen i testen | low | **rettet**: testen krever «](#med-docker-desktop) (» foran |
| BH12 | Kommentarer i testene nevner pila med det gamle navnet | low | **står**: de er historikk fra 3.5g, og konstanten `VELG_VEI_PIL` sier det nye |
| BH13 | Testen sjekket ikke at pila står rett etter linja «Linux» | low | **rettet**: bare `<details>` står mellom |
| BH14 | `docs/hjelp.md` var ikke nevnt som slått opp | low | **rettet**: hjelpen nevner verken «Til faglærer» eller pila |
| BH15 | Linjene i 3.5g sa «Rettet i 3.5h» før flettingen | low | **rettet**: de viser til commitene på grenen |
| BH16 | Status og frist uten reserve | low | **avvist**: status settes til `done` ved flettingen, og instruksjonen sier at det stoppes etter 13:40 |

Ord før «Kom i gang» (telt med `\w+` i råteksten, også lenkeadressene): 537 på `acc5b0e`, 506 etter a, og 523 etter rettingene.
