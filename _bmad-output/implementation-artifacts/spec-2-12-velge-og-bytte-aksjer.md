---
title: 'Story 2.12: Velge og bytte aksjer, «Dine egne aksjer» og «Din egen liste»'
type: 'feature'
created: '2026-11-08'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '4594dfa2'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designutdrag-2026-11-08.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-11-lista-leses-fra-basen.md'
---

Skrevet 08.11 i instruksjonen kl. 14:05 (`docs/ai-prompts/2026-11-08.md`). Gruppen har sagt at Claude Code bygger etter forslagene i spesifikasjonene, og at de gås gjennom før flettingen (svaret 08.11 kl. 12:32). Storyen bygger på grenen for 2.11 og tas i bruk fra mandag 09.11 (svaret kl. 11:57).

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Hva er en «egen» aksje?** *Forslag:* en aksje i lista som er tatt inn fra et ønske på siden. Den merkes «Egen» i tabellen og står under «Dine egne aksjer». «Ikke blant de 15 i `AKSJEUNIVERS`» ville gjort alle selskapene i demoen til egne. En av de 15 som er byttet ut og tatt inn igjen fra siden, er egen.
2. **Hvor kommer lista over Oslo Børs fra?** Avgjørelsen 22.10 kl. 23:14 sier at hentekommandoen lagrer den i basen, og at siden bare viser tickere som står der. *Forslag:* en ny tabell `boersliste`, fylt med kommandoen `uv run python src/fetch_prices.py --les-boerslista`, som leser `data/proever/symbolliste-OL-2026-10-22.json` uten kall. Bare typen «Common Stock». Fila committes ikke (regel 10). Mandag kjører gruppen kommandoen én gang før aksjer kan velges.
3. **Ønsket.** *Forslag:* webserveren skriver bare i en ny tabell `oenske` (AD-3): følg, fjern eller bytt, med tickeren, navnet og bransjen brukeren valgte. Kveldens henting tar ønskene i bruk før den leser lista, og er fortsatt eneste skriver av `aksje`, kurser og vurderinger. Et ønske som ikke er tatt i bruk, kan angres, og da slettes raden.
4. **Bransjen.** *Forslag:* brukeren velger en av de 13 i dialogen (svaret kl. 11:57), og ingen forslag (NFR-06). Triggeren fra 2.11 avviser alt annet.
5. **Taket.** *Forslag:* aksjene i lista pluss ønskene om å følge, minus ønskene om å fjerne, er høyst 18. Den nittende avvises med «Lista er full. Fjern en aksje for å følge en annen.», både på siden og i porten.
6. **En ticker som ikke gir rader.** *Forslag:* hentingen tar aksjen inn, og gir svaret ingen rader, slettes raden i `aksje` igjen (den har ingen kurser), ønsket merkes avvist, og utskriften sier det.
7. **Omsetningen.** *Forslag:* den siste målingen i `omsetning` (2.13). Under 32 MNOK, eller ikke målt, gir merket «Utenfor målingen» i grått, som utdraget. Er den ikke målt, står «Omsetningen er ikke målt ennå …» i dialogen. Hentingen måler den ikke med det samme kallet i denne storyen; det står som åpent punkt.
8. **Dialogene uten JavaScript.** *Forslag:* «Følg en aksje» og «Bytt ut» er egne sider med skjema (`/folg`), som virker med tastatur og uten skript. Tekstene er utdragets.
9. **Steg 2 i «Din egen liste».** Utdraget sier at nøkkelen legges inn når den ekte versjonen startes første gang (avviket i utdraget §2). *Forslag:* som utdraget.
10. **Demoen.** *Forslag:* demobasen får `boersliste` med noen oppdiktede selskaper som kan velges, og valget, «x av 18» og «Dine egne aksjer» virker likt. Demoen henter aldri, så ønsket står som «Venter på henting i kveld etter kl. 22.», og en boks sier det.

## Intent

**Problem:** lista kan ikke byttes fra siden. Gruppen vil følge så mange aksjer som mulig (svaret 08.11 kl. 11:41 og 11:43), opptil 18, og bytte fra mandag 09.11 (kl. 11:57).

**Avgjørelsene:** story 2.12 i `epics.md` (08.10, tillegget 13.10, beslutningen 16.10 om demoen, 21.10 kl. 16:47 og 18:38 om taket og kallene, 22.10 kl. 23:14 om lista over Oslo Børs), svarene 08.11 kl. 11:41–12:39, og §1 og §2 i `designutdrag-2026-11-08.md`.

## Bygget 08.11 (instruksjonen kl. 14:05)

Bygget på grenen `2-12-velge-og-bytte-aksjer`, i worktreen `G74-lund-osen-2-12`, fra grenen for 2.11 (`4594dfa2`, med rettingene fra `db9e4ab9` og `e34de7e3` flettet inn).

- **Basen:** `src/migrasjoner/0010_valg.sql` med `boersliste` og `oenske`.
- **Porten:** `src/valg.py`: `Valglager` (bare `oenske` skrives), `les_boerslista`, `ta_i_bruk` og `uten_rader` (hentingen), taket, kallene og «Utenfor målingen».
- **Hentingen:** `ta_i_bruk_oenskene` i `src/fetch_prices.py` før lista leses, og `--les-boerslista`, uten kall. En egen aksje uten kurser tas ut kvelden etter, så et nytt forsøk samme kveld fortsatt kan hente den (avvik fra spørsmål 6, som sa samme kveld).
- **Sidene:** «Dine egne aksjer» under tabellen og «Din egen liste» i Min liste (`src/templates/_egne.html`), siden «Følg en aksje» og «Bytt ut» (`src/templates/folg.html`), merkene «Egen» og «Utenfor målingen» i tabellen, og rutene `/folg`, `/fjern` og `/angre`, som bare skriver `oenske`. Hjelpen bak «?», `docs/hjelp.md` («Hvordan følger jeg andre aksjer?») og README-en med bildet `docs/appen/din-egen-liste-demo.png`.
- **Demoen:** fem oppdiktede selskaper på «Demo Børs» som kan velges, og to målinger av omsetningen, én over og én under 32 MNOK (`DEMOBOERSEN` og `DEMOMAALT` i `src/demo.py`).
- **Avvik:** en egen aksje er en aksje tatt inn fra et ønske på siden, ikke «ikke blant de 15» (spørsmål 1, rettet før byggingen). Et ønske som venter, telles med i «N egne». Hentingen måler ikke omsetningen med det samme kallet; teksten i dialogen sier det likevel, ordrett fra utdraget, og det står som åpent punkt. Lenken «Åpne eodhd.com» er tekst, fordi sidene ikke har lenker ut av appen (`test_utseende.py`).
- **Tester («Ville feilet hvis» i hver):** `tests/test_valg.py`.
- **Hele settet,** alene: kl. 17:01:58–17:12:26 ga 14 feil (versjonen 10 i ni tester, SQL i `app.py`, en stiplet kant, «kl.» som en setning i hjelpen, vinduene på oversikten og den sjuende malen), rettet. Kl. 17:15:45–17:25:33: 4633 bestått, 24 hoppet over og 0 feilet. Bildene ble tatt på nytt: Min liste og oversikten ved 390 px viser de nye delene, og de fem andre er byte for byte de samme.
