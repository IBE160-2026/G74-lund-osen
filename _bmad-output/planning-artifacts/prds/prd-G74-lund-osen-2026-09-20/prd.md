---
title: "PRD — OSE Signal"
status: draft
created: 2026-09-20
updated: 2026-09-20
---

# PRD — OSE Signal

**Emne:** IBE160 Programmering med KI, Høgskolen i Molde
**Gruppe:** G74 — Joakim Lund, Marian Osen

Dette dokumentet fastsetter hva OSE Signal skal gjøre i v1. Det er et
kravregister: hvert krav står med sin normative setning og én linje begrunnelse.
Her står kravene og beslutningene som må være låst før arkitekturarbeidet
starter.

**Tilhørende dokumenter.** `begrunnelser.md` bærer resonnementet bak kravene —
hvorfor grensene går der de går. `malinger.md` inneholder alle målinger med
metode og rådatareferanser. `.memlog.md` er beslutningsloggen, og
`gjennomganger/` inneholder avstemmingene mot kildedokumentene.

**Om lengden.** Vi satte ambisjonsnivået til middels — 5–8 sider — og landet på
omtrent 11,7. Avviket er kjent og bevisst. Resonnementet er allerede flyttet ut
til `begrunnelser.md` og målingene til `malinger.md`; det som står igjen er
kravene selv, og 115 av linjene her er tabellrader som *er* krav: kolonnene i
markedsoversikten, de ti kategoriene med bøtte, feltene som skal lagres,
suksessmålene og de åpne punktene. Å komme under 11 sider krever at krav går ut,
ikke at teksten strammes.

---

## 1. Bakgrunn og mål

Den som følger 10–30 norske aksjer ved siden av jobb eller studier, har ikke et
informasjonsproblem, men et sorteringsproblem. Kursene, meldingene og
rapportdatoene finnes, men ligger på ulike steder og i ulikt format, og det
meste er irrelevant akkurat i dag.

OSE Signal samler dette i én oversikt, slik at spørsmålet *hva beveget seg i
går, hvorfor, og er det noe viktig på vei?* kan besvares på omtrent fem minutter
om morgenen.

**Målet med v1** er at en vanlig sparer skal kunne åpne løsningen om morgenen,
se hva som har endret seg, forstå hvorfor noe skiller seg ut, og finne det
viktigste uten å slå opp flere steder.

**Det bærende prinsippet** er at kode og KI holdes fra hverandre: regler
sorterer, KI forklarer, og grensen er synlig i grensesnittet — ikke bare i
koden.

---

## 2. Omfang

### Inne i v1

- Markedsoversikt og aksjedetalj for 15 likvide Oslo Børs-aksjer
- Signalstyrke og retning med synlig begrunnelse
- Børsmeldinger sortert av regler og forklart av KI
- Av/på-bryter for KI-laget, synlig i grensesnittet
- Kommende finansielle hendelser

Løsningen er en **webapplikasjon for PC**. Mobiltilpasning er utenfor v1, og
plattformvalget er dermed låst.

Første versjon er på norsk og kjører lokalt.

### Hvis vi rekker

- Favorittmerking av aksjer, slik at egne aksjer ikke havner tilfeldig i lista
- Flere valgbare tidsperioder i kursgrafen enn de faste seks månedene
- OSEBX som referanseindeks. Koster ett API-kall i døgnet og ville redusert
  marginen fra fem til fire; det er heller ikke kontrollert om indeksdata er
  tilgjengelig på EODHDs gratisnivå

### Utenfor v1

Brukerkontoer, innlogging og personlig portefølje; varsler, betaling,
mobiltilpasning og meglerintegrasjon; flere børser og flere språk;
fundamental- og verdimodell; intradag- og sanntidsdata; statistisk studie av om
signalene slår markedet.

### Utsatte vurderinger

Tre vurderinger er utsatt til løsningen eventuelt publiseres:
**videreformidlingsrett**, **personvern**, og **regelverket som gjelder når en
tjeneste presenterer finansielle signaler**.

**Utløseren er publisering, ikke kommersialisering.** Kildedokumentet krever at
vilkårene vurderes på nytt dersom applikasjonen skal publiseres — også uten at
noen tar betalt. Kodebasen er allerede offentlig i IBE160-organisasjonen;
skillet mellom hva som publiseres og hva som blir liggende lokalt står i
`docs/kilder-og-rettigheter.md`.

---

## 3. Aksjeuniverset

### Kriterium

Et symbol er med i universet når det oppfyller begge kravene:

1. **Median daglig omsetning over 25 MNOK**, målt over siste tre måneder.
   Omsetning regnes som `volume × close` per handelsdag, og medianen tas over
   perioden.
2. **Universet dekker minst åtte sektorer.** Kravet gjelder lista som helhet,
   ikke det enkelte symbolet.

