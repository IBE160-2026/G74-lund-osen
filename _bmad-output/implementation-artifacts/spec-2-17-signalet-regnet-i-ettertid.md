---
title: 'Story 2.17: signalet regnet i ettertid for børsdager uten lagret vurdering'
type: 'feature'
created: '2026-11-14'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'c452e171'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
---

Skrevet 14.11 i et nytt vindu i hovedkopien, etter instruksjonen kl. 16:57, tillegg 1
kl. 16:58 og beskjeden kl. 17:00, ført i `docs/ai-prompts/2026-11-14.md`. Neste ledige
nummer etter 2.16 i Epic 2 er 2.17 (2.15 er gitt til «Utbytte fra EODHD», se 2.16).
Worktreen `G74-lund-osen-2-17`, grenen `2-17-signalet-i-ettertid`, fra `origin/main`
(`c452e171`).

## Storyen

Som **bruker** vil jeg se signalet også for en børsdag appen ikke vurderte samme
kveld, merket «i ettertid». Da har historikken, grafen og børsometeret ingen hull
der kursene finnes, og jeg ser hvilke dager som ble vurdert samme kveld.

**Oppfyller:** FR-408 og FR-409 (endret, se PRD-en) · **Begrenses av:** AD-7
(merknaden 2026-11-14), AD-3, AD-16, AD-17, NFR-04, NFR-06, regel 16 og 22

**Avhenger av:** 2.4, 2.5, 2.7b, 2.16. **Én økt:** nei.

## Svarene

Svarene er gitt i økta til instruksjonen og står ordrett i dagsfila. De er ikke
skrevet andre steder i repoet, så teksten her bygger på instruksjonen (regel 3).

*Svar 2026-11-14 kl. 05:41–05:49 (gruppens svar, rådet anbefalte det):* v1.1,
signalet regnet i ettertid for børsdager uten lagret vurdering. Til slutt i hver
henting, etter kveldens vurderinger og KI-tekster, regnes signalet for hver børsdag
med kurser i basen, for aksjene i lista, når dagen mangler rad i vurdering og
aksjen har nok kurser etter kveldens regel (`MINST_HANDELSDAGER`), bare med kursene
til og med dagen. Aldri inneværende børsdag. En kveldsrad, også en rad med grunn,
overskrives aldri. En feil stopper aldri kvelden. Radene får eget merke i basen og
kan regnes på nytt eller slettes med en kommando som bare rører dem. Ingen
KI-tekst for dem, og KI-grunnlaget og setningen om hvor lenge signalet har vært
slik leser bare kveldsradene.

*Svaret kl. 05:49 (grunnen):* KI-tekst for små hull (1–3 kvelder) står som
senere, fordi det tar tid, krever kontroll, gir fare for å se framover, og gir
mindre nytte bakover.

*Gruppens ønske kl. 05:51 (tillegg 1):* alle endringene noteres, med hvor de
gjøres og hvordan de sjekkes etterpå (kontrollisten under).

*Visningen, valgt av gruppen (skissene er ikke i repoet):* en dag i ettertid får
stiplet kant og «i ettertid» i «Signalet dag for dag». Aksjesiden for en slik dag
sier under datoen at signalet er regnet i ettertid, og «Signalet forklart» sier at
KI-teksten bare lages samme kveld som kursene hentes. Merket står overalt der en
tidligere dag vises med signal, også i grafen og børsometeret. «Skilte seg ut» i
uka og i måneden teller dagene med og sier hvor mange som er i ettertid.

*Beskjed kl. 17:00 (rådet):* i «Kontroll etter flettingen» regnes sha256 av
kveldsradene over kolonnene som fantes før migrasjonen, sortert på aksje og dato,
så den nye kolonnen ikke endrer avtrykket. Kommandoen står ordrett, leser basen
med `mode=ro` og skriver bare avtrykket og antallet rader.

## Det som var

`vurdering` hadde bare rader skrevet av kveldens henting (og av demokommandoen med
lagerets klokke stilt på hver dag). `SqliteVurderingslager.skriv` avviser andre
datoer enn inneværende børsdag (AD-7), med unntaket for første henting på dagtid.
En børsdag uten rad viste «ikke vurdert» (FR-409), og fotnoten sa at signalet
«regnes aldri ut bakover». Det gjaldt dagene før første henting, kvelder uten
henting og dagene fra `--les-inn`.

## Spørsmål til gruppen, med forslag

Et spørsmål stopper ikke arbeidet, og alt er bygget etter forslaget.

1. **Merket i basen.** *Forslag, som bygget:* kolonnen `regnet` i `vurdering`, med
   `kveld` eller `ettertid`, i migrasjonen `0014_regnet.sql` (`ADD COLUMN ... NOT
   NULL DEFAULT 'kveld'`, uten `DROP TABLE`). Alle radene som finnes, blir `kveld`.
   En CHECK sier at en rad i ettertid aldri har grunn, og en trigger avviser at en
   kveldsrad blir en rad i ettertid. Ingen trigger for `DELETE`, fordi testene
   sletter rader i testbaser, og `vurdering` hadde ingen slik trigger før.
