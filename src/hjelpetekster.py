"""Hjelpetekstene bak «?» - story 8.0b.

Ren logikk. Fila leser ingen filer og gjoer ingen kall. Alle tekstene staar
her og ikke i malene, saa et ord kan endres ett sted. Min liste (8.3) skal
bruke de samme.

Tallene som er parametre, hentes fra Parametre og skrives med tall() (regel
21). Da kan ikke hjelpen si én ting mens koden gjoer en annen. Tallene som er
maalinger, staar som egne konstanter med kilden sin.

Hver tekst har kildene sine: en fil i repoet og et sted i den, ordrett, som en
test slaar opp. Teksten sier bare det koden gjoer og det kilden sier, og den
gir ikke raad (NFR-06). Retningen forklares med ordene og symbolene fra
RETNINGSVISNING (FR-704, FR-103), ikke med egne ord.

Tekstene ble godkjent av gruppen 11.10 kl. 11:33, med endringene i
spesifikasjonen. Story 8.0c (godkjent 13.10 kl. 15:36): hvert «?» staar ved
det det forklarer, hver tekst har hoeyst 3 setninger utenom grensene og
skjevhet, og retningen forklares med +1 og -1 (FR-704, rettet 13.10).
"""

from dataclasses import dataclass

from aksjedetalj import INGEN_UTSLAG
from markedsoversikt import RETNINGSVISNING, UKJENT_RETNING
from signalberegning import (
    BLANDET,
    INGEN,
    NEGATIV,
    POSITIV,
    STANDARD,
    Parametre,
    nodvendige_dager,
)
from tallformat import HARDT_MELLOMROM, tall

# Kildene, som stier fra roten av repoet.
PRD = "_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md"
BEGRUNNELSER = "_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/begrunnelser.md"
MAALINGER = "_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/malinger.md"
SIGNALBEREGNING = "src/signalberegning.py"
MARKEDSOVERSIKT = "src/markedsoversikt.py"
AKSJEDETALJ = "src/aksjedetalj.py"
APP = "src/app.py"
INDEX_MAL = "src/templates/index.html"
AKSJE_MAL = "src/templates/aksje.html"

# FR-701: tre sjekker, ingen fjerde.
ANTALL_SJEKKER = 3

# Maalingene bak grensene (malinger.md §7.4 og §9). De er ikke parametre: de
# sier hva grensene ble kontrollert mot.
#
# Grensene som ble maalt, staar for seg og ikke fra Parametre: teksten om
# maalingen sier hvilke verdier som ble kontrollert, og det var disse. En test
# krever at STANDARD er lik dem, saa en ny grense i Parametre stopper testene
# til grensen er maalt og teksten rettet (gjennomgangen av 8.0b).
MAALTE_GRENSER = Parametre(
    noytralsone=0.02, volumfaktor=1.5, volatilitet_vindu=20, volum_vindu=20, terskel=2,
)
MAALTE_BOERSDAGER = 199
MAALTE_AKSJER = 15
MAALT_PERIODE = "fra desember 2025 til september 2026"

# Retningen over de 199 dagene, andel av aksjedagene med utslag
# (malinger.md §7.4, begrunnelser.md §6, rettet 03.10).
ANDEL_POSITIV = 60.0
ANDEL_NEGATIV = 29.5

# Betingelsen for hver retning, med ordene i FR-704 (rettet 13.10: +1 og -1,
# ikke «peker opp» og «peker ned»). Ordet og symbolet foran kommer fra
# RETNINGSVISNING.
_RETNINGSBETINGELSE = {
    POSITIV: "alle sjekkene som slo ut, ga +1.",
    NEGATIV: "alle sjekkene som slo ut, ga -1.",
    BLANDET: "noen av sjekkene som slo ut, ga +1, og noen -1.",
    INGEN: "ingen av sjekkene slo ut, og styrken er 0.",
}


