# Story 2.12: velge og bytte aksjer

## 2026-11-08 kl. 18:00 — Marian Osen

### Oppgave
Instruksjonen kl. 14:05 08.11, story nummer tre av sju: spesifikasjon og bygging av 2.12 på grenen for 2.11, med PR, stopp før flettingen. Lista over Oslo Børs leses fra `data/proever/symbolliste-OL-2026-10-22.json` uten kall og uten at fila committes, brukeren velger bransjen, taket er 18, og README-en får et bilde fra demoen av «Din egen liste».

### Plan
- Spesifikasjon etter storyen, svarene 08.11 og utdraget §1–§2.
- Migrasjonen 0010, porten for ønskene, hentingen som tar dem i bruk, sidene, demoen og bildet.
- Hele settet alene, mutantene, gjennomgangen, triage, push, PR og CI.

### Resultat
- Grenen `2-12-velge-og-bytte-aksjer` i worktreen `G74-lund-osen-2-12`, fra grenen for 2.11: `f87c29ea` (byggingen), `1f936f3a` (rettingene etter gjennomgangen) og `f09e0c6f` (mutantene). PR #124, ikke flettet, med basen main så CI kjører; diffen viser 2.11 også til PR #123 er flettet. CI grønn på `f09e0c6f` (run 42502444489).
- Hele settet alene: 4633 bestått, 24 hoppet over og 0 feilet (17:15:45–17:25:33), og etter rettingene 4646 bestått, 24 hoppet over og 0 feilet (17:39:18–17:49:44). Kjøringen før det ga 14 feil, som ble rettet.
- Mutantene: åtte på `f87c29ea` og tolv på `1f936f3a`, alle fanget, og hver fil var lik HEAD etterpå.
- Gjennomgangen: Blind Hunter 11, Edge Case Hunter 11 og Verification Gap 12 funn. De to høye (lista kunne få 19 ved å angre et ønske om å fjerne, og «Utenfor målingen» sto bare i tabellen) er rettet. Middels er rettet, utenom BH6/ECH5 (en aksje som tas inn igjen), som er spørsmål 6 i 2.11 (regel 25).
- Bildet `docs/appen/din-egen-liste-demo.png` er nytt, og Min liste og oversikten ved 390 px er tatt på nytt med de nye delene.
- `data/db/ose.db` er ikke rørt. Fila med lista over Oslo Børs er ikke committet.

### Åpne punkter
- PR #124 (2.12) er ikke flettet; den flettes etter PR #123, og gruppen går gjennom spørsmålene først.
- Mandag 09.11: kjør `uv run python src/fetch_prices.py --les-boerslista` én gang før aksjer kan velges.
- `index.html` får en konflikt mellom 10.6 og 2.12 ved flettingen; rekkefølgen er «Dine egne aksjer» og så «Børsdagen kort fortalt».
- Spørsmål 11: hentingen måler ikke omsetningen for en ny aksje, så den står som «Utenfor målingen» til den er målt.
