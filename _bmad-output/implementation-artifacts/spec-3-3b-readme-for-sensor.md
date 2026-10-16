---
title: 'Story 3.3b: README-en for sensor'
type: 'docs'
created: '2026-10-16'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '1806484'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3-readme-slik-kjoerer-du-den.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-4-demoversjonen.md'
---

## Intent

**Problem:** README-en er det første sensor leser. «Status» sto stille fra 12.10 og nevnte ikke KI-delen på aksjesiden, ingen bilde viste hvordan appen ser ut, «Tester» sa ikke hvordan testene kjøres uten Docker, og «Kom i gang» sa ikke at demoen er veien for å se appen med en gang på dagtid en børsdag.

**Approach:** fem punkter, ett per commit, med testene for README-en rettet eller skrevet i samme commit.

## Beslutningene

Instruksjonen 16.10 kl. 15:59 (`docs/ai-prompts/2026-10-16.md`) sier at gruppen sa ja til de fem punktene 15.10 kl. 22:54. Svaret er ikke ført i dagsfila for 15.10 eller noe annet sted i repoet, så tidspunktet står her slik instruksjonen oppgir det. Punktene er beslutninger, med punkt d uten `--hent-foer-kl-22` etter svar 3 i [spesifikasjonen for 3.3](spec-3-3-readme-slik-kjoerer-du-den.md):

- **a) Statusen.** Det som er flettet siden sist, legges til med vanlige ord, og «Neste:» følger rekkefølgen i `epics.md`: resten av KI-laget først (svar 10 15.10 kl. 14:47), så rekkefølgen fra 14.10 kl. 22:19 og 22:25.
- **b) Et skjermbilde av oversikten i demoen,** 1280 px bredt, med «Eksempeltall» synlig, i `docs/bilder/`, med en alt-tekst som sier at det er demoen. Demobasen lages i en midlertidig mappe, og serveren går på 127.0.0.1 med en ledig port, uten å stoppe servere som kjører. `test_ingen_bilder_utenom_ci_merket` godtar CI-merket og dette ene bildet, og ingen flere.
- **c) «Tester»:** hvordan testene kjøres på en ren maskin uten Docker, med uv og Python-versjonen fra `pyproject.toml`, `uv sync` og `uv run pytest`, og hva man skal se: alle består, og noen hoppes over på Windows, med grunnen. Ikke et fast testtall.
- **d) «Kom i gang»:** på dagtid en børsdag er demoen veien for å se appen med en gang. Steg 8 i den ekte versjonen og raden «Klar» i tabellen nevner også helgen, slik `docs/hjelp.md` gjør.
- **e) «Du trenger»:** versjonene, Docker Desktop slik den er prøvd, og Python for veien uten Docker.

Skjermbildet erstatter «uten bilder» (svar 4, 11.10). Regelen fra 25.09 står: bildet viser bare demoen, aldri ekte kurser (regel 16). Svar 3 i 3.3 står også: `--hent-foer-kl-22` står verken i README-en eller i `docs/hjelp.md`, fordi en henting før dagens kurser finnes, kan låse dagen.

**Plassen til bildet:** testen fra beslutningen kl. 23:41 (`test_til_faglaerer_og_kom_i_gang_foer_status`) krever at ingenting står mellom beskrivelsen og «Til faglærer». Bildet står derfor rett under lista «Til faglærer» og over «Kom i gang», øverst i README-en, og den beslutningen står.

**Bildet tas på nytt når oversikten endres.** Skriptet som lager det, er beskrevet under «Bildet».

## Boundaries & Constraints

- Ingen API-kall utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke.
- Bildet lages fra demobasen i en midlertidig mappe, aldri fra `data/db/ose.db` (regel 16 og 22).
- Ingen kode i `src/` endres.
- Ingen kommando i «Kom i gang» endres, så tabellene i §9 i `docs/kvalitetssikring.md` står.

## Bildet

`docs/bilder/oversikten-demo.png` er toppen av oversikten i demoen, 1280 × 1000 px, tatt 16.10 med Edge uten vindu (headless). **Bildet tas på nytt når oversikten endres,** i samme commit som endringen, slik:

1. Lag demobasen i en midlertidig mappe (`tempfile.TemporaryDirectory()`), med `lagring_sqlite.BASE_STI` satt dit før `demo.lag_demobase(demo_sti())`, aldri i `data/`.
2. Sett `OSE_DEMO=1`, importer `app`, og start `waitress.server.create_server(app.app, host="127.0.0.1", port=...)` i en tråd, med en port som er ledig (`socket.bind(("127.0.0.1", 0))`). Ingen server som kjører, stoppes.
3. Sjekk at siden har «Eksempeltall», og ta bildet med `msedge --headless --disable-gpu --hide-scrollbars --window-size=1280,1000 --screenshot=<fil> http://127.0.0.1:<port>/`, med en egen `--user-data-dir` i den midlertidige mappa.
4. Lukk serveren. Den midlertidige mappa slettes med basen.

Testene i `TestSkjermbildet` krever at fila er en PNG som er 1280 px bred, at alt-teksten sier at det er demoen, at bildet står under «Til faglærer» og over «Kom i gang», og at `docs/bilder/` bare har dette bildet.

