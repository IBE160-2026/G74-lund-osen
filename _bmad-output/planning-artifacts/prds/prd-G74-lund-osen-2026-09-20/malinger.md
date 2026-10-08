---
title: "Målinger — grunnlaget for PRD-en"
status: aktiv
created: 2026-09-20
updated: 2026-10-08T22:11
---

# Målinger — grunnlaget for PRD-en

Alle tall PRD-en bygger på, med metode og dato, slik at de kan etterprøves eller
kjøres på nytt. PRD-en beholder konklusjonene; detaljene ligger her.

Grepet er at lesestrømmen ikke skal bære tallene, men at tallene skal finnes og
kunne kontrolleres.

Målingene i §0–§6 er gjort 2026-09-20, §7 er fra 2026-09-21, §8–§10 fra 2026-09-22, og §11 fra 2026-09-23.

---

## 0. Medietesten 17.09.2026

Denne målingen bærer én av de tre begrunnelsene for KI-laget (PRD 4.3), men er
den eneste uten metodebeskrivelse og rådata. Den er ført opp her for å gjøre
mangelen synlig, ikke for å skjule den.

**Hva som er kjent**, gjengitt fra `docs/ai-prompts/product-brief/claude-utkast.md`
linje 19:

> I vår egen test av finansnyheter 17.09 hentet vi ti nyheter for DNB. Flere av
> dem handlet i realiteten om Infosys, om europeiske aksjer generelt eller om
> helt andre selskaper, og nevnte DNB bare fordi selskapet var ett av mange
> symboler i artikkelen. For Frontline var bildet motsatt: nyhetene var i
> hovedsak faktisk om selskapet eller om oljemarkedet det opererer i.

**Metode:** ti nyhetstreff per selskap, lest og vurdert manuelt. To selskaper,
DNB og Frontline.

**Det som mangler:**

| Mangler | Hvorfor det betyr noe |
|---|---|
| Hvilken nyhetskilde treffene kom fra | Kilden er nå avklart som EODHDs nyhets-API, men innsamlingen er avhengig av vilkårskontrollen — se åpent punkt 1, og punkt 5, som ble lukket 26.09. *Rettet 2026-09-26:* her sto «se åpne punkter 1 og 5». |
| Rådata eller loggført resultat per artikkel | Testen kan ikke etterprøves, og kan ikke gjenbrukes som en del av testsettet på 50 |
| Nøyaktig hvor mange av de ti som var feiltreff | «Flere av dem» er ikke et tall. De to andre målingene i dette dokumentet har tall |

**Konsekvens for testsettet på 50 artikler:** motprøven med Frontline viser at
feiltreffraten varierer sterkt med selskapet. Et testsett hentet fra bare én
selskapstype vil måle feil. Sammensetningen må dekke begge mønstrene.

Skal testen bære vekt i innleveringen, bør den kjøres på nytt med kilde, tall og
rådata loggført — slik de to andre målingene er.

---

## 1. Likviditet i aksjeuniverset

**Metode.** Ett `/api/eod`-kall per symbol med `from=2026-06-22`, 15 kall totalt.
65 handelsdager, siste 2026-09-18. Omsetning regnes som `volume × close` per
handelsdag; medianen tas over perioden. Median, ikke gjennomsnitt, fordi
enkeltdager med ekstrem omsetning ellers løfter et symbol som til vanlig
omsettes tynt.

**Rådata.** `data/volumsjekk-raa-2026-09-20.json` — tidsstemplet øyeblikksbilde,
skrives aldri om (jf. FR-406). Fila finnes **bare lokalt** og er ikke sporet i
git; skillet mellom utledede tall som publiseres og datasett som blir liggende,
står i `docs/kilder-og-rettigheter.md`.

| # | Symbol | Selskap | Sektor | Median omsetning | Andel av median |
|---|---|---|---|---:|---:|
| 1 | EQNR | Equinor | Energi | 919,9 MNOK | 4,11× |
| 2 | DNB | DNB Bank | Finans | 400,4 MNOK | 1,79× |
| 3 | KOG | Kongsberg Gruppen | Industri | 374,7 MNOK | 1,67× |
| 4 | AKRBP | Aker BP | Energi | 312,1 MNOK | 1,39× |
| 5 | NHY | Norsk Hydro | Materialer | 293,0 MNOK | 1,31× |
| 6 | FRO | Frontline | Shipping | 284,8 MNOK | 1,27× |
| 7 | VAR | Vår Energi | Energi | 252,9 MNOK | 1,13× |
| 8 | TEL | Telenor | Telekom | 223,9 MNOK | 1,00× |
| 9 | YAR | Yara International | Materialer | 220,5 MNOK | 0,98× |
| 10 | MOWI | Mowi | Sjømat | 182,1 MNOK | 0,81× |
| 11 | ORK | Orkla | Konsum | 140,3 MNOK | 0,63× |
| 12 | SALM | SalMar | Sjømat | 81,8 MNOK | 0,37× |
| 13 | GJF | Gjensidige Forsikring | Finans | 59,8 MNOK | 0,27× |
| 14 | DNO | DNO | Energi | 34,7 MNOK | 0,16× |
| 15 | MPCC | MPC Container Ships | Shipping | 32,3 MNOK | 0,14× |

Median for universet: 223,9 MNOK per dag.

**Funnet som avgjorde kriteriet.** DNO omsetter flere aksjer per dag enn DNB,
men til en lav aksjekurs blir det 34,7 MNOK mot DNBs 400,4 MNOK. MPCC
viser samme mønster. Målt på antall aksjer alene ville begge de lavest omsatte
symbolene sett ut som de hørte hjemme øverst på lista. Derfor måles likviditet i
kroner, ikke i volum.

---

## 2. EODHD — kvote og oppførsel

Hentet fra EODHDs dokumentasjon 2026-09-20.

| Forhold | Hva som gjelder |
|---|---|
| Publiseringstid | Ingen dokumentert tid for Oslo Børs. Generell regel: «2–3 timer etter at børsen stenger». Oslo stenger 16:20 lokal tid, så ~19:20 er *utledet*, ikke dokumentert |
| `from` / `to` | Begge inklusive, `YYYY-MM-DD` |
| Kostnad per kall | Ett kall per symbol **uansett intervallengde** |
| Gratisnivå | 20 kall i døgnet, ett års historikk |
| Kvotenullstilling | Midnatt GMT — dette er *ikke* publiseringstid |
| `adjusted_close` | Regnes om bakover ved hvert nytt utbytte. Dokumentasjonen sier serien skal lastes ned på nytt, ikke skjøtes på |

Konsekvensene er skrevet inn i FR-402 (kontroll mot forventet børsdag),
FR-403 (etterfylling) og FR-406 (to lagre).

---

## 3. NewsWeb — intervall, historikk og resultattak

**Endepunkt:** `api3.oslo.oslobors.no/v1/newsreader/list`, med parametrene
`category`, `issuer`, `fromDate` og `toDate`.

### Intervall og historikk

| Test | Resultat |
|---|---|
| `fromDate` alene | Returnerer ett døgn |
| `fromDate` + `toDate` | Ekte intervall — 175 meldinger over 3 døgn i ett kall |
| Ett år tilbake (2025-09-19) | 59 meldinger, http 200 |
| Tre år tilbake (2023-09-19) | 98 meldinger, http 200 |
| Søndag 2026-09-13 | 2 meldinger — meldinger følger kalenderdøgn, ikke børsdager |

### Resultattaket

| Forespurt intervall | Meldinger | Dager returnert | `data.overflow` |
|---|---:|---|---|
| 2 dager | 226 | 2 av 2 | `false` |
| 5 dager | 555 | 5 av 5 | `false` |
| 6 dager | 557 | 6 av 6 | `false` |
| 7 dager | 557 | 6 av 6 (12.09 var en tom lørdag) | `false` |
| 19 dager | 601 | **7 av 19** | `true` |

Taket ligger mellom 557 og 601 meldinger. API-et returnerer de **nyeste** i
intervallet og forkaster resten med http 200 og ingen feilmelding.

**Parametre uten effekt:** `limit`, `count`, `size`, `length`, `rows`, `page`,
`start`, `offset` — alle testet, ingen endret resultatet.

**Feltet som avslører avkortingen:** `data.overflow`. Udokumentert, men
verifisert i begge retninger. Skrevet inn som FR-405.

---

## 4. Meldingsbildet for universet

**Metode.** 2026-08-22 til 2026-09-18, **28 kalenderdager**, hentet i sju biter
à fire døgn med `overflow` kontrollert i hver. Filtrert til de 15 utstederne.

**Resultat:** 121 meldinger, **4,3 per kalenderdag**. Mengden er ikke problemet.

Fordelingen er ujevn: de 15 selskapene hadde meldinger på bare 19 av 28 dager,
og på de dagene var snittet 6,4. To dager var helt uten meldinger på hele børsen
— søndag 2026-08-23 og lørdag 2026-09-12.

*Rettet 2026-09-20: tallet 26 var antall dager med minst én melding på børsen,
ikke periodens lengde. Perioden er 28 kalenderdager.*

| Kategori | Antall | Andel |
|---|---:|---:|
| Utsteders meldeplikt ved handel i egne aksjer | 35 | 28,9 % |
| Annen informasjonspliktig regulatorisk informasjon | 24 | 19,8 % |
| Ikke-informasjonspliktige pressemeldinger | 18 | 14,9 % |
| Meldepliktig handel for primærinnsidere | 10 | 8,3 % |
| Renteregulering | 10 | 8,3 % |
| Endringer i rettighetene til aksjer/verdipapirer | 7 | 5,8 % |
| Halvårsrapport | 6 | 5,0 % |
| Flagging | 5 | 4,1 % |
| Eks.dato | 3 | 2,5 % |
| Innsideinformasjon | 3 | 2,5 % |

**Meldinger per selskap over fire uker:** TEL 15, SALM 15, EQNR 12, DNB 11,
GJF 10, FRO 9, ORK 8, NHY 7, AKRBP 6, KOG 6, VAR 6, MOWI 5, MPCC 4, DNO 4,
YAR 3.

### Språkdubletter

32 av 121 meldinger (26,4 %) er samme melding på norsk og engelsk, publisert
samme minutt fra samme utsteder. To eksempler:

- Equinors melding om en ny transje i tilbakekjøpsprogrammet, på engelsk og norsk
- DNBs ukentlige statusrapport for tilbakekjøpsprogrammet, på engelsk og norsk

*Titlene er byttet med beskrivelser 2026-09-24 (regel 16 i `CLAUDE.md`). De ligger i historikken.* Kategorien er ikke ført for disse to.

Skrevet inn som FR-501.

### Samlekategorien — belegget for KI-vurderingen

De 18 meldingene i `IKKE-INFORMASJONSPLIKTIGE PRESSEMELDINGER` inneholder både
reelle hendelser og ren støy, med samme kategorifelt:

| Reell hendelse | Støy |
|---|---|
| Aker BP: produksjonsstart på et felt | Hydro: invitasjon til en investordag |
| Kongsberg: et oppkjøp er fullført | MPCC: skal presentere på en investorkonferanse |
| Telenor: et datterselskap får en rammeavtale med en forsvarskunde | Gjensidige: ny leder for investorrelasjoner |
| Telenor: en transaksjon er gjennomført | Gjensidige: analytikerdag |

*Titlene er byttet med beskrivelser 2026-09-24 (regel 16 i `CLAUDE.md`). De ligger i historikken.*

### Tilbakekjøpskategorien — samme problem

Kategorien er `UTSTEDERS MELDEPLIKT VED HANDEL I EGNE AKSJER`
(`begrunnelser.md` §1).

| Reell hendelse | Rutine |
|---|---|
| SalMar: oppstart av et tilbakekjøpsprogram | DNB: ukentlig statusrapport for tilbakekjøpsprogrammet |

*Titlene er byttet med beskrivelser 2026-09-24 (regel 16 i `CLAUDE.md`). De ligger i historikken.*

Ført som åpent punkt 8 i PRD-en.

### Kontroll av briefens eget tall

Briefen oppgir at 15.09.2026 ga 102 meldinger fra 73 utstedere, hvorav 31
rentejusteringer. Kontrollert: alle tre tallene stemmer, `overflow: false`.

Men **ingen av de 31 gjaldt noen av de 15 selskapene i universet**.
Renteregulering kommer fra obligasjonsutstedere.

Døgnet er samtidig et godt eksempel i den *andre* retningen: av de 14 meldingene
som gjaldt universet den dagen, var fire språkdubletter — Equinors tilbakekjøp og
Hydros investordag, begge på norsk og engelsk.

Briefen er rettet 2026-09-20; eksempelet er erstattet med den målte støyen for
vårt eget univers.

---

## 5. Signaltesten

**Metode.** Modellen i FR-701 kjørt mot `data/volumsjekk-raa-2026-09-20.json`.
Alle beregninger på `adjusted_close`.

**Vinduet er tynt:** 50-dagers snittet krever 50 dagers historikk, så av 65
handelsdager gir bare **15** et gyldig signal — 2026-08-31 til 2026-09-18.
Alle tall under er derfor foreløpige.

### Terskel mot volumfaktor

| Volumfaktor | Terskel ≥2: snitt / mest / minst | Terskel ≥3: snitt / mest / minst | Dager uten noen på ≥3 |
|---|---|---|---|
| 1,25× | 7,5 / 15 / 3 | 2,1 / 7 / 0 | 4 av 15 |
| **1,5× (valgt)** | **5,4 / 13 / 2** | 1,6 / 7 / 0 | 7 av 15 |
| 2,0× | 4,8 / 12 / 1 | 0,8 / 7 / 0 | 12 av 15 |

Terskel 3 gir syv av femten dager helt uten utslag. Med volumfaktor 2,0 er tolv
av femten tomme. For en demonstrasjon i uke 45 er det en reell risiko.

### Nøytralsonens virkning

| | Uten nøytralsone | Med ±2 % |
|---|---:|---:|
| Styrke 0 | 0,0 % | 11,1 % |
| Styrke 1 | 64,0 % | 57,8 % |
| Styrke 2 | 25,3 % | 22,7 % |
| Styrke 3 | 10,7 % | 8,4 % |
| Retning positiv | 68,0 % | 65,3 % |
| Retning negativ | 19,6 % | 14,7 % |
| Retning blandet | 12,4 % | 8,9 % |
| Retning ingen | 0,0 % | 11,1 % |

Uten nøytralsone kan signalstyrke 0 ikke forekomme, fordi en aksje alltid ligger
enten over eller under sitt eget snitt. Skrevet inn som FR-702.

### Samvariasjon

Bare 2 av 15 dager hadde 10 eller flere av de 15 over terskel 2. Unntaket var
2026-09-18, med 7 av 15 på bevegelse −1 samtidig. Frykten for at signalet mest
måler «markedet beveget seg» ble altså ikke bekreftet i dette vinduet, men
vinduet er for kort til å avgjøre spørsmålet.

---

## 6. Målinger som gjenstår

| Måling | Formål | Kostnad |
|---|---|---|
| ~~Nyhetstest mot én `.OL`-ticker~~ | ~~Avgjøre om `/api/news` svarer på gratisnivå i det hele tatt~~ | **Gjort 2026-09-21, se §7.2. Kostet 5 kall, ikke 10. Svaret er ja** |
| ~~Har NewsWeb et språkfelt?~~ | ~~Avgjør om FR-501 kan bruke språkkode eller må bygge på heuristikk~~ | **Gjort 2026-09-21, se §7.3. Svaret er nei — heuristikken må beholdes** |
| ~~Signaltest mot ~200 handelsdager~~ | ~~Låse terskel, volumfaktor og nøytralsonebredde~~ | **Gjort 2026-09-21, se §7.4. 15 kall, 199 dager. Alle tre verdiene holdt** |
| Vilkårskontroll NewsWeb + Euronext | Avgjøre om datagrunnlaget holder | 0 kall, frist 2026-09-27. *Rettet 2026-10-03 (kontrollen 26.09, P4):* gjort. Vilkårene til EODHD og Euronext ble kontrollert 2026-09-21 (`prd.md` §2), og fristen gruppen satte for svaret fra Euronext, var 28.09 (åpent punkt 1 i `prd.md` §8) |
| Relevanseksperiment del 1, innsamling av ~50 medieartikler | Grunnlaget for symbolmatching mot KI-klassifisering | `extraLimit`, uke 39–40. Kalltallet kontrolleres i første forespørsel. *Rettet 2026-10-03 (kontrollen 26.09, P4):* gjort 25.09, med 40 kall, 20 fra dagskvoten og 20 fra bonuskvoten (`relevanseksperiment.md` §6) |
| Relevanseksperiment del 2, KI-klassifiseringen | Symbolmatching mot KI-klassifisering | 0 kall mot EODHD. Venter på KI-laget og på betingelse 4 *Lagt til 2026-10-06:* utgår. Marians beslutning 2026-10-06 kl. 21:11: del 2 av relevanseksperimentet kjøres ikke, og story 9.5 utgår. Grunnen er rettighetene: nyhetene kan brukes privat, men ikke i en app som kan bli tilgjengelig for andre, og henvendelsene om dem er ikke besvart. Del 1 viste at mye av nyhetene kunne vært silt bort, og den brukes i refleksjonsrapporten. |
| Kontrollregning av de tre sjekkene *(lagt til 2026-10-01)* | Vise at trend, bevegelse og interesse i aksjedetaljen stemmer: én aksje og én børsdag regnes for hånd i et regneark fra rådatafila i data/, og sammenlignes med tallene appen viser. Regnearket blir liggende lokalt, fordi det inneholder rådata. Bare tallene side om side, og om de stemmer, føres hit | 0 kall. Gjort 2026-10-06, se under |
| Sluttkurs, høy og lav mot Oslo Børs *(lagt til 2026-10-01)* | Vise at kursene fra EODHD stemmer med børsens egne tall: noen dager sammenlignes for hånd med børsens side, lest av en av oss | 0 kall |

**Rekkefølgen er bestemt av kvoten, ikke av prioritet.** Nyhetstesten var
budsjettert til 10 kall og signaltesten til 15; dagsgrensen er 20, så de kunne
ikke kjøres samme dag. Nyhetstesten gikk først fordi et negativt svar velter
relevanseksperimentet, og det måtte oppdages tidlig. Signaltesten kunne vente
et døgn uten at noe annet stoppet. Kvoten nullstilles midnatt GMT.

*Rettet 2026-09-21: nyhetstesten kostet 5 kall, ikke 10 (§7.2). Rekkefølgen
ville vært den samme, men premisset om at de to ikke får plass samme dag holdt
ikke.*

### Kontrollregningen av de tre sjekkene, EQNR 2026-10-05 *(lagt til 2026-10-06)*

EQNR og børsdagen 2026-10-05, regnet for hånd av Joakim i et regneark fra
`data/raa/kurser-raa-2026-10-05.json`, med 51 rader fra 27.07 til 05.10. Appens tall er vurderingen som ble lagret
05.10, lest med `SqliteVurderingslager.les` fra `data/db/ose.db` uten å regne
noe på nytt (AD-7). Regnearket ligger bare lokalt i `data/kontroll/` (regel 10).
Bare de utledede tallene står her, ingen kurser eller volumer (regel 16).

| | Regnearket | Appen (lagret 05.10) | Stemmer |
|---|---|---|---|
| Avvik fra snittet (`trend_avvik`) | 0,0201 | 0,020140 | Ja |
| Endring 05.10 (`dagens_endring`) | 0,0030 | 0,002979 | Ja |
| Standardavvik (`standardavvik`) | 0,0181 | 0,018062 | Ja |
| Volum mot medianen (`volumforhold`) | 0,8798 | 0,879759 | Ja |
| Trend | 1 | 1 | Ja |
| Bevegelse | 0 | 0 | Ja |
| Interesse | 0 | 0 | Ja |
| Styrke | 1 | 1 | Ja |
| Retning | Positiv | Positiv | Ja |

Et tall stemmer når appens verdi, avrundet til fire desimaler, er lik regnearkets.
**Alt stemmer.** Trend lå 0,014 prosentpoeng over grensen på 2 %: avviket
var 2,0140 %. Kontrollen gjelder én aksje og én dag.

### Kontrollregningen av de tre sjekkene, GJF 2026-10-02 *(lagt til 2026-10-06)*

GJF og børsdagen 2026-10-02, regnet for hånd av Joakim i et regneark fra
`data/raa/kurser-raa-2026-10-02.json`, med 51 rader fra 24.07 til 02.10. Appens
tall er vurderingen som ble lagret 02.10, lest med `SqliteVurderingslager.les`
fra `data/db/ose.db` uten å regne noe på nytt (AD-7). Regnearket ligger bare
lokalt i `data/kontroll/` (regel 10). Bare de utledede tallene står her, ingen
kurser eller volumer (regel 16).

**Slik ble dagen valgt:** etter regelen i instruksjonen kl. 22:23 06.10, den
første aksjen og dagen med utslag på bevegelse. Av 45 lagrede aksjedager hadde 8
utslag på bevegelse og ingen på interesse, så vi visste at bevegelse slo ut, men
ikke tallene.

| | Regnearket | Appen (lagret 02.10) | Stemmer |
|---|---|---|---|
| Avvik fra snittet (`trend_avvik`) | -0,0736 | -0,073593 | Ja |
| Endring 02.10 (`dagens_endring`) | 0,0126 | 0,012628 | Ja |
| Standardavvik (`standardavvik`) | 0,0116 | 0,011637 | Ja |
| Volum mot medianen (`volumforhold`) | 0,9598 | 0,959832 | Ja |
| Trend | -1 | -1 | Ja |
| Bevegelse | 1 | 1 | Ja |
| Interesse | 0 | 0 | Ja |
| Styrke | 2 | 2 | Ja |
| Retning | Blandet | Blandet | Ja |

Et tall stemmer når appens verdi, avrundet til fire desimaler, er lik regnearkets.
**Alt stemmer.** Dagens endring var 1,09 ganger standardavviket, regnet fra de
lagrede verdiene. En håndregning av en dag der interesse slår ut, gjenstår.

---

## 7. Målinger 2026-09-21

Seksjonen ligger etter §6 og ikke foran den, for at §1–§6 skal beholde numrene
sine — de er kryssreferert fra `prd.md` og fra gjennomgangene.

### 7.1 Kvotekontroll før nyhetstesten

**Dato:** 2026-09-21, kl. 17:36 lokal tid (15:36 UTC). **Kostnad: 0 kall.**

**Metode.** `GET https://eodhd.com/api/user?api_token=…&fmt=json`. Endepunktet
koster ingenting; EODHDs `/financial-apis/api-limits/` sier om det at «it does
not cost an API call — you can poll it safely from your own monitoring».

**Svar, nøkkelfeltene:**

| Felt | Verdi |
|---|---|
| `apiRequests` | 15 |
| `apiRequestsDate` | 2026-09-20 |
| `dailyRateLimit` | 20 |
| `extraLimit` | 485 |

**Tolkning.** De 15 kallene gjelder 2026-09-20 — det er volumsjekken i §1.
`apiRequestsDate` står på gårsdagen fordi teller og dato henger igjen til første
kall etter nullstillingen. EODHDs brukerdokumentasjon, hentet 2026-09-21:

> Please note, that the number of API requests resets at midnight GMT, but you
> will see the limit for the previous day until an API request is made after
> the reset.

Klokka var 15:36 UTC den 21., altså godt etter nullstillingen midnatt GMT.

