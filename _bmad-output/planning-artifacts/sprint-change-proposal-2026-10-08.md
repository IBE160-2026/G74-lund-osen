---
title: "Endringsforslag 08.10: femten idéer inn i v1"
status: final
created: 2026-10-08
updated: 2026-10-08T08:09
---

# Endringsforslag 08.10: femten idéer inn i v1

Laget med `bmad-correct-course` i modusen Batch, etter instruksjonen kl. 07:32 i
`docs/ai-prompts/2026-10-08.md`. Bygd opp som
[`sprint-change-proposal-2026-09-28.md`](sprint-change-proposal-2026-09-28.md).

**Godkjent av Marian 08.10 kl. 08:04**, med endringene i instruksjonen kl. 08:06
i `docs/ai-prompts/2026-10-08.md`. De er ført inn her, og forslaget er deretter
ført inn i `prd.md`, `epics.md`, `sprint-status.yaml`, spinen og README-en, som
i punkt 6. `designregler.md` venter til 8.16.
*Skrevet 07:51, bevart:* «**Dette er et forslag.** Ingenting i `prd.md`,
`epics.md`, `sprint-status.yaml`, spinen eller `designregler.md` er endret.
Ingenting endres før rådet har lest forslaget og Marian har sagt ja (regel 2 og
9).»

## 1. Hva som utløste forslaget

**Beslutningen.** Marian bestemte 08.10 kl. 07:15–07:29 at femten idéer skal inn
i v1, som «Fast i v1» og ikke «Hvis vi rekker». Tretten er rader fra v1.1 i
`prd.md` §8, og to er fra designforslaget, som ligger i designtavla og ikke i
repoet (`designregler.md` §1). Kl. 07:29 bestemte hun i tillegg at de 15 kan
byttes helt ut, så lista kan ha opptil 18 aksjer valgt fritt.

| Rad | Idé | Hvor den står i dag |
|---:|---|---|
| 1 | Sektorvisning (børsometeret) | §8, «Sektorvisning» |
| 2 | Sjekk 2 og 3 synlige i grafen | §8 |
| 3 | Signaldager i grafen | §8 |
| 4 | Omvisning på alle sidene («Vis meg rundt») | §8 |
| 5 | Innstillinger øverst | §8 |
| 6 | Egne aksjelister | §8 |
| 7 | Flere ferdige lister og filter på signalet | §8 |
| 8 | Merk det som er nytt siden forrige henting | §8 |
| 9 | Lær noe nytt | §8 |
| 10 | Egne aksjer («Følg en aksje») | §8 |
| 11 | Utbyttehistorikk, vist i grafen | §8, «Utbyttehistorikk i aksjedetaljen» |
| 12 | Kommende eks.dato, vist i grafen | §8, «Kommende eks.dato i oversikten» |
| 13 | Måling av omsetning med kall til overs, som egen kommando | §8 |
| 14 | Sortering ved klikk på Sluttkurs, Endring og Signalstyrke i kolonneraden | Designforslaget |
| 15 | Periodevalg likt overalt, også i kursgrafen | Designforslaget, `designregler.md` §2, og «Flere valgbare tidsperioder» under «Hvis vi rekker» i §2 |

**Typen endring.** Nye krav fra produkteier. Ingen av radene er en feil i det
som er bygget.

**Navnene.** Rad 11 heter «Utbyttehistorikk i aksjedetaljen» i §8, og rad 12
heter «Kommende eks.dato i oversikten». Instruksjonen flytter begge til grafen.
Forslaget følger instruksjonen. Rad 1 kalles «børsometeret» bare i
`designregler.md` §3 og i instruksjonene, ikke i §8.

## 2. Virkninger

### Epics

Ingen ny epic. Tilbakemeldingen fra faglærer 06.10 ber om at antall epics ikke
vokser ([`tilbakemelding-product-brief.md`](tilbakemelding-product-brief.md)).

| Epic | Virkning |
|---|---|
| **Epic 2** | Tre nye storyer: 2.11 og 2.12 for lista (rad 6, 7 og 10), og 2.13 for målingskommandoen (rad 13). 2.3, som bygges nå, får ett kontrollpunkt til. 2.3b får færre kall å bruke |
| **Epic 3** | 3.4 (demoen) må kunne vise alt som kommer inn i v1, også lista og målingen, med oppdiktede tall (punkt 4.4) |
| **Epic 8** | Tolv nye storyer, 8.6–8.17. Epic 8 blir den største epicen, med 20 storyer |
| **Epic 10** | 10.1 og 10.6 får ett kontrollpunkt hver, om KI og lista som kan byttes (punkt 4.5) |
| Epic 4, 9 | Ingen virkning |
| Epic 5, 6, 7 | Ute av v1 fra 28.09 (plan B). Rad 8 og rad 12 avhang av Epic 6 og 7, se punkt 4.2 |

### Andre dokumenter

Punkt 6 har lista over hva som må endres hvis forslaget godtas.

## 3. Anbefalt vei

**Direkte justering:** nye storyer i Epic 2 og Epic 8, nye FR-er og tillegg til
FR-er som finnes. Ingenting rulles tilbake. Omfanget blir større, og det er det
Marian har bestemt. Det er ikke foreslått å kutte noe.

- **Innsats:** stor. 15 nye storyer, mot 32 som står igjen i v1 i dag (punkt 5).
- **Risiko:** middels til høy. Rad 6 og 10 endrer `AD-21`, kvoten, basen og
  vurderingene til en aksje som tas ut. Resten leser data som finnes.
- **Tid:** etter farten de siste ni dagene rekker vi ikke alt før demoen (punkt
  5). Rekkefølgen i punkt 5 setter det som ikke kan vente, først.

## 4. Forslagene i detalj

### 4.1 Krav og storyer per rad

FR-numrene er de neste ledige i hver del: §4.1 har FR-101–105, §4.2 har
FR-201–205 og §4.4 har FR-401–411. Storyene i Epic 2 fortsetter etter 2.10, og
storyene i Epic 8 etter 8.5.

#### Rad 1 — Børsometeret

**Krav: ny FR-106 — Børsometeret.** Markedsoversikten viser endringen per sektor
for lista som er aktiv, for perioden som er valgt (FR-201, tillegget for rad 15).
En sektor med én aksje vises som aksjen og merkes «1 aksje». En aksje med 3 av 3
på siste børsdag har gul ramme med hvit kant og merket «3 av 3»
(`designregler.md` §3). Ingen nye kall, ingen ny tabell. Sektoren står i
`aksje`.

```
### Story 8.6: Børsometeret

Som **bruker**, vil jeg se hvilke sektorer som trakk opp og ned, så jeg ser om
dagen gjaldt hele børsen eller noen bransjer.

**Oppfyller:** FR-106 · **Begrenses av:** FR-101, FR-105, FR-412, `AD-10`,
`AD-21`, NFR-06, NFR-08

**Kontroll — hva testen ser etter:**
- Én verdi per sektor i lista som er aktiv, regnet som snittet av endringen i
  FR-101 for aksjene i sektoren
- En sektor med én aksje merkes «1 aksje»
- Antallet sektorer og aksjer telles fra lista og prøves med en kortere liste
  enn 15 (føringen 30.09 under AD-21)
- Gult bare ved 3 av 3 på siste børsdag (`designregler.md` §3)
- Ingen nye kall og ingen ny tabell
- **Ville feilet hvis:** en sektor med én aksje så ut som et snitt av flere, eller
  antallet sektorer var fast

**Avhenger av:** 2.9b for søylene den står ved, og 8.17 for periodene. **Én økt:** ja.
```

