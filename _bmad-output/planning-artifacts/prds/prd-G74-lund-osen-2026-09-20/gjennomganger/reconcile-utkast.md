# Avstemming av utkastmappa mot briefen og PRD-en

**Dato:** 2026-09-20
**Formål:** finne substansielt innhold — krav, tall, forbehold, kriterier og
beslutninger — som står i `docs/ai-prompts/product-brief/` men ikke gjenfinnes i
noen av de fire dokumentene prosjektet nå arbeider etter.

**Lest (alle fire utkast, i sin helhet):**

- `docs/ai-prompts/product-brief/chatgpt-utkast.md` (107 linjer)
- `docs/ai-prompts/product-brief/claude-utkast.md` (108 linjer)
- `docs/ai-prompts/product-brief/sprakvasket-korrigert.md` (101 linjer)
- `docs/ai-prompts/product-brief/endelig-kandidat.md` (101 linjer)

**Avstemt mot:**

- `_bmad-output/planning-artifacts/product-brief.md`
- `_bmad-output/planning-artifacts/prd-notater.md`
- `_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md`
- `_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md`

Detalj 1–6 i `korreksjon-til-brief.md` er allerede berget og er ikke behandlet
på nytt her. Nummereringen nedenfor fortsetter derfra.

**Resultat: sju nye funn.** Tre av dem er reelle krav som bør berges (7, 8, 10),
to er beslutninger som bør tas bevisst i stedet for å ha forsvunnet (9, 13), og
to er svake (11, 12) og tas med for fullstendighetens skyld.

---

## 7. Automatisk lagring av daglige vurderinger — borte i sin helhet

**Kilde (står i alle fire utkast, tre steder i hvert):**

`endelig-kandidat.md` linje 32 (identisk i `sprakvasket-korrigert.md` linje 32;
nær identisk i `chatgpt-utkast.md` linje 34 og `claude-utkast.md` linje 35):

> Dagens vurderinger lagres automatisk med dato, signalstyrke, retning,
> bidragende faktorer, relevante nyheter og kurs.

`endelig-kandidat.md` linje 58 (suksesskriterium, likelydende i de tre andre):

> dagens vurderinger lagres automatisk med det som trengs for senere historikk

`endelig-kandidat.md` linje 76 (omfangspunkt, likelydende i de tre andre):

> automatisk lagring av daglige vurderinger

**Status:** ingen treff på «automatisk lagring», «daglige vurderinger» eller
«dagens vurdering» i noen av de fire dokumentene. Kravet finnes hverken i
briefens omfang, i briefens suksessmål, i PRD-ens seksjon 2, blant FR-ene eller
blant NFR-ene.

**Er det dekket av noe annet? Nei.** De to lagringskravene PRD-en faktisk har,
dekker andre behov:

- **FR-406 (to lagre)** gjelder *kursdata*. Beregningsgrunnlaget lastes ned på
  nytt ved hver kjøring og skjøtes aldri på; rådatalageret er uttrykkelig
  «dokumentasjon og sikkerhetsnett, ikke beregningskilde». Ingen av dem lagrer
  en vurdering.
- **FR-604 (logging av KI-bidraget)** lagrer per *melding*: meldings-id,
  utsteder, kategori, hva regelfilteret gjorde, KI-ens vurdering og
  promptversjon. Den lagrer ikke signalstyrke, retning eller bidragende
  faktorer per aksje per dag, og er begrunnet i suksesskriteriet «KI-bidrag i
  drift», ikke i historikk.

**Vurdering: reelt krav, bør berges.** Dette er det største funnet i
gjennomgangen. Konsekvensene er konkrete:

1. Prosjektet har i dag ingen krav som gjør det mulig å svare på «hva sa
   løsningen om EQNR for to uker siden». Signalstyrke kan i prinsippet regnes
   om igjen fra kursserien, men *hvilke meldinger som ble vist som relevante
   den dagen* kan ikke rekonstrueres — NewsWeb-uttrekket og KI-vurderingen var
   knyttet til det tidspunktet.
2. Suksesskriteriet «Adopsjon» (minst 4 av 5 børsdager) og «KI-bidrag i drift»
   (eksempelsett fra minst én ukes drift) hviler begge på at driften etterlater
   seg spor. FR-604 dekker meldingssiden; signalsiden har ingen tilsvarende.
3. «Enkel historikkvisning» stod som strekkmål i alle fire utkast (se funn 11).
   Uten lagringen er det strekkmålet ikke bare utelatt, men umulig.

Anbefaling: inn som eget FR i PRD-ens seksjon 4.4/4.5, formulert som daglig
øyeblikksbilde per aksje med dato, signalstyrke, retning, bidragende faktorer,
viste meldinger og kurs.

---

