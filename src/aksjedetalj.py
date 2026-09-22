"""Aksjedetaljen - FR-201, FR-202 og FR-706.

Ren logikk. Ingen API-kall, ingen filer, ingen HTML. Leser gjennom Kurskilde,
akkurat som markedsoversikten.

Avgrenset til forklaringsdelen. Boersmeldinger (FR-203), KI-forklaring
(FR-602) og kommende hendelser (FR-301) mangler med vilje: de krever kilder
som ligger bak aapent punkt 1, 3 og 12.

Forklarbarhet er hele poenget. En bruker skal kunne lese seg fram til hvorfor
styrken ble 2 og ikke 1, uten aa kjenne formelen paa forhaand. Derfor baerer
hver sjekk maalingen sin hit ut, ikke bare fortegnet den endte paa.
"""

from dataclasses import dataclass
from datetime import date, timedelta

from kursdata import Aksje, Kurskilde
from markedsoversikt import RETNINGSVISNING, UKJENT_RETNING, Retningsvisning
from signalberegning import Parametre, STANDARD, Signal, beregn_signal

# FR-201: seks maaneder. Regnet i kalenderdager fra siste boersdag, ikke i
# antall rader - en boersdag er ikke en fast broekdel av en maaned.
GRAFVINDU_DAGER = 182


@dataclass(frozen=True)
class Punkt:
    """Ett punkt i grafen. ma50 er None foer snittet har nok historikk."""

    dato: str
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
    aksje: Aksje
    dato: str
    sluttkurs: float
    signal: Signal | None
    mangler: str | None
    punkter: tuple[Punkt, ...]

    @property
    def styrke(self) -> int | None:
        return self.signal.styrke if self.signal else None

    @property
    def retning(self) -> Retningsvisning:
        if not self.signal:
            return UKJENT_RETNING
        return RETNINGSVISNING.get(self.signal.retning, UKJENT_RETNING)

    @property
    def sjekker(self) -> tuple[SjekkVisning, ...]:
        if not self.signal:
            return ()
        return tuple(
            SjekkVisning(navn=s.navn, verdi=s.verdi, maaling=s.forklaring)
            for s in self.signal.sjekker
        )

    @property
    def bidragsytere(self) -> tuple[SjekkVisning, ...]:
        """De sjekkene som faktisk ga utslag. Summen av dem er styrken."""
        return tuple(s for s in self.sjekker if s.bidro)

    @property
    def har_ma50(self) -> bool:
        return any(p.ma50 is not None for p in self.punkter)


def _justert(rad: dict) -> float | None:
    verdi = rad.get("adjusted_close") or rad.get("close")
    return float(verdi) if verdi else None


def glidende_snitt(kurser: list[float], vindu: int) -> list[float | None]:
    """Snitt over de siste `vindu` verdiene, None foer det finnes nok."""
    ut: list[float | None] = []
    for i in range(len(kurser)):
        if i + 1 < vindu:
            ut.append(None)
        else:
            ut.append(sum(kurser[i + 1 - vindu : i + 1]) / vindu)
    return ut


def _innenfor_vindu(rader: list[dict], dager: int) -> int:
    """Indeksen der grafvinduet starter. Regnet paa dato, ikke paa radtall."""
    try:
        siste = date.fromisoformat(rader[-1]["date"][:10])
    except (ValueError, KeyError):
        return 0

    grense = siste - timedelta(days=dager)
    for i, rad in enumerate(rader):
        try:
            if date.fromisoformat(rad["date"][:10]) >= grense:
                return i
        except (ValueError, KeyError):
            continue
    return 0


def bygg_punkter(
    rader: list[dict], p: Parametre = STANDARD, dager: int = GRAFVINDU_DAGER
) -> tuple[Punkt, ...]:
    """Grafpunktene for de siste seks maanedene, med MA50 oppaa (FR-202).

    Kursen og snittet tegnes fra SAMME serie - den utbyttejusterte. Tegnet
    vi close mot et snitt regnet paa adjusted_close, ville de to ligget paa
    hver sin skala, og avstanden mellom dem ville vaert stoerst for aksjene
    som betaler mest utbytte. Linja skal vise sjekk 1, ikke et utbytte.

    Snittet regnes paa HELE serien og klippes etterpaa. Ellers ville de
    foerste 50 dagene i vinduet mistet snittet sitt uten grunn.
    """
    kurser = [k for k in (_justert(rad) for rad in rader) if k is not None]
    if len(kurser) != len(rader):
        rader = [rad for rad in rader if _justert(rad) is not None]

    snitt = glidende_snitt(kurser, p.ma_vindu)
    start = _innenfor_vindu(rader, dager)

    return tuple(
        Punkt(dato=rad["date"], kurs=kurs, ma50=ma)
        for rad, kurs, ma in zip(rader[start:], kurser[start:], snitt[start:])
    )


def bygg_detalj(
    aksje: Aksje, kilde: Kurskilde, p: Parametre = STANDARD
) -> Detalj | None:
    """Detaljen for en aksje, eller None hvis kilden ikke har den i det hele tatt."""
    rader = kilde.serie(aksje.symbol)
    if not rader:
        return None

    signal: Signal | None = None
    mangler: str | None = None
    try:
        signal = beregn_signal(rader, p)
    except ValueError as feil:
        mangler = str(feil)

    return Detalj(
        aksje=aksje,
        dato=rader[-1]["date"],
        sluttkurs=float(rader[-1]["close"]),
        signal=signal,
        mangler=mangler,
        punkter=bygg_punkter(rader, p),
    )


def finn_aksje(symbol: str, univers: tuple[Aksje, ...]) -> Aksje | None:
    letes_etter = symbol.strip().upper()
    for aksje in univers:
        if aksje.symbol == letes_etter:
            return aksje
    return None
