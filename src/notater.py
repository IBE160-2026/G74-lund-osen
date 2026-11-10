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


# --- Tillegget kl. 14:44: tenkte kjøp og salg ---------------------------------

Sjekker = tuple[int, int, int] | None


@dataclass(frozen=True)
class TenktKjoep:
    """Et tenkt kjøp ved et notat, med salget når det er notert.

    kjoep_etter og salg_etter er dagen sluttkursen må være etter (spørsmål 15):
    kursen er den første i serien etter den dagen, lest når siden vises.
    Sjekkene er (trend, bevegelse, interesse) slik de sto på siden ved
    trykket, eller None når dagen ikke var vurdert."""

    id: int
    notat: int
    symbol: str
    kjoept: datetime
    kjoep_etter: date
    kjoep_sjekker: Sjekker
    solgt: datetime | None = None
    salg_etter: date | None = None
    salg_sjekker: Sjekker = None

    @property
    def aapent(self) -> bool:
        return self.solgt is None


def kontroller_sjekker(sjekker: Sjekker) -> Sjekker:
    if sjekker is None:
        return None
    if len(sjekker) != 3 or any(isinstance(s, bool) or s not in (-1, 0, 1) for s in sjekker):
        raise UgyldigNotat("sjekkene må være tre verdier -1, 0 eller 1")
    return tuple(sjekker)


class MinneNotatlagerMedKjoep(MinneNotatlager):
    """MinneNotatlager med de tenkte kjøpene, for testene. Samme kontrakt som
    SqliteNotatlager."""

    def __init__(self, symboler: Iterable[str]):
        super().__init__(symboler)
        self._kjoep: dict[int, TenktKjoep] = {}
        self._neste_kjoep = 1

    def alle_notater(self) -> list[Notat]:
        return sorter(self._notater.values())

    def kjoepene(self) -> dict[int, TenktKjoep]:
        return {k.notat: k for k in self._kjoep.values() if k.notat in self._notater}

    def slett(self, symbol: str, notat_id: int) -> bool:
        slettet = super().slett(symbol, notat_id)
        if slettet:
            self._kjoep = {i: k for i, k in self._kjoep.items() if k.notat != notat_id}
        return slettet

    def noter_kjoep(self, symbol: str, notat_id: int, kjoept: datetime, etter: date, sjekker: Sjekker) -> TenktKjoep:
        notat = self._notater.get(notat_id)
        if notat is None or notat.symbol != symbol or symbol not in self._symboler:
            raise UgyldigNotat("notatet hører ikke til aksjen")
        if any(k.notat == notat_id for k in self._kjoep.values()):
            raise UgyldigNotat("notatet har alt et tenkt kjøp")
        if any(k.symbol == symbol and k.aapent for k in self._kjoep.values()):
            raise UgyldigNotat("aksjen har alt et åpent tenkt kjøp")
        # Gjennomgangen av tilleggene (BH9): en id som aldri brukes på nytt.
        neste, self._neste_kjoep = self._neste_kjoep, self._neste_kjoep + 1
        kjoep = TenktKjoep(neste, notat_id, symbol, kjoept, etter, kontroller_sjekker(sjekker))
        self._kjoep[kjoep.id] = kjoep
        return kjoep

    def noter_salg(self, symbol: str, notat_id: int, solgt: datetime, etter: date, sjekker: Sjekker) -> TenktKjoep:
        kjoep = next((k for k in self._kjoep.values() if k.notat == notat_id and k.symbol == symbol), None)
        if kjoep is None or not kjoep.aapent:
            raise UgyldigNotat("notatet har ikke et åpent tenkt kjøp")
        if etter < kjoep.kjoep_etter:
            raise UgyldigNotat("salget kan ikke være før kjøpet")
        nytt = TenktKjoep(
            **{**kjoep.__dict__, "solgt": solgt, "salg_etter": etter, "salg_sjekker": kontroller_sjekker(sjekker)}
        )
        self._kjoep[kjoep.id] = nytt
        return nytt
