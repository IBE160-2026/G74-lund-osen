"""Skalering av kursgrafen til SVG-koordinater.

Ren regning. Ingen HTML og ingen tegnebibliotek - grafen er en SVG-polyline,
og malen setter bare tallene inn. Det holder for FR-201 og FR-202, og det
sparer oss for en frontend-avhengighet vi ellers maatte forsvart.

Aarsaken til at dette ligger i en egen fil, er at koordinatregning er lett aa
teste og vanskelig aa se feil i. En linje som ligger noen piksler galt, ser
riktig ut.
"""

from dataclasses import dataclass

from aksjedetalj import Punkt

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


@dataclass(frozen=True)
class Graf:
    bredde: int
    hoyde: int
    kurslinje: str
    ma50linje: str
    lav: float
    hoy: float
    forste_dato: str
    siste_dato: str
    rutenett: tuple[Rutelinje, ...]

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
        rutenett=_rutenett(lav, hoy, hoyde),
    )
