---
title: 'Story 2.9b: søylene under hovedindeksen'
type: 'feature'
created: '2026-10-17'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'e0519b5'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/src/hovedindeks.py'
  - '{project-root}/src/templates/index.html'
---

## Intent

**Problem:** delen om hovedindeksen på forsiden (story 2.9) viser verdien, endringen og «x av N gikk bedre», men ikke hvilke aksjer som trakk opp og ned. FR-105 og story 2.9b i `epics.md` ber om én søyle per aksje med dagens endring under indeksen.

**Grunnlaget:** instruksjonen 17.10 kl. 23:13, steg 4, kontrollpunktene under story 2.9b og svaret 16.10 kl. 18:04: søylene viser bare dagens tall. Periodene og «Velg dag» kommer med 8.17.

## Planen, én commit per punkt

1. Denne spesifikasjonen.
2. `src/hovedindeks.py`: `Soeyle` og `bygg_soeyler`. Én søyle per aksje i lista med kurs for indeksens dato og en rad før, sortert fra størst fall til størst stigning. Høyden og plassen til indekslinja regnes her, ikke i malen. `Hovedindeksvisning` får søylene, og `app.py` gir hvilke aksjer som har 3 av 3.
3. `src/templates/index.html`: søylene under «x av N», med bransjesymbolet over tickeren, den stiplede linja for indeksen, en tekst for skjermleser med alle tallene, og teksten bak «?» i vinduet for hovedindeksen.
4. `designregler.md`: fargegrensene og gult ved 3 av 3 for søylene.
5. Testene for demoen: søylene mot DEMIX.

## Avgjort i spesifikasjonen

- **Hvilke aksjer.** En aksje får søyle når den har kurs for indeksens dato og en rad før den, så endringen fra FR-101 kan regnes (`aksjeendring`, som «x av N» bruker). En aksje uten kurs for dagen står allerede under «Ikke med». En aksje med kurs, men uten rad før, får ingen søyle og navngis under søylene. Antallet telles, aldri et fast 15 (føringen 30.09 under AD-21).
- **Rekkefølgen.** Fra størst fall til venstre til størst stigning til høyre, på endringen uavrundet. Er to like, står de i rekkefølgen fra lista.
- **Fargegrensene.** De følger endringen slik den vises, med to desimaler (`tallformat.avrundet`), som tabellen og endringen ved indeksen (story 2.9):
  - over 0,00 % gir Positiv `#13703C` (6,16:1 mot hvitt);
  - under 0,00 % gir Negativ `#B42318` (6,57:1);
  - 0,00 % gir Ingen `#5F646C` (5,96:1).

  Det samme gjelder søylene og den stiplede linja. Ingen andre grenser: lengden på søylen viser hvor stor endringen er.
- **Skalaen.** Null står midt i feltet. Den største endringen, av søylene og indeksen, fyller halve høyden. Er alle 0, er skalaen 1 %.
- **Gult ved 3 av 3.** Bransjesymbolet tegnes i `#a67c00` (3,82:1 mot hvitt), som var «Gul ring» i designregler §5. Sterk oransje `#F2B53A` har 1,83:1 mot det hvite kortet, under 3:1 for grafikk som bærer mening (WCAG 1.4.11). «3 av 3» står også i teksten for skjermleser.
- **390 px.** Søylene deler bredden likt (`flex: 1 1 0`, `min-width: 0`), og tickeren står loddrett. Da får 15 søyler plass uten fast bredde, og siden ruller ikke sideveis.
- **Linja.** Den stiplede linja tegnes bare når indeksen har en endring. Uten den står søylene alene, og teksten sier at linja mangler.

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke mot EODHD. `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Demobaser lages bare i midlertidige mapper.
- Ingen ny tabell og ingen nye kall: endringen er den i FR-101, og bransjen står i `AKSJEUNIVERS`.
