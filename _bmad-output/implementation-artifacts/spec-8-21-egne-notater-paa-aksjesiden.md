---
title: 'Story 8.21: Egne notater på aksjesiden'
type: 'feature'
created: '2026-11-10'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '53ff012c'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md'
---

Skrevet 10.11 i instruksjonen kl. 16:08, etter gruppens svar kl. 14:32. Instruksjonen lagres i `docs/ai-prompts/2026-11-10.md` etter flettingen (steg 3), og storyen og svaret kl. 14:32 føres da i `epics.md`. Svaret kl. 14:32 står ikke i repoet ennå; det som står her om det, er hentet fra instruksjonen. Gruppen har sagt at Claude Code bygger etter forslagene i spesifikasjonene, og at de gås gjennom før flettingen (svaret 08.11 kl. 12:32).

## Storyen

Som **bruker**, vil jeg skrive et kort notat på aksjesiden og senere se hvordan det gikk etterpå, så jeg kan lære av det jeg selv tenkte, uten at appen sier hva som var riktig.

**Oppfyller:** svaret 10.11 kl. 14:32 · **Begrenses av:** NFR-06, NFR-08, `AD-3`, `AD-7`, `AD-10`, `AD-16`

**Kontroll — hva testen ser etter:**
- Brukeren skriver et kort notat på aksjesiden. Notatet får dagen siden viser: siste børsdag, eller dagen fra «Vis dagen»
- Under hvert notat står hvordan det gikk etterpå: endringen i aksjen og i hovedindeksen fra notatdagen til siste dag med kurser, og signalet som er lagret for de dagene
- Bare fakta: appen sier aldri om noe var riktig eller galt, og gir ingen råd (NFR-06)
- Notatene kan slettes, og lagres i en ny tabell med egen migrasjon (`AD-16`). Webserveren er eneste skriver av tabellen, som for Min liste, ønskene og innstillingene
- Notatene virker i demoen og i den ekte versjonen
- Ingen API-kall (`AD-10`)
- **Ville feilet hvis:** et notat fikk en annen dag enn siden viste, «etterpå» regnet signalet på nytt i stedet for å lese det som er lagret, eller siden brukte et ord som «riktig», «galt», «kjøp» eller «selg» om et notat

**Avhenger av:** 2.7b for siden for dagen, 8.16b for «Vis dagen», 8.17b for endringen fra en dag til siste børsdag. **Én økt:** ja.

## Svaret kl. 14:32, slik instruksjonen gjengir det

