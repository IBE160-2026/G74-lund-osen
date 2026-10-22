---
title: 'Story 3.4 (3.4c): historikken i demoen som den ekte'
type: 'feature'
created: '2026-10-22'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '5ff304f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/ux-logg.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-7b-signalet-dag-for-dag.md'
---

## Intent

**Problem:** demoen har en vurdering for hver aksje hver børsdag fra 02.01.2026, så «Signalet dag for dag» viser signal hele året. Den ekte versjonen har signal bare fra første henting, og «ikke vurdert» før.

**Grunnlaget:** avgjørelsen 21.10 kl. 23:09 under «Prioritering» og story 3.4 i `epics.md`: «historikken i demoen («Signalet dag for dag», 2.7b) viser det samme bildet som den ekte: signal bare fra en startdag noen uker før siste demodag, og «ikke vurdert» før. Det må passe med de 10 fargekombinasjonene på siste demodag (avgjørelsen 16.10 kl. 21:49, 3.4) og KI-tekstene i demoen (3.4b).» U45 i `docs/ux-logg.md`, og gruppens svar 22.10 kl. 18:20 om å ta den nå, før 8.6. Instruksjonen er den kl. 19:31 i dagsfila 22.10. Bare demoen endres.

## Slik virker det i dag (slått opp 22.10 på `5ff304f`)

- **`_bygg` i `src/demo.py`** skriver kursene for alle 195 handelsdagene fra `FOERSTE_DAG` (02.01) til `SLUTTDATO` (09.10), og så, for hver handelsdag og hver aksje, det `vurder()` gir for serien fram til dagen, med `SqliteVurderingslager` og lagerets klokke stilt på dagen kl. 22:30 (`_klokke_for`, AD-7, merknaden 2026-10-03). KI-radene skrives for `SLUTTDATO` med klokka stilt på den dagen.
- **Den ekte versjonen** skriver en vurdering bare for inneværende børsdag (AD-7), så dagene før første henting har ingen rad. Historikken går gjennom `les_tilstand`, og en dag med kurs uten rad står uten signal. `docs/hjelp.md`: «En dag uten vurdering står med «–» og grunnen, og dagene før første og etter siste kurs står tomme. Det gjelder både demoen og den ekte versjonen.»
- **En demobase fra før** lages på nytt i Docker hver gang demoen starter (`demo-lag` i `compose.yaml` kjører `src/demo.py`). Med uv lages den bare når `uv run python src/demo.py` kjøres, og webserveren lager den aldri (AD-10). En demobase fra før denne endringen kan altså bli vist med den gamle historikken når demoen startes med uv.

## Kontrollpunktene

- a) Demoen: vurderingene skrives bare fra mandag 21.09.2026 (`STARTDAG`), tre uker før siste demodag fredag 09.10. Dagene før står uten signal, slik den ekte viser dagene før første henting. Kursene, de 10 fargekombinasjonene på 09.10 og KI-tekstene for 09.10 er som før. En demobase fra før endringen, med en vurdering før `STARTDAG`, vises ikke: webserveren sier at den er laget av en eldre versjon av demoen, og viser kommandoen som lager den på nytt. README-en, `docs/hjelp.md` og hjelpetekstene følger med der de sier noe om historikken i demoen (regel 19), og bildene tas på nytt bare hvis testene krever det.
- b) Testene, med «Ville feilet hvis», uten nett.

## Planen, én commit per punkt

1. a) `STARTDAG` og løkka i `_bygg`, docstringen i `demo.py`, `gammel_demobase` i `demo.py`, og i `app.py` at en demobase fra før vises som «laget av en eldre versjon», med en egen setning i `index.html`. Fingeravtrykkene av demobasen i `tests/test_demo.py` og avtrykkene bak bildene i `tests/test_docker.py` følger med, med grunnen, i samme commit, så hver commit er grønn. Tekstene.
2. b) De nye testene.

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter:

- **M1:** en vurdering før startdagen.
- **M2:** en børsdag etter startdagen uten vurdering.
- **M3:** startdagen flyttet.

## Avgjort underveis

