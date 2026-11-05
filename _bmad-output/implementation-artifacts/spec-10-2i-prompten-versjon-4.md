---
title: 'Story 10.2, 10.2i: promptversjon 4, teksten sier hvordan dagen var rundt aksjen'
type: 'feature'
created: '2026-11-05'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 1
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

*Lagt til etter gjennomgangen (ECH1, BH3):* linja krevde hovedindeksen og bransjen også når feltet mangler, mot reglene om at teksten ikke sier noe om et felt som mangler. I `c9dbb342` sier den «… steg, falt eller var uendret, når feltet står i opplysningene, og hvor mange …». Versjonen står som 4, fordi ingen tekst i `ose.db` har versjon 4, og avtrykket er `0df61d8f…c825` (var `e0306762…`). Docstringen i `test_versjon_4` sier nå hva testen sjekker, og viser til `test_versjonen_foelger_teksten` for resten (BH12, ECH7).

**b) Demoen:** KI-tekstene i demoen lages på nytt med Gemma (`uv run python src/demo_ki.py`). En tekst som ikke består kontrollen, vises ikke, som før.

*Utfallet:* `37fb7c9c`. Laget 18:07:25–18:07:38: 13 av 13 besto, 0 ble stoppet, og modellen feilet for 0. Alle har `promptversjon` 4 og `promptavtrykk` `e0306762…d3f7`. Alle 13 har en setning til om dagen: hovedindeksen falt, bransjen steg eller falt, og sju aksjer steg og sju falt. Hver tekst er lest mot grunnlaget, og alle stemmer. Bildet av aksjesiden for BRFE i README-en er tatt på nytt med fremgangsmåten i 3.3b, fordi teksten ble én linje lengre: bunnen av `p.dagene` er 2224,5 px, målt i Edge, og `HOEYDE_PAA_AKSJESIDEN` er 2225 (var 2198). Bildene av børsometeret og Min liste ble tatt på nytt og er like (1280 px byte for byte, 390 px piksel for piksel), så bare avtrykkene er satt på nytt. Målingen ga 2198, 1329, 1155 og 1687 px på main, de samme som konstantene.

*Lagt til etter gjennomgangen:* i `c9dbb342` er demotekstene laget på nytt med den rettede linja, 18:30:37–18:30:50: 13 av 13 besto, og alle stemmer med grunnlaget. Teksten for BRFE er den samme, og bildene ved 1280 px ble tatt på nytt og er byte for byte de samme. Bildet ved 390 px er ikke tatt på nytt denne gangen, fordi siden er den samme. Bare avtrykkene er satt på nytt. Den første setningen er også endret i noen tekster, for eksempel FJSB og SGNT fra «har en negativ retning» til «er negativt» (BH9). Alle demotekstene sier at sju aksjer steg og sju falt: lista i demoen har 15 aksjer, og grunnlaget teller bare dem som steg og falt (BH2).

**c) Prøvekjøringen** (§54 i `malinger.md`): grunnlaget for de 15 aksjene for 04.11, lest fra `ki_logg` i `ose.db` med `mode=ro`, gjennom modellen, kontrollen og visningen (samsvaret og vakta), uten å skrive til basen og uten kopi. Klassene «gjentar», «sier mer» og «usikker» etter regelen i `spec-10-4-loggdelen.md`, for versjon 3 i uka og versjon 4 i prøven.

*Utfallet:* `a6992014`. Kjørt 18:06:36–18:07:08: 15 av 15 besto, 0 ble stoppet, modellen feilet for 0, og alle 15 ville blitt vist. Versjon 3 i uka: 75 gjentar, 0 sier mer og 0 usikre. Versjon 4: 0 gjentar, 15 sier mer og 0 usikre. Hver tekst er lest mot grunnlaget, og hovedindeksen, bransjen og antallene stemmer i alle 15. sha256 for `ose.db` var `58b893eb…c1be` før og etter. Tekstene står bare i scratchpad.

