---
title: 'Story 2.3: Børsdagskontroll før kvoten brukes'
type: 'feature'
created: '2026-10-07'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '7d03d8ea74e9d3d74947c78e4aa3a24988ce6b85'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-2-hentekommandoen-som-egen-inngang.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-5-vurderingen-skrives-i-samme-kjoering.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Hentekommandoen bruker 15 kall hver gang den startes, med ett unntak: dagens fil finnes (AD-6). En kjøring før kl. 22:00 bruker dagens kall uten å få dagens rad, og en kjøring en lørdag bruker 15 kall på data basen alt har. Oppgaveplanlegging kan ikke starte den hver dag før den vet selv om det er noe å hente (FR-401, FR-402).

**Approach:** `kjoer()` sjekker i fast rekkefølge før første kall: klokka, tidskontrollen, basen, filvakten, nøkkelen og kvoten. Hver sjekk som sier nei, gir 0 kall og en utskrift som sier hvorfor. Øyeblikksbildet får navn etter børsdagen vurderingene skrives for (K8).

## Planen

Planen fra 05.10 kl. 17:35 ble gitt i chatten og finnes ikke i denne økta. Den er laget på nytt 07.10 fra storyen i `epics.md` (med gruppens svar kl. 19:17) og punktene i instruksjonen kl. 20:35 i `docs/ai-prompts/2026-10-07.md`. Mutantene M1–M8 er derfor nummerert her, ikke hentet fra planen kl. 17:35.

## Boundaries & Constraints

**Always:**
- **Rekkefølgen før første kall:** (1) klokka: `oeyeblikk` leses én gang (AD-20), og `dag` og `dato` (inneværende børsdag) regnes av den. (2) tidskontrollen. (3) basen. (4) filvakten. (5) nøkkelen. (6) kvoten. Nøkkelen leses først etter filvakten, så en kjøring som stopper tidligere, aldri leser `.env`. En test låser rekkefølgen.
- **Tidskontrollen:** er `dag` en børsdag og klokka i Oslo før 22:00, blir det 0 kall, og utskriften nevner `--hent-foer-kl-22`. Med flagget hentes det, og navnet blir dagens dato, som før. `argparse` med `allow_abbrev=False`, så `--hent` ikke gjelder som flagget. På en dag som ikke er børsdag gjelder ingen tidskontroll; basen avgjør.
- **Basen:** har hver aksje i `AKSJEUNIVERS` en kurs for `dato` i basen, blir det 0 kall, og utskriften sier at basen alt har dataene for børsdagen (FR-402). Mangler noen, hentes det (AD-7: raden for `dato` kan fortsatt skrives). Basen åpnes for lesing med `aapne_base`. Kan den ikke åpnes eller leses, hentes det, og utskriften sier det: fila skrives først uansett (AD-6), og den kan leses inn senere med `--les-inn`.
- **Filvakten (K8):** fila heter `kurser-raa-<dato>.json`, der `dato` er børsdagen vurderingene skrives for, ikke kjøredagen. Finnes den, stopper kjøringen med 0 kall som i dag (AD-6), også på en dag som ikke er børsdag, og utskriften sier hvorfor og at et nytt forsøk hører til 2.3b. Intervallet slutter fortsatt på kjøredagen.
- **Kvoten:** leses med `/api/user` gjennom en egen nettfunksjon `hent_kvote` i `fetch_prices.py`, injisert som `les_kvote`, etter nøkkelen og før første kall. Kallet er gratis (regel 15). Regnestykket:
  - `brukt` er `apiRequests`, men 0 når `apiRequestsDate` er før dagens dato i GMT (regel 15, presisert 04.10). Dagens dato i GMT regnes av `oeyeblikk`.
  - `igjen` er `dailyRateLimit − brukt`, aldri under 0.
  - `igjen ≥ 15`: hent. `igjen < 15` og `igjen + extraLimit ≥ 15`: hent, og utskriften sier hvor mange kall som tas fra bonusen (`15 − igjen`). Ellers: 0 kall, utskriften sier hvorfor, kode 1.
  - Kan svaret ikke leses (nettfeil, ikke JSON, et felt mangler eller er ikke et heltall, en dato som ikke kan leses): hent, og utskriften sier at kvoten ikke kunne leses. Feilteksten er bare typenavnet, som i `hent_ett_symbol` (story 2.0).
  - Navn, e-post og andre felt fra svaret står aldri i utskriften. Bare tallene over.
