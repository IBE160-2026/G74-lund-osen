---
title: "Leveranseliste — IBE160, gruppe G74"
status: aktiv
created: 2026-09-22
updated: 2026-10-06T18:36
---

# Leveranseliste — IBE160, gruppe G74

**Kvalitetssikringsdokumentasjonen — kontrollrapporter, mutanttester,
memlogger, refleksjonslogg — er del av de 70 prosentene, ikke bare de 30:
emnesiden legger «hvordan studentene har kvalitetssikret koden» under
prosjektkoden, ikke under rapporten (se «Eksamen» under).**

**Bygget 2026-09-22 på kilder, ikke på hukommelse.** Hvert punkt bærer sitatet
det hviler på, og hvor sitatet står. Punkter uten ordrett kilde står nederst,
under «Antatt, ikke bekreftet» — de er ikke fjernet, men de er ikke blandet inn
blant det som er belagt.

Lista er kort med vilje. Et punkt uten kilde er verdt mindre enn ingen punkter,
fordi det ser like troverdig ut som resten.

*Oppdatert 2026-09-23* etter at emnesiden ble lest i sin helhet og hjelpelærer
svarte på spørsmålene fra 22.09. **Om kildene:** sitatene fra emnesiden og fra
svaret er utdrag, gjengitt av Marian i økta 23.09. Verken emnesiden eller
e-posten er lagt i repoet, så de kan ikke kontrolleres herfra, og utdragene er
ikke rekonstruert til mer enn det som ble gjengitt. Legg inn fullteksten når
den finnes.

---

## Status 2026-10-05

**Virker nå:** hentingen av sluttkurser fra EODHD til SQLite-basen, med dagens
vurdering per aksje i samme kjøring, og markedsoversikten og aksjedetaljen, som
leser kursene og den lagrede vurderingen fra basen.

**Kommer:** børsdagskontrollen (2.3), så Docker og demoversjonen (3.1–3.4).
Demoversjonen er hovedveien for vurderingen etter svaret fra hjelpelæreren
05.10 (under). Deretter KI-laget (Epic 4 og 10).

**Ukjent:** datoene for prosjektinnlevering og demonstrasjon (punkt C og D).
Hver story og status står i [sprintstatusen](../_bmad-output/implementation-artifacts/sprint-status.yaml).

---

## Eksamen — fra emnesiden

**Kilde:** emnesiden for IBE160, lest i sin helhet 2026-09-23. Utdrag gjengitt
av Marian samme dag. Tekst i «» er ordrett, resten er referat.

### Mappeinnlevering

**Prosjektkode og funksjonalitet** — «Prosjektkode og funksjonalitet (70%)».
Gruppevis.

- «Studentene leverer en KI-generert applikasjon»
- «Dokumentasjon må vise hvordan KI ble brukt, og hvordan studentene har
  kvalitetssikret koden»

**Refleksjonsrapport** — «Refleksjonsrapport (30%)». Gruppevis.

- «Beskrivelse av utviklingsprosessen, utfordringer og løsninger»
- «Kritisk vurdering av hvordan KI påvirket sluttresultatet»
- «Argumentasjon for etiske og teknologiske implikasjoner»

### Arbeidskrav

Product brief i repoet, frist 20. september kl. 23:59 (referat, ikke sitat).
Fristen ble senere utsatt til 27.09. **Utsettelsen har ingen navngitt kilde i
repoet.** Det eneste stedet den står, er `docs/reflection-log.md`, oppføringen
fra 19.–20.09: «Ny innleveringsdato for BMAD-leveransen er satt til søndag
27.09.2026 (uke 39).» Loggen sier ikke hvem som satte den eller hvor den er
kunngjort. Se §7.

**Frist og vurdering** *(kilde: faglærer)*: Product Brief skal være ferdig
**søndag 27.09.2026**. Da vurderer faglærerne den som godkjent eller
ikke godkjent, med tilbakemelding. Den skal være på 1–2 sider. *Rettet
2026-09-24:* «Utsettelsen har ingen navngitt kilde» gjelder ikke lenger.
Fristen 27.09 er gitt av faglærer. *Rettet 2026-09-24:* klokkeslettet er
fjernet fra fristen her, i §4 og i §7, etter beskjed fra Marian. *Rettet
2026-09-24:* kilden for fristen og lengdekravet er faglærer.

### Hva emnesiden ikke sier

