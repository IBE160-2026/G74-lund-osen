"""Porten for vurderingene: typene og kontrakten, uten I/O - FR-408, AD-3, AD-7.

Vurderingen er det loesningen mente om en aksje en boersdag. Den kan ikke
regnes ut paa nytt, for en omregning gir dagens parametres svar, ikke
datidens. Derfor har porten bare skriv og les (AD-7), og skriv avviser
enhver dato som ikke er inneveerende boersdag. Den kontrollen ligger i
adapteren, fordi porten ikke importerer kjernen: dette er en loevnode, som
kursdata.py.

Det finnes med vilje ikke noe minnelager. Reglene for overskriving skal staa
ett sted, i adapterens upsert, og testene bruker SQLite i minnet.

En rad har enten en Vurdering eller en Grunn (punkt 24 i prd.md §8). Grunnen
sier hvorfor kjoeringen ikke kunne vurdere aksjen, saa ingen rad paa en
boersdag bare betyr at kommandoen ikke ble kjoert (FR-409).
"""

import math
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Protocol, runtime_checkable

# Samme tekster som signalberegning.POSITIV, NEGATIV, BLANDET og INGEN. Porten
# importerer ikke kjernen, saa en test binder de to sammen.
RETNINGER = ("Positiv", "Negativ", "Blandet", "Ingen")

SJEKKVERDIER = (-1, 0, 1)


class Grunn(StrEnum):
    """Hvorfor kjoeringen ikke kunne vurdere aksjen - punkt 24 i prd.md §8.

    Verdiene er radene i tabellen grunn (0002). En ny grunn er en ny verdi
    her og en INSERT INTO grunn i en ny migrasjon.
    """

    SYMBOL_FEILET = "symbol_feilet"            # AD-15
    KURS_IKKE_FRA_DAGEN = "kurs_ikke_fra_dagen"  # FR-402, punkt 23
    SIGNAL_IKKE_REGNET = "signal_ikke_regnet"    # FR-204


class UgyldigVurdering(ValueError):
    """En verdi Vurdering ikke godtar. Ogsaa feil type gir denne."""


def _heltall(verdi) -> bool:
    return isinstance(verdi, int) and not isinstance(verdi, bool)


@dataclass(frozen=True)
class Vurdering:
    """Vurderingen slik den var, med feltene i FR-408.

    styrke er summen av de tre sjekkenes absoluttverdier, som i
    signalberegning (FR-704). slutt og justert_slutt kopieres fra kursen
    vurderingen bygde paa, uten fremmednoekkel (AD-18).
    """

    styrke: int
    retning: str
    trend: int
    bevegelse: int
    interesse: int
    slutt: float
    justert_slutt: float

    def __post_init__(self):
        for navn in ("trend", "bevegelse", "interesse"):
            verdi = getattr(self, navn)
            if not _heltall(verdi) or verdi not in SJEKKVERDIER:
                raise UgyldigVurdering(f"{navn} maa vaere -1, 0 eller 1, fikk {verdi!r}")
        if not _heltall(self.styrke) or not 0 <= self.styrke <= 3:
            raise UgyldigVurdering(f"styrke maa vaere et heltall 0-3, fikk {self.styrke!r}")
        sum_sjekker = abs(self.trend) + abs(self.bevegelse) + abs(self.interesse)
        if self.styrke != sum_sjekker:
            raise UgyldigVurdering(
                f"styrke {self.styrke} stemmer ikke med sjekkene, som gir {sum_sjekker}"
            )
        if self.retning not in RETNINGER:
            raise UgyldigVurdering(f"retning maa vaere en av {RETNINGER}, fikk {self.retning!r}")
        for navn in ("slutt", "justert_slutt"):
            verdi = getattr(self, navn)
            if isinstance(verdi, bool) or not isinstance(verdi, (int, float)):
                raise UgyldigVurdering(f"{navn} maa vaere et tall, fikk {verdi!r}")
            try:
                endelig = math.isfinite(verdi)
            except OverflowError:
                endelig = False
            if not endelig or verdi <= 0:
                raise UgyldigVurdering(
                    f"{navn} maa vaere et endelig tall over null, fikk {verdi!r}"
                )


@runtime_checkable
class Vurderingslager(Protocol):
    """Porten for vurderingene - AD-3, AD-7. Bare skriv og les.

    Det finnes med vilje ingen slett og ingen endre. Fravaeret er invarianten
    (AD-7), og testen ser paa protokollen, ikke paa en implementasjon.
    """

    def skriv(self, symbol: str, dato: date, innhold: "Vurdering | Grunn") -> bool:
        """Skriv dagens rad for symbolet. Returnerer om raden ble skrevet.

        dato maa vaere inneveerende boersdag i Europe/Oslo, regnet fra
        lagerets klokke. Enhver annen dato reiser, og da skrives ingenting.
        Samme (symbol, dato) igjen skriver over, og den siste vinner. Unntaket
        er en Grunn over en Vurdering: den ignoreres, og skriv gir False uten
        aa reise, saa en kjoering der ett symbol feiler, ikke stopper (AD-15).
        """

    def les(self, symbol: str, dato: date) -> "Vurdering | Grunn | None":
        """Raden for symbolet og datoen. None hvis den ikke finnes."""
