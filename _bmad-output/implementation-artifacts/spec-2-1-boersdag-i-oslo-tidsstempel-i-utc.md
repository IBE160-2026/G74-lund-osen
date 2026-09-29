---
title: 'Story 2.1: Børsdag i Oslo, tidsstempel i UTC'
type: 'bugfix'
created: '2026-09-29'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: ''
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `fetch_prices.main` gir fila navn etter `date.today()` (maskinens dato) og stempler `hentet` med `datetime.now(timezone.utc)` etter hentingen. Mellom midnatt og 02:00 norsk tid peker de på hver sin dag, og ingen av dem sier at dagen er Oslos (AD-20). `meldinger._minutt` kutter `tidspunkt[:16]`, så `…08:30:00Z` og `…08:30:00+02:00` blir samme nøkkel, mens `…06:30:00Z` og `…08:30:00+02:00`, som er samme øyeblikk, blir to.

**Approach:** `main` leser klokka én gang, i UTC. `kjoer` tar dette øyeblikket i stedet for en dato og utleder alt av det: dagen med `boersdag.norsk_dato` (filnavn, vakten og `to` i intervallet) og `hentet` som øyeblikket i UTC med offset. `_minutt` parser med `datetime.fromisoformat`, krever offset, regner om til UTC og kutter sekunder.

## Boundaries & Constraints

**Always:**
- Øyeblikket tas før vakten mot en fil som finnes, og `hentet` er dette øyeblikket. `hentet` blir altså tidspunktet da kjøringen startet, ikke da siste kall var ferdig (se Design Notes).
- Ingen kode i `fetch_prices.py` eller `meldinger.py` leser maskinens lokale sone: ingen `date.today()`, ingen `datetime.now()` uten sone, ingen `astimezone()` uten argument.
- Formatet i øyeblikksbildet er uendret: samme felter, `hentet` som `isoformat()` med `+00:00`.
- Regel 6: ingen nett i testene (AD-8). Ingen API-kall, og `src/fetch_prices.py` kjøres ikke.

**Never:**
- Ikke forventet børsdag (2.3) eller datoen for vurderingen (2.5). 2.1 lager øyeblikket de skal bygge på.
- Ikke flytting til `data/raa/` (2.1b).
- Ingen endring i formatet av `feil`, i `hent_universet` eller i `hent_ett_symbol`.

## Beslutninger

- **`kjoer(data_katalog, oeyeblikk, api_nokkel, hent, skriv)`:** `i_dag: date` byttes med `oeyeblikk: datetime`. Et øyeblikk uten sone gir `ValueError` fra `norsk_dato`, før vakten og før noe kall.
- **`filnavn` og `bygg_intervall`** mister standardverdien `date.today()` og krever datoen. Ingen annen kode kaller dem uten.
- **Klokka i `main`:** en modulfunksjon `naa()` som gir `datetime.now(timezone.utc)`, samme mønster som klokka `SqliteVurderingslager` tar. Testen bytter den ut med `monkeypatch`.
- **`_minutt` uten sone:** `ValueError`, ikke en gjetning på UTC eller Oslo. NewsWeb gir `publishedTime` med `Z` (formen er sjekket lokalt i rådataene fra 21.09, ingen verdier er ført). `_minutt` returnerer et `datetime`, og nøkkelen i `dedupliser` blir `tuple[str, str, datetime]`.
- **Meldingsdelen tas med her.** Rettingen er om lag ti linjer i `_minutt` og nye tidsstempler i fem eksisterende tester, altså en liten retting, ikke en sak for Epic 6.
- **Maskinen i UTC (svar A, 29.09 kl. 11:17):** TZ-testene setter `TZ` og kaller `time.tzset()`, og hoppes over der den mangler (Windows). I tillegg en strengvakt som leter i hele `src/` etter `date.today(`, `datetime.now()` uten argument og `astimezone()` uten argument. `datetime.now(timezone.utc)`, som i `migrering.py`, er lov. M6 prøves lokalt mot strengvakten. TZ-testene kjøres bare i CI: før flettingen skal CI-kjøringen på PR-en være grønn, og rapporten sier kjørings-ID, antall passed og at ingen TZ-test ble hoppet over der.
- **Spesifikasjonen holdes samlet** (29.09), selv om den er over 1600 tokens.

