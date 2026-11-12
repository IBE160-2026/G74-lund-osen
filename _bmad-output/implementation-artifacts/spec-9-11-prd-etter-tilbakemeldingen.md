---
title: 'Story 9.11: PRD-en etter tilbakemeldingen fra faglærer 12.11'
type: 'docs'
created: '2026-11-12'
status: 'review'
route: 'dispatch'
baseline_commit: 'a93c668f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/tilbakemelding-prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
---

Skrevet 12.11 i et nytt vindu i hovedkopien, i worktreen `G74-lund-osen-9-11` på
grenen `9-11-prd-etter-tilbakemeldingen` fra `origin/main` (`a93c668f`).
Instruksjonen ble limt inn kl. 18:03 og føres i `docs/ai-prompts/2026-11-12.md`
når den står på main. Gruppens svar 12.11 kl. 18:00: en ny versjon med gjeldende
tekst, slik briefen fikk v8 i 9.6. Rådet anbefalte det.

Tilbakemeldingen ([`tilbakemelding-prd.md`](../planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/tilbakemelding-prd.md),
`29cf2874`) er lest hele: §1–§7, med de fem forbedringene 4.1–4.5, de mekaniske
funnene i §5 og de to refleksjonsspørsmålene i §7.

## Spørsmål til gruppen før flettingen

1. **Nummeret.** *Forslag:* 9.11, neste ledige i Epic 9 (9.10 er den siste i
   `epics.md` og `sprint-status.yaml`, og ingen gren bruker 9.11).
2. **Navnet på taggen.** Taggen står på `10265324`, den siste commiten som
   endret `prd.md`, som `prd-ferdig-2026-11-03` sto på sin. Den ble laget før
   noe ble endret og pushes med grenen. En tag flyttes aldri. *Forslag:*
   `prd-vurdert-2026-11-12` står.
3. **Status i frontmatteren.** Den sto `final`. *Forslag:* `aktiv`, fordi
   `prd.md` nå er levende som README-en (regel 4 tillater `aktiv`).
4. **«Under 5 minutter» står.** SM-1 har terskelen som før, og statusen sier at
   den ikke er nådd 10.11. Instruksjonen sier at UX ble endret etter testen
   10.11 (Vis meg rundt, hovedflyten først) og at brukertest 2 måler det. Slått
   opp (regel 3): 8.23 (funnene fra brukertesten) og 8.25 («Spill av
   omvisningen», med tilbudet første gang) er flettet 11.11. «Hovedflyten først»
   står ikke ordrett noe sted i repoet, og «brukertest 2» finnes verken som story
   i `epics.md` eller i `docs/brukertest.md`. *Forslag:* PRD-en nevner ikke
   brukertest 2 før den er planlagt; den føres som en egen story i Epic 8 når
   gruppen vil, og SM-1 får status etter den.
5. **Avvik mellom taggen og koden, som den nye teksten følger koden i.** Lest i
   koden 12.11, med fil og linje:
   - FR-412: «De 15 mest omsatte» som ferdig liste finnes ikke. Bransjelistene har
     de opptil 18 med høyest målt omsetning (`src/ferdige_lister.py`).
   - FR-203: aksjesiden nevner ikke NewsWeb (`_investorboble.html`). Kravet sier
     nå bare at appen ikke lenker til Euronexts nettsteder.
   - FR-201: det finnes ingen knapp «Velg dag»; det er et datofelt med «Vis
     dagen» (`_perioder.html`).
   - FR-101: Signalstyrke er ikke tom, men «–» med grunnen under. Hjelpeteksten
     `uten_styrke` siterer raden «| Signalstyrke | Tom |» som kilde, og
     `src/hjelpetekster.py` står bak avtrykkene til bildene (`test_docker.py`).
     Raden står derfor med en tredje kolonne som sier hva som vises, og `src/`
     er ikke endret.
   - NFR-01 og FR-413: valget `--med-bonuskvoten` (2.13b) bruker bonuskvoten ned
     til 200 igjen. Kravene sier «aldri bonuskvoten» med det ene unntaket
     avgjort 10.11 kl. 13:48.
   - FR-201: at «grafen sier det» når serien er kortere enn perioden, fant jeg
     ikke i koden. Kravet sier nå at det som finnes tegnes, med datoene på
     aksen.
   - FR-109, FR-110, FR-108, FR-407, FR-202 (søylene og båndet), FR-403, FR-409
     («ikke i lista»), FR-412 og FR-607 sto som «ikke bygget per 3.11», men er
     bygget. FR-107, FR-205, FR-207, FR-414, «Lær noe nytt» og høy, lav og kroner
     er ikke bygget.

   *Forslag:* teksten følger koden som over, og tabellen i §2 sier det.
