---
title: 'Story 10.2, 10.2e: prompten versjon 3'
type: 'feature'
created: '2026-10-24'
status: 'done'
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

## Fjerde forsøk etter gruppens svar 25.10 kl. 00:50 og 00:51

Gruppen ville prøve igjen (kl. 00:50). Modellen får ikke dagene og nevner dem ikke, og appen skriver dagene selv i en setning rett under KI-teksten på aksjesiden. Det endrer hvem som skriver dagene i svarene 21.10 kl. 22:57 og 23:51, og tellingen i svaret 24.10 kl. 16:15 a) står. Flettes bare med 15 av 15 og ingen tekst med feil (under story 10.2 i `epics.md`).

**a) Modellen** (`src/ki_grunnlag.py`, `src/ki_prompt.py`, `src/ki_kontroll.py`):
- Grunnlaget har ikke `dager` eller `dager_merke`. `Dagsbilde` teller dem fortsatt (`tell_dagene`), men `ki_grunnlag` legger dem ikke inn, og et grunnlag med dem avvises. Resten av grunnlaget står: fortegnene, styrken, retningen, hovedindeksen, antallet aksjer som steg og falt, og bransjen.
- Prompten forklarer ikke dagene, og ordlyden fra tredje forsøk er tatt bort (`ordlyd_for_dagene`, `ORDLYDEN`). Reglene sier: «Ikke si hvor lenge signalet har vart, om det er nytt, eller om det er første gang. Siden sier det under teksten.» `PROMPTVERSJON` står som «3». Avtrykket dekker reglene, merket og `lag_prompt` og er satt på nytt.
- Kontrollen stopper dagene i enhver form, uansett grunnlaget: et antall dager, «minst» ved et ord om dagene, «på rad», ordenstall og «for første gang», og ord som «fortsatt», «lenge», «uker» og «nytt signal». Rettingene fra gjennomgangen 25.10 for «andre», «i dag», «1. Dagen» og regelens vinduer står.
- Testene som godtok ordlyden eller et antall dager, er snudd eller tatt bort, og formene fra §44 og §45, blant dem VAR og TEL, stoppes i `TestDageneStoppes`.

**b) Setningen om dagene og demoen** (`src/dagene.py`, `src/app.py`, `src/templates/aksje.html`):
- `tell_dagene` er flyttet fra `ki_grunnlag.py` til den nye modulen `src/dagene.py`, fordi webserveren ikke importerer noe fra `ki_*` (AD-10, `test_webserveren_importerer_ingen_modell_heller_ikke_under_en_forespoersel`). `setning_om_dagene` lager setningen: «Signalet er slik i dag for første gang.», «Signalet har vært slik i N børsdager på rad.», «Signalet har vært slik i minst 1 børsdag.» og «Signalet har vært slik i minst N børsdager.», med tallet etter regel 21.
- For en tidligere dag valgt med «Velg dag» passer ikke «i dag», så setningen for 1 dag er da «Signalet ble slik denne dagen for første gang.» Den ordlyden er ikke gitt av gruppen og står under «Åpent».
- *Rettet 2026-10-25 kl. 13 (gjennomgangen, BH2):* ordlyden i de to punktene over gjelder ikke lenger. Gruppens svar kl. 12:12 og 12:19 under «Valg» tok ut «for første gang» og ga ordlyden for en dag som ikke er i dag.
- Aksjesiden viser setningen rett under KI-feltet og over bryteren, også når KI er av, teksten er stoppet, modellen feilet eller det ikke er noen rad. Uten en vurdering for dagen står den ikke. Tellingen leser vurderingene for aksjen fra basen (AD-3, AD-10), i demoen og i den ekte versjonen.
- KI-tekstene i demoen er laget på nytt, 01:09:25–01:09:44: 13 av 13 besto, og ingen nevner dagene. Hver er lest mot grunnlaget, og ingen sier feil om en sjekk. Bildet viser fortsatt BRFE, der teksten besto, nå med setningen, 1280 × 1934, målt i Edge uten vindu (var 1872). README-teksten under bildet, høyden, `src/dagene.py` i filene bak aksjesiden og avtrykket følger med.
- `test_ma_vinduet_kommer_fra_parametre` tar KI-feltet ut før den ser etter «de siste 50 børsdagene», fordi den nye demoteksten for BRFE forklarer regelen med det faste tallet.

