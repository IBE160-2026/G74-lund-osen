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

## Review Triage Log

## Verification
