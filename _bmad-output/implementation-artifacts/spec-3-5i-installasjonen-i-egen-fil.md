---
title: 'Story 3.5 (3.5i): installasjonen i docs/installasjon.md, og «Kom i gang» med de fem stegene'
type: 'docs'
created: '2026-11-08'
status: 'review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '958c27a3'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-5g-kortere-kom-i-gang.md'
  - '{project-root}/README.md'
  - '{project-root}/docs/hjelp.md'
---

## Intent

README-en ryddes etter gruppens svar 07.11 kl. 23:26 under story 3.3 og «Prioritering» i `epics.md`: README-en beholder hva appen er, de fem stegene for dobbeltklikket og én linje om den ekte versjonen. Docker, uv, Linux, «Står du fast?» og «Mer for den som vil» flyttes uendret til `docs/installasjon.md`, og testene følger med. Rådet anbefalte det. Instruksjonen er kl. 10:36 i `docs/ai-prompts/2026-11-08.md`.

## Slik er det i dag (slått opp 08.11 på `958c27a3`)

- «Kom i gang» er linje 58–471 i README-en: anbefalingen av demoen, «Enklest: dobbeltklikk (anbefalt)» med de fem stegene, linja «Første gang», linja «Ekte kurser», linja «Linux», så pilene «Velg vei», «Du trenger», «Med Docker Desktop», «Demoen», «Den ekte versjonen», advarselen mot `docker compose down -v`, «Uten Docker, med uv», «Slik virker dobbeltklikket», «Står du fast?», og «Mer for den som vil» med fem piler: bytte versjon, variablene i `.env`, den lokale modellen, egen nøkkel og hentingen hver kveld.
- Ankeret `den-ekte-versjonen` står på pila med Docker-stegene 5–9. Lenken i demoen er `EKTE_VERSJONEN_URL` i `src/app.py`, `…/G74-lund-osen#den-ekte-versjonen`.
- Det som viser til delene som flyttes: «Til faglærer» (`#med-docker-desktop`, `#demoen`, `#den-ekte-versjonen`), «Status» («README-en med bilder i «Kom i gang»»), «Mappestruktur» (de tre skjermbildene «i «Kom i gang»»), `docs/hjelp.md` (`../README.md#slik-virker-dobbeltklikket` og `../README.md#hentingen-hver-kveld`), tre meldinger i `src/ki_tekst.py` («se «Den lokale modellen» i README-en» og «se «Egen nøkkel til Gemini, Anthropic eller OpenAI» i README-en») og to kommentarer i `.env.example` som brukeren leser.
- Testene som leser delene: mest `tests/test_docker.py` (135 treff på README), `tests/test_dobbeltklikk.py` (16) og noen få andre. `tests/test_readme.py` sjekker at hver lenke i README-en går til en fil som finnes, men ikke ankeret.
- Avtrykkene bak bildene i `docs/appen/` (`tests/test_docker.py`) har `src/app.py`, men ikke `src/ki_tekst.py` eller `.env.example`. Lenken i demoen er den samme etter ryddingen, så `src/app.py` endres ikke, bildene tas ikke på nytt, og ECH7 og BH16 venter fortsatt (`issues.md`).

## Kontrollpunktene

- a) «Kom i gang» i README-en har bare de fem stegene, linja om første gang og linja om den ekte versjonen, med lenke til `docs/installasjon.md`. **Ville feilet hvis** en pil, Docker, uv, Linux, «Står du fast?» eller «Mer for den som vil» sto igjen i README-en.
- b) `docs/installasjon.md` har resten av «Kom i gang» i samme rekkefølge og ordrett, bare med stiene rettet for den nye mappa. **Ville feilet hvis** en linje var endret utover stiene, eller manglet (en test sammenligner med README-en på `958c27a3`, linje for linje, etter at stiene er rettet tilbake).
- c) Linja om den ekte versjonen har ankeret `den-ekte-versjonen`, så `EKTE_VERSJONEN_URL` går dit. **Ville feilet hvis** ankeret sto på en annen linje eller manglet i README-en.
- d) Hver lenke i README-en og `docs/installasjon.md` går til en fil som finnes og til et anker som finnes i den fila. **Ville feilet hvis** én lenke pekte på et anker som er flyttet.
- e) Lenkene i README-en og `docs/hjelp.md`, meldingene i `src/ki_tekst.py` og kommentarene i `.env.example` viser til `docs/installasjon.md` der delene nå står. **Ville feilet hvis** en melding fortsatt sa «i README-en» om en del som er flyttet.
- f) Testene som leste delene i README-en, leser dem i `docs/installasjon.md`, med de samme kravene. **Ville feilet hvis** en test bare ble slettet, eller sjekket mindre enn før.
- g) «Dokumentene» og «Mappestruktur» i README-en lenker til `docs/installasjon.md` (regel 19).

