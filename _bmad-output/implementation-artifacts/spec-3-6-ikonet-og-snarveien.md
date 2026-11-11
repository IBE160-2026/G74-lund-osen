---
title: 'Story 3.6: ikonet og snarveien (del C)'
type: 'feature'
created: '2026-11-11'
status: 'done'
route: 'dispatch'
baseline_commit: '059dc10c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
---

Skrevet 11.11 etter instruksjonen «Del C, ikonet og snarveien 10.11» (limt inn 10.11 kl. 17:23, med tillegget om demoen kl. 17:23), som føres i `docs/ai-prompts/2026-11-10.md` når den har Utført-linje. Bygget fra main (`059dc10c`), etter at del A fikk Utført-linje, på grenen `3-6-ikonet-og-snarveien`, i worktreen `G74-lund-osen-3-6`. 3.6 er neste ledige nummer i Epic 3.

*Svar 2026-11-10 kl. 14:07 (gruppens svar):* appen får et ikon laget av logoen i toppen, og en snarvei «OSE Signal» på skrivebordet i Windows. Mobil kommer i en senere versjon, fordi appen bare svarer på 127.0.0.1. Rådet anbefalte det.

*Svar 2026-11-10 kl. 15:57 (gruppens svar):* alt nytt skal kunne ses i demoen uten nøkkel, og startskriptet for demoen tilbyr også snarveien, med et eget navn. Rådet anbefalte det.

*Svar 2026-11-11 kl. 13:47 (gruppens svar):* ja til ikonet som bygget (spørsmål 1) og til forslagene i spørsmål 2–7. I spørsmål 8 skal startskriptet spørre om snarveien skal peke hit når den peker på en annen kopi. Del C flettes når svarene er bygget, gjennomgått og CI er grønn, uten at gruppen ser på den igjen. Rådet anbefalte det.

*Svar 2026-11-11 kl. 13:49 (gruppens svar):* README-en får en fjerde liste under «Status», «Ekstra, ferdig», og brukertesten flyttes fra «Neste i v1» til setningen om det som er ferdig rundt appen, fordi «Ferdig» lister det appen kan. Rådet anbefalte det.

## Spørsmål til gruppen

Forslaget er det som bygges. *Besvart 2026-11-11 kl. 13:47:* spørsmål 1–7 som foreslått, og spørsmål 8 annerledes enn forslaget (se «Spørsmål 8, slik gruppen svarte»).

1. **Ikonet.** *Forslag:* de tre søylene fra logoen, hvite og den høyeste oransje, på et avrundet kvadrat i blekk, som stripa. Det tegnes av `src/ikon.py` med bare standardbiblioteket (`zlib` og `struct`) og ligger i `src/static` som `ikon.svg`, `ikon-16/32/48/180/192/512.png` og `ikon.ico` med 16, 32, 48 og 256 px.
2. **Fanen.** *Forslag:* `_ramme.html` har `ikon.svg`, `ikon-32.png` og `ikon-180.png` (for iPhone og iPad), så alle sidene, i demoen og i den ekte versjonen, viser det i fanen.
3. **Når det spørres.** *Forslag:* når appen svarer, etter at nettleseren er åpnet, så spørsmålet ikke står i veien for oppstarten. Bare i Windows, og ikke i CI (`OSE_START_SVAR_JA=1`).
4. **Et nei.** *Forslag:* huskes i `data\snarvei-nei-ekte` eller `data\snarvei-nei-demo`, som ikke committes (regel 10). Sletter man fila, spørres det igjen. Finnes snarveien, spørres det ikke.
5. **Demoen.** *Forslag:* «OSE Signal (demo)», som starter «Start demoen.cmd», og «OSE Signal» for den ekte versjonen, som starter «Start den ekte versjonen.cmd», begge med ikonet.
6. **Mac.** *Forslag:* ingen snarvei i denne storyen; instruksjonen gjelder Windows.
7. **Bildet.** *Forslag:* ikonet i 48 px i installasjonen, ved punktet om snarveien. Et skjermbilde av skrivebordet viser andres filer og gir ikke mer.
   *Rettet 2026-11-11 (testene):* installasjonen har bare de tre skjermbildene fra gjennomgangen (`test_bildene_er_de_tre_fra_gjennomgangen_og_ci_merket`), så ikonet beskrives med ord der, og «Kom i gang» har fem avsnitt (`test_dobbeltklikket_staar_foerst_og_ikke_bak_en_pil`), så snarveien står i avsnittet «Første gang».

