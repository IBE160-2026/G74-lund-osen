"""Skalering av kursgrafen til SVG-koordinater.

Ren regning. Ingen HTML og ingen tegnebibliotek - grafen er en SVG-polyline,
og malen setter bare tallene inn. Det holder for FR-201 og FR-202, og det
sparer oss for en frontend-avhengighet vi ellers maatte forsvart.

Aarsaken til at dette ligger i en egen fil, er at koordinatregning er lett aa
teste og vanskelig aa se feil i. En linje som ligger noen piksler galt, ser
riktig ut.
"""

from dataclasses import dataclass
from datetime import date

from aksjedetalj import Punkt
from boersdag import UtenforKalenderen, er_boersdag

BREDDE = 720
HOYDE = 260
MARG_X = 8
MARG_Y = 12

# Litt luft over og under, saa kurven ikke klistrer seg til kanten.
LUFT = 0.04


@dataclass(frozen=True)
class Rutelinje:
    y: float
    verdi: float


# Story 8.0c: fullt norsk maanedsnavn, smaa bokstaver (designregler §4).
MAANEDER = ("januar", "februar", "mars", "april", "mai", "juni", "juli",
            "august", "september", "oktober", "november", "desember")


@dataclass(frozen=True)
class Maanedsmerke:
    x: float
    navn: str


@dataclass(frozen=True)
class Graf:
    bredde: int
    hoyde: int
    kurslinje: str
    ma50linje: str
    lav: float
    hoy: float
    forste_dato: date
    siste_dato: date
    rutenett: tuple[Rutelinje, ...]
    maanedsmerker: tuple[Maanedsmerke, ...] = ()

    @property
    def har_ma50(self) -> bool:
        return bool(self.ma50linje)


def _spenn(punkter: tuple[Punkt, ...]) -> tuple[float, float]:
    """Laveste og hoyeste verdi som skal faa plass - baade kurs og snitt.

    Snittet maa vaere med i regnestykket. Var det ikke det, kunne MA50-linja
    havnet utenfor tegneflaten uten at noe feilet, og sjekk 1 ville blitt
    usynlig akkurat naar den er mest interessant.
    """
    verdier = [p.kurs for p in punkter]
    verdier += [p.ma50 for p in punkter if p.ma50 is not None]

    lav, hoy = min(verdier), max(verdier)
    if lav == hoy:
        # Flat serie. Uten dette blir hoyden null og alt deles paa null.
        return lav - 1.0, hoy + 1.0

    luft = (hoy - lav) * LUFT
    return lav - luft, hoy + luft


def _koordinater(punkter, hent, lav, hoy, bredde, hoyde) -> str:
    """Punktstreng til SVG. Hopper over punkter der verdien mangler."""
    if len(punkter) < 2:
        return ""

    tegne_bredde = bredde - 2 * MARG_X
    tegne_hoyde = hoyde - 2 * MARG_Y
    skala = hoy - lav

    deler = []
    for i, punkt in enumerate(punkter):
        verdi = hent(punkt)
        if verdi is None:
            continue
        x = MARG_X + tegne_bredde * i / (len(punkter) - 1)
        y = MARG_Y + tegne_hoyde * (1 - (verdi - lav) / skala)
        deler.append(f"{x:.1f},{y:.1f}")

    return " ".join(deler) if len(deler) >= 2 else ""


def _foerste_boersdag(aar: int, maaned: int) -> date | None:
    """Foerste boersdag i maaneden etter er_boersdag, eller None naar
    kalenderen ikke dekker aaret (boersdag.DEKKEDE_AAR)."""
    dag = date(aar, maaned, 1)
    try:
        while not er_boersdag(dag):
            dag = date.fromordinal(dag.toordinal() + 1)
    except UtenforKalenderen:
        return None
    return dag


def _maanedsmerker(punkter: tuple[Punkt, ...], bredde: int) -> tuple[Maanedsmerke, ...]:
    """Et merke ved foerste boersdag i hver maaned som finnes i serien - story
    8.0c. x er samme x som punktet for dagen, altsaa etter indeks og ikke
    etter kalenderen, fordi linja har lik avstand per boersdag. Mangler dagen
    i serien, faar maaneden ikke merke."""
    if len(punkter) < 2:
        return ()
    tegne_bredde = bredde - 2 * MARG_X
    indeks = {p.dato: i for i, p in enumerate(punkter)}
    merker = []
    sett = set()
    for p in punkter:
        maaned = (p.dato.year, p.dato.month)
        if maaned in sett:
            continue
        sett.add(maaned)
        foerste = _foerste_boersdag(*maaned)
        if foerste is None or foerste not in indeks:
            continue
        x = MARG_X + tegne_bredde * indeks[foerste] / (len(punkter) - 1)
        merker.append(Maanedsmerke(x=x, navn=MAANEDER[foerste.month - 1]))
    return tuple(merker)


def _rutenett(lav: float, hoy: float, hoyde: int, linjer: int = 3) -> tuple[Rutelinje, ...]:
    tegne_hoyde = hoyde - 2 * MARG_Y
    ut = []
    for i in range(linjer):
        andel = i / (linjer - 1)
        ut.append(
            Rutelinje(
                y=MARG_Y + tegne_hoyde * (1 - andel),
                verdi=lav + (hoy - lav) * andel,
            )
        )
    return tuple(ut)


def bygg_graf(
    punkter: tuple[Punkt, ...], bredde: int = BREDDE, hoyde: int = HOYDE
) -> Graf | None:
    """Koordinatene for kurs og MA50. None naar det ikke er noe aa tegne."""
    if len(punkter) < 2:
        return None

    lav, hoy = _spenn(punkter)

    return Graf(
        bredde=bredde,
        hoyde=hoyde,
        kurslinje=_koordinater(punkter, lambda p: p.kurs, lav, hoy, bredde, hoyde),
        ma50linje=_koordinater(punkter, lambda p: p.ma50, lav, hoy, bredde, hoyde),
        lav=lav,
        hoy=hoy,
        forste_dato=punkter[0].dato,
        siste_dato=punkter[-1].dato,
        maanedsmerker=_maanedsmerker(punkter, bredde),
        rutenett=_rutenett(lav, hoy, hoyde),
    )