Emnesiden sier «tre deler», men lister to, og nevner at «delvurdering 3 gir
anledning til å demonstrere unike bidrag». Hva den tredje delen er, er ikke
oppgitt. Ført som **åpent punkt 21** i `prd.md`.

---

## 1. Kildekode og Dockerfile

**Dockerfile: sagt i samtale av faglærer, ikke bekreftet på emnesiden — gjøres
likevel.** Kildekoden er belagt på emnesiden («Studentene leverer en
KI-generert applikasjon»). Dockerfilen er det ikke. Hjelpelærer 23.09: «Det
står derimot ikke på emnesiden jeg har tilgjengelig at Dockerfile eller en
bestemt type database er et eksplisitt leveransekrav.» Arkitekturen er besluttet,
og sensor skal kunne kjøre løsningen, så den bygges uansett. Men den er ikke et
belagt krav.

> **Innleveringen er «kildekode og docker fil».**

**Kilde:** faglærer i IBE160, 21.09.2026. Ført i `docs/reflection-log.md`,
oppføringen «Faglærer om rammene: database, docker, stack og rapportens plass»
(21.09), punkt 2. *Rettet 2026-09-24: her sto «Fire avklaringer fra faglærer».*
Merk at bare frasen
«kildekode og docker fil» er ordrett; setningen rundt er loggens egen.

| | |
|---|---|
| **Status** | **Delvis** |
| **Ligger i** | `src/` (12 moduler og `migrasjoner/`), `tests/` (17 testfiler, 468 tester — telt 2026-09-26), `.github/workflows/`, `pyproject.toml`, `uv.lock`. *Rettet 2026-09-26:* her sto 10 moduler, 13 filer og 285 tester, telt 2026-09-24. *Rettet 2026-09-26, etter 1.5b (`ef1cca7`):* her sto 427 tester. *Rettet 2026-09-26, etter 2.0 (`4b65a3c`):* her sto 455 tester. *Telt 2026-10-05, på `3fac7cc`:* 17 moduler i `src/` og fire migrasjoner i `src/migrasjoner/`, 23 testfiler og 1148 tester |
| **Gjenstår** | **Dockerfile finnes ikke.** Kontrollert 21.09 og igjen 22.09: ingen treff på `Dockerfile` eller `docker-compose` noe sted i repoet. Beslutningen var punkt 18 i `prd.md`, som ble lukket 22.09 (AD-9 til AD-12), og selve Dockerfilen er story 3.1. *Rettet 2026-09-26:* her sto «Ført som åpent punkt 18 i `prd.md`». |

Arkitekturen for den er besluttet 22.09 og ligger i `ARCHITECTURE-SPINE.md`:
`AD-9` (imaget inneholder aldri data), `AD-10` (webserveren henter aldri),
`AD-11` (to volumer), `AD-12` (hemmeligheter fra miljøet). Selve filen er ikke
skrevet.

*Lagt til 2026-10-05:* hjelpelæreren anbefaler «en anbefalt hovedmåte å kjøre
prosjektet på» i README-en (svaret 05.10, under «Spørsmål sendt hjelpelærer
2026-10-04»). Dockerfilen er fortsatt ikke et belagt krav.

---

## 2. Database

**Sagt i samtale av faglærer, ikke bekreftet på emnesiden — gjøres likevel.**
Samme setning fra hjelpelærer 23.09 som under §1: verken Dockerfile «eller en
bestemt type database» står som eksplisitt leveransekrav på emnesiden.
Databasen bygges likevel. Behovet er begrunnet i kravene selv (FR-407, FR-408,
FR-604/605, se `begrunnelser.md` §9), og faglærerens advarsel om karakter står
uansett.

> Hvis du ikke har behov for en database, så er prosjektet ditt for enkelt, noe
> som vil gjenspeile karakter. Vi har tre nivå: Enkel, Medium, Vanskelig. Alle
> tre nivåene innebærer database, så uten database vil dette påvirke karakteren
> hardt.

**Kilde:** faglærer i IBE160, 21.09.2026. Ordrett i `docs/reflection-log.md` og
i `begrunnelser.md` §9.

