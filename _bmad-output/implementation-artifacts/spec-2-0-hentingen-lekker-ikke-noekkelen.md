---
title: 'Story 2.0: Hentingen lekker ikke nøkkelen og skriver ikke over et øyeblikksbilde'
type: 'bugfix'
created: '2026-09-26'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '1e56e6fbb008741dc486a870b118ddad5b6d83ba'
context:
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `hent_ett_symbol` (`src/fetch_prices.py:66`) sender nøkkelen som `api_token` i adressen. Når et kall feiler, tar feilteksten fra `requests` med hele adressen, og `hent_universet` skriver den ut (linje 109) og lagrer den i `feil` i øyeblikksbildet (linje 108 og 132). `filnavn()` bruker kjøredagen, og `main()` skriver med `write_text` (linje 158), så en ny kjøring samme dag skriver over dagens øyeblikksbilde, mot AD-6.

**Approach:** Nøkkelen holdes ute av feilteksten i to lag: `hent_ett_symbol` gjør enhver feil fra `requests` om til en tekst uten adressen, og `hent_universet` fjerner nøkkelen fra enhver feiltekst før den skrives ut eller lagres. Kjøringen stopper før første kall hvis dagens øyeblikksbilde finnes, og fila skrives bare hvis den ikke finnes. Kilde: story 2.0 i `epics.md` slik den står 26.09 (`1e56e6f`).

## Boundaries & Constraints

**Always:**
- Regel 6: ingen nett i testene. Testene bytter ut `requests.get` og bruker en falsk nøkkel.
- AD-6: et øyeblikksbilde skrives aldri om. AD-12: nøkkelen kommer fra miljøet og vises aldri.
- Statuskoden og feiltypen beholdes i feilteksten, så en feil fortsatt kan forstås.

**Never:**
- Ingen endring i hvilke symboler som hentes, i intervallet eller i formatet på øyeblikksbildet.
- Ingen børsdagskontroll. Den er story 2.3. 2.0 ser bare etter en fil med dagens navn.
- `src/fetch_prices.py` kjøres ikke, og ingen test bruker kvote.

## Beslutninger 26.09

- **Formen på svaret kontrolleres i 2.0 (valg A).** `hent_universet` leser `rader[-1]['date']` utenfor `try`, så et svar som ikke er en ikke-tom liste med `date` i siste rad, stopper hele hentingen etter at kallene er brukt, og ingenting lagres. Det går mot AD-15 og NFR-03. Et slikt svar gir nå feilen «svar med feil form» for symbolet, og de andre hentes og lagres likevel. Story 2.0 i `epics.md` har fått samme kontrollpunkt, og Oppfyller og Begrenses av er utvidet med NFR-03 og `AD-15`.

## I/O & Edge-Case Matrix

| Punkt | Tilstand | Forventet |
|---|---|---|
| Nøkkel | `requests` gir en HTTP-feil (500), med adressen og nøkkelen i teksten | Feilteksten er «HTTPError: HTTP 500 Internal Server Error», uten adresse og uten nøkkel |
| Nøkkel | `requests` gir en tilkoblingsfeil (`ConnectionError`) eller tidsavbrudd, med adressen i teksten | Feilteksten er feiltypen, for eksempel «ConnectionError», uten adresse og uten nøkkel |
| Nøkkel | Henteren gir en feil som inneholder nøkkelen | Nøkkelen er byttet med «***» både i utskriften og i `feil` |
| Overskriving | Dagens øyeblikksbilde finnes før kjøringen | Kjøringen stopper før første kall, fila er uendret, og meldingen sier at 0 kall er brukt |
| Overskriving | Fila dukker opp mens kjøringen pågår | Fila skrives ikke over. Meldingen sier at kallene er brukt og ingenting er lagret |
| Form | Henteren gir et svar som ikke er en liste av rader med `date`, for ett symbol | Symbolet får feilen «svar med feil form», og de andre hentes og lagres |

</frozen-after-approval>

## Code Map

- `src/fetch_prices.py` -- `hent_ett_symbol` (66–80): nøkkelen går i `params`. `raise_for_status()` (79) gir `HTTPError` med «for url: …». `requests.get` kan også kaste `ConnectionError`, `Timeout` og andre `RequestException`, alle med adressen i teksten. `hent_universet` (83–121): feilteksten lagres (108) og skrives ut (109). `filnavn` (136–143). `main` (146–166) skriver med `write_text` (158).
- `tests/test_fetch_prices.py` -- 17 tester. `test_en_feil_stopper_ikke_de_andre` (84–96) injiserer `RuntimeError("HTTP 500")` og sjekker at «HTTP 500» står i `feil`. Modulteksten sier at `hent_ett_symbol` ikke røres av noen test. Det endres: den prøves nå med `requests.get` byttet ut, uten nett. `test_ingen_test_her_roerer_nettet` (177) står.
- `tests/conftest.py` sperrer nettet, så en test som når `requests` uten å bytte ut `get`, feiler.
- `requests` 2.34.2. `HTTPError` fra `raise_for_status()` har formen «500 Server Error: Internal Server Error for url: <adresse>».

