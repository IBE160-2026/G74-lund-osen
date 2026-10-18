---
title: 'Story 3.3d: README-en blir lettere å finne fram i'
type: 'docs'
created: '2026-10-18'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f7c0eed'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/hjelp.md'
---

## Intent

**Problem:** README-en er lang, og det er vanskelig å finne fram. «Status» er ett langt avsnitt, «Står du fast?» har 10 spørsmål, uv-delen og «Tester» er tett tekst, «Til faglærer» lenker ikke til det faglærer skal prøve, og det er ingen innholdsliste. Beslutningen 16.10 kl. 21:53–21:58 under story 3.3 i `epics.md` sier at README-en ryddes i en egen PR etter README-PR-en (3.3c), og beslutningen kl. 21:16, med svarene kl. 21:25 og 21:57, sier at «Til faglærer» får lenker til demoen, den ekte versjonen og testene.

**Grunnlaget:** instruksjonen 18.10 kl. 17:04, og svarene på spørsmålene kl. 15:12 i instruksjonen kl. 15:37: lenkene i «Til faglærer» kommer i ryddingen, og ryddingen tar «Står du fast?» ned til fem spørsmål. Grensen på 10 gjaldt bare til ryddingen. PR-en stopper før flettingen og venter på ja.

## Planen, én commit per punkt

1. Denne spesifikasjonen, linja under story 3.3 og linjene i spesifikasjonene for 3.4 og 3.3b.
2. a) «Status» som to lister, «Ferdig» og «Neste», med høyst 8 punkter hver.
3. b) «Står du fast?» med fem spørsmål. De fem som tas ut, står i `docs/hjelp.md` med minst det samme svaret.
4. c) uv-delen under «Mer for den som vil» som to nummererte lister, «Demoen» og «Den ekte versjonen».
5. d) «Tester»: forklaringen om testene som hoppes over, bak knappen «Hvorfor hoppes noen over?».
6. e) Tre lenker først under «Til faglærer»: demoen, den ekte versjonen og «Tester».
7. f) «Innhold» under beskrivelsen, og relative lenker i «Mappestruktur».

## Avgjort i spesifikasjonen

- **De fem spørsmålene** er rådets forslag, ikke avgjort 16.10: «Engine running», ZIP-fila som ser ut som en vanlig mappe, «is not recognized as the name of a cmdlet», «Cannot find path» og «no configuration file provided». De som tas ut: «Mappa lar seg ikke dra inn i vinduet.», «Ingenting skjer når jeg limer inn.», «Cannot connect to the Docker daemon …», «port is already allocated …» og «Oversikten er tom.». Alle fem står i `docs/hjelp.md`, og svaret der begynner med svaret fra README-en.
- **«Neste»** følger rekkefølgen under «Prioritering» etter svarene 18.10 kl. 00:39 og 11:20, med KI-tekstene i demoen (3.4b) og Min liste (8.3) først: historikken (2.7), lenkene til selskapets sider (10.5), egen nøkkel (10.7), innstillingene med «Vis KI-tekst» (8.10 og 8.10b), periodene i kursgrafen og på forsiden periodevalget, børsometeret og KI-teksten om dagen (8.16, 8.17 og 10.6), og til slutt å velge og bytte aksjer (2.11 og 2.12). Det er ni grupper i rekkefølgen, og 8.16, 8.17 og 10.6 er samlet i ett punkt, så lista har 8. 9.9 og 9.10 endrer ikke det appen gjør, og står ikke i «Neste».
- **Overskriftene i uv-delen** er fet tekst, ikke `###`, så de ikke blir egne deler av «Kom i gang» og lager ankre som kan forveksles med «Demoen» og «Den ekte versjonen (anbefalt)» over.
- **Lenkene i «Mappestruktur»** peker på stier som finnes og ikke holdes ute av `.gitignore`. `data/`, `local-tests/`, `_privat/` og `.env` blir ikke lenker.
  *Rettet 2026-10-18 (gjennomgangen, BH8):* rekkefølgen har ti grupper, ikke ni: 3.4b, 8.3, 2.7, 10.5, 10.7, 8.10 og 8.10b, 8.16, 8.17, 10.6, og 2.11 og 2.12. Når 8.16, 8.17 og 10.6 er samlet i ett punkt, blir det 8.
  *Lagt til 2026-10-18 (gjennomgangen, BH1, VG3 og VG4):* «Neste» har bare det svarene kl. 00:39 og 11:20 nevner. Derfor står ikke 9.9 og 9.10, tester i ekte nettleser, UX-gjennomgangen (8.2) eller tabellen på smal skjerm (svaret 17.10 kl. 22:38–22:42) der. «Ferdig» har med alt som er flettet, også 9.1, 9.7 og 9.8, som ikke endrer appen, fordi instruksjonen sier «alt som er flettet til nå». «Historikken og signaldagene i grafen» er teksten fra før, og signaldagene er story 8.8, som rekkefølgen fra 14.10 hadde sammen med 2.7. «Lenkene til selskapets side på NewsWeb og selskapets egen nettside» er 10.5 slik storyen ble utvidet 30.09. Svaret kl. 00:39 nevner bare nettsiden, men storyen har begge lenkene, så det er ikke et sprik.

