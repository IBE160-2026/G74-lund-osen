---
title: "Endringsforslag 13.10: samlelista, tekstene og rekkefølgen"
status: draft
created: 2026-10-13
updated: 2026-10-13T11:28
---

# Endringsforslag 13.10: samlelista, tekstene og rekkefølgen

Laget med `bmad-correct-course` i modusen Batch, etter instruksjonen kl. 11:17 i
`docs/ai-prompts/2026-10-13.md`. Bygd opp som
[`sprint-change-proposal-2026-10-08.md`](sprint-change-proposal-2026-10-08.md).

**Dette er et utkast.** Samlelista sier at den samlede endringen tas etter
README-prøven 13.–16.10, så forslaget godkjennes først da, og funnene fra prøven
kommer med i punkt 5. Ingenting i `prd.md`, `epics.md`, `designregler.md`,
`sprint-status.yaml`, spinen eller koden er endret. Ingenting endres før rådet
har lest forslaget og Marian har sagt ja (regel 2 og 9).

Grunnlaget er [`samleliste-endringsforslag.md`](../implementation-artifacts/samleliste-endringsforslag.md),
punkt 1–13 med de daterte linjene og utdraget fra designforslaget nederst, og
ordlista i [`designregler.md`](designregler.md) §4. Linjenumrene viser til filene
slik de sto på main 13.10 kl. 11:20.

## 1. Hva som utløste forslaget

**Samlelista.** Marian bestemte 12.10 kl. 12:21 at punkter som dukker opp, samles
og tas i ett endringsforslag, ikke ett og ett. Lista har 13 punkter fra 11.10 og
12.10. De fleste kom da Marian så hjelpen fra 8.0b på skjermen og sammenlignet
den med designforslaget, som ligger på en tavle i Claude og ikke i repoet.

| Punkt | Hva | Typen endring |
|---:|---|---|
| 1, 2 | Kortere hjelp, og tekstene i vanlige ord (NFR-05) | Tekst og test, 8.0c og 8.9 |
| 3, 4 | Hjelp og KI av og på øverst | Story 8.10 |
| 5 | Utseendet fra designforslaget | Story 8.0d, som finnes |
| 6, 12 | Knapperaden og hovedindeksen tidligere | Rekkefølgen i `epics.md` |
| 7, 10 | Tekstene på tavla, kontrollert mot koden | Tekst, 8.0c og 8.9 |
| 8 | Samme ord for signalstyrke, trend og retning | Krav (FR-701, FR-703, FR-704), mal og hjelp |
| 9 | Fire hull fra gjennomgangene 12.10 | Test og dokument |
| 11 | Seks ting fra tavla uten story | Story 8.0c, 8.0d og én ny |
| 13 | Kravlista og dekningstabellen etter 05.10 | `epics.md` |

Ordlista fra tavla ble ført i `designregler.md` §4 13.10, i `bab4adb` og `f33db34`.
Den er kontrollert i punkt 4.3.

**Typen endring.** Ingen nye idéer fra produkteier, og ingenting som er bygget, er
feil i det det gjør. Det som endres, er ord, rekkefølge og hva noen storyer tar
med. Ett unntak: punkt 11 gir oversikten mer innhold (T, B og I i hver rad, delt
tabell og en overskrift), som Marian bestemte 12.10 kl. 22:03.

**Rådets anbefaling.** Øverst i samlelista står det at rådet anbefalte kl. 22:03
og 22:40 at den samlede endringen tas før 8.0c planlegges, fordi 8.0c blir større
med de fire første tingene i punkt 11. Det er ikke avgjort (spørsmål 1 i punkt 7).

## 2. Virkninger

### Epics

Ingen ny epic. Tilbakemeldingen fra faglærer 06.10 ber om at antall epics ikke
vokser ([`tilbakemelding-product-brief.md`](tilbakemelding-product-brief.md)).

