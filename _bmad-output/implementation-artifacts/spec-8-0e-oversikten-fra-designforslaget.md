---
title: 'Story 8.0e: Oversikten fra designforslaget'
type: 'feature'
created: '2026-10-13'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '4c4b420f3ef2bd6ef07d1ae24d301632d721544c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-0c-tydelig-merking-ord-ved-sjekkene-og-datoer-paa-grafen.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Oversikten viser bare «N av 3» og ikke hvilke sjekker som slo ut, og aksjene som skilte seg ut, står i samme liste som resten (story 8.0e i `epics.md`, endringsforslaget 13.10, punkt 4.6).

**Approach:** To pull requests. PR 1 (grenen `8-0e`) tar tabellen: T, B og I under «N av 3», de to delene «Skilte seg ut» og «Øvrige aksjer», og pillen «3 av 3» med svart fyll. PR 2 tar teksten over tabellen: overskriften med ukedagen, innledningen, linja om «3 av 3», «Slik leser du tabellen», «Demo Børs» og README-statusen.

## Planen

Planen ble vist i chatten 13.10 og er ført kort i `docs/ai-prompts/2026-10-13.md` (Utført-linja for instruksjonen kl. 20:34). Svarene kl. 21:10 (1–7) og kl. 21:27 (8) er beslutninger:

1. **Demoen sier «Demo Børs»** der den ekte versjonen sier «Oslo Børs»: i innledningen og i linja over tabellen («Demo Børs · 09.10 · 14 aksjer»). Det endrer beslutning 3 i 8.0c. Merket «Demoversjon. Eksempeltall: …» står som før, og grensene i hjelpen sier fortsatt «15 aksjer på Oslo Børs» (beslutning 5 i 8.0c). PR 2.
2. **Første punkt i «Slik leser du tabellen»:** «T, B og I er trend, bevegelse og interesse, og hver gir +1, 0 eller -1. Øverst i cellen står hvor mange som slo ut, fra 0 av 3 til 3 av 3.» PR 2.
3. **Når ingen skiller seg ut:** overskriften er «0 av M aksjer skilte seg ut <ukedag>», setningen «Hos …» står ikke, og setningen fra 8.0c står der «Skilte seg ut» ellers står. Uten en eneste vurdering står ingen overskrift. Setningene i PR 1, overskriften i PR 2.
4. **Når N er 1:** «Hos 1 aksje slo minst 2 av 3 ut.» Ellers tavlas ordlyd. PR 2.
5. **Ukedagen** gjelder samme dato som linja over tabellen, altså den eldste (story 8.0). PR 2.
6. **To pull requests:** først tabellen, så teksten over tabellen.
7. **Demoen har samme logo og utseende** som den ekte versjonen, nå og når 8.0d kommer. Bare merket øverst og «Demo Børs» skiller dem (FR-411).
8. **Pillen «3 av 3»** får svart fyll og hvit tekst inne i den gule ringen (`#a67c00`), som i designforslaget. 2 av 3 merkes som i dag, med fet skrift og strek, uten fyll og uten gult. PR 1, med en test for kontrasten, og `designregler.md` §3 får en datert linje.

## PR 2: teksten over tabellen

Instruksjonen kl. 23:43 13.10 (grenen `8-0e-tekst`, fra main etter `85fe8a4`). Svarene 1–5 over er beslutningene, med disse i tillegg:

