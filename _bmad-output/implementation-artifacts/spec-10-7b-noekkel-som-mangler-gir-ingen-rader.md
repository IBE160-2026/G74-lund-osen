---
title: 'Story 10.7 (10.7b): en nøkkel som mangler, gir ingen rader'
type: 'feature'
created: '2026-10-22'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '07770d8'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-7-egen-noekkel-til-gemini-anthropic-og-openai.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-2b-teksten-i-hentekommandoen.md'
---

## Intent

**Problem:** etter 10.7 (`6b39b80`) gir en nøkkel til Gemini, Anthropic eller OpenAI som mangler, eller som har tegn som ikke kan sendes i en header, en rad i KI-loggen for hver aksje med vurdering. Radene står (FR-604), så ingen aksje får tekst den dagen, heller ikke om nøkkelen legges inn og hentingen kjøres igjen samme kveld. Hos Ollama skrives ingen rader når tjenesten ikke svarer eller mangler modellen, og samme kommando kan kjøres igjen (svar c kl. 23:32, `_ikke_klar` i `src/ki_tekst.py`).

**Grunnlaget:** gruppens svar 22.10 kl. 14:38, b, under «Prioritering» og story 10.7 i `epics.md` og ved «Åpent» i spesifikasjonen 10.7. Det endrer kontrollpunktet i story 10.7 om at en nøkkel som mangler, gir en rad, og snur avvisningen av ECH11 i triagen til 10.7. Instruksjonen er den kl. 14:41 i dagsfila 22.10.

## Kontrollpunktene

- a) De tre tjenestene får `sjekk`, som `OllamaModell`: den gir grunnen når nøkkelen mangler eller har tegn som ikke kan sendes, ellers `None`, og den gjør ingen kall. `lag_ki_tekster` bruker den før første kall, som for Ollama, så KI-steget stopper før noe sendes, uten rader. Utskriften sier variabelen og at man kan legge den inn og hente igjen samme kveld. En feil hos tjenesten etter kallet gir fortsatt en rad med grunnen. README-en, `docs/hjelp.md` og `.env.example` følger med (regel 19).
- b) Testene, med «Ville feilet hvis», med falsk hentefunksjon og uten nett: en nøkkel som mangler eller har tegn som ikke kan sendes, gir ingen rader og ingen kall, og en ny henting samme kveld med nøkkelen gir tekstene; en feil hos tjenesten gir fortsatt en rad med grunnen; nøkkelen står aldri i utskriften.

## Planen, én commit per punkt

1. a) `noekkel_feil` i `src/ki_sky.py` gir grunnen, og `sjekk_noekkel` reiser `ModellFeilet` med den, som før. `sjekk` i `ki_gemini.py`, `ki_anthropic.py` og `ki_openai.py` gir `noekkel_feil` for nøkkelen og variabelen. `_hva_naa` i `ki_tekst.py` sier hva man gjør når grunnen er nøkkelen, og `velg_modell` sier at ingen rader skrives og at man kan legge nøkkelen inn og hente igjen. Docstringene i `ki_tekst.py`, `ki_sky.py` og adapterne rettes. Testene i `tests/test_ki_tjenestene.py` som krever rader når nøkkelen mangler, rettes til det nye i samme commit, så hver commit er grønn. README-en, `docs/hjelp.md` og `.env.example` i samme commit.
2. b) De nye testene i `tests/test_ki_tjenestene.py`.

## Avgjort i spesifikasjonen

- **Sjekken gjør ingen kall.** Den ser bare på nøkkelen, som `sjekk_noekkel` gjør i dag. Om nøkkelen er gyldig, vet man først når tjenesten svarer, og da gir et feilsvar (for eksempel HTTP 401) fortsatt en rad med grunnen, som svaret sier: «En feil hos tjenesten etter kallet gir fortsatt en rad med grunnen.»
- **`sjekk_noekkel` i `lag_tekst` står**, så en adapter som kalles uten sjekken, sender aldri uten nøkkel.
- **`velg_modell` gir fortsatt den valgte modellen** når nøkkelen mangler, ikke `None` og ikke `lokal`, så det aldri blir en overgang til en annen tjeneste (10.7, M1). Steget stopper i `lag_ki_tekster`, der utskriften har antallet aksjer som venter, som for Ollama.

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter:

- **M1:** rader skrives når nøkkelen mangler (`sjekk` gir `None`).
- **M2:** kallet gjøres uten nøkkel (`sjekk_noekkel` tas ut av `lag_tekst`, og `sjekk` gir `None`).

## Det som ikke endres

- Ingen test går på nett, og ingen test kaller en ekte tjeneste (`AD-8`). Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22), og skjemaet i basen endres ikke.
- Den ekte `.env` røres ikke, og ingen nøkkel skrives ut.
- `lokal` og `av`, prompten (versjon 2) og kontrollen endres ikke.
