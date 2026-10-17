---
title: 'Story 9.1, oppdatering 17.10: docs/kvalitetssikring.md følger repoet'
type: 'docs'
created: '2026-10-17'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '3699a16'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/kvalitetssikring.md'
  - '{project-root}/docs/vurderingsmatrise.md'
---

## Intent

**Problem:** `docs/kvalitetssikring.md` (story 9.1) har tallene fra 03.–05.10. §3 og §5 slutter ved 2.5, 8.0 og 9.0, og §6 sier at mye som er bygget, ikke er det: Docker, KI-laget, 2.3, 2.8, nettsperren og at webserveren leser basen. README-en viser til dokumentet under «Tester». Story 9.1 sier at dokumentet oppdateres ved hver epic (`epics.md`, «Tidspunkt»), og §8 i dokumentet sier hvordan.

**Grunnlaget:** instruksjonen 17.10 kl. 22:22, spesifikasjonene i `_bmad-output/implementation-artifacts/`, dagsfilene i `docs/ai-prompts/` og git-loggen. PR-en flettes i instruksjonen når vilkårene i steg 5 holder (svarene 17.10 kl. 22:06).

## Planen, én commit per punkt

**a) §1 og §2:** testene telles på nytt med `uv run pytest --collect-only -q` på `3699a16`, med CI-kjøringen for samme commit, i en ny tabell med dato over den fra 03.10, som står. Antallet som hoppes over lokalt, og testene for nettsperren, får en datert linje.

**b) §3 og §5:** en rad for hver spesifikasjon som mangler, 27 i alt: de 25 med status `done` fra 2.2 til 10.3, og 3.4 og 10.2a, som har en annen status. §3 har mutantene og hvilke som overlevde en stund, og vedlegget får én linje per spesifikasjon med mutantene og testene som fanget dem. §5 har radene i triagen (rettet, avvist, utsatt). Tallene er hentet fra spesifikasjonene. Der spesifikasjonen og dagsfila sier ulikt, føres det som et åpent punkt (regel 12). Tre agenter leste spesifikasjonene og dagsfilene, og et utvalg av påstandene deres er slått opp på nytt før de ble skrevet.

**c) §6:** hver linje som ikke stemmer lenger, får en Rettet-linje med commit. Nye hull føres inn: testene som bare bruker testklienten, ekte svar fra EODHD og Ollama, at CI kjører uten hemmeligheter uten egen test, og README-prøven.

**d) «Feil vi fant og rettet»:** 12 til 15 eksempler fra repoet. Minst ett for hver måte de ble funnet: en test, en mutant, en linse i gjennomgangen, utskriften fra en ekte henting, kontrollen av KI-teksten og vår egen gjennomgang av «Kom i gang» 16.10. For hvert: hva som var feil, hvordan det ble funnet, commiten som rettet det og testen som passer på nå. Det som rettes i README-PR-en søndag, står som ikke rettet ennå.

**e) Feilhåndtering, validering av input og hemmeligheter,** med testene som viser det.

**f) Manuelle tester og testplaner,** med dato og resultat der det finnes.

**Testfila** `tests/test_kvalitetssikring.py`:
- Hver spesifikasjon med status `done` har en rad i §3 og i §5. Deler flere spesifikasjoner samme story, kreves én rad for hver.
- Hver test som `kvalitetssikring.md` og `vurderingsmatrise.md` nevner med fil og navn, finnes.

**§5** får en linje om at hver PR fra nå får triagen som kommentar. PR #56–#60 og denne PR-en får en slik kommentar (steg 4).

## Boundaries & Constraints

- Bare det som står i repoet. Ingen karakter, intet anslag, og ingenting sitert fra sensorveiledningen.
- Ingen linje fjernes, utenom status og `updated`. En linje som ikke stemmer lenger, får en Rettet-linje.
- Ingen kall til EODHD utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- **Steg 4 i instruksjonen** ber om at kommentarene i PR #56–#60 merkes «satt sammen 18.10». De settes sammen 17.10, så de merkes med den datoen. Det er et avvik fra instruksjonen, og det står i svaret til gruppen.

**Testtallet før:** 2366 bestått og 17 hoppet over lokalt, og 2383 bestått i CI (kjøring 39066471455 på `3699a16`).

*Lagt til 2026-10-17 kl. 22:59:* PR #61 er squash-flettet i `eca81b4`, låst til head-en `d1a1d0d`. CI var grønn på head-en (39068835003) og på main (39068954002). Triagen står som kommentar i PR #61, og PR #56–#60 fikk sin, satt sammen 17.10 fra spesifikasjonene.

## Mutantene