| | |
|---|---|
| **Status** | **Delvis — oppdatert 2026-09-23** *Oppdatert 2026-10-03 (story 2.2b):* sidene leser kursene og vurderingene fra basen. |
| **Ligger i** | `src/migrering.py` (story 1.1), `src/lagring_sqlite.py` og `src/migrasjoner/0001_kurs.sql` (story 1.3). Beslutningen ligger i `ARCHITECTURE-SPINE.md` `AD-3` til `AD-7`, `AD-16`, `AD-18`, `AD-19` *Lagt til 2026-10-03 (story 2.2b):* også `0002_vurdering.sql` (1.6), `0003_aksje.sql` (1.9) og `0004_maalinger.sql` (2.1c), og `src/oversiktsdata.py` med `SqliteOversiktsleser`, som sidene leser gjennom (2.2b). |
| **Gjenstår** | Å koble lagringen til appen: ingen story har det som kontrollpunkt ennå, se innledningen til Epic 2 i `epics.md` (lagt til 25.09). 1.4a–1.5 er ferdige uten at appen leser fra basen. *Rettet 2026-09-26:* her sto «Å koble lagringen til appen (story 1.4–1.5)». Videre gjenstår vurderingslageret (1.6–1.7) og KI-loggen (4.3). *Skrevet 22.09, bevart:* «Hele lagringslaget. `kursdata.py` leser i dag en JSON-fil, og `app.py` leser den direkte utenom porten» *Rettet 2026-10-03 (story 2.2b):* lagringen er koblet til appen. Sidene leser kursene fra basen fra story 2.2, og dagens vurdering fra 2.2b. Vurderingslageret (1.6–1.7) er bygget. KI-loggen (4.3) gjenstår. |

**Valget er kontrollert med faglærerstaben 22.09** og godkjent av assisterende
hjelpelærer — ikke av emneansvarlig:

> Slik dere beskriver bruken, strukturert lagring over tid, relasjoner mellom
> data, joins, migrasjoner og logging av KI-vurderinger, bruker dere SQLite som
> en ordentlig database, ikke bare som enkel fillagring. […] Så ut fra det vi
> vet nå mener jeg dette er helt innenfor.

Svaret bærer to begrensninger som ikke skal skrives bort: det kom ikke fra
emneansvarlig, og det sier «ut fra det vi vet nå».

---

## 3. Refleksjonsrapport

> refleksjonsrapporten skal dere skrive ETTER dere har gjennomført prosjektet,
> og har ingenting med product brief å gjøre.

**Kilde:** faglærer i IBE160, 21.09.2026, ordrett i `docs/reflection-log.md`.

| | |
|---|---|
| **Status** | **Delvis — råmaterialet finnes, rapporten ikke** |
| **Ligger i** | `docs/reflection-log.md`, ført løpende siden 13.09. Arbeidsutkast i `_privat/refleksjonsrapport-utkast.md` (gitignorert) |
| **Gjenstår** | Selve rapporten. Den skal skrives **etter** at prosjektet er gjennomført, så den kan ikke ferdigstilles nå |

Sitatet sier *når* rapporten skrives, ikke hva den skal inneholde eller hvor
lang den skal være. Det er ikke funnet noen kilde på formkrav.
*Rettet 2026-09-24:* innholdet er gitt av emnesiden, sitert under «Eksamen»
øverst: beskrivelse av utviklingsprosessen, utfordringer og løsninger; kritisk
vurdering av hvordan KI påvirket sluttresultatet; og argumentasjon for etiske og
teknologiske implikasjoner. Det som er ukjent, er lengde, struktur og format.

---

## 4. Product Brief

> Jeg har sett gjennom briefen, og dette ser veldig bra ut. Dere har en tydelig
> ide, et fornuftig omfang og et godt skille mellom hva som løses med vanlig
> kode og hva KI faktisk skal brukes til.
>
> […] Formatet ser også helt fint ut. Det viktigste er innholdet og at
> strukturen er tydelig.

**Kilde:** faglærer i IBE160, 20.09.2026, ordrett i `docs/reflection-log.md`.

| | |
|---|---|
| **Status** | **Låst og klar for levering: tag `arbeidskrav-product-brief-v7`, commit `e62ea77`** |
| **Ligger i** | `_bmad-output/planning-artifacts/product-brief.md` |
| **Gjenstår** | Vurdering fra faglærerne etter fristen 27.09. **Lengdekrav: 1–2 sider** (arbeidskravet, kilde: faglærer) *Rettet 2026-10-06:* vurderingen fra faglærer kom 06.10 i egen fil, [`tilbakemelding-product-brief.md`](../_bmad-output/planning-artifacts/tilbakemelding-product-brief.md). Versjon 8 av briefen er story 9.6 i `epics.md`. |

