---
title: "Relevanseksperimentet — kriteriene for del 1"
status: aktiv
created: 2026-09-25
updated: 2026-09-26T19:02
---

# Relevanseksperimentet — kriteriene for del 1

**Kriteriene er skrevet og committet før noen artikkel er hentet til
eksperimentet.** Tidspunktet for commiten er beviset. Kriteriene endres ikke
etter at innsamlingen har startet. Må noe endres, føres det som et avvik med
dato og grunn.

Fila inneholder ingen titler, utdrag eller andre rådata (regel 16 i
`CLAUDE.md`). Artiklene og merkingen ligger bare i `data/`. Her står bare
summene.

## 1. Selskapene

Ett selskap per sektor, det mest likvide i hver, målt som median omsetning
(PRD §3):

| Sektor | Selskap |
|---|---|
| Energi | EQNR |
| Finans | DNB |
| Industri | KOG |
| Materialer | NHY |
| Shipping | FRO |
| Telekom | TEL |
| Sjømat | MOWI |
| Konsum | ORK |

Regelen er valgt før vi har sett artiklene. DNB og Frontline er med fordi de
er størst i sin sektor, ikke fordi vi vet hva artiklene deres vil vise.

De ti DNB-artiklene fra nyhetstesten 21.09
(`data/nyhetstest-raa-2026-09-21.json`, `malinger.md` §7.2) holdes utenfor.

**Svakhet:** artiklene som ble lest 17.09 for DNB og Frontline, kan ikke
holdes utenfor, fordi det ikke finnes rådata fra den testen (`malinger.md`
§0). Vi vet ikke om noen av dem kommer med igjen.

## 2. Antall, periode og kostnad

- De **seks nyeste** artiklene per selskap på hentedagen, **48** til sammen.
- **Én forespørsel per selskap**, så hvert selskap får sine egne artikler.
- Vi henter **ti** per selskap, og **20 for DNB**, fordi de ti fra 21.09 tas
  ut.
- Ut tas: dubletter, artikler uten tekst og, for DNB, de ti fra 21.09. Av
  resten brukes de seks nyeste.
- **Dublett:** samme lenke eller samme tittel to ganger for samme selskap.
  Samme sak fra to kilder med ulik tittel teller som to artikler. Utvalget
  følger regler uten skjønn. Skjønnet hører hjemme i merkingen.
- Har et selskap færre enn seks, bruker vi dem som finnes, og det føres i
  resultatet.
- Perioden er den de seks artiklene dekker. Den føres per selskap i
  resultatet.

**Kostnad.** Prisen for én forespørsel med én ticker er målt: 5 kall
(`malinger.md` §7.2).

- `/api/user` leses før og etter hver forespørsel. Koster en forespørsel noe
  annet enn 5 kall, stopper vi før neste og vurderer.
- Slik blir det også målt om `limit=20` for DNB koster mer enn `limit=10`.
- Budsjettet er åtte forespørsler, ~40 kall.

**Avvik fra story 9.4 og åpent punkt 5 i PRD-en.** Begge sier at den første
forespørselen skal ha to tickere, for å måle om to tickere koster 10 eller 15
kall. Den kontrollen er byttet ut med målingen over. Den måler hva en
forespørsel med flere tickere koster, og det trenger vi ikke når hvert selskap
hentes for seg.

## 3. Merkingen

**Enheten er artikkel pluss selskap.** Samme artikkel merkes for hvert selskap
den er hentet for.

Hvert par får én verdi fra FR-606:

| Verdi | Betyr |
|---|---|
| Påvirker selskapet direkte | Saken har konkret betydning for selskapets drift, kontrakter, eierskap eller resultat |
| Kan påvirke | Saken kan få betydning, men det er ikke gitt |
| Lite relevant | Saken har ingen praktisk betydning for en sparer |

FR-606 avgjør. To regler gjelder grensetilfellene:

- Selskapet er part, men saken handler om noen andre: **høyst «Kan påvirke»**.
- Selskapet er bare nevnt, i en liste, en indeks eller en markedsoversikt:
  **«Lite relevant»**.

**Tvil:** vi setter verdien vi lander på, og et flagg for tvil. Flaggene
telles i resultatet.

**To merkere:** vi merker hver for oss først, uten å se den andres svar, og
blir så enige om én verdi per par. Hvor ofte vi var enige før vi snakket
sammen, føres i resultatet.

## 4. Det vi ser når vi merker

Bare **selskapsnavnet, tittelen og teksten**, i blandet rekkefølge. Disse
feltene skjules: `sentiment`, `tags`, `symbols`, lenke og dato.