- **Utskrift og koder:** tidskontrollen, basen og filvakten gir kode 0 (ingenting å gjøre). Kvoten som ikke strekker til, gir kode 1, fordi dagen da ikke får data.
- **Spinen:** raden «Datoer» sier at datoen i navnet på et øyeblikksbilde er børsdagen vurderingene skrives for, og at dataene i fila kan være eldre når FR-402 slår til (API-et har ikke dagens kurs ennå). En merknad under AD-2: `/api/user` og `/api/eod` er to nettfunksjoner mot samme kilde, begge i `fetch_prices.py`, begge injisert.
- **Docstringen i `lagring_fil.py`** (`nyeste_snapshot`) sier det samme som spinen.
- **`CLAUDE.md`** får regel 22: en gren bruker bare testbaser, aldri `data/db/ose.db`.
- **README:** bare det som ellers blir feil: linjen om å kjøre hentingen mellom kl. 22 og midnatt.
- **K8** i `deferred-work.md` merkes løst i 2.3. **E9** venter på 2.4, med en datert linje.
- Ingen API-kall utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, heller ikke med `--les-inn`. Ingen test eller kjøring rører `data/db/ose.db`.

**Never:** nye forsøk for en dag som har fil (2.3b). Arbeidskopien jobben kjører fra og oppsettet i Oppgaveplanlegging (etter flettingen). Etterfylling og E9 (2.4). Indekskallet (2.8). Ingen fil i `data/raa/` får nytt navn.

</frozen-after-approval>

## I/O & Edge-Case Matrix

| Scenario | Tilstand | Forventet |
|---|---|---|
| Børsdag før 22:00 | Tirsdag 21:59 Oslo | 0 kall, nevner `--hent-foer-kl-22`, kode 0, nøkkelen ikke lest |
| Børsdag før 22:00 med flagget | Tirsdag 12:00, flagget | Henter, fila heter tirsdagens dato |
| Børsdag etter 22:00, basen har dagen | Alle 15 har kurs for tirsdag | 0 kall, kode 0 |
| Børsdag etter 22:00, basen mangler én | 14 av 15 har kurs for tirsdag | Henter |
| Lørdag, basen har fredag | Alle 15 har kurs for fredag | 0 kall |
| Lørdag, basen mangler fredag | Fredag mangler for noen | Henter, fila heter fredagens dato |
| Lørdag, fredagens fil finnes | `kurser-raa-<fredag>.json` | 0 kall, sier hvorfor, nevner 2.3b |
| Basen kan ikke leses | Ødelagt basefil | Henter, sier at basen ikke kunne leses |
| Kvote: nok igjen | 20 igjen | Henter, ingen bonuslinje |
| Kvote: under 15, bonus dekker | 10 igjen, `extraLimit` 463 | Henter, «5 kall fra bonusen» |
| Kvote: under 15, bonus dekker ikke | 10 igjen, `extraLimit` 2 | 0 kall, kode 1 |
| Kvote: gårsdagens tall | `apiRequests` 20, `apiRequestsDate` i går (GMT) | Henter, 20 igjen |
| Kvote: 01:00 norsk tid | `apiRequestsDate` lik dagens dato i GMT, som er gårsdagen i Oslo | Tallet teller |
| Kvote: kan ikke leses | Unntak, ikke JSON, felt mangler | Henter, sier det |
| Kvote: navn og e-post | Svaret har `name` og `email` | Står ikke i utskriften |

## Code Map

