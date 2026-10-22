---
title: 'Story 2.3 (2.3c): første henting på dagtid når basen er tom'
type: 'feature'
created: '2026-10-22'
status: 'review'
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

## Avgjort underveis

- **Første henting bruker aldri bonuskvoten** (ECH3, VG8). Mangler den kall av dagens, gir den 0 kall og kode 1. Bonusen brukes fortsatt bare til å fullføre kveldens henting (NFR-01, beslutningen 08.10 kl. 08:06).
- **Kvelden etter første henting:** den trenger 16 kall, og det er normalt 4 igjen. Med minst 12 i bonuskvoten tas de derfra, og dagen får signal. Ellers bruker den 0 kall, og den dagen får aldri signal, fordi en vurdering bare kan skrives for inneværende børsdag (AD-7); neste kveld hentes neste børsdag. Det sier utskriften (`_kvelden`), hjelpen og raden «Klar» i README-en, og en datert rettelse står etter presiseringen i `epics.md` (BH1, ECH2, VG1–VG3). Det erstatter «dagens kurser kommer neste kveld» i presiseringen og i punktet «Kallene samme kveld» over.
- **Unntaket i lagrene** krever også at `vurdering` ikke har en rad for en annen dato, så en base med historikk og en tom `ki_logg` ikke kan få KI-rader for en eldre dag (BH4).
- **Når KI-tjenesten ikke er klar ved første henting,** sier utskriften at teksten for den dagen ikke kan lages senere, og lover ingen ny kjøring (ECH1).
- **`--les-inn`** nevnes ikke lenger som vei når fila for forrige børsdag finnes og basen er tom: innlesingen gir kurser uten signal for den dagen (BH5, ECH4, VG6).
- **En dag utenfor kalenderen** (`UtenforKalenderen` for forrige børsdag) gir den gamle avvisningen med 0 kall, ikke kode 1 (ECH6).
- **AD-7 har fått en merknad** i `ARCHITECTURE-SPINE.md` om unntaket, merket «foreslått, ikke godkjent av gruppen» (VG4).
- **Commit a (`0c85909`) var ikke grønn:** avtrykkene bak bildene i `tests/test_docker.py` følger `boersdag.py` og `lagring_sqlite.py`, og de testene var ikke med i kjøringen før commiten. Rettet i `10b6e4f` (VG9). Historikken skrives ikke om (regel 7).
- **Sitatet under «Slik virker det i dag», «siste børsdag på eller før», er gjenskapt** (VG10). Docstringen i `boersdag.py` sier «Siste boersdag paa eller foer dag.», og PRD-en, punkt 3 i tabellen over åpne punkter: «Inneværende børsdag er siste børsdag på eller før dagens dato i Europe/Oslo.»
- **Testen for dagtid i `tests/test_docker.py`** (`test_demoen_paa_dagtid_og_helgen_i_steg_8`) og avtrykket av pila til den ekte versjonen er endret i `70c8eb5`, fordi README-en ikke lenger sier at demoen er eneste vei på dagtid. Grunnen står i testen.

## Mutantene, kjørt

I en fersk klon med `core.autocrlf=false`, slettet etterpå, én om gangen med `-x`, med kopi før og sha256 lik HEAD etter hver. Kjørt på `9ad2c60` og igjen på `1431a6a`, med `tests/test_fetch_prices.py`, og en gang til med bare `TestFoersteHenting` (`-k`).

| # | Mutant | Først i fila (`1431a6a`) | `TestFoersteHenting` alene |
|---|---|---|---|
| M1 | Dagens rad skrevet før kl. 22 med tom base (datoen ikke flyttet) | `test_tom_base_foer_22_henter_forrige_boersdag` | den samme |
| M2 | En base som ikke er tom, hentet før kl. 22 | `test_boersdag_kl_21_59_59_gir_0_kall_og_nevner_flagget` | `test_base_som_ikke_er_tom_gir_0_kall_foer_22` |
| M3 | Kursene bedt om til og med i dag | `test_tom_base_foer_22_henter_forrige_boersdag` | den samme |

