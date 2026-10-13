---
title: "Utdrag fra designtavla til story 8.0d"
status: aktiv
created: 2026-10-13
updated: 2026-10-13T23:18
---

# Utdrag fra designtavla til story 8.0d

Laget av rådet 13.10.2026 fra designtavla «OSE Signal – designforslag» i Claude, versjon 117. Tavla ligger i Claude og ikke i repoet, så story 8.0d sier at rådet gir utdraget fra den. Verdiene er lest ut av kildekoden til tavlene «Markedsoversikt», «Aksjedetalj – Equinor» og «Bransjer». Tavla er tegnet 1280 px bred med eksempeltall, og ingen kurser eller volum fra tavla står her.

Utdraget er grunnlaget for planen til 8.0d. Ingenting her er en regel før gruppen har godkjent teksten planen skriver inn i `designregler.md`. Det som står i §13, er ikke avgjort.

## 1. Farger

| Navn | Verdi | Brukes til på tavla |
|---|---|---|
| Blekk | `#16181D` | Hovedtekst, stripa øverst, kolonneraden, fyllet i «3 av 3» og knappen «?» |
| Tekst | `#3C4048` | Brødtekst og innledninger |
| Dempet | `#5F646C` | Etiketter, linja under selskapsnavnet, fotnoter og aksetekst i grafen |
| Dempet 2 | `#70757D` | Teksten i en sjekk som ga 0 |
| Bakgrunn | `#F3F2EE` | Hele siden |
| Kort | `#FFFFFF` | Kort og tabell |
| Strek | `#E4E2DB` | Kanten rundt kort og linja mellom radene |
| Strek 2 | `#D6D3CA` | Kanten rundt en sjekk som ga 0, rundt merker og rundt knapper uten fyll |
| Rutenett | `#ECEAE4` | Vannrette linjer i grafen |
| Positiv | `#13703C` på `#E4F4EA` | Retningen Positiv, +1 og stigning |
| Negativ | `#B42318` på `#FBE9E6` | Retningen Negativ, -1 og fall |
| Blandet | `#6A46A0` på `#F0EBF8` | Retningen Blandet |
| Ingen | `#5F646C` på `#EEEDEA` | Retningen Ingen |
| Gul | `#F2B53A` | Ringen og streken for 3 av 3, logoens høyeste søyle, klokka i stripa og fokus |
| Gul understrek | `#F8DE9C` | Markeringen bak det viktigste i overskriften |
| Gult bånd | `#FFF6DC`, kant `#F0E3BD`, tekst `#6B4E00` | Båndet «Skilte seg ut» |
| Gul rad | `#FFFCF3`, strek `#F1E9D3` | Radene under «Skilte seg ut» |
| Grått bånd | `#F7F6F2`, kant `#E4E2DB`, tekst `#3C4048` | Båndet «Øvrige aksjer» |
| Hjelp | `#6B4E00` på `#FFF1CC` | Merket «Hjelp» i hjelpevinduet |
| Kurs | `#1F4E8C` | Kurslinja i grafen |
| Snitt | `#B86E12` | 50-dagers snittet i grafen |
| Nøytralsone | `#CFCABD`, 45 % dekning | Feltet ±2 % rundt snittet i grafen |
| Det grå feltet | spor `#F1EFEA`, felt `#D9D5CB` | Skalaen i hvert sjekkort på aksjesiden |
| I stripa | tekst `#DADDE2`, `#C9CCD2` og `#A9AEB8`, kanter `#3A3E47` og `#2A2E36` | Linja under logoen, merket «Eksempeltall» og skillestreker |
| Under kolonnenavn | `#B9BDC5` | Linja under navnet i kolonneraden |

Blått (`#1D47A8`, `#2457C5` og `#E7EEFC`) er merket «Egen» og hører til 2.12.

## 2. Kontrast

Regnet med formelen i WCAG 2.1. Tekst skal ha minst 4,5:1. Streker og felt som må ses for å forstå siden, skal ha minst 3:1 (WCAG 1.4.11).

