---
title: 'Story 10.7: egen nøkkel til Gemini, Anthropic og OpenAI'
type: 'feature'
created: '2026-10-22'
status: 'review'
route: 'dispatch'
review_loop_iteration: 1
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

## Avgjort underveis

- **Det felles kallet står i `src/ki_sky.py`** (`761c970`): hentefunksjonen `http`, sjekken av nøkkelen, kallet med feilene, teksten og `modell_id` fra svaret. Hver adapter har fortsatt én injisert hentefunksjon, og standard er `ki_sky.http`, slått opp ved kallet, så en test kan bytte den (gjennomgangen, BH11, VG8). Det erstatter første punkt under «Avgjort i spesifikasjonen» om én `http` i hver fil.
- **Ingen videresending:** `http` sender `allow_redirects=False`. En 30x gir «svarte HTTP 307», og `x-api-key` og `x-goog-api-key` følger ikke med til en annen vert (BH4, VG5).
- **Nøkkelen sjekkes før kallet.** Mangler den, er grunnen «OSE_KI_GEMINI_NOKKEL mangler», uten «i .env», fordi den også kan komme fra miljøet (BH11). Har den et tegn som ikke er ASCII, ikke kan skrives ut, eller et mellomrom, er grunnen «… har tegn som ikke kan sendes, lim den inn paa nytt», og tjenesten kalles ikke. Før ga et slikt tegn `UnicodeEncodeError` fra `http.client`, som stoppet steget uten rader (ECH1, BH6, VG4). `UnicodeError` fra hentefunksjonen gir også en grunn.
- **`ModellFeilet` reises utenfor `except`-blokken**, så feilen fra `requests` ikke henger ved den som `__context__` (BH5, ECH10). `from None` skjulte den bare.
- **Bare `completed` gir tekst** hos Gemini og OpenAI. `incomplete` gir «svaret fra … ble kortet av», og alle andre statuser gir «… ga ingen ferdig tekst». Hos Anthropic gir `stop_reason` `max_tokens` «ble kortet av», og `refusal` «avslo». Hos OpenAI gir en del med type `refusal` «avslo». Det erstatter punktet om avslag under «Avgjort i spesifikasjonen» (VG1, ECH2–ECH4, BH2, BH8).
- **Teksten** settes sammen bare når alle delene er strenger, og en tekst med tegn som ikke kan lagres i UTF-8, gir en grunn i stedet for en feil i basen (ECH6, ECH13). En tom tekst eller bare mellomrom går videre, og `lag_ki_rad` gir grunnen «tom tekst», som for Ollama (BH1).
- **`modell_id`** er `model` fra svaret bare når den, uten mellomrom rundt, begynner med modellen som ble bedt om og er høyst 100 tegn. Ellers er den `None` (ECH5). Det erstatter setningen om `modell_id` under «Avgjort i spesifikasjonen».
- **Utskriften** sier «KI-teksten lages av gemini (gemini-3.5-flash-lite) med noekkelen din. Grunnlaget sendes dit.» når nøkkelen finnes, på samme måte som hentingen sier fra når Ollama-adressen ikke er på maskinen (BH8).
- **README-en og hjelpen** sier at én feil gir ingen tekst for resten av aksjene den kvelden, og at det ikke hjelper å legge inn nøkkelen og hente igjen samme kveld (`43abd75`, BH3, VG9). Modellnavnene står med koden, og en test binder dem til konstantene (VG6).
- **Sitatene:** OpenAI-referansen deler setningen om `store` i to, og bare «Defaults to true when omitted.» er sitert ordrett herfra; resten er gjengitt. Sitatene under «Lagringen» hos Gemini er fra siden om Interactions, https://ai.google.dev/gemini-api/docs/interactions, ikke fra siden om nøkkelen. Referansen for `generateContent` hadde ingen dato for oppdateringen i den delen som ble lest (VG10).
- **Testen i `tests/test_ki_tekst.py`** som krevde «ikke bygget ennaa» for gemini, har fått `ollama` som eksempel på en ukjent verdi. Det nye for gemini står i `tests/test_ki_tjenestene.py` (VG11).

## Mutantene, kjørt

I en fersk klon med `core.autocrlf=false`, slettet etterpå. M1–M3 er fra instruksjonen, kjørt på `c3be49c` og igjen på `43abd75`. N1–N8 dekker mutantene fra Edge Case Hunter som overlevde på `c3be49c`, og rettingene, kjørt på `43abd75`. Alle ble fanget, med sha256 lik HEAD og `git status` tom etter hver.

| # | Mutant | Først i fila (`43abd75`) | Testen for den |
|---|---|---|---|
| M1 | Overgang til lokal i `lag_ki_rad` når den valgte feiler | `test_svar_uten_tekst[anthropic-tomt]`, via nettsperren | `test_en_valgt_tjeneste_som_feiler_gir_ingen_tekst_fra_en_annen[anthropic-noekkel]` |
| M2 | Nøkkelen i adressen (Gemini) | `test_kallet_slik_dokumentasjonen_sier[gemini]` | den samme, og `test_noekkelen_bare_i_den_ene_headeren` |
| M3 | Nøkkelen i grunnen, fra feilen (`ki_sky.py`) | `test_ingen_forbindelse[anthropic-feil2-InvalidHeader]` | `test_ikke_i_feilen_eller_grunnen_naar_feilen_har_den[anthropic-0]` |
| N1 | Gemini sjekker ikke statusen | `test_bare_completed_gir_tekst[failed-gemini]` | den samme |
| N2 | OpenAI sjekker ikke statusen | `test_bare_completed_gir_tekst[failed-openai]` | den samme |
| N3 | Nøkkelen også i kroppen (Gemini) | `test_kallet_slik_dokumentasjonen_sier[gemini]` | den samme |
| N4 | Videresending fulgt | `test_hentefunksjonen_foelger_ingen_videresending` | den samme |
| N5 | `ModellFeilet` reist inne i `except` | `test_ikke_i_feilen_eller_grunnen_naar_feilen_har_den[anthropic-1]` | den samme |
| N6 | `modell_id` uten sjekk | `test_modell_id_fra_svaret[anthropic-en-annen-modell-None]` | den samme |
| N7 | Avkortet tekst godtatt (Anthropic) | `test_kortet_av_hos_anthropic` | den samme |
| N8 | Nøkkelen ikke sjekket for tegn | `test_tegn_som_ikke_kan_sendes[anthropic-\u200b]` | den samme |

