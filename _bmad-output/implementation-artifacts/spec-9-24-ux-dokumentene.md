---
title: 'Story 9.24: UX-dokumentene, DESIGN.md og EXPERIENCE.md'
type: 'docs'
created: '2026-11-22'
status: 'in-review'
route: 'dispatch'
baseline_commit: '30a247ff'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/docs/ux-logg.md'
  - '{project-root}/docs/heuristisk-evaluering.md'
  - '{project-root}/docs/brukertest.md'
---

Skrevet 22.11 etter instruksjonen kl. 14:46 i scratchpad, som føres i
`docs/ai-prompts/2026-11-22.md` på main etter flettingen. Den bygger på
gruppens svar 16.11 kl. 20:22 og 20.11 kl. 18:00. Rådet anbefalte det.
Instruksjonen 16.11 kl. 20:22 sa at det samlede UX-dokumentet skulle tas
senere (`docs/ai-prompts/2026-11-16.md`), og det er det som manglet i kursets
steg om design og UX: det finnes ingen samlet UX-spesifikasjon. Neste ledige
nummer i Epic 9 etter 9.23 er 9.24. Worktreen er `G74-lund-osen-9-24`, på
grenen `9-24-ux-dokumentene`, fra `origin/main` (`30a247ff`).

## Storyen

Som **gruppe** vil vi ha én samlet UX-spesifikasjon, med hvordan appen ser ut
(`DESIGN.md`) og hvordan den virker (`EXPERIENCE.md`), så designet og
opplevelsen kan leses ett sted, med kildene og testene som låser dem.

**Oppfyller:** steget om design og UX i kurset, etter svarene 16.11 kl. 20:22
og 20.11 kl. 18:00 · **Begrenses av:** NFR-06 (også i teksten), regel 3, 11,
16, 19 og 22, og FR-411 (demoen)

**Avhenger av:** 9.16, 9.17, 9.18, 9.21. **Én økt:** ja. Dokumentene bygger også på brukertest 1 (10.11), som ikke er en story.

## Metoden

- Skillen `bmad-ux` kjøres headless med Create (`references/headless.md`). Den
  spør ikke, og de kreative verktøyene er av. Dokumentene legges der skillen
  legger dem: `_bmad-output/planning-artifacts/ux-designs/ux-G74-lund-osen-2026-11-22/`,
  med `DESIGN.md`, `EXPERIENCE.md` og `.memlog.md`.
- Kildene er det som er bygget og bestemt: PRD-en med brukerreisene,
  `designregler.md` og designutdragene, `docs/skisser/`, `docs/ux-logg.md`,
  `docs/heuristisk-evaluering.md` og `docs/brukertest.md`, ordlista, malene og
  `stil.css` i `src/`, og demoen.
- Uttrekket fra kildene gjøres av underagenter som bare leser. Hver påstand
  får kilden med fil og linje, og testen som låser den, der den finnes.
- Demoen kan startes fra en midlertidig mappe i scratchpad, med en ny
  demobase, `OSE_DEMO=1` og en ledig port som ikke er 8000, for å lese sidene.
  Den stoppes etterpå. Den ekte versjonen startes ikke, og `data/` leses ikke.

## Det som skrives

- `DESIGN.md`: Google Labs-formen med tokenene i frontmatteren (farger,
  typografi, hjørner, avstander og komponenter) og delene i fast rekkefølge.
  Verdiene er de som står i `src/static/stil.css`.
- `EXPERIENCE.md`: grunnlaget, informasjonsarkitekturen, språket,
  komponentene, tilstandene, samspillet, tilgjengeligheten og brukerreisene
  med navnene fra PRD-en, og en del om det som ikke er godt nok ennå.
- Begge har frontmatteren fra regel 4 i tillegg til feltene skillen krever.
- Dokumentene beskriver appen slik den er, uten nye designvalg. Der kildene er
  uenige eller tause, står det som et åpent spørsmål til gruppen.
