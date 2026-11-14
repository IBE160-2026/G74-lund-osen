---
title: 'Story 2.17: signalet regnet i ettertid for børsdager uten lagret vurdering'
type: 'feature'
created: '2026-11-14'
status: 'done'
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
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
2. **Porten for kvelden.** `test_ad7_stopper_et_forsoek_paa_aa_etterfylle` skal stå
   uendret, og den krever at `SqliteVurderingslager.les` gir `None` for en dag i
   hullet. *Forslag, som bygget:* `les` og `les_periode` gir bare kveldsradene, som
   før, og visningene ber om radene i ettertid med `med_ettertid=True`. Da leser
   hentingen, KI-laget og demoens KI-tekster bare kveldsradene uten at noen må huske
   det. `Vurdering` har feltet `ettertid` (standard `False`), og `skriv` avviser en
   vurdering med `ettertid` satt. Radene i ettertid skrives og slettes bare av
   `SqliteEttertidslager`.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
3. **Hvilken liste.** *Forslag, som bygget:* aksjene i lista i basen på inneværende
   børsdag (`les_lista`), regnet når hentingen er ferdig. En aksje som kom inn i
   lista senere, får da signalet i ettertid for de tidligere dagene med kurser. En
   aksje som er tatt ut, røres ikke.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
4. **Dager før børskalenderen.** Kursene i den ekte basen går ett år tilbake, til
   2025, og kalenderen begynner i 2026 (2.16). *Forslag, som bygget:* en dag før
   2026 får ingen rad i ettertid, fordi kalenderen ikke kan si om den var børsdag.
   Den viser «utenfor børskalenderen, som begynner i 2026» som før.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
5. **Kommandoen.** *Forslag, som bygget:* `uv run python src/fetch_prices.py
   --regn-ettertid-paa-nytt` sletter radene i ettertid og regner dem på nytt med
   kursene i basen, og `--slett-ettertid` sletter dem. Begge rører bare radene i
   ettertid, gjør ingen kall, leser ingen nøkkel og nekter en demobase.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
6. **Dagene fra `--les-inn`.** *Forslag, som bygget:* innlesingen regner ikke selv.
   Dagene får signalet i ettertid ved neste henting, og meldingen sier det.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
7. **Setningene i «Signalet forklart» for en dag i ettertid.** *Forslag, som
   bygget:* setningen om hvor lenge signalet har vært slik, og setningen om hva
   hovedindeksen og bransjen gjorde samme dag, står ikke for en dag i ettertid,
   fordi de er en del av det KI-grunnlaget leser. For en kveldsdag telles bare
   kveldsradene, så setningen er som før.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
8. **Tellingen i uka og måneden.** *Forslag, som bygget:* «3 av 5 dager skilte seg
   ut, 1 i ettertid» betyr at 1 av de 5 vurderte dagene er regnet i ettertid.
   Måneden sier det samme etter antallet børsdager.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
9. **«3 av 3» det siste året.** *Forslag, som bygget:* linja over historikken teller
   dagene i ettertid med og sier hvor mange av dem som er i ettertid, som uka.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
10. **Demobasen fra før.** *Forslag, som bygget:* en demobase uten rader i ettertid
    regnes som gammel (`gammel_demobase`), så webserveren ber om at den lages på
    nytt, som etter 3.4c.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
11. **Kveldens rad over en rad i ettertid.** Det skjer bare om klokka går bakover,
    fordi radene i ettertid bare regnes for dager før inneværende børsdag.
    *Forslag, som bygget:* kveldens rad skriver over raden i ettertid, også med en
    grunn, fordi kveldens rad er den som gjelder.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
12. **Når hentingen ikke henter.** *Forslag, som bygget:* signalet i ettertid regnes
    til slutt i hver henting, også når tidskontrollen sier nei, basen har alt, eller
    hentingen stopper med en kode. Aldri for en demobase, og aldri når basen ikke
    finnes.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
13. **Stiplet i grafen.** Designregler §5 sier at stiplet bare brukes for
    hovedindeksen. Gruppen valgte stiplet kant for en dag i ettertid. *Forslag,
    som bygget:* prikken for en dag i ettertid har hvit midte og stiplet kant i
    fargen for retningen (gul ved 3 av 3), og teksten under grafen sier hva den
    betyr og hvor mange dager i grafen som er i ettertid. Designregler §3 og §5
    får en datert linje.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
