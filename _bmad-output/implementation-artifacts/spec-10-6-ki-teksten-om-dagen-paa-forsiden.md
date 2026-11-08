---
title: 'Story 10.6: KI-teksten om dagen på forsiden, «Børsdagen kort fortalt»'
type: 'feature'
created: '2026-11-08'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '408b7494'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designutdrag-2026-11-08.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-9-ki-teksten-forklarer-det-siden-viser.md'
---

Skrevet 08.11 i instruksjonen kl. 14:05 (`docs/ai-prompts/2026-11-08.md`). Gruppen har sagt at Claude Code bygger etter forslagene i spesifikasjonene, og at de gås gjennom før flettingen (svaret 08.11 kl. 12:32). Storyen bygges derfor etter forslagene under, og spørsmålene står åpne til gruppen har svart.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Er uka med?** FR-607 (rettet 05.10) sier at det avgjøres her. *Forslag:* nei. Teksten gjelder én børsdag, og i en periode står «Perioden er uten KI-tekst. Teksten skrives for én børsdag om gangen.», som i utdraget §3.
2. **Hva er «antall per retning»?** *Forslag:* retningene blant aksjene som skilte seg ut, som eksempelteksten i utdraget: «4 skilte seg ut: 2 med positiv retning, 1 negativ og 1 blandet.» «Skilte seg ut» er det samme som på forsiden: signalstyrke på terskelen eller over (`del_i_to` i `markedsoversikt.py`).
3. **Hvilke bransjer får modellen?** *Forslag:* alle bransjer i lista med minst 2 aksjer med en endring den dagen, som bransjen i 10.2i (`MINST_I_BRANSJEN`), med hvor mange som steg og hvor mange som hadde en endring. Prompten ber om høyst to bransjer, og kontrollen sjekker hver bransje teksten nevner.
4. **Ukedagen.** Eksempelteksten sier «Hovedindeksen falt tirsdag». *Forslag:* grunnlaget har ukedagen som tekst fra en lukket liste, og kontrollen stopper en annen ukedag og ord som «i dag» og «i går», fordi teksten også leses senere.
5. **Faste former.** *Forslag:* som i 10.9: prompten gir én form for hvert faktum, og kontrollen leser tallene bare i formene, ved feltet sitt. Et tall utenfor formene stoppes.
6. **Promptversjonen.** *Forslag:* en egen prompt med versjonen `dag-1`, så teksten om dagen og teksten om én aksje ikke kan blandes i loggen (FR-605).
7. **Bryteren.** FR-601 sier at én bryter styrer begge KI-tekstene. *Forslag:* samme informasjonskapsel (`ose_ki`), med «Vis KI-tekst» ved overskriften, som i utdraget. Etter et trykk kommer man tilbake til oversikten ved delen. Innstillinger (8.10b) bruker den samme kapselen.
8. **Prikket strek.** Hjelpen sier «tall med prikket strek står i det modellen fikk». *Forslag:* hvert tall i en tekst som er vist, har prikket strek. Alle tallene er sjekket mot grunnlaget, ellers vises ikke teksten.
9. **Velg dag og Min liste.** *Forslag:* med «Velg dag» vises teksten for den dagen når raden finnes og grunnlaget stemmer. Min liste har ikke delen, fordi FR-607 gjelder markedsoversikten. I demoen finnes teksten bare for siste dag, som KI-teksten på aksjesiden.
10. **Prøvekjøringen.** *Forslag:* de 10 siste børsdagene i `ose.db`, lest med `mode=ro`. Bare antallene står i repoet (§57 i `malinger.md`), ikke tekstene (regel 16).

11. **Navnet «kort fortalt».** Story 8.20a tok bort «‹navn› kort fortalt» på aksjesiden, og `test_de_gamle_ordene_staar_ikke_igjen` forbyr «kort fortalt» i hjelpen, README-en og på sidene. Utdraget 08.11 §3 kaller delen «Børsdagen kort fortalt». *Forslag:* navnet fra utdraget, og testen godtar akkurat «Børsdagen kort fortalt».
12. **Hjelpen i tre setninger.** Utdraget har fem setninger bak «?», og hver hjelpetekst har høyst tre (story 8.0c, `test_hoeyst_tre_setninger_per_tekst`). *Forslag:* ordene fra utdraget, satt sammen til tre setninger.

## Intent

**Problem:** forsiden har tabellen, hovedindeksen og søylene, men ingen setninger om hele børsdagen (FR-607).

**Avgjørelsene:** story 10.6 i `epics.md` (02.10, rettet 05.10, tillegget 08.10 om lista som er aktiv), FR-601–FR-605 og FR-607 i `prd.md`, svaret 08.11 kl. 11:57 («Ollama i dag», prøvekjøringer på `ose.db` med `mode=ro`) og kl. 12:39 (som designforslaget), og §3 i `designutdrag-2026-11-08.md`.

