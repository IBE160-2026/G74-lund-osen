---
title: 'Story 10.7: egen nøkkel til Gemini, Anthropic og OpenAI'
type: 'feature'
created: '2026-10-22'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '92ead71'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/docs/kilder-og-rettigheter.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-2b-teksten-i-hentekommandoen.md'
---

## Intent

**Problem:** briefen v8 lover egne nøkler til Gemini, Anthropic og OpenAI i v1 (svaret 19.10 kl. 16:12, FR-608). I dag sier hentingen «OSE_KI_TJENESTE=gemini er ikke bygget ennaa (story 10.7)» og lager ingen tekst (`velg_modell` i `src/ki_tekst.py`).

**Grunnlaget:** story 10.7 i `epics.md`, med linja 05.10 kl. 16:53 om avsnittet i README-en, FR-608 i `prd.md`, og avgjørelsen 04.10 i `docs/kilder-og-rettigheter.md`, «Betingelse 4 og KI-tjenestene (2026-10-04)»: standard er den lokale modellen, og den som vil, kan bruke sin egen nøkkel til «Gemini 3.5 Flash-Lite, med gratis nøkkel, til Anthropic API eller til OpenAI API». Ingen nøkkel følger med appen eller repoet (`AD-12`). Rekkefølgen er 10.7, README-rettingen, 8.6, så 2.12 (svaret 22.10 kl. 00:09). Instruksjonen er den kl. 09:55 i dagsfila 22.10.

## Kontrollpunktene

- a) Adapterne `ki_gemini.py`, `ki_anthropic.py` og `ki_openai.py` med porten `Modell`, som `ki_lokal.py`, hver med én injisert hentefunksjon og uten nye pakker. `OSE_KI_TJENESTE` velger tjenesten, og nøkkelen leses fra `OSE_KI_GEMINI_NOKKEL`, `OSE_KI_ANTHROPIC_NOKKEL` eller `OSE_KI_OPENAI_NOKKEL` i miljøet eller `.env`, slik de to OSE_KI-variablene leses i dag. Nøkkelen sendes bare i en header, aldri i adressen. Mangler nøkkelen, eller feiler tjenesten, blir det ingen tekst og en rad i loggen, og ingen overgang til en annen tjeneste. `lokal` og `av` virker som før, med samme prompt, så uka med logget drift med prompten versjon 2 ikke påvirkes.
- b) `.env.example`, README-en (avsnittet om egne nøkler) og `docs/hjelp.md` følger med (regel 19). README-en sier at grunnlaget da sendes til tjenesten man har valgt, at det kan koste hos dem, at nøkkelen aldri skal deles, og at man ikke må ha sagt ja til at tjenesten trener på innholdet.
- c) Testene, med «Ville feilet hvis», med falsk hentefunksjon og uten nett: kallet og svaret for hver tjeneste; nøkkelen som mangler og feilen fra tjenesten; nøkkelen står aldri i grunnen, loggen, utskriften eller på en side; en valgt tjeneste som feiler, gir ingen tekst fra en annen. Mutantene M1–M3 under.

## Kallene, slik dokumentasjonen sier

Alt under er lest 22.10.2026, før grenen ble laget kl. 10:02.

### Gemini

- **Modellen** er Gemini 3.5 Flash-Lite, som avgjørelsen 04.10 sier. Modellsiden, https://ai.google.dev/gemini-api/docs/models, sist oppdatert 2026-10-21 UTC, har modellkoden `gemini-3.5-flash-lite`.
- **Kallet** er Interactions API. Fra https://ai.google.dev/gemini-api/docs/interactions, sist oppdatert 2026-10-15 UTC: Interactions API «is now Generally Available and recommended for all new projects», og «the original `generateContent` API remains fully supported». Eksempelet der er:

  ```
  curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
    -H "Content-Type: application/json" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -d '{
      "model": "gemini-3.8-flash",
      "input": "Tell me a short story about a time-traveling lighthouse."
    }'
  ```

