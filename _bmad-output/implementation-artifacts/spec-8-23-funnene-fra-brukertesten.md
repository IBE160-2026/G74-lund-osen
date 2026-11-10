---
title: 'Story 8.23: funnene fra brukertesten 10.11 (del A)'
type: 'feature'
created: '2026-11-10'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '86d1fe4f'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designregler.md'
---

Skrevet 10.11 etter instruksjonen «Del A, funnene fra brukertesten 10.11» (lest kl. 21:31), med tillegget om overskriften i Min liste (gruppens funn kl. 14:15), tillegg 2 (gruppens svar kl. 14:53 og 14:59), tillegg 3 (gruppens svar kl. 15:54) og tillegget om demoen (gruppens svar kl. 15:57). Alt føres ordrett i `docs/ai-prompts/2026-11-10.md` når instruksjonen har Utført-linje. Bygget fra main (`86d1fe4f`), på grenen `8-23-funnene-fra-brukertesten`, i worktreen `G74-lund-osen-8-23`. 8.21 og 8.22 er tatt av de åpne PR-ene #139 og #138, så 8.23 er neste ledige nummer i Epic 8.

*Svar 2026-11-10 kl. 13:54 (gruppens svar):* «ja» til del A og B. Rådet anbefalte det.

*Svar 2026-11-10 kl. 14:15 (gruppens funn), 14:53 og 14:59 (gruppens svar), 15:54 og 15:57 (gruppens svar):* tilleggene 1, 2 og 3 og tillegget om demoen er en del av del A. Rådet anbefalte alle.

Grensene i appen som styrer delene: `src/static/hjelp.js` er det eneste skriptet, og testene krever det (`test_app.py`, `test_hjelpetekster.py`, `test_aksjesiden_8_20a.py`), så alt annet er lenker og skjemaer. Hver endring i `stil.css` eller `hjelp.js` gir nye avtrykk for alle bildene i `docs/appen/`. Demoen har vurderinger fra 21.09 til 09.10 og ingen ventende endringer i lista.

## Spørsmål til gruppen

Forslaget er det som bygges. Spørsmålene står åpne til gruppen har svart.

