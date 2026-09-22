---
title: 'Motstandergjennomgang — ARCHITECTURE-SPINE.md'
lens: motstander
target: '../ARCHITECTURE-SPINE.md'
sources:
  - ../ARCHITECTURE-SPINE.md
  - ../../../prds/prd-G74-lund-osen-2026-09-20/prd.md
  - src/kursdata.py
  - src/fetch_prices.py
  - src/app.py
  - src/signalberegning.py
  - src/meldinger.py
  - src/markedsoversikt.py
  - src/aksjedetalj.py
  - src/graf.py
created: '2026-09-22T11:40'
---

# Motstandergjennomgang — ARCHITECTURE-SPINE.md

## Dom

Spinen holder lagene fra hverandre, men ikke **byggerne**: den sier hvem som
*ikke* får røre hva, og nesten ingenting om hvem som *skal* røre hva — og
derfor kan to personer levere hver sin AD-lydige enhet som ikke passer sammen,
i minst elleve punkter, hvorav to gjør at v1 enten mister historikk eller
aldri får noen.

## Metode

For hvert funn er det konstruert **to enheter ett nivå under spinen** — to
stories, tenkt bygget av to ulike personer som begge har lest spinen og fulgt
hver eneste AD til punkt og prikke. Et funn teller bare hvis **begge** enhetene
er AD-lydige og de likevel ikke kan stå i samme kodebase. Der funnet også
treffer kode som finnes i dag, er linjen sitert.

Hvert funn ender i en **lukking**: ordlyden i en ny eller strammere AD.

## Funn

| # | Hull | Kolliderende par | Alvorlighet |
|---|---|---|---|
| 1 | Ingen skriver `vurdering` | Websiden vs. hentekommandoen | **Kritisk** |
| 2 | `erstatt_serie` river grunnen under `vurdering` | Kurslageret vs. Vurderingslageret | **Kritisk** |
| 3 | Utbyttemerkingen har to kilder og `melding` to eiere | Meldingsfilteret vs. utbyttemerkingen | **Høy** |
| 4 | `Kurslager` og `Kurskilde` er to porter til ett datasett | Lagringsadapteren vs. testdoblene | **Høy** |
| 5 | Kursraden har to former — engelske API-nøkler vs. norsk i kode | SQLite-adapteren vs. kjernen | **Høy** |
| 6 | «Dagen» er udefinert når klokka er UTC og børsen i Oslo | Børsdagskontrollen vs. vurderingsskriveren | **Høy** |
| 7 | AD-16 mot AD-7: en migrasjon som endrer formen på `vurdering` | Migrasjon 003 vs. Migrasjon 003' | **Høy** |
| 8 | To prosesser skriver til samme SQLite-fil — skapt av AD-10 selv | Web-oppstart vs. hent-oppstart | **Middels** |
| 9 | `feil` har verken eier, port eller form | Hentingen vs. markedsoversikten | **Middels** |
| 10 | `melding` er uklassifisert i AD-7, og `vurdering` peker på den | Etterfyllingen vs. historikkvisningen | **Middels** |
| 11 | Datasett uten port: Euronext-oppslaget og `skjema_versjon` | Hendelsesvisningen vs. migrasjonskjøreren | **Lav** |

---

### Funn 1 — Ingen skriver `vurdering`. Begge enhetene har rett. `[Kritisk]`

**Enhet A — «Markedsoversikten leser fra basen» (bygger A).**
A leser AD-10: *«`docker run` starter Flask og koster null API-kall, alltid.»*
A implementerer `app.py` slik den er i dag: leser gjennom porten, regner
signalet i kjernen per visning, rendrer. A skriver ingenting. Begrunnelsen er
AD-1 (kjernen gjør ingen I/O) og AD-10 (webserveren starter aldri en henting).
Capability-kartet gir A områdene FR-101..103 og FR-201..204. **FR-408 står ikke
i A sin rad.**

**Enhet B — «Hentekommandoen» (bygger B).**
B leser AD-2, AD-5, AD-6, AD-15 og bygger `docker run … hent`: femten kall,
øyeblikksbilde til `ose-raa`, `erstatt_serie` mot `ose-db`. Capability-kartet
gir B raden «Henting og kvote (FR-401..405) → `fetch_prices.py`, styres av
AD-2, AD-5, AD-10, AD-15». **FR-408 står ikke i B sin rad heller** — den ligger
i en tredje rad, «Dagens vurdering (FR-408) → `Vurderingslager`», som navngir
*porten*, ikke *kalleren*.

