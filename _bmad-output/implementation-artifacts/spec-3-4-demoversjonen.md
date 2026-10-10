---
title: 'Story 3.4: Demoversjonen'
type: 'feature'
created: '2026-10-10'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'b294a9514aca2d455e72b6da3942abe7fff49910'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3-readme-slik-kjoerer-du-den.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Appen kan bare prøves med en egen EODHD-nøkkel. Faglærer, sensor og medstudenter skal kunne se hvordan den virker uten konto, og demoen er hovedveien for vurderingen (FR-411, svaret fra hjelpelæreren 05.10).

**Approach:** En egen kommando lager `data/db/demo.db` med 15 oppdiktede selskaper, kurser etter en skrevet regel med fast frø, og én vurdering per aksje og børsdag regnet med `vurder()`. Basen er merket som demobase, og merket avgjør «Eksempeltall» på sidene. Én bryter velger hvilken base webserveren åpner. Vaktene hindrer at demobasen og den ekte basen blandes, begge veier.

## Planen

Planen er vist i chatten 10.10 og ført i `docs/ai-prompts/2026-10-10.md` (instruksjonen kl. 12:06 og Utført-linjen). Gruppen sa ja kl. 12:27 med disse svarene, som er beslutninger:

1. **Navnene.** Joakim kontrollerte de 15 tickerne for hånd mot lista over aksjer i Oslo hos Euronext 10.10 kl. 12:25, og ingen av dem står der. Rådet søkte samme dag på nettet etter de 15 navnene, nøyaktig skrevet, og fant ingen selskaper med de navnene. Programmet henter aldri lista.
2. **Port 5000 for demoen.** App og demo kan ikke kjøre samtidig. `docker compose down` stopper også demotjenestene, og README-en sier hvordan man bytter (PR 2).
3. **Fast sluttdato, fredag 2026-10-09.**
4. **To pull requests.** PR 1 er demoen med uv. PR 2, med Docker og README, bygges på en ny gren fra main etter at PR 1 er flettet.

I tillegg, fra instruksjonen:
- Normalfordelingen og volumene lages fra `random()` med Box–Muller, fordi Python bare lover at `Random.random()` gir samme rekke med samme frø på tvers av versjoner.
- En base som ikke finnes eller ikke kan leses, regnes ikke som demobase i vakten i hentingen, og hentingen går videre som i dag.
- Demobaser lages bare i midlertidige mapper og prøveprosjekter, aldri i `data/db/` i repoet (regel 22).

## Boundaries & Constraints

**Always:**
- `DEMOUNIVERS` har de 15 i tabellen under. Ingen symbol eller ticker står i `AKSJEUNIVERS`.
- Kursene: 195 handelsdager fra 2026-01-02 til 2026-10-09 etter `boersdag.er_boersdag`. Hver aksje har sitt eget frø, `FROE * 100 + nummeret i lista`. Daglig logavkastning er drift + volatilitet · z, der z er normalfordelt fra Box–Muller på `random()`. Drift og volatilitet følger sektoren. Volumet er et nivå per aksje ganger `exp(0,3 · z)`, og med sannsynlighet 0,04 per dag tre ganger det. `adjusted_close` er lik `close`. Kursene avrundes til to desimaler, volumet til heltall. Siste dag faller Brattfjell Energi 6 % med tre ganger volumet, så minst én aksje skiller seg ut.
- Tilstandene: Varde Systemer har bare de siste 30 dagene (nylig notert, «signalet kunne ikke regnes» og «Trenger 51 dager»), Tareøy Havbruk mangler siste dag («ingen kurs fra dagen»), og Matfjord Merkevarer har ingen kurser («Uten data i denne kilden»).
- Hver børsdag i serien har én rad i `vurdering` per aksje, lik det `vurder()` gir for serien fram til dagen, skrevet med `SqliteVurderingslager.skriv` uendret og lagerets klokke stilt på dagen (`AD-7`).
- Merket er `PRAGMA application_id = 0x4F534544`. Bare demokommandoen setter det.
- Demokommandoen nekter en fil uten merket, også en tom fil. En demobase lages på nytt fra bunnen.
- Hentekommandoen og `--les-inn` nekter en demobase før noe annet. En base som ikke finnes eller ikke kan leses, regnes ikke som demobase.
- Bryteren er `OSE_DEMO=1`, eller `--demo` til `python src/app.py`. Med bryteren åpner webserveren `demo.db` ved siden av `ose.db` og lager den aldri. Mangler den, viser siden kommandoen som lager den. Uten bryteren åpnes `ose.db` som før.
- «Eksempeltall» står på hver side som viser en base med merket, og på ingen side med en base uten. Merket leses fra basen, ikke fra bryteren.
- Portene som skriver, tar lista som parameter, med `AKSJEUNIVERS` som standard. Testen som holder `aksje` lik `AKSJEUNIVERS` i den ekte basen, står (`AD-21`).

