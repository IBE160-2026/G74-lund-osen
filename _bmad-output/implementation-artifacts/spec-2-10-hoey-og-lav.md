---
title: 'Story 2.10: høy og lav lagres med kursene'
type: 'feature'
created: '2026-11-19'
status: 'done'
route: 'dispatch'
baseline_commit: 'd764b9e5'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md'
---

Skrevet 19.11 etter instruksjonen kl. 14:24 og de to tilleggene kl. 14:27 og
14:39, ført i `docs/ai-prompts/2026-11-19.md`. Storyen står i `epics.md` som
2.10. Worktreen `G74-lund-osen-2-10`, grenen `2-10-hoey-og-lav`, fra
`origin/main` (`d764b9e5`).

## Storyen

Som **bruker** vil jeg at dagens høyeste og laveste kurs finnes i basen, så
aksjedetaljen kan vise dem uten et nytt kall.

**Oppfyller:** FR-203 (tillegget 2026-10-07) · **Begrenses av:** AD-5, AD-6,
AD-16, AD-19, NFR-01, NFR-08, regel 16 og 22

**Avhenger av:** ingen åpne. **Én økt:** ja.

## Svaret

*Svar 2026-11-19 kl. 13:51 (gruppens svar på rådets spørsmål):* 2.10 tas i dag,
med ny migrasjon og endret henting kvelden før brukertest 2. Rådet anbefalte å
vente til etter brukertest 2. Svaret er gitt i økta til instruksjonen, og
instruksjonen står ordrett i dagsfila (regel 3).

## Kontrollen i storyen

Fra `epics.md`, og den gjelder:

- Adapteren i `eodhd.py`, `Kursrad` og lageret tar med `high` og `low` fra
  svaret, og en ny migrasjon legger dem til (AD-16).
- Ingen nye kall. Øyeblikksbildene har feltene alt (AD-6), og neste henting
  fyller dem for hele året, fordi serien byttes ut (AD-5).
- En rad uten `high` eller `low` lagres uten dem.
- Grenen bruker bare testbaser og rører aldri `data/db/ose.db`.
- **Ville feilet hvis:** en rad uten `high` eller `low` stoppet hentingen.

## Det som er nå

Slått opp på `d764b9e5`:

- `Kursrad` i `src/kursdata.py` har `dato`, `slutt`, `justert_slutt` og
  `volum`, og ingen av dem kan mangle.
- `kursrad_fra_eodhd` i `src/eodhd.py` leser `date`, `close`, `adjusted_close`
  og `volume`. Et felt som mangler, gir `KeyError`, og `serie_fra_eodhd` gjør
  det til `UgyldigSerie`, så hele serien for aksjen avvises.
- Tabellen `kurs` fra `0001_kurs.sql` har de samme fire kolonnene. Siste
  migrasjon er `0014_regnet.sql`.
- Radene i testene (`tests/eodhd_serier.py`) har `high` og `low`, som svarene
  fra EODHD.
- PRD-en har raden «FR-203 | Høy og lav og endringen i kroner | senere | nei».
  Den gjelder det aksjesiden viser.

## Delene

1. **`Kursrad`** får `hoey` og `lav`, valgfrie, med `None` som standard. Er de
   satt, må de være endelige tall over null, og `hoey` kan ikke være under
   `lav`. Ellers `UgyldigKursrad`, som for de andre feltene.
2. **Adapteren** leser `high` og `low`. Mangler feltet, er det `null`, ikke et
   tall, ikke endelig eller ikke over null, blir det `None`. Er høy under lav,
   blir begge `None`, fordi det ikke kan avgjøres hvilken som er feil. Resten
   av raden leses som før, så hentingen ikke stopper.
3. **Migrasjonen** `0015_hoey_lav.sql` legger til `hoey REAL` og `lav REAL` i
   `kurs` og `indeks`, med `ADD COLUMN` som i 0014, og en `CHECK` som sier det
   samme som `Kursrad`. Radene som finnes, får `NULL`, til neste henting bytter
   ut serien. Hovedindeksen lagres som `Kursrad`, som aksjene. Uten kolonnene i
   `indeks` ville `SqliteIndekslager` gitt en annen serie tilbake enn
   `MinneIndekslager`.
