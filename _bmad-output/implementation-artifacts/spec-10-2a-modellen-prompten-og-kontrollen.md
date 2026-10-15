---
title: 'Story 10.2, PR E (10.2a): porten Modell, prompten og kontrollen i FR-603'
type: 'feature'
created: '2026-10-15'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f87931a'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md'
  - '{project-root}/_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Story 10.2 lager KI-teksten i hentekommandoen og lagrer den i `KILogg`. Før noe kobles til hentingen, trengs porten for modellen, prompten og kontrollen i FR-603, prøvd med en falsk modell (story 10.2 i `epics.md`, FR-603, FR-604, FR-605, FR-608, AD-2, AD-8).

**Approach:** Tre rene moduler og én funksjon som setter dem sammen, uten I/O:
- `src/ki_modell.py`: porten `Modell` (AD-2), `Modellsvar`, `ModellFeilet`, og `lag_ki_rad`, som lager prompten, kaller modellen én gang, kontrollerer teksten og gir `KIRad` for `KILogg`. Feiler modellen, blir det en rad uten tekst og med grunnen (NFR-04).
- `src/ki_prompt.py`: `PROMPTVERSJON` og `lag_prompt`. Prompten sier at fortegnet for interessen følger dagens kursendring og ikke volumet (lærdommen fra C-med i `malinger.md` §19).
- `src/ki_kontroll.py`: `kontroller`, de fire punktene i FR-603 med ordlistene, tall skrevet med ord, og «fordi» om regelen som lov.

PR E i planen for KI-laget. `ki_lokal.py` mot Ollama, steget i hentekommandoen, compose, `.env.example` og README er PR F (10.2b), i en egen instruksjon. Story 10.2 er ikke ferdig før F er flettet.

## Planen

Planen for KI-laget ble vist i chatten 15.10 kl. 15:43 og er ført kort i Utført-linja for den instruksjonen i `docs/ai-prompts/2026-10-15.md` (`5ce64f6`). Testtallet før: 1763 bestått og 17 hoppet over på main (`f87931a`).

## Svarene

*Lagt til 2026-10-15 (gruppens svar på de ti spørsmålene i planen, instruksjonen kl. 15:53):* svarene er beslutninger. Alle ti står under Epic 10 i `epics.md`. De som gjelder denne PR-en:

- Svar 2: raden står når den finnes, også når modellen feilet. `lag_ki_rad` gir alltid en rad, også når modellen feiler, så hentingen kan skrive den (PR F).
- Svar 5: `av` er et eget valg i `OSE_KI_TJENESTE`. Med KI av kalles ikke `lag_ki_rad`, og ingen rad skrives (PR F).
- Svar 10: grunnlaget for én aksje har ingen antall, så de lovlige tallene i punkt 2 er styrken og regelens faste tall.

**Mutantene** (planen kl. 15:43): E1–E4 hvert av de fire punktene slått av; E5 «femti» slipper gjennom; E6 «fordi ingen sjekk ga utslag» stoppes.

## Boundaries & Constraints

- Ingen modell kalles, heller ikke Ollama. Ingen API-kall. Testene bruker en falsk modell (AD-8), og nettsperren fra 4.0 stopper en test som prøver.
- Ingen endring i `src/fetch_prices.py`, compose, `.env.example` eller README. Det er PR F.
- Kontrollen er grov: den fanger ord, ikke mening (FR-603).

## I/O & Edge-Case Matrix

| Inndata | Forventet |
|---|---|
| En tekst som bare forklarer grunnlaget | består |
| «Retningen er positiv» når regelen sier Blandet | stopper, punkt 1 |
| «Ingen av de tre sjekkene» når styrken er 2 | stopper, punkt 1 |
| «2,4 prosent», «3 %», «femdagssnittet», «seks av de femti» | stopper, punkt 2 |
| «50 dager», «MA50», «to av de tre» når styrken er 2 | består |
| «kjøpe», «bør», «investeringsråd», «alternativ for investorer» | stopper, punkt 3 |
| «trolig», «skyldes», «nyheter», «kontrakt» | stopper, punkt 4 |
| «fordi ingen sjekk ga utslag», «resultatet av sjekkene», «børsdagen» | består |
| Modellen reiser `ModellFeilet`, eller svarer tomt | en rad uten tekst, `besto=False` og «modellen feilet» |
| Modellen reiser en annen feil | feilen går videre |

</frozen-after-approval>

## Code Map

- `src/ki_modell.py`: `Modell`, `Modellsvar`, `ModellFeilet`, `lag_ki_rad`.
- `src/ki_prompt.py`: `PROMPTVERSJON`, `lag_prompt`.
- `src/ki_kontroll.py`: `kontroller`, `Kontrollsvar`, ordlistene.
- `tests/test_ki_modell.py`: testene, med `FalskModell`.

## Spec Change Log

## Review Triage Log

## Verification
