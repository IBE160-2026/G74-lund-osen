---
title: "Endringsforslag 13.10: samlelista, tekstene og rekkefølgen"
status: draft
created: 2026-10-13
updated: 2026-10-13T12:29
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

*Rettet 2026-10-13, Marians beslutning kl. 11:34:* forslaget godkjennes uten å vente på README-prøven, så 8.0c kan planlegges denne uka. Bare rekkefølgen (spørsmål 14 og 15) venter til etter prøven, «når farten er kjent». Funn fra prøven blir små rettelser. Det over om at forslaget godkjennes først etter prøven, gjelder ikke lenger. Status står som `draft` til svarene og de nye punktene i 4.9 er ført inn i `prd.md` og `epics.md`.

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

*Rettet 2026-10-13, Marians beslutning kl. 11:34:* avgjort. Den samlede endringen tas før 8.0c planlegges (svar 1).

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

*Rettet 2026-10-13:* Epic 10 får FR-601, FR-602 og FR-603. FR-605 står i Epic 4, som punkt 4.8 sier.

*Lagt til 2026-10-13, etter svarene og punkt 4.9:* Epic 2 får 2.15, utbytte fra EODHD (N1), og 2.11 og 2.12 får de 13 bransjene (N3). Epic 8 får 8.0e (svar 12), 8.10b og 8.19 (svar 13). Epic 10 får et tillegg i 10.1 og 10.2 hvis beslutningen 04.10 endres (N2, spørsmål 23).

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

### 4.4 Punkt 8: samme ord for signalstyrke, trend og retning

Koden er fasit. `finn_styrke` er `sum(abs(verdi))` (`signalberegning.py:278`),
altså hvor mange sjekker som slo ut, og alle tre sjekkene får den utbyttejusterte
kursen (`signalberegning.py:311`).

**Krav: FR-701, tabellen** (`prd.md:1499`).

```
| 1 | **Trend** | Utbyttejustert kurs mot 50-dagers glidende snitt | Kursen ligger mer enn **2 %** over eller under snittet |
```

*Her sto:* «Sluttkurs mot 50-dagers glidende snitt». Setningen under tabellen,
«Alle beregninger bruker `adjusted_close`» (`prd.md:1507`), står. Det var bare
tabellen som sa noe annet.

**Krav: FR-703, første avsnitt** (`prd.md:1527–1529`).

```
Signalstyrke er summen av absoluttverdiene til de tre sjekkene, altså et helt
tall fra 0 til 3: hvor mange av sjekkene som slo ut. Styrken sier ikke hvor
sannsynlig en kursbevegelse er, og ikke om aksjen bør kjøpes eller selges.
```

*Her sto:* «Styrken sier hvor kraftig sjekkene slår ut — ikke hvor sannsynlig en
kursbevegelse er, og ikke om aksjen bør kjøpes eller selges.» Definisjonen er den
samme. Bare forklaringen endres.

**Krav: FR-704, tabellen** (`prd.md:1540–1545`). Hjelpen følger FR-704 i dag
(«peker opp», `hjelpetekster.py:69–74`). Bytter hjelpen til +1 og -1 uten at
FR-704 følger med, sier de to hver sin ting.

```
| Positiv | Alle utslag er +1 |
| Negativ | Alle utslag er -1 |
| Blandet | Noen utslag er +1 og noen -1 |
| Ingen | Ingen av sjekkene ga utslag (styrke 0) |
```

*Her sto:* «Alle utslag peker opp», «Alle utslag peker ned» og «Utslagene
spriker».

**Fotnoten under oversikten** (`index.html:134–139`). Første del står, fordi
hjelpen viser til den ordrett (`hjelpetekster.py:135`, og testen i
`tests/test_hjelpetekster.py:196–207`).

```
Sluttkursen er den ujusterte kursen aksjen omsettes til. Endringen er
regnet på utbyttejustert kurs, slik at et ordinært utbytte ikke ser ut
som et kursfall. Signalstyrken sier hvor mange av de 3 sjekkene som slo
ut, ikke om du bør kjøpe eller selge.
```

*Her sto:* «Signalstyrken er 0–3 og sier hvor kraftig de tre sjekkene slår ut —
ikke om aksjen bør kjøpes eller selges.» Siste setning er tavlas fotnote ordrett.
Raden for NFR-06 i `epics.md:352` siterer den gamle fotnoten, med linjenummeret
`index.html:108`, som ikke stemmer lenger. Den får en datert linje, som den
daterte linja 11.10 under 8.0c sier (`epics.md:2721`).

**Aksjesiden** (`aksje.html:164`): «Signalstyrken er summen av tallene uten
fortegn:» blir «Signalstyrken er hvor mange sjekker som slo ut:». Resten av
setningen står. Det er også utsatt arbeid i `deferred-work.md:138` og funn 23 i
gjennomgangen av 8.0b.

**Hjelpen** (`src/hjelpetekster.py`):

| Hvor | I dag | Ny |
|---|---|---|
| Retning, Positiv (linje 70) | «alle sjekkene som slo ut, peker opp.» | «alle sjekkene som slo ut, ga +1.» |
| Retning, Negativ (71) | «alle sjekkene som slo ut, peker ned.» | «alle sjekkene som slo ut, ga -1.» |
| Retning, Blandet (72) | «sjekkene som slo ut, spriker.» | «noen ga +1 og noen -1.» |
| Retning (197–198) | «Retningen sier hva sjekkene peker mot, ikke hvor kursen går videre.» | «Retningen sier om sjekkene som slo ut, ga +1 eller -1, ikke hvor kursen går videre.» |
| Signalstyrke (177) | «hvor mange av de tre sjekkene som ga +1 eller -1» | «hvor mange av de 3 sjekkene som ga +1 eller -1» |

