---
title: 'Story 2.1c: Vurderingen lagrer målingene bak de tre sjekkene'
type: 'feature'
created: '2026-10-01'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '94ee9bb4df50c3ed3dd39c645dab34620c7e7365'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-1b-basen-aapnes-ett-sted-og-hentingen-skriver-kursene-dit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-0-de-rene-feilene-i-de-to-skjermbildene.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** En vurdering lagrer bare fortegnene til de tre sjekkene. Tallene de ble avgjort av, finnes bare som tekst i `Sjekk.forklaring` og kastes. Et fortegn uten måling kan ikke etterprøves (FR-706), og en rad kan ikke få målingene etterpå (AD-7).

**Approach:** `Sjekk` bærer målingen og grensen som tall, og forklaringen lages av dem. Interesse avgjøres med forholdstallet. `0004_maalinger.sql` legger fire kolonner til `vurdering` med en CHECK i hver kolonne, og `Vurdering` kontrollerer verdiene i porten.

## Boundaries & Constraints

**Always:**
- Fire kolonner, uavrundet, i samme enhet som regelen regner i: `trend_avvik` (brøk, (kurs − MA50) / MA50), `dagens_endring` (brøk), `standardavvik` (brøk) og `volumforhold` (dagens volum / medianvolumet de `volum_vindu` dagene før). Aldri prosent, aldri avrundet.
- `0004`: først hjelpetabellen `kontroll_0004 (vurderinger_uten_grunn … CHECK (= 0))` med antall rader uten grunn, så `DROP TABLE kontroll_0004`, så fire `ADD COLUMN … REAL CHECK (…)`. Ingen `DROP TABLE vurdering`. En kommentar gir enheten for hver kolonne.
  - `trend_avvik`, `dagens_endring`: `(grunn IS NULL) = (<kol> IS NOT NULL)`.
  - `standardavvik`: det samme, og `standardavvik >= 0` (tillegg 01.10).
  - `volumforhold`: `grunn IS NOT NULL AND volumforhold IS NULL OR grunn IS NULL AND (volumforhold IS NOT NULL OR interesse = 0)`, og `volumforhold >= 0` når det finnes (tillegg 01.10).
- `Sjekk` får `maaling: float | None = None` og `grense: float | None = None`. Trend: målingen er avviket. Bevegelse: målingen er dagens endring, grensen standardavviket. Interesse: målingen er forholdstallet.
- Interesse: `volumforhold = dagens_volum / median_volum` når medianen er over 0, ellers `None`. `slaar_ut = volumforhold is not None and volumforhold > p.volumfaktor`.
- `forklaring` lages av feltene med `tallformat.tall` og `desimaler_mot_grense` (8.0, regel 21). Teksten for trend og bevegelse er uendret. Interesse: «volum 4,95 × medianen», med `desimaler_mot_grense(forhold, p.volumfaktor, minst=2)`. `tallformat` får slaget `"forhold"`: to desimaler, uten fortegn og uten %.
- Mangler forholdstallet: «–, medianvolumet de 20 dagene før er 0», der 20 er `p.volum_vindu` (NFR-08). Aldri 0 og aldri et anslag.
- `Vurdering` får de fire feltene, påkrevd, etter `justert_slutt`: endelige tall (`bool` og tekst avvises, heltall blir `float`), standardavvik ≥ 0, forholdstall ≥ 0 eller `None`, og `None` bare med interesse 0. Porten sjekker ikke fortegnet mot målingen.
- De fire står i `VURDERINGSKOLONNER`, så `_UPSERT` og `les` tar dem med.
- Ingen API-kall. `src/fetch_prices.py` kjøres ikke, heller ikke med `--les-inn`. Ingen rå enkeltverdier i sporede filer (regel 16).

**Never:** Vurderingen i hentingen og omformingen fra `Signal` til `Vurdering` (2.5). Historikken (2.7). KI (Epic 10). `ki_logg` (4.3, blir `0005`). Ingen endring i `sprint-change-proposal-2026-09-28.md`. Ingen egen commit på grenen for noe annet enn 2.1c.

## Beslutninger (godkjent 01.10 kl. 11:10)

