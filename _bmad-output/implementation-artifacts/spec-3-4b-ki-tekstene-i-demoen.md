---
title: 'Story 3.4b: KI-tekstene i demoen'
type: 'feature'
created: '2026-10-18'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '5d5dc87'
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
  - '{project-root}/docs/kvalitetssikring.md'
---

## Intent

**Problem:** demoen har ingen KI-tekst, så faglærer og sensor ser ikke hva KI-laget gjør uten Ollama. Story 3.4b i `epics.md` (gruppens beslutning 05.10 kl. 16:53, og svaret 17.10 kl. 22:06 om når den bygges).

**Grunnlaget:** instruksjonen 18.10 kl. 19:51. PR-en flettes når vilkårene i steg 4 i instruksjonen holder.

## Kontrollpunktene fra storyen

- Demoen får ferdige KI-tekster, laget med Gemma og merket med modellen.
- De ferdige tekstene ligger i en fil i repoet, fordi demobasen aldri ligger der (`AD-9`). Demokommandoen leser fila og skriver tekstene inn i demobasen.
- En test krever at grunnlaget for hver tekst stemmer med demodagen den hører til (FR-602).
- Tekstene består kontrollen i FR-603, og raden har tjenesten, modellen og hvordan modellen kjørte (FR-604, FR-605).
- **Ville feilet hvis:** demoen endret seg, og tekstene ble stående. Da forklarer KI en annen dag enn den siden viser.

## Planen, én commit per punkt

1. a) Tekstene: `src/demo_ki.py` lager dem én gang for siste demodag (`SLUTTDATO`), for hver demoaksje med en vurdering den dagen, med `lag_ki_tekster` fra hentingen (grunnlaget, prompten versjon 2, kontrollen og raden), klokka satt til demodagen kl. 21:30 og en demobase i en midlertidig mappe. Radene lagres med et avtrykk av grunnlaget i `src/demo_ki_tekster.json`.
2. b) Demoen: `demo.py` leser fila og skriver radene i KI-loggen i demobasen. «Status» i README-en og «Hva er demoen?» i `docs/hjelp.md` sier at demoen har KI-teksten.
3. c) Testene i `tests/test_demo_ki.py`, og mutantene.

## Avgjort i spesifikasjonen

- **Navnene:** modulen er `src/demo_ki.py`, og fila er `src/demo_ki_tekster.json`. Fila ligger under `src/`, så imaget har den (`COPY src/ src/` i `Dockerfile`), og `.dockerignore` holder den ikke ute.
- **Bare siste demodag,** som instruksjonen sier. Storyen sier «de oppdiktede dagene», men aksjesiden viser KI-teksten for dagen den viser, og i demoen er det `SLUTTDATO`. De andre dagene har ingen rader, og siden sier det samme som i den ekte versjonen for en dag uten rad.
- **Ingen ny runde (FR-604):** `lag_ki_tekster` kalles én gang. Består en tekst ikke kontrollen, står raden som den ble, og aksjesiden viser grunnen i stedet for teksten, som i appen.
- **Demokommandoen importerer ikke modellen:** `demo_ki.py` importerer `ki_tekst`, `ki_lokal` og `demo` bare inne i funksjonen som lager tekstene. Demokommandoen bruker bare lesingen, så den importerer verken `requests` eller Ollama.
- **Lekkasjesjekken i morgensjekken** flagger hver sporede `.json` utenfor `.claude/` og `_bmad/`. `src/demo_ki_tekster.json` får et unntak med akkurat den stien. Fila har oppdiktede tall og tekster om dem, ikke rådata fra kildene (regel 16).

## Boundaries

- Ingen kall til EODHD: ingen API-kall utover kvotesjekken i regel 15, og `src/fetch_prices.py` kjøres ikke.
- `data/db/ose.db` og `data/db/demo.db` røres ikke (regel 22). Demobaser bare i midlertidige mapper.
- Tekstene lages med Gemma i Ollama på denne maskinen, én gang. Ingen test kaller Ollama.

## Avgjort underveis

