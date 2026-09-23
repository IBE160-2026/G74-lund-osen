# Rettingsplan etter kontrollen 22.09.2026

**Ingenting er skrevet til kildefilene.** Dette er forslag, til lesning sammen
med `kontroll-2026-09-22.md`. Rekkefølgen er prioritert, ikke kronologisk.

Nederst står **fire funn jeg er uenig i eller vil justere diagnosen på.**

---

## 1. A1 — `tags`-argumentet i `malinger.md` §10

Bygget opp på nytt fra rådataene, ikke omformulert.

### Hva taggene faktisk er

Alle ti artiklene, lest på nytt:

| # | `tags` |
|---|---|
| 1 | `[]` |
| 2 | `SHARE-BUYBACK` |
| 3 | `ACQUISITION, ENERGY, ENGINEERING, M-A, OFFSHORE-WIND` |
| 4 | `BANKS, FINANCIALS, M-A` |
| 5 | `BANKS, EARNINGS, FINANCIALS, RETURN ON EQUITY, SHARE-BUYBACK` |
| 6 | `ENERGY-TRANSITION, GREEN-FINANCING, OFFSHORE-WIND` |
| 7 | `AI, CLOUD-COMPUTING, FINANCIAL-SERVICES, PARTNERSHIP, TECHNOLOGY` |
| 8 | `BANKING, EARNINGS, PRICE-TARGET, RISKS, SHAREHOLDER` |
| 9 | `BANKS, DISCOUNTED CASH FLOW, DIVIDENDS, EARNINGS PER SHARE, INCOME-INVESTING, NET INCOME, NORWEGIAN-MARKET, REVENUE GROWTH, SHARE PRICE, SHAREHOLDER, VALUATION` |
| 10 | `AI, CLOUD-COMPUTING, FINANCIALS, TECH` |

**31 unike tagger over ti artikler. Ni av ti har minst én.**

### Hva som FORTSATT støtter konklusjonen

**Det sterkeste argumentet er nytt, og det er bedre enn det som falt.**

EODHDs tagger er **tematiske**: hva saken handler om. NewsWebs kategorier er
**regulatoriske**: hvilken meldeplikt meldingen oppfyller. FR-502 sorterer på
det siste, og bøttene følger av det:

| NewsWeb-kategori | Bøtte |
|---|---|
| Innsideinformasjon | Slipper gjennom |
| Utsteders meldeplikt ved handel i egne aksjer | **Filtreres bort** (35 av 121) |
| Ikke-informasjonspliktige pressemeldinger | KI avgjør relevans |

En tag som `SHARE-BUYBACK` sier at saken handler om tilbakekjøp. Den sier
**ikke** om det er den ukentlige statusrapporten under meldeplikt — som
filtreres bort — eller oppstarten av et nytt program, som er ekte nyhet. Det er
nøyaktig skillet **åpent punkt 8** handler om, og EODHDs taksonomi kan ikke
uttrykke det.

**FR-502s bøtter kan derfor ikke utledes av EODHDs tagger.** Det er et sterkere
og mer presist argument enn «tags er tom», og det er belagt i data.

De to andre bena står uendret:

- **Rettighetene.** Alle ti artiklene peker til `finance.yahoo.com`, og
  `content` er syndikert utdrag. EODHD er mellomledd, ikke rettighetshaver.
- **Kvoten.** 5 kall per ticker × 15 = 75 i døgnet mot en kvote på 20. Dette
  alene utelukker kilden for drift, uavhengig av alt annet.
- **`issuerSign` finnes ikke**, og 6 av 10 saker er ikke om selskapet. KI-jobben
  ville blitt å avgjøre hvilket selskap saken gjelder — som §4.6 uttrykkelig
  sier den ikke skal ha.

### Hva som IKKE lenger støtter den

| Falt | Hvorfor |
|---|---|
| «`tags` er tom» | Usant. 9 av 10 har tagger |
| «har ingen kategorier» | Usant. Den har 31, av en annen art |
| «**Da har reglene ingen jobb**» | **For sterkt.** Et regelfilter *kunne* bygges på EODHDs tagger. Det ville bare ikke vært FR-502 |
| «FR-604 mister kontrasten» | **Svekket.** Bygges et nytt regelfilter på taggene, finnes det en kontrast igjen. Argumentet holder bare så lenge «regelfilteret» betyr *det eksisterende* |

