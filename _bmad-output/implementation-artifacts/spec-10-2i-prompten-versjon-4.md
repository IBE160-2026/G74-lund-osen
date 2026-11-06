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


## Svarene 5.11 kl. 19:13 og 23:36 (instruksjonen kl. 23:53)

**Beslutningen** (under story 10.4 i `epics.md`): spørsmål 1 i PR #113 er besvart kl. 19:13: appen skriver setningen om hovedindeksen, bransjen og antallene, alltid riktig, som setningen om dagene, og modellen sier bare med faste ord om aksjen gikk samme vei som børsen, og det sjekker kontrollen. Kl. 23:36: spørsmål 2 og 3 er besvart av det samme svaret: appen lager setningen om dagen (BH6), modellen skriver ikke om dagen, og appens setning står for seg selv under teksten og sier aldri at dagen forklarer signalet (BH7).

Main ble flettet inn i grenen i `62b412ee`, og hele settet ga 4086 bestått, 24 hoppet over og 6 porttester for `start.ps1` som feilet.

**a) Setningen om samme dag** (`28302119`): `setning_om_samme_dag` i `src/dagene.py` er en ren funksjon som `setning_om_dagene`. Den sier hva hovedindeksen, bransjen og antallene gjorde samme dag, for eksempel «Samme dag falt hovedindeksen, bransjen falt i snitt, og 7 aksjer i lista steg og 7 falt.», og tar ikke med det som mangler. `Dagsbilde` og `lag_dagsbilde` er flyttet fra `ki_grunnlag.py` til `dagene.py`, så siden og grunnlaget regnes av den samme funksjonen, og webserveren importerer fortsatt ikke KI-laget (AD-10). Setningen står i `p.samme-dag` rett under `p.dagene`, også med KI av. Siden leser lista fra `aksje` i basen, kursene og indeksen som i `ki_tekst._grunnlagene`. Mutant A (`steg` og `falt` byttet i `_VERBET`) ble fanget av 4 tester.

**b) Grunnlaget** (`59ab436a`): `Dagsbilde` har `aksjen`, regnet med `_retningen_paa_dagen`, den samme funksjonen som hovedindeksen. Grunnlaget har `hovedindeksen` og `aksjen` (`DAGFELTENE`), og ikke `bransjen`, `aksjer_steg` og `aksjer_falt`. `ANTALLENE` er bare styrken. Prompten forklarer `aksjen`, og linja om dagen rundt aksjen fra kl. 16:05 er tatt ut. Mutant B (aksjen regnet av indeksserien) ble fanget av 2 tester.

**c) Ordlyden** (`c986d07c`): `ordlyd_om_hovedindeksen` i `ki_prompt.py` gir «Aksjen gikk samme vei som hovedindeksen.» når aksjen og hovedindeksen begge steg eller begge falt, og «Aksjen gikk motsatt vei av hovedindeksen.» når den ene steg og den andre falt. Ellers, også ved uendret eller et felt som mangler, er det ingen ordlyd. Den er en hel setning, så den ikke settes inn i en annen setning, slik ordlyden for dagene ble i §44. Den står på en egen linje etter opplysningene, og reglene sier at teksten bruker den ordrett eller ikke sier noe om hovedindeksen. Avtrykket dekker ordlyden og funksjonen. Mutant C (`==` til `!=`, byttede retninger) ble fanget av 7 tester, og oppsettet for demotestene feilet.

**d) Kontrollen** (`281a8f84`): `_om_dagen` i `ki_kontroll.py` tar ut ordlyden fra den samme funksjonen når den står ordrett som en hel setning, og stopper alt annet om hovedindeksen, bransjen, børsen og antallet aksjer. Sjekkene fra 10.2e av retningen og antallene er erstattet, og testene som godtok dem, er snudd. Mutant D (kontrollen godtar alltid «samme vei») ble fanget av 5 tester.

**`PROMPTVERSJON`** står som 4, fordi versjon 4 ikke er flettet og ingen tekst i `ose.db` har versjon 4. Grunnen står i docstringen, og avtrykket i `AVTRYKK["4"]` er nå `ec084a52…e251`.

**Demotekstene** er laget på nytt med Gemma etter b, c og d og etter rettingene. Etter d besto 12 av 13: HVDO brukte ordlyden inne i en setning og ble stoppet, og vises ikke. Etter rettingene besto 13 av 13. Bildet av BRFE er tatt på nytt med fremgangsmåten i 3.3b etter hver endring (2261 px), og de andre seks bildene ble tatt på nytt og er byte for byte de samme. Bare avtrykkene er satt på nytt.