1. **«Dine egne aksjer» (A1).** Radene er en liste med navn, symbol og bransje i teksten. *Forslag:* en tabell i samme `tabellboks` som tabellen over, med samme rad, skrift og skillelinje, bransjeikonet i en egen liten celle foran navnet, og status og knappen i hver sin kolonne. Kursene står fortsatt i tabellen over; denne lista er for å følge og fjerne.
2. **Sorteringen (A2).** Lenkene i kolonneraden har ikke noe anker, så siden hopper til toppen. *Forslag:* `#aksjene` på sorteringslenkene, «Standard rekkefølge» og filterknappene, uten skript.
3. **«?» (A3).** *Forslag:* et nytt trykk på samme «?» lukker hjelpen, både i sidefeltet og under knappen på smal skjerm, i `hjelp.js`. Uten skript gjør nettleseren det selv (`popovertarget` veksler).
4. **Små ruter i børsometeret (A4).** I dag viser de minste rutene bare fargen, og de nest minste bare symbolet. *Forslag:* ruter som har plass til symbolet, viser også endringen og styrken i liten skrift («-1,7 %», «2/3»), og alle rutene har en `title` med symbolet, endringen og styrken, så musa viser det også på de minste. Forklaringen «Rammen» sier at ringen rundt styrken gjelder siste børsdag, og at den tykke rammen rundt ruta er gul ved 3 av 3 og mørk ved 2 av 3.
5. **«Volum mot vanlig» med to desimaler (A4).** I dag står flere desimaler når to ville rundet over en grense (1,4996 vises ikke som 1,50). *Forslag:* alltid to desimaler, og et tall like under en grense rundes ned mot den siden det står på (1,4996 blir 1,49), så tallet og ordet (vanlig, høyt, lavt) aldri sier ulikt.
6. **«Se tallene som tabell» (A5 og tillegg 3).** *Forslag:* tabellen står åpen fra start, og knappen, som ser ut som de andre knappene, lukker den. Tabellen har stilen til tabellen på oversikten og beholder bransjeradene. «?» ved «Endring» og «Volum mot vanlig». Hjelpen ved volumet sier lavt under 1, vanlig fra 1 til 1,5 og høyt over 1,5 (`VOLUMFAKTOR`), og hjelpen ved bransjeraden sier at snittet er gjennomsnittet av endringen for aksjene i bransjen som har kurs, uten vekt. Svaret 26.10 kl. 15:21 (f) får Rettet-linje i epics.md.
7. **Oransje i Innstillinger (A6).** Designreglene sier at sterk oransje står på blekk. *Forslag:* bryteren er oransje når den er på, med svart knott, også KI-bryteren på aksjesiden og bryteren for dagens tekst, og siden man er på har oransje kant og strek i toppen, som er blekk. designregler.md får regelen som Lagt til-linje.
8. **Kallene på «Følg en aksje» (A7).** *Forslag:* 20, 1 kall per aksje, taket og «Med N aksjer er M kall igjen» regnes av `KVOTE`, `TAK`, `INDEKSKALL` og lista, ikke skrevet for hånd.
9. **Filteret «3 av 3» (A8).** *Forslag:* knappene har antallet i parentes, for eksempel «3 av 3 positiv (2)». Gir filteret 0, står «Ingen fikk 3 av 3 positiv. 3 fikk 2 av 3 positiv: se dem.», og lenken viser dem som fikk 2 av 3 i samme retning, med samme periode og sortering.
10. **Overskriften i Min liste (tillegg 1).** *Forslag:* med «Alle» står «10 av 15 skilte seg ut mandag, 6 av dem i Min liste», og med «Min liste» som før, «6 av 9 i Min liste skilte seg ut mandag».
11. **0-brikken (tillegg 2).** *Forslag:* «Slik leser du tabellen» viser +1, 0 og -1, med 0 hvit med kant som i tabellen.
12. **Teksten under kursgrafen (tillegg 2).** *Forslag:* først én kort setning i vanlig størrelse om linjene og tegnene, og resten bak «Mer om grafen» (`details`), med de samme setningene som nå. Bygges etter at #134 og #135 er flettet; de er flettet.
13. **«Signalet forklart» (tillegg 2).** *Forslag:* «13 av de 15 aksjene i lista steg og 2 falt», med antallet i lista den dagen.
14. **Endringer som venter (tillegg 2).** *Forslag:* når en endring i lista venter på hentingen etter kl. 22, står en kort linje øverst på oversikten og i Min liste: «N endringer i lista tas i bruk ved hentingen etter kl. 22.» I demoen står den med «Eksempeltall» og sier at demoen ikke henter, så endringene ikke tas i bruk der.
15. **3 av 3 det siste året (tillegg 2).** *Forslag:* hjelpen ved signalstyrken forklarer 3 av 3, og aksjesiden sier under «Signalet dag for dag» for eksempel «3 av 3 fire ganger det siste året, sist 14.10», regnet av vurderingene som er lagret. Er serien kortere enn et år, står «siden» og den første dagen. Ingen avkastning (NFR-06). I demoen er det vurderingene fra 21.09.
16. **Sjekkortene (tillegg 2).** *Forslag:* tykk venstrekant, 4 px, i `--opp`, `--ned` eller `--dempet-2` etter resultatet; merket står som før.
17. **«Alle | Min liste» på oversikten (tillegg 2).** *Forslag:* «Min liste» over «Aksjene» filtrerer tabellen på oversikten (`/?vis=min`) og beholder perioden og sorteringen, og knappen «Min liste» i menyen går til siden. Det som står om valget i designregler.md og designutdragene, får Rettet-linje.
18. **Demoen (tillegget om demoen).** *Forslag:* hver del kan ses i demoen uten nøkkel. Endringene som venter og «3 av 3 … det siste året» står med «Eksempeltall», aldri ekte navn eller kurser. Snarveien for demoen hører til del C.

## Delene og «Ville feilet hvis»

Hver del får tester med «Ville feilet hvis» og én mutant med kopi før og sha256 mot HEAD etter. Delene, testene og mutantene føres under, del for del, når de er bygget.
