"""Porten sidene leser gjennom: typene og kontrakten, uten I/O - story 2.2b,
FR-101, FR-408, FR-409, AD-3, AD-21.

Oversikten trenger, per aksje, selskapet fra aksje, nyeste og forrige kurs,
naar serien sist ble hentet, og dagens rad i vurdering. Det er tre datasett,
og hvert har sin egen port med sin egen skriver (AD-3). Denne porten skriver
ingenting og har ingen skriver: den leser paa tvers av datasettene, i en
spoerring med join, saa sidene faar en vei til tallet (merknaden under AD-3).

Dagens vurdering er raden for datoen til nyeste kurs, ikke for dagens dato.
Har hentekommandoen ikke skrevet en ny kurs i dag, viser siden gaarsdagens
vurdering med gaarsdagens dato (FR-101), ogsaa naar dagens rad har en grunn.

Selskapene kommer fra aksje i basen, i rekkefoelgen der (rowid), og koden
antar aldri hvor mange det er (merknaden 2026-10-03 under AD-21).

Her staar bare typene og porten. Adapteren er SqliteOversiktsleser i
lagring_sqlite.py. Porten importerer ingen av dem og gjoer ingen I/O.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from kursdata import Aksje, Kursrad
from vurderingsdata import Grunn, Vurdering


@dataclass(frozen=True)
class Oversiktspost:
    """En aksje slik oversikten leser den.

    nyeste og forrige er de to siste kursradene, None naar de mangler.
    Mangler nyeste, har aksjen ingen kurser, og forrige og innhold er None.
    innhold er raden i vurdering for nyeste.dato, None naar den mangler.
    hentet er naar serien sist ble hentet, i UTC (AD-20).
    """

    aksje: Aksje
    nyeste: Kursrad | None
    forrige: Kursrad | None
    hentet: datetime | None
    innhold: Vurdering | Grunn | None


@runtime_checkable
class Oversiktsleser(Protocol):
    """Porten for oversikten. Bare lesemetoder, og en test holder det slik."""

    def oversikt(self) -> list[Oversiktspost]:
        """En post per aksje i aksje, i rowid-rekkefoelge."""

    def post(self, symbol: str) -> Oversiktspost | None:
        """Posten for symbolet, None hvis det ikke staar i aksje."""