## Planen

1. `docs/installasjon.md` med frontmatter som `docs/hjelp.md`, og resten av «Kom i gang» flyttet ordrett. Stiene rettes: `docs/bilder/readme/` blir `bilder/readme/`, `docs/hjelp.md` blir `hjelp.md`, `docs/kilder-og-rettigheter.md` blir `kilder-og-rettigheter.md`, `start/` blir `../start/`, og ankrene som står igjen i README-en (`#tester`, `#demoen-og-den-ekte-versjonen`), blir `../README.md#…`.
2. README-en: «Kom i gang» som i a), «Til faglærer», «Status», «Dokumentene» og «Mappestruktur» rettet.
3. `docs/hjelp.md`, `src/ki_tekst.py` og `.env.example` rettet.
4. Testene: en felles leser for `docs/installasjon.md`, de som leser delene, flyttet dit, testen for lenker og ankre (d), og testen for at flyttingen er ordrett (b).

## Spørsmål til gruppen før det bygges

*Avgjort 2026-11-08 kl. 11:24 (gruppens svar):* forslagene i spørsmål 1–3 er godtatt, og rådet anbefalte alle tre. Overskriften «Enklest: dobbeltklikk (anbefalt)» med ankeret står over de fem stegene i README-en, og setningen om demoen flyttes først i `docs/installasjon.md`. Setningen «Velg versjon», som flyttes, sier «øverst i README-en». `docs/installasjon.md` er levende som README-en og `docs/hjelp.md`, med en ny linje om det i regel 19 i `CLAUDE.md`. Svaret er ført etter instruksjonen kl. 11:27 i `docs/ai-prompts/2026-11-08.md`.

Det er tre ting sensor vil se som svaret kl. 23:26 og instruksjonen ikke avgjør:

1. **Overskriften «Enklest: dobbeltklikk (anbefalt)» og setningen «Vi anbefaler demoen for faglærer og sensor …».** Etter ordlyden flyttes begge, fordi bare stegene og de to linjene står igjen. Da står overskriften i `docs/installasjon.md` over pilene, uten stegene den gjaldt, og ankeret `enklest-dobbeltklikk-uten-docker`, som «Til faglærer» og hjelpen lenker til, havner der. **Forslag:** overskriften og ankeret står over de fem stegene i README-en, og setningen om demoen flyttes først i `docs/installasjon.md`.
2. **«øverst» i en setning som flyttes.** «Velg versjon. Klikk på pila for den versjonen du vil prøve. [Tabellen «Demoen og den ekte versjonen»](#demoen-og-den-ekte-versjonen) øverst viser forskjellen.» i pila «Med Docker Desktop» viser til tabellen øverst i README-en, men står nå i en annen fil. Uendret leses «øverst» som toppen av `docs/installasjon.md`. **Forslag:** «øverst i README-en», og ellers ingen ordendringer.
3. **Er `docs/installasjon.md` et levende dokument, som README-en og `docs/hjelp.md`?** Regel 19 sier at de andre dokumentene får en Rettet-linje. Teksten er README-tekst og leses av brukere. **Forslag:** ja, rettes der den står, med historikken i git, og en linje i regel 19 i `CLAUDE.md` i samme PR.

Linja om den ekte versjonen blir, med forslaget i 1:

> <a name="den-ekte-versjonen"></a>**Ekte kurser:** dobbeltklikk «Start den ekte versjonen» i stedet for «Start demoen». Den spør etter en gratis nøkkel fra EODHD første gang, og starter bare i en kopi fra ZIP-fila, ikke i en klon. Docker, uv, Linux, hjelp når du står fast og mer for den som vil: [Installasjonen](docs/installasjon.md).

Lenken i demoen lander da på denne linja, ikke på Docker-stegene 5–9, som før ryddingen. Dobbeltklikket spør selv etter nøkkelen, så stegene for nøkkelen trengs ikke der.

## Gjennomgangen

Fylles ut etter at det er bygget.

*Rettet 2026-11-08 kl. 12:45:* kontrollpunkt b) og punkt 4 i planen sier at en test sammenligner med README-en på `958c27a3`. Instruksjonen kl. 11:27 sier at b) sjekkes én gang under byggingen og ikke som en fast test, fordi `docs/installasjon.md` er levende (svaret kl. 11:24). Sjekken står under.

