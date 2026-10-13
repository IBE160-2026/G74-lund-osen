---
title: 'Story 8.0c: Tydelig merking, ord ved sjekkene og datoer på grafen'
type: 'feature'
created: '2026-10-13'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'd9315a9570fdd8fa3b63f15e4f8fc8a93d143ffd'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-0b-hjelp-bak-et-spoersmaalstegn.md'
  - '{project-root}/_bmad-output/planning-artifacts/sprint-change-proposal-2026-10-13.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Sidene viser ikke tydelig hvilke aksjer som skiller seg ut, Ga-kolonnen viser bare et fortegn, grafen har datoer bare i bildeteksten, og hjelpen er lang og bruker ord ordlista har valgt bort (story 8.0c med tilleggene 05.10, 11.10 og 13.10 i `epics.md`).

**Approach:** To pull requests. PR 1 (grenen `8-0c`) tar merkingen, ordene, fotnotene, demoen, linja «under arbeid» og hjelpen. PR 2 (grenen `8-0c-datoer`) tar datoene og månedsmerkene i grafen, etter at PR 1 er flettet.

## Planen

Planen ble vist i chatten 13.10 og er ført i `docs/ai-prompts/2026-10-13.md` (instruksjonen kl. 13:35 og Utført-linjen). Gruppen sa ja kl. 14:33 med disse svarene, som er beslutninger:

1. **To pull requests.** PR 2 (datoene og månedsmerkene) kommer etter at PR 1 er flettet.
2. **2 av 3 eller mer** merkes med fet skrift og en strek til venstre i tekstfargen, uten gult, i begge tabellene. 3 av 3 får i tillegg gul ring rundt pillen i oversikten (designregler §3).
3. **Linja over tabellen i demoen** sier «Eksempeltall» i stedet for «Oslo Børs». Formen på datoen («09.10») kommer med PR 2.
4. **Linja nederst** er «Appen er under utvikling og ikke ferdig.», styrt av én konstant i `app.py`. `docs/innlevering.md` får et punkt i §5.
5. **Grensene** sier «15 aksjer på Oslo Børs» i begge versjonene.
6. **Hjelpen lages på nytt** og bygges ikke før gruppen har sagt ja til den nye delen 2: hvert «?» står ved det det forklarer, de to vinduene «Tallene og signalet» blir borte (det endrer svar 2 fra 8.0b), tekstene om sjekkene og grensene står på aksjesiden, og «Ikke et råd» står i vinduet for signalstyrken på begge sidene. Høyst 3 setninger per tekst, utenom grensene og skjevhet.
7. **Setningen «Ingen aksjer skilte seg ut …»** står bare når ingen har styrke på terskelen eller mer. En test med én aksje på 3 av 3 og ingen på 2 krever at den ikke står.
8. **Fotnoten på aksjesiden** slutter med «Signalstyrken sier ikke om du bør kjøpe eller selge.» (tillegget 11.10).
9. **Ordtesten** leter også etter «kr» som eget ord.
11. **Setningen når noen rader mangler vurdering** (svar 3 på BH1/ECH2, 13.10 kl. 16:42): står setningen fra 05.10, og minst én rad mangler vurdering, kommer «N av M aksjer ble vurdert.» under den. N er radene med vurdering og M alle radene, begge talt fra radene, og den virker for alle tall, også 1. Er alle vurdert, står setningen fra 05.10 alene. Har ingen rad vurdering, står ingen av dem.
12. **PR 2, datoene** (instruksjonen kl. 18:45 13.10): `dato()` i `tallformat.py` gir «22.09», og med år bare når året er et annet enn i dag: «29.09.2025». I dag kommer fra `app.idag()`, så testene styrer det. `norsk_tid` gir «24.09 kl. 20.05». Alle datoene på sidene går gjennom `dato()` eller `norsk_tid`: linja over tabellen (i demoen «Eksempeltall · 09.10 · 14 aksjer»), «data hentet», tidsstempelet under navnet, datoene på aksjesiden, grafens fra–til og «Ingen vurdering for …». En test krever at ingen synlig tekst på sidene har en dato som 2026-10-13, også med demobasen (FR-411).
13. **PR 2, månedsmerkene:** merket står ved første børsdag i måneden etter `er_boersdag`, med fullt norsk månedsnavn i små bokstaver («oktober»), på samme x som punktet for den dagen. Mangler den dagen i serien, får måneden ikke merke. Datoene i bildeteksten står. Mutantene M7 (merkene etter kalenderen), M8 (merkene én dag feil) og én der `dato()` viser året i samme år, fanges.
10. **Den nye delen 2 er godkjent** 13.10 kl. 15:36, slik den ble vist kl. 15:03 (instruksjonen og svaret i `docs/ai-prompts/2026-10-13.md`), med én endring: i tabellen med sjekkene på aksjesiden får hver sjekk sitt eget «?» ved navnet, med bare sin tekst (trend 2, bevegelse 3 og interesse 3 setninger). «?» ved «Hvorfor signalet ble …» har bare «Hvorfor disse 3» og antall dager (5 setninger). Oversikten får 6 «?»: Selskap, Sluttkurs, Endring, Signalstyrke, Retning og «data hentet». Aksjesiden får «?» ved Sluttkurs, kursgrafen, Signalstyrke, Retning (med skjevhet), «Hvorfor signalet ble …», hver sjekk, Ga og «Målt mot» (med grensene).

