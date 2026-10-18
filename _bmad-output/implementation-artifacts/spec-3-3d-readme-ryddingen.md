---
title: 'Story 3.3d: README-en blir lettere å finne fram i'
type: 'docs'
created: '2026-10-18'
status: 'in-progress'
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

## Boundaries

- Bare dokumenter og tester. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- Ingen kommando i README-en endres.