**Brukt i dag: 0 av 20. Igjen: 20.** Grensen på ti er ikke i nærheten, og
nyhetstesten i 7.2 kunne kjøres.

`extraLimit: 485` er en egen bonuskvote ved siden av dagsgrensen. Feltet er
observert, ikke testet — vi vet ikke om det er den kvoten
relevanseksperimentet er tenkt å bruke, og det er ikke kontrollert mot
dokumentasjonen.

*Besvart 2026-09-23, §11:* kall nummer 21 lyktes og trakk fra `extraLimit`
(485 → 484). Bonuskvoten brukes automatisk når dagskvoten er tom.

### 7.2 Nyhetstesten mot en `.OL`-ticker

**Dato:** 2026-09-21, kl. 17:38 lokal tid (15:38 UTC). **Kostnad: 5 kall** —
se avsnittet om kalltallet under.

**Formål.** Avgjøre om EODHDs `/api/news` svarer for norske tickere på
gratisnivå i det hele tatt. Hypotesen fra 20.09 var at det ikke gjør det:
`/api/calendar` svarte HTTP 403 med «Only EOD data allowed for free users», og
prissiden sier at alle datatyper er tilgjengelige bare for seks demo-tickere.

**Metode.** Én forespørsel, én ticker:

```
GET https://eodhd.com/api/news?s=DNB.OL&limit=10&api_token=…&fmt=json
```

DNB fordi det er selskapet medietesten 17.09 brukte (§0). Ingen kall etterpå
utenom gratiskontroller mot `/api/user`.

**Rådata.** `data/nyhetstest-raa-2026-09-21.json` — 33 738 byte, tidsstemplet
øyeblikksbilde. Fila finnes bare lokalt og er ikke sporet i git, jf. skillet i
`docs/kilder-og-rettigheter.md`.

#### Utfall: endepunktet svarer

**HTTP 200, ti artikler.** Hypotesen er avkreftet. Gratisnivået gir `/api/news`
for `.OL`-tickere, og 403-svaret på `/api/calendar` kan ikke generaliseres til
de andre endepunktene.

| Forhold | Målt |
|---|---|
| HTTP-status | 200 |
| Artikler returnert | 10 av `limit=10` |
| Datospenn | 2026-06-07 til 2026-09-11 |
| Felter per artikkel | `date`, `title`, `content`, `link`, `symbols`, `tags`, `sentiment` |
| Artikler med `content` | 10 av 10 |
| Artikler med `tags` | 9 av 10 |
| Språkfelt | Finnes ikke |

To ting å merke seg ved siden av hovedspørsmålet. Nyeste artikkel er
2026-09-11, ti dager gammel på målingsdagen — ti treff strekker seg over tre
måneder for DNB. Og `sentiment` følger med som ferdig beregnet objekt
(`polarity`, `neg`, `neu`, `pos`), uten at noe krav ber om det.

#### Kalltallet: 5, ikke 10

`/api/user` viste 0 kall brukt før forespørselen (7.1) og `apiRequests: 5`
umiddelbart etter, kontrollert to ganger med 37 sekunders mellomrom. **Én
forespørsel med én ticker koster 5 kall.**

`docs/kilder-og-rettigheter.md` har siden 20.09 sagt 10, lest ut av denne
setningen i EODHDs dokumentasjon:

> Each request consumes 5 API calls and 5 API calls per ticker. E.g: 10 API
> calls for one request with two tickers

Eksempelet i setningen sier 10 kall for **to** tickere. Lest som «5 for
forespørselen pluss 5 per ticker» skulle to tickere kostet 15, ikke 10. Den
lesningen som passer både eksempelet og målingen, er 5 per ticker, med
forespørselen selv som gulvet. Målingen avgjør spørsmålet for én ticker; for
flere er 5 per ticker fortsatt utledet av eksempelet, ikke målt.

**Konsekvens for relevanseksperimentet:** anslaget på ~80 kall for åtte
selskaper bygger på det doble kalltallet. Med 5 per ticker blir det ~40.

**[UTLEDET] Tallet ~40 er ikke målt.** Det som er målt, er én forespørsel med
én ticker: 5 kall. At åtte tickere koster 5 hver, følger av EODHDs eget
eksempel — «10 API calls for one request with two tickers» — og ikke av noe vi
har kjørt. Samme merking som anslagene per kategori etter deduplisering i §4,
der dublettandelen er målt samlet og ikke per kategori.

**Verifiseringen koster 5 kall** og kan tas sammen med innsamlingen til
relevanseksperimentet: kontroller `apiRequests` før og etter den første
forespørselen med to tickere. Er differansen 10, holder utledningen. Er den 15,
er den opprinnelige lesningen riktig likevel, og budsjettet må dobles.

Tallet er ikke rettet i `prd.md` eller `begrunnelser.md` her, nettopp fordi det
er utledet. Ført som eget punkt i `docs/kilder-og-rettigheter.md`.

*Lagt til 2026-09-25:* målt ved innsamlingen til relevanseksperimentet
(`relevanseksperiment.md` §6). Åtte forespørsler mot `/api/news`, én ticker
hver, kostet **5 kall hver, 40 til sammen**. `limit=20` (DNB) kostet ikke mer
enn `limit=10`. Tallet ~40 over er dermed målt for åtte forespørsler med én
ticker hver. En forespørsel med **flere tickere samtidig er fortsatt ikke
målt**: kontrollen med to tickere ble byttet ut før innsamlingen (`bb54553`),
fordi hvert selskap hentes for seg.

#### Sidefunn: relevansen i de ti treffene

Dette var ikke formålet med testen, og koster ingen ekstra kall å notere. §0
sier at medietesten 17.09 mangler nøyaktig hvor mange av de ti som var
feiltreff. De ti treffene fra i dag, vurdert på tittel og innledning:

| Vurdering | Antall | Artikler |
|---|---:|---|
| Handler om DNB | 3 | Q2-resultatpresentasjon, to analysenotater om verdsettelsen |
| DNB er part i hendelsen, men saken er en annens | 2 | OTP Bank kjøper Luminor av blant andre DNB; Infosys-kontrakt der DNB er kunde |
| Nevner DNB uten å handle om selskapet | 5 | Europeiske aksjer generelt (24 symboler), SalMars tilbakekjøp, to saker om Cadeler, Infosys' AI-kontrakter |

Mønsteret fra 17.09 gjenfinnes: Infosys og «europeiske aksjer generelt» dukker
opp begge ganger. **Dette er ikke en gjentakelse av medietesten.** Én leser har
vurdert ti titler med innledning, ikke blindt og ikke mot et forhåndsdefinert
kriterium, og det er ingen motprøve med Frontline. Mangelen §0 beskriver står
derfor fortsatt åpen. Det dette gir, er et tidsstemplet råmateriale som en
ordentlig kjøring kan bygge på.

#### Kvotestatus etter testen

5 av 20 brukt, **15 igjen**. Signaltesten koster 15 og kunne i prinsippet
kjørts i dag på restkvoten, siden nyhetstesten ble halvparten så dyr som
budsjettert. Den er ikke kjørt — den står til 22.09 etter avtale, og å bruke
hele resten av dagskvoten ville fjernet muligheten til å kontrollere noe som
helst mer i dag.

### 7.3 Har NewsWeb et språkfelt?

**Dato:** 2026-09-21. **Kostnad: 0 EODHD-kall** — NewsWeb koster ingen kvote.

**Metode.** Ett døgn hentet og alle feltnavn i svaret listet opp:

```
GET https://api3.oslo.oslobors.no/v1/newsreader/list?category=&issuer=&fromDate=2026-09-18&toDate=2026-09-18
```

HTTP 200, 86 meldinger, `overflow: false`. **Rådata:**
`data/newsweb-felter-raa-2026-09-21.json` — bare lokalt, ikke sporet i git.

#### Svaret: nei

Meldingsobjektet har 20 felter, og ingen av dem er et språkfelt:

| | Felter |
|---|---|
| Identitet | `id`, `messageId`, `newsId`, `clientAnnouncementId` |
| Utsteder | `issuerId`, `issuerSign`, `issuerName` |
| Instrument | `instrId`, `instrumentName`, `instrumentFullName`, `markets` |
| Innhold | `title`, `category`, `numbAttachments` |
| Korreksjon | `correctionForMessageId`, `correctedByMessageId` |
| Øvrig | `publishedTime`, `test`, `infoRequired`, `oamMandatory` |

Ingen feltnavn inneholder *lang*, *locale*, *culture* eller *språk*. Antakelsen
i `src/meldinger.py` — at NewsWeb kanskje bærer en språkkode — er dermed
avkreftet. FR-501 må bygge på kjennetegn, ikke på et felt.

#### Fire sidefunn

**1. `category` er tospråklig, men det er kategorinavnet, ikke meldingen.**
Feltet er en liste med ett objekt: `{id, category_no, category_en}`. Alle 86
meldingene har nøyaktig én kategori. Begge språkversjonene av samme melding får
samme kategoriobjekt, så feltet skiller dem ikke — men `category_no` er en
stabil nøkkel å slå opp bøttene i FR-502 på, i stedet for en fritekststreng.

**2. Ingen felles nøkkel binder en språkdublett sammen.** `id`, `messageId`,
`newsId` og `clientAnnouncementId` er alle unike — 86 av 86. Equinor-paret
denne dagen har `newsId` 635211 og 635212: naboer, men ikke like. Det finnes
altså ikke noe eksakt ID-par som kunne erstattet kjennetegnet i FR-501.

**3. Kjennetegnet i FR-501 traff 8 av 11 riktig denne dagen.** Utsteder +
kategori + publiseringsminutt slår sammen 11 grupper. Åtte er ekte
språkdubletter. Tre er det ikke:

| Utsteder | Hva som skjedde | Følge |
|---|---|---|
| NOKO | To ulike rentefastsettelser, begge norske, 11:39:37 og 11:39:50 | Harmløs — `RENTEREGULERING` filtreres bort uansett |
| PARB | Samme mønster, 11:38:45 og 11:38:48 | Harmløs, samme grunn |
| GOD | en innkalling til ekstraordinær generalforsamling og en melding om et foreslått ekstra kontantutbytte — to *forskjellige* meldinger, begge engelske, samme minutt og kategori | **Reelt tap.** Kategorien slipper gjennom filteret, så den ene meldingen ville forsvunnet |

Ingen av de tre gjelder de 15 selskapene i universet. Equinor-paret samme dag er
en ekte dublett og håndteres riktig. Én dag er ikke grunnlag for en rate.

**4. `gjett_spraak` tar feil på Euronext-meldingene.** Funksjonen i
`src/meldinger.py` lar æ, ø og å avgjøre alene. Fire engelske titler denne dagen
begynner med «Euronext Oslo Børs – …» og blir derfor klassifisert som norske.
For FROKO, STBYG og NANKO betyr det at den engelske versjonen beholdes der
regelen sier den norske skal vinne. Feilen ligger i heuristikken, ikke i
kjennetegnet.

*Rettet 2026-09-21:* her sto det først at feilen «ikke ville blitt oppdaget av
en test på våre 15 selskaper — de sender ikke meldinger som bærer børsens eget
navn i tittelen». **Den påstanden var for trang.** Mekanismen er ikke bundet til
børsens navn, men til at ett eneste norsk tegn hvor som helst i tittelen
avgjør — og **`VAR` er Vår Energi ASA**. Enhver engelsk melding fra det selskapet
bærer «å» i sitt eget firmanavn og blir lest som norsk.

Kontrollert på funksjonen med konstruerte titler, siden det ene døgnet vi har
hentet ikke inneholder meldinger fra Vår Energi:

| Konstruert tittel | `gjett_spraak` gir |
|---|---|
| `Vår Energi ASA: Third quarter 2026 results` | **norsk** — feil |
| `Vår Energi ASA - Update on drilling programme` | **norsk** — feil |
| `Equinor ASA: Share buy-back programme third tranche` | uavklart |

*Rettet 2026-09-27:* den andre tittelen var bygget av en ekte meldingstittel
fra NewsWeb, ordrett, med et annet selskapsnavn foran. Den engelske delen er
byttet med en konstruert tekst, og `gjett_spraak` gir fortsatt norsk
(regel 16).

At Vår Energi faktisk skriver firmanavnet i titlene sine er utledet av mønsteret
hos de andre — Equinors meldinger 18.09 begynner alle med «Equinor ASA: …» —
ikke målt på selskapets egne meldinger.

**Begrensningen er kjent, ikke lukket.** En retting som ser bort fra børsens navn
fjerner de fire tilfellene fra 18.09, men ikke svakheten: én tegnklasse avgjør
fortsatt alene, og eksempelet over ligger i vårt eget univers. Skal svakheten
fjernes, må regelen bygges om — ikke lappes på.

### Hva dette betyr for FR-501

Funnene over peker samme vei, og formuleres derfor som ett prinsipp, ikke som et
unntak for GOD-tilfellet:

> **Kjennetegnet slår sammen bare når det finnes positivt grunnlag for at det er
> samme melding. Ved tvil beholdes begge.**

Begrunnelsen er at de to feilene ikke koster det samme:

| Feil | Hva brukeren ser | Kostnad |
|---|---|---|
| En dublett slipper gjennom | Samme melding to ganger, på hvert sitt språk | Kosmetikk. Brukeren ser det og forstår det |
| En ekte melding slås sammen bort | Ingenting | **Tap av data.** Brukeren vet ikke at noe mangler, og kan ikke oppdage det |

Asymmetrien avgjør hvilken vei tvilen skal falle. Det henger sammen med
kriteriet i briefen om at **systemet ikke skal tvinge fram et resultat**: en
regel som slår sammen på svakt grunnlag, produserer en ren liste ved å skjule at
grunnlaget var svakt.

Prinsippet er ikke skrevet inn i kravteksten. Vurderingen står i memloggen.

### 7.4 Signaltesten mot 199 handelsdager

**Dato:** 2026-09-21. **Kostnad: 15 kall** — hele restkvoten for døgnet.

**Formål.** Låse de tre parametrene som siden 20.09 har stått merket
`[FORELØPIG]` i `src/signalberegning.py` og i FR-701/FR-702: terskel,
volumfaktor og nøytralsonebredde. Målingen i §5 var gjort mot 15 handelsdager,
fordi MA50 spiste 50 av de 65 vi da hadde hentet.

**Metode.** Ett `/api/eod`-kall per symbol, 15 totalt, med
`from=2025-09-22&to=2026-09-18` — så nær ett års historikk som gratisnivået
tillater. 249 handelsdager per symbol, identisk datoserie for alle 15
(kontrollert). MA50 spiser de første 50, så **199 dager gir gyldig signal:
2025-12-01 til 2026-09-18.**

Modellen er `src/signalberegning.py` kjørt uendret. Alle beregninger på
`adjusted_close`. Hver kombinasjon er regnet på nytt over alle 199 × 15 =
2 985 aksjedager.

**Rådata.** `data/signaltest-raa-2026-09-21.json` — tidsstemplet øyeblikksbilde,
bare lokalt, ikke sporet i git.

#### Terskel mot volumfaktor

| Volumfaktor | Terskel ≥2: snitt / mest / minst | Terskel ≥3: snitt / mest / minst | Dager uten noen på ≥3 | Dager uten noen på ≥2 |
|---|---|---|---|---|
| 1,25× | 5,6 / 15 / 0 | 1,7 / 9 / 0 | 56 av 199 (28 %) | 1 av 199 (0,5 %) |
| **1,5× (valgt)** | **4,6 / 13 / 0** | 1,1 / 7 / 0 | 87 av 199 (44 %) | **5 av 199 (2,5 %)** |
| 2,0× | 4,0 / 12 / 0 | 0,5 / 5 / 0 | 143 av 199 (72 %) | 7 av 199 (3,5 %) |

#### Nøytralsonens bredde

Andel av alle 2 985 aksjedager:

| Sone | Styrke 0 | Styrke 1 | Styrke 2 | Styrke 3 | Positiv | Negativ | Blandet | Ingen |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Uten sone | 0,0 % | 63,9 % | 27,3 % | 8,8 % | 56,8 % | 30,5 % | 12,7 % | 0,0 % |
| ±1 % | 5,6 % | 60,5 % | 25,8 % | 8,1 % | 54,7 % | 28,6 % | 11,1 % | 5,6 % |
| **±2 % (valgt)** | **12,7 %** | 56,3 % | 23,9 % | 7,0 % | 52,4 % | 25,8 % | 9,1 % | 12,7 % |
| ±3 % | 19,1 % | 52,7 % | 22,0 % | 6,2 % | 49,4 % | 24,0 % | 7,5 % | 19,1 % |
| ±4 % | 25,7 % | 49,0 % | 19,7 % | 5,6 % | 46,0 % | 22,2 % | 6,0 % | 25,7 % |

Uten nøytralsone er styrke 0 fortsatt umulig — 0,0 % over 2 985 aksjedager, ikke
bare over 225. FR-702 er dermed bekreftet mot et vindu som er tretten ganger
større.

#### Hva som endret seg fra det korte vinduet

| Forhold | 15 dager (§5) | 199 dager | Vurdering |
|---|---|---|---|
| Terskel ≥2, snitt ved 1,5× | 5,4 | 4,6 | Samme størrelsesorden |
| Terskel ≥3, snitt ved 1,5× | 1,6 | 1,1 | Samme størrelsesorden |
| Dager uten noen på ≥3 (1,5×) | 7 av 15 (47 %) | 87 av 199 (44 %) | **Bekreftet.** Terskel 3 er tom annenhver dag |
| Styrke 0 ved ±2 % | 11,1 % | 12,7 % | Bekreftet |
| Retning positiv | 65,3 % | 52,4 % | **Vesentlig lavere.** Se under |
| Dager med ≥10 av 15 over terskel 2 | 2 av 15 (13 %) | 14 av 199 (7,0 %) | Lavere, og fortsatt lavt |

#### Skjevfordelingen er mindre enn det korte vinduet viste

Åpent punkt 10 sa at 68 % positiv retning skulle vurderes mot året, ikke mot
femten dager. Det er nå gjort.

Målt over 199 dager er **60,0 % av aksjedagene med utslag positive**, mot 29,5 %
negative og 10,5 % blandede. Det korte vinduet fra august–september 2026 lå
altså i en oppgangsperiode og overdrev skjevheten.

Årsaken som ble antatt 20.09 holder likevel — trend er en vedvarende tilstand
mens de to andre er hendelser:

| Sjekk | +1 | 0 | −1 |
|---|---:|---:|---:|
| Trend | 55,3 % | 19,7 % | 25,0 % |
| Bevegelse | 16,7 % | 69,9 % | 13,4 % |
| Interesse | 8,0 % | 85,1 % | 6,9 % |

Trend gir utslag fire av fem dager; de to andre gir utslag sjelden. Retningen
blir derfor i hovedsak trendens fortegn, og aksjene lå over MA50 oftere enn under
i denne perioden. En skjevhet på 60/30 over ti måneder er en egenskap ved
markedet i perioden, ikke ved modellen.

#### Samvariasjon

14 av 199 dager (7,0 %) hadde ti eller flere av de femten over terskel 2. På de
dagene er retningen sjelden entydig: 2026-03-04 hadde elleve aksjer over terskel,
men åtte av dem blandet. Den klareste fellesdagen er **2026-09-18 med 13 av 15,
sju av dem negative** — samme dag som pekte seg ut i det korte vinduet.

Fordelingen er ensidig mot få: 113 av 199 dager har fire eller færre aksjer over
terskel. Frykten for at signalet mest måler «markedet beveget seg» er dermed
ikke bekreftet i et vindu som er langt nok til å svare på spørsmålet.

#### Konklusjon: parametrene holder

Alle tre foreløpige verdiene overlever det brede vinduet, og de låses derfor
uendret:

| Parameter | Verdi | Belegg fra denne målingen |
|---|---|---|
| **Terskel** | **2** | Gir 4,6 av 15 aksjer per dag i snitt, og bare 5 av 199 dager helt uten utslag. Terskel 3 ville gitt 1,1 i snitt og 87 tomme dager |
| **Volumfaktor** | **1,5×** | 1,25× gjør signalet nesten alltid utløst (1 tom dag av 199); 2,0× tømmer terskel 3 på 72 % av dagene. 1,5× ligger mellom |
| **Nøytralsone** | **±2 %** | Gir styrke 0 på 12,7 % av aksjedagene. ±1 % gir bare 5,6 %, ±4 % spiser 6 prosentpoeng av styrke 2 og 3 til sammen |

**De to bekymringene fra §5 er avklart hver sin vei.** Risikoen for en tom
demonstrasjon gjaldt terskel 3, ikke terskel 2 — på terskel 2 er bare 2,5 % av
dagene tomme, og de fem tomme dagene er nettopp de stille dagene briefens
kriterium om robusthet ber om at systemet skal kunne vise. Skjevfordelingen er
reell, men mindre enn fryktet, og forklares av at trend er en tilstand og ikke
en hendelse.

**Dette er en måling, ikke en optimalisering.** Vi har ikke søkt etter
parameterne som gir penest fordeling; vi har kontrollert om de valgte holder
mot et vindu som er langt nok. Det gjør de. En søking ville dessuten hatt et
annet problem: vi har ingen fasit å optimere mot, og modellen skal beskrive hva
som skjedde, ikke forutsi hva som skjer.

---

## 8. Målinger 2026-09-22

### 8.1 Første kjøring av `fetch_prices.py`, med kvotekontroll rundt

**Dato:** 2026-09-22, kl. 10:32–10:34 lokal tid (08:32–08:34 UTC).
**Kostnad: 16 kall** — 15 for universet, pluss ett diagnosekall som ikke burde
vært brukt. Se under.

**Formål.** Kjøre den rettede `fetch_prices.py` for første gang, og måle om
bonuskvoten `extraLimit` tappes automatisk når dagskvoten brukes.

**Metode.** `/api/user` lest før og etter kjøringen. Endepunktet er gratis, og
det er nå målt og ikke bare dokumentert: fire lesninger på rad flyttet ikke
`apiRequests` med ett eneste hakk.

**Lesningen før kjøringen:**

| Felt | Verdi |
|---|---|
| `apiRequests` | 20 |
| `apiRequestsDate` | 2026-09-21 |
| `dailyRateLimit` | 20 |
| `extraLimit` | 485 |

Telleren sto på 20 av 20 klokka 08:32 UTC, altså over åtte timer etter
nullstillingen midnatt GMT. Det er den late nullstillingen §7.1 allerede har
dokumentert med sitat: telleren henger igjen til første kall etter midnatt.

**Diagnosekallet — et kall som ikke burde vært brukt.** Lesningen ble likevel
behandlet som et mulig brudd på premisset om 20 ledige kall, og ett kall mot
`/api/eod/EQNR.OL` ble brukt for å avgjøre saken. Telleren gikk til
`apiRequests: 1`, `apiRequestsDate: 2026-09-22`, og `extraLimit` sto urørt.
Svaret var riktig, men det sto i §7.1 fra før. Kallet var overflødig, og er ført
opp her fordi kvoten er liten nok til at et bortkastet kall skal være synlig.

**Kjøringen.** `uv run python src/fetch_prices.py`, intervall 2025-09-23 til
2026-09-22.

| Forhold | Resultat |
|---|---|
| Symboler hentet | 15 av 15 |
| Feil | ingen |
| Handelsdager per symbol | 249, likt for alle 15 |
| Siste handelsdag i serien | 2026-09-21 (mandag) |
| Fil | `data/kurser-raa-2026-09-22.json` |
| `hentet` | `2026-09-22T08:33:34.919997+00:00` |

