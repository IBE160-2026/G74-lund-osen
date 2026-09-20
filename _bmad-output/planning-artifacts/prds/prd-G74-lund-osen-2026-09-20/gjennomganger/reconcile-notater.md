# Avstemming: `prd-notater.md` mot PRD og `malinger.md`

**Dato:** 2026-09-20
**Kilde:** `_bmad-output/planning-artifacts/prd-notater.md`
**Kontrollert mot:** `prd.md` og `malinger.md` i denne mappa, med oppslag i
`korreksjon-til-brief.md` og `docs/kilder-og-rettigheter.md` der PRD-en henviser dit.

Notatene ble skrevet for å bære teknisk stoff fra Product Brief inn i PRD-en.
Kontrollen er derfor gjort avsnitt for avsnitt i notatene: for hvert krav, tall,
forbehold og beslutning er det slått opp om det gjenfinnes i PRD-en, i vedlegget,
eller i et dokument PRD-en eksplisitt henviser til.

**Resultat i korthet:** 6 punkter fra notatene er borte eller bare delvis båret
over, 7 motsetninger eller kryssreferansefeil er funnet, og ett av de to åpne
spørsmålene nederst i notatene er bare halvveis lukket.

---

## Status 2026-09-20 — avstemmingen er lukket, notatfila er slettet

Alle seks punktene under er kontrollert på nytt mot `prd.md`, `begrunnelser.md`,
`malinger.md` og `docs/kilder-og-rettigheter.md` slik de står etter
korreksjonsrunden. Resultatet:

| # | Punkt | Status |
|---|---|---|
| 1.1 | Alpha Vantage-beslutningen | Lukket ved henvisning. Beslutningen med begrunnelse står i `docs/kilder-og-rettigheter.md`; PRD §6 sier nå eksplisitt at forkastede kilder ligger der, og punkt 9 i §8 fører vilkårskontrollen |
| 1.2 | Bulk-endepunktet, 100 kall flatt | Skrevet inn i NFR-01 som begrunnelsen for ett kall per symbol, og gjentatt i `begrunnelser.md` |
| 1.3 | EODHDs nyhets-API som kilde for relevanseksperimentet | Lukket i `begrunnelser.md` §7, som navngir API-et, fører 5–10 kall per ticker, anslaget på ~80 kall fra bonuskvoten, og som løser opp motsetningen i 2.4: «for dyrt» gjaldt daglig drift. `malinger.md` §0 navngir samme kilde, og kildetabellen i `prd.md` §6 har fått en fjerde rad for API-et |
| 1.4 | Signalstyrke for hele universet | Dekket i substans: FR-101 krever signalstyrke for alle 15 i markedsoversikten, og NFR-01 fører daglig drift som 15 kall — beregningen koster ingen kvote |
| 1.5 | Regelanalysen styrer hvor KI-laget arbeider | Bortfalt ved beslutning, ikke ved forglemmelse. FR-705 sier nå at terskelen styrer visning og sortering, ikke hentingen, og at meldinger hentes for alle 15 hver dag. Begrunnelsen står i `begrunnelser.md`: begrensningen manglet grunnlag siden NewsWeb er gratis, og motsa FR-404 og FR-203 |
| 1.6 | Behovsstyrt henting for aksjer uten utslag | Bortfalt av samme grunn. Når alle 15 hentes daglig, finnes ikke tilfellet kravet skulle dekke |

Punkt 1.5 og 1.6 er grunnen til at `prd-notater.md` ikke kunne bli stående:
notatene sier at nyheter bare hentes for selskaper med utslag, PRD-en sier det
motsatte. Fila er slettet 2026-09-20 etter denne kontrollen. Innholdet finnes i
git-historikken og i dokumentene tabellen peker på.

Resten under 1.3 er lukket 2026-09-20. Spriket mellom «ett ticker per kall» og
«5–10 kall per forespørsel» var vår egen lesefeil i begge retninger:
dokumentasjonen sier 5 kall per forespørsel pluss 5 kall per ticker, altså 10
for én ticker. Rettet i `prd.md` §6 og `begrunnelser.md` §7, med sitat og dato i
`docs/kilder-og-rettigheter.md`.

