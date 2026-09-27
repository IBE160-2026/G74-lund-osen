---
title: 'Story 1.8: Hentingen godtar bare det leseren kan lese'
type: 'bugfix'
created: '2026-09-27'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f6d82c4adf031ab327aa8782f71a68349f24c426'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/kodegjennomgang-epic-1.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `_riktig_form` i `fetch_prices.py` sjekker bare at fire felt finnes og at `date` er tekst, mens `SnapshotLeser` oversetter hver rad og avviser like datoer. En serie med `close` None, `close` 0, `volume` 1000.0, `date` «2026-9-24» eller en dato som går igjen, lagres uten noe i `feil`, og leseren dropper den (G1, prøvd 27.09).

**Approach:** Én funksjon, `serie_fra_eodhd` i `eodhd.py`, avgjør om en hel serie kan leses og reiser én feiltype, `UgyldigSerie`. `SnapshotLeser` og `hent_universet` bruker den begge, og `FELT` og `_riktig_form` forsvinner. G2–G5 og G8 tas i samme story.

## Boundaries & Constraints

**Always:**
- Leseren oppfører seg som før: ingen test i `test_snapshotleser.py` endrer det den krever.
- Hentingen lagrer rådataene uendret, i samme format. `[]` gir «tomt svar», alt annet leseren avviser, gir «svar med feil form», og de andre aksjene lagres likevel (AD-15).
- EODHDs feltnavn står bare i `eodhd.py`. `fetch_prices.py` kommer under strengvakten.
- Regel 6: ingen nett i testene. `src/fetch_prices.py` kjøres ikke.

**Never:**
- Ingen endring i `Kursrad`, `kursrad_fra_eodhd`s regler, lagrene eller migrasjonene.
- Ingen ny sjanse for et symbol som feiler, og ingen endring i hvordan kall telles.

## Beslutninger (godkjent 27.09)

- **`serie_fra_eodhd(raa) -> list[Kursrad]`** i `eodhd.py`, sortert med nyeste sist. `UgyldigSerie(ValueError)` i `eodhd.py` reises når serien ikke er en liste, når en rad gir `UgyldigKursrad` eller `KeyError`, og ved like datoer. `[]` gir `[]`, ikke en feil.
- **Én felles liste** i `tests/eodhd_serier.py` med bare serier `serie_fra_eodhd` avviser: minst tilfellene `test_snapshotleser.py` prøver i dag, de fem fra 27.09 og de fem i `TestSvarMedFeilForm`. Den tomme serien er ikke med. Den prøves for seg.
- **G5:** `finn_styrke(sjekker)` i `signalberegning.py`, brukt av `beregn_signal`, slik retningen har `finn_retning`. Testen i `test_signalberegning.py` bruker minst én serie der en sjekk er negativ.
- **Gjennomgangen** har tre lag: Blind Hunter, Edge Case Hunter og Verification Gap.
- **Spinen:** kanten `fetch --> eodhd`, en merknad under AD-15 og en «Bygget»-linje under AD-19. «Ferdig»-linjen i `epics.md` får datoen fra klokka ved flettingen.

## I/O & Edge-Case Matrix

| Scenario | Input | Hentingen | Leseren |
|---|---|---|---|
| Gyldig serie | ISO-datoer, gyldige verdier | rådataene lagres, utskriften viser siste dato fra den oversatte serien | serien leses |
| Tom serie | `[]` | «tomt svar» i `feil` | manglende |
| Avvist serie | hvert tilfelle i den felles lista | «svar med feil form» i `feil`, de andre lagres | bare det symbolet er manglende |

</frozen-after-approval>

## Code Map

- `src/eodhd.py` -- `kursrad_fra_eodhd` (`:34`) gjenbrukes. Ny `serie_fra_eodhd` og `UgyldigSerie` her.
- `src/lagring_fil.py:92–103` -- løkken i `SnapshotLeser.__init__`: `isinstance(raa, list)`, fangsten av `(UgyldigKursrad, KeyError)` og kontrollen av like datoer flyttes inn i funksjonen. `kilde.serier` som ikke er en dict, blir stående her.
- `src/fetch_prices.py:112–125` -- `FELT` og `_riktig_form` fjernes. `:162–174`: rekkefølgen er feil form, så tom, så lagring. `:174` bruker `rader[-1]['date']`. Docstringene `:15` og `:180` sier `SnapshotKilde` (G4).
- `tests/test_konsumentene.py:55–58` -- `UTEN_EODHD_STRENGER` og kommentaren.
- `tests/test_fetch_prices.py` -- `falsk_serie` bruker «dag-000» og må få ISO-datoer. `TestSvarMedFeilForm` (`:179`). G2: `:203–204, 235–236, 248, 280, 290, 393`. G3: `:101–114`.
- `tests/test_snapshotleser.py` -- de eksisterende testene står urørt. Tilfellene til lista: `:139–173` og `:195–203`.
- `src/signalberegning.py:211` -- `styrke = sum(abs(...))`. `tests/test_vurderingslager.py:442` -- mønsteret for `finn_retning`. `tests/test_signalberegning.py:112` -- serien som gir Trend 1, Bevegelse -1, Interesse -1.
- `tests/test_lagring_sqlite.py:51` -- G8-navnet.
- `ARCHITECTURE-SPINE.md` -- grafen (`:93–94`), AD-15 (`:224`) og AD-19 (`:297`).

## Tasks & Acceptance

