---
title: "PRD — OSE Signal"
status: final
created: 2026-09-20
# updated settes fra klokka, aldri for hånd:
#   date +%Y-%m-%dT%H:%M   (lokal tid, samme som memloggen)
# Feltet sto på 2026-09-20 mens fem commits den 21.09 hadde endret dokumentet.
updated: 2026-10-03T12:56
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
kravene selv, og 130 av linjene her er tabellrader som *er* krav: kolonnene i
markedsoversikten, de ti kategoriene med bøtte, feltene som skal lagres,
suksessmålene og de åpne punktene. Å komme under 11 sider krever at krav går ut,
ikke at teksten strammes. *Talt på nytt 2026-09-24: 130 datarader, uten
overskrift- og skillelinjer. Her sto 115; da det ble skrevet, hadde fila 114
tabellinjer medregnet overskrift- og skillelinjer.*

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
- Børsmeldinger sortert av regler og forklart av KI *Ute av v1 fra 2026-09-28 (plan B, punkt 1 i §8).*
- Av/på-bryter for KI-laget, synlig i grensesnittet
- Kommende finansielle hendelser *Ute av v1 fra 2026-09-28 (plan B, punkt 1 i §8).*
- Lenke fra aksjedetaljen til selskapets side på NewsWeb *(plan B, 28.09)*
- Lenke fra aksjedetaljen til selskapets egen nettside, på norsk der den finnes *(lagt til 2026-09-30)*
- Tickeren fra Oslo Børs står ved selskapsnavnet i aksjedetaljen, for eksempel EQNR *(lagt til 2026-09-30)*
- Hovedindeksen OSEBX i markedsoversikten, med søyler for dagens endring per aksje (FR-104, FR-105, FR-410) *(lagt til 2026-10-01, Marians beslutning)*
- «Se nærmere» i aksjedetaljen: tre ting brukeren kan sjekke selv (FR-205) *(lagt til 2026-10-02, Marians beslutning)*
- KI-tekst om dagen på forsiden, under tabellen (FR-607) *(lagt til 2026-10-02, Marians beslutning)*

*Plan B, 2026-09-28:* KI-laget forklarer signalet i stedet for børsmeldingene, ut fra tall regnet av kursene (Epic 10). Av/på-bryteren står. FR-601–606 er skrevet om for plan B 2026-09-28, og meldingsversjonen står i §4.6A. *Her sto:* «FR-601–606 skrives om for plan B i en egen runde.»

Løsningen er en **webapplikasjon for PC**. Mobiltilpasning er utenfor v1, og
plattformvalget er dermed låst.

Første versjon er på norsk og kjører lokalt.

### Hvis vi rekker

- Favorittmerking av aksjer, slik at egne aksjer ikke havner tilfeldig i lista
  *Flyttet til v1 2026-09-30:* story 8.3, som eget skjermbilde (Marians beslutning).
- Flere valgbare tidsperioder i kursgrafen enn de faste seks månedene
- OSEBX som referanseindeks. Koster ett API-kall i døgnet og ville redusert
  marginen fra fem til fire; det er heller ikke kontrollert om indeksdata er
  tilgjengelig på EODHDs gratisnivå. *Rettet 2026-09-30:* kontrollert med ett
  kall. Gratisnivået gir indeksdata for `OSEBX.OL`: HTTP 200 og ett års serie
  med de samme feltene som aksjene (`malinger.md` §14)
  *Flyttet til v1 2026-10-01, Marians beslutning:* FR-104, FR-105 og FR-410.

### Utenfor v1

Brukerkontoer, innlogging og personlig portefølje; varsler, betaling,
mobiltilpasning og meglerintegrasjon; flere børser og flere språk;
fundamental- og verdimodell; intradag- og sanntidsdata; statistisk studie av om
signalene slår markedet.

### Utsatte vurderinger

Tre vurderinger er utsatt til løsningen eventuelt publiseres:
**videreformidlingsrett**, **personvern**, og **regelverket som gjelder når en
tjeneste presenterer finansielle signaler**.

*Rettet 2026-09-24:* videreformidlingsretten er ikke lenger utsatt. Vilkårene
til EODHD og til Euronext, som dekker NewsWeb, ble kontrollert 2026-09-21. Se
`docs/kilder-og-rettigheter.md` og åpent punkt 1.

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
| Retning | Positiv, Negativ, Blandet eller Ingen, jf. FR-704 *(rettet 2026-09-23 fra «Opp, Ned»)* |

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

##### Hvor gamle dataene er

*Endret 2026-09-23.* Sidens tidsstempel er det **eldste** `sist_hentet` blant
symbolene som vises. En rad med eldre tidsstempel enn det nyeste viser sitt
eget, i selskapscellen under navnet — ikke som en sjette kolonne. Tidsstempler
vises i norsk tid (lagret i UTC, AD-20).

Begrunnelse: AD-15 lar ett symbol feile og beholde sin gamle serie. Viste siden
det nyeste tidspunktet, ville en side med én fersk rad og fjorten foreldede sett
fersk ut.

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

*Endret 2026-09-23.* **Tidsstempelet påvirker ikke sorteringen.** En rad med
eldre data sorteres etter samme regel som de andre, ikke sist. Sorteringen er
signalets, ikke ferskhetens, og ferskheten vises på raden (FR-101).

Merk at styrken bare har fire verdier fordelt på femten rader, så lik styrke er
normalen og ikke unntaket. Målingen 2026-09-21 viste 13 av 15 aksjer på styrke
2 eller høyere for 2026-09-18. **Sekundærkriteriet gjør derfor mesteparten av
sorteringsarbeidet**, og det er verdt å vite når rekkefølgen skal forklares i
en demonstrasjon.

At brukerens egne aksjer havner tilfeldig i lista, er akseptert i v1.
Favorittmerking hører til «hvis vi rekker».
*Flyttet til v1 2026-09-30:* story 8.3, som eget skjermbilde (Marians beslutning).

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

#### FR-104 — Hovedindeksen i markedsoversikten

*Lagt til 2026-10-01, Marians beslutning.*

Over tabellen står overskriften «Hovedindeksen» med OSEBX ved siden av,
indeksverdien (`close` for indeksens siste børsdag), dagens endring i prosent og
«x av N gikk bedre enn indeksen». Ingenting av dette er en kolonne: FR-101 står
med fem.

- Endringen regnes mot forrige børsdag, ikke mot forrige rad, fordi indeksen har
  datoer aksjene ikke har (`malinger.md` §14). `close` og `adjusted_close` er like
  for indeksen (§14), så den sammenlignes med aksjenes endring fra FR-101.
- N er aksjene med kurs for samme dato som indeksen, aldri et fast 15 (føringen
  30.09 under `AD-21`). En aksje som ikke er med, navngis, slik FR-101 navngir
  aksjer som mangler. Mangler én aksje dagens kurs, står det «x av 14».
- «Bedre» avgjøres på endringen slik den vises, og lik er ikke bedre.
- Har ingen aksje kurs for indeksens dato, vises ikke sammenligningen. Mangler
  indeksen, står siste lagrede verdi med datoen sin, eller at indeksen mangler
  (NFR-03). Hentingen står i FR-410.

#### FR-105 — Søylene under hovedindeksen

*Lagt til 2026-10-01, Marians beslutning.*

Under indeksen (FR-104) står én søyle per aksje med dagens endring, fra størst
fall til størst stigning. Over hver søyle står bransjesymbolet, over tickeren.
Indeksens endring er en stiplet linje, grønn når indeksen steg og rød når den
falt.

- Antallet telles (føringen 30.09 under `AD-21`). En aksje uten kurs for
  indeksens dato får ingen søyle.
- Søylene har en tekst for skjermleser med alle tallene.
- Ingen nye kall og ingen ny lagring: endringen er den i FR-101, og bransjen står
  i `AKSJEUNIVERS`.
- Bare dagens søyler. Periodene og «Velg dag» fra designtavla er idé til v1.1.

*Lagt til 2026-10-01:* bransjesymbolet er gult når aksjen har 3 av 3 på siste børsdag (designregler.md §3).

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
- Børsmeldinger som passerte filteret, med lenke til originalen på NewsWeb *Ute av v1 fra 2026-09-28 (plan B).*
- KI-forklaring per melding når KI-laget er på, eller «ikke vurdert» når det er
  av (FR-602A) *Ute av v1 fra 2026-09-28 (plan B).*
- Kommende finansielle hendelser fra Euronext *Ute av v1 fra 2026-09-28 (plan B).*
- KI-teksten under regelforklaringen når KI-laget er på (FR-602) *(plan B, 2026-09-28)*
- Én lenke til selskapets side på NewsWeb. Lenken hentes aldri av programmet:
  brukeren klikker, og siden åpnes i nettleseren. Ingen kode i `src/` henter fra
  NewsWeb (Euronexts vilkår, punkt 1 i §8). Adressen og det vilkårene sier om
  lenker, slås opp av en av oss før lenken bygges *(plan B, 2026-09-28)*

*Ute av v1 fra 2026-09-28 (plan B).* *Lagt til 2026-09-25:* over meldingene står en teller for hvor mange som ble
funnet og hvor mange som vises, med grunnen til at resten er skjult: filtrert
bort etter kategori (FR-502) eller vurdert som «lite relevant» (FR-606A). En
bryter veksler mellom **Anbefalt**, som er filteret over, og **Alle**, som også
viser det som er skjult, merket med grunnen. Eks.dato er fortsatt merking, ikke
melding (FR-503). Bryteren endrer bare visningen, ikke hva KI-laget vurderer.
KI-forklaringen per melding ligger bak «Vis forklaring». Teksten er laget i
hentingen, og et klikk viser den, men lager den ikke (NFR-02).

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

#### FR-205 — Se nærmere

*Lagt til 2026-10-02, Marians beslutning (story 8.4).*

Aksjedetaljen har delen «Se nærmere», rett under kursgrafen, med tre spørsmål brukeren kan sjekke selv. Den gir ikke råd (NFR-06). Svarene regnes av tall appen allerede har, uten nye kall og uten ny tabell.

