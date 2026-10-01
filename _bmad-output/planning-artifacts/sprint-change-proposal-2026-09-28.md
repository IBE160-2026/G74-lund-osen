---
title: "Endringsforslag 28.09: databasen i bruk i Epic 2"
status: final
created: 2026-09-28
updated: 2026-10-01T23:43
---

# Endringsforslag 28.09: databasen i bruk i Epic 2

Laget med `bmad-correct-course` i modusen Batch, etter instruksjonen kl. 17:32 i
`docs/ai-prompts/2026-09-28.md`. **Godkjent av gruppen 28.09**, med endringene
i instruksjonen kl. 20:25 samme sted. De er ført inn her, og forslaget er deretter
ført inn i `epics.md`, `sprint-status.yaml` og spinen, som i punkt 6.
*Skrevet 17:35, bevart:* «Dette er et forslag. Ingenting i `epics.md`,
`sprint-status.yaml`, PRD-en eller spinen er endret, og ingenting endres før
gruppen har sagt ja (regel 2 og 9).»

Plan B er ført inn 28.09 (`733239e` til `023dabb`), og Epic 5B heter Epic 10.
Epic 10 er med i tidsplanen (punkt 4.6). *Her sto 17:35:* «Plan B (Epic 5B) er
ikke med. Den føres inn i kveld med egne blokker.»

## 1. Hva som utløste forslaget

**Problemet.** Faglærerne krever at databasen er i bruk. Fra `docs/innlevering.md`
§2, ordrett fra faglærer 21.09: «Alle tre nivåene innebærer database, så uten
database vil dette påvirke karakteren hardt.» I dag ligger basen ferdig, men
ubrukt:

- Ingen fil under `src/` åpner en base. Det finnes ingen `sqlite3.connect` i
  `src/`, og `migrer()`, `SqliteKurslager` og `SqliteVurderingslager` kalles
  bare fra testene (slått opp 28.09).
- `app.py` leser gjennom `lagring_fil.nyeste_leser()`, altså fra det nyeste
  øyeblikksbildet i `data/`.
- `fetch_prices.main()` kaller `kjoer(DATA_KATALOG, date.today(), …)` og skriver
  bare et øyeblikksbilde. `DATA_KATALOG` er `PROSJEKTROT / "data"`, og
  `nyeste_snapshot` leser bare den katalogen, ikke undermapper.
- Innledningen til Epic 2 (lagt til 25.09) sier det selv: ingen story har som
  kontrollpunkt at hentekommandoen skriver kursene til basen gjennom
  `Kurslager`, eller at webserveren leser dem derfra.

**Typen endring.** Ikke et nytt krav. Kravet står i FR-406 og FR-408, AD-4 og
AD-17, og i prioriteringen fra 27.09 («databasen i bruk i Epic 2, med skrivingen
først»). Det som mangler, er stories som gjør det til kontrollpunkter.

**Hvorfor det haster.** En vurdering kan ikke etterfylles (AD-7, AD-17). Hver
børsdag før hentekommandoen skriver til basen, er en dag som mangler for godt i
historikken som 2.7 skal vise, og som «Adopsjon» og «Fortsatt bruk» i PRD §7
måler.

## 2. Virkninger

### Epics

| Epic | Virkning |
|---|---|
| **Epic 2** | Én ny story (2.1b), ny rekkefølge, kontrollpunkter lagt til i 2.2, 2.3 og 2.5, og forutsetningen fra 2.5 flyttet til 2.1b. Ingen story får nytt nummer, og ingen strykes |
| **Epic 3** | Innholdet er det samme, men 3.1 og 3.2 får mindre å avgjøre. Stiene, åpningen av basen og migrasjonene er avgjort i Epic 2. 3.1 bare pakker |
| **Epic 4** | 4.3 flyttes til rett etter 2.1b, fordi den bruker samme åpning av basen og `0004`. 4.2 kan tas når som helst. *29.09: `ki_logg` blir `0005`, fordi `0004` er målingene i story 2.1c.* |
| **Epic 8** | 8.1 kan tas når 2.2 og 2.7 er ferdige, uten å vente på 2.4 og 2.6 |
| **Epic 10** | 10.1 i uke 40–41, og 10.2 og 10.3 i uke 42–43 (punkt 4.6). 10.3 leser KI-teksten med `ki_logg` mot `vurdering` (punkt 4.5) |
| Epic 5, 6, 7 | Ute av v1 fra 28.09 (plan B). Ingen virkning her |
| Epic 9 | Ingen virkning |

