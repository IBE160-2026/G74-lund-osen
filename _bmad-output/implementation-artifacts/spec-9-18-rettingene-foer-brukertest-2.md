---
title: 'Story 9.18: rettingene før brukertest 2'
type: 'feature'
created: '2026-11-17'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'e29f3020'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/docs/heuristisk-evaluering.md'
  - '{project-root}/docs/ux-logg.md'
  - '{project-root}/docs/brukertest.md'
---

Skrevet 17.11 i vinduet som bygde 9.16 og 9.17, etter instruksjonen om
rettingene før brukertest 2 og gruppens svar 17.11 kl. 13:03–13:33 på
spørsmålene i 9.17, med beskjeden kl. 14:16 (begge i
`docs/ai-prompts/2026-11-17.md`). Rådet anbefalte svarene. Neste ledige nummer i
Epic 9 etter 9.17 er 9.18. Worktreen er `G74-lund-osen-9-18`, på grenen
`9-18-rettingene-foer-brukertest-2`, fra `origin/main` (`e29f3020`). Brukertest
2 er tidligst fredag 20.11, i den ekte versjonen.

## Storyen

Som **gruppe** vil vi rette funnene fra den heuristiske evalueringen som gruppen
valgte før brukertest 2, så testen måler appen uten hindrene vi alt kjenner.

**Oppfyller:** svarene 17.11 kl. 13:03–13:33 på spørsmål 1–4 i 9.17, og HE18 ·
**Begrenses av:** regel 3, 16, 19, 21, 22 og 23, NFR-06, og ingen ny migrasjon
før testen

**Avhenger av:** 9.17, 8.21, 8.22, 8.25, 8.26. **Én økt:** nei.

## Svarene

*Svar 2026-11-17 kl. 13:03–13:33 (gruppens svar, rådet anbefalte det):* HE2,
HE3, HE5, HE8, HE9 og HE10 fra evalueringen og gruppens HE14–HE18 rettes før
brukertest 2, i én story. HE1 blir et spørsmål i brukertest 2. HE4, HE6, HE7,
HE11, HE12 og HE13 venter til etter testen. *Beskjeden kl. 14:16 (svaret på
spørsmål 4 i 9.17):* «Mine notater» i Min liste viser alle notatene, også uten
stjerne. Følg setter også stjernen, så aksjen står i tabellen i Min liste, og
beskrivelsen av HE15 rettes.

## Rettingene

Hver retting får en test som feiler mot koden før rettingen.

| Funn | Retting |
|---|---|
| HE14 | En lenke ved månedspilene i «Signalet dag for dag», tilbake til måneden for dagen siden viser, for eksempel «Til november 2026». Den vises bare når en annen måned er valgt, og beholder dagen eller perioden og ankeret |
| HE15 | Følg setter også stjernen, så aksjen står i tabellen i Min liste. Stjernen kan tas bort etterpå. Fjern endres ikke. *Slått opp 17.11:* det er alt bygget, se «Bygget» og spørsmål 1 |
| HE2 | «Slett» ved et notat spør først, som `bekreft_fjern.html`, og sier om et tenkt kjøp slettes også. Avbryt lar alt stå |
| HE3 | På smal skjerm (390 px) står styrken og retningen under selskapsnavnet, så kjernen synes uten å dra sidelengs. Avgjørelsen 17.10 om tabellen på smal skjerm gjelder |
| HE16 | Boksen i omvisningen får fast bredde, så knappene står likt hver gang. At den bytter hjørne, endres ikke |
| HE17 | Et steg om notatene ved notatfeltet på aksjesiden og et ved notatene i Min liste, i «Vis meg rundt» og i hele omvisningen, med de samme ordene som i Innstillinger |
| HE18 | Omvisningen blar bare når det merkede ikke synes. Funnet av gruppen kl. 13:32: den blar alltid, og ved linja «Oppdatert …» hopper siden et hakk ned, og stripa forsvinner |
| HE5 | Teksten ved «Vis hjelp» sier at av også skjuler «Vis meg rundt» og omvisningen |
| HE8 | «mot 50-dagers snitt» i stedet for «mot MA50». Står «MA50» i tekst som er lagret i basen eller i KI-grunnlaget, endres bare visningen |
| HE9 | «Øvrige aksjer» med ett tall per gruppe |
| HE10 | Et navn på steg 2 som sier hvor nøkkelen limes inn |

## Det som følger med

- Hjelpetekstene, `docs/hjelp.md` og «Vis meg rundt» sier det samme som appen
  etterpå. Står virkemåten i et krav i `prd.md`, rettes kravet, med en linje i
  endringsloggen (regel 19).
- `docs/heuristisk-evaluering.md` og `docs/ux-logg.md`: en datert linje per
  funn om hva som er gjort.
- `docs/brukertest.md`, under «Brukertest 2», etter oppgave G: «Hva er
  forskjellen på «Min liste» og «Dine egne aksjer»?» (HE1).