249 dager er samme tall som signaltesten fikk 21.09 på et vindu forskjøvet én
dag, slik §7.4 forutsatte.

**Siste handelsdag er i går, ikke i dag.** Kjøringen skjedde 10:33 lokal tid,
mens Oslo Børs fortsatt var åpen, så tirsdagens sluttkurs fantes ikke ennå.
Vinduet er dermed flyttet én *handelsdag* i forhold til gårsdagens
øyeblikksbilde, som endte fredag 2026-09-18. Dette er publiseringstiden i §2
sett i praksis, og bekrefter at FR-402 må kontrollere mot forventet børsdag og
ikke mot dagens dato.

**Lesningen etter kjøringen:**

| Felt | Verdi |
|---|---|
| `apiRequests` | 16 |
| `apiRequestsDate` | 2026-09-22 |
| `dailyRateLimit` | 20 |
| `extraLimit` | 485 |

**Tolkning — og hva målingen ikke svarer på.** 16 = 1 diagnosekall + 15 for
universet. `extraLimit` er uendret på 485.

Spørsmålet var om bonuskvoten tappes automatisk når dagskvoten brukes. **Det er
ikke besvart.** Vi brukte 16 av 20, så dagskvoten ble aldri oppbrukt. Det
målingen viser, er det svakere utsagnet: bonuskvoten tappes ikke så lenge det er
dagskvote igjen. Hva som skjer ved kall nummer 21 — om det gir HTTP 402, om det
trekkes fra `extraLimit`, eller om `extraLimit` må aktiveres først — er fortsatt
åpent, og er det samme forbeholdet §7.1 tok da feltet ble «observert, ikke
testet».

*Besvart 2026-09-23, §11:* HTTP 200, og `extraLimit` sank fra 485 til 484.
Ingen aktivering trengs.

Å svare krever fire kall til i dag, og de kallene tar vi ikke uten at det er
bestemt hva svaret skal brukes til.

**Brukt i dag: 16 av 20. Igjen: 4.**

---

## 9. De to `[FORELØPIG]`-vinduene, målt

**Dato:** 2026-09-22. **Kostnad: 0 kall** — alt er regnet mot
`data/kurser-raa-2026-09-22.json`, øyeblikksbildet fra §8.1.

`VOLATILITET_VINDU` og `VOLUM_VINDU` var de to eneste signalparametrene uten
måling bak seg. §7.4 låste terskel, volumfaktor og nøytralsone mot 199
handelsdager, men testen dekket tre parametre og ikke fem. Vinduene sto merket
`[FORELØPIG]` i `signalberegning.py` og i `prd.md` §4.7, og de utgjorde punkt 4
i utgangsbetingelsen for PRD-ens `draft`-status.

**Spørsmålet var ikke om 20 virker, men om 20 er et valg eller en tilfeldighet.**

### Metode

Like mange aksjedager som §7.4, men ikke de samme: **2 985 aksjedager** — 15
symboler × 199 handelsdager, 2025-12-02 til 2026-09-21. §7.4 regnet på
øyeblikksbildet dagen før, 2025-12-01 til 2026-09-18, så vinduene er forskjøvet
én handelsdag. Grensen på 199 følger av at MA50 krever 50 dager pluss dagen som
måles, altså 51 av seriens 249.

Hvert vindu ble kjørt over spennet 5–65 dager. To mål ble tatt, og det andre
kom til fordi det første ikke kunne svare:

| Mål | Hva det viser |
|---|---|
| **Utslagsrate** | Hvor ofte sjekken gir noe annet enn 0. Samme metrikk §7.4 brukte på trend/bevegelse/interesse |
| **Nabostabilitet** | Hvor mange aksjedager som skifter verdi mellom vindu *w* og *w−5*. Flat kurve betyr at tallet ikke bærer vekt; bratt kurve betyr at det gjør det |

**Et mål som ble forkastet underveis, og hvorfor.** Først ble «hvor mange
aksjedager får et annet signal enn med 20» målt. Den metrikken er **0 ved 20 per
konstruksjon** — den måler avstand fra 20, ikke om 20 er spesiell. Den kunne
aldri ha svart på spørsmålet, og er byttet ut med de to over.

### Resultat

**Bevegelse (`VOLATILITET_VINDU`):**

| Vindu | Utslagsrate | Endring mot *w*−5 |
|---:|---:|---:|
| 5 | 37,0 % | — |
| 10 | 32,1 % | 11,2 % |
| 15 | 30,8 % | 6,7 % |
| **20** | **30,2 %** | **4,7 %** |
| 25 | 29,7 % | 3,5 % |
| 30 | 29,0 % | 2,9 % |
| 40 | 28,4 % | 2,1 % |
| 50 | 27,7 % | 1,3 % |
| 65 | 27,3 % | 1,2 % |

**Interesse (`VOLUM_VINDU`):**

| Vindu | Utslagsrate | Endring mot *w*−5 |
|---:|---:|---:|
| 5 | 14,1 % | — |
| 10 | 14,2 % | 5,5 % |
| 15 | 14,4 % | 3,5 % |
| **20** | **14,8 %** | **3,1 %** |
| 25 | 15,3 % | 2,0 % |
| 30 | 15,6 % | 1,9 % |
| 40 | 17,0 % | 1,6 % |
| 50 | 17,2 % | 1,2 % |
| 60 | **17,5 %** | 0,7 % |
| 65 | 17,4 % | 1,2 % |

**Aksjedager som faller ut: null**, for hvert vindu til og med 49. Grunnen er at
`_nodvendige_dager` tar det lengste vinduet, og MA50 krever allerede 50 dager.
Først ved vindu 50 begynner vinduet å koste dekning: 15 aksjedager ved 50, og
165 ved 60. **Et lengre vindu er gratis helt til det passerer MA50.**

### Tre funn

**1. Utslagsraten går i motsatt retning i de to — men ingen av dem er
monoton.** Bevegelse faller (37,0 → 27,3 %). Interesse stiger til vindu 60
(14,1 → 17,5 %), og ligger 0,1 prosentpoeng lavere ved 65 (17,4 %). Et langt
vindu gjør volatilitetsterskelen høyere og medianvolumet lavere. **Det finnes
derfor ingen vindulengde som er best for begge**, og det er et argument for å
holde dem like på en nøytral verdi framfor å stille hver for seg.

**De 0,1 prosentpoengene er ikke et skille målingen kan bære.** Det er 3
aksjedager: 521 mot 518 av 2 985. Regnet for hvert vindu fra 5 til 65, ikke
bare radene i tabellen, går ingen av kurvene jevnt. Over vindu 15 går interesse
opptil 5 aksjedager *ned* mellom to nabovinduer, og bevegelse opptil 8
aksjedager *opp*. Et steg på 3 ligger innenfor den svingningen. Høyeste
interesse i hele spennet er dessuten vindu 61 (522), ikke 60. Det som er
reelt, er retningen over hele spennet: interesse +3,3 og bevegelse −9,7
prosentpoeng. Retningen på ett enkelt steg er ikke reell.

*Rettet 2026-09-23.* Funnet sa «monoton i begge». Det holdt for radene tabellen
viste, men ikke for tallene bak dem. Hvert vindu 5–65 er regnet på nytt fra
`kurser-raa-2026-09-22.json` med `interesse()` og `bevegelse()` fra
`signalberegning.py`, over de siste 199 dagene per symbol og uten dekningskrav.
Metoden gjenskaper alle ti
interesseverdiene i tabellen. For bevegelse er fire av ni kontrollert (5, 20,
50, 65), og alle fire stemmer.

**2. Knekkpunktet ligger på stabiliteten, ikke på 20.** Nabostabiliteten faller
bratt under 15 og flater ut fra rundt 25. Under 15 bærer tallet reell vekt;
over 25 gjør det nesten ingenting.

**3. 20 ligger på skulderen.** Like over det ustabile området og like under
platået. Målingen peker ikke ut 20 som noe optimum — **alt mellom 15 og 30
oppfører seg tilnærmet likt**.

### Konklusjon: 20 låses, og begrunnelsen er målt

Begge vinduene låses på **20**, og `[FORELØPIG]` fjernes.

Begrunnelsen er ikke at 20 er best, for det viser målingen ikke. Den er at **20
ligger i et område der modellen ikke er følsom for valget** — nabostabiliteten
er 3–5 % ved 20 og faller videre — samtidig som den ligger klar av det ustabile
området under 15, der valget ville båret vekt det ikke kan forsvare. Et tall
plukket under 15 måtte vært begrunnet; et tall i platået kunne vært hva som
helst.

At vinduet er gratis i dekning opp til 49 er verdt å merke, men det er ikke et
argument for å øke: utslagsratene beveger seg i hver sin retning, så et lengre
vindu kjøper stabilitet i bevegelse på bekostning av at interesse slår ut
oftere.

**Dette er en måling, ikke en optimalisering** — samme forbehold som §7.4. Vi
har ikke søkt etter vinduene som gir penest fordeling; vi har kontrollert om det
arvede tallet ligger et sted der det kan forsvares. Det gjør det, og nå står det
et sted som viser hvorfor.

**Med dette er alle fem signalparametrene målt.** §7.4 låste terskel,
volumfaktor og nøytralsone; denne paragrafen låser de to vinduene.

---

## 10. Kan EODHDs nyhetsendepunkt bære KI-laget?

**Dato:** 2026-09-22. **Kostnad: 0 kall** — alt er lest av
`data/nyhetstest-raa-2026-09-21.json`, øyeblikksbildet fra §7.2, og av vår egen
korrespondanse.

**Formål.** Avgjøre om `/api/news` kan erstatte NewsWeb som driftskilde for
KI-laget hvis Euronext svarer nei 28.09 (åpent punkt 1). Spørsmålet ble stilt i
to trinn, der trinn 1 — rettighetene — ikke skulle koste kall.

### Rettighetene

**Godkjenningen dekker nyhetsendepunktet eksplisitt.** Spørsmålet som ble
besvart «ja, med fire betingelser» navnga `/api/news`, og svaret gjentar det:

> Yes, we approve the limited use you described: **sending headlines and article
> text obtained through our News API** to a third-party language model solely to
> classify company relevance for your private, non-commercial course project.

*Til sammenligning* gjaldt «Yes, we confirm both» fra samme kveld de **to andre**
spørsmålene — «displaying» i undervisning og sammendragsstatistikk i et
offentlig repo. Ikke nyhetene.

**Men EODHD eier ikke innholdet.** Alle ti artiklene i øyeblikksbildet peker til
`finance.yahoo.com`, og `content` er syndikert utdrag — den første ender på
«Continue Reading» etter 394 tegn. EODHD er et mellomledd.

Det er strukturelt samme forhold som hos Euronext: en leverandør gir tillatelse
over innhold den distribuerer, ikke eier. Prosjektet har presedensen fra før —
E24-klausulen i `docs/kilder-og-rettigheter.md` forbyr uttrykkelig å bruke
«article headlines, summaries, links, full-text, images, metadata or other
elements» som input til språkmodeller, og den kilden ble forkastet av nettopp
den grunnen.

Det som taler den andre veien: EODHD visste hva API-et returnerer da de
godkjente «article text obtained through our News API». Men svaret er fra EOD
Support Team, og `kilder-og-rettigheter.md` fører det selv som «belegg for hva
leverandøren aksepterer, ikke en tolkning av vilkårene som binder dem».

### Kvoten

Målingen i §7.2: **én forespørsel med én ticker koster 5 kall.** Daglig drift
for universet blir 15 × 5 = **75 kall per dag**, mot en dagskvote på 20.
Bonuskvoten på 485 ville holdt i seks dager.

Som *driftskilde* er det derfor utelukket uavhengig av rettighetsspørsmålet.

### Hva kilden faktisk inneholder

Målt på de ti DNB-artiklene:

| Forhold | Målt |
|---|---|
| Språk | **Engelsk, 10 av 10.** Ingen norske saker |
| Tekstens form | Utdrag, ikke hel artikkel. 394–4 719 tegn; den korteste ender på «Continue Reading» |
| Utgiverfelt | **Finnes ikke.** Feltene er `date`, `title`, `content`, `link`, `symbols`, `tags`, `sentiment` — ingen av dem navngir utgiveren |
| Kategori | **Tematisk, ikke regulatorisk.** 31 unike `tags` over ti artikler, 9 av 10 har minst én. Ingen motsvarighet til NewsWebs meldepliktkategorier |
| Saker med selskapet i tittelen | **4 av 10** |
| Ytterpunktet | Én sak bærer `DNB.OL` blant **24 symboler** og nevner DNB **null ganger** i teksten |

**Dette lukker delvis hullet i §0.** Medietesten 17.09 sa «flere av dem handlet i
realiteten om Infosys, om europeiske aksjer generelt», og §0 noterer selv at
«flere av dem» ikke er et tall. Tallet for DNB er **6 av 10 uten selskapet i
tittelen**, og mønsteret §0 beskrev — Infosys, europeiske aksjer generelt —
gjenfinnes ordrett i titlene. Målingen gjelder ti artikler for ett selskap og
erstatter ikke et testsett, men den er ikke lenger uten tall.

### Konklusjon: det er et annet produkt

Spørsmålet var om FR-601..606 kan skrives om til denne kilden uten at kravene
endrer karakter. **Det kan de ikke**, og grunnen er ikke språket eller formatet:

Regelfilteret sorterer på NewsWebs **regulatoriske** kategoritaksonomi
(FR-502, tre bøtter): hvilken meldeplikt meldingen oppfyller.

EODHDs nyheter har tagger — **31 unike over ti artikler, 9 av 10 har minst én**
— men de er **tematiske**, som tagger om tilbakekjøp, resultater, oppkjøp og
verdsettelse. De sier hva saken handler om, ikke hvilken meldeplikt den
oppfyller.

Forskjellen er ikke akademisk. En tagg om tilbakekjøp skiller ikke den
ukentlige statusrapporten under «Utsteders meldeplikt ved handel i egne aksjer»
— som FR-502 filtrerer bort, 35 av 121 meldinger — fra oppstarten av et nytt
program, som er ekte nyhet. Det er nøyaktig skillet **åpent punkt 8** handler
om, og EODHDs taksonomi kan ikke uttrykke det. **FR-502s bøtter kan ikke
utledes av den**, og måtte bygges om fra grunnen.

*Rettet 2026-09-22 etter kontroll.* Paragrafen sa opprinnelig at `tags` er tom
og at reglene derfor ikke har noen jobb. Det var feil: kontrollen så på artikkel
1, som er den ene av ti uten tagger, og §7.2 i denne filen sier det riktige.
Konklusjonen står, men på et annet og bedre grunnlag — og **påstanden om at
kilden ikke *kan* brukes, var for sterk.** Et regelfilter kunne bygges på disse
taggene; det ville bare ikke vært FR-502, og kontrasten FR-604 måler ville
måttet defineres på nytt. Det som faktisk stenger kilden for drift, er
rettighetene og kvoten — og de er uavhengige av taksonomien.

Videre sier seksjonsingressen i §4.6: *«KI-laget brukes ikke til å avgjøre
hvilket selskap en melding gjelder — den jobben gjør `issuerSign` bedre og
gratis.»* EODHDs nyheter har ingen `issuerSign`, og 6 av 10 saker er ikke om
selskapet. KI-oppgaven ville dermed blitt **nettopp den oppgaven PRD-en sier den
ikke skal ha**.

Det er relevanseksperimentets oppgave, ikke driftsoppgaven. **Relevanseksperimentet
står urørt** og kjøres på plan A som planlagt — ~50 artikler, én gang, lokalt,
rundt 40 kall.

*Dette er en vurdering, ikke en beslutning.* Den er lagt under åpent punkt 1.

---

## 11. Kvoten brukt opp med vilje, og gjentatt henting samme dag

**Dato:** 2026-09-23, kl. 19:03–19:05 lokal tid (17:03–17:05 UTC).
**Kostnad: 21 kall** — 20 av dagskvoten og ett fra bonuskvoten. Kallene var avtalt
på forhånd og hadde tre spørsmål:

1. Hva `/api/user` viser etter en full henting.
2. Om to hentinger samme dag gir samme data.
3. Hva som skjer med kall nummer 21.

**Metode.** `/api/user` ble lest før og etter hvert steg. Endepunktet er gratis,
jf. §7.1. Bare kvotefeltene er ført her. Svaret inneholder også navn og e-post,
og de er ikke skrevet ned noe sted. Rådata ligger i `data/`, som er gitignorert:

| Fil | Innhold |
|---|---|
| `kurser-raa-2026-09-23.json` | Steg 1, alle 15, skrevet av `fetch_prices.py` |
| `gjentak-raa-2026-09-23.json` | Steg 2, fem symboler hentet på nytt |
| `kall21-raa-2026-09-23.json` | Steg 3, HTTP-status, rate-limit-headere og hele responsen |

Ingen kode i repoet ble endret. Steg 2 og 3 brukte skript utenfor repoet som kaller
den eksisterende `hent_ett_symbol`, eller `BASE_URL` direkte.

### Kall for kall

| Tid (UTC) | Steg | `apiRequests` | `apiRequestsDate` | `extraLimit` |
|---|---|---:|---|---:|
| 17:03:50 | Før alt | 16 | 2026-09-22 | 485 |
| 17:04:12 | Etter steg 1, 15 kall | 15 | 2026-09-23 | 485 |
| 17:04:31 | Etter steg 2, 5 kall | 20 | 2026-09-23 | 485 |
| 17:05:07 | Før kall 21 | 20 | 2026-09-23 | 485 |
| 17:05:09 | Etter kall 21 | **20** | 2026-09-23 | **484** |

**Før alt:** telleren sto på 16 med datoen 22.09, altså gårsdagens telling. Den
blir hengende til første betalte kall etter midnatt GMT (§7.1). Brukt 23.09 før
målingen: **0**.

### Steg 1 — full henting, 15 kall

`uv run python src/fetch_prices.py`, intervall 2025-09-24 til 2026-09-23. Alle
15 svarte med 249 handelsdager. **Siste dag er 2026-09-22 for alle** — kl. 19:04
lokal tid var 23.09 ikke publisert ennå, jf. publiseringstiden i §2. Telleren
gikk fra «16 i går» til 15 i dag. `extraLimit` sto urørt.

### Steg 2 — fem hentet på nytt, 5 kall

EQNR, DNB, KOG, AKRBP og NHY, med samme intervall som steg 1. **Alle fem er
identiske med steg 1**, felt for felt i alle 249 rader. Telleren gikk til 20.

**Hva dette prøver, og hva det ikke prøver.** AD-5 bygger på at EODHD regner
`adjusted_close` om bakover når det kommer et nytt utbytte. To hentinger med to
minutters mellomrom, uten noe nytt utbytte imellom, viser at hentingen gir samme
svar hver gang. De prøver ikke premisset.

**En prøve som kommer nærmere, uten kostnad:** i går (`kurser-raa-2026-09-22.json`,
hentet 22.09 kl. 10:33 lokal tid) og i dag har 248 felles datoer for hvert av de
15 symbolene. Sammenlikningen viser:

| Felt | Ulike verdier over 15 × 248 |
|---|---:|
| `close` | 0 |
| `adjusted_close` | 0 |
| `volume` | **1** |

**Ingen `adjusted_close` ble regnet om mellom 22.09 og 23.09.** AD-5-premisset
er dermed verken bekreftet eller avkreftet, fordi ingen av de 15 hadde nytt
utbytte i vinduet. Det ene avviket er MOWI 2026-09-21: `volume` ble **justert
ned 0,8 %** ved neste henting, med `close` uendret. 21.09 var den
**siste** raden i gårsdagens øyeblikksbilde. Den ble hentet mens børsen var åpen,
dagen etter. Den nyeste raden kan altså bli korrigert i etterkant. Det er en
annen grunn enn utbyttet til at serien aldri skjøtes på (AD-5): en skjøtet serie
ville beholdt det foreløpige tallet. Ett tilfelle er ikke en rate.

### Steg 3 — kall nummer 21

Ett `/api/eod`-kall for EQNR.OL etter at dagskvoten var brukt opp.

**Utfall: kallet lykkes, og `extraLimit` synker.** HTTP 200, hele serien
(249 rader, 28 701 tegn), identisk med EQNR fra steg 1. `apiRequests` står fortsatt
på 20, og `extraLimit` gikk fra 485 til 484.

Råsvaret ligger lokalt i `data/kall21-raa-2026-09-23.json` og publiseres ikke.

Svaret hadde headerne `X-RateLimit-Limit: 1200` og `X-RateLimit-Remaining: 1198`.
Det er en annen grense enn dagskvoten, og den er ikke tolket her.

### Hva dette avgjør

**Spørsmålet fra §7.1 og §8.1 er besvart: bonuskvoten tappes automatisk når
dagskvoten er brukt opp.** Den trenger ikke aktiveres, og kall 21 gir ingen
feilkode. To konsekvenser:

- **Relevanseksperimentet kan trekke fra `extraLimit`** (punkt 5, lukket
  26.09). Kalltallet er målt 25.09: 5 kall per forespørsel med én ticker, og 40
  kall for de åtte selskapene, 20 fra dagskvoten og 20 fra bonuskvoten
  (`relevanseksperiment.md` §6). *Rettet 2026-09-26:* her sto «(åpent punkt 5).
  Kalltallet per ticker (§7.2, «~40 kall») er fortsatt utledet og ikke målt.»
- **En henting for mye tar ikke stopp, den koster bonuskvote.** NFR-01 og
  FR-402-kontrollen er det som hindrer at 485 bonuskall går tapt stille. Hentes det
  to ganger om dagen, stopper det ikke ved 20. Det tærer på bonusen.
  *Rettet 2026-10-03 (kontrollen 26.09, P2):* 485 er tallet før kall 21 den 23.09. Bonuskvoten synker når den brukes: 484 etter kall 21, 464 etter innsamlingen til relevanseksperimentet 25.09 (`relevanseksperiment.md` §6) og 463 etter OSEBX-kallet 30.09 (§14).

Det målingen **ikke** avgjør: om det finnes noe tak når `extraLimit` når 0.
Det er ikke prøvd, og det skal ikke prøves.

---

## 12. Kvotemåling og kveldshenting 2026-09-24

**Dato:** 2026-09-24, kl. 21:31:44–21:31:54 norsk tid (19:31 UTC). **Kostnad:
15 kall**, avtalt på forhånd (regel 6 og 15 i `CLAUDE.md`).

**Formål.** Svare på åpent punkt 23 med en henting etter børsens stengetid, og
se om gårsdagens rader endret seg.

**Metode.** `/api/user` lest før og etter. Hentekommandoen (`fetch_prices.py`)
kjørt én gang for alle 15 symbolene. Det nye øyeblikksbildet er sammenlignet
med det fra 23.09 på de felles datoene, og lest med `SnapshotLeser` (story 1.4a).
Bare utledede tall er ført her (regel 16). Rådata ligger lokalt i
`data/kurser-raa-2026-09-24.json`.

### Kvoten

| | Før | Etter |
|---|---|---|
| `apiRequests` | 20 | 15 |
| `apiRequestsDate` | 2026-09-23 | 2026-09-24 |
| `extraLimit` | 484 | 484 |

