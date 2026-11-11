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
