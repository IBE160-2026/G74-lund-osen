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
- **FR-409** — De tre tilstandene skal være skillbare i lageret *(ny 22.09. Rettet 2026-09-24: her sto «vises». Kravet gjelder lageret, ikke en skjerm)*

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
| FR-101, FR-102 | `markedsoversikt.py`, commit `706720f` |
| FR-103 | `markedsoversikt.py` + `index.html`. **`706720f` inneholdt bruddet** — den hadde `Retningsvisning("Opp", "↑", "opp")`, mens kravet krever modellens egen streng. Oppfylt av den senere commiten som fjernet oversettelsen |
| FR-201 | `aksjedetalj.py` `076bb12`, `graf.py` `b6ba9d8` |
| FR-202, FR-204 | Samme, **pluss `app.py` og `src/templates/`** — tegnforklaring, 200-svar og «kunne ikke regnes»-beskjed ligger der |
| FR-701 – FR-705 | `signalberegning.py`, commit `01af1a5` |
| FR-706 | `aksjedetalj.py` (`076bb12`) + `aksje.html`. **Ikke `signalberegning.py`** — kravet gjelder aksjedetaljen |

**Merk at tabellen er skrevet fra kjernemodulene.** `app.py` og
`src/templates/` bærer halvparten av fem av disse kravene, og sto ikke nevnt før
kontrollen 22.09 fant det.

**Fordelt på epics — 22 FR-er.** *Rettet 2026-09-24: her sto 21. Tabellen har 22, og summen under er 12 + 22.*

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
| **NFR-04** KI tar ikke ned hovedflyten | **Eid av Epic 5.** Bortfaller hvis Epic 5 strykes. *Rettet 2026-09-24:* bortfaller ikke med Epic 5 alene. Epic 5B begrenses også av NFR-04 (5B.2 og 5B.3), så kravet gjelder så lenge én av dem bygges |
| **NFR-05** Norsk | **Tverrgående, levert i alt som finnes.** **Kontroll på hver visningsstory:** all brukervendt tekst er norsk |
| **NFR-06** Ikke investeringsråd | **Tverrgående.** Forbeholdstekst finnes: `src/templates/index.html:108` sier «Signalstyrken er 0–3 og sier hvor kraftig de tre sjekkene slår ut — *ikke om aksjen bør kjøpes eller selges*». Kravet er likevel et **forbud**, ikke et tekstkrav: ingen del av grensesnittet skal formuleres som anbefaling. **Kontroll på hver visningsstory:** ordlyden leses mot NFR-06 |
| **NFR-07** Rådata bevares | **Eid av Epic 1** (`AD-6`). Delvis levert: `fetch_prices` skriver tidsstemplede øyeblikksbilder (`352e3a2`) |