Tittel og tekst er det samme som KI-en skal få i del 2. EODHDs godkjenning
21.09 gjelder «headlines and article text» (`docs/kilder-og-rettigheter.md`).

## 5. Resultatet som skal regnes ut

**Del 1:** andelen par som ikke er «Lite relevant», samlet og per selskap. Det
er treffsikkerheten til symbolmatchingen. I tillegg føres:

- perioden per selskap
- selskaper med færre enn seks artikler
- antall tvilsflagg
- hvor ofte vi var enige før vi snakket sammen

**Del 2:** verdiene fra KI-en sammenlignes med den endelige verdien vår, både
på de tre nivåene og som relevant eller ikke relevant.

## 6. Innsamlingen 25.09

**Tid:** 2026-09-25, kl. 13:02 lokal tid (11:02:24–11:02:48 UTC). Åtte
forespørsler mot `/api/news`, én per selskap, i rekkefølgen i §1. `/api/user`
ble lest før og etter hver av dem.

**Kall.** Hver forespørsel kostet **5 kall**, også DNB med `limit=20`. En
høyere `limit` kostet altså ikke mer. Til sammen **40 kall**: 20 fra
dagskvoten og 20 fra bonuskvoten.

| | `apiRequests` | `apiRequestsDate` | `extraLimit` |
|---|---:|---|---:|
| Før første forespørsel | 15 (gårsdagens, altså 0 i dag) | 2026-09-24 | 484 |
| Etter siste forespørsel | 20 | 2026-09-25 | 464 |

**Per selskap.** Hver artikkel er telt under én grunn, i denne rekkefølgen:
uten tekst, dublett, og for DNB blant de ti fra 21.09. Av resten ble de seks
nyeste brukt.

| Selskap | Hentet | Uten tekst | Dublett | Fra 21.09 | Utenfor de seks nyeste | Brukt | Datospenn for de brukte |
|---|---:|---:|---:|---:|---:|---:|---|
| EQNR | 10 | 0 | 0 | — | 4 | 6 | 2026-09-21 – 2026-09-24 |
| DNB | 20 | 0 | 2 | 10 | 2 | 6 | 2026-05-04 – 2026-06-04 |
| KOG | 10 | 0 | 0 | — | 4 | 6 | 2026-05-19 – 2026-08-07 |
| NHY | 10 | 0 | 0 | — | 4 | 6 | 2026-08-13 – 2026-09-23 |
| FRO | 10 | 0 | 0 | — | 4 | 6 | 2026-09-15 – 2026-09-23 |
| TEL | 10 | 0 | 0 | — | 4 | 6 | 2026-05-28 – 2026-07-16 |
| MOWI | 10 | 0 | 0 | — | 4 | 6 | 2026-06-19 – 2026-08-31 |
| ORK | 10 | 0 | 0 | — | 4 | 6 | 2026-05-21 – 2026-08-21 |
| **Sum** | **90** | **0** | **2** | **10** | **30** | **48** | |

Alle åtte fikk seks artikler, så ingen selskaper har færre. Det gir **48 par**.

Alle de ti DNB-artiklene fra 21.09 kom med i svaret og ble tatt ut. De er
datert 2026-06-07 til 2026-09-11 (`malinger.md` §7.2), og EODHD hadde ingen
nyere DNB-artikler 25.09. De seks som ble brukt, er derfor eldre enn alle de
ti, og DNBs datospenn slutter før alle de andre selskapenes.

Artiklene, utvalget, tekstene, nøkkelen og de to tomme merkefilene ligger bare
i `data/`. Frøet for blandingen står i utvalgsfila der.

## 7. Merkingen 26.09

Marian og Joakim merket de 48 parene hver for seg, uten å se den andres svar
(bekreftet av Marian 26.09 kl. 19:00). Hver av oss har sin egen merkefil i
`data/`. Tallene under er regnet med skriptet `data/relevans_enighet.py`, som
ikke er i repoet, og de stemmer med det rådet regnet ut fra de samme verdiene.

| | Like | Andel | Forventet ved tilfeldighet | Cohens kappa |
|---|---:|---:|---:|---:|
| Tre verdier (D, K, L) | 40 av 48 | 83 % | 0,336 | 0,749 |
| Relevant (D eller K) mot L | 42 av 48 | 88 % | 0,586 | 0,698 |

**Tvil.** Hver av oss satte tvil på 4 par, og 3 av dem var de samme.

**De åtte ulike parene** avgjøres i samtale. Den felles verdien står i
`data/relevans-merker-endelig.csv` for de 40 like parene, og feltet er tomt for
de åtte til vi har snakket sammen. Resultatet for del 1 (§5) regnes først når
alle 48 har en endelig verdi.