---

## 1. Borte fra PRD-en

### 1.1 Alpha Vantage-beslutningen (notat linje 13–14)

> «Alpha Vantage ble testet som alternativ, men Oslo Børs-symbolene var ikke
> pålitelige nok til å være hovedkilde.»

Ordet «Alpha Vantage» finnes ikke i `prd.md` og ikke i `malinger.md`.
Kildetabellen i PRD §6 lister bare de tre kildene som brukes; den har ingen rad
eller linje for kilder som er vurdert og forkastet. Begrunnelsen — upålitelige
Oslo Børs-symboler — er dermed ikke i PRD-en.

Beslutningen finnes i `docs/kilder-og-rettigheter.md` linje 26, som PRD §6
henviser til. Den er altså ikke tapt for prosjektet, men den er ikke i PRD-en,
og PRD-en signaliserer ikke at den finnes.

**Dette er andre gang detaljen faller ut.** `korreksjon-til-brief.md` fører den
som berget detalj nr. 2 i commit `270026d` — berget fra utkastmappa inn i
notatene, og nå ikke videre inn i PRD-en. Nøyaktig mønsteret som samme dokument
beskriver i avsnittet «Mønsteret: seks detaljer berget fra utkastmappa».

**Forslag:** én linje i §6, under kildetabellen: Alpha Vantage ble testet mot
Oslo Børs og forkastet som hovedkilde fordi symbolene ikke var pålitelige nok.

### 1.2 Bulk-endepunktet koster 100 kall flatt (notat linje 21)

> «Bulk-endepunktet koster 100 kall flatt og er ubrukelig på gratisnivå.»

Hverken «bulk» eller tallet 100 finnes i `prd.md`, i `malinger.md` §2 (tabellen
«EODHD — kvote og oppførsel»), eller i `docs/kilder-og-rettigheter.md`.
**Dette punktet er helt tapt — det finnes nå bare i notatene.**

Det er ikke en kuriositet. Det er belegget for at ett kall per symbol er den
eneste farbare veien på gratisnivå. Uten det står NFR-01 («15 kall, fem kalls
margin») og hele utledningen av universstørrelsen på 15 aksjer uten svar på det
nærliggende motspørsmålet: *hvorfor ikke hente alle symbolene i ett bulk-kall?*
En sensor eller en arkitekt vil stille det spørsmålet.

**Forslag:** én rad i `malinger.md` §2: «Bulk-endepunkt | 100 kall flatt —
ubrukelig på et gratisnivå med 20 kall i døgnet», og en henvisning fra NFR-01.

### 1.3 EODHDs nyhets-API som kilde for relevanseksperimentet (notat linje 22–23)

> «EODHDs nyhets-API tar ett ticker per kall og brukes bare til
> relevanseksperimentet, som bruker restkvoten én gang og ikke inngår i den
> daglige driften.»

Konsekvensen er båret over — NFR-01 sier «Relevanseksperimentet bruker restkvoten
én gang og inngår ikke i daglig drift», og `malinger.md` §6 fører «Restkvoten én
gang, uke 41». **Men kilden er borte.** PRD-en sier ingen steder hvilket API
eksperimentet henter fra, og heller ikke at det koster ett kall per ticker.

Følgen er at suksessmålet «Relevanseksperiment — testsett på 50 medieartikler»
(§7) og det åpne punktet om uke 41 ikke har noen navngitt datakilde i PRD-en.
Kildetabellen i §6 har tre rader; EODHDs nyhets-API er ikke en av dem, selv om
PRD-en planlegger å bruke det. Se også motsetning 2.4.

**Forslag:** en fjerde rad i §6-tabellen: «EODHD `/api/news` | Relevanseksperimentet
(én gang, uke 41) | 1 kall per ticker, restkvoten».

### 1.4 At signalstyrke beregnes for hele universet lokalt (notat linje 32–33)

> «signalstyrke beregnes for hele universet lokalt»