- **Overskriften** «N av M aksjer skilte seg ut <ukedag>», med «N av M aksjer» i fet skrift. N og M telles fra radene, og ukedagen er datoen i linja over tabellen (svar 3 og 5). Den gule understreken fra tavla tas ikke med: det viktigste merkes med fet skrift (`designregler.md` §4, rettet 13.10), og gult betyr bare 3 av 3 (beslutningen kl. 23:43).
- **Innledningen** med ordlyden i `epics.md`, tallene fra radene, `Parametre` og `antall_sjekker`, «Hos 1 aksje» når N er 1, og ingen setning «Hos …» når N er 0 (svar 3 og 4).
- **Linja om «3 av 3»:** «Bare <navn> fikk utslag på alle 3 sjekkene.», med navnene fra radene bundet med «og». Har ingen 3 av 3, står ikke linja.
- **«Slik leser du tabellen»** med 3 punkter: «Signalstyrke 0–3» med ordlyden i svar 2, og tavlas tekster om retning og selskapsnavnet fra endringsforslaget 13.10, punkt 4.2 («Kan tas som de står»). Ingen setning om klikk på T, B eller I.
- **«Demo Børs»** i innledningen og linja over tabellen i demoen (svar 1). Ingen tekst bak «?» endres.
- **README-en:** statuslinja ordrett fra instruksjonen, steg 2 får setningen fra «Jeg har fått koden fra før» i `docs/hjelp.md`, og steg 4 får «Har mappa et annet navn, drar du den mappa der README og compose ligger.» `docs/kvalitetssikring.md` §9 rettes i samme commit, med en datert linje om at Prøve 1 og 2 tas etter at 8.0d er flettet (beslutningen kl. 23:40), og at prøven før innleveringen bruker ZIP-fila som faktisk leveres (kl. 23:22).
- **Ordene i et steg i README-en** telles slik leseren ser dem, med lenketeksten og uten adressen bak, og grensen er 65, ikke 60 (svaret i chatten kl. 23:50, ført i dagsfila på main i `bb56d61`). Setningen fra `docs/hjelp.md` gjorde steg 2 til 70 ord, 8 av dem i adressen til GitHub.
- **Mutantene:** M skrevet fast som 15; ukedagen fra dagen siden åpnes; feil indeks i lista over ukedager; linja med «3 av 3» uten 3 av 3; «Oslo Børs» i innledningen i demoen; «Hos 1 aksjer»; setningen om klikk i første punkt; setningen borte fra steg 2 i README-en.

## Boundaries & Constraints

**Always:**
- Tabellen har fortsatt fem kolonner (FR-101).
- T, B og I leses fra den lagrede vurderingen, aldri regnet på nytt (FR-101, AD-7).
- Delingen bruker terskelen fra `Parametre` (FR-705), og hver del er sortert etter FR-102.
- Det nye vises også med demobasen, og en test krever det (FR-411).
- Grenen bruker bare testbaser (regel 22). Ingen API-kall, ingen nettkall i tester (AD-8).
- Tall vises med vanlig bindestrek som minus (regel 21), og formen bestemmes ett sted.

**Never:**
- Ingen sjette kolonne og ingen endring i signalberegningen, hentingen eller basen.
- README-en endres ikke i PR 1.
- Ingen tekst bak «?» endres i PR 1.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Noen over terskelen | Rader med 3, 2, 1 og 0 | «Skilte seg ut» med 3 og 2, så «Øvrige aksjer» med 1, 0 og radene uten vurdering, hver del i FR-102-rekkefølge | N/A |
| Ingen over terskelen | Alle vurderte har 0 eller 1 | Setningene fra 8.0c i stedet for «Skilte seg ut», så «Øvrige aksjer» | N/A |
| Ingen vurdering | Ingen rad har vurdering | Én del uten overskrift, ingen setning | N/A |
| Alle over terskelen | Alle har 2 eller 3 | Bare «Skilte seg ut» | N/A |
| Rad uten vurdering | Grunn eller ingen rad | «–» og grunnen, uten T, B og I | N/A |
| Lagret mot kursene | Vurderingen sier T +1, kursene ville gitt 0 | «T +1» | N/A |

</frozen-after-approval>

## Code Map

- `src/markedsoversikt.py` -- `Rad` (vurdering, styrke, skiller_seg_ut med `>= p.terskel` i `bygg_rad`), `bygg_oversikt` (FR-102), `ingen_skilte_seg_ut`, `antall_vurdert`. Ny: `Rad.sjekker` og `del_i_to`.
- `src/tallformat.py` -- formen på tall (regel 21). Ny: `fortegn(verdi)` gir «+1», «0», «-1».
- `src/aksjedetalj.py:66` -- `SjekkVisning.fortegn`, samme form. Bruker `fortegn()`.
- `src/vurderingsdata.py` -- `Vurdering.trend`, `bevegelse`, `interesse`. Endres ikke.
- `src/app.py` -- ruta for `/`: gir `rader`, `ingen_skilte_seg_ut`, `antall_vurdert`, `parametre`, `antall_sjekker` til malen. Får de to delene.
- `src/templates/index.html` -- tabellen, `.pille.tre-av-tre`, setningene fra 8.0c.
- `tests/test_app.py` -- `_Tabell` (leser `tbody`), `test_fortsatt_fem_kolonner`, `TestStory80c`, kontrasttesten for ringen.
- `tests/test_demo.py` -- `TestStory80cIDemoen`, fixturen `demobase` (kopi i tmp).
- `_bmad-output/planning-artifacts/designregler.md` §3 -- datert linje om fyllet.

