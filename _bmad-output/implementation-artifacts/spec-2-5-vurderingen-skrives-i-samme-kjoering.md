---
title: 'Story 2.5: Vurderingen skrives i samme kjøring'
type: 'feature'
created: '2026-10-02'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'c5c42f101ef7c2041ebecebbf83226c45b70dde0'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-1b-basen-aapnes-ett-sted-og-hentingen-skriver-kursene-dit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-1c-vurderingen-lagrer-maalingene-bak-de-tre-sjekkene.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Hentingen skriver kursene til basen, men ingen vurdering. En vurdering kan ikke etterfylles (AD-7), så hver kjøring uten den mangler for alltid i historikken (FR-408).

**Approach:** Etter at kursene er skrevet, leser `kjoer` seriene tilbake fra basen og skriver én rad per aksje i universet med `SqliteVurderingslager`: en `Vurdering` regnet av den ene rene funksjonen `signalberegning.vurder`, eller en `Grunn` (punkt 24). Datoen regnes én gang fra øyeblikket.

## Boundaries & Constraints

**Always:**
- Rekkefølgen i `kjoer`: øyeblikket, `dato = innevaerende_boersdag(norsk_dato(oeyeblikk))` før filvakten og før første kall, filvakten, hentingen, fila, kursene, vurderingene, utskriften.
- Seriene til vurderingen leses tilbake med `SqliteKurslager.serie` etter at alle seriene er skrevet, bare for symbolene `skriv_til_basen` skrev i denne kjøringen.
- Én rad for hvert symbol i `AKSJEUNIVERS`, aldri ingen rad: `SYMBOL_FEILET` for et symbol i `resultat.feil` eller som basen avviste eller hoppet over; ellers `vurder(rader, dato)`.
- `vurder`: `KURS_IKKE_FRA_DAGEN` når `rader[-1].dato != dato`; `SIGNAL_IKKE_REGNET` når `beregn_signal` eller `Vurdering` reiser `ValueError` eller `ArithmeticError`; ellers `Vurdering` med `trend_avvik` = trend.maaling, `dagens_endring` = bevegelse.maaling, `standardavvik` = bevegelse.grense, `volumforhold` = interesse.maaling, `slutt` og `justert_slutt` fra siste rad.
- `kjoer(…, klokke=None)`: `main` gir `naa`. Uten klokke leses `oeyeblikk`. Klokka går til `SqliteVurderingslager`, og leses én gang før vurderingene: er `norsk_dato(klokke())` en annen dag enn øyeblikkets, stopper kjøringen, sier fra og avslutter med kode 1. En `ValueError` fra `skriv` midt i universet gir samme melding med antallet som alt er skrevet.
- Feiler basen, skrives ingen vurdering, meldingen sier at dagen ikke kan fylles inn etterpå, og kode 1.
- `--les-inn` skriver aldri vurdering (AD-7).
- Utskriften: antall vurderinger, dagen raden gjelder, antall med grunn og symbolene med grunnen. Ingen kurser og ingen målinger (regel 16).
- Ingen API-kall. `src/fetch_prices.py` kjøres ikke, heller ikke med `--les-inn`.

**Never:** Børsdagskontrollen og nekting før kl. 22 (2.3). Historikken (2.7). Indeksen (2.8). KI (Epic 10). Relevante meldinger i raden. Ingen egen commit på grenen for noe annet enn 2.5.

## Beslutninger (godkjent 02.10 kl. 10:29)

1. **A:** En dag børsen er stengt, gjelder raden inneværende børsdag (AD-7, 1.7). Finnes raden for den dagen fra før, står den, og utskriften sier det. Utskriften sier alltid hvilken dag raden gjelder.
2. **A:** `UtenforKalenderen` stopper kjøringen før første kall, med 0 kall brukt, og meldingen sier at de stengte dagene må føres inn for året (NFR-08).
3. **A:** `vurder()` ligger i `signalberegning.py` som en ren funksjon. Kjernen importerer porten `vurderingsdata`. Pila føres inn i spinen og diagrammet, og `test_konsumentene.py` låser den.
4. **A:** Hentingen kjøres for hånd mellom kl. 22 og midnatt til 2.3. README får én setning: kjøres hentingen før kursene er publisert, stopper filvakten kveldens kjøring, og dagen får ingen vurdering.
- **Tillegg:** kontrollregning med `vurder()` på det nyeste øyeblikksbildet, uten nett og uten basen. Bare antall og symboler.