**Kollisjonen.** Ingen av dem skriver en eneste `vurdering`-rad, og begge har
fulgt spinen. FR-408 krever at *«lagringen skjer automatisk, fra første
kjøring»*, og FR-604 gjentar kravet for KI-loggen: *«Loggingen starter ved
første kjøring, ikke når eksempelsettet skal lages.»* Spinen navngir porten og
utelater utløseren. Resultatet er at AD-7 — som finnes for å verne historikken
— verner en tom tabell.

**Og den motsatte feilen er like AD-lydig.** Leser A i stedet AD-10 bokstavelig
(*«starter aldri en **henting**»* — skriving er ikke henting), skriver A en
`vurdering`-rad per sidevisning. Da faller tre ting samtidig:

- Åpnes siden to ganger samme dag, er det andre skrivet enten et
  primærnøkkelbrudd eller en stille endring. AD-7 forbyr `endre`, så porten har
  ingen lovlig måte å håndtere det på. **AD-7 beskriver hvilke metoder porten
  mangler, men ikke hva `skriv` gjør når raden finnes fra før.**
- En dag ingen åpner løsningen, finnes ingen rad. FR-408 sier *«For hver aksje,
  hver dag»*. AD-10 gjør «hver dag» umulig å oppfylle fra websiden, fordi en
  container som ikke startes ikke gjør noe.
- Feltet **«Relevante meldinger»** i FR-408 kan bare fylles der meldingene er —
  og meldingsdelen ligger bak åpent punkt 1. Skriver B vurderingen ved henting,
  har B ingen meldinger å føre inn. Skriver A den ved visning, har A dem.

**Lukking — ny AD-17, «Vurderingen skrives av hentekommandoen, én gang per
børsdag».** Utløseren må navngis, ikke bare porten: *etter en vellykket
`erstatt_serie` for et symbol skriver hentekommandoen symbolets vurdering for
den børsdagen serien slutter på. `Vurderingslager.skriv` er idempotent på
(symbol, dato): et andre skriv med identisk innhold er en no-op, et andre skriv
med avvikende innhold er en feil — ikke en oppdatering.* Og: *websiden skriver
ingenting, i noen tabell.* Da er AD-10 en skriveregel og ikke bare en
hentingsregel, og FR-408s «hver dag» blir et spørsmål om at hentingen kjøres —
noe som er synlig og målbart — i stedet for om noen tilfeldigvis åpnet siden.

---

### Funn 2 — `erstatt_serie` river grunnen under `vurdering`. `[Kritisk]`

**Enhet C — «`Kurslager` med `erstatt_serie`» (bygger A).**
AD-5 er ordrett: *«`Kurslager.erstatt_serie(symbol, rader)` sletter symbolets
rader og setter inn de nye i én transaksjon.»* C skriver nøyaktig det:
`DELETE FROM kurs WHERE symbol = ?` etterfulgt av `INSERT`. Ingen
`legg_til_rad`, én transaksjon. AD-5 er innfridd til punkt og prikke.

**Enhet D — «`Vurderingslager` med referanseintegritet» (bygger B).**
FR-408 krever at vurderingen bærer `close` og `adjusted_close`. B vil at de
lagrede kursene ikke skal kunne peke på noe som ikke finnes, og legger
`FOREIGN KEY (symbol, dato) REFERENCES kurs(symbol, dato)`. AD-4 sier SQLite;
AD-16 sier migrasjon; AD-7 sier ingen `slett` og ingen `endre` på porten — og B
legger ingen av dem inn. B er også AD-lydig.

**Kollisjonen, i tre varianter, alle AD-lydige:**

| B sitt valg | Hva C sin `erstatt_serie` gjør dag 2 |
|---|---|
| `ON DELETE CASCADE` | Hver henting sletter all vurderingshistorikk for symbolet. AD-7 er brutt uten at noen kalte `slett` — kaskaden ligger i skjemaet, og **AD-7 regulerer portens metoder, ikke SQL-nivået** |
| `ON DELETE RESTRICT` (eller default med `PRAGMA foreign_keys=ON`) | Hentingen feiler for hvert symbol som har en vurdering fra i går. Fra dag 2 kan løsningen aldri hente mer. AD-15 reddet oss fra én feilende ticker; her feiler alle femten |
| Ingen fremmednøkkel | Ingenting knekker, men `vurdering`-radene peker på kursrader som ikke lenger finnes i den formen de ble regnet på — se under |

