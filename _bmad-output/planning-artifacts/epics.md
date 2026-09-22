---
stepsCompleted: [1, 2]
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

1. **Hver story leveres med test som kan kjøres uten API-kall.** Åpent punkt 14,
   og allerede bindende som `AD-8`. `tests/conftest.py` sperrer `socket.connect`,
   så en story som trenger nett for å testes, er ikke ferdig.
2. **Meldingsdelen (FR-5xx) skal kunne falle bort uten at resten ryker.** Den
   hviler på en ubesvart Euronext-forespørsel; 28.09 er vår egen frist for å ta
   stilling uten svar. Ingen annen epic skal forutsette at den finnes.
3. **KI-laget (FR-6xx) legges tidlig, ikke sist.** Eksamen ber om KI-bidrag i
   drift, og det krever at laget har vært i bruk over tid. De tre blokkeringene
   beskriver hva «tidlig» må bestå av, ikke at det ikke kan være tidlig:
   **første KI-epic er *velg modelltjeneste og dokumentér betingelse 4*.**
   Det er papirarbeid, kan gjøres nå, og låser opp resten.
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
- **FR-407** — Merking av utbyttedager *(ID beholdt fra da kravet lå i datahentingen)*

**4.2 Aksjedetaljen**

- **FR-201** — Kursgraf med seks måneders historikk
- **FR-202** — MA50-linjen tegnes oppå kursen
- **FR-203** — Øvrig innhold
- **FR-204** — Aksjedetaljen for en aksje uten gyldig signal

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

**4.5 Meldingsfilter og deduplisering**

- **FR-501** — Deduplisering av språkdubletter
- **FR-502** — Kategorifilter i tre bøtter
- **FR-503** — Eks.dato som datakilde for utbyttemerking

**4.6 KI-laget og grensen mot regelbasert kode**

- **FR-601** — Av/på-bryteren er brukersynlig
- **FR-602** — Visningen når KI-laget er av
- **FR-603** — Usikkerhet vises som forbehold, ikke som rekkefølge
- **FR-604** — Logging av KI-bidraget, fra første kjøring
- **FR-605** — Promptversjon og modell lagres med hver vurdering
- **FR-606** — Relevansskalaen

**4.7 Signalstyrke og retning**

- **FR-701** — Tre navngitte sjekker
- **FR-702** — Nøytralsone i trendsjekken
- **FR-703** — Signalstyrke
- **FR-704** — Retning
- **FR-705** — Terskel for at en aksje skiller seg ut
- **FR-706** — Synlig begrunnelse i aksjedetaljen

**33 FR-er i alt.**

### NonFunctional Requirements

- **NFR-01** — Daglig drift skal holde seg innenfor API-kvoten
- **NFR-02** — Brukeren venter aldri på en henting
- **NFR-03** — Manglende data stopper ikke hovedflyten
- **NFR-04** — KI-laget skal ikke kunne ta ned hovedflyten
- **NFR-05** — Norsk i grensesnitt og forklaringer
- **NFR-06** — Løsningen gir ikke investeringsråd
- **NFR-07** — Rådata bevares fra første kjøring

### Additional Requirements

Fra `ARCHITECTURE-SPINE.md`. Disse er bindende på samme måte som FR-ene, og
flere av dem er **allerede oppfylt i kode** — de er merket med opphav.

**Lagring og datamodell**

- `AD-3` — Én port per eid datasett, én skriver per datasett. Portene er
  `Kurslager`, `Meldingskilde`, `Vurderingslager`, `KILogg`
- `AD-4` — SQLite fra standardbiblioteket. Ingen hostet database. *Bekreftet av
  faglærerstaben 22.09*
- `AD-5` — `erstatt_serie(symbol, rader)` gjør DELETE+INSERT i én transaksjon.
  Ingen `legg_til_rad`
- `AD-6` — Rådata er uforanderlige filer, aldri rader. `<prefiks>-raa-<dato>.json`
- `AD-7` — `Vurderingslager` og `KILogg` har ingen slette- eller endremetode.
  `skriv` avviser enhver dato som ikke er inneværende børsdag
- `AD-18` — `vurdering` lagrer kursen som **verdi**, ikke som fremmednøkkel
- `AD-19` — Porten returnerer `list[Kursrad]` med norske felt. **Innføres i
  SAMME endring som SQLite-adapteren**, ikke som egen runde
- `AD-16` — Skjemaendringer skjer med nummererte migrasjoner. Migrasjonsløperen
  må styre transaksjonen selv; `executescript()` gjør implisitt COMMIT

