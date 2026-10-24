---
title: 'Story 10.2, 10.2e: prompten versjon 3'
type: 'feature'
created: '2026-10-24'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '153aba8'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

## Intent

**Problem:** KI-teksten i versjon 2 får bare fortegnet for de tre sjekkene, styrken og retningen. Den kan ikke si hvor lenge signalet har vært slik, eller hvordan dagen var på børsen.

**Beslutningene** (under story 10.1 og 10.2 i `epics.md`):
- *2026-10-21 kl. 22:57 og 23:51:* den nye promptversjonen får hvor lenge signalet har vært slik, retningen på hovedindeksen og børsometeret, og bare våre egne resultater. Ingen kurser, volumer, prosenter eller forholdstall, heller ikke tallene som står på siden. Teksten kan vise til tallene på siden uten å gjenta dem, og hvert tall i teksten kontrolleres mot grunnlaget.
- *2026-10-24 kl. 15:50:* versjon 3 bygges og flettes i kveld, etter uka med logget drift med versjon 2 (19.–23.10).
- *2026-10-24 kl. 16:15:* a) hvor lenge signalet har vært slik, er børsdager på rad med samme retning og styrke, til og med dagen; b) fra børsometeret: hvor mange aksjer i lista som steg og falt fra børsdagen før, og om bransjen til aksjen steg eller falt i snitt. Begge er fortegn og antall.
- *2026-10-16 kl. 23:51 (2):* en ny promptversjon flettes når den består minst like mange tekster som versjonen før, i en prøvekjøring på samme dags data, og ingen tekst gjetter på en årsak utenfor regelen.

## Approach

**a) Grunnlaget** (`src/ki_grunnlag.py`). `ki_grunnlag` får `dagen=`, et `Dagsbilde`, og grunnlaget får disse feltene i tillegg:
- `dager`: et heltall fra 1. Det er børsdager på rad bakover fra dagen, etter børskalenderen, der den lagrede vurderingen har samme retning og samme styrke. Rekka stopper ved en vurdering med annen retning eller styrke, eller ved en grunn. Den stopper også ved en børsdag uten rad, også før første lagrede vurdering, og der kalenderen slutter. Da får grunnlaget `dager_merke: "minst"`, fordi det ikke er kjent hvordan signalet var før.
- `hovedindeksen`: `steg`, `falt` eller `uendret`, etter fortegnet på endringen slik den vises (`avrundet(..., "endring")`). Endringen er den samme som `indeksendring` i `hovedindeks.py` gir den stiplede linja på forsiden. Feltet mangler når indeksen ikke har en rad for dagen, eller ingen rad for børsdagen før. Indeksen velges som i appen: OSEBX når basen har den, ellers den basen har (DEMIX i demoen). Valget flyttes fra `app.py` til `valgt_indeks` i `hovedindeks.py`, så begge bruker det samme.
- `aksjer_steg` og `aksjer_falt`: aksjene i lista med kurs for dagen og en rad før, som har endring over eller under null slik den vises. Endringen er den samme som i børsometeret (`endring_i_prosent` på de to siste radene). Uendret og uten data telles ikke.
- `bransjen`: `steg`, `falt` eller `uendret` for snittet av endringen til aksjene i lista i samme bransje, som i børsometeret. Fortegnet tas av snittet slik det vises. Feltet mangler når ingen aksje i bransjen har en endring.

Fortsatt ingen kurser, volumer, prosenter eller forholdstall. Grunnlaget har bare heltall og tekst fra lukkede lister, og `_kontroller` sjekker de nye feltene. `ki_tekst.lag_ki_tekster` leser seriene, indeksen og vurderingene fra basen og gir `dagen` for hver aksje. `dagen=None` gir grunnlaget fra versjon 2, slik testene fra 10.1 bruker det.

**b) Prompten** (`src/ki_prompt.py`): `PROMPTVERSJON = "3"`. Reglene forklarer de nye feltene med ord. Teksten kan vise til tallene på siden uten å gjenta dem. Avtrykket for versjon 3 står i `AVTRYKK` i testen, og avtrykkene for versjon 1 og 2 står.

