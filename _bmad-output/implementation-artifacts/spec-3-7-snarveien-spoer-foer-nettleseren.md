---
title: 'Story 3.7: snarveien spør før nettleseren, og KI-teksten på en ny PC'
type: 'feature'
created: '2026-11-12'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'a93c668f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-6-ikonet-og-snarveien.md'
---

Skrevet 12.11 etter instruksjonen «Ny liten story etter 3.6: snarveien spør før nettleseren åpnes» (limt inn 12.11 kl. 16:48) med tillegg 1 (kl. 16:36, limt inn på nytt kl. 16:48), tillegg 2 (kl. 16:49) og tillegg 3 (kl. 16:49). Instruksjonen og tilleggene føres i `docs/ai-prompts/2026-11-12.md` med flettingen. Bygget fra origin/main (`a93c668f`) på grenen `3-7-snarveien-spoer-foer-nettleseren`, i worktreen `G74-lund-osen-3-7`. 3.7 er neste ledige nummer i Epic 3, slik 3.6 var (`epics.md`, story 3.6).

*Svar 2026-11-11 kl. 22:07 (gruppens svar):* snarveien spør før nettleseren åpnes. Rådet anbefalte det. Funnet fra demoprøven 11.11 kl. 22:06: snarveien kom ikke på skrivebordet. `start/start.ps1` åpnet nettleseren (`Start-Process $Adresse`) før `Tilby-Snarvei` i `start/snarvei.ps1` spurte med `Read-Host`, så spørsmålet sto i vinduet bak nettleseren og ble ikke sett.

*Svar 2026-11-12 kl. 16:23:* ønsket om å gjøre ferdig alt nå. Rådet anbefalte det.

*Svar 2026-11-12 kl. 16:32 (gruppens svar, tillegg 1):* KI-teksten står på når den ekte versjonen installeres på en ny PC, med en tydelig beskjed når maskinen ikke har noen modell. Det retter svar 5 i planen for KI-laget (15.10) om at `.env.example` har `av`. Rådet anbefalte det.

*Svar 2026-11-12 kl. 16:41 (gruppens svar, tillegg 2):* startskriptet henter Gemma første gang den ekte versjonen startes, som planen 05.10 sa (FR-608: den lokale modellen er gratis standard). Rådet anbefalte det.

*Svar 2026-11-12 kl. 16:46 (gruppens svar, tillegg 3):* spørsmålet om Gemma ved første start tilbyr også egen API-nøkkel. Rådet anbefalte det.

*Tillegg 4 (limt inn 12.11 kl. 17:02), en rettelse fra rådet:* svaret 11.11 kl. 22:07 hadde én del til, som instruksjonen ikke tok med: får vinduet ikke svar på spørsmålet om snarveien innen 30 sekunder, lages ingen snarvei, og den tilbys igjen neste gang.