**Alle sju NFR-er er plassert:** fire eid av en epic (NFR-01, 02, 04, 07), tre
tverrgående med navngitt kontroll (NFR-03, 05, 06).

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
```

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
- **Epic 5 etter både Epic 4.1 og Epic 6.** Se avhengighetsvarselet under.
- **Epic 8.1 rett etter Epic 2, ikke etter Epic 3.** Brukertesten trenger ekte
  data og begge skjermbildene, ikke Docker. Den kan kjøres på vår egen maskin.
- **Epic 8.2 etter 8.1.** Funnene fra brukertesten er det viktigste
  grunnlaget for gjennomgangen.

### Epic 1: Dataene overlever en omstart, og historikken lagres slik at den kan leses tilbake (punkt 20)

Brukeren kan slå av maskinen og finne oversikten igjen — og spørsmålet «hva sa
løsningen om EQNR for to uker siden?» får et svar. *Rettet 2026-09-24:* i v1
er historikken lagret, men ikke besvarbar. Hvordan spørsmålet skal kunne
stilles, er åpent punkt 20 i `prd.md`.

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

**FR-er:** FR-401, FR-402, FR-403, FR-407 · **NFR-01, NFR-02** · **AD-er:** 2, 10, 17, 20

De to kjente `AD-20`-feilene rettes her: `fetch_prices.main` som blander lokal
dato og UTC, og `meldinger._minutt` som kutter på tegn 16. FR-407 ligger her
fordi deteksjonen — avviket mellom `close`- og `adjusted_close`-endringen —
skjer på serien under henting, og den veien gjør kravet uavhengig av NewsWeb.

### Epic 3: Løsningen kan kjøres av andre enn oss

Sensor kan bygge og kjøre den, uten vår nøkkel og uten våre data.

**FR-er:** FR-401 (tom-tilstanden, story 3.3) · **AD-er:** 9, 10, 11, 12 · Dekker åpent punkt 18

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
| **Ved nei fra Euronext** | **Epicen strykes i sin helhet.** Alle seks FR-6xx er om meldinger — FR-602 «meldingene i samlekategorien», FR-604 «for hver melding», FR-606 «melding i samlekategorien». Uten Epic 6 finnes ikke datagrunnlaget. **Da bortfaller også NFR-04**, og suksessmålet «KI-bidrag i drift» kan ikke nås, fordi PRD-en måler det i hvilke *meldinger* laget forklarte. Det som overlever er relevanseksperimentet, som henter fra EODHDs nyhets-API og ikke fra NewsWeb — KI kan da demonstreres, men ikke vises i drift *Endret 2026-09-23:* med plan B (**Epic 5B**) er KI i drift likevel mulig, men som en forklaring av signalet, ikke av meldinger. Det som strykes, er KI-laget over meldinger. Plan A og B utelukker ikke hverandre: kommer et ja senere, bygges plan A oppå 5B. *Rettet 2026-09-24:* NFR-04 bortfaller ikke heller, fordi Epic 5B begrenses av det. |

### Epic 5B: KI forklarer signalet (plan B) 🔀

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

### Epic 6: Børsmeldinger i oversikten 🔒

**FR-er:** FR-404, FR-405, FR-501, FR-502, FR-503, del av FR-203

| Felt | |
|---|---|
| **Blokkert av** | Åpent punkt 1 — Euronext forbyr automatisert henting uten tillatelse på forhånd |
| **Eier** | Gruppen |
| **Avgjøres** | Forespørsel sendt 21.09, ubesvart. **28.09** er vår egen frist for å ta stilling uten svar |
| **Ved nei** | Strykes i sin helhet — **og tar Epic 5 med seg ned.** Det er ikke en fri strykning: den koster hele KI-laget, NFR-04, to av tre deler av FR-203, og suksessmålet «KI-bidrag i drift». Logikken i `meldinger.py` er bygget og testet fra før, og blir liggende som kode uten datakilde *Endret 2026-09-23:* det tar KI-laget **over meldinger** med seg ned, ikke hele KI-laget. Epic 5B står igjen. *Rettet 2026-09-24:* NFR-04 blir også stående, fordi Epic 5B begrenses av det. |

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

### Epic 9: Dokumentasjon av prosessen

Sensor kan se hvordan KI ble brukt og hvordan koden er kvalitetssikret, uten å
lese git-loggen. Emnesiden legger dette under prosjektkoden (70 %): «Dokumentasjon
må vise hvordan KI ble brukt, og hvordan studentene har kvalitetssikret koden».

**FR-er:** ingen · Avhengigheter: 9.1 etter Epic 1; 9.2 og 9.3 ingen; 9.4 uke 39–40

---

# Stories

42 stories. Hver bærer hvilket krav den oppfyller, hvilke `AD`-er som begrenser
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
- **Ville feilet hvis:** noen la til en `oppdater`-metode «for migrasjoner», eller hvis datogrensen ble regnet i UTC — da ville en kjøring 00:30 norsk tid (22:30 UTC dagen før) skrevet på
  gårsdagen. *Rettet 2026-09-24:* her sto 23:30. Det er samme dato i UTC og
  avslører ingenting. Feilvinduet er 00:00–02:00 norsk sommertid (00:00–01:00
  om vinteren), og 00:30 ligger i begge

**Forutsetning:** story 1.5b er ferdig. `0002` skrives ikke før
migrasjonsløperen og SQLite-adapteren er herdet. *Flyttet 2026-09-24:
forutsetningene a–h sto her og er nå kontrollpunktene i 1.5b.*

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

**Forutsetning** *(lagt til 2026-09-24)*: «ingen rad på en børsdag betyr at
kommandoen ikke ble kjørt» holder ikke i to tilfeller. Kommandoen kan ha kjørt
før dagens kurs var publisert (åpent punkt 23), og et symbol kan ha feilet mens
de andre ble hentet (`AD-15`). Begge gir ingen rad, uten at det er et hull i
driften. Ført som **åpent punkt 24** i `prd.md`, med frist før denne storyen:
en fjerde tilstand, eller en lagret grunn.

**Én økt:** ja.

---

## Epic 2: Ferske data uten at kvoten sprenges

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
   som **åpent punkt 23** i `prd.md`, med frist før story 2.1.

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

**Forutsetning** *(fra kodegjennomgangen 2026-09-23)*: Flask kjører
forespørsler i egne tråder (`threaded=True` er standard, `flask/app.py:655`), og
en `sqlite3`-tilkobling kan som standard ikke deles mellom tråder
(`check_same_thread`). Prøvd: brukt fra en annen tråd gir den `ProgrammingError`.
Det avgjøres her hvordan webserveren åpner basen, for eksempel én tilkobling per
forespørsel. Åpner webserveren basen tidligere, følger forutsetningen dit.

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
- **Et symbol som feilet** (`AD-15`): storyen sier eksplisitt hva som skrives
  for det, og testen prøver det. Svaret avgjøres av åpent punkt 24 før 1.7: en
  rad med en egen tilstand, eller en rad med grunnen. Ingen rad er ikke et
  gyldig svar, fordi det da leses som at kommandoen ikke ble kjørt. *Lagt til
  2026-09-24*
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
> spørsmål til gruppen, ikke rettet. *24.09: sagt av faglærer i samtale 21.09,
> ikke på emnesiden (hjelpelærer 23.09); lages likevel.*

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


### Story 3.3: README — «Slik kjører du den»

Som **en som ikke er oss**, vil jeg komme fra et rent utsjekk til begge
skjermbildene med ekte data ved å følge README alene.

**Oppfyller:** FR-401 (tom-tilstanden) · **Begrenses av:** `AD-9`, `AD-10`, `AD-12`

**Kontroll — hva testen og den ferdige storyen ser etter:**
- README-seksjonen: egen gratisnøkkel fra EODHD (20 kall i døgnet holder til én
  henting av de 15 symbolene), `.env` fra `.env.example`, bygging av imaget, og
  de to kommandoene — webserveren og hentingen
- **Avsnittet «Kom i gang» erstattes helt,** ikke utvides. Det sier i dag
  «Applikasjonen leser bare fra `data/`», som blir usant etter 1.4 og 1.5
- **Den tomme siden sier hvordan man henter, med samme kommando som README.**
  I dag sier den «Ingen kursdata funnet i `data/`. Kjør
  `uv run python src/fetch_prices.py` først» (`index.html:110–114`). Etter
  Epic 2 og 3 er det feil kommando og feil sted
- Kommandoen i tom-tilstanden kommer fra én konstant, og en test krever at den
  står i den tomme siden
- **Ville feilet hvis:** README og den tomme siden viste hver sin kommando. Da er
  det tilfeldig hvilken av dem som stemmer

**Avhenger av:** 3.1. **Én økt:** ja.

---

## Epic 4: KI kan tas i bruk uten å bryte godkjenningen

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
- `gethostbyname`, `gethostbyname_ex` og `getfqdn` sperres også
- `getaddrinfo`-erstatningen får signaturen `(host, port, *resten, **navngitt)`,
  og `AF_UNIX` slippes gjennom
- Tester for `connect_ex` og for en fixture med `scope="module"`. Docstringen i
  `test_loopback_slippes_gjennom` rettes: Flask-testklienten bruker ikke socket
  (kontrollert 24.09: ingen `socket.connect`-kall fra `test_client().get("/")`)
- **Ville feilet hvis:** en fixture med `scope="module"` kunne nå nettet

**Én økt:** ja.

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

## Epic 5B: KI forklarer signalet (plan B) 🔀

> **Utløses av nei eller taushet fra Euronext 28.09.** 5B.1 kan bygges før
> det, fordi den ikke sender noe. Plan A og B utelukker ikke hverandre.

### Story 5B.1: Grunnlaget som sendes — bare utledede verdier

Som **gruppe**, vil vi at det som sendes til modellen, er bestemt av én ren
funksjon, så ingen kan sende rådata ved et uhell.

**Oppfyller:** — *(plan B, punkt 2)* · **Begrenses av:** `AD-1`, betingelse 4

**Kontroll — hva testen ser etter:**
- `ki_grunnlag(signal)` er ren logikk og gir bare: fortegnet og målingen for hver
  av de tre sjekkene, styrken og retningen
- Interessesjekken sendes som **forholdstall** (volum mot median), ikke som de to
  volumtallene. Forklaringsteksten i dag inneholder rå volumtall
  (`signalberegning.py:165`)
- En test krever at ingen kurs og ingen volumverdi fra serien finnes i grunnlaget
- **Ville feilet hvis:** grunnlaget inneholdt dagens volum eller en kurs. Da
  sendes et rått datapunkt fra EODHD til en tredjepart, og det har ingen av
  svarene fra EODHD godkjent

**Én økt:** ja. Kan bygges før 28.09, fordi den ikke sender noe.

### Story 5B.2: Teksten lages i hentekommandoen og lagres i `KILogg`

Som **bruker**, vil jeg at KI-teksten er klar når jeg åpner siden, så jeg aldri
venter på en modell.

**Oppfyller:** — *(plan B, punkt 1 og 4)* · **Begrenses av:** `AD-2`, `AD-8`,
`AD-10`, `AD-17`, NFR-02, NFR-04

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
- **Ville feilet hvis:** KI-kallet lå i webserveren. Da koster hver visning av
  siden et kall, brukeren venter (NFR-02), og teksten som ble vist, finnes ikke
  igjen i loggen

**Én økt:** ja.

### Story 5B.3: Visningen i aksjedetaljen

Som **bruker**, vil jeg lese regelforklaringen først og KI-teksten som et tillegg,
så jeg alltid ser hva signalet faktisk bygger på.

**Oppfyller:** — *(plan B, punkt 1)* · **Begrenses av:** NFR-04, NFR-05, NFR-06

**Kontroll — hva testen ser etter:**
- Regelforklaringen (FR-706) står først og er alltid synlig
- KI-teksten står under, merket som laget av KI, med modellnavnet
- Av/på-bryteren er synlig for brukeren. Med KI av er siden lik den som finnes i
  dag
- En dag uten KI-tekst sier det, i stedet for å vise et tomt felt
- En vakt på vår side: tekst med ord som «kjøp», «selg» eller «anbefal» vises
  ikke, men logges (NFR-06)
- **Ville feilet hvis:** KI-teksten erstattet regelforklaringen eller sto før den.
  Da leses KI som kilden og regelen som en fotnote

**Én økt:** ja.

### Story 5B.4: Måle bidraget — egen brukertest, etter 8.1

Som **gruppe**, vil vi vite om KI-teksten faktisk hjelper, så refleksjonsrapporten
kan vurdere det kritisk i stedet for å anta det.

**Oppfyller:** suksessmålet «KI-bidrag i drift», tilpasset plan B · **Begrenses
av:** —

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

---

## Epic 6: Børsmeldinger i oversikten 🔒

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

**Spørsmål testen skal svare på** *(lagt til 2026-09-23)*: **Er oversikten for
tett med 15 rader?** 15 er valgt av kvoten, ikke av skjermen, og antall rader
per skjermbilde avgjøres ikke før testen har svart. Svaret observeres, det
spørres ikke om: stopper personen, scroller tilbake eller mister raden de leste,
noteres det, med tidspunkt.

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

**Føring** *(lagt til 2026-09-23, fra v1.1-idéene i `prd.md` §8)*: gjennomgangen
skal si **hvordan et tredje skjermbilde ville passet inn** i navigasjonen, uten å
bygge det. Det er et svar på papir, ikke en endring.

**Avhenger av:** 8.1. **Én økt:** ja.

---

## Epic 9: Dokumentasjon av prosessen

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

**Oppfyller:** suksessmålet «Relevanseksperiment», del 1 (PRD §7, åpent punkt
5) · **Begrenses av:** regel 6 og 16 i `CLAUDE.md`

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