**c) Kontrollen** (`src/ki_kontroll.py`, FR-603):
- Et tall er lov bare når det står i grunnlaget som et antall (`styrke`, `dager`, `aksjer_steg`, `aksjer_falt`), eller er et av regelens faste tall. Fortegnene er ikke antall, som før.
- Sier teksten at hovedindeksen eller bransjen steg, falt eller var uendret, skal det stemme med grunnlaget. Mangler feltet, stoppes et slikt utsagn.

**d) Demoen og prøvekjøringen:**
- KI-tekstene i demoen lages på nytt med versjon 3 (`uv run python src/demo_ki.py`). Bildene og avtrykkene følger med.
- Prøvekjøringen (§43 i `malinger.md`) går som i §34. Bare KI-steget (`lag_ki_tekster`) kjøres mot `data/db/ki-proeve-v3.db` for børsdagen 23.10, med den ekte klokka, fra et skript utenfor repoet.
- Kopien har radene med versjon 2 fra kveldshentingen 23.10. Utfallet av dem føres som sammenligning på samme dags data. Så slettes de i kopien, og bare i kopien, med utløseren `ki_logg_slettes_ikke` tatt bort og satt inn igjen, før KI-steget kjøres.
- sha256 for `data/db/ose.db` er den samme før og etter.

## Rettingen etter gruppens svar 24.10 kl. 21:49

Versjon 3 rettes på grenen og prøvekjøres på nytt, og flettes bare hvis færre enn tre tekster stoppes og ingen tekst sier feil om en sjekk eller om dagene (under story 10.2 i `epics.md`).

**a) Prompten** (`src/ki_prompt.py`): én sjekk omtales med navnet, som «interessen ga ikke utslag», og «ingen sjekk» brukes bare når styrken er 0. Hver sjekk beskrives slik fortegnet i grunnlaget er. «Minst» om dagene brukes bare når grunnlaget har `dager_merke`, og da alltid. `PROMPTVERSJON` står som «3», fordi versjon 3 ikke er flettet, og avtrykket i `AVTRYKK` er satt på nytt. Den første teksten til versjon 3 står på `c848ea6`.

**b) Kontrollen** (`src/ki_kontroll.py`, FR-603, under punkt 1):
- Et utsagn om én sjekk, med navnet og utslaget, skal stemme med fortegnet i grunnlaget. Det leses i formene «interessen ga et positivt utslag», «ga ikke (noe) utslag», «slo (ikke) ut», «trenden er positiv», i en liste som «bevegelse og interesse ikke ga noe utslag», og som «(ingen sjekk ga / ikke noe / et positivt) utslag på interessen». En liste over tankestrek leses ikke, så «ingen av de tre sjekkene – trend, bevegelse og interesse – ga et utslag» er styrken.
- «Ingen sjekk ga utslag på» en sjekk er et utsagn om den sjekken, ikke om styrken. «Ingen sjekk ga et positivt utslag», uten en sjekk etter, leses fortsatt som styrken.
- «Minst» og et ord om dagene i samme setning er lov bare når grunnlaget har `dager_merke`. Med merket stoppes et antall dager uten «minst». Dagene leses også i «i to børsdager», «har vært minst én børsdag» og «to børsdager med samme retning». «En dag» uten «i», «har vært», «minst» eller et ledd etter er et vanlig ord.
- Testene fra 10.2d med de 13 demotekstene fra versjon 2 (`tests/demo_ki_tekster_versjon_2.json`) er kjørt mot den nye kontrollen: ingen ble stoppet. Én form i `test_formene_om_en_sjekk_stoppes_ikke`, «… og bevegelsen ga et positivt utslag», stoppes nå, fordi bevegelsen er 0 i grunnlaget. Den står med trenden i stedet, som er 1.
- Mot tekstene fra §43 stopper den nye kontrollen 10 av 15: MOWI, ORK og SALM på interessen, DNB, FRO, VAR, TEL, GJF og DNO på «minst» uten merket, og MPCC på «Ingen sjekk ga et positivt utslag» (styrken). EQNR og AKRBP består nå.

