---
title: 'Story 2.14: eks.datoer føres inn for hånd'
type: 'code'
created: '2026-11-24'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '4275cd79'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
---

Skrevet 24.11 etter instruksjonen kl. 13:02 i `docs/ai-prompts/2026-11-24.md`,
steg 5, og gruppens svar kl. 13:05: storyen bygges på egen gren, PR-en åpnes,
og den flettes ikke før brukertest 2 er gjort. Rådet anbefalte det, fordi
migreringen endrer den ekte databasen. Worktreen er `G74-lund-osen-2-14`, på
grenen `2-14-eksdatoer`, fra main (`4275cd79`), etter at 2.22 er flettet i
`3f965546` og ført.

## Storyen

Som **gruppe** vil vi føre inn kommende eks.datoer fra selskapenes egne sider,
så appen kan vise dem uten en kilde vi ikke har.

**Oppfyller:** FR-414 · **Begrenses av:** NFR-08, AD-3, AD-6, AD-10, AD-16,
regel 16 og 22

**Avhenger av:** 2.3. Vilkårene leses før første dato. **Én økt:** ja.

## Det som er slått opp

- FR-414 i `prd.md`: datoene føres inn med en kommando, lagres i basen og
  aldri i en fil i repoet. Hver dato har datoen den ble sjekket og hvor den
  ble lest. Et selskap får ingen dato før vilkårene for nettstedet er lest og
  ført i `docs/kilder-og-rettigheter.md`. Kommandoen gjør 0 nettkall, og
  webserveren skriver ikke tabellen. En dato uten sjekkdato eller kilde
  avvises.
- FR-207, visningen i kursgrafen, er et eget krav og er ikke med i kontrollen
  for 2.14.
- Siste migrasjon er `0015_hoey_lav.sql`, så den nye er `0016`.
- `docs/kilder-og-rettigheter.md` har «Status per kilde», men ingen del for
  selskapenes egne sider.
- Basen åpnes med `aapne_base`, som migrerer. Hentingen nekter en demobase
  (`nekt_demobase`).

## Det som gjøres

1. **Tabellen.** `0016_eksdato.sql` lager `eksdato` med `symbol`, `eks_dato`,
   `sjekket` og `kilde`. Hvert symbol har høyst én rad, den kommende
   eks.datoen. Datoene er ISO-datoer, `eks_dato` er ikke før `sjekket`, og
   kilden er ikke tom. Symbolet må stå i `aksje`.
2. **Kommandoen.** `uv run python src/eksdato.py <symbol> <eks.dato>
   --sjekket <dato> --kilde <adresse>`. Den tar én dato for ett symbol og
   gjør ingen nettkall. `--sjekket` og `--kilde` må gis. Den avviser:
   - et symbol som ikke står i lista i basen;
   - et symbol der vilkårene for nettstedet ikke er ført i
     `docs/kilder-og-rettigheter.md`;
   - en kilde som ikke er en adresse på nettstedet som er ført for symbolet;
   - en dato som ikke kan leses, en sjekkdato etter i dag, og en eks.dato
     før sjekkdatoen;
   - en demobase.
3. **Samme dato sjekket på nytt** oppdaterer `sjekket` og `kilde`. **En
   flyttet dato** erstatter den gamle. En eldre sjekk skriver ikke over en
   nyere.
4. **Vilkårene.** `docs/kilder-og-rettigheter.md` får delen «Selskapenes egne
   sider (eks.datoer)» med en tabell: symbol, nettsted, datoen vilkårene ble
   lest, og vurderingen. Tabellen er tom. Gruppen fører radene selv, og
   storyen skriver ingen vilkår for ekte nettsteder. Kommandoen godtar et
   symbol når raden har et nettsted, en dato og vurderingen «ja».
5. **Webserveren** skriver ikke tabellen, og en test holder det.
6. **Ingen eks.dato i sporede filer.** Testene bruker oppdiktede symboler,
   nettsteder og datoer i baser under `tmp_path`.
7. **Dokumentene:** arkitekturen og innleveringen sier `0016`, og README-en
   og hjelpen følger med der de nevner migrasjonene eller kommandoene.

## Resultatet

- `src/migrasjoner/0016_eksdato.sql` lager tabellen `eksdato` med to
  triggere, uten å endre noe som finnes, og uten rader.
- `src/eksdato.py` er kommandoen. Den sjekker formen, datoene, kilden og
  vilkårene før basen åpnes for skriving, og om symbolet står i lista med
  basen åpnet bare for lesing. En dato som avvises, migrerer derfor ikke
  basen. En dato som godtas, gjør det: første dato som føres inn fra main,
  løfter basen fra versjon 15 til 16, hvis hentingen eller webserveren ikke
  alt har gjort det.