### Andre dokumenter

| Dokument | Hva som må rettes, hvis forslaget godtas |
|---|---|
| `epics.md` | Innledningen til Epic 2, den nye 2.1b, 2.2, 2.3, 2.5, avhengighetsgrafen, AD-lista for Epic 2, og merknaden i 3.1 om migrasjoner |
| `sprint-status.yaml` | En ny linje: `2-1b-basen-åpnes-ett-sted-og-hentingen-skriver-kursene-dit: backlog` |
| Spinen | Raden «Hvem kjører migrasjonene, og når» under Deferred blir avgjort. Mappetreet får `[2.1b]` ved `data/raa/` og `data/db/ose.db`. AD-16 får en linje om hvor `migrer()` skal kalles. *Rettet 28.09 kl. 20:25: her sto «Mappetreet får `[bygget i 2.1b]`». Ingenting er bygget før 2.1b er ferdig* |
| PRD-en | Ingen krav endres. Terskelen for «Drift» i §7 («migrasjoner er uttrykkelig ikke et eget steg») blir oppfylt i 2.1b, ikke i 3.1. Det kan føres som en merknad |
| `docs/innlevering.md` §2 | «Gjenstår» sier at 1.6–1.7 står igjen, men de er ferdige. Dette står alt i `deferred-work.md`. Rettes når 2.1b er ferdig, med den nye stien |
| `README.md` | Når webserveren leser fra basen (2.2), blir «Kom i gang» feil (regel 19, story 3.3) |

## 3. Anbefalt vei

**Direkte justering** i Epic 2: én ny story og nye kontrollpunkter i stories som
finnes. Ingenting må rulles tilbake. Omfanget i PRD-en står.

- **Innsats:** middels. 2.1b er én økt, og resten er kontrollpunkter i stories
  som alt er planlagt.
- **Risiko:** lav til middels. Det største spørsmålet er åpningen av basen i
  webserveren, fordi `migrer()` alltid tar skrivelås (punkt 4.4 under).
- **Tid:** de daglige kjøringene til basen kan begynne når 2.5 er ferdig. Da får
  historikken dager fra og med da, i stedet for fra etter Epic 3.

Rollback er vurdert og forkastet: ingenting i Epic 1 står i veien. MVP-kutt er
ikke nødvendig. Kuttlista i punkt 4.6 er for når tiden blir knapp.

## 4. Forslagene i detalj

### 4.1 Hvilke stories som tar basen i bruk

| Det som skal skje | Forslag | Nummer |
|---|---|---|
| Hentekommandoen skriver kursene gjennom `Kurslager` | **Egen story**, fordi den også avgjør stiene og åpningen av basen for begge inngangene | **2.1b** (ny) |
| Vurderingen skrives i samme kjøring | **Kontrollpunkter i 2.5**, som alt har kravet («Én kjøring skriver kurser **og** vurderinger») | 2.5 |
| Webserveren leser fra basen | **Kontrollpunkter i 2.2**, som alt forutsetter det («også når basen er tom», «hvordan webserveren åpner basen») | 2.2 |

**Nummeret.** `2.1b` følger BMAD-grammatikken: `STORY_RE` i `sprint_plan.py`
godtar `(\d+)\.(\d+[a-z]?)`, og nøkkelen blir `2-1b-…`. Det følger 1.5b, som også
var en ny story etter 1.5, ikke en del av den. Ingen eksisterende story får nytt
nummer.

**Hvorfor ikke 2.8.** 2.8 ville stått sist i sprint-statusen, men storyen er
den andre som bygges. 2.1b står der den bygges.

#### Story 2.1b: Basen åpnes ett sted, og hentingen skriver kursene dit *(ny)*