- Avtrykkene bak bildene i `tests/test_docker.py` er satt på nytt, med en
  kommentar. Bildene i `docs/appen/` er ikke tatt på nytt, fordi instruksjonen
  sier at bildene blir i scratchpad. Spørsmål 2.

## Bygget

Bygget 17.11 av én agent i worktreen, med én commit per retting, og
kontrollert i vinduet: commitene, at ingen migrasjon og ingen bilder er med, og
to av bildene fra demoen. Hver test ble kjørt og sett feile før rettingen og
bestå etter den. HE3 og HE18 ble også kjørt mot koden før med `git stash`.

| Funn | Commit | Testen |
|---|---|---|
| HE14 | `773c78ab` | `tests/test_historikken.py::TestTilbakeTilMaaneden` |
| HE2 | `3d2599cf` | `tests/test_notater.py::TestSlettSpoerFoerst`, og testene som sletter, sender nå `bekreftet=1` |
| HE3 | `fde463cd`, `8ffd671f` | `tests/test_rettingene_9_18.py::TestTabellenPaaSmalSkjerm`, også i nettleseren ved 390 og 1280 px |
| HE16 | `46082e05` | `tests/test_rettingene_9_18.py::TestBoksenIOmvisningen` |
| HE18 | `32a69e6f` | `tests/test_rettingene_9_18.py::TestOmvisningenBlarBareNaarDetTrengs` (`OMVISNING.maaBla` med Node, og i nettleseren) |
| HE17 | `73cb94c4` | `tests/test_rettingene_9_18.py::TestStegetOmNotatene` |
| HE5 | `a1720f3a` | `tests/test_innstillinger.py::test_teksten_og_steget_sier_at_av_ogsaa_skjuler_omvisningen` |
| HE8 | `a2a28bdc` | `tests/test_signalberegning.py::test_trend_sier_snittet_med_ord`, og tre endrede tester |
| HE9 | `a88aa68d` | `tests/test_app.py::test_oevrige_uten_en_gruppe_nevner_den_ikke`, og de endrede testene for båndet |
| HE10 | `4f01c344` | `tests/test_din_egen_liste_8_22.py::test_tre_stegkort_i_rekkefoelgen_fra_utdraget` |
| Avtrykkene | `261e1e2a` | `tests/test_docker.py` |
| PRD-en | `5586b394` | FR-706 (HE8) og FR-101 (HE3), med en linje i endringsloggen |
| Dokumentene | `ddeef476` | Evalueringen, UX-loggen (U131 for HE18) og spørsmålet om HE1 i brukertest 2 |

- **HE8:** målingen lages i `_trendforklaring` når siden vises. Basen lagrer
  bare tall, og KI-grunnlaget har ingen målinger, så bare visningen er endret.
- **HE15:** `Valglager.folg` i `src/valg.py` setter stjernen i samme
  transaksjon som ønsket, fra 8.26 (gruppens svar 11.11 kl. 17:47), og
  `test_vis_meg_rundt_8_26.py::TestStjernenOgDeSomVenter::test_foelg_gir_stjerne_og_rad_i_min_liste`
  låser det. Ingen kode er endret.
- **HE17:** setningen om tenkte kjøp og salg fra Innstillinger står ikke i
  stegene, fordi testen for rådordene i omvisningen ikke tillater «kjøp» der.