| Forgrunn på bakgrunn | Kontrast |
|---|---|
| `#16181D` på `#F3F2EE` | 15,85 |
| `#3C4048` på `#F3F2EE` | 9,28 |
| `#5F646C` på `#F3F2EE` og `#FFFFFF` | 5,32 og 5,96 |
| `#70757D` på `#FFFFFF` | 4,64 |
| `#13703C` på `#FFFFFF`, `#FFFCF3` og `#E4F4EA` | 6,16, 6,00 og 5,40 |
| `#B42318` på `#FFFFFF`, `#FFFCF3` og `#FBE9E6` | 6,57, 6,41 og 5,60 |
| `#6A46A0` på `#F0EBF8` | 5,99 |
| `#5F646C` på `#EEEDEA` | 5,09 |
| `#FFFFFF` på `#13703C`, `#B42318` og `#16181D` | 6,16, 6,57 og 17,76 |
| `#6B4E00` på `#FFF6DC` og `#FFF1CC` | 7,17 og 6,89 |
| `#B9BDC5`, `#DADDE2`, `#C9CCD2` og `#A9AEB8` på `#16181D` | 9,43, 13,04, 11,04 og 7,98 |
| `#1F4E8C` på `#FFFFFF` | 8,31 |
| `#B86E12` på `#FFFFFF` | 3,98 |
| `#F2B53A` på `#FFFFFF`, `#F3F2EE` og `#16181D` | 1,83, 1,64 og 9,68 |
| `#a67c00` (ringen i appen i dag) på `#FFFFFF`, `#F3F2EE` og `#16181D` | 3,82, 3,41 og 4,65 |
| `#CFCABD` (nøytralsonen) på `#FFFFFF` | 1,64 |
| `#D9D5CB` (det grå feltet) på `#F1EFEA` | 1,28 |

Lysheten (L*) til de fire retningsfargene er nesten lik: positiv 41, negativ 40, blandet 38 og ingen 42. De skiller seg mest i fargetone, så retningen må alltid stå med ord og symbol, som i dag («Uten farger» i `designregler.md` §4).

## 3. Skrift

`designregler.md` §1 gjelder: IBM Plex Sans til tekst og tall, med tabelltall, og Newsreader til overskrifter og titler. Størrelsene på tavla, i px ved 1280 px bredde:

| Del | Skrift | Størrelse og vekt |
|---|---|---|
| Logoen «OSE Signal» | Newsreader | 27, 600, bokstavavstand -0,01em |
| Overskriften i oversikten | Newsreader | 52, 500, linjehøyde 1,06, bokstavavstand -0,015em |
| Overskriften på aksjesiden | Newsreader | 56, 500, linjehøyde 1,05, bokstavavstand -0,02em |
| Delene på aksjesiden | Newsreader | 36 |
| Navnet på en sjekk | Newsreader | 30, 600, linjehøyde 1,1 |
| Tittelen i hjelpevinduet | Newsreader | 23, 600, linjehøyde 1,2 |
| Innledningen | IBM Plex Sans | 17, linjehøyde 1,5–1,55, farge Tekst, høyst 560 px bred i oversikten og 780 px på aksjesiden |
| Små overskrifter («Slik leser du tabellen», «Sjekk 1») | IBM Plex Sans | 12,5, 700, store bokstaver, bokstavavstand 0,07em, farge Dempet |
| Punktene i «Slik leser du tabellen» | IBM Plex Sans | tittelen 15, 600, og teksten 13,5, linjehøyde 1,45, farge Dempet |
| Kolonnenavnene | IBM Plex Sans | 14, 700, hvit på blekk, og linja under 12 i `#B9BDC5` |
| Selskapsnavnet i tabellen | IBM Plex Sans | 16,5, 600 under «Skilte seg ut» og 15,5, 600 ellers, understreket i `#B5B9C0`, 1,5 px tykk og 4 px under teksten |
| Linja under navnet (ticker og bransje) | IBM Plex Sans | 12,5, farge Dempet, med bransjesymbolet i 15 px |
| Tallene i tabellen | IBM Plex Sans, tabelltall | 16 under «Skilte seg ut» og 15 ellers, og linja under 13 og 12,5 |
| Båndene | IBM Plex Sans | 14,5, 700, og teksten bak 13,5 |
| Pillene for retning | IBM Plex Sans | 14, 600 |
| Nøkkeltallene på aksjesiden | IBM Plex Sans, tabelltall | verdien 36, 500, bokstavavstand -0,01em, og etiketten 13,5, 600, farge Dempet |
| Målingen i et sjekkort | IBM Plex Sans, tabelltall | 36, 600, og teksten bak 14,5 |
| Brødtekst i hjelpen | IBM Plex Sans | 15, linjehøyde 1,55, farge Tekst |
| Fotnoten nederst | IBM Plex Sans | 13, linjehøyde 1,5, farge Dempet |
| Aksetekst i grafen | IBM Plex Sans | 12, farge Dempet |