Egne notater på aksjesiden bygges i dag og flettes i natt kl. 23:50–23:58, fordi de trenger en ny tabell. Rådet anbefalte onsdag, men gruppen valgte i natt. Nettsiden får også skrive notatene til basen, som ønskene og innstillingene, og det utvider svaret 09.11 kl. 10:23; rådet anbefalte det.

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Hvor står notatene?** *Forslag:* en egen del, «Mine notater», nederst på aksjesiden, under «Signalet dag for dag» og over boblen til investorsiden. Skjemaet for et nytt notat står øverst i delen, og notatene under, med den nyeste notatdagen først.
2. **Hvor kort er kort?** *Forslag:* høyst 280 tegn. Et tomt notat, eller et notat med bare mellomrom, lagres ikke. Mellomrom før og etter tas bort, og linjeskift blir mellomrom, så notatet er ett avsnitt.
3. **Hvilken dag får notatet?** *Forslag:* dagen siden viser, og den kan ikke velges for seg. Ved «Siste børsdag» og periodene er det siste dag med kurser for aksjen, og ved «Vis dagen» den valgte dagen. Skjemaet sier dagen: «Notatet får datoen <dag>.» Flere notater samme dag er lov.
4. **Hva står under «Etterpå»?** *Forslag:* én linje med endringen i aksjen og én med endringen i hovedindeksen, fra sluttkursen på notatdagen til siste dag med kurser for aksjen, på justert kurs (FR-101), regnet som «Sammenlign siste børsdag med» i Min liste (8.17b). Så signalet som er lagret for notatdagen og for den siste dagen, med pillen, brikkene og «N av 3» som i «Signalet dag for dag». Signalet leses fra `vurdering` og regnes aldri (`AD-7`). Mangler en kurs eller en vurdering, står «–» med grunnen (NFR-08).
5. **Og når notatdagen er den siste dagen?** *Forslag:* «Ingen børsdager med kurs etter notatdagen ennå.», og signalet for notatdagen.
6. **Hvilke ord?** *Forslag:* bare tall og datoer, med overskriften «Etterpå» og linjene «Aksjen fra <dag> til <dag>: +x %», «Hovedindeksen (<symbol>) samme dager: +y %» og «Signalet <dag>: …». Ingen ord som sier at notatet traff eller bommet, og ingen råd. En test leser siden etter ordene «riktig», «galt», «feil», «traff», «bom», «kjøp», «selg» og «bør» i delen.
7. **Slette.** *Forslag:* knappen «Slett» ved hvert notat sletter raden straks, uten å spørre først, fordi skjemaet virker uten skript. Notatene er ikke et uerstattelig lager som `vurdering` (`AD-7`), som merkingen i Min liste. Et notat kan ikke endres; det slettes og skrives på nytt.
8. **Tabellen.** *Forslag:* `notat` i `0012_notat.sql`, med `id`, `symbol`, `dato`, `tekst` og `laget`. En trigger avviser et symbol som ikke står i `aksje`, som for `min_liste` (0007). `CHECK` holder teksten mellom 1 og 280 tegn og datoen på formen ÅÅÅÅ-MM-DD. Porten heter `Notatlager` (`src/notater.py`) med `MinneNotatlager` og `SqliteNotatlager` i `lagring_sqlite.py`, etter navneregelen (`AD-3`).
9. **Demoen.** *Forslag:* notatene virker i demoen og lagres i demobasen, som merkingen i Min liste. Demokommandoen skriver ingen notater. En demobase fra før 0012 vises ikke, og sidene ber om at den lages på nytt, som etter 0011.
10. **En aksje som er tatt ut av lista.** *Forslag:* notatene står fortsatt på siden for aksjen, og kan slettes, men det kan ikke skrives nye, fordi aksjen ikke har kurser etter at den gikk ut.
11. **Hjelpen.** *Forslag:* ingen «?»-knapp. Én kort linje under overskriften: «Notatene lagres på denne maskinen. Under hvert notat står hva aksjen, hovedindeksen og signalet gjorde etterpå.» `docs/hjelp.md` får «Hva er «Mine notater»?».
12. **Rekkefølgen i natt.** *Forslag:* 0012 er neste ledige nummer, og ingen av grenene for 2.4, 2.6, 8.7 og 8.9 har en ny migrasjon. 8.21 flettes kl. 23:50–23:58, etter de fire som flettes i dag.

## Delene

### A) Tabellen `notat` (`0012_notat.sql`) og porten `Notatlager`

`id`, `symbol`, `dato`, `tekst` og `laget`. Triggeren mot `aksje` og `CHECK` fra spørsmål 8. Porten har `notater(symbol)`, `skriv(symbol, dato, tekst)` og `slett(symbol, id)`.

**Ville feilet hvis:** et notat ikke overlevde en omstart, tabellen godtok et ukjent symbol, en tom tekst eller over 280 tegn, eller `slett` kunne slette et notat for en annen aksje.

### B) Skjemaet og slettingen på aksjesiden

`POST /aksje/<symbol>/notat` lagrer et notat med dagen siden viste, og `POST /aksje/<symbol>/notat/slett` sletter ett. Begge sender tilbake til samme side og samme dag (303) med ankeret `#mine-notater`. Kommer forespørselen med Origin, må den være denne siden, som bryteren og stjernen. Webserveren skriver bare tabellen `notat` her (`AD-3`), og henter aldri noe (`AD-10`).

**Ville feilet hvis:** notatet fikk en annen dag enn siden viste, en dag uten kurs for aksjen ble godtatt, en annen side kunne skrive eller slette, eller en GET endret noe.