## Slått opp 08.11 på `408b7494` (regel 3)

- **Loggen** har alt et emne for dagen: `Emne.dagen(dato)` i `src/kilogg.py` (svar 6 kl. 15:53). `SqliteKILogg` skriver og leser det som en aksje.
- **«Skilte seg ut»** er signalstyrke på terskelen eller over (`del_i_to` i `src/markedsoversikt.py`, `Parametre.terskel`, 2).
- **«N av M gikk bedre enn indeksen»** regnes av `sammenlign` i `src/hovedindeks.py`, med indeksens endring for dagen (`indeks_for_dagen` i `src/boersometer.py`). Forsiden bruker den samme.
- **Retningen på en aksje og på hovedindeksen** regnes av `bevegelse` og `_endringen` i `src/dagene.py`, etter endringen slik den vises.
- **Kontrollen for én aksje** (`kontroller` i `src/ki_kontroll.py`) stopper alt om bransjen, børsen og antall aksjer, så teksten om dagen trenger sin egen. Listene `RAAD`, `GJETNING` og `AARSAKER`, tallordene og mønsteret for enheter kan brukes som de er.
- **Bryteren** er kapselen `ose_ki` (`src/ki_visning.py`), og `/ki` sender bare tilbake til en aksjeside (`_TILBAKE` i `src/app.py`).
- **Demoen** har KI-tekstene i `src/demo_ki_tekster.json`, laget med `uv run python src/demo_ki.py`, med promptens avtrykk på hver rad.

## Delene

### A) Grunnlaget for dagen

En ren funksjon (`dagsgrunnlag` i `src/ki_dagen.py`) regner grunnlaget av vurderingene for dagen, kursene og hovedindeksen, for lista som er aktiv:

- `aksjer`: antallet aksjer i lista (FR-412, tillegget 08.10).
- `ukedag`: mandag til fredag (spørsmål 4).
- `hovedindeksen`: steg, falt eller uendret, når den kan regnes.
- `bedre_enn_indeksen` og `med_kurs`: «N av M» som på forsiden, når indeksen har en endring.
- `skilte_seg_ut`, `skilte_seg_ut_positiv`, `skilte_seg_ut_negativ` og `skilte_seg_ut_blandet` (spørsmål 2).
- `bransjer`: for hver bransje med minst 2 aksjer med endring, `steg` og `med_endring` (spørsmål 3).

Bare heltall og tekst fra lukkede lister. Ingen kurs, prosent, volum eller forholdstall (beslutningen 04.10).

**Ville feilet hvis:** grunnlaget fikk et desimaltall eller en kurs, eller sa 15 aksjer når lista hadde et annet antall.

### B) Prompten for dagen

Egen prompt med versjonen `dag-1` (spørsmål 6), med én form for hvert faktum, og reglene fra prompten for én aksje om råd, gjetning og årsaker. Avtrykket bindes til versjonen med en test, som for prompten for én aksje.

**Ville feilet hvis:** prompten ble endret uten ny versjon. Da ser to prompter ut som én i loggen (FR-605).

### C) Kontrollen for dagen (FR-603, alle fire punktene)

`kontroller_dagen` i `src/ki_dagen.py`:

1. **Retning.** Det teksten sier om hovedindeksen og retningene blant dem som skilte seg ut, skal stemme med grunnlaget. Mangler feltet, stoppes utsagnet.
2. **Tallene.** Et tall er lov bare i formene, ved feltet sitt, også skrevet med ord. Prosent, desimaltall og beløp stoppes.
3. **Råd.** Som for én aksje.
4. **Gjetning.** Som for én aksje, også årsakene.

Ukedagen skal være grunnlagets, og «i dag», «i går» og «i morgen» stoppes (spørsmål 4).

**Ville feilet hvis:** teksten nevnte et tall som ikke står i grunnlaget, eller kunne leses som et råd (kontrollpunktet i storyen).

### D) Teksten i hentingen

Hentingen lager teksten etter tekstene for hver aksje, med ett kall til modellen per børsdag (NFR-02), og skriver raden i `ki_logg` (FR-604, FR-605). Finnes raden, står den. Feilet modellen for en aksje samme kveld, kalles den ikke for dagen, og raden sier hvorfor. Siden lager aldri teksten.

**Ville feilet hvis:** modellen ble kalt to ganger for samme dag, eller siden kalte modellen.

### E) «Børsdagen kort fortalt» på forsiden