«20» før gjaldt gårsdagen: datoen sto på 23.09, så det var brukt 0 kall i dag
(§7.1). **Kjøringen trakk nøyaktig 15 kall**, og ingenting fra bonuskvoten.

### Åpent punkt 23: er dagens rad der?

**Ja, for alle 15.** Kl. 21:31 norsk tid hadde alle 15 serier en rad for
2026-09-24, og siste dato var 24.09 for alle. Hentingen 23.09 kl. 19:04 hadde
ingen rad for 23.09 (§11). Den raden er med nå, så begge dagene kom inn i
kveldens henting.

Det dette viser, er at dagens rad fantes kl. 21:31, ikke når den kom. Tidspunktet
ligger et sted mellom 19:04 og 21:31, målt på to forskjellige dager. Om raden
for 24.09 er endelig, viser først neste henting.

*Svar 2026-10-07 (§22):* neste henting viste det, og det samme gjelder alle
kveldshentingene til og med 06.10. `close` og `adjusted_close` er endelige.
`volume` er det nesten: 6 av 90 rader hentet etter kl. 22 fikk et litt høyere
volum dagen etter, med opptil 6,9 %. Raden for 24.09 var uendret bortsett fra
volumet for AKRBP, som var 0,04 % høyere 29.09.

### Endringer mot øyeblikksbildet fra 23.09

**Null.** På de 3 720 felles aksjedagene (15 symboler × 248 datoer) er det ingen
endring i `close`, `adjusted_close` eller `volume`. Siste felles dato er 22.09,
og den raden var hentet 23.09 kl. 19:04, etter at børsen stengte.

Datoene som ikke er felles, følger av at hentevinduet flyttet seg én dag: 2025-09-24
falt ut i starten (15 rader), og 2026-09-23 og 2026-09-24 kom inn i slutten
(30 rader). Hver serie har derfor 250 rader, mot 249 i øyeblikksbildet fra 23.09.

### Lest med `SnapshotLeser`

15 symboler, 3 750 rader, ingen manglende. `sist_hentet` er hentetidspunktet i
UTC for alle 15.

---

## 13. Sjømat: fem kandidater mot kriteriet i §3 (2026-09-30)

**Metode.** Som i §1: ett `/api/eod`-kall per symbol, med `from=2026-06-30` og
`to=2026-09-30`. Omsetning regnes som `volume × close` per handelsdag, og
medianen tas over perioden. Kravet er en median daglig omsetning over 25 MNOK
(`prd.md` §3). Målingen er første målerunde for idéen «Egne aksjelister» i
v1.1-tabellen i `prd.md` §8.

**Kostnad.** 5 kall, tatt av dagskvoten 30.09 etter den daglige hentingen på
15. Ingen kall feilet.

**Rådata.** `data/raa/maaling-sjomat-raa-2026-09-30.json`. Fila finnes **bare
lokalt** og er ikke sporet i git. Bare tallene under er regnet ut og ført her.

| Symbol | Selskap | Handelsdager | Median omsetning | Over 25 MNOK |
|---|---|---:|---:|---|
| BAKKA | Bakkafrost | 67 | 36,7 MNOK | Ja |
| LSG | Lerøy Seafood Group | 67 | 18,3 MNOK | Nei |
| AUSS | Austevoll Seafood | 67 | 9,7 MNOK | Nei |
| GSF | Grieg Seafood | 67 | 6,7 MNOK | Nei |
| SALME | Salmon Evolution | 67 | 2,6 MNOK | Nei |

Alle fem har 67 handelsdager, fra 2026-06-30 til 2026-09-30.

Ingen av dem er lagt i universet, fordi AD-21 holder `aksje` lik `AKSJEUNIVERS`,
og egne aksjelister er en idé til v1.1.

---

## 14. OSEBX på gratisnivået (2026-09-30)

**Metode.** Ett `/api/eod`-kall for `OSEBX.OL`, med `from=2025-10-01` og
`to=2026-09-30`. Kallet ble ikke prøvd på nytt.

*Lagt til 2026-10-01:* EODHD fører indeksen som `OSEBX.OL`, «OSE Benchmark», med
typen Index, på https://eodhd.com/financial-summary/OSEBX.OL. Siden er lest av
rådet og hentes ikke av programmet.

**Kostnad.** 1 kall fra `extraLimit`, etter at dagskvoten var brukt opp av
hentingen og sjømatmålingen (§13). `apiRequests` sto på 20 før og etter, og
`extraLimit` gikk fra 464 til 463, som §11 viste for kall nummer 21.

**Rådata.** `data/raa/maaling-osebx-raa-2026-09-30.json`. Fila finnes **bare
lokalt** og er ikke sporet i git. Ingen tall fra serien er ført her.

**Svaret:**

- HTTP 200. Gratisnivået gir indeksdata for `OSEBX.OL`.
- 255 rader, fra 2025-10-01 til 2026-09-30.
- Feltene er de samme som for aksjene: `date`, `open`, `high`, `low`,
  `close`, `adjusted_close` og `volume`.
- `volume` finnes på alle rader og er 0 på én (2025-10-03).
- `close` og `adjusted_close` er like på alle 255 radene.
- Aksjene har 250 rader over samme periode (EQNR i basen). Indeksen har fem
  datoer som aksjene ikke har: 2025-12-24, 2025-12-31, 2026-04-02, 2026-05-14
  og 2026-05-25. De tre i 2026 står som stengte dager i `STENGT` i
  `src/boersdag.py`. Lista dekker ikke 2025, men ingen av de 15 aksjene har
  rader for de to datoene i desember. Hver dato EQNR har, finnes også i
  indeksen. *Rettet 2026-09-30:* her sto «som alle er norske helligdager». Det
  var ikke slått opp, og 2025-12-24 og 2025-12-31 er ingen helligdager.

Om sluttkursen stemmer med Oslo Børs, avgjøres for hånd av en av oss, og bare
svaret føres her.

*Lagt til 2026-10-01:* Kontrollert for hånd av Marian 01.10. `close` for 2026-09-30 i råfila er, avrundet til to desimaler, lik sluttverdien hun hadde fra Oslo Børs samme dag. Ingen tall er ført (regel 16).

---

## 15. OBX: fem aksjer utenom de 15 (2026-10-02)

**Metode.** Som i §13: ett `/api/eod`-kall per symbol, med `from=2026-07-02` og
`to=2026-10-02`. Omsetning regnes som `volume × close` per handelsdag, og
medianen tas over perioden. Målingen er den første etter raden «Måling av
omsetning med kall til overs» i v1.1-tabellen i `prd.md` §8, kjørt for hånd
etter at kveldens henting hadde gått bra, med de kallene som var igjen.

De fem er de første av de 12 aksjene i OBX som ikke er blant de 15.
OBX-sammensetningen fra 21.09.2026 er lest av et menneske i Euronexts
pressemelding, ikke hentet av programmet. De 7 andre måles senere: Vend
Marketplaces, Höegh Autoliners, Nordic Semiconductor, Norwegian Air Shuttle,
TGS, Tomra og BlueNord. Vend heter Schibsted til 2025, så tickeren hos EODHD
slås opp før den måles.

*Rettet 2026-10-03:* sammensetningen ble satt sammen av rådet fra flere offentlige kilder, ikke lest som én liste i pressemeldingen. Kongsberg Maritime er utledet av utskillelsen fra Kongsberg Gruppen i april 2026, ikke lest direkte. Av de 15 er alle unntatt DNO og MPCC i OBX.

**Kostnad.** 5 kall, tatt av dagskvoten 02.10 etter den daglige hentingen på
15. `apiRequests` gikk fra 15 til 20, og `extraLimit` sto på 463 før og etter.
Ingen kall feilet, og ingen kall er igjen til en ny kjøring samme dag.

**Rådata.** `data/raa/maaling-obx-raa-2026-10-02.json`. Fila finnes **bare
lokalt** og er ikke sporet i git. Bare tallene under er regnet ut og ført her.

| Symbol | Selskap | Handelsdager | Median omsetning | Over 32 MNOK | Over 25 MNOK |
|---|---|---:|---:|---|---|
| AKER | Aker | 67 | 150,5 MNOK | Ja | Ja |
| SUBC | Subsea 7 | 67 | 83,7 MNOK | Ja | Ja |
| STB | Storebrand | 67 | 87,8 MNOK | Ja | Ja |
| KMAR | Kongsberg Maritime | 67 | 58,3 MNOK | Ja | Ja |
| BWLPG | BW LPG | 67 | 70,4 MNOK | Ja | Ja |

«Over 32 MNOK» betyr innenfor målingen: de 15 omsettes for 32 til 920 MNOK om
dagen (`prd.md` §3). «Over 25 MNOK» er kriteriet i `prd.md` §3.

Alle fem har 67 handelsdager, fra 2026-07-02 til 2026-10-02.

Ingen av dem er lagt i universet.

---

## 16. Helgemåling: 20 aksjer (2026-10-03)

**Metode.** Som i §15: ett `/api/eod`-kall per symbol, med `from=2026-07-02` og
`to=2026-10-02`, samme vindu. Omsetning regnes som `volume × close` per
handelsdag, og medianen tas over perioden. Målingen ble kjørt lørdag 03.10, da
børsen var stengt og ingen henting trengte kallene. Marians beslutning 02.10
kl. 23:26: på dager uten henting kan alle 20 kallene brukes til måling.

De 7 første er resten av OBX, de som §15 sa skulle måles senere. De 13 neste er
de største av resten, målt i markedsverdi. Markedsverdien er bare brukt som en
rekkefølge for målingen, og er ikke et tall appen bruker. Tickeren til Vend hos
EODHD er `VEND.OL`, og den ga rader for hele perioden.

**Kostnad.** 20 kall, tatt av dagskvoten 03.10. Før målingen sto
`apiRequestsDate` på 2026-10-02, altså 0 brukt i dag. Etter første kall sto
`apiRequests` på 1 med datoen 2026-10-03, og `extraLimit` var uendret på 463.
Etter målingen er `apiRequests` 20 og `extraLimit` fortsatt 463. Ingen kall
feilet, ingen symboler var tomme, og ingen dagskall er igjen.

**Rådata.** `data/raa/maaling-raa-2026-10-03.json`. Fila finnes **bare
lokalt** og er ikke sporet i git. Bare tallene under er regnet ut og ført her.

| Symbol | Selskap | Handelsdager | Median omsetning | Over 32 MNOK | Over 25 MNOK |
|---|---|---:|---:|---|---|
| VEND | Vend Marketplaces | 67 | 108,7 MNOK | Ja | Ja |
| HAUTO | Höegh Autoliners | 67 | 57,0 MNOK | Ja | Ja |
| NOD | Nordic Semiconductor | 67 | 132,5 MNOK | Ja | Ja |
| NAS | Norwegian Air Shuttle | 67 | 70,2 MNOK | Ja | Ja |
| TGS | TGS | 67 | 49,7 MNOK | Ja | Ja |
| TOM | Tomra | 67 | 45,7 MNOK | Ja | Ja |
| BNOR | BlueNord | 67 | 78,4 MNOK | Ja | Ja |
| SB1NO | SpareBank 1 Sør-Norge | 67 | 31,7 MNOK | Nei | Ja |
| WAWI | Wallenius Wilhelmsen | 67 | 47,6 MNOK | Ja | Ja |
| CMBTO | CMB.TECH | 67 | 47,6 MNOK | Ja | Ja |
| AUTO | AutoStore | 67 | 52,1 MNOK | Ja | Ja |
| HAFNI | Hafnia | 67 | 35,0 MNOK | Ja | Ja |
| PROT | Protector Forsikring | 67 | 30,7 MNOK | Nei | Ja |
| SBNOR | Sparebanken Norge | 67 | 19,1 MNOK | Nei | Nei |
| WWI | Wilh. Wilhelmsen Holding | 67 | 8,3 MNOK | Nei | Nei |
| DOFG | DOF Group | 67 | 34,0 MNOK | Ja | Ja |
| OET | Okeanis Eco Tankers | 67 | 46,1 MNOK | Ja | Ja |
| MING | SpareBank 1 SMN | 67 | 17,8 MNOK | Nei | Nei |
| VEI | Veidekke | 67 | 10,0 MNOK | Nei | Nei |
| SPOL | SpareBank 1 Østlandet | 67 | 5,2 MNOK | Nei | Nei |

«Over 32 MNOK» betyr innenfor målingen: de 15 omsettes for 32 til 920 MNOK om
dagen (`prd.md` §3). «Over 25 MNOK» er kriteriet i `prd.md` §3. 13 av de 20 er
over 32 MNOK, og 15 er over 25 MNOK.

Alle 20 har 67 handelsdager, fra 2026-07-02 til 2026-10-02.

Selskapsnavnene for de 13 siste er ikke slått opp i en kilde i denne økta, og
svaret fra `/api/eod` har ingen navn. De føres når de er slått opp.

*Rettet 2026-10-03:* navnene på de 13 siste er ført inn. Her sto «ikke slått opp». Navnene er slått opp av rådet 03.10 på offentlige kurssider, blant dem Euronext, Bloomberg, Yahoo Finance og eodhd.com.

Ingen av dem er lagt i universet.

---

## 17. De 15 i samme vindu, og alle 40 rangert (2026-10-03)

**Metode.** Som i §15 og §16: omsetning regnes som `volume × close` per
handelsdag, og medianen tas over perioden fra 2026-07-02 til 2026-10-02. Tallene
er regnet fra `data/raa/kurser-raa-2026-10-02.json`, kveldens henting 02.10, uten
nye kall. Fila finnes **bare lokalt** og er ikke sporet i git. Bare tallene under
er regnet ut og ført her.

**Kostnad.** 0 kall.

### De 15 i universet

Alle 15 har 67 handelsdager i vinduet, fra 2026-07-02 til 2026-10-02.

| Symbol | Selskap | Handelsdager | Median omsetning | Over 32 MNOK | Over 25 MNOK | §1, annet vindu |
|---|---|---:|---:|---|---|---:|
| EQNR | Equinor | 67 | 937,9 MNOK | Ja | Ja | 919,9 MNOK |
| DNB | DNB Bank | 67 | 391,2 MNOK | Ja | Ja | 400,4 MNOK |
| KOG | Kongsberg Gruppen | 67 | 363,6 MNOK | Ja | Ja | 374,7 MNOK |
| AKRBP | Aker BP | 67 | 312,1 MNOK | Ja | Ja | 312,1 MNOK |
| NHY | Norsk Hydro | 67 | 276,7 MNOK | Ja | Ja | 293,0 MNOK |
| FRO | Frontline | 67 | 303,2 MNOK | Ja | Ja | 284,8 MNOK |
| VAR | Vår Energi | 67 | 252,9 MNOK | Ja | Ja | 252,9 MNOK |
| TEL | Telenor | 67 | 226,2 MNOK | Ja | Ja | 223,9 MNOK |
| YAR | Yara International | 67 | 213,1 MNOK | Ja | Ja | 220,5 MNOK |
| MOWI | Mowi | 67 | 187,5 MNOK | Ja | Ja | 182,1 MNOK |
| ORK | Orkla | 67 | 140,3 MNOK | Ja | Ja | 140,3 MNOK |
| SALM | SalMar | 67 | 83,3 MNOK | Ja | Ja | 81,8 MNOK |
| GJF | Gjensidige Forsikring | 67 | 60,5 MNOK | Ja | Ja | 59,8 MNOK |
| DNO | DNO | 67 | 40,5 MNOK | Ja | Ja | 34,7 MNOK |
| MPCC | MPC Container Ships | 67 | 33,9 MNOK | Ja | Ja | 32,3 MNOK |

§1 gjaldt et annet vindu, fra 2026-06-22 til 2026-09-18, med 65 handelsdager.
Tallene kan derfor ikke sammenlignes én til én. AKRBP, VAR og ORK har samme
median i begge vinduene. Vinduene overlapper i 57 handelsdager, og for AKRBP og
ORK er medianen omsetningen samme dag i begge. For VAR er det to ulike dager med
samme verdi, avrundet til én desimal. Regnet på samme fil gir vinduet fra §1
919,9 MNOK for EQNR, som i §1.

Alle 15 er over 32 MNOK i dette vinduet. MPCC er lavest, med 33,9 MNOK.

### Alle 40, rangert

De 15 fra §17, de 5 fra §15 og de 20 fra §16, alle i samme vindu. «I OBX» følger
§15 og rettelsen der: av de 15 er alle unntatt DNO og MPCC i OBX, og 25 av de 40
er i OBX.

| # | Symbol | Selskap | Median omsetning (MNOK) | Blant de 15 | I OBX | Fra |
|---|---|---|---:|---|---|---|
| 1 | EQNR | Equinor | 937,9 | Ja | Ja | §17 |
| 2 | DNB | DNB Bank | 391,2 | Ja | Ja | §17 |
| 3 | KOG | Kongsberg Gruppen | 363,6 | Ja | Ja | §17 |
| 4 | AKRBP | Aker BP | 312,1 | Ja | Ja | §17 |
| 5 | FRO | Frontline | 303,2 | Ja | Ja | §17 |
| 6 | NHY | Norsk Hydro | 276,7 | Ja | Ja | §17 |
| 7 | VAR | Vår Energi | 252,9 | Ja | Ja | §17 |
| 8 | TEL | Telenor | 226,2 | Ja | Ja | §17 |
| 9 | YAR | Yara International | 213,1 | Ja | Ja | §17 |
| 10 | MOWI | Mowi | 187,5 | Ja | Ja | §17 |
| 11 | AKER | Aker | 150,5 | Nei | Ja | §15 |
| 12 | ORK | Orkla | 140,3 | Ja | Ja | §17 |
| 13 | NOD | Nordic Semiconductor | 132,5 | Nei | Ja | §16 |
| 14 | VEND | Vend Marketplaces | 108,7 | Nei | Ja | §16 |
| 15 | STB | Storebrand | 87,8 | Nei | Ja | §15 |
| 16 | SUBC | Subsea 7 | 83,7 | Nei | Ja | §15 |
| 17 | SALM | SalMar | 83,3 | Ja | Ja | §17 |
| 18 | BNOR | BlueNord | 78,4 | Nei | Ja | §16 |
| 19 | BWLPG | BW LPG | 70,4 | Nei | Ja | §15 |
| 20 | NAS | Norwegian Air Shuttle | 70,2 | Nei | Ja | §16 |
| 21 | GJF | Gjensidige Forsikring | 60,5 | Ja | Ja | §17 |
| 22 | KMAR | Kongsberg Maritime | 58,3 | Nei | Ja | §15 |
| 23 | HAUTO | Höegh Autoliners | 57,0 | Nei | Ja | §16 |
| 24 | AUTO | AutoStore | 52,1 | Nei | Nei | §16 |
| 25 | TGS | TGS | 49,7 | Nei | Ja | §16 |
| 26 | WAWI | Wallenius Wilhelmsen | 47,6 | Nei | Nei | §16 |
| 27 | CMBTO | CMB.TECH | 47,6 | Nei | Nei | §16 |
| 28 | OET | Okeanis Eco Tankers | 46,1 | Nei | Nei | §16 |
| 29 | TOM | Tomra | 45,7 | Nei | Ja | §16 |
| 30 | DNO | DNO | 40,5 | Ja | Nei | §17 |
| 31 | HAFNI | Hafnia | 35,0 | Nei | Nei | §16 |
| 32 | DOFG | DOF Group | 34,0 | Nei | Nei | §16 |
| 33 | MPCC | MPC Container Ships | 33,9 | Ja | Nei | §17 |
| 34 | SB1NO | SpareBank 1 Sør-Norge | 31,7 | Nei | Nei | §16 |
| 35 | PROT | Protector Forsikring | 30,7 | Nei | Nei | §16 |
| 36 | SBNOR | Sparebanken Norge | 19,1 | Nei | Nei | §16 |
| 37 | MING | SpareBank 1 SMN | 17,8 | Nei | Nei | §16 |
| 38 | VEI | Veidekke | 10,0 | Nei | Nei | §16 |
| 39 | WWI | Wilh. Wilhelmsen Holding | 8,3 | Nei | Nei | §16 |
| 40 | SPOL | SpareBank 1 Østlandet | 5,2 | Nei | Nei | §16 |

De fem sjømatselskapene i §13 (BAKKA, LSG, AUSS, GSF og SALME) er ikke med,
fordi vinduet der er 2026-06-30 til 2026-09-30.

Rangeringen endrer ikke universet. Parametrene i signalet er låst og målt på de
15 (AD-13). Rangeringen er grunnlaget for idéen «De 15 mest omsatte» i raden
«Flere ferdige lister og filter på signalet» i `prd.md` §8.

---

## 18. Søndagsmåling: 20 aksjer til, og alle 60 rangert (2026-10-04)

**Metode.** Som i §15 og §16: ett `/api/eod`-kall per symbol, med
`from=2026-07-02` og `to=2026-10-02`, samme vindu. Omsetning regnes som
`volume × close` per handelsdag, og medianen tas over perioden. Målingen ble
kjørt søndag 04.10, da børsen var stengt og ingen henting trengte kallene, etter
Marians beslutning 02.10 kl. 23:26 (se §16).

De 20 er de neste etter markedsverdi, uten dem som alt er målt. Navnene og
rekkefølgen etter markedsverdi er fra rådets liste 02.10, satt sammen fra
stockanalysis.com. Markedsverdien er bare brukt som en rekkefølge for målingen,
og er ikke et tall appen bruker.

**Kostnad.** 20 kall, tatt av dagskvoten 04.10. Før målingen sto
`apiRequestsDate` på 2026-10-03, altså 0 brukt i dag. Etter første kall sto
`apiRequests` på 1 med datoen 2026-10-04, og `extraLimit` var uendret på 463.
Etter målingen er `apiRequests` 20 og `extraLimit` fortsatt 463. Ingen kall
feilet, ingen symboler var tomme, og ingen dagskall er igjen.

**Rådata.** `data/raa/maaling-raa-2026-10-04.json`. Fila finnes **bare
lokalt** og er ikke sporet i git. Bare tallene under er regnet ut og ført her.

| Symbol | Selskap | Handelsdager | Median omsetning | Over 32 MNOK | Over 25 MNOK |
|---|---|---:|---:|---|---|
| ODL | Odfjell Drilling | 67 | 23,9 MNOK | Nei | Nei |
| CAPT | Capital Tankers | 67 | 28,4 MNOK | Nei | Ja |
| CADLR | Cadeler | 67 | 21,2 MNOK | Nei | Nei |
| SWON | SoftwareOne | 67 | 4,8 MNOK | Nei | Nei |
| AFG | AF Gruppen | 67 | 4,3 MNOK | Nei | Nei |
| KIT | Kitron | 67 | 56,5 MNOK | Ja | Ja |
| AKSO | Aker Solutions | 67 | 14,8 MNOK | Nei | Nei |
| SNI | Stolt-Nielsen | 67 | 8,3 MNOK | Nei | Nei |
| ATEA | Atea | 67 | 9,4 MNOK | Nei | Nei |
| ENTRA | Entra | 67 | 4,8 MNOK | Nei | Nei |
| NONG | SpareBank 1 Nord-Norge | 67 | 9,2 MNOK | Nei | Nei |
| SCATC | Scatec | 67 | 33,2 MNOK | Ja | Ja |
| BWE | BW Energy | 67 | 3,4 MNOK | Nei | Nei |
| BRG | Borregaard | 67 | 8,8 MNOK | Nei | Nei |
| SOMA | Solstad Maritime | 67 | 3,5 MNOK | Nei | Nei |
| EPR | Europris | 67 | 13,4 MNOK | Nei | Nei |
| BORR | Borr Drilling | 67 | 4,8 MNOK | Nei | Nei |
| ELK | Elkem | 67 | 24,5 MNOK | Nei | Nei |
| NORCO | Norconsult | 67 | 7,0 MNOK | Nei | Nei |
| COSH | Constellation Oil Services | 67 | 14,3 MNOK | Nei | Nei |