Samme tilbakemelding er positiv til fordelingen mellom brief og PRD, inkludert
vår egen seksjon «Data og kilder» som ikke står i malen.

*Rettet 2026-09-24:* her sto at briefen var godkjent, og at tilbakemeldingen
«godkjenner» fordelingen. Tilbakemeldingen var svar på et spørsmål fra gruppen
(bekreftet av Marian 24.09). Den er positiv, men ikke en godkjenning av briefen
som leveranse.

*2026-09-24:* **briefen er endret etter tilbakemeldingen 20.09.** `git log` viser
minst 11 commits fra 21.09 til 24.09, blant annet at NewsWeb ikke er en avklart
kilde, at det ikke hentes før Euronext har svart, og plan B. Tilbakemeldingen
gjaldt versjonen faglærer så.

*Rettet 2026-09-24:* her sto «Formatkrav: ingen — sagt eksplisitt i tilbakemeldingen
20.09». Tilbakemeldingen sa at formatet så fint ut, ikke at det ikke fantes krav.
Arbeidskravet sier 1–2 sider. Versjon 2 hadde om lag 1470 ord og er kortet til
om lag 750 i versjon 3. Versjon 2 står ordrett i `product-brief-tillegg.md`.

*Rettet 2026-09-24:* versjon 3 lenket til `product-brief-tillegg.md`, som hadde versjon
2 i full lengde. Lenken og tillegget er fjernet i versjon 4, fordi briefen skal
stå alene på to sider. Versjon 2 ligger uendret i taggen
`arbeidskrav-product-brief-v2`, og det som bare sto i briefen, står nå i
`begrunnelser.md`, seksjonen «Fra Product Brief, versjon 2».

*Rettet 2026-09-24:* versjon 3 og 4 festet påstanden om nyhetstreffene bare til
testen 17.09, som ikke har tall eller rådata (`malinger.md` §0). Versjon 5
skiller testen 17.09 («flere av de ti») fra kjøringen 21.09, der det gjaldt
flertallet (`malinger.md` §7.2 og §10), slik versjon 2 festet påstanden (commit
`fc8edc2`).

*Rettet 2026-09-25:* versjon 6 sier «webapplikasjon som kjører lokalt» i stedet for
«webapplikasjon for PC». Mobiltilpasning står fortsatt utenfor v1 under «Scope»,
og plattformvalget står i PRD-en.

*Presisering 2026-09-25:* merknaden om versjon 5 sier «slik versjon 2 festet
påstanden». Det gjelder kjøringen 21.09. Versjon 2 sa også «flertallet» om
testen 17.09, så skillet mellom «flere» (17.09) og «flertallet» (21.09) er nytt i
versjon 5.

*Rettet 2026-09-25:* versjon 7 har fått en linje til slutt med lenker til PRD-en,
målingene og datakildenes vilkår. Linjen kom ikke med i versjon 6.

---

## 5. Offentlig repo

> Repoet deres er allerede offentlig i IBE160-organisasjonen, så det er også i
> orden.

**Kilde:** faglærer i IBE160, 20.09.2026, ordrett i `docs/reflection-log.md`.

| | |
|---|---|
| **Status** | **Finnes** |
| **Ligger i** | `IBE160-2026/G74-lund-osen` |
| **Gjenstår** | Ingenting. Merk at dette er en **betingelse** for hva som kan ligge der: EODHDs godkjenning krever at data ikke publiseres, og `data/` er gitignorert |

*Lagt til 2026-10-05:* utviklingen skal ligge fortløpende i GitHub: «Derfor er
det også viktig at prosjektet og utviklingen ligger fortløpende i GitHub, slik
at vi kan følge progresjonen deres.» (hjelpelæreren, svaret 05.10, under
«Spørsmål sendt hjelpelærer 2026-10-04»).

---

## 6. Teknologistack — anbefaling, ikke krav

> en klar fordel å bruke omtrent samme teknologistack som Bård Inge bruker i
> undervisningen

**Kilde:** faglærer i IBE160, 21.09.2026. Frasen er ordrett; gjengitt i
`begrunnelser.md` §10. Undervisningen bruker Node.js.

| | |
|---|---|
| **Status** | **Bevisst avvik, med kostnaden ført** |
| **Ligger i** | `begrunnelser.md` §10 |
| **Gjenstår** | Ingenting. Gruppen står fritt til å velge Python, TypeScript eller en kombinasjon — dette er en anbefaling med begrunnelse, ikke et krav |

---

