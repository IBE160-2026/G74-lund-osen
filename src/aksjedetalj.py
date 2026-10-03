"""Aksjedetaljen - FR-201, FR-202, FR-204 og FR-706.

Ren logikk. Ingen API-kall, ingen filer, ingen HTML. Grafen tegnes av serien
i kurs. Sjekkene og maalingene kommer fra raden i vurdering for datoen til
nyeste kurs, gjennom tilstand(), som i markedsoversikten (story 2.2b).
Signalet regnes aldri her.

Avgrenset til forklaringsdelen. Boersmeldinger (FR-203) og kommende
hendelser (FR-301) er ikke med: Euronext ga ikke tillatelse innen fristen, saa
plan B gjelder fra 28.09 (Epic 10 i epics.md). KI-forklaringen av signalet
(FR-602) kommer med Epic 10.

Forklarbarhet er hele poenget. En bruker skal kunne lese seg fram til hvorfor
styrken ble 2 og ikke 1, uten aa kjenne formelen paa forhaand. Derfor baerer
hver sjekk maalingen sin hit ut, ikke bare fortegnet den endte paa.
"""

from dataclasses import dataclass
from datetime import date, timedelta

from kursdata import Aksje, Kursrad
from markedsoversikt import (
    RETNINGSVISNING,
    UKJENT_RETNING,
    Retningsvisning,
    les_tilstand,
)
from oversiktsdata import Oversiktspost
from signalberegning import Parametre, STANDARD, nodvendige_dager, sjekker_fra
from tilstand import Art, Tilstand
from vurderingsdata import Grunn, Vurdering

# FR-201: seks maaneder. Regnet i kalenderdager fra siste boersdag, ikke i
# antall rader - en boersdag er ikke en fast broekdel av en maaned.
GRAFVINDU_DAGER = 182


@dataclass(frozen=True)
class Punkt:
    """Ett punkt i grafen. ma50 er None foer snittet har nok historikk."""

    dato: date
    kurs: float
    ma50: float | None


@dataclass(frozen=True)
class SjekkVisning:
    """En sjekk slik den vises: navn, fortegn, og maalingen bak fortegnet.

    FR-706 krever navn og verdi. Maalingen er tatt med i tillegg, fordi
    verdien alene ikke forklarer noe: at trend ga +1 sier ikke hvor mye over
    snittet kursen laa, og da kan brukeren ikke etterproeve summen.
    """

    navn: str
    verdi: int
    maaling: str

    @property
    def fortegn(self) -> str:
        return f"{self.verdi:+d}" if self.verdi else "0"

    @property
    def klasse(self) -> str:
        if self.verdi > 0:
            return "opp"
        if self.verdi < 0:
            return "ned"
        return "ingen"

    @property
    def bidro(self) -> bool:
        """Talte denne sjekken med i styrken?"""
        return self.verdi != 0


@dataclass(frozen=True)
class Detalj:
    """Aksjedetaljen. tilstand og tekst er som i markedsoversikten: tekst er
    None bare naar raden har en vurdering. sjekker er tom naar den ikke har
    det, og da staar tekst i stedet (FR-204)."""

    aksje: Aksje
    dato: date
    sluttkurs: float
    tilstand: Tilstand | None
    tekst: str | None
    sjekker: tuple[SjekkVisning, ...]
    punkter: tuple[Punkt, ...]
    antall_dager: int = 0
    noedvendige_dager: int = 0

    @property
    def vurdering(self) -> Vurdering | None:
        if self.tilstand is not None and self.tilstand.art is Art.SVAR:
            return self.tilstand.innhold
        return None

    @property
    def styrke(self) -> int | None:
        return self.vurdering.styrke if self.vurdering else None

    @property
    def retning(self) -> Retningsvisning:
        if not self.vurdering:
            return UKJENT_RETNING
        return RETNINGSVISNING.get(self.vurdering.retning, UKJENT_RETNING)

    @property
    def signalet_ikke_regnet(self) -> bool:
        return self.tilstand is not None and self.tilstand.innhold is Grunn.SIGNAL_IKKE_REGNET

    @property
    def bidragsytere(self) -> tuple[SjekkVisning, ...]:
        """De sjekkene som faktisk ga utslag. Summen av dem er styrken."""
        return tuple(s for s in self.sjekker if s.bidro)