Ingen test låser «peker opp», «hvor kraftig» eller «summen av tallene» i malene
eller hjelpen. Treffene i `tests/` er bare kommentarer
(`tests/test_signalberegning.py:126–128`, `tests/test_docker.py:884`). Testen i
punkt 4.1 som leter etter ordene ordlista har valgt bort, låser den nye
ordlyden.

**Hvor:** malene og hjelpen i 8.0c. PRD-en endres når forslaget godkjennes.
Når 8.0c gir tabellen «N av 3» (`epics.md:2700`), sier hjelpen det samme.

### 4.5 Punkt 9: fire hull fra gjennomgangene 12.10

| Hull | Slått opp | Forslag |
|---|---|---|
| Ingen test sjekker at `../README.md#status` i `docs/innlevering.md` peker på en overskrift | Lenken står i `docs/innlevering.md:34`. `tests/test_readme.py` sjekker bare lenkene i README-en, og den ser bort fra ankeret etter `#` (linje 17 og 27). Ingen test leser `docs/innlevering.md` | En test: hvert anker fra `docs/innlevering.md` til README-en svarer til en overskrift. **Ville feilet hvis** «## Status» fikk nytt navn |
| Taggen i linja om briefen under «Dokumentene» er ikke knyttet til regel 17 | `test_til_faglaerer_lenker_til_briefen_med_gjeldende_tag` (`tests/test_docker.py:917`) sjekker bare lista under «Til faglærer:». Linja under «Dokumentene» (`README.md:250`) har både `-v7` og `-v8` | Testen utvides til linja under «Dokumentene»: den gjeldende taggen står der, og en eldre tag står bare som historikk. Hvordan «historikk» skal kjennes igjen, avgjøres i planen |
| Testen for «Status» sjekker ikke at en sak under Flettet til main mangler under Neste | `tests/test_docker.py:855` sjekker bare den andre veien. Også funnet i Verification Gap av flettingen 12.10 | `assert sak not in neste` for sakene under Flettet til main. **Ville feilet hvis** «kallene som er igjen» sto begge steder |
| `updated` i `docs/hjelp.md` ble ikke satt i flettingen av PR #28 | Står på 2026-10-12T10:26, også etter `c3d6660` | Settes fra klokka neste gang fila endres (regel 4), med en linje i dagsfila om hvorfor |

**Hvor:** tre tester og én frontmatterlinje, uten en story. Forslaget er én commit
per sak rett på main etter godkjenningen, eller i 8.0c. Spørsmål 10.

### 4.6 Punkt 11: seks ting fra tavla som ikke har en story

Marian bestemte 12.10 kl. 22:03 at alle seks skal med. Ingen av dem står i 8.0c
eller 8.0d i dag. Det nærmeste er setningen for dager uten utslag i 8.0c, «Ingen
aksjer skilte seg ut: ingen fikk 2 av 3 eller mer.» (`epics.md:2706`).

FR-101 sier «nøyaktig fem kolonner» (`prd.md:240`), og en sjette ville bryte
kravet (`prd.md:312–314`). Tabellen har fem i dag: Selskap, Sluttkurs, Endring,
Signalstyrke og Retning (`index.html:80–84`).

**Rådets forslag** (samlelista punkt 11): de fire første i 8.0c, «Neste» som egen
liten story eller i 8.0d, og rekkefølgen inn i `designregler.md` i planen for
8.0d.

#### 1. T, B og I i hver rad

```
- Hver rad med vurdering viser T, B og I med +1, 0 eller -1 i cellen for
  signalstyrke, under «N av 3». Tabellen har fortsatt fem kolonner (FR-101)
- Verdiene leses fra den lagrede vurderingen, aldri regnet på nytt (FR-101,
  `prd.md:267`)
- En rad uten vurdering viser grunnen, som i dag, og ingen T, B eller I
- **Ville feilet hvis:** tabellen fikk en sjette kolonne, eller en rad uten
  vurdering viste T, B og I
```

Formen («T +1» eller «+1 positiv») avhenger av spørsmål 8. Klikk på T, B og I
venter (punkt 4.2). Hvor klikket skal føre, er ikke beskrevet i utdraget.

#### 2. Tabellen delt i «Skilte seg ut», «Øvrige aksjer» og «Dine egne aksjer»

```
- Radene med styrke på terskelen eller mer står under «Skilte seg ut», og de
  andre under «Øvrige aksjer». Terskelen kommer fra Parametre (FR-705)
- Er ingen over terskelen, står setningen fra 05.10 i stedet for «Skilte seg ut»
- **Ville feilet hvis:** en rad med 1 av 3 sto under «Skilte seg ut», eller
  terskelen var skrevet fast i malen
```

«Dine egne aksjer» kan ikke bygges før egne aksjer finnes (2.12), og «Egen»
avgjøres i planen for 2.12 (`prd.md:1064`). Ordlista sier dessuten at en egen
aksje «står i tabellen sammen med de andre og sorteres likt» (§4, punkt 9). Det
strider mot en egen del for dem. Spørsmål 11.

Sorteringen i 8.15 må da gjelde innenfor hver del. Det er et nytt kontrollpunkt i
8.15 hvis delingen kommer først.

#### 3. Overskriften «4 av 15 aksjer skilte seg ut tirsdag», med innledningen

```
- Over tabellen står «N av M aksjer skilte seg ut <ukedag>», der N og M telles
  fra radene, og ukedagen er børsdagen vurderingene gjelder, på norsk
- Er N 0, står setningen fra 05.10 (epics.md:2706)
- **Ville feilet hvis:** M var skrevet fast som 15, eller ukedagen var dagen
  siden ble åpnet og ikke børsdagen
```

