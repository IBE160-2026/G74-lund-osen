"""Datalaget: hvor kursseriene kommer fra.

Visningen skal ikke vite om en serie kommer fra en fil eller fra en database.
I dag er kilden et tidsstemplet JSON-oeyeblikksbilde i data/. I arkitekturfasen
blir den etter alt aa doemme en database - aapent punkt 17 - og da skal bare
denne fila endres.

Derfor gaar all lesing gjennom en port. I dag er det to: Kurskilde, som
visningen leser gjennom, og Kurslager (story 1.2), som skal erstatte den.
Mellom 1.2 og 1.4 har kursdataene altsaa to porter. Det bryter AD-3, og
bruddet varer til 1.4 flytter konsumentene over og fjerner Kurskilde.

Ingen funksjon her gjoer API-kall. Kvoten brukes bare av fetch_prices.py.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Protocol, runtime_checkable

PROSJEKTROT = Path(__file__).resolve().parent.parent
DATA_KATALOG = PROSJEKTROT / "data"


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


@dataclass(frozen=True)
class Kursrad:
    """En handelsdag slik porten gir den ut - AD-19.

    Norske feltnavn, og ingen av dem kan mangle eller vaere None. En
    feilstavet noekkel gir TypeError her, der dataene kommer inn, i stedet
    for en None som forplanter seg inn i signalberegningen som et tall som
    mangler.

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
            raise TypeError(f"dato maa vaere datetime.date, fikk {self.dato!r}")
        for navn in ("slutt", "justert_slutt"):
            verdi = getattr(self, navn)
            if isinstance(verdi, bool) or not isinstance(verdi, (int, float)):
                raise TypeError(f"{navn} maa vaere et tall, fikk {verdi!r}")
        if isinstance(self.volum, bool) or not isinstance(self.volum, int):
            raise TypeError(f"volum maa vaere et heltall, fikk {self.volum!r}")


@runtime_checkable
class Kurslager(Protocol):
    """Porten for kursdata - AD-3, AD-5, AD-19. Erstatter Kurskilde i 1.4.

    Bare tre metoder. Det finnes med vilje ingen legg_til_rad: serien skjoetes
    aldri paa, fordi EODHD regner adjusted_close om bakover ved hvert nytt
    utbytte (AD-5).
    """

    def erstatt_serie(self, symbol: str, rader: list[Kursrad], hentet: datetime) -> None:
        """Bytt ut hele symbolets serie, og sett sist_hentet, i ett.

        hentet er oeyeblikket dataene ble hentet, og maa ha tidssone. Det er
        et argument og ikke lagerets egen klokke, saa basen og raadatafila fra
        samme henting baerer samme tidspunkt. En tom serie, en feil radtype,
        to rader med samme dato eller en tid uten sone avvises, og da endres
        ingenting.
        """

    def serie(self, symbol: str) -> list[Kursrad]:
        """Kronologiske kursrader, nyeste sist. Tom liste hvis vi mangler."""

    def sist_hentet(self, symbol: str) -> datetime | None:
        """Naar symbolets serie sist ble erstattet, i UTC. None hvis aldri.

        Per symbol og ikke globalt: AD-15 lar ett symbol feile og beholde sin
        gamle serie, og da ogsaa sin gamle tid.
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


class Kurskilde(Protocol):
    """Det visningen faar lov til aa vite om lagringen.

    **PAA VEI UT - fjernes i story 1.4.** Erstattes av Kurslager, som gir
    Kursrad i stedet for dict. Ikke skriv ny kode mot denne porten;
    tests/test_kurslager.py feiler hvis en ny modul importerer den.

    To metoder, ingen av dem knyttet til fil eller database.
    """

    def tidsstempel(self) -> str | None:
        """Naar dataene ble hentet. None hvis kilden ikke vet det."""

    def serie(self, symbol: str) -> list[dict]:
        """Kronologiske kursrader, nyeste sist. Tom liste hvis vi mangler."""


@dataclass(frozen=True)
class MinneKilde:
    """Kilde som holder seriene i minnet.

    Finnes for at testene skal slippe aa skrive filer, og for at en test
    skal kunne beskrive noeyaktig den serien den vil proeve.
    """

    serier: dict[str, list[dict]]
    hentet: str | None = None

    def tidsstempel(self) -> str | None:
        return self.hentet

    def serie(self, symbol: str) -> list[dict]:
        return self.serier.get(symbol, [])


@dataclass(frozen=True)
class SnapshotKilde:
    """Leser et tidsstemplet oeyeblikksbilde slik signaltesten skrev det.

    Formatet er {"hentet": ..., "serier": {symbol: [rader]}}. Oeyeblikksbilder
    skrives aldri om (FR-406, NFR-07), saa denne kilden er bare lesende - det
    finnes med vilje ingen skrivemetode her.
    """

    hentet: str | None
    serier: dict[str, list[dict]]

    @classmethod
    def fra_fil(cls, sti: Path) -> "SnapshotKilde":
        innhold = json.loads(sti.read_text(encoding="utf-8"))
        return cls(
            hentet=innhold.get("hentet"),
            serier=innhold.get("serier", {}),
        )

    def tidsstempel(self) -> str | None:
        return self.hentet

    def serie(self, symbol: str) -> list[dict]:
        return self.serier.get(symbol, [])


# Oeyeblikksbilder heter <prefiks>-raa-<ÅÅÅÅ-MM-DD>.json. fetch_prices skriver
# KURSPREFIKS; eksperimentene skrev signaltest-, volumsjekk-, nyhetstest-.
# Alle leses likt, men ved lik dato vinner kursfila - se nyeste_snapshot.
KURSPREFIKS = "kurser"

_SNAPSHOT_MONSTER = re.compile(r"-raa-(\d{4}-\d{2}-\d{2})\.json$")


def nyeste_snapshot(katalog: Path = DATA_KATALOG) -> Path | None:
    """Oeyeblikksbildet med nyeste dato i navnet, eller None hvis ingen finnes.

    Datoen leses ut av filnavnet, ikke av filtidsstempelet. Et oeyeblikksbilde
    som kopieres eller sjekkes ut paa nytt, faar ny mtime, men datoen i navnet
    er den som gjelder - det er den dagen dataene er fra.

    **Datoen avgjoer alene.** Prefikset er aldri med i sammenligningen av
    datoer. Det var feilen her foer: valget var `max` over tuplene
    (dato, sti), og ved LIK dato falt `max` tilbake paa stien - da vant
    "signaltest-" over "kurser-" fordi s kommer etter k. Docstringen lovet at
    prefikset ikke ble sortert med, og det holdt saa lenge datoene var ulike.

    **Ved lik dato gjelder denne regelen:** fila fetch_prices skriver
    (KURSPREFIKS) vinner over alle andre prefikser. De andre er engangsuttrekk
    fra maalingene - signaltest, volumsjekk, nyhetstest - og skal ikke kunne
    fortrenge dagens kurser. Er ingen av dem kursfila, velges den alfabetisk
    foerste, slik at svaret er det samme hver gang og ikke avhenger av hvilken
    rekkefoelge katalogen leses i.
    """
    if not katalog.is_dir():
        return None

    datert = [
        (treff.group(1), sti)
        for sti in katalog.glob("*-raa-*.json")
        if (treff := _SNAPSHOT_MONSTER.search(sti.name))
    ]
    if not datert:
        return None

    nyeste_dato = max(dato for dato, _ in datert)
    return min(
        (sti for dato, sti in datert if dato == nyeste_dato),
        key=lambda sti: (not sti.name.startswith(f"{KURSPREFIKS}-raa-"), sti.name),
    )
