---
title: 'Story 8.15 (8.15b): Selskap kan sorteres, og den sorterte kolonnen synes'
type: 'feature'
created: '2026-10-18'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'd6e2d1c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-15-sortering-ved-klikk-i-kolonneraden.md'
---

## Intent

**Problem:** I oversikten kan Sluttkurs, Endring, Signalstyrke og Retning sorteres ved klikk (story 8.15), men ikke Selskap. Den sorterte kolonnen skilles fra de andre bare av fargen på vinkelen. Designtavla har sorteringsmerket på Selskap, og et lysere felt med en oransje strek under den sorterte kolonnen.

**Grunnlaget:** gruppens svar 18.10 kl. 22:06 og instruksjonen 18.10 kl. 23:58.

## Kontrollpunktene

- a) Selskap: navnet i kolonneraden blir en sorteringslenke som de andre, med vinkel, og «?» ved siden av. Første klikk gir A til Å i den norske rekkefølgen som alt brukes ved lik verdi (Æ, Ø og Å etter Z, uten forskjell på store og små bokstaver), og et nytt klikk snur. Sorteringen gjelder innenfor hver del, som før (tillegget 13.10). Linja over tabellen og teksten for skjermleseren sier «stigende (A til Å)» eller «synkende (Å til A)», som for Retning. Hjelpen og `docs/hjelp.md` følger med der sorteringen nevnes (regel 19).
- b) Markeringen: kolonnen tabellen er sortert på, får et lysere felt og en oransje strek under i kolonneraden, med fargene i `designregler.md`, og kontrasten regnes i testene for utseendet. `designregler.md` får en datert linje om det under linja fra 15.10 om vinkelen. Endres en fil bak bildet av oversikten, tas bildet på nytt slik feilmeldingen i testen sier.
- c) Testene, med «Ville feilet hvis»: Selskap sorteres i norsk rekkefølge og innenfor hver del; et nytt klikk snur; bare den sorterte kolonnen har markeringen, og uten sortering har ingen den; `aria-sort` som før. Mutanter én om gangen med `-x` og kopi før og sha256 mot HEAD etter: navnet sortert på kodepunkt, markeringen på alle kolonnene, og Selskap sortert på tvers av delene.

## Planen, én commit per punkt

1. a) `selskap` i `SORTERBARE` med stigende først, verdien er navnet med `_navn` (norsk rekkefølge), lenken og «?» i kolonneraden, ordene «(A til Å)» og «(Å til A)», og bildet av oversikten tatt på nytt, fordi Selskap får en vinkel.
2. b) Markeringen i stilen, med velgeren `th[aria-sort]`, så den følger `aria-sort`, som bare står på den sorterte kolonnen. Linja i `designregler.md`, og bildet på nytt hvis avtrykket endres.
3. c) Testene.

## Avgjort i spesifikasjonen

- **Fargene:** feltet er `#3A3E47`, kanten i stripa i `designregler.md` §5, og streken er sterk oransje `#F2B53A` (`--oransje`, §3), 3 px nederst i cellen. Begge står i `designregler.md`. Det lysere feltet står ikke med egen farge der, så kanten fra stripa brukes, fordi den er den lyseste av de mørke fargene og hører til samme flate.
- **Markeringen følger `aria-sort`**, så det ikke er to ting som kan si hvilken kolonne som er sortert.
- **Bildet** tas på nytt i a, fordi Selskap får en vinkel i kolonneraden, så hver commit har et bilde som stemmer.

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Bildet tas fra en demobase i en midlertidig mappe.
