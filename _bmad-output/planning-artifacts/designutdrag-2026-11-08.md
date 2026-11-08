---
title: "Utdrag fra designtavla til story 2.12, 8.10, 8.10b og 10.6"
status: aktiv
created: 2026-11-08
updated: 2026-11-08T12:50
---

# Utdrag fra designtavla til story 2.12, 8.10, 8.10b og 10.6

Laget av rådet 08.11.2026 fra designtavla «OSE Signal – designforslag» i Claude, versjon 1792655075-9a81, tavlene «Markedsoversikt» og «Min liste (planlagt, story 8.3)». Grunnen er gruppens svar 08.11 kl. 12:39: egne aksjer bygges som i designforslaget, på oversikten og i Min liste, og Innstillinger har bare «Vis hjelp» og «Vis KI-tekst». Tavla ligger i Claude og ikke i repoet, som i [utdraget 13.10](designutdrag-2026-10-13.md).

Tekstene i «» står ordrett fra tavla. `{{…}}` er felt tavla fyller med eksempeltall. Ingen kurser, volum eller omsetningstall fra tavla står her. Der appen må gjøre noe annet enn tavla, står det under **Avvik**.

## 1. Oversikten: «Dine egne aksjer» under tabellen (2.12)

Rekkefølgen på oversikten er den i §11 i utdraget 13.10: tabellen, så «Dine egne aksjer» med «Følg en aksje», så «Børsdagen kort fortalt».

- Overskriften «Dine egne aksjer» med «?» og antallet: «`{{antallEgne}}` egne · `{{antallTotalt}}` av 18 aksjer i lista».
- Hjelpen bak «?»:
  - «Lista kan ha opptil 18 aksjer. Aksjer du følger selv, står i tabellen sammen med de andre, merket «Egen».»
  - «En ny aksje hentes etter kl. 22 og bruker da 1 kall om dagen. Fjerner du den før det, brukes ingen kall. Valget lagres på denne maskinen.»
  - «Signalet er målt på aksjer som omsettes for over 32 MNOK om dagen. Omsettes aksjen mindre, merkes den «Utenfor målingen». Vil du følge helt andre aksjer, se Min liste.»
- Én rad per egen aksje: navnet, tickeren og bransjen («`{{ticker}}` · `{{bransje}}`»), merket «Egen», og
  - «Hentet. Står i tabellen over.» med knappen «Fjern», eller
  - «Venter på henting i kveld etter kl. 22.» med knappen «Angre»,
  - og merket «Utenfor målingen» der det gjelder.
- «+ Følg en aksje» åpner en dialog:
  - «Følge `{{navn}}`?» og «Aksje på Oslo Børs».
  - Omsetningen, én av tre: «Median omsetning de 3 siste månedene: ca. `{{oms}}` MNOK om dagen, målt `{{dato}}`.» med «Det er over de 32 MNOK signalet er målt på.» eller «Det er under de 32 MNOK signalet er målt på, så den merkes «Utenfor målingen».», eller «Omsetningen er ikke målt ennå. Den står etter hentingen, som måler den med det samme kallet.»
  - «Aksjen hentes ved neste henting, tidligst i kveld etter kl. 22. Siste henting brukte `{{kallSist}}` av 20 kall. Med denne bruker neste henting `{{kallNeste}}`, og `{{kallIgjen}}` er igjen til nye forsøk.»
  - «Valget lagres på denne maskinen og huskes neste gang. Fjerner du aksjen før kvelden, brukes ingen kall.»
  - Knappene «Avbryt» og «Følg aksjen», hovedvalget til høyre, og under dem «Hver aksje bruker 1 kall om dagen.»
  - Når lista er full: «Lista er full. Fjern en aksje for å følge en annen.»
- I tabellen står en egen aksje sammen med de andre, med blått merke «Egen» og blå strek, og den sorteres likt (ordlista på tavla).

## 2. Min liste: «Din egen liste» (2.12)

- Innledningen: «Vil du følge helt andre aksjer, lager du din egen liste. Hver bruker har sin egen gratis nøkkel fra EODHD, som legges inn én gang.»
- «Din egen liste: kom i gang»: «Appen kjører på din egen maskin, så det finnes ingen innlogging hos oss. Du trenger bare din egen gratiskonto hos EODHD. Da velger du selv hvilke aksjer du følger.»
- Steg 1, «Lag en gratis konto hos EODHD»: «Registreringen skjer hos EODHD, ikke hos oss. Gratiskontoen gir 20 kall i døgnet og sluttkurser 1 år tilbake.» og «Kontoen er din egen. Den kan ikke deles med andre, heller ikke i en gruppe.» Lenken «Åpne eodhd.com».
- Steg 2, «Lim inn nøkkelen din»: «Nøkkelen står på kontosiden hos EODHD. Den lagres bare på denne maskinen.» Tavla har feltet «API-nøkkel», knappen «Sjekk nøkkelen» og «Nøkkelen virker. 20 kall igjen i dag.»
  **Avvik:** webserveren rører aldri nøkkelen og henter aldri (AD-10). Steg 2 blir derfor en forklaring, ikke et felt: nøkkelen legges inn når den ekte versjonen startes første gang, og startskriptet spør etter den (gruppens svar 08.11 kl. 12:39).