**Arkitekturgrenser**

- `AD-1` — Kjernen gjør ingen I/O *(oppfylt: commit `01af1a5`, `706720f` m.fl.)*
- `AD-2` — Nettkall bare i skallet, én hentefunksjon per kilde, injisert
- **Gjenstående brudd:** `kursdata.py` gjør I/O i dag — `SnapshotKilde.fra_fil`
  leser fil, `nyeste_snapshot` globber katalog, og `app.py` kaller den direkte
  utenom enhver port. Utskillingen er arbeid som må gjøres

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
  tester grønne)*
- `AD-13` — Signalparametre er konstanter med måling bak seg
- `AD-14` — Deduplisering før kategorifilter *(oppfylt: commit `9acb55c`)*
- `AD-15` — En aksje som mangler data stopper ikke hovedflyten

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

### FR Coverage Map

**Levert før nedbrytingen — 12 FR-er.** Bygget som ren logikk med tester. De
*berøres* av Epic 1 gjennom `Kursrad`, men leverer ingen ny brukerverdi der.

| FR | Levert i |
|---|---|
| FR-101, FR-102, FR-103 | `markedsoversikt.py`, commit `706720f` |
| FR-201, FR-202, FR-204 | `aksjedetalj.py` `076bb12`, `graf.py` `b6ba9d8` |
| FR-701 – FR-706 | `signalberegning.py`, commit `01af1a5` |

**Fordelt på epics — 21 FR-er.**

| FR | Epic |
|---|---|
| FR-203 | **Epic 5, 6 og 7 — delt.** «Øvrig innhold» er meldinger *pluss* KI-forklaring *pluss* hendelser. `aksjedetalj.py` sier selv at alle tre mangler med vilje. Å mappe den til én epic ville vært feil |
| FR-301, FR-302, FR-303 | Epic 7 🔒 |
| FR-401, FR-402, FR-403 | Epic 2 |
| FR-404, FR-405 | Epic 6 🔒 |
| FR-406, FR-408 | Epic 1 |
| FR-407 | Epic 2 |
| FR-501, FR-502, FR-503 | Epic 6 🔒 |
| FR-601, FR-602, FR-603, FR-606 | Epic 5 🔒 |
| FR-604, FR-605 | Epic 4 |

**12 + 21 = 33.** Alle FR-er er plassert.

### NFR Coverage Map

| NFR | Dekning |
|---|---|
| **NFR-01** Kvote | **Eid av Epic 2.** Tverrgående støtte: `AD-8` gjør at ingen test kan bruke kvote |
| **NFR-02** Venter aldri | **Eid av Epic 2** (`AD-10`). Brødteksten rettet 22.09 fordi den lovet en mekanisme som ikke finnes |
| **NFR-03** Manglende data | **Tverrgående.** Delvis levert: `hent_universet` fortsetter ved feil (`352e3a2`), `app.py` tåler `kilde=None`, FR-204 finnes. **Kontroll på hver story:** en test for den tomme eller manglende stien |
| **NFR-04** KI tar ikke ned hovedflyten | **Eid av Epic 5.** Bortfaller hvis Epic 5 strykes |
| **NFR-05** Norsk | **Tverrgående, levert i alt som finnes.** **Kontroll på hver visningsstory:** all brukervendt tekst er norsk |
| **NFR-06** Ikke investeringsråd | **Tverrgående.** Søk i `src/templates/` og `src/*.py` ga null treff på forbeholdstekst — men kravet ber ikke om en tekst. Det sier at *ingen del* skal formuleres som anbefaling, altså et forbud oppfylt ved fravær. **Kontroll på hver visningsstory:** ordlyden leses mot NFR-06 |
| **NFR-07** Rådata bevares | **Eid av Epic 1** (`AD-6`). Delvis levert: `fetch_prices` skriver tidsstemplede øyeblikksbilder (`352e3a2`) |

**Alle sju NFR-er er plassert:** tre eid av en epic, fire tverrgående med
navngitt kontroll.

## Epic List

**Rekkefølge.** Pilene er harde avhengigheter, ikke anbefalinger.

```
Epic 1 (lagring) ──> Epic 2 (henting) ──> Epic 3 (leveranse)
                 └─> Epic 4.3 (SQLite-adapter for KILogg)

Epic 4.1 (papirarbeid)  ─┐  ingen avhengighet —
Epic 4.2 (port + minne) ─┘  parallelt med Epic 1 fra dag én

Epic 6 (meldinger) 🔒 ──> Epic 5 (KI i drift) 🔒 <── Epic 4.1
Epic 7 (hendelser) 🔒
```

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
- **Epic 5 etter både Epic 4.1 og Epic 6.** Se avhengighetsvarselet under.

