---
title: 'Story 3.4: Demoversjonen'
type: 'feature'
created: '2026-10-10'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'b294a9514aca2d455e72b6da3942abe7fff49910'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3-readme-slik-kjoerer-du-den.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Appen kan bare prøves med en egen EODHD-nøkkel. Faglærer, sensor og medstudenter skal kunne se hvordan den virker uten konto, og demoen er hovedveien for vurderingen (FR-411, svaret fra hjelpelæreren 05.10).

**Approach:** En egen kommando lager `data/db/demo.db` med 15 oppdiktede selskaper, kurser etter en skrevet regel med fast frø, og én vurdering per aksje og børsdag regnet med `vurder()`. Basen er merket som demobase, og merket avgjør «Eksempeltall» på sidene. Én bryter velger hvilken base webserveren åpner. Vaktene hindrer at demobasen og den ekte basen blandes, begge veier.

## Planen

Planen er vist i chatten 10.10 og ført i `docs/ai-prompts/2026-10-10.md` (instruksjonen kl. 12:06 og Utført-linjen). Gruppen sa ja kl. 12:27 med disse svarene, som er beslutninger:

1. **Navnene.** Joakim kontrollerte de 15 tickerne for hånd mot lista over aksjer i Oslo hos Euronext 10.10 kl. 12:25, og ingen av dem står der. Rådet søkte samme dag på nettet etter de 15 navnene, nøyaktig skrevet, og fant ingen selskaper med de navnene. Programmet henter aldri lista.
2. **Port 5000 for demoen.** App og demo kan ikke kjøre samtidig. `docker compose down` stopper også demotjenestene, og README-en sier hvordan man bytter (PR 2).
3. **Fast sluttdato, fredag 2026-10-09.**
4. **To pull requests.** PR 1 er demoen med uv. PR 2, med Docker og README, bygges på en ny gren fra main etter at PR 1 er flettet.

I tillegg, fra instruksjonen:
- Normalfordelingen og volumene lages fra `random()` med Box–Muller, fordi Python bare lover at `Random.random()` gir samme rekke med samme frø på tvers av versjoner.
- En base som ikke finnes eller ikke kan leses, regnes ikke som demobase i vakten i hentingen, og hentingen går videre som i dag.
- Demobaser lages bare i midlertidige mapper og prøveprosjekter, aldri i `data/db/` i repoet (regel 22).

## Boundaries & Constraints

**Always:**
- `DEMOUNIVERS` har de 15 i tabellen under. Ingen symbol eller ticker står i `AKSJEUNIVERS`.
- Kursene: 195 handelsdager fra 2026-01-02 til 2026-10-09 etter `boersdag.er_boersdag`. Hver aksje har sitt eget frø, `FROE * 100 + nummeret i lista`. Daglig logavkastning er drift + volatilitet · z, der z er normalfordelt fra Box–Muller på `random()`. Drift og volatilitet følger sektoren. Volumet er et nivå per aksje ganger `exp(0,3 · z)`, og med sannsynlighet 0,04 per dag tre ganger det. `adjusted_close` er lik `close`. Kursene avrundes til to desimaler, volumet til heltall. Siste dag faller Brattfjell Energi 6 % med tre ganger volumet, så minst én aksje skiller seg ut.
- Tilstandene: Varde Systemer har bare de siste 30 dagene (nylig notert, «signalet kunne ikke regnes» og «Trenger 51 dager»), Tareøy Havbruk mangler siste dag («ingen kurs fra dagen»), og Matfjord Merkevarer har ingen kurser («Uten data i denne kilden»).
- Hver børsdag i serien har én rad i `vurdering` per aksje, lik det `vurder()` gir for serien fram til dagen, skrevet med `SqliteVurderingslager.skriv` uendret og lagerets klokke stilt på dagen (`AD-7`).
- Merket er `PRAGMA application_id = 0x4F534544`. Bare demokommandoen setter det.
- Demokommandoen nekter en fil uten merket, også en tom fil. En demobase lages på nytt fra bunnen.
- Hentekommandoen og `--les-inn` nekter en demobase før noe annet. En base som ikke finnes eller ikke kan leses, regnes ikke som demobase.
- Bryteren er `OSE_DEMO=1`, eller `--demo` til `python src/app.py`. Med bryteren åpner webserveren `demo.db` ved siden av `ose.db` og lager den aldri. Mangler den, viser siden kommandoen som lager den. Uten bryteren åpnes `ose.db` som før.
- «Eksempeltall» står på hver side som viser en base med merket, og på ingen side med en base uten. Merket leses fra basen, ikke fra bryteren.
- Portene som skriver, tar lista som parameter, med `AKSJEUNIVERS` som standard. Testen som holder `aksje` lik `AKSJEUNIVERS` i den ekte basen, står (`AD-21`).

