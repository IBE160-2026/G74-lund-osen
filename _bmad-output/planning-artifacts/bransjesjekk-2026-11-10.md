---
title: "Kontrollsjekken av bransjene 10.11"
status: final
created: 2026-11-10
updated: 2026-11-10T16:43
---

# Kontrollsjekken av bransjene 10.11

Story 8.22. Hver aksje i lista over Oslo Børs har en fast bransje, så den som følger en aksje, ikke velger bransjen selv (gruppens svar 10.11 kl. 13:38, som erstatter svaret 08.11 kl. 11:57). Bransjen står i `BRANSJE` i `src/ferdige_lister.py`, og `tests/test_bransjene_8_22.py` sjekker at tabellen under er lik den. Selskapsnavnene står ikke her.

## Fremgangsmåten

1. Instruksjonen kl. 13:41 i vindu 2 lagde forslagsfila `bransjeforslag-2026-11-10.csv` i scratchpad, med én rad per aksje i tabellen `boersliste` (lest med `mode=ro`). Fila committes aldri.
2. De 87 i `BRANSJE` på main, som gruppen sjekket 08.11 kl. 22:01 og 22:03, sto med bransjen derfra uendret. De andre fikk en av de 13 bransjene i `designregler.md` §4 ut fra navnet og det som er kjent om selskapet, merket usikker der det var lite å gå på.
3. Gruppen sjekket lista på en delt side kl. 14:43. Alle 195 forslag og usikre ble avgjort: 194 som foreslått, og MULTI ble tatt ut. De 195 er de 210 forslagene minus de 15 aksjene i lista. Den delte siden viste de 15 for seg, med bransjen fra `designregler.md` §4, så de skulle ikke avgjøres.
4. Kl. 15:22 bestemte gruppen at SCOIN er ute, som 08.11 kl. 22:03.
5. Story 8.22 førte resultatet inn i `BRANSJE` 10.11. Før commit ble antallet per bransje og sha256 av linjene «TICKER;Bransje», sortert og med `\n` etter hver, sjekket mot instruksjonen. Samme sjekk står i testen.

## Tallene

- 297 aksjer i forslagsfila: 87 sjekket 08.11, 157 forslag og 53 forslag merket usikker. 15 av forslagene er de 15 aksjene i lista.
- 295 aksjer har en bransje. MULTI og SCOIN er tatt ut.
- Per bransje: Energi 57, Finans 50, Industri 34, Teknologi 32, Shipping 27, Helse 21, Sjømat 20, Materialer 17, Forbruk 15, Kraft 9, Eiendom 7, Konsum 4, Telekom 2.
- sha256 av linjene «TICKER;Bransje»: `302e28433bf582ec9abad65ffde06c2dbcd533cd6130713990e2fa3ed0c6dec9`.

## Grunnene til at to er ute

- **MULTI:** en fusjon gjør det usikkert hva som skjer med aksjen (svaret kl. 14:43).
- **SCOIN:** selskapet er under avvikling (svaret kl. 15:22, som 08.11 kl. 22:03).

## Aksjene

