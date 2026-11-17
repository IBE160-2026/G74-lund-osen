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
- Ingen bilder i repoet. Svaret ba ikke om dem, og
  `TestBildeneIDocs::test_bare_de_tre_bildene_i_docs_bilder` og
  `test_mappa_har_bare_bilder_og_video_av_appen` i `tests/test_docker.py` låser
  `docs/bilder/` og `docs/appen/`. De 33 bildene av demoen ligger bare i
  scratchpad, og dokumentet sier det.
- Ingen kode og ingen maler endres. Den eneste endringen i testene er avtrykket
  for «Dokumentene» i `AVTRYKK_I_PILENE` i `tests/test_docker.py`, med en
  kommentar, som README-lenken krever. Testen sier selv at avtrykket settes på
  nytt i samme commit når innholdet endres, slik 9.11, 9.12 og 9.14 gjorde.

## Resultatet

Én evaluerer (KI-assistenten i økten) gikk gjennom demoen 17.11, på port 62957 fra en
midlertidig mappe i scratchpad, og stoppet serveren og nettleseren den startet.
Vinduet slo opp funnene mot malene før de ble skrevet inn: overskriftene i
`_egne.html` (HE1), slettingen i `_notat.html` og `app.py` (HE2), bildet av
tabellen på 390 px (HE3), `_rundtur.html`, `innstillinger.html` og
`hjelpetekster.py` (HE5), `signalberegning.py` (HE8), `index.html` (HE9),
`_egne.html` (HE10) og at ingen mal lenker til `docs/hjelp.md` (HE11).
HE6, HE7, HE12 og HE13 er sjekket mot malene i gjennomgangen, og HE4 bygger
bare på bildene.
Radene i UX-loggen som dokumentet viser til, er også slått opp (U23, U105, og
radene om smal skjerm og 404-siden).

13 funn: 3 på middels (HE1–HE3) og 10 lave (HE4–HE13), og ingen høye. To ting
som alt står i UX-loggen, er nevnt, men ikke ført som nye. Funnene står i
`docs/heuristisk-evaluering.md` og som U114–U126 i `docs/ux-logg.md`.

Funnene i evalueringen er innholdet i storyen, forslag som gruppen svarer på.
De er ikke funn i gjennomgangen av denne PR-en, og de følger ikke av et svar,
så regel 25 gjelder gjennomgangen under.

## Gjennomgangen 17.11

Én leser med Blind Hunter, Edge Case Hunter og Verification Gap, bare med
lesing, på `d5ce16b3`. 18 funn: 2 på middels og 16 lave. Ingen av dem følger
av et svar.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| ECH1 | middels | HE2 og H3 sa at Fjern alltid spør først, men `/fjern` spør bare når aksjen har et åpent tenkt kjøp, og ellers kan det angres | Rettet, og HE2 sier at et tenkt kjøp også slettes |
| VG1 | middels | Grunnen til at bildene ikke ligger i repoet var for sterk | Rettet: svaret ba ikke om dem, og `docs/bilder/` og `docs/appen/` er låst av testene |
| BH1 | lav | Hvem som evaluerte, sto ulikt | Rettet: «én evaluerer (KI-assistenten i økten)» overalt |
| BH2 | lav | Grunnen i spørsmål 1 passet HE1, ikke HE2 og HE3 | Rettet: en grunn for hver |
| BH3 | lav | Uklar norsk i innledningen, HE5, HE9 og spørsmål 3 | Rettet |
| BH4 | lav | Lenketeksten i README-en sier ikke hvem heuristikkene er fra | Står: dokumentet sier det, og avtrykket for «Dokumentene» endres ikke for det |
| BH5 | lav | Metoden og spesifikasjonen sa ulikt om hvilke funn som er slått opp | Rettet: HE4 bygger bare på bildene, og de andre er slått opp |
| ECH2 | lav | HE3 er nær avgjørelsen 17.10 om tabellen på smal skjerm | Rettet: HE3 og U116 viser til den |
| ECH3 | lav | HE9 sa ikke at ordlyden er gruppens fra 14.10 | Rettet |
| ECH4 | lav | HE12 var sterkere enn koden, og punktet 18.10 manglet | Rettet: aksjesiden åpner på en periode, H4 er tatt bort, og 18.10 står |
| ECH5 | lav | H1 beskrev en dag som ikke er børsdag | Rettet: en tidligere dag |
| ECH6 | lav | H8 sa at gult bare brukes for 3 av 3 | Rettet: ved en aksje |
| ECH7 | lav | H4 sa «på alle sidene» | Rettet: på sidene som har dem |
| ECH8 | lav | HE11 sa at bare malen nevner `docs/hjelp.md` | Rettet |
| ECH9 | lav | HE10 var for sterk, fordi teksten sier hvor nøkkelen limes inn | Rettet: det er tittelen som villeder |
| VG2 | lav | `status: aktiv` for et dokument som venter på svar | Står: gruppen svarer på forslagene i dokumentet, så det er levende til da |
| VG3 | lav | `--dokumentene`, CI og radene i kvalitetssikringen | Tas før flettingen og i føringen |
| VG4 | lav | Konflikt i `epics.md` og `sprint-status.yaml` med 9.16 | Tas når main flettes inn: 9.16 foran 9.17 |
| VG5 | lav | Heuristikkene sto uten kilde | Rettet: kilden er nevnt, men ikke sitert, fordi den ikke er lest i økta (regel 11) |

## Spørsmål til gruppen

Spørsmålene står også nederst i `docs/heuristisk-evaluering.md`. Et spørsmål
stopper ikke arbeidet.

1. **HE1–HE3 (middels).** Skal de rettes før brukertest 2? *Forslag:* HE2 og
   HE3 før testen, og HE1 som et spørsmål i brukertest 2 først. Grunnene står
   i dokumentet.
2. **HE4–HE13 (lave).** *Forslag:* HE5, HE8, HE9 og HE10 er tekst og kan tas i
   én liten story. Resten venter til etter brukertest 2.
3. **Én evaluerer.** *Forslag:* gruppen går selv gjennom tabellen før
   brukertest 2 og fører funn den er uenig i, som en datert linje.

## Grenser

- Bare demoen, bare oppdiktede selskaper og tall. Ingen kurser fra den ekte
  basen (regel 16).
- Dokumentet sier at evalueringen er laget 17.11, etter at appen ble bygget.

## Kontroll

- [x] Alle de sju delene er gått gjennom mot de ti heuristikkene
- [x] Hvert funn har heuristikken, siden, grad, kilden og et forslag
- [x] Radene i UX-loggen og lenken i README-en
- [x] Gjennomgangen er tatt
- [ ] `--dokumentene` er grønn lokalt
- [ ] CI er grønn i alle jobbene
