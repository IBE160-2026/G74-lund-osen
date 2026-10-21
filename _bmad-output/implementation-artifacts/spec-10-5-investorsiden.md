---
title: 'Story 10.5: lenken til selskapets investorside i aksjedetaljen'
type: 'feature'
created: '2026-10-21'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '4baa247'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
  - '{project-root}/docs/kilder-og-rettigheter.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-7a-stilen-i-en-css-fil.md'
---

## Intent

**Problem:** briefen v8 lover lenken til selskapets investorside i v1, og story 10.5 står igjen. Aksjesiden sier i dag bare at børsmeldingene ikke er med.

**Grunnlaget:** story 10.5 i `epics.md`, med utvidelsen 30.09, rettingen 06.10 og gruppens svar 19.10 kl. 16:03 og 19:49, og instruksjonen 21.10 kl. 10:25. `designregler.md` sier at lenken går til selskapets investorside, den norske når den finnes, uten å skrive «på norsk», og at NewsWeb og Oslo Børs nevnes uten lenke. Euronexts vilkår forbyr lenker til `newsweb.oslobors.no`, `oslobors.no` og `live.euronext.com` uten tillatelse (`docs/kilder-og-rettigheter.md`). Ingen kode henter noe fra investorsidene, NewsWeb eller Euronext (AD-2).

## Kontrollpunktene

- a) Adressene: de 15 fra linjene kl. 16:03 og 19:49, ved navn og bransje, knyttet til symbolet fra Oslo Børs (EQNR), ikke til tickeren hos EODHD. Demoselskapene har ingen adresse.
- b) Siden: aksjesiden har lenken til investorsiden for aksjen siden viser, med selskapets navn i lenketeksten, og en kort tekst om at børsmeldingene står på NewsWeb og ofte også på investorsiden, uten lenke til NewsWeb eller Oslo Børs. Lenken henter ingenting, og plasseringen følger designreglene og CSS-fila. I demoen står teksten fra linja kl. 19:49 i stedet. Alt virker på 390 px uten vannrett rulling. Hjelpen, `docs/hjelp.md` og README-en følger med (regel 19), og bildene tas på nytt slik testen sier.
- c) Testene, med «Ville feilet hvis»: hver av de 15 har nøyaktig adressen fra linjene kl. 16:03 og 19:49, og lenken på siden går til aksjen siden viser; ingen mal og ingen side som vises, har en lenke til `newsweb.oslobors.no`, `oslobors.no` eller `live.euronext.com`; demoen viser teksten og ingen lenke; ingen kode i `src/` kaller adressene.

## Planen, én commit per punkt

1. a) Feltet `investorside` i `Aksje` i `src/kursdata.py`, med adressen for hver av de 15 i `AKSJEUNIVERS`, og et oppslag på symbolet.
2. b) Avsnittet på aksjesiden i `src/templates/aksje.html`, ruta i `src/app.py`, `docs/hjelp.md` og bildene.
3. c) Testene i `tests/test_investorsiden.py`, og mutantene.

## Avgjort i spesifikasjonen

- **Adressen står i `Aksje`, ved navn og bransje.** Feltet `investorside` har `None` som standard, så demoselskapene i `src/demo.py` ikke har noen adresse. Siden slår opp adressen på symbolet i `AKSJEUNIVERS`, fordi aksjen siden viser, leses fra `aksje` i basen (story 2.2b), og den tabellen har ingen adresse. Skjemaet i basen endres ikke.
- **Plasseringen:** avsnittet står under grafen, rett etter fotnoten «Signalet bygger bare på kurs og volum. Børsmeldinger og kommende finansielle hendelser er ikke med i denne versjonen.». Det er der siden alt sier hva den ikke viser. Avsnittet bruker klassen `fotnote` fra `src/static/stil.css`, så stilarket endres ikke.
- **Teksten** i den ekte versjonen: «Børsmeldingene står på NewsWeb og ofte også på investorsiden til <navn>.», der «investorsiden til <navn>» er lenken. NewsWeb står uten lenke, og «på norsk» står ikke.
- **Teksten i demoen** (svaret kl. 19:49): «Børsmeldingene står på NewsWeb og ofte også på selskapets investorside. <navn> er oppdiktet og har ingen investorside. I den ekte versjonen står lenken her.» Demoen kjennes på det samme som merket «Eksempeltall».
- **Hjelpen bak «?»** sier ingenting om lenker eller børsmeldinger, så ingen tekst i `src/hjelpetekster.py` blir feil og ingen endres. `docs/hjelp.md` får et spørsmål under «Den ekte versjonen». «Ferdig» i README-en får lenken etter flettingen, fordi «Ferdig» betyr flettet til main.

## Det som ikke endres

- Ingen kode henter fra investorsidene, NewsWeb eller Euronext, og ingen test går på nett.
- `data/db/ose.db` og `data/db/demo.db` røres ikke, og skjemaet i basen endres ikke.
- Briefen står.
