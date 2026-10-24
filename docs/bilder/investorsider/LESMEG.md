# Investorsidene i demoen – tegninger og oppsett (story 3.4h)

Laget av rådet i chatten 24.10.2026 etter gruppens svar kl. 11:58, 12:01, 12:37,
12:39, 12:51, 13:02 og 13:03. Tegningene er SVG laget av KI og merkes
«Illustrasjon laget av KI» på siden. Humoren handler om navnet eller bransjen,
aldri om kurser eller kjøp og salg (NFR-06).

## Innhold

- `svg/` – 15 tegninger, én per oppdiktet selskap, `viewBox="0 0 420 300"`, med
  `<title>` og `<desc>` på norsk. Ingen eksterne filer. Teksten i tegningene er
  bare korte formler og merker (E = mgh, y = sin(x), NPK, 99 %, NY, backup).
- `forhandsvisning/` – slik siden er tenkt å se ut, ett PNG per selskap. Skriftene
  i forhåndsvisningene er de samme som foreslås under.
- `bobler.json` – plassen til snakkeboblen og halen for hvert selskap, målt i
  forhåndsvisningen.

## Oppsettet på siden

- **Øverst:** lenken «Tilbake til ‹navn›» til aksjesiden, i samme stil som
  lenken «Markedsoversikt» på aksjesiden (`a.tilbake`).
- **Logo:** sirkel 116 px med 4 px kant i Blekk `#16181D`, en gul ring innenfor
  (`#F2B53A`), bransjesymbolet fra appen (designutdraget §12) øverst og symbolet
  under, i selskapets skrift.
- **Navn:** 50 px i selskapets skrift. Under: bransjesymbolet og «‹Bransje› · Demo Børs».
- **Tegningen:** 560 × 400 px, på samme sted på alle sidene: rett under
  overskriften og venstrejustert (gruppens svar kl. 13:02). Full bredde på smal skjerm.
- **Snakkeboblen:** hvit, 3,5 px kant i Blekk, runde hjørner 22 px, IBM Plex Sans
  600, 22 px. Den står nær den som snakker, og halen er 34–50 px lang (gruppens svar
  kl. 13:02). Halen går ut fra kanten av boblen som er nærmest den som snakker, og
  den hvite flaten dekker kanten der halen går ut. Boblen dekker aldri tekst i
  tegningen, overskriften, KI-merket eller teksten nederst. Plassen står i
  `bobler.json`. På smal skjerm står boblen under tegningen.
- **KI-merket:** «Illustrasjon laget av KI» rett under tegningen, på samme sted på
  alle sidene (gruppens svar kl. 13:02).
- **Nederst:** «Oppdiktet selskap i demoen. I den ekte versjonen åpner knappen
  selskapets egen investorside i en ny fane.»
- **Ikke vannmerke** (gruppens svar kl. 12:51).

I forhåndsvisningene er det sjekket at tegningen står på samme sted i alle 15, og
at ingen tekst overlapper.

## Hvordan man kommer tilbake

Investorsiden i demoen er en vanlig side i appen og åpnes i samme fane. Man kommer
tilbake med lenken øverst eller med nettleserens tilbakeknapp. Det er ikke noe
vindu å lukke. I den ekte versjonen åpner knappen selskapets egen investorside i en
ny fane, slik alle lenker ut av appen gjør (avgjort kl. 11:48). Appen står igjen i
den første fanen.

## Skriftene

Appens to skrifter, IBM Plex Sans og Newsreader, og tre nye med åpen lisens:
Inter Display (OFL), Lora (OFL) og Liberation Mono (OFL). De nye lagres i
`src/static/fonts/` med lisensfila og føres i `docs/kilder-og-rettigheter.md`, så
appen ikke henter noe utenfra.

## De 15

| Symbol | Navn | Bransje | Skrift | Slagord | Fil |
|---|---|---|---|---|---|
| BRFE | Brattfjell Energi | Energi | Inter Display 900, store bokstaver | «Potensiell energi: vi har mye av den.» | `brfe.svg` |
| HVDO | Havdyp Olje | Energi | Lora 700 | «Dypere enn rekursjon uten stoppbetingelse.» | `hvdo.svg` |
| NLYS | Nordlysfeltet | Energi | Inter Display 200, store bokstaver, sperret 3 px | «Grønt lys lenge før RGB.» | `nlys.svg` |
| SLVP | Sølvbank Petroleum | Energi | Newsreader 600 | «Hver dråpe teller. Vi teller fra 0.» | `slvp.svg` |
| FJSB | Fjellheim Sparebank | Finans | Lora 500, kapitéler | «Renters rente, med utsikt.» | `fjsb.svg` |
| TRHF | Trygghavn Forsikring | Finans | IBM Plex Sans 600 | «Vi har backup av backupen.» | `trhf.svg` |
| VRDS | Varde Systemer | Industri | Liberation Mono 700 | «Nylig notert: stabelen er ny, men den står.» | `vrds.svg` |
| KVST | Kvitstein Mineral | Materialer | Lora 400, store bokstaver, sperret 4 px | «Grunnleggende stabil. pH 7.» | `kvst.svg` |
| JGRD | Jordgrøde Gjødsel | Materialer | IBM Plex Sans 500 | «Laster … 99 % grønt.» | `jgrd.svg` |
| BLGT | Bølgetopp Tankers | Shipping | Inter Display 800 kursiv | «Vi rir på sinusbølgen.» | `blgt.svg` |
| LSTF | Lastfjord Container | Shipping | Liberation Mono 400, store bokstaver | «Perfekt stablet, hver gang.» | `lstf.svg` |
| SGNT | Signalnett | Telekom | Inter Display 700 | «Fem streker, null buffering.» | `sgnt.svg` |
| LKSV | Laksevik Sjømat | Sjømat | Lora 600 kursiv | «Svømmer oppstrøms, som en god pull request.» | `lksv.svg` |
| TROY | Tareøy Havbruk | Sjømat | IBM Plex Sans 400, store bokstaver, sperret 2 px | «Ikke en trojaner. Bare tare.» | `troy.svg` |
| MTFJ | Matfjord Merkevarer | Konsum | Newsreader 72pt 500 | «404: Varene ble ikke funnet.» | `mtfj.svg` |

Navnet skrives aldri med små bokstaver. Det har alltid stor forbokstav, slik det
står i resten av appen (gruppens svar kl. 13:03). Fem av navnene vises med bare
store bokstaver som en del av skriften. Symbolet i logoen har alltid store bokstaver.

## Tilgjengelighet

Tegningen settes inn med `alt` lik teksten i `<desc>`, eller som dekor med tom
`alt` når slagordet står som tekst ved siden av. Slagordet i boblen er vanlig
tekst, ikke en del av bildet. Halen er pynt (`aria-hidden="true"`). Kontrasten i
boblen og teksten er Blekk på hvitt.
