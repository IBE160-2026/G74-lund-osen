---
title: 'Story 10.2, PR E (10.2a): porten Modell, prompten og kontrollen i FR-603'
type: 'feature'
created: '2026-10-15'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f87931a'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Story 10.2 lager KI-teksten i hentekommandoen og lagrer den i `KILogg`. Før noe kobles til hentingen, trengs porten for modellen, prompten og kontrollen i FR-603, prøvd med en falsk modell (story 10.2 i `epics.md`, FR-603, FR-604, FR-605, FR-608, AD-2, AD-8).

**Approach:** Tre rene moduler og én funksjon som setter dem sammen, uten I/O:
- `src/ki_modell.py`: porten `Modell` (AD-2), `Modellsvar`, `ModellFeilet`, og `lag_ki_rad`, som lager prompten, kaller modellen én gang, kontrollerer teksten og gir `KIRad` for `KILogg`. Feiler modellen, blir det en rad uten tekst og med grunnen (NFR-04).
- `src/ki_prompt.py`: `PROMPTVERSJON` og `lag_prompt`. Prompten sier at fortegnet for interessen følger dagens kursendring og ikke volumet (lærdommen fra C-med i `malinger.md` §19).
- `src/ki_kontroll.py`: `kontroller`, de fire punktene i FR-603 med ordlistene, tall skrevet med ord, og «fordi» om regelen som lov.

PR E i planen for KI-laget. `ki_lokal.py` mot Ollama, steget i hentekommandoen, compose, `.env.example` og README er PR F (10.2b), i en egen instruksjon. Story 10.2 er ikke ferdig før F er flettet.

## Planen