```
Som **gruppe**, vil vi at hentekommandoen skriver kursene til basen, så
databasen er i bruk fra første henting, og så vurderingen i 2.5 har noe å
regnes av.

**Oppfyller:** FR-406 · **Begrenses av:** `AD-4`, `AD-5`, `AD-6`, `AD-11`,
`AD-16`, `AD-21`

**Kontroll — hva testen ser etter:**
- Øyeblikksbildene skrives til `data/raa/`, og basen ligger i `data/db/ose.db`,
  som i mappetreet i spinen
- Én funksjon åpner basen: den lager mappa hvis den mangler, kobler til og
  kjører `migrer()`. Både hentekommandoen og webserveren (2.2) bruker den.
  Ingen egen kommando for migrasjonene (PRD §7, «Drift»)
- Hentekommandoen kaller `erstatt_serie` for hvert symbol som ble hentet, med
  samme `hentet` som øyeblikksbildet (AD-5, AD-20)
- Et symbol som feilet, rører ikke serien sin i basen (AD-15)
- Kjøringen virker når både `data/raa/` og `data/db/` mangler (3.2)
- Fire dagers opphold i serien er borte etter neste henting, uten ekstra kall
  (FR-403, se 4.6 om 2.4)
- Leseren av øyeblikksbildene ser i `data/raa/`, så markedsoversikten og
  aksjedetaljen viser de samme kursene før og etter flyttingen. Til 2.2 er
  ferdig, leser webserveren fortsatt øyeblikksbildene, og `nyeste_snapshot`
  ser i dag bare i `data/`
- Et øyeblikksbilde som alt finnes, kan skrives til basen uten API-kall, samme
  vei som etter en henting. Det skriver bare `kurs`, aldri `vurdering` (AD-7).
  Det gir en test med ekte data uten kall, og en reserve til demonstrasjonen
  (punkt D i `docs/innlevering.md`). AD-6 forbyr å lagre filene i basen, ikke å
  lese kursene ut av dem
- **Ville feilet hvis:** webserveren og hentekommandoen hadde hver sin
  åpning av basen. Da kan den ene migrere og den andre ikke, og AD-16 er brutt
  av den første som startet

**Forutsetning** *(flyttet fra 2.5)*: `SqliteKurslager` gjør avvisningen fra
`0003` om til `ValueError`, mens `MinneKurslager` godtar `EQNR.OL` (G10, G11).
Her avgjøres det om porten `Kurslager` skal sjekke symbolet.

**Spørsmål til planen:** `erstatt_serie` bytter ut hele serien (AD-5). Et
øyeblikksbilde som er eldre enn serien i basen, ville derfor skrevet en eldre
serie over en nyere. Planen avgjør om det avvises.

**Lokalt, utenfor git:** de eksisterende `kurser-raa-*.json` flyttes for hånd
fra `data/` til `data/raa/`. `data/` committes aldri (regel 10).

**Én økt:** ja.
```

#### Story 2.5: nye kontrollpunkter

```
OLD (forutsetningen):
**Forutsetning** *(fra kodegjennomgangen av Epic 1, 2026-09-27)*: `SqliteKurslager`
godtar ethvert symbol, … Blir skrivingen til basen en egen story, følger
forutsetningen dit.

NEW:
(forutsetningens første del står, med tillegget:) *Flyttet til 2.1b
2026-09-28 for `Kurslager`.* Det som gjelder `SqliteVurderingslager.skriv`, som
slipper ut `sqlite3`-feil (G11), står igjen her.

Nye kontrollpunkter:
- Datoen for vurderingen regnes én gang, fra samme øyeblikk som filnavnet og
  `hentet` (2.1). En kjøring som går over midnatt i Oslo, stopper og sier fra,
  i stedet for å få `ValueError` fra `skriv` midt i universet (`deferred-work.md`,
  fra spesifikasjonen for 1.6)
- Vurderingene leses tilbake gjennom `Vurderingslager.les` i samme test, fra en
  base på disk, ikke bare `:memory:`
```

Grunnen: `SqliteVurderingslager.skriv` leser klokka ved hvert kall
(`lagring_sqlite.py`), mens datoen er fast for kjøringen. Det er oppføringen i
`deferred-work.md`, og den hører til 2.5.

#### Story 2.2: nye kontrollpunkter

