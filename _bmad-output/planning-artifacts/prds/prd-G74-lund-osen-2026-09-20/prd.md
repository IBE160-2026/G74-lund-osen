---
title: "PRD — OSE Signal"
status: final
created: 2026-09-20
# updated settes fra klokka, aldri for hånd:
#   date +%Y-%m-%dT%H:%M   (lokal tid, samme som memloggen)
# Feltet sto på 2026-09-20 mens fem commits den 21.09 hadde endret dokumentet.
updated: 2026-09-23T18:40
#
# Hvorfor status var draft, og hva som avsluttet den.
#
# «draft» er IKKE en påstand om at dokumentet er uferdig. Det har vært gjennom
# fem gjennomganger og en sjekkliste, og kravene er nummererte og begrunnet.
# Det står som draft fordi ARKITEKTURFASEN KOMMER TIL Å ENDRE KRAV DET
# INNEHOLDER — først og fremst FR-406.
#
# Statusen endres når alle fire er innfridd. Dette er en betingelse, ikke en
# dato; ingen frist løser den ut:
#   1. Åpent punkt 17 (database) er besluttet
#   2. Åpent punkt 18 (Dockerfile) er besluttet
#   3. FR-406 er oppdatert i tråd med 1 og 2
#   4. De to gjenstående [FORELØPIG]-vinduene i §4.7 er målt: de 20 dagene i
#      bevegelsessjekken og de 20 i interessesjekken. De var ikke med i testen
#      i malinger.md §7.4, som låste tre parametre og ikke fem
#
# INNFRIDD 2026-09-22T16:07 — alle fire. Betingelsen står igjen slik den ble
# formulert, ikke slettet: den viser hva som skulle til, og refleksjonsrapporten
# skal kunne lese det. 1 og 2 ble besluttet i arkitekturfasen (spinen AD-3..AD-5,
# AD-9..AD-11). 3 ble skrevet inn samme dag. 4 ble målt mot de 2 985
# aksjedagene, malinger.md §9 — og målingen måtte bytte metrikk underveis, fordi
# den første målte avstand fra 20 og var 0 ved 20 per konstruksjon.
#
# Betingelsen står her fordi en status uten utgangsbetingelse blir stående til
# noen tilfeldigvis tar den opp — samme mekanisme som datoen på
# relevanseksperimentet, som ble stående i uke 41 etter at det som blokkerte
# det var avklart.
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

**Aksjer uten gyldig signal vises likevel.** Signalet krever 51 handelsdager
fordi MA50 spiser 50 av dem. En nynotert aksje, eller en serie med hull, gir
derfor ingen signalverdi. Raden skal da vises med:

| Kolonne | Innhold når signalet mangler |
|---|---|
| Selskap, Sluttkurs, Endring | Som vanlig, hvis dataene finnes |
| Signalstyrke | Tom |
| Retning | **Ukjent** |

«Ukjent» er ikke en femte retning i FR-704 — det er fraværet av en vurdering.
Skillet betyr noe: *Ingen* sier at de tre sjekkene ble regnet og ingen slo ut,
*Ukjent* sier at de ikke kunne regnes.

Begrunnelsen er NFR-03: manglende data for én aksje skal ikke stoppe
hovedflyten. En rad som forsvinner, forteller brukeren at aksjen ikke finnes.
En rad med tom styrke forteller at den finnes og at vi ikke kunne vurdere den.
Bare det andre er sant.

Aksjer kilden ikke har en eneste kursrad for, faller ut av tabellen, men skal
navngis under den, slik at brukeren vet at oversikten er ufullstendig.

##### Navigasjon til aksjedetaljen

**Selskapsnavnet i første kolonne er lenken til aksjedetaljen** (FR-201 til
FR-203). Aksjedetaljen skal ha en synlig vei tilbake til markedsoversikten.

Kravet stod ikke skrevet før 2026-09-21. De to skjermbildene var spesifisert
hver for seg, og ingenting sa at det ene fører til det andre — de hang
uforbundet i kravregisteret selv om hovedflyten forutsetter begge.

Navnet er valgt som lenke framfor en egen kolonne med knapp, fordi femte
kolonne allerede er brukt opp: FR-101 sier nøyaktig fem kolonner, og en sjette
ville brutt kravet for å løse et navigasjonsproblem.

#### FR-102 — Standard sortering

Sortering er **signalstyrke fallende**, med **absolutt kursendring** som
sekundærkriterium ved lik styrke.

Absolutt, ikke fortegn: et stort fall skal ikke havne bakerst fordi det er
negativt.

**Aksjer uten gyldig signal sorteres sist**, uansett kursendring. En rad vi
ikke kunne vurdere, skal ikke legge seg foran en vi kunne vurdere.

Merk at styrken bare har fire verdier fordelt på femten rader, så lik styrke er
normalen og ikke unntaket. Målingen 2026-09-21 viste 13 av 15 aksjer på styrke
2 eller høyere for 2026-09-18. **Sekundærkriteriet gjør derfor mesteparten av
sorteringsarbeidet**, og det er verdt å vite når rekkefølgen skal forklares i
en demonstrasjon.

At brukerens egne aksjer havner tilfeldig i lista, er akseptert i v1.
Favorittmerking hører til «hvis vi rekker».

#### FR-103 — Retning vises i tre redundante kanaler

Retningen vises som tekst, symbol og farge samtidig.

**Visningen bruker FR-704s ordforråd uendret.** Teksten på skjermen er den
samme strengen som modellen produserer — ingen oversettelse mellom de to:

| Retning (FR-704) | Tekst på skjermen | Symbol |
|---|---|---|
| Positiv | Positiv | ↑ |
| Negativ | Negativ | ↓ |
| Blandet | Blandet | ↔ |
| Ingen | Ingen | – |