## Tasks & Acceptance

**Execution:**
- [x] `src/fetch_prices.py` -- `hent_ett_symbol`: `requests.get` og `raise_for_status()` i en `try`. En `requests.HTTPError` blir en ny `HTTPError` med teksten «HTTP <status> <reason>». Enhver annen `requests.RequestException` blir en feil av samme type med bare typenavnet som tekst. Begge kastes `from None`, så den opprinnelige teksten ikke henger med -- nøkkel, lag 1
- [x] `src/fetch_prices.py` -- `hent_universet`: feilteksten som skrives ut og lagres, går gjennom `_uten_noekkel(tekst, api_nokkel)`, som bytter nøkkelen med «***». Gjelder alle unntak fra henteren, også de som ikke kommer fra `requests` -- nøkkel, lag 2
- [x] `src/fetch_prices.py` -- `main` deles, så en ny `kjoer(data_katalog, i_dag, api_nokkel, hent, skriv) -> Path | None` gjør arbeidet og kan testes uten nett. Finnes `data_katalog / filnavn(i_dag)`, stopper den før første kall, og `main` avslutter med kode 0. Fila skrives med `open(fil, "x")`, og finnes den da, skrives den ikke over -- overskriving
- [x] `src/fetch_prices.py` -- `hent_universet`: svaret kontrolleres (en liste der hver rad er en `dict` med `date`) i samme `try` som kallet. Er formen feil, føres «svar med feil form», og løkka går videre -- form (valg A)
- [x] `tests/test_fetch_prices.py` -- tester for nøkkelen, overskrivingen og formen (se Design Notes). `test_en_feil_stopper_ikke_de_andre` beholder navnet, men går gjennom den ekte `hent_ett_symbol` med en falsk 500 -- nøkkel, overskriving

**Acceptance Criteria:**
- Gitt koden fra `baseline_commit`, når de nye testene kjøres, så feiler hver av dem av grunnen i matrisen.
- Gitt mutantene i Design Notes, når hver av dem legges inn én om gangen, så feiler testene for det kontrollpunktet med forventet melding, og ingen andre.
- Gitt hele testsettet lokalt på Windows og i CI på Linux, når det kjøres, så er det grønt begge steder.

