---
title: 'Story 9.26: skjermene i OSE Signal, ordnet etter epic og story'
type: 'docs'
created: '2026-11-22'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'ea6362c7'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-25-svarene-paa-ux-spoersmaalene.md'
---

Skrevet 22.11 etter instruksjonen om skjermene i OSE Signal (limt inn kl. 19:06
i `docs/ai-prompts/2026-11-22.md`, tatt kl. 21:18 etter at 9.25 var ført og
pushet) og gruppens svar 22.11 kl. 19:05. Rådet anbefalte siden. Den er laget
etter mønster av faglærers side for ØL-spillet, slik instruksjonen beskriver
den: ett til to bilder per story ved 1280 px bredde, med en kort tekst under
fra kontrollen. Faglærers side ligger ikke i repoet. Neste ledige nummer i
Epic 9 etter 9.25 er 9.26. Worktreen er `G74-lund-osen-9-26`, på grenen
`9-26-skjermene`, fra `origin/main` (`ea6362c7`), der 9.25 er flettet, så
bildene viser de nye tekstene.

## Storyen

Som **faglærer eller sensor** vil jeg se skjermene i OSE Signal ordnet etter
epic og story, med det kontrollen sjekket under hvert bilde, så jeg kan se hva
hver story ga uten å starte appen.

**Oppfyller:** gruppens svar 22.11 kl. 19:05 · **Begrenses av:** regel 3, 16,
19, 20 og 22, NFR-06; ingen kode i `src/` og ingen migrasjon

**Avhenger av:** 9.25. **Én økt:** ja.

## Det som gjøres

1. **Siden** er `docs/skjermene.md`, med bildene i `docs/skjermene/`.
   - Ordnet etter epic, med storyene i rekkefølgen i `epics.md`.
   - Ett til to bilder per story som har en egen skjerm, 1280 px brede, av
     hele siden eller av delen storyen ga.
   - Storyer uten skjerm, som hentingen, står med én linje om hvorfor.
   - Under hvert bilde står en kort tekst fra kontrollen: hva bildet viser, og
     hva som ble sjekket, med lenke til spesifikasjonen, eller til storyen i
     `epics.md` når den ikke har en egen spesifikasjon.
   - Øverst står hvor mange epics, storyer og bilder siden har, og at alt er
     fra demoen med oppdiktede selskaper.
2. **Bildene** tas av demoen på grenen, på en ledig port, aldri 8000, med
   skriptet fra 9.19–9.25. De komprimeres, og hele mappa holdes under 15 MB.
   Går ikke det, blir det færre bilder, og det står her.
3. **README-en** lenker til siden under «Dokumentene», og vurderingsmatrisen
   nevner den under «Design og brukeropplevelse». Testene som låser README-en,
   følger med.
4. **Testene** for siden og bildene: se «Avtrykk og tester» under.

## Avtrykk og tester

Bildene i `docs/appen/` har et avtrykk av filene bak hvert bilde, så en test
feiler når siden bak bildet endres (`tests/test_docker.py`). Det passer for de
20 bildene README-en viser, som skal vise demoen slik den er. Skjermene her er
et bilde av appen på én commit, med datoen og commiten øverst, slik faglærers
side viser spillet ved innleveringen. Med et avtrykk per bilde ville nesten
hver endring i en mal gjøre mange bilder røde, og siden er ikke ment å følge
hver endring. Derfor får bildene ikke avtrykk. Testene sjekker i stedet:

- at hver lenke til et bilde peker på en fil i `docs/skjermene/`, og at hver fil
  der har en lenke;
- at hvert bilde er en PNG, 1280 px bredt og uten tekstbiter (metadata);
- at mappa er under 15 MB;
- at tallene øverst stemmer med overskriftene og bildene på siden;
- at hver tekst lenker til en spesifikasjon eller en story som finnes.

## Grenser

- Bilder bare av demoen, på en ledig port, aldri 8000, og uten ekte kurser.
  Ingen kode i `src/` og ingen migrasjon.
- Ingen API-kall utover kvotesjekken. `data/` og `_privat/` røres ikke, og den
  ekte versjonen startes ikke.
- Aldri to pytest samtidig. Lokalt kjøres bare testfilene storyen rører, og
  `--dokumentene`. Hele settet kjøres i CI.
- Pausene om kvelden gjelder: ingen pytest kl. 22:15–23:50, ingen git kl.
  22:10–22:20, 22:43–22:48, 23:13–23:18 og 23:43–23:48, og ingen fletting kl.
  22:10–23:58.

## Kontroll

- [ ] `docs/skjermene.md` ordnet etter epic og story, med tallene øverst
- [ ] Ett til to bilder per story med egen skjerm, 1280 px, og én linje for de andre
- [ ] En tekst fra kontrollen under hvert bilde, med lenke til spesifikasjonen
- [ ] Mappa under 15 MB, med komprimerte bilder
- [ ] Testene for siden og bildene
- [ ] README-en og vurderingsmatrisen, med testene som låser README-en
- [ ] Gjennomgangen, som sjekker hver tekst mot bildet og spesifikasjonen
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