### Epic 1: Dataene overlever en omstart, og historikken kan leses tilbake

Brukeren kan slå av maskinen og finne oversikten igjen — og spørsmålet «hva sa
løsningen om EQNR for to uker siden?» får et svar.

**FR-er:** FR-406, FR-408 · **NFR-07** · **AD-er:** 3, 4, 5, 6, 7, 16, 18, 19

`AD-19` binder rekkefølgen inne i epicen: `Kursrad` innføres i **samme endring**
som SQLite-adapteren. Konsumentene — `markedsoversikt`, `aksjedetalj`, `graf`,
`signalberegning` — oppdateres her, med full testkjøring mellom hvert steg. Det
er også her `kursdata.py` sitt I/O-brudd lukkes og `app.py` slutter å lese
snapshot utenom porten.

### Epic 2: Ferske data uten at kvoten sprenges

Brukeren kan hente nye kurser bevisst, og kan ikke ved uhell brenne dagskvoten.

**FR-er:** FR-401, FR-402, FR-403, FR-407 · **NFR-01, NFR-02** · **AD-er:** 2, 10, 17, 20

De to kjente `AD-20`-feilene rettes her: `fetch_prices.main` som blander lokal
dato og UTC, og `meldinger._minutt` som kutter på tegn 16. FR-407 ligger her
fordi deteksjonen — avviket mellom `close`- og `adjusted_close`-endringen —
skjer på serien under henting, og den veien gjør kravet uavhengig av NewsWeb.

### Epic 3: Løsningen kan kjøres av andre enn oss

Sensor kan bygge og kjøre den, uten vår nøkkel og uten våre data.

**FR-er:** ingen · **AD-er:** 9, 11, 12 · Dekker åpent punkt 18

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

**FR-er:** FR-601, FR-602, FR-603, FR-606, del av FR-203 · **NFR-04**

| Felt | |
|---|---|
| **Blokkert av** | Åpent punkt 5b (betingelse 4) **og åpent punkt 1 (Euronext)** |
| **Eier** | Gruppen |
| **Avgjøres** | Punkt 5b av Epic 4.1, som er ublokkert. Punkt 1 av Euronext — 28.09 er vår egen frist |
| **Ved nei fra Euronext** | **Epicen strykes i sin helhet.** Alle seks FR-6xx er om meldinger — FR-602 «meldingene i samlekategorien», FR-604 «for hver melding», FR-606 «melding i samlekategorien». Uten Epic 6 finnes ikke datagrunnlaget. **Da bortfaller også NFR-04**, og suksessmålet «KI-bidrag i drift» kan ikke nås, fordi PRD-en måler det i hvilke *meldinger* laget forklarte. Det som overlever er relevanseksperimentet, som henter fra EODHDs nyhets-API og ikke fra NewsWeb — KI kan da demonstreres, men ikke vises i drift |

### Epic 6: Børsmeldinger i oversikten 🔒

**FR-er:** FR-404, FR-405, FR-501, FR-502, FR-503, del av FR-203

| Felt | |
|---|---|
| **Blokkert av** | Åpent punkt 1 — Euronext forbyr automatisert henting uten tillatelse på forhånd |
| **Eier** | Gruppen |
| **Avgjøres** | Forespørsel sendt 21.09, ubesvart. **28.09** er vår egen frist for å ta stilling uten svar |
| **Ved nei** | Strykes i sin helhet — **og tar Epic 5 med seg ned.** Det er ikke en fri strykning: den koster hele KI-laget, NFR-04, to av tre deler av FR-203, og suksessmålet «KI-bidrag i drift». Logikken i `meldinger.py` er bygget og testet fra før, og blir liggende som kode uten datakilde |

### Epic 7: Kommende finansielle hendelser 🔒

**FR-er:** FR-301, FR-302, FR-303, del av FR-203

| Felt | |
|---|---|
| **Blokkert av** | Åpent punkt 1 og 16 |
| **Eier** | Gruppen |
| **Avgjøres** | Samme frist som Epic 6 |
| **Ved nei** | Strykes. Tar ingenting med seg ned — ingen annen epic leser kalenderen. Krever dessuten en manuelt vedlikeholdt oppslagstabell, siden kalenderen verken oppgir ticker eller ISIN |
