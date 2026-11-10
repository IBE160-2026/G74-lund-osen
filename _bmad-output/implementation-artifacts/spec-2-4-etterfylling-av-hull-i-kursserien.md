---
title: 'Story 2.4: etterfylling av hull i kursserien'
type: 'feature'
created: '2026-11-09'
status: 'done'
route: 'dispatch'
baseline_commit: '1a72810a'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-1b-basen-aapnes-ett-sted-og-hentingen-skriver-kursene-dit.md'
---

Skrevet 09.11 i ekstravinduet (instruksjonen limt inn kl. 11:00, med tilleggene kl. 11:28, 12:00 og 15:43, som føres i `docs/ai-prompts/2026-11-09.md` i steg 4). Gruppens svar 09.11 kl. 10:30 og 10:43: 2.4, 2.6 med 8.14, 8.7 og 8.9 bygges i dag og flettes onsdag etter brukertesten. Instruksjonen sier for 2.4: «hullet fylles ved neste henting med de samme kallene som ellers, prøvd bare på testbaser.» Bygget fra head-en til PR #126 (`1a72810a`), på grenen `2-4-etterfylling`, i worktreen `G74-lund-osen-2-4`, og stoppet før flettingen. Spørsmålene står åpne til gruppen har svart; forslaget er det som er bygget.

## Spørsmål til gruppen før flettingen

1. **Hva bygges?** Hver henting tar et år bakover for hver aksje og hovedindeksen (`DAGER_TILBAKE` i `fetch_prices.py`) og erstatter hele serien i basen (`erstatt_serie`, AD-5). Et hull fylles derfor alt ved neste henting, og K9 i 2.1b (`test_fire_dagers_opphold_fylles_med_16_kall`) prøver fire dager. Det står også i endringsforslaget 28.09, §4.6: «2.4 står, men kan lukkes med en henvisning dit». *Forslag:* ingen endring i koden. 2.4 får testene for resten av kontrollen i epics.md og et svar i hjelpen.
2. **«15 kall».** Med 2.8 ble det 16, og med lista fra basen (2.11) er det én per aksje i lista og én for hovedindeksen. *Forslag:* kontrollen leses som «de samme kallene som en vanlig kveld», slik instruksjonen sier, og testen sammenligner en kveld etter et hull med kvelden etter.
3. **Hjelpen.** *Forslag:* et nytt spørsmål i `docs/hjelp.md`, «Jeg har ikke hentet på noen dager.», etter «Når kan jeg hente?»: neste henting fyller hullet, og dagene uten henting har ikke signal.
4. **Før neste henting.** Åpnes appen før hullet er fylt, går kurslinja rett over dagene som mangler, og endringen regnes mot forrige rad (gruppens svar 06.11 kl. 09:55 og 12:16). *Forslag:* som før, uten merking av hullet. Det er utenfor kontrollen i 2.4.
5. **Over et år.** Serien er alltid ett år bakover fra dagen, så etter et opphold på over et år er hele serien ny, og kurser eldre enn et år står ikke i basen, som før. *Forslag:* ingen endring.

*Svar 2026-11-10 kl. 11:52 (gruppens svar):* forslagene i spørsmål 1–5 er godtatt. Rådet anbefalte det. Spørsmål 6 står under funnene og kom ikke med i spørsmålet til gruppen kl. 11:52; svaret på det står under spørsmål 6. Svarene er ført etter instruksjonen kl. 15:24 i `docs/ai-prompts/2026-11-10.md`, med svaret kl. 15:30 under den.

## Intent

**Problem:** En bruker som ikke har hentet på en uke, skal se en hel graf etter neste henting, uten at hullet ser ut som en kursbevegelse, og uten at noen vurdering etterfylles (AD-7).

**Approach:** Oppførselen finnes fra 2.1b. Testene i `tests/test_etterfyllingen_2_4.py` prøver resten av kontrollen på testbaser, og hjelpen sier det.

## Delene

### A) Serien byttes i sin helhet
- **Ville feilet hvis:** hentingen bare la til dagene som manglet, så eldre kurser som kilden har justert, og en dag kilden ikke lenger har, sto igjen.