*Endret 2026-09-21.* Kravet sa tidligere «Opp» og «Ned». De ordene sto rett ved
siden av kolonnen Endring og inviterte til å lese pilen som kursbevegelse,
mens retningen sier noe annet: hva de tre sjekkene peker mot. Briefen slår fast
at signalstyrke ikke er en anbefaling om kjøp eller salg, og «Opp/Ned» lener
seg mot nettopp den lesningen. Oversettelsen er fjernet, ikke dokumentert.

Alle tre kanalene er obligatoriske. Farge alene utelukker fargeblinde brukere,
og «blandet» lar seg ikke uttrykke lesbart i farge i det hele tatt. Teksten er
den bærende kanalen; symbol og farge er forsterkninger. Symbolet står ved siden
av teksten, ikke i stedet for den, og skjules for skjermlesere så pilen ikke
leses opp i tillegg til ordet.

#### FR-407 — Merking av utbyttedager

*ID-en er beholdt fra da kravet lå i datahentingen. Det hører hjemme her.*

> **Datakilden er ikke lenger avhengig av NewsWeb.** Kravet forutsatte
> opprinnelig EKS.DATO-meldinger (FR-503). Målingen 2026-09-21 viser at
> justeringsdagen kan leses ut av kursserien alene. Se åpent punkt 4 og
> `begrunnelser.md` §11.

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
50-dagers snittet har kontekst, og kort nok til å være lesbar. Det gir omtrent
125 handelsdager; kravet til hvor mye kilden må inneholde, står i FR-406.

**Grafen tegnes på `adjusted_close`**, ikke på `close`. Det gjelder både
kurslinjen og MA50-linjen i FR-202.

Flere valgbare tidsperioder hører til «hvis vi rekker».

#### FR-202 — MA50-linjen tegnes oppå kursen

Grafen tegner 50-dagers glidende snitt som en linje oppå kursen. Det gjør
**sjekk 1, trend**, direkte synlig.

**Begge linjene tegnes på samme serie: `adjusted_close`.**

Begrunnelsen er at aksjedetaljen finnes for å forklare signalet. MA50 regnes på
utbyttejustert kurs etter FR-701. Tegner grafen en annen serie enn den signalet
bruker, forklarer skjermbildet noe annet enn det som faktisk skjedde — og
avviket ville vært systematisk, ikke tilfeldig.

**Målt i grafvinduet 2026-09-21**, som avstand mellom `close` og
`adjusted_close`:

| Symbol | Avstand |
|---|---:|
| FRO | 8,93 % |
| DNB | 5,84 % |
| GJF | 5,64 % |
| **Median over de 15** | **3,72 %** |

Avstanden er størst for aksjene som betaler mest utbytte. En kurslinje på
`close` mot et snitt på `adjusted_close` ville altså ligget mest feil nettopp
der utbyttet betyr mest.

**Markedsoversikten og aksjedetaljen viser derfor bevisst ulike serier:**

| Skjermbilde | Hva som vises | Hvorfor |
|---|---|---|
| Markedsoversikten (FR-101) | `close` | Det er kursen aksjen faktisk omsettes til |
| Aksjedetaljen (FR-201) | `adjusted_close` | Det er serien signalet er regnet på |

Det er en reell forskjell brukeren kan oppdage, og den skal forklares der den
oppstår: **tegnforklaringen i grafen skal si at linjene viser utbyttejustert
kurs.** Uten det vil en bruker som sammenligner de to skjermbildene, lese
forskjellen som en feil.

**Sjekk 2 (bevegelse) og sjekk 3 (interesse) vises bare som tall** i lista over
de tre sjekkene, jf. FR-706. Volatilitetsbånd og volumsøyler tegnes ikke i v1.

#### FR-203 — Øvrig innhold

Aksjedetaljen viser i tillegg:

- En synlig vei tilbake til markedsoversikten, jf. navigasjonskravet i FR-101
- De tre sjekkene ved navn, med verdien hver av dem ga og målingen bak den
  (FR-706)
- Børsmeldinger som passerte filteret, med lenke til originalen på NewsWeb
- KI-forklaring per melding når KI-laget er på, eller «ikke vurdert» når det er
  av (FR-602)
- Kommende finansielle hendelser fra Euronext

#### FR-204 — Aksjedetaljen for en aksje uten gyldig signal

Signalet krever 51 handelsdager (FR-701). Har en aksje kortere historikk, eller
hull i serien, kan det ikke regnes.

**Aksjedetaljen skal da svare som vanlig, ikke feile:**

| Del | Hva som skjer |
|---|---|
| Svaret | 200, ikke 404 |
| Kursgrafen | Tegnes, så langt dataene rekker. MA50-linjen utelates hvis snittet ikke finnes |
| De tre sjekkene | Utelates — det finnes ingen verdier å vise |
| I stedet | En beskjed om at signalet ikke kunne regnes, med grunnen |

**Kursen finnes selv om snittet ikke kan regnes**, og da skal den vises.

Begrunnelsen er den samme som FR-101 fikk: en 404 forteller brukeren at aksjen
ikke finnes. En side med graf og en beskjed forteller at den finnes og at vi
ikke kunne vurdere den. Bare det andre er sant, og NFR-03 sier at manglende
data for én aksje ikke skal stoppe hovedflyten.

**404 er forbeholdt to tilfeller:** et symbol som ikke er i aksjeuniverset, og
en aksje kilden ikke har en eneste kursrad for.

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

#### FR-401 — Henting utløses eksplisitt, aldri av en oppstart

Henting er en egen, bevisst handling — verken en bivirkning av at noe startet
eller en planlagt jobb med fast klokkeslett.

**Webserveren henter aldri.** Den starter alltid uten å bruke et eneste
API-kall, og viser siste kjente data med tidsstempel. Finnes ingen data ennå,
vises en tom tilstand som forklarer hvordan henting gjøres — ikke en feil.