## 7. BMAD-leveransen, frist 27.09.2026

**Kilde:** `docs/reflection-log.md`, oppføringen fra 19.–20.09: «Ny
innleveringsdato for BMAD-leveransen er satt til søndag 27.09.2026 (uke 39).»

⚠️ **Datoen står uten navngitt kilde.** Loggen fører den som et faktum, men sier
ikke hvem som satte den eller hvor den er kunngjort. Den er tatt med her fordi
den er ført i repoet og styrer arbeidet, men den bør bekreftes mot Canvas eller
faglærer før den brukes til å planlegge.

*Rettet 2026-09-24 (kilde: faglærer):* fristen for arbeidskravet er
**søndag 27.09.2026**. Da vurderer faglærerne Product Brief som
godkjent eller ikke godkjent, med tilbakemelding. Datoen har dermed en kilde.
Om fristen også gjelder de andre BMAD-dokumentene, er ikke opplyst.

| | |
|---|---|
| **Status** | **Uavklart hva den omfatter** |
| **Ligger i** | Product Brief, PRD, arkitekturspine og `epics.md` er alle skrevet |
| **Gjenstår** | **Besvart 23.09, se under:** BMAD er «fortsatt en sterkt anbefalt arbeidsmetode» — anbefalt, ikke krav — og de sentrale dokumentene «bør derfor ... pushes dit». De ligger allerede i repoet. Emnesiden fører selve arbeidskravet som product brief i repoet (se «Eksamen»). Fristen 27.09 er gitt av faglærer (rettelsene under «Arbeidskrav»). *Rettet 2026-09-26:* her sto «Utsettelsen til 27.09 har fortsatt ingen navngitt kilde». |

---

## 8. Dokumentasjon av KI-bruk og kvalitetssikring

*Lagt til 2026-09-24.* Emnesiden legger dette under prosjektkoden (70 %):
«Dokumentasjon må vise hvordan KI ble brukt, og hvordan studentene har
kvalitetssikret koden». Se «Eksamen» øverst.

| | |
|---|---|
| **Status** | **Delvis — materialet finnes, samlingen ikke** *Rettet 2026-10-03:* samlingen finnes nå i `docs/kvalitetssikring.md` (story 9.1, `2208ae1`), som står i review til Marian eller Joakim har lest den. *Rettet 2026-10-03:* dokumentet er lest av Marian, og 9-1 er done. |
| **Ligger i** | `docs/reflection-log.md` (ført siden 13.09), kontrollrapportene `docs/kontroll-2026-09-22.md`, `docs/kontroll-2026-09-22-plan.md` og `docs/kontroll-2026-09-26.md`, CI i `.github/workflows/tester.yml`, nettverkssperren i `tests/conftest.py`, mutantene, som står i commit-meldingene og i spesifikasjonene i `_bmad-output/implementation-artifacts/`, og instruksjonene ordrett i dagsfilene i `docs/ai-prompts/` (regel 18). *Rettet 2026-09-26:* her sto «mutantene, som i dag bare står i commit-meldingene». |
| **Gjenstår** | Epic 9 i `epics.md`: 9.1 `docs/kvalitetssikring.md` (tester, CI, mutanter, og hva som ikke testes), og 9.2 instruksjonene ordrett, som nå føres i dagsfilene etter regel 18 (story 9.2 i `epics.md`). 9.3 arbeidsmønsteret er ferdig (`7152b51`). *Rettet 2026-09-26:* her sto «9.2 instruksjonene ordrett i `docs/ai-prompts/bygging/`, og 9.3 arbeidsmønsteret». `bygging/` finnes ikke. *Rettet 2026-10-03:* 9.1 er skrevet (`2208ae1`), så det som gjenstår her, er 9.2. |

---

## Spørsmål sendt faglærer 2026-09-22

Sendt i Teams av Marian. Tre spørsmål, alle om ting denne lista ikke kan
kontrollere mot en kilde:

| # | Spørsmål | Hvilke punkter det treffer |
|---|---|---|
| 1 | **Er leveranselista fullstendig?** Altså: er «kildekode og docker fil» pluss refleksjonsrapporten alt, eller finnes det mer | Hele dokumentet. Svaret avgjør om delen «Antatt, ikke bekreftet» kan tømmes |
| 2 | **Hvilke datoer gjelder for demonstrasjon og prosjektinnlevering?** | Punkt C og D under. Åpent punkt 13 i `prd.md` |
| 3 | **Skal noen BMAD-dokumenter leveres inn?** | Punkt E under, og BMAD-fristen 27.09 i §7 |

