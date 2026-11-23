---
title: 'Story 9.26: skjermene i OSE Signal, ordnet etter epic og story'
type: 'docs'
created: '2026-11-22'
status: 'done'
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

- at epicene og storyene står i rekkefølgen i `epics.md`, med 8.28 i Epic 8;
- at tallene øverst stemmer med `epics.md` og bildene, og at tallene i README-en
  og vurderingsmatrisen følger siden;
- at hvert bilde har en tekst under seg, at den siste har lenken, og at en story
  uten bilde har én linje med tekst før lenken;
- at hver lenke går til en fil og et anker som finnes, for samme story;
- at filnavnet og alt-teksten til hvert bilde begynner med storyen;
- at hver lenke til et bilde peker på en fil i `docs/skjermene/` som git sporer,
  og at hver fil der har en lenke;
- at hvert bilde er en PNG, 1280 px bredt og uten tekstbiter (metadata);
- at mappa er under 15 MB.

## Resultatet

| Del | Commit |
|---|---|
| Storyen i `epics.md` og sprintstatusen | `6ca3e8a8` |
| Siden, bildene og testene | `f8cf3fe3`, og rettingene etter gjennomgangen |
| README-en, med avtrykkene og tallene i `tests/test_docker.py` | `2776181b` |
| Vurderingsmatrisen | `0e003203` |

**Kartleggingen.** Fire lesere kartla de 142 storyene i hver sin del av
`epics.md`: om storyen har en skjerm, adressen og utsnittet i demoen, og teksten
fra kontrollen. Jobblistene ble satt sammen i ett skript, som også bygger siden.

**Bildene.** Bildene ble tatt i demoen på grenen på port 8931 med skriptet fra
9.19–9.25, i Edge uten vindu. Etter gjennomgangen ble alle tatt på nytt, og noen
er klippet til delen storyen ga. De er komprimert til 256 farger. Siden har 53
bilder for 42 storyer, til sammen 1,37 MB, langt under 15 MB. De 100 andre
storyene har én linje: hvorfor storyen ikke har skjerm, eller hvilket bilde som
viser det den ga.

**Like bilder.** Et bilde av appen i dag viser også det senere storyer la til.
Der to storyer ville fått samme eller nesten samme bilde, har bildet stått under
den storyen det hører mest til, og den andre viser til det. Dette står øverst på
siden.

## Gjennomgangen 22.11

Fire lesere i parallell, bare med lesing. Tre gikk gjennom tekstene mot bildene,
kontrollen og demoen: A (Epic 1–5 og 10), C (8.0–8.17) og D (8.18–8.31, og
Epic 6, 7 og 9). Den fjerde var Blind Hunter og Edge Case Hunter for testene,
README-en og spesifikasjonen. Ingen kjørte pytest. 55 funn: 19 middels og 36
lave. 53 er rettet, og 2 lave står.