- **Ordlista** (gruppens svar kl. 20:08): ordlista i `designregler.md` §4 gjelder vår tekst, ikke KI-teksten, til prompten får den i versjon 3. Testene for ordlista i `test_demo.py` og `test_hjelpetekster.py` tar ut bare avsnittet `<p class="ki-tekst">`, høyst ett, og bare på aksjesiden. Tekstene står som de ble (FR-604).
- **Kjøringen 18.10 kl. 19:54–19:56:** 13 rader, alle 13 besto kontrollen. `gemma4:e4b` (`dc35e8d9c606`) i Ollama 0.35.1, på gpu, seed 42 og temperatur 0. Tiden per tekst var 0,7–75,1 s, i alt 92,2 s, og den første lastet modellen. Tiden står bare i utskriften fra kjøringen, ikke i fila.

## Åpent punkt til gruppen

- **Kontrollen i FR-603 slipper gjennom en feil retning skrevet som «Dette signalet er Positivt».** Funnet da mutant K2 ble laget: `kontroller("Dette signalet er Positivt, fordi alle sjekkene ga et positivt utslag.", grunnlaget for BRFE)` gir `besto=True`, selv om retningen er Negativ. «Retningen er Positiv» blir fanget. Hullet er i `ki_kontroll.py` fra før, og gjelder også den ekte versjonen. Alle de 13 tekstene i demoen har riktig retning, sjekket for hånd. Ikke rettet her, fordi det endrer kontrollen for alle tekster.

*Lagt til 2026-10-18 (gruppens svar kl. 21:03):* hullet rettes i spesifikasjonen 10.2d under story 10.2, før byggestoppen mandag 19.10 kl. 20:40, så uka med logget drift går med den rettede kontrollen.

## Mutantene

Én om gangen med `-x` på `tests/test_demo_ki.py`, i en fersk klon med `core.autocrlf=false`, med kopi av fila før og sha256 mot HEAD etter hver, og `git status` tom etter hver. K1–K3 er fra instruksjonen. K4–K6 er for funnene med dom medium. Alle seks ble fanget på `c06e8e4`, og K1–K3 også på `c0aefc6`:
- K1, et grunnlag for BRFE som ikke stemmer med demoen (trend 0 og styrke 2), med avtrykket regnet på nytt, så fila er gyldig: `test_grunnlaget_stemmer_med_demodagen`.
- K2, teksten for BRFE byttet med «Dette er et kjøpssignal.», merket bestått: `test_hver_tekst_demoen_viser_bestaar_kontrollen_slik_den_er_naa`. Første forsøk brukte «Dette signalet er Positivt …», som består kontrollen (se det åpne punktet), og var ikke en riktig mutant.
- K3, demokommandoen uten å skrive KI-radene: `test_skriver_radene_uten_nett_og_uten_ollama`. Første forsøk på `c06e8e4` traff ikke, fordi koden var endret, og ble kjørt på nytt fra en skriptfil.
- K4, `lag_tekstene` skriver fila også etter en kjøring som ikke er hel (BH4, ECH1): `test_en_kjoering_som_ikke_er_hel_skriver_ikke_fila`.
- K5, en ødelagt fil stopper demoen (BH2, ECH3): `test_en_oedelagt_fil_gir_en_demo_uten_ki_tekst`.
- K6, `maskinvare` tatt ut av `FELTENE` (BH7): fila kan ikke leses, og fiksturen `radene` gir en feil i `test_grunnlaget_stemmer_med_demodagen`. Testen blir ikke grønn, men det er fiksturen som stopper den, ikke `test_rundtur_gjennom_fila`.

## Gjennomgangen

Gjennomgang 18.10 på diffen `a0afada..c0aefc6`. Linsene var Blind Hunter (BH, 15 funn, bare diffen), Edge Case Hunter (ECH, 10, der ECH8 og ECH9 ikke fant noen feil) og Verification Gap (VG, 14, der VG1, VG3, VG5, VG6, VG7, VG9, VG10, VG13 og VG14 fant kravene oppfylt). Ingen av dem kjørte pytest eller Ollama. Åtte rader har dom medium. Sju er rettet i `c06e8e4` og her, og BH1 er avvist med beviset under.

