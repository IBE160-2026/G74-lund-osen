# «Vis meg rundt» spiller av siden, knappene øverst og funnene fra demoprøven (story 8.26)

## 2026-11-11 kl. 21:57 — Marian Osen

### Oppgave
Instruksjonen kl. 18:01, etter gruppens svar 11.11 kl. 16:58, 17:06, 17:12 og 17:21, med tilleggene 1–4 (kl. 18:02), 6 (kl. 19:43), 8 (kl. 19:56), 10 (kl. 20:18) og 12 (kl. 20:35). Ny story med spesifikasjon, spørsmål og forslag, tester, mutanter, bilder før og etter, gjennomgang, hele settet, PR og CI grønn, uten fletting før gruppens ja.

### Plan
- Kvotesjekken først (regel 15). Story 8.26 på grenen `8-26-vis-meg-rundt-spiller-av-siden` i worktreen `G74-lund-osen-8-26`, fra origin/main (`7fd5320c`).
- Spesifikasjonen: `_bmad-output/implementation-artifacts/spec-8-26-vis-meg-rundt-spiller-av-siden.md`, med delene, spørsmålene 1–11, mutantene og tre triager.
- Delene én etter én, hver med tester i `tests/test_vis_meg_rundt_8_26.py` og én mutant, og så gjennomgangene.

### Resultat
- Kvoten kl. 18:02: 0 kall brukt i dag (GMT), 20 igjen, `extraLimit` 296. Ingen andre API-kall.
- Del 1 (`e06fa3e6`): «Vis meg rundt» åpner boksen fra omvisningen med stegene for siden, med «Ferdig» og «Spill av hele omvisningen» på siste steg; knappene står i raden øverst. Rettet-linjer under 8.9.
- Del 2 (`d24de09a`): hjelpevinduet, brikkene i «Slik leser du tabellen», «?» ved Hovedindeksen, «Dine egne aksjer», beskjeden om taket, KI-bryterne oransje; punktet om spørsmål 5 i 8.2b lukket.
- Del 3 (`1b180fcf`): fotnoten og innledningen på aksjesiden tatt bort, NFR-06 i innledningene.
- Del 4 og tillegg 8 (`4d2ee9ec`, `66163a36`): «ingen kurser ennå» fra én konstant overalt, med hvorfor og navnet fra demodataene.
- Del 5 (`c922edcc`): stjernen ved «Følg» med migrasjon 0013, aksjene som venter nederst i tabellen, «appen følger».
- Del 6 (`8846fbc1`): filteret på signalet tatt bort (Rettet-linjer i PRD-en og under 8.11 og 8.23), «Den ekte versjonen» i en ny fane.
- Tillegg 6 (`d1a9e775`), 10 (`bbce8602`) og 12 (`67ea74e2`): ankrene, lenkefargen, og «Din egen liste» som på tavla med siden `/eodhd-demo` i demoen (Rettet-linje for spørsmål 9 i 8.22).
- Mutanter: én per del og for tilleggene 6, 8, 10 og 12, alle fanget, og hver fil lik HEAD etterpå.
- Gjennomganger: tre runder (35, 30 og 30 funn). Ett høyt (VG1 i andre runde) og flere på middels er rettet; VG1 i første runde og ECH2 i andre står åpne som spørsmål 9 og 10.
- Main (10.10) ble flettet inn i `aebf1f47`, med bildene tatt på nytt og høyden på oversikten ved 390 px målt (4534). Hele settet i seks deler etter det: 5439 bestått, 37 hoppet over (5476, likt `--collect-only`).
- PR #146 med bildene fra `pr-8-26-bilder` (før og etter, også ved 390 px). Ikke flettet.
- Tilleggene 5, 7, 9, 11, 13 og 14 kom aldri til vinduet; tillegg 15 (kl. 20:46) stoppet i steg 0, fordi det bygger på tillegg 14. Instruksjonen og tilleggene ligger ordrett i scratchpad og føres i dagsfila 11.11 med flettingen.
- Ventingen: ingen ventekommando ble stoppet. Ingen pytest kl. 22:15–23:50 og ingen git i stilletidene.

### Åpne punkter
- PR #146 venter på gruppens svar på spørsmål 1–11; med migrasjon 0013 kan den bare flettes kl. 23:50–23:58.
- Spørsmål 9 (VG1, middels): testene av boksen i nettleseren søker i kildeteksten.
- Spørsmål 10 (ECH2, middels): forklaringen på hvorfor en aksje er uten kurser, som tillegg 8 har den.
- Tilleggene 5, 7, 9, 11, 13 og 14 er ikke limt inn i vinduet, og tillegg 15 venter på tillegg 14.

## 2026-11-12 kl. 00:59 — Marian Osen

### Oppgave
Tilleggene 5, 7, 9, 13, 14, 16, 17, 18, 19 og 20 til 8.26, og tillegg 15 som stoppet kl. 20:46, etter gruppens svar og ønsker 11.11 kl. 18:09–22:20. Tilleggene kom til vinduet 11.11 kl. 22:05–22:25 og ble lagret ordrett i scratchpad med klokkeslett fra `date`. Tillegg 11 kom aldri.

