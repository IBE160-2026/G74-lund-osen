---
title: 'Story 2.22: en egen kode når det eneste som mangler, er aksjer tatt inn etter kveldens henting'
type: 'code'
created: '2026-11-24'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '609f555b'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-28-tatt-inn-uten-kurser.md'
---

Skrevet 24.11 etter beskjeden kl. 14:31 i `docs/ai-prompts/2026-11-24.md` og
gruppens svar kl. 14:29 på spørsmål 3 i 9.28. Rådet anbefalte å vente til
etter brukertest 2, men gruppen valgte nå. Neste ledige nummer i Epic 2
etter 2.21 er 2.22. Worktreen er `G74-lund-osen-2-22`, på grenen
`2-22-egen-kode-for-tatt-inn`, fra main (`609f555b`), etter at 2.21 er
flettet i `e80d9227` og ført.

## Storyen

Som **gruppe som leser resultatet av kveldsjobben** vil vi at en kveld der
alt er i orden, ikke ender med kode 1, så 1 fortsatt betyr at noe som skulle
vært hentet, mangler.

**Oppfyller:** spørsmål 3 i 9.28 (svaret 24.11 kl. 14:29), FR-412 ·
**Begrenses av:** NFR-01 (nye forsøk bruker aldri bonuskvoten), AD-6, AD-7,
regel 3, 19, 20, 22 og 23; ingen migrering, og hva som hentes, endres ikke

**Avhenger av:** 9.28, 2.21, 2.3b og 2.8. **Én økt:** ja.

## Det som er slått opp

- `start/kveldshenting.ps1` avslutter med koden fra `fetch_prices.py`
  (`$kode = $LASTEXITCODE` og `exit $kode`), så Oppgaveplanleggeren viser
  koden fra kveldens siste kjøring som `LastTaskResult`.
- En kjøring som tar inn en aksje etter kveldens henting, finner at aksjen
  mangler dagens kurs, og går til `nytt_forsoek` i `src/fetch_prices.py`. Gir
  `kall_til_nye_forsoek` 0, avslutter det med `sys.exit(1)`. Det samme
  skjer i hver senere kjøring samme kveld (føringen av 9.28, «Kode 1 fra
  kveldsjobben»).
- Kodene i dag: 0 når alt er hentet, 1 når noe mangler eller feilet, 2 fra
  `argparse` for feil i argumentene, og 3, `KODE_BARE_INDEKSEN`, når bare
  hovedindeksen feilet (beslutningen 17.10 kl. 11:58). 4 er ledig.
- `valg.ikke_forsoekt` (9.28) gir de egne aksjene som er tatt inn uten en
  eneste kurs og uten en rad i `vurdering` fra dagen de kom inn. En aksje som
  sto i lista da kveldens vanlige henting gikk, har en slik rad. En aksje
  med `inn` lik børsdagen og uten rad er derfor tatt inn etter kveldens
  henting.
- Kodene står beskrevet i `docs/hjelp.md` («Kan hentingen gå av seg selv?»,
  som alt sier at hentingen slutter med kode 1 i dette tilfellet, og at det
  ikke er en feil), i modulteksten og docstringene i `src/fetch_prices.py`,
  og i toppen av `start/kveldshenting.ps1`. README-en og
  `docs/installasjon.md` nevner ikke kodene fra hentingen; installasjonen
  har delen «Hentingen hver kveld», som viser til loggen.

## Det som gjøres

1. **Koden.** `KODE_BARE_TATT_INN = 4` i `src/fetch_prices.py`. Et nytt
   forsøk ender med 4 når alt dette gjelder:
   - kjøringen går på selve børsdagen;
   - hver aksje som mangler dagens kurs etter forsøket, er tatt inn i dag
     uten å være forsøkt hentet (`valg.ikke_forsoekt`, med `inn` lik
     børsdagen), og forsøket gjorde ikke noe kall for den;
   - grunnen til at den ikke ble forsøkt, er at det ikke var kall igjen til
     nye forsøk;
   - hovedindeksen feilet ikke i kveldens henting.

   *Lagt til 2026-11-24 (gjennomgangen, ECH1–ECH3):* «ikke forsøkt» gjelder
   hele kvelden, ikke bare kjøringen: har et forsøk tidligere i kveld spurt
   EODHD om aksjen, står den i forsøksfila for dagen, og koden er 1.
   Hovedindeksen må også ha børsdagen i basen. Stoppet forsøket av klokka,
   av at kvoten ikke kunne leses, eller av at bonuskvoten sank, er koden 1.
