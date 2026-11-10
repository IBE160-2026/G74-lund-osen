---
title: 'Story 8.7: sjekk 2 og 3 i kursgrafen'
type: 'feature'
created: '2026-11-09'
status: 'done'
route: 'dispatch'
baseline_commit: '1a72810a'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
---

Skrevet 09.11 i ekstravinduet (instruksjonen limt inn kl. 11:00, med tilleggene kl. 11:28, 12:00 og 15:43, som føres i `docs/ai-prompts/2026-11-09.md` i steg 4). Gruppens svar 09.11 kl. 10:30 og 10:43: 2.4, 2.6 med 8.14, 8.7 og 8.9 bygges i dag og flettes onsdag etter brukertesten. Instruksjonen sier for 8.7: «volumet og bevegelsen i grafen, med de oppdiktede tallene i demoen.» Bygget fra head-en til PR #126 (`1a72810a`), på grenen `8-7-sjekk-2-og-3-i-grafen`, i worktreen `G74-lund-osen-8-7`, og stoppet før flettingen. Spørsmålene står åpne til gruppen har svart; forslaget er det som er bygget.

## Spørsmål til gruppen før flettingen

1. **Båndet for sjekk 2.** FR-202 (tillegget 08.10): «et bånd rundt forrige dags `adjusted_close` med standardavviket fra sjekk 2». *Forslag:* for hver dag fra forrige dags kurs ganger (1 − standardavviket) til forrige dags kurs ganger (1 + standardavviket), med standardavviket sjekk 2 ville regnet den dagen, som en lys flate under linjene. Båndet klippes til grafen, så skalaen er den samme som før.
2. **Volumet.** *Forslag:* søylene i et eget felt under datoene, i samme SVG, med en heltrukken strek for medianvolumet og en stiplet for grensen, `VOLUMFAKTOR` ganger medianen, begge regnet for hver dag med det sjekk 3 ville brukt den dagen. Feltet er like høyt i den brede og den smale grafen (`VOLUMFELT`, 84 px), og den smale har det under forklaringen.
3. **Funksjonene.** *Forslag:* `standardavvik` og `medianvolum` i `signalberegning.py`, som `bevegelse` og `interesse` nå bruker, og grafen også. Da er det én funksjon og ett vindu, og en test bytter vinduet i `Parametre` og ser at streken og båndet følger med.
4. **Dagene uten strek.** De første dagene i serien har ikke nok dager før seg, og en dag der medianvolumet er 0, har ingen strek (NFR-08). *Forslag:* streken brytes der, og teksten under grafen sier hvor mange dager i grafen som mangler den.
5. **Teksten.** *Forslag:* teksten under grafen forklarer båndet og strekene med tallene fra `Parametre`, og «Sjekk 2 og 3 tegnes ikke — de står i kortene over.» er tatt bort. Hjelpen får «Hva er båndet og søylene i kursgrafen?».
6. **Andre grafer.** `bygg_graf` tegner båndet og volumet bare når kalleren gir volumfaktoren. *Forslag:* bare aksjesiden, som instruksjonen sier.
7. **Flettingen med 2.6 og 8.14.** Begge endrer `graf.py`, `aksje.html`, stilarket og avtrykkene. *Forslag:* den som flettes sist, får konfliktene løst og avtrykkene og bildet av aksjesiden laget på nytt.

*Svar 2026-11-10 kl. 11:52 (gruppens svar):* alle sju forslagene er godtatt. Rådet anbefalte det. Svaret er ført etter instruksjonen kl. 15:24 i `docs/ai-prompts/2026-11-10.md`.

## Intent

**Problem:** Grafen viser sjekk 1 med snittet, men sjekk 2 og 3 står bare som tall i kortene (FR-202, FR-706).

**Approach:** Punktene i grafen får volumet, medianvolumet, standardavviket og forrige dags kurs for hver dag, regnet med funksjonene sjekkene bruker. `graf.py` tegner båndet og feltet for volumet i samme SVG.

## Delene

### A) Funksjonene
`standardavvik` og `medianvolum` i `src/signalberegning.py`, og `bygg_punkter` i `src/aksjedetalj.py`.
- **Ville feilet hvis:** streken var en median over et annet vindu enn sjekk 3, den siste dagen i grafen ga et annet utslag enn sjekkene, eller en dag før vinduet fikk en median.

