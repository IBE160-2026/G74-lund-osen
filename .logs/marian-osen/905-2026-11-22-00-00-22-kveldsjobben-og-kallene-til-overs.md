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