### Holder konklusjonen?

**Ja — og spørsmålet var stilt slik at den holder klarere enn før.**
Spørsmålet var «kan FR-601..606 skrives om uten at kravene endrer karakter,
eller er det et annet produkt?». Svaret er fortsatt *et annet produkt*: FR-502
måtte bygges om fra grunnen på en fremmed taksonomi, og FR-604s kontrast måtte
defineres på nytt.

**Men påstanden om umulighet faller.** Det jeg skrev, sa i praksis at kilden
ikke *kan* brukes. Det riktige er at den kan brukes til noe annet enn det
PRD-en beskriver — og at rettighetene og kvoten er det som faktisk stenger den
for drift.

**Det endrer ikke hva et nei fra Euronext betyr**, fordi kvoten og
rettighetene er uavhengige av taksonomien. Men det endrer *hvorfor*, og
begrunnelsen står gjengitt to steder.

### Forslag

**Fil:** `malinger.md`, linje 931–941 (§10, «Konklusjon: det er et annet produkt»)

**Dagens tekst:**

> PRD-ens bærende prinsipp er at **«regler sorterer, KI forklarer»**, og
> regelfilteret sorterer på NewsWebs kategoritaksonomi (FR-502, tre bøtter).
> EODHDs nyheter **har ingen kategorier** — `tags` er tom. Da har reglene ingen
> jobb, og FR-604 mister feltet «hva regelfilteret alene gjorde med den» […]

**Foreslått tekst:**

> Regelfilteret sorterer på NewsWebs **regulatoriske** kategoritaksonomi
> (FR-502, tre bøtter): hvilken meldeplikt meldingen oppfyller.
>
> EODHDs nyheter har tagger — 31 unike over ti artikler, 9 av 10 har minst én —
> men de er **tematiske**: `SHARE-BUYBACK`, `EARNINGS`, `M-A`. De sier hva saken
> handler om, ikke hvilken meldeplikt den oppfyller.
>
> Forskjellen er ikke akademisk. `SHARE-BUYBACK` skiller ikke den ukentlige
> statusrapporten under meldeplikt — som FR-502 filtrerer bort, 35 av 121
> meldinger — fra oppstarten av et nytt program, som er ekte nyhet. Det er
> nøyaktig skillet åpent punkt 8 handler om. **FR-502s bøtter kan ikke utledes
> av denne taksonomien**, og måtte bygges om fra grunnen.
>
> *Rettet 2026-09-22 etter kontroll.* Paragrafen sa opprinnelig at `tags` er tom
> og at reglene derfor ikke har noen jobb. Det var feil: kontrollen så på
> artikkel 1, som er den ene av ti uten tagger. §7.2 i denne filen sier det
> riktige. Konklusjonen står, men på et annet og bedre grunnlag — og påstanden
> om at kilden ikke *kan* brukes, er for sterk. Det som stenger den for drift,
> er rettighetene og kvoten.

**Fil:** `malinger.md`, linje 912–913 (tabellen «Hva kilden faktisk inneholder»)

| | Dagens | Foreslått |
|---|---|---|
| l. 912 | «`tags` er tom» | «`tags` finnes på 9 av 10, 31 unike» |
| l. 913 | «Kategori — **Finnes ikke**» | «Kategori — **tematisk, ikke regulatorisk.** Ingen motsvarighet til NewsWebs meldepliktkategorier» |

**Fil:** `prd.md`, åpent punkt 1

**Dagens tekst** inneholder: «den har ingen kategorier, så regelfilteret mister
jobben sin og FR-604 mister kontrasten den måler KI-bidraget mot».

**Foreslått:** «taksonomien er tematisk og ikke regulatorisk, så FR-502s bøtter
måtte bygges om fra grunnen — se `malinger.md` §10».

---

## 2. De tre restene fra den gamle hentemodellen

### 2a. Suksessmålet «Drift» — `prd.md` linje 973

**Dagens:** terskel «Ingen manuelle steg, ingen stopp ved manglende data»

**Foreslått:** «Hentekommandoen fullfører uten manuelle inngrep underveis, ingen
stopp ved manglende data»