14. **«Loggen viser migrasjonen».** Migrasjonsløperen skriver ingenting, og
    kveldsjobben logger bare det hentingen skriver ut. Appen migrerer dessuten
    basen ved første forespørsel (`_migrer_en_gang` i `src/app.py`), så
    migrasjonen kan skje når den ekte versjonen startes, før jobben går
    (beskjeden kl. 19:07). *Forslag:* morgenkontrollen leser raden for
    `0014_regnet.sql` i `skjema_versjon`, med tidspunktet, med kommandoen under
    «Kontroll etter flettingen». Loggen viser antallet dager regnet i ettertid.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
15. **Merket i børsometeret.** Rutene er små, og teksten står bare der ruta har
    plass. *Forslag, som bygget:* ruta har stiplet kant utenfor ruta, mot kartet
    (gjennomgangen, VG1), og «i ettertid» der grunnen ellers står, så kartet regner
    plassen som før (VG2). Teksten står også i tittelen, og tabellen under kartet
    har merket ved styrken. I de minste rutene er det bare kanten og tittelen.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
16. **Sjekkene ved et tenkt kjøp.** *Forslag, som bygget:* «Sjekkene på siden da
    kjøpet ble notert» leses også fra en rad i ettertid, fordi siden viste den.
    Notatet lagrer sjekkene, ikke merket. Et tenkt kjøp noteres bare fra siden for
    siste dag med kurser, og den er en kveldsrad, så det gjelder bare en dag
    hentingen ikke vurderte samme kveld.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
17. **Metoden for bildene.** Tillegg 1 viser til spørsmål 4 i spesifikasjonen
    for 3.3k. Spørsmål 4 og del 2 der beskriver panelet og «Vis meg rundt», men
    teksten i spesifikasjonen for 3.3k sier ikke ordrett hvordan
    `notatene-brfe-390-demo.png` tas (slått opp 14.11). Det står i
    spesifikasjonen for 8.22, tillegg 5: «bare delen `mine-notater`». *Forslag,
    som bygget:* bildene tas med skriptet og jobblista fra vinduet som bygde 3.3k,
    kopiert uendret: notatene ved 390 px er elementet `#mine-notater` med 16 px
    over og under, panelet tas etter et klikk på «Mine notater», og «Vis meg
    rundt» etter et klikk på knappen, med utsnittet slik vinduet står.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
18. **Dagene før aksjen kom inn i lista.** Hver henting tar et år bakover, så en
    aksje som nettopp er fulgt, får nesten et år med rader i ettertid, og en aksje
    som er tatt inn igjen, får rader for tiden den var ute (gjennomgangen, ECH7).
    *Forslag, som bygget:* slik, fordi svaret sier hver børsdag med kurser, for
    aksjene i lista. Linja under datoen sier «fordi dagen ikke har en vurdering
    fra kvelden», ikke at hentingen ikke ble kjørt. Vil gruppen ha rader bare fra
    `inn`, er det en endring i `fyll_i_ettertid`.
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt.
19. **En henting som stopper før kallene** (gjennomgangen, BH1, middels). Steget i
    ettertid kjører til slutt i hver henting, også når tidskontrollen sier nei.
    *Bygget etter rettingen:* da migrerer steget aldri basen selv. Står basen ikke
    på siste versjon, venter steget til hentingen eller webserveren har migrert den,
    og sjekken før kallene leser som før (testen fra 2.8 er uendret). På en base
    på siste versjon skriver en slik henting rader i ettertid og sier det i
    utskriften. *Forslag:* slik. Funnet står åpent til gruppen har svart (regel 25).
    *Svar 2026-11-14 kl. 21:07 (gruppens svar, rådet anbefalte det):* forslaget er godtatt, også som bygget (BH1).

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

## Bygget 14.11

Commitene `cf045f35` (spesifikasjonen og storyen), `242c210b` (koden og testene),
`92763443` (PRD-en, AD-7, designreglene, hjelpen, README-en og loggene),
`0ff7d1cd` (rettingene etter gjennomgangen), `0789f2b3` (flettingen av
`origin/main`, bare dagsfila), `00f77291` (bildene og avtrykkene), `4d0f3b15`
(denne delen av spesifikasjonen) og `afe343fe` (rettingene etter
`--dokumentene`).

