---
title: 'Story 2.10: høy og lav lagres med kursene'
type: 'feature'
created: '2026-11-19'
status: 'in-progress'
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
   på 14 og har ikke kolonnene. Lagrene leser dem derfor bare når de finnes
   (`_hoey_lav`, som `_regnet` for 0014). Uten det ville sjekken stoppet med
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
etter at main med 2.10 er hentet, står basen på 15 før jobben kl. 22:15. Da
stopper jobben med «Basen er nyere enn koden», fordi den kjører koden for 14.
Vinduet sa fra til gruppen 19.11 mellom kl. 14:42 og 14:49 (`date` før og
etter), og fortsatte. Hovedkopien får ikke
2.10 før jobben er sjekket etter kl. 23:50, og føringen på main kommer etter det.

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
