---
title: 'Story 2.2: Hentekommandoen som egen inngang'
type: 'feature'
created: '2026-10-03'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '325abb202cb7bdbb0efbc90d35dd7965a706452b'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-1b-basen-aapnes-ett-sted-og-hentingen-skriver-kursene-dit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-5-vurderingen-skrives-i-samme-kjoering.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Webserveren leser kursene fra øyeblikksbildene i `data/raa/`, mens hentingen skriver dem til basen. Sidene og basen kan dermed vise hver sitt, og den tomme siden sier «Ingen kursdata funnet i `data/`».

**Approach:** Webserveren åpner basen med `aapne_base`, kjører `migrer()` én gang per prosess og per base ved første forespørsel, og åpner én tilkobling per forespørsel uten migrering. Sidene leser kursene gjennom `SqliteKurslager`. Signalet regnes som før (2.2b endrer det). Hentekommandoen er fortsatt `src/fetch_prices.py`.

## Boundaries & Constraints

**Always:**
- `aapne_base(sti, *, kjoer_migrasjoner=True)`. Med `False` åpnes basen med `mode=rw`, så en manglende fil gir feil og ikke en ny fil, og ingen mappe lages. Ventetiden er `VENTETID_SEKUNDER = 5.0`, skrevet ut i koden (BH7 fra 2.1b). Fortsatt eneste kall til `sqlite3.connect`.
- Migreringen kjøres i `before_request`, første gang en prosess får en forespørsel mot en gitt `BASE_STI`, under en lås. Det virker likt med `python src/app.py`, `flask run` og en WSGI-server. Ingen migrering ved import av `app`.
- Kan basen ikke migreres eller åpnes (`BASEFEIL`), svarer siden 503 med en kort beskjed som sier at basen ikke kan åpnes, og hva som er feil. Ingen traceback.
- Én tilkobling per forespørsel i `flask.g`, lukket i `teardown_appcontext`.
- `hent_leser()` gir `SqliteKurslager` på forespørselens tilkobling, eller `None` når basen ikke har en eneste serie. Kroken beholdes for testene.
- Tom tilstand, både for tom base og basefil som mangler: «Ingen kurser i basen ennå. Hent dem med `<kommando>`.» Kommandoen kommer fra konstanten `HENTEKOMMANDO` i `app.py`, og en test krever den både på den tomme siden og i README (story 3.3).
- `app.py` importerer verken `fetch_prices`, `requests`, `eodhd` eller `lagring_fil`. Oppstart og forespørsler gjør null nettkall.
- Nøkkelen leses fra miljøet (`EODHD_API_KEY`), også uten `.env` (AD-12).
- README «Kom i gang» og docstringen i `app.py` sier at sidene leser basen (regel 19).
- `deferred-work.md`: punktene fra 1.4b og 1.5 får `resolved:`. Punktet fra 1.5b får en merknad om at webserveren nå kaller `migrer()` og har skrivetilgang. Om imaget skal ha en skrivebeskyttet base, avgjøres i 3.1.
- Ingen API-kall. `src/fetch_prices.py` kjøres ikke, heller ikke med `--les-inn`.

**Never:** Vurderingen på sidene og spørringen med join (2.2b). Børsdagskontrollen (2.3). Historikken (2.7). Indeksen (2.8). Docker (3.1). Ingen egen commit på grenen for noe annet enn 2.2.

## Beslutninger (godkjent 03.10 kl. 18:05)

1. **A:** Storyen deles. 2.2b står i `epics.md` og `sprint-status.yaml` (`325abb2`).
2. **A, for 2.2b:** «–» med tilstanden. Signalet regnes ikke når raden mangler.
3. **A:** ventetiden er 5 sekunder, skrevet ut i koden.
- **Tillegg:** konstanten for kommandoen og testen mot README. Migrering uansett hvordan webserveren startes. Merknaden i `deferred-work.md` om skrivetilgang. Kontrollregning med bare antall.

## I/O & Edge-Case Matrix