| Epic | Virkning |
|---|---|
| **Epic 8** | 8.0c får flere kontrollpunkter (punkt 1, 7, 8 og 11). 8.0d får rekkefølgen av delene på sidene (punkt 11). 8.9 får tekstene fra tavla (punkt 7). 8.10 kan deles, så hjelpebryteren kommer før KI-bryteren (punkt 3 og 4). Én ny liten story for stripa øverst, hvis Marian vil ha den for seg (punkt 11) |
| **Epic 2** | Rekkefølgen for 2.8, 2.9 og 2.9b (punkt 12). 2.12 får «Dine egne aksjer» hvis den delen skal stå for seg (punkt 11) |
| **Epic 10** | Får FR-601, FR-602, FR-603 og FR-605 i dekningstabellen og en FR-linje (punkt 13) |
| **Epic 5** | Beholder bare A-variantene av FR-6xx (punkt 13). Er fortsatt ute av v1 |
| Epic 4, 9 | Ingen virkning, utenom rekkefølgen |

### Andre dokumenter

`prd.md` får ny ordlyd i FR-701, FR-703 og FR-704 (punkt 8). `designregler.md`
får rettelser i §4 der ordlista strider mot krav eller regler (punkt 4.3), og
rekkefølgen av delene på sidene i planen for 8.0d. `sprint-status.yaml` mangler
8.0d i dag. Punkt 6 har hele lista.

## 3. Anbefalt vei

**Direkte justering:** nye kontrollpunkter i storyer som finnes, ny ordlyd i tre
krav, en rettet rekkefølge og opprydding i `epics.md`. Ingenting rulles tilbake,
og ingenting kuttes.

- **Innsats:** liten til middels. Det meste er tekst og kontrollpunkter. Det
  største er punkt 11, som gjør 8.0c større.
- **Risiko:** liten. Ingen endring i hentingen, basen eller signalet. Tekstene i
  hjelpen er låst av tester som henter tallene fra `Parametre`
  (`tests/test_hjelpetekster.py:26–33`), så en kortere tekst kan ikke få feil tall
  uten at en test feiler.
- **Tid:** avhenger av rekkefølgen i punkt 4.7. Bare ett av alternativene der får
  både KI-teksten fra rundt 26.10 og brukertesten 8.1 før uke 45 innenfor farten
  som står i repoet.

## 4. Forslagene i detalj

### 4.1 Punkt 1–5: kortere hjelp, tekstene, bryterne og utseendet

#### Punkt 1 og 2 — Kortere hjelp, i vanlige ord

**I dag.** Hjelpen fra 8.0b står i ett vindu bak «?» ved hver tittel, og tekstene
ligger i `src/hjelpetekster.py`. Tallene i dem hentes fra `Parametre`, og
`tests/test_hjelpetekster.py:26–33` krever dem. Tavla har «Slik leser du
tabellen» med tre korte punkter, noen få korte setninger bak hvert «?», og
«Vis meg rundt» i sju korte steg (samlelista punkt 1).

**Forslag: nye kontrollpunkter i 8.0c.** 8.0c avgjør alt fotnotene (den daterte
linja 11.10 i `epics.md:2715–2722`), så hjelpen tas samme sted.

```
- Hver tekst bak «?» er kort: høyst [N] setninger. Unntak: «Grensene» og
  «Hvorfor retningen oftere er positiv», som forklarer en måling
- Tekstene som kan tas fra tavla, står ordrett, og de som må rettes, står med
  rettet ordlyd (punkt 4.2 i endringsforslaget 13.10)
- Ordene følger ordlista i designregler §4, slik den står etter rettelsene i
  punkt 4.3. En test leter etter ordene ordlista har valgt bort («peker opp»,
  «peker ned», «alle tre», «kroner») i malene og i hjelpetekstene
- Tallene kommer fortsatt fra Parametre, og testene som krever det, står
- **Ville feilet hvis:** en tekst bak «?» var lengre enn grensen, eller «peker
  opp» sto igjen i hjelpen for retning
```

