---
title: 'Story 3.6: ikonet og snarveien (del C)'
type: 'feature'
created: '2026-11-11'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '059dc10c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
---

Skrevet 11.11 etter instruksjonen «Del C, ikonet og snarveien 10.11» (limt inn 10.11 kl. 17:23, med tillegget om demoen kl. 17:23), som føres i `docs/ai-prompts/2026-11-10.md` når den har Utført-linje. Bygget fra main (`059dc10c`), etter at del A fikk Utført-linje, på grenen `3-6-ikonet-og-snarveien`, i worktreen `G74-lund-osen-3-6`. 3.6 er neste ledige nummer i Epic 3.

*Svar 2026-11-10 kl. 14:07 (gruppens svar):* appen får et ikon laget av logoen i toppen, og en snarvei «OSE Signal» på skrivebordet i Windows. Mobil kommer i en senere versjon, fordi appen bare svarer på 127.0.0.1. Rådet anbefalte det.

*Svar 2026-11-10 kl. 15:57 (gruppens svar):* alt nytt skal kunne ses i demoen uten nøkkel, og startskriptet for demoen tilbyr også snarveien, med et eget navn. Rådet anbefalte det.

## Spørsmål til gruppen

Forslaget er det som bygges. Spørsmålene står åpne til gruppen har svart.

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

## Mutantene

Én per del før gjennomgangen, alle fanget: den høye søylen hvit (del 1), et nei som ikke huskes (del 2) og installasjonen uten mobil (del 3). Etter gjennomgangen ble seks mutanter kjørt, og fem ble fanget:

- Enter er ja (VG4)
- ikonet uten `src` (VG5)
- kallet etter ventingen (VG2)
- en død snarvei (BH2)
- `Set-Content` for et nei utenfor `try` (ECH1)

Den sjette, `New-Item` utenfor `try`, overlevde. `New-Item -Force` feiler ikke når `data` er en fil, så det er `Set-Content` som feiler der, og den er fanget. Hver fil var lik før og etter (sha256).
