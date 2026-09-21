# Begrunnelser — hvorfor kravene i PRD-en ser slik ut

`prd.md` er et kravregister: hva løsningen skal gjøre. Dette dokumentet bærer
resonnementet: hvorfor grensene går der de går, hvilke alternativer som ble
forkastet, og hva som ville gått galt med det opplagte valget.

Skillet er det samme som mellom PRD-en og `malinger.md`. Et kravregister og et
begrunnelsesdokument er to forskjellige lesninger, og de leses best hver for seg.

Målinger med metode og rådata: `malinger.md`.

---

## 1. Hvorfor KI-laget finnes: metadata skiller ikke betydning

Dette er den bærende begrunnelsen for hele KI-laget, og den eneste påstanden i
prosjektet som er målt tre ganger uavhengig.

Påstanden om at regler alene ikke strekker til, er ikke lenger en påstand. Den
er målt tre ganger, uavhengig av hverandre — ulike kilder, ulike metadatafelt,
ulike uker — og målingene peker samme vei.

**1. Symbolkoblingen i medier (egen test, 2026-09-17).** Vi leste manuelt de ti
siste nyhetstreffene for et utvalg selskaper. For et stort finansselskap handlet
flertallet av treffene i realiteten om andre selskaper; symbolet var bare ett av
mange i artikkelen.

For et shippingselskap var bildet motsatt: treffene handlet i hovedsak om
selskapet selv eller om markedet det opererer i. *At en artikkel er knyttet til
et symbol, betyr ikke at den handler om selskapet — og hvor ofte det slår feil,
varierer med selskapet.*

Motprøven er ikke et sidepoeng. Den styrer hvordan testsettet på 50
medieartikler må settes sammen: et testsett fra bare én selskapstype vil måle
feil.

**2. Samlekategorien i NewsWeb (måling 2026-09-20).** Kategorien
`IKKE-INFORMASJONSPLIKTIGE PRESSEMELDINGER` inneholdt over fire uker både
«Aker BP has started production from the Skarv Satellites» og «Invitation to
Hydro's Investor Day, London». *Samme kategorifelt, uforenlig betydning.*

**3. Tilbakekjøpskategorien (måling 2026-09-20).** Kategorien
`UTSTEDERS MELDEPLIKT VED HANDEL I EGNE AKSJER` inneholdt både SalMars
«Oppstart for tilbakekjøpsprogram for aksjer» — en reell hendelse — og DNBs
«status for tilbakekjøpsprogram etter uke 34 2026», en rutinerapport.
*Samme felt igjen, samme problem.*

Tre uavhengige målinger av det samme: **metadata skiller ikke betydning.**

Regler kan sortere på det metadata faktisk bærer — hvem som er utsteder, hvilken
kategori meldingen har — og det gjør de godt nok til at grovsorteringen hører
hjemme i kode. Men der to meldinger deler felt og likevel betyr helt ulike ting,
har regelen ingenting igjen å sortere på. Da er språkforståelse det eneste som
skiller.

*Denne begrunnelsen hører også hjemme i refleksjonsrapporten. Den er sterkere
enn den opprinnelige formuleringen i Product Brief, fordi den hviler på tre
målinger fra ulike vinkler i stedet for ett eksempel.*

---

## 2. Aksjeuniverset

### Hvorfor vi tåler spennet fra 920 til 32 MNOK

32 MNOK omsetning per dag er rikelig likvid for en privat sparer. Poenget er at
brukeren skal kunne handle aksjen, ikke at den skal tåle institusjonell
ordreflyt. Et univers som bare inneholder de aller største, speiler ikke
porteføljen til målgruppen, og ville gjort løsningen mindre nyttig for dem den
er laget for.

### Hvorfor omsetning i kroner, ikke antall aksjer

Målingen avdekket at det opplagte målet var feil mål. DNO omsetter 1 956 182
aksjer per dag — flere enn DNB — men til 19,62 kroner blir det 34,7 MNOK mot
DNBs 400,4 MNOK. MPCC viser samme mønster. Målt på antall aksjer alene ville
begge de lavest omsatte symbolene sett ut som de hørte hjemme øverst på lista.

### Hvorfor median og ikke gjennomsnitt

Enkeltdager med ekstrem omsetning ville ellers løftet et symbol som til vanlig
omsettes tynt.

### Hvorfor minst åtte sektorer

