---
title: 'Story 2.21: en aksje som tas ut og inn igjen, får dagen den kom inn igjen'
type: 'code'
created: '2026-11-24'
status: 'done'
route: 'dispatch'
baseline_commit: '11a54503'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-28-tatt-inn-uten-kurser.md'
---

Skrevet 24.11 etter instruksjonen kl. 13:02 i `docs/ai-prompts/2026-11-24.md`
og gruppens svar kl. 12:57 på spørsmål 2 i 9.28 (ECH5 i gjennomgangen). Rådet
anbefalte å vente til etter brukertest 2, men gruppen valgte nå. Neste ledige
nummer i Epic 2 etter 2.20 er 2.21. Worktreen er `G74-lund-osen-2-21`, på
grenen `2-21-ut-og-inn-igjen`, fra main (`11a54503`), etter at 9.28 er flettet
i `4c5bfca8` og ført.

## Storyen

Som **bruker som følger en aksje på nytt** vil jeg at appen regner aksjen som
ny fra dagen den kom inn igjen, så den ikke tas ut før kursene er hentet, og
statusen sier når de kommer.

**Oppfyller:** ECH5 i gjennomgangen av 9.28 (svaret 24.11 kl. 12:57), FR-412,
FR-415 · **Begrenses av:** AD-7 (ingen rad slettes), AD-21, regel 3, 16, 19,
20, 22 og 23; ingen ny migrasjon

**Avhenger av:** 9.28 og 2.12. **Én økt:** ja.

## Det som er slått opp

- `valg.ta_i_bruk` tar en aksje inn igjen med
  `UPDATE aksje SET ut = NULL, sektor = ?`. `inn` røres ikke, så aksjen
  beholder dagen den først kom inn.
- `valg.uten_rader` tar ut en egen aksje som kom inn før dagen, ikke har en
  eneste kurs, og har en rad i `vurdering` fra og med `inn`. `valg.ikke_forsoekt`
  (9.28) bruker samme rad for å skille «bare tatt inn» fra «EODHD ga ingen
  kurser».
- Tilfellet: en egen aksje EODHD ikke ga kurser for, har en rad i `vurdering`
  med en grunn for dagen den ble forsøkt. Kvelden etter tar `uten_rader` den
  ut. Følger brukeren den igjen, og tar en sen kjøring uten kall ønsket i
  bruk, står den med den gamle `inn`. Den gamle raden i `vurdering` teller da
  som et forsøk: statusen sier «Hentet. Står i tabellen over.», og neste
  børsdag tar `uten_rader` den ut før hentingen har spurt EODHD på nytt.
- `inn` brukes også til å si hvilke aksjer som var i lista en bestemt dag:
  `les_lista` og `oversikt` i `src/lagring_sqlite.py` og de ferdige listene i
  `src/ferdige_lister.py` bruker `inn <= dag` og `ut > dag`. Tabellen har én
  `inn` og én `ut` per aksje, så den kan ikke holde to perioder.
- `aksje` har `CHECK (ut IS NULL OR inn < ut)` fra `0009_lista.sql`. Når
  aksjen tas inn igjen, er `ut` NULL, så en ny `inn` bryter ikke regelen.
  `ta_i_bruk` setter alt `ut` til dagen etter når en aksje fjernes samme dag
  som den kom inn.
- Gruppen avgjorde 08.11 kl. 21:35 (spørsmål 6 i 2.11, `epics.md`) at en
  aksje som kommer inn igjen, får `ut` nullstilt, og at en egen tabell med
  periodene venter til det trengs. 2.21 holder det for aksjer med kurser, og
  endrer det bare for aksjer uten en eneste kurs, som ikke har noen periode
  med kurser å vise (gjennomgangen, AA3).
- **Ingen migrering trengs.** Kolonnen `inn` finnes, og rettingen skriver bare
  en ny verdi i den.

## Det som gjøres

1. **Regelen.** Når `ta_i_bruk` tar inn igjen en aksje som er tatt ut, og
   aksjen ikke har en eneste rad i `kurs`, settes `inn` til børsdagen ønsket
   tas i bruk. Da teller ikke eldre rader i `vurdering` som et forsøk:
   `uten_rader` tar den ikke ut før hentingen har prøvd på nytt, og
   `ikke_forsoekt` gir den med den nye dagen, så statusen fra 9.28 regner fra
   den.
2. **En aksje som har kurser, beholder `inn`.** Den tas aldri ut av
   `uten_rader` og er aldri med i `ikke_forsoekt`, så målet gjelder den ikke.
   Ble `inn` flyttet, ville aksjen falle ut av lista for dagene den har
   kurser og vurderinger for, fordi lista for en dag leses av `inn` og `ut`.
   Det står som spørsmål 1.