1. «Børsen, bransjen eller selskapet?»: aksjens endring mot hovedindeksen (FR-104) og mot snittet av de andre i samme bransje i lista som er aktiv. Svarene er «Børsen», «Bransjen», «Selskapet», «Selskapet eller bransjen» når aksjen er alene i bransjen, og «Liten bevegelse». Grensene avgjøres i spesifikasjonen og står i `Parametre`. Svaret sier hvor bevegelsen ser ut til å komme fra, ikke hvorfor.
2. «Står det noe i børsmeldingene?»: lenken til NewsWeb fra FR-203 står her.
3. «Er en slik dag vanlig for aksjen?»: dagens endring mot standardavviket, og volumet mot medianen, slik de er lagret i vurderingen (FR-408).

Mangler et tall, står grunnen, ikke et gjettet svar (NFR-03).

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

*Avgjort 2026-09-29, gjelder når story 2.3 er bygget.* Da endres kravet slik
at hentekommandoen kan startes av en planlagt jobb på Marians PC:
Oppgaveplanlegging i Windows, hverdager kl. 22:15. Tapte kjøringer tas ikke
igjen, og utskriften går til en loggfil i `data/`. Grunnene: punkt 23 har lagt
kjøringen til kl. 22:00–midnatt, 2.3 gjør kommandoen trygg å starte når som
helst, og etter 2.5 er en dag uten henting en vurdering som mangler for alltid
(AD-7). Til da kjøres hentingen for hånd, og kravteksten over står uendret.

#### FR-402 — Kontroll mot forventet børsdag, ikke mot klokkeslett

Hentingen skal ikke anta at data er ferske fordi klokka har passert et
tidspunkt. Den skal kontrollere at nyeste `date` i svaret er forventet børsdag.

Er nyeste `date` ikke forventet børsdag, vises siste kjente data med
tidsstempel, og hentingen prøves igjen ved neste kjøring av hentekommandoen.
Applikasjonen skal aldri presentere gårsdagens tall som dagens.

Kontrollen eies av hentekommandoen alene — webserveren henter ikke, og kan
derfor ikke handle på utfallet. «Forventet børsdag» regnes i norsk
kalenderdato; se arkitekturspinen AD-20. Hva en børsdag er, står i punkt 3 i §8, lukket 2026-09-27.

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
| Målingene | Tallet hver sjekk ble avgjort av: avviket fra MA50, dagens endring og standardavviket den måles mot, og volumet som forholdstall mot medianen. Uavrundet, som brøk, ikke prosent, i samme enhet som regelen regner i. Forholdstallet mangler bare når medianvolumet er 0, og da er interesse 0. *Lagt til 2026-09-29* |
| Relevante meldinger | Hvilke meldinger som ble vist for aksjen den dagen |
| Kurs | `close` og `adjusted_close` |
| Grunn | Bare når vurderingen mangler: hvorfor (punkt 24 i §8) |

*Lagt til 2026-09-29, avgjort av gruppen 28.09.* Målingene lagres fordi en
vurdering skal kunne etterprøves og sjekkes. Et fortegn uten måling kan ikke det
(FR-706): «trend +1» sier ikke hvor langt over snittet kursen lå. Med målingen
kan fortegnet regnes etter fra raden alene, med de låste parametrene (AD-13).
Endres en parameter, føres det i `malinger.md` (AD-13) med datoen den nye
grensen gjelder fra, så en eldre rad leses med grensene som gjaldt da.

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
porten, også for skriving. Hva en børsdag er, står i punkt 3 i §8, lukket 2026-09-27. Hvordan spørsmålet stilles i appen, står i punkt 20 i §8, lukket 2026-09-27.

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

*Avgjort 2026-09-27 (punkt 24 i §8):* kan kjøringen ikke vurdere en aksje,
skriver den en rad med grunnen i stedet. Det er fortsatt tre tilstander: raden
finnes, men bærer grunnen i stedet for vurderingen. En slik rad er verken styrke
0 eller et hull i driften, og ingen rad på en børsdag betyr bare at kommandoen
ikke ble kjørt.

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

#### FR-410 — Hovedindeksen hentes i samme kjøring

*Lagt til 2026-10-01, Marians beslutning.*

Hentekommandoen henter `OSEBX.OL` med ett kall per kjøring, med samme intervall
som aksjene. Daglig henting koster da 16 kall (NFR-01).

- Rådata lagres i samme øyeblikksbilde som aksjene, under en egen nøkkel og ikke
  blant aksjeseriene (FR-406, NFR-07).
- Indeksen lagres i en egen tabell, `indeks`, aldri i `aksje`, `kurs`, `kursserie`
  eller `vurdering` (føringen 2026-10-01 under `AD-21`). Migreringen er `0006`,
  etter `ki_logg` i `0005` (`AD-16`). Tabellen kan bygges opp igjen fra kilden,
  som `kurs` (`AD-7`).
- Bare børsdager lagres, i årene kalenderen dekker (`DEKKEDE_AAR` i
  `boersdag.py`), uten et fast årstall i koden.
- Webserveren henter aldri indeksen (`AD-10`).
- Feiler indekskallet, lagres og vurderes aksjene som vanlig. Indeksen føres i
  `feil` og får ingen ny sjanse (`AD-15`), og den gir aldri en rad i `vurdering`.

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
   2026-09-21. *Merknad 2026-09-26:* kontrollert 2026-09-21 og avkreftet.
   Meldingsobjektet har ikke noe språkfelt (`malinger.md` §7.3), så punkt 2 er
   hovedregelen.
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

*Skrevet om 2026-09-28 for plan B* (punkt 1 i §8). Kravene for KI-laget over
meldinger står ordrett i 4.6A. FR-601 og FR-605 gjelder begge planene.

KI forklarer signalet med ord, for én aksje om gangen, i aksjedetaljen. Regler
regner, og KI formulerer. Bidraget er **forståelighet, ikke informasjon**: med
bare tall regnet av kursene kan KI ikke vite noe reglene ikke vet, men den kan
si det slik at en person forstår det første gang. Det er et mindre bidrag enn
forklaringen av meldinger ville vært, og det skal stå slik.

Grensen mot regelbasert kode: KI får bare utledede verdier, aldri rådata fra
kilden (story 10.1). Teksten lages i hentekommandoen, ikke når siden vises
(NFR-02), og står under regelforklaringen, aldri i stedet for den (FR-602).

Om EODHD skal spørres før tallene sendes til en modell, er et åpent punkt under
«Å følge opp» i `docs/kilder-og-rettigheter.md` («Plan B for KI-laget: spørre
EODHD eller ikke?»). Story 10.2 er blokkert til det er avgjort.

#### FR-601 — Av/på-bryteren er brukersynlig

KI-laget skal kunne slås av og på fra grensesnittet. Bryteren er ikke et
utviklerflagg i en konfigurasjonsfil, fordi bidraget skal kunne vises fram under
demonstrasjonen mens noen ser på.

I v1 slår bryteren av og på KI-teksten i aksjedetaljen (FR-602). *Lagt til 2026-10-02:* Bryteren gjelder også KI-teksten om dagen på forsiden (FR-607). Én bryter styrer begge.

#### FR-602 — Visningen når KI-laget er av

Med laget av er forklaringen i aksjedetaljen de tre sjekkene med verdiene og
målingene sine (FR-706), uten KI-tekst. Med laget på står KI-teksten **under**
regelforklaringen, merket som laget av KI, med modellnavnet. Regelforklaringen
vises alltid, og KI-teksten erstatter den aldri. En dag uten KI-tekst sier det,
i stedet for å vise et tomt felt.

KI-teksten vises bare når grunnlaget i loggen (FR-604) stemmer med vurderingen
som vises: samme styrke, samme retning, samme fortegn for de tre sjekkene, og
samme målinger, avrundet som i FR-706. Ellers vises siden som en dag uten
KI-tekst. *Rettet 2026-09-29:* her sto «samme styrke, samme retning og samme
fortegn for de tre sjekkene» og «Målingene lagres ikke i vurderingen (FR-408),
så de kan ikke sammenlignes der.» Målingene lagres fra story 2.1c (FR-408).

Begrunnelsen er den samme som i FR-602A: av og på skal kunne sammenlignes, og
det eneste som skiller dem, er KI-teksten. Bidraget er **forståelighet, ikke
informasjon**: KI-teksten sier det samme som regelforklaringen, i hele setninger.

#### FR-603 — KI-teksten sier ikke mer enn grunnlaget

KI-teksten kontrolleres mot grunnlaget som ble sendt (story 10.1), før den
kan vises. Kontrollen er én ren funksjon, som hentekommandoen kaller når
teksten lages (story 10.2), og den testes med en falsk modell (AD-8). Den bygger
på kjennetegn som kan observeres, ikke på en sikkerhetsscore fra modellen:

1. **Retning og styrke.** Sier teksten hva retningen eller styrken er, skal det
   være regelens. Det sjekkes der teksten sier det, som «retningen er blandet»,
   ikke som enkeltord. «Positiv» og «negativ» står naturlig i en tekst om
   retningen Blandet, og «ingen» er et vanlig ord.
2. **Tallene.** Hvert tall i teksten står i grunnlaget, med samme avrunding som
   i FR-706, eller er et av regelens faste tall, som 50 i MA50.
3. **Råd.** Teksten har ingen ord som gir råd (NFR-06).
4. **Gjetning.** Teksten gjetter ikke. Den har ingen ord som gjetter eller spår,
   som «trolig», «sannsynligvis», «kan tyde på» eller «forventes», og nevner
   ingen årsak som ikke står i grunnlaget, som nyheter, resultater eller
   kontrakter. Grunnlaget har bare fortegn og målinger for de tre sjekkene,
   styrken og retningen (story 10.1), så en årsak i teksten er alltid gjettet.
   Ordene står i lister i kontrollen, og en test viser at hvert av dem stopper
   teksten. *Lagt til 2026-10-01, Marians beslutning.*

En tekst som ikke består, vises ikke, men logges med grunnen (FR-604). Aksjen
får da ingen KI-tekst den dagen, og siden sier det (FR-602).

**Kontrollen er grov.** Den fanger feil tall og feil retning, ikke en misvisende
tekst med riktige tall.

*Lagt til 2026-10-01:* punkt 4 fanger ord, ikke mening.

#### FR-604 — Logging av KI-bidraget, fra første kjøring

For hver aksje og børsdag KI-laget forklarer, lagres én rad:

| Felt | Hvorfor |
|---|---|
| Aksje og børsdag | Emnet. Det samme paret som vurderingen (FR-408), så KI-teksten kan leses sammen med den |
| Grunnlaget som ble sendt (story 10.1) | Det modellen faktisk så. Dagens vurdering kan skrives om samme dag (AD-7, AD-17), og loggen skal vise hva modellen så, ikke hva som står i vurderingen etterpå. Uten det finnes ingen kontrast å måle KI-teksten mot |
| KI-teksten | Selve bidraget |
| Om teksten besto kontrollen i FR-603, og ellers hvorfor ikke | En tekst som ikke vises, skal fortsatt finnes |
| Promptversjon og modell | Se FR-605 |

Det er én rad per aksje og børsdag, også når modellen feiler. Da har raden
ingen tekst og sier at modellen feilet (NFR-04). Finnes raden for dagen, kalles
ikke modellen på nytt, og raden står.

Loggen skrives i hentekommandoen. Siden skriver aldri i den.

Loggingen starter ved første kjøring, ikke når eksempelsettet skal lages. Skrus
loggingen på i etterkant, finnes ikke uka målet krever.

#### FR-605 — Promptversjon og modell lagres med hver KI-tekst

Hver lagret KI-tekst skal bære promptversjonen og modellen som produserte den.
Ellers blandes den sammen med vurderingen i FR-408, som er regelens og ikke
KI-ens.

Justeres prompten i oktober, må det være mulig å se hvilken versjon som ga
hvilken tekst. Uten det blir eksempelsettet en blanding av flere systemer
som ser ut som ett.

#### FR-606 — Relevansskalaen

Relevansskalaen har tre verdier:

| Verdi | Betyr |
|---|---|
| **Påvirker selskapet direkte** | Saken har konkret betydning for selskapets drift, kontrakter, eierskap eller resultat |
| **Kan påvirke** | Saken kan få betydning, men det er ikke gitt |
| **Lite relevant** | Saken har ingen praktisk betydning for en sparer |

De tre nivåene er bevisst de samme som brukes i relevanseksperimentet, slik at
resultatene kan sammenlignes direkte.

I v1 brukes skalaen i relevanseksperimentet, på EODHDs medieartikler
(`relevanseksperiment.md` §3, story 9.5), og ikke i applikasjonen. Hvordan den
brukes på meldinger i applikasjonen, står i FR-606A.

#### FR-607 — KI-teksten om dagen på forsiden

*Lagt til 2026-10-02, Marians beslutning (story 10.6).*

Under tabellen i markedsoversikten står noen setninger om hele børsdagen, skrevet av KI. Grunnlaget er bare utledede tall regnet av kursene: hvor mange som skilte seg ut, hvor mange som gikk bedre enn hovedindeksen (FR-104), indeksens endring, og snittendringen per bransje, for dagen og for uka. Teksten lages én gang i hentekommandoen, med ett kall til modellen per børsdag (NFR-02), og logges som i FR-604 og FR-605. Den er merket som laget av KI, med modellnavnet (FR-602). Kontrollen i FR-603 gjelder med alle 4 punktene, og teksten vises bare når grunnlaget stemmer med det siden viser. Ellers står det at dagen er uten KI-tekst. Teksten gir ikke råd og spår ikke (NFR-06).

### 4.6A Plan A: KI-laget over meldinger (utenfor v1)

*Lagt til 2026-09-28.* Ute av v1 fra 2026-09-28 (plan B, punkt 1 i §8). Dette er
innledningen og kravene fra §4.6 slik de sto før plan B, ordrett. Kravene som
bare gjelder meldinger, har fått en A. FR-601 og FR-605 gjelder begge planene og
står i §4.6. Kommer et ja fra Euronext, bygges plan A oppå plan B.

Til 28.09 var første setning i FR-605, ordrett:

Hver lagret vurdering skal bære promptversjonen og modellen som produserte den.

Til 28.09 var overskriften i FR-605 «FR-605 — Promptversjon og modell lagres med
hver vurdering», og andre avsnitt var, ordrett:

Justeres prompten i oktober, må det være mulig å se hvilken versjon som ga
hvilken vurdering. Uten det blir eksempelsettet en blanding av flere systemer
som ser ut som ett.

KI brukes der, og bare der, metadata er uttømt. At metadata ikke skiller
betydning er målt tre ganger uavhengig; argumentet står i `begrunnelser.md`.

KI-laget brukes ikke til å avgjøre hvilket selskap en melding gjelder — den
jobben gjør `issuerSign` bedre og gratis.

#### FR-602A — Visningen når KI-laget er av

Meldingene i samlekategorien skal fortsatt vises når laget er av, merket
**«ikke vurdert»**. De skal ikke forsvinne.

Med laget av gjelder altså: regelfilteret sorterer som før, meldinger som slapp
gjennom vises uten KI-forklaring, og samlekategorien vises uten
relevansmerking, men merket som uvurdert.

Begrunnelsen er at meldinger som forsvinner, blander sammen to forskjellige ting
— færre meldinger og uforklarte meldinger — og gjør sammenligningen av og på
meningsløs.

#### FR-603A — Usikkerhet vises som forbehold, ikke som rekkefølge

Er en KI-vurdering usikker, skal den vises med forbehold der den står.
Usikkerhet skal ikke håndteres ved å sortere meldingen ned.

Usikkerhet avledes av observerbare kjennetegn, ikke av en selvrapportert
sikkerhetsscore fra modellen:

1. Om selskapet nevnes i overskrift eller ingress
2. Om mange selskaper nevnes likeverdig i samme sak
3. Om to kjøringer gir samme klassifisering

Der kjennetegnene spriker, merkes vurderingen som usikker i stedet for at
modellen tvinges til et svar.

#### FR-604A — Logging av KI-bidraget, fra første kjøring

For hver melding KI-laget behandler, lagres:

| Felt | Hvorfor |
|---|---|
| Meldings-id, utsteder, kategori, publiseringstidspunkt | Identifiserer meldingen entydig mot NewsWeb |
| Hva regelfilteret alene gjorde med den | Uten dette finnes ingen kontrast å måle KI-bidraget mot |
| KI-lagets vurdering, forklaring og usikkerhetsmerke | Selve bidraget |
| Promptversjon og modell som ga vurderingen | Se FR-605 |

Loggingen starter ved første kjøring, ikke når eksempelsettet skal lages. Skrus
loggingen på i etterkant, finnes ikke uka målet krever.

#### FR-606A — Relevansskalaen

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

*Lagt til 2026-09-25:* visningsbryteren er bryteren Anbefalt/Alle i FR-203.

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
> som låste tre parametre og ikke fem. De ble målt 2026-09-22 mot like mange
> aksjedager, 2 985, forskjøvet én handelsdag; metode og tall i `malinger.md`
> §9. *Rettet 2026-09-24: her sto «de samme 2 985». §9 sier «Like mange
> aksjedager som §7.4, men ikke de samme».*

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
> Interesse −1 (volum 4,95 × medianen) → styrke 3, retning blandet

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

*Endret 2026-10-01 (OSEBX i v1, Marians beslutning):* hovedindeksen hentes i
samme kjøring (FR-410), så daglig henting koster 16 kall og gir **fire kalls
margin**. Avsnittet over gjelder til story 2.8 er bygget.

*Lagt til 2026-10-02:* idéen «Måling av omsetning med kall til overs» i §8 bruker marginen bare etter at kveldens henting har gått bra, og lar 2 kall stå igjen. Alle kallene brukes bare når brukeren selv kjører målingen etter at dagen er ferdig.

*Lagt til 2026-10-02:* lista har opptil 18 aksjer (§8, «Egne aksjer»), så minst 1 kall er igjen hver dag.

Ett bulk-kall er ikke et alternativ: bulk-endepunktet koster 100 kall flatt. Ett
kall per symbol er eneste vei, og det er denne begrensningen som gir universet
på 15.

Relevanseksperimentet er en engangsinnsamling og inngår ikke i daglig drift; se
punkt 5, lukket 26.09, og `relevanseksperiment.md` §8.

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

### NFR-08 — Bare tall vi kan stå for

*Lagt til 2026-10-01, Marians regel.*

Et tall vises bare når det kommer fra dataene, er regnet etter en regel som står
skrevet, og har bestått kontrollen. Mangler tallet, eller ser det feil ut, vises
«–» med grunnen, aldri et anslag eller et reservetall. Appen gjør det allerede:
«Ukjent» i FR-101, og ingen fallback mellom `close` og `adjusted_close` i
`eodhd.py`. Kravet gjelder også tall som kommer senere: høy og lav vises bare
når begge finnes og lav ≤ sluttkurs ≤ høy. Valgbare perioder (1 uke, 1 mnd og så
videre) får én skriftlig regel for startdagen, lik for alle periodene, og testes
med faste datoer rundt helger, helligdager og nyttår før de bygges.

---

## 6. Datakilder

Kildestatus, kontrollerte vilkår, forkastede kilder og skillet mellom hva som
publiseres og hva som blir liggende lokalt: `docs/kilder-og-rettigheter.md`.

| Kilde | Brukes til | Koster kvote |
|---|---|---|
| EODHD `/api/eod` | Sluttkurser | 1 kall per symbol, 15 i døgnet |
| Oslo Børs NewsWeb | Børsmeldinger | Nei |
| Euronext finanskalender | Kommende hendelser | Nei |
| EODHD `/api/news` | Relevanseksperimentet, én engangsinnsamling | Målt: 5 kall per forespørsel med én ticker (`malinger.md` §7.2). Åtte selskaper, én forespørsel hver, kostet 40 kall 25.09, og `limit=20` kostet ikke mer enn `limit=10` (`relevanseksperiment.md` §6). En forespørsel med flere tickere samtidig er ikke målt, og story 9.4 avgjør det ikke lenger: kontrollen med to tickere ble byttet ut (`bb54553`). Ikke daglig drift — se punkt 5, lukket 26.09, og `relevanseksperiment.md` §8. *Rettet 2026-09-24: her sto 10 per ticker og ~80* *Rettet 2026-09-25: her sto «For flere tickere er tallet ikke målt: ~40 kall for åtte selskaper hvis det er 5 per ticker, ~80 hvis det er 10. Avgjøres av den første forespørselen med to tickere (story 9.4).»* |