**Den siste varianten er den farligste, fordi den ikke feiler.** AD-5s egen
begrunnelse er at *«EODHD regner serien om bakover ved hvert nytt utbytte»*.
Det betyr at `erstatt_serie` ikke bare setter inn de samme radene på nytt — den
setter inn **et nytt justeringsgrunnlag for hele historikken**. Gårsdagens
lagrede `adjusted_close` i `vurdering` er da et annet tall enn gårsdagens
`adjusted_close` i `kurs`, og gårsdagens lagrede signalstyrke er et annet tall
enn det `beregn_signal` gir hvis den kjøres på dagens `kurs`-tabell.

AD-7 sier at dette er **riktig**: *«en omregning gir dagens parametres svar,
ikke datidens.»* Men spinen sier ikke hvilken av de to som vises. Og der står
to nye enheter:

- **Enhet C′ — «Aksjedetaljen viser de tre sjekkene» (bygger A)** følger FR-706
  og regner sjekkene fra `kurs`, slik `aksjedetalj.bygg_detalj` gjør i dag.
- **Enhet D′ — «Historikk: hva sa løsningen om EQNR?» (bygger B)** følger
  FR-408 og AD-7 og leser den lagrede vurderingen.

Etter ett utbytte viser de to skjermbildene **ulik styrke for samme aksje samme
dato**, og begge kan peke på et krav som sier at de har rett. FR-202 har
allerede målt hvor stor avstanden er: median 3,72 %, og 8,93 % for FRO.

**Lukking — stram AD-5 og AD-7 sammen.**
1. *`kurs` er gjenoppbyggbar og har ingen innkommende fremmednøkler. `vurdering`
   og `ki_logg` kopierer de kursverdiene de trenger og peker ikke på `kurs`.
   Referanseintegritet mot en tabell som erstattes i sin helhet er en felle, ikke
   en garanti.*
2. *En lagret vurdering er datidens svar og skal vises som det. Der en lagret og
   en omregnet verdi kan stå side om side, merkes den lagrede med datoen den ble
   skrevet, og ingen skjerm blander de to i samme tabell.*

---

### Funn 3 — Utbyttemerkingen har to kilder, og `melding` to eiere. `[Høy]`

Dette er hullet mellom AD-3 og AD-7 som oppdraget peker på, og det er verre enn
det ser ut, fordi PRD-en har **to** veier til samme svar.

**Enhet E — «Meldingsfilteret» (bygger A).**
A eier `Meldingskilde` per AD-3 og implementerer FR-501/FR-502 med AD-14s
bindende rekkefølge: dedupliser først, bøtte etterpå. A legger rekkefølgen
**i porten**, slik at ingen kaller kan få den gal — nettopp det AD-14 finnes
for. A sin port returnerer derfor bare bøttene som skal vises, og EKS.DATO er
ikke blant dem: FR-503 sier at de *«vises ikke i meldingslista»*.

**Enhet F — «Utbyttemerking» (bygger B).**
B skal oppfylle FR-407. Nå kan B velge, og **begge valgene er AD-lydige**:

- **F1, meldingsveien.** FR-503 sier rett ut at EKS.DATO-kategorien *«føres til
  utbyttemerkingen»*. B trenger rader A sin port aldri gir ut, og lager derfor
  `Utbyttekilde` over samme `melding`-tabell. AD-3 forbyr to **skrivere** — ikke
  to **porter** — og setningen *«hvert datasett har nøyaktig én port»* redder
  ikke situasjonen, for spinen definerer aldri hva et datasett er. Er «meldinger
  til visning» og «eks.dato-hendelser» ett datasett eller to? B svarer to.
- **F2, kursveien.** Boksen i FR-407 sier: *«Datakilden er ikke lenger avhengig
  av NewsWeb … justeringsdagen kan leses ut av kursserien alene»*, og åpent
  punkt 4 har målt den: 38 hendelser over 3 720 dagoverganger, rent skille fra
  0,05 til 0,5 prosentpoeng. B utleder eks.dato fra `kurs` og rører aldri
  `melding`.

**Kollisjonene.**

1. **To sannheter om samme dag.** Bygges F1 og F2 av hver sin person — og
   ingenting i spinen hindrer det, siden utbyttemerking **ikke finnes som rad i
   Capability-kartet i det hele tatt** — kan de to være uenige om hvilke dager
   som merkes. Spinen binder FR-407 til AD-4 («SQLite er motoren») og FR-503 til
   `meldinger.py`, og velger aldri kilde.
2. **Dedupliseringen gjelder ikke for F1.** AD-14 binder FR-501 og FR-502 — ikke
   FR-503. Leser F1 `melding`-tabellen direkte, får F1 språkdublettene med:
   samme eks.dato kommer som norsk og engelsk melding, og dagen merkes to
   ganger. F1 har ikke brutt AD-14; AD-14 gjelder ikke der.
