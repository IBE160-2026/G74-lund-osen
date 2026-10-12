---
title: 'Story 2.3b: Kallene som er igjen, brukes på nye forsøk'
type: 'feature'
created: '2026-10-10'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '8905b5d4a2d601fa80eee9e362080244fae6c89d'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-3-boersdagskontroll-foer-kvoten-brukes.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Når kveldens fil finnes, stopper hentingen ved filvakten med 0 kall, også når basen mangler dagens kurs for noen aksjer. Kallene som er igjen av dagens 20, blir ubrukt, og dagen får en grunn i stedet for en vurdering for de aksjene (FR-402, NFR-01). Et symbol som feiler, gir dessuten kode 0, mens et svar uten dagens kurs gir kode 1 (ECH1 i 2.3).

**Approach:** Finnes kveldens fil, og basen mangler dagens kurs for noen aksjer, gjør samme kommando et nytt forsøk: den henter bare de aksjene, eldste først, med det som er igjen av dagens kall, aldri bonuskvoten. Forsøket lagres i en egen fil, og en vurdering som lykkes, skriver over grunnen samme børsdag (AD-7). Har basen alle kursene, men mangler vurderinger, skrives de med 0 kall (ECH8).

## Planen

Planen er vist i chatten 10.10 og ført i `docs/ai-prompts/2026-10-10.md` (instruksjonen kl. 19:07 og Utført-linjen). Gruppen sa ja kl. 19:32 med disse svarene, som er beslutninger:

1. **Fila for et nytt forsøk** heter `forsoek<n>-raa-<dato>.json`, med n fra 2: første n som ikke finnes. Den åpnes med modus `"x"`. `kurser-raa-<dato>.json` skrives aldri om (AD-6).
2. **Én runde per kjøring**, eldste først. Gjentakelsen av kommandoen gir «rundt igjen».
3. **En dag børsen er stengt**, står en rad som finnes fra før, som beslutning 1 i spesifikasjonen til 2.5 (02.10 kl. 10:29). Kursene skrives, men grunnen blir stående.
4. **Ingen nye kall etter kl. 23:50** i Oslo.
5. **Kode 1** når en aksje mangler dagens kurs etter kjøringen, også når den feilet (ECH1). Hver eldre test som endres, står i spesifikasjonen med grunnen, og bare koden den venter, endres.
6. **ECH8 tas i 2.3b:** vurderingene som mangler når basen har kursene, skrives med 0 kall.
7. **Flettes tidligst etter at hentingen mandag 12.10 er gjort og kontrollert.** README-prøven fører commiten den brukte.

I tillegg, fra instruksjonen kl. 19:32: Oppgaveplanlegging blir et eget steg etter README-prøven, med egen plan. 2.3b skriver ingen oppskrift for Oppgaveplanlegging, og kontrollpunktet om jobben hver halvtime er flyttet dit. README-en får bare det 2.3b endrer: setningen om dager børsen er stengt, og at samme kommando kjørt igjen senere samme kveld prøver aksjene som mangler. Ingen ny kommando, så tabellen i §9 står, og §9 får en datert linje om teksten som er endret.

## Boundaries & Constraints

