---
title: 'Story 8.0c: Tydelig merking, ord ved sjekkene og datoer på grafen'
type: 'feature'
created: '2026-10-13'
status: 'in-review'
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

- Del a `fcb6c31`, b `83fa382`, c `e2e3f79`, d `c6769d8`. Main hentet inn med merge i `b5fcc8f`. Den commiten mangler Co-authored-by og er ikke skrevet om (regel 7).
- `ingen_skilte_seg_ut()` i `markedsoversikt.py` leser `skiller_seg_ut`, som alt bruker terskelen fra `Parametre`.
- `antall_sjekker` gis til malene fra kontekstprosessoren, fra `ANTALL_SJEKKER` i `hjelpetekster.py`.
- Merket står ett sted, `EKSEMPELTALL_MERKE` i `app.py`. README-ens sitat i steg 6 står ordrett øverst på siden, så README-en er ikke endret. `test_merket_i_demoen_er_det_samme_som_i_malene` sammenligner med konstanten.
- Linja over tabellen i demoen er «Eksempeltall · 2026-10-09 · 14 aksjer». «09.10» kommer med PR 2.
- Hjelpen: 6 «?» i oversikten (23 setninger) og 12 på aksjesiden. Ny tekst «selskap», ordrett fra tavla. Ingen «?» med tom base. «Ga» bygges av `POSITIV`, `NEGATIV` og `INGEN_UTSLAG`.
- Testene som er endret: «N av 3» i `test_app.py`, demolinja og hjelpen i `test_demo.py`, grensene, plasseringen og tom base i `test_hjelpetekster.py`, og merket i `test_docker.py`.

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q` -- expected: grønn. Før: 1404 bestått og 16 hoppet over, 1420 samlet (instruksjonen kl. 14:33). På main før grenen: 1407 og 16, 1423 samlet, etter `tests/test_suksesskriterier.py`.