3. **Kategorinormaliseringen er privat i dag.** `meldinger._normaliser` gjør
   `" ".join(kategori.strip().upper().split())`, men funksjonen er understreket
   og ikke en del av noen port. F1 vil sammenligne mot strengen `"EKS.DATO"` med
   sin egen normalisering. To normaliseringer av samme felt er samme begrep i to
   representasjoner.
4. **AD-7 klassifiserer ikke `melding`.** Merknaden under AD-7 sier at `kurs` er
   gjenoppbyggbar og at `vurdering` og `ki_logg` ikke er det. `melding` nevnes
   ikke. Er den gjenoppbyggbar, kan den erstattes som `kurs` — og da gjelder
   funn 2 en gang til, her.

**Lukking — ny AD-18, «Utbyttedagen utledes av kursserien, og `melding` har én
port».**
*Eks.dato utledes av avviket mellom `close`-endringen og `adjusted_close`-endringen
(åpent punkt 4), ikke av EKS.DATO-meldinger. FR-503 nedgraderes til en
kryssjekk, ikke en kilde. `melding` har én port, `Meldingskilde`, og den porten
leverer alle bøttene fra `meldinger.filtrer` — inkludert `utbyttemerking` — etter
dedupliseringen i AD-14. Ingen annen modul spør `melding`-tabellen.*
Da faller også avhengigheten til åpent punkt 1 bort for FR-407, akkurat slik
PRD-ens egen note sier at den kan.

---

### Funn 4 — `Kurslager` og `Kurskilde`: spinen gir ett datasett to porter. `[Høy]`

**Kollisjonen står inne i spinen selv.** AD-3: *«hvert datasett har nøyaktig
**én** port og nøyaktig **én** skriver. Lesere går gjennom porten. Portene er
`Kurslager`, `Meldingskilde`, `Vurderingslager` og `KILogg`.»* Consistency
Conventions: *«Porter navngis `<Datasett>lager` (skriver) eller `<Datasett>kilde`
(leser).»* Den ene sier én port; den andre deler ut to navn per datasett. Og
koden har allerede `Kurskilde` (`src/kursdata.py`), mens AD-5 navngir
`Kurslager.erstatt_serie`.

**Enhet G — «SQLite-adapteren» (bygger A)** leser AD-3 bokstavelig: **én** port.
A lager `Kurslager` med både `erstatt_serie`, `serie` og `tidsstempel`, og
pensjonerer `Kurskilde`.

**Enhet H — «Markedsoversikten mot base» (bygger B)** leser AD-3s eget forbehold:
*«mønsteret er utvidet, ikke oppfunnet. `Kurskilde` i `kursdata.py`»*, og
konvensjonens skriver/leser-deling. B beholder `Kurskilde` som lesende port —
også fordi `MinneKilde` og `SnapshotKilde` allerede implementerer den, og
Conventions krever at *«skall testes med port-dobler som `MinneKilde`»*.

**Kollisjonen.** A sin adapter implementerer ikke B sin protokoll og omvendt;
`markedsoversikt.bygg_oversikt(kilde: Kurskilde)` og
`aksjedetalj.bygg_detalj(aksje, kilde)` tar B sin form, mens A sin adapter er
det eneste som kan skrive. Testdoblene AD-8 forutsetter, dekker bare den ene.

**Lukking — stram AD-3.** *Ett datasett har én lesende port `<Datasett>kilde` og
høyst én skrivende port `<Datasett>lager`. Den skrivende arver den lesende, slik
at en adapter tilfredsstiller begge og en testdobbel kan nøye seg med den
lesende. For `kurs` betyr det: `Kurskilde` (`tidsstempel`, `serie`) og
`Kurslager(Kurskilde)` (`erstatt_serie`).* Og AD-3s liste over porter må skrives
om, for den navngir i dag bare den ene halvparten.

---

### Funn 5 — Kursraden har to former. `[Høy]`

`Kurskilde.serie` returnerer `list[dict]`. Hva som står i den dicten, står ikke
i spinen — men kjernen vet det:

```python
# signalberegning.py
return [float(rad.get("adjusted_close") or rad["close"]) for rad in rader]
# markedsoversikt.py / aksjedetalj.py
verdi = rad.get("adjusted_close") or rad.get("close")
# markedsoversikt.py
dato=siste["date"], sluttkurs=float(siste["close"])
```

