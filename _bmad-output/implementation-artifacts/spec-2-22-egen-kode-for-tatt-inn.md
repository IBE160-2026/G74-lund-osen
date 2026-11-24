---
title: 'Story 2.22: en egen kode når det eneste som mangler, er aksjer tatt inn etter kveldens henting'
type: 'code'
created: '2026-11-24'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '609f555b'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-28-tatt-inn-uten-kurser.md'
---

Skrevet 24.11 etter beskjeden kl. 14:31 i `docs/ai-prompts/2026-11-24.md` og
gruppens svar kl. 14:29 på spørsmål 3 i 9.28. Rådet anbefalte å vente til
etter brukertest 2, men gruppen valgte nå. Neste ledige nummer i Epic 2
etter 2.21 er 2.22. Worktreen er `G74-lund-osen-2-22`, på grenen
`2-22-egen-kode-for-tatt-inn`, fra main (`609f555b`), etter at 2.21 er
flettet i `e80d9227` og ført.

## Storyen

Som **gruppe som leser resultatet av kveldsjobben** vil vi at en kveld der
alt er i orden, ikke ender med kode 1, så 1 fortsatt betyr at noe som skulle
vært hentet, mangler.

**Oppfyller:** spørsmål 3 i 9.28 (svaret 24.11 kl. 14:29), FR-412 ·
**Begrenses av:** NFR-01 (nye forsøk bruker aldri bonuskvoten), AD-6, AD-7,
regel 3, 19, 20, 22 og 23; ingen migrering, og hva som hentes, endres ikke

**Avhenger av:** 9.28, 2.21, 2.3b og 2.8. **Én økt:** ja.

## Det som er slått opp

- `start/kveldshenting.ps1` avslutter med koden fra `fetch_prices.py`
  (`$kode = $LASTEXITCODE` og `exit $kode`), så Oppgaveplanleggeren viser
  koden fra kveldens siste kjøring som `LastTaskResult`.
- En kjøring som tar inn en aksje etter kveldens henting, finner at aksjen
  mangler dagens kurs, og går til `nytt_forsoek` i `src/fetch_prices.py`. Gir
  `kall_til_nye_forsoek` 0, avslutter det med `sys.exit(1)`. Det samme
  skjer i hver senere kjøring samme kveld (føringen av 9.28, «Kode 1 fra
  kveldsjobben»).
- Kodene i dag: 0 når alt er hentet, 1 når noe mangler eller feilet, 2 fra
  `argparse` for feil i argumentene, og 3, `KODE_BARE_INDEKSEN`, når bare
  hovedindeksen feilet (beslutningen 17.10 kl. 11:58). 4 er ledig.
- `valg.ikke_forsoekt` (9.28) gir de egne aksjene som er tatt inn uten en
  eneste kurs og uten en rad i `vurdering` fra dagen de kom inn. En aksje som
  sto i lista da kveldens vanlige henting gikk, har en slik rad. En aksje
  med `inn` lik børsdagen og uten rad er derfor tatt inn etter kveldens
  henting.
- Kodene står beskrevet i `docs/hjelp.md` («Kan hentingen gå av seg selv?»,
  som alt sier at hentingen slutter med kode 1 i dette tilfellet, og at det
  ikke er en feil), i modulteksten og docstringene i `src/fetch_prices.py`,
  og i toppen av `start/kveldshenting.ps1`. README-en og
  `docs/installasjon.md` nevner ikke kodene fra hentingen; installasjonen
  har delen «Hentingen hver kveld», som viser til loggen.

## Det som gjøres

1. **Koden.** `KODE_BARE_TATT_INN = 4` i `src/fetch_prices.py`. Et nytt
   forsøk ender med 4 når alt dette gjelder:
   - kjøringen går på selve børsdagen;
   - hver aksje som mangler dagens kurs etter forsøket, er tatt inn i dag
     uten å være forsøkt hentet (`valg.ikke_forsoekt`, med `inn` lik
     børsdagen), og forsøket gjorde ikke noe kall for den;
   - grunnen til at den ikke ble forsøkt, er at det ikke var kall igjen til
     nye forsøk;
   - hovedindeksen feilet ikke i kveldens henting.
2. **Som før:** mangler også en annen aksje, eller feilet et kall for en
   aksje som er tatt inn, er koden 1. Feilet indeksen, er koden den som
   gjelder i dag. Kan kvoten eller basen ikke leses, eller er klokka etter
   23:50, er koden 1. Hva som hentes og lagres, endres ikke.
3. **Utskriften** sier koden, hva den betyr, og at det er i orden.
4. **Skriptet.** `start/kveldshenting.ps1` gir koden videre som før, og
   skriver en linje i loggen om hva 4 betyr. Kveldsjobben på PC-en røres
   ikke; skriptet når den først kvelden etter flettingen.
5. **Tekstene.** Hjelpen, installasjonen, modulteksten og docstringene sier
   koden, hva den betyr, og at det er i orden.
6. **Testen** lager tilstandene med hentingen selv, som i 9.28, og feiler
   før rettingen. Testene fra 9.28 og 2.21 som låste kode 1 for tilfellet,
   rettes med en linje om svaret.

## Grenser

- Ingen API-kall utover kvotesjekken. `data/`, `.env` og `_privat/` røres
  ikke, og den ekte versjonen startes ikke. Kveldsjobben på PC-en og
  databasekopien røres ikke.
- Ingen migrering. Bare testbaser under `tmp_path` (regel 22).
- Aldri to pytest samtidig. Lokalt kjøres testfilene storyen rører, og
  `--dokumentene`. Hele settet kjøres i CI.

## Kontroll

- [ ] En kjøring der bare aksjer tatt inn etter kveldens henting mangler kursen, uten kall igjen, ender med kode 4
- [ ] Hver senere kjøring samme kveld ender også med 4
- [ ] Mangler også en annen aksje, er koden 1
- [ ] Feilet indeksen i kveldens henting, er koden som før
- [ ] En aksje EODHD ikke ga kurser for, gir fortsatt 1
- [ ] Utskriften, skriptet, hjelpen og installasjonen sier hva 4 betyr, og at det er i orden
- [ ] Ingen migrering, og det som hentes og lagres, er som før
- [ ] Testen feilet før rettingen
- [ ] Gjennomgangen med fire roller er tatt, og regel 25 holder
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
