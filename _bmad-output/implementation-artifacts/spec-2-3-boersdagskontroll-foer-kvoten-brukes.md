---
title: 'Story 2.3: Børsdagskontroll før kvoten brukes'
type: 'feature'
created: '2026-10-07'
status: 'done'
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
  *Rettet 2026-10-08 kl. 20:22, Marians beslutning (BH4 i gjennomgangen):* filvakten gir kode 1, ikke 0. Når filvakten stopper kjøringen, mangler basen dagen eller kunne ikke leses, så dagen er ikke komplett. Utskriften sier fortsatt hvorfor, og at et nytt forsøk hører til 2.3b. Tidskontrollen og basen gir fortsatt kode 0.
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
| Lørdag, fredagens fil finnes | `kurser-raa-<fredag>.json` | 0 kall, sier hvorfor, nevner 2.3b. *Rettet 08.10 (BH4):* kode 1 |
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
- [x] Del 3: spinen, `lagring_fil.py`, `CLAUDE.md`, README, `deferred-work.md`. Commit og push. *08.10:* regel 22 i `CLAUDE.md`, raden «Datoer» og merknaden under AD-2 i spinen, docstringen i `nyeste_snapshot`, README-linjen om kl. 22, K8 løst og E9 til 2.4.
- [x] Mutantene M1–M8, K1–K4 og V1–V4 (Spec Change Log 08.10), kjørt 08.10 kl. 18:18–18:56 mot hele `tests/` med `-x`. Resultatet står under Verification. PR mot main, gjennomgang (Blind Hunter, Edge Case Hunter, Verification Gap), CI grønn. Stopp før flettingen.

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

**Hele suiten, undersøkt 08.10 kl. 18:03–18:06** (instruksjonen kl. 18:03): `uv run pytest -o faulthandler_timeout=120` på grenen etter mergen av main (`ee79105`), i forgrunnen med en grense på 10 minutter. Den hang ikke: 1164 passed og 16 skipped på 92 s, og 75 s andre gang. faulthandler skrev ingenting. Hengen 07.10 er ikke gjenskapt, og årsaken er ikke funnet. Det som er sjekket: `kjoer()` har ingen løkke eller ventetid, og `requests.get` i `hent_kvote` har `timeout=30`. Funnet underveis: 40 kall til `fp.kjoer` i 34 tester i `test_fetch_prices.py` er uten `les_kvote` (telt med `ast`). De som kommer forbi filvakten, går mot nettet med `hent_kvote`. Sperren i `tests/conftest.py` avviser kallet med en gang, og `except Exception` i kvotesjekken sluker feilen og henter likevel. Det henger ikke, men sperren sees ikke i testene. Ført som funn til gjennomgangen. *Rettet 08.10 (instruksjonen kl. 19:00, `f48729b`):* `kjoer()` har ingen standardverdi for `les_kvote`, `main()` gir `hent_kvote`, og de 40 kallene har fått `nok_kvote`. En test som glemmer kvoten, feiler nå med `TypeError` (AD-8). `data/db/ose.db` er ikke endret av kjøringene (sist endret 07.10 kl. 22:24, av kveldshentingen fra main).

**Gjenstår:** hele suiten grønn. Del 3 (spinen med raden «Datoer» og merknaden under AD-2, docstringen i `lagring_fil.py`, regel 22 i `CLAUDE.md`, README-linjen, K8 og E9 i `deferred-work.md`). Mutantene M1–M8 og K1–K4. PR, gjennomgang og CI. Kontrollen av `data/raa/`: navnene er lest. De ni kursfilene (22.–24.09, 29.09–02.10, 05.–06.10) har alle en børsdag i navnet, så de følger regelen. Ingen fil har fått nytt navn.

## Spec Change Log

