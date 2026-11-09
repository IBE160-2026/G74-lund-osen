---
title: 'Story 8.1 og 10.4: opplegget for brukertesten, med KI av og så på i samme økt'
type: 'docs'
created: '2026-10-23'
status: 'ready-for-dev'
route: 'dispatch'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/kvalitetssikring.md'
  - '{project-root}/docs/brukertest.md'
---

## Intent

**Problem:** suksesskriteriet «Brukerutfall» er ikke målt (`docs/kvalitetssikring.md` §10), og ingen brukertest er tatt (§13). Story 8.1 og 10.4 står i backlog.

**Grunnlaget:**
- Story 8.1 i `epics.md`, med suksessmålet ordrett fra `prd.md`: «En person utenfor gruppen gjennomfører hovedflyten og forklarer uoppfordret hvorfor en aksje skiller seg ut | Minst 1 person, under 5 minutter, uten hjelp | Før prosjektinnlevering». Spørsmålene om 15 rader (lagt til 23.09) og om indeksen og søylene (lagt til 01.10) følger med.
- Story 10.4 i `epics.md`: samme person ser samme aksje først med KI av og så med KI på, og svarene noteres ordrett. Det er en egen test, ikke en del av 8.1 (avgjort 23.09).
- Gruppens svar 23.10 kl. 12:29 under story 8.1 og 10.4: 10.4 tas rett etter 8.1, med samme person og samme aksje, som to tester med hvert sitt notat. Brukertesten tas neste uke.
- Gruppens svar 23.10 kl. 11:56 (b) under «Prioritering»: opplegget for brukertesten kommer etter 3.4d.
- Instruksjonen 23.10 kl. 14:38 i dagsfila, med teksten under.
- *Lagt til 2026-11-08 (gruppens svar 07.11 kl. 22:51):* brukertesten tas tirsdag 10.11 eller onsdag 11.11, eller begge dagene, med den ekte versjonen og dataene fra kvelden før. Det erstatter «Brukertesten tas neste uke» i svaret kl. 12:29 over.

Skjemaet som fylles ut, er `docs/brukertest.md`.

## Slik er det i dag (slått opp 23.10 på `069ecb1`)

- **KI-teksten er på som standard.** Bryteren er informasjonskapselen `ose_ki` (`KAPSEL` i `src/ki_visning.py`). `ki_paa` gir på når kapselen mangler eller sier `paa`, og av bare når den sier `av`.
- **Den slås av med knappen «Skjul KI-teksten»** på en aksjeside (`src/templates/aksje.html`, skjemaet `ki-bryter` med `POST /ki`). Kapselen varer i ett år (`max_age=365 * 24 * 3600` i `ki_bryter` i `src/app.py`) og gjelder bare den nettleseren og den profilen. Et privat vindu eller en annen nettleser har ingen kapsel, og der er KI-teksten på.
- **Knappen står bare på en aksjeside med sjekker** (`{% if detalj.sjekker %}`), og den sier «Vis KI-teksten» når teksten er av. Personen kan altså slå KI-teksten på selv i del A.
- *Rettet 2026-11-07:* knappen «Skjul KI-teksten» og «Vis KI-teksten» finnes ikke lenger. Den er nå bryteren «KI-tekst» med «På» og «Av» (`role="switch"` i makroen `ki_bryter` i `src/templates/aksje.html`), inne i rammen «‹navn› kort fortalt» øverst til høyre når teksten vises, og alene når KI er av. Den kom med story 8.2b (U33, U46 og U67), squash-flettet i `6f62f564`, PR #109, og svaret 04.11 kl. 09:58 på spørsmål 5 og 6 i `spec-8-2b-funnene-fra-ux-loggen.md` holdt den i blekk og utenfor stripa. KI av før del A betyr at bryteren viser «Av», og i del B slås den til «På». Det gjelder også stegene under og «Åpent», der knappen nevnes.
- *Rettet 2026-11-08 (slått opp i `src/templates/aksje.html` på `50103bcc`):* rammen heter nå «Signalet forklart», ikke «‹navn› kort fortalt» (story 10.9, del C, gruppens svar 06.11 kl. 22:16 og 22:23), med «?» ved overskriften. Den står på aksjesider med sjekker, etter grafen. Appens setninger om dagene og om hva hovedindeksen, bransjen og aksjene i lista gjorde samme dag står først, og KI-teksten med «Laget av KI» under, når den er på. Bryteren «KI-tekst» står fast øverst til høyre i rammen, både med KI på og av, og med KI av står rammen med appens setninger og bryteren, uten KI-teksten. Bryteren er fortsatt kapselen `ose_ki`, på når den mangler (`ki_paa` i `src/ki_visning.py`), og personen kan slå KI-teksten på fra rammen på hver aksjeside med sjekker i del A.
- **Den ekte versjonen** startes med `docker compose up --build` (steg 7 i README-en) og åpnes på http://127.0.0.1:8000. Demoen har merket «Eksempeltall» øverst, og den ekte versjonen har det ikke.
  *Rettet 2026-11-08 (slått opp i `compose.yaml`, `start/start.ps1`, `src/app.py` og `src/lagring_sqlite.py` på `50103bcc`):* på denne maskinen er det kveldsjobben som henter, og den skriver `data/db/ose.db` i repo-mappa (lenken `data` i `G74-lund-osen-jobb`). Den ekte versjonen startes derfor fra repo-mappa på main med `uv run python src/app.py`, som åpner `data/db/ose.db` og svarer på http://127.0.0.1:8000. `docker compose up --build` bruker volumet `ose-db`, ikke den basen, og «Start den ekte versjonen» stopper i en klon med `.git`, som repo-mappa er (svaret 23.10 kl. 23:31, b, i `start/start.ps1`). Webserveren fra main skriver bare merkingen i Min liste til basen (regel 22, tillegget 19.10).
