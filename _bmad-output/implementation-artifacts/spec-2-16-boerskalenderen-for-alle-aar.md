---
title: 'Story 2.16: Børskalenderen for alle år'
type: 'feature'
created: '2026-11-07'
status: 'done'
route: 'dispatch'
baseline_commit: '5b1e2778'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/kilder-og-rettigheter.md'
  - '{project-root}/docs/kvalitetssikring.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-20-ux-rettingene-etter-gjennomgangen-06-11.md'
---

Skrevet og bygget 07.11 i instruksjonen kl. 13:35 (`docs/ai-prompts/2026-11-07.md`), på grenen `2-16-boerskalenderen-for-alle-aar` i worktreen `G74-lund-osen-2-16`. Samme PR har 8.20c (spesifikasjonen for 8.20, «8.20c») og porttestene. Den flettes ikke før gruppen har svart på spørsmålene under.

## Svarene

- *Avgjort 2026-11-07 kl. 11:05 (gruppens svar):* appen regner ut de stengte hverdagene for hvert år etter reglene Oslo Børs følger: 1. januar, skjærtorsdag, langfredag, 2. påskedag, 1. mai, 17. mai, Kristi himmelfartsdag, 2. pinsedag, julaften, 1. og 2. juledag og nyttårsaften, med påsken regnet ut. Listene for 2026 og 2027 blir tester regelen må stemme med. Ingen henting og ingen API-kall. Rådet anbefalte det.
- *Sjekket 2026-11-07 kl. 11:10 (gruppens svar):* Euronexts kalender for 2027 (IF261106CADE, 06.11.2026), lastet ned for hånd, lest ut av rådet og sjekket av gruppen: stengt 2027-01-01, 03-25, 03-26, 03-29, 05-06, 05-17, 12-24 og 12-31, og 2027-03-24 er halv handelsdag og regnes som børsdag.
- *Avgjort 2026-11-07 kl. 11:47 (gruppens svar):* porttestene rettes i samme PR: start.ps1 finner lytteren på port 8000 med netstat når Get-NetTCPConnection ikke ser den. Rådet anbefalte det.

## Spørsmål til gruppen før flettingen

*Svar 2026-11-07 kl. 15:34 (gruppens svar):* forslagene i spørsmål 1–4 under er godtatt: 1) kalenderen dekker 2026 og hvert år etter, og 2025 står utenfor, som avgjort 30.10 kl. 10:45; svaret kl. 11:05 gjaldt årene framover; 2) for en dag utenfor kalenderen står «utenfor børskalenderen, som begynner i 2026», og «ikke vurdert» står som før (spørsmål 18 i 8.20); 3) `Lyttere` i `start/start.ps1` spør først som før, så `Get-NetTCPConnection` uten tilstand etter raden med fjernport 0, og så netstat, fordi netstat alene så lytteren 0 og 4 av 30 ganger; 4) ingen øvre grense og ingen ny kontroll av klokka, og risikoen ved en klokke langt fram i tid er godtatt (BH1, ECH1). Rådet anbefalte alle fire. Svaret står også under story 2.16 i `epics.md` (`c183a07f`).

Hvert spørsmål har et forslag. Byggingen følger forslaget til gruppen har svart.

