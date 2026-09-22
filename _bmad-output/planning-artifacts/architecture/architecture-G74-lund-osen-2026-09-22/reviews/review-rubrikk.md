---
type: review
rubrikk: good-spine checklist
gjelder: ARCHITECTURE-SPINE.md (status draft, updated 2026-09-22)
utfoert: 2026-09-22
metode: dokumentet lest i sin helhet; .memlog.md og prd.md lest; src/ og tests/ lest; alle åtte commit-påstander kontrollert med git show --stat
---

# Rubrikk-gjennomgang — ARCHITECTURE-SPINE.md (OSE Signal)

## Dom

Spinen er uvanlig godt forankret: **hver eneste ADOPTED-påstand jeg kunne
kontrollere, stemmer** — commit-hasher, datoer, meldinger, berørte filer,
måletall, testtall og versjoner. Men den **ratifiserer ett lag feil**
(`kursdata.py` er ikke I/O-fri), den er **helt taus om et helt PRD-kapittel**
(FR-301..FR-303, kommende finansielle hendelser), og den **låser FR-407 til
en kilde den selv andre steder sier kanskje ikke finnes**. De tre er alle
divergenspunkter for epics/stories, altså nettopp det spinen finnes for.

---

## 1. Fikser den de reelle divergenspunktene for nivået under?

**Treff.** Disse er ekte divergenspunkter, og de er skikkelig lukket:

| Truffet | Hvorfor det er ekte |
|---|---|
| AD-3 (én port per eid datasett) | Uten den bygger FR-408-storyen og FR-604-storyen hver sin skrivesti |
| AD-7 (ingen slett/endre på uerstattelige lagre) | «Fraværet er invarianten» er et sjeldent presist grep, og det er testbart |
| AD-10 (webserveren henter aldri) | Kvoten er 20, en henting koster 15 — to `docker run` er dagen brukt opp |
| AD-11 + AD-9 (to volumer, ingen data i imaget) | Volumstrukturen gjør regelen strukturell istedenfor noe man må huske |
| AD-14 (deduplisering før kategorifilter) | Rekkefølgen er ikke åpenbar, og feil vei teller dubletter to ganger |
| AD-5 (serien skjøtes aldri på) | Den virkelige grunnen — adjusted_close regnes om bakover — står der |

**Bom — FUNN 1 (kritisk).** *FR-301, FR-302 og FR-303 finnes ikke i spinen.*
PRD-ens §4.3 «Kommende finansielle hendelser» er ikke i `binds`, ikke i
Capability-kartet, ikke i Deferred og ikke ført som åpent punkt. Kapittelet
innfører tre ting som er arkitekturens eget ansvar:

1. **En tredje ekstern kilde** — Euronexts finanskalender (FR-301). Den må
   hentes over nett, og det kolliderer med AD-2 (se funn 2).
2. **Et nytt eid datasett** — oppslagstabellen som knytter kalenderoppføringer
   til selskap, fordi kalenderen «oppgir verken ticker eller ISIN» og tabellen
   «vedlikeholdes manuelt». Under AD-3 skal det ha nøyaktig én port og én
   skriver. Ingen port er navngitt.
3. **En tom-tilstand med egen regel** — FR-303 sier at manglende hendelser
   vises som *fravær av seksjon*, ikke feilmelding. Det er samme familie som
   AD-15, men er ikke ført dit.

Koden vet dette selv: `src/app.py` sin docstring i `aksjedetalj()` sier
«Meldinger, KI-forklaring og **kommende hendelser** mangler med vilje». Spinen
har fanget de to første og mistet den tredje.

*Konsekvens:* to stories kan trygt sprike — én legger kalenderkallet i
`fetch_prices.py` for å respektere AD-2, en annen gir den egen modul med egen
`requests`-import. Begge kan forsvare seg mot spinen slik den står.

*Rettes ved:* enten en AD for kalenderkilden, eller en Deferred-rad som sier
hvor svaret skal lande (modul + port), selv om kilden er åpen.

---

