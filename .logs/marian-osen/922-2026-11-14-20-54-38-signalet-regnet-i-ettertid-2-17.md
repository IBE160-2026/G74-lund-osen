# Signalet regnet i ettertid (2.17)

## 2026-11-14 kl. 20:54 — Marian Osen

### Oppgave
Ny story i Epic 2, v1.1: signalet regnet i ettertid for børsdager uten lagret vurdering, etter gruppens svar 14.11 kl. 05:41–05:49. Med tillegg 1 (kontrollisten), beskjeden kl. 17:00 (avtrykket av kveldsradene) og fortsettelsen kl. 19:07 etter en API-feil. Alt er ført i `docs/ai-prompts/2026-11-14.md`. Stopp når PR-en er grønn, ingen fletting før gruppens ja.

### Plan
- Kvotesjekken først (regel 15), instruksjonen ordrett i scratchpad og dagsfila, så grenen `2-17-signalet-i-ettertid` i worktreen `G74-lund-osen-2-17` fra `origin/main`.
- Spesifikasjon med svarene og spørsmål med forslag: [`spec-2-17-signalet-regnet-i-ettertid.md`](../../_bmad-output/implementation-artifacts/spec-2-17-signalet-regnet-i-ettertid.md).
- Kode og tester, dokumentene, mutanter, gjennomgang med tre hunters, bildene, flettingen av main, lokale tester, PR og CI.

### Resultat
- **Kvoten** ved øktstart kl. 16:57: 20 av 20 kall brukt i dag (`apiRequestsDate` 2026-11-14), og 296 i bonuskvoten. Ingen andre API-kall.
- **Dagsfila** på main: `c452e171`, `9aa716bc` og `674343bf`.
- **Grenen**, åtte commits: `cf045f35` (spesifikasjonen), `242c210b` (koden og testene), `92763443` (PRD-en, AD-7, designreglene, hjelpen og README-en), `0ff7d1cd` (rettingene etter gjennomgangen), `0789f2b3` (flettingen av `origin/main`), `00f77291` (bildene og avtrykkene), `4d0f3b15` (kontrollisten og resten av spesifikasjonen), `afe343fe` (rettingene etter `--dokumentene`) og `2ab516bc` (treffene på nytt).
- **Koden:** migrasjonen `0014_regnet.sql` (kolonnen `regnet`, `kveld` eller `ettertid`, og en trigger), `src/ettertid.py`, `SqliteEttertidslager`, steget til slutt i hentingen (migrerer aldri basen selv), `--regn-ettertid-paa-nytt` og `--slett-ettertid`. Porten for kvelden gir bare kveldsradene uten `med_ettertid=True`, så KI-grunnlaget er uendret. Den fjerde tilstanden `Art.ETTERTID`, og «i ettertid» med stiplet kant overalt der en tidligere dag vises med signal.
- **Testene:** 37 i `tests/test_ettertid_2_17.py`. Testene som gjaldt det som var før, er endret med Rettet-linje. Ingen er slettet, og `test_ad7_stopper_et_forsoek_paa_aa_etterfylle` står uendret.
- **Mutantene:** seks, én per del (A–F), alle fanget, og filene var like HEAD etterpå.
- **Gjennomgangen:** Blind Hunter, Edge Case Hunter og Verification Gap. VG1 (høy, kanten i ruta i børsometeret ga 1,3:1) er rettet. De middels funnene er rettet, og BH1 står åpent som spørsmål 19 (regel 25). Triagen står i spesifikasjonen.
- **Bildene** ble tatt på nytt med skriptet og jobblista fra vinduet for 3.3k, fra en demobase i scratchpad og ledige porter, aldri 8000. `aksjesiden-brfe-demo.png` og `mobil/notatene-brfe-390-demo.png` er endret, og 16 er like byte for byte. Før og etter ligger på grenen `pr-2-17-bilder` (`16fa85c3`).
- **Lokalt:** hele settet én gang før gjennomgangen, kl. 17:56–19:16 (5855 bestått, 37 feilet, 24 hoppet over). Feilene var testene for det som var før, og de er rettet. Etter rettingene: de 24 testfilene storyen rører, 2273 bestått og 16 hoppet over. `--dokumentene` ga først 3 feil, som er rettet i `afe343fe`. Til slutt besto den på `2ab516bc` (2957 bestått og 7 hoppet over, kl. 20:35–20:47).
- **PR #157**, CI grønn i alle fire jobbene på `2ab516bc` (run 43634016363). Jobben `pytest` hadde 5854 bestått og 99 hoppet over. Ikke flettet.
- **Kveldsjobben** sto som Disabled hver gang den ble lest (16:58, 20:04 og 20:47), så pausene gjaldt ikke. `data/db/ose.db` ble aldri åpnet. Prøven av kommandoen for avtrykket ble kjørt på en prøvebase i scratchpad.
- **Ryddet:** demoserverne og nettleserne er stoppet med `Stop-Process`, og ingenting er slettet med `rm`. Én mappe fra `mktemp` står i `/tmp` (`tmp.JS6UjK2gQg`, med en demobase for innsyn). Lite minne stoppet ingenting.

