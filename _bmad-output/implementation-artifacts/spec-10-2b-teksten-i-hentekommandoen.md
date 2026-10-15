---
title: 'Story 10.2, PR F (10.2b): teksten lages i hentekommandoen og lagres i KILogg'
type: 'feature'
created: '2026-10-15'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '5586924'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Porten `Modell`, prompten og kontrollen i FR-603 er flettet (PR E), og `KILogg` står i basen (4.3). Hentingen lager likevel ingen KI-tekst. Story 10.2 krever at teksten lages i hentekommandoen, rett etter vurderingen (AD-17), og at hentingen går som før når modellen feiler, mangler eller er slått av (NFR-04).

**Approach:**
- `src/ki_lokal.py`: `OllamaModell` mot Ollama med én injisert hentefunksjon (AD-2), `think: false`, temperatur 0 og seed 42, og modell-ID, maskinvare og Ollama-versjonen lest fra Ollama (FR-604, FR-605).
- `src/ki_tekst.py`: `velg_modell` leser `OSE_KI_TJENESTE` og `OSE_KI_OLLAMA_URL` (svar 5 og 8). `lag_ki_tekster` skriver én rad per aksje med vurdering og uten rad, og en feil der stopper aldri hentingen.
- `src/fetch_prices.py`: steget kjøres etter vurderingene, når basen alt har kursene, og etter et nytt forsøk. `main` velger modellen.
- `compose.yaml`: Ollama i profilen `ki`, med porten bare på 127.0.0.1, volumet `ose-ki-ollama` og grafikkortet. `hent` når Ollama på `http://ollama:11434`.
- `.env.example` med `OSE_KI_TJENESTE=av`, README-avsnittet «Den lokale modellen (KI-teksten)», og Prøve 3 i `docs/kvalitetssikring.md` §9.

PR F i planen for KI-laget. Flettes ikke i denne instruksjonen: en dag uten henting, etter en avtalt prøvekjøring mot en kopi av basen (instruksjonen kl. 22:36).

## Planen

Planen for KI-laget ble vist i chatten 15.10 kl. 15:43 og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-15.md` (`5ce64f6`). Testtallet før: 2037 bestått og 17 hoppet over på main (`808948c`).

## Svarene

*Lagt til 2026-10-15 (gruppens svar på de ti spørsmålene i planen, instruksjonen kl. 15:53):* svarene er beslutninger. Alle ti står under Epic 10 i `epics.md`. De som gjelder denne PR-en:

- Svar 1: kveldshentingen går på PC-en med RTX 4070, med Ollama i Docker, alltid med grafikkort. Compose reserverer grafikkortet for Ollama.
- Svar 2: raden står når den finnes, også når modellen feilet. Modellen kalles ikke for en aksje som har raden.
- Svar 5: `av` er et eget valg i `OSE_KI_TJENESTE`. `.env.example` har `av`, og README-en sier hvordan KI slås på. Uten variabelen gjelder `lokal`.
- Svar 8: `OSE_KI_OLLAMA_URL`, med `http://127.0.0.1:11434` som standard og `http://ollama:11434` i compose. Porten publiseres bare på 127.0.0.1.

**Fra `deferred-work.md`, tatt her:**
- Midnatt under hentingen: `KILogg` avviser datoen (`IkkeInnevaerendeBoersdag`), og steget stopper med beskjed uten å endre utgangskoden.
- Rekkefølgen vurdering, så KI-rad: hver i sin transaksjon. Stopper kjøringen mellom dem, lager samme kommando kjørt igjen radene som mangler, med 0 kall til EODHD. En dag uten rad viser siden som en dag uten KI-tekst (FR-602).

**Mutantene** (planen kl. 15:43): F1 en feil hos modellen stopper hentingen; F2 modellen kalles på nytt når raden finnes; F3 KI-steget kjører før vurderingene; F4 en tekst som ikke besto, logges som bestått; F5 KI-steget gjør et kall til EODHD.

## Boundaries & Constraints

- Ingen API-kall, verken til EODHD utover kvotesjekken eller til en KI-tjeneste, heller ikke Ollama. Modellen og HTTP-funksjonen er falske i testene, og nettsperren stopper en ekte (4.0).
- `src/fetch_prices.py` kjøres ikke, og `ose.db`, `.env` og volumene røres ikke. Grenen bruker bare testbaser (regel 22).
- Utskriften har antall, aldri teksten eller tall fra kildene (regel 16).
- `gemini`, `anthropic` og `openai` kommer i 10.7. Til da gir de ingen KI-tekst og en beskjed, uten stille overgang (FR-608).

