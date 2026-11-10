---
title: 'Story 8.11c: «Utenfor målingen» med medianen av kursene'
type: 'feature'
created: '2026-11-09'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '78a45186'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-8-11b-de-15-i-bransjelistene.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-12-velge-og-bytte-aksjer.md'
---

Skrevet 09.11 i ekstravinduet (instruksjonen limt inn kl. 11:00, med tilleggene kl. 11:28 og 12:00, som føres i `docs/ai-prompts/2026-11-09.md` i steg 4). Gruppens svar 09.11 kl. 10:23: spørsmål 9 i 8.11b blir et punkt i `issues.md` til senere. Kl. 10:47 og 10:53: de fire små tingene fra `issues.md` tas nå. Tillegget kl. 11:28: de tre små PR-ene bygges først og flettes i natt av en egen instruksjon. Endringen bygges fra head-en til PR #129 (`78a45186`), på grenen `8-11c-utenfor-maalingen`, i worktreen `G74-lund-osen-8-11c`, og stoppes før flettingen. Spørsmålene står åpne til gruppen har svart; forslaget er det som er bygget.

## Spørsmål til gruppen før flettingen

1. **Nummeret.** *Forslag:* story 8.11c, etter 8.11 og 8.11b, fordi endringen er spørsmål 9 i 8.11b. Den føres i `epics.md` i steg 4.
2. **Hvilke aksjer?** *Forslag:* de samme som regnes av kursene i de ferdige listene: alle aksjene i `aksje` som står i `boersliste`, i lista eller tatt ut (spørsmål 1 i 8.11b, utvidet etter ECH1). For dem gjelder medianen av kursene. De andre har den siste målingen i `omsetning` (2.13), som før. Det gjelder også en aksje som venter på henting, fordi den ikke er i `aksje` ennå.
3. **Hvor?** *Forslag:* merket ved navnet i oversikten, på aksjesiden og i børsometeret, «Dine egne aksjer» og «Din egen liste», og omsetningen på «Følg en aksje», både for en valgt aksje og i søket. Da sier alle sidene det samme tallet som de ferdige listene.
4. **Teksten.** For en median av kursene sier teksten bak merket «regnet av kursene til 22.09.2026» i stedet for «målt 22.09.2026». Dagen er den siste dagen med kurser i basen. *Forslag:* som bygget, og samme ord på «Følg en aksje».
5. **En aksje i lista uten kurser i vinduet.** Den har ingen median av kursene og bruker ikke en eldre måling (BH3 i 8.11b). *Forslag:* merket står da som «Omsetningen er ikke målt ennå», som i de ferdige listene, der den ikke står.
6. **«+0,1 % MNOK» på «Følg en aksje».** Siden fra 2.12 viste omsetningen med slaget for målingene, med fortegn og %. Funnet under byggingen. *Forslag:* rettet i en egen commit i samme PR (`e5d456a2`), med et nytt slag `mnok` i `tallformat.py` (regel 21) og en test. Rettingen følger med i natt, ellers står feilen i 2.12 etter flettingen kl. 23:50.
7. **Samspillet med de lave funnene.** BH4/ECH4 i 8.11b (`max(dato)` over hele `kurs` og én spørring per aksje) rettes i PR-en for de lave funnene, i `_aksjene_i_lista`. *Forslag:* 8.11c endrer ikke `_aksjene_i_lista`, men kaller den fra en ny funksjon, `medianene()`, nederst i `ferdige_lister.py`, så de to PR-ene endrer ulike deler av fila og kan flettes etter hverandre i natt.

*Svar 2026-11-09 kl. 17:37 (gruppens svar):* alle sju forslagene er godtatt, og BH3 lukkes med spørsmål 5. Rådet anbefalte det. Svaret er ført etter instruksjonen kl. 21:41 i `docs/ai-prompts/2026-11-09.md`, og storyen står i `epics.md` etter 8.11.

## Intent

**Problem:** Merket «Utenfor målingen» fra 2.12 leser den siste målingen i `omsetning`, mens de ferdige listene i 8.11b regner medianen av kursene for aksjene appen henter. En egen aksje kunne stå som ikke målt i tabellen og med en median i den ferdige lista (ECH2 i 8.11b).

**Approach:** `medianene()` i `src/ferdige_lister.py` gir medianen `lister()` bruker for hver aksje som regnes av kursene, og `_omsetningen()` i `src/app.py` bruker den for merket og «Følg en aksje», med målingen fra 2.13 for de andre.

## Delene

### A) Medianene
`medianene()` i `src/ferdige_lister.py`.
- **Ville feilet hvis:** merket og de ferdige listene fikk hver sin median for en aksje som regnes av kursene, eller en aksje som bare er målt i 2.13, fikk en median herfra.

### B) Merket
`_omsetningen()` og `_egne()` i `src/app.py`.
- **Ville feilet hvis:** merket fulgte målingen i 2.13 og ikke medianen av kursene for en egen aksje som er hentet, eller merket og den ferdige lista var uenige.

### C) «Følg en aksje»
`folg_side()` i `src/app.py` og `src/templates/folg.html`.
- **Ville feilet hvis:** siden viste målingen i 2.13 for en aksje som regnes av kursene, eller mistet målingen for en aksje appen aldri har hentet.

### D) Teksten
`utenfor_tekst()` i `src/valg.py`.
- **Ville feilet hvis:** teksten sa «målt» om en median regnet av kursene, eller omvendt.

## Grenser

Ingen API-kall, `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` røres ikke. Ingen migrasjon. Medianene regnes når siden vises og lagres ikke, og ingen tall fra kildene står i koden, testene eller spesifikasjonen (regel 16).

## Bygget 09.11 (ekstravinduet)