## 4. Stripa øverst

- Blekk som bakgrunn over hele bredden. Den øverste raden er 72 px høy, og den andre 38 px, med en strek i `#2A2E36` mellom.
- Til venstre logoen: tre avrundede søyler i en boks på 28 × 24 px, de to første hvite og den høyeste gul, og «OSE Signal» i hvitt. Søylene er `<rect x="1" y="14" width="6.5" height="9" rx="1.6"/>`, `<rect x="10.75" y="8" width="6.5" height="15" rx="1.6"/>` og `<rect x="20.5" y="1" width="6.5" height="22" rx="1.6"/>`.
- Den andre raden: til venstre en klokke i gult og «Oppdatert <ukedag> <dato> kl. <tid>» i 13,5, 600, `#DADDE2`. Til høyre merket «Eksempeltall» i 12,5, `#C9CCD2`, med kant i `#3A3E47` og runde hjørner, når siden viser demobasen.
- Når dataene ble hentet, står i dag i linja under tittelen. «· Neste: <dag> etter kl. 22» bak «Oppdatert» er 8.19.
- Knapperaden (Markedsoversikt, Børsometer, Min liste), «Innstillinger» og «Vis meg rundt» står også i stripa på tavla, men hører til 8.3, 8.10 og 8.9.

## 5. Oversikten

- Siden har bakgrunnen `#F3F2EE` og 120 px marg på hver side ved 1280 px, så innholdet er 1040 px bredt.
- Øverst (teksten kommer i 8.0e PR 2): overskriften og innledningen til venstre, og kortet «Slik leser du tabellen» til høyre, 390 px bredt, med 36 px mellom. Kortet er hvitt med kant i Strek, radius 16 og luft 20/22 px. Hvert punkt har et lite felt på 36 × 36 px (radius 10, `#F3F2EE`) med et symbol til venstre.
- Det viktigste i overskriften (på tavla «4 av 16 aksjer») har gul understrek: bakgrunnen `linear-gradient(transparent 60%, #F8DE9C 60%)`.
- Tabellen står i ett kort: hvitt, kant 1 px i Strek og øverste kant i blekk, radius 16, og skyggen `0 1px 2px rgba(22, 24, 29, 0.04), 0 10px 28px rgba(22, 24, 29, 0.05)`. Kolonneraden er 64 px høy med blekk som bakgrunn, så kortet har svart topp.
- Kolonneraden: navnene i hvitt, og under dem en linje i `#B9BDC5`: «NOK» under Sluttkurs, «i går» under Endring og Signalstyrke, og «hva sjekkene peker mot» under Retning.
- Båndene er egne rader øverst i hver del. «Skilte seg ut» er 46 px høyt i Gult bånd, med antallet i en pille (`#6B4E00` med hvit tekst, 12,5, 700) og «signalstyrke 2 eller mer» bak. «Øvrige aksjer» har samme form i Grått bånd, med antallet i en pille i `#3C4048`.
- Radene under «Skilte seg ut» er 66 px høye, med bakgrunnen `#FFFCF3` og strek i `#F1E9D3`. En rad med 3 av 3 har i tillegg en gul strek på 4 px langs venstre kant (`box-shadow: inset 4px 0 0 #F2B53A`). Radene under «Øvrige aksjer» er 54 px høye og hvite, med strek i Strek.
- Tallene står til høyre i kolonnen, med 22 px luft mot høyre. Endringen har farge etter fortegnet.
- Bunnlinja har 32 px over seg, en strek i Strek øverst og 16 px luft, og teksten er 13 i Dempet.