*Skrevet 22.09, bevart:* «Svar avventes. Spørsmål 2 og 3 er de to eldste
ubesvarte i prosjektet — spørsmålet om hvilke BMAD-artefakter som er
innleveringskrav ble stilt i `reflection-log.md` allerede 20.09 og har stått
siden.»

### Svaret, 2026-09-23

**Fra:** hjelpelærer i IBE160. Navnet er ikke oppgitt i økta og ikke ført her.
**Dato:** 2026-09-23. **Form:** de bærende setningene, gjengitt av Marian.
Fullteksten ligger ikke i repoet.

> Det viktigste er at dere utvikler en applikasjon ved hjelp av KI, og at
> utviklingsprosessen er synlig og dokumentert.

> Det står derimot ikke på emnesiden jeg har tilgjengelig at Dockerfile eller en
> bestemt type database er et eksplisitt leveransekrav.

> BMAD er fortsatt en sterkt anbefalt arbeidsmetode

> de sentrale dokumentene som viser hvordan prosjektet er planlagt og utviklet er
> viktige

> bør derfor ... pushes dit

> Bård Inge vil presisere dette.

| # | Spørsmålet | Svaret |
|---|---|---|
| 1 | Er leveranselista fullstendig? | **Delvis.** Emnesiden lister mappeinnlevering (prosjektkode 70 %, refleksjonsrapport 30 %) og arbeidskravet. **Dockerfile og database står ikke der** — de flyttes til «sagt i samtale, ikke bekreftet» i §1 og §2. Emnesiden sier «tre deler» og lister to: åpent punkt 21 |
| 2 | Datoer for demonstrasjon og prosjektinnlevering? | **Ingen dato finnes ennå.** «Bård Inge vil presisere dette.» Åpent punkt 13 står nå som «avventer Bård Inge» |
| 3 | Skal BMAD-dokumenter leveres inn? | **Anbefalt, ikke krav.** De sentrale dokumentene er «viktige» og «bør derfor ... pushes dit». De ligger allerede i repoet |

## Spørsmål sendt hjelpelærer 2026-10-04

Sendt på e-post av Marian før kl. 21:49. Navnet på hjelpelæreren føres ikke.
Teksten ordrett:

> Hei! Gruppe G74 her, med et kort spørsmål om innleveringen.
>
> Appen kjører lokalt og starter med én kommando i Docker. Vi lager to versjoner med samme kode og samme SQLite-database:
> - Den ekte versjonen henter sluttkurser fra EODHD. Den krever en gratis konto hos dem, uten betalingskort, fordi vilkårene ikke lar oss dele vår: https://eodhd.com/register. Gratisplanen gir 20 kall i døgnet, og appen bruker 15 per henting. README-en viser hvordan nøkkelen legges inn.
> - Demoversjonen har oppdiktede tall og trenger ingen konto.
>
> KI-teksten lages av en lokal modell som lastes ned automatisk første gang, så den krever verken konto eller nøkkel.
>
> Vi håper dere vil teste med ekte kurser. Er dere villige til å lage en gratis konto hos EODHD, eller foretrekker dere demoversjonen? Og bruker dere Docker Desktop eller Python?
>
> Takk!
> Marian og Joakim, G74

Svar avventes.

*Besvart 2026-10-05:* svaret står under.

| Svaret om | Storyene det treffer |
|---|---|
| Docker Desktop eller Python | 3.1 og 3.3 (Docker og README) |
| Ekte kurser eller demoversjonen | 3.3 og 3.4 |
| Den lokale modellen | 10.2 |

### Svaret, 2026-10-05

**Fra:** hjelpelærer i IBE160, i Teams. Navnet føres ikke. **Form:** fullteksten,
slik Marian ga den videre 05.10.