Under tabellen, som i utdraget §3 og §11 i utdraget 13.10. Overskriften med «?», merket «Laget av KI» og bryteren «Vis KI-tekst». Teksten vises bare når grunnlaget i raden er det samme som grunnlaget regnet av det siden viser (FR-607), og ikke stoppet av vakta (NFR-06). Under teksten: «Skrevet av ‹modellen› da kursene ble hentet.» Uten tekst står «Dagen er uten KI-tekst.», med en periode «Perioden er uten KI-tekst. Teksten skrives for én børsdag om gangen.», og med KI av «KI-teksten er slått av. Tabellen over viser bare det reglene har regnet ut.» Tallene har prikket strek (spørsmål 8).

**Ville feilet hvis:** teksten ble vist når grunnlaget ikke stemmer med siden, eller bryteren ikke slo av begge KI-tekstene.

### F) Hjelpen, README-en og `docs/hjelp.md`

Hjelpen bak «?» er de fire setningene i utdraget §3. `docs/hjelp.md` og README-en sier det samme (regel 19).

### G) Demoen og prøvekjøringen

Demoteksten lages med Gemma i Ollama, med samme vei som hentingen, i en egen fil `src/demo_ki_dagen.json`, og demokommandoen skriver den inn. Prompten prøves på de siste børsdagene i `ose.db`, lest med `mode=ro`, og bare antallet som besto og ble stoppet står i repoet (§57 i `malinger.md`).

## Grenser

- Ingen kall til EODHD utover kvotesjekken i regel 15. `data/db/ose.db` leses bare, med `mode=ro` (svaret kl. 11:57, med en Lagt til-linje under regel 22). Demobaser bare i midlertidige mapper.
- Ingen tekst fra den ekte versjonen i sporede filer (regel 16).
- Egen gren, PR, og stopp før flettingen.

## Bygget 08.11 (instruksjonen kl. 14:05)

Bygget på grenen `10-6-ki-teksten-om-dagen`, i worktreen `G74-lund-osen-10-6`, fra `408b7494`. Ingen migrasjon: raden har emnet `Emne.dagen`, som `ki_logg` har hatt siden 4.2.

- **Filene.** `src/dagsgrunnlag.py` (del A, uten `ki_` i navnet, fordi webserveren regner grunnlaget på nytt og aldri importerer KI-laget, AD-10), `src/ki_dagen.py` (del B, C og raden), `lag_ki_tekster` med `med_dagen` i `src/ki_tekst.py` (del D, satt i alle fire kallene i `fetch_prices.py`), `bygg_dagsvisning` i `src/ki_visning.py` og `_boersdagen` i `src/app.py` (del E), og `src/demo_ki_dagen.json` med `uv run python src/demo_ki.py --dagen` (del G).
- **Avvik fra delene.** Hjelpen er tre setninger (spørsmål 12). Bryteren `/ki` godtar nå også `/`, med perioden eller dagen, og sender tilbake til `#boersdagen-kort-fortalt`. Linja om at teksten om dagen venter, står sist i utskriften når Ollama ikke svarer, så resten av linja er som før.
- **Tester («Ville feilet hvis» i hver):** `tests/test_ki_dagen.py`. Antallet kall i `tests/test_ki_tekst.py` og `tests/test_ki_tjenestene.py` er ett høyere, fordi hentingen kaller modellen én gang for dagen.
- **Demoen.** Teksten ble laget med Gemma kl. 14:28 og besto (oppdiktede selskaper). Alle sju bildene i `docs/appen/` ble tatt på nytt med DevTools-protokollen i Edge uten vindu. Seks er byte for byte de samme, og oversikten ved 390 px er 3832 px høy med delen nederst. Demoteksten ble laget på nytt kl. 14:46, etter `ruff format`, som endret koden i promptens avtrykk, og ble den samme teksten.
- **Prøvekjøringen:** §57 i `malinger.md`, 10 av 10 besto.
- **Hele settet,** alene, uten Ollama og Docker Desktop, med 7,2 GB ledig minne: kl. 15:00:33–15:10:32, 4631 bestått, 24 hoppet over og 0 feilet. To kjøringer før det (14:35:47–14:45:08 og 14:48:53–14:58:21) ga 16 og 3 feil, som er rettet: antall kall i to tester til, ordlista for stilarket (bryteren på forsiden har sin egen klasse, `dagsbryter`), demotestene som teller radene, og «gikk bedre enn indeksen» i hjelpen, som testene for periodevalget ikke tillater på siden når indeksen mangler.

## Mutantene

Én per del, på `1c27113e`, med kopi før og sha256 mot HEAD etter. Alle sju ble fanget, og hver fil var lik HEAD etterpå.