Antallet på 15 er utledet av API-kvoten, ikke valgt etter skjønn: EODHD på
gratisnivå gir 20 kall i døgnet, og kurser koster ett kall per symbol.

Likviditet måles i **kroner, ikke i antall aksjer**. Se `begrunnelser.md` for
hvorfor den opplagte målingen var feil mål.

### Universet

Målt 2026-09-20 over 65 handelsdager. Volumtall, andel av median og metode: se
`malinger.md`, seksjon 1.

| # | Symbol | Selskap | Sektor | Median omsetning |
|---|---|---|---|---:|
| 1 | EQNR | Equinor | Energi | 919,9 MNOK |
| 2 | DNB | DNB Bank | Finans | 400,4 MNOK |
| 3 | KOG | Kongsberg Gruppen | Industri | 374,7 MNOK |
| 4 | AKRBP | Aker BP | Energi | 312,1 MNOK |
| 5 | NHY | Norsk Hydro | Materialer | 293,0 MNOK |
| 6 | FRO | Frontline | Shipping | 284,8 MNOK |
| 7 | VAR | Vår Energi | Energi | 252,9 MNOK |
| 8 | TEL | Telenor | Telekom | 223,9 MNOK |
| 9 | YAR | Yara International | Materialer | 220,5 MNOK |
| 10 | MOWI | Mowi | Sjømat | 182,1 MNOK |
| 11 | ORK | Orkla | Konsum | 140,3 MNOK |
| 12 | SALM | SalMar | Sjømat | 81,8 MNOK |
| 13 | GJF | Gjensidige Forsikring | Finans | 59,8 MNOK |
| 14 | DNO | DNO | Energi | 34,7 MNOK |
| 15 | MPCC | MPC Container Ships | Shipping | 32,3 MNOK |

Median for universet: 223,9 MNOK per dag. Laveste symbol ligger på 32,3 MNOK,
over terskelen på 25 MNOK. Lista dekker åtte sektorer. Begge kriteriene er
oppfylt for hele universet — ingen symboler er tatt inn som unntak.

Hvorfor spennet fra 920 til 32 MNOK er akseptabelt: se `begrunnelser.md`.

---

## 4. Funksjonelle krav

Rekkefølgen følger kravnumrene: grensesnittet først, deretter data og
beregning.

### 4.1 Markedsoversikten

#### FR-101 — Fem kolonner

Markedsoversikten viser de 15 aksjene i universet med nøyaktig fem kolonner:

| Kolonne | Innhold |
|---|---|
| Selskap | Selskapsnavn |
| Sluttkurs | `close` for siste børsdag |
| Endring | Endring i prosent, regnet på `adjusted_close` |
| Signalstyrke | 0–3, jf. FR-703 |
| Retning | Opp, Ned, Blandet eller Ingen, jf. FR-704 |

Sluttkursen vises som `close`, mens prosenten regnes på `adjusted_close`. På
utbyttedager gir det et synlig avvik mellom de to kolonnene, og dagen skal da
merkes etter FR-407.

#### FR-102 — Standard sortering

Sortering er **signalstyrke fallende**, med **absolutt kursendring** som
sekundærkriterium ved lik styrke.

At brukerens egne aksjer havner tilfeldig i lista, er akseptert i v1.
Favorittmerking hører til «hvis vi rekker».

#### FR-103 — Retning vises i tre redundante kanaler

Retningen vises som tekst, symbol og farge samtidig:

| Retning | Visning |
|---|---|
| Positiv | Opp ↑ |
| Negativ | Ned ↓ |
| Blandet | Blandet ↔ |
| Ingen | Ingen utslag |

Alle tre kanalene er obligatoriske. Farge alene utelukker fargeblinde brukere,
og «blandet» lar seg ikke uttrykke lesbart i farge i det hele tatt. Teksten er
den bærende kanalen; symbol og farge er forsterkninger.

#### FR-407 — Merking av utbyttedager

*ID-en er beholdt fra da kravet lå i datahentingen. Det hører hjemme her.*

Markedsoversikten viser `close`, mens endringen i prosent regnes på
`adjusted_close`. Det er riktig — et ordinært utbytte skal ikke se ut som et
kursfall — men på en utbyttedag stemmer ikke differansen mellom to viste
sluttkurser med den viste prosenten. En bruker som regner etter, vil lese det
som en feil.

Utbyttedager skal derfor merkes i grensesnittet, slik at avviket er forklart i
stedet for å se ut som en feil. Kravet må være oppfylt før demonstrasjonen.

---

### 4.2 Aksjedetaljen

#### FR-201 — Kursgraf med seks måneders historikk

Kursgrafen viser seks måneders historikk, fast i v1. Perioden er lang nok til at
50-dagers snittet har kontekst, og kort nok til å være lesbar.

Flere valgbare tidsperioder hører til «hvis vi rekker».

#### FR-202 — MA50-linjen tegnes oppå kursen