1. **Får kalenderen 2025?** To svar spriker. 30.10 kl. 10:45 (under 8.17, a): «Børskalenderen får ikke 2025». 07.11 kl. 11:05: «for hvert år». Ingen av dem opphever den andre uttrykkelig. *Forslag:* kalenderen dekker 2026 og hvert år etter, uten øvre grense (`FOERSTE_AAR = 2026` i `src/boersdag.py`), og 2025 står utenfor, som avgjort 30.10. Grunnen: regelen er sjekket mot Euronext for 2026 og 2027, og repoet har ingen liste for 2025. Hva som ville endret seg for 2025 i den ekte versjonen, står under «Slått opp». Sier gruppen ja til 2025, er endringen `FOERSTE_AAR = 2025` og testene som bruker 2025 som «utenfor».
2. **Spørsmål 18 i 8.20 (U100): «ikke vurdert» og «utenfor børskalenderen».** Forslaget i 8.20 var «utenfor børskalenderen, som bare har 2026», med årene fra `DEKKEDE_AAR`. Med 2.16 har kalenderen ingen siste år, så den setningen stemmer ikke lenger. *Forslag:* begge tekstene står, fordi FR-409 skiller dem, og den andre sier året kalenderen begynner i, lest fra `FOERSTE_AAR`: «utenfor børskalenderen, som begynner i 2026». Den kan bare stå for en dag før 2026. «ikke vurdert» står uendret.
3. **Porttestene: netstat alene finner ikke lytteren.** Målt 07.11 med en lytter på 127.0.0.1:8000 som sto hele tiden, 30 forsøk med 0,3 sekunder imellom, to ganger: `netstat -ano` hadde raden 0 og 4 ganger, `Get-NetTCPConnection -State Listen` 1 og 0 ganger, og `Get-NetTCPConnection` uten tilstand, med fjernport 0, 30 og 30 ganger. Windows melder tilstanden feil (`FinWait1`, 0 eller ingen), og netstat bygger på det samme. *Forslag:* `Lyttere` i `start/start.ps1` spør først som før, så `Get-NetTCPConnection` uten tilstand etter raden med fjernport 0 og fjernadresse 0.0.0.0 eller ::, og så netstat, som svaret sier, opptil fem ganger med et halvt sekund imellom. Med netstat alene feilet porttestene fortsatt.
4. **Klokka langt fram i tid (BH1 og ECH1 i gjennomgangen, middels).** Uten øvre grense stopper ikke hentingen lenger når klokka på maskinen står i et år etter 2026. Står klokka for eksempel i 2031, bruker hentingen kallene og skriver vurderinger for en dag i 2031, som etter AD-7 ikke kan rettes. Før 2.16 stoppet hentingen for alle år etter 2026, men det var et vern ingen hadde bestemt, og innenfor 2026 fantes ikke vernet. Reglene er heller ikke sjekket mot Euronext etter 2027. *Forslag:* ingen øvre grense, som svaret kl. 11:05 sier, og ingen ny kontroll av klokka i denne storyen. Funnene står åpne til gruppen har svart (regel 25).

## Slått opp 07.11 på `5b1e2778` (regel 3)

**`src/boersdag.py`:** `STENGT` var de ti stengte hverdagene i 2026, ført for hånd, og `DEKKEDE_AAR = frozenset({2026})`. `innevaerende_boersdag`, `forrige_boersdag` og `er_boersdag` reiste `UtenforKalenderen` for en dag de måtte slå opp utenfor `DEKKEDE_AAR`. Fra 01.01.2027 ville derfor kveldshentingen stoppet med 0 kall, og `skriv` reist (punkt 25 i PRD-en).

**Stedene som bruker `DEKKEDE_AAR`:** `src/indeksdata.py` (`bare_boersdager`, porten for indeksen), `src/fetch_prices.py` (utskriften om dagene som ble tatt bort, og kommentaren om at modulen leses), og i kommentarer `src/graf.py` og `src/lagring_sqlite.py`. Testene: `test_boersdag.py`, `test_fetch_prices.py` (utskriften og årsskiftet), `test_indeks.py`. `STENGT` ble bare brukt i `boersdag.py`, i en kommentar i `perioder.py` og i testene.

**Stedene som fanger `UtenforKalenderen`:** `aksjedetalj.boersdag_mellom` (gir True, så datoene står), `app._innevaerende` (gir None, så fotnoten om lagring ikke står) og utfallet for samme dag (siden uten setningen), `dagene.tell_dagene` («minst»), `fetch_prices.kjoer` (stopper med 0 kall før nøkkel og kvote, og første henting på dagtid sier nei), `graf._foerste_boersdag` (intet månedsmerke), `hovedindeks.forrige_boersdag` (None, ingen endring), `markedsoversikt.les_tilstand` («utenfor børskalenderen»), `moenstrene.boersdagene` og `skiftene` (færre dager, «minst»), `omsetning` (målingen stopper) og `perioder.foerste_boersdag_fra` (første hverdag). `tilstand.tilstand` og `SqliteVurderingslager.skriv` slipper den gjennom. Ingen av stedene endres: med 2.16 kan de bare nås for en dag før `FOERSTE_AAR`.

*Rettet 2026-11-07 etter gjennomgangen (VG11):* lista over steder som slipper `UtenforKalenderen` gjennom, er ikke fullstendig. Også `dagen_ferdig.py`, `ki_tekst.py`, `kilogg_minne.py` og tre steder i `lagring_sqlite.py` gjør det. Alle kan bare nås for en dag før `FOERSTE_AAR`.

