---
title: 'Story 10.10: Rikere KI-tekster, med navnene og bransjene i teksten om børsdagen og kortere setninger om én aksje'
type: 'feature'
created: '2026-11-11'
status: 'in-review'
route: 'dispatch'
baseline_commit: '059dc10c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-6-ki-teksten-om-dagen-paa-forsiden.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-9-ki-teksten-forklarer-det-siden-viser.md'
  - '{project-root}/docs/brukertest.md'
---

Skrevet 11.11 i instruksjonen kl. 11:00, «Rikere KI-tekster». Den ble først gitt 10.11 kl. 16:28 og ble aldri startet. Instruksjonen er kopiert til scratchpad og føres i dagsfila sammen med flettingen, etter gruppens ja. Storyen bygges nå, og spørsmålene under har hvert et forslag som koden bygger på. Gruppen svarer før PR-en flettes (svaret kl. 16:18: ingen fletting før det).

**Svaret 10.11 kl. 16:18** (gruppens svar, gjengitt fra instruksjonen, fordi svaret ikke står andre steder i repoet; slått opp med `git grep` 11.11): teksten om børsdagen får navnene på aksjene som skilte seg ut og retningen deres, og bransjene som steg og falt mest i snitt. Teksten om én aksje får kortere setninger uten tall som er 0. Rådet anbefalte det. Flettingen og føringen i dagsfila og `epics.md` kommer i en egen instruksjon etter gruppens ja.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag, og koden bygger på forslaget.

1. **Hvilke bransjer er med når appen finner bransjen som steg og falt mest i snitt?** *Forslag:* de samme som i feltet `bransjer`, altså bransjer der minst to aksjer i lista har en endring den dagen (`MINST_I_BRANSJEN`). Snittet regnes som på Børsometeret, av endringen for aksjene som har en endring (`snitt` i `src/boersometer.py`), og sammenlignes slik det vises, med to desimaler. Bransjen som steg mest må ha et snitt over 0,00 og bransjen som falt mest et snitt under 0,00. Med én aksje ville snittet bare si hva den aksjen gjorde (svaret 6.11 kl. 11:15, 1).
2. **Hva skjer når to bransjer har samme snitt?** *Forslag:* da nevnes ingen bransje for den siden, og feltet mangler i grunnlaget. Ellers måtte appen eller modellen velge en av dem, og modellen skal ikke velge noe selv.
3. **I hvilken rekkefølge står navnene?** *Forslag:* 3 av 3 først og så 2 av 3, og alfabetisk etter navnet innenfor samme styrke, i norsk rekkefølge med Æ, Ø og Å sist og uten hensyn til store og små bokstaver (gjennomgangen, BH5). Rekkefølgen følger ikke tabellen, fordi forsiden regner grunnlaget på nytt med den sorteringen siden har (FR-607). Med tabellens rekkefølge ville teksten forsvinne når noen sorterer.
4. **Hvordan skrives navnene?** *Forslag:* én setning etter tallet på dem som skilte seg ut: «Blant dem var Brattfjell Energi (3 av 3, negativ), Kvitstein Mineral (3 av 3, positiv) og 2 andre.» Navnet står som i lista, og retningen med liten bokstav. Høyst fem navn står i teksten, og resten som antall. Den eldre setningen med antallet i hver retning står fortsatt.
5. **Hva skjer med tekstene om dagen fra før flettingen?** Grunnlaget har fire nye felt, så en rad med promptversjon dag-1 ville ikke lenger vært lik grunnlaget forsiden regner ut. Da ville teksten forsvunnet fra de dagene. *Forslag:* forsiden sammenligner en rad med dag-1 med grunnlaget uten de nye feltene (`for_promptversjon` i `src/dagsgrunnlag.py`), så tekstene fra 09.11 og 10.11 fortsatt vises.
6. **Hvem skriver eksempeltekstene i demoen, og hva står i merket?** Ollama skulle ikke startes, så Gemma kan ikke lage tekstene i de nye formene nå. *Forslag:* en fast skriver i appen (`src/ki_eksempel.py`) skriver formene fra reglene med tallene og navnene fra grunnlaget. Den er også den falske modellen i testene, og den finner ingenting selv. Merket står som før, «Laget av KI», men modellen heter «eksempeltekst (lokal)», ikke gemma4:e4b, så ingen tekst ser ut som den er laget av Gemma. «Laget av KI» stemmer da ikke helt for demoen, og gruppen avgjør om merket skal si noe annet der. Etter gruppens ja kan Gemma-tekster lages med `uv run python src/demo_ki.py` og `--dagen`, i en egen instruksjon med Ollama.
7. **Hvilke nye ord stopper kontrollen (NFR-06)?** «bør» sto allerede i lista. *Forslag:* «verdt» («verdt å følge»), «følg med» med bøyningene og «vil» stoppes i begge kontrollene. «vil» står ikke i noen av formene. Vakta på siden (`_VAKT` i `src/ki_visning.py`) er urørt, fordi den stopper ordstammer, og et nytt ord der ville stoppet tekster som besto kontrollen.
8. **Hva er «kortere setninger» i teksten om én aksje?** *Forslag:* formen for bevegelsen er kortere: «fordi kursen steg mer enn den vanligvis svinger» og «fordi dagens endring ikke var stor». Hvert mønster får sin egen korte setning, ikke én lang. En form med tallet 0 skrives ikke: «negativt 0» står ikke, og er antallet dager aksjen gikk samme vei som hovedindeksen eller antallet skift 0, står ikke den setningen. Kontrollen stopper en form med 0. Formene for trenden og interessen står, fordi kontrollen leser dem.
9. **Står setningen «I ‹bransje› steg ‹steg› av ‹med_endring› aksjer» fortsatt i teksten om dagen?** *Forslag:* ja, for nå. Den sier noe annet enn snittet. Teksten har nå opptil sju korte setninger, og gruppen kan be om at den tas ut når de har sett tekstene.