**c) Prøvekjøringen** (§46 i `malinger.md`), mot kopien `data/db/ki-proeve-v3d.db`, laget med skallet på main kl. 00:56:04 før grenen, med samme sha256 som `ose.db`. Kjørt 01:15:01–01:15:17: 15 av 15 besto, 0 ble stoppet, og modellen feilet for 0. Hver tekst er lest mot grunnlaget. Ingen sier feil om en sjekk, og ingen nevner dagene. Med kontrollen fra a) består fortsatt alle 15 fra §34.

## Valg

Gruppens svar 25.10 kl. 11:04:

- **a) Lesingen på aksjesiden.** Setningen om dagene leser vurderingene for aksjen med ett kall, fra første dato til dagen siden viser. `test_siden_leser_en_gang_per_maaned` godtar nøyaktig det ene kallet i tillegg til måneden i historikken, og feiler fortsatt hvis siden leser dag for dag eller gjør mer enn ett kall til.
- **b) Ordlyden for en valgt dag.** Med «Velg dag» står ordlyden fra fjerde forsøk, som «Signalet ble slik denne dagen for første gang.», fordi datoen står øverst på siden. Punktet under «Åpent» er dermed avgjort.

Gruppens svar 25.10 kl. 12:12 og 12:19, på funnene fra gjennomgangen kl. 11:

- **a) Uten «for første gang».** Tellingen gjelder dagene på rad (BH2, ECH7), så setningen for 1 dag er «Signalet ble slik i dag.», og for en dag som ikke er i dag «Signalet ble slik denne dagen.». Tellingen fra svaret 24.10 kl. 16:15 a) står. Det endrer ordlyden fra svarene kl. 00:51 og 11:04 b).
- **b) «Fortsatt», «lenge» og «uke»** stoppes som før, fordi modellen ikke vet hva som var før (ECH4, BH14). Kontrollen er ikke endret.
- **c) «Denne dagen»** gjelder alle dager som ikke er i dag, også i helga og før kveldshentingen, ikke bare med «Velg dag». Siden gjorde det allerede etter rettingen av BH1 (`21cebff`), og testene sier det nå.
- **d) Flere dager og «minst» en dag som ikke er i dag:** «Denne dagen hadde signalet vært slik i 4 børsdager på rad.» og «Denne dagen hadde signalet vært slik i minst 12 børsdager.» (BH5). Entall står ikke i svaret. Det er utledet av d) og av entall for i dag: «Denne dagen hadde signalet vært slik i minst 1 børsdag.»
- **e) Retningen Ingen:** setningen står som den er, fordi «slik» viser til retningen rett over (ECH10).

`src/dagene.py` har ordlyden fra a), c) og d). README-en, `docs/hjelp.md` og `src/hjelpetekster.py` siterer ikke setningen, så de er ikke endret. Bildet av BRFE er tatt på nytt, 1280 × 1934, og viser «Signalet ble slik denne dagen.».

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

*Lagt til 2026-10-25 kl. 13 (flettet i `0c2568660e1e`):* ordlyden etter gruppens svar kl. 12:12 og 12:19, én mutant med `-x`, med kopi før og fila lik HEAD etter (samme blob): «Signalet har vært slik i N børsdager på rad.» for en dag som ikke er i dag, på `7d61aaf` kl. 12:45:00, fanget av `test_setningen[4-False-True-…]`. Mutantene i tredje og fjerde forsøk og for lesingen står i Utført-linjene i dagsfila for 25.10.

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

### Gjennomgangen 25.10

