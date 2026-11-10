# Flettingen av de fem storyene

## 2026-11-10 kl. 20:37 — Marian Osen

### Oppgave
Flettingen av 2.4 (#133), 2.6 og 8.14 (#134), 8.7 (#135) og 8.9 (#136) etter brukertesten, etter gruppens svar kl. 11:52, i den rekkefølgen (instruksjonen kl. 15:24). Underveis kom svaret kl. 15:30 (spørsmål 6 i 2.4: hovedindeksen hentes også når bare den mangler), teksten kl. 16:47 etter at vinduet ble lukket ved en feil kl. 16:42, tillegget om main og testene i natt (lest kl. 17:23) og svaret kl. 17:43 om BH2 og ECH7. Alt står ordrett i `docs/ai-prompts/2026-11-10.md`.

### Plan
- Steg 1: instruksjonen og svarene i dagsfila og `epics.md`, testene for dokumentene, push.
- Steg 2 for hver PR: svaret i spesifikasjonen, main inn (resultatet er treet på main pluss grenens diff mot `1a72810a`), avtrykkene og bildene på nytt med `ta_bildene.py` fra 09.11, hele settet i ni deler, push, CI, squash-fletting låst til head-en, grenen og worktreen bort, treet på main likt head-en.
- Steg 3 etter hver fletting: spesifikasjonen, sprint-status, `epics.md`, kvalitetssikringen, testene for dokumentene; til slutt «Status» og «Mappestruktur» i README-en.

### Resultat
- **Kl. 14:12** kom instruksjonen avkortet (uten steg 3–4); ingenting ble gjort utover kvotesjekken (0 brukt i dag i GMT, 20 igjen, bonuskvoten 463).
- **Kl. 15:24** stoppet steg 1: instruksjonen sa «de fem forslagene» for 2.4, men spesifikasjonen hadde seks spørsmål. Svaret kl. 15:30 avgjorde det.
- **Steg 1:** `53ff012c` (dagsfila og svarene under 2.4, 2.6, 8.14, 8.7 og 8.9). `--dokumentene`: 2179 bestått, 20 hoppet over.
- **#133 (2.4):** svarene i spesifikasjonen `674b5abd`, main inn `53c020ff`. Nytt etter svaret kl. 15:30: `indeksen_mangler` og `hent_bare_indeksen` i `fetch_prices.py` (`72aa38d4`), med kvoten som et nytt forsøk, aldri bonuskvoten og egen forsøksfil (AD-6). Mutanten (`indeksen_mangler` alltid `False`) ble fanget av alle åtte testene. Gjennomgangen: 28 funn, én høy (ECH1: `--maal-omsetning` brukte opp kallet indeksen trengte, og venter nå også når bare indeksen mangler), rettet i `27473030` med tester. Ti mutanter etter rettingen, alle fanget. BH2 og ECH7 (middels) ble lukket av gruppen kl. 17:43 (`07a3380f`). Hele settet: 4869 bestått og 31 hoppet over, til sammen 4900. CI grønn (run 42857890383). Flettet som `2c1a17af`; done i `71a9d262`.
- **Vinduet ble lukket kl. 16:42** midt i første kjøring av mutantene. Tilstanden ble sjekket kl. 16:47: ingen låsfil, ingen mutant igjen (fila var lik kopien), og pytest som kjørte, hørte til `G74-lund-osen-8-22` og ble ikke rørt. Mutantene ble kjørt på nytt, alle ti.
- **#134 (2.6 og 8.14):** main inn `299cbc1b`, med konflikten i `app.py` og avtrykkene løst. De ti bildene var byte for byte de samme. Hele settet: 4893 og 25, til sammen 4918. CI grønn (run 42865134280). Flettet som `a2427bee`; done i `5c08697a`.
- **#135 (8.7):** main inn `199a3ee8`, med båndet og volumet og justeringsdagene side om side i `graf.py`, `stil.css` og hjelpen. Bildet av aksjesiden er nytt. Vurderingen i en kopi av basen med koden på main og på grenen: 3750 vurderinger, 0 ulike, og sha256 for basen var lik før og etter. Hele settet: 4907 og 25, til sammen 4932. CI grønn (run 42870268837). Flettet som `2d0cfc8b`; done i `715fcb0b`.
- **#136 (8.9):** main inn `98f0d024`, med fem bilder nye. CI feilet: vakten fra 9.9 fant at `test_vis_meg_rundt_8_9.py` leser endringsforslaget 13.10 gjennom `src/hjelpetekster.py`. Rettet i `d7818bbd` (modulen i `TILLEGG`, og `modulene` tar bare med dem som finnes i mappa). Hele settet: 4921 og 25, til sammen 4946. CI grønn (run 42878900090). Flettet som `eb3ba928`; done i `a314ec9b`, med punktene om spørsmålene og flettingen krysset av i issues.md. Testen for vedlegget fant at `test_samme_tekster_som_hjelpen` er omdøpt til `test_tekstene_fra_tavla`; raden bruker navnet den har nå.
- **README:** `69fe677a`. «Ferdig» har sjekkene og justeringsdagene i kursgrafen innenfor 8 punkter og 20 ord, og setningen under listene «Vis meg rundt», dokumenttestene og etterfyllingen. «Ekstra» har storyene i de åpne PR-ene #137–#139, som 09.11, fordi testen krever minst ett punkt der. «Mappestruktur» har `din-egen-liste-demo.png` og `investorsiden-brfe-demo.png`. Hele settet på main: 4921 og 25, til sammen 4946. CI grønn (run 42886551475).
- **CI på main:** jobben for macOS på `71a9d262` fikk aldri en maskin og ble avbrutt uten steg; kjørt på nytt én gang med `gh run rerun --failed` og grønn. Alle commitene på main i dag har grønn CI.
- **Grenser:** ingen API-kall utover kvotesjekken, `src/fetch_prices.py` er ikke kjørt, `data/db/ose.db` er bare lest som kopi i en midlertidig mappe (sha256 lik), den ekte versjonen og Ollama er ikke startet, og oppgaven, `G74-lund-osen-jobb` og `_privat/` er ikke rørt.
- **Ikke gjort her:** del A kom avkortet (uten steg 2–3 og sluttmarkør) og er ikke startet. Tilleggene 1–3 til del A, del C og tillegget om demoen er hele og ligger i scratchpad til del A er limt inn på nytt. Svaret om 2.13b kl. 17:42 hører til ekstravinduet og er ikke ført her.

### Åpne punkter
- Hele settet i deler kjører `test_dokumenttestene.py` alene i siste del, og da hopper vakten `test_ingen_test_som_leser_dokumentene_faller_utenfor` over seg selv. Bare CI prøver den (8.9 ga rød CI på `98f0d024`).
- «Ekstra» i README-en har de åpne PR-ene #137–#139 fra andre vinduer; gruppen kan bestemme noe annet.
- Del A må limes inn på nytt i sin helhet.