### B) Hovedindeksen
- **Ville feilet hvis:** bare aksjene ble fylt, og hovedindeksen sto med hullet.

### C) De samme kallene
- **Ville feilet hvis:** hullet ble hentet med ett kall per dag som manglet, eller med et annet intervall enn en vanlig kveld.

### D) Ingen vurderinger etterfylles
- **Ville feilet hvis:** hentingen etter hullet skrev vurderinger for dagene i hullet, eller lageret godtok en vurdering for en av dem (AD-7).

### E) Hjelpen
«Jeg har ikke hentet på noen dager.» i `docs/hjelp.md` (regel 19). Ingen side endres, så bildene i `docs/appen/` tas ikke på nytt.

## Grenser

Ingen API-kall, `src/fetch_prices.py` kjøres bare i testene med en falsk henter, og `data/db/ose.db` røres ikke. Ingen migrasjon.

## Bygget 09.11 (ekstravinduet)

Bygget på grenen `2-4-etterfylling`, i worktreen `G74-lund-osen-2-4`, fra `1a72810a`. Ingen endring i `src/`. Testene er i `tests/test_etterfyllingen_2_4.py`, og svaret står i «Jeg har ikke hentet på noen dager.» i `docs/hjelp.md`. Ingen side endres, så bildene og avtrykkene i `tests/test_docker.py` står.

## Mutantene

Én per del på `653d8d0c`, med kopi før og fila lik HEAD etterpå: A (`kurs` skjøtes med `INSERT OR REPLACE` uten `DELETE`) fanget av `test_eldre_rader_er_kildens_nye`, B (indeksen lagres ikke) av `test_hullet_i_hovedindeksen_fylles_ogsaa`, C (intervallet fire dager) av `test_samme_kall_etter_et_hull_som_dagen_etter`, etter at testen regner intervallet av `DAGER_TILBAKE` og ikke av `bygg_intervall` (`fbf4c7ce`), og D (lageret godtar enhver dato) av `test_ad7_stopper_et_forsoek_paa_aa_etterfylle`.

## Gjennomgangen 09.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Diffen `1a72810a..fbf4c7ce`: Blind Hunter med bare diffen (11 funn), og Edge Case Hunter og Verification Gap i samme agent med repoet (5 og 5 funn, med mutanter i en kopi utenfor worktreen). Ingen høye.

**Middels**
- *BH1, BH2, BH3, ECH1, ECH2 og ECH3, rettet.* Hjelpen sa «Neste henting fyller hullet» uten forbehold, og at kurslinja går rett over dagene som mangler. Et hull fra dager uten henting står i enden av serien, så grafen slutter på siste dag som er hentet, og har ingen linje over hullet. Hjelpen sier nå at hentingen må være etter kl. 22 eller i helgen når basen mangler forrige børsdag, at en aksje som feiler, står med hullet til et nytt forsøk eller neste henting, og at hovedindeksen som feiler, står med hullet til neste kveld som henter, fordi den ikke prøves på nytt og en henting som finner aksjenes kurser i basen, ikke henter den (`manglende_i_basen` ser bare på aksjene).
- *BH5 og VG1, rettet.* Testen for indeksen så bare at hullet var fylt. Nå med kildens endrede kurser, og mutanten B2 (`indeks` skjøtes uten `DELETE`), som overlevde i gjennomgangen, ble fanget.
- *VG2, rettet.* `TestNaarHentingenFeiler`: en aksje og hovedindeksen som feiler etter hullet.
- *BH4, rettet.* `test_en_uke_med_helgen`: en uke borte, over helgen.
- *BH11, ikke reelt.* K9 og sitatet fra endringsforslaget 28.09, §4.6, er slått opp (Edge Case Hunter gjorde det samme).
- *ECH1, lagt til 2026-11-10:* det som sto igjen etter rettingen i hjelpen, at hovedindeksen ikke hentes før neste kveld når bare den mangler, ble spørsmål 6. Gruppen avgjorde det kl. 15:30: hovedindeksen hentes også når bare den mangler. Graden er middels som før (regel 25).