Grafen tegner 50-dagers glidende snitt som en linje oppå kursen. Det gjør
**sjekk 1, trend**, direkte synlig.

**Sjekk 2 (bevegelse) og sjekk 3 (interesse) vises bare som tall** i lista over
de tre sjekkene, jf. FR-706. Volatilitetsbånd og volumsøyler tegnes ikke i v1.

#### FR-203 — Øvrig innhold

Aksjedetaljen viser i tillegg:

- De tre sjekkene ved navn med verdien hver av dem ga (FR-706)
- Børsmeldinger som passerte filteret, med lenke til originalen på NewsWeb
- KI-forklaring per melding når KI-laget er på, eller «ikke vurdert» når det er
  av (FR-602)
- Kommende finansielle hendelser fra Euronext

---

### 4.3 Kommende finansielle hendelser

#### FR-301 — Kilde og kobling til selskap

Kommende finansielle hendelser hentes fra Euronexts finanskalender. Kilden
koster ingen EODHD-kvote.

Kalenderen oppgir **verken ticker eller ISIN**. Hendelser må derfor kobles til
selskap via en oppslagstabell som settes opp for aksjeuniverset én gang, og som
vedlikeholdes manuelt hvis universet endres.

#### FR-302 — Hvilke hendelser og hvor langt frem

`[ANTAKELSE]` Aksjedetaljen viser kommende hendelser for selskapet innenfor de
neste `[FORELØPIG] 90` dagene. Hendelsestypene er de kalenderen oppgir — typisk
resultatfremleggelser, generalforsamlinger og utbyttedatoer.

Horisonten og typeutvalget er antatt, ikke besluttet. Begge må bekreftes når
kalenderens faktiske innhold for universet er undersøkt.

#### FR-303 — Når kalenderen ikke svarer

Er kalenderen utilgjengelig eller uten treff for et selskap, vises aksjedetaljen
uten hendelsesseksjonen, ikke med en feilmelding. Manglende hendelser er en
normaltilstand, og skal ikke se ut som en feil.

Dette følger NFR-03.

---

### 4.4 Datahenting og oppdatering

#### FR-401 — Oppstartsutløst henting

Henting utløses når applikasjonen starter, ikke av en planlagt jobb med fast
klokkeslett. Er lagrede data eldre enn siste børsslutt, hentes nye data da —
kurser først, deretter meldinger. Hentingen kjører som bakgrunnsoppgave.
Brukeren venter aldri på den og ser siste kjente data med tidsstempel mens den
pågår.

#### FR-402 — Kontroll mot forventet børsdag, ikke mot klokkeslett

Hentingen skal ikke anta at data er ferske fordi klokka har passert et
tidspunkt. Den skal kontrollere at nyeste `date` i svaret er forventet børsdag.

Er nyeste `date` ikke forventet børsdag, vises siste kjente data med
tidsstempel, og hentingen prøves igjen ved neste oppstart. Applikasjonen skal
aldri presentere gårsdagens tall som dagens.

EODHD dokumenterer ingen publiseringstid for Oslo Børs; se `begrunnelser.md`.

#### FR-403 — Etterfylling av kurser etter dager uten bruk

Åpner ingen applikasjonen på flere dager, oppstår hull i serien. Hullene skal
fylles ved neste oppstart uten ekstra kostnad i kvote.

`/api/eod` tar `from` og `to`, begge inklusive, og **ett kall koster det samme
uansett hvor langt intervallet er**. Etterfylling av 15 symboler koster derfor
15 kall enten hullet er én dag eller fire måneder.

#### FR-404 — Etterfylling av børsmeldinger

Meldinger etterfylles på samme måte som kurser og koster ingen EODHD-kvote.
NewsWeb støtter `fromDate` og `toDate` som et ekte intervall.

Meldinger følger kalenderdøgn, ikke børsdager. Etterfylling skal derfor dekke
alle kalenderdager i hullet, ikke bare børsdagene.

#### FR-405 — Avkorting ved lange meldingsintervaller

NewsWeb har et resultattak på mellom 557 og 601 meldinger per forespørsel. Er
intervallet for langt, returneres de **nyeste** meldingene og resten forkastes —
med HTTP 200 og ingen feilmelding. Ingen av de vanlige parametrene for
paginering eller grense har effekt. Målingene står i `malinger.md`, seksjon 3.

Svaret inneholder derimot feltet `data.overflow`, som er `true` nøyaktig når noe
ble forkastet. Feltet er udokumentert, men oppførselen er verifisert i begge
retninger.

**Kravet:** etter hver meldingshenting skal `data.overflow` kontrolleres. Er den
`true`, er svaret ufullstendig, og intervallet skal deles og hentes på nytt til
hver del kommer tilbake med `overflow: false`. Meldinger skal aldri regnes som
fullstendig hentet uten at flagget er sjekket.

Delingen er gratis i kvotesammenheng, så det er ingen grunn til å presse
intervallene.

