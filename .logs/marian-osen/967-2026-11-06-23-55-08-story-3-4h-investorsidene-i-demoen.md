# Story 3.4h, investorsidene i demoen

## 2026-11-06 kl. 23:55 — Marian Osen

### Oppgave
Instruksjonen kl. 23:53: slå opp story 3.4h, før den inn i `epics.md` og `sprint-status.yaml` som backlog hvis den mangler, med svarene fra 24.10, og før avgjørelsen kl. 23:51 under den.

### Plan
- Klokka sjekket med `date` (23:53), og instruksjonen lagret i dagsfila først.
- Slått opp: story 3.4 i `epics.md`, `docs/bilder/investorsider/LESMEG.md`, instruksjonen kl. 15:30 i `docs/ai-prompts/2026-10-24.md` og oppføringen for 24.10 i `docs/reflection-log.md`.
- Én commit for storyen og statusen.

### Resultat
- `6e8be94e`: instruksjonen kl. 23:53 i dagsfila for 06.11.
- 3.4h fantes bare som navn: i instruksjonen 24.10 kl. 15:30, i `LESMEG.md` og i refleksjonsloggen («Det skjer i 3.4h»). Den fantes verken i `epics.md` eller i `sprint-status.yaml`.
- `a60a4882`: «Story 3.4h: Investorsidene i demoen» mellom 3.4b og 3.5, med de elleve linjene fra 24.10 under story 3.4 ordrett, avhengig av 3.4 og 10.5, og «Avgjort 2026-11-06 kl. 23:51 (gruppens svar)». `3-4h-investorsidene-i-demoen: backlog` står etter 3-4b i `sprint-status.yaml`.
- Kontrollen mot HEAD viste ingen fjernede linjer. Dokumenttestene (de seks filene) ga 257 bestått før hver push. Ingen API-kall i denne instruksjonen.

### Åpne punkter
- Det er ikke avklart hvordan lenken nederst på aksjesiden (svaret kl. 23:51) henger sammen med kortet «Mer om ‹navn›» fra svaret 24.10 kl. 15:21. Det avgjøres i spesifikasjonen for 3.4h.
- Under story 10.5 står det at demoen ikke viser noen lenke, og at hva som står i stedet, avgjøres når 10.5 planlegges. Den linja er ikke rettet etter svaret kl. 23:51.