2. **Som før:** mangler også en annen aksje, eller feilet et kall for en
   aksje som er tatt inn, er koden 1. Feilet indeksen, er koden den som
   gjelder i dag. Kan kvoten eller basen ikke leses, eller er klokka etter
   23:50, er koden 1. Hva som hentes og lagres, endres ikke.
3. **Utskriften** sier koden, hva den betyr, og at det er i orden.
4. **Skriptet.** `start/kveldshenting.ps1` gir koden videre som før, og
   skriver en linje i loggen om hva 4 betyr. Kveldsjobben på PC-en røres
   ikke; skriptet når den først kvelden etter flettingen.
5. **Tekstene.** Hjelpen, installasjonen, modulteksten og docstringene sier
   koden, hva den betyr, og at det er i orden.
6. **Testen** lager tilstandene med hentingen selv, som i 9.28, og feiler
   før rettingen. Testene fra 9.28 og 2.21 som låste kode 1 for tilfellet,
   rettes med en linje om svaret.

## Resultatet

- `KODE_BARE_TATT_INN = 4` og `_koden_naar_noe_mangler` i
  `src/fetch_prices.py`, brukt de to stedene et nytt forsøk ender med at
  noe mangler: når det ikke har kall til nye forsøk, og når noe fortsatt
  mangler etter kallene. Funksjonen leser bare: forsøksfilene for dagen,
  `valg.ikke_forsoekt` og indeksen. Hva som hentes og lagres, er ikke endret.
- `start/kveldshenting.ps1` gir koden videre som før, og skriver en linje i
  loggen om hva 4 betyr, helt til slutt, etter målingen.
- `docs/hjelp.md` og `docs/installasjon.md` sier hva kodene 0, 1, 3 og 4
  betyr, og at 4 er i orden. Hjelpen sa før at hentingen slutter med kode 1
  i tilfellet. README-en nevner ikke kodene.
- `tests/test_kode_4_2_22.py` hadde 15 tester da den ble målt mot koden før
  rettingen (`852f1aa9`): 8 feilet. De 7 som besto, er vakter for at kode 1
  står der noe mangler, og for at hentingen henter som før. Etter
  gjennomgangen har fila 18 tester, og `tests/test_kveldshenting.py` har to
  nye som kjører skriptet med en falsk henting.
- Testene fra 9.28 og 2.21 som låste kode 1 for tilfellet, er rettet med en
  linje om svaret.
- Ingen fil bak bildene er endret, så bildene og avtrykkene står.

## Gjennomgangen 24.11

Én leser, bare med lesing, i fire roller: Blind Hunter, Edge Case Hunter,
Acceptance Auditor og Verification Gap. Den kjørte ikke pytest. 22 funn: 5 på
middels og 17 lave. ECH2 og AA1 er samme sak, og VG1 og VG2 er hullene i
testene for ECH1 og ECH2. Alle de 5 på middels er rettet, 8 lave er rettet,
og 9 lave står med grunn.