Kravet sikrer at markedsoversikten ikke blir en energiliste med noen få innslag
fra andre sektorer.

---

## 3. Datahenting

### Hvorfor FR-402 ikke stoler på klokkeslett

Tidspunktet er ikke garantert. EODHD dokumenterer bare en generell regel —
børser oppdateres «2–3 timer etter stengetid» — og oppgir ingenting som gjelder
Oslo Børs spesifikt. Oslo Børs stenger 16:20 lokal tid, noe som gir omtrent
19:20 som tidligste forventede publisering, men det tallet er utledet av oss,
ikke dokumentert av kilden.

Derfor kontrolleres innholdet, ikke klokka.

### Hvorfor beregningsgrunnlaget lastes ned på nytt (FR-406)

`adjusted_close` er ikke en stabil verdi. EODHD regner hele historikken om
bakover hver gang et nytt utbytte kommer, og dokumentasjonen sier eksplisitt at
serien skal lastes ned på nytt fremfor at nye rader limes bakpå en lagret serie.

Siden et kall koster det samme uansett intervall, er det å laste ned på nytt
gratis for oss. Det er derfor kravet ikke koster noe å oppfylle.

### Hvorfor rådata bevares (NFR-07)

NewsWeb-API-et er udokumentert backend for Oslo Børs' egen nettside og kan endres
uten varsel. Øyeblikksbildene sikrer at prosjektet ikke står tomhendt om en kilde
forsvinner, og gjør målingene våre etterprøvbare i etterkant.

### Hvorfor `data.overflow` måtte oppdages (FR-405)

Taket var ikke dokumentert noe sted. Et forespurt intervall på 19 dager ga 7
dager tilbake, med HTTP 200 og uten feilmelding — svaret så vellykket ut.
Åtte vanlige parametre for paginering og grense ble testet uten effekt.

Feltet `data.overflow` ble funnet ved å se på svarets struktur fremfor på
meldingene i det. Det er udokumentert, som resten av API-et, men verifisert i
begge retninger. Fordi det er udokumentert, har kravet en fallback-sjekk i
tillegg.

---

## 4. Meldingsfilteret

### Hvorfor hver kategori havnet i sin bøtte

**Flagging slipper gjennom** fordi den er signalet om at en storaksjonær har
kjøpt eller solgt seg opp eller ned. Det er nettopp den «hvorfor falt den»-typen
forklaring løsningen ellers mister ved ikke å bruke mediekilder.

**Meldepliktig handel for primærinnsidere slipper gjennom** fordi 10 meldinger
på 28 dager er neglisjerbart i kostnad, og fordi det er en av få meldingstyper
private sparere faktisk følger.

**Utsteders meldeplikt ved handel i egne aksjer filtreres bort** fordi de 35
meldingene kommer fra bare seks selskaper, som ukentlige statusrapporter med
samme ordlyd hver gang.

### Hvorfor dedupliseringen kjøres først (FR-501)

Kjøres kategorifilteret først, filtreres dubletter hver for seg, og statistikken
over hva som passerte blir feil. Dessuten ville KI-laget betalt for å forklare
den samme saken to ganger, og brukeren sett hver sak dobbelt.

### Hvorfor den norske beholdes

Grensesnittet er norsk, og KI-forklaringen skal gis på norsk. Da er den norske
originalen et riktigere utgangspunkt enn en oversettelse av en engelsk tekst.

### Åpent punkt: oppstart av tilbakekjøpsprogram

Oppstarten av et tilbakekjøpsprogram er ekte nyhet, men ligger i samme kategori
som de ukentlige statusrapportene:

> SalMar — Oppstart for tilbakekjøpsprogram for aksjer
> DNB Bank ASA — status for tilbakekjøpsprogram etter uke 34 2026

Med regelen i FR-502 filtreres begge bort, og den første er et tap. Dette er
samme problem som i samlekategorien — kategorifeltet skiller ikke — og må løses
før innlevering. Ført som åpent punkt 8 i PRD-en.

---

## 5. KI-laget

### Hvorfor samlekategorien fortsatt vises når laget er av (FR-602)

Forsvinning ville blandet sammen to forskjellige ting — færre meldinger og
uforklarte meldinger — og gjort sammenligningen av og på meningsløs. Den ærlige
kontrasten er de samme meldingene, uten forklaring og uten relevansvurdering.

