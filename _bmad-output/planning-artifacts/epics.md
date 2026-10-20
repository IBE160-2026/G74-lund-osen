---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md
  - _bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md
  - docs/kilder-og-rettigheter.md
excludedDocuments:
  - begrunnelser.md — rasjonale som med vilje er holdt ute av kravene. En nedbryting
    som leser den, skriver rasjonale inn i stories. Trenger en story en begrunnelse
    for å gi mening, er det kravet som er utydelig.
  - gjennomganger/ og memloggene — prosessmateriale, ikke krav.
---

# G74-lund-osen — Epic Breakdown

## Overview

Nedbryting av OSE Signal i epics og stories, fra en PRD og en arkitekturspine
som begge står som `final` per 2026-09-22.

**Fire føringer gjelder hele nedbrytingen:**

1. **Hver story leveres med test som kan kjøres uten API-kall.** Punkt 14,
   lukket 22.09 som `AD-8`. `tests/conftest.py` sperrer `socket.connect`, så en
   story som trenger nett for å testes, er ikke ferdig. *Rettet 2026-09-26:* her
   sto «Åpent punkt 14, og allerede bindende som `AD-8`».
2. **Meldingsdelen (FR-5xx) skal kunne falle bort uten at resten ryker.** Den
   hviler på en ubesvart Euronext-forespørsel; 28.09 er vår egen frist for å ta
   stilling uten svar. Ingen annen epic skal forutsette at den finnes.
3. **KI-laget (FR-6xx) legges tidlig, ikke sist.** Briefen og PRD-en lover
   KI-bidrag i drift (suksessmål i PRD §7), og det krever at laget har vært i
   bruk over tid. De tre blokkeringene beskriver hva «tidlig» må bestå av, ikke
   at det ikke kan være tidlig: **første KI-epic er *velg modelltjeneste og
   dokumentér betingelse 4*.** Det er papirarbeid, kan gjøres nå, og låser opp
   resten. *Rettet 2026-09-26:* her sto «Eksamen ber om KI-bidrag i drift».
   Emnesiden ber om en KI-generert applikasjon, og om dokumentasjon av hvordan
   KI ble brukt og hvordan koden ble kvalitetssikret (`docs/innlevering.md`),
   ikke om KI i selve applikasjonen.
   *Lagt til 2026-10-06:* suksessmålet heter nå «KI-forklaringen» (`prd.md` §7,
   brief v8), og det krever fortsatt én ukes logget drift.
4. **Blokkerte krav får egne epics, tydelig merket.** Ikke av ryddighetshensyn,
   men fordi blokkeringene kan slå ut: kommer Euronext-svaret som et nei, skal
   meldingsdelen kunne falle bort som **én hel enhet**. Blandes blokkerte krav
   inn blant ublokkerte, etterlater et nei hull spredt utover planen i stedet
   for én epic som strykes. Å holde dem helt utenfor er også feil — da
   forsvinner sporet av at de var planlagt, og det er nettopp det
   refleksjonsrapporten skal kunne lese.

**Hver blokkert epic skal bære fire ting:**

| Felt | Hva det svarer på |
|---|---|
| Blokkert av | Hvilket åpent punkt, med nummer |
| Eier | Hvem som eier punktet |
| Avgjøres | Når |
| Ved nei | Strykes epicen, eller finnes en målt vei rundt slik FR-407 har? |

**Rekkefølgeregelen i KI-epicen er en betingelse, ikke en merknad.** Betingelse 4
i EODHDs godkjenning — at modelltjenesten ikke trener på innholdet — må være
**ført** før artikkeltekst sendes inn i en modell. En story som sender inn tekst
er **blokkert av** dokumentasjonsstoryen. Ikke rekkefølgemessig anbefalt:
blokkert.

**Utvelgelsen av modelltjeneste må kunne forsvares mot betingelse 4**, og det
krever tre konkrete svar per kandidat:

1. Brukes innsendte data til trening?
2. Kan det slås av?
3. Står det i **vilkårene**, eller bare i markedsføringen?

## Requirements Inventory

### Functional Requirements

**4.1 Markedsoversikten**

- **FR-101** — Fem kolonner: selskap, sluttkurs, endring, signalstyrke, retning
- **FR-102** — Standard sortering
- **FR-103** — Retning vises i tre redundante kanaler
- **FR-104** — Hovedindeksen i markedsoversikten *(ny 2026-10-01)*
- **FR-105** — Søylene under hovedindeksen *(ny 2026-10-01)*
- **FR-106** — Børsometeret *(ny 2026-10-08)*
- **FR-107** — Endret signalstyrke siden forrige børsdag *(ny 2026-10-08)*
- **FR-108** — Filter på signalet *(ny 2026-10-08)*
- **FR-109** — Hjelpen på sidene *(ny 2026-10-08)*
- **FR-110** — Innstillinger *(ny 2026-10-08)*
- **FR-407** — Merking av utbyttedager *(ID beholdt fra da kravet lå i datahentingen)*

**4.2 Aksjedetaljen**

- **FR-201** — Kursgraf med seks måneders historikk
- **FR-202** — MA50-linjen tegnes oppå kursen
- **FR-203** — Øvrig innhold
- **FR-204** — Aksjedetaljen for en aksje uten gyldig signal
- **FR-205** — Se nærmere *(lagt til 2026-10-03)*
- **FR-206** — Signaldager i kursgrafen *(ny 2026-10-08)*
- **FR-207** — Kommende eks.dato i kursgrafen *(ny 2026-10-08)*

**4.3 Kommende finansielle hendelser**

- **FR-301** — Kilde og kobling til selskap
- **FR-302** — Hvilke hendelser og hvor langt frem
- **FR-303** — Når kalenderen ikke svarer

**4.4 Datahenting og oppdatering**

- **FR-401** — Henting utløses eksplisitt, aldri av en oppstart
- **FR-402** — Kontroll mot forventet børsdag, ikke mot klokkeslett
- **FR-403** — Etterfylling av kurser etter dager uten bruk
- **FR-404** — Etterfylling av børsmeldinger
- **FR-405** — Avkorting ved lange meldingsintervaller
- **FR-406** — To lagre for kursdata, med hvert sitt ansvar
- **FR-408** — Dagens vurdering lagres per aksje
- **FR-409** — De tre tilstandene skal være skillbare i lageret *(ny 22.09. Rettet 2026-09-24: her sto «vises». Kravet gjelder lageret, ikke en skjerm)*
- **FR-410** — Hovedindeksen hentes i samme kjøring *(ny 2026-10-01)*
- **FR-411** — Demoversjonen har oppdiktede tall i en egen base *(ny 2026-10-03)*
- **FR-412** — Lista over aksjer *(ny 2026-10-08)*
- **FR-413** — Måling av omsetning *(ny 2026-10-08)*
- **FR-414** — Eks.datoer ført for hånd *(ny 2026-10-08)*

**4.5 Meldingsfilter og deduplisering**

- **FR-501** — Deduplisering av språkdubletter
- **FR-502** — Kategorifilter i tre bøtter
- **FR-503** — Eks.dato som datakilde for utbyttemerking

**4.6 KI-laget og grensen mot regelbasert kode**

- **FR-601** — Av/på-bryteren er brukersynlig
- **FR-602** — Visningen når KI-laget er av
- **FR-603** — KI-teksten sier ikke mer enn grunnlaget
- **FR-604** — Logging av KI-bidraget, fra første kjøring
- **FR-605** — Promptversjon og modell lagres med hver KI-tekst
- **FR-606** — Relevansskalaen
- **FR-607** — KI-teksten om dagen på forsiden *(lagt til 2026-10-03)*
- **FR-608** — Valg av tjeneste *(lagt til 2026-10-05)*

*Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.8), godkjent av Marian kl. 12:46:* titlene på FR-603 og FR-605 følger `prd.md` etter omskrivingen 05.10. Her sto «FR-603 — Usikkerhet vises som forbehold, ikke som rekkefølge» og «FR-605 — Promptversjon og modell lagres med hver vurdering». Den gamle FR-603 heter nå FR-603A. FR-602A, FR-603A, FR-604A og FR-606A står i `prd.md` §4.6A og gjelder plan A, utenfor v1. De telles ikke med i de 51.

**4.7 Signalstyrke og retning**

- **FR-701** — Tre navngitte sjekker
- **FR-702** — Nøytralsone i trendsjekken
- **FR-703** — Signalstyrke
- **FR-704** — Retning
- **FR-705** — Terskel for at en aksje skiller seg ut
- **FR-706** — Synlig begrunnelse i aksjedetaljen

**34 FR-er i alt.** FR-409 kom til 22.09, da konsekvensen av `AD-7` ble
avgjort eksplisitt i stedet for å bli stående som en stille mangel.

*Lagt til 2026-10-01:* FR-104, FR-105 og FR-410 kom til med hovedindeksen OSEBX i
v1 (Marians beslutning), så det er 37 FR-er.

*Rettet 2026-10-03:* FR-205 (story 8.4) og FR-607 (story 10.6) kom til med
Marians beslutninger 02.10 og sto i PRD-en, men manglet i lista. Med dem er det
39 FR-er.

*Lagt til 2026-10-03:* FR-411 kom til med demoversjonen (Marians beslutning), så
det er 40 FR-er.

*Lagt til 2026-10-05:* FR-608 kom til med valget av KI-tjeneste (gruppens
beslutning 04.10), så det er 41 FR-er.

*Lagt til 2026-10-08:* FR-106–FR-110, FR-206, FR-207 og FR-412–FR-414 kom til
med endringsforslaget 08.10 (Marians beslutning), så det er 51 FR-er. FR-101,
FR-102, FR-201, FR-202, FR-407, FR-409, FR-411 og NFR-01 har fått tillegg.

### NonFunctional Requirements

- **NFR-01** — Daglig drift skal holde seg innenfor API-kvoten
- **NFR-02** — Brukeren venter aldri på en henting
- **NFR-03** — Manglende data stopper ikke hovedflyten
- **NFR-04** — KI-laget skal ikke kunne ta ned hovedflyten
- **NFR-05** — Norsk i grensesnitt og forklaringer
- **NFR-06** — Løsningen gir ikke investeringsråd
- **NFR-07** — Rådata bevares fra første kjøring
- **NFR-08** — Bare tall vi kan stå for *(lagt til 2026-10-03)*

*Rettet 2026-10-03:* NFR-08 kom inn i PRD-en 2026-10-01 og sto i NFR Coverage
Map, men manglet i lista. Med den er det åtte NFR-er.

### Additional Requirements

Fra `ARCHITECTURE-SPINE.md`. Disse er bindende på samme måte som FR-ene, og
flere av dem er **allerede oppfylt i kode** — de er merket med opphav.

**Lagring og datamodell**

- `AD-3` — Én port per eid datasett, én skriver per datasett. Portene er
  `Kurslager`, `Meldingslager`, `Vurderingslager`, `KILogg`. *`Meldingskilde` omdøpt
  2026-09-24 etter navneregelen i spinen: porten har en skriver.* *Bruddet med
  `Kurskilde` ved siden av `Kurslager` ble lukket 2026-09-25 i story 1.4c (`a91ef79`)*
- `AD-4` — SQLite fra standardbiblioteket. Ingen hostet database. *Bekreftet av
  faglærerstaben 22.09*
- `AD-5` — `erstatt_serie(symbol, rader, hentet)` gjør DELETE+INSERT i én
  transaksjon, og setter `sist_hentet` i samme transaksjon. Ingen `legg_til_rad`.
  *Rettet 2026-09-24: `hentet` manglet*
- `AD-6` — Rådata er uforanderlige filer, aldri rader. `<prefiks>-raa-<dato>.json`
- `AD-7` — `Vurderingslager` og `KILogg` har ingen slette- eller endremetode.
  `skriv` avviser enhver dato som ikke er inneværende børsdag
- `AD-18` — `vurdering` lagrer kursen som **verdi**, ikke som fremmednøkkel
- `AD-19` — Porten returnerer `list[Kursrad]` med norske felt. **Innføres i
  SAMME endring som SQLite-adapteren**, ikke som egen runde. *Rettet
  2026-09-24:* slik ble det ikke. Rekkefølgen ble story 1.2 (`Kursrad` og
  porten, `a796214`), 1.3 (SQLite-adapteren, `f4fada0`) og 1.4a–c. `Kursrad`
  kom i en egen endring før adapteren, som i spinens «Slik det ble»
- `AD-16` — Skjemaendringer skjer med nummererte migrasjoner. Migrasjonsløperen
  må styre transaksjonen selv; `executescript()` gjør implisitt COMMIT

**Arkitekturgrenser**

- `AD-1` — Kjernen gjør ingen I/O *(oppfylt: commit `01af1a5`, `706720f` m.fl.)*
- `AD-2` — Nettkall bare i skallet, én hentefunksjon per kilde, injisert
- **Gjenstående brudd:** `kursdata.py` gjør I/O i dag — `SnapshotKilde.fra_fil`
  leser fil, `nyeste_snapshot` globber katalog, og `app.py` kaller den direkte
  utenom enhver port. Utskillingen er arbeid som må gjøres. *Lukket 2026-09-25:
  story 1.5 flyttet lesingen til `lagring_fil.py` og oversettelsen til
  `eodhd.py`, commit `23af8db`. `app.py` får en `Kursleser` fra
  `lagring_fil.nyeste_leser`*

**Drift og leveranse**

- `AD-9` — Imaget inneholder aldri data. Bygges fra repoet, som ikke har noen
- `AD-10` — Webserveren starter aldri en henting. `docker run` koster null kall
- `AD-11` — To volumer: `ose-db` og `ose-raa`
- `AD-12` — Hemmeligheter fra miljøet, aldri fra image eller git
- `AD-17` — Hentekommandoen skriver dagens vurdering i samme kjøring
- `AD-20` — Børsdager i Europe/Oslo, tidsstempler i UTC. **To kjente feil i
  kode:** `fetch_prices.main` blander lokal dato og UTC; `meldinger._minutt`
  kutter på tegn 16 uten å gå via et tidsobjekt

**Kvalitet**

- `AD-8` — Nettverk sperret i testkjøringen *(oppfylt: commit `266e6d9`, 166
  tester grønne 2026-09-22. DNS og proxy sperret i `982b216`, 23.09)*
- `AD-13` — Signalparametre er konstanter med måling bak seg *(oppfylt:
  `NOYTRALSONE`, `VOLUMFAKTOR`, `TERSKEL`, `VOLATILITET_VINDU` og `VOLUM_VINDU`
  i `signalberegning.py`. Linjenumre byttet med navn 2026-09-24. Terskel,
  volumfaktor og nøytralsone i commit
  `8e88ecd`, de to vinduene i `eb7fd9a`)*
- `AD-14` — Deduplisering før kategorifilter *(oppfylt: commit `9acb55c`)*
- `AD-15` — En aksje som mangler data stopper ikke hovedflyten *(oppfylt:
  hentingen i `fetch_prices.hent_universet`, commit `352e3a2`; visningen i
  `markedsoversikt.py`, `706720f`, og `app.py` + `index.html`, `f4112fc`)*

**Låste parameterverdier fra `malinger.md`** — en story som rører disse, skal
stoppe mot målingen, ikke mot hukommelse:

| Parameter | Verdi | Målt |
|---|---|---|
| Terskel | **2** | §7.4, 199 handelsdager |
| Volumfaktor | **1,5 ×** | §7.4 |
| Nøytralsone | **±2 %** | §7.4 |
| `VOLATILITET_VINDU` | **20** | §9, 2 985 aksjedager |
| `VOLUM_VINDU` | **20** | §9, 2 985 aksjedager |
| MA-vindu | **50** | FR-701 |
| Minste historikk | **175 handelsdager** | FR-406 |

**Vilkårsbegrensninger fra `docs/kilder-og-rettigheter.md`**

- Euronext forbyr automatisert henting fra NewsWeb uten tillatelse på forhånd.
  Forespørsel sendt 21.09, **ubesvart**. Dette treffer FR-404, FR-501, FR-502,
  FR-503 og dermed FR-407 hvis den velger meldingsveien
- EODHDs godkjenning av språkmodellbruk har fire betingelser. **Betingelse 4 —
  at modelltjenesten ikke trener på innholdet — er udokumentert**, og må føres
  **før** artikkeltekst sendes inn i en modell
- Ingenting forlater maskinen: «the output stays local, the project is not
  publicly deployed»

### UX Design Requirements

**Ingen.** `[CU] bmad-ux` er bevisst hoppet over — UX-innholdet ligger i PRD-en
som ordinære funksjonelle krav (FR-101 fem kolonner, FR-103 retning i tre
redundante kanaler, FR-201/202 grafen, FR-204 tom-tilstand, FR-706 synlig
begrunnelse), og NFR-05 dekker språk. Det finnes derfor ingen egne UX-DR-er å
hente ut, og ingen er oppfunnet for å fylle seksjonen.

*Oppfølging 2026-09-23:* beslutningen står — det finnes fortsatt ingen UX-DR-er,
og designet ble ikke laget på forhånd. Men `[CU] bmad-ux` kjøres **sent**, som
en gjennomgang av de to skjermbildene som finnes, ikke som design fra bunnen:
**story 8.2**. To skjermbilder bærer hele inntrykket, og jo enklere
applikasjonen er, jo tydeligere må den være. Beslutningen om å hoppe over
steget er ført i PRD-memloggen 22.09, ikke 20.09 som den senere ble omtalt som.

### FR Coverage Map

**Levert før nedbrytingen — 12 FR-er.** Bygget som ren logikk med tester. De
*berøres* av Epic 1 gjennom `Kursrad`, men leverer ingen ny brukerverdi der.

| FR | Levert i |
|---|---|
| FR-101, FR-102 | `markedsoversikt.py`, commit `706720f`. *Lagt til 2026-10-07:* endringen i NOK i FR-101 er Epic 8, story 8.5 (Marians beslutning kl. 23:11). *Lagt til 2026-10-08:* lista som er aktiv i FR-101 er Epic 2, story 2.11, periodevalget i FR-101 er Epic 8, story 8.17, og sorteringen ved klikk i FR-102 er Epic 8, story 8.15 (endringsforslaget 08.10). |
| FR-103 | `markedsoversikt.py` + `index.html`. **`706720f` inneholdt bruddet** — den hadde `Retningsvisning("Opp", "↑", "opp")`, mens kravet krever modellens egen streng. Oppfylt av den senere commiten som fjernet oversettelsen |
| FR-201 | `aksjedetalj.py` `076bb12`, `graf.py` `b6ba9d8` |
| FR-202, FR-204 | Samme, **pluss `app.py` og `src/templates/`** — tegnforklaring, 200-svar og «kunne ikke regnes»-beskjed ligger der. *Lagt til 2026-10-08:* periodevalget i FR-201 er Epic 8, story 8.16, og sjekk 2 og 3 i grafen (FR-202, tillegget) er Epic 8, story 8.7 (endringsforslaget 08.10) |
| FR-701 – FR-705 | `signalberegning.py`, commit `01af1a5` |
| FR-706 | `aksjedetalj.py` (`076bb12`) + `aksje.html`. **Ikke `signalberegning.py`** — kravet gjelder aksjedetaljen |

**Merk at tabellen er skrevet fra kjernemodulene.** `app.py` og
`src/templates/` bærer halvparten av fem av disse kravene, og sto ikke nevnt før
kontrollen 22.09 fant det.

*Rettet 2026-10-03 (kontrollen 26.09, E7):* FR-101 ble endret 23.09, og story 1.4c i Epic 1 oppfyller kravet slik det står nå. FR-101 er altså også levert i Epic 1, selv om FR-lista for Epic 1 ikke nevner det.

**Fordelt på epics — 22 FR-er.** *Rettet 2026-09-24: her sto 21. Tabellen har 22, og summen under er 12 + 22.*

| FR | Epic |
|---|---|
| FR-203 | **Epic 5, 6 og 7 — delt.** «Øvrig innhold» er meldinger *pluss* KI-forklaring *pluss* hendelser. `aksjedetalj.py` sier selv at alle tre mangler med vilje. Å mappe den til én epic ville vært feil. *Lagt til 2026-10-07:* høy og lav i FR-203 er Epic 2, story 2.10 (lagringen), og Epic 8, story 8.5 (visningen), etter Marians beslutning kl. 23:11. |
| FR-301, FR-302, FR-303 | Epic 7 🔒 |
| FR-401, FR-402, FR-403 | Epic 2 |
| FR-404, FR-405 | Epic 6 🔒 |
| FR-406, FR-408, FR-409 | Epic 1 |
| FR-407 | Epic 2 |
| FR-104, FR-105, FR-410 | Epic 2 *(lagt til 2026-10-01)*. *Lagt til 2026-10-08 kl. 21:48:* periodene for søylene i FR-105 er Epic 8, story 8.17 |
| FR-501, FR-502, FR-503 | Epic 6 🔒 |
| FR-601, FR-602, FR-603 | Epic 10 *(rettet 2026-10-13)* |
| FR-606 | Ikke i v1: skalaen brukes ikke i applikasjonen (`prd.md`, FR-606) *(rettet 2026-10-13)* |
| FR-602A, FR-603A, FR-604A, FR-606A | Epic 5 🔒 *(lagt til 2026-10-13)* |
| FR-604, FR-605 | Epic 4 |
| FR-205 | Epic 8 *(lagt til 2026-10-03)* |
| FR-607 | Epic 10 *(lagt til 2026-10-03)* |
| FR-411 | Epic 3 *(lagt til 2026-10-03)* |
| FR-608 | Epic 10 *(lagt til 2026-10-05)* |
| FR-106, FR-107, FR-108, FR-109, FR-110, FR-206, FR-207 | Epic 8 *(lagt til 2026-10-08)*: 8.6, 8.12, 8.11, 8.9 og 8.13, 8.10, 8.8 og 8.18 |
| FR-412, FR-413, FR-414 | Epic 2 *(lagt til 2026-10-08)*: 2.11 og 2.12, 2.13, 2.14. De ferdige listene i FR-412 er Epic 8, story 8.11 |

*Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.8), godkjent av Marian kl. 12:46:* her sto «FR-601, FR-602, FR-603, FR-606 | Epic 5 🔒». Kravene ble skrevet om 05.10. FR-601, FR-602 og FR-603 bygges i Epic 10, FR-606 brukes ikke i v1, og Epic 5 har nå bare A-variantene.

*Rettet 2026-10-03 (kontrollen 26.09, E7):* tabellen viser epicen der kravet først bygges. FR-401 hører også til Epic 3, der en story oppfyller tom-tilstanden, og FR-408 også til Epic 2, der story 2.5 skriver vurderingen i hentingen.

**12 + 22 = 34.** Alle FR-er er plassert.

*Lagt til 2026-10-01:* med FR-104, FR-105 og FR-410 er det 12 + 25 = 37.

*Rettet 2026-10-03:* FR-205 og FR-607 manglet i tabellen. Med dem er det
12 + 27 = 39.

*Lagt til 2026-10-03:* med FR-411 er det 12 + 28 = 40.

*Lagt til 2026-10-05:* med FR-608 er det 12 + 29 = 41.

*Lagt til 2026-10-08:* med FR-106–FR-110, FR-206, FR-207 og FR-412–FR-414 er det
12 + 39 = 51. Tillegget til FR-407 (justeringsdagene i grafen) er Epic 8, story
8.14, og tillegget til FR-409 («ikke i lista») er Epic 2, story 2.11.

*Lagt til 2026-10-13, endringsforslaget 13.10 (punkt 4.8), godkjent av Marian kl. 12:46:* summen står: 12 + 39 = 51. FR-601, FR-602 og FR-603 er flyttet til Epic 10, og FR-606 står som ikke i v1, men alle er fortsatt plassert. A-variantene telles ikke, som i kravlista.

### NFR Coverage Map

| NFR | Dekning |
|---|---|
| **NFR-01** Kvote | **Eid av Epic 2.** Tverrgående støtte: `AD-8` gjør at ingen test kan bruke kvote |
| **NFR-02** Venter aldri | **Eid av Epic 2** (`AD-10`). Brødteksten rettet 22.09 fordi den lovet en mekanisme som ikke finnes |
| **NFR-03** Manglende data | **Tverrgående.** Delvis levert: `hent_universet` fortsetter ved feil (`352e3a2`), `app.py` tåler `kilde=None`, FR-204 finnes. **Kontroll på hver story:** en test for den tomme eller manglende stien |
| **NFR-04** KI tar ikke ned hovedflyten | **Eid av Epic 5.** Bortfaller hvis Epic 5 strykes. *Rettet 2026-09-24:* bortfaller ikke med Epic 5 alene. Epic 5B begrenses også av NFR-04 (5B.2 og 5B.3), så kravet gjelder så lenge én av dem bygges |
| **NFR-05** Norsk | **Tverrgående, levert i alt som finnes.** **Kontroll på hver visningsstory:** all brukervendt tekst er norsk |
| **NFR-06** Ikke investeringsråd | **Tverrgående.** Forbeholdstekst finnes: `src/templates/index.html:108` sier «Signalstyrken er 0–3 og sier hvor kraftig de tre sjekkene slår ut — *ikke om aksjen bør kjøpes eller selges*». Kravet er likevel et **forbud**, ikke et tekstkrav: ingen del av grensesnittet skal formuleres som anbefaling. **Kontroll på hver visningsstory:** ordlyden leses mot NFR-06 |
| **NFR-07** Rådata bevares | **Eid av Epic 1** (`AD-6`). Delvis levert: `fetch_prices` skriver tidsstemplede øyeblikksbilder (`352e3a2`) |
| **NFR-08** Bare tall vi kan stå for *(lagt til 2026-10-01)* | **Tverrgående.** Levert i det som finnes: «Ukjent» i FR-101, og ingen fallback mellom `close` og `adjusted_close` i `eodhd.py`. **Kontroll på hver visningsstory:** et tall som mangler eller ikke består kontrollen, vises som «–» med grunnen. For KI-teksten gjelder FR-603 |

*Lagt til 2026-10-13, Marians ja kl. 13:44, etter faglærers tilbakemelding 06.10 (`tilbakemelding-product-brief.md`):* FR-411 er også tverrgående. **Kontroll på hver visningsstory:** det storyen viser, vises også med demobasen, og en test krever det. Gjelder fra 8.0c.

**Alle sju NFR-er er plassert:** fire eid av en epic (NFR-01, 02, 04, 07), tre
tverrgående med navngitt kontroll (NFR-03, 05, 06).
*Rettet 2026-10-01:* med NFR-08 er det åtte: fire eid av en epic og fire
tverrgående (NFR-03, 05, 06 og 08).

*Lagt til 2026-10-13, endringsforslaget 13.10 (punkt 4.4), godkjent av Marian kl. 12:46:* fotnoten som raden for NFR-06 siterer, står nå i `src/templates/index.html:137`, ikke på linje 108. Den endres i 8.0c til «Signalstyrken sier hvor mange av de 3 sjekkene som slo ut, ikke om du bør kjøpe eller selge.» Forbeholdet om kjøp og salg står fortsatt synlig.

## Epic List

**Rekkefølge.** Pilene er harde avhengigheter, ikke anbefalinger.
Nummereringen er ikke byggerekkefølgen; grafen gjelder. *Lagt til 2026-09-24.*

```
Epic 1 (lagring) ──> Epic 2 (henting) ──> Epic 3 (leveranse)
                 └─> Epic 4.3 (SQLite-adapter for KILogg)

Epic 4.1 (papirarbeid)  ─┐  ingen avhengighet —
Epic 4.2 (port + minne) ─┘  parallelt med Epic 1 fra dag én

Epic 6 (meldinger) 🔒 ──> Epic 5 (KI i drift) 🔒 <── Epic 4.1
Epic 7 (hendelser) 🔒

Epic 2 ──> Epic 8.1 (brukertest) ──> Epic 8.2 (UX-gjennomgang)

Epic 4.1 + 4.2 ──> Epic 5B (KI forklarer signalet) 🔀 <── Epic 1.4a
                   utløses av nei eller taushet fra Euronext 28.09

Epic 1.9 (aksje-tabellen) ──> Epic 2 skriver til basen
Epic 2.2 + 2.5 ──> Epic 2.7 (historikken i aksjedetaljen)
Epic 2.1 ──> 2.1b (basen) ──> 2.5 ──> de daglige kjøringene til basen
Epic 2.1b ──> 2.1c (målingene) ──> 2.5   *(lagt til 2026-09-29)*
Epic 2.1b ──> Epic 4.3 (samme åpning av basen)
Epic 2.3 + 4.3 ──> 2.8 (indeksen hentes) ──> 2.9 (indeksen vises) ──> 2.9b (søylene)   *(lagt til 2026-10-01)*
Epic 2.2 ──> 2.9
Epic 4.1 ──> Epic 9.5 (relevanseksperimentet, del 2)   *(utgår 2026-10-06)*
Epic 2.5 ──> Epic 10.2 (teksten lages rett etter vurderingen)   *(lagt til 2026-10-03, E6)*
Epic 4.3 + 8.1 + 10.3 ──> Epic 10.4 (måle bidraget, med KILogg)   *(lagt til 2026-10-03, E6)*
Epic 4.0 + 4.2 + 4.3 ──> Epic 10.2 (nettsperren og KILogg før modellen)   *(lagt til 2026-10-05)*
Epic 10.1 ──> Epic 10.2 (grunnlaget)   *(lagt til 2026-10-05)*
Epic 3.4 + 10.2 + 10.3 ──> Epic 3.4b (KI-tekstene i demoen)   *(lagt til 2026-10-05)*
Epic 2.3 + 3.4 ──> Epic 2.3b (nye forsøk med kallene som er igjen)   *(lagt til 2026-10-05)*
Epic 8.0 ──> 8.0b + 8.0c ──> Epic 8.1   *(lagt til 2026-10-05)*
Epic 2.10 (høy og lav lagres) ──> Epic 8.5 (kroner, høy og lav)   *(lagt til 2026-10-07)*
Epic 2.3 + 2.8 ──> 2.11 (lista i basen) ──> 2.12 (velge og bytte) ──> 8.11 (ferdige lister)   *(lagt til 2026-10-08)*
Epic 2.3 + 2.8 ──> 2.13 (måling av omsetning) ──> 8.11   *(lagt til 2026-10-08)*
Epic 2.3 ──> 2.14 (eks.datoer for hånd) ──> 8.18 (eks.dato i grafen) <── 2.6   *(lagt til 2026-10-08)*
Epic 2.9b ──> 8.6 (børsometeret)   *(lagt til 2026-10-08)*
Epic 8.16 (startdagen) ──> 8.17 (periodene i oversikten) <── 8.3 + 8.6   *(lagt til 2026-10-08)*
Epic 2.7 ──> 8.8 (signaldager) og 8.12 (endret signalstyrke) <── 8.3   *(lagt til 2026-10-08)*
Epic 2.6 ──> 8.14 (justeringsdager)   *(lagt til 2026-10-08)*
Epic 8.0b ──> 8.9 (omvisningen) og 8.13 (Lær noe nytt)   *(lagt til 2026-10-08)*
Epic 8.0b + 8.3 + 10.3 ──> 8.10 (Innstillinger)   *(lagt til 2026-10-08)*
Epic 8.17 («Sammenlign med») ──> 8.12   *(lagt til 2026-10-08 kl. 21:48)*
```

*Lagt til 2026-10-08:* 8.6 sier i forslaget at den avhenger av 8.17 for
periodene, og 8.17 at den avhenger av 8.6. Grafen følger rekkefølgen Marian
godkjente: 8.6 først, med siste børsdag, og periodene i børsometeret kommer med
8.17. 8.7, 8.15 og 8.16 har ingen åpne avhengigheter. 8.9 bygges etter sidene den
viser.

*Lagt til 2026-10-05:* 10.2 skriver til `KILogg` (FR-604), og nettsperren må
dekke hele testkjøringen før noe kan kalle Ollama (`AD-8`). Derfor kommer 4.0,
4.2 og 4.3 før 10.2. Rekkefølgen for KI-laget er da 4.0, 4.2, 4.3, 10.1, 10.2,
3.1 med compose-fila, 10.3, 10.6, 3.4 og 10.7. 10.8 er kandidat til v1.1. Blir
tiden knapp, gir den lokale modellen alene gratis KI for alle, og 10.7 kan
vente.

*Rettet 2026-10-05, gruppens beslutning kl. 16:53, etter svaret fra
hjelpelæreren (`docs/innlevering.md`, «Svaret, 2026-10-05»):* 3.1, 3.2, 3.3
og 3.4 uten KI-tekster bygges rett etter 2.3. KI-laget kommer så i rekkefølgen
4.0, 4.2, 4.3, 10.1, 10.2, 10.3, 10.6, 3.4b og 10.7. 3.4b er KI-tekstene i
demoen. 10.8 er fortsatt kandidat til v1.1. Hentingen fortsetter hver børsdag
uansett hva som bygges, fordi en vurdering ikke kan fylles inn senere (`AD-7`).
En bygging som ikke er ferdig kl. 22:00, stopper på en commit, så hentingen kan
kjøres fra main.

*Lagt til 2026-10-05, gruppens beslutning kl. 19:17:* rekkefølgen er 2.3, 3.1–3.4, 2.3b, og så KI-laget. Når jobben kjører fra en egen arbeidskopi av main (svar 3 under story 2.3), gjelder ikke lenger regelen over om at byggingen stopper kl. 22:00.

*Lagt til 2026-10-17:* fra 19.10 går hentingen fra kl. 21:00 på børsdager (beslutningen 16.10 kl. 21:09 under story 2.3, `malinger.md` §31). Der regelen om at byggingen stopper, fortsatt gjelder, er klokkeslettet kl. 21:00.

*Lagt til 2026-10-20 kl. 15:24:* fra 20.10 går hentingen fra kl. 22:00 på børsdager igjen (gruppens svar 19.10 kl. 22:19 under story 2.3, `malinger.md` §37). Der regelen om at byggingen stopper, fortsatt gjelder, er klokkeslettet kl. 21:40.

*Lagt til 2026-10-05, Marians beslutning kl. 21:23:* 8.0b og 8.0c bygges etter 2.3b og før KI-laget.

*Lagt til 2026-10-06, Marians beslutning:* tilbakemeldingen på briefen ([`tilbakemelding-product-brief.md`](tilbakemelding-product-brief.md)) ber om at oversikten og aksjedetaljen er ferdige og stabile i demoen før KI-laget bygges ut, og at antall epics ikke vokser. Rekkefølgen fra 05.10 står: 2.3 først, fordi kveldshentingen da går fra egen arbeidskopi, og demoen kan bygges over flere dager uten stopp kl. 22:00. Så 9.6 og 3.1–3.4, før 2.3b, 8.0b, 8.0c og KI-laget.

*Rettet 2026-10-03 (kontrollen 26.09, E6):* grafen manglet to harde avhengigheter som står i storyene. 10.2 lager teksten i hentekommandoen rett etter vurderingen, og trenger derfor 2.5. 10.4 avhenger av 8.1 og 10.3, og måler bidraget med `KILogg` over minst én ukes drift, som krever 4.3.

*2026-09-28:* plan B er utløst. Epic 5, 6 og 7 er ute av v1, og Epic 5B heter Epic 10.

**Prioritering, besluttet 2026-09-23:** Epic 1, 2 og 3 først, fordi det er at
noen utenfor gruppen kan kjøre `docker run`, hente kurser og se begge
skjermbildene med ekte data. Brukertesten (8.1) kommer rett etter Epic 2, ikke
før innlevering. UX-gjennomgangen (8.2) kommer sent. Ingen utvidelse av
omfanget, og forbedringer ut over v1 tas først når dette er kontrollert og
virker. Begrunnelsen står i PRD-memloggen og i refleksjonsloggen 23.09.
**Epic 4.1 og 4.2 tas parallelt med Epic 1** (plan B, besluttet 23.09). De er
papirarbeid og en port, og de trengs i både plan A og plan B.

- **Epic 1 før Epic 2:** hentingen skriver gjennom `Kurslager`, som Epic 1
  oppretter. Uten porten har Epic 2 ingenting å skrive til.