| Id | Grad | Funnet | Gjort |
|---|---|---|---|
| ECH1, VG1 | middels | Et forsøk med kall som spurte EODHD om aksjen og ikke fikk kurser, ga riktig 1, men skrev ingen rad. Kjøringene etterpå uten kall ga 4 | Rettet: `_spurt_i_kveld` leser forsøksfilene for dagen, med to tester |
| ECH2, AA1, VG2 | middels | Hovedindeksen lagret uten børsdagen ga 4, fordi bare «indeksen feilet» ble sjekket | Rettet: `indeksen_mangler` sjekkes også, med en test |
| ECH3 | lav | Stoppet forsøket etter et kall på grunn av klokka, kvoten eller bonuskvoten, ga aksjene som ikke ble spurt, 4 | Rettet: `avbrutt`, med en test for bonuskvoten |
| BH1 | lav | Kunne basen ikke leses, ble koden 1 uten en linje om hvorfor | Rettet: utskriften sier det |
| AA2 | lav | Kontrollpunktet om en aksje EODHD ikke ga kurser for, gjaldt bare kjøringen som spurte | Rettet med ECH1 |
| AA3 | lav | Docstringen i `_henting` som lister kodene, manglet 4 | Rettet |
| AA4 | lav | Hjelpen sa at kjøringene etterpå slutter med kode 4 uten forbehold | Rettet: «når det nye forsøket ikke har kall til den» |
| AA5 | lav | `updated` var ikke satt i `docs/hjelp.md` og `docs/installasjon.md` | Rettet, fra `date` |
| VG5 | lav | Skriptet ble bare testet som tekst | Rettet: to tester kjører skriptet med en falsk henting som gir 4 og 3 |
| VG6 | lav | Tekstsjekkene i dokumentene er svake | Rettet for docstringen (AA3); resten står: tekstene er lest i gjennomgangen |
| BH2 | lav | «Kjør samme kommando igjen senere i kveld» står rett før «Kode 4 … Det er i orden» når noen aksjer ble hentet og andre ikke | Står: begge linjene er sanne, og koden sier hva som gjelder |
| BH3 | lav | «1 aksjer» | Står: som resten av utskriften |
| ECH4 | lav | Kveldens siste kjøring, kl. 23:45, kan ende med 1 hvis klokka passerer 23:50 før forsøket starter | Står: spørsmål 1 |
| ECH5 | lav | `start/start.ps1` og `start/start.sh` sier det samme for alle koder utenom 0, også rådet om nøkkelen | Står: spørsmål 2 |
| ECH6 | lav | Feilet `skriv_vurderinger` i kveldens henting, og tas en aksje inn etterpå, er koden 4 og ikke 1 | Står: to feil samtidig, og vurderingene skrives ved neste kjøring uten at noe mangler |
| AA6 | lav | Ingen datert linje ved 2.3b og 2.8 i `epics.md` om unntaket | Står: det står under 2.22 |
| VG3 | lav | Ingen test for basen som ikke kan leses i funksjonen, eller klokka etter 23:50 med en inntatt aksje | Står: begge går til 1 før funksjonen eller i den første linja |
| VG4 | lav | Testen for kl. 23:45 bruker en klokke som står stille | Står: se ECH4 |
| VG7 | lav | Sju av testene består også før rettingen | Står: de er vakter, og «Resultatet» sier det |

Uten funn: argumentene de to stedene, at funksjonen bare leser, BOM i
skriptet, `exit $kode` på siste linje, en aksje fra den første lista, en
aksje tatt inn før kveldens henting, en base en versjon bak, helg, to aksjer
der den ene hentes, andre lesere av koden, NFR-01, at ingen migrering er lagt
til, og at README-en ikke beskriver kodene.

## Spørsmål til gruppen

1. **Kjøringen kl. 23:45 (ECH4, lav).** Starter det nye forsøket etter
   kl. 23:50, er koden 1, også når bare en nylig inntatt aksje mangler.
   Jobben kan bruke inntil tre minutter på Docker og Ollama først.
   *Forslag:* la det stå til etter brukertest 2. Står `LastTaskResult` som 1
   en morgen, sier loggen «Et nytt forsøk starter ingen kall så sent».
2. **Dobbeltklikket (ECH5, lav).** «Start den ekte versjonen» sier det samme
   for alle koder utenom 0, også at nøkkelen kan være feil. *Forslag:* la
   det stå til etter brukertest 2, og gi kode 4 da en egen linje i
   `start/start.ps1` og `start/start.sh`.

## Grenser

- Ingen API-kall utover kvotesjekken. `data/`, `.env` og `_privat/` røres
  ikke, og den ekte versjonen startes ikke. Kveldsjobben på PC-en og
  databasekopien røres ikke.
- Ingen migrering. Bare testbaser under `tmp_path` (regel 22).
- Aldri to pytest samtidig. Lokalt kjøres testfilene storyen rører, og
  `--dokumentene`. Hele settet kjøres i CI.

## Kontroll

- [x] En kjøring der bare aksjer tatt inn etter kveldens henting mangler kursen, uten kall igjen, ender med kode 4
- [x] Hver senere kjøring samme kveld ender også med 4
- [x] Mangler også en annen aksje, er koden 1
- [x] Feilet indeksen i kveldens henting, eller mangler den børsdagen, er koden som før
- [x] En aksje EODHD ikke ga kurser for, gir fortsatt 1, også i kjøringene etterpå samme kveld
- [x] Utskriften, skriptet, hjelpen og installasjonen sier hva 4 betyr, og at det er i orden
- [x] Ingen migrering, og det som hentes og lagres, er som før
- [x] Testen feilet før rettingen: 8 av 15 på `852f1aa9`
- [x] Gjennomgangen med fire roller er tatt, og regel 25 holder: de 5 på middels er rettet
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
