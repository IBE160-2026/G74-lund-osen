---
title: 'Story 10.2, 10.2i: promptversjon 4, teksten sier hvordan dagen var rundt aksjen'
type: 'feature'
created: '2026-11-05'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '72250544'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-2h-ordstilling.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-4-loggdelen.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

## Intent

**Problem:** Loggdelen av story 10.4 (`spec-10-4-loggdelen.md`) fant at alle 75 KI-tekstene i uka 29.10–04.11 bare gjentar regelforklaringen. Ingen nevner bransjen, hovedindeksen eller hvor mange aksjer som steg og falt, selv om grunnlaget har dem fra versjon 3 (10.2e).

**Beslutningen** (under story 10.4 i `epics.md`, *Avgjort 2026-11-05 kl. 16:05*): en ny promptversjon lages før brukertesten, der modellen bes bruke bransjen, hovedindeksen og antallene med ord, innenfor kontrollen, og tellingen gjentas etter noen dager med den.

**Instruksjonen kl. 18:02** (dagsfila 05.11): i tillegg til sjekkene skal teksten si med ord hvordan dagen var rundt aksjen, ut fra hovedindeksen, bransjen og antallene som steg og falt, og fortsatt ikke si at de forklarer signalet. Alle andre regler står. Grunnlaget, kontrollen (FR-603) og vakta (NFR-06) endres ikke.

## Approach

**a) Prompten** (`src/ki_prompt.py`): én linje til under «Regler for teksten», rett foran linja om at hovedindeksen og bransjen ikke forklarer signalet: «- I tillegg til sjekkene skal teksten si med ord hvordan dagen var rundt aksjen: om hovedindeksen og bransjen steg, falt eller var uendret, og hvor mange av aksjene i lista som steg og som falt.» `PROMPTVERSJON` blir «4», fordi `ose.db` har tekster med versjon 3 (svaret 25.10 kl. 20:54 b). Versjonen og grunnen står i docstringen, og avtrykket i `AVTRYKK` i `tests/test_ki_modell.py`.

*Utfallet:* `37fb7c9c`. Avtrykket for versjon 4 er `e0306762…d3f7`, og avtrykket for versjon 3 står. `test_versjon_4` erstatter `test_versjon_3`, og `test_teksten_sier_hvordan_dagen_var_rundt_aksjen` sjekker at linja står én gang i reglene, rett foran linja om at hovedindeksen og bransjen ikke forklarer signalet, og kommer med i prompten, med og uten merket.

**b) Demoen:** KI-tekstene i demoen lages på nytt med Gemma (`uv run python src/demo_ki.py`). En tekst som ikke består kontrollen, vises ikke, som før.

*Utfallet:* `37fb7c9c`. Laget 18:07:25–18:07:38: 13 av 13 besto, 0 ble stoppet, og modellen feilet for 0. Alle har `promptversjon` 4 og `promptavtrykk` `e0306762…d3f7`. Alle 13 har en setning til om dagen: hovedindeksen falt, bransjen steg eller falt, og sju aksjer steg og sju falt. Hver tekst er lest mot grunnlaget, og alle stemmer. Bildet av aksjesiden for BRFE i README-en er tatt på nytt med fremgangsmåten i 3.3b, fordi teksten ble én linje lengre: bunnen av `p.dagene` er 2224,5 px, målt i Edge, og `HOEYDE_PAA_AKSJESIDEN` er 2225 (var 2198). Bildene av børsometeret og Min liste ble tatt på nytt og er like (1280 px byte for byte, 390 px piksel for piksel), så bare avtrykkene er satt på nytt. Målingen ga 2198, 1329, 1155 og 1687 px på main, de samme som konstantene.

**c) Prøvekjøringen** (§54 i `malinger.md`): grunnlaget for de 15 aksjene for 04.11, lest fra `ki_logg` i `ose.db` med `mode=ro`, gjennom modellen, kontrollen og visningen (samsvaret og vakta), uten å skrive til basen og uten kopi. Klassene «gjentar», «sier mer» og «usikker» etter regelen i `spec-10-4-loggdelen.md`, for versjon 3 i uka og versjon 4 i prøven.