Hentekommandoen kontrollerer først om lagrede data er eldre enn siste
børsslutt (FR-402). Er de ikke det, hentes ingenting og ingen kvote brukes.
Skal det hentes, skjer det i denne rekkefølgen: kurser, deretter meldinger, og
til slutt dagens vurdering per aksje (FR-408).

**Hvor langt tilbake hver henting går, er fastsatt i FR-406.**

*Endret 2026-09-22.* Kravet sa opprinnelig at henting utløses når applikasjonen
starter. Det var skrevet for en applikasjon som starter én gang. En container
startes på nytt hver gang, så «ved oppstart» ville betydd 15 kall per
`docker run` mot en dagskvote på 20 — to kjøringer ville brukt opp dagen.
Arkitekturspinen AD-10 og AD-17.

#### FR-402 — Kontroll mot forventet børsdag, ikke mot klokkeslett

Hentingen skal ikke anta at data er ferske fordi klokka har passert et
tidspunkt. Den skal kontrollere at nyeste `date` i svaret er forventet børsdag.

Er nyeste `date` ikke forventet børsdag, vises siste kjente data med
tidsstempel, og hentingen prøves igjen ved neste kjøring av hentekommandoen.
Applikasjonen skal aldri presentere gårsdagens tall som dagens.

Kontrollen eies av hentekommandoen alene — webserveren henter ikke, og kan
derfor ikke handle på utfallet. «Forventet børsdag» regnes i norsk
kalenderdato; se arkitekturspinen AD-20.

EODHD dokumenterer ingen publiseringstid for Oslo Børs; se `begrunnelser.md`.

#### FR-403 — Etterfylling av kurser etter dager uten bruk

Kjører ingen hentekommandoen på flere dager, oppstår hull i serien. Hullene
skal fylles ved neste henting uten ekstra kostnad i kvote.

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

#### FR-406 — To lagre for kursdata, med hvert sitt ansvar

Kursdata lagres i to atskilte lagre som aldri blandes:

| Lager | Innhold | Regel |
|---|---|---|
| **Beregningsgrunnlag** | Serien som signalberegningen leser — `kurs`-tabellen i databasen | Erstattes i sin helhet **ved hver henting**, per symbol, i én transaksjon. Skjøtes aldri på. |
| **Rådata** | Øyeblikksbilder med tidsstempel per henting | Skrives aldri om. Dokumentasjon og sikkerhetsnett, ikke beregningskilde. |

De to lagrene ligger nå i hvert sitt medium: beregningsgrunnlaget i databasen,
rådata som filer. **Regelen var aldri fil mot base.** Den var at serien aldri
skjøtes på, fordi EODHD regner `adjusted_close` om bakover ved hvert nytt
utbytte. Den regelen holdes i databasen ved at hver henting erstatter symbolets
rader i sin helhet. Se arkitekturspinen AD-5 og AD-6.

**Merk at dette ikke er et krav om å hente oftere.** En henting utløses bare når
noen kjører hentekommandoen, og bare hvis betingelsen i FR-401 er oppfylt.
Kravet her gjelder *hva* en henting gjør når
den først skjer: den laster ned hele serien på nytt i stedet for å skjøte nye
rader på en lagret serie. Kjøres hentekommandoen flere ganger samme dag, hentes
ingenting etter første vellykkede henting.

##### Minste historikk: 175 handelsdager

Hver henting skal dekke **minst 175 handelsdager** per symbol. Tallet er ikke
valgt, det er summen av to krav som må oppfylles samtidig:

| Kilde til kravet | Handelsdager |
|---|---:|
| Grafvinduet i FR-201 — seks måneder | 125 |
| MA50 må finnes allerede på grafens *første* punkt (FR-202) | 50 |
| **Sum** | **175** |

Uten de 50 ekstra dagene finnes ikke det glidende snittet for den første delen
av grafen, og MA50-linjen ville startet midt inne i bildet uten at noe feilet.
Sjekk 1 ville da vært usynlig nettopp i den perioden brukeren ser først.

**I praksis hentes et helt år.** Ett kall koster det samme uansett
intervallengde — målt og ført i `malinger.md` §2 — så et kortere intervall ville
kostet nøyaktig like mye og gitt mindre. Gratisnivået gir ett års historikk, og
det er derfor taket, ikke et valg.

*Skrevet inn 2026-09-21.* Kravet manglet. `fetch_prices.py` hentet 364 dager,
og det var tilstrekkelig — men det var en egenskap ved implementasjonen, ikke
noe noe krav ba om. En senere endring som kortet ned intervallet for å «spare»,
ville ødelagt grafen uten å bryte et eneste krav.

Uten denne presiseringen ville 15 kall gått med ved hver oppstart, og oppstart
nummer to samme dag ville sprengt kvoten på 20.

> *Merknad 2026-09-22.* Resonnementet over er bevart slik det ble skrevet.
> Utløseren det beskriver — henting ved oppstart — finnes ikke lenger etter
> omskrivingen av FR-401. Kvoteregnestykket står seg: 15 symboler mot en
> dagskvote på 20 er fortsatt grunnen til at minstehistorikk-kravet ser ut som
> det gjør. Det er ordet «oppstart» som er foreldet, ikke regnestykket.

Rådatalageret svarer på et annet behov, se NFR-07. Hvorfor serien må lastes ned
på nytt: se `begrunnelser.md`.

#### FR-408 — Dagens vurdering lagres per aksje

For hver aksje, **hver dag kommandoen kjøres**, lagres vurderingen slik den
var:

| Felt | Innhold |
|---|---|
| Dato | Børsdagen vurderingen gjelder |
| Signalstyrke | 0–3 |
| Retning | Positiv, negativ, blandet eller ingen |
| De tre sjekkene | Hvilken verdi hver av trend, bevegelse og interesse ga |
| Relevante meldinger | Hvilke meldinger som ble vist for aksjen den dagen |
| Kurs | `close` og `adjusted_close` |

