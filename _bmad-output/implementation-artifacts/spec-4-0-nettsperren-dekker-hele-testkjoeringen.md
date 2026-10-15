---
title: 'Story 4.0: Nettsperren dekker hele testkjøringen'
type: 'feature'
created: '2026-10-15'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '48b8125'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Sperren i `tests/conftest.py` er en autouse-fixture med funksjonsscope. Den gjelder bare inne i testfunksjonene, ikke i fixturer med module- eller session-scope og ikke under innsamlingen. Loopback slippes gjennom til alle porter, så en test kunne nå en Ollama eller en proxy som kjører på maskinen. `gethostbyname`, `gethostbyname_ex` og `getfqdn` er ikke sperret (story 4.0 i `epics.md`).

**Approach:** Socket-sperren settes i `pytest_configure` med `pytest.MonkeyPatch()` og fjernes i `pytest_unconfigure`. `socket.socket.listen` pakkes inn, og loopback slippes bare gjennom til en port som en åpen socket i samme prosess lytter på. Fixturen beholdes for proxyvariablene. PR A i planen for KI-laget, før alt som kan kalle Ollama (svar 9).

## Planen

Planen for KI-laget ble vist i chatten 15.10 kl. 15:43 og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-15.md` (`5ce64f6`). Testtallet før: 1608 bestått og 16 hoppet over på main (`48b8125`).

## Svarene

*Lagt til 2026-10-15 (gruppens svar på de ti spørsmålene i planen, instruksjonen kl. 15:53):* svarene er beslutninger. Alle ti står under Epic 10 i `epics.md`. De som gjelder denne storyen:

- Svar 8: adressen til Ollama er `OSE_KI_OLLAMA_URL`, med `http://127.0.0.1:11434` som standard. Ollama lytter da på loopback, og sperren må stoppe en test som prøver å nå den.
- Svar 9: 4.0 er første PR.

**Mutantene** (planen kl. 15:43): N1 sperren bare i fixturen; N2 `gethostbyname` åpen; N3 loopback åpen for en port ingen lytter på; N4 `connect_ex` åpen.

## Boundaries & Constraints

- Bare testoppsettet endres. Ingen kode under `src/`.
- Ingen test kaller nettet eller en tjeneste på maskinen (AD-8). Ingen API-kall.

## I/O & Edge-Case Matrix

| Inndata | Forventet |
|---|---|
| `connect` eller `connect_ex` mot en adresse utenfor maskinen, i en test eller en fixture med module- eller session-scope | `NettverkISTest` |
| `connect` mot loopback til en port en åpen socket i prosessen lytter på | slippes gjennom |
| `connect` mot loopback til en port ingen lytter på, eller en lytter som er lukket | `NettverkISTest` |
| `getaddrinfo`, `gethostbyname`, `gethostbyname_ex` eller `getfqdn` på et navn utenom loopback, og `getfqdn()` uten navn | `NettverkISTest` |
| `getaddrinfo(host=…, port=…)` med navngitte argumenter | virker som før |
| `AF_UNIX` | slippes gjennom |

</frozen-after-approval>

## Code Map

- `tests/conftest.py`: `pytest_configure` og `pytest_unconfigure` med sperren, `_lytt` og `_lytter_paa` for loopback, oppslagene, og fixturen `ingen_nettverk` med bare proxyen.
- `tests/test_ingen_nettverk.py`: testene for kontrollpunktene.

## Spec Change Log

## Commitene

Grenen `4-0-nettsperren`, PR #44: `d909d58` spesifikasjonen og 4-0 til in-progress; `c82bbaf` sperren i `pytest_configure` med testene; `954eb73` rettingene fra gjennomgangen.

## Review Triage Log