| Ticker | Navn | Sektor |
|---|---|---|
| BRFE | Brattfjell Energi | Energi |
| HVDO | Havdyp Olje | Energi |
| NLYS | Nordlysfeltet | Energi |
| SLVP | Sølvbank Petroleum | Energi |
| FJSB | Fjellheim Sparebank | Finans |
| TRHF | Trygghavn Forsikring | Finans |
| VRDS | Varde Systemer | Industri |
| KVST | Kvitstein Mineral | Materialer |
| JGRD | Jordgrøde Gjødsel | Materialer |
| BLGT | Bølgetopp Tankers | Shipping |
| LSTF | Lastfjord Container | Shipping |
| SGNT | Signalnett | Telekom |
| LKSV | Laksevik Sjømat | Sjømat |
| TROY | Tareøy Havbruk | Sjømat |
| MTFJ | Matfjord Merkevarer | Konsum |

**PR 1 (denne grenen, 3-4):** `src/demo.py`, merket, vaktene begge veier, lista som parameter i skriveportene, bryteren og siden når demobasen mangler, «Eksempeltall» og testene.

**PR 2 (ny gren fra main etter PR 1):** demotjenestene `demo-lag` og `demo` i profilen `demo`, volumet `ose-demo`, CI-steget, «Kom i gang» med demoen først og hvordan man bytter, testen for kommandoene, `docs/kvalitetssikring.md` klar for README-prøven, og merknader i spinen.

**Never:**
- KI-tekstene (3.4b), hovedindeksen (2.8), lista som kan byttes (2.11) og resten av punkt 4.4 i endringsforslaget 08.10, som ikke er bygget.
- Demokommandoen gjør ingen nettkall, leser ingen nøkkel og importerer verken `requests`, `eodhd` eller `fetch_prices`.
- Ingen demobase i `data/db/` i repoet under byggingen. `hent` kjøres aldri gjennom compose lokalt.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Ny demobase | `demo.db` finnes ikke | lages med merket, 15 aksjer, 195 dager, 2 925 vurderinger | — |
| Demobase finnes | `demo.db` med merket | lages på nytt, lik den forrige | — |
| Fil uten merket | `demo.db` uten merket, også tom | ingenting skrives, kode 1 | Utskriften sier hvorfor |
| Henting mot demobase | `ose.db` med merket | 0 kall, kode 1 | Utskriften sier hvorfor |
| Henting uten base | `ose.db` finnes ikke eller kan ikke leses | som i dag | — |
| Bryteren, ingen demobase | `OSE_DEMO=1`, `demo.db` mangler | siden viser `DEMOKOMMANDO`, ingen fil lages | — |

</frozen-after-approval>

## Code Map

- `src/kursdata.py` -- `kontroller_skriving` (linje 162) sjekker mot `AKSJEUNIVERS`. Får `univers` som parameter.
- `src/lagring_sqlite.py` -- `SqliteKurslager` (118), `SYMBOLER` og `_kontroller_noekkel` (192, 213) i vurderingslageret. Får `univers`. Nytt: `DEMOMERKE`, `er_demobase(sti)` og `demo_sti()` ved siden av `BASE_STI`.
- `src/fetch_prices.py` -- `kjoer` (547) og `les_inn` (775) får vakten først.
- `src/app.py` -- `_aapne_basen` (118) og `_migrer_en_gang`, rutene `markedsoversikt` og `aksjedetalj`. Bryteren, `DEMOKOMMANDO` og «Eksempeltall» gjennom en context processor.
- `src/templates/index.html`, `aksje.html`, `basefeil.html` -- merket etter `<body>`, og teksten når demobasen mangler.
- `src/signalberegning.py` -- `vurder` og `nodvendige_dager` (51), uendret.
- `tests/conftest.py` -- flytter `BASE_STI` til `tmp_path`, så `demo_sti()` følger med.

## Tasks & Acceptance