#### Rad 2 — Sjekk 2 og 3 synlige i grafen

**Krav: tillegg til FR-202.** FR-202 sier i dag: «Volatilitetsbånd og volumsøyler
tegnes ikke i v1.» Tillegget må ha en Rettet-linje som sier at setningen ikke
lenger gjelder. Volumsøyler under kursgrafen, med en strek for medianvolumet og
en for grensen sjekk 3 slår ut ved. Medianen er regnet over samme vindu som i
sjekk 3 (`VOLUM_VINDU`, 20 dager), og grensen er `VOLUMFAKTOR` ganger medianen.
For sjekk 2 tegnes et bånd rundt forrige dags `adjusted_close` med standardavviket
fra sjekk 2 (`VOLATILITET_VINDU`, 20 dager). Tallene hentes fra `Parametre`, som
i hjelpen.

```
### Story 8.7: Sjekk 2 og 3 i kursgrafen

Som **bruker**, vil jeg se volumet og bevegelsen i grafen, så jeg ser hvorfor
sjekk 2 og 3 slo ut, slik MA50-linjen viser sjekk 1.

**Oppfyller:** FR-202 (tillegget) · **Begrenses av:** FR-201, FR-706, `AD-1`,
`AD-13`, NFR-08

**Kontroll — hva testen ser etter:**
- Volumsøylene står under kursgrafen, i samme SVG (`graf.py`)
- Streken for medianen og streken for grensen regnes med samme funksjon og
  samme vindu som sjekk 3. En test bytter vinduet i `Parametre` og ser at
  streken følger med
- Båndet for sjekk 2 bruker standardavviket fra sjekk 2, på `adjusted_close`
  (FR-201)
- Den siste dagen i grafen gir samme utslag som sjekkene i aksjedetaljen
- Mangler volumet eller medianen er 0, tegnes ikke streken, og grafen sier det
  (NFR-08)
- **Ville feilet hvis:** streken var en median over et annet vindu enn sjekk 3.
  Da forklarer grafen en annen regel enn den som ble brukt

**Avhenger av:** ingen åpne. **Én økt:** ja.
```

#### Rad 3 — Signaldager i grafen

**Krav: ny FR-206 — Signaldager i kursgrafen.** Kursgrafen markerer dagene der
den lagrede vurderingen hadde styrke på terskelen eller over (`TERSKEL`).
Markeringen leses fra `vurdering`, og signalet regnes aldri på nytt (AD-7). Det
finnes vurderinger fra 02.10, så grafen sier fra hvilken dato markeringene
finnes. En dag med grunn eller uten rad markeres ikke som signal, og tilstandene
i FR-409 blandes ikke.

```
### Story 8.8: Signaldager i kursgrafen

Som **bruker**, vil jeg se hvilke dager aksjen skilte seg ut, så jeg ser hvordan
signalet har oppført seg over tid.

**Oppfyller:** FR-206 · **Begrenses av:** FR-408, FR-409, `AD-7`, `AD-20`, NFR-06

**Kontroll — hva testen ser etter:**
- Markeringene leses med lesemetoden for en periode fra 2.7
- Grafen sier hvilken dato markeringene starter, og før den datoen er det ingen
  markeringer
- En dag med grunn, en dag uten rad og en dag som ikke er børsdag ser ulike ut,
  eller markeres ikke, og ser aldri ut som styrke 0
- **Ville feilet hvis:** markeringene ble regnet av kursene. Da viser grafen
  dagens parametre, ikke hva løsningen sa

**Avhenger av:** 2.7. **Én økt:** ja.
```

#### Rad 4 — Omvisning på alle sidene

**Krav: ny FR-109 — Hjelpen på sidene.** Det finnes ingen FR for hjelpen i dag:
8.0b oppfyller raden «Hjelp bak et spørsmålstegn». FR-109 samler hjelpen,
omvisningen og «Lær noe nytt» (rad 9). Omvisningen viser siden steg for steg,
med fast tekst vi har skrevet og sjekket, uten KI. Tall i teksten hentes fra
`Parametre`.

```
### Story 8.9: «Vis meg rundt»

Som **bruker som er ny**, vil jeg bli vist rundt på siden, så jeg vet hva hver
del er før jeg leser tallene.

**Oppfyller:** FR-109 · **Begrenses av:** FR-701, FR-703, FR-704, NFR-05, NFR-06

**Kontroll — hva testen ser etter:**
- En knapp «Vis meg rundt» på hver side som finnes
- Teksten ligger i samme tekstfil som hjelpen fra 8.0b
- En test sjekker at hvert steg peker på noe som finnes på siden
- Tall i teksten kommer fra `Parametre`, og en test krever det
- Ingen KI og ingen nettkall
- **Ville feilet hvis:** et steg pekte på noe siden ikke har, for eksempel
  børsometeret før 8.6 er bygget

**Avhenger av:** 8.0b, og bygges etter sidene den viser. **Én økt:** ja.
```

#### Rad 5 — Innstillinger øverst

**Krav: ny FR-110 — Innstillinger.** En knapp «Innstillinger» i knapperaden på
alle sider, med «Vis hjelp» og «Vis KI-tekst». Valgene gjelder alle sidene og
lagres i basen, slik merkingen i Min liste (8.3) gjør. FR-601 står: bryteren ved
hver KI-tekst blir der, og begge styrer samme valg.

```
### Story 8.10: Innstillinger øverst

Som **bruker**, vil jeg slå hjelpen og KI-teksten av og på ett sted, så valget
gjelder alle sidene og huskes.

**Oppfyller:** FR-110 · **Begrenses av:** FR-601, `AD-3`, `AD-10`, `AD-16`

**Kontroll — hva testen ser etter:**
- Valgene ligger i en egen tabell, med ny migrasjon (`AD-16`). Webserveren er
  eneste skriver av tabellen, som for Min liste (føringen 30.09 under `AD-3`)
- Valgene overlever en omstart og gjelder maskinen. Ingen innlogging
- Bryteren ved KI-teksten og valget i Innstillinger viser alltid det samme
- Ingen API-kall
- **Ville feilet hvis:** bryteren ved KI-teksten og Innstillinger kunne vise hver
  sin verdi

**Avhenger av:** 8.3 for knapperaden, 8.0b for hjelpen og 10.3 for KI-teksten.
**Én økt:** ja.
```

#### Rad 6 og 10 — Egne aksjelister og egne aksjer

Marian kl. 07:29: de 15 kan byttes helt ut, og lista kan ha opptil 18 aksjer
valgt fritt. Raden «Egne aksjer» fra 02.10 kl. 19:01 hadde allerede samme tak,
men som «de 15 og opptil 3 egne». Nå er alle 18 frie.

