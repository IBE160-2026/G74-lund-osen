---
title: "Relevanseksperimentet — kriteriene for del 1"
status: aktiv
created: 2026-09-25
updated: 2026-09-25T12:57
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