Nøklene er **EODHDs engelske feltnavn**, lekket helt inn i kjernen. Og
Consistency Conventions sier: *«Navn: Norsk i kode og kommentarer, som i resten
av prosjektet.»*

**Enhet I — «Skjema og adapter» (bygger A)** følger navnekonvensjonen og lager
`kurs(symbol, dato, sluttkurs, justert_kurs, volum)` med norske kolonner, og
returnerer `sqlite3.Row`-lignende dicter med de navnene. AD-1 er ikke brutt —
adapteren ligger i skallet. Konvensjonen er fulgt.

**Enhet J — «Signalet mot base» (bygger B)** rører ikke kjernen, fordi AD-13
låser parametrene og AD-1 holder kjernen ren, og fordi ingen AD ber om at
kjernen endres. B forventer `adjusted_close`.

**Kollisjonen.** A sin adapter gir `justert_kurs`; B sin kjerne spør etter
`adjusted_close`, får `None`, faller tilbake på `rad["close"]` som heller ikke
finnes, og kaster `KeyError` — eller, verre, hvis A beholder `close` på engelsk
og bare oversetter den justerte: da faller kjernen stille tilbake på **ujustert
kurs**, alle beregninger bryter FR-701, og ingen test feiler. Spinen har en rad
om `close` mot `adjusted_close` under Consistency Conventions, men den handler om
*hvilken serie som vises hvor* — ikke om hva feltet heter når det krysser porten.

**Tilleggsfunn i samme linje.** `rad.get("adjusted_close") or rad["close"]` er
en falsy-fallback: en justert kurs på `0.0` — som EODHD kan levere for en
suspendert eller feilrapportert dag — leses som «mangler» og erstattes med
ujustert kurs. Samme mønster i `_justert` i to moduler. Det er ikke et
spine-hull, men det er den typen feil et manglende formkrav inviterer til.

**Lukking — ny AD-19, «Portens radform er en verditype, ikke en dict».**
*`Kurskilde.serie` returnerer `list[Kursrad]`, en frossen dataklasse i
`kursdata.py` med felt `dato: str`, `sluttkurs: float`, `justert_kurs: float`,
`volum: float`. Oversettelsen fra EODHDs engelske feltnavn skjer nøyaktig ett
sted — i skallet, der svaret kommer inn — og ingen kjernemodul slår opp en
strengnøkkel i en rad. Mangler `justert_kurs`, er raden ugyldig; den erstattes
ikke stilltiende av `sluttkurs`.*

---

### Funn 6 — «Dagen» er udefinert. `[Høy]`

Consistency Conventions: *«Datoer: `YYYY-MM-DD` som tekst, overalt. Tidsstempler
er ISO 8601 med UTC-offset.»* AD-6: *«Datoen i et filnavn er dataenes dag —
aldri filens mtime.»* Ingen av dem sier **i hvilken sone en dato regnes**.

**Enhet K — «Børsdagskontroll» (FR-402, bygger A)** skal kontrollere at
*«nyeste `date` i svaret er forventet børsdag»*. A har lest at tidsstempler er
UTC og regner forventet børsdag fra `datetime.now(timezone.utc).date()`.

**Enhet L — «Vurderingsskriver» (FR-408, bygger B)** skal skrive *«Børsdagen
vurderingen gjelder»*. B bruker `date.today()` — lokal tid, samme som PRD-ens
egen instruks om at `updated` settes fra lokal klokke.

**Kollisjonen.** Oslo ligger på UTC+1/+2. Mellom midnatt og 01:00 (vinter) eller
02:00 (sommer) lokal tid er `date.today()` én dag foran UTC-datoen. En henting
kjørt 01:30 norsk tid gir da:

- K regner forventet børsdag fra gårsdagens UTC-dato, godtar svaret;
- L skriver vurderingen på dagens lokale dato.

Vurderingen for én og samme børsdag får to nøkler avhengig av hvem som skrev
den, og AD-7 forbyr å rette det etterpå. FR-402s løfte — *«Applikasjonen skal
aldri presentere gårsdagens tall som dagens»* — kan ikke innfris når «dagens»
ikke er definert.

**Dette er ikke hypotetisk; koden gjør det allerede.** I `fetch_prices.main`:

```python
naa = datetime.now(timezone.utc).isoformat()   # UTC
fil = DATA_KATALOG / filnavn()                 # date.today() → lokal dato
```

og `bygg_intervall` bruker `date.today()` for både `from` og `to`. Et
øyeblikksbilde hentet 01:30 norsk tid heter `kurser-raa-2026-09-22.json` og
inneholder `"hentet": "2026-09-21T23:30:...+00:00"`. AD-6 sier at datoen i
navnet er **dataenes dag** — her er den verken dataenes dag eller
tidsstempelets; den er hentemaskinens lokale dag.