## Intent

**Problem:** testpersonen forsto ikke alt og ville ha mer KI-hjelp (brukertesten 10.11, `docs/brukertest.md`, «Funnene», og U103 i `docs/ux-logg.md`). Teksten om børsdagen hadde bare antall, og teksten om én aksje hadde lange setninger med tall som var 0.

**Brukertesten 10.4 ble tatt 10.11 med promptversjon 5 for teksten om én aksje og dag-1 for teksten om dagen.** Testen brukte dataene fra 09.11 (`docs/brukertest.md`, Rettet-linja 11.11). KI-loggen i `data/db/ose.db` har for 09.11 bare rader med versjon 5 og dag-1 (lest 11.11 med `mode=ro`, sha256 for basen den samme før og etter). Versjon 6 og dag-2 er altså ikke testet med en person.

**Målet:** teksten om dagen sier hvilke aksjer og bransjer som skilte seg ut, og teksten om én aksje er lettere å lese. Appen regner ut alt, og modellen skriver det i faste former.

## Slått opp 11.11 på `059dc10c` (regel 3)

- **Grunnlaget for dagen** (`dagsgrunnlag` i `src/dagsgrunnlag.py`) hadde antallet aksjer, ukedagen, retningen på hovedindeksen, «bedre enn indeksen», antallet som skilte seg ut og retningene blant dem, og for hver bransje med minst to aksjer med en endring hvor mange som steg. Ingen navn.
- **Forsiden** (`_boersdagen` i `src/app.py`) regner grunnlaget på nytt av aksjene på siden, i den rekkefølgen siden har, og `bygg_dagsvisning` i `src/ki_visning.py` viser teksten bare når grunnlaget er likt.
- **Snittet på Børsometeret** er gjennomsnittet av endringen for aksjene i bransjen som har en endring (`snitt` i `src/boersometer.py`), uten vekt.
- **KI-loggen** godtar lister i grunnlaget og lagrer dem som tuple (`_frys` i `src/kilogg.py`). Grunnlaget regnet på nytt har en liste, så sammenligningen måtte gjøre begge til lister.
- **Prompten for én aksje** var versjon 5 (`src/ki_prompt.py`), med én lang setning om mønstrene. **Prompten for dagen** var dag-1 (`src/ki_dagen.py`).
- **Kontrollen for dagen** tar ut formene og stopper alt som er igjen utenom «og», «men» og tegnsetting. **Kontrollen for én aksje** stoppet «bør», men ikke «verdt», «følg med» eller «vil» alene.
- **Navnene i lista:** ingen av de 312 navnene i `aksje` og `boersliste` i `data/db/ose.db` har ord vakta på siden eller de nye ordene stopper (lest 11.11 med `mode=ro`). Navnene har tegnene `&`, `(`, `)`, `-`, `.`, `/` og hardt mellomrom, så kontrollen leser navnet ordrett, med hvilket som helst mellomrom.
- **Demotekstene** lages med Gemma (`src/demo_ki.py`), og testene avviser en tekst laget med en annen prompt.

## Delene

### A) Teksten om børsdagen, promptversjon dag-2