**Krav: ny FR-412 — Lista over aksjer.** Lista har opptil 18 aksjer. De 15 i §3 er
lista appen starter med. Aksjer kan legges til og tas ut, og lista kan byttes med
en ferdig liste (rad 7). Siden viser plassene som er brukt, for eksempel «16 av 18
aksjer». En endring tas i bruk ved neste henting, fordi webserveren aldri henter
(AD-10). En aksje som tas ut, beholder kursene og vurderingene sine, og merkes som
ute av lista fra den dagen. En aksje som omsettes mindre enn de 15 ble målt på,
merkes «Utenfor målingen» i grått overalt (Marians beslutning 02.10 i raden «Egne
aksjelister»).

**Krav: tillegg til FR-409.** En dag etter at aksjen ble tatt ut av lista, er
verken «ikke kjørt» eller «ikke børsdag». Den vises som «ikke i lista», så den
ikke telles som et hull i driften.

**Krav: tillegg til NFR-01.** 18 aksjer og hovedindeksen gir 19 kall og 1 kall
igjen. Kvotesjekken regner med antall aksjer i lista pluss indeksen, ikke med 15.

```
### Story 2.11: Lista leses fra basen

Som **gruppe**, vil vi at hentingen og sidene leser lista fra basen, så den kan
byttes uten at koden endres.

**Oppfyller:** FR-412, FR-409 (tillegget), NFR-01 (tillegget) · **Begrenses av:**
`AD-3`, `AD-7`, `AD-10`, `AD-16`, `AD-21` (endret, punkt 4.3)

**Kontroll — hva testen ser etter:**
- `aksje` får når aksjen kom inn i lista og når den gikk ut, med ny migrasjon
  (`AD-16`). De 15 som står i dag, får datoen for den første raden sin
- Hentekommandoen henter aksjene som er i lista, og kvotesjekken fra 2.3 regner
  med antallet pluss indeksen
- En aksje som er tatt ut, hentes ikke, og vurderingene og kursene står (`AD-7`,
  `AD-21`). Aksjedetaljen viser den fortsatt med historikken
- En dag etter at aksjen gikk ut, gir «ikke i lista» i `tilstand`, ikke «ikke
  kjørt»
- `AKSJEUNIVERS` er lista appen starter med, og testen som holder `aksje` lik
  `AKSJEUNIVERS`, byttes mot en som holder de 15 i første migrasjon like
- Grenen bruker bare testbaser og rører aldri `data/db/ose.db`
- **Ville feilet hvis:** en aksje som ble tatt ut, mistet vurderingene sine, eller
  dagene etter ble talt som dager vi ikke kjørte

**Avhenger av:** 2.3, og 2.8 for indekskallet. **Én økt:** avgjøres i planen.
```

```
### Story 2.12: Velge og bytte aksjer

Som **bruker**, vil jeg velge opptil 18 aksjer selv og bytte underveis, så appen
følger aksjene jeg bryr meg om.

**Oppfyller:** FR-412, rad 6 og 10 · **Begrenses av:** NFR-01, NFR-06, `AD-3`,
`AD-10`, `AD-13`, `AD-21`

**Kontroll — hva testen ser etter:**
- Siden viser «x av 18 aksjer», og en nittende avvises med en forklaring
- Webserveren skriver bare ønsket om endring, i en egen tabell. Hentekommandoen
  tar ønsket i bruk ved neste henting og er fortsatt eneste skriver av kurser og
  vurderinger (`AD-3`). Webserveren henter aldri (`AD-10`)
- En ticker som ikke gir rader ved hentingen, tas ikke inn, og utskriften sier det
- Står omsetningen målt fra før (2.13), vises den før brukeren velger. Er den
  under det de 15 ble målt på, merkes aksjen «Utenfor målingen» i grått overalt
- Ingen forslag fra KI om hvilke aksjer man bør følge (NFR-06)
- **Ville feilet hvis:** et valg i nettsiden startet et API-kall, eller lista
  kunne få 19 aksjer

**Avhenger av:** 2.11. **Én økt:** avgjøres i planen.
```

**Hva det betyr:**

| Gjelder | Virkning |
|---|---|
| **Kvotesjekken i 2.3** | 2.3 regner med 15 (svar 1 kl. 19:17 den 05.10, under 2.3 i `epics.md`). Forslaget er at 2.3, som bygges nå, tar antallet fra lista som parameter og testes med en kortere liste enn 15 (føringen 30.09 under `AD-21`). Da trenger 2.11 bare å gi den et annet tall. Med 2.8 blir det antallet pluss 1 |
| **2.3b** | Med 15 aksjer og indeksen er 4 kall igjen til nye forsøk (2.3b). Med 18 er det 1 |
| **Rad 13** | Målingen om kvelden lar 2 kall stå igjen (raden i §8 og NFR-01). Med 17 eller 18 aksjer og indeksen blir det ingen måling om kvelden. Med 15 aksjer og indeksen blir det 2 |
| **`AD-13`, grensene** | Grensene er låst mot de 15 og endres ikke. En aksje utenfor de 15 får signal med de samme grensene, og merket «Utenfor målingen» sier at signalet ikke er målt på slike aksjer. `AD-13` får en merknad om det |
| **`AD-7`, vurderingene** | En aksje som tas ut, beholder radene sine i `vurdering`. De kan verken slettes eller skrives om. Tas den inn igjen, begynner vurderingene på nytt fra den dagen. Dagene mellom kan ikke fylles inn |
| **Demoen (3.4)** | Demoen har ingen nøkkel og henter ikke. Den må likevel kunne vise lista som er byttet, «x av 18», en aksje som er tatt ut og «Utenfor målingen», med oppdiktede selskaper. Faglærer ber om at alle funksjoner i v1 kan vises i demoversjonen (tilbakemeldingen 06.10, forslag 2) |
| **`AD-10`** | Står. Et valg i nettsiden tas i bruk ved neste henting |
| **`AD-21`** | Må endres. Regelen om at `aksje` har de samme femten som `AKSJEUNIVERS` erstattes, se punkt 4.3 |

#### Rad 7 — Flere ferdige lister og filter på signalet

**Krav: tillegg til FR-412 og ny FR-108 — Filter på signalet.** Ferdige lister å
starte fra: de 15 i §3, «De 15 mest omsatte» når OBX er målt, og én liste per
sektor, som gruppen lager og måler (rad 6 og 13). Filteret på forsiden viser 3 av
3 med positiv eller negativ retning, innenfor lista som er aktiv. Det heter ikke
«topp» (NFR-06, FR-703). «De 15 mest omsatte» har ikke kravet om minst åtte
sektorer i §3.

```
### Story 8.11: Ferdige lister og filter på signalet

Som **bruker**, vil jeg starte fra en ferdig liste og se bare aksjene med 3 av 3,
så jeg slipper å sette lista sammen selv.

**Oppfyller:** FR-108, FR-412 (tillegget) · **Begrenses av:** FR-102, FR-703,
NFR-01, NFR-06

**Kontroll — hva testen ser etter:**
- De ferdige listene står ett sted i koden og har aldri mer enn 18 aksjer
- Filteret viser bare aksjer med 3 av 3 i den retningen som er valgt, og
  rekkefølgen er fortsatt FR-102
- Filteret virker bare innenfor lista som er aktiv. Ingen kall
- En liste vi ikke har målt, står ikke som ferdig liste
- **Ville feilet hvis:** filteret kunne leses som et råd, eller en ferdig liste
  hadde 19 aksjer

**Avhenger av:** 2.12, og 2.13 for listene som må måles. **Én økt:** ja.
```