**Always:**
- Rekkefølgen før første kall er som i 2.3: demovakten, klokka, tidskontrollen, basen, filvakten, nøkkelen og kvoten. Demovakten kommer fortsatt før alt annet (3.4).
- Et nytt forsøk skjer bare når `kurser-raa-<dato>.json` finnes og basen kan leses og mangler dagens kurs for minst én aksje i lista. Kan basen ikke leses, stopper filvakten som før, med 0 kall og kode 1.
- Bare aksjene som mangler kursen for børsdagen i basen, hentes. Rekkefølgen er eldste `kursserie.hentet` først, en aksje uten serie først av alle, og ellers rekkefølgen i lista.
- Kallene til nye forsøk er det minste av kall igjen av dagens (`/api/user`) og `dailyRateLimit` minus antallet aksjer i lista og indeksen. Lista og indeksen gis som ett antall av den som kaller. I dag er det 15, og 20 − 15 = 5. Med 18 aksjer og indeksen er det 1.
- Bonuskvoten brukes aldri. `/api/user` leses før første kall og etter hvert kall. Står `extraLimit` lavere enn før første kall, eller kan svaret ikke leses etter et kall, stopper forsøket. Kan kvoten ikke leses før første kall, blir det 0 kall og kode 1. Avviser `/api/user` nøkkelen (401, 403), stopper forsøket med kode 1, som i 2.3.
- Ingen nye kall etter kl. 23:50 i Oslo, og heller ikke etter midnatt i Oslo.
- Forsøket lagres i `forsoek<n>-raa-<dato>.json` før basen, med samme form som kursfila og `hentet` fra øyeblikket forsøket startet (AD-6, AD-20). Fila skrives også når alle kallene feilet.
- Kursene går til basen gjennom `skriv_til_basen`, og vurderingene bare for aksjene forsøket fikk skrevet. Et forsøk som feiler igjen, rører ikke raden. En vurdering skriver over en grunn, en grunn aldri over en vurdering (`_UPSERT`, uendret). En dag børsen er stengt, står en rad som finnes (svar 3).
- Kode 1 når en aksje i lista mangler kursen for børsdagen etter kjøringen, både etter hovedhentingen og etter et nytt forsøk.
- ECH8: har basen kursen for børsdagen for alle aksjene, men noen mangler en rad i `vurdering` for dagen, skrives radene som mangler, med 0 kall. Rader som finnes, røres ikke.
- Ny kode tar lista som parameter, med `AKSJEUNIVERS` som standard (`AD-21`, føringen 30.09), og prøves med en liste på 18.
- Utskriften har ingen kurser (regel 16) og aldri nøkkelen.

**Ask First:** endringer i `src/lagring_sqlite.py`, i `boersdag.py` eller i skjemaet.

**Never:** Oppgaveplanlegging og arbeidskopien jobben kjører fra (eget steg). Indekskallet (2.8). Bonuskvoten. En ny kommando eller et nytt flagg. Endring av `kurser-raa-<dato>.json` eller navnet på den.

## I/O & Edge-Case Matrix

| Scenario | Tilstand | Forventet |
|---|---|---|
| Kveldens fil finnes, 2 av 15 mangler dagens kurs | 0 brukt av 20 | 2 kall, eldste først, `forsoek2-raa-<dato>.json`, 2 vurderinger over grunn, kode 0 |
| Som over, en av de 2 feiler igjen | | 2 kall, raden til den som feilet står, kode 1 |
| 6 mangler, 15 brukt av 20 | | 5 kall, de 5 eldste, kode 1 |
| Alle 20 brukt | | 0 kall, kode 1, sier at bonuskvoten ikke brukes |
| `extraLimit` synker etter første kall | | stopper etter det kallet, kode 1 |
| Kvoten kan ikke leses | | 0 kall, kode 1 |
| `forsoek2` finnes | | `forsoek3-raa-<dato>.json` |
| Klokka 23:50 | | 0 kall, kode 1 |
| Lørdag, fredagens fil, en aksje mangler fredag | rad med grunn for fredag | kursen skrives, raden står (svar 3) |
| Basen har alle kursene, 3 rader mangler | | 3 rader, 0 kall, kode 0 |
| Hovedhentingen, ett symbol feiler | | kode 1 (ECH1), og utskriften nevner det |
| Demobase | | stopp før alt annet, 0 kall, kode 1 |
| Liste med 18 og indeksen | 0 brukt | 1 kall til nye forsøk |

</frozen-after-approval>

## Code Map

- `src/fetch_prices.py`:
  - `kjoer`: filvakten (`fil.exists()`) går til `nytt_forsoek` når basen mangler aksjer; basesjekken får ECH8; slutten gir kode 1 for alle aksjer uten dagens kurs (ECH1). Ny parameter `lista`.
  - `tolk_kvote`: deles, så grensen også kan leses (`les_kvotetall`). `tolk_kvote` gir det samme som før.
  - Nye: `kall_til_nye_forsoek`, `forsoeksfil`, `eldste_foerst`, `manglende_vurderinger`, `nytt_forsoek`.
  - `hent_universet`, `manglende_i_basen`, `skriv_til_basen`, `skriv_vurderinger`: lista som parameter. `skriv_vurderinger` får `bare`, aksjene som skal få rad.
  - Tekstene «Et nytt forsoek ... kommer med story 2.3b» byttes.