**c) Demoen og prøvekjøringen:**
- KI-tekstene i demoen er laget på nytt (`uv run python src/demo_ki.py`, 22:01:46–22:02:09): 10 av 13 besto. KVST ble stoppet på «det tredje på rad» (punkt 2, dagene er 1), og LKSV og TROY på «minst» uten merket. De 10 som besto, er lest mot grunnlaget, og ingen sier feil om en sjekk eller om dagene. Ingen ny runde (FR-604).
- Fordi teksten for KVST ble stoppet, viser bildet av aksjesiden nå feltet for KI-teksten med «Ingen KI-tekst for denne dagen». Grafen slutter ved 1827 px, målt i Edge uten vindu, og bildet ble tatt på nytt med den høyden (`HOEYDE_PAA_AKSJESIDEN`, var 1872). Bildeteksten i README-en sier at teksten ble stoppet (regel 19).
- Prøvekjøringen står i §44 i `malinger.md`, mot kopien `data/db/ki-proeve-v3b.db`, laget med skallet på main kl. 21:52 før grenen. Tekstene står bare i kopien.

## Tredje forsøk etter gruppens svar 24.10 kl. 23:23

Ett forsøk til med versjon 3 søndag 25.10. Det flettes bare med 15 av 15 i prøvekjøringen og ingen tekst med feil (beslutningen 16.10 kl. 23:51, 2). Blir demoteksten for KVST stoppet igjen, viser bildet i README-en en demoaksje der teksten besto (under story 10.2 i `epics.md`).

**a) Ordlyden for dagene** (`src/ki_prompt.py`, `src/ki_kontroll.py`):
- `ordlyd_for_dagene` lager ordlyden av `dager` og `dager_merke`: «i dag for første gang» (1), «i N børsdager på rad» (2 eller flere), «i minst 1 børsdag» og «i minst N børsdager» (med merket). Grunnlaget er som før. Uten `dager` er det ingen ordlyd.
- Prompten har ordlyden på en egen linje etter opplysningene, «Ordlyden for dagene: …», og reglene sier at dagene bare nevnes med den, ordrett, og aldri med egne ord. «Minst» står ikke i reglene, bare i ordlyden, og i grunnlaget som verdien til `dager_merke`. `PROMPTVERSJON` står som «3», og avtrykket er satt på nytt, nå med ordlyden (`ORDLYDEN`).
- Kontrollen tar ordlyden ut av teksten og stopper det som står igjen om dagene: et antall dager, også riktig antall med egne ord, «minst» ved et ord om dagene, «på rad», «etter hverandre», «i trekk» og ordenstall ved «gang», «på rad» eller et ord om dagene, som «det tredje på rad». Det erstatter sjekken av antallet og «minst» fra kl. 21:49. Regelens vinduer og «en dag» som vanlig ord står som før.
- Tester som godtok dagene med egne ord etter kl. 21:49, er snudd til å kreve stopp, og docstringene sier det. De fire formene som ble stoppet i §44 er med i `TestOrdlyden`.
- Ordenstall ved «signalet», «det første signalet med denne retningen», stoppes også. Hullet ble funnet da demotekstene fra den første kjøringen 25.10 kl. 00:13 ble lest mot grunnlaget (NLYS, SLVP og KVST), før de ble committet. Tekstene ble lagt bort, og kommandoen ble kjørt på nytt med den rettede kontrollen (under b).

