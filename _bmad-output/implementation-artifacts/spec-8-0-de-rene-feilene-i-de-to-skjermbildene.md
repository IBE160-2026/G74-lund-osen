---
title: 'Story 8.0: De rene feilene i de to skjermbildene'
type: 'bugfix'
created: '2026-09-30'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '348ce60a68a97856a647d50044129f4c73f27fc8'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-8-context.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Sidene viser tall med punktum og «-0,00», forklaringen kan vise «-1,2 % mot 1,2 %» ved en sjekk som ga -1, en aksje som skiller seg ut er merket bare med en nesten usynlig farge, lenkene ser ikke ut som lenker, fotnoten sier noe som ikke stemmer etter plan B, en feilmelding har «aa», og datoen over tabellen avhenger av sorteringen.

**Approach:** Én ren funksjon formaterer tallene etter regel 21 og brukes både som Jinja-filter og i forklaringen. Resten er små rettinger i malene, i `signalberegning.py` og i to docstringer, hver med en test og en mutant.

## Boundaries & Constraints

**Always:**
- `src/tallformat.py` er ren (ingen import, løvnode). `tall(verdi, slag)` bestemmer desimalene per slag: kurs 2, endring 2 med fortegn og hardt mellomrom foran %, måling minst 1, volum 0, akse 0. Medianvolumet får 1 desimal når det ikke er et heltall. Desimalkomma, U+00A0 som tusenskille og foran %, `-` som minus. Et tall som rundes til null, vises uten fortegn.
- `desimaler_mot_grense(maaling, grense)` gir færrest desimaler (minst 1, høyst 6) der avrundet |måling| og avrundet grense er ulike, med mindre de er nøyaktig like. Brukes for trend (mot nøytralsonen) og bevegelse (mot standardavviket), og av 2.1c senere.
- Tabellen i oversikten har nøyaktig fem kolonner (FR-101). Merket «skiller seg ut» står som tekst i Signalstyrke-cellen når styrken er 2 eller mer (FR-705).
- Kode, JSON og basen er urørt av formateringen (regel 21): bare det som vises, rundes.
- Ingen nett, og `src/fetch_prices.py` kjøres ikke (regel 6).

**Never:** Nytt design, omvisning eller andre farger (egen story etter skissen). Forholdstallet i interesse (2.1c). Historikken (2.7). KI (Epic 10).

## Beslutninger (godkjent 30.09 kl. 20:12)

- **Datoen over tabellen er den eldste datoen blant radene som vises**, samme prinsipp som tidsstempelet i FR-101 («Hvor gamle dataene er»). Tester: radene i to rekkefølger gir samme dato, og når én rad har eldre dato enn de andre, vises den eldre. En mutant som bruker den nyeste datoen skal fanges.
- **Fotnoten i `aksje.html`:** «Signalet bygger bare på kurs og volum. Børsmeldinger og kommende finansielle hendelser er ikke med i denne versjonen.» Docstringene i `app.py` og `aksjedetalj.py` sier grunnen: Euronext ga ikke tillatelse innen fristen, så plan B gjelder fra 28.09 (Epic 10 i `epics.md`), og KI-forklaringen kommer med Epic 10. Testen: fotnoten har ikke «under avklaring» og sier «kurs og volum».
- **Spinen:** `tallformat.py` i mappetreet og i grafen, med kantene `signal --> tallformat` og `app --> tallformat`.

## I/O & Edge-Case Matrix

| Scenario | Inn | Ut |
|---|---|---|
| Negativt | `tall(-1.5, "kurs")` | `-1,50` |
| Null | `tall(0, "kurs")` | `0,00` |
| Rundes til null | `tall(-0.004, "kurs")`, `tall(0.004, "endring")` | `0,00`, `0,00 %` |
| Over 1 000 | `tall(1234.5, "kurs")`, `tall(1234567, "volum")` | `1 234,50`, `1 234 567` (U+00A0) |
| Måling mot grense | dagens -1,214 %, standardavvik 1,212 % | `-1,214 % mot 1,212 % standardavvik` |
| Lik grensen | trend nøyaktig 2 % | `+2,0 %` |

</frozen-after-approval>

## Code Map

- `src/templates/index.html:28,30-31,54,70,73,77` -- farge, lenkestil, dato, merke, tallene
- `src/templates/aksje.html:24-25,74,99,161-164` -- tilbakelenken, sluttkurs, aksen, fotnoten
- `src/signalberegning.py:129,149,168,210` -- forklaringene og «for aa regne»
- `src/markedsoversikt.py` -- `sidens_tidsstempel` er mønsteret for en ny `sidens_dato(rader)`
- `src/app.py:24-25,59-62` -- filterregistrering, docstring
- `src/aksjedetalj.py:6-8` -- docstring
- `tests/test_konsumentene.py` -- `KJERNEMODULER` får `tallformat.py`
- Spinen: grafen (Invariants & Rules) og mappetreet (Structural Seed)

## Tasks & Acceptance

**Execution:**
- [ ] `src/tallformat.py`, `tests/test_tallformat.py` -- funksjonen og matrisen over
- [ ] `src/signalberegning.py` -- forklaringene gjennom `tall`, og «å regne»
- [ ] `src/markedsoversikt.py`, `src/app.py`, malene -- filteret, `sidens_dato`, merket, lenkene, fotnoten, docstringene
- [ ] `tests/test_app.py`, `tests/test_markedsoversikt.py` -- sidetestene
- [ ] Spinen -- grafen og mappetreet

**Acceptance Criteria:**
- Given en oversikt med styrke 2 og 1, when siden vises, then bare raden med 2 har teksten «skiller seg ut», og hver rad har fem celler
- Given sidene, when de vises, then ingen tallcelle har punktum som desimaltegn eller «-0,00»
- Given malenes stil, when `td.selskap a` og `a.tilbake` leses, then ingen har `text-decoration: none`, og begge har en `:focus-visible`-regel med `outline`

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest` -- expected: alt grønt, testtallet før og etter føres
- Hver mutant (tolv fra planen og mutanten med nyeste dato) legges inn én om gangen og settes tilbake fra en kopi; testene skal feile for hver
