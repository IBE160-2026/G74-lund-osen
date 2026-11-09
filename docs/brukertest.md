---
title: "Brukertesten"
status: aktiv
created: 2026-10-23
updated: 2026-11-09T10:31
---

# Brukertesten

**Ikke tatt ennå.** Brukertesten tas neste uke (gruppens svar 23.10 kl. 12:29). Opplegget står i [spesifikasjonen 8.1](../_bmad-output/implementation-artifacts/spec-8-1-brukertesten.md): story 8.1 i del A, med KI av, og story 10.4 i del B, med samme person og samme aksje, først med KI av og så på. Del A og del B er to tester med hvert sitt notat.

*Rettet 2026-10-23 (gjennomgangen av 3.4e, VG6):* slår personen på KI-teksten selv i del A, hoppes del B over, og 10.4 tas med neste person (svaret 23.10 kl. 15:53, b).

*Rettet 2026-11-03 (gruppens svar 02.11 kl. 22:15, C):* «neste uke» i svaret 23.10 kl. 12:29 gjelder ikke lenger. Brukertesten, story 8.1 og 10.4, tas senere, uten dato ennå, og «Brukerutfall» står som mål for v1 i §7 i PRD-en.

*Rettet 2026-11-08 (gruppens svar 07.11 kl. 22:51):* brukertesten tas tirsdag 10.11 eller onsdag 11.11, eller begge dagene, med den ekte versjonen og dataene fra kvelden før.

Ingen navn eller annet som kan kjenne personen igjen, står her. En kurs eller et volum som personen sier høyt, står som [kurs] eller [volum] (regel 16). Originalnotatene ligger i `_privat/` (regel 10).

## Før testen

| Felt | Notat |
|---|---|
| Dato | |
| Muntlig ja til observasjon og anonyme notater, klokkeslett | |
| Den ekte versjonen på http://127.0.0.1:8000, uten «Eksempeltall» øverst | |
| Siste henting, dato | |
| KI av: knappen sier «Vis KI-teksten» | |
| Bare oversikten åpen, øverst på siden | |
| Det som ble sagt, ordrett | |

*Rettet 2026-11-07:* knappen «Skjul KI-teksten» og «Vis KI-teksten» finnes ikke lenger. Den er nå bryteren «KI-tekst» med «På» og «Av» (`role="switch"` i makroen `ki_bryter` i `src/templates/aksje.html`), inne i rammen «‹navn› kort fortalt» øverst til høyre når teksten vises, og alene når KI er av. Den kom med story 8.2b (U33, U46 og U67), squash-flettet i `6f62f564`, PR #109, og svaret 04.11 kl. 09:58 på spørsmål 5 og 6 i `spec-8-2b-funnene-fra-ux-loggen.md` holdt den i blekk og utenfor stripa. KI av før del A betyr at bryteren viser «Av», og i del B slås den til «På». Raden «KI av: knappen sier «Vis KI-teksten»» over gjelder bryteren som viser «Av».

*Rettet 2026-11-08 (slått opp i `src/templates/aksje.html` på `50103bcc`):* rammen heter nå «Signalet forklart», ikke «‹navn› kort fortalt» (story 10.9). Bryteren «KI-tekst» står fast øverst til høyre i rammen, både med KI på og av. Med KI av står rammen med appens setninger om dagene og om samme dag, uten KI-teksten. Med KI på kommer KI-teksten under dem, med «Laget av KI».

*Lagt til 2026-11-08 (slått opp i `src/templates/_perioder.html` og `src/perioder.py` på `50103bcc`):* datofeltet står etter periodeknappene på oversikten, Min liste, aksjesiden og børsometeret. Med dataene fra kvelden før heter den første knappen «I går», og feltet viser den dagen. Det er dagen raden «Siste henting, dato» gjelder.

*Lagt til 2026-11-08 (slått opp i `compose.yaml`, `start/start.ps1` og `src/app.py` på `50103bcc`):* på denne maskinen startes den ekte versjonen fra repo-mappa på main med `uv run python src/app.py`, fordi kveldsjobben skriver `data/db/ose.db` der. Docker bruker sitt eget volum, og «Start den ekte versjonen» stopper i en klon. Opplegget står i spesifikasjonen, under «Slik er det i dag».

*Lagt til 2026-11-09 (story 10.6, flettet 08.11 i `c517e460`; slått opp i `src/templates/index.html`, `src/app.py` og `src/ki_visning.py` på `673230d9`):* under tabellen på oversikten står «Børsdagen kort fortalt», med bryteren «Vis KI-tekst». Den bruker samme informasjonskapsel som bryteren på aksjesiden (FR-601), så KI av før del A gjelder begge. Med KI av står «KI-teksten er slått av. Tabellen over viser bare det reglene har regnet ut.» Slås KI på i del B, kommer også teksten om dagen på oversikten.