### B) Båndet
`_baandet` i `src/graf.py`.
- **Ville feilet hvis:** båndet ikke fulgte standardavviket fra sjekk 2, eller ikke fulgte vinduet i `Parametre`.

### C) Volumet
`_volumet` i `src/graf.py`, og malen.
- **Ville feilet hvis:** søylene sto i en annen SVG enn kursgrafen, grensen ikke var volumfaktoren ganger medianen, eller streken ble tegnet der medianvolumet er 0.

### D) Teksten og hjelpen
`src/templates/aksje.html` og `docs/hjelp.md`.
- **Ville feilet hvis:** teksten ikke forklarte båndet og strekene med tallene fra `Parametre`.

## Grenser

Ingen API-kall, `src/fetch_prices.py` kjøres bare i testene med en falsk henter, og `data/db/ose.db` røres ikke. Ingen migrasjon. Bildet av aksjesiden i demoen er tatt på nytt.

## Bygget 09.11 (ekstravinduet)

Bygget på grenen `8-7-sjekk-2-og-3-i-grafen`, i worktreen `G74-lund-osen-8-7`, fra `1a72810a`. Filene: `src/signalberegning.py`, `src/aksjedetalj.py`, `src/graf.py`, `src/app.py`, `src/templates/aksje.html`, `src/static/stil.css`, «Hva er båndet og søylene i kursgrafen?» i `docs/hjelp.md`, og testene i `tests/test_sjekk_2_og_3_i_grafen_8_7.py`. `test_den_smale_grafen_har_det_samme_som_den_brede` i `tests/test_kursgrafen_smal.py` venter nå høyden med feltet for volumet, med en kommentar om det. Bildet av aksjesiden i demoen er tatt på nytt med DevTools-protokollen, og de åtte andre er byte for byte de samme. Avtrykkene er regnet ut på nytt.

## Mutantene

Én per del på `482ab6dc`, med kopi før og fila lik HEAD etterpå: A (medianen med vinduet fra `STANDARD`, ikke fra `p`) fanget av `test_streken_foelger_vinduet_i_parametre`, B (båndet med to standardavvik) av `test_baandet_er_forrige_kurs_pluss_og_minus_avviket`, C (grensen to ganger medianen) av `test_baand_soeyler_og_streker`, og D (teksten om båndet tatt bort) av `test_i_samme_svg_og_teksten`. Testene for B og D ble skjerpet før mutantene (`482ab6dc`), fordi en dobbel bredde på båndet og en tekst uten båndet ellers ville sluppet gjennom.

## Gjennomgangen 09.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Diffen `1a72810a..482ab6dc`, uten `tests/test_docker.py` og bildet: Blind Hunter med bare diffen (13 funn), og Edge Case Hunter og Verification Gap i samme agent med repoet (6 og 4 funn, med 19 mutanter i en kopi utenfor worktreen). Ingen høye.

**Middels**
- *ECH1, rettet.* Hjelpen sa at den siste dagen i grafen alltid gir det samme utslaget som kortene. Kortene leser vurderingen som ble lagret den kvelden (AD-7), mens grafen regner av kursene som er lagret nå, og kilden justerer dem ved hvert utbytte (FR-406). Hjelpen sier nå at de to er like den kvelden kursene hentes, men kan skille seg litt for en eldre dag.
- *VG1 og BH2, rettet.* At grafen får volumfaktoren fra `Parametre`, var ikke prøvd på siden. Nå `test_grafen_faar_volumfaktoren_fra_parametre`, og mutanten M7 (faktoren 2,0) ble fanget. `parametre` i malene er `STANDARD`, som grafen får.
- *VG2, rettet.* At båndet klippes og at skalaen tar med grensen, var ikke testet. Nå `test_baandet_og_grensen_holder_seg_i_feltet`, og M4 og M15 ble fanget.
- *VG3, rettet.* At vinduene er dagene før, uten dagen selv, ble prøvd med funksjonen mot seg selv. Nå `test_vinduene_er_dagene_foer_uten_dagen_selv`. M13 (medianen med dagen selv) overlevde først, fordi tallene ga samme median, og ble fanget med andre tall.
- *BH1, rettet.* Hver dag regnet av hele serien foran seg. Nå bare vinduet og dagen, med det samme resultatet.
- *BH3 og ECH3, rettet.* Teksten og hjelpen sier nå at standardavviket er av endringene i prosent, ikke i kroner.
- *BH8, ikke reelt.* `Kursrad.volum` er et heltall og kan ikke være `None` (`kursdata.py`).