**Andre halvdel: `_minutt` tåler ikke offset.** `meldinger._minutt` er
`tidspunkt[:16]` — en ren tekstavkorting. Konvensjonen «ISO 8601 med UTC-offset»
tillater både `2026-09-18T09:00:00+02:00` og `2026-09-18T07:00:00Z` for samme
øyeblikk. To enheter som normaliserer hver sin vei gir ulike
dublettnøkler, og FR-501 slutter å virke **stille**: 26 % av meldingene blir
liggende i dobbelt opp. Ingen test fanger det, fordi testdataene er skrevet av
den som skrev koden.

**Lukking — ny AD-20, «Én sone for dager, én form for tidsstempler».**
*Alle datoer i `kurs`, `melding`, `vurdering`, `ki_logg` og i filnavn er
børsdager i `Europe/Oslo`, regnet fra `datetime.now(ZoneInfo("Europe/Oslo"))` —
aldri fra `date.today()` og aldri fra en UTC-dato. Alle tidsstempler lagres
normalisert til UTC med suffikset `Z` og sekundoppløsning. Sammenligning av
tidsstempler skjer på parsede verdier, aldri på strengprefiks.* Konvensjonsraden
«Datoer» må skrives om tilsvarende, og åpent punkt 3 (kilden for
handelskalenderen) får da et entydig spørsmål å svare på.

---

### Funn 7 — AD-16 mot AD-7: er en formendrende migrasjon forbudt? `[Høy]`

Spinen svarer ikke, og den vet det: AD-16 er merket *«en ny beslutning, ikke
ADOPTED … ingen kode viser den ennå.»*

**Enhet M — «Migrasjon 003: promptversjon og modell på vurdering» (bygger A).**
FR-605 krever at hver lagret vurdering bærer promptversjon og modell. Skal de
være `NOT NULL`, eller skal `sjekker`-feltet deles fra én JSON-kolonne til tre
navngitte, har SQLite bare én vei: lag ny tabell, `INSERT INTO ny SELECT … FROM
gammel`, `DROP TABLE gammel`, `ALTER TABLE ny RENAME`. A gjør dette i en
nummerert SQL-fil og har fulgt AD-16 til punkt og prikke: ingen `ALTER TABLE`
utenfor en migrasjonsfil.

**Enhet N — «Migrasjon 003′» (bygger B).** B leser AD-7: *«Ingen `slett`, ingen
`endre`. **Fraværet er invarianten.**»* B mener et `DROP TABLE vurdering` er
den mest omfattende sletten som finnes og nekter. B legger i stedet til en
nullbar kolonne — det eneste `ALTER TABLE` SQLite gjør trygt — og der den
strengere formen kreves, oppretter B `vurdering_v2` og et view som forener de
to.

**Kollisjonen.** A ender med én tabell som er skrevet om; B med to tabeller som
holder samme entitet — og **da er AD-3 brutt av en AD-16-lydig handling**: to
skrivestier til «vurdering». Begge har fulgt bokstaven i hver AD. Spinen sier
selv at AD-16 *«følger av AD-7»*, men ikke hva som skjer når de to trekker i
hver sin retning.

**Lukking — presiser AD-7 og AD-16 i samme setning.**
*AD-7 forbyr at **applikasjonen** sletter eller endrer en vurdering. En migrasjon
som bevarer hver rads innhold — også når den gjør det ved å bygge tabellen på
nytt — er ikke en endring i AD-7s forstand og er tillatt. En migrasjon som
forkaster rader, slår sammen rader, eller utleder en verdi som ikke fantes,
er forbudt og skal i stedet legge til en kolonne med `NULL` for de gamle radene.
Hver migrasjon mot `vurdering` eller `ki_logg` skal ha en radtelling før og etter
i filhodet, og de to skal stemme.* Og: *en entitet skal aldri finnes som to
tabeller samtidig.*

---

### Funn 8 — To prosesser skriver til samme SQLite-fil. Skapt av AD-10. `[Middels]`

AD-4 sier at lagringsvalget *«omgjøres av: flere samtidige skrivere … Ingen av
delene er i v1.»* Men AD-10 og AD-16 skaper dem sammen.

**Enhet O — «Web-oppstart» (bygger A)** kjører migrasjonene ved oppstart, slik
AD-16 krever at `skjema_versjon` holdes à jour, og AD-10 tillater det — AD-10
forbyr *henting*, ikke migrasjon.