Grensen [N] er ikke avgjort (spørsmål 2). Utdraget fra tavla har tekster på én
til to setninger.

**Forslag: nytt kontrollpunkt i 8.9.**

```
- «Vis meg rundt» har høyst sju steg, og stegene om retning, signalstyrke og
  sjekkene bruker tekstene fra tavla i punkt 4.2
```

**Avhengigheter:** ingen nye. 8.0c avhenger av 8.0 (`epics.md:2713`), og 8.9 av
8.0b og sidene den viser (`epics.md:2960`).

**En test som står i veien.** `RAADSORD` i `tests/test_hjelpetekster.py:173`
tillater ikke ord som «bør», «kjøp» og «selg» i andre hjelpetekster enn
«ikke_raad». Tavlas tekst for retning, «Ikke et råd om å kjøpe eller selge», og
fotnoten «ikke om du bør kjøpe eller selge» kan derfor ikke legges inn som en
vanlig hjelpetekst. De må stå i «ikke_raad» eller i malen, som fotnoten gjør i
dag.

#### Punkt 3 og 4 — Hjelp og KI av og på øverst

**I dag.** Begge valgene står i 8.10 «Innstillinger øverst», som avhenger av 8.3
for knapperaden, 8.0b for hjelpen og 10.3 for KI-teksten (`epics.md:2980`).
Samlelista punkt 3 sier at hjelpebryteren kan komme før KI-bryteren, fordi
hjelpen finnes alt.

**Forslag: 8.10 deles i to.**

```
### Story 8.10: Innstillinger øverst, med «Vis hjelp»
**Avhenger av:** 8.3 for knapperaden og 8.0b for hjelpen

### Story 8.10b: «Vis KI-tekst» i Innstillinger
**Avhenger av:** 8.10 og 10.3
```

Kontrollpunktene i 8.10 står (`epics.md:2971–2978`). Punktet «Bryteren ved
KI-teksten og valget i Innstillinger viser alltid det samme» og «Ville feilet
hvis» om de to bryterne flyttes til 8.10b.

**Et alternativ.** Hjelpebryteren kan komme uten knapperaden, for eksempel ved
«?» øverst på siden, og da før 8.3. Det krever en plass for den som ikke finnes
på tavla i utdraget, så det er spørsmål 3.

#### Punkt 5 — Utseendet fra designforslaget

Story 8.0d finnes (`epics.md:2724–2742`) og avhenger av 8.0b og 8.0c. Den skal
bygges før KI-laget (den daterte linja 11.10, `epics.md:492`). Planen for 8.0d
skriver reglene for utseendet inn i `designregler.md`, og gruppen godkjenner dem
før noe bygges (`epics.md:2735`). Endringen her er bare det punkt 11 legger til
(punkt 4.6).

**Funn:** 8.0d har ingen linje i `sprint-status.yaml`. Den føres inn som
`backlog` når forslaget godkjennes (punkt 6).

### 4.2 Punkt 7 og 10: tekstene fra tavla

Utdraget står nederst i samlelista. Rådet gikk gjennom tavlene 12.10, versjon
1791623938-3408. Hver tekst er kontrollert mot `src/signalberegning.py`,
`src/hjelpetekster.py` og `prd.md`. Kodens verdier: `MA_VINDU = 50` og
`NOYTRALSONE = 0.02` (linje 31 og 34), `VOLUMFAKTOR = 1.5` og `TERSKEL = 2`
(35–36), og begge vinduene på 20 (40–41). Alle tre sjekkene får den
utbyttejusterte kursen (311), og styrken er summen av absoluttverdiene (278).

#### Kan tas som de står