## 8. Den tredelte relevansskalaen er borte — og ikke erstattet

**Kilde:** `endelig-kandidat.md` linje 28 (identisk i `sprakvasket-korrigert.md`
linje 28; samme innhold i `chatgpt-utkast.md` linje 30 og `claude-utkast.md`
linje 29):

> KI vurderer nyheter som direkte relevante, indirekte relevante eller lite
> relevante for selskapet

**Status:** ingen treff på «direkte relevant», «indirekte» eller «lite relevant»
i noen av de fire dokumentene.

**Vurdering: reelt krav, bør berges i tilpasset form.** Dette er ikke bare en
formulering. PRD-en pålegger KI-laget en relevansvurdering flere steder —
FR-502 sender samlekategorien (18 meldinger på fire uker) til «KI avgjør
relevans», og FR-602 sier at samlekategorien «vises umerket av relevans» når
laget er av — men **ingen steder står det hvilke verdier vurderingen kan ha.**
Utfallsrommet er udefinert i PRD-en. Utkastene hadde det definert.

Merk at oppgaven er endret siden utkastene: i utkastene gjaldt skalaen
medieartikler og spørsmålet «handler denne saken om selskapet», mens den i
PRD-en gjelder børsmeldinger der `issuerSign` allerede har svart på det
spørsmålet, og KI-spørsmålet er «betyr denne saken noe for en sparer». Skalaen
må derfor omformuleres, ikke kopieres tilbake. Men den må erstattes av noe —
dette er samme type hull som åpent punkt 2 i PRD-en beskriver for
usikkerhetskriteriene.

---

## 9. «KI identifiserer type hendelse» — falt ut uten at beslutningen er tatt

**Kilde:** `endelig-kandidat.md` linje 28 (likelydende i de tre andre utkastene;
`chatgpt-utkast.md` linje 30 har det som eget punktum: «KI skal også kunne
identifisere type hendelse og lage en kort forklaring.»):

> ... identifiserer type hendelse og lager en kort forklaring

**Status:** ingen treff på «type hendelse» eller «hendelsestype» i noen av de
fire dokumentene. «Kort forklaring»-halvdelen overlevde og er nå FR-604 og
FR-203.

**Vurdering: delvis overtatt, men beslutningen er ikke dokumentert.** Når kilden
ble byttet fra medier til NewsWeb, kom hendelsestypen med i metadataene —
kategorifeltet *er* en hendelsestype, og PRD-en bygger hele grovsorteringen på
det. Så langt er utelatelsen riktig.

Men akkurat der kategorifeltet ikke holder — i samlekategorien, som er hele
begrunnelsen for KI-laget (berget detalj 3: kategorien skiller ikke en
kontraktstildeling fra et sponsorat) — er «hvilken type hendelse er dette»
nettopp det spørsmålet KI skulle svare på. At kravet forsvant samtidig som
begrunnelsen for det ble styrket, ser ut som en forglemmelse snarere enn et
valg. Bør avklares sammen med funn 8, siden det er samme udefinerte utfallsrom.

---

## 10. Suksesskriteriet om stabilitet og gjennomarbeidet grensesnitt

**Kilde:** `endelig-kandidat.md` linje 60 (likelydende i alle fire; ordlyden i
`chatgpt-utkast.md` linje 66 er «de viktigste brukerflytene fungerer stabilt og
har et enkelt, ryddig og gjennomarbeidet grensesnitt i en demonstrasjon»):

> hovedflytene fungerer stabilt og har et ryddig, gjennomarbeidet grensesnitt i
> en demonstrasjon

Tilhørende omfangspunkt, `endelig-kandidat.md` linje 77:

> enkelt og gjennomarbeidet brukergrensesnitt

**Status:** ingen treff på «gjennomarbeid», «ryddig» eller «brukergrensesnitt» i
noen av de fire dokumentene. Briefens suksesstabell har seks rader
(Brukerutfall, Adopsjon, Kvalitet, KI-bidrag, Relevanseksperiment, Fortsatt
bruk), PRD-en sju — ingen av dem måler grensesnittet eller stabiliteten under
demonstrasjon. Briefens «Kvalitet»-rad måler daglig henting innenfor kvoten,
altså drift, ikke grensesnitt.

**Vurdering: reelt kriterium, bør berges.** Tre grunner:

1. Alle fire utkast — inkludert begge de uavhengige førsteutkastene — har det.
   Det er gruppens egen prioritering, gjentatt i både Executive Summary
   («prioriterer stabilitet, enkelhet og et ryddig grensesnitt fremfor mange
   funksjoner», som delvis overlevde i briefen som «prioriterer stabilitet
   fremfor mange funksjoner») og i omfanget og suksesskriteriene.
