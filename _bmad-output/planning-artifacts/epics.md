---
stepsCompleted: [1, 2, 3]
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
- **FR-409** — Dager uten vurdering vises som det de er *(ny 22.09)*

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

**34 FR-er i alt.** FR-409 kom til 22.09, da konsekvensen av `AD-7` ble
avgjort eksplisitt i stedet for å bli stående som en stille mangel.

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
- `AD-13` — Signalparametre er konstanter med måling bak seg *(oppfylt:
  `signalberegning.py:23–31`. Terskel, volumfaktor og nøytralsone i commit
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
| FR-101, FR-102 | `markedsoversikt.py`, commit `706720f` |
| FR-103 | `markedsoversikt.py` + `index.html`. **`706720f` inneholdt bruddet** — den hadde `Retningsvisning("Opp", "↑", "opp")`, mens kravet krever modellens egen streng. Oppfylt av den senere commiten som fjernet oversettelsen |
| FR-201 | `aksjedetalj.py` `076bb12`, `graf.py` `b6ba9d8` |
| FR-202, FR-204 | Samme, **pluss `app.py` og `src/templates/`** — tegnforklaring, 200-svar og «kunne ikke regnes»-beskjed ligger der |
| FR-701 – FR-705 | `signalberegning.py`, commit `01af1a5` |
| FR-706 | `aksjedetalj.py` (`076bb12`) + `aksje.html`. **Ikke `signalberegning.py`** — kravet gjelder aksjedetaljen |

**Merk at tabellen er skrevet fra kjernemodulene.** `app.py` og
`src/templates/` bærer halvparten av fem av disse kravene, og sto ikke nevnt før
kontrollen 22.09 fant det.

**Fordelt på epics — 21 FR-er.**

| FR | Epic |
|---|---|
| FR-203 | **Epic 5, 6 og 7 — delt.** «Øvrig innhold» er meldinger *pluss* KI-forklaring *pluss* hendelser. `aksjedetalj.py` sier selv at alle tre mangler med vilje. Å mappe den til én epic ville vært feil |
| FR-301, FR-302, FR-303 | Epic 7 🔒 |
| FR-401, FR-402, FR-403 | Epic 2 |
| FR-404, FR-405 | Epic 6 🔒 |
| FR-406, FR-408, FR-409 | Epic 1 |
| FR-407 | Epic 2 |
| FR-501, FR-502, FR-503 | Epic 6 🔒 |
| FR-601, FR-602, FR-603, FR-606 | Epic 5 🔒 |
| FR-604, FR-605 | Epic 4 |

**12 + 22 = 34.** Alle FR-er er plassert.

### NFR Coverage Map

| NFR | Dekning |
|---|---|
| **NFR-01** Kvote | **Eid av Epic 2.** Tverrgående støtte: `AD-8` gjør at ingen test kan bruke kvote |
| **NFR-02** Venter aldri | **Eid av Epic 2** (`AD-10`). Brødteksten rettet 22.09 fordi den lovet en mekanisme som ikke finnes |
| **NFR-03** Manglende data | **Tverrgående.** Delvis levert: `hent_universet` fortsetter ved feil (`352e3a2`), `app.py` tåler `kilde=None`, FR-204 finnes. **Kontroll på hver story:** en test for den tomme eller manglende stien |
| **NFR-04** KI tar ikke ned hovedflyten | **Eid av Epic 5.** Bortfaller hvis Epic 5 strykes |
| **NFR-05** Norsk | **Tverrgående, levert i alt som finnes.** **Kontroll på hver visningsstory:** all brukervendt tekst er norsk |
| **NFR-06** Ikke investeringsråd | **Tverrgående.** Forbeholdstekst finnes: `src/templates/index.html:108` sier «Signalstyrken er 0–3 og sier hvor kraftig de tre sjekkene slår ut — *ikke om aksjen bør kjøpes eller selges*». Kravet er likevel et **forbud**, ikke et tekstkrav: ingen del av grensesnittet skal formuleres som anbefaling. **Kontroll på hver visningsstory:** ordlyden leses mot NFR-06 |
| **NFR-07** Rådata bevares | **Eid av Epic 1** (`AD-6`). Delvis levert: `fetch_prices` skriver tidsstemplede øyeblikksbilder (`352e3a2`) |

**Alle sju NFR-er er plassert:** fire eid av en epic (NFR-01, 02, 04, 07), tre
tverrgående med navngitt kontroll (NFR-03, 05, 06).

## Epic List

**Rekkefølge.** Pilene er harde avhengigheter, ikke anbefalinger.

```
Epic 1 (lagring) ──> Epic 2 (henting) ──> Epic 3 (leveranse)
                 └─> Epic 4.3 (SQLite-adapter for KILogg)

Epic 4.1 (papirarbeid)  ─┐  ingen avhengighet —
Epic 4.2 (port + minne) ─┘  parallelt med Epic 1 fra dag én

Epic 6 (meldinger) 🔒 ──> Epic 5 (KI i drift) 🔒 <── Epic 4.1
Epic 7 (hendelser) 🔒

Epic 2 ──> Epic 8.1 (brukertest) ──> Epic 8.2 (UX-gjennomgang)
```

**Prioritering, besluttet 2026-09-23:** Epic 1, 2 og 3 først, fordi det er at
noen utenfor gruppen kan kjøre `docker run`, hente kurser og se begge
skjermbildene med ekte data. Brukertesten (8.1) kommer rett etter Epic 2, ikke
før innlevering. UX-gjennomgangen (8.2) kommer sent. Ingen utvidelse av
omfanget, og forbedringer ut over v1 tas først når dette er kontrollert og
virker. Begrunnelsen står i PRD-memloggen og i refleksjonsloggen 23.09.

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
- **Epic 8.1 rett etter Epic 2, ikke etter Epic 3.** Brukertesten trenger ekte
  data og begge skjermbildene, ikke Docker. Den kan kjøres på vår egen maskin.
- **Epic 8.2 etter 8.1.** Funnene fra brukertesten er det viktigste
  grunnlaget for gjennomgangen.

### Epic 1: Dataene overlever en omstart, og historikken kan leses tilbake

Brukeren kan slå av maskinen og finne oversikten igjen — og spørsmålet «hva sa
løsningen om EQNR for to uker siden?» får et svar.

**FR-er:** FR-406, FR-408, FR-409 · **NFR-07** · **AD-er:** 3, 4, 5, 6, 7, 16, 17, 18, 19

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
| **Blokkert av** | Åpent punkt 1 (Euronext), 3 (kilde for handelskalenderen) og 12 (horisont og hendelsestyper) |
| **Eier** | Gruppen |
| **Avgjøres** | Samme frist som Epic 6 |
| **Ved nei** | Strykes. Tar ingenting med seg ned — ingen annen epic leser kalenderen. Krever dessuten en manuelt vedlikeholdt oppslagstabell, siden kalenderen verken oppgir ticker eller ISIN |

### Epic 8: Tydelig for den som ikke har bygget den

En person utenfor gruppen forstår begge skjermbildene uten hjelp, og designet er
vurdert, ikke bare arvet fra kravene.

**FR-er:** ingen nye. Prøver FR-101–103, FR-201–204 og FR-706 fra utsiden ·
**NFR-05, NFR-06** · Oppfyller suksessmålet «Brukerutfall» (PRD §7)

Egen epic og ikke en del av Epic 3: Epic 3 har ett utfall — at løsningen kan
bygges og kjøres av andre — og brukertesten skal ikke vente på Dockerfilen.

---

# Stories

32 stories. Hver bærer hvilket krav den oppfyller, hvilke `AD`-er som begrenser
den, hva kontrollen faktisk ser etter, og om den kan gjøres ferdig i én økt.

**«Ville feilet hvis» er kontrollen.** Resten er beskrivelse. En story uten den
linjen er ikke ferdig spesifisert.

---

## Epic 1: Dataene overlever en omstart

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
- **`Kurskilde` blir stående ved siden av `Kurslager` til 1.4** (valg b). Det er et brudd på AD-3 så lenge det varer. En test hindrer at nye moduler tar `Kurskilde` i bruk.

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

### Story 1.4: Konsumentene leser `Kursrad`

Som **utvikler**, vil jeg at kjernen slutter å røre `dict`-nøkler, så `AD-19`
gjelder hele veien og ikke bare ved porten.

**Oppfyller:** — *(fullfører FR-406)* · **Begrenses av:** `AD-19`, `AD-1`

**Kontroll — hva testen ser etter:**
- `signalberegning`, `markedsoversikt`, `aksjedetalj` og `graf` tar `Kursrad`
- **Alle 166 testene er grønne etter endringen** — tallet kontrolleres, ikke antas
- Ingen av de fire importerer `sqlite3` eller `pathlib`
- **Ville feilet hvis:** en konsument beholdt oppslaget som faller tilbake fra justert til ujustert kurs. Den linjen bryter FR-701 stille, uten at noen test feiler

**Én økt: nei, dette er den største.** Fem moduler og deler av testsettet.

**Hva som gikk tapt ved delingen:** `AD-19` ville at `Kursrad` innføres i samme
endring som adapteren, slik at konsumentene røres **én** gang. Med 1.2–1.4 som
tre steg røres de fortsatt bare i 1.4, så intensjonen overlever. Men mellom 1.2
og 1.4 finnes en tilstand der porten lover `Kursrad` mens `SnapshotKilde`
fortsatt gir `dict`. Den tilstanden er grunnen til at 1.2–1.4 ikke bør ligge i
hver sin uke.

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

### Story 1.6: `Vurderingslager` med datoavvisning

Som **utvikler på laget**, vil jeg ha et `Vurderingslager` som **nekter** å
skrive en eldre dato, så historikken ikke kan skrives om i ettertid uten at noen
har bestemt det.

**Oppfyller:** FR-408 · **Begrenses av:** `AD-3`, `AD-7`, `AD-18`, `AD-20`

**Kontroll — hva testen ser etter:**
- `skriv` med gårsdagens dato **reiser** — den logger ikke og hopper ikke stille over
- `skriv` to ganger med samme `(symbol, dato)` gir **én** rad, og den siste vinner
- Porten har **ingen** `slett` og **ingen** `endre` — kontrollert på protokollen, ikke på implementasjonen
- En `vurdering` overlever `erstatt_serie` på samme symbol: kursverdiene i raden er uendret etterpå
- **Ville feilet hvis:** noen la til en `oppdater`-metode «for migrasjoner», eller hvis datogrensen ble regnet i UTC — da ville en kjøring 23:30 norsk tid skrevet på gårsdagen

**Én økt:** ja.

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
- **Ville feilet hvis:** lageret svarte `None` både for «ikke kjørt» og «ikke børsdag». Da er de to umulige å skille, og skillet kan ikke gjenskapes i ettertid

**Én økt:** ja.

---

## Epic 2: Ferske data uten at kvoten sprenges

### Story 2.1: Børsdag i Oslo, tidsstempel i UTC

Som **utvikler**, vil jeg at «dagen» betyr én ting, så to verdier ikke kan være
enige og begge være feil.

**Oppfyller:** — *(grunnlag for FR-402, FR-408)* · **Begrenses av:** `AD-20`

**Kontroll — hva testen ser etter:**
- Filnavn og `hentet` i samme øyeblikksbilde utledes av **samme** øyeblikk
- En kjøring 00:30 norsk tid gir filnavn og tidsstempel som peker på samme dag
- `meldinger._minutt` går via et tidsobjekt, ikke en tegnavkorting
- To representasjoner av samme øyeblikk gir **samme** dublettnøkkel
- **Ville feilet hvis:** rettingen bare gjorde filnavn og tidsstempel konsistente uten å si hvilken sone de er i. To verdier kan være enige og begge være feil

**Én økt:** ja. Retter de to kjente feilene fra `AD-20`.

### Story 2.2: Hentekommandoen som egen inngang

Som **sensor som kjører containeren**, vil jeg at oppstart ikke bruker et eneste
API-kall, så jeg ikke brenner gruppens dagskvote ved å se på løsningen.

**Oppfyller:** FR-401 · **Begrenses av:** `AD-10`, `AD-2`, `AD-12`

**Kontroll — hva testen ser etter:**
- Å starte webserveren utløser **null** nettkall, også når basen er tom
- Tom base gir tom-tilstand med beskjed om hvordan man henter, ikke en feilside
- Hentekommandoen er en egen inngang mot samme kodebase
- Nøkkelen leses fra miljøet, ikke fra en fil i imaget
- **Ville feilet hvis:** noen la hentingen i en oppstartskrok «for at det skal virke ut av boksen». To kjøringer samme dag hadde da brukt 30 av 20 kall

**Én økt:** ja.

### Story 2.3: Børsdagskontroll før kvoten brukes

Som **gruppe med 20 kall i døgnet**, vil jeg at kommandoen sjekker om vi
allerede har dagens data, så en kjøring nummer to ikke koster 15 kall til.

**Oppfyller:** FR-402 · **Begrenses av:** `AD-20`, `AD-10`, NFR-01

**Kontroll — hva testen ser etter:**
- Er lagrede data fra siste forventede børsdag, hentes **ingenting** og kalltelleren er uendret
- Er de eldre, hentes det
- Er nyeste dato i svaret ikke forventet børsdag, vises siste kjente data med tidsstempel
- Kontrollen regner børsdag i **norsk** kalenderdato
- **Ville feilet hvis:** kontrollen lå i webserveren. Den kan ikke handle på utfallet, og da ville sjekken vært pynt

**Én økt:** ja.

### Story 2.4: Etterfylling av hull i kursserien

Som **bruker som ikke åpnet løsningen på en uke**, vil jeg at grafen er hel når
jeg kommer tilbake, så hullet ikke ser ut som en kursbevegelse.

**Oppfyller:** FR-403 · **Begrenses av:** `AD-5`, NFR-01

**Kontroll — hva testen ser etter:**
- Fire dagers opphold fylles ved neste henting
- Etterfyllingen koster **15 kall**, ikke 15 per manglende dag
- Serien erstattes i sin helhet, den skjøtes ikke
- **Ville feilet hvis:** noen etterfylte vurderinger på samme måte. Kurser kan etterfylles; vurderinger kan ikke, og `AD-7` skal stoppe forsøket

**Én økt:** ja.

### Story 2.5: Vurderingen skrives i samme kjøring

Som **gruppe**, vil jeg at vurderingen regnes av kursene som nettopp ble lagret,
så den ikke kan regnes av en serie som er byttet ut siden.

**Oppfyller:** FR-408 · **Begrenses av:** `AD-17`, `AD-5`, `AD-7`

**Kontroll — hva testen ser etter:**
- Én kjøring skriver kurser **og** vurderinger for alle femten
- Vurderingen er regnet av de radene kjøringen selv lagret
- Kjøres kommandoen to ganger samme dag, finnes fortsatt én vurdering per aksje
- **Ville feilet hvis:** vurderingen ble skrevet av en egen kommando. Kjøres den etter en ny henting, er grunnlaget byttet ut — og raden ville lagret hva løsningen mente om *andre* data enn de som lå der

**Én økt:** ja.

### Story 2.6: Utbyttedager merkes

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
- Migrasjoner kjøres **uten** et eget kommandosteg
- **Ville feilet hvis:** migrasjonene ble lagt i en egen kommando. Det ville sett ut som ryddig ansvarsdeling og brutt suksessmålet «Drift»

**Én økt:** ja.

> **Denne storyen har ingen FR bak seg, og det er ikke storyens mangel.**
> Ingen av de sju NFR-ene dekker at løsningen skal kunne bygges og kjøres av
> andre — kontrollert 2026-09-22. PRD-en har altså ikke med selve leveransen,
> mens faglærer navngir «kildekode og docker fil» som innleveringen. Ført som
> spørsmål til gruppen, ikke rettet.

### Story 3.2: To volumer, og ingenting uerstattelig i imaget

Som **gruppe**, vil jeg at rådataøyeblikksbildene ligger utenfor alt som kan
slettes ved et uhell, så det som ikke kan hentes på nytt, overlever.

**Oppfyller:** NFR-07 · **Begrenses av:** `AD-11`, `AD-6`, `AD-9`

**Kontroll — hva testen ser etter:**
- `ose-db` og `ose-raa` er atskilte volumer
- Å fjerne basevolumet lar øyeblikksbildene stå
- Imaget kjører uten at noen av volumene finnes fra før
- **Ville feilet hvis:** ett volum dekket hele `data/`. Da tar én kommando med seg både det gjenoppbyggbare og det uerstattelige — og `vurdering` er uerstattelig selv om den ligger i basen

**Én økt:** ja.

---

## Epic 4: KI kan tas i bruk uten å bryte godkjenningen

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

### Story 4.2: `KILogg`-porten med minneimplementasjon

Som **utvikler**, vil jeg definere KI-loggen som en port før modellen finnes, så
arbeidet ikke venter på et valg som ikke er tatt.

**Oppfyller:** FR-604, FR-605 · **Begrenses av:** `AD-3`, `AD-7`

**Kontroll — hva testen ser etter:**
- Porten lagrer meldings-id, utsteder, kategori, publiseringstidspunkt, regelfilterets utfall, KI-vurdering, forklaring, usikkerhetsmerke, promptversjon og modell
- Porten har **ingen** `slett` og **ingen** `endre`
- Hele porten prøves mot minneimplementasjonen, uten database
- **Ville feilet hvis:** promptversjon og modell var utelatt fra raden. Justeres prompten i oktober, blir eksempelsettet en blanding av flere systemer som ser ut som ett

**Én økt:** ja. **Ingen avhengighet til Epic 1** — porten vet ikke om
lagringsformen.

### Story 4.3: SQLite-adapter for `KILogg`

Som **gruppe**, vil jeg at KI-loggen overlever en omstart, så eksempelsettet fra
én ukes drift finnes når det skal brukes.

**Oppfyller:** FR-604 · **Begrenses av:** `AD-4`, `AD-7`, `AD-16`

**Kontroll — hva testen ser etter:**
- `ki_logg`-tabellen opprettes av en nummerert migrasjon
- En skrevet rad finnes etter omstart
- Ingen vei gjennom adapteren kan slette eller endre en eldre rad
- **Ville feilet hvis:** tabellen ble opprettet utenfor migrasjonsløperen. Da har to utviklere hvert sitt skjema, og `AD-16` er brutt av den første som kjørte

**Én økt:** ja. **Avhenger av Epic 1.**

---

## Epic 5: KI-laget i drift 🔒

> **Blokkert.** Av åpent punkt 5b (betingelse 4, løses av story 4.1) **og**
> åpent punkt 1 og 19 (Euronext). Et nei 28.09 stryker hele epicen, fordi alle
> FR-6xx handler om meldinger.
>
> Storyene er skrevet likevel. En blokkert epic uten stories ser billigere ut
> enn den er, og da blir et nei vanskeligere å vurdere.

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

**Oppfyller:** FR-602 · **Begrenses av:** NFR-04, NFR-05

**Kontroll — hva testen ser etter:**
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

## Epic 6: Børsmeldinger i oversikten 🔒

> **Blokkert av åpent punkt 1 og 19.** Euronext forbyr automatisert henting uten
> tillatelse, og punkt 19 gjelder om innhold i det hele tatt kan sendes til en
> modelltjeneste.
>
> **Et nei stryker epicen i sin helhet — og tar Epic 5 med seg ned.**
> Logikken i `meldinger.py` er allerede bygget og testet; den blir liggende som
> kode uten datakilde.

### Story 6.1: Meldingskilden som port 🔒

Som **utvikler**, vil jeg at meldingene nås gjennom en port, så resten av
systemet ikke vet hvor de kom fra.

**Oppfyller:** — *(grunnlag for FR-404)* · **Begrenses av:** `AD-3`, `AD-2`

**Kontroll — hva testen ser etter:**
- `Meldingskilde` har én skriver, og lesere går gjennom porten
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

**Én økt:** ja.

---

## Epic 7: Kommende finansielle hendelser 🔒

> **Blokkert av åpent punkt 1 (Euronext), 3 (kilde for handelskalenderen) og 12
> (horisont og hendelsestyper).**
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

**Tidspunkt:** rett etter Epic 2, ikke før innlevering. Suksessmålets frist
«Før prosjektinnlevering» står fortsatt som ytre grense.

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

**Avhenger av:** 8.1. **Én økt:** ja.