To forbehold hører til PRD-en fordi de kan velte krav: **NewsWeb-vilkårene er
ikke kontrollert**, og API-et er udokumentert backend for Oslo Børs' egen
nettside. *Rettet 2026-09-24:* vilkårene ble kontrollert 2026-09-21. Euronexts
vilkår dekker NewsWeb ved navn og forbyr automatisert henting uten skriftlig
tillatelse på forhånd; se åpent punkt 1. Faller NewsWeb bort, finnes ingen åpenbar erstatning — E24 er forkastet
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
| Relevanseksperiment | Testsett på ~50 medieartikler fra åtte selskaper, merket manuelt, kjørt mot både symbolmatching og KI-klassifisering | Eksperimentet gjennomført og tallene dokumentert — ikke at KI kommer best ut | **Del 1** innsamling og merking, uke 39–40. *Gjennomført 26.09* (`relevanseksperiment.md` §8). **Del 2** KI-kjøringen, når KI-laget finnes |
| Fortsatt bruk | Om vi bruker løsningen frivillig etter at utviklingen er ferdig, ikke bare for å teste den | Minst tre dager i uka de to siste ukene, loggført | Ved prosjektinnlevering |
| Grensesnitt og stabilitet | Hovedflyten fungerer uten feil og med et ryddig, gjennomarbeidet grensesnitt i en demonstrasjon | Hovedflyten gjennomført uten feil eller manuelle inngrep | Ved demonstrasjonen |

**Hovedflyten** er definert som: åpne markedsoversikten, se hvilke aksjer som
skiller seg ut, åpne én av dem, og lese hvorfor — de tre sjekkene med verdiene
sine, og meldingene som gjelder. Både brukerutfallsmålet og stabilitetsmålet
måler denne flyten.

**Bundet til datoer som ikke er fastsatt:** FR-407, FR-601 og FR-408, og fire av
de åtte målene: «Brukerutfall», «KI-bidrag i drift», «Fortsatt bruk» og
«Grensesnitt og stabilitet». Se åpent punkt 13. *Rettet 2026-09-24: her sto
bare «KI-bidrag i drift» og «Grensesnitt og stabilitet». «Brukerutfall» og
«Fortsatt bruk» har frist ved prosjektinnlevering.*

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
| 2 | **KI-terskelen i samlekategorien** — hvor grensen mellom «kan påvirke» og «lite relevant» skal gå. Kan ikke avgjøres på papir; relevanseksperimentet er input. Foreløpig regel står i FR-606. *Plan B 2026-09-28:* gjelder meldingsdelen, som ikke er med i v1. | *‹fylles inn›* | Utenfor v1 (plan B, 28.09) | Kalibrering av FR-606 |
| 4 | **Hvordan utledes eks.dato?** FR-407 og FR-503 forutsetter at utbyttedager kan identifiseres. **En målt vei finnes, funnet 2026-09-21:** avviket mellom close-endringen og `adjusted_close`-endringen peker ut dagen justeringen skjedde. 38 hendelser over 3 720 dagovergangner, og antallet står stille fra 0,05 til 0,5 prosentpoeng — et rent skille, så terskelen kan begrunnes i stedet for velges. **Konsekvensen er større enn kravet:** FR-407 blir da uavhengig av EKS.DATO-meldinger, og dermed av NewsWeb og punkt 1. Se `begrunnelser.md` §11. *Frist endret 2026-09-24:* sto «Før demonstrasjonen»; story 2.6 bygger merkingen | Gruppen | **Før story 2.6** | FR-407, FR-503 |
| 16 | **Språkgjenkjenningen slår systematisk feil for Vår Energi.** `gjett_spraak` lar ett norsk tegn avgjøre alene, og `VAR` heter *Vår Energi ASA*. Hver engelsk melding derfra bærer «å» i sitt eget firmanavn og leses som norsk, så FR-501 vil beholde den engelske versjonen hver gang selskapet sender et meldingspar. Dette er ikke en kantsituasjon — det er hver gang, for én av de femten, og det vises i en norsk applikasjon. **To forsvarlige veier:** bygge om språkregelen, eller la den stå og forklare avviket i demonstrasjonen. Det som ikke er forsvarlig er at valget tas ved at ingen tar det opp. *Frist endret 2026-09-24:* sto «Før UI-arbeidet starter»; story 6.3 bygger dedupliseringen. *Plan B 2026-09-28:* gjelder meldingsdelen, som ikke er med i v1. | Gruppen | Utenfor v1 (plan B, 28.09) | FR-501, demonstrasjonen |

### Må følges opp

| # | Punkt | Eier | Frist |
|---|---|---|---|
| 5b | **Relevanseksperimentet, del 2: KI-klassifiseringen.** Kan ikke gjøres ennå, og det er tre grunner, ikke én: KI-laget finnes ikke som kode, ingen modelltjeneste er valgt, og **betingelse 4 i EODHDs godkjenning — at modelltjenesten ikke trener på innholdet — er udokumentert.** Den må være ført før artikkeltekst sendes inn i en modell, se `docs/kilder-og-rettigheter.md` | Gruppen | Når KI-laget finnes |
| 6 | **Usikkerhetskriteriene er skrevet for medieartikler.** Kjennetegn 1 bærer svakt når utstederen selv er avsender | | Før KI-laget implementeres |
| 8 | **Oppstart av tilbakekjøpsprogram** er ekte nyhet, men filtreres bort sammen med de ukentlige statusrapportene | | Før innlevering |
| 9 | **Kontrollere Alpha Vantages vilkår** for ikke-kommersiell bruk | | Før innlevering |
| 11 | **Meldepliktig handel for primærinnsidere** justeres hvis den viser seg å være i hovedsak opsjonsutøvelse | | Etter én ukes drift |
| 12 | **Bekrefte horisont og hendelsestyper** i FR-302, som i dag er antatt | | Før implementasjon |
| 13 | **Datoer for demonstrasjon og prosjektinnlevering.** Spørsmål sendt faglærer i Teams 2026-09-22, sammen med spørsmål om leveranselista er fullstendig og om noen BMAD-dokumenter skal leveres inn. **Besvart av hjelpelærer 2026-09-23: ingen dato finnes ennå** — «Bård Inge vil presisere dette». Fire av de åtte suksessmålene i §7 er bundet til disse datoene (*rettet 2026-09-24: her sto «Åtte suksessmål»*), og «est. uke 45» er vår egen estimering — ikke en oppgitt dato. Se `docs/innlevering.md` | Marian | **Avventer Bård Inge** (spurt 22.09, besvart 23.09) |
| 15 | **Plassér kategoriene som havnet i «ukjent»** i riktig bøtte. Krever en ukes drift for å vite hvilke som faktisk dukker opp | | Etter én ukes drift |
| 21 | **Hva er emnesidens tredje del?** Emnesiden sier «tre deler», men lister to, og nevner at «delvurdering 3 gir anledning til å demonstrere unike bidrag». Hva den tredje delen er, er ikke oppgitt. Spørres Bård Inge sammen med datoene i punkt 13. Se `docs/innlevering.md`, «Eksamen» | Marian | Sammen med punkt 13 |
| 22 | **Kodegjennomgang som BMAD-steg, én per epic.** `bmad-code-review` kjøres etter hver ferdige epic, første gang etter Epic 1. Emnesiden: «Dokumentasjon må vise hvordan KI ble brukt, og hvordan studentene har kvalitetssikret koden» — en gjennomgang med flere uavhengige lesere er en del av det, i tillegg til testene og mutantene. Lagt til 2026-09-23. *2026-09-24:* den første gjennomgangen ble gjort 23.09 etter story 1.1–1.3, midt i Epic 1, ikke etter den. Funnene står som forutsetninger i `epics.md` under 1.5b og 2.2. *Rettet 2026-09-26:* her sto «under 1.6 og 2.2». De ble flyttet fra 1.6 til 1.5b 24.09 (`f7e4544`). *2026-09-28:* gjennomgangen etter Epic 1 ble gjort 27.09 (`kodegjennomgang-epic-1.md`). Funnene er rettet i 1.8 og 1.9 eller lagt til 2.1, 2.5 og 4.0. Fristen var «Etter Epic 1». Punktet står åpent, fordi det gjelder hver epic. | Gruppen | Etter Epic 2 |
| 25 | **Dagene Oslo Børs er stengt i 2027.** Fra 2027-01-01 reiser `innevaerende_boersdag`, og dermed `skriv`, til dagene for 2027 er ført inn (punkt 3, og BH2 i gjennomgangen av story 1.6). Når Euronext publiserer kalenderen for 2027, føres dagene inn i `STENGT` i `src/boersdag.py` og i seksjonen Handelskalenderen i `docs/kilder-og-rettigheter.md`, og 2027 legges til i `DEKKEDE_AAR`. Kalenderen for 2026 er merket «© 2025», så kalenderen for 2027 kommer trolig i høst | Marian | 2026-12-01 |

### Lukket

Punkter som er avgjort. De står igjen med hva som lukket dem, ikke slettet —
uten det kan ingen se at de var åpne, eller hva som måtte til.

