---
title: 'Story 9.25: svarene på E1, E2, E4, E5 og E6 i UX-dokumentene'
type: 'code'
created: '2026-11-22'
status: 'done'
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

## Resultatet

| Del | Commit | Testen |
|---|---|---|
| E1: «Min liste» i innledningen, i teksten for en tom Min liste og i teksten for «Min liste» på oversikten | `ffe4aa09` | `TestE1MinListe` |
| E2: `{{ tidsgrense() }}` i stedet for «kl. 22» i fire maler, med `grensen_som_tekst` som global i `app.py` | `3cb0ffb0` | `TestE2Klokkeslettet` |
| E4: «Modell: {modell}, {tjeneste}» på oversikten, fra `_modellnavnet` i `ki_visning.py`, og hjelpen rettet | `82440ecf` | `TestE4Modellnavnet` |
| E5: «tickeren» i steget ved søkefeltet, «Ticker» i ordlista og en linje i endringsloggen | `776dad70`, `369f7022` | `TestE5Ticker` |
| E6: steget `notater-valget` i omvisningen i Innstillinger | `87387c96`, `8120b5f1` | `TestE6Notater` |
| Bildene og avtrykkene | `8ce60c2e`, `8120b5f1` | `tests/test_docker.py` |
| Bildegrenen `pr-9-25-bilder`, pushet | `1dbe7110`, `efcce60d` | Bildene før og etter, med `LESMEG.md` |

Testfila ble kjørt mot koden på `9ef4c60b`, før rettingene: 13 av de 14
testene feilet, og besto etter rettingene. Den 14.,
`test_grensen_i_hele_timer_som_foer`, låser at sidene sier det samme som før
med grensen kl. 22, og besto før og etter. De to testene som kom etter
gjennomgangen (BH2), er ikke kjørt mot koden før rettingene. Tre eldre tester låste den gamle
teksten og følger den nye: `tests/test_min_liste.py` («lista») og
`tests/test_ki_dagen.py` og `tests/test_de_lave_funnene_9_10.py`
(modellnavnet). `tests/test_prd_9_11.py` tillater 13 ord i ordlista.

**Ordlista har 13 ord.** `tests/test_prd_9_11.py` tillot 8–12, etter svaret
18.11 kl. 11:49 på spørsmål 3 i 9.20 («behold», 12 ord). Faglærer foreslo
8–10. Instruksjonen sier at ordlista får «ticker», så grensen er 13, med
grunnen i testen. Se spørsmål 1.

**Bildene.** Alle de 20 bildene i `docs/appen/` ble tatt i demoen på port 8925
og 8926, med en ny demobase hver gang, tre ganger to (kl. 19:14–19:21,
19:34–19:35 og 19:40–19:42, filtidene), og var like byte for byte hver gang.
`min-liste-demo.png` (E1) og `mobil/oversikten-390-demo.png` (E4) er nye. De
andre 18 er uendret: E2 endrer ingen tekst så lenge grensen er kl. 22, og
stegene for «Følg en aksje» og Innstillinger står ikke på noe bilde.

## Gjennomgangen 22.11

To lesere, på `5706ead5..8ce60c2e`: Blind Hunter og Edge Case Hunter, og
Acceptance Auditor og Verification Gap. Den andre leste også sidene i demoen på
8925 og 8926 og så på bildene. Ingen kjørte pytest. 13 funn: 1 middels og 12
lave.

| Id | Grad | Funnet | Gjort |
|---|---|---|---|
| BH1 | middels | Raden «Ticker» sa at bare koden sier «symbol», men kravene om hentingen og lagringen gjør det også, og FR-103 bruker «symbol» om pilen | Rettet: raden sier det, som raden for «Bransje» (`369f7022`) |
| BH2 | lav | E6-testen sjekket ikke teksten eller at steget står med notatene av | Rettet (`863e0e2e`) |
| BH3 | lav | Den statiske testen fant bare «kl. 22» | Rettet: den finner også «kl 22» og «klokka 22» (`863e0e2e`) |
| VG1 | lav | Docstringen for `_modellnavnet` lovet mer enn testen sjekker | Rettet (`863e0e2e`) |
| AA1 | lav | `LESMEG.md` sa at ingen bilder viser omvisningen | Rettet på bildegrenen (`efcce60d`) |
| AA2 | lav | Steget for «Notater» nevnte ikke knappen «Mine notater» | Rettet, uten «kjøp», som er et rådsord i omvisningen (`8120b5f1`) |
| AA3 | lav | Regel 20 manglet under «Begrenses av» i `epics.md` | Rettet (`5c69a525`) |
| VG2 | lav | Statusene i `_egne.html` og meldingen i `index.html` vises ikke i demoen | Står: den statiske testen dekker malene, og eldre tester viser dem med grensen kl. 22 |
| ECH4 | lav | Hjelpeteksten om neste henting regnes når modulen lastes, ikke ved hver visning | Står: `TIDSGRENSE` er en konstant, og E2 gjaldt malene |
| ECH1 | lav | `docs/hjelp.md` sier «symbolet» om ticker i avsnittet om børsometeret | Står: spørsmål 2 |
| ECH2, AA4 | lav | `docs/hjelp.md` sier «lista» om Min liste i ett svar | Står: spørsmål 2 |
| ECH3 | lav | «i kveld» står fast i statusene, mens stripa regner dagen | Står, fantes fra før: spørsmål 3 |

## Spørsmål til gruppen

1. **Ordlista har 13 ord.** Faglærer foreslo 8–10, og svaret 18.11 kl. 11:49
   holdt 12. *Forslag:* behold «Ticker», fordi E5 gjelder ordet brukeren ser.
2. **`docs/hjelp.md`.** Hjelpen sier «symbolet» om ticker på rutene i
   børsometeret og «lista» om Min liste i ett svar. Svarene på E1 og E5 gjaldt
   siden, omvisningen og ordlista. *Forslag:* rett hjelpen på samme måte, fordi
   den er levende og leses i brukertest 2.
3. **«i kveld».** Statusene i «Dine egne aksjer» og «Følg en aksje» sier
   «i kveld etter kl. 22» også etter kveldsjobben, mens stripa regner dagen.
   *Forslag:* vent til etter brukertest 2.

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

- [x] E1: «Min liste» der Min liste sa «lista» om aksjene med stjerne
- [x] E2: «kl. 22» i malene kommer fra `TIDSGRENSE`, og testen ser på malene
- [x] E4: «Modell: {modell}, {tjeneste}» på oversikten
- [x] E5: «ticker» i steget ved søkefeltet, og i ordlista med en linje i endringsloggen
- [x] E6: et steg for «Notater» i omvisningen i Innstillinger
- [x] Hver retting har en test som feilet før rettingen
- [x] Bildene som endrer seg, avtrykkene og bildegrenen følger med
- [x] Gjennomgangen er tatt, også mot demoen
- [x] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt: 922 bestått (kl. 19:59–20:03, etter en ny start etter lite minne) og 3112 bestått og 7 hoppet over (kl. 20:04–20:25), på `5b70659a`
- [x] CI er grønn i alle jobbene (run 45060734980)

## Flettet 22.11

PR #174 er squash-flettet i `c0192467` kl. 20:56, låst til head-en `8803a598`, uten nytt ja. CI var grønn i alle fire jobbene (run 45060734980), med 6140 bestått og 99 hoppet over i jobben `pytest`. Ingen funn på middels eller høy grad sto åpne.