**b) Demoen:**
- KI-tekstene i demoen er laget på nytt (`uv run python src/demo_ki.py`). Første kjøring, 00:13:04–00:13:31, ga 13 av 13 bestått med kontrollen før rettingen over, og ble ikke committet. Andre kjøring, 00:16:07–00:16:18, med den rettede kontrollen: 10 av 13 besto. NLYS, SLVP og KVST ble stoppet på «det første signalet» (dagene i annen form). Grunnlaget var likt i begge kjøringene, og 12 av 13 tekster var ordrett like. Bare BRFE skilte seg: anførselstegnene rundt ordlyden falt bort. Ingen ny runde for en bedre tekst (FR-604).
- De 10 som besto, er lest mot grunnlaget. Ingen sier feil om en sjekk eller om dagene. Åtte har ordlyden i anførselstegn etter «i», som «i "i dag for første gang"» (HVDO, FJSB, TRHF, JGRD, LSTF, SGNT, LKSV og TROY). Det er dårlig språk, men ordlyden står ordrett, og kontrollen sjekker ikke språket (under «Åpent»).
- Teksten for KVST ble stoppet igjen, så bildet av aksjesiden i README-en viser nå BRFE (Brattfjell Energi), der teksten besto (svaret b): `docs/appen/aksjesiden-brfe-demo.png`, 1280 × 1872, målt i Edge uten vindu til bunnen av grafen. Målingen ga 1827 for KVST, som før, og 1872 for BRFE. Bildet av KVST er tatt bort. Bildeteksten, «Mappestruktur» (regel 19), stien, høyden og avtrykkene i `tests/test_docker.py` følger med.

**c) Prøvekjøringen** (§45 i `malinger.md`), mot kopien `data/db/ki-proeve-v3c.db`, laget med skallet på main kl. 00:04:21 før grenen, med samme sha256 som `ose.db`. Kjørt 00:20:45–00:20:56: 13 av 15 besto, 2 ble stoppet, og modellen feilet for 0. VAR og TEL ble stoppet på «det første signalet», dagene med egne ord. Hver tekst er lest mot grunnlaget, og ingen av de 13 sier feil om en sjekk eller om dagene. Ti setter ordlyden klønete inn i setningen (under «Åpent»). 13 av 15 er under kravet (15 av 15) i svaret kl. 23:23, så grenen flettes ikke. Med kontrollen fra a) består fortsatt alle 15 fra §34.

## Boundaries & Constraints

- Ingen kall til EODHD utover kvotesjekken i regel 15. `src/fetch_prices.py` kjøres ikke, og `data/db/ose.db` røres ikke (regel 22).
- Kopien ble laget med skallet på main kl. 20:11, før grenen. sha256 var lik `ose.db`: `e3184c07…f4a4`.
- Tekstene fra prøvekjøringen føres ikke i en sporet fil (regel 16).
- Stopp før flettingen hvis kontrollen stopper tre eller flere av tekstene i §43, eller hvis versjon 3 består færre enn versjon 2 på 23.10 (beslutningen 16.10 kl. 23:51, 2).

## Mutantene

Én om gangen med `-x`, med kopi før og sha256 mot HEAD etter:
- M1: dagene telt bare på retningen.
- M2: kontrollen slipper et tall utenfor grunnlaget.

**Utfallet** (på `1795981`, kl. 20:33, med sha256 lik HEAD etter hver):
- M1, `(rad.retning, rad.styrke) != …` byttet med `rad.retning != vurdering.retning`, ble fanget av `test_dagene_naar_styrken_byttes`.
- M2, alle heltallene i grunnlaget og tallene 4–12 lagt til de lovlige, ble fanget av `test_2_tall_og_mengder_som_ikke_er_i_grunnlaget[Femdagssnittet ligger lavere.]`.

**Rettingen etter svaret kl. 21:49**, én om gangen med `-x`, med kopi før og fila lik HEAD etter (`git hash-object` lik bloben på HEAD):
- M1, `grunner += _en_sjekk(…)` tatt ut, kontrollen uten sjekken av én sjekk: på `f42c9d7` kl. 22:07:15 og på `4a1d088` kl. 22:23:22, fanget begge ganger av `test_de_tre_tekstene_i_43_som_sa_feil_om_interessen` (MOWI).
- M2, `if not merket:` byttet med `if False:`, «minst» sluppet uten merket: på `f42c9d7` kl. 22:07:17 og på `4a1d088` kl. 22:23:25, fanget begge ganger av `test_minst_uten_merket_stoppes`.

## Prøvekjøringen

