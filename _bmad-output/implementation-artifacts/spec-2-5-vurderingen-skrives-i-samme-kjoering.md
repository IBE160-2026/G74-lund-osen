---
title: 'Story 2.5: Vurderingen skrives i samme kjøring'
type: 'feature'
created: '2026-10-02'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'c5c42f101ef7c2041ebecebbf83226c45b70dde0'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-1b-basen-aapnes-ett-sted-og-hentingen-skriver-kursene-dit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-1c-vurderingen-lagrer-maalingene-bak-de-tre-sjekkene.md'
  - '{project-root}/CLAUDE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Hentingen skriver kursene til basen, men ingen vurdering. En vurdering kan ikke etterfylles (AD-7), så hver kjøring uten den mangler for alltid i historikken (FR-408).

**Approach:** Etter at kursene er skrevet, leser `kjoer` seriene tilbake fra basen og skriver én rad per aksje i universet med `SqliteVurderingslager`: en `Vurdering` regnet av den ene rene funksjonen `signalberegning.vurder`, eller en `Grunn` (punkt 24). Datoen regnes én gang fra øyeblikket.

## Boundaries & Constraints

**Always:**
- Rekkefølgen i `kjoer`: øyeblikket, `dato = innevaerende_boersdag(norsk_dato(oeyeblikk))` før filvakten og før første kall, filvakten, hentingen, fila, kursene, vurderingene, utskriften.
- Seriene til vurderingen leses tilbake med `SqliteKurslager.serie` etter at alle seriene er skrevet, bare for symbolene `skriv_til_basen` skrev i denne kjøringen.
- Én rad for hvert symbol i `AKSJEUNIVERS`, aldri ingen rad: `SYMBOL_FEILET` for et symbol i `resultat.feil` eller som basen avviste eller hoppet over; ellers `vurder(rader, dato)`.
- `vurder`: `KURS_IKKE_FRA_DAGEN` når `rader[-1].dato != dato`; `SIGNAL_IKKE_REGNET` når `beregn_signal` eller `Vurdering` reiser `ValueError` eller `ArithmeticError`; ellers `Vurdering` med `trend_avvik` = trend.maaling, `dagens_endring` = bevegelse.maaling, `standardavvik` = bevegelse.grense, `volumforhold` = interesse.maaling, `slutt` og `justert_slutt` fra siste rad.
- `kjoer(…, klokke=None)`: `main` gir `naa`. Uten klokke leses `oeyeblikk`. Klokka går til `SqliteVurderingslager`, og leses én gang før vurderingene: er `norsk_dato(klokke())` en annen dag enn øyeblikkets, stopper kjøringen, sier fra og avslutter med kode 1. En `ValueError` fra `skriv` midt i universet gir samme melding med antallet som alt er skrevet.
- Feiler basen, skrives ingen vurdering, meldingen sier at dagen ikke kan fylles inn etterpå, og kode 1.
- `--les-inn` skriver aldri vurdering (AD-7).
- Utskriften: antall vurderinger, dagen raden gjelder, antall med grunn og symbolene med grunnen. Ingen kurser og ingen målinger (regel 16).
- Ingen API-kall. `src/fetch_prices.py` kjøres ikke, heller ikke med `--les-inn`.

**Never:** Børsdagskontrollen og nekting før kl. 22 (2.3). Historikken (2.7). Indeksen (2.8). KI (Epic 10). Relevante meldinger i raden. Ingen egen commit på grenen for noe annet enn 2.5.

## Beslutninger (godkjent 02.10 kl. 10:29)

