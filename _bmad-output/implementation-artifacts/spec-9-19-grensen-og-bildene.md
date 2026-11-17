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

## Grenser

- Ingen API-kall, ingen ny migrasjon, og `data/` og `_privat/` røres ikke. Den
  ekte versjonen startes ikke. Ingen ekte kurser i bildene.
- Lokalt kjøres bare testfilene storyen rører, og `--dokumentene`, og utfallet
  sjekkes før hver push. Hele settet kjøres i CI.

## Kontroll

- [ ] Styrken og retningen står bare én gang i alle bredder, med en test
- [ ] Bildene er tatt på nytt fra grenen i demoen, og de som er like, er ikke byttet
- [ ] Avtrykkene er regnet ut fra de nye bildene, og bildegrenen har bildene før og etter
- [ ] Svarene og VG1 i spesifikasjonen for 9.18, og linja i UX-loggen
- [ ] Gjennomgangen er tatt
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
