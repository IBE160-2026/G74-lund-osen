---
title: 'Story 9.19: grensen på 640–760 px og bildene av appen'
type: 'feature'
created: '2026-11-17'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'e00f6502'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-18-rettingene-foer-brukertest-2.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3k-bildene-av-appen-i-readme.md'
---

Skrevet 17.11 i vinduet som bygde 9.18, etter instruksjonen om grensen og
bildene (limt inn kl. 18:25 i `docs/ai-prompts/2026-11-17.md`) og gruppens svar
17.11 kl. 16:19 og 18:23. Neste ledige nummer i Epic 9 etter 9.18 er 9.19.
Worktreen er `G74-lund-osen-9-19`, på grenen `9-19-grensen-og-bildene`, fra
`origin/main` (`e00f6502`).

## Storyen

Som **gruppe** vil vi at styrken og retningen står bare én gang i tabellen i
alle bredder, og at bildene av appen viser rettingene fra 9.18, så README-en og
brukertest 2 viser appen slik den er.

**Oppfyller:** spørsmål 4 og VG1 i 9.18 · **Begrenses av:** regel 3, 16, 19,
21, 22 og 23, og ingen ny migrasjon før testen

**Avhenger av:** 9.18, 3.3k. **Én økt:** ja.

## Svarene

*Svar 2026-11-17 kl. 16:19 (gruppens svar, VG1 i 9.18):* bildene i
`docs/appen/` tas på nytt i en egen liten story rett etter 9.18, før
rubrikk-passet. *Svar 2026-11-17 kl. 18:23 (gruppens svar):* spørsmål 3 i 9.18
godtas, og stegene om notatene står uten setningen om tenkte kjøp, med testen
for rådord uendret (rådet anbefalte det). Spørsmål 4 rettes i denne storyen,
etter gruppens valg.

*Svar 2026-11-17 kl. 18:26 (gruppens svar, rådet anbefalte det, beskjeden kl.
18:27):* bildene fra mobil vises ikke lenger i README-en. Pila «Bilder av appen
på mobil (demoen)», som ble lagt til i 3.3k (spørsmål 2 i
`spec-3-3k-bildene-av-appen-i-readme.md`), er tatt ut. I stedet står én linje:
bildene fra smal skjerm ligger i `docs/appen/mobil/`, og mobil kanskje kommer
senere, fordi appen i v1 bare svarer på denne maskinen. Mappa står, og bildene
der tas på nytt som før. Testene sjekker linja og mappa, ikke pila.

## Det som gjøres

1. **Grensen.** Mellom 640 og 760 px skal styrken og retningen stå bare én
   gang, som på PC og på 390 px. Linja under navnet vises bare når kolonnene
   ikke får plass, med en test i nettleseren for bredder på begge sider av
   grensen.
2. **Bildene.** Bildene i `docs/appen/` og `docs/appen/mobil/` tas på nytt, slik
   3.3k gjorde: fra grenen og i demoen, med demobasen i en midlertidig mappe og
   serveren på en ledig port, aldri 8000. Et bilde som er likt byte for byte,
   byttes ikke. Avtrykkene i testene regnes ut fra de nye bildene. Bildene før
   og etter legges på en egen bildegren, som før.
3. Rettingene fra 9.18 synes i bildene der de står: tabellen på 390 px,
   omvisningen, og der bildene viser dem, spørsmålet før sletting og lenken
   tilbake i «Signalet dag for dag». Et nytt bilde i README-en blir et
   spørsmål med forslag.
4. Svarene kl. 18:23 står under spørsmål 3 og 4 i spesifikasjonen for 9.18, og
   VG1 der får en datert linje om at bildene er tatt. UX-loggen får en linje om
   grensen.

## Bygget

Bygget 17.11 av én agent i worktreen, og kontrollert i vinduet: commitene, at
ingen demoserver eller nettleser står igjen, og at ingen migrasjon er med.

| Del | Commit | Testen eller kontrollen |
|---|---|---|
| Grensen, første trinn | `c06cbc39` | `tests/test_rettingene_9_18.py::TestBareEnGangIAlleBredder` |
| README-en uten pila for mobil | `20a39b47` | `test_mobillinja_lenker_til_mappa_med_bildene_ved_390_px` og de andre README-testene i `tests/test_docker.py` |
| Bildene og avtrykkene | `10a96e50` | `tests/test_docker.py` |
| To trinn i linja | `960ca037` | `TestBareEnGangIAlleBredder::test_styrken_og_retningen_en_gang_hver`, som feilet for styrken ved 610, 640, 700 og 739 px før rettingen |
| Avtrykkene etter de to trinnene | `5f83c0d5` | `tests/test_docker.py` |
| Bildegrenen | `5e60ee19` på `pr-9-19-bilder` | Bildene før og etter, med `LESMEG.md` |

- **Grensen:** målt i Edge med demodataene er tabellen 709 px bred, og boksen
  34 px smalere enn vinduet. Kolonnen for styrken får plass fra 607 px, og
  kolonnen for retningen fra 743 px. Linja viser «N av 3 · retning» under
  607 px, bare retningen fra 607 til 743 px, og ingenting fra 743 px. Merket
  «i ettertid» og grunnen for en rad uten signal hører til styrken.
- **Bildene:** alle 18 er tatt to ganger med ny demobase, og kjøringene var
  like byte for byte. Seks er byttet: `aksjesiden-brfe-demo.png` (HE8),
  `din-egen-liste-demo.png` (HE10), `innstillinger-demo.png` (HE5),
  `min-liste-demo.png` (HE9), `vis-meg-rundt-demo.png` (HE16 og HE18) og
  `mobil/oversikten-390-demo.png` (HE3, tatt i full høyde, 4773 px). Tolv var
  like og står. Etter de to trinnene ble alle tatt på nytt igjen, og alle var
  like med det som var committet.
- Spørsmålet før sletting (HE2) og lenken «Til <måned>» (HE14) står ikke i noen
  av bildene.

## Spørsmål til gruppen, med forslag

Et spørsmål stopper ikke arbeidet.

1. **Nye bilder i README-en.** HE2 og HE14 står ikke i noen av bildene.
   *Forslag:* ingen nye bilder nå. Etter brukertest 2 kan bildet av spørsmålet
   før sletting og bildet av «Signalet dag for dag» med lenken tilbake legges i
   pila «Bilder av appen (demoen)».
2. **Bruddene er målt med demodataene.** Tabellen er like bred med eller uten
   linja, men andre tickere og bransjer i den ekte versjonen kan gjøre den noen
   px bredere eller smalere. Da kan et smalt spenn vise styrken eller retningen
   to ganger eller ingen ganger. *Forslag:* godta det for v1, og se på det i den
   ekte versjonen på telefonbredde i brukertest 2.

## Grenser

- Ingen API-kall, ingen ny migrasjon, og `data/` og `_privat/` røres ikke. Den
  ekte versjonen startes ikke. Ingen ekte kurser i bildene.
- Lokalt kjøres bare testfilene storyen rører, og `--dokumentene`, og utfallet
  sjekkes før hver push. Hele settet kjøres i CI.

## Kontroll

- [x] Styrken og retningen står bare én gang i alle bredder, med en test
- [x] Bildene er tatt på nytt fra grenen i demoen, og de som er like, er ikke byttet
- [x] Avtrykkene er regnet ut fra de nye bildene, og bildegrenen har bildene før og etter
- [x] Svarene og VG1 i spesifikasjonen for 9.18, og linja i UX-loggen
- [ ] Gjennomgangen er tatt
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
