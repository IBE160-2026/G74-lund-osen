# Bildene for story 9.19: grensen og bildene av appen

Bildene er tatt av demoen 17.11 med Edge uten vindu, med skriptet og jobblista
fra vinduet som bygde 3.3k, en demobase i en midlertidig mappe og webserveren på
en ledig port, aldri 8000. Alle bildene ble tatt to ganger, med en ny demobase
hver gang, og var like byte for byte. «Før» er bildet på main (`e00f6502`), og
«etter» er grenen `9-19-grensen-og-bildene` (`10a96e50`), etter rettingene i
9.18. Bare demoen, med oppdiktede selskaper og kurser.

- `aksjesiden-brfe-demo.png`: trendkortet sier «mot 50-dagers snitt» i stedet
  for «mot MA50» (HE8).
- `din-egen-liste-demo.png`: steg 2 heter «Lim inn nøkkelen i startskriptet»
  (HE10).
- `innstillinger-demo.png`: teksten ved «Vis hjelp» sier at av også skjuler
  «Vis meg rundt» og «Spill av omvisningen» (HE5).
- `min-liste-demo.png`: «Øvrige aksjer» har ett tall per gruppe, «2 med
  signalstyrke 0 eller 1» (HE9).
- `vis-meg-rundt-demo.png`: første steg står uten at siden blar, så toppen med
  knappene synes (HE18), og boksen har fast bredde (HE16).
- `oversikten-390-demo.png` (i `docs/appen/mobil/`): styrken og retningen står
  under selskapsnavnet i hver rad (HE3). Bildet er hele siden, 4773 px høyt i
  stedet for 4477, fordi radene er høyere. Før ville 4477 px kuttet bort
  slutten av «Børsdagen kort fortalt».
- De tolv andre bildene i `docs/appen/` og `docs/appen/mobil/` er byte for byte
  de samme og er ikke byttet.

Spørsmålet før sletting av et notat (HE2) og lenken «Til <måned>» i «Signalet
dag for dag» (HE14) står ikke i noen av bildene, fordi ingen av dem viser den
siden eller en annen måned valgt.