- `docs/kilder-og-rettigheter.md` har delen «Selskapenes egne sider
  (eks.datoer)» med en tom tabell. Ingen vilkår for ekte nettsteder er
  skrevet.
- `tests/test_eksdato_2_14.py` bruker det oppdiktede symbolet NYA, nettstedet
  `nyaksje.example` og oppdiktede datoer. Testene som navngir siste
  migrasjon, sier 16, og testen fra 2.10 for en base én versjon bak bruker
  katalogen til og med 0015.
- Migrasjonsfilene står bak bildene av aksjesiden, så de 20 bildene er tatt
  på nytt i demoen på port 8927 og er byte for byte de samme. Avtrykkene i
  `tests/test_docker.py` er regnet ut.
- Storyen er ny kode uten en feil som rettes, så det finnes ingen test som
  feilet før en retting. Testene for migreringen av en base på versjon 15
  kom etter gjennomgangen.

## Gjennomgangen 24.11

Én leser, bare med lesing, i fire roller: Blind Hunter, Edge Case Hunter,
Acceptance Auditor og Verification Gap. Den kjørte ikke pytest. 24 funn: 1
høy, 3 på middels og 20 lave. 9 er rettet, AA1 (middels) står åpent som
spørsmål 1, og 14 lave står med grunn.

