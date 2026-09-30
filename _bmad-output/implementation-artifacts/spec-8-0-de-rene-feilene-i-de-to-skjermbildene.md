---
title: 'Story 8.0: De rene feilene i de to skjermbildene'
type: 'bugfix'
created: '2026-09-30'
status: 'done'
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
- [x] `src/tallformat.py`, `tests/test_tallformat.py` -- funksjonen og matrisen over
- [x] `src/signalberegning.py` -- forklaringene gjennom `tall`, og «å regne»
- [x] `src/markedsoversikt.py`, `src/app.py`, malene -- filteret, `sidens_dato`, merket, lenkene, fotnoten, docstringene
- [x] `tests/test_app.py`, `tests/test_markedsoversikt.py` -- sidetestene
- [ ] Spinen -- grafen og mappetreet

**Acceptance Criteria:**
- Given en oversikt med styrke 2 og 1, when siden vises, then bare raden med 2 har teksten «skiller seg ut», og hver rad har fem celler
- Given sidene, when de vises, then ingen tallcelle har punktum som desimaltegn eller «-0,00»
- Given malenes stil, when `td.selskap a` og `a.tilbake` leses, then ingen har `text-decoration: none`, og begge har en `:focus-visible`-regel med `outline`

## Implementation Notes

- Bygget direkte i denne økta, ikke av en egen implementasjonsagent. Gjennomgangen gjøres av tre agenter uten kontekst.
- `tallformat.tall(verdi, slag, desimaler=None, fortegn=None)`. `fortegn=False` brukes for standardavviket, som ikke har retning. `desimaler_mot_grense` gir `minst` når tallene er like også med seks desimaler: da er forskjellen støy fra flyttallene.
- Forklaringen ligger i tre hjelpere i `signalberegning.py`: `_trendforklaring`, `_bevegelsesforklaring` og `_interesseforklaring`. Testene kaller dem direkte, fordi en serie som treffer 1,214 mot 1,212 er vanskelig å lage.
- `markedsoversikt.sidens_dato(rader)` gir den eldste datoen. `app.py` sender den til malen som `dato`.
- Merket er `<span class="merke">skiller seg ut</span>` i Signalstyrke-cellen, med `display: block`. Fargen på `tr.utslag` står.
- Lenkene er alltid understreket og har `:focus-visible` med `outline`. `a.tilbake` har `color: inherit` i stedet for den dempede fargen.
- `tallformat.py` står i `KJERNEMODULER` i `test_konsumentene.py`, og en egen test holder den som løvnode. Spinen har modulen i grafen, kantene `app --> tallformat` og `signal --> tallformat`, og mappetreet.
- To eksisterende tester så etter punktum (`101.00` og `123.45`) og er rettet til komma.
- `tallformat.py` og to testfiler hadde det harde mellomrommet som et usynlig tegn i kilden. Nå står det som `"\u00a0"`, i `7e7aa54`.
- Mutantene (14): de tolv fra planen, nyeste dato (13) og tilbakelenken uten understrek (14). Hver ble lagt inn én om gangen og satt tilbake fra en kopi, og alle ble fanget. Mutant 2 ble først ikke lagt inn, fordi kilden hadde et literalt hardt mellomrom. Den ble kjørt på nytt etter `7e7aa54` og ble fanget.
- Testene: før 928 passed og 16 skipped lokalt, og 944 passed i CI på main (kjøring 36744235389). Etter: 973 passed og 16 skipped lokalt.

## Spec Change Log

## Review Triage Log

Gjennomgang 1, 30.09, av diffen fra `348ce60` til `4975f21`, med Blind Hunter (BH), Edge Case Hunter (ECH) og Verification Gap (VG). 17 funn: 8 rettet, 1 utsatt og 8 avvist.