#### Rad 8 — Merk det som er nytt siden forrige henting

*Rettet 2026-10-08 kl. 08:06, Marians beslutning:* rad 8 gjelder som Marian
bestemte 02.10 kl. 23:30. Beslutningen er gjengitt i instruksjonen kl. 08:06 og
står ikke i repoet fra før. FR-107 og 8.12 er skrevet om etter den. Teksten fra
07:51 står under, merket «Her sto».

**Krav: ny FR-107 — Endret signalstyrke siden forrige børsdag.** Når
signalstyrken har endret seg siden forrige lagrede børsdag, står et lite merke
under den, for eksempel «var 1 mandag», i markedsoversikten og i Min liste.
Merket regnes av lagrede vurderinger, og signalet regnes aldri på nytt (AD-7).
Det vises fra 05.10, den første børsdagen med en lagret børsdag før seg. Merket
skjules når «Sammenlign med» er på. Det har ingen pil, fordi pilene står for
retning (FR-103). Mangler den forrige raden, eller har den en grunn, står det
ikke noe merke.

```
### Story 8.12: Endret signalstyrke siden forrige børsdag

Som **bruker**, vil jeg se når signalstyrken har endret seg siden forrige
børsdag, så jeg ser med en gang hva som er nytt.

**Oppfyller:** FR-107 · **Begrenses av:** FR-103, FR-408, FR-409, `AD-7`, `AD-20`

**Kontroll — hva testen ser etter:**
- Merket står under signalstyrken i oversikten og i Min liste, for eksempel
  «var 1 mandag», og bare når styrken er en annen enn forrige lagrede børsdag
- Ukedagen er forrige børsdag, regnet i Europe/Oslo (`AD-20`)
- Merket regnes av to lagrede vurderinger, dagens og forrige børsdags, og vises
  fra 05.10
- En forrige dag med grunn, uten rad eller som ikke var børsdag, gir ikke noe
  merke
- Merket har ingen pil, og skjules når «Sammenlign med» er på
- **Ville feilet hvis:** forrige dags styrke ble regnet av kursene, eller merket
  hadde en pil som kunne leses som retning

**Avhenger av:** 2.7 for lesingen av en periode, og 8.3 for Min liste. **Én økt:** ja.
```

*Her sto 07:51:*

Raden i §8 gjaldt meldinger og avhang av meldingslageret i story 6.1. Epic 6 er
ute av v1. **Forslaget leser raden om vurderingene:** det som er nytt, er det
som har endret seg siden forrige lagrede børsdag. Marian bør bekrefte den
lesningen (punkt 7).

**Krav: ny FR-107 — Nytt siden forrige henting.** En aksje som skiller seg ut i
dag, men ikke gjorde det forrige børsdag, eller som har fått en annen retning,
merkes «Ny». Det sammenlignes bare med lagrede vurderinger, og signalet regnes
aldri på nytt (AD-7). Første dag med en forrige vurdering er 05.10. Mangler den
forrige raden, eller har den en grunn, merkes ingenting, og siden sier hvorfor.

```
### Story 8.12: Det som er nytt siden forrige henting

Som **bruker**, vil jeg se hva som har endret seg siden i går, så jeg ser med en
gang hva som er nytt.

**Oppfyller:** FR-107 · **Begrenses av:** FR-408, FR-409, `AD-7`, `AD-20`

**Kontroll — hva testen ser etter:**
- «Ny» settes bare ut fra to lagrede vurderinger: dagens og forrige børsdags
- En forrige dag med grunn, uten rad eller som ikke var børsdag, gir ingen
  merking, og siden sier hvorfor
- En aksje som kom inn i lista i dag, merkes ikke som ny på grunn av signalet
- **Ville feilet hvis:** forrige dags signal ble regnet av kursene

**Avhenger av:** 2.7 for lesingen av en periode. **Én økt:** ja.
```

#### Rad 9 — Lær noe nytt

**Krav: FR-109 (over).** En liten boks i markedsoversikten med ett kort tips per
dag, fra en fast liste. KI skriver utkast til lista, og vi kontrollerer og retter
hvert tips før det tas inn. Ingen KI og ingen nettkall når siden vises.

```
### Story 8.13: Lær noe nytt

Som **bruker**, vil jeg lære ett nytt begrep om dagen, så jeg forstår mer av det
appen viser.

**Oppfyller:** FR-109 · **Begrenses av:** NFR-05, NFR-06

**Kontroll — hva testen ser etter:**
- Tipsene står i en fast liste i repoet, og hvert tips er merket med hvem som
  kontrollerte det og når
- Dagens tips velges ut fra datoen, eller ut fra dagens tall når et tips passer.
  Valget er en regel i koden og testes med faste datoer
- Tall i teksten kommer fra `Parametre`
- Ingen KI og ingen nettkall når siden vises
- **Ville feilet hvis:** et tips kom på skjermen uten at noen av oss hadde
  kontrollert det, eller kunne leses som et råd

**Avhenger av:** 8.0b. **Én økt:** ja.
```

#### Rad 11 — Utbyttehistorikk, vist i grafen

Dagene finnes i kursserien: 2.6 finner dem etter FR-407, med avviket mellom
endringen i `close` og i `adjusted_close`. Metoden ser justeringer, ikke
utbytter, og en splitt gir samme utslag (`begrunnelser.md` §11). Raden i §8 sier
at grensesnittet bare kan bruke ordet *utbytte* hvis en kilde sier det. Forslaget
bruker derfor «justeringsdag» i grafen og i teksten, og ikke «utbytte».

**Krav: tillegg til FR-407.** Kursgrafen markerer justeringsdagene det siste
året, og aksjedetaljen viser hvor mange det var og datoen for den siste.
Vinduet er ett år, så et selskap som betaler én gang i året, kan i perioder stå
med null. Historikken sier ingenting om neste justering (NFR-06).

```
### Story 8.14: Justeringsdager i kursgrafen

Som **bruker**, vil jeg se dagene kursen ble justert det siste året, så jeg ser
hvor ofte det skjer og når det sist skjedde.

**Oppfyller:** FR-407 (tillegget) · **Begrenses av:** FR-201, `AD-5`, `AD-19`,
NFR-06, NFR-08

**Kontroll — hva testen ser etter:**
- Dagene er de samme som 2.6 finner, regnet av kursserien alene
- Antallet og den siste datoen står i aksjedetaljen
- Ordet «utbytte» står ikke ved dagene. En test krever det
- Teksten sier ikke noe om neste justering
- **Ville feilet hvis:** grensesnittet kalte en justering for utbytte, eller
  dagene ble lest fra en annen kilde enn kursserien

**Avhenger av:** 2.6. **Én økt:** ja.
```

**Merk:** FR-407 heter «Merking av utbyttedager», og 2.6 heter «Utbyttedager
merkes». Navnene står i dag. Om de skal endres, er et spørsmål til 2.6 (punkt 7).

#### Rad 12 — Kommende eks.dato, vist i grafen

**Ingen story ennå.** Marian avgjør raden etter at hun har lest dette.

