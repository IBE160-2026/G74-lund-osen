---
title: 'Story 4.2: KILogg-porten med minneimplementasjon'
type: 'feature'
created: '2026-10-15'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'de94bc9'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** KI-laget trenger én logg for det KI la til, før modellen kalles (story 4.2 i `epics.md`, FR-604, FR-605). Uten loggen fra første kjøring finnes ikke uka briefen krever, og en tekst kan ikke knyttes til prompten og modellen som laget den.

**Approach:** `src/kilogg.py` er porten: typene `Emne` og `KIRad` med kontrollene, og protokollen `KILogg` med bare `skriv`, `les` og `les_alle` (AD-3, AD-7). `src/kilogg_minne.py` er `MinneKILogg`, som hele porten prøves mot uten database. SQLite-adapteren er story 4.3. PR B i planen for KI-laget.

## Planen

Planen for KI-laget ble vist i chatten 15.10 kl. 15:43 og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-15.md` (`5ce64f6`). Testtallet før: 1633 bestått og 17 hoppet over på main (`de94bc9`).

## Svarene

*Lagt til 2026-10-15 (gruppens svar på de ti spørsmålene i planen, instruksjonen kl. 15:53):* svarene er beslutninger. Alle ti står under Epic 10 i `epics.md`. De som gjelder denne storyen:

- Svar 2: raden står når den finnes, også når modellen feilet (FR-604). `skriv` gir da `False` uten å reise.
- Svar 6: loggen gir plass til dagsteksten i 10.6, med en dato som eneste emne. Et emne er derfor en aksje og en dato (plan B), en melding (plan A) eller dagen alene. Kontrollpunktet i 4.2 om at en rad med ingen av dem avvises, gjelder aksje og melding. Dagen er et eget slag, så den må velges uttrykkelig (`Emne.dagen`).

**Mutantene** (planen kl. 15:43): K1 promptversjon kan mangle; K2 begge emnene godtas; K3 porten har `slett`; K4 en eldre dato godtas; K5 en rad som finnes, skrives over.

## Boundaries & Constraints

- Porten importerer ikke kjernen (AD-3), som `vurderingsdata.py`. Kontrollen av datoen ligger i implementasjonen.
- Ingen database, ingen migrasjon og ingen endring i hentingen. Ingen API-kall.
- «av» er ikke en tjeneste i raden: med KI av skrives ingen rad (svar 5).

## I/O & Edge-Case Matrix

| Inndata | Forventet |
|---|---|
| En rad uten promptversjon eller modell, eller med tom tekst i dem | `UgyldigKIRad` |
| Et emne med både symbol og melding, eller et felt slaget ikke har | `UgyldigKIRad` |
| `besto=True` uten tekst eller med grunn, eller `besto=False` uten grunn | `UgyldigKIRad` |
| Modellen feilet: ingen tekst, `besto=False` og en grunn | raden godtas |
| `skriv` med en annen dato enn inneværende børsdag | `ValueError`, ingenting skrevet |
| `skriv` for et emne som finnes | `False`, den første raden står |
| `les_alle` | alle slag, ordnet etter dato og så rekkefølgen de ble skrevet i |

</frozen-after-approval>

## Code Map

- `src/kilogg.py`: `Emne`, `KIRad`, `UgyldigKIRad` og protokollen `KILogg`.
- `src/kilogg_minne.py`: `MinneKILogg`.
- `tests/test_kilogg.py`: testene for kontrollpunktene.

## Spec Change Log

## Commitene

Grenen `4-2-kilogg`, PR #45: `39ff578` spesifikasjonen og 4-2 til in-progress; `4c4d1b9` porten, `MinneKILogg` og testene; `49de30e` rettingene fra gjennomgangen.

## Review Triage Log

Gjennomgang 15.10 på diffen `main...4c4d1b9`, med Blind Hunter (BH, 15 funn), Edge Case Hunter (ECH, 15) og Verification Gap (VG, 4). Rettingene står i `49de30e`, og punktet i `deferred-work.md` i samme commit som denne triagen. Ingen funn må avgjøres av gruppen.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH2, ECH, VG4 | Grunnlaget var bare fryst på øverste nivå, så en liste eller mapping inni kunne endres etter at raden var skrevet | medium | patch: `_frys` på alle nivåer, mapping til `MappingProxyType` og liste til `tuple` |
| BH3, ECH | Nøkler som ikke er tekst inni grunnlaget, og tupler, ble endret av JSON i stedet for å avvises | medium | patch: `_frys` godtar bare det JSON kan holde uten å endre det |
| BH1, ECH | «EQNR», «eqnr» og «EQNR » var tre ulike emner, så samme aksje kunne få to rader | medium | patch: symbol og melding-id uten mellomrom, og symbolet med store bokstaver |
| BH5, ECH | Feil dag, en klokke uten sone, `UtenforKalenderen` og en ugyldig rad var alle `ValueError` | medium | patch: `IkkeInnevaerendeBoersdag` for feil dag, og `TypeError` for en klokke uten sone |
| VG1 | Ingen test så at `les_alle` ordner etter dato, fordi radene ble skrevet i datorekkefølge | low | patch: `test_ordnet_etter_dato_ikke_etter_skrivingen` |
| VG2, BH12 | Ingen test så at dagen regnes i Oslo, eller en helligdag | low | patch: `test_dagen_regnes_i_oslo`, `test_en_helligdag_hoerer_til_dagen_foer`, `test_klokke_uten_sone_avvises` |
| VG3 | Ingen test så at `temperatur` blir `float` | low | patch: `type(rad.temperatur) is float` |
| BH4, ECH | `regelen` kunne være tom | low | patch: må være tekst som ikke er tom |
| BH8, ECH | Maskinvaren og Ollama-versjonen ble godtatt for en tjeneste på nettet | low | patch: bare for `lokal` (FR-605). For `lokal` kan de mangle, fordi de ikke kan vites når Ollama ikke kjører |
| BH9, ECH | `hash(rad)` ga `TypeError`, fordi grunnlaget ikke kan hashes | low | patch: `field(hash=False)` på grunnlaget, `test_raden_kan_hashes` |
| BH10, ECH | «Modellen feilet» og «besto ikke kontrollen» kunne bare skilles på fritekst | low | patch: `modellen_feilet` er `tekst is None`, og testene viser begge |
| BH15, ECH | En seed utenfor 64 bit ble godtatt, og ville feilet i SQLite (4.3) | low | patch: grensen i `KIRad` |
| ECH | `temperatur=10**400` ga `OverflowError`, og et svært dypt grunnlag `RecursionError` | low | patch: begge gir `UgyldigKIRad` |
| ECH | `les` sjekket ikke typen | low | patch: `TypeError` |
| BH6 | Porten sa ikke hva nøkkelen er | low | patch: hele emnet, i docstringen, og `test_dagen_og_meldingen_har_ogsaa_bare_en_rad` |
| BH7 | Testene for porten kunne ikke brukes av adapteren i 4.3 | low | patch: fixturen `logg_lager` |
| BH11 | Testen for «ingen slett» så ikke etter `__delitem__` eller endring gjennom lista fra `les_alle` | low | patch: begge testet |
| BH13 | Klokka ble ikke sjekket før første `skriv` | low | patch: `TypeError` i `__init__` hvis den ikke kan kalles |
| BH14 | Verification var tom | low | patch: fylt ut under |
| ECH | Passerer hentingen midnatt mellom modellkallet og `skriv`, reiser `skriv` for resten | low | utsatt: `deferred-work.md`, tas i 10.2b, der hentekommandoen kaller `skriv` |
| ECH | En klokke etter 2026 gir `UtenforKalenderen` ved hver `skriv` | avvist | slik virker kalenderen overalt (`boersdag.py`): den gjetter ikke en dag lista ikke dekker |
| BH15 (del) | `temperatur` har ingen øvre grense | avvist | grensen er tjenestens. Raden logger det som ble brukt |


## Verification

**Commands:**
- `uv run pytest -q` -- før 1633 bestått og 17 hoppet over på main (`de94bc9`). 1695 og 17 på `4c4d1b9`. Etter rettingene 1721 og 17 på `49de30e`.

**Mutantene**, kjørt én om gangen med `-x` og bare `tests/test_kilogg.py`, med kopi før og sha256 mot HEAD etter hver. Fila var lik HEAD etter hver. K1–K5 ble først kjørt på `4c4d1b9` og fanget alle, og så på nytt på `49de30e` med KR1–KR6. Alle er fanget:

| # | Mutant | Fanget av |
|---|---|---|
| K1 | promptversjon kan mangle | `test_promptversjon_og_modell_kan_ikke_mangle` |
| K2 | begge emnene godtas | `test_begge_emnene_avvises` |
| K3 | porten har `slett` | `test_bare_skriv_og_lesemetoder` |
| K4 | en eldre dato godtas | `test_bare_inneveerende_boersdag` |
| K5 | en rad som finnes, skrives over | `test_raden_staar_naar_den_finnes` |
| KR1 | lister i grunnlaget kan endres | `test_grunnlaget_er_en_kopi_som_ikke_kan_endres` |
| KR2 | symbolet med små bokstaver godtas | `test_samme_noekkel_kan_ikke_skrives_paa_to_maater` |
| KR3 | dagen regnes ikke i Oslo | `test_dagen_regnes_i_oslo` |
| KR4 | `les_alle` i rekkefølgen radene ble skrevet | `test_ordnet_etter_dato_ikke_etter_skrivingen` |
| KR5 | maskinvaren godtas for en tjeneste på nettet | `test_maskinvaren_og_ollama_bare_for_den_lokale` |
| KR6 | `regelen` kan være tom | `test_ugyldige_verdier` |
