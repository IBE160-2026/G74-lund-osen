# Sesjonsloggen tas i bruk

## 2026-10-28 kl. 07:29 — Marian Osen

### Oppgave
Ta i bruk skillen `sesjonslogg` fra faglærer, etter gruppens svar 26.10 kl. 19:14 og 21:09, og fullføre det som stoppet i steg 2 kl. 06:13 27.10. Loggen dekker denne økta, økta kl. 06:09 27.10 og hentingen 27.10, og viser bakover til 26.10.

### Plan
- Instruksjonene står ordrett i [dagsfila 27.10](../../docs/ai-prompts/2026-10-27.md) (kl. 06:09 og 21:28) og [dagsfila 28.10](../../docs/ai-prompts/2026-10-28.md) (kl. 07:24).
- Avgjørelsene 27.10 kl. 06:31 og 20:58 og 26.10 kl. 22:58 føres i dagsfila 28.10.
- Regel 24 i `CLAUDE.md`, foran «## Sesjonslogg», uten å røre teksten til faglærer.
- Punktet om `.logs/` i «Mappestruktur» i README-en, avtrykket og tallene i testene, og de første loggfilene i én commit denne ene gangen (svaret kl. 06:31).

### Resultat
- **Økta kl. 06:09 27.10:** instruksjonen i `2c14839b` og avgjørelsene 26.10 kl. 19:14 og 21:09 i `67e34dda`. Stoppet i steg 2 kl. 06:13 (`fa9cea29`), fordi `test_mappestrukturen_lenker_til_stier_i_repoet` og `test_mappestrukturen_forklarer_alt_i_rota` står mot rekkefølgen: en lenke til `.logs/` feiler før mappa finnes, og en loggcommit feiler før `.logs/` er lenket. Gruppens svar kl. 06:31 løste det: README-en og loggfilene i samme commit.
- **Dagsfila 26.10** ([docs/ai-prompts/2026-10-26.md](../../docs/ai-prompts/2026-10-26.md)) har fire flettinger: 3.5e, stoppen før webserveren, i `dbfa0b9` (PR #100); 3.5f, hovedveien med dobbeltklikket, i `8cd20b3` (PR #101); 8.6b, børsometeret som tavla, i `7f6d9e4` (PR #99); og 8.0f, hjelpefeltet, i `238ef18` (PR #102). Grenen `pr-8-0f-bilder` (`b546d81`) beholdes for bildene i PR #102 og flettes aldri.
- **Hentingen 26.10** (instruksjonen kl. 22:54, `6de5fef`): kode 0, 16 kall, 15 vurderinger og 15 KI-tekster som besto. De 4 kallene som var igjen, gikk til målingen i §51 i `malinger.md` (`d7b964c2`): fire nye aksjer etter GOD, uten bonuskvoten.
- **3.5g natt til 27.10:** «Kom i gang» med fem steg og resten bak piler, på grenen `3-5g-kortere-kom-i-gang`, PR #103. Stoppet før flettingen, som instruksjonen sa; head-en `cc7f5875` er grønn i CI. PR-en står åpen.
- **Hentingen 27.10** (instruksjonen kl. 21:28 i `afcf5020`, Utført-linja i `b17bda66`): kode 0, 16 kall, 15 vurderinger og 15 KI-tekster som besto, og en andre kjøring som brukte 0 kall. De 4 kallene som var igjen, ble ikke brukt, fordi instruksjonen om dem ikke kom før dagskvoten gikk ut kl. 01:00 (svaret kl. 20:58).
- **Denne økta 28.10:** kvoten kl. 07:24 viste `apiRequestsDate` 2026-10-27, så 0 kall brukt 28.10 i GMT og 20 igjen. Instruksjonen i `fc05865f`, avgjørelsene i dagsfila i `0d5e9228`, og regel 24 i `CLAUDE.md` i `ae5b3308`, alle pushet. README-en fikk punktet om `.logs/`, og punktet om `.claude/skills/` sier at skillen kommer fra faglærer; i `tests/test_docker.py` er tallene 16 punkter og 31 lenker, og avtrykket for «Mappestruktur» er satt på nytt. Ingen API-kall utover kvotesjekken, `src/fetch_prices.py` er ikke kjørt, og `data/db/ose.db` er ikke rørt.

### Åpne punkter
- Jobben i Oppgaveplanlegging bygges 28.10 og går første gang torsdag 29.10 (svaret 27.10 kl. 20:58). Onsdag 28.10 hentes det med instruksjonen som vanlig.
- 3.5g (PR #103) venter på gruppen: BH3, en synlig linje til Docker og uv, og ECH7, «steg 4» i svarene under «Står du fast?», begge med dom medium. Flettingen er ikke avgjort.
- 3.5f: BH15, prøven av hovedveien (D1) etter flettingen; BH8, hjelpen har ikke eget svar når installasjonen av uv feiler; ECH2, at vinduet lukkes inne i ZIP-fila, er slått opp, ikke prøvd.
- 3.5e: BH3, hentingen mens den andre ekte versjonen kjører fra samme mappe, er ikke prøvd; BH8, to vinduer startet nesten samtidig.
- 8.6b: BH5, høyden på den smale flaten mellom 390 og 760 px; ECH5, linja «Mål mot børsen» når børsdagen før er mer enn 6 dager før eller ikke er den samme i kursene og kalenderen; BH5, ECH5 og VG4 i andre runde, overskriften for en bransje der ingen aksje har kurs.