PRD §4.4 beskriver *hvordan* signalet regnes (FR-701–705), men sier ingen steder
at beregningen kjøres for alle 15 uansett, og ikke at den er lokal og dermed
gratis i kvotesammenheng. Det er den halvdelen av arbeidsdelingen som forklarer
hvorfor markedsoversikten kan vise signalstyrke for alle 15 aksjer hver dag,
mens KI-laget bare rører noen få.

### 1.5 At den regelbaserte analysen styrer hvor KI-laget arbeider (notat linje 32–36)

Dette er hovedprinsippet i notatenes avsnitt om henting, og det er **ikke ført
opp som krav noe sted.** Det finnes bare som en bisetning i FR-705:

> «Terskelen har en driftskonsekvens utover visningen: nyheter hentes og
> KI-vurderes bare for selskapene som skiller seg ut **(se 4.1)**.»

**Kryssreferansen peker på ingenting.** Seksjon 4.1 er FR-401 til FR-407, og
ingen av dem sier noe om selektiv nyhetshenting. FR-401 sier tvert imot
«kurser først, deretter meldinger», uten forbehold om hvilke selskaper.

Prinsippet som skulle styre hele kostnadsprofilen i løsningen ligger altså som
en parentes i et terskelkrav, med en henvisning til et sted der kravet ikke står.

Begrunnelsens andre halvdel er også borte: notatene sier at ordningen «retter
vurderingene mot de aksjene brukeren faktisk skal lese om». PRD-en beholder bare
kostnadsargumentet.

**Forslag:** eget krav i 4.1 — f.eks. FR-408, «Selektiv nyhetshenting»:
signalstyrke beregnes lokalt for hele universet ved hver henting; nyheter hentes
og KI-vurderes bare for selskaper over terskelen i FR-705. Da får FR-705 noe å
henvise til.

### 1.6 Behovsstyrt nyhetshenting for aksjer uten utslag (notat linje 34–35)

> «Åpner brukeren en aksje uten utslag, hentes nyhetene for den ved behov og
> lagres ut dagen.»

**Helt borte fra PRD-en.** Uttrykket «ved behov» finnes ikke i dokumentet.
FR-401 dekker bare oppstartsutløst henting. FR-203 («Øvrig innhold» i
aksjedetaljen) lister «Børsmeldinger som passerte filteret» uten å si hva som
skjer når meldingene for den aksjen aldri ble hentet. NFR-02 («Brukeren venter
aldri på en henting») er skrevet for bakgrunnshentingen, ikke for et oppslag
brukeren selv utløser.

Dette er en reell funksjonell luke, ikke en formulering som mangler. Slik PRD-en
står nå, er dette den definerte oppførselen: en aksje med signalstyrke 0 eller 1
har ingen meldinger å vise i aksjedetaljen, fordi de aldri ble hentet. Det er
stikk i strid med notatene, og trolig i strid med hva gruppen mener.

Lagringsregelen «lagres ut dagen» mangler også. FR-406 definerer to lagre
(beregningsgrunnlag og rådata) med hvert sitt ansvar; en dagsfersk
meldingsbuffer for behovshentede aksjer passer i ingen av dem, og trenger enten
en tredje rad eller en eksplisitt plassering.

**Forslag:** ta med i samme nye krav som 1.5: åpnes en aksje under terskelen,
hentes meldingene for den ved behov og bufres ut kalenderdøgnet. Presiser
forholdet til NFR-02 — venter brukeren her, eller vises aksjedetaljen tomt med
tidsstempel mens hentingen går?

---

## 2. Motsetninger og kryssreferansefeil

### 2.1 FR-705 viser til 4.1, som ikke har kravet

Se 1.5. Dette er både et manglende krav og en død kryssreferanse.

### 2.2 Selektiv henting mot etterfylling — hvilken regel gjelder?

FR-404 og FR-405 beskriver etterfylling av meldinger over hele hullet, med
deling av intervaller til `overflow: false` — en operasjon som henter alle
meldinger i perioden. Notatenes prinsipp henter bare for selskaper med utslag.
PRD-en avstemmer aldri de to.

