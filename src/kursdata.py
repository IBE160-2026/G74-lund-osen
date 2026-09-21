"""Datalaget: hvor kursseriene kommer fra.

Visningen skal ikke vite om en serie kommer fra en fil eller fra en database.
I dag er kilden et tidsstemplet JSON-oeyeblikksbilde i data/. I arkitekturfasen
blir den etter alt aa doemme en database - aapent punkt 17 - og da skal bare
denne fila endres.

Derfor gaar all lesing gjennom Kurskilde. Den har to metoder, og ingen av dem
sier noe om lagringsform.

Ingen funksjon her gjoer API-kall. Kvoten brukes bare av fetch_prices.py.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

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


class Kurskilde(Protocol):
    """Det visningen faar lov til aa vite om lagringen.

    To metoder, ingen av dem knyttet til fil eller database. En
    databaseimplementasjon i arkitekturfasen skal kunne settes inn her uten at
    markedsoversikt.py eller app.py endres.
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


# Oeyeblikksbilder heter <noe>-raa-<ÅÅÅÅ-MM-DD>.json. fetch_prices skriver
# kurser-raa-, signaltesten skrev signaltest-raa-. Begge leses likt.
_SNAPSHOT_MONSTER = re.compile(r"-raa-(\d{4}-\d{2}-\d{2})\.json$")


def nyeste_snapshot(katalog: Path = DATA_KATALOG) -> Path | None:
    """Oeyeblikksbildet med nyeste dato i navnet, eller None hvis ingen finnes.

    Datoen leses ut av filnavnet, ikke av filtidsstempelet. Et oeyeblikksbilde
    som kopieres eller sjekkes ut paa nytt, faar ny mtime, men datoen i navnet
    er den som gjelder - det er den dagen dataene er fra.

    Prefikset sorteres bevisst IKKE med: "kurser-" kommer foer "signaltest-"
    alfabetisk, saa alfabetisk sortering ville valgt feil fil.
    """
    if not katalog.is_dir():
        return None

    datert = [
        (treff.group(1), sti)
        for sti in katalog.glob("*-raa-*.json")
        if (treff := _SNAPSHOT_MONSTER.search(sti.name))
    ]
    return max(datert)[1] if datert else None