4. **Lageret** `SqliteKurslager` og `SqliteIndekslager` skriver og leser `hoey`
   og `lav`. Minnelagrene har dem alt gjennom `Kursrad`.
5. **En base én versjon bak.** Sjekken før kallene leser basen med
   `godta_en_versjon_bak` (story 2.8). Den kvelden 0015 er flettet, står basen
   på 14 og har ikke kolonnene. `SqliteKurslager` leser dem derfor bare når de
   finnes (`_hoey_lav`, som `_regnet` for 0014). `SqliteIndekslager` godtar
   ikke en base én versjon bak, så der er det bare for at de to skal være like.
   Sjekken leser `indeks` med egen SQL (`indeksen_mangler`). Uten det ville sjekken stoppet med
   «no such column: hoey». Det sto i docstringen til
   `test_siste_migrasjon_roerer_ikke_tabellene_sjekken_leser` i
   `tests/test_fetch_prices.py`: sjekken må vurderes på nytt når siste migrasjon
   endrer `kurs`. Testen vurderer nå 0015 som den vurderte 0014.
6. **Versjonen** er 15 der testene sa 14, med en Rettet-linje.

## Kveldsjobben og flettingen

Instruksjonen sier at kveldsjobben i kveld går med den nye koden hvis PR-en
flettes før kl. 22:10. Det stemmer ikke (regel 3). `start/kveldshenting.ps1`
flytter jobbens arbeidskopi til commiten `origin/main` hadde ved midnatt,
«så det som flettes en dag, ikke går samme kveld» (linje 8–9 og 130–131, svar 3
under story 2.3). Jobben i kveld går med koden fra 19.11 kl. 00:00, uansett når
2.10 flettes. Den nye koden går først i jobben 20.11, hvis 2.10 er flettet før
midnatt.

Det gir én fare: appen migrerer basen ved første forespørsel
(`_migrer_en_gang` i `src/app.py`). Startes den ekte versjonen fra hovedkopien
etter at main med 2.10 er hentet, står basen på 15 før jobben kl. 22:15, og
jobben kjører koden for 14. *Rettet etter gjennomgangen (BH1):* her sto at
jobben da stopper. Det er verre: sjekken før kallene får `RuntimeError`, som
hører til `BASEFEIL` (`fetch_prices.py:542`), og hentingen skriver «Henter
likevel» (`fetch_prices.py:1275–1281`). Kallene brukes og fila skrives, men
`skriv_til_basen` får feilen fra `migrer()`, og dagen får ingen kveldsvurdering
(AD-7). Dagen må leses inn senere og får da bare signalet i ettertid.

Det samme gjelder jobben 20.11, dagen for brukertest 2, hvis flettecommiten
kommer etter midnatt (BH2). Derfor:

- PR-en flettes når CI er grønn og ingen funn på middels står åpne, før
  kl. 22:10 hvis den rekker det, ellers mellom kl. 23:58 og midnatt. Etter
  flettingen sjekkes det med `git log --format=%cd` at flettecommiten har en
  dato før midnatt.
- Hovedkopien får ikke 2.10 før jobben i kveld er sjekket etter kl. 23:50.
  Føringen på main kommer etter det.
Vinduet sa fra til gruppen 19.11 mellom kl. 14:42 og 14:49 (`date` før og
etter), og fortsatte. Hovedkopien får ikke
2.10 før jobben er sjekket etter kl. 23:50, og føringen på main kommer etter det.

## Bygget 19.11

| Del | Commit |
|---|---|
| `Kursrad` med `hoey` og `lav`, valgfrie | `e96d7233` |
| Adapteren leser `high` og `low`, og en verdi som ikke kan brukes, blir `None` | `ca4176e3` |
| `0015_hoey_lav.sql`, lagrene, en base én versjon bak, og versjonen 15 i testene | `057cf1af` |
| Testene i `tests/test_hoey_lav_2_10.py` | `76aab27e` |
| Spinen (AD-16) og «Teknologi og nøkler» | `2949d63a` |

