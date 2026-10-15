---
title: 'Story 4.0: Nettsperren dekker hele testkjøringen'
type: 'feature'
created: '2026-10-15'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '48b8125'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Sperren i `tests/conftest.py` er en autouse-fixture med funksjonsscope. Den gjelder bare inne i testfunksjonene, ikke i fixturer med module- eller session-scope og ikke under innsamlingen. Loopback slippes gjennom til alle porter, så en test kunne nå en Ollama eller en proxy som kjører på maskinen. `gethostbyname`, `gethostbyname_ex` og `getfqdn` er ikke sperret (story 4.0 i `epics.md`).

**Approach:** Socket-sperren settes i `pytest_configure` med `pytest.MonkeyPatch()` og fjernes i `pytest_unconfigure`. `socket.socket.listen` pakkes inn, og loopback slippes bare gjennom til en port som en åpen socket i samme prosess lytter på. Fixturen beholdes for proxyvariablene. PR A i planen for KI-laget, før alt som kan kalle Ollama (svar 9).

## Planen

Planen for KI-laget ble vist i chatten 15.10 kl. 15:43 og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-15.md` (`5ce64f6`). Testtallet før: 1608 bestått og 16 hoppet over på main (`48b8125`).

## Svarene

*Lagt til 2026-10-15 (gruppens svar på de ti spørsmålene i planen, instruksjonen kl. 15:53):* svarene er beslutninger. Alle ti står under Epic 10 i `epics.md`. De som gjelder denne storyen:

- Svar 8: adressen til Ollama er `OSE_KI_OLLAMA_URL`, med `http://127.0.0.1:11434` som standard. Ollama lytter da på loopback, og sperren må stoppe en test som prøver å nå den.
- Svar 9: 4.0 er første PR.

**Mutantene** (planen kl. 15:43): N1 sperren bare i fixturen; N2 `gethostbyname` åpen; N3 loopback åpen for en port ingen lytter på; N4 `connect_ex` åpen.

## Boundaries & Constraints

- Bare testoppsettet endres. Ingen kode under `src/`.
- Ingen test kaller nettet eller en tjeneste på maskinen (AD-8). Ingen API-kall.

## I/O & Edge-Case Matrix

| Inndata | Forventet |
|---|---|
| `connect` eller `connect_ex` mot en adresse utenfor maskinen, i en test eller en fixture med module- eller session-scope | `NettverkISTest` |
| `connect` mot loopback til en port en åpen socket i prosessen lytter på | slippes gjennom |
| `connect` mot loopback til en port ingen lytter på, eller en lytter som er lukket | `NettverkISTest` |
| `getaddrinfo`, `gethostbyname`, `gethostbyname_ex` eller `getfqdn` på et navn utenom loopback, og `getfqdn()` uten navn | `NettverkISTest` |
| `getaddrinfo(host=…, port=…)` med navngitte argumenter | virker som før |
| `AF_UNIX` | slippes gjennom |

</frozen-after-approval>

## Code Map

- `tests/conftest.py`: `pytest_configure` og `pytest_unconfigure` med sperren, `_lytt` og `_lytter_paa` for loopback, oppslagene, og fixturen `ingen_nettverk` med bare proxyen.
- `tests/test_ingen_nettverk.py`: testene for kontrollpunktene.

## Spec Change Log

## Review Triage Log

## Verification