| # | Punkt | Lukket av | Dato |
|---|---|---|---|
| 10 | **Skjevfordeling mot positiv retning**, 68 % i testen. Vurderes mot året, ikke mot femten dager | `malinger.md` §7.4 målte over 199 handelsdager: 60,0 % av aksjedagene med utslag er positive, mot 29,5 % negative. Det korte vinduet lå i en oppgangsperiode og overdrev skjevheten. Flyttet hit 2026-09-24 | 21.09 |
| 7 | **Låsing av signalparametre** mot ~200 handelsdager | `malinger.md` §7.4 låste terskel, volumfaktor og nøytralsone mot 199 handelsdager; §9 låste de to vinduene mot like mange aksjedager, 2 985, forskjøvet én handelsdag. **Punktet anslo 15 kall.** §7.4 kostet 15 kall, og §9 kostet 0, fordi den ble regnet mot lagrede øyeblikksbilder (`malinger.md`). *Rettet 2026-09-26:* her sto «Punktet anslo 15 kall. Det kostet 0 — begge målingene ble gjort mot lagrede øyeblikksbilder» | 21.09 og 22.09 |
| 14 | **Hver story leveres med test**, kjørbar uten API-kall | Skrevet inn som `AD-8` i arkitekturspinen. Praksisen var allerede innført: `tests/conftest.py` sperrer `socket.connect`, og CI kjører uten hemmeligheter | 22.09 |
| 17 | **Database** | SQLite besluttet i arkitekturfasen — spinen `AD-3` til `AD-7`, `AD-16`, `AD-18`, `AD-19`. Rådata forblir filer. **Kontrollert med faglærerstaben 22.09** og bekreftet av assisterende hjelpelærer: «Slik dere beskriver bruken […] bruker dere SQLite som en ordentlig database, ikke bare som enkel fillagring. […] Så ut fra det vi vet nå mener jeg dette er helt innenfor.» Svaret kom ikke fra emneansvarlig og bærer sitt eget forbehold | 22.09 |
| 18 | **Dockerfile** | Arkitekturen besluttet: `AD-9` (ingen data i imaget), `AD-10` (webserveren henter aldri), `AD-11` (to volumer), `AD-12` (hemmeligheter fra miljøet). **Merk at selve filen ikke er skrevet** — punktet gjaldt beslutningen, og bygget står i `docs/innlevering.md` | 22.09 |
| 5 | **Relevanseksperimentet, del 1: utvalgskriterier, innsamling og manuell merking.** Flyttet fram fra uke 41 den 2026-09-21. Uke 41 ble satt mens eksperimentet var blokkert av to ting — om vilkårene tillot språkmodellbruk, og om `/api/news` svarte for `.OL`. **Begge ble avklart 21.09**, men datoen ble aldri flyttet etterpå. Rekkefølge: (a) utvalgskriteriene skriftlig — hvilke åtte selskaper, hvor mange artikler per selskap, og hva som teller som at en artikkel handler om selskapet; (b) innsamlingen, med kalltall-kontrollen som **første** forespørsel: to tickere, og se om `apiRequests` flytter seg 10 eller 15, så kostnaden for resten er kjent før den brukes. Tas fra bonuskvoten `extraLimit`. *Prøvd 2026-09-23, `malinger.md` §11:* kall nummer 21 lyktes og trakk fra bonuskvoten (485 → 484), så den brukes automatisk når dagskvoten er tom. Kalltallet per ticker er fortsatt utledet, ikke målt. *Rettet 2026-09-24:* fristen sto «Etter punkt 17 og 18», som begge ble lukket 22.09. Ny frist fra briefen og §7. Bygges som story 9.4. *Endret 2026-09-25:* kontrollen med to tickere er byttet ut. Den måler hva en forespørsel med flere tickere koster, og det trenger vi ikke når hvert selskap hentes for seg. Prisen for én ticker er målt: 5 kall (`malinger.md` §7.2). I stedet leses `/api/user` før og etter hver forespørsel, og koster en forespørsel noe annet enn 5 kall, stopper vi før neste. Budsjettet er åtte forespørsler, ~40 kall. Kriteriene står i `relevanseksperiment.md` | Del 1 er gjennomført 25.–26.09. Kriteriene ble låst før innsamlingen, og de 48 parene ble merket hver for oss. Vi var enige om 40 av 48 før vi snakket sammen (kappa 0,749), og 35 av 48 par (72,9 %) er ikke «Lite relevant». Se `relevanseksperiment.md` §6–§8. Del 2 venter på KI-laget | 26.09 |
| 3 | **Hvilken kilde gir handelskalenderen?** FR-402 hviler på «forventet børsdag», men ingen kilde er utpekt for hvilke dager Oslo Børs er åpen. **Utvidet 2026-09-24: «inneværende børsdag» er heller ikke definert for helg og helligdager.** FR-408 og spinens skjerping av AD-7 lar `skriv` avvise enhver dato som ikke er inneværende børsdag, men sier ikke hva den er en lørdag eller en helligdag. Definisjonen må være avgjort før story 1.6. Forslag, ikke avgjort: «siste børsdag på eller før dagens dato i Europe/Oslo». *Rettet 2026-09-24:* fristen sto «Før implementasjon», som er passert, og punktet hadde ingen eier | **Avgjort av gruppen 27.09: forslaget er vedtatt.** Inneværende børsdag er siste børsdag på eller før dagens dato i Europe/Oslo. En børsdag er mandag–fredag som ikke står på lista over dager Oslo Børs er stengt, ført for hånd fra Euronexts egen kalender (`docs/kilder-og-rettigheter.md`, seksjonen Handelskalenderen). Halve handelsdager er børsdager. Lista dekker 2026; for en dato utenfor reiser funksjonen en feil i stedet for å gjette, og Marian fører inn dagene for 2027 når Euronext publiserer dem. Funksjonen er ren, ligger i kjernen, får datoen inn og brukes av story 1.6 (FR-408, AD-7), 1.7 (FR-409) og 2.3 (FR-402). Lista kommer inn i koden i 1.6. Når på døgnet dagens rad kan ventes, er fortsatt punkt 23 | 27.09 |
| 24 | **«Ingen rad på en børsdag» betyr ikke alltid at kommandoen ikke ble kjørt.** FR-409 leser det slik, men to tilfeller gir ingen rad uten et hull i driften: kommandoen kjørte før dagens kurs var publisert (punkt 23), eller ett symbol feilet mens de andre ble hentet (`AD-15`). To veier: en fjerde tilstand i FR-409, eller en lagret grunn på raden. Story 2.5 må si hva som skrives for et symbol som feilet. Lagt til 2026-09-24 | **Avgjort av gruppen 27.09: lagret grunn på raden.** Kan kjøringen ikke vurdere en aksje, skriver den likevel en rad for dagen, med grunnen i stedet for vurderingen: symbolet feilet (AD-15), nyeste kurs var ikke fra dagen (FR-402, punkt 23), eller signalet kunne ikke regnes (FR-204). Da betyr ingen rad på en børsdag bare at kommandoen ikke ble kjørt, slik FR-409 leser det. En rad med grunn skriver aldri over en rad med vurdering samme dag. Grunnen er valgt fremfor en egen tilstand fordi hentekommandoen alt vet den, og fordi FR-408s spørsmål da får et svar. Avgjort før story 1.6, ikke 1.7, fordi svaret bestemmer formen på `vurdering`, som 1.6 lager i `0002`. Da slipper tabellen å bygges om senere (spinen, Deferred) | 27.09 |
| 20 | **Hvordan skal FR-408s eget spørsmål kunne stilles?** Kravet begrunner seg med «hva sa løsningen om EQNR for to uker siden?», men ingen visning, kommando eller spørring i v1 svarer på det. Historikken er da **lagret, men ikke besvarbar**. Tre veier: en visning i aksjedetaljen, en egen kommando, eller en direkte spørring mot basen under demonstrasjonen. FR-409 binder alle tre til å bevare skillet mellom «ingen rad» og «styrke 0» | **Avgjort av gruppen 27.09: en visning i aksjedetaljen.** De siste ukenes vurderinger vises dag for dag, lest gjennom `Vurderingslager` og `tilstand`, så skillet i FR-409 står. Valgt fremfor en kommando eller en spørring under demonstrasjonen, fordi svaret da finnes i appen, der brukeren og sensor ser det. Story 2.7 | 27.09 |
| 23 | **Når på døgnet skal hentekommandoen kjøres?** Kl. 19:04 lokal tid 2026-09-23 var dagens sluttkurs ikke publisert: alle 15 serier sluttet 22.09 (`malinger.md` §11). Og en rad hentet mens børsen er åpen, kan bli korrigert i etterkant — MOWI 21.09 fikk volumet justert ned 0,8 % ved neste henting, med sluttkursen uendret. EODHD dokumenterer bare «2–3 timer etter at børsen stenger» (§2). Kjøres kommandoen for tidlig, får brukeren gårsdagens data eller en foreløpig rad; kjøres den to ganger, trekkes det stille fra bonuskvoten. Lagt til 2026-09-23. *Målt 2026-09-24 (`malinger.md` §12):* kl. 21:31 norsk tid hadde alle 15 serier en rad for 24.09, og ingen av de 3 720 felles aksjedagene med øyeblikksbildet fra 23.09 var endret. Når raden kommer mellom 19:04 og 21:31, og om den er endelig, er ikke målt | **Avgjort av gruppen 28.09: på børsdager mellom kl. 22:00 og midnatt, norsk tid.** Kl. 19:04 den 23.09 fantes ikke dagens rad, og kl. 21:31 den 24.09 fantes den for alle 15 (`malinger.md` §11 og §12). En rad hentet etter stengetid var uendret dagen etter, mens MOWI-raden som ble rettet, var hentet mens børsen var åpen. Før midnatt havner hele kjøringen på samme børsdag, slik vurderingen krever (AD-7). Om morgenen har en ny børsdag begynt uten kurs, og en kjøring som kommer for tidlig, bruker 15 kall uten å få dagens rad. Nøyaktig når raden kommer mellom 19:04 og 21:31, er ikke målt. Planen for story 2.3 avgjør om kommandoen advarer eller nekter før kl. 22:00. | 28.09 |
| 1 | **Vilkårskontroll — to av tre deler lukket 2026-09-21.** *Lukket:* EODHD har svart skriftlig ja til språkmodellbruk, med fire betingelser, og kontrollen av NewsWeb og Euronext er gjennomført. *Åpent:* kontrollen ga et **uttrykkelig forbud** mot automatisert henting uten tillatelse på forhånd. Forespørsel sendt 21.09, **purret 22.09 i samme tråd** — purringen dekker både de fire opprinnelige delene og overføring til en modelltjeneste (punkt 19), og tilbyr et smalere alternativ. Svar avventes. Holder ikke unntaket, må meldingsdelen omdisponeres. **Kontrollert 22.09: EODHDs `/api/news` er ikke en reservekilde** — den koster 75 kall i døgnet for universet mot en kvote på 20, innholdet er syndikert fra tredjepart via Yahoo, og taksonomien er **tematisk og ikke regulatorisk**, så FR-502s tre bøtter måtte bygges om fra grunnen. Vurderingen med tall i `malinger.md` §10. Et nei tar derfor hele KI-laget med seg. *Tillegg 2026-09-24:* et nei tar KI-laget **over meldinger** med seg, ikke hele KI-laget. Plan B (Epic 5B) utløses, og det hentes ikke fra NewsWeb før Euronext har svart (beslutningen 23.09) | **Avgjort av gruppen 28.09: plan B.** Euronext har ikke gitt tillatelse innen 28.09, vår egen frist for å ta stilling uten svar, og taushet regnes som nei for v1. Det hentes ikke fra NewsWeb eller Euronext i v1. Børsmeldingene og de kommende hendelsene er ute av v1, og storyene i Epic 5, 6 og 7 står som plan for en senere versjon. KI-laget forklarer signalet ut fra tall regnet av kursene (Epic 5B, som heter Epic 10 fra 28.09). Svarer Euronext senere, er det en ny beslutning, og plan A bygges da oppå plan B. | 28.09 |
| 19 | **Forespørselen til Euronext ba aldri om å sende innhold til en modelltjeneste.** Vilkårene forbyr å «otherwise transfer any of the Content to any third person», og parentesen strekker det til «others in your company or organisation» — altså svært bredt. Å sende meldingstekst inn i en språkmodell er en slik overføring. Brevet 21.09 beskriver fire ting — Retrieval, Storage, Display, Source code — og **ingen av dem nevner en modelltjeneste**; kontrollert 22.09, null treff på «language model», «LLM», «third person» og «third party» i hele brevet. Manuell innsamling løser klausul 1 om automatisert henting, men **ikke** overføringsklausulen. **Konsekvens: selv et fullt ja på alle fire delene lukker ikke dette.** Det må stilles som eget spørsmål. Kalenderspørsmålet i samme brev hjelper ikke: det ber om «the same answer» og arver dermed de fire overskriftenes rekkevidde, inkludert utelatelsen. **Purret 22.09, og purringen dekker begge deler** — de fire opprinnelige og overføringen — så et kort svar kan ikke lenger se fullstendig ut mens det bare dekker det ene. Purringen tilbyr også et smalere alternativ: et lite, manuelt innsamlet utvalg brukt én gang. Ordrett i `docs/epost-til-euronext.md` | **Bortfalt 28.09 med plan B.** Ikke noe innhold fra Euronext sendes til en modelltjeneste i v1. Reservealternativet for relevanseksperimentet trengs ikke: del 1 er gjort på EODHDs medieartikler (punkt 5). | 28.09 |

