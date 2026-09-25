"""Porten for kursdata: typene og kontrakten, uten I/O - AD-1, AD-3, AD-19.

Visningen skal ikke vite om en serie kommer fra en fil eller fra en database.
Derfor gaar all lesing gjennom en port: Kurslager, med lesesiden Kursleser
(AD-3). Visningen leser gjennom Kursleser. Den gamle porten ved siden av ble
fjernet i story 1.4c, og kursdataene har naa bare denne ene.

Her staar bare porten og typene den gir ut. Adapterne ligger i skallet:
lagring_fil.py leser oeyeblikksbildene i data/, lagring_sqlite.py er basen,
og eodhd.py oversetter kildens feltnavn til Kursrad. Porten importerer ingen
av dem, og gjoer ingen I/O selv (story 1.5).

Ingen funksjon her gjoer API-kall. Kvoten brukes bare av fetch_prices.py.
"""

import math
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class Aksje:
    """Ett selskap i universet.

    Symbolet er formen NewsWeb bruker i issuerSign, tickeren er formen EODHD
    bruker. De to maa holdes fra hverandre: den dagen meldinger og kurser skal
    kobles sammen, er det denne raden som binder dem.
    """

    symbol: str
    ticker: str
    navn: str
    sektor: str


# De 15 er valgt paa median daglig omsetning over 25 MNOK maalt over tre
# maaneder, og spredning over minst aatte sektorer. Maalingen som avgjorde
# lista staar i malinger.md §1. Navn og sektor er hardkodet fordi /api/eod
# ikke returnerer dem, og et oppslag ville kostet kvote uten aa gi noe nytt.
AKSJEUNIVERS: tuple[Aksje, ...] = (
    Aksje("EQNR", "EQNR.OL", "Equinor", "Energi"),
    Aksje("DNB", "DNB.OL", "DNB Bank", "Finans"),
    Aksje("KOG", "KOG.OL", "Kongsberg Gruppen", "Industri"),
    Aksje("AKRBP", "AKRBP.OL", "Aker BP", "Energi"),
    Aksje("NHY", "NHY.OL", "Norsk Hydro", "Materialer"),
    Aksje("FRO", "FRO.OL", "Frontline", "Shipping"),
    Aksje("VAR", "VAR.OL", "Vår Energi", "Energi"),
    Aksje("TEL", "TEL.OL", "Telenor", "Telekom"),
    Aksje("YAR", "YAR.OL", "Yara International", "Materialer"),
    Aksje("MOWI", "MOWI.OL", "Mowi", "Sjømat"),
    Aksje("ORK", "ORK.OL", "Orkla", "Konsum"),
    Aksje("SALM", "SALM.OL", "SalMar", "Sjømat"),
    Aksje("GJF", "GJF.OL", "Gjensidige Forsikring", "Finans"),
    Aksje("DNO", "DNO.OL", "DNO", "Energi"),
    Aksje("MPCC", "MPCC.OL", "MPC Container Ships", "Shipping"),
)


class UgyldigKursrad(ValueError):
    """En verdi Kursrad ikke godtar.

    Alle avvisningene i Kursrad reiser denne, ogsaa feil type. Foer 24.09 kom
    de som TypeError, ValueError og OverflowError, og en oversetter som fanget
    ValueError, slapp de to andre gjennom. Naa er det en klasse aa fange.

    Et felt som mangler helt, er unntaket: det stoppes av dataclassens
    __init__ med TypeError, foer denne kontrollen kjoerer.
    """


@dataclass(frozen=True)
class Kursrad:
    """En handelsdag slik porten gir den ut - AD-19.

    Norske feltnavn, og ingen av dem kan mangle eller vaere None. En
    feilstavet noekkel gir TypeError her, der dataene kommer inn, i stedet
    for en None som forplanter seg inn i signalberegningen som et tall som
    mangler. Feil verdi i et felt som finnes, gir UgyldigKursrad.

    dato er en kalenderdato (AD-20), ikke tekst og ikke et tidspunkt.
    Adapteren oversetter fra kildens "YYYY-MM-DD".
    """

    dato: date
    slutt: float
    justert_slutt: float
    volum: int

    def __post_init__(self):
        # datetime er en underklasse av date, men baerer et klokkeslett, og et
        # klokkeslett i feil sone kan gi feil boersdag.
        if not isinstance(self.dato, date) or isinstance(self.dato, datetime):
            raise UgyldigKursrad(f"dato maa vaere datetime.date, fikk {self.dato!r}")
        for navn in ("slutt", "justert_slutt"):
            verdi = getattr(self, navn)
            if isinstance(verdi, bool) or not isinstance(verdi, (int, float)):
                raise UgyldigKursrad(f"{navn} maa vaere et tall, fikk {verdi!r}")
            # NaN og uendelig er tall for Python, men ikke kurser. Slapp de
            # gjennom, ville minnelageret lagret NaN mens SQLite avviste den.
            # Et heltall for stort for float gir OverflowError i isfinite.
            try:
                endelig = math.isfinite(verdi)
            except OverflowError:
                endelig = False
            if not endelig:
                raise UgyldigKursrad(f"{navn} maa vaere et endelig tall, fikk {verdi!r}")
            # En kurs paa null eller under er ikke en kurs, og
            # signalberegningen deler paa kursen.
            if verdi <= 0:
                raise UgyldigKursrad(f"{navn} maa vaere over null, fikk {verdi!r}")
        if isinstance(self.volum, bool) or not isinstance(self.volum, int):
            raise UgyldigKursrad(f"volum maa vaere et heltall, fikk {self.volum!r}")
        # Null er en dag uten handel og lovlig. Under null er det ikke.
        if self.volum < 0:
            raise UgyldigKursrad(f"volum kan ikke vaere negativt, fikk {self.volum!r}")


