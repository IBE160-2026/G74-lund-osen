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