- Steg 3, «Velg aksjene dine»: tavla har «Start med dagens 15 eller en ferdig liste for 1 bransje, og bytt ut dem du vil. Du kan ha opptil 18.» og knapper for bransjelister.
  **Avvik:** ferdige lister per bransje er story 8.11 og er ikke med nå. Søket står: «Du kan søke blant alle aksjene på Oslo Børs. Er omsetningen målt, står den i søket. Omsettes en aksje for mindre enn 32 MNOK om dagen i median de 3 siste månedene, merkes den «Utenfor målingen».»
- «Følg flere aksjer»: «Lista kan ha opptil 18 aksjer. Hver aksje bruker 1 av de 20 kallene i døgnet, og hovedindeksen 1. Med 18 aksjer er 1 kall igjen til et nytt forsøk hvis noe feiler. Vil du følge andre, bytter du dem inn for noen i lista.» Kallbudsjettet som linjer, regnet av lista: «15 kall: de 15 aksjene», «1 kall: hovedindeksen», «1 kall: din egen aksje», «3 kall: margin». Under: «Hver bruker har sin egen gratiskonto hos EODHD, så lista di påvirker ingen andre.»
- Bytte, «Bytt ut `{{gammel}}`»: «Etter byttet er `{{ny}}` en av de 15, og `{{gammel}}` hentes ikke lenger om kvelden. Det som alt er lagret for `{{gammel}}`, kursene og signalet dag for dag, blir liggende. Bytter du `{{gammel}}` inn igjen senere, mangler signalet for dagene den var ute.» Knappene «Avbryt» og «Bytt inn `{{ny}}`».
- «Utenfor målingen»: «`{{navn}}` er utenfor målingen» med «Median daglig omsetning de 3 siste månedene er `{{oms}}` MNOK, målt `{{dato}}`. Signalet er målt på aksjer som omsettes for over 32 MNOK om dagen, og er ikke prøvd på en aksje som omsettes så lite.» Knappene «Velg en annen» og «Følg aksjen». Forklaringen: «Merket står ved navnet i oversikten, på aksjesiden og i børsometeret. Peker man på det, står omsetningen og hva signalet er målt på.»

## 3. «Børsdagen kort fortalt» på oversikten (10.6)

- Under «Dine egne aksjer». Overskriften «Børsdagen kort fortalt» med «?», merket «Laget av KI» og bryteren «Vis KI-tekst».
- Hjelpen bak «?»: «Et kort sammendrag av børsdagen, skrevet av en språkmodell (KI).» «Modellen fikk bare dette: om hovedindeksen steg eller falt, hvor mange aksjer som gikk bedre enn indeksen, hvor mange som skilte seg ut og med hvilken retning, og hvor mange som steg i hver bransje.» «Ingen prosenter, kurser eller nyheter.» «Teksten sjekkes før den vises: tall med prikket strek står i det modellen fikk. Den gir ikke råd.»
- Eksempelteksten på tavla: «Hovedindeksen falt tirsdag, og `{{bedreDag}}` av `{{antallAlle}}` aksjer gjorde det bedre enn indeksen. 4 skilte seg ut: 2 med positiv retning, 1 negativ og 1 blandet. I energi steg 1 av 4 aksjer.» Under teksten: «Skrevet av Gemma 4 E4B da kursene ble hentet.»
- Uten tekst: «Dagen er uten KI-tekst.», «Perioden er uten KI-tekst. Teksten skrives for én børsdag om gangen.» og «KI-teksten er slått av. Tabellen over viser bare det reglene har regnet ut.»

## 4. «Innstillinger» øverst (8.10 og 8.10b)

- I stripa, etter knappene «Markedsoversikt», «Børsometer» og «Min liste».
- «Hjelp», med «Vis hjelp»: «Faste forklaringer som vi har skrevet og sjekket: hva tallene, bokstavene og fargene betyr. Lik for alle aksjer hver dag, og uten KI.»
- «KI-tekst», med «Vis KI-tekst»: «Noen setninger om dagen og om hver aksje, skrevet av en språkmodell når kursene hentes. Merket «Laget av KI». Hver KI-tekst har også sin egen bryter.»
- Nederst: «Valgene gjelder alle sidene og lagres på denne maskinen.»
- Tavla har også «Vis meg rundt» i stripa. Det er story 8.9 og er ikke med nå.

## 5. Signaldagene i kursgrafen (8.8)

Ikke tegnet på tavla: notatet «Bestemt 08.10» sier «Ikke tegnet ennå: signaldagene i grafen (8.8)». Storyen bygges etter story 8.8 i `epics.md` og `designregler.md`.