*Lagt til etter gjennomgangen:* kjørt på nytt med den rettede linja (`bb495bda`), 18:29:56–18:30:23: 15 av 15 besto, 0 stoppet, og alle 15 ville blitt vist. 0 gjentar, 15 sier mer og 0 usikre, og alt stemmer med grunnlaget. Fem grunnlag ble også kjørt uten hovedindeksen, uten bransjen og uten begge: 13 av 15 besto, og kontrollen stoppet de 2 som sa noe om et felt som manglet. Retningen på hovedindeksen for 04.11 står ikke lenger i §54 (BH14).

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke. `data/db/ose.db` leses bare, med `mode=ro`, og ingen tekst skrives til den (regel 22). Demobaser bare i midlertidige mapper.
- Grunnlaget (`ki_grunnlag.py`), kontrollen (`ki_kontroll.py`) og vakta (`ki_visning.py`) endres ikke.
- Ingen tekst fra den ekte versjonen ordrett i sporede filer eller i PR-en (regel 16). PR-en har tre demotekster før og etter.
- Ollama ble startet i Docker for prøven og demoen (`docker compose --profile ki up -d ollama`, 18:05:45 og 18:29:44) og stoppet etterpå (18:07:50 og 18:30:56), før hele settet. Docker Desktop kjørte fra før og er ikke stoppet.
- Stopp før flettingen.

## Mutanten

Én, med kopi før og sha256 mot HEAD etter: den nye linja tatt ut av prompten.

*Utfallet:* kjørt kl. 18:24 på `37fb7c9c`. Fanget av `test_teksten_sier_hvordan_dagen_var_rundt_aksjen`, `test_versjonen_foelger_teksten` og `test_hver_rad_har_promptens_avtrykk_ved_promptversjonen`, og testene som leser demoradene med promptens avtrykk feilet i oppsettet (10). `src/ki_prompt.py` var lik HEAD etterpå (samme blob, `98213f40`, og samme sha256 som kopien).

*Lagt til:* kjørt på nytt kl. 18:38:50 på `c9dbb342`, med den rettede linja tatt ut. Fanget av de samme tre testene, og fila var lik HEAD etterpå (blob `689e0aa4`, og samme sha256 som kopien).

## Demotekstene før og etter

Tre av de 13, fra `src/demo_ki_tekster.json` (oppdiktede selskaper), etter rettingen i `c9dbb342`:

- **BRFE** (trend, bevegelse og interesse negative). Før: «Signalet er negativt fordi trenden ga et negativt utslag, bevegelsen ga et negativt utslag, og interessen ga et negativt utslag.» Etter: «Signalet er negativt fordi trenden ga et negativt utslag, bevegelsen ga et negativt utslag, og interessen ga et negativt utslag. Dagen var preget av at hovedindeksen falt, bransjen falt, og det var syv aksjer som steg og syv aksjer som falt.»
- **SLVP** (retningen Ingen). Før: «Signalet har ingen retning fordi trenden ikke ga utslag, bevegelsen ikke ga utslag, og interessen ikke ga utslag.» Etter: «Signalet har ingen retning fordi trenden ikke ga utslag, bevegelsen ikke ga utslag og interessen ikke ga utslag. Dagen var preget av at hovedindeksen falt, bransjen falt, og det var syv aksjer som steg og syv aksjer som falt.»
- **KVST** (alle tre positive, bransjen steg). Før: «Signalet er positivt fordi trenden ga et positivt utslag, bevegelsen ga et positivt utslag, og interessen ga et positivt utslag.» Etter: «Signalet er positivt fordi trenden ga et positivt utslag, bevegelsen ga et positivt utslag, og interessen ga et positivt utslag. Rundt aksjen falt hovedindeksen, og i lista steg syv aksjer mens syv falt, og bransjen steg.»

## Gjennomgangen