def glidende_snitt(kurser: list[float], vindu: int) -> list[float | None]:
    """Snitt over de siste `vindu` verdiene, None foer det finnes nok."""
    ut: list[float | None] = []
    for i in range(len(kurser)):
        if i + 1 < vindu:
            ut.append(None)
        else:
            ut.append(sum(kurser[i + 1 - vindu : i + 1]) / vindu)
    return ut


def _innenfor_vindu(rader: list[Kursrad], dager: int) -> int:
    """Indeksen der grafvinduet starter. Regnet paa dato, ikke paa radtall."""
    if not rader:
        return 0

    grense = rader[-1].dato - timedelta(days=dager)
    for i, rad in enumerate(rader):
        if rad.dato >= grense:
            return i
    return 0


def bygg_punkter(
    rader: list[Kursrad], p: Parametre = STANDARD, dager: int = GRAFVINDU_DAGER
) -> tuple[Punkt, ...]:
    """Grafpunktene for de siste seks maanedene, med MA50 oppaa (FR-202).

    Kursen og snittet tegnes fra SAMME serie - den utbyttejusterte. Tegnet
    vi slutt mot et snitt regnet paa justert_slutt, ville de to ligget paa
    hver sin skala, og avstanden mellom dem ville vaert stoerst for aksjene
    som betaler mest utbytte. Linja skal vise sjekk 1, ikke et utbytte.

    Snittet regnes paa HELE serien og klippes etterpaa. Ellers ville de
    foerste 50 dagene i vinduet mistet snittet sitt uten grunn.
    """
    kurser = [float(rad.justert_slutt) for rad in rader]
    snitt = glidende_snitt(kurser, p.ma_vindu)
    start = _innenfor_vindu(rader, dager)

    return tuple(
        Punkt(dato=rad.dato, kurs=kurs, ma50=ma)
        for rad, kurs, ma in zip(rader[start:], kurser[start:], snitt[start:])
    )


def bygg_detalj(
    post: Oversiktspost, rader: list[Kursrad], idag: date, p: Parametre = STANDARD
) -> Detalj | None:
    """Detaljen for en aksje, eller None hvis den ikke har en eneste kursrad.

    post er aksjen og raden i vurdering fra Oversiktsleser, rader er serien i
    kurs. Grafen tegnes av serien. Sjekkene kommer fra raden, med
    forklaringene laget av maalingene der (FR-706). Har raden ingen
    vurdering, er sjekkene tomme og teksten sier hvorfor (FR-204).
    """
    if not rader or post.nyeste is None:
        return None

    utfall, tekst = les_tilstand(post.innhold, post.nyeste.dato, idag)
    sjekker: tuple[SjekkVisning, ...] = ()
    if utfall is not None and utfall.art is Art.SVAR:
        sjekker = tuple(
            SjekkVisning(navn=s.navn, verdi=s.verdi, maaling=s.forklaring)
            for s in sjekker_fra(utfall.innhold, p)
        )

    return Detalj(
        aksje=post.aksje,
        dato=post.nyeste.dato,
        sluttkurs=float(post.nyeste.slutt),
        tilstand=utfall,
        tekst=tekst,
        sjekker=sjekker,
        punkter=bygg_punkter(rader, p),
        antall_dager=len(rader),
        noedvendige_dager=nodvendige_dager(p),
    )


def normaliser_symbol(symbol: str) -> str:
    """Symbolet i ruta slik aksje har det: uten mellomrom, med store
    bokstaver. En ticker som EQNR.OL blir ikke et symbol."""
    return symbol.strip().upper()