*Utfallet:* `a6992014`. Kjørt 18:06:36–18:07:08: 15 av 15 besto, 0 ble stoppet, modellen feilet for 0, og alle 15 ville blitt vist. Versjon 3 i uka: 75 gjentar, 0 sier mer og 0 usikre. Versjon 4: 0 gjentar, 15 sier mer og 0 usikre. Hver tekst er lest mot grunnlaget, og hovedindeksen, bransjen og antallene stemmer i alle 15. sha256 for `ose.db` var `58b893eb…c1be` før og etter. Tekstene står bare i scratchpad.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke. `data/db/ose.db` leses bare, med `mode=ro`, og ingen tekst skrives til den (regel 22). Demobaser bare i midlertidige mapper.
- Grunnlaget (`ki_grunnlag.py`), kontrollen (`ki_kontroll.py`) og vakta (`ki_visning.py`) endres ikke.
- Ingen tekst fra den ekte versjonen ordrett i sporede filer eller i PR-en (regel 16). PR-en har tre demotekster før og etter.
- Ollama ble startet i Docker for prøven og demoen (`docker compose --profile ki up -d ollama`, 18:05:45) og stoppet etterpå (18:07:50), før hele settet. Docker Desktop kjørte fra før og er ikke stoppet.
- Stopp før flettingen.

## Mutanten

Én, med kopi før og sha256 mot HEAD etter: den nye linja tatt ut av prompten.

*Utfallet:* kjørt kl. 18:24 på `37fb7c9c`. Fanget av `test_teksten_sier_hvordan_dagen_var_rundt_aksjen`, `test_versjonen_foelger_teksten` og `test_hver_rad_har_promptens_avtrykk_ved_promptversjonen`, og testene som leser demoradene med promptens avtrykk feilet i oppsettet (10). `src/ki_prompt.py` var lik HEAD etterpå (samme blob, `98213f40`, og samme sha256 som kopien).

## Demotekstene før og etter

Tre av de 13, fra `src/demo_ki_tekster.json` (oppdiktede selskaper):

- **BRFE** (trend, bevegelse og interesse negative). Før: «Signalet er negativt fordi trenden ga et negativt utslag, bevegelsen ga et negativt utslag, og interessen ga et negativt utslag.» Etter: «Signalet er negativt fordi trenden ga et negativt utslag, bevegelsen ga et negativt utslag, og interessen ga et negativt utslag. Dagen var preget av at hovedindeksen falt, bransjen falt, og det var syv aksjer som steg og syv aksjer som falt.»
- **SLVP** (retningen Ingen). Før: «Signalet har ingen retning fordi trenden ikke ga utslag, bevegelsen ikke ga utslag, og interessen ikke ga utslag.» Etter: «Signalet har ingen retning fordi trenden ikke ga utslag, bevegelsen ikke ga utslag og interessen ikke ga utslag. Dagen var preget av at hovedindeksen falt, bransjen falt, og det var syv aksjer som steg og syv aksjer som falt.»
- **KVST** (alle tre positive, bransjen steg). Før: «Signalet er positivt fordi trenden ga et positivt utslag, bevegelsen ga et positivt utslag, og interessen ga et positivt utslag.» Etter: «Signalet er positivt fordi trenden ga et positivt utslag, bevegelsen ga et positivt utslag, og interessen ga et positivt utslag. Dagen var preget av at hovedindeksen falt, bransjen steg, og det var syv aksjer som steg og syv aksjer som falt.»

## Åpent

- Kontrollen leser «N aksjer steg», men ikke «N aksjer som steg» eller «falt åtte og steg syv», som er formene modellen brukte. Der sjekkes bare at tallet er et av antallene i grunnlaget, ikke at det står ved riktig felt (§54). Antallene i prøven og i demoen er riktige, lest for hånd.
