---
title: 'Story 2.2: Hentekommandoen som egen inngang'
type: 'feature'
created: '2026-10-03'
status: 'ready-for-dev'
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
- [ ] `src/lagring_sqlite.py` -- `kjoer_migrasjoner`, `mode=rw`, `VENTETID_SEKUNDER`
- [ ] `src/app.py` og `src/templates/index.html` -- basen per forespørsel, migrering én gang, 503, `HENTEKOMMANDO`, tom tilstand
- [ ] Testene og mutantene i Verification
- [ ] `README.md`, `deferred-work.md`, spinen ved AD-10

**Acceptance Criteria:**
- Given en base med serier, when `/` og `/aksje/EQNR` vises, then tallene kommer fra basen, også når øyeblikksbildet i `data/raa/` har andre tall.
- Given øyeblikksbildet 02.10 og en kopi av basen etter hentingen 02.10, when sidene vises fra hver av dem, then radene, detaljene og sidene er like, bortsett fra det som sier hvor dataene kommer fra.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q` -- grønn. Før: 1074 i CI på main, kjøring 37132586305 (1058 passed og 16 skipped lokalt).

**Mutantene**, én om gangen, satt tilbake fra en kopi med sha256. Hver føres med testen som fanget den:
1. Oppstart kaller hentingen. 2. `migrer()` ved hver forespørsel. 3. Tilkoblingen lukkes ikke. 4. Tilkoblingen på modulnivå. 5. Sidene leser øyeblikksbildet. 6. Tom base gir feilside. 7. `mode=rw` fjernet, så en forespørsel uten migrering lager fila. 8. Den gamle meldingen om `data/`. 9. Nøkkelen fra fil. 10. Feil ved migrering gir 500 i stedet for 503. 11. Ventetiden fjernet. 12. Kommandoen skrevet i malen i stedet for fra konstanten.