- *Lagt til 2026-11-08 (slått opp i `src/templates/_perioder.html` og `src/perioder.py` på `50103bcc`):* oversikten, Min liste, aksjesiden og børsometeret har datofeltet etter periodeknappene, med «Vis dagen» (story 8.20a). Den første knappen heter «I dag», «I går» eller ukedagen for siste børsdag i dataene (`foerste_knapp`), og feltet viser den dagen ved den knappen og dagen som er valgt, og er tomt i en periode (`dagen_i_feltet`). Er dataene fra kvelden før, heter den første knappen «I går», og feltet viser den dagen.
- **Oversikten** har 15 rader, én per aksje i lista, med hovedindeksen og søylene over tabellen og «Skilte seg ut» først.

## Hvem

- Én person utenfor gruppen som ikke har sett appen.
- Ingen navn eller annet som kan kjenne personen igjen, står i repoet: ikke i skjemaet, i commitene, i dagsfila eller i UX-loggen.
- Før testen sier personen muntlig ja til at vi ser på og tar anonyme notater. Det noteres med klokkeslett i skjemaet, uten navn.

## Oppsettet

1. Den ekte versjonen på http://127.0.0.1:8000, med dataene fra siste henting. Aldri demoen: det står ikke «Eksempeltall» øverst.
   *Lagt til 2026-11-08:* dataene er fra kvelden før (svaret 07.11 kl. 22:51). Den første periodeknappen heter da «I går», og datofeltet viser den dagen. Den ekte versjonen startes med `uv run python src/app.py` fra repo-mappa på main (under «Slik er det i dag»).
2. KI av før del A: én av oss åpner en aksjeside i den nettleseren og profilen testen tas i, trykker «Skjul KI-teksten» og ser at knappen sier «Vis KI-teksten». Personen ser ikke dette.
   *Rettet 2026-11-08:* én av oss trykker bryteren «KI-tekst» øverst til høyre i rammen «Signalet forklart» og ser at den viser «Av». Rammen står fortsatt, med appens setninger og bryteren.
3. Bare oversikten er åpen, i én fane, øverst på siden, når personen setter seg.
4. En klokke som viser sekunder, og skjemaet `docs/brukertest.md` på papir eller en annen skjerm, ikke på maskinen testen tas på.

## Det som sies

Ordrett, og uten ordene «skiller seg ut», «hvorfor» eller «signal»:

> «Dette er en nettside om aksjer på Oslo Børs. Se deg rundt som du vil, og si høyt hva du ser og tenker. Jeg kan ikke hjelpe deg underveis.»

Spør personen om noe underveis, er svaret alltid:

> «Gjør det du ville gjort hvis du satt alene.»

## Del A (story 8.1)

- **Tiden** måles fra oversikten vises til personen uoppfordret sier hvorfor en aksje skiller seg ut. Grensen er 5 minutter. Del A stopper etter 10 minutter, også uten forklaring.
- **Forklaringen** noteres ordrett, med tiden den kom.
- **Observeres, ikke spørres om**, med tidspunkt:
  - Stopper personen, ruller tilbake eller mister raden de leste (15 rader)?
  - Ser personen hovedindeksen og søylene?
  - Hvilke sider åpnes, i rekkefølge?
- **Slår personen på KI-teksten selv** i del A («Vis KI-teksten»), noteres det med tidspunkt. Da har personen sett KI-teksten før del B, og 10.4 ville feilet (under). Hva som gjøres da, står under «Åpent».
  *Rettet 2026-10-23 (gjennomgangen av 3.4e, VG5):* avgjort kl. 15:53 (b), se Lukket-linja under «Åpent»: forklaringen teller for 8.1 bare hvis den kom før, del B hoppes over, og 10.4 tas med neste person.

## Del B (story 10.4)

Etter at tiden i del A er stoppet.

- **Aksjen** er den personen forklarte i del A. Uten forklaring er det den første aksjesiden personen åpnet. Åpnet personen ingen aksjeside, er aksjen ikke avgjort (se «Åpent»).
  *Rettet 2026-10-23 (gjennomgangen av 3.4e, VG5):* avgjort kl. 15:53 (a): aksjen er den øverste i tabellen.
- **Ett fast spørsmål**, ordrett: «Hva sier siden om denne aksjen?»
  1. Først med KI av. Svaret noteres ordrett.
  2. Så slår én av oss KI-teksten på med «Vis KI-teksten», og spørsmålet stilles på nytt, ordrett. Svaret noteres ordrett.
     *Rettet 2026-11-08:* med bryteren «KI-tekst» øverst til høyre i rammen «Signalet forklart», til den viser «På». KI-teksten kommer da under appens setninger i samme ramme.
- Del A og del B har hvert sitt notat i skjemaet (svaret kl. 12:29).

## Notatene

- En kurs eller et volum som personen sier høyt, står som [kurs] eller [volum] i repoet (regel 16).
- Originalnotatene ligger i `_privat/`, som aldri committes (regel 10).
- Etter testen føres funnene i `docs/brukertest.md` med dato, hva som endres og hva som ikke endres, og i `docs/ux-logg.md`. Et funn om at KI-teksten ikke hjelper, føres som funn og ikke som feil (story 10.4).

## Ville feilet hvis

- Personen ble spurt hvorfor en aksje skiller seg ut i del A. Da er forklaringen oppfordret, og testen måler om personen kan svare på et spørsmål, ikke om skjermen forklarer (story 8.1).
- Personen så KI-teksten før del B. Da kan ingen si hvordan siden virker uten (story 10.4).

## Åpent

Ikke avgjort av gruppen, og ikke i instruksjonen kl. 14:38:
- **Aksjen i del B når personen ikke åpnet en aksjeside** i del A og ikke ga en forklaring.
  *Lukket 2026-10-23 (gruppen uten preferanse, rådets forslag kl. 15:53, a):* aksjen i del B er den øverste i tabellen.
- **Når personen slår på KI-teksten selv i del A:** om del B tas likevel og merkes, eller om 10.4 tas med en annen person. Knappen «Vis KI-teksten» står på hver aksjeside med sjekker, så det kan skje.
  *Lukket 2026-10-23 (gruppen uten preferanse, rådets forslag kl. 15:53, b):* forklaringen teller for 8.1 bare hvis den kom før det, del B hoppes over, og 10.4 tas med neste person.

## Det som ikke dekkes her

- `KILogg` over minst én ukes drift i story 10.4, hvor ofte KI-teksten sa noe regelforklaringen ikke sa med ord. Det er en egen måling og står fortsatt i storyen.
- README-prøven på en ren maskin, som tas neste uke (svaret kl. 11:56, c).
  *Rettet 2026-11-08 (gruppens svar 07.11 kl. 22:48 og 22:49 under «Prioritering» i `epics.md`):* README-prøven er ikke tatt. Videoen av demoen lages rett før den, og målet er at alt er ferdig innen 15.11.

