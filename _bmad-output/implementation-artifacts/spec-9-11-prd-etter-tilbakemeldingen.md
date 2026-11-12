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
| `prd.md` etter | 1 631 | 13 310 | 83 943 |
| `prd-endringslogg.md` | 1 611 | 20 132 | 129 621 |

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
