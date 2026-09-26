# AI-prompts – IBE160

Denne mappen brukes til å lagre viktige KI-prompts og arbeidsøkter som senere kan brukes som dokumentasjon i refleksjonsrapporten.

## Hva bør lagres?

Det er ikke nødvendig å lagre hvert eneste korte spørsmål. Lagre først og fremst prompts eller samtaler som:

- påvirket krav, design eller arkitektur
- førte til kode eller større endringer
- ble brukt til testing eller feilretting
- ga feil eller dårlige forslag som dere måtte oppdage og rette
- førte til en viktig beslutning
- viser forskjeller mellom Claude Code, ChatGPT og Codex
- er nyttige eksempler på hvordan KI påvirket arbeidsprosessen

## Filnavn

Bruk gjerne:

`ÅÅÅÅ-MM-DD-navn-tema.md`

Eksempler:

- `2026-09-16-marian-product-brief.md`
- `2026-09-20-joakim-database.md`
- `2026-10-02-begge-debugging.md`

## Instruksjoner til byggeøktene (regel 18)

*Lagt til 2026-09-24.* *Endret 2026-09-26, som regel 18 i `CLAUDE.md`
(`77a9d1c`).* Hver instruksjon lagres ordrett, også når den skrives rett inn, i
`docs/ai-prompts/<ÅÅÅÅ-MM-DD>.md`, én fil per dag, **før** den utføres.
Formatet:

````markdown
## 22:05

```text
<instruksjonen, ordrett, med sluttmarkøren når den er limt inn>
```

**Utført:** <commitene>. <utfallet i én eller to setninger>.
````

- Klokkeslettet er når instruksjonen ble lagret, i norsk tid.
- Linjen «Utført» legges til etterpå, under blokken. Blokken selv endres ikke.
- Ingen rådata eller nøkler i fila (regel 16 i `CLAUDE.md`).
- **Lesing før commit** *(avgjort av Marian 2026-09-24)*: gjelder ikke dagsfilene
  etter regel 18. Marian leser hver instruksjon når hun limer den inn, så kravet
  er oppfylt der. Før hver commit sjekker økta selv at fila ikke inneholder
  rådata, nøkler eller personopplysninger om andre enn Marian og Joakim. For
  instruksjonene fra 21.–24.09 som hentes inn i story 9.2, gjelder lesingen
  før commit som før.
- Dagsfilene har frontmatter, som andre dokumenter under `docs/` (regel 4).
- Filnavnkonvensjonen under gjelder andre prompts og samtaler, ikke disse.

## Arbeidsmønsteret

*Lagt til 2026-09-26, story 9.3.* Arbeidet går mellom tre deler:

- **Rådet** er en Claude-økt i Claude-appen som skriver instruksjonene og
  vurderer resultatene. Først hadde den ikke tilgang til repoet
  (`docs/reflection-log.md`, 20.–21.09). Fra 23.09 kl. 20:03 leser den det
  offentlige repoet gjennom sin egen kopi. Den skriver, committer og pusher
  aldri, og den ser ikke `data/`, `.env` eller noe annet som bare ligger på
  Marians maskin. Kilden for tilgangen er rådet selv, i instruksjonen kl. 20:43
  i dagsfila for 26.09.
- **Byggeøkta** er Claude Code på Marians PC, med tilgang til repoet og
  `data/`. Den utfører instruksjonene, sjekker påstander mot repoet (regel 3),
  stopper når noe ikke stemmer, og committer og pusher.
- **Marian og Joakim** er reléet mellom dem. Vi leser hver instruksjon før vi
  limer den inn, den lagres ordrett (regel 18), og vi avgjør.

| Hva | Hvem avgjør | Kilde |
|---|---|---|
| Ingenting bygges før vi har sagt fra | Vi | Regel 9 i `CLAUDE.md` |
| En plan vises og godkjennes før bygging | Vi | Regel 2, og planinstruksjonene i dagsfilene, for eksempel 1.4b, 1.4c og 1.5 i `2026-09-25.md` |
| Flettingen til `main` venter på ja | Vi | Instruksjonene, for eksempel «Før grenen flettes inn: stopp og vis oss resultatet» (byggeinstruksjonen for 1.4b, kl. 17:01 i `2026-09-25.md`) |
| Vilkår og datakilder | Vi | `docs/kilder-og-rettigheter.md`, «Beslutningen gruppen har tatt i mellomtiden» |
| Merkingen i relevanseksperimentet, for hånd og uten KI | Vi | `relevanseksperiment.md` §3 og §7, og story 9.4 i `epics.md` |
| En påstand kontrolleres i økta som har kilden | Byggeøkta | Regel 3, og tiltaket fra 20.09 i `docs/reflection-log.md` |

**Hvorfor dette mønsteret.** Rådet har ikke skrevet det det kontrollerer, og
ser derfor arbeidet utenfra. Byggeøkta har tilgangen, så det er der påstander
sjekkes. Og ingenting skjer uten at en av oss har lest det og limt det inn.

**Tilfeller begge veier:**

- *Rådet tok feil, og feilen ble fanget.* Rådet oppga `legal@oslobors.no` som
  adresse til Euronext. Vilkårene oppgir en annen, og den ble rettet før
  sending (PRD-memloggen, 21.09). «Basen er gjenoppbyggbar» kom også fra rådet,
  og ble funnet ved å lese FR-408 helt ut (arkitekturmemloggen, 22.09).
- *Byggeøkta fanget en faktafeil fra rådet.* 25.09 kl. 23:19 skrev byggeøkta
  ikke raden om hjelpevinduet, fordi to påstander i instruksjonen ikke stemte
  mot repoet. Den rettede instruksjonen kom kl. 23:22 (`2026-09-25.md`).
- *Rådet tok feil og rettet seg selv.* 26.09 gjentok rådet «Eksamen ber om
  KI-bidrag i drift» fra `epics.md` uten å slå det opp. Da det leste
  `docs/innlevering.md`, viste det seg at emnesiden ikke sier det, og
  påstanden ble rettet i `2a96cc0`. Kilden for at rådet gjentok den, er rådet
  selv, i instruksjonen kl. 20:43.
- *Rådet korrigerte byggeøkta.* Byggeøkta skrev EODHD-utkastet med fire
  spørsmål (`0945818`, 20.09). Rådet avgjorde at det skulle sendes ett
  (`docs/reflection-log.md`, 20.–21.09, «Det motsatte gjelder også»). Det var
  en rettet vurdering, ikke en rettet faktafeil.
- *Rådet fant en faktafeil i et dokument.* `begrunnelser.md` §11 sa «over ti
  måneder» om en tabell over 249 handelsdager. Instruksjonen kl. 00:29 i
  dagsfila for 26.09 ba om kontroll, og setningen ble rettet i `b65808d`.
  Setningen kom inn i `a0ffc99` 21.09. Hvem som formulerte den, kan ikke
  avgjøres: instruksjonene fra før 24.09 er ikke lagret ordrett.

## Viktig

Skriv hvem som brukte KI-verktøyet. Git-historikken viser hvem som committed filer,
men promptloggen bør også forklare hvem som gjorde vurderingen og hva dere valgte å bruke.