- `src/fetch_prices.py` -- `kjoer()` får sjekkene, `hent_foer_kl_22` og `les_kvote`. Nye funksjoner: `hent_kvote` (nettfunksjonen), `vurder_kvote` (regnestykket, ren), `basen_har_dagen`. `main()` får flagget og sender nøkkelen som funksjon. Docstringene følger.
  *Rettet 2026-10-08:* navnene i koden er `hent_kvote` (nettfunksjonen), `UlesbarKvote` og `tolk_kvote` (leser svaret, ren), `vurder_kvote(igjen, bonus, antall)` (regnestykket, ren, med antallet som parameter) og `manglende_i_basen` (aksjene som mangler børsdagen). `basen_har_dagen` finnes ikke. Varselet for svar uten børsdagen (FR-402) ligger i `kjoer()`.
- `src/lagring_fil.py` -- docstringen i `nyeste_snapshot` (K8).
- `tests/test_fetch_prices.py` -- nye klasser for tidskontrollen, basen, helgen, filvakten, kvoten og rekkefølgen. Matrisetestene som starter før 22:00 på en børsdag, får flagget.
- `ARCHITECTURE-SPINE.md` -- raden «Datoer», merknad under AD-2.
- `CLAUDE.md`, `README.md`, `deferred-work.md`, `sprint-status.yaml`.

## Tasks & Acceptance

**Execution:**
- [x] Spesifikasjonen. Commit og push (`acb3d90`).
- [x] Del 1: tidskontrollen, basen, filvakten med K8, nøkkelen sist, flagget. Tester. Commit og push.
- [x] Del 2: kvoten med `/api/user`. Tester. Del 1 og 2 ble én commit (`600096e`), fordi de ligger i de samme funksjonene.
- [ ] Del 3: spinen, `lagring_fil.py`, `CLAUDE.md`, README, `deferred-work.md`. Commit og push.
- [ ] Mutantene M1–M8 og kvote- og helgemutantene. PR mot main, gjennomgang (Blind Hunter, Edge Case Hunter, Verification Gap), CI grønn. Stopp før flettingen.

**Mutantene** (én om gangen, hele `tests/`):
- M1: tidskontrollen fjernet.
- M2: grensen `<` 22:00 byttet med `<=`.
- M3: basesjekken krever at bare én aksje har dagen (`any` i stedet for `all`).
- M4: filvakten sjekker `dag` i stedet for `dato` (K8 tilbake).
- M5: nøkkelen leses før tidskontrollen.
- M6: flagget ignoreres.
- M7: tidskontrollen gjelder også dager som ikke er børsdag.
- M8: en base som ikke kan leses, gir 0 kall.
- K1: `apiRequestsDate` sammenlignes med datoen i Oslo, ikke GMT.
- K2: bonusen telles ikke med.
- K3: et svar som ikke kan leses, gir 0 kall.
- K4: hele svaret skrives ut.

**Acceptance Criteria:**
- Given en lørdag og en base der alle har fredagens kurs, when kommandoen kjøres, then 0 kall, og nøkkelen er ikke lest.
- Given en lørdag og en base som mangler fredagen, when kommandoen kjøres, then fila heter fredagens dato og vurderingene skrives for fredag.

## Implementation Notes

**Stoppet 07.10 kl. 21:29, fristen var 21:40.** Det som er gjort:
- `src/fetch_prices.py`: `hent_kvote`, `UlesbarKvote`, `tolk_kvote`, `manglende_i_basen`, sjekkene i `kjoer()` i rekkefølgen fra spesifikasjonen, `--hent-foer-kl-22` med `allow_abbrev=False`, og nøkkelen gis til `kjoer()` som funksjon.
- `tests/test_fetch_prices.py`: 32 nye testkjøringer (tidskontrollen, basen, helgen, rekkefølgen, kvoten og `hent_kvote`). Fem eldre tester er tilpasset: matrisen fra 2.1 får flagget, egen base per øyeblikk og navnet etter børsdagen (K8). Tre tester fra 2.5 som kjører to ganger samme dag, slår av basesjekken (og for lørdagen filvakten), som et nytt forsøk i 2.3b. `test_main_skriver_fila_for_norsk_dato_uten_noekkel` får flagget. `uv run pytest tests/test_fetch_prices.py`: 163 passed og 16 skipped (før: 131 passed og 16 skipped i samme fil).
- **Hele suiten ble ikke ferdig.** `uv run pytest` gikk i over en halvtime uten utskrift og ble stoppet kl. 21:29. Det må undersøkes først i morgen: om en test i en annen fil henger på den nye koden (for eksempel `les_kvote` med `hent_kvote` som standard), eller om det var noe annet. `data/db/ose.db` er ikke endret (sist endret 06.10 kl. 22:17).

