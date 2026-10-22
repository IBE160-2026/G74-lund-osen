---
title: 'Story 2.3 (2.3c): første henting på dagtid når basen er tom'
type: 'feature'
created: '2026-10-22'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'fb9bcac'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/docs/ux-logg.md'
---

## Intent

**Problem:** på en børsdag før `TIDSGRENSE` (kl. 22:00) gir den første hentingen 0 kall, så den som prøver den ekte versjonen på dagtid, ser ingen kurser før kvelden (U53). README-en sier ikke hva første henting gir (U54).

**Grunnlaget:** avgjørelsen 21.10 kl. 23:33 under «Prioritering» og story 2.3 i `epics.md`: «når basen er tom, henter første henting siste fullførte børsdag også på dagtid en hverdag, så en ny bruker ser kursene og signalet med en gang. Dagens rad skrives aldri før `TIDSGRENSE` (kl. 22:00 i `src/fetch_prices.py`), kallene er da brukt for dagen, og en base som ikke er tom, hentes som før.» Den sier også at det «må passe med FR-402 (kontroll mot forventet børsdag) og AD-7 (ingen slette- eller endremetode)». U53 og U54 i `docs/ux-logg.md`. Instruksjonen er den kl. 18:18 i dagsfila 22.10. Den flettes ikke før kveldens henting er ferdig.

## Slik virker det i dag (slått opp 22.10 på `fb9bcac`)

- **Tidskontrollen** (`kjoer` i `src/fetch_prices.py`): på en børsdag før `TIDSGRENSE` i Oslo skriver den hvorfor og gir 0 kall og `None`, uten å se på basen. Med `--uten-tidskontroll` hentes det likevel, for dagens dato. Den kommer før basen, filvakten, nøkkelen og kvoten.
- **Børsdagen** raden gjelder, er `dato = innevaerende_boersdag(dag)`, «siste børsdag på eller før» kalenderdagen i Oslo (`boersdag.py`). På en børsdag er det dagen selv.
- **Basen (FR-402):** `manglende_i_basen` gir aksjene uten kurs for `dato`. Mangler ingen, hentes ingenting. Etter hentingen nevner `kjoer` aksjene der svaret ikke har kursen for `dato`, og gir kode 1. FR-402 i `prd.md`: «Den skal kontrollere at nyeste `date` i svaret er forventet børsdag.»
- **Filvakten:** fila heter etter `dato` (`filnavn(dato)`). Finnes den, og basen mangler dagens kurs for noen, går kjøringen til et nytt forsøk (2.3b); ellers stopper den med kode 1.
- **Intervallet:** `bygg_intervall(dag)` ber om kurser fra 364 dager før kalenderdagen til og med den.
- **Kvoten:** `vurder_kvote(igjen, bonus, behov)` med `behov = len(lista) + 1`, 16 med de 15. Er det færre enn 16 igjen av dagens kall, men bonuskvoten dekker resten, hentes det med kall fra bonusen; ellers 0 kall og kode 1. Docstringen: «Bonusen brukes bare til aa fullfoere kveldens henting (NFR-01, beslutningen 08.10 kl. 08:06).»
- **Vernene i lagrene:** `SqliteVurderingslager.skriv` og `SqliteKILogg.skriv` i `src/lagring_sqlite.py` regner `innevaerende_boersdag(norsk_dato(klokke()))` og avviser enhver annen dato (`ValueError` og `IkkeInnevaerendeBoersdag`). `lag_ki_tekster` i `src/ki_tekst.py` gjør den samme sjekken selv før hver rad. AD-7, «Skjerpet»: «`skriv` tar imot datoen og **avviser enhver dato som ikke er inneværende børsdag**.»
- **Visningen** leser vurderingen for datoen til nyeste kurs, ikke dagens dato (`oversiktsdata.py`), så en base med gårsdagens kurser viser gårsdagens signal.

## Hvordan endringen passer med dette

