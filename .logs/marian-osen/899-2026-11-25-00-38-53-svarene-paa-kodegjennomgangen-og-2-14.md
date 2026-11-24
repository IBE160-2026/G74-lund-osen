# Svarene 24.11 kl. 21:47: kodegjennomgangen av v1 og 2.14

## 2026-11-25 kl. 00:38 — Marian Osen

### Oppgave
Instruksjonen kl. 21:54 i `docs/ai-prompts/2026-11-24.md`, med gruppens svar kl. 21:47 på de seks spørsmålene i kodegjennomgangen av v1 og spørsmål 1–4 i 2.14. Bare dokumenter, ingen kode, og ingen fletting.

### Plan
- Svarlinjene ved spørsmålene, storyene i backlog, FR-412 og raden i brukertest-skjemaet på main, hver i sin commit.
- Svarlinjene i spesifikasjonen for 2.14 på grenen `2-14-eksdatoer`.
- `--dokumentene` på main og på grenen etter pytest-pausen, så push utenom git-pausene.
- Arbeidet før dette står i [svarene-24-11-og-fem-storyer](900-2026-11-24-17-44-30-svarene-24-11-og-fem-storyer.md).

### Resultat
- Kvoten kl. 21:54: 0 av 20 brukt 24.11 i GMT, og bonuskvoten 296. Ingen andre API-kall. `data/`, `.env` og `_privat/` er ikke rørt, den ekte versjonen ble ikke startet, og kveldsjobben og databasekopien er ikke rørt. Ingen kode er endret, og ingenting er flettet.
- **Svarlinjene** ved de seks spørsmålene i `kodegjennomgang-v1.md` (`78597d89`).
- **Sju storyer i backlog**, merket «etter brukertest 2» (`9891d86a`): 10.12 (G1 og G2), 10.13 (G3 og G4), 2.23 (G5), 2.24 (G6), 10.14 (G12), 2.25 (testene for G8, G10 og G14) og 10.15 (G11). De står i `epics.md`, sprintstatusen og `docs/skjermene.md`, og tallet i vurderingsmatrisen har en datert linje. 10.13 står i Epic 10 fordi «Børsdagen kort fortalt» er story 10.6; stjernen i G4 er fra Epic 8. 2.25 står i Epic 2 fordi to av de tre testene gjelder hentingen og lista.
- **FR-412** i `prd.md` sier det koden gjør med en ticker uten kurser, med en linje i endringsloggen, og raden i sporingen har 2.21, 2.22, 9.27 og 9.28 (`4514f110`). Lest i `uten_rader` og `ta_i_bruk` i `src/valg.py`.
- **Brukertest 2:** raden om KI-teksten for aksjen i oppgave B står i «Før testen (brukertest 2)» i `docs/brukertest.md` (`0452d769`).
- **2.14:** svarlinjene ved spørsmål 1–4 i spesifikasjonen på grenen (`45b52e58`). PR #180 er ikke flettet.
- **Et brudd på pytest-pausen:** `--dokumentene` gikk første gang kl. 21:59–22:45, i pytest-pausen, fordi ventebetingelsen i skriptet som skulle starte kjøringene etter kl. 23:50, var feil. Kjøringen på main (kl. 21:59–22:21) ga 3184 bestått, 7 hoppet over og 1 feil: vakta for regel 22 så at `data/db/ose.db` ble endret mens testene gikk, og kveldsjobben kl. 22:15 gikk midt i kjøringen. Kjøringen på grenen (kl. 22:21–22:45) ga 3247 bestått og 7 hoppet over. Kveldsjobben endte med kode 0 kl. 22:45 og sto som Ready etterpå; koden fra kl. 22:15 er ikke lest. Ingenting ble pushet på disse kjøringene.
- **Kjøringene etter pausen:** main kl. 23:51–00:13 ga 3184 bestått og 7 hoppet over, og grenen kl. 00:13–00:37 ga 3247 bestått og 7 hoppet over. Main og grenen ble pushet kl. 00:38.
- Lukket i `issues.md`: spørsmål 1 og spørsmål 2–5 i 2.14, og de to punktene om spørsmålene i kodegjennomgangen av v1.

### Åpne punkter
- Før brukertest 2 leser gruppen KI-teksten for aksjen i oppgave B, og velger en annen aksje hvis den har tall som ikke står i tabellen, eller råd.
- Etter brukertest 2: storyene 10.12, 10.13, 2.23, 2.24, 10.14, 2.25 og 10.15, i den rekkefølgen.
- G7: gruppen avgjør om lista over Oslo Børs kan ligge i repoet, når den har lest vilkårene.
- G13: gruppen skriver selv i `docs/kilder-og-rettigheter.md` at prompten for dagen sender selskapsnavn og bransjenavn.
- 2.14: når PR #180 flettes etter testen, skrives den daterte linja i regel 22 og under AD-3 (AA1), og grenen må først ha main flettet inn, med de sju nye storyene. Spørsmål 5 (Docker) er ikke besvart, og storyen fra spørsmål 3 står ikke i `epics.md` ennå.
- Vinduet starter ikke en ventende pytest-kjøring uten først å prøve ventebetingelsen mot klokka.
