---
title: 'Story 2.12: Velge og bytte aksjer, «Dine egne aksjer» og «Din egen liste»'
type: 'feature'
created: '2026-11-08'
status: 'in-progress'
route: 'dispatch'
baseline_commit: '4594dfa2'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/_bmad-output/planning-artifacts/designutdrag-2026-11-08.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-2-11-lista-leses-fra-basen.md'
---

Skrevet 08.11 i instruksjonen kl. 14:05 (`docs/ai-prompts/2026-11-08.md`). Gruppen har sagt at Claude Code bygger etter forslagene i spesifikasjonene, og at de gås gjennom før flettingen (svaret 08.11 kl. 12:32). Storyen bygger på grenen for 2.11 og tas i bruk fra mandag 09.11 (svaret kl. 11:57).

## Spørsmål til gruppen før flettingen

Hvert spørsmål har et forslag. Forslaget er det som er bygget.

1. **Hva er en «egen» aksje?** *Forslag:* en aksje i lista som er tatt inn fra et ønske på siden. Den merkes «Egen» i tabellen og står under «Dine egne aksjer». «Ikke blant de 15 i `AKSJEUNIVERS`» ville gjort alle selskapene i demoen til egne. En av de 15 som er byttet ut og tatt inn igjen fra siden, er egen.
2. **Hvor kommer lista over Oslo Børs fra?** Avgjørelsen 22.10 kl. 23:14 sier at hentekommandoen lagrer den i basen, og at siden bare viser tickere som står der. *Forslag:* en ny tabell `boersliste`, fylt med kommandoen `uv run python src/fetch_prices.py --les-boerslista`, som leser `data/proever/symbolliste-OL-2026-10-22.json` uten kall. Bare typen «Common Stock». Fila committes ikke (regel 10). Mandag kjører gruppen kommandoen én gang før aksjer kan velges.
3. **Ønsket.** *Forslag:* webserveren skriver bare i en ny tabell `oenske` (AD-3): følg, fjern eller bytt, med tickeren, navnet og bransjen brukeren valgte. Kveldens henting tar ønskene i bruk før den leser lista, og er fortsatt eneste skriver av `aksje`, kurser og vurderinger. Et ønske som ikke er tatt i bruk, kan angres, og da slettes raden.
4. **Bransjen.** *Forslag:* brukeren velger en av de 13 i dialogen (svaret kl. 11:57), og ingen forslag (NFR-06). Triggeren fra 2.11 avviser alt annet.
5. **Taket.** *Forslag:* aksjene i lista pluss ønskene om å følge, minus ønskene om å fjerne, er høyst 18. Den nittende avvises med «Lista er full. Fjern en aksje for å følge en annen.», både på siden og i porten.
6. **En ticker som ikke gir rader.** *Forslag:* hentingen tar aksjen inn, og gir svaret ingen rader, slettes raden i `aksje` igjen (den har ingen kurser), ønsket merkes avvist, og utskriften sier det.
7. **Omsetningen.** *Forslag:* den siste målingen i `omsetning` (2.13). Under 32 MNOK, eller ikke målt, gir merket «Utenfor målingen» i grått, som utdraget. Er den ikke målt, står «Omsetningen er ikke målt ennå …» i dialogen. Hentingen måler den ikke med det samme kallet i denne storyen; det står som åpent punkt.
8. **Dialogene uten JavaScript.** *Forslag:* «Følg en aksje» og «Bytt ut» er egne sider med skjema (`/folg`), som virker med tastatur og uten skript. Tekstene er utdragets.
9. **Steg 2 i «Din egen liste».** Utdraget sier at nøkkelen legges inn når den ekte versjonen startes første gang (avviket i utdraget §2). *Forslag:* som utdraget.
10. **Demoen.** *Forslag:* demobasen får `boersliste` med noen oppdiktede selskaper som kan velges, og valget, «x av 18» og «Dine egne aksjer» virker likt. Demoen henter aldri, så ønsket står som «Venter på henting i kveld etter kl. 22.», og en boks sier det.

11. **Teksten når omsetningen ikke er målt.** Utdraget sier «Den står etter hentingen, som måler den med det samme kallet.», men hentingen måler den ikke, og målingen i 2.13 hopper over aksjene i lista. *Forslag:* teksten sier bare at den ikke er målt og merkes. Å la hentingen måle omsetningen med det samme kallet er en egen endring.

## Intent

**Problem:** lista kan ikke byttes fra siden. Gruppen vil følge så mange aksjer som mulig (svaret 08.11 kl. 11:41 og 11:43), opptil 18, og bytte fra mandag 09.11 (kl. 11:57).