Én om gangen med `-x` og bare `tests/test_kvalitetssikring.py`, i den ferske klonen med `core.autocrlf=false`, med kopi av `docs/kvalitetssikring.md` før og sha256 mot HEAD etter hver:
- Q1, raden for 2.9 tatt bort fra §5: `test_hver_ferdige_spesifikasjon_har_en_rad`. Fanget på `af04741` og på `70a22ef`.
- Q2, et testnavn som ikke finnes: `test_hver_test_dokumentene_nevner_finnes`. Fanget på `af04741` og på `70a22ef`.
- Q3, raden for «3.4, alle 10» tatt bort fra §5: overlevde på `af04741`, fordi radene for 3.4 Demoversjonen dekket den (ECH3). Fanget av `test_hver_ferdige_spesifikasjon_har_en_rad` på `70a22ef`.
- Q4, raden for 1.6 tatt bort fra hovedtabellen i §3: overlevde på `af04741`, fordi 1.6 også står i tabellen over mutanter som overlevde (ECH2). Fanget av `test_hver_ferdige_spesifikasjon_har_en_rad` på `70a22ef`.

## Gjennomgangen

Gjennomgang 17.10 på diffen `main...af04741`, med Blind Hunter (BH, 13 funn), Edge Case Hunter (ECH, 15) og Verification Gap (VG, 7). Verification Gap sjekket hvert tall og hver commit i de nye delene. Alle 38 tallene per fil, summen 2383, CI-kjøringen 39066471455 og alle 56 commitene stemmer, og så gjør de 42 radene i §5, utenom én klassifisering (VG3). Rettingene står i `70a22ef` og i denne commiten.

| # | Funn | Dom | Rute |
|---|---|---|---|
| ECH2, BH6, VG | Tabellen over mutanter som overlevde i §3 telte med, så en rad som var tatt bort fra hovedtabellen for 1.5b, 1.6, 1.8, 1.9, 2.0 eller 2.1, ble ikke oppdaget | medium | patch: bare den første tabellen under «### Per story» og «### Gjennomgangen av hver story». Q4 |
| ECH3, VG | En rad for en annen spesifikasjon med samme story dekket en som manglet: radene for 3.4 Demoversjonen dekket «3.4, alle 10» | medium | patch: hver spesifikasjon må ha sin egen rad, med egen merkelapp der to deler story, og en test krever merkelappen. Q3 |
| BH5, ECH1 | Settes spesifikasjonen for 9.1 til done, mangler raden for den | low | patch: radene for 9.1 i §3, §5 og vedlegget |
| BH3, BH4, ECH11 | Navnene i vedlegget fra 17.10 står uten fil og ble ikke sjekket, og linja for 2.3 hadde de gamle navnene | low | patch: `test_testene_i_vedlegget_fra_17_10_finnes`, og de nye navnene med «før 17.10:» foran de gamle |
| BH7, ECH4 | Status ble lest fra den første linja med `status:` i fila | low | patch: bare fra frontmatter, og `test_status_leses_bare_fra_frontmatter` |
| BH8, ECH5 | Et filnavn uten storynummer ga en uklar feil | low | patch: en tydelig melding, og flere tegn etter tallet godtas |
| BH9 | Gulvet på 40 var ikke forklart | low | patch: `MINST_FERDIGE` med kommentar |
| BH10, ECH7, ECH8, ECH9, ECH10 | `async def`, nøstede klasser, en klasse alene og en fil som mangler | low | patch: alle tas med, og en fil som mangler står i lista |
| ECH6 | En overskrift med nytt navn ga en feil uten forklaring | low | patch: en tydelig melding |
| ECH12 | Får en test nytt navn, må en gammel linje endres, og det er ikke lov | low | patch: `OMDOEPT`, der et gammelt navn kan godtas |
| ECH13 | Samme fil ble lest én gang per navn | low | patch: `lru_cache` |
| BH1, VG | Tallene i §1 og §2 tar ikke med den nye testfila | low | patch: en datert linje om 2393 tester i 39 filer etter flettingen |
| BH11, VG1 | «Målt på `59976ee`» hadde ingen kilde, og klokkeslettet var tidspunktet linja ble skrevet | low | patch: beskrivelsen av PR #60 og `git diff` som kilde, og klokkeslettet er tatt ut |
| VG2 | Tellingen med `-rs` hadde ingen kilde | low | patch: grenen for 9.1 som kilde |
| VG3 | Raden BH2 i 2.3b har ruten «Verification under», og regelen for «Rettet» nevnte den ikke | low | patch: regelen nevner den |
| ECH14, BH13 | «Kan ikke settes til done uten rad» lovet mer enn testen gjør, og spesifikasjonen sa «fra 2.2 til 2.9 og 10.3» | low | patch: «gjør testen rød» og «fra 2.2 til 10.3» |
| ECH15 | Toppen av dokumentet nevnte ikke testen | low | patch |
| BH2 | 3.4 PR #27 står med 12 rettet, og det åpne punktet sier 11 rader med patch | low | avvist: «Rettet» tar med en Rettet-linje (notatet i §5), så 11 og 1 er 12, slik det åpne punktet sier |
| BH12 | Datoen i kommentarene i PR #56–#60 er 17.10, ikke 18.10 som instruksjonen sier | low | avvist: kommentarene settes sammen 17.10, og avviket står i Boundaries og i svaret til gruppen |