## Boundaries & Constraints

**Always:**
- Tabellen i oversikten har fortsatt fem kolonner (FR-101).
- Tall i malene kommer fra `Parametre` og `ANTALL_SJEKKER`, ikke skrevet fast.
- Det storyen viser, vises også med demobasen, og en test krever det (FR-411, tverrgående fra 8.0c).
- Grenen bruker bare testbaser (regel 22). Ingen API-kall, ingen nettkall i tester (AD-8).
- Hver hjelpetekst har en kilde som finnes, og sier bare det koden gjør og det kilden sier. Ingen tekst kan leses som et råd (NFR-06, `RAADSORD`).

**Never:**
- Ingen sjette kolonne, ingen ny funksjon og ingen knapp til en side som ikke finnes.
- Ingen endring i signalberegningen, hentingen eller basen.
- Hjelpen bygges ikke før gruppen har sagt ja til den nye delen 2.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Ingen over terskelen | Alle rader med vurdering har 0 eller 1 | «Ingen aksjer skilte seg ut: ingen fikk 2 av 3 eller mer.» | N/A |
| Bare 3 av 3 | Én rad 3 av 3, ingen på 2 | Ingen setning, gul ring på raden | N/A |
| Ingen vurdering | Ingen rad har styrke | Ingen setning | N/A |
| Demobasen | Bryteren med demobase | «Demoversjon.» foran merket, «Eksempeltall · …» over tabellen | N/A |

</frozen-after-approval>

## Code Map

- `src/markedsoversikt.py` -- `ingen_skilte_seg_ut(rader)` ved `sidens_dato`, ren logikk.
- `src/app.py` -- kontekstprosessoren gir `antall_sjekker`, merket for demoen og linja «under arbeid». Ruten for oversikten gir `ingen_skilte_seg_ut`.
- `src/templates/index.html` -- «N av 3», `.pille.tre-av-tre`, `tr.utslag`, `th.tall`, setningen, fotnoten, demolinja.
- `src/templates/aksje.html` -- Ga med ord, `tr.bidro`, `th.fortegn`, fotnoten, «N av 3».
- `src/templates/basefeil.html` -- merket og linja «under arbeid».
- `src/aksjedetalj.py` -- `Sjekkvisning.ord`, bygget av `POSITIV` og `NEGATIV` i `signalberegning.py`, og `INGEN_UTSLAG`.
- `src/hjelpetekster.py` -- tekstene etter den nye delen 2 (venter på ja).
- `tests/test_app.py`, `tests/test_aksjedetalj.py`, `tests/test_demo.py`, `tests/test_hjelpetekster.py` -- testene.
- Ikke endre: `signalberegning.py`, `fetch_prices.py`, `lagring_sqlite.py`.