```
Nye kontrollpunkter:
- Markedsoversikten og aksjedetaljen leser kursene fra basen gjennom
  `SqliteKurslager`, ikke fra øyeblikksbildet
- Webserveren åpner basen med samme funksjon som hentekommandoen (2.1b)
- Én tilkobling per forespørsel, lukket når forespørselen er ferdig
  (forutsetningen om `check_same_thread`)
- Meldingen på den tomme siden sier ikke lenger «Ingen kursdata funnet i
  `data/`» (`deferred-work.md`), og «Kom i gang» i README rettes i samme commit
  (regel 19)

Spørsmål til planen:
- Kan oversikten hente de femten fra `aksje` sammen med nyeste kurs i én
  spørring? Det er en join appen faktisk bruker (punkt 4.5)
- Skal oversikten lese dagens vurdering fra `vurdering` i stedet for å regne
  signalet av kursene ved hver visning? Samme data og samme parametre gir
  samme svar, men det er to veier til samme tall
```

Grunnen: forutsetningen i 2.2 sier alt at det er her det avgjøres hvordan
webserveren åpner basen. Blir 2.2 mer enn én økt, deles den i 2.2 og 2.2b når
den planlegges, ikke nå.

#### Story 10.3: nytt kontrollpunkt *(lagt til 28.09 kl. 20:25)*

```
- KI-teksten leses med `ki_logg` mot `vurdering`, så teksten vises sammen med
  vurderingen den forklarer
```

### 4.2 Rekkefølgen i Epic 2

**Forslag:** 2.1 → **2.1b** → 2.5 → *(de daglige kjøringene begynner)* → 2.3 → 2.2
→ 2.7 → 2.4 → 2.6.

| # | Story | Hvorfor her |
|---|---|---|
| 1 | 2.1 | Liten, og alt som kommer etter, bygger på én dag og ett øyeblikk. Testen for `main()` legges i datakatalogen, som 2.1b flytter |
| 2 | 2.1b | Kursene i basen. Uten den har 2.5 ingenting å regne av |
| 3 | 2.5 | **Dette er storyen som gjør at hentingen kan kjøres hver børsdag mellom kl. 22:00 og midnatt og skrive til basen.** Fra da av blir hver dag et svar eller en grunn i `vurdering` |
| 4 | 2.3 | Vern for kvoten og for dagen (se under) |
| 5 | 2.2 | Webserveren leser basen. Det er da databasen synes i appen |
| 6 | 2.7 | Historikken, som bare er verdt noe når den har dager i seg |
| 7–8 | 2.4, 2.6 | Se kuttlista |

**Hva det krever av 2.1.** At filnavnet, `hentet` og datoen for vurderingen
kommer fra samme øyeblikk i Europe/Oslo. Det er kontrollpunktene som står.
Merk: i vinduet 22:00–24:00 er Oslo-datoen og UTC-datoen den samme både vinter
og sommer, så feilen i AD-20 slår ikke til i vinduet. 2.1 er likevel først,
fordi 2.5 trenger én dato å regne ut fra, og fordi et vindu er en vane og ikke
en garanti.

**Hva det krever av 2.3.** Et funn fra oppslaget: **en kjøring som kommer for
tidlig, koster mer enn 15 kall.** Den skriver `kurser-raa-<dagens dato>.json`,
og vernet fra 2.0 i `kjoer()` stopper da enhver ny kjøring samme dag («finnes
allerede … 0 kall brukt»). Kveldens riktige kjøring blir altså stoppet, og
dagen får en grunn («nyeste kurs var ikke fra dagen») i stedet for en
vurdering, og kan ikke etterfylles. **Forslaget er derfor at 2.3 nekter før kl.
22:00, og ikke bare advarer**, med en uttrykkelig overstyring for det tilfellet
at vi vet raden finnes. Punkt 23 overlot valget til planen for 2.3, og det er
fortsatt der det avgjøres. Dette er et argument for planen, ikke en avgjørelse.

**Mellom 2.5 og 2.3** kjører vi for hånd, bare på børsdager og bare mellom
22:00 og midnatt. 2.0 stopper en kjøring nummer to samme dag, men ikke en kjøring
på en lørdag eller en som kommer for tidlig. Derfor bør 2.3 komme rett etter.

### 4.3 Det Epic 2 må avgjøre, så Epic 3 bare pakker