Gjennomgang 15.10 på diffen `main...c82bbaf`, med Blind Hunter (BH, 16 funn), Edge Case Hunter (ECH, 15) og Verification Gap (VG, 3). Rettingene står i `954eb73`, og punktet i `deferred-work.md` i samme commit som denne triagen. Ingen funn må avgjøres av gruppen.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH4, ECH5, VG2 | asyncio på Windows kobler til med ConnectEx og går forbi `socket.connect` | medium | patch: `IocpProactor.connect` sperres på Windows, `test_asyncio_blokkeres`. VG bekreftet luken lokalt mot loopback før rettingen |
| BH5, ECH1 | `_lytter_paa` sammenlignet bare portnummeret, så en lytter på `::1` åpnet 127.0.0.1 på samme port | medium | patch: samme familie, og lytteren bundet til loopback eller alle adresser, `test_lytter_i_en_annen_familie_slipper_ikke_gjennom` |
| BH10, ECH11 | Testene som fanger en sperre som mangler, gjorde et ekte oppslag og en ekte tilkobling når sperren manglet, som under mutantene | medium | patch: de prøver loopback til en port ingen lytter på, eller ser at funksjonen er byttet ut før den kalles. Under den første kjøringen av N1 ble `eodhd.com` slått opp i DNS og det ble forsøkt en tilkobling til 192.0.2.1 (TEST-NET-1, rutes ikke), og under N4 en tilkobling til 192.0.2.1. Ingen API-kall |
| BH3, ECH6, ECH7, VG3 | UDP (`sendto`, `sendmsg`), `gethostbyaddr` og `getnameinfo` var ikke sperret | low | patch: alle sperret, `test_udp_blokkeres`, `test_navneoppslag_blokkeres`, `test_getnameinfo_blokkeres` |
| VG1 | Ingen test så at innsamlingen er sperret | low | patch: `_VED_INNSAMLINGEN` kjører når modulen importeres, `test_innsamlingen_er_sperret` |
| BH1, BH2 | Docstringen i `conftest.py` sa fortsatt «inne i hver test» og den gamle regelen for loopback | low | patch: docstringen sier hva som gjelder fra 4.0, og det gamle står som historikk |
| BH6, ECH8 | `getfqdn()` uten navn sperres, og standardbiblioteket kaller den selv (`email.utils.make_msgid`, `smtplib`) | low | patch: dokumentert i docstringen, og `test_http_server_paa_loopback_virker` viser at en falsk tjeneste på 127.0.0.1 virker. Kontrollpunktet krever at `getfqdn` sperres |
| ECH9 | `getfqdn("localhost")` gikk til den ekte `getfqdn`, som slår opp med `gethostbyaddr` | low | patch: et loopbacknavn gir `localhost` uten oppslag |
| BH13 | «LOCALHOST», «localhost.» og 127.0.0.2 ble regnet som navn på nettet | low | patch: `_er_loopbacknavn` med `ipaddress`, `test_andre_skrivemaater_for_loopback` |
| ECH2 | En lytter med `AF_UNIX` i `_lyttere` kunne gi `IndexError` | low | patch: bare `AF_INET` og `AF_INET6` sammenlignes |
| ECH3 | En annen tråd som lytter, kunne endre mengden mens den ble lest | low | patch: en lås rundt `_lyttere` |
| BH11 | En lytter en annen test ikke lukket, kunne holde porten testen bruker | low | patch: `_ledig_port` sjekker at ingen lytter i prosessen holder porten |
| BH15 | Verification var tom | low | patch: fylt ut under |
| BH16 | Docstringen i `test_loopback_slippes_gjennom` påsto en kontroll uten kilde | low | patch: viser til kontrollpunktet i `epics.md` og `test_rutene_gjoer_ingen_nettverkskall` |
| BH7, ECH (påstand) | Sperren gjelder ikke en underprosess som en test starter | low | utsatt: `deferred-work.md`. Grensen står i docstringen. Den eneste underprosessen i dag leser to konstanter |
| BH8 | En debugger som kobler seg til en port i en annen prosess (debugpy), stoppes | avvist | dokumentert i docstringen. En åpning for porter i andre prosesser er det sperren skal stenge |
| BH9 | Kode som kjører når `conftest.py` importeres, kjører før `pytest_configure` | avvist | dokumentert i docstringen. `conftest.py` importerer bare `requests` og standardbiblioteket |
| BH12 | Ingenting hindrer en falsk tjeneste i å lytte på 11434 | avvist | en falsk tjeneste binder til port 0, og en lytter på 11434 ville ikke fått porten når Ollama kjører |
| BH14 | `last_updated: 10-15-2026 16:00` ser anslått ut | avvist | tatt fra `date`, og commiten `d909d58` er fra kl. 16:00:27 |
| ECH4 | En lyttende socket som flyttes til et nytt objekt (`detach`, `wrap_socket` etter `listen`), sperres | avvist | ingen test gjør det. Sperren stenger da for mye, ikke for lite |
| ECH12 | `tmp_path` kan være for lang for `AF_UNIX` på macOS | avvist | testen hoppes over på Windows og kjører i CI på Linux, der stien er kort nok |


## Verification

**Commands:**
- `uv run pytest -q` -- før 1608 bestått og 16 hoppet over på main (`48b8125`). 1622 og 17 på `c82bbaf`. Etter rettingene 1633 og 17 på `954eb73`. Testen for `AF_UNIX` hoppes over på Windows.

**Mutantene**, kjørt én om gangen med `-x` og bare `tests/test_ingen_nettverk.py`, med kopi før og sha256 mot HEAD etter hver. Fila var lik HEAD etter hver. N1–N4 ble først kjørt på `c82bbaf` og fanget alle (se BH10 over), og så på nytt på `954eb73` med N5 og R1–R5. Alle er fanget:

| # | Mutant | Fanget av |
|---|---|---|
| N1 | sperren bare i fixturen | `test_innsamlingen_er_sperret` |
| N2 | `gethostbyname` åpen | `test_navneoppslag_blokkeres[gethostbyname]` |
| N3 | loopback åpen for en port ingen lytter på | `test_innsamlingen_er_sperret` |
| N4 | `connect_ex` åpen | `test_connect_ex_blokkeres` |
| N5 | sperren i en autouse-fixture med session-scope, ikke i `pytest_configure` | `test_innsamlingen_er_sperret` |
| R1 | asyncio på Windows åpen | `test_asyncio_blokkeres` |
| R2 | UDP åpen | `test_udp_blokkeres` |
| R3 | `gethostbyaddr` åpen | `test_navneoppslag_blokkeres[gethostbyaddr]` |
| R4 | familien sjekkes ikke | `test_lytter_i_en_annen_familie_slipper_ikke_gjennom` |
| R5 | 127.0.0.2 regnes ikke som loopback | `test_andre_skrivemaater_for_loopback[127.0.0.2]` |
