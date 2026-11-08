---
title: 'Story 2.11: Lista leses fra basen'
type: 'feature'
created: '2026-11-08'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '907393d6'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/_bmad-output/planning-artifacts/designutdrag-2026-11-08.md'
---

Skrevet 08.11 i instruksjonen kl. 14:05 (`docs/ai-prompts/2026-11-08.md`). Gruppen har sagt at Claude Code bygger etter forslagene i spesifikasjonene, og at de gås gjennom før flettingen (svaret 08.11 kl. 12:32). Storyen bygges etter forslagene under, og spørsmålene står åpne til gruppen har svart. 2.12 bygger på grenen for denne.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Når kom de 15 inn i lista?** Storyen sier «datoen for den første raden sin». *Forslag:* den første raden i `vurdering`, fordi det er dagen appen begynte å følge aksjen. Kursene går et år lenger tilbake, fordi første henting henter historikken. En aksje uten rad i `vurdering` får ingen dato (`NULL`), som betyr at den er med fra første henting.
2. **Hva betyr `ut`?** *Forslag:* den første dagen aksjen ikke er i lista. Hentingen dagen før er den siste for aksjen. En aksje med `ut` står ikke i oversikten, Min liste eller børsometeret, men aksjesiden viser den med historikken.
3. **Hva står for en dag etter at aksjen gikk ut?** *Forslag:* «ikke i lista», en egen tilstand (`Art.IKKE_I_LISTA` i `tilstand.py`), og ikke «ikke vurdert». Det gjelder en dag uten rad fra og med `ut`.
4. **Hvem setter `inn` og `ut`?** *Forslag:* ingen side i 2.11. Lista byttes i 2.12, som skriver ønsket i en egen tabell, og hentekommandoen tar det i bruk (AD-3). I 2.11 leser hentingen og sidene lista fra basen, og testene setter datoene direkte.
5. **Bransjen.** *Forslag:* en trigger i basen avviser en aksje med en bransje som ikke er blant de 13 i `designregler.md` §4, ved `INSERT` og ved `UPDATE OF sektor`, så den ikke kan komme inn uten.

## Intent

**Problem:** lista er `AKSJEUNIVERS` i koden. For at brukeren skal kunne bytte aksjer (2.12), må hentingen og sidene lese den fra basen.

**Avgjørelsene:** story 2.11 i `epics.md` (08.10 og tillegget 13.10 om bransjen), svaret 08.11 kl. 11:41 og 11:43 (bygges i dag, opptil 18) og kl. 11:57 (prøvekjøringer på `ose.db` med `mode=ro`, her en kopi i en midlertidig mappe).

## Slått opp 08.11 på `907393d6` (regel 3)

- `aksje` har `symbol`, `ticker`, `navn` og `sektor` (`0003_aksje.sql`), og triggere hindrer at en aksje med rader slettes. Siste migrasjon er `0008_omsetning.sql`.
- Hentekommandoen tar `lista` som parameter med `AKSJEUNIVERS` som standard (`fetch_prices.py`), og kvoten regnes av `len(lista) + 1`.
- Oversikten leser alle radene i `aksje` (`_OVERSIKT` i `lagring_sqlite.py`), i rowid-rekkefølge.
- `tilstand()` gir `IKKE_KJOERT` for en børsdag uten rad (`tilstand.py`), og `les_tilstand` i `markedsoversikt.py` gjør den om til «ikke vurdert».
- `tests/test_aksje.py` holder `aksje` lik `AKSJEUNIVERS` felt for felt.
- De 13 bransjene står i `designregler.md` §4 og i `BRANSJER` i `boersometer.py`.

## Delene

### A) Migrasjonen `0009_lista.sql`

`aksje` får `inn` og `ut` (dato som tekst, eller `NULL`), med `CHECK (ut IS NULL OR inn IS NULL OR inn < ut)`. De 15 får `inn` fra spørsmål 1. To triggere avviser en bransje utenfor de 13 (spørsmål 5). Ingen tabell eller trigger som finnes, endres.

**Ville feilet hvis:** en aksje kunne komme inn uten bransje eller med en som ikke er blant de 13, eller `inn` var datoen for den første kursen.

### B) Lista fra basen