- **2026-10-08, instruksjonen kl. 18:03 i `docs/ai-prompts/2026-10-08.md`: to ting fra planen 05.10 som manglet her.**
  - *Vintertid.* Etter 25.10 er kl. 22:30 i Oslo 21:30 UTC. En test henter tirsdag 27.10 kl. 21:30 UTC, og en test nekter tirsdag 10.11 kl. 21:59 i Oslo (20:59 UTC). Mutanter: V1 klokka regnet i UTC, V2 klokka regnet med fast UTC+2.
  - *Svaret er ikke fra børsdagen (FR-402).* Mangler svaret kursen for børsdagen for noen av aksjene, nevner utskriften dem (antall og symboler), og kjøringen avslutter med kode 1. Kursene, fila og vurderingene med grunnen `kurs_ikke_fra_dagen` står. En ny kjøring samme kveld gir 0 kall, fordi filvakten stopper den (et nytt forsøk er 2.3b). Mutant: V3 varselet fjernet. Ni eldre tester brukte `falsk_serie()`, som slutter 30.07, i kjøringer for 22.09 eller andre dager. De handler om noe annet og får nå en serie som slutter på børsdagen (`serie_til`). Testen for K4 i 2.5 (EQNR uten kurs for 22.09) venter nå kode 1.
- **2026-10-08, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 6 og 10), Marians beslutning:** kvotesjekken tar antallet aksjer i lista som parameter, ikke 15. Regnestykket er skilt ut i `vurder_kvote(igjen, bonus, antall)`, som testes med en kortere liste (10) og med 18. `kjoer()` gir `len(AKSJEUNIVERS)`, og 2.11 gir bare et annet tall. Grensen «`igjen ≥ 15`» under Boundaries gjelder dermed antallet. Mutant: V4 15 skrevet inn i `vurder_kvote`. Bonuskvoten brukes bare til å fullføre kveldens henting (Marians beslutning 08.10 kl. 08:06), som før.
- **2026-10-08: navnene i Code Map** er rettet til navnene i koden (`tolk_kvote`, `manglende_i_basen`).
- **2026-10-08 kl. 20:22, Marians beslutning, instruksjonen kl. 20:22 i `docs/ai-prompts/2026-10-08.md`: filvakten gir kode 1 (BH4).** Dette endrer den frosne delen. Rettet-linjen står under «Utskrift og koder», og teksten over den står. Når filvakten stopper, mangler basen dagen eller kunne ikke leses, så dagen er ikke komplett. Tidskontrollen og basen gir fortsatt kode 0. Tre tester låser kode 1, og mutanten B4 (kode 0 igjen) fanges av alle tre. `--hent-foer-kl-22` (BH1/ECH2) skriver fila som før, med advarselen: flagget er en overstyring for hånd (gruppens beslutning 29.09), og den planlagte jobben bruker det aldri.
- **2026-10-08, etter gjennomgangen (VG7):** «Feilteksten er bare typenavnet» under Boundaries gjelder nettfeil. Et svar med feil form gir `UlesbarKvote`, der teksten nevner feltnavnet, aldri en verdi fra svaret. En 401 eller 403 fra `/api/user` er ikke et ulesbart svar: den stopper med 0 kall og kode 1 (BH2). En test låser begge.

## Review Triage Log

