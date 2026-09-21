# Målinger — grunnlaget for PRD-en

Alle tall PRD-en bygger på, med metode og dato, slik at de kan etterprøves eller
kjøres på nytt. PRD-en beholder konklusjonene; detaljene ligger her.

Grepet er at lesestrømmen ikke skal bære tallene, men at tallene skal finnes og
kunne kontrolleres.

Målingene i §0–§6 er gjort 2026-09-20. §7 er fra 2026-09-21.

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
| Hvilken nyhetskilde treffene kom fra | Kilden er nå avklart som EODHDs nyhets-API, men innsamlingen er avhengig av vilkårskontrollen — se åpne punkter 1 og 5 |
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

| # | Symbol | Selskap | Sektor | Median volum | Median omsetning | Andel av median |
|---|---|---|---|---:|---:|---:|
| 1 | EQNR | Equinor | Energi | 2 478 662 | 919,9 MNOK | 4,11× |
| 2 | DNB | DNB Bank | Finans | 1 318 670 | 400,4 MNOK | 1,79× |
| 3 | KOG | Kongsberg Gruppen | Industri | 1 228 088 | 374,7 MNOK | 1,67× |
| 4 | AKRBP | Aker BP | Energi | 886 576 | 312,1 MNOK | 1,39× |
| 5 | NHY | Norsk Hydro | Materialer | 3 220 200 | 293,0 MNOK | 1,31× |
| 6 | FRO | Frontline | Shipping | 715 503 | 284,8 MNOK | 1,27× |
| 7 | VAR | Vår Energi | Energi | 5 279 688 | 252,9 MNOK | 1,13× |
| 8 | TEL | Telenor | Telekom | 1 632 539 | 223,9 MNOK | 1,00× |
| 9 | YAR | Yara International | Materialer | 496 492 | 220,5 MNOK | 0,98× |
| 10 | MOWI | Mowi | Sjømat | 900 050 | 182,1 MNOK | 0,81× |
| 11 | ORK | Orkla | Konsum | 1 385 880 | 140,3 MNOK | 0,63× |
| 12 | SALM | SalMar | Sjømat | 159 922 | 81,8 MNOK | 0,37× |
| 13 | GJF | Gjensidige Forsikring | Finans | 214 425 | 59,8 MNOK | 0,27× |
| 14 | DNO | DNO | Energi | 1 956 182 | 34,7 MNOK | 0,16× |
| 15 | MPCC | MPC Container Ships | Shipping | 1 253 156 | 32,3 MNOK | 0,14× |

Median for universet: 223,9 MNOK per dag.

**Funnet som avgjorde kriteriet.** DNO omsetter 1 956 182 aksjer per dag — flere
enn DNB — men til 19,62 kroner blir det 34,7 MNOK mot DNBs 400,4 MNOK. MPCC
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

- «Equinor ASA: Share buy-back — third tranche for 2026» og
  «Equinor ASA: Tilbakekjøp av egne aksjer — tredje transje for 2026»
- «DNB Bank ASA — status of share buy-back programme after week 34 2026» og
  «DNB Bank ASA — status for tilbakekjøpsprogram etter uke 34 2026»

Skrevet inn som FR-501.

### Samlekategorien — belegget for KI-vurderingen

De 18 meldingene i `IKKE-INFORMASJONSPLIKTIGE PRESSEMELDINGER` inneholder både
reelle hendelser og ren støy, med samme kategorifelt:

| Reell hendelse | Støy |
|---|---|
| Aker BP has started production from the Skarv Satellites | Invitation to Hydro's Investor Day, London |
| KONGSBERG completes Sonatech acquisition | MPCC to present at the Pareto Securities' Energy Conference |
| Telenor's subsidiary KNL secures framework agreement with the Danish Armed Forces | Gjensidige appoints Berit Nilsen as Head of Investor Relations |
| Completion of the Telenor Connexion Transaction | Gjensidige hosts its Analyst Day 2026 today |

### Tilbakekjøpskategorien — samme problem

| Reell hendelse | Rutine |
|---|---|
| SalMar — Oppstart for tilbakekjøpsprogram for aksjer | DNB Bank ASA — status for tilbakekjøpsprogram etter uke 34 2026 |

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
| Har NewsWeb et språkfelt? | Avgjør om FR-501 kan bruke språkkode eller må bygge på heuristikk | 0 kall, mandag 2026-09-21 |
| Signaltest mot ~200 handelsdager | Låse terskel, volumfaktor og nøytralsonebredde | 15 kall, tirsdag 2026-09-22 |
| Vilkårskontroll NewsWeb + Euronext | Avgjøre om datagrunnlaget holder | 0 kall, frist 2026-09-27 |
| Relevanseksperiment, 50 medieartikler | Symbolmatching mot KI-klassifisering | Restkvoten én gang, uke 41 |

**Rekkefølgen er bestemt av kvoten, ikke av prioritet.** Nyhetstesten var
budsjettert til 10 kall og signaltesten til 15; dagsgrensen er 20, så de kunne
ikke kjøres samme dag. Nyhetstesten gikk først fordi et negativt svar velter
relevanseksperimentet, og det måtte oppdages tidlig. Signaltesten kunne vente
et døgn uten at noe annet stoppet. Kvoten nullstilles midnatt GMT.

*Rettet 2026-09-21: nyhetstesten kostet 5 kall, ikke 10 (§7.2). Rekkefølgen
ville vært den samme, men premisset om at de to ikke får plass samme dag holdt
ikke.*

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
selskaper bygger på det doble kalltallet. Med 5 per ticker blir det ~40. Tallet
er ikke rettet i `prd.md` eller `begrunnelser.md` her, fordi det avhenger av
den utledede delen. Ført som eget punkt i `docs/kilder-og-rettigheter.md`.

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
