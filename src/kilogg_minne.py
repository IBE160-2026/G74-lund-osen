"""MinneKILogg: KI-loggen i minnet, for testene - story 4.2.

Samme regler som SQLite-adapteren i story 4.3: bare inneveerende boersdag,
og en rad som finnes, staar. Hele porten proeves mot denne, uten database.
"""

from collections.abc import Callable
from datetime import datetime

from boersdag import innevaerende_boersdag, norsk_dato
from kilogg import Emne, KIRad


class MinneKILogg:
    """KILogg i minnet. Klokka leses ved hvert kall til skriv."""

    def __init__(self, klokke: Callable[[], datetime]):
        self._klokke = klokke
        self._rader: dict[Emne, KIRad] = {}

    def skriv(self, rad: KIRad) -> bool:
        if not isinstance(rad, KIRad):
            raise TypeError(f"rad maa vaere KIRad, fikk {rad!r}")
        dagens = innevaerende_boersdag(norsk_dato(self._klokke()))
        if rad.emne.dato != dagens:
            raise ValueError(
                f"{rad.emne.dato.isoformat()} er ikke inneveerende boersdag "
                f"({dagens.isoformat()}). En eldre rad kan ikke skrives (AD-7)."
            )
        if rad.emne in self._rader:
            return False
        self._rader[rad.emne] = rad
        return True

    def les(self, emne: Emne) -> KIRad | None:
        return self._rader.get(emne)

    def les_alle(self) -> list[KIRad]:
        return sorted(self._rader.values(), key=lambda rad: rad.emne.dato)