## 6. Piller, brikker og merker

- T, B og I i en rad: hver i en brikke på minst 34 × 24 px, radius 6, 12, 700, med 3 px mellom bokstaven og verdien og 3 px mellom brikkene. +1 har grønt fyll og hvit tekst, -1 rødt fyll og hvit tekst, og 0 er hvit med tekst i `#70757D` og kant 1,5 px i `#D6D3CA`. På aksjesiden er brikkene 36 × 26 px og 12,5.
- «3 av 3»: en pille 26 px høy, radius 999, 13, 700, fyll i blekk, hvit tekst, kant 1,5 px i blekk og en gul ring på 2 px utenfor (`box-shadow: 0 0 0 2px #F2B53A`).
- «2 av 3»: samme pille, hvit med tekst og kant i blekk, uten gult.
- «1 av 3» og «0 av 3»: tekst uten pille, 700, farge Tekst.
- Retning: en pille 28 px høy, radius 999, 14, 600, med symbolet først: ↑ Positiv, ↓ Negativ, ↔ Blandet og – Ingen, i fargene fra §1.
- Merkene for ticker og bransje øverst på aksjesiden: 28 px høye, radius 8, hvite med kant i `#D6D3CA`, 13,5, 600, farge Tekst, og bransjen med symbolet.

## 7. Hjelp bak «?»

- Knappen er en svart sirkel på 22 px med et hvitt «?» (13, 700). Klikkflaten rundt er minst 44 × 44 px.
- Vinduet er hvitt, høyst 440 px bredt, radius 16, luft 16/20/18/22 px, med skyggen `0 24px 60px rgba(0, 0, 0, 0.30), 0 2px 6px rgba(0, 0, 0, 0.12)`. Øverst står merket «Hjelp» (12,5, 700, i fargene Hjelp fra §1 og med runde hjørner), så tittelen i Newsreader og teksten under.

## 8. Aksjesiden

- Øverst merkene for ticker og bransje, så overskriften og innledningen. På tavla er overskriften «Equinor skilte seg ut tirsdag», med gul understrek på «skilte seg ut tirsdag».
- Nøkkeltallene: fire hvite kort på rad (Sluttkurs, Endring, Signalstyrke og Retning), 136 px høye, med kant i Strek, radius 16, luft 18/20 px og 16 px mellom. Etiketten står øverst, verdien stort, og en kort forklaring nederst, som «fra mandag til tirsdag» eller «trend, bevegelse og interesse slo ut». Signalstyrken har tallet stort med «av 3» bak og T, B og I som brikker. Retningen har ordet stort i retningsfargen, med symbolet.
- De 3 sjekkene: tre hvite kort side om side med 16 px mellom, luft 20/22 px og radius 16. Hvert kort har «Sjekk 1» og resultatet i en pille med lys bakgrunn (+1 i `#13703C` på `#E4F4EA`, -1 i `#B42318` på `#FBE9E6`), navnet på sjekken i Newsreader, hva sjekken måler, målingen stort (for eksempel «+3,1 % over snittet»), skalaen med det grå feltet, og regelen nederst.
- Det grå feltet: et spor på 10 px (`#F1EFEA`, runde ender) med feltet der sjekken gir 0 (`#D9D5CB`). Grensene står over feltet (for eksempel «-2 %» og «+2 %», 11,5, Dempet) og «gir 0» under (11,5, 600). Målingen er en prikk på 20 px i resultatfargen, med hvit kant på 3 px og skyggen `0 1px 3px rgba(0, 0, 0, 0.25)`. For interesse går feltet fra 0 til 1,5 × medianen. På tavla går skalaen for trend til tre ganger grensen på hver side, skalaen for interesse fra 0 til 6 ×, og skalaen for bevegelse er tilpasset målingen. Skalaen er skjult for skjermlesere (`aria-hidden`), fordi teksten i kortet sier det samme.
- Kursgrafen: kurslinja i `#1F4E8C`, 2,5 px, med runde ledd og siste punkt som en prikk med hvit kant. Snittet i `#B86E12`, 1,75 px, heltrukket. Nøytralsonen ±2 % som et felt i `#CFCABD` med 45 % dekning. Vannrette linjer i `#ECEAE4`, streker for månedene i `#D6D3CA`, og aksetekst i 12, Dempet. Navnene på kurslinja og snittet står ved enden av linjene, i linjefargen. Stiplet linje brukes bare for hovedindeksen (`designregler.md` §4).
- Tilbakelenken står i dag øverst som «← Markedsoversikt». På tavla gjør knapperaden i stripa (8.3) den jobben. 8.0d sier tekst uten pil.

