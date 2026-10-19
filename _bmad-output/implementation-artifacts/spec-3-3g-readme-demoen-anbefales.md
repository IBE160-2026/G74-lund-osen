---
title: 'Story 3.3 (3.3g): README-en anbefaler demoen, og regelen for omfanget'
type: 'feature'
created: '2026-10-19'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '9c3d8a1'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/product-brief.md'
  - '{project-root}/_bmad-output/planning-artifacts/tilbakemelding-product-brief.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-4-demoversjonen.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-3-3d-readme-ryddingen.md'
---

## Intent

**Problem:** README-en anbefaler den ekte versjonen, mens briefen v8 sier at demoen «viser sensor alt i v1», og tilbakemeldingen 06.10 (punkt 2) ber om at demoen er «den versjonen sensor bruker». Den lokale modellen står uten at det står at den er valgfri. «Neste» under «Status» blander det briefen lover med det den ikke lover, og punktet om lenkene nevner NewsWeb, som appen ikke lenker til (06.10, story 10.5).

**Grunnlaget:** gruppens svar 19.10 kl. 14:46, 14:48 og 16:12 under «Prioritering» i `epics.md`, og instruksjonen 19.10 kl. 16:00 med svaret kl. 16:12. Svaret 14:46 snur anbefalingen i svaret 11.10 kl. 22:32 (`spec-3-4-demoversjonen.md`), og med det «den ekte versjonen er fortsatt anbefalt» i svaret 16.10 kl. 21:16. Rekkefølgen i «Kom i gang» står.

## Kontrollpunktene

- a) Anbefalingen: «Kom i gang» begynner med at demoen anbefales for faglærer og sensor, fordi den ikke trenger nøkkel og viser hovedfunksjonene med faste eksempeldata, også KI-teksten, og at den ekte versjonen er for å prøve løsningen med kurser fra EODHD. «(anbefalt)» tas bort ved den ekte versjonen, og lenkene til ankeret følger med
- b) Den lokale modellen: overskriften og første setning sier at den er valgfri og ikke trengs for demoen eller for å vurdere appen, fordi demoen har ferdig KI-tekst og bare trenger Docker. Innholdet står
- c) Beskrivelsen øverst sier «interesse (handelsvolum)». «Status» begynner med «Prosjektet er under utvikling. Listene under viser hva som er ferdig på main, og hva som gjenstår.» «Neste» deles i «Neste i v1», det briefen lover og som ikke er ferdig, og «Ekstra, hvis tiden rekker», med én setning om regelen kl. 14:48. NewsWeb tas ut av punktet om lenkene. `docs/hjelp.md`, kvalitetssikringen og vurderingsmatrisen følger med, med daterte linjer (regel 19)
- d) Testene, med «Ville feilet hvis»: «Kom i gang» anbefaler demoen for faglærer og sensor; ingen «(anbefalt)» ved den ekte versjonen; delen om den lokale modellen sier at den er valgfri; «interesse (handelsvolum)» øverst; ingen av de ekstra står under «Neste i v1»

## Planen, én commit per punkt

1. a) Første avsnitt i «Kom i gang» begynner med anbefalingen. Overskriften blir «Den ekte versjonen», tabellhodet «| | Demoen | Den ekte versjonen |», og lenken under «Til faglærer» går til `#den-ekte-versjonen`. Testene som bruker overskriften som nøkkel, følger med.
2. b) `<summary>` og første setning i knappen for den lokale modellen. Testene som slår opp knappen på navnet, følger med.
3. c) Beskrivelsen, «Status» og de to listene, og de daterte linjene i `docs/hjelp.md`, `docs/kvalitetssikring.md` og `docs/vurderingsmatrise.md`. Testen for «Status» følger med.
4. d) De nye testene, og mutantene.

## Avgjort i spesifikasjonen

- **Hvilke punkter som er v1.** Briefen v8, «Inne i v1»: kjernen, KI-forklaringen med av/på-bryter, historikk, hovedindeks og «Min liste». Under «The Solution» lenker aksjedetaljen «til selskapets investorside», og under «Data og kilder» kan Gemini, Anthropic eller OpenAI velges med egen nøkkel (svaret kl. 16:12). «Neste i v1» er derfor Min liste (8.3), historikken i aksjedetaljen (2.7), lenken til selskapets egen nettside (10.5) og egen nøkkel (10.7), i den rekkefølgen «Neste» hadde dem.
- **Signaldagene i grafen** (8.8) sto i samme punkt som historikken. Briefen nevner historikk, ikke signaldagene, så punktet deles: historikken under «Neste i v1» og signaldagene under «Ekstra».
- **«Ekstra, hvis tiden rekker»** er signaldagene (8.8), innstillingene med «Vis KI-tekst» (8.10 og 8.10b, svaret 18.10 kl. 11:20), periodevalget, børsometeret og KI-teksten om dagen på forsiden (8.17 og 10.6) og å velge og bytte aksjer (2.11 og 2.12).
- **«(anbefalt)»** settes ikke ved demoen. Overskriften «Demoen» og ankeret `#demoen` står, så lenkene til den ikke endres.

