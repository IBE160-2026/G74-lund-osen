---
title: "PRD — OSE Signal"
status: aktiv
created: 2026-09-20
updated: 2026-11-14T19:15
---

# PRD — OSE Signal

**Emne:** IBE160 Programmering med KI, Høgskolen i Molde
**Gruppe:** G74 — Joakim Lund, Marian Osen

Dette er den gjeldende teksten. Hvert krav sier hva appen gjør nå, og hva en
test kan sjekke. Hvordan kravene har endret seg, står i
[endringsloggen](prd-endringslogg.md), med de daterte linjene ordrett. PRD-en
slik faglærer vurderte den 12.11, står i taggen `prd-vurdert-2026-11-12`. Slik
den var ved fristen 5.11, står den i taggen `prd-ferdig-2026-11-03`.

## Kort fortalt

**Problemet.** Den som følger 10–30 norske aksjer ved siden av jobb eller
studier, har et sorteringsproblem. Kursene finnes, men de ligger på ulike steder,
og det meste er uviktig akkurat i dag (§1).

**For hvem.** En vanlig sparer som vil se hva som beveget seg siste børsdag, og
hvorfor (§1, brukerreisen UJ-1).

**Hva v1 er.** En webapplikasjon for PC, på norsk, som kjører lokalt (§2). Lista
har 15 likvide aksjer på Oslo Børs fra start og kan ha opptil 18. Grensen kommer
av at EODHD gir 20 kall i døgnet (§3). Kjernen er det briefen v8 lover:
signalet med forklaring, KI-teksten med bryter, historikken, hovedindeksen, Min
liste, lenken til investorsiden og egne nøkler til Gemini, Anthropic og OpenAI.
En lokal modell er standard og trenger ingen nøkkel (FR-608). Én tabell i §2
viser hva som er kjerne, ekstra og senere, og hva som er bygget.

**Hva v1 ikke er.** Ingen investeringsråd (NFR-06), kontoer, varsler, betaling
eller mobilapp (§2). Børsmeldingene og de kommende hendelsene er ute. Euronext
ga ikke tillatelse til automatisert henting (plan B, vedlegg A).

**De viktigste kravene.**