| Tekst (tavle) | Kontrollert mot | Merknad |
|---|---|---|
| Retning: «Om sjekkene som slo ut, ga +1 eller -1. Ikke et råd om å kjøpe eller selge.» (Main) | `finn_retning`, `signalberegning.py:286–293` | Stemmer. Andre setning kan ikke bli en vanlig hjelpetekst (`RAADSORD`, punkt 4.1) |
| Selskapsnavnet: «Klikk for å se sjekkene, tallene bak og kursgrafen.» (Main) | Aksjesiden, `hjelpetekster.py:302–323` | Stemmer |
| Retning i omvisningen (Main) | `finn_retning`; `prd.md:362–366` | Stemmer. Hører til 8.9 |
| Fotnoten: «Signalstyrken sier hvor mange av de 3 sjekkene som slo ut, ikke om du bør kjøpe eller selge.» (Main) | `signalberegning.py:278` | Stemmer med koden, men ikke med ordlyden i FR-703 (`prd.md:1528`). Punkt 8 retter FR-703 |
| Sjekkene: «Hver sjekk gir +1, 0 eller -1. Signalstyrken er hvor mange som slo ut. Ingen vekting og ingen skjult formel.» (Aksje) | `prd.md:1494–1495`; `signalberegning.py:278` | Stemmer |
| Trend: «Slår ut når kursen ligger mer enn 2 % over eller under snittet.» (Aksje) | `signalberegning.py:176`, strengt større enn | Stemmer |
| Bevegelse: «Endringen fra børsdagen før, mot de vanlige svingningene de 20 børsdagene før. Slår ut over 1 standardavvik.» og «Måles mot hvor mye akkurat denne aksjen pleier å svinge.» | `signalberegning.py:192–197` | Stemmer |
| Interesse: «Volumet mot medianvolumet de 20 børsdagene før. Slår ut over 1,5 × medianen, i samme retning som endringen.» og «Volum har ingen retning, så fortegnet følger dagens endring.» | `signalberegning.py:217–223` | Stemmer. At uendret kurs gir 0, står ikke på tavla, men står i hjelpen i dag (`hjelpetekster.py:256–259`) |
| Styrken: «Styrken er hvor mange sjekker som slo ut. Ga noen +1 og noen -1, er retningen Blandet.» (Aksje) | `signalberegning.py:278, 286–293` | Stemmer |
| «Hver sjekk ser på sin del av dataene: kursnivå, endring og volum. Da ser du hva som ga utslaget.» (Aksje) | `hjelpetekster.py:272–273`; `begrunnelser.md:269` | Stemmer |
| «Trend varer, de 2 andre er hendelser. I en stigende periode blir retningen derfor oftere Positiv.» (Aksje) | `begrunnelser.md:276–278`; `hjelpetekster.py:290–293` | Stemmer |

Tallene i tekstene (2 %, 20, 1,5, 1 standardavvik) skal hentes fra `Parametre`
når de legges inn, som i dag.

#### Må rettes før de brukes, med rettet ordlyd

| Tekst (tavle) | Hvorfor | Rettet ordlyd |
|---|---|---|
| «3 faste sjekker måler sluttkurs og volum» (Main) | Trend, bevegelse og fortegnet i interesse bruker utbyttejustert kurs (`signalberegning.py:311`) | «3 faste sjekker måler kurs og volum». Samme ord som aksjesiden: «Signalet bygger bare på kurs og volum.» (`aksje.html:190`) |
| «Sluttkursen mot/lå … snittet» (Main, flere steder) | Trend bruker `justert_slutt` (svar 3 11.10) | «Kursen, justert for utbytte, lå … snittet», eller «Kursen lå …» der hjelpen alt har sagt at kursen er justert. Utdraget gir ikke hver setning ordrett, så de rettes når rådet gir dem (spørsmål 4) |
| «Grensene er valgt etter målinger …» (Aksje) | De ble kontrollert før de ble låst, ikke valgt etter målingen (`hjelpetekster.py:280–284`) | «Grensene ble kontrollert mot 15 aksjer over 199 børsdager, fra desember 2025 til september 2026, før de ble låst.» Tallene fra `MAALTE_AKSJER`, `MAALTE_BOERSDAGER` og `MAALT_PERIODE`, som i dag |
| «summen av tallene uten fortegn» (TydeligMerking) | Svar 3 11.10 tok det ut. Står fortsatt i `aksje.html:164` | «Signalstyrken er hvor mange sjekker som slo ut.» Samme rettelse i `aksje.html:164` (punkt 4.4) |