**Execution (PR 1):**
- [x] `src/kursdata.py`, `src/lagring_sqlite.py` -- lista som parameter, merket og `er_demobase`.
- [x] `src/demo.py` -- `DEMOUNIVERS`, regelen og demokommandoen.
- [x] `src/fetch_prices.py` -- vakten i `kjoer` og `les_inn`.
- [x] `src/app.py` og malene -- bryteren, siden når demobasen mangler, «Eksempeltall».
- [x] `tests/test_demo.py` -- kontrollpunktene.

**Acceptance Criteria:**
- Given to kjøringer av demokommandoen, then er basene like rad for rad.
- Given en demobase og bryteren av, then sier sidene «Eksempeltall». Given en ekte base og bryteren på, then gjør de det ikke.
- Given en demobase som `ose.db`, when hentingen eller `--les-inn` kjøres, then stopper den før noe annet med kode 1.

## Implementation Notes

- **Skriveportene:** `kontroller_skriving`, `SqliteKurslager` og `SqliteVurderingslager` (`skriv` og `les`) tar lista som skrives, med `AKSJEUNIVERS` som standard. Med standardlista er feilteksten den samme som før («ikke et symbol i AKSJEUNIVERS»), fordi to tester krever den.
- **Merket:** `DEMOMERKE = 0x4F534544` («OSED») i `lagring_sqlite.py`. `er_demobase` åpner med `aapne_base(..., kjoer_migrasjoner=False, skrivebeskyttet=True)` (`mode=ro`), fordi testen fra 2.1b krever at ingen annen kode i `src/` kaller `sqlite3.connect`.
- **Demokommandoen** skriver med `PRAGMA synchronous = OFF` på sin egen tilkobling. Med fsync per transaksjon tok de 2 925 vurderingene 34 sekunder på Windows, uten 2,7. Demobasen kan alltid lages på nytt. En demobase som finnes, slettes med `-wal` og `-shm` og lages fra bunnen.
- **Vakten i hentingen** er `nekt_demobase(base_sti, skriv)`, første linje i `kjoer` og `les_inn`. Den kommer før klokka: en test gir et øyeblikk uten sone og får kode 1, ikke `ValueError`. En base som ikke finnes, eller en fil som ikke er en SQLite-base, gir ingen stopp. Alle 190 testene i `tests/test_fetch_prices.py` er grønne uendret.
- **Endringer i `src/fetch_prices.py`:** bare `nekt_demobase` og kallet til den i `kjoer` og `les_inn`, og et avsnitt i docstringen til `kjoer`.
- **Webserveren:** med bryteren migreres og lages demobasen aldri. Mangler `demo.db`, får oversikten `DEMOKOMMANDO`, og aksjedetaljen gir 404. «Eksempeltall» kommer fra en context processor som leser `g.eksempeltall`, satt fra merket i basen ved hver forespørsel. Feilsiden viser navnet på basen bryteren valgte.
- **«samme frø gir like baser»** sammenligner `aksje`, `kurs`, `kursserie`, `vurdering`, merket og `skjema_versjon` uten kolonnen `anvendt`, som er tidspunktet migrasjonen ble kjørt.
- **Regel 22:** alle demobaser under byggingen er laget i `tmp_path` eller i scratch-mappa for økta. `data/db/` har ingen `demo.db`.

## Spec Change Log

- **2026-10-10 kl. 12:45, Tareøy Havbruk (avvik fra planen):** Boundaries sier at Tareøy Havbruk mangler siste dag, for å vise «ingen kurs fra dagen». Det virket ikke: oversikten leser vurderingen for datoen til nyeste kurs for hver aksje, så Tareøy viste vurderingen for 08.10, og datoen over tabellen ble 2026-10-08, fordi den er den eldste nyeste datoen (story 8.0). Regelen er tatt ut, og alle 14 med kurser har siste dag. «ingen kurs fra dagen» er ikke blant tilstandene demoen viser, som «hentingen feilet». En test krever at datoen over tabellen er 2026-10-09. **Til gruppen:** avviket står her og i PR-en, og kan tas tilbake før flettingen.

## Review Triage Log