Fordi flagget er udokumentert, skal implementasjonen ikke stole på det alene:
er **den eldste meldingen i svaret** nyere enn `fromDate` selv om `overflow` er
`false`, behandles også det som en ufullstendig henting.

Delingen har en nedre grense på ett døgn. Gir ett enkelt døgn fortsatt
`overflow: true`, skal hentingen stoppe og feilen rapporteres i stedet for å
dele videre.

#### FR-406 — To lagre med hvert sitt ansvar

Kursdata lagres i to atskilte lagre som aldri blandes:

| Lager | Innhold | Regel |
|---|---|---|
| **Beregningsgrunnlag** | Serien som signalberegningen leser | Lastes ned i sin helhet **ved hver henting**. Skjøtes aldri på. |
| **Rådata** | Øyeblikksbilder med tidsstempel per henting | Skrives aldri om. Dokumentasjon og sikkerhetsnett, ikke beregningskilde. |

**Merk at dette ikke er et krav om å hente oftere.** En henting utløses bare når
betingelsen i FR-401 er oppfylt. Kravet her gjelder *hva* en henting gjør når
den først skjer: den laster ned hele serien på nytt i stedet for å skjøte nye
rader på en lagret serie. Starter applikasjonen flere ganger samme dag, hentes
ingenting etter første vellykkede henting.

Uten denne presiseringen ville 15 kall gått med ved hver oppstart, og oppstart
nummer to samme dag ville sprengt kvoten på 20.

Rådatalageret svarer på et annet behov, se NFR-07. Hvorfor serien må lastes ned
på nytt: se `begrunnelser.md`.

#### FR-408 — Dagens vurdering lagres per aksje

For hver aksje, hver dag, lagres vurderingen slik den var:

| Felt | Innhold |
|---|---|
| Dato | Børsdagen vurderingen gjelder |
| Signalstyrke | 0–3 |
| Retning | Positiv, negativ, blandet eller ingen |
| De tre sjekkene | Hvilken verdi hver av trend, bevegelse og interesse ga |
| Relevante meldinger | Hvilke meldinger som ble vist for aksjen den dagen |
| Kurs | `close` og `adjusted_close` |

Lagringen skjer automatisk, fra første kjøring. Uten den kan spørsmålet «hva sa
løsningen om EQNR for to uker siden?» ikke besvares.

Dette er et tredje lager, med et annet formål enn de to i FR-406: de lagrer
*data fra kilden*, dette lagrer *hva løsningen mente om dem*.

---

### 4.5 Meldingsfilter og deduplisering

Grunnlaget er en måling over 2026-08-22 til 2026-09-18, **28 kalenderdager**.
For de 15 selskapene ga det **121 meldinger, 4,3 per kalenderdag**. Mengden er
ikke problemet; sorteringen er. Fordelingen i sin helhet: `malinger.md`,
seksjon 4.

#### FR-501 — Deduplisering av språkdubletter

32 av 121 meldinger (26 %) er samme melding publisert på norsk og engelsk.

**Kjennetegn på en dublett:** samme utsteder, samme kategori, samme
publiseringsminutt.

**Hvilken beholdes:** den norske når begge finnes. Finnes bare én av dem,
beholdes den. Språkvalget er eksplisitt fordi grensesnittet er norsk, og fordi
KI-forklaringen skal gis på norsk.

**Rekkefølge:** dedupliseringen kjøres **før** kategorifilteret, ikke etter.

#### FR-502 — Kategorifilter i tre bøtter

Grovsorteringen gjøres med regler i vanlig programkode på NewsWebs kategorifelt.
Hver kategori hører til nøyaktig én bøtte.

Antallene er **før** dedupliseringen i FR-501, altså av de 121 hentede
meldingene.

| Kategori | Antall før dedup | Bøtte |
|---|---:|---|
| Innsideinformasjon | 3 | Slipper gjennom |
| Halvårsrapport | 6 | Slipper gjennom |
| Annen informasjonspliktig regulatorisk informasjon | 24 | Slipper gjennom |
| Flagging | 5 | Slipper gjennom |
| Meldepliktig handel for primærinnsidere | 10 | Slipper gjennom |
| Ikke-informasjonspliktige pressemeldinger | 18 | **KI avgjør relevans** |
| Utsteders meldeplikt ved handel i egne aksjer | 35 | Filtreres bort |
| Renteregulering | 10 | Filtreres bort |
| Endringer i rettighetene til aksjer/verdipapirer | 7 | Filtreres bort |
| Eks.dato | 3 | Vises ikke som melding — se FR-503 |

Begrunnelsen for hver bøtte står i `begrunnelser.md`.

#### FR-503 — Eks.dato som datakilde for utbyttemerking

Meldinger i kategorien `EKS.DATO` vises ikke i meldingslista, men skal ikke
forkastes. De er inngangen til kravet i FR-407 om å merke utbyttedager: det er
eks.dato som forteller hvilke dager differansen mellom to viste sluttkurser ikke
vil stemme med den viste prosenten.