**Lagringen skjer automatisk innenfor en kjøring** — ingen skal måtte be om
vurderingen separat. Den skjer **ikke** automatisk i tid: ingenting utløses av
seg selv, jf. FR-401. Kjøres kommandoen, skrives vurderingen; kjøres den ikke,
skrives ingenting.

Uten lagringen kan spørsmålet «hva sa løsningen om EQNR for to uker siden?»
ikke besvares.

Dette er et tredje lager, med et annet formål enn de to i FR-406: de lagrer
*data fra kilden*, dette lagrer *hva løsningen mente om dem*.

##### Vurderinger etterfylles ikke, og det er med vilje

FR-403 fyller hull i **kursserien** etter dager uten kjøring. Vurderinger
behandles motsatt, og forskjellen følger av hva de to er:

| | Kan etterfylles? | Hvorfor |
|---|---|---|
| **Kurs** for 12.09 | **Ja** | Den er den samme uansett når den hentes |
| **Vurdering** for 12.09 | **Nei** | En vurdering skrevet i dag for 12.09 ville vært *dagens* parametres svar, ikke datidens |

Det er nettopp det dette kravet finnes for å hindre. Lageret skal vise hva
løsningen mente den dagen — og en dag ingen kjørte kommandoen, mente løsningen
ingenting. Da skal det stå at den ikke sa noe.

Håndhevet av arkitekturspinen `AD-7`: `Vurderingslager.skriv` avviser enhver
dato som ikke er inneværende børsdag. En eldre rad er utilgjengelig gjennom
porten, også for skriving.

*Presisert 2026-09-22.* Kravet sa «for hver aksje, hver dag» og «lagringen skjer
automatisk». Begge deler kunne leses som at systemet skriver av seg selv hver
dag, og det motsier FR-401 etter omskrivingen samme dag. Skillet mellom kurser
som etterfylles og vurderinger som ikke gjør det, var ikke skrevet ned før nå.

#### FR-409 — De tre tilstandene skal være skillbare i lageret

Vurderingslageret skal kunne skille tre tilstander fra hverandre **entydig**.
De ser alle tomme ut hvis de ikke skilles:

| Tilstand | Hva det betyr |
|---|---|
| Rad finnes, signalstyrke 0 | **Et gyldig svar.** Sjekkene ga ingen utslag den dagen |
| Ingen rad, og dagen var en børsdag | **Kommandoen ble ikke kjørt.** Et hull i vår egen drift |
| Ingen rad, og dagen var ikke en børsdag | Dagen finnes ikke, og skal ikke telles som noe |

Uten skillet blir en dag vi ikke kjørte, umulig å skille fra en dag uten utslag.
Det første er en mangel hos oss; det andre er et funn om markedet. De skal ikke
kunne forveksles.

**Kravet gjelder lageret, ikke en skjerm.** Det finnes ingen visning av
vurderingshistorikk i v1 — se åpent punkt 20. Skillet må likevel finnes nå,
fordi det ikke kan gjenskapes i ettertid: mangler raden, finnes det ingen måte å
vite om kommandoen ble kjørt den dagen.

**Bindingen gjelder videre.** Enhver visning, kommando eller spørring som senere
leser denne historikken, **skal bevare skillet** — ikke gjengi «ingen rad» og
«styrke 0» som samme tilstand. Står ikke dette her, er grunnen til at kravet
finnes glemt den dagen visningen bygges.

**Ikke dekket av FR-204.** Det kravet gjelder en aksje som ikke kan vurderes
*nå* — for kort historikk eller hull i serien. FR-409 gjelder den lagrede raden
for en dag som allerede har passert.

*Skrevet inn 2026-09-22*, da `AD-17` ble tatt opp igjen og konsekvensen av
`AD-7` ble avgjort eksplisitt. *Rettet samme kveld:* kravet var først formulert
som et visningskrav og lovet at dagen ikke skulle se ut som «et hopp i
historikken» — i en historikkvisning som ikke er spesifisert noe sted.

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

**Hvordan språket avgjøres.** Kravet sa opprinnelig bare «behold den norske»,
og det er ikke implementerbart uten å vite hvilket språk en melding er på.
NewsWeb-målingene dokumenterer feltene `issuerSign`, `issuerName`, `category`,
`publishedTime` og `title` — ingen språkindikator. Regelen er derfor:

1. **Språkkoden fra NewsWeb**, hvis feltet finnes. `[ANTAKELSE]` At det finnes,
   er ikke verifisert. Kontrollen koster ingen kvote og står på lista til
   2026-09-21.
2. **Ellers heuristikk på tittelen.** Æ, ø eller å avgjør alene — de finnes
   ikke i engelske titler. Ellers telles kjente norske ord mot kjente engelske.
3. **Er det uavklart, beholdes den første.** Vi gjetter ikke når vi ikke vet.
   Et vilkårlig valg forkledd som en regel er verre enn en åpen
   førstemann-regel.

Heuristikken er et kompromiss, ikke et ideal. Finnes språkkoden, erstatter den
punkt 2 som hovedregel, og heuristikken blir liggende som reserve.

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

**Kategorier som ikke står i tabellen** går i en egen bøtte. De vises for
brukeren merket **«ukjent kategori»** og føres i loggen, men de sendes **ikke**
til KI-laget: prompten er skrevet for samlekategorien og ville gitt en
vurdering den ikke er kalibrert for. Et svar som ser like sikkert ut som de
andre, men som kommer fra en modell utenfor sitt område, er verre enn ingen
vurdering.

Bøtta er en mellomstasjon, ikke en endestasjon. Etter en ukes drift vet vi
hvilke kategorier som faktisk dukket opp, og plasserer dem bevisst — se åpent
punkt 15.

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