| Id | Grad | Funnet | Gjort |
|---|---|---|---|
| BH1 | middels | Testene låste ikke rekkefølgen eller hvilken epic en story står under | Rettet: testen sammenligner med `epics.md` |
| BH2, BH3, BH5, ECH1–ECH3 | lav | Lenken og bildet sjekket ikke mot storyen, teksten sto ikke under hvert bilde, regelen for lenkene, tallene i README-en, filer som ikke er sporet, og formatet på `updated` | Rettet |
| BH4, C10, C12 | lav og middels | Kontrollen bak det andre bildet i 8.16 og 8.17 sto i 8.16b og 8.17b | Rettet: hvert bilde kan ha sin egen spesifikasjon |
| A1, D2 | middels | 10.5 og 8.29 hadde samme bilde | Rettet: bildet står under 10.5, og 8.29 viser til det |
| A2 | middels | Teksten om fotnoten i 3.4 lenket til en spesifikasjon som ikke nevner den | Rettet: lenken går til 3.4e, og teksten er ny |
| A3, A5, A4 | middels | 2.9 viste søylene fra 2.9b, og 10.3 og 10.10 var utsnitt av 10.9 og 10.6 | Rettet: 2.9 er klippet, og 10.3 og 10.10 viser til bildet for 10.9 og 10.6 |
| C1, C11 | middels | 1 år viser navn ved annenhver måned, som 8.16 avgjorde | Rettet: 8.0c viser 3 mnd, og 1 år står under 8.16 med «Mer om grafen» åpen |
| C2, C3, C4, C6 | middels og lav | 8.0d, 8.0 og 8.10 viste det samme som andre bilder | Rettet: bildet av oversikten er tatt bort fra 8.0d, og de andre er klippet |
| C5, C9 | middels | Feil story for kortene på børsometeret, og feil grunn for 8.11c | Rettet |
| C8, D5 | middels og lav | 8.11 og 8.30 var utsnitt av bildet for 8.29 | Rettet: de viser til bildet for 8.29 |
| D1 | middels | 8.23 og 8.0e hadde samme bilde | Rettet: bildet er tatt bort fra 8.23 |
| D3, D11, A10, A11 | middels og lav | 6.3 og 6.4 er bygget, men ikke i bruk, og «låst» står ikke i kilden | Rettet |
| D4 | lav | 9.22 var et utsnitt av bildet for 8.21 | Rettet: bildet viser spørsmålet før sletting |
| A6, D15 | lav | Utsnitt med halve linjer øverst | Rettet: klippet |
| A7, A9, A13, A15, C7, C13–C15, D6–D10, D14, D16 | lav | Ordlyd, en grunn som ikke holdt, og delstoryene | Rettet |
| A8, A12, D12, D13 | lav | Bilder som viser det senere storyer la til, og kantene av utsnittene | Rettet: en setning øverst om begge deler |
| A14 | lav | Hjelpen ved «Børsdagen kort fortalt» står i et hjørne av bildet | Står: teksten stemmer med bildet, og bildet er 1280 px bredt |
| A16 | lav | 2.8 og 10.4 har flere spesifikasjoner, og lenken går til den ene | Står: de har ingen bilder, og spesifikasjonene står ved siden av hverandre i `implementation-artifacts/` |

## Spørsmål til gruppen

1. **Like bilder.** Der to storyer ville vist det samme, står bildet under den
   ene, og den andre viser til det. *Forslag:* behold, så siden ikke viser det
   samme bildet to ganger.
   *Svar 2026-11-23 kl. 14:49 (gruppens svar, rådet anbefalte det):* står. Like
   bilder står under én story.
2. **Avtrykk.** Bildene har ikke avtrykk, og siden er et bilde av appen på
   `c0192467`. *Forslag:* behold. Siden tas på nytt når gruppen vil.
   *Svar 2026-11-23 kl. 14:49 (gruppens svar, rådet anbefalte det):* står.
   Bildene har ikke avtrykk.

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

- [x] `docs/skjermene.md` ordnet etter epic og story, med tallene øverst
- [x] Ett til to bilder per story med egen skjerm, 1280 px, og én linje for de andre
- [x] En tekst fra kontrollen under hvert bilde, med lenke til spesifikasjonen
- [x] Mappa under 15 MB, med komprimerte bilder
- [x] Testene for siden og bildene
- [x] README-en og vurderingsmatrisen, med testene som låser README-en
- [x] Gjennomgangen, som sjekker hver tekst mot bildet og spesifikasjonen
- [x] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt (171 og 3122 passerte, 7 hoppet over, 22.–23.11 kl. 23:51–00:13)
- [x] CI er grønn i alle jobbene (run 45082122376)

## Flettet 23.11

PR #175 er squash-flettet i `16b74c35` kl. 00:20, låst til head-en `485dff7d`, uten nytt ja. CI var grønn i alle fire jobbene (run 45082122376), med 6150 bestått og 99 hoppet over i jobben `pytest`. Ingen funn på middels eller høy grad sto åpne.