Merknad om «Grensene»: de to vinduene på 20 dager ble målt på et vindu som er
forskjøvet én handelsdag (`signalberegning.py:13–15`). Hjelpen sier ikke det i
dag, og tavla heller ikke.

#### Venter til det er bygget

| Tekst eller del | Story |
|---|---|
| T, B og I i tabellen, og klikk på dem | Ny i 8.0c (punkt 4.6) |
| «N av 3» | 8.0c (`epics.md:2700`) |
| Hovedindeksen og søylene | 2.9 og 2.9b |
| Egne aksjer | 2.12 |
| Min liste | 8.3 |
| Innstillinger | 8.10 |
| KI-teksten | 10.3 og 10.6 |
| Den svarte stripa | 8.0d, og «Neste» i punkt 4.6 |
| Periodevalget | 8.16 og 8.17 |
| Historikken | 2.7 |
| U-dager | 8.14, med ordet «justeringsdag» (punkt 4.3) |
| «Hva du kan sjekke selv» og det grå feltet | Ikke funnet i `epics.md`. Spørsmål 5 |

### 4.3 Ordlista i designregler §4 mot koden, PRD-en og §1–3

Ordlista har 31 punkter og en sluttsetning (`designregler.md:59–91`). Hvert punkt
er kontrollert mot koden, `prd.md`, `designregler.md` §1–3 og `epics.md`. Det
meste stemmer eller venter bare på en story. Det som strider mot et krav eller en
regel, står først.

#### Strider mot et krav eller en regel

| # | Ordlista sier | Kilden sier | Forslag til rettelse i §4 |
|---:|---|---|---|
| 21 | «U ved kursen: aksjen har betalt utbytte i perioden.» | FR-407: «grafen og teksten sier «justeringsdag», ikke «utbytte»» (`prd.md:511–512`). Story 8.14: «Ordet «utbytte» står ikke ved dagene. En test krever det» (`epics.md:3064`). Metoden ser justeringer, og en splitt gir samme utslag | «Merket ved kursen: en justeringsdag i perioden. Sluttkursen er ikke justert, endringen er det, så de to stemmer ikke helt (FR-101, FR-407).» Om merket fortsatt skal være bokstaven U, er spørsmål 6 |
| 25 | «Gul strek: det viktigste på siden.» | §3: «Gult betyr 3 av 3» (`designregler.md:42`), og samme farge overalt gjør det lett å finne (linje 49) | Det viktigste merkes uten gult. Hvordan, er spørsmål 7 |
| 20 | «… datoen står i gult under.» | §3, som over. Ordlista grunngir selv grått for «Utenfor målingen» med at gult betyr 3 av 3 | Datoen står under, uten gult |
| 22 | «Ikke vurdert: en dag uten lagret vurdering. … (designregler §2, story 2.7).» | §2: «ikke vurdert» gjelder en børsdag uten rad. Har raden en grunn, står grunnen, og en dag som ikke er børsdag, viser «– ikke børsdag» (`designregler.md:34–35`). At signalet aldri regnes på nytt, står i FR-101 (`prd.md:267`) og 2.7, ikke i §2 | «Ikke vurdert: en børsdag uten lagret vurdering. Har raden en grunn, står grunnen, og en dag som ikke er børsdag, står som «ikke børsdag» (§2, FR-409). Signalet regnes aldri ut på nytt i ettertid (FR-101, story 2.7).» Story 2.7 bruker fortsatt det gamle ordet «ikke kjørt» (`epics.md:1550`), som rettes i `epics.md` |
| 6, 9, 19 | Kolonnehodet sier «i går»; gult betyr 3 av 3 «i går»; periodevalget begynner med «I går» | §2: første knapp heter «I går», «I dag» eller ukedagen (`designregler.md:32`). §3 sier «siste børsdag» | Ordlista følger §2 og §3: «siste børsdag», og knappen heter «I går», «I dag» eller ukedagen |
| 32 | «Ord kan endres rett i tavla.» | Innledningen til `designregler.md`: «En regel endres bare her, med dato og grunn» (linje 10) | «Ord endres her, med dato og grunn, og så i tavla.» |
| 2 | Sjekkene skrives «T +1» overalt, «som kolonnen «Ga» i appen» | Ga-kolonnen viser bare «+1», og navnet står i en egen kolonne (`aksje.html:147–148`, `aksjedetalj.py:63`). 8.0c sier tall og ord: «positiv ved +1, negativ ved -1 og ingen utslag ved 0» (`epics.md:2701`) | Ett av dem må vike. Spørsmål 8 |

