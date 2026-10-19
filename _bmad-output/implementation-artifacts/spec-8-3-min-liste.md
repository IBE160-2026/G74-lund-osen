---
title: 'Story 8.3: Min liste, med stjerne i oversikten og en egen side'
type: 'feature'
created: '2026-10-19'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '7f2c11c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-7a-stilen-i-en-css-fil.md'
---

## Intent

**Problem:** briefen v8 lover «Min liste» i v1, og story 8.3 står igjen. I dag har appen bare oversikten og aksjesiden, og ingen måte å følge et utvalg av aksjene på.

**Grunnlaget:** story 8.3 i `epics.md`, gruppens svar 19.10 kl. 10:29 under «Prioritering» og under story 8.3, og instruksjonen 19.10 kl. 20:20. Føringen 2026-09-30 under AD-3 sier at merkingen blir et eget datasett med egen port og webserveren som eneste skriver, og at navnet på porten settes når 8.3 bygges. Regel 22 i `CLAUDE.md` har fått en datert linje om at webserveren fra main skriver merkingen, og grenen bygges derfor i en egen worktree utenfor repo-mappa.

## Kontrollpunktene

- a) Lagringen: migrasjonen `0007` med en egen tabell for merkingen, med bare symbolet og en trigger mot `aksje` som for de andre tabellene (AD-21). En egen port etter navneregelen, i minnet og i `lagring_sqlite.py` (AD-3). Demoen merker fem av selskapene, fra begge delene av tabellen.
- b) Merkingen: en POST som bryteren for KI-teksten (`/ki` i `app.py`), med 403 fra en annen side, bare egne stier tilbake, og 303 til samme side med sorteringen. Webserveren skriver bare den nye tabellen og henter aldri (AD-10).
- c) Sidene: i stripa på alle sidene en knapperad med «Markedsoversikt» og «Min liste», der knappen for siden man står på, er fylt (`aria-current`). Aksjesiden beholder veien tilbake. På hver rad i oversikten og i Min liste står en stjerne i cellen for Selskap, foran navnet, så tabellen har fem kolonner (FR-101): fylt når aksjen er merket, en knapp med `aria-pressed` og selskapets navn, og «★ = Min liste» under «Selskap». `/min-liste` har overskriften «Min liste», en kort tekst om at stjernen legger aksjen i lista uten kall, knappen «Alle / Min liste» med antallet, og samme tabell i samme rekkefølge (FR-102), også med sorteringen fra 8.15. En tom liste sier hvordan man merker. Alt virker på 390 px uten vannrett rulling. Hjelpen, `docs/hjelp.md` og README-en følger med (regel 19). Stilen står i CSS-fila. Bildene tas på nytt slik feilmeldingen i testen sier.
- d) Testene, med «Ville feilet hvis»: merkingen overlever en omstart; filteret endrer ikke rekkefølgen, heller ikke sortert; tabellen for merkingen har ingen kolonne for antall, beløp eller kurs; et ukjent symbol avvises i porten og i basen; en POST fra en annen side og en fremmed adresse tilbake; under en merking skrives bare den nye tabellen; lista som parameter, også med færre enn 15 aksjer; den tomme lista; den fylte knappen på hver side; kontrasten til stjernen. Spinen får daterte linjer under AD-3, AD-10 og AD-16.

## Planen, én commit per punkt

1. a) `src/migrasjoner/0007_min_liste.sql`, porten og de to lagerne, og merkingen i demoen.
2. b) POST-ruten for merkingen i `app.py`.
3. c) Knapperaden, stjernen, `/min-liste`, stilen i `src/static/stil.css`, hjelpen, `docs/hjelp.md`, README-en og bildene.
4. d) De nye testene, de daterte linjene i spinen, og mutantene.

## Avgjort i spesifikasjonen

- **Navnet på porten** (føringen 30.09 under AD-3) er `Minlistelager`, etter navneregelen i spinen: `<Datasett>lager` er porten med skrivesiden. Den har `MinneMinlistelager` i minnet og `SqliteMinlistelager` i `lagring_sqlite.py`.
- **Rekkefølgen:** Min liste filtrerer radene fra oversikten og sorterer dem ikke på nytt, så rekkefølgen er den samme som i oversikten (FR-102), også når en kolonne er sortert (8.15).
- **Den ekte basen** får en tom tabell fra `0007`. Demoen merker fem (svaret kl. 10:29).

## Avgjort underveis

## Mutantene

Én om gangen med `-x`, med kopi før og sha256 mot HEAD etter hver:

- Merkingen bare i minnet.
- Min liste i annen rekkefølge enn oversikten.
- POST uten Origin-sjekken.

## Gjennomgangen