Innledningen under overskriften står ikke i utdraget. Spørsmål 4.

#### 4. «Slik leser du tabellen»

```
- Over tabellen står «Slik leser du tabellen» med tre korte punkter. To av dem er
  tavlas tekster om retning og selskapsnavnet (punkt 4.2)
- **Ville feilet hvis:** et punkt brukte et ord ordlista har valgt bort
```

Det tredje punktet står ikke i utdraget. Spørsmål 4.

#### 5. «Neste: … etter kl. 22» i stripa

8.0d sier «Ingen nye funksjoner» (`epics.md:2739`). «Neste» er en ny funksjon:
den sier når neste henting tidligst kan komme. To plasseringer:

- **A, ny liten story (rådets første forslag).**

  ```
  ### Story 8.19: Neste henting i stripa øverst

  **Kontroll — hva testen ser etter:**
  - Stripa øverst sier når dataene ble hentet, og når neste henting tidligst
    kan komme: «Neste: <dag> etter kl. 22»
  - Klokkeslettet kommer fra KL_22 i fetch_prices.py (linje 91), og dagen fra
    boersdag.py, ikke skrevet fast
  - Ingen API-kall
  - **Ville feilet hvis:** stripa sa i morgen en fredag, eller klokkeslettet
    sto fast i malen

  **Avhenger av:** 8.0d for stripa
  ```

- **B, i 8.0d.** Unntaket «bortsett fra Neste i stripa» skrives inn i
  kontrollpunktet «Ingen nye funksjoner». Det er færre storyer, men 8.0d blir
  ikke bare utseende lenger.

#### 6. Rekkefølgen av delene på sidene

Står bare i notatene på tavla, ikke i `designregler.md`. 8.0d sier alt at planen
skriver reglene for utseendet inn i `designregler.md` og at rådet gir utdraget
(`epics.md:2735`). Forslag: «rekkefølgen av delene på hver side» legges til i den
lista.

#### En annen plassering for 1–4

8.0c har alt mange kontrollpunkter: tre under «Kontroll», tre i den daterte
linja 05.10 kl. 22:24 og sju i den daterte linja 11.10 (`epics.md:2698–2722`), og
«Én økt: ja» (`epics.md:2713`). Med punkt 1, 2,
4.4 og 4.6 blir den trolig ikke én økt.

- **Rådets forslag:** 1–4 i 8.0c.
- **Alternativ:** 8.0c som i dag, med ordene fra punkt 4.4 og hjelpen fra punkt
  4.1. 1–4 i en ny story 8.0e «Oversikten fra designforslaget», som avhenger av
  8.0c og kommer før 8.0d, så utseendet legges på den nye oversikten. 8.0c blir
  da fortsatt én økt, og 8.0e kan planlegges når utdraget for innledningen og
  det tredje punktet finnes.

Marian velger (spørsmål 12).

### 4.7 Punkt 6 og 12: rekkefølgen etter README-prøven

**Rekkefølgen i dag** står i `epics.md:476–488`, punkt 1–12. Punkt 1 og 2 er
gjort, og av punkt 3 er 2.3b og 8.0b flettet. 8.0d kommer etter 8.0b og 8.0c og
før KI-laget (`epics.md:492`). «Rekkefølgen tas opp igjen etter README-prøven,
når farten er kjent» (`epics.md:494`).

**Det som bryter avhengighetene i dag:**

| Brudd | Kilde |
|---|---|
| 8.12 (punkt 7) trenger 8.3 (punkt 10) og 8.17 (punkt 9) | `epics.md:3025`, og den daterte linja 08.10 kl. 21:48 (`epics.md:490`) |
| 8.17 (punkt 9) trenger 8.3 (punkt 10) | `epics.md:3141`, og linja kl. 21:48 |
| 10.6 (punkt 8) trenger hovedindeksen, FR-104 og FR-410, som er 2.9 og 2.8 (punkt 9) | `epics.md:2413`. Dette står ikke i linja kl. 21:48 |
| 8.1 krever at 2.9 og 2.9b er ferdige før testen, så 8.1 kan tidligst komme etter punkt 9 | `epics.md:2772` |
| 8.3 skal bygges etter brukertesten i 8.1 | `epics.md:2825` |
| 2.8 trenger 4.3, fordi `ki_logg` er migrasjon `0005` | `epics.md:1579` |
| 8.10 trenger 10.3 for KI-teksten | `epics.md:2980`. Punkt 4.1 foreslår å dele den |
| 8.9 bygges etter sidene den viser | `epics.md:2960` |

**Farten.** Endringsforslaget 08.10 regnet om lag 0,8 storyer per dag (7 storyer
29.09–07.10) og kalte det grovt
([`sprint-change-proposal-2026-10-08.md`](sprint-change-proposal-2026-10-08.md)
§5). Fra 08.10 til 12.10 ble 2.3, 3.1, 3.2, 3.3, 8.0b og 2.3b flettet, og 3.4 i
flere PR-er (git-loggen). Det er om lag 1,2 per dag med de seks, regnet her og
ikke ført noe annet sted. Begge tallene er brukt under. Fra 16.10 er det 10 dager
til 26.10 og 17 dager til mandag 02.11, da uke 45 begynner.

Plassene under teller fra første story etter README-prøven. Ny 8.0e eller 8.19
(punkt 4.6) gir én plass til hver der de står.

#### A — dagens rekkefølge, bare rettet for avhengighetene

1. 8.0c, 8.0d
2. 4.0, 4.2, 4.3, 10.1, 10.2
3. 10.3, 3.4b
4. 8.15, 8.16, 8.7
5. 2.7, 8.8, 2.6, 8.14, 2.14, 8.18
6. 10.7
7. 2.8, 2.9, 2.9b, 8.1, 8.6, 10.6
8. 8.3, 8.17, 8.12, 8.10, 8.9, 8.13
9. Lista: 2.11, 2.12, 2.13, 8.11