## 2. Er hver Rule HÅNDHEVBAR, og hindrer den divergensen den påstår?

Gjennomgående ja — flere regler er strukturelle og ikke disiplinbaserte
(AD-7s fravær av metode, AD-11s to volumer, AD-8s autouse-fixture). Tre
unntak:

**FUNN 2 (høy) — AD-2s regel er for smal til å overleve PRD-en.**
Regelen lyder: «`fetch_prices.hent_ett_symbol` er eneste sted `requests`
brukes.» Men PRD-en krever to nettkilder til:

- FR-404: meldinger etterfylles fra NewsWeb (`fromDate`/`toDate`).
- FR-301: hendelser hentes fra Euronexts finanskalender.

Regelen kan dermed ikke holdes uten å la være å bygge to krav. Deferred
skjermer NewsWeb fra å bli *låst inn*, men sier ingenting om hva som skjer
med AD-2 når kilde nummer to kommer. Resultatet er en regel som enten blir
stilltiende brutt, eller som blokkerer en story — og i begge tilfeller
forsvinner invarianten den skulle gi.

*Den håndhevbare formen er invarianten under påstanden:* nettkall skjer bare
i skall-laget, én funksjon per kilde, og alle konsumenter får hentefunksjonen
injisert — slik `hent_universet(..., hent=hent_ett_symbol)` allerede gjør det
(kontrollert i `src/fetch_prices.py`, linje 82–88). Formulert slik overlever
regelen at kilde nummer to og tre kommer.

**FUNN 6 (middels) — AD-5s «minst 175 handelsdager» er ikke håndhevet noe
sted.** Koden har `DAGER_TILBAKE = 364` og `MINST_HANDELSDAGER = 51`, og 51
gir bare en merknad i utskriften («← for kort for MA50»), ikke en feil. PRD-ens
FR-406 skrev nettopp 175-kravet inn fordi tallet var «en egenskap ved
implementasjonen, ikke noe noe krav ba om». Spinen gjentar tallet uten å gi
det en håndhever — verken en sjekk, en test eller en ansvarlig modul. Det er
samme fellen PRD-en allerede har beskrevet, ett nivå opp.

**FUNN 7 (lav/middels) — AD-1s regel er en liste med fire modulnavn.**
`requests`, `sqlite3`, `pathlib`, `flask`. `urllib.request`, `httpx`, `open()`
og `os.path` går rett gjennom. Kjernen er ren i dag (kontrollert: kun
`dataclasses`, `datetime`, `statistics` og prosjektmoduler), og presedensen for
å håndheve finnes — `tests/test_ingen_nettverk.py` gjør akkurat dette for
nett. En importtest over kjernemodulene ville gjort AD-1 like hard som AD-8.

---

## 3. Kan noe under Deferred la to enheter sprike?

| Utsatt | Kan sprike? |
|---|---|
| FR-401 må skrives om | Nei — og håndteringen er forbilledlig: spinen nekter å overstyre PRD-en stilltiende |
| Nøyaktig Docker-baseimage | Nei — én fil, én forfatter, og bindingen (3.13 som i CI) er gitt |
| Om SQLite godtas | Nei — AD-3 gjør motorbyttet lokalt, og det er eksplisitt begrunnet |
| KI-laget (FR-601..606) | Lav risiko — AD-3/AD-7 holder formen, modelltjenesten er reelt uavklart |
| De to `[FORELØPIG]`-vinduene | Nei — konstanter på ett sted, merket i koden |
| **Kilde for handelskalenderen** | **Ja — FUNN 5 (middels)** |
| **NewsWeb-hentingen** | **Ja, indirekte — se funn 4** |

**FUNN 5 (middels).** Handelskalenderen er utsatt på *kilde*, men FR-402
trenger «forventet børsdag» for å avgjøre om et svar er ferskt, og det er
hentekommandoens egen logikk. Utsettelsen sier hvor svaret *ikke* er, ikke hvor
det skal lande. En story kan hardkode en helligdagsliste i `fetch_prices.py`,
en annen kan utlede børsdager av `date`-feltene i serien. Utsettelsen burde
feste **plasseringen** (modul/port) selv når kilden står åpen — samme grep
som Deferred gjør for Docker-baseimaget, der bindingen holdes selv om taggen er
åpen.