**Avgjørelsene:** story 2.12 i `epics.md` (08.10, tillegget 13.10, beslutningen 16.10 om demoen, 21.10 kl. 16:47 og 18:38 om taket og kallene, 22.10 kl. 23:14 om lista over Oslo Børs), svarene 08.11 kl. 11:41–12:39, og §1 og §2 i `designutdrag-2026-11-08.md`.

## Bygget 08.11 (instruksjonen kl. 14:05)

Bygget på grenen `2-12-velge-og-bytte-aksjer`, i worktreen `G74-lund-osen-2-12`, fra grenen for 2.11 (`4594dfa2`, med rettingene fra `db9e4ab9` og `e34de7e3` flettet inn).

- **Basen:** `src/migrasjoner/0010_valg.sql` med `boersliste` og `oenske`.
- **Porten:** `src/valg.py`: `Valglager` (bare `oenske` skrives), `les_boerslista`, `ta_i_bruk` og `uten_rader` (hentingen), taket, kallene og «Utenfor målingen».
- **Hentingen:** `ta_i_bruk_oenskene` i `src/fetch_prices.py` før lista leses, og `--les-boerslista`, uten kall. En egen aksje uten kurser tas ut kvelden etter, så et nytt forsøk samme kveld fortsatt kan hente den (avvik fra spørsmål 6, som sa samme kveld).
- **Sidene:** «Dine egne aksjer» under tabellen og «Din egen liste» i Min liste (`src/templates/_egne.html`), siden «Følg en aksje» og «Bytt ut» (`src/templates/folg.html`), merkene «Egen» og «Utenfor målingen» i tabellen, og rutene `/folg`, `/fjern` og `/angre`, som bare skriver `oenske`. Hjelpen bak «?», `docs/hjelp.md` («Hvordan følger jeg andre aksjer?») og README-en med bildet `docs/appen/din-egen-liste-demo.png`.
- **Demoen:** fem oppdiktede selskaper på «Demo Børs» som kan velges, og to målinger av omsetningen, én over og én under 32 MNOK (`DEMOBOERSEN` og `DEMOMAALT` i `src/demo.py`).
- **Avvik:** en egen aksje er en aksje tatt inn fra et ønske på siden, ikke «ikke blant de 15» (spørsmål 1, rettet før byggingen). Et ønske som venter, telles med i «N egne». Hentingen måler ikke omsetningen med det samme kallet; teksten i dialogen sier det likevel, ordrett fra utdraget, og det står som åpent punkt. Lenken «Åpne eodhd.com» er tekst, fordi sidene ikke har lenker ut av appen (`test_utseende.py`).
- **Tester («Ville feilet hvis» i hver):** `tests/test_valg.py`.
- **Hele settet,** alene: kl. 17:01:58–17:12:26 ga 14 feil (versjonen 10 i ni tester, SQL i `app.py`, en stiplet kant, «kl.» som en setning i hjelpen, vinduene på oversikten og den sjuende malen), rettet. Kl. 17:15:45–17:25:33: 4633 bestått, 24 hoppet over og 0 feilet. Bildene ble tatt på nytt: Min liste og oversikten ved 390 px viser de nye delene, og de fem andre er byte for byte de samme.

## Gjennomgangen 08.11 (Blind Hunter, Edge Case Hunter og Verification Gap)

Tre gjennomganger av `f87c29ea`, i parallell etter hele settet og mutantene: Blind Hunter med bare diffen, Edge Case Hunter og Verification Gap med repoet. Blind Hunter hadde 11 funn, Edge Case Hunter 11 og Verification Gap 12.

**Høy**
- *BH1, ECH1 og VG1, rettet.* Lista kunne få 19 aksjer: «Fjern», så «Følg» til 18, så «Angre» på ønsket om å fjerne. Nå avviser `angre` det når lista da ville fått mer enn 18, og hentingen tar aldri inn mer enn 18: et ønske om å følge med full liste avvises med grunnen (`test_angre_et_oenske_om_aa_fjerne_kan_ikke_gi_19`, `test_hentingen_tar_aldri_inn_mer_enn_18`).
- *VG2 og ECH10, rettet.* «Utenfor målingen» sto bare i tabellen. Nå står merket også på aksjesiden og i børsometeret, med omsetningen og hva signalet er målt på når man peker på det, og dialogen heter «‹navn› er utenfor målingen» med «Velg en annen» når omsetningen er målt og under 32 MNOK.