**Execution:** én commit per punkt, pushet til grenen `1-8`.
- [x] `src/eodhd.py`, `src/lagring_fil.py` -- seriefunksjonen og leseren. Tester for funksjonen i `test_snapshotleser.py` (`TestOversetteren` eller en ny klasse).
- [x] `tests/eodhd_serier.py`, `src/fetch_prices.py`, `tests/test_fetch_prices.py`, `tests/test_snapshotleser.py`, `tests/test_konsumentene.py` -- den felles lista og hentingen. Nye tester: lista mot leseren, lista mot hentingen, lista gjennom `kjoer` og `nyeste_leser` (hver aksje kan leses eller står i `feil`), rådataene er uendret, og en strukturtest for at begge bruker `serie_fra_eodhd` og ingen av dem `kursrad_fra_eodhd` direkte.
- [x] `tests/test_fetch_prices.py` -- G2.
- [x] `tests/test_fetch_prices.py` -- G3: en nøkkel med mellomrom, parametrisert over `quote` og `quote_plus`.
- [x] `src/fetch_prices.py` -- G4.
- [x] `src/signalberegning.py`, `tests/test_vurderingslager.py`, `tests/test_signalberegning.py` -- G5.
- [x] `tests/test_lagring_sqlite.py` -- G8: `test_tom_base_migreres_og_faar_kurs_og_kursserie`.
- [x] `ARCHITECTURE-SPINE.md` -- kanten, AD-15 og AD-19.

**Acceptance Criteria:**
- Gitt en serie i den felles lista for DNB, når `hent_universet` kjøres, så står DNB med «svar med feil form» i `feil`, og de andre er i `serier`.
- Gitt den samme serien, når `SnapshotLeser` leser den, så er bare DNB manglende.
- Gitt hvert kontrollpunkt, når mutanten legges inn alene, så feiler minst én test, og koden settes tilbake før neste: egen regel i hentingen, en henting som hopper over kontrollen, ingen sjekk av like datoer, `"date"` tilbake i utskriften, oversatt serie lagret, `UgyldigSerie` for `[]`, G3 med `quote` og `quote_plus` fjernet hver for seg, og G5 med `finn_styrke` uten `abs` og `beregn_signal` uten `abs`. G2 prøves med en 16. aksje, og G4 og G8 med grep.

## Implementation Notes

Bygget 27.09 direkte fra spesifikasjonen, ikke av en subagent, fordi planen krever én commit per sak og mutantene én om gangen. Commitene på grenen `1-8`: (a) `8cabfe3`, (b) `8802ff7`, (c) `d5e5fb7`, (d) `3c49590`, (e) `3f16bc7`, (f) `66ed0ae`, (g) `0af3cdf` og (h) `ac1514b`. Tester: 665 før og 815 etter.

- `serie_fra_eodhd` fanger `UgyldigKursrad` og `KeyError` og reiser `UgyldigSerie` med den opprinnelige feilen som `__cause__`. `SnapshotLeser` sjekker fortsatt selv at `kilde.serier` er en dict.
- `tests/eodhd_serier.py` har 27 serier. `falsk_serie` i `test_fetch_prices.py` fikk ISO-datoer fra 2026-06-01.
- `test_henter_alle_femten_…` beholder navnet sitt. Tallet i `Resultat(..., kall_brukt=15)` i `test_feil_foelger_med_i_bildet` er data, ikke en påstand, og står.

**Mutantene**, hver lagt inn alene, full testkjøring og koden satt tilbake før neste:

| Mutant | Utfall |
|---|---|
| M1: hentingen med sin egen regel (`fetch_prices.py` fra baseline) | 30 feil: 14 av 27 serier i hver av de to testene over lista, strukturtesten og strengvakten. Den gamle regelen slapp gjennom 14 av de 27 |
| M2: hentingen hopper over kontrollen og lagrer rådataene | 54 feil: alle 27 i begge testene over lista |
| M3: seriefunksjonen sjekker ikke like datoer | 6 feil, både for leseren og for hentingen |
| M4: `rader[-1]['date']` tilbake i utskriften | 1 feil: strengvakten for `fetch_prices.py` |
| M5: den oversatte serien lagres | 29 feil: rådatatesten, `test_formatet_kan_leses_av_visningen` og alle 27 gjennom `kjoer` |
| M6: `UgyldigSerie` for `[]` | 2 feil: «tomt svar» i hentingen og testen for funksjonen |
| G2: en 16. aksje i `AKSJEUNIVERS` | De nye testene består (81 av 81). Testene fra før G2 gir 5 feil |
| G3: `quote`, så `quote_plus`, fjernet fra `_uten_noekkel` | 1 feil hver, i hver sin parametrisering |
| G5: `finn_styrke` uten `abs` | 22 feil, 19 av dem i testen over de 27 kombinasjonene |
| G5: `beregn_signal` summerer selv uten `abs` | 4 feil, blant dem de to seriene med negative sjekker i `TestStyrke` |

G4 og G8 er kontrollert med grep: «SnapshotKilde leser» og `versjon_1` finnes ikke lenger.

**Hendelse:** den første kjøringen av mutantene for G5 satte koden tilbake med `git checkout`. Det tilbakestilte også `finn_styrke`, som ikke var committet. Mutant 1 var alt kjørt mot den riktige koden, og mutant 2 feilet før den ble lagt inn, fordi teksten ikke fantes. Endringen ble lagt inn på nytt, mutant 2 ble kjørt, og fra da av ble koden satt tilbake fra en kopi.

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q` -- expected: alle består. 665 før, og tallet etter føres i commit-meldingen.
- `grep -n "SnapshotKilde leser\|versjon_1" src/fetch_prices.py tests/test_lagring_sqlite.py` -- expected: ingen treff.