## Tasks & Acceptance

**Execution:**
- [x] `src/tallformat.py`, `src/aksjedetalj.py` -- `fortegn()` og bruk den i `SjekkVisning` -- én form for fortegnet
- [x] `src/markedsoversikt.py` -- `Rad.sjekker` (T, B, I fra vurderingen, tom uten vurdering) og `del_i_to(rader)` (skiller seg ut / øvrige, rekkefølgen beholdt) -- logikken uten HTML
- [x] `src/app.py`, `src/templates/index.html` -- to `tbody` med en overskriftsrad hver, setningene fra 8.0c i første del når ingen skilte seg ut, T, B og I under pillen, svart fyll på «3 av 3» -- tabellen
- [x] `tests/test_app.py`, `tests/test_markedsoversikt.py`, `tests/test_tallformat.py`, `tests/test_demo.py` -- testene for matrisen og mutantene
- [x] `designregler.md` §3 -- datert linje

**Acceptance Criteria:**
- Given en rad med vurdering, when oversikten vises, then cellen har «N av 3» og under den «T +1», «B 0» og «I -1» fra vurderingen.
- Given demobasen, when oversikten vises, then T, B og I, de to delene og pillen med fyll står der.
- Given «3 av 3», when oversikten vises, then pillen har svart fyll, hvit tekst og gul ring, og kontrasten er minst 4,5:1.

## Implementation Notes

- *PR 1, 13.10:* `e5060f3` tabellen og testene, `4ad1013` den daterte linja i `designregler.md` §3, `877cd01` rettingene fra gjennomgangen. Bygget direkte i økta, ikke av en egen agent.
- `fortegn()` i `tallformat.py` gir formen for både T, B og I og Ga på aksjesiden (regel 21). `Rad.sjekker` leser `trend`, `bevegelse` og `interesse` fra `Rad.vurdering` og er tom uten vurdering. `del_i_to` deler etter `skiller_seg_ut` og beholder rekkefølgen fra `bygg_oversikt`.
- Radene står i makroen `tabellrad` i `index.html`, så de to delene bruker samme rad. Setningene fra 8.0c er flyttet fra over tabellen til en rad `<tr class="del">` i første `tbody`.
- `_Tabell` i `test_app.py` legger overskriftsradene i `deler` og ikke i `rader`, og `del_av` sier hvilken del hver rad står under. Fire tester som sammenlignet hele cellen med styrken, krever nå også T, B og I.
- Demobasen har både «Skilte seg ut» og «Øvrige aksjer», og minst én rad med 3 av 3.
- Epic 8-konteksten er ikke laget på nytt: den eneste endringen i planleggingsmappa etter den, er linja om at 8.0c er ferdig (`3ad2922`).
- *PR 2, 13.–14.10 (grenen `8-0e-tekst`):* `b6468af` PR 2 i spesifikasjonen, `72e5210` teksten over tabellen og testene, `c235631` README-en, `kvalitetssikring.md` §9 og testene for dem, `a4a93bb` rettingene fra gjennomgangen og `bb81b7b` den daterte linja om README-prøven i `epics.md`. `ukedag()` og `med_og()` står i `tallformat.py`. Overskriften står bare når minst én rad har en vurdering. Innledningen og «Slik leser du tabellen» står uansett. Tavlas tekster om retning og selskapsnavnet er tatt fra endringsforslaget 13.10, punkt 4.2.
- Pillen «3 av 3» står også i linja over tabellen, så testen for ringen i 8.0c ser nå bare i tabellen.

## Spec Change Log

## Review Triage Log