## I/O & Edge-Case Matrix

| Scenario | Øyeblikk (UTC) | Filnavn | `hentet` |
|---|---|---|---|
| 00:30 norsk sommertid | 2026-09-24 22:30 | `kurser-raa-2026-09-25.json` | `2026-09-24T22:30:00+00:00` |
| Like før midnatt | 2026-09-24 21:59:59 | `…-2026-09-24.json` | `2026-09-24T21:59:59+00:00` |
| Like etter midnatt | 2026-09-24 22:00:00 | `…-2026-09-25.json` | `2026-09-24T22:00:00+00:00` |
| 00:30 siste sommertidsdag | 2026-10-24 22:30 | `…-2026-10-25.json` | `2026-10-24T22:30:00+00:00` |
| 02:30 to ganger 25.10 | 00:30 og 01:30 den 25.10 | begge `…-2026-10-25.json` | hver sin |
| Midnatt i vintertid | 2026-10-25 22:59:59 / 23:00:00 | `…-10-25` / `…-10-26` | uendret UTC |
| Øyeblikk uten sone | `datetime(2026, 9, 25, 0, 30)` | ingen fil, ingen kall | `ValueError` |
| `_minutt`: samme øyeblikk | `…T06:30:00Z` og `…T08:30:00+02:00` | — | én dublett |
| `_minutt`: samme tekst, ulikt øyeblikk | `…T08:30:00Z` og `…T08:30:00+02:00` | — | ikke dublett |
| `_minutt`: millisekunder | `…T06:30:00.123Z` og `…T06:30:41Z` | — | én dublett |
| `_minutt` uten sone | `…T08:30:00` | — | `ValueError` |

</frozen-after-approval>

## Code Map

- `src/fetch_prices.py:62–65` `bygg_intervall` -- standardverdi `date.today()` fjernes.
- `src/fetch_prices.py:185–192` `filnavn` -- standardverdi `date.today()` fjernes.
- `src/fetch_prices.py:195–243` `kjoer` -- tar `oeyeblikk`; `dag = norsk_dato(oeyeblikk)` før vakten; `naa` på linje 227 (etter hentingen) erstattes av øyeblikket i UTC.
- `src/fetch_prices.py:246–247` `main` -- `kjoer(DATA_KATALOG, naa(), hent_api_nokkel())`.
- `src/boersdag.py:93` `norsk_dato` -- gjenbrukes, endres ikke.
- `src/meldinger.py:110–117` `_minutt`, `:186–213` `dedupliser` -- nøkkeltypen.
- `src/lagring_sqlite.py:177–192` -- mønsteret for en klokke som tas inn.
- `tests/test_fetch_prices.py` -- seks kall til `kjoer` med en `date` (linje 148, 169, 185, 225, 241, 419) får et øyeblikk. `TestSkriverIkkeOver.DAG` får et øyeblikk ved siden av.
- `tests/test_meldinger.py:30, 69–70, 88–89` -- tidsstemplene får `Z`, fordi `_minutt` nå avviser et tidsstempel uten sone. Hva testene sjekker, er uendret.
- Urørt: `tests/test_lagring_fil.py:104` og `test_intervall` gir allerede datoen; `tests/test_snapshotleser.py:300` viser formen `hentet` fortsatt har.

## Tasks & Acceptance