Gjennomgang 25.10, etter hele settet (00:22:52–00:30:02), på diffen `cfceb42..d5a3476` på grenen (`0830edd`, `8627536` og `d5a3476`) og `6fc31fd` på main, med Blind Hunter (BH, 13 funn), Edge Case Hunter (ECH, 12) og Verification Gap (VG, 10), hver for seg og uten å endre noe i repoet. Rettingene står i `c6d0c85`. Med den rettede kontrollen er utfallet det samme: §34 15 bestått, §43 13 stoppet, §44 14 stoppet, §45 de samme 13 bestått og VAR og TEL stoppet, og demoradene får svaret som er lagret. Mutanten (dagene sluppet i annen form) ble kjørt på nytt på `c6d0c85` kl. 00:40:24 og fanget igjen av `test_dagene_byttet_med_styrken`.

| # | Funn | Dom | Rute |
|---|---|---|---|
| ECH1, BH3 | «andre … i dag» ble lest som dagene, også med grunnlaget fra versjon 2 | high | patch: «i dag» er ikke et ord om dagene i `_DAGENE_I_ANNEN_FORM` |
| ECH5 | Et galt antall dager lik regelens vinduer, «holdt seg 20 børsdager», slapp gjennom | high | patch: vinduene godtas uten ledd bare når setningen nevner vinduet, snittet, medianen eller trenden. «De siste 20 dager» står: defer |
| BH1, ECH7 | Ordlyden nektet, «ikke vært slik i dag for første gang», slapp gjennom | high | patch: «ikke» eller «aldri» inntil tre ord foran ordlyden stoppes |
| BH2, ECH6 | Dagene uten tall: «flere ganger», «nok en gang», «i går», «siden mandag», «flere dager», «handelsdager», «det første med denne retningen» | medium | patch. «Fortsatt», «lenge», «uker» og «førstegangssignal» leses ikke: **må avgjøres av gruppen**, under «Åpent» |
| ECH2, VG4 | «andre» og «annen» som «other», «andre dager», «en annen dag», «andre signaler», ble stoppet | medium | patch: ordenstall bare ved «gang» og «på rad» |
| ECH3 | «styrke 1. Dagen …» ble lest som ordenstall | medium | patch: «1.» er ordenstall bare foran liten bokstav |
| BH4 | Ordlyden godtas også i en annen setning, «Hovedindeksen steg i dag for første gang» | medium | **må avgjøres av gruppen**: kontrollen fanger ord, ikke mening (FR-603). Under «Åpent» |
| VG1 | Ingen test for at prompten og kontrollen bruker samme ordlyd | medium | patch: `test_prompten_og_kontrollen_bruker_samme_ordlyd` |
| VG2, BH7 | Avtrykket dekket malene, ikke koden som velger ordlyden | medium | patch: avtrykket dekker `ordlyd_for_dagene` og `lag_prompt`, og er satt på nytt |
| BH6 | `ordlyd_for_dagene` hadde «minst» som tekst | medium | patch: `MINST` fra `ki_grunnlag` |
| BH5 | Like grunner kan komme to ganger | medium | defer: gir bare en grunn til, ikke et annet svar |
| VG3, BH12 | «etter hverandre» uten tall, ordenstall fra «femte», «4.», og «i minst fire børsdager på rad» hadde ingen test | medium | patch |
| VG6 | Ordlyden i rette anførselstegn hadde ingen egen test | low | patch |
| VG7 | Ingenting sjekket at aksjen på bildet besto | low | patch: `test_bildet_viser_en_aksje_der_teksten_besto` |
| BH8, VG5 | Parameteret `symbol` gjorde ingenting | low | patch: én test |
| BH10 | Setningen fra kl. 21:49 i docstringen sto som gjeldende | low | patch: merket som erstattet |
| VG9 | `0830edd` ble endret med `--amend` før push, så forfattertiden (00:12) er før rettingen | low | Utført-linja bruker tiden commiten fikk (00:16) |
| ECH9, VG4 | «på rad» og «etter hverandre» om noe annet stoppes | low | defer: gir et stopp, ikke en feil som slipper gjennom |
| ECH8 | «første gang» ved siden av ordlyden stoppes | low | avvist: følger regelen |
| ECH10 | Prompten nevner ordlyden også for grunnlaget fra versjon 2 | low | defer: hentingen gir alltid dagene |
| ECH11 | Ugyldige dager gir ingen ordlyd | low | avvist: `ki_grunnlag` avviser dem |
| ECH12 | Linja etter JSON bryter en enkel lesing av prompten | low | avvist: ingenting i `src/` leser den slik |
| BH9, VG8 | Testen for §43 godtar også grunner om dagene | low | avvist: sjekken av interessen må fortsatt stoppe |
| BH11 | Docstringen viser til §44 | low | avvist: §44 er grunnen |
| BH13, VG10 | §45 og tidene | low | avvist: tallene stemmer, og prøvekjøringen kom etter rettingen |