## Testene før

`tests/test_hoey_lav_2_10.py` ble kjørt mot koden på `d764b9e5`, i en egen
utsjekk i scratchpad: alle 65 feilet. På grenen besto de.

Fem tester i andre filer måtte følge med, fordi de låste det som er endret:
feltene i `Kursrad` (`test_kurslager.py`), raden fra adapteren
(`test_snapshotleser.py`), radene i `kurs` etter migreringen (`test_aksje.py`),
en `INSERT` uten kolonnenavn (`test_indeks.py`) og katalogen uten 0014
(`test_ettertid_2_17.py`). Hver har en Rettet-linje og sjekker det samme som før.

## Mutantene

Kjørt mot `tests/test_hoey_lav_2_10.py`. Alle ble fanget:

| Mutant | Feilet |
|---|---|
| M1: adapteren krever `high` og `low` (`rad["high"]`) | 5, også `test_hentingen_stopper_ikke_naar_hoey_eller_lav_mangler` |
| M2: adapteren slipper høy under lav gjennom | 2 |
| M3: lageret leser alltid kolonnene | 1, `test_en_base_en_versjon_bak_leses_av_sjekken` |
| M4: 0015 uten CHECK | 1, `test_basen_avviser_det_kursrad_avviser` |
| M5: lageret skriver ikke `hoey` | 3 |

## Bildene

Ingen bilder er nye. `--dokumentene` på grenen fant at avtrykkene bak bildene i
`tests/test_docker.py` var endret, fordi `src/kursdata.py` er med bak bildene.
Alle de 20 bildene ble tatt på nytt 19.11 av demoen på grenen, på port 8924 med
en ny demobase, med skriptet og jobblista fra 9.22. Alle 20 var like byte for
byte som dem i `docs/appen/`, så bare avtrykkene er regnet ut på nytt.

## Gjennomgangen 19.11

Én leser med Blind Hunter, Edge Case Hunter og Verification Gap, bare med
lesing, på `2949d63a`. 15 funn: 2 på middels og 13 lave.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| BH1 | middels | Spesifikasjonen sa at jobben stopper mot en base på 15. Den henter likevel, og dagen får ingen kveldsvurdering | Rettet: avsnittet sier hva som skjer |
| BH2 | middels | Faren gjelder også jobben 20.11 hvis flettecommiten kommer etter midnatt | Rettet: flettingen før midnatt, sjekket med `git log --format=%cd`, og hovedkopien får 2.10 først etter jobben i kveld |
| BH3 | lav | Docstringen i adapteren sa at ingen verdi sjekkes der, og at hvert felt som mangler, gir `KeyError` | Rettet |
| BH4 | lav | `SqliteIndekslager` godtar ikke en base én versjon bak, så reserven der nås ikke | Rettet: tre steder sier det |
| BH5 | lav | `docs/innlevering.md` sa 0001–0014 | Rettet: en Rettet-linje |
| BH6 | lav | `dagen_ferdig.py` og `fetch_prices.py:1588` leser indeksen uten å godta en base én versjon bak | Står: fra før 2.10, ufarlig (kode 2 og jobben går som før), og det samme ved hver migrasjon |
| ECH1 | lav | Oversikten leser ikke høy og lav, så `Kursrad`-ene derfra har `None` | Rettet: en kommentar ved `_KURSFELT` |
| ECH2 | lav | Et stort heltall i `slutt` gir `OverflowError` i sqlite3 | Står: fra før 2.10. Adapteren gjør høy og lav til `float` |
| ECH3 | lav | Høy og lav sjekkes ikke mot sluttkursen | Står: spørsmål 2 |
| ECH4 | lav | 0015 sa at CHECK-en sier det samme som `Kursrad`, men uendelig og NaN slipper gjennom der | Rettet: kommentaren sier det |
| VG1 | lav | Hentingen skrev aldri høy og lav til `indeks` i testen | Rettet |
| VG2 | lav | Ingen test for at høy og lav ikke endrer signalet | Rettet: samme vurdering for alle aksjene hver dag |
| VG3 | lav | Ingen test for første henting på en base på 14 | Rettet: `test_foerste_henting_paa_en_base_paa_14_fyller_dem` |
| VG4 | lav | Testen for siste migrasjon tok ikke med `indeks` | Rettet |
| VG5 | lav | Hull i parametrene | Rettet: `-inf`, `False`, `10**400`, og høy lik lav i adapteren |