3. **Ingen rad slettes.** Radene i `vurdering` og `oenske` står (AD-7).
4. **Docstringen** i `ikke_forsoekt` og `ta_i_bruk` sier det koden nå gjør,
   og `docs/hjelp.md` følger med der den sier noe om det.
5. **Testen** lager tilstandene med hentingen selv, som i 9.28, og feiler før
   rettingen. Avtrykkene og bildene håndteres som i 9.27 hvis en fil bak et
   bilde endres, og `docs/skjermene.md` får en linje for 2.21.

## Resultatet

- `valg.ta_i_bruk` setter `inn` til børsdagen når en aksje uten en eneste
  kurs tas inn igjen. En aksje med kurser beholder `inn`. Ingen migrering, og
  ingen rad slettes.
- `tests/test_ut_og_inn_2_21.py` har 8 tester, med tilstandene laget av
  hentingen selv. 6 av 8 feilet mot koden før rettingen (`f01dd638`). De to
  som besto, er vakter som skal si det samme før og etter: en aksje med
  kurser beholder dagen, og regelen i basen om at `inn` er før `ut`, står.
- *Lagt til 2026-11-24 (gruppens beskjed kl. 14:31):* testene bruker bare
  faste øyeblikk, aldri den ekte klokka. Slått opp: `fetch_prices.kjoer` får
  øyeblikket som argument og bruker det som klokke når ingen klokke er gitt,
  `Valglager` får en fast klokke, og sidene får klokka fra `_klient`, som
  bytter ut `app.naa`. Den ekte klokka leses bare i `naa()` i `app.py` og
  `fetch_prices.py` og i tidsstempelet migreringen skriver. Feilen under
  arbeidet var et fast øyeblikk som var lagt etter midnatt norsk tid, ikke
  den ekte klokka. En niende test, `test_klokka_i_testene_er_fast`, holder
  de sene kjøringene mellom kl. 22:00 og 23:50 norsk tid samme børsdag.
- `docs/hjelp.md` sier at en aksje som følges på nytt, regnes som ny fra
  dagen den kom inn igjen.
- `src/valg.py` står bak bildene, så de 20 bildene er tatt på nytt i demoen
  på port 8927 og er byte for byte de samme som i `docs/appen/` og
  `docs/appen/mobil/`. Avtrykkene i `tests/test_docker.py` er regnet ut.

## Gjennomgangen 24.11

Én leser, bare med lesing, i fire roller: Blind Hunter, Edge Case Hunter,
Acceptance Auditor og Verification Gap. Den kjørte ikke pytest. 16 funn: 2
høye, som er samme sak sett fra to roller, og 14 lave. 5 er rettet, AA2 står
som spørsmål 1, og 10 lave står med grunn.

| Id | Grad | Funnet | Gjort |
|---|---|---|---|
| VG1, AA1 | høy | `src/valg.py` står bak bildene, og avtrykkene i `tests/test_docker.py` var ikke regnet ut, så CI ville blitt rød | Rettet: bildene er tatt på nytt og er like, og avtrykkene er regnet ut |
| AA2 | lav | Bare aksjer uten kurser får ny dag, mens instruksjonen og tittelen sier det uten forbehold. Avviket betyr ikke noe for målet, fordi `uten_rader` og `ikke_forsoekt` begge krever en aksje uten en eneste kurs | Står som spørsmål 1. Storyen i `epics.md` sier det nå |
| AA3 | lav | Avgjørelsen 08.11 kl. 21:35 om at en aksje som kommer inn igjen, får `ut` nullstilt, var ikke nevnt | Rettet: «Det som er slått opp» og storyen i `epics.md` |
| AA4 | lav | Setningen i hjelpen sa at statusen alltid sier når kursene kommer, og «før hentingen har spurt» | Rettet: den sier kveldens vanlige henting, og at statusen gjelder en senere kjøring uten kall |
| BH2 | lav | Docstringen i `ta_i_bruk` hadde en lang linje | Rettet |
| BH1 | lav | Én linje i `valg.py` er 121 tegn | Står: `ruff check` og `ruff format --check` er grønne |
| BH3 | lav | `har_kurser` leses i en egen spørring | Står: det er riktig, og lettere å lese |
| BH4 | lav | Utskriften «… er tatt inn i lista fra …» står også for en aksje som beholder en eldre `inn` | Står: linja sier fra hvilken dag den er i lista igjen |
| ECH1 | lav | Fjernes en aksje uten kurser samme kveld som kveldens henting har forsøkt den, og følges den igjen samme kveld, teller forsøket fra samme dag, og den tas ut kvelden etter | Står: forsøket samme børsdag var ekte, så regelen fra 2.12 holder. Spørsmål 2 |
| ECH2 | lav | Etter ny `inn` er aksjen ikke i lista for de eldre dagene den ble forsøkt | Står, følger av valget: den har ingen kurser de dagene, og radene i `vurdering` og `oenske` står |
| ECH3 | lav | En aksje fra den første lista med `inn` NULL, tatt ut og inn igjen uten en eneste kurs, får nå en dag og kan tas ut | Står: den er da en egen aksje uten kurser, som regelen gjelder |
| ECH4 | lav | De ferdige listene regner aksjen som utenfor lista til kursene er lagret | Står: som for en helt ny aksje |
| VG2 | lav | To av åtte tester består også før rettingen | Står: de er vakter, og «Resultatet» sier det |
| VG3 | lav | ECH1 og ECH3 har ingen test | Står: de står med grunn over |
| VG4 | lav | Testene teller radene i `vurdering`, men ikke i `oenske` | Står: rettingen rører ikke `oenske` |