### Åpne punkter
- Gruppens ja til flettingen av PR #157, med spørsmål 1–19 i spesifikasjonen. BH1 (middels) står åpent som spørsmål 19 til gruppen har svart.
- «Kontroll etter flettingen» i spesifikasjonen. Rett etter flettingen, før den ekte versjonen startes eller jobben går: en kopi av `data/db/ose.db` og sha256 av kveldsradene. Morgenen etter første kveldskjøring: loggen, `skjema_versjon` og avtrykket.
- `docs/kvalitetssikring.md` får radene for 2.17 ved føringen etter flettingen.
- Bildegrenen `pr-2-17-bilder` kan slettes når gruppen vil.

## 2026-11-14 kl. 21:57 — Marian Osen

### Oppgave
Tillegg 2 til 2.17 for natta, etter gruppens svar 14.11 kl. 21:07: alle forslagene er godtatt, også spørsmål 19 (BH1) som bygget. Svarene skal føres, PR #157 flettes uten nytt ja når CI er grønn, med avtrykket av kveldsradene rett før, og så føringen. Tillegg 3 og 4 kom samtidig og gjøres etterpå, i rekkefølge.

### Plan
- Tilleggene ordrett i scratchpad og i dagsfila.
- Svarene under spørsmål 1–19, BH1 lukket, `origin/main` flettet inn, CI på den nye head-en.
- Avtrykket med kommandoen i spesifikasjonen, så flettingen, låst til head-en, og føringen som for 8.30.

### Resultat
- **Tilleggene** 2, 3 og 4 er ført i `3b83d2c5`. Kveldsjobben sto som Disabled (kl. 21:15, 21:22).
- **Svarene** står under spørsmål 1–19, og BH1 er lukket i triagen (`2d489390`), etter flettingen av main (`d180a3b0`). CI var grønn i alle fire jobbene på `2d489390` (run 43636648065, `pytest` 5854 bestått og 99 hoppet over).
- **Avtrykket** av kveldsradene kl. 21:22, fra hovedkopien med `mode=ro` og datoen 2026-11-14: `665d4eff98e57820f399d874f233667388ca32470e25818741200da5124e4bf9`, 477 rader. sha256 av `data/db/ose.db` var lik før og etter, og basen sto på versjon 13 uten kolonnen `regnet`. Ingen kurser er skrevet ut.
- **Flettet:** PR #157 ble squash-flettet i `1fafddce` kl. 21:23, låst til `2d489390`.
- **Føringen:** `8c2c1ce0` (status done, «Flettet», avtrykket og linja i `epics.md`), `68f6c4b4` (kvalitetssikringen) og `73db9ae7` (hele testnavnet). `--dokumentene` på main ga først 1 feil, testnavnet med «…», kl. 21:24–21:40. Etter rettingen besto den: 2957 bestått og 7 hoppet over, kl. 21:40–21:57.

### Åpne punkter
- Morgenkontrollen etter første kveldskjøring med 2.17 (punkt 2 under «Kontroll etter flettingen»): loggen, `skjema_versjon` og avtrykket med samme dato. Kopien av basen før det er gruppens.
- Bildegrenen `pr-2-17-bilder` kan slettes når gruppen vil.