Kategorien føres derfor til utbyttemerkingen, ikke til meldingsvisningen.

#### Resultat av filteret

| Steg | Meldinger over 4 uker | Per kalenderdag |
|---|---:|---:|
| Hentet fra NewsWeb | 121 | 4,3 |
| Etter deduplisering | 89 | 3,2 |
| Slipper gjennom til KI-forklaring | ~35 | ~1,25 |
| Til KI-relevansvurdering | ~13 | ~0,5 |

Tallene etter deduplisering er anslag: dublettandelen er målt samlet, ikke per
kategori. Størrelsesorden er poenget — KI-laget skal behandle noen få meldinger
om dagen, ikke titalls.

---

### 4.6 KI-laget og grensen mot regelbasert kode

KI brukes der, og bare der, metadata er uttømt. At metadata ikke skiller
betydning er målt tre ganger uavhengig; argumentet står i `begrunnelser.md`.

KI-laget brukes ikke til å avgjøre hvilket selskap en melding gjelder — den
jobben gjør `issuerSign` bedre og gratis.

#### FR-601 — Av/på-bryteren er brukersynlig

KI-laget skal kunne slås av og på fra grensesnittet. Bryteren er ikke et
utviklerflagg i en konfigurasjonsfil, fordi bidraget skal kunne vises fram under
demonstrasjonen mens noen ser på.

#### FR-602 — Visningen når KI-laget er av

Meldingene i samlekategorien skal fortsatt vises når laget er av, merket
**«ikke vurdert»**. De skal ikke forsvinne.

Med laget av gjelder altså: regelfilteret sorterer som før, meldinger som slapp
gjennom vises uten KI-forklaring, og samlekategorien vises uten
relevansmerking, men merket som uvurdert.

Begrunnelsen er at meldinger som forsvinner, blander sammen to forskjellige ting
— færre meldinger og uforklarte meldinger — og gjør sammenligningen av og på
meningsløs.

#### FR-603 — Usikkerhet vises som forbehold, ikke som rekkefølge

Er en KI-vurdering usikker, skal den vises med forbehold der den står.
Usikkerhet skal ikke håndteres ved å sortere meldingen ned.

Usikkerhet avledes av observerbare kjennetegn, ikke av en selvrapportert
sikkerhetsscore fra modellen:

1. Om selskapet nevnes i overskrift eller ingress
2. Om mange selskaper nevnes likeverdig i samme sak
3. Om to kjøringer gir samme klassifisering

Der kjennetegnene spriker, merkes vurderingen som usikker i stedet for at
modellen tvinges til et svar.

#### FR-604 — Logging av KI-bidraget, fra første kjøring

For hver melding KI-laget behandler, lagres:

| Felt | Hvorfor |
|---|---|
| Meldings-id, utsteder, kategori, publiseringstidspunkt | Identifiserer meldingen entydig mot NewsWeb |
| Hva regelfilteret alene gjorde med den | Uten dette finnes ingen kontrast å måle KI-bidraget mot |
| KI-lagets vurdering, forklaring og usikkerhetsmerke | Selve bidraget |
| Promptversjon og modell som ga vurderingen | Se FR-605 |

Loggingen starter ved første kjøring, ikke når eksempelsettet skal lages. Skrus
loggingen på i etterkant, finnes ikke uka målet krever.

#### FR-605 — Promptversjon og modell lagres med hver vurdering

Hver lagret vurdering skal bære promptversjonen og modellen som produserte den.

Justeres prompten i oktober, må det være mulig å se hvilken versjon som ga
hvilken vurdering. Uten det blir eksempelsettet en blanding av flere systemer
som ser ut som ett.

#### FR-606 — Relevansskalaen

KI-vurderingen av en melding i samlekategorien gir én av tre verdier:

| Verdi | Betyr |
|---|---|
| **Påvirker selskapet direkte** | Saken har konkret betydning for selskapets drift, kontrakter, eierskap eller resultat |
| **Kan påvirke** | Saken kan få betydning, men det er ikke gitt |
| **Lite relevant** | Saken har ingen praktisk betydning for en sparer |

De tre nivåene er bevisst de samme som brukes i relevanseksperimentet, slik at
resultatene kan sammenlignes direkte.

**Visning `[FORELØPIG]`:** meldinger vurdert som *påvirker direkte* eller *kan
påvirke* vises. *Lite relevant* skjules bak en visningsbryter — skjult, men ikke
borte, slik at brukeren kan kontrollere hva som ble sortert vekk.

Hvor grensen faktisk bør gå, er ikke avgjort og kan ikke avgjøres på papir. Se
åpent punkt 2.

---

### 4.7 Signalstyrke og retning