Gjennomgang 1 (08.10 kl. 19:05–19:20, PR #22), Blind Hunter (BH, bare diffen), Edge Case Hunter (ECH) og Verification Gap (VG), som tre uavhengige agenter. Rettelsene er `df02b7f`.

| # | Funn | Dom | Grunnlag | Rute |
|---|---|---|---|---|
| BH1, ECH2 | `--hent-foer-kl-22` før dagens kurs finnes, skriver fila under dagens dato. Svaret mangler dagen (FR-402, kode 1), og kveldens henting stopper ved filvakten med 0 kall | high | Stemmer. Spesifikasjonen sier at flagget gir dagens navn «som før», og et nytt forsøk er 2.3b | patch: utskriften og hjelpeteksten sier at fila kan låse dagen. **Til Marian:** om flagget skal skrive fila før kursen finnes, eller nekte å skrive fila når svaret mangler dagen. *Avgjort 08.10 kl. 20:22, Marians beslutning:* flagget skriver fila som før, med advarselen. Det er en overstyring for hånd, slik gruppen bestemte 29.09, og den planlagte jobben bruker det aldri. Ingen ny endring i koden |
| ECH1 | Et symbol som feiler i hentingen, gir kode 0, mens et svar uten dagens rad gir kode 1 | medium | Kode 0 ved et symbol som feiler, er oppførselen fra main (AD-15, NFR-03: «stopper aldri på en enkelt feil»). «Hoppet over eller avvist» i docstringen gjelder basen. En retting ga 35 tester som feilet | utsatt til 2.3b, som gjør nye forsøk for symbolene som feilet (`deferred-work.md`) |
| BH2 | En nøkkel som avvises av `/api/user` (401 eller 403), gir likevel henting og en fil med 15 feil | medium | Stemmer. En avvist nøkkel er ikke et ulesbart svar | patch: 401 og 403 stopper med 0 kall og kode 1. Andre HTTP-feil gir henting. To tester |
| BH3 | `except Exception` sluker programmeringsfeil, og hentingen går uten kvotesjekk | medium | Stemmer | patch: bare `requests.RequestException` og `ValueError`. Testene som brukte `RuntimeError`, bruker nå `requests.ConnectionError`. Én test for `AttributeError` |
| BH4 | Filvakten gir kode 0 også når basen mangler dagen | medium | Når filvakten svarer, mangler basen dagen, eller den kunne ikke leses. Kode 0 for filvakten står i den frosne delen (Boundaries) | **til Marian**, fordi det endrer den frosne delen. Ikke endret. *Avgjort 08.10 kl. 20:22, Marians beslutning:* kode 1. patch: `sys.exit(1)` i filvakten, tre tester, mutant B4 |
| ECH3 | En base på nyere skjemaversjon gir «henter likevel» og 15 kall som så feiler i basen | medium | Stemmer. Tilstanden er kjent før første kall | utsatt (`deferred-work.md`). Skillet mellom nyere og eldre versjon må gjøres i porten |
| VG1 | «En test låser rekkefølgen» gjelder bare nøkkel, kvote og kall | medium | Stemmer. To flyttinger overlevde | patch: to tester der to sjekker sier nei samtidig |
| VG2, ECH5 | `igjen` under 0 er ikke testet, og negative tall i svaret godtas | medium | Stemmer. Etter kall 21 er `apiRequests` over 20 | patch: test med 25 brukt. Negative tall er `UlesbarKvote` |
| VG3 | At basesjekken ikke migrerer, er ikke testet | medium | Stemmer. En base på siste versjon endres ikke av en migrering, så første forsøk på test fanget ikke mutanten | patch: test med en base på versjon 3, som skal gi «kunne ikke leses» i basesjekken |
| VG4 | Regel 22 håndheves ikke av noen test | medium | Stemmer. Fixturen flytter `BASE_STI`, men ser ikke på fila | patch: en fixture for hele økta i `conftest.py` sammenligner innhold og mtime for `data/db/ose.db` før og etter. Hoppes over når fila ikke finnes, som i CI |
| VG6, VG7 | Feilgrenen for et ulesbart svar er ikke testet med navn og e-post. Spesifikasjonen sier «bare typenavnet», men `UlesbarKvote` gir feltnavn | medium | Stemmer | patch: test med navn, e-post og verdier i et ulesbart svar. Spec Change Log: feltnavn, aldri verdier |
| VG5 | Tabellen viste bare første test som feilet, med `-x`, og M4 var ikke entydig | low | Stemmer | patch: hver mutant kjørt mot sin egen test (under Verification), og M4 delt i M4a og M4b |
| BH5, ECH6 | «Dette koster 15 av dagskvoten paa 20» også når bonusen brukes | low | Stemmer | patch: «Dette koster 15 kall.» |
| BH6, VG9 | Docstringen til `kjoer()` sier None bare for fila som finnes | low | Stemmer | patch |
| BH7, VG9 | README om stengte dager nevner ikke filvakten | low | Stemmer | patch |
| BH8, VG8 | Testen for ulesbar base sjekker ikke koden, og meldingen kunne vært kvotens | low | Stemmer | patch: kode 1 og linja som begynner med «Basen ose.db kunne ikke leses» |
| BH9 | GMT-testen sjekker bare kode 1 | low | Stemmer | patch: utskriften sier 0 igjen, trenger 15 og 0 kall brukt |
| ECH4 | En `dato` i `kurs` som ikke kan leses, gir `ValueError` og traceback før første kall | low | Bare en endring for hånd i basen gir det. Triggerne og porten slipper ikke slike rader inn | utsatt (`deferred-work.md`) |
| ECH7 | Stopper vurderingene ved midnatt eller basefeil, nevnes ikke aksjene uten dagens kurs | low | Stemmer. Fila står og kan leses | utsatt (`deferred-work.md`) |
| ECH8 | Basen har kursene, men vurderingene for dagen mangler: «Ingenting aa hente», kode 0 | low | Ingen regresjon: filvakten ville stoppet kjøringen uansett. `--les-inn` skriver ingen vurdering (2.1b), og en ny kjøring stopper ved basesjekken, så dagen blir stående uten vurdering | utsatt til 2.3b (`deferred-work.md`) |

## Verification

**Mutantene, 08.10 kl. 18:18–18:56.** Én om gangen, et eksakt bytte i `src/fetch_prices.py`, `uv run pytest -q -x tests/`, originalen tilbake etter hver. 16 av 16 gir en feilende test. 15 ble drept i første kjøring:

| Mutant | Første test som feilet |
|---|---|
| M1 tidskontrollen fjernet | `TestTidskontrollen::test_boersdag_foer_kl_22_gir_0_kall_og_nevner_flagget` |
| M2 `<` byttet med `<=` | `TestSkriverIkkeOver::test_tom_katalog_gir_ny_fil_som_kan_leses_og_er_uten_noekkel` |
| M3 `any` i stedet for `all` | `TestVurderingenISammeKjoering::test_vurderingen_er_regnet_av_serien_kjoeringen_selv_lagret` |
| M4 filvakten sjekker `dag` | Se under. `TestBoersdagIOsloTidsstempelIUtc::test_filnavn_og_hentet_fra_samme_oeyeblikk[00:30 siste sommertidsdag]`, linje 544 |
| M5 nøkkelen før tidskontrollen | `TestTidskontrollen::test_boersdag_foer_kl_22_gir_0_kall_og_nevner_flagget` |
| M6 flagget ignoreres | `test_filnavn_og_hentet_fra_samme_oeyeblikk[00:30 norsk sommertid, gitt i Oslo-tid]` |
| M7 tidskontroll alle dager | `TestTidskontrollen::test_dag_som_ikke_er_boersdag_har_ingen_tidskontroll` |
| M8 ulesbar base gir 0 kall | `TestHentingenSkriverBasen::test_basen_kan_ikke_aapnes_fila_staar_og_kode_1` |
| K1 kvotedato i Oslo | `TestKvoten::test_dagen_regnes_i_gmt_ikke_i_oslo` |
| K2 bonusen telles ikke | `TestKvoten::test_under_15_med_bonus_henter_og_sier_hvor_mange` |
| K3 ulesbart svar gir 0 kall | `test_main_skriver_fila_for_norsk_dato_uten_noekkel` |
| K4 hele svaret skrives ut | `TestRekkefoelgen::test_noekkelen_og_kvoten_kommer_foer_foerste_kall` |
| V1 klokka i UTC | `TestSkriverIkkeOver::test_tom_katalog_gir_ny_fil_som_kan_leses_og_er_uten_noekkel` |
| V2 fast UTC+2 | `TestVintertid::test_kl_21_59_i_oslo_i_november_nekter` |
| V3 FR-402-varselet fjernet | `TestVurderingenISammeKjoering::test_nyeste_kurs_ikke_fra_dagen_gir_en_rad_med_grunn` |
| V4 15 skrevet inn i `vurder_kvote` | `TestKvotenTarAntallet::test_vurder_kvote[12-0-10-0]` |

**M4 hang én gang.** I første kjøring ga M4 tidsavbrudd etter 600 s, uten faulthandler. Ingen pytest-prosess ble stående igjen. Kjørt på nytt fire ganger: én gang mot `tests/test_fetch_prices.py` med `faulthandler_timeout=45` (drept på 17 s), og tre ganger mot hele `tests/`, én gang med `faulthandler_timeout=60` kl. 18:57 og to ganger kl. 18:59–19:00 (drept på 35–38 s, i testen i tabellen). faulthandler skrev ingenting, fordi ingen kjøring hang. Hengen er derfor ikke gjenskapt, og det er **ikke avgjort** om den har samme årsak som hengen 07.10. Ingen rettelse er gjort i testen eller koden for selve hengen, fordi årsaken ikke er funnet. Ingen test starter `fetch_prices` som underprosess, så M4 kan ikke ha brukt kvoten. Kandidat, ikke vist: `traad.join()` uten tidsgrense i `tests/test_app.py` (`test_en_forespoersel_i_en_annen_traad_faar_egen_tilkobling`). Tiltakene er at en ny heng skal synes: `faulthandler_timeout = 120` i `pyproject.toml` (`74f8210`), og `timeout-minutes: 15` på pytest-jobben i `tester.yml` (`5e9efde`).

**Hver mutant mot sin egen test, 08.10 kl. 19:28** (VG5, uten `-x`). 15 av 15 drept:

| Mutant | Testen som fanger den |
|---|---|
| M2 `<` byttet med `<=` | `TestTidskontrollen::test_kl_22_presis_henter` |
| V1 klokka i UTC | `TestVintertid::test_kl_22_30_i_oslo_etter_25_10_er_21_30_utc_og_henter` |
| M4a navnet etter `dag` | `TestHelgen::test_loerdag_uten_fredagens_kurser_henter_med_fredagens_navn` |
| M4b vakten etter `dag` | `TestHelgen` (1 av 3) |
| M6 flagget ignoreres | `TestTidskontrollen::test_flagget_henter_foer_kl_22_med_dagens_navn` |
| K4 hele svaret skrives ut | `TestKvoten::test_navn_og_epost_staar_aldri_i_utskriften` (1 av 3) |
| VG1a basen før tidskontrollen | `TestEtterGjennomgangen::test_tidskontrollen_kommer_foer_basen` |
| VG1b filvakten før basen | `TestEtterGjennomgangen::test_basen_kommer_foer_filvakten` |
| VG2 `max(grense - brukt, 0)` fjernet | `TestEtterGjennomgangen::test_brukt_over_grensen_gir_0_igjen_og_bonusen_fullfoerer` |
| VG3 basesjekken migrerer | `TestEtterGjennomgangen::test_basesjekken_migrerer_ikke` |
| VG6 verdien i feilteksten | `TestEtterGjennomgangen::test_ulesbart_svar_med_navn_og_epost_viser_ingen_verdier` |
| BH2 avvist nøkkel henter | `TestEtterGjennomgangen::test_avvist_noekkel_gir_0_kall_og_kode_1` |
| BH3 `except Exception` tilbake | `TestEtterGjennomgangen::test_programmeringsfeil_i_kvoten_synes` |
| ECH5 negative tall godtas | `TestEtterGjennomgangen::test_negativt_tall_er_ulesbart` (3 av 3) |
| BH1 advarselen fjernet | `TestEtterGjennomgangen::test_flagget_advarer_om_filvakten` |

**B4, 08.10 kl. 20:25** (BH4, Marians beslutning): filvakten gir kode 0 igjen. Drept av alle tre: `TestHelgen::test_loerdag_naar_fredagens_fil_finnes_gir_0_kall_og_sier_hvorfor`, `TestSkriverIkkeOver::test_dagens_fil_finnes_og_ingen_kall_brukes` og `TestSvaretIkkeFraBoersdagen::test_ny_kjoering_samme_kveld_gir_0_kall`. Suiten etterpå: 1191 passed og 16 skipped.

Fixturen for `data/db/ose.db` (VG4) er ikke prøvd med en mutant, fordi en mutant måtte skrive den ekte basen.

**Suiten** etter del 4, del 3 og rettingen av `les_kvote`: 1179 passed og 16 skipped (`uv run pytest -q`, 92 s, kl. 19:03).
