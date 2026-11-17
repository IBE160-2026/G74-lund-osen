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
| HE15 | Følg setter også stjernen, så aksjen står i tabellen i Min liste. Stjernen kan tas bort etterpå. Fjern endres ikke |
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
- Avtrykkene bak bildene i `tests/test_docker.py` settes på nytt der malene
  endres. Bildene i `docs/appen/` tas ikke på nytt i denne storyen uten at
  gruppen ber om det; avtrykkene sier hvilke kildefiler som er endret.

## Grenser

- Ingen ny migrasjon. Ingen API-kall. `data/` og `_privat/` røres ikke, og den
  ekte versjonen startes ikke.
- Hver retting sjekkes i demoen, i full bredde og på 390 px, på en port som
  ikke er 8000, og serveren stoppes etterpå. Bildene blir i scratchpad.
- Lokalt kjøres bare testfilene storyen rører, og `--dokumentene`. Hele settet
  kjøres i CI.

## Kontroll

- [ ] Hver retting har en test som feilet mot koden før rettingen
- [ ] Hjelpen, `docs/hjelp.md`, omvisningen og kravene sier det samme som appen
- [ ] Datert linje per funn i evalueringen og UX-loggen, og spørsmålet om HE1 i brukertest 2
- [ ] Sjekket i demoen i full bredde og på 390 px
- [ ] Gjennomgangen er tatt
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