*Rettet 2026-10-08 kl. 08:06, Marians beslutning:* ja, nå. To storyer, 2.14 og
8.18, med det tabellen under sier om vilkår, hvor ofte, lagring og merking.
Vilkårene for hvert selskap leses og føres i `docs/kilder-og-rettigheter.md`
før datoen tas inn.

**Krav: ny FR-414 — Eks.datoer ført for hånd.** Kommende eks.datoer føres inn
for hånd fra selskapenes egne investorsider, med en kommando, og lagres i basen,
aldri i en sporet fil (regel 16). Hver dato har datoen den ble sjekket og hvor den
ble lest. Et selskap får ingen dato før vilkårene for nettstedet er lest og ført
i `docs/kilder-og-rettigheter.md`. Sidene leses av en av oss og hentes aldri av
programmet. Lista sjekkes minst én gang i uka, og dagen før en eks.dato.

**Krav: ny FR-207 — Kommende eks.dato i kursgrafen.** Kursgrafen viser neste
eks.dato som er ført inn, med datoen den ble sjekket. Er den sjekket for mer enn
7 dager siden, vises den i grått med «sjekket <dato>, kan være endret». En dato
som har passert uten at kursserien viser en justering, merkes «ikke bekreftet».
Ingen dato vises uten at den er sjekket (NFR-08). I demoen er datoene oppdiktet
og merket «Eksempeltall» (FR-411).

```
### Story 2.14: Eks.datoer føres inn for hånd

Som **gruppe**, vil vi føre inn kommende eks.datoer fra selskapenes egne sider,
så appen kan vise dem uten en kilde vi ikke har.

**Oppfyller:** FR-414 · **Begrenses av:** NFR-08, `AD-3`, `AD-6`, `AD-10`,
`AD-16`, regel 16

**Kontroll — hva testen ser etter:**
- En egen tabell, med ny migrasjon (`AD-16`): symbol, eks.dato, datoen den ble
  sjekket og hvor den ble lest
- Kommandoen tar inn én dato for ett symbol, og nekter et symbol der vilkårene
  for nettstedet ikke er ført i `docs/kilder-og-rettigheter.md`
- Kommandoen gjør ingen nettkall, og webserveren skriver ikke tabellen
- Ingen eks.dato står i en sporet fil (regel 16)
- En ny sjekk av samme dato oppdaterer datoen den ble sjekket, og en flyttet dato
  erstatter den gamle
- **Ville feilet hvis:** programmet hentet en side fra et selskap, eller en dato
  kunne føres inn uten dato for sjekken

**Avhenger av:** 2.3. Vilkårene leses før første dato. **Én økt:** ja.
```

```
### Story 8.18: Kommende eks.dato i kursgrafen

Som **bruker**, vil jeg se neste eks.dato i kursgrafen, så jeg vet det før jeg
handler, og ser hvor gammel opplysningen er.

**Oppfyller:** FR-207 · **Begrenses av:** FR-201, FR-407, FR-411, NFR-06, NFR-08

**Kontroll — hva testen ser etter:**
- Neste eks.dato står i grafen med datoen den ble sjekket
- Sjekket for mer enn 7 dager siden: grått og «sjekket <dato>, kan være endret».
  En test med faste datoer prøver grensen
- En passert dato uten justering i kursserien (2.6) merkes «ikke bekreftet»
- Uten dato står det ingenting, og det ser ikke ut som en feil (FR-303)
- I demoen er datoene oppdiktet og merket «Eksempeltall»
- **Ville feilet hvis:** en dato som ikke er sjekket på over 7 dager, så like
  sikker ut som en som ble sjekket i dag

**Avhenger av:** 2.14, og 2.6 for «ikke bekreftet». **Én økt:** ja.
```

**Hvorfor kilden mangler:**

- Kursserien kan ikke gi datoen. Metoden bak FR-407 finner dagen først når den
  har skjedd (`begrunnelser.md` §11, forbehold 2, og raden i §8).
- EODHDs kalender svarer 403 på gratisnivået, «Only EOD data allowed for free
  users» (`docs/kilder-og-rettigheter.md`).
- Euronext er ute. Epic 7 og finanskalenderen er ute av v1 fra 28.09 (plan B),
  og appen lenker ikke til Euronexts nettsteder (Marians beslutning 06.10 kl.
  20:42).

**Hva en liste vi fører for hånd fra selskapenes egne investorsider ville kreve:**

| Spørsmål | Hva det krever |
|---|---|
| **Vilkårene** | Hvert selskap har egne bruksvilkår på nettstedet sitt. De må leses for hvert selskap før datoen tas inn, og det leste føres i `docs/kilder-og-rettigheter.md`, slik vilkårene til EODHD og Euronext er ført. Sidene leses av en av oss og hentes aldri av programmet, som sammenligningen med Oslo Børs' side (`malinger.md` §6). Ingen vilkår for investorsidene står i `docs/kilder-og-rettigheter.md` i dag |
| **Hvem og hvor ofte** | Selskapene melder eks.dato i kvartalsrapporten, i innkallingen til generalforsamlingen eller i en egen melding. Datoen kan flyttes. Lista må derfor sjekkes minst én gang i uka, og dagen før en eks.dato. Med lista som kan byttes (rad 6 og 10), gjelder det opptil 18 selskaper, og et selskap som legges til, må sjekkes før datoen vises |
| **Hvor den lagres** | En eks.dato fra et selskap er en rå enkeltverdi fra en kilde, så den kan ikke stå i en sporet fil (regel 16). Den må føres inn i basen eller under `data/`, med en egen kommando eller et skjema, og aldri i koden |
| **Hvordan en gammel dato merkes** | Hver dato står med datoen den ble sjekket og hvor den ble lest. Er den sjekket for mer enn 7 dager siden, vises den i grått med «sjekket <dato>, kan være endret». En dato som har passert uten at kursserien viser en justering, merkes «ikke bekreftet». Ingen dato vises uten at den er sjekket (NFR-08) |
| **I demoen** | Oppdiktede datoer, merket «Eksempeltall» (FR-411) |

Sier Marian ja, blir det minst to storyer: én for lista og kommandoen som fører
den inn, og én for visningen i grafen.

#### Rad 13 — Måling av omsetning som egen kommando

**Krav: ny FR-413 — Måling av omsetning.** Som raden i §8 og NFR-01 sier, med
reglene fra 02.10 slik de står i raden og i tilleggene 02.10 under NFR-01. De
står ikke med klokkeslett i repoet. Kommandoen:

- kjøres for hånd, etter en vellykket henting, og aldri fra webserveren (AD-10)
- nekter hvis kveldens henting ikke har gått bra
- sier først hvor mange kall den bruker
- lar 2 kall stå igjen, med mindre brukeren selv ber om å bruke alle når dagen er
  ferdig, og da sier den først at ingen blir igjen
- bruker aldri bonuskvoten
- måler aksjene i OBX som ikke er i lista, først, og så resten
- måler hver aksje på nytt etter 3 måneder, og datoen står ved tallet
- kan bruke alle 20 kallene på en dag uten henting (tillegget 03.10 i raden)

Median omsetning regnes som i `malinger.md` §21: `volume × close` per
handelsdag, median over tre måneder (§3).