*Svar 2026-11-12 kl. 19:06 (gruppens svar på spørsmålene i PR #148, tillegg 5):* alle 26 forslag godtas som bygget, også spørsmål 26, så lenken «Slik slår du den på» får fargen til teksten rundt, med understrek, som de andre lenkene i appen. PR-en flettes i natt etter 8.27. Rådet anbefalte det.

## Spørsmål til gruppen

Forslaget er det som bygges (regel 3).

### Del A: snarveien før nettleseren (instruksjonen)

1. **Rekkefølgen.** *Forslag:* når appen svarer, skriver vinduet «Appen kjører på …», så spørsmålet om snarveien, og nettleseren åpnes etter svaret, også etter et nei og når vinduet ikke spør. Rett før spørsmålet står linja «Nettleseren åpner appen når du har svart.» Det gjelder begge spørsmålene, også det om en snarvei som starter en annen kopi.
2. **Hvor rekkefølgen står.** *Forslag:* i funksjonen `Snarvei-Og-Nettleser` i `start/snarvei.ps1`, som `start.ps1` kaller med to skriptblokker: om appen kjører, og hvordan nettleseren åpnes. Da kan testene prøve rekkefølgen med en falsk nettleser, i stedet for bare teksten i skriptet.
3. **Uten nettleser.** *Forslag:* med `OSE_START_UTEN_NETTLESER=1` står ikke linja om nettleseren, fordi ingen nettleser åpnes. `OSE_START_SVAR_SNARVEI` og `OSE_START_SVAR_JA` virker som før.
4. **Appen stoppet mens vinduet spør.** *Forslag:* da åpnes ingen nettleser, og beskjeden om at appen stoppet står som før (fra `start.ps1`, etter `WaitForExit`).
5. **Mac.** *Forslag:* ingen endring. `start.sh` har ingen snarvei, og der åpnes nettleseren som før.

### Del B: KI-teksten står på (tillegg 1)

6. **`.env.example`.** *Forslag:* `OSE_KI_TJENESTE=lokal`. `start.ps1` og `start.sh` kopierer den til `.env` når den mangler, så en ny installasjon har `lokal`, og Docker leser den samme `.env`. En `.env` som finnes fra før, endres ikke av dette. Kveldsjobben setter `OSE_KI_TJENESTE` selv i miljøet, som går foran `.env`, og virker som før.
7. **Linja i vinduet.** *Forslag:* hentingen skriver den alt i dag, i én linje, når Ollama ikke svarer, modellen mangler eller nøkkelen mangler: at teksten ikke lages, hvorfor og hvor i `docs/installasjon.md` det står hva man gjør. Endringene: linja ved første henting i en tom base får også pekeren, og «Start Ollama» blir «Start Ollama, eller installer den». Ingen ny sjekk i `start.ps1`. Sjekken i `ki_lokal.py` har tidsfristen 10 s fra før; en port der ingenting lytter, svarer med en gang, så hentingen venter ikke på Ollama.
8. **Siden: «ingen modell» eller en tekst kontrollen stoppet.** *Forslag:* uten ny migrasjon skiller siden dem på om KI-loggen har en rad. En tekst kontrollen stoppet, har en rad, og siden sier det som før. Har dagen ingen rad, står det i den ekte versjonen «Ingen KI-tekst for denne dagen. Den lages når kursene hentes, på en maskin med en språkmodell.» og lenken «Slik slår du den på» til installasjonen. Det samme gjelder «Børsdagen kort fortalt» på oversikten når dagen ikke har noen rad. Siden kan ikke vite om maskinen har en modell nå, så teksten sier når den lages, ikke at modellen mangler. Bryteren «Vis KI-tekst» virker som før, og demoen viser det den viste.
9. **Lenken.** *Forslag:* til `docs/installasjon.md` på GitHub, ankeret `ki-teksten`, som lenken til den ekte versjonen i demolinja (`EKTE_VERSJONEN_URL`), fordi appen ikke viser filene i `docs/`.

### Del C: Gemma eller egen nøkkel første gang (tillegg 2 og 3)

10. **Fila.** *Forslag:* `start/ki-modell.ps1` med `Tilby-KI`, som bare den ekte versjonen kaller, etter nøkkelen til EODHD og før hentingen.
11. **Når det spørres.** *Forslag:* bare i Windows, ikke med `OSE_START_SVAR_JA=1` (CI), og bare når alt dette gjelder: `.env` har `OSE_KI_TJENESTE=lokal` eller ingen slik linje, ingen `data\ki-nei-ekte` finnes, og Ollama svarer ikke på http://127.0.0.1:11434 med modellen `gemma4:e4b`, den samme som kveldsjobben bruker. Har `.env` fra før `av` eller en tjeneste med nøkkel, er det et valg, og vinduet spør ikke.
12. **Teksten i spørsmålet.** *Forslag:*

    ```
    KI-teksten på aksjesidene skrives av en språkmodell. Appen virker også uten.
      1  Hent Gemma, en gratis språkmodell som kjører på denne maskinen. Ollama installeres,
         og Gemma hentes nå (noen GB og noen minutter). Ingenting sendes ut.
      2  Bruk din egen API-nøkkel til Gemini, Anthropic (Claude) eller OpenAI (ChatGPT).
         En API-nøkkel er ikke det samme som et abonnement på ChatGPT eller Claude.
         Tallene teksten bygger på, sendes da til tjenesten, og det kan koste der.
         Gemini har en gratis nøkkel.
      3  Ikke nå. Vinduet spør ikke igjen.
    Skriv 1, 2 eller 3 og trykk Enter (bare Enter er 3)
    ```
13. **Svar 1.** *Forslag:* finnes `ollama`, hentes bare modellen. Ellers installeres Ollama med `winget install --id Ollama.Ollama --exact --source winget` når `winget` finnes. Pakkenavnet `Ollama.Ollama` er sjekket 12.11 med `winget search --id Ollama.Ollama --exact`, uten å installere noe. Uten `winget` åpnes https://ollama.com/download, og vinduet venter på Enter. Svarer ikke Ollama etterpå, startes `ollama serve`, og vinduet venter i høyst 30 s. Så hentes modellen med `ollama pull gemma4:e4b`, med framdriften i vinduet. `.env` endres ikke, fordi den alt har `lokal`.
14. **En feil.** *Forslag:* feiler `winget`, `ollama pull` eller noe annet, sier vinduet hva som skjedde, at appen starter uten KI-tekst, og at vinduet spør igjen neste gang, eller at det står under «Den lokale modellen uten Docker» i `docs/installasjon.md`. En feil huskes ikke som nei. Ctrl+C under nedlastingen stopper vinduet, som før.
15. **Svar 2.** *Forslag:* vinduet spør «Hvilken tjeneste? Skriv g for Gemini, a for Anthropic (Claude) eller o for OpenAI (ChatGPT)», så etter nøkkelen med skjult inntasting, som for EODHD-nøkkelen. `OSE_KI_TJENESTE` og nøkkelen til den tjenesten skrives i `.env`. En linje som finnes fra før, byttes ut der den står, og flere like linjer blir én. Ingenting annet i `.env` endres. Nøkkelen skrives aldri ut.
16. **En nøkkel som er tom eller feil.** *Forslag:* en tom nøkkel eller en ukjent bokstav endrer ingenting i `.env`, og vinduet spør igjen neste gang. Nøkkelen prøves ikke med et kall ved oppstart; er den feil, sier hentingen det i linja fra del B (spørsmål 7).
17. **Svar 3, et tomt svar og alt annet.** *Forslag:* huskes som nei i `data\ki-nei-ekte`, som ikke committes (regel 10). Sletter man fila, spørres det igjen.
18. **Variablene for testene og CI.** *Forslag:* `OSE_START_SVAR_KI` (1, 2 eller 3), `OSE_START_SVAR_KI_TJENESTE` (g, a eller o) og `OSE_START_SVAR_KI_NOEKKEL` (bare testene, med falske nøkler), og `OSE_START_OLLAMA_URL` og `OSE_START_OLLAMA_VENT` (adressen og ventetiden i testene). `OSE_START_SVAR_JA=1` gir verken spørsmål eller endring i `.env`, og CI laster aldri ned Ollama eller modellen.
19. **Mac (`start.sh`).** *Forslag:* ikke i denne storyen. En senere story kan stille samme spørsmål i `start.sh`, med `brew install ollama` når Homebrew finnes, ellers https://ollama.com/download, og samme valg for egen nøkkel. Til da har en ny `.env` på Mac `lokal`, og hentingen sier fra når Ollama mangler.
20. **Svar 1 i planen for KI-laget (15.10).** Der står «Ingenting installeres på Windows» om kveldshentingen på gruppens PC. Tillegg 2 installerer Ollama på brukerens maskin etter et ja. *Forslag:* svar 1 gjelder fortsatt kveldsjobben, som bruker Ollama i Docker, og får en datert linje om det når gruppen har svart.
    *Svar 12.11 kl. 19:06:* som bygget. Linja står under svar 1 i `epics.md`.
21. **README-en.** *Forslag:* innenfor reglene fra 3.5i (fem avsnitt og høyst 25 ord per steg) får linja om den ekte versjonen to setninger: at den første gang tilbyr å hente Gemma, en gratis lokal modell for KI-teksten, eller å bruke egen API-nøkkel, og at appen virker uten KI-tekst. Minnet står som det er målt: modellen er prøvd på en maskin med 15,7 GB minne (`malinger.md` §19). Raden «KI-tekst» i tabellen «Demoen og den ekte versjonen» kommer med 8.26 og følger når main med 8.26 er flettet inn.

### Tillegg 4: fristen på 30 sekunder

22. **Fristen.** *Forslag:* spørsmålet om snarveien, også det om en snarvei som starter en annen kopi, venter høyst 30 sekunder (`start/frist.ps1`). Uten svar lages eller flyttes ingen snarvei, vinduet sier at spørsmålet kommer igjen neste gang, nettleseren åpnes, og ingenting huskes. Det første spørsmålet om KI-teksten har samme frist, og uten svar er det «ikke nå» bare denne gangen, så appen alltid starter. Spørsmålene etter et valg (hvilken tjeneste, nøkkelen, Enter etter nedlastingen) har ingen frist, fordi brukeren alt har svart. I testene setter `OSE_START_SVAR_FRIST` sekundene, og `OSE_START_SVAR_SNARVEI` virker som før. Uten svar betyr også at standard inn er lukket.

### Fra testene

23. **De to kommandoene uten Docker.** `tests/test_docker.py` krever at hver kommando i en kodeblokk i installasjonen har en rad i tabellen for README-prøven i `docs/kvalitetssikring.md`. `winget install --id Ollama.Ollama --exact --source winget` og `ollama pull gemma4:e4b` er ikke kjørt, fordi instruksjonen sier at ingenting installeres på denne PC-en. *Forslag:* de står som kode i teksten, ikke som blokker, til de er prøvd på en PC uten Ollama i neste README-prøve. Da blir de blokker med en rad i tabellen.

## Delene og «Ville feilet hvis»

- **Del A:** `TestRekkefoelgen` i `tests/test_snarveien_foer_nettleseren_3_7.py` (Windows).
- **Del B:** `TestKITekstenStaarPaa` og `TestSiden` i samme fil.
- **Del C:** `TestKIValget` (Windows) i samme fil, med falske `winget` og `ollama` og en falsk Ollama på 127.0.0.1 i testen.
- **Tillegg 4:** `TestFristen` (Windows) i samme fil, med standard inn åpen uten svar og fristen satt til 2 sekunder.
- **Den ekte versjonen og demoen på sidene:** `test_ki_visning.py`, `test_ki_dagen.py` (ingen rad gir linja og lenken, en tekst kontrollen stoppet gir den ikke) og `TestDemoen`.
- **CI:** steget «Snarveien og KI-spørsmålet på Windows (3.7)» kjører fila og feiler hvis noen test hoppes over.

## Gjennomgangen 12.11 kl. 17:14 og triagen

Blind Hunter (bare diffen), Edge Case Hunter og Verification Gap (grenen, bare lesing) hadde 18, 15 og 15 funn. To var høye, begge fra Verification Gap. Rettet før første commit:

- **VG1 og VG2 (høye), BH4 og ECH12:** ingen test sendte et svar gjennom lesingen, og løkka for et ekte vindu ble aldri kjørt. Tastene leses nå i `Les-Taster` gjennom to skriptblokker, som testene gir falske taster (Enter, Backspace, frist uten taster, stjerner for en skjult nøkkel). Et svar på standard inn («j» og «1») prøves gjennom hele lesingen.
- **BH3 og ECH1 (middels):** taster trykket før spørsmålet, for eksempel Enter mens `uv sync` går, ble svaret og kunne huskes som nei. Bufferen tømmes nå før spørsmålet.
- **BH2 (middels):** ventingen på Enter uten `winget`, tjenesten og nøkkelen hadde ingen frist. Nå 10 minutter for installasjonen, 30 sekunder for tjenesten og 2 minutter for nøkkelen, som skrives inn skjult med stjerner.
- **ECH2 og BH10 (middels):** vinduet leste den første linja med `OSE_KI_TJENESTE`, mens hentingen (python-dotenv) leser den siste. Nå leses den siste, med `export ` og en kommentar etter ` #` tatt bort (test mot `dotenv_values`).
- **ECH3 (middels):** miljøet går foran `.env`, også i vinduet, og adressen til Ollama er `OSE_KI_OLLAMA_URL` fra miljøet eller `.env` når den finnes.
- **ECH4 og BH1 (middels):** linja om modellen lovet tekst for eldre dager, som ikke kan få den (AD-7). Nå står den bare for siste børsdag, og eldre dager har grunnen som før.
- **ECH5 (middels):** forsiden sa at maskinen trenger en modell også når aksjene hadde KI-tekst den dagen. Nå bare når ingen aksje har en rad, og bare for siste dag.
- **ECH6 og VG8 (middels):** en feil i spørsmålet om snarveien ble til `Stopp` gjennom `trap` i `start.ps1`, som stopper appen. Nå fanges den, og nettleseren åpnes. Uten en konsoll å lese tastene fra brukes `Read-Host`, som før. Fristen tåler en verdi som ikke er et tall.
- **VG3 (middels):** lukket standard inn prøves.
- **VG4 (middels):** demoen uten rad prøves uten linja og lenken (`test_funnene_8_2b.py`).
- **VG5 og ECH7 (middels og lav):** er Ollama installert, men stoppet, startes den før det spørres, og etter svar 1. Prøvd med en falsk `ollama serve` mot en lukket port.
- **VG6 (middels):** at siden der Ollama lastes ned, åpnes, prøves med en falsk `Start-Process`.
- **VG7 (middels):** svar 2 prøves på en `.env` fra `.env.example`, med «» og æøå, og bare de to linjene endres.
- **ECH8 og BH7:** gir `winget` en annen kode enn 0, men Ollama finnes etterpå (pakken var installert), hentes modellen. Ollama under Program Files finnes også.
- **ECH10:** meldingene viser til «Den lokale modellen for KI-teksten» og «Egen nøkkel til Gemini, Anthropic eller OpenAI», som finnes (test). En `.env` som ikke kan skrives, gir beskjeden.
- **ECH13:** bare 3 og bare Enter huskes som nei. Et annet svar, for eksempel `j`, gjelder bare denne gangen. Det endrer forslaget i spørsmål 17, se under.
- **BH13, ECH14 og ECH15:** setningene i installasjonen er rettet, og den sier at kveldsjobben velger selv. Ankeret `ki-teksten` står foran pila, ikke inne i den.
- **BH14:** ankeret står nå utenfor `<details>`.
- **BH18, VG9–VG12, VG14 og VG15:** `"$valg"` før `.Trim()`, fristen på 30 sekunder, modellen og adressen mot `ki_lokal.py`, stedene vinduet viser til, `OSE_START_SVAR_JA=1` alene, framdrift på stderr fra den falske `ollama`, og én linje fra hentingen er prøvd.
- **Testene:** `ProgramFiles` og `LOCALAPPDATA` peker til midlertidige mapper, og `OSE_KI_TJENESTE` fra `conftest.py` tas bort, så ingen ekte Ollama på PC-en finnes eller startes av testene.

*Lukket 2026-11-12 (gruppens svar kl. 19:06, tillegg 5):* ECH3, ECH4 og ECH5 (middels, spørsmål 25) og ECH13 (lav, spørsmål 24) er lukket som bygget. Ingen funn på middels eller over står åpne.

Ikke rettet, lave:

- **BH5:** et svar som er skrevet uten Enter når fristen går ut, forkastes. Fristen er for hele svaret.
- **BH6 og ECH11:** EOF og en frist som går ut, gir samme melding. Lesingen bruker nå én leser for hele skriptet.
- **BH8 og ECH9:** Ollama-appen og `ollama serve` kan starte samtidig etter installasjonen; den andre feiler på porten, og den første svarer. Den skjulte `serve` lever til maskinen startes på nytt. Ventetiden måles nå med klokka.
- **BH9:** om framdriften fra `winget` og `ollama pull` vises riktig i et ekte vindu, er ikke prøvd. Det prøves i README-prøven (spørsmål 23).
- **BH11:** «Gemini har en gratis nøkkel» står i tillegg 3. Vilkårene om trening for gratisnøkkelen i EØS står sitert i `docs/kilder-og-rettigheter.md`, og installasjonen viser dit.
- **BH12:** `.env` lages fra `.env.example` (UTF-8) og skrives av startskriptet som UTF-8, så ANSI gjelder ikke.
- **BH15:** `_hva_naa` gir ingen tekst med punktum til slutt, så det blir ikke «..».
- **BH16:** malen sammenligner med `"ingen_modell"` som tekst. Testene sammenligner hele linja med lenken.
- **BH17:** `demo_sti()` peker til en midlertidig mappe i testene (`conftest.py`), som i 3.6.
- **VG13:** `OSE_START_SVAR_JA=1` sammen med `OSE_START_SVAR_KI` spør, som for snarveien, og kommentaren sier det.

## Spørsmål til gruppen etter gjennomgangen

24. **Spørsmål 17, et svar som ikke er 1, 2 eller 3** (ECH13, lav). *Forslag:* bare 3 og bare Enter huskes som nei. Et annet svar gjelder bare denne gangen, fordi `j` er svaret på de andre spørsmålene i vinduet.
    *Svar 12.11 kl. 19:06:* som bygget. ECH13 er lukket.
25. **Spørsmål 8 og 11 etter ECH3, ECH4 og ECH5** (middels). *Forslag:* som bygget. Linja om modellen står bare for siste børsdag, og på forsiden bare når ingen aksje har en rad. Vinduet leser tjenesten og adressen som hentingen leser dem, med miljøet først. Funnene står åpne til gruppen har svart (regel 25).
    *Svar 12.11 kl. 19:06:* som bygget. ECH3, ECH4 og ECH5 er lukket.

## Bildene av linja 12.11

Tatt etter tillegg 1 med en testbase uten demomerket og uten rader i KI-loggen (`forsiden_med(None)` i `tests/test_ki_dagen.py`, med `BASE_STI` i en midlertidig mappe), før på `a93c668f` og etter på `d3cbb938`, med waitress på en ledig port og Edge uten vindu, 1280 px. Bildene ligger utenfor repoet. På aksjesiden for EQNR, fredag 30.10, sto før «Ingen KI-tekst for denne dagen: KI var slått av, eller modellen svarte ikke da hentingen gikk.» og etter «Ingen KI-tekst for denne dagen. Den lages når kursene hentes, på en maskin med en språkmodell. Slik slår du den på». Under «Børsdagen kort fortalt» sto før «Dagen er uten KI-tekst.» og etter den samme setningen med de samme to setningene og lenken.

26. **Fargen på lenken** (fra bildene, lav). Lenken «Slik slår du den på» står i nettleserens blå med understrek, mens resten av rammen er i blekk. *Forslag:* lenken får fargen til teksten rundt, med understrek, i `stil.css`. Det endrer avtrykkene bak alle bildene i `docs/appen/`, så det bygges etter gruppens svar, med bildene tatt på nytt.
    *Svar 12.11 kl. 19:06:* ja. Det bygges når main med 8.27 er flettet inn i grenen.
