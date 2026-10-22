---
title: 'Story 3.3 (3.3j): fem spørsmål i «Står du fast?» igjen'
type: 'feature'
created: '2026-10-22'
status: 'review'
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

## Mutantene, kjørt

I en fersk klon med `core.autocrlf=false`, slettet etterpå, én om gangen med `-x`, med kopi før og sha256 lik HEAD etter hver. Kjørt på `3252f5b` og igjen på `1c757b4`, med `tests/test_docker.py`, og en gang til med bare de nye testene (`-k`).

| # | Mutant | Først i fila (`1c757b4`) | De nye testene alene |
|---|---|---|---|
| M1 | Et sjette spørsmål under «Står du fast?» | `test_staar_du_fast_har_hoeyst_5_spoersmaal` | den samme |
| M2 | «Cannot find path … because it does not exist» borte fra spørsmålet | `test_svaret_om_mellomrommet_etter_cd` | `test_begge_meldingene_i_samme_spoersmaal` |

## Gjennomgangen

Gjennomgang 22.10 på diffen `d8ea38c..3252f5b`. Linsene var Blind Hunter (BH, 6 funn, bare diffen), Edge Case Hunter (ECH, 5 funn) og Verification Gap (VG, 3 funn), hver for seg og uten å endre noe i repoet. Edge Case Hunter prøvde begge meldingene i PowerShell 5.1 på maskinen: de står ordrett i meldingene brukeren ser. 14 funn ble 13 rader. Ingen hadde dom medium eller høyere. Rettingene er i `1c757b4`, utenom VG1 og VG2, som føres etter flettingen.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH4, ECH2 | Testen av hjelpen så bare på overskriften, og ikke på en gammel overskrift i en annen form | low | rettet: ordene uten anførselstegn, og begge svarene under spørsmålet |
| ECH1 | `updated` i `docs/hjelp.md` sto på 21.10 | low | rettet: satt fra klokka |
| VG1 | Spesifikasjonen 3.3i sier at «Står du fast?» har høyst 6 | low | rettet etter flettingen: en datert linje der |
| VG2 | Linja under story 3.3 om grensen på 6 | low | rettet etter flettingen: den daterte linja med flettecommiten |
| BH1 | Spørsmålet er langt å lese | low | avvist: gruppen ba om begge meldingene ordrett i spørsmålet |
| BH3 | README-en har ikke setningen om `.zip` til slutt i stien, som hjelpen har | low | uten endring: slik var det før 3.3j, og hjelpen kan ha mer etter svaret |
| ECH4 | Svaret nevner også `'docker'` og `'uv'`, som ikke kommer etter `cd` | low | uten endring: ordlyden er fra før 3.3j |
| ECH3 | De to sidene av testen av «Cannot find path» delte avsnittene ulikt | nit | rettet |
| BH5 | `TestFemSpoersmaal` teller ikke spørsmålene | nit | rettet: docstringen sier hvor grensen står |
| VG3 | Ingen triage eller mutanter i spesifikasjonen før steg 3 | nit | rettet: her |
| BH2 | «Kommer «…»:» er tungt norsk | nit | uten endring: det skiller de to svarene, og testene binder det |
| BH6 | En eldre docstring sier at spørsmålene sto hver for seg | nit | uten endring: historikk, og 3.3j står etter |
| ECH5 | Meldingen fra zsh på Mac har ikke eget spørsmål | nit | uten endring: utenfor 3.3j |

## Det som ikke endres

- Ingen test går på nett. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22).
- Stegene, de andre spørsmålene og bildene. Briefen står.