«Over 32 MNOK» betyr innenfor målingen: de 15 omsettes for 32 til 920 MNOK om
dagen (`prd.md` §3). «Over 25 MNOK» er kriteriet i `prd.md` §3. 2 av de 20 er
over 32 MNOK, og 3 er over 25 MNOK.

Alle 20 har 67 handelsdager, fra 2026-07-02 til 2026-10-02.

Ingen av dem er lagt i universet.

### Alle 60, rangert

De 15 fra §17, de 5 fra §15, de 20 fra §16 og de 20 over, alle i samme vindu.
Tallene for de 40 er regnet på nytt fra de lokale råfilene og er de samme som i
§17. «I OBX» følger §15 og §17: alle 25 i OBX er blant de 40 i §17, så ingen av
de 20 over er i OBX. Der to aksjer har samme avrundede median, står den med
høyest uavrundet median først.

| # | Symbol | Selskap | Median omsetning (MNOK) | Blant de 15 | I OBX | Fra |
|---|---|---|---:|---|---|---|
| 1 | EQNR | Equinor | 937,9 | Ja | Ja | §17 |
| 2 | DNB | DNB Bank | 391,2 | Ja | Ja | §17 |
| 3 | KOG | Kongsberg Gruppen | 363,6 | Ja | Ja | §17 |
| 4 | AKRBP | Aker BP | 312,1 | Ja | Ja | §17 |
| 5 | FRO | Frontline | 303,2 | Ja | Ja | §17 |
| 6 | NHY | Norsk Hydro | 276,7 | Ja | Ja | §17 |
| 7 | VAR | Vår Energi | 252,9 | Ja | Ja | §17 |
| 8 | TEL | Telenor | 226,2 | Ja | Ja | §17 |
| 9 | YAR | Yara International | 213,1 | Ja | Ja | §17 |
| 10 | MOWI | Mowi | 187,5 | Ja | Ja | §17 |
| 11 | AKER | Aker | 150,5 | Nei | Ja | §15 |
| 12 | ORK | Orkla | 140,3 | Ja | Ja | §17 |
| 13 | NOD | Nordic Semiconductor | 132,5 | Nei | Ja | §16 |
| 14 | VEND | Vend Marketplaces | 108,7 | Nei | Ja | §16 |
| 15 | STB | Storebrand | 87,8 | Nei | Ja | §15 |
| 16 | SUBC | Subsea 7 | 83,7 | Nei | Ja | §15 |
| 17 | SALM | SalMar | 83,3 | Ja | Ja | §17 |
| 18 | BNOR | BlueNord | 78,4 | Nei | Ja | §16 |
| 19 | BWLPG | BW LPG | 70,4 | Nei | Ja | §15 |
| 20 | NAS | Norwegian Air Shuttle | 70,2 | Nei | Ja | §16 |
| 21 | GJF | Gjensidige Forsikring | 60,5 | Ja | Ja | §17 |
| 22 | KMAR | Kongsberg Maritime | 58,3 | Nei | Ja | §15 |
| 23 | HAUTO | Höegh Autoliners | 57,0 | Nei | Ja | §16 |
| 24 | KIT | Kitron | 56,5 | Nei | Nei | §18 |
| 25 | AUTO | AutoStore | 52,1 | Nei | Nei | §16 |
| 26 | TGS | TGS | 49,7 | Nei | Ja | §16 |
| 27 | WAWI | Wallenius Wilhelmsen | 47,6 | Nei | Nei | §16 |
| 28 | CMBTO | CMB.TECH | 47,6 | Nei | Nei | §16 |
| 29 | OET | Okeanis Eco Tankers | 46,1 | Nei | Nei | §16 |
| 30 | TOM | Tomra | 45,7 | Nei | Ja | §16 |
| 31 | DNO | DNO | 40,5 | Ja | Nei | §17 |
| 32 | HAFNI | Hafnia | 35,0 | Nei | Nei | §16 |
| 33 | DOFG | DOF Group | 34,0 | Nei | Nei | §16 |
| 34 | MPCC | MPC Container Ships | 33,9 | Ja | Nei | §17 |
| 35 | SCATC | Scatec | 33,2 | Nei | Nei | §18 |
| 36 | SB1NO | SpareBank 1 Sør-Norge | 31,7 | Nei | Nei | §16 |
| 37 | PROT | Protector Forsikring | 30,7 | Nei | Nei | §16 |
| 38 | CAPT | Capital Tankers | 28,4 | Nei | Nei | §18 |
| 39 | ELK | Elkem | 24,5 | Nei | Nei | §18 |
| 40 | ODL | Odfjell Drilling | 23,9 | Nei | Nei | §18 |
| 41 | CADLR | Cadeler | 21,2 | Nei | Nei | §18 |
| 42 | SBNOR | Sparebanken Norge | 19,1 | Nei | Nei | §16 |
| 43 | MING | SpareBank 1 SMN | 17,8 | Nei | Nei | §16 |
| 44 | AKSO | Aker Solutions | 14,8 | Nei | Nei | §18 |
| 45 | COSH | Constellation Oil Services | 14,3 | Nei | Nei | §18 |
| 46 | EPR | Europris | 13,4 | Nei | Nei | §18 |
| 47 | VEI | Veidekke | 10,0 | Nei | Nei | §16 |
| 48 | ATEA | Atea | 9,4 | Nei | Nei | §18 |
| 49 | NONG | SpareBank 1 Nord-Norge | 9,2 | Nei | Nei | §18 |
| 50 | BRG | Borregaard | 8,8 | Nei | Nei | §18 |
| 51 | SNI | Stolt-Nielsen | 8,3 | Nei | Nei | §18 |
| 52 | WWI | Wilh. Wilhelmsen Holding | 8,3 | Nei | Nei | §16 |
| 53 | NORCO | Norconsult | 7,0 | Nei | Nei | §18 |
| 54 | SPOL | SpareBank 1 Østlandet | 5,2 | Nei | Nei | §16 |
| 55 | SWON | SoftwareOne | 4,8 | Nei | Nei | §18 |
| 56 | ENTRA | Entra | 4,8 | Nei | Nei | §18 |
| 57 | BORR | Borr Drilling | 4,8 | Nei | Nei | §18 |
| 58 | AFG | AF Gruppen | 4,3 | Nei | Nei | §18 |
| 59 | SOMA | Solstad Maritime | 3,5 | Nei | Nei | §18 |
| 60 | BWE | BW Energy | 3,4 | Nei | Nei | §18 |

35 av de 60 er over 32 MNOK, og 38 er over 25 MNOK. Av de 20 over er Kitron
høyest, på plass 24.

De fem sjømatselskapene i §13 (BAKKA, LSG, AUSS, GSF og SALME) er fortsatt ikke
med, fordi vinduet der er et annet, 2026-06-30 til 2026-09-30.

Rangeringen endrer ikke universet. Parametrene i signalet er låst og målt på de
15 (AD-13).


---

## 19. Prøve av KI-modeller for teksten (2026-10-04)

**Hva som er prøvd.** Tre modeller har skrevet tekst for fem oppdiktede
aksjedager, med og uten målingene, og for én oppdiktet børsdag med bare antall
og retninger. Tallene i eksemplene er laget for prøven og er ikke hentet fra
EODHD eller fra `data/`. Det ble ikke gjort noen kall til EODHD.