| Del | Mutant | Fanget av |
|---|---|---|
| A | grunnlaget sier alltid 15 aksjer | 3 tester i `TestGrunnlaget` |
| B | linja om råd tatt ut av prompten | 3 tester, også `test_versjonen_foelger_teksten` |
| C | tallet ved feltet sjekkes ikke | 4 tester i `TestKontrollen` |
| D | modellen kalles for dagen selv om den feilet for en aksje | 3 tester |
| E | teksten vises uten at grunnlaget stemmer med siden | `test_grunnlaget_maa_stemme_med_siden` |
| F | hjelpen sier ikke at teksten ikke gir råd | `test_hjelpen_har_ordene_fra_utdraget_i_tre_setninger` |
| G | demoen skriver ikke inn teksten om dagen | 3 tester |

## Gjennomgangen 08.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Tre gjennomganger av `1c27113e`, i parallell etter hele settet og mutantene: Blind Hunter med bare diffen, Edge Case Hunter og Verification Gap med repoet. De kjørte snutter og enkeltfiler, ikke hele settet. Blind Hunter hadde 11 funn, Edge Case Hunter 14 og Verification Gap 11.

**Høy**
- *BH1, BH2, ECH2, ECH3, ECH4 og VG1, rettet.* Kontrollen stoppet bare ord fra en liste utenfor formene. «Hovedindeksen steg ikke fredag.», «Aksjene gikk opp fredag.», «Oslo Børs gikk opp fredag.» og «Det var en negativ dag.» besto. Nå kan resten av teksten, når formene er tatt ut, bare være «og», «men» og tegnsetting (`BINDEORD` i `ki_dagen.py`), som setningen om mønstrene i 10.9. Hvert eksempel fra gjennomgangene står i `test_bare_formene_og_bindeord`.
- *BH4, ECH1 og VG3 (høy og middels), rettet.* Teksten om dagen ble laget også i en henting der noen aksjer ventet på et nytt forsøk. Raden sto da med et grunnlag siden aldri regner, og dagen ble for godt uten tekst. Nå lages den først når hver aksje i lista har en rad for dagen (`_grunnlaget_for_dagen` i `ki_tekst.py`, `test_ikke_teksten_om_dagen_foer_alle_aksjene_har_en_rad`).

**Middels**
- *BH3, ECH5, ECH6 og VG2, rettet* med regelen over: bransjer utenfor formen, selskaper, «kraftig», «for andre dag på rad» og «flertallet» stoppes.
- *VG5, rettet.* Modellnavnet sto uten tjenesten, mot FR-602. Nå «Skrevet av gemma4:e4b (lokal) da kursene ble hentet.»
- *BH6 og VG6, rettet.* Hjelpen på siden sa «Modellen fikk bare dette» uten ukedagen, antallet aksjer og grensen for bransjene. Nå sier hjelpen og `docs/hjelp.md` det samme, ordrett, og testen sammenligner setningen.
- *VG4, rettet.* Ingen test for en valgt dag. Nå `test_velg_dag_viser_teksten_for_den_dagen`, med teksten for torsdagen før siste dag, og bryteren tilbake til dagen.
- *BH9, avvist.* `conftest.py` flytter `BASE_STI`, og dermed `demo_sti()`, til `tmp_path`.

**Lav**
- *Rettet:* ECH7 og ECH8 («1 aksje skilte seg ut», «av de 15 aksjene»), ECH10 og VG7 (tallene står med sifre, så hvert tall som vises, har prikket strek), ECH12 (uten `tilbake` går bryteren til `/` som før), ECH13 (utskriften når bare teksten om dagen venter), BH5 (en eldre dag uten raden stopper ikke steget), BH8 (terskelen fra `STANDARD`), BH10 (grunnen er tallet), BH11 (en feil i grunnlaget for dagen stopper ikke tekstene for aksjene), VG8 (Lagt til-linje i §57), VG9 (docstringen nevner alle ordene).
- *Ført:* BH7 og ECH11. Bryteren på forsiden beholder perioden og dagen, men ikke sorteringen. ECH9: «1 skilte seg ut med negativ retning» stoppes; prompten gir formen med kolon. ECH14: feilet hovedindeksen om kvelden og ble hentet neste kveld, sier grunnlaget på siden noe annet enn raden, og dagen er uten tekst under «Velg dag». VG10: at hentingen og siden bruker samme liste når den ikke har 15 aksjer, er bare testet i `dagsgrunnlag`; lista fra basen kommer i 2.11. VG11: utdraget sier «under Dine egne aksjer», som kommer i 2.12; til da står delen under tabellen.
- **Etter gjennomgangen:** hele settet alene kl. 15:22:02–15:31:42, 6,5 GB ledig minne: 4650 bestått, 24 hoppet over og 0 feilet.