- **Tidskontrollen** ser på basen bare når den ellers ville sagt nei: på en børsdag før `TIDSGRENSE`, uten `--uten-tidskontroll`. Er basen tom, er det første henting: `dato` blir forrige børsdag, og kjøringen går videre. Ellers sier den nei som før, med 0 kall. Etter `TIDSGRENSE`, på dager børsen er stengt og med `--uten-tidskontroll` er alt som før.
- **Tom base** betyr at fila ikke finnes, eller at `kurs` og `vurdering` ikke har én rad. Kan basen ikke leses, regnes den ikke som tom, så det blir 0 kall som før.
- **Intervallet** går til og med `dato`, forrige børsdag, så dagens rad aldri kommer med i svaret, heller ikke når API-et alt har en foreløpig rad for dagen.
- **FR-402** kontrollerer mot `dato`, den dagen som hentes. Har svaret ikke kursen for den, nevnes aksjen og kjøringen gir kode 1, som før.
- **Filvakten** sjekker fila for `dato`, så fila heter etter forrige børsdag. Kveldens henting samme dag skriver fila for dagens dato og stoppes ikke. Finnes fila for forrige børsdag alt, og basen er tom, stopper kjøringen med 0 kall og kode 1, fordi et nytt forsøk (2.3b) ikke gjelder første henting.
- **AD-7:** lagrene får et smalt unntak, ikke en ny metode. `SqliteVurderingslager` og `SqliteKILogg` tar `foerste_dag` (standard `None`). En rad for `foerste_dag` godtas bare når den er børsdagen rett før inneværende børsdag, og tabellen ikke har noen rad for en annen dato. Uten `foerste_dag` er vernet som før for alle som skriver. Ingen rad som finnes, skrives om på annen måte enn før: det er ingen eldre rader i en tom base, og vurderingen regnes av kurser for en dag som er avsluttet, slik kveldens henting den dagen ville regnet den. Unntaket må godkjennes av gruppen før flettingen (se «Åpent»).
- **Kallene samme kveld:** første henting bruker 16 av dagens 20 kall. Kveldens henting trenger 16, og 4 er igjen. Har kontoen bonuskvote, tar `vurder_kvote` de 12 som mangler derfra, og kveldens henting går; ellers gir den 0 kall og kode 1, og dagens rad hentes neste kveld. Linja kl. 23:33 sier «kallene er da brukt for dagen». Koden bruker bonuskvoten når den finnes, så linja får en datert presisering.
- **Signalet** lagres fra første henting og regnes aldri bakover: «Signalet dag for dag» fylles én børsdag om gangen, fra den første.

## Kontrollpunktene

- a) Koden: er basen tom på en børsdag før `TIDSGRENSE`, henter første henting forrige børsdag, med kurser til og med den dagen. Fila i `data/raa/`, vurderingene og KI-tekstene gjelder den dagen, og filvakten stopper ikke kveldens henting. En base som ikke er tom, hentes som før, og etter `TIDSGRENSE` og på dager børsen er stengt er alt som før.
- b) Brukeren: README-en (raden «Klar», setningen om første gang før kl. 22, og steg 8), `docs/hjelp.md` og utskriften (regel 19), og den daterte presiseringen av linja kl. 23:33 under «Prioritering» og story 2.3.
- c) Testene, med «Ville feilet hvis», med falsk hentefunksjon og uten nett.

## Planen, én commit per punkt

1. a) `forrige_boersdag` i `boersdag.py`, `foerste_dag` i de to lagrene, `foerste_henting` i `lag_ki_tekster`, og i `kjoer` tidskontrollen, intervallet, filvakten og vurderingene for første henting. Eksisterende tester som bruker en tom base for å vise at det blir 0 kall før kl. 22, får en base som ikke er tom, i samme commit, så hver commit er grønn.
2. b) README-en, `docs/hjelp.md`, utskriften og presiseringen i `epics.md`.
3. c) De nye testene.

## Mutantene

Én om gangen, med `-x`, med kopi før og sha256 mot HEAD etter:

- **M1:** dagens rad skrevet før kl. 22 med tom base (`dato` ikke flyttet til forrige børsdag).
- **M2:** en base som ikke er tom, hentet før kl. 22.
- **M3:** kursene bedt om til og med i dag.

## Åpent

- **Unntaket i lagrene (AD-7)** må godkjennes av gruppen før flettingen. Alternativet er at første henting på dagtid bare lagrer kursene, uten vurdering og KI-tekst, og at signalet kommer fra kveldens henting. Det gir ikke «signalet med en gang» som avgjørelsen 23:33 sier.

## Det som ikke endres

- Ingen test går på nett. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22), og den ekte `.env` røres ikke.
- `TIDSGRENSE`, `--uten-tidskontroll`, nye forsøk (2.3b) og demovakten.
- Grenen flettes ikke i denne instruksjonen. Kveldens henting kl. 22:00 går på koden på main.