| # | Funn | Dom | Rute |
|---|---|---|---|
| ECH1, BH4, VG4 | `lag_tekstene` skrev over fila uten å sjekke kjøringen, og ikke atomisk | medium | patch: fila skrives bare etter en hel kjøring, via `.ny` og `os.replace`. K4 |
| BH2, ECH3 | En ødelagt eller manglende fil stoppet hele demoen, også `demo-lag` i compose | medium | patch: demoen lages uten KI-tekst og sier hvorfor (NFR-04). K5 |
| BH3 | Demoen sjekket ikke dato, symbol eller antall | medium | patch: `sjekk_radene`, og alle radene må skrives |
| BH7 | Rundturen kunne ikke oppdage et felt som falt bort | medium | patch: `FELTENE` mot feltene i `KIRad`, og radene mot fila tegn for tegn. K6 |
| BH8 | Testen lappet `ki_lokal`, som demoen ikke importerer, og sammenlignet bare tre felt | medium | patch: underprosessen bygger en demobase og sjekker importene etterpå, og hele raden sammenlignes |
| ECH2, BH10 | To tester krevde at BRFE besto, og ingen test viste siden med en tekst som ikke besto | medium | patch: testene tåler FR-604, og en ny test viser grunnen i stedet for teksten |
| VG12 | Mutantene var ikke ført | medium | patch: over, og i Utført-linja |
| BH1 | Commit a skulle kalle `med_ki`, som kom først i b | medium | avvist: `git show e8b8137:src/demo_ki.py` kaller `lag_demobase(base, skriv=...)` uten `med_ki`, og `med_ki=False` kom i `6dd1eaa`. Commit b har det instruksjonen kaller punkt b, og testene som måtte følge |
| BH5 | Rader som ikke gjelder en aksje, kunne stoppe kjøringen | low | patch: bare `slag == AKSJE` |
| BH6, ECH4 | Docstringen lovet mer av avtrykket enn det kan | low | patch |
| BH11 | Ordlista ble unntatt uten å telle avsnittene | low | patch: høyst ett, og bare på aksjesiden |
| BH12 | Escapingen var ikke prøvd med farlige tegn | low | patch: `markupsafe.escape` og en test med `<script>`, `&` og `'` |
| BH13, ECH5 | `fra_json` og `les_radene` godtok for mye | low | patch: format som heltall og `utf-8-sig`. Feil typer gir `UgyldigKIRad`, som også er en `ValueError` og fanges av demoen |
| ECH7 | CI sjekket ikke KI-teksten i demoen | low | patch: utskriften fra `demo-lag` og «Laget av KI» på `/aksje/BRFE` |
| BH9 | `utenfor_maalingen=False` står fast i testen | low | avvist: `lag_ki_tekster` bruker samme verdi (`ki_tekst.py`, `lag_ki_rad(... ki_grunnlag(vurdering, utenfor_maalingen=False) ...)`) |
| BH14 | Modulen lastes to ganger som skript | low | avvist: ufarlig, og `main` fanger `UgyldigDemoKI` fra samme modul |
| BH15, ECH8 | Unntaket i morgensjekken | low | avvist: gjelder bare den ene stien, og nøkkelsøket kjøres på fila |
| ECH6 | `les_radene` binder standardstien når den defineres | low | avvist: testene lapper `demo.les_radene` |
| ECH9 | Regexen for avsnittet | low | avvist: ingen feil, teksten er escapet, så `</p>` kan ikke stå i den |
| VG2 | Tiden per tekst kan ikke etterprøves | low | avvist: den står i utskriften og i «Avgjort underveis» |
| VG8 | «Ferdig» før PR-en er flettet | low | avvist: regelen i spesifikasjonen for 3.4 sier at den som fletter, flytter saken, og det gjøres i PR-en som fletter |
| VG11 | Spesifikasjonen har «siste demodag», storyen «de oppdiktede dagene» | low | avvist: begrunnet under «Avgjort i spesifikasjonen» |
| ECH10 | `sprint-status.yaml` sier `backlog` for 3-4b | low | utsatt: settes til done etter flettingen (steg 4) |

*Lagt til 2026-10-18 (hele testsettet på `c61266a`):* `test_konsumentene.py::test_bare_aapne_base_kobler_til_basen` feilet. `lag_tekstene` koblet til demobasen med `sqlite3.connect`, men bare `aapne_base` i `lagring_sqlite.py` skal gjøre det (story 2.1b, K2). Rettet: `lag_tekstene` bruker `aapne_base`.

*Lagt til 2026-10-18 kl. 20:55:* PR #69 er squash-flettet i `ab81d3f`, låst til head-en `8d632b0`, der main var flettet inn. CI var grønn på head-en (39156153956), også demoen med compose og sjekken av KI-teksten, og på main (39156267219). Triagen står som kommentar i PR #69.
