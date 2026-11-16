---
title: 'Story 9.15: meldingene etter v1.1 og det som ikke brukes'
type: 'chore'
created: '2026-11-16'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'c2adf7f5'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-17-signalet-regnet-i-ettertid.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-14-kontrollrunden-etter-v1-1.md'
---

Skrevet 16.11 i vinduet som bygde 2.18, etter steg 2 i instruksjonen kl. 15:39
og gruppens svar 16.11 kl. 15:39 på spørsmål 10, 11 og 12 i 9.14, ført i
`docs/ai-prompts/2026-11-16.md`. Svaret endrer svaret kl. 09:51 («etter
innleveringen»), fordi testen tidligst blir i morgen. Rådet anbefalte alle
svarene. Neste ledige nummer i Epic 9 etter 9.14 er 9.15. Worktreen er
`G74-lund-osen-9-15`, på grenen `9-15-meldingene-og-det-som-ikke-brukes`, fra
`origin/main` (`c2adf7f5`).

## Storyen

Som **gruppe** vil vi at meldingene fra hentingen sier det v1.1 gjør med en dag
uten kveldsrad, og at kode som ikke brukes noe sted, er tatt bort, så det vi
leverer, ikke motsier seg selv.

**Oppfyller:** spørsmål 10 og 11 i 9.14 · **Begrenses av:** 2.17 (FR-401, FR-408,
AD-7), regel 16, 22 og 23

**Avhenger av:** 2.17, 9.14. **Én økt:** ja.

## Svarene

*Svar 2026-11-16 kl. 15:39 (gruppens svar, rådet anbefalte det), spørsmål 10, 11
og 12 i 9.14:* storyen tas nå. D1–D4: meldingene i `src/fetch_prices.py`
(`_stoppet_ved_midnatt` og `_kan_skrives_til`), i `src/tilstand.py` og i
utskriften fra `--les-inn` skal si det v1.1 gjør, og hver melding får en test
som feiler mot teksten før rettingen. D5–D10: det som ikke brukes noe sted i
repoet, tas bort, etter et søk i hele repoet. Det testene bruker, og
`src/meldinger.py` (Epic 6), står, og spesifikasjonen sier hvorfor. Ryddingen
(spørsmål 12) tas etter at storyen er flettet, og ikke i denne storyen.

## Det v1.1 gjør

Slått opp på `c2adf7f5`. `kjoer` i `src/fetch_prices.py` kaller
`regn_signalet_i_ettertid` i `finally`, etter alt annet i hentingen, også når
den stopper med en kode, men aldri for en demobase. Steget regner, med
`regn_i_ettertid` i `src/ettertid.py`, et signal for hver børsdag før
inneværende børsdag som har kursene i basen og ingen rad i vurdering. Raden
merkes «i ettertid» og får ingen KI-tekst (FR-601, FR-408). Kveldsraden for en
dato kan fortsatt bare skrives så lenge datoen er inneværende børsdag (AD-7).

Altså: en dag uten kveldsrad blir ikke stående uten signal. Når datoen ikke
lenger er inneværende børsdag og kursene står i basen, regner siste steg i en
henting signalet i ettertid. Det kan være den samme kjøringen: går den over
midnatt til en ny børsdag, er datoen ikke lenger inneværende når steget
kjøres.

## D1–D4: meldingene

| Funn | Hvor | Teksten før | Rettingen |
|---|---|---|---|
| D1 | `_stoppet_ved_midnatt` i `src/fetch_prices.py` | «… er stoppet etter N rader, og datoen regnes ikke på nytt.» | Sier at kveldsraden ikke skrives, og hva som skjer med dagen etterpå (D2) |
| D2 | `_kan_skrives_til` i `src/fetch_prices.py`, brukt seks steder, ett av dem i `_stoppet_ved_midnatt` | «En rad for DATO kan bare skrives så lenge den er inneværende børsdag (AD-7).» | «Kveldsraden for DATO …», og en setning om signalet i ettertid |
| D3 | Docstringen til `tilstand` i `src/tilstand.py` | «Hullet er endelig først når dato ikke lenger er inneværende børsdag (AD-7).» | Ingen kveldsrad etter det, men et signal i ettertid gir ETTERTID, og hullet står bare når det ikke kan regnes |
| D4 | Utskriften fra `--les-inn` (`les_inn`), og de to meldingene i hentingen som viser til `--les-inn` når basen feilet | `les_inn` sier ingenting om vurderingene. Meldingene sier at «--les-inn skriver ingen» | `les_inn` sier at innlesingen ikke skriver vurderinger, og at dagene uten rad får signalet i ettertid ved neste henting. Meldingene i hentingen får det samme gjennom D2 |