- **Epic 2 før Epic 3:** Dockerfilen pakker to kommandoer, og den ene er
  hentekommandoen (`AD-10`). Den må finnes før den kan pakkes.
- **Epic 4.1 er parallell fra dag én.** Det er papirarbeid uten kodeavhengighet,
  og det er dette som gjør «KI tidlig» mulig i det hele tatt.
- **Bare Epic 4.3 venter på Epic 1.** Porten `KILogg` er en `Protocol` og vet
  ikke om lagringsformen — det er hele poenget med `AD-3`. Den kan defineres og
  prøves i sin helhet mot en minneimplementasjon, slik `MinneKilde` alt gjør i
  35 testreferanser over fire testfiler. Bare **SQLite-adapteren** trenger
  databasen. To av Epic 4s tre deler kan derfor kjøre parallelt med Epic 1.
  *Rettet 2026-09-25:* `MinneKilde` ble fjernet i story 1.4c. `MinneKurslager`
  viser det samme i dag: porten `Kurslager` prøves mot den i minnet.
- **Epic 5 etter både Epic 4.1 og Epic 6.** Se avhengighetsvarselet under.
- **Epic 8.1 rett etter Epic 2, ikke etter Epic 3.** Brukertesten trenger ekte
  data og begge skjermbildene, ikke Docker. Den kan kjøres på vår egen maskin.
- **Epic 8.2 etter 8.1.** Funnene fra brukertesten er det viktigste
  grunnlaget for gjennomgangen.

**Prioritering, oppdatert 2026-09-27**, etter svarene fra faglærerne og kodegjennomgangen av Epic 1. Prioriteringen fra 23.09 står, og rekkefølgen innenfor den er:
- *Må med, fordi faglærerne krever det:* databasen i bruk i Epic 2, med skrivingen først, fordi en vurdering ikke kan etterfylles (`AD-7`), og fordi «Adopsjon» og «Fortsatt bruk» i PRD §7 krever at vi bruker løsningen jevnlig. Punkt 23 avgjøres denne uka, fordi det blokkerer 2.1 *(avgjort 28.09)*. Deretter Dockerfile og README (Epic 3), `docs/kvalitetssikring.md` (9.1) og refleksjonsrapporten.
- *Det vi prøver å få til:* `aksje` med relasjoner (1.9) før Epic 2 skriver til basen, historikken i aksjedetaljen (2.7), KI-laget (4.0–4.3, og 5B.1–5B.3 hvis Euronext sier nei eller ikke svarer 28.09 (utløst 28.09)), målingene av KI (9.5 og 5B.4), brukertesten (8.1), og et kort demomanus med en reserve på kjente data (punkt D i `docs/innlevering.md`).
- *Hvis tiden strekker til:* 8.2 med endringene fra brukertesten, og 2.6.

Ingen av 1.9, 2.7 og 9.5 utvider omfanget: 1.9 er en skjemaendring før basen har data, 2.7 svarer på FR-408s eget spørsmål (punkt 20), og 9.5 er et suksessmål i PRD §7. «KI-bidrag i drift» krever minst én ukes drift før demonstrasjonen, som vi har anslått til uke 45, så KI-teksten må lages hver dag fra rundt 26.10.

**Prioritering, endret 2026-10-08, Marians beslutning** (endringsforslaget 08.10, [`sprint-change-proposal-2026-10-08.md`](sprint-change-proposal-2026-10-08.md), godkjent kl. 08:04 med endringene kl. 08:06): femten idéer er «Fast i v1», og 17 storyer kom til. «Ingen utvidelse av omfanget» fra 23.09 gjelder ikke dem. Rekkefølgen:
1. 2.3 bygges ferdig først, med kontrollpunktet om lista som parameter.
2. 3.1–3.4 før README-prøven 13.–16.10, med demoen i punkt 4.4 i forslaget.
3. 2.3b, 8.0b og 8.0c, som besluttet 05.10 og 06.10.
4. 4.0, 4.2, 4.3, 10.1 og 10.2, så KI-teksten lages hver dag fra rundt 26.10.
5. 10.3 og 3.4b rett etter 10.2, før de nye storyene, fordi KI-teksten må vises og være med i demoen for suksessmålet «KI-forklaringen».
6. De nye som bare leser det vi har, og er små: 8.15, 8.16 og 8.7.
7. Det som trenger historikken: 2.7, så 8.8 og 8.12. 2.6, så 8.14, og 2.14 og 8.18.
8. 10.6 og 10.7.
9. 2.8, 2.9, 2.9b, så 8.6 og 8.17.
10. 8.3, så 8.10, 8.9 og 8.13.
11. Lista: 2.11, 2.12, 2.13 og 8.11. 2.13 kan tas tidligere, fordi den ikke endrer lista.
12. 8.1, brukertesten for «Brukerutfall», har fast plass før uke 45 og før 8.2. 8.2, 8.4, 8.5, 2.10, 2.4 og 9.2 der de passer.

*Lagt til 2026-10-08 kl. 21:48:* storyene krever at 8.3 kommer før 8.17 og 8.12, og 8.17 før 8.12. Punkt 7, 9 og 10 følger ikke det, og rettes når rekkefølgen tas opp igjen etter README-prøven.

*Lagt til 2026-10-11, Marians beslutning:* 8.0d bygges etter 8.0b og 8.0c og før KI-laget (kl. 12:13).

Rekkefølgen tas opp igjen etter README-prøven, når farten er kjent. «Egen» avgjøres i planen for 2.12, og navnet på FR-407 og 2.6 i planen for 2.6.

*Lagt til 2026-10-13, endringsforslaget 13.10 ([`sprint-change-proposal-2026-10-13.md`](sprint-change-proposal-2026-10-13.md)), godkjent av Marian kl. 12:46:* 8.0e kommer etter 8.0c og før 8.0d. 10.6 kommer etter 2.9, fordi den trenger hovedindeksen (svar 16). Plassen til 8.19, 8.10b og resten avgjøres etter README-prøven (spørsmål 14 og 15). 2.15, endringen i 8.14 og tillegget i 10.1 og 10.2 føres etter prøven i kveld (N1, svar 6 og 23).

*Lagt til 2026-10-14 (gruppen kl. 22:19 og 22:25, «ja» og «1 ja mest mulig inn før readme prøven og 2 = ja»):* Rekkefølgen etter 8.0d er 8.15, så 2.8, 2.9 og 2.9b, 8.3, 8.10, 8.16 og 8.17, 2.7 og 8.8, 10.1–10.3, 8.10b, 10.6, og til slutt 2.11 og 2.12. README-prøven tas når mest mulig av dette er bygget, og senest én uke før innleveringen. Det erstatter linja under story 3.4 om at prøven tas etter at 8.0d er flettet (§9 i `docs/kvalitetssikring.md`).

*Lagt til 2026-10-15 (gruppens svar 10 kl. 14:47, spesifikasjonen for 8.15):* etter 8.15 kommer KI-laget først, med 4.2, 4.3 og 10.1–10.3, så resten i rekkefølgen fra 14.10 kl. 22:19 og 22:25. Grunnen er suksesskriteriet «KI-forklaringen» i briefen v8: én ukes drift skal være logget før demonstrasjonen.

*Avgjort 2026-10-17 kl. 22:06 (gruppens svar i chatten med rådet):* KI-tekstene i demoen (story 3.4b) bygges søndag 18.10 rett etter de to README-PR-ene og før 2.9b, fordi demoen i dag ikke har noen KI-tekst.

*Avgjort 2026-10-17 kl. 22:38, 22:41 og 22:42 (gruppens svar):* fire ting kommer inn: linter og formatterer i CI (story 9.7), tester i ekte nettleser, UX-gjennomgangen (8.2) med bilder av designarbeidet, og tabellen på smal skjerm. Søylene (2.9b) bygges før KI-tekstene i demoen (3.4b), og det erstatter rekkefølgen mellom de to i linja over fra kl. 22:06. Hovedindeksen blir en stiplet linje i kursgrafen på aksjesiden, som story 2.9c etter 2.9b. I natt bygges 9.7, 2.9b og 2.9c i den rekkefølgen, én PR hver.

*Avgjort 2026-10-18 kl. 00:03 (gruppens svar):* kopien `.agents/skills/` tas bort (story 9.8), og README-prøven tas første gang i uke 43, etter at de to README-PR-ene er flettet, og på nytt senest én uke før innleveringen, med ZIP-fila som leveres.

*Avgjort 2026-10-18 kl. 00:20 (gruppens svar):* et skjermbilde av oversikten i demoen kommer øverst i README-en igjen etter 3.4b, i en README-PR som stopper før flettingen (snur 16.10 kl. 21:38); arkitekturdokumentet oppdateres søndag etter 3.4b, med en test som krever at hver modul i `src/` står der, og `meldinger.py` tas bort med testene (story 9.9); de lange funksjonene i `fetch_prices.py` deles opp lørdag 24.10, uten endret oppførsel (story 9.10).

*Endret 2026-10-19 (gruppens svar 18.10 kl. 23:03, spesifikasjonen 3.3f):* bildet av oversikten står ikke lenger under «Til faglærer», men bak en knapp rett under beskrivelsen, sammen med de andre bildene av appen, i en egen mappe for bilder og video.

*Avgjort 2026-10-18 kl. 00:39 (gruppens svar):* etter søndagens arbeid kommer først det briefen v8 lover i v1: historikken (2.7), bryteren for KI-teksten på siden (8.10 og 8.10b), lenken til selskapets egen nettside (10.5) og egne nøkler (10.7). 8.16 og 8.17, 10.6, 2.11 og 2.12 kommer etter, siden briefen ikke nevner dem. Promptene fra 15.–23.09 føres inn denne uka som dagsfiler, merket som satt sammen i etterkant fra samtalene, uten nøkler, kurser eller andre navn enn medlemmene.

*Avgjort 2026-10-18 kl. 11:20 (gruppens svar):* spørsmålet kl. 00:39 bygde på en feil fra rådet. Bryteren for KI-teksten finnes alt på aksjesiden («Vis KI-teksten», FR-601), så briefens av/på-bryter er bygget, og 8.10 og 8.10b er ikke et løfte i briefen. De kommer etter 2.7, 10.5 og 10.7, og før 8.16 og 8.17, 10.6, 2.11 og 2.12. «Min liste» i briefen er story 8.3, som bygges i dag. 8.17 er periodevalget i oversikten, Min liste og børsometeret, og det nevner ikke briefen. En video av demoen, under 2 minutter og 5 MB, tas opp med nettlesertestene neste uke og lenkes fra README-en.

*Avgjort 2026-10-18 kl. 17:40 (gruppens svar):* appen bruker port 8000 i stedet for 5000, fordi AirPlay på Mac bruker 5000, i en egen PR i kveld (story 3.2b); og PR #67 flettes etter at spørsmålene om «Engine running» og «Cannot connect to the Docker daemon» er slått sammen til ett, fordi grunnen er den samme.

*Avgjort 2026-10-18 kl. 20:08 (gruppens svar, under instruksjonen kl. 19:51):* ordlista i `designregler.md` §4 gjelder vår tekst, ikke KI-teksten, til prompten får den. I PR-en for 3.4b ser testen for ordlista bort fra KI-teksten, med grunnen, og tekstene står som de ble (FR-604). Ordlista kommer inn i prompten i versjon 3, sammen med innstrammingen av «fordi», etter uka med logget drift som begynner mandag 19.10. Da lages tekstene i demoen på nytt.

*Avgjort 2026-10-18 kl. 20:39 (gruppens svar):* «Tester» står der den står, og får installasjonen av uv for Windows og Mac og hvor lang tid testene tar, i neste README-PR.

*Avgjort 2026-10-18 kl. 21:42 (gruppens svar):* bildet av oversikten tas høyere, så hele gruppen «Skilte seg ut» i tabellen er med, og PR #70 flettes etter det. Grunnen: i 1280 × 1000 slutter bildet der tabellen begynner, så signalstyrken og fargene per aksje er ikke med.

*Avgjort 2026-10-18 kl. 21:03 (gruppens svar):* hullet i kontrollen fra 3.4b rettes før byggestoppen mandag 19.10 kl. 20:40, så uka med logget drift går med den rettede kontrollen. Kontrollen i FR-603 leser da retningen og styrken også i formene Gemma skriver, som «Dette signalet er Negativt», «av typen Ingen» og «av styrke tre» (spesifikasjonen 10.2d). Prompten står, versjon 2.

*Avgjort 2026-10-18 kl. 21:46, 21:49 og 21:50 (gruppens svar):* 8.16 bygges i kveld etter PR #70 og 10.2d, og 8.17 flyttes ikke. Grafen får alle åtte knappene i `designregler.md` §2, som PRD-en sier (FR-201). «I går» (siste børsdag) og «Velg dag» viser 6 mnd fram til dagen, med dagen merket, endringen den dagen og signalet som er lagret for den.

*Avgjort 2026-10-18 kl. 22:06 (gruppens svar):* Selskap kan sorteres A til Å, og kolonnen tabellen er sortert på, får et lysere felt og en oransje strek under, som på designtavla, i en liten PR etter 8.16 i kveld (spesifikasjonen 8.15b). Grunnen: tavla har sorteringsmerket på Selskap, og i appen skiller bare fargen på vinkelen den sorterte kolonnen fra de andre.

*Avgjort 2026-10-18 kl. 23:03 (gruppens svar):* bildene av appen står bak en knapp rett under beskrivelsen, i en egen mappe for bilder og video, fordi appen endres hele tiden; de endelige bildene og videoen legges inn før innleveringen (spesifikasjonen 3.3f). Det endrer plassen fra svaret 18.10 kl. 00:20 og svar 4 i spesifikasjonen for 3.4 (11.10) om at bildene bare ligger i `docs/bilder/readme/`.

*Avgjort 2026-10-19 kl. 00:00 (gruppens svar):* når en dag er valgt med «Velg dag», viser hele aksjesiden den dagen: kortene øverst, «Hvorfor signalet ble», KI-teksten og grafen, lest fra det som er lagret for dagen, med et merke øverst og en lenke tilbake til siste børsdag (spesifikasjonen 8.16b). Grunnen: etter 8.16 viste toppen siste børsdag og linja over grafen den valgte dagen, to ulike signaler på samme side. Det utvider svaret 18.10 kl. 21:50.

*Avgjort 2026-10-19 kl. 12:06 (gruppens svar):* stilen flyttes til én CSS-fil nå, som første del av 2.7 (spesifikasjonen 2.7a), før 8.3 og historikken, fordi seks regler står likt i `index.html` og `aksje.html`, og kontrollpunktet i 2.7 sier én layout og én CSS-fil. Det erstatter svarene kl. 11:54 og 11:58 samme dag om at rammen skulle telle som felles stil til en egen PR senere i uka. Historikken blir 2.7b.

*Avgjort 2026-10-19 kl. 13:59 (gruppens svar):* grenene som er flettet, slettes på GitHub, og «Automatically delete head branches» slås på, så lista over grener bare viser arbeid som pågår. PR-ene beholder commitene, og en slettet gren kan hentes tilbake fra PR-en.

*Avgjort 2026-10-19 kl. 14:46 (gruppens svar):* README-en anbefaler demoen for faglærer og sensor, som briefen v8 og tilbakemeldingen 06.10 sier, og den lokale modellen merkes som valgfri. Det snur svaret 11.10 kl. 22:32 om å anbefale den ekte versjonen (`spec-3-4-demoversjonen.md`), og med det «den ekte versjonen er fortsatt anbefalt» i svaret 16.10 kl. 21:16 under story 3.3. Rekkefølgen i «Kom i gang» står. Det bygges i spesifikasjonen 3.3g.

*Avgjort 2026-10-19 kl. 14:48 (gruppens svar):* det briefen ikke lover, bygges på egen gren og flettes bare ferdig og grønt; det som ikke er ferdig ved funksjonsstoppen, flettes ikke. Funksjonsstoppen er README-prøven med ZIP-fila, senest én uke før innleveringen. Briefens suksessmål går foran: README-prøven, brukertesten, én ukes drift og en stabil demo.

*Avgjort 2026-10-19 kl. 16:12 (gruppens svar):* egne nøkler til Gemini, Anthropic og OpenAI (10.7) står i briefen v8 under «Data og kilder» og hører til v1. Svaret 18.10 kl. 00:39 står uten rettelse.

*Avgjort 2026-10-19 kl. 15:43 (gruppens svar):* endelig v1 er det briefen v8 lover: kjernen, KI-teksten med bryter, historikken, hovedindeksen, Min liste, lenken til investorsiden og egne nøkler til Gemini, Anthropic og OpenAI (10.7, briefen under «Data og kilder», gruppens svar kl. 16:12), og det som alt er flettet. Det PRD-en ellers har under «Inne i v1», også de femten «Fast i v1» fra 08.10, flyttes til «Ekstra, hvis tiden rekker» og bygges etter regelen kl. 14:48; det som ikke er flettet ved funksjonsstoppen, står som plan for en senere versjon. Grunnen: tilbakemeldingen 06.10 om at omfanget ikke skal vokse, og at planen skal beskrive den appen som leveres. Endringsforslaget er `sprint-change-proposal-2026-10-19.md`.

*Avgjort 2026-10-19 kl. 10:29 (gruppens svar):* 8.3 bygges i dag og flettes etter kveldens henting og måling; stjernen står både i oversikten og i Min liste; demoen starter med fem merket, den ekte med en tom liste.

### Epic 1: Dataene overlever en omstart, og historikken lagres slik at den kan leses tilbake (punkt 20)

Brukeren kan slå av maskinen og finne oversikten igjen — og spørsmålet «hva sa
løsningen om EQNR for to uker siden?» får et svar. *Rettet 2026-09-24:* i v1
er historikken lagret, men ikke besvarbar. Hvordan spørsmålet skal kunne
stilles, er åpent punkt 20 i `prd.md`. *Avgjort 2026-09-27:* historikken vises i aksjedetaljen, story 2.7 i Epic 2, fordi den trenger at webserveren leser basen (2.2) og at vurderingen skrives (2.5).

**FR-er:** FR-406, FR-408, FR-409 · **NFR-07** · **AD-er:** 3, 4, 5, 6, 7, 16, 17, 18, 19

`AD-19` binder rekkefølgen inne i epicen: `Kursrad` innføres i **samme endring**
som SQLite-adapteren. *Rettet 2026-09-24:* slik ble det ikke. `Kursrad` og porten
kom i 1.2 (`a796214`), SQLite-adapteren i 1.3 (`f4fada0`) og lesegrensen i 1.4a,
som i AD-19-rettelsen og spinens «Slik det ble». Konsumentene — `markedsoversikt`, `aksjedetalj`, `graf`,
`signalberegning` — oppdateres her, med full testkjøring mellom hvert steg. Det
er også her `kursdata.py` sitt I/O-brudd lukkes og `app.py` slutter å lese
snapshot utenom porten.

### Epic 2: Ferske data uten at kvoten sprenges

Brukeren kan hente nye kurser bevisst, og kan ikke ved uhell brenne dagskvoten.

**FR-er:** FR-401, FR-402, FR-403, FR-407 · **NFR-01, NFR-02** · **AD-er:** 2, 10, 17, 20 · *utvidet 2026-09-28 med 2.1b og 2.5:* 4, 5, 6, 7, 11, 16, 21 · *utvidet 2026-10-01 med 2.8, 2.9 og 2.9b:* FR-104, FR-105, FR-410, AD-15 · *utvidet 2026-10-07 med 2.10:* del av FR-203 · *utvidet 2026-10-08 med 2.11–2.14, endringsforslaget 08.10:* FR-412, FR-413, FR-414, tillegget til FR-409, tillegget til NFR-01, `AD-3`, `AD-13`, `AD-21` (endret)

De to kjente `AD-20`-feilene rettes her: `fetch_prices.main` som blander lokal
dato og UTC, og `meldinger._minutt` som kutter på tegn 16. FR-407 ligger her
fordi deteksjonen — avviket mellom `close`- og `adjusted_close`-endringen —
skjer på serien under henting, og den veien gjør kravet uavhengig av NewsWeb.

### Epic 3: Løsningen kan kjøres av andre enn oss

Sensor kan bygge og kjøre den, uten vår nøkkel og uten våre data.

**FR-er:** FR-401 (tom-tilstanden, story 3.3) · **AD-er:** 9, 10, 11, 12 · Dekker punkt 18, lukket 22.09 *(rettet 2026-09-26: her sto «Dekker åpent punkt 18»)* · *utvidet 2026-10-03 med 3.4:* FR-411, NFR-08, AD-7, AD-21

### Epic 4: KI kan tas i bruk uten å bryte godkjenningen

Låser opp KI-laget, og gjør at det kan være i drift over tid i stedet for å
bygges til slutt.

**FR-er:** FR-604, FR-605

Epicen deler seg i tre, med hver sin avhengighet:

| Del | Innhold | Avhengig av |
|---|---|---|
| **4.1** | Velg modelltjeneste, dokumentér betingelse 4 | **Ingenting.** Papirarbeid, fra dag én |
| **4.2** | `KILogg` som `Protocol` + minneimplementasjon + tester | **Ingenting.** Porten vet ikke om lagringsformen |
| **4.3** | SQLite-adapter for `KILogg` | **Epic 1** |

Story 4.1 krever tre svar per kandidat: brukes innsendte data til trening, kan
det slås av, og står det i **vilkårene** eller bare i markedsføringen.
**Betingelse 4 må være ført før artikkeltekst sendes inn i en modell** — en
story som sender inn tekst er *blokkert av* 4.1, ikke anbefalt etter den.

### Epic 5: KI-laget i drift 🔒

*Ute av v1 fra 2026-09-28 (plan B, punkt 1 i `prd.md` §8).* Storyene står som plan for en senere versjon.

**FR-er:** FR-602A, FR-603A, FR-604A, FR-606A, del av FR-203 · **NFR-04**

*Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.8), godkjent av Marian kl. 12:46:* her sto «FR-601, FR-602, FR-603, FR-606». Etter omskrivingen 05.10 gjelder FR-601–FR-603 KI-teksten i plan B (Epic 10), og FR-606 brukes ikke i v1. Det tabellen under sier om at «alle seks FR-6xx er om meldinger», gjelder A-variantene i `prd.md` §4.6A.

| Felt | |
|---|---|
| **Blokkert av** | Åpent punkt 5b (betingelse 4) **og åpent punkt 1 (Euronext)** |
| **Eier** | Gruppen |
| **Avgjøres** | Punkt 5b av Epic 4.1, som er ublokkert. Punkt 1 av Euronext — 28.09 er vår egen frist |
| **Ved nei fra Euronext** | **Epicen strykes i sin helhet.** Alle seks FR-6xx er om meldinger — FR-602 «meldingene i samlekategorien», FR-604 «for hver melding», FR-606 «melding i samlekategorien». Uten Epic 6 finnes ikke datagrunnlaget. **Da bortfaller også NFR-04**, og suksessmålet «KI-bidrag i drift» kan ikke nås, fordi PRD-en måler det i hvilke *meldinger* laget forklarte. Det som overlever er relevanseksperimentet, som henter fra EODHDs nyhets-API og ikke fra NewsWeb — KI kan da demonstreres, men ikke vises i drift *Endret 2026-09-23:* med plan B (**Epic 5B**) er KI i drift likevel mulig, men som en forklaring av signalet, ikke av meldinger. Det som strykes, er KI-laget over meldinger. Plan A og B utelukker ikke hverandre: kommer et ja senere, bygges plan A oppå 5B. *Rettet 2026-09-24:* NFR-04 bortfaller ikke heller, fordi Epic 5B begrenses av det. |

### Epic 10: KI forklarer signalet (plan B) 🔀

*Het Epic 5B til 28.09.* *Utløst 2026-09-28:* Euronext ga ikke tillatelse innen fristen, og epicen bygges i v1. Nummeret ble endret fordi BMAD-skriptet bare leser epics med hele tall.

KI legger en forklaring i naturlig språk oppå den regelbaserte forklaringen i
FR-706, for én aksje om gangen, i aksjedetaljen. Bare utledede verdier fra
kursdata, ikke innhold fra tredjeparter.

**Bidraget er forståelighet, ikke informasjon.** Med bare kursdata kan KI ikke
vite noe reglene ikke vet. Den kan si det slik at en person forstår det første
gang hun leser det. Det er et mindre bidrag enn forklaringen av meldinger ville
vært, og det skal stå slik.

| Felt | |
|---|---|
| **Utløses av** | Nei eller taushet fra Euronext 28.09 (åpent punkt 1 og 19) |
| **Avhenger av** | Epic 4.1 (betingelse 4 dokumentert), `KILogg` (4.2/4.3), 1.4a (`Kursleser`), og at oppfølgingspunktet om EODHD og plan B er avgjort (`docs/kilder-og-rettigheter.md`) |
| **Krav** | FR-601..606 skrives ikke om før 28.09. Blir plan B utløst, skrives de om da, med «forståelighet, ikke informasjon» i kravteksten |
| **Forhold til plan A** | Ikke enten–eller. Kommer et ja senere, bygges plan A oppå 5B, ikke i stedet for |

*Lagt til 2026-10-05:* 4.1 er ført, og oppfølgingspunktet om EODHD og plan B er
avgjort 04.10 (vi spør ikke). FR-601 til FR-607 er skrevet om etter valget av
tjeneste, og FR-608 er ny. Epicen har fått 10.7 (egen nøkkel) og 10.8 (ChatGPT,
kandidat til v1.1).

*Lagt til 2026-10-13, endringsforslaget 13.10 (punkt 4.8, svar 17), godkjent av Marian kl. 12:46:* **FR-er:** FR-601, FR-602, FR-603, FR-607, FR-608. 10.2 oppfyller FR-603, 10.3 oppfyller FR-601 og FR-602, 10.6 oppfyller FR-607, og 10.7 og 10.8 oppfyller FR-608.

### Epic 6: Børsmeldinger i oversikten 🔒

*Ute av v1 fra 2026-09-28 (plan B, punkt 1 i `prd.md` §8).* Storyene står som plan for en senere versjon.

**FR-er:** FR-404, FR-405, FR-501, FR-502, FR-503, del av FR-203

| Felt | |
|---|---|
| **Blokkert av** | Åpent punkt 1 — Euronext forbyr automatisert henting uten tillatelse på forhånd |
| **Eier** | Gruppen |
| **Avgjøres** | Forespørsel sendt 21.09, ubesvart. **28.09** er vår egen frist for å ta stilling uten svar |
| **Ved nei** | Strykes i sin helhet — **og tar Epic 5 med seg ned.** Det er ikke en fri strykning: den koster hele KI-laget, NFR-04, to av tre deler av FR-203, og suksessmålet «KI-bidrag i drift». Logikken i `meldinger.py` er bygget og testet fra før, og blir liggende som kode uten datakilde *Endret 2026-09-23:* det tar KI-laget **over meldinger** med seg ned, ikke hele KI-laget. Epic 5B står igjen. *Rettet 2026-09-24:* NFR-04 blir også stående, fordi Epic 5B begrenses av det. |

### Epic 7: Kommende finansielle hendelser 🔒

*Ute av v1 fra 2026-09-28 (plan B, punkt 1 i `prd.md` §8).* Storyene står som plan for en senere versjon.

**FR-er:** FR-301, FR-302, FR-303, del av FR-203

| Felt | |
|---|---|
| **Blokkert av** | Åpent punkt 1 (Euronext) og 12 (horisont og hendelsestyper) *(rettet 2026-09-27: her sto også «3 (kilde for handelskalenderen)». Punkt 3 gjelder hvilke dager børsen er åpen, ikke finanskalenderen, og er lukket 27.09)* |
| **Eier** | Gruppen |
| **Avgjøres** | Samme frist som Epic 6 |
| **Ved nei** | Strykes. Tar ingenting med seg ned — ingen annen epic leser kalenderen. Krever dessuten en manuelt vedlikeholdt oppslagstabell, siden kalenderen verken oppgir ticker eller ISIN |

### Epic 8: Tydelig for den som ikke har bygget den

En person utenfor gruppen forstår begge skjermbildene uten hjelp, og designet er
vurdert, ikke bare arvet fra kravene.

**FR-er:** ingen nye. Prøver FR-101–103, FR-201–204 og FR-706 fra utsiden ·
**NFR-05, NFR-06** · Oppfyller suksessmålet «Brukerutfall» (PRD §7)
*Lagt til 2026-10-07, Marians beslutning kl. 23:11:* story 8.5 oppfyller endringen i NOK i FR-101 og del av FR-203 (høy og lav i aksjedetaljen).
*Lagt til 2026-10-08, endringsforslaget 08.10, godkjent av Marian kl. 08:04:* story 8.6–8.18 oppfyller FR-106, FR-107, FR-108, FR-109, FR-110, FR-206, FR-207 og tilleggene til FR-101, FR-102, FR-201, FR-202 og FR-407, og ferdige lister i FR-412. «FR-er: ingen nye» over gjelder ikke lenger. Epic 8 er den største epicen, med 21 storyer.

Egen epic og ikke en del av Epic 3: Epic 3 har ett utfall — at løsningen kan
bygges og kjøres av andre — og brukertesten skal ikke vente på Dockerfilen.

### Epic 9: Dokumentasjon av prosessen

Sensor kan se hvordan KI ble brukt og hvordan koden er kvalitetssikret, uten å
lese git-loggen. Emnesiden legger dette under prosjektkoden (70 %): «Dokumentasjon
må vise hvordan KI ble brukt, og hvordan studentene har kvalitetssikret koden».

**FR-er:** ingen · Avhengigheter: 9.1 etter Epic 1; 9.2 og 9.3 ingen; 9.4 uke 39–40

---

# Stories

72 stories. Hver bærer hvilket krav den oppfyller, hvilke `AD`-er som begrenser
den, hva kontrollen faktisk ser etter, og om den kan gjøres ferdig i én økt.
*Rettet 2026-09-26:* her sto 42. Tallet er telt fra overskriftene «### Story».
*Rettet 2026-09-27:* her sto 46. Story 9.0 kom til 27.09.
*Rettet 2026-09-29:* her sto 47. Siden 27.09 har 1.8, 1.9, 2.1b, 2.1c, 2.7, 8.0,
9.5 og 10.5 kommet til. 10.1–10.4 er 5B.1–5B.4 med nytt navn, ikke nye.
*Rettet 2026-10-05:* her sto «55 stories». Siden 29.09 har 2.2b, 2.3b, 2.8, 2.9,
2.9b, 3.4, 3.4b, 8.0b, 8.0c, 8.3, 8.4, 10.6, 10.7 og 10.8 kommet til, og ingen er fjernet.
*Rettet 2026-10-06:* her sto «69 stories». Story 9.6 kom til 06.10.
*Rettet 2026-10-07:* her sto «70 stories». Story 2.10 og 8.5 kom til 07.10.
*Rettet 2026-10-08:* her sto «72 stories». Story 2.11–2.14 og 8.6–8.18 kom til
08.10 med endringsforslaget (`sprint-change-proposal-2026-10-08.md`), og det er
89. Forslaget sa først 87, før rad 12 ga 2.14 og 8.18.

**«Ville feilet hvis» er kontrollen.** Resten er beskrivelse. En story uten den
linjen er ikke ferdig spesifisert.

---

## Epic 1: Dataene overlever en omstart

*Lukket 2026-09-28:* alle storyene, 1.1–1.9 med 1.4a–1.4c og 1.5b, er flettet. Funnene fra kodegjennomgangen av Epic 1 (`kodegjennomgang-epic-1.md`) er rettet i 1.8 og 1.9 eller lagt til 2.1, 2.5 og 4.0. Verken appen eller hentingen bruker basen ennå. Det avgjøres når Epic 2 planlegges (innledningen til Epic 2).

Rekkefølgen inne i epicen er bundet av `AD-19`.

### Story 1.1: Migrasjonsløperen og `skjema_versjon`

Som **utvikler på laget**, vil jeg ha én vei å endre skjemaet på, så vi to ikke
bygger hver vår `ALTER TABLE` og basen slutter å være den samme hos begge.

**Oppfyller:** — *(infrastruktur for FR-406, FR-408)* · **Begrenses av:** `AD-16`, `AD-4`

**Kontroll — hva testen ser etter:**
- En tom base kjøres opp til nyeste versjon, og `skjema_versjon` viser riktig tall
- Samme migrasjon kjørt to ganger endrer ingenting andre gang
- **En migrasjon som feiler midtveis etterlater `skjema_versjon` uendret.** Testen skriver en migrasjon som med vilje feiler etter første setning, kjører den, og leser versjonsraden: den skal stå på tallet fra før. Skjemaet skal heller ikke være halvveis endret
- Løperen kan kalles **to ganger fra samme prosess** uten å endre oppførsel
- **Ville feilet hvis:** løperen brukte `executescript()`. Den gjør en implisitt `COMMIT` før den kjører noe, så den nærliggende måten å kjøre en `.sql`-fil på er **ikke** atomisk sammen med oppdateringen av `skjema_versjon`. Feilen er stille: skjemaet er halvveis endret mens versjonsraden sier at ingenting skjedde, og neste kjøring prøver den samme migrasjonen på nytt mot en base som alt er delvis migrert

**To ting storyen ikke skal avgjøre:**

| Åpent | Hvorfor 1.1 ikke lukker det | Hva som lukker det |
|---|---|---|
| **Hvem kjører migrasjonene, og når** | Storyen bygger løperen, ikke kalleren. `AD-16` sier at migrasjonene finnes, ikke hvem som anvender dem | **Story 3.1**, når Dockerfilen skrives. Merk at suksessmålet «Drift» krever at én kommando gjør hele hentingen — en egen `migrer`-kommando ville brutt det |
| **Skjemaendring på et uerstattelig lager** | 1.1 rører ikke `vurdering`. SQLite krever `DROP TABLE` for de fleste formendringer, og `AD-7` forbyr sletting gjennom porten uten å si om en migrasjon er unntatt | **Første migrasjon som rører `vurdering`** — tidligst etter story 1.6. Beslutningen tas da, ikke nå |

**Derfor skal løperen kunne kalles fra både hentekommandoen og webserverens
oppstart, uten å endres.** Den tar en tilkobling og en katalog med migrasjoner,
og gjør resten. Hvem som kaller den, er et valg Dockerfilen tar — ikke et valg
denne storyen tar ved å gjøre det ene enklere enn det andre.

**Og løperen skal ikke inneholde noe som foregriper det andre spørsmålet:** ingen
`DROP TABLE`-hjelpefunksjon, ingen «rebuild table»-mekanikk, ingen unntaksvei
for lagre `AD-7` verner. Trengs det, er det en beslutning som skal tas synlig.

**Én økt:** ja.

### Story 1.2: `Kursrad` og `Kurslager`-porten

Som **utvikler**, vil jeg at kursrader har navngitte norske felt, så en
feilstavet nøkkel blir en feil i stedet for `None`.

**Oppfyller:** — *(grunnlag for FR-406)* · **Begrenses av:** `AD-19`, `AD-3`, `AD-1`

**Kontroll — hva testen ser etter:**
- `Kursrad` har `dato`, `slutt`, `justert_slutt`, `volum` og avviser å bli konstruert uten dem
- `Kurslager`-protokollen har `erstatt_serie`, `serie` og `sist_hentet`, og **ingen** `legg_til_rad`
- En minneimplementasjon oppfyller protokollen og brukes av testene
- **Ville feilet hvis:** porten returnerte `list[dict]` med EODHDs engelske nøkler — da kunne en ny kilde bare passe inn ved å etterligne EODHDs feltnavn, og porten ville ikke lenger vært en port