> **Parametrene er låst 2026-09-21.** Terskel, volumfaktor og nøytralsonebredde
> er testet mot **199 handelsdager** (2025-12-01 til 2026-09-18, 2 985
> aksjedager) og beholdt uendret. Metode og tall: `malinger.md` §7.4.
>
> **Alle fem parametrene er nå låst.** De to vinduene — de 20 dagene i
> bevegelsessjekken og de 20 i interessesjekken — var ikke med i testen 21.09,
> som låste tre parametre og ikke fem. De ble målt 2026-09-22 mot de samme
> 2 985 aksjedagene; metode og tall i `malinger.md` §9.

Kravet til signalet er **forklarbarhet, ikke treffsikkerhet**. Vi lover ikke
bedre signaler enn andre, men at brukeren alltid kan se hva som ga utslaget.

#### FR-701 — Tre navngitte sjekker

Signalet består av tre sjekker. Hver gir +1, 0 eller −1. Det finnes ingen fjerde
sjekk, ingen vekting og ingen skjult formel.

| # | Sjekk | Måler | Gir utslag når |
|---|---|---|---|
| 1 | **Trend** | Sluttkurs mot 50-dagers glidende snitt | Kursen ligger mer enn **2 %** over eller under snittet |
| 2 | **Bevegelse** | Dagens endring mot aksjens egen volatilitet | Endringen overstiger ett standardavvik av siste **20** dagers endringer |
| 3 | **Interesse** | Dagens volum mot eget medianvolum | Volumet overstiger **1,5 ×** medianen siste **20** dager |

Fortegnet på **interesse** følger dagens kursendring: høyt volum på en dag med
oppgang gir +1, høyt volum på en dag med nedgang gir −1. Volum har ingen retning
i seg selv.

Alle beregninger bruker `adjusted_close`, slik at et ordinært utbytte ikke
feiltolkes som kursfall.

#### FR-702 — Nøytralsone i trendsjekken

Trendsjekken skal ha en nøytralsone på **±2 %** rundt det glidende snittet.
Innenfor sonen gir sjekken 0.

Uten nøytralsonen kan signalstyrke 0 ikke forekomme: en aksje ligger alltid
enten over eller under sitt eget snitt, så trendsjekken slår alltid ut. Målt
over 2 985 aksjedager er andelen med styrke 0 da **0,0 %**, og 63,9 % havner på
styrke 1. Oversikten kan dermed aldri si at det ikke skjer noe, og det bryter
målet «Dager uten signal».

Med nøytralsonen får **12,7 %** av aksjedagene styrke 0. Bredden er valgt mot
målte alternativer: ±1 % gir bare 5,6 %, ±4 % gir 25,7 % og spiser seks
prosentpoeng av styrke 2 og 3 til sammen. Se `malinger.md` §7.4.

#### FR-703 — Signalstyrke

Signalstyrke er summen av absoluttverdiene til de tre sjekkene, altså et helt
tall fra 0 til 3. Styrken sier hvor kraftig sjekkene slår ut — ikke hvor
sannsynlig en kursbevegelse er, og ikke om aksjen bør kjøpes eller selges.

Målt fordeling over 199 handelsdager og 2 985 aksjedager: styrke 0 hos
**12,7 %**, styrke 1 hos **56,3 %**, styrke 2 hos **23,9 %**, styrke 3 hos
**7,0 %**. Testoppsett og følsomhet for volumfaktoren: `malinger.md` §7.4. Den
første målingen over 15 dager står i §5 til sammenligning.

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

En aksje skiller seg ut den dagen signalstyrken er **2** eller høyere.

Målt over 199 dager gir terskel 2 i snitt 4,6 av de 15 aksjene per dag, og bare
5 dager av 199 helt uten utslag. Terskel 3 ville gitt 1,1 i snitt og 87 tomme
dager — nær annenhver dag uten noe å vise.

Terskelen styrer **visningen og sorteringen**, ikke hentingen.
**Meldinger hentes for alle 15 selskapene ved hver henting**, uavhengig av om
aksjen kommer over terskelen. KI-kostnaden er omtrent 1,25 forklaringer og 0,5
relevansvurderinger per henting.

Hvorfor terskel 2 og ikke 3: se `begrunnelser.md`.

*Endret 2026-09-22.* Setningen sa «hver dag» og «i døgnet». Det var en
frekvensgaranti fra modellen der applikasjonen hentet ved oppstart, og den
motsier FR-401 etter omskrivingen samme dag. Poenget setningen gjør, er
**omfanget per henting** — at terskelen ikke begrenser hva som hentes — og det
er uendret.

#### FR-706 — Synlig begrunnelse i aksjedetaljen

Aksjedetaljen skal liste de tre sjekkene ved navn, med **tre ting per sjekk**:

| Del | Eksempel |
|---|---|
| Navn | Trend |
| Verdien den ga | +1 |
| **Målingen bak verdien** | +3,1 % mot MA50 |

Brukeren skal kunne lese at trend ga +1, bevegelse −1 og interesse −1, se at
styrken derfor ble 3, og se hva hvert fortegn ble målt mot.

**Alle tre sjekkene vises, også de som ga 0.** En sjekk uten utslag er også en
forklaring — den sier at akkurat den tingen ikke skjedde.

##### Hvorfor målingen må med

*Skjerpet 2026-09-21.* Kravet ba tidligere bare om navn og verdi. Det er ikke
nok til å oppfylle kravets eget formål: «Trend +1» kan ikke etterprøves uten å
vite hvor mye over snittet kursen lå. Brukeren ville sett et fortegn og måttet
tro på det — altså nøyaktig den skjulte formelen kravet finnes for å unngå.

Med målingen kan brukeren regne etter:

> Trend +1 (+3,1 % mot MA50) · Bevegelse −1 (−3,5 % mot 1,1 % standardavvik) ·
> Interesse −1 (volum 3 975 318 mot median 802 964) → styrke 3, retning blandet

De tre tallene til høyre er grunnlaget. De to til venstre er utledet av dem.
Ingen vekting og ingen skjult formel. Dette er kravet som gjør signalet
forklarbart, og det er ikke valgfritt — og da kan heller ikke grunnlaget være
det.

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