#### Strider mot det som er bygget, uten å bryte et krav

| # | Ordlista sier | I dag | Forslag |
|---:|---|---|---|
| 14 | 50-dagers snittet er heltrukket. Stiplet linje er bare for hovedindeksen | Snittet er stiplet (`aksje.html:41, 47`), og hjelpen sier «den stiplede er snittet» (`hjelpetekster.py:304`) | Endres i 8.0d, med hjelpeteksten. Ingen krav i PRD-en sier noe om det |
| 3 | Pilene brukes bare for retning | Tilbakelenken er «← Markedsoversikt» (`aksje.html:76`) | Lenken får tekst uten pil i 8.0d |
| 4 | 3 av 3 er «fylt med gul ring» | §3: «gul ring rundt pillen «3 av 3»» (`designregler.md:46`) | «med gul ring rundt», som §3 |
| 10 | «Utenfor målingen: en egen aksje som omsettes for under 32 MNOK» | PRD: «omsettes mindre enn de 15 ble målt på» (`prd.md:1059`), og den laveste ligger på 32,3 MNOK (`prd.md:214`). Etter 08.10 kan hele lista byttes, så «en egen aksje» er utdatert | Ordlista følger PRD-en: «en aksje som omsettes for mindre enn de 15 ble målt på» |

#### Står ikke i noen kilde i repoet

| # | Ordlista sier | Merknad |
|---:|---|---|
| 12 | 13 bransjer, ICB, OBSFX og OBSHX, fem nye | Koden har 8 sektorer (`kursdata.py:42–55`), og PRD-en sier «minst åtte sektorer» (`prd.md:182–184`). Spørsmål 9 |
| 8 | «når neste oppdatering tidligst kan komme» | Ikke i PRD-en eller `epics.md`. Hører til «Neste» i punkt 4.6 |
| 11 | Tallet står med «for hovedindeksen» | Ikke funnet. Hører til 8.4 |
| 20 | «Retningen står bare for i går» | Ikke funnet. Hører til 8.17 |
| 25 | Prikket strek ved sjekkede tall i KI-teksten | Ikke funnet. Hører til 10.3 |
| 23 | Den ordrette teksten «Laget av KI» | FR-602 sier «merket som laget av KI, med modellnavnet» (`prd.md:1252`). Ordlyden avgjøres i 10.3 |
| 16 | Hovedvalget til høyre i en dialog, og «Følg aksjen» | Appen har ingen dialoger. PRD-en sier «Følg en aksje» (`prd.md:123`) |

#### Stemmer, eller venter bare på en story

Punkt 1, 5, 7, 11, 13, 15, 17, 18, 24, 26, 27, 28, 29, 30 og 31. To av dem er
ikke tatt inn i appen ennå, selv om ingen krav sier noe annet: tall med sifre
(5), der hjelpen og fotnoten skriver «de tre sjekkene» (`hjelpetekster.py:177`,
`index.html:137–138`), og datoer som «22.09» (15), der appen viser ISO-dato
(`index.html:73`, og `"%Y-%m-%d kl. %H.%M"` i `markedsoversikt.py:274`). Begge kan
tas i 8.0c, med en test.