*Endret 2026-09-23, før bygging:*
- **`sist_hentet(symbol) -> datetime | None`, i UTC (AD-20),** legges i porten nå og ikke i 1.4. Den settes av `erstatt_serie(symbol, rader, hentet)` i samme kall som serien byttes ut, så serie og tidsstempel kommer fra samme øyeblikk. Tidsstempelet er per symbol og ikke globalt, fordi AD-15 lar ett symbol feile og beholde sin gamle serie. Grunnen til å ta det nå: utsettes det, må porten endres to ganger, mens AD-19 sier at kjernen skal røres én gang. «Bare `erstatt_serie` og `serie`» var ment å holde `legg_til_rad` ute, ikke en lesemetode. Hvordan oversikten viser tidsstempelet, avgjøres i 1.4.
- **`Kursrad.dato` er `datetime.date`, ikke tekst.** En `date` kan ikke være feil formatert, og AD-20 sier at børsdagen er en kalenderdato. Adapteren oversetter.
- **`Kurskilde` blir stående ved siden av `Kurslager` til 1.4** (valg b). Det er et brudd på AD-3 så lenge det varer. En test hindrer at nye moduler tar `Kurskilde` i bruk. *Lukket 2026-09-25: story 1.4c fjernet `Kurskilde`, `MinneKilde` og testen, commit `a91ef79`.*

**Én økt:** ja.

### Story 1.3: SQLite-adapteren og `kurs`-tabellen

Som **bruker**, vil jeg at kursene finnes etter at maskinen har vært av, så
oversikten ikke er tom hver morgen.

**Oppfyller:** FR-406 · **Begrenses av:** `AD-4`, `AD-5`, `AD-16`, `AD-3`

**Kontroll — hva testen ser etter:**
- `erstatt_serie` på et symbol med eksisterende rader gir **nøyaktig** de nye radene, ikke de gamle pluss de nye
- Slettingen og innsettingen skjer i **én** transaksjon: en feil midtveis lar den gamle serien stå urørt
- `erstatt_serie` på ett symbol rører ikke de andre fjorten
- **Ville feilet hvis:** adapteren skjøtet på i stedet for å erstatte. Da ville `adjusted_close` blandet to justeringsgrunnlag etter første utbytte — og ingenting ville feilet, tallene ville bare vært gale
- `sist_hentet` byttes i samme transaksjon som radene: feiler innsettingen, står både gammel serie og gammel tid
- Serie og tid overlever at tilkoblingen lukkes og åpnes på nytt
- **En tom serie avvises** med `ValueError`, i begge lagre, og ingenting endres

*Endret 2026-09-23, før bygging:*
- **Adapteren er `src/lagring_sqlite.py`, klassen `SqliteKurslager`.** Den tar en
  `sqlite3.Connection`, ikke en filsti. Hvem som åpner basen og hvor fila ligger,
  avgjøres i skallet (1.5, 2.2, 3.1). Det er samme grense som for
  migrasjonsløperen.
- **1.3 lager den første migrasjonen, `src/migrasjoner/0001_kurs.sql`, og dermed
  katalogen.** Adapteren kjører ikke migrasjoner selv, og hvem som kaller
  `migrer`, er fortsatt 3.1s avgjørelse. Testene migrerer en tom base før de
  bruker adapteren.
- **`sist_hentet` lagres i en egen tabell, `kursserie(symbol PRIMARY KEY, hentet)`,**
  med én rad per symbol, skrevet i samme transaksjon som `kurs`-radene byttes
  ut. Kursradene byttes ut i sin helhet, mens tidsstempelet hører til symbolets
  serie og ikke til radene. Tabellen heter ikke `aksje`, fordi navn og sektor
  allerede har ett sted, `AKSJEUNIVERS`.
- **Adapteren oversetter ved grensen.** `Kursrad.dato` lagres som `YYYY-MM-DD`,
  og `hentet` som ISO 8601 med UTC-offset. Begge leses tilbake som `date` og
  `datetime` i UTC. Ingen tekst slipper ut av porten.
- **Kontrakttestene fra 1.2 kjøres mot både `MinneKurslager` og
  `SqliteKurslager`,** slik at de to beviselig oppfører seg likt.
- **En tom serie avvises i porten.** `erstatt_serie(symbol, [], t)` gir
  `ValueError` i begge lagre, og ingenting endres. AD-5 sier at hver henting
  dekker minst 175 handelsdager, så ingen lovlig kaller sender en tom liste. Den
  eneste veien dit er en feil et sted før porten, og da ville porten stille
  slettet symbolets historikk og satt et ferskt tidsstempel på ingenting. Det er
  samme feilklasse som AD-15 finnes for: en feil som ser ut som suksess.
  `MinneKurslager` fra 1.2 endres tilsvarende.

**Én økt:** ja.

**Story 1.4 er delt i 1.4a–c.** *Skrevet om 2026-09-23, før bygging.* Den gamle
teksten var én story merket
«Én økt: nei». Rettet: testtallet er 253 per 23.09, ikke 166. *24.09: 285, telt
ved å kjøre testene.* Mellomtilstanden
den advarte mot — porten lover `Kursrad` mens `SnapshotKilde` gir `dict` —
oppstod ikke, fordi valg b i 1.2 holdt `SnapshotKilde` utenfor `Kurslager`.
«Fem moduler» er erstattet med filene ved navn. Tre ting manglet: hvor appen
får `Kursrad` fra, fjerningen av `Kurskilde`, og visningen av `sist_hentet`.

### Story 1.4a: Lesegrensen — `Kursleser` og oversetteren fra øyeblikksbildet

Som **utvikler**, vil jeg at konsumentene kan få `Kursrad` fra øyeblikksbildet
uten at `SnapshotKilde` får en skrivemetode, så 1.4b har noe å lese fra.

**Oppfyller:** — *(grunnlag for FR-406 og FR-101)* · **Begrenses av:** `AD-3`,
`AD-7`, `AD-19`, `AD-20`

**Kontroll — hva testen ser etter:**
- `Kursleser` er en `Protocol` med `serie` og `sist_hentet`. `Kurslager` er
  `Kursleser` pluss `erstatt_serie`. Kontrollert på protokollene
- `SnapshotLeser` pakker inn `SnapshotKilde` og gir `Kursrad`, og `sist_hentet`
  i UTC. `SnapshotKilde` får ingen skrivemetode
- EODHDs feltnavn oversettes ett sted: `kursrad_fra_eodhd(rad)`. Epic 2 bruker den
  samme funksjonen når hentingen skriver til basen
- Lese-kontrakttestene kjøres mot tre lagre: `MinneKurslager`, `SqliteKurslager`
  og `SnapshotLeser`
- Et symbol med en rad som ikke kan oversettes, behandles som manglende: tom
  serie og ingen tid, og symbolet navngis for brukeren som manglende (AD-15). De
  andre symbolene leses som vanlig. Oversetteren tvinger aldri en rad gjennom
  ved å gjette. Dagens øyeblikksbilde har ingen slike rader: 3 735 rader og null
  manglende felt, kontrollert 23.09
- En EODHD-rad med NaN eller uendelig i `close` eller `adjusted_close` er en rad
  som ikke kan oversettes, og behandles likt (AD-15). Det samme gjelder feil
  type, et tall for stort for `float`, kurs på null eller under og negativt
  volum. `Kursrad` reiser `UgyldigKursrad` for alle disse fra 24.09.
  Oversetteren fanger `UgyldigKursrad` og `KeyError` (manglende felt), og har
  ingen egen sjekk av verdiene. *Rettet 2026-09-24:* her sto før at
  oversetteren skulle fange `ValueError`. `Kursrad` reiste også `TypeError` og
  `OverflowError`, og de ville sluppet gjennom
- Datoen parses strengt: en dato godtas bare hvis `dato.isoformat()` er lik
  teksten. Det avviser «2026-9-1», «20260921» og «2026-W39-1». En umulig
  dato som «2026-09-31» feiler allerede i parsingen. *Rettet 2026-09-24:* her
  sto `datetime.strptime(tekst, "%Y-%m-%d")` alene. Den godtar «2026-9-1», og
  `date.fromisoformat` godtar «20260921» og «2026-W39-1», prøvd 24.09
- **Ingen konsument røres.** Hele testsettet er grønt, og tallet telles før og
  etter
- **Ville feilet hvis:** oversetteren falt tilbake fra `adjusted_close` til
  `close` når feltet manglet. Det er fallbacken AD-19 finnes for å fjerne: den
  gir et tall som ser riktig ut, men er regnet på feil serie

**Merknad: lesekontrakten kan ikke kjøres uendret mot `SnapshotLeser`.**
*Lagt til 2026-09-24.* Kontrakttestene i `test_kurslager.py` fyller lageret med
`erstatt_serie`, og den har ikke `SnapshotLeser`. Testen for tid per symbol
(`TestSistHentet.test_er_per_symbol`) krever to ulike tider, mens
`SnapshotKilde` har én tid per fil. Løsning:
- En leser-fixture med én fyllefunksjon per lager. For `MinneKurslager` og
  `SqliteKurslager` kaller den `erstatt_serie`, for `SnapshotLeser` bygger den
  et øyeblikksbilde
- Tester som krever ulike tider per symbol, kjøres bare mot de to skrivbare
  lagrene
- Egne lesetester for det alle tre skal oppfylle: en tom serie gir
  `sist_hentet` `None`, og `serie` gir sorterte, unike datoer

**Én økt:** ja.

### Story 1.4b: Konsumentene leser `Kursrad`

Som **utvikler**, vil jeg at kjernen slutter å røre `dict`-nøkler, så `AD-19`
gjelder hele veien og ikke bare ved porten.

**Oppfyller:** — *(fullfører FR-406)* · **Begrenses av:** `AD-19`, `AD-1`, `AD-3`

**Kontroll — hva testen ser etter:**
- `signalberegning`, `markedsoversikt` og `aksjedetalj` tar `Kursrad` og leser
  gjennom `Kursleser`. `graf.py` får `dato` som `date`
- `app.py` gir konsumentene `SnapshotLeser` i stedet for `SnapshotKilde`
- Ingen av de fire kjernemodulene importerer `sqlite3`, `pathlib` eller
  `Kurskilde`
- Hele testsettet er grønt. Tallet telles før og etter og føres i
  commit-meldingen, det antas ikke
- **Ville feilet hvis:** en konsument regnet på `slutt` der den skal regne på
  `justert_slutt`. Kontrolleres med en serie der de to spriker (et utbytte), og
  med en mutant som bytter `justert_slutt` med `slutt` i `signalberegning`. Den
  feilen bryter FR-701 stille
- *Lagt til 2026-09-25:* kontrollregning på ekte data. Markedsoversikten og de
  15 aksjedetaljene bygges fra samme øyeblikksbilde før og etter endringen, og
  tallene skal være like. Utfallet føres som antall like rader, uten verdiene
  (regel 16). Ingen API-kall

**Omfang, telt 23.09:**
- 11 `dict`-oppslag: `signalberegning` 2, `markedsoversikt` 3, `aksjedetalj` 6
- To typeannotasjoner i `graf.py:39–40`, og koblingen i `app.py`
- I testene: de fire `serie()`-hjelperne og 32 `MinneKilde`-kall (`test_app` 17,
  `test_aksjedetalj` 8, `test_markedsoversikt` 7). De tre i `test_kursdata`
  tester `MinneKilde` selv og fjernes i 1.4c

**Kan ikke deles videre.** `beregn_signal` kalles av både
`markedsoversikt.bygg_rad` og `aksjedetalj` med de samme radene. Endres én av
dem uten de andre, må det ligge en midlertidig oversettelse fra `dict` til
`Kursrad` mellom dem. En midlertidig oversettelse er nettopp stedet der en
fallback fra justert til ujustert kurs kan gjemme seg. Grensen går derfor rundt
alle tre, pluss `app.py`, som kobler dem til kilden.

**Forutsetning** *(fra gjennomgangen av 23.09, lagt til 2026-09-24)*:
testhjelperne `serie()` i `test_app.py:23`, `test_markedsoversikt.py:31` og
`test_signalberegning.py:56` lager datoen som `f"2026-09-{…:02d}"`. En serie
med mer enn 30 rader gir datoer som «2026-09-31» og høyere. Talt 24.09 ved å
kjøre testene: `test_app` lager 50 slike datoer (til og med «2026-09-80»),
`test_signalberegning` 21, `test_markedsoversikt` ingen, fordi ingen av
seriene der er lengre enn 30. I dag går det bra fordi datoene er tekst:
`aksjedetalj._innenfor_vindu` (`aksjedetalj.py:121–134`) fanger `ValueError`
fra `date.fromisoformat` og faller stille tilbake til hele serien eller hopper
over raden. Når konsumentene leser `Kursrad`, vil de ugyldige datoene feile
eller behandles som manglende. De tre hjelperne byttes derfor til `date` +
`timedelta`, slik `test_aksjedetalj.py:20` gjør, i en egen commit før 1.4b.

**Én økt:** nei, dette er den største. Kodeendringen er liten, testendringen er
det ikke.

### Story 1.4c: Rydding — `Kurskilde` ut, `sist_hentet` inn

Som **gruppe**, vil vi at bruddet på AD-3 lukkes og at oversikten sier hvor
gamle dataene er, så ingen leser en foreldet rad som dagens.

**Oppfyller:** FR-101 *(endret 2026-09-23)* · **Begrenses av:** `AD-3`,
`AD-15`, `AD-20`

**Kontroll — hva testen ser etter:**
- `Kurskilde`, `MinneKilde` og `TestKurskildeErPaaVeiUt` er fjernet. Det finnes
  ingen referanse til dem i `src/` eller `tests/`
- Sidens tidsstempel er det **eldste** `sist_hentet` blant symbolene som vises
- En rad med eldre `sist_hentet` enn den nyeste viser sitt eget tidsstempel på
  raden, uten en sjette kolonne
- Tidsstempler vises i norsk tid (AD-20: lagret i UTC)
- Spinen og `epics.md` er i takt: AD-3-bruddet er merket lukket, med commit
- **Ville feilet hvis:** sidens tidsstempel var det nyeste. Da ser en side med én
  fersk rad og fjorten foreldede ut som fersk

**Én økt:** ja.

### Story 1.5: `SnapshotKilde` ut av `kursdata.py`

Som **utvikler**, vil jeg at portmodulen slutter å lese filer, så laginndelingen
i spinen beskriver koden og ikke bare ønsket.

**Oppfyller:** NFR-07 · **Begrenses av:** `AD-6`, `AD-2`, `AD-1`

**Kontroll — hva testen ser etter:**
- `kursdata.py` importerer verken `json` eller `pathlib`
- `app.py` kaller ikke `nyeste_snapshot()` direkte — den går gjennom en port
- `nyeste_snapshot` velger fortsatt på dato alene, og `KURSPREFIKS` vinner ved lik dato
- **Ville feilet hvis:** flyttingen tok med seg sammenligningen over tuplene `(dato, sti)`. Den falt tilbake på stien ved lik dato, og da vant `signaltest-` over `kurser-`

**Én økt:** ja.

### Story 1.5b: Migrasjonsløperen og SQLite-adapteren herdes

*Lagt til 2026-09-24.* Kontrollpunktene er forutsetningene a–h, som sto under
1.6. De er flyttet hit ordrett.

Som **utvikler**, vil jeg at løperen og adapteren tåler den neste migrasjonen,
så `0002` ikke kan kjøres feil, halvveis eller mot en katalog som er endret.

**Oppfyller:** — *(grunnlag for FR-408, som trenger `0002`)* · **Begrenses av:**
`AD-16`, `AD-5`, `AD-7`

**Kontroll — hva testen ser etter:**

**Forutsetninger før neste migrasjon** *(fra kodegjennomgangen 2026-09-23,
hver prøvd mot koden samme dag)*. Ingen av dem slår ut i dag, fordi det bare
finnes én migrasjon. Alle åtte må være på plass før `0002` skrives. *e–h lagt
til 2026-09-24, fra gjennomgangen av 23.09, og prøvd mot koden 24.09:*

- **a) `migrer()` sammenlikner bare antall.** Filnavnene lagres i
  `skjema_versjon`, men sammenliknes ikke. Prøvd: en base som har kjørt
  `0002_min.sql`, godtar en katalog med `0002_din.sql`, og `0002_din` kjøres
  aldri. Løperen skal avvise en katalog der et anvendt nummer har fått nytt
  filnavn.
- **b) En `COMMIT` i migrasjonsfila avslutter transaksjonen for tidlig.**
  Resten av fila kjøres uten den. Prøvd: `CREATE TABLE foer; COMMIT; CREATE
  TABLE etter; <ugyldig>` etterlater `foer`, `etter` og `skjema_versjon` med
  versjon 0, **mens feilmeldingen sier «rullet tilbake»**. Neste kjøring stopper
  på `table foer already exists`. `_kjoer()` skal sjekke `in_transaction` etter
  hver setning og avvise fila hvis transaksjonen er borte.
- **c) `SqliteKurslager` godtar en base på versjon 1** selv om katalogen har flere
  migrasjoner, fordi den bare sjekker `versjon < 1`. Adapteren skal kreve siste
  versjon.
- **d) Tilbakerullingen er ikke testet for feil i siste steg,** skrivingen til
  `kursserie`. Den er bare testet for feil midt i kurs-radene (like datoer).
  Koden er riktig i dag. Prøvd med trigger: serie og tid står uendret. Men
  ingen test holder den riktig. Testen bruker `RAISE(ABORT)` i triggere på
  **både** `INSERT` og `UPDATE` på `kursserie`, fordi `erstatt_serie` gjør
  `ON CONFLICT DO UPDATE` når symbolet finnes fra før. **Ville feilet hvis:**
  `COMMIT` lå før skrivingen til `kursserie`. Da får symbolet ny serie med
  gammel tid.
- **e) En kjørt migrasjonsfil som endres i ettertid, oppdages aldri.** Prøvd:
  en base som har kjørt `0001_a.sql`, godtar samme fil med helt annet innhold,
  og `migrer()` returnerer 1 uten feil. `skjema_versjon` skal lagre sha256 av
  filinnholdet, og løperen skal avvise katalogen hvis en kjørt fil er endret.
  Billigst nå, før noen ekte base finnes.
- **f) `migrer()` leser versjonen før transaksjonen starter,** og `BEGIN` er
  utsatt (deferred). Feilmeldingen regner ut versjonen (`nummer - 1`) i stedet
  for å lese den. Hentekommandoen og webserverens oppstart kan migrere
  samtidig. Prøvd med to tilkoblinger: A leser versjon 0, B migrerer til 1, og
  A kjører så `0001` og får «table a already exists … Basen staar paa versjon
  0», mens basen står på 1. Løperen skal bruke `BEGIN IMMEDIATE` og lese
  versjonen på nytt inne i transaksjonen.
- **g) Katalogkontrollen har tre hull.** Prøvd:
  - `glob("*.sql")` skiller store og små bokstaver på Linux og hopper stille
    over `0002_ny.SQL`. På Windows tar `glob` den med, og `FILNAVN` avviser
    den. Samme katalog oppfører seg altså ulikt på de to plattformene
  - En fil med nummer `0000` gir en villedende melding: `0000` og `0001` gir
    «Migrasjon 0002 mangler»
  - En tom katalog gir versjon 0 uten feil
- **h) To tester lover mer enn de sjekker.** «lar tom base være tom»
  (`test_migrering.py:174`) bruker `tabeller()`, som filtrerer bort
  `skjema_versjon`. «umigrert base … får ingen tabeller»
  (`test_lagring_sqlite.py:119`) sjekker bare versjonen. Begge skal sjekke
  `count(*)` i `sqlite_master`.

- **Ville feilet hvis:** `0002` ble skrevet før a–h var på plass. Da kjøres
  den første migrasjonen på en uerstattelig tabell av en løper som ikke
  oppdager et nytt filnavn, en endret fil eller en `COMMIT` midt i fila

**Én økt:** ikke vurdert. Åtte kontrollpunkter.

*Ferdig 2026-09-26:* flettet i `ef1cca7`, PR #5.

### Story 1.6: `Vurderingslager` med datoavvisning

Som **utvikler på laget**, vil jeg ha et `Vurderingslager` som **nekter** å
skrive en eldre dato, så historikken ikke kan skrives om i ettertid uten at noen
har bestemt det.

**Oppfyller:** FR-408 · **Begrenses av:** `AD-3`, `AD-7`, `AD-18`, `AD-20`

**Kontroll — hva testen ser etter:**
- `skriv` med en dato før inneværende børsdag **reiser** — den logger ikke og
  hopper ikke stille over. Testen injiserer klokka, så den ikke avhenger av
  hvilken dag den kjøres. *Rettet 2026-09-24:* her sto «gårsdagens dato». En
  lørdag er gårsdagen inneværende børsdag, og regelen i spinen er at `skriv`
  avviser enhver dato som ikke er inneværende børsdag
- `skriv` to ganger med samme `(symbol, dato)` gir **én** rad, og den siste vinner
- Porten har **ingen** `slett` og **ingen** `endre` — kontrollert på protokollen, ikke på implementasjonen
- En `vurdering` overlever `erstatt_serie` på samme symbol: kursverdiene i raden er uendret etterpå
- `vurdering`-tabellen opprettes av en nummerert migrasjon, `0002`, slik 4.3
  har for `ki_logg` *(lagt til 2026-09-24)*
- `vurdering` har plass til en rad med grunn i stedet for vurdering, og `skriv`
  lar aldri en rad med grunn skrive over en rad med vurdering samme dag *(lagt
  til 2026-09-27, punkt 24)*
- **Ville feilet hvis:** noen la til en `oppdater`-metode «for migrasjoner», eller hvis datogrensen ble regnet i UTC — da ville en kjøring 00:30 norsk tid (22:30 UTC dagen før) skrevet på
  gårsdagen. *Rettet 2026-09-24:* her sto 23:30. Det er samme dato i UTC og
  avslører ingenting. Feilvinduet er 00:00–02:00 norsk sommertid (00:00–01:00
  om vinteren), og 00:30 ligger i begge

**Forutsetning:** story 1.5b er ferdig, og åpent punkt 3 er avgjort (`prd.md`:
«Definisjonen må være avgjort før story 1.6»). `0002` skrives ikke før
migrasjonsløperen og SQLite-adapteren er herdet. *Flyttet 2026-09-24:
forutsetningene a–h sto her og er nå kontrollpunktene i 1.5b.* *Lagt til
2026-09-26: punkt 3, som PRD-en og Epic 1-konteksten alt krever.* *Oppfylt
2026-09-27:* punkt 3 er lukket (`prd.md` §8). Lista og funksjonen bygges i
denne storyen. *Punkt 24 lukket 2026-09-27:* svaret bestemmer formen på
`vurdering`, derfor før denne storyen (`prd.md` §8).

**Én økt:** ja.

*Ferdig 2026-09-27:* flettet i `7dc8a48`, PR #8.

### Story 1.7: De tre tilstandene skilles

Som **gruppe som skal forsvare tallene**, vil jeg kunne skille en dag uten
utslag fra en dag vi ikke kjørte, så et hull i vår egen drift ikke blir lest som
et funn om markedet.

**Oppfyller:** FR-409 · **Begrenses av:** `AD-7`, `AD-20`

**Kontroll — hva testen ser etter:**
- En rad med styrke 0 leses som **et svar**, ikke som fravær
- En manglende rad på en børsdag leses som «kommandoen ble ikke kjørt»
- En manglende rad på en ikke-børsdag leses som «dagen finnes ikke»
- De tre returnerer **tre forskjellige** verdier, ikke to og en `None`
- En rad med grunn leses som en rad: kommandoen kjørte, men kunne ikke vurdere
  aksjen. Den leses ikke som styrke 0 og ikke som fravær *(lagt til 2026-09-27,
  punkt 24)*
- **Ville feilet hvis:** lageret svarte `None` både for «ikke kjørt» og «ikke børsdag». Da er de to umulige å skille, og skillet kan ikke gjenskapes i ettertid
  *Løst slik 27.09 (spesifikasjonen for 1.7):* lageret svarer fortsatt `None` for begge, og `tilstand` skiller dem med kalenderen i `boersdag.py`. Skillet kan gjenskapes så lenge kalenderen dekker året (punkt 25 i `prd.md` §8).

**Forutsetning** *(lagt til 2026-09-24)*: «ingen rad på en børsdag betyr at
kommandoen ikke ble kjørt» holder ikke i to tilfeller. Kommandoen kan ha kjørt
før dagens kurs var publisert (åpent punkt 23 *(avgjort 28.09)*), og et symbol kan ha feilet mens
de andre ble hentet (`AD-15`). Begge gir ingen rad, uten at det er et hull i
driften. Ført som **åpent punkt 24** i `prd.md`, med frist før denne storyen:
en fjerde tilstand, eller en lagret grunn. *Oppfylt 2026-09-27:* punkt 24 er
lukket med en rad med grunnen (`prd.md` §8).

**Én økt:** ja.

*Ferdig 2026-09-27:* flettet i `5e9e6ad`, PR #9.

### Story 1.8: Hentingen godtar bare det leseren kan lese

*Lagt til 2026-09-27, fra kodegjennomgangen av Epic 1 (G1).*

Som **gruppe**, vil vi at en aksje hentingen melder som hentet, også kan leses, så ingen aksje forsvinner fra oversikten uten at noe er ført.

**Oppfyller:** — *(retting etter punkt 22 i `prd.md` §8)* · **Begrenses av:** `AD-15`, `AD-19`

**Grunnen:** `_riktig_form` i `fetch_prices.py` sjekker bare at feltene finnes og at `date` er tekst, mens `SnapshotLeser` oversetter hver rad og avviser like datoer. Prøvd 27.09: `close` 0, `volume` 1000.0 eller en dato som går igjen gir en serie som lagres uten noe i `feil`, og som leseren dropper.

**Kontroll — hva testen ser etter:**
- Én funksjon avgjør om en serie fra EODHD kan leses, og både `SnapshotLeser` og `hent_universet` bruker den
- Hver slags rad leseren avviser, gir «svar med feil form» for symbolet, og de andre lagres likevel. Testene for leseren og hentingen tar radene fra samme liste
- `fetch_prices.py` kommer under strengvakten i `test_konsumentene.py`, så EODHDs feltnavn bare står i `eodhd.py`
- Øyeblikksbildet har samme format som før
- G2–G5 og G8: `len(AKSJEUNIVERS)` for 14 og 15, en nøkkel med mellomrom i testen for URL-koding, `SnapshotLeser` i docstringene, en test som binder `styrke` i `Vurdering` til `beregn_signal`, og testnavnet uten `versjon_1`
- **Ville feilet hvis:** hentingen og leseren hadde hver sin regel for en gyldig serie

**Forutsetning:** ingen.

**Én økt:** ja.

*Ferdig 2026-09-27:* flettet i `5c316e8`, PR #10.

### Story 1.9: Aksjene i basen, og tabellene peker på dem

*Lagt til 2026-09-27, fra prioriteringen samme dag.*

Som **gruppe**, vil vi at basen selv kjenner de femten, så en rad for et symbol utenfor universet avvises av basen, og historikken kan hentes sammen med aksjen i én spørring.

**Oppfyller:** — *(grunnlag for FR-408, og G10 i kodegjennomgangen)* · **Begrenses av:** `AD-4`, `AD-7`, `AD-16`, `AD-18`

**Grunnen:** migrasjonene lager fire tabeller, `kurs`, `kursserie`, `grunn` og `vurdering`, og ingen av dem har fremmednøkler. Ingen spørring henter fra flere tabeller. Assisterende hjelpelærer godtok SQLite 22.09 ut fra «relasjoner mellom data, joins, migrasjoner og logging av KI-vurderinger» (`AD-4`).

**Kontroll — hva testen ser etter:**
- `0003` lager `aksje` med de femten, og en test holder tabellen og `AKSJEUNIVERS` like
- En rad i `kurs`, `kursserie` eller `vurdering` for et symbol som ikke står i `aksje`, avvises av basen, også `EQNR.OL` (G10)
- En aksje med rader kan ikke slettes
- Ingen fremmednøkkel fra `vurdering` til `kurs` (`AD-18`)
- Planen velger fremmednøkkel eller trigger, med grunnen fra `0002`. Fremmednøkler på en kolonne som finnes, krever at tabellen bygges om, og det er billigst før den har data
- **Ville feilet hvis:** porten var eneste vakt

**Forutsetning:** før Epic 2 skriver til basen.

**Én økt:** ja.

*Ferdig 2026-09-28:* flettet i `cfe2977`, PR #11.

---

## Epic 2: Ferske data uten at kvoten sprenges

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* i v1 står 2.7, historikken, som briefen v8 lover. 2.4, 2.6, 2.10, 2.11, 2.12, 2.13 og 2.14 er «Ekstra, hvis tiden rekker», etter regelen kl. 14:48. Resten av epicen er flettet.

**Føringer fra kvotemålingen 2026-09-23** (`malinger.md` §11). De gjelder hele
epicen:

1. **Hentekommandoen skal nekte å hente to ganger samme børsdag, ikke bare
   unngå det.** Grunnen er målt: kall nummer 21 stopper ikke, men trekker
   stille fra bonuskvoten (`extraLimit` 485 → 484). Kontrollen mot forventet
   børsdag i FR-402 er dermed et **kvotevern**, ikke bare en datakontroll.
   Story 2.3 skal prøves mot det: en andre kjøring samme børsdag gjør null kall.
2. **Siste rad kan endres i etterkant.** MOWI 21.09 fikk volumet justert ned
   0,8 % ved neste henting, med sluttkursen uendret, fordi raden var hentet mens
   børsen var åpen. Det er
   en egen grunn til å erstatte i stedet for å skjøte, uavhengig av utbytter
   (AD-5). Det reiser et spørsmål epicen må svare på: **når på døgnet skal
   hentekommandoen kjøres**, når dagens kurs ikke var publisert kl. 19:04? Ført
   som **åpent punkt 23** *(avgjort 28.09)* i `prd.md`, med frist før story 2.1.
   *Avgjort 2026-09-28:* på børsdager mellom kl. 22:00 og midnatt, norsk tid.
   *Lagt til 2026-10-17:* mellom kl. 21:00 og midnatt fra 19.10 (beslutningen 16.10 kl. 21:09 under story 2.3,
   `malinger.md` §31).
   *Lagt til 2026-10-20:* mellom kl. 22:00 og midnatt fra 20.10 (gruppens svar 19.10 kl. 22:19 under story 2.3,
   `malinger.md` §37).

*Lagt til 2026-09-25, fra planen for 1.5:* Ingen story i Epic 2 har som
kontrollpunkt at hentekommandoen skriver kursene til basen gjennom
`Kurslager`, eller at webserveren leser dem derfra i stedet for fra
øyeblikksbildet. Skrivingen er forutsatt i 2.5 («Én kjøring skriver kurser
**og** vurderinger»), og lesingen i 2.2 («også når basen er tom», «hvordan
webserveren åpner basen»). Når Epic 2 planlegges, avgjøres det om de to blir
egne stories. Meldingen «Ingen kursdata funnet i `data/`» i `deferred-work.md`
hører til lesingen.

*Avgjort 2026-09-28 (endringsforslaget, `sprint-change-proposal-2026-09-28.md`):* skrivingen blir en egen story, 2.1b, og lesingen blir kontrollpunkter i 2.2. Rekkefølgen i epicen er 2.1, 2.1b og 2.5, så begynner de daglige kjøringene til basen, og deretter 2.3, 2.2, 2.7, 2.4 og 2.6. 2.5 er storyen som gjør at hentingen kan kjøres hver børsdag mellom kl. 22:00 og midnatt og skrive til basen.

*Lagt til 2026-09-29, avgjort av gruppen 28.09:* story 2.1c, der vurderingen lagrer målingene bak de tre sjekkene, kommer mellom 2.1b og 2.5. Rekkefølgen er da 2.1, 2.1b, 2.1c og 2.5, så begynner de daglige kjøringene. 2.1c må være ferdig før den første ekte raden skrives, fordi en rad aldri kan endres eller fylles inn etterpå (AD-7).

*Lagt til 2026-10-01, med hovedindeksen OSEBX i v1 (Marians beslutning):* rekkefølgen er 2.1, 2.1b, 2.1c, 2.5, de daglige kjøringene, 2.3, 2.8 (etter 4.3), 2.2, 2.9, 2.9b, 2.7, 2.4 og 2.6. De daglige kjøringene begynner rett etter 2.5 og venter ikke på 2.8: indeksen kan bygges fra siste øyeblikksbilde, som har et helt år (`DAGER_TILBAKE` i `fetch_prices.py`), men en vurdering kan ikke etterfylles (AD-7). Blir 4.3 utsatt, tas den før 2.8, fordi indeksen får `0006` etter `ki_logg` i `0005`. Ingen av de tre står på lista «Kan ikke kuttes», og blir det trangt, venter 2.9b først.

### Story 2.0: Hentingen lekker ikke nøkkelen og skriver ikke over et øyeblikksbilde

*Lagt til 2026-09-26, fra kontrollen av repoet.*

Som **gruppe**, vil vi at hentingen aldri viser eller lagrer API-nøkkelen, og
aldri skriver over et øyeblikksbilde, så en feilmelding ikke kan føre nøkkelen
inn i repoet, og så råfilene forblir uforanderlige.

**Oppfyller:** NFR-03 — *(og grunnlag for NFR-07)* · **Begrenses av:** `AD-6`,
`AD-12`, `AD-15`

**Grunnen:** `hent_ett_symbol` sender nøkkelen som `api_token` i adressen.
Feiler kallet, tar feilteksten fra `requests` med hele adressen, og
`hent_universet` både skriver den ut og lagrer den i `feil` i øyeblikksbildet
(`deferred-work.md`). Kontrollen 26.09 fant ingen lekkasje. `filnavn()` bruker
kjøredagen, og `main()` skriver med `write_text`, så en ny kjøring samme dag
skriver over dagens øyeblikksbilde. AD-6 sier at råfilene aldri skrives om.

**Kontroll — hva testen ser etter:**
- En feil fra `requests`, både en HTTP-feil og en tilkoblingsfeil, gir en
  feiltekst uten nøkkelen, både i utskriften og i `feil`. Testen bruker en falsk
  nøkkel og ingen nett
- Et øyeblikksbilde som finnes fra før, skrives ikke over
- Et svar med feil form gir feilen «svar med feil form» for det symbolet, og de
  andre symbolene hentes og lagres likevel *(lagt til 2026-09-26, valg A i
  planen)*
- **Ville feilet hvis:** feilteksten fra `requests` ble lagret uendret, eller
  fila ble skrevet uten at det var sjekket at den ikke fantes

**Forutsetning:** ingen. Storyen rører bare `src/fetch_prices.py` og testene for
den, og tas før neste henting.

**Én økt:** ja.

*Ferdig 2026-09-26:* flettet i `4b65a3c`, PR #6.

### Story 2.1: Børsdag i Oslo, tidsstempel i UTC

Som **utvikler**, vil jeg at «dagen» betyr én ting, så to verdier ikke kan være
enige og begge være feil.

**Oppfyller:** — *(grunnlag for FR-402, FR-408)* · **Begrenses av:** `AD-20`

**Kontroll — hva testen ser etter:**
- Filnavn og `hentet` i samme øyeblikksbilde utledes av **samme** øyeblikk
- En kjøring 00:30 norsk tid gir filnavn og tidsstempel som peker på samme dag
- `meldinger._minutt` går via et tidsobjekt, ikke en tegnavkorting
- To representasjoner av samme øyeblikk gir **samme** dublettnøkkel
- En test kjører `main()` uten nett, og øyeblikksbildet havner i datakatalogen med Oslo-datoen i navnet *(lagt til 2026-09-27, G12 i kodegjennomgangen av Epic 1)*
- **Ville feilet hvis:** rettingen bare gjorde filnavn og tidsstempel konsistente uten å si hvilken sone de er i. To verdier kan være enige og begge være feil

**Én økt:** ja. Retter de to kjente feilene fra `AD-20`.

*Ferdig 2026-09-29:* flettet i `27ae8e3`, PR #13.

### Story 2.1b: Basen åpnes ett sted, og hentingen skriver kursene dit

*Lagt til 2026-09-28, fra endringsforslaget (`sprint-change-proposal-2026-09-28.md`).*

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
  (FR-403, se 2.4)
- Leseren av øyeblikksbildene ser i `data/raa/`, så markedsoversikten og
  aksjedetaljen viser de samme kursene før og etter flyttingen. Til 2.2 er
  ferdig, leser webserveren fortsatt øyeblikksbildene, og `nyeste_snapshot`
  ser i dag bare i `data/`
