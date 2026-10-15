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

## Commitene

Grenen `8-15-sortering`, PR #43: `370441c` spesifikasjonen med svarene, de daterte linjene i PRD-en, memloggen og designreglene, og 8-15 til in-progress; `1ba1cf0` `sorter`, `Sortering` og `neste_orden`; `8f82f84` lenkene i kolonneraden og sorteringen i ruten; `dd3f361` README-statusen; `9976ddc` lenken «Standard rekkefølge» i blekk, ikke nettleserens blå; `385bb6b` rettingene fra gjennomgangen; `c97c5fe` punktet i `deferred-work.md` (BH4).

## Spec Change Log

## Review Triage Log

Gjennomgang 15.10 på diffen `main...9976ddc`, med Blind Hunter (BH, 14 funn), Edge Case Hunter (ECH, 4) og Verification Gap (VG, 2). Rettingene står i `385bb6b` og `c97c5fe`. To funn må avgjøres av gruppen, så PR-en flettes ikke før det er avgjort.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH1 | Linja over tabellen sier «Sortert på retning, stigende», mens skjermleseren hører «alfabetisk, A til Å» i kolonneraden | medium | **avgjøres av gruppen**: svar 5 gir ordlyden «synkende» eller «stigende», og svar 2 sier «alfabetisk» for skjermleseren. En retting endrer teksten på siden |
| ECH2 | `aria-sort` sier at hele kolonnen er sortert, men sorteringen gjelder innenfor hver del, så verdiene begynner på nytt ved «Øvrige aksjer» | medium | **avgjøres av gruppen**: en retting endrer det skjermleseren hører, for eksempel «innenfor hver del» i den skjulte teksten, som planen viste uten det |
| VG1 | Ingen test så hvilken vei vinkelen peker | medium | patch: `test_vinkelen_peker_etter_retningen` |
| VG2 | Navnet i linja over tabellen var bare prøvd for signal og endring | low | patch: alle kolonnene i `test_linja_over_tabellen_bare_med_valg` |
| BH5 | Lenken var valgfri i regexen i `test_viser_selskapsnavn_og_de_fem_kolonnene` | low | patch: påkrevd ved de fire som kan sorteres |
| BH6 | Unntaket i fokustesten gjaldt alle velgere som inneholdt `a.sorter` | low | patch: bare akkurat regelen |
| BH7 | Den alfabetiske rekkefølgen var ikke prøvd mot teksten som vises | low | patch i testen. Teksten bygges av konstanten (`RETNINGSVISNING`), så de er like |
| BH8 | At lik verdi beholder FR-102 i begge retninger, hviler på at `sort` er stabil med `reverse=True` | low | patch: kommentar i `sorter` |
| BH9 | En `Sortering` laget direkte kunne ha en ukjent kolonne og gi KeyError i malen | low | patch: `__post_init__` med ValueError |
| BH14 | Ingen rutetest hadde en rad uten endring i «Skilte seg ut» | low | patch: `test_rad_uten_endring_sist_i_skilte_seg_ut` |
| ECH4 | Navnet ved lik verdi ble sortert på kodepunkt, med Å før Æ og store før små | low | patch: norsk alfabet uten forskjell på store og små |
| BH4 | Lenkene tar ikke med andre parametre i adressen, så perioden i 8.17 vil nullstilles ved et klikk | low | utsatt: `deferred-work.md` (`c97c5fe`). Oversikten har ingen andre parametre i dag |
| BH2 | Andre klikk på Retning gir Å til A, med Positiv først | avvist | svar 2 gir A til Å ved første klikk, og et nytt klikk snur (svar 1). S11 gjelder første klikk |
| BH3 | Vinkelen viser retningen et klikk gir når kolonnen ikke er valgt, og den som gjelder når den er valgt | avvist | svar 4 skiller dem med farge, og linja over tabellen og `aria-sort` sier hva som gjelder |
| BH10 | `aria-sort` og den skjulte teksten sier begge retningen | avvist | den skjulte teksten var med i planen, som gruppen godtok («Resten av planen gjelder som vist») |
| BH11 | `.skjult` er `position: absolute` uten posisjon | avvist | `.tabellboks` er `position: relative` (kommentaren i stilen), som for `.merke.skjult`, og bildet ved 390 px har ingen rulling på siden |
| BH12 | README-en sier «Flettet til main» på grenen | avvist | statusen endres i PR-en som fletter saken, som svar 26 i 8.0d |
| BH13 | Linja i memloggen har «på» | avvist | memloggen hadde norske bokstaver fra før, i 7 linjer på main |
| ECH3 | Lik vist verdi kan ha ulik full presisjon | avvist | tall lagres og sammenlignes med full presisjon, og avrunding skjer bare der tallet vises (regel 21) |

