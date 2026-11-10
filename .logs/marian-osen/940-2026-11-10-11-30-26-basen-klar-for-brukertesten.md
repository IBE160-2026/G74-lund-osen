# Basen klar for brukertesten

## 2026-11-10 kl. 11:30 — Marian Osen

### Oppgave
Morgenen før brukertesten 10.11: kjøre `--les-boerslista` én gang, som migrerer basen først, med en kopi av basen før (gruppens svar 09.11 kl. 10:23), og prøvekjøre appen på en kopi av den migrerte basen (svaret kl. 10:44). Instruksjonen kl. 11:20 i dagsfila 10.11.

### Plan
- Steg 0: main, ren, ingenting på port 8000, kveldsoppgaven ikke i gang.
- Kvotesjekk og tellinger for 09.11 fra basen med `mode=ro`.
- Kopi med sqlite3 sin backup, så `--les-boerslista` én gang.
- Prøvekjøring med Flask sin testklient mot en kopi i en midlertidig mappe.

### Resultat
- Kvoten: 0 kall brukt i dag (GMT); 20 brukt 09.11, bonuskvote 463. Kveldsjobben 09.11 kl. 23:45 med resultat 0.
- Basen 09.11: 15 aksjer med kursrad og vurdering, OSEBX med én rad, KI-tekster 1 for dagen og 15 for aksjene.
- Kopien `data/db/ose-foer-les-boerslista-2026-11-10.db` med `integrity_check` ok. `--les-boerslista`: exit 0, ingen FEIL-linjer. Migreringene 10 og 11 er lagt til, 297 rader i boersliste, kursrader (3750) og vurderinger (405) uendret.
- Prøvekjøringen: 20 sider, alle 200. ose.db uendret under den.
- `uv run pytest --dokumentene`: 2192 bestått, 7 hoppet over.
- Commit `096bebd7` med dagsfila og avkrysningen i issues.md.

### Åpne punkter
Ingen.