- **KI-laget:** 10.2 er plass 7. Om lag 9 dager med 0,8 per dag og 6 med 1,2.
  KI-teksten fra rundt 26.10 holder med begge.
- **8.1:** plass 23. Om lag 29 dager med 0,8 og 19 med 1,2. Kommer etter
  02.11 med begge, så 8.1 før uke 45 holder ikke.

#### B — knapperaden tidligere (samlelista punkt 6)

1. 8.0c, 8.0d
2. 4.0, 4.2, 4.3, 10.1, 10.2
3. 10.3, 3.4b
4. 8.3, 8.10, 8.13, og 8.9 når sidene den viser, finnes
5. Resten som i A

- Krever at linja «Bygges etter brukertesten i 8.1» i 8.3 (`epics.md:2825`)
  endres, ellers kan 8.3 ikke komme før 8.1. Spørsmål 15.
- Med delingen i punkt 4.1 kan hjelpebryteren (8.10) komme rett etter 8.3, og
  KI-bryteren (8.10b) står allerede etter 10.3.
- **KI-laget:** som A, plass 7.
- **8.1:** enda senere enn i A, fordi 2.9 og 2.9b skyves bak. Holder ikke.

#### C — hovedindeksen tidligere (samlelista punkt 12)

1. 8.0c, 8.0d
2. 4.0, 4.2, 4.3, 10.1, 10.2
3. 2.8, 2.9, 2.9b
4. 10.3, 3.4b
5. 8.1
6. 8.6, 10.6
7. Resten som i A, med 8.3 etter 8.1

- 2.8 kan ikke komme før 4.3 (`epics.md:1579`), så hovedindeksen kan ikke legges
  før KI-laget uten en endring som ikke finnes.
- Punkt 5 i dag sier at 10.3 og 3.4b kommer «før de nye storyene». 2.8–2.9b er
  fra 01.10 og ikke blant de nye fra 08.10, så ordlyden brytes ikke. Om det er
  meningen, avgjør Marian.
- **KI-laget:** 10.2 er fortsatt plass 7, så teksten lages fra rundt 26.10.
  Visningen (10.3) kommer på plass 11.
- **8.1:** plass 13. Om lag 16 dager med 0,8 og 11 med 1,2. Før 02.11 med
  begge, men med 0,8 per dag bare akkurat, og ingenting annet kan legges inn
  mellom 2.9b og 8.1.
- 10.6 og 8.6 blir mulige tidlig, og bruddet for 10.6 i dag er borte.

Legges 2.8–2.9b i stedet før 10.1, blir 10.2 plass 10, og KI-teksten fra rundt
26.10 holder ikke med 0,8 per dag.

**Oppsummert:** bare C får både KI-teksten fra rundt 26.10 og 8.1 før uke 45
innenfor farten som står i repoet. B gir knapperaden tidligere, men skyver 8.1
lenger bak. Marian velger (spørsmål 14).

### 4.8 Punkt 13: kravlista og dekningstabellen etter 05.10

PRD-en skrev FR-601 til FR-607 om etter valget av tjeneste 05.10, og kravene fra
før plan B står ordrett i §4.6A, med en A på dem som bare gjelder meldinger:
«Dette er innledningen og kravene fra §4.6 slik de sto før plan B, ordrett.
Kravene som bare gjelder meldinger, har fått en A.» (`prd.md:1389–1390`). Det
finnes ingen FR-601A og ingen FR-605A. `epics.md` er ikke fulgt etter.

**Lista under «4.6 KI-laget og grensen mot regelbasert kode»** (`epics.md:128–137`):

| Linje | I dag | Ny, etter `prd.md` |
|---:|---|---|
| 132 | FR-603 — Usikkerhet vises som forbehold, ikke som rekkefølge | FR-603 — KI-teksten sier ikke mer enn grunnlaget (`prd.md:1273`) |
| 134 | FR-605 — Promptversjon og modell lagres med hver vurdering | FR-605 — Promptversjon og modell lagres med hver KI-tekst (`prd.md:1337`) |

Under lista kommer en linje om 4.6A: FR-602A, FR-603A, FR-604A og FR-606A gjelder
plan A, utenfor v1 (`prd.md:1386–1452`). Alle andre titler i lista er like i
ordlyden som i `prd.md`, og antallet, 51 FR-er, stemmer (`epics.md:165`).

**Dekningstabellen** (`epics.md:317–322`):

| I dag | Ny |
|---|---|
| FR-601, FR-602, FR-603, FR-606 \| Epic 5 🔒 | FR-601, FR-602, FR-603 \| Epic 10 |
| | FR-606 \| ikke i v1: skalaen brukes ikke i applikasjonen (`prd.md:1368`) |
| | FR-602A, FR-603A, FR-604A, FR-606A \| Epic 5 🔒 |
| FR-604, FR-605 \| Epic 4 | Står. 4.2 oppfyller begge (`epics.md:2053`) |
| FR-607 \| Epic 10, og FR-608 \| Epic 10 | Står |

**FR-linjene:** Epic 5 (`epics.md:554`) får A-variantene i stedet for FR-601,
FR-602, FR-603 og FR-606. Epic 10 har ingen FR-linje i dag. Den får FR-601,
FR-602, FR-603, FR-607 og FR-608.

**Hvilken story som oppfyller hva.** I Epic 10 står FR-601–605 bare i
kontrollpunktene, ikke i «Oppfyller». Kontrollen i FR-603 er en ren funksjon i
10.2 (`epics.md:2243`), og 10.3 sier at siden sier hvorfor når KI er av (FR-601,
`epics.md:2309`). Forslag: 10.2 oppfyller FR-603, og 10.3 oppfyller FR-601 og
FR-602. 8.10 (eller 8.10b) begrenses fortsatt av FR-601 (`epics.md:2969`).
Spørsmål 17.

