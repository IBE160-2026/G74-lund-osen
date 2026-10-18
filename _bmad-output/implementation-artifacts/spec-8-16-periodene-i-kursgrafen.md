---
title: 'Story 8.16: regelen for startdagen, og periodene i kursgrafen'
type: 'feature'
created: '2026-10-18'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'efa3224'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
---

## Intent

**Problem:** Kursgrafen på aksjesiden har fast 6 måneder, regnet som 182 kalenderdager (`GRAFVINDU_DAGER`). FR-201 er rettet 08.10: grafen skal ha periodevalget i `designregler.md` §2, med de samme knappene som oversikten får i 8.17, og startdagen skal følge én skriftlig regel.

**Grunnlaget:** kontrollpunktene under story 8.16 i `epics.md`, FR-201 med tillegget 08.10, `designregler.md` §2, gruppens svar 18.10 kl. 21:46, 21:49 og 21:50 (alle åtte knappene; siste børsdag og «Velg dag» viser 6 mnd fram til dagen, med dagen merket, endringen den dagen og signalet som er lagret for den), og instruksjonen 18.10 kl. 22:54.

## Kontrollpunktene

- a) Regelen før koden: §2 i `designregler.md` får regelen for startdagen. 1 uke, 1, 3 og 6 mnd og 1 år regnes bakover fra siste dag i grafen etter kalenderen, og en dato måneden ikke har, blir månedens siste dag. Startdagen er første børsdag på eller etter den datoen. I år starter på årets første børsdag. Én funksjon i en ren modul gir startdagen for hver periode, med tester på faste datoer rundt helger, helligdager og nyttår.
- b) Grafen: knappene i én delmal som 8.17 skal bruke, i rekkefølgen og med navnene i §2, valgt knapp med `aria-current` og synlig fokus. Perioden står i adressen, og grafen åpner med 6 mnd. Kurslinja, MA50 og indekslinja følger perioden, og overskriften og merkene på aksen passer den. MA50 finnes fra første punkt for 6 mnd og kortere, og 1 år viser bare det serien har, og sier det. «Velg dag» er et datofelt i et skjema, uten skript fra nettet, og dagen står på knappen. Signalet for dagen er det som er lagret, ellers «– ikke vurdert», grunnen eller «– ikke børsdag», og det regnes aldri på nytt (AD-7). En feil i adressen gir 6 mnd og en kort beskjed, aldri en feilside. På 390 px bryter knappene linja, og siden ruller ikke sidelengs.
- c) Tekstene (regel 19): hjelpen til grafen, «Status» i README-en og `docs/hjelp.md` der grafen nevnes. Endres en fil bak bildet av oversikten, tas bildet på nytt slik feilmeldingen i testen sier.
- d) Testene, med «Ville feilet hvis»: to perioder som regner startdagen med hver sin regel; knappene og rekkefølgen; 6 mnd når siden åpnes; punktene fra startdagen for hver periode; indekslinja følger perioden; 1 år med kortere serie sier det; «Velg dag» for en dag uten vurdering viser «– ikke vurdert»; feil i adressen (ukjent periode, en dato fram i tid, tekst) gir 6 mnd og ingen feilside; 390 px. Mutanter én om gangen med `-x` og kopi før og sha256 mot HEAD etter: 1 mnd som 30 dager, «Velg dag» som regner signalet, indekslinja fast på 6 mnd, og en ukjent periode som gir en feil.

## Planen, én commit per punkt

1. a) Regelen i `designregler.md` §2, og `src/perioder.py` med `startdag()` og testene i `tests/test_perioder.py`.
2. b) Delmalen `_perioder.html`, adressen og valget i `perioder.py`, punktene fra startdagen i `aksjedetalj.py`, merkene på aksen og den merkede dagen i `graf.py`, lesingen av en lagret vurdering for en dag i porten `Oversiktsleser`, ruten og `aksje.html`.
3. c) Hjelpen til grafen, «Status» i README-en og `docs/hjelp.md`, og bildet av oversikten tatt på nytt, fordi den nye delmalen er en fil bak bildet.
4. d) Testene for grafen og siden.

## Avgjort i spesifikasjonen

- **Adressen:** `?periode=` med kodene `siste`, `1-uke`, `1-mnd`, `3-mnd`, `6-mnd`, `i-aar`, `1-aar` og `velg`, og `&dag=ÅÅÅÅ-MM-DD` for «Velg dag». En `dag` uten `periode` leses som «Velg dag».
- **Utenfor børskalenderen:** `boersdag.DEKKEDE_AAR` er bare 2026, så 1 år fra oktober 2026 havner i 2025. Der er startdagen første hverdag på eller etter datoen, og I år starter på første hverdag etter 1. januar. Grafen starter uansett på første dag serien har fra startdagen, og serien har bare børsdager.
- **«Velg dag»:** vurderingen leses med en ny lesemetode på porten `Oversiktsleser` (`vurdering(symbol, dato)`), som bare leser. Tilstanden og teksten kommer fra `les_tilstand`, som i oversikten. Signalet regnes aldri.
- **Merkene på aksen:** 1 uke har dagene, 1 mnd mandagene (første børsdag i hver uke), 3 og 6 mnd, I år, siste børsdag og «Velg dag» månedene, og 1 år månedene med navn på annenhver, så navnene får plass.

## Boundaries

- Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Bildet tas fra en demobase i en midlertidig mappe.
- Ingen skript fra nettet. 8.17 bygges ikke her, men delmalen skal kunne brukes der.