**Hele suiten, undersøkt 08.10 kl. 18:03–18:06** (instruksjonen kl. 18:03): `uv run pytest -o faulthandler_timeout=120` på grenen etter mergen av main (`ee79105`), i forgrunnen med en grense på 10 minutter. Den hang ikke: 1164 passed og 16 skipped på 92 s, og 75 s andre gang. faulthandler skrev ingenting. Hengen 07.10 er ikke gjenskapt, og årsaken er ikke funnet. Det som er sjekket: `kjoer()` har ingen løkke eller ventetid, og `requests.get` i `hent_kvote` har `timeout=30`. Funnet underveis: 40 kall til `fp.kjoer` i 34 tester i `test_fetch_prices.py` er uten `les_kvote` (telt med `ast`). De som kommer forbi filvakten, går mot nettet med `hent_kvote`. Sperren i `tests/conftest.py` avviser kallet med en gang, og `except Exception` i kvotesjekken sluker feilen og henter likevel. Det henger ikke, men sperren sees ikke i testene. Ført som funn til gjennomgangen. `data/db/ose.db` er ikke endret av kjøringene (sist endret 07.10 kl. 22:24, av kveldshentingen fra main).

**Gjenstår:** hele suiten grønn. Del 3 (spinen med raden «Datoer» og merknaden under AD-2, docstringen i `lagring_fil.py`, regel 22 i `CLAUDE.md`, README-linjen, K8 og E9 i `deferred-work.md`). Mutantene M1–M8 og K1–K4. PR, gjennomgang og CI. Kontrollen av `data/raa/`: navnene er lest. De ni kursfilene (22.–24.09, 29.09–02.10, 05.–06.10) har alle en børsdag i navnet, så de følger regelen. Ingen fil har fått nytt navn.

## Spec Change Log

- **2026-10-08, instruksjonen kl. 18:03 i `docs/ai-prompts/2026-10-08.md`: to ting fra planen 05.10 som manglet her.**
  - *Vintertid.* Etter 25.10 er kl. 22:30 i Oslo 21:30 UTC. En test henter tirsdag 27.10 kl. 21:30 UTC, og en test nekter tirsdag 10.11 kl. 21:59 i Oslo (20:59 UTC). Mutanter: V1 klokka regnet i UTC, V2 klokka regnet med fast UTC+2.
  - *Svaret er ikke fra børsdagen (FR-402).* Mangler svaret kursen for børsdagen for noen av aksjene, nevner utskriften dem (antall og symboler), og kjøringen avslutter med kode 1. Kursene, fila og vurderingene med grunnen `kurs_ikke_fra_dagen` står. En ny kjøring samme kveld gir 0 kall, fordi filvakten stopper den (et nytt forsøk er 2.3b). Mutant: V3 varselet fjernet. Ni eldre tester brukte `falsk_serie()`, som slutter 30.07, i kjøringer for 22.09 eller andre dager. De handler om noe annet og får nå en serie som slutter på børsdagen (`serie_til`). Testen for K4 i 2.5 (EQNR uten kurs for 22.09) venter nå kode 1.
- **2026-10-08, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 6 og 10), Marians beslutning:** kvotesjekken tar antallet aksjer i lista som parameter, ikke 15. Regnestykket er skilt ut i `vurder_kvote(igjen, bonus, antall)`, som testes med en kortere liste (10) og med 18. `kjoer()` gir `len(AKSJEUNIVERS)`, og 2.11 gir bare et annet tall. Grensen «`igjen ≥ 15`» under Boundaries gjelder dermed antallet. Mutant: V4 15 skrevet inn i `vurder_kvote`. Bonuskvoten brukes bare til å fullføre kveldens henting (Marians beslutning 08.10 kl. 08:06), som før.
- **2026-10-08: navnene i Code Map** er rettet til navnene i koden (`tolk_kvote`, `manglende_i_basen`).

## Review Triage Log

## Verification