- **Nøkkelen i en header.** Referansen for `generateContent`, https://ai.google.dev/api/generate-content, viser nøkkelen i adressen: «`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$GEMINI_API_KEY`». Siden om nøkkelen, https://ai.google.dev/gemini-api/docs/api-key, sist oppdatert 2026-10-06 UTC, og eksempelet over sender den i headeren `x-goog-api-key`. Det er grunnen til at adapteren bruker Interactions API: der viser dokumentasjonen nøkkelen i en header, slik kontrollpunkt a krever.
- **Lagringen.** Fra samme side: «By default, the API stores all Interaction objects (`store=true`).» og «If you don't want this, you can set `store=false` in your request.» Adapteren sender `"store": false`.
- **Svaret.** Fra referansen, https://ai.google.dev/api/interactions-api: teksten står i `steps`, der et steg med `"type": "model_output"` har en liste `content` med `"type": "text"` og `text`, og svaret har `model` og `status`, med blant annet `completed`, `failed` og `incomplete`. `generation_config` har `max_output_tokens` og ingen temperatur.

### Anthropic

- **Modellen** er Claude Haiku 5.5, `claude-haiku-5-5`. Avgjørelsen 04.10 sier «Anthropic API» uten modell. Fra https://platform.claude.com/docs/en/about-claude/models/overview, lest 22.10.2026: Haiku 5.5 er «For high-volume, latency-sensitive tasks such as classification, extraction, and routing», med «Fastest» og den laveste prisen i tabellen. Teksten er tre setninger per aksje, 15 ganger en kveld.
- **Kallet.** Fra https://platform.claude.com/docs/en/get-started, lest 22.10.2026:

  ```
  curl https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5-5",
      "max_tokens": 1000,
      "messages": [ { "role": "user", "content": "…" } ]  (meldingen forkortet her)
    }'
  ```

- **Svaret** har `"content": [ { "type": "text", "text": "…" } ]`, `"model"` og `"stop_reason"` (samme side). Fra https://platform.claude.com/docs/en/build-with-claude/working-with-messages, lest 22.10.2026: «Refusal responses (`stop_reason: "refusal"`) also include a `stop_details` object».
- **Ingen temperatur.** Samme side: «The `temperature`, `top_p`, and `top_k` sampling parameters are not supported on Claude 4.7 and later models […]. Setting them to a non-default value returns a 400 error».

### OpenAI

- **Modellen** er GPT-6 Luna, `gpt-6-luna`. Avgjørelsen 04.10 sier «OpenAI API» uten modell. Fra https://developers.openai.com/api/docs/models, lest 22.10.2026: «Our most efficient model for focused, high-volume tasks», med de laveste prisene blant de tre første modellene.
- **Kallet.** Fra https://developers.openai.com/api/docs/quickstart, lest 22.10.2026: `curl "https://api.openai.com/v1/responses"`, `-H "Content-Type: application/json"` og `-H "Authorization: Bearer $OPENAI_API_KEY"`, med `"model"` og `"input"` i kroppen.
- **Lagringen.** Fra referansen, https://developers.openai.com/api/reference/resources/responses/methods/create, lest 22.10.2026: `store` er «Whether to store the generated model response for later retrieval via» «API.» «Defaults to true when omitted.» Adapteren sender `"store": false`. `max_output_tokens` er «An upper bound for the number of tokens that can be generated for a response».
- **Svaret.** Samme referanse: en melding i `output` har `type` «Always `message`», og `content` med `ResponseOutputText`, der `type` er «Always `output_text`» og `text` er «The text output from the model.» Et avslag står som `ResponseOutputRefusal`.

## Planen, én commit per punkt

1. a) `src/ki_gemini.py`, `src/ki_anthropic.py` og `src/ki_openai.py`, valget i `src/ki_tekst.py`, og testen i `tests/test_ki_tekst.py` som krevde «ikke bygget ennaa» for gemini, rettet til det nye.
2. b) `.env.example`, README-en og `docs/hjelp.md`.
3. c) Testene i `tests/test_ki_tjenestene.py`, `ki_av` i `tests/conftest.py`, og mutantene.

## Avgjort i spesifikasjonen