Leseren fant at ingen kode i `src/` sammenligner `Kursrad`-er eller leser `kurs`
eller `indeks` med `SELECT *`, og at demoen og øyeblikksbildene gir det samme som
før, med `None` der feltene mangler.

## Spørsmål

1. Kveldsjobben i kveld går med koden fra midnatt, ikke med 2.10 (avsnittet
   «Kveldsjobben og flettingen»). Skal den nye hentingen gå allerede i kveld?
   Det krever at jobben startes på en annen måte, og det gjør ikke vinduet.
   *Forslag:* nei. 2.10 går i jobben 20.11, og høy og lav brukes ikke av noe
   brukertest 2 ser.
   *Svart 2026-11-19 kl. 18:51:* nei, som rådet anbefalte. Jobben 20.11 fyller
   dem inn. Det blir ingen ekstra henting og ingen API-kall utover kvotesjekken.
2. Skal høy og lav sjekkes mot sluttkursen, så en rad med lav over slutt eller
   høy under slutt får `None` (ECH3)? *Forslag:* ja, men først når aksjesiden
   viser dem (FR-203). Radene i testene har høy og lav som ikke følger
   sluttkursen, og det ville endret dem.
   *Svart 2026-11-19 kl. 18:47:* ja, nå, i story 2.19
   ([`spec-2-19-hoey-og-lav-mot-slutt.md`](spec-2-19-hoey-og-lav-mot-slutt.md)).
   Rådet anbefalte å vente til aksjesiden viser tallene. *Rettet 2026-11-19
   (story 2.19):* radene i testene har høy og lav rundt sluttkursen, og ingen
   test i andre filer måtte endres med 2.19.

## Flettet 19.11

CI var grønn i alle fire jobbene på head-en `cc77e36f` (run 44555722272): 6090 bestått og
99 hoppet over i jobben `pytest`. Ingen funn på middels eller høy grad sto åpne
(regel 25). PR #171 ble squash-flettet i `92862551` 19.11 kl. 16:40, låst til `cc77e36f`,
uten nytt ja. Flettecommiten har en dato før midnatt (`git log --format=%cd`), så
jobben 20.11 går med 2.10.

## Kveldsjobben 19.11

Sjekket 19.11 kl. 23:51 (`date`), etter kl. 23:50 som instruksjonen kl. 14:24 sa:
«OSE Signal kveldshenting» står som Ready med resultat 0 (Last Result), som
før. Siste kjøring var 19.11 kl. 23:45, og neste er 20.11 kl. 22:15, med koden
origin/main hadde ved midnatt, altså 2.10 og 2.19. Hovedkopien ble trukket
til `690fea4c` etter sjekken.

## Grenser

- Ingen API-kall utover kvotesjekken. `data/` og `_privat/` røres ikke, og den
  ekte versjonen startes ikke.
- Grenen bruker bare testbaser og rører aldri `data/db/ose.db` (regel 22).
  Den bygges i en egen worktree, fordi den har en ny migrasjon.
- Aksjesiden viser ikke høy og lav. Raden for FR-203 i PRD-en står som
  «senere».
- Signalberegningen bruker ikke høy og lav.
- Den planlagte oppgaven «Morgensjekk OSE Signal» endres ikke. Aldri to
  pytest samtidig. Pausene om kvelden gjelder.