> **Foreløpige parametre.** Alle terskler og vinduer i denne seksjonen er merket
> `[FORELØPIG]` og bygger på en test over **15 handelsdager**. Testen kjøres på
> nytt mot omtrent 200 handelsdager, og først da låses verdiene.

Kravet til signalet er **forklarbarhet, ikke treffsikkerhet**. Vi lover ikke
bedre signaler enn andre, men at brukeren alltid kan se hva som ga utslaget.

#### FR-701 — Tre navngitte sjekker

Signalet består av tre sjekker. Hver gir +1, 0 eller −1. Det finnes ingen fjerde
sjekk, ingen vekting og ingen skjult formel.

| # | Sjekk | Måler | Gir utslag når |
|---|---|---|---|
| 1 | **Trend** | Sluttkurs mot 50-dagers glidende snitt | Kursen ligger mer enn `[FORELØPIG] 2 %` over eller under snittet |
| 2 | **Bevegelse** | Dagens endring mot aksjens egen volatilitet | Endringen overstiger ett standardavvik av siste `[FORELØPIG] 20` dagers endringer |
| 3 | **Interesse** | Dagens volum mot eget medianvolum | Volumet overstiger `[FORELØPIG] 1,5 ×` medianen siste `[FORELØPIG] 20` dager |

Fortegnet på **interesse** følger dagens kursendring: høyt volum på en dag med
oppgang gir +1, høyt volum på en dag med nedgang gir −1. Volum har ingen retning
i seg selv.

Alle beregninger bruker `adjusted_close`, slik at et ordinært utbytte ikke
feiltolkes som kursfall.

#### FR-702 — Nøytralsone i trendsjekken

Trendsjekken skal ha en nøytralsone på `[FORELØPIG] ±2 %` rundt det glidende
snittet. Innenfor sonen gir sjekken 0.

Uten nøytralsonen kan signalstyrke 0 ikke forekomme: en aksje ligger alltid
enten over eller under sitt eget snitt, så trendsjekken slår alltid ut. Målingen
viste at 64 % av alle aksjedager da havner på styrke 1. Oversikten kan dermed
aldri si at det ikke skjer noe, og det bryter målet «Dager uten signal».

Med nøytralsonen får `[FORELØPIG] 11,1 %` av aksjedagene styrke 0.

#### FR-703 — Signalstyrke

Signalstyrke er summen av absoluttverdiene til de tre sjekkene, altså et helt
tall fra 0 til 3. Styrken sier hvor kraftig sjekkene slår ut — ikke hvor
sannsynlig en kursbevegelse er, og ikke om aksjen bør kjøpes eller selges.

Målt fordeling `[FORELØPIG]`: styrke 0 hos 11,1 %, styrke 1 hos 57,8 %, styrke 2
hos 22,7 %, styrke 3 hos 8,4 % av aksjedagene. Testoppsett og følsomhet for
volumfaktoren: `malinger.md`, seksjon 5.

#### FR-704 — Retning

Retningen leses av fortegnene til de sjekkene som ga utslag:

| Retning | Betingelse |
|---|---|
| Positiv | Alle utslag peker opp |
| Negativ | Alle utslag peker ned |
| Blandet | Utslagene spriker |
| Ingen | Ingen av sjekkene ga utslag (styrke 0) |

Blandet er et gyldig og informativt svar — et kursfall på høyt volum i en aksje
som fortsatt ligger over sitt eget snitt *er* blandet, og skal presenteres som
det.

#### FR-705 — Terskel for at en aksje skiller seg ut

En aksje skiller seg ut den dagen signalstyrken er `[FORELØPIG] 2` eller høyere.

Terskelen styrer **visningen og sorteringen**, ikke hentingen.
**Meldinger hentes for alle 15 selskapene hver dag.** KI-kostnaden er omtrent
1,25 forklaringer og 0,5 relevansvurderinger i døgnet.

Hvorfor terskel 2 og ikke 3: se `begrunnelser.md`.

#### FR-706 — Synlig begrunnelse i aksjedetaljen

Aksjedetaljen skal liste de tre sjekkene ved navn med verdien hver av dem ga den
dagen — ikke bare den samlede styrken. Brukeren skal kunne lese at trend ga +1,
bevegelse 0 og interesse −1, og selv se hvorfor styrken ble 2 og retningen
blandet.

Ingen vekting og ingen skjult formel. Dette er kravet som gjør signalet
forklarbart, og det er ikke valgfritt.

---

## 5. Tverrgående krav

### NFR-01 — Daglig drift skal holde seg innenfor API-kvoten

EODHD gir 20 kall i døgnet på gratisnivå. Daglig henting av kurser koster ett
kall per symbol, altså 15. Det gir **fem kalls margin** til omkjøringer,
feilretting og manuell testing.

Ett bulk-kall er ikke et alternativ: bulk-endepunktet koster 100 kall flatt. Ett
kall per symbol er eneste vei, og det er denne begrensningen som gir universet
på 15.