Henting skjer i en **egen kommando, i en egen prosess** — aldri i webserveren,
og aldri når en side vises. Webserveren viser **alltid** siste kjente data med
tidsstempel: ikke fordi en henting pågår, men fordi den aldri henter.

*Endret 2026-09-22.* Kravet lovet opprinnelig en bakgrunnsoppgave med samtidig
visning. Utfallet er uendret — brukeren venter fortsatt aldri — men mekanismen
finnes ikke lenger etter omskrivingen av FR-401, og et krav som beskriver en
bakgrunnsjobb i webserveren, ville ført en utvikler til å bryte AD-10.

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
| Drift | Én henting fullfører innenfor kvoten; ved kildefeil vises siste kjente data med tidsstempel | **Én kommando gjør hele hentingen.** Ingen skjulte steg, ingenting som må huskes utenom den — **migrasjoner er uttrykkelig ikke et eget steg**. Ingen stopp ved manglende data | Ukentlig |
| Dager uten signal | Dager uten tydelige signaler håndteres uten at hovedflyten stopper eller systemet tvinger frem et resultat | Signalstyrke 0 forekommer og vises korrekt | Løpende |
| KI-bidrag i drift | Hvilke meldinger KI-laget forklarte eller omklassifiserte som regelfilteret alene ikke klarte å skille | Dokumentert eksempelsett fra minst én ukes drift | Før demonstrasjonen, est. uke 45 |
| Relevanseksperiment | Testsett på ~50 medieartikler fra åtte selskaper, merket manuelt, kjørt mot både symbolmatching og KI-klassifisering | Eksperimentet gjennomført og tallene dokumentert — ikke at KI kommer best ut | **Del 1** innsamling og merking, uke 39–40. **Del 2** KI-kjøringen, når KI-laget finnes |
| Fortsatt bruk | Om vi bruker løsningen frivillig etter at utviklingen er ferdig, ikke bare for å teste den | Minst tre dager i uka de to siste ukene, loggført | Ved prosjektinnlevering |
| Grensesnitt og stabilitet | Hovedflyten fungerer uten feil og med et ryddig, gjennomarbeidet grensesnitt i en demonstrasjon | Hovedflyten gjennomført uten feil eller manuelle inngrep | Ved demonstrasjonen |

**Hovedflyten** er definert som: åpne markedsoversikten, se hvilke aksjer som
skiller seg ut, åpne én av dem, og lese hvorfor — de tre sjekkene med verdiene
sine, og meldingene som gjelder. Både brukerutfallsmålet og stabilitetsmålet
måler denne flyten.

**Bundet til datoer som ikke er fastsatt:** FR-407, FR-601 og FR-408, og målene
«KI-bidrag i drift» og «Grensesnitt og stabilitet». Se åpent punkt 13.

*Endret 2026-09-22.* Terskelen sa «Ingen manuelle steg». Den målte **to**
egenskaper, og FR-401 har skilt dem fra hverandre:

| | Status |
|---|---|
| Ingenting utløses av et menneske | **Gitt opp. Det var et valg.** En container startes på nytt hver gang, så «ved oppstart» ville betydd 15 kall per `docker run` mot en dagskvote på 20 — to kjøringer samme dag hadde brukt opp dagen. FR-401 og `AD-10` |
| Når hentingen først er utløst, må ingenting annet huskes | **Beholdt.** Det er denne halvdelen terskelen nå måler, og `AD-17` finnes for å sikre den: vurderingen skrives i samme kjøring, så det ikke oppstår et steg to |

Målet er omformulert og ikke strøket, fordi den andre halvdelen er ønsket og
ikke måles noe annet sted. Men **den første halvdelen er oppgitt, ikke myknet
opp** — det skal stå, ellers ser omformuleringen ut som at målet ble justert til
å passe det vi bygde.

