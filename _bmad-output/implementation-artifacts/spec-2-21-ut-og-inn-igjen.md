---
title: 'Story 2.21: en aksje som tas ut og inn igjen, får dagen den kom inn igjen'
type: 'code'
created: '2026-11-24'
status: 'in-progress'
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

## Spørsmål til gruppen

1. **Bare aksjer uten kurser får ny dag.** Instruksjonen sier at aksjen får
   dagen den kom inn igjen. Storyen gjør det for en aksje uten en eneste
   kurs, som er tilfellet målet gjelder. En aksje med kurser beholder dagen,
   fordi en ny `inn` ville tatt den ut av lista for dagene den har kurser
   for. *Forslag:* behold det. Alternativet, ny dag for alle, trenger en
   tabell med periodene aksjen har vært i lista, og altså en migrering.

## Grenser

- Ingen API-kall utover kvotesjekken. `data/`, `.env` og `_privat/` røres
  ikke, og den ekte versjonen startes ikke. Kveldsjobben og databasekopien
  røres ikke.
- Ingen migrering. Bare testbaser under `tmp_path` (regel 22).
- Bilder bare av demoen, på en ledig port, aldri 8000.
- Aldri to pytest samtidig. Lokalt kjøres testfilene storyen rører, og
  `--dokumentene`. Hele settet kjøres i CI.

## Kontroll

- [ ] En egen aksje uten kurser som tas ut og inn igjen, får `inn` lik dagen den kom inn igjen
- [ ] Den tas ikke ut av `uten_rader` før hentingen har forsøkt den på nytt
- [ ] Statusen fra 9.28 står for den, og regner fra den nye dagen
- [ ] Gir EODHD ingen kurser ved det nye forsøket, tas den ut kvelden etter, som før
- [ ] En aksje med kurser som tas ut og inn igjen, beholder `inn`, og lista for de gamle dagene er som før
- [ ] Ingen migrering, og ingen rad er slettet
- [ ] Testen feilet før rettingen
- [ ] Gjennomgangen med fire roller er tatt, og regel 25 holder
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