1. **A:** En dag børsen er stengt, gjelder raden inneværende børsdag (AD-7, 1.7). Finnes raden for den dagen fra før, står den, og utskriften sier det. Utskriften sier alltid hvilken dag raden gjelder.
2. **A:** `UtenforKalenderen` stopper kjøringen før første kall, med 0 kall brukt, og meldingen sier at de stengte dagene må føres inn for året (NFR-08).
3. **A:** `vurder()` ligger i `signalberegning.py` som en ren funksjon. Kjernen importerer porten `vurderingsdata`. Pila føres inn i spinen og diagrammet, og `test_konsumentene.py` låser den.
4. **A:** Hentingen kjøres for hånd mellom kl. 22 og midnatt til 2.3. README får én setning: kjøres hentingen før kursene er publisert, stopper filvakten kveldens kjøring, og dagen får ingen vurdering.
- **Tillegg:** kontrollregning med `vurder()` på det nyeste øyeblikksbildet, uten nett og uten basen. Bare antall og symboler.

## I/O & Edge-Case Matrix

| Scenario | Tilstand | Forventet |
|---|---|---|
| Vanlig børsdag | 15 serier med dagens kurs | 15 `Vurdering` |
| Symbol feilet i hentingen eller i basen | | rad med `symbol_feilet` |
| Nyeste kurs er fra dagen før | | rad med `kurs_ikke_fra_dagen` |
| For kort serie | under 51 dager | rad med `signal_ikke_regnet` |
| To kjøringer samme dag | fila finnes | andre stopper ved filvakten, 15 rader |
| Ny kjøring uten fil, et symbol feiler | vurdering finnes | vurderingen står (grunn skriver ikke over) |
| Stengt dag, raden finnes | lørdag, fredagens rad | raden står, utskriften sier det |
| Over midnatt | klokka på neste dag | stopp, melding, kode 1, ingen rad for neste dag |
| Basen feiler | | 0 vurderinger, melding, kode 1 |
| Utenfor kalenderen | 2027 | stopp før første kall, 0 kall |
| `--les-inn` | | 0 vurderinger |

</frozen-after-approval>

## Code Map

- `src/signalberegning.py` -- `beregn_signal` (l. 252), `Sjekk.maaling`/`grense`. Ny `vurder(rader, dato)`. Importerer `vurderingsdata` (port, løvnode).
- `src/fetch_prices.py` -- `kjoer` (l. 335), `skriv_til_basen` (l. 248, returnerer i dag `bool`), `les_inn` (l. 399), `main` (l. 444). Ny `skriv_vurderinger`.
- `src/lagring_sqlite.py` -- `SqliteVurderingslager(tilkobling, klokke)`, `skriv` gir `False` når en grunn ikke får skrive over. Endres ikke.
- `src/vurderingsdata.py`, `src/boersdag.py` -- endres ikke.
- `tests/test_fetch_prices.py` -- `falsk_serie` slutter 30.07, `serie_til(siste, dager)`, `stier`, `lager_i`, `antall_rader`. `test_foerste_henting_…` (l. 699) venter `vurdering == 0` og må få 15.
- `tests/test_signalberegning.py` -- tester for `vurder`. `tests/test_konsumentene.py` -- låser importen.
- `README.md` (l. 68–76), spinen (diagrammet l. 78–113, teksten l. 116–125, AD-17), `deferred-work.md` (midnatt, l. 40–42).

## Tasks & Acceptance

**Execution:**
- [x] `src/signalberegning.py` -- `vurder` -- den ene omformingen fra `Signal` til `Vurdering | Grunn`
- [x] `src/fetch_prices.py` -- dato før vakten, `skriv_til_basen` gir de skrevne symbolene, `skriv_vurderinger`, klokke og midnatt, `main` gir `naa` -- vurderingen i samme kjøring
- [x] Testene og mutantene i Verification
- [x] `README.md`, spinen, `deferred-work.md` -- regel 19 og pila

**Acceptance Criteria:**
- Given en falsk kilde og en base på disk, when `kjoer` går, then `Vurderingslager.les` gir 15 rader, og målingene er lik `beregn_signal` av serien i basen.
- Given en base med en eldre serie, when `kjoer` går, then vurderingen er regnet av den nye.
- Given en klokke som går over midnatt, when vurderingene skal skrives, then kjøringen stopper med kode 1 og ingen rad for neste dag.

## Implementation Notes

