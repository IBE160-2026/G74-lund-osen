---
title: 'Story 8.19: Neste henting i stripa øverst'
type: 'feature'
created: '2026-11-12'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'a93c668f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/ux-logg.md'
---

Skrevet 12.11 etter tillegg 1 (kl. 17:04) til instruksjonen kl. 17:03 om 10.11, etter gruppens svar 12.11 kl. 17:01: når 10.11 er grønn og har stoppet for gruppens ja, bygger samme vindu 8.19 som egen story med egen gren, worktree og PR. Rådet anbefalte det. Tillegget er kopiert til scratchpad og føres i dagsfila med flettingen. PR #149 (10.11) var grønn kl. 18:40. Storyen bygges nå, og spørsmålene under har hvert et forslag som koden bygger på. Gruppen svarer før PR-en flettes.

**Svaret 12.11 kl. 17:01** (gjengitt fra tillegget, fordi det ikke står andre steder i repoet): bare i den ekte versjonen står det bak «Oppdatert …» når nye kurser tidligst kan hentes, regnet med børsdagskontrollen (2.3) og grensen kl. 22. Linja sier aldri at en henting kommer, fordi det avhenger av om appen eller kveldsjobben kjører. Demoen viser ingenting, fordi den ikke henter.

Tillegg 2 (kl. 18:58, svaret kl. 17:31) og tillegg 3 (kl. 17:59, svaret kl. 17:44) legger omvisningen til denne storyen. Begge bygges etter at 8.26 er flettet og main er flettet inn i grenen, fordi 8.26 bygger om omvisningen (`rundturer()` i `src/hjelpetekster.py`). Tillegg 3 kom før tillegg 2, så det ventet til tillegg 2 var limt inn. Spørsmålene står under «Tillegg 2 og 3».

## Slått opp 12.11 på `a93c668f` (regel 3)

- **Story 8.19** står i `epics.md` (backlog) med «Neste: ‹dag› etter kl. 22», og i `docs/ux-logg.md` som U60.
- **Hentingen** (`kjoer` i `src/fetch_prices.py`): på en børsdag før `TIDSGRENSE` (kl. 22:00) hentes ingenting uten `--uten-tidskontroll`, bortsett fra første henting i en tom base, som henter forrige børsdag (2.3c). Ellers hentes inneværende børsdag (`innevaerende_boersdag`) når basen mangler den, også i helgen.
- **`TIDSGRENSE`** sto i `src/fetch_prices.py`, som importerer KI-laget (`ki_modell`, `ki_tekst`). Webserveren importerer aldri KI-laget (AD-10).
- **Stripa** (`_ramme.html`) viser «Oppdatert ‹tidspunkt›» fra `hentet`, det eldste `sist_hentet` blant radene (`sidens_tidsstempel`). Demoen har `eksempeltall`.
- **Kalenderen** (`boersdag.py`) har stengte dager for hvert år fra 2026, og `dekker` er sann for alle år fra og med 2026.

## Spørsmål til gruppen før flettingen

1. **Ordene.** *Forslag:* bak «Oppdatert ‹tidspunkt›» står « · » og så:
   - «nye kurser fra kl. 22 i kveld»
   - «nye kurser fra kl. 22 i morgen»
   - «nye kurser fra mandag kl. 22»: ukedagen innen en uke
   - «nye kurser fra onsdag 25.11 kl. 22»: ukedag og dato når dagen er en uke eller mer fram
   - «nye kurser kan hentes nå»

   «fra» sier når de tidligst kan komme, ikke at de kommer, og hjelpen sier det.
2. **Tilfellene.** *Forslag:* regnet som hentingen gjør det:
   - **Før kl. 22 en børsdag:** «i kveld», også etter midnatt, fordi hentingen ikke henter før kl. 22.
   - **Etter kl. 22, når dagen ikke er hentet:** «kan hentes nå».
   - **Etter kl. 22, når dagen alt er hentet:** neste børsdag, og fredag gir mandag.
   - **Helg og fridag:** «kan hentes nå» når siste børsdag mangler, og ellers neste børsdag. 23.12 kveld gir mandag 28.12, fordi 24. og 25.12 er stengt.
