---
title: 'Story 10.7 (10.7b): en nøkkel som mangler, gir ingen rader'
type: 'feature'
created: '2026-10-22'
status: 'review'
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

## Avgjort underveis

- **`velg_modell` sier bare hva som er galt**: «… mangler i .env og i miljoeet. KI-teksten lages ikke foer den er lagt inn.», eller grunnen og «KI-teksten lages ikke foer den er rettet.». Om noe venter på teksten, og om man kan hente igjen, vet først `lag_ki_tekster`, så løftet om radene står bare der (`d7feed6`, VG1, BH2, ECH3). Det erstatter ordlyden i punkt a under «Planen» om at `velg_modell` sier at ingen rader skrives.
- **Rådet** sier «Legg noekkelen inn eller rett den i .env, eller i miljoeet, som gaar foran», fordi miljøet går foran `.env` (`ki_innstillinger`), og fordi en nøkkel med feil tegn alt står der (BH1, ECH1, ECH2). At en tom variabel i miljøet skjuler nøkkelen i `.env`, er eldre enn 10.7b og står, som ECH12 i triagen til 10.7.

## Mutantene, kjørt

I en fersk klon med `core.autocrlf=false`, slettet etterpå, én om gangen med `-x`, med kopi før og sha256 lik HEAD etter hver. Kjørt på `6d0981c` og igjen på `d7feed6`, med `tests/test_ki_tjenestene.py` og `tests/test_ki_tekst.py`, og en gang til med bare testen for hele hentingen.

| # | Mutant | Først i fila (`d7feed6`) | Testen for hele hentingen |
|---|---|---|---|
| M1 | Rader skrives når nøkkelen mangler: `sjekk` gir `None` i de tre adapterne | `test_en_valgt_tjeneste_som_feiler_gir_ingen_tekst_fra_en_annen[anthropic-noekkel]` | `test_ingen_rader_og_ingen_kall[anthropic-mangler]` |
| M2 | Kallet gjøres uten nøkkel: som M1, og `sjekk_noekkel` tatt ut av `lag_tekst` | `test_noekkelen_mangler[anthropic-]` | `test_ingen_rader_og_ingen_kall[anthropic-mangler]` |

## Gjennomgangen

Gjennomgang 22.10 på diffen `d21a8bd..6d0981c`. Linsene var Blind Hunter (BH, 5 funn, bare diffen), Edge Case Hunter (ECH, 6 funn) og Verification Gap (VG, 5 funn), hver for seg og uten å endre noe i repoet. 16 funn ble 13 rader. Ett hadde dom medium, og det er rettet. Rettingene er i `d7feed6`, utenom VG3 og VG4, som føres etter flettingen.

| # | Funn | Dom | Rute |
|---|---|---|---|
| VG1 | Testen av valget sjekket ikke det nye løftet når nøkkelen mangler | medium | rettet: testen krever den nye setningen og ingen setning om radene |
| BH2, ECH3 | `velg_modell` lovet «ingen rader» og «hent igjen» før dagen var kjent, og dobbel melding | low | rettet: valget sier bare hva som er galt |
| BH1, ECH1, ECH2 | Rådet sa bare `.env`, men miljøet går foran, og en nøkkel med feil tegn står alt der | low | rettet: rådet nevner begge og «rett den» |
| VG2 | Setningene i README-en og hjelpen var ikke bundet til en test | low | rettet: to setninger i README-testen, og en test for hjelpen |
| VG3 | Mutantene og testene som fanget dem, sto ikke i repoet | low | rettet: tabellen over, og radene i kvalitetssikringen etter flettingen |
| ECH4 | Ved et nytt forsøk samme kjøring (`nytt_forsoek` i `fetch_prices.py`) settes modellen til `None` etter en sjekk som sa nei, og aksjene som først får vurdering der, nevnes ikke | low | uten endring: eldre enn 10.7b, ingen rader skrives, og en ny kjøring samme kveld lager dem |
| BH3 | «nøkkel» med ø i en utskrift | nit | avvist: overskriften i README-en siteres ordrett, så den kan finnes |
| BH4 | Testen for hele hentingen hadde bare et usynlig tegn, ikke mellomrom eller tabulator | nit | rettet |
| BH5 | Testen om overgang sjekket ingenting om utskriften uten nøkkel | nit | rettet: stoppmeldingen |
| ECH5 | En nøkkel i riktig form som tjenesten avviser, gir rader for alle | nit | avvist: svaret kl. 14:38 sier at en feil hos tjenesten etter kallet gir en rad |
| ECH6 | Ingen grense for lengden på nøkkelen | nit | avvist: sjekken ser bare på tegnene, og tjenesten avgjør resten, med en rad |
| VG4 | Kontrollpunktet i story 10.7 leses fortsatt alene som at en nøkkel som mangler, gir en rad | nit | rettet etter flettingen: en datert linje under story 10.7 |
| VG5 | Nøkkelen kan ikke stå i utskriften når den mangler | nit | uten endring: tilfellene med tegn gjør jobben |

## Det som ikke endres

- Ingen test går på nett, og ingen test kaller en ekte tjeneste (`AD-8`). Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22), og skjemaet i basen endres ikke.
- Den ekte `.env` røres ikke, og ingen nøkkel skrives ut.
- `lokal` og `av`, prompten (versjon 2) og kontrollen endres ikke.