- Bygget 02.10 direkte i økta, ikke av en egen implementasjonsagent: planen og kildene var alt lest, og koden er liten.
- `vurder(rader, dato, p=STANDARD)` i `signalberegning.py`. Tom serie gir `KURS_IKKE_FRA_DAGEN`. `beregn_signal` og `Vurdering` ligger i samme `try`, så en verdi porten avviser, gir `SIGNAL_IKKE_REGNET`.
- `skriv_til_basen` gir `set[str] | None`. `les_inn` regner «alt skrevet» som `skrevne == set(serier)`.
- `kjoer(…, klokke=None)`: uten klokke leses `oeyeblikk`, så de om lag 20 testkallene som finnes, står uendret. `main` gir `klokke=naa`.
- Klokka leses én gang i `kjoer` før vurderingene (`norsk_dato(klokke()) != dag`), og lageret leser den ved hver `skriv`. Sjekken i `kjoer` stopper også fredag → lørdag, som lageret ville godtatt.
- `skriv_vurderinger` fanger `ValueError` fra `skriv` som midnatt. Andre `ValueError` kan ikke nås der: symbolene kommer fra `AKSJEUNIVERS`, og datoen er en `date`.
- Utskriften: «Skrev N rader i vurdering for børsdagen D[ (børsen er stengt X)]: A vurderinger og B med grunn.», «Med grunn: SYM (grunn), …» og «Raden for D sto fra før og er ikke skrevet over: …».
- G11 (`SqliteVurderingslager.skriv` slipper ut `sqlite3`-feil) er løst i kalleren: `skriv_vurderinger` fanger `BASEFEIL`.
- Spinen: pilene `signal --> vurdering`, `fetch --> signal` og `fetch --> vurdering`, og de manglende `fetch --> sqlite` og `fetch --> boersdag`. «Bygget»-linje ved AD-17.
- Tester: før 1031 passed og 16 skipped lokalt (1047 i CI på main), etter 1058 passed og 16 skipped. 19 nye i `tests/test_fetch_prices.py`, 7 i `tests/test_signalberegning.py` og 1 i `tests/test_konsumentene.py`. Én test endret: `test_foerste_henting_…` venter 15 vurderinger.
- Kontrollregningen, uten nett og uten basen, på `kurser-raa-2026-10-01.json` med dato 2026-10-01: 15 av 15 gir en `Vurdering`, ingen grunn.
- Mutantene, én om gangen, hele `tests/` hver gang, satt tilbake fra en kopi i scratchpad med sha256 sjekket: M1 2 feilet, M2 12, M3 4, M4 2, M5 4, M6 2, M7 1, M8a 2, M8b 1, M9 2, M10 1, M11 1, M12 1, M13 1. Etter gjennomgangen: M14 1, M15 1, M16 1. Alle fanget. M8 er delt i to: a) sjekken før vurderingene fjernet, b) `ValueError` fra `skriv` fanges ikke.

## Spec Change Log

## Review Triage Log

Gjennomgang 1 (02.10), Blind Hunter (BH), Edge Case Hunter (ECH) og Verification Gap (VG).