**Mutantene** ble kjørt med kopi før og fila lik HEAD etter (samme blob, og samme sha256 uten CR): A kl. 00:33:33 på `28302119`, B kl. 00:56:17 på `59ab436a`, C kl. 01:14:55 på `c986d07c` og D kl. 01:31:24 på `281a8f84`.

**Hele settet**, alene og med Ollama stoppet, før hver commit med kode eller tester: 4119 (a), 4123 (b), 4136 (c), 4176 (d) og 4212 (rettingene) bestått, 24 hoppet over hver gang, og bare 4–7 porttester for `start.ps1` som feilet.

**Prøvekjøringen** (§55 i `malinger.md`): grunnlaget for de 15 for 05.11, regnet på nytt fra `ose.db` med `mode=ro`. Før rettingene besto 14 av 15. YAR brukte ordlyden inne i en setning og ble stoppet. Etter rettingene besto 15 av 15, og alle 15 ville blitt vist. Klassene: 0 gjentar, 15 sier mer (bare ordlyden) og 0 usikre. Lista i `aksje` i basen var den samme som `AKSJEUNIVERS`.

### Demotekstene før og etter

Tre av de 13, fra `src/demo_ki_tekster.json` (oppdiktede selskaper). «Før» er teksten etter `c9dbb342`. «Etter» er teksten nå, med setningen appen skriver under den.

- **BRFE.** Før: «Signalet er negativt fordi trenden ga et negativt utslag, bevegelsen ga et negativt utslag, og interessen ga et negativt utslag. Dagen var preget av at hovedindeksen falt, bransjen falt, og det var syv aksjer som steg og syv aksjer som falt.» Etter: «Signalet er Negativt fordi trenden ga et negativt utslag, bevegelsen ga et negativt utslag, og interessen ga et negativt utslag. Aksjen gikk samme vei som hovedindeksen.» Under: «Samme dag falt hovedindeksen, bransjen falt i snitt, og 7 aksjer i lista steg og 7 falt.»
- **SLVP.** Før: «Signalet har ingen retning fordi trenden ikke ga utslag, bevegelsen ikke ga utslag og interessen ikke ga utslag. Dagen var preget av at hovedindeksen falt, bransjen falt, og det var syv aksjer som steg og syv aksjer som falt.» Etter: «Signalet har ingen retning fordi trenden ikke ga utslag, bevegelsen ikke ga utslag og interessen ikke ga utslag. Aksjen gikk motsatt vei av hovedindeksen.» Under: «Samme dag falt hovedindeksen, bransjen falt i snitt, og 7 aksjer i lista steg og 7 falt.»
- **KVST.** Før: «Signalet er positivt fordi trenden ga et positivt utslag, bevegelsen ga et positivt utslag, og interessen ga et positivt utslag. Rundt aksjen falt hovedindeksen, og i lista steg syv aksjer mens syv falt, og bransjen steg.» Etter: «Signalet er Positivt fordi trenden ga et positivt utslag, bevegelsen ga et positivt utslag, og interessen ga et positivt utslag. Aksjen gikk motsatt vei av hovedindeksen.» Under: «Samme dag falt hovedindeksen, bransjen steg i snitt, og 7 aksjer i lista steg og 7 falt.»

### Gjennomgangen av svarene

Gjennomgang 06.11 etter hele settet for d, av diffen `62b412ee..64337644` uten PNG-filene, med Blind Hunter (BH, 13 funn), Edge Case Hunter (ECH, 12) og Verification Gap (VG, 11). Triagen følger regel 25: et funn på middels eller over som følger av et svar eller av instruksjonen, står åpent til gruppen har svart, og graden settes ikke ned. Rettet i `2602f1e4`.

