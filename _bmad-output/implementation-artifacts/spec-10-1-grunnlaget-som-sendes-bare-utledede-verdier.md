---
title: 'Story 10.1: Grunnlaget som sendes — bare utledede verdier'
type: 'feature'
created: '2026-10-15'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'a2f71ae'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/docs/kilder-og-rettigheter.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Det som sendes til modellen, må være bestemt av én ren funksjon, så ingen kan sende rådata ved et uhell (story 10.1 i `epics.md`, betingelse 4 og merknaden 04.10 i 4.1, `prd.md` §4.6).

**Approach:** `ki_grunnlag(kilde)` i `src/ki_grunnlag.py` tar et `Signal` eller en `Vurdering` og gir fortegnet for de tre sjekkene, styrken og retningen, og ingenting annet. En aksje utenfor de 15 (FR-412) får merket «Utenfor målingen». Grunnlaget er det `KIRad.grunnlag` lagrer (4.2). Ingen modell kalles. PR D i planen for KI-laget.

## Planen

Planen for KI-laget ble vist i chatten 15.10 kl. 15:43 og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-15.md` (`5ce64f6`). Testtallet før: 1721 bestått og 17 hoppet over på main (`a2f71ae`).

## Svarene

*Lagt til 2026-10-15 (gruppens svar på de ti spørsmålene i planen, instruksjonen kl. 15:53):* svarene er beslutninger. Alle ti står under Epic 10 i `epics.md`. Det som gjelder denne storyen:

- Svar 10: «antall» gjelder dagsteksten i 10.6, og 10.1 sender ikke antall. Ført også under §4.6 i PRD-en.

**Mutantene** (planen kl. 15:43): G1 `dagens_endring` med; G2 `volumforhold` med; G3 sluttkursen med; G4 styrken som desimaltall.

## Boundaries & Constraints

- Ren logikk: ingen I/O, ingen modell, ingen endring i hentingen. Ingen API-kall.
- Ingen kurser, volumer, prosenter, forholdstall eller målinger, og ingen antall (beslutningen 04.10, svar 10).

## I/O & Edge-Case Matrix

| Inndata | Forventet |
|---|---|
| `Signal` fra `beregn_signal` | `trend`, `bevegelse`, `interesse`, `styrke` og `retning` |
| `Vurdering` fra samme serie | det samme |
| `utenfor_maalingen=True` | de samme verdiene og `merke: «Utenfor målingen»` |
| En sjekk med ukjent navn, eller styrke utenfor 0–3 | `ValueError` |
| Noe annet enn `Signal` eller `Vurdering` | `TypeError` |

</frozen-after-approval>

## Code Map

- `src/ki_grunnlag.py`: `ki_grunnlag`.
- `tests/test_ki_grunnlag.py`: testene for kontrollpunktene.

## Spec Change Log

## Commitene

Grenen `10-1-ki-grunnlag`, PR #47: `a1acaf9` spesifikasjonen og 10-1 til in-progress; `4e71a59` `ki_grunnlag` og testene; `8f22131` rettingene fra gjennomgangen; `2ae86b4` testen for retning utenfor lista, så den fanger GR2.

## Review Triage Log

Gjennomgang 15.10 på diffen `main...4e71a59`, med Blind Hunter (BH, 16 funn), Edge Case Hunter (ECH, 8) og Verification Gap (VG, 4). Rettingene står i `8f22131`. Ingen funn må avgjøres av gruppen.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, BH2, ECH, VG4 | `int()` gjorde et desimaltall, en tekst eller `True` om til et gyldig heltall før kontrollen så det | high | patch: ingenting gjøres om. `type(v) is int` og området, ellers `ValueError`. `test_fortegn_som_ikke_er_heltallet_minus_1_0_eller_1`, `test_styrke_som_ikke_er_et_heltall_fra_0_til_3` |
| VG1 | Testserien ga +1 på alle tre sjekkene, så en ombytting eller et tapt fortegn ble ikke sett | medium | patch: `TestFortegnene` med ulike fortegn, for `Signal` og `Vurdering` |
| BH5, ECH | Et dobbelt sjekknavn ga stille én av verdiene, og store og små bokstaver ble godtatt | medium | patch: sjekkene må være Trend, Bevegelse og Interesse, én av hver og i den rekkefølgen |
| ECH | Styrken og retningen i et `Signal` ble ikke sjekket mot sjekkene, som `Vurdering` gjør | medium | patch: `_samsvar` med `finn_styrke` og `finn_retning` |
| BH3, BH4 | Kontrollen så ikke på nøklene eller merket | medium | patch: nøklene må være de fem, og merket kan bare være «Utenfor målingen» |
| VG2, VG3 | Ingen test ga en retning utenfor lista eller et fortegn utenfor -1..1 | medium | patch: `test_retning_utenfor_den_lukkede_lista` og testen for fortegnene |
| BH6 | Merket hadde `False` som standard og kunne glemmes | low | patch: `utenfor_maalingen` må oppgis, `test_merket_maa_oppgis` |
| BH7, ECH | Grunnlaget var en vanlig dict som kunne endres etter kontrollen | low | patch: `MappingProxyType` |
| BH9 | Feilene tok med verdien, som kan være en rå verdi (regel 16) | low | patch: feilene nevner bare feltet og typen, `test_feilen_nevner_ikke_verdien` |
| BH16 | `retning` ble ikke krevd som `str` | low | patch: `type(retning) is str` |
| BH8, ECH | `None` eller `inf` ga en annen feil enn `ValueError` | low | patch: typen sjekkes først, så de gir `ValueError` |
| BH10 | Testen for kurs og volum var delvis tautologisk | low | patch: nøkkelsettet og typene er nå testet for begge kildene, og testene for desimaltall og typer fanger det testen ikke gjorde |
| BH11, BH12, BH14 | Flere grener i kontrollen hadde ingen test, og Verification var tom | low | patch: testene over, og Verification under |
| BH13 | `epic-10` står som backlog mens 10-1 er in-progress | avvist | slik står epicene i `sprint-status.yaml` i dag, også `epic-8` med ferdige storyer |
| BH15 | Modulen sier «plan B», spesifikasjonen «PR D i planen for KI-laget» | avvist | begge stemmer: plan B er Epic 10, og PR D er nummeret i planen 15.10 |


## Verification

**Commands:**
- `uv run pytest -q` -- før 1721 bestått og 17 hoppet over på main (`a2f71ae`). 1734 og 17 på `4e71a59`. Etter rettingene 1763 og 17 på `8f22131`.

**Mutantene**, kjørt én om gangen med `-x` og bare `tests/test_ki_grunnlag.py`, med kopi før og sha256 mot HEAD etter hver. Fila var lik HEAD etter hver. G1–G4 ble først kjørt på `4e71a59` og fanget alle, og så på nytt på `8f22131` med GR1–GR4. GR2 overlevde først, fordi `_samsvar` også avviser en retning utenfor lista. Testen sjekker nå at det er kontrollen av lista som stopper den (`2ae86b4`), og GR2 ble kjørt på nytt og fanget. Alle er fanget:

| # | Mutant | Fanget av |
|---|---|---|
| G1 | `dagens_endring` med | `test_signalet_gir_bare_fortegn_styrke_og_retning` (kontrollen av nøklene reiser) |
| G2 | `volumforhold` med | samme |
| G3 | sluttkursen med | samme |
| G4 | styrken som desimaltall | samme |
| GR1 | fortegnet rundes av til et heltall | `test_fortegn_som_ikke_er_heltallet_minus_1_0_eller_1` |
| GR2 | retning sjekkes ikke mot lista | `test_retning_utenfor_den_lukkede_lista` |
| GR3 | sjekkene slås opp på navn uten kontroll | `test_sjekkene_maa_vaere_de_tre_en_av_hver` |
| GR4 | et `Signal` som ikke stemmer med sjekkene, godtas | `test_et_signal_som_ikke_stemmer_med_sjekkene` |
