"""Børsometeret - story 8.6, FR-106, designregler.md §3 og §4.

Ren logikk. Ingen API-kall, ingen filer og ingen klokke: aksjene, de to
kursene og vurderingen for dagen kommer inn som argumenter. Siden leser dem
gjennom portene som finnes (AD-3), og ingen ny tabell trengs.

Én rute per aksje i lista, ordnet etter bransje i rekkefølgen i
designregler.md §4 (avgjørelsen 22.10 kl. 23:19). Fargen er endringen fra
børsdagen før (FR-101, endring_i_prosent), størrelsen er volumforholdet i den
lagrede vurderingen, og rammen er styrken: gul ved 3 av 3, mørk ved 2 av 3,
ellers ingen. Signalet regnes aldri her, det leses (AD-7). Snittet per
bransje er snittet av endringen for aksjene i bransjen som har en endring,
og en bransje med én aksje merkes «1 aksje» (FR-106). Antallet bransjer og
aksjer telles fra lista, aldri fra et fast tall (føringen 30.09 under AD-21).
"""

from dataclasses import dataclass
from datetime import date

from kursdata import Aksje, Kursrad
from markedsoversikt import endring_i_prosent, les_tilstand
from signalberegning import STANDARD, Parametre
from tilstand import Art
from vurderingsdata import Grunn, Vurdering

# De 13 bransjene i designregler.md §4, i rekkefølgen tabellen står.
BRANSJER = (
    "Energi",
    "Finans",
    "Industri",
    "Materialer",
    "Shipping",
    "Telekom",
    "Sjømat",
    "Konsum",
    "Forbruk",
    "Teknologi",
    "Helse",
    "Eiendom",
    "Kraft",
)

# Størrelsen på ruta, etter volumforholdet (spesifikasjonen 8.6, «Avgjort»).
LAV, VANLIG, HOEY = "lav", "vanlig", "hoey"
# Rammen, etter styrken (designregler.md §3).
GUL, MOERK = "gul", "moerk"
UTEN_DATA = "Uten data"


@dataclass(frozen=True)
class Rute:
    """Én aksje i børsometeret."""

    aksje: Aksje
    endring: float | None
    volumforhold: float | None
    styrke: int | None
    tekst: str | None
    uten_data: bool = False

    @property
    def stoerrelse(self) -> str:
        return stoerrelse(self.volumforhold)

    @property
    def ramme(self) -> str | None:
        return ramme(self.styrke)


@dataclass(frozen=True)
class Bransje:
    """En bransje med rutene sine og snittet av endringen."""

    navn: str
    ruter: tuple[Rute, ...]

    @property
    def antall(self) -> int:
        return len(self.ruter)

    @property
    def snitt(self) -> float | None:
        return snitt(self.ruter)


def stoerrelse(volumforhold: float | None, p: Parametre = STANDARD) -> str:
    """Tre trinn: under 1, fra 1 til under volumfaktor, og fra volumfaktor,
    som gir utslag på interesse. Uten volumforhold vanlig størrelse."""
    if volumforhold is None:
        return VANLIG
    if volumforhold >= p.volumfaktor:
        return HOEY
    if volumforhold < 1:
        return LAV
    return VANLIG


def ramme(styrke: int | None) -> str | None:
    """Gul ved 3 av 3, mørk ved 2 av 3, ellers ingen (designregler.md §3)."""
    if styrke == 3:
        return GUL
    if styrke == 2:
        return MOERK
    return None


def snitt(ruter: tuple[Rute, ...] | list[Rute]) -> float | None:
    """Snittet av endringen for rutene som har en endring, None uten noen."""
    endringer = [r.endring for r in ruter if r.endring is not None]
    if not endringer:
        return None
    return sum(endringer) / len(endringer)


def bygg_rute(aksje: Aksje, kurser: list[Kursrad], innhold: Vurdering | Grunn | None, dato: date, idag: date) -> Rute:
    """Ruta for én aksje på dato. kurser er kursradene til og med dato. En
    aksje uten kurs på dato står med «Uten data» og uten ramme."""
    if not kurser or kurser[-1].dato != dato:
        return Rute(aksje=aksje, endring=None, volumforhold=None, styrke=None, tekst=UTEN_DATA, uten_data=True)
    utfall, tekst = les_tilstand(innhold, dato, idag)
    vurdering = utfall.innhold if utfall is not None and utfall.art is Art.SVAR else None
    return Rute(
        aksje=aksje,
        endring=endring_i_prosent(kurser[-2:]),
        volumforhold=vurdering.volumforhold if vurdering else None,
        styrke=vurdering.styrke if vurdering else None,
        tekst=tekst,
    )


def bygg_boersometer(ruter: list[Rute]) -> list[Bransje]:
    """Rutene gruppert etter bransje, i rekkefølgen i designregler.md §4, og
    i lista sin rekkefølge inne i hver bransje. Bare bransjene som har en
    aksje i lista, og en ukjent bransje sist."""
    grupper: dict[str, list[Rute]] = {}
    for rute in ruter:
        grupper.setdefault(rute.aksje.sektor, []).append(rute)
    rekkefoelge = sorted(grupper, key=lambda navn: (BRANSJER.index(navn) if navn in BRANSJER else len(BRANSJER), navn))
    return [Bransje(navn=navn, ruter=tuple(grupper[navn])) for navn in rekkefoelge]