- NFR-06 gjelder også teksten: ingen råd, ingen spådommer og ingen rangering.
- Bildene i `docs/appen/` kan lenkes. Det tas ingen nye bilder.
- `README.md` får lenken i «Dokumentene», og «Mappestruktur» hvis mappa skal
  stå der (regel 19). `docs/innlevering.md` og `docs/vurderingsmatrise.md`
  nevner dokumentene der UX står. Testene som låser README-en, følger med.
- Ingen kode i `src/`, ingen migrasjon og ingen nye bilder.

## Resultatet

`bmad-ux` ble kjørt headless med Create 22.11. De kreative verktøyene var av,
og ingen bilder ble laget. Uttrekket fra kildene ble gjort av fire
underagenter som bare leste, med `fil:linje` ved hver påstand. To
underagenter skrev dokumentene fra uttrekkene (Finalize i skillen):

- `DESIGN.md` (427 linjer): frontmatter med de 41 fargetokenene fra `:root` i
  `stil.css`, typografien, hjørnene, avstandene og komponentene, og de åtte
  delene i fast rekkefølge. Fargene ble lest med en YAML-parser og sammenlignet
  med `:root`: 41 av 41 er like. Det finnes ingen mørk modus, bare tvungne
  farger (`forced-colors`).
- `EXPERIENCE.md` (464 linjer): flatene, språket, komponentene,
  tilstandene, samspillet, tilgjengeligheten, skjermbreddene, brukerreisene
  UJ-1–UJ-3 med navnene fra PRD-en, det vi har valgt bort, og det som ikke er
  godt nok ennå: de åpne HE-funnene, de åpne radene i UX-loggen, brukertest 1
  og hva brukertest 2 skal vise.
- Commitene: `73551cf6` (dokumentene), `0bb7b41f` (README-en,
  leveranselista og vurderingsmatrisen, med avtrykket for «Dokumentene» i
  `tests/test_docker.py`) og `6d049465` (rettingene etter gjennomgangen).
- **Avvik:** leveranselista (`docs/innlevering.md`) har ingen egen del for
  design og UX. Dokumentene står derfor med en datert linje i §7,
  BMAD-leveransen. I vurderingsmatrisen står de under «Design og
  brukeropplevelse», med statusen urørt.
- «Mappestruktur» i README-en er ikke endret. Den nevner `_bmad-output/`,
  og regel 19 krever ikke en egen linje for en ny undermappe der.
- Lokalt: `tests/test_docker.py` og `tests/test_readme.py`, 161 bestått, og
  `--dokumentene`. Den første kjøringen ble stoppet av lite minne ved 62 % og
  startet igjen etter rettingene (svaret 14.11 kl. 05:18).

## Gjennomgangen 22.11

Fire lesere i parallell, bare med lesing, på `0bb7b41f`:
- Blind Hunter, bare med diffen.
- Edge Case Hunter, med repoet.
- Verification Gap for hvert dokument. Den for `EXPERIENCE.md` leste også
  sidene i demoen, på port 8924 fra en midlertidig mappe i scratchpad, og
  stoppet serveren etterpå.

Sammen sjekket de om hver påstand stemmer med appen og kildene: rundt 590 i
`EXPERIENCE.md` og rundt 570 i `DESIGN.md`.

| Leser | Funn | Høy | Middels | Lav |
|---|---|---|---|---|
| Blind Hunter (BH) | 28 | 0 | 2 | 26 |
| Edge Case Hunter (ECH) | 12 | 0 | 4 | 8 |
| Verification Gap, DESIGN.md (VGD) | 21 | 1 | 6 | 14 |
| Verification Gap, EXPERIENCE.md (VGE) | 29 | 0 | 7 | 22 |

Alle funnene på middels og høy er rettet. Ingen av dem følger av et svar fra
gruppen, så regel 25 gjelder ikke.

- **Det høye funnet, VGD1:** D3 spurte om KI-bryterne skal være oransje. Det
  var avgjort 11.11 kl. 17:21 (`spec-8-26`, `epics.md`). Det er tatt ut av
  spørsmålene og beskrevet som bygget.