Uten funn: rekkefølgen på parametrene, regelen `inn < ut` i alle
rekkefølgene av fjern og følg, signalet i ettertid, `dagen_ferdig.py`,
målingen, notatene og Min liste, `bruk_liste`, kurser bare fra `--les-inn`,
helgen, at ingen rad slettes, at ingen migrering er lagt til, og tallene på
skjermsiden og i matrisen.

## Spørsmål til gruppen

1. **Bare aksjer uten kurser får ny dag.** Instruksjonen sier at aksjen får
   dagen den kom inn igjen. Storyen gjør det for en aksje uten en eneste
   kurs, som er tilfellet målet gjelder. En aksje med kurser beholder dagen,
   fordi en ny `inn` ville tatt den ut av lista for dagene den har kurser
   for. *Forslag:* behold det. Alternativet, ny dag for alle, trenger en
   tabell med periodene aksjen har vært i lista, og altså en migrering.
   Leseren i gjennomgangen satte avviket til lav (AA2), så det hindrer ikke
   flettingen etter regel 25.
2. **Fjernet og fulgt igjen samme kveld som et forsøk (ECH1, lav).** Da
   teller forsøket fra samme dag, og aksjen tas ut kvelden etter uten et
   nytt forsøk. *Forslag:* la det stå. Det krever to handlinger og tre
   kjøringer samme kveld, og forsøket var ekte.

## Grenser

- Ingen API-kall utover kvotesjekken. `data/`, `.env` og `_privat/` røres
  ikke, og den ekte versjonen startes ikke. Kveldsjobben og databasekopien
  røres ikke.
- Ingen migrering. Bare testbaser under `tmp_path` (regel 22).
- Bilder bare av demoen, på en ledig port, aldri 8000.
- Aldri to pytest samtidig. Lokalt kjøres testfilene storyen rører, og
  `--dokumentene`. Hele settet kjøres i CI.

## Kontroll

- [x] En egen aksje uten kurser som tas ut og inn igjen, får `inn` lik dagen den kom inn igjen
- [x] Den tas ikke ut av `uten_rader` før hentingen har forsøkt den på nytt
- [x] Statusen fra 9.28 står for den, og regner fra den nye dagen
- [x] Gir EODHD ingen kurser ved det nye forsøket, tas den ut kvelden etter, som før
- [x] En aksje med kurser som tas ut og inn igjen, beholder `inn`, og lista for de gamle dagene er som før
- [x] Ingen migrering, og ingen rad er slettet
- [x] Testen feilet før rettingen: 6 av 8 på `f01dd638`
- [x] Gjennomgangen med fire roller er tatt, og regel 25 holder: ingen funn på middels, og de to høye er rettet
- [x] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt: 306 bestått (24.11 kl. 14:17–14:18) og 3164 bestått og 7 hoppet over (kl. 14:18–14:36), på `609fdf46`; testfila med den niende testen ga 9 bestått etterpå
- [x] CI er grønn i alle jobbene (run 45405266824, på `20cd316b`)

## Flettet 24.11

PR #178 er squash-flettet i `e80d9227` 24.11 kl. 14:42, låst til head-en `20cd316b`, etter instruksjonen kl. 13:02 i `docs/ai-prompts/2026-11-24.md`, uten nytt ja. CI var grønn i alle fire jobbene (run 45405266824), med 6231 bestått og 99 hoppet over i jobben `pytest`. Ingen funn på middels eller høy grad sto åpne: de to høye (VG1 og AA1, avtrykkene) er rettet. Spørsmål 1 (AA2, lav) og spørsmål 2 (ECH1, lav) står til gruppen har svart. Koden når kveldsjobben først 25.11, fordi jobben bruker commiten main hadde ved midnatt.