- Et øyeblikksbilde som alt finnes, kan skrives til basen uten API-kall, samme
  vei som etter en henting. Det skriver bare `kurs`, aldri `vurdering` (AD-7).
  Det gir en test med ekte data uten kall, og en reserve til demonstrasjonen
  (punkt D i `docs/innlevering.md`). AD-6 forbyr å lagre filene i basen, ikke å
  lese kursene ut av dem
- Testen der to migratorer overlapper (`deferred-work.md`, utsatt til 3.1), tas
  her, fordi det er her to innganger får samme åpning
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
fra `data/` til `data/raa/`. Målingsfilene blir liggende. `data/` committes
aldri (regel 10).

**Avhenger av:** 2.1. **Én økt:** ja.

*Ferdig 2026-09-29:* flettet i `9aa6131`, PR #14.

### Story 2.1c: Vurderingen lagrer målingene bak de tre sjekkene

*Lagt til 2026-09-29, avgjort av gruppen 28.09.*

Som **gruppe**, vil vi at hver vurdering lagrer tallene sjekkene ble avgjort av,
så en vurdering kan etterprøves og sjekkes. Et fortegn uten måling kan ikke det
(FR-706).

**Oppfyller:** FR-408 (raden «Målingene») · **Begrenses av:** `AD-1`, `AD-7`,
`AD-13`, `AD-16`, `AD-18`

**Kontroll — hva testen ser etter:**
- Fire tall lagres i `vurdering`, uavrundet og som brøk, i samme enhet som
  regelen regner i: `trend_avvik`, `dagens_endring`, `standardavvik` og
  `volumforhold`. Volumet lagres som forholdstall mot medianen, ikke som to
  volumtall
- Én funksjon avrunder, og visningen i FR-706, grunnlaget i 10.1 og kontrollen i
  FR-603 bruker den alle tre: én desimal for prosent og to for forholdstallet
- `Sjekk` får `maaling` og `grense`. Bare bevegelse har en grense som varierer
  (standardavviket). `forklaring` lages av de to feltene, og teksten for
  interesse blir forholdstallet i stedet for to volumtall
- Regelen for interesse avgjør med forholdstallet, så det lagrede tallet er det
  som avgjorde. Er medianvolumet 0, er `volumforhold` `None`, og interesse er 0
- Testene for `signalberegning` står uendret og er grønne. En ny test viser at
  regelen, brukt på `maaling` og `grense`, gir samme verdi som sjekken for hver
  av de tre
  *Rettet 2026-10-01:* tre tester fra 8.0 sjekket den gamle teksten for
  interesse og er byttet ut, fordi teksten følger FR-706. Resten står uendret.
- En kontrollregning på det nyeste øyeblikksbildet i `data/`, før og etter, som
  i 1.4b–1.5: styrke, retning og de tre verdiene er like for alle 15, og bare
  teksten for interesse skiller. Skifter noen, føres det. Ingen API-kall, og
  `fetch_prices.py` kjøres ikke
- Migrasjonen `0004_maalinger.sql` legger kolonnene til med `ADD COLUMN` og en
  CHECK i hver kolonne, uten `DROP TABLE`: en vurdering har alle fire, bortsett
  fra at `volumforhold` kan mangle når `interesse = 0`, og en rad med grunn har
  ingen av dem. En kommentar i `0004` gir enheten for hver kolonne
- `0004` har en hjelpetabell som `kontroll_0003`, som stopper migrasjonen hvis
  det finnes vurderingsrader uten grunn. De kan ikke få målinger etterpå (AD-7)
- `Vurdering` kontrollerer verdiene: endelige tall, standardavvik ≥ 0,
  forholdstall ≥ 0 eller `None`, og `None` bare når interesse er 0. Porten
  sjekker ikke fortegnet mot målingen, fordi den da ville vært bundet til
  parametrene i kjernen, og en eldre rad ikke lenger kunne leses
- Kolonnene står i `VURDERINGSKOLONNER`, så `_UPSERT` og `les` tar dem med
- **Ville feilet hvis:** målingene ble lagret avrundet, eller i prosent. Da er
  det lagrede tallet ikke det regelen sammenlignet med grensen, og fortegnet kan
  ikke regnes etter fra raden

**Forutsetning:** finnes det vurderingsrader uten grunn i basen på PC-en, stopper
`0004`, og gruppen avgjør hva som skjer med dem før 2.1c flettes.

**Avhenger av:** 2.1b. **Én økt:** ja.

*Ferdig 2026-10-01:* flettet i `4b7e074`, PR #16.

*Lagt til 2026-10-16 kl. 11:54:* delen av kontrollpunkt 2 om grunnlaget i 10.1 og kontrollen i FR-603 ble trukket 05.10: grunnlaget har ingen målinger lenger (avgjort 04.10, `prd.md` §4.6). Se «Rettet 2026-10-05» under story 10.1 og kontrollpunktet om sammenligningen i FR-602 under story 10.3. Delen om visningen i FR-706 står, og er oppfylt.

### Story 2.2: Hentekommandoen som egen inngang

Som **sensor som kjører containeren**, vil jeg at oppstart ikke bruker et eneste
API-kall, så jeg ikke brenner gruppens dagskvote ved å se på løsningen.

**Oppfyller:** FR-401 · **Begrenses av:** `AD-10`, `AD-2`, `AD-12`

**Kontroll — hva testen ser etter:**
- Å starte webserveren utløser **null** nettkall, også når basen er tom
- Tom base gir tom-tilstand med beskjed om hvordan man henter, ikke en feilside
- Hentekommandoen er en egen inngang mot samme kodebase
- Nøkkelen leses fra miljøet, ikke fra en fil i imaget
- Markedsoversikten og aksjedetaljen leser kursene fra basen gjennom
  `SqliteKurslager`, ikke fra øyeblikksbildet *(lagt til 2026-09-28, fra
  endringsforslaget)*
- Webserveren åpner basen med samme funksjon som hentekommandoen (2.1b), og
  kjører `migrer()` én gang ved oppstart, ikke ved hver forespørsel, fordi
  `migrer()` alltid tar skrivelås (`deferred-work.md`) *(lagt til 2026-09-28)*
- Én tilkobling per forespørsel, lukket når forespørselen er ferdig
  (forutsetningen under) *(lagt til 2026-09-28)*
- Meldingen på den tomme siden sier ikke lenger «Ingen kursdata funnet i
  `data/`» (`deferred-work.md`), og «Kom i gang» i README rettes i samme commit
  (regel 19) *(lagt til 2026-09-28)*
- **Ville feilet hvis:** noen la hentingen i en oppstartskrok «for at det skal virke ut av boksen». To kjøringer samme dag hadde da brukt 30 av 20 kall

**Forutsetning** *(fra kodegjennomgangen 2026-09-23)*: Flask kjører
forespørsler i egne tråder (`threaded=True` er standard, `flask/app.py:655`), og
en `sqlite3`-tilkobling kan som standard ikke deles mellom tråder
(`check_same_thread`). Prøvd: brukt fra en annen tråd gir den `ProgrammingError`.
Det avgjøres her hvordan webserveren åpner basen, for eksempel én tilkobling per
forespørsel. Åpner webserveren basen tidligere, følger forutsetningen dit.

**Spørsmål til planen** *(fra endringsforslaget 2026-09-28)*:
- Kan oversikten hente de femten fra `aksje` sammen med nyeste kurs i én
  spørring? Det er en join appen faktisk bruker. Gruppen vil ha minst én, og en
  join mot `aksje` i 2.7 bare for navnet teller ikke
- Skal oversikten lese dagens vurdering fra `vurdering` i stedet for å regne
  signalet av kursene ved hver visning? Samme data og samme parametre gir samme
  svar, men det er to veier til samme tall

Blir storyen mer enn én økt, deles den i 2.2 og 2.2b når den planlegges.

**Én økt:** ja.

*Delt 2026-10-03, Marians beslutning:* 2.2 tar de to inngangene, at sidene leser kursene fra basen, den tomme tilstanden og at oppstart gjør null nettkall. Signalet regnes fortsatt av kursene. De to spørsmålene over er tatt videre til 2.2b.

*Ferdig 2026-10-03:* flettet i `1570ae9`, PR #19.

### Story 2.2b: Sidene leser dagens vurdering

*Lagt til 2026-10-03, Marians beslutning, da 2.2 ble delt.*

Som **bruker**, vil jeg at oversikten og aksjedetaljen viser det løsningen mente
den dagen, så siden og historikken aldri sier hver sin ting.

**Oppfyller:** FR-101, FR-408, FR-409 · **Begrenses av:** `AD-3`, `AD-7`, `AD-17`

Svarene på de to spørsmålene i 2.2, gitt i planen 03.10:

- Oversikten henter de femten fra `aksje` sammen med nyeste og forrige kurs,
  `hentet` fra `kursserie` og dagens rad i `vurdering` i én spørring. Det er en
  join appen faktisk bruker.
- Oversikten og aksjedetaljen leser dagens vurdering fra `vurdering` for
  datoen til nyeste kurs, og regner ikke signalet av kursene. Da finnes det én
  vei til tallet.

**Kontroll — hva testen ser etter:**
- Oversikten bygges av én spørring med join mot `aksje`, og testen ser at den
  gir de femten med navn, kurs, endring og vurdering
- En aksje med rad i `vurdering` viser styrke, retning og sjekkene derfra.
  Aksjedetaljen tegner grafen av serien i `kurs` og forklarer sjekkene med
  målingene i `vurdering` (FR-706)
- En dag uten vurdering viser «–» med tilstanden fra `tilstand.py` (FR-409):
  grunnen når raden har en grunn, og «ikke vurdert» når kommandoen ikke ble
  kjørt. Signalet regnes ikke i stedet
- En base som er lest inn med `--les-inn`, viser ingen signaler, fordi
  `--les-inn` aldri skriver vurderinger (AD-7). Siden sier det med tilstanden
- **Ville feilet hvis:** siden regnet signalet når raden mangler. Da finnes to
  veier til samme tall, og en dag ingen kjørte kommandoen, ser ut som en dag
  med svar

**Avhenger av:** 2.2 og 2.5. **Én økt:** ja.

*Ferdig 2026-10-04:* flettet i `ff58ecf`, PR #20.

### Story 2.3: Børsdagskontroll før kvoten brukes

Som **gruppe med 20 kall i døgnet**, vil jeg at kommandoen sjekker om vi
allerede har dagens data, så en kjøring nummer to ikke koster 15 kall til.

**Oppfyller:** FR-402 · **Begrenses av:** `AD-20`, `AD-10`, NFR-01

**Kontroll — hva testen ser etter:**
- Er lagrede data fra siste forventede børsdag, hentes **ingenting** og kalltelleren er uendret
- Er de eldre, hentes det
- Er nyeste dato i svaret ikke forventet børsdag, vises siste kjente data med tidsstempel
- Kontrollen regner børsdag i **norsk** kalenderdato
- Startet før kl. 22:00, på en dag som ikke er børsdag, eller når dataene for siste børsdag finnes, bruker kommandoen **null** kall og sier hvorfor *(lagt til 2026-09-29)*
  *(rettet 2026-10-05, svar 2 kl. 19:17: på en dag som ikke er børsdag avgjør basen. Mangler siste børsdag for noen av aksjene, hentes den, fordi raden for den dagen fortsatt kan skrives (AD-7). Ellers null kall)*
- **Ville feilet hvis:** kontrollen lå i webserveren. Den kan ikke handle på utfallet, og da ville sjekken vært pynt

**Forutsetning** *(punkt 23, avgjort 2026-09-28)*: kommandoen kjøres på børsdager mellom kl. 22:00 og midnatt. Planen avgjør om den advarer eller nekter før kl. 22:00, fordi en kjøring som kommer for tidlig, bruker dagens kall uten å få dagens rad.

*Avgjort, lagt til 2026-09-29:* kommandoen nekter før kl. 22:00, med en uttrykkelig
overstyring for kjøring for hånd. En planlagt jobb kan ikke svare på en advarsel.

*Fra endringsforslaget 2026-09-28, et argument for planen og ikke en
avgjørelse:* en kjøring som kommer for tidlig, skriver dagens øyeblikksbilde, og
vernet fra 2.0 i `kjoer()` stopper da kveldens kjøring. Dagen får en grunn i
stedet for en vurdering, og kan ikke etterfylles. Det taler for at kommandoen
nekter før kl. 22:00, med en uttrykkelig overstyring. Mellom 2.5 og 2.3 kjøres
hentingen for hånd, bare på børsdager og bare mellom kl. 22:00 og midnatt.

**Følge** *(lagt til 2026-09-29)*: når 2.3 er flettet, endres FR-401, og oppsettet i
Oppgaveplanlegging beskrives i README (regel 19).

*Lagt til 2026-10-01:* med 2.8 koster en henting 16 kall, ikke 15. 2.8 utvider testen her med indekskallet, så en andre kjøring samme børsdag fortsatt gjør null kall.

*Avgjort 2026-10-05, gruppens svar kl. 19:17 på planen kl. 17:35:*
1. **Kvoten** leses med `/api/user` før første kall. Er det færre enn 15 igjen av dagens 20, men bonuskvoten (`extraLimit`) dekker resten, hentes det likevel, og utskriften sier hvor mange kall som tas fra bonusen. Dekker heller ikke bonusen 15, blir det 0 kall. Kan svaret ikke leses, hentes det, og utskriften sier det. Navn og e-post fra svaret står aldri i utskriften.
2. **Overstyringen** gjelder bare før kl. 22:00 på en børsdag. På en dag som ikke er børsdag avgjør basen: mangler siste børsdag for noen av aksjene, hentes den, fordi raden for den dagen fortsatt kan skrives (AD-7). Ellers 0 kall. Oppgaveplanlegging kjører derfor hver dag kl. 22:15, ikke bare på hverdager.
3. **Jobben** kjører fra en egen arbeidskopi av main. `data/` og `.env` deles med hovedkopien uten at nøkkelen kopieres, helst uten ny kode. Når jobben går slik, gjelder ikke lenger regelen fra 05.10 om at byggingen stopper kl. 22:00.
- **Rekkefølgen før første kall:** klokka, tidskontrollen, basen, filvakten, nøkkelen og kvoten.
- **Regelen om at grener bare bruker testbaser** føres i `CLAUDE.md` når 2.3 bygges, ikke i README-en.

*Lagt til 2026-10-08, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 6 og 10), godkjent av Marian kl. 08:04:*
- **Kontroll:** kvotesjekken tar antallet aksjer i lista som parameter og regner ikke med et fast 15. Testen prøver den med en kortere liste enn 15 (føringen 30.09 under `AD-21`). Med 2.8 er det antallet pluss 1. Da trenger 2.11 bare å gi den et annet tall.
- *Avgjort 2026-10-08 kl. 08:06, Marians beslutning:* svar 1 over står. Bonuskvoten brukes bare til å fullføre kveldens henting, aldri til 2.3b, målingen i 2.13 eller noe annet (NFR-01).

**Én økt:** ja.

*Ferdig 2026-10-08:* flettet i `249853e`, PR #22.

*Avgjort 2026-10-16, gruppens beslutning kl. 21:09:* hentingen på børsdager flyttes fra kl. 22:00 til kl. 21:00, på betingelse av at radene fra prøvene kl. 20:30 og 21:00 er like raden i kursfila etter kveldens henting (`malinger.md` §31). Er de ulike, tas spørsmålet opp igjen. Endringen bygges som en egen PR søndag 18.10 og gjelder fra mandag 19.10. Mangler noen aksjer raden kl. 21, henter et nytt forsøk dem senere samme kveld med kallene som er igjen (2.3b).

*Lagt til 2026-10-20 kl. 15:12:* beslutningen er snudd av gruppens svar 19.10 kl. 22:19 (under): hentingen på børsdager går tilbake til kl. 22:00 fra tirsdag 20.10, fordi raden fra kl. 21 ikke var endelig for DNO (`malinger.md` §37). Byggestoppen blir kl. 21:40.

*Lagt til 2026-10-17:* betingelsen holdt for EQNR.OL 16.10, i alle sju feltene (tillegget til §31 i `malinger.md`). Fra 19.10 er grensen kl. 21:00, og kl. 22:00 i kontrollpunktene og avgjørelsene over gjelder til da. Flagget som slipper forbi tidskontrollen, heter `--uten-tidskontroll` (spesifikasjonen `spec-2-3-hentingen-fra-kl-21.md`).

*Lagt til 2026-10-17 kl. 21:38:* grensen kl. 21:00 og flagget `--uten-tidskontroll` er flettet i `336204f`, PR #60. PR-en ble bygget lørdag kveld 17.10 etter gruppens svar kl. 21:01, i stedet for søndag 18.10. CI var grønn på head-en `f506133` (kjøring 39063125455) og på main (39063214018). Den gjelder fra første henting mandag 19.10.

*Avgjort 2026-10-17 kl. 22:00 (gruppens svar på ECH2 og BH7 i gjennomgangen av PR #60):* betingelsen for kl. 21:00 er prøvd for én aksje én dag. Hentingen går kl. 21:00 mandag 19.10, som avgjort. Trenger ingen aksje et nytt forsøk, brukes kallene som er igjen av dagens kvote etter kl. 22 til å hente fire aksjer på nytt og sammenligne radene for dagen med kursfila fra kl. 21, i alle sju feltene. Er noen ulike, tas spørsmålet opp igjen før tirsdag. Målingen bruker bare kallene som er igjen av dagens kvote, aldri bonuskvoten. Aksjene velges før kallene etter denne regelen: de fire med volumforholdet nærmest grensen for interesse (1,5) i kveldens vurderinger, fordi en endring i volumet der lettest endrer vurderingen. Verken kurser eller volum skrives av, bare om hvert felt er likt.

*Lagt til 2026-10-19 (målingen etter svaret kl. 22:00, `malinger.md` §37):* DNO, MOWI, GJF og AKRBP, de fire med volumforholdet nærmest 1,5 i kveldens vurderinger, ble hentet på nytt kl. 22:00. MOWI, GJF og AKRBP er like kursfila fra kl. 21 i alle sju feltene. DNO er ulik i `volume` og lik i de seks andre. Raden fra kl. 21 var altså ikke endelig for volumet til DNO, og spørsmålet tas opp igjen før tirsdag, som svaret sier. Om forskjellen endrer vurderingen for DNO, er ikke regnet ut.

*Avgjort 2026-10-19 kl. 22:19 (gruppens svar):* hentingen på børsdager går tilbake til kl. 22:00 fra tirsdag 20.10, fordi raden fra kl. 21 ikke var endelig for DNO (`malinger.md` §37), og en vurdering kan ikke skrives om (AD-7). Byggestoppen blir kl. 21:40. Det snur beslutningen 16.10 kl. 21:09.

*Lagt til 2026-10-20 kl. 16:07:* hentingen tilbake til kl. 22:00 på børsdager er squash-flettet i `54a4c51`, PR #79, låst til head-en `1eb5f6c` (spesifikasjonen `spec-2-3-hentingen-fra-kl-22.md`). Hele settet på `1eb5f6c`: 2763 bestått og 17 hoppet over. CI var grønn på head-en (39435878366). Grenen er slettet på GitHub. Mutantene G1 (grensen tilbake på kl. 21:00) og G2 (grensen på kl. 22:01) ble fanget.

### Story 2.3b: Kallene som er igjen, brukes på nye forsøk

*Lagt til 2026-10-05, gruppens beslutning kl. 19:17.*

Som **gruppe med 20 kall i døgnet**, vil vi at kallene som er igjen etter kveldens henting, brukes til å hente aksjer som mangler dagens kurs, så færre dager får en grunn i stedet for en vurdering.

**Oppfyller:** FR-402, NFR-01 · **Begrenses av:** `AD-6`, `AD-7`, `AD-20`

**Kontroll — hva testen ser etter:**
- Aksjer som feilet eller mangler dagens kurs etter hentingen, prøves igjen med det som er igjen av dagens 20 kall, aldri bonuskvoten. Eldste først, og rundt igjen til alle har dagens kurs, kallene er brukt eller klokka er 23:45
- En aksje som allerede har dagens kurs, hentes ikke igjen. Hvert kall henter hele året, så eldre kurser er alt sjekket
- Et forsøk som lykkes, skriver vurderingen over grunnen samme dag. En grunn skriver aldri over en vurdering (AD-7)
- Filvakten slipper gjennom et delvis forsøk uten å skrive over kveldens øyeblikksbilde
- Oppgaveplanlegging gjentar jobben hver halvtime fra 22:15 til 23:45
- **Ville feilet hvis:** et nytt forsøk brukte bonuskvoten eller hentet en aksje som har dagens kurs

Med 2.8 er det 4 kall igjen, ikke 5.

*Lagt til 2026-10-08, endringsforslaget 08.10:* kallene som er igjen, er 20 minus antallet aksjer i lista og indeksen, ikke et fast 4. Med 18 aksjer og indeksen er det 1. Testen prøver en liste med 18. Bonuskvoten brukes fortsatt aldri her (Marians beslutning kl. 08:06).

**Avhenger av:** 2.3, og bygges etter 3.4. **Én økt:** avgjøres i planen.

*Lagt til 2026-10-10, gruppens svar kl. 19:32 på planen kl. 19:07 (`spec-2-3b-kallene-som-er-igjen-brukes-paa-nye-forsoek.md`):*
1. Fila for et nytt forsøk heter `forsoek<n>-raa-<dato>.json`, med n fra 2.
2. Én runde per kjøring, eldste først. Gjentakelsen gir «rundt igjen».
3. En dag børsen er stengt, står raden, som beslutning 1 i spesifikasjonen til 2.5 (02.10 kl. 10:29).
4. Ingen nye kall etter kl. 23:50.
5. Kode 1 når en aksje mangler dagens kurs etter kjøringen, også når den feilet (ECH1 i 2.3).
6. ECH8 fra 2.3 tas i 2.3b: vurderingene som mangler når basen har kursene, skrives med 0 kall.
7. Flettes tidligst etter at hentingen mandag 12.10 er gjort og kontrollert. README-prøven fører commiten den brukte.
- Kontrollpunktet «Oppgaveplanlegging gjentar jobben hver halvtime fra 22:15 til 23:45» er flyttet til et eget steg etter README-prøven, med egen plan. 2.3b skriver ingen oppskrift for Oppgaveplanlegging.
- **Én økt:** ja.

*Ferdig 2026-10-12:* flettet i `c3d6660`, PR #28.

### Story 2.4: Etterfylling av hull i kursserien

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

Som **bruker som ikke åpnet løsningen på en uke**, vil jeg at grafen er hel når
jeg kommer tilbake, så hullet ikke ser ut som en kursbevegelse.

**Oppfyller:** FR-403 · **Begrenses av:** `AD-5`, NFR-01

**Kontroll — hva testen ser etter:**
- Fire dagers opphold fylles ved neste henting
- Etterfyllingen koster **15 kall**, ikke 15 per manglende dag
- Serien erstattes i sin helhet, den skjøtes ikke
- **Ville feilet hvis:** noen etterfylte vurderinger på samme måte. Kurser kan etterfylles; vurderinger kan ikke, og `AD-7` skal stoppe forsøket

*Lagt til 2026-10-01:* med 2.8 blir tallet 16 kall, ikke 15.

**Én økt:** ja.

### Story 2.5: Vurderingen skrives i samme kjøring

Som **gruppe**, vil jeg at vurderingen regnes av kursene som nettopp ble lagret,
så den ikke kan regnes av en serie som er byttet ut siden.

**Oppfyller:** FR-408 · **Begrenses av:** `AD-17`, `AD-5`, `AD-7`

**Kontroll — hva testen ser etter:**
- Én kjøring skriver kurser **og** vurderinger for alle femten
- Vurderingen er regnet av de radene kjøringen selv lagret
- Kjøres kommandoen to ganger samme dag, finnes fortsatt én vurdering per aksje
- **Et symbol som feilet** (`AD-15`): storyen sier eksplisitt hva som skrives
  for det, og testen prøver det. Svaret avgjøres av åpent punkt 24 før 1.7: en
  rad med en egen tilstand, eller en rad med grunnen. Ingen rad er ikke et
  gyldig svar, fordi det da leses som at kommandoen ikke ble kjørt. *Lagt til
  2026-09-24* *Avgjort 2026-09-27 (punkt 24):* en rad med grunnen. Det gjelder
  også når nyeste kurs ikke er fra dagen, og når signalet ikke kan regnes.
- Datoen for vurderingen regnes én gang, fra samme øyeblikk som filnavnet og
  `hentet` (2.1). En kjøring som går over midnatt i Oslo, stopper og sier fra, i
  stedet for å få `ValueError` fra `skriv` midt i universet (`deferred-work.md`,
  fra spesifikasjonen for 1.6) *(lagt til 2026-09-28, fra endringsforslaget)*
- Vurderingene leses tilbake gjennom `Vurderingslager.les` i samme test, fra en
  base på disk, ikke bare `:memory:` *(lagt til 2026-09-28)*
- Vurderingen bygges med målingene fra `Signal` (2.1c), og testen leser dem
  tilbake *(lagt til 2026-09-29)*
- **Ville feilet hvis:** vurderingen ble skrevet av en egen kommando. Kjøres den etter en ny henting, er grunnlaget byttet ut — og raden ville lagret hva løsningen mente om *andre* data enn de som lå der

**Forutsetning** *(fra kodegjennomgangen av Epic 1, 2026-09-27)*: `SqliteKurslager` godtar ethvert symbol, også `EQNR.OL`, mens `SqliteVurderingslager` bare godtar symbolene i `AKSJEUNIVERS` (G10). *Løses i basen i 1.9 (lagt til 2026-09-27).* *Løst i basen i 1.9 (2026-09-27, AD-21):* `0003` avviser et ukjent symbol i `kurs`, `kursserie` og `vurdering`, og `SqliteKurslager` gjør avvisningen om til `ValueError`. `MinneKurslager` godtar fortsatt `EQNR.OL`, så de to lagrene oppfører seg ulikt der. `SqliteVurderingslager.skriv` slipper ut `sqlite3`-feil, mens `erstatt_serie` gjør `IntegrityError` om til `ValueError` (G11). Her avgjøres det om `Kurslager` skal sjekke symbolet, og hvilke feil kjøringen fanger. Blir skrivingen til basen en egen story, følger forutsetningen dit. *Flyttet til 2.1b 2026-09-28 for `Kurslager`.* Det som gjelder `SqliteVurderingslager.skriv`, som slipper ut `sqlite3`-feil (G11), står igjen her.

**Én økt:** ja.

*Ferdig 2026-10-02:* flettet i `c65f587`, PR #18.

### Story 2.6: Utbyttedager merkes

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

Som **bruker som regner etter**, vil jeg vite når en kurs falt på grunn av
utbytte, så avviket mellom vist kurs og vist prosent ikke ser ut som en feil.

**Oppfyller:** FR-407 · **Begrenses av:** `AD-5`, `AD-19`

**Kontroll — hva testen ser etter:**
- En dag der endringen i ujustert og justert kurs spriker, merkes
- Merkingen leses av **kursserien alene** — ingen avhengighet til NewsWeb
- En vanlig dag merkes ikke
- **Ville feilet hvis:** merkingen hentet eks.dato fra `melding`-tabellen. Da ville Epic 2 hvilt på Epic 6, som kan strykes 28.09

**Én økt:** ja. **Merk:** kilden er ikke endelig valgt — åpent punkt 4. Storyen
forutsetter den målte veien.

### Story 2.7: Historikken i aksjedetaljen

*Lagt til 2026-09-27, fra prioriteringen samme dag.*

Som **bruker**, vil jeg se hva løsningen sa om aksjen de siste ukene, så FR-408s spørsmål har et svar i appen.

**Oppfyller:** FR-408, FR-409, punkt 20 i `prd.md` §8 · **Begrenses av:** `AD-3`, `AD-7`, `AD-20`

**Kontroll — hva testen ser etter:**
- De siste fire ukene, dag for dag: styrke og retning, eller grunnen, «ikke vurdert» eller «ikke børsdag»
- Målingene vises dag for dag, avrundet som i FR-706 (2.1c) *(lagt til 2026-09-29)*
- Hver dag går gjennom `tilstand`, så styrke 0, en grunn og en manglende rad aldri ser like ut
- `Vurderingslager` får en lesemetode for en periode, og ingen slette- eller endremetode (`AD-7`)
- Dagens rad som ikke er skrevet ennå, vises ikke som et hull
- Malene deler én layout og én CSS-fil
- **Ville feilet hvis:** historikken ble regnet ut på nytt av kursene. Da viser den dagens parametre, ikke hva løsningen sa

**Avhenger av:** 2.2 og 2.5. **Én økt:** ja.

*Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.3, nr. 22), godkjent av Marian kl. 12:46:* her sto «ikke kjørt» i første kontrollpunkt. Teksten brukeren ser, er «ikke vurdert», som i `designregler.md` §2. `Art.IKKE_KJOERT` i koden står.

*Avgjort 2026-10-19 kl. 12:06 (gruppens svar):* stilen flyttes til én CSS-fil nå, som første del av 2.7 (spesifikasjonen 2.7a), før 8.3 og historikken, fordi seks regler står likt i `index.html` og `aksje.html`, og kontrollpunktet i 2.7 sier én layout og én CSS-fil. Det erstatter svarene kl. 11:54 og 11:58 samme dag om at rammen skulle telle som felles stil til en egen PR senere i uka. Historikken blir 2.7b.

*Lagt til 2026-10-19 kl. 14:28:* all stilen står i `src/static/stil.css`, lenket fra `_ramme.html` med et avtrykk av fila, og sidene ser ut som før, flettet i `dc521ff`, PR #76 (spesifikasjonen `spec-2-7a-stilen-i-en-css-fil.md`). Kontrollpunktet om én layout og én CSS-fil er oppfylt. Historikken er 2.7b.

### Story 2.8: Hovedindeksen hentes i samme kjøring

*Lagt til 2026-10-01, Marians beslutning.*

Som **bruker**, vil jeg at hovedindeksen hentes sammen med aksjene, så dagens
tall kan sammenlignes med børsen som helhet.

**Oppfyller:** FR-410 · **Begrenses av:** `AD-10`, `AD-15`, `AD-16`, `AD-21` med føringen 2026-10-01, NFR-01, NFR-07

**Kontroll — hva testen ser etter:**
- Én kjøring henter `OSEBX.OL` med ett kall, med samme intervall som aksjene, og bruker 16 kall i alt
- Rådata står i samme øyeblikksbilde som aksjene, under en egen nøkkel og ikke blant aksjeseriene
- Indeksen lagres i tabellen `indeks` fra migrering `0006`, aldri i `aksje`, `kurs`, `kursserie` eller `vurdering`
- Bare børsdager lagres, i årene `DEKKEDE_AAR` dekker, uten et fast årstall i koden. Datoene fra `malinger.md` §14 som aksjene ikke har, lagres ikke
- Feiler indekskallet, lagres og vurderes aksjene som vanlig. Indeksen står i `feil` og får ingen ny sjanse (`AD-15`), og `vurdering` får ingen rad for den
- Testen i 2.3 er utvidet med indekskallet: en andre kjøring samme børsdag gjør null kall
- README (linje 82, «15 kall») og diagrammet i spinen («15 kall, bevisst») rettes til 16 i samme commit som koden (regel 19)
- **Ville feilet hvis:** indeksen ble lagt i `kurs` eller `AKSJEUNIVERS` for å slippe en ny tabell. Da teller den som en aksje i signalet og i «x av N»

*Avgjort 2026-10-16, gruppens svar kl. 18:04 på planen for hovedindeksen (instruksjonen kl. 17:45):*
- **PR 1** (tabellen `indeks`, porten og demoindeksen) flettes etter PR #49, ikke før: prøvekjøringen av #49 bruker grenen, som bare kjenner versjon 5 av basen.
- **Demobasen** får en oppdiktet hovedindeks i PR 1, så 2.9 kan vises i demoen før kallet er flettet (beslutningen kl. 11:46 under story 2.12).
- **PR 2** (kallet for indeksen i hentingen) flettes lørdag 17.10, etter at PR #49 er flettet. Lørdag er det ingen henting.
- **Henteinstruksjonen** fra mandag 19.10 har 16 kall, versjon 6 og 4 kall til nye forsøk. Rådet skriver den.
- **README-henvisningen:** «README (linje 82, «15 kall»)» i kontrollen over gjelder nå `docs/hjelp.md`, som rettes i PR 2 (regel 19).

*Avgjort 2026-10-16 kl. 22:16 (gruppens beslutning, gitt i chatten med rådet):* sjekken av basen før kallene skal virke også når basen står en versjon bak, som 16.10 med `0005`: «Basen ose.db kunne ikke leses (RuntimeError). Henter likevel», og filvakten holdt (Utført-linja for hentingen 16.10, `6b07a53`). Det rettes i PR 2 lørdag 17.10, som egen commit med en test, før migrasjonen `0006` møter den ekte basen.

*Lagt til 2026-10-17:* PR 1 (2.8a), tabellen `indeks` i migrering `0006`, porten og demoindeksen, er flettet i `1d3a21d`, PR #56, etter gruppens ja kl. 00:25 og sjekken for hånd samme minutt av `DEMIX` og «Demoindeksen» mot lista hos Euronext. CI var grønn på head-en `114a380` (kjøring 38975808686). Storyen står som in-progress til PR 2, kallet i hentingen, er flettet.