- **«Signal hele året»** under «Intent» er unøyaktig (VG3): demoen hadde en rad i `vurdering` for hver børsdag fra 02.01, men U45 i `docs/ux-logg.md` sier at signalet startet 13.03, fordi MA50 trenger 51 dager. Begge sier at det var rader fra 02.01.
- **En demobase fra før** gjenkjennes på dataene: en rad i `vurdering` før `STARTDAG` (`gammel_demobase` i `demo.py`). Webserveren sier at den er laget av en eldre versjon og viser kommandoen som lager den på nytt, både med demobryteren og når en demobase ligger der den ekte basen skal ligge (`c60be34`, BH1). Aksjesiden gir 404 som når demobasen mangler.
- **Fingeravtrykket av vurderingene** før siste dag (`FINGERAVTRYKK_VURDERING_FOER_SISTE_DAG` i `tests/test_demo.py`) er nytt, fordi radene før 21.09 er borte. Fingeravtrykkene av kursene står. Avtrykkene bak bildene er nye, fordi `demo.py`, `app.py` og `index.html` er endret; bildene ble tatt på nytt og er byte for byte de samme.
- **`test_hver_vurdering_er_det_vurder_gir`** sjekker dagene fra `STARTDAG`, med grunnen i docstringen.

## Mutantene, kjørt

I en fersk klon med `core.autocrlf=false`, slettet etterpå, én om gangen med `-x`, med kopi før og sha256 lik HEAD etter hver. Kjørt på `c137b66` og igjen på `c60be34`, med `tests/test_demo.py`, og en gang til med bare `TestHistorikkenSomDenEkte` (`-k`) (VG1).

| # | Mutant | Først i fila (`c60be34`) | `TestHistorikkenSomDenEkte` alene |
|---|---|---|---|
| M1 | En vurdering før startdagen (fra 18.09) | `test_hver_vurdering_er_det_vurder_gir` | `test_ingen_vurdering_foer_startdagen` |
| M2 | En børsdag etter startdagen uten vurdering (30.09) | `test_hver_vurdering_er_det_vurder_gir` | `test_en_rad_per_aksje_hver_boersdag_fra_startdagen` |
| M3 | Startdagen flyttet til 28.09 | `test_froeet_og_de_andre_dagene_staar_som_foer` | `test_startdagen` |

## Gjennomgangen

Gjennomgang 22.10 på diffen `5ff304f..c137b66`. Linsene var Blind Hunter (BH, 6 funn, bare diffen), Edge Case Hunter (ECH, 5 funn, prøvd mot demobaser i midlertidige mapper) og Verification Gap (VG, 5 funn), hver for seg og uten å endre noe i repoet. 16 funn ble 11 rader. To hadde dom medium, og begge er rettet i `c60be34`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH3, VG2 | En demobase fra før der den ekte basen skal ligge, ble vist med den gamle historikken | medium | rettet: samme sjekk og melding der, og testet |
| ECH1, BH6 | Hjelpen sa at en demobase fra før 20.10 gir `RuntimeError`, men nå kommer meldingen om en eldre versjon | medium | rettet i hjelpen |
| BH4, ECH4, VG5 | Testen av en demobase fra før så ikke på Min liste, eller på en ny demobase | low | rettet |
| VG1 | Mutantene var ikke ført | low | rettet: tabellen over |
| VG3 | «Signal hele året» stemmer ikke med U45 | low | rettet under «Avgjort underveis» |
| VG4 | «aksjene har signal fra 21.09» stemmer ikke for VRDS og MTFJ | nit | rettet: «vurderingene starter» |
| BH3 | Ingen versjon av demoen i basen, bare dataene | low | avvist: `application_id` er demomerket og `user_version` er migrasjonene; dataene skiller en demobase fra før, og et eget merke vurderes ved neste endring av demoen |
| ECH2 | Siden for en dag før 21.09 i demoen sier at hentekommandoen ikke har skrevet en vurdering, «for eksempel fordi kursene er lest inn med `--les-inn`» | low | uten endring: teksten er felles med den ekte versjonen og står i `aksje.html` bak bildet; føres under «Åpent» |
| BH2 | `/aksje/<symbol>` gir 404 uten melding for en demobase fra før | low | uten endring: som når demobasen mangler, og forsiden og Min liste sier fra |
| ECH5 | Stjernen på en åpen side med en demobase fra før gir 404 | nit | uten endring: som BH2 |
| BH5 | Spørringen etter en gammel rad går ved hver forespørsel | nit | uten endring: 225 rader i en ny demobase |

## Åpent

- **Fotnoten på siden for en dag uten vurdering** i demoen viser til hentekommandoen og `--les-inn` (ECH2). En egen tekst for demoen kan komme i en liten PR.

## Det som ikke endres

- Den ekte versjonen, hentingen og lagrene. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` røres ikke (regel 22), og demobaser lages bare i midlertidige mapper.
- Grenen for 2.3c røres ikke.
