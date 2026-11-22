---
title: 'Story 9.24: UX-dokumentene, DESIGN.md og EXPERIENCE.md'
type: 'docs'
created: '2026-11-22'
status: 'in-progress'
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

**Avhenger av:** 9.16, 9.17, 9.18, 9.21 og brukertest 1. **Én økt:** ja.

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