*Lagt til 2026-11-09 (story 2.12, PR #124, ikke flettet; spørsmål 1 og 8 i `spec-2-12-velge-og-bytte-aksjer.md`):* over «Børsdagen kort fortalt» står «Dine egne aksjer» med «+ Følg en aksje», og i Min liste «Din egen liste» med «Bytt ut». Valg som bytter aksjer, også «Bruk denne lista» fra 8.11, gjøres bare i demoen, så den ekte lista ikke endres.

*Lagt til 2026-11-09 (story 8.10 og 8.10b, PR #125 og #126 på grenene `8-10-innstillinger-oeverst` og `8-10b-vis-ki-tekst`, ikke flettet; slått opp i `src/templates/innstillinger.html` på `95e0d5d7` og i spørsmål 2 og 4 i `spec-8-10-innstillinger-oeverst.md`):* «Innstillinger» i stripa etter «Min liste» åpner en side med «Vis hjelp» og «Vis KI-tekst». «Vis KI-tekst» er det samme valget som bryteren ved KI-teksten, så KI av før del A kan settes der eller ved teksten. «Vis hjelp» skal stå på, så «?»-knappene finnes; uten valg er den på.

*Lagt til 2026-11-09 (story 8.8, PR #127; spørsmål 1 og 3 i `spec-8-8-signaldager-i-kursgrafen.md`):* kursgrafen på aksjesiden har prikker på dagene med signalstyrke 2 eller mer, og under grafen står «Prikkene på kurslinja viser dagene med signalstyrke 2 eller mer, fra ‹dato›.»

*Lagt til 2026-11-09 (slått opp i `src/app.py`, `src/lagring_sqlite.py` og `start/kveldshenting.ps1` på `673230d9`):* slik får `data/db/ose.db` migrasjonen 0011 (8.10) før testen tirsdag 10.11. 0011 flettes mandag 09.11 kl. 23:50, etter 0010 (2.12). Jobben kl. 22:15 mandag bruker commiten origin/main hadde ved midnatt søndag–mandag (steg 1 i `kveldshenting.ps1`), så den gir basen 0009 (2.11, flettet 08.11 kl. 23:50), ikke 0010 og 0011. Startes den ekte versjonen tirsdag fra repo-mappa på main etter `git pull --ff-only`, kjører `aapne_base` `migrer()` én gang i prosessen, og basen får 0010 og 0011 før siden vises. Ellers får basen dem i jobben tirsdag kl. 22:15, som bruker main fra midnatt mandag–tirsdag. Regel 22 sier at webserveren bare skriver merkingen i Min liste. At den også migrerer basen, er et åpent punkt til gruppen. Er 2.12 og 8.10 ikke flettet mandag, har testen ikke Innstillinger, og KI slås av med bryteren som før.

*Avgjort 2026-11-09 kl. 10:23 (gruppens svar), lagt til etter linja over:* webserveren migrerer basen når den startes, og skriver også ønskene (2.12) og innstillingene (8.10), så punktet over er besvart, med en Lagt til-linje under regel 22 i `CLAUDE.md`. Rådet anbefalte at `--les-boerslista` migrerer først tirsdag. Svaret er ført etter instruksjonen kl. 10:28 i `docs/ai-prompts/2026-11-09.md`.

## Del A (story 8.1): KI av

| Felt | Notat |
|---|---|
| Klokkeslett da oversikten ble vist | |
| Forklaringen av hvorfor en aksje skiller seg ut, ordrett | |
| Tiden fra oversikten ble vist til forklaringen | |
| Under 5 minutter (ja eller nei) | |
| Stoppet etter 10 minutter uten forklaring (ja eller nei) | |
| Stoppet, rullet tilbake eller mistet raden (15 rader), med tidspunkt | |
| Så hovedindeksen og søylene, med tidspunkt | |
| Sidene som ble åpnet, i rekkefølge | |
| Slo på KI-teksten selv, med tidspunkt | |
| Forklaringen kom før KI-teksten ble slått på (ja eller nei). Kom den etter, teller den ikke for 8.1 (svaret 23.10 kl. 15:53, b) | |
| Spørsmål personen stilte, og svaret «Gjør det du ville gjort hvis du satt alene.» | |

## Del B (story 10.4): samme aksje, først KI av og så på

| Felt | Notat |
|---|---|
| Aksjen, og om den kom fra forklaringen eller var den første aksjesiden personen åpnet | |
| Den øverste i tabellen, fordi personen verken forklarte noe eller åpnet en aksjeside (ja eller nei, svaret 23.10 kl. 15:53, a) | |
| Hoppet over, fordi personen slo på KI-teksten selv i del A. 10.4 tas da med neste person (ja eller nei, svaret 23.10 kl. 15:53, b) | |
| Klokkeslett da del B startet | |
| «Hva sier siden om denne aksjen?», KI av, svaret ordrett | |
| «Hva sier siden om denne aksjen?», KI på, svaret ordrett | |

## Funnene

Føres etter testen, med dato, og også i [UX-loggen](ux-logg.md). Et funn om at KI-teksten ikke hjelper, føres som funn og ikke som feil (story 10.4).

| Dato | Funn | Det som endres | Det som ikke endres |
|---|---|---|---|
| | | | |