@dataclass(frozen=True)
class Hjelpetekst:
    """En tekst i hjelpevinduet. tittel staar i fet skrift foran teksten,
    og er tom naar teksten er en hel setning.

    kilder er par av (fil, sted): fila fra roten av repoet, og tekst som
    staar ordrett i den.
    """

    tittel: str
    tekst: str
    kilder: tuple[tuple[str, str], ...]


def _retningstittel(retning: str) -> str:
    visning = RETNINGSVISNING[retning]
    return f"{visning.symbol} {visning.tekst}:"


def _vis(verdi: float, slag: str) -> str:
    """Tallet som tekst etter regel 21, eller ValueError hvis det ikke kan
    vises uten aa rundes av. Da ville hjelpen vist en annen grense enn den
    koden bruker, for eksempel «1,3» for en volumfaktor paa 1,25."""
    tekst = tall(verdi, slag)
    tilbake = float(tekst.replace(HARDT_MELLOMROM, "").removesuffix("%").replace(",", "."))
    if abs(tilbake - verdi) > 1e-9:
        raise ValueError(f"{verdi} vises som {tekst!r} med slaget {slag!r}. Rett desimalene i tallformat.py")
    return tekst


def _grensene(m: Parametre) -> str:
    """Grensene som ble maalt, i den rekkefoelgen teksten nevner dem."""
    if m.volatilitet_vindu == m.volum_vindu:
        vinduene = f"de to vinduene på {_vis(m.volatilitet_vindu, 'heltall')} børsdager"
    else:
        vinduene = (f"vinduene på {_vis(m.volatilitet_vindu, 'heltall')} og "
                    f"{_vis(m.volum_vindu, 'heltall')} børsdager")
    return (f"{_vis(m.noytralsone * 100, 'grense')}, {_vis(m.volumfaktor, 'faktor')} ganger, "
            f"{vinduene} og terskelen {_vis(m.terskel, 'heltall')}")