**Daterte linjer** der teksten fortsatt bygger på A-innholdet: `epics.md:561`
(FR-602, FR-604 og FR-606 sitert som meldingskrav) og `epics.md:2106` («FR-6xx
handler om meldinger»), og storyene 5.1–5.4, som oppfyller FR-601, FR-602,
FR-603 og FR-606 (`epics.md:2116`, `2131`, `2147`, `2162`). Linjene sier at
storyene gjelder kravene slik de sto før 05.10, nå A-variantene og FR-601.

**Ordet «utbytte» på tavla** (andre halvdel av punkt 13) er tatt i punkt 4.3,
linje 21 i ordlista.

### 4.9 Nye punkter 13.10

*Lagt til 2026-10-13, Marian kl. 11:50–11:58, etter instruksjonen kl. 12:19 i
`docs/ai-prompts/2026-10-13.md`.*

#### N1 — Utbytte fra EODHD

**I dag.** `/api/eod` har intet utbyttefelt (`begrunnelser.md` §11), så
justeringsdagen leses av kursserien, og «Metoden ser justeringer, ikke utbytter.
En aksjesplitt gir samme utslag.» (§11, forbehold 1). Derfor sier FR-407 og 8.14
«justeringsdag», ikke «utbytte» (`prd.md:507–513`, `epics.md:3064`). Kommende
eks.datoer skal føres inn for hånd (FR-414, story 2.14), fordi EODHDs kalender
svarer 403 på gratisnivået (`prd.md:1109–1110`).

**Hva Marian vil.** Utbytte hentes fra EODHD med `/api/div/{symbol}?fmt=json`.
Instruksjonen kl. 12:19 sier at endepunktet er med i gratisnivået, med ett års
historikk, og koster 1 kall per aksje (EODHD-dokumentasjonen, «Splits and
Dividends API»). Det står ikke i repoet. `docs/kilder-og-rettigheter.md:31` viser
at `/api/calendar` svarte 403 «Only EOD data allowed for free users». Spørsmål
22.

**Krav: ny FR-415 — Utbytte fra kilden.** Neste ledige nummer i §4.4 etter
FR-414 (`prd.md:1095`). FR-407 rettes etter svar 6: merket under kursen sier
«utbytte» når dataene fra EODHD har utbytte den dagen, ellers «justeringsdag».

```
### Story 2.15: Utbytte fra EODHD

Som **bruker**, vil jeg se hva aksjen har betalt i utbytte det siste året, så
jeg forstår en dag der kursen og endringen spriker.

**Oppfyller:** FR-415, og FR-407 slik den rettes · **Begrenses av:** NFR-01,
NFR-06, NFR-08, `AD-6`, `AD-10`, regel 10 og 16

**Kontroll — hva testen ser etter:**
- Ett kall til /api/div per aksje i lista, én gang i uka, bare med kallene som
  er igjen etter kveldens henting og nye forsøk (2.3b)
- Bruker aldri bonuskvoten: står extraLimit lavere etter første kall, stopper
  den (NFR-01, tillegget 08.10, som FR-413)
- Rådata skrives til data/raa/ og står aldri i en sporet fil (AD-6, regel 10
  og 16)
- Merket under kursen sier «utbytte» når dataene har utbytte den dagen, ellers
  «justeringsdag»
- Aksjedetaljen viser utbyttet det siste året og utbytteavkastningen. Beløpet
  står i valutaen det betales i, og i NOK når det er en annen, omregnet med kurs
  og dato fra en kilde som avgjøres i planen
- Ingen nettkall i testene (AD-8)
- **Ville feilet hvis:** et kall ble tatt fra bonuskvoten, en justeringsdag uten
  utbytte i dataene sto som «utbytte», eller et beløp sto i en sporet fil

**Avhenger av:** 2.3b for kallene som er igjen, og 2.6 og 8.14 for merket.
```

**Kallene.** Rådets forslag til rekkefølge for kallene som er igjen: nye forsøk
(2.3b), så utbytte, så måling (FR-413). Med 15 aksjer er det 5 kall igjen etter
en henting (20 minus én per aksje), mens en runde med utbytte koster 15. Runden
må da deles over minst tre kvelder, eller tas på en dag uten henting, slik
FR-413 kan bruke alle 20 (`prd.md:1088`). Med 17 eller 18 aksjer og indeksen er
det ingen kall igjen om kvelden (`prd.md:1092–1093`). Spørsmål 21.

**FR-414 og 2.14.** Om eks.datoer ført for hånd fortsatt trengs når utbyttet
kommer fra EODHD, avgjøres etter prøven i kveld (spørsmål 19). `/api/div` gir
utbytte som er betalt. Om det også gir kommende eks.datoer, står ikke i repoet.

Historikken (Marian 13.10 kl. 12:19): gratisnivået gir utbyttet ett år bakover. Kursgrafen (8.14) viser utbyttet med beløp der EODHD har det, ellers «justeringsdag», og aksjesiden viser hva aksjen har betalt det siste året. Om utbytte eldre enn ett år tas vare på når det faller ut av vinduet, så historikken blir lengre etter hvert, avgjøres i planen for 2.15, fordi kursserien byttes ut ved hver henting (AD-5). Signalhistorikken står i 2.7, og når den kommer, avgjøres med rekkefølgen.

#### N2 — KI-teksten forklarer med tall hva som har skjedd