| Ticker | Bransje | Kilde |
|---|---|---|
| 2020 | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| 5PG | Forbruk | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| AASB | Finans | forslag, sjekket 10.11 kl. 14:43 |
| ABG | Finans | forslag, sjekket 10.11 kl. 14:43 |
| ABS | Helse | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| ABTEC | Konsum | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| ACED | Teknologi | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| ACR | Finans | forslag, sjekket 10.11 kl. 14:43 |
| ADS | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| AFG | Industri | forslag, sjekket 10.11 kl. 14:43 |
| AFISH | Sjømat | forslag, sjekket 10.11 kl. 14:43 |
| AFK | Finans | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| AGLX | Materialer | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| AIX | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| AKAST | Energi | forslag, sjekket 10.11 kl. 14:43 |
| AKBM | Konsum | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| AKER | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| AKOBO | Materialer | forslag, sjekket 10.11 kl. 14:43 |
| AKRBP | Energi | de 15 i lista, bransjen fra designregler.md §4 |
| AKSO | Energi | forslag, sjekket 10.11 kl. 14:43 |
| AKVA | Industri | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| ALNG | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| ANDF | Sjømat | forslag, sjekket 10.11 kl. 14:43 |
| APR | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| AQUA | Energi | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| ARCH | Energi | forslag, sjekket 10.11 kl. 14:43 |
| ARR | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| ASA | Sjømat | forslag, sjekket 10.11 kl. 14:43 |
| ATEA | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| AURG | Finans | forslag, sjekket 10.11 kl. 14:43 |
| AUSS | Sjømat | forslag, sjekket 10.11 kl. 14:43 |
| AUTO | Industri | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| AZT | Helse | forslag, sjekket 10.11 kl. 14:43 |
| B2I | Finans | forslag, sjekket 10.11 kl. 14:43 |
| BAKKA | Sjømat | forslag, sjekket 10.11 kl. 14:43 |
| BALT | Eiendom | forslag, sjekket 10.11 kl. 14:43 |
| BARRA | Sjømat | forslag, sjekket 10.11 kl. 14:43 |
| BCS | Materialer | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| BEWI | Materialer | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| BIEN | Finans | forslag, sjekket 10.11 kl. 14:43 |
| BINT | Finans | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| BMA | Industri | forslag, sjekket 10.11 kl. 14:43 |
| BNOR | Energi | forslag, sjekket 10.11 kl. 14:43 |
| BOHUS | Forbruk | forslag, sjekket 10.11 kl. 14:43 |
| BONHR | Kraft | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| BOR | Shipping | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| BORR | Energi | forslag, sjekket 10.11 kl. 14:43 |
| BOUV | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| BRG | Materialer | forslag, sjekket 10.11 kl. 14:43 |
| BRUT | Finans | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| BSP | Eiendom | forslag, sjekket 10.11 kl. 14:43 |
| BWE | Energi | forslag, sjekket 10.11 kl. 14:43 |
| BWLPG | Shipping | sjekket 08.11 kl. 22:01 og 22:03 |
| BWO | Energi | forslag, sjekket 10.11 kl. 14:43 |
| CADLR | Energi | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| CAMBI | Industri | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| CAPSL | Industri | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| CAPT | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| CAVEN | Energi | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| CLOUD | Kraft | forslag, sjekket 10.11 kl. 14:43 |
| CMBTO | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| CODE | Finans | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| CONTX | Helse | forslag, sjekket 10.11 kl. 14:43 |
| COSH | Energi | forslag, sjekket 10.11 kl. 14:43 |
| CRNA | Helse | forslag, sjekket 10.11 kl. 14:43 |
| CYVIZ | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| DDRIL | Energi | forslag, sjekket 10.11 kl. 14:43 |
| DELIA | Teknologi | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| DFENS | Industri | forslag, sjekket 10.11 kl. 14:43 |
| DNB | Finans | de 15 i lista, bransjen fra designregler.md §4 |
| DNO | Energi | de 15 i lista, bransjen fra designregler.md §4 |
| DOFG | Energi | forslag, sjekket 10.11 kl. 14:43 |
| DSRT | Materialer | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| DVD | Energi | forslag, sjekket 10.11 kl. 14:43 |
| EAM | Kraft | forslag, sjekket 10.11 kl. 14:43 |
| EIOF | Energi | forslag, sjekket 10.11 kl. 14:43 |
| ELABS | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| ELK | Materialer | forslag, sjekket 10.11 kl. 14:43 |
| ELMRA | Kraft | forslag, sjekket 10.11 kl. 14:43 |
| ELO | Materialer | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| ELOO | Materialer | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| ENDUR | Industri | forslag, sjekket 10.11 kl. 14:43 |
| ENERG | Kraft | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| ENH | Energi | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| ENSU | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| ENTRA | Eiendom | forslag, sjekket 10.11 kl. 14:43 |
| ENVIP | Industri | forslag, sjekket 10.11 kl. 14:43 |
| EPR | Forbruk | forslag, sjekket 10.11 kl. 14:43 |
| EQNR | Energi | de 15 i lista, bransjen fra designregler.md §4 |
| EQVA | Industri | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| EXTX | Helse | forslag, sjekket 10.11 kl. 14:43 |
| FFSB | Finans | forslag, sjekket 10.11 kl. 14:43 |
| FRO | Shipping | de 15 i lista, bransjen fra designregler.md §4 |
| GEM | Materialer | forslag, sjekket 10.11 kl. 14:43 |
| GENO | Industri | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| GENT | Helse | forslag, sjekket 10.11 kl. 14:43 |
| GEOS | Energi | forslag, sjekket 10.11 kl. 14:43 |
| GIGA | Sjømat | forslag, sjekket 10.11 kl. 14:43 |
| GJF | Finans | de 15 i lista, bransjen fra designregler.md §4 |
| GKP | Energi | forslag, sjekket 10.11 kl. 14:43 |
| GOD | Industri | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| GOLDR | Materialer | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| GRONG | Finans | forslag, sjekket 10.11 kl. 14:43 |
| GSF | Sjømat | forslag, sjekket 10.11 kl. 14:43 |
| GYL | Forbruk | forslag, sjekket 10.11 kl. 14:43 |
| HAFNI | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| HAUTO | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| HAV | Industri | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| HAVI | Energi | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| HBC | Konsum | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| HDLY | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| HELG | Finans | forslag, sjekket 10.11 kl. 14:43 |
| HERMA | Finans | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| HEX | Industri | forslag, sjekket 10.11 kl. 14:43 |
| HGSB | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| HKY | Forbruk | sjekket 08.11 kl. 22:01 og 22:03 |
| HPUR | Industri | sjekket 08.11 kl. 22:01 og 22:03 |
| HSHP | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| HSPG | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| HUDL | Teknologi | sjekket 08.11 kl. 22:01 og 22:03 |
| HUNT | Shipping | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| HYN | Energi | sjekket 08.11 kl. 22:01 og 22:03 |
| HYPRO | Energi | sjekket 08.11 kl. 22:01 og 22:03 |
| IDEX | Teknologi | sjekket 08.11 kl. 22:01 og 22:03 |
| INDCT | Teknologi | sjekket 08.11 kl. 22:01 og 22:03 |
| INIFY | Helse | sjekket 08.11 kl. 22:01 og 22:03 |
| ININ | Industri | sjekket 08.11 kl. 22:01 og 22:03 |
| INSTA | Finans | forslag, sjekket 10.11 kl. 14:43 |
| IOX | Energi | sjekket 08.11 kl. 22:01 og 22:03 |
| ISLAX | Sjømat | forslag, sjekket 10.11 kl. 14:43 |
| ITERA | Teknologi | sjekket 08.11 kl. 22:01 og 22:03 |
| IWS | Energi | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| JACK | Energi | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| JAREN | Finans | forslag, sjekket 10.11 kl. 14:43 |
| JIN | Shipping | sjekket 08.11 kl. 22:01 og 22:03 |
| KCC | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| KID | Forbruk | forslag, sjekket 10.11 kl. 14:43 |
| KING | Sjømat | sjekket 08.11 kl. 22:01 og 22:03 |
| KIT | Industri | forslag, sjekket 10.11 kl. 14:43 |
| KLDVK | Sjømat | sjekket 08.11 kl. 22:01 og 22:03 |
| KMAR | Industri | sjekket 08.11 kl. 22:01 og 22:03 |
| KOA | Forbruk | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| KOG | Industri | de 15 i lista, bransjen fra designregler.md §4 |
| KOMPL | Forbruk | sjekket 08.11 kl. 22:01 og 22:03 |
| KRAB | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| LIFE | Helse | sjekket 08.11 kl. 22:01 og 22:03 |
| LINK | Telekom | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| LOKO | Teknologi | sjekket 08.11 kl. 22:01 og 22:03 |
| LSG | Sjømat | forslag, sjekket 10.11 kl. 14:43 |
| LUMI | Forbruk | sjekket 08.11 kl. 22:01 og 22:03 |
| LYTIX | Helse | sjekket 08.11 kl. 22:01 og 22:03 |
| MAS | Sjømat | forslag, sjekket 10.11 kl. 14:43 |
| MDATA | Teknologi | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| MEDI | Helse | forslag, sjekket 10.11 kl. 14:43 |
| MELG | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| MGN | Kraft | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| MING | Finans | forslag, sjekket 10.11 kl. 14:43 |
| MORG | Finans | forslag, sjekket 10.11 kl. 14:43 |
| MORLD | Energi | forslag, sjekket 10.11 kl. 14:43 |
| MOWI | Sjømat | de 15 i lista, bransjen fra designregler.md §4 |
| MPCC | Shipping | de 15 i lista, bransjen fra designregler.md §4 |
| MPCES | Kraft | sjekket 08.11 kl. 22:01 og 22:03 |
| MULTI | – | tatt ut 10.11 kl. 14:43: en fusjon gjør det usikkert hva som skjer |
| MVW | Industri | sjekket 08.11 kl. 22:01 og 22:03 |
| NAPA | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| NAS | Forbruk | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| NAVA | Helse | sjekket 08.11 kl. 22:01 og 22:03 |
| NBX | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| NCOD | Sjømat | sjekket 08.11 kl. 22:01 og 22:03 |
| NEL | Energi | forslag, sjekket 10.11 kl. 14:43 |
| NEXT | Teknologi | sjekket 08.11 kl. 22:01 og 22:03 |
| NHY | Materialer | de 15 i lista, bransjen fra designregler.md §4 |
| NISB | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| NKR | Industri | forslag, sjekket 10.11 kl. 14:43 |
| NOAP | Sjømat | forslag, sjekket 10.11 kl. 14:43 |
| NOD | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| NOFIN | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| NOHAL | Sjømat | forslag, sjekket 10.11 kl. 14:43 |
| NOL | Energi | forslag, sjekket 10.11 kl. 14:43 |
| NOM | Materialer | sjekket 08.11 kl. 22:01 og 22:03 |
| NONG | Finans | forslag, sjekket 10.11 kl. 14:43 |
| NORAM | Energi | forslag, sjekket 10.11 kl. 14:43 |
| NORBT | Teknologi | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| NORCO | Industri | forslag, sjekket 10.11 kl. 14:43 |
| NORDH | Helse | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| NORSE | Forbruk | sjekket 08.11 kl. 22:01 og 22:03 |
| NORTH | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| NOSN | Industri | sjekket 08.11 kl. 22:01 og 22:03 |
| NRC | Industri | forslag, sjekket 10.11 kl. 14:43 |
| NSKOG | Materialer | forslag, sjekket 10.11 kl. 14:43 |
| NTG | Industri | sjekket 08.11 kl. 22:01 og 22:03 |
| NTI | Industri | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| NYKD | Helse | sjekket 08.11 kl. 22:01 og 22:03 |
| OBSRV | Helse | sjekket 08.11 kl. 22:01 og 22:03 |
| OCEAN | Industri | sjekket 08.11 kl. 22:01 og 22:03 |
| ODF | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| ODFB | Shipping | sjekket 08.11 kl. 22:01 og 22:03 |
| ODL | Energi | forslag, sjekket 10.11 kl. 14:43 |
| OET | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| OKEA | Energi | forslag, sjekket 10.11 kl. 14:43 |
| OMC | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| OMDA | Helse | sjekket 08.11 kl. 22:01 og 22:03 |
| ONCIN | Helse | sjekket 08.11 kl. 22:01 og 22:03 |
| ORK | Konsum | de 15 i lista, bransjen fra designregler.md §4 |
| OSUN | Energi | sjekket 08.11 kl. 22:01 og 22:03 |
| OTEC | Teknologi | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| OTL | Energi | forslag, sjekket 10.11 kl. 14:43 |
| OTOVO | Energi | sjekket 08.11 kl. 22:01 og 22:03 |
| OUTLT | Forbruk | sjekket 08.11 kl. 22:01 og 22:03 |
| PARB | Finans | forslag, sjekket 10.11 kl. 14:43 |
| PEN | Energi | forslag, sjekket 10.11 kl. 14:43 |
| PEXIP | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| PHO | Helse | forslag, sjekket 10.11 kl. 14:43 |
| PLCAN | Shipping | sjekket 08.11 kl. 22:01 og 22:03 |
| PLGC | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| PLSV | Energi | forslag, sjekket 10.11 kl. 14:43 |
| PLT | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| PNOR | Energi | forslag, sjekket 10.11 kl. 14:43 |
| POL | Forbruk | forslag, sjekket 10.11 kl. 14:43 |
| POLAR | Materialer | sjekket 08.11 kl. 22:01 og 22:03 |
| PPG | Eiendom | sjekket 08.11 kl. 22:01 og 22:03 |
| PROT | Finans | forslag, sjekket 10.11 kl. 14:43 |
| PROXI | Sjømat | sjekket 08.11 kl. 22:01 og 22:03 |
| PRS | Energi | forslag, sjekket 10.11 kl. 14:43 |
| PSE | Energi | sjekket 08.11 kl. 22:01 og 22:03 |
| PUBLI | Eiendom | sjekket 08.11 kl. 22:01 og 22:03 |
| PYRUM | Materialer | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| QEC | Energi | sjekket 08.11 kl. 22:01 og 22:03 |
| QGAS | Energi | sjekket 08.11 kl. 22:01 og 22:03 |
| REACH | Energi | forslag, sjekket 10.11 kl. 14:43 |
| REFL | Energi | sjekket 08.11 kl. 22:01 og 22:03 |
| RING | Finans | forslag, sjekket 10.11 kl. 14:43 |
| RIVER | Teknologi | sjekket 08.11 kl. 22:01 og 22:03 |
| ROGS | Finans | forslag, sjekket 10.11 kl. 14:43 |
| ROM | Eiendom | sjekket 08.11 kl. 22:01 og 22:03 |
| ROMER | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| SAGA | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| SALM | Sjømat | de 15 i lista, bransjen fra designregler.md §4 |
| SALME | Sjømat | forslag, sjekket 10.11 kl. 14:43 |
| SATS | Forbruk | forslag, sjekket 10.11 kl. 14:43 |
| SB1NO | Finans | forslag, sjekket 10.11 kl. 14:43 |
| SB68 | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| SBNOR | Finans | forslag, sjekket 10.11 kl. 14:43 |
| SBO | Eiendom | forslag, sjekket 10.11 kl. 14:43 |
| SCANA | Industri | sjekket 08.11 kl. 22:01 og 22:03 |
| SCATC | Kraft | forslag, sjekket 10.11 kl. 14:43 |
| SCOIN | – | tatt ut 10.11 kl. 15:22, som 08.11 kl. 22:03: selskapet er under avvikling |
| SDSD | Energi | sjekket 08.11 kl. 22:01 og 22:03 |
| SEA1 | Energi | forslag, sjekket 10.11 kl. 14:43 |
| SKAND | Kraft | sjekket 08.11 kl. 22:01 og 22:03 |
| SKUE | Finans | forslag, sjekket 10.11 kl. 14:43 |
| SMOP | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| SNI | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| SNM | Energi | forslag, sjekket 10.11 kl. 14:43 |
| SNOR | Finans | forslag, sjekket 10.11 kl. 14:43 |
| SNTIA | Industri | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| SOAG | Finans | forslag, sjekket 10.11 kl. 14:43 |
| SOFF | Energi | forslag, sjekket 10.11 kl. 14:43 |
| SOFTX | Helse | sjekket 08.11 kl. 22:01 og 22:03 |
| SOGN | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| SOMA | Energi | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| SPOG | Finans | forslag, sjekket 10.11 kl. 14:43 |
| SPOL | Finans | forslag, sjekket 10.11 kl. 14:43 |
| STB | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| STECH | Energi | sjekket 08.11 kl. 22:01 og 22:03 |
| STRO | Teknologi | sjekket 08.11 kl. 22:01 og 22:03 |
| STST | Shipping | sjekket 08.11 kl. 22:01 og 22:03 |
| SUBC | Energi | sjekket 08.11 kl. 22:01 og 22:03 |
| SWON | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| TECH | Teknologi | sjekket 08.11 kl. 22:01 og 22:03 |
| TEKNA | Industri | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| TEL | Telekom | de 15 i lista, bransjen fra designregler.md §4 |
| TGS | Energi | forslag, sjekket 10.11 kl. 14:43 |
| TINDE | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| TOM | Industri | forslag, sjekket 10.11 kl. 14:43 |
| TRMED | Helse | forslag, sjekket 10.11 kl. 14:43 |
| TRSB | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| VAR | Energi | de 15 i lista, bransjen fra designregler.md §4 |
| VEI | Industri | forslag, sjekket 10.11 kl. 14:43 |
| VEND | Forbruk | forslag, sjekket 10.11 kl. 14:43 |
| VISTN | Helse | sjekket 08.11 kl. 22:01 og 22:03 |
| VLCC | Shipping | sjekket 08.11 kl. 22:01 og 22:03 |
| VOIM | Energi | sjekket 08.11 kl. 22:01 og 22:03 |
| VOW | Industri | sjekket 08.11 kl. 22:01 og 22:03 |
| VTURA | Energi | forslag, sjekket 10.11 kl. 14:43 |
| VVL | Finans | sjekket 08.11 kl. 22:01 og 22:03 |
| WAWI | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| WEST | Shipping | sjekket 08.11 kl. 22:01 og 22:03 |
| WSTEP | Teknologi | sjekket 08.11 kl. 22:01 og 22:03 |
| WWI | Shipping | forslag, sjekket 10.11 kl. 14:43 |
| WWIB | Shipping | sjekket 08.11 kl. 22:01 og 22:03 |
| XPLRA | Teknologi | sjekket 08.11 kl. 22:01 og 22:03 |
| YAR | Materialer | de 15 i lista, bransjen fra designregler.md §4 |
| ZAL | Teknologi | forslag, sjekket 10.11 kl. 14:43 |
| ZAP | Industri | forslag merket usikker, sjekket 10.11 kl. 14:43 |
| ZENA | Energi | sjekket 08.11 kl. 22:01 og 22:03 |
| ZLNA | Helse | sjekket 08.11 kl. 22:01 og 22:03 |