`SqliteListeleser.aktiv(dato)` gir aksjene som er i lista den dagen (`inn` er `NULL` eller ikke etter dagen, og `ut` er `NULL` eller etter dagen), i rowid-rekkefølge. Hentekommandoen henter aksjene i lista for børsdagen, og kvotesjekken regner med antallet pluss indeksen.

**Ville feilet hvis:** en aksje som er tatt ut, ble hentet, eller kvoten ble regnet av 15 når lista hadde et annet antall.

### C) En aksje som er tatt ut

Vurderingene og kursene står (AD-7, AD-21). Oversikten, Min liste og børsometeret viser bare aksjene i lista, og aksjesiden viser en som er tatt ut, med historikken. En dag uten rad fra og med `ut` gir «ikke i lista».

**Ville feilet hvis:** en aksje som ble tatt ut, mistet vurderingene sine, eller dagene etter ble talt som dager vi ikke kjørte.

### D) Testen for de 15

Testen som holdt `aksje` lik `AKSJEUNIVERS`, byttes mot en som holder de 15 i `0003_aksje.sql` like `AKSJEUNIVERS`, og `AKSJEUNIVERS` er lista appen starter med.

### E) Prøven på en kopi av `ose.db`

Migrasjonen prøves på en kopi av `data/db/ose.db` i en midlertidig mappe, som slettes etterpå. Antallet aksjer, `inn` for hver av dem og at radene i `vurdering` og `kurs` er like før og etter, står her. Ingen kurser eller rådata (regel 16).

## Grenser

- Ingen kall til EODHD utover kvotesjekken i regel 15. `data/db/ose.db` skrives aldri; prøven gjøres på en kopi (svaret kl. 11:57, regel 22).
- Egen gren, PR, og stopp før flettingen.

## Bygget 08.11 (instruksjonen kl. 14:05)

Bygget på grenen `2-11-lista-leses-fra-basen`, i worktreen `G74-lund-osen-2-11`, fra `907393d6`.

- **Filene.** `src/migrasjoner/0009_lista.sql` (del A), `les_lista` og `Oversiktspost.ut` i `src/lagring_sqlite.py` og `src/oversiktsdata.py`, `lista_fra_basen` i `src/fetch_prices.py` (del B), `Art.IKKE_I_LISTA` i `src/tilstand.py`, «ikke i lista» i `src/markedsoversikt.py`, `src/aksjedetalj.py`, `src/historikk.py` og `src/app.py` (del C), og `docs/hjelp.md` («Hva betyr «ikke i lista»?»).
- **Avvik fra delene.** Hentingen leser lista uten å migrere basen, som sjekkene før første kall (`_aapne_for_sjekken`): en base en versjon bak, før 0009, gir alle aksjene i `aksje`, som før. Testen som sier at siste migrasjon ikke rører tabellene sjekken leser, er vurdert og godtar de tre setningene i 0009 mot `aksje`. En helgedag etter `ut` er fortsatt «ikke børsdag».
- **Tester («Ville feilet hvis» i hver):** `tests/test_lista.py`. Testene som skrev fire verdier i `aksje`, navngir kolonnene, og testene med bransjen «Test» bruker «Teknologi».

**Prøven på en kopi av `ose.db`** (del E), rett før hele settet kl. 15:48:47, med koden i worktreen: basen ble kopiert med SQLite sin backup fra en tilkobling med `mode=ro` til en midlertidig mappe, og migrert der. Versjonen gikk fra 8 til 9. Antallet rader i `kurs`, `vurdering`, `kursserie`, `ki_logg`, `min_liste`, `omsetning` og `indeks` var det samme før og etter, og et avtrykk av alle radene i `vurdering` og `kurs` var likt. De 15 aksjene fikk `inn` 2026-10-02, den første dagen med vurdering, og ingen fikk `ut`. Lista for 09.11 har 15 aksjer. Den midlertidige mappa er slettet, og sha256 for `data/db/ose.db` var den samme før og etter.
- **Hele settet,** alene: kl. 15:48:47–15:58:36 ga 6 feil (bildeavtrykkene og to tester i `test_omsetning.py` som ventet versjon 8), rettet. Kl. 16:00:02–16:09:39 ga bare `test_ruff` (to ubrukte importer), rettet. Kl. 16:09:52–16:19:22: 4602 bestått, 24 hoppet over og 0 feilet. Alle sju bildene ble tatt på nytt med DevTools-protokollen og er byte for byte de samme.