**Hva Marian vil.** KI-teksten forklarer med tall hva som har skjedd: signalet,
utbyttet og hvordan aksjen har gått mot hovedindeksen. Den gir ikke råd og spår
ikke (NFR-06, FR-603). «Se nærmere» (8.4) viser hva brukeren kan sjekke selv.
Grunnlaget i 10.1 får utbyttet fra N1, og hovedindeksen når 2.8 er bygget.

**Det står i veien.** 10.1 ble rettet 05.10 etter beslutningen 04.10: grunnlaget
«gir bare fortegnet for hver av de tre sjekkene, styrken og retningen», og «En
test krever at det ikke finnes desimaltall i grunnlaget». «Ville feilet hvis»
sier: «grunnlaget hadde en prosent eller et forholdstall. Da sendes mer enn våre
egne resultater, mot beslutningen 04.10» (`epics.md:2205–2214`). Kontrollpunktet
fra før sier også at et rått datapunkt fra EODHD til en tredjepart ikke er
godkjent av EODHD (`epics.md:2201–2203`). Et utbyttebeløp er en rå verdi fra
EODHD, og endringen mot hovedindeksen er en prosent. N2 krever derfor at
beslutningen 04.10 tas opp igjen. Spørsmål 23.

**Forslag, hvis beslutningen endres:** et tillegg i 10.1 med det som kan sendes
(for eksempel om aksjen har betalt utbytte det siste året, og om den gikk bedre
eller dårligere enn hovedindeksen, uten beløp), og et kontrollpunkt i 10.2 om at
tallene i teksten finnes i grunnlaget (FR-603). Avhenger av 2.15 for utbyttet og
2.8 for hovedindeksen.

**8.4.** «Se nærmere» står rett under kursgrafen, med «Børsen, bransjen eller
selskapet?», «Står det noe i børsmeldingene?» og «Er en slik dag vanlig for
aksjen?» (`epics.md:2837–2841`). Svar 5 legger «hva du kan sjekke selv» dit. Det
krever ingen endring i 8.4 utenom tekstene fra tavla.

#### N3 — Alle 13 bransjene nå

**Hva Marian vil.** Alle 13 bransjene fra tavla «Bransjer» og ordlista tas inn
nå. De 8 som de 15 hører til, er de samme som i `src/kursdata.py`. De 5 nye
brukes når egne aksjer kan velges (2.11 og 2.12), og symbolene kommer med 8.0d og
8.6.

**I dag.** `Aksje` har feltet `sektor` (`kursdata.py:33`), og de 15 fordeler seg
på 8: Energi, Finans, Industri, Materialer, Shipping, Telekom, Sjømat og Konsum
(`kursdata.py:42–55`). PRD-en sier «Universet dekker minst åtte sektorer»
(`prd.md:184`). Ordlista sier: «De 11 hos Euronext (ICB), med sjømat og shipping
for seg, som Euronexts indekser OBSFX og OBSHX. Nye: Forbruk, Teknologi, Helse,
Eiendom og Kraft.» (`designregler.md` §4). Navnene på de 8 står ikke i ordlista,
så at de er de samme som i koden, er Marians ord og ikke slått opp på tavla.

**Forslag.**
- `designregler.md` §4: de 13 navnene skrives inn, når rådet gir dem fra tavla.
- Koden: de 13 står som én konstant ved `AKSJEUNIVERS`, og en test krever at
  hver aksje har en sektor fra den. De 15 endres ikke.
- **Ordet.** Koden og PRD-en sier «sektor», ordlista og tavla «bransje». Ett av
  dem velges, som en del av punkt 8. Spørsmål 24.
- 2.11 og 2.12 får et kontrollpunkt om at en aksje som velges, får en av de 13.
  8.0d og 8.6 får symbolene.

## 5. Fra README-prøven

*Tom til prøven er gjort.* Funnene føres her før forslaget godkjennes, med
hvilken story eller hvilket punkt over de hører til.

*Rettet 2026-10-13, Marians beslutning kl. 11:34:* funnene fra prøven blir små rettelser og venter ikke på godkjenningen. Første prøve er i kveld 13.10.

## 6. Hva som må endres, hvis forslaget godtas

| Dokument | Endring |
|---|---|
| `prd.md` | FR-701 (tabellen), FR-703 (første avsnitt) og FR-704 (tabellen), med «Her sto» (punkt 4.4). Memloggen: en decision-linje nederst i `.memlog.md`, direkte og ikke med skriptet (regel 5) |
| `epics.md` | 8.0c: kontrollpunktene fra punkt 4.1, 4.4 og 4.6, eller ny 8.0e. 8.0d: rekkefølgen av delene, og eventuelt «Neste». Ny 8.19 hvis «Neste» blir egen story. 8.9: tekstene fra tavla. 8.10 delt i 8.10 og 8.10b. 8.15: sortering innenfor hver del. 2.7: «ikke kjørt» blir «ikke vurdert». Raden for NFR-06 med en datert linje. Kravlista under 4.6, dekningstabellen, FR-linjene for Epic 5 og 10, og de daterte linjene i punkt 4.8. Prioriteringen med en datert linje etter valget i punkt 4.7 |
| `designregler.md` | §4: rettelsene i punkt 4.3, med «Her sto» (innledningen, linje 10). Rekkefølgen av delene på sidene skrives i planen for 8.0d, ikke nå |
| `sprint-status.yaml` | 8.0d som `backlog` (mangler i dag). Nye linjer for 8.10b, og for 8.0e og 8.19 hvis de kommer. `last_updated` |
| Spinen | Ingen endring funnet. Den binder FR-604 og FR-605 med nummer (`ARCHITECTURE-SPINE.md:16, 178, 190, 210`), og ingen av dem får nytt innhold |
| `README.md` | Ingen, utenom lenken til dette forslaget, som står fra før (regel 19). Statuslinja rettes når rekkefølgen er valgt, hvis den sier noe om «Neste» som endres |
| Tester | De tre testene i punkt 4.5, og testen for ordene ordlista har valgt bort (punkt 4.1). Ingen tester endres nå |