**Lav**
- *Rettet:* ECH4 (feltet, strekene og teksten står også når alle dagene i grafen har volum 0, `volumfelt`, `test_volum_null_i_hele_grafen`), ECH5 og BH6 (en dag med median alene mellom to hull telles med dagene uten strek), BH4 og ECH2 («ikke noe bånd»), BH11 (testen av siste dag krever at verdiene finnes), VG4 (setningen om dagene uten strek er testet).
- *Ført:* BH5 (båndet brytes ikke ved et hull midt i serien; hull finnes bare i starten, fordi `Kursrad` avviser kurser på null), BH7 (dekket av ECH4), BH9 (feltet har ingen akse og ingen lapp ved musepekeren, og strekene skilles bare ved stipling; skjermleseren får hva feltet viser, og tallene står i kortene), BH10 (testen av `medianvolum` mot seg selv er nå supplert av testen av vinduene), BH12 (båndet prøves ved siste dag og i feltet), BH13 og ECH (den smale grafen: forklaringen slutter over feltet, kontrollert av Edge Case Hunter), ECH6 og VG4 (tallene 20 og 1,5 står i hjelpen som ellers i fila; stiplingen, bredden på søylene og aria-teksten er ikke testet).

Etter rettingen er bildet av aksjesiden tatt på nytt (teksten under grafen er endret), og avtrykkene er regnet ut på nytt.

*Lagt til 2026-11-09 (hele settet i deler, del 1):* to tester i `tests/test_app.py` feilet etter gjennomgangen, og begge hadde rett. `test_grafen_har_heltrukket_snitt_og_navnene_ved_enden` krever at bare hovedindeksen er stiplet (designregler §5), så grensen for sjekk 3 er nå en gul, heltrukken strek, og teksten og hjelpen sier «den gule». Den samme testen krever aria-teksten slik den var, så setningen om båndet og volumet står bare i teksten under grafen. `test_teksten_sier_hva_linja_er_uten_raad` fant «bør» i «børsdagene» i teksten under grafen; teksten sier nå «dagene før». Ingen test er svekket. Bildet og avtrykkene er tatt og regnet ut på nytt.

*Lagt til 2026-11-10:* 8.7 er flettet med PR #135 i `2d0cfc8b` kl. 19:01, låst til head-en `199a3ee8`, etter instruksjonen kl. 15:24 i `docs/ai-prompts/2026-11-10.md` og gruppens svar 10.11 kl. 11:52. Main, med 2.4, 2.6 og 8.14, ble flettet inn i `199a3ee8`. Konfliktene i `src/graf.py`, `src/static/stil.css` og `docs/hjelp.md` var justeringsdagene fra main og båndet og volumet fra grenen på samme sted, og begge står; i `tests/test_docker.py` gjaldt de avtrykkene. Diffen mot main er endringene grenen hadde mot `1a72810a` (spørsmål 7). Avtrykkene er regnet ut på nytt, og alle de ti bildene er tatt på nytt fra demoen med DevTools-protokollen: aksjesiden er ny, med båndet, volumet og justeringsdagene, og de andre er byte for byte de samme. Før flettingen: vurderingen for hver aksje og hver dag i en kopi av `data/db/ose.db` i en midlertidig mappe, regnet med koden på main (`5c08697a`) og på grenen, er lik, 3750 vurderinger og 0 ulike, og sha256 for basen var lik før og etter. Hele settet alene i ni deler 18:44:54–18:57:34: 4907 bestått, 25 hoppet over og 0 feilet, til sammen de 4932 som `pytest --collect-only` finner. CI var grønn på head-en (run 42870268837). Treet på main etter `git pull --ff-only` er likt treet på `199a3ee8`. Ingen funn på middels eller over sto åpne.