**Enhet P — «Hent-oppstart» (bygger B)** gjør det samme, av samme grunn. AD-10
sier selv at hentingen er *«en egen kommando mot samme image»*, og
Structural-Seed-diagrammet viser begge som `docker run` mot samme `ose-db`.

**Kollisjonen.** Kjøres `docker run … hent` mens webcontaineren står, har to
prosesser samme fil åpen for skriving. `erstatt_serie` er en sletting pluss en
innsetting i én transaksjon over femten symboler — den holder skrivelåsen lenge
nok til at websidens migrasjonskjøring kan møte `database is locked`. Verre: to
migrasjonskjøringer som starter samtidig kan begge lese `skjema_versjon = 2`.
AD-4s forutsetning om én skriver er altså ikke en observasjon om v1; den er en
forutsetning spinens egne beslutninger bryter.

**Lukking.** *Migrasjoner kjøres av nøyaktig én inngang — hentekommandoen, eller
en egen `migrer`-kommando. Webserveren kjører aldri en migrasjon; møter den en
`skjema_versjon` som er lavere enn koden forventer, viser den tom-tilstanden med
beskjed om hvilken kommando som skal kjøres, slik AD-10 allerede gjør for tom
base. Tilkoblingene åpnes med `PRAGMA journal_mode=WAL` og en `busy_timeout`.*

---

### Funn 9 — `feil` har verken eier, port eller form. `[Middels]`

AD-15: *«de som mangler føres i `feil` og navngis for brukeren.»* Consistency
Conventions: *«En manglende aksje er en **rad i `feil`**»* — «rad» antyder en
tabell. I dag er `feil` en `dict[str, str]` på `Resultat` og en nøkkel i
øyeblikksbilde-JSON-en.

**Enhet Q — «Hentingen fører feil» (bygger A)** beholder dagens form: `feil` går
inn i øyeblikksbildet. AD-6 er fulgt — filen skrives aldri om.

**Enhet R — «Markedsoversikten navngir de manglende» (bygger B)** skal oppfylle
AD-15s «navngis for brukeren». B kan ikke lese A sin `feil`, for AD-6 sier at
*«filene går ikke inn i databasen»* og Structural Seed viser `web --> db` og
ingen pil fra `web` til `ose-raa`. B utleder derfor de manglende som
«symboler uten kursrader», slik `app.py` gjør i dag:

```python
mangler = [a.navn for a in AKSJEUNIVERS if a.symbol not in vist]
```

**Kollisjonen.** De to listene er ikke den samme. A sin `feil` skiller «tomt
svar» fra «HTTPError 402 kvote brukt opp» — begrunnelsen for AD-15 er nettopp at
brukeren skal få vite *hvilke*. B sin liste sier bare at noe mangler, og den
mister også skillet FR-101 krever mellom *«Ukjent»* (kunne ikke regnes) og
*ingen rad i det hele tatt*. Dessuten: etter én vellykket henting og én mislykket
ligger gamle kursrader igjen i basen for symbolet, så B sin liste er **tom** mens
A sin har femten navn. Brukeren ser da en fullstendig oversikt bygget på
gårsdagens tall uten å få vite det — stikk i strid med FR-402.

**Tilleggsobservasjon.** Spinens Structural Seed viser at websiden bare leser
`db`, men `app.py` leser i dag `SnapshotKilde` fra fil, og AD-7 bruker nettopp
`SnapshotKilde` som presedens. Spinen pensjonerer altså den eksisterende
lesestien uten å si det. Migreringen av `app.hent_kilde` bør stå som en egen
story, ikke som noe den første som tar en base-story oppdager selv.

**Lukking.** *`feil` er et eid datasett med egen port `Feillager`, skrevet av
hentekommandoen i samme transaksjon som `erstatt_serie`, med feltene symbol,
dato, årsak og hentetidspunkt. Det er gjenoppbyggbart. Markedsoversikten leser
den, ikke en avledet liste, og skiller de tre tilstandene FR-101 krever: rad med
signal, rad med «Ukjent», og symbol uten rad.*

---

### Funn 10 — `melding` er uklassifisert, og `vurdering` peker på den. `[Middels]`

AD-7s merknad deler tabellene i to: *«`kurs` er gjenoppbyggbar; `vurdering` og
`ki_logg` er det ikke.»* `melding` og `feil` nevnes ikke i noen av gruppene.

Samtidig krever FR-408 feltet **«Relevante meldinger — hvilke meldinger som ble
vist for aksjen den dagen»**, altså en referanse fra en uerstattelig tabell til
en uklassifisert.

