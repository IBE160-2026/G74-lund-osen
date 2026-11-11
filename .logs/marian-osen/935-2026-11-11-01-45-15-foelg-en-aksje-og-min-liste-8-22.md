# «Følg en aksje» og «Din egen liste» (8.22)

## 2026-11-11 kl. 01:45 — Marian Osen

### Oppgave
Del B 10.11 i vindu 4 er instruksjonen kl. 16:26, etter gruppens svar kl. 13:38, 14:43, 14:59, 15:22, 15:57 og 17:42. Den gjelder story 8.22: faste bransjer for alle aksjene, «Følg en aksje» med hele lista og «Din egen liste» som tre stegkort. Senere kom fire tillegg:
- kl. 17:16 om demoen
- kl. 17:46 om testene i kveld
- kl. 17:47, etter at vinduet ble lukket ved en feil
- tillegg 4 kl. 22:52, etter svaret kl. 22:50: steg 2 skal være som på tavla, men uten felt

Fortsettelsen kl. 20:43 sa at PR-en skulle gjøres ferdig så tidlig som tillegget om testene tillot. Ingenting skulle flettes (svaret kl. 14:59). Instruksjonene og tilleggene står ordrett i scratchpad-mappa til økta. De føres i dagsfila med flettingen, i en egen instruksjon etter gruppens ja.

### Plan
- Spesifikasjonen er [spec-8-22-foelg-en-aksje-og-min-liste.md](../../_bmad-output/implementation-artifacts/spec-8-22-foelg-en-aksje-og-min-liste.md), med spørsmål 1–14 og triagen.
- Arbeidet foregikk i worktreen `G74-lund-osen-8-22` på grenen `8-22-foelg-en-aksje-og-min-liste`, PR #138.
- Delene A–D og demoen ble fulgt av en gjennomgang med Blind Hunter, Edge Case Hunter og Verification Gap, triage, mutanter og hele settet i deler.
- Tillegg 4 ble gjort på samme måte.

### Resultat
- **Kvotesjekken kl. 16:26:** 0 kall brukt 10.11 i GMT, 20 igjen og 463 i `extraLimit`. Ingen andre kall. `ose.db` ble bare lest med `mode=ro`, og sha256 var den samme før og etter hver gang.
- **Grenen:**
  - spesifikasjonen og del A–D: `87d49f1a`, `7d382c77`, `74c1cfe3`, `5c626be3`, `644dc156` og `7100df7b`
  - demoen og bildene: `078387e8` og `59a84ee4`
  - rettingene etter gjennomgangen og triagen: `cde3c545` og `d4c393b5`
  - main flettet inn: `7b974036`, `046635c1`, `b91a0c48` og `02843a1d`
  - «Demo Børs» på bekreftelsen: `58ef3679`
  - spesifikasjonen etter flettingen: `a251c087`
  - tillegg 4 med rettingene og testene: `508a3a16`, `7eccce1c` og `f75fa1a3`
- **Gjennomgangen av 8.22:** 36 funn. Det høye funnet var at forslagene ble skjult av søket, og det er rettet. ECH5 står som spørsmål 12 og ECH12 som spørsmål 13.
- **Gjennomgangen av tillegg 4:** 11 funn. Funnene på middels er rettet: teksten sier «virket» og «minst», byttet gjelder også Docker, og testen for AD-10 er strengere. VG2 er bare delvis rettet og står som spørsmål 14 (regel 25).
- **Tillegg 4:** steg 2 viser «Nøkkelen virket ved siste henting …, som brukte minst … av 20 kall». `valg.siste_henting` leser bare `kursserie.hentet` og `indeksserie.hentet`, uten kall og uten `.env`. Den ekte basen ga 10.11 og 19 kall.
- **Testene etter flettingen av 2.13b ble først kjørt kl. 21:31, etter tillegget kl. 17:46.** VG3-testen for demoen feilet. Den fant ingen kode på bekreftelsen, og bekreftelsen sa «Oslo Børs» i demoen. Begge er rettet i `58ef3679`. Tre nye tester for steg 2 feilet ved første kjøring kl. 00:07 og ble rettet i `f75fa1a3`.
- **Hele settet ble kjørt i fire deler, med summen lik `--collect-only` og 0 feilet hver gang:**
  - 5007 på `58ef3679`
  - 5014 på `f75fa1a3`
  - 5136 på `b91a0c48`
  - del 1–3 på `046635c1`; del 4 rakk ikke å starte før kl. 22:15 og ble tatt på `f75fa1a3`
- **Mutantene:** A–D og demoen ble fanget før gjennomgangen. Etter den ble alle disse fanget, og filene var like HEAD etterpå:
  - forslagene skjules av søket
  - ønsker for MULTI og SCOIN tas i bruk
  - `bransjen` slipper MULTI og SCOIN gjennom
  - bekreftelsen sier «Oslo Børs»
  - steg 2 teller alle dagene
  - steg 2 leser nøkkelen
- **Bildene:** alt i `docs/appen/` ble tatt på nytt med DevTools-protokollen etter hver fletting og etter tillegg 4. «Følg en aksje» er 1368 px og «Din egen liste» 1714 px. Notatene i Min liste ble tatt på nytt fra 8.21 og har samme høyde. PR-bildene ligger på grenen `pr-8-22-bilder`.
- **Feil underveis:**
  - Da PR-bildene ble lagt på egen gren, slettet en `git push origin :refs/heads/pr-8-22-bilder` med tom variabel bildegrenen på GitHub. Den ble laget på nytt og spolt fram uten force.
  - Kl. 22:14 ble `git ls-remote` kjørt i stilletiden kl. 22:10–22:20. Den leste bare.
  - Kl. 01:44 ble henting og push sendt samtidig. Grenen ble derfor pushet mens main var to loggcommits foran. De ble flettet inn i `02843a1d` før neste push.
  - Ventekommandoen ble stoppet av lite minne før kl. 19:34 og startet på nytt etter fortsettelsen kl. 20:43.
