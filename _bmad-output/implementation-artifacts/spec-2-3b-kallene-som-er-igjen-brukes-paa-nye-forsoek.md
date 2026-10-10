---
title: 'Story 2.3b: Kallene som er igjen, brukes på nye forsøk'
type: 'feature'
created: '2026-10-10'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '8905b5d4a2d601fa80eee9e362080244fae6c89d'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-3-boersdagskontroll-foer-kvoten-brukes.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Når kveldens fil finnes, stopper hentingen ved filvakten med 0 kall, også når basen mangler dagens kurs for noen aksjer. Kallene som er igjen av dagens 20, blir ubrukt, og dagen får en grunn i stedet for en vurdering for de aksjene (FR-402, NFR-01). Et symbol som feiler, gir dessuten kode 0, mens et svar uten dagens kurs gir kode 1 (ECH1 i 2.3).

**Approach:** Finnes kveldens fil, og basen mangler dagens kurs for noen aksjer, gjør samme kommando et nytt forsøk: den henter bare de aksjene, eldste først, med det som er igjen av dagens kall, aldri bonuskvoten. Forsøket lagres i en egen fil, og en vurdering som lykkes, skriver over grunnen samme børsdag (AD-7). Har basen alle kursene, men mangler vurderinger, skrives de med 0 kall (ECH8).

## Planen

Planen er vist i chatten 10.10 og ført i `docs/ai-prompts/2026-10-10.md` (instruksjonen kl. 19:07 og Utført-linjen). Gruppen sa ja kl. 19:32 med disse svarene, som er beslutninger:

1. **Fila for et nytt forsøk** heter `forsoek<n>-raa-<dato>.json`, med n fra 2: første n som ikke finnes. Den åpnes med modus `"x"`. `kurser-raa-<dato>.json` skrives aldri om (AD-6).
2. **Én runde per kjøring**, eldste først. Gjentakelsen av kommandoen gir «rundt igjen».
3. **En dag børsen er stengt**, står en rad som finnes fra før, som beslutning 1 i spesifikasjonen til 2.5 (02.10 kl. 10:29). Kursene skrives, men grunnen blir stående.
4. **Ingen nye kall etter kl. 23:50** i Oslo.
5. **Kode 1** når en aksje mangler dagens kurs etter kjøringen, også når den feilet (ECH1). Hver eldre test som endres, står i spesifikasjonen med grunnen, og bare koden den venter, endres.
6. **ECH8 tas i 2.3b:** vurderingene som mangler når basen har kursene, skrives med 0 kall.
7. **Flettes tidligst etter at hentingen mandag 12.10 er gjort og kontrollert.** README-prøven fører commiten den brukte.

I tillegg, fra instruksjonen kl. 19:32: Oppgaveplanlegging blir et eget steg etter README-prøven, med egen plan. 2.3b skriver ingen oppskrift for Oppgaveplanlegging, og kontrollpunktet om jobben hver halvtime er flyttet dit. README-en får bare det 2.3b endrer: setningen om dager børsen er stengt, og at samme kommando kjørt igjen senere samme kveld prøver aksjene som mangler. Ingen ny kommando, så tabellen i §9 står, og §9 får en datert linje om teksten som er endret.

## Boundaries & Constraints

**Always:**
- Rekkefølgen før første kall er som i 2.3: demovakten, klokka, tidskontrollen, basen, filvakten, nøkkelen og kvoten. Demovakten kommer fortsatt før alt annet (3.4).
- Et nytt forsøk skjer bare når `kurser-raa-<dato>.json` finnes og basen kan leses og mangler dagens kurs for minst én aksje i lista. Kan basen ikke leses, stopper filvakten som før, med 0 kall og kode 1.
- Bare aksjene som mangler kursen for børsdagen i basen, hentes. Rekkefølgen er eldste `kursserie.hentet` først, en aksje uten serie først av alle, og ellers rekkefølgen i lista.
- Kallene til nye forsøk er det minste av kall igjen av dagens (`/api/user`) og `dailyRateLimit` minus antallet aksjer i lista og indeksen. Lista og indeksen gis som ett antall av den som kaller. I dag er det 15, og 20 − 15 = 5. Med 18 aksjer og indeksen er det 1.
- Bonuskvoten brukes aldri. `/api/user` leses før første kall og etter hvert kall. Står `extraLimit` lavere enn før første kall, eller kan svaret ikke leses etter et kall, stopper forsøket. Kan kvoten ikke leses før første kall, blir det 0 kall og kode 1. Avviser `/api/user` nøkkelen (401, 403), stopper forsøket med kode 1, som i 2.3.
- Ingen nye kall etter kl. 23:50 i Oslo, og heller ikke etter midnatt i Oslo.
- Forsøket lagres i `forsoek<n>-raa-<dato>.json` før basen, med samme form som kursfila og `hentet` fra øyeblikket forsøket startet (AD-6, AD-20). Fila skrives også når alle kallene feilet.
- Kursene går til basen gjennom `skriv_til_basen`, og vurderingene bare for aksjene forsøket fikk skrevet. Et forsøk som feiler igjen, rører ikke raden. En vurdering skriver over en grunn, en grunn aldri over en vurdering (`_UPSERT`, uendret). En dag børsen er stengt, står en rad som finnes (svar 3).
- Kode 1 når en aksje i lista mangler kursen for børsdagen etter kjøringen, både etter hovedhentingen og etter et nytt forsøk.
- ECH8: har basen kursen for børsdagen for alle aksjene, men noen mangler en rad i `vurdering` for dagen, skrives radene som mangler, med 0 kall. Rader som finnes, røres ikke.
- Ny kode tar lista som parameter, med `AKSJEUNIVERS` som standard (`AD-21`, føringen 30.09), og prøves med en liste på 18.
- Utskriften har ingen kurser (regel 16) og aldri nøkkelen.