**Hva som mest sannsynlig bryter terskelen:** at migrasjonene blir en egen
kommando. Arkitekturspinen fører «Hvem kjører migrasjonene, og når» som utsatt —
`AD-16` sier at de finnes, ikke hvem som anvender dem. Et svar som deler dem ut
i `docker run … migrer` ville sett ut som ryddig ansvarsdeling og brutt målet.
**Det skal leses når Dockerfilen skrives.**

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
| 1 | **Vilkårskontroll — to av tre deler lukket 2026-09-21.** *Lukket:* EODHD har svart skriftlig ja til språkmodellbruk, med fire betingelser, og kontrollen av NewsWeb og Euronext er gjennomført. *Åpent:* kontrollen ga et **uttrykkelig forbud** mot automatisert henting uten tillatelse på forhånd. Forespørsel sendt 21.09, **purret 22.09 i samme tråd** — purringen dekker både de fire opprinnelige delene og overføring til en modelltjeneste (punkt 19), og tilbyr et smalere alternativ. Svar avventes. Holder ikke unntaket, må meldingsdelen omdisponeres. **Kontrollert 22.09: EODHDs `/api/news` er ikke en reservekilde** — den koster 75 kall i døgnet for universet mot en kvote på 20, innholdet er syndikert fra tredjepart via Yahoo, og taksonomien er **tematisk og ikke regulatorisk**, så FR-502s tre bøtter måtte bygges om fra grunnen. Vurderingen med tall i `malinger.md` §10. Et nei tar derfor hele KI-laget med seg | Gruppen | **2026-09-28** | Meldingsdelen |
| 2 | **KI-terskelen i samlekategorien** — hvor grensen mellom «kan påvirke» og «lite relevant» skal gå. Kan ikke avgjøres på papir; relevanseksperimentet er input. Foreløpig regel står i FR-606 | *‹fylles inn›* | Etter del 2 av relevanseksperimentet | Kalibrering av FR-606 |
| 3 | **Hvilken kilde gir handelskalenderen?** FR-402 hviler på «forventet børsdag», men ingen kilde er utpekt for hvilke dager Oslo Børs er åpen | *‹fylles inn›* | Før implementasjon | FR-402 |
| 4 | **Hvordan utledes eks.dato?** FR-407 og FR-503 forutsetter at utbyttedager kan identifiseres. **En målt vei finnes, funnet 2026-09-21:** avviket mellom close-endringen og `adjusted_close`-endringen peker ut dagen justeringen skjedde. 38 hendelser over 3 720 dagovergangner, og antallet står stille fra 0,05 til 0,5 prosentpoeng — et rent skille, så terskelen kan begrunnes i stedet for velges. **Konsekvensen er større enn kravet:** FR-407 blir da uavhengig av EKS.DATO-meldinger, og dermed av NewsWeb og punkt 1. Se `begrunnelser.md` §11 | Gruppen | Før demonstrasjonen | FR-407, FR-503 |
| 16 | **Språkgjenkjenningen slår systematisk feil for Vår Energi.** `gjett_spraak` lar ett norsk tegn avgjøre alene, og `VAR` heter *Vår Energi ASA*. Hver engelsk melding derfra bærer «å» i sitt eget firmanavn og leses som norsk, så FR-501 vil beholde den engelske versjonen hver gang selskapet sender et meldingspar. Dette er ikke en kantsituasjon — det er hver gang, for én av de femten, og det vises i en norsk applikasjon. **To forsvarlige veier:** bygge om språkregelen, eller la den stå og forklare avviket i demonstrasjonen. Det som ikke er forsvarlig er at valget tas ved at ingen tar det opp | Gruppen | **Før UI-arbeidet starter** | FR-501, demonstrasjonen |
| 20 | **Hvordan skal FR-408s eget spørsmål kunne stilles?** Kravet begrunner seg med «hva sa løsningen om EQNR for to uker siden?», men ingen visning, kommando eller spørring i v1 svarer på det. Historikken er da **lagret, men ikke besvarbar**. Tre veier: en visning i aksjedetaljen, en egen kommando, eller en direkte spørring mot basen under demonstrasjonen. FR-409 binder alle tre til å bevare skillet mellom «ingen rad» og «styrke 0» | Gruppen | **Før demonstrasjonen** | FR-408s begrunnelse |
| 19 | **Forespørselen til Euronext ba aldri om å sende innhold til en modelltjeneste.** Vilkårene forbyr å «otherwise transfer any of the Content to any third person», og parentesen strekker det til «others in your company or organisation» — altså svært bredt. Å sende meldingstekst inn i en språkmodell er en slik overføring. Brevet 21.09 beskriver fire ting — Retrieval, Storage, Display, Source code — og **ingen av dem nevner en modelltjeneste**; kontrollert 22.09, null treff på «language model», «LLM», «third person» og «third party» i hele brevet. Manuell innsamling løser klausul 1 om automatisert henting, men **ikke** overføringsklausulen. **Konsekvens: selv et fullt ja på alle fire delene lukker ikke dette.** Det må stilles som eget spørsmål. Kalenderspørsmålet i samme brev hjelper ikke: det ber om «the same answer» og arver dermed de fire overskriftenes rekkevidde, inkludert utelatelsen. **Purret 22.09, og purringen dekker begge deler** — de fire opprinnelige og overføringen — så et kort svar kan ikke lenger se fullstendig ut mens det bare dekker det ene. Purringen tilbyr også et smalere alternativ: et lite, manuelt innsamlet utvalg brukt én gang. Ordrett i `docs/epost-til-euronext.md` | Gruppen | **Sammen med punkt 1, 2026-09-28** | Plan B for relevanseksperimentet; KI-laget over NewsWeb-innhold |

### Må følges opp

| # | Punkt | Eier | Frist |
|---|---|---|---|
| 5 | **Relevanseksperimentet, del 1: utvalgskriterier, innsamling og manuell merking.** Flyttet fram fra uke 41 den 2026-09-21. Uke 41 ble satt mens eksperimentet var blokkert av to ting — om vilkårene tillot språkmodellbruk, og om `/api/news` svarte for `.OL`. **Begge ble avklart 21.09**, men datoen ble aldri flyttet etterpå. Rekkefølge: (a) utvalgskriteriene skriftlig — hvilke åtte selskaper, hvor mange artikler per selskap, og hva som teller som at en artikkel handler om selskapet; (b) innsamlingen, med kalltall-kontrollen som **første** forespørsel: to tickere, og se om `apiRequests` flytter seg 10 eller 15, så kostnaden for resten er kjent før den brukes. Tas fra bonuskvoten `extraLimit` 485 — men den er observert, ikke testet, se `malinger.md` §7.1 | Gruppen | Etter punkt 17 og 18 |
| 5b | **Relevanseksperimentet, del 2: KI-klassifiseringen.** Kan ikke gjøres ennå, og det er tre grunner, ikke én: KI-laget finnes ikke som kode, ingen modelltjeneste er valgt, og **betingelse 4 i EODHDs godkjenning — at modelltjenesten ikke trener på innholdet — er udokumentert.** Den må være ført før artikkeltekst sendes inn i en modell, se `docs/kilder-og-rettigheter.md` | Gruppen | Når KI-laget finnes |
| 6 | **Usikkerhetskriteriene er skrevet for medieartikler.** Kjennetegn 1 bærer svakt når utstederen selv er avsender | | Før KI-laget implementeres |
| 8 | **Oppstart av tilbakekjøpsprogram** er ekte nyhet, men filtreres bort sammen med de ukentlige statusrapportene | | Før innlevering |
| 9 | **Kontrollere Alpha Vantages vilkår** for ikke-kommersiell bruk | | Før innlevering |
| 10 | **Skjevfordeling mot positiv retning**, 68 % i testen. Vurderes mot året, ikke mot femten dager | | Etter utvidet test |
| 11 | **Meldepliktig handel for primærinnsidere** justeres hvis den viser seg å være i hovedsak opsjonsutøvelse | | Etter én ukes drift |
| 12 | **Bekrefte horisont og hendelsestyper** i FR-302, som i dag er antatt | | Før implementasjon |
| 13 | **Datoer for demonstrasjon og prosjektinnlevering.** Spørsmål sendt faglærer i Teams 2026-09-22, sammen med spørsmål om leveranselista er fullstendig og om noen BMAD-dokumenter skal leveres inn. **Besvart av hjelpelærer 2026-09-23: ingen dato finnes ennå** — «Bård Inge vil presisere dette». Åtte suksessmål i §7 er bundet til disse datoene, og «est. uke 45» er vår egen estimering — ikke en oppgitt dato. Se `docs/innlevering.md` | Marian | **Avventer Bård Inge** (spurt 22.09, besvart 23.09) |
| 15 | **Plassér kategoriene som havnet i «ukjent»** i riktig bøtte. Krever en ukes drift for å vite hvilke som faktisk dukker opp | | Etter én ukes drift |
| 21 | **Hva er emnesidens tredje del?** Emnesiden sier «tre deler», men lister to, og nevner at «delvurdering 3 gir anledning til å demonstrere unike bidrag». Hva den tredje delen er, er ikke oppgitt. Spørres Bård Inge sammen med datoene i punkt 13. Se `docs/innlevering.md`, «Eksamen» | Marian | Sammen med punkt 13 |
| 22 | **Kodegjennomgang som BMAD-steg, én per epic.** `bmad-code-review` kjøres etter hver ferdige epic, første gang etter Epic 1. Emnesiden: «Dokumentasjon må vise hvordan KI ble brukt, og hvordan studentene har kvalitetssikret koden» — en gjennomgang med flere uavhengige lesere er en del av det, i tillegg til testene og mutantene. Lagt til 2026-09-23 | Gruppen | Etter Epic 1 |