| Scenario | Tilstand | Forventet |
|---|---|---|
| Vanlig | Base med 15 serier | Oversikten og detaljene fra basen |
| Tom base | Basefil uten serier | 200, tom tilstand med `HENTEKOMMANDO` |
| Ingen basefil | `BASE_STI` finnes ikke | Første forespørsel migrerer og lager en tom base, så tom tilstand |
| Basen nyere enn koden | `skjema_versjon` over katalogen | 503 med beskjed, ingen traceback |
| To forespørsler | Samme prosess | `migrer()` én gang, to tilkoblinger, begge lukket |
| Annen tråd | Forespørsel i ny tråd | Egen tilkobling, ingen `ProgrammingError` |
| Import av `app` | Ingen forespørsel | Ingen migrering, ingen fil |
| Oppstart | Tom base | Null nettkall |

</frozen-after-approval>

## Code Map

- `src/lagring_sqlite.py` -- `aapne_base` (l. 41), `BASE_STI`, `SqliteKurslager`, `_krev_siste_versjon`.
- `src/app.py` -- `hent_leser`, rutene `/` og `/aksje/<symbol>`, `__main__`. Importerer i dag `lagring_fil.nyeste_leser`.
- `src/templates/index.html` -- tom tilstand l. 117–121.
- `src/fetch_prices.py` -- `BASEFEIL`, `hent_api_nokkel`. Endres ikke.
- `tests/test_app.py` -- 11 tester monterer `hent_leser`. `test_uten_kilde_…`, `test_uleselig_hentet_…`, `test_rutene_gjoer_ingen_nettverkskall` og `TestHentLeser` gjelder filadapteren og skrives om.
- `tests/test_konsumentene.py` -- `test_bare_aapne_base_kobler_til_basen`, `test_app_velger_ikke_oeyeblikksbilde_selv`.
- `tests/conftest.py` -- `stiene_i_tmp_path` peker `BASE_STI` mot `tmp_path`.
- `README.md` «Kom i gang», `_bmad-output/implementation-artifacts/deferred-work.md`.

## Tasks & Acceptance

**Execution:**
- [x] `src/lagring_sqlite.py` -- `kjoer_migrasjoner`, `mode=rw`, `VENTETID_SEKUNDER`
- [x] `src/app.py` og `src/templates/index.html` -- basen per forespørsel, migrering én gang, 503, `HENTEKOMMANDO`, tom tilstand
- [x] Testene og mutantene i Verification
- [x] `README.md`, `deferred-work.md`, spinen ved AD-10

**Acceptance Criteria:**
- Given en base med serier, when `/` og `/aksje/EQNR` vises, then tallene kommer fra basen, også når øyeblikksbildet i `data/raa/` har andre tall.
- Given øyeblikksbildet 02.10 og en kopi av basen etter hentingen 02.10, when sidene vises fra hver av dem, then radene, detaljene og sidene er like, bortsett fra det som sier hvor dataene kommer fra.

## Implementation Notes

- Bygget 03.10 direkte i økta, ikke av en egen implementasjonsagent.
- `aapne_base(sti, *, kjoer_migrasjoner=True)`. Uten migrering: `sqlite3.connect(sti.resolve().as_uri() + "?mode=rw", uri=True, timeout=VENTETID_SEKUNDER)`, uten `mkdir`. `VENTETID_SEKUNDER = 5.0`. Ny `har_kurser(tilkobling)` i `lagring_sqlite.py`, så `app.py` har ingen SQL.
- `app.py`: `before_request` kjører `_migrer_en_gang(sti)` under en lås, med et sett av stier som er migrert i prosessen, og åpner så `aapne_base(sti, kjoer_migrasjoner=False)` i `g.tilkobling`. `teardown_appcontext` lukker den. `BASEFEIL` gir `g.basefeil`, og begge rutene svarer 503 med `basefeil.html`. Stien slås opp ved hver forespørsel (`lagring_sqlite.BASE_STI`), så fixturen i `conftest.py` styrer den i testene, og ingen import rører basen.
- Avvik fra planen som ble vist i chatten kl. 17:52, ikke fra denne spesifikasjonen: planen sa at en forespørsel ikke lager basefila. Fordi migreringen nå skjer ved første forespørsel, lager den første forespørselen en tom base hvis den mangler, slik hentingen gjør. Forespørsler etter det åpner med `mode=rw`. Det står i matrisen.
- `HENTEKOMMANDO = "uv run python src/fetch_prices.py"` i `app.py`, sendt til malen som `hentekommando`.
- Testene som ble skrevet om, fordi de gjaldt filadapteren: `test_uten_kilde_…`, `test_tom_kilde_…`, `test_uleselig_hentet_…` (bare teksten), `test_rutene_gjoer_ingen_nettverkskall` (basen i stedet for fila) og `TestHentLeser`.
- Tester: før 1058 passed og 16 skipped lokalt (1074 i CI på main). Etter byggingen 1077 passed og 16 skipped, og etter gjennomgangen 1083 passed og 16 skipped. De 25 nye er talt som testkjøringer: 16 i `TestBasenIWebserveren` (6 etter gjennomgangen), 6 i `TestAapneBaseUtenMigrering` (den parametriserte ventetidstesten teller to), 2 for nøkkelen i `test_fetch_prices.py` og 1 vakt i `test_konsumentene.py`.
- Kontrollregning uten kall, på en kopi av basen i scratchpad, som ble slettet etterpå: forsiden og de 15 aksjedetaljene vist fra øyeblikksbildet `kurser-raa-2026-10-02.json` og fra basen etter hentingen 02.10. 16 av 16 sider like, 16 av 16 rader i oversikten (15 aksjer og overskriftsraden) og 15 av 15 detaljer.
- Mutantene, én om gangen, hele `tests/` hver gang, satt tilbake fra en kopi i scratchpad med sha256 sjekket. Testen som fanget hver:

| Mutant | Feilet | Testen som fanget den |
|---|---:|---|
| M1 oppstart kaller hentingen (`requests.get` i `before_request`) | 56 | `test_oppstart_med_tom_base_gjoer_ingen_nettkall`, `test_webserveren_importerer_ikke_hentingen` og alle sidetestene |
| M2 `migrer()` ved hver forespørsel | 1 | `test_migrer_kjoeres_en_gang_for_to_forespoersler` |
| M3 tilkoblingen lukkes ikke | 1 | `test_tilkoblingen_lukkes_etter_forespoerselen` |
| M4 tilkoblingen på modulnivå | 6 | `test_en_forespoersel_i_en_annen_traad_faar_egen_tilkobling` og fem til |
| M5 sidene leser øyeblikksbildet | 7 | `test_sidene_leser_basen_ikke_oeyeblikksbildet` og seks til |
| M6 tom base gir feilside | 4 | `test_tom_base_gir_tom_tilstand_med_kommandoen` og tre til |
| M7 `mode=rw` fjernet | 1 | `test_en_base_som_mangler_lages_ikke`. Overlevde først, fordi testen brukte en mappe som ikke fantes. Rettet i `e4f1be8` |
| M8 den gamle meldingen om `data/` | 6 | `test_tom_base_gir_tom_tilstand_med_kommandoen` og fem til |
| M9 nøkkelen fra fil | 1 | `test_noekkelen_leses_fra_miljoeet_uten_env_fil` |
| M10 feil ved migrering gir 500 | 1 | `test_basen_nyere_enn_koden_gir_503_med_grunnen` |
| M11 ventetiden fjernet | 2 | `test_tilkoblingen_bruker_ventetiden_fra_koden[med]` og `[uten]`. Overlevde først, fordi standarden i `sqlite3` også er 5 sekunder. Testen setter nå ventetiden til 2,5. Rettet i `e4f1be8` |
| M12 kommandoen skrevet i malen | 1 | `test_kommandoen_paa_den_tomme_siden_staar_i_readme` |
| M13 feil i `hent_leser` fanges ikke (etter gjennomgangen) | 1 | `test_basen_migrert_forbi_koden_etter_oppstart_gir_503` |
| M14 ny migrering når fila er borte, fjernet | 1 | `test_slettet_base_lages_paa_nytt` |
| M15 stien merkes før migreringen | 1 | `test_basen_nyere_enn_koden_gir_503_med_grunnen`. `test_mislykket_migrering_proeves_igjen` fanget den ikke, fordi den nye migreringen ved en slettet fil dekker over den |
| M16 hele feilteksten på 503-siden | 1 | `test_feilsiden_viser_ingen_stier` |
| M17 kroken gjelder alle forespørsler | 1 | `test_andre_ruter_roerer_ikke_basen` |