### C) «Etterpå» under hvert notat

Endringen i aksjen og hovedindeksen fra notatdagen til siste dag med kurser, og signalet som er lagret for de to dagene (spørsmål 4–6).

**Ville feilet hvis:** endringen var regnet på en annen kurs enn den justerte, signalet ble regnet på nytt, eller delen brukte et av ordene i spørsmål 6.

### D) Demoen, README-en og hjelpen

Notatene virker i demoen. README-en sier at aksjesiden har «Mine notater», og `docs/hjelp.md` har «Hva er «Mine notater»?» (regel 19). Bildene i `docs/appen/` tas på nytt når sidene de viser, er endret.

**Ville feilet hvis:** et notat i demoen ikke ble lagret, eller README-en eller hjelpen ikke nevnte notatene.

## Bygget 10.11 (instruksjonen kl. 16:08)

Bygget på grenen `8-21-egne-notater`, i worktreen `G74-lund-osen-8-21`, fra origin/main (`53ff012c`).

- **Filene:** `src/migrasjoner/0012_notat.sql`, `src/notater.py` (porten og minneutgaven), `src/etterpaa.py` («Etterpå», ren logikk), `SqliteNotatlager` i `src/lagring_sqlite.py`, rutene `POST /aksje/<symbol>/notat` og `POST /aksje/<symbol>/notat/slett` og delen på aksjesiden i `src/app.py`, `src/templates/aksje.html` og `src/static/stil.css`. `docs/hjelp.md` har «Hva er «Mine notater»?», og punktet om aksjesiden i «Status» i README-en sier «notater».
- **Avvik fra delene:** README-en sier «notater», ikke «Mine notater», fordi et punkt i «Status» har høyst 20 ord (testen i `tests/test_docker.py`). Navnet på delen står i hjelpen. Signalet og endringen leses fra hele serien til siste dag, også når siden viser en periode eller en dag fra «Vis dagen».
- **Tester («Ville feilet hvis» i hver):** `tests/test_notater.py`. Testene som teller migrasjonene, sier versjon 12.
- **Bildene:** alle ti i `docs/appen/` er tatt på nytt med DevTools-protokollen i Edge uten vindu, med de samme høydene, mot en demobase i en midlertidig mappe. Alle var byte for byte de samme, fordi bildet av aksjesiden slutter ved «Signalet forklart», over «Mine notater». Avtrykkene i `tests/test_docker.py` er regnet ut på nytt, og `src/notater.py` og `src/etterpaa.py` står bak bildet av aksjesiden.

## Mutantene

På `5a8816b9` fire, én per del: A (`slett` sletter for en annen aksje), B (en dag uten kurs godtas), C (endringen regnet på sluttkursen, ikke den justerte) og D (README-en nevner ikke notatene). Alle ble fanget av `tests/test_notater.py`, og hver fil var lik HEAD etterpå (kopi før, sha256 mot HEAD etter). På nytt på `05e9a877`, etter rettingene: A 2, B 3, C 2 og D 1 test, alle fanget, og hver fil lik HEAD.

## Gjennomgangen 10.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Blind Hunter med bare diffen, og Edge Case Hunter og Verification Gap i samme agent, med repoet. Blind Hunter hadde 12 funn, Edge Case Hunter 8 og Verification Gap 6.

**Middels**
- *ECH1, rettet.* «Vis dagen» godtar en dag uten kurs for aksjen, som en lørdag, og skjemaet sto da, men lagringen ble avvist med 400. Nå står ikke skjemaet en slik dag, bare en linje om at notatet trenger en dag med kurs. Test: `test_dag_uten_kurs_har_ikke_skjemaet`.
- *BH1, ikke en feil.* `slutt` er en dag fra aksjens egen serie (`rader`, `src/app.py`), ikke siste børsdag for lista, så standardvisningen har alltid kurs for aksjen.
- *BH2, ikke en feil, test lagt til.* «Etterpå» får hele serien, vurderingene til siste dag og hele indeksen, også med «Vis dagen». `test_etterpaa_med_vis_dagen_gaar_til_siste_dag` viser det.