## Implementation Notes
**Bygget 26.09**, direkte i økta etter instruksjonen kl. 23:17, på grenen `2-0` (PR #6). Commitene er `55851ea` og rettingene etter gjennomgangen.

- **Tester:** 455 før. 461 etter `55851ea` (6 nye, 1 endret), som planen sa. 468 etter rettingene fra gjennomgangen, med 7 til: tidsavbrudd i tilkoblingstesten, en URL-kodet nøkkel, en kjøring som lykkes (`kjoer` skriver en fil som kan leses og er uten nøkkel), og fire formtilfeller til (rad uten `close`, feilobjekt, liste uten rader og `None`).
- **Mot `baseline_commit`:** alle nye tester feilet. HTTP-testen feilet med «500 Server Error: Internal Server Error for url: …?api_token=<falsk nøkkel>», og tilkoblingstesten med «HTTPSConnectionPool(…): … api_token=<falsk nøkkel>». Testen gjennom `hent_universet` fant nøkkelen i `feil`. Formtesten feilet med `KeyError: 'date'`, fordi hele hentingen stoppet. Den endrede testen fant ikke «HTTP 500», bare «500 Server Error … for url» med nøkkelen. De to overskrivingstestene feilet med `AttributeError`, fordi `kjoer` ikke fantes. `main()` kunne ikke testes uten nett før.
- **Mutanter, én om gangen, mot hele testsettet, etter rettingene:**
  - lag 1 fjernet
  - lag 1 bare for `HTTPError`
  - `HTTPError` beholder `response`
  - `from None` fjernet for `RequestException`
  - lag 2 fjernet
  - lag 2 uten URL-kodet form
  - sjekken før første kall fjernet
  - `"x"` byttet med `"w"`
  - kode 1 byttet med `return None`
  - `mkdir` i `kjoer` fjernet
  - kontrollen av formen fjernet
  - bare `date` kontrolleres
  - tomt svar sjekkes før formen

  Alle ble fanget av testene for sitt kontrollpunkt, og ingen overlevde.
- **Formkontrollen** ligger ikke «i samme `try` som kallet», som oppgaven sa. Den ligger rett etter, før kontrollen av tomt svar. `_riktig_form` kan ikke kaste, så oppførselen er den samme, og rekkefølgen gjør at et feilobjekt eller `None` føres som «svar med feil form» og ikke som «tomt svar». Den krever feltene `eodhd.py` leser (`date`, `close`, `adjusted_close`, `volume`), og at `date` er tekst.
- **`svar.json()`** ligger utenfor lag 1. En feil der gjelder innholdet, ikke adressen, og lag 2 fanger nøkkelen uansett.
- **Kode 1** når fila dukker opp under kjøringen, fordi kallene da er brukt og ingenting lagret. Kode 0 når dagens fil fantes fra før, fordi det ikke er en feil.
- **README-en** (regel 19): hentesteget og avsnittet om kvoten sier nå at en kjøring nummer to samme dag bruker 0 kall.


## Spec Change Log

## Review Triage Log
Tre lag gjennomgikk diffen `1e56e6f..55851ea` for `src/` og `tests/` den 26.09: Blind Hunter (BH), Edge Case Hunter (ECH) og Verification Gap (VG).

| # | Funn | Dom | Bevis | Rute |
|---|---|---|---|---|
| ECH1 | En skriving som feiler halvveis, etterlater en tom fil som stopper senere kjøringer | low | Krever full disk eller I/O-feil. Fila kan slettes for hånd | avvist: lite sannsynlig, og krever en ny vakt |
| ECH2 | `kjoer` bruker kvoten før den feiler på en katalog som ikke finnes | medium | Bare `main` laget katalogen | patch: `mkdir` i `kjoer` før sjekken, og testen for vellykket kjøring bruker en ny katalog |
| ECH3 | Koden skiller ikke «ingenting å gjøre» fra «kall brukt, ingenting lagret» | medium | Begge ga kode 0 | patch: kode 1 når fila dukker opp under kjøringen |
| ECH4 | `reason` som er `None`, gir «HTTP 500 None» | low | `.strip()` hjalp bare for tom tekst | patch: `r.reason or ''` |
| ECH5 | Den nye `HTTPError` beholder `response`, og `response.url` har nøkkelen | medium | Riktig | patch: ingen `response`, og testen sjekker det |
| ECH6 | Lag 2 finner ikke nøkkelen i URL-kodet form | low | `requests` koder `params` | patch: også `quote` og `quote_plus`, og ny test |
| ECH7 | En rad der `date` er `None` eller ikke tekst, godtas | low | Riktig | patch: `date` må være tekst |
| ECH8 | `svar.json()` ligger utenfor lag 1 | low | Feilen gjelder innholdet, ikke adressen, og lag 2 fanger nøkkelen | patch: docstringen sier det |
| ECH9 | Et feilobjekt eller `None` føres som «tomt svar» | low | `if not rader` kom før formkontrollen | patch: formen sjekkes først |
| VG1 | En kjøring som lykkes, er ikke testet, og testene bruker dagens dato | medium | Bare de to veiene som stopper, var testet | patch: ny test, og 22.09 i stedet for dagens dato |
| VG2 | Formkontrollen ligger ikke der spesifikasjonen sa | low | Samme oppførsel, siden `_riktig_form` ikke kan kaste | patch: ført i Implementation Notes |
| VG3 | `from None` for `RequestException` er ikke prøvd | low | Bare HTTP-testen sjekket det | patch: tilkoblingstesten sjekker det |
| BH1 | Formkontrollen ligger feil sted og i feil rekkefølge | low | Samme som ECH9 og VG2 | patch: under ECH9 |
| BH2 | `svar.json()` utenfor lag 1 | low | Samme som ECH8 | patch: under ECH8 |
| BH3 | `response` har nøkkelen | medium | Samme som ECH5 | patch: under ECH5 |
| BH4 | En URL-kodet nøkkel | low | Samme som ECH6 | patch: under ECH6 |
| BH5 | Formkontrollen ser bare etter `date`, ikke prisfeltene `eodhd.py` leser | low | `eodhd.py` leser `close`, `adjusted_close` og `volume` | patch: alle fire felt, og ny test |
| BH6 | Formtesten dekker bare én form | low | Bare en rad uten `date` | patch: fem former |
| BH7 | Tidsavbrudd og `from None` for tilkoblingsfeil er ikke testet | low | Riktig | patch: parametrisert over `ConnectionError` og `Timeout` |
| BH8 | Ingen test av en vellykket kjøring, og nøkkelen er ikke sjekket i fila | medium | Samme som VG1 | patch: under VG1, og testen sjekker fila |
| BH9 | En katalog som mangler | medium | Samme som ECH2 | patch: under ECH2 |
| BH10 | Koden for kall brukt og ingenting lagret | medium | Samme som ECH3 | patch: under ECH3 |
| BH11 | Nøkkelen kreves før det er kjent at den trengs | low | Nøkkelen finnes ved vanlig bruk | avvist: lite sannsynlig å merkes |
| BH12 | README-en er ikke oppdatert (regel 19) | medium | README-en sa «bruker 15 API-kall» og «én full henting per dag» | patch |
| BH13 | «HTTP 500 None» | low | Samme som ECH4 | patch: under ECH4 |
| BH14 | En test har «15» skrevet inn | low | Riktig | patch: `len(AKSJEUNIVERS)` |


## Design Notes

**Nøkkelen, to lag.** Lag 1 er i `hent_ett_symbol`: den kjenner `requests` og vet at adressen er det som lekker. Teksten bygges på nytt av det som er trygt: statuskode og årsak for en `HTTPError`, og bare typenavnet for resten. `from None` kutter kjeden, så heller ikke en traceback viser den gamle teksten. Lag 2 er i `hent_universet`: henteren er injisert, og alt kan kaste. Den fjerner derfor nøkkelen fra enhver tekst før utskrift og lagring. Hvert lag har sin mutant, så ingen av dem hviler på det andre.

**Overskriving, og story 2.3.** 2.0 ser bare etter en fil med dagens navn, og stopper før første kall med meldingen «Dagens øyeblikksbilde <fil> finnes allerede. Hentingen er stoppet før noe kall er brukt (AD-6). 0 kall brukt.» og kode 0. Det er ikke en feil at dagens data finnes. Story 2.3 bygger videre på dette: den sammenlikner med siste forventede børsdag i norsk dato, og gjør null kall også når fila er fra forrige børsdag og det ikke har kommet noen ny. 2.0 gjør det enkleste 2.3 må ha, og låser ikke hvordan 2.3 løses. `open(fil, "x")` er den andre sikringen, for en fil som dukker opp mens kjøringen pågår. Da er kallene brukt, og meldingen sier det.

**Testene** (455 før):
- Nøkkel: HTTP-feil gjennom `hent_ett_symbol` (en ekte `requests.Response` med status 500 og nøkkelen i adressen), tilkoblingsfeil gjennom `hent_ett_symbol`, og en feil med nøkkelen i teksten gjennom `hent_universet`, sjekket både i utskriften og i `feil`. Det er 3 nye.
- Overskriving: dagens fil finnes, så henteren kalles aldri og fila er uendret, og en fil som dukker opp under kjøringen, blir ikke skrevet over. Det er 2 nye.
- `test_en_feil_stopper_ikke_de_andre` endres til å gå gjennom den ekte `hent_ett_symbol` med en falsk 500. Den sjekker at «HTTP 500» står i `feil` og at nøkkelen ikke gjør det.
- Form: ett symbol gir et svar med feil form, og de andre lagres. Det er 1 ny.
- Totalt 6 nye og 1 endret: 461.

**Mutantene**, én per kontrollpunkt og én per lag:
- Lag 1 fjernet (`str(feil)` fra `requests` slippes gjennom): HTTP-testen og tilkoblingstesten på `hent_ett_symbol` feiler.
- Lag 1 gjelder bare `HTTPError`: tilkoblingstesten feiler.
- Lag 2 fjernet: testen gjennom `hent_universet` feiler, både for utskrift og `feil`.
- Sjekken før første kall fjernet: testen «dagens fil finnes» feiler, fordi henteren kalles.
- `open(fil, "x")` byttet med `"w"`: testen «fil dukker opp under kjøringen» feiler.
- Kontrollen av formen fjernet: testen med feil form feiler.

**Arbeidsflyt, som 1.5b:** grenen `2-0` fra `main`. Mellomcommits pushes. PR mot `main`. Gjennomgang med tre lag. Stopp før flettingen og vent på ja. Squash med `Co-authored-by: Joakim Lund`. Testtallene føres i squash-meldingen.

**Etter flettingen:** `epics.md` får «*Ferdig …*» under 2.0, spesifikasjonen settes til done, og 2-0 til review. Oppføringen i `deferred-work.md` merkes løst. `docs/innlevering.md` linje 98 får nytt testtall.

## Verification

**Commands:**
- `uv run pytest -q` -- forventet: grønt, 461
- `uv run pytest -q tests/test_fetch_prices.py` -- forventet: grønt, med de nye testene
- Mutantene over, én om gangen -- forventet: bare testene for kontrollpunktet feiler