- Grunnlaget får `skilte_seg_ut_navn` (høyst fem, med `navn`, `styrke` og `retning`), `skilte_seg_ut_andre` (bare når det er flere), `bransje_mest_opp` og `bransje_mest_ned` (spørsmål 1–4).
- Prompten forklarer feltene og gir formene «Blant dem var ‹navn› (‹styrke› av 3, ‹retning›) … og ‹skilte_seg_ut_andre› andre.», «I snitt steg ‹bransje_mest_opp› mest.» og «I snitt falt ‹bransje_mest_ned› mest.». Modellen finner ingenting selv og sammenligner ikke.
- `dagsregel` skriver navnene og bransjene i regelen (FR-604).
- En rad med dag-1 vises fortsatt (spørsmål 5).

### B) Teksten om én aksje, promptversjon 6

- Kortere form for bevegelsen, én setning per mønster og ingen tall som er 0 (spørsmål 8).
- Linja om råd sier «bør», «verdt å følge» og «følg med».

### C) Kontrollen (FR-603)

- Teksten om dagen: hvert navn leses ordrett fra grunnlaget med styrken og retningen i parentesen. Feil styrke eller retning stoppes, og det samme gjør et navn som står to ganger eller ikke står i grunnlaget, fordi det blir stående igjen når formene er tatt ut. «og ‹N› andre» må stemme med feltet, og bransjene må være de appen regnet ut. Mangler feltet, stoppes formen.
- Teksten om én aksje: en form for mønstrene med 0 stoppes.
- Begge: «verdt», «følg med» og «vil» stoppes (spørsmål 7).

### D) Demoen

- `src/demo_ki_tekster.json` og `src/demo_ki_dagen.json` er laget på nytt med `uv run python src/demo_ki.py --eksempel` og `--eksempel --dagen`, i de nye formene, med modellen «eksempeltekst» (spørsmål 6). Alle 13 tekstene og teksten om dagen besto kontrollen.

### E) Testene

`tests/test_rikere_ki_tekster.py`, med «Ville feilet hvis» i hver test og eksempelskriveren som falsk modell. Testene for 10.6, 10.9 og demoen er rettet til de nye versjonene.

## Grenser

- Ingen API-kall utover kvotesjekken, `src/fetch_prices.py` er ikke kjørt, og `data/db/ose.db` er bare lest med `mode=ro`.
- Ollama og den ekte versjonen er ikke startet. Ingen KI-tekst fra den ekte versjonen står i repoet.
- Vakta på siden (NFR-06) er urørt (spørsmål 7).

## Bygget 11.11 (instruksjonen kl. 11:00)

- Grenen `10-10-rikere-ki-tekster` fra `origin/main` (`059dc10c`), i worktreen `G74-lund-osen-10-10`.
- `e754a91e` spesifikasjonen, `aa740217` del A og C (dag-2), `c9df6cae` del B og C (versjon 6), `c090db5d` del D og E (eksempeltekstene og testene), `2c2d5b11` README-en og hjelpen. Rettingene etter gjennomgangen står i en egen commit etter disse.
- Demotekstene er laget med `uv run python src/demo_ki.py --eksempel` og `--eksempel --dagen`. Alle 13 tekstene og teksten om dagen besto kontrollen. Etter rettingene ble de laget på nytt og var byte for byte de samme.

## Demotekstene før og etter

Teksten om dagen i demoen (fredag 9. oktober 2026, oppdiktede selskaper), før med Gemma og dag-1:

> Hovedindeksen falt fredag. 7 av 14 aksjer gjorde det bedre enn indeksen. 7 skilte seg ut: 2 med positiv retning, 2 negativ og 3 blandet. I energi steg 1 av 4 aksjer. I materialer steg 2 av 2 aksjer.

Etter, som eksempeltekst med dag-2:

> Hovedindeksen falt fredag. 7 av 14 aksjer gjorde det bedre enn indeksen. 7 skilte seg ut: 2 med positiv retning, 2 negativ og 3 blandet. Blant dem var Brattfjell Energi (3 av 3, negativ), Kvitstein Mineral (3 av 3, positiv), Laksevik Sjømat (3 av 3, blandet), Trygghavn Forsikring (3 av 3, blandet), Havdyp Olje (2 av 3, blandet) og 2 andre. I snitt steg sjømat mest. I snitt falt finans mest.

Teksten om én aksje i demoen (Havdyp Olje), etter, med versjon 6:

> Trenden ga et positivt utslag fordi kursen ligger over snittet for de siste 50 børsdagene. Bevegelsen ga ikke utslag fordi dagens endring ikke var stor. Interessen ga et negativt utslag fordi det ble handlet mer enn vanlig på en dag kursen falt. Aksjen gikk samme vei som hovedindeksen. Av de 15 vurderte børsdagene av de siste 20 var signalet positivt 12 og blandet 3. Aksjen gikk samme vei som hovedindeksen 1 av de 5 dagene som kunne telles av de siste 5 børsdagene. Den siste måneden skiftet retningen minst 5 ganger.