## Boundaries

- Bare dokumenter og tester. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- Ingen kommando i README-en endres.

## Mutantene

Én om gangen med `-x` på `tests/test_docker.py` og `tests/test_ryddighet.py`, i en fersk klon med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver, og `git status` tom etter hver. N1–N6 er fra instruksjonen. N6 overlevde først på `8dc1e8f`: `ignorert()` leste `data` som en fil, og «data/» i `.gitignore` gjelder bare mapper. Testen ble rettet i `ff2f540`, og N1–N6 ble fanget der. N7–N10 er for funnene med dom medium, og alle ti ble fanget på `fc84a57`:
- N1, «Min liste» før «KI-tekstene i demoen» i «Neste»: `test_status_uten_storynumre_og_uten_kommando`.
- N2, et sjette spørsmål under «Står du fast?»: `test_staar_du_fast_har_hoeyst_5_spoersmaal`.
- N3, «Oversikten er tom.» tatt ut av `docs/hjelp.md`, så spørsmålet står ingen av stedene: `test_hvert_tema_staar_i_readme_eller_hjelp` (og `test_spoersmaalene_som_ble_tatt_ut_staar_i_hjelp`).
- N4, forklaringen i «Tester» utenfor knappen: `test_forklaringen_i_tester_staar_bak_en_knapp`.
- N5, `#statusen` i «Innhold»: `test_lenkene_virker`.
- N6, en lenke til `data/` i «Mappestruktur», med `data/db/` laget i klonen: `test_mappestrukturen_lenker_til_stier_i_repoet`.
- N7, en tom linje inni «Ferdig» (ECH2): `test_status_uten_storynumre_og_uten_kommando`.
- N8, `powershell-mappa.png` uten lenke (BH3): `test_mappestrukturen_lenker_til_stier_i_repoet`.
- N9, `../G74-lund-osen/src/` som mål for `src/` (ECH3): `test_lenkene_virker` i klonen, som har et annet mappenavn, og `test_mappestrukturen_lenker_til_stier_i_repoet` alene med `-k`.
- N10, «fra kl. 21 på børsdager» tatt ut av «Ferdig» (VG1): `test_status_uten_storynumre_og_uten_kommando`.
- *Lagt til 2026-10-18 (gruppens svar kl. 17:40):* N11, «Cannot connect to the Docker daemon» tatt ut av det første spørsmålet, fanget på `db9ffaf` av `test_staar_du_fast_har_hoeyst_5_spoersmaal`, og av `test_det_foerste_spoersmaalet_er_at_docker_ikke_kjoerer` alene med `-k`.

## Gjennomgangen

Gjennomgang 18.10 på diffen `f7c0eed..ff2f540`. Linsene var Blind Hunter (BH, 12 funn, bare diffen), Edge Case Hunter (ECH, 8) og Verification Gap (VG, 13, der VG5, VG7, VG8, VG11 og VG13 fant kravene oppfylt). Ingen av dem kjørte pytest. Åtte rader har dom medium. Sju er rettet i `df014f7` og `fc84a57`, og én er avvist.