6. **To nye åpne punkter i §8.** 26: en test som går gjennom alle malene etter
   rådord (NFR-06). I dag har hjelpen, omvisningen og enkelte sider hver sin
   test, men ingen går gjennom alle malene, slik 4.2 foreslår. 27: en misvisende
   KI-tekst med riktige tall (refleksjonsspørsmål 2). *Forslag:* begge står som
   åpne punkter, og 26 bygges som en egen story i Epic 9, ikke i 9.11, så denne
   PR-en bare endrer dokumenter og tester av dokumenter.
7. **Punkt 4 i §8** («Hvordan utledes eks.dato?») sto under «Utenfor v1».
   Metoden er bygget i 2.6 og står i FR-407. *Forslag:* §8 sier at punktet er
   besvart av metoden i FR-407; det står ordrett i endringsloggen.
8. **Assumptions Index (§5).** *Forslag:* ingen egen indeks. Antakelsene som står
   igjen, `[ANTAKELSE]` og `[FORELØPIG]` i FR-302 og FR-606A, er plan A i
   vedlegg A, og antakelsen i FR-501 var avkreftet 21.09.
9. **Kjerne eller ekstra.** Tabellen i §2 følger svaret 19.10 kl. 15:43: kjerne er
   det briefen v8 lover og det som var flettet da. Børsometeret, periodevalget i
   oversikten og KI-teksten om dagen står derfor som ekstra, selv om README-en
   lister dem under «Ferdig». *Forslag:* tabellen følger svaret 19.10, og
   README-en endres ikke.
10. **Navn i `.env` og feltnavn.** `OSE_KI_TJENESTE`, nøkkelnavnene, `close` og
    `adjusted_close` står i kravene, fordi de er det brukeren setter eller ser.
    *Forslag:* de står.
11. **Lenker i README-en.** Linja om PRD-en under «Dokumentene» og i «Til
    faglærer» lenker nå til tilbakemeldingen og endringsloggen (regel 17 og 19).
    `technology.md` fra faglærer (`a93c668f`) er ikke lenket. *Forslag:* den
    lenkes i en egen liten commit utenfor 9.11.
12. **Linja i CLAUDE.md.** Under regel 19: `prd.md` er levende som README-en, og
    historikken står i endringsloggen og taggen. *Forslag:* som skrevet.
13. **Flettingen.** *Forslag:* tidligst etter 8.26 i natt, med main flettet inn i
    grenen først, og hele settet på nytt etter det.
14. **Min liste har ikke eget FR** (BH5). Den er kjerne og står i ordlista, men
    har ingen kravtekst med konsekvenser. *Forslag:* et nytt FR, FR-111, i en
    egen story, fordi et nytt krav er en avgjørelse og ikke en omskriving.
15. **«De 15 mest omsatte» er borte uten en beslutning** (VG-B4). Taggen hadde den
    som ferdig liste i FR-412; koden har bare §3-lista og bransjelistene, og jeg
    fant ingen datert linje som tok den ut. *Forslag:* teksten følger koden, og
    gruppen avgjør om lista skal bygges eller strykes.
16. **Status for 3.4 i sprintstatusen** (VG12, regel 12). Tabellen i §2 sier
    «ja» for FR-411, fordi demoen er flettet, men `sprint-status.yaml` har
    `3-4-demoversjonen: review`. *Forslag:* 3.4 settes til `done` i en egen
    commit utenfor 9.11, eller tabellen sier «delvis».
17. **Pekere i koden til §8 og en Rettet-linje i prd.md** (ECH4). `src/app.py`,
    `aksje_uten_kurser.html`, `tilstand.py`, `vurderingsdata.py`, `boersdag.py`
    og `meldinger.py` viser til tekst som nå står i endringsloggen. `src/` er
    ikke endret, fordi `app.py` og malene står bak avtrykkene til bildene.
    *Forslag:* pekerne rettes neste gang filene endres av en annen grunn.
