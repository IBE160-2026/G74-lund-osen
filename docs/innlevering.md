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
| **Ligger i** | `src/` (10 moduler og `migrasjoner/`), `tests/` (13 filer, 285 tester — telt 2026-09-24), `.github/workflows/`, `pyproject.toml`, `uv.lock` |
| **Gjenstår** | **Dockerfile finnes ikke.** Kontrollert 21.09 og igjen 22.09: ingen treff på `Dockerfile` eller `docker-compose` noe sted i repoet. Ført som åpent punkt 18 i `prd.md` |

Arkitekturen for den er besluttet 22.09 og ligger i `ARCHITECTURE-SPINE.md`:
`AD-9` (imaget inneholder aldri data), `AD-10` (webserveren henter aldri),
`AD-11` (to volumer), `AD-12` (hemmeligheter fra miljøet). Selve filen er ikke
skrevet.

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
| **Status** | **Delvis — oppdatert 2026-09-23** |
| **Ligger i** | `src/migrering.py` (story 1.1), `src/lagring_sqlite.py` og `src/migrasjoner/0001_kurs.sql` (story 1.3). Beslutningen ligger i `ARCHITECTURE-SPINE.md` `AD-3` til `AD-7`, `AD-16`, `AD-18`, `AD-19` |
| **Gjenstår** | Å koble lagringen til appen (story 1.4–1.5), vurderingslageret (1.6–1.7) og KI-loggen (4.3). *Skrevet 22.09, bevart:* «Hele lagringslaget. `kursdata.py` leser i dag en JSON-fil, og `app.py` leser den direkte utenom porten» |

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
| **Status** | **Finnes. Faglærer svarte 20.09 på et spørsmål fra gruppen om briefen, med positiv tilbakemelding – ikke en godkjenning** |
| **Ligger i** | `_bmad-output/planning-artifacts/product-brief.md` |
| **Gjenstår** | Fryse teksten og føre hvilken commit som leveres. **Formatkrav: ingen** — sagt eksplisitt i tilbakemeldingen |

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

| | |
|---|---|
| **Status** | **Uavklart hva den omfatter** |
| **Ligger i** | Product Brief, PRD, arkitekturspine og `epics.md` er alle skrevet |
| **Gjenstår** | **Besvart 23.09, se under:** BMAD er «fortsatt en sterkt anbefalt arbeidsmetode» — anbefalt, ikke krav — og de sentrale dokumentene «bør derfor ... pushes dit». De ligger allerede i repoet. Emnesiden fører selve arbeidskravet som product brief i repoet (se «Eksamen»). Utsettelsen til 27.09 har fortsatt ingen navngitt kilde |

---

## 8. Dokumentasjon av KI-bruk og kvalitetssikring

*Lagt til 2026-09-24.* Emnesiden legger dette under prosjektkoden (70 %):
«Dokumentasjon må vise hvordan KI ble brukt, og hvordan studentene har
kvalitetssikret koden». Se «Eksamen» øverst.

| | |
|---|---|
| **Status** | **Delvis — materialet finnes, samlingen ikke** |
| **Ligger i** | `docs/reflection-log.md` (ført siden 13.09), kontrollrapportene `docs/kontroll-2026-09-22.md` og `docs/kontroll-2026-09-22-plan.md`, CI i `.github/workflows/tester.yml`, nettverkssperren i `tests/conftest.py`, og mutantene, som i dag bare står i commit-meldingene |
| **Gjenstår** | Epic 9 i `epics.md`: 9.1 `docs/kvalitetssikring.md` (tester, CI, mutanter, og hva som ikke testes), 9.2 instruksjonene ordrett i `docs/ai-prompts/bygging/`, og 9.3 arbeidsmønsteret |

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
| **Product Brief** | Finnes. Faglærer svarte 20.09 på et spørsmål fra gruppen om briefen, med positiv tilbakemelding – ikke en godkjenning. Formatkrav: ingen. Gjenstår: fryse teksten og levere som arbeidskrav |
| **Offentlig repo** | Bekreftet i orden |
| **Teknologivalg** | Avviket er besluttet og begrunnelsen ført |
| **Databasevalget** | Besluttet og kontrollert med faglærerstaben — *valget*, ikke lagringen |

## Delvis bygget

*Egen overskrift 2026-09-24:* databaseraden sto under «Finnes ikke i det hele
tatt».

| Punkt | Merknad |
|---|---|
| **Databasen** | Sagt i samtale av faglærer 21.09, ikke bekreftet på emnesiden. Gjøres likevel. **Delvis bygget 23.09:** migrasjonsløper (story 1.1, `57a83c5`), `kurs` og `kursserie` med SQLite-adapter (story 1.3, `f4fada0`). Ikke koblet til appen ennå |

## Finnes ikke i det hele tatt

| Punkt | Merknad |
|---|---|
| **Dockerfile** | Sagt i samtale av faglærer 21.09 («kildekode og docker fil»), ikke bekreftet på emnesiden (hjelpelærer 23.09). Gjøres likevel. Arkitekturen er klar, filen er ikke skrevet |
| **Refleksjonsrapporten** | Råmaterialet er ført siden 13.09, men rapporten skal etter faglærers eget svar skrives *etter* prosjektet |
| **Datoene** | Både prosjektinnlevering og demonstrasjon er ukjente, og fire av de åtte suksessmålene henger på dem (*rettet 2026-09-24: her sto «åtte»*) |

**Det mest presserende er ikke en fil, men to datoer.** Dockerfilen og databasen
har begge en besluttet arkitektur og kan bygges. Punkt 13 har stått med frist
«Snarest» og uten eier siden PRD-en ble skrevet, og uten de datoene kan ikke
«uke 45» eller «minst én ukes drift» planlegges mot noe. *Rettet 2026-09-24:*
punkt 13 har eier, Marian, og status «avventer Bård Inge», jf. «C. Dato for
prosjektinnlevering» over.