Relevanseksperimentet er en engangsinnsamling og inngår ikke i daglig drift; se
åpent punkt 5.

### NFR-02 — Brukeren venter aldri på en henting

Henting og KI-behandling skjer som bakgrunnsoppgave, ikke når en side vises.
Mens en henting pågår, vises siste kjente data med tidsstempel.

### NFR-03 — Manglende data stopper ikke hovedflyten

Ved kildefeil, manglende data eller dager uten tydelige signaler skal
hovedflyten verken stoppe eller tvinge frem et resultat. Siste kjente data vises
med tidsstempel, og signalstyrke 0 er et gyldig svar (FR-702).

### NFR-04 — KI-laget skal ikke kunne ta ned hovedflyten

Applikasjonen skal fungere med den regelbaserte analysen alene. En treg eller
utilgjengelig modell skal ikke forsinke eller stoppe markedsoversikten. Dette
henger sammen med av/på-bryteren i FR-601, som gjør KI-bidraget etterprøvbart.

### NFR-05 — Norsk i grensesnitt og forklaringer

Grensesnittet er på norsk, og KI-forklaringene gis på norsk. Dette er også
begrunnelsen for språkvalget i dedupliseringen (FR-501).

### NFR-06 — Løsningen gir ikke investeringsråd

Signalstyrke og retning beskriver hva sjekkene slo ut på, ikke hva brukeren bør
gjøre. Ingen del av grensesnittet skal formuleres som en anbefaling om kjøp
eller salg.

### NFR-07 — Rådata bevares fra første kjøring

NewsWeb er udokumentert backend og kan endres uten varsel. Rådata lagres som
tidsstemplede øyeblikksbilder fra første henting (FR-406), slik at prosjektet
ikke står tomhendt om en kilde forsvinner, og slik at målinger kan etterprøves.

---

## 6. Datakilder

Kildestatus, kontrollerte vilkår, forkastede kilder og skillet mellom hva som
publiseres og hva som blir liggende lokalt: `docs/kilder-og-rettigheter.md`.

| Kilde | Brukes til | Koster kvote |
|---|---|---|
| EODHD `/api/eod` | Sluttkurser | 1 kall per symbol, 15 i døgnet |
| Oslo Børs NewsWeb | Børsmeldinger | Nei |
| Euronext finanskalender | Kommende hendelser | Nei |
| EODHD `/api/news` | Relevanseksperimentet, én engangsinnsamling | 10 kall per ticker (5 per forespørsel + 5 per ticker), ~80 kall for åtte selskaper. Ikke daglig drift — se åpent punkt 5 |

To forbehold hører til PRD-en fordi de kan velte krav: **NewsWeb-vilkårene er
ikke kontrollert**, og API-et er udokumentert backend for Oslo Børs' egen
nettside. Faller NewsWeb bort, finnes ingen åpenbar erstatning — E24 er forkastet
på vilkår, og andre norske finansmedier publiserer ikke lenger åpen RSS. Se
åpent punkt 1.

---

## 7. Suksessmål

| Mål | Hva vi måler | Terskel | Frist |
|---|---|---|---|
| Brukerutfall | En person utenfor gruppen gjennomfører hovedflyten og forklarer uoppfordret hvorfor en aksje skiller seg ut | Minst 1 person, under 5 minutter, uten hjelp | Før prosjektinnlevering |
| Adopsjon | Gruppen bruker løsningen på egne aksjer og logger feil | Minst 4 av 5 børsdager fra første fungerende versjon | Løpende |
| Drift | Daglig henting fullfører innenfor kvoten; ved kildefeil vises siste kjente data med tidsstempel | Ingen manuelle steg, ingen stopp ved manglende data | Ukentlig |
| Dager uten signal | Dager uten tydelige signaler håndteres uten at hovedflyten stopper eller systemet tvinger frem et resultat | Signalstyrke 0 forekommer og vises korrekt | Løpende |
| KI-bidrag i drift | Hvilke meldinger KI-laget forklarte eller omklassifiserte som regelfilteret alene ikke klarte å skille | Dokumentert eksempelsett fra minst én ukes drift | Før demonstrasjonen, est. uke 45 |
| Relevanseksperiment | Testsett på ~50 medieartikler fra åtte selskaper, merket manuelt, kjørt mot både symbolmatching og KI-klassifisering | Eksperimentet gjennomført og tallene dokumentert — ikke at KI kommer best ut | Uke 41, fra 2026-10-05 |
| Fortsatt bruk | Om vi bruker løsningen frivillig etter at utviklingen er ferdig, ikke bare for å teste den | Minst tre dager i uka de to siste ukene, loggført | Ved prosjektinnlevering |
| Grensesnitt og stabilitet | Hovedflyten fungerer uten feil og med et ryddig, gjennomarbeidet grensesnitt i en demonstrasjon | Hovedflyten gjennomført uten feil eller manuelle inngrep | Ved demonstrasjonen |