18. **Taggene i CI** (BH27). Testen som sjekker endringsloggen ordrett mot taggen,
    hoppes over i CI, fordi checkout ikke henter taggene. *Forslag:* `fetch-tags`
    i `tester.yml` i en egen story; lokalt kjører den.
19. **Overskrifter som sier mindre enn kravet** (BH10–BH12): «aksjedetaljen» i
    overskriftene, «De tre tilstandene» med fem i tabellen, og «Visningen når
    KI-laget er av» som også dekker på. *Forslag:* de står, fordi
    hjelpetekstene og eldre filer viser til overskriftene; ordlista forklarer
    «aksjedetaljen».
20. **SM-2 «fra første fungerende versjon»** (BH17). Bruken er ført fra 4.11.
    *Forslag:* terskelen står, fordi den er et suksessmål og en avgjørelse;
    statusen sier at brukslogga har én linje 12.11.

*Svar 2026-11-12 kl. 20:04 og 20:06 (gruppens svar):* alle 20 forslagene godtas
som bygget, med tre avgjørelser. Spørsmål 14: Min liste får sitt eget krav,
FR-111, med konsekvenser, i 9.11. Spørsmål 15: «De 15 mest omsatte» står i FR-412
og bygges i natt som egen story (tillegg 2). Spørsmål 16: tabellen står med ja for
FR-411, og 3.4 settes til done i dokumentrunden etter prøven på ny PC fredag.
PR-en flettes i natt, sist, etter 8.19 og lista. Rådet anbefalte alt utenom at
lista bygges, som gruppen valgte. Svarene er ført etter tillegg 1 og 2, limt inn
kl. 20:10, som føres i `docs/ai-prompts/2026-11-12.md`.

*Svar 2026-11-12 kl. 20:09 og 20:10 (gruppens svar):* «Lær noe nytt» kommer ikke
i v1, og de åtte kravene som sto som ekstra og ikke bygget, står som «senere»:
FR-101 (kronene), FR-107, FR-109 («Lær noe nytt»), FR-203 (høy, lav og kronene),
FR-205, FR-207, FR-414 og FR-608 («Sign in with ChatGPT»). Rådet anbefalte det.
Svaret er ført etter tillegg 3, limt inn kl. 20:12. Tabellen i §2 og kravteksten
sier det, §8 lister de åtte under «v1.1», og «De 15 mest omsatte» står som ekstra.

## Delene

### A) Taggen
`prd-vurdert-2026-11-12` på `10265324`, laget før noe ble endret.
- **Ville feilet hvis:** `prd.md` i taggen ikke var lik `prd.md` på `origin/main`
  før grenen (sjekket med `git diff --quiet` før taggen ble laget).

### B) `prd.md` med gjeldende tekst
Hvert FR og NFR med én gjeldende tekst og «*Konsekvenser:*», de samme ID-ene, UJ-1,
ordlista, tabellen «Kjerne, ekstra og senere», SM-1–SM-9 med krav, og vedlegg A.
Gamle ankre står med `<a name>` der en overskrift er endret. Tekstene
`src/hjelpetekster.py` siterer, står ordrett.
- **Ville feilet hvis:** se testene under.

### C) `prd-endringslogg.md`
Alle de daterte linjene ordrett, ordnet etter krav og dato, laget av et skript
som sjekket hver bit mot taggen, med tabellen over tilbakemeldingen øverst,
kommentaren om status fra frontmatteren og hele §8 slik den sto.

### D) Resonnementet
Avsnittene som ikke er krav, står ordrett i §13 i `begrunnelser.md`. Diffen mot
taggen (regel 13) gikk avsnitt for avsnitt: det som manglet i både `prd.md` og
endringsloggen, er enten skrevet om i den nye teksten, flyttet til §13, eller
foreldet og står i taggen. Ni setninger ble lagt tilbake i `prd.md` etter diffen
(FR-603, FR-604, FR-408, FR-409, FR-702, FR-706, NFR-01 og «Drift» i §7).

### E) Navnene som gikk ut av kravene (4.4)
Tabellen under story 9.11 i `epics.md` har navnene og commitene fra kravene i
taggen som ikke sto i arkitekturen eller `epics.md` fra før.