## 9. Avstander

- Sidemargen er 120 px ved 1280 px. På en telefon (390 px) er den 16 px.
- Mellom delene er det 40–44 px i oversikten og 60 px på aksjesiden, og 28 px fra overskriften til nøkkeltallene.
- Kort har radius 16, kant 1 px i Strek, luft 18–22 px og 16 px mellom kort på rad.
- Piller har radius 999, brikker radius 6 og merker radius 8.
- Knapper og klikkflater er minst 44 px høye.

## 10. Fokus

Tavla har `a:focus-visible, button:focus-visible { outline: 3px solid #F2B53A; outline-offset: 2px }`. Gult har 1,64:1 mot bakgrunnen og 1,83:1 mot hvitt, under 3:1, som fokus skal ha (WCAG 1.4.11). Se avvik 2 i §13.

## 11. Rekkefølgen av delene

Oversikten på tavla, ovenfra:

1. Stripa (§4).
2. Overskriften, innledningen og «3 av 3»-linja, med «Slik leser du tabellen» til høyre (8.0e PR 2).
3. Hovedindeksen med søylene (2.9 og 2.9b, ikke 8.0d).
4. «Aksjene» med antallet og valget mellom Alle og Min liste (8.3 og 8.11, ikke 8.0d).
5. Tabellen (8.0e og §5).
6. «Dine egne aksjer» og «Følg en aksje» (2.12, ikke 8.0d).
7. «Børsdagen kort fortalt» med KI-teksten (10.6, ikke 8.0d).
8. Bunnlinja.

Aksjesiden på tavla, ovenfra:

1. Stripa (§4).
2. Merkene, overskriften og innledningen.
3. Nøkkeltallene.
4. De 3 sjekkene med det grå feltet.
5. Kursgrafen. Periodene er 8.16, U-merkene 8.14, volumet med grensen for interesse 8.7 og signaldagene 8.8.
6. «Se nærmere» (8.4, ikke 8.0d).
7. KI-teksten (10.3, ikke 8.0d).
8. «Signalet dag for dag» (2.7, ikke 8.0d).

I appen i dag står kursgrafen før sjekkene på aksjesiden.

Feilsiden har ingen egen tavle.

## 12. Bransjesymbolene

De 13 bransjene og symbolene fra tavla «Bransjer». Hvert symbol er en strektegning i `viewBox="0 0 24 24"`, uten fyll, med strek 1,8 px i tekstfargen og runde ender og ledd (`fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"`). I tabellen er symbolet 15 px og grått (Dempet). Symbolene ligger i appen og hentes ikke fra nettet. Bransjene til de 15 i `AKSJEUNIVERS` i `src/kursdata.py` har de samme navnene som de 8 første i tabellen under (lest 13.10).