## Gjennomgangen

Gjennomgang 22.10 på diffen `92ead71..c3be49c`. Linsene var Blind Hunter (BH, 11 funn, bare diffen), Edge Case Hunter (ECH, 13 funn, med 16 mutanter i en fersk klon som ble slettet etterpå) og Verification Gap (VG, 11 funn). Ingen funn hadde dom høy.

| # | Funn | Dom | Rute |
|---|---|---|---|
| ECH1, BH6, VG4 | Et tegn i nøkkelen som ikke kan stå i en header, stoppet steget uten rader | medium | rettet: sjekken av nøkkelen, og `UnicodeError` gir en grunn |
| VG1, ECH2, ECH3 | Statusene var ikke testet, og OpenAI godtok alt utenom `failed` | medium | rettet: bare `completed`, testet med tekst i svaret |
| BH2, ECH4 | En avkortet tekst ble lagret som hel | medium | rettet: `incomplete` og `max_tokens` gir ingen tekst |
| BH3 | README-en sa at aksjen får raden, men én feil stopper kallene for kvelden | medium | rettet i README-en og hjelpen |
| BH1 | En tom tekst | medium | uten endring i koden: `lag_ki_rad` gir alt «tom tekst»; testet nå |
| BH4, VG5 | Videresending sender nøkkelen videre | low | rettet: `allow_redirects=False` |
| BH5, ECH10 | `from None` lot feilen henge ved som `__context__` | low | rettet: reist utenfor `except` |
| BH7 | Testene av nøkkelen gikk via vaskingen i `_grunn` | low | rettet: feilen fra adapteren testes selv, med nøkler i ekte form |
| BH8 | Avslag hos OpenAI, og ingen beskjed om at grunnlaget sendes ut | low | rettet |
| BH9 | Ingen test av hva som ikke sendes | low | rettet: ingen symboler eller navn i kroppen |
| ECH5 | Hva som helst fra `model` i `modell_id` | low | rettet |
| ECH6 | Tekst som ikke er en streng | low | rettet |
| ECH7 | Nøkkelen i kroppen eller en annen header | low | rettet |
| ECH13 | Et ensomt surrogat stoppet steget i basen | low | rettet |
| VG2, BH10, ECH8 | Grensen og tidsfristen ikke testet | low | rettet |
| VG3 | Adressene testet mot seg selv | low | rettet: adressene står som tekst i testen |
| VG6 | Ingenting bandt README-en til koden | low | rettet |
| VG7 | Tester uten «Ville feilet hvis» | low | rettet |
| VG9 | En nøkkel som mangler, bruker opp dagens rader | low | rettet i README-en og hjelpen; atferden står, som story 10.7 sier |
| ECH11 | En `sjekk` for nøkkelen ville gitt «kjør igjen» som for Ollama | low | avvist: story 10.7 sier «ingen tekst og en rad i loggen». Ført under «Åpent» |
| ECH12 | En tom variabel i miljøet slår en nøkkel i `.env`, og «Bearer » limt inn | low | avvist: samme regel som de to OSE_KI-variablene; en feil nøkkel gir HTTP 401 og en rad |
| ECH9 | Mellomrom fjernes to steder | nit | uten endring: ufarlig |
| VG8 | `andre_kalt` byttet en `http` som ikke ble brukt | nit | rettet: adapterne slår opp `ki_sky.http` ved kallet |
| VG10 | Sitatene om `store` og kilden under «Lagringen» | nit | rettet under «Avgjort underveis» |
| VG11 | Ordlyden om testen i `test_ki_tekst.py`, og avslag hos OpenAI | nit | rettet |
| BH11 | Ordlyden «som har en gratis nøkkel», «mangler i .env», og `http` i tre filer | nit | rettet |

## Åpent

- **Modellene til Anthropic og OpenAI** er valgt her, som de minste og raskeste, fordi avgjørelsen 04.10 bare navngir modellen til Gemini. Gruppen kan velge andre. Det er én konstant i hver fil.
- **En nøkkel som mangler** gir rader for dagen, etter story 10.7. En `sjekk` før første kall, som for Ollama (svar c kl. 23:32), ville latt brukeren legge inn nøkkelen og kjøre igjen samme kveld (ECH11). Det er gruppens valg.
- **Vilkårene** ble lest 04.10 og 05.10 (`docs/kilder-og-rettigheter.md`), og er ikke lest på nytt her.

## Det som ikke endres

- Ingen test går på nett, og ingen test kaller en ekte tjeneste (`AD-8`). Ingen API-kall utover kvotesjekken.
- `data/db/ose.db` og `data/db/demo.db` røres ikke, og skjemaet i basen endres ikke.
- Den ekte `.env` røres ikke, og ingen nøkkel skrives ut.
- Briefen står.