| Modell | Hvor | Versjon | Lisens, sitert fra modellsiden 04.10 |
|---|---|---|---|
| Gemma 4 E4B | Ollama 0.35.1 i Docker (`ollama/ollama`) | `gemma4:e4b`, ID `dc35e8d9c606` | «License: apache-2.0» (https://huggingface.co/google/gemma-4-e4b-it) |
| Qwen 3.5 4B | Ollama 0.35.1 i Docker (`ollama/ollama`) | `qwen3.5:4b`, ID `2a654d98e6fb` | «License: apache-2.0» (https://huggingface.co/Qwen/Qwen3.5-4B) |
| NorMistral-7b-warm-instruct | Ollama 0.35.1 i Docker (`ollama/ollama`) | `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, ID `a9435d7c2cfb` | «License: apache-2.0» (https://huggingface.co/ltg/normistral-7b-warm-instruct), lest 04.10 |
| Gemini 3.5 Flash-Lite | Gemini API, gratisnivået | `gemini-3.5-flash-lite`, `modelVersion` i svaret: `gemini-3.5-flash-lite` | Vilkårene er ført i dagsfila 04.10 kl. 11:00 |

For Qwen ble lisensen først lest på kortet for Qwen3.5-9B, i samme familie, før nedlastingen. Kortet for Qwen3.5-4B ble lest etterpå, og det sier det samme.

**Innstillinger.** Temperatur 0 og seed 42 for alle. For Gemma og Qwen var
tenkingen slått av (`think: false`). For Gemini sto tenkingen på standard, som
er «minimal» for Flash-Lite ifølge Googles side om thinking.

**Kjøringene.** Ollama kjørte i en container med modellene i det navngitte
volumet `ose-ki-ollama`. Det ble ikke installert noe på Windows. PC-en har
15,7 GB minne, i7-13700HX og RTX 4070 Laptop med 8 188 MiB. Docker Desktop hadde
8,2 GB minne. `ollama ps` viste «100% GPU» for kjøringene med grafikkort og
«100% CPU» for kjøringen uten.

- **Qwen uten grafikkort ble hoppet over.** Windows hadde 1,7 GB ledig minne
  før kjøringen, og 1,8 GB etter at Docker Desktop var startet på nytt. Grensen
  var 2 GB.
- **Gemma med grafikkort ble kjørt** etter at Docker Desktop var startet på nytt
  en gang til. Da var 3,3 GB ledig.
- **Gemma uten grafikkort ble kjørt** med 2,1 GB ledig.
- **Gemini: 11 kall.** Det kom ingen nye kall etter de 11.
- **NorMistral med grafikkort ble kjørt** med 3,8 GB ledig, og **uten grafikkort** med 2,3 GB ledig. *Lagt til kl. 18:02.*

**NorMistral-7b-warm-instruct ble ikke prøvd.** Nedlastingen ble stoppet da
PC-en hadde for lite minne, og instruksjonen kl. 16:52 valgte å gå videre uten
den. Etter instruksjonen kl. 16:52 viste det seg at nedlastingen hadde fullført i
containeren. Sjekksummen stemte med manifestet. Modellen ligger i volumet,
men er ikke kjørt.

*Lagt til 2026-10-04 kl. 18:02:* NorMistral er prøvd etter instruksjonen kl. 17:56, med og uten grafikkort, i samme oppsett og med samme eksempler, prompt og innstillinger. `ollama ps` viste kontekst 2048 og «100% GPU» og «100% CPU».

**Tiden** er målt fra kallet ble sendt til svaret kom, per tekst. Den første
teksten i hver lokal kjøring tar med innlastingen av modellen. For Gemini er
tiden med nettverket.

### Tid og kontroll per kjøring

| Modell | Kjøring | Tekster | Besto FR-603 | Median tid per tekst | Lengste | Første (med innlasting) |
|---|---|---:|---:|---:|---:|---:|
| `gemini-3.5-flash-lite` | sky | 11 | 10 | 4,2 s | 7,6 s | 5,1 s |
| `qwen3.5:4b` | gpu | 11 | 9 | 1,4 s | 61,4 s | 61,4 s |
| `gemma4:e4b` | gpu | 11 | 9 | 0,9 s | 79,9 s | 79,9 s |
| `gemma4:e4b` | cpu | 11 | 9 | 7,7 s | 32,7 s | 32,7 s |
| `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M` | gpu | 11 | 2 | 2,9 s | 42,6 s | 42,6 s |
| `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M` | cpu | 11 | 3 | 14,5 s | 35,8 s | 27,1 s |

Med samme seed og temperatur ga Gemma ulik tekst med og uten grafikkort i 7 av
11 tilfeller. Lik tekst kom for A-uten, B-uten, E-med og Dag. Om samme kjøring
gir samme tekst to ganger på samme maskin, er ikke prøvd.

### Prompten, ordrett

For aksjedetaljen, der `{grunnlag}` byttes ut med grunnlaget:

```text
Du skriver en kort forklaring på norsk (bokmål) av et regelbasert signal for én aksje på Oslo Børs. Skriv to eller tre hele setninger. Bruk bare det som står i grunnlaget under. Ikke gi råd om å kjøpe, selge eller holde. Ikke gjett på årsaker, og ikke si noe om hva som vil skje videre. Ikke nevn tall som ikke står i grunnlaget.

Slik leses grunnlaget:
- Trend: kursen sammenlignet med snittet de siste 50 dagene (MA50).
- Bevegelse: dagens endring sammenlignet med det vanlige daglige utslaget de siste 20 dagene.
- Interesse: dagens volum sammenlignet med medianvolumet de 20 dagene før.
- Hver sjekk har fortegn +1 (utslag opp), -1 (utslag ned) eller 0 (ingen utslag).
- Styrke er hvor mange av de tre sjekkene som ga utslag (0 til 3).
- Retning er Positiv, Negativ, Blandet eller Ingen.

Grunnlag:
{grunnlag}
```

For dagsteksten:

```text
Du skriver en kort tekst på norsk (bokmål) om hele børsdagen for de 15 aksjene i en oversikt over Oslo Børs. Skriv to eller tre hele setninger. Bruk bare det som står i grunnlaget under. Ikke gi råd om å kjøpe, selge eller holde. Ikke gjett på årsaker, og ikke si noe om hva som vil skje videre. Ikke nevn tall som ikke står i grunnlaget.

Grunnlag:
{grunnlag}
```

### Eksemplene

Uten målingene er grunnlaget det samme, uten parentesene. Eksempel A uten
målingene:

```text
Aksje: Eksempel A
Trend: +1
Bevegelse: +1
Interesse: +1
Styrke: 3
Retning: Positiv
```

Eksempel A, med målingene:

```text
Aksje: Eksempel A
Trend: +1 (+3,4 % mot MA50)
Bevegelse: +1 (+2,8 % mot 1,6 % standardavvik)
Interesse: +1 (volum 2,10 × medianen)
Styrke: 3
Retning: Positiv
```

Eksempel B, med målingene:

```text
Aksje: Eksempel B
Trend: -1 (-4,1 % mot MA50)
Bevegelse: -1 (-3,0 % mot 1,9 % standardavvik)
Interesse: 0 (volum 1,12 × medianen)
Styrke: 2
Retning: Negativ
```

Eksempel C, med målingene:

```text
Aksje: Eksempel C
Trend: +1 (+2,6 % mot MA50)
Bevegelse: -1 (-2,2 % mot 1,4 % standardavvik)
Interesse: -1 (volum 1,80 × medianen)
Styrke: 3
Retning: Blandet
```

Eksempel D, med målingene:

```text
Aksje: Eksempel D
Trend: 0 (+0,8 % mot MA50)
Bevegelse: 0 (+0,5 % mot 1,3 % standardavvik)
Interesse: 0 (volum 0,95 × medianen)
Styrke: 0
Retning: Ingen
```

Eksempel E, med målingene:

```text
Aksje: Eksempel E
Trend: -1 (-2,9 % mot MA50)
Bevegelse: 0 (-0,7 % mot 1,5 % standardavvik)
Interesse: 0 (volum 1,20 × medianen)
Styrke: 1
Retning: Negativ
```

Dagen:

```text
Antall aksjer: 15
Skilte seg ut (styrke 2 eller mer): 3
Retning Positiv: 5
Retning Negativ: 4
Retning Blandet: 2
Retning Ingen: 4
Gikk bedre enn hovedindeksen: 6
Hovedindeksen: ned
Energi: 3 av 4 opp
Sjømat: 1 av 3 opp
Finans: 2 av 4 opp
Industri: 1 av 4 opp
```

### Kontrollen mot FR-603

Kontrollen er et lite skript utenfor repoet, med ordlister for de fire
punktene: retning og styrke, tallene, råd og gjetning eller årsak. Den er grov.
Punkt 2 kjenner bare tall skrevet med sifre. Underveis fikk den en sjekk av
fortegn: et negativt tall i grunnlaget kan stå uten minus bare når teksten sier
at det gikk ned. Sjekken kom etter at Gemini-teksten B-med ble lest. Alle
tekstene i tabellen er sjekket med den endelige versjonen.

**Tekster kontrollen stoppet:**

- `gemini-3.5-flash-lite`, sky, B-med: 2: 4,1 står uten minus, grunnlaget har -4,1
- `qwen3.5:4b`, gpu, C-uten: 4: «på grunn av»
- `qwen3.5:4b`, gpu, D-med: 4: «fordi»
- `gemma4:e4b`, gpu, D-uten: 4: «skyldes»
- `gemma4:e4b`, gpu, D-med: 4: «skyldes»
- `gemma4:e4b`, cpu, D-uten: 4: «skyldes»
- `gemma4:e4b`, cpu, D-med: 4: «skyldes»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, gpu, A-uten: 4: «resultat»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, gpu, A-med: 3: «investeringsalternativ»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, gpu, B-uten: 4: «resultat»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, gpu, C-uten: 4: «sannsynlig»; 4: «sannsynlig»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, gpu, C-med: 4: «resultatet»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, gpu, D-uten: 3: «investeringsråd»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, gpu, D-med: 3: «kjøps»; 3: «salgs»; 4: «resultatene»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, gpu, E-uten: 4: «resultater»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, gpu, E-med: 1: «ingen av de tre sjekk», styrken er 1; 4: «resultat»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, cpu, A-uten: 3: «investeringsmulighet»; 4: «resultater»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, cpu, A-med: 4: «sannsynligvis»; 4: «vil fortsette»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, cpu, C-uten: 3: «kjøpe»; 3: «anbefales»; 3: «investeringsbeslutninger»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, cpu, C-med: 4: «kanskje»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, cpu, D-med: 4: «forventede»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, cpu, E-uten: 3: «bør»; 3: «investeringsbeslutninger»; 4: «sannsynlig»; 4: «vil fortsette»; 4: «resultater»; 4: «resultater»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, cpu, E-med: 4: «resultat»
- `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, cpu, Dag: 4: «resultater»; 4: «resultater»

**Lest manuelt etterpå.** Ordene «fordi», «skyldes» og «på grunn av» viser i
alle seks tilfellene til regelen selv, for eksempel at retningen er Ingen fordi
ingen sjekk ga utslag. De nevner ingen årsak utenfor grunnlaget.

Kontrollen slapp gjennom disse feilene, fordi de er skrevet med ord og ikke med
sifre:

- `qwen3.5:4b` A-uten sier «den femdagssnittet». Grunnlaget har snittet over 50 dager.
- `qwen3.5:4b` Dag sier «seks av de femti aksjene». Grunnlaget har 15 aksjer.
- `qwen3.5:4b` Dag sier at det i de fire sektorene var flere aksjer som gikk opp
  enn ned. Grunnlaget har 7 av 15 opp.
- `gemma4:e4b` uten grafikkort skriver i C-med «interessen er negativ
  sammenlignet med medianvolumet». Det kan leses som at volumet var lavt, men
  grunnlaget har 1,80 × medianen. Fortegnet for interessen følger dagens
  kursendring, og det står ikke i prompten. Kontrollen fanger ikke en slik feil.

*Lagt til kl. 18:02:* NorMistral-tekstene som besto kontrollen, har også feil kontrollen ikke ser:

- Med grafikkort, B-med: «Interessenivået … var også negativt», og «to positive
  signaler og ett negativt signal». Grunnlaget har interesse 0 og to negative.
- Med grafikkort, Dag: «Disse aksjene var positive» om de tre som skilte seg
  ut. Det står ikke i grunnlaget. Hver retning forklares som at aksjene
  «presterte bedre enn markedet» eller «omtrent som markedet».
- Uten grafikkort, B-uten: «Interesseindikatoren viser også en negativ verdi».
  Grunnlaget har 0.
- Uten grafikkort, B-med: «to av tre signaler (trend og interesse) har vært
  negative». Grunnlaget har trend og bevegelse.
- Uten grafikkort, D-uten: «dagens handelsvolum under gjennomsnittet». Grunnlaget
  uten målinger sier ikke noe om volumet.

Ordet «resultat» stoppet seks NorMistral-tekster alene. Der viser det til
sjekkene eller til kursen, som i «ga et positivt resultat», og ikke til
selskapenes regnskap. To av de seks har likevel råd eller spådom med ord som
ikke står i listene:

- Med grafikkort, A-uten: «kan være et godt alternativ for investorer å vurdere».
- Med grafikkort, E-uten: «kan antyde at prisen på aksjen kan stabilisere seg
  eller til og med øke i nær fremtid».

### Tekstene, ordrett

#### `gemini-3.5-flash-lite`, sky

- **A-uten** (5,1 s): Aksje Eksempel A har en positiv retning med en styrke på 3, ettersom alle de tre sjekkene for trend, bevegelse og interesse ga utslag på +1. Kursen er høyere enn snittet de siste 50 dagene, dagens endring er større enn det vanlige utslaget de siste 20 dagene, og dagens volum er høyere enn medianvolumet de 20 dagene før.
- **A-med** (5,6 s): For aksjen Eksempel A viser trenden og bevegelsen utslag opp med henholdsvis +3,4 % mot MA50 og +2,8 % mot standardavviket. Dagens volum er 2,10 ganger medianen, noe som gir et utslag opp på interesse. Samlet gir dette en styrke på 3 og en positiv retning.
- **B-uten** (0,8 s): Aksje Eksempel B har en negativ retning med en styrke på 2. Trenden og bevegelsen gir utslag ned, mens interessen viser ingen utslag.
- **B-med** (6,9 s): For Eksempel B er trenden -1 med en kurs som ligger 4,1 % mot MA50, og bevegelsen er -1 med et utslag på -3,0 % mot 1,9 % standardavvik. Interessen er 0 med et volum på 1,12 ganger medianen, noe som gir en styrke på 2 og en negativ retning.
- **C-uten** (6,4 s): For aksjen Eksempel C viser trenden et utslag opp, mens både bevegelse og interesse viser utslag ned. Styrken er tre, og retningen er blandet.
- **C-med** (4,2 s): For aksjen Eksempel C viser trenden +1 med en kurs som er 2,6 prosent mot MA50, mens bevegelsen er -1 på -2,2 prosent mot 1,4 prosent standardavvik. Interessen er -1 med et volum på 1,80 ganger medianen, noe som gir en styrke på 3 og en blandet retning.
- **D-uten** (0,9 s): Aksje Eksempel D har en styrke på 0 og en retning som er satt til Ingen. Sjekkene for både trend, bevegelse og interesse viser ingen utslag med verdien 0.
- **D-med** (0,8 s): For aksjen Eksempel D viser sjekkene en styrke på 0, ettersom ingen av de tre sjekkene ga utslag. Dette gir en retning som er definert som Ingen.
- **E-uten** (0,9 s): For aksjen Eksempel E viser trenden et negativt utslag på -1, mens bevegelse og interesse ikke gir noen utslag. Den totale styrken er 1, og samlet retning er definert som negativ.
- **E-med** (7,6 s): For aksjen Eksempel E viser trenden et negativt utslag på minus 2,9 prosent mot MA50, mens bevegelse og interesse ikke gir noen utslag. Dette gir en samlet styrke på én og en negativ retning.
- **Dag** (1,0 s): Oslo Børs endte ned for hovedindeksen, og av de 15 aksjene i oversikten hadde 5 en positiv retning, 4 en negativ retning, 2 en blandet retning og 4 ingen retning. Tre aksjer skilte seg ut med en styrke på 2 eller mer, og 6 aksjer gikk bedre enn hovedindeksen. Innen sektorene gikk 3 av 4 opp i energi, 1 av 3 opp i sjømat, 2 av 4 opp i finans og 1 av 4 opp i industri.

#### `qwen3.5:4b`, gpu

- **A-uten** (61,4 s): For aksjen Eksempel A indikerer regelbaserte sjekker at kursen ligger over den femdagssnittet, har en positiv endring i forhold til det vanlige daglige utslaget og et volum som overstiger medianvolumet. Alle tre faktorer gir et positivt utslag, noe som resulterer i en styrke på 3 og en total retning klassifisert som Positiv.
- **A-med** (1,7 s): Signalet for aksjen er basert på at kursen ligger over snittet de siste 50 dagene, at dagens endring overstiger det vanlige daglige utslaget og at dagens volum er høyere enn medianvolumet de siste 20 dagene. Alle tre sjekker gir et positivt utslag, noe som resulterer i en styrke på 3 og en retning klassifisert som Positiv.
- **B-uten** (1,0 s): For aksjen Eksempel B indikerer analysen en negativ retning basert på at både trend og bevegelse viser nedadgående utslag. Dette gir en styrke på to, mens interesse sjekken ikke ga et klart utslag.
- **B-med** (1,1 s): Signalet for aksjen Eksempel B er basert på en negativ trend og en nedadbevegelse, mens volumet ligger i snitt. Dette gir et totalt styrkeverdi på to utslag, noe som resulterer i en negativ retning.
- **C-uten** (1,1 s): For aksjen Eksempel C er trenden positiv, mens bevegelsen og interessen begge viser nedadgående utslag. Dette gir en styrke på tre, men retningen blir klassifisert som blandet på grunn av motsetningene mellom de ulike faktorene.
- **C-med** (1,4 s): Signalet for aksjen Eksempel C er basert på en analyse av trend, bevegelse og interesse i forhold til henholdsvis 50-dagers snitt, standardavvik og medianvolum. Alle tre sjekker ga utslag, noe som resulterte i en styrke på 3 og en retning klassifisert som blandet.
- **D-uten** (0,8 s): For aksjen Eksempel D er trend, bevegelse og interesse alle null, noe som gir en styrke på null. Dette resulterer i at retningen blir klassifisert som «Ingen».
- **D-med** (1,5 s): For aksjen Eksempel D er trenden, bevegelsen og interessen alle null fordi dagens utvikling ikke avviker markant fra snittet, det vanlige utslaget eller medianvolumet. Det betyr at ingen av de tre sjekkene ga et utslag, noe som resulterte i en styrke på null og en retning klassifisert som «Ingen».
- **E-uten** (1,0 s): For aksjen Eksempel E er trenden negativ siden kursen ligger under snittet på 50 dager, mens bevegelsen og interessen ikke viste utslag. Dette gir en styrke på én og en generell retning som er negativ.
- **E-med** (1,4 s): Signalet for aksjen Eksempel E er basert på en trend som ligger under snittet de siste 50 dagene, noe som gir et negativt utslag. Bevegelsen og interessen viser ingen utslag, slik at styrken blir én av tre sjekker. Dette resulterer i en total retning som er negativ.
- **Dag** (1,9 s): I dagens børsdag på Oslo Børs var hovedindeksen ned, og seks av de femti aksjene i oversikten gikk bedre enn denne. Av de 15 aksjene som ble presentert, skilte tre ut med en styrke på to eller mer, mens retningen varierte fra positiv til negativ blandet med ingen endring. I sektorene energi, sjømat, finans og industri var det flere aksjer som opp enn som gikk ned.

#### `gemma4:e4b`, gpu

- **A-uten** (79,9 s): For aksjen Eksempel A er trenden positiv, da kursen er sammenlignet med snittet de siste 50 dagene. Bevegelsen er også positiv, basert på dagens endring sammenlignet med det vanlige daglige utslaget de siste 20 dagene. Samlet sett har aksjen en styrke på 3, noe som gir en positiv retning.
- **A-med** (0,9 s): For aksjen Eksempel A er trenden positiv, da kursen er opp mot MA50. Bevegelsen er også positiv, og volumet er høyere enn medianvolumet de siste 20 dagene. Dette resulterer i en styrke på 3 og en retning som er Positiv.
- **B-uten** (0,9 s): For aksjen Eksempel B er trenden negativ, da kursen sammenlignes med snittet de siste 50 dagene. Bevegelsen er også negativ, basert på dagens endring sammenlignet med det vanlige daglige utslaget de siste 20 dagene. Samlet sett har aksjen en styrke på 2, noe som gir en negativ retning.
- **B-med** (0,9 s): For aksjen Eksempel B er trenden negativ, da kursen er -4,1 % mot MA50. Bevegelsen er også negativ, med en endring på -3,0 % mot det vanlige daglige utslaget. Samlet gir dette en negativ retning med en styrke på 2.
- **C-uten** (0,6 s): For aksjen Eksempel C er trenden positiv, mens bevegelsen og interessen er negative. Styrken til signalet er 3, og retningen er Blandet.
- **C-med** (0,9 s): For aksjen Eksempel C er trenden positiv, da kursen er opp 2,6 % mot MA50. Bevegelsen er negativ, og volumet er høyere enn medianvolumet de 20 dagene før. Dette resulterer i en styrke på 3 og en retning som er Blandet.
- **D-uten** (0,7 s): For aksjen Eksempel D er styrken på signalet 0. Retningen på signalet er Ingen. Dette skyldes at Trend, Bevegelse og Interesse alle ga utslag på 0.
- **D-med** (1,1 s): For aksjen Eksempel D er styrken 0, da ingen av de tre sjekkene ga utslag. Retningen er Ingen. Dette skyldes at kursen sammenlignet med snittet de siste 50 dagene, dagens endring sammenlignet med det vanlige daglige utslaget de siste 20 dagene, og dagens volum sammenlignet med medianvolumet de 20 dagene før, alle ga utslag på 0.
- **E-uten** (0,8 s): For aksjen Eksempel E er trenden negativ basert på sammenligningen med snittet de siste 50 dagene. Bevegelsen og interessen gir ingen utslag. Styrken på signalet er 1, og retningen er Negativ.
- **E-med** (0,9 s): For aksjen Eksempel E er trenden negativ, da kursen er -2,9 % mot MA50. Bevegelsen er nøytral, og interessen er nøytral. Styrken til signalet er 1, og retningen er Negativ.
- **Dag** (0,9 s): På børsdagen var det totalt 15 aksjer i oversikten. Tre aksjer skilte seg ut med styrke to eller mer, mens fem aksjer hadde en positiv retning. Hovedindeksen gikk ned, men seks aksjer gikk bedre enn hovedindeksen.

#### `gemma4:e4b`, cpu

- **A-uten** (32,7 s): For aksjen Eksempel A er trenden positiv, da kursen er sammenlignet med snittet de siste 50 dagene. Bevegelsen er også positiv, basert på dagens endring sammenlignet med det vanlige daglige utslaget de siste 20 dagene. Samlet sett har aksjen en styrke på 3, noe som gir en positiv retning.
- **A-med** (7,4 s): For aksjen Eksempel A er trenden positiv, da kursen er opp mot MA50. Bevegelsen er også positiv, og interessen er positiv da volumet er høyere enn medianvolumet. Dette resulterer i en styrke på 3 og en retning som er Positiv.
- **B-uten** (7,1 s): For aksjen Eksempel B er trenden negativ, da kursen sammenlignes med snittet de siste 50 dagene. Bevegelsen er også negativ, basert på dagens endring sammenlignet med det vanlige daglige utslaget de siste 20 dagene. Samlet sett har aksjen en styrke på 2, noe som gir en negativ retning.
- **B-med** (8,6 s): For aksjen Eksempel B er trenden negativ, da kursen er -4,1 % mot MA50. Bevegelsen er også negativ, med en endring på -3,0 % mot det vanlige daglige utslaget. Samlet sett har aksjen en styrke på 2, noe som gir en negativ retning.
- **C-uten** (6,6 s): For aksjen Eksempel C er trenden +1, bevegelsen er -1 og interessen er -1. Styrken er 3, og retningen er Blandet.
- **C-med** (7,9 s): For aksjen Eksempel C er trenden positiv, da kursen er opp mot MA50. Bevegelsen er negativ, og interessen er negativ sammenlignet med medianvolumet de 20 dagene før. Styrken er 3, og retningen er Blandet.
- **D-uten** (7,7 s): For aksjen Eksempel D er styrken på signalet 0. Retningen på signalet er Ingen. Dette skyldes at Trend, Bevegelse og Interesse alle ga et utslag på 0.
- **D-med** (8,5 s): For aksjen Eksempel D er styrken 0, da ingen av de tre sjekkene ga utslag. Retningen er Ingen. Dette skyldes at trenden, bevegelsen og interessen alle ga et utslag på 0.
- **E-uten** (7,2 s): For aksjen Eksempel E er trenden negativ basert på kursen sammenlignet med snittet de siste 50 dagene. Bevegelsen og interessen gir ingen utslag. Styrken på signalet er 1, og retningen er Negativ.
- **E-med** (8,2 s): For aksjen Eksempel E er trenden negativ, da kursen er -2,9 % mot MA50. Bevegelsen er nøytral, og interessen er nøytral. Styrken til signalet er 1, og retningen er Negativ.
- **Dag** (7,6 s): På børsdagen var det totalt 15 aksjer i oversikten. Tre aksjer skilte seg ut med styrke to eller mer, mens fem aksjer hadde en positiv retning. Hovedindeksen gikk ned, men seks aksjer gikk bedre enn hovedindeksen.

NorMistral skrev flere avsnitt i noen tekster. Avsnittsskiftene er slått sammen til mellomrom her, og ordene står som modellen skrev dem.

#### `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, gpu

- **A-uten** (42,6 s): Aksjeeksempel A viser en positiv trend, noe som indikerer at aksjekursen har vært konsekvent økende over en lengre periode. I tillegg viser den et positivt momentum, noe som indikerer at dagens endring i aksjekursen er større enn det vanlige daglige utslaget som har forekommet i løpet av de siste 20 dagene. Videre viser den et positivt interessevolum, noe som indikerer at dagens handelsvolum er høyere enn det vanlige daglige volumet som har forekommet i løpet av de siste 20 dagene. Til slutt viser den en styrke på 3, noe som indikerer at alle tre av de tre sjekkene som er nevnt i grunnlaget, ga et positivt resultat. Derfor er aksjeeksempel A for øyeblikket i en positiv retning og kan være et godt alternativ for investorer å vurdere.
- **A-med** (2,3 s): Aksjeeksempel A viser en positiv trend, noe som indikerer at kursen har vært konsekvent økende sammenlignet med gjennomsnittet de siste 50 dagene. I tillegg viser aksjen en positiv bevegelse, noe som betyr at dagens endring i pris var større enn det vanlige daglige utslaget de siste 20 dagene. Til slutt viser aksjen en sterk interesse, med dagens volum som er mer enn dobbelt så mye som medianvolumet de siste 20 dagene. Alle disse faktorene bidrar til en samlet positiv vurdering av aksjen, noe som gjør den til et lovende investeringsalternativ.
- **B-uten** (2,3 s): Aksjen med tickersymbol Eksempel B har for tiden en negativ trend, noe som betyr at den har prestert dårligere enn gjennomsnittet de siste 50 dagene. I tillegg har den opplevd et negativt avvik i dag sammenlignet med det vanlige daglige avviket de siste 20 dagene. Interessen for denne aksjen er også lavere enn gjennomsnittet, som indikert av dagens volum. Denne kombinasjonen av faktorer har ført til at styrken til denne signalsjekken er vurdert til 2 av 3, noe som indikerer et sterkt negativt sentiment. Som et resultat er retningen på dette signalet negativt.
- **B-med** (2,7 s): Aksjeeksempel B viser en negativ trend, med en nedgang på -4,1 % sammenlignet med glidende gjennomsnitt (MA50). Dagens endring i aksjeprisen var også negativ, med en nedgang på -3,0 % sammenlignet med det vanlige daglige utslaget de siste 20 dagene. Interessenivået, som måler dagens volum sammenlignet med medianvolumet de siste 20 dagene, var også negativt, med et volum på 1,12 ganger medianen. Aksjen hadde to positive signaler og ett negativt signal, noe som gir en styrke på 2. Basert på disse signalene er retningen på aksjens bevegelse negativ.
- **C-uten** (5,4 s): Aksjeeksempel C viser et regelbasert signal basert på tre nøkkelindikatorer: trenden, bevegelsen og interessen. Testen av trenden er positiv, noe som indikerer at aksjekursen har vært konsekvent økende sammenlignet med sitt 50-dagers glidende gjennomsnitt (MA50). Bevegelsestesten viser en negativ verdi, noe som indikerer at dagens endring i aksjekursen har vært mindre enn det typiske daglige utslaget som er observert i løpet av de siste 20 dagene. Til slutt viser interesse testen en negativ verdi, noe som indikerer at dagens handelsvolum er lavere enn medianverdien som er observert i løpet av de siste 20 dagene.  I tillegg til disse testene evaluerer signalet også styrken til signalet ved å telle antall positive, negative og nøytrale tester. I dette tilfellet er det tre positive tester av tre mulige, noe som resulterer i en styrkeverdi på 3. Styrkeverdien indikerer den generelle helsen til signalet og dets evne til å nøyaktig identifisere potensielle prisbevegelser.  Til slutt indikerer retningen på signalet Blandet, noe som indikerer at det er like sannsynlig at aksjekursen vil øke som å falle basert på de nåværende markedsforholdene. Samlet sett indikerer det regelbaserte signalet for aksjeeksempel C en positiv trend og er sannsynlig å generere sterke signaler i de kommende dagene.
- **C-med** (4,4 s): Aksjeeksempel C viser en blandet trend basert på de tre sjekkene som er nevnt i grunnlaget. Trendsjekken sammenligner aksjens kurs med gjennomsnittet de siste 50 dagene (MA50), og den gir en +1-score (+2,6 % mot MA50). Bevegelsessjekken måler dagens endring mot det vanlige daglige utslaget de siste 20 dagene. I dette tilfellet resulterer det i en -1-score (-2,2 % mot 1,4 % standardavvik). Interessesjekken vurderer dagens volum mot medianvolumet de siste 20 dagene. Resultatet er en -1-score (volum 1,80 ganger medianen). Styrkesjekken evaluerer antall positive, negative og nøytrale trender blant de tre sjekkene. I dette tilfellet er det 3 positive trender, noe som resulterer i en +1-score. Til slutt indikerer retningssjekken at trenden er blandet, noe som resulterer i en -1-score.
- **D-uten** (2,0 s): Aksjeeksempel D viser for øyeblikket ingen trend. Aksjen har beveget seg innenfor sitt vanlige daglige område de siste 20 dagene, men det er ingen signifikant endring i dag sammenlignet med dette gjennomsnittet. Interessen for aksjen er også lav, med dagens handelsvolum under gjennomsnittet. Basert på disse faktorene har aksjen ingen trend og anses for øyeblikket for å være sidelengs. Denne informasjonen er basert på de gitte grunnlagene og gir ikke investeringsråd.
- **D-med** (4,5 s): Aksjen som heter Eksempel D på Oslo Børs viser en trend på 0% sammenlignet med sitt 50-dagers glidende gjennomsnitt (MA50). Dagens endring i prisvolatilitet er også 0%, noe som er innenfor det vanlige 1,3% standardavviket. Interessenivået, som er beregnet ved å sammenligne dagens volum med medianvolumet de siste 20 dagene, er også 0%, noe som indikerer at volumet er innenfor det vanlige området.  Styrken til denne trenden er 0 av 3 sjekker, noe som indikerer at ingen av de tre komponentene i trenden - prisendring, volumendring eller pris-volum-korrelasjon - har vært sterke nok til å produsere en betydelig trend.  Basert på disse resultatene er retningen på trenden ingen. Dette betyr at det ikke er noe tydelig bevis for at prisen på aksjen vil øke eller redusere i nær fremtid. Det er viktig å merke seg at denne informasjonen ikke er en kjøps-, salgs- eller holdanbefaling. I stedet gir den en kortfattet oppsummering av den nåværende tilstanden til trenden for denne aksjen.
- **E-uten** (2,9 s): Aksjen med tickersymbol Eksempel E er for tiden i en negativ trend, som indikert av verdien -1 i grunnlaget. Dette betyr at prisen på aksjen har vært synkende sammenlignet med gjennomsnittet de siste 50 dagene. I tillegg er det ingen interesse for aksjen, som indikert av verdien 0 i grunnlaget. Imidlertid er det ett positivt aspekt ved denne aksjen, og det er at volumet er høyere enn gjennomsnittet for de siste 20 dagene. Denne kombinasjonen av negative trender og positive aspekter kan antyde at prisen på aksjen kan stabilisere seg eller til og med øke i nær fremtid. Det er imidlertid viktig å merke seg at dette bare er en regelbasert signal, og faktiske resultater kan variere.
- **E-med** (2,4 s): Aksjeeksempel E viser en negativ trend, noe som indikerer at kursen har vært konsekvent synkende sammenlignet med gjennomsnittet de siste 50 dagene. Denne trenden forsterkes ytterligere av en negativ bevegelse, som indikerer at dagens endring i pris var større enn det vanlige daglige utslaget de siste 20 dagene. I tillegg var dagens volum under gjennomsnittet, noe som ytterligere støtter den negative retningen. Imidlertid er det ingen styrke i dette tilfellet, noe som betyr at ingen av de tre sjekkene - trend, bevegelse og interesse - ga et positivt eller negativt resultat. Derfor er retningen for denne aksjen negativ.
- **Dag** (5,3 s): Basert på informasjonen som er oppgitt, var det 15 aksjer som ble handlet på Oslo Børs i løpet av handelsdagen. Av disse skilte tre aksjer seg ut med en styrke på 2 eller mer. Disse aksjene var positive, noe som indikerer at de presterte bedre enn markedet. Fem aksjer skilte seg ut i en positiv retning, noe som indikerer at de presterte bedre enn markedet. Fire aksjer skilte seg ut i en negativ retning, noe som indikerer at de presterte dårligere enn markedet. To aksjer skilte seg ut som blandet, noe som indikerer at de presterte omtrent som markedet. Fire aksjer skilte seg ikke ut i noen retning, noe som indikerer at de presterte omtrent som markedet.  I tillegg var seks av aksjene bedre enn hovedindeksen, noe som indikerer at de presterte bedre enn markedet. Hovedindeksen gikk ned i løpet av handelsdagen. Energi-, sjømat-, finans- og industrisektorene hadde også aksjer som presterte bedre enn markedet. Energi-sektoren hadde tre av sine fire aksjer som presterte bedre enn markedet, mens sjømatsektoren hadde én av sine tre aksjer som presterte bedre enn markedet. Finanssektoren hadde to av sine fire aksjer som presterte bedre enn markedet, og industrisektoren hadde én av sine fire aksjer som presterte bedre enn markedet.

#### `hf.co/ltg/normistral-7b-warm-instruct:Q4_K_M`, cpu

- **A-uten** (27,1 s): Aksjeeksempel A viser en positiv trend, noe som indikerer at aksjekursen har vært konsekvent økende over en lengre periode. I tillegg viser den et positivt momentum, noe som indikerer at dagens økning i aksjekursen er større enn det typiske daglige utslaget som har skjedd i løpet av de siste 20 dagene. Videre viser den et positivt interessevolum, noe som indikerer at dagens handelsvolum er høyere enn det typiske daglige volumet som har skjedd i løpet av de siste 20 dagene. Til slutt viser den en styrke på 3, noe som indikerer at alle tre komponentene i signalet - trend, momentum og interesse - har vist positive resultater. Derfor er aksjeeksempel A for øyeblikket i en positiv retning og kan være en lovende investeringsmulighet.
- **A-med** (15,3 s): Aksjeeksempel A viser en positiv trend, noe som indikerer at aksjekursen har økt sammenlignet med gjennomsnittet de siste 50 dagene. I tillegg viser aksjen en positiv bevegelse, noe som betyr at dagens endring i pris er større enn det vanlige daglige utslaget som er observert de siste 20 dagene. Aksjen viser også en positiv interesse, med dagens volum som er større enn medianvolumet de siste 20 dagene.  Styrken til denne signalet beregnes ved å telle antall positive, negative og blandede signaler blant de tre tilgjengelige. I dette tilfellet er det tre positive signaler, noe som resulterer i en styrke på 3.  Til slutt indikerer retningen på signalet den generelle trenden i aksjekursen. I dette tilfellet er retningen positiv, noe som indikerer at aksjekursen sannsynligvis vil fortsette å øke.
- **B-uten** (14,5 s): Aksjeeksempel B viser en negativ trend, noe som indikerer at aksjekursen har vært konsekvent synkende sammenlignet med gjennomsnittet de siste 50 dagene. I tillegg viser den en negativ bevegelse, noe som indikerer at dagens endring i aksjekursen har vært større enn det vanlige daglige utslaget, som har vært synkende de siste 20 dagene. Interesseindikatoren viser også en negativ verdi, noe som indikerer at dagens handelsvolum har vært lavere enn medianverdien de siste 20 dagene. Til slutt viser styrken til signalet en verdi på 2, noe som indikerer at to av de tre sjekkene som ble utført, ga en negativ verdi, noe som ytterligere støtter den negative retningen til signalet. Derfor er retningen til signalet for aksjeeksempel B negativ.
- **B-med** (13,4 s): Aksjeeksempel B viser en negativ trend, med en nedgang på -4,1 % sammenlignet med glidende gjennomsnitt (MA50). Dagens endring i kursen er også negativ, med en nedgang på -3,0 % sammenlignet med det vanlige daglige utslaget de siste 20 dagene. Interessenivået, som måler dagens volum sammenlignet med medianvolumet de siste 20 dagene, er negativt, med et volum på 1,12 ganger medianen. Denne aksjen har vist styrke ved at to av tre signaler (trend og interesse) har vært negative, noe som resulterer i en samlet retning på -1 (negativ).
- **C-uten** (13,3 s): Aksjeeksempel C viser et blandet signal, noe som indikerer en delt trend mellom trenden og bevegelsen. Interesseindikatoren viste også et negativt signal, noe som indikerer en nedgang i handelsvolumet. Imidlertid var styrken til signalet høy, med alle tre av de tre sjekkene som viste et positivt signal. Dette indikerer en sterk trend i favør av en bullish posisjon. Derfor, basert på dette signalet, kan det være tilrådelig å vurdere å kjøpe aksjeeksempel C. Det er imidlertid viktig å merke seg at dette bare er ett signal, og markedsforholdene kan endres raskt. Derfor anbefales det å konsultere ytterligere kilder og utføre grundig forskning før du tar investeringsbeslutninger.
- **C-med** (35,8 s): Aksjeeksempel C er en regelbasert signal for én aksje på Oslo Børs. Signalet er basert på tre nøkkelindikatorer: trenden, bevegelsen og interessen.  Trendindikatoren sammenligner aksjens pris med sitt glidende gjennomsnitt (MA50) over de siste 50 dagene. En positiv trend er indikert når prisen er høyere enn MA50, og en negativ trend er indikert når prisen er lavere enn MA50. I dette tilfellet er trenden positiv, med en +1-score.  Bevegelsesindikatoren måler dagens endring i pris sammenlignet med det vanlige daglige utslaget over de siste 20 dagene. En positiv bevegelse er indikert når prisen stiger, og en negativ bevegelse er indikert når prisen faller. I dette tilfellet er bevegelsen negativ, med en -1-score.  Interesseindikatoren måler dagens handelsvolum sammenlignet med medianvolumet over de siste 20 dagene. En positiv interesse er indikert når volumet er høyere enn medianen, og en negativ interesse er indikert når volumet er lavere enn medianen. I dette tilfellet er interessen negativ, med en -1-score.  Styrkeindikatoren teller antall positive trender blant de tre indikatorene. En styrke på 3 betyr at alle tre indikatorene ga et positivt signal. I dette tilfellet er styrken 3.  Retningindikatoren bestemmer den generelle retningen til signalet. Den kan være positiv, negativ, blandet eller ingen. I dette tilfellet er retningen blandet, noe som betyr at signalet ikke er sterkt nok til å indikere en klar retning.  Oppsummert er aksjeeksempel C et blandet signal, med en positiv trend, negativ bevegelse og negativ interesse. Styrken på 3 indikerer at dette signalet er sterkt, men retningen er blandet, noe som betyr at investorer kanskje vil vente på ytterligere bekreftelse før de tar noen avgjørelser.
- **D-uten** (7,8 s): Aksjeeksempel D viser for øyeblikket ingen trend. Aksjen har beveget seg innenfor sitt vanlige daglige område de siste 20 dagene, men det er ingen signifikant endring i dag sammenlignet med dette gjennomsnittet. Interessen for aksjen er også minimal, med dagens handelsvolum som ligger under gjennomsnittet. Basert på disse faktorene har aksjen ingen trend og anses å være i en flat eller hakkete fase.
- **D-med** (11,1 s): Aksjeeksempel D følger ikke en klar trend, ettersom kursen har beveget seg både opp og ned sammenlignet med gjennomsnittet de siste 50 dagene (MA50). Dagens endring i forhold til det vanlige daglige utslaget de siste 20 dagene er også ubetydelig, og ligger innenfor det forventede området. Interessen for aksjen er også minimal, ettersom dagens handelsvolum er under gjennomsnittet. Basert på disse faktorene tildeles Aksjeeksempel D en styrke på 0 av 3 mulige. Aksjen viser ingen klar retning, så retningen tildeles Ingen.
- **E-uten** (21,0 s): Aksjeeksempel E viser en negativ trend, noe som indikerer at kursen har vært konsekvent synkende sammenlignet med gjennomsnittet de siste 50 dagene. I tillegg viser den en nøytral bevegelse, noe som betyr at dagens endring ikke er betydelig sammenlignet med det vanlige daglige utslaget de siste 20 dagene. Interessenivået er også nøytralt, med dagens handelsvolum som samsvarer med medianvolumet de siste 20 dagene.  Styrken til denne regelen er indikert av styrken, som er 1 i dette tilfellet. Styrke måler antall positive, negative eller nøytrale signaler blant de tre faktorene som vurderes. Når styrken er 1, indikerer det at alle tre faktorene viser et negativt signal.  Retningen til denne regelen er negativ, noe som betyr at basert på de nåværende markedsforholdene, er det sannsynlig at aksjekursen vil fortsette å synke. Denne regelen er basert på analysen av historiske data og gir innsikt i potensielle fremtidige prisbevegelser. Det er imidlertid viktig å merke seg at tidligere resultater ikke er en garanti for fremtidige resultater, og investorer bør alltid gjøre sin egen forskning og konsultere en finansiell rådgiver før de tar investeringsbeslutninger.
- **E-med** (12,6 s): Aksjeeksempel E viser en negativ trend, noe som betyr at kursen har gått ned sammenlignet med gjennomsnittet de siste 50 dagene. Denne trenden er betydelig, ettersom den er -2,9 % mot MA50. I tillegg er det ingen interesse for aksjen, noe som betyr at dagens volum er under gjennomsnittet for de siste 20 dagene. Imidlertid er det ett positivt aspekt ved denne aksjen, og det er at styrken er 1. Dette indikerer at det er minst én av de tre sjekkene som ble utført på aksjen, som ga et positivt resultat. Til slutt er retningen for denne aksjen negativ.
- **Dag** (23,3 s): Basert på informasjonen som er oppgitt, var det 15 aksjer som ble handlet på Oslo Børs i løpet av handelsdagen. Av disse skilte tre aksjer seg ut med en styrke på 2 eller mer, noe som indikerer et sterkt handelsvolum. Tre aksjer hadde en positiv retning, noe som betyr at de presterte bedre enn markedet som helhet. På den annen side hadde fire aksjer en negativ retning, noe som betyr at de presterte dårligere enn markedet. To aksjer hadde en blandet retning, noe som betyr at de presterte omtrent som markedet. Til slutt hadde fire aksjer ingen retning, noe som betyr at de ikke presterte bedre eller dårligere enn markedet. I tillegg hadde seks aksjer bedre resultater enn hovedindeksen, noe som indikerer at de presterte bedre enn markedet som helhet. Hovedindeksen gikk ned i løpet av handelsdagen. Energi-, sjømat-, finans- og industrisektorene hadde varierende resultater. Energi- og industrisektorene hadde tre aksjer hver som presterte bedre enn markedet, mens sjømat- og finanssektorene hadde en aksje hver som presterte bedre enn markedet.

---

## 20. Sjømat-fem i samme vindu, og alle 65 rangert (2026-10-05)

**Metode.** Som i §15–§18: ett `/api/eod`-kall per symbol, med
`from=2026-07-02` og `to=2026-10-02`, samme vindu. Omsetning regnes som
`volume × close` per handelsdag, og medianen tas over perioden. Symbolene er de
fem fra §13, som §18 sa ikke var med fordi vinduet der var et annet. Målingen ble
kjørt 05.10, etter den daglige hentingen, med de 5 kallene som var
igjen, etter Marians beslutning kl. 22:11.

**Kostnad.** 5 kall, tatt av dagskvoten 05.10. Før målingen sto `apiRequests` på
15 for 2026-10-05, etter den daglige hentingen. Etter første kall sto den på 16
med `extraLimit` uendret på 463. Etter målingen er `apiRequests` 20 og
`extraLimit` fortsatt 463. Ingen kall feilet, og ingen symboler var tomme.

**Rådata.** `data/raa/maaling-raa-2026-10-05.json`. Fila finnes **bare
lokalt** og er ikke sporet i git. Bare tallene under er regnet ut og ført her.

| Symbol | Selskap | Handelsdager | Median omsetning | Over 32 MNOK | Over 25 MNOK | Plass av 65 |
|---|---|---:|---:|---|---|---:|
| BAKKA | Bakkafrost | 67 | 36,2 MNOK | Ja | Ja | 32 |
| LSG | Lerøy Seafood Group | 67 | 17,5 MNOK | Nei | Nei | 45 |
| AUSS | Austevoll Seafood | 67 | 9,7 MNOK | Nei | Nei | 50 |
| GSF | Grieg Seafood | 67 | 6,7 MNOK | Nei | Nei | 57 |
| SALME | Salmon Evolution | 67 | 2,5 MNOK | Nei | Nei | 65 |

Plassen er regnet mot de 60 medianene i rangeringen i §18, som er i samme vindu.
Ingen av de fem har samme median som en av de 60. Med de fem er 36 av de 65 over
32 MNOK, og 39 er over 25 MNOK. Bakkafrost er den eneste av de fem over begge.

I §13, med vinduet 2026-06-30 til 2026-09-30, var tallene 36,7, 18,3, 9,7, 6,7 og
2,6 MNOK. Svaret på kriteriet i §3 er det samme i begge vinduene.

Målingen endrer ikke universet. Parametrene i signalet er låst og målt på de
15 (AD-13).

## 21. Fem til fra rådets liste, og alle 70 rangert (2026-10-06)

**Metode.** Som i §18 og §20: ett `/api/eod`-kall per symbol, med
`from=2026-07-02` og `to=2026-10-02`, samme vindu. Omsetning regnes som
`volume × close` per handelsdag, og medianen tas over perioden. Målingen ble
kjørt 06.10, etter den daglige hentingen, med de 5 kallene som var igjen.

De fem er de neste etter markedsverdi på rådets liste 02.10, satt sammen fra
stockanalysis.com, uten dem som alt er målt. Rådet har lista og trakk fra de 65
i §15–§20, og plassen på lista står i tabellen. B-aksjer er hoppet over, så
ODFB på plass 68 er ikke med. Lista finnes ikke i repoet. Markedsverdien er bare
brukt som en rekkefølge for målingen, og er ikke et tall appen bruker.

**Kostnad.** 5 kall, tatt av dagskvoten 06.10. Før målingen sto `apiRequests` på
15 for 2026-10-06, etter den daglige hentingen. Etter første kall sto den på 16
med `extraLimit` uendret på 463. Etter målingen er `apiRequests` 20 og
`extraLimit` fortsatt 463. Ingen kall feilet, og ingen symboler var tomme.

**Rådata.** `data/raa/maaling-raa-2026-10-06.json`. Fila finnes **bare
lokalt** og er ikke sporet i git. Bare tallene under er regnet ut og ført her.

| Symbol | Selskap | Plass på lista | Handelsdager | Median omsetning | Over 32 MNOK | Over 25 MNOK | Plass av 70 |
|---|---|---:|---:|---:|---|---|---:|
| AKBM | Aker BioMarine | 65 | 67 | 0,9 MNOK | Nei | Nei | 69 |
| BONHR | Bonheur | 66 | 67 | 3,6 MNOK | Nei | Nei | 65 |
| ODF | Odfjell SE | 67 | 67 | 5,2 MNOK | Nei | Nei | 60 |
| AFK | Arendals Fossekompani | 69 | 67 | 0,6 MNOK | Nei | Nei | 70 |
| NORBT | Norbit | 70 | 67 | 22,8 MNOK | Nei | Nei | 42 |

Alle fem har 67 handelsdager, fra 2026-07-02 til 2026-10-02. Ingen av de fem er
over 25 MNOK. Med de fem er fortsatt 36 av de 70 over 32 MNOK, og 39 over
25 MNOK.

### Alle 70, rangert

De 60 fra §18, de 5 fra §20 og de 5 over, alle i samme vindu. Tallene for de 65
er regnet på nytt fra de lokale råfilene og er de samme som i §18 og §20. Ingen
av de ti fra §20 og §21 er i OBX (se §18). Der to aksjer har samme avrundede
median, står den med høyest uavrundet median først.

| # | Symbol | Selskap | Median omsetning (MNOK) | Blant de 15 | I OBX | Fra |
|---|---|---|---:|---|---|---|
| 1 | EQNR | Equinor | 937,9 | Ja | Ja | §17 |
| 2 | DNB | DNB Bank | 391,2 | Ja | Ja | §17 |
| 3 | KOG | Kongsberg Gruppen | 363,6 | Ja | Ja | §17 |
| 4 | AKRBP | Aker BP | 312,1 | Ja | Ja | §17 |
| 5 | FRO | Frontline | 303,2 | Ja | Ja | §17 |
| 6 | NHY | Norsk Hydro | 276,7 | Ja | Ja | §17 |
| 7 | VAR | Vår Energi | 252,9 | Ja | Ja | §17 |
| 8 | TEL | Telenor | 226,2 | Ja | Ja | §17 |
| 9 | YAR | Yara International | 213,1 | Ja | Ja | §17 |
| 10 | MOWI | Mowi | 187,5 | Ja | Ja | §17 |
| 11 | AKER | Aker | 150,5 | Nei | Ja | §15 |
| 12 | ORK | Orkla | 140,3 | Ja | Ja | §17 |
| 13 | NOD | Nordic Semiconductor | 132,5 | Nei | Ja | §16 |
| 14 | VEND | Vend Marketplaces | 108,7 | Nei | Ja | §16 |
| 15 | STB | Storebrand | 87,8 | Nei | Ja | §15 |
| 16 | SUBC | Subsea 7 | 83,7 | Nei | Ja | §15 |
| 17 | SALM | SalMar | 83,3 | Ja | Ja | §17 |
| 18 | BNOR | BlueNord | 78,4 | Nei | Ja | §16 |
| 19 | BWLPG | BW LPG | 70,4 | Nei | Ja | §15 |
| 20 | NAS | Norwegian Air Shuttle | 70,2 | Nei | Ja | §16 |
| 21 | GJF | Gjensidige Forsikring | 60,5 | Ja | Ja | §17 |
| 22 | KMAR | Kongsberg Maritime | 58,3 | Nei | Ja | §15 |
| 23 | HAUTO | Höegh Autoliners | 57,0 | Nei | Ja | §16 |
| 24 | KIT | Kitron | 56,5 | Nei | Nei | §18 |
| 25 | AUTO | AutoStore | 52,1 | Nei | Nei | §16 |
| 26 | TGS | TGS | 49,7 | Nei | Ja | §16 |
| 27 | WAWI | Wallenius Wilhelmsen | 47,6 | Nei | Nei | §16 |
| 28 | CMBTO | CMB.TECH | 47,6 | Nei | Nei | §16 |
| 29 | OET | Okeanis Eco Tankers | 46,1 | Nei | Nei | §16 |
| 30 | TOM | Tomra | 45,7 | Nei | Ja | §16 |
| 31 | DNO | DNO | 40,5 | Ja | Nei | §17 |
| 32 | BAKKA | Bakkafrost | 36,2 | Nei | Nei | §20 |
| 33 | HAFNI | Hafnia | 35,0 | Nei | Nei | §16 |
| 34 | DOFG | DOF Group | 34,0 | Nei | Nei | §16 |
| 35 | MPCC | MPC Container Ships | 33,9 | Ja | Nei | §17 |
| 36 | SCATC | Scatec | 33,2 | Nei | Nei | §18 |
| 37 | SB1NO | SpareBank 1 Sør-Norge | 31,7 | Nei | Nei | §16 |
| 38 | PROT | Protector Forsikring | 30,7 | Nei | Nei | §16 |
| 39 | CAPT | Capital Tankers | 28,4 | Nei | Nei | §18 |
| 40 | ELK | Elkem | 24,5 | Nei | Nei | §18 |
| 41 | ODL | Odfjell Drilling | 23,9 | Nei | Nei | §18 |
| 42 | NORBT | Norbit | 22,8 | Nei | Nei | §21 |
| 43 | CADLR | Cadeler | 21,2 | Nei | Nei | §18 |
| 44 | SBNOR | Sparebanken Norge | 19,1 | Nei | Nei | §16 |
| 45 | MING | SpareBank 1 SMN | 17,8 | Nei | Nei | §16 |
| 46 | LSG | Lerøy Seafood Group | 17,5 | Nei | Nei | §20 |
| 47 | AKSO | Aker Solutions | 14,8 | Nei | Nei | §18 |
| 48 | COSH | Constellation Oil Services | 14,3 | Nei | Nei | §18 |
| 49 | EPR | Europris | 13,4 | Nei | Nei | §18 |
| 50 | VEI | Veidekke | 10,0 | Nei | Nei | §16 |
| 51 | AUSS | Austevoll Seafood | 9,7 | Nei | Nei | §20 |
| 52 | ATEA | Atea | 9,4 | Nei | Nei | §18 |
| 53 | NONG | SpareBank 1 Nord-Norge | 9,2 | Nei | Nei | §18 |
| 54 | BRG | Borregaard | 8,8 | Nei | Nei | §18 |
| 55 | SNI | Stolt-Nielsen | 8,3 | Nei | Nei | §18 |
| 56 | WWI | Wilh. Wilhelmsen Holding | 8,3 | Nei | Nei | §16 |
| 57 | NORCO | Norconsult | 7,0 | Nei | Nei | §18 |
| 58 | GSF | Grieg Seafood | 6,7 | Nei | Nei | §20 |
| 59 | SPOL | SpareBank 1 Østlandet | 5,2 | Nei | Nei | §16 |
| 60 | ODF | Odfjell SE | 5,2 | Nei | Nei | §21 |
| 61 | SWON | SoftwareOne | 4,8 | Nei | Nei | §18 |
| 62 | ENTRA | Entra | 4,8 | Nei | Nei | §18 |
| 63 | BORR | Borr Drilling | 4,8 | Nei | Nei | §18 |
| 64 | AFG | AF Gruppen | 4,3 | Nei | Nei | §18 |
| 65 | BONHR | Bonheur | 3,6 | Nei | Nei | §21 |
| 66 | SOMA | Solstad Maritime | 3,5 | Nei | Nei | §18 |
| 67 | BWE | BW Energy | 3,4 | Nei | Nei | §18 |
| 68 | SALME | Salmon Evolution | 2,5 | Nei | Nei | §20 |
| 69 | AKBM | Aker BioMarine | 0,9 | Nei | Nei | §21 |
| 70 | AFK | Arendals Fossekompani | 0,6 | Nei | Nei | §21 |

*Rettet 2026-10-06:* to navn fikk komma i stedet for punktum da desimaltegnene ble gjort om. Her sto `| 28 | CMBTO | CMB,TECH | 47,6 | Nei | Nei | §16 |` og `| 56 | WWI | Wilh, Wilhelmsen Holding | 8,3 | Nei | Nei | §16 |`. Navnene er nå som i §16–§20. Ingen andre navn eller tall i §21 hadde samme feil.

Målingen endrer ikke universet. Parametrene i signalet er låst og målt på de
15 (AD-13).

---

## 22. Er kveldens rad endelig? (2026-10-07)

**Formål.** Svare på setningen i §12: «Om raden for 24.09 er endelig, viser
først neste henting.» Det trengs nå fordi interesse ga 0 utslag på 60
aksjedager (02.10, 05.10, 06.10 og 07.10), mot 14,9 % utslag i §7.4
(8,0 % +1 og 6,9 % −1 over 199 dager). Er dagens volum ikke ferdig når vi
henter, slår interesse sjeldnere ut enn den skal.

**Kostnad.** 0 kall. Bare kursfilene i `data/raa/` er lest, og basen er ikke
lest.

**Metode.** De ti kursfilene `kurser-raa-*.json` fra 22.09 til 07.10 er tatt i
datorekkefølge, to og to, så det blir ni par. For hvert par er siste rad i den
første fila sammenlignet med raden for samme dato i den neste, for alle 15
aksjene. Interesse er regnet for datoen med `beregn_signal` i
`signalberegning.py`, slik appen gjør, én gang med serien fra den første fila og
én gang med serien fra den neste, kuttet ved samme dato. Seriene er lest med
`SnapshotLeser`. Det nederste paret (07.10 mot 08.10) kan først måles etter
neste henting. Bare antall og forholdstall er ført her (regel 16).

| Fila | Hentet (norsk tid) | Dato | Annet `volume` | Annen `close` | Annen `adjusted_close` | `volume` ny/gammel: minst / median / størst | Interesse skifter |
|---|---|---|---:|---:|---:|---|---:|
| `kurser-raa-2026-09-22.json` | 22.09 10:33 | 2026-09-21 | 1 av 15 | 0 | 0 | 0,9919 / 1,0000 / 1,0000 | 0 |
| `kurser-raa-2026-09-23.json` | 23.09 19:04 | 2026-09-22 | 0 av 15 | 0 | 0 | 1,0000 / 1,0000 / 1,0000 | 0 |
| `kurser-raa-2026-09-24.json` | 24.09 21:31 | 2026-09-24 | 1 av 15 | 0 | 0 | 1,0000 / 1,0000 / 1,0004 | 0 |
| `kurser-raa-2026-09-29.json` | 29.09 22:27 | 2026-09-29 | 0 av 15 | 0 | 0 | 1,0000 / 1,0000 / 1,0000 | 0 |
| `kurser-raa-2026-09-30.json` | 30.09 22:09 | 2026-09-30 | 1 av 15 | 0 | 0 | 1,0000 / 1,0000 / 1,0008 | 0 |
| `kurser-raa-2026-10-01.json` | 01.10 23:13 | 2026-10-01 | 0 av 15 | 0 | 0 | 1,0000 / 1,0000 / 1,0000 | 0 |
| `kurser-raa-2026-10-02.json` | 02.10 22:39 | 2026-10-02 | 3 av 15 | 0 | 0 | 1,0000 / 1,0000 / 1,0280 | 0 |
| `kurser-raa-2026-10-05.json` | 05.10 22:09 | 2026-10-05 | 2 av 15 | 0 | 0 | 1,0000 / 1,0000 / 1,0693 | 0 |
| `kurser-raa-2026-10-06.json` | 06.10 22:17 | 2026-10-06 | 0 av 15 | 0 | 0 | 1,0000 / 1,0000 / 1,0000 | 0 |

De to første filene ble hentet før dagens rad var kommet. Siste rad er derfor
dagen før, og den raden var en dag gammel da den ble hentet. Fra 24.09 er siste
rad dagens.

Volumet endret seg for disse, med forholdet ny/gammel:

| Fila | Symbol | Dato | Ny/gammel |
|---|---|---|---:|
| `kurser-raa-2026-09-22.json` | MOWI | 2026-09-21 | 0,9919 |
| `kurser-raa-2026-09-24.json` | AKRBP | 2026-09-24 | 1,0004 |
| `kurser-raa-2026-09-30.json` | MOWI | 2026-09-30 | 1,0008 |
| `kurser-raa-2026-10-02.json` | NHY | 2026-10-02 | 1,0233 |
| `kurser-raa-2026-10-02.json` | MOWI | 2026-10-02 | 1,0280 |
| `kurser-raa-2026-10-02.json` | ORK | 2026-10-02 | 1,0137 |
| `kurser-raa-2026-10-05.json` | VAR | 2026-10-05 | 1,0693 |
| `kurser-raa-2026-10-05.json` | ORK | 2026-10-05 | 1,0116 |

**Interesse.** 0 av 135 rader skifter verdi på interesse mellom den første og
den neste fila.

For å se hvor nær terskelen dagene var, er volumforholdet regnet for alle 15 på
hver av de fire dagene uten utslag, fra fila for dagen. Ingen er over 1,5×.
Det største forholdet var 1,28 (NHY) 02.10, 1,30 (FRO) 05.10, 1,21 (GJF) 06.10
og 1,40 (YAR) 07.10. Den største revisjonen i tabellen, 6,9 %, ville ikke løftet
noen av disse over 1,5×.

**Konklusjon.**

- **`close` og `adjusted_close` er endelige når vi henter etter kl. 22.** Ingen
  av de 90 radene fra de seks hentingene etter kl. 22 er endret dagen etter.
- **`volume` er nesten endelig.** 6 av de 90 radene fikk et høyere volum dagen
  etter, med 0,08 % til 6,9 %. Ingen fikk lavere volum. Det eneste fallet,
  MOWI med 0,9919, var en rad som var en dag gammel da den ble hentet kl. 10:33
  22.09.
- **For interesse betyr det lite.** Ingen verdi på interesse skifter. De 0
  utslagene på 60 aksjedager skyldes ikke et volum som ikke er ferdig: det
  største forholdet på de fire dagene var 1,40, og terskelen er 1,5×.
  Volumforholdet som lagres i `vurdering`, kan likevel være noen prosent for
  lavt. En aksje med forhold mellom om lag 1,40 og 1,5 kan da slå ut dagen
  etter, men ikke i den lagrede vurderingen.
- **Ingen endring trengs nå, verken i koden eller i hentetidspunktet.** Det som
  er åpent, er hvorfor fire dager på rad har gitt 0 utslag mot 14,9 % i §7.4.
  Målingen her sier bare at årsaken ikke er hentetidspunktet. Paret 07.10 mot
  08.10 måles etter neste henting.

*Lagt til 2026-10-07 kl. 23:02:* er det rolige dager? Ja, men ikke uvanlig rolige.
Interesse er regnet med `beregn_signal` i `signalberegning.py`, slik appen gjør,
for hver dag i `kurser-raa-2026-10-07.json` der signalet kan regnes. Det første
er dag 51 i serien, og det gir 200 dager fra 2025-12-17 til 2026-10-07 og 3 000
aksjedager for de 15. Vinduet overlapper §7.4 (2025-12-01 til 2026-09-18), men er
ikke det samme.

| Periode | Dager | +1 | −1 | Utslag i alt |
|---|---:|---:|---:|---:|
| §7.4 (199 dager) | 199 | 8,0 % | 6,9 % | 14,9 % |
| Hele fila | 200 | 7,6 % | 6,9 % | 14,5 % |
| 2025-12 (fra 17.12) | 7 | 12,4 % | 3,8 % | 16,2 % |
| 2026-01 | 21 | 14,3 % | 8,9 % | 23,2 % |
| 2026-02 | 20 | 9,7 % | 5,0 % | 14,7 % |
| 2026-03 | 22 | 13,6 % | 9,4 % | 23,0 % |
| 2026-04 | 19 | 2,1 % | 5,3 % | 7,4 % |
| 2026-05 | 18 | 4,8 % | 12,6 % | 17,4 % |
| 2026-06 | 22 | 5,8 % | 7,0 % | 12,7 % |
| 2026-07 | 23 | 3,5 % | 4,1 % | 7,5 % |
| 2026-08 | 21 | 10,5 % | 5,7 % | 16,2 % |
| 2026-09 | 22 | 4,2 % | 6,7 % | 10,9 % |
| 2026-10 (til 07.10) | 5 | 0,0 % | 2,7 % | 2,7 % |
| Siste 20 børsdager (10.09–07.10) | 20 | 3,0 % | 6,3 % | 9,3 % |

**43 av de 200 dagene** (21,5 %) hadde 0 utslag på interesse for alle 15. Slike
dager kom i 26 perioder: 15 på én dag, 7 på to dager, 2 på tre dager og 2 på fire
dager. De lengste var 2026-04-13 til 2026-04-16 og 2026-10-02 til 2026-10-07, fire
børsdager hver. Deretter kom 2026-03-24 til 2026-03-26 og 2026-07-03 til
2026-07-07, tre børsdager hver.

Svaret er at de fire dagene uten utslag er rolige dager, ikke en feil. Over hele
fila slår interesse ut like ofte som i §7.4 (14,5 % mot 14,9 %), og andelen
varierer mye fra måned til måned, fra 7,4 % i april til 23,2 % i januar. De siste
20 børsdagene ligger lavt, på 9,3 %, og fire dager på rad med 0 utslag har
skjedd før, i april. Utslagene samler seg på noen få dager: 18.09 hadde 13 av 15,
mens 16 av de andre 19 dagene i det samme vinduet hadde 0 eller 1. Det trengs
ingen endring i koden.

---

## 23. Fem til fra rådets liste, og alle 75 rangert (2026-10-07)

**Metode.** Som i §21: ett `/api/eod`-kall per symbol, med `from=2026-07-02` og
`to=2026-10-02`, samme vindu. Omsetning regnes som `volume × close` per
handelsdag, og medianen tas over perioden. Målingen ble kjørt 07.10, etter den
daglige hentingen, med de 5 kallene som var igjen.

De fem er de neste etter markedsverdi på rådets liste 02.10, satt sammen fra
stockanalysis.com, uten de 70 som alt er målt. Plassen på lista står i tabellen.
B-aksjer er hoppet over, som ODFB i §21. Lista finnes ikke i repoet.
Markedsverdien er bare brukt som en rekkefølge for målingen, og er ikke et tall
appen bruker.

**Kostnad.** 5 kall, tatt av dagskvoten 07.10. Før målingen sto `apiRequests` på
15 for 2026-10-07, etter den daglige hentingen. Etter første kall sto den på 16
med `extraLimit` uendret på 463. Etter målingen er `apiRequests` 20 og
`extraLimit` fortsatt 463. Ingen kall feilet, og ingen symboler var tomme.

**Rådata.** `data/raa/maaling-raa-2026-10-07.json`. Fila finnes **bare
lokalt** og er ikke sporet i git. Bare tallene under er regnet ut og ført her.

| Symbol | Selskap | Plass på lista | Handelsdager | Median omsetning | Over 32 MNOK | Over 25 MNOK | Plass av 75 |
|---|---|---:|---:|---:|---|---|---:|
| ELO | Elopak | 71 | 67 | 7,0 MNOK | Nei | Nei | 61 |
| B2I | B2 Impact | 72 | 67 | 10,1 MNOK | Nei | Nei | 52 |
| SNTIA | Sentia | 73 | 67 | 5,9 MNOK | Nei | Nei | 63 |
| SATS | Sats | 74 | 67 | 11,6 MNOK | Nei | Nei | 51 |
| HSHP | Himalaya Shipping | 75 | 67 | 22,1 MNOK | Nei | Nei | 43 |

Alle fem har 67 handelsdager, fra 2026-07-02 til 2026-10-02. Ingen av de fem er
over 25 MNOK. Med de fem er fortsatt 36 av de 75 over 32 MNOK, og 39 over
25 MNOK.

### Alle 75, rangert

De 70 fra §21 og de 5 over, alle i samme vindu. Tallene for de 70 er regnet på
nytt fra de lokale råfilene og er de samme som i §21, i samme rekkefølge. Ingen
av de fem over er i OBX, fordi alle 25 i OBX er blant de 40 i §17 (se §18). Der
to aksjer har samme avrundede median, står den med høyest uavrundet median
først.

| # | Symbol | Selskap | Median omsetning (MNOK) | Blant de 15 | I OBX | Fra |
|---|---|---|---:|---|---|---|
| 1 | EQNR | Equinor | 937,9 | Ja | Ja | §17 |
| 2 | DNB | DNB Bank | 391,2 | Ja | Ja | §17 |
| 3 | KOG | Kongsberg Gruppen | 363,6 | Ja | Ja | §17 |
| 4 | AKRBP | Aker BP | 312,1 | Ja | Ja | §17 |
| 5 | FRO | Frontline | 303,2 | Ja | Ja | §17 |
| 6 | NHY | Norsk Hydro | 276,7 | Ja | Ja | §17 |
| 7 | VAR | Vår Energi | 252,9 | Ja | Ja | §17 |
| 8 | TEL | Telenor | 226,2 | Ja | Ja | §17 |
| 9 | YAR | Yara International | 213,1 | Ja | Ja | §17 |
| 10 | MOWI | Mowi | 187,5 | Ja | Ja | §17 |
| 11 | AKER | Aker | 150,5 | Nei | Ja | §15 |
| 12 | ORK | Orkla | 140,3 | Ja | Ja | §17 |
| 13 | NOD | Nordic Semiconductor | 132,5 | Nei | Ja | §16 |
| 14 | VEND | Vend Marketplaces | 108,7 | Nei | Ja | §16 |
| 15 | STB | Storebrand | 87,8 | Nei | Ja | §15 |
| 16 | SUBC | Subsea 7 | 83,7 | Nei | Ja | §15 |
| 17 | SALM | SalMar | 83,3 | Ja | Ja | §17 |
| 18 | BNOR | BlueNord | 78,4 | Nei | Ja | §16 |
| 19 | BWLPG | BW LPG | 70,4 | Nei | Ja | §15 |
| 20 | NAS | Norwegian Air Shuttle | 70,2 | Nei | Ja | §16 |
| 21 | GJF | Gjensidige Forsikring | 60,5 | Ja | Ja | §17 |
| 22 | KMAR | Kongsberg Maritime | 58,3 | Nei | Ja | §15 |
| 23 | HAUTO | Höegh Autoliners | 57,0 | Nei | Ja | §16 |
| 24 | KIT | Kitron | 56,5 | Nei | Nei | §18 |
| 25 | AUTO | AutoStore | 52,1 | Nei | Nei | §16 |
| 26 | TGS | TGS | 49,7 | Nei | Ja | §16 |
| 27 | WAWI | Wallenius Wilhelmsen | 47,6 | Nei | Nei | §16 |
| 28 | CMBTO | CMB.TECH | 47,6 | Nei | Nei | §16 |
| 29 | OET | Okeanis Eco Tankers | 46,1 | Nei | Nei | §16 |
| 30 | TOM | Tomra | 45,7 | Nei | Ja | §16 |
| 31 | DNO | DNO | 40,5 | Ja | Nei | §17 |
| 32 | BAKKA | Bakkafrost | 36,2 | Nei | Nei | §20 |
| 33 | HAFNI | Hafnia | 35,0 | Nei | Nei | §16 |
| 34 | DOFG | DOF Group | 34,0 | Nei | Nei | §16 |
| 35 | MPCC | MPC Container Ships | 33,9 | Ja | Nei | §17 |
| 36 | SCATC | Scatec | 33,2 | Nei | Nei | §18 |
| 37 | SB1NO | SpareBank 1 Sør-Norge | 31,7 | Nei | Nei | §16 |
| 38 | PROT | Protector Forsikring | 30,7 | Nei | Nei | §16 |
| 39 | CAPT | Capital Tankers | 28,4 | Nei | Nei | §18 |
| 40 | ELK | Elkem | 24,5 | Nei | Nei | §18 |
| 41 | ODL | Odfjell Drilling | 23,9 | Nei | Nei | §18 |
| 42 | NORBT | Norbit | 22,8 | Nei | Nei | §21 |
| 43 | HSHP | Himalaya Shipping | 22,1 | Nei | Nei | §23 |
| 44 | CADLR | Cadeler | 21,2 | Nei | Nei | §18 |
| 45 | SBNOR | Sparebanken Norge | 19,1 | Nei | Nei | §16 |
| 46 | MING | SpareBank 1 SMN | 17,8 | Nei | Nei | §16 |
| 47 | LSG | Lerøy Seafood Group | 17,5 | Nei | Nei | §20 |
| 48 | AKSO | Aker Solutions | 14,8 | Nei | Nei | §18 |
| 49 | COSH | Constellation Oil Services | 14,3 | Nei | Nei | §18 |
| 50 | EPR | Europris | 13,4 | Nei | Nei | §18 |
| 51 | SATS | Sats | 11,6 | Nei | Nei | §23 |
| 52 | B2I | B2 Impact | 10,1 | Nei | Nei | §23 |
| 53 | VEI | Veidekke | 10,0 | Nei | Nei | §16 |
| 54 | AUSS | Austevoll Seafood | 9,7 | Nei | Nei | §20 |
| 55 | ATEA | Atea | 9,4 | Nei | Nei | §18 |
| 56 | NONG | SpareBank 1 Nord-Norge | 9,2 | Nei | Nei | §18 |
| 57 | BRG | Borregaard | 8,8 | Nei | Nei | §18 |
| 58 | SNI | Stolt-Nielsen | 8,3 | Nei | Nei | §18 |
| 59 | WWI | Wilh. Wilhelmsen Holding | 8,3 | Nei | Nei | §16 |
| 60 | NORCO | Norconsult | 7,0 | Nei | Nei | §18 |
| 61 | ELO | Elopak | 7,0 | Nei | Nei | §23 |
| 62 | GSF | Grieg Seafood | 6,7 | Nei | Nei | §20 |
| 63 | SNTIA | Sentia | 5,9 | Nei | Nei | §23 |
| 64 | SPOL | SpareBank 1 Østlandet | 5,2 | Nei | Nei | §16 |
| 65 | ODF | Odfjell SE | 5,2 | Nei | Nei | §21 |
| 66 | SWON | SoftwareOne | 4,8 | Nei | Nei | §18 |
| 67 | ENTRA | Entra | 4,8 | Nei | Nei | §18 |
| 68 | BORR | Borr Drilling | 4,8 | Nei | Nei | §18 |
| 69 | AFG | AF Gruppen | 4,3 | Nei | Nei | §18 |
| 70 | BONHR | Bonheur | 3,6 | Nei | Nei | §21 |
| 71 | SOMA | Solstad Maritime | 3,5 | Nei | Nei | §18 |
| 72 | BWE | BW Energy | 3,4 | Nei | Nei | §18 |
| 73 | SALME | Salmon Evolution | 2,5 | Nei | Nei | §20 |
| 74 | AKBM | Aker BioMarine | 0,9 | Nei | Nei | §21 |
| 75 | AFK | Arendals Fossekompani | 0,6 | Nei | Nei | §21 |

Målingen endrer ikke universet. Parametrene i signalet er låst og målt på de
15 (AD-13).

## 24. Fem til fra rådets liste, og alle 80 rangert (2026-10-08)

**Metode.** Som i §23: ett `/api/eod`-kall per symbol, med `from=2026-07-02` og
`to=2026-10-02`, samme vindu. Omsetning regnes som `volume × close` per
handelsdag, og medianen tas over perioden. Målingen ble kjørt 08.10, etter den
daglige hentingen, med de 5 kallene som var igjen.

De fem er de neste etter markedsverdi på rådets liste 02.10, satt sammen fra
stockanalysis.com, uten de 75 som alt er målt. Plassen på lista står i tabellen.
B-aksjer er hoppet over, som ODFB i §21. Lista finnes ikke i repoet.
Markedsverdien er bare brukt som en rekkefølge for målingen, og er ikke et tall
appen bruker.

**Kostnad.** 5 kall, tatt av dagskvoten 08.10. Før målingen sto `apiRequests` på
15 for 2026-10-08, etter den daglige hentingen. Etter første kall sto den på 16
med `extraLimit` uendret på 463. Etter målingen er `apiRequests` 20 og
`extraLimit` fortsatt 463. Ingen kall feilet, og ingen symboler var tomme.

**Rådata.** `data/raa/maaling-raa-2026-10-08.json`. Fila finnes **bare
lokalt** og er ikke sporet i git. Bare tallene under er regnet ut og ført her.

| Symbol | Selskap | Plass på lista | Handelsdager | Median omsetning | Over 32 MNOK | Over 25 MNOK | Plass av 80 |
|---|---|---:|---:|---:|---|---|---:|
| PLSV | Paratus Energy Services | 76 | 67 | 7,7 MNOK | Nei | Nei | 62 |
| PEXIP | Pexip | 77 | 67 | 8,6 MNOK | Nei | Nei | 59 |
| BWO | BW Offshore | 78 | 67 | 3,2 MNOK | Nei | Nei | 76 |
| RING | SpareBank 1 Ringerike Hadeland | 79 | 67 | 0,2 MNOK | Nei | Nei | 80 |
| LINK | LINK Mobility | 80 | 67 | 16,7 MNOK | Nei | Nei | 48 |

Alle fem har 67 handelsdager, fra 2026-07-02 til 2026-10-02. Ingen av de fem er
over 25 MNOK. Med de fem er fortsatt 36 av de 80 over 32 MNOK, og 39 over
25 MNOK.

### Alle 80, rangert

De 75 fra §23 og de 5 over, alle i samme vindu. Tallene for de 75 er regnet på
nytt fra de lokale råfilene og er de samme som i §23, i samme rekkefølge. Ingen
av de fem over er i OBX, fordi alle 25 i OBX er blant de 40 i §17 (se §18). Der
to aksjer har samme avrundede median, står den med høyest uavrundet median
først.

| # | Symbol | Selskap | Median omsetning (MNOK) | Blant de 15 | I OBX | Fra |
|---|---|---|---:|---|---|---|
| 1 | EQNR | Equinor | 937,9 | Ja | Ja | §17 |
| 2 | DNB | DNB Bank | 391,2 | Ja | Ja | §17 |
| 3 | KOG | Kongsberg Gruppen | 363,6 | Ja | Ja | §17 |
| 4 | AKRBP | Aker BP | 312,1 | Ja | Ja | §17 |
| 5 | FRO | Frontline | 303,2 | Ja | Ja | §17 |
| 6 | NHY | Norsk Hydro | 276,7 | Ja | Ja | §17 |
| 7 | VAR | Vår Energi | 252,9 | Ja | Ja | §17 |
| 8 | TEL | Telenor | 226,2 | Ja | Ja | §17 |
| 9 | YAR | Yara International | 213,1 | Ja | Ja | §17 |
| 10 | MOWI | Mowi | 187,5 | Ja | Ja | §17 |
| 11 | AKER | Aker | 150,5 | Nei | Ja | §15 |
| 12 | ORK | Orkla | 140,3 | Ja | Ja | §17 |
| 13 | NOD | Nordic Semiconductor | 132,5 | Nei | Ja | §16 |
| 14 | VEND | Vend Marketplaces | 108,7 | Nei | Ja | §16 |
| 15 | STB | Storebrand | 87,8 | Nei | Ja | §15 |
| 16 | SUBC | Subsea 7 | 83,7 | Nei | Ja | §15 |
| 17 | SALM | SalMar | 83,3 | Ja | Ja | §17 |
| 18 | BNOR | BlueNord | 78,4 | Nei | Ja | §16 |
| 19 | BWLPG | BW LPG | 70,4 | Nei | Ja | §15 |
| 20 | NAS | Norwegian Air Shuttle | 70,2 | Nei | Ja | §16 |
| 21 | GJF | Gjensidige Forsikring | 60,5 | Ja | Ja | §17 |
| 22 | KMAR | Kongsberg Maritime | 58,3 | Nei | Ja | §15 |
| 23 | HAUTO | Höegh Autoliners | 57,0 | Nei | Ja | §16 |
| 24 | KIT | Kitron | 56,5 | Nei | Nei | §18 |
| 25 | AUTO | AutoStore | 52,1 | Nei | Nei | §16 |
| 26 | TGS | TGS | 49,7 | Nei | Ja | §16 |
| 27 | WAWI | Wallenius Wilhelmsen | 47,6 | Nei | Nei | §16 |
| 28 | CMBTO | CMB.TECH | 47,6 | Nei | Nei | §16 |
| 29 | OET | Okeanis Eco Tankers | 46,1 | Nei | Nei | §16 |
| 30 | TOM | Tomra | 45,7 | Nei | Ja | §16 |
| 31 | DNO | DNO | 40,5 | Ja | Nei | §17 |
| 32 | BAKKA | Bakkafrost | 36,2 | Nei | Nei | §20 |
| 33 | HAFNI | Hafnia | 35,0 | Nei | Nei | §16 |
| 34 | DOFG | DOF Group | 34,0 | Nei | Nei | §16 |
| 35 | MPCC | MPC Container Ships | 33,9 | Ja | Nei | §17 |
| 36 | SCATC | Scatec | 33,2 | Nei | Nei | §18 |
| 37 | SB1NO | SpareBank 1 Sør-Norge | 31,7 | Nei | Nei | §16 |
| 38 | PROT | Protector Forsikring | 30,7 | Nei | Nei | §16 |
| 39 | CAPT | Capital Tankers | 28,4 | Nei | Nei | §18 |
| 40 | ELK | Elkem | 24,5 | Nei | Nei | §18 |
| 41 | ODL | Odfjell Drilling | 23,9 | Nei | Nei | §18 |
| 42 | NORBT | Norbit | 22,8 | Nei | Nei | §21 |
| 43 | HSHP | Himalaya Shipping | 22,1 | Nei | Nei | §23 |
| 44 | CADLR | Cadeler | 21,2 | Nei | Nei | §18 |
| 45 | SBNOR | Sparebanken Norge | 19,1 | Nei | Nei | §16 |
| 46 | MING | SpareBank 1 SMN | 17,8 | Nei | Nei | §16 |
| 47 | LSG | Lerøy Seafood Group | 17,5 | Nei | Nei | §20 |
| 48 | LINK | LINK Mobility | 16,7 | Nei | Nei | §24 |
| 49 | AKSO | Aker Solutions | 14,8 | Nei | Nei | §18 |
| 50 | COSH | Constellation Oil Services | 14,3 | Nei | Nei | §18 |
| 51 | EPR | Europris | 13,4 | Nei | Nei | §18 |
| 52 | SATS | Sats | 11,6 | Nei | Nei | §23 |
| 53 | B2I | B2 Impact | 10,1 | Nei | Nei | §23 |
| 54 | VEI | Veidekke | 10,0 | Nei | Nei | §16 |
| 55 | AUSS | Austevoll Seafood | 9,7 | Nei | Nei | §20 |
| 56 | ATEA | Atea | 9,4 | Nei | Nei | §18 |
| 57 | NONG | SpareBank 1 Nord-Norge | 9,2 | Nei | Nei | §18 |
| 58 | BRG | Borregaard | 8,8 | Nei | Nei | §18 |
| 59 | PEXIP | Pexip | 8,6 | Nei | Nei | §24 |
| 60 | SNI | Stolt-Nielsen | 8,3 | Nei | Nei | §18 |
| 61 | WWI | Wilh. Wilhelmsen Holding | 8,3 | Nei | Nei | §16 |
| 62 | PLSV | Paratus Energy Services | 7,7 | Nei | Nei | §24 |
| 63 | NORCO | Norconsult | 7,0 | Nei | Nei | §18 |
| 64 | ELO | Elopak | 7,0 | Nei | Nei | §23 |
| 65 | GSF | Grieg Seafood | 6,7 | Nei | Nei | §20 |
| 66 | SNTIA | Sentia | 5,9 | Nei | Nei | §23 |
| 67 | SPOL | SpareBank 1 Østlandet | 5,2 | Nei | Nei | §16 |
| 68 | ODF | Odfjell SE | 5,2 | Nei | Nei | §21 |
| 69 | SWON | SoftwareOne | 4,8 | Nei | Nei | §18 |
| 70 | ENTRA | Entra | 4,8 | Nei | Nei | §18 |
| 71 | BORR | Borr Drilling | 4,8 | Nei | Nei | §18 |
| 72 | AFG | AF Gruppen | 4,3 | Nei | Nei | §18 |
| 73 | BONHR | Bonheur | 3,6 | Nei | Nei | §21 |
| 74 | SOMA | Solstad Maritime | 3,5 | Nei | Nei | §18 |
| 75 | BWE | BW Energy | 3,4 | Nei | Nei | §18 |
| 76 | BWO | BW Offshore | 3,2 | Nei | Nei | §24 |
| 77 | SALME | Salmon Evolution | 2,5 | Nei | Nei | §20 |
| 78 | AKBM | Aker BioMarine | 0,9 | Nei | Nei | §21 |
| 79 | AFK | Arendals Fossekompani | 0,6 | Nei | Nei | §21 |
| 80 | RING | SpareBank 1 Ringerike Hadeland | 0,2 | Nei | Nei | §24 |

Målingen endrer ikke universet. Parametrene i signalet er låst og målt på de
15 (AD-13).