**Hva som endres for 2025 i den ekte versjonen:** med forslaget i spørsmål 1 ingenting, fordi 2025 står utenfor som før. `data/db/ose.db` er ikke lest. Kom 2025 med, ville dette endret seg, etter koden over: indeksen ville fått dagene i 2025 ved neste henting (serien fra EODHD går ett år bakover), så perioden «1 år» får den stiplede linja før 02.01.2026 (U4); startdagen for en periode som begynner i 2025, ville tatt hensyn til helligdagene i stedet for å ta første hverdag; grafen ville fått månedsmerker for månedene i 2025; endringskortet ville slått opp helligdagene mellom to kursrader i 2025 i stedet for å vise datoene; endringen i hovedindeksen tidlig i januar 2026 ville blitt regnet mot 31.12.2025; en dag i 2025 i «Signalet dag for dag» ville stått som «ikke vurdert» eller «ikke børsdag» i stedet for «utenfor børskalenderen»; og rekkene og mønstrene ville gått inn i 2025 i stedet for å stoppe med «minst». Det skrives ingen vurderinger for 2025, fordi bare inneværende børsdag skrives (AD-7). Regelen er ikke sjekket mot en liste for 2025.

**Hvorfor porttestene feiler her:** se spørsmål 3. Testene feilet ved `Frigjoer-Porten`: `Opptatt` fant porten opptatt, men `Lyttere` fant ingen prosess, så skriptet stoppet med «et program skriptet ikke fant navnet på». I miljøet testene gir PowerShell, uten `PATHEXT`, kjører heller ikke `netstat` («Cannot run a document in the middle of a pipeline»), så netstat startes gjennom .NET med full sti.

**Demoen i januar 2027:** demoen har faste datoer fra 02.01 til 09.10.2026 og slår aldri opp en dag etter 09.10.2026. Med klokka 15.01.2027 er sidene `/`, `/min-liste`, `/boersometer`, `/aksje/BRFE`, `/aksje/BRFE?periode=iaar` og `/?periode=iaar` like som med klokka 13.10.2026, bortsett fra året bak datoene (story 8.0c). Det var de også med kalenderen bare for 2026, prøvd 07.11 med `boersdag.dekker` byttet ut.

## Delene

### A) Regelen (svaret kl. 11:05)

`stengte_dager(aar)` i `src/boersdag.py` regner ut de stengte hverdagene for et år etter reglene, med påsken fra `paaskedag(aar)` (den gregorianske, anonyme algoritmen). En helligdag på en helg tas ikke med. Halve handelsdager er børsdager. `STENGT` går ut.

**Ville feilet hvis:** en regel manglet eller var feil, for eksempel 2. pinsedag regnet fra feil dag: da gir 2026 eller 2027 en annen liste enn Euronext (`TestStengteDager::test_regelen_stemmer_med_euronext`). Listene står også i `docs/kilder-og-rettigheter.md`, og en test holder dem like.

### B) Grensen: `FOERSTE_AAR` i stedet for `DEKKEDE_AAR` (spørsmål 1 og 2)

`DEKKEDE_AAR` går ut. `dekker(aar)` er sann fra `FOERSTE_AAR`, uten øvre grense. Indeksporten, hentingen og utskriften leser året fra modulen, så en test kan flytte det. Utskriften fra indeksen sier «dager før 2026» og «Børskalenderen i appen begynner i 2026, så dager før lagres ikke.» Hentingen før `FOERSTE_AAR` sier at kalenderen begynner i 2026, og ber om å sjekke klokka, i stedet for å be om at dagene føres inn. «utenfor børskalenderen» får året (spørsmål 2).

**Ville feilet hvis:** kalenderen sluttet i 2026, som før 2.16: årsskiftet til 2027 stoppet hentingen med 0 kall (`TestAarsskiftet::test_aarsskiftet_gir_nye_dager_i_indeksen`), mandag 04.01.2027 kunne ikke skrives (`test_2027_skrives`), eller inneværende børsdag reiste en dag i 2027 eller 2028 (`test_aarene_etter_2026_er_med` og `test_enig_med_innevaerende_boersdag_hver_dag_2026_til_2028`).

### C) Demoen i januar 2027

**Ville feilet hvis:** en side i demoen feilet med klokka i januar 2027, eller viste noe annet enn året bak datoene (`TestDemoenIJanuar2027`). Testen er et vern: demoen var lik også før 2.16 (se «Slått opp»), så mutanten for denne delen fanges av testene i A og B, ikke her.

### D) Porten (svaret kl. 11:47, spørsmål 3)