Gjennomgang 05.11 etter hele settet (4069 bestått, 24 hoppet over, 6 porttester for `start.ps1` feilet), av diffen `72250544..2dab3ac9` uten PNG-fila, med Blind Hunter (BH, 15 funn), Edge Case Hunter (ECH, 8) og Verification Gap (VG, 2). Rettet i `c9dbb342`, `bb495bda` og her.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, VG1, ECH3, ECH8 | Kontrollen leser ikke «N aksjer som steg», «steg 8 og falt 7» eller sammenligninger som «flere aksjer steg enn falt», så byttede antall består. Hjelpen sier at tallene med prikket strek er sjekket | høy | **spørsmål 1 til gruppen:** kontrollen skulle ikke endres i denne instruksjonen. Antallene i prøvene og demoen er riktige, lest for hånd |
| ECH2 | Kontrollen leser ikke alle formene for retningen på hovedindeksen og bransjen («gikk også opp», «holdt seg uendret», «flat», «markedet steg») | middels | **spørsmål 1**, som over. Ingen tekst i prøvene brukte dem |
| ECH1, BH3 | Linja krevde hovedindeksen og bransjen også når feltet mangler | middels | **rettet** i `c9dbb342`, og prøvd uten feltene i `bb495bda` |
| BH6 | Setningen om dagen er nesten lik for alle aksjene og kunne vært laget av koden, uten modell og uten hullet i kontrollen | middels | **spørsmål 2 til gruppen** |
| BH7 | «Dagen var preget av» rett etter en «fordi»-setning kan leses som at markedet forklarer signalet | middels | **spørsmål 3 til gruppen:** gruppens regel står, og ingen tekst sier at markedet forklarer signalet. Etter rettingen bruker de fleste «Rundt aksjen …» |
| BH4 | Prøven og demoen har bare én retning på hovedindeksen | middels | **står:** tellingen gjentas etter noen dager i driften (svaret 5.11 kl. 16:05) |
| BH5 | Klassene er satt av Claude, som også skrev prompten | middels | **står:** ført i §54 og i 10.4. Delen med en person er brukertesten |
| BH14 | Retningen på hovedindeksen for 04.11 sto i §54 | lav | **rettet** i `bb495bda` |
| BH12, ECH7 | Docstringen i `test_versjon_4` lovet mer enn testen sjekker | lav | **rettet** i `c9dbb342` |
| BH2 | Demotekstene sier sju og sju, ikke 15 | lav | **rettet:** forklart under b) |
| BH9 | Første setning er også endret i noen demotekster | lav | **rettet:** ført under b) |
| BH8 | Over halvparten skriver antallene med sifre, selv om linja sier «med ord» | lav | **står:** «med ord» gjelder hvordan dagen var, og regelen om tall lar antallene stå |
| BH10 | Høyden på bildet følger lengden på KI-teksten | lav | **står:** slik bildetesten er laget (3.3f) |
| BH11 | Avtrykkene for børsometeret og Min liste er endret, men bildene ikke | lav | **står:** `demo_ki_tekster.json` er blant filene bak, og kommentaren sier det |
| BH13 | «sju» i dokumentene, «syv» i demotekstene | lav | **står:** begge er bokmål |
| BH15 | Bare én mutant | lav | **står:** instruksjonen ba om én. Den er kjørt to ganger |
| ECH4 | «Sju av 15 aksjer» og «én aksje var uendret» stoppes | lav | **står:** ingen tekst i prøvene gjorde det |
| ECH5, VG2 | Demoen har like antall og samme retning på hovedindeksen i alle rader, så den kan ikke vise byttede antall | lav | **står:** demodagen er fast. En test for byttede antall hører til spørsmål 1 |
| ECH6 | «To eller tre hele setninger» mot en setning til om dagen | lav | **står:** alle tekstene i prøvene har to eller tre setninger |

## Åpent

- Kontrollen leser «N aksjer steg», men ikke «N aksjer som steg» eller «falt åtte og steg syv», som er formene modellen brukte. Der sjekkes bare at tallet er et av antallene i grunnlaget, ikke at det står ved riktig felt (§54). Antallene i prøven og i demoen er riktige, lest for hånd.
- *Lagt til etter gjennomgangen:* spørsmål til gruppen:
  1. Skal kontrollen lese antallene i formene modellen bruker («N aksjer som steg», «steg 8 og falt 7», «flere aksjer steg enn falt») og flere former for retningen på hovedindeksen og bransjen (BH1, VG1, ECH2, ECH3, ECH8)? Til da kan et byttet antall vises med prikket strek.
  2. Skal setningen om dagen lages av koden i stedet for av modellen (BH6)?
  3. Er «Dagen var preget av …» rett etter forklaringen av signalet greit, eller skal prompten be om en nøytral innledning (BH7)?