2. **Porten for kvelden.** `test_ad7_stopper_et_forsoek_paa_aa_etterfylle` skal stå
   uendret, og den krever at `SqliteVurderingslager.les` gir `None` for en dag i
   hullet. *Forslag, som bygget:* `les` og `les_periode` gir bare kveldsradene, som
   før, og visningene ber om radene i ettertid med `med_ettertid=True`. Da leser
   hentingen, KI-laget og demoens KI-tekster bare kveldsradene uten at noen må huske
   det. `Vurdering` har feltet `ettertid` (standard `False`), og `skriv` avviser en
   vurdering med `ettertid` satt. Radene i ettertid skrives og slettes bare av
   `SqliteEttertidslager`.
3. **Hvilken liste.** *Forslag, som bygget:* aksjene i lista i basen på inneværende
   børsdag (`les_lista`), regnet når hentingen er ferdig. En aksje som kom inn i
   lista senere, får da signalet i ettertid for de tidligere dagene med kurser. En
   aksje som er tatt ut, røres ikke.
4. **Dager før børskalenderen.** Kursene i den ekte basen går ett år tilbake, til
   2025, og kalenderen begynner i 2026 (2.16). *Forslag, som bygget:* en dag før
   2026 får ingen rad i ettertid, fordi kalenderen ikke kan si om den var børsdag.
   Den viser «utenfor børskalenderen, som begynner i 2026» som før.
5. **Kommandoen.** *Forslag, som bygget:* `uv run python src/fetch_prices.py
   --regn-ettertid-paa-nytt` sletter radene i ettertid og regner dem på nytt med
   kursene i basen, og `--slett-ettertid` sletter dem. Begge rører bare radene i
   ettertid, gjør ingen kall, leser ingen nøkkel og nekter en demobase.
6. **Dagene fra `--les-inn`.** *Forslag, som bygget:* innlesingen regner ikke selv.
   Dagene får signalet i ettertid ved neste henting, og meldingen sier det.
7. **Setningene i «Signalet forklart» for en dag i ettertid.** *Forslag, som
   bygget:* setningen om hvor lenge signalet har vært slik, og setningen om hva
   hovedindeksen og bransjen gjorde samme dag, står ikke for en dag i ettertid,
   fordi de er en del av det KI-grunnlaget leser. For en kveldsdag telles bare
   kveldsradene, så setningen er som før.
8. **Tellingen i uka og måneden.** *Forslag, som bygget:* «3 av 5 dager skilte seg
   ut, 1 i ettertid» betyr at 1 av de 5 vurderte dagene er regnet i ettertid.
   Måneden sier det samme etter antallet børsdager.
9. **«3 av 3» det siste året.** *Forslag, som bygget:* linja over historikken teller
   dagene i ettertid med og sier hvor mange av dem som er i ettertid, som uka.
10. **Demobasen fra før.** *Forslag, som bygget:* en demobase uten rader i ettertid
    regnes som gammel (`gammel_demobase`), så webserveren ber om at den lages på
    nytt, som etter 3.4c.
11. **Kveldens rad over en rad i ettertid.** Det skjer bare om klokka går bakover,
    fordi radene i ettertid bare regnes for dager før inneværende børsdag.
    *Forslag, som bygget:* kveldens rad skriver over raden i ettertid, også med en
    grunn, fordi kveldens rad er den som gjelder.
12. **Når hentingen ikke henter.** *Forslag, som bygget:* signalet i ettertid regnes
    til slutt i hver henting, også når tidskontrollen sier nei, basen har alt, eller
    hentingen stopper med en kode. Aldri for en demobase, og aldri når basen ikke
    finnes.

## Delene

### A) Basen og porten (spørsmål 1, 2 og 11)
`src/migrasjoner/0014_regnet.sql`, `src/vurderingsdata.py` (`ettertid`,
`i_ettertid`, `kveldsradene`), `src/lagring_sqlite.py` (`_UPSERT` setter
`regnet = 'kveld'`, `les` og `les_periode` med `med_ettertid`,
`SqliteEttertidslager`, `_regnet` for en base én versjon bak, story 2.8).

### B) Regelen (svaret kl. 05:41–05:49, spørsmål 3, 4 og 12)
`src/ettertid.py`: `regn_i_ettertid` og `fyll_i_ettertid`, uten I/O.
`src/fetch_prices.py`: `kjoer` kaller `_henting` og så `regn_signalet_i_ettertid`
til slutt. En feil fanges og føres med typen alene, uten kurser (regel 16).

### C) Kommandoen (spørsmål 5 og 6)
`--regn-ettertid-paa-nytt` og `--slett-ettertid` i `src/fetch_prices.py`.

### D) KI-grunnlaget (svaret kl. 05:49, spørsmål 7)
`dagene.tell_dagene`, `moenstrene.retningene` og `skiftene`, `dagsgrunnlag.vanlig`
leser bare kveldsradene, og `ki_tekst.lag_ki_tekster` lager ingen tekst for en rad
i ettertid. Teksten om dagen på forsiden sammenlignes med et grunnlag av
kveldsradene.

### E) Demoen
`src/demo.py` regner radene før startdagen med samme funksjon, med klokka på
siste demodag. Ingen kveldsrad og ingen KI-tekst i demoen endres.

### F) Visningen (spørsmål 7–9)
Den fjerde tilstanden `Art.ETTERTID` i `src/tilstand.py`, merket «i ettertid» med
stiplet kant overalt der en tidligere dag vises med signal, tekstene om «ikke
vurdert», hjelpen, omvisningen og README-en.

## Grenser

Ingen API-kall utover kvotesjekken. `data/db/ose.db` skrives aldri (regel 22).
Bildene tas fra demobasen, aldri på port 8000. Ingen KI-modell kjøres og ingen
KI-tekst lages.
