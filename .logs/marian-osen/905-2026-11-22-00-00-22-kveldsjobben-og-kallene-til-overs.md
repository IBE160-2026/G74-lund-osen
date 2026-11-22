# Kveldsjobben 20.11 og kallene til overs

## 2026-11-22 kl. 00:00 — Marian Osen

### Oppgave
Kommandoen kl. 21:46 21.11 leste statusen for kveldsjobben, og gruppen svarte kl. 21:46 at den skulle føres etter kl. 23:58. Instruksjonen kl. 22:02 ba om en ny story i backlog for Epic 2: kallene til overs skulle holde aksjene utenfor lista oppdatert. Etter svaret kl. 22:09 skulle den tas sammen med føringen, men kl. 22:22 stoppet gruppen den, fordi grunnlaget var feil. Gruppen ba om et nytt utkast i oppsummeringen.

### Plan
- Lese statusen og utløseren for kveldsjobben, uten å endre noe.
- Sjekke hvert tall og hver henvisning i storyen mot `epics.md`, PRD-en og koden før noe ble skrevet.
- Føre dagsfila 21.11 etter kl. 23:58 og kjøre `--dokumentene` før push.

### Resultat
- **Kveldsjobben 20.11**, den første med 2.10 og 2.19, startet sist kl. 23:45:02 og endte med 0. Kl. 23:45 er den siste av fire starttider: utløseren starter daglig kl. 22:15 og gjentar hvert 30. minutt i 1 t 35 min. Kl. 23:59 sto jobben for 21.11 også som Ready med resultat 0, med siste kjøring kl. 23:45 og neste 22.11 kl. 22:15.
- **Kvoten** kl. 00:00 22.11 (23:00 GMT 21.11): 20 av 20 brukt 21.11 i GMT, 296 i bonuskvoten. 21.11 var en lørdag. Ingen andre API-kall er gjort.
- **Storyen** ble stoppet kl. 22:22. Ingenting av den står i repoet: `epics.md`, sprintstatusen, PRD-en, endringsloggen, `prd-sporing.md` og `tests/test_prd_9_11.py` er urørt.
- **Dagsfila** står i `3068cd01`.

#### Utkastet

#### Det som ble funnet

- **Målingen bruker allerede kallene til overs.** Kveldsjobben kjører `--maal-omsetning` etter hentingen i alle fire kjøringene, også dager børsen er stengt. Den bruker alle kallene som er igjen av dagens 20 i GMT, uten reserve, og aldri bonuskvoten. Det står i FR-413, i avgjørelsen 28.10 kl. 22:17 (b og c) og i koden (`plan[:igjen]` i `src/omsetning.py`). §53 i `malinger.md` viser målinger lørdag 31.10 og søndag 01.11.
- **Alle er målt.** Alle de 280 aksjene i børslista utenfor appens liste har hatt en måling siden 2.13b (11.11). Nå måles de eldste målingene på nytt først.
- **2 kall i reserve** står bare i kontrollen for 2.13 («lar 2 stå igjen, med mindre alle er bedt om»). Jobben bruker alle (svaret 28.10 kl. 22:17, c).
- **Per kall** henter målingen `/api/eod` for symbolet i tre måneder bakover fra børsdagen (`vindu`, `MAANEDER = 3` i `src/omsetningsregning.py`).
  - Svaret skrives uendret til `data/raa/omsetning<n>-raa-<børsdag>.json` (AD-6).
  - Basen får bare én rad i `omsetning`: medianen, vinduet, antall handelsdager, dager uten volum, rader uten tall og feil.
  - Ingen kurser går til `kurs`.
  - Ett kall koster det samme uansett hvor langt tilbake det henter (FR-406, `malinger.md` §2), så målingen kunne hentet hele året uten flere kall.
- **Kursene fra målingen kan ikke vises for en aksje som følges, slik appen er nå:**
  - De står bare i råfila, og etter AD-6 går råfilene ikke inn i basen.
  - `kurs` godtar bare aksjer som står i `aksje`, og der står bare aksjer som har vært i lista (AD-21).
  - Tre måneder er rundt 63 børsdager. Det holder til signalet, som krever 51, men ikke til de 175 grafen trenger (FR-406).
  - Ønsket tas bare i bruk på selve børsdagen (`dag == dato`, `src/fetch_prices.py:1283`, ECH3 i 2.12). Da hentes aksjen likevel med et helt år (AD-5). ECH3 sier ikke hvorfor helgen er unntatt.
- **Hvor gamle målingene er (et anslag, regnet og ikke målt):**
  - Med 18 aksjer og indeksen brukte hentingen 19 kall 16.11, og målingen fikk 1 (epics.md, 2.17).
  - Det gir rundt 1 kall hver børsdag uten nye forsøk og 20 hver helgedag, altså rundt 45 i uka.
  - En runde over 280 aksjer tar da rundt seks uker.

#### Utkast til en ny story (gruppen avgjør etter brukertest 2)

**Målingen holder de mest omsatte utenfor lista ferske, og en aksje som følges i helgen, venter ikke til mandag.**

Som bruker vil jeg at en aksje jeg begynner å følge, har en fersk omsetning og får kurser og signal før neste børsdag kl. 22.