| # | Funn | Dom | Rute |
|---|---|---|---|
| VG1, BH1 | «Ferdig» manglet hentingen fra kl. 21 (PR #60), bildene og demoen først (3.3c), kvalitetssikringen (9.1) og ryddingen (9.8), og «formatterer» var feilstavet | medium | patch. N10 |
| BH2 | Demolenken hoppet over steg 1–4 | medium | patch: «etter [steg 1–4](#felles-for-begge)» |
| BH3, ECH4 | En sti etter tankestreken kunne miste lenken uten at testen feilet | medium | patch: hver sti i punktet, og nøyaktig 15 lenker. N8 |
| BH4, ECH3, VG9 | Bare siste ledd i målet ble sammenlignet, og `..`, store bokstaver og filer som ikke er sporet, slapp gjennom | medium | patch: målet er lik teksten, uten `..`, og sporet i git. N9 |
| ECH1 | «Ferdig» igjen, mens sprintstatusen sier `review` for 3.4 (gjennomgangen 12.10) | medium | patch: «Ferdig» betyr flettet til main, under listene |
| ECH2 | Et punkt etter en tom linje i en liste ble ikke telt | medium | patch: listene må stå samlet. N7 |
| VG10 | Mutantene og triagen var ikke ført | medium | patch: her, og i Utført-linja |
| BH5 | «Cannot connect to the Docker daemon» og porten er tatt ut av «Står du fast?» | medium | avvist: instruksjonen velger de fem, og svarene står i `docs/hjelp.md`, som «Står du fast?» lenker til |
| BH8 | «ni grupper» gikk ikke opp | low | patch: Rettet-linje over |
| VG3, VG4 | 8.8 og 10.5, og saker fra 17.10 som ikke står i «Neste» | low | patch: forklart over |
| VG12 | «fra punkt a» i linja i spesifikasjonen for 3.3b var upresist | low | patch: Rettet-linje der |
| BH10, ECH7 | Indekser i to strenger, og knappen kunne flyttes under punktene | low | patch. Importen fra `test_ryddighet` står: testene importerer fra hverandre fra før |
| BH11 | «Alle testene skal bestå» alene, mens utskriften viser «skipped» | low | patch: «Noen hoppes over, og knappen under sier hvorfor.» |
| ECH5 | Like overskrifter ga samme anker i testene | low | patch: hvert anker finnes én gang |
| ECH6 | Setningene rundt uv-listene var ikke sjekket | low | patch |
| BH6 | To punkter i «Ferdig» er lange | low | avvist: teksten er den fra før, samlet så lista har høyst 8 |
| BH7 | «børsometeret» og NewsWeb ved siden av børsmeldingene | low | avvist: navnene fra storyene, og setningen om plan B står under |
| BH9, VG6 | Boksene uten innrykk deler listene | low | avvist: som i «Kom i gang». GitHub viser riktige tall |
| BH12 | Spesifikasjonen for 3.4 har den gamle regelen med «Flettet til main» | low | avvist: append-only, og linja rett under sier hva som gjelder nå |
| VG2 | Rekkefølgen i «Neste» mot `epics.md` er sjekket for hånd | low | avvist: VG og ECH fant den riktig, og testen låser den |
| ECH8 | Linja kl. 15:42 i vurderingsmatrisen sier at kopieringen står under «Står du fast?» | low | utsatt: en ny linje i vurderingsmatrisen når PR-en flettes |

*Rettet 2026-10-18 (gruppens svar kl. 17:40, BH5):* raden BH5 er rettet. Det første spørsmålet under «Står du fast?» er nå ett spørsmål om at Docker ikke kjører: «Engine running» kommer ikke, eller det står «Cannot connect to the Docker daemon» eller «error during connect». Svaret har det som sto i begge, og de to står fortsatt hver for seg i `docs/hjelp.md`. Det er fortsatt fem spørsmål. Testen er `test_det_foerste_spoersmaalet_er_at_docker_ikke_kjoerer`. Spørsmålet om porten står bare i `docs/hjelp.md`, og appen får port 8000 i story 3.2b.

*Lagt til 2026-10-18 kl. 18:01:* PR #67 er squash-flettet i `1be3a57`, låst til head-en `8ffa969`. Main var flettet inn i `8ffa969`, med en konflikt i `epics.md`: linja for 3.3d og linja kl. 17:40 sto begge under linja kl. 15:41. Begge står. Mens PR-en hadde konflikten, startet ikke CI for `db9ffaf`. CI var grønn på `ec96388` (39140683606), på `8ffa969` (39142845474) og på main (39142953539). Triagen står som kommentar i PR #67. ECH8 er rettet med linja i vurderingsmatrisen.