## Gjennomgangen

Gjennomgang 22.10 på diffen `fb9bcac..9ad2c60`. Linsene var Blind Hunter (BH, 8 funn, bare diffen), Edge Case Hunter (ECH, 7 funn) og Verification Gap (VG, 11 funn), hver for seg og uten å endre noe i repoet. 26 funn ble 18 rader. Fire hadde dom medium. Tre er rettet i `1431a6a`. Den fjerde, VG4, kan bare gruppen lukke: unntaket fra AD-7 må godkjennes.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH2, VG1, VG2, VG3 | Uten nok bonuskvote får dagen aldri signal, men tekstene sa at dagens kurser kommer neste kveld, og README-en sa ingenting | medium | rettet: samme ordlyd i utskriften, hjelpen og raden «Klar», og en datert rettelse etter presiseringen |
| BH2 | `base_er_tom` var ikke testet for en base webserveren har laget | medium | rettet: testene for en migrert tom base og en base med én kursrad |
| ECH1 | Når KI-tjenesten ikke var klar ved første henting, lovet utskriften en ny kjøring som ikke kan lage teksten | medium | rettet |
| VG4 | Unntaket fra AD-7 er ikke godkjent, og spinen sa ingenting | medium | åpent: merknaden står i spinen, og godkjenningen er gruppens. Grenen flettes ikke før den finnes |
| BH4 | Unntaket i KI-loggen så bare på `ki_logg` | low | rettet: også `vurdering` |
| ECH3, VG8 | Første henting kunne ta kall fra bonuskvoten på dagtid | low | rettet: den bruker den aldri |
| BH5, ECH4, VG6 | Meldingen anbefalte `--les-inn`, som gir kurser uten signal | low | rettet, og testet |
| VG5 | Ingen test av en base som ikke kan leses, mandag morgen, kvoten om kvelden eller `forrige_boersdag` | low | rettet, utenom grenen utenfor kalenderen, som ikke kan nås i 2026 |
| VG9 | Commit a var ikke grønn | low | uten endring: står over og i Utført-linja (regel 7) |
| VG7 | «Neste i v1» har første henting på dagtid | low | uten endring: flyttes til «Ferdig» etter flettingen |
| BH3 | En base som ikke kan leses, gir den gamle meldingen | low | uten endring: slik var det før 2.3c, og det blir 0 kall |
| ECH5 | Meldingene når basen feiler eller kveldens henting overlapper første henting | low | uten endring: sjeldne, og ingen rad skrives feil |
| ECH6 | Utenfor kalenderen ga kode 1 | nit | rettet: den gamle avvisningen |
| BH6 | Docstringen om ny dag i KI-steget | nit | rettet |
| BH7 | «Dagens kurs hentes aldri før kl. 22» stemmer ikke med flagget | nit | rettet |
| BH8, ECH7 | «16 av dagens 20» gjelder ikke mellom midnatt og midnatt GMT | nit | rettet: «normalt» |
| VG10 | Sitatet om inneværende børsdag var gjenskapt | nit | rettet under «Avgjort underveis», med kilden ordrett |
| VG11 | To funksjoner heter `forrige_boersdag` | nit | rettet: docstringen viser til den andre |

## Åpent

- **Unntaket i lagrene (AD-7)** må godkjennes av gruppen før flettingen. Alternativet er at første henting på dagtid bare lagrer kursene, uten vurdering og KI-tekst, og at signalet kommer fra kveldens henting. Det gir ikke «signalet med en gang» som avgjørelsen 23:33 sier.

## Det som ikke endres

- Ingen test går på nett. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22), og den ekte `.env` røres ikke.
- `TIDSGRENSE`, `--uten-tidskontroll`, nye forsøk (2.3b) og demovakten.
- Grenen flettes ikke i denne instruksjonen. Kveldens henting kl. 22:00 går på koden på main.
