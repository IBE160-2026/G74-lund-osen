# Skisser etter gjennomgangen 06.11.2026

Laget av rådet i chatten 06.11.2026 kl. 21:15–23:55, etter gruppens gjennomgang av appen kl. 20:16–21:10 og svarene underveis. Skissene er forslag og er ikke bygget. Selskapene og tallene er oppdiktet, og det er ingen ekte kurser i bildene. Fargene, skriftene og størrelsene er de samme som i `src/static/stil.css`. Bildene er 1280 px brede.

## Filene

- `aksjesiden-ki-paa.png`: hele aksjesiden. Toppen er som i dag, og under står grafen, rammen «Signalet forklart», «Signalet dag for dag» og boblen for investorsiden.
- `aksjesiden-ki-av.png`: rammen «Signalet forklart» med KI-teksten av.
- `investorsiden-i-demoen.png`: boblen i den ekte versjonen og i demoen, og forhåndsvisningen av demosiden fra `docs/bilder/investorsider/` (story 3.4h).
- `boersometeret-1-uke.png`: børsometeret for en periode, med like store ruter og tabellen åpen.
- `boersometeret-en-dag.png`: børsometeret for én dag med alle 15 aksjene, der arealet følger volumet mot vanlig.

## Gruppens svar 06.11 som skissene bygger på

- 22:16 og 22:23: KI-teksten står i rammen «Signalet forklart», med appens setninger først og bryteren fast øverst til høyre. Investorsiden står som en boble nederst, uten NewsWeb.
- 22:24: datoen og «Vis dagen» står for seg selv.
- 22:25: toppen av aksjesiden er som i dag. Fotnoten under summen flyttes.
- 22:57: for én dag følger størrelsen på rutene volumet (beslutningen 22.10 kl. 23:19 står). Gult har to nyanser som i appen.
- 23:07: ett «?» per kort og del på aksjesiden, og høyst 60 ord i hvert hjelpevindu.
- 23:42: datofeltet viser dagen ved «I går» og en valgt dag, og er tomt i en periode, på alle sidene med datovelger.
- 23:51: investorsidene med tegningene bygges i demoen (story 3.4h).

## Ønsker fra gruppen i skissene, ikke ført som beslutninger

- Børsometeret: «Slik leser du børsometeret» øverst til høyre (22:30), «2 av 3» og «3 av 3» like store og aldri utenfor ruta (22:31 og 22:56), «Mål mot børsen» som kort med «N av 15 gikk bedre enn indeksen» (22:32), tabellen i samme stil som på forsiden (22:32), bransjeoverskriftene med symbol, antall og snitt (22:57), ingen hull ved siden av kortet og datoen samlet med periodeknappene (23:19–23:30).
- Forslag fra rådet: merket U for utbytte og verdiene ved musepekeren i grafen, piler for forrige og neste børsdag ved datoen, «2 av 3» med svart ring også på aksjesiden, og datovelgeren bare ved grafen på aksjesiden.

Hver av dem avgjøres i spesifikasjonen for UX-rettingene før noe bygges.

*Lagt til 2026-11-08:* skissene ble bygget 07.11: aksjesiden i story 8.20a (PR #118, `427a1de2`), børsometeret i 8.20b (PR #119, `8d89cf8c`) og investorsidene i demoen med boblen i 3.4h (PR #120, `7565651f`). Setningen over om at skissene ikke er bygget, gjaldt da de ble lagt inn.
