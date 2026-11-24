---
title: 'Story 9.28: en egen aksje som er tatt inn uten kurser, står ikke som «Hentet»'
type: 'code'
created: '2026-11-24'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'bbf861f6'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-27-statusene-regner-dagen.md'
---

Skrevet 24.11 etter instruksjonen kl. 23:29 i `docs/ai-prompts/2026-11-23.md`
og gruppens svar 23.11 kl. 23:27 på spørsmål 4 i 9.27 (AA1 i gjennomgangen
etter svarene). Rådet anbefalte å vente med storyen til etter brukertest 2,
men gruppen valgte nå. Neste ledige nummer i Epic 9 etter 9.27 er 9.28.
Worktreen er `G74-lund-osen-9-28`, på grenen `9-28-tatt-inn-uten-kurser`, fra
`origin/main` (`bbf861f6`), etter at 9.27 er flettet i `93b26f50` og ført.

## Storyen

Som **bruker som følger en aksje sent en børsdag** vil jeg at appen sier at
aksjen er tatt inn og når kursene kommer, så jeg ikke leser «Hentet» om en
aksje uten kurser, eller at EODHD ikke ga kurser når ingen har spurt.

**Oppfyller:** AA1 i gjennomgangen etter svarene i 9.27 (svaret 23.11 kl.
23:27), FR-412, FR-415 · **Begrenses av:** regel 3, 16, 19, 20, 21 og 22,
NFR-06, NFR-08, AD-3 og AD-10 (siden leser bare); ingen ny migrasjon, og
hentingen endres ikke

**Avhenger av:** 9.27. **Én økt:** ja.

## Det som er slått opp

- Tilfellet: en kjøring av kveldsjobben etter den første tar et ønske i bruk
  (`ta_i_bruk_oenskene` i `src/fetch_prices.py`), så aksjen står i lista med
  `inn` lik dagen. Det nye forsøket som skulle hentet den, bruker bare
  kallene som er igjen av dagens, og målingen etter første kjøring har brukt
  dem. Aksjen har da ingen kurser, og ingen har spurt EODHD om den.
- Det appen viser i dag: «Hentet. Står i tabellen over.» under «Dine egne
  aksjer» (`_egne_regnet` i `src/app.py` og `_egne.html`), og «EODHD har ikke
  gitt kurser for aksjen. Gir EODHD ingen kurser ved neste henting heller,
  slutter appen å følge en aksje du har valgt selv.» bak «?» ved «Oppdatert»
  og på siden for aksjen (`UTEN_KURSER_HVORFOR` i `src/hjelpetekster.py`,
  `aksje_uten_kurser.html`).
- **Appen kan se forskjellen med det som alt er lagret, så ingen migrering
  trengs.** En vanlig henting skriver en rad i `vurdering` for hver aksje i
  lista, også når EODHD ikke ga kurser, da med grunnen `symbol_feilet`
  (`skriv_vurderinger`). En aksje som bare er tatt inn, har ingen rad. Det er
  regelen `valg.uten_rader` alt bruker for å ta ut en aksje som «ble forsøkt
  hentet»: en rad i `vurdering` med `dato >= aksje.inn`.
- «Ikke forsøkt» er derfor: en egen aksje i lista (`ut` ikke satt, og et ønske
  om å følge som er tatt i bruk), med `inn` satt, uten en eneste rad i `kurs`
  og uten en rad i `vurdering` fra og med `inn`.

## Det som gjøres

1. **Regelen.** `valg.ikke_forsoekt(tilkobling)` gir de egne aksjene som er
   tatt inn uten kurser og ikke er forsøkt hentet, med dagen de kom inn. Bare
   lesing.
2. **Dagen.** Kursene kommer ved hentingen dagen etter at aksjen kom inn,
   skrevet som i 9.27: «i morgen etter kl. 22» samme kveld, og «i kveld etter
   kl. 22» fra dagen etter. *Rettet 2026-11-24 (gjennomgangen, ECH1):* her sto
   neste børsdag, med «mandag etter kl. 22» en fredag. Hentingen henter også
   lørdag, se spørsmål 1.
3. **Statusen.** Under «Dine egne aksjer» står «Tatt inn. Kursene kommer ved
   hentingen …» i stedet for «Hentet. Står i tabellen over.» for en slik
   aksje. Knappen «Fjern» står som før.
4. **Teksten bak «?» og på siden for aksjen.** For en slik aksje sier «?» ved
   «Oppdatert» og siden for aksjen at den er tatt inn og at kursene ikke er
   hentet ennå (*rettet 2026-11-24, ECH2:* her sto «ingen kall er brukt på
   den ennå»), ikke at EODHD ikke ga kurser eller at appen slutter å
   følge den.
5. **Som før:** en aksje EODHD faktisk ikke ga kurser for, beholder «Hentet.
   Står i tabellen over.» og teksten om EODHD. Raden i tabellen sier «ingen
   kurser ennå» i begge tilfellene.