> Hei Marian,
>
> Takk for god forklaring
>
> Jeg ville anbefalt at dere ikke gjør vurderingen avhengig av at vi må opprette konto hos en ekstern tjeneste for å kunne teste appen. Det tryggeste er at dere sørger for at løsningen også kan kjøres og vurderes uten dette.
>
> En demoversjon med samme funksjonalitet og struktur, men med test-/demodata, høres derfor ut som en veldig god løsning. Dere kan gjerne samtidig dokumentere i README hvordan man kan koble til EODHD med egen API-nøkkel dersom man ønsker å teste med ekte data.
>
> I dette emnet er det heller ikke nødvendigvis poenget at absolutt alt skal være helt perfekt eller produksjonsklart. Det viktigste er at dere lærer underveis, utvikler løsningen steg for steg og viser at dere forstår sammenhengene og valgene dere gjør. Derfor er det også viktig at prosjektet og utviklingen ligger fortløpende i GitHub, slik at vi kan følge progresjonen deres.
>
> Så jeg mener en god demoversjon er mer enn tilstrekkelig for å vise hvordan løsningen fungerer, samtidig som dere dokumenterer hvordan den kan brukes med ekte data. Bård Inge kommer heller ikke til å sitte og detaljteste hver eneste ekstern integrasjon i alle prosjektene.
>
> Når det gjelder Docker/Python, ville jeg lagt opp README-en slik at oppstarten er så enkel og tydelig som mulig, gjerne med en anbefalt hovedmåte å kjøre prosjektet på.
>
> Dette ser derfor ut som en veldig fornuftig løsning

| Spørsmålet | Svaret |
|---|---|
| Ekte kurser eller demoversjonen? | Demoversjonen er «mer enn tilstrekkelig», og README-en kan vise hvordan man kobler til EODHD med egen nøkkel |
| Docker Desktop eller Python? | Ikke besvart direkte, men README-en bør ha «en anbefalt hovedmåte å kjøre prosjektet på» |
| Den lokale modellen | Ikke nevnt |

Hva gruppen gjør med svaret, føres når det er avgjort.

*Avgjort 2026-10-05, gruppens beslutning kl. 16:53:* demoversjonen er hovedveien
for vurderingen, og den ekte versjonen med egen EODHD-nøkkel står i README-en
som et valg. Docker er hovedmåten i README-en, og Python med uv er
alternativet. Den første kommandoen starter demoen. Den lokale modellen starter
ikke av seg selv, og blir et eget valg i story 10.2. 3.1 til 3.4 bygges uten
KI-tekster rett etter 2.3, og KI-tekstene i demoen blir story 3.4b. Hentingen
fortsetter hver børsdag. Ført i `prd.md` under FR-411, i `epics.md` og i spinen
(AD-9).

---

## Antatt, ikke bekreftet

Dette er ting vi arbeider som om de gjelder, **uten at det finnes en ordrett
kilde i repoet.** De er ikke gale — de er ubelagte.

### A. «Emnets vurdering ber om dokumentasjon på hvordan koden er kvalitetssikret»

**Belagt 2026-09-23 — står ikke lenger som antakelse.** Emnesiden:
«Dokumentasjon må vise hvordan KI ble brukt, og hvordan studentene har
kvalitetssikret koden», under prosjektkoden (70 %). Se «Eksamen» øverst.
*Skrevet 22.09, bevart:* antakelsen sto som begrunnelse i
`.github/workflows/`-kommentaren og i `README.md`, begge uten kilde, og testene
og CI-oppsettet var bygget på den.

### B. Hva de tre nivåene krever ut over database

Sitatet navngir «Enkel, Medium, Vanskelig», men sier bare at **alle tre**
innebærer database. Hva som skiller dem, og hvilket nivå prosjektet sikter mot,
finnes ikke skrevet ned noe sted.

### C. Dato for prosjektinnlevering

Ukjent. Ført som **åpent punkt 13** i `prd.md` — eier **Marian**, status
**avventer Bård Inge**. Spørsmålet ble stilt 22.09 og besvart 23.09: det finnes
ingen dato ennå, og «Bård Inge vil presisere dette». Fire av de åtte suksessmålene i PRD §7 er bundet til
de to datoene: «Før prosjektinnlevering», «Ved prosjektinnlevering», «Før
demonstrasjonen» og «Ved demonstrasjonen». *Rettet 2026-09-24: her sto «Åtte
suksessmål».*

### D. Dato for demonstrasjonen

Ukjent, samme åpne punkt 13, samme eier og status — avventer Bård Inge. PRD §7 fører «Før
demonstrasjonen, est. uke 45» — og «est.» er vår egen estimering, ikke en
oppgitt dato. Målene «KI-bidrag i drift» og «Grensesnitt og stabilitet» henger
på den.

*Lagt til 2026-09-25:* Demonstrasjonen skal ikke avhenge av dagens henting. Det
trengs et kort demomanus og en måte å kjøre løsningen på kjente data, i tilfelle
hentingen feiler eller kvoten er brukt opp den dagen. Når datoen er kjent, blir
det en egen oppgave.

