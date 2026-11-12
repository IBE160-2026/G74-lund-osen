---
title: 'Story 10.11: «mest av bransjene med minst to aksjer» i teksten om børsdagen'
type: 'feature'
created: '2026-11-12'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'a93c668f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-6-ki-teksten-om-dagen-paa-forsiden.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-10-rikere-ki-tekster.md'
---

Skrevet 12.11 etter instruksjonen kl. 17:03, «Ny liten story i Epic 10: KI-teksten om dagen sier «av bransjene med minst to aksjer»». Instruksjonen er kopiert til scratchpad og føres i dagsfila sammen med flettingen, etter gruppens ja. 10.11 var neste ledige nummer i Epic 10 (`sprint-status.yaml` og `epics.md` har 10.1–10.10, og ingen åpen PR eller gren har 10.11). Storyen bygges nå, og spørsmålene under har hvert et forslag som koden bygger på. Gruppen svarer før PR-en flettes.

**Svaret 11.11 kl. 22:04** (gruppens svar på funn 4 fra demoprøven, gjengitt fra instruksjonen, fordi svaret ikke står andre steder i repoet; slått opp med `git grep` i `origin/main` og grenene til de åpne PR-ene 12.11): formene med «mest» i teksten om børsdagen sier at bransjen er den som steg eller falt mest av bransjene med minst to aksjer. Ønsket 12.11 kl. 16:51 er at alt gjøres ferdig i dag og i natt. Rådet anbefalte det.

## Funnet

I demoen står «I snitt falt finans mest», mens børsometeret viser Industri med −3,97 %. Snittet for «mest» regnes bare for bransjer med minst to aksjer med en endring den dagen (`MINST_I_BRANSJEN` i `src/dagene.py`, brukt i `dagsgrunnlag` i `src/dagsgrunnlag.py`), og det ser ikke leseren.

## Slått opp 12.11 på `a93c668f` (regel 3)

- **Demoen, fredag 09.10** (demobase i en midlertidig mappe, skriptet i scratchpad): Industri har én aksje, med −3,97 %, og Telekom én, med −1,93 %. Finans har to aksjer med −2,68 % i snitt og Energi fire med −2,48 %, så Finans er bransjen som falt mest av bransjene med minst to aksjer. Sjømat har to aksjer med +2,99 % og steg mest. Konsum har én aksje uten endring.
- **Grunnlaget** tar bare med bransjer med minst `MINST_I_BRANSJEN` (2) aksjer med en endring, både i `bransjer` og når `bransje_mest_opp` og `bransje_mest_ned` regnes (`mest_opp_og_ned` av `snitt`). En bransje med én aksje kan altså ikke bli «mest» i dag heller. Det endres ikke.
- **Prompten** (`REGLER_DAGEN` i `src/ki_dagen.py`, versjon dag-2) har formene «I snitt steg ‹bransje_mest_opp› mest.» og «I snitt falt ‹bransje_mest_ned› mest.», og **kontrollen** (`_F_MEST` i `kontroller_dagen`) leser dem. **Eksempelskriveren** (`tekst_om_dagen` i `src/ki_eksempel.py`) skriver de samme formene.
- **KI-loggen i `data/db/ose.db`** har tekster om dagen for 09.11, 10.11 og 11.11, alle med dag-1, og ingen med dag-2 (lest 12.11 kl. 17:05 med `mode=ro`, sha256 for basen den samme før og etter). Kveldshentingen fra main skriver dag-2 fra 12.11, hvis denne storyen ikke er flettet før det.
- **Hjelpen** ved «Børsdagen kort fortalt» (`src/hjelpetekster.py`) er 125 ord på main. PR #146 (8.26) korter den til 48 ord og setter grensen på 50 ord for hver hjelpetekst. `docs/hjelp.md` har setningen om hva modellen fikk ordrett (`test_docs_hjelp_og_readme_sier_det_samme`).

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag, og koden bygger på forslaget.