| Id | Grad | Funnet | Gjort |
|---|---|---|---|
| VG1 | høy | Migrasjonsfilene står bak bildene av aksjesiden, og avtrykkene i `tests/test_docker.py` var ikke regnet ut | Rettet: bildene er tatt på nytt og er like, og avtrykkene er regnet ut |
| ECH1 | middels | Kommandoen migrerte basen før noe var sjekket, også når datoen ble avvist | Rettet: sjekkene går først, og basen leses uten migrering før den åpnes for skriving. `test_en_dato_som_avvises_migrerer_ikke_basen` |
| VG2 | middels | Ingen test viste at 0016 lar det som finnes i en base på versjon 15, stå | Rettet: `test_migreringen_lar_det_som_finnes_staa` sammenligner skjemaet og alle radene før og etter |
| AA1 | middels | Regel 22 i `CLAUDE.md` sier at basen bare skrives av hentingen og webserveren, med daterte tillegg. Kommandoen er en ny skriver uten en slik linje | Åpent: spørsmål 1. `CLAUDE.md` endres ikke uten gruppens svar |
| BH1, BH4 | lav | En kilde med `\`, brukerinfo eller kontrolltegn kunne lure sjekken mot nettstedet, eller bli lagret | Rettet: slike adresser avvises, med tester |
| BH3 | lav | «ja/nei» og «ja?» i vurderingen talte som ja | Rettet, med tester |
| AA4 | lav | `baseline_commit` pekte på en commit som ikke er på main | Rettet etter at grenen ble flyttet oppå main |
| VG3, VG4 | lav | Flere regler i tabellen og i modulen kunne fjernes uten at en test feilet | Rettet for sjekkdatoen som ikke finnes, og kilden over 500 tegn. Resten står: reglene overlapper |
| BH2 | lav | En rad med feil antall celler eller feil form på symbolet hoppes over, så en eldre «ja»-rad kan vinne | Står: gruppen fører tabellen selv, og formen står over tabellen |
| BH5 | lav | Mangler vilkårsfila, sier meldingen at raden mangler | Står: begge betyr at vilkårene ikke er ført |
| ECH2, ECH3 | lav | En eks.dato som har passert, blir stående, og en dato for en aksje som tas ut, kan ikke rettes | Står: visningen (FR-207) må filtrere. Spørsmål 4 |
| ECH4 | lav | I Docker finnes ikke `docs/`, så kommandoen avviser alt der | Står: spørsmål 5 |
| ECH5, ECH6 | lav | Første kveld etter flettingen gir `dagen_ferdig.py` kode 2, og en eldre demobase må lages på nytt | Står: slik er det for hver migrasjon |
| ECH7 | lav | Vilkårene leses fra arbeidskopien, så en rad som ikke er committet, teller | Står: kommandoen kan ikke se forskjellen |
| AA2 | lav | «Lista sjekkes minst én gang i uka» i FR-414 har ingen kode: kommandoen kan ikke vise hva som er lagret | Står: spørsmål 3 |
| AA3 | lav | `prd.md` sier fortsatt «Ikke i v1» for FR-414 | Står: føres når PR-en flettes |
| AA5 | lav | Linja for 2.14 på skjermsiden er byttet uten Rettet-linje | Står: siden har ingen slike linjer |
| AA6 | lav | Modulen skriver med egen SQL, uten en port i `lagring_sqlite.py` (AD-3), som `valg.py` | Står: tas med AA1 |
| VG5 | lav | Testen for demobasen bæres av utskriften | Står |
| VG6 | lav | Importtesten ser bare importer i margen, og `main` prøves med den ekte klokka og datoer langt tilbake | Står: nettet er sperret i alle testene (AD-8) |

Uten funn: SQL-en i migrasjonen, `ON CONFLICT`, sjekkene før kallene på en
base én versjon bak, to rader for samme symbol, CRLF i dokumentet, «i dag» i
norsk tid, at ingen eks.dato fra en kilde står i en sporet fil, at ingen
vilkår for ekte nettsteder er skrevet, og at README-en ikke trenger retting.

## Spørsmål til gruppen

1. **En ny skriver av basen (AA1, middels).** `src/eksdato.py` skriver
   tabellen `eksdato` i den ekte basen, og regel 22 nevner bare hentingen og
   webserveren. *Forslag:* en datert linje i regel 22 og under AD-3 når
   PR-en flettes: kommandoen fra main skriver bare tabellen `eksdato`.
   *Svar 24.11 kl. 21:47:* som foreslått. Rådet anbefalte det. Den daterte linja i regel 22 og under AD-3
   skrives når PR-en flettes etter brukertest 2, ikke nå. AA1 står til da.
2. **Én rad per symbol.** Tabellen har den kommende eks.datoen for hvert
   symbol, og en ny dato erstatter den gamle. *Forslag:* behold det.
   Alternativet er én rad per dato, med historikken.
   *Svar 24.11 kl. 21:47:* som foreslått: én rad per symbol. Rådet anbefalte det.
3. **Sjekken hver uke (AA2, lav).** Kommandoen kan ikke vise hva som er
   lagret, og når det ble sjekket. *Forslag:* en liten story sammen med
   visningen (FR-207), med et valg som lister radene.
   *Svar 24.11 kl. 21:47:* som foreslått: en liten story sammen med visningen (FR-207). Rådet
   anbefalte det.
4. **Datoer som har passert, og aksjer som tas ut (ECH2, ECH3, lave).**
   Radene blir stående. *Forslag:* la dem stå, og la visningen (FR-207)
   velge hva som vises.
   *Svar 24.11 kl. 21:47:* som foreslått: radene står, og visningen (FR-207) velger hva som vises.
   Rådet anbefalte det.
5. **Docker (ECH4, lav).** Kommandoen leser vilkårene fra `docs/`, som ikke
   er i imaget, så den virker bare fra mappa med koden. *Forslag:* la det
   stå. Datoene føres av gruppen, ikke av en bruker i Docker.
6. **Når flettes den?** Gruppens svar 24.11 kl. 13:05: ikke før brukertest 2
   er gjort. PR-en står åpen til gruppen sier fra.

## Grenser

- Ingen API-kall utover kvotesjekken. Bare testbaser (regel 22). Kommandoen
  kjøres ikke mot `data/db/ose.db`, og den ekte versjonen startes ikke.
- Ingen vilkår for ekte nettsteder skrives i `docs/kilder-og-rettigheter.md`.
- PR-en åpnes, men flettes ikke før brukertest 2 er gjort (gruppens svar
  24.11 kl. 13:05).
- Aldri to pytest samtidig. Hele settet kjøres i CI.

## Kontroll

- [x] En egen tabell, med ny migrasjon: symbol, eks.dato, datoen den ble sjekket, og hvor den ble lest
- [x] Kommandoen tar inn én dato for ett symbol, og nekter et symbol der vilkårene ikke er ført
- [x] Kommandoen gjør ingen nettkall, og webserveren skriver ikke tabellen
- [x] Ingen eks.dato står i en sporet fil
- [x] En ny sjekk av samme dato oppdaterer datoen den ble sjekket, og en flyttet dato erstatter den gamle
- [x] En dato kan ikke føres inn uten dato for sjekken eller uten kilde
- [x] Gjennomgangen med fire roller er tatt. AA1 (middels) står åpent som spørsmål 1
- [x] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt: `--dokumentene` ga 3247 bestått og 7 hoppet over (24.11 kl. 17:04–17:28), på `32b4ab7d`. Testfilene ga da 1188 bestått og 4 feilet, i `tests/test_fetch_prices.py`: hjelperen for en base én versjon bak satte inn rader uten kolonnenavn, og basen på versjon 15 har høy og lav. Etter rettingen ga `tests/test_fetch_prices.py`, `tests/test_indeks.py` og `tests/test_ruff.py` 361 bestått og 16 hoppet over (kl. 17:33–17:37)
- [ ] CI er grønn i alle jobbene
- [ ] PR-en er åpnet og ikke flettet