Gjennomgang av PR 1 (diffen `4c4b420...4ad1013`, 13.10), med Blind Hunter (BH, 12 funn), Edge Case Hunter (ECH, 1) og Verification Gap (VG, 1) som tre uavhengige agenter. Rettingene står i `877cd01`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| VG1 | Navnene i `<abbr title>` ved T, B og I er ikke prøvd i siden | low | patch: test på de tre `<abbr>` |
| BH1 | Kontrasttesten leser ikke tekstfargen | medium | patch: fargen leses fra regelen |
| BH2 | Den gule ringen står nå mot svart, og ingen test prøver det | low | patch: ringen mot fyllet minst 3:1 |
| BH4 | Navnet står to ganger i `SJEKKBOKSTAVER` | low | patch: feltnavnet er navnet |
| BH5, ECH1 | Demotesten krever ikke pillen med fyll i HTML-en | medium | patch |
| BH11 | Setningen fra 05.10 alene er ikke prøvd i tabellen | low | patch |
| BH12 | Importen i `aksjedetalj.py` står ikke i rekkefølge | low | patch |
| BH3 | T, B og I forklares ikke på siden før PR 2 | avvist | svar 6 legger teksten over tabellen i PR 2, og `<abbr>` har navnet til da |
| BH6 | Malen stoler på at `del_i_to` og `ingen_skilte_seg_ut` er enige | false | begge leser `skiller_seg_ut`: er `skilte_seg_ut` ikke tom, gir `ingen_skilte_seg_ut` False |
| BH7 | Spesifikasjonen mangler notater, testtall og avkryssing | avvist | rettingen er å skrive i spesifikasjonen, som gjøres her |
| BH8 | Fyllet har ingen mørk modus | avvist | sidene har ingen mørk modus i dag, og utseendet hører til 8.0d |
| BH9 | Demotesten importerer hjelpere fra `test_app` | low, avvist | samme mønster som importen fra `test_hjelpetekster` i 8.0c |
| BH10 | CSS-testene ser etter eksakt tekst | low, avvist | samme form som testene for ringen og streken i 8.0c |

Gjennomgang av PR 2 (diffen `main...8-0e-tekst` på `c235631`, 13.10), med Blind Hunter (BH, 9 funn), Edge Case Hunter (ECH, 3) og Verification Gap (VG, ingen hull). Rettingene står i `a4a93bb` og `bb81b7b`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH3 | Pillen i 8.0c-testen kunne finnes i linja over tabellen | low | patch: sjekket i tabellen |
| BH4 | Setningen fra 8.0c er ikke prøvd ved N lik 0 | low | patch |
| ECH3 | Linja om «3 av 3» tok navnene bare fra «Skilte seg ut» | low | patch: fra alle radene, med test for terskel over 3 |
| BH5 | `epics.md` sier fortsatt «README-prøven 13.–16.10 gjenstår» | low | patch: datert linje under 3.4 |
| BH1 | Grensen på 65 ord viser til et svar som ikke er ført | false | svaret er ført i dagsfila på main i `bb56d61`. Det står nå også i PR 2-delen av spesifikasjonen |
| BH2, ECH1 | Ukedagen kommer fra den eldste datoen, også fra rader uten vurdering | avvist | svar 5: samme dato som linja over tabellen, altså den eldste |
| ECH2 | M teller også rader uten vurdering | avvist | `epics.md` og svar 3: N og M telles fra radene, og «N av M aksjer ble vurdert.» står når noen mangler |
| BH6 | Innledningen og «Slik leser du tabellen» står uten en eneste vurdering | avvist | svar 3 tar bare bort overskriften, og innledningen er sann uten vurderinger |
| BH7 | Setningen i steg 2 står etter sjekken og sier «pakker ut» også om en mappe | avvist | instruksjonen: ordrett fra `docs/hjelp.md`, til slutt i steget |
| BH8 | Demotesten krever en aksje på 3 av 3 i demobasen | avvist | demobasen er laget av faste tall, og testen fra PR 1 krever det samme |
| BH9 | «Eksempeltall» og «Demo Børs» er ikke prøvd sammen i demoen | false | `test_bryteren_med_demobase_viser_eksempeltall` krever merket og «Demo Børs · 09.10 · 14 aksjer» på samme side |

## Design Notes