**Punkt 1 og 19 er de to som kan velte datagrunnlaget.** Punkt 1 velter nå bare
én ting, ikke to. Punkt 19 kom til 22.09 og treffer meldingsdelen og KI-laget
sammen. *Tillegg 2026-09-24:* KI-laget betyr her KI-laget over meldinger. Et nei
utløser plan B (Epic 5B), og det hentes ikke fra NewsWeb før Euronext har svart.

*Avgjort 2026-09-28:* plan B. Se punkt 1 og 19 i «Lukket».

*Oppdatert 2026-09-21.* EODHD-halvdelen er lukket: språkmodellbruken er
skriftlig godkjent, og `/api/news` er målt til å svare for `.OL`-tickere.
Relevanseksperimentet kjøres derfor på medieartiklene (her sto «plan A»; *rettet 2026-09-24*, fordi plan B nå betyr Epic 5B) og deler ikke lenger kilde med
meldingsdelen. Det som står igjen, er Euronext: vilkårene som dekker NewsWeb
forbyr uttrykkelig automatisert henting uten tillatelse på forhånd, og
forespørselen om tillatelse ble sendt 21.09 og er ubesvart. Fristen 28.09 er vår
egen frist for å ta stilling uten svar, ikke en dato Euronext har lovet.
Fullstendig
gjennomgang med sitater i `docs/kilder-og-rettigheter.md`.

Av de åpne punktene har 4, 5b, 13, 16, 21, 22 og 25 eier. Punkt 2, 6, 8, 9, 11, 12 og 15 mangler det. Punkt 1, 3, 5, 7, 10, 14, 17, 18, 19, 20, 23 og 24 er lukket. *Rettet 2026-09-28, kveld: punkt 1 og 19 ble lukket med plan B, og punkt 2 har ikke lenger en frist.* *Rettet 2026-09-28: punkt 23 ble lukket.* *Rettet 2026-09-27: punkt 3, 20 og 24 ble lukket, og punkt 25 kom til, med Marian som eier.* *Rettet 2026-09-26: punkt 5 ble lukket.* *Rettet 2026-09-24: punkt 3 fikk eier, punkt 10 ble lukket, og punkt 24 kom til, med Gruppen som eier.* *Rettet 2026-09-23: setningen talte lukkede punkter blant de åpne, og manglet 13, 20 og 21.*

**Om nummereringen.** Numrene følger rekkefølgen punktene ble opprettet i, ikke
rekkefølgen i tabellene. Punkt 16 står derfor over sammen med de andre som må
avgjøres, selv om numrene 5–15 ligger i tabellen under. Det er gjort for at
kryssreferanser fra `malinger.md` og gjennomgangene skal forbli gyldige — et
punkt som renummereres, mister sporet tilbake til målingen som begrunnet det.

**Om eierfeltet.** «Gruppen» er et bevisst valg, ikke en tom rubrikk: vi er to,
og fordelingen gjøres internt etter hva som passer når punktet skal tas. Det
eierfeltet skal sikre, er at punktet har en frist og noen som svarer for den —
ikke at navnet er låst på forhånd. Punkt 6, 8, 9, 11, 12 og 15 har frist, men mangler eier. Punkt 2 mangler eier, men har ikke lenger en frist (plan B). *Rettet 2026-09-28:* her sto «Punkt 2, 6, 8, 9, 11, 12 og 15 har frist». *Rettet 2026-09-26:* her sto «Punkt 2, 3, 6, 8–12 og 15». Punkt 3 har eier, og punkt 10 er lukket, slik oppsummeringen over sier.

### v1.1 — vurderes etter at v1 er kontrollert

*Lagt til 2026-09-23.* Dette er ideer, ikke krav og ikke stories. Ingen av dem
tas før v1 er kontrollert og virker, jf. prioriteringen 23.09. Hver står med det
den avhenger av.

