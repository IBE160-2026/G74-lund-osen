---
title: 'Story 2.0: Hentingen lekker ikke nøkkelen og skriver ikke over et øyeblikksbilde'
type: 'bugfix'
created: '2026-09-26'
status: 'ready-for-dev'
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
- [ ] `src/fetch_prices.py` -- `hent_ett_symbol`: `requests.get` og `raise_for_status()` i en `try`. En `requests.HTTPError` blir en ny `HTTPError` med teksten «HTTP <status> <reason>». Enhver annen `requests.RequestException` blir en feil av samme type med bare typenavnet som tekst. Begge kastes `from None`, så den opprinnelige teksten ikke henger med -- nøkkel, lag 1
- [ ] `src/fetch_prices.py` -- `hent_universet`: feilteksten som skrives ut og lagres, går gjennom `_uten_noekkel(tekst, api_nokkel)`, som bytter nøkkelen med «***». Gjelder alle unntak fra henteren, også de som ikke kommer fra `requests` -- nøkkel, lag 2
- [ ] `src/fetch_prices.py` -- `main` deles, så en ny `kjoer(data_katalog, i_dag, api_nokkel, hent, skriv) -> Path | None` gjør arbeidet og kan testes uten nett. Finnes `data_katalog / filnavn(i_dag)`, stopper den før første kall, og `main` avslutter med kode 0. Fila skrives med `open(fil, "x")`, og finnes den da, skrives den ikke over -- overskriving
- [ ] `src/fetch_prices.py` -- `hent_universet`: svaret kontrolleres (en liste der hver rad er en `dict` med `date`) i samme `try` som kallet. Er formen feil, føres «svar med feil form», og løkka går videre -- form (valg A)
- [ ] `tests/test_fetch_prices.py` -- tester for nøkkelen, overskrivingen og formen (se Design Notes). `test_en_feil_stopper_ikke_de_andre` beholder navnet, men går gjennom den ekte `hent_ett_symbol` med en falsk 500 -- nøkkel, overskriving

**Acceptance Criteria:**
- Gitt koden fra `baseline_commit`, når de nye testene kjøres, så feiler hver av dem av grunnen i matrisen.
- Gitt mutantene i Design Notes, når hver av dem legges inn én om gangen, så feiler testene for det kontrollpunktet med forventet melding, og ingen andre.
- Gitt hele testsettet lokalt på Windows og i CI på Linux, når det kjøres, så er det grønt begge steder.

## Implementation Notes

## Spec Change Log

## Review Triage Log

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