## I/O & Edge-Case Matrix

| Inndata | Forventet |
|---|---|
| `OSE_KI_TJENESTE=av` | ingen modell, ingen rader, hentingen som før |
| Uten `OSE_KI_TJENESTE` | `lokal`, `OllamaModell` mot `http://127.0.0.1:11434` |
| Ollama svarer ikke eller gir tidsavbrudd | en rad per aksje om at modellen feilet, kode som før |
| En annen feil i steget | steget stopper med beskjed, kode som før |
| En tekst som ikke består kontrollen | raden med teksten og grunnen, `besto=False` |
| En aksje med grunn i stedet for vurdering | ingen rad |
| Hentingen kjørt igjen samme kveld | radene som finnes, står, og modellen kalles bare for dem som mangler, med 0 kall til EODHD |
| Midnatt passerer før steget er ferdig | steget stopper med beskjed |

</frozen-after-approval>

## Code Map

- `src/ki_lokal.py`: `OllamaModell`, `http`.
- `src/ki_tekst.py`: `ki_innstillinger`, `velg_modell`, `regeltekst`, `lag_ki_tekster`.
- `src/fetch_prices.py`: `kjoer`, `nytt_forsoek` og `main`.
- `compose.yaml`, `.env.example`, `README.md`, `docs/kvalitetssikring.md` §9 (Prøve 3).
- `tests/test_ki_lokal.py`, `tests/test_ki_tekst.py`, `tests/test_docker.py` (`TestOllama`), `tests/conftest.py` (`ki_av`).

## Spec Change Log

## Commitene

Grenen `10-2b-teksten-i-hentingen`, PR #49: `3b592ac` spesifikasjonen; `9bc8b3b` modellen, steget, hentingen, compose, `.env.example`, README og Prøve 3 med testene; `5dd8a00` rettingene fra gjennomgangen; `48838a7` testen som fanger FR2.

## Må avgjøres av gruppen før flettingen

Fra gjennomgangen. Begge gjelder svar 2 og 5 kl. 15:53 og FR-604, så de rettes ikke uten et svar:

1. **Uten `OSE_KI_TJENESTE` gjelder `lokal` (svar 5).** Den ekte `.env` har ikke variabelen. Etter flettingen bruker hver kveldshenting Ollama, også når ingen har startet den (BH1, ECH).
2. **Kjører ikke Ollama, får hver aksje en rad om at modellen feilet, og raden står (FR-604, svar 2).** Da er KI-teksten borte for den dagen, også om Ollama startes og hentingen kjøres igjen. En forhåndssjekk som ikke skriver rader når Ollama ikke svarer, ville gått mot FR-604 og tillegget 05.10 i 10.2, som sier at det blir en rad i loggen (BH2, BH12).

Rettingen gjør det så lite vondt som mulig innenfor svarene: feiler modellen for én aksje, kalles den ikke for resten den kvelden, og de får en rad med grunnen «ikke kalt» (BH3). Det er også en del av spørsmål 2: gruppen kan velge at modellen prøves for hver aksje.

## Review Triage Log

