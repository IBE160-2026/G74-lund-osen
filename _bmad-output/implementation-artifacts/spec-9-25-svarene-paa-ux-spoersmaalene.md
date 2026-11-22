---
title: 'Story 9.25: svarene på E1, E2, E4, E5 og E6 i UX-dokumentene'
type: 'code'
created: '2026-11-22'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '5706ead5'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-24-ux-dokumentene.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G74-lund-osen-2026-11-22/EXPERIENCE.md'
---

Skrevet 22.11 etter instruksjonen om svarene på de åpne spørsmålene i
UX-dokumentene (limt inn kl. 18:33 i `docs/ai-prompts/2026-11-22.md`) og
gruppens svar 22.11 kl. 18:23. For E1, E2, E4, E5 og E6 ville rådet vente til
etter brukertest 2, men gruppen valgte å ta dem nå. Neste ledige nummer i Epic 9
etter 9.24 er 9.25. Worktreen er `G74-lund-osen-9-25`, på grenen
`9-25-svarene-paa-ux-spoersmaalene`, fra `origin/main` (`5706ead5`). Svarene på
D1–D13, E3, E7 og E8 og den nye datoen for brukertest 2 står på main, ikke på
grenen (steg 1 i instruksjonen, `115505cd`–`5706ead5`).

## Storyen

Som **bruker i brukertest 2** vil jeg at appen bruker de samme ordene og det
samme klokkeslettet overalt, og at omvisningen forklarer alle valgene i
Innstillinger, så jeg ikke møter to navn på det samme.

**Oppfyller:** E1, E2, E4, E5 og E6 i `EXPERIENCE.md` (svaret 22.11 kl. 18:23),
FR-602 · **Begrenses av:** regel 3, 16, 19, 20, 21 og 22, NFR-06; ingen ny
migrasjon

**Avhenger av:** 9.24. **Én økt:** ja.

## Det som gjøres

1. **E1, «Min liste» i stedet for «lista».** Der Min liste sier «lista» om
   aksjene med stjerne, står «Min liste», som ordlista skiller (`prd.md` §1):
   innledningen og teksten for en tom Min liste i `src/templates/index.html`,
   og teksten for «Min liste» på oversikten uten merkede aksjer. «Lista» om
   aksjene appen henter, står som før.
2. **E2, klokkeslettet fra `TIDSGRENSE`.** «kl. 22» i malene (`_egne.html`,
   `folg.html`, `index.html` og `ferdig_liste.html`) kommer fra
   `boersdag.TIDSGRENSE`, regnet som i stripa (`grensen_som_tekst` i
   `src/markedsoversikt.py`). Testen ser også på malene.
3. **E4, modellnavnet.** Oversikten skriver modellnavnet i samme form som
   aksjesiden, «Modell: {modell}, {tjeneste}» (FR-602).
4. **E5, «ticker».** Steget i omvisningen ved søkefeltet i «Følg en aksje» sier
   «ticker», og ordlista i `prd.md` får ordet, med en linje i
   `prd-endringslogg.md` (regel 19).
5. **E6, steget for «Notater».** Omvisningen i Innstillinger får et steg for
   bryteren «Notater», som stegene for «Hjelp» og «KI-tekst».
6. Hver retting får en test som feiler før rettingen. Endrer et bilde i
   `docs/appen/` seg, tas det på nytt i demoen, og avtrykkene og bildegrenen
   følger med.

## Grenser

- Ingen API-kall utover kvotesjekken. `data/` og `_privat/` røres ikke, og den
  ekte versjonen startes ikke.
- Bilder bare av demoen, på en ledig port, aldri 8000, og uten ekte kurser.
- Ingen ny migrasjon.
- Aldri to pytest samtidig. Lokalt kjøres bare testfilene storyen rører, og
  `--dokumentene`. Hele settet kjøres i CI.
- Pausene om kvelden gjelder: ingen pytest kl. 22:15–23:50, ingen git kl.
  22:10–22:20, 22:43–22:48, 23:13–23:18 og 23:43–23:48, og ingen fletting kl.
  22:10–23:58.

## Kontroll

- [ ] E1: «Min liste» der Min liste sa «lista» om aksjene med stjerne
- [ ] E2: «kl. 22» i malene kommer fra `TIDSGRENSE`, og testen ser på malene
- [ ] E4: «Modell: {modell}, {tjeneste}» på oversikten
- [ ] E5: «ticker» i steget ved søkefeltet, og i ordlista med en linje i endringsloggen
- [ ] E6: et steg for «Notater» i omvisningen i Innstillinger
- [ ] Hver retting har en test som feilet før rettingen
- [ ] Bildene som endrer seg, avtrykkene og bildegrenen følger med
- [ ] Gjennomgangen er tatt, også mot demoen
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