- **Andre spørsmål som var avgjort, er også tatt ut:**
  - valgbrikkene og omvisningens ramme (VGD2);
  - størrelsene i designreglene (VGD3);
  - grafens grensestrek (VGD7);
  - omvisningen uten skript, avgjort 11.11 kl. 16:58 (VGE6);
  - `|round(2)` i malene, valgt i 8.0 og latt stå i 8.17b (VGE7).
- **Merket «Hjelp» (BH1 og ECH4):** det er lyst gult etter
  `designregler.md:183`. Teksten sier det nå, og det står ikke som et nytt
  spørsmål.
- **Tilstandene som manglet (ECH1–ECH3), står nå i `EXPERIENCE.md`:**
  - grunnene til at KI-teksten mangler;
  - kort serie og tidligere dag;
  - «Egen» og «Utenfor målingen»;
  - justeringsdagene.
- **Testene som ikke låste det som sto (VGE2–VGE5),** er rettet til det de
  låser, eller tatt ut.

Lave funn som står, med grunnen:
- BH19: statusen `final` er det skillen setter.
- BH22: DESIGN.md har ingen h1, etter spesifikasjonen for formen.
- BH20: memloggen kan bare skrives til nederst, og ordene er skillens.
- BH27: memloggen har samme frontmatter som de andre memloggene.
- BH26 og ECH9: «Mappestruktur», som over.
- BH10 og BH16 i EXPERIENCE.md: teksten følger PRD-en.

Tabellene over hvert funn og utfall ligger i scratchpad for økta.

## Spørsmål til gruppen

Spørsmålene står nederst i hvert dokument, med kildene på begge sider og
uten forslag til svar. Et spørsmål stopper ikke flettingen, fordi dokumentene
beskriver appen slik den er.

- **`DESIGN.md`, D1–D13:**
  1. blåfargen for «Egen» (D1);
  2. den blå streken ved en egen aksje (D2);
  3. oransje i meldingene (D3);
  4. gult utenfor 3 av 3 (D4);
  5. eldre linjer i designreglene §5 (D5);
  6. hjørnene på merkene (D6);
  7. klikkflater under 44 px (D7);
  8. tekstfargene i stripa (D8);
  9. sideklassene (D9);
  10. mørk modus (D10);
  11. radene under «Øvrige aksjer» (D11);
  12. størrelsene fra utdraget 13.10 (D12);
  13. pilene (D13).
- **`EXPERIENCE.md`, E1–E8:**
  1. «lista» om Min liste (E1);
  2. «kl. 22» fast i malene (E2);
  3. 404, 400 og 403 som Flasks engelske side (E3);
  4. modellnavnet skrevet ulikt (E4);
  5. «ticker» eller «symbol» (E5);
  6. omvisningen i Innstillinger (E6);
  7. 17 eller 18 HE-funn, etter regel 12 (E7);
  8. rader i UX-loggen som ser bygget ut, men står åpne (E8).

## Kontroll

- `DESIGN.md` og `EXPERIENCE.md` finnes i mappa skillen bruker, og hver del
  viser til en kilde, et krav eller en story, og til testen der den finnes.
- Hver farge og hver verdi i frontmatteren står i `stil.css`.
- Hver påstand om appen er sjekket mot malene, CSS-en eller demoen i
  gjennomgangen.
- De åpne funnene fra den heuristiske evalueringen og brukertest 1, og hva
  brukertest 2 skal vise, står med.
- Lokalt bare testfilene storyen rører, og `--dokumentene`. Hele settet i CI.
- **Ville feilet hvis:** et dokument beskrev noe appen ikke gjør, en verdi
  ikke fantes i CSS-en, en tekst ga råd eller rangerte aksjer, eller
  README-lenken ikke virket.

## Grenser

- Bare dokumenter. Den ekte versjonen fryses til etter brukertest 2, tirsdag
  24.11 eller onsdag 25.11, så hovedkopien får bare tekst.
- Ingen API-kall utover kvotesjekken (regel 15). `data/` og `_privat/` røres
  ikke.
- Aldri to pytest samtidig, og pausene om kvelden gjelder når kveldsjobben er
  Ready. PR-en flettes ikke i pausene.