- `src/lagring_sqlite.py`: uendret. `_UPSERT` bærer AD-7, og `SqliteKurslager` og `SqliteVurderingslager` tar lista allerede (3.4).
- `tests/test_fetch_prices.py`: nye tester i egne klasser. Eldre tester som endres, står i Implementation Notes.
- `README.md`, «Når du henter» og `docs/kvalitetssikring.md` §9: én commit.

## Tasks & Acceptance

**Execution:**
- [x] `src/fetch_prices.py` -- lista som parameter, `les_kvotetall`, `kall_til_nye_forsoek`, `forsoeksfil`, og ECH1 med de eldre testene.
- [x] `src/fetch_prices.py` -- `nytt_forsoek` og filvakten, med testene.
- [x] `src/fetch_prices.py` -- ECH8, med testene.
- [x] `README.md` og `docs/kvalitetssikring.md` §9.
- [x] Gjennomgangen, mutantene, spinen hvis noe der ikke stemmer.

**Acceptance Criteria:**
- Given kveldens fil og en base som mangler dagens kurs for noen aksjer, when kommandoen kjøres igjen, then hentes bare de, eldste først, innenfor kallene som er igjen av dagens, og aldri fra bonuskvoten.
- Given et forsøk som lykkes for en aksje med grunn, when vurderingene skrives, then står vurderingen for børsdagen, og en vurdering som fantes, står.
- Given kveldens fil, when et forsøk lagres, then er `kurser-raa-<dato>.json` byte for byte uendret, og forsøket står i `forsoek<n>-raa-<dato>.json`.
- Given en aksje som mangler dagens kurs etter kjøringen, when kjøringen er ferdig, then er koden 1.
- Given en base med alle kursene og rader som mangler, when kommandoen kjøres, then skrives radene med 0 kall.

## Implementation Notes

**Eldre tester som er endret (svar 5).** Bare koden de venter, er endret, og grunnen står ved hver. 11 testfunksjoner, 36 testkjøringer, alle i `tests/test_fetch_prices.py`:

| Test | Endret | Grunn |
|---|---|---|
| `TestSkriverIkkeOver::test_tom_katalog_gir_ny_fil_som_kan_leses_og_er_uten_noekkel` | venter kode 1, og fila slås opp på navnet i stedet for å komme fra `kjoer` | DNB feiler (ECH1). Fila står som før |
| `TestSvarMedFeilForm::test_ingen_aksje_forsvinner_uten_aa_staa_i_feil` (26 kjøringer) | venter kode 1, fila slås opp på navnet | DNB har feil form (ECH1) |
| `TestSvarMedFeilForm::test_tom_serie_forsvinner_heller_ikke_uten_aa_staa_i_feil` | som over | DNB gir tomt svar (ECH1) |
| `TestHentingenSkriverBasen::test_symbol_som_feilet_faar_ingen_rad_i_ny_base` | venter kode 1 | DNB feiler (ECH1) |
| `TestHentingenSkriverBasen::test_symbol_som_feilet_beholder_gammel_serie_og_tid` | venter kode 1 i kjøring nummer to | DNB gir tomt svar (ECH1) |
| `TestHentingenSkriverBasen::test_hentingen_og_innlesingen_gaar_samme_vei` | spionen tar også `lista` | `kjoer` gir lista til `skriv_til_basen` (AD-21). Det spionen sammenligner, er det samme |
| `TestVurderingenISammeKjoering::test_symbol_som_feilet_i_hentingen_faar_en_rad_med_grunn` | venter kode 1 | DNB feiler (ECH1) |
| `TestVurderingenISammeKjoering::test_grunn_skriver_ikke_over_vurderingen_fra_tidligere_i_dag` | venter kode 1 i kjøring nummer to | DNB feiler (ECH1) |
| `TestVurderingenISammeKjoering::test_utskriften_har_antall_dag_og_grunner_men_ingen_kurser` | venter kode 1, fila slås opp på navnet | DNB feiler (ECH1) |
| `TestBasenAvgjoer::test_basen_mangler_en_aksje_og_da_hentes_det` | første kjøring venter kode 1 | DNB feiler (ECH1) |

**Eldre tester som er endret av det nye forsøket.** Filvakten stopper ikke lenger en kjøring når basen mangler dagens kurs for noen aksjer. Tre tester prøvde at den gjorde det. De får en kvote der dagens 20 kall er brukt, så det nye forsøket bruker 0 kall, og prøver fortsatt at fila står og at koden er 1:

| Test | Endret | Grunn |
|---|---|---|
| `TestSkriverIkkeOver::test_dagens_fil_finnes_og_ingen_kall_brukes` | kvoten med 20 brukt, og teksten «finnes og skrives aldri om» og «0 kall brukt» i hver sin linje | basen finnes ikke, så alle mangler, og det blir et nytt forsøk |
| `TestHelgen::test_loerdag_naar_fredagens_fil_finnes_gir_0_kall_og_sier_hvorfor` | nøkkelen og kvoten med 20 brukt i stedet for funksjonene som feiler testen | det nye forsøket leser nøkkelen og kvoten |
| `TestSvaretIkkeFraBoersdagen::test_ny_kjoering_samme_kveld_gir_0_kall` | som over | som over |

Totalt er 14 eldre testfunksjoner endret, 39 testkjøringer.

*Rettet 2026-10-10 kl. 20:57:* tallene over er feil (BH1 i gjennomgangen). Den første tabellen har 10 testfunksjoner, ikke 11, og `test_ingen_aksje_forsvinner_uten_aa_staa_i_feil` har 27 kjøringer, ikke 26 (`AVVISTE` i `tests/eodhd_serier.py`). Det gir 10 funksjoner og 36 kjøringer for svar 5, og totalt 13 eldre testfunksjoner og 39 kjøringer. Etter gjennomgangen er `test_dagens_fil_finnes_og_ingen_kall_brukes` strammet til igjen: linjen med 0 kall skal være kvotelinjen i forsøket (ECH8 i gjennomgangen).

**Presisert etter gjennomgangen:** et forsøk som «feiler igjen», er et forsøk der aksjen ikke fikk en serie skrevet (kallet feilet, svaret hadde feil form eller var tomt). Får den en serie uten dagens kurs, er serien skrevet, og raden får grunnen `vurder()` gir, `kurs_ikke_fra_dagen`. Det kan erstatte `symbol_feilet` fra hovedhentingen, fordi en grunn kan skrive over en grunn (`_UPSERT`). Aldri en vurdering. Kjøringen gir kode 1 (VG1).

## Spec Change Log

- **2026-10-12, instruksjonen kl. 22:15 i `docs/ai-prompts/2026-10-12.md`: main flettet inn i grenen før flettingen av PR #28.** Etter PR #30 står ikke «Når du henter» lenger i README-en. Endringen fra denne storyen i teksten om når en kan hente, er ført under «Når kan jeg hente?» i `docs/hjelp.md`. Statuslinja i README-en har flyttet nye forsøk fra Neste til Flettet til main, og testen for «Status» i `tests/test_docker.py` følger. Flettingen ga ingen konflikt i `src/`, og ingen kode er endret for hånd.

## Review Triage Log

Gjennomgang av PR #28 etter `afd5545` (kl. 20:05), Blind Hunter (BH, bare diffen), Edge Case Hunter (ECH) og Verification Gap (VG), som tre uavhengige agenter mot diffen fra `8905b5d`. Rettelsene er `e245619` og `796d4b7`, og det som er utsatt, står i `8c14a17`.