### F) Testene
`tests/test_prd_9_11.py`, og de tre testene i `tests/test_periodevalget_oversikten.py`
som leste de daterte linjene i `prd.md`, leser dem nå i endringsloggen.

## Grenser

Ingen API-kall utover kvotesjekken i regel 15. `src/` er ikke endret.
`data/db/ose.db` røres ikke. Lærerens filer, `_privat/` og de andre worktreene
røres ikke.

## Lengden

Målt med `wc -l -w -c`:

| Fil | Linjer | Ord | Byte |
|---|---:|---:|---:|
| `prd.md` i taggen | 2 264 | 28 752 | 185 850 |
| `prd.md` etter, før gjennomgangen | 1 631 | 13 310 | 83 943 |
| `prd.md` etter triagen | 1 672 | 13 777 | 86 612 |
| `prd-endringslogg.md` etter triagen | 1 616 | 20 154 | 131 383 |

## Stikkord til refleksjonsrapporten (§7 i tilbakemeldingen)

Gruppen skriver rapporten selv. Stikkordene er hentet fra det denne storyen så.

**1. En datert linje i stedet for å skrive om kravet: hva ga det, og hva koster
det leseren?**
- Ga: sporbarhet (når, hvem og hvilket svar), og at et mål som ble gitt opp, sto
  som gitt opp, ikke myknet opp (§7 «Drift», som faglærer trakk fram). Regel 5
  og 13 gjorde det til en vane.
- Ga: tester kunne feste seg til linjene (tre tester i
  `test_periodevalget_oversikten.py` leste dem).
- Kostet: 275 forekomster av «Rettet» og «Lagt til», 2 264 linjer og 28 752 ord.
  Første setning var ofte foreldet, som «fast i v1» i FR-201.
- Kostet: «ikke bygget per 3.11» sto igjen ved ni krav som var bygget 12.11. En
  datert statuslinje blir feil uten at noen skriver en ny.
- Etter: 1 631 linjer og 13 310 ord i `prd.md`, og historikken i
  endringsloggen. Prisen er at den som vil se hvorfor, må åpne én fil til.

**2. FR-603 sier «Kontrollen er grov». Hvordan oppdage en misvisende tekst med
riktige tall, og kan det skrives som en testbar konsekvens?**
- Kontrollen ser ord og tall, ikke mening. Punkt 1 ble utvidet til utsagn om én
  sjekk, hovedindeksen og mønstrene, men bare der teksten sier det direkte.
- En samling håndskrevne misvisende tekster med riktige tall, som testdata: hvor
  mange stopper kontrollen? Det kan skrives som en konsekvens med et tall, men
  tallet ville trolig vist at kontrollen ikke klarer det.
- En brukertest der personen forklarer signalet etter å ha lest bare KI-teksten,
  sammenlignet med regelforklaringen.
- En annen modell som dommer er KI som kontrollerer KI, og bryter med
  «regler regner».
- `malinger.md` §19 har tekstene fra prøven som viste feil tall skrevet med ord.

## Bygget 12.11

Commitene `409f81f0` (spesifikasjonen og storyen), `1ecd7213` (omskrivingen) og
`d38e1101` (CLAUDE.md), og rettingene etter gjennomgangen i commiten etter dem.

## Mutanten

Én mutant: «*Konsekvenser:*» ble fjernet fra FR-108 i en kopi av `prd.md` på HEAD
`d38e1101`. `test_hvert_krav_har_konsekvenser` feilet (1 feilet, 9 bestått).
Kopien ble lagt tilbake, og sha256 for fila var lik `git show HEAD:` etterpå
(`cbd4a583…`), med ren arbeidskopi.

## Gjennomgangen 12.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Fire uavhengige lesere: Blind Hunter leste bare de endrede filene, Edge Case
Hunter hele repoet, og Verification Gap gikk krav for krav mot taggen og koden, i
to deler (§1–4.2, og 4.4–vedlegget). 27 + 8 + 13 + 12 funn.

### Triage

**Rettet i prd.md:**
- BH1 og VG-B1 (middels): konsekvensen i NFR-06 var usann. Malene sier «ikke et
  råd» og har notatene om tenkte kjøp og salg. Den sier nå hva testene sjekker.
