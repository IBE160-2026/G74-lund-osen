"""Porten for KI-loggen: typene og kontrakten, uten I/O - FR-604, FR-605,
AD-3, AD-7, story 4.2.

KI-loggen er det KI-laget la til, med det regelen sa og det modellen fikk.
Den kan ikke lages paa nytt: en ny kjoering gir en annen tekst, kanskje med en
annen prompt eller modell. Derfor har porten bare skriv og lesemetoder (AD-7),
og skriv godtar bare inneveerende boersdag. Den kontrollen ligger i
implementasjonene, fordi porten ikke importerer kjernen: dette er en
loevnode, som vurderingsdata.py.

Det er en logg for begge planene, ikke to (story 4.2): emnet er en aksje og en
boersdag (plan B), en melding (plan A) eller en boersdag alene, for teksten om
dagen paa forsiden (FR-607, svar 6 kl. 15:53). Finnes raden for emnet, staar
den, ogsaa naar modellen feilet (FR-604, svar 2 kl. 15:53). Da kalles ikke
modellen paa nytt.

Implementasjonene er MinneKILogg (kilogg_minne.py), som testene bruker, og
SQLite-adapteren i story 4.3.
"""

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from types import MappingProxyType
from typing import Protocol, runtime_checkable

AKSJE = "aksje"
MELDING = "melding"
DAG = "dag"
SLAG = (AKSJE, MELDING, DAG)

# Tjenestene i FR-608. «av» er ikke her: med KI av skrives ingen rad.
TJENESTER = ("lokal", "gemini", "anthropic", "openai")

# Hvordan modellen kjoerte (FR-604). None for en tjeneste paa nettet, der det
# ikke kan vites.
MASKINVARE = ("gpu", "cpu")


class UgyldigKIRad(ValueError):
    """En verdi Emne eller KIRad ikke godtar. Ogsaa feil type gir denne."""


def _tekst(navn: str, verdi) -> str:
    if not isinstance(verdi, str) or not verdi.strip():
        raise UgyldigKIRad(f"{navn} maa vaere en tekst som ikke er tom, fikk {verdi!r}")
    return verdi


def _tekst_eller_ingen(navn: str, verdi) -> str | None:
    return None if verdi is None else _tekst(navn, verdi)


@dataclass(frozen=True)
class Emne:
    """Hva raden forklarer. Lag den med Emne.aksje, Emne.melding eller
    Emne.dagen, saa slaget og feltene alltid hoerer sammen.

    En aksje har symbol og ingen melding, en melding har melding_id og ikke
    symbol, og dagen har ingen av dem. Alt annet avvises, ogsaa en rad med
    begge (story 4.2).
    """

    slag: str
    dato: date
    symbol: str | None = None
    melding_id: str | None = None

    def __post_init__(self):
        if self.slag not in SLAG:
            raise UgyldigKIRad(f"slag maa vaere en av {SLAG}, fikk {self.slag!r}")
        if not isinstance(self.dato, date) or isinstance(self.dato, datetime):
            raise UgyldigKIRad(f"dato maa vaere datetime.date, fikk {self.dato!r}")
        if self.slag == AKSJE:
            _tekst("symbol", self.symbol)
        elif self.symbol is not None:
            raise UgyldigKIRad(f"et emne av slaget {self.slag} har ikke symbol, fikk {self.symbol!r}")
        if self.slag == MELDING:
            _tekst("melding_id", self.melding_id)
        elif self.melding_id is not None:
            raise UgyldigKIRad(
                f"et emne av slaget {self.slag} har ikke melding_id, fikk {self.melding_id!r}"
            )

    @classmethod
    def aksje(cls, symbol: str, dato: date) -> "Emne":
        return cls(AKSJE, dato, symbol=symbol)

    @classmethod
    def melding(cls, melding_id: str, dato: date) -> "Emne":
        return cls(MELDING, dato, melding_id=melding_id)

    @classmethod
    def dagen(cls, dato: date) -> "Emne":
        return cls(DAG, dato)


def _som_json(grunnlag) -> Mapping[str, object]:
    """Grunnlaget slik det ble sendt, som en kopi ingen kan endre etterpaa.

    Det maa kunne skrives som JSON, med tekst som noekler, fordi adapteren
    lagrer det slik (4.3). NaN og uendelig avvises, fordi JSON ikke har dem.
    """
    if not isinstance(grunnlag, Mapping):
        raise UgyldigKIRad(f"grunnlag maa vaere en mapping, fikk {grunnlag!r}")
    if not all(isinstance(noekkel, str) for noekkel in grunnlag):
        raise UgyldigKIRad("noeklene i grunnlaget maa vaere tekst")
    try:
        kopi = json.loads(json.dumps(dict(grunnlag), allow_nan=False))
    except (TypeError, ValueError) as feil:
        raise UgyldigKIRad(f"grunnlaget kan ikke skrives som JSON: {feil}") from feil
    return MappingProxyType(kopi)