def hjelpetekster(p: Parametre = STANDARD) -> dict[str, Hjelpetekst]:
    """Alle hjelpetekstene, med tallene fra p. Teksten om maalingen bruker
    MAALTE_GRENSER, fordi den sier hva som ble maalt."""
    sone = _vis(p.noytralsone * 100, "grense")
    faktor = _vis(p.volumfaktor, "faktor")
    ma = _vis(p.ma_vindu, "heltall")
    volatilitet = _vis(p.volatilitet_vindu, "heltall")
    volum = _vis(p.volum_vindu, "heltall")
    terskel = _vis(p.terskel, "heltall")
    dager = _vis(nodvendige_dager(p), "heltall")

    tekster = {
        "selskap": Hjelpetekst(
            "",
            "Klikk for å se sjekkene, tallene bak og kursgrafen.",
            ((INDEX_MAL, '<a href="/aksje/{{ rad.aksje.symbol }}">'),
             (AKSJE_MAL, '<p class="maalt">Målt mot'),
             (AKSJE_MAL, 'class="kurslinje"')),
        ),
        "sluttkurs": Hjelpetekst(
            "Sluttkurs:",
            "kursen ved børsens stengning siste børsdag i dataene, uten "
            "utbyttejustering.",
            ((PRD, "| Sluttkurs | `close` for siste børsdag |"),
             (INDEX_MAL, "Sluttkursen er den ujusterte kursen")),
        ),
        # Svar 32 i 8.0d (rettet kl. 13:05): én tekst for oversikten og
        # aksjesiden, og datoene står bare ved endringen på aksjesiden.
        "endring": Hjelpetekst(
            "Endring:",
            "endringen i prosent fra forrige dag med kurs, regnet på "
            "utbyttejustert kurs. Mangler kilden kurser for noen børsdager, "
            "står datoene ved endringen på aksjesiden.",
            ((PRD, "| Endring | Endring i prosent, regnet på "),
             (MARKEDSOVERSIKT, "def endring_i_prosent("),
             (AKSJEDETALJ, "def boersdag_mellom("),
             (AKSJE_MAL, "{% if detalj.endring_med_datoer %}")),
        ),
        "utbyttejustert": Hjelpetekst(
            "Utbyttejustert kurs:",
            "kilden regner kursen om bakover ved hvert nytt utbytte, så et "
            "ordinært utbytte ikke ser ut som et kursfall. Endringen, de "
            f"{ANTALL_SJEKKER} sjekkene og kursgrafen bruker den.",
            ((PRD, "#### FR-701"),
             (SIGNALBEREGNING, "Kildens justerte kurs regnes om bakover ved hvert nytt"),
             (AKSJE_MAL, "Begge linjene er tegnet på utbyttejustert kurs")),
        ),
        "data_hentet": Hjelpetekst(
            # Story 8.0d, PR 2, svar 5: tidspunktet heter «Oppdatert» i stripa.
            "Oppdatert:",
            "når kursene sist ble hentet, i norsk tid. Øverst står det eldste "
            "tidspunktet blant aksjene. En aksje som ble hentet tidligere enn "
            "de nyeste, har sitt eget tidspunkt under navnet.",
            ((PRD, "##### Hvor gamle dataene er"),
             (MARKEDSOVERSIKT, "def sidens_tidsstempel("),
             (MARKEDSOVERSIKT, "def eldre_enn_nyeste(")),
        ),
        "data_hentet_aksje": Hjelpetekst(
            "Data hentet:",
            "når kursene for aksjen sist ble hentet, i norsk tid.",
            ((PRD, "##### Hvor gamle dataene er"),
             (APP, "hentet=post.hentet")),
        ),
        "uten_data": Hjelpetekst(
            "Uten data i denne kilden:",
            "aksjer uten en eneste kurs. De står ikke i tabellen, men navnes "
            "under den.",
            ((PRD, "Aksjer kilden ikke har en eneste kursrad for"),
             (MARKEDSOVERSIKT, "def uten_kurser(")),
        ),
        "signalstyrke": Hjelpetekst(
            "Signalstyrke:",
            f"hvor mange av de {ANTALL_SJEKKER} sjekkene som slo ut, fra 0 til "
            f"{ANTALL_SJEKKER}. Både +1 og -1 teller, så en sjekk med +1 og en "
            f"med -1 gir 2. En aksje med styrke {terskel} eller mer er merket "
            f"«skiller seg ut» i oversikten.",
            ((PRD, "#### FR-703 — Signalstyrke"),
             (PRD, "#### FR-705"),
             (SIGNALBEREGNING, "def finn_styrke(")),
        ),
        "uten_styrke": Hjelpetekst(
            "",
            "Står det «–» med en tekst under i stedet for et tall, finnes det "
            "ingen vurdering for dagen, og teksten sier hvorfor.",
            ((PRD, "| Signalstyrke | Tom |"),
             (MARKEDSOVERSIKT, "GRUNNTEKST"),
             (MARKEDSOVERSIKT, 'IKKE_VURDERT = "ikke vurdert"'),
             (MARKEDSOVERSIKT, 'IKKE_BOERSDAG = "ikke børsdag"')),
        ),
        "retning": Hjelpetekst(
            "",
            "Retningen sier om sjekkene som slo ut, ga +1 eller -1, ikke hvor "
            "kursen går videre.",
            ((PRD, "#### FR-103"),
             (BEGRUNNELSER, "Om de sier noe om kursen videre, er ikke målt (FR-703).")),
        ),
        **{
            noekkel: Hjelpetekst(
                _retningstittel(retning),
                _RETNINGSBETINGELSE[retning],
                ((PRD, "#### FR-704 — Retning"),
                 (MARKEDSOVERSIKT, "_SYMBOL_OG_KLASSE")),
            )
            for noekkel, retning in (
                ("positiv", POSITIV),
                ("negativ", NEGATIV),
                ("blandet", BLANDET),
                ("ingen", INGEN),
            )
        },
        "ukjent": Hjelpetekst(
            f"{UKJENT_RETNING.symbol} {UKJENT_RETNING.tekst}:",
            f"det finnes ingen vurdering for dagen, og grunnen står under "
            f"signalstyrken. Det er ikke en femte retning: «{INGEN}» betyr at "
            f"sjekkene ble regnet uten at noen slo ut.",
            ((PRD, "«Ukjent» er ikke en femte retning i FR-704"),
             (MARKEDSOVERSIKT, "UKJENT_RETNING")),
        ),
        "ukjent_aksje": Hjelpetekst(
            f"{UKJENT_RETNING.symbol} {UKJENT_RETNING.tekst}:",
            f"det finnes ingen vurdering for dagen, og grunnen står under "
            f"«Hvorfor signalet ble ukjent». Det er ikke en femte retning: "
            f"«{INGEN}» betyr at sjekkene ble regnet uten at noen slo ut.",
            ((PRD, "«Ukjent» er ikke en femte retning i FR-704"),
             (AKSJE_MAL, "Hvorfor signalet ble")),
        ),
        "trend": Hjelpetekst(
            "Trend:",
            f"ligger den utbyttejusterte kursen mer enn {sone} over eller "
            f"under snittet av de siste {ma} børsdagene? Over gir +1, under "
            f"gir -1, og innenfor {sone} gir 0.",
            ((PRD, "#### FR-701"),
             (PRD, "#### FR-702"),
             (SIGNALBEREGNING, "def trend(")),
        ),
        "bevegelse": Hjelpetekst(
            "Bevegelse:",
            f"endringen fra børsdagen før, mot de vanlige svingningene de "
            f"{volatilitet} børsdagene før. Slår ut over 1 standardavvik: +1 når "
            f"kursen steg, -1 når den falt. Måles mot hvor mye akkurat denne "
            f"aksjen pleier å svinge.",
            ((PRD, "#### FR-701"),
             (SIGNALBEREGNING, "def bevegelse("),
             (BEGRUNNELSER, "så en rolig og en urolig aksje måles hver på sitt")),
        ),
        "interesse": Hjelpetekst(
            "Interesse:",
            f"volumet mot medianvolumet de {volum} børsdagene før. Slår ut over "
            f"{faktor} ganger medianen. Volum har ingen retning i seg selv, så "
            f"fortegnet følger dagens kursendring: +1 en dag kursen steg, -1 "
            f"en dag den falt, og 0 når kursen var uendret.",
            ((PRD, "#### FR-701"),
             (SIGNALBEREGNING, "def interesse(")),
        ),
        "antall_dager": Hjelpetekst(
            "",
            f"Signalet trenger {dager} børsdager med kurser. Har aksjen færre, "
            f"kan det ikke regnes.",
            ((PRD, "Signalet krever 51 handelsdager"),
             (SIGNALBEREGNING, "def nodvendige_dager(")),
        ),
        "hvorfor_tre": Hjelpetekst(
            f"Hvorfor disse {ANTALL_SJEKKER}:",
            "hver sjekk ser på sin del av dataene: kursnivå, endring og volum, "
            "med én regel og én grense hver. Da ser du hva som ga utslaget. "
            "Sjekkene er valgt for å kunne forklares, ikke for å treffe "
            "markedet.",
            ((BEGRUNNELSER, "### Hvorfor akkurat disse tre sjekkene (FR-701)"),),
        ),
        "grensene": Hjelpetekst(
            "Grensene:",
            f"{_grensene(MAALTE_GRENSER)} ble "
            f"kontrollert mot {MAALTE_AKSJER} aksjer på Oslo Børs over {MAALTE_BOERSDAGER} "
            f"børsdager, {MAALT_PERIODE}, før de ble låst. Det var en kontroll "
            f"av at de holder, ikke et søk etter verdiene som gir penest "
            f"resultat.",
            ((MAALINGER, "### 7.4 Signaltesten mot 199 handelsdager"),
             (MAALINGER, "## 9. De to `[FORELØPIG]`-vinduene, målt"),
             (MAALINGER, "**Dette er en måling, ikke en optimalisering.**")),
        ),
        "skjevhet": Hjelpetekst(
            "Hvorfor retningen oftere er positiv når kursene stiger:",
            f"trend er en tilstand som kan vare i uker, mens bevegelse og "
            f"interesse er hendelser som sjelden slår ut. Retningen blir derfor "
            f"oftest trendens. I målingen over {MAALTE_BOERSDAGER} børsdager var "
            f"{tall(ANDEL_POSITIV, 'andel')} av aksjedagene med utslag positive "
            f"og {tall(ANDEL_NEGATIV, 'andel')} negative. Det beskriver "
            f"perioden, ikke det som kommer.",
            ((BEGRUNNELSER, "### Åpent punkt: skjevfordeling mot positiv retning"),
             (BEGRUNNELSER, "Det er en tilstand, som kan vare i uker."),
             (MAALINGER, "Målt over 199 dager er **60,0 % av aksjedagene med "
                         "utslag positive**, mot 29,5 %")),
        ),
        "grafen": Hjelpetekst(
            "Kursgrafen:",
            f"den tykke linja er utbyttejustert kurs, og den tynne er "
            f"snittet av de siste {ma} børsdagene, som trendsjekken måler mot. "
            f"Navnet står ved enden av hver linje. Sjekk 2 og 3 står i kortene over.",
            ((AKSJE_MAL, "Sjekk 2 og 3 tegnes ikke"),
             (AKSJEDETALJ, "glidende_snitt(kurser, p.ma_vindu)")),
        ),
        "ga": Hjelpetekst(
            "Ga:",
            f"det hver sjekk ga: +1 {POSITIV.lower()}, -1 {NEGATIV.lower()} eller "
            f"0 {INGEN_UTSLAG}.",
            ((PRD, "#### FR-706"),
             (AKSJE_MAL, '<span class="ga">Ga'),
             (AKSJEDETALJ, 'INGEN_UTSLAG = "ingen utslag"')),
        ),
        "maalt_mot": Hjelpetekst(
            "Målt mot:",
            "tallet sjekken ble avgjort av, og hva det ble målt mot. "
            "Feltet under tallet viser hvor sjekken gir 0, og prikken er målingen.",
            ((PRD, "#### FR-706"),
             (PRD, "se hva hvert fortegn ble målt mot"),
             (AKSJE_MAL, '<p class="maalt">Målt mot'),
             (AKSJE_MAL, '<div class="skala" aria-hidden="true">'),
             (AKSJEDETALJ, "def bygg_skala(")),
        ),
        "ikke_raad": Hjelpetekst(
            "",
            "Signalet er ikke en spådom: om sjekkene sier noe om kursen "
            "videre, er ikke målt. Det er heller ikke et råd om å kjøpe eller "
            "selge.",
            ((PRD, "### NFR-06 — Løsningen gir ikke investeringsråd"),
             (BEGRUNNELSER, "Om de sier noe om kursen videre, er ikke målt (FR-703).")),
        ),
    }
    return tekster


class Hjelp:
    """Oppslaget malene bruker: hjelp.tekst("trend").

    En metode og ikke hjelp["trend"], fordi Jinja gjoer en manglende noekkel i
    [] om til en tom verdi. Her feiler siden i stedet, saa en test ser det.
    """

    def __init__(self, tekster: dict[str, Hjelpetekst]):
        self._tekster = dict(tekster)

    def tekst(self, noekkel: str) -> Hjelpetekst:
        try:
            return self._tekster[noekkel]
        except KeyError:
            raise KeyError(f"Ingen hjelpetekst med nøkkelen {noekkel!r} i hjelpetekster.py") from None