- BH2: FR-602 nevner at visningen har en egen, kortere liste. FR-603 viser til
  lista i kontrollen.
- BH3: FR-604 skiller en modell som feiler for én aksje fra en lokal modell som
  ikke svarer i det hele tatt.
- BH4: MA50 fra første punkt gjelder 6 mnd. Med 1 år begynner linja etter 50 dager.
- BH5 (delvis): setningen om det som er uten FR. Min liste er spørsmål 14.
- BH6 og VG3: kronene står i FR-101 med regelen, uten byggestatus.
- BH7: 16 kall i begrunnelsen for FR-401.
- BH8: «sensuren» i FR-411.
- BH9: §3 sier «sektor», kravene «bransje».
- BH13 (delvis): punkt 23 og AD-8 er ute av kravteksten. Henvisningene til
  reglene i `CLAUDE.md` står, fordi de er krav til repoet.
- BH14: «Ikke bygget (§2)» er ute av kravene; tabellen i §2 bærer statusen.
- BH15: FR-608 sier at malen gir KI av for en ny bruker.
- BH16 og VG-B7: SM-1 har FR-402, FR-602 og NFR-03, og SM-8 har FR-607.
- BH18 (delvis): FR-408 har unntaket for tom base.
- BH19, BH21: ordlyden.
- VG1: 6 mnd fram til dagen, med dagen merket, i FR-201.
- VG2: datoen i overskriften er den eldste.
- VG4, VG5, VG8, VG13: konsekvensene i FR-106, FR-105, FR-108 og «Hvor gamle
  dataene er».
- VG6: grafen merker justeringsdagene i perioden, og teksten teller siste år.
- VG7: rammen «Signalet forklart» etter grafen.
- VG9: 503, demo uten base og hull i serien i FR-204.
- VG10: tilbudet heter «Spill av omvisningen».
- VG11: tickeren, «Lær noe nytt», høy og lav ikke i grafen, gul ramme, norsk tid
  i FR-107, og grensene i FR-205.
- VG-B2: §6 sier at lista over Oslo Børs er EODHDs, lest av koden.
- VG-B3: grunnlaget i FR-607 slik `dagsgrunnlag.py` har det.
- VG-B5 og VG-B6: SM-8 med modell og promptversjon 3, og at 0 stoppet er et
  varsel etter motmålet; brukslogga har én linje.
- VG-B8: unntaket i FR-413 og NFR-01 gjaldt kjøringen 10.11.
- VG-B9: definisjonene i FR-606A.
- VG-B10: bildene i demoen lages fra testdata.
- VG-B11: «resultat» står ikke i lista over årsaker.
- VG-B12: kveldsjobben kjører commiten main hadde ved midnatt.

**Rettet i testene og endringsloggen:**
- BH23 og ECH1 (middels): endringsloggen har «Endringer etter 12.11» nederst, og
  tellingen og kontrollen mot taggen gjelder bare delen fra taggen. CLAUDE.md sier
  hvor nye linjer føres.
- BH24 og ECH7: en test for de andre daterte merkene, storynummer, commiter,
  «bygget per» og navn utenom gruppelinja.
- BH25: konsekvensen kan ikke være tom, og UJ-1 og ordlista testes.
- BH26: tabellen i §2 og FR-ID-ene må være like; FR-605A er ute av raden.
- ECH2: lenkesjekken tar ikke med `tilbakemelding-prd.md#`.
- ECH3: tabellradene strippes før de splittes.
- ECH5: innledningen sier at rekkefølgen følger den første datoen i linja.
- ECH8: setningen i story 9.11 er tydeligere.

**Ikke rettet, med grunn:**
- BH10–BH12, BH17, BH27, VG12, VG-B4 og ECH4: spørsmål 14–20.
- BH20 (lav): regel 21 krever hardt mellomrom i det sidene viser. Dokumentene har
  desimalkomma, og eksemplet i FR-706 er sitert fra taggen.
- BH22 (lav): 51 dager er forklart i FR-101 og FR-204.
- ECH6 (lav): ankeret `utenfor-v1` er dobbelt, som i taggen. Ingen lenke bruker
  `#utenfor-v1-1`.
- BH18, resten (lav): «Ukentlig» i SM-3 er gruppens frist.

Ingen funn på middels eller over står åpne (regel 25).