- **Demoen:** sjekket på port 62971 i 1280 og 390 px, og stoppet etterpå.
  Bildene ligger i scratchpad, `ux918\ut\`.

## Gjennomgangen 17.11

Én leser med Blind Hunter, Edge Case Hunter og Verification Gap, bare med
lesing, på `acc52a83`. 18 funn: 3 på middels og 15 lave.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| ECH1 | middels | Linja under navnet på smal skjerm manglet merket «i ettertid» | Rettet, med en test som feilet mot malen før (`3e225584`) |
| VG1 | middels | Avtrykkene er regnet ut på nytt, men bildene i `docs/appen/` er ikke tatt på nytt | Middels, følger av instruksjonen (regel 25). Besvart 17.11 kl. 16:19: bildene tas på nytt i en egen liten story rett etter 9.18, før rubrikk-passet. Spørsmål 2 |
| VG2 | middels | Raden for HE15 i evalueringen og U128 var ikke rettet, og spørsmål 4 manglet svarlinja kl. 14:16 | Rettet i dokumentene |
| BH1 | lav | Knappen sa «det tenkte kjøpet» når salget også slettes | Rettet: «Slett notatet, kjøpet og salget», med test (`9b186fa8`) |
| BH2 | lav | Lenken «Til …» sto utenfor navigasjonen for måneden | Rettet (`5fa19b16`) |
| BH3 | lav | Kommentaren i `hjelp.js` talte 23 steg | Rettet |
| BH4 | lav | `vis` og `tilbake` gikk urørt inn i skjemaet på siden med spørsmålet | Rettet: bare verdier som godtas (`9b186fa8`) |
| BH5 | lav | `docs/hjelp.md` sa at stegene sier det samme som Innstillinger, og «trykker «Slett»» | Rettet |
| ECH2 | lav | `white-space: nowrap` på linja kunne gjøre navnekolonnen bred | Rettet: linja kan brytes |
| ECH3 | lav | Linja under i Min liste (sammenligningen) har ikke linja på smal skjerm | Står: sammenligningen er en detalj under raden, og styrken står i raden over |
| ECH4 | lav | `maaBla` ser ikke på `.tabellboks` eller boksen selv | Står: boksen flytter seg når den dekker (8.26), og noe som er klippet, blir merket |
| ECH5 | lav | To lange hopp i Min liste | Står: rekkefølgen er bundet av 8.27 |
| ECH6 | lav | Stegene om notatene har ingen demovariant | Står: teksten gjelder begge versjonene |
| VG3 | lav | Ingen test for «Avbryt» med en adresse utenfor appen, eller 403 uten bekreftet | Rettet: to tester (`9b186fa8`) |
| VG4 | lav | Noen mellomcommits er røde | Står: PR-en squash-flettes |
| VG5 | lav | Én av testene for HE2 er en vakt | Står: de andre feilet før rettingen |

## Spørsmål til gruppen, med forslag

Et spørsmål stopper ikke arbeidet. Spørsmål 2 er VG1 i gjennomgangen, på
middels og fra instruksjonen, så PR-en flettes ikke før gruppen har svart
(regel 25).
*Svar 2026-11-17 kl. 16:19 (gruppens svar, rådet anbefalte det):* spørsmål 1 og 2 er besvart, og ingen funn på middels
eller høy grad står åpne.

1. **HE15 er alt bygget.** Følg setter stjernen fra 11.11. Gruppen så ingen
   stjerne i den ekte versjonen. Det kan være en aksje som ble fulgt før 11.11,
   eller en som kom inn med en ferdig liste eller «De 15 mest omsatte»
   (`bruk_liste` setter ingen stjerne). *Forslag:* ingen kodeendring før testen.
   Gruppen setter stjernen selv på de aksjene den følger, i den ekte versjonen.
   Om en ferdig liste også skal sette stjerner, tas etter testen, sammen med
   spørsmålet om Fjern.
   *Svar 2026-11-17 kl. 16:19 (gruppens svar, rådet anbefalte det):* HE15 lukkes som alt bygget. Følg har satt
   stjernen siden 8.26 (11.11), og en test låser det. De tre egne aksjene ble
   fulgt før det, og gruppen setter stjernen på dem selv i den ekte versjonen.
2. **Bildene i `docs/appen/`.** Malene, stilen og hjelpetekstene er endret, så
   bildene av appen viser den gamle versjonen. Instruksjonen sier at bildene
   blir i scratchpad, så bare avtrykkene er regnet ut på nytt. *Forslag:* ta
   bildene på nytt fra demoen i en egen liten story etter brukertest 2, og
   flett 9.18 nå med bildene som de er. Det andre valget er å ta bildene på
   nytt i 9.18, før flettingen.
   *Svar 2026-11-17 kl. 16:19 (gruppens svar, rådet anbefalte det):* bildene i `docs/appen/` tas på nytt i en egen
   liten story rett etter 9.18, før rubrikk-passet, med sin egen instruksjon.
   Graden på VG1 står (regel 25).
3. **HE17 uten setningen om tenkte kjøp.** *Forslag:* godta det. Stegene sier
   hvor notatene står, og at appen aldri sier om noe var riktig.
4. **HE3 mellom 640 og 760 px.** Linja vises under 760 px, som er bruddet
   prosjektet bruker. I det spennet står styrken og retningen både i linja og i
   kolonnene. *Forslag:* godta det.

## Grenser

- Ingen ny migrasjon. Ingen API-kall. `data/` og `_privat/` røres ikke, og den
  ekte versjonen startes ikke.
- Hver retting sjekkes i demoen, i full bredde og på 390 px, på en port som
  ikke er 8000, og serveren stoppes etterpå. Bildene blir i scratchpad.
- Lokalt kjøres bare testfilene storyen rører, og `--dokumentene`. Hele settet
  kjøres i CI.

## Kontroll

- [x] Hver retting har en test som feilet mot koden før rettingen
- [x] Hjelpen, `docs/hjelp.md`, omvisningen og kravene sier det samme som appen
- [x] Datert linje per funn i evalueringen og UX-loggen, og spørsmålet om HE1 i brukertest 2
- [x] Sjekket i demoen i full bredde og på 390 px
- [x] Gjennomgangen er tatt
- [x] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt: testfilene én om gangen etter gjennomgangen, og `--dokumentene` på `6ab838d8` kl. 15:44–16:03, med 2996 bestått og 20 hoppet over. De 13 ekstra som hoppet over, er i `tests/test_dobbeltklikk.py`, fordi gruppens app var på port 8000. Første kjøring kl. 15:39 ble stoppet for lite minne og startet igjen. Etter svarene kl. 16:19: på `358aa863` kl. 16:53–17:14, med 3009 bestått og 7 hoppet over (port 8000 var ledig), etter én omstart til for lite minne
- [ ] CI er grønn i alle jobbene
