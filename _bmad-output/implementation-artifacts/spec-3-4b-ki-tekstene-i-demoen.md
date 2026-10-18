---
title: 'Story 3.4b: KI-tekstene i demoen'
type: 'feature'
created: '2026-10-18'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '5d5dc87'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/kvalitetssikring.md'
---

## Intent

**Problem:** demoen har ingen KI-tekst, så faglærer og sensor ser ikke hva KI-laget gjør uten Ollama. Story 3.4b i `epics.md` (gruppens beslutning 05.10 kl. 16:53, og svaret 17.10 kl. 22:06 om når den bygges).

**Grunnlaget:** instruksjonen 18.10 kl. 19:51. PR-en flettes når vilkårene i steg 4 i instruksjonen holder.

## Kontrollpunktene fra storyen

- Demoen får ferdige KI-tekster, laget med Gemma og merket med modellen.
- De ferdige tekstene ligger i en fil i repoet, fordi demobasen aldri ligger der (`AD-9`). Demokommandoen leser fila og skriver tekstene inn i demobasen.
- En test krever at grunnlaget for hver tekst stemmer med demodagen den hører til (FR-602).
- Tekstene består kontrollen i FR-603, og raden har tjenesten, modellen og hvordan modellen kjørte (FR-604, FR-605).
- **Ville feilet hvis:** demoen endret seg, og tekstene ble stående. Da forklarer KI en annen dag enn den siden viser.

## Planen, én commit per punkt

1. a) Tekstene: `src/demo_ki.py` lager dem én gang for siste demodag (`SLUTTDATO`), for hver demoaksje med en vurdering den dagen, med `lag_ki_tekster` fra hentingen (grunnlaget, prompten versjon 2, kontrollen og raden), klokka satt til demodagen kl. 21:30 og en demobase i en midlertidig mappe. Radene lagres med et avtrykk av grunnlaget i `src/demo_ki_tekster.json`.
2. b) Demoen: `demo.py` leser fila og skriver radene i KI-loggen i demobasen. «Status» i README-en og «Hva er demoen?» i `docs/hjelp.md` sier at demoen har KI-teksten.
3. c) Testene i `tests/test_demo_ki.py`, og mutantene.

## Avgjort i spesifikasjonen

- **Navnene:** modulen er `src/demo_ki.py`, og fila er `src/demo_ki_tekster.json`. Fila ligger under `src/`, så imaget har den (`COPY src/ src/` i `Dockerfile`), og `.dockerignore` holder den ikke ute.
- **Bare siste demodag,** som instruksjonen sier. Storyen sier «de oppdiktede dagene», men aksjesiden viser KI-teksten for dagen den viser, og i demoen er det `SLUTTDATO`. De andre dagene har ingen rader, og siden sier det samme som i den ekte versjonen for en dag uten rad.
- **Ingen ny runde (FR-604):** `lag_ki_tekster` kalles én gang. Består en tekst ikke kontrollen, står raden som den ble, og aksjesiden viser grunnen i stedet for teksten, som i appen.
- **Demokommandoen importerer ikke modellen:** `demo_ki.py` importerer `ki_tekst`, `ki_lokal` og `demo` bare inne i funksjonen som lager tekstene. Demokommandoen bruker bare lesingen, så den importerer verken `requests` eller Ollama.
- **Lekkasjesjekken i morgensjekken** flagger hver sporede `.json` utenfor `.claude/` og `_bmad/`. `src/demo_ki_tekster.json` får et unntak med akkurat den stien. Fila har oppdiktede tall og tekster om dem, ikke rådata fra kildene (regel 16).

## Boundaries

- Ingen kall til EODHD: ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Demobaser bare i midlertidige mapper.
- Tekstene lages med Gemma i Ollama på denne maskinen, én gang. Ingen test kaller Ollama.