## Avgjort underveis

- **Lenken i «Neste i v1»** heter «Lenken til selskapets investorside», ikke «egen nettside» som i «Neste» før 3.3g og i «Avgjort i spesifikasjonen» over. Briefen v8 sier at aksjedetaljen lenker «til selskapets investorside», og story 10.5 sier det samme etter rettelsen 06.10 (gjennomgangen, BH2 og VG1).
- **Setningen om regelen kl. 14:48** er «Det som står under «Ekstra», er ikke lovet i briefen og kommer bare med hvis det er ferdig og testet før README-prøven, senest én uke før innleveringen.» Den første formen hadde to «før» etter hverandre og «flettes» (BH5).
- **De daterte linjene** i `docs/hjelp.md` og `docs/kvalitetssikring.md` om punkt a og b står i commiten for punkt c, som instruksjonen samler dem under.

## Mutantene

Én om gangen med `-x` på `tests/test_docker.py` og `tests/test_readme.py`, i en fersk klon av `a97293d` med `core.autocrlf=false`, med kopi av README-en før og sha256 mot HEAD etter hver, og `git status` tom etter hver. Alle ble også kjørt mot `TestReadmeDemoenAnbefales` alene, og alle ble fanget der også. M1–M3 er fra instruksjonen. M2 er kjørt i to former. N1–N3 er for rettingene. Med `-x` stopper kjøringen på første test som feiler, så for M1 og M2a er det en eldre test som står først:

- M1, «Vi anbefaler den ekte versjonen.» tilbake etter anbefalingen: `test_tabellen_nevner_begge_og_hvilken_som_er_anbefalt`, og alene `test_kom_i_gang_anbefaler_demoen_for_faglaerer_og_sensor`.
- M2a, «(valgfri)» tatt bort fra overskriften: `test_readme_lover_0_kall_bare_naar_basen_har_kursene`, og alene `test_delen_om_den_lokale_modellen_sier_at_den_er_valgfri`.
- M2b, «valgfri» tatt bort fra første setning: `test_delen_om_den_lokale_modellen_sier_at_den_er_valgfri`.
- M3, «Signaldagene i kursgrafen» flyttet til «Neste i v1»: `test_ingen_av_de_ekstra_staar_under_neste_i_v1`.
- N1, «Likevel anbefaler vi den ekte versjonen.» etter anbefalingen: `test_kom_i_gang_anbefaler_demoen_for_faglaerer_og_sensor`.
- N2, «egen nettside» tilbake i stedet for investorsiden: `test_status_uten_storynumre_og_uten_kommando`, og alene `test_ingen_av_de_ekstra_staar_under_neste_i_v1`.
- N3, børsometeret flyttet inn i et punkt under «Neste i v1» («Min liste og børsometeret»): `test_ingen_av_de_ekstra_staar_under_neste_i_v1`.

## Gjennomgangen