Kontroll (forslag):
- **Hele året per kall.** Målingen henter hele året per kall, til samme pris, og regner omsetningen over tre måneder som før. Råfila får da kurser nok til en serie (175 børsdager).
- **De mest omsatte oftere.** De 20 mest omsatte utenfor lista måles hver lørdag, og resten som i dag, eldste måling først, søndag og børsdager. Da er de 20 høyst en uke gamle, og resten rundt ti uker. Det er et anslag: 260 aksjer og rundt 25 kall i uka.
- **Følg i helgen.** Følger noen en aksje en dag børsen er stengt, tar jobben ønsket i bruk og henter aksjen med ett av dagens kall, som en vanlig henting. 2.17 regner så signalet i ettertid. Alternativet er at hentekommandoen leser kursene fra den siste målingen inn med 0 kall. Det krever at AD-6 eller AD-21 endres, og målingen kan være uker gammel.
- **Kvoten.** Bonuskvoten brukes aldri. Hentingen og nye forsøk får fortsatt kallene først.

Spørsmål til gruppen:
1. Hvorfor tas ønskene bare i bruk på børsdagen (ECH3 i 2.12)? Svaret avgjør om «Følg i helgen» er trygt. Kanskje er grunnen datoene `inn` og `ut` i `aksje`.
2. Skal målingen ha 2 kall i reserve, slik kontrollen i 2.13 sier, eller bruke alle, slik jobben gjør nå?

### Åpne punkter
- Utkastet til en story om kallene til overs: gruppen avgjør etter brukertest 2. Der står to spørsmål: hvorfor ønskene bare tas i bruk på børsdagen (ECH3 i 2.12), og om målingen skal ha 2 kall i reserve.

## 2026-11-22 kl. 12:04 — Marian Osen

### Oppgave
Instruksjonen kl. 11:33: storyen om kallene til overs, skrevet om etter funnene 21.11 og gruppens svar 22.11 kl. 11:29 (rådet anbefalte svarene), skal legges i backlog. Bare tekst på main, utenom én linje i `NYE_KRAV`. En innliming like før var avkortet og ble ikke utført (regel 1).

### Plan
- Kvotesjekken først (regel 15), og så sjekke storyen mot koden og mot funnene over (seksjonen 22.11 kl. 00:00) før noe skrives.
- Føre inn story 2.20 i `epics.md` og sprintstatusen, FR-416 i PRD-en med endringsloggen, `prd-sporing.md` og `NYE_KRAV`, en datert linje under 2.13 og svarene ved punktet i `issues.md`.
- Kjøre `--dokumentene` før push. Utført-linja kommer i `docs/ai-prompts/2026-11-22.md`.

### Resultat
- Kvoten kl. 11:34: `apiRequestsDate` 2026-11-21, altså 0 av 20 brukt 22.11 i GMT, og `extraLimit` 296. Kveldsjobben er Ready. Ingen andre kall.
- **Sjekken mot koden.** Det meste stemte: målingen bruker alle kallene som er igjen (`plan[:igjen]` i `src/omsetning.py`), vinduet er tre måneder (`MAANEDER = 3`), taket er 18 (`TAK` i `src/valg.py`), og ECH3 står i kommentaren ved `dag == dato` i `src/fetch_prices.py`: ønskene tas ikke i bruk når datoen er en dag som alt er hentet. Det passer med grunnen i svaret: lista er knyttet til hver børsdag. 2.17 regner alle dagene i serien, også dagene før aksjen kom inn i lista (`src/ettertid.py`).
- **Rettet i storyen:** «bare omsetningen lagres» er nå «basen får bare omsetningen». Svaret står uendret som råfil i `data/raa/` og går ikke inn i basen (AD-6).
- **Lagt til under «Planen avgjør», med et eget merke:**
  - 2.17 regner bare for aksjene i lista, så planen må avgjøre hvordan signalet regnes for en aksje som ennå ikke er der.
  - En dag børsen er stengt bruker målingen alle kallene i kjøringen kl. 22:15. Et ønske som kommer etter det, får da ikke noe kall samme kveld.
- **Ikke endret, men sagt fra:** en lørdag der noen følger en aksje, tar hentingen ett av de 20 kallene. Da får bare 19 av de 20 mest omsatte en måling den dagen.
- **Commits:**
  - `04fec617`: instruksjonen i dagsfila.
  - `b2dfd382`: story 2.20 i `epics.md`, og som backlog i sprintstatusen.
  - `c82049f6`: FR-416 i §4.4 som «senere», med raden i §2, «v1.1» i §8, linja i endringsloggen, raden i `prd-sporing.md`, intervallet FR-401–FR-416 og `NYE_KRAV`.
  - `a3e98fa3`: en datert linje under 2.13 om at ingen kall står i reserve.
- Testene for PRD-en, sporingen og README-en: 31 bestått. `--dokumentene`: 3096 bestått og 7 hoppet over, kl. 11:41–12:04, før push.
- Punktet om utkastet i `issues.md` er lukket, med svarene som en datert linje.

### Åpne punkter
Ingen nye. Spørsmålene til planen står i 2.20 under «Planen avgjør», og storyen står som backlog.