Planen for KI-laget ble vist i chatten 15.10 kl. 15:43 og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-15.md` (`5ce64f6`). Testtallet før: 1763 bestått og 17 hoppet over på main (`f87931a`).

## Svarene

*Lagt til 2026-10-15 (gruppens svar på de ti spørsmålene i planen, instruksjonen kl. 15:53):* svarene er beslutninger. Alle ti står under Epic 10 i `epics.md`. De som gjelder denne PR-en:

- Svar 2: raden står når den finnes, også når modellen feilet. `lag_ki_rad` gir alltid en rad, også når modellen feiler, så hentingen kan skrive den (PR F).
- Svar 5: `av` er et eget valg i `OSE_KI_TJENESTE`. Med KI av kalles ikke `lag_ki_rad`, og ingen rad skrives (PR F).
- Svar 10: grunnlaget for én aksje har ingen antall, så de lovlige tallene i punkt 2 er styrken og regelens faste tall.

**Mutantene** (planen kl. 15:43): E1–E4 hvert av de fire punktene slått av; E5 «femti» slipper gjennom; E6 «fordi ingen sjekk ga utslag» stoppes.

## Boundaries & Constraints

- Ingen modell kalles, heller ikke Ollama. Ingen API-kall. Testene bruker en falsk modell (AD-8), og nettsperren fra 4.0 stopper en test som prøver.
- Ingen endring i `src/fetch_prices.py`, compose, `.env.example` eller README. Det er PR F.
- Kontrollen er grov: den fanger ord, ikke mening (FR-603).

## I/O & Edge-Case Matrix

| Inndata | Forventet |
|---|---|
| En tekst som bare forklarer grunnlaget | består |
| «Retningen er positiv» når regelen sier Blandet | stopper, punkt 1 |
| «Ingen av de tre sjekkene» når styrken er 2 | stopper, punkt 1 |
| «2,4 prosent», «3 %», «femdagssnittet», «seks av de femti» | stopper, punkt 2 |
| «50 dager», «MA50», «to av de tre» når styrken er 2 | består |
| «kjøpe», «bør», «investeringsråd», «alternativ for investorer» | stopper, punkt 3 |
| «trolig», «skyldes», «nyheter», «kontrakt» | stopper, punkt 4 |
| «fordi ingen sjekk ga utslag», «resultatet av sjekkene», «børsdagen» | består |
| Modellen reiser `ModellFeilet`, eller svarer tomt | en rad uten tekst, `besto=False` og «modellen feilet» |
| Modellen reiser en annen feil | feilen går videre |

</frozen-after-approval>

## Code Map

- `src/ki_modell.py`: `Modell`, `Modellsvar`, `ModellFeilet`, `lag_ki_rad`.
- `src/ki_prompt.py`: `PROMPTVERSJON`, `lag_prompt`.
- `src/ki_kontroll.py`: `kontroller`, `Kontrollsvar`, ordlistene.
- `tests/test_ki_modell.py`: testene, med `FalskModell`.

## Commitene

Grenen `10-2a-modell-og-kontroll`, PR #48: `9d35e0c` spesifikasjonen og 10-2 til in-progress; `1dd7150` porten, prompten, kontrollen og testene; `a8ce3eb` rettingene fra gjennomgangen.

## Spec Change Log

- *2026-10-15, gjennomgangen av PR E:* prompten beskriver fortegnene med ord og nevner ikke antallet aksjer i målingen, fordi kontrollen i punkt 2 ellers stopper en tekst som gjentar prompten. FR-603 sier at bare antall fra grunnlaget og regelens faste tall er lov, og fortegnene er ikke antall. Prompten ber modellen skrive utslagene med ord. Gruppen bør vite at en tekst som skriver «trenden ga +1», stoppes, selv om regelforklaringen (FR-704) bruker +1 og -1.

## Review Triage Log

Gjennomgang 15.10 på diffen `main...1dd7150`, med Blind Hunter (BH, 20 funn), Edge Case Hunter (ECH, 19) og Verification Gap (VG, 5). Rettingene står i `a8ce3eb`, og punktet i `deferred-work.md` i samme commit som denne triagen. Ingen funn må avgjøres av gruppen før flettingen. Spec Change Log over sier hva gruppen bør vite om fortegnene.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH, VG4 | Prompten sa «de 15 aksjene», og kontrollen stoppet en tekst som gjentok det | high | patch: prompten nevner ikke tallet, `test_prompten_har_ingen_tall_kontrollen_stopper`, `test_merket_og_en_tekst_som_sier_det` |
| BH2, ECH | Prompten ga tallene +1, 0, -1 og «0 til 3», som punkt 2 stopper | high | patch: prompten beskriver utslagene med ord og ber modellen skrive dem slik. Se Spec Change Log |
| BH3, ECH, VG2 | «prosent» som ord, «kroner» og «dobbelt» ble ikke fanget med et lovlig tall | high | patch: enheter og mengder er egne treff i punkt 2 |
| BH4, BH5, BH6, ECH, VG3 | Mange former av en feil styrke slapp gjennom: «en av de tre», «alle tre sjekkene», «to sjekker ga utslag», «styrken på signalet er», «3 av 3» | high | patch: tre mønstre for styrken og `STYRKEORD` med «en», «alle» og «begge» |
| BH7, ECH | «fordi ingen sjekk ga utslag» slapp gjennom når styrken var 2 | medium | patch: det er et utsagn om styrken, `test_fordi_ingen_sjekk_naar_noen_ga_utslag` |
| BH8, ECH | «ingen retning» og «retningen er ikke blandet» ble ikke sjekket, og «trendens retning er positiv» ble stoppet | medium | patch: «ingen» i begge mønstrene, «ikke» snur utsagnet, og retningen til én sjekk sjekkes ikke |
| BH12, ECH | Sammensatte tallord («femtifem»), «tiårs» og ordenstall og mengder slapp gjennom | medium | patch: flere tallord i ett ord, «år» og «time», og ordenstall og mengder i punkt 2 |
| ECH | «én aksje» ble stoppet som tallet 1 | medium | patch: «én», «en» og «ett» er antall bare i et utsagn om styrken |
| BH9, ECH | Gjetning i fortid og framtid slapp gjennom («skyldtes», «vil stige», «ventes», «grunnet», «i morgen») | medium | patch: flere ord i `GJETNING` |
| BH10, ECH | Råd om å holde slapp gjennom | medium | patch: «behold», «hold», «undervurdert», «oppside» og flere |
| ECH | NFD-tegn, myk bindestrek og usynlige tegn slapp et ord gjennom | medium | patch: `normaliser` før kontrollen |
| ECH | «²» og et svært langt tall reiste `ValueError` | medium | patch: `isdecimal` og en grense på seks siffer |
| BH15, ECH, VG5 | Et svar som ikke er et `Modellsvar`, og ugyldige verdier i svaret, reiste og ville stoppet hentingen | medium | patch: en rad uten tekst og med grunnen (NFR-04) |
| BH11, ECH | En feil styrke-type eller feil emne ga feil først etter modellkallet | medium | patch: `lag_ki_rad` avviser dem før modellen kalles, og `kontroller` krever heltall |
| BH14 | Feilmeldingen fra modellen kom ukortet inn i grunnen, og kunne ha en nøkkel | medium | patch: kortes til 200 tegn, og `key=` og lignende blir `***` |
| VG1 | Testene for ordlistene ble laget av listene selv | medium | patch: `test_ordene_fr_603_nevner` med ordene skrevet i testen |
| BH13 | Ingenting bandt promptteksten til versjonen | low | patch: `test_versjonen_foelger_teksten` med sha256 |
| BH17 | Testen for porten så ikke feltene | low | patch: `Modell.__annotations__` |
| BH18 | Kontrollen ble bare prøvd med styrke 0 og 2 | low | patch: tester med styrke 1 og 3 |
| BH20 | Matrisen manglet tilfellene over | low | patch: testene over. Matrisen er frosset, og tilfellene står i testene og her |
| BH16 | Kontrollen ser ikke på lengde, språk eller setningen om målingen | low | utsatt: `deferred-work.md` |
| ECH (påstand) | «resultater» står ikke på lista, selv om FR-603 nevner resultater som årsak | avvist | FR-603, tillegget 05.10: «Ordet «resultat» står ikke i lista, fordi det i §19 viste til sjekkene» |
| BH10 (del) | «salgspress» stoppes av «salgs» | avvist | kontrollen er grov (FR-603). En tekst som stoppes, gir en dag uten KI-tekst, ikke en feil |
| BH9 (del) | «etter at» og «peker mot» er ikke på lista | avvist | for vanlige i en tekst som bare forklarer regelen |
| BH19 | `epic-10` står som backlog | avvist | slik står epicene i `sprint-status.yaml` i dag |


## Verification

**Commands:**
- `uv run pytest -q` -- før 1763 bestått og 17 hoppet over på main (`f87931a`). 1863 og 17 på `1dd7150`. Etter rettingene 1970 og 17 på `a8ce3eb`.

**Mutantene**, kjørt én om gangen med `-x` og bare `tests/test_ki_modell.py`, med kopi før og sha256 mot HEAD etter hver. Fila var lik HEAD etter hver. E1–E6 ble først kjørt på `1dd7150` og fanget alle, og så på nytt på `a8ce3eb` med ER1–ER6. Alle er fanget:

| # | Mutant | Fanget av |
|---|---|---|
| E1 | punkt 1 slått av | `test_fordi_ingen_sjekk_naar_noen_ga_utslag` |
| E2 | punkt 2 slått av | `test_2_tall_og_mengder_som_ikke_er_i_grunnlaget` |
| E3 | punkt 3 slått av | `test_3_raad` |
| E4 | punkt 4 slått av | `test_ordene_fr_603_nevner` |
| E5 | «femti» og andre tall skrevet med ord slipper gjennom | `test_2_tall_og_mengder_som_ikke_er_i_grunnlaget` |
| E6 | «fordi ingen sjekk ga utslag» stoppes | `test_regelen_selv_kan_forklares` |
| ER1 | «prosent» og andre enheter slipper gjennom | `test_2_tall_og_mengder_som_ikke_er_i_grunnlaget` |
| ER2 | teksten normaliseres ikke | `test_andre_tegn_slipper_ikke_gjennom` |
| ER3 | «ingen sjekk ga utslag» er ikke et utsagn om styrken | `test_fordi_ingen_sjekk_naar_noen_ga_utslag` |
| ER4 | et svar som ikke er et `Modellsvar`, reiser | `test_et_svar_som_ikke_er_et_modellsvar` |
| ER5 | ugyldige verdier i svaret reiser | `test_ugyldige_verdier_i_svaret` |
| ER6 | nøkler fjernes ikke fra grunnen | `test_modellen_feilet_gir_en_rad_uten_tekst` |