1. **Hva står i formene?** *Forslag:* «I snitt steg ‹bransje_mest_opp› mest av bransjene med minst to aksjer.» og «I snitt falt ‹bransje_mest_ned› mest av bransjene med minst to aksjer.», som i instruksjonen. Regelen er egentlig minst to aksjer *med en endring den dagen*, men formen holdes kort, og hjelpen og `docs/hjelp.md` sier det presist. «to» regnes av `MINST_I_BRANSJEN`, så formen følger grensen hvis den endres.
2. **Hva gjør kontrollen med den gamle formen?** *Forslag:* den stoppes med en egen grunn: «1: «I snitt falt finans mest» sier ikke «av bransjene med minst to aksjer»». «to» står bare i formen, så «minst 2 aksjer» med siffer, eller ordene etter «mest» på en annen måte, stoppes også, som før, fordi ordene blir stående igjen når formene er tatt ut.
3. **Ny versjon, og hva med tekstene med dag-2?** *Forslag:* prompten får versjon dag-3, fordi dag-2 er flettet og kveldshentingen kan skrive tekster med den (FR-605). Grunnlaget er det samme i dag-2 og dag-3, så en tekst med dag-2 vises fortsatt på forsiden. Den er ikke feil, bare mindre tydelig, og en vurdering eller tekst som er skrevet, skrives ikke på nytt (AD-7).
4. **Hvordan holder hjelpen seg innenfor 50 ord?** På main er hjelpen 125 ord, og grensen på 50 kommer med 8.26. *Forslag:* på grenen nå sier den lange teksten «… i hver bransje med minst to aksjer med en endring, og av dem bransjen som steg mest og den som falt mest i snitt» (128 ord), og `docs/hjelp.md` det samme, med en egen setning: «Bransjen som steg eller falt mest regnes bare av bransjene med minst to aksjer med en endring, så en bransje med én aksje kan ha steget eller falt mer på børsometeret.» (27 ord). Når main med 8.26 er flettet inn i grenen, blir hjelpen: «Et kort sammendrag av børsdagen, skrevet av en språkmodell (KI). Modellen fikk bare det appen regnet ut: hovedindeksen, aksjene som skilte seg ut og bransjene med minst to aksjer, ingen kurser eller nyheter. Teksten sjekkes først: tall med prikket strek står i det modellen fikk, og den gir ikke råd.», 50 ord telt med `\w+`. «før den vises» blir «først» for å holde grensen. Begynnelsen og slutten som testene for 8.26 krever, står.
5. **Hva sier teksten når bare én bransje er med?** Har bare én bransje minst to aksjer med en endring, eller bare én av dem et snitt over (eller under) 0, blir den likevel «mest», og teksten sier «mest av bransjene med minst to aksjer» om en mengde på én (gjennomgangen, ECH5). Det gjaldt også dag-2. *Forslag:* godta det. Det er sant, og en egen form for én bransje ville gitt modellen og kontrollen en form til.
6. **Tekstene med dag-2 fra kveldshentingen i kveld (ECH3).** Kveldshentingen kjører fra main fra kl. 22:15, og denne PR-en flettes tidligst etter 8.26 kl. 23:50–23:58. Teksten for 12.11 får da dag-2 og den gamle formen, og den står (AD-7). *Forslag:* godta det, som i spørsmål 3. Den er ikke feil.

## Delene

### A) Prompten, versjon dag-3

- Formene med «mest» får «av bransjene med minst to aksjer» (spørsmål 1), og forklaringen av feltene `bransje_mest_opp` og `bransje_mest_ned` sier det samme.
- Versjonen er dag-3, og avtrykket i `tests/test_ki_dagen.py` er satt (spørsmål 3). Grunnlaget og tallene er de samme.

### B) Kontrollen (FR-603)

- `_F_MEST` godtar bare formene med «av bransjene med minst to aksjer». Formen uten stoppes med egen grunn (spørsmål 2).

### C) Eksempelskriveren, hjelpen og demoen

- `tekst_om_dagen` i `src/ki_eksempel.py` skriver de nye formene.
- Hjelpen ved «Børsdagen kort fortalt» og `docs/hjelp.md` sier at bransjen som steg eller falt mest er regnet av bransjene med minst to aksjer med en endring (spørsmål 4, regel 19).
- Ny tekst om dagen i `src/demo_ki_dagen.json` fra Gemma med `uv run python src/demo_ki.py --dagen`, høyst tre forsøk. Tekstene om aksjene står. Bildene i `docs/appen/` som viser teksten om dagen, tas på nytt.

### D) Testene

`tests/test_mest_av_bransjene.py`, med «Ville feilet hvis» i hver test: de nye formene består, en form med «mest» uten «av bransjene med minst to aksjer» stoppes, og en bransje med én aksje blir aldri «mest». Testene for 10.6 og 10.10 som har formene, er rettet.

## Grenser

- Ingen API-kall utover kvotesjekken, `src/fetch_prices.py` er ikke kjørt, og `data/db/ose.db` er bare lest med `mode=ro`.
- Grunnlaget, tallene og `MINST_I_BRANSJEN` endres ikke. Teksten om én aksje er urørt.
- Ingen KI-tekst fra den ekte versjonen står i repoet.

## Bygget 12.11 (instruksjonen kl. 17:03)

- Grenen `10-11-mest-av-bransjene-med-minst-to-aksjer` fra `origin/main` (`a93c668f`), i worktreen `G74-lund-osen-10-11`.
- `bd33bdda` spesifikasjonen, `d14d9b08` prompten (dag-3), kontrollen, eksempelskriveren og testene, `e01579a7` hjelpen og `docs/hjelp.md`, `1b14b21f` `epics.md`, sprint-status og Rettet-linjene, `95361180` demoteksten og bildet. Rettingene etter gjennomgangen står i en egen commit etter disse. `d14d9b08` alene er rød for testene av demoteksten, til `95361180`.
- **Gemma:** Ollama-containeren ble startet fra dette vinduet kl. 18:02, da ingen pytest kjørte, og stoppet kl. 18:03. `uv run python src/demo_ki.py --dagen` ga en tekst som besto kontrollen på første forsøk. Tekstene om aksjene står. Teksten (demoen, fredag 9. oktober 2026, oppdiktede selskaper):