2. Demonstrasjonen er et faktisk milepælspunkt i PRD-en (uke 45, fra
   2026-11-02) og nevnes i fire sammenhenger der, men uten at noe mål sier hva
   som skal være godt nok ved den.
3. PRD-en har ett enkeltkrav som går på lesbarhet (FR-103, retning i tre
   redundante kanaler), men ingen paraply over grensesnittkvalitet. Det er en
   underlig asymmetri i et prosjekt som eksplisitt har valgt bort funksjoner
   til fordel for gjennomarbeiding.

---

## 11. Strekkmålene «enkel historikkvisning» og «sektorfilter»

**Kilde:** `endelig-kandidat.md` linje 79 (likelydende i alle fire):

> Hvis kjernen fungerer stabilt før fristen, kan enkel historikkvisning,
> sektorfilter, flere tidsperioder og lokalt lagrede favoritter legges til.

**Status:** to av fire punkter overlevde inn i PRD-ens «Hvis vi rekker»
(favorittmerking, flere valgbare tidsperioder), og OSEBX som referanseindeks er
kommet til. «Historikkvisning» og «sektorfilter» finnes ikke i noe av de fire
dokumentene — heller ikke som bortvalgt.

**Vurdering: svakt alene, men henger sammen med funn 7.** Strekkmål er per
definisjon ikke krav, og at en liste over «hvis vi rekker» blir omprioritert er
normalt. Det som gjør historikkvisningen verdt å nevne, er at den ikke er
omprioritert, men gjort umulig: uten lagringen i funn 7 finnes det ingen
historikk å vise. Sektorfilteret står svakere igjen — sektor er en kolonne i
`malinger.md`, universet er på 15 aksjer, og et filter på 15 rader har liten
verdi. Det siste er antakelig med rette strammet bort.

---

## 12. Premium/abonnement som betinget forretningsbeslutning

**Kilde:** `endelig-kandidat.md` linje 99 (likelydende i alle fire):

> Premiumfunksjoner eller abonnement kan vurderes dersom brukere faktisk
> opplever løsningen som nyttig nok.

Beslektet, `endelig-kandidat.md` linje 95: tidshorisonten «i løpet av de neste
2–3 årene» for veien fra markedsoversikt til personlig markedsassistent.

**Status:** ingen treff på «abonnement» eller «premium»; ingen tidshorisont i
briefens Vision. Briefen har beholdt «kommersiell versjon» som begrep, men bare
knyttet til rettigheter, personvern og regelverk.

**Vurdering: grensetilfelle, trolig med rette strammet bort.** Setningen bærer
en beslutning med et forbehold — betaling vurderes *først* hvis nytten er
dokumentert — og forbeholdet er den substansielle delen. Men den gjelder en
horisont langt utenfor v1, «betaling og abonnement» står uansett eksplisitt
utenfor v1 i både brief og PRD, og briefens Vision er kortet ned gjennomgående.
Tas med her fordi gjennomgangen skal være uttømmende, ikke fordi den bør
berges. Tidshorisonten 2–3 år er ren innramming.

---

## 13. Rådataene bak medietesten 17.09 finnes ikke dokumentert noe sted

**Kilde:** `claude-utkast.md` linje 19:

> I vår egen test av finansnyheter 17.09 hentet vi ti nyheter for DNB. Flere av
> dem handlet i realiteten om Infosys, om europeiske aksjer generelt eller om
> helt andre selskaper, og nevnte DNB bare fordi selskapet var ett av mange
> symboler i artikkelen. For Frontline var bildet motsatt: nyhetene var i
> hovedsak faktisk om selskapet eller om oljemarkedet det opererer i.

**Status:** testen omtales tre steder — `product-brief.md` linje 18, `prd.md`
linje 356 og `prd-notater.md` linje 73 — men konsekvent anonymisert: «et utvalg
selskaper», «et stort finansselskap», «et shippingselskap». Selskapsnavnene,
antallet på ti treff per selskap og eksempelet Infosys finnes ikke i noen av de
fire dokumentene. Ingen treff på «Infosys» overhodet.

**Vurdering: bør berges som måledokumentasjon, ikke som brieftekst.**
Anonymiseringen i selve briefen er et forsvarlig redaksjonelt valg — briefen
skal ikke henge ut navngitte selskaper. Problemet er at dataene da ikke havnet
noe annet sted. `malinger.md` sier i ingressen: «Alle tall PRD-en bygger på, med
metode og dato, slik at de kan etterprøves eller kjøres på nytt» — og fører for
hver eneste andre måling både metode, dato og rådatareferanse. Medietesten 17.09
står ikke i `malinger.md` i det hele tatt.

