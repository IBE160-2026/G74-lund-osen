# Rådordene i alle malene (9.12)

## 2026-11-14 kl. 06:43 — Marian Osen

### Oppgave
Steg 1 i tillegg 2 og tillegg 7 til 9.11: én test av rådordene i FR-603 i alle malene, hjelpetekstene og omvisningen. Taggene skal hentes i CI, og `technology.md` fra faglærer skal lenkes i README-en. 9.12 skulle flettes sist i køen, etter Utført-linja for 3.3k, og PRD-en skulle lukke punkt 26 i §8. Det felles tillegget 13.11 kl. 19:35, tillegg 9 og beskjeden 14.11 kl. 05:21 gjaldt også.

### Plan
- Bygget 12.11 på grenen `9-12-raadordene-i-alle-malene` i worktreen `G74-lund-osen-9-12`, med spesifikasjonen [`spec-9-12-raadordene-i-alle-malene.md`](../../_bmad-output/implementation-artifacts/spec-9-12-raadordene-i-alle-malene.md). PR #152.
- Ventet på Utført-linja for 3.3k, fletting av main inn i grenen, testfilene og `--dokumentene` lokalt, CI, fletting låst til head-en og føring på main.
- Arbeidet med 9.11 står i [`931-2026-11-12-19-18-47-prd-etter-tilbakemeldingen-9-11.md`](931-2026-11-12-19-18-47-prd-etter-tilbakemeldingen-9-11.md).

### Resultat
- **Bygget 12.11:** `e81c2387`, `0f197813`, `3e83744b`, `349f052b`, `5394b45d` og `f0658f32`. Mutanten «Du bør kjøpe aksjene med gul ramme.» ble fanget, og malen var lik HEAD etterpå.
- **Flettingen av main 13.11** (`912a2b43`): punkt 26 er lukket, og NFR-06 sier at testen finnes (`16ccf117`). CI (run 43519071873) var rød fordi 8.28 hadde «og hver følges med sin egen bransje», og «følg… med» står i rådlista. Setningen ble skrevet om til «og hver aksje står med sin egen bransje» i malen, `docs/hjelp.md` og FR-412 (`a2ae3884`), uten nye unntak.
- **Ventingen:** ventekommandoen ble stoppet av lite minne flere ganger natt til 14.11 og startet igjen uten å spørre. Den fant Utført-linja for 3.3k (`4457edee`) kl. 05:59.
- **Kveldsjobben:** den sto som Disabled kl. 19:35, 21:51 og 22:46 13.11, og som Ready kl. 05:59 og 06:24 14.11. Flettingen kl. 06:25 lå utenfor pausene, og jobben ble ikke rørt.
- **Flettingen av main 14.11** (`8cfaef22`): én konflikt, i `docs/hjelp.md`. Overskriften «Din egen liste: kom i gang» fra 8.29 og «hver aksje står med» fra 9.12 står begge. Det første forsøket på å løse konflikten feilet fordi `python` ikke fantes i bash. Fila ble lagt til med markørene, men rettet med `uv run python` før commiten.
- **Lokalt:** `test_raadordene_9_12.py`, `test_docker.py`, `test_prd_9_11.py` og `test_readme.py` ga 178 bestått. `test_kom_i_gang_8_29.py`, `test_hjelpetekster.py` og `test_hjelpefeltet.py` ga 121 bestått. `--dokumentene` ble kjørt i tre deler: 1 264 bestått og 7 hoppet over, 1 072 og 612, til sammen 2 955, lik `--collect-only`.
- **CI** (run 43560865780): alle fire jobbene grønne, og 5 808 bestått og 99 hoppet over i `pytest`.
- **Flettet:** PR #152 ble squash-flettet i `e537345f` kl. 06:25, låst til `8cfaef22`. Treet på main var likt head-en.
- **Ført på main:** `3adf6eff` (done), `8521c5d3` (kvalitetssikringen) og `f14ea2b7` (dagsfilene med tillegg 7, det felles tillegget, tillegg 9 og beskjeden kl. 05:21). `--dokumentene` på main etter føringen kl. 06:25–06:42 ga 2 955 (7 hoppet over).
- Ingen API-kall, `data/db/ose.db` ble ikke rørt, og Gemma ble ikke brukt.

### Åpne punkter
- Steg 1–3 i tillegg 9 gjenstår. Det er storyen for streken (trolig 8.30), som lages fra origin/main etter Utført-linja for 9.12.