«negativt 0» og «uten retning 0» står ikke. Tekstene er i de faste formene fra eksempelskriveren, ikke fra en modell (spørsmål 6).

## Mutantene

Én per del, med kopi av fila før og sha256 mot HEAD etter (skriptet ligger i scratchpad og er ikke i repoet). Alle ble fanget, og alle filene var like HEAD etterpå.

| Del | Fil | Mutanten | Fanget av |
|---|---|---|---|
| A | `src/dagsgrunnlag.py` | navnene etter navnet, ikke styrken først | `TestGrunnlagetForDagen` |
| B | `src/ki_prompt.py` | «Tall som er 0, kan du ta med» | `TestVersjon6` |
| C | `src/ki_dagen.py` | retningen ved et navn sjekkes ikke | `TestKontrollenForDagen` |
| D | `src/ki_eksempel.py` | modellnavnet «gemma4:e4b» | `TestDemoen` |
| E | denne spesifikasjonen | setningen om promptversjonene i brukertesten | `test_spesifikasjonen_sier_hvilke_versjoner_brukertesten_brukte` |

Del C ble prøvd på nytt etter rettingene, se under.

## Gjennomgangen 11.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Tre lesere i parallell, uten å kjøre tester eller endre noe. Blind Hunter leste bare diffen.

| Funn | Grad | Hva | Triage |
|---|---|---|---|
| BH1, ECH1 | middels | Kontrollen krevde ikke alle navnene, så «og 2 andre» kunne bli feil | Rettet: bruker teksten navnene, må alle stå der, i rekkefølgen i grunnlaget (`_navnene` i `src/ki_dagen.py`) |
| BH3, VG1 | middels | Testen av avrundingen av snittet ville bestått uten avrunding | Rettet: testen går gjennom `dagsgrunnlag` med 1,001 mot 1,004 og 0,004 mot 0,003 |
| VG2 | middels | `dagsregel` hadde ingen test | Rettet: `test_regelen_har_navnene_og_bransjene`, og regelen i demoen sammenlignes |
| VG3 | middels | «vil» ble stoppet av den gamle lista også uten det nye ordet | Rettet: testen bruker «Det vil vise seg.» og krever punkt 4 |
| BH2, ECH2 | lav | Et navn som er slutten av et annet («BP» i «Aker BP») | Rettet: det lengste navnet leses først |
| ECH3 | lav | To aksjer med samme navn | Rettet: leses som to oppføringer |
| ECH4 | lav | «Blant dem var» og «I snitt … mest» kunne stå to ganger | Rettet |
| ECH5 | lav | Navnet i grunnlaget ble ikke normalisert som teksten | Rettet |
| BH4 | lav | Testen med hardt mellomrom | Avvist: grunnlaget hadde hardt mellomrom, også bekreftet av VG. Gjort tydelig med `HARDT` i testen |
| BH5 | lav | Alfabetisk etter kodepunkt, ikke norsk | Rettet (spørsmål 3) |
| BH6 | lav | «følges med» og «fulgte med» slapp gjennom | Rettet. «følg nøye med» slipper fortsatt gjennom teksten om én aksje, men stoppes i teksten om dagen som rest |
| BH7 | lav | Et navn kunne stå utenfor setningen etter «Blant dem var» | Rettet |
| BH8 | lav | Testen av eksempelradene tok ikke med temperaturen | Rettet |
| BH9 | lav | Den negative korte formen for bevegelsen ble ikke prøvd som riktig | Rettet: `test_eksempelskriverens_form_bestaar_for_hvert_fortegn` |
| VG4 | lav | Grunnen (punkt 3 og 4) ble ikke sjekket i teksten om dagen | Rettet |
| VG5 | lav | «Blant dem var» uten navnene i grunnlaget ble ikke prøvd alene | Rettet |
| VG6 | lav | «ordrett» stemte ikke, fordi navnet ble lest uten hensyn til store og små bokstaver | Rettet: navnet leses med bokstavene i grunnlaget |
| VG7 | lav | Hjelpen ved «Børsdagen kort fortalt» hadde tatt ut antallet i hver bransje | Rettet, og setningen står ordrett i `docs/hjelp.md` |
| VG8 | lav | At tekstene for aksjene og `--eksempel` er det skriveren gir, ble ikke testet | Rettet |
| VG9 | lav | Docstrings og navn på tester sa versjon 5 | Rettet |
| VG10 | lav | Endringen i `som_vanlig`, som ingen kaller | Tatt ut igjen, `som_vanlig` er som på `059dc10c` |

Ingen funn står åpent på middels eller over.