---

## 4. Er navngitt teknologi verifisert-gjeldende?

**Ja, og det er kontrollert mot filene, ikke antatt.** Stack-tabellen stemmer
ordrett med `pyproject.toml` og `.github/workflows/tester.yml`:

| Påstand i spinen | Funnet i repoet |
|---|---|
| Python 3.13, `requires-python = ">=3.13"`, CI pinner 3.13 | Stemmer — `pyproject.toml` og `setup-uv` med `python-version: "3.13"` |
| Flask >= 3.0, requests >= 2.32, python-dotenv >= 1.0, pytest >= 8.0 | Stemmer ordrett |
| `uv.lock`, CI kjører `uv sync --locked` | Stemmer |
| sqlite3 fra standardbiblioteket | Riktig for 3.13 — ingen ny avhengighet |
| Ingen frontend-avhengighet | Stemmer — `src/templates/` har to maler, `graf.py` regner SVG-koordinater |

At Docker-baseimaget er utsatt til Dockerfilen skrives, med bindingen «samme
Python-versjon som CI», er riktig håndtert: en tag navngitt i dag ville vært
uverifisert i morgen.

---

## 5. Ratifiserer den kodebasen, eller motsier den den?

### 5a. Commit-påstandene — alle åtte stemmer

Kontrollert med `git show --stat`:

| Commit | Dato | Melding | Berørte filer | Dom |
|---|---|---|---|---|
| `be2ba93` | 2026-09-21 | Legg datalaget bak et grensesnitt… | `src/kursdata.py`, `tests/test_kursdata.py` | Stemmer — AD-3 og AD-7s `SnapshotKilde`-presedens har riktig opphav |
| `266e6d9` | 2026-09-21 | Legg inn CI, og gjør løftet om null nettbruk håndhevet | `.github/workflows/tester.yml`, `tests/conftest.py`, `tests/test_ingen_nettverk.py` | Stemmer — AD-8 |
| `352e3a2` | 2026-09-21 | Rett fetch_prices: de 15 aksjene og et helt år… | `src/fetch_prices.py`, `src/kursdata.py`, tester | Stemmer — AD-2 |
| `01af1a5` | 2026-09-20 | Bygg signalberegningen med tester ved siden av koden | `src/signalberegning.py` + test | Stemmer — AD-1, AD-13 |
| `9acb55c` | 2026-09-20 | Legg til deduplisering og kategorifilter med tester | `src/meldinger.py` + test | Stemmer — AD-1, AD-14 |
| `706720f` | 2026-09-21 | Bygg markedsoversikten som ren logikk… | `src/markedsoversikt.py` + test | Stemmer — AD-1 |
| `076bb12` | 2026-09-21 | Bygg forklaringsdelen av aksjedetaljen som ren logikk | `src/aksjedetalj.py` + test | Stemmer — AD-1 |
| `b6ba9d8` | 2026-09-21 | Skaler kursgrafen til SVG-koordinater, som ren regning | `src/graf.py` + test | Stemmer — AD-1 |

Ingen feil opphav funnet. Datoene i parentes i spinen stemmer med
commit-datoene.

### 5b. Andre etterprøvbare påstander — stemmer

- **«166 tester grønne 2026-09-22»**: `pytest --collect-only` gir *166 tests
  collected* i dag. Tallet er ikke pyntet.
- **AD-8s mekanisme**: `tests/conftest.py` monkeypatcher faktisk
  `socket.socket.connect` og `connect_ex` med `@pytest.fixture(autouse=True)`,
  og `LOOPBACK = {"127.0.0.1", "::1", "localhost"}` slipper gjennom. Ordrett
  som beskrevet.