**Ask First:** endringer i `src/lagring_sqlite.py`, i `boersdag.py` eller i skjemaet.

**Never:** Oppgaveplanlegging og arbeidskopien jobben kjører fra (eget steg). Indekskallet (2.8). Bonuskvoten. En ny kommando eller et nytt flagg. Endring av `kurser-raa-<dato>.json` eller navnet på den.

## I/O & Edge-Case Matrix

| Scenario | Tilstand | Forventet |
|---|---|---|
| Kveldens fil finnes, 2 av 15 mangler dagens kurs | 0 brukt av 20 | 2 kall, eldste først, `forsoek2-raa-<dato>.json`, 2 vurderinger over grunn, kode 0 |
| Som over, en av de 2 feiler igjen | | 2 kall, raden til den som feilet står, kode 1 |
| 6 mangler, 15 brukt av 20 | | 5 kall, de 5 eldste, kode 1 |
| Alle 20 brukt | | 0 kall, kode 1, sier at bonuskvoten ikke brukes |
| `extraLimit` synker etter første kall | | stopper etter det kallet, kode 1 |
| Kvoten kan ikke leses | | 0 kall, kode 1 |
| `forsoek2` finnes | | `forsoek3-raa-<dato>.json` |
| Klokka 23:50 | | 0 kall, kode 1 |
| Lørdag, fredagens fil, en aksje mangler fredag | rad med grunn for fredag | kursen skrives, raden står (svar 3) |
| Basen har alle kursene, 3 rader mangler | | 3 rader, 0 kall, kode 0 |
| Hovedhentingen, ett symbol feiler | | kode 1 (ECH1), og utskriften nevner det |
| Demobase | | stopp før alt annet, 0 kall, kode 1 |
| Liste med 18 og indeksen | 0 brukt | 1 kall til nye forsøk |

</frozen-after-approval>

## Code Map

- `src/fetch_prices.py`:
  - `kjoer`: filvakten (`fil.exists()`) går til `nytt_forsoek` når basen mangler aksjer; basesjekken får ECH8; slutten gir kode 1 for alle aksjer uten dagens kurs (ECH1). Ny parameter `lista`.
  - `tolk_kvote`: deles, så grensen også kan leses (`les_kvotetall`). `tolk_kvote` gir det samme som før.
  - Nye: `kall_til_nye_forsoek`, `forsoeksfil`, `eldste_foerst`, `manglende_vurderinger`, `nytt_forsoek`.
  - `hent_universet`, `manglende_i_basen`, `skriv_til_basen`, `skriv_vurderinger`: lista som parameter. `skriv_vurderinger` får `bare`, aksjene som skal få rad.
  - Tekstene «Et nytt forsoek ... kommer med story 2.3b» byttes.
- `src/lagring_sqlite.py`: uendret. `_UPSERT` bærer AD-7, og `SqliteKurslager` og `SqliteVurderingslager` tar lista allerede (3.4).
- `tests/test_fetch_prices.py`: nye tester i egne klasser. Eldre tester som endres, står i Implementation Notes.
- `README.md`, «Når du henter» og `docs/kvalitetssikring.md` §9: én commit.

## Tasks & Acceptance

**Execution:**
- [ ] `src/fetch_prices.py` -- lista som parameter, `les_kvotetall`, `kall_til_nye_forsoek`, `forsoeksfil`, og ECH1 med de eldre testene.
- [ ] `src/fetch_prices.py` -- `nytt_forsoek` og filvakten, med testene.
- [ ] `src/fetch_prices.py` -- ECH8, med testene.
- [ ] `README.md` og `docs/kvalitetssikring.md` §9.
- [ ] Gjennomgangen, mutantene, spinen hvis noe der ikke stemmer.

**Acceptance Criteria:**
- Given kveldens fil og en base som mangler dagens kurs for noen aksjer, when kommandoen kjøres igjen, then hentes bare de, eldste først, innenfor kallene som er igjen av dagens, og aldri fra bonuskvoten.
- Given et forsøk som lykkes for en aksje med grunn, when vurderingene skrives, then står vurderingen for børsdagen, og en vurdering som fantes, står.
- Given kveldens fil, when et forsøk lagres, then er `kurser-raa-<dato>.json` byte for byte uendret, og forsøket står i `forsoek<n>-raa-<dato>.json`.
- Given en aksje som mangler dagens kurs etter kjøringen, when kjøringen er ferdig, then er koden 1.
- Given en base med alle kursene og rader som mangler, when kommandoen kjøres, then skrives radene med 0 kall.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest` -- før: 1269 passed og 16 skipped lokalt, 1285 i CI.