@runtime_checkable
class Kursleser(Protocol):
    """Lesesiden av kursporten - AD-3, AD-19. Story 1.4a.

    Det konsumentene trenger, og ikke mer. SnapshotLeser oppfyller bare denne:
    et oeyeblikksbilde skrives aldri om (FR-406, NFR-07), saa det faar ingen
    skrivemetode.

    Lesekontrakten for alle lagre: sist_hentet(s) er None hvis og bare hvis
    serie(s) er tom.
    """

    def serie(self, symbol: str) -> list[Kursrad]:
        """Kronologiske kursrader, nyeste sist. Tom liste hvis vi mangler."""

    def sist_hentet(self, symbol: str) -> datetime | None:
        """Naar symbolets serie sist ble erstattet, i UTC. None hvis aldri.

        Per symbol og ikke globalt: AD-15 lar ett symbol feile og beholde sin
        gamle serie, og da ogsaa sin gamle tid.
        """


@runtime_checkable
class Kurslager(Kursleser, Protocol):
    """Porten for kursdata - AD-3, AD-5, AD-19. Den eneste for kursdataene.

    Kursleser pluss erstatt_serie, altsaa tre metoder. Det finnes med vilje
    ingen legg_til_rad: serien skjoetes aldri paa, fordi EODHD regner
    den justerte kursen om bakover ved hvert nytt utbytte (AD-5).
    """

    def erstatt_serie(self, symbol: str, rader: list[Kursrad], hentet: datetime) -> None:
        """Bytt ut hele symbolets serie, og sett sist_hentet, i ett.

        hentet er oeyeblikket dataene ble hentet, og maa ha tidssone. Det er
        et argument og ikke lagerets egen klokke, saa basen og raadatafila fra
        samme henting baerer samme tidspunkt. En tom serie, en feil radtype,
        to rader med samme dato eller en tid uten sone avvises, og da endres
        ingenting.
        """


def kontroller_skriving(rader: list[Kursrad], hentet: datetime) -> datetime:
    """Felles kontroll for alle Kurslager-implementasjoner. Returnerer hentet i UTC.

    Kjoeres foer noe lagres, saa en avvist skriving etterlater lageret slik
    det var. Like datoer kontrolleres IKKE her: i SQLite stoppes de av
    primaernoekkelen midt i transaksjonen, og det er den veien som beviser at
    slettingen og innsettingen henger sammen.
    """
    for rad in rader:
        if not isinstance(rad, Kursrad):
            raise TypeError(f"Kurslager tar Kursrad, fikk {type(rad).__name__}")
    if not rader:
        # AD-5: hver henting dekker minst 175 handelsdager, saa ingen lovlig
        # kaller sender tom liste. Slapp den gjennom, ville symbolets historikk
        # blitt slettet og faatt et ferskt tidsstempel paa ingenting.
        raise ValueError("Tom serie avvises - en henting gir aldri null rader")
    if not isinstance(hentet, datetime):
        raise TypeError(f"hentet maa vaere datetime, fikk {hentet!r}")
    if hentet.tzinfo is None or hentet.utcoffset() is None:
        raise ValueError(f"hentet maa ha tidssone (AD-20), fikk {hentet!r}")
    return hentet.astimezone(timezone.utc)


@dataclass
class MinneKurslager:
    """Kurslager i minnet, for testene. Samme kontrakt som SQLite-adapteren.

    Alt valideres foer noe lagres, saa en avvist skriving etterlater lageret
    slik det var - samme egenskap som transaksjonen gir i databasen.
    """

    _serier: dict[str, tuple[Kursrad, ...]] = field(default_factory=dict)
    _hentet: dict[str, datetime] = field(default_factory=dict)

    def erstatt_serie(self, symbol: str, rader: list[Kursrad], hentet: datetime) -> None:
        rader = list(rader)
        tid = kontroller_skriving(rader, hentet)
        # Samme regel som primaernoekkelen (symbol, dato) i SQLite.
        datoer = [rad.dato for rad in rader]
        if len(set(datoer)) != len(datoer):
            raise ValueError(f"To rader med samme dato for {symbol}")
        self._serier[symbol] = tuple(sorted(rader, key=lambda rad: rad.dato))
        self._hentet[symbol] = tid

    def serie(self, symbol: str) -> list[Kursrad]:
        return list(self._serier.get(symbol, ()))

    def sist_hentet(self, symbol: str) -> datetime | None:
        return self._hentet.get(symbol)