| # | Funn | Grad | Rute |
|---|---|---|---|
| BH1, VG1, ECH1 | Utsagn om aksjen selv ble ikke sjekket mot feltet `aksjen` («Aksjen steg» med `aksjen` falt besto) | høy | **rettet:** et verb om retningen med «aksjen» foran skal stemme med feltet, og uten feltet stoppes det |
| ECH2 | Retningen kunne gjentas eller snus med et pronomen etter ordlyden («Begge falt i dag.») | høy | **rettet:** et verb om retningen uten «aksjen» eller «kursen» foran stoppes |
| BH2, VG4, ECH4 | Sammensatte ord, ord med bindestrek og ord om lista slapp gjennom («Aksjemarkedet», «OSEBX-indeksen», «Oslo-børsen», «listen», «selskapene») | høy (BH), middels (VG, ECH) | **rettet**, med testene i `TestOmDagenEtterGjennomgangen` |
| BH3, VG5, ECH3 | En slutning eller kobling til signalet rett etter ordlyden besto («Det forklarer signalet.») | middels | **rettet:** «Derfor», «Dermed», «Følgelig» og «Så» rett etter ordlyden stoppes, og «Det» og «Dette» med et ord som kobler |
| BH4, ECH9 | Aksjen regnes mot forrige børsdag, som hovedindeksen, mens antallene og tabellen regnes mot forrige rad. På en dag med hull kan aksjen telles i antallene uten å få en ordlyd | middels | **åpent, spørsmål 1 til gruppen:** følger av instruksjonen («regnet som for hovedindeksen»), så graden settes ikke ned (regel 25) |
| BH5, VG3, ECH10 | «0 aksjer i lista steg og 0 falt» når kursene mangler | middels | **rettet:** antallene står ikke når begge er 0, og uten noe å si er det ingen setning |
| BH8, ECH5 | Linja om hovedindeksen i prompten kunne leses som at teksten kan nevne den når feltet er der, og linja om aksjen manglet forbeholdet | middels | **rettet:** avtrykket er satt på nytt, og versjonen står som 4 |
| VG2, ECH11 | Siden leser lista fra `aksje` i basen, og hentingen fra `AKSJEUNIVERS` | middels (VG), lav (ECH) | **står:** `test_aksje_er_lik_aksjeuniverset_felt_for_felt_og_i_samme_rekkefoelge` binder `aksje` i en ny base til `AKSJEUNIVERS`, og §55 målte at de var like i `ose.db`. Demotesten sammenligner nå også `aksjen` (BH12) |
| BH9, BH10, ECH12 | En feil i indeksen (RuntimeError) eller i utregningen av dagen ga 500 | lav | **rettet**, med tester |
| BH6 | Visningen kunne kjøre kontrollen på nytt på tekster fra versjon 3 | middels | **avvist:** `ki_visning.py` kjører ikke kontrollen, og `prikkede_tall` leser ikke `ANTALLENE` |
| BH7, ECH8 | Merket med «som» («aksjene som grensene er målt på») ble stoppet | lav | **rettet**. «Markedet for aksjen», «andre aksjer» og «på Oslo Børs» stoppes fortsatt: kontrollen leser ord, ikke mening (FR-603) |
| ECH6, BH11 | Snittet for bransjen tar med aksjen selv, så i en bransje med én aksje i lista er «bransjen» aksjen | lav | **står, spørsmål 2 til gruppen:** slik bransjen er regnet fra 10.2e |
| ECH7 | Ordlyden etter linjeskift eller med annet hvitt rom ble stoppet | lav | **rettet** |
| VG6, VG7 | Docstringer som ikke stemte lenger | lav | **rettet** |
| VG8 | Avtrykket dekker ikke feltene i grunnlaget | lav | **står:** `test_feltene` og `test_reglene_forklarer_hvert_felt_i_grunnlaget` låser feltene |
| VG9 | En dag der hovedindeksen steg, er bare enhetstestet | lav | **står:** `test_ordlyden_om_hovedindeksen` og `TestOmDagen` dekker begge retningene. Demodagen er fast |
| VG10, BH13 | Hjelpen sa «steg eller falt», og feltene kan være uendret | lav | **rettet** i README-en, `docs/hjelp.md` og `hjelpetekster.py` |
| VG11 | Et grunnlag med bare `aksjen` eller bare `hovedindeksen` godtas | lav | **står:** begge kan mangle hver for seg, og da er det ingen ordlyd |
| BH12 | Demotesten sammenlignet bare hovedindeksen | lav | **rettet:** også `aksjen` |

### Åpent etter svarene

Spørsmål til gruppen:

1. **BH4, ECH9 (middels, følger av instruksjonen):** aksjen regnes mot forrige børsdag, som hovedindeksen, men endringen i tabellen og antallene regnes mot forrige rad. På en dag der aksjen mangler kurs dagen før, får den ingen ordlyd, men telles i antallene. Skal aksjen regnes som i tabellen i stedet?
2. **ECH6, BH11 (lav):** «bransjen i snitt» tar med aksjen selv, så for en aksje alene i bransjen i lista sier setningen bare hva aksjen gjorde. Skal bransjen regnes uten aksjen, eller bare stå når den har minst to?