### Plan
- Tilleggene i den rekkefølgen de kom, med 17 først. Steg 1 i tillegg 18 (hjelpetekstene) kom etter de andre, og bilderunden i tillegg 16 til slutt, etter grønn CI.
- Pytest var stengt kl. 22:15–23:50, så testene ble skrevet før og kjørt etter kl. 23:50. Gjennomgangen med de tre agentene ble gjort uten pytest.

### Resultat
- Tillegg 17 (`301d92ca`): brikkene i «Følg en aksje» med antallet, grå ved 0 og filtrering med en gang (`FOLGLISTA` i `hjelp.js`). Overskriften og linja om 3 av 3 følger dagen med «Vis dagen». «Signalet er ikke regnet ennå» for Varde Systemer. «Oppdatert …» på alle sidene med basen.
- Tillegg 18: hjelpetekstene på høyst 50 ord og tre setninger, uten «basen», «kilden» og «kontrollsjekken», med en tabell før og etter i spesifikasjonen. Bryteren «Vis KI-tekst» er lik på alle tre stedene, og stegene om signalstyrken og retningen merker bare kolonnen.
- Tillegg 19: eksempelboksen i demoen er borte (Rettet-linje i spesifikasjonen for 8.23). Tillegg 20: KI-stegene, hele omvisningen uten stegene som gjentas, og README-en.
- Tillegg 5 og 7: setningen om den første knappen og «Uten ramme/ring: 0 eller 1 av 3.». Tillegg 9 og 13 var alt gjort; testene dekker dem nå. Tillegg 14 og 15: «Følg flere aksjer» som tegnet.
- Gjennomgangen (Blind Hunter 15 funn, Edge Case Hunter 9, Verification Gap 12). To høye (VG1/VG2, eldre tester) og VG3 (vinduene over 60 ord) er rettet. VG3 er også spørsmål 22. Rettingene står i `fb43d76a`, og triagen i spesifikasjonen.
- Testene etter kl. 23:50 viste regler fra før som tekstene og README-en brøt: tre setninger (8.0c), fem avsnitt i «Kom i gang» (3.5i), 20 ord under «Ekstra», ordene fra utdraget 08.11 og designforslaget, og «uten ramme» i hjelpen. Alt er rettet i `7582131f` og commiten etter.
- Mutantene M13–M26, én per tillegg: alle fanget, og hver fil var lik HEAD etterpå.
- Hele settet i seks deler: 5524 bestått og 24 hoppet over (5548, likt `--collect-only`). Bildene i `docs/appen/` er tatt på nytt med høydene og avtrykkene.
- CI er grønn på `6b2b5067`. Bilderunden i tillegg 16 ligger på bildegrenen med kontaktark, og PR #146 har lista. Ikke flettet.
- Brudd på rammene i instruksjonen: `git status` kl. 22:11 og `git archive` kl. 22:16 i stilletiden for git, begge bare lesing. Mutantene kl. 00:06, `--collect-only` kl. 00:13 og testene kl. 00:28–00:30 startet mens et annet vindu kjørte pytest; etter det har hver kjøring en betingelse foran.

### Åpne punkter
- Spørsmål 12–22 i spesifikasjonen venter på gruppen. Spørsmål 22 (VG3, middels) står åpent til gruppen har svart (regel 25).
- Tillegg 11 er ikke limt inn i vinduet.
- Ved 390 px er tabellen i «Følg en aksje» kuttet til høyre («Føl…»), også før 8.26 (kontaktarket på bildegrenen).

## 2026-11-12 kl. 11:03 — Marian Osen

