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

Lokalt kjøres bare testfilene storyen rører og `--dokumentene`. Hele settet
kjøres i CI. `src/fetch_prices.py` kjøres ikke, bare testene.

## Bildene

Storyen endrer ingen mal og ingen fil i `src/static/`. Avtrykkene bak bildene i
`tests/test_docker.py` regnes av malene, så `--dokumentene` viser om noe er
endret. Ingen nye bilder hvis ikke.

## Grenser

- Ingen API-kall utover kvotesjekken, og `src/fetch_prices.py` kjøres ikke.
- `data/`, `_privat/` og `local-tests/` røres ikke, og den ekte versjonen startes
  ikke. Testene bruker bare testbaser (regel 22).
- Atferden i hentingen endres ikke, bare tekstene.
- ruff før hver commit som endrer `src/` eller `tests/` (regel 23).

## Kontroll

- [ ] D1–D4 rettet, med en test for hver som feilet mot teksten før rettingen
- [ ] D5 og D6 tatt bort, og D7–D10 står med grunn
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] Ingen bilder endret
- [ ] Gjennomgangen er tatt
- [ ] CI er grønn i alle jobbene