**Execution:**
- [ ] `src/fetch_prices.py` -- øyeblikket, `naa()`, `kjoer`, `main`, ingen `date.today()`; docstringene sier at `hentet` er starten.
- [ ] `tests/test_fetch_prices.py` -- de seks kallene; matrisen over som parametrisert test av `kjoer`; samme sett med `TZ=UTC` og `TZ=Pacific/Auckland` (hoppes over uten `tzset`); `naa()` gir sone med offset 0; G12.
- [ ] `src/meldinger.py` -- `_minutt` via `fromisoformat`.
- [ ] `tests/test_meldinger.py` -- `Z` i fem tidsstempler; de fire meldingsradene i matrisen.
- [ ] `tests/test_tidssone.py` -- strengvakten over hele `src/` (svar A).
- [ ] Spinen, AD-20 -- en linje «Bygget 2026-09-.., story 2.1» (dato fra klokka).
- [ ] `kodegjennomgang-epic-1.md` -- merknad ved G12: raden sier «tas i 2.3», men epics.md la den til 2.1 27.09. Tatt i 2.1.

**Acceptance Criteria (kontrollpunktene i epics.md, hvert med en mutant, én om gangen, satt tilbake fra kopi):**
- K1 Filnavn og `hentet` fra samme øyeblikk: gitt et fast øyeblikk, så er `norsk_dato(fromisoformat(hentet))` datoen i filnavnet og `hentet` lik øyeblikket. *Mutant M1:* `hentet` leses fra klokka etter hentingen.
- K2 00:30 norsk tid: filnavn og `hentet` peker på 25.09. *M2:* `dag = oeyeblikk.date()` (UTC-dagen).
- K3/K4 `_minutt` via tidsobjekt, samme øyeblikk gir samme nøkkel. *M3:* `[:16]` tilbake i `_minutt`. *M4:* `_minutt` godtar tidsstempel uten sone.
- K5 G12: gitt falsk nøkkel (`EODHD_API_KEY` satt, `load_dotenv` byttet ut), falsk `requests.get`, `DATA_KATALOG` i `tmp_path` og `naa()` 2026-09-24 22:30 UTC, når `main()` kjøres, så finnes `kurser-raa-2026-09-25.json` med 15 serier, uten nøkkelen. *M5:* `date.today()` tilbake i `main`.
- K6 «Ville feilet hvis» sonen ikke var sagt: *M6:* `dag = oeyeblikk.astimezone().date()` (maskinens sone), fanget av strengvakten lokalt og av TZ-testene i CI. *M7:* `hentet` i Oslo-tid (`+02:00`), fanget av K1.

## Design Notes

**`hentet` blir starten på kjøringen.** I dag stemples fila etter at de 15 kallene er ferdige. Med ett øyeblikk før vakten blir `hentet` tidspunktet da kjøringen startet, typisk noen sekunder tidligere, i verste fall inntil 15 × 60 s (tidsavbruddet) tidligere. Det betyr: (1) Filnavn og `hentet` kan aldri havne på hver sin dag, heller ikke når kjøringen går over midnatt. Den tilhører dagen den startet. (2) `sist_hentet` i visningen viser når hentingen begynte. Dataene kan være inntil én kjøretid nyere enn stempelet, aldri eldre. (3) 2.1b kan gi `erstatt_serie` samme `hentet`. (4) Det som betyr noe for 2.3 og 2.5, er Oslo-dagen, og den er den samme for fila og stempelet.

**Antall tester:** før 875. Etter om lag 875 + 7 (matrisen for `kjoer`) + 14 (samme med to soner) + 2 (`naa`, G12) + 4 (meldinger) + 1 (strengvakten) ≈ 903. På Windows hoppes de 14 over. Nøyaktige tall føres i commit-meldingen, både lokalt og i CI.

**Én økt:** ja.

## Verification

**Commands:**
- `uv run pytest -q` -- lokalt: alle grønne, TZ-testene hoppet over; i CI på PR-en: alle grønne, ingen hoppet over.
- `grep -rn "date.today(\|datetime.now()\|astimezone()" src/` -- ingen treff.
- CI på PR-en -- grønn, ingen TZ-test hoppet over; kjørings-ID og antall passed i rapporten.

## Implementation Notes

## Spec Change Log

## Review Triage Log
