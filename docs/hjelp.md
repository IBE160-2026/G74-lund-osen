---
title: "Hjelp til «Kom i gang»"
status: aktiv
created: 2026-10-11
updated: 2026-11-08T12:31
---

# Hjelp til «Kom i gang»

Spørsmål og svar til «Kom i gang» i [README-en](../README.md) og til [installasjonen](installasjon.md), sortert etter steget de hører til. De vanligste står også i installasjonen, under «Står du fast?». Dobbeltklikket står først, som i README-en. Stegene 1–4 hører til «Med Docker Desktop» i installasjonen og er felles for begge versjonene der, og demoen står før den ekte versjonen.

## Start med dobbeltklikk

### Jeg finner ikke de fire filene.

Etter «Pakk ut alle» på Windows ligger en `G74-lund-osen-main` inne i en annen med samme navn. Åpne den innerste, der README ligger. De fire filene står øverst der: `Start demoen` og `Start den ekte versjonen`, som `.cmd` for Windows og `.command` for Mac. Står du inne i ZIP-fila, se «ZIP-fila ser ut som en vanlig mappe.» under steg 2.

### Vinduet lukkes med en gang.

Har du dobbeltklikket inne i ZIP-fila uten å pakke ut, finner ikke startfila skriptene i `start/`. Pakk ut først, og dobbeltklikk i den innerste `G74-lund-osen-main`.

### Det er to filer som heter «Start demoen».

Windows viser ofte `Start demoen.cmd` uten filendelsen og `Start demoen.command` med den. På Windows tar du den som bare heter «Start demoen». `.command` er for Mac, og på Windows spør den bare hvilket program som skal åpne den.

### Windows advarer mot fila.