**Lav**
- *Rettet:* ECH4 (signalet lagres bare for børsdagen hentingen gjelder, også i helgen), ECH5 (en aksje som er tatt ut av lista, hentes ikke).
- *Ført:* BH6 (den eldste dagen i `endret` er ikke en egen prøve, fordi serien fra mandag alt begynner tidligere), BH7 og VG4 (testen for AD-7 prøver regelen i lageret, som kontrollen i epics.md ber om, ikke noe 2.4 endrer), BH8 (testene bruker `AKSJEUNIVERS`, som er lista i en ny testbase), BH9 (kl. 22:00 sommertid er grensen og godtas), BH10 og VG5 (ett år er prøvd i `test_fetch_prices.py`, `TestIntervall`), VG3 (sidene endres ikke).

*Lagt til 2026-11-09 under spørsmål 4 (gjennomgangen, BH3):* et hull fra dager uten henting står i enden av serien, så grafen slutter på den siste dagen som er hentet, og går ikke over hullet. Forslaget er det samme: ingen merking.

6. **Hovedindeksen etter en feil.** *Lagt til 2026-11-09 (gjennomgangen, ECH1):* feiler hovedindeksen i hentingen etter hullet, henter ingen kjøring den før neste kveld der en aksje mangler kursene, fordi `manglende_i_basen` bare ser på aksjene. *Forslag:* som før, og hjelpen sier det. Å hente indeksen i helgen når bare den mangler, ville bruke et kall som i dag ikke brukes.

*Svar 2026-11-10 kl. 15:30 (gruppens svar):* hovedindeksen hentes også når bare den mangler. Rådet anbefalte forslaget om å la det være som før, men gruppen valgte dette. Det bygges på grenen før flettingen. Svarene er ført etter instruksjonen kl. 15:24 i `docs/ai-prompts/2026-11-10.md`, med svaret kl. 15:30 under den.

## Hovedindeksen alene (svaret 10.11 kl. 15:30)

Bygget 10.11 på grenen, etter at main ble flettet inn (`53c020ff`), etter instruksjonen kl. 15:24 og svaret kl. 15:30 i `docs/ai-prompts/2026-11-10.md`.

- **Hva:** har basen kursen for børsdagen for alle aksjene i lista, men hovedindeksen mangler dagen (`indeksen_mangler`), henter `kjoer` indeksen alene med ett kall (`hent_bare_indeksen`), også i helgen. Før var svaret «Ingenting å hente» med 0 kall.
- **Kvoten:** som et nytt forsøk (2.3b): ingen kall fra kl. 23:50 i Oslo eller etter midnatt, bare kall som er igjen av dagens, aldri bonuskvoten (NFR-01), og 0 kall når kvoten ikke kan leses. Intervallet er det samme som en vanlig kveld.
- **Fila:** svaret skrives først til en egen forsøksfil (`forsoek<n>-raa-<dato>.json`) med indeksen under nøkkelen `indeks` og ingen aksjer (AD-6), og kursfila røres ikke. Indeksen lagres gjennom `skriv_indeksen_til_basen`, aldri i `kurs` eller `vurdering`.
- **Koden:** har basen ikke dagen i `indeks` etterpå (kallet feilet, svaret manglet dagen, eller kvoten eller klokka sa nei), gir kjøringen kode 3, som før. Indeksen hentes før KI-tekstene, så teksten om dagen (10.6) kan lages med den.
  *Lagt til 2026-11-10 (gjennomgangen, ECH3):* det hjelper bare når teksten om dagen også mangler; en tekst som alt er laget uten indeksen, lages ikke på nytt.