**Målt.** I demoen får 13 av 15 aksjer signalet i ettertid fra 13.03 til 18.09,
1 690 rader. Varde Systemer har for få kurser, og Matfjord Merkevarer har ingen.
De 225 kveldsradene fra 21.09 og KI-radene for 09.10 er de samme: avtrykket av
kveldsradene i `tests/test_demo.py` er uendret, med kolonnene fra før 0014. I den
ekte versjonen med én henting 22.09 og en serie på 80 dager får dagene fra den
51. kursdagen signalet i ettertid. KI-promptene 23.09 er like med og uten radene
i ettertid (`TestKIGrunnlaget`).

**Testene.** `tests/test_ettertid_2_17.py` har 37 tester, alle med «Ville feilet
hvis». Hele settet ble kjørt én gang lokalt før gjennomgangen, 14.11 kl.
17:56–19:16 (5855 bestått, 37 feilet, 24 hoppet over). Feilene var testene som
gjaldt det som var før, og de er rettet med en Rettet-linje (kontrollisten under).
Etter det er bare testfilene storyen rører og `--dokumentene` kjørt lokalt, og
hele settet i CI. 14.11 kl. 20:10–20:32: de 24 testfilene storyen rører, 2273
bestått og 16 hoppet over, og så `--dokumentene`, 2954 bestått, 7 hoppet over og 3
feilet: ankeret til overskriften i FR-408, ordene fra 8.19 i steget «Dag for
dag», og fila med treffene, som het `spec-2-17-…` og ble lest som en andre
spesifikasjon. Rettet i `afe343fe`, og de seks testfilene med dem besto (307).

## Kontrollisten (tillegg 1)

Stedet, endringen og hvordan den er sjekket: test, bilde eller lest. Treffene fra
søket i steg 1, med hvert treff som er endret eller står, er i
[`treffene-2-17.md`](treffene-2-17.md). Treffene som står i `src/`, er
kommentarer om at visningen leser signalet og aldri regner det. Det gjelder
fortsatt, fordi radene i ettertid regnes i hentingen. Treffene i `tests/`, i
eldre spesifikasjoner og i loggene er historikk.

### Koden

