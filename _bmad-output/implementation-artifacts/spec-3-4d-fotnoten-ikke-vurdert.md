---
title: 'Story 3.4 (3.4d): fotnoten for «ikke vurdert» i demoen og den ekte versjonen'
type: 'feature'
created: '2026-10-22'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f4f0875'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-4c-historikken-i-demoen.md'
---

## Intent

**Problem:** fotnoten for «ikke vurdert» sier at hentekommandoen ikke har skrevet en vurdering, «for eksempel fordi kursene er lest inn med `--les-inn`». I demoen, der vurderingene starter 21.09 (3.4c), stemmer ikke det (ECH2, åpent punkt i spesifikasjonen 3.4c).

**Grunnlaget:** gruppens svar 22.10 kl. 20:11 under story 3.4 i `epics.md`, med tekstene ordrett. Den ekte versjonen: «Ikke vurdert»: signalet lagres bare den kvelden kursene hentes, og regnes aldri ut bakover. Det gjelder dagene før første henting, og dager der kursene er lest inn med --les-inn. Demoen: «Ikke vurdert»: i demoen starter vurderingene mandag 21.09, slik den ekte versjonen har signal fra første henting. Datoen i demoteksten kommer fra `STARTDAG` i `src/demo.py`. Instruksjonen er den kl. 20:13 i dagsfila 22.10.

## Slik er det i dag (slått opp 22.10 på `f4f0875`)

- **Fotnoten står to steder:** `src/templates/aksje.html` (siden for en dag uten vurdering, når dagen har kurs, `detalj.ikke_vurdert`) og `src/templates/index.html` (under tabellen, når en rad er «ikke vurdert»). Begge sier: «Ikke vurdert»: hentekommandoen har ikke skrevet en vurdering for dagen, for eksempel fordi kursene er lest inn med `--les-inn`.
- **Malene vet at det er demoen** gjennom `eksempeltall`, som `_eksempeltall` i `src/app.py` gir hver side (demomerket i basen). `aksje.html` og `index.html` bruker det alt for «Demo Børs».
- **`docs/hjelp.md` og `src/hjelpetekster.py`** sier ikke det fotnoten sier. Hjelpen sier at en dag uten vurdering står med «–» og grunnen, og at demoen starter vurderingene 21.09.

## Kontrollpunktene

- a) Fotnoten begge steder, med den ekte teksten i den ekte versjonen og demoteksten i demoen. Datoen i demoteksten kommer fra `STARTDAG`, gjennom `_eksempeltall` i `app.py`, med ukedagen. Bildene tas på nytt bare hvis testene krever det.
- b) Testene, med «Ville feilet hvis», uten nett, på aksjesiden for en dag før startdagen og på oversikten.

## Planen, én commit per punkt

1. a) `demo_startdag` i `_eksempeltall`, «mandag 21.09» regnet fra `STARTDAG`, og fotnoten i de to malene. Avtrykkene bak bildene følger med, med grunnen, så hver commit er grønn.
2. b) De nye testene.

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter: den ekte teksten i demoen, demoteksten i den ekte versjonen, og en fast dato i stedet for `STARTDAG`.

*Lagt til 2026-10-23:* M1–M3 ble fanget på `8dcde6d` 22.10, i en fersk klon som ble slettet etterpå. Instruksjonen 23.10 kl. 12:59 (punkt c) la til to, kjørt på `abdb110` i en klon med `core.autocrlf=false`, med `tests/test_boersometer.py` og `tests/test_demo.py`, og så med hver ny test alene (`-k`). Begge ble fanget, og sha256 var lik HEAD etter hver:

| # | Mutant | Først i filene | Alene |
|---|---|---|---|
| c M1 | Datoen skrevet fast i `_fotnote_ikke_vurdert.html` i stedet for `{{ demo_startdag }}` | `TestFotnoten::test_datoen_i_fotnoten_kommer_fra_startdag` | `test_datoen_paa_sidene_kommer_fra_startdag[/aksje/KVST?dag=2026-09-18]` |
| c M2 | Fotnoten borte fra `boersometer.html` | `TestFotnoten::test_demoen_foer_startdagen_har_fotnoten` | `test_den_ekte_versjonen_har_den_ekte_teksten` |

## Gjennomgangen 22.10

Gjennomgang 22.10, ferdig kl. 21:27, på diffen `f4f0875..8dcde6d`. Linsene var Blind Hunter (BH, 5 funn), Edge Case Hunter (ECH, 4 funn) og Verification Gap (VG, 6 funn), hver for seg og uten å endre noe i repoet. 15 funn ble 11 rader. To hadde dom medium, VG1 og VG2, og begge er rettet 23.10 etter instruksjonen kl. 12:59.

| # | Funn | Dom | Rute |
|---|---|---|---|
| VG1 | En dato skrevet fast i malene i stedet for `{{ demo_startdag }}` ble ikke fanget, fordi sidetestene sammenlignet med «mandag 21.09» | medium | rettet i `abdb110` (c): sidene testes med en annen `STARTDAG`, og mutanten c M1 ble fanget |
| VG2 | `demo_startdag` hadde sin egen `UKEDAGER` og sitt eget datoformat, mens `ukedag` og `dato` i `tallformat.py` finnes (regel 21) | medium | rettet i `0565b92` (a), og teksten er den samme |
| BH1, VG3 | Testene av den ekte teksten sjekket bare første del | low | rettet i `16a5c9e` (b): hele teksten |
| BH2, ECH4, VG4 | Sjekken av `--les-inn` sto to ganger, og `and` skjulte hvilken halvdel som feilet | nit | rettet i `16a5c9e` (b): én sjekk av hele teksten |
| ECH2 | Den ekte teksten nevnte ikke en kveld uten henting | low | løst med gruppens svar 22.10 kl. 23:19, bygget i `16a5c9e` (b) |
| BH3, ECH1 | I demoen sier fotnoten at vurderingene starter 21.09, også for en rad som mangler etter 21.09, og testen av oversikten låser den teksten | low | uten endring: en demobase fra demokommandoen har en rad for hver aksje hver børsdag fra `STARTDAG`; føres under «Åpent» |
| VG5 | Kommentarene ved avtrykkene sier «byte for byte det samme», uten bilder i diffen | low | uten endring: bildene ble tatt på nytt 22.10 og var like (Utført-linja kl. 21:30), og igjen etter hvert punkt 23.10 |
| VG6 | `docs/hjelp.md` skriver startdagen for hånd | low | uten endring: hjelpen leses av brukere, og flyttes `STARTDAG`, rettes hjelpen i samme commit (regel 19) |
| ECH3 | En base med demomerket der den ekte skal ligge, uten `OSE_DEMO`, får demoteksten | nit | uten endring: det samme som merket «Eksempeltall» på siden |
| BH4 | Spesifikasjonen sto på `ready-for-dev` | nit | rettet: `in-review` |
| BH5 | `demo_startdag()` regnes ved hver forespørsel | nit | uten endring: det koster nesten ingenting |

## Åpent

- **Demoteksten for en rad som mangler etter 21.09** (BH3, ECH1): fotnoten i demoen forklarer en rad «ikke vurdert» med startdagen, også når raden er fra etter 21.09. Demokommandoen lager ikke en slik base, men testen av oversikten sletter en rad 09.10 og låser teksten.

## Det som ikke endres

- Hentingen, lagrene og demodataene. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` røres ikke, og demobaser lages bare i midlertidige mapper. Grenen for 2.3c røres ikke.