| Bransje | Hva som hører til | Hos Euronext (ICB) | Aksjer i lista i dag |
|---|---|---|---|
| Energi | Olje og gass, oljeservice og utstyr til fornybar energi | Energy | EQNR, VAR, AKRBP, DNO |
| Finans | Banker, forsikring og andre finansselskaper | Financials | DNB, GJF |
| Industri | Forsvar, maskiner, bygg, elektronikk og transport utenom skip | Industrials, utenom shipping | KOG |
| Materialer | Metaller, gruver, kjemikalier, gjødsel og skog | Basic Materials | NHY, YAR |
| Shipping | Rederier og skipsfart | Marine Transportation, som indeksen OBSHX | FRO, MPCC |
| Telekom | Mobil, bredbånd og utstyr til nett | Telecommunications | TEL |
| Sjømat | Oppdrett og fiske | Farming, Fishing, Ranching and Plantations, som indeksen OBSFX | MOWI, SALM |
| Konsum | Mat, drikke, dagligvarer og pleieprodukter, utenom sjømat | Consumer Staples, utenom sjømat | ORK |
| Forbruk | Butikker, media, reiser, fritid og biler | Consumer Discretionary | ingen |
| Teknologi | Programvare, IT-tjenester og maskinvare | Technology | ingen |
| Helse | Legemidler, bioteknologi, medisinsk utstyr og helsetjenester | Health Care | ingen |
| Eiendom | Selskaper som eier, leier ut eller utvikler eiendom | Real Estate | ingen |
| Kraft | Strøm og fornybar kraft, vann og avfall | Utilities | ingen |

Innholdet i hvert symbol, ordrett fra tavla:

```
Energi:     <ellipse cx="12" cy="5" rx="6" ry="2"></ellipse><path d="M6 5v14c0 1.1 2.7 2 6 2s6-.9 6-2V5"></path><path d="M6 10c0 1.1 2.7 2 6 2s6-.9 6-2"></path><path d="M6 15c0 1.1 2.7 2 6 2s6-.9 6-2"></path>
Finans:     <path d="M3 9l9-5 9 5"></path><path d="M5 10v7"></path><path d="M9.7 10v7"></path><path d="M14.3 10v7"></path><path d="M19 10v7"></path><path d="M3 20h18"></path>
Industri:   <circle cx="12" cy="12" r="3"></circle><circle cx="12" cy="12" r="6.5"></circle><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"></path>
Materialer: <path d="M3 19l2-4h6l2 4z"></path><path d="M11 19l2-4h6l2 4z"></path><path d="M7 15l2-4h6l2 4"></path>
Shipping:   <path d="M3 15h18l-2.5 5h-13z"></path><path d="M5.5 15v-4h5v4"></path><path d="M10.5 15v-4h5v4"></path><path d="M15.5 11V7h3v8"></path>
Telekom:    <path d="M12 10v11"></path><path d="M8 21h8"></path><circle cx="12" cy="8" r="2"></circle><path d="M7.8 3.8a6 6 0 0 0 0 8.4"></path><path d="M16.2 3.8a6 6 0 0 1 0 8.4"></path>
Sjømat:     <path d="M2 12c2.5-4 8-6 12-3 1 .7 2 1.8 2.5 3-.5 1.2-1.5 2.3-2.5 3-4 3-9.5 1-12-3z"></path><path d="M16.5 12l5.5-4v8z"></path><circle cx="7" cy="11" r="0.9"></circle>
Konsum:     <path d="M4 9h16l-1.5 10h-13z"></path><path d="M8 9l3-5"></path><path d="M16 9l-3-5"></path><path d="M9 13v3M12 13v3M15 13v3"></path>
Forbruk:    <path d="M3 11.5v-7A1.5 1.5 0 0 1 4.5 3h7l9.5 9.5-8.5 8.5z"></path><circle cx="8" cy="8" r="1.6"></circle>
Teknologi:  <rect x="6.5" y="6.5" width="11" height="11" rx="1.5"></rect><rect x="9.5" y="9.5" width="5" height="5" rx="0.5"></rect><path d="M9.5 3v3.5M14.5 3v3.5M9.5 17.5V21M14.5 17.5V21M3 9.5h3.5M3 14.5h3.5M17.5 9.5H21M17.5 14.5H21"></path>
Helse:      <path d="M9 3.5h6v5.5h5.5v6H15v5.5H9V15H3.5V9H9z"></path>
Eiendom:    <path d="M5 21V4.5A1.5 1.5 0 0 1 6.5 3h11A1.5 1.5 0 0 1 19 4.5V21"></path><path d="M3 21h18"></path><path d="M9 7h1.5M13.5 7H15M9 11h1.5M13.5 11H15"></path><path d="M10.5 21v-4.5h3V21"></path>
Kraft:      <path d="M13 2.5L5 13.5h6l-1 8 8-11h-6z"></path>
```