### Hvorfor usikkerhet ikke sorteres ned (FR-603)

Løftet er at usikkerhet **vises** i stedet for at modellen gjetter. Nedsortering
skjuler usikkerheten bak en rekkefølge brukeren ikke kan se, og gjør av/på-
sammenligningen vanskeligere å lese.

### Hvorfor relevansskalaen ble oversatt, ikke arvet (FR-606)

Tredelingen kommer fra utkastene til Product Brief, der den svarte på «handler
saken om selskapet?». For NewsWeb er det spørsmålet allerede besvart av
`issuerSign` og trenger ingen modell. Skalaen svarer derfor nå på «betyr den noe
for en sparer?» — samme tre nivåer, nytt spørsmål.

### Åpent punkt: usikkerhetskriteriene er skrevet for medieartikler

De tre kjennetegnene i FR-603 ble formulert etter medietesten 2026-09-17, der
oppgaven var å avgjøre *hvilket selskap* en artikkel handler om. For NewsWeb er
den oppgaven allerede løst av `issuerSign`, og KI-oppgaven er en annen: om saken
betyr noe for en sparer.

Kjennetegn 2 og 3 overføres direkte. Den felles letemeldingen fra Equinor,
Aker BP og Vår Energi er nøyaktig tilfellet der mange selskaper nevnes
likeverdig.

Kjennetegn 1 bærer svakt: når utstederen selv er avsender, nevnes selskapet
nærmest alltid i overskrift eller ingress. Kriteriet må enten omformuleres for
meldingsoppgaven eller forbeholdes relevanseksperimentet, som fortsatt bruker
medieartikler. Må avklares før KI-laget implementeres.

---

## 6. Signalet

### Hvorfor nøytralsonen ikke er valgfri (FR-702)

Dette er ikke en justering for penhetens skyld. Kravet stammer fra en
formulering i utkastene til Product Brief:

> manglende data, feilende kilder og dager uten tydelige signaler håndteres
> uten at hovedflyten stopper eller systemet tvinger frem et resultat
>
> — `docs/ai-prompts/product-brief/endelig-kandidat.md`, linje 59

Formuleringen står i tre av utkastene, men falt ut under språkvasken og finnes
ikke i briefen slik den foreligger. Kravet er likevel gruppens eget, og en
trendsjekk som alltid slår ut, bryter det.

### Hvorfor terskel 2 og ikke 3 (FR-705)

Målt mot de 15 dagene:

| Terskel | Aksjer per dag, snitt | Mest | Minst | Dager uten utslag |
|---|---:|---:|---:|---:|
| ≥ 2 | 5,4 av 15 | 13 | 2 | 0 av 15 |
| ≥ 3 | 1,6 av 15 | 7 | 0 | 7 av 15 |

Terskel 3 gir sju av femten dager helt uten utslag. For en demonstrasjon er det
en reell risiko: gruppen kan treffe en uke der løsningen ikke har noe å vise
fram.

### Hvorfor begrensningen på selektiv nyhetshenting ble fjernet

Et tidligere utkast av FR-705 begrenset meldingshenting og KI-vurdering til
selskapene som skilte seg ut. Begrensningen hadde ingen begrunnelse — NewsWeb
koster ingen kvote — og den motsa både FR-404, som etterfyller meldinger for hele
intervallet, og FR-203, som lover meldinger i aksjedetaljen for enhver aksje.

### Åpent punkt: skjevfordeling mot positiv retning

Målingen ga 68 % positiv retning mot 19,6 % negativ; med nøytralsonen faller den
positive andelen til 65,3 %.

Årsaken er strukturell: trend er en **vedvarende tilstand**, mens bevegelse og
interesse er **hendelser**. I en stigende periode gir det systematisk positivt
utslag, fordi trendsjekken bidrar hver eneste dag mens de to andre tier.

Skjevheten skal *ikke* justeres bort nå. Om den er et problem eller bare en
riktig beskrivelse av perioden, avgjøres mot året — ikke mot femten dager.

---

## 7. Kvoten og relevanseksperimentet

### Hvorfor universet er 15 og ikke flere

EODHD gir 20 kall i døgnet på gratisnivå, og kurser koster ett kall per symbol.
Bulk-endepunktet koster 100 kall flatt og er ubrukelig. Ett kall per symbol er
eneste vei, og 15 symboler gir fem kalls margin til omkjøringer, feilretting og
manuell testing.