*Lagt til 2026-10-13, etter svarene og punkt 4.9:*

| Dokument | Endring |
|---|---|
| `prd.md` | FR-407 rettes: merket under kursen sier «utbytte» når dataene fra EODHD har utbytte den dagen, ellers «justeringsdag» (svar 6). Ny FR-415, utbytte fra kilden (N1). FR-414 avgjøres etter prøven (spørsmål 19). «Sektor» eller «bransje» i §3 etter spørsmål 24. Beslutningen 04.10 om grunnlaget i §4.6, hvis spørsmål 23 endrer den |
| `epics.md` | Ny 2.15 (N1), ny 8.0e (svar 12), ny 8.19 (svar 13) og 8.10b. Kontrollpunkt i 2.11 og 2.12 om de 13 bransjene (N3). Tillegg i 10.1 og 10.2 etter spørsmål 23. Dekningstabellen for FR-415 |
| `designregler.md` | §4: de 13 bransjene (N3), merket under kursen (svar 6), fet skrift og prikket strek i tekstfargen i stedet for gul strek (svar 7), «T +1» i oversikten og navnet og ordet på aksjesiden (svar 8), og egen del for egne aksjer (svar 11) |
| `sprint-status.yaml` | `2-15`, `8-0e`, `8-10b` og `8-19` som `backlog` |

## 7. Spørsmål til Marian

1. **Når.** Rådet anbefaler at den samlede endringen tas før 8.0c planlegges.
   Skal den det, eller planlegges 8.0c som den står, og dette tas etterpå?
   *Svar 13.10:* Marians beslutning kl. 11:34: forslaget godkjennes uten å vente på README-prøven, så 8.0c kan planlegges denne uka. Bare rekkefølgen (spørsmål 14 og 15) venter til etter prøven.
2. **Lengden på hjelpen.** Hvor mange setninger kan en tekst bak «?» ha (punkt
   4.1)?
   *Svar 13.10:* høyst 3 setninger, med unntakene som står («Grensene» og «Hvorfor retningen oftere er positiv»).
3. **Hjelpebryteren.** Skal «Vis hjelp» vente på knapperaden i 8.3, eller komme
   før, et annet sted på siden (punkt 4.1)?
   *Svar 13.10:* vent på 8.3.
4. **Tekster som mangler i utdraget.** Kan rådet gi setningene med «Sluttkursen …»
   ordrett, innledningen under overskriften, og det tredje punktet i «Slik leser
   du tabellen» (punkt 4.2 og 4.6)?
   *Svar 13.10:* rådet gir tekstene i neste instruksjon.
   Tekstene fra tavla (rådet 13.10), med rettet ordlyd der den trengs:
   - Innledningen under overskriften (Main): «OSE Signal er et regelbasert signal for aksjer på Oslo Børs: 3 faste sjekker måler sluttkurs og volum mot aksjens egen historikk. Hos disse 4 slo minst 2 av 3 ut. Det viser hvor du kan se nærmere, ikke hva du bør kjøpe eller selge.» Rettet: «måler kurs og volum», og tallet telles fra radene. Under står «3 av 3» og «Bare Equinor fikk utslag på alle 3 sjekkene.», med navnene fra radene.
   - Første punkt i «Slik leser du tabellen» (Main), «Signalstyrke 0–3»: «T, B og I er trend, bevegelse og interesse, og hver gir +1, 0 eller -1. Til høyre står hvor mange som slo ut, fra 0 av 3 til 3 av 3. Klikk på T, B eller I i en rad for å se hva sjekken målte.» Kan tas når T, B og I står i radene (8.0e). Siste setning venter til klikket finnes.
   - Trend (Main): «Sluttkursen mot snittet av de 50 siste børsdagene. Slår ut når avstanden er mer enn 2 %.» blir «Kursen, justert for utbytte, mot snittet av de 50 siste børsdagene. Slår ut når avstanden er mer enn 2 %.» Fire setninger begynner med «Sluttkursen lå»: «… mer enn 2 % over snittet av 50 børsdager.», «… mer enn 2 % under snittet av 50 børsdager.», «… innenfor ±2 % av snittet av 50 børsdager.» og «… X % over snittet av 50 børsdager (grense 2 %).». De begynner i stedet med «Kursen lå».
   - Trend (Aksje): «Tirsdagens sluttkurs mot snittet av 50 børsdager» blir «Tirsdagens kurs, justert for utbytte, mot snittet av 50 børsdager».
5. **«Hva du kan sjekke selv» og det grå feltet.** Hvilken story hører de til?
   Ingen av dem står i `epics.md` (punkt 4.2).
   *Svar 13.10:* «hva du kan sjekke selv» er 8.4, og det grå feltet tas i 8.0d.
6. **Merket ved kursen.** FR-407 og 8.14 sier «justeringsdag», ikke «utbytte».
   Skal merket fortsatt være bokstaven U (punkt 4.3)?
   *Svar 13.10:* merket står under kursen. Det sier «utbytte» når dataene fra EODHD har utbytte den dagen (N1, punkt 4.9), ellers «justeringsdag», og FR-407 rettes etter det.
7. **Det viktigste på siden.** Gult betyr 3 av 3 (§3). Hvordan merkes det
   viktigste uten gult (punkt 4.3)?
   *Svar 13.10:* fet skrift, og prikket strek i tekstfargen for tall som er sjekket.
8. **Sjekkene.** «T +1» som i ordlista, eller «+1 positiv» som i 8.0c (punkt
   4.3)? Svaret gjelder også T, B og I i oversikten (punkt 4.6).
   *Svar 13.10:* «T +1» i oversikten, navnet og ordet på aksjesiden.