### Gjennomgangen 25.10 kl. 11

Gjennomgang 25.10, etter hele settet (11:09:48–11:17:23, fil for fil, 3560 bestått, 20 hoppet over, 0 feilet), på diffen `dce8d1e..dfa39fc` på grenen, uten dagsfilene, `epics.md` og bildet. Den dekker fjerde forsøk (`10123df`, `7b2eda8`, `9aa4219`) og testen og «Valg» fra i dag (`dfa39fc`). Blind Hunter (BH, 17 funn), Edge Case Hunter (ECH, 14) og Verification Gap (VG, 17) gikk gjennom hver for seg, uten å endre noe i repoet. Rettingene står i `21cebff` (siden), `fa6b9bc` (kontrollen) og `0cb83bb` (henvisningene og en test). Kontrollen ble endret, så §46 ble kjørt på nytt mot en ny kopi av basen (`a2d13b5`): 15 av 15 besto, og ingen tekst har feil.

| # | Funn | Dom | Rute |
|---|---|---|---|
| BH1, ECH6, VG1 | «I dag for første gang» om forrige børsdag i helga, før kveldshentingen og i demoen | high | patch: ordlyden fra svaret 11:04 b) når dagen siden viser, ikke er i dag. Bildet viser nå «Signalet ble slik denne dagen for første gang.» |
| ECH1 | «De siste 3 børsdager», «de siste dagene» og «de siste ukene» slapp gjennom | high | patch: «siste» er vinduet bare med 20 eller 50 |
| BH2, ECH7 | «For første gang» er usant når signalet var slik før, med en annen dag imellom. Tellingen er «på rad» | medium | **må avgjøres av gruppen**: ordlyden og tellingen er gruppens (svarene 24.10 kl. 16:15 a) og 25.10 kl. 00:51). Under «Åpent» |
| ECH4, BH14 | «Fortsatt», «lenge» og «uke» stopper også riktige tekster, som «Kursen ligger fortsatt over snittet» | medium | **må avgjøres av gruppen**: et stopp, ikke en feil som slipper gjennom, og §46 på nytt hadde 0 stoppet. Om ordene skal leses snevrere, eller prompten nevne dem. Under «Åpent» |
| ECH2 | Et vindu etter «har vært» eller «har ligget», «Trenden har vært positiv 50 dager», slapp gjennom | medium | patch: et verb om varighet foran i setningen gjør tallet til dagene |
| ECH3, BH4, VG3 | Dagene uten tall: «igjen», «fortsetter», «forrige børsdag», «dagen før», «det nye signalet», «en stund», «ukene». «I enhver form» var en overpåstand | medium | patch: formene er lagt til, og docstringen sier «de kjente formene». Kontrollen leser ord, ikke mening: under «Åpent» |
| ECH5 | Vinduene for bevegelsen og interessen, «Bevegelsen måles over 20 dager» og «20 handelsdager», ble stoppet | medium | patch |
| VG2, BH16 | «Velg dag» på siste dag var ikke testet | medium | patch: `test_velg_dag_paa_siste_dag` |
| VG4, BH7, ECH11 | Feilgrenen for dagene var utestet, og `RuntimeError` fra versjonssjekken ga 500 | medium | patch: fanges som i `_ki_visning`, og `test_uten_setning_naar_dagene_ikke_kan_leses` |
| VG5 | Regel 21 i «minst» var utestet | low | patch |
| VG7 | «Fremdeles», «uken», «et nytt positivt signal» og «ble helt nytt» var utestet | low | patch |
| VG12, BH8 | Ingen test for at et grunnlag med `dager` eller `dager_merke` avvises | low | patch: `test_et_grunnlag_med_dagene_avvises` |
| VG10, BH10, VG8 | Docstringene viste til §45, `ordlyd_for_dagene` og `test_aksjedetalj.py` | low | patch |
| VG11 | Kommentaren i `aksje.html` sa at siden med KI av er lik den før 10.3 | low | patch i malen. Kontrollpunktet under 10.3 i `epics.md`: defer, gruppen fører det |
| VG13 | `test_ugyldige_dager_avvises` manglet «Ville feilet hvis» | low | patch |
| BH5 | «Har vært slik i 4 børsdager på rad» om en tidligere dag | low | **må avgjøres av gruppen**: ordlyden. Under «Åpent» |
| ECH10 | «Signalet er slik» også med retningen Ingen | low | **må avgjøres av gruppen**: under «Åpent» |
| BH3 | Demoteksten for BRFE sier 50 og 20, også om parametrene var andre | low | defer: KI-steget bruker standardparametrene, som siden |
| BH6 | Siden leser hele historikken for aksjen | low | defer: ett kall per side (svaret 11:04 a) |
| ECH12 | En låst base gir ingen setning, men 503 i historikken | low | defer: setningen er et tillegg |
| ECH13 | «Vart én dag» slipper gjennom | low | defer: «en dag» er et vanlig ord (kjent avveining) |
| ECH14, VG16 | Testen for lesingen dekker bare siste dag, og plasseringen er bare testet med KI på | low | defer |
| VG6 | Setningen i demoen har ingen egen test | low | defer: bildet og avtrykket dekker den |
| VG9, BH11 | Testgrunnlag i `test_ki_modell.py` har fortsatt `dager` | low | defer: kontrollen leser ikke nøklene, og at grunnlaget avvises, er nå testet |
| VG14 | Tellingen for §34–§45 med den nye kontrollen har ingen test | low | defer: tekstene står bare i kopiene, og tellingen er ført i §46 |
| VG15 | `Dagsbilde.dager` regnes i KI-steget, men brukes ikke | low | defer |
| VG17, BH9 | Avtrykket dekker ikke feltene i grunnlaget, og versjon 3 har hatt flere prompter | low | avvist: versjon 3 er ikke flettet, og avtrykket skiller promptene |
| ECH8, ECH9 | En grunn dagen før gir et kjent antall, og rekka ser bare på retning og styrke | low | avvist: følger svaret 24.10 kl. 16:15 a) |
| BH12, BH13, BH15 | Svake påstander i to tester, regexen for KI-seksjonen, og formen på demotekstene | low | avvist: testene feiler fortsatt på det de skal, og demotekstene er modellens |
| BH17 | Hjelpen nevner ikke setningen | low | avvist: hjelpen sier ikke hva KI-teksten tar med |