## Delene og «Ville feilet hvis»

- **Del 1, ikonet:** `TestIkonet` i `tests/test_ikonet_og_snarveien_3_6.py`: filene er det `src/ikon.py` lager, størrelsene stemmer, søylene er logoen, hver side har ikonet i fanen, og ingen nye avhengigheter.
- **Del 2, snarveien:** `start/snarvei.ps1`, som `start.ps1` kaller når appen svarer. `TestSnarveien` (Windows) og `TestStartskriptet`: ja lager snarveien med ikonet og riktig fil, også for demoen, nei huskes, en snarvei som finnes gir ikke spørsmålet, og CI gir ingen snarvei.
- **Del 3, dokumentene:** README-en og `docs/installasjon.md` sier det, med ikonet og at mobil kommer senere (`TestDokumentene`).

## Gjennomgangen 11.11 kl. 04:10 og triagen

Blind Hunter (bare diffen) hadde 15 funn, og Edge Case Hunter og Verification Gap (grenen, bare lesing) hadde 12 og 9 funn. Ingen var høye. Rettet i commiten etter gjennomgangen:

- **BH1 (middels):** PNG-ene ble sammenlignet byte for byte, så en annen zlib kunne gi feil uten at bildet var endret. Nå sammenlignes pikslene, med CRC og IHDR sjekket.
- **BH12:** ICO-katalogen sjekkes nå fullt ut: størrelse, farger, plan, bit, lengde og start.
- **BH2 og ECH4 (middels):** en snarvei til en mappe som er slettet, tilbys på nytt. En snarvei til en annen kopi som finnes, blir stående, som instruksjonen sier («spør ikke igjen hvis snarveien finnes»). Det står åpent til gruppen har svart (regel 25), se under.
- **ECH1, BH9 og VG6 (middels):** et nei som ikke kunne skrives, ga en feil som `trap` i `start.ps1` gjorde om til `Stopp`, og da stoppet appen. Feilen fanges nå, og vinduet sier at det spør igjen neste gang (test).
- **ECH2 (middels):** har appen alt stoppet, spørres det ikke. Mens spørsmålet står, venter vinduet på svaret; etter svaret kommer beskjeden om at appen stoppet, som før.
- **BH3 og ECH5:** rota er nå `Split-Path -Parent $PSScriptRoot`. Det er det `start.ps1` alt gjør `Set-Location` til, og det virker også for en UNC-sti.
- **BH6:** README-en nevner «OSE Signal (demo)».
- **BH13 og VG5:** alle tre ikonfilene hentes. Ikonet i snarveien må være `src\static\ikon.ico` og finnes.
- **VG7:** testene sjekker `WorkingDirectory`.
- **VG1 (middels):** snarveitestene kjøres i jobben «Snarveien på Windows» i CI, og steget feiler hvis noen hoppes over.
- **VG2, VG3 og VG4 (middels):** testene sjekker hele kallet, med rota, og at det står etter nettleseren og før ventingen. Et tomt svar, «nei» og «x» er nei (test).
- **ECH12:** «Mappestruktur» nevner snarveien (regel 19).

Ikke rettet, lave:

- **BH4 og ECH6:** spørsmålet står i samme vindu som waitress. Waitress skriver ikke en linje per side, og Ctrl+C stopper begge, som vinduet sier.
- **BH5 og ECH3:** et tomt svar huskes som nei. Det følger av instruksjonen («et nei huskes»), og spørsmålet sier «bare Enter for nei».
- **BH7:** bare j, ja, y og yes er ja.
- **BH8:** `OSE_START_SVAR_SNARVEI` brukes bare av testene, og de gir alltid `OSE_SKRIVEBORD`.
- **BH10 og ECH7:** en sti med apostrof i testene. Det gjelder ingen av maskinene våre eller CI.
- **BH11:** `start.ps1` prøves på teksten og i CI med `OSE_START_SVAR_JA=1`, som hopper over spørsmålet.
- **BH14 og ECH8:** ikonet har ikke noe avtrykk i adressen. Det er likt i alle versjoner så langt.
- **BH15 og ECH11:** det tar om lag 10 s å tegne ikonet i testene.
- **ECH9:** `/favicon.ico` gir 404 i nettleseren. Alle sidene har lenkene.
- **ECH10:** ICO-fila har bare PNG-bilder. Det virker fra Windows Vista.
- **VG8:** vaktene for ikke-Windows og for et skrivebord som mangler, er ikke prøvd.
- **VG9:** fire sider til bruker `_ramme.html`.