## Det som ikke endres

- Koden, testene og basen. Bare dokumenter endres. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` røres ikke av dette opplegget (regel 22). Testen bruker den ekte versjonen fra main, og merkingen i Min liste er det eneste webserveren skriver (regel 22, tillegget 19.10).

*Lagt til 2026-11-09 (story 10.6, flettet 08.11 i `c517e460`; slått opp i `src/templates/index.html`, `src/app.py` og `src/ki_visning.py` på `673230d9`):* under tabellen på oversikten står «Børsdagen kort fortalt», med bryteren «Vis KI-tekst». Den bruker samme informasjonskapsel som bryteren på aksjesiden (FR-601), så KI av før del A gjelder begge. Med KI av står «KI-teksten er slått av. Tabellen over viser bare det reglene har regnet ut.» Slås KI på i del B, kommer også teksten om dagen på oversikten.

*Lagt til 2026-11-09 (story 2.12, PR #124, ikke flettet; spørsmål 1 og 8 i `spec-2-12-velge-og-bytte-aksjer.md`):* over «Børsdagen kort fortalt» står «Dine egne aksjer» med «+ Følg en aksje», og i Min liste «Din egen liste» med «Bytt ut». Valg som bytter aksjer, også «Bruk denne lista» fra 8.11, gjøres bare i demoen, så den ekte lista ikke endres.

*Lagt til 2026-11-09 (story 8.10 og 8.10b, PR #125 og #126 på grenene `8-10-innstillinger-oeverst` og `8-10b-vis-ki-tekst`, ikke flettet; slått opp i `src/templates/innstillinger.html` på `95e0d5d7` og i spørsmål 2 og 4 i `spec-8-10-innstillinger-oeverst.md`):* «Innstillinger» i stripa etter «Min liste» åpner en side med «Vis hjelp» og «Vis KI-tekst». «Vis KI-tekst» er det samme valget som bryteren ved KI-teksten, så KI av før del A kan settes der eller ved teksten. «Vis hjelp» skal stå på, så «?»-knappene finnes; uten valg er den på.

*Lagt til 2026-11-09 (story 8.8, PR #127; spørsmål 1 og 3 i `spec-8-8-signaldager-i-kursgrafen.md`):* kursgrafen på aksjesiden har prikker på dagene med signalstyrke 2 eller mer, og under grafen står «Prikkene på kurslinja viser dagene med signalstyrke 2 eller mer, fra ‹dato›.»

*Lagt til 2026-11-09 (slått opp i `src/app.py`, `src/lagring_sqlite.py` og `start/kveldshenting.ps1` på `673230d9`):* slik får `data/db/ose.db` migrasjonen 0011 (8.10) før testen tirsdag 10.11. 0011 flettes mandag 09.11 kl. 23:50, etter 0010 (2.12). Jobben kl. 22:15 mandag bruker commiten origin/main hadde ved midnatt søndag–mandag (steg 1 i `kveldshenting.ps1`), så den gir basen 0009 (2.11, flettet 08.11 kl. 23:50), ikke 0010 og 0011. Startes den ekte versjonen tirsdag fra repo-mappa på main etter `git pull --ff-only`, kjører `aapne_base` `migrer()` én gang i prosessen, og basen får 0010 og 0011 før siden vises. Ellers får basen dem i jobben tirsdag kl. 22:15, som bruker main fra midnatt mandag–tirsdag. Regel 22 sier at webserveren bare skriver merkingen i Min liste. At den også migrerer basen, er et åpent punkt til gruppen. Er 2.12 og 8.10 ikke flettet mandag, har testen ikke Innstillinger, og KI slås av med bryteren som før.

*Avgjort 2026-11-09 kl. 10:23 (gruppens svar), lagt til etter linja over:* webserveren migrerer basen når den startes, og skriver også ønskene (2.12) og innstillingene (8.10), så punktet over er besvart, med en Lagt til-linje under regel 22 i `CLAUDE.md`. Rådet anbefalte at `--les-boerslista` migrerer først tirsdag. Svaret er ført etter instruksjonen kl. 10:28 i `docs/ai-prompts/2026-11-09.md`.

Linjene over står også i `docs/brukertest.md`, under «Før testen».