| Stedet | Endringen | Sjekket |
|---|---|---|
| `src/migrasjoner/0014_regnet.sql` | Kolonnen `regnet` (`kveld` eller `ettertid`) med CHECK, og triggeren som avviser at en kveldsrad blir en rad i ettertid | Test: `TestMigrasjonen`, `test_basen_avviser_…`, `test_aksje.py`, `test_migrering.py`, vakten for siste migrasjon i `test_fetch_prices.py` |
| `src/migrering.py` | Står. Løperen kjører 0014 som de andre | Test: `test_migrering.py` (versjon 14) |
| `src/vurderingsdata.py` | `Vurdering.ettertid`, `i_ettertid`, `kveldsradene`, og `med_ettertid` i porten | Test: `test_vurderingslager.py`, `TestLageret` |
| `src/lagring_sqlite.py` | `_UPSERT` setter `regnet = 'kveld'`, `les` og `les_periode` gir bare kveldsradene uten `med_ettertid`, `_regnet` for en base én versjon bak, `SqliteEttertidslager`, og oversikten leser `regnet` | Test: `TestLageret`, `TestEtterGjennomgangen`, `TestSjekkenLeserEnBaseEnVersjonBak` |
| `src/ettertid.py` (ny) | `regn_i_ettertid` og `fyll_i_ettertid` | Test: `TestRegelen`, `TestEtterGjennomgangen` |
| `src/fetch_prices.py` | `kjoer` kaller `_henting` og så steget i ettertid (`bare_migrert`), kommandoene, og meldingene om første henting, kvelden og `--les-inn` | Test: `TestHentingen`, `test_fetch_prices.py` og `test_etterfyllingen_2_4.py` (Rettet) |
| `src/fetch_prices.py`, dagene fra `--les-inn` | Innlesingen regner ikke selv. Neste henting regner dagene, og meldingen sier det | Test: `test_meldingen_om_les_inn` (Rettet) |
| `src/demo.py` | Radene før STARTDAG med `fyll_i_ettertid`, og `gammel_demobase` | Test: `TestDemoen`, `test_gammel_demobase_…`, `test_demo.py` (Rettet). Bilde |
| `src/tilstand.py` | Den fjerde tilstanden `Art.ETTERTID`, `MED_SIGNAL`, `Tilstand.vurdering` og `.ettertid` | Test: `test_tilstanden_er_en_egen` |
| `src/historikk.py` | `Dag.ettertid`, `Uke.ettertid`, `Maaned.ettertid` og `AlleSjekkene.ettertid` | Test: `test_signalet_dag_for_dag_…`, `test_funnene_8_23.py` (Rettet) |
| `src/perioder.py` | Står. Ingen tilstand. «regnes bakover» gjelder periodene | Lest |
| `src/boersometer.py` | `Rute.ettertid`, og `Rute.grunn` gir «i ettertid» | Test: `test_grafen_boersometeret_…` |
| `src/graf.py` og signaldagene i `src/app.py` | `Signaldag.ettertid`, og tredje ledd i `_signaldagene` | Test: `test_grafen_boersometeret_…` |
| `src/etterpaa.py` | Står. «Etterpå» bruker `historikk.Dag`, som har merket | Test: `test_etterpaa_under_notatet_…` |
| `src/oversiktsdata.py` | Står. `Oversiktspost.innhold` har `Vurdering` med `ettertid` | Lest. Test: `test_linja_for_siste_dag_…` |
| `src/markedsoversikt.py` | `MED_SIGNAL`, `Rad.ettertid` | Test: oversikten og Min liste i `TestVisningen` |
| `src/aksjedetalj.py` | `MED_SIGNAL`, `Detalj.ettertid` og `Dagen.ettertid` | Test: `test_aksjesiden_for_dagen_…`, `test_linja_for_siste_dag_…` |
| `src/app.py`, fotnoten og valgt dag | `signal_trenger` til fotnoten, `med_ettertid` der siden viser signalet, ingen setning om dagene for en dag i ettertid, og teksten om dagen leser bare kveldsradene | Test: `TestVisningen`, `test_app.py`, `test_de_lave_funnene_9_10.py` og `test_ki_visning.py` (Rettet) |
| `src/dagen_ferdig.py` | Står. `les` uten `med_ettertid` gir bare kveldsradene, så sjekken om dagen er ferdig er som før | Lest |
| `src/hjelpetekster.py` | Hjelpen ved «Signalet dag for dag», steget «Dag for dag» og steget «Signalet forklart» | Test: `test_hjelpetekster.py`, `test_vis_meg_rundt_8_26.py` (50 ord), `test_funnene_8_2b.py` |
| `src/ki_tekst.py`, `dagene.py`, `moenstrene.py`, `dagsgrunnlag.py` | Bare kveldsradene, og ingen KI-tekst for en rad i ettertid | Test: `TestKIGrunnlaget`. Mutant D |

### Visningen

| Stedet | Endringen | Sjekket |
|---|---|---|
| `aksje.html` | Linja under datoen, linja «Signal: …» ved grafen, prikkene og teksten under grafen, cellen med stiplet kant i «Signalet dag for dag», uka, måneden og «3 av 3»-linja, og «Signalet forklart» | Test: `TestVisningen`. Bilde ved 1280 og 390 px |
| `index.html` | Merket i raden og i linja under i Min liste | Test: `test_grafen_…`, `test_min_liste_…`, `test_linja_for_siste_dag_…` |
| `_notat.html` | Merket i «Etterpå» | Test: `test_etterpaa_under_notatet_…` |
| `boersometer.html` | Klassen og tittelen i ruta, teksten fra `Rute.grunn`, og merket i tabellen | Test: `test_grafen_…` |
| `_brikker.html` | Makroen `ettertid` | Test: `test_stilen_…`, `test_kom_i_gang_8_29.py` (Rettet) |
| `_fotnote_ikke_vurdert.html` | Ny tekst, også demoteksten | Test: `test_app.py`, `test_demo.py`, `test_boersometer.py` (Rettet) |
| `_rundtur.html` | Står. Stegene kommer fra `hjelpetekster.rundturer`, der «Dag for dag» er endret | Test: `test_vis_meg_rundt_8_26.py` |
| `_hjelp.html` og `hjelp.js` | Står. Vinduene kommer fra `hjelpetekster.py`, og skriptet har ingen tekst om tilstandene (søket) | Lest |
| `stil.css` | Merket med stiplet kant i `--dempet-2` (4,14:1 mot bakgrunnen, 4,64:1 mot kortene og kartet), cellen, prikkene, kanten utenfor ruta, og regler for forced-colors. Teksten bærer merket | Test: `test_stilen_…`, `test_app.py` (stiplet, Rettet), `test_utseende.py`. Bilde ved 1280 og 390 px |

### Dokumentene