§43 i `malinger.md`, kl. 20:31:25–20:31:36: 12 av 15 besto, og 3 ble stoppet, mot 15 av 15 med versjon 2 på samme dag. Alle tre ble stoppet på «Ingen sjekk ga …» om én sjekk, som styrkeregelen fra 10.2a leser som styrke 0, og utsagnet var riktig. Etter instruksjonen kl. 20:00 (steg 4, tre eller flere stoppet) og beslutningen 16.10 kl. 23:51 (2) flettes ikke grenen før gruppen har avgjort det. Med kontrollen etter gjennomgangen (`6f34ebd`) er utfallet det samme: 12 besto.

KI-tekstene i demoen ble laget på nytt med versjon 3: 11 av 13 besto, mot 13 av 13 med versjon 2. NLYS ble stoppet på «skyldes» og TROY på «Ingen sjekk ga utslag på interesse».

**§44** (rettingen etter svaret kl. 21:49), kl. 22:05:12–22:05:22 mot `ki-proeve-v3b.db`: 11 av 15 besto, 4 ble stoppet og modellen feilet for 0. EQNR, AKRBP og FRO ble stoppet på «minst én børsdag» uten merket, og VAR på «det tredje på rad» (punkt 2, dagene er 1). Ingen av de 11 som besto, sier feil om en sjekk eller om dagene. Fire stoppet er over grensen i svaret kl. 21:49 (færre enn tre), så grenen flettes ikke. Med kontrollen etter gjennomgangen av rettingen (`4a1d088`) er utfallet det samme: §34 0 stoppet, §43 de samme 10, §44 de samme 4 med samme grunner, og demoradene får grunnene som er lagret.

MPCC i §43, «Ingen sjekk ga et positivt utslag», med styrke 2: utsagnet stemmer om fortegnene (ingen ga et positivt utslag), men bruker «ingen sjekk» der styrken ikke er 0, som prompten nå sier nei til. Det er ikke «utslag på» én sjekk, så kontrollen leser det fortsatt som styrken og stopper det (gjennomgangen av rettingen, BH12).

## Gjennomgangen

Gjennomgang 24.10 på diffen `df137b3..1795981` (commitene `ed68979` og `153aba8` på main og grenen), med Blind Hunter (BH, 15 funn), Edge Case Hunter (ECH, 12) og Verification Gap (VG, 3). Rettingene står i `6f34ebd`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH7 | Grenen gjør versjon 3 til standard og bytter demotekstene, men §43 sier at den ikke skal flettes | medium | **må avgjøres av gruppen:** grenen flettes ikke. Gruppen avgjør om versjon 3 rettes, eller legges bort |
| BH6 | «Ingen sjekk ga utslag på interesse» om én sjekk leses som styrke 0. Det stoppet alle tre i §43 og TROY i demoen, og utsagnet var riktig | medium | **må avgjøres av gruppen:** det er styrkeregelen fra 10.2a, og en retting endrer kontrollen etter prøvekjøringen |
| BH8 | Kontrollen sjekker ikke utsagn om én sjekk: tre tekster i §43 sier at interessen ga utslag der bare trenden ga det, og de besto | medium | **må avgjøres av gruppen**, og ført under «Åpent» |
| BH1, ECH6 | «Minst» om dagene sjekkes ikke: fem tekster i §43 og seks i demoen sier «minst» uten merket, og en tekst med merket kan si et eksakt antall | medium | **må avgjøres av gruppen:** en sjekk ville stoppe flere tekster i §43 og i demoen |
| BH9, VG2 | En feil ved lesingen av indeksen stoppet KI-teksten for alle aksjene | medium | patch: grunnlaget uten hovedindeksen, som forsiden, og `test_en_indeks_som_ikke_kan_leses_stopper_ikke_tekstene` |
| VG1 | Ingen test for valget av OSEBX når basen har en annen indeks | medium | patch: `test_hovedindeksen_er_osebx_ogsaa_med_en_annen_indeks` |
| BH3, ECH1 | «Alle aksjene» og «begge» ble lest som styrkens 3 og 2 | low | patch: egen ordliste for antallene, og «alle» og «begge» om aksjene stoppes |
| BH4, ECH3 | Perfektum, «har steget», «har sunket», «har gått opp», ble ikke lest | low | patch |
| BH5, VG3 | «Aksjen på børsen steg» ble lest som hovedindeksen | low | patch |
| BH2, ECH8, ECH12 | Tallene er lov som én mengde, og bare «N aksjer steg/falt» og «N (børs)dager på rad» knyttes til feltet sitt. «I sju dager» eller «og fem falt» sjekkes bare mot mengden | low | defer: punkt c) sier at et tall er lov når det står i grunnlaget. Ført under «Åpent» |
| ECH2 | Et antall uendrede aksjer stoppes alltid | low | defer: grunnlaget har ikke antallet |
| ECH7 | Sammensatte tallord over 20, som «tjueen», leses ikke | low | defer |
| ECH4, BH12 | Ord mellom feltet og verbet kan binde feltet til en annen setningsdel, som «Sammenlignet med bransjen falt aksjen» | low | defer: gir et stopp, ikke en feil som slipper gjennom |
| ECH5 | To mellomrom foran «Oslo Børs» | low | defer |
| ECH9 | Bransjen med bare aksjen selv | low | defer: står under «Åpent» fra før |
| BH10, ECH10 | Aksjene bruker forrige rad og indeksen forrige børsdag | avvist | som børsometeret (`bygg_rute`) og forsiden (`indeksendring`), slik spesifikasjonen sier |
| BH11 | Blandet med styrke 2 telles på rad selv om fortegnene bytter | avvist | gruppens svar kl. 16:15: samme retning og styrke |
| BH13, ECH11 | Uten OSEBX velges en annen indeks og kalles hovedindeksen | avvist | som forsiden og kursgrafen (`valgt_indeks`). Basen har bare OSEBX, og demoen DEMIX |
| BH14 | NLYS i demoen brukte «skyldes» igjen | low | ført i «Prøvekjøringen» over |
| BH15 | Tester for hullene over | low | testene er lagt til for funnene som er rettet |

