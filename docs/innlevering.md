# Leveranseliste — IBE160, gruppe G74

**Bygget 2026-09-22 på kilder, ikke på hukommelse.** Hvert punkt bærer sitatet
det hviler på, og hvor sitatet står. Punkter uten ordrett kilde står nederst,
under «Antatt, ikke bekreftet» — de er ikke fjernet, men de er ikke blandet inn
blant det som er belagt.

Lista er kort med vilje. Et punkt uten kilde er verdt mindre enn ingen punkter,
fordi det ser like troverdig ut som resten.

---

## 1. Kildekode og Dockerfile

> **Innleveringen er «kildekode og docker fil».**

**Kilde:** faglærer i IBE160, 21.09.2026. Ført i `docs/reflection-log.md`,
oppføringen «Fire avklaringer fra faglærer», punkt 2. Merk at bare frasen
«kildekode og docker fil» er ordrett; setningen rundt er loggens egen.

| | |
|---|---|
| **Status** | **Delvis** |
| **Ligger i** | `src/` (8 moduler), `tests/` (10 filer, 166 tester), `.github/workflows/`, `pyproject.toml`, `uv.lock` |
| **Gjenstår** | **Dockerfile finnes ikke.** Kontrollert 21.09 og igjen 22.09: ingen treff på `Dockerfile` eller `docker-compose` noe sted i repoet. Ført som åpent punkt 18 i `prd.md` |

Arkitekturen for den er besluttet 22.09 og ligger i `ARCHITECTURE-SPINE.md`:
`AD-9` (imaget inneholder aldri data), `AD-10` (webserveren henter aldri),
`AD-11` (to volumer), `AD-12` (hemmeligheter fra miljøet). Selve filen er ikke
skrevet.

---

## 2. Database

> Hvis du ikke har behov for en database, så er prosjektet ditt for enkelt, noe
> som vil gjenspeile karakter. Vi har tre nivå: Enkel, Medium, Vanskelig. Alle
> tre nivåene innebærer database, så uten database vil dette påvirke karakteren
> hardt.

**Kilde:** faglærer i IBE160, 21.09.2026. Ordrett i `docs/reflection-log.md` og
i `begrunnelser.md` §9.

| | |
|---|---|
| **Status** | **Mangler** |
| **Ligger i** | Ingenting er bygget. Beslutningen ligger i `ARCHITECTURE-SPINE.md` `AD-3` til `AD-7`, `AD-16`, `AD-18`, `AD-19` |
| **Gjenstår** | Hele lagringslaget. `kursdata.py` leser i dag en JSON-fil, og `app.py` leser den direkte utenom porten |

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
| **Status** | **Finnes, og er godkjent** |
| **Ligger i** | `_bmad-output/planning-artifacts/product-brief.md` |
| **Gjenstår** | Ingenting. **Formatkrav: ingen** — bekreftet eksplisitt |

Samme tilbakemelding godkjenner fordelingen mellom brief og PRD, inkludert vår
egen seksjon «Data og kilder» som ikke står i malen.

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
| **Gjenstår** | **Hvilke BMAD-artefakter som faktisk er innleveringskrav, er ikke avklart.** Loggen skrev 20.09 at dette burde avklares tidlig i uken; noe svar finnes ikke i repoet |

---

## Spørsmål sendt faglærer 2026-09-22

Sendt i Teams av Marian. Tre spørsmål, alle om ting denne lista ikke kan
kontrollere mot en kilde:

| # | Spørsmål | Hvilke punkter det treffer |
|---|---|---|
| 1 | **Er leveranselista fullstendig?** Altså: er «kildekode og docker fil» pluss refleksjonsrapporten alt, eller finnes det mer | Hele dokumentet. Svaret avgjør om delen «Antatt, ikke bekreftet» kan tømmes |
| 2 | **Hvilke datoer gjelder for demonstrasjon og prosjektinnlevering?** | Punkt C og D under. Åpent punkt 13 i `prd.md` |
| 3 | **Skal noen BMAD-dokumenter leveres inn?** | Punkt E under, og BMAD-fristen 27.09 i §7 |

**Svar avventes.** Spørsmål 2 og 3 er de to eldste ubesvarte i prosjektet —
spørsmålet om hvilke BMAD-artefakter som er innleveringskrav ble stilt i
`reflection-log.md` allerede 20.09 og har stått siden.

---

## Antatt, ikke bekreftet

Dette er ting vi arbeider som om de gjelder, **uten at det finnes en ordrett
kilde i repoet.** De er ikke gale — de er ubelagte.

### A. «Emnets vurdering ber om dokumentasjon på hvordan koden er kvalitetssikret»

Står som begrunnelse i `.github/workflows/`-kommentaren og i `README.md`, begge
uten kilde. Testene og CI-oppsettet er bygget på denne antakelsen. Hvis den
stemmer, er punktet dekket; hvis den ikke gjør det, har vi bygget noe nyttig av
feil grunn.

### B. Hva de tre nivåene krever ut over database

Sitatet navngir «Enkel, Medium, Vanskelig», men sier bare at **alle tre**
innebærer database. Hva som skiller dem, og hvilket nivå prosjektet sikter mot,
finnes ikke skrevet ned noe sted.

### C. Dato for prosjektinnlevering

Ukjent. Ført som **åpent punkt 13** i `prd.md` — eier **Marian**, status
«spørsmål sendt 22.09, svar avventes». Åtte suksessmål i PRD §7 er bundet til
den, blant annet «Før prosjektinnlevering» og «Ved prosjektinnlevering».

### D. Dato for demonstrasjonen

Ukjent, samme åpne punkt 13, samme eier og status. PRD §7 fører «Før
demonstrasjonen, est. uke 45» — og «est.» er vår egen estimering, ikke en
oppgitt dato. Målene «KI-bidrag i drift» og «Grensesnitt og stabilitet» henger
på den.

### E. Om PRD og arkitekturdokument er innleveringskrav i seg selv

Faglærer har godkjent fordelingen mellom brief og PRD, men det er ikke det samme
som at PRD-en skal leveres. Spørsmålet ble stilt i loggen 20.09 og **stilt på
nytt i Teams 22.09** — se over.

### F. Formkrav til refleksjonsrapporten

Lengde, struktur og format er ukjent. Det eneste som er bekreftet, er *når* den
skrives.

---

## Ferdig i dag

| Punkt | |
|---|---|
| **Product Brief** | Godkjent av faglærer, formatkrav bekreftet fraværende |
| **Offentlig repo** | Bekreftet i orden |
| **Teknologivalg** | Avviket er besluttet og begrunnelsen ført |
| **Databasevalget** | Besluttet og kontrollert med faglærerstaben — *valget*, ikke lagringen |

## Finnes ikke i det hele tatt

| Punkt | Merknad |
|---|---|
| **Dockerfile** | Navngitt av faglærer som halve innleveringen. Arkitekturen er klar, filen er ikke skrevet |
| **Databasen** | Besluttet, ikke bygget. Ingen tabell, ingen migrasjon, ingen adapter |
| **Refleksjonsrapporten** | Råmaterialet er ført siden 13.09, men rapporten skal etter faglærers eget svar skrives *etter* prosjektet |
| **Datoene** | Både prosjektinnlevering og demonstrasjon er ukjente, og åtte suksessmål henger på dem |

**Det mest presserende er ikke en fil, men to datoer.** Dockerfilen og databasen
har begge en besluttet arkitektur og kan bygges. Punkt 13 har stått med frist
«Snarest» og uten eier siden PRD-en ble skrevet, og uten de datoene kan ikke
«uke 45» eller «minst én ukes drift» planlegges mot noe.
