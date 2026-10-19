"""Min liste: porten for merkingen, uten I/O - story 8.3, FR-101, FR-102,
AD-3, AD-10, AD-21.

Merkingen er et eget datasett med webserveren som eneste skriver (foeringen
2026-09-30 under AD-3). Det eneste som lagres, er hvilke aksjer som er
merket: ingen antall, beloep eller kurs. Merkingen gjelder maskinen, uten
innlogging, og koster ingen API-kall.

Lista tas som parameter og antas aldri aa ha 15 aksjer (foeringen 2026-09-30
under AD-21). Et symbol som ikke staar i lista, avvises med UkjentAksje, i
porten og, i SQLite, av triggeren i 0007.

Her staar porten og minneutgaven. SQLite-adapteren er SqliteMinlistelager i
lagring_sqlite.py.
"""

from collections.abc import Iterable
from typing import Protocol, runtime_checkable


class UkjentAksje(ValueError):
    """Symbolet staar ikke i lista, og kan ikke merkes."""


@runtime_checkable
class Minlistelager(Protocol):
    """Porten med skrivesiden for merkingen (AD-3, navneregelen i spinen)."""

    def merkede(self) -> frozenset[str]:
        """Symbolene som er merket, blant dem som staar i lista."""

    def merk(self, symbol: str) -> None:
        """Merker aksjen. Er den merket fra foer, skjer ingenting."""

    def fjern(self, symbol: str) -> None:
        """Tar merket bort. Er aksjen ikke merket, skjer ingenting."""


def kontroller_symbol(symbol: str, symboler: Iterable[str]) -> None:
    """UkjentAksje naar symbolet ikke staar i lista."""
    if not isinstance(symbol, str) or symbol not in set(symboler):
        raise UkjentAksje(f"{symbol!r} staar ikke i lista og kan ikke merkes")


class MinneMinlistelager:
    """Minlistelager i minnet, for testene. Samme kontrakt som SQLite-adapteren."""

    def __init__(self, symboler: Iterable[str]):
        self._symboler = frozenset(symboler)
        self._merket: set[str] = set()

    def merkede(self) -> frozenset[str]:
        return frozenset(self._merket & self._symboler)

    def merk(self, symbol: str) -> None:
        kontroller_symbol(symbol, self._symboler)
        self._merket.add(symbol)

    def fjern(self, symbol: str) -> None:
        kontroller_symbol(symbol, self._symboler)
        self._merket.discard(symbol)