- **Uendret:** mangler også en aksje dagens kurs, henter et nytt forsøk bare aksjene, som før, og indeksen hentes av kjøringen etter. Utskriften etter en indeks som feilet, sier nå at en ny kjøring samme kveld henter den, ikke at den står til neste kveld.
- **Hjelpen:** «Når kan jeg hente?» og «Jeg har ikke hentet på noen dager.» i `docs/hjelp.md` sier det nye.
- **Testene:** `TestHovedindeksenAlene` i `tests/test_etterfyllingen_2_4.py`, åtte tester med «Ville feilet hvis». Seks tester i `tests/test_fetch_prices.py` feilet, fordi basen deres manglet indeksen etter `--les-inn`, som ikke leser den. Fem prøver noe annet (vurderingene uten kall, lørdag og en base en versjon bak) og har fått indeksen i basen (`med_indeksen`), så de prøver det samme som før. `test_en_andre_kjoering_samme_boersdag_gjoer_0_kall` prøvde den gamle regelen, at en indeks som feilet, ikke hentes igjen samme kveld. Den prøver nå at en ny kjøring gjør 0 kall når basen har dagen for aksjene og indeksen, og den nye regelen prøves i `TestHovedindeksenAlene`.
- **Dokumentene:** PRD-en (FR-410), epics.md (2.8) og arkitekturen (AD-15, 2.8) sier at et indekskall som feiler, «får ingen ny sjanse». Det gjelder fortsatt i samme kjøring; ingen linje er endret der.

### Mutanten (10.11)

Én mutant på `72aa38d4`, med kopi før og fila lik HEAD etterpå (samme blob-hash, og sha256 lik når CRLF i arbeidskopien regnes som LF): `indeksen_mangler` gir alltid `False`, som før svaret. Fanget av alle åtte testene i `TestHovedindeksenAlene`.

### Gjennomgangen 10.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Diffen `53c020ff..72aa38d4`: Blind Hunter med bare diffen (14 funn), og Edge Case Hunter og Verification Gap i samme agent med worktreen (7 og 7 funn, med 14 mutanter i en kopi utenfor worktreen; 8 overlevde). Én høy.

**Høy**
- *ECH1, rettet.* Kveldsjobben kjører `--maal-omsetning` etter hver henting, og målingen ventet bare når en aksje manglet kursen. Etter en kjøring med kode 3 brukte den kallene som var igjen, så en ny kjøring samme kveld fikk aldri kallet for indeksen. Målingen venter nå også når bare hovedindeksen mangler dagen, til kl. 23:45 som for en aksje (`omsetning.py`), og hjelpen sier det. `test_maaler_ikke_naar_bare_hovedindeksen_mangler`.

**Middels**
- *ECH2 og BH7, rettet.* Hentingen av indeksen leser nøkkelen og kvoten i en kjøring som før bare lagde KI-tekstene. Nå lages KI-tekstene i en `finally`, også når nøkkelen mangler, og en `OSError` fra forsøksfila gir kode 3 i stedet for en krasj. `test_ki_tekstene_etter_indeksen_ogsaa_naar_den_stopper` og `test_en_fil_som_ikke_kan_skrives_gir_kode_3`.
- *BH3, BH4 og BH11, rettet.* Utskriften ba om en ny kjøring «i kveld» også når klokka, kvoten eller nøkkelen sa nei. Nå følger rådet grunnen (`PROEV_INDEKSEN_IGJEN` når kallet ble gjort, `VENT_PAA_INDEKSEN` ellers), og ingen av dem sier «i kveld». Linja før kallet sier «når klokka og kvoten tillater det», og utskriften etter en indeks som feilet, nevner også en dag børsen er stengt. `test_raadet_foelger_grunnen`.
- *BH1, rettet i hjelpen.* Etter `--les-inn`, som ikke leser indeksen, henter neste kjøring indeksen med ett kall. Det er det svaret kl. 15:30 ber om. Hjelpen sa at hentingen bruker 0 kall når basen har kursene, og sier nå «og hovedindeksen».
- *BH2 og ECH7, ført.* En base én versjon bak som mangler indeksen for dagen, migreres når indeksen skrives, som ved enhver henting som skriver. Testen for sjekken (`TestSjekkenLeserEnBaseEnVersjonBak`) prøver at sjekken før kallene ikke skriver, og har fått indeksen i basen, så den prøver det samme som før.
- *BH2 og ECH7, lukket 2026-11-10 som avgjort av gruppen* (svaret kl. 17:43), middels som før (regel 25): en base én versjon bak migreres når indeksen skrives, som ved all henting som skriver, og testen prøver det samme som før. Rådet anbefalte det. Svaret er ført etter instruksjonen kl. 15:24 i `docs/ai-prompts/2026-11-10.md`.
- *VG1, VG2, VG3, VG4 og VG5, rettet med tester.* Nøkkelen som funksjon (`test_noekkelen_som_funksjon`), kvoten fra dagen før i GMT (`test_kvoten_fra_gaarsdagen_er_0_brukt_i_dag`), rekkefølgen indeksen før KI-tekstene (`test_ki_tekstene_etter_indeksen_ogsaa_naar_den_stopper`), basen som feiler (`test_basen_som_feiler_gir_ikke_hentet`), og 401, 500 og et svar som ikke kan leses (`test_kvoten_som_ikke_kan_leses_gir_0_kall_og_ingen_krasj`).

