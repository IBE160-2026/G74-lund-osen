---
title: 'Story 2.14: eks.datoer føres inn for hånd'
type: 'code'
created: '2026-11-24'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'ed7360f5'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
---

Skrevet 24.11 etter instruksjonen kl. 13:02 i `docs/ai-prompts/2026-11-24.md`,
steg 5, og gruppens svar kl. 13:05: storyen bygges på egen gren, PR-en åpnes,
og den flettes ikke før brukertest 2 er gjort. Rådet anbefalte det, fordi
migreringen endrer den ekte databasen. Worktreen er `G74-lund-osen-2-14`, på
grenen `2-14-eksdatoer`.

## Storyen

Som **gruppe** vil vi føre inn kommende eks.datoer fra selskapenes egne sider,
så appen kan vise dem uten en kilde vi ikke har.

**Oppfyller:** FR-414 · **Begrenses av:** NFR-08, AD-3, AD-6, AD-10, AD-16,
regel 16 og 22

**Avhenger av:** 2.3. Vilkårene leses før første dato. **Én økt:** ja.

## Det som er slått opp

- FR-414 i `prd.md`: datoene føres inn med en kommando, lagres i basen og
  aldri i en fil i repoet. Hver dato har datoen den ble sjekket og hvor den
  ble lest. Et selskap får ingen dato før vilkårene for nettstedet er lest og
  ført i `docs/kilder-og-rettigheter.md`. Kommandoen gjør 0 nettkall, og
  webserveren skriver ikke tabellen. En dato uten sjekkdato eller kilde
  avvises.
- FR-207, visningen i kursgrafen, er et eget krav og er ikke med i kontrollen
  for 2.14.
- Siste migrasjon er `0015_hoey_lav.sql`, så den nye er `0016`.
- `docs/kilder-og-rettigheter.md` har «Status per kilde», men ingen del for
  selskapenes egne sider.
- Basen åpnes med `aapne_base`, som migrerer. Hentingen nekter en demobase
  (`nekt_demobase`).

## Det som gjøres

1. **Tabellen.** `0016_eksdato.sql` lager `eksdato` med `symbol`, `eks_dato`,
   `sjekket` og `kilde`. Hvert symbol har høyst én rad, den kommende
   eks.datoen. Datoene er ISO-datoer, `eks_dato` er ikke før `sjekket`, og
   kilden er ikke tom. Symbolet må stå i `aksje`.
2. **Kommandoen.** `uv run python src/eksdato.py <symbol> <eks.dato>
   --sjekket <dato> --kilde <adresse>`. Den tar én dato for ett symbol og
   gjør ingen nettkall. `--sjekket` og `--kilde` må gis. Den avviser:
   - et symbol som ikke står i lista i basen;
   - et symbol der vilkårene for nettstedet ikke er ført i
     `docs/kilder-og-rettigheter.md`;
   - en kilde som ikke er en adresse på nettstedet som er ført for symbolet;
   - en dato som ikke kan leses, en sjekkdato etter i dag, og en eks.dato
     før sjekkdatoen;
   - en demobase.
3. **Samme dato sjekket på nytt** oppdaterer `sjekket` og `kilde`. **En
   flyttet dato** erstatter den gamle. En eldre sjekk skriver ikke over en
   nyere.
4. **Vilkårene.** `docs/kilder-og-rettigheter.md` får delen «Selskapenes egne
   sider (eks.datoer)» med en tabell: symbol, nettsted, datoen vilkårene ble
   lest, og vurderingen. Tabellen er tom. Gruppen fører radene selv, og
   storyen skriver ingen vilkår for ekte nettsteder. Kommandoen godtar et
   symbol når raden har et nettsted, en dato og vurderingen «ja».
5. **Webserveren** skriver ikke tabellen, og en test holder det.
6. **Ingen eks.dato i sporede filer.** Testene bruker oppdiktede symboler,
   nettsteder og datoer i baser under `tmp_path`.
7. **Dokumentene:** arkitekturen og innleveringen sier `0016`, og README-en
   og hjelpen følger med der de nevner migrasjonene eller kommandoene.

## Grenser

- Ingen API-kall utover kvotesjekken. Bare testbaser (regel 22). Kommandoen
  kjøres ikke mot `data/db/ose.db`, og den ekte versjonen startes ikke.
- Ingen vilkår for ekte nettsteder skrives i `docs/kilder-og-rettigheter.md`.
- PR-en åpnes, men flettes ikke før brukertest 2 er gjort (gruppens svar
  24.11 kl. 13:05).
- Aldri to pytest samtidig. Hele settet kjøres i CI.

## Kontroll

- [ ] En egen tabell, med ny migrasjon: symbol, eks.dato, datoen den ble sjekket, og hvor den ble lest
- [ ] Kommandoen tar inn én dato for ett symbol, og nekter et symbol der vilkårene ikke er ført
- [ ] Kommandoen gjør ingen nettkall, og webserveren skriver ikke tabellen
- [ ] Ingen eks.dato står i en sporet fil
- [ ] En ny sjekk av samme dato oppdaterer datoen den ble sjekket, og en flyttet dato erstatter den gamle
- [ ] En dato kan ikke føres inn uten dato for sjekken eller uten kilde
- [ ] Gjennomgangen med fire roller er tatt
- [ ] Testfilene storyen rører, og `--dokumentene`, er grønne lokalt
- [ ] CI er grønn i alle jobbene
- [ ] PR-en er åpnet og ikke flettet