**Lav**
- *Rettet:* ECH2 og BH7 (svaret går tilbake til samme periode eller dag, med feltet `vis`), BH3 og ECH3 (en id med over 18 sifre gir 400, ikke 500), BH4 (CHECK for en dato som finnes og et tidspunkt som kan leses; en CHECK som ble NULL, slapp først raden gjennom, og testen fanget det), BH8 (egen grunn når indeksen ikke kunne leses), BH9 og ECH5 (et notat med bare tegn uten bredde avvises), BH10 (minneutgaven sjekker dagen), BH11 (testen sammenligner styrken og retningen på siden med raden i `vurdering`), ECH7 (malen viser ikke «None»), ECH8 (aksjen sjekkes i samme transaksjon som innsettingen), VG1 (tekstene for grunnene og teksten i malen sjekkes mot ordene i spørsmål 6), VG2 (docstringen sier hva testen kan skille), VG3 (en aksje som er tatt ut, og en demobase fra før 0012, på siden), VG4 (perioden og «Vis dagen» for siste dag), VG5 (siden står når notatene ikke kan leses) og VG6 (linja ved avtrykket for aksjesiden).
- *Ikke en feil:* BH5 (`RuntimeError` står i `BASEFEIL`, så en base på en gammel versjon gir 503, ikke 500; testen for demobasen fra før 0012 viser det) og BH12 (hjelpen sier «justert for utbytte» som tittelen «Kurs justert for utbytte» i `src/hjelpetekster.py`).
- *Ført:* BH6 (Origin sjekkes bare når den er med, som for stjernen og innstillingene; en POST uten Origin godtas), ECH4 (en POST mot en demobase som mangler, gir 404, mens siden ber om demokommandoen) og ECH6 (mangler indeksen den siste dagen, står grunnen uten å si hvilken dag).

## Tilleggene: svaret kl. 14:44 (plassering, bryter og tenkte kjøp) og kl. 15:57 (demoen)

Limt inn kl. 16:52, etter at delene A-D var bygget og gjennomgått. Storyen blir større, og resten gjelder som før. Svarene kl. 14:44 og 15:57 står ikke i repoet ennå; det som står her om dem, er hentet fra tilleggene. Spørsmål 1 og 9 over er endret av dem, som spørsmål 13 og 21 sier.

### Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