3. **Hvilken dag er hentet?** *Forslag:* dagen regnes av tidspunktet i «Oppdatert» med reglene i hentingen (`boersdagen_hentet`). En henting før kl. 22 en børsdag hadde forrige børsdag, og ellers inneværende. Stripa leser altså ikke basen på nytt. Fordi «Oppdatert» er det eldste tidspunktet, sier stripa «kan hentes nå» når én aksje mangler dagen, og det stemmer: da henter hentingen.
4. **Hvor står grensen?** *Forslag:* `TIDSGRENSE` er flyttet til `src/boersdag.py`, og `fetch_prices.TIDSGRENSE` er det samme objektet, så webserveren slipper å importere hentingen (AD-10). Story 8.19 i `epics.md` sier at grensen kommer fra `fetch_prices.py`, og får en Rettet-linje etter svaret.
5. **Når kalenderen ikke dekker dagen.** *Forslag:* ingenting står (NFR-08), som ellers i appen.
6. **Hjelpen.** *Forslag:* en egen tekst i vinduet ved «Oppdatert» på oversikten og aksjesiden, 38 ord: «Neste henting: i den ekte versjonen står bak tidspunktet når nye kurser tidligst kan hentes, fra kl. 22 en børsdag, men ikke om de blir hentet: det avhenger av at appen eller kveldsjobben kjører. Demoen henter ikke og viser det ikke.» `docs/hjelp.md` har det samme under «Når kan jeg hente?».
7. **Stripa med 8.26 og 8.27.** Begge endrer stripa, og 8.26 gir «Oppdatert» til flere sider (`hentet_felles`). *Forslag:* linja står inne i den samme `<span>` som «Oppdatert», så den følger med på hver side som får «Oppdatert». Når main er flettet inn, beholdes begge endringene, og testen sjekker sidene på nytt.

## Grenser

- Ingen API-kall utover kvotesjekken. Ingenting rører `data/db/ose.db`.
- Linja vises bare i den ekte versjonen, og demoen viser den ikke.

## Tillegg 2 og 3: omvisningen (bygges etter 8.26)

Slått opp i grenen for 8.26 (`origin/8-26-vis-meg-rundt-spiller-av-siden`): `MAKS_STEG = 7`, og oversikten har sju steg: «Dagen og perioden», «Hovedindeksen», «Tabellen», «Signalstyrken», «Retningen», «Slik leser du tabellen» og «Børsdagen kort fortalt».

8. **Hvor står linja om neste henting i omvisningen (tillegg 2)?** Oversikten har alt sju steg. *Forslag:* steget «Dagen og perioden» får én setning til.
   - **Ekte versjon:** «Bak «Oppdatert» øverst står når nye kurser tidligst kan hentes.» Steget merker både dagvalget og linja i stripa.
   - **Demoen:** «Den ekte versjonen viser bak «Oppdatert» øverst når nye kurser tidligst kan hentes; demoen henter ikke.»
   - **Aksjesiden:** samme setning i steget om dagen, hvis det finnes etter 8.26.
   - **Hjelpen:** sier det samme i begge versjonene (spørsmål 6).
9. **Ordene i tillegg 3.** *Forslag:* ordene fra tillegget, kortet inn under 50 ord og rettet etter det koden gjør:
   - **«Signalstyrken»:** nevner trend, bevegelse og interesse (T, B og I).
   - **«Retningen»:** får setningen om Blandet og «Det er ikke et råd om å kjøpe eller selge.» (NFR-06).
   - **«Signalet forklart» på aksjesiden:** får sin egen tekst. Først appens egne setninger, så KI-teksten om sjekkene, merket «Laget av KI», med tallene med prikket strek sjekket mot det appen regnet ut.
   - **«Hovedindeksen» og «Dag for dag»:** får småtingene.
   - **Boksen «Slik leser du tabellen» og hjelpen:** følger der de sier det samme (regel 19).