`Lyttere` i `start/start.ps1` spør som i spørsmål 3. `Lyttere-I-Netstat` leser linjene fra `netstat -ano`: lokal port 8000 og fjernadresse 0.0.0.0:0 eller [::]:0, uansett tilstand, uten prosess 0. Funnet prosess sjekkes som før av `Er-OseSignal`, så skriptet stopper fortsatt aldri et annet program.

**Ville feilet hvis:** netstat-linjene ble lest etter tilstanden LISTENING, så lytteren med FIN_WAIT_1 ble borte, eller en tilkobling, en annen port, UDP eller prosess 0 ble tatt med (`test_start_ps1_kjenner_lytteren_i_netstat_uansett_tilstand`); eller `Lyttere` bare spurte med `-State Listen` og netstat (`test_start_ps1_finner_lytteren_naar_tilstanden_er_feil`). De sju porttestene fra 3.5d og 3.5e går gjennom igjen lokalt, og de som sjekker at et fremmed program og en annen mappe aldri stoppes, står.

### Bildene

`boersdag.py`, `markedsoversikt.py` og de andre modulene er med i avtrykkene bak bildene i `docs/appen/`, så alle sju ble tatt på nytt, med DevTools-protokollen i Edge uten vindu som i 10.9. Seks er byte for byte de samme. `min-liste-demo.png` er ny fordi 8.20c endrer navnet på periodevalget (U101), med samme høyde.

## Grenser

- Ingen kall til EODHD utover kvotesjekken i regel 15, og `src/fetch_prices.py` er ikke kjørt. `data/db/ose.db` er ikke rørt (regel 22). Demobasene lå i midlertidige mapper.
- Euronext er ikke hentet, og PDF-en er ikke committet eller lest utover sha256.
- `start.ps1` stopper aldri et annet program.

## Bygget 07.11

Tre commits, én sak hver, og hele settet kjørt alene før hver, med ledig minne 4,6–4,7 GB av 15,7 GB:

| Commit | Saken | Hele settet |
|---|---|---|
| `2b8db0d7` | Porten (del D) | 14:14:08–14:25:57: 4338 bestått, 24 hoppet over, 0 feilet |
| `df946918` | Kalenderen (del A–C) | 14:27:33–14:39:42: 4378 bestått, 24 hoppet over, 0 feilet |
| `fea11d48` | 8.20c | 14:40:27–14:52:01: 4380 bestått, 24 hoppet over, 0 feilet |

De sju porttestene som feilet lokalt siden 29.10, går gjennom fra `2b8db0d7`.

**Mutantene** på `fea11d48`, hver med kopi av fila før og blob lik HEAD etter (`git hash-object` mot `git rev-parse HEAD:fil`):

| Del | Mutanten | Fanget av |
|---|---|---|
| A | 2. pinsedag fra påskedag + 49 | `test_regelen_stemmer_med_euronext[2026]` og testen for 2. pinsedag 2026 |
| B | `dekker` slutter i 2026 | `test_aarsskiftet_gir_nye_dager_i_indeksen`, `test_2027_skrives`, `test_ingen_rad_i_2027_er_ikke_kjoert` og `test_nyttaar_2027_er_i_kalenderen`. I `tests/test_boersdag.py` stopper den allerede innsamlingen, fordi parametriseringen regner ut 2027 |
| C | samme som B | **ikke fanget** av `TestDemoenIJanuar2027`, som ventet: demoen slår ikke opp dager etter 09.10.2026. B fanger den |
| D | `Lyttere` uten spørsmålet uten tilstand | `test_start_ps1_finner_lytteren_naar_tilstanden_er_feil` |
| D | netstat-linjene lest etter LISTENING | `test_start_ps1_kjenner_lytteren_i_netstat_uansett_tilstand` |
| 8.20c | `debug=True`, setningen om kontoen borte, «utenfor børskalenderen» uten året, «Sammenlign med» | testene i avsnittet 8.20c i spesifikasjonen for 8.20 |

*Rettet 2026-11-07 etter gjennomgangen (VG2):* `aksjedetalj.boersdag_mellom` gir `endring_med_datoer`, men ingen mal bruker det feltet etter 8.2b (`6f62f564`). Endringskortet viser alltid «fra … til …». Setningen om endringskortet under «Hva som endres for 2025» og «så datoene står» under «Slått opp» gjelder derfor ingenting brukeren ser. `test_nyttaar_2027_er_i_kalenderen` prøver funksjonen, ikke siden.

## Gjennomgangen 07.11