**b), sjekket én gang 08.11 på arbeidskopien før `7be9aac8`.** Skriptet tar `git show 958c27a3:README.md`, linje 62 (anbefalingen), en tom linje og linje 78–471 (fra «Linux» til slutten av «Mer for den som vil»), og sammenligner linje for linje med alt under `# Installasjonen` i `docs/installasjon.md`, etter at stiene er rettet tilbake: `](bilder/readme/` til `](docs/bilder/readme/`, `](hjelp.md` til `](docs/hjelp.md`, `](kilder-og-rettigheter.md` til `](docs/kilder-og-rettigheter.md`, `](../start/)` til `](start/)`, `](../README.md#` til `](#`, og «øverst i README-en viser» til «øverst viser» (spørsmål 2). Resultatet: 396 linjer forventet, 396 i fila, 0 avvik, og 12 linjer med rettet sti. Med stiene rettet tilbake på samme måte gir de seks pilene i `AVTRYKK_I_KOM_I_GANG` avtrykkene fra før (sjekket samme sted), og pilene til demoen og den ekte versjonen har de samme avtrykkene uten noen retting.

**Testene.** Hele settet alene, med grense på 15 minutter: 4573 bestått, 24 hoppet over og 0 feilet tre ganger: 11:57:43–12:11:01 (3,5 GB ledig) før `7be9aac8`, 12:12:35–12:25:45 (3,6 GB) før `059a0ea9`, og 12:31:44–12:44:17 (3,8 GB) før `4d1656f7`.

**Mutantene**, én om gangen, med kopi før og sha256 mot HEAD etter, alle like:

| Kontrollpunkt | Mutant | Test | Utfall |
|---|---|---|---|
| a) | linja «Linux» tilbake i «Kom i gang» i README-en | `TestHovedveien::test_dobbeltklikket_staar_foerst_og_ikke_bak_en_pil` | drept |
| c) | ankeret tatt av linja om den ekte versjonen | samme | drept |
| d) | «Til faglærer» lenker til `#med-docker-desktop` i README-en | `test_readme.py::test_hver_lenke_i_readme_og_installasjonen_gaar_til_en_fil_og_et_anker_som_finnes` | drept |
| e) | meldingen «Start Ollama» sier «i README-en» | `TestInstallasjonen::test_meldingene_og_kommentarene_viser_til_installasjonen` | drept |
| f) | `test_stopp_i_begge_versjonene` gjort om til en hjelpefunksjon | `TestInstallasjonen::test_testene_leser_delene_i_installasjonen_og_ingen_er_borte` | overlevde på `7be9aac8`, drept fra `059a0ea9` |
| f) | samme test med nytt navn | samme | drept på `4d1656f7` |
| g) | lenketeksten «Installasjonen» i «Dokumentene» endret | `TestInstallasjonen::test_dokumentene_og_mappestrukturen_lenker_til_installasjonen` | drept |