| Ticker | Navn | Sektor |
|---|---|---|
| BRFE | Brattfjell Energi | Energi |
| HVDO | Havdyp Olje | Energi |
| NLYS | Nordlysfeltet | Energi |
| SLVP | Sølvbank Petroleum | Energi |
| FJSB | Fjellheim Sparebank | Finans |
| TRHF | Trygghavn Forsikring | Finans |
| VRDS | Varde Systemer | Industri |
| KVST | Kvitstein Mineral | Materialer |
| JGRD | Jordgrøde Gjødsel | Materialer |
| BLGT | Bølgetopp Tankers | Shipping |
| LSTF | Lastfjord Container | Shipping |
| SGNT | Signalnett | Telekom |
| LKSV | Laksevik Sjømat | Sjømat |
| TROY | Tareøy Havbruk | Sjømat |
| MTFJ | Matfjord Merkevarer | Konsum |

**PR 1 (denne grenen, 3-4):** `src/demo.py`, merket, vaktene begge veier, lista som parameter i skriveportene, bryteren og siden når demobasen mangler, «Eksempeltall» og testene.

**PR 2 (ny gren fra main etter PR 1):** demotjenestene `demo-lag` og `demo` i profilen `demo`, volumet `ose-demo`, CI-steget, «Kom i gang» med demoen først og hvordan man bytter, testen for kommandoene, `docs/kvalitetssikring.md` klar for README-prøven, og merknader i spinen.

**Never:**
- KI-tekstene (3.4b), hovedindeksen (2.8), lista som kan byttes (2.11) og resten av punkt 4.4 i endringsforslaget 08.10, som ikke er bygget.
- Demokommandoen gjør ingen nettkall, leser ingen nøkkel og importerer verken `requests`, `eodhd` eller `fetch_prices`.
- Ingen demobase i `data/db/` i repoet under byggingen. `hent` kjøres aldri gjennom compose lokalt.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Ny demobase | `demo.db` finnes ikke | lages med merket, 15 aksjer, 195 dager, 2 925 vurderinger | — |
| Demobase finnes | `demo.db` med merket | lages på nytt, lik den forrige | — |
| Fil uten merket | `demo.db` uten merket, også tom | ingenting skrives, kode 1 | Utskriften sier hvorfor |
| Henting mot demobase | `ose.db` med merket | 0 kall, kode 1 | Utskriften sier hvorfor |
| Henting uten base | `ose.db` finnes ikke eller kan ikke leses | som i dag | — |
| Bryteren, ingen demobase | `OSE_DEMO=1`, `demo.db` mangler | siden viser `DEMOKOMMANDO`, ingen fil lages | — |

</frozen-after-approval>

## Code Map

- `src/kursdata.py` -- `kontroller_skriving` (linje 162) sjekker mot `AKSJEUNIVERS`. Får `univers` som parameter.
- `src/lagring_sqlite.py` -- `SqliteKurslager` (118), `SYMBOLER` og `_kontroller_noekkel` (192, 213) i vurderingslageret. Får `univers`. Nytt: `DEMOMERKE`, `er_demobase(sti)` og `demo_sti()` ved siden av `BASE_STI`.
- `src/fetch_prices.py` -- `kjoer` (547) og `les_inn` (775) får vakten først.
- `src/app.py` -- `_aapne_basen` (118) og `_migrer_en_gang`, rutene `markedsoversikt` og `aksjedetalj`. Bryteren, `DEMOKOMMANDO` og «Eksempeltall» gjennom en context processor.
- `src/templates/index.html`, `aksje.html`, `basefeil.html` -- merket etter `<body>`, og teksten når demobasen mangler.
- `src/signalberegning.py` -- `vurder` og `nodvendige_dager` (51), uendret.
- `tests/conftest.py` -- flytter `BASE_STI` til `tmp_path`, så `demo_sti()` følger med.

## Tasks & Acceptance

**Execution (PR 1):**
- [ ] `src/kursdata.py`, `src/lagring_sqlite.py` -- lista som parameter, merket og `er_demobase`.
- [ ] `src/demo.py` -- `DEMOUNIVERS`, regelen og demokommandoen.
- [ ] `src/fetch_prices.py` -- vakten i `kjoer` og `les_inn`.
- [ ] `src/app.py` og malene -- bryteren, siden når demobasen mangler, «Eksempeltall».
- [ ] `tests/test_demo.py` -- kontrollpunktene.

**Acceptance Criteria:**
- Given to kjøringer av demokommandoen, then er basene like rad for rad.
- Given en demobase og bryteren av, then sier sidene «Eksempeltall». Given en ekte base og bryteren på, then gjør de det ikke.
- Given en demobase som `ose.db`, when hentingen eller `--les-inn` kjøres, then stopper den før noe annet med kode 1.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q` -- expected: grønn.