### Hvorfor OSEBX er holdt utenfor v1

OSEBX ble hentet i de tidlige datakildetestene — se `docs/reflection-log.md` —
og ble med videre i planleggingsnotatene av den grunn. Ingen av kravene i PRD-en
bruker den. Å hente den ville kostet et sekstende kall og
redusert marginen til fire, og en ubrukt datakilde er bare én ting til som kan
feile.

### Hvorfor «for dyrt» ikke gjelder relevanseksperimentet

`docs/kilder-og-rettigheter.md` fører EODHDs nyhets-API som «forkastet — for
dyrt». Den vurderingen gjaldt *daglig drift*, der 10 kall per ticker hver dag er
uholdbart mot en kvote på 20. For én engangsinnsamling er regnestykket et annet.

Kostnaden er dokumentert 2026-09-20: 5 kall per forespørsel pluss 5 kall per
ticker, altså 10 for én ticker.

Åtte selskaper à 10 kall er 80 kall, som er anslaget gruppen kom fram til —
riktig tall, men av en annen grunn enn den gruppen la til grunn. Innsamlingen
gjøres i uke 39 eller 40, mens bonuskvoten finnes. At bonuskvoten dekker 80 kall
er ikke kontrollert mot faktisk kontosaldo, og det er heller ikke verifisert at
gratisnivået gir tilgang til nyhets-API-et for `.OL`-tickere i det hele tatt.

**Innsamlingen skjer først etter at EODHDs bruksvilkår er kontrollert.**
Spørsmålet er om vilkårene tillater at innholdet brukes som input til en
språkmodell — nøyaktig det spørsmålet E24 svarte nei på.

---

## 8. Krav som er berget fra utkastene

Flere krav i PRD-en stod i utkastene til Product Brief og falt ut av den
leverte versjonen. De er berget og skrevet inn:

| Krav | Hva som falt ut |
|---|---|
| FR-408 | «Dagens vurderinger lagres automatisk med dato, signalstyrke, retning, bidragende faktorer, relevante nyheter og kurs» |
| FR-606 | Den tredelte relevansskalaen |
| FR-702 | «…uten at systemet tvinger frem et resultat» |
| Suksessmålet «Grensesnitt og stabilitet» | «hovedflytene fungerer stabilt og har et ryddig, gjennomarbeidet grensesnitt i en demonstrasjon» |

Fullstendig oversikt over mønsteret, de to tapsmekanismene og tiltaket:
`docs/reflection-log.md`, oppføringen 20.09.2026.

---

## 9. Lagringen: filer i dag, database i arkitekturfasen

**Åpent punkt 17.** Dette er en vurdering av grunnlaget, ikke en beslutning.

### Hva faglærer sa, ordrett

> Hvis du ikke har behov for en database, så er prosjektet ditt for enkelt, noe
> som vil gjenspeile karakter. Vi har tre nivå: Enkel, Medium, Vanskelig. Alle
> tre nivåene innebærer database, så uten database vil dette påvirke karakteren
> hardt.

Supabase ble nevnt som eksempel, ikke som krav. Valget skal begrunnes i
applikasjonens behov.

### Dagens beslutning dekker ikke dette

FR-406 fastsetter **to lagre**: beregningsgrunnlaget som lastes ned i sin helhet
ved hver henting, og rådata som tidsstemplede øyeblikksbilder som aldri skrives
om. Begge er i dag tenkt som filer, og `data/` er gitignorert.

Den beslutningen ble tatt for å løse et *kvoteproblem* — at serien aldri skal
skjøtes på, fordi EODHD regner `adjusted_close` om bakover ved hvert utbytte.
Den ble ikke tatt som et svar på hvordan applikasjonen skal lagre noe som helst
annet. Det spørsmålet er ikke stilt før nå.

### Hvilke krav peker mot relasjonell lagring