- Tre sjekker, trend, bevegelse og interesse, gir hver +1, 0 eller -1.
  Signalstyrken er hvor mange som slo ut, og retningen leses av fortegnene.
  Styrken er verken en sannsynlighet eller et råd om kjøp eller salg
  ([FR-701](#fr-701--tre-navngitte-sjekker),
  [FR-703](#fr-703--signalstyrke), [FR-704](#fr-704--retning)).
- Aksjesiden viser målingen bak hver sjekk, så brukeren kan regne etter
  ([FR-706](#fr-706--synlig-begrunnelse-i-aksjedetaljen)).
- Oversikten har fem kolonner, sortert på signalstyrke
  ([FR-101](#fr-101--fem-kolonner), [FR-102](#fr-102--standard-sortering)).
- Webserveren henter aldri, og driften holder seg innenfor kvoten
  ([FR-401](#fr-401--henting-utløses-eksplisitt-aldri-av-en-oppstart),
  [NFR-01](#nfr-01--daglig-drift-skal-holde-seg-innenfor-api-kvoten)).
- Dagens vurdering lagres, regnes aldri på nytt og etterfylles ikke
  ([FR-408](#fr-408--dagens-vurdering-lagres-per-aksje)). En børsdag uten den får
  signalet regnet i ettertid av kursene, merket «i ettertid» og uten KI-tekst.
- Regler regner, og KI formulerer. KI-teksten står under regelforklaringen. Den
  kontrolleres og logges, og den kan slås av
  ([FR-601](#fr-601--avpå-bryteren-er-brukersynlig),
  [FR-603](#fr-603--ki-teksten-sier-ikke-mer-enn-grunnlaget),
  [FR-604](#fr-604--logging-av-ki-bidraget-fra-første-kjøring)).
- Demoen har oppdiktede tall og trenger ingen nøkkel
  ([FR-411](#fr-411--demoversjonen-har-oppdiktede-tall-i-en-egen-base)).

Hva som er ferdig på main akkurat nå, står i [«Status» i README-en](../../../../README.md#status).

---

Dette dokumentet fastsetter hva OSE Signal skal gjøre i v1. Det er et
kravregister. Hvert krav har én gjeldende tekst og én linje begrunnelse der den
trengs. Under «*Konsekvenser:*» står det en test kan sjekke. Kodenavn, commits,
migrasjoner og storynummer står i arkitekturen og i `epics.md`, ikke her.
Avgjørelsene er gruppens.

**Tilhørende dokumenter.** [`prd-endringslogg.md`](prd-endringslogg.md) har
historikken. `begrunnelser.md` har resonnementet bak kravene, og `malinger.md`
har alle målingene med metode. `.memlog.md` er beslutningsloggen, og
`gjennomganger/` har avstemmingene mot kildedokumentene. `epics.md` knytter hvert
FR til storyene («FR Coverage Map»).

---

## 1. Bakgrunn og mål

Den som følger 10–30 norske aksjer ved siden av jobb eller studier, har ikke et
informasjonsproblem, men et sorteringsproblem. Kursene og rapportdatoene finnes.
De ligger på ulike steder og i ulikt format, og det meste er uviktig akkurat i
dag.

**Målet med v1** er at en vanlig sparer kan åpne løsningen når kveldens henting
er gjort. Da skal sparen se hva som skilte seg ut siste børsdag, og forstå hvorfor,
uten å slå opp flere steder. Spørsmålet v1 svarer på, er *hva beveget seg, og
hvorfor*.

**Det bærende prinsippet** er at kode og KI holdes fra hverandre. Regler
sorterer, og KI forklarer. Grensen er synlig i grensesnittet, ikke bare i koden.

### Brukerreisen UJ-1

**UJ-1. Kari** følger 12 aksjer ved siden av studiene. Hun åpner appen om
kvelden, etter at hentingen er gjort. Første gang tilbyr oversikten «Vis meg
rundt», og hun kan si «Nei takk». Oversikten viser at to
aksjer har 3 av 3. De står øverst under «Skilte seg ut». Hun åpner den ene og
leser de tre sjekkene under «Hvorfor signalet ble 3». Hver sjekk har verdien den
ga og målingen bak. I kursgrafen ser hun volumsøylene og 50-dagerssnittet. Med KI
på står en kort tekst under sjekkene, som sier det samme i hele setninger.

- *Climax:* hun kan forklare hvorfor aksjen skiller seg ut, med tallene, uten
  å ha lest noe annet sted.
- *Edge:* hentingen mangler i dag. Oversikten viser siste kjente børsdag med
  dato og tidspunktet dataene ble hentet. Aksjen som mangler dagens kurs, sier
  hvilken dag raden gjelder. Ingenting ser ut som dagens tall.

Kravene UJ-1 hviler på: FR-101, FR-102, FR-109, FR-201, FR-202, FR-401, FR-402,
FR-602, FR-706 og NFR-03. Suksessmålet SM-1 måler reisen.

### Ordliste

Ordene slik appen bruker dem. Koden og eldre krav kan bruke ordet i parentes.

| Ord | Betyr i appen |
|---|---|
| **Børsdag** | Mandag–fredag som Oslo Børs ikke har stengt, regnet i norsk tid. Halve handelsdager er børsdager |
| **Henting** | Kommandoen som henter kursene og hovedindeksen og skriver dagens vurderinger og KI-tekster. Den kjører hver kveld fra kl. 22:15, eller når noen starter den. Webserveren henter aldri |
| **Lista** (aktiv liste) | Aksjene appen henter og vurderer, opptil 18. Fra start er det de 15 i §3 |
| **Min liste** | Siden med aksjene brukeren har merket med stjerne (FR-111). Den er et utvalg av lista, ikke en egen henting |
| **Bransje** (sektor) | Gruppen en aksje hører til. Brukeren ser «bransje», og koden og §3 sier «sektor» |
| **Aksjesiden** (aksjedetaljen) | Siden for én aksje, med kursgrafen, sjekkene og KI-teksten |
| **Sjekk** | Én av de tre reglene, trend, bevegelse og interesse. Hver gir +1, 0 eller -1 (FR-701) |
| **Signal** | Signalstyrken, 0–3, og retningen, Positiv, Negativ, Blandet eller Ingen, for én aksje og én børsdag (FR-703, FR-704). En aksje skiller seg ut ved 2 eller mer (FR-705) |
| **Vurdering** | Den lagrede raden med signalet, sjekkene og målingene for én aksje og én børsdag, eller grunnen til at den mangler. Kveldens vurdering skrives én gang og etterfylles ikke. En børsdag uten den kan få signalet regnet i ettertid, merket (FR-408) |
| **Den justerte sluttkursen** (`adjusted_close`) | Kursen kilden har regnet om bakover etter utbytte og splitt. Signalet, endringen og grafen bruker den. Sluttkursen (`close`) er den ujusterte, og den står i oversikten. På en justeringsdag stemmer derfor ikke differansen mellom to sluttkurser med prosenten (FR-407) |

Kolonnene i oversikten bygger på disse feltene fra kilden:

| Kolonne | Felt |
|---|---|
| Sluttkurs | `close` for siste børsdag |
| Endring | Endring i prosent, regnet på `adjusted_close` |

Sluttkursen vises som `close`, mens endringen regnes på `adjusted_close` (FR-407).

---

## 2. Omfang

<a name="inne-i-v1"></a><a name="hvis-vi-rekker"></a>

### Kjerne, ekstra og senere

**Kjerne** er det briefen v8 lover, og det som var flettet da gruppen avgjorde
omfanget 19.10. **Ekstra** er det som er bygget utover briefen. Det ble bygget på
egen gren og flettet ferdig og grønt før funksjonsstoppen, README-prøven senest
én uke før innleveringen. **Senere** er plan A og det som ikke er i v1, men står
som plan for en senere versjon (§8, «v1.1»). **Bygget** betyr flettet til main og
lest i koden 12.11.

| FR | Krav | Kjerne / ekstra / senere | Bygget? |
|---|---|---|---|
| FR-101 | Fem kolonner, raden uten signal og raden uten kurser | kjerne | ja |
| FR-101 | Periodevalget i oversikten | ekstra | ja |
| FR-101 | Oversikten viser lista som er aktiv | ekstra | ja |
| FR-101 | Endringen i kroner under prosenten | senere | nei |
| FR-102 | Standard sortering og sortering ved klikk | kjerne | ja |
| FR-103 | Retning som tekst, symbol og farge | kjerne | ja |
| FR-104 | Hovedindeksen over tabellen | kjerne | ja |
| FR-105 | Søylene under hovedindeksen | kjerne | ja |
| FR-106 | Børsometeret | ekstra | ja |
| FR-107 | Merket for endret signalstyrke | senere | nei |
| FR-108 | Filter på signalet, tatt bort 11.11 | ekstra | nei |
| FR-109 | Hjelpen bak «?» | kjerne | ja |
| FR-109 | «Vis meg rundt» og «Spill av omvisningen» | ekstra | ja |
| FR-109 | «Lær noe nytt» | senere | nei |
| FR-110 | Innstillinger | ekstra | ja |
| FR-111 | Min liste | kjerne | ja |
| FR-201 | Kursgrafen med periodevalget | kjerne | ja |
| FR-202 | MA50 og hovedindeksen i grafen | kjerne | ja |
| FR-202 | Volumsøylene og båndet for sjekk 2 | ekstra | ja |
| FR-203 | Sjekkene, KI-teksten, historikken og lenken til investorsiden | kjerne | ja |
| FR-203 | Høy og lav og endringen i kroner | senere | nei |
| FR-204 | Aksjesiden uten gyldig signal | kjerne | ja |
| FR-205 | «Se nærmere» | senere | nei |
| FR-206 | Signaldager i kursgrafen | ekstra | ja |
| FR-207 | Kommende eks.dato i kursgrafen | senere | nei |
| FR-301–FR-303 | Kommende finansielle hendelser (vedlegg A) | senere | nei |
| FR-401 | Henting bare når kommandoen kjøres, og kveldsjobben | kjerne | ja |
| FR-402 | Kontroll mot forventet børsdag | kjerne | ja |
| FR-403 | Hull i kursserien fylles | ekstra | ja |
| FR-404, FR-405 | Børsmeldingene hentes (vedlegg A) | senere | nei |
| FR-406 | To lagre for kursdata | kjerne | ja |
| FR-407 | Justeringsdagene merkes | ekstra | ja |
| FR-408 | Dagens vurdering lagres | kjerne | ja |
| FR-408 | Signalet regnet i ettertid for børsdager uten vurdering, merket «i ettertid» | ekstra | ja |
| FR-408 | KI-tekst for små hull, 1–3 kvelder | senere | nei |
| FR-409 | Tilstandene skilles, også «ikke i lista» | kjerne | ja |
| FR-410 | Hovedindeksen hentes i samme kjøring | kjerne | ja |
| FR-411 | Demoversjonen | kjerne | ja |
| FR-412 | Lista over aksjer, ferdige lister og egne aksjer | ekstra | ja |
| FR-412 | «De 15 mest omsatte» | ekstra | ja |
| FR-413 | Måling av omsetning | ekstra | ja |
| FR-414 | Eks.datoer ført for hånd | senere | nei |
| FR-501–FR-503 | Meldingsfilteret (vedlegg A) | senere | nei |
| FR-601 | Av/på-bryteren | kjerne | ja |
| FR-602 | Visningen av KI-teksten | kjerne | ja |
| FR-603 | Kontrollen av KI-teksten | kjerne | ja |
| FR-604 | Loggen over KI-teksten | kjerne | ja |
| FR-605 | Promptversjon og modell | kjerne | ja |
| FR-606 | Relevansskalaen | senere | nei |
| FR-607 | KI-teksten om dagen | ekstra | ja |
| FR-608 | Valg av tjeneste og egne nøkler | kjerne | ja |
| FR-608 | ChatGPT med «Sign in with ChatGPT» | senere | nei |
| FR-602A–FR-604A, FR-606A | KI-laget over meldinger (vedlegg A) | senere | nei |
| FR-701–FR-706 | Signalet og forklaringen | kjerne | ja |

Uten eget FR, men ekstra og bygget: egne notater på aksjesiden med tenkte kjøp
og salg, «Følg en aksje» og «Din egen liste». De står i `epics.md`.

KI-tekst for små hull står som senere, fordi den tar tid, krever kontroll, gir
fare for å se framover, og gir mindre nytte bakover (gruppens svar 14.11 kl.
05:49).

Løsningen er en **webapplikasjon for PC**. Den er på norsk og kjører lokalt.
Sidene virker også på smal skjerm, men en mobilapp er utenfor v1.

### Utenfor v1

Utenfor v1 er brukerkontoer, innlogging og ekte portefølje. Det samme er
varsler, betaling, mobilapp og meglerintegrasjon, flere børser og flere språk.
Også fundamental- og verdimodell, intradag- og sanntidsdata og en statistisk
studie av om signalene slår markedet er utenfor. Børsmeldingene og de kommende
hendelsene er plan A, i vedlegg A.

### Utsatte vurderinger

To vurderinger er utsatt til løsningen eventuelt publiseres: **personvern** og
**regelverket som gjelder når en tjeneste presenterer finansielle signaler**.
Videreformidlingsretten er kontrollert. Vilkårene til EODHD og Euronext står i
`docs/kilder-og-rettigheter.md`.

**Utløseren er publisering, ikke kommersialisering.** Skal applikasjonen
publiseres, også uten at noen tar betalt, vurderes vilkårene på nytt. Kodebasen
er offentlig i IBE160-organisasjonen. Hva som publiseres, og hva som blir
liggende lokalt, står i `docs/kilder-og-rettigheter.md`.

---

## 3. Aksjeuniverset

### Kriterium

De 15 aksjene appen starter med, oppfyller begge kravene:

1. **Median daglig omsetning over 25 MNOK**, målt over siste tre måneder.
   Omsetning regnes som volum × sluttkurs per handelsdag. Medianen tas over
   perioden.
2. **Universet dekker minst åtte sektorer.** Kravet gjelder lista som helhet,
   ikke det enkelte symbolet.

Det brukeren ser, heter «bransje», og koden og denne delen sier «sektor». Appen
har 13 bransjer (`designregler.md` §4), og de 15 hører til 8 av dem.

Antallet er utledet av API-kvoten. EODHD på gratisnivå gir 20 kall i døgnet.
Kursene koster ett kall per symbol, og hovedindeksen ett til (NFR-01).
Likviditet måles i **kroner, ikke i antall aksjer** (`begrunnelser.md` §2).

### Universet

Målt 2026-09-20 over 65 handelsdager. Metoden står i `malinger.md`, seksjon 1.

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

Medianen for universet er 223,9 MNOK per dag. Det laveste symbolet ligger på
32,3 MNOK, over terskelen på 25 MNOK. Lista dekker åtte sektorer. Hvorfor spennet
fra 920 til 32 MNOK er akseptabelt, står i `begrunnelser.md` §2.

Lista kan byttes (FR-412). Kriteriet over gjelder de 15, og grensene i signalet
er målt på dem. En aksje som omsettes for mindre enn 32 MNOK om dagen, eller som
ikke er målt, merkes «Utenfor målingen».

---

## 4. Funksjonelle krav

Rekkefølgen følger kravnumrene: grensesnittet først, så data og beregning.
FR-407 står i 4.1, fordi det hører til visningen. ID-en er beholdt. Plan A står i
vedlegg A.

### 4.1 Markedsoversikten

#### FR-101 — Fem kolonner

Markedsoversikten viser aksjene i lista som er aktiv (FR-412). Den har nøyaktig
fem kolonner:

| Kolonne | Innhold |
|---|---|
| Selskap | Selskapsnavnet som lenke til aksjesiden, med ticker og bransje under |
| Sluttkurs | Sluttkursen for siste børsdag |
| Endring | Endringen i prosent, regnet på den justerte sluttkursen |
| Signalstyrke | 0–3, jf. FR-703, med de tre sjekkene som små merker |
| Retning | Positiv, Negativ, Blandet eller Ingen, jf. FR-704 |

Sluttkursen er den ujusterte, og prosenten er regnet på den justerte. På en
justeringsdag stemmer derfor ikke differansen mellom to sluttkurser med
prosenten (se ordlista), og dagen merkes (FR-407).

Endringen i kroner er ikke i v1, men kan komme senere. Planen er en mindre linje
under prosenten. Den regnes av den justerte sluttkursen for de samme to dagene,
så kronene og prosenten alltid peker samme vei. Sorteringen er fortsatt på
prosent, og det er fortsatt fem kolonner.

Tabellen er delt i to. «Skilte seg ut» har aksjene med styrke på terskelen eller
over (FR-705), og «Øvrige aksjer» har resten. Selskapscellen har også merkene
«Egen» og «Utenfor målingen» (FR-412) og stjernen for Min liste.

**Periodevalget.** Over tabellen velges siste børsdag («I dag», «I går» eller
ukedagen), 1 uke, 1 mnd, 3 mnd, 6 mnd, I år eller 1 år. Det går også an å velge
en dag i datofeltet med «Vis dagen». Oversikten åpner på siste børsdag.
Startdagen for hver periode følger én regel, lik for oversikten og kursgrafen
(FR-201, `designregler.md` §2). Endringen over en periode regnes av kursserien,
på den justerte sluttkursen. Signalet for en dag vises bare der vurderingen er
lagret, fra kvelden eller regnet i ettertid og merket «i ettertid». Det regnes
aldri på nytt når siden vises (FR-408).

**Aksjer uten gyldig signal vises likevel.** Signalet krever 51 handelsdager
fordi MA50 bruker 50 av dem. En nynotert aksje, eller en serie med hull, gir
derfor ingen signalverdi. Raden vises da slik:

| Kolonne | Verdi | Hva som står |
|---|---|---|
| Selskap, Sluttkurs, Endring | Som vanlig | Tallene, når dataene finnes |
| Signalstyrke | Tom | «–», med grunnen under, som «ikke vurdert», «ingen kurs fra dagen», «for kort historikk» eller «ikke børsdag» |
| Retning | **Ukjent** | «– Ukjent», som tekst uten farge |

«Ukjent» er ikke en femte retning i FR-704 — det er fraværet av en vurdering.
*Ingen* sier at de tre sjekkene ble regnet og at ingen slo ut. *Ukjent* sier at
de ikke kunne regnes. Begrunnelse: en rad som forsvinner, sier at aksjen ikke
finnes, og det er ikke sant (NFR-03).

Uten kurser: en aksje uten en eneste kursrad har en rad nederst i tabellen, med
navnet som lenke, «–» i hver kolonne og «ingen kurser ennå». En aksje som venter
på den første hentingen, har «venter på henting» og navnet uten lenke. Tallet i
overskriften stemmer med radene.

*Konsekvenser:*
- Tabellen har fem kolonner for hver periode, også i Min liste.
- En aksje uten vurdering for dagen har «–» og grunnen i Signalstyrke og «Ukjent» i Retning, aldri 0 og aldri «Ingen».
- En aksje uten kurser står nederst med «ingen kurser ennå».
- Når endringen i kroner bygges, har den samme fortegn som prosenten.
- Antallet rader er antallet aksjer i lista.
- Ingen side gjør et API-kall.

##### Hvor gamle dataene er

Stripa øverst sier når dataene sist ble oppdatert. Tidspunktet er det **eldste**
hentetidspunktet blant aksjene som vises. En rad som ble hentet tidligere enn de
nyeste, har «hentet» med tidspunktet under navnet. En rad med en eldre dag enn
sidens har «siste kurs» med ukedag og dato. Det er ingen sjette kolonne.
Ukedagen i overskriften og datoen under den er den eldste dagen blant radene.
Hovedindeksen, søylene og linja over tabellen gjelder den nyeste dagen (FR-104).
Tidsstempler vises i norsk tid.

I den ekte versjonen står det bak tidspunktet når nye kurser tidligst kan
hentes, for eksempel «nye kurser fra kl. 22 i kveld». Dagen regnes av den siste
kursdagen i basen og børskalenderen. Linja sier ikke om kursene blir hentet,
fordi det avhenger av at appen eller kveldsjobben kjører. Demoen henter ikke og
viser ikke linja.

*Konsekvenser:*
- Med én aksje hentet tidligere enn de andre viser stripa den eldste tiden, og raden har sin egen.
- I den ekte versjonen står «nye kurser fra kl. 22 i kveld» bak tidspunktet når neste børsdag er i dag, og demoen har ingen slik linje.
- Med én aksje med en eldre dag har overskriften den eldre ukedagen.

##### Navigasjon til aksjedetaljen

**Selskapsnavnet i første kolonne er lenken til aksjesiden** (FR-201 til
FR-203). Aksjesiden har en synlig lenke tilbake til markedsoversikten. Navnet er
lenken, fordi en egen kolonne med knapp ville brutt de fem kolonnene.

*Konsekvenser:*
- Hver rad med en aksje i lista har en lenke til aksjesiden for aksjen.
- Aksjesiden har lenken «Markedsoversikt».

#### FR-102 — Standard sortering

Standarden er **signalstyrke fallende**. Ved lik styrke sorteres det på
**absolutt kursendring**, innenfor hver av de to delene av tabellen. Absolutt, og
ikke med fortegn, slik at et stort fall ikke havner bakerst bare fordi det er
negativt. **Aksjer uten gyldig signal sorteres sist**, og aksjene uten kurser
aller sist. Tidspunktet dataene ble hentet, påvirker ikke sorteringen.

Et klikk på en kolonne i kolonneraden sorterer på den, og et nytt klikk snur
rekkefølgen. Første klikk sorterer Sluttkurs, Endring og Signalstyrke synkende,
og Selskap og Retning stigende. Selskap sorteres i norsk alfabetisk rekkefølge.
Endring sorteres med fortegn.

Retning grupperes alfabetisk: Blandet, Ingen, Negativ og Positiv. Innenfor hver
gruppe gjelder standarden, og Ukjent står sist i begge retninger. Rekkefølgen er
ikke en rangering fra godt til dårlig (NFR-06). Rader uten verdi står sist i
begge retninger.

Med en kolonne valgt blir tabellen én liste. Linja over tabellen og teksten for
skjermleseren sier kolonnen og retningen. For Retning står det «stigende (A til
Å)» eller «synkende (Å til A)». Lenken «Standard rekkefølge» tar standarden
tilbake. Det samme gjelder Min liste.

*Konsekvenser:*
- Med styrkene 3, 2, 2 og endringene −5 %, +1 % og −3 % blir rekkefølgen 3, så −3 %, så +1 %.
- En rad uten signal står etter alle med signal, uansett endring.
- Et klikk på Endring gir den største oppgangen først, og et nytt klikk den største nedgangen først.
- Ukjent står sist både stigende og synkende.

#### FR-103 — Retning vises i tre redundante kanaler

Retningen vises som tekst, symbol og farge samtidig. Teksten er det samme ordet
som FR-704 bruker, uten oversettelse:

| Retning (FR-704) | Tekst på skjermen | Symbol |
|---|---|---|
| Positiv | Positiv | ↑ |
| Negativ | Negativ | ↓ |
| Blandet | Blandet | ↔ |
| Ingen | Ingen | – |

Teksten er den bærende kanalen, og symbol og farge forsterker. Symbolet står ved
siden av teksten og er skjult for skjermleseren. Ordene «Opp» og «Ned» brukes
ikke. Retningen er hva sjekkene peker mot, ikke kursbevegelsen (NFR-06).

*Konsekvenser:*
- Hver retning har både ordet og symbolet på siden.
- Skjermleseren leser ordet og ikke symbolet.
- Ordene «Opp» og «Ned» står ikke ved retningen.

#### FR-104 — Hovedindeksen i markedsoversikten

Over tabellen står overskriften «Hovedindeksen» med indeksens symbol. Der står
også indeksverdien, endringen i prosent og «x av N gikk bedre enn indeksen».
Ingenting av dette er en kolonne.

- Alt gjelder dagen eller perioden tabellen viser: én dag per side.
- Endringen regnes mot forrige børsdag for indeksen, ikke mot forrige rad, fordi
  indeksen har datoer aksjene ikke har. For indeksen er sluttkursen og den
  justerte sluttkursen like. Derfor kan den sammenlignes med aksjenes endring fra
  FR-101.
- N er aksjene med kurs for dagen, aldri et fast tall. En aksje som ikke er med,
  navngis under: «Ikke med, uten kurs <dato>».
- «Bedre» avgjøres på endringen slik den vises, og lik er ikke bedre.
- Har ingen aksje kurs for dagen, vises ikke sammenligningen. Mangler indeksen
  kurs den dagen, står det der tallet ellers står. Er den ikke hentet ennå, sier
  siden det (NFR-03).

**Unntaket fra én dag per side.** Mangler en aksje kurs for dagen siden viser,
viser raden aksjens egen siste dag. Det gjelder i oversikten og i Min liste, også
ved en periode. Raden har «siste kurs» og datoen under navnet (FR-101).
Hovedindeksen, søylene og linja over tabellen gjelder den nyeste dagen. I
kursgrafen slutter den stiplede indekslinja ved indeksens siste kurs, med
«Indeksen går bare til» og datoen. Med en dag valgt i datofeltet gjelder ikke
unntaket. Der har en aksje uten kurs den dagen «–».

*Konsekvenser:*
- Med 15 aksjer der én mangler dagens kurs, står det «x av 14» og navnet under.
- En aksje med samme endring som indeksen telles ikke som bedre.
- Uten indekskurs for dagen står ingen verdi fra en annen dag i stedet.

#### FR-105 — Søylene under hovedindeksen

Under indeksen (FR-104) står én søyle per aksje med endringen for dagen eller
perioden, med bransjesymbolet og tickeren. Søylene står fra det største fallet til
den største stigningen.
Indeksens endring er en stiplet linje, grønn når indeksen steg og rød når den
falt.

- En aksje uten kurs for tabellens dag får ingen søyle, og siden sier hvilke som
  mangler. Mangler indeksen kurs, sier siden det over søylene.
- Bransjesymbolet er gult når aksjen har 3 av 3 (`designregler.md` §3).
- Søylene har en tekst for skjermleseren med alle tallene. De har også en lenke
  til samme dag eller periode i børsometeret.
- Ingen nye kall og ingen ny lagring: endringen er den i FR-101.

*Konsekvenser:*
- Antallet søyler er antallet aksjer med en endring for dagen.
- En aksje uten kurs dagen før navngis under søylene.
- Søylene står sortert fra den laveste til den høyeste endringen.
- Søylene og tabellen viser samme endring for samme aksje og periode.

#### FR-106 — Børsometeret

Børsometeret er en egen side, i stripa mellom Markedsoversikt og Min liste. Det
viser lista som er aktiv som et kart, med én rute per aksje, ordnet etter
bransje. Fargen viser endringen, størrelsen viser volumet mot vanlig, og rammen
viser signalet. En aksje med 3 av 3 har gul ramme. Ved navnet på bransjen står
snittet av endringen. En bransje med én aksje merkes «1 aksje». Siden har
periodevalget fra FR-101, forklaringen «Slik leser du børsometeret» og en tabell
med de samme tallene. Den gjør ingen nye kall, og ingenting nytt lagres.

*Konsekvenser:*
- Snittet for en bransje er snittet av endringene i FR-101 for aksjene i bransjen.
- Antallet ruter er antallet aksjer i lista. En aksje uten kurser har «Ingen kurser ennå», og en uten kurs den dagen har «Ingen kurs».
- Tabellen og rutene viser samme endring.

#### FR-107 — Endret signalstyrke siden forrige børsdag

*Ikke i v1. Det kan komme senere, og teksten under er planen (§2, §8).*

Når signalstyrken har endret seg siden forrige lagrede børsdag, står et lite
merke under den, for eksempel «var 1 mandag». Det står i markedsoversikten og i
Min liste. Ukedagen er forrige børsdag i norsk tid. Merket regnes av lagrede
vurderinger og aldri på nytt (FR-408). Det har ingen pil, fordi pilene står for
retning (FR-103). Mangler den forrige raden, eller har den en grunn, står det
ikke noe merke. Merket skjules når en sammenligning med en annen dag er valgt.

*Konsekvenser:*
- Med styrke 1 forrige børsdag og 3 i dag står «var 1 <ukedag>».
- Med samme styrke, en forrige rad med grunn eller ingen forrige rad står ingenting.

#### FR-108 — Filter på signalet

Filteret er tatt bort 11.11, etter gruppens ønske. Raden «Alle», «3 av 3
positiv» og «3 av 3 negativ» viste ikke noe tabellen ikke alt viser under
«Skilte seg ut». Med raden gikk også linja om filteret og lenken til dem som
fikk 2 av 3. Over tabellen står nå bare «Alle» og «Min liste» (FR-111). At
signalstyrken ikke er et råd om å kjøpe eller selge, står fortsatt i
innledningen på oversikten (NFR-06).

*Konsekvenser:*
- Oversikten og Min liste har ikke noe valg for signalet, og adressen leser ikke `?signal=`.
- Over tabellen står bare «Alle» og «Min liste», med antallet.
- Innledningen på oversikten sier at signalstyrken ikke er et råd.

#### FR-109 — Hjelpen på sidene

All hjelp er fast tekst vi har skrevet og kontrollert. Ingen KI og ingen
nettkall når siden vises. Tall i teksten hentes fra parametrene beregningen
bruker. Da kan ikke hjelpen si én ting mens koden gjør en annen.

- **Hjelpen bak «?».** Et «?» ved det som forklares, åpner en kort tekst, og et
  nytt trykk lukker den.
- **«Vis meg rundt».** Hver side har en liste med stegene på siden. «Spill av
  omvisningen» går gjennom oversikten, en aksjeside, børsometeret, Min liste,
  «Følg en aksje» og Innstillinger. Den går ett steg om gangen, med «Tilbake»,
  «Neste» og «Lukk».
- **Knappene øverst.** «Vis meg rundt» og «Spill av omvisningen» står i raden
  øverst på sidene når «Vis hjelp» er på. Et trykk starter omvisningen med en
  gang, uten spørsmål. «Vis meg rundt» viser stegene på siden, og «Spill av
  omvisningen» hele omvisningen.
- **Tilbudet.** Første gang oversikten åpnes, tilbyr den «Vis meg rundt» øverst
  på siden, med knappene «Vis meg rundt» og «Nei takk». Et ja starter «Vis meg
  rundt» for oversikten. Et nei gjelder bare tilbudet: det kommer ikke igjen,
  og knappene øverst står som før. Svaret huskes i nettleseren.
- **«Lær noe nytt».** Ikke i v1, men kan komme senere. Planen er en liten boks i
  oversikten med ett tips per dag, fra en fast liste. KI kan skrive utkast, men
  hvert tips kontrolleres og rettes av en av oss før det tas inn. Tipset er
  merket med hvem og når. Dagens tips velges etter en regel i koden, ut fra
  datoen eller dagens tall.

Hjelpen og omvisningen skjules når «Vis hjelp» er av (FR-110). Ingen tekst kan
leses som et råd (NFR-06).

*Konsekvenser:*
- Hvert tall i hjelpen er lik parameteren i beregningen.
- Hvert steg i omvisningen peker på noe som finnes på siden.
- Ingen hjelpetekst har et ord fra rådlista.
- Et nei til tilbudet gir ikke tilbudet igjen, og knappene øverst står fortsatt.
- Et trykk på «Vis meg rundt» eller «Spill av omvisningen» starter omvisningen uten spørsmål.
- Med «Vis hjelp» av står verken knappene eller tilbudet på siden.

#### FR-110 — Innstillinger

Knappen «Innstillinger» står i stripa på alle sider. Siden har bryterne «Vis
hjelp», «Vis KI-tekst» og «Vis notater», under overskriftene «Hjelp»,
«KI-tekst» og «Notater». Hver bryter viser «På» eller «Av». Valgene gjelder alle
sidene, lagres i basen og overlever en omstart. Det er ingen innlogging, så valgene gjelder
maskinen. Bryteren ved hver KI-tekst (FR-601) styrer det samme valget som «Vis
KI-tekst», så de to viser aldri hver sin verdi.

*Konsekvenser:*
- Et valg som slås av, er av på alle sidene og etter en omstart.
- Bryteren ved KI-teksten og bryteren i Innstillinger viser samme verdi.

#### FR-111 — Min liste

Min liste er en egen side i stripa. Den har samme tabell som oversikten, i samme
rekkefølge og med de samme kolonnene (FR-101, FR-102). Den viser bare aksjene
brukeren har merket med stjernen. «Alle / Min liste» viser hele lista med
stjernene. «Min liste» over tabellen på oversikten filtrerer den samme tabellen.
Stjernen står foran hvert selskap. Et klikk merker aksjen eller tar merket bort.
Brukeren kommer så tilbake til samme side og samme rad, med samme sortering. Uten noe merket sier
siden hvordan man merker.

Merket lagres i basen, gjelder maskinen og overlever en omstart. Webserveren
skriver bare merket og henter aldri (NFR-02). Min liste har periodevalget med
«Sammenlign siste børsdag med». Notatene står samlet nederst under «Mine
notater» når «Vis notater» er på (FR-110). Da står også knappen «Mine notater» i
raden øverst på alle sidene. På en bred skjerm åpner den notatene i et panel ved
siden av siden, og ellers går den til notatene i Min liste. Min liste er et utvalg av lista
(FR-412), ikke en egen henting og ikke en portefølje.

*Konsekvenser:*
- En merket aksje står i Min liste, og en umerket står ikke der.
- Med «Alle» står alle aksjene i lista.
- Merket står etter en omstart.
- Et klikk på stjernen gjør ingen API-kall og går tilbake til samme side med sorteringen.
- Et merke for en aksje som ikke er i lista, avvises med en feil (400).

#### FR-407 — Merking av utbyttedager

Et utbytte skal ikke se ut som et kursfall. Endringen regnes derfor på den
justerte sluttkursen, mens oversikten viser sluttkursen (se ordlista). På dagen
kilden har regnet de eldre kursene om, stemmer ikke differansen mellom to
sluttkurser med prosenten. Dagen merkes derfor som **justeringsdag**, så avviket
er forklart.

En justeringsdag finnes av kursserien alene. Endringen på sluttkursen og
endringen på den justerte sluttkursen skiller seg da med mer enn 0,1
prosentpoeng (`begrunnelser.md` §11). Metoden ser justeringer, ikke utbytter, og
en splitt gir samme utslag. Derfor sier appen «justeringsdag», ikke «utbytte».

- Oversikten merker endringen «justeringsdag» for dagen.
- Aksjesiden forklarer merket ved endringen. Den markerer justeringsdagene i
  perioden kursgrafen viser. Den sier hvor mange det var det siste året og datoen
  for den siste, eller at det ikke var noen.
- Historikken sier ingenting om neste justering (NFR-06).

*Konsekvenser:*
- En serie der sluttkursen falt 3 % og den justerte sluttkursen 0 %, gir en justeringsdag.
- Et avvik på 0,1 prosentpoeng eller mindre gir det ikke.
- Ordet «utbytte» står ikke ved merket.
- Med 1 år valgt er antallet i teksten antallet markerte dager i grafen.

---

### 4.2 Aksjedetaljen

<a name="fr-201--kursgraf-med-seks-måneders-historikk"></a>

#### FR-201 — Kursgraf med periodevalg

Kursgrafen har periodevalget fra FR-101, med de samme knappene: siste børsdag,
1 uke, 1 mnd, 3 mnd, 6 mnd, I år og 1 år, og datofeltet med «Vis dagen». Grafen
åpner med 6 mnd. Siste børsdag og en dag valgt i datofeltet viser 6 mnd fram til
dagen. Dagen er merket, med endringen den dagen og signalet som er lagret for
den. Startdagen for hver periode er den samme i oversikten og grafen. Regelen
testes med faste datoer rundt helger, helligdager og nyttår (NFR-08). Har serien
færre dager enn perioden, tegnes det som finnes, med datoene på aksen.

**Grafen tegnes på den justerte sluttkursen**, både kurslinja og MA50-linja i
FR-202.

Med en dag valgt i datofeltet viser hele aksjesiden den dagen. Kortene øverst,
sjekkene, KI-teksten og grafen leses fra det som er lagret for dagen. Øverst står
«Siden viser <dag>, ikke siste børsdag» og en lenke tilbake. Signalet regnes
aldri på nytt (FR-408).

*Konsekvenser:*
- 6 mnd er valgt når siden åpnes.
- Startdagen for 1 mnd er den samme på aksjesiden og i oversikten for samme dag.
- Med 100 dager i serien og 1 år valgt tegnes de 100 dagene og ingen tomme dager foran.
- Med en dag valgt viser sjekkene den lagrede vurderingen for dagen, og grafen viser 6 mnd fram til den, med dagen merket.

#### FR-202 — MA50-linjen tegnes oppå kursen

Grafen tegner kursen og 50-dagers glidende snitt («50-dagers snitt (sjekk 1)»).
Hovedindeksen står som en stiplet linje, regnet om så den starter på aksjens
kurs. **Kurslinja og MA50 tegnes på samme serie, den justerte sluttkursen.**
Tegnforklaringen sier at kursen er justert for utbytte. Begrunnelse: grafen
finnes for å forklare signalet. En annen serie enn den signalet bruker, ville
forklart noe annet enn det som skjedde (`begrunnelser.md` §13).

Sjekk 2 og 3 er også synlige. Under kursen står volumsøyler med to streker: én
for medianvolumet og én for grensen sjekk 3 slår ut ved. De regnes med samme
funksjon, samme vindu og samme faktor som sjekken. Rundt forrige dags kurs står
et bånd med standardavviket fra sjekk 2. Tallene hentes fra parametrene
beregningen bruker. Mangler volumet, eller er medianen 0, tegnes ikke streken, og
grafen sier det (NFR-08). Detaljene står bak «Mer om grafen».

*Konsekvenser:*
- MA50 i grafen er lik snittet trendsjekken brukte for samme dag.
- Grensestreken er 1,5 × medianen sjekk 3 brukte.
- Med median 0 finnes ingen grensestrek, og en tekst sier hvorfor.
- Markedsoversikten viser sluttkursen og grafen den justerte, og tegnforklaringen sier det.

#### FR-203 — Øvrig innhold

Aksjesiden viser i tillegg:

- Lenken «Markedsoversikt» tilbake til oversikten (FR-101)
- Tickeren ved selskapsnavnet, for eksempel EQNR
- De tre sjekkene ved navn under «Hvorfor signalet ble N», med verdien hver av
  dem ga og målingen bak den (FR-706)
- Rammen «Signalet forklart» etter kursgrafen, med appens setninger om
  sjekkene og bryteren, og KI-teksten når KI er på (FR-602)
- «Signalet dag for dag», de lagrede vurderingene måned for måned, med skillet i
  FR-409
- Lenken til selskapets investorside. Den åpnes i nettleseren og hentes aldri av
  programmet. I demoen går den til en oppdiktet investorside i appen. Appen
  lenker ikke til Euronexts nettsteder, fordi vilkårene forbyr lenker uten
  tillatelse (`docs/kilder-og-rettigheter.md`)
- Notatene, når «Vis notater» er på (FR-110)
- Høy og lav for dagen ved sluttkursen, og endringen i kroner ved prosenten. Det
  er ikke i v1, men kan komme senere. Planen er at høy og lav bare vises når
  begge finnes og lav ≤ sluttkurs ≤ høy, ellers «–» (NFR-08). De tegnes ikke i
  grafen

*Konsekvenser:*
- Aksjesiden har alle tre sjekkene, også når de ga 0.
- Lenken til investorsiden åpnes i en ny fane i den ekte versjonen.
- Lenken peker aldri til `newsweb.oslobors.no`, `oslobors.no` eller `live.euronext.com`.
- Ingen kode i `src/` henter fra investorsiden.

#### FR-204 — Aksjedetaljen for en aksje uten gyldig signal

Signalet krever 51 handelsdager (FR-701). Har en aksje kortere historikk, eller
hull i serien, kan det ikke regnes. Aksjesiden svarer da som vanlig:

| Tilfelle | Hva brukeren får | Hva siden viser |
|---|---|---|
| For kort serie | Aksjesiden | Grafen så langt dataene rekker, uten MA50 når snittet ikke finnes, og «Signalet kunne ikke regnes» med antallet dager. Ingen sjekker |
| Hull i en lang nok serie | Aksjesiden | Grafen, og at det ikke finnes noen vurdering for dagen fordi signalet ikke kunne regnes |
| Aksje i lista uten en eneste kurs | Aksjesiden | En beskjed om at det ikke finnes kurser ennå, uten graf og sjekker |
| Symbol utenfor lista | Siden finnes ikke | — |
| Base uten en eneste kurs, før første henting, eller demo uten demobase | Siden finnes ikke | — |
| Basen kan ikke leses | En feilside | — |

**Kursen finnes selv om snittet ikke kan regnes**, og da vises den. Begrunnelse:
svarer appen at siden ikke finnes, sier det at aksjen ikke finnes. NFR-03 sier at manglende
data for én aksje ikke stopper hovedflyten.

*Konsekvenser:*
- En aksje med 30 dager gir aksjesiden, en graf uten MA50 og grunnen med antallet dager.
- En aksje i lista uten kurser gir aksjesiden.
- Et symbol utenfor lista gir en side som ikke finnes.

#### FR-205 — Se nærmere

*Ikke i v1. Det kan komme senere, og teksten under er planen (§2, §8).*

Aksjesiden har delen «Se nærmere», rett under kursgrafen. Den har tre spørsmål
brukeren kan sjekke selv, og den gir ikke råd (NFR-06). Svarene regnes av tall
appen allerede har. Den gjør ingen nye kall, og ingenting nytt lagres. Grensene
står i parametrene beregningen bruker.

1. «Børsen, bransjen eller selskapet?»: aksjens endring mot hovedindeksen og mot
   snittet av de andre i samme bransje i lista. Svarene er «Børsen», «Bransjen»,
   «Selskapet», «Selskapet eller bransjen» når aksjen er alene i bransjen, og
   «Liten bevegelse». Svaret sier hvor bevegelsen ser ut til å komme fra, ikke
   hvorfor.
2. «Står det noe i børsmeldingene?»: lenken til investorsiden fra FR-203.
3. «Er en slik dag vanlig for aksjen?»: dagens endring mot standardavviket, og
   volumet mot medianen, slik de er lagret i vurderingen (FR-408).

Mangler et tall, står grunnen, ikke et gjettet svar (NFR-03).

*Konsekvenser:*
- Med aksjen og indeksen ned like mye er svaret «Børsen».
- Uten hovedindeksen for dagen står grunnen i stedet for et svar.

#### FR-206 — Signaldager i kursgrafen

Kursgrafen markerer dagene der den lagrede vurderingen hadde styrke på terskelen
eller over (FR-705). Hver retning har sin form, og 3 av 3 har en gul ring.
Markeringen leses fra de lagrede vurderingene, og signalet regnes aldri på nytt
(FR-408). Grafen sier fra hvilken dato markeringene finnes. En dag med grunn, en
dag uten rad og en dag som ikke er børsdag, markeres ikke. De ser aldri ut som
styrke 0 (FR-409). En dag med signalet regnet i ettertid har hvit midte og stiplet
kant, og teksten under grafen sier det.

*Konsekvenser:*
- En dag med styrke 2 markeres, og en med 1 markeres ikke.
- En dag med grunn markeres ikke.
- Før første lagrede vurdering finnes ingen markering, og teksten sier datoen.

#### FR-207 — Kommende eks.dato i kursgrafen

*Ikke i v1. Det kan komme senere, og teksten under er planen (§2, §8).*

Kursgrafen viser neste eks.dato som er ført inn (FR-414), med datoen den ble
sjekket. Er den sjekket for mer enn 7 dager siden, vises den i grått med
«sjekket <dato>, kan være endret». En dato som har passert uten at kursserien
viser en justering (FR-407), merkes «ikke bekreftet». Ingen dato vises uten at
den er sjekket (NFR-08), og uten dato står det ingenting. I demoen er datoene
oppdiktet og merket «Eksempeltall» (FR-411).

*Konsekvenser:*
- En dato sjekket for 8 dager siden er grå, med teksten.
- En dato uten sjekkdato vises ikke.

---

### 4.4 Datahenting og oppdatering

Kommende finansielle hendelser (4.3) er plan A og står i vedlegg A.

#### FR-401 — Henting utløses eksplisitt, aldri av en oppstart

Henting er en egen, bevisst handling: hentekommandoen. **Webserveren henter
aldri.** Den starter uten å bruke et eneste API-kall og viser siste kjente data
med tidsstempel. Finnes ingen data ennå, viser den en tom tilstand som forklarer
hvordan henting gjøres, ikke en feil.

Hentekommandoen:

1. nekter på en børsdag før kl. 22:00 norsk tid. Før det er dagens rad ikke
   endelig, og en vurdering kan ikke skrives om (`malinger.md` §37). Unntaket fra
   sperren er første henting i en tom base, som henter forrige børsdag (FR-402)
2. tar i bruk endringene i lista brukeren har bedt om (FR-412)
3. sjekker basen først. Har den kursene for børsdagen for alle i lista, gjøres
   ingen kall til kursene (FR-402). Det som mangler av hovedindeksen,
   vurderingene og KI-tekstene, gjøres for seg
4. sjekker kvoten (NFR-01), henter kursene for aksjene og så hovedindeksen, og
   skriver rådata (NFR-07) og basen (FR-406, FR-410)
5. skriver dagens vurderinger (FR-408) og så KI-tekstene, også teksten om dagen
   (FR-602, FR-607)
6. regner til slutt signalet i ettertid for børsdagene uten vurdering (FR-408).
   En feil der stopper ikke kvelden

**Kveldsjobben.** Oppgaveplanlegging på en PC i gruppen starter hentekommandoen
hver dag kl. 22:15, og igjen kl. 22:45, 23:15 og 23:45. Den kjører fra en egen
arbeidskopi av main, på commiten main hadde ved midnatt. Tapte kjøringer tas
ikke igjen. Først sjekker jobben om børsdagen alt er ferdig, med basen bare for
lesing og uten kall. Er den det, startes verken Docker Desktop eller den lokale
modellen. Etter hentingen måler jobben omsetning med kallene som er igjen
(FR-413). Loggen skrives under `data/`.

**«Start den ekte versjonen»** kjører hentekommandoen før webserveren, og
dobbeltklikket er den bevisste handlingen. Er det ingenting nytt å hente, gir det
0 kall. I en mappe med `.git` starter ikke den ekte versjonen. Da henter et
dobbeltklikk i en klon aldri med gruppens nøkkel.

Begrunnelse: en container startes på nytt hver gang. Henting ved oppstart ville
brukt ett kall per aksje og ett for indeksen ved hver start, 16 med 15 aksjer,
mot en dagskvote på 20.

*Konsekvenser:*
- Å starte webserveren gir 0 kall.
- En kjøring på en børsdag kl. 21:59 gir 0 kall og en melding.
- To kjøringer samme kveld gir kall bare i den første.
- I en mappe med `.git` nekter den ekte versjonen å starte.

#### FR-402 — Kontroll mot forventet børsdag, ikke mot klokkeslett

Hentingen antar ikke at data er ferske fordi klokka har passert et tidspunkt.
Den kontrollerer at svaret har raden for forventet børsdag. Mangler raden for en
aksje, får aksjen ingen vurdering. Den får i stedet en rad med grunnen «kurs ikke
fra dagen» (FR-408), og hentingen prøves igjen ved neste kjøring. Applikasjonen
viser aldri gårsdagens tall som dagens.

Forventet børsdag er siste børsdag på eller før dagens dato i norsk tid. En
børsdag er mandag–fredag som Oslo Børs ikke har stengt. De stengte dagene regnes
ut for hvert år fra 2026 etter reglene børsen følger, med påsken regnet ut.
Euronexts lister for 2026 og 2027 er tester regelen må stemme med. Halve
handelsdager er børsdager. Når basen er tom, henter første henting siste
fullførte børsdag, også på dagtid en hverdag (FR-408).

*Konsekvenser:*
- Et svar der nyeste dato er gårsdagen, gir en rad med grunn og ingen vurdering.
- 2027-03-25 er ikke børsdag, og 2027-03-24 er det.
- En dato før 2026 gir en feil i stedet for en gjetning.

#### FR-403 — Etterfylling av kurser etter dager uten bruk

Kjører ingen hentekommandoen på flere dager, fylles hullet i kursserien ved neste
henting, uten ekstra kall. EODHD tar en fra-dato og en til-dato, og ett kall
koster det samme uansett hvor langt intervallet er. Hver henting erstatter
symbolets serie (FR-406), så et hull fylles uansett. Mangler bare hovedindeksen
dagen, hentes den alene med ett kall, også i helgen, og aldri med bonuskvoten.

*Konsekvenser:*
- En base som mangler fire dager, har alle fire etter én henting, med samme antall kall som en vanlig henting.

#### FR-406 — To lagre for kursdata, med hvert sitt ansvar

Kursdata lagres i to atskilte lagre som aldri blandes:

| Lager | Innhold | Regel |
|---|---|---|
| **Beregningsgrunnlag** | Serien signalberegningen leser, i databasen | Erstattes i sin helhet ved hver henting, per symbol, i én transaksjon. Skjøtes aldri på |
| **Rådata** | Øyeblikksbilder med tidsstempel per henting, som filer | Skrives aldri om. Dokumentasjon og sikkerhetsnett, ikke beregningskilde |

Serien skjøtes aldri på. Grunnen er at EODHD regner `adjusted_close` om bakover
ved hvert nytt utbytte. En eldre fil skriver aldri over en nyere serie. Dette er ikke et krav om
å hente oftere. Kravet gjelder hva en henting gjør når den først skjer.

##### Minste historikk: 175 handelsdager

Hver henting dekker **minst 175 handelsdager** per symbol: 125 for seks måneder
i grafen (FR-201) og 50 til. Da finnes MA50 på første punkt når grafen viser 6
mnd (FR-202). Med 1 år valgt begynner MA50-linja etter de første 50 dagene i
serien. **I praksis hentes et helt år.** Ett kall koster det samme uansett
intervall (`malinger.md` §2), og gratisnivået gir ett år.

*Konsekvenser:*
- Etter en henting har basen for hvert symbol nøyaktig radene i siste svar, også når svaret har en annen `adjusted_close` for en gammel dag.
- En henting som feiler midt i et symbol, etterlater den gamle serien hel.
- Rådatafila for en henting skrives ikke over av neste.

#### FR-408 — Dagens vurdering lagres per aksje

Hver gang hentekommandoen kjøres, lagres vurderingen per aksje for børsdagen,
slik den var:

| Felt | Innhold |
|---|---|
| Dato | Børsdagen vurderingen gjelder |
| Signalstyrke | 0–3 |
| Retning | Positiv, Negativ, Blandet eller Ingen |
| De tre sjekkene | Verdien hver av trend, bevegelse og interesse ga |
| Målingene | Tallet hver sjekk ble avgjort av: avviket fra MA50, dagens endring og standardavviket den måles mot, og volumet som forholdstall mot medianen. Uavrundet, som brøk, i samme enhet som regelen regner i. Forholdstallet mangler bare når medianvolumet er 0, og da er interesse 0 |
| Kurs | `close` og `adjusted_close` |
| Grunn | Bare når vurderingen mangler: symbolet feilet, kursen var ikke fra dagen, eller signalet kunne ikke regnes |

Målingene lagres, så en vurdering kan regnes etter fra raden alene, med
parametrene som gjaldt den dagen (`malinger.md`). Dette er et tredje lager, ved
siden av de to i FR-406. De lagrer data fra kilden, og dette lagrer hva
løsningen mente om dem. Vurderingen lagres i samme kjøring som hentingen.
Ingenting skrives uten at kommandoen kjøres (FR-401).

##### Kveldens vurdering etterfylles ikke, og det er med vilje

| | Kan etterfylles? | Hvorfor |
|---|---|---|
| **Kurs** for 12.09 | **Ja** | Den er den samme uansett når den hentes |
| **Kveldens vurdering** for 12.09 | **Nei** | En vurdering skrevet i dag for 12.09 ville vært *dagens* parametres svar, ikke datidens |
| **Signalet i ettertid** for 12.09 | **Ja, merket** | Det regnes av kursene til og med 12.09, er merket «i ettertid» og vises aldri som kveldens vurdering. Ingen KI-tekst |

Lageret for kveldens vurderinger avviser enhver dato som ikke er inneværende
børsdag. Det ene unntaket er første henting på dagtid i en tom base. Den skriver
vurderingene og KI-tekstene for børsdagen rett før, én gang. Spørsmålet «hva sa
løsningen om EQNR for to uker siden?» besvares av «Signalet dag for dag» på
aksjesiden (FR-203).

**Signalet regnet i ettertid.** Til slutt i hver henting, etter kveldens
vurderinger og KI-tekster, regnes signalet for hver børsdag med kurser i basen,
for aksjene i lista, når dagen mangler vurdering og aksjen har like mange
kursdager til og med dagen som kvelden krever. Det regnes bare med kursene til og
med dagen, aldri for inneværende børsdag, og ingen rad fra kvelden, heller ikke en
rad med grunn, skrives over. Raden er merket i basen, får ingen KI-tekst, og
KI-grunnlaget leser bare radene fra kvelden. En kommando regner radene i ettertid
på nytt eller sletter dem, uten å røre radene fra kvelden. En feil stopper ikke
hentingen (NFR-03).

*Konsekvenser:*
- Å skrive en vurdering fra kvelden for en tidligere børsdag gir en feil, utenom første henting i en tom base.
- En rad med grunn skriver aldri over en rad med vurdering samme dag.
- Målingene på raden gir samme fortegn som sjekkene med parametrene for dagen.
- Signalet i ettertid for en dag er det samme som det som regnes med kursene etter dagen fjernet.
- En dag med for få kurser, og inneværende børsdag, får ikke signalet i ettertid.
- Å regne radene i ettertid på nytt eller slette dem endrer ingen rad fra kvelden.

#### FR-409 — De tre tilstandene skal være skillbare i lageret

Lageret skiller tilstandene for en aksje og en dag **entydig**:

| Tilstand | Hva det betyr |
|---|---|
| Rad med vurdering fra kvelden, også styrke 0 | **Et gyldig svar.** Med 0 ga sjekkene ingen utslag |
| Rad med vurdering regnet i ettertid | **Et gyldig svar, merket «i ettertid».** Kvelden skrev ingen vurdering, og signalet er regnet senere av kursene til og med dagen. Ingen KI-tekst |
| Rad med grunn | Kjøringen kunne ikke vurdere aksjen, og grunnen står |
| Ingen rad, og dagen var en børsdag | **Kommandoen ble ikke kjørt,** og signalet er ikke regnet i ettertid, fordi aksjen hadde for få kurser eller dagen er inneværende børsdag. Et hull i vår egen drift |
| Ingen rad, og dagen var ikke en børsdag | Dagen finnes ikke, og telles ikke |
| Ingen rad etter at aksjen ble tatt ut av lista | «Ikke i lista», ikke et hull |

Enhver visning, kommando eller spørring som leser historikken, **bevarer
skillet**. «Ingen rad» og «styrke 0» vises aldri som samme tilstand. Begrunnelse:
uten skillet kan en dag vi ikke kjørte, ikke skilles fra en dag uten utslag, og
det kan ikke gjenskapes i ettertid. Det første er en mangel hos oss, og det
andre er et funn om markedet. FR-204 gjelder en aksje som ikke kan vurderes nå.
FR-409 gjelder den lagrede raden for en dag som har passert.

*Konsekvenser:*
- En dag uten rad på en børsdag gir «ikke kjørt».
- En dag med signalet regnet i ettertid er merket «i ettertid» overalt der den vises.
- En helgedag gir «ikke børsdag».
- En dag etter at aksjen gikk ut, gir «ikke i lista».
- Ingen av dem vises som 0 i «Signalet dag for dag», i signaldagene (FR-206) eller i oversikten.

#### FR-410 — Hovedindeksen hentes i samme kjøring

Hentekommandoen henter hovedindeksen OSEBX med ett kall per kjøring, med samme
intervall som aksjene. En henting koster da antallet aksjer pluss én (NFR-01).

- Rådata lagres i samme øyeblikksbilde som aksjene, under en egen nøkkel.
- Indeksen lagres for seg, aldri blant aksjene eller vurderingene. Den kan bygges
  opp igjen fra kilden.
- Bare børsdager lagres, fra 2026, uten et fast sluttår.
- Webserveren henter aldri indeksen.
- Feiler indekskallet, lagres og vurderes aksjene som vanlig. Indeksen gir aldri
  en vurdering.

*Konsekvenser:*
- En henting med 15 aksjer bruker 16 kall.
- Et feilet indekskall gir 15 vurderinger og ingen indeksrad.
- En lørdag i svaret lagres ikke.

#### FR-411 — Demoversjonen har oppdiktede tall i en egen base

Appen kan vises fram uten EODHD-nøkkel og uten data fra EODHD. Demoen er
hovedveien for faglærer og sensor, fordi sensuren ikke skal avhenge av at noen
oppretter konto hos en ekstern tjeneste (`docs/innlevering.md`). En egen
kommando lager demobasen.

- Kommandoen gjør null API-kall, leser ingen nøkkel og virker uten nett.
- Selskapene, tickerne og hovedindeksen er oppdiktet, med navn som ikke finnes på
  Oslo Børs.
- Kursene lages etter en regel som står skrevet. Tilfeldighetene starter fra et
  fast tall, så samme kommando gir samme base. Serien er lang nok til alt sidene
  viser, også MA50 fra grafens første punkt.
- Vurderingene regnes med den samme beregningen som hentekommandoen bruker.
- Basen er merket som demobase, og hver side som viser den, sier
  «Eksempeltall» (NFR-08). Merket avgjøres av basen. En demobase vises derfor
  aldri uten merket, og en ekte base aldri med det.
- Demokommandoen nekter å skrive til en base uten demomerket. Hentekommandoen
  nekter å skrive til en demobase.
- Én bryter avgjør hvilken base webserveren åpner, og webserveren lager aldri
  demobasen selv. Mangler demobasen, viser siden kommandoen som lager den.
- Demobasen ligger aldri i imaget eller i repoet.
- Alt brukeren ser i v1, kan vises i demoen, også KI av og på, med ferdige
  KI-tekster. Kan demoen ikke gjøre det samme fordi den ikke henter, sier en kort
  tekst hvordan det er i den ekte versjonen, for eksempel at et valg står som
  «Venter på henting». Demoen viser ikke et eksempel når ingen endring venter.
  Lista i demoen kan byttes, men det hentes aldri.

*Konsekvenser:*
- Demokommandoen kjørt to ganger gir byte for byte samme kurser.
- Hver side fra demobasen har «Eksempeltall».
- Hentekommandoen mot demobasen nekter og bruker 0 kall.
- Demokommandoen mot en base uten merket nekter.

#### FR-412 — Lista over aksjer

Lista har opptil 18 aksjer, valgt fritt. De 15 i §3 er lista appen starter med.
Aksjer kan legges til og tas ut, og lista kan byttes med en ferdig liste. Siden
viser plassene som er brukt, for eksempel «Appen følger 16 av 18, 2 plasser
ledige.». En nittende
avvises med en forklaring. En aksje brukeren har valgt selv, merkes «Egen».

- En endring tas i bruk ved neste henting, på en børsdag. Webserveren skriver bare
  ønsket og henter aldri, og siden sier at endringen venter.
- En aksje som tas ut, beholder kursene og vurderingene sine og er «ikke i lista»
  fra den dagen (FR-409). Tas den inn igjen, begynner kveldens vurderinger på
  nytt, og dagene mellom får signalet regnet i ettertid når kursene finnes, merket
  (FR-408).
- En ticker som ikke gir rader ved hentingen, tas ikke inn, og utskriften sier
  det.
- Er omsetningen målt fra før (FR-413), vises den før brukeren velger.
- En aksje som omsettes for mindre enn 32 MNOK om dagen, eller ikke er målt,
  merkes «Utenfor målingen» i grått. Gult betyr 3 av 3 (`designregler.md` §3).
  Grensene i signalet gjelder uendret.
- Ingen forslag fra KI om hvilke aksjer man bør følge (NFR-06).

**Ferdige lister:** de 15 i §3, «De 15 mest omsatte» på hele børsen, og én liste
per bransje med de opptil 18 med høyest målt omsetning. «De 15 mest omsatte» står
først blant de ferdige listene i «Din egen liste», og hver aksje står med sin
egen bransje. «De 15 mest omsatte»
regnes av den samme målingen som bransjelistene, bare med målte aksjer. Den har
ikke kravet om minst åtte bransjer i §3. En liste vi ikke har målt, står ikke
som ferdig liste.

*Konsekvenser:*
- Med 18 aksjer avvises den nittende, og lista er uendret.
- Et ønske endrer ikke lista før hentingen.
- En aksje med 20 MNOK er merket «Utenfor målingen» overalt der den vises.
- Ingen ferdig liste har mer enn 18.
- «De 15 mest omsatte» har bare målte aksjer, de med høyest målt omsetning først.

#### FR-413 — Måling av omsetning

Hentekommandoen har et eget valg som måler median omsetning for aksjer på Oslo
Børs. Den regnes som i §3: volum × sluttkurs per handelsdag, med medianen over
tre måneder bakover fra børsdagen. Tallet og datoen lagres i basen. Rådata
skrives under `data/` og legges aldri i repoet.

- Den kjøres av kveldsjobben etter hentingen, eller for hånd, aldri fra
  webserveren.
- Den nekter hvis kveldens henting ikke er ferdig, og venter på manglende kurser
  til kl. 23:45. Hentingen og nye forsøk får kallene først.
- Den leser kvoten før første kall og sier hvor mange kall den bruker. Den
  bruker kallene som er igjen den dagen i GMT, også på dager børsen er stengt.
- Først måles aksjene som aldri er målt, uten aksjene i lista. Så måles aksjene
  med den eldste målingen. Datoen står ved hvert tall.
- Den bruker ikke bonuskvoten, og den stopper hvis bonuskvoten endrer seg. Ett
  unntak ble avgjort for kjøringen 10.11. Et eget valg brukte da bonuskvoten til
  aksjene som manglet en måling, og lot minst 200 kall stå igjen i den. Valget
  finnes fortsatt i koden (NFR-01).

*Konsekvenser:*
- Med 0 kall igjen gjøres ingen måling.
- En kjøring før hentingen er ferdig, gir 0 kall.
- Uten det egne valget endrer bonuskvoten seg aldri.

#### FR-414 — Eks.datoer ført for hånd

*Ikke i v1. Det kan komme senere, og teksten under er planen (§2, §8).*

Kommende eks.datoer føres inn for hånd fra selskapenes egne investorsider, med en
kommando. De lagres i basen og aldri i en fil i repoet, fordi kildedata for en
bestemt dag ikke skal ligge der. Hver dato har datoen den ble sjekket og hvor den
ble lest. Et selskap får ingen dato før vilkårene for nettstedet er lest og ført
i `docs/kilder-og-rettigheter.md`. Sidene leses av en av oss og hentes aldri av
programmet. Kommandoen gjør ingen nettkall, og webserveren skriver ikke tabellen.
Lista sjekkes minst én gang i uka, og dagen før en eks.dato.

Begrunnelse: kursserien finner dagen først når den har skjedd. EODHDs kalender
svarer 403 på gratisnivået, og Euronext er ute (`begrunnelser.md` §11).

*Konsekvenser:*
- Kommandoen gjør 0 nettkall.
- En dato uten sjekkdato eller kilde avvises.

---

### 4.6 KI-laget og grensen mot regelbasert kode

KI forklarer signalet med ord. Den gjør det for én aksje om gangen på aksjesiden,
og for hele børsdagen på forsiden. Regler regner, og KI formulerer. Bidraget er
**forståelighet, ikke informasjon**. Med bare våre egne resultater kan KI ikke
vite noe reglene ikke vet. Men den kan si det slik at en person forstår det
første gang.

**Grensen mot regelbasert kode.** Modellen får bare våre egne resultater:
fortegn, styrke, retning, antall og retningsord som steg, falt eller uendret. Den
får aldri kurser, volumer, prosenter eller forholdstall, og aldri rådata fra
kilden. Derfor trengs ikke en egen tillatelse fra EODHD
(`docs/kilder-og-rettigheter.md`, «Betingelse 4 og KI-tjenestene (2026-10-04)»).

Grunnlaget for én aksje er fortegnet for de tre sjekkene, styrken og retningen.
Når det finnes, får modellen også merket «Utenfor målingen», om aksjen steg, falt
eller sto stille, retningen på hovedindeksen og antallene bak mønstrene i
signalet. Teksten lages i hentekommandoen, ikke når siden vises (NFR-02). Den
står under regelforklaringen, aldri i stedet for den (FR-602).

#### FR-601 — Av/på-bryteren er brukersynlig

KI-teksten kan slås av og på fra grensesnittet, ved teksten og i Innstillinger
(FR-110). Én bryter styrer både teksten på aksjesiden og teksten om dagen på
forsiden (FR-607), uansett hvilken tjeneste som er valgt (FR-608). Bryteren er
ikke et utviklerflagg, fordi bidraget skal kunne vises fram mens noen ser på.

Med KI på sier siden hvorfor en tekst mangler:

- Har den siste børsdagen ingen tekster i loggen i den ekte versjonen, sier den
  at teksten lages når kursene hentes, på en maskin med en språkmodell, med
  lenken «Slik slår du den på».
- Har en tidligere dag ingen tekster i loggen, sier den at KI var av, eller at
  modellen ikke svarte da hentingen gikk.
- Svarte ikke modellen da hentingen gikk, sier den det.
- Har andre aksjer tekster for dagen, sier den at teksten for denne ikke ble
  laget.
- Ellers sier den om teksten ikke besto kontrollen, eller ikke stemmer med
  vurderingen.

*Konsekvenser:*
- Med KI av har aksjesiden og forsiden ingen KI-tekst og ingen melding om KI.
- Et klikk på bryteren ved teksten endrer valget i Innstillinger.
- En tidligere dag uten rader i loggen gir meldingen om at KI var av, eller at modellen ikke svarte.
- Den siste børsdagen uten rader i loggen gir lenken «Slik slår du den på».

#### FR-602 — Visningen når KI-laget er av

Med KI av er forklaringen på aksjesiden de tre sjekkene med verdiene og
målingene sine (FR-706), uten KI-tekst. Med KI på står KI-teksten **under**
regelforklaringen. Den er merket som laget av KI, med modellen og tjenesten, for
eksempel «gemma4:e4b, lokal». Regelforklaringen vises alltid, og KI-teksten
erstatter den aldri.

KI-teksten vises bare når grunnlaget i loggen (FR-604) stemmer med vurderingen
som vises: samme styrke, samme retning og samme fortegn for de tre sjekkene.
Ellers vises siden som en dag uten KI-tekst. Visningen stopper også en tekst med
ord fra en egen, kortere liste om kjøp, salg og anbefaling, selv om den besto
kontrollen.

*Konsekvenser:*
- Sjekkene er de samme med KI av og på, og det eneste som skiller sidene, er KI-teksten.
- En logget tekst med en annen styrke enn vurderingen vises ikke.
- Modellnavnet står ved hver tekst som vises.

#### FR-603 — KI-teksten sier ikke mer enn grunnlaget

KI-teksten kontrolleres mot grunnlaget som ble sendt, før den kan vises.
Kontrollen er én funksjon som bare sjekker teksten og ikke lagrer eller henter
noe. Hentekommandoen kaller den når teksten lages, og den testes med en falsk
modell. Den bygger på kjennetegn som kan observeres, ikke på en sikkerhetsscore
fra modellen:

1. **Retning og styrke.** Sier teksten hva retningen, styrken, en enkelt sjekk,
   hovedindeksen eller et mønster er, skal det være grunnlagets. Det sjekkes der
   teksten sier det, ikke som enkeltord. «Positiv» og «negativ» står naturlig i
   en tekst om retningen Blandet, og «ingen» er et vanlig ord.
2. **Tallene.** Bare antall fra grunnlaget og regelens faste tall, som 50 i MA50,
   er lov. Tall skrevet med ord sjekkes også. Desimaltall, prosent og enheter
   stoppes alltid.
3. **Råd.** Teksten har ingen ord fra rådlista i kontrollen, blant annet «bør»,
   «råd», «anbefal», «investerings-», «behold» og «verdt» (NFR-06).
4. **Gjetning.** Teksten har ingen ord som gjetter eller spår, som «trolig»,
   «sannsynligvis», «kan tyde på», «antyde» og «forventes». Den nevner ingen
   årsak som ikke står i grunnlaget, som nyheter, kontrakter eller rapporter.
   Ordet «resultat» står ikke i lista, fordi det i prøven viste til sjekkene. En
   forklaring av regelen selv er lov, som «fordi ingen sjekk ga utslag».
   Grunnlaget har ingen årsaker, så en årsak i teksten er alltid gjettet.

En tekst som ikke består, vises ikke, men logges med grunnen (FR-604). Siden
sier da at dagen er uten KI-tekst (FR-601).

**Kontrollen er grov.** Den fanger feil tall, feil retning og ord, men ikke en
misvisende tekst med riktige tall. Hvordan det kunne oppdages, er et åpent
refleksjonsspørsmål (§8).

*Konsekvenser:*
- Hvert ord i rådlista og gjetningslista stopper en tekst som ellers ville bestått.
- «Retningen er positiv» stoppes når grunnlaget sier blandet.
- «4,2 %» og «femti prosent» stoppes.
- En tekst som stoppes, har en rad i loggen med grunnen og vises ikke.

#### FR-604 — Logging av KI-bidraget, fra første kjøring

For hver aksje og børsdag KI-laget forklarer, og for teksten om dagen, lagres én
rad:

| Felt | Hvorfor |
|---|---|
| Aksje og børsdag | Det samme paret som vurderingen (FR-408), så teksten kan leses sammen med den |
| Grunnlaget som ble sendt | Det modellen faktisk så, ikke det som står i vurderingen etterpå |
| KI-teksten | Selve bidraget |
| Om teksten besto kontrollen i FR-603, og ellers hvorfor ikke | En tekst som ikke vises, skal fortsatt finnes |
| Promptversjon, tjeneste, modell, modell-ID, seed, temperatur, om modellen kjørte med eller uten grafikkort, og Ollama-versjonen for den lokale | To tekster kan bare sammenlignes når dette er kjent (`malinger.md` §19, FR-605) |

Det er én rad per aksje og børsdag, også når modellen feiler for en aksje. Da har
raden ingen tekst og sier at modellen feilet (NFR-04). Finnes raden, kalles ikke
modellen på nytt. En rad kan verken endres eller slettes. Loggen skrives i
hentekommandoen, og siden skriver aldri i den.

Hentingen sjekker den lokale modellen før første tekst. Svarer den ikke i det
hele tatt, skrives ingen rader for dagen. Utskriften sier da at samme kommando
kan kjøres igjen samme kveld, med 0 kall til EODHD.

Loggingen startet ved første kjøring, ikke da eksempelsettet skulle lages. Ble
loggingen slått på i etterkant, ville ikke uka som SM-8 krever, finnes.

*Konsekvenser:*
- En modell som feiler, gir en rad uten tekst.
- Å kjøre hentingen to ganger samme dag gir ikke en ny rad og ikke et nytt kall til modellen.
- En oppdatering eller sletting av en rad i loggen feiler.

#### FR-605 — Promptversjon og modell lagres med hver KI-tekst

Hver lagret KI-tekst har promptversjonen og modellen som laget den, med feltene i
FR-604. Ellers blandes den sammen med vurderingen i FR-408, som er regelens og
ikke KI-ens. Da ville et eksempelsett blitt en blanding av flere systemer som ser
ut som ett.

*Konsekvenser:*
- Hver rad i loggen har promptversjon, tjeneste og modell.
- To rader med ulik promptversjon kan skilles.

#### FR-606 — Relevansskalaen

Relevansskalaen har tre verdier: **Påvirker selskapet direkte**, **Kan påvirke**
og **Lite relevant**. Det er de samme som i relevanseksperimentet. Skalaen brukes
ikke i v1. Del 2 av relevanseksperimentet kjøres ikke, fordi nyhetene ikke kan
brukes i en app som kan bli tilgjengelig for andre. Hvordan skalaen ville blitt
brukt på meldinger, står i FR-606A i vedlegg A.

*Konsekvenser:*
- Ingen side i v1 viser en relevansverdi.

#### FR-607 — KI-teksten om dagen på forsiden

Under tabellen i markedsoversikten står noen setninger om hele børsdagen,
«Børsdagen kort fortalt», skrevet av KI. Grunnlaget er bare antall og retninger:

- ukedagen, og retningen på hovedindeksen for dagen og for uka
- hvor mange som gikk bedre enn indeksen, og hvor mange som hadde kurs
- hvor mange som skilte seg ut per retning, og navnene på høyst fem av dem med
  styrke og retning
- antall som steg per bransje, og bransjene som steg og falt mest, regnet bare
  for bransjene med minst to aksjer med endring den dagen
- om flere eller færre enn vanlig skilte seg ut

Grunnlaget har ingen prosenter. Teksten lages én gang i hentekommandoen, med ett
kall til modellen per børsdag (NFR-02). Den logges som i FR-604 og FR-605, og den
er merket med modellen. Kontrollen i FR-603 gjelder. Teksten vises bare når
grunnlaget stemmer med det siden viser. Den gir ikke råd og spår ikke (NFR-06).

*Konsekvenser:*
- Teksten om dagen har én rad i loggen per børsdag.
- Et tall i teksten som ikke står i grunnlaget, stopper den.
- Med KI av vises den ikke.
- En setning om bransjen som steg eller falt mest, slutter med «mest av bransjene med minst to aksjer», ellers stopper kontrollen den.

#### FR-608 — Valg av tjeneste

Tjenesten velges i `.env` med `OSE_KI_TJENESTE`: `lokal`, `gemini`, `anthropic`,
`openai` eller `av`. Uten variabelen gjelder `lokal`. Malen `.env.example` har
`lokal`, så KI-teksten står på i en ny installasjon. Den lokale modellen trenger
verken nøkkel eller konto.

Første gang den ekte versjonen startes med dobbeltklikk på Windows, og den lokale
modellen ikke svarer, spør startskriptet om tre valg: hente Gemma, bruke egen
API-nøkkel eller «Ikke nå». Svarer ingen på 30 sekunder, blir det ingen KI-tekst
denne gangen, og spørsmålet kommer igjen neste gang. «Ikke nå» huskes, så
vinduet spør ikke igjen. En `.env` som finnes fra før, endres ikke uten et valg.
Svarer ikke modellen ved hentingen, lages ingen KI-tekst, og hentingen sier
hvorfor. Kursene hentes som før (NFR-04). Demoen spør aldri.

Det er én tjeneste per kjøring, uten stille overgang til en annen. Feiler
tjenesten, blir det ingen tekst og en rad i loggen (FR-604, NFR-04). Nøklene
heter `OSE_KI_GEMINI_NOKKEL`, `OSE_KI_ANTHROPIC_NOKKEL` og
`OSE_KI_OPENAI_NOKKEL`. Ingen nøkkel følger med appen eller repoet. Hver kobler
bare til sin egen, på sine egne vilkår. Med `av` lages ingen KI-tekst, og
hentingen går som før.

ChatGPT med «Sign in with ChatGPT» er ikke i v1, men kan komme senere (§2, §8).
Et Claude-abonnement kan ikke brukes.

*Konsekvenser:*
- En tjeneste som feiler, gir ingen tekst fra en annen tjeneste.
- Med `av` gjøres ingen kall til en modell.
- Ingen nøkkel står i repoet.
- `.env.example` har `OSE_KI_TJENESTE=lokal`.
- Uten svar på 30 sekunder starter appen uten KI-tekst, og ingenting lagres.

---

### 4.7 Signalstyrke og retning

> **Parametrene er låst.** Terskel, volumfaktor og nøytralsonebredde er testet
> mot **199 handelsdager** (2025-12-01 til 2026-09-18, 2 985 aksjedager). De to
> vinduene på 20 dager er testet mot like mange aksjedager, forskjøvet én
> handelsdag. Metode og tall står i `malinger.md` §7.4 og §9. Endres en
> parameter, føres det i `malinger.md`, med datoen den nye grensen gjelder fra.

Kravet til signalet er **forklarbarhet, ikke treffsikkerhet**. Vi lover ikke
bedre signaler enn andre. Vi lover at brukeren alltid kan se hva som ga utslaget.

#### FR-701 — Tre navngitte sjekker

Signalet består av tre sjekker. Hver gir +1, 0 eller -1. Det finnes ingen fjerde
sjekk, ingen vekting og ingen skjult formel.

| # | Sjekk | Måler | Gir utslag når |
|---|---|---|---|
| 1 | **Trend** | Den justerte sluttkursen mot 50-dagers glidende snitt | Kursen ligger mer enn **2 %** over eller under snittet |
| 2 | **Bevegelse** | Dagens endring mot aksjens egen volatilitet | Endringen overstiger ett standardavvik av de **20** dagenes endringer før |
| 3 | **Interesse** | Dagens volum mot eget medianvolum | Volumet overstiger **1,5 ×** medianen de **20** dagene før |

Fortegnet på **interesse** følger dagens kursendring. Høyt volum på en dag med
oppgang gir +1, og på en dag med nedgang -1. Er medianvolumet 0, gir interesse 0.
Alle beregninger bruker den justerte sluttkursen, så et ordinært utbytte ikke
leses som et kursfall.

*Konsekvenser:*
- Håndlagde kursserier gir forhåndsberegnet verdi for hver sjekk (SM-7).
- En kurs nøyaktig 2 % over snittet gir trend 0.
- Dagens endring regnes ikke med i standardavviket den måles mot.

#### FR-702 — Nøytralsone i trendsjekken

Trendsjekken har en nøytralsone på **±2 %** rundt det glidende snittet. Innenfor
sonen gir den 0. Uten sonen kan styrke 0 ikke forekomme. Målt over 2 985
aksjedager er andelen med styrke 0 da **0,0 %**, og oversikten kunne aldri sagt
at det ikke skjer noe (SM-4). Med sonen får **12,7 %** av aksjedagene styrke 0.
±1 % gir 5,6 %. ±4 % gir 25,7 % og tar seks prosentpoeng av styrke 2 og 3
(`malinger.md` §7.4).

*Konsekvenser:*
- En kurs 1,9 % over snittet gir trend 0, og 2,1 % gir +1.

#### FR-703 — Signalstyrke

Signalstyrke er summen av absoluttverdiene til de tre sjekkene. Det er et helt
tall fra 0 til 3: hvor mange av sjekkene som slo ut. Styrken sier ikke hvor
sannsynlig en kursbevegelse er, og ikke om aksjen bør kjøpes eller selges.

Fordelingen er målt over 199 handelsdager og 2 985 aksjedager (`malinger.md`
§7.4). Styrke 0 fikk **12,7 %**, 1 fikk **56,3 %**, 2 fikk **23,9 %** og 3 fikk
**7,0 %**.

*Konsekvenser:*
- Sjekkene +1, -1 og 0 gir styrke 2.
- Tre nuller gir 0.

#### FR-704 — Retning

Retningen leses av fortegnene til de sjekkene som ga utslag:

| Retning | Betingelse |
|---|---|
| Positiv | Alle utslag er +1 |
| Negativ | Alle utslag er -1 |
| Blandet | Noen utslag er +1 og noen -1 |
| Ingen | Ingen av sjekkene ga utslag (styrke 0) |

Blandet er et gyldig og informativt svar. Et kursfall på høyt volum i en aksje
som fortsatt ligger over sitt eget snitt, *er* Blandet.

*Konsekvenser:*
- +1, 0, +1 gir Positiv.
- +1, -1, -1 gir Blandet.
- 0, 0, 0 gir Ingen.

#### FR-705 — Terskel for at en aksje skiller seg ut

En aksje skiller seg ut den dagen signalstyrken er **2** eller høyere. Målt over
199 dager gir terskel 2 i snitt 4,6 av de 15 aksjene per dag. Bare 5 dager er
helt uten utslag. Terskel 3 ville gitt 1,1 og 87 tomme dager (`begrunnelser.md`
§6). Terskelen styrer **visningen**, ikke hentingen. Alle aksjene i lista hentes
og vurderes, og KI-teksten lages for hver aksje med en vurdering.

*Konsekvenser:*
- En aksje med styrke 2 står under «Skilte seg ut», og en med 1 under «Øvrige aksjer».
- Antallet i overskriften er antallet med 2 eller mer.

#### FR-706 — Synlig begrunnelse i aksjedetaljen

Aksjesiden lister de tre sjekkene ved navn, med **tre ting per sjekk**:

| Del | Eksempel |
|---|---|
| Navn | Trend |
| Verdien den ga | +1 |
| **Målingen bak verdien** | +3,1 % mot MA50 |

**Alle tre sjekkene vises, også de som ga 0.** En sjekk uten utslag sier at
akkurat den tingen ikke skjedde.

##### Hvorfor målingen må med

«Trend +1» kan ikke etterprøves uten å vite hvor langt over snittet kursen lå.
Med målingen kan brukeren regne etter:

> Trend +1 (+3,1 % mot MA50) · Bevegelse −1 (−3,5 % mot 1,1 % standardavvik) ·
> Interesse −1 (volum 4,95 × medianen) → styrke 3, retning Blandet

Tallene i parentes er grunnlaget. Styrken og retningen etter pila er utledet av
dem. Det er ingen vekting og ingen skjult formel. Er medianvolumet 0, står «–»
med grunnen i stedet for forholdstallet.

*Konsekvenser:*
- Målingen på siden er lik målingen i den lagrede vurderingen, avrundet for visning.
- Tallene vises med desimalkomma, slik norske tall skrives.
- En sjekk som ga 0, har fortsatt sin måling.

---

## 5. Tverrgående krav

### NFR-01 — Daglig drift skal holde seg innenfor API-kvoten

EODHD gir 20 kall i døgnet på gratisnivå, og døgnet regnes i GMT. En henting
koster ett kall per aksje i lista og ett for hovedindeksen. De 20 er fordelt
slik: 1 til hovedindeksen, 15 til de 15 aksjene, 3 til egne aksjer opp til 18, og
1 i reserve. Med 15 aksjer er 4 kall igjen til nye forsøk samme kveld, og med 18
er det 1. Hentekommandoen leser kvoten før første kall.

Bonuskvoten (`extraLimit`) brukes bare til å fullføre kveldens hovedhenting. Er
det færre kall igjen av dagens 20 enn hentingen trenger, men bonusen dekker
resten, hentes det. Utskriften sier da hvor mange kall som tas fra bonusen.
Dekker heller ikke bonusen det, blir det 0 kall. Første henting i en tom base,
nye forsøk og målingen av omsetning bruker aldri bonuskvoten. Unntaket er
kjøringen 10.11 i FR-413.

Ett bulk-kall er ikke et alternativ, fordi det koster 100 kall. Ett kall per
symbol er eneste vei, og det er denne begrensningen som gir universet på 15.
Ingen del av v1 krever betaling. Demoen trenger verken konto eller nøkkel, ekte
kurser trenger en gratis konto hos EODHD, og KI-teksten lages med den lokale
modellen.

*Konsekvenser:*
- Med 15 aksjer bruker en henting 16 kall og lar 4 stå.
- Med 3 kall igjen og bonus nok bruker hentingen bonusen og sier det.
- Et nytt forsøk med 0 kall igjen av dagens 20 gjør ingen kall.
- Ingen test gjør et API-kall.

### NFR-02 — Brukeren venter aldri på en henting

Henting skjer i en **egen kommando, i en egen prosess**. Den skjer aldri i
webserveren og aldri når en side vises. Webserveren viser alltid siste kjente
data med tidsstempel, fordi den aldri henter.

*Konsekvenser:*
- Webserveren laster ingen kode som kaller en modell.
- Nettsperren i testene stopper ethvert nettkall fra en side.

### NFR-03 — Manglende data stopper ikke hovedflyten

Kildefeil, manglende data og dager uten tydelige signaler stopper ikke
hovedflyten. De tvinger heller ikke fram et resultat. Siste kjente data vises med
tidsstempel, og signalstyrke 0 er et gyldig svar (FR-702).

*Konsekvenser:*
- En base der én aksje mangler alle kurser, viser oversikten og aksjesiden som vanlig.
- En dag der alle har styrke 0, viser «0 av N skilte seg ut» og tabellen.

### NFR-04 — KI-laget skal ikke kunne ta ned hovedflyten

Applikasjonen fungerer med den regelbaserte analysen alene. En treg eller
utilgjengelig modell forsinker eller stopper verken hentingen av kursene eller
markedsoversikten.

*Konsekvenser:*
- En modell som feiler, gir vurderingene som vanlig og en rad i loggen uten tekst.
- Webserveren starter uten modell.

### NFR-05 — Norsk i grensesnitt og forklaringer

Grensesnittet er på norsk, og KI-tekstene skrives på norsk.

*Konsekvenser:*
- Sidene er merket som norske (`lang="no"`).
- Prompten ber om en forklaring på norsk.

### NFR-06 — Løsningen gir ikke investeringsråd

Signalstyrke og retning beskriver hva sjekkene slo ut på, ikke hva brukeren bør
gjøre. Ingen del av grensesnittet formuleres som en anbefaling om kjøp eller
salg: ikke malene, ikke hjelpen og ikke KI-tekstene.

*Konsekvenser:*
- Ingen KI-tekst som vises, har et ord fra rådlista i FR-603. Kontrollen skjer når teksten lages og når den vises.
- Hjelpetekstene og omvisningen har ingen ord fra rådordene testene for hjelpen bruker.
- Ord som «råd», «kjøp» og «salg» står bare der en side sier at noe ikke er et råd, og i notatene om tenkte kjøp og salg.
- En test går gjennom alle malene, hjelpetekstene og omvisningen etter ordene i rådlista i FR-603, og unntakene står i testen med grunn.

### NFR-07 — Rådata bevares fra første kjøring

Rådata fra kursene lagres som tidsstemplede øyeblikksbilder fra første henting
(FR-406). Da står ikke prosjektet tomhendt om en kilde endres, og målinger kan
etterprøves. Rådata legges aldri i repoet.

*Konsekvenser:*
- En ny henting lager en ny fil og skriver aldri over en gammel.

### NFR-08 — Bare tall vi kan stå for

Et tall vises bare når det kommer fra dataene, er regnet etter en regel som står
skrevet, og har bestått kontrollen. Mangler tallet, eller ser det feil ut, vises
«–» med grunnen. Appen viser aldri et anslag eller et reservetall. Mangler den
ene av sluttkursen og den justerte sluttkursen, brukes ikke den andre i stedet. Oppdiktede tall merkes
«Eksempeltall» på hver side der de vises. De vises aldri sammen med ekte tall,
fordi en side leser enten demobasen eller den ekte basen.

*Konsekvenser:*
- En kursrad uten justert sluttkurs gir ingen endring, og ikke endringen på sluttkursen.
- Ingen side viser tall fra begge basene.
- Perioderegelen testes med faste datoer rundt helger, helligdager og nyttår.

---

## 6. Datakilder

Kildestatus, kontrollerte vilkår og forkastede kilder står i
`docs/kilder-og-rettigheter.md`.

| Kilde | Brukes til | Koster kvote |
|---|---|---|
| EODHD, kurser per dag | Kursene for aksjene og hovedindeksen, og målingen av omsetning | 1 kall per symbol |
| EODHD, kontoen | Kvoten før og etter kall | Nei |
| EODHD, nyheter | Relevanseksperimentet del 1, én innsamling 25.09 | 5 kall per forespørsel med én ticker (`malinger.md` §7.2). Ikke daglig drift |
| Lista over aksjene på Oslo Børs | Rekkefølgen i målingen av omsetning, lest av et menneske | Nei |
| KI-tjenesten | KI-tekstene, med bare våre egne resultater (§4.6) | Nei. Den lokale er gratis, og Gemini, Anthropic og OpenAI bruker egen nøkkel |

Oslo Børs NewsWeb og Euronexts finanskalender brukes ikke i v1. Euronexts
vilkår dekker NewsWeb ved navn. De forbyr automatisert henting uten skriftlig
tillatelse på forhånd, og tillatelse er ikke gitt (vedlegg A).

---

## 7. Suksessmål

| ID | Mål | Hva vi måler | Terskel | Frist | Krav |
|---|---|---|---|---|---|
| SM-1 | Brukerutfall | En person utenfor gruppen gjennomfører hovedflyten og forklarer uoppfordret hvorfor en aksje skiller seg ut | Minst 1 person, under 5 minutter, uten hjelp | Før prosjektinnlevering | FR-101, FR-102, FR-109, FR-201, FR-202, FR-402, FR-602, FR-706, NFR-03 |
| SM-2 | Adopsjon | Gruppen bruker løsningen på egne aksjer og logger feil | Minst 4 av 5 børsdager fra første fungerende versjon, ført i brukslogga | Løpende | FR-111, FR-401, FR-412, NFR-02 |
| SM-3 | Drift | Én henting fullfører innenfor kvoten. Ved kildefeil vises siste kjente data med tidsstempel | Én kommando gjør hele hentingen, også migrasjonene. Ingen stopp ved manglende data | Ukentlig | FR-401, FR-402, FR-406, FR-408, NFR-01, NFR-03 |
| SM-4 | Dager uten signal | Dager uten tydelige signaler håndteres uten at hovedflyten stopper eller tvinger fram et resultat | Signalstyrke 0 forekommer og vises riktig | Løpende | FR-702, FR-703, FR-409, NFR-03 |
| SM-5 | Fortsatt bruk | Om vi bruker løsningen frivillig etter at utviklingen er ferdig | Minst tre dager i uka de to siste ukene, ført i brukslogga | Ved prosjektinnlevering | FR-101, FR-401 |
| SM-6 | Grensesnitt og stabilitet | Hovedflyten fungerer uten feil i en demonstrasjon | Hovedflyten gjennomført uten feil eller manuelle inngrep | Ved demonstrasjonen | FR-101, FR-201, FR-204, FR-411, NFR-03 |
| SM-7 | Riktige beregninger | Håndlagde kursserier gir forhåndsberegnet styrke og retning | Testene består, og en kontroll for hånd stemmer med appen (`malinger.md` §6) | Ved hver testkjøring | FR-701, FR-702, FR-703, FR-704, NFR-08 |
| SM-8 | KI-forklaringen | Hver KI-tekst som vises, har bestått kontrollen mot grunnlaget, og hver tekst er logget | Testene viser at feil stoppes. Én ukes drift er logget | Før demonstrasjonen | FR-601, FR-602, FR-603, FR-604, FR-605, FR-607, NFR-04 |
| SM-9 | Kjørbar for andre | README-oppskriften fullføres gratis på en ren maskin, uten gruppens nøkler. Demoen virker uten konto, og den ekte versjonen med egen gratiskonto hos EODHD | README-prøven fra en ren maskin | Senest én uke før innleveringen | FR-411, FR-608, NFR-01 |

**Hovedflyten** er: åpne markedsoversikten, se hvilke aksjer som skiller seg ut,
åpne én av dem, og lese hvorfor. Forklaringen er de tre sjekkene med målingene,
og KI-teksten når den er på. SM-1 og SM-6 måler denne flyten, som brukerreisen UJ-1
beskriver.

**Status 12.11.**

- SM-1 er ikke nådd. Brukertesten 10.11 hadde én person og den ekte versjonen.
  Personen forklarte uoppfordret hvorfor en aksje skilte seg ut, men brukte over
  5 minutter (`docs/brukertest.md`). Terskelen står.
- SM-8: uka 29.10–04.11 er logget, med 75 tekster, 15 på hver av de fem
  børsdagene. De er laget med `gemma4:e4b` lokalt og promptversjon 3. Alle besto
  kontrollen, og 0 ble stoppet. Etter motmålet under er det et varsel, ikke en
  suksess. Promptversjonen er 6 i dag, så uka gjelder en eldre prompt.
- SM-2 og SM-5 føres i [brukslogga](../../../../docs/brukslogg.md) fra 4.11, med
  én linje per dag gruppen bruker appen. Jobbens logger regnes ikke som bruk.
  Brukslogga har én linje 12.11.
- SM-9: README-prøven tas når v1 er ferdig bygget.
- Datoene for demonstrasjon og innlevering er ikke kjent (§8, punkt 13).

**Drift: hva målet ga opp.** Målet sa først «ingen manuelle steg», og det målte
to ting. *Ingenting utløses av et menneske* er **gitt opp, og det var et valg**.
Henting ved oppstart ville brukt 16 kall per start mot en dagskvote på 20
(FR-401). *Når hentingen først er utløst, må ingenting annet huskes* er
**beholdt**. Vurderingen skrives i samme kjøring, og migrasjonene kjøres når
basen åpnes, ikke som et eget steg. Målet er omformulert og ikke strøket. Men den
første halvdelen er oppgitt, ikke myknet opp. Ellers ville det sett ut som om
målet ble justert til å passe det vi bygde.

To mål fra eldre versjoner gjelder ikke lenger. «KI-bidrag i drift» er erstattet
av SM-8 etter plan B, og «Relevanseksperiment» utgikk etter del 1. Begge står i
endringsloggen.

### Motmål

Mål kan nås på måter som ikke betyr noe. Disse leses sammen med tabellen over:

- **Vi setter ikke mål for hvor godt signalene treffer markedet.** Kravet til
  signalet er forklarbarhet, ikke treffsikkerhet.
- **KI-laget måles i at tekstene består kontrollen** i FR-603, ikke i hvor mange
  det lager.
- **Adopsjon som bare er testing, teller ikke.** Derfor er SM-5 et eget mål med
  egen terskel.
- **En kontroll som aldri slår til, er et varsel**, ikke en suksess. Stopper
  FR-603 aldri en tekst, kan kriteriene være feil kalibrert.
- **Vi har ingen teknisk fordel andre ikke kan kopiere**, og vi skal ikke påstå
  at vi har den. Datakildene er åpne eller kommersielt tilgjengelige for alle.

---

## 8. Åpne punkter

<a name="må-avgjøres-før-arbeidet-går-videre"></a>

Numrene følger rekkefølgen punktene ble opprettet i, så kryssreferanser fra
`malinger.md` og gjennomgangene holder. Punktene slik de sto, med alle de
lukkede, står ordrett i endringsloggen.

### Må følges opp

| # | Punkt | Eier | Frist |
|---|---|---|---|
| 13 | **Datoer for demonstrasjon og prosjektinnlevering.** Ikke oppgitt ennå (`docs/innlevering.md`). SM-1, SM-5, SM-6, SM-8 og SM-9 er bundet til dem | Gruppen | Avventer faglærer |
| 21 | **Hva er emnesidens tredje del?** Emnesiden sier «tre deler», men lister to (`docs/innlevering.md`, «Eksamen») | Gruppen | Sammen med punkt 13 |
| 22 | **Kodegjennomgang.** Én samlet `bmad-code-review` av v1-koden. Gjennomgangene per PR står i `docs/kvalitetssikring.md` §5 | Gruppen | Før innleveringen |
| 27 | **En misvisende KI-tekst med riktige tall** (FR-603). Kontrollen fanger ord og tall, ikke mening. Hvordan det kunne oppdages og skrives som en testbar konsekvens, er refleksjonsspørsmål 2 i tilbakemeldingen 12.11 | Gruppen | Til refleksjonsrapporten |

### Utenfor v1

Punkt 2, 6, 8, 11, 12, 15 og 16 gjelder plan A, børsmeldingene og de kommende
hendelsene. De tas opp igjen bare hvis plan A tas opp (vedlegg A). Punkt 4,
hvordan en justeringsdag finnes, er besvart av metoden i FR-407.

### Lukket

Punkt 1, 3, 5, 5b, 7, 9, 10, 14, 17, 18, 19, 20, 23, 24, 25 og 26 er lukket. Hva som
lukket dem, står i endringsloggen.

### v1.1 — vurderes etter at v1 er kontrollert

Gruppen avgjorde 12.11 kl. 20:09 og 20:10 at disse åtte ikke er i v1. Kravene
står som plan for en senere versjon:

- endringen i kroner under prosenten i oversikten (FR-101)
- merket for endret signalstyrke (FR-107)
- «Lær noe nytt» (FR-109)
- høy og lav og endringen i kroner på aksjesiden (FR-203)
- «Se nærmere» (FR-205)
- kommende eks.dato i kursgrafen (FR-207)
- eks.datoer ført for hånd (FR-414)
- ChatGPT med «Sign in with ChatGPT» (FR-608)

De andre idéene til v1.1 er enten tatt inn som krav over, eller de står med
forbeholdene sine i endringsloggen. Ingen av dem tas før v1 er kontrollert og
virker.

---

## Vedlegg A. Plan A: børsmeldinger, hendelser og KI over meldinger

Plan A er ute av v1. Euronext ga ikke tillatelse til automatisert henting fra
NewsWeb før gruppens frist 28.09, og taushet ble regnet som nei (plan B).
Kravene står her slik de ville vært bygget. Kommer et ja, er det en ny
beslutning, og plan A bygges da oppå plan B. Status: senere, ikke bygget (§2).

### 4.3 Kommende finansielle hendelser

#### FR-301 — Kilde og kobling til selskap

Kommende finansielle hendelser hentes fra Euronexts finanskalender. Kilden koster
ingen EODHD-kvote. Kalenderen oppgir **verken ticker eller ISIN**. Hendelser
kobles derfor til selskap gjennom en oppslagstabell. Den settes opp for
aksjeuniverset én gang og vedlikeholdes for hånd hvis universet endres.

*Konsekvenser:*
- En hendelse kobles til selskap bare gjennom oppslagstabellen.
- Koblingen gjør ingen EODHD-kall.

<a name="fr-302--hvilke-hendelser-og-hvor-langt-frem"></a>

#### FR-302 — Hvilke hendelser og hvor langt fram

`[ANTAKELSE]` Aksjedetaljen viser kommende hendelser for selskapet innenfor de
neste `[FORELØPIG] 90` dagene. Hendelsestypene er de kalenderen oppgir. Typisk
er det resultatfremleggelser, generalforsamlinger og utbyttedatoer. Horisonten og
typeutvalget er antatt. De bekreftes når kalenderens innhold for universet er
undersøkt.

*Konsekvenser:*
- En hendelse om mer enn 90 dager vises ikke.
- En hendelse for et selskap utenfor oppslagstabellen vises ikke.

#### FR-303 — Når kalenderen ikke svarer

Er kalenderen utilgjengelig, eller uten treff for et selskap, vises aksjedetaljen
uten hendelsesseksjonen. Den viser ikke en feilmelding (NFR-03).

*Konsekvenser:*
- En kalender som svarer med feil, gir aksjesiden uten hendelser og uten feilmelding.

#### FR-404 — Etterfylling av børsmeldinger

Meldinger etterfylles som kurser og koster ingen EODHD-kvote. NewsWeb støtter
`fromDate` og `toDate` som et ekte intervall. Meldinger følger kalenderdøgn, så
etterfyllingen dekker alle kalenderdager i hullet, ikke bare børsdagene.

*Konsekvenser:*
- Et hull fra fredag til mandag henter også lørdag og søndag.
- Etterfyllingen gjør ingen EODHD-kall.

#### FR-405 — Avkorting ved lange meldingsintervaller

NewsWeb har et resultattak på mellom 557 og 601 meldinger per forespørsel. Er
intervallet for langt, returneres de **nyeste** meldingene, og resten forkastes.
Svaret er da HTTP 200, uten feilmelding (`malinger.md` §3). Feltet
`data.overflow` er `true` nøyaktig når noe ble forkastet. Det er udokumentert,
men verifisert i begge retninger.

**Kravet:** etter hver meldingshenting kontrolleres `data.overflow`. Er den
`true`, deles intervallet og hentes på nytt, til hver del kommer tilbake med
`overflow: false`. Er **den eldste meldingen i svaret** nyere enn `fromDate`,
behandles også det som en ufullstendig henting, selv om `overflow` er `false`.
Delingen har en nedre grense på ett døgn. Gir ett døgn fortsatt
`overflow: true`, stopper hentingen, og feilen rapporteres.

*Konsekvenser:*
- Et svar med `overflow: true` deles og hentes på nytt.
- Ett døgn med `overflow: true` stopper hentingen med en feil.
- Et svar der den eldste meldingen er nyere enn `fromDate`, regnes som ufullstendig.

### 4.5 Meldingsfilter og deduplisering

Grunnlaget er en måling over 2026-08-22 til 2026-09-18, **28 kalenderdager**. For
de 15 selskapene ga det **121 meldinger, 4,3 per kalenderdag**. Mengden er ikke
problemet. Sorteringen er det (`malinger.md` §4).

#### FR-501 — Deduplisering av språkdubletter

32 av 121 meldinger (26 %) er samme melding publisert på norsk og engelsk.
**Kjennetegn på en dublett:** samme utsteder, samme kategori og samme
publiseringsminutt. Kjennetegnet slår sammen bare når det finnes positivt
grunnlag for at det er samme melding. Ved tvil beholdes begge. **Hvilken
beholdes:** den norske når begge finnes.

Meldingen har ikke noe felt for språket (`malinger.md` §7.3). Språket avgjøres
derfor av tittelen. Æ, ø eller å avgjør alene. Ellers telles kjente norske ord mot
kjente engelske. **Er det uavklart, beholdes den første.** Regelen slår feil for
Vår Energi, som har «å» i navnet (punkt 16). Dedupliseringen kjøres **før**
kategorifilteret.

*Konsekvenser:*
- To meldinger fra samme utsteder, kategori og minutt, der den ene er norsk, gir én norsk melding.
- To meldinger uten positivt grunnlag beholdes begge.

#### FR-502 — Kategorifilter i tre bøtter

Grovsorteringen gjøres med regler på NewsWebs kategorifelt. Hver kategori hører
til nøyaktig én bøtte. Antallene er før dedupliseringen.

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

**Kategorier som ikke står i tabellen**, vises merket **«ukjent kategori»** og
føres i loggen. De sendes **ikke** til KI-laget, fordi prompten ikke er
kalibrert for dem (`begrunnelser.md` §4).

*Konsekvenser:*
- Hver kategori i tabellen havner i sin bøtte.
- En ukjent kategori merkes «ukjent kategori» og sendes ikke til KI-laget.

#### FR-503 — Eks.dato som datakilde for utbyttemerking

Meldinger i kategorien `EKS.DATO` vises ikke i meldingslista, men forkastes ikke.
I plan A ville de vært en kilde til merkingen i FR-407. I v1 finnes
justeringsdagene av kursserien alene.

*Konsekvenser:*
- En melding i `EKS.DATO` står ikke i meldingslista.

#### Resultat av filteret

| Steg | Meldinger over 4 uker | Per kalenderdag |
|---|---:|---:|
| Hentet fra NewsWeb | 121 | 4,3 |
| Etter deduplisering | 89 | 3,2 |
| Slipper gjennom til KI-forklaring | ~35 | ~1,25 |
| Til KI-relevansvurdering | ~13 | ~0,5 |

Tallene etter deduplisering er anslag, fordi dublettandelen er målt samlet og
ikke per kategori.

### 4.6A Plan A: KI-laget over meldinger (utenfor v1)

KI brukes der, og bare der, metadata er uttømt (`begrunnelser.md` §1). KI-laget
avgjør ikke hvilket selskap en melding gjelder. Den jobben gjør utstederfeltet
bedre og gratis. FR-601 og FR-605 gjelder begge planene.

#### FR-602A — Visningen når KI-laget er av

Meldingene i samlekategorien vises fortsatt når laget er av, merket **«ikke
vurdert»**. Regelfilteret sorterer som før, og meldinger som slapp gjennom,
vises uten KI-forklaring. Begrunnelse: meldinger som forsvinner, ville gjort
sammenligningen av av og på meningsløs.

*Konsekvenser:*
- Med KI av vises meldingene i samlekategorien merket «ikke vurdert», like mange som med KI på.

#### FR-603A — Usikkerhet vises som forbehold, ikke som rekkefølge

Er en KI-vurdering usikker, vises den med forbehold der den står. Meldingen
sorteres ikke ned. Usikkerheten avledes av kjennetegn som kan observeres:

- om selskapet nevnes i overskrift eller ingress
- om mange selskaper nevnes likeverdig
- om to kjøringer gir samme klassifisering

Der kjennetegnene spriker, merkes vurderingen som usikker.

*Konsekvenser:*
- En usikker vurdering står på samme plass i lista, merket som usikker.

#### FR-604A — Logging av KI-bidraget, fra første kjøring

For hver melding KI-laget behandler, lagres meldings-id, utsteder, kategori og
publiseringstidspunkt. Det lagres også hva regelfilteret alene gjorde med den,
KI-lagets vurdering, forklaring og usikkerhetsmerke, og promptversjon og modell
(FR-605). Loggingen starter ved første kjøring.

*Konsekvenser:*
- Hver melding KI-laget behandlet, har én rad med feltene.

#### FR-606A — Relevansskalaen

KI-vurderingen av en melding i samlekategorien gir én av tre verdier:

| Verdi | Betyr |
|---|---|
| **Påvirker selskapet direkte** | Saken har konkret betydning for selskapets drift, kontrakter, eierskap eller resultat |
| **Kan påvirke** | Saken kan få betydning, men det er ikke gitt |
| **Lite relevant** | Saken har ingen praktisk betydning for en sparer |

Meldinger vurdert som *påvirker direkte* eller *kan påvirke*, vises. *Lite
relevant* skjules bak bryteren **Anbefalt**/**Alle**, skjult, men ikke borte.
Grensen `[FORELØPIG]` kan ikke avgjøres på papir (punkt 2).

Med bryteren Anbefalt/Alle står det over meldingene hvor mange som ble funnet og
hvor mange som vises. Grunnen til at resten er skjult, står også. Eks.dato er
merking, ikke melding (FR-503). KI-forklaringen per melding ligger bak «Vis
forklaring». Den lages i hentingen, ikke ved klikket (NFR-02).

*Konsekvenser:*
- «Lite relevant» vises under Alle og ikke under Anbefalt.