| Stedet | Endringen | Sjekket |
|---|---|---|
| `prd.md` | FR-408 og tabellen i FR-409, hentekommandoen (steg 6), «Kort fortalt», ordlisten, oversikten, kursgrafen og lista. I §2 ekstra og senere (KI-tekst for små hull, med grunnen fra 05:49) | Lest. `--dokumentene` |
| `prd-endringslogg.md` | Datert linje under «Endringer etter 12.11» | Lest |
| `ARCHITECTURE-SPINE.md` | Datert merknad under AD-7, kartet og migrasjonene | Lest |
| `designregler.md` | Daterte linjer i §3 og §5 | Lest |
| `epics.md` og `sprint-status.yaml` | Story 2.17 | `--dokumentene` |
| `docs/hjelp.md` | «Signalet dag for dag», «ikke vurdert», «Når kan jeg hente?» og «Jeg har ikke hentet på noen dager» | Test: `test_hjelpen_sier_det_fotnoten_sier` (Rettet) |
| `README.md` | Raden «Klar» for den ekte versjonen, og teksten og alt-teksten for aksjesiden | `--dokumentene`. Bilde |
| `docs/innlevering.md` | Migrasjonene 0001–0014, med Rettet-linje | Lest |
| `docs/brukertest.md` | Oppgaven om «i ettertid» i brukertest 2 | Lest |
| `docs/kvalitetssikring.md` | Føres når storyen er flettet, som for 8.30 | Ved føringen |
| `docs/ux-logg.md` | U113 | Lest |
| `issues.md` | Kontrollen etter flettingen og spørsmålene, i sesjonsloggen | Sesjonsloggen |

### Testene som er endret, med Rettet-linje

`test_vurderingslager.py`, `test_etterfyllingen_2_4.py`
(`test_bare_kveldens_vurdering_skrives` gjelder kveldsradene), `test_fetch_prices.py`
(hjelperne for vurdering, meldingene og vakten for 0014), `test_demo.py`
(`test_ikke_vurdert_i_historikken_foer_startdagen`, avtrykket av kveldsradene og
fotnoten), `test_app.py`, `test_boersometer.py`, `test_historikken.py`,
`test_aksje.py`, `test_migrering.py`, `test_kilogg_sqlite.py`, `test_lista.py`,
`test_omsetning.py`, `test_vis_meg_rundt_8_26.py`, `test_vis_meg_rundt_8_9.py`,
`test_funnene_8_23.py`, `test_funnene_8_2b.py`, `test_kom_i_gang_8_29.py`,
`test_de_lave_funnene_9_10.py`, `test_ki_visning.py`, `test_valg.py`,
`test_periodevalget_oversikten.py`, `test_periodevalget_min_liste_boersometer.py`
og `test_docker.py` (fillistene og avtrykkene). Ingen test er slettet, og
`test_ad7_stopper_et_forsoek_paa_aa_etterfylle` står uendret.

## Mutantene

Én per del, i en kopi av fila, med `tests/test_ettertid_2_17.py`. Kopien ble lagt
tilbake, og sha256 og git-hashen var lik HEAD (`92763443`) etter hver.

| Del | Mutanten | Fanget av |
|---|---|---|
| A basen | `slett` sletter alle radene, ikke bare `regnet = 'ettertid'` | `test_ny_utregning_og_sletting_…`, `test_kommandoene_…` |
| B regelen | Signalet regnes med kursen dagen etter | `test_likt_det_som_regnes_med_kursene_etter_dagen_fjernet` |
| C kommandoen | `--slett-ettertid` og `--regn-ettertid-paa-nytt` byttet | `test_kommandoene_roerer_bare_radene_i_ettertid` |
| D KI-grunnlaget | `les_periode` gir radene i ettertid uten `med_ettertid` | `test_kveldsporten_ser_ikke_radene_i_ettertid` |
| E demoen | Demoen regner ikke radene før STARTDAG | fire tester i `TestVisningen` og `TestDemoen` |
| F visningen | «i ettertid» borte fra cellen i «Signalet dag for dag» | `test_signalet_dag_for_dag_…` i begge versjonene |

Mutant D ble ikke fanget av prompttesten, fordi `dagene`, `moenstrene` og
`dagsgrunnlag` filtrerer kveldsradene selv også. Vernet har altså to lag.

## Bildene