```
### Story 2.13: Kommandoen som måler omsetning

Som **gruppe**, vil vi måle omsetningen for nye aksjer med kallene som er til
overs, så lista kan vise den før noen velger en aksje.

**Oppfyller:** FR-413 · **Begrenses av:** NFR-01, `AD-2`, `AD-6`, `AD-10`,
`AD-16`

**Kontroll — hva testen ser etter:**
- Tallet og datoen lagres i en egen tabell, med ny migrasjon (`AD-16`). Rådata
  skrives til `data/raa/` (`AD-6`) og committes aldri (regel 10)
- Kommandoen nekter når dagens henting ikke er gjort eller har feilet, og bruker
  da 0 kall
- Den leser `/api/user` før første kall, sier hvor mange kall den vil bruke, og
  lar 2 stå igjen, med mindre alle er bedt om
- Den bruker aldri bonuskvoten: står `extraLimit` lavere etter første kall,
  stopper den
- OBX først, så resten, og en aksje målt de siste 3 månedene måles ikke på nytt
- Kommandoen er en del av hentekommandoen, som et eget valg, så Dockerfilen i
  3.1 fortsatt har to innganger. Planen avgjør navnet (`allow_abbrev=False`)
- **Ville feilet hvis:** målingen kunne startes fra nettsiden, eller tok et kall
  fra bonuskvoten

**Avhenger av:** 2.3 og 2.8. **Én økt:** ja.
```

#### Rad 14 — Sortering ved klikk

**Krav: tillegg til FR-102.** Standarden står: signalstyrke fallende, med
absolutt kursendring ved lik styrke. Et klikk på Sluttkurs, Endring eller
Signalstyrke i kolonneraden sorterer på kolonnen, og et nytt klikk snur
rekkefølgen. Endring sorteres på prosent. Rader uten verdi står sist i begge
retninger. Det er fortsatt fem kolonner (FR-101).

```
### Story 8.15: Sortering ved klikk i kolonneraden

Som **bruker**, vil jeg sortere tabellen på kursen, endringen eller signalet, så
jeg finner det jeg leter etter.

**Oppfyller:** FR-102 (tillegget) · **Begrenses av:** FR-101, FR-103, NFR-05

**Kontroll — hva testen ser etter:**
- Uten klikk er rekkefølgen FR-102
- Ett klikk sorterer stigende eller fallende på kolonnen, og et nytt klikk snur
- Endring sorteres på prosent, ikke på kroner (FR-101, tillegget 07.10)
- Rader uten verdi står sist i begge retninger
- Kolonneraden sier hvilken kolonne og retning som gjelder, også til
  skjermleseren
- **Ville feilet hvis:** en rad uten signal kom først når rekkefølgen ble snudd

**Avhenger av:** ingen åpne. Gjelder også Min liste når 8.3 er bygget.
**Én økt:** ja.
```

#### Rad 15 — Periodevalg likt overalt

**Krav: tillegg til FR-201 og FR-101.** Periodevalget i `designregler.md` §2
gjelder markedsoversikten, kursgrafen, børsometeret og Min liste. Knappene er
siste børsdag («I går», «I dag» eller ukedagen), 1 uke, 1 mnd, 3 mnd, 6 mnd, I år,
1 år og «Velg dag». Kursgrafen åpner med 6 mnd (FR-201). Startdagen følger én
regel, skrevet før den bygges, lik for alle periodene, og testet med faste
datoer rundt helger, helligdager og nyttår (NFR-08). Signalet for en dag vises
bare der vurderingen er lagret, ellers «– ikke vurdert», eller «– ikke børsdag»
(`designregler.md` §2). Kursene for en periode regnes av kursserien. Det
regnes aldri et signal for en tidligere dag.

```
### Story 8.16: Regelen for startdagen, og periodene i kursgrafen

Som **bruker**, vil jeg velge hvor langt tilbake kursgrafen går, med samme
knapper som ellers i appen.

**Oppfyller:** FR-201 (tillegget) · **Begrenses av:** FR-202, NFR-08, `AD-20`

**Kontroll — hva testen ser etter:**
- Én funksjon gir startdagen for hver periode, og regelen står skrevet i
  `designregler.md` §2 før koden
- Testene har faste datoer rundt helger, helligdager og nyttår
- Knappene står i rekkefølgen i `designregler.md` §2, og grafen åpner med 6 mnd
- 1 år viser bare det kursserien har, og grafen sier det når serien er kortere
- MA50-linjen finnes fra første punkt for 6 mnd og kortere (FR-406)
- **Ville feilet hvis:** to perioder regnet startdagen med hver sin regel

**Avhenger av:** ingen åpne. **Én økt:** ja.
```

```
### Story 8.17: Periodevalget i oversikten, Min liste og børsometeret

Som **bruker**, vil jeg se endringen over en uke eller en måned i oversikten, og
signalet for en dag jeg velger.

**Oppfyller:** FR-101 (tillegget), FR-106 · **Begrenses av:** FR-102, FR-409,
`AD-7`, NFR-08

**Kontroll — hva testen ser etter:**
- Startdagen kommer fra funksjonen i 8.16
- Endringen over en periode regnes av kursserien, på `adjusted_close`, som
  endringen for én dag
- «Velg dag» viser vurderingen som er lagret for dagen, eller «– ikke vurdert»,
  grunnen, eller «– ikke børsdag». Signalet regnes aldri på nytt (`AD-7`)
- Gult står ved 3 av 3 også når en annen dag eller periode vises
  (`designregler.md` §3)
- **Ville feilet hvis:** «Velg dag» for 01.10 viste et signal. Det finnes
  vurderinger fra 02.10

**Avhenger av:** 8.16, 8.3 for Min liste og 8.6 for børsometeret. **Én økt:**
avgjøres i planen.
```

### 4.2 Det som fortsatt gjelder, og hva som står i strid med det

| Det som gjelder | Står noe i strid? |
|---|---|
| **Aldri flere enn 20 kall i døgnet, og aldri bonuskvoten (NFR-01)** | **Ja, NFR-01 selv.** Tillegget 05.10 under NFR-01 og svar 1 under 2.3 sier at bonuskvoten brukes til å fullføre hovedhentingen når færre enn 15 kall er igjen. Det er da flere enn 20 kall i døgnet. Enten må tillegget 05.10 og kontrollpunktet i 2.3 endres, eller så gjelder regelen her med det unntaket. **Marian avgjør det** (punkt 7). Resten av forslaget bruker aldri bonusen |
| **Bare rad 6, 10 og 13 berører kallene** | Stemmer. Rad 7 bruker kallene bare gjennom målingen i rad 13, og rad 12 bruker ingen kall |
| **Signalet regnes aldri på nytt (AD-7)** | Stemmer. Rad 3, 8 og 15 leser lagrede vurderinger. De finnes fra 02.10, og det første paret av to børsdager er 02.10 og 05.10 |
| **Ingen lenker til Euronexts nettsteder** | Stemmer. Raden for rad 13 i §8 viser til euronext.com for hva OBX er. Lista over OBX føres inn for hånd og lenkes ikke. Rad 12 bruker selskapenes egne sider |
| **KI får bare våre egne resultater** | Rad 9 sier at KI skriver utkast til tipsene. Forslaget lar det stå, men utkastet lages av våre egne begreper og `Parametre`, uten data fra kildene, og hvert tips kontrolleres. 10.1 og 10.6 får et kontrollpunkt om at en aksje utenfor de 15 sendes med de samme utledede verdiene og merket «Utenfor målingen» |
| **Rad 8 og rad 12 avhang av Epic 6 og 7** | Ja. Rad 8 er lest om vurderingene i stedet (over). Rad 12 venter på Marian |
| **«Ingen utvidelse av omfanget» (prioriteringen 23.09 i `epics.md`)** | Ja. Prioriteringen sa at forbedringer ut over v1 tas først når v1 er kontrollert og virker, og innledningen til v1.1 i §8 sier det samme. Marians beslutning 08.10 endrer det. Prioriteringen bør få en datert linje |
| **Faglærer: oversikten og aksjedetaljen ferdige og stabile i demoversjonen før KI-laget bygges ut** | Står i tilbakemeldingen 06.10. Tolv av de nye storyene endrer de to sidene. Rekkefølgen i punkt 5 legger dem etter at den daglige KI-teksten er i gang, unntatt 2.3, 3.1–3.4, 8.0b og 8.0c |