**Lukket med svaret 12.11 kl. 20:04 og 20:06:**
- BH5: FR-111 er skrevet, med konsekvenser, og står som kjerne og bygget i §2
  (spørsmål 14).
- VG-B4: «De 15 mest omsatte» står i FR-412 og i §2 som ekstra, ikke bygget, til
  storyen fra tillegg 2 er flettet (spørsmål 15).
- VG12: tabellen står med ja for FR-411; 3.4 settes til done etter prøven fredag
  (spørsmål 16).
- BH10–BH12, BH17, BH27, ECH4 og resten av spørsmålene: forslagene er godtatt som
  bygget. BH27 (taggene i CI) og punkt 26 (testen av alle malene) bygges i 9.12.

## Språkrunden (tillegg 5)

Gruppens ønske 12.11 kl. 20:21 om en nøye språkgjennomgang, og svarene kl. 20:40.
Rådet anbefalte det. Tillegget ble limt inn kl. 20:43 og føres i
`docs/ai-prompts/2026-11-12.md`. Runden er gjort på grenen før steg 2 i tillegg 1.

**Lengden**, målt med `wc -l -w -c`:

| `prd.md` | Linjer | Ord | Byte |
|---|---:|---:|---:|
| Før språkrunden (`3ae521b4`) | 1 721 | 14 205 | 89 050 |
| Etter språkrunden og rettingene etter gjennomgangen | 1 831 | 14 698 | 93 025 |

Teksten ble ikke kortere i ord, selv om tillegget ba om det. Den ble om lag
3 % lengre. Delte setninger gjentar subjektet, og hver konsekvens står nå på sin
egen linje. Kodeordene er også erstattet av lengre vanlige ord: `close` er blitt
«sluttkursen», og `adjusted_close` er blitt «den justerte sluttkursen».
Etter runden er ingen setninger i løpende tekst over 30 ord.

**Eksempler på endringene:**
- FR-102, før: «et klikk på Endring gir størst oppgang først, og et nytt klikk
  størst nedgang først». Etter: «Et klikk på Endring gir den største oppgangen
  først, og et nytt klikk den største nedgangen først.»
- FR-101, før: «| Sluttkurs | `close` for siste børsdag |». Etter: «| Sluttkurs |
  Sluttkursen for siste børsdag |». Raden med `close` står i ordlista, fordi
  hjelpetekstene siterer den.
- FR-203, før: «lenken til investorsiden har `target="_blank"`». Etter: «Lenken
  til investorsiden åpnes i en ny fane i den ekte versjonen.»
- FR-204: kolonnen «Svar» med 200, 404 og 503 heter nå «Hva brukeren får», med
  «Aksjesiden», «Siden finnes ikke» og «En feilside».
- §4.6, før: «EODHD spørres derfor ikke før tallene sendes». Etter: «Derfor
  trengs ikke en egen tillatelse fra EODHD».
- Forklaringen av justert og ujustert sluttkurs står i ordlista. FR-101, FR-407
  og FR-202 viser dit.
- Punkt 22 i §8 har fristen «Før innleveringen» (svaret kl. 20:40).

**Gjennomgangen med Blind Hunter**, krav for krav før og etter, og triagen:
- BH1 (middels): NFR-08 gjaldt bare én vei etter runden. Rettet: «Mangler den
  ene av sluttkursen og den justerte sluttkursen, brukes ikke den andre i
  stedet.»
- BH2 (middels): 400 i konsekvensen i FR-111 var falt ut. Den er tatt inn igjen.
- BH3 og BH8 (lav): FR-104 sier «Der står også», og FR-401 sier «Unntaket fra
  sperren».
- BH4 og BH5 (lav): grunnen er tatt inn igjen i FR-406, FR-101 og FR-407.
- BH6 (lav): i «Kort fortalt» står nå «lagres, regnes aldri på nytt og
  etterfylles ikke». Tillegget ba om «regnes aldri på nytt», og «etterfylles
  ikke» er beholdt.
- BH7 (lav): ordlyden i FR-203 stemmer med koden, som en agent leste 12.11. Ingen
  endring.
- BH9 (lav): åtte klossete setninger er skrevet om.
- BH10 (lav): `lang="no"` står igjen i parentes i NFR-05.

Ingen funn på middels eller over står åpne (regel 25).