- **Én hentefunksjon per adapter**, som `http` i `ki_lokal.py`, men med headerne: `http(url, headere, json, tidsfrist)` gir status og JSON-svaret, med `requests`, som alt er en pakke i prosjektet. Adressen er en konstant i hver fil, og det er ingen variabel for å endre den, så nøkkelen bare går til tjenesten den hører til.
- **Kroppen** er det dokumentasjonen viser, og ikke mer: modellen og prompten, `"store": false` hos Gemini og OpenAI, og en øvre grense på 1024 tokens (`max_output_tokens` i `generation_config` hos Gemini, `max_tokens` hos Anthropic, `max_output_tokens` hos OpenAI). Anthropic krever `max_tokens`. Ingen temperatur og ingen seed, så `temperatur` og `seed` i raden er `None`, som FR-604 sier for det som ikke kan vites.
- **Prompten** er den samme som for den lokale modellen, `lag_prompt` i `ki_prompt.py`, versjon 2, sendt som én tekst (`input` hos Gemini og OpenAI, én melding fra `user` hos Anthropic). `lokal` og `av` endres ikke, og `ki_prompt.py` og `ki_lokal.py` røres ikke.
- **Raden** får tjenesten (`gemini`, `anthropic` eller `openai`, som `TJENESTER` i `kilogg.py` alt har) og modellnavnet adapteren sendte, i `modell`. Modellen tjenesten sier svarte, fra `model` i svaret, står i `modell_id` når det er en tekst. `maskinvare` og `ollama_versjon` er `None`, som `KIRad` krever for andre tjenester enn `lokal`.
- **Mangler nøkkelen**, kalles ikke tjenesten. `lag_tekst` reiser `ModellFeilet` med navnet på variabelen, så raden for første aksje sier «modellen feilet: OSE_KI_GEMINI_NOKKEL mangler i .env», og de andre får raden om at modellen ikke ble kalt (`lag_ki_tekster`, gjennomgangen av PR F, BH3). Hentingen sier det også når tjenesten velges. Det er det story 10.7 sier: ingen tekst og en rad i loggen. Det er ulikt Ollama som ikke svarer (svar c kl. 23:32), der ingen rader skrives og samme kommando kan kjøres igjen. Adapterne har ingen `sjekk`, så `_ikke_klar` regner dem som klare, som docstringen der alt sier.
- **Grunnen** sier bare tjenesten og HTTP-statusen, tidsavbruddet, at tjenesten ikke svarer, eller typen på feilen. Teksten fra tjenesten, feilmeldingen fra `requests` og kroppen i et feilsvar kommer aldri med, fordi de kan inneholde nøkkelen eller adressen. `_grunn` i `ki_modell.py` fjerner i tillegg det som ser ut som en nøkkel.
- **Ingen overgang.** `velg_modell` gir én modell for kjøringen og ingen reserve. Feiler den, gir `lag_ki_tekster` rader uten tekst, og ingen annen modell kalles.
- **Et avslag** (`stop_reason` `refusal` hos Anthropic) eller et svar uten tekst gir `ModellFeilet`, som en tom tekst hos Ollama. Et svar med `status` `failed` hos Gemini gir også det.
- **Docker:** `hent` i `compose.yaml` har `env_file: .env`, så nøklene kommer med uten endring i compose.

## Mutantene

Én om gangen med `-x` på `tests/test_ki_tjenestene.py`, med kopi av fila før og sha256 lik HEAD etter hver:

- M1: overgang til lokal når den valgte feiler
- M2: nøkkelen i adressen
- M3: nøkkelen i grunnen

## Åpent

- **Modellene til Anthropic og OpenAI** er valgt her, som de minste og raskeste, fordi avgjørelsen 04.10 bare navngir modellen til Gemini. Gruppen kan velge andre. Det er én konstant i hver fil.
- **Vilkårene** ble lest 04.10 og 05.10 (`docs/kilder-og-rettigheter.md`), og er ikke lest på nytt her.

## Det som ikke endres

- Ingen test går på nett, og ingen test kaller en ekte tjeneste (`AD-8`). Ingen API-kall utover kvotesjekken.
- `data/db/ose.db` og `data/db/demo.db` røres ikke, og skjemaet i basen endres ikke.
- Den ekte `.env` røres ikke, og ingen nøkkel skrives ut.
- Briefen står.
