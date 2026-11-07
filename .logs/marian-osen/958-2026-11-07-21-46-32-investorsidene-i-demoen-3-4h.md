# Investorsidene i demoen, 3.4h

## 2026-11-07 kl. 21:46 — Marian Osen

### Oppgave
Fortsette instruksjonen kl. 20:17 (story 3.4h) fra der den stoppet kl. 20:53, da Claude Code falt ut. Instruksjonen kl. 20:57 ba om å fullføre steg 2 i worktreen `G74-lund-osen-3-4h`, kontrollere skriftene tabell for tabell mot kildene, kjøre hele settet alene (fil for fil ved for lite minne), committe med mutanter, gå gjennom endringene med tre lag, føre triagen og åpne PR med grønn CI. Den skulle stoppe før flettingen.

### Plan
- Kvotesjekk, og så steg 0: tilstanden på main og i worktreen.
- Steg 1: instruksjonen og linja om stoppen kl. 20:53 i dagsfila. Tallene er slått opp i transkripsjonen fra økta som falt ut.
- Steg 2: diffen i worktreen og spesifikasjonen. WOFF-filene kontrollert mot arkivene fra forrige økt, lisensene og OFL-FAQ 2.2.1 lest, og NewsWeb søkt opp i malene.
- Steg 3: hele settet, commit, mutanter, PR, gjennomgang, rettinger, settet fil for fil, triage og CI.

### Resultat
- Kvote: 0 kall brukt 07.11 i GMT og 20 igjen (`extraLimit` 463). Ingen andre API-kall.
- Main: `e9bead13`, med instruksjonen kl. 20:57 og linja om stoppen kl. 20:53.
- Grenen `3-4h-investorsidene-i-demoen`, PR #120 (ikke flettet):
  - `ac0944f9`: delene A–G.
  - `5cb46117`: delen om det som er bygget i spesifikasjonen, og linja i `spec-10-5`.
  - `72efb6e8`: rettingene etter gjennomgangen.
  - `57ed1431`: triagen.
- Skriftene. Alle ti WOFF-filene har tabeller som er byte for byte like TTF-ene i arkivene, og sha256 for arkivene stemmer med radene i kildene. Ingen av filene har WOFF-metadata eller privat blokk.
  - Inter Display: Inter 4.1, `Inter-4.1.zip` fra rsms/inter v4.1. OFL 1.1, uten reserverte navn.
  - Lora: Lora 3.021, `Lora.zip` og `OFL.txt` fra cyrealtype/Lora-Cyrillic v3.021. OFL 1.1, med det reserverte navnet «Lora».
  - Liberation Mono: Liberation 2.1.5, `liberation-fonts-ttf-2.1.5.tar.gz` fra liberationfonts 2.1.5. OFL 1.1, med de reserverte navnene Liberation, Arimo, Tinos og Cousine.
- Testene:
  - Hele settet alene før `ac0944f9` (21:03:09–21:15:01, med 3,9 GB ledig av 15,7 GB): 4568 bestått, 24 hoppet over og 0 feilet.
  - Fil for fil før `72efb6e8` (21:27:38–21:40:04, med 2,8 GB ledig): 4569 bestått, 24 hoppet over og 0 feilet, uten at noen fil måtte kjøres på nytt.
  - Dokumenttestene ga 258 bestått før hver push.
- Mutantene:
  - 7 på `ac0944f9`, én per del (A–G).
  - 5 på `72efb6e8`: VG1, VG2, BH2, BH3 og BH8.
  - Alle ble fanget, og hver fil var lik HEAD etterpå.
- Gjennomgangen: 16 funn fra Blind Hunter, 7 fra Edge Case Hunter og 2 fra Verification Gap, ingen på høy.
  - Middels, alle rettet: VG1/BH4, VG2/BH5, BH2 og BH3.
  - Utsatt: ECH7 og BH16 er kommentarer i filer som inngår i avtrykket bak bildene, og BH7 gjelder vedlegget.
  - Ingen spørsmål til gruppen før flettingen.
- CI: grønn på `5cb46117` (run 42410394337) og på head-en `57ed1431` (run 42412331838). Jobben `pytest` ga 4562 bestått og 31 hoppet over.
- `data/db/ose.db`, oppgaven, worktreen `G74-lund-osen-jobb` og `_privat/` er ikke rørt. Ollama er ikke startet, og ingen andre programmer er stoppet.

### Åpne punkter
- PR #120 (3.4h) venter på gruppen før flettingen.
- Etter flettingen: U84 i `docs/ux-logg.md` får en datert linje, og vedlegget i `docs/kvalitetssikring.md` får de 12 mutantene i 3.4h (BH7).
- ECH7 og BH16 fra 3.4h: kommentaren om U66 i `aksje.html` og kommentaren ved `_RUTER_MED_BASE` i `app.py` rettes neste gang filene endres, fordi de inngår i avtrykket bak bildene.