6. **Hjelpen.** `docs/hjelp.md` sier det appen nå viser.
7. **Testen** feiler før rettingen. Bildene og avtrykkene håndteres som i
   9.27, og `docs/skjermene.md` får en linje for 9.28.

## Resultatet

| Del | Testen |
|---|---|
| Regelen: `valg.ikke_forsoekt`, bare lesing | `TestRegelen` |
| Dagen: `kursene_kommer_tekst` i `src/markedsoversikt.py` | `TestDagen` |
| Statusen «Tatt inn. Kursene kommer ved hentingen …», med «Fjern» | `TestSidene`, `test_en_aksje_som_skal_fjernes_lover_ikke_kurser` |
| «?» ved «Oppdatert»: `tatt_inn_uten_kurser` i `src/hjelpetekster.py`, i stedet for eller sammen med `uten_data` | `TestSidene`, `test_blandet_viser_begge_tekstene` |
| Siden for aksjen: «… er tatt inn i lista, men kursene er ikke hentet ennå.» | `TestSidene` |
| Tilfellet der EODHD ikke ga kurser, som før | `test_eodhd_ga_ingen_kurser_har_teksten_som_foer` |
| Hentingen er ikke endret, og henter aksjen dagen etter | `test_hentingen_er_ikke_endret_av_regelen`, `test_hentingen_henter_aksjen_en_loerdag` |
| Hjelpen, skjermsiden (144 storyer) og vurderingsmatrisen (102 uten bilde) | `tests/test_skjermene_9_26.py` |
| Avtrykkene bak de 20 bildene | `tests/test_docker.py` |

Tilstandene i testene lages av hentingen selv: kveldens henting, et ønske
etterpå, og en kjøring 45 minutter senere med 20 av 20 kall brukt. Den tar
ønsket i bruk, gjør ingen kall og slutter med kode 1, slik AA1 i 9.27
beskrev.

Testfila ble kjørt mot koden på `29cb5e45`, før rettingen: 20 av de 24
testene feilet. De 4 som besto, var raden i tabellen, de to for tilfellet der
EODHD ikke ga kurser, og oversikten uten en slik aksje, som alle skal være som
før. Etter rettingen besto alle. Testene som kom etter gjennomgangen, er ikke
kjørt mot koden før rettingen.

**Ingen migrering.** Ingen ny tabell, kolonne eller fil. `src/fetch_prices.py`
og `src/migrasjoner/` er ikke rørt.

**Bildene.** Ingen bilder i `docs/appen/` endrer seg, fordi tilstanden ikke
finnes i demoen: demoen henter aldri, så ingen aksje er tatt inn fra et ønske
uten kurser. Alle de 20 bildene ble tatt på nytt i demoen på grenen, på port
8927 med en midlertidig demobase, 24.11 kl. 00:56–00:57 og igjen kl.
01:01–01:02 etter rettingene fra gjennomgangen, og var byte for byte de samme
begge gangene. Avtrykkene i `tests/test_docker.py` er regnet ut på nytt, og
storyen har ingen bildegren.

## Gjennomgangen 24.11

Én leser, bare med lesing, i fire roller: Blind Hunter, Edge Case Hunter,
Acceptance Auditor og Verification Gap. Den kjørte ikke pytest. ECH1 er slått
opp etterpå og vist med en test. 19 funn: 1 høy, 6 middels og 12 lave. ECH1 og
AA2 er samme sak sett fra to roller, og det samme er ECH2 og AA1. 10 er rettet,
7 lave står med grunn, og ECH1 og AA2 står åpne som spørsmål 1.