Meldingen om fila som finnes ved første henting, ble rettet i 2.17
(`test_meldingen_om_les_inn`) og røres ikke. Ingen meldinger får kurser, volum
eller annet fra kildene (regel 16). Atferden endres ikke, bare tekstene.

## D5–D10: det som ikke brukes

Søkt med `git grep` i hele repoet på `c2adf7f5`, også i `start/`, `docs/`,
README-en, testene, `Dockerfile`, `compose.yaml` og `.github/`.

| Funn | Hva | Brukt av | Utfall |
|---|---|---|---|
| D5 | `MinneNotatlagerMedKjoep` i `src/notater.py` | Ingenting. Docstringen sier «for testene», men ingen test importerer den | Tas bort |
| D6 | `RETNINGENE` i `src/dagsgrunnlag.py` | Ingenting | Tas bort |
| D7 | `nyeste_leser` i `src/lagring_fil.py` | Testene | Står, fordi testene bruker den |
| D8 | `ANDEL_NEGATIV`, `ANDEL_POSITIV`, `ENDRINGSFORSLAGET_13_10`, `MAALINGER`, `MAALTE_AKSJER`, `MAALTE_BOERSDAGER`, `MAALT_PERIODE` og `TAVLA_STYRKEN` i `src/hjelpetekster.py` | Bare testene (søkt med `git grep -w` i `src/`, malene og `start/`) | Står, fordi testene bruker dem |
| D9 | `src/meldinger.py` | Ingenting i appen, ubrukt med vilje | Står, for Epic 6 (svaret kl. 15:39) |
| D10 | `ikon-16.png`, `ikon-48.png`, `ikon-192.png` og `ikon-512.png` i `src/static/` | Ingen mal, men `src/ikon.py` lager dem (`IKON_STOERRELSER`), og `test_filene_i_repoet_er_det_modulen_lager` og `test_stoerrelsene` i `tests/test_ikonet_og_snarveien_3_6.py` leser dem | Står, fordi modulen lager dem og testene bruker dem. Å ta dem bort ville kreve en endring i `src/ikon.py` og testene, og det er ikke svaret |

## Testene

Nye tester i `tests/test_meldingene_9_15.py`, én for hver melding. Hver av dem
skal feile mot teksten før rettingen, og kjøringen før rettingen føres her.

- D1: `_stoppet_ved_midnatt` sier ikke «regnes ikke på nytt», og sier «i ettertid».
- D2: `_kan_skrives_til` sier «Kveldsraden» og «i ettertid».
- D3: docstringen til `tilstand` sier ikke «Hullet er endelig først», og nevner ETTERTID.
- D4: `les_inn` sier i utskriften at innlesingen ikke skriver vurderinger, og at
  dagene uten rad får signalet regnet i ettertid ved neste henting. Testen
  bruker `lag_bilde` i en midlertidig mappe, som `TestInnlesing`, og ingen
  kall.
- D5 og D6: navnene finnes ikke i modulene (`hasattr`).

**Kjøringen før rettingen:** kl. 16:25, med testfila på spesifikasjonen
(`42730a24`) og koden før rettingen. Alle seks feilet: D1 på «regnes ikke på
nytt», D2 på starten «Kveldsraden for …», D3 på «Hullet er endelig først», D4
på «Innlesingen skriver ingen vurderinger (AD-7)», og D5 og D6 på `hasattr`.
Etter gjennomgangen sjekker testene også forbeholdet om lista og kursene
(ECH1), rettingen i D1 (VG1), at utskriften fra `--les-inn` ikke har tall med
desimaler (VG2), og at innlesingen ikke nevner signalet i ettertid når basen
feilet (VG2).

Lokalt kjøres bare testfilene storyen rører og `--dokumentene`. Hele settet
kjøres i CI. `src/fetch_prices.py` kjøres ikke, bare testene.

## Bildene

Storyen endrer ingen mal og ingen fil i `src/static/`. Avtrykkene bak bildene i
`tests/test_docker.py` regnes av malene og noen moduler, blant dem
`src/dagsgrunnlag.py` og `src/tilstand.py` (gjennomgangen, VG3). Begge er endret,
så avtrykkene ble endret. Alle 18 bildene ble tatt på nytt kl. 16:37–16:38 og
igjen kl. 16:50–16:51 etter rettingene, med demobasen i en midlertidig mappe,
demoserveren på en ledig port (62931 og 62933, aldri 8000) og skriptet og
jobblista fra 2.17. Alle 18 er byte for byte de samme som i `docs/appen/` og
`docs/appen/mobil/`, så bare avtrykkene er satt på nytt (`303841a9` og
`d2f3f5e3`), og ingen bilder er endret. Demoserveren er stoppet.

## Grenser