Bygget på grenen `8-11c-utenfor-maalingen`, i worktreen `G74-lund-osen-8-11c`, fra `78a45186`.

- **Filene.** `medianene()` i `src/ferdige_lister.py`, `_medianene()`, `_omsetningen()` og `_egne()` i `src/app.py`, `utenfor_tekst()` i `src/valg.py`, `src/templates/folg.html`, slaget `mnok` i `src/tallformat.py` (`e5d456a2`), og «Hvordan følger jeg andre aksjer?» i `docs/hjelp.md` (regel 19). Testene: `tests/test_utenfor_maalingen_8_11c.py`, `test_mnok_uten_fortegn_og_prosent` i `tests/test_tallformat.py`, og testen for merket i `tests/test_valg.py`, som nå venter «regnet av kursene til» etter svaret.
- **Bildene.** `app.py`, `valg.py`, `ferdige_lister.py`, `tallformat.py` og `folg.html` står bak bildene i `docs/appen/`. Avtrykkene er regnet ut på nytt, og alle ni bildene er tatt på nytt med DevTools-protokollen, med de samme høydene. Alle var byte for byte de samme. Fremgangsmåten ble først prøvd mot `78a45186`, der alle ni ble like.

## Mutantene

Én per del på `a1914c9b`, med kopi før og fila lik HEAD etterpå (`git hash-object` mot `git rev-parse HEAD:<fil>`): A (medianene doblet) fanget av `TestMedianene`, B (`_omsetningen` bruker aldri medianene) av `TestMerket`, C (`kursene` alltid usann på «Følg en aksje») av `TestFoelgSiden`, D (teksten sier alltid «målt») av `TestTeksten`, og `mnok` med % av `test_mnok_uten_fortegn_og_prosent` og `TestFoelgSiden`.

## Gjennomgangen 09.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Diffen `78a45186..a1914c9b`: Blind Hunter med bare diffen, uten `tests/test_docker.py` (10 funn), og Edge Case Hunter og Verification Gap i samme agent med repoet (5 og 6 funn, med mutanter i en kopi utenfor worktreen). Ingen høye.

**Middels**
- *BH1 og ECH1, rettet.* Dagen i teksten var den siste dagen med kurser i basen, også for en aksje som er tatt ut og har sin siste kurs før. Nå er dagen aksjens egen siste dag med kurser (`test_dagen_er_aksjens_siste_dag_med_kurser`). Spørsmål 4 over sier «den siste dagen med kurser i basen»; det gjelder nå vinduet, som fortsatt er tre måneder til basens siste dag, som i de ferdige listene. For en aksje som er tatt ut, kan medianen derfor være av færre dager enn tre måneder.
- *BH4 og ECH2, rettet.* Medianene og de ferdige listene ble regnet 4–5 ganger per side, fordi `_egne()` kjøres både i ruta og i context processoren, og «Følg en aksje» regnet medianene i tillegg. Nå regnes `_egne()` og medianene én gang per forespørsel (`g`), og «Følg en aksje» regner medianene bare når siden viser en omsetning.
- *VG1, rettet.* Rettingen av «+0,1 % MNOK» var bare testet i søket. Nå også for en valgt aksje (`ca. 0,1 MNOK om dagen`).
- *VG2, rettet.* Spørsmål 5 var ikke testet. Nå `test_en_aksje_i_lista_uten_kurser_bruker_ikke_maalingen`.
- *BH3, står med spørsmål 5.* En aksje i lista uten kurser i vinduet står som «ikke målt ennå», også med en måling i 2.13. En aksje som er tatt ut og ikke har kurser i vinduet, er ikke regnet av kursene og bruker målingen, så den delen av funnet holder ikke.
- *BH3, lukket 2026-11-09 med spørsmål 5* (gruppens svar kl. 17:37), middels som før (regel 25): forslaget i spørsmål 5 er godtatt.
- *BH2, ikke reelt.* Er `regnet` ikke tom, har `_aksjene_i_lista` alt lest en dato (Edge Case Hunter kontrollerte det samme). Dagen leses nå per aksje og tåler at den mangler.

**Lav**
- *Rettet:* BH5 (teksten bak merket bruker `tall(…, "mnok")`, regel 21), BH6 (omsetningen leses én gang per rad), BH8 (hjelpen sier aksjens siste dag, at en aksje i lista uten kurser står som ikke målt, og at en aksje som venter, har målingen), BH9 og ECH5 (testen av `mnok` står for seg, med null og avrundingen), BH10 (`test_begge_uten_merket` og dagen for en aksje som er tatt ut), VG3 (den andre linja på «Følg en aksje»), VG4 (en base uten tabellene).
- *Ført:* BH7 (ordene «regnet av kursene til» står i malen og i `utenfor_tekst`), ECH3 (spørsmål 2 sier at en aksje som venter, har målingen fordi den ikke er i `aksje`; en aksje som er tatt ut og følges på nytt, står i `aksje` og bruker medianen av kursene mens den venter, som i de ferdige listene), ECH4 (en feil i basen gir stille målingen; `lister()` gjør det samme, så de er enige), VG5 (en aksje som følges på nytt, er ikke testet), VG6 (merket på aksjesiden og i børsometeret kommer fra samme context processor og er ikke testet på nytt).
- **Mutantene for rettingene** på `ec21d3fd`, med kopi før og fila lik HEAD etterpå: BH1 (dagen er basens siste dag) fanget av `test_dagen_er_aksjens_siste_dag_med_kurser`. BH4 (`_egne()` uten bufferen) og BH5 (teksten regner tallet selv) overlevde, fordi ingen test talte utregningene eller hadde en median over 1000 MNOK. Nå `TestEnGangPerSide` og `test_teksten_med_tusenskille`, og begge mutantene ble fanget.
