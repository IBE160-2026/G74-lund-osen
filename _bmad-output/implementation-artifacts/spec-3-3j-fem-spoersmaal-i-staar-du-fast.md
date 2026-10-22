---
title: 'Story 3.3 (3.3j): fem spørsmål i «Står du fast?» igjen'
type: 'feature'
created: '2026-10-22'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'b751e91'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3i-readme-rettingen-etter-demoen.md'
---

## Intent

**Problem:** etter 3.3i (`a98146b`) har «Står du fast?» seks spørsmål, fordi svaret på at 127.0.0.1 nektet å koble til kom i tillegg. Avgjørelsen 16.10 kl. 21:53–21:58 sa fem.

**Grunnlaget:** gruppens svar 22.10 kl. 17:42 under «Prioritering» og story 3.3 i `epics.md`: de to svarene om `cd` i steg 4, «is not recognized as the name of a cmdlet» og «Cannot find path … because it does not exist», blir ett spørsmål med begge meldingene ordrett, så «Står du fast?» har fem spørsmål. Det erstatter grensen på 6 fra 3.3i. Instruksjonen er den kl. 17:43 i dagsfila 22.10.

## Kontrollpunktene

- a) README-en: ett spørsmål for begge meldingene etter `cd` i steg 4, med svarene fra begge, og `docs/hjelp.md` følger med (regel 19). Lenker som peker til de to, peker til det nye. Søket 22.10 fant ingen lenker til dem i README-en, `docs/` eller `src/`.
- b) Testene, med «Ville feilet hvis»: «Står du fast?» har høyst 5 spørsmål igjen, og begge meldingene står ordrett i det samme spørsmålet.

## Planen, én commit per punkt

1. a) Spørsmålet i README-en er «is not recognized as the name of a cmdlet» eller «Cannot find path … because it does not exist» etter cd., i samme form som de andre. Svaret på den første meldingen står i ett avsnitt og svaret på den andre i neste, ordrett som før, med «Kommer …» foran hvert. I `docs/hjelp.md` erstatter det samme spørsmålet de to under «Steg 4: mappa», med samme svar, og setningen om `.zip` til slutt i stien, som bare står i hjelpen. `BEHOLDT_I_README`, `test_svaret_om_mellomrommet_etter_cd` og `test_svaret_om_cannot_find_path` i `tests/test_docker.py` rettes til det ene spørsmålet i samme commit, så hver commit er grønn.
2. b) De nye testene, og grensen i `test_staar_du_fast_har_hoeyst_5_spoersmaal` tilbake til 5. Navnet står, fordi `docs/vurderingsmatrise.md` og vedlegget i `docs/kvalitetssikring.md` nevner testen.

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter:

- **M1:** et sjette spørsmål under «Står du fast?».
- **M2:** den ene meldingen borte fra spørsmålet.

## Det som ikke endres

- Ingen test går på nett. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22).
- Stegene, de andre spørsmålene og bildene. Briefen står.