## Tasks & Acceptance

**Execution:**
- [x] a. Oversikten: «N av 3», gul ring, merkingen av 2 av 3, `th.tall`, setningen -- tillegget 05.10 og svar 2 og 7
- [x] b. Aksjesiden: Ga med ord, merkingen av radene, `th.fortegn`, fotnotene på begge sidene -- tilleggene 05.10, 11.10 og svar 8
- [x] c. Demoen og linja nederst: «Demoversjon.», «Eksempeltall · …», «under arbeid», `docs/innlevering.md` -- svar 3 og 4
- [x] d. Hjelpen etter den nye delen 2, ordtesten og grensene -- svar 5, 6 og 9 (venter på ja)
- [x] e. Demotesten for alt det nye (`TestStory80cIDemoen` og testene i `test_demo.py`). README-ens statuslinje flyttes i flettingen

**Acceptance Criteria:**
- Given en aksje med 2 av 3, when oversikten vises, then raden har fet skrift og en strek til venstre, uten gult og uten bare lys bakgrunn.
- Given demobasen, when sidene vises, then alt det nye i PR 1 står også der.

## Implementation Notes

- *Lagt til 2026-10-13:* PR 1 er flettet i `82271fb`, PR #35, låst til `5fa7304`. PR 2 med datoene og månedsmerkene gjenstår, og spesifikasjonen står som in-progress til den er flettet.

- Del a `fcb6c31`, b `83fa382`, c `e2e3f79`, d `c6769d8`. Main hentet inn med merge i `b5fcc8f`. Den commiten mangler Co-authored-by og er ikke skrevet om (regel 7).
- `ingen_skilte_seg_ut()` i `markedsoversikt.py` leser `skiller_seg_ut`, som alt bruker terskelen fra `Parametre`.
- `antall_sjekker` gis til malene fra kontekstprosessoren, fra `ANTALL_SJEKKER` i `hjelpetekster.py`.
- Merket står ett sted, `EKSEMPELTALL_MERKE` i `app.py`. README-ens sitat i steg 6 står ordrett øverst på siden, så README-en er ikke endret. `test_merket_i_demoen_er_det_samme_som_i_malene` sammenligner med konstanten.
- Linja over tabellen i demoen er «Eksempeltall · 2026-10-09 · 14 aksjer». «09.10» kommer med PR 2.
- Hjelpen: 6 «?» i oversikten (23 setninger) og 12 på aksjesiden. Ny tekst «selskap», ordrett fra tavla. Ingen «?» med tom base. «Ga» bygges av `POSITIV`, `NEGATIV` og `INGEN_UTSLAG`.
- Tekstene avviker fra tavla og fra tabellen i 4.4 der planen kl. 13:35 og delen 2 kl. 15:03 viste det: trend står som før, fordi testen krever «de siste 50 børsdagene», interesse sier «1,5 ganger» og ikke «1,5 ×», bevegelse og hvorfor_tre har +1 og -1 og «med én regel og én grense hver», og blandet og signalstyrke har ordlyden fra delen 2. Godkjent 13.10 kl. 14:33 og 15:36.
- Testene som er endret: «N av 3» i `test_app.py`, demolinja og hjelpen i `test_demo.py`, grensene, plasseringen og tom base i `test_hjelpetekster.py`, og merket i `test_docker.py`.

## Spec Change Log

## Review Triage Log