Alle bildene i `docs/appen/` og `docs/appen/mobil/` er tatt på nytt med skriptet og
jobblista fra 3.3k (spørsmål 17), fra en demobase i en midlertidig mappe og
demoserveren på en ledig port, ikke 8000, etter rettingene og flettingen. Sammenlignet
byte for byte med main:

- `aksjesiden-brfe-demo.png`: endret. Prikkene i grafen for dagene i ettertid,
  med hvit midte og stiplet kant. «Signalet forklart», setningene og KI-teksten er
  de samme. Teksten og alt-teksten i README-en følger.
- `mobil/notatene-brfe-390-demo.png`: endret i fire rader nederst i
  gjengivelsen. Innholdet er det samme, og bildet ble likt da det ble tatt to ganger.
- De 16 andre er byte for byte de samme, også panelet, «Vis meg rundt» og
  notatene ved 1280 px, og er ikke byttet.

Avtrykkene i `tests/test_docker.py` er regnet ut på nytt, og `src/ettertid.py` er
med i fillistene bak bildene. Bilder før og etter av kalenderen og aksjesiden for
fredag 18.09 i demoen, ved 1280 og 390 px, og av de to bildene som er byttet,
ligger på grenen `pr-2-17-bilder`, med en LESMEG.

## Gjennomgangen 14.11

Blind Hunter (BH, bare diffen), Edge Case Hunter (ECH) og Verification Gap (VG),
hver for seg, bare med lesing, på diffen `c452e171..92763443`. Rettingene står i
`0ff7d1cd`.

| Funn | Grad | Hva | Utfall |
|---|---|---|---|
| VG1 | høy | Den stiplede kanten i ruta i børsometeret ga 1,3:1 mot grønn og rød fyll | Rettet: kanten står utenfor ruta, mot kartet (4,64:1), og testen sjekker det |
| BH1 / ECH8 | middels | Steget i ettertid migrerte basen også når hentingen stoppet før kallene | Rettet: hentingen migrerer aldri for steget. Lukket: gruppen godtok spørsmål 19 som bygget (svaret 14.11 kl. 21:07) |
| BH2 | middels | «Regn på nytt» slettet radene for en aksje som er tatt ut | Rettet, med test |
| ECH1 | middels | «Regn på nytt» slettet rader som ikke kan regnes på nytt når vinduet har flyttet seg | Rettet: regner først og bytter ut per aksje i én transaksjon, med test |
| VG2 / BH6 / ECH4 | middels | Ruta med gul ramme hadde «i ettertid» bare for skjermleseren | Rettet: teksten står der grunnen står, med test |
| VG3–VG6 | middels | «Regn på nytt», tellingen, grafen, «Etterpå», linja ved grafen og Min liste var ikke testet godt nok | Rettet, med tester |
| VG7 | middels | Kontrollisten og «Kontroll etter flettingen» manglet | Rettet: delene over og under |
| BH9 | lav | Sletting og ny utregning i hver sin transaksjon | Rettet sammen med ECH1 |
| ECH2 | lav | En feil for én aksje stoppet de neste | Rettet: utskriften sier hvilken, med test |
| ECH3, ECH7, VG12 | lav | Fotnoten, linja under datoen og FR-409 sa mer eller mindre enn koden | Rettet |
| VG8–VG11 | lav | Kveldens rad over en rad i ettertid, demobasen fra før, hentingen på dagtid, og docstringene | Rettet, med tester |
| BH3 | lav | Den justerte kursen er regnet om etter dagen | Står: en justering ganger alle kursene før en dag med samme tall, så sjekkene er de samme. Kursen i raden er den justerte som står nå |
| BH4 | lav | Oversiktsleseren tåler ikke en base uten `regnet` | Står: den krever siste versjon og leser aldri en base én versjon bak |
| BH5 | lav | `gammel_demobase` bygger på data, ikke et merke | Står: demoen har faste kurser, og testen viser at en ny demobase ikke er gammel |
| BH7, BH8 | lav | Andre steder som sjekker `Art.SVAR` eller leser `vurdering` med SQL | Står: søkt opp, bare `valg.py` og `demo.py`, som gjelder dagens dato eller kveldsradene |
| BH10 | lav | Regelen er kvadratisk i lengden på serien | Står: målt 14.11, 251 børsdager for 18 aksjer, 3 618 rader, ga 0,34 s for regelen |
| ECH5 | lav | «N i ettertid» teller blant de vurderte dagene i uka, men blant dagene med 3 av 3 i linja over | Står: slik eksempelet i instruksjonen er, og spørsmål 8 og 9 sier det |
| ECH6 | lav | Tallene øverst på oversikten for en valgt dag sier ikke hvor mange som er i ettertid | Står: hver rad har merket |