| Idé | Avhenger av | Forbehold |
|---|---|---|
| **Sektorvisning:** endring per sektor for dag, uke og måned | Ingenting nytt. Sektor finnes i `AKSJEUNIVERS`, og tallene regnes fra kursserien | 15 aksjer gir få per sektor: 8 sektorer, der Energi har 4, fire har 2 og **tre har bare én** (Industri, Telekom, Konsum). En «sektor» med én aksje er aksjen selv. Vurderes etter brukertesten (story 8.1). *Lagt til 2026-10-01, Marians beslutning:* søylene per aksje for dagens endring, med bransjesymbol og indeksen som stiplet linje, er tatt inn i v1 (FR-105). Endring per sektor står igjen her |
| **Større aksjeunivers enn 15** | Målingen av `extraLimit` 23.09 (`malinger.md` §11): bonuskvoten trer inn ved kall 21, men den er på 485 og tar slutt. *Rettet 2026-10-03 (kontrollen 26.09, P2):* 485 gjaldt 23.09. Bonuskvoten synker når den brukes. Den var 485 fram til kall 21 den 23.09, 484 etter det (`malinger.md` §11), 464 etter innsamlingen til relevanseksperimentet 25.09 (`relevanseksperiment.md` §6) og 463 etter OSEBX-kallet 30.09 (`malinger.md` §14) | Se regnestykket under. Det skal stå før idéen vurderes |
| **Navigasjon mellom flere skjermbilder** *(utvidet 2026-09-26)*: en knapperad øverst, der knappen for skjermbildet man står på, er fylt. Kandidatene er Markedsoversikt, Min liste, Nyheter og Kalender. En knapp vises bare når skjermbildet finnes | Story 8.2, som skal si hvordan et tredje skjermbilde ville passet inn, uten å bygge det. Min liste er «Favorittmerking av aksjer» fra «Hvis vi rekker». Nyheter krever Epic 6 eller raden «Mediesaker for ett selskap». Kalender er Epic 7, der utbyttedatoer er blant de typiske hendelsestypene (FR-302) | Med to skjermbilder i v1 gir en knapperad lite: aksjedetaljen nås ved å klikke på en aksje. Epic 6 og 7 er blokkert av åpent punkt 1, så uten et ja fra Euronext blir det verken børsmeldinger under Nyheter eller noen Kalender. Min liste er favorittmerking, ikke en personlig portefølje, som står under «Utenfor v1», og med 15 aksjer kan den like gjerne være et filter i oversikten. Utbyttehistorikken fra kursserien er historikk, ikke en kalender, og hører til aksjedetaljen. *Delvis flyttet til v1 2026-09-30:* knapperaden med Markedsoversikt og Min liste bygges i 8.3. Nyheter og Kalender står igjen her |
| **Mediesaker for ett selskap** *(lagt til 2026-09-25)*: de nyeste artiklene fra EODHDs nyhets-API for én aksje, hentet bare når brukeren ber om det. Også for selskaper utenfor de 15, med ticker skrevet inn | Relevanseksperimentet del 1 (story 9.4): hvor mange artikler som finnes per selskap, og hvor mange av dem som faktisk handler om selskapet. For selskaper utenfor universet: et eget skjermbilde uten kurs og signal, jf. idéen om flere skjermbilder | 5 kall per selskap (`malinger.md` §7.2). Kurshentingen bruker 15 av 20, så ett selskap per dag holder seg innenfor dagskvoten, og mer tar av bonuskvoten (§11). Hentes av hentekommandoen, ikke av en knapp i nettsiden: webserveren henter aldri (NFR-02, AD-10). Artiklene vises bare lokalt og publiseres ikke (`docs/kilder-og-rettigheter.md`). Skal KI vurdere relevansen, gjelder EODHDs betingelser fra 21.09, også betingelse 4 |
| **Egendefinert meldingsfilter** *(lagt til 2026-09-25)*: brukeren velger selv hvilke kategorier som vises, i tillegg til Anbefalt og Alle (FR-203) | Story 6.5, og en brukertest som viser at noen savner det | Rundt ti kategorier, og valgene må lagres. Hvert valg koster tid i hovedflyten, som skal gå på under fem minutter (§7, «Brukerutfall»). Tas ikke inn uten at en test viser behovet |
| **Merk det som er nytt siden forrige henting** *(lagt til 2026-09-25)*: meldinger som har kommet siden forrige henting, merkes som nye | At meldingslageret (story 6.1) lagrer når hver melding ble hentet første gang | Svarer rett på spørsmålet i briefen: «hva beveget seg i går, hvorfor». Ingen kall og ingen KI |
| **Lenke til selskapets side på NewsWeb** *(lagt til 2026-09-25)*: én lenke fra aksjedetaljen, så alle børsmeldingene er ett klikk unna, også de som er filtrert bort | Ingenting nytt. Lenken henter ingenting | Vurderes allerede 28.09 hvis Euronext sier nei eller ikke svarer. Da har aksjedetaljen ingen meldinger, og lenken er det eneste som viser dem (åpent punkt 1). Adressen må slås opp før den bygges. *Tatt inn i v1 28.09 (plan B).* Adressen og det Euronexts vilkår sier om lenker, slås opp av en av oss før lenken bygges |
| **Sjekk 2 og 3 synlige i grafen** *(lagt til 2026-09-25)*: volumsøyler under kursgrafen, med en strek for medianvolumet, så sjekk 3 (interesse) synes slik MA50-linjen viser sjekk 1. Eventuelt også et bånd for sjekk 2 (bevegelse) | Ingenting nytt. Volumet finnes i `Kursrad`, og tegningen er samme SVG som i dag (`graf.py`). Tas stilling til i UX-gjennomgangen (8.2), etter brukertesten (8.1) | FR-202 sier at volatilitetsbånd og volumsøyler ikke tegnes i v1, så å ta dem inn er en endring av FR-202. Streken må være samme median, over samme vindu, som sjekk 3 regner med, etter samme prinsipp som i FR-202. Story 8.2 skal ikke ende i ny funksjonalitet, så søylene må begrunnes som en forbedring av forklaringen i FR-706, ellers hører de til v1.1 |
| **Signaldager i grafen** *(lagt til 2026-09-25)*: kursgrafen markerer dagene med sterkt signal, så man ser hvordan signalet har oppført seg over tid | Vurderingslageret (1.6) og at hentekommandoen skriver vurderingen hver dag (2.5). Historikken bygges opp fra første daglige kjøring | Bare visning. En studie av om signalene slår markedet er utenfor v1. Med få ukers historikk ved demonstrasjonen blir det få markeringer |
| **Hjelp bak et spørsmålstegn** *(lagt til 2026-09-25)*: et «?» på begge skjermbildene åpner et lite vindu som forklarer begrepene og symbolene appen viser: sluttkurs og endring, utbyttejustert kurs, signalstyrke 0–3, retningen (↑ Positiv, ↓ Negativ, ↔ Blandet, – Ingen eller Ukjent), de tre sjekkene (trend med 50-dagers snitt, bevegelse og interesse), «data hentet» og «Uten data». Vinduet sier også at signalene ikke er investeringsråd (NFR-06) | Ingenting nytt. Fast tekst, uten nettkall og uten KI, og det kan lages med HTML alene, uten et nytt bibliotek. Bør bygges før brukertesten (8.1), så testen viser om hjelpen blir brukt | Forklarer bare det appen faktisk viser. P/E og andre nøkkeltall fra regnskapet ligger utenfor v1 («fundamental- og verdimodell»). Retningen forklares med ordene fra FR-704, ikke med «opp» og «ned», som ble fjernet fordi de inviterer til å lese pilen som kursbevegelse (`markedsoversikt.py`). Hjelpen skiller «Ingen» fra «Ukjent», slik FR-101 gjør. Tall i teksten, som 50 dager, hentes fra de samme parametrene som beregningen (`Parametre` i `signalberegning.py`), og en test krever det. Ellers kan hjelpeteksten si én ting mens koden gjør en annen, den samme feilen som story 3.3 skal hindre mellom README og den tomme siden. *Flyttet til v1 2026-10-01:* story 8.0b (Marians beslutning). |
| **Utbyttehistorikk i aksjedetaljen** *(lagt til 2026-09-26)*: hvor mange utbyttedager aksjen har hatt det siste året, og datoen for den siste, så man ser om selskapet betaler hvert kvartal, hvert halvår eller én gang i året | Story 2.6 (FR-407), som finner dagene i kursserien. Ingen nye kall og ingen ny kilde | Et ja/nei-merke («utbytteaksje») ville ikke skilt aksjene fra hverandre: alle 15 hadde minst én hendelse i målingen (`begrunnelser.md` §11). Metoden ser justeringer, ikke utbytter, og en splitt gir samme utslag, så grensesnittet kan bare bruke ordet *utbytte* hvis en kilde sier det (samme sted, forbehold 1). Vinduet er ett år, så et selskap som betaler én gang i året, kan i perioder stå med null. Historikken sier ingenting om neste utbytte, og den skal ikke formuleres som et råd (NFR-06) |
| **Kommende eks.dato i oversikten** *(lagt til 2026-09-26)*: aksjer med eks.dato de nærmeste dagene får et merke i markedsoversikten, så det synes før man handler, ikke bare i aksjedetaljen | Epic 7 (FR-301–FR-303). Utbyttedatoer er blant hendelsestypene FR-302 regner med, men horisonten og typene er antatt (åpent punkt 12) | Kursserien kan ikke gi dette: metoden bak FR-407 finner dagen først når den har skjedd (`begrunnelser.md` §11, forbehold 2). EODHDs kalender svarer 403 på gratisnivået (`docs/kilder-og-rettigheter.md`). Epic 7 er blokkert av åpent punkt 1 (Euronext). Et nei stryker epicen, og idéen med den. Merket vises når appen åpnes. Et varsel på e-post eller telefon ville krevd kontaktopplysninger og noe som kjører uten at brukeren ber om det, og er ikke med her |
| **Høy, lav og omsetning i aksjedetaljen** *(lagt til 2026-09-26)*: høyeste og laveste kurs siste børsdag, og omsetningen i kroner, øverst i aksjedetaljen | Ingen nye kall: EODHDs svar har allerede open, high og low (`begrunnelser.md` §11), men adapteren (`eodhd.py`) tar bare med close, adjusted_close og volume. `Kursrad`, adapteren og lageret må utvides | FR-101 låser markedsoversikten til fem kolonner, så dette hører til aksjedetaljen. Høy og lav vises ved siden av sluttkursen, ikke i grafen, som tegnes på adjusted_close (FR-201). Omsetning regnet som volum ganger sluttkurs er et anslag, ikke børsens eget tall, og må merkes slik. *Rettet 2026-10-01 (NFR-08):* omsetningen tas ikke med, fordi volum ganger sluttkurs bare er et anslag. Før høy og lav vises, sammenlignes noen dager for hånd med Oslo Børs' egen side. Siden leses av en av oss og hentes aldri av programmet. |
| **Lær noe nytt** *(lagt til 2026-09-26)*: en liten boks i markedsoversikten med ett kort tips om aksjer per dag, for eksempel hva utbyttejustert kurs, medianvolum eller eks.dato betyr. Tipsene står i en fast liste. Dagens tips velges ut fra datoen, eller ut fra dagens tall når et tips passer, for eksempel tipset om medianvolum når en aksje har uvanlig høyt volum | KI skriver utkast til lista, og vi kontrollerer og retter hvert tips før det tas inn. Ingen nettkall og ingen KI når siden vises. Kan dele tekst med «Hjelp bak et spørsmålstegn» | Hvert tips må være riktig og kontrollert, og det skal ikke kunne leses som et råd (NFR-06). Tall i teksten hentes fra de samme parametrene som beregningen, slik som i hjelpen. Et nytt KI-tips hver dag er valgt bort: da når teksten skjermen uten at noen har lest den, og det krever modelltjenesten fra Epic 4. Bør bygges sammen med hjelpen, før brukertesten (8.1), så testen viser om noen leser den |
| **Retning og type for nyheter** *(lagt til 2026-09-26, fra merkingen i 9.4)*: i tillegg til relevansen (FR-606) viser nyheten mulig retning (positiv, negativ, blandet eller uklar) og type (for eksempel resultat, kontrakt, oppkjøp, analytikervurdering eller sektor) | Relevanseksperimentet (story 9.4). Børsmeldingene har allerede kategori fra NewsWeb (Epic 6), og EODHDs nyheter har feltene `sentiment` og `tags`, som ble skjult under merkingen (`relevanseksperiment.md` §4) | EODHDs godkjenning gjelder å sende tekst til en språkmodell «solely to classify company relevance» (`docs/kilder-og-rettigheter.md`). Retning og type fra vår egen KI krever derfor et nytt spørsmål til EODHD. Retning må ikke kunne leses som et råd (NFR-06). Kriteriene i del 1 endres ikke: der merkes bare relevans, slik det ble bestemt før innsamlingen |
| **Egne aksjelister** *(lagt til 2026-09-30)*: hver bruker velger sine egne aksjer, opptil 18, og kan bytte underveis. *Rettet 2026-10-02:* samme grense som i «Egne aksjer». Her sto «opptil 15». Appen kjører lokalt, og hver bruker har sin egen gratiskonto hos EODHD med 20 kall i døgnet. Vilkårene forbyr å dele en konto med andre, også innen grupper (`docs/kilder-og-rettigheter.md`), så gruppens nøkkel kan ikke deles. Færre aksjer bruker færre kall. Ferdige lister å starte fra: dagens 15 og én liste per bransje, som gruppen lager og måler én gang. Innenfor lista kan appen vise for eksempel dagens og ukens mest omsatte, regnet av kursene som allerede er hentet | At `aksje` får aktiv fra og til, så en aksje som byttes ut, blir stående med historikken sin (AD-21 lar ikke en aksje med rader slettes). At regelen i AD-21 om at `aksje` og `AKSJEUNIVERS` er like, erstattes av at lista leses fra basen. En måte å velge og bytte på, med kontroll av tickeren. Og at kriteriet i §3 sjekkes for hver aksje. Gratisnivået gir ett års kurser i ett kall (`malinger.md` §2), så en ny aksje får signal med en gang | Parametrene er testet på dagens 15 (AD-13), så en ny liste bør måles før grensene brukes på den. Trolig har få bransjer 15 aksjer over kriteriet i §3. Det er ikke målt, og målingen koster kall. Lister for hele børsen, som mest omsatt, flest nyheter eller små selskaper på vei opp, krever data for langt flere aksjer enn 20 kall rekker til: bulk-endepunktet koster 100 kall (`begrunnelser.md` §7), og nyheter koster 5 kall per aksje (`malinger.md` §7.2). Små selskaper faller dessuten ofte under kriteriet i §3. Forslag fra KI om hvilke aksjer man bør følge, er ikke med, fordi det ligger for nær et råd (NFR-06). Vilkårene gjelder personlig bruk. *Lagt til 2026-09-30, Marians beslutning:* en aksje under kriteriet i §3 stoppes med en forklaring som viser median omsetning og kravet. Vil brukeren likevel ha den, legges den til og merkes «Under kravet» overalt der den vises. Første målerunde, for sjømat, står i malinger.md §13. *Rettet 2026-10-02, Marians beslutning:* stoppet ved kriteriet i §3 fra 30.09 gjelder ikke lenger. Appen sier hva signalet er målt på: de 15, som omsettes for 32 til 920 MNOK om dagen (§3). En aksje som omsettes mindre, kan velges og merkes «Utenfor målingen» overalt, i grått, fordi gult betyr 3 av 3 (designregler.md §3). Omsetningen står før brukeren velger når den er målt fra før, ellers etter hentingen, som måler den med samme kall. Utledede tall er ikke EODHDs data (svaret 21.09). |
| **KI-tekst om dagen på forsiden** *(lagt til 2026-10-01)*: noen setninger under tabellen om hele børsdagen: hvor mange som skilte seg ut, hvilke bransjer som trakk opp eller ned, og hvordan dagen var mot uka. Samme bryter som KI-teksten i aksjedetaljen | Epic 10, altså grunnlaget, loggen (FR-604), kontrollen (FR-603) og bryteren (FR-601), og at story 10.4 har vist om KI-teksten hjelper. Grunnlaget er bare utledede tall regnet av kursene: hvor mange som skilte seg ut, og snittendringen per bransje for dagen og for uka. Kommer OSEBX med, kan indeksens endring også stå i grunnlaget. Teksten lages én gang i hentekommandoen, med ett kall til modellen per børsdag | FR-601 sier at bryteren i v1 gjelder KI-teksten i aksjedetaljen, så den må da gjelde begge steder. Kontrollen i FR-603 gjelder også her, med alle 4 punktene, og grunnlaget vises ved teksten. Et spørsmål til EODHD om plan B bør også dekke dette grunnlaget. Teksten gir ikke råd og spår ikke (NFR-06) *Flyttet til v1 2026-10-02, Marians beslutning:* FR-607 og story 10.6. Den venter ikke på at 10.4 har vist om KI-teksten hjelper. |
| **Endring i kroner** *(lagt til 2026-10-01)*: endringen fra forrige børsdag vises også i kroner. I markedsoversikten står kronene på en mindre linje under prosenten, i samme celle. I aksjedetaljen står de ved prosenten, sammen med høy og lav fra raden «Høy, lav og omsetning i aksjedetaljen» | Ingenting nytt. Kronene regnes av `adjusted_close` for de to siste børsdagene, de samme tallene som prosenten (`endring_i_prosent`). Ingen nye kall og ingen endring i basen | FR-101 sier nøyaktig fem kolonner, så kronene står i samme celle som prosenten, slik tidsstempelet står under selskapsnavnet, og FR-101 må endres før idéen bygges. Kronene regnes på samme justerte kurs som prosenten, så de to peker alltid samme vei. På en utbyttedag blir kronene derfor ikke lik forskjellen mellom de to sluttkursene og kan avvike fra børsens egne sider. Dagen merkes etter FR-407. Sorteringen i FR-102 er fortsatt på prosent: 5 kr er 2 % av 250 kr, men 10 % av 50 kr |
| **Innstillinger øverst** *(lagt til 2026-10-01)*: en knapp «Innstillinger» i knapperaden på alle sider, med «Vis hjelp» og «Vis KI-tekst». Valgene gjelder alle sidene og lagres i basen på samme måte som merkingen i Min liste (8.3), så de huskes | Hjelpen (8.0b), KI-teksten (Epic 10) og en tabell for innstillinger i basen | FR-601 sier at bryteren skal kunne brukes under demonstrasjonen mens noen ser på, så hver KI-tekst beholder sin egen bryter ved teksten. Begge styrer samme valg. Ingen innlogging: valgene gjelder maskinen |
| **Omvisning på alle sidene** («Vis meg rundt») *(lagt til 2026-10-01)*: en knapp som viser siden steg for steg, med fast tekst vi har skrevet og sjekket | Hjelpen (8.0b), som omvisningen deler tekstfil med, og at sidene finnes: først markedsoversikten og aksjedetaljen, så Min liste (8.3), og børsometeret hvis det blir bygget | Uten KI. Tall i teksten hentes fra `Parametre`, som i hjelpen. En test sjekker at hvert steg peker på noe som finnes på siden |
| **Egne aksjer** («Følg en aksje») *(lagt til 2026-10-01)*: opptil 3 aksjer i tillegg til de 15, valgt av brukeren og merket «Egen». Hver hentes med samme nøkkel og ett av de fem ekstra kallene, så de er gratis og krever ingen konto; appen har ingen innlogging. Stjernen i Min liste virker også på dem, og hjelpen forklarer dette. Er en aksje under kriteriet i §3, gjelder Marians beslutning i raden «Egne aksjelister»: først en forklaring, og merket «Under kravet» hvis brukeren velger den likevel | At `aksje` kan ha opptil 3 aksjer utenom AKSJEUNIVERS, samme endring av AD-21 som «Egne aksjelister» trenger. Kriteriet sjekkes med ett kall per aksje, som i malinger.md §13, der Bakkafrost var over kravet | Hver aksje tar ett av de fem kallene i NFR-01, så 3 gir 2 kall i margin, og 1 med OSEBX i tillegg. Marians beslutning 01.10: flest mulig, og taket settes ned hvis marginen blir for liten i drift. Grensene i signalet er målt på de 15 (AD-13), og det må stå ved aksjen. *Rettet 2026-10-01:* OSEBX er nå i v1 (FR-410), så det er fire ekstra kall, og 3 egne aksjer gir 1 kall i margin. *Rettet 2026-10-02:* «Under kravet» er erstattet av «Utenfor målingen», se «Egne aksjelister». *Lagt til 2026-10-02 kl. 19:01, Marians beslutning:* én grense for hele lista: opptil 18 aksjer, de 15 og opptil 3 egne. Appen viser plassene som er brukt, for eksempel «16 av 18 aksjer», så det spiller ingen rolle om brukeren legger til én eller flere. 18 aksjer og hovedindeksen gir 19 kall, og 1 er igjen til en ny kjøring (NFR-01). 20 aksjer ville trengt 21 kall. |
| **Måling av omsetning med kall til overs** *(lagt til 2026-10-02, Marians beslutning)*: når kveldens henting har gått bra, måler den median omsetning for nye aksjer med kallene som er til overs, og lar 2 stå igjen til omkjøring. Vil man bruke alle kallene, kjører man målingen selv når man er ferdig for dagen. Den nekter hvis kveldens henting ikke har gått bra, og sier først hvor mange kall den bruker. Aksjene i OBX som ikke er blant de 15, måles først, så resten. Hver aksje måles på nytt etter 3 måneder, og datoen står ved tallet | En tabell for median omsetning og dato per symbol, i en ny migrasjon. Kvotesjekken før målingen. OBX-lista ført inn for hånd | 1 kall per aksje (malinger.md §13): med 1 egen aksje blir det 1 måling per kveld, uten egne 2. *Lagt til 2026-10-02:* med 2 eller 3 egne aksjer blir det ingen måling om kvelden, fordi bare 2 eller 1 kall er igjen etter hentingen, og 2 skal stå igjen (raden «Egne aksjer»). Kjører brukeren målingen selv med alle kallene, måles 2 eller 1, og den sier først at ingen blir igjen til en ny kjøring. Euronext beskriver OBX som de 25 mest omsatte på Oslo Børs, regnet over seks måneder og revidert i mars og september (https://www.euronext.com/en/news/obx-index-0). Det er en ny kilde, lest av et menneske, ikke hentet av programmet. Webserveren henter aldri (AD-10), og rådata committes aldri (regel 10) *Lagt til 2026-10-03, Marians beslutning 02.10 kl. 23:26:* på dager uten henting, som lørdag og søndag, kan alle 20 kallene brukes til måling. |
| **Flere ferdige lister og filter på signalet** *(lagt til 2026-10-02, idé fra Marian)*: «De 15 mest omsatte» som ferdig liste når OBX er målt, og et filter på forsiden for 3 av 3 med positiv eller negativ retning | Målingen i raden over, og «Egne aksjelister» for å bytte liste | En liste på 18 aksjer går innenfor kvoten, men gir 1 kall i margin og ingen egne aksjer. *Rettet 2026-10-02:* klarere ordlyd. Her sto «18 aksjer går i kall». «De 15 mest omsatte» har ikke kravet om minst åtte sektorer i §3. *Rettet 2026-10-02:* §3 sier «sektorer». Her sto «bransjer». Filteret virker bare innenfor lista som er aktiv: hele børsen krever kurser for alle aksjene hver dag, og bulk koster 100 kall (NFR-01). Filteret heter ikke «topp», fordi styrken verken er et råd eller en sannsynlighet (NFR-06, FR-703) |

**Regnestykket for et større univers.** Det er regnet 23.09 fra målte tall: én
henting per døgn, ett kall per symbol (§2), dagskvote 20, og bonus 484 etter
kall 21. **Det forutsettes at bonusen ikke fylles på. Det er ikke kjent.**

*Rettet 2026-10-03 (kontrollen 26.09, P2):* regnestykket bruker 484, tallet 23.09. Bonuskvoten synker når den brukes. Den var 485 fram til kall 21 den 23.09, 484 etter det (`malinger.md` §11), 464 etter innsamlingen til relevanseksperimentet 25.09 (`relevanseksperiment.md` §6) og 463 etter OSEBX-kallet 30.09 (`malinger.md` §14).

| Symboler | Kall per henting | Fra bonus per døgn | Bonusen varer |
|---:|---:|---:|---|
| 15 | 15 | 0 | Urørt. Margin 5 kall per døgn |
| 20 | 20 | 0 | Urørt, men **margin 0**: hver ekstra kjøring tar fra bonus |
| 25 | 25 | 5 | 96 døgn (484 / 5) |
| 30 | 30 | 10 | 48 døgn (484 / 10) |

*Rettet 2026-10-01:* med hovedindeksen i v1 (FR-410) koster hentingen ett kall
mer enn antall aksjer. 15 aksjer gir 16 kall og margin 4.

**Antall rader per skjermbilde avgjøres ikke her.** 15 er valgt av kvoten, ikke
av skjermen. Om oversikten er for tett, er et spørsmål til brukertesten (story 8.1).