Skillet er at *å starte* hentingen nå er en bevisst handling (FR-401), mens
*gjennomføringen* fortsatt skal være uten inngrep. Målet mister ellers mening.

### 2b. FR-705 — `prd.md` linje 850

**Dagens:** «**Meldinger hentes for alle 15 selskapene hver dag.**»

**Foreslått:** «**Hver henting dekker alle 15 selskapene.**»

Setningen står i et kostnadsregnestykke for KI-laget, og poenget er *omfanget
per henting*, ikke frekvensen. Endringen tar bort frekvensgarantien uten å røre
regnestykket.

### 2c. FR-408 «automatisk» — `prd.md` linje 579, og AD-17

Dette er det vanskeligste, og jeg foreslår **ikke** en tekstendring før dere har
avgjort noe.

**Dagens:** «Lagringen skjer automatisk, fra første kjøring.»

**To lesninger, og de gir forskjellige svar:**

| Lesning | Betyr | Forhold til FR-401 |
|---|---|---|
| Automatisk **i tid** | Systemet skriver hver dag av seg selv | **Motsier FR-401.** Ingenting skjer av seg selv lenger |
| Automatisk **innenfor en kjøring** | Du behøver ikke be om det separat | **Forenlig.** AD-17 oppfyller det |

Den andre lesningen er sannsynligvis det som var ment — setningen fortsetter
«Uten den kan spørsmålet *hva sa løsningen om EQNR for to uker siden?* ikke
besvares», som handler om at lagringen ikke må glemmes, ikke om klokkeslett.

**Men det er deres avgjørelse, ikke min.**

### Holder AD-17s konklusjon når begrunnelsen faller?

AD-17 forkastet «egen tredje kommando» med to grunner: *den kan glemmes*, og
*kravet sier automatisk*. Den andre hviler på FR-408s ordlyd.

**Konklusjonen holder — men ikke på den grunnen, og ikke uten en ny svakhet.**

- «Den kan glemmes» står uavhengig av FR-408 og er fortsatt gyldig.
- Den positive begrunnelsen — én utløser, ett tidspunkt, vurderingen skrevet før
  noen ser på siden — er uavhengig av ordlyden.

**Men kontrollen fant en svakhet i AD-17 som jeg ikke så da jeg skrev den:**
AD-17 forkastet lat skriving fordi «en dag ingen åpner siden, blir aldri
lagret». Det argumentet **rammer AD-17s egen løsning like hardt** — en dag ingen
kjører hentekommandoen, blir heller aldri lagret. Forskjellen er hvem som må
huske, ikke om noe kan glemmes.

Og `AD-7`s skjerping gjør det verre: `skriv` avviser enhver dato som ikke er
inneværende børsdag, så **dagene som ble hoppet over kan ikke etterfylles** —
mens FR-403 forutsetter nettopp dager uten kjøring.

**Forslag: AD-17 tas opp igjen som beslutning.** Ikke fordi den er gal, men
fordi den ene begrunnelsen faller, den andre viser seg å ramme begge veier, og
`AD-7` + `FR-403` åpner et hull ingen av alternativene var vurdert mot. Jeg
skriver ikke om begrunnelsen for å redde konklusjonen.

---

## 3. A2, A3, A12 — dokumenter i utakt med seg selv

### 3a. Spinen `AD-13` — linje 179

**Dagens:** «**Uprøvd:** `VOLATILITET_VINDU=20` og `VOLUM_VINDU=20` er merket
`[FORELØPIG]` og er **ikke** målt.»

**Foreslått:** «**Målt 2026-09-22** mot 2 985 aksjedager, `malinger.md` §9.
Begge låst på 20. Alt mellom 15 og 30 oppfører seg tilnærmet likt; begrunnelsen
er at 20 ligger klar av det ustabile området under 15.»

### 3b. Spinen `Deferred` — linje 344 og 348

| Rad | Handling |
|---|---|
| «FR-401 må skrives om» | **Fjernes.** Omskrivingen er gjort samme dag |
| «De to `[FORELØPIG]`-vinduene» | **Fjernes.** Målt samme dag |

### 3c. Spinen `AD-10` — linje 158