*Rettet 2026-10-08 kl. 08:06, Marians beslutning:* regelen fra 05.10 står (svar 1
under 2.3 og tillegget 05.10 under NFR-01). Bonuskvoten brukes bare til å fullføre
kveldens henting, aldri til 2.3b, målingen i rad 13 eller noe annet. «Aldri
bonuskvoten» i instruksjonen kl. 07:32 var for kort sagt. Første rad i tabellen
over står slik den ble skrevet 07:51.

### 4.3 Spinen

| AD | Forslag |
|---|---|
| **`AD-21`** | Regelen «tabellen `aksje` har … de samme femten som `AKSJEUNIVERS`, i samme rekkefølge. En test holder dem like» erstattes. `aksje` har alle aksjene som har vært i lista, med når de kom inn og gikk ut. `AKSJEUNIVERS` er lista appen starter med. Triggerne, at en aksje med rader ikke kan slettes, og at symbolet aldri endres, står. Føringen 30.09 blir regel: koden teller aksjene og antar aldri at det er 15 |
| **`AD-3`** | En føring: hentekommandoen er eneste skriver av `aksje`. Webserveren skriver ønsket om endring i en egen tabell (2.12) og innstillingene (8.10), som Min liste. Målingen (2.13) skriver sin egen tabell |
| **`AD-10`** | En merknad: et valg i nettsiden tas i bruk ved neste henting. Målingskommandoen er en del av hentekommandoen og startes for hånd |
| **`AD-13`** | En merknad: grensene gjelder uendret for aksjer utenfor de 15, og «Utenfor målingen» sier at de ikke er målt på dem. Ingen ny måling |
| **`AD-16`** | Nye migrasjoner: lista i `aksje`, ønsket om endring, omsetningen og innstillingene. Numrene settes når storyene bygges, etter `0005` (`ki_logg`), `0006` (indeksen) og høy og lav i 2.10 |
| **`AD-7`** | Ingen endring. Tillegget i FR-409 («ikke i lista») kommer i `tilstand`, ikke i porten |

### 4.4 Demoen

3.4 er planlagt med 15 oppdiktede selskaper. For at alt i v1 kan vises i demoen
(tilbakemeldingen 06.10), trenger demobasen i tillegg minst én aksje som er tatt
ut, én merket «Utenfor målingen», noen målte omsetninger og vurderinger nok til
at signaldagene, «Ny» og «Velg dag» har noe å vise. Det er kontrollpunkter i 3.4,
ikke en ny story. Lista i demoen kan byttes, men det hentes aldri. 3.4b har
KI-tekstene.

### 4.5 Epic 10

- **10.1:** en aksje utenfor de 15 sendes med de samme utledede verdiene som de
  andre, og merket «Utenfor målingen».
- **10.6:** teksten om dagen gjelder lista som er aktiv, og tallet på aksjer
  telles.

## 5. Hvor mye som står igjen, og rekkefølgen

### Storyene i v1

Telt fra `sprint-status.yaml` 08.10 kl. 07:38, uten Epic 5, 6 og 7 (ute av v1),
9.5 (utgår 06.10) og 10.8 (kandidat til v1.1):

| | I dag | Etter forslaget |
|---|---:|---:|
| `backlog` | 32 | 47 |
| `review`, flettet | 7 | 7 |
| Storyer i `epics.md` | 72 | 87 |

De 32 er 2.3, 2.3b, 2.4, 2.6, 2.7, 2.8, 2.9, 2.9b, 2.10, 3.1–3.4, 3.4b, 4.0, 4.2,
4.3, 8.0b, 8.0c, 8.1–8.5, 9.2 og 10.1–10.7. Rad 12 kan gi minst to til.

*Rettet 2026-10-08 kl. 08:06:* rad 12 gir to storyer, 2.14 og 8.18. Det er 17 nye
storyer, ikke 15. Etter forslaget er det 49 i `backlog`, ikke 47, og 89 storyer i
`epics.md`, ikke 87. Anslaget over gjelder fortsatt: om lag 20 storyer før uke 45.

### Farten

Fra 29.09 til 07.10 ble 7 storyer flettet: 2.1, 2.1b, 8.0, 2.1c, 2.5, 2.2 og 2.2b
(git-loggen). Det er om lag 0,8 per dag. 2.3 ble ikke ferdig 07.10.

**Anslaget:** fra 08.10 til demoen i uke 45 (fra 02.11) er det 25 dager. Med samme
fart blir det om lag 20 storyer. Det er færre enn de 32 som står i dag, og om lag
27 færre enn de 47 etter forslaget. Anslaget er grovt: storyene er ulike store,
og noen av de nye er små (8.15, 8.13). Det er ikke regnet på hver story.

| Milepæl | Hva den trenger | Med forslaget |
|---|---|---|
| **README-prøven 13.–16.10** | 2.3 og 3.1–3.4. Datoene står i instruksjonen kl. 07:32. Jeg finner dem ikke i repoet | Ingen nye storyer før prøven. 3.4 får kontrollpunktene i punkt 4.4, så den blir større |
| **Uka med KI-drift** | KI-teksten hver dag fra rundt 26.10 (`epics.md`), og minst én ukes drift før demoen (10.4). Krever 4.0, 4.2, 4.3, 10.1 og 10.2 | Står, hvis de nye storyene kommer etter 10.2 |
| **Demoen, est. uke 45** | Alt i v1 skal kunne vises i demoen | Med farten over rekker vi ikke alle 47. Det som står sist i rekkefølgen under, er det som blir igjen |

### Forslag til rekkefølge

1. **2.3** bygges ferdig først, med kontrollpunktet om lista som parameter (punkt
   4.1, rad 6 og 10).
2. **3.1–3.4** før README-prøven 13.–16.10, med demoen i punkt 4.4.
3. **2.3b, 8.0b og 8.0c**, som besluttet 05.10 og 06.10.
4. **4.0, 4.2, 4.3, 10.1 og 10.2**, så KI-teksten lages hver dag fra rundt 26.10.
5. **De nye som bare leser det vi har, og er små:** 8.15 (sortering), 8.16
   (startdagen og kursgrafen), 8.7 (sjekk 2 og 3 i grafen).