### Gjennomgangen av rettingen

Gjennomgang 24.10, etter hele settet (ferdig 22:14:29) og før `4a1d088` (22:23), på diffen `c848ea6..f42c9d7` (commitene `4467688` og `43e7717` fra main, flettet i `08dcb3c`, og `fb363cd`, `c3dcfce` og `f42c9d7`), med Blind Hunter (BH, 16 funn), Edge Case Hunter (ECH, 15) og Verification Gap (VG, 3). Rettingene står i `4a1d088`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH4, ECH14 | «Ingen sjekk ga dessverre noe utslag på interessen» og «… på trenden, bevegelsen eller interessen» slo av styrken og ble lest halvt | medium | patch: styrken hoppes over bare når hele utsagnet leses med «ingen», og «eller» i lista |
| BH2 | «har ikke gitt utslag» ble ikke lest | medium | patch |
| BH3, ECH6 | Genitiv, «Trendens utslag var negativt», og «slo ut negativt» ble ikke lest | medium | patch. «ga et utslag som var negativt» er ikke lest: defer, under «Åpent» |
| ECH5 | Gradsord, «et sterkt positivt utslag», ble ikke lest | medium | patch |
| VG2 | «Interessen ga et positivt signal» og «negativt på bevegelse» ble ikke lest, og en test holdt den siste som bestått | medium | patch: formen i testen står med interessen, og den gamle stoppes i `TestGjennomgangenAvRettingen` |
| BH7, ECH2, ECH13 | Et antall dager uten «i» ble ikke lest, også med merket | medium | patch: bare «en», «én», «ett» og «ingen» og regelens vinduer trenger et ledd |
| BH6, ECH8 | «Minst» om sjekkene i en setning om dagene ble stoppet | medium | patch: «minst» må stå inntil to ord fra et ord om dagene |
| VG3 | Stoppede demorader ble ikke sjekket mot kontrollen | medium | patch |
| BH13 | Prompten nevner «minst» også når merket mangler, og 3 av 4 stopp i §44 er «minst» | medium | **må avgjøres av gruppen:** en endret prompt må prøvekjøres på nytt |
| BH15 | Bildet av aksjesiden i README-en viser feltet uten KI-tekst | medium | **må avgjøres av gruppen:** FR-604 gir ingen ny runde. Bildeteksten sier det. Grenen er ikke flettet, så main viser fortsatt bildet med teksten |
| BH4, ECH3 | «Verken … eller» ble stoppet | low | patch |
| BH5, ECH7 | «og interessen et negativt» ble ikke lest | low | patch. «det gjorde også interessen» og en liste mellom komma før verbet: defer |
| BH8 | «minst i fire børsdager» ble lest som eksakt | low | patch. «mer enn fire» med merket stoppes som eksakt |
| BH10 | Se BH1 | low | patch |
| BH11 | «fem» og «seks» tekster med «minst» i §43 | low | patch: seks (fem med «minst N børsdager» og TEL), i testene |
| BH12 | MPCC: «utsagnet var riktig» i §43, «styrken» nå | low | patch: forklart under «Prøvekjøringen» |
| BH16, VG1 | Tester for formene over, «har vært» og «etter hverandre» | low | patch: `TestGjennomgangenAvRettingen` |
| ECH1 | «i hele fire børsdager» | low | patch |
| ECH9 | «i  dag» med to mellomrom | low | patch |
| ECH12 | En sjekk som mangler i grunnlaget, ble ikke sjekket | low | patch: stoppes |
| BH9 | «Kursen falt i tre dager» leses som dagene | low | defer: gir et stopp, ikke en feil som slipper gjennom. Står i kommentaren |
| ECH10 | «fire børsdager på rad, minst» med merket stoppes | low | defer: gir et stopp |
| BH14 | «i ett børsdag» og ordstillingen etter «fordi» i demotekstene | low | defer: kontrollen sjekker ikke språket. Gruppen avgjør sammen med BH13 |
| ECH11 | Et grunnlag fra versjon 2 uten dagene stopper nå flere former om dagene | low | avvist: grunnlaget har ikke dagene, så et utsagn om dem er feil. De 13 demotekstene fra versjon 2 og de 15 fra §34 består |
| ECH15 | Kriteriet «ingen tekst sier feil» hviler på lesingen av 15 tekster, ikke på kontrollen | low | avvist: instruksjonen ber om at hver tekst leses mot grunnlaget, og det står i §44 |