- **Etter lukkingen kl. 17:47:** tilstanden ble sjekket, og arbeidskopien var ren. De tre gjennomgangene, som hadde stoppet, ble kjørt på nytt.

### Åpne punkter
- 8.22 venter på gruppens svar på spørsmål 1–14 i spesifikasjonen. Det gjelder også ECH5 (12) og VG2 (14) på middels. Ingen fletting før svaret (kl. 14:59).
- Instruksjonen kl. 16:26, tilleggene og fortsettelsen kl. 20:43 skal føres i dagsfila 10.11, og svaret kl. 22:50 i `epics.md`, når del B flettes.
- Svarene kl. 13:54 og 14:53, som instruksjonen viser til, er ikke funnet i repoet eller i scratchpad-mappene.

## 2026-11-11 kl. 14:07 — Marian Osen

### Oppgave
Instruksjonen 11.11 kl. 11:56 ba om tre ting:
- main inn i grenen for del B (8.22, PR #138);
- tillegg 3 og 5 til del B, gitt 10.11 kl. 22:44 og 22:55, som aldri kom fram til vindu 4;
- spesifikasjonen med svarene kl. 13:54, 14:53, 22:44 og 22:55.

Windows Update startet maskinen på nytt kl. 04:29, og vinduet ble tatt opp igjen med /resume. Instruksjonen står ordrett i scratchpad-mappa. Ingenting flettes til main før gruppens ja (svaret kl. 14:59).

### Plan
- Steg 0: statusen ble sjekket. Fem commits fra main manglet før kl. 10:29, og den sjette (`ce33771c`) kom kl. 11:55.
- Kvotesjekken (regel 15): `apiRequestsDate` sto på 10.11, så 0 kall var brukt 11.11, 20 var igjen og 296 sto i `extraLimit`. Ingen andre kall ble gjort.
- Arbeidsgangen var main inn, så tillegg 3 i fire deler med tester og mutanter, så én gjennomgang med tre gjennomgåere, så tillegg 5 og bildene, og til slutt spesifikasjonen, hele settet, push og CI.

### Resultat
- **Main inn:** `45111d53` (8.23, del A) og `8aec5c4b` (loggen og Utført-linja for del C).
  - Konfliktene i `45111d53` var de ventede, og begge sider er beholdt.
  - Én test for den faste bransjen leste radene som `<li>` og leser nå tabellraden fra 8.23.
  - Hele settet ga 5206, lik `--collect-only`, med den ene feilen rettet og fila kjørt på nytt.
  - CI var grønn på `45111d53`.
- **Tillegg 3:**
  - Sorteringen i stedet for «Mest omsatt»: `013d1974`.
  - Flere bransjer, og det valgte i oransje med hakemerke: `2dbe3a4d`.
  - Radene som tabellen på oversikten: `42ebdc5a`.
  - De ferdige listene som knapper, og siden «Er du sikker?»: `05b527da`.
  - Rettingene etter gjennomgangen: `05cd01e4`.
- **Gjennomgangen:** 14 funn fra Blind Hunter, 12 fra Edge Case Hunter og 12 fra Verification Gap. Triagen står i spesifikasjonen. ECH2 står åpent som spørsmål 15 (regel 25): den oransje fargen er også fargen for 3 av 3.
- **Mutantene:** ni ble fanget, og filene var like HEAD etterpå.
- **Tillegg 5 og bildene (`66fff077`):**
  - `folg-en-aksje-390-demo.png` (1573 px) og `notatene-brfe-390-demo.png` (utsnitt, 1354 px), i README-en og i «Mappestruktur».
  - Alle bildene er tatt på nytt med DevTools-protokollen. «Din egen liste» er 1454 px og «Følg en aksje» 1252 px.
- **Spesifikasjonen (`b4f0b773`):**
  - Svarene kl. 13:54 og 14:53 står nå med kilden.
  - Spørsmål 5 og 7 er bortfalt med grunnen.
  - Spørsmål 15–18 er nye.
- **Testene og CI:** hele settet i fem deler på `b4f0b773`, med 5217 tester, lik `--collect-only`, og 0 feilet. Pushet `8aec5c4b` kl. 14:02, og CI var grønn kl. 14:07.
- **PR-en:** bildene ble tatt på nytt fra demoen på `pr-8-22-bilder` (`566e46c6`, spolt fram uten force). Kommentaren med bildene og spørsmålene står i PR #138.
- **Feil underveis:**
  - Del 2 av hele settet ble stoppet av tidsgrensen etter sju minutters venting på en annen pytest, og ble kjørt i to halvdeler.
  - To tester fra 8.11c leste den gamle radteksten etter del 3. Det ble funnet og rettet i del 4.
  - Loggfila til 8.25 på main har også nummeret 935.

### Åpne punkter
- 8.22 venter på gruppens svar på spørsmål 1–18 i spesifikasjonen. 5 og 7 er bortfalt. ECH5 (12), VG2 (14) og ECH2 (15) er på middels. Ingen fletting før svaret.
- Disse føres i dagsfila når del B flettes:
  - instruksjonen kl. 16:26, tilleggene og fortsettelsen kl. 20:43 i dagsfila 10.11;
  - instruksjonen 11.11 kl. 11:56 i dagsfila 11.11.
- Svarene kl. 22:44, 22:50 og 22:55 føres i `epics.md` når del B flettes.
