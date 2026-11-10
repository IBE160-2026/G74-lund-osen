"""Mine notater: porten for notatene, uten I/O - story 8.21, AD-3, AD-10,
AD-16 (gruppens svar 10.11 kl. 14:32).

Notatene er et eget datasett med webserveren som eneste skriver, som Min
liste, ønskene og innstillingene. Et notat har aksjen, dagen siden viste da
det ble skrevet, teksten og tidspunktet det ble lagret. Det kan slettes, men
ikke endres (spørsmål 7 i spec-8-21-egne-notater-paa-aksjesiden.md).

«Etterpå» under hvert notat står i etterpaa.py. Her står porten og
minneutgaven, uten andre importer enn standardbiblioteket, så
lagring_sqlite.py kan importere den. SQLite-adapteren er SqliteNotatlager i
lagring_sqlite.py.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol, runtime_checkable

# Spørsmål 2: høyst 280 tegn, også i CHECK i 0012.
MAKS_TEGN = 280


class UgyldigNotat(ValueError):
    """Teksten er tom eller for lang, eller aksjen står ikke i lista."""


@dataclass(frozen=True)
class Notat:
    id: int
    symbol: str
    dato: date
    tekst: str
    laget: datetime


@runtime_checkable
class Notatlager(Protocol):
    """Porten med skrivesiden for notatene (AD-3, navneregelen i spinen)."""

    def notater(self, symbol: str) -> list[Notat]:
        """Notatene for aksjen, den nyeste notatdagen først, og det sist
        lagrede først samme dag."""

    def skriv(self, symbol: str, dato: date, tekst: str, laget: datetime) -> Notat:
        """Lagrer et notat. Teksten renskes med rens(), og en tom eller for
        lang tekst og et symbol som ikke står i lista, avvises."""

    def slett(self, symbol: str, notat_id: int) -> bool:
        """Sletter notatet når det hører til aksjen. Gir om noe ble slettet."""


def rens(tekst: object) -> str:
    """Teksten slik den lagres: ett avsnitt, uten mellomrom før og etter
    (spørsmål 2). UgyldigNotat når den er tom eller over MAKS_TEGN."""
    if not isinstance(tekst, str):
        raise UgyldigNotat("notatet må være tekst")
    renset = " ".join(tekst.split())
    # Gjennomgangen (BH9, ECH5): tegn uten bredde, som U+200B, er ikke
    # mellomrom for split(), men et notat med bare dem er like tomt.
    if not any(tegn.isprintable() and not tegn.isspace() for tegn in renset):
        raise UgyldigNotat("notatet er tomt")
    if len(renset) > MAKS_TEGN:
        raise UgyldigNotat(f"notatet har over {MAKS_TEGN} tegn")
    return renset


def sorter(notater: Iterable[Notat]) -> list[Notat]:
    """Den nyeste notatdagen først, og det sist lagrede først samme dag."""
    return sorted(notater, key=lambda n: (n.dato, n.laget, n.id), reverse=True)


class MinneNotatlager:
    """Notatlager i minnet, for testene. Samme kontrakt som SQLite-adapteren."""

    def __init__(self, symboler: Iterable[str]):
        self._symboler = frozenset(symboler)
        self._notater: dict[int, Notat] = {}
        self._neste = 1

    def notater(self, symbol: str) -> list[Notat]:
        return sorter(n for n in self._notater.values() if n.symbol == symbol)

    def skriv(self, symbol: str, dato: date, tekst: str, laget: datetime) -> Notat:
        if symbol not in self._symboler:
            raise UgyldigNotat(f"{symbol!r} står ikke i lista")
        # Gjennomgangen (BH10): samme kontroll av dagen som SQLite-adapteren.
        if not isinstance(dato, date) or isinstance(dato, datetime):
            raise UgyldigNotat("dagen må være en dato")
        notat = Notat(self._neste, symbol, dato, rens(tekst), laget)
        self._notater[notat.id] = notat
        self._neste += 1
        return notat

    def slett(self, symbol: str, notat_id: int) -> bool:
        notat = self._notater.get(notat_id)
        if notat is None or notat.symbol != symbol:
            return False
        del self._notater[notat_id]
        return True