## Åpent til gruppen har svart

8. **En snarvei til en annen kopi** (BH2 og ECH4, middels). Pakkes en ny ZIP ut i en ny mappe, starter «OSE Signal» fortsatt den gamle kopien, og den nye spør ikke, fordi snarveien finnes. *Forslag:* slik instruksjonen sier. Snarveien rettes bare når mappen den peker på, er slettet, og installasjonen kan si at man sletter snarveien for å få en ny.
   *Besvart 2026-11-11 kl. 13:47:* ikke som forslaget. Startskriptet spør om snarveien skal peke hit. Se «Spørsmål 8, slik gruppen svarte». Ingenting står åpent etter gjennomgangen av svaret.

## Spørsmål 8, slik gruppen svarte (11.11)

Bygget etter svaret kl. 13:47, i `d4dd5382`, og rettet etter gjennomgangen i `f8eaec8f`.

- **Hva skjer:** finnes snarveien og starter den samme startfil i en annen kopi som finnes, sier vinduet hvilken mappe den peker på. Så spør det én gang om den skal starte denne kopien i stedet.
  - Ja retter snarveien hit, med målet, mappa og ikonet, og nullstiller argumentene.
  - Nei huskes i data-mappa til denne kopien, i `data\snarvei-nei-flytt-<versjon>`, ved siden av det andre neiet.
  - En snarvei til en mappe som er slettet, rettes som før.
  - En snarvei som starter denne kopien, også skrevet med andre store og små bokstaver, gir ikke spørsmålet.
  - Det gjelder begge snarveiene, og installasjonen sier det med én setning.
- **Ville feilet hvis:**
  - en snarvei til en annen kopi ble stående uten spørsmål, vinduet ikke sa mappa, eller ja ikke rettet den hit (`test_en_snarvei_til_en_annen_kopi_ja_flytter_den_hit`, ekte og demo);
  - nei flyttet snarveien, ble husket i den andre kopien eller ikke ble husket (`…_nei_huskes_i_denne_kopien`);
  - en snarvei hit ble regnet som en annen kopi (`…_hit_med_andre_store_bokstaver_…`);
  - installasjonen manglet setningen (`TestDokumentene`).
- **Mutanten:** en snarvei til en annen kopi som finnes, blir stående uten spørsmål, slik det var før svaret. Den ble fanget av fire tester. Fila var lik før og etter og lik HEAD (sha256).

### Gjennomgangen 11.11 kl. 14:36–14:55 og triagen

Blind Hunter (bare diffen) hadde 7 funn. Edge Case Hunter og Verification Gap (grenen, bare lesing) hadde 5 og 4 funn. Ingen var høye. Rettet i `f8eaec8f`:

- **ECH1 og BH1 (middels):** et nei til å la snarveien starte denne kopien ble husket i samme fil som et nei til å lage den. Ble den andre kopien slettet, ble snarveien død og ble aldri tilbudt på nytt. Neiet har nå sin egen fil, `snarvei-nei-flytt-<versjon>`, og installasjonen sier at man sletter fila som begynner med `snarvei-nei` (test, og mutanten med samme fil ble fanget).
- **VG1 (middels):** spørsmålet om å starte denne kopien ble aldri prøvd, fordi testene svarer gjennom miljøvariabelen. Spørsmålet skrives nå også da, og teksten prøves for begge spørsmålene. Mutanten uten spørsmålet ble fanget av seks tester.
- **ECH3 og BH2:** en snarvei med samme navn til noe annet enn startfila, for eksempel en brukeren har laget selv, ble regnet som en annen kopi og kunne overskrives. Nå er bare samme startfil i en annen mappe en annen kopi, og argumentene fra den gamle snarveien nullstilles ved ja (tester).
- **VG2:** testen for den døde snarveien sjekker at den tilbys som før, uten å si en mappe.
- **BH5:** testen med store bokstaver sjekker at snarveien faktisk lagret stien slik.
- **ECH5 og BH7:** regelsetningen etter listene sier «Ekstra, hvis tiden rekker», fordi «Ekstra, ferdig» er ferdig.

Ikke rettet, lave:

- **BH3 og ECH2:** `GetFullPath` gjør ikke om korte 8.3-navn, subst-stasjoner eller junctions, så samme kopi nådd på to måter kan gi spørsmålet. Svarer man nei, huskes det, og ingenting går tapt. Testene bruker lange stier.
- **BH4:** et ja huskes ikke. Bruker man to kopier vekselvis, spør hver av dem når den andre har snarveien. Det følger av svaret: ja flytter snarveien hit.
- **ECH4:** en snarvei vi ikke har laget, med en miljøvariabel eller relativ sti, kan regnes som død og tilbys på nytt. Ja overskriver den da, men bare etter spørsmålet.
- **BH6:** et nei som ikke kan skrives, er prøvd for spørsmålet om å lage snarveien. Spørsmålet om å flytte den bruker de samme linjene.
- **VG3:** ingen test har en sti som bare `GetFullPath` gjør lik, som en relativ sti.
- **VG4:** et gammelt nei til å lage snarveien stopper også spørsmålet om å flytte den. Det følger av at et nei huskes. Fila slettes for å bli spurt igjen.
- **Kosmetisk:** en lang kommentarlinje i toppen av `snarvei.ps1`.

## README-en etter svaret kl. 13:49

`7153b37a`: «Status» har lista «Ekstra, ferdig» rett etter «Ferdig». Den har målingen av omsetningen og notatene, som ikke lenger står under «Ekstra, hvis tiden rekker», og ikonet med snarveien. Brukertesten er flyttet fra «Neste i v1» til setningen om det som er ferdig rundt appen. I `tests/test_docker.py` står kommentarer om svaret og «Ville feilet hvis» for den nye lista: den mangler, står et annet sted, har for mange eller for få punkter, eller et punkt står i en annen liste. Det gjelder også om brukertesten står igjen i en liste.

## Mutantene

Én per del før gjennomgangen, alle fanget: den høye søylen hvit (del 1), et nei som ikke huskes (del 2) og installasjonen uten mobil (del 3). Etter gjennomgangen ble seks mutanter kjørt, og fem ble fanget:

- Enter er ja (VG4)
- ikonet uten `src` (VG5)
- kallet etter ventingen (VG2)
- en død snarvei (BH2)
- `Set-Content` for et nei utenfor `try` (ECH1)

Den sjette, `New-Item` utenfor `try`, overlevde. `New-Item -Force` feiler ikke når `data` er en fil, så det er `Set-Content` som feiler der, og den er fanget. Hver fil var lik før og etter (sha256).

## CI etter gjennomgangen: lenketesten i test_utseende.py (11.11)

Pytest i CI feilet på `ec558aec` kl. 04:23 i `TestRammen::test_hver_lenke_gaar_til_en_side_som_finnes`, med `('tom base', '/static/ikon.svg')`. Kl. 04:29 startet Windows Update maskinen på nytt midt i rettingen, og den ble gjort ferdig 11.11 etter instruksjonen kl. 11:52.

- **Årsaken:** testen går gjennom hver `href` på sidene, også i `<head>`, mot en liste over lovlige adresser. Stilarket står på lista med sitt eget mønster (2.7a). Ikonlenkene fra 3.6 er `<link rel="icon">` og `<link rel="apple-touch-icon">` i `_ramme.html`, og de manglet der. Lenkene i appen er riktige, så rettingen er i testen.
- **Rettingen:** lista har nå nøyaktig de tre adressene `/static/ikon.svg`, `/static/ikon-32.png` og `/static/ikon-180.png`, og bare når fila finnes i `src/static`. Ingen andre adresser slippes gjennom, og ingen sjekk er tatt bort.
- **Ville feilet hvis** en side lenket til en annen ikonfil enn de tre, for eksempel `/static/ikon-64.png`, eller hvis en av de tre filene manglet i `src/static`.

## Flettingen

*Lagt til 2026-11-11:* 3.6 er flettet med PR #144 i `078c7c28` kl. 15:21, låst til head-en `11998215` (main flettet inn), etter instruksjonen kl. 14:26 i `docs/ai-prompts/2026-11-11.md` og gruppens svar 11.11 kl. 13:47 og 13:49. Hele settet lokalt i åtte deler før pushen kl. 15:15 (`date`), hver del bare når ingen annen pytest kjørte: 5166 bestått, 25 hoppet over og 0 feilet, til sammen de 5191 som `pytest --collect-only` finner. CI var grønn på head-en (run 43036831538), med 5143 bestått og 48 hoppet over i jobben `pytest`, og steget «Snarveien på Windows» kjørte 29 tester uten at noen ble hoppet over. Treet på main etter `git pull --ff-only` er likt treet på `11998215`. Ingen funn på middels eller over sto åpne.