Gjennomgang 19.10 på diffen `9c3d8a1..364b781`. Linsene var Blind Hunter (BH, 17 funn, bare diffen), Edge Case Hunter (ECH, 11, 33 prøver i en klon, som var ren etterpå) og Verification Gap (VG, 10). Ingen av dem kjørte hele testsettet, en server eller et nettkall. Tre funn hadde dom medium, og alle er rettet i `a97293d`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH4 | Det gamle ankeret ble bare sjekket i README-en og hjelpen | medium | rettet: alle `.md` under `docs/` og `_bmad-output/`, utenom dagsfilene. Ingen lenke dit finnes i dag |
| BH2, VG1 | «egen nettside» der briefen v8 og 10.5 sier investorside | medium | rettet: «Lenken til selskapets investorside», og testene |
| ECH1 | Testen stoppet bare «anbefaler den ekte», ikke «Likevel anbefaler vi …» eller «… anbefales» | medium | rettet: «anbefal» står bare én gang i README-en, og ikke i hjelpen utenom de daterte linjene |
| ECH2 | «Anbefalt» uten parentes i tabellen slapp gjennom | low | rettet med ECH1 |
| ECH3 | Hjelpen ble ikke sjekket for en anbefaling | low | rettet med ECH1 |
| BH3 | Hovedindeksen mangler under «Neste i v1» | low | uten endring: den er ferdig og står under «Ferdig». Børsometeret er 8.17, som briefen ikke nevner |
| BH4 | «for å vurdere appen» mot «Ferdig» om den lokale modellen | low | avvist: ordlyden står i instruksjonen |
| BH5 | Setningen om regelen var tung, med to «før» og «flettes» | low | rettet, se «Avgjort underveis» |
| BH6 | Første setning i «Status» passer dårlig med «Ekstra» | nit | avvist: ordlyden står i instruksjonen |
| BH7, VG3 | Testen for «(handelsvolum)» sjekket ikke at det står bare øverst | low | rettet: `tekst.count("(handelsvolum)") == 1` |
| BH8 | `.replace` slapp forklaringen gjennom ved et annet navn | low | rettet: bare rett etter det siste navnet |
| BH9 | Innholdet i knappen for modellen sjekkes med to setninger | low | avvist: `test_readme_lover_0_kall_bare_naar_basen_har_kursene` og de andre testene for knappen sjekker mer av innholdet |
| BH10 | Navnet sier «ved den ekte versjonen», testen forbyr «(anbefalt)» overalt | nit | uten endring: ingen av versjonene merkes (se «Avgjort i spesifikasjonen») |
| BH11, VG2, ECH5 | Bare ett ord per punkt under «Ekstra», så «signaldager» og børsometeret slapp gjennom | low | rettet: alle sakene i punktet, og stammen «signaldag» |
| BH12 | Overflødig sjekk og gammelt navn på testen for tabellen | nit | avvist: navnet står, så historikken i kvalitetssikringen stemmer |
| BH13, ECH10 | `startswith` og `==` er sårbare for mellomrom | low | avvist: som de andre testene for README-en |
| BH14, VG10 | Spesifikasjonen var `in-progress` uten mutanter og triage | low | uten endring: de står her nå. Samlingen av punkt c er instruksjonens |
| BH15 | Klokkeslettene i de daterte linjene | nit | uten endring: `updated` og «kl. 16:20» er fra `date`, og stemmer med commiten |
| BH16, BH17 | Tre ord for eksempeldataene, og «raskest» som grunn for rekkefølgen | nit | avvist: ordlyden står i instruksjonen og fra 3.3c |
| VG4 | Ingen test knytter «Neste i v1» til briefen | low | avvist: briefen er låst (regel 17), og en ny versjon gir en ny gjennomgang |
| VG5, ECH11a | Prøve 3 i kvalitetssikringen har det gamle navnet på knappen | low | rettet: datert linje under Prøve 3 |
| VG6 | «Neste tiltak» i matrisen nevner «Neste» | low | rettet: datert *Rettet*-linje under tabellene |
| VG7 | Svaret 16.10 kl. 21:16 under story 3.3 sier at den ekte er «fortsatt anbefalt» | low | rettet: datert linje under svaret |
| VG8 | De daterte linjene kom i commiten etter endringene | low | uten endring: instruksjonen samler dem i punkt c |
| VG9 | «bare trenger Docker», men demoen går også med uv | low | avvist: ordlyden står i instruksjonen, og uv står under «Mer for den som vil» |
| ECH6 | NewsWeb sjekkes bare i de to listene under «Neste» | low | uten endring: det er punktet instruksjonen gjelder |
| ECH7 | En gammel knapp for modellen utenfor «Mer for den som vil» blir ikke fanget | low | avvist: `test_mer_for_den_som_vil_er_lukket` holder knappene der |
| ECH8, ECH9 | Prøvene som ble fanget, og CRLF | – | uten endring: ingen feil |
| ECH11b | Klassen `TestReadmeForNybegynnere` sa «den ekte versjonen (anbefalt)» | low | rettet: «(anbefalt til 3.3g)» |

**Testene:** `uv run pytest` på hele settet på `a97293d`: 2697 bestått og 17 hoppet over, på 340 s.

## Boundaries

- Ingen kode i `src/` endres. Ingen API-kall, `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db`, `data/db/demo.db` og den ekte `.env` røres ikke.
- Ingen linje fjernes fra andre dokumenter enn README-en, utenom status og updated.
- PR-en stopper før flettingen og venter på ja.