**Dagens:** `- **Binds:** FR-401 *(konflikt — se Deferred)*`

**Foreslått:** `- **Binds:** FR-401, FR-408`

Konflikten er løst, og FR-408 hører med siden AD-17 skriver vurderingen i samme
kjøring.

### 3d. PRD §8 — punkt 17 og 18

Begge står under «Må avgjøres før arbeidet går videre», mens frontmatteren sier
«INNFRIDD 2026-09-22T16:07» og `status: final` hviler på dem.

**Foreslått:** flyttes til en ny gruppe **«Lukket»**, hver med hva som lukket
dem — punkt 17 med SQLite-beslutningen *og* svaret fra assisterende
hjelpelærer 22.09, som i dag ikke er nevnt i punktet i det hele tatt. Punkt **7**
og **14** hører samme vei.

### 3e. PRD §8 — de tre usanne oppsummeringene

| Dagens | Foreslått |
|---|---|
| «Punkt 1 har fått eier. De øvrige har det ennå ikke» | «Punkt 1, 4, 5, 5b, 16, 17, 18 og 19 har eier. Punkt 2, 3 og 6–15 mangler» |
| «Punkter som fortsatt står tomme, har ingen av delene» | «Punkt 6–15 har frist, men mangler eier» |
| «Punkt 1 er fortsatt det eneste som kan velte datagrunnlaget» | «Punkt 1 og 19 er de to som kan velte datagrunnlaget» |

---

## 4. Punktnummeret 16 mot 3

Feilen står **fire steder**, og opphavet er de to kodekommentarene.

| Fil | Linje | Dagens | Foreslått |
|---|---|---|---|
| `src/aksjedetalj.py` | 8 | «som ligger bak aapent punkt 1 og punkt 16.» | «som ligger bak aapent punkt 1, 3 og 12.» |
| `src/app.py` | 52 | «krever kilder som ligger bak aapent punkt 1 og punkt 16.» | «krever kilder som ligger bak aapent punkt 1, 3 og 12.» |
| `epics.md` | Epic 7 | «Åpent punkt 1 og 16» | «Åpent punkt 1, 3 og 12» |
| `ARCHITECTURE-SPINE.md` | 350 | «bak åpent punkt 1 og 16» | «bak åpent punkt 1, 3 og 12» |

Punkt **3** er kilden for handelskalenderen, punkt **12** er horisont og
hendelsestyper i FR-302. Punkt **16** er språkgjenkjenningen for Vår Energi og
hører til FR-501.

---

## 5. F8 og F4 — rettelser i refleksjonsmaterialet

### 5a. F8 — «null treff på forbeholdstekst»

**Fil:** `epics.md`, NFR-dekningskartet, NFR-06

**Dagens:** «Søk i `src/templates/` og `src/*.py` ga null treff på
forbeholdstekst — men kravet ber ikke om en tekst.»

**Foreslått:** «`src/templates/index.html:108` sier *«Signalstyrken er 0–3 og
sier hvor kraftig de tre sjekkene slår ut — ikke om aksjen bør kjøpes eller
selges»*. Kravet er likevel et forbud, ikke et tekstkrav: ingen del av
grensesnittet skal formuleres som anbefaling. **Kontroll på hver visningsstory:**
ordlyden leses mot NFR-06.»

Og i `docs/reflection-log.md`, 22.09-oppføringen: at søket lette etter fire
ordformer og at ingen av dem står der — et tomt søk beviser at ordene ikke er
der, ikke at saken ikke er der.

### 5b. F4 — commit-referansene i `epics.md`

**Dagens tabell** fører 12 FR-er på fire commits. Fem av henvisningene er gale.

| FR | Dagens | Foreslått |
|---|---|---|
| FR-103 | `706720f` | Den senere commiten som fjernet «Opp»/«Ned». **`706720f` inneholdt bruddet**, ikke oppfyllelsen |
| FR-706 | `signalberegning.py` / `01af1a5` | `aksjedetalj.py` (`076bb12`) + `aksje.html` |
| FR-202, FR-204 | `076bb12` / `b6ba9d8` | Samme, **pluss `app.py` og `src/templates/`** |

Og en merknad i tabellen: den er skrevet fra kjernemodulene og nevner ikke
`app.py` eller `src/templates/`, selv om de bærer halvparten av fem krav.