| # | Funn | Dom | Grunnlag | Rute |
|---|---|---|---|---|
| BH5, ECH4 | Forsøket sjekker bare om `extraLimit` sank etter et kall. Bruker en annen kjøring kall samtidig, kan ett kall tas fra bonuskvoten | medium | Stemmer. `apiRequests` ble lest, men ikke sammenlignet med grensen | patch: stopp når `apiRequests` når `dailyRateLimit` (M22) |
| ECH3 | To forsøk samtidig leser samme kvote og kan til sammen bruke mer enn marginen | medium | Stemmer. Ingen lås mellom kjøringer | utsatt: `deferred-work.md`, hører til steget med Oppgaveplanlegging |
| VG1 | Et forsøk som får et svar uten dagen, er ikke prøvd. Med `or False` i `fortsatt` var suiten grønn | medium | Stemmer | patch: test, kode 1 og grunnen `kurs_ikke_fra_dagen` (M21), og presisering i Implementation Notes |
| VG2 | «Eldste først» er bare prøvd for «uten serie før med serie», ikke for ulik `hentet` over to forsøk | medium | Stemmer | patch: to forsøk med sju aksjer, det andre tar de to som ikke ble prøvd |
| VG3 | ECH8-testene teller rader, men sjekker ikke at de er vurderinger | medium | Stemmer | patch: test (M24) |
| ECH5 | ECH8 skriver rader etter midnatt i Oslo, ulikt hovedhentingen | medium | Stemmer: fredag 23:59, og lageret godtar fredag også lørdag | patch: samme midnattssjekk (M25) |
| BH3 | README-en lover «kallene som er igjen av dagens 20», mens koden gir det som er til overs etter hentingen | medium | Stemmer. 10 kall igjen gir 5, ikke 10 | patch: setningen sier 5 med de 15, aldri bonuskvoten og ikke etter kl. 23:50 (`796d4b7`) |
| BH6, ECH2 | En forsøksfil som dukker opp mens forsøket pågår, kaster kallene, selv om navnet er fritt | low | Stemmer | patch: neste ledige n (M23) |
| BH7 | Feiler basen i forsøket, avslutter det uten å si hva som er skrevet | low | Delvis: `skriv_til_basen` sier at fila kan leses inn, men ikke at ingen vurdering er skrevet | patch: samme linje som hovedhentingen |
| ECH1 | `eldste_foerst` kan gi en traceback hvis basen ikke kan leses | low | Stemmer, smalt vindu etter `manglende_i_basen` | patch: kode 1 og 0 kall |
| ECH6 | Etter midnatt sier forsøket «23:50» | low | Stemmer | patch: grunnen sier at det er blitt en ny dag |
| BH9 | Docstringene sier ikke hva `kjoer` gir tilbake med 2.3b | low | Stemmer | patch |
| BH10 | Indeksen (2.8) er ikke merket der antallet gis | low | Stemmer | patch: kommentar ved kallet. `kall_til_nye_forsoek` er prøvd med 19 |
| BH11, VG4 | Testhull: ECH8 som ikke kan lese radene, ECH8 på en lørdag, 403 og alle kallene feiler | low | Stemmer | patch: fire tester |
| ECH8 | Testen for filvakten sjekket «0 kall brukt» i en hvilken som helst linje | low | Stemmer | patch: kvotelinjen i forsøket |
| BH1 | Tallene for eldre tester i spesifikasjonen spriker | low | Stemmer: 10 og 36, ikke 11 og 36, og 27 kjøringer, ikke 26 | Rettet-linje i Implementation Notes |
| BH2 | Mutantene og tallene etter står ikke i spesifikasjonen | low | Stemmer da gjennomgangen ble gjort | Verification under |
| BH4 | Svar 4 sier «etter kl. 23:50», og koden stopper fra 23:50:00 | low | Matrisen sier 0 kall kl. 23:50, og forskjellen er under ett minutt | ikke endret |
| BH8 | ECH8 skriver bare når alle kursene finnes | low | En aksje med dagens kurs har rad etter en hovedhenting som fullfører. Mangler radene likevel, skrives de ved første kjøring der alle kursene er der | ikke endret |
| ECH7 | `nyeste_snapshot` kan velge en forsøksfil hvis kursfila er borte | low | Kursfila slettes aldri (AD-6), og appen leser basen, ikke `nyeste_leser` | ikke endret |
| ECH9 | En lørdag står grunnen og kjøringen gir kode 0 | low | Svar 3, beslutning 1 i 2.5 | ikke endret |

## Verification

## Verification

**Commands:**
- `uv run pytest` -- før: 1269 passed og 16 skipped lokalt, 1285 i CI.

**Mutantene, 10.10 etter `796d4b7`.** Eksakt tekstbytting i `src/fetch_prices.py`, og originalen lagt tilbake etter hver. Mot `tests/test_fetch_prices.py` og `tests/test_tidssone.py` med `-x`, så første test som feiler, står i tabellen. 28 av 28 drept:

| Mutant | Utfall | Første test som feilet |
|---|---|---|
| M1 alle aksjene hentes paa nytt | drept | TestNyttForsoek::test_bare_de_som_mangler_hentes_eldste_foerst |
| M2 en aksje med dagens kurs tas med | drept | TestNyttForsoek::test_bare_de_som_mangler_hentes_eldste_foerst |
| M3 bonusen regnes med | drept | TestNyttForsoekKvoten::test_ingen_kall_igjen_gir_0_kall_selv_med_bonus |
| M3b kallene igjen av dagens regnes ikke med | drept | TestSkriverIkkeOver::test_dagens_fil_finnes_og_ingen_kall_brukes |
| M4 ingen stopp naar extraLimit synker | drept | TestNyttForsoekKvoten::test_stopper_naar_extralimit_synker |
| M5 et forsoek som feiler igjen, skriver en grunn | drept | TestNyttForsoek::test_et_forsoek_som_feiler_igjen_roerer_ikke_raden |
| M6 forsoeket skriver over kursfila | drept | TestNyttForsoek::test_bare_de_som_mangler_hentes_eldste_foerst |
| M6b forsoeksfila begynner paa 1 | drept | TestForsoeksfila::test_foerste_er_forsoek2 |
| M7 kvoten som ikke kan leses, gir kall | drept | TestNyttForsoekKvoten::test_kvote_som_ikke_kan_leses_gir_0_kall[tomt |
| M8 et fast 15 i kallene til nye forsoek | drept | TestNyttForsoekKvoten::test_liste_med_18_gir_2_kall_og_med_indeksen_1 |
| M8b hovedhentingen uten lista | drept | TestListaMedAtten::test_hovedhentingen_med_atten |
| M9 demovakten borte | drept | TestNyttForsoekVaktene::test_demobasen_nektes_foer_alt_annet |
| M10 ingen midnattssjekk foer vurderingene i forsoeket | drept | TestNyttForsoekEtterMutantene::test_fredag_over_midnatt_skriver_ingen_rad |
| M11 ECH8 skriver ikke radene | drept | TestVurderingeneSomMangler::test_radene_skrives_med_0_kall |
| M12 kode 0 naar en aksje feilet | drept | TestSkriverIkkeOver::test_tom_katalog_gir_ny_fil_som_kan_leses_og_er_uten_noekkel |
| M13 rekkefoelgen er lista | drept | TestNyttForsoek::test_bare_de_som_mangler_hentes_eldste_foerst |
| M14 forsoeket skriver alle radene | drept | TestNyttForsoek::test_vurderingen_skriver_over_grunnen_og_bare_den |
| M15 klokka bare ved starten | drept | TestNyttForsoekKlokka::test_klokka_passerer_23_50_under_forsoeket |
| M16 grensen kl. 23:55 | drept | TestNyttForsoekKlokka::test_kl_23_50_gir_0_kall |
| M17 kvoten leses ikke etter kallet | drept | TestNyttForsoekKvoten::test_stopper_naar_extralimit_synker |
| M18 ECH8 skriver over rader som finnes | drept | TestVurderingeneSomMangler::test_rader_som_finnes_roeres_ikke |
| M19 nytt forsoek ogsaa naar basen ikke kan leses | drept | TestNyttForsoekVaktene::test_basen_som_ikke_kan_leses_gir_ingen_forsoek |
| M20 tom forsoeksfil naar ingen kall ble gjort | drept | TestNyttForsoekEtterMutantene::test_ingen_kall_gir_ingen_fil |
| M21 svar uten dagen i forsoeket teller ikke | drept | TestNyttForsoekEtterGjennomgangen::test_svar_som_fortsatt_mangler_dagen_gir_kode_1 |
| M22 ingen stopp naar dagens kall er brukt | drept | TestNyttForsoekEtterGjennomgangen::test_dagens_kall_brukt_opp_underveis_stopper |
| M23 fil som dukker opp, gir ikke neste n | drept | TestNyttForsoekEtterGjennomgangen::test_fil_som_dukker_opp_gir_neste_n |
| M24 ECH8 skriver grunner | drept | TestVurderingeneSomManglerEtterGjennomgangen::test_radene_er_vurderinger |
| M25 ECH8 uten midnattssjekk | drept | TestVurderingeneSomManglerEtterGjennomgangen::test_ny_dag_foer_radene_stopper |

**Suiten:** 1332 passed og 16 skipped lokalt etter `bf41134`, mot 1269 og 16 før (253 passed og 16 skipped i `tests/test_fetch_prices.py`, mot 190 og 16 før). M10 og M20 overlevde første kjøring og ble drept av de to testene i `bf41134`, kjørt på nytt hver for seg. CI på PR #28: se Utført-linjen i dagsfila.