Gjennomgang 08.11 av diffen `643d32cd..059a0ea9` (grenen etter flettingen av main), med Blind Hunter (BH, 16 funn), Edge Case Hunter (ECH, 5 funn) og Verification Gap (VG, 3 funn):

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1 | Ankeret `den-ekte-versjonen`, som lenken i demoen og «Til faglærer» går til, står nå på linja om dobbeltklikket, ikke på Docker-stegene 5–9. Den som kjører demoen i Docker, lander på en linje om dobbeltklikket, med lenke videre til installasjonen | medium | **åpent, spørsmål til gruppen** (regel 25): det følger av linja i spesifikasjonen og svaret kl. 11:24. Å la lenken i demoen gå til `docs/installasjon.md#den-ekte-versjonen` endrer `src/app.py`, så bildene i `docs/appen/` må tas på nytt, med ECH7 og BH16 (`issues.md`) |
| BH2, VG1, ECH4 | b) har ingen fast test, og de nye avtrykkene låser bare teksten slik den er nå. Delene under «Mer for den som vil» har ikke avtrykk | low | **står**: instruksjonen kl. 11:27 sier at b) ikke skal være en fast test. b) er sjekket én gang (over), og delene under «Mer for den som vil» hadde ikke avtrykk i README-en heller |
| BH3 | Testen for stegene, kommandoene og lenkene fra før godtar et anker i hvilken som helst av de to filene | low | **står**: d) sjekker hver lenke mot fila den går til |
| BH4 | Testen for g) låste `updated` til 08.11 i en levende fil | medium | **rettet** i `4d1656f7`: formen fra `date`, ikke før `created` |
| BH5 | e) leser bare fire filer | low | **står**: `git grep` etter lenker til ankrene som er flyttet, i sporede filer utenom dagsfilene og loggene, finner bare spesifikasjonen og en docstring. Ingen tekst i `src/` utenom `ki_tekst.py` viser til delene |
| BH6, ECH1, ECH5 | Testen for f) teller testene, men sjekker ikke navnene, som kommentaren sa | medium | **rettet** i `4d1656f7`: `TESTENE_SOM_LESER_DELENE` med de 96 testene som leser delene. Hver av dem må finnes og lese delene, og mutanten f2 dør |
| BH7 | Installasjonen hopper fra `#` til `###` | low | **står**: flyttet ordrett (b) |
| BH8 | Installasjonen sier ikke først hva fila er | low | **står**: anbefalingen står først, etter svaret kl. 11:24 |
| BH9 | Hjelpen sier at stegene 1–4 hører til «Med Docker Desktop», uten å si hvor | low | **rettet** i `4d1656f7`: «i installasjonen». «se «Tester» i README-en» i «Står du fast?» står ordrett (b) |
| BH10 | Navn i testene sier fortsatt «readme» | low | **står**: navnene står, fordi kvalitetssikringen og spesifikasjonene viser til dem |
| BH11 | Noen positive krav leser README-en og installasjonen sammen | low | **står**: a) og d) sier hvor delene står |
| BH12 | Gulvet på 20 lenker med anker i d), mot 27 nå | low | **står**: gulvet hindrer at testen går tom, og hver lenke sjekkes |
| BH13 | a) forbyr «docker compose» og «uv run python» i hele README-en | low | **står**: a) sier at Docker og uv ikke står igjen i README-en |
| BH14 | Svaret kl. 11:24 står to ganger i `epics.md` | low | **står**: instruksjonen sier der svaret kl. 23:26 står, og det står to steder |
| BH15 | Kommentarlinjene i `.env.example` er lengre | low | **står**: kosmetisk |
| BH16 | «Status» sier at installasjonen er ferdig, mens storyen var `in-progress` | low | **rettet** i `4d1656f7`: `review`. «Ferdig» betyr flettet til main, og setningen gjelder når PR-en er flettet |
| ECH2 | `_fra_rota` gjorde `../README.md` uten anker til `#` | low | **rettet** i `4d1656f7` |
| ECH3 | `_seksjon` ga IndexError uten melding | low | **rettet** i `4d1656f7` |
| VG2 | Kommentaren i testen viste til en utsettelse for raden D7 som ikke sto i spesifikasjonen. §9 i `docs/kvalitetssikring.md` sier at kommandoene står i rekkefølgen i README-en | low | **rettet** i `4d1656f7` (kommentaren). **Åpent punkt**: D7 og innledningen til §9 viser til README-en og rettes før README-prøven. Ingen linje fjernes fra kvalitetssikringen i denne PR-en |
| VG3 | Morgensjekken sjekker bare lenkene i README-en, og kommentaren sier «samme logikk som tests/test_readme.py» | low | **åpent punkt**: `.github/scripts/morgensjekk.py` er ikke endret i 3.5i |

**Spørsmål til gruppen etter gjennomgangen:** BH1: skal lenken «Den ekte versjonen» i demoen gå til `docs/installasjon.md#den-ekte-versjonen` (stegene 5–9 med Docker), med nye bilder i `docs/appen/` og ECH7 og BH16 samtidig, i en egen PR? Forslag: ja, i en egen PR etter denne. Til da lander lenken på linja om den ekte versjonen i README-en, som lenker videre.

*Svar 2026-11-08 kl. 12:57 (gruppens svar):* BH1 lukkes. Lenken «Den ekte versjonen» i demoen beholdes som den er, fordi dobbeltklikket er hovedveien. Rådet anbefalte det. Det blir ingen egen PR for lenken, og ECH7 og BH16 står fortsatt i `issues.md`. Med det står ingen funn på middels eller over åpne. Svaret er ført etter instruksjonen kl. 13:00 i `docs/ai-prompts/2026-11-08.md`.