1. **A:** De tre testene fra 8.0 for den gamle interesseteksten (`test_interesse_med_hel_median`, `test_interesse_med_median_paa_halv`, `test_interesse_gjennom_beregn_signal`) byttes ut med tester for forholdstallet. Resten av `tests/test_signalberegning.py` står uendret. *Rettet 2026-10-01:* tre tester fra 8.0 sjekket den gamle teksten for interesse og er byttet ut, fordi teksten følger FR-706. Resten står uendret.
2. **A:** 2.5 lager en `Vurdering` av et `Signal`. 2.1c har bare en rundturtest.
3. **B:** «–, medianvolumet de 20 dagene før er 0», med 20 fra `Parametre.volum_vindu`.
4. **B:** Merknaden om `0005` står alt i linje 58 og 291 i `sprint-change-proposal-2026-09-28.md`. Ingenting endres der.
- **Tillegg:** CHECK i basen for standardavvik ≥ 0 og forholdstall ≥ 0, med mutant 12 og 13.

## I/O & Edge-Case Matrix

| Scenario | Tilstand | Forventet |
|---|---|---|
| Vanlig dag | median > 0 | fire tall, forholdstallet avgjør interesse |
| Forholdstall nøyaktig 1,5 | `volumforhold == volumfaktor` | interesse 0 |
| Medianvolum 0 | `median_volum == 0` | `volumforhold` `None`, interesse 0, teksten med «–» og grunnen |
| Trend på grensen | avvik nøyaktig 0,02 | trend 0, «+2,0 % mot MA50» |
| Gammel vurderingsrad uten grunn | base i versjon 3 | `0004` stopper på `kontroll_0004`, rulles tilbake, versjon 3 |
| Rad med grunn i versjon 3 | | står, de fire kolonnene er NULL |
| Rad med grunn og en måling | rå SQL | avvist av basen |
| Vurdering uten en måling | rå SQL | avvist av basen |
| Negativt standardavvik eller forholdstall | rå SQL eller `Vurdering` | avvist begge steder |
| `volumforhold` NULL med interesse ±1 | rå SQL eller `Vurdering` | avvist begge steder |

</frozen-after-approval>

## Code Map

- `src/signalberegning.py` -- `Sjekk` (l. 61), `_trendforklaring`/`_bevegelsesforklaring`/`_interesseforklaring` (l. 115–142), `trend`/`bevegelse`/`interesse` (l. 145–200). `finn_styrke`, `finn_retning`, `beregn_signal` endres ikke.
- `src/tallformat.py` -- `DESIMALER`, `tall`, `desimaler_mot_grense`. Nytt slag `"forhold"`.
- `src/vurderingsdata.py` -- `Vurdering.__post_init__`. Porten importerer ikke kjernen (l. 7).
- `src/lagring_sqlite.py` -- `VURDERINGSKOLONNER` (l. 166). `_UPSERT`, `skriv` og `les` bygger på den.
- `src/migrasjoner/0004_maalinger.sql` -- ny. Mønster: `kontroll_0003` i `0003_aksje.sql`.
- `src/aksjedetalj.py`, `src/templates/aksje.html` -- ingen kodeendring (`maaling=s.forklaring`).
- `tests/test_signalberegning.py` -- `TestForklaringenPaaNorsk` l. 320–335 byttes (beslutning 1). Ny klasse for målingen.
- `tests/test_vurderingslager.py` -- hjelperen `vurdering()` (l. 48) og `GYLDIG` (l. 355) får de fire. `Sjekk(navn="", verdi=…, forklaring="")` (l. 445, 460) står.
- `tests/test_tilstand.py` (l. 29), `tests/test_aksje.py` (l. 308, og `== 3` i l. 48, 49, 256) -- følger med.
- `tests/test_app.py` l. 347 -- skjerpes til «× medianen». `tests/test_aksjedetalj.py` -- ny test for «–».
- `tests/test_migrering.py`, `tests/test_tallformat.py` -- nye tester.

## Tasks & Acceptance

**Execution:**
- [x] `src/tallformat.py` -- slaget `"forhold"` -- forholdstallet vises etter regel 21
- [x] `src/signalberegning.py` -- `maaling`, `grense`, forholdstallet, forklaringen av feltene -- målingen er det regelen så
- [x] `src/migrasjoner/0004_maalinger.sql` -- hjelpetabell og fire kolonner med CHECK -- basen krever målingene
- [x] `src/vurderingsdata.py`, `src/lagring_sqlite.py` -- fire felt med kontroller, `VURDERINGSKOLONNER` -- porten og lageret tar dem med
- [x] Testene i Code Map, og mutantene 1–13 i Verification
- [x] Spinen -- en «Bygget»-linje ved AD-7 og ved AD-18

