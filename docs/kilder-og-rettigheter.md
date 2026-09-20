# Kilder og rettigheter

Oversikt over datakildene OSE Signal bruker eller har vurdert, hva vilkårene sier
om bruken vår, og når vi sist kontrollerte det. Formålet er at kildevalgene skal
være etterprøvbare, ikke bare dokumentert som «vi fant data».

**Premiss for v1:** applikasjonen kjøres lokalt i undervisningssammenheng og
publiseres ikke. Vurderingen gjelder derfor ikke-kommersiell, pedagogisk bruk.

**Men repoet er offentlig.** Kildekoden og planleggingsdokumentene ligger i
`IBE160-2026/G74-lund-osen`, som er åpent tilgjengelig. Applikasjonen er altså
ikke publisert, men arbeidet med den er. Skillet mellom hva som deles og hva som
blir liggende lokalt er derfor et valg vi må ta bevisst — se neste avsnitt.

Sist oppdatert: 2026-09-20

---

## Status per kilde

| Kilde | Brukes til | Vilkår kontrollert | Vurdering |
|---|---|---|---|
| EODHD `/api/eod` | Sluttkurser | 2026-09-19, delvis | Gratisnivå dekker EOD. 1 kall per symbol. |
| EODHD `/api/real-time` | — (forkastet) | 2026-09-19 | Virker, men prissiden sier gratisnivået ikke har det. Ikke bygg på. |
| EODHD `/api/news` | — (forkastet) | 2026-09-19 | Ett ticker per kall, 5–10 kall per forespørsel. For dyrt. |
| EODHD `/api/calendar` | — (utilgjengelig) | 2026-09-19 | HTTP 403: «Only EOD data allowed for free users». |
| Oslo Børs NewsWeb | Selskapsmeldinger | **Ikke kontrollert** | Åpent JSON-API, ferdig tagget med utsteder. Vilkår må sjekkes. |
| E24 RSS | — (forkastet) | 2026-09-19 | Forbyr eksplisitt LLM-input. Se under. |
| NRK RSS | — (vurdert) | Ikke kontrollert | Feeder virker, men generelle nyheter uten finansfokus. |
| Euronext | Finanskalender | Ikke kontrollert | Eneste gratis vei til kalender etter at EODHD falt bort. |
| Alpha Vantage | — (forkastet som hovedkilde) | Ikke kontrollert | Testet mot Oslo Børs, men symbolene var ikke pålitelige nok. Brukt i tidlige tester på gull og sølv. |

---

## E24: forbud mot KI-bruk

E24s RSS-feed inneholder i sitt eget `<description>`-felt en klausul som forbyr
bruk av innholdet som input til språkmodeller. Sitat, hentet 2026-09-19:

> E24 does not permit any unlicensed use of the content referenced in this feed —
> including article headlines, summaries, links, full-text, images, metadata or
> other elements — for the purpose of training, fine-tuning, or evaluating, or
> providing input to large language models (LLMs), generative AI systems, or any
> automated systems that produce derivative or synthetic content.

Dette rammer direkte arkitekturen vi vurderte, der KI skulle avgjøre hvilket
selskap en artikkel faktisk handler om. Kilden er derfor forkastet, ikke fordi den
var teknisk utilstrekkelig, men fordi vilkårene ikke tillater bruken.

Andre norske finansmedier (DN, Finansavisen, Hegnar, Kapital) publiserer ikke
lenger åpen RSS, så spørsmålet om deres vilkår ble ikke aktuelt.

---

## Oslo Børs NewsWeb

```
https://api3.oslo.oslobors.no/v1/newsreader/list?category=&issuer=&fromDate=ÅÅÅÅ-MM-DD
```

Offisielle børsmeldinger. Ett døgn (15.09.2026) ga 102 meldinger fra 73 utstedere.
Hver melding har `issuerSign`, `issuerName`, `category`, `publishedTime` og `title`.

Tre forbehold vi må følge opp:

1. **Vilkårene er ikke kontrollert.** API-et er udokumentert og er backend-en til
   Oslo Børs' egen nettside, ikke et publisert utvikler-API.
2. **Ingen garanti for stabilitet.** Det kan endres eller stenges uten varsel.
   Vi lagrer derfor rådata lokalt fra første henting.
3. **Oslo Børs eies av Euronext.** Vilkårene for NewsWeb og for finanskalenderen
   henger derfor trolig sammen, og må kontrolleres under ett.

Meldingene er allerede knyttet til utsteder. Det betyr at KI ikke brukes til å
avgjøre hvilket selskap en melding gjelder — den jobben gjør `issuerSign`. KI
brukes først etter at kategorifiltrering i vanlig programkode har luket bort
støyen, og da til å forklare innholdet på norsk.

---

## Hva vi publiserer, og hva vi ikke publiserer

Besluttet 2026-09-20, da det ble bekreftet at repoet er offentlig i
IBE160-organisasjonen.

Skillet går mellom **aggregert statistikk utledet av en kilde** og **selve
datasettet**.

| Publiseres i repoet | Blir liggende lokalt |
|---|---|
| Median daglig omsetning per symbol | Kursseriene fra EODHD |
| Kategorifordelinger i meldingsbildet | Meldingene fra NewsWeb |
| Kalltall, kvoteforbruk og måleresultater | Alt innhold i `data/` |
| Metodebeskrivelser og konklusjoner | |

`data/` ligger i `.gitignore`, sammen med `.env`. Rådata og API-nøkler er derfor
ikke eksponert.

**Begrunnelsen:** sammendragsstatistikk er ikke databasen. At medianomsetningen
for et symbol var 34,7 MNOK over en gitt periode, er et resultat vi har regnet
ut — det gjenskaper ikke kursserien det er regnet på, og det setter ingen i
stand til å omgå kildens egne vilkår. Det samme gjelder at en kategori utgjorde
28,9 % av meldingene i en måleperiode.

**Dette er en forsvarlig posisjon, men den skal stå som et bevisst valg.**
Slik det er nå, følger skillet av at `data/` tilfeldigvis ble gitignorert tidlig
i prosjektet. Det er ikke godt nok som begrunnelse. Regelen er herved skrevet
ned, og den gjelder også for filer vi lager senere: et måleresultat kan
publiseres, et datasett kan det ikke.

Posisjonen er ikke en erstatning for vilkårskontrollen. Den sier hva vi gjør i
mellomtiden, ikke at vilkårene tillater det.

---

## Å følge opp

- [ ] **Euronext samlet:** kontrollere bruksvilkårene for NewsWeb-data og for
      finanskalenderen i samme runde. Oslo Børs er en del av Euronext, så de to
      kildene deler sannsynligvis vilkår.
- [ ] Kontrollere Alpha Vantage sine vilkår for ikke-kommersiell bruk
- [ ] Lese EODHDs fullstendige ToS, ikke bare prissiden
- [ ] Vurdere vilkårene på nytt dersom applikasjonen skal publiseres
- [ ] **Kontrollere at skillet over holder mot EODHDs og NewsWebs faktiske
      vilkår.** Posisjonen «sammendragsstatistikk er ikke databasen» er vår egen
      vurdering, ikke noe kildene har sagt. Tas i samme runde, frist 2026-09-27