**Middels**
- *BH2, rettet.* Sjekken av taket og skrivingen er i én transaksjon med skrivelås (`BEGIN IMMEDIATE`).
- *BH3 og ECH2, rettet.* De to ønskene i et bytte peker på hverandre (`par` i `oenske`) og angres sammen (`test_et_bytte_angres_helt`).
- *BH4 og ECH4, rettet.* Hentingen sletter aldri en rad i `aksje`. Har aksjen kurs eller vurdering for dagen, eller kom den inn samme dag, får den `ut` dagen etter, og ingen ønsker rulles tilbake (`test_en_aksje_med_rader_samme_dag_slettes_ikke`).
- *BH5, rettet.* En egen aksje tas bare ut som «ga ingen kurser» når hentingen har prøvd den (den har en rad i `vurdering`).
- *ECH3, rettet.* Ønskene tas bare i bruk på selve børsdagen, ikke i helgen eller om natta etter.
- *BH6 og ECH5, åpent.* En aksje som tas inn igjen, beholder den gamle `inn`, og dagene den var ute, står ikke som «ikke i lista». Det er spørsmål 6 i 2.11 og står åpent til gruppen har svart (regel 25).
- *VG3, rettet.* Treffene i søket viser omsetningen når den er målt, og merket når den er under 32 MNOK.
- *VG4 og BH7, rettet.* Kalltallene regnes i koden, ikke i malen, og testen leser 16, 17 og 3 på siden. Teksten «Den står etter hentingen, som måler den med det samme kallet.» er tatt ut, fordi hentingen ikke måler omsetningen. Den står nå: «Omsetningen er ikke målt ennå, så den merkes «Utenfor målingen».» Det er et avvik fra utdraget (spørsmål 11).
- *VG5, rettet med avvik.* Storyen (tillegget 13.10) sier at en valgt aksje ikke skal stå under «Øvrige aksjer». Utdraget §1, som gruppen valgte 08.11 kl. 12:39, sier at den står i tabellen sammen med de andre, merket «Egen». Bygget etter utdraget, og testen viser merket i tabellen og raden under «Dine egne aksjer» (`test_en_egen_aksje_staar_i_tabellen_med_merket`).
- *VG6, rettet med avvik.* Hjelpen bak «?» har ordene fra utdraget i tre setninger (story 8.0c), uten «kl. 22», fordi «kl.» telles som en setning, og uten «Vil du følge helt andre aksjer, se Min liste.». Den sier nå også at en aksje som ikke er målt, merkes.

**Lav**
- *Rettet:* ECH6 (% og _ i søket), ECH7 (den siste målingen, også med feil, og datoen i Oslo), ECH9 og BH9 (en avvist forespørsel sender tilbake til samme side med aksjen og byttet), ECH11 (en aksje i lista kan ikke følges igjen fra siden), BH10 (docstringen), VG11 (byttet sier antallet i lista), VG8 og BH11 (rutene skriver bare `oenske`, og Origin for `/fjern` og `/angre`).
- *Ført:* BH7 og VG12 («i kveld» står også når ønsket er laget etter kveldens henting eller i helga), BH8 (ingen CSRF-token utover Origin, som stjernen i Min liste), ECH8 (delene står ikke før første henting, når tabellen er tom), VG7 (en ticker uten rader står i lista til kvelden etter), VG9 og VG10 (testene for NFR-06 og demoen er smale).

- **Etter gjennomgangen:** hele settet alene kl. 17:39:18–17:49:44: 4646 bestått, 24 hoppet over og 0 feilet. Alle bildene ble tatt på nytt og er byte for byte de samme som før rettingene.

## Mutantene

På `f87c29ea` åtte (A–H), alle fanget. På `1f936f3a`, etter gjennomgangen, tolv: A 2, A2 1 (angre sjekker ikke taket), A3 1 (hentingen tar inn mer enn 18), B 1, C 4, D 1 (en aksje med rader samme dag får ut samme dag), E 1, F 1, G 1, H 1, I 1 (et bytte angres bare halvveis) og J 1 («Utenfor målingen» mangler i tabellen) test. Alle ble fanget, og hver fil var lik HEAD etterpå (kopi før, sha256 mot HEAD etter).

## Bygget og ikke flettet

Grenen `2-12-velge-og-bytte-aksjer` er ikke flettet. Den bygger på 2.11 (PR #123), som flettes først. Gruppen går gjennom spørsmålene før flettingen, og BH6/ECH5 står åpent som spørsmål 6 i 2.11 (regel 25). Mandag kjøres `uv run python src/fetch_prices.py --les-boerslista` én gang før aksjer kan velges. `index.html` får en konflikt med 10.6 (PR #122), fordi begge legger en del under tabellen; rekkefølgen er «Dine egne aksjer» og så «Børsdagen kort fortalt» (§11 i utdraget 13.10).
