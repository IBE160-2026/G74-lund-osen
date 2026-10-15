---
title: 'Story 8.15: Sortering ved klikk i kolonneraden'
type: 'feature'
created: '2026-10-15'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'c33fd96'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Oversikten står alltid i FR-102-rekkefølgen. Brukeren kan ikke sortere på kursen, endringen, signalet eller retningen (story 8.15 i `epics.md`, med tillegget 13.10, og FR-102-tillegget 08.10).

**Approach:** Kolonnenavnene i den svarte kolonneraden blir lenker med en parameter i adressen (`?sorter=…&orden=…`). Sorteringen gjøres i Python, hver del for seg, uten JavaScript. Én pull request, grenen `8-15-sortering`.

## Planen

Planen ble vist i chatten 15.10 kl. 13:44 og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-15.md` (`ab6c9c7`). Testtallet før: 1569 bestått og 16 hoppet over på main (`73cdc45`).

- Lenker med parameter i adressen, fordi malene ikke har `<script>`, og `test_ingen_skript_og_ingenting_fra_nettet` krever det. Ukjent eller manglende parameter gir FR-102.
- `sorter` i `src/markedsoversikt.py` sorterer én del. Ruten bruker den på hver del etter `del_i_to`, så ingen rad flytter seg mellom «Skilte seg ut» og «Øvrige aksjer» (tillegget 13.10). Den tar en vilkårlig liste, så den kan brukes på Min liste (8.3).
- Ved lik verdi gjelder FR-102 og så navnet. Bare hovedkriteriet snus. Rader uten verdi står sist i begge retninger.
- I kolonneraden: navnet er en lenke med en vinkel som SVG (`aria-hidden`), og «?» står ved siden av, utenfor lenken. `aria-sort` på kolonnen som er valgt, skjult tekst for skjermleseren, og oransje fokusring på blekk, som «?».
- Ved 390 px ruller tabellen i sin egen boks som før (avvik 8).
- README-statusen: «sortering ved klikk i kolonneraden» flyttes fra «Neste:» til «Flettet til main» (regel 19).

## Svarene

*Lagt til 2026-10-15 (gruppens svar på de sju spørsmålene i planen, instruksjonen kl. 14:01):* svarene er beslutninger:

1. Første klikk gir synkende (høyest kurs, størst oppgang og sterkest signal først), og neste klikk stigende. Endring sorteres med fortegn ved klikk. Standarden i FR-102 står som før. Ført også under FR-102 i PRD-en.
2. Retning kan sorteres som en gruppering i alfabetisk rekkefølge, Blandet, Ingen, Negativ og Positiv, med FR-102 innenfor hver gruppe og Ukjent sist i begge retninger. Første klikk gir A til Å, og teksten for skjermleseren sier «alfabetisk». Ført også under FR-102 i PRD-en.
3. Lenken «Markedsoversikt» går til standarden (FR-102). Tilbakeknappen i nettleseren beholder sorteringen.
4. Kolonnene som kan sorteres, har en dempet vinkel i `#B9BDC5` når de ikke er valgt, og en hvit vinkel når de er valgt. Ført også i designregler §5.
5. Når en kolonne er valgt, står en linje rett over tabellen, «Sortert på <kolonne>, synkende» eller «stigende», og lenken «Standard rekkefølge» til /. Uten valg står ingen linje. Ført også i designregler §5.
6. Ingen ny hjelpetekst. Vinklene og teksten for skjermleseren sier det.
7. Linja om 3 av 3 og «N av M aksjer» følger FR-102 uansett sortering.

Resten av planen gjelder som vist.

**Mutantene** (planen kl. 13:44 og instruksjonen kl. 14:01): S1 sortering over hele tabellen, ikke per del; S2 rader uten verdi først når rekkefølgen snus; S3 endring sortert på kroner; S4 endring sortert på absoluttverdi; S5 lenken snur ikke; S6 `aria-sort` mangler eller står på feil kolonne; S7 ukjent parameter gir feil eller en annen rekkefølge enn FR-102; S8 vinkelen som tegnet ↑ eller ↓; S9 fokus i blekk; S10 uten FR-102 ved lik verdi; S11 Retning sortert med Positiv først; S12 linja over tabellen står også uten valg; S13 den dempede vinkelen er hvit.

## Boundaries & Constraints

- Ingen JavaScript og ingenting fra nettet (`test_ingen_skript_og_ingenting_fra_nettet`).
- Fortsatt fem kolonner (FR-101). Ingen ny hjelpetekst (svar 6).
- Pilene er bare for retning (designregler §4): vinkelen er en SVG, ikke tegnene ↑ og ↓.
- Grenen bruker bare testbaser (regel 22). Ingen API-kall.

## I/O & Edge-Case Matrix

| Inndata | Forventet |
|---|---|
| `/` uten parameter | FR-102, ingen linje over tabellen, ingen `aria-sort` |
| `?sorter=endring` uten `orden`, eller ukjent kolonne eller orden | FR-102, som uten parameter |
| `?sorter=signal&orden=stigende` med rader uten vurdering | radene uten vurdering sist i hver del |
| `?sorter=endring&orden=synkende` med en rad med én kursdag | raden uten endring sist |
| Lik verdi | FR-102, så navnet, i begge retninger |
| `?sorter=retning&orden=stigende` | Blandet, Ingen, Negativ, Positiv, og Ukjent sist |

</frozen-after-approval>

## Code Map

- `src/markedsoversikt.py`: `Sortering`, `sorter` og nøklene per kolonne.
- `src/app.py`: ruten `/` leser `sorter` og `orden` og sorterer hver del.
- `src/templates/index.html`: lenkene og vinklene i kolonneraden, linja over tabellen og stilen.
- `README.md`: statuslinja.

## Spec Change Log

## Review Triage Log

## Verification