**Lav**
- *Rettet:* ECH4 (klokka sjekkes også rett før kallet), ECH5 (hjelpen sier bare kall som er igjen av dagens, aldri bonuskvoten og ikke etter kl. 23:50, og ikke «de samme vilkårene»; taket fra `kall_til_nye_forsoek` gjelder ikke, fordi aksjene alt har kursene), ECH3 (spesifikasjonen: indeksen før KI-tekstene hjelper bare når teksten om dagen også mangler), VG6 (`test_en_base_uten_tabellen_indeks`), BH12 (`test_ett_kall_igjen_holder`), BH13 (testen krever at indeksen har dagen etter første kjøring).
- *Ført:* BH8 og ECH6 (mangler kilden dagen for indeksen, bruker hver kjøring ett kall av dagens og skriver en ny forsøksfil; det er det svaret ber om, og kvoten setter grensen), BH9 (hovedhentingen med et svar uten dagen for indeksen er som før 2.4, og en senere kjøring henter den nå), BH14 (`INSERT` uten kolonnenavn i testen for en base én versjon bak), VG7 (`open(fil, "x")` er ikke prøvd med en fil som dukker opp underveis; det samme gjelder `nytt_forsoek`).
- *Ikke reelt:* BH5 (`hent_indeksen` fører alltid symbolet i `feil` når det ikke er i `serier`), BH6 (`UlesbarKvote` er en `ValueError`), BH10 (vurderingen bruker ikke indeksen).

### Mutantene etter rettingen (10.11)

Ti mutanter mot `tests/test_etterfyllingen_2_4.py` og `tests/test_omsetning.py`, med kopi før og fila lik før og etter (sha256): de sju som overlevde i gjennomgangen og ikke er ført (M5, M6, M7, M8, M11, M12 og M4), og én for hver av BH3, ECH2 og ECH1. Alle ble fanget. M4 (KI-tekstene før indeksen) slo også av hentingen av indeksen, så den ble fanget av `test_en_senere_kjoering_samme_kveld_henter_den_med_ett_kall`; rekkefølgen prøves av `test_ki_tekstene_etter_indeksen_ogsaa_naar_den_stopper`. Vinduet ble lukket ved en feil kl. 16:42 midt i første kjøring av mutantene; ingen mutant ble liggende, og alle ti ble kjørt på nytt etterpå.

*Lagt til 2026-11-10:* 2.4 er flettet med PR #133 i `2c1a17af` kl. 18:00, låst til head-en `07a3380f`, etter instruksjonen kl. 15:24 i `docs/ai-prompts/2026-11-10.md` og gruppens svar 10.11 kl. 11:52, 15:30 og 17:43. Main ble flettet inn i `53c020ff`, og diffen mot main var endringene grenen hadde mot `1a72810a`. Avtrykkene i `tests/test_docker.py` besto, så bildene er ikke tatt på nytt. Hele settet alene i ni deler 17:46:07–18:00:29: 4869 bestått, 31 hoppet over og 0 feilet, til sammen de 4900 som `pytest --collect-only` finner. CI var grønn på head-en (run 42857890383). Treet på main etter `git pull --ff-only` er likt treet på `07a3380f`. Ingen funn på middels eller over sto åpne.