| Id | Grad | Funnet | Gjort |
|---|---|---|---|
| T1 | høy | Avtrykkstestene i `tests/test_docker.py` ville feile | Rettet: bildene er tatt på nytt, og avtrykkene er regnet ut |
| ECH1, AA2 | middels | «mandag etter kl. 22» en fredag var ikke sant: jobben går hver dag, og lørdag henter et nytt forsøk fredagens kurs med lørdagens kall | Rettet i koden, men åpent: spørsmål 1. Dagen er nå dagen etter, ikke neste børsdag, og det avviker fra ordlyden i svaret (regel 25) |
| ECH2, AA1 | middels | «ingen kall er brukt på den ennå» er ikke sant når et nytt forsøk hadde kall, men ikke fikk kurser. Det skriver ingen rad i `vurdering` | Rettet: tekstene sier «kursene er ikke hentet ennå», og docstringen, hjelpen og spesifikasjonen sier at regelen ser den vanlige hentingen |
| VG1 | middels | Ingen test hadde én aksje bare tatt inn og én som er forsøkt hentet | Rettet: `test_blandet_viser_begge_tekstene` |
| VG2 | middels | Testen fanget ikke at «egen» ble tatt ut av regelen | Rettet: aksjen i testen har en dag den kom inn |
| BH1 | lav | Regelen ble lest to ganger per forespørsel, med to klokker | Rettet: én gang, i `g` |
| BH2 | lav | En aksje som bare er tatt inn og så fjernes, lovet fortsatt kurser på siden sin | Rettet: den holdes utenfor, med en test |
| BH3 | lav | I det blandede tilfellet sier ikke «?» hvilken aksje som er hvilken | Står: statusen og siden for hver aksje sier det |
| ECH3 | lav | En vanlig henting som stopper ved midnatt eller på en basefeil, skriver heller ingen rad | Står: «kursene er ikke hentet ennå» er sant da også |
| ECH4 | lav | Stopper kveldens første kjøring før første kall, kan en senere kjøring hente aksjen samme kveld, mens statusen sier «i morgen» | Står: avviket går i forsiktig retning |
| ECH5 | lav | En aksje som er tatt ut og inn igjen, beholder dagen den først kom inn, så eldre rader i `vurdering` gjør at den leses som forsøkt, og `uten_rader` kan ta den ut igjen før den hentes | Står, fantes fra før: spørsmål 2. Docstringen sier det |
| ECH6 | lav | En klokke før 2026 | Står: teksten slår ikke lenger opp i kalenderen |
| AA3 | lav | Kontrollpunktene var ikke krysset av | Rettet |
| VG3 | lav | Betingelsen på datoen skiller ingenting i tilstandene hentingen kan lage (ECH5) | Står: den følger `uten_rader` |
| VG4 | lav | En egen aksje med kurser, men uten rad i `vurdering` | Rettet: testen har tilfellet |
| VG5 | lav | Et nytt forsøk med kall der EODHD feiler, har ingen test | Står: tekstene er sanne i begge veiene (ECH2) |
| VG6 | lav | «Fjernes» foran «Tatt inn», og en fridag på en hverdag | Rettet for «Fjernes». Fridagen faller bort med ECH1 |

Uten funn: Jinja-uttrykket i `index.html`, en base en versjon bak (ingen 500),
demoen, de ferdige listene, tom base, og at ingen andre steder i `src/` sier
«Hentet» eller teksten om EODHD for en aksje som bare er tatt inn.

## Spørsmål til gruppen

1. **Dagen (ECH1, middels).** Svaret sa «kursene kommer ved hentingen neste
   børsdag, med dagen regnet som i 9.27». Slått opp og vist med
   `test_hentingen_henter_aksjen_en_loerdag`: jobben går hver dag, og en aksje
   som tas inn fredag kveld, får kursene lørdag kveld, av et nytt forsøk med
   lørdagens kall. Grenen sier derfor «i morgen etter kl. 22» samme kveld og
   «i kveld etter kl. 22» fra dagen etter, også i helgen, i stedet for
   «mandag». *Forslag:* behold det grenen gjør, fordi det er det hentingen
   gjør. Alternativet er «mandag», etter ordlyden i svaret, som lover kursene
   to dager for sent. PR-en flettes ikke før gruppen har svart (regel 25).
2. **En aksje som tas inn igjen (ECH5, lav).** Den beholder dagen den først
   kom inn. Ble den tatt ut fordi EODHD ikke ga kurser, og tas den inn igjen
   av en sen kjøring uten kall, står den som «Hentet», og hentingen tar den ut
   igjen neste børsdag før den er hentet. Det fantes før 9.28 og ligger i
   hentingen, som ikke skulle endres. *Forslag:* en egen liten story etter
   brukertest 2, der `inn` settes på nytt når en aksje tas inn igjen.

## Grenser

- Ingen API-kall utover kvotesjekken. `data/`, `.env` og `_privat/` røres
  ikke, og den ekte versjonen startes ikke. Kveldsjobben og databasekopien
  røres ikke.
- Ingen migrering, ingen ny tabell og ingen ny fil for å se forskjellen.
  Hentingen endres ikke.
- Bilder bare av demoen, på en ledig port, aldri 8000, og uten ekte kurser.
- Aldri to pytest samtidig. Lokalt kjøres bare testfilene storyen rører, og
  `--dokumentene`. Hele settet kjøres i CI.

## Kontroll

- [x] En egen aksje som er tatt inn uten kurser og ikke er forsøkt hentet, står som «Tatt inn. Kursene kommer ved hentingen …», med dagen skrevet som i 9.27. Dagen er dagen etter, ikke neste børsdag: spørsmål 1
- [x] «?» ved «Oppdatert» og siden for aksjen sier ikke at EODHD ikke ga kurser, eller at appen slutter å følge den
- [x] En aksje EODHD ikke ga kurser for, har teksten som før
- [x] Ingen migrering, og hentingen er ikke endret
- [x] Testen feilet før rettingen: 20 av 24 på `29cb5e45`
- [x] Hjelpen følger med
- [x] Bildene og avtrykkene er håndtert som i 9.27: de 20 bildene er like, og avtrykkene er regnet ut (`8dbd9ea9`)
- [x] Gjennomgangen med fire roller er tatt. ECH1 (middels) følger av svaret og står som spørsmål 1, så PR-en flettes ikke før gruppen har svart (regel 25)
- [x] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt: 943 bestått (24.11 kl. 01:03–01:09) og 3164 bestått og 7 hoppet over (kl. 01:09–01:29), på `66ddd241`
- [ ] CI er grønn i alle jobbene
