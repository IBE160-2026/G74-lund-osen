# Målinger — grunnlaget for PRD-en

Alle tall PRD-en bygger på, med metode og dato, slik at de kan etterprøves eller
kjøres på nytt. PRD-en beholder konklusjonene; detaljene ligger her.

Grepet er at lesestrømmen ikke skal bære tallene, men at tallene skal finnes og
kunne kontrolleres.

Målingene i §0–§6 er gjort 2026-09-20, §7 er fra 2026-09-21, og §8–§10 fra 2026-09-22.

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
| ~~Har NewsWeb et språkfelt?~~ | ~~Avgjør om FR-501 kan bruke språkkode eller må bygge på heuristikk~~ | **Gjort 2026-09-21, se §7.3. Svaret er nei — heuristikken må beholdes** |
| ~~Signaltest mot ~200 handelsdager~~ | ~~Låse terskel, volumfaktor og nøytralsonebredde~~ | **Gjort 2026-09-21, se §7.4. 15 kall, 199 dager. Alle tre verdiene holdt** |
| Vilkårskontroll NewsWeb + Euronext | Avgjøre om datagrunnlaget holder | 0 kall, frist 2026-09-27 |
| Relevanseksperiment del 1, innsamling av ~50 medieartikler | Grunnlaget for symbolmatching mot KI-klassifisering | `extraLimit`, uke 39–40. Kalltallet kontrolleres i første forespørsel |
| Relevanseksperiment del 2, KI-klassifiseringen | Symbolmatching mot KI-klassifisering | 0 kall mot EODHD. Venter på KI-laget og på betingelse 4 |

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

#### Tre sidefunn

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
| GOD | «Notice of Extraordinary General Meeting» og «Key information relating to the proposed supplemental cash dividend» — to *forskjellige* meldinger, begge engelske, samme minutt og kategori | **Reelt tap.** Kategorien slipper gjennom filteret, så den ene meldingen ville forsvunnet |

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

| Tittel | `gjett_spraak` gir |
|---|---|
| `Vår Energi ASA: Third quarter 2026 results` | **norsk** — feil |
| `Vår Energi ASA - Notice of Extraordinary General Meeting` | **norsk** — feil |
| `Equinor ASA: Share buy-back programme third tranche` | uavklart |

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

Samme datagrunnlag som §7.4: **2 985 aksjedager** — 15 symboler × 199
handelsdager. Grensen på 199 følger av at MA50 krever 50 dager pluss dagen som
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

EODHDs nyheter har tagger — **31 unike over ti artikler, 9 av 10 har minst én** —
men de er **tematiske**: `SHARE-BUYBACK`, `EARNINGS`, `M-A`, `VALUATION`. De
sier hva saken handler om, ikke hvilken meldeplikt den oppfyller.

Forskjellen er ikke akademisk. `SHARE-BUYBACK` skiller ikke den ukentlige
statusrapporten under «Utsteders meldeplikt ved handel i egne aksjer» — som
FR-502 filtrerer bort, 35 av 121 meldinger — fra oppstarten av et nytt program,
som er ekte nyhet. Det er nøyaktig skillet **åpent punkt 8** handler om, og
EODHDs taksonomi kan ikke uttrykke det. **FR-502s bøtter kan ikke utledes av
den**, og måtte bygges om fra grunnen.

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