### Lukket

Punkter som er avgjort. De står igjen med hva som lukket dem, ikke slettet —
uten det kan ingen se at de var åpne, eller hva som måtte til.

| # | Punkt | Lukket av | Dato |
|---|---|---|---|
| 7 | **Låsing av signalparametre** mot ~200 handelsdager | `malinger.md` §7.4 låste terskel, volumfaktor og nøytralsone mot 199 handelsdager; §9 låste de to vinduene mot like mange aksjedager, 2 985, forskjøvet én handelsdag. **Punktet anslo 15 kall. Det kostet 0** — begge målingene ble gjort mot lagrede øyeblikksbilder | 21.09 og 22.09 |
| 14 | **Hver story leveres med test**, kjørbar uten API-kall | Skrevet inn som `AD-8` i arkitekturspinen. Praksisen var allerede innført: `tests/conftest.py` sperrer `socket.connect`, og CI kjører uten hemmeligheter | 22.09 |
| 17 | **Database** | SQLite besluttet i arkitekturfasen — spinen `AD-3` til `AD-7`, `AD-16`, `AD-18`, `AD-19`. Rådata forblir filer. **Kontrollert med faglærerstaben 22.09** og bekreftet av assisterende hjelpelærer: «Slik dere beskriver bruken […] bruker dere SQLite som en ordentlig database, ikke bare som enkel fillagring. […] Så ut fra det vi vet nå mener jeg dette er helt innenfor.» Svaret kom ikke fra emneansvarlig og bærer sitt eget forbehold | 22.09 |
| 18 | **Dockerfile** | Arkitekturen besluttet: `AD-9` (ingen data i imaget), `AD-10` (webserveren henter aldri), `AD-11` (to volumer), `AD-12` (hemmeligheter fra miljøet). **Merk at selve filen ikke er skrevet** — punktet gjaldt beslutningen, og bygget står i `docs/innlevering.md` | 22.09 |

**Punkt 1 og 19 er de to som kan velte datagrunnlaget.** Punkt 1 velter nå bare
én ting, ikke to. Punkt 19 kom til 22.09 og treffer meldingsdelen og KI-laget
sammen.

*Oppdatert 2026-09-21.* EODHD-halvdelen er lukket: språkmodellbruken er
skriftlig godkjent, og `/api/news` er målt til å svare for `.OL`-tickere.
Relevanseksperimentet kjøres derfor på plan A og deler ikke lenger kilde med
meldingsdelen. Det som står igjen, er Euronext: vilkårene som dekker NewsWeb
forbyr uttrykkelig automatisert henting uten tillatelse på forhånd, og
forespørselen om tillatelse ble sendt 21.09 og er ubesvart. Fristen 28.09 er vår
egen frist for å ta stilling uten svar, ikke en dato Euronext har lovet.
Fullstendig
gjennomgang med sitater i `docs/kilder-og-rettigheter.md`.

Av de åpne punktene har 1, 4, 5, 5b, 13, 16, 19, 20, 21 og 22 eier. Punkt 2, 3, 6, 8–12 og 15 mangler det. Punkt 7, 14, 17 og 18 er lukket. *Rettet 2026-09-23: setningen talte lukkede punkter blant de åpne, og manglet 13, 20 og 21.*

**Om nummereringen.** Numrene følger rekkefølgen punktene ble opprettet i, ikke
rekkefølgen i tabellene. Punkt 16 står derfor over sammen med de andre som må
avgjøres, selv om numrene 5–15 ligger i tabellen under. Det er gjort for at
kryssreferanser fra `malinger.md` og gjennomgangene skal forbli gyldige — et
punkt som renummereres, mister sporet tilbake til målingen som begrunnet det.

**Om eierfeltet.** «Gruppen» er et bevisst valg, ikke en tom rubrikk: vi er to,
og fordelingen gjøres internt etter hva som passer når punktet skal tas. Det
eierfeltet skal sikre, er at punktet har en frist og noen som svarer for den —
ikke at navnet er låst på forhånd. Punkt 2, 3, 6, 8–12 og 15 har frist, men mangler eier.