@dataclass(frozen=True)
class KIRad:
    """En rad i KI-loggen, med feltene i FR-604 og FR-605.

    De felles feltene (story 4.2) er datoen (i emnet), modellen,
    promptversjonen, hva regelen sa og hva KI la til. grunnlag er det modellen
    faktisk fikk (story 10.1), og tekst er det den svarte. besto sier om
    teksten besto kontrollen i FR-603. Gjorde den ikke det, eller feilet
    modellen, sier grunn hvorfor, og da finnes raden likevel (FR-604, NFR-04).

    tjeneste, modell_id, seed, temperatur, maskinvare og ollama_versjon er
    tilleggene 05.10 i FR-604 og FR-605. Det som ikke kan vites, er None.
    """

    emne: Emne
    grunnlag: Mapping[str, object]
    regelen: str
    tekst: str | None
    besto: bool
    grunn: str | None
    promptversjon: str
    tjeneste: str
    modell: str
    modell_id: str | None = None
    seed: int | None = None
    temperatur: float | None = None
    maskinvare: str | None = None
    ollama_versjon: str | None = None

    def __post_init__(self):
        if not isinstance(self.emne, Emne):
            raise UgyldigKIRad(f"emne maa vaere Emne, fikk {self.emne!r}")
        object.__setattr__(self, "grunnlag", _som_json(self.grunnlag))
        if not isinstance(self.regelen, str):
            raise UgyldigKIRad(f"regelen maa vaere tekst, fikk {self.regelen!r}")
        _tekst_eller_ingen("tekst", self.tekst)
        if not isinstance(self.besto, bool):
            raise UgyldigKIRad(f"besto maa vaere True eller False, fikk {self.besto!r}")
        _tekst_eller_ingen("grunn", self.grunn)
        if self.besto and (self.tekst is None or self.grunn is not None):
            raise UgyldigKIRad("en tekst som besto, har tekst og ingen grunn")
        if not self.besto and self.grunn is None:
            raise UgyldigKIRad("en rad uten bestaatt tekst maa ha en grunn (FR-604)")
        _tekst("promptversjon", self.promptversjon)
        _tekst("modell", self.modell)
        if self.tjeneste not in TJENESTER:
            raise UgyldigKIRad(f"tjeneste maa vaere en av {TJENESTER}, fikk {self.tjeneste!r}")
        _tekst_eller_ingen("modell_id", self.modell_id)
        _tekst_eller_ingen("ollama_versjon", self.ollama_versjon)
        if self.seed is not None and (not isinstance(self.seed, int) or isinstance(self.seed, bool)):
            raise UgyldigKIRad(f"seed maa vaere et heltall eller None, fikk {self.seed!r}")
        if self.temperatur is not None:
            if isinstance(self.temperatur, bool) or not isinstance(self.temperatur, (int, float)):
                raise UgyldigKIRad(f"temperatur maa vaere et tall eller None, fikk {self.temperatur!r}")
            if not math.isfinite(self.temperatur) or self.temperatur < 0:
                raise UgyldigKIRad(f"temperatur maa vaere endelig og ikke negativ, fikk {self.temperatur!r}")
            object.__setattr__(self, "temperatur", float(self.temperatur))
        if self.maskinvare is not None and self.maskinvare not in MASKINVARE:
            raise UgyldigKIRad(f"maskinvare maa vaere en av {MASKINVARE} eller None, fikk {self.maskinvare!r}")


@runtime_checkable
class KILogg(Protocol):
    """Porten for KI-loggen - AD-3, AD-7. Bare skriv og lesemetoder.

    Det finnes med vilje ingen slett og ingen endre. Fravaeret er invarianten
    (AD-7), og testen ser paa protokollen, ikke paa en implementasjon.
    """

    def skriv(self, rad: KIRad) -> bool:
        """Skriv raden. Returnerer om den ble skrevet.

        Datoen i emnet maa vaere inneveerende boersdag i Europe/Oslo, regnet
        fra loggens klokke. Enhver annen dato reiser ValueError, og da skrives
        ingenting. Finnes en rad for emnet, staar den, ogsaa naar modellen
        feilet: skriv gir False uten aa reise, saa hentingen gaar videre
        (FR-604, svar 2 kl. 15:53).
        """

    def les(self, emne: Emne) -> KIRad | None:
        """Raden for emnet. None hvis den ikke finnes."""

    def les_alle(self) -> list[KIRad]:
        """Alle radene, av alle slag, ordnet etter dato og saa rekkefoelgen
        de ble skrevet i."""
