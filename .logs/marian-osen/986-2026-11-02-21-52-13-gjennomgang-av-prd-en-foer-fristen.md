# Gjennomgang av PRD-en før fristen

## 2026-11-02 kl. 21:52 — Marian Osen

### Oppgave
Instruksjonen kl. 21:42 i `docs/ai-prompts/2026-11-02.md`: lese `prd.md` mot repoet før fristen torsdag 5.11, etter beskjeden fra faglærer på emnesiden 2.11 og gruppens svar kl. 21:18: les først, rett onsdag. `prd.md` endres ikke i kveld.

### Plan
- Steg 0 og kvoten (regel 15), og instruksjonen i dagsfila.
- Beskjeden under E i `docs/innlevering.md` og to Rettet-linjer i oppføringen 30.10 i refleksjonsloggen, slått opp i dagsfila 30.10 og `git log` først.
- §8 lest selv mot `epics.md`, `docs/innlevering.md`, `src/boersdag.py` og `docs/kilder-og-rettigheter.md`. §4 og §5 lest av en underagent, og funnene stikkprøvd mot `prd.md`, `src/` og commitene.
- Funnene i en ny fil i `gjennomganger/`, med lenke fra `docs/innlevering.md`.

### Resultat
- Kvoten kl. 21:42 (20:42 GMT): 0 brukt og 20 igjen 02.11 i GMT, `extraLimit` 463. Ingen andre kall.
- `6748dc18`: instruksjonen i dagsfila.
- `88827911`: beskjeden og svaret kl. 21:18 under E i `docs/innlevering.md`, og to Rettet-linjer i 30.10 (kl. 12:00 var planen; instruksjonen kl. 12:21 heter «8.17a siste rettinger»).
- `95edc9e9`: `_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/gjennomganger/gjennomgang-2026-11-02-foer-fristen.md` med de 14 punktene i §8, 37 rader for resten (2 uten retting: front matter og lenkene) og 11 spørsmål, og lenken under beskjeden.
- Forslag for §8: lukk 5b og 9; utenfor v1 for 2, 4, 6, 8, 11, 12, 15 og 16; åpne med eier og frist: 13, 21, 22 og 25.
- Testene for dokumentene, de seks i `docs/kvalitetssikring.md`, ga 255 bestått før hver push. `prd.md` og koden er ikke endret.

### Åpne punkter
- Rettingen av `prd.md` onsdag 4.11, etter gruppens svar på de 11 spørsmålene i gjennomgangen.
- `sprint-status.yaml` henger etter `epics.md`: 2.13 står som review (flettet i `676fbc8b`), 9.5 som backlog (utgår 06.10), og 2.3c, 2.3d og 3.5a–h mangler.

## 2026-11-03 kl. 16:27 — Marian Osen

### Oppgave
Rette `prd.md` før fristen 5.11 etter gjennomgangen 02.11 og gruppens svar 02.11 kl. 22:15 (A–D), bare dokumenter og ingen nye krav (instruksjonen kl. 14:41 i dagsfila 03.11).

### Plan
- Svarene under spørsmålene i gjennomgangen, så §8, så R1–R35 med én datert linje ved hvert krav, slått opp på nytt.
- README-ens «Status», sprint-status, ny `docs/brukslogg.md` og `docs/brukertest.md` i hver sin commit.
- Linjene om at PRD-en er rettet, i gjennomgangen og i `docs/innlevering.md`.

### Resultat
- Kvoten kl. 14:41 (13:41 GMT): 0 brukt 03.11 i GMT og 20 igjen, med `extraLimit` 463. Ingen andre kall.
- `5a6141f3` (14:42) dagsfila, og `bdbfa260` (14:42) svarene A–D i gjennomgangen.
- §8 i `c075b54e` (14:45): 5b og 9 i «Lukket», og 2, 4, 6, 8, 11, 12, 15 og 16 i den nye tabellen «Utenfor v1», med punktteksten ordrett (kontrollert linje for linje) og eier Gruppen der feltet var tomt eller en plassholder. Linja om én samlet `bmad-code-review` under punkt 22, og Rettet-linjer ved oppsummeringen og «Om eierfeltet» (R34). «Må avgjøres før arbeidet går videre» er tom. Alpha Vantage i `docs/kilder-og-rettigheter.md` i `8a006032` (14:45), uten avkrysning.
- R1–R7 i `a79bd455`, R8–R13 i `b0cfa6b2`, R14–R25 i `3c74eff1`, R28 med brukslogga i `7d36abef`, R26, R27 og R29–R33 i `b33c1ae5`, og R35 i `d8524821`. Slått opp på nytt: FR-501 var ikke merket for plan B, som gjennomgangen sa, så overskriften i §4.5 er merket. `compose.yaml` kom i story 3.1 (`a2ecee8a`), ikke 3.2. Svaret 21.10 kl. 18:33 står ikke under en story i `epics.md`.
- R35: «Kort fortalt» har høyst 400 ord (`test_hoeyst_400_ord`) og hadde 396, så linjene står like under den, etter svaret kl. 16:25. README-ens «Status» i `7f67d336`: «Ferdig» har 8 punkter, som er taket, så jobben og målingen står som en setning etter «Rundt appen er dette også ferdig».
- `docs/brukslogg.md` er ny, med lenke i «Dokumentene». Avtrykket for «Dokumentene» i `tests/test_docker.py` er satt på nytt, som da `docs/brukertest.md` kom.
- `sprint-status.yaml` i `fb6d1051`: 2-13 done, 2-3c, 2-3d, 3-5a og 3-5d–h done, og 3-5b og 3-5c backlog med kommentar om at de ikke bygges. 9-5 står som før, med kommentaren om at den utgår. `docs/brukertest.md` i `ef5f627a`.
- `prd.md`: 126 linjer lagt til fra `5a6141f3`, og 11 fjernet: de ti flyttede radene og `updated`. `status` står som final, og 16 lenker og ankre fører fram. Testene som leser `prd.md`, og de seks for dokumentene ga 684 bestått før hver commit som endret `prd.md`. Hele settet er ikke kjørt.
- Linjene om rettingen i gjennomgangen og i `docs/innlevering.md` i `6432e605` (16:27).

### Åpne punkter
- Brukslogga starter 4.11: én linje for hver dag gruppen bruker appen.
- R29: hvilken uke som teller for «Én ukes drift er logget», og antallet rader i `ki_logg` for den, er ikke regnet ut.
- `sprint-status.yaml` har ingen rad for 8-0f, som er flettet (`238ef186`, PR #102).