9. **Bransjene.** Ordlista har 13 bransjer, mens koden har 8 sektorer og PRD-en
   krever minst åtte. Skal de 13 inn, og i så fall i hvilken story (8.6?), eller
   følger ordlista sektorene (punkt 4.3)?
   *Svar 13.10:* alle 13 bransjene nå (N3, punkt 4.9).
10. **Hullene fra 12.10.** Rett på main, én commit per sak, eller i 8.0c (punkt
    4.5)?
    *Svar 13.10:* rett på main, én commit per sak.
11. **Egne aksjer.** Egen del «Dine egne aksjer», som tavla viser, eller i
    tabellen sammen med de andre, som ordlista sier (punkt 4.6)?
    *Svar 13.10:* egen del, som Marian valgte 12.10 kl. 22:03, og ordlista rettes.
12. **T, B og I, delt tabell, overskrift og «Slik leser du tabellen».** I 8.0c,
    som rådet foreslår, eller i en ny 8.0e etter 8.0c (punkt 4.6)?
    *Svar 13.10:* ny 8.0e etter 8.0c.
13. **«Neste» i stripa.** Ny story 8.19, eller et unntak i 8.0d (punkt 4.6)?
    *Svar 13.10:* ny 8.19.
14. **Rekkefølgen.** A, B eller C (punkt 4.7)?
    *Svar 13.10:* etter README-prøven.
15. **8.3 og brukertesten.** Skal linja «Bygges etter brukertesten i 8.1» i 8.3
    stå? Den avgjør om B er mulig (punkt 4.7).
    *Svar 13.10:* etter README-prøven.
16. **10.6 og hovedindeksen.** 10.6 står før 2.8 og 2.9 i dag, men trenger dem.
    Skal den flyttes etter 2.9, som i alle tre alternativene (punkt 4.7)?
    *Svar 13.10:* som forslaget.
17. **Epic 10.** 10.2 oppfyller FR-603, og 10.3 FR-601 og FR-602? (punkt 4.8)
    *Svar 13.10:* som forslaget.
18. **Snittet i kursgrafen.** Heltrukket, som ordlista sier, med hjelpeteksten
    rettet i 8.0d? I dag er det stiplet (punkt 4.3).
    *Svar 13.10:* som forslaget.
19. **FR-414 og 2.14.** Trengs eks.datoer ført for hånd når utbyttet kommer fra
    EODHD (N1, punkt 4.9)? Avgjøres etter prøven i kveld.
20. **Valutakursen.** Hvilken kilde gir kursen og datoen når et utbytte i en annen
    valuta vises i NOK (N1)?
21. **Kallene som er igjen.** Nye forsøk, så utbytte, så måling, som rådet
    foreslår? En runde med utbytte koster 15 kall og det er 5 igjen etter en
    henting: deles den over tre kvelder, eller tas den på en dag uten henting (N1)?
22. **Gratisnivået for `/api/div`.** Det står ikke i repoet, og `/api/calendar`
    svarte 403 på gratisnivået. Skal det prøves med ett kall, etter avtale
    (regel 6), før 2.15 planlegges (N1)?
23. **Beslutningen 04.10.** Grunnlaget i 10.1 har bare fortegn, styrke og
    retning, uten desimaltall. Skal det få mer, og i så fall hva, så KI-teksten
    kan forklare med tall (N2)?
24. **Sektor eller bransje.** Koden og PRD-en sier «sektor», ordlista og tavla
    «bransje». Hvilket ord gjelder (N3)?

## 8. Overlevering

**Omfang: middels.** Ingen nye epics og ingen endring i hentingen, basen eller
signalet. Ny ordlyd i tre krav, kontrollpunkter i fem storyer, opptil tre nye små
storyer (8.0e, 8.10b og 8.19), rettelser i ordlista og en ny rekkefølge.

*Lagt til 2026-10-13:* med punkt 4.9 kommer 2.15 og FR-415 til, og et tillegg i 10.1 og 10.2 hvis beslutningen 04.10 endres. Omfanget er fortsatt middels, men N1 og N2 berører kvoten og grunnlaget til KI.

**Før godkjenning:**

1. README-prøven 13.–16.10, og funnene i punkt 5
2. Rådet leser forslaget og gir tekstene i spørsmål 4
3. Marian svarer på spørsmålene i punkt 7

*Rettet 2026-10-13, Marians beslutning kl. 11:34:* forslaget godkjennes uten å vente på prøven, og Marian har svart på spørsmål 1–18 13.10. Det som står igjen før svarene føres inn i `prd.md` og `epics.md`: tekstene fra rådet (svar 4) og spørsmål 19–24. Rekkefølgen (spørsmål 14 og 15) avgjøres etter prøven, og prøven i kveld 13.10 kan gi små rettelser i punkt 5.

**Hvis Marian sier ja:**

1. `prd.md` med memloggen, i én commit
2. `epics.md` med `sprint-status.yaml`, i én commit
3. `designregler.md` §4, i én commit
4. Testene i punkt 4.5, én commit per sak, hvis de tas rett på main
5. Status `final` her, og en datert linje i samlelista om hvor hvert punkt ble
   tatt

**Suksesskriterier:**

- PRD-en, malene og hjelpen bruker samme ord for signalstyrke, trend og retning
- Ingen tekst fra tavla kommer inn i appen uten å være kontrollert mot koden
- Ordlista i `designregler.md` §4 strider ikke mot §1–3 eller mot noe krav
- Rekkefølgen bryter ingen «Avhenger av»-linje
- Kravlista og dekningstabellen i `epics.md` har samme FR-er og titler som
  `prd.md`