| Spørsmål | Forslag | Hvor |
|---|---|---|
| **Mappene** | `data/raa/` for øyeblikksbildene og `data/db/ose.db` for basen, som i mappetreet i spinen. `DATA_KATALOG` beholdes som roten, og det kommer to konstanter under den | 2.1b |
| **Flytting lokalt** | `kurser-raa-*.json` flyttes for hånd fra `data/` til `data/raa/`. Målingsfilene (`signaltest-`, `volumsjekk-`, `nyhetstest-`, `gjentak-`, `kall21-`, `relevans-`) blir liggende. `data/` committes aldri | 2.1b, utenfor git |
| **Ett sted åpner basen og kjører migrasjonene** | Én funksjon, som begge inngangene kaller. Da oppfyller 3.1 «Migrasjoner kjøres **uten** et eget kommandosteg» uten å gjøre noe nytt | 2.1b (lages), 2.2 (webserveren) |
| **Mappene lages når volumene er tomme** | Funksjonen lager `data/db/`, og `kjoer()` lager `data/raa/` (den gjør `mkdir(parents=True, exist_ok=True)` alt). Testen kjører uten at noen av dem finnes | 2.1b |
| **Én tilkobling per forespørsel** | Åpnes ved forespørselen og lukkes etter | 2.2 |
| **Sti fra miljøet** | **Nei, ikke i v1.** Stiene er faste under `PROSJEKTROT`, og 3.1 monterer `ose-raa` og `ose-db` på `data/raa/` og `data/db/`. Testene peker stiene mot `tmp_path` med `monkeypatch`, som i dag. Trenger 3.1 likevel en variabel, er det en endring i 3.1 og ikke en ny beslutning | 2.1b |

Dette tar også to rader under Deferred i spinen: «Hvem kjører migrasjonene, og
når» blir avgjort. «Kjøremåte i containeren» (WSGI, flate importer) står igjen
til 3.1, fordi den gjelder pakkingen.

### 4.4 Webserveren og migrasjonene *(det største spørsmålet)*

`deferred-work.md`: «migrer() krever skrivetilgang også når basen er oppdatert,
fordi den starter med BEGIN IMMEDIATE.» Kjører webserveren `migrer()` ved hver
forespørsel, tar hver sidevisning en skrivelås. Da kan en visning mens
hentekommandoen skriver, gi «database is locked».

**Forslag:** webserveren kjører åpningen med `migrer()` én gang ved oppstart.
Hver forespørsel kobler seg deretter bare til, og adapterne sjekker selv at basen
står på siste versjon (`_krev_siste_versjon`). Testen der to migratorer
overlapper (`deferred-work.md`, utsatt til 3.1), flyttes til 2.1b, fordi det er
der to innganger får samme åpning.

### 4.5 Hvor godkjenningen av SQLite 22.09 synes

Godkjenningen (`innlevering.md` §2, AD-4) nevner fem ting: «strukturert lagring
over tid, relasjoner mellom data, joins, migrasjoner og logging av
KI-vurderinger».

| Punktet | I dag | Etter forslaget |
|---|---|---|
| **Lagring over tid** | `vurdering` finnes (`0002`, 1.6), men ingenting skriver dit utenom testene | Én rad per aksje per børsdag fra 2.5. Vises dag for dag i 2.7 |
| **Relasjoner mellom data** | `aksje` med triggere fra `kurs`, `kursserie` og `vurdering` (`0003`, AD-21), prøvd i `tests/test_aksje.py` | Holdes av basen ved hver ekte skriving fra 2.1b. `ki_logg` peker på `vurdering` i 4.3 (ER-diagrammet i spinen) |
| **Joins** | **Ingen.** Ingen `JOIN` i `src/` (slått opp 28.09) | Minst én join som appen faktisk bruker. Planen for 2.2 vurderer om oversikten kan hente de femten fra `aksje` sammen med nyeste kurs i én spørring, og 10.3 leser KI-teksten med `ki_logg` mot `vurdering`. En join mot `aksje` i 2.7 bare for navnet teller ikke, fordi siden alt vet hvilken aksje den viser. *Avgjort 28.09 kl. 20:25. Her sto:* «Se usikkerhetene. Forslaget er at lesingen for en periode i 2.7 er én spørring over `vurdering` og `aksje`, og at KI-teksten leses med `ki_logg` mot `vurdering` i 4.3» |
| **Migrasjoner** | `0001`–`0003`, løperen og `skjema_versjon`, prøvd i testene | Kjøres av appen selv fra 2.1b, ved oppstart av begge inngangene |
| **Logging av KI-vurderinger** | Ingenting. 4.2 og 4.3 er `backlog` | 4.2 (porten og minneutgaven) når som helst. 4.3 (`0004_ki_logg.sql` og adapteren) rett etter 2.1b, fordi den bruker samme åpning av basen. *29.09: `ki_logg` blir `0005`, fordi `0004` er målingene i story 2.1c.* |