**Enhet S — «Etterfylling av meldinger» (FR-404, bygger A)** henter alle
kalenderdager i hullet på nytt. A behandler `melding` som gjenoppbyggbar — den
koster ingen kvote, så det er billigste vei — og erstatter intervallets rader,
i tråd med mønsteret AD-5 setter for `kurs`.

**Enhet T — «Historikkvisning» (FR-408, bygger B)** slår opp meldings-id-ene en
vurdering lagret og viser dem.

**Kollisjonen.** NewsWeb er *«udokumentert backend og kan endres uten varsel»*
(NFR-07). Endrer id-formen seg, eller faller en melding ut av et nytt svar, er
B sine referanser døde — og AD-7 forbyr B å rydde opp. Løsningen kan da ikke
besvare FR-408s eget spørsmål, som er hele grunnen til at AD-7 finnes.

**Lukking.** *Klassifiser hver tabell eksplisitt i AD-7: `kurs`, `melding` og
`feil` er gjenoppbyggbare; `vurdering` og `ki_logg` er det ikke. En uerstattelig
tabell refererer aldri til en gjenoppbyggbar ved nøkkel — den kopierer det den
trenger. `vurdering` lagrer meldingenes id, utsteder, kategori, tidspunkt og
tittel som verdier, slik FR-604 allerede krever for KI-loggen.*

---

### Funn 11 — Datasett uten port. `[Lav]`

AD-3 lister fire porter. Minst tre eide datasett mangler:

| Datasett | Hvor det kommer fra | Hvem eier det i spinen |
|---|---|---|
| Oppslagstabellen selskap ↔ Euronext-kalendernavn | FR-301: kalenderen oppgir *«verken ticker eller ISIN»*, og tabellen *«vedlikeholdes manuelt»* | ingen |
| Kommende hendelser | FR-301/FR-302 | ingen — ligger ikke i Capability-kartet |
| `skjema_versjon` | AD-16 | ingen (se funn 8) |
| `feil` | AD-15 | ingen (se funn 9) |

`AKSJEUNIVERS` er et femte, men det er en frossen konstant i `kursdata.py` og
faller innenfor portlagets *«verdityper»* — det er greit, og bør stå eksplisitt i
AD-3 så ingen «retter» det til en tabell.

**Lukking.** *AD-3s portliste skal være uttømmende for eide datasett, og et
datasett uten port er en mangel i spinen — ikke en frihet for den som bygger.
Kalenderoppslaget er en versjonert datafil i repoet, ikke en tabell, fordi det
vedlikeholdes for hånd og skal kunne leses i en diff.*

---

## Feil i kode, funnet underveis

Disse er ikke spine-hull, men de er konsekvenser av dem og bør rettes i samme
slengen:

1. **`src/fetch_prices.py`** blander `date.today()` (filnavn, `bygg_intervall`)
   og `datetime.now(timezone.utc)` (`hentet`). Se funn 6. Mellom midnatt og
   01–02 norsk tid er filnavnet en annen dag enn innholdet.
2. **`rad.get("adjusted_close") or rad["close"]`** i `signalberegning.py`, og
   `rad.get("adjusted_close") or rad.get("close")` i `markedsoversikt.py` og
   `aksjedetalj.py`: en justert kurs på `0.0` faller stille tilbake på ujustert
   kurs og bryter FR-701 uten at noe feiler. Bruk `is None`.
3. **`meldinger._minutt`** avkorter en tidsstempelstreng på tegn 16 og
   sammenligner tekst. Med «ISO 8601 med UTC-offset» som konvensjon er den
   sammenligningen ikke gyldig. Se funn 6.

## Hva som bør skje

| Rekkefølge | Handling |
|---|---|
| 1 | AD-17 (hvem skriver vurderingen) og den strammede AD-5/AD-7 — uten dem bygges funn 1 og 2 inn i første base-story |
| 2 | AD-19 (radformen) og AD-20 (sone og tidsstempel) — de treffer hver eneste story som rører data |
| 3 | AD-18 (én kilde for utbyttedagen, én port for `melding`) og presiseringen av AD-7/AD-16 |
| 4 | AD-3 skrives om: portlisten gjøres uttømmende, skriver/leser-delingen avklares, «datasett» defineres |
| 5 | Funn 8–11 som egne rader i åpne punkter |

Spinen bør ikke forlate draft før punkt 1 og 2 er skrevet inn. De øvrige kan
stå som åpne punkter, fordi de gjør skade først når meldingsdelen og KI-laget
bygges — og begge deler ligger uansett bak åpent punkt 1.