*Lagt til 2026-10-05:* demoversjonen (FR-411, story 3.4) er måten å kjøre
løsningen på kjente data. Hjelpelæreren skriver at «en god demoversjon er mer
enn tilstrekkelig for å vise hvordan løsningen fungerer» (svaret 05.10, under
«Spørsmål sendt hjelpelærer 2026-10-04»).

### E. Om PRD og arkitekturdokument er innleveringskrav i seg selv

**Besvart 23.09:** ikke et krav, men de sentrale dokumentene «bør derfor ...
pushes dit», og BMAD er «fortsatt en sterkt anbefalt arbeidsmetode». De ligger
allerede i repoet. *Skrevet 22.09, bevart:* spørsmålet ble stilt i loggen 20.09
og stilt på nytt i Teams 22.09.

### F. Formkrav til refleksjonsrapporten

Lengde, struktur og format er ukjent. Det eneste som er bekreftet, er *når* den
skrives. *Rettet 2026-09-24:* innholdet er også bekreftet. Emnesiden gir tre
innholdskrav, sitert under «Eksamen» øverst.

---

## Ferdig i dag

| Punkt | |
|---|---|
| **Product Brief** | Låst og klar for levering: tag `arbeidskrav-product-brief-v7`, commit `e62ea77`. Arbeidskrav på 1–2 sider, innleveringsfrist 27.09. Gjenstår: vurdering fra faglærerne etter fristen *Rettet 2026-10-06:* vurderingen fra faglærer kom 06.10 i egen fil, [`tilbakemelding-product-brief.md`](../_bmad-output/planning-artifacts/tilbakemelding-product-brief.md). Versjon 8 av briefen er story 9.6 i `epics.md`. |
| **Offentlig repo** | Bekreftet i orden |
| **Teknologivalg** | Avviket er besluttet og begrunnelsen ført |
| **Databasevalget** | Besluttet og kontrollert med faglærerstaben — *valget*, ikke lagringen |

## Delvis bygget

*Egen overskrift 2026-09-24:* databaseraden sto under «Finnes ikke i det hele
tatt».

| Punkt | Merknad |
|---|---|
| **Databasen** | Sagt i samtale av faglærer 21.09, ikke bekreftet på emnesiden. Gjøres likevel. **Delvis bygget 23.09:** migrasjonsløper (story 1.1, `57a83c5`), `kurs` og `kursserie` med SQLite-adapter (story 1.3, `f4fada0`). Ikke koblet til appen ennå. *Rettet 2026-10-05:* koblet til appen. Hentingen skriver kursene og dagens vurdering til basen (story 2.1b og 2.5), og sidene leser kursene og vurderingen derfra (story 2.2, `1570ae9`, og 2.2b, `ff58ecf`). Basen har migrasjonene 0001–0004: `kurs`, `vurdering`, `aksje` og målingene |

## Finnes ikke i det hele tatt

| Punkt | Merknad |
|---|---|
| **Dockerfile** | Sagt i samtale av faglærer 21.09 («kildekode og docker fil»), ikke bekreftet på emnesiden (hjelpelærer 23.09). Gjøres likevel. Arkitekturen er klar, filen er ikke skrevet |
| **Demoversjonen** *(lagt til 2026-10-05)* | Oppdiktede selskaper og kurser i en egen base, uten konto og uten nøkkel (FR-411, story 3.4). Hovedveien for vurderingen etter svaret fra hjelpelæreren 05.10. Bygges sammen med Docker i 3.1–3.4 |
| **Refleksjonsrapporten** | Råmaterialet er ført siden 13.09, men rapporten skal etter faglærers eget svar skrives *etter* prosjektet |
| **Datoene** | Både prosjektinnlevering og demonstrasjon er ukjente, og fire av de åtte suksessmålene henger på dem (*rettet 2026-09-24: her sto «åtte»*) |

**Det mest presserende er ikke en fil, men to datoer.** Dockerfilen og databasen
har begge en besluttet arkitektur og kan bygges. Punkt 13 har stått med frist
«Snarest» og uten eier siden PRD-en ble skrevet, og uten de datoene kan ikke
«uke 45» eller «minst én ukes drift» planlegges mot noe. *Rettet 2026-09-24:*
punkt 13 har eier, Marian, og status «avventer Bård Inge», jf. «C. Dato for
prosjektinnlevering» over.