Med dom medium er BH2, ECH7 og ECH4, BH14 ikke rettet. De må avgjøres av gruppen, og grenen flettes ikke før det.

*Lagt til 2026-10-25 kl. 12:12 og 12:19 (gruppens svar):* BH2, ECH7: ordlyden uten «for første gang» (svaret a). ECH4, BH14: stoppes som før (svaret b), ingen endring. BH5: ordlyden fra svaret d). ECH10: setningen står som den er (svaret e). Se «Valg».

### Gjennomgangen 25.10 kl. 13

Gjennomgang 25.10, etter hele settet (12:45:29–12:53:48, fil for fil, 3624 bestått, 20 hoppet over, 0 feilet), på diffen `d24d9b5..7d61aaf` på grenen, uten bildet. Den dekker ordlyden etter gruppens svar kl. 12:12 og 12:19 (`7d61aaf`). Flettingen av main (`d24d9b5`) hadde bare dagsfila og `epics.md`. Blind Hunter (BH, 9 funn), Edge Case Hunter (ECH, 1) og Verification Gap (VG, ingen hull, ett funn utenfor diffen) gikk gjennom hver for seg, uten å endre noe i repoet. Rettingene står i `e150117` (kontrollen) og `c3cf84b` (testene og spesifikasjonen). Kontrollen ble endret, så §46 ble kjørt på nytt mot en ny kopi av basen (`ce36870`): 15 av 15 besto, og ingen tekst har feil.