## Verification

**Commands:**
- `uv run pytest -q` -- før 1569 bestått og 16 hoppet over på main (`73cdc45`). Før PR-en 1603 og 16 på `9976ddc`. Etter rettingene 1607 og 16 på `c97c5fe`.

**Mutantene** (15.10, på `dd3f361`), kjørt én om gangen med `-x` og bare testfilene som skulle fange dem, med kopi før og sha256 mot HEAD etter hver. Fila var lik HEAD etter hver (sha256 uten CRLF, og ingen endring i `git status`). Alle 13 er fanget.

| # | Mutant | Fanget av |
|---|---|---|
| S1 | sortering over hele tabellen, ikke per del | `tests/test_app.py::TestStory815Sortering::test_hver_del_sorteres_for_seg` |
| S2 | rader uten verdi først når rekkefølgen snus | `tests/test_markedsoversikt.py::TestSorteringVedKlikk::test_kolonnen_og_retningen` |
| S3 | endring sortert på kroner | `tests/test_markedsoversikt.py::TestSorteringVedKlikk::test_kolonnen_og_retningen` |
| S4 | endring sortert på absoluttverdi | `tests/test_markedsoversikt.py::TestSorteringVedKlikk::test_kolonnen_og_retningen` |
| S5 | lenken snur ikke | `tests/test_app.py::TestStory815Sortering::test_lenken_snur_og_aria_sort_staar_paa_kolonnen` |
| S6 | `aria-sort` på feil kolonne | `tests/test_app.py::TestStory815Sortering::test_lenken_snur_og_aria_sort_staar_paa_kolonnen` |
| S7 | ukjent retning i adressen gir en sortering | `tests/test_app.py::TestStory815Sortering::test_uten_klikk_er_rekkefoelgen_fr_102` |
| S8 | vinkelen som tegnet ↑ eller ↓ | `tests/test_utseende.py::TestSorteringen::test_vinkelen_er_en_svg_dempet_eller_hvit` |
| S9 | fokus i blekk | `tests/test_utseende.py::TestSorteringen::test_fokus_er_oransje_paa_blekk_og_klikkflaten_44_px` |
| S10 | uten FR-102 ved lik verdi | `tests/test_markedsoversikt.py::TestSorteringVedKlikk::test_kolonnen_og_retningen` |
| S11 | Retning sortert med Positiv først | `tests/test_markedsoversikt.py::TestSorteringVedKlikk::test_kolonnen_og_retningen` |
| S12 | linja over tabellen også uten valg | `tests/test_app.py::TestStory815Sortering::test_linja_over_tabellen_bare_med_valg` |
| S13 | den dempede vinkelen er hvit | `tests/test_utseende.py::TestSorteringen::test_vinkelen_er_en_svg_dempet_eller_hvit` |

Testene fra gjennomgangen ble prøvd på samme måte på `385bb6b`, og alle fem ble fanget: vinkelen med retningen et klikk gir også på den valgte kolonnen (`test_vinkelen_peker_etter_retningen`), «kurs» som navn i linja (`test_linja_over_tabellen_bare_med_valg`), navnet uten norsk alfabet (`test_navnet_ved_lik_verdi_i_norsk_alfabet`), `Sortering` uten kontroll (`test_sortering_laget_direkte_maa_vaere_kjent`) og rader uten verdi først i stigende (`test_hver_del_sorteres_for_seg`).

Bildene av oversikten i demoen ved 1280 og 390 px, med og uten valgt kolonne (`?sorter=endring&orden=synkende`), ligger bare i scratchpad. Ved 390 px er de tatt i en ramme på 390 px, fordi Edge uten vindu har en minste bredde over 390 px.