*Avgjort 2026-10-17 kl. 11:58 (gruppens svar om PR #57):* feiler bare hovedindeksen, gir hentingen kode 3, så en feil med indeksen ikke ser ut som en vellykket kjøring (BH7 i gjennomgangen av 2.8b). Ikke 2, fordi argparse bruker 2 for feil i argumentene. Kode 1 går foran: mangler også en aksje dagens kurs, gir kjøringen 1, fordi aksjen kan prøves igjen samme kveld. Rådet anbefalte 0. Ja til flettingen når det er gjort.

*Lagt til 2026-10-17 kl. 12:30:* PR 2 (2.8b), kallet for `OSEBX.OL` i hentingen med 16 kall, kode 3 når bare hovedindeksen feiler, og sjekken av basen som leser en base en versjon bak, er flettet i `bcac2b5`, PR #57. CI var grønn på head-en `b4a0721` (kjøring 39025050482). Storyen er done.

*Lagt til 2026-10-17:* gruppen godtok kl. 12:44 at et nytt forsøk gir kode 3 når indeksen feilet i kveldens hovedhenting (rettingen etter gjennomgangen, `a15f234`), som går ut over beslutningen kl. 11:58.

**Avhenger av:** 2.3 og 4.3 (`ki_logg` er `0005`). **Én økt:** ja.

### Story 2.9: Hovedindeksen i markedsoversikten

*Lagt til 2026-10-01, Marians beslutning.*

Som **bruker**, vil jeg se hvordan børsen gikk i dag, og hvor mange av aksjene som
gikk bedre, før jeg leser tabellen.

**Oppfyller:** FR-104 · **Begrenses av:** FR-101, `AD-10`, `AD-21` med føringene 30.09 og 2026-10-01, NFR-03, NFR-06, NFR-08

**Kontroll — hva testen ser etter:**
- Over tabellen står «Hovedindeksen» med OSEBX ved siden av, verdien, dagens endring og «x av N gikk bedre enn indeksen». Tabellen har fortsatt fem kolonner (FR-101)
- Endringen regnes mot forrige børsdag, ikke mot forrige rad
- N er aksjene med kurs for indeksens dato, og testen prøver det med en kortere liste enn 15. En aksje som ikke er med, navngis
- «Bedre» avgjøres på endringen slik den vises, og lik er ikke bedre
- Uten indeks i basen viser siden det, og resten av siden virker (NFR-03). Webserveren gjør ingen nettkall (`AD-10`)
- **Ville feilet hvis:** N var et fast 15. Da står det «x av 15» en dag én aksje mangler kurs

*Lagt til 2026-10-17 kl. 19:55:* PR 3 for hovedindeksen, «Hovedindeksen» over tabellen på forsiden (FR-104), er flettet i `b44284f`, PR #59. CI var grønn på head-en `bdfd412` (kjøring 39055685375) og på main (39055792414). Spesifikasjonen er `spec-2-9-hovedindeksen-paa-forsiden.md`. Søylene (2.9b) kommer i PR 4.

**Avhenger av:** 2.2 og 2.8. **Én økt:** ja.

### Story 2.9b: Søylene under hovedindeksen

*Lagt til 2026-10-01, Marians beslutning kl. 18:19.*

Som **bruker**, vil jeg se dagens endring for hver aksje mot indeksen, så jeg ser
med en gang hvilke som trakk opp og ned.

**Oppfyller:** FR-105 · **Begrenses av:** FR-101, FR-104, `AD-21` med føringen 30.09, NFR-05, NFR-06

**Kontroll — hva testen ser etter:**
- Én søyle per aksje med kurs for indeksens dato, fra størst fall til størst stigning
- Antallet telles og prøves med en kortere liste enn 15
- Indeksens endring er en stiplet linje, grønn når indeksen steg og rød når den falt
- Skjermleserteksten har alle tallene
- Bransjesymbolene ligger i malen og hentes ikke fra nettet, som skriftene i `designregler.md`
- Grensene for fargene avgjøres i spesifikasjonen og føres i `designregler.md`
- Bare dagens søyler. Periodene og «Velg dag» fra designtavla er idé til v1.1
- Bransjesymbolet er gult når aksjen har 3 av 3 på siste børsdag (`designregler.md` §3) *(lagt til 2026-10-01)*
- **Ville feilet hvis:** søylene trengte et nytt kall eller en ny tabell. Endringen er den i FR-101, og bransjen står i `AKSJEUNIVERS`

*Avgjort 2026-10-16, gruppens svar kl. 18:04 på planen for hovedindeksen (instruksjonen kl. 17:45):* søylene viser bare dagens tall. Periodene og «Velg dag» kommer med 8.17.

**Avhenger av:** 2.9. **Én økt:** ja.

*Lagt til 2026-10-18 kl. 00:16:* søylene er flettet i `73098ed`, PR #63 (spesifikasjonen `spec-2-9b-soeylene-under-hovedindeksen.md`). Fargegrensene følger endringen slik den vises, og gult ved 3 av 3 er `#a67c00` (designregler §3 og §5). CI var grønn på head-en `dbb6fe6` (kjøring 39074089927) og på main (39074214167).

### Story 2.9c: Hovedindeksen som stiplet linje i kursgrafen

*Lagt til 2026-10-18, gruppens svar 17.10 kl. 22:38, 22:41 og 22:42 (instruksjonen 17.10 kl. 23:13, steg 5).*

Som **bruker**, vil jeg se hovedindeksen i kursgrafen på aksjesiden, så jeg ser om aksjen gikk bedre eller dårligere enn børsen i perioden.

**Oppfyller:** svaret kl. 22:38–22:42 under «Prioritering» · **Begrenses av:** FR-201, FR-104, `AD-10`, NFR-03, NFR-06, `designregler.md`

**Kontroll — hva testen ser etter:**
- Hovedindeksen er en stiplet linje i kursgrafen på aksjesiden. Stiplet linje brukes bare for indeksen (`designregler.md`)
- Linja regnes om, så den starter på aksjens justerte sluttkurs første dag i grafen og følger indeksens endring derfra. Aksjens linje over den stiplede betyr at aksjen gikk bedre enn børsen i perioden
- Bare dager indeksen har, uten nye kall. Indeksen leses fra basen gjennom porten, som på forsiden
- Mangler indeksen for perioden, tegnes ingen linje, og grafen sier det
- «?» og teksten for skjermleser forklarer linja, uten råd (NFR-06)
- Virker i demoen med DEMIX og ved 390 px
- **Ville feilet hvis:** indeksen ble tegnet i sine egne poeng, startet på en annen dag enn grafen, eller ble tegnet uten indeks

**Avhenger av:** 2.9b. **Én økt:** ja.

*Lagt til 2026-10-18 kl. 11:04:* linja er flettet i `24849dd`, PR #64 (spesifikasjonen `spec-2-9c-hovedindeksen-i-kursgrafen.md`). Startdagen er den første dagen i grafen som indeksen har, som er grafens første dag når indeksen har den (gjennomgangen, BH4 og VG1). CI var grønn på head-en `c41133e` (kjøring 39113646261) og på main (39113734933).

### Story 2.10: Høy og lav lagres med kursene

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-07, Marians beslutning kl. 23:11.*

Som **bruker**, vil jeg at dagens høyeste og laveste kurs finnes i basen, så
aksjedetaljen kan vise dem uten et nytt kall.

**Oppfyller:** FR-203 (tillegget 2026-10-07) · **Begrenses av:** `AD-5`, `AD-6`, `AD-16`, `AD-19`, NFR-01, NFR-08

**Kontroll — hva testen ser etter:**
- Adapteren i `eodhd.py`, `Kursrad` og lageret tar med `high` og `low` fra svaret, og en ny migrasjon legger dem til (`AD-16`)
- Ingen nye kall. Øyeblikksbildene har feltene alt (`AD-6`), og neste henting fyller dem for hele året, fordi serien byttes ut (`AD-5`)
- En rad uten `high` eller `low` lagres uten dem
- Grenen bruker bare testbaser og rører aldri `data/db/ose.db`
- **Ville feilet hvis:** en rad uten `high` eller `low` stoppet hentingen

**Avhenger av:** ingen åpne. **Én økt:** ja.

### Story 2.11: Lista leses fra basen

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 6 og 10).*

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

*Lagt til 2026-10-13, endringsforslaget 13.10 (N3, svar 24), godkjent av Marian kl. 12:46:*
- En aksje som kommer inn i lista, får en av de 13 bransjene i `designregler.md` §4, i feltet `sektor`
- **Ville feilet hvis:** en aksje kunne komme inn uten bransje, eller med en som ikke er blant de 13

### Story 2.12: Velge og bytte aksjer

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 6 og 10).*

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

*Lagt til 2026-10-13, endringsforslaget 13.10 (N3, svar 11 og 24), godkjent av Marian kl. 12:46:*
- En aksje som velges, får en av de 13 bransjene, og det brukeren ser, heter «bransje»
- Oversikten får delen «Dine egne aksjer» for aksjene brukeren har valgt selv (8.0e). Hva «egen» betyr, avgjøres i planen, som før
- **Ville feilet hvis:** en valgt aksje sto uten bransje, eller sto under «Øvrige aksjer» i stedet for «Dine egne aksjer»

*Lagt til 2026-10-16 (gruppens beslutning kl. 11:46, instruksjonen kl. 15:59):* demoen skal være mest mulig lik den ekte versjonen. Der demoen ikke kan gjøre det samme, fordi den ikke henter (FR-411), forklarer en boks hvordan det er i den ekte versjonen, gjerne med et bilde som blir stort ved klikk, trykk eller tastatur, ikke bare når musa holdes over. Bildet kan vise hele siden, for eksempel «Min liste» i den ekte versjonen, men lages fra testdata, aldri med ekte kurser (regelen 25.09 under story 3.3 i `epics.md`). For 2.12 betyr det noen ekstra oppdiktede selskaper i demobasen som kan velges, og at valget, «x av 18» og «Dine egne aksjer» virker likt i begge versjonene. Detaljene avgjøres i planen for 2.12.

*Avgjort 2026-10-16, gruppens beslutning kl. 21:49:* demoen viser alle 10 fargekombinasjonene av de tre sjekkene på siste dag, fra 3 grønne til 3 grå, og en test krever dem. De to aksjene som viser en grunn i stedet for en vurdering (`NYLIG_NOTERT` og `UTEN_KURSER` i `src/demo.py`), blir stående. Det bygges lørdag 17.10 etter PR 1 og PR 2 for hovedindeksen, fordi PR 1 også endrer demobasen.

### Story 2.13: Kommandoen som måler omsetning

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 13).*

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

### Story 2.14: Eks.datoer føres inn for hånd

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 12, Marians beslutning kl. 08:06).*

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

---

## Epic 3: Løsningen kan kjøres av andre enn oss

### Story 3.1: Dockerfile med to innganger

Som **sensor**, vil jeg kunne bygge og kjøre løsningen fra repoet alene, så
vurderingen ikke avhenger av at gruppens maskin er i rommet.

**Oppfyller:** **ingen FR — se merknad** · **Begrenses av:** `AD-9`, `AD-10`, `AD-12`, `AD-16`

**Kontroll — hva testen ser etter:**
- Imaget bygges fra et rent utsjekk og inneholder **ingen** rådatafiler og ingen base
- Å starte webserveren gjør null nettkall
- Hentekommandoen kjører hentingen
- Python-versjonen i imaget er **3.13**, samme som CI
- Migrasjoner kjøres **uten** et eget kommandosteg *(avgjort i 2.1b 2026-09-28: én funksjon åpner basen og kjører migrasjonene for begge inngangene, så 3.1 bare pakker)*
- **Ville feilet hvis:** migrasjonene ble lagt i en egen kommando. Det ville sett ut som ryddig ansvarsdeling og brutt suksessmålet «Drift»

*Lagt til 2026-10-05 (KI-laget, FR-608):*
- En compose-fil med appen og Ollama, og volumene `ose-db`, `ose-raa` og
  `ollama` (3.2)
- Modellen hentes første gang med Ollamas pull-endepunkt og bakes aldri inn i
  imaget (`AD-9`)
- Appen starter og viser sidene uten at Ollama kjører. KI er da av, og siden
  sier hvorfor (FR-601, NFR-04)
- **Ville feilet hvis:** modellen lå i imaget. Da blir imaget flere GB større,
  og modellen følger med leveransen i stedet for å hentes av den som kjører

*Rettet 2026-10-05, gruppens beslutning kl. 16:53:* compose-fila i 3.1 har bare
appen og volumene `ose-db` og `ose-raa`. Den lokale modellen starter ikke av seg
selv. Punktene over om Ollama og volumet `ollama` gjelder 10.2, der Ollama kommer
inn som eget valg. Punktet om at appen virker uten Ollama, står.

**Én økt:** ja.

> **Denne storyen har ingen FR bak seg, og det er ikke storyens mangel.**
> Ingen av de sju NFR-ene dekker at løsningen skal kunne bygges og kjøres av
> andre — kontrollert 2026-09-22. PRD-en har altså ikke med selve leveransen,
> mens faglærer navngir «kildekode og docker fil» som innleveringen. Ført som
> spørsmål til gruppen, ikke rettet. *24.09: sagt av faglærer i samtale 21.09,
> ikke på emnesiden (hjelpelærer 23.09); lages likevel.*

*Ferdig 2026-10-09:* flettet i `a2ecee8`, PR #23.

### Story 3.2: To volumer, og ingenting uerstattelig i imaget

Som **gruppe**, vil jeg at rådataøyeblikksbildene ligger utenfor alt som kan
slettes ved et uhell, så det som ikke kan hentes på nytt, overlever.

**Oppfyller:** NFR-07 · **Begrenses av:** `AD-11`, `AD-6`, `AD-9`

**Kontroll — hva testen ser etter:**
- `ose-db` og `ose-raa` er atskilte volumer
- Å fjerne basevolumet lar øyeblikksbildene stå
- Imaget kjører uten at noen av volumene finnes fra før
- **Ville feilet hvis:** ett volum dekket hele `data/`. Da tar én kommando med seg både det gjenoppbyggbare og det uerstattelige — og `vurdering` er uerstattelig selv om den ligger i basen

*Merknad 2026-10-05:* med den lokale modellen (FR-608) kommer et tredje volum,
`ollama`, for modellen. Det er gjenoppbyggbart: modellen kan hentes på nytt, og
volumet har ingen data fra kildene. Det holdes atskilt fra `ose-db` og
`ose-raa`, så å fjerne det tar verken basen eller øyeblikksbildene med seg. I
prøven i `malinger.md` §19 var volumet `ose-ki-ollama` på 6,2 GB med bare Gemma
igjen (dagsfila 04.10, instruksjonen kl. 21:29).

*Rettet 2026-10-05, gruppens beslutning kl. 16:53:* 3.2 har bare `ose-db` og
`ose-raa`. Merknaden over om det tredje volumet gjelder 10.2.

**Én økt:** ja.

*Ferdig 2026-10-09:* flettet i `088c885`, PR #24.

### Story 3.2b: Port 8000 i stedet for 5000

*Lagt til 2026-10-18, gruppens svar kl. 17:40 (instruksjonen kl. 18:05).*

Som **bruker på Mac**, vil jeg at appen starter uten at jeg må slå av noe, så jeg ikke står fast fordi AirPlay-mottakeren bruker port 5000.

**Oppfyller:** svaret kl. 17:40 under «Prioritering» · **Begrenses av:** `AD-10`, regel 19 i `CLAUDE.md`

**Kontroll — hva den ferdige storyen inneholder:**
- a) `compose.yaml` (begge tjenestene og kommentarene øverst), `Dockerfile` (`EXPOSE` og waitress), `src/app.py` (`app.run`) og CI i `.github/workflows/tester.yml` bruker 8000. Porten er den samme inne i containeren og på maskinen, så «Serving on» og adressen man åpner, sier det samme tallet
- b) README-en og `docs/hjelp.md`: hver adresse og «Serving on» sier 8000. Svaret om porten i `docs/hjelp.md` sier 8000, og setningen om AirPlay får en Rettet-linje
- c) `docs/kvalitetssikring.md`: radene i Prøve 1 og 2 som sa 5000, sier 8000, med en Rettet-linje. Arkitekturdokumentet får en datert linje der det nevner 5000. Spesifikasjonene og dagsfilene står som de er
- d) En test: porten er den samme i `compose.yaml`, `Dockerfile`, `src/app.py`, CI og README-en, og 5000 står ikke igjen i noen av dem
- Hentingen og basene røres ikke
- **Ville feilet hvis:** 5000 sto igjen i `compose.yaml`, README-en eller `Dockerfile`, eller to av dem sa forskjellige porter

**Avhenger av:** ingen. **Én økt:** ja.

*Lagt til 2026-10-18 kl. 19:07:* appen bruker port 8000, flettet i `3f1c789`, PR #68 (spesifikasjonen `spec-3-2b-port-8000.md`). Setningen om AirPlay er tatt ut av svaret om porten i `docs/hjelp.md` (gruppens svar kl. 18:58), og står ordrett i en Rettet-linje. CI var grønn på head-en `b4eaa7d` (kjøring 39147924016) og på main (39148045129).


### Story 3.3: README — «Slik kjører du den»

Som **en som ikke er oss**, vil jeg komme fra et rent utsjekk til begge
skjermbildene med ekte data ved å følge README alene.

**Oppfyller:** FR-401 (tom-tilstanden) · **Begrenses av:** `AD-9`, `AD-10`, `AD-12`

**Kontroll — hva testen og den ferdige storyen ser etter:**
- README-seksjonen: egen gratisnøkkel fra EODHD (20 kall i døgnet holder til én
  henting av de 15 symbolene), `.env` fra `.env.example`, bygging av imaget, og
  de to kommandoene — webserveren og hentingen
- **Avsnittet «Kom i gang» erstattes helt,** ikke utvides. Det sier i dag
  «Applikasjonen leser bare fra `data/`», som blir usant etter 1.4 og 1.5.
  *Rettet 2026-09-25:* setningen blir usann først når webserveren leser fra
  basen, som etter spinen skal ligge i `db/ose.db`. 1.4 og 1.5 endrer ikke
  hvor appen leser fra
- **Den tomme siden sier hvordan man henter, med samme kommando som README.**
  I dag sier den «Ingen kursdata funnet i `data/`. Kjør
  `uv run python src/fetch_prices.py` først» (`index.html:110–114`). Etter
  Epic 2 og 3 er det feil kommando og feil sted
- Kommandoen i tom-tilstanden kommer fra én konstant, og en test krever at den
  står i den tomme siden
- **Ville feilet hvis:** README og den tomme siden viste hver sin kommando. Da er
  det tilfeldig hvilken av dem som stemmer

*Lagt til 2026-10-09, gruppens svar kl. 23:13 (spesifikasjonen til 3.3):* kontrollpunktet om én konstant blir to, én for hver måte å kjøre på: `HENTEKOMMANDO` for uv og `HENTEKOMMANDO_DOCKER` for Docker. Den tomme siden viser Docker-kommandoen når `OSE_I_DOCKER=1`, som Dockerfile setter. README-en har begge, og testen krever det. Grunnen: Docker er hovedmåten og uv alternativet, og én kommando ville vært feil på den ene.

*Lagt til 2026-09-25:* Får README-en skjermbilder, viser de bare testdata, aldri
ekte kurser. Et skjermbilde med ekte EODHD-data i det offentlige repoet ville
publisert dataene, mot EODHDs betingelse («the data is not published») og regel
16.

*Lagt til 2026-10-05 (KI-laget, FR-608):*
- «Kom i gang» sier at den lokale modellen er gratis standard og hentes første
  gang, og at hver enkelt kan velge Gemini, Anthropic eller OpenAI med sin egen
  nøkkel, på sine egne vilkår
- README-en sier hvor mye minne den lokale modellen trenger, etter
  `malinger.md` §19. §19 har ikke målt et minstekrav. Den viser at Gemma
  kjørte med 2,1 GB ledig uten grafikkort og 3,3 GB med, på en PC med 15,7 GB
  og 8,2 GB til Docker Desktop. Tallet README-en oppgir, måles derfor når
  storyen bygges
- README-en sier at appen virker uten KI-tekst når minnet ikke holder (NFR-04)
- README-en endres først i denne storyen, når det den sier, stemmer. Ikke før
  (regel 19)

*Rettet 2026-10-05, gruppens beslutning kl. 16:53, etter svaret fra
hjelpelæreren (`docs/innlevering.md`, «Svaret, 2026-10-05»):*
- Docker er hovedmåten i README-en, og Python med uv er alternativet
- Demoen står først. EODHD med egen nøkkel er et eget avsnitt for den som vil
  teste med ekte data
- Punktene over om den lokale modellen og minnet gjelder 10.2, og punktet om
  egne nøkler gjelder 10.7. Punktet om at README-en endres når det den sier,
  stemmer, står

**Avhenger av:** 3.1. **Én økt:** ja.

*Ferdig 2026-10-10:* flettet i `5816bc2`, PR #25.

*Lagt til 2026-10-16 kl. 11:54:* kontrollpunktet «Demoen står først» fra 05.10 ble snudd 11.10 kl. 22:32: README-en anbefaler den ekte versjonen og har den før demoen (spesifikasjonen for 3.4, `spec-3-4-demoversjonen.md`, «2026-10-11 kl. 22:32», og testen `tests/test_docker.py::TestReadme::test_ekte_versjonen_foerst_og_zip_foer_kommandoene`). Docker som hovedmåten og uv som alternativet står. Kontrollpunktene er gått gjennom igjen mot main, og alle er oppfylt. At 20 kall i døgnet holder til én henting, står i `docs/hjelp.md`, som README-en lenker til, etter omskrivingen i 3.4, PR 3. 3-3 er done.

*Avgjort 2026-10-16 kl. 21:16, med svarene kl. 21:25 og 21:57 (gruppens beslutning, gitt i chatten med rådet, ført etter instruksjonen kl. 23:32):* i «Kom i gang» kommer demoen etter fellesstegene og før den ekte versjonen, fordi faglærer prøver demoen. Det snur rekkefølgen fra 11.10 kl. 22:32, ikke anbefalingen: den ekte versjonen er fortsatt anbefalt. «Til faglærer» får lenker til demoen, den ekte versjonen og testene. Gruppen gikk selv gjennom «Kom i gang» kl. 20:40–21:11 og fant fire ting: ZIP-fila ble dratt inn i stedet for mappa, mellomrommet etter `cd` manglet, «Cannot find path» hadde ikke noe svar, og det var uklart hvor kommandoen limes inn og hvor kopi-ikonet er. Det bygges søndag 18.10 i README-PR-en, med tre skjermbilder fra gjennomgangen.

*Lagt til 2026-10-19 (story 3.3g):* «den ekte versjonen er fortsatt anbefalt» over er snudd av gruppens svar 19.10 kl. 14:46 under «Prioritering»: README-en anbefaler demoen for faglærer og sensor. Rekkefølgen står.

*Avgjort 2026-10-16 kl. 21:53–21:58 (gruppens beslutning, gitt i chatten med rådet):* README-en ryddes i en egen PR etter README-PR-en søndag: «Status» som to lister, fem spørsmål under «Står du fast?», uv-delen som to lister, forklaringen under «Tester» bak en knapp, en linje «Innhold» og lenker i «Mappestruktur».

*Lagt til 2026-10-16 kl. 16:02 (instruksjonen kl. 15:59, som sier at gruppen sa ja 15.10 kl. 22:54; det svaret er ikke ført i dagsfila for 15.10):* fem forbedringer i README-en for sensor er beslutninger, i `spec-3-3b-readme-for-sensor.md`: a) «Status» med det som er flettet siden sist, og «Neste:» i rekkefølgen her; b) et skjermbilde av oversikten i demoen, 1280 px bredt med «Eksempeltall» synlig, i `docs/bilder/`; c) under «Tester», hvordan testene kjøres uten Docker med uv, og hva man skal se; d) i «Kom i gang», at demoen er veien for å se appen med en gang på dagtid en børsdag, og helgen i steg 8 og raden «Klar»; e) under «Du trenger», versjonene, Docker Desktop slik den er prøvd, og Python. Skjermbildet erstatter «uten bilder» (svar 4, 11.10). Regelen fra 25.09 står: bildet viser bare demoen. Svar 3 står: `--hent-foer-kl-22` står verken i README-en eller i `docs/hjelp.md`, fordi en henting før dagens kurser finnes, kan låse dagen.

*Lagt til 2026-10-16 kl. 16:33:* README-en for sensor (3.3b) er flettet i `6b9dc2f`, PR #53 (ja kl. 16:31). Spesifikasjonen `spec-3-3b-readme-for-sensor.md` og 3-3b i sprintstatusen er done. README-prøven står igjen under story 3.4.

*Avgjort 2026-10-16:* gruppen tok 16.10 kl. 21:38 skjermbildet av oversikten i demoen ut av README-en igjen. Det snur punkt b i 3.3b (ja 15.10 kl. 22:54, flettet i `6b9dc2f`, PR #53). Bildet og teksten under det er tatt ut, `docs/bilder/readme/oversikten-demo.png` er slettet, og testene godtar igjen ingen bilder i README-en og i `docs/bilder/` utenom CI-merket (PR #54). Regelen står: bilder i README-en kommer bare fra `docs/bilder/readme/` og viser aldri den ekte versjonen. Bildene som kommer i «Kom i gang» søndag, er ikke berørt, men PR-en med dem må endre de to testene, med stien og alt-teksten som sier at det er demoen, og PR 1 for hovedindeksen trenger ikke ta bildet på nytt.

*Lagt til 2026-10-16:* uttaket av skjermbildet er flettet i `1a95495`, PR #54, etter gruppens ja kl. 22:55. CI var grønn på head-en `cecf94e` (kjøring 38965865603).

*Avgjort 2026-10-18 kl. 00:03 (gruppens svar):* README-prøven tas første gang i uke 43 (19.–25.10), etter at de to README-PR-ene er flettet: Prøve 1, og Prøve 2 samtidig hvis testeren har egen gratiskonto. Den tas på nytt senest én uke før innleveringen, med ZIP-fila som leveres. Det endrer setningen fra 14.10 under story 3.4 om at prøven tas når mest mulig er bygget (§9 og §13 i `docs/kvalitetssikring.md`).

*Avgjort 2026-10-18 kl. 14:48 (gruppens svar, under instruksjonen kl. 12:23):* README-PR-en med bildene og rettelsene fra gjennomgangen 16.10 (`spec-3-3c-kom-i-gang-bilder-og-demoen-foerst.md`). «Står du fast?» kan ha høyst 10 spørsmål, ikke 8 som fra 11.10 kl. 22:32. Grensen på 65 ord per steg står for teksten i steget. Teksten under et bilde telles for seg, høyst 25 ord. Forklaringen av hvordan en kommando kopieres, står én gang, i et kort avsnitt rett før det første steget med en kommando, og hvert steg med en kommando sier bare at den limes inn i PowerShell-vinduet fra steg 4. Blir et steg fortsatt over 65 ord, flyttes detaljene til `docs/hjelp.md` med en lenke fra steget.

*Lagt til 2026-10-18 kl. 15:41:* tre skjermbilder i «Kom i gang», demoen først og fire rettelser fra gjennomgangen 16.10, flettet i `fdaf403`, PR #66 (spesifikasjonen `spec-3-3c-kom-i-gang-bilder-og-demoen-foerst.md`), etter gruppens ja kl. 15:35. CI var grønn på head-en `87e4f8e` (kjøring 39132413724) og på main (39132517882). Svarene på spørsmålene kl. 15:12 står i instruksjonen kl. 15:37: lenkene i «Til faglærer» kommer i README-ryddingen, og ryddingen tar «Står du fast?» ned til fem spørsmål, med svarene om mellomrommet etter `cd` og «Cannot find path» blant dem. Grensen på 10 gjelder bare til ryddingen. Instruksjonen sier at dette følger av beslutningene 16.10 og av gruppens svar kl. 21:56 og 21:57. De to svarene er ikke ført i repoet. Dagsfila 16.10 og `epics.md` nevner svaret kl. 21:57 bare ved rekkefølgen (beslutningen kl. 21:16), og de sier ikke hvilke fem spørsmål ryddingen beholder.

*Lagt til 2026-10-18 (instruksjonen kl. 17:04, story 3.3d):* README-ryddingen fra beslutningen 16.10 kl. 21:53–21:58 bygges i `spec-3-3d-readme-ryddingen.md`. Hvilke fem spørsmål «Står du fast?» beholder, er rådets forslag her, ikke avgjort 16.10: «Engine running», ZIP-fila som ser ut som en vanlig mappe, «is not recognized as the name of a cmdlet», «Cannot find path» og «no configuration file provided». «Status» får to lister, «Ferdig» og «Neste», i stedet for «Flettet til main» og «Neste:».

*Avgjort 2026-10-18 kl. 17:40 (gruppens svar):* appen bruker port 8000 i stedet for 5000, fordi AirPlay på Mac bruker 5000, i en egen PR i kveld (story 3.2b); og PR #67 flettes etter at spørsmålene om «Engine running» og «Cannot connect to the Docker daemon» er slått sammen til ett, fordi grunnen er den samme.

*Lagt til 2026-10-18 kl. 18:01:* README-ryddingen er flettet i `1be3a57`, PR #67 (spesifikasjonen `spec-3-3d-readme-ryddingen.md`): «Status» som «Ferdig» og «Neste», «Står du fast?» med fem spørsmål, der «Engine running» og «Cannot connect to the Docker daemon» er ett (svaret kl. 17:40), uv-delen som to lister, knappen i «Tester», tre lenker først under «Til faglærer», «Innhold» og lenker i «Mappestruktur». CI var grønn på head-en `8ffa969` (kjøring 39142845474) og på main (39142953539).

*Avgjort 2026-10-18 kl. 20:39 (gruppens svar):* «Tester» står der den står, og får installasjonen av uv for Windows og Mac og hvor lang tid testene tar, i neste README-PR.

*Avgjort 2026-10-18 kl. 21:42 (gruppens svar):* bildet av oversikten tas høyere, så hele gruppen «Skilte seg ut» i tabellen er med, og PR #70 flettes etter det. Grunnen: i 1280 × 1000 slutter bildet der tabellen begynner, så signalstyrken og fargene per aksje er ikke med.

*Lagt til 2026-10-18 kl. 22:09:* bildet av oversikten, uv i «Tester» og variablene i `.env` er flettet i `c5464e7`, PR #70 (spesifikasjonen `spec-3-3e-bildet-uv-og-variablene.md`). Bildet er tilbake under «Til faglærer», 1280 × 1573 px, til bunnen av «Skilte seg ut». «Tester» har installasjonen av uv for Windows og Mac og tiden for testene, og «Mer for den som vil» har tabellen over variablene.

*Avgjort 2026-10-18 kl. 23:03 (gruppens svar):* bildene av appen står bak en knapp rett under beskrivelsen, i en egen mappe for bilder og video, fordi appen endres hele tiden; de endelige bildene og videoen legges inn før innleveringen (spesifikasjonen 3.3f). Det endrer plassen fra svaret 18.10 kl. 00:20 og svar 4 i spesifikasjonen for 3.4 (11.10) om at bildene bare ligger i `docs/bilder/readme/`.

*Avgjort 2026-10-19 kl. 11:57 (gruppens svar):* ja til flettingen av PR #75, etter at README-en før og etter og begge bildene er sett.

*Lagt til 2026-10-19 kl. 12:19:* bildene av appen står bak knappen «Bilder av appen (demoen)» rett under beskrivelsen, i `docs/appen/`, med bildet av oversikten og et nytt bilde av aksjesiden for KVST, flettet i `208d086`, PR #75 (spesifikasjonen `spec-3-3f-bildene-av-appen-bak-en-knapp.md`).

*Avgjort 2026-10-19 kl. 16:46 (gruppens svar):* ja til flettingen av PR #77, etter at README-en før og etter er sett.

*Lagt til 2026-10-19 kl. 16:55:* README-en anbefaler demoen for faglærer og sensor, den lokale modellen er merket valgfri, og «Status» har «Neste i v1» og «Ekstra, hvis tiden rekker», flettet i `855ba75`, PR #77 (spesifikasjonen `spec-3-3g-readme-demoen-anbefales.md`).

*Avgjort 2026-10-20 kl. 10:14, 10:15, 10:18 og 10:19 (gruppens svar):* README-en blir kortere å lese, med mer bak en pil som foldes ut: de felles stegene står åpent, og demoen og den ekte versjonen står bak hver sin pil; «Dokumentene», «Mappestruktur» og installasjonen av uv står bak en pil; «Status» står åpent, og «Ferdig» blir en kort liste over det appen kan. Alt står i én fil, som virker fra ZIP-fila (spesifikasjonen 3.3h).

*Avgjort 2026-10-20 kl. 16:19 (gruppens svar):* `docs/hjelp.md` er et levende dokument som README-en: teksten rettes der den står, og historikken ligger i git, fordi hjelpen leses av brukere. De andre dokumentene får fortsatt en Rettet-linje.

*Avgjort 2026-10-20 kl. 20:20 (gruppens svar):* advarselen mot `docker compose down -v` står synlig rett under pila til den ekte versjonen, så den kommer rett etter steg 9 når pila er åpen, og synes for alle når den er lukket. Det snur avvisningen av BH4 og ECH8 i triagen til 3.3h.

### Story 3.4: Demoversjonen

*Lagt til 2026-10-03, Marians beslutning kl. 18:10.*

Som **faglærer, sensor eller medstudent uten egen EODHD-nøkkel**, vil jeg kunne
prøve appen med oppdiktede tall, så jeg ser hvordan den virker uten at gruppen
deler kontoen sin.

**Oppfyller:** FR-411 · **Begrenses av:** NFR-08, `AD-7`, `AD-9`, `AD-10`, `AD-12`, `AD-21`

**Kontroll — hva testen ser etter:**
- Demokommandoen lager `data/db/demo.db` med nettsperren på (AD-8) og uten
  `EODHD_API_KEY` i miljøet
- To kjøringer med samme frø gir like baser, rad for rad
- Serien er lang nok til seks måneder i grafen og MA50 fra grafens første punkt
  (FR-201, FR-202)
- Ingen symbol eller ticker i demobasen står i `AKSJEUNIVERS`. Navnene er
  kontrollert for hånd mot Oslo Børs' liste, og datoen står i spesifikasjonen;
  lista hentes aldri av programmet
- Demokommandoen fjerner de 15 som `0003` legger inn, før den skriver noe, og
  `aksje` i demobasen er lik `DEMOUNIVERS`. Testen som holder `aksje` lik
  `AKSJEUNIVERS` i den ekte basen, står (AD-21)
- Sidene leser selskapene fra `aksje` i basen. Portene som skriver, tar lista
  som parameter, med `AKSJEUNIVERS` som standard
- Hver børsdag i serien har én rad i `vurdering` per aksje, lik det `vurder()`
  gir for serien fram til den dagen. Raden er skrevet med `skriv` uendret og
  lagerets klokke stilt på dagen (AD-7)
- Bare demokommandoen setter `PRAGMA application_id` til demoverdien
- Hver side med demobasen viser «Eksempeltall», og ingen side med en ekte base
  gjør det. Merket leses fra basen, og testen bytter bryteren uten å bytte
  basen, og omvendt
- Begge vaktene: demokommandoen nekter en base uten demomerket, også en tom
  base, og hentekommandoen og `--les-inn` nekter en demobase før første kall
- Uten bryteren åpner webserveren `data/db/ose.db`. Med bryteren åpner den
  `data/db/demo.db` og lager den aldri selv. Mangler demobasen, viser siden
  kommandoen som lager den
- Imaget har ingen base, heller ikke demobasen
- README «Kom i gang» har demoversjonen, og en test krever at kommandoen der er
  den samme som i koden (regel 19)
- **Ville feilet hvis:** merket fulgte bryteren. Da kunne en ekte base vises som
  eksempeltall, eller en demobase vises uten merket, og det er det NFR-08 forbyr

**Hovedindeksen** kommer inn i demoen i den av 2.8 og 3.4 som bygges sist.
**Legger en senere story noe til på sidene,** får den et kontrollpunkt om at
demoen viser det også.

**Åpent:** hva KI-laget gjør med demobasen (Epic 10).

*Avgjort 2026-10-05:* demoen får ferdige KI-tekster for de oppdiktede dagene,
laget med Gemma og merket med modellen. Da ser faglærer KI uten Ollama og uten
å vente.
- De ferdige tekstene ligger i en fil i repoet, fordi demobasen aldri ligger der
  (`AD-9`). Demokommandoen leser fila og skriver tekstene inn i demobasen
- En test krever at grunnlaget for hver tekst stemmer med demodagen den hører
  til (FR-602)
- Tekstene består kontrollen i FR-603, og raden har tjenesten, modellen og
  hvordan modellen kjørte (FR-604, FR-605)
- **Ville feilet hvis:** demoen endret seg, og tekstene ble stående. Da forklarer
  KI en annen dag enn den siden viser

**Avhenger av:** 2.2b, 3.1 og 3.3, ikke av 2.8. **Én økt:** avgjøres i planen.

*Rettet 2026-10-05, gruppens beslutning kl. 16:53:* 3.4 bygges uten
KI-tekster, og demoen står først i «Kom i gang». Demoen er hovedveien for
vurderingen (svaret fra hjelpelæreren, `docs/innlevering.md`, «Svaret,
2026-10-05»). Den første kommandoen i README-en starter demoen. Hvordan,
avgjøres i planen for 3.1 og 3.4, uten at webserveren lager basen selv
(FR-411). Punktene over fra «Avgjort 2026-10-05» om KI-tekstene gjelder 3.4b.

*Lagt til 2026-10-06, etter tilbakemeldingen på briefen:* punkt 3 under «Neste steg for gruppen» i [`tilbakemelding-product-brief.md`](tilbakemelding-product-brief.md).
- README-oppskriften er fulgt fra start til slutt på en maskin som ikke har hatt repoet eller imaget før, uten nøkler. Dato, maskin og det som ikke stemte, føres i `docs/kvalitetssikring.md`. Prøven gjentas før innleveringen
- **Ville feilet hvis:** README-en bare var prøvd på maskinen den ble skrevet på

*Lagt til 2026-10-08, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, punkt 4.4), godkjent av Marian kl. 08:04:* alt i v1 skal kunne vises i demoen (tilbakemeldingen 06.10). Kontrollpunktene gjelder det som er bygget når 3.4 bygges, og en senere story legger til sitt eget, som avsnittet over sier.
- Demobasen har minst én aksje som er tatt ut av lista, én merket «Utenfor målingen», noen målte omsetninger, oppdiktede eks.datoer merket «Eksempeltall», og vurderinger nok til at signaldagene, merket for endret signalstyrke og «Velg dag» har noe å vise
- Lista i demoen kan byttes, og siden viser «x av 18», men det hentes aldri
- Når 2.11 er bygget, byttes testen som holder `aksje` lik `AKSJEUNIVERS`, mot den i 2.11
- **Ville feilet hvis:** en funksjon i v1 bare kunne vises med ekte data og nøkkel