**4.2 og 4.3 i rekkefølgen.** 4.2 har ingen avhengighet og kan tas mellom
stories i Epic 2. 4.3 kan tas når 2.1b er ferdig, og må være ferdig før
KI-teksten skal lages hver dag fra rundt 26.10.

Merk at prioriteringen fra 23.09 sa at 4.1 og 4.2 skulle tas parallelt med
Epic 1. Det skjedde ikke: begge står som `backlog` i `sprint-status.yaml`.

### 4.6 Kutt og grov rekkefølge

**Kan kuttes, i denne rekkefølgen**, etter prioriteringen fra 27.09:

1. **8.2**, fra «hvis tiden strekker til»
2. **2.6**, fra samme linje
3. **2.4**, som krymper av seg selv: hver henting erstatter hele året (AD-5), så
   et hull fylles ved neste henting uten ekstra kall. Kontrollpunktet om fire
   dagers opphold er lagt i 2.1b. 2.4 står, men kan lukkes med en henvisning dit
4. **2.7**, fra «det vi prøver å få til». Den kuttes sist av disse, fordi det er
   den som viser «lagring over tid» i appen

**Kan ikke kuttes:** 2.1, 2.1b, 2.5, 2.3, 2.2 og 3.1–3.3. Det er databasen i
bruk, og Dockerfile og README.

**Grov rekkefølge fram til 26.10** (fire uker):

| Uke | Datoer | Hva |
|---|---|---|
| 40 | 28.09–04.10 | 2.1, 2.1b, 2.1c, 2.5. **Første kjøring til basen så tidlig som mulig i uka.** Deretter 2.3. 4.2, og 4.3 rett etter den. 4.1 (papirarbeid) og 10.1 ved siden av |
| 41 | 05.10–11.10 | 2.2, 2.7. 4.1 og 10.1 ferdige. Punktet om EODHD og plan B avgjøres før 10.2 |
| 42 | 12.10–18.10 | 8.1 (brukertesten) tidlig i uka, med data fra uke 40 og 41 i historikken. 3.1, 3.2, 3.3. 10.2 |
| 43 | 19.10–25.10 | 10.2 og 10.3 ferdige. 2.4 og 2.6 hvis det er tid |
| 44 | fra 26.10 | KI-teksten lages hver dag (Epic 10) |

*Rettet 2026-09-29:* 2.1c (målingene) er tatt inn i uke 40, før 2.5, og 4.2 er flyttet fra uke 41 til uke 40, før 4.3, fordi 4.3 er adapteren for porten 4.2 lager. Her sto for uke 40: «2.1, 2.1b, 2.5. **Første kjøring til basen så tidlig som mulig i uka.** Deretter 2.3. 4.3 rett etter 2.1b. 4.1 (papirarbeid) og 10.1 ved siden av |» og for uke 41: «2.2, 2.7. 4.2. 4.1 og 10.1 ferdige. Punktet om EODHD og plan B avgjøres før 10.2 |».

*Rettet 28.09 kl. 20:25:* Epic 10 er tatt inn. 4.1 og 10.1 i uke 40–41 (10.1
sender ingenting), 4.2 i uke 41, 4.3 rett etter 2.1b, og 10.2 og 10.3 i uke
42–43. Punktet «Plan B for KI-laget: spørre EODHD eller ikke?» i
`docs/kilder-og-rettigheter.md` avgjøres før 10.2. Uke 43 er ikke lenger
reserve. Her sto for uke 40–44: «2.1, 2.1b, 2.5. … 4.1 (papirarbeid) ved siden
av», «2.2, 2.7. 4.2 ved siden av», «… 3.1, 3.2, 3.3. 4.3», «Reserve. 2.4 og 2.6
hvis det er tid. Plan B kommer i tillegg (ikke med her)» og «KI-teksten lages
hver dag».