Gjennomgang 15.10 på diffen `main...9bc8b3b`, med Blind Hunter (BH, 16 funn), Edge Case Hunter (ECH, 13) og Verification Gap (VG, 5). Rettingene står i `5dd8a00` og `48838a7`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH | Uten variabelen er KI på, og den ekte `.env` har den ikke | high | **avgjøres av gruppen** (spørsmål 1 over) |
| BH2, BH12 | Kjører ikke Ollama, blir 15 rader om at modellen feilet stående | high | **avgjøres av gruppen** (spørsmål 2 over) |
| BH3 | Henger Ollama, venter hver aksje på tidsfristen, opptil om lag 50 minutter | high | patch: etter første feil kalles ikke modellen for resten, `test_modellen_kalles_ikke_igjen_etter_en_feil` |
| BH4, ECH, VG1 | Et nytt forsøk som stopper tidlig, lot vurderte aksjer stå uten KI-rad, og veien var ikke testet | medium | patch: KI-radene som mangler, lages før et nytt forsøk, `test_et_nytt_forsoek_faar_ki_tekst`, `test_ki_radene_som_mangler_lages_foer_et_nytt_forsoek` |
| BH6, ECH | `OSE_KI_TJENESTE=` (tom) slo KI på | medium | patch: tom eller ukjent verdi gir ingen KI-tekst og en beskjed |
| ECH | `main` kunne stoppe på en `.env` som ikke kan leses, før hentingen | medium | patch: `modell_fra_miljoeet` fanger det (NFR-04) |
| ECH | `except Exception` svelget nettsperren i testene | medium | patch: `AssertionError` går videre, `test_nettsperren_svelges_ikke` |
| ECH | `models` som ikke er en liste ga `TypeError` | medium | patch: `_modeller` sjekker typen |
| BH9, ECH | En kort digest ga en modell-ID kortere enn 12 tegn | low | patch: lengden sjekkes etter «sha256:» |
| ECH, VG3 | Med tjenesten i miljøet ble adressen i `.env` ikke lest, og miljøet vant ikke per nøkkel | medium | patch: per nøkkel, `test_miljoeet_vinner_per_noekkel` |
| ECH | En adresse uten skjema ga 15 rader om at modellen feilet | low | patch: adressen sjekkes, og gir ingen KI-tekst og en beskjed |
| BH13 | En adresse utenfor maskinen sender prompten ut uten beskjed | low | patch: beskjed i utskriften, og README sier «med adressen som står som standard» |
| ECH | Modellen ble kalt etter midnatt før `skriv` avviste datoen | low | patch: børsdagen sjekkes før kallet |
| BH8 | 404 fra Ollama sa ikke at modellen mangler | low | patch: «modellen er ikke hentet (ollama pull gemma4:e4b)» |
| BH10 | En feil i KI-laget ga bare én linje | low | patch: sporet på stderr, utgangskoden som før |
| ECH | Meldingen ved stopp tok ikke med radene som sto fra før | low | patch: tatt med |
| BH11 | Uten grafikkort fra NVIDIA starter ikke Ollama | low | patch: README og Prøve 3 sier det |
| BH14 | Prøve 3 manglet modellen uten pull og en ny kjøring etter en feil | low | patch: steg 7 og 8 |
| BH7 | Testen for nøkler i compose så etter «NOKKEL» | low | patch: «NOEKKEL», «NØKKEL», «KEY», «TOKEN», og ingen variabel utenom adressen og `OSE_DEMO` |
| VG2 | Ingen test så at `main` leser `av` fra `.env` | low | patch: `test_main_leser_av_fra_env` |
| VG4 | Ingen test for en base som ikke kan åpnes i steget | low | patch: `test_basen_som_ikke_kan_aapnes` |
| ECH | Når `skriv_vurderinger` feiler for én aksje, avslutter hentingen før KI-steget | low | avvist: da har basen feilet eller midnatt passert, og KI-steget ville feilet likt. Neste kjøring lager radene |
| BH15 | Tilkoblingen er åpen under modellkallene | avvist | ingen transaksjon er åpen mellom skrivingene: `SqliteKILogg.skriv` styrer sin egen, og lesingen åpner ingen |
| BH16 | Matrisen manglet flere tilfeller | low | patch: testene over. Matrisen er frosset |


## Verification

**Commands:**
- `uv run pytest -q` -- før 2037 bestått og 17 hoppet over på main (`808948c`). 2082 og 17 på `9bc8b3b`. Etter rettingene 2105 og 17 på `5dd8a00`, og samme antall på `48838a7`.

**Mutantene**, kjørt én om gangen med `-x` og bare `tests/test_ki_tekst.py`, med kopi før og sha256 mot HEAD etter hver. Fila var lik HEAD etter hver. F1–F5 ble først kjørt på `9bc8b3b` og fanget alle, og så på nytt på `5dd8a00` med FR1–FR4. FR2 overlevde først, og testen ble skrevet om (`48838a7`) og fanget den. Alle er fanget:

| # | Mutant | Fanget av |
|---|---|---|
| F1 | en feil hos modellen stopper hentingen | `test_en_annen_feil_stopper_steget_ikke_hentingen` |
| F2 | modellen kalles på nytt når raden finnes | `test_raden_staar_og_modellen_kalles_ikke_igjen` |
| F3 | KI-steget kjører før vurderingene | `test_en_rad_per_aksje_etter_vurderingene` |
| F4 | en tekst som ikke besto, logges som bestått | `test_en_tekst_som_ikke_bestaar_logges_med_grunnen` |
| F5 | KI-steget gjør et kall til EODHD | `test_ingen_kall_til_eodhd_fra_steget` |
| FR1 | modellen kalles igjen etter en feil | `test_modellen_kalles_ikke_igjen_etter_en_feil` |
| FR2 | ingen KI-rader før et nytt forsøk | `test_ki_radene_som_mangler_lages_foer_et_nytt_forsoek` |
| FR3 | en tom `OSE_KI_TJENESTE` gir `lokal` | `test_ingen_stille_overgang` |
| FR4 | ny børsdag sjekkes ikke før kallet | `test_modellen_kalles_ikke_etter_midnatt` |