> Hovedindeksen falt fredag. De siste fem børsdagene falt hovedindeksen. 7 av 14 aksjer gjorde det bedre enn indeksen. 7 skilte seg ut: 2 med positiv retning, 2 negativ og 3 blandet. Det var flere enn vanlig: snittet de siste 20 børsdagene er 3. Blant dem var Brattfjell Energi (3 av 3, negativ), Kvitstein Mineral (3 av 3, positiv), Laksevik Sjømat (3 av 3, blandet), Trygghavn Forsikring (3 av 3, blandet), Havdyp Olje (2 av 3, blandet) og 2 andre. I snitt steg sjømat mest av bransjene med minst to aksjer. I snitt falt finans mest av bransjene med minst to aksjer.

- **Bildene:** alle bildene i `docs/appen/` er tatt på nytt med DevTools-protokollen, fra en demobase i en midlertidig mappe og waitress på en ledig port. Bare oversikten ved 390 px, som viser teksten om dagen, er ny (samme høyde, 4810 px). `notatene-brfe-390-demo.png` er som på main, som i 10.10. Avtrykkene i `tests/test_docker.py` er regnet ut på nytt, fordi `hjelpetekster.py` og `demo_ki_dagen.json` er med bak bildene.

## Mutanten

Kopi av fila før og sha256 mot HEAD etter (skriptet ligger i scratchpad og er ikke i repoet).

| Fil | Mutanten | Fanget av |
|---|---|---|
| `src/ki_dagen.py` | grunnen for formen uten «av bransjene med minst to aksjer» tatt bort (`if False:`) | `test_mest_uten_av_bransjene_stoppes` (to former) og `test_den_gamle_formen_faar_en_egen_grunn` |

Fanget, og sha256 for fila var lik HEAD etterpå (`340c937c…`).

## Gjennomgangen 12.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Tre lesere i parallell, uten å kjøre pytest eller endre noe. Blind Hunter leste bare diffen.

| Funn | Grad | Hva | Triage |
|---|---|---|---|
| BH1, ECH2, VG1 | middels | Testen av hjelpen så etter «minst to aksjer», som sto der fra før | Rettet: testen ser etter «… med en endring, og av dem bransjen som steg mest» |
| BH2, ECH1, VG2 | lav | Prompten hadde «to» skrevet fast, så bare kontrollen og eksempelskriveren fulgte `MINST_I_BRANSJEN` | Rettet: prompten får `AV_BRANSJENE` (teksten og avtrykket er de samme). Hjelpen og `docs/hjelp.md` har «to» skrevet, og `_SOM_ORD` har 2–5; testen låser grensen til 2 |
| VG3 | lav | Forklaringen av feltene ble ikke testet | Rettet |
| BH4, VG5 | lav | Testen av versjonen sammenlignet to konstanter | Rettet: avtrykket av prompten |
| BH3, VG6 | lav | Testen av en bransje med én aksje i kontrollen sa mer enn den prøvde | Rettet: docstringen sier hva den prøver |
| BH5 | lav | Testen av dag-2 sjekket ikke teksten som vises | Rettet |
| BH7 | lav | Kommentaren i `test_docker.py` sa ikke hvorfor alle avtrykkene ble endret | Rettet |
| BH8 | lav | Rettet-linja under 10.6 i `epics.md` hadde ‹bransje› | Rettet: ‹bransje_mest_ned› |
| VG7 | lav | Spørsmål 4 sa en annen ordlyd enn hjelpen | Rettet i spørsmål 4 |
| ECH3 | lav | Tekstene med dag-2 fra kveldshentingen i kveld får den gamle formen | Spørsmål 6 |
| ECH5 | lav | «mest» når bare én bransje er med | Spørsmål 5 |
| BH6 | lav | `dagsregel` sier «Høyest snitt» uten grensen | Står: regelen er det appen regnet ut (FR-604), og grunnlaget skulle ikke endres |
| VG4 | lav | Testen av dag-2 bruker grunnlaget regnet nå, ikke et fast fra dag-2 | Står: `test_grunnlaget_er_det_samme_som_den_falske_modellen_faar` og grunnlagets avtrykk i demofila (`cd4235ec…`, uendret) dekker det |
| ECH4 | lav | Bransjenavn på tre ord eller med tankestrek leses ikke | Står: gjaldt også dag-2, og ingen bransje i appen har det |
| ECH6 | lav | En lengre fast frase kan gjøre at Gemma bommer oftere | Står: måles i kveldshentingen etter flettingen |

Ingen funn står åpent på middels eller over.

## Hele settet

I fire deler etter filnavn, én om gangen og bare når ingen annen pytest kjørte, kl. 18:11–18:34 på `eec91492`: 1653 (1630 bestått og 23 hoppet over) + 1784 (1783 og 1) + 1186 + 800 = 5423, likt `--collect-only`. ruff og testene for dokumentene besto.
