"""Børsometeret - story 8.6, FR-106, designregler.md §3 og §4.

Ren logikk. Ingen API-kall, ingen filer og ingen klokke: aksjene, de to
kursene og vurderingen for dagen kommer inn som argumenter. Siden leser dem
gjennom portene som finnes (AD-3), og ingen ny tabell trengs.

Én rute per aksje i lista, ordnet etter bransje i rekkefølgen i
designregler.md §4 (avgjørelsen 22.10 kl. 23:19). Fargen er endringen fra
børsdagen før (FR-101, endring_i_prosent), størrelsen er volumforholdet i den
lagrede vurderingen, og rammen er signalet. Signalet regnes aldri her, det
leses (AD-7). Snittet per bransje er snittet av endringen for aksjene i
bransjen som har en endring, og en bransje med én aksje merkes «1 aksje»
(FR-106). Antallet bransjer og aksjer telles fra lista, aldri fra et fast tall
(føringen 30.09 under AD-21).

Rammen (designregler §3, gjennomgangen VG1): gult betyr 3 av 3 på siste
børsdag og står også når siden viser en annen dag, også en dag uten vurdering
eller uten kurs (gruppens svar 23.10 kl. 09:24, a). 2 av 3 merkes bare for
siste børsdag.

Story 8.6b (avgjørelsen 24.10 kl. 11:54): søylene står bare på oversikten,
og hovedindeksen står som et tall i linja «Mål mot børsen», med endringen
for dagen som vises.
"""

from dataclasses import dataclass
from datetime import date

from hjelpetekster import ANTALL_SJEKKER
from hovedindeks import indeksendring
from kursdata import Aksje, Kursrad
from markedsoversikt import IKKE_VURDERT, endring_i_prosent, grunn_med_tall, les_tilstand
from signalberegning import STANDARD, Parametre
from tallformat import avrundet, desimaler_mot_grense, tall
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
# Ordet for størrelsen, i ruta for skjermleser og i tabellen.
VOLUMORD = {LAV: "lavt", VANLIG: "vanlig", HOEY: "høyt"}
# Rammen, etter styrken (designregler.md §3).
GUL, MOERK = "gul", "moerk"
UTEN_DATA = "Uten data"

# Story 8.6b, c: fem fargetrinn etter endringen slik den vises, med grensene i
# prosent. Navnene er klassene i malen og fargene i :root i stil.css.
GRENSE_LYS = 0.5
GRENSE_STERK = 2.0
NOEYTRAL, LYS_OPP, LYS_NED, STERK_OPP, STERK_NED = "noeytral", "lys-opp", "lys-ned", "opp", "ned"


@dataclass(frozen=True)
class Rute:
    """Én aksje i børsometeret.

    styrke er fra vurderingen for dagen som vises, siste_styrke fra siste
    børsdag. er_siste sier om dagen som vises, er siste børsdag."""

    aksje: Aksje
    endring: float | None
    volumforhold: float | None
    styrke: int | None
    tekst: str | None
    uten_data: bool = False
    siste_styrke: int | None = None
    er_siste: bool = True

    @property
    def stoerrelse(self) -> str:
        return stoerrelse(self.volumforhold)

    @property
    def fargetrinn(self) -> str | None:
        return fargetrinn(self.endring)

    @property
    def volumord(self) -> str | None:
        return None if self.volumforhold is None else VOLUMORD[self.stoerrelse]

    @property
    def volum_vist(self) -> str | None:
        return None if self.volumforhold is None else vis_volumforhold(self.volumforhold)

    @property
    def ikke_vurdert(self) -> bool:
        """Ruta sier «ikke vurdert», og siden får fotnoten (story 3.4d,
        gruppens svar 23.10 kl. 11:44, b). En rute uten kurs sier «Uten
        data»."""
        return self.tekst == IKKE_VURDERT

    @property
    def ramme(self) -> str | None:
        if self.er_siste:
            return ramme(self.styrke)
        # Gruppens svar 23.10 kl. 09:24 (a): gult også en dag uten vurdering
        # eller uten kurs.
        return GUL if self.siste_styrke == ANTALL_SJEKKER else None


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
    """Tre trinn: under 1, fra 1 til og med volumfaktor, og over volumfaktor,
    som gir utslag på interesse (signalberegning.interesse, «>»). Uten
    volumforhold vanlig størrelse."""
    if volumforhold is None:
        return VANLIG
    if volumforhold > p.volumfaktor:
        return HOEY
    if volumforhold < 1:
        return LAV
    return VANLIG