Med dom medium er BH13 og BH15 ikke rettet. De må avgjøres av gruppen, og grenen flettes uansett ikke, fordi fire tekster ble stoppet i §44.

## Åpent

- `bransjen` for en bransje med bare aksjen selv sier det samme som aksjens egen endring. Børsometeret merker den «1 aksje». Grunnlaget har ikke det merket.
- *Lagt til 2026-10-24:* om versjon 3 skal rettes og prøvekjøres på nytt, eller legges bort: styrkeregelen og «Ingen sjekk ga» (BH6), utsagn om én sjekk (BH8) og «minst» (BH1, ECH6).
- *Lagt til 2026-10-24:* tall som står i grunnlaget, men om et annet felt, sjekkes bare der teksten har formene «N aksjer steg/falt» og «N (børs)dager på rad» (BH2, ECH8, ECH12).
- *Lagt til 2026-10-24 kl. 22:24:* versjon 3 rettet ble stoppet fire ganger i §44, og flettes ikke etter svaret kl. 21:49. Gruppen avgjør om prompten skal nevne «minst» bare med merket (BH13), og hva bildet av aksjesiden skal vise (BH15).
- *Lagt til 2026-10-24:* utsagn om én sjekk i formene «ga et utslag som var negativt», «det gjorde også interessen» og en liste mellom komma før verbet leses ikke (gjennomgangen av rettingen, BH5, ECH6, ECH7).
- *Lagt til 2026-10-25:* modellen setter ofte ordlyden i anførselstegn etter et ekstra «i», som «i "i dag for første gang"» (åtte av de ti demotekstene som besto). Ordlyden står ordrett, så kontrollen slipper den. Om prompten skal si hvordan ordlyden settes inn i setningen, avgjør gruppen.