| # | Funn | Dom | Rute |
|---|---|---|---|
| ECH1 | Kontrollen slapp appens nye setning for 1 dag fra modellen, «Signalet ble slik i dag.» og «Signalet ble slik denne dagen.», også om en lengre rekke | high | patch: stoppes som dagene, med en test i `test_dagene_i_enhver_form_stoppes` |
| BH1 | Linja under «Åpent» sa «de fire punktene» og kunne leses som at VG3 var avgjort | low | patch |
| BH2 | «Fjerde forsøk» viste fortsatt den gamle ordlyden uten henvisning til svarene | low | patch: en Rettet-linje. «Valg» har svarene rett under b), og triagen kl. 11 har en Lagt til-linje |
| BH3 | Entall for en annen dag sto som gruppens svar | low | patch: merket som utledet av d) |
| BH4 | Vakttesten sjekket bare setningene for en annen dag | low | patch: i dag får aldri «denne dagen» eller «hadde» |
| BH6 | Premisset for «minst» i `test_minst_paa_siste_dag_som_ikke_er_i_dag` var ikke sagt | low | patch: docstringen |
| BH5 | Ingen test for retningen Ingen (svaret e) | low | defer: `setning_om_dagene` tar ikke retningen inn, så setningen kan ikke variere med den |
| BH7 | Ingen sidetest for «minst» med flere dager en annen dag | low | defer: enhetstesten dekker ordlyden, og siden sender `annen_dag` likt for alle |
| BH8 | Kommentaren om avtrykket i `test_docker.py` er lagt oppå den forrige | low | avvist: lista over endringer bak avtrykket er historikk, som resten av lista |
| BH9 | Docstringen i `dagene.py` sier ikke hva ordlyden er | low | avvist: konstantene står rett under, med kommentarer |
| VG-utenfor | `ki_prompt.py`: «Siden sier det under teksten» gjelder ikke lenger «første gang» | low | under «Åpent»: koden er ikke endret i denne instruksjonen, og en endring i prompten avgjør gruppen |

Ingen funn med dom medium eller høyere står urettet.

## Åpent