Gjennomgang 1 av PR 1 (10.10 kl. 13:02–13:06, PR #26), Blind Hunter (BH, bare diffen), Edge Case Hunter (ECH) og Verification Gap (VG), som tre uavhengige agenter. Rettelsene er `5bcdef0`, `f9bbdcd` og `680fcf6`.

| # | Funn | Dom | Grunnlag | Rute |
|---|---|---|---|---|
| BH2, ECH5, ECH2, ECH3 | En bygging som stopper halvveis, etterlater en halv base med merket, og en gammel `-journal` kan bli liggende | high | Stemmer. Merket ble satt før innholdet, i fila webserveren leser | patch: bygges i `demo.db.ny` og byttes inn med `os.replace`. `-journal`, `-wal` og `-shm` fjernes. Test og mutant M19 |
| BH6 | Uten bryteren migrerer webserveren en demobase som ligger som `ose.db` | medium | Stemmer. `_migrer_en_gang` kom før merket ble lest | patch: en demobase åpnes skrivebeskyttet og migreres ikke. Test med kallene, mutant M20 (overlevde først, fordi en migrering av en base på siste versjon ikke endrer en byte) |
| BH5 | Webserveren åpner demobasen skrivbar | medium | Stemmer, `mode=rw` | patch: `skrivebeskyttet=True` |
| VG1 | 503 med bryteren og en ulesbar `demo.db` er ikke prøvd, heller ikke navnet på feilsiden | medium | Stemmer | patch: test for begge rutene, som krever `demo.db` og `DEMOKOMMANDO`. Mutantene M21 og M23 |
| ECH6 | En demobase uten kurser viser hentekommandoen, som skriver til `ose.db` | medium | Stemmer | patch: `DEMOKOMMANDO` med bryteren. Mutant M22 |
| VG3 | `--demo` er bare prøvd som tekst | medium | Stemmer | patch: `les_flagg(argv)`, testet ved å kalle den. Testen lekket `OSE_DEMO` til testene etter, og det er også rettet |
| BH11 | At samme frø gir samme base på andre plattformer, er ikke prøvd | medium | Stemmer. `math.log`, `cos` og `exp` er ikke lovet like overalt | patch: et fingeravtrykk av `kurs` regnet på Windows. CI på Linux ga samme (kjøring 38047102791) |
| ECH1, ECH11 | Vakten slipper gjennom en låst demobase eller en med varm journal | low | Stemmer, den går videre ved enhver lesefeil | ikke endret: gruppens beslutning kl. 12:27 er at en base som ikke kan leses, ikke er en demobase, og hentingen går videre som før |
| VG2 | «Eksempeltall» på feilsiden er ikke prøvd | low | Stemmer | patch: test der lesingen feiler etter at demobasen er åpnet |
| ECH4 | `PermissionError` når `demo.db` er åpen i et annet program, gir traceback | low | Stemmer på Windows | patch: `main` fanger `OSError` med kode 1 |
| ECH10, BH | `main(argv)` ser bort fra `argv` | low | Stemmer | patch: argparse. Test for et ukjent argument |
| ECH9 | En demobase på eldre skjema gir 503 uten råd | low | Stemmer | patch: feilsiden viser `DEMOKOMMANDO` med bryteren |
| ECH7 | I Docker viser siden uv-kommandoen for demoen | low | Stemmer | utsatt til PR 2, som har Docker-kommandoen |
| ECH8 | `demo.db` kan forsvinne mellom `is_file()` og åpningen | low | Med `os.replace` forsvinner den ikke under en ny bygging | ikke endret |
| BH1 | Kommentaren ved `DEMOKOMMANDO` sier at README og en test holder dem like | low | Stemmer ikke ennå | patch: kommentaren sier PR 2. Den ubrukte `README` i testen er fjernet |
| BH3 | Docstringen til `kjoer` sier at `ValueError` kommer før vakten | low | Stemmer ikke lenger | patch: en setning som sier at vakten for demobasen kommer før |
| BH9 | Feilteksten velges etter om det er samme objekt | low | Stemmer | patch: sammenligner innholdet |
| BH4 | Boundaries nevner fortsatt Tareøy uten siste dag | low | Står i Spec Change Log, og den frosne delen endres ikke uten gruppen | ikke endret |
| BH8 | Merket er kopiert i tre maler | low | Det finnes ingen felles mal. Tre korte blokker | ikke endret |
| BH10 | Varde Systemer har rader med grunn før den ble notert | low | Storyen krever én rad per aksje og børsdag. Oversikten leser datoen til nyeste kurs | ikke endret |
| BH12 | Linjenumrene i Code Map er utdatert, og statusen henger etter | low | Linjenumrene var riktige da planen ble skrevet | status satt til in-review. Linjenumrene står |

*Rettet 2026-10-10 kl. 13:23:* klokkeslettene i denne spesifikasjonen er ikke lest fra klokka: «kl. 12:45» i Spec Change Log, «12:49–12:58» for de første mutantene, «13:02–13:06» for gjennomgangen og «13:10–13:35» for mutantene etter den. Etter git log: avviket for Tareøy er committet kl. 12:47 (`a1f8e54`), de første mutantene gikk mellom 12:47 og 12:57 (`63c19cc`), gjennomgangen startet etter 12:57 og rettingene er fra 13:04 (`5bcdef0`, `f9bbdcd`), og mutantene etter den gikk mellom 13:04 og 13:22 (`680fcf6`).

## Verification

**Mutantene, 10.10 kl. 12:49–12:58.** Mot `tests/test_demo.py`, `tests/test_app.py`, `tests/test_fetch_prices.py` og `tests/test_aksje.py`. 18 av 18 drept:

| Mutant | Testen som fanger den |
|---|---|
| M1 merket følger bryteren | `test_merket_foelger_basen_ikke_bryteren` |
| M2 hentingen setter merket | `test_bare_demokommandoen_setter_merket` |
| M3 vakten i hentingen borte | `test_hentingen_nekter_en_demobase_foer_alt_annet` |
| M4 vakten i demokommandoen borte | `test_demokommandoen_nekter_en_ekte_base` |
| M5 nytt frø per kjøring | `test_samme_froe_gir_like_baser` |
| M6 serien på 120 dager | `test_serien_er_lang_nok_for_grafen_og_ma50` |
| M7 et navn fra `AKSJEUNIVERS` | `test_ingen_symboler_fra_den_ekte_lista` |
| M8 vurderingen regnes av hele serien | `test_hver_vurdering_er_det_vurder_gir` |
| M9 webserveren lager demobasen | `test_bryteren_uten_demobase_viser_kommandoen` |
| M10 «Eksempeltall» borte fra aksjedetaljen | `test_bryteren_med_demobase_viser_eksempeltall` |
| M11 `aksje` i en annen rekkefølge | `test_aksje_er_lik_demounivers` |
| M12 `gauss` i stedet for Box–Muller | `test_normalfordelingen_bruker_bare_random` |
| M13 en ulesbar base regnes som demobase | `test_en_base_som_mangler_eller_ikke_kan_leses_er_ikke_en_demobase` |
| M14 enhver verdi slår på bryteren | `test_bare_verdien_1_slaar_paa_bryteren` |
| M15 `les` sjekker mot `AKSJEUNIVERS` | `test_hver_vurdering_er_det_vurder_gir` |
| M16 siste dag uten fallet | `test_tilstandene_siste_dag` |
| M17 en tom fil godtas | `test_demokommandoen_nekter_en_tom_fil` |
| M18 `--demo` setter ikke bryteren | `test_demo_flagget_setter_bryteren` |

**Suiten:** 1250 passed og 16 skipped, mot 1226 og 16 før (24 i `tests/test_demo.py`).

**Etter gjennomgangen, 10.10 kl. 13:10–13:35.** Alle mutantene kjørt på nytt med de nye ankrene, 24 av 24 drept. Nye: M1b en demobase som `ose.db` følger bryteren, M19 byggingen rett i `demo.db`, M20 webserveren migrerer en demobase som `ose.db`, M21 feilsiden uten demokommandoen, M22 en tom demobase viser hentekommandoen, M23 feilsiden nevner `ose.db`. M1 er flyttet til grenen med bryteren, der merket faktisk leses. Første kjøring etter rettingene viste M1 og M20 som drept av en test i `test_app.py`. Det var `OSE_DEMO` som lekket fra testen for `--demo`, ikke mutantene. Etter rettingen ble M20 fanget først med testen som ser på kallene. M2 er bare fanget av en test som leser kildene. M12 og M16 fanges nå også av fingeravtrykket.

**Suiten etter rettingene:** 1257 passed og 16 skipped (31 i `tests/test_demo.py`). CI på `f9bbdcd`, kjøring 38047102791: `pytest` 1273 passed og `docker` grønn.

**Commands:**
- `uv run pytest -q` -- expected: grønn.