*Ferdig 2026-10-10:* flettet i `0ed87be`, PR #26, og `59c0baf`, PR #27. README-prøven 13.–16.10 gjenstår (§9 i `docs/kvalitetssikring.md`).

*Lagt til 2026-10-11, Marians beslutning:* README-en skrives om for en som aldri har brukt Docker eller et terminalvindu, med steg, bilder og «Hvis noe går galt», før README-prøven (PR 3). Grunnen: Marian fant ikke ut hvor kommandoene skulle skrives. Bildet av demosiden tas etter 8.0d.

*Lagt til 2026-10-12:* PR 3 er flettet i `4464a10`, PR #30. README-en har en tabell over de to versjonene, felles steg 1–4, den ekte versjonen og demoen, «Står du fast?» og `docs/hjelp.md`, uten bilder (svar 4 11.10). README-prøven 13.–16.10 gjenstår (§9 i `docs/kvalitetssikring.md`).

*Lagt til 2026-10-13 (story 8.0e, PR 2):* README-prøven tas etter at 8.0d er flettet, så testeren ser det nye utseendet, og ikke 13.–16.10 (beslutningen kl. 23:40, §9 i `docs/kvalitetssikring.md`).

*Lagt til 2026-10-14 (gruppen kl. 22:19 og 22:25):* README-prøven tas når mest mulig av rekkefølgen etter 8.0d er bygget (se «Prioritering» øverst), og senest én uke før innleveringen. Det erstatter linja over om at prøven tas etter at 8.0d er flettet.

*Lagt til 2026-10-17 kl. 19:03:* demoen viser alle 10 fargekombinasjonene av de tre sjekkene på siste demodag (beslutningen 16.10 kl. 21:49 under story 2.12), flettet i `f21f927`, PR #58. Spesifikasjonen er `spec-3-4-alle-ti-kombinasjonene-paa-siste-demodag.md`. CI var grønn på head-en `33ca133` (kjøring 39051824634) og på main (39051953417).

### Story 3.4b: KI-tekstene i demoen

*Lagt til 2026-10-05, gruppens beslutning kl. 16:53.*

Som **faglærer eller sensor**, vil jeg se KI-teksten i demoen, så jeg ser hva
KI-laget gjør uten Ollama og uten å vente.

**Oppfyller:** FR-411 for KI-tekstene · **Begrenses av:** FR-602, FR-603,
FR-604, FR-605, `AD-8`, `AD-9`

**Kontroll — hva testen ser etter:**
- Demoen får ferdige KI-tekster for de oppdiktede dagene, laget med Gemma og
  merket med modellen
- De ferdige tekstene ligger i en fil i repoet, fordi demobasen aldri ligger der
  (`AD-9`). Demokommandoen leser fila og skriver tekstene inn i demobasen
- En test krever at grunnlaget for hver tekst stemmer med demodagen den hører
  til (FR-602)
- Tekstene består kontrollen i FR-603, og raden har tjenesten, modellen og
  hvordan modellen kjørte (FR-604, FR-605)
- **Ville feilet hvis:** demoen endret seg, og tekstene ble stående. Da forklarer
  KI en annen dag enn den siden viser

**Avhenger av:** 3.4, 10.2 og 10.3. **Én økt:** ja.

*Avgjort 2026-10-17 kl. 22:06 (gruppens svar i chatten med rådet):* KI-tekstene i demoen (story 3.4b) bygges søndag 18.10 rett etter de to README-PR-ene og før 2.9b, fordi demoen i dag ikke har noen KI-tekst.

*Lagt til 2026-10-18 kl. 20:55:* KI-tekstene i demoen er flettet i `ab81d3f`, PR #69 (spesifikasjonen `spec-3-4b-ki-tekstene-i-demoen.md`). 13 rader for siste demodag, laget én gang med `gemma4:e4b`, og alle besto kontrollen. Ordlista gjelder ikke KI-teksten før prompten versjon 3 (gruppens svar kl. 20:08). CI var grønn på head-en `8d632b0` (kjøring 39156153956) og på main (39156267219).

---

## Epic 4: KI kan tas i bruk uten å bryte godkjenningen

*Lagt til 2026-10-15 (gruppens svar på de ti spørsmålene i planen for KI-laget, instruksjonen kl. 15:53):* svarene er beslutninger. De som gjelder Epic 4:
- Svar 2: raden i `KILogg` står når den finnes, også når modellen feilet (FR-604).
- Svar 6: `0005` gir plass til dagsteksten i 10.6, med en dato som eneste emne. Et emne er da en meldings-id (plan A), et `(symbol, dato)`-par (plan B) eller en dato alene (FR-607).
- Svar 9: 4.0 er første PR i KI-laget.

Alle ti svarene står under Epic 10.

### Story 4.0: Nettsperren dekker hele testkjøringen

*Lagt til 2026-09-24.*

Som **gruppe**, vil vi at ingen del av testkjøringen kan nå nettet, så en
modelltjeneste som tas inn i Epic 4, ikke kan sende noe ut fra en test.

**Oppfyller:** — *(grunnlag for NFR-01)* · **Begrenses av:** `AD-8`

**Grunnen:** sperren i `tests/conftest.py` er en autouse-fixture med
funksjonsscope, og gjelder bare inne i testfunksjonene. Gruppen prøvde 23.09 en
fixture med `scope="module"`, som koblet seg til `192.0.2.1` uten
`NettverkISTest`; det forsøket er ikke ført i repoet. Kontrollert på nytt
24.09 uten nettkall: i en fixture med `scope="module"` var verken
`socket.connect` eller `socket.getaddrinfo` sperret, og `gethostbyname` er ikke
sperret i det hele tatt. Proxyvernet dekker i dag bare `requests` og `urllib`
(`getproxies`). En SDK for en modelltjeneste kan bruke et annet HTTP-bibliotek,
for eksempel `httpx`. Hvordan det leser proxyinnstillingene, er ikke
kontrollert; `httpx` er ikke installert.

**Kontroll — hva testen ser etter:**
- Socket-sperren settes i `pytest_configure` med `pytest.MonkeyPatch()` og
  fjernes i `pytest_unconfigure`. Fixturen beholdes for proxyvariablene
- Loopback slippes bare gjennom til porter som en socket i samme prosess lytter
  på (`socket.socket.listen` pakkes inn). Da stoppes en proxy på loopback
  uansett bibliotek
- `gethostbyname`, `gethostbyname_ex` og `getfqdn` sperres også, så docstringen i `conftest.py` stemmer når den sier at testene ikke gjør navneoppslag *(lagt til 2026-09-27, G9)*
- `getaddrinfo`-erstatningen får signaturen `(host, port, *resten, **navngitt)`,
  og `AF_UNIX` slippes gjennom
- Tester for `connect_ex` og for en fixture med `scope="module"`. Docstringen i
  `test_loopback_slippes_gjennom` rettes: Flask-testklienten bruker ikke socket
  (kontrollert 24.09: ingen `socket.connect`-kall fra `test_client().get("/")`)
- **Ville feilet hvis:** en fixture med `scope="module"` kunne nå nettet

**Én økt:** ja.

*Lagt til 2026-10-15:* flettet i `dc43569`, PR #44.

### Story 4.1: Velg modelltjeneste og dokumentér betingelse 4

Som **gruppe**, vil jeg ha modelltjenestens egne vilkår sitert og datert, så vi
kan sende artikkeltekst inn uten å bryte godkjenningen vi fikk.

**Oppfyller:** — *(lukker betingelse 4 i EODHDs godkjenning)* · **Begrenses av:** ingen AD-er

**Kontroll — hva den ferdige storyen inneholder:**
- Tre kandidater vurdert, med tre svar hver: brukes innsendte data til trening, kan det slås av, og står det i **vilkårene** eller bare i markedsføringen
- Den valgte tjenesten har setningen sitert **ordrett**, med lenke og dato, i `docs/kilder-og-rettigheter.md`
- **Ville feilet hvis:** svaret ble hentet fra en produktside i stedet for vilkårene. En markedsføringspåstand kan endres uten varsel; en vilkårsklausul kan siteres

**Én økt:** ja. Papirarbeid, ingen kode.

> **Ingen AD-er begrenser denne — og den er ikke triviell.** Den er en
> beslutning om noe utenfor systemet, og spinen fikser bare det som holder
> delene av systemet fra å sprike. **Enhver story som sender artikkeltekst inn i
> en modell, er blokkert av denne.** Ikke anbefalt etter: blokkert.

*Merknad 2026-10-04:* det som sendes til modellen i v1, er våre egne resultater: fortegn, styrke, retning og antall. Det er ikke artikkeltekst, og ikke prosenter, forholdstall, kurser eller volumer. Betingelse 4 ble stilt for artikkeltekst. Vilkårene er likevel ført for hver tjeneste, slik storyen krever. Valget: en lokal modell, Gemma 4 E4B, er standard, og egne nøkler til Gemini, Anthropic API og OpenAI API er valg. Prøven står i `malinger.md` §19.

*Ferdig 2026-10-04:* skrevet i `dcbce6d` (vilkårene i `docs/kilder-og-rettigheter.md`), `28851b0` (plan B) og `a4b7171` (`prd.md`), uten PR, fordi bare dokumenter endres. Står i review til Marian eller Joakim har lest seksjonen.

*Lest 2026-10-05:* Marian sa kl. 17:29 at seksjonen er lest, og 4-1 er done.

### Story 4.2: `KILogg`-porten med minneimplementasjon

Som **utvikler**, vil jeg definere KI-loggen som én port før modellen finnes, så
arbeidet ikke venter på et valg som ikke er tatt, og så plan A og plan B logger
til samme sted.

**Oppfyller:** FR-604, FR-605 · **Begrenses av:** `AD-3`, `AD-7`

*Skrevet om 2026-09-23, før bygging.* Første versjon definerte loggen for
meldinger alene. Med plan B (Epic 5B) logges også forklaringer av signalet, per
aksje per dag. **Det er én logg, ikke to:** én port, én tabell. Sammenlikningen
i refleksjonsrapporten — hva KI bidro med over tid — skal kunne gjøres på tvers
av begge, og to logger med ulik form ville gjort den til to rapporter.

**Kontroll — hva testen ser etter:**
- Hver rad har de **felles feltene**: dato, modell, promptversjon, hva regelen
  sa, og hva KI la til
- Hver rad har **ett emne**: enten en meldings-id (plan A) eller et
  `(symbol, dato)`-par (plan B). En rad med begge, eller ingen av dem, avvises
- Én lesing gir rader av begge slag, ordnet etter dato
- Porten har **ingen** `slett` og **ingen** `endre`
- Hele porten prøves mot minneimplementasjonen, uten database
- **Ville feilet hvis:** promptversjon og modell var utelatt fra raden. Justeres
  prompten i oktober, blir eksempelsettet en blanding av flere systemer som ser
  ut som ett
- **Ville også feilet hvis:** plan B fikk sin egen port eller tabell. Da kan ikke
  bidraget sammenliknes på tvers, og AD-3 er brutt

**Åpent, avgjøres når plan A bygges:** FR-604 nevner også utsteder, kategori,
publiseringstidspunkt og usikkerhetsmerke. Om de lagres i loggen eller slås opp
via meldings-id, avgjøres da. FR-604 står uendret til 28.09.

**Én økt:** ja. **Ingen avhengighet til Epic 1** — porten vet ikke om
lagringsformen.

*Lagt til 2026-10-15:* flettet i `a1d22f1`, PR #45.

### Story 4.3: SQLite-adapter for `KILogg`

Som **gruppe**, vil jeg at KI-loggen overlever en omstart, så eksempelsettet fra
én ukes drift finnes når det skal brukes.

**Oppfyller:** FR-604 · **Begrenses av:** `AD-4`, `AD-7`, `AD-16`

**Kontroll — hva testen ser etter:**
- `ki_logg`-tabellen opprettes av en nummerert migrasjon *(29.09: den blir
  `0005`, fordi `0004` er målingene i 2.1c)*
- En skrevet rad finnes etter omstart
- Ingen vei gjennom adapteren kan slette eller endre en eldre rad
- **Ville feilet hvis:** tabellen ble opprettet utenfor migrasjonsløperen. Da har to utviklere hvert sitt skjema, og `AD-16` er brutt av den første som kjørte

**Én økt:** ja. **Avhenger av Epic 1.**

*Lagt til 2026-10-15:* flettet i `3a089c8`, PR #46. Hentingen 16.10 kjører migrasjonen 0005 på ose.db.

---

## Epic 5: KI-laget i drift 🔒

*Ute av v1 fra 2026-09-28 (plan B, punkt 1 i `prd.md` §8).* Storyene står som plan for en senere versjon.

> **Blokkert.** Av åpent punkt 5b (betingelse 4, løses av story 4.1) **og**
> åpent punkt 1 og 19 (Euronext). Et nei 28.09 stryker hele epicen, fordi alle
> FR-6xx handler om meldinger.
>
> Storyene er skrevet likevel. En blokkert epic uten stories ser billigere ut
> enn den er, og da blir et nei vanskeligere å vurdere.

*Lagt til 2026-10-13, endringsforslaget 13.10 (punkt 4.8), godkjent av Marian kl. 12:46:* storyene under gjelder kravene slik de sto før 05.10: 5.1 FR-601, som gjelder begge planene, 5.2 FR-602A, 5.3 FR-603A og 5.4 FR-606A (`prd.md` §4.6A). At «alle FR-6xx handler om meldinger», gjelder A-variantene.

### Story 5.1: Av/på-bryteren i grensesnittet 🔒

Som **person som ser demonstrasjonen**, vil jeg se KI-laget slås av og på mens
jeg ser på, så bidraget er noe jeg kan kontrollere og ikke noe jeg må tro på.

**Oppfyller:** FR-601 · **Begrenses av:** NFR-04

**Kontroll — hva testen ser etter:**
- Bryteren finnes i grensesnittet, ikke i en konfigurasjonsfil
- Med laget av svarer markedsoversikten like raskt
- En treg eller utilgjengelig modell stopper ikke hovedflyten
- **Ville feilet hvis:** bryteren var et miljøvariabelflagg. Da kan bidraget ikke vises fram under demonstrasjonen, som er hele grunnen til at kravet finnes

**Én økt:** ja.

### Story 5.2: Visningen når laget er av 🔒

Som **bruker**, vil jeg at meldingene fortsatt vises når KI er av, merket «ikke
vurdert», så av og på er sammenlignbart.

**Oppfyller:** FR-602, del av FR-203 · **Begrenses av:** NFR-04, NFR-05

**Kontroll — hva testen ser etter:**
- Med laget på vises KI-forklaringen per melding i aksjedetaljen, og med laget
  av «ikke vurdert» (FR-203) *(lagt til 2026-09-24)*
- Samlekategorien vises med laget av, merket «ikke vurdert»
- Antallet meldinger er **det samme** av og på
- **Ville feilet hvis:** meldingene forsvant når laget slås av. Da blander visningen sammen «færre meldinger» og «uforklarte meldinger», og sammenligningen blir meningsløs

**Én økt:** ja.

### Story 5.3: Usikkerhet som forbehold 🔒

Som **bruker**, vil jeg se at en vurdering er usikker der den står, så jeg ikke
må gjette hvorfor noe er sortert ned.

**Oppfyller:** FR-603 · **Begrenses av:** NFR-04, NFR-06

**Kontroll — hva testen ser etter:**
- Usikkerhet avledes av de tre observerbare kjennetegnene, ikke av en score fra modellen
- En usikker vurdering vises **der den står**, ikke lenger ned i lista
- **Ville feilet hvis:** usikkerhet ble håndtert ved å sortere meldingen ned. Da er informasjonen borte, og brukeren ser en rekkefølge uten å vite hvorfor

**Én økt:** ja. **Merk:** kjennetegn 1 bærer svakt når utstederen selv er
avsender — åpent punkt 6.

### Story 5.4: Relevansskalaen med tre verdier 🔒

Som **bruker**, vil jeg at samlekategorien sorteres i tre nivåer med det laveste
skjult men ikke borte, så jeg kan kontrollere hva som ble sortert vekk.

**Oppfyller:** FR-606 · **Begrenses av:** `AD-7`

**Kontroll — hva testen ser etter:**
- De tre verdiene er de samme som relevanseksperimentet bruker
- «Lite relevant» er skjult bak en bryter, ikke fjernet
- Hver vurdering lagres med promptversjon og modell
- **Ville feilet hvis:** skalaen fikk andre nivåer enn eksperimentet. Da kan resultatene ikke sammenlignes, og eksperimentet mister sin funksjon

**Én økt:** ja. **Merk:** hvor grensen går, er åpent punkt 2 og kan ikke avgjøres
på papir.

---

## Epic 10: KI forklarer signalet (plan B) 🔀

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* i v1 står 10.5, lenken til investorsiden, og 10.7, egne nøkler, som briefen v8 lover, og 10.4 for suksessmålet. 10.6 og 10.8 er «Ekstra, hvis tiden rekker», etter regelen kl. 14:48. 10.1–10.3 er flettet.

*Het Epic 5B til 28.09.* *Utløst 2026-09-28:* Euronext ga ikke tillatelse innen fristen, og epicen bygges i v1. Nummeret ble endret fordi BMAD-skriptet bare leser epics med hele tall.

> **Utløses av nei eller taushet fra Euronext 28.09.** 5B.1 kan bygges før
> det, fordi den ikke sender noe. Plan A og B utelukker ikke hverandre.

*Lagt til 2026-10-15 (gruppens svar på de ti spørsmålene i planen for KI-laget, instruksjonen kl. 15:53):* svarene er beslutninger:
1. Kveldshentingen går på PC-en den går på i dag (15,7 GB og RTX 4070), med Ollama i Docker som i `malinger.md` §19, alltid med grafikkort. Ingenting installeres på Windows.
2. Raden står når den finnes, også når modellen feilet (FR-604).
3. Kjøres hentingen på nytt samme dag og vurderingen endrer seg, vises dagen uten KI-tekst (FR-602).
4. Bryteren huskes i en informasjonskapsel nå. 8.10b flytter bryteren til innstillingene og bruker samme kapsel.
5. «av» er et eget valg i `OSE_KI_TJENESTE`. `.env.example` har «av», og README-en sier hvordan KI slås på. Uten variabelen gjelder «lokal», som i FR-608. Ført også under FR-608 i PRD-en.
6. `0005` gir plass til dagsteksten i 10.6, med en dato som eneste emne.
7. 3.4b kommer rett etter 10.3. Demotekstene lages med Gemma lokalt av de oppdiktede demodataene, i en egen avtalt kjøring.
8. Adressen til Ollama er `OSE_KI_OLLAMA_URL`, med `http://127.0.0.1:11434` som standard og `http://ollama:11434` i compose. Porten publiseres bare på 127.0.0.1.
9. 4.0 er første PR.
10. «Antall» gjelder dagsteksten i 10.6, og 10.1 sender ikke antall. Ført også under §4.6 i PRD-en.

Rekkefølgen er PR A (4.0), B (4.2), C (4.3), D (10.1), E (10.2a: porten `Modell`, prompten og kontrollen i FR-603), F (10.2b: teksten i hentekommandoen) og G (10.3).

### Story 10.1: Grunnlaget som sendes — bare utledede verdier

*Het Story 5B.1 til 28.09.*

Som **gruppe**, vil vi at det som sendes til modellen, er bestemt av én ren
funksjon, så ingen kan sende rådata ved et uhell.

**Oppfyller:** — *(plan B, punkt 2)* · **Begrenses av:** `AD-1`, betingelse 4

**Kontroll — hva testen ser etter:**
- `ki_grunnlag(signal)` er ren logikk og gir bare: fortegnet og målingen for hver
  av de tre sjekkene, styrken og retningen
- Interessesjekken sendes som **forholdstall** (volum mot median), ikke som de to
  volumtallene. Forklaringsteksten i dag inneholder rå volumtall
  (`signalberegning.py:165`) *(29.09: løses i 2.1c, der teksten blir
  forholdstallet. Linja er nå 168)*
- Målingene tas fra `Sjekk.maaling` og `Sjekk.grense` (2.1c), og avrundes med
  samme funksjon som FR-706 *(lagt til 2026-09-29)*
- En test krever at ingen kurs og ingen volumverdi fra serien finnes i grunnlaget
- **Ville feilet hvis:** grunnlaget inneholdt dagens volum eller en kurs. Da
  sendes et rått datapunkt fra EODHD til en tredjepart, og det har ingen av
  svarene fra EODHD godkjent

*Rettet 2026-10-05:* grunnlaget har ingen målinger lenger (`prd.md` §4.6,
avgjort 2026-10-04). Punktene over om forholdstallet og om målingene fra
`Sjekk.maaling` og `Sjekk.grense` gjelder ikke grunnlaget lenger. De står for
historikken.
- `ki_grunnlag(signal)` er ren logikk og gir bare fortegnet for hver av de tre
  sjekkene, styrken og retningen
- En test krever at det ikke finnes desimaltall i grunnlaget
- Testen om at ingen kurs og ingen volumverdi finnes i grunnlaget, står
- **Ville feilet hvis:** grunnlaget hadde en prosent eller et forholdstall. Da
  sendes mer enn våre egne resultater, mot beslutningen 04.10

*Lagt til 2026-10-08, endringsforslaget 08.10 (punkt 4.5), godkjent av Marian kl. 08:04:*
- En aksje utenfor de 15 (FR-412) sendes med de samme utledede verdiene som de andre, og med merket «Utenfor målingen»
- **Ville feilet hvis:** KI-teksten for en aksje utenfor målingen ikke kunne si at grensene ikke er målt på den

**Én økt:** ja. Kan bygges før 28.09, fordi den ikke sender noe.

*Lagt til 2026-10-15:* flettet i `6855861`, PR #47.

### Story 10.2: Teksten lages i hentekommandoen og lagres i `KILogg`

*Het Story 5B.2 til 28.09.*

Som **bruker**, vil jeg at KI-teksten er klar når jeg åpner siden, så jeg aldri
venter på en modell.

**Oppfyller:** FR-603, *(plan B, punkt 1 og 4)* · **Begrenses av:** `AD-2`, `AD-8`,
`AD-10`, `AD-17`, NFR-02, NFR-04

*Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.8, svar 17), godkjent av Marian kl. 12:46:* her sto «**Oppfyller:** — *(plan B, punkt 1 og 4)*». Kontrollen i FR-603 er en ren funksjon i denne storyen.

**Blokkert av:** 4.1 (betingelse 4) og oppfølgingspunktet om EODHD og plan B.

**Kontroll — hva testen ser etter:**
- Modellen kalles fra én skallfil med én hentefunksjon, og funksjonen er injisert
  (AD-2). Testene bruker en falsk modell (AD-8)
- Teksten lages i hentekommandoen, rett etter vurderingen (samme mønster som
  AD-17), ikke når siden vises
- Feil eller tidsavbrudd hos modellen stopper ikke hentingen. Aksjen får ingen
  KI-tekst den dagen, og det logges (NFR-04)
- `KILogg` får én rad per aksje per dag, med emnet `(symbol, dato)`: hva
  regelforklaringen sa, hva KI la til, promptversjon og modell (FR-605, story 4.2)
- Kontrollen i FR-603 er én ren funksjon, som kalles før teksten logges som
  bestått. En test med falsk modell viser at hvert av de fire punktene stopper en
  tekst: feil tall, feil retning eller styrke, råd og gjetning. Et tall kan stå
  uten fortegn når teksten sier «falt» eller «steg». En tekst som stopper, vises
  ikke og logges med grunnen (FR-604) *(lagt til 2026-10-01)*
- **Ville feilet hvis:** KI-kallet lå i webserveren. Da koster hver visning av
  siden et kall, brukeren venter (NFR-02), og teksten som ble vist, finnes ikke
  igjen i loggen

*Lagt til 2026-10-05:* blokkeringen er løst. 4.1 er ført, og spørsmålet om
EODHD og plan B er avgjort 04.10 (vi spør ikke). **Avhenger av:** 4.0, 4.2 og
4.3. 10.2 skriver til `KILogg` (FR-604), og nettsperren må dekke hele
testkjøringen før noe kan kalle Ollama (`AD-8`).
*Lagt til 2026-10-05, kl. 17:13:* avhengighetene over er i tillegg til de som
fantes. 2.5 gjelder fortsatt, fordi teksten lages rett etter vurderingen, og
10.1 gjelder fortsatt, fordi 10.2 sender grunnlaget fra `ki_grunnlag`. Grafen
har fått «Epic 10.1 ──> Epic 10.2 (grunnlaget)».
- Porten `Modell`, og `ki_lokal.py` mot Ollama med `think: false`,
  temperatur 0 og seed (FR-608, `AD-2`)
- Prompten forklarer at fortegnet for interessen følger dagens kursendring og
  ikke volumet. Det er lærdommen fra Gemma i C-med i `malinger.md` §19
- Kontrollen i FR-603 med de nye ordlistene, tall skrevet med ord og «fordi» om
  regelen. En test med falsk modell viser hvert av dem (`AD-8`)
- Raden har tjenesten, modell-ID, seed, temperatur, om modellen kjørte med
  eller uten grafikkort, og Ollama-versjonen (FR-604, FR-605)
- Kjører ikke Ollama, eller feiler tjenesten, blir det ingen tekst og en rad i
  loggen, og hentingen går videre (NFR-04)

*Lagt til 2026-10-05, gruppens beslutning kl. 16:53:* den lokale modellen
starter ikke av seg selv.
- Ollama kommer inn i compose-fila som eget valg, med volumet `ollama`.
  Punktene fra 3.1 og 3.2 om Ollama og det tredje volumet gjelder her
- README-en får avsnittet om den lokale modellen, med minnet målt. Punktene fra
  3.3 om den lokale modellen og minnet gjelder her (regel 19)

**Én økt:** ja.

*Lagt til 2026-10-15 (gruppens svar kl. 23:32 på spørsmålene i PR F og G, instruksjonen kl. 23:33):* a) G (story 10.3) flettes i kveld, fordi hentingen for 15.10 er ferdig. b) «lokal» gjelder fortsatt når `OSE_KI_TJENESTE` mangler (svar 5 kl. 15:53 står). c) Hentingen sjekker først at Ollama svarer og har modellen. Gjør den ikke det, skrives ingen rader i `ki_logg` for dagen, og utskriften sier hvorfor og at samme kommando kan kjøres igjen samme kveld, med 0 kall til EODHD. Svarer den, skrives rader som før, også når modellen feiler for en aksje (svar 2). Grunnen: formålet med FR-604, at en tekst ikke kan lages på nytt til man får en man liker, holder, fordi ingen tekst ble laget.

*Lagt til 2026-10-16:* PR F (10.2b), der hentekommandoen lager KI-teksten, er flettet i `b13e50f`, PR #49, etter prøvekjøringen kl. 22:26–22:27 (`malinger.md` §32) og gruppens ja kl. 22:33. CI var grønn på head-en `26cf89c` (kjøring 38963318061). Storyen står som in-progress, fordi prompten versjon 2 (beslutningen kl. 22:33 under) bygges i 10.2.

*Avgjort 2026-10-16, gruppens beslutning kl. 22:33:* i prøvekjøringen (`malinger.md` §32) stoppet regel 4 i kontrollen 9 av 15 tekster, 8 på «skyldes» og 1 på «indikerer», også der ordet bare forklarte regelen. Prompten får versjon 2, som ber modellen forklare regelen med «fordi» og ikke bruke «skyldes» eller «indikerer». Kontrollen endres ikke. Det bygges lørdag 17.10, med en ny prøvekjøring på en fersk kopi av basen, og flettes før hentingen mandag 19.10. Er det ikke flettet da, går mandagens henting med `OSE_KI_TJENESTE=av`, så ingen dag får tekster med versjon 1.

*Lagt til 2026-10-16:* prompten versjon 2 (PR H, 10.2c) er flettet i `cafe067`, PR #55, etter gruppens ja kl. 23:51. CI var grønn på head-en `f3e52bd` (kjøring 38972334506). I prøvekjøringen 16.10 kl. 23:43–23:44 (`malinger.md` §34) besto 15 av 15 tekster, mot 6 med versjon 1 (§32), og modellen feilet for 0. Mandagens henting går med versjon 2, så reserven med `OSE_KI_TJENESTE=av` fra beslutningen kl. 22:33 trengs ikke. Med PR E, F og H er kontrollpunktene i storyen oppfylt, og 10-2 er done. Innstrammingen av kontrollen fra beslutningen kl. 23:51 under er en egen liten PR, ført i `deferred-work.md`.

*Avgjort 2026-10-16, gruppens beslutninger kl. 23:51 (svarene på de to spørsmålene fra instruksjonen kl. 23:35):* 1) Kontrollen strammes inn i en liten PR neste uke: et «fordi»-ledd må nevne en av sjekkene, ellers stoppes teksten. Føres også i `deferred-work.md`. 2) En ny promptversjon flettes når den består minst like mange tekster som versjonen før, i en prøvekjøring på samme dags data, og ingen tekst gjetter på en årsak utenfor regelen.

*Avgjort 2026-10-18 kl. 21:03 (gruppens svar):* hullet i kontrollen fra 3.4b rettes før byggestoppen mandag 19.10 kl. 20:40, så uka med logget drift går med den rettede kontrollen. Kontrollen i FR-603 leser da retningen og styrken også i formene Gemma skriver, som «Dette signalet er Negativt», «av typen Ingen» og «av styrke tre» (spesifikasjonen 10.2d). Prompten står, versjon 2.

*Lagt til 2026-10-18 kl. 22:49:* kontrollen i FR-603 leser retningen og styrken også i formene Gemma skriver, flettet i `3c2bd51`, PR #71 (spesifikasjonen `spec-10-2d-kontrollen-leser-formene-gemma-skriver.md`), før byggestoppen mandag. Ingen av de 79 KI-tekstene i sporede filer fikk et annet svar, så tekstene i demoen står. Det åpne punktet i spesifikasjonen for 3.4b er dermed lukket.

### Story 10.3: Visningen i aksjedetaljen

*Het Story 5B.3 til 28.09.*

Som **bruker**, vil jeg lese regelforklaringen først og KI-teksten som et tillegg,
så jeg alltid ser hva signalet faktisk bygger på.

**Oppfyller:** FR-601, FR-602, *(plan B, punkt 1)* · **Begrenses av:** NFR-04, NFR-05, NFR-06

*Rettet 2026-10-13, endringsforslaget 13.10 (punkt 4.8, svar 17), godkjent av Marian kl. 12:46:* her sto «**Oppfyller:** — *(plan B, punkt 1)*». Siden viser KI-teksten og sier hvorfor når KI er av (FR-601, FR-602).

**Kontroll — hva testen ser etter:**
- Regelforklaringen (FR-706) står først og er alltid synlig
- KI-teksten står under, merket som laget av KI, med modellnavnet
- Av/på-bryteren er synlig for brukeren. Med KI av er siden lik den som finnes i
  dag
- En dag uten KI-tekst sier det, i stedet for å vise et tomt felt
- En vakt på vår side: tekst med ord som «kjøp», «selg» eller «anbefal» vises
  ikke, men logges (NFR-06)
- KI-teksten leses med `ki_logg` mot `vurdering`, så teksten vises sammen med
  vurderingen den forklarer *(lagt til 2026-09-28, fra endringsforslaget)*
- Sammenligningen i FR-602 tar med målingene, avrundet som i FR-706 (2.1c)
  *(lagt til 2026-09-29)* *(rettet 2026-10-05: gjelder ikke lenger.
  Sammenligningen tar ikke med målingene, fordi grunnlaget ikke har dem
  (FR-602))*
- **Ville feilet hvis:** KI-teksten erstattet regelforklaringen eller sto før den.
  Da leses KI som kilden og regelen som en fotnote

*Lagt til 2026-10-05:*
- Modellnavnet vises med tjenesten, også for den lokale modellen, for eksempel
  «gemma4:e4b, lokal» (FR-602)
- Er tjenesten ikke tilgjengelig, er KI av, og siden sier hvorfor (FR-601)

**Én økt:** ja.

*Lagt til 2026-10-15:* flettet i `e728c37`, PR #50. Står som review: kontrollpunktet om at siden sier hvorfor når tjenesten ikke er tilgjengelig (FR-601), er ikke oppfylt. Med svar c kl. 23:32 skriver hentingen ingen rad når Ollama ikke svarer, og siden viser da bare «Ingen KI-tekst for denne dagen.» uten grunnen. Det trengs et sted der hentingen fører at tjenesten ikke svarte for dagen, og det avgjøres av gruppen.

*Lagt til 2026-10-15 (gruppens svar kl. 23:57 på spørsmålet i Utført-linja kl. 23:51, instruksjonen kl. 23:58):* siden sier hvorfor med det loggen kan vise. Har dagen ingen rader i `ki_logg` i det hele tatt, står det «Ingen KI-tekst for denne dagen: KI var slått av, eller modellen svarte ikke da hentingen gikk.» Har andre aksjer rader for dagen, men ikke denne, sier siden at teksten for denne aksjen ikke ble laget i hentingen. Den nøyaktige grunnen står i utskriften fra hentingen og i Utført-linja for den kvelden. Med dette regnes kontrollpunktet fra 05.10 om at siden sier hvorfor (FR-601), som oppfylt.

*Lagt til 2026-10-16 kl. 00:21:* PR 2 flettet i `4a22199`, PR #51 (ja kl. 00:16). Alle kontrollpunktene er oppfylt på main, og 10-3 er done. At siden med KI av er lik den som fantes, ble sjekket ved å sammenligne aksjesiden i demoen med kapselen av mot siden fra `8c3a58b`, før 10.3: eneste forskjell er bryteren og stilen dens, som kontrollpunktet over krever. At teksten vakten stopper «logges», er raden i `ki_logg`, som står (AD-7).

### Story 10.4: Måle bidraget — egen brukertest, etter 8.1

*Het Story 5B.4 til 28.09.*

Som **gruppe**, vil vi vite om KI-teksten faktisk hjelper, så refleksjonsrapporten
kan vurdere det kritisk i stedet for å anta det.

**Oppfyller:** suksessmålet «KI-bidrag i drift», tilpasset plan B · **Begrenses
av:** —

*Lagt til 2026-10-06:* «KI-bidrag i drift» er erstattet av «KI-forklaringen»
(`prd.md` §7, brief v8). 10.4 dekker «Én ukes drift er logget» i det
kriteriet, og brukertesten står som måling til refleksjonsrapporten.

**Egen test, ikke en del av 8.1** *(avgjort 2026-09-23)*. 8.1 måler skjermen
uten KI. 5B.4 måler KI-tillegget. Blandes de, vet ingen hva som ble målt.

**Kontroll — hva den ferdige storyen inneholder:**
- Samme person ser samme aksje først med KI av og deretter med KI på. Svarene
  noteres ordrett
- `KILogg` over minst én ukes drift: hvor ofte KI-teksten sa noe regelforklaringen
  ikke sa med ord, og hvor ofte den bare gjentok
- Et funn om at KI ikke hjelper, føres som funn og ikke som feil
- **Ville feilet hvis:** personen så KI-versjonen først. Da er det ikke mulig å
  måle hvordan siden fungerer uten

**Avhenger av:** 8.1 og 5B.3. **Én økt:** ja.

### Story 10.5: Lenke til selskapets side på NewsWeb

*Lagt til 2026-09-28, med plan B.*

Som **bruker**, vil jeg komme til selskapets side på NewsWeb med ett klikk fra
aksjedetaljen, så børsmeldingene er ett klikk unna når løsningen ikke viser dem.