13. **Hvor står notatene nå?** Tillegget: «under signalet og kursgrafen». *Forslag:* rett under kursgrafen og «Signalet forklart», over «Signalet dag for dag». Det erstatter forslaget i spørsmål 1 (nederst, under «Signalet dag for dag»). Alle notatene står også samlet nederst i Min liste, det nyeste først, med navnet på aksjen som lenke, «Etterpå» og det tenkte kjøpet, men uten skjemaene: de skrives og slettes på aksjesiden. Stripa øverst får ingen ny knapp.
14. **Bryteren «Notater».** *Forslag:* en tredje bryter i Innstillinger, «Vis notater», på fra start, med «?» og en kort tekst under. Den lagres i en ny tabell, `notatvalg`, i 0012, fordi CHECK i `innstilling` (0011) bare godtar de to valgene der, og en tabell som finnes, endres ikke (`AD-16`). Av skjuler delen på aksjesidene og i Min liste, og sletter ingenting.
15. **Kursen ved kjøpet og salget, og en serie som hentes på nytt eller justeres.** *Forslag:* kursen lagres ikke. Ved trykket lagres dagen sluttkursen må være etter: den siste dagen med kurs for aksjen da brukeren trykket, eller børsdagen før i dag om den er senere. Sidene leser den første kursen i serien etter den dagen hver gang de vises, og endringen regnes på justert kurs, som ellers (FR-101). Hentes serien på nytt eller justeres for utbytte eller splitt, følger prosenten serien, og et hull som fylles senere, kan ikke bli kjøpsdagen, fordi dagen er minst børsdagen før trykket.
16. **Når kan det noteres?** *Forslag:* bare fra siden for siste dag med kurser, så sjekkene som lagres, er de siden viser. Ikke ved «Vis dagen» for en tidligere dag. Et salg kan noteres først når kjøpet har fått sluttkursen. Et notat har høyst ett tenkt kjøp, og en aksje høyst ett åpent (en unik indeks i 0012).
17. **Et tenkt kjøp når notatet slettes.** *Forslag:* kjøpet hører til notatet og slettes med det, av en trigger i 0012. Knappen sier det: «Slett notatet og det tenkte kjøpet».
18. **Hva står ved kjøpet?** *Forslag:* mens det venter: «Notert <tid>, venter på sluttkursen.» Mens det er åpent: kjøpsdagen, sjekkene på siden da kjøpet ble notert, og «Aksjen siden kjøpet, til <dag>: +x %» med hovedindeksen de samme dagene. Etter salget: kjøpsdagen, salgsdagen, antallet børsdager med kurs etter kjøpsdagen til og med salgsdagen, sjekkene begge gangene, og endringen fra kjøpet til salget med hovedindeksen ved siden av. Bare prosent.
19. **Ordene.** *Forslag:* knappene heter «Noter et tenkt kjøp» og «Noter et tenkt salg», som i tillegget. Ingen knapp eller tekst sier «Kjøp» eller «Selg» alene, og ordene gevinst, tap, riktig, galt og vant brukes ikke. Testen leser delen etter ordene i spørsmål 6 og disse, med «tenkt kjøp» tatt bort først. Ingen samlet statistikk, treffprosent, snitt, sortering etter resultat eller varsler.
20. **Når en aksje med et åpent tenkt kjøp tas ut.** *Forslag:* «Fjern» viser først en side som sier at kursene for aksjen stopper, med «Fjern likevel». «Bytt ut» og de ferdige listene sier det samme i teksten før knappen. Ingenting skrives før brukeren trykker.
21. **Demoen (tillegg 2).** *Forslag:* demokommandoen skriver fire oppdiktede notater fra dager i demoserien etter 21.09 (BRFE to, KVST og NLYS), alle med teksten «Eksempel: …», og ett avsluttet (BRFE) og ett åpent (KVST) tenkt kjøp, med sjekkene som er lagret for dagene, som om brukeren hadde trykket. Hvert notat i demoen er merket «Eksempeltall». Nye notater og tenkte kjøp virker, men demoen henter aldri kurser, så et nytt kjøp venter, og siden sier «Demoen henter ikke kurser, så den kommer ikke her.» Det erstatter forslaget i spørsmål 9 om at demokommandoen ikke skriver notater.
22. **Bildene (tillegg 2).** *Forslag:* tre nye bilder i `docs/appen/`, fra demoen: «Mine notater» på aksjesiden for BRFE, notatene samlet i Min liste, og Innstillinger med bryteren. De andre bildene tas på nytt.

### Delene

#### E) Bryteren «Notater» (`notatvalg` i 0012)

**Ville feilet hvis:** bryteren manglet, ikke var på fra start, sto uten «?» og teksten, eller av viste notatene eller slettet noe.

#### F) Notatene samlet i Min liste

**Ville feilet hvis:** Min liste ikke viste notatene for alle aksjene, nyeste først, med lenke til aksjen, eller stripa fikk en ny knapp.

#### G) Tenkte kjøp og salg (`tenkt_kjoep` i 0012)

**Ville feilet hvis:** kjøpet ikke lagret sjekkene slik de sto på siden, fikk en annen kurs enn den første etter trykket, en aksje fikk to åpne kjøp, et salg kom før kjøpet hadde kursen, kursen ble lagret, kjøpet ble liggende uten notatet, eller en aksje med et åpent kjøp ble tatt ut uten at appen sa fra.

#### H) Demoen og bildene (tillegg 2)

**Ville feilet hvis:** demoen manglet eksemplene med tall, ett åpent og ett avsluttet kjøp med sjekkene begge gangene, et eksempel ga råd, eller et nytt kjøp i demoen ikke sa at demoen ikke henter kurser.