## Flettet 14.11

Svarene kl. 21:07 står under spørsmål 1–19 (tillegg 2), og BH1 er lukket i
triagen. `origin/main` ble flettet inn igjen (`d180a3b0`, bare dagsfila). CI var
grønn på head-en `2d489390` (run 43636648065): 5854 bestått og 99 hoppet over i
jobben `pytest`, og alle fire jobbene grønne. PR #157 ble squash-flettet i
`1fafddce` kl. 21:23, låst til `2d489390`. Kveldsjobben sto som Disabled.

## Kontroll etter flettingen

For gruppen, ikke for vinduet som bygde storyen. Appen migrerer basen ved første
forespørsel (`_migrer_en_gang` i `src/app.py`), så det første som kjører koden fra
2.17 mot `data/db/ose.db`, kan være den ekte versjonen gruppen starter selv, ikke
kveldsjobben (beskjeden kl. 19:07). Jobben kjører koden main hadde ved midnatt, så
første kveldskjøring med 2.17 er den første kvelden jobben går etter flettedagen.
Den står på pause til mandag 16.11.

1. **Rett etter flettingen, før den ekte versjonen startes eller jobben går.**
   *Forslag:* ta en kopi av `data/db/ose.db` til en mappe utenfor repoet. Regn så
   sha256 av kveldsradene med kommandoen under, fra hovedkopien i PowerShell, med
   flettedagen som dato. Den leser basen med `mode=ro`, regner over kolonnene som
   fantes før 0014, sortert på aksje og dato, og skriver bare avtrykket og
   antallet rader, aldri kurser (beskjeden kl. 17:00). En base før 0014 har ingen
   kolonne `regnet`, og da er alle radene kveldsrader.

   ```powershell
   uv run python -c "import hashlib, sqlite3, sys; t = sqlite3.connect('file:data/db/ose.db?mode=ro', uri=True); alle = [r[1] for r in t.execute('PRAGMA table_info(vurdering)')]; k = [n for n in alle if n != 'regnet']; hvor = ' AND regnet = ?' if 'regnet' in alle else ''; arg = (sys.argv[1], 'kveld') if hvor else (sys.argv[1],); rader = t.execute('SELECT ' + ', '.join(k) + ' FROM vurdering WHERE dato <= ?' + hvor + ' ORDER BY symbol, dato', arg).fetchall(); print(hashlib.sha256(repr(rader).encode()).hexdigest(), len(rader))" 2026-11-16
   ```

   Datoen er flettedagen, `ÅÅÅÅ-MM-DD`. Prøvd 14.11 på en prøvebase i scratchpad,
   aldri på `data/db/ose.db`: avtrykket og antallet var like før 0014 og etter
   0014 med 50 rader i ettertid, og sha256 av fila var lik før og etter
   kommandoen.
2. **Morgenen etter første kveldskjøring.**
   - Loggen i `data/logg/` viser «Signalet er regnet i ettertid for N børsdager …»
     og like mange kall som før: én per aksje i lista og én for hovedindeksen.
   - `skjema_versjon` har raden for `0014_regnet.sql` (spørsmål 14):

     ```powershell
     uv run python -c "import sqlite3; t = sqlite3.connect('file:data/db/ose.db?mode=ro', uri=True); print(t.execute('SELECT versjon, fil, anvendt FROM skjema_versjon WHERE versjon = 14').fetchall())"
     ```

   - Kommandoen i punkt 1 med samme dato gir samme avtrykk og samme antall.
   - Kveldens rader har KI-tekst, som før.
3. **Så** den siste gjennomgangen av alle bildene på main (gruppens svar 14.11
   kl. 16:13), README-prøven og brukertest 2.

*Ført 2026-11-14 kl. 21:22 (tillegg 2), rett før flettingen:* kommandoen i punkt 1
med datoen `2026-11-14`, kjørt fra hovedkopien, lest med `mode=ro`, ga avtrykket
`665d4eff98e57820f399d874f233667388ca32470e25818741200da5124e4bf9` og 477
kveldsrader. sha256 av `data/db/ose.db` var lik før og etter kommandoen. Basen
stod da før 0014. Kopien av basen i punkt 1 er gruppens.