Det er den ene målingen som bærer mest vekt i prosjektet: den begrunner hele
premisset om at et symbol ikke garanterer relevans, de tre
usikkerhetskjennetegnene i FR-603 er utledet fra den (PRD linje 458), og
relevanseksperimentet i uke 41 er en oppskalering av den til 50 artikler.
Anbefaling: eget avsnitt i `malinger.md` med selskaper, antall treff, dato og
hva som faktisk ble lest — slik at eksperimentet i uke 41 har et sammenlignbart
utgangspunkt.

---

## Kontrollert og funnet i behold

For å vise hva gjennomgangen har dekket, og at funnene over ikke er et utvalg:

| Innhold i utkastene | Hvor det er ivaretatt |
|---|---|
| «omtrent 30–40 likvide aksjer» | Bevisst erstattet av 15, utledet av kvoten — brief «Data og kilder», `prd-notater.md`, `malinger.md` |
| «10–30 norske aksjer» som brukerbeskrivelse | `product-brief.md` linje 16, `prd.md` linje 26 |
| «omtrent fem minutter om morgenen» | Brief linje 8 og suksesstabell; PRD seksjon 1 og seksjon 7 |
| Signalstyrke er ikke en anbefaling om kjøp/salg | Brief linje 34; NFR-06 |
| Signalstyrke = hvor kraftig kriteriene slår ut; retning = positiv/negativ/blandet | Brief linje 28; FR-703/FR-704, FR-103 |
| KI-laget kan slås av, appen fungerer uten | Brief linje 32; FR-601, FR-602, NFR-04 |
| Treg eller feilende modell tar ikke ned hovedflyten | Brief linje 32; NFR-04 |
| Usikkerhet vises i stedet for at modellen gjetter | Brief linje 30; FR-603 |
| Originalkilde synlig | Brief linje 30; FR-203 |
| Utbyttejusterte kurser i historiske sammenligninger | `prd-notater.md` linje 53; FR-406, FR-407, PRD linje 502 |
| Kommende finansielle hendelser når data finnes | Brief omfang; FR-203, seksjon 6 |
| «Vi har ingen teknisk moat» / datakildene er åpne for alle | Brief linje 44 |
| Forklarbarhet før presisjon | Brief linje 52; PRD linje 484 og motmål |
| Ikke mål for hvor godt signalene treffer markedet | Brief linje 71; PRD motmål |
| Ingen brukerundersøkelse gjennomført | Brief linje 58 |
| Gruppen bruker løsningen jevnlig og logger feil | Brief «Adopsjon»; PRD seksjon 7 |
| Minst én person utenfor gruppen gjennomfører hovedflyten | Brief «Brukerutfall»; PRD seksjon 7 |
| Hele universet hentes uten manuelle mellomsteg | Brief «Kvalitet»; NFR-01, NFR-02 |
| Norsk i v1, flere språk senere | Brief; NFR-05, omfang |
| Rettigheter, personvern og regelverk ved kommersiell versjon | Brief linje 79 og 85; PRD linje 77 |
| Veien mot personlig portefølje / markedsassistent | Brief Vision |
| Alt i «Utenfor v1» (kontoer, varsler, betaling, mobil, megler, fundamentalmodell, intradag, statistisk studie) | Brief omfang; PRD seksjon 2 |

Én detalj er strammet bort uten at den regnes som funn: utkastene skriver at
gruppen «registrerer feil **og forbedringspunkter** underveis», mens brief og
PRD skriver «logger feil». Forskjellen er reell, men for liten til å bære et
eget punkt.

---

## Mønsteret, oppdatert

De seks berget detaljene forsvant alle i språkvasken mellom
`claude-utkast.md`/`chatgpt-utkast.md` og `sprakvasket-korrigert.md`. De sju nye
fordeler seg annerledes, og det er verdt å merke seg:

- **Funn 7, 10, 11 og 12 overlevde språkvasken.** De står i alle fire utkast,
  også `endelig-kandidat.md`, og forsvant i steget fra endelig kandidat til
  levert brief — altså i selve forkortingen, ikke i språkvasken.
- **Funn 8, 9 og 13 forsvant senere igjen**, i omleggingen fra medienyheter til
  NewsWeb-meldinger. Der er årsaken en annen: innholdet ble ikke strammet bort,
  det mistet sin kontekst da kilden ble byttet, og ble aldri oversatt til den
  nye.

Tiltaket i `korreksjon-til-brief.md` — diff mot forrige versjon etter hver
omskriving, med blikk for krav som er borte — dekker den første gruppen. Den
andre gruppen krever noe annet: **når en kilde eller et premiss byttes ut, må
kravene som hang på det gamle premisset gjennomgås ett for ett og enten
oversettes eller avskrives eksplisitt.** Funn 8 og 9 er begge krav som stilltiende
falt bort fordi kilden endret seg, ikke fordi noen bestemte at de skulle bort.