- **AD-13s måletall**: «199 handelsdager og 2 985 aksjedager» står i
  `malinger.md` §7.4. Konstantene i `signalberegning.py` bærer målingen i
  kommentaren ved siden av seg, som påstått.
- **`[FORELØPIG]`**: står faktisk i koden over `VOLATILITET_VINDU` og
  `VOLUM_VINDU` («Disse to var ikke med i testen 21.09»).
- **AD-15s «ingen ny sjanse»**: står i `hent_universet`-docstringen og i
  koden (`continue` etter at `kall_brukt` er økt).
- **AD-12**: `.gitignore` utelater `.env`, `.env.example` inneholder bare
  variabelnavnet, CI har `permissions: contents: read` og ingen hemmeligheter.
- **Avhengighetsdiagrammet**: stemmer mot faktiske imports, inkludert at
  `graf.py` importerer `Punkt` fra `aksjedetalj.py`, og at
  `signalberegning.py` og `meldinger.py` er løvnoder.

### 5c. FUNN 3 (høy) — lagtabellen motsier `src/kursdata.py`

Spinen skriver:

> | **Porter** | `kursdata.py` | Bare `Protocol`-definisjoner og verdityper. **Ingen implementasjon som rører I/O** |

Faktisk innhold i `src/kursdata.py`:

- `import json`, `from pathlib import Path`
- `PROSJEKTROT = Path(__file__).resolve().parent.parent` og `DATA_KATALOG`
- `SnapshotKilde.fra_fil(sti)` — `sti.read_text(...)` + `json.loads(...)`
- `nyeste_snapshot(katalog)` — skanner katalogen med regex mot filnavn

Det er I/O, og det er ikke en verditype. **Memloggen sier selv det motsatte av
spinen:** «Skallet er fetch_prices.py (nett), **kursdata.py (lagring)** og
app.py» (memloggens paradigme-oppføring). Spinen har altså flyttet
`kursdata.py` fra skall til port i destillasjonen, uten at noen beslutning i
memloggen sier det.

Dette er ikke pedanteri, fordi det åpner et konkret divergenspunkt:
`src/app.py` kaller i dag `nyeste_snapshot()` og `SnapshotKilde.fra_fil()`
**direkte** i `hent_kilde()` — utenom enhver `Kurslager`-port. Når
`lagring_sqlite.py` kommer, sier spinen ingenting om hva som skjer med
`SnapshotKilde` og `nyeste_snapshot`:

- Story A ruter `app.py` gjennom `Kurslager` og lar filkilden dø.
- Story B beholder `SnapshotKilde` som «fallback når basen er tom» — og
  AD-10 kan til og med brukes som argument for det, siden tom base skal gi
  tom-tilstand.

Begge er forsvarlige mot spinen slik den står. Og legg merke til at
AD-6s velger `nyeste_snapshot` **er** filkoden — den ligger i fila spinen
kaller I/O-fri.

*Rettes ved:* enten en egen rad i lagtabellen for rådatalesingen med
filplassering, eller en omformulering: «`kursdata.py` holder porter,
verdityper, universet og rådatalesing. Ingen nett, ingen database.» Og én
setning om hvor `SnapshotKilde` havner etter AD-4.

### 5d. FUNN 4 (høy) — FR-407 låses til en kilde spinen selv utsetter

`Structural Seed` sitt ER-diagram fastsetter:

```
KURS }o--o| MELDING : "eks.dato (utsteder, dato)"
```

og AD-4 bruker nettopp denne joinen som begrunnelse for databasen. Samtidig
sier Deferred at NewsWeb-hentingen er åpen, at Euronext forbyr automatisert
henting, og at «arkitekturen låser seg derfor **ikke** til at meldingsdelen
finnes». De to kan ikke begge være sanne: FR-407 i kjerneentitetsmodellen
*er* en låsing til meldingsdelen.