Gjennomgang av PR #35 (diffen `main...8-0c` på `c6db3e5`), med Blind Hunter (BH, bare diffen), Edge Case Hunter (ECH) og Verification Gap (VG) som tre uavhengige agenter 13.10. Rettingene står i `1dcfbdb`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| VG1 | Setningen «Ingen aksjer skilte seg ut» er ikke prøvd med 2 av 3, så en mutant med `== ANTALL_SJEKKER` overlever | høy | patch: test med én aksje på 2 av 3 |
| VG2 | Merkingen er bare prøvd der den skal stå, ikke at den mangler der den ikke skal | medium | patch: én rad med 1 av 3 og én med 2 av 3, og antall `bidro` |
| VG3 | Ingen test binder «Målt mot» til merkingen | medium | patch: «lys bakgrunn» i ordtesten |
| ECH3, ECH4 | Ordtesten bommer når et ord er delt over to linjer, og kan treffe CSS | medium | patch: bare synlig tekst, med mellomrom slått sammen |
| BH2 | Ingen mellomrom mellom tallet og ordet i Ga | medium | patch |
| BH3 | Den gule ringen har om lag 2,3:1 mot hvit | medium | patch: `#a67c00`, og en test for minst 3:1 |
| VG6 | Forbeholdet om kjøp og salg står bare med tabellen | lav-medium | patch: egen fotnote, test på en side uten sjekker |
| BH7, ECH11 | «Blandet» skrevet fast i fotnoten | lav | patch: fra `BLANDET` |
| BH8 | Testen låser `UNDER_ARBEID` på True | lav | patch: monkeypatch |
| BH9, VG10 | Vindustesten finner ikke escapet tekst og sjekker ikke rekkefølgen | lav | patch |
| BH10, ECH5 | Setningstelleren teller ikke setninger som slutter med «.»» | lav | patch, med tilfellet i testen |
| BH12 | Betingelsen for grafhjelpen står to steder | lav | patch: `vis_grafhjelp` |
| BH15 | `.tittelrad` brukes ikke lenger | lav | patch: fjernet |
| ECH6 | Id-en per sjekk kommer fra navnet | lav-medium | patch: test som krever en gyldig og unik nøkkel per sjekk |
| ECH7 | `ANTALL_SJEKKER` er ikke bundet til antall sjekker i koden | lav-medium | patch: test |
| VG8 | Bevegelse er ikke bundet til koden i hjelpen | lav | patch: test |
| VG11 | «seks måneder» med bokstaver | lav | patch: «6 måneder» |
| BH1, ECH2 | Setningen står selv om noen rader ikke er vurdert | medium | spørsmål til gruppen før flettingen |
| BH4 | «?» inne i `<th>` og `<h2>` gir overskriftene et lengre tilgjengelig navn | medium | utsatt: `deferred-work.md`, 8.0d (fokus og utseende) |
| BH5, ECH8 | `uten_data` vises bare når `hentet` finnes | lav | utsatt: `deferred-work.md` |
| ECH1 | Ga sier «ingen utslag» når volumet var høyt og kursen uendret | lav | utsatt: `deferred-work.md` |
| ECH9 | 404-siden har verken merket eller linja «under arbeid» | lav | utsatt: `deferred-work.md` |
| BH14 | «Demoversjon.» og stilen står i tre maler | lav | utsatt: felles layout i 8.0d |
| BH6 | Fotnoten viser antall sjekker som slo ut, ikke den lagrede styrken | false | `test_aksjedetalj.py` krever `d.styrke == len(d.bidragsytere)` |
| BH11 | `hjelpetekster` importerer `INGEN_UTSLAG` fra `aksjedetalj` | avvist | `aksjedetalj` importerer ikke `hjelpetekster`, og spesifikasjonen sier ingen endring i `signalberegning.py` |
| BH13 | «selskap» sier «Klikk» og nevner grafen også når den mangler | avvist | ordrett fra tavla, godkjent i delen 2 |
| ECH10 | Ingen «?» ved grafen når tabellen mangler | avvist | samme betingelse som i 8.0b, og teksten viser til tabellen |
| ECH12 | Terskelen kommer fra to steder | avvist | begge er `STANDARD` i `app.py`, og testen bytter begge |
| VG4 | Tekstene er ikke ordrett fra tavla og 4.4 | avvist | avvikene ble vist i planen kl. 13:35 og delen 2 kl. 15:03 og godkjent kl. 14:33 og 15:36. Ført under Implementation Notes |
| VG5 | Kildene er overskrifter og funksjonsnavn | avvist | samme form som i 8.0b, og VG fant at alle sier det teksten sier |
| VG7 | Fotnoten på aksjesiden følger tavlas tekst for styrken, ikke resten av 4.4 | avvist | teksten sto i planen kl. 13:35 (4b) og ble godkjent |
| VG9, VG12, VG13 | Små merknader: ordet bygget av konstanten, `data_hentet_aksje` uten `hentet`, perioden for vinduene | avvist | merknader uten feil |