I refleksjonsloggen hører F4 hjemme som eget punkt: **det er mulig å føre et
krav på commiten som brøt det**, hvis man leser filnavnet og ikke diffen.

---

## Funn jeg er uenig i, eller vil justere diagnosen på

Disse står som uenighet. De er ikke rettet bort og ikke godtatt i stillhet.

### U1. «17,5 % motsier tabellen» — diagnosen er feil, funnet står

Lens 4 skriver at 17,5 % er en regnefeil: «518/2 985 = 17,353 % → **17,4 %**,
som tabellen rett over selv oppgir».

**17,5 % er ikke feilregnet.** Det er den faktiske verdien ved vindu **60**.
Tabellen hopper fra 50 til 65 og viser aldri 60. Så brødteksten siterer en rad
som ikke er med, ikke et galt tall.

Funnet står — teksten og tabellen spriker — men rettingen er en annen: **enten
tas raden for 60 inn i tabellen, eller så siteres 17,4 %.** Jeg foreslår det
første, siden 60 er toppunktet og det er poenget setningen gjør.

### U2. «Uoppfulgt renummerering» — usannsynlig forklaring

Lens 2 antyder at punkt 16 kan skyldes en renummerering som ikke ble fulgt opp.

PRD-en sier uttrykkelig at numrene følger opprettelsesrekkefølge og **aldri**
renummereres, nettopp for at kryssreferanser skal holde. Forklaringen er
enklere: tallet var galt da kodekommentaren ble skrevet 21.09. Det betyr noe for
rettingen — det er ikke et system som er ute av sync, det er ett tall å rette
fire steder.

### U3. «AD-13 og AD-15 er ikke tildelt en epic» — riktig, men ikke en mangel

Lens 2 fører dem som uklare. Begge er **allerede oppfylt i kode**: parametrene
er konstanter med måling ved siden av seg, og `hent_universet` fortsetter ved
feil.

De burde merkes «oppfylt» som de fire andre — men de mangler ikke en epic, de
mangler et merke. Jeg vil ikke ha dem tildelt arbeid som ikke finnes.

### U4. Lens 3s «18 FEIL» er overtelt

Flere av dem er samme funn sett fra to kanter — FR-401-konflikten telles både
som spine-Deferred og som AD-10-binds, og «punkt 17/18 står som åpent» telles
per punkt. Det endrer ingen konklusjon, men tallet 18 gir et strengere inntrykk
enn substansen bærer. Jeg vil anslå **12–13 distinkte feil** i lens 3s område.

---

### Avgjort 2026-09-23

| | Avgjørelse | Utført |
|---|---|---|
| **U1** | Økta følges: rad 60 blir stående. Men da stemmer ikke «monoton». Regnet for hvert vindu 5–65 er ingen av kurvene monoton, og fallet 60→65 er 3 aksjedager, mindre enn svingningen mellom nabovinduer. Funn 1 i §9 er skrevet om | `94fd482` |
| **U2** | Lukket. Konklusjonen står, men begrunnelsen var upresis: punktene *ble* renummerert 20.09, og regelen mot renummerering kom først 21.09. Det som avgjør, er at kommentaren ble skrevet en time etter at punkt 16 fantes | `3c78c8a` |
| **U3** | Økta følges, med oppslag først. Hvert ledd i AD-13 og AD-15 er slått opp i koden og ført til commiten som innførte det. Begge holder og er merket oppfylt | `5a056fd` |
| **U4** | Talt, ikke anslått. **Diagnosen i U4 over var feil:** lens 3 har 18 distinkte funn, og dobbelttellingen ligger mellom lensene. 31 distinkte i alt, ikke 35 | `027866a` |

## Rekkefølge jeg foreslår i morgen

1. **A1** — den er den eneste som rører en konklusjon, og den er gjengitt to steder
2. **2c / AD-17** — krever en beslutning, ikke en retting
3. **2a, 2b** — to setninger
4. **3a–3e** — mekanisk, ingen vurdering
5. **4** — ett tall, fire steder
6. **5a, 5b** — refleksjonsmaterialet, ingen hast

Punkt 2c er det eneste som ikke kan gjøres med en tekstendring.