Etter en uke uten bruk: skal etterfyllingen hente meldinger for alle 15 (som
FR-404 leser), eller bare for de som hadde utslag på hver av de dagene (som
prinsippet tilsier — men da må signalet regnes per dag bakover først)?
Uavklart, og det er et implementasjonsvalg noen må ta.

Merk at NewsWeb ikke koster kvote, så selektiv henting har ingen
kvotebegrunnelse for meldinger — bare en KI-kostnadsbegrunnelse. Det er verdt å
si eksplisitt, for ellers ser selektiviteten ut som en kvotebesparelse den ikke er.

### 2.3 «26 kalenderdager» stemmer ikke med datointervallet

PRD §4.2, `malinger.md` §4 og `korreksjon-til-brief.md` oppgir alle
«2026-08-22 til 2026-09-18, 26 kalenderdager».

Intervallet er **28 dager** (22.–31. august = 10, 1.–18. september = 18).
`malinger.md` §4 sier selv «sju biter à fire døgn», altså 7 × 4 = 28 — som
bekrefter at 28 er riktig og at 26 er feilen.

Konsekvensen er at alle per-dag-tallene er ca. 7 % for høye:

| Steg | PRD i dag (÷26) | Riktig (÷28) |
|---|---:|---:|
| Hentet fra NewsWeb, 121 | 4,7 per dag | 4,3 per dag |
| Etter deduplisering, 89 | 3,4 per dag | 3,2 per dag |
| Til KI-forklaring, ~35 | ~1,3 per dag | ~1,25 per dag |

Konklusjonen («noen få meldinger om dagen, ikke titalls») står uendret, så dette
velter ingenting — men tallet 4,7 står tre steder og er lett å kontrollere for
en sensor.

### 2.4 Nyhets-API-et er «forkastet» i én kilde og planlagt brukt i en annen

`docs/kilder-og-rettigheter.md` linje 20 fører EODHD `/api/news` som
«— (forkastet)», med begrunnelsen «Ett ticker per kall, 5–10 kall per forespørsel.
For dyrt.»

Notatene og PRD-en planlegger samtidig et relevanseksperiment i uke 41 som
bruker nettopp dette API-et. Ingen av dokumentene sier «forkastet for daglig
drift, men brukt én gang til eksperimentet» — som er det som faktisk gjelder.

I tillegg spriker kostnadsangivelsene: notatene sier «ett ticker per kall»,
kilde-dokumentet sier «ett ticker per kall, 5–10 kall per forespørsel». Det er
to forskjellige tall for samme ting, og ingen av dem er ført inn i PRD-en.

### 2.5 `malinger.md` henviser til feil åpent punkt

`malinger.md` linje 160, om tilbakekjøpskategorien: «Ført som åpent punkt 5 i
PRD-en.»

I PRD §8 er tilbakekjøp **punkt 4**. Punkt 5 er skjevfordelingen mot positiv
retning. Rett nummeret, eller — bedre — henvis til FR-502 i stedet for til et
listenummer som flytter seg hver gang lista endres.

### 2.6 FR-405, siste avsnitt: sikkerhetssjekken er logisk feil skrevet

> «returneres meldinger som er nyere enn `fromDate` selv om `overflow` er
> `false`, behandles også det som en ufullstendig henting.»

Alle meldinger i et svar er per definisjon nyere enn `fromDate` — det er
intervallets startpunkt. Slik regelen står, slår den enten alltid ut eller aldri.

Det som er ment, følger av `malinger.md` §3: API-et returnerer de **nyeste** og
forkaster resten. Avkorting viser seg derfor ved at den **eldste** meldingen i
svaret er nyere enn `fromDate` — altså at starten av intervallet ikke er dekket.

**Forslag til ordlyd:** «er den eldste meldingen i svaret vesentlig nyere enn
`fromDate`, behandles hentingen som ufullstendig selv om `overflow` er `false`.»
(«Vesentlig» fordi et intervall som starter i en helg lovlig kan mangle de første
døgnene — jf. at meldinger følger kalenderdøgn, men at ikke alle døgn har meldinger.)