### Oppgave
Tillegg 21 (gruppens svar 12.11 kl. 09:58 om «Brukerutfall» i §7 i PRD-en) og tillegg 22 (svaret kl. 10:16 på spørsmålene i PR #146) til 8.26. Begge kom til vinduet 12.11, kl. 10:04:34 og 10:20:02 (fra `date`), og er lagret ordrett i scratchpad. Tillegg 22 sier ja til flettingen kl. 23:50–23:58 med begge tilleggene.

### Plan
- Bilder før fra demoen på HEAD, så tillegg 21 i `hjelp.js`, tester, README-en og hjelpen; deretter tillegg 22.
- Én commit per tillegg, én mutant per tillegg mot HEAD, hele settet i seks deler, push og CI grønn før kl. 22:10. Flettingen kl. 23:50–23:58, og føringen på main etterpå.

### Resultat
- Tillegg 21 (`500e795a`): tilbudet første gang starter «Vis meg rundt» for oversikten (`OMVISNING.TILBUDET`, `visSiden`), ikke hele omvisningen, og kommer ikke uten knappen. Det siste steget i «Vis meg rundt» på oversikten har linja om å klikke et navn under «Skilte seg ut» (`OMVISNING.videre`), og «Ferdig» gir fokus til det første navnet, eller til tabellen når ingen aksje står der. Prøvd i Edge mot demoen: tilbudet gir steg 1 av 7, og «Ferdig» gir fokus til Brattfjell Energi, eller til `#aksjene` når tabellen er sortert. README-en, hjelpen, Rettet-linjer under svaret 11.11 kl. 13:49 i spesifikasjonen for 8.25 og i `epics.md`, og del 13.
- Tillegg 22 (`5dd9af96`): forklaringen på en aksje uten kurser sier at EODHD ikke har gitt kurser, og at appen slutter å følge en aksje brukeren har valgt selv hvis EODHD heller ikke gir kurser ved neste henting (`valg.uten_rader`), uten «nettopp er lagt til». Svarene i spesifikasjonen, og VG1, ECH2 og VG3 lukket i triagen.
- Bildene i `docs/appen/` er like (16 av 16); bare avtrykkene er nye. Bildene før og etter fra demoen ligger i `tillegg-21/` på bildegrenen (`c3da99f6`), og PR-en har dem.
- Mutantene M27 (linja i hele omvisningen) og M28 (den gamle grunnen tilbake) ble fanget, og filene var like HEAD etterpå (`git hash-object`, og sha256 uten CR).
- Hele settet i seks deler på `5dd9af96`: 5540 bestått og 24 hoppet over (5564, likt `--collect-only`). Den første runden etter tillegg 21 viste at linja under «Ekstra» må si «seks av sidene» (VG5 i 8.25), og avtrykkene.
- Brudd: den første runden av hele settet ble stoppet da tillegg 22 kom, fordi den testet en arbeidskopi som endret seg. Del 3 av den runden fortsatte i egen venv til tidsgrensen, fordi stoppen av prosessen ble avslått; mine neste kjøringer ventet på den med `vent.sh`.

### Åpne punkter
- PR #146 flettes 12.11 kl. 23:50–23:58, og dagsfilene 11.11 og 12.11, `epics.md`, sprint-status og README-en føres på main etterpå.
- Ved 390 px er tabellen i «Følg en aksje» kuttet til høyre, også før 8.26 (fra før).

## 2026-11-13 kl. 00:07 — Marian Osen

### Oppgave
Tillegg 23 til 8.26 (gruppens svar 12.11 kl. 16:23 og ønsket kl. 16:24, limt inn kl. 16:31:10), om README-en som inngangen for faglærer, og flettingen av PR #146 kl. 23:50–23:58 etter tillegg 22, med føringen på main etterpå. Tillegg 24 (limt inn kl. 17:37:51) gjelder tiden etter flettingen og føres i egen seksjon.

### Plan
- Tillegg 23 på grenen: to linjer under «Til faglærer», «Versjon 1 er ferdig» i ingressen og «Status», fire rader i tabellen om demoen og den ekte versjonen, og antakelsen i `docs/innlevering.md`.
- Hele settet, ruff, push og CI grønn før kl. 22:10, og ingen commits på grenen etter det. Sjekk av main kl. 22:00, flettingen låst til den testede head-en kl. 23:50–23:58, og føringen på main.

### Resultat
- Tillegg 23 på grenen: `acce9574` (hovedflyten og brukertesten under «Til faglærer»), `66ea2977` (versjon 1 er ferdig), `431f565d` (forskjellene i tabellen), `ddbd2c91` (`docs/innlevering.md`) og `6d1e138f` (svaret og del 15 i spesifikasjonen). Main (tilbakemeldingen på PRD-en og `technology.md`) ble flettet inn i `82f50471` uten konflikter.
- Hele settet i seks deler på `82f50471`: 5551 bestått og 24 hoppet over (5575, likt `--collect-only`). ruff er ren. CI grønn på head-en (run 43261288679) kl. 17:52.
- Kl. 22:00:10 var main uendret (`a93c668f`), og PR-en kunne flettes. Ventekommandoen til kl. 23:50 ble stoppet av lite minne og startet igjen kl. 22:15, etter instruksjonen kl. 18:01.
- PR #146 er squash-flettet i `719e5f07` kl. 23:51:14, låst til `82f50471`. Treet på main var likt head-en (0 linjer i diffen). Testene for dokumentene på main: 2766 bestått, 7 hoppet over.
- Føringen på main: dagsfila 11.11 med instruksjonen kl. 18:01 og tilleggene 1–20 (`cc289203`), done og storyen med svarene i `epics.md` (`02ea922e`), og dagsfila 12.11 med tilleggene 21–24 og spørsmålene kl. 20:52 og 23:06 (`19a4d524`). README-en hadde 8.26 under «Ekstra, ferdig» fra grenen.

### Åpne punkter
- Bunnteksten i appen sier fortsatt «Appen er under utvikling og ikke ferdig.» (`UNDER_ARBEID` i `src/app.py`), mens README-en sier at versjon 1 er ferdig. Tillegg 23 nevnte ikke koden, så den er ikke endret.
- Faglærers `tilbakemelding-prd.md` (lagt til 12.11) er ikke lenket i «Dokumentene» ennå, slik regel 17 sier.
- Faglærers `technology.md` i arkitekturmappa (lagt til 12.11) beskriver et annet prosjekt (pytagoras-website-v2).
- Ved 390 px er tabellen i «Følg en aksje» kuttet til høyre (fra før).