Verre: **PRD-ens åpne punkt 4 har allerede en målt vei ut**, funnet
2026-09-21 — avviket mellom `close`-endringen og `adjusted_close`-endringen
peker ut eks.dato, 38 hendelser over 3 720 dagovergangner, med et rent skille
fra 0,05 til 0,5 prosentpoeng. PRD-en skriver selv: «**Konsekvensen er større
enn kravet:** FR-407 blir da uavhengig av EKS.DATO-meldinger, og dermed av
NewsWeb og punkt 1.»

Spinen nevner ikke punkt 4 med et ord. Det er det tyngste enkeltfunnet etter
funn 1, fordi det treffer tre ting samtidig: entitetsmodellen, AD-4s
begrunnelse, og hvilken story FR-407 faktisk blir.

*Rettes ved:* føre FR-407 som åpen dimensjon med to navngitte veier
(meldingsjoin vs. utledet fra `adjusted_close`), og gjøre ER-kanten betinget.
AD-4 tåler det — de to andre grunnene (FR-408-oppslaget, FR-604/605-spørringen)
bærer valget alene.

---

## 6. Dekker den PRD-ens krav, og finnes ID-ene?

**Alle siterte ID-er finnes i `prd.md`.** Kontrollert mot hele
FR/NFR-registeret: FR-101..103, FR-201..204, FR-301..303, FR-401..408,
FR-501..503, FR-601..606, FR-701..706, NFR-01..07. Ingen oppdiktet ID, ingen
feilnummerering.

Dekning:

| Krav | Status i spinen |
|---|---|
| FR-101..103, FR-201..204 | Dekket (AD-1, AD-3, kapabilitetskartet) |
| FR-301..303 | **Ikke nevnt noe sted — funn 1** |
| FR-401..408 | Dekket, og FR-401-konflikten er ærlig ført |
| FR-501..503 | Dekket (AD-14), med NewsWeb-forbeholdet |
| FR-601..606 | Utsatt med begrunnelse; FR-604/605 delvis bundet av AD-3/AD-7 |
| FR-701..706 | Dekket (AD-13); de to `[FORELØPIG]`-vinduene merket |
| NFR-03, NFR-07 | Bundet og dekket |
| NFR-01 | Ikke i `binds`, men i praksis hele grunnen til AD-2 og AD-10 |
| **NFR-02** | **Truffet av AD-10, men ikke ført — se under** |
| NFR-04, NFR-05, NFR-06 | Ikke arkitekturbærende i v1; greit utelatt |

**FUNN 8 (middels) — NFR-02 og FR-402 står i samme konflikt som FR-401.**
Deferred fører FR-401 til omskriving, korrekt og ryddig. Men NFR-02 sier
«Henting og KI-behandling skjer som **bakgrunnsoppgave**», og FR-402 sier at
hentingen «prøves igjen **ved neste oppstart**». Begge hviler på den samme
oppstartsmekanismen som AD-10 avskaffer. Konflikten er ført for ett av tre
krav. Når FR-401 skrives om, må NFR-02 og FR-402 med i samme endring, ellers
står PRD-en igjen med to setninger som beskriver en mekanisme som ikke finnes.

---

## 7. Er hver dimensjon besluttet, utsatt eller ført som åpent punkt?

Driftskonvolutten er den **best** dekkede delen av spinen — AD-9 (ingen data i
imaget), AD-10 (null kall ved start), AD-11 (to volumer), AD-12 (hemmeligheter
fra miljøet) og CI i AD-8 er fem reelle driftsbeslutninger med begrunnelse.
Ingen taushet på det store.

To hull innenfor konvolutten:

**FUNN 9 (middels) — AD-16 sier at migrasjoner finnes, men ikke hvem som
kjører dem eller når.** Med to kommandoer mot samme image (`docker run` = web,
`docker run … hent`) er det tre mulige svar, og alle tre kan forsvares:

1. Webkommandoen migrerer ved oppstart — men AD-10s ånd er at `docker run`
   ikke gjør arbeid utover å vise.
2. Hentekommandoen migrerer — da er en fersk base uten henting ubrukelig, og
   tom-tilstanden i AD-10 kan ikke leses.
3. En tredje kommando — da må den stå i leveransen.

