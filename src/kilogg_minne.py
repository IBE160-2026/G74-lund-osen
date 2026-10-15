"""MinneKILogg: KI-loggen i minnet, for testene - story 4.2.

Samme regler som SQLite-adapteren i story 4.3: bare inneveerende boersdag,
og en rad som finnes, staar. Hele porten proeves mot denne, uten database.
"""

from collections.abc import Callable
from datetime import datetime

from boersdag import innevaerende_boersdag, norsk_dato
from kilogg import Emne, IkkeInnevaerendeBoersdag, KIRad


class MinneKILogg:
    """KILogg i minnet. Klokka leses ved hvert kall til skriv."""

    def __init__(self, klokke: Callable[[], datetime]):
        if not callable(klokke):
            raise TypeError(f"klokke maa kunne kalles, fikk {klokke!r}")
        self._klokke = klokke
        self._rader: dict[Emne, KIRad] = {}

    def skriv(self, rad: KIRad) -> bool:
        if not isinstance(rad, KIRad):
            raise TypeError(f"rad maa vaere KIRad, fikk {rad!r}")
        naa = self._klokke()
        if not isinstance(naa, datetime) or naa.tzinfo is None:
            raise TypeError(f"klokka maa gi et tidspunkt med sone, ga {naa!r}")
        dagens = innevaerende_boersdag(norsk_dato(naa))
        if rad.emne.dato != dagens:
            raise IkkeInnevaerendeBoersdag(
                f"{rad.emne.dato.isoformat()} er ikke inneveerende boersdag "
                f"({dagens.isoformat()}). En eldre rad kan ikke skrives (AD-7)."
            )
        if rad.emne in self._rader:
            return False
        self._rader[rad.emne] = rad
        return True

    def les(self, emne: Emne) -> KIRad | None:
        if not isinstance(emne, Emne):
            raise TypeError(f"emne maa vaere Emne, fikk {emne!r}")
        return self._rader.get(emne)

    def les_alle(self) -> list[KIRad]:
        return sorted(self._rader.values(), key=lambda rad: rad.emne.dato)