Overskriften for hver del er en rad `<tr class="del"><th colspan="5" scope="rowgroup">` først i sin `tbody`, så tabellen har fortsatt fem kolonner. Setningene fra 8.0c står i en rad `<tr class="del">` med én celle over fem kolonner. Er det ingen første del (ingen vurdering), står radene i én `tbody` uten overskrift.

```html
<td class="tall styrke">
  <span class="pille tre-av-tre">3 av 3</span>
  <span class="sjekker"><span>T +1</span> <span>B +1</span> <span>I +1</span></span>
  <span class="merke">skiller seg ut</span>
</td>
```

## Verification

**Commands:**
- `uv run pytest -q` -- expected: grønn. Før: 1461 bestått og 16 hoppet over på main (`3ad2922`, 13.10 kl. 22:32).

**Etter:** 1478 bestått og 16 hoppet over på `877cd01` (1477 og 16 før rettingene).

**Mutantene** (13.10, på `4ad1013`) ble kjørt én om gangen mot hele testsettet med `-x`, og fila settes tilbake og kontrolleres med sha256: T, B og I regnet av kursene; en sjette kolonne; T, B og I på en rad uten vurdering; `>=` blir `>` i delingen; terskelen skrevet fast; «Skilte seg ut» sammen med setningen fra 8.0c; sorteringen snudd i én del; «3 av 3» uten svart fyll. Alle 8 ble fanget:

| # | Mutant | Fanget av |
|---|---|---|
| M1 | T, B og I regnet av kursene (B fra endringen) | `tests/test_app.py::TestStory80e::test_t_b_og_i_staar_under_n_av_3_fra_vurderingen` |
| M2 | en sjette kolonne | `tests/test_app.py::TestTidsstempler::test_fortsatt_fem_kolonner` |
| M3 | T, B og I på en rad uten vurdering | `tests/test_app.py::TestVurderingenPaaOversikten::test_ikke_vurdert_med_fotnoten` |
| M4 | `>=` blir `>` i delingen | `tests/test_app.py::TestStory80::test_aksjen_som_skiller_seg_ut_er_merket_med_tekst` |
| M5 | terskelen skrevet fast | `tests/test_app.py::TestStory80c::test_terskelen_i_setningen_kommer_fra_parametre` |
| M6 | «Skilte seg ut» sammen med setningen fra 8.0c | `tests/test_app.py::TestStory80e::test_setningene_fra_8_0c_der_skilte_seg_ut_ellers_staar` |
| M7 | sorteringen snudd i én del | `tests/test_app.py::TestStory80e::test_to_deler_hver_sortert_etter_fr_102` |
| M8 | «3 av 3» uten svart fyll | `tests/test_app.py::TestStory80e::test_tre_av_tre_har_svart_fyll_og_hvit_tekst` |

**PR 2:** før 1478 bestått og 16 hoppet over på main (`63ac793`), etter 1491 og 16 på `a4a93bb`. Mutantene for PR 2 (13.10, på `c235631`), kjørt på samme måte. Alle 8 ble fanget:

| # | Mutant | Fanget av |
|---|---|---|
| P1 | M skrevet fast som 15 | `tests/test_app.py::TestStory80eTekst::test_overskriften_teller_fra_radene` |
| P2 | ukedagen fra dagen siden åpnes | `tests/test_app.py::TestStory80eTekst::test_overskriften_teller_fra_radene` |
| P3 | feil indeks i lista over ukedager | `tests/test_app.py::TestStory80eTekst::test_overskriften_teller_fra_radene` |
| P4 | linja med «3 av 3» uten 3 av 3 | `tests/test_app.py::TestStory80eTekst::test_linja_om_3_av_3_med_navnene_fra_radene` |
| P5 | «Oslo Børs» i innledningen i demoen | `tests/test_demo.py::TestStory80eTekstIDemoen::test_teksten_over_tabellen_i_demoen` |
| P6 | «Hos 1 aksjer» | `tests/test_app.py::TestStory80eTekst::test_innledningen_med_én_aksje` |
| P7 | setningen om klikk i første punkt | `tests/test_app.py::TestStory80eTekst::test_slik_leser_du_tabellen_har_3_punkter` |
| P8 | setningen borte fra steg 2 i README-en | `tests/test_docker.py::TestReadmeForNybegynnere::test_zip_fila_maa_pakkes_ut` |