**Oppfyller:** §2 i `prd.md` («Lenke fra aksjedetaljen til selskapets side på
NewsWeb») · **Begrenses av:** `AD-2`

Én lenke per aksje i aksjedetaljen. Lenken henter ingenting, og ingen kode i
`src/` henter fra NewsWeb.

**Kontroll — hva testen ser etter:**
- Aksjedetaljen har lenken for hver av de femten
- **Ville feilet hvis:** programmet hentet innholdet fra NewsWeb for å vise det.
  Da er det automatisert henting, som Euronexts vilkår forbyr uten tillatelse

**Forutsetning:** punktet «Lenken til NewsWeb (plan B)» under «Å følge opp» i
`docs/kilder-og-rettigheter.md` er gjort.

**Én økt:** ja.

*Utvidet 2026-09-30:*

- Aksjedetaljen har to lenker: selskapets side på NewsWeb og selskapets egen
  nettside, på norsk der den finnes. Begge gjelder aksjen siden viser, og ingen
  av dem henter noe.
- Adressene slås opp én gang per aksje og står sammen med navn og bransje,
  knyttet til symbolet fra Oslo Børs (EQNR), ikke til tickeren hos EODHD
  (EQNR.OL).
- Tickeren fra Oslo Børs står ved navnet øverst i aksjedetaljen.
- Kontrollpunkter: begge lenkene finnes for hver av de femten, og tickeren står
  ved navnet. Ville feilet hvis en lenke gikk til en annen aksje enn den siden
  viser.

*Rettet 2026-10-06, Marians beslutning:* appen lenker ikke til
`newsweb.oslobors.no`, `oslobors.no` eller `live.euronext.com`, fordi Euronexts
vilkår forbyr lenker uten tillatelse (`docs/kilder-og-rettigheter.md`, «Lenker
til Euronexts nettsteder (lest 2026-10-06)»). Aksjedetaljen lenker til
selskapets investorside, der mange selskaper viser dagens kurs og børsmeldingene
sine, og nevner NewsWeb uten lenke. Vi ber ikke Euronext om tillatelse, fordi
brevet 21.09 og purringen 22.09 ikke er besvart. Tittelen står.
- Ingen mal har en lenke til `newsweb.oslobors.no`, `oslobors.no` eller
  `live.euronext.com`, og en test krever det
- Lenken går til selskapets investorside, slått opp for hånd for hver av de 15
- I demoen er selskapene oppdiktet, så der vises ingen lenke. Hva som står i
  stedet, avgjøres når 10.5 planlegges
- **Ville feilet hvis:** en lenke til et av Euronexts nettsteder kom inn i en mal

*Avgjort 2026-10-19 kl. 16:03 (gruppens svar):* adressene til investorsidene er åpnet og godkjent: EQNR https://www.equinor.com/investors, DNB https://www.ir.dnb.no/, KOG https://www.kongsberg.com/investor-relations/, AKRBP https://akerbp.com/en/investor/, NHY https://www.hydro.com/en/global/investors/, FRO https://www.frontlineplc.cy/investor-relations/, VAR https://varenergi.no/en/investor/, TEL https://www.telenor.com/investors/, YAR https://www.yara.com/investor-relations/, MOWI https://mowi.com/investors/, ORK https://www.orkla.com/investors/, SALM https://www.salmar.no/en/investor/, GJF https://www.gjensidige.com/investor-relations/, DNO https://www.dno.no/en/investors/ og MPCC https://www.mpc-container.com/investors/.

### Story 10.6: KI-teksten om dagen på forsiden

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-02, Marians beslutning.*

Som **bruker**, vil jeg lese noen setninger om hele børsdagen under tabellen, så
jeg ser sammenhengen uten å regne selv.

**Oppfyller:** FR-607 · **Begrenses av:** FR-601, FR-602, FR-603, FR-604, FR-605, NFR-02, NFR-06

Grunnlaget er bare utledede tall regnet av kursene: hvor mange som skilte seg ut,
hvor mange som gikk bedre enn hovedindeksen, indeksens endring og snittendringen
per bransje, for dagen og for uka. Teksten lages én gang i hentekommandoen, med
ett kall til modellen per børsdag, og logges. Den står under tabellen, merket som
laget av KI, med modellnavnet.

**Kontroll — hva testen ser etter:**
- Grunnlaget har ingen kurser eller rådata fra EODHD
- Teksten lages i hentingen, aldri når siden vises
- En tekst som ikke består FR-603, vises ikke
- Bryteren slår av begge KI-tekstene
- **Ville feilet hvis:** teksten nevnte et tall som ikke står i grunnlaget, eller kunne leses som et råd

**Avhenger av:** 10.1, 10.2 og 10.3, FR-104 og FR-410 for hovedindeksen, og spørsmålet til EODHD om plan B, som raden i §8 sier.
**Én økt:** ja.

*Rettet 2026-10-05:* grunnlaget følger FR-607 slik det står nå: bare antall og
retninger, altså hvor mange som skilte seg ut, antall per retning, hvor mange
som gikk bedre enn hovedindeksen, retningen for hovedindeksen og antall opp per
bransje. Ingen prosenter. Avsnittet over om indeksens endring og snittendringen
per bransje gjelder ikke lenger. Om uka skal med som antall, avgjøres når
storyen bygges. Spørsmålet til EODHD er avgjort 04.10: vi spør ikke.
- Samme kontroll som i 10.2 (FR-603), også for tall skrevet med ord
- En test krever at det ikke finnes desimaltall i grunnlaget

*Lagt til 2026-10-08, endringsforslaget 08.10 (punkt 4.5), godkjent av Marian kl. 08:04:*
- Teksten gjelder lista som er aktiv (FR-412), og tallet på aksjer telles. Testen prøver en liste med færre enn 15 og en med 18
- **Ville feilet hvis:** grunnlaget sa «av 15» når lista hadde et annet antall

### Story 10.7: Egen nøkkel til Gemini, Anthropic og OpenAI

*Lagt til 2026-10-05, gruppens beslutning 04.10.*

Som **bruker med egen nøkkel**, vil jeg kunne la en tjeneste jeg selv har valgt,
skrive KI-teksten, på mine egne vilkår.

**Oppfyller:** FR-608 · **Begrenses av:** `AD-2`, `AD-8`, `AD-12`, FR-603,
FR-604, FR-605, NFR-04

**Kontroll — hva testen ser etter:**
- `ki_gemini.py`, `ki_anthropic.py` og `ki_openai.py`, hver for seg og med samme
  port `Modell` som `ki_lokal.py` (10.2)
- `OSE_KI_TJENESTE` velger tjenesten, og nøkkelen leses fra miljøet
  (`OSE_KI_GEMINI_NOKKEL`, `OSE_KI_ANTHROPIC_NOKKEL`, `OSE_KI_OPENAI_NOKKEL`)
- Mangler nøkkelen, eller feiler tjenesten, blir det ingen tekst og en rad i
  loggen. Det er ingen stille overgang til en annen tjeneste
- Nøkkelen står aldri i loggen, i en feilmelding eller på en side
- Testene bruker en falsk modell og gjør ingen nettkall (`AD-8`)
- **Ville feilet hvis:** appen gikk over til en annen tjeneste da den valgte
  feilet. Da sendes grunnlaget til en tjeneste brukeren ikke har valgt, på
  vilkår brukeren ikke har godtatt

**Avhenger av:** 10.2. **Én økt:** ja. Den er liten.

*Lagt til 2026-10-05, gruppens beslutning kl. 16:53:* README-en får avsnittet om
egne nøkler (regel 19). Punktet fra 3.3 om egne nøkler gjelder her.

### Story 10.8: ChatGPT med «Sign in with ChatGPT»

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-05, gruppens beslutning 04.10.* **Kandidat til v1.1.**

**Blokkert av:** oppfølgingspunktet «Brukes innholdet til trening når appen
bruker et ChatGPT-abonnement?» i `docs/kilder-og-rettigheter.md`. Ingen av
sidene som er lest, sier det.

Som **bruker med ChatGPT Plus eller Pro**, vil jeg kunne logge inn med ChatGPT,
så KI-teksten bruker abonnementet jeg har.

**Oppfyller:** FR-608 · **Begrenses av:** `AD-2`, `AD-8`, `AD-12`

**Kontroll — hva testen ser etter:**
- Innloggingen går via `127.0.0.1`, og tokenfila ligger under `data/ki/`, som er
  gitignorert (regel 10)
- Samme port `Modell` som de andre tjenestene
- Tokenet står aldri i loggen, i en feilmelding eller på en side
- **Ville feilet hvis:** tokenfila lå et sted git kunne ta med. Da kan en
  innlogging havne i det offentlige repoet

**Avhenger av:** 10.7. **Én økt:** avgjøres i planen.

---

## Epic 6: Børsmeldinger i oversikten 🔒

*Ute av v1 fra 2026-09-28 (plan B, punkt 1 i `prd.md` §8).* Storyene står som plan for en senere versjon.

> **Blokkert av åpent punkt 1 og 19.** Euronext forbyr automatisert henting uten
> tillatelse, og punkt 19 gjelder om innhold i det hele tatt kan sendes til en
> modelltjeneste.
>
> **Et nei stryker epicen i sin helhet — og tar Epic 5 med seg ned.**
> Logikken i `meldinger.py` er allerede bygget og testet; den blir liggende som
> kode uten datakilde.

### Story 6.1: Meldingslageret som port 🔒

Som **utvikler**, vil jeg at meldingene nås gjennom en port, så resten av
systemet ikke vet hvor de kom fra.

**Oppfyller:** — *(grunnlag for FR-404)* · **Begrenses av:** `AD-3`, `AD-2`

**Kontroll — hva testen ser etter:**
- `Meldingslager` har én skriver, og lesere går gjennom porten. *Het
  `Meldingskilde` til 2026-09-24*
- Hele porten prøves mot en minneimplementasjon
- **Ville feilet hvis:** meldingshentingen kalte nettet fra en modul utenfor skallet. `AD-2` krever én hentefunksjon per kilde, i sin egen skallfil

**Én økt:** ja.

### Story 6.2: Etterfylling med avkortingsvakt 🔒

Som **gruppe**, vil jeg at en avkortet henting stopper i stedet for å levere et
halvt resultat, så vi ikke bygger et meldingslager med usynlige hull.

**Oppfyller:** FR-404, FR-405 · **Begrenses av:** `AD-2`, `AD-20`

**Kontroll — hva testen ser etter:**
- `overflow: true` i svaret stopper hentingen og rapporterer feilen
- Et intervall som deles og hentes på nytt gir ikke dubletter i lageret
- `messageId` er primærnøkkel, så gjentatte svar er idempotente
- **Ville feilet hvis:** koden stolte på antall meldinger i stedet for `overflow`. Taket ligger mellom 557 og 601, og API-et returnerer HTTP 200 uten feilmelding når det kutter

**Én økt:** ja.

### Story 6.3: Deduplisering av språkdubletter 🔒

Som **bruker**, vil jeg se hver melding én gang, så den norske og engelske
versjonen ikke fyller lista med det samme.

**Oppfyller:** FR-501 · **Begrenses av:** `AD-14`, `AD-20`, NFR-05

**Kontroll — hva testen ser etter:**
- Dedupliseringen skjer **før** kategorifilteret
- To oversettelser av samme melding gir én rad, og den norske vinner
- Dublettnøkkelen tåler at tidsstemplene kommer i ulik representasjon
- **Ville feilet hvis:** rekkefølgen ble snudd. Da telles dubletter som passerer filteret to ganger — og `AD-14` finnes nettopp for det

**Én økt:** ja. **Merk:** `gjett_spraak` slår systematisk feil for Vår Energi,
åpent punkt 16. Storyen må ikke arve feilen.

### Story 6.4: Kategorifilteret i tre bøtter 🔒

Som **bruker**, vil jeg at rutinemeldinger sorteres bort av regler, så KI-laget
bare får det reglene ikke kan skille.

**Oppfyller:** FR-502 · **Begrenses av:** `AD-14`, `AD-1`

**Kontroll — hva testen ser etter:**
- Hver kategori havner i nøyaktig én bøtte
- En ukjent kategori vises merket «ukjent kategori» og sendes **ikke** til KI
- Filteret er ren logikk uten I/O
- **Ville feilet hvis:** ukjente kategorier ble sendt til KI-laget likevel. Prompten er skrevet for samlekategorien, og et svar som ser like sikkert ut men kommer fra en modell utenfor sitt område, er verre enn ingen vurdering

**Én økt:** ja.

### Story 6.5: Meldinger i aksjedetaljen 🔒

Som **bruker**, vil jeg se meldingene som gjelder aksjen der jeg leser om den,
så jeg slipper å lete et annet sted.

**Oppfyller:** FR-503, del av FR-203 · **Begrenses av:** `AD-1`, NFR-05

**Kontroll — hva testen ser etter:**
- Meldingene vises i aksjedetaljen, filtrert etter FR-502
- Eks.dato vises ikke som melding, men som merking
- **Ville feilet hvis:** utbyttemerkingen tok eks.dato herfra i stedet for fra kursserien. Da hviler FR-407 på en epic som kan strykes
- *Lagt til 2026-09-25:* telleren for funnet og vist, og bryteren Anbefalt/Alle
  (FR-203). Med Alle vises også det som er filtrert bort, merket med grunnen
- **Ville også feilet hvis:** bryteren endret hva KI-laget vurderer. Da kan KI
  på og av ikke sammenlignes (FR-602)

**Én økt:** ja.

---

## Epic 7: Kommende finansielle hendelser 🔒

*Ute av v1 fra 2026-09-28 (plan B, punkt 1 i `prd.md` §8).* Storyene står som plan for en senere versjon.

> **Blokkert av åpent punkt 1 (Euronext) og 12 (horisont og hendelsestyper).**
> *Rettet 2026-09-27:* her sto også «3 (kilde for handelskalenderen)». Punkt 3
> gjelder hvilke dager børsen er åpen, ikke finanskalenderen, og er lukket 27.09.
>
> **Et nei stryker epicen, men tar ingenting med seg ned** — ingen annen epic
> leser kalenderen.

### Story 7.1: Kalenderkilden og koblingen til selskap 🔒

Som **utvikler**, vil jeg koble kalenderhendelser til våre femten aksjer, så
hendelsene kan vises på riktig aksje.

**Oppfyller:** FR-301 · **Begrenses av:** `AD-2`, `AD-3`

**Kontroll — hva testen ser etter:**
- Koblingen skjer gjennom en oppslagstabell som vedlikeholdes manuelt
- En hendelse uten treff i tabellen forkastes ikke stille, men føres
- **Ville feilet hvis:** koblingen antok at kalenderen oppgir ticker eller ISIN. Den gjør ikke det, og det er grunnen til at tabellen må finnes

**Én økt:** ja.

### Story 7.2: Hendelser innenfor horisonten 🔒

Som **bruker**, vil jeg se hva som er på vei for aksjen, så jeg vet om det
kommer noe før jeg handler.

**Oppfyller:** FR-302, del av FR-203 · **Begrenses av:** `AD-1`, NFR-05

**Kontroll — hva testen ser etter:**
- Bare hendelser innenfor horisonten vises
- Hendelsestypene er de kalenderen oppgir
- **Ville feilet hvis:** horisonten ble hardkodet uten at åpent punkt 12 var avgjort. Tallet står i dag som `[FORELØPIG] 90` og er antatt

**Én økt:** ja.

### Story 7.3: Når kalenderen ikke svarer 🔒

Som **bruker**, vil jeg at resten av siden virker selv om kalenderen er nede, så
én kilde ikke tar ned aksjedetaljen.

**Oppfyller:** FR-303 · **Begrenses av:** NFR-03, `AD-15`

**Kontroll — hva testen ser etter:**
- Kalenderfeil gir en beskjed i seksjonen, ikke en feilside
- Signalet, grafen og meldingene vises som vanlig
- **Ville feilet hvis:** kalenderkallet lå i samme try-blokk som resten av siden. Da tar én kilde ned hele detaljen, stikk i strid med NFR-03

**Én økt:** ja.

---

## Epic 8: Tydelig for den som ikke har bygget den

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* i v1 står 8.3, Min liste, som briefen v8 lover, og 8.1 og 8.2. 8.4–8.14, 8.10b, 8.17, 8.18 og 8.19 er «Ekstra, hvis tiden rekker», etter regelen kl. 14:48. 8.0–8.0e, 8.15 og 8.16 er flettet.

### Story 8.0: De rene feilene i de to skjermbildene

*Lagt til 2026-09-29, fra gjennomgangen av skjermbildene 29.09 og regel 21.*

Som **bruker**, vil jeg at tallene står på norsk, at jeg ser hvilke aksjer som skiller seg ut og hva jeg kan klikke på, og at siden ikke sier noe som ikke stemmer, så 8.1 tester skjermbildene og ikke feil vi kjenner fra før.

**Oppfyller:** NFR-05, FR-705, navigasjonen i FR-101 · **Begrenses av:** FR-101–103, FR-706, NFR-06, regel 21

**Kontroll — hva testen ser etter:**
- Tallene følger regel 21 i begge skjermbildene: sluttkurs, endring og målingene. Én funksjon formaterer, og «-0,00» vises aldri
- Endringen i oversikten har to desimaler, som i dag, så rekkefølgen i FR-102 kan leses av
- En måling som blir lik grensen etter avrunding uten å være det, vises med så mange desimaler at forskjellen synes
- En aksje som skiller seg ut, er merket med tekst og ikke bare farge, og tabellen har fortsatt nøyaktig fem kolonner
- Selskapsnavnet ser ut som en lenke og har synlig fokus, og veien tilbake i aksjedetaljen er like tydelig
- Fotnoten i aksjedetaljen og docstringene i `app.py` og `aksjedetalj.py` sier det som stemmer etter plan B
- Tekst brukeren ser, har æ, ø og å (i dag står «for aa regne signal»)
- Datoen over tabellen avhenger ikke av sorteringen
- **Ville feilet hvis:** en rad med styrke 2 og en med styrke 1 så like ut for en som ikke ser farger, eller «-1,2 % mot 1,2 % standardavvik» sto ved en sjekk som ga -1

**Avhenger av:** ingen. 2.1c bruker samme funksjon når forklaringen lages av `maaling` og `grense`. **Én økt:** ja.

*Ferdig 2026-09-30:* flettet i `33317df`, PR #15.

### Story 8.0b: Hjelp bak et spørsmålstegn

*Lagt til 2026-10-01, Marians beslutning.*

Som **bruker**, vil jeg kunne trykke på et «?» og få forklart det appen viser, så
jeg forstår tallene uten å spørre noen.

**Oppfyller:** raden «Hjelp bak et spørsmålstegn» i v1.1-tabellen i `prd.md` §8 ·
**Begrenses av:** FR-701, FR-703, FR-704, NFR-06

Et «?» på begge skjermbildene åpner et lite vindu med fast tekst, uten nettkall og
uten KI. Det sier hva hver sjekk måler (FR-701), hvorfor akkurat disse tre (den
nye delen i §6 i `begrunnelser.md`), at grensene er valgt etter målinger over 199
børsdager (`malinger.md` §7.4 og §9), hvorfor retningen oftere blir positiv i en
stigende periode («Åpent punkt» i §6), og at signalet ikke sier noe om
fremtiden (FR-703, NFR-06).

Hjelpetekstene ligger i én fil, ikke spredt i malene, så et ord kan endres ett
sted. Min liste (8.3) bruker de samme.

**Kontroll — hva testen ser etter:**
- Tall i teksten, som 50 dager og 1,5 ganger, hentes fra `Parametre`, og en test krever det
- En test sjekker at hver tekst malene ber om, finnes i fila
- «Ingen» og «Ukjent» forklares hver for seg
- Retningen forklares med ordene i FR-704
- **Ville feilet hvis:** teksten sa noe koden ikke gjør, noe som ikke står i en kilde, eller noe som kan leses som et råd

**Avhenger av:** 8.0. Ferdig før 8.1, så testen viser om hjelpen blir brukt.
**Én økt:** ja.

*Lagt til 2026-10-05, Marians beslutning kl. 21:23:* i oversikten står et «?» ved overskriften Signalstyrke. I dag forklares 0–3 bare i fotnoten nederst.

*Lagt til 2026-10-11, Marians beslutning:* fotnotene under tabellene (funn 23 i gjennomgangen av 8.0b, `deferred-work.md`) tas i 8.0c, ikke før flettingen.

*Ferdig 2026-10-12:* flettet i `8d70762`, PR #29.

### Story 8.0c: Tydelig merking, ord ved sjekkene og datoer på grafen

*Lagt til 2026-10-05, fra rådets gjennomgang av sidene og Marians beslutning kl. 21:23.*

Som **bruker**, vil jeg se med en gang hvilke aksjer som skiller seg ut, lese hva hver sjekk ga uten å tolke et fortegn, og se datoene langs grafen, så 8.1 tester skjermbildene og ikke feil vi kjenner fra før.

**Oppfyller:** designregler §3 for tabellen, FR-705, FR-706, FR-201 · **Begrenses av:** FR-101, FR-103, FR-704, NFR-05, NFR-06

**Kontroll — hva testen ser etter:**
- Signalstyrken i oversikten står som «N av 3», som i aksjedetaljen. 3 av 3 får gul ring (designregler §3). 2 av 3 merkes med mer enn lys bakgrunn, uten gult. «skiller seg ut» står fortsatt, og tabellen har fortsatt fem kolonner
- Ga-kolonnen viser tallet og et ord: positiv ved +1, negativ ved -1 og ingen utslag ved 0. Positiv og negativ bygges av konstantene i `signalberegning.py`, som retningen
- Kursgrafen har et merke ved første børsdag i hver måned, med norsk månedsnavn. Merket står på samme x som punktet for den dagen i kurslinja. Datoene i bildeteksten står fortsatt
- **Ville feilet hvis:** en rad med 2 av 3 bare skilte seg fra en med 1 av 3 ved lys bakgrunn, det sto opp eller ned ved en sjekk, eller et månedsmerke sto under feil dag fordi merkene ble spredd etter kalenderen, mens linja har lik avstand per børsdag

*Lagt til 2026-10-05, Marians beslutning kl. 22:24:* 05.10, den andre dagen med lagret vurdering, fikk ingen av aksjene 2 av 3 eller mer (4 fikk 0 og 11 fikk 1, dagsfila kl. 22:08), så ingen rad var merket, og siden sa ikke at ingen skilte seg ut. Det skjer 5 av 199 dager i målingene (FR-705).
- En dag der ingen aksje har styrke 2 eller mer, står det over tabellen: «Ingen aksjer skilte seg ut: ingen fikk 2 av 3 eller mer.»
- Tallet 2 hentes fra `Parametre` (terskelen i FR-705), ikke skrevet fast i malen, og en test krever det
- Setningen står ikke når minst én aksje har styrke 2 eller mer, og ikke når ingen rad har en vurdering
- **Ville feilet hvis:** setningen sto en dag der en aksje hadde 2 av 3, eller manglet en dag der alle hadde 0 eller 1

**Funnene bak** (rådets gjennomgang 05.10): signalstyrken 0–3 forklares bare i fotnoten. Radene som skiller seg ut, har bakgrunnen `#fafafa`, som er nesten hvit, og ellers bare den lille teksten «skiller seg ut». Ga-kolonnen viser bare +1, -1 og 0. Grafen har datoer bare i bildeteksten. Ordene ved sjekkene er FR-704 sine, positiv og negativ, ikke opp og ned (FR-103, endret 21.09).

**Avhenger av:** 8.0. Ferdig før 8.1, som 8.0b, så brukertesten ikke finner det vi alt vet. **Én økt:** ja.

*Lagt til 2026-10-11, Marians beslutning:*
- Overskriftene over tallkolonnene står over tallene, også i tabellene i aksjedetaljen
- Merket i demoen sier «Demoversjon» foran «Eksempeltall: …», og «Eksempeltall» står (FR-411, NFR-08)
- En linje nederst på alle sidene sier at appen er under arbeid, styrt av én innstilling, og `docs/innlevering.md` får et punkt om å bytte den ved innleveringen
- Radene i aksjedetaljen med sjekkene som slo ut, har også `#fafafa` og synes nesten ikke. De merkes så de synes, og hjelpeteksten «Målt mot» («lys bakgrunn») følger merkingen
- Planen avgjør «Oslo Børs ·» over tabellen i demoen (`deferred-work.md`, 10.10)
- Planen avgjør fotnotene under tabellene. De bruker ordene i FR-703, mens hjelpen sier det enklere. Forbeholdet om kjøp og salg står synlig (NFR-06), og raden for NFR-06 i denne fila, som siterer fotnoten, får en datert linje hvis den endres
- Planen avgjør om hjelpen i demoen skal si at målingen over 199 børsdager er gjort på ekte kurser (funn 21 i gjennomgangen av 8.0b)

*Lagt til 2026-10-13, endringsforslaget 13.10 (punkt 4.1, 4.3 og 4.4, svar 2 og 4), godkjent av Marian kl. 12:46:*
- Hver tekst bak «?» har høyst 3 setninger. Unntak: «Grensene» og «Hvorfor retningen oftere er positiv», som forklarer en måling
- Tekstene som kan tas fra tavla, står ordrett, og de som må rettes, står med rettet ordlyd (punkt 4.2 og tekstene under svar 4 i endringsforslaget 13.10)
- Ordene følger ordlista i `designregler.md` §4, slik den står etter rettelsene i punkt 4.3. En test leter etter ordene ordlista har valgt bort («peker opp», «peker ned», «alle tre», «kroner») i malene og i hjelpetekstene
- Malene og hjelpen følger FR-701, FR-703 og FR-704 slik de ble rettet 13.10: fotnoten under oversikten slutter med «Signalstyrken sier hvor mange av de 3 sjekkene som slo ut, ikke om du bør kjøpe eller selge.», aksjesiden sier «Signalstyrken er hvor mange sjekker som slo ut:», og hjelpen for retning sier +1 og -1 (tabellen i punkt 4.4)
- Tall skrives med sifre («de 3 sjekkene»), og datoer som «22.09», med år bare når året er et annet. Formen bestemmes ett sted, med tester (regel 21)
- Tallene kommer fortsatt fra `Parametre`, og testene som krever det, står
- **Ville feilet hvis:** en tekst bak «?» hadde mer enn 3 setninger utenom unntakene, «peker opp» sto igjen i hjelpen for retning, eller en dato sto som 2026-10-12 på siden

*Lagt til 2026-10-13:* PR 1 flettet i `82271fb`, PR #35. PR 2 med datoene og månedsmerkene gjenstår.

*Lagt til 2026-10-13:* PR 2 flettet i `16e18d8`, PR #36. Begge PR-ene er flettet, og 8.0c er ferdig.

### Story 8.0e: Oversikten fra designforslaget

*Lagt til 2026-10-13, endringsforslaget 13.10 (punkt 4.6, nr. 1–4, svar 8, 11 og 12), godkjent av Marian kl. 12:46.*

Som **bruker**, vil jeg se i oversikten hvilke sjekker som slo ut og hvilke
aksjer som skilte seg ut, så jeg kan lese tabellen uten å åpne hver aksje.

**Oppfyller:** designforslaget, punkt 11 i samlelista · **Begrenses av:** FR-101,
FR-103, FR-703, FR-705, NFR-05, NFR-06

**Kontroll — hva testen ser etter:**
- Hver rad med vurdering viser T, B og I med +1, 0 eller -1, skrevet «T +1», i cellen for signalstyrke, under «N av 3». Tabellen har fortsatt fem kolonner (FR-101)
- Verdiene leses fra den lagrede vurderingen, aldri regnet på nytt (FR-101)
- En rad uten vurdering viser grunnen, som i dag, og ingen T, B eller I
- Radene med styrke på terskelen eller mer står under «Skilte seg ut», og de andre under «Øvrige aksjer». Terskelen kommer fra `Parametre` (FR-705). Er ingen over terskelen, står setningen fra 8.0c (05.10) i stedet for «Skilte seg ut»
- Over tabellen står «N av M aksjer skilte seg ut <ukedag>», der N og M telles fra radene, og ukedagen er børsdagen vurderingene gjelder, på norsk
- Under overskriften står innledningen fra tavla, med rettet ordlyd: «OSE Signal er et regelbasert signal for aksjer på Oslo Børs: 3 faste sjekker måler kurs og volum mot aksjens egen historikk. Hos disse 4 slo minst 2 av 3 ut. Det viser hvor du kan se nærmere, ikke hva du bør kjøpe eller selge.» Tallene telles fra radene og `Parametre`. Under står «3 av 3» og hvilke aksjer som fikk utslag på alle 3 sjekkene, med navnene fra radene
- «Slik leser du tabellen» står over tabellen med 3 korte punkter. Det første er «Signalstyrke 0–3» fra tavla, uten setningen om klikk til klikket finnes. De to andre er tavlas tekster om retning og selskapsnavnet
- **Ville feilet hvis:** tabellen fikk en sjette kolonne, en rad med 1 av 3 sto under «Skilte seg ut», M var skrevet fast som 15, ukedagen var dagen siden ble åpnet og ikke børsdagen, eller en rad uten vurdering viste T, B og I

Delen «Dine egne aksjer» kommer med 2.12 (svar 11).

**Avhenger av:** 8.0c. **Én økt:** avgjøres i planen.

*Lagt til 2026-10-13:* PR 1 flettet i `85fe8a4`, PR #37.

*Lagt til 2026-10-14:* PR 2 flettet i `cfc373e`, PR #38. Begge PR-ene er flettet, og 8.0e er ferdig.

*Lagt til 2026-10-14 (gruppen 14.10 kl. 21:04 og 21:06):* M i «N av M aksjer» er alle aksjene i lista, også de uten kurser, ikke bare radene. Det gjelder overskriften, linja under den og «… av M aksjer ble vurdert». Dette erstatter «N og M telles fra radene» over for M. Bygges i 8.0d, PR 2b (spesifikasjonen for 8.0d).

### Story 8.0d: Utseendet fra designforslaget

*Lagt til 2026-10-11, Marians beslutning kl. 12:13.*

Som **gruppe**, vil vi at sidene ser ut som designforslaget i designtavla, så
demoen sensor ser, har det utseendet vi har valgt.

**Oppfyller:** `designregler.md` §1, og reglene planen skriver inn i `designregler.md` ·
**Begrenses av:** FR-411, NFR-06, NFR-08

**Kontroll — hva testen ser etter:**
- Planen skriver reglene for utseendet inn i `designregler.md`, med dato og grunn, og gruppen godkjenner dem før noe bygges: farger, skrift, stripa øverst, kolonneraden, avstander og fokus. Tavla ligger i Claude og ikke i repoet, så rådet gir utdraget fra den
- Oversikten, aksjedetaljen og feilsiden følger reglene, også i demoen, og «Eksempeltall» synes like godt som før
- Skriften fra §1: filene ligger i appen med lisensen, ingen skrift eller skript hentes fra nettet, og tallcellene har tabelltall, med testene som sto i 8.2
- Tekst har kontrast på minst 4,5:1, og farger som skal skilles, skiller seg også i lyshet
- Ingen nye funksjoner og ingen knapp til en side som ikke finnes. Knapperaden kommer med 8.3
- **Ville feilet hvis:** en side hentet noe fra nettet, eller utseendet tok inn en funksjon som ikke er bygget

**Avhenger av:** 8.0b og 8.0c. **Én økt:** avgjøres i planen.

*Lagt til 2026-10-13, endringsforslaget 13.10 (punkt 4.3 og 4.6, svar 5, 12 og 18, og N3), godkjent av Marian kl. 12:46:*
- Lista over det planen skriver inn i `designregler.md`, får også rekkefølgen av delene på hver side og det grå feltet fra tavla
- 50-dagers snittet i kursgrafen er heltrukket, og hjelpeteksten om kursgrafen følger (i dag «den stiplede er snittet» i `src/hjelpetekster.py`). Stiplet linje er bare for hovedindeksen (`designregler.md` §4)
- Tilbakelenken på aksjesiden har tekst uten pil. Pilene er bare for retning (FR-103)
- Symbolene for de 13 bransjene (N3, `designregler.md` §4)
- 8.0d avhenger også av 8.0e, så utseendet legges på den nye oversikten
- **Ville feilet hvis:** snittet var stiplet, hjelpen sa noe annet enn grafen, eller en pil sto ved noe annet enn retningen

*Lagt til 2026-10-14:* PR 1 flettet i `e862743`, PR #39. IBM Plex Sans har ikke `tnum`, men sifrene er like brede, så testen fra 8.2 krever like brede sifre i hver fil og `tnum` i Newsreader (`designregler.md` §1 og §5).

*Lagt til 2026-10-14:* PR 2 flettet i `179b415`, PR #40. Fargene ved en aksje er som i originalen (`designregler.md` §3, 14.10).

*Lagt til 2026-10-14:* PR 2b flettet i `8c9f8b7`, PR #41.

*Lagt til 2026-10-14 (gruppen kl. 19:59, «ja til begge»):* «2 av 3» får den hvite pillen med svart kant fra originalen (utdraget §6), med den lys oransje streken som før (`designregler.md` del 5). Sorteringen (8.15) kommer rett etter 8.0d.

*Lagt til 2026-10-15:* PR 3 flettet i `f7c5e64`, PR #42. Alle tre PR-ene er flettet, og 8.0d er ferdig.

### Story 8.1: Brukertest rett etter Epic 2

Som **gruppe**, vil vi se en person utenfor gruppen bruke løsningen tidlig, så
vi vet om FR-706 faktisk forklarer før vi bygger mer rundt den.

**Oppfyller:** suksessmålet «Brukerutfall», PRD §7 · **Begrenses av:** FR-706,
NFR-05, NFR-06

Suksessmålet, ordrett fra `prd.md`: «En person utenfor gruppen gjennomfører
hovedflyten og forklarer uoppfordret hvorfor en aksje skiller seg ut | Minst 1
person, under 5 minutter, uten hjelp | Før prosjektinnlevering».

**Kontroll — hva den ferdige storyen inneholder:**
- Én person utenfor gruppen, uten hjelp, med ekte data fra siste henting og begge skjermbildene
- Tiden måles fra det første skjermbildet vises til forklaringen er gitt. Terskelen er under 5 minutter
- Forklaringen personen gir, er notert **ordrett**, ikke referert
- Funnene er ført i `docs/` med dato, sammen med hva som endres og hva som ikke endres
- **Ville feilet hvis:** personen ble spurt «hvorfor skiller denne seg ut?». Da er forklaringen oppfordret, og testen måler om personen kan svare på et spørsmål, ikke om skjermen forklarer

**Spørsmål testen skal svare på** *(lagt til 2026-09-23)*: **Er oversikten for
tett med 15 rader?** 15 er valgt av kvoten, ikke av skjermen, og antall rader
per skjermbilde avgjøres ikke før testen har svart. Svaret observeres, det
spørres ikke om: stopper personen, scroller tilbake eller mister raden de leste,
noteres det, med tidspunkt.

**Tidspunkt:** rett etter Epic 2, ikke før innlevering. Suksessmålets frist
«Før prosjektinnlevering» står fortsatt som ytre grense.

*Lagt til 2026-10-01:* 2.9 og 2.9b er ferdige før testen. Testen får et spørsmål til, som observeres og ikke spørres om: legger personen merke til indeksen og søylene?

**Én økt:** ja.

### Story 8.2: UX-gjennomgang av de to skjermbildene med `[CU] bmad-ux`

Som **gruppe**, vil vi at de to skjermbildene er vurdert som design, så
inntrykket ikke bare hviler på at logikken er riktig.

**Oppfyller:** — *(oppfølging av beslutningen 22.09 om å hoppe over `bmad-ux`)* ·
**Begrenses av:** FR-101–103, FR-201–204, FR-706, NFR-05, NFR-06

**Kontroll — hva den ferdige storyen inneholder:**
- `[CU] bmad-ux` er kjørt som en **gjennomgang** av skjermbildene som finnes, ikke som design fra bunnen
- Funnene fra 8.1 er brukt som grunnlag
- Et dokument viser at designet ble vurdert, med konkrete forbedringer. Hver forbedring er knyttet til et skjermbilde og et krav
- Forbedringene som tas inn, blir egne små endringer med test
- **Ville feilet hvis:** gjennomgangen endte i nye skjermbilder eller ny funksjonalitet. Da er det design fra bunnen og en utvidelse av omfanget, ikke en gjennomgang