## Spec Change Log

## Review Triage Log

Gjennomgang 1 (03.10), Blind Hunter (BH), Edge Case Hunter (ECH) og Verification Gap (VG).

| # | Funn | Dom | Grunnlag | Rute |
|---|---|---|---|---|
| BH1, ECH1, VG-annet | Feil i `hent_leser` etter oppstart, for eksempel en base en nyere henting har migrert forbi koden, gir 500 | medium | `SqliteKurslager` reiser `RuntimeError` utenfor `try` i kroken | patch: `_leser_eller_basefeil` og en errorhandler gir 503. Test og M13 |
| VG1 | Feil ved åpningen per forespørsel er ikke testet gjennom rutene | medium | Bare migreringsfeil var testet | patch: `test_feil_ved_aapning_per_forespoersel_gir_503` |
| BH2, ECH2 | `_migrerte` glemmes aldri, så en slettet base gir 503 til omstart | medium | Stemmer | patch: mangler fila, glemmes stien og migreringen prøves én gang til. Test og M14 |
| BH3 | At en mislykket migrering prøves på nytt, er ikke testet | low | Stemmer | patch: `test_mislykket_migrering_proeves_igjen`. M15 ble fanget av `test_basen_nyere_enn_koden_gir_503_med_grunnen` |
| BH4, ECH3 | Låsen setter forespørslene i kø når migreringen feiler | low | Stemmer, men gjelder først en skrivebeskyttet base | utsatt til `deferred-work.md`, for 3.1 |
| BH5 | Kommandoen for Docker er ikke ført noe sted | low | Stemmer | utsatt til `deferred-work.md`, for 3.1 |
| BH6 | Avviket i Implementation Notes ser ut til å motsi matrisen | low | Avviket gjaldt planen i chatten, ikke spesifikasjonen | patch: notatet sier det |
| BH7 | Testtallet blander enheter | low | Den parametriserte testen teller to | patch: notatet teller testkjøringer |
| BH8, ECH5 | 503-siden viser stier og påstår at ingen kvote er brukt | medium | `str(feil)` kan ha stier, og siden vet ikke om en henting kjører | patch: bare feiltypen og filnavnet, og påstanden er fjernet. Test og M16 |
| BH9 | Kroken åpner basen for alle forespørsler | low | Stemmer | patch: bare de to rutene. Test og M17 |
| BH10 | Reload av `app` i testen kan gi gamle objekter i andre moduler | false | Ingen modul gjør `from app import`. `test_app.py` leser `app_modul.app` ved hvert kall | avvist |
| BH11 | `test_ventetiden_er_fem_sekunder` sjekker bare tallet | low | Beslutning 3 sier at 5 sekunder står i koden, og testen holder valget | avvist |
| BH12 | README sier ikke at webserveren trenger skrivetilgang | low | Stemmer | patch: én setning i README |
| ECH4 | En UNC-sti gir en URI SQLite avviser | low | Basen ligger lokalt under `data/db/` (AD-4). Ingen kaller bruker en nettverkssti | avvist |

## Verification

**Commands:**
- `uv run pytest -q` -- grønn. Før: 1074 i CI på main, kjøring 37132586305 (1058 passed og 16 skipped lokalt).

**Mutantene**, én om gangen, satt tilbake fra en kopi med sha256. Hver føres med testen som fanget den:
1. Oppstart kaller hentingen. 2. `migrer()` ved hver forespørsel. 3. Tilkoblingen lukkes ikke. 4. Tilkoblingen på modulnivå. 5. Sidene leser øyeblikksbildet. 6. Tom base gir feilside. 7. `mode=rw` fjernet, så en forespørsel uten migrering lager fila. 8. Den gamle meldingen om `data/`. 9. Nøkkelen fra fil. 10. Feil ved migrering gir 500 i stedet for 503. 11. Ventetiden fjernet. 12. Kommandoen skrevet i malen i stedet for fra konstanten. *Lagt til etter gjennomgangen:* 13. Feil i `hent_leser` fanges ikke. 14. Ny migrering når fila er borte, fjernet. 15. Stien merkes før migreringen. 16. Hele feilteksten på 503-siden. 17. Kroken gjelder alle forespørsler.