### 2.7 Dato for kvotemålingene spriker

Notatene: «Målte kalltall 19.09.2026». `kilder-og-rettigheter.md`: 2026-09-19.
`malinger.md`: «Alle målinger er gjort 2026-09-20», og §2 «Hentet fra EODHDs
dokumentasjon 2026-09-20». PRD-en oppgir ingen dato for kvotetallene.

Sannsynligvis to forskjellige målinger på to dager, men slik det står ser det ut
som én måling med to datoer. Presiser i `malinger.md` §2 hvilke tall som er fra
19.09 og hvilke fra 20.09.

---

## 3. De to åpne spørsmålene nederst i notatene

### 3.1 «Hvilke 15 aksjer, og etter hvilke kriterier» — LUKKET

Fullt besvart i PRD §3: to kriterier (median daglig omsetning over 25 MNOK målt
over tre måneder, og minst åtte sektorer i lista som helhet), navngitt liste med
15 symboler, og måling med metode og rådatareferanse i `malinger.md` §1.
PRD-en fører også hvorfor omsetning måles i kroner og ikke i volum, med DNO og
MPCC som belegg. Ingenting mangler her.

### 3.2 «Kategorihvitliste eller KI-terskel» — BARE HALVVEIS LUKKET

Forutsetningen er innfridd: gruppen har sett på fire ukers meldinger
(`malinger.md` §4), og **valget mellom hvitliste og terskel er tatt** — FR-502
er en kategorihvitliste i tre bøtter, med antall per kategori og begrunnelse for
hver grensesak (flagging inn, primærinnsidere inn, tilbakekjøpsstatus ut).

**Men KI-terskelen mangler.** For den ene bøtta der KI avgjør — de 18 meldingene
i samlekategorien — sier PRD-en bare «KI avgjør relevans». Den sier ikke hva som
skal til for at en melding regnes som relevant: en binær klassifisering? En
score med en grense? Hvem setter grensen, og mot hva kalibreres den?

Tallet «~13 til KI-relevansvurdering» i resultattabellen er volum *inn* i
vurderingen, ikke hvor mange som kommer ut. Hvor mange som til slutt «passerer
filteret» — som var det spørsmålet faktisk spurte om — er dermed fortsatt ubesvart.

Verre: **punktet står ikke i §8 Åpne punkter.** De åtte punktene der dekker
vilkårskontroll, usikkerhetskriterier, parameterlåsing, tilbakekjøpsoppstart,
skjevfordeling, primærinnsidere, briefkorreksjoner og innleveringsdato — ingen
av dem er KI-terskelen. Spørsmålet har altså ikke blitt lukket; det har falt ut.

**Forslag:** nytt åpent punkt i §8, knyttet til FR-502, med frist før KI-laget
implementeres — samme frist som punkt 2, siden de to henger sammen: hvordan
relevans avgjøres, og hvordan usikkerhet i den avgjørelsen måles.

---

## 4. Kontrollert og funnet dekket

Til dokumentasjon av at gjennomgangen er gjort avsnitt for avsnitt:

| Fra notatene | Status i PRD-en |
|---|---|
| Kursdata og OSEBX fra EODHD | Dekket. OSEBX bevisst ut av v1, og avviket fra notatene er **eksplisitt forklart** i NFR-01 og i §2 «hvis vi rekker» |
| Børsmeldinger fra NewsWeb, tagget med utsteder og kategori | Dekket — `issuerSign` i §4.3, kategorifeltet i FR-502 |
| Euronext finanskalender for kommende hendelser | Dekket — §2, FR-203, §6 |
| **Kalenderen mangler ticker og ISIN, krever oppslagstabell** | **Dekket** — PRD §6, linje 744–745, båret ordrett over. Men bare som prosa i kildeseksjonen: den har ikke FR-nummer, FR-203 henviser ikke til den, og §8 har ingen eier eller frist for å sette opp tabellen |
| ~15 aksjer utledet av kvoten, ikke skjønn | Dekket — §3 og NFR-01 |
| NewsWeb og Euronext koster ingen kall | Dekket — §3, §6 |
| Henting som bakgrunnsoppgave, ikke ved sidevisning | Dekket — FR-401, NFR-02 |
| Eldre enn siste børsslutt → kurser først, så meldinger | Dekket — FR-401 |
| Siste kjente data med tidsstempel mens henting pågår | Dekket — FR-401, NFR-02, NFR-03 |
| Rådata lagres fra første kjøring | Dekket — FR-406, NFR-07 |
| NewsWeb er udokumentert backend, reell risiko | Dekket — FR-406, NFR-07, åpent punkt i §6 |
| Merking av utbyttedager, før demonstrasjonen | Dekket — FR-407 ordrett, forsterket med FR-101 og FR-503 (eks.dato som datakilde) |
| Historiske sammenligninger på utbyttejusterte kurser | Dekket — FR-701 |
| Grovsortering i kode, KI på det som passerer | Dekket — FR-502, §4.3 |
| Grensen går ved samlekategorien for ikke-regulatoriske pressemeldinger | Dekket, og **styrket**: notatenes ene eksempel (kontrakt mot sponsorat) er i PRD-en blitt tre uavhengige målinger |
| Usikkerhet av observerbare kjennetegn, ikke selvrapportert score | Dekket — FR-603, alle tre kriteriene |
| Testen 17.09: finansselskap der flertallet av treffene gjaldt andre | Dekket — §4.3 punkt 1, og som åpent punkt 2 om at kriteriene er skrevet for medieartikler |

---

## 5. Prioritert liste

| # | Sak | Type | Hastegrad |
|---|---|---|---|
| 1 | Behovsstyrt nyhetshenting for aksjer uten utslag, lagret ut dagen (1.6) | Manglende krav | Høy — funksjonell luke |
| 2 | Prinsippet om at regelanalysen styrer KI-laget mangler i 4.1; FR-705 henviser til ingenting (1.5, 2.1) | Manglende krav | Høy |
| 3 | KI-terskelen er ikke avgjort og ikke ført som åpent punkt (3.2) | Åpent spørsmål falt ut | Høy — før KI-laget bygges |
| 4 | FR-405 sikkerhetssjekk er logisk feil skrevet (2.6) | Feil i krav | Middels — implementeres snart |
| 5 | Bulk-endepunktet, 100 kall flatt (1.2) | Tapt måling | Middels |
| 6 | EODHDs nyhets-API mangler som navngitt kilde; «forkastet» mot planlagt bruk (1.3, 2.4) | Manglende kilde + motsetning | Middels |
| 7 | 26 mot 28 kalenderdager, og alle per-dag-tall (2.3) | Regnefeil i tre dokumenter | Middels |
| 8 | Alpha Vantage-beslutningen (1.1) | Tapt beslutning | Lav — finnes i kildedokumentet |
| 9 | Signalstyrke beregnes lokalt for hele universet (1.4) | Manglende presisering | Lav |
| 10 | Feil nummer på åpent punkt i `malinger.md` (2.5), datospriket (2.7) | Kryssreferanse | Lav |

---

## 6. Observasjon om arbeidsmåten

`korreksjon-til-brief.md` avslutter med tiltaket: *«Etter hver omskriving av et
dokument: kjør en diff mot forrige versjon og se spesifikt etter krav som er
borte.»*

Denne avstemmingen er det samme tiltaket brukt på neste ledd i kjeden — notat til
PRD — og den fant seks nye tilfeller. Alpha Vantage-beslutningen (1.1) er den
samme detaljen som allerede ble berget én gang, i `270026d`, og som nå falt ut
igjen i neste omskriving.

Det styrker observasjonen som er ført til refleksjonsrapporten, og skjerper den:
tapet skjer ikke bare i språkvask, men i **hver overføring mellom dokumenter** —
også der overføringen er selve meningen med dokumentet. Notatene ble skrevet
nettopp for å bære dette stoffet videre, og bar likevel ikke alt.