**Hovedflyten** er definert som: åpne markedsoversikten, se hvilke aksjer som
skiller seg ut, åpne én av dem, og lese hvorfor — de tre sjekkene med verdiene
sine, og meldingene som gjelder. Både brukerutfallsmålet og stabilitetsmålet
måler denne flyten.

**Bundet til datoer som ikke er fastsatt:** FR-407, FR-601 og FR-408, og målene
«KI-bidrag i drift» og «Grensesnitt og stabilitet». Se åpent punkt 13.

### Motmål

Mål kan nås på måter som ikke betyr noe. Disse leses sammen med tabellen over:

- **Vi setter ikke mål for hvor godt signalene treffer markedet.** Kravet til
  signalet er forklarbarhet, ikke treffsikkerhet.
- **Relevanseksperimentet skal avgjøre påstanden, ikke bekrefte den.** Viser
  målingen liten forskjell mellom symbolmatching og KI-klassifisering, er det
  også et funn.
- **KI-bidrag måles i hva laget faktisk klarte å skille**, ikke i hvor mange
  meldinger det behandlet.
- **Adopsjon som bare er testing teller ikke.** Derfor er «fortsatt bruk» et
  eget mål med egen terskel.
- **Usikkerhetsmerking som aldri slår til er et varsel**, ikke en suksess. Slår
  FR-603 aldri ut, er kriteriene sannsynligvis feil kalibrert.
- **Vi har ingen teknisk fordel andre ikke kan kopiere**, og skal ikke påstå at
  vi har den. Datakildene er åpne eller kommersielt tilgjengelige for alle.

---

## 8. Åpne punkter

### Må avgjøres før arbeidet går videre

| # | Punkt | Eier | Frist | Blokkerer |
|---|---|---|---|---|
| 1 | **Vilkårskontroll i tre deler:** NewsWeb, Euronext finanskalender, og om EODHDs vilkår tillater nyhetsinnhold som input til en språkmodell. Fristen kan ikke skyves: holder ikke vilkårene, må hele meldingsdelen omdisponeres, og det må oppdages mens det er tid | *‹fylles inn›* | **2026-09-27** | Meldingsdelen og relevanseksperimentet |
| 2 | **KI-terskelen i samlekategorien** — hvor grensen mellom «kan påvirke» og «lite relevant» skal gå. Kan ikke avgjøres på papir; relevanseksperimentet er input. Foreløpig regel står i FR-606 | *‹fylles inn›* | Etter uke 41 | Kalibrering av FR-606 |
| 3 | **Hvilken kilde gir handelskalenderen?** FR-402 hviler på «forventet børsdag», men ingen kilde er utpekt for hvilke dager Oslo Børs er åpen | *‹fylles inn›* | Før implementasjon | FR-402 |
| 4 | **Hvordan utledes eks.dato?** FR-407 og FR-503 forutsetter at utbyttedager kan identifiseres, men regelen er ikke skrevet | *‹fylles inn›* | Før demonstrasjonen | FR-407, FR-503 |

### Må følges opp

| # | Punkt | Eier | Frist |
|---|---|---|---|
| 5 | **Samle inn testsettet til relevanseksperimentet** — ~50 artikler fra åtte selskaper, ~80 kall fra bonuskvoten. Kan ikke startes før punkt 1 er besvart. Det er heller ikke verifisert at `/api/news` svarer for `.OL`-tickere på gratisnivå; én testforespørsel avgjør | | Uke 39 eller 40 |
| 6 | **Usikkerhetskriteriene er skrevet for medieartikler.** Kjennetegn 1 bærer svakt når utstederen selv er avsender | | Før KI-laget implementeres |
| 7 | **Låsing av signalparametre** mot ~200 handelsdager. Koster 15 kall | | Før signalet låses |
| 8 | **Oppstart av tilbakekjøpsprogram** er ekte nyhet, men filtreres bort sammen med de ukentlige statusrapportene | | Før innlevering |
| 9 | **Kontrollere Alpha Vantages vilkår** for ikke-kommersiell bruk | | Før innlevering |
| 10 | **Skjevfordeling mot positiv retning**, 68 % i testen. Vurderes mot året, ikke mot femten dager | | Etter utvidet test |
| 11 | **Meldepliktig handel for primærinnsidere** justeres hvis den viser seg å være i hovedsak opsjonsutøvelse | | Etter én ukes drift |
| 12 | **Bekrefte horisont og hendelsestyper** i FR-302, som i dag er antatt | | Før implementasjon |
| 13 | **Datoer for demonstrasjon og prosjektinnlevering** | | Snarest |

**Punkt 1 er det eneste som kan velte datagrunnlaget**, og det vil i så fall
velte to ting samtidig: meldingsdelen hvis NewsWeb-vilkårene ikke holder, og
relevanseksperimentet hvis EODHDs vilkår forbyr språkmodellbruk.

Ingen av punktene har eier ennå.