*Lagt til 2026-10-01 (hovedindeksen OSEBX i v1, Marians beslutning):* 2.8, 2.9
og 2.9b kommer inn i uke 41, etter 4.2 og 4.3 i uke 40, så `ki_logg` blir `0005`
og indeksen `0006`. Ingen av dem står på lista «Kan ikke kuttes», og blir det
trangt, venter 2.9b først. Rekkefølgen i Epic 2 står i `epics.md`.

Det er ikke regnet på hvor lang tid storyene tar. Rekkefølgen er avhengighetene
og prioriteringen, ikke et estimat.

## 5. Det jeg er usikker på

1. **Joins.** Jeg fant ingen spørsmål i appen som krever en join mellom tabellene
   i dag. Navnet på aksjen står også i `AKSJEUNIVERS`, så en join mot `aksje` i
   2.7 kan bli en join for å ha en join. Den mest naturlige er `ki_logg` mot
   `vurdering`, men den kommer først med 4.3 og plan B. Det bør gruppen avgjøre,
   ikke jeg. *Avgjort 28.09 kl. 20:25:* se «Joins» i punkt 4.5.
2. **Om webserveren fortsatt skal regne signalet selv.** Markedsoversikten regner
   signalet av kursene ved hver visning. Etter 2.5 ligger dagens vurdering i
   basen. Samme data og samme parametre gir samme svar, men det er to veier til
   samme tall. Om oversikten skal lese `vurdering`, er ikke vurdert her.
   *Avgjort 28.09 kl. 20:25:* et spørsmål i planen for 2.2.
3. **Om AD-6 tillater at basen fylles fra et øyeblikksbilde.** «Filene går ikke
   inn i databasen» (AD-6) kan leses som et forbud mot å importere et
   øyeblikksbilde til `kurs`. En slik import ville kostet 0 kall og gitt en
   reserve til demonstrasjonen (punkt D i `innlevering.md`). Den er ikke foreslått.
   *Avgjort 28.09 kl. 20:25:* gruppen leser AD-6 slik at den forbyr å lagre
   filene i basen, ikke å lese kursene ut av dem. Importen er et kontrollpunkt i
   2.1b, og den skriver bare `kurs`.
4. **Om 2.2 blir én økt.** Lesingen fra basen, tilkoblingen per forespørsel og
   den tomme siden er tre ting. Det er grunnen til at en deling i 2.2b er nevnt.
5. **Webserverens lås.** Forslaget i punkt 4.4 bygger på at adapterne sjekker
   versjonen uten skrivelås. `_krev_siste_versjon` leser bare. Hvordan
   `versjon()` oppfører seg mens hentekommandoen skriver, er ikke prøvd.
6. **Den første daglige kjøringen.** Den kan tidligst gå kvelden 2.5 er
   ferdig. Hvor mange dager uke 40 da mister, avhenger av hvor fort 2.1, 2.1b og
   2.5 går.
7. **Tidsplanen** bygger på at demonstrasjonen er i uke 45, som er vår egen
   anslåtte dato (punkt 13, `innlevering.md` punkt D).

## 6. Overlevering

**Omfang: moderat.** Backloggen omorganiseres, og én story kommer til. Ingen
PRD-krav og ingen AD-er endres, bare Deferred-raden om migrasjonene og
merknadene over.

*Godkjent 28.09 kl. 20:25.* **Hvis gruppen sier ja:**

1. `epics.md`: endringene i punkt 4.1–4.3, i én commit
2. `sprint-status.yaml`: linja for 2.1b, i samme commit eller den neste
3. Spinen: Deferred-raden, mappetreet og AD-16, i én commit
4. Deretter bygges 2.1 med `bmad-build`

**Suksesskriterier:**

- Den første kjøringen etter 2.5 gir 15 rader i `vurdering` for dagen, med svar
  eller grunn
- Etter 2.2 viser webserveren det som ligger i basen, og en tom base gir den
  tomme siden
- 3.1 trenger ingen ny beslutning om stier eller migrasjoner