To personer som bygger hver sin kommando vil velge hver sitt. Dette er akkurat
den klassen divergens spinen er skrevet for å hindre, og AD-16 er dessuten den
eneste AD-en uten kode bak seg (merket som ny, korrekt).

**FUNN 10 (lav) — kjøremåten i containeren er ikke ført.** `src/app.py` har
ingen `if __name__ == "__main__"` og ingen WSGI-oppføring, og importene er
flate (`from kursdata import …`) og virker bare fordi `pyproject.toml` setter
`pythonpath = ["src"]` for pytest. I en container finnes ikke det oppsettet.
Hvordan Flask serveres (utviklingsserver eller WSGI), hvilken port og hvilken
`PYTHONPATH`/arbeidskatalog som gjelder, er ikke bestemt. Det er en liten sak
med Dockerfilen foran seg — men den er ikke ført noe sted, og den vil bli
oppdaget under demonstrasjonsforberedelsen istedenfor før.

Positivt verdt å merke: AD-12 kunne med fordel si eksplisitt at
**webkommandoen ikke trenger `EODHD_API_KEY` i det hele tatt**. Det styrker
AD-10 strukturelt — sensoren kan kjøre visningen uten noen nøkkel, og da er
kvoteforbruket null ved konstruksjon.

---

## Funn sortert etter alvorlighetsgrad

| # | Alvorlighet | Funn |
|---|---|---|
| 1 | **Kritisk** | FR-301..303 (hele §4.3, Euronexts finanskalender + manuell oppslagstabell) er taus: ikke bundet, ikke kartlagt, ikke utsatt, ikke åpent punkt |
| 2 | **Høy** | AD-2s regel («eneste sted `requests` brukes») kan ikke overleve FR-404 og FR-301; den håndhevbare invarianten er «bare i skallet, én funksjon per kilde, injisert til konsumenter» |
| 3 | **Høy** | Lagtabellen kaller `kursdata.py` I/O-fri. Fila leser filer (`SnapshotKilde.fra_fil`, `nyeste_snapshot`). Memloggen selv plasserer den i skallet. Åpner divergens om hvor rådatalesingen havner når SQLite kommer |
| 4 | **Høy** | FR-407 låses til EKS.DATO-joinen i ER-diagrammet, mens NewsWeb utsettes — og PRD-ens åpne punkt 4 (målt vei via `adjusted_close`-avviket) er ikke nevnt |
| 5 | **Middels** | Utsettelsen av handelskalenderen fester ikke hvor svaret skal lande (modul/port), bare at kilden er åpen |
| 6 | **Middels** | AD-5s «minst 175 handelsdager» har ingen håndhever; koden advarer først under 51 |
| 8 | **Middels** | NFR-02 og FR-402 hviler på samme oppstartsmekanisme som AD-10 avskaffer; bare FR-401 er ført til omskriving |
| 9 | **Middels** | AD-16 sier ikke hvem som kjører migrasjonene eller når — tre forsvarlige svar med to kommandoer |
| 7 | **Lav/middels** | AD-1s regel er en liste med fire modulnavn; `urllib`, `httpx`, `open()` går gjennom. Presedens for håndheving finnes i `test_ingen_nettverk.py` |
| 10 | **Lav** | Kjøremåten i containeren (WSGI/port/`PYTHONPATH`) er ikke ført; dagens flate imports virker bare via `pythonpath = ["src"]` i pytest-konfigurasjonen |

## Det som bør sies også

Tre ting er gjort bedre enn vanlig og bør ikke drukne i funnlista:

1. **Ingen falske opphav.** Åtte commit-påstander, åtte treff. I dokumenter
   av denne typen er det normalt å finne minst én hash som peker feil.
2. **Deferred-raden om FR-401.** Å oppdage at en arkitekturbeslutning motsier
   et krav, og så *nekte å fikse det i spinen*, er riktig håndtering av
   grensen mellom nivåene.
3. **AD-7s «fraværet er invarianten».** En regel som håndheves av at en metode
   ikke finnes, kan ikke glemmes i en code review.