## 13. Avvik planen må avgjøre

1. Ringen rundt «3 av 3»: tavla har `#F2B53A`, som har 1,83:1 mot hvitt. Appen har `#a67c00` fra 8.0c, med en test for minst 3:1.
2. Fokus: den gule fokusringen på tavla har 1,64:1 mot bakgrunnen. Fokus skal ha minst 3:1, for eksempel med blekk ytterst eller en dobbel ring.
3. «2 av 3»: tavla har en hvit pille med kant i blekk. `designregler.md` §3 og beslutningen 13.10 kl. 21:27 sier fet skrift og strek, uten fyll og uten gult.
4. Demobanneret er gult i dag (`#fff3cd` med kant `#c9a227`), men gult betyr 3 av 3. Tavla viser «Eksempeltall» som et merke i stripa, og 8.0d krever at «Eksempeltall» synes like godt som før.
5. Navnet på snittet i grafen står i `#B86E12`, som har 3,98:1 mot hvitt. Det er under 4,5:1 for liten tekst, men streken selv holder 3:1.
6. Det grå feltet (`#D9D5CB` på `#F1EFEA`, 1,28:1) og nøytralsonen (`#CFCABD`, 1,64:1 mot hvitt) synes svakt. Teksten ved feltet sier det samme, men feltet bør kunne ses.
7. Tavla har en liten vinkel (›) etter selskapsnavnet. Pilene er bare for retning (FR-103), og tilbakelenken skal ha tekst uten pil.
8. Smal skjerm: tavla er 1280 px bred. Oversikten er i dag 585 px bred i et vindu på 390 px. Ved 390 px må tabellen få plass, eller rulle i en egen boks.
9. Overskriften på aksjesiden: tavla viser bare tilfellet der aksjen skilte seg ut. Hva den sier når aksjen ikke skilte seg ut, eller ikke ble vurdert, står ikke på tavla.
10. Endringen som eget nøkkeltall: tavla har fire kort, og appen har tre i dag (sluttkurs, signalstyrke og retning). Beløpet i NOK og lav og høy er 8.5.
11. Ticker og bransje under navnet i oversikten: dataene finnes i `AKSJEUNIVERS` i dag. Om linja kommer i 8.0d eller med 2.11, avgjøres i planen.

## 14. På tavla, men ikke i 8.0d

Knapperaden (8.3), Innstillinger (8.10), «Vis meg rundt» (8.9), «Neste: …» i stripa (8.19), hovedindeksen og søylene (2.9 og 2.9b), periodevalget (8.16 og 8.17), stjernen og Min liste (8.3), listene og filteret (8.11), «var 1 mandag» (8.12), sorteringen (8.15), egne aksjer og merket «Egen» (2.12), NOK og lav og høy (8.5), klikk på T, B og I (ingen story ennå), «Se nærmere» (8.4), KI-tekstene (10.3 og 10.6), historikken (2.7), U-merkene (8.14), sjekk 2 og 3 i grafen (8.7) og signaldagene (8.8).