## Verification

**Commands:**
- `uv run pytest -q` -- expected: grønn. Før: 1404 bestått og 16 hoppet over, 1420 samlet (instruksjonen kl. 14:33). På main før grenen: 1407 og 16, 1423 samlet, etter `tests/test_suksesskriterier.py`.

**Mutantene** (13.10, på `ce4f6e0`): hver mutant ble kjørt mot hele testsettet med `-x`, én om gangen. Fila ble satt tilbake fra en kopi og kontrollert med sha256. Alle 19 ble fanget. M7, M8, M17 og M18 i planen gjelder datoene og grafen og hører til PR 2.

| # | Mutant | Fanget av |
|---|---|---|
| M1 | styrken bare som tall | `tests/test_app.py::TestStory80::test_aksjen_som_skiller_seg_ut_er_merket_med_tekst` |
| M2 | den gule ringen borte | `tests/test_app.py::TestStory80c::test_tre_av_tre_har_gul_ring_og_to_av_tre_ikke` |
| M3 | 2 av 3 bare med lys bakgrunn | `tests/test_app.py::TestStory80c::test_to_av_tre_merkes_med_mer_enn_lys_bakgrunn` |
| M4 | en sjette kolonne | `tests/test_app.py::TestTidsstempler::test_fortsatt_fem_kolonner` |
| M5 | Ga uten ordet | `tests/test_app.py::TestStory80c::test_ga_kolonnen_har_tallet_og_ordet` |
| M6 | Ga sier opp | `tests/test_aksjedetalj.py::TestByggDetalj::test_ordet_bygges_av_konstantene_i_signalberegning` |
| M9 | terskelen fast i setningen | `tests/test_app.py::TestStory80c::test_terskelen_i_setningen_kommer_fra_parametre` |
| M10 | setningen ser etter 3 av 3 | `tests/test_app.py::TestStory80c::test_setningen_staar_ikke_med_to_av_tre` |
| M11 | th.tall venstrejustert | `tests/test_app.py::TestStory80c::test_overskriftene_staar_over_tallene` |
| M12 | «Demoversjon.» borte | `tests/test_demo.py::TestSidene::test_bryteren_med_demobase_viser_eksempeltall` |
| M13 | «under arbeid» ikke fra innstillingen | `tests/test_app.py::TestStory80c::test_under_arbeid_styres_av_en_innstilling` |
| M14 | en hjelpetekst med 4 setninger | `tests/test_hjelpetekster.py::TestStory80c::test_hoeyst_tre_setninger_per_tekst[standard]` |
| M15 | «peker opp» igjen | `tests/test_demo.py::TestStory80cIDemoen::test_merkingen_og_ordene_i_demoen` |
| M16 | fotnoten sier «hvor kraftig» | `tests/test_app.py::TestStory80c::test_fotnoten_i_oversikten_sier_hvor_mange_som_slo_ut` |
| M19 | demolinja sier Oslo Børs | `tests/test_demo.py::TestSidene::test_bryteren_med_demobase_viser_eksempeltall` |
| M20 | forbeholdet borte fra aksjesiden | `tests/test_app.py::TestStory80c::test_fotnoten_paa_aksjesiden_har_forbeholdet` |
| M21 | «?» per sjekk borte | `tests/test_demo.py::TestSidene::test_hjelpen_virker_ogsaa_i_demoen` |
| M22 | «Målt mot» sier lys bakgrunn | `tests/test_demo.py::TestStory80cIDemoen::test_merkingen_og_ordene_i_demoen` |
| M23 | grensene uten «på Oslo Børs» | `tests/test_hjelpetekster.py::TestGrensene::test_teksten_om_maalingen_nevner_de_maalte_grensene` |
| M24 | «N av M aksjer ble vurdert.» borte | `tests/test_app.py::TestStory80c::test_noen_mangler_vurdering_gir_begge_setningene` |