- Ingen API-kall utover kvotesjekken, og `src/fetch_prices.py` kjøres ikke.
- `data/`, `_privat/` og `local-tests/` røres ikke, og den ekte versjonen startes
  ikke. Testene bruker bare testbaser (regel 22).
- Atferden i hentingen endres ikke, bare tekstene.
- ruff før hver commit som endrer `src/` eller `tests/` (regel 23).

## Gjennomgangen 16.11

Én leser med Blind Hunter, Edge Case Hunter og Verification Gap, bare med
lesing, på `303841a9`. 9 funn: 2 på middels og 7 lave.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| ECH1 | middels | Meldingene i `_kan_skrives_til` og `les_inn` lovet signal i ettertid uten forbehold, men `regn_i_ettertid` gir ingen rad for en aksje utenfor lista, med for få kurser eller uten kursene for dagen, og to kallsteder gjelder nettopp basen som feilet | Rettet: «for aksjene i lista som har nok kurser i basen til og med dagen», som `docs/hjelp.md`, med test (`d2f3f5e3`) |
| BH1 | middels | D10: svaret kl. 15:39 nevner ikonfilene «som ingenting viser til», men spesifikasjonen lar dem stå fordi `src/ikon.py` lager dem og testene leser dem | **Står åpent, følger av et svar (regel 25).** Spørsmål 1 under |
| ECH2 | lav | Docstringen i `tilstand.py`: «første rad i tabellen» og «hullet står bare der …» | Rettet: «første kveldsrad», og hullet står til en henting har regnet signalet (`d2f3f5e3`) |
| ECH3 | lav | Utskriften fra `--les-inn` sier ingenting om inneværende børsdag | Står: meldingen gjelder dagene før inneværende børsdag og sier det. Hva som skjer med inneværende dag, er hentingens sak og uendret |
| VG1 | lav | D1-testen sjekket ikke selve rettingen | Rettet (`d2f3f5e3`) |
| VG2 | lav | D4-testen sjekket ikke regel 16, og ikke tilfellet der basen feilet | Rettet, med en ny test (`d2f3f5e3`) |
| VG3 | lav | «Bildene» sa at avtrykkene bare regnes av malene, og kjøringen før rettingen sto bare i commit-meldingen | Rettet her |
| VG4 | lav | `90d93016` alene feiler avtrykkstestene, rettet i `303841a9` | Står: PR-en squash-flettes, så mellomcommiten kommer ikke på main |
| BH2 | lav | `AVTRYKK_BAK_BILDET` manglet en 9.15-kommentar | Rettet (`d2f3f5e3`) |

## Spørsmål til gruppen

1. **BH1: ikonfilene `ikon-16.png`, `ikon-48.png`, `ikon-192.png` og
   `ikon-512.png` (middels, følger av svaret kl. 15:39).** Ingen mal viser til
   dem, men `src/ikon.py` lager dem (`IKON_STOERRELSER = (16, 32, 48, 180, 192,
   512)`), og `test_filene_i_repoet_er_det_modulen_lager` og `test_stoerrelsene`
   i `tests/test_ikonet_og_snarveien_3_6.py` leser dem. Svaret sier både at
   ikonfilene som ingenting viser til, tas bort, og at det testene bruker,
   står. *Forslag:* de står, som nå, fordi modulen og testene bruker dem. Det
   andre valget er å ta dem bort med `IKON_STOERRELSER = (32, 180)` i
   `src/ikon.py` og de to testene, i denne storyen. `ikon.ico` lages av
   `ICO_STOERRELSER` uten filene og endres ikke.

Spørsmål 1 er på middels og følger av et svar, så det står åpent til gruppen
har svart (regel 25). PR-en stopper ved grønn CI og flettes ikke før det.

## Kontroll

- [x] D1–D4 rettet, med en test for hver som feilet mot teksten før rettingen
- [x] D5 og D6 tatt bort, og D7–D10 står med grunn
- [x] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt: de 25 testfilene som importerer modulene, kl. 16:27–16:36 (1428 bestått, og 4 i `tests/test_docker.py` feilet på avtrykkene, satt på nytt i `303841a9`); etter gjennomgangen `test_meldingene_9_15.py`, `test_tilstand.py`, `test_docker.py`, `test_fetch_prices.py`, `test_ettertid_2_17.py`, `test_etterfyllingen_2_4.py` og `test_notater.py` kl. 16:44–16:50 (711 bestått, de 4 avtrykkene satt på nytt i `d2f3f5e3`), og så de tre første på nytt (195 bestått); `--dokumentene` på `82f97c58` kl. 16:52–17:10 (2966 bestått og 7 hoppet over)
- [x] Ingen bilder endret
- [x] Gjennomgangen er tatt
- [ ] CI er grønn i alle jobbene