**Føring** *(lagt til 2026-09-23, fra v1.1-idéene i `prd.md` §8)*: gjennomgangen
skal si **hvordan et tredje skjermbilde ville passet inn** i navigasjonen, uten å
bygge det. Det er et svar på papir, ikke en endring.
*Rettet 2026-09-30:* Min liste blir det tredje skjermbildet (8.3) og er bygget
før gjennomgangen. Den sier fortsatt på papir hvordan Nyheter og Kalender ville
passet inn.

*Lagt til 2026-10-01:* skriftregelen i `designregler.md` §1 tas inn her, som en egen liten endring med tre tester: ingen mal viser til en skrift på nettet, tallcellene i tabellene har tabelltall, og skriftfilene har OpenType-funksjonen `tnum`.

*Lagt til 2026-10-11, Marians beslutning:* skriftregelen i `designregler.md` §1 flyttes til 8.0d, med de tre testene (kl. 12:13).

**Avhenger av:** 8.1. **Én økt:** ja.

### Story 8.3: Min liste: eget skjermbilde med stjerne og filter

*Lagt til 2026-09-30, Marians beslutning.*

Som **bruker**, vil jeg ha en egen side der jeg merker aksjene jeg følger med en
stjerne og ser bare dem.

**Oppfyller:** «Favorittmerking av aksjer» fra «Hvis vi rekker» i `prd.md` §2, og
knapperaden fra v1.1-raden «Navigasjon mellom flere skjermbilder», for
skjermbildene som finnes · **Begrenses av:** FR-101–103, `AD-3`, `AD-10`,
`AD-16`, `AD-21` med føringen 30.09

**Kontroll — hva testen ser etter:**
- Min liste har samme tabell som oversikten, med en stjerne på hver rad, og en knapp «Alle / Min liste» som viser alle eller bare de merkede, sortert etter FR-102
- Øverst på alle skjermbildene står en knapperad med Markedsoversikt og Min liste, og knappen for siden man står på, er fylt. Aksjedetaljen beholder veien tilbake (FR-101)
- Merkingen er et eget datasett med egen port og webserveren som eneste skriver (`AD-3`), i en egen tabell med ny migrering (`AD-16`). Webserveren skriver bare denne tabellen og henter aldri (`AD-10`)
- Merkingen overlever en omstart, gjelder maskinen (ingen innlogging) og koster ingen API-kall
- En tom liste sier hvordan man merker
- Lista tas som parameter og testes også med færre enn 15 aksjer (føringen 30.09 under `AD-21`)
- **Ville feilet hvis:** merkingen forsvant ved omstart, filteret endret rekkefølgen fra FR-102, eller lista fikk antall aksjer eller kjøpskurs. Da er det en personlig portefølje, som er utenfor v1

**Avhenger av:** 2.2. Bygges etter brukertesten i 8.1 og før UX-gjennomgangen i
8.2, så 8.2 vurderer alle tre skjermbildene.

*Avgjort 2026-10-19 kl. 10:29 (gruppens svar):* 8.3 bygges i dag og flettes etter kveldens henting og måling; stjernen står både i oversikten og i Min liste; demoen starter med fem merket, den ekte med en tom liste.

*Lagt til 2026-10-20 kl. 10:17:* PR #78 er squash-flettet i `e02240a`, etter gruppens svar 19.10 kl. 10:29 om å flette etter hentingen og målingen, låst til head-en `dca69d0`, der main var flettet inn (regel 7). Hele settet på `dca69d0`: 2761 bestått og 17 hoppet over. CI var grønn på head-en (39391917414). Grenen er slettet på GitHub. Basen ble kopiert til `data/db/ose-kopi-2026-10-20-foer-0007.db` før pullen, og migrasjonene på en kopi av kopien ga versjon 7 med like mange rader i kurs, vurdering, indeks og ki_logg (regel 22).

### Story 8.4: Se nærmere i aksjedetaljen

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-02, Marians beslutning.*

Som **bruker**, vil jeg se hva jeg kan sjekke selv når en aksje skiller seg ut, så
jeg forstår dagen uten at appen gir råd.

**Oppfyller:** FR-205 · **Begrenses av:** FR-104, FR-203, FR-408, NFR-06

Delen «Se nærmere» står rett under kursgrafen og har tre deler, som i FR-205:
«Børsen, bransjen eller selskapet?», med aksjens endring mot hovedindeksen og mot
snittet av de andre i samme bransje; «Står det noe i børsmeldingene?», med lenken
til NewsWeb; og «Er en slik dag vanlig for aksjen?», med målingene som er lagret i
vurderingen. Tekstene ligger i hjelpefila fra 8.0b.

**Kontroll — hva testen ser etter:**
- Hvert av de fem svarene i del 1, med grensene fra `Parametre`
- «Selskapet eller bransjen» når aksjen er alene i bransjen
- Del 3 bruker målingene i vurderingen og regner ikke kursene på nytt
- Ingen nye kall og ingen ny tabell
- **Ville feilet hvis:** et svar kunne leses som et råd eller en spådom, eller et tall ble gjettet

**Avhenger av:** 10.5 for lenken, FR-104 og FR-410 for hovedindeksen, og 2.5 for målingene.
**Én økt:** ja.

*Lagt til 2026-10-06, Marians beslutning kl. 20:42:* «Står det noe i børsmeldingene?» nevner NewsWeb uten lenke og viser til lenken til selskapets investorside (10.5). Euronexts vilkår forbyr lenker uten tillatelse (`docs/kilder-og-rettigheter.md`, «Lenker til Euronexts nettsteder (lest 2026-10-06)»).

*Lagt til 2026-10-13, endringsforslaget 13.10 (svar 5), godkjent av Marian kl. 12:46:* «Hva du kan sjekke selv» fra designforslaget hører hit, i delen «Se nærmere». Tekstene kontrolleres mot koden og PRD-en før de brukes, som i 8.0c.

### Story 8.5: Endring i kroner, og høy og lav i aksjedetaljen

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-07, Marians beslutning kl. 23:11.*

Som **bruker**, vil jeg se hvor mange kroner aksjen endret seg, og hvor høyt og
lavt den gikk, så jeg forstår dagen uten å regne selv.

**Oppfyller:** FR-101 og FR-203 (tilleggene 2026-10-07) · **Begrenses av:** FR-102, FR-201, FR-407, `AD-10`, NFR-08

**Kontroll — hva testen ser etter:**
- Markedsoversikten viser kronene på en mindre linje under prosenten, i samme celle. Det er fortsatt fem kolonner (FR-101), og sorteringen er fortsatt på prosent (FR-102)
- Aksjedetaljen viser kronene ved prosenten, og høy og lav for siste børsdag ved sluttkursen. Høy og lav tegnes ikke i grafen (FR-201)
- Kronene regnes av `adjusted_close` for de to siste børsdagene, som prosenten, så de to peker alltid samme vei. En utbyttedag merkes etter FR-407
- Høy og lav vises bare når begge finnes og lav ≤ sluttkurs ≤ høy, ellers «–» (NFR-08)
- Før høy og lav vises, sammenlignes noen dager for hånd med Oslo Børs' egen side, lest av en av oss (`malinger.md` §6, raden «Sluttkurs, høy og lav mot Oslo Børs»). Siden hentes aldri av programmet
- **Ville feilet hvis:** kronene ble regnet av `close` og pekte en annen vei enn prosenten på en utbyttedag, eller høy og lav ble vist når lav ≤ sluttkurs ≤ høy ikke holder

**Avhenger av:** 2.10 for høy og lav. **Én økt:** ja.

### Story 8.6: Børsometeret

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 1).*

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

*Lagt til 2026-10-13, endringsforslaget 13.10 (N3, svar 24), godkjent av Marian kl. 12:46:*
- Børsometeret bruker de 13 bransjene i `designregler.md` §4, med symbolene fra 8.0d. Det brukeren ser, heter «bransje», og koden sier `sektor`
- **Ville feilet hvis:** siden sa «sektor», eller en bransje sto uten symbol

### Story 8.7: Sjekk 2 og 3 i kursgrafen

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 2).*

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

### Story 8.8: Signaldager i kursgrafen

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 3).*

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

### Story 8.9: «Vis meg rundt»

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 4).*

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

*Lagt til 2026-10-13, endringsforslaget 13.10 (punkt 4.1), godkjent av Marian kl. 12:46:*
- «Vis meg rundt» har høyst 7 steg, og stegene om retning, signalstyrke og sjekkene bruker tekstene fra tavla i punkt 4.2

### Story 8.10: Innstillinger øverst

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 5).*

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

*Lagt til 2026-10-13, endringsforslaget 13.10 (punkt 4.1, svar 3), godkjent av Marian kl. 12:46:* 8.10 deles. 8.10 har «Vis hjelp» og avhenger av 8.3 for knapperaden og 8.0b for hjelpen. «Vis KI-tekst» kommer i 8.10b. Kontrollpunktet «Bryteren ved KI-teksten og valget i Innstillinger viser alltid det samme», «Ville feilet hvis» over og 10.3 i «Avhenger av» gjelder 8.10b.

### Story 8.10b: «Vis KI-tekst» i Innstillinger

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-13, endringsforslaget 13.10 (punkt 4.1), godkjent av Marian kl. 12:46.*

Som **bruker**, vil jeg slå KI-teksten av og på i Innstillinger, så valget
gjelder alle sidene og huskes.

**Oppfyller:** FR-110 (KI-delen) · **Begrenses av:** FR-601, `AD-3`, `AD-10`, `AD-16`

**Kontroll — hva testen ser etter:**
- «Vis KI-tekst» står i Innstillinger, i samme tabell som «Vis hjelp» fra 8.10
- Bryteren ved KI-teksten og valget i Innstillinger viser alltid det samme
- Ingen API-kall
- **Ville feilet hvis:** bryteren ved KI-teksten og Innstillinger kunne vise hver
  sin verdi

**Avhenger av:** 8.10 og 10.3. **Én økt:** ja.

### Story 8.11: Ferdige lister og filter på signalet

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 7).*

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

### Story 8.12: Endret signalstyrke siden forrige børsdag

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 8, skrevet om etter Marians beslutning 02.10 kl. 23:30).*

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

*Lagt til 2026-10-08 kl. 21:48:* avhenger også av 8.17, fordi merket ikke kan
prøves skjult før «Sammenlign med» finnes.

### Story 8.13: Lær noe nytt

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 9).*

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

### Story 8.14: Justeringsdager i kursgrafen

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 11).*

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

### Story 8.15: Sortering ved klikk i kolonneraden

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 14).*

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

*Lagt til 2026-10-13, endringsforslaget 13.10 (punkt 4.6, nr. 2), godkjent av Marian kl. 12:46:*
- Når tabellen er delt i «Skilte seg ut» og «Øvrige aksjer» (8.0e), gjelder sorteringen innenfor hver del
- **Ville feilet hvis:** en rad fra «Øvrige aksjer» havnet under «Skilte seg ut» etter et klikk

*Lagt til 2026-10-15:* flettet i `a13d273`, PR #43.

*Avgjort 2026-10-18 kl. 22:06 (gruppens svar):* Selskap kan sorteres A til Å, og kolonnen tabellen er sortert på, får et lysere felt og en oransje strek under, som på designtavla, i en liten PR etter 8.16 i kveld (spesifikasjonen 8.15b). Grunnen: tavla har sorteringsmerket på Selskap, og i appen skiller bare fargen på vinkelen den sorterte kolonnen fra de andre.

*Lagt til 2026-10-19 kl. 00:22:* Selskap kan sorteres, og den sorterte kolonnen har et lysere felt og en oransje strek under, flettet i `b6449ac`, PR #73 (spesifikasjonen `spec-8-15b-selskap-og-den-sorterte-kolonnen.md`).

### Story 8.16: Regelen for startdagen, og periodene i kursgrafen

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 15).*

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

*Avgjort 2026-10-18 kl. 21:46, 21:49 og 21:50 (gruppens svar):* 8.16 bygges i kveld etter PR #70 og 10.2d, og 8.17 flyttes ikke. Grafen får alle åtte knappene i `designregler.md` §2, som PRD-en sier (FR-201). «I går» (siste børsdag) og «Velg dag» viser 6 mnd fram til dagen, med dagen merket, endringen den dagen og signalet som er lagret for den.

*Lagt til 2026-10-18 kl. 23:28:* regelen for startdagen og periodene i kursgrafen er flettet i `be05337`, PR #72 (spesifikasjonen `spec-8-16-periodene-i-kursgrafen.md`). Regelen står i `designregler.md` §2, og `startdag` i `src/perioder.py` er funksjonen 8.17 skal bruke, sammen med delmalen `_perioder.html`.

*Avgjort 2026-10-19 kl. 00:00 (gruppens svar):* når en dag er valgt med «Velg dag», viser hele aksjesiden den dagen: kortene øverst, «Hvorfor signalet ble», KI-teksten og grafen, lest fra det som er lagret for dagen, med et merke øverst og en lenke tilbake til siste børsdag (spesifikasjonen 8.16b). Grunnen: etter 8.16 viste toppen siste børsdag og linja over grafen den valgte dagen, to ulike signaler på samme side. Det utvider svaret 18.10 kl. 21:50.

*Lagt til 2026-10-19 kl. 11:00:* med «Velg dag» viser hele aksjesiden dagen, lest fra det som er lagret, med et merke øverst og en lenke tilbake til siste børsdag, flettet i `4e43ba5`, PR #74 (spesifikasjonen `spec-8-16b-dagen-paa-hele-siden.md`).

### Story 8.17: Periodevalget i oversikten, Min liste og børsometeret

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 15).*

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

*Lagt til 2026-10-08 kl. 21:48, Marians beslutning (FR-105, FR-107):*
- Søylene under hovedindeksen følger periodevalget og «Velg dag», som tabellen,
  og indekslinja følger samme periode. Endringen regnes som i FR-101, av
  kursserien på `adjusted_close`. Bransjesymbolet er gult ved 3 av 3 som før
- «Sammenlign med» er periodevalget i Min liste: hver rad viser tallene for
  siste børsdag øverst og dagen man sammenligner med under
- **Ville feilet hvis:** søylene viste dagens endring mens tabellen viste en uke

**Avhenger av:** 8.16, 8.3 for Min liste og 8.6 for børsometeret. **Én økt:**
avgjøres i planen.

### Story 8.18: Kommende eks.dato i kursgrafen

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-08, Marians beslutning, endringsforslaget 08.10 (`sprint-change-proposal-2026-10-08.md`, rad 12, Marians beslutning kl. 08:06).*

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

### Story 8.19: Neste henting i stripa øverst

*Lagt til 2026-10-19 (gruppens svar 19.10 kl. 15:43, `sprint-change-proposal-2026-10-19.md`):* «Ekstra, hvis tiden rekker». Briefen v8 lover ikke dette, så storyen er ikke v1. Den bygges på egen gren og flettes bare ferdig og grønt (svaret kl. 14:48). Er den ikke flettet ved funksjonsstoppen, README-prøven senest én uke før innleveringen, står den som plan for en senere versjon.

*Lagt til 2026-10-13, endringsforslaget 13.10 (punkt 4.6, nr. 5 A, svar 13), godkjent av Marian kl. 12:46.*

Som **bruker**, vil jeg se når dataene ble hentet og når neste henting tidligst
kan komme, så jeg vet hvor ferske tallene er.

**Oppfyller:** designforslaget, punkt 11 i samlelista · **Begrenses av:** NFR-05,
NFR-08, `AD-10`

**Kontroll — hva testen ser etter:**
- Stripa øverst sier når dataene ble hentet, og når neste henting tidligst kan
  komme: «Neste: <dag> etter kl. 22»
- Klokkeslettet kommer fra `KL_22` i `fetch_prices.py`, og dagen fra
  `boersdag.py`, ikke skrevet fast
  *Lagt til 2026-10-17:* konstanten heter `TIDSGRENSE` og er kl. 21:00 fra 19.10
  (story 2.3, beslutningen 16.10 kl. 21:09), så stripa sier «etter kl. 21»
  *Lagt til 2026-10-20:* fra 20.10 er `TIDSGRENSE` kl. 22:00 igjen (story 2.3, gruppens
  svar 19.10 kl. 22:19), så stripa sier «etter kl. 22»
- Ingen API-kall
- **Ville feilet hvis:** stripa sa i morgen en fredag, eller klokkeslettet sto
  fast i malen

**Avhenger av:** 8.0d for stripa. **Én økt:** avgjøres i planen.

---

## Epic 9: Dokumentasjon av prosessen

### Story 9.0: Fem tester sjekker det de lover

*Lagt til 2026-09-27, fra kontrollen av repoet 26.09 (`docs/kontroll-2026-09-26.md`, «Utsatt», K3 og K4).*

Som **gruppe**, vil vi at hver test sjekker det navnet og docstringen lover, så en grønn testkjøring betyr det vi sier den betyr, og så 9.1 kan vise til tester som faktisk kan feile.

**Oppfyller:** — *(grunnlag for 9.1)* · **Begrenses av:** `AD-8`

**Grunnen:** kontrollen 26.09 fant fem tester som består uten å sjekke det de lover: `test_absolutt_endring_avgjoer_ved_lik_styrke`, `test_noeyaktig_paa_grensen_gir_null` og `test_formatet_kan_leses_av_snapshotkilde` (ført i `deferred-work.md`), og `test_kort_serie_viser_kurs_men_sier_at_signalet_mangler` og `test_ruta_gjoer_ingen_nettverkskall` (K3 og K4 i kontrollrapporten).

**Kontroll — hva testen ser etter:**
- Hver av de fem testene feiler mot en mutant som bryter det den lover, og består mot koden slik den er
- Koden i `src/` endres ikke. Viser en test at koden er feil, stopper vi og avgjør det som egen sak
- **Ville feilet hvis:** en av de fem fortsatt besto med mutanten for sitt løfte

**Forutsetning:** ingen. Storyen rører bare `tests/`.

**Én økt:** ja.

*Ferdig 2026-09-27:* flettet i `c2c26ba`, PR #7.

### Story 9.1: `docs/kvalitetssikring.md`

Som **sensor**, vil jeg finne i ett dokument hva som er testet, hvordan, og hva
som ikke er det, så jeg ikke må sette det sammen fra commit-meldinger.

**Oppfyller:** — *(emnesiden, «hvordan studentene har kvalitetssikret koden»)* ·
**Begrenses av:** `AD-8`

**Kontroll — hva den ferdige storyen inneholder:**
- Hva som testes og hvordan: antall tester (**telt da dokumentet skrives, ikke
  kopiert herfra**), CI, nettverkssperren i `tests/conftest.py`, og
  kontrakttestene som kjøres mot begge lagrene
- Mutantpraksisen: hva den er, og hver gang den er kjørt, med story, commit,
  mutant og hvilke tester som fanget den. Den forkastede transaksjonsmutanten
  fra 1.3 er med
- Hva kontrollensene 22.09 fant, med henvisning til `docs/kontroll-2026-09-22.md`
- **Hva som ikke testes**, som egen seksjon. Et eksempel: den ekte
  `hent_ett_symbol`, som bruker kvote og derfor aldri kjøres i tester
- **Ville feilet hvis:** dokumentet bare listet det som testes. Da ser et hull
  ut som dekning

**Tidspunkt:** skrives når Epic 1 er ferdig, og oppdateres ved hver epic.
**Én økt:** ja.

*Ferdig 2026-10-03:* skrevet i `2208ae1`, uten PR, fordi bare dokumenter endres. Står i review til Marian eller Joakim har lest dokumentet.

*Lagt til 2026-10-17 kl. 22:59:* dokumentet er oppdatert og flettet i `eca81b4`, PR #61 (spesifikasjonen `spec-9-1-kvalitetssikringen-oppdateres.md`). Tallene er talt på nytt, §3 og §5 har en rad for hver spesifikasjon fra 2.2 til 10.3, §6 har Rettet-linjer, og §11–§13 er nye. `tests/test_kvalitetssikring.py` holder radene og testnavnene. CI var grønn på head-en `d1a1d0d` (kjøring 39068835003) og på main (39068954002).

*Lest 2026-10-03:* Marian svarte kl. 01:05 at dokumentet er lest, og 9-1 er done.

### Story 9.2: `docs/ai-prompts/bygging/`

Som **gruppe**, vil vi at instruksjonene som styrte byggingen, ligger ordrett i
repoet, så refleksjonsrapporten kan vise dem i stedet for å gjenfortelle dem.

**Oppfyller:** — *(emnesiden, «hvordan KI ble brukt»)* · **Begrenses av:** regel
10, 11 og 18 i `CLAUDE.md`

*Endret 2026-09-24:* regel 18 i `CLAUDE.md` sier nå at hver innlimte
instruksjon lagres ordrett i `docs/ai-prompts/<ÅÅÅÅ-MM-DD>.md` før den
utføres, med klokkeslett og en linje om utfallet etterpå. Formatet står i
`docs/ai-prompts/README.md`. Fra 24.09 kl. 22:05 skjer det løpende. Det som
gjenstår i denne storyen, er å hente inn instruksjonene fra 21.–24.09 fra
historikken til øktene, i samme format. Punktene under om `bygging/` og
filnavn er erstattet av regel 18. *Avgjort av Marian 2026-09-24:* lesingen
før commit gjelder ikke dagsfilene etter regel 18, fordi Marian leser hver
instruksjon når hun limer den inn. Før hver commit sjekker økta selv at fila
ikke inneholder rådata, nøkler eller personopplysninger om andre enn Marian og
Joakim (regel 16). For instruksjonene fra 21.–24.09 som hentes inn her, gjelder
lesingen før commit som før.

**Kontroll — hva den ferdige storyen inneholder:**
- Katalogen finnes, og `docs/ai-prompts/README.md` peker på den
- Én fil per dag, med filnavn etter konvensjonen som alt står i README
  (`ÅÅÅÅ-MM-DD-navn-tema.md`)
- Blokkene legges inn **ordrett**, med sluttmarkøren, av Marian. Storyen gjelder
  strukturen, ikke innholdet
- **Hver fil leses av Marian eller Joakim før commit, fordi repoet er offentlig.**
  Det gjelder ikke bare nøkler, men også navn og formuleringer som ikke bør stå
  offentlig. Blokkene inneholder analyser av svar fra faglærerstaben. Innholdet
  i svarene står alt i `innlevering.md` og er ikke nytt — lesingen gjelder navn
  og formuleringer
- **Ville feilet hvis:** blokkene ble renskrevet eller oppsummert. Da er arkivet
  et referat, og det er nettopp i omskriving at krav har forsvunnet før (de seks
  detaljene i `reflection-log.md`)

**Én økt:** ja.

### Story 9.3: Arbeidsmønsteret

Som **sensor**, vil jeg forstå hvem som bestemte hva, så jeg kan vurdere hvordan
KI ble brukt og ikke bare at den ble brukt.

**Oppfyller:** — *(emnesiden, «hvordan KI ble brukt»)* · **Begrenses av:** ingen AD-er

**Kontroll — hva den ferdige storyen inneholder:**
- En kort beskrivelse i `docs/ai-prompts/README.md`: en rådgivende KI-økt uten
  tilgang til repoet, en byggeøkt med tilgang, og et menneske som relé mellom dem
  *Rettet 2026-10-03 (kontrollen 26.09, E22):* rådgivningsøkta hadde ikke tilgang
  til repoet de første dagene, men har lest det offentlige repoet gjennom sin egen
  kopi siden 23.09 (`docs/ai-prompts/README.md`, «Arbeidsmønsteret»)
- En tabell over hva som avgjøres av hvem
- Hvorfor mønsteret ble valgt
- **Tilfeller begge veier, med kilde.** Reléet går begge veier, og beskrivelsen
  skal vise det:
  - *Rådgivningsøkta tok feil, og feilen ble fanget:* `legal@oslobors.no` som
    adresse til Euronext (PRD-memloggen, 21.09), og «basen er gjenoppbyggbar»,
    som ble funnet ved å lese FR-408 helt ut (arkitekturmemloggen, 22.09)
  - *Rådgivningsøkta korrigerte byggeøkta:* byggeøkta skrev EODHD-utkastet med
    **fire** spørsmål (`0945818`, 20.09). Rådgivningsøkta avgjorde at det skulle
    sendes **ett** (`reflection-log.md`, 20.–21.09, «Det motsatte gjelder også»).
    Svaret kom på under ett døgn. Dette er en rettet vurdering, ikke en rettet
    faktafeil — et tilfelle der rådgivningsøkta fanget en faktafeil byggeøkta
    hadde skrevet, er ikke funnet med kilde
- **Ville feilet hvis:** beskrivelsen bare sa at mønsteret virker. Da mangler
  gangene det ikke virket, og det er dem refleksjonen trenger

**Én økt:** ja. Kort.

### Story 9.4: Relevanseksperimentet, del 1 — utvalg, innsamling og merking

*Lagt til 2026-09-24.* Ingen story dekket del 1, mens briefen og PRD §7 setter
innsamling og merking til uke 39–40. **Eier: Joakim.**

Som **gruppe**, vil vi ha et testsett på ~50 medieartikler fra åtte selskaper,
merket for hånd, så del 2 har noe å kjøre KI-klassifiseringen mot.

**Oppfyller:** suksessmålet «Relevanseksperiment», del 1 (PRD §7, punkt 5,
lukket 26.09) · **Begrenses av:** regel 6 og 16 i `CLAUDE.md` *(rettet
2026-09-26: her sto «åpent punkt 5»)*

**Kontroll — hva den ferdige storyen inneholder:**
- Utvalgskriteriene skriftlig **før** innsamlingen: hvilke åtte selskaper, hvor
  mange artikler per selskap, og hva som teller som at en artikkel handler om
  selskapet
- Kalltallet kontrolleres med den **første** forespørselen: to tickere, med
  `/api/user` lest før og etter. Differansen avgjør om ~40 eller ~80 kall er
  riktig (`malinger.md` §7.2). Ingen kall uten avtale (regel 6)
- Artiklene ligger bare lokalt, i `data/`. Ingen titler eller utdrag i sporede
  filer (regel 16)
- Merkingen gjøres for hånd, én vurdering per artikkel, før noen modell ser
  artiklene
- **Ville feilet hvis:** kriteriene ble skrevet etter at artiklene var sett. Da
  er utvalget tilpasset det som ble funnet

**Én økt:** nei. Merkingen tar tid.

*Endret 2026-09-25:* kontrollen med to tickere i den første forespørselen er
byttet ut. Den måler hva en forespørsel med flere tickere koster, og det
trenger vi ikke når hvert selskap hentes for seg. Prisen for én ticker er målt:
5 kall (`malinger.md` §7.2). I stedet leses `/api/user` før og etter hver
forespørsel, og koster en forespørsel noe annet enn 5 kall, stopper vi før
neste. Budsjettet er åtte forespørsler, ~40 kall. Se
`prds/prd-G74-lund-osen-2026-09-20/relevanseksperiment.md` §2.

### Story 9.5: Relevanseksperimentet, del 2 — KI-kjøringen

*Utgår fra 2026-10-06 (Marians beslutning kl. 21:11, `prd.md` §7).* Del 2 kjøres ikke, fordi nyhetene kan brukes privat, men ikke i en app som kan bli tilgjengelig for andre, og henvendelsene om dem er ikke besvart. Del 1 står og brukes i refleksjonsrapporten. Storyen står som den var.

*Lagt til 2026-09-27, fra prioriteringen samme dag.*

Som **gruppe**, vil vi kjøre KI-klassifiseringen på de merkede artiklene, så refleksjonsrapporten kan vurdere KI med tall.

**Oppfyller:** suksessmålet «Relevanseksperiment», del 2 · **Begrenses av:** regel 6 og 16 i `CLAUDE.md`, betingelse 4

**Kontroll — hva den ferdige storyen inneholder:**
- Tjenesten er valgt i 4.1, og betingelse 4 er dokumentert før noe sendes
- KI-en får samme kriterier og tekst som merkingen (§4 og §7 i `prds/prd-G74-lund-osen-2026-09-20/relevanseksperiment.md`), og resultatet regnes som §5 sier, uansett utfall
- Artiklene og svarene ligger bare i `data/`. Bare tallene føres i sporede filer
- **Ville feilet hvis:** kriteriene eller prompten ble justert etter at svarene var sett

**Avhenger av:** 4.1. **Én økt:** nei.

### Story 9.6: Product brief v8 etter plan B

*Lagt til 2026-10-06, fra tilbakemeldingen på briefen ([`tilbakemelding-product-brief.md`](tilbakemelding-product-brief.md), `d363002`).*

Som **gruppe**, vil vi ha en brief som beskriver appen vi leverer, så sensor kan følge veien fra brief til kode uten å møte børsmeldinger som ikke er i v1.

**Oppfyller:** punkt 1 og 2 under «Neste steg for gruppen» i tilbakemeldingen · **Begrenses av:** regel 17 i `CLAUDE.md`, FR-608

**Kontroll — hva den ferdige storyen inneholder:**
- v8 erstatter v7 i `product-brief.md` og får taggen `arbeidskrav-product-brief-v8`. v7 står urørt i sin tag. Øverst står kort hva som er endret mot v7. v8 er ikke lengre enn v7, telt som i regel 17
- Scope: børsmeldinger og kommende hendelser står under «Utenfor v1», med svaret fra Euronext som grunn. «Inne i v1» skiller kjernen som skal bli ferdig uansett (oversikten og aksjedetaljen med regelbasert signal, i demoen) fra trinnene etter, i rekkefølge
- Solution: det v7 hadde som reserveplan under «Data og kilder», er nå planen. KI-laget forklarer signalet ut fra fortegn, styrke, retning og antall (avgjort 04.10), og briefen sier hvilken modell som er standard og hva den koster (FR-608). Demoen med oppdiktede selskaper er versjonen sensor bruker, og alt i v1 kan vises der, også med KI av
- «KI-bidrag i drift» er skrevet om til et sjekkbart kriterium for KI-laget etter plan B
- Minst ett kriterium for at beregningene er riktige: kjente kursserier gir forhåndsberegnet styrke og retning, sporbart til testene med håndlagde serier i `tests/test_signalberegning.py`. De bruker korte vinduer, og de ekte parameterne dekkes av kontrollregningen for hånd i `malinger.md` §6. Den gjenstår, og briefen sier ikke at den er gjort
- **Ville feilet hvis:** v8 lovet noe som ikke er i v1, eller taggen for v7 ble flyttet

**Avhenger av:** ingen. Gjøres før 3.1, så demoen og briefen beskriver samme app. **Én økt:** ja.

*Lagt til 2026-10-06:* kontrollregningen i `malinger.md` §6 er gjort for EQNR 05.10 og stemmer (`55a1165`), så v8 kan vise til den.

*Lagt til 2026-10-06, Marians beslutning:* v8 lover ikke lenker til NewsWeb eller Oslo Børs, men kan nevne lenken til investorsiden (10.5).

*Lagt til 2026-10-06:* v8 er lagt inn i `product-brief.md` i `52023c9`, med taggen `arbeidskrav-product-brief-v8`, etter at Marian og Joakim leste utkastet og sa ja.

### Story 9.7: Linter og formatterer i CI

*Lagt til 2026-10-17, gruppens svar kl. 22:38, 22:41 og 22:42 (instruksjonen kl. 23:13).*

Som **gruppe**, vil vi at ruff finner ubrukte importer, rot i importene og vanlige feil før en commit, og at CI stopper det som slipper gjennom, så sensor ser kode som er formattert på én måte og sjekket av et verktøy.

**Oppfyller:** svaret kl. 22:38–22:42 under «Prioritering» · **Begrenses av:** regel 8 og 19 i `CLAUDE.md`, AD-8

**Kontroll — hva den ferdige storyen inneholder:**
- ruff er en utviklingsavhengighet i `uv.lock`, og reglene står i `pyproject.toml`. Bare regler som finner feil eller rot: pyflakes (`F`), importene (`I`) og bugbear (`B`), ikke smak
- Først én commit med `ruff format` på `src/` og `tests/`, uten endring i oppførsel, så én commit per regelgruppe
- CI kjører `ruff check` og `ruff format --check`, og en test gjør det samme, så `uv run pytest` feiler lokalt også
- README («Tester»), `docs/kvalitetssikring.md` og `CLAUDE.md` sier at ruff kjøres før en commit
- `src/meldinger.py` sier i docstringen at den ikke brukes i v1 (plan B), og at den er beholdt med testene
- **Ville feilet hvis:** en ubrukt import eller en linje som ikke er formattert, slapp gjennom testene

**Avhenger av:** ingen. **Én økt:** ja.

*Lagt til 2026-10-17 kl. 23:41:* ruff er i CI og i pytest, flettet i `faaa36c`, PR #62 (spesifikasjonen `spec-9-7-linter-og-formatterer-i-ci.md`). Reglene er pyflakes, importene og bugbear, med B905 slått av. CI var grønn på head-en `4cf27a9` (kjøring 39071749356) og på main (39071843876).

### Story 9.8: Kopien `.agents/skills/` tas bort

*Lagt til 2026-10-18, gruppens svar kl. 00:03 (instruksjonen kl. 11:40).*

Som **gruppe**, vil vi at BMAD-skillene ligger én gang i repoet, så sensor ikke finner 242 filer som er kopier, og så rotmappa bare har det vi bruker.

**Grunnen:** BMAD ble satt opp for Claude Code og Codex 15.09 (`59a90a2`). Installasjonen la de samme skillene i `.claude/skills/` for Claude Code og i `.agents/skills/` for Codex, 242 filer hver, med likt innhold. Gruppen bruker bare Claude Code.

**Oppfyller:** svaret kl. 00:03 under «Prioritering», raden «Ryddighet i repoet» i `docs/vurderingsmatrise.md` · **Begrenses av:** regel 8, 10 og 19 i `CLAUDE.md`, AD-8

**Kontroll — hva den ferdige storyen inneholder:**
- a) De 242 filene under `.agents/` er tatt ut av git, og `git diff` mot main er tom under `.claude/skills/`. Blir det igjen en lokal `.agents/` med bare `__pycache__`, slettes den; ellers står den, og det sies fra
- b) `_bmad/_config/manifest.yaml` har bare `claude-code` under `ides`, så en ny BMAD-installasjon ikke legger kopien inn igjen
- c) «Mappestruktur» i README-en nevner bare `_bmad/` og `.claude/skills/` (regel 19), og `.agents/` er tatt ut av unntaket i lekkasjesjekken i `.github/scripts/morgensjekk.py`
- d) En test i `tests/test_ryddighet.py`: ingen fil under `.agents/` er sporet i git (uten git hoppes den over), og manifestet har bare `claude-code`
- e) `.gitignore`: delen for Next.js fra malen er tatt bort (`.next/`, `out/`, `.vercel/`, `.turbo/`, `*.tsbuildinfo`, `next-env.d.ts` og loggene for npm, yarn og pnpm, som `*.log` dekker). `node_modules/`, `dist/` og `build/` står. Kommentarene er på norsk, og `test_ryddighet.py` består
- f) `.env.example` sier at det er tre variabler å sette i `.env`, ikke én, og at en full henting bruker 16 av de 20 kallene
- **Ville feilet hvis:** en fil under `.agents/` ble lagt inn i git igjen, eller `codex` kom tilbake under `ides` i manifestet

**Avhenger av:** ingen. **Én økt:** ja.

*Lagt til 2026-10-18 kl. 12:09:* kopien `.agents/skills/` er tatt bort, flettet i `b5395e9`, PR #65 (spesifikasjonen `spec-9-8-agents-kopien-bort.md`). Manifestet har bare `claude-code`, og `tests/test_ryddighet.py` har åtte nye tester, også for README-en, morgensjekken, `.gitignore` og `.env.example`. CI var grønn på head-en `76eae1c` (kjøring 39117952490) og på main (39118029686).
