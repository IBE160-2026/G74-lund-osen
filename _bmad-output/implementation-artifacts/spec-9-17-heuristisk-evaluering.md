---
title: 'Story 9.17: en heuristisk evaluering av demoen'
type: 'docs'
created: '2026-11-17'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'ba866204'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/docs/ux-logg.md'
  - '{project-root}/docs/brukertest.md'
---

Skrevet 17.11, etter at appen ble bygget, i vinduet som bygde 9.15, etter steg 2
i instruksjonen etter gruppens svar 16.11 kl. 20:22 (design og UX før brukertest
2), ført i `docs/ai-prompts/2026-11-16.md`. Rådet anbefalte det. Neste ledige
nummer i Epic 9 etter 9.16 er 9.17. Worktreen er `G74-lund-osen-9-17`, på grenen
`9-17-heuristisk-evaluering`, fra `origin/main` (`ba866204`).

## Storyen

Som **gruppe** vil vi ha en heuristisk evaluering av demoen før brukertest 2, så
vi vet hvilke brukbarhetsproblemer som finnes, og kan svare på små rettinger før
testen.

**Oppfyller:** steg 2 i instruksjonen etter svaret 16.11 kl. 20:22 ·
**Begrenses av:** regel 3, 16, 19 og 22, og FR-411 (demoen)

**Avhenger av:** 8.2, 8.9, 8.21, 8.27, 2.18. **Én økt:** ja.

## Svaret

*Svar 2026-11-16 kl. 20:22 (gruppens svar, rådet anbefalte det):* demoen gås
gjennom mot de ti vanlige heuristikkene (Nielsen): oversikten, aksjesiden, Min
liste, Innstillinger, «Vis meg rundt», hjelpen og visningen på 390 px. Hvert
funn får heuristikken, siden, grad (lav, middels eller høy) og et forslag.
Resultatet står i et nytt dokument i `docs/`, med rader i `docs/ux-logg.md` og
en lenke fra README-en. Ingen kode endres. Små, klare rettinger blir forslag som
gruppen svarer på. Bilder tas bare av demoen, og ingen nye bilder kommer i
README-en.

## Metoden

- Demoen kjøres fra en midlertidig mappe i scratchpad, med en ny demobase og
  `OSE_DEMO=1`, på en ledig port som ikke er 8000, og stoppes etterpå. Den ekte
  versjonen startes ikke, og `data/` leses ikke.
- Én evaluerer (KI-assistenten i økten) går gjennom sidene i bredde og på 390 px,
  med bilder fra en nettleser uten vindu og HTML-en fra demoserveren, og
  slår opp i malene.
- Hvert funn sjekkes mot `docs/ux-logg.md`, så et funn som alt står der, får
  nummeret sitt og ikke føres som nytt.
- Én evaluerer er færre enn de tre til fem metoden anbefaler. Det står i
  dokumentet, og brukertest 2 er den andre kilden.

## Det som skrives

- `docs/heuristisk-evaluering.md`: metoden, funnene i en tabell (heuristikken,
  siden, grad, det som ble sett, kilden og forslaget), det som virker, og
  spørsmålene til gruppen. Samme frontmatter som de andre dokumentene i
  `docs/` (regel 4).
- `docs/ux-logg.md`: en ny del med én rad per nytt funn, med neste ledige
  U-nummer.
- `README.md`: lenken i «Dokumentene» (regel 19).
- Bilder av demoen kan legges ved dokumentet i `docs/bilder/`, men ikke i
  README-en.
- Ingen kode, ingen maler og ingen tester endres.

## Grenser

- Bare demoen, bare oppdiktede selskaper og tall. Ingen kurser fra den ekte
  basen (regel 16).
- Dokumentet sier at evalueringen er laget 17.11, etter at appen ble bygget.

## Kontroll

- [ ] Alle de sju delene er gått gjennom mot de ti heuristikkene
- [ ] Hvert funn har heuristikken, siden, grad, kilden og et forslag
- [ ] Radene i UX-loggen og lenken i README-en
- [ ] Gjennomgangen er tatt
- [ ] `--dokumentene` er grønn lokalt
- [ ] CI er grønn i alle jobbene