6. **Det som trenger historikken:** 2.7, så 8.8 (signaldager) og 8.12 (nytt). 2.6,
   så 8.14 (justeringsdager).
7. **10.3, 10.6, 3.4b og 10.7**, KI-laget som står igjen.
8. **Indeksen og børsometeret:** 2.8, 2.9, 2.9b, så 8.6 (børsometeret) og 8.17
   (periodene i oversikten).
9. **8.3, så 8.10 (Innstillinger), 8.9 (omvisningen) og 8.13 (Lær noe nytt).**
   Omvisningen kommer sist av dem, fordi den skal peke på sidene som finnes.
10. **Lista:** 2.11, 2.12, 2.13 og 8.11. Den kommer sist fordi den endrer
    `AD-21`, kvoten og basen, og fordi en aksje som tas ut midt i driften, har
    vurderinger som ikke kan fylles inn igjen (`AD-7`). 2.13 kan tas tidligere,
    fordi den ikke endrer lista.
11. **8.1, 8.2, 8.4, 8.5, 2.10, 2.4 og 9.2** der de passer. 8.1 (brukertesten)
    bør komme før 8.2, og 8.2 før de nye sidene er låst.

Rekkefølgen er avhengighetene og risikoen, ikke et estimat.

*Rettet 2026-10-08 kl. 08:06, Marians beslutning:* 10.3 og 3.4b kommer rett etter
10.2, før de nye storyene, fordi KI-teksten må vises og være med i demoen for
suksessmålet «KI-forklaringen». Punkt 7 over har da bare 10.6 og 10.7. 8.1,
brukertesten for «Brukerutfall», får fast plass før uke 45 og før 8.2, og står
ikke lenger i punkt 11 «der de passer». 2.14 og 8.18 (rad 12) kommer etter 2.6.
Rekkefølgen tas opp igjen etter README-prøven, når farten er kjent.

## 6. Hva som må endres, hvis forslaget godtas

| Dokument | Endring |
|---|---|
| `prd.md` | §2: femten nye punkter under «Inne i v1», merket som de andre beslutningene, og «Flyttet til v1» under «Flere valgbare tidsperioder» i «Hvis vi rekker». §3 «Universet»: lista kan byttes (FR-412). §8: «Flyttet til v1 2026-10-08, Marians beslutning» på de tretten radene, rad 12 med «avgjøres etter endringsforslaget». Nye FR-106, FR-107, FR-108, FR-109, FR-110, FR-206, FR-412 og FR-413. Tillegg til FR-101, FR-102, FR-201, FR-202 (med Rettet-linje for «tegnes ikke i v1»), FR-407, FR-409 og NFR-01. Memloggen: en decision-linje |
| `epics.md` | Storyene 2.11–2.13 og 8.6–8.17. Kontrollpunktene i 2.3, 2.3b, 3.4, 10.1 og 10.6. Avhengighetsgrafen. Tallet 72 blir 87, med en Rettet-linje. FR-linjene under Epic 2 og Epic 8, FR Coverage Map og prioriteringen med en datert linje |
| `sprint-status.yaml` | Femten nye linjer som `backlog`, og `last_updated` |
| Spinen | `AD-21` endres. Føring under `AD-3`, merknader under `AD-10` og `AD-13`, og migrasjonene under `AD-16` (punkt 4.3) |
| `designregler.md` | §2: regelen for startdagen skrives inn før 8.16, og «I dag:» rettes når den er bygget |
| `README.md` | Når lista og målingskommandoen er bygget (regel 19) |

## 7. Det jeg er usikker på

1. **Bonuskvoten.** NFR-01 og 2.3 tillater i dag bonuskvoten for å fullføre
   hovedhentingen. Instruksjonen sier aldri bonuskvoten. Det må avgjøres før 2.3
   flettes (punkt 4.2).
   *Rettet 2026-10-08 kl. 08:06, Marians beslutning:* regelen fra 05.10 står.
   Bonuskvoten brukes bare til å fullføre kveldens henting, aldri til 2.3b,
   målingen i rad 13 eller noe annet.
2. **Rad 8.** Er det riktig å lese «det som er nytt» om vurderingene, nå som
   meldingene er ute?
   *Avgjort 2026-10-08 kl. 08:06:* nei. Rad 8 gjelder som Marian bestemte 02.10
   kl. 23:30: et merke under signalstyrken når den har endret seg (FR-107).
3. **«Egen».** Raden «Egne aksjer» merket aksjene utenom de 15 «Egen». Når hele
   lista kan byttes, er det uklart hva «Egen» skal bety. Forslaget bruker bare
   «Utenfor målingen» og «x av 18».
   *Avgjort 2026-10-08 kl. 08:06:* i planen for 2.12.
4. **Navnet på FR-407 og 2.6.** Begge sier «utbyttedager», mens rad 11 ikke kan
   bruke ordet. Det bør avgjøres i planen for 2.6.
   *Avgjort 2026-10-08 kl. 08:06:* i planen for 2.6.
5. **Hvem skriver `aksje`.** Forslaget lar hentekommandoen være eneste skriver,
   så valg i nettsiden tas i bruk ved neste henting. Vil man se valget med en
   gang, må webserveren skrive `aksje`, og det er en endring av `AD-3`.
6. **Farten.** Anslaget på 0,8 storyer per dag bygger på ni dager med Epic 2,
   som har mange kontrollpunkter og mutanter. Det kan være for lavt for de små
   storyene i Epic 8.
7. **README-prøven.** Datoene 13.–16.10 står i instruksjonen og ikke i repoet.
8. **Regelen fra 02.10.** Den står i raden «Måling av omsetning med kall til
   overs» i §8 og i tilleggene 02.10 under NFR-01. Tidspunktet 10:57 er fra en
   samtale og står ikke i repoet, så forslaget viser til de to.
9. **Beslutningen 02.10 kl. 23:30 og «Sammenlign med».** *Lagt til 2026-10-08
   kl. 08:06:* beslutningen om rad 8 står ikke i repoet. Den er ført inn slik
   instruksjonen kl. 08:06 gjengir den. «Sammenlign med» er heller ikke beskrevet
   i repoet. Det må beskrives før 8.12 bygges, ellers kan testen ikke prøve at
   merket skjules.

## 8. Overlevering

**Omfang: stort.** Femten nye storyer, åtte nye FR-er, en endring i `AD-21` og
en ny rekkefølge. Rådet leser forslaget, og Marian sier ja eller ber om
endringer.

**Hvis Marian sier ja:**

1. Punkt 1 i punkt 7 avgjøres først, fordi det gjelder 2.3, som bygges nå
   *(avgjort 08.10 kl. 08:06)*
2. `prd.md` med memloggen, i én commit
3. `epics.md` med `sprint-status.yaml`, i én commit
4. Spinen, i én commit
5. 2.3 bygges ferdig

**Suksesskriterier:**

- Ingen kjøring bruker flere kall enn NFR-01 tillater, med 18 aksjer og indeksen
- En aksje som tas ut, beholder alle vurderingene sine, og dagene etter vises som
  «ikke i lista»
- Ingen side viser et signal for en dag uten lagret vurdering
- Alt i v1 kan vises i demoen uten nøkkel