**Acceptance Criteria:**
- Given testseriene, when regelen brukes på `maaling` og `grense`, then den gir samme verdi som sjekken, for alle tre sjekker.
- Given et `Signal` fra `beregn_signal`, when en `Vurdering` med målingene skrives og leses tilbake, then de fire flyttallene er nøyaktig like.
- Given det nyeste øyeblikksbildet i `data/raa/`, when kontrollregningen kjøres før og etter, then styrke, retning og de tre verdiene er like for alle 15, og bare teksten for interesse skiller.
- Given en base i versjon 3 med en vurdering uten grunn, when `migrer` kjøres, then den stopper med `kontroll_0004` i feilen, og basen står på versjon 3 med radene urørt.
- Given en base etter `0004`, when en rad for ukjent aksje eller med ukjent grunn settes inn, then triggerne fra `0003` og `0002` avviser den.

## Implementation Notes

- Bygget 01.10 av en implementasjonsagent. Ingenting er committet; commitene, dagsfila (regel 18) og pull requesten står igjen.
- `Sjekk(navn, verdi, forklaring, maaling=None, grense=None)`. `forklaring` er fortsatt et felt, så `Sjekk("A", 1, "")` virker som før; hjelperne lager teksten av de samme tallene som legges i `maaling` og `grense`. Trend og interesse har `grense=None`: grensene deres er `noytralsone` og `volumfaktor` i `Parametre`.
- `_interesseforklaring(forhold, p)`: «volum 4,95 × medianen» med vanlige mellomrom rundt ×, eller «–, medianvolumet de {p.volum_vindu} dagene før er 0».
- `Vurdering`: ny hjelper `_endelig` (bool og tekst avvises, heltall blir `float`, et heltall for stort for float regnes som uendelig). `volumforhold` gjøres til `float` når det ikke er `None`.
- `0004`: CHECK-ene står i hver kolonne, som i spesifikasjonen. `standardavvik >= 0` og `volumforhold >= 0` gir NULL når kolonnen er NULL, og en CHECK som gir NULL, godtas, så de slår bare til når tallet finnes.
- Testene som fulgte med: `vurdering()` i `test_tilstand.py`, `test_aksje.py` og `test_vurderingslager.py` og `GYLDIG` fikk de fire (oppdiktede verdier). `test_aksje.py`: versjon 3 → 4, og `test_rader_for_kjente_aksjer_blir_staaende` venter fire NULL-kolonner i `vurdering` etter `0004`.
- Tester: før 976 passed og 16 skipped lokalt, etter 1031 passed og 16 skipped (`uv run pytest -q`). CI er ikke kjørt.
- Kontrollregningen (`--etter`, `--sammenlign`, på `kurser-raa-2026-09-30.json`): styrke, retning og de tre verdiene er like for alle 15, tekst for trend og bevegelse lik, tekst for interesse ulik for alle 15.
- Mutantene, én om gangen, hele `tests/` hver gang, satt tilbake fra en kopi i scratchpad med sha256 sjekket: M1 3 feilet, M2 1, M3 2, M4 2, M5 2, M6 2, M7 2, M8 1, M9 17, M10 1, M11 2, M12 1, M13 1. Alle fanget.
- Spinen: «Bygget»-linjer ved AD-7 og AD-18, `updated` fra klokka.
- Ikke rørt, men utdatert: `docs/kilder-og-rettigheter.md` linje 440–443 sier at forklaringen til interesse «i dag» er `"volum {dagens_volum} mot median {median_volum}"`. Det stemmer ikke lenger etter 2.1c.

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q` -- grønn. Før: 992 i CI på main (976 passed og 16 skipped lokalt).
- `uv run python data/kontrollregning_2_1c.py --foer` (på main), `--etter` og `--sammenlign` -- bare symboler og lik/ulik.

**Mutantene**, én om gangen, koden satt tilbake fra en kopi i scratchpad, ikke med `git checkout`:
1. Målingen i prosent. 2. Målingen avrundet. 3. CHECK på `trend_avvik` fjernet. 4. CHECK på `volumforhold` godtar NULL uansett interesse. 5. Hjelpetabellen fjernet. 6. `>` → `>=` i interesse. 7. Porten godtar `None` med interesse 1. 8. Porten godtar negativt standardavvik. 9. En kolonne mangler i `VURDERINGSKOLONNER`. 10. Fast to desimaler i stedet for `desimaler_mot_grense`. 11. Medianvolum 0 gir `0.0`. 12. CHECK `standardavvik >= 0` fjernet. 13. CHECK `volumforhold >= 0` fjernet.