| # | Kilde | Funn | Verdikt | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | VG | Ingen test ser `_interesseforklaring` gjennom `interesse()` og `beregn_signal`. Tilbakeført f-streng ville overlevd | medium | Stemmer. Volumene var 1 000, og den gamle formen gir «1000», uten punktum | patch: `test_interesse_gjennom_beregn_signal`, mutant 17 fanget |
| 2 | VG | Aksen i grafen testes ikke i siden | medium | Stemmer. `"%.0f"` gir aldri punktum, så sjekken fanget ikke en tilbakeføring | patch: aksen i `test_tallene_i_detaljen_er_norske`, mutant 16 fanget |
| 3 | ECH | `desimaler_mot_grense` faller tilbake til `minst` når tallene er like med seks desimaler, også når sjekken slo ut (trend) | low | Stemmer bare når avviket ligger under 5e-9 fra sonen, altså ved støy fra flyttallene. Med ekte kurser forekommer det nesten aldri, og rettingen krever at sjekkens utfall sendes inn | avvist: lav, og rettingen legger til en parameter |
| 4 | ECH | Samme for bevegelse | low | Samme grunn som 3 | avvist |
| 5 | ECH | Grensen sammenlignes skalert med 100, mens sjekken er uskalert | low | Skaleringen kan bare flytte likhet på støynivå, samme tilfelle som 3 | avvist |
| 6 | ECH | Endringen farges opp eller ned når teksten viser «0,00 %» | medium | Stemmer: +0,003 % fikk klassen `opp`. Farge og tekst sa hver sin ting (FR-103) | patch: fargen følger `round(2)`, `test_endring_som_vises_som_null_har_ingen_farge`, mutant 15 fanget |
| 7 | ECH | Negativt eller ikke-heltallig `desimaler` gir en uklar feil | false | Ingen kaller sender det. Malene bruker slagets tall, og `desimaler_mot_grense` gir 1–6 | avvist |
| 8 | BH | Spinen sier fortsatt «importerer bare `kursdata`» over den nye merknaden | low | Stemmer | patch: rettet på stedet med *Rettet 2026-09-30* |
| 9 | BH | `tallformat.py` mangler i lista over løvnoder i spinen | low | Stemmer | patch: lagt til i lista (samme retting som 8) |
| 10 | BH | Fotnoten nevner ikke lenger KI-forklaringen | false | Teksten er gruppens eget valg 30.09 kl. 20:12, og den stemmer også etter Epic 10. Docstringene nevner Epic 10 | avvist: avgjort av gruppen |
| 11 | BH | Løkkene over regnestykket og tabellradene kan passere uten å sjekke noe | low | Stemmer | patch: `len(...) == 3` og `len(tabell.rader) == 2` |
| 12 | BH | `test_desimaler_kan_overstyres` godtar to svar, og `startswith("-1,2")` er svak | low | Stemmer. Rettelsen fra byggingen ble ikke lagt inn, fordi shellet endret teksten den skulle erstatte | patch: nøyaktige strenger med 1.2346 og -1.236 |
| 13 | BH | Datotesten lover i docstringen mer enn den sjekker | low | Stemmer | patch: docstringen og en kommentar om hvor datoene kommer fra |
| 14 | BH | `tall()` har ingen oppførsel for NaN og uendelig | low | Ingen vei inn er vist: kursene kommer gjennom oversetteren, `endring` er None uten forrige dag, og medianvolumet er beskyttet med `> 0`. Hvis NaN likevel kom inn, ville «nan» stått på siden | avvist: ingen vei vist |
| 15 | BH | Aksen med 0 desimaler viser like tall ved et smalt kursspenn | low | Stemmer, men oppførselen er fra før 8.0 (`"%.0f"`) | utsatt til `deferred-work.md` |
| 16 | BH | Merket testes bare den ene veien | low | Stemmer for en rad uten signal | patch: `test_rad_uten_signal_er_ikke_merket` |
| 17 | BH | Blandet skrivemåte av «å» i testnavn, og andre tekster med «aa» | false | ASCII i kode og kommentarer er prosjektets skikk. Søket etter «aa» i strenger brukeren ser, fant bare `signalberegning.py:210` (planen) | avvist |

Etter rettingene: 976 passed og 16 skipped lokalt, og mutant 15–17 ble fanget.

## Verification

**Commands:**
- `uv run pytest` -- expected: alt grønt, testtallet før og etter føres
- Hver mutant (tolv fra planen og mutanten med nyeste dato) legges inn én om gangen og settes tilbake fra en kopi; testene skal feile for hver