## I/O & Edge-Case Matrix

| Scenario | Tilstand | Forventet |
|---|---|---|
| Vanlig børsdag | 15 serier med dagens kurs | 15 `Vurdering` |
| Symbol feilet i hentingen eller i basen | | rad med `symbol_feilet` |
| Nyeste kurs er fra dagen før | | rad med `kurs_ikke_fra_dagen` |
| For kort serie | under 51 dager | rad med `signal_ikke_regnet` |
| To kjøringer samme dag | fila finnes | andre stopper ved filvakten, 15 rader |
| Ny kjøring uten fil, et symbol feiler | vurdering finnes | vurderingen står (grunn skriver ikke over) |
| Stengt dag, raden finnes | lørdag, fredagens rad | raden står, utskriften sier det |
| Over midnatt | klokka på neste dag | stopp, melding, kode 1, ingen rad for neste dag |
| Basen feiler | | 0 vurderinger, melding, kode 1 |
| Utenfor kalenderen | 2027 | stopp før første kall, 0 kall |
| `--les-inn` | | 0 vurderinger |

</frozen-after-approval>

## Code Map

- `src/signalberegning.py` -- `beregn_signal` (l. 252), `Sjekk.maaling`/`grense`. Ny `vurder(rader, dato)`. Importerer `vurderingsdata` (port, løvnode).
- `src/fetch_prices.py` -- `kjoer` (l. 335), `skriv_til_basen` (l. 248, returnerer i dag `bool`), `les_inn` (l. 399), `main` (l. 444). Ny `skriv_vurderinger`.
- `src/lagring_sqlite.py` -- `SqliteVurderingslager(tilkobling, klokke)`, `skriv` gir `False` når en grunn ikke får skrive over. Endres ikke.
- `src/vurderingsdata.py`, `src/boersdag.py` -- endres ikke.
- `tests/test_fetch_prices.py` -- `falsk_serie` slutter 30.07, `serie_til(siste, dager)`, `stier`, `lager_i`, `antall_rader`. `test_foerste_henting_…` (l. 699) venter `vurdering == 0` og må få 15.
- `tests/test_signalberegning.py` -- tester for `vurder`. `tests/test_konsumentene.py` -- låser importen.
- `README.md` (l. 68–76), spinen (diagrammet l. 78–113, teksten l. 116–125, AD-17), `deferred-work.md` (midnatt, l. 40–42).

## Tasks & Acceptance

**Execution:**
- [ ] `src/signalberegning.py` -- `vurder` -- den ene omformingen fra `Signal` til `Vurdering | Grunn`
- [ ] `src/fetch_prices.py` -- dato før vakten, `skriv_til_basen` gir de skrevne symbolene, `skriv_vurderinger`, klokke og midnatt, `main` gir `naa` -- vurderingen i samme kjøring
- [ ] Testene og mutantene i Verification
- [ ] `README.md`, spinen, `deferred-work.md` -- regel 19 og pila

**Acceptance Criteria:**
- Given en falsk kilde og en base på disk, when `kjoer` går, then `Vurderingslager.les` gir 15 rader, og målingene er lik `beregn_signal` av serien i basen.
- Given en base med en eldre serie, when `kjoer` går, then vurderingen er regnet av den nye.
- Given en klokke som går over midnatt, when vurderingene skal skrives, then kjøringen stopper med kode 1 og ingen rad for neste dag.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q` -- grønn. Før: 1047 i CI på main, kjøring 36932258136 (1031 passed og 16 skipped lokalt).

**Mutantene**, én om gangen, koden satt tilbake fra en kopi i scratchpad, ikke med `git checkout`:
1. `standardavvik` og `dagens_endring` byttet om. 2. Vurderingen regnes før kursene er skrevet. 3. Et feilet symbol gir ingen rad. 4. Datokontrollen i `vurder` fjernet. 5. `ValueError` fanges ikke i `vurder`. 6. `WHERE`-leddet i `_UPSERT` fjernet. 7. Datoen leses på nytt for hvert symbol. 8. Midnattsjekken fjernet. 9. `les_inn` skriver vurderinger. 10. `slutt` i utskriften. 11. Vurderingene skrives når basen har feilet. 12. Raden for en stengt dag skrives over. 13. Datoen regnes etter kallene.