def fargetrinn(endring: float | None) -> str | None:
    """Fem trinn etter endringen slik den vises, to desimaler (8.6b, c):
    under GRENSE_LYS i tallverdi nøytral, fra GRENSE_LYS lys, og fra
    GRENSE_STERK sterk. 0,50 % er lys, og 2,00 % er sterk. None uten endring."""
    if endring is None:
        return None
    vist = avrundet(endring, "endring")
    if vist >= GRENSE_STERK:
        return STERK_OPP
    if vist <= -GRENSE_STERK:
        return STERK_NED
    if vist >= GRENSE_LYS:
        return LYS_OPP
    if vist <= -GRENSE_LYS:
        return LYS_NED
    return NOEYTRAL


def trinnforklaringer() -> list[tuple[str, str]]:
    """Trinnene til «Hva fargene betyr», fra størst fall til størst
    stigning, med tallene fra grensene (regel 21)."""
    lys, sterk = tall(GRENSE_LYS, "faktor"), tall(GRENSE_STERK, "grense")
    return [
        (STERK_NED, f"Ned {sterk} eller mer"),
        (LYS_NED, f"Ned fra {lys} til under {sterk}"),
        (NOEYTRAL, f"Under ±{tall(GRENSE_LYS, 'grense', desimaler=1)}"),
        (LYS_OPP, f"Opp fra {lys} til under {sterk}"),
        (STERK_OPP, f"Opp {sterk} eller mer"),
    ]


def vis_volumforhold(volumforhold: float, p: Parametre = STANDARD) -> str:
    """Volumforholdet med så mange desimaler, minst to, at det skilles fra
    grensene 1 og volumfaktor, som på aksjesiden (gjennomgangen, BH2/ECH4)."""
    antall = max(
        desimaler_mot_grense(volumforhold, 1, minst=2), desimaler_mot_grense(volumforhold, p.volumfaktor, minst=2)
    )
    return tall(volumforhold, "forhold", antall)


def ramme(styrke: int | None) -> str | None:
    """Gul ved 3 av 3, mørk ved 2 av 3, ellers ingen (designregler.md §3).
    Gjelder siste børsdag; Rute.ramme sier hva som gjelder en annen dag."""
    if styrke == ANTALL_SJEKKER:
        return GUL
    if styrke == ANTALL_SJEKKER - 1:
        return MOERK
    return None


def snitt(ruter: tuple[Rute, ...] | list[Rute]) -> float | None:
    """Snittet av endringen for rutene som har en endring, None uten noen."""
    endringer = [r.endring for r in ruter if r.endring is not None]
    if not endringer:
        return None
    return sum(endringer) / len(endringer)


def bygg_rute(
    aksje: Aksje,
    kurser: list[Kursrad],
    innhold: Vurdering | Grunn | None,
    dato: date,
    idag: date,
    siste_styrke: int | None = None,
    er_siste: bool = True,
    p: Parametre = STANDARD,
) -> Rute:
    """Ruta for én aksje på dato. kurser er kursradene til og med dato. En
    aksje uten kurs på dato står med «Uten data», og med gult bare ved 3 av 3
    på siste børsdag."""
    if not kurser or kurser[-1].dato != dato:
        return Rute(
            aksje=aksje,
            endring=None,
            volumforhold=None,
            styrke=None,
            tekst=UTEN_DATA,
            uten_data=True,
            siste_styrke=siste_styrke,
            er_siste=er_siste,
        )
    utfall, tekst = les_tilstand(innhold, dato, idag)
    # Story 8.2a, d (gruppens svar 24.10 kl. 11:29): ruta sier hvorfor, med
    # samme tall som aksjesiden for dagen, regnet av kursene til og med dato.
    tekst = grunn_med_tall(utfall, tekst, len(kurser), p)
    vurdering = utfall.innhold if utfall is not None and utfall.art is Art.SVAR else None
    return Rute(
        aksje=aksje,
        endring=endring_i_prosent(kurser[-2:]),
        volumforhold=vurdering.volumforhold if vurdering else None,
        styrke=vurdering.styrke if vurdering else None,
        tekst=tekst,
        siste_styrke=siste_styrke,
        er_siste=er_siste,
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


def dagen_foer(datoer: list[date], dag: date) -> date | None:
    """Datoen før dag blant kursdatoene for aksjene i lista, den endringen i
    rutene regnes fra (8.6b, b). None når dag er den første."""
    foer = [d for d in datoer if d < dag]
    return max(foer) if foer else None


def indeks_for_dagen(serie: list[Kursrad], dag: date) -> float | None:
    """Endringen i hovedindeksen for dag, mot børsdagen før etter kalenderen
    (hovedindeks.indeksendring). None når indeksen ikke har en rad for dag,
    eller ikke for børsdagen før (8.6b, b)."""
    til = [rad for rad in serie if rad.dato <= dag]
    if not til or til[-1].dato != dag:
        return None
    return indeksendring(til)