- `bransjen` for en bransje med bare aksjen selv sier det samme som aksjens egen endring. Børsometeret merker den «1 aksje». Grunnlaget har ikke det merket.
- *Lagt til 2026-10-24:* om versjon 3 skal rettes og prøvekjøres på nytt, eller legges bort: styrkeregelen og «Ingen sjekk ga» (BH6), utsagn om én sjekk (BH8) og «minst» (BH1, ECH6).
- *Lagt til 2026-10-24:* tall som står i grunnlaget, men om et annet felt, sjekkes bare der teksten har formene «N aksjer steg/falt» og «N (børs)dager på rad» (BH2, ECH8, ECH12).
- *Lagt til 2026-10-24 kl. 22:24:* versjon 3 rettet ble stoppet fire ganger i §44, og flettes ikke etter svaret kl. 21:49. Gruppen avgjør om prompten skal nevne «minst» bare med merket (BH13), og hva bildet av aksjesiden skal vise (BH15).
- *Lagt til 2026-10-24:* utsagn om én sjekk i formene «ga et utslag som var negativt», «det gjorde også interessen» og en liste mellom komma før verbet leses ikke (gjennomgangen av rettingen, BH5, ECH6, ECH7).
- *Lagt til 2026-10-25:* modellen setter ofte ordlyden i anførselstegn etter et ekstra «i», som «i "i dag for første gang"» (åtte av de ti demotekstene som besto). Ordlyden står ordrett, så kontrollen slipper den. Om prompten skal si hvordan ordlyden settes inn i setningen, avgjør gruppen.
- *Lagt til 2026-10-25:* versjon 3 med ferdig ordlyd besto 13 av 15 i §45 (VAR og TEL på «det første signalet»), under kravet 15 av 15 i svaret kl. 23:23, og flettes ikke. Gruppen avgjør veien videre.
- *Lagt til 2026-10-25:* ordlyden godtas der den står, også i en annen setning (BH4), og dagene med ord som «fortsatt», «lenge» og «uker» leses ikke (BH2, ECH6).
- *Lagt til 2026-10-25:* for en tidligere dag valgt med «Velg dag» skriver siden «Signalet ble slik denne dagen for første gang.» i stedet for «i dag». Gruppen avgjør ordlyden.
- *Lagt til 2026-10-25 kl. 11:04:* ordlyden for en valgt dag er avgjort av gruppen (under «Valg», svaret b).
- *Lagt til 2026-10-25 kl. 11:* «for første gang» sier noe om hele historikken, men tellingen gjelder rekka på rad. Positiv/1, Negativ/1, Positiv/1 gir «i dag for første gang» (BH2, ECH7). Gruppen avgjør ordlyden eller tellingen.
- *Lagt til 2026-10-25 kl. 11:* «fortsatt», «lenge» og «uke» stopper også tekster om trenden, som «Kursen ligger fortsatt over snittet» (ECH4, BH14). Gruppen avgjør om ordene skal leses snevrere, eller om prompten skal nevne dem.
- *Lagt til 2026-10-25 kl. 11:* kontrollen leser ord, ikke mening, så en form for dagene som ikke er i lista, slipper gjennom (VG3). «I enhver form» i svaret kl. 00:51 er derfor de kjente formene.
- *Lagt til 2026-10-25 kl. 11:* ordlyden for flere dager og «minst» om en dag som ikke er i dag («har vært slik», BH5), og setningen når retningen er Ingen (ECH10).
- *Lagt til 2026-10-25 kl. 12:12 og 12:19:* punktene om BH2, ECH7, ECH4, BH14, BH5 og ECH10 fra gjennomgangen kl. 11 over er avgjort av gruppen (under «Valg»): «for første gang» er tatt ut (BH2, ECH7), «fortsatt», «lenge» og «uke» stoppes som før (ECH4, BH14), en dag som ikke er i dag får «Denne dagen hadde signalet vært slik …» (BH5), og setningen med retningen Ingen står (ECH10). Punktet om VG3 står åpent.
- *Lagt til 2026-10-25 kl. 13:* prompten sier om dagene, nyheten og «første gang» at «Siden sier det under teksten», men siden sier ikke lenger «for første gang» etter svaret kl. 12:12 a) (gjennomgangen kl. 13). Regelen for modellen står. Om begrunnelsen skal endres, avgjør gruppen, fordi prompten og avtrykket da endres.
  - *Avgjort 2026-10-25 kl. 18:34 og 18:35 (gruppens svar):* a) grunnen i prompten endres i kveld, fordi siden ikke lenger sier «for første gang» (svaret kl. 12:12 a). Linja blir: «Ikke si hvor lenge signalet har vart, om det er nytt, eller om det er første gang. Siden sier under teksten hvor lenge signalet har vart.» Regelen for modellen står. b) `PROMPTVERSJON` står som «3», fordi ingen tekst i `ose.db` er laget med versjon 3 ennå. Avtrykket settes på nytt, og demotekstene og prøvekjøringen lages på nytt, så alle tekster med versjon 3 er laget med samme prompt. Det er et unntak fra regelen om ny versjon i docstringen i `ki_prompt.py`, og docstringen sier det.