| Krav | Hva det krever | Peker mot database? |
|---|---|---|
| **FR-408** — dagens vurdering per aksje per dag | Nøkkel `(dato, aksje)` med signalstyrke, retning, tre sjekkverdier, kurs og hvilke meldinger som ble vist. Spørsmålet kravet selv stiller er «hva sa løsningen om EQNR for to uker siden?» | **Ja, sterkest.** Det er et oppslag på nøkkel og et intervall over tid. En fil per dag gjør dette til en katalogskanning |
| **FR-604 / FR-605** — KI-logg med promptversjon og modell | Hver vurdering skal bære promptversjon og modell, og eksempelsettet i uke 45 skal vise *hva KI-laget skilte* — altså en sammenstilling av regelfilterets utfall mot KI-vurderingen, filtrert på promptversjon | **Ja.** Det er en spørring med filter og sammenstilling, ikke en filoperasjon |
| **FR-407** — merking av utbyttedager | Kursraden for en dato må kobles mot `EKS.DATO`-meldinger for samme utsteder og dato (FR-503) | **Ja.** Det er en join mellom to datasett på `(utsteder, dato)` |
| **FR-405** — avkorting og deling av intervaller | Når et intervall deles og hentes på nytt, kommer de samme meldingene tilbake i flere svar. De må skrives idempotent | **Delvis.** Et unikt `messageId` som primærnøkkel løser det; i filer må det løses for hånd |
| **FR-606** — relevansskalaen | Tre verdier lagret per melding | Marginalt. Det er én kolonne |
| **FR-406** — beregningsgrunnlaget | Lastes ned i sin helhet og erstattes | Nøytralt. Passer like godt som tabell som lastes på nytt, og som fil |
| **NFR-07 / FR-406** — rådata som uforanderlige øyeblikksbilder | Skrives aldri om, skal kunne leses om ti år uten applikasjonen | **Nei — taler imot.** Et tidsstemplet JSON-øyeblikksbilde *er* formatet. En database legger et lag mellom dokumentasjonen og den som skal etterprøve den |

**Konklusjonen på behovsspørsmålet:** behovet er reelt, og det er ikke konstruert
for å tilfredsstille et karakterkrav. FR-408 og FR-604/605 er begge
tidsserie- og spørringsproblemer som ble skrevet inn lenge før faglærer uttalte
seg, og FR-407 er en join. Det som *ikke* hører hjemme i en database, er
rådatalageret — det skal fortsatt være filer.

### SQLite mot Postgres/Supabase

| Hensyn | SQLite | Postgres / Supabase |
|---|---|---|
| Applikasjonen kjører lokalt, én bruker | Passer. Ingen server, ingen port, ingen oppstartsrekkefølge | Krever en server som kjører ved siden av — eller en sky-instans |
| Del av Python-standardbiblioteket | Ja, `sqlite3`. Ingen ny avhengighet | Nei. Driver, tilkoblingsstreng og hemmeligheter |
| Demonstrasjonen | Filen følger med. Ingenting å sette opp foran klassen | Én ting til som kan feile i rommet |
| Læringsverdi og «nivå» | SQL, skjema, nøkler, joins og migrasjoner — alt som er poenget med kravet | Det samme, pluss drift |
| Backup og etterprøvbarhet | Én fil, kopieres. Ligger under `data/`, altså utenfor git | Dump må eksporteres |
| **Vilkårene fra 21.09** | **Ingenting forlater maskinen** | **Se under — dette er den avgjørende forskjellen** |

**Vilkårene begrenser valget, og det er nytt siden i går.**

Supabase er en *hostet* tjeneste. Å legge børsmeldinger fra NewsWeb og kursdata
fra EODHD i en Supabase-instans er å overføre innholdet til en tredjepart. Det
treffer to ting vi nettopp har dokumentert:

- **EODHDs godkjenning av 21.09** er uttrykkelig betinget av at «the output
  stays local, the project is not publicly deployed, and the data is not
  published, redistributed, resold». En hostet database er ikke «local».
- **Euronexts vilkår** forbyr å «otherwise transfer any of the Content to any
  third person». Klausulen er sitert i `docs/kilder-og-rettigheter.md`.

Det betyr ikke at Supabase er utelukket — tjenesten kan kjøres selvhostet, og
faglærer nevnte den som eksempel, ikke som krav. Men **velges en hostet database,
må vilkårsarbeidet gjøres om igjen**, og godkjenningen vi fikk 21.09 dekker det
ikke.

**Vurderingen peker mot SQLite**, fordi den gir hele det faglige innholdet i
kravet uten å røre en premiss vi nettopp har brukt to dager på å få skriftlig.
Beslutningen er likevel ikke tatt her — den hører til arkitekturfasen, og står
som åpent punkt 17 med eier Gruppen.
