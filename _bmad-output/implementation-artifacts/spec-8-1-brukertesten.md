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

Skjemaet som fylles ut, er `docs/brukertest.md`.

## Slik er det i dag (slått opp 23.10 på `069ecb1`)

- **KI-teksten er på som standard.** Bryteren er informasjonskapselen `ose_ki` (`KAPSEL` i `src/ki_visning.py`). `ki_paa` gir på når kapselen mangler eller sier `paa`, og av bare når den sier `av`.
- **Den slås av med knappen «Skjul KI-teksten»** på en aksjeside (`src/templates/aksje.html`, skjemaet `ki-bryter` med `POST /ki`). Kapselen varer i ett år (`max_age=365 * 24 * 3600` i `ki_bryter` i `src/app.py`) og gjelder bare den nettleseren og den profilen. Et privat vindu eller en annen nettleser har ingen kapsel, og der er KI-teksten på.
- **Knappen står bare på en aksjeside med sjekker** (`{% if detalj.sjekker %}`), og den sier «Vis KI-teksten» når teksten er av. Personen kan altså slå KI-teksten på selv i del A.
- **Den ekte versjonen** startes med `docker compose up --build` (steg 7 i README-en) og åpnes på http://127.0.0.1:8000. Demoen har merket «Eksempeltall» øverst, og den ekte versjonen har det ikke.
- **Oversikten** har 15 rader, én per aksje i lista, med hovedindeksen og søylene over tabellen og «Skilte seg ut» først.

## Hvem

- Én person utenfor gruppen som ikke har sett appen.
- Ingen navn eller annet som kan kjenne personen igjen, står i repoet: ikke i skjemaet, i commitene, i dagsfila eller i UX-loggen.
- Før testen sier personen muntlig ja til at vi ser på og tar anonyme notater. Det noteres med klokkeslett i skjemaet, uten navn.

## Oppsettet

1. Den ekte versjonen på http://127.0.0.1:8000, med dataene fra siste henting. Aldri demoen: det står ikke «Eksempeltall» øverst.
2. KI av før del A: én av oss åpner en aksjeside i den nettleseren og profilen testen tas i, trykker «Skjul KI-teksten» og ser at knappen sier «Vis KI-teksten». Personen ser ikke dette.
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

## Del B (story 10.4)

Etter at tiden i del A er stoppet.

- **Aksjen** er den personen forklarte i del A. Uten forklaring er det den første aksjesiden personen åpnet. Åpnet personen ingen aksjeside, er aksjen ikke avgjort (se «Åpent»).
- **Ett fast spørsmål**, ordrett: «Hva sier siden om denne aksjen?»
  1. Først med KI av. Svaret noteres ordrett.
  2. Så slår én av oss KI-teksten på med «Vis KI-teksten», og spørsmålet stilles på nytt, ordrett. Svaret noteres ordrett.
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
- **Når personen slår på KI-teksten selv i del A:** om del B tas likevel og merkes, eller om 10.4 tas med en annen person. Knappen «Vis KI-teksten» står på hver aksjeside med sjekker, så det kan skje.

## Det som ikke dekkes her

- `KILogg` over minst én ukes drift i story 10.4, hvor ofte KI-teksten sa noe regelforklaringen ikke sa med ord. Det er en egen måling og står fortsatt i storyen.
- README-prøven på en ren maskin, som tas neste uke (svaret kl. 11:56, c).

## Det som ikke endres

- Koden, testene og basen. Bare dokumenter endres. Ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` røres ikke av dette opplegget (regel 22). Testen bruker den ekte versjonen fra main, og merkingen i Min liste er det eneste webserveren skriver (regel 22, tillegget 19.10).