Blind Hunter, Edge Case Hunter og Verification Gap på `5b1e2778..6eeaf5b2`, etter hele settet, med 10, 8 og 11 funn. Ingen på høy. Rettet i `c140e607`, med hele settet kjørt alene før commiten kl. 15:04:00–15:15:27: 4387 bestått, 24 hoppet over, 0 feilet.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| BH1, ECH1 | middels | Uten øvre grense skrives vurderinger hvis klokka står langt fram i tid | **åpent**, spørsmål 4 (regel 25) |
| VG1, BH6, ECH2 | middels | «utenfor børskalenderen» laget ved import, så den fulgte ikke `FOERSTE_AAR` | rettet: `utenfor_kalenderen()` leser året når teksten brukes, og en test flytter `FOERSTE_AAR` |
| VG2 | middels | Påstandene om endringskortet stemte ikke: feltet brukes ikke i noen mal | rettet i spesifikasjonen (Rettet-linja over) og i docstringen i `tests/test_app.py`. Det ubrukte feltet er ikke tatt her |
| VG3 | middels | Ingen test for månedsmerkene i 2027, og punktet i `deferred-work.md` sto åpent | rettet: `TestMaanedsmerkerI2027`, og en linje `resolved` i `deferred-work.md` |
| BH2 | middels | En lytter med feil tilstand ble ikke sett når en annen var sett med `-State Listen` | rettet: raden uten tilstand tas alltid med, test `to_lyttere` |
| BH7, ECH3 | lav | Cachen gikk forbi grensen | rettet: grensen sjekkes før `_regn_ut` |
| BH4, ECH7 | lav | netstat uten tidsgrense | rettet: høyst 5 sekunder, så stoppes bare netstat. Kostnaden med fem runder står, fordi den bare kommer når porten svarer uten en lytter som kan ses |
| BH9, VG10 | lav | Gjentakelsen, netstat til slutt, prosess 0 og :: var ikke testet | rettet: `test_start_ps1_lyttere_proever_alle_veiene` |
| VG8 | lav | Meldingen om klokka var ikke testet | rettet |
| VG9 | lav | Hjelpeknappen for U101 var ikke testet | rettet |
| BH5, ECH5, VG5, ECH6, VG7 | lav | Kommentarer og docstrings om `debug=True`, `STENGT` og `DEKKEDE_AAR` | rettet |
| VG4 | lav | Kildene sa at dagene for 2027 føres inn når Euronext publiserer dem | rettet med en Rettet-linje |
| VG11 | lav | Lista over steder som slipper feilen gjennom, var ufullstendig | rettet med en Rettet-linje |
| VG6 | lav | Planleggingsdokumentene og `sprint-status.yaml` nevner `DEKKEDE_AAR` og står som `backlog` | føres ved flettingen, med punkt 25 i PRD-en |
| BH3 | lav | En rad med fjernport 0 regnes som lytter også når den virkelig lukkes | avvist: det er den tilstanden Windows feilaktig melder for lytteren, så den kan ikke skilles ut. Feilen kan bare gi en feil melding, aldri at et annet program stoppes |
| BH8 | lav | Testen for januar 2027 fanger ikke 2.16 | avvist: står i «Slått opp» og i mutanttabellen. Testen er et vern |
| BH10 | lav | Vinduet ved dobbeltklikket nevner ikke en konto fra før | utsatt: spørsmål 20 i 8.20 gjaldt README-en. Kan tas med 3.4h eller 8.20a |
| ECH4 | lav | `foerste_boersdag_fra(date(9999, 12, 31))` gir `OverflowError` | avvist: kan ikke nås, fordi en dag etter i dag og etter siste kurs avvises |
| ECH8 | lav | Prosess 4 (System) vises som et program uten kommandolinje | avvist her: fantes før, og stoppes aldri |

*BH1 og ECH1, lukket 2026-11-07 etter gruppens svar kl. 15:34 (regel 25).* Svar 4: ingen øvre grense og ingen ny kontroll av klokka, og risikoen ved en klokke langt fram i tid er godtatt. Koden er ikke endret.

**Mutantene for rettingene**, på `c140e607`, med kopi før og blob lik HEAD etter: bare én runde i `Lyttere` (fanget av `tredje_runde`), prosess 0 tatt med (`prosess_0_og_ipv6`), raden uten tilstand bare når ingen er sett (`to_lyttere`), året skrevet fast i teksten (`test_utenfor_boerskalenderen_foelger_foerste_aar`), og cachen rundt grensen (`test_grensen_gjelder_ogsaa_et_aar_som_er_regnet_ut`). Alle ble fanget.