| # | Funn | Dom | Grunnlag | Rute |
|---|---|---|---|---|
| BH1 | «Kan ikke fylles inn etterpå» stemmer ikke når neste dag er stengt | low | En kjøring lørdag skriver fredagens rad når den mangler (K11) | patch: meldingene sier at raden kan skrives så lenge datoen er inneværende børsdag |
| BH2 | «Aldri ingen rad» lover for mye | low | Midnatt og feil i basen gir færre enn 15 (K7, K10) | patch: docstringen og spinen gjelder en kjøring som fullfører |
| BH3, VG1 | `except BASEFEIL` i `skriv_vurderinger` (G11) har ingen test | medium | Ingen test lot basen feile etter kursene. Mutantene M14–M16 overlevde ikke etter rettingen | patch: to tester |
| BH4 | G11 står som «vent» i `kodegjennomgang-epic-1.md` | low | Linje 56 og 64 | patch: merknad som for G12 |
| BH5 | `sprint-status.yaml` står på in-progress | false | 2-5 settes til review etter flettingen, slik planen sier | avvist |
| BH6 | README nevner ikke stopp i 2027 eller stengt dag | low | Ny atferd README-en burde nevne (regel 19). «Dagen får ingen vurdering» er setningen fra svar 4, og en rad med grunn er ingen vurdering | patch: én setning til |
| BH7 | Feil i hentingen gir kode 0, avvisning i basen kode 1 | low | Slik siden 2.1b. 2.5 endrer ikke kodene | avvist: fra før |
| BH8 | Testene viser til M8, ikke M8a/M8b | low | Kosmetisk, men sporingen til mutantene | patch: docstringene |
| BH9 | K1: `len(rader) == 15` kan ikke feile, og `styrke > 0` sjekker bare siste | low | Riktig | patch: antall fra basen, styrke i løkka |
| BH10 | Regel 16-testen fanger bare `str()` | low | En avrundet kurs i utskriften er lite sannsynlig, og testen er som i 2.1b | avvist |
| BH11 | K7 avhenger av hvor ofte klokka leses | low | Riktig | patch: antagelsen står i docstringen |
| BH12 | Hver `ValueError` fra `skriv` meldes som midnatt | low | Andre kan ikke nås fra `AKSJEUNIVERS` med en `date`. `UtenforKalenderen` ved nyttår er også midnatt | patch: meldingen tar med teksten fra lageret |
| ECH1 | Meldingen om kalenderen kan nevne feil år | low | Når dagen er dekket, men oppslaget går til året før | patch: feilteksten fra `boersdag` nevner dagen, meldingen nevner ikke året |
| ECH2 | Fredag til lørdag midt i universet skriver videre | false | Fredagen er fortsatt inneværende børsdag, og radene gjelder fredagens kurser. AD-7 tillater det | avvist |
| ECH3 | `UgyldigKursrad` fra `serie` midt i universet | false | Radene i basen er skrevet gjennom `Kursrad` og `kontroller_skriving`, og `0001` har samme kontroller | avvist |
| ECH4 | `TypeError` fra `beregn_signal` slipper ut av `vurder` | false | Alle verdiene kommer fra `Kursrad`, som avviser feil type | avvist |
| ECH5 | Utenfor kalenderen gir kode 1 også når dagens fil finnes | false | Svar 2: stopper før første kall. Ingen fil kan finnes for en dag i 2027 før kalenderen er ført inn | avvist |
| VG-annet | `ArithmeticError` i `vurder` er ikke dekket | low | `Kursrad` avviser kurs ≤ 0, så delingen kan ikke treffe 0. Forsvar, ikke et hull | avvist |

## Verification

**Commands:**
- `uv run pytest -q` -- grønn. Før: 1047 i CI på main, kjøring 36932258136 (1031 passed og 16 skipped lokalt).

**Mutantene**, én om gangen, koden satt tilbake fra en kopi i scratchpad, ikke med `git checkout`:
1. `standardavvik` og `dagens_endring` byttet om. 2. Vurderingen regnes før kursene er skrevet. 3. Et feilet symbol gir ingen rad. 4. Datokontrollen i `vurder` fjernet. 5. `ValueError` fanges ikke i `vurder`. 6. `WHERE`-leddet i `_UPSERT` fjernet. 7. Datoen leses på nytt for hvert symbol. 8. Midnattsjekken fjernet. 9. `les_inn` skriver vurderinger. 10. `slutt` i utskriften. 11. Vurderingene skrives når basen har feilet. 12. Raden for en stengt dag skrives over. 13. Datoen regnes etter kallene. *Lagt til etter gjennomgangen:* 14. `sqlite3`-feilen i vurderingene slipper ut. 15. Feil i basen midt i vurderingene gir kode 0. 16. Basen som ikke åpnes for vurderingene, gir kode 0.