Første gang kan Windows advare mot `Start demoen.cmd` eller `Start den ekte versjonen.cmd`, fordi fila er lastet ned fra nettet. Advarselen heter «Windows beskyttet PC-en». Klikk «Mer informasjon», og så «Kjør likevel». Spør Windows om du vil kjøre fila, svarer du ja. Mer står under «Slik virker dobbeltklikket» i [installasjonen](installasjon.md#slik-virker-dobbeltklikket).

### Mac sier at fila ikke kan åpnes.

Første gang kan macOS stoppe `Start demoen.command` eller `Start den ekte versjonen.command`, fordi fila er lastet ned fra nettet. Fra macOS 15 holder det ikke å høyreklikke og velge Åpne. Velg Apple-menyen > Systeminnstillinger, og Personvern og sikkerhet i sidepanelet. Under Sikkerhet klikker du «Åpne likevel» og skriver inn passordet ditt. Knappen står der i omtrent en time etter at du prøvde å åpne fila. Dobbeltklikk så fila på nytt. På macOS 14 og eldre kan du også høyreklikke fila, velge Åpne og bekrefte.

### Vinduet sier at mappa har .git.

`Start den ekte versjonen` starter ikke i en mappe med `.git`, en klon av repoet, heller ikke på main. Da stopper vinduet før noe installeres eller hentes, så et dobbeltklikk i en klon aldri henter med nøkkelen som ligger i den. Last ned en egen kopi med «Download ZIP» på GitHub, pakk den ut, og bruk din egen nøkkel fra EODHD. `Start demoen` starter også i en klon.

### Vinduet sier at den andre versjonen av OSE Signal stoppes.

Demoen eller den ekte versjonen kjørte allerede fra denne mappa, på samme port, fra et annet dobbeltklikk eller startet med `uv run waitress-serve`. Skriptet sier fra med en gang, men stopper den først rett før appen starter, så den kjører videre hvis skriptet stopper før det, for eksempel fordi `uv sync` feiler. Feiler hentingen, starter appen likevel med det som er hentet før, og da stoppes den andre versjonen. Så venter skriptet til porten er ledig, og starter den du dobbeltklikket. Det andre vinduet sier da at appen stoppet, og at det kan lukkes fordi den andre versjonen kjører.

### Vinduet sier at et annet program svarer på 127.0.0.1:8000.

Skriptet stopper aldri andre programmer, heller ikke OSE Signal fra en annen mappe, og vinduet sier hvilket program det er. Det sjekkes før uv, og igjen rett før appen starter, i tilfelle et annet program har tatt porten i mellomtiden. Er det demoen eller appen i Docker, stopper du den med `docker compose --profile demo down` i et terminalvindu i mappa med koden. Den stopper både demoen og den ekte versjonen. Er det et annet program, lukker du det. Dobbeltklikk så på nytt.

### Hvor finner jeg nøkkelen, og hvordan limer jeg den inn?

`Start den ekte versjonen` åpner registreringssiden hos EODHD første gang. Har du en konto hos EODHD fra før, logger du inn. Når du har laget kontoen eller logget inn, står nøkkelen som «API token» under «Dashboard», med kopiknappen til høyre. Lim den inn i vinduet med Ctrl+V eller et høyreklikk på Windows, og med Cmd+V på Mac, og trykk Enter. På Windows vises den som stjerner. På Mac vises ingenting mens du limer inn, men nøkkelen kommer med.

### Nøkkelen var feil.

Vinduet spør bare etter nøkkelen når den mangler i `.env`. Åpne `.env` i mappa, slett det som står etter `EODHD_API_KEY=`, og lagre. Neste dobbeltklikk på «Start den ekte versjonen» spør da på nytt.

## Steg 1: Docker Desktop

### Må jeg logge inn eller lage konto?

Nei. Hopp over innloggingen i Docker Desktop. Demoen trenger verken Docker-konto, GitHub-konto eller nøkkel. Den ekte versjonen trenger en gratis bruker hos EODHD (steg 5 i den ekte versjonen).

### Hvilken Docker Desktop skal jeg velge?

Windows: den vanlige (AMD64), med mindre maskinen har en ARM-prosessor. Mac: «Apple Silicon» hvis Apple-menyen → Om denne maskinen (About This Mac) viser en M-brikke på linja Brikke (Chip), ellers «Intel».

### Hva skjer under installasjonen?

Windows: åpne fila du lastet ned, og behold valgene som er krysset av. Spør Windows om programmet får gjøre endringer, svarer du ja. Ber Windows om omstart, gjør det. Mac: åpne fila og dra Docker til Programmer (Applications). Første gang Docker Desktop starter, godtar du vilkårene, og på Mac kan det be om passordet ditt. Docker Desktop ligger så i Start-menyen (Windows) eller i Programmer (Mac).

### Installasjonen ber om administrator.

Docker Desktop må installeres av en som er administrator på maskinen. Spør den som har ansvar for maskinen, eller bruk en annen maskin.

### Docker Desktop sier at virtualisering mangler.

Virtualisering må være slått på i maskinens oppstartsinnstillinger (BIOS eller UEFI). Hvordan, er forskjellig fra maskin til maskin. Spør den som har ansvar for maskinen, eller søk på maskinmodellen og «enable virtualization».

### Docker Desktop ber om å oppdatere WSL (Windows).

Følg beskjeden, eller lim inn `wsl --update` i PowerShell og start Docker Desktop på nytt.

### Det står ikke «Engine running» etter noen minutter.

Avslutt Docker Desktop helt: høyreklikk hvalen ved klokka (Windows) eller klikk den i menylinja øverst (Mac), og velg «Quit Docker Desktop». Åpne det igjen og vent. Hjelper ikke det, starter du maskinen på nytt.

Står det «Resource Saver mode», med en måne, er alt i orden: Docker har stoppet motoren fordi ingen containere kjører, og starter den selv når den trengs, bare litt tregere. Da trenger du ikke vente på «Engine running».

## Steg 2: koden

### ZIP-fila ser ut som en vanlig mappe.

Du må pakke ut. Står det «Komprimert størrelse» (Compressed size) som kolonne og «Pakk ut alle» (Extract All) øverst i vinduet, er du inne i ZIP-fila, og den er ikke pakket ut. Trykk «Pakk ut alle», og bruk mappa som lages. På Windows finner du Nedlastinger (Downloads) i Filutforsker (File Explorer), og etter «Pakk ut alle» trykker du «Pakk ut» (Extract).

### Det er to mapper med samme navn.

Bruk den innerste `G74-lund-osen-main`, den der filene README og compose ligger. Windows viser dem ofte uten filendelsen (.md og .yaml). På Windows har også ZIP-fila samme navn: den har en glidelås på ikonet, og den skal du ikke bruke. Har du lastet ned flere ganger, kan ZIP-fila og den ytre mappa ha fått et tall i navnet, som `G74-lund-osen-main (4)`. Bruk den nyeste ytre mappa, og den innerste i den. Vil du slette de gamle, flytter du først ut en `.env` med nøkkelen din (se «Mappa finnes fra før.»).

### Jeg finner ikke ZIP-fila på Mac.

Ligger mappa `G74-lund-osen-main` allerede i Nedlastinger (Downloads), har Safari pakket den ut for deg. Bruk den.

### Jeg har fått koden fra før.

Har du fått koden som mappe eller ZIP-fil, pakker du den ut og går til steg 3.

### Mappa finnes fra før.

Vil du laste ned på nytt, og det ligger en `.env` med nøkkelen din i den gamle mappa, flytter du den ut først. Slett så den gamle mappa og pakk ut på nytt. Demodataene ligger i Docker, ikke i mappa, så de går ikke tapt. Har du hentet koden med `git clone`, går du heller inn i mappa og skriver `git pull`.

## Steg 3: terminalvinduet

### Hvilket vindu skal jeg åpne?

Et terminalvindu, der du skriver kommandoer i stedet for å klikke. Windows: gå i Filutforsker inn i den innerste mappa `G74-lund-osen-main`, klikk i adressefeltet øverst, skriv `powershell` og trykk Enter. Da åpnes PowerShell i mappa, og du slipper `cd`, men gjør kontrollen i steg 4: `dir` skal vise `README.md` og `compose.yaml`. Du kan også trykke Start, skrive `PowerShell` og åpne «Windows PowerShell», men ikke «Kjør som administrator» (Run as administrator). Fra Start-menyen står vinduet i en annen mappe, og du går til mappa med steg 4. Ikke velg «Windows PowerShell ISE», som også står i lista. Mac: trykk Cmd+mellomrom, skriv `Terminal` og trykk Enter. Når det har gått bra, ser du et vindu med en linje som venter på at du skriver. Kommandoene er de samme i PowerShell på Windows og i Terminal på Mac og Linux.

### Ingenting skjer når jeg limer inn.

Kommandoene skrives i PowerShell eller Terminal, ikke i Docker Desktop. Docker Desktop skal bare være åpent, og du skriver ingenting i det. Ledetekst (Command Prompt) på Windows virker også for demoen, men stegene er skrevet for PowerShell, og den ekte versjonen trenger PowerShell.

Kopier kommandoen med ikonet til høyre i den grå boksen i installasjonen. Ikonet synes først når musa er over boksen. Du kan også markere kommandoen og trykke Ctrl+C (Cmd+C på Mac), eller skrive den inn. Lim den inn i PowerShell-vinduet fra steg 4 med Ctrl+V (Cmd+V på Mac), og trykk Enter.

## Steg 4: mappa

### Hva betyr cd, og hvordan ser jeg at det gikk?

`cd` betyr «gå til mappe», og kommandoene etter steg 4 virker bare fra mappa med koden. Når det har gått bra, står `G74-lund-osen-main` rett før `>` (Windows) eller `%` (Mac) på linja som venter. Det gjør det også i den ytre mappa, så sjekk med `dir` (Windows) eller `ls` (Mac): lista skal vise `README.md` og `compose.yaml`. Viser den bare en mappe som heter `G74-lund-osen-main`, står du i den ytre: skriv `cd G74-lund-osen-main`, trykk Enter og sjekk igjen.

### Står det .zip til slutt i linja.

Du har dratt inn ZIP-fila, ikke mappa. Dra mappa du pakket ut i steg 2, ikke ZIP-fila. Står det `.zip` til slutt i linja før du har trykket Enter, trykker du Esc (Windows) eller Ctrl+U (Mac), så linja blir tom, og skriver `cd` og et mellomrom på nytt. Dra så mappa inn i vinduet. På Windows har ZIP-fila en glidelås på ikonet.

### Mappa lar seg ikke dra inn i vinduet.

PowerShell er trolig åpnet som administrator, og da sperrer Windows dra og slipp. Lukk vinduet og åpne PowerShell på vanlig måte (steg 3 med Docker). Åpner du den fra adressefeltet i Filutforsker, står du alt i mappa og trenger ikke dra.

### «is not recognized as the name of a cmdlet» eller «Cannot find path … because it does not exist» etter cd.

Kommer «is not recognized as the name of a cmdlet»: Det mangler mellomrom etter `cd`. Står `cd` klistret til stien i meldingen, for eksempel `'cdC:\...'`, skriver du `cd`, et mellomrom, og drar mappa inn i vinduet på nytt (steg 4 med Docker). Står det `'docker'` i meldingen, er Docker Desktop ikke installert, eller vinduet ble åpnet før installasjonen: lukk det og åpne et nytt (steg 3 med Docker). Står det `'uv'` i meldingen, er uv ikke installert, eller vinduet ble åpnet før installasjonen: se «Tester» i README-en.

Kommer «Cannot find path … because it does not exist»: Mappa ligger ikke der stien sier, for eksempel fordi den er flyttet, eller fordi ZIP-fila ble dratt inn i stedet for mappa. Skriv `cd` og et mellomrom, og dra mappa inn i vinduet på nytt (steg 4 med Docker). Står det `.zip` til slutt i stien i meldingen, var det ZIP-fila: se «Står det .zip til slutt i linja.» over.

### Stien har mellomrom og fikk ikke anførselstegn.

Får du en feil etter `cd` når mappa ligger i en mappe med mellomrom i navnet, skriver du anførselstegn rundt stien, for eksempel `cd "C:\Users\Ola Nordmann\Downloads\G74-lund-osen-main"`. På Mac setter Terminal `\` foran hvert mellomrom, og det virker også.

### Terminal spør om tilgang til Nedlastinger (Mac).

Svar OK. Ellers får ikke Terminal åpne mappa.

## Demoen

### Hva skal jeg se etter i vinduet?

Første gang bygger Docker appen, og det kommer mange linjer. Demoen er klar når denne linja kommer. Den skal du ikke kopiere, bare se etter:

```text
demo-1  | INFO:waitress:Serving on http://0.0.0.0:8000
```

Under den kan det komme en linje med valg fra Docker. La terminalvinduet stå åpent mens du bruker demoen. `0.0.0.0` er adressen inne i Docker, og du åpner http://127.0.0.1:8000 i steg 6 i demoen. «Serving on http://0.0.0.0:8000» betyr bare at appen kjører.

### Hva er demoen?

Sidene sier «Eksempeltall»: 15 oppdiktede selskaper med kurser til fredag 9. oktober 2026, ikke data fra Oslo Børs. Under merket står en tabell med aksjer, og du klikker på et selskapsnavn for å se aksjen. Hver aksje har en rad. Matfjord Merkevarer har ingen kurser i demoen, med vilje, og står nederst med «–» og «uten data» når tabellen ikke er sortert. Varde Systemer er nylig notert, så raden sier hvor mange dager kursserien har og hvor mange signalet trenger. Klikker du på et kolonnenavn, sorteres alle aksjene i én liste på den kolonnen, og «Standard rekkefølge» gir delene «Skilte seg ut» og «Øvrige aksjer» tilbake. Demoen trenger verken `.env` eller nøkkel, og gjør ingen kall. Aksjesiden viser KI-teksten for siste dag, laget én gang med Gemma og lagret i repoet, så demoen trenger ikke Ollama. For en tidligere dag sier siden at demoen har KI-tekst bare for siste børsdag. KI-teksten står i rammen «Signalet forklart» etter kursgrafen, og bryteren «KI-tekst» øverst til høyre i rammen slår den av og på. Med KI av står rammen med appens setninger og bryteren. Tallene i teksten har prikket strek. Demobasen lages på nytt hver gang demoen starter, i sitt eget volum, `ose-demo`. Den ekte basen røres ikke. Mens demoen kjører, kan demobasen også lages på nytt med `docker compose run --rm demo-lag` i et nytt terminalvindu, fra samme mappe.

Øverst på sidene står knappene «Markedsoversikt» med en tabell, «Børsometer» med en måler og «Min liste» med en stjerne, og knappen for siden du står på, er fylt. På aksjesiden har «Markedsoversikt» en hvit kant uten fyll, fordi aksjesiden hører til oversikten. Stjernen foran et selskap legger aksjen i Min liste, og et nytt trykk tar den ut. Siden står etterpå ved raden, eller ved tabellen når aksjen ble tatt ut av Min liste og raden er borte. Over tabellen på oversikten står «Aksjene» med antallet, og valget «Alle» og «Min liste». I Min liste sier tittelen hvor mange av de merkede som skilte seg ut siste børsdag, for eksempel «3 av 5 i Min liste skilte seg ut fredag», og valget står til høyre for tittelen. Demoen starter med fem merket, og siden demobasen lages på nytt hver gang demoen starter, er det de samme fem neste gang. I den ekte versjonen starter lista tom, og merkingen blir liggende til du tar den bort.

Har du laget demobasen utenfor Docker før 22.10, sier sidene «Demobasen er laget av en eldre versjon av demoen». Lag den på nytt med `uv run python src/demo.py`. I Docker lages den på nytt hver gang demoen starter.

### Hva viser børsometeret?

Én rute per aksje, samlet etter bransje. Fargen har fem trinn etter endringen fra børsdagen før, eller i perioden du velger, slik tallet står i ruta: grå under ±0,5 %, lys grønn eller lys rød fra 0,5 % til under 2 %, og sterk grønn eller rød med hvit tekst fra 2 %. En rute uten endring er hvit med grå kant. Øverst står to kort, side om side i et bredt vindu og under hverandre på smal skjerm. «Mål mot børsen» har endringen i hovedindeksen den dagen eller for perioden, eller «–» når indeksen ikke har den, hvor mange av aksjene med en endring som gikk bedre enn indeksen, slik tallene vises, uten aksjer med en kortere kursserie i perioden, og hva fargen og størrelsen måler. «Slik leser du børsometeret» viser fargene med grensene, rammene, størrelsen og hva et klikk på ruta gjør. Rutene er et fylt kart: hver bransje er et felt, og for én dag følger arealet av ruta volumet mot medianen for de 20 børsdagene før, men ruta blir ikke større over tre ganger vanlig volum eller mindre under halvparten, og tabellen under har det faktiske tallet. Med Tab går du gjennom kartet fra det største feltet og den største ruta, slik kartet legger dem, mens tabellen har bransjene i fast rekkefølge. Symbolet og endringen står på ruter som er store nok, og i et bredt vindu får flere ruter plass til teksten. I et vindu fra 1079 px har de største rutene symbolet og styrken øverst, selskapsnavnet under, kuttet med «…» når det er for langt, og endringen i stor skrift nederst, med merket og grunnen mellom der de får plass. En stor rute med gul ramme en annen dag har merket «3 av 3 siste børsdag» og styrken i stedet for navnet når merket ikke får plass under navnet. Mindre ruter har teksten som før. Rammen er tykk med en hvit linje innenfor, gul ved 3 av 3 på siste børsdag, også når du velger en annen dag, og mørk ved 2 av 3 bare på siste børsdag. Styrken står i rutene som har plass, som i tabellen på oversikten: «3 av 3» og «2 av 3» i ring for siste børsdag, like store i alle rutene og aldri utenfor ruta, og ellers som tekst. En annen dag står styrken i en rute med gul ramme bare der merket «3 av 3 siste børsdag» også får plass. En rute med kurs, men uten styrke, sier «ikke vurdert» der styrken ellers står, når ruta har plass, med grunnen under når hele grunnen får plass. Viser en rute «ikke vurdert» av en annen grunn enn at signalet ikke er lagret, som for kort kurshistorikk, sier en fotnote under kartet at grunnen står i tabellen og på aksjesiden. Hver bransje har en tynn ramme. Øverst i feltet står symbolet og navnet, og under dem antallet aksjer og snittet av endringen for aksjene i bransjen som har kurs, for eksempel «3 aksjer · snitt -1,92 %», eller «1 aksje». Den linja står alltid, fordi hvert felt er bredt nok til den, og blir navnet for langt, kuttes det med «…». Over rutene står de samme knappene som i oversikten. Ved 1 uke, 1 mnd, 3 mnd, 6 mnd, I år og 1 år er fargen og snittet endringen fra den første kursen i perioden til siste børsdag, og rutene er like store, fordi volumet mot vanlig gjelder én dag; rammen er fortsatt signalet siste børsdag. Med datoen og «Vis dagen» ser du en tidligere dag. Gult står da fortsatt ved 3 av 3 på siste børsdag, også en dag uten vurdering, og mørk ramme står bare for siste børsdag. En dag uten vurdering står som «ikke vurdert», og da står fotnoten om «ikke vurdert» under tabellen. Klikk på en rute for å se aksjen den dagen. For en aksje uten kurser sier aksjesiden at det ikke finnes kurser ennå. Under rutene står de samme tallene i en tabell, bak «Se tallene som tabell». Den er lukket til du åpner den, og er som tabellen på oversikten: kolonneraden i svart, et bånd for hver bransje i fast rekkefølge med symbolet, antallet og snittet, en oransje strek ved 3 av 3 siste børsdag og styrken i ring på siste børsdag. Søylene står bare på oversikten. Det gjelder både demoen og den ekte versjonen.

### Hva gjør knappene over hovedindeksen?

Knappene velger hva oversikten viser. Den første heter etter siste børsdag, for eksempel «Fredag», og er valgt når siden åpnes. 1 uke, 1 mnd, 3 mnd, 6 mnd, I år og 1 år viser endringen fra den første kursen i perioden til siste børsdag, regnet på kursen justert for utbytte, med samme regel for når perioden begynner som kursgrafen: perioden starter på første børsdag fra samme dato bakover etter kalenderen, og I år på årets første børsdag. Linja over tabellen sier dagen den første kursen er fra. Sluttkursen og signalet gjelder fortsatt siste børsdag. Begynner kursserien til en aksje senere, står «fra» og datoen under tallet. Datoen står etter knappene. Feltet viser siste børsdag ved den første knappen og dagen du har valgt, og er tomt ved en periode. Velg en dag i feltet og trykk «Vis dagen», så viser oversikten sluttkursen, endringen den dagen og signalet som er lagret for dagen, eller «– ikke vurdert», grunnen eller «– ikke børsdag». Pilene på hver side av datoen går til forrige og neste børsdag, og står bare når feltet viser en dag; ved første og siste dag er pila grå. Signalet regnes aldri på nytt. Aksjene som fikk 3 av 3 siste børsdag, har oransje strek og teksten «3 av 3 siste børsdag», og 2 av 3 merkes bare for siste børsdag. Søylene under hovedindeksen og den stiplede linja følger samme periode eller dag, og samme siste børsdag som tabellen. Det gjør også tallet for hovedindeksen over søylene, med endringen og «gikk bedre», som alltid er endringen den dagen, også ved en periode. Med en dag du har valgt, gjelder alt den dagen. Mangler indeksen kurs den dagen, står det der tallet ellers står og over søylene, og da er det ingen stiplet linje. En søyle er mørk fra 2 % opp eller ned, som i børsometeret, og lys under. Under søylene står hva lys og mørk betyr, og «Stiplet linje: hovedindeksen» med endringen, og til høyre for den lenken «Se dagen i Børsometer ›» når oversikten viser én dag, og «Se perioden i Børsometer ›» ved en periode, som åpner børsometeret med samme dag eller periode, og hovedindeksen og søylene har hvert sitt «?». I et bredt vindu står tickeren over søylene vannrett, og på smal skjerm på høykant. Perioden og dagen står i adressen, også når du sorterer. En aksje som mangler kurs for siste børsdag, viser sin egen siste dag, med «siste kurs» og datoen under navnet. I Min liste heter knappene «Sammenlign siste børsdag med»: øverst i hver rad står fortsatt siste børsdag, og med en periode eller en dag står en linje under med datoen, sluttkursen den dagen, endringen derfra til siste børsdag og signalet som er lagret for dagen. Børsometeret har de samme knappene. Kursgrafen på aksjesiden har de også, og der velger knappene hvor langt tilbake grafen går. Den første viser 6 måneder fram til siste børsdag, og dagen grafen viser, er en strek med datoen i en svart lapp øverst. Holder du musa over grafen, står datoen, kursen og snittet for dagen i en lapp ved musa. Den stiplede linja er hovedindeksen, og den sier ikke noe om hva aksjen gjør videre. Med datoen og «Vis dagen» viser hele aksjesiden dagen du velger, med signalet som er lagret for den, og det regnes aldri på nytt. Det gjelder både demoen og den ekte versjonen.

### Hva sa appen om en aksje tidligere?

Nederst på aksjesiden står «Signalet dag for dag»: det appen skrev om aksjen hver børsdag, en måned om gangen, med retningen, T, B, I og styrken. Hver uke er en rad, fra mandag til fredag, og summen for uka står til høyre. Pilene på hver side av måneden viser måneden før og etter, så langt kursserien går. Klikk på en dag med kurs for å se hele siden for den dagen, med målingene, eller velg dagen med datoen over kursgrafen. En dag uten vurdering står med «–» og grunnen, og dagene før første og etter siste kurs står tomme. Det gjelder både demoen og den ekte versjonen. Den ekte versjonen har signal fra første henting, og dagene før står som «ikke vurdert». Demoen viser det samme: vurderingene starter mandag 21. september 2026, tre uker før siste demodag, og dagene før står som «ikke vurdert».

### Hva er prikkene på kurslinja?

Prikkene på kurslinja i kursgrafen på aksjesiden viser dagene aksjen skilte seg ut, med signalstyrke 2 eller mer, som i oversikten. Fargen og formen er retningen den dagen: en grønn rund prikk for positiv, en rød firkant for negativ og en lilla rute for blandet, og en gul ring betyr 3 av 3. Under grafen står hvor mange slike dager grafen har. Prikkene er det appen lagret den kvelden, ikke regnet på nytt av kursene. En dag uten signal, med en grunn eller som ikke er børsdag, har ingen prikk, og heller ikke en dag med styrke 0 eller 1. Under grafen står datoen den første raden for aksjen ble lagret, med signal eller med en grunn, og før den er det ingen prikker. I demoen begynner de mandag 21. september 2026.

### Hva er «Signalet forklart» på aksjesiden?

Under grafen står rammen «Signalet forklart». Først skriver appen selv, også når KI-teksten er av, hvor lenge signalet har vært slik, med datoen for den første dagen i rekka, og hva hovedindeksen, bransjen og antallet aksjer i lista som steg og falt gjorde samme dag. Mangler børsdagen før rekka i basen, står «minst siden» den første dagen som er lagret, fordi dagen signalet skiftet ikke er kjent. Bransjen står bare når minst to aksjer i bransjen har en endring den dagen, og den regnes som snittet i børsometeret, av de aksjene. De to setningene er ikke laget av KI, og de sier ikke at dagen forklarer signalet.

Med KI-teksten på kommer en tekst om signalet for aksjen den dagen, skrevet av en språkmodell og merket «Laget av KI» med navnet på modellen. Teksten har én setning for hver sjekk, som sier med vanlige ord hva sjekken måler og hva den ga, og en setning eller to om tre mønstre appen har regnet ut av signalene og kursene som er lagret: hvor mange av de siste 20 børsdagene signalet var positivt, negativt, blandet og uten retning, hvor mange av de siste 5 børsdagene aksjen gikk samme vei som hovedindeksen, og hvor mange ganger retningen skiftet den siste måneden. En dag uten vurdering telles ikke. Med færre enn 10 vurderte dager av de 20, eller færre enn 3 av de 5 dagene som kunne telles, står ikke mønsteret, og mangler noen dager i måneden, står «minst» foran antallet skift. Mønstrene sier bare hva som har skjedd, ikke hva som vil skje.

Modellen fikk bare det appen har regnet ut: om hver av sjekkene ga +1, 0 eller -1, styrken og retningen, antallene i mønstrene, om aksjen selv steg, falt eller var uendret den dagen når det kan regnes, regnet mot forrige kurs, som endringen i tabellen, og når aksjens forrige kurs er fra forrige børsdag, også om hovedindeksen steg, falt eller var uendret, med en ferdig setning om aksjen gikk samme vei som hovedindeksen eller motsatt, og et merke når aksjen er utenfor de 15 grensene er målt på, men ingen kurser, prosenter eller volumer. Tallene med prikket strek er sjekket mot det før teksten vises, og teksten som vises, gir ikke råd, finner ikke mønstre selv og sier ikke noe annet om hovedindeksen, bransjen, børsen eller antallet aksjer enn den ferdige setningen og mønstrene. «?» ved overskriften sier det kort. Det gjelder både demoen og den ekte versjonen.

### Hva er «Børsdagen kort fortalt» på forsiden?

Under tabellen på oversikten står «Børsdagen kort fortalt»: noen setninger om hele børsdagen, skrevet av en språkmodell da kursene ble hentet, merket «Laget av KI» og med navnet på modellen under teksten. Modellen fikk bare antall: om hovedindeksen steg eller falt, hvor mange aksjer som gjorde det bedre enn indeksen, hvor mange som skilte seg ut og med hvilken retning, og hvor mange som steg i hver bransje med minst to aksjer med en endring, med ukedagen og antallet aksjer i lista, og ingen prosenter, kurser eller nyheter. Teksten sjekkes før den vises: tallene står med sifre og prikket strek og står i det modellen fikk, og teksten gir ikke råd og gjetter ikke på årsaker. Den kan bare ha setningene i de faste formene appen gir modellen, så den sier ingenting annet om dagen. Den vises bare når det modellen fikk, er det samme som siden viser. Ellers står «Dagen er uten KI-tekst.» Teksten lages først når alle aksjene i lista har en rad for dagen, og under den står modellen og tjenesten, for eksempel «gemma4:e4b (lokal)». Teksten skrives for én børsdag om gangen, så i en periode står «Perioden er uten KI-tekst.», og med en valgt dag står teksten for den dagen når den finnes. Bryteren «Vis KI-tekst» er den samme som på aksjesiden og slår av begge KI-tekstene. Min liste har ikke delen. I demoen er teksten laget én gang med Gemma, for siste børsdag.

### Hvordan ble grensene valgt?

Signalet har tre sjekker, hver på sin del av dataene: kursnivå, endring og volum, med én regel og én grense hver, så du ser hva som ga utslaget. Sjekkene er valgt for å kunne forklares, ikke for å treffe markedet. Signalet trenger 51 børsdager med kurser, og har aksjen færre, kan det ikke regnes. Grensene 2 %, 1,5 ganger, de to vinduene på 20 børsdager og terskelen 2 ble kontrollert mot 15 aksjer på Oslo Børs over 199 børsdager, fra desember 2025 til september 2026, før de ble låst. Det var en kontroll av at de holder, ikke et søk etter verdiene som gir penest resultat.

Retningen er oftere positiv når kursene stiger. Trend er en tilstand som kan vare i uker, mens bevegelse og interesse er hendelser som sjelden slår ut, så retningen blir oftest trendens. I målingen over 199 børsdager var 60,0 % av aksjedagene med utslag positive og 29,5 % negative. Det beskriver perioden, ikke det som kommer. Vinduet ved «Retning» på aksjesiden sier det i én setning. Det gjelder både demoen og den ekte versjonen.

### Hvorfor står det «ikke vurdert»?

Står «ikke vurdert» på oversikten, aksjesiden eller børsometeret, sier en fotnote hvorfor. Retningen står da som «– Ukjent», som ikke er en femte retning: «– Ingen» betyr at sjekkene ble regnet uten at noen slo ut. I børsometeret kan «ikke vurdert» i en rute også ha en annen grunn, som for kort kurshistorikk. Når en slik rute viser «ikke vurdert», sier en egen fotnote under kartet at grunnen står i tabellen og på aksjesiden, og har kartet begge slags ruter, står begge fotnotene. I den ekte versjonen lagres signalet bare den kvelden kursene hentes, og regnes aldri ut bakover. Det gjelder dagene før første henting, kvelder uten henting, og dager der kursene er lest inn med `--les-inn`. Er dagen siste børsdag, også når siden leses i helga eller på en helligdag, sier fotnoten i tillegg at signalet for den dagen fortsatt kan lagres hvis hentingen kjøres ferdig før neste børsdag. I demoen sier fotnoten for en dag før 21.09 at vurderingene starter mandag 21.09, slik den ekte versjonen har signal fra første henting. En dag fra 21.09 uten vurdering får den ekte teksten, også i demoen.

### Hva betyr «ikke i lista»?

Appen henter og vurderer bare aksjene som er i lista. Lista står i basen, med datoen hver aksje kom inn og gikk ut. En aksje som er tatt ut, står ikke lenger i oversikten, Min liste eller børsometeret, men aksjesiden viser den fortsatt, med kursene og signalet som er lagret. For en børsdag etter at aksjen gikk ut står «ikke i lista», ikke «ikke vurdert», fordi appen ikke skulle vurdere den den dagen. Det som alt er lagret, slettes aldri.

## Den ekte versjonen

### Hva med nøkkelen?

Du trenger en egen gratis API-nøkkel fra [EODHD](https://eodhd.com/register), fordi vilkårene ikke lar oss dele vår. Den gir 20 kall i døgnet, og en henting bruker 16: ett per aksje og ett for hovedindeksen. Åpne `.env` i en teksteditor (`notepad .env` på Windows, `open -e .env` på macOS, `nano .env` på Linux) og lim den inn etter `EODHD_API_KEY=`. `cp` skriver over en `.env` som finnes, så kopier bare første gang. Webserveren starter uten `.env`, henter aldri og bruker aldri kvote. Den skriver bare én ting i basen, merkingen i Min liste, når du trykker på stjernen. Bare hentingen trenger nøkkelen, og `docker compose run --rm hent` starter ikke uten `.env`.

### Hvorfor bare 15 aksjer?

Kursene kommer fra EODHD, og den gratis nøkkelen gir 20 kall i døgnet. Hver aksje koster ett kall, og hovedindeksen ett til, så med 15 aksjer er det kall til overs hvis noe må hentes på nytt. Planen er at du senere kan velge opptil 18 aksjer selv.

### Når kan jeg hente?

Hent etter kl. 22 og før midnatt på en børsdag. Første gang, når basen er tom, kan du også hente på dagtid og i helgen: da henter den siste fullførte børsdag, før kl. 22 en børsdag altså forrige børsdag, og aldri dagens kurs. Signalet lagres fra første henting og regnes aldri bakover, så «Signalet dag for dag» fylles én børsdag om gangen. Første henting på dagtid bruker normalt 16 av dagens 20 kall, så det er ingen kall igjen til nye forsøk samme kveld, og den bruker aldri bonuskvoten. Kveldens henting samme dag trenger 16 til: har kontoen minst 12 i bonuskvoten, tas de derfra, og dagen får signal. Ellers bruker den 0 kall, og den dagen får aldri signal, fordi en vurdering bare kan skrives for inneværende børsdag. Neste kveld hentes neste børsdag. Før kl. 22 en børsdag stopper hentingen med 0 kall og sier hvorfor når basen ikke er tom: dagens sluttkurs er ikke klar ennå, og en vurdering kan ikke fylles inn senere. Har basen alt kursene for børsdagen, bruker den også 0 kall. På en dag børsen er stengt henter den bare hvis basen mangler forrige børsdag. Mangler noen aksjer dagens kurs etter hentingen, sier den hvilke. Kjør samme kommando igjen senere samme kveld, så prøver den bare dem, med kallene som er til overs etter hentingen (20 minus ett per aksje og ett for hovedindeksen, altså 4 med de 15), aldri bonuskvoten og ikke etter kl. 23:50. Hovedindeksen prøves ikke på nytt samme kveld. Før kallene leser den kvoten med `/api/user`, som er gratis.

### Kan hentingen gå av seg selv hver kveld?

Ja, på Windows, med en jobb i Oppgaveplanlegging. Den går hver dag kl. 22:15, og igjen kl. 22:45, 23:15 og 23:45, fra en egen arbeidskopi på commiten main hadde ved midnatt, og henter uten KI-tekst hvis Docker Desktop eller Ollama ikke svarer. Er børsdagen alt ferdig, med kursene og vurderingene for aksjene i lista, hovedindeksen og KI-tekstene, startes verken Docker Desktop eller Ollama, og hentingen og målingen går som før, uten KI-tekst. Mangler noe, eller feiler sjekken, går kjøringen som før. Loggen står i `data/logg/kveldshenting-<dato>.log`. Slik slås den på og av, med `start\legg-inn-kveldshentingen.ps1` og `start\ta-bort-kveldshentingen.ps1`: [Hentingen hver kveld](installasjon.md#hentingen-hver-kveld) i installasjonen. Slå den av før du henter for hånd samme kveld, eller vent til den er ferdig, så to hentinger ikke går samtidig. Etter hentingen måler jobben omsetningen for de neste aksjene i lista over Oslo Børs med `--maal-omsetning`, med kallene som er igjen av dagens, også i helgene. Den bruker aldri bonuskvoten og venter til hentingen har kursene for alle aksjene. Startes den kl. 23:45 eller senere, som i jobbens siste kjøring, går den likevel, med kallene som er igjen, og sier hvor mange av aksjene i lista som mangler kursen.

### Oversikten er tom.

Uten henting starter appen med tom oversikt og viser kommandoen som henter. Hent kursene med steg 8 i den ekte versjonen, og last siden på nytt. Utskriften fra hentingen sier hvilken børsdag vurderingene gjelder, og hvilke aksjer som fikk en grunn i stedet for en vurdering.

### Hvor ligger dataene?

Dataene ligger i to Docker-volumer: `ose-db` med basen og `ose-raa` med øyeblikksbildene fra EODHD. De står når containerne stoppes. **Bruk aldri `docker compose down -v`.** `-v` fjerner begge volumene, og verken øyeblikksbildene eller vurderingene kan hentes på nytt. Basen kan heller ikke slettes og bygges opp igjen: kursene kan hentes på nytt, men vurderingene for dagene som har gått, kan ikke lages på nytt.

### Kan appen nås fra nettet?

Nei. Porten er bare åpen på maskinen selv (127.0.0.1). Appen kan ikke nås fra nettet.

### Hvor finner jeg børsmeldingene?

Appen viser ikke børsmeldingene. De står på NewsWeb og ofte også på selskapets investorside. Nederst på aksjesiden står boblen «Investorsiden til ‹navn›». I den ekte versjonen åpner den selskapets egen investorside i en ny fane, og appen henter ingenting derfra. Har appen ingen adresse til selskapet, står det ingen boble. I demoen er selskapene oppdiktet, så boblen går til en side i appen, i samme fane, med logoen og en tegning laget av KI. Lenken øverst på den siden tar deg tilbake til aksjen.

### Kan KI-teksten lages uten grafikkort?

Ja, med din egen nøkkel til Gemini, Anthropic eller OpenAI. Sett `OSE_KI_TJENESTE=gemini`, `anthropic` eller `openai` i `.env`, og lim inn nøkkelen etter `OSE_KI_GEMINI_NOKKEL=`, `OSE_KI_ANTHROPIC_NOKKEL=` eller `OSE_KI_OPENAI_NOKKEL=`. Da sendes grunnlaget for hver aksje til tjenesten du har valgt, og det kan koste hos dem. Del aldri nøkkelen, og bruk ikke en konto der du har sagt ja til at tjenesten trener på innholdet. Mangler nøkkelen, eller har den tegn som ikke kan sendes, skrives ingen rader, og utskriften sier hvilken variabel det gjelder: legg den inn og hent igjen samme kveld, før midnatt. Feiler tjenesten, for eksempel fordi nøkkelen er feil, blir det ingen KI-tekst for noen av aksjene den dagen, heller ikke om du retter det og henter igjen samme kveld. Hentingen går ikke over til en annen tjeneste. Mer står under «Egen nøkkel til Gemini, Anthropic eller OpenAI» i [installasjonen](installasjon.md).

## Når appen kjører, eller ikke

### Siden åpnes ikke.

Vent til linja med «Serving on» har kommet, og sjekk at terminalvinduet fortsatt er åpent. Adressen er http://127.0.0.1:8000, ikke 0.0.0.0.

### Nettleseren sier at 127.0.0.1 nektet å koble til.

Nettleseren viser da `ERR_CONNECTION_REFUSED`. Andre nettlesere sier det med andre ord. Ingenting svarer på adressen ennå. Appen er ikke klar, eller den er stoppet. Se i terminalvinduet: vent til linja med «Serving on» har kommet, og sjekk at vinduet fortsatt er åpent og at Docker Desktop kjører. Last så siden på nytt. Adressen er http://127.0.0.1:8000, ikke 0.0.0.0.

### «The term 'uv' is not recognized» eller «command not found: uv».

Blir `uv` ikke funnet etter installasjonen, lukker du vinduet, åpner et nytt og går til mappa, som i steg 4 med Docker. Er uv ikke installert, står installasjonen for Windows og Mac under «Tester» i [README-en](../README.md#tester).

### «docker» er ikke gjenkjent, eller «command not found: docker».

Docker Desktop er ikke installert, eller terminalvinduet ble åpnet før installasjonen. Lukk terminalvinduet og åpne et nytt (steg 3 med Docker).

### «Cannot connect to the Docker daemon», «error during connect» eller «dockerDesktopLinuxEngine».

Docker Desktop er ikke startet, eller motoren er ikke klar. Start Docker Desktop, vent til det står «Engine running» (steg 1 med Docker), og prøv kommandoen igjen.

### To kommandoer havnet på samme linje.

For eksempel med feilen «no such service». Lim inn én kommando om gangen, og trykk Enter etter hver. Står det noe på linja fra før, sletter du det først.

### «no configuration file provided: not found».

Terminalvinduet står i feil mappe. Gjør steg 4 med Docker på nytt, og dra den mappa der fila compose ligger. Windows viser den uten filendelsen, som compose og ikke compose.yaml.

### «toomanyrequests» fra Docker Hub.

Docker Hub begrenser hvor ofte samme IP-adresse kan laste ned uten innlogging. Prøv igjen senere, eller fra et annet nett. Innlogging i Docker Desktop hever grensen, men trengs ellers ikke.

### «port is already allocated», «address already in use» eller «ports are not available».

Noe annet bruker port 8000. Kjører den andre versjonen, stopper du den først (se «Bytte mellom demoen og den ekte versjonen» under «Mer for den som vil»). «Mer for den som vil» står i [installasjonen](installasjon.md).

## Stopp

### Jeg lukket vinduet før jeg stoppet.

Åpne et nytt terminalvindu, gjør steg 4 med Docker og lim inn stoppkommandoen for versjonen du kjørte: `docker compose down` for den ekte versjonen, eller `docker compose --profile demo down` for demoen.

## Neste gang

### Hvordan starter jeg neste gang?

Med dobbeltklikket: dobbeltklikk «Start demoen» eller «Start den ekte versjonen» i mappa igjen. Den ekte versjonen henter det som mangler før appen starter.

Med Docker: start Docker Desktop fra Start-menyen (Windows) eller Programmer (Mac), og vent til det står «Engine running». Gjør så steg 3 og 4, og hopp over steg 2. Start så appen med steg 7 i den ekte versjonen, og hent kursene med steg 8 om kvelden, eller start demoen med steg 5 i demoen. Det går raskere enn første gang. Etter «Stopp» kan du lukke terminalvinduet og Docker Desktop.
