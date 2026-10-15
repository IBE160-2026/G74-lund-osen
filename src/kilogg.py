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
modellen paa nytt. Noekkelen er hele emnet: slaget, datoen, symbolet og
meldingen, der feltene slaget ikke har, er tomme.

Implementasjonene er MinneKILogg (kilogg_minne.py), som testene bruker, og
SQLite-adapteren i story 4.3.
"""

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from types import MappingProxyType
from typing import Protocol, runtime_checkable

AKSJE = "aksje"
MELDING = "melding"
DAG = "dag"
SLAG = (AKSJE, MELDING, DAG)

# Tjenestene i FR-608. «av» er ikke her: med KI av skrives ingen rad.
LOKAL = "lokal"
TJENESTER = (LOKAL, "gemini", "anthropic", "openai")

# Hvordan modellen kjoerte (FR-604). Bare for den lokale modellen. For en
# tjeneste paa nettet kan det ikke vites, og da er feltet None.
MASKINVARE = ("gpu", "cpu")

# SQLite lagrer heltall med 64 bit (4.3).
_STOERSTE_SEED = 2**63

# Hvor dypt grunnlaget kan vaere. Grunnlaget fra 10.1 er flatt.
_DYPESTE = 20


class UgyldigKIRad(ValueError):
    """En verdi Emne eller KIRad ikke godtar. Ogsaa feil type gir denne."""


class IkkeInnevaerendeBoersdag(ValueError):
    """skriv fikk en annen dato enn inneveerende boersdag (AD-7).

    Egen type, saa hentingen kan skille den fra en feil i klokka eller
    kalenderen (UtenforKalenderen) og fra en ugyldig rad (gjennomgangen av
    4.2, BH5).
    """


def _tekst(navn: str, verdi) -> str:
    if not isinstance(verdi, str) or not verdi.strip():
        raise UgyldigKIRad(f"{navn} maa vaere en tekst som ikke er tom, fikk {verdi!r}")
    return verdi


def _tekst_eller_ingen(navn: str, verdi) -> str | None:
    return None if verdi is None else _tekst(navn, verdi)


def _noekkeltekst(navn: str, verdi) -> str:
    """Symbol og melding_id er noekler: uten mellomrom rundt, saa samme aksje
    ikke kan faa to rader (gjennomgangen, BH1)."""
    _tekst(navn, verdi)
    if verdi != verdi.strip():
        raise UgyldigKIRad(f"{navn} kan ikke ha mellomrom rundt seg, fikk {verdi!r}")
    return verdi


@dataclass(frozen=True)
class Emne:
    """Hva raden forklarer. Lag den med Emne.aksje, Emne.melding eller
    Emne.dagen, saa slaget og feltene alltid hoerer sammen.

    En aksje har symbol og ingen melding, en melding har melding_id og ikke
    symbol, og dagen har ingen av dem. Alt annet avvises, ogsaa en rad med
    begge (story 4.2). Symbolet skrives med store bokstaver, som i
    AKSJEUNIVERS.
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
            _noekkeltekst("symbol", self.symbol)
            if self.symbol != self.symbol.upper():
                raise UgyldigKIRad(f"symbol skrives med store bokstaver, fikk {self.symbol!r}")
        elif self.symbol is not None:
            raise UgyldigKIRad(f"et emne av slaget {self.slag} har ikke symbol, fikk {self.symbol!r}")
        if self.slag == MELDING:
            _noekkeltekst("melding_id", self.melding_id)
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


def _frys(verdi, dybde: int = 0):
    """Grunnlaget som JSON-verdier ingen kan endre: en mapping blir
    MappingProxyType og en liste blir tuple, paa alle nivaaer (BH2).

    Bare det JSON kan holde uten aa endre det, godtas: tekst som noekler paa
    alle nivaaer, tekst, heltall, endelige tall, True, False, None og lister.
    En tuple avvises, fordi JSON ville gjort den til en liste (BH3).
    """
    if dybde > _DYPESTE:
        raise UgyldigKIRad(f"grunnlaget er dypere enn {_DYPESTE} nivaaer")
    if isinstance(verdi, Mapping):
        if not all(isinstance(noekkel, str) for noekkel in verdi):
            raise UgyldigKIRad("noeklene i grunnlaget maa vaere tekst, paa alle nivaaer")
        return MappingProxyType({n: _frys(v, dybde + 1) for n, v in verdi.items()})
    if isinstance(verdi, list):
        return tuple(_frys(v, dybde + 1) for v in verdi)
    if verdi is None or isinstance(verdi, (str, bool, int)):
        return verdi
    if isinstance(verdi, float):
        if not math.isfinite(verdi):
            raise UgyldigKIRad(f"grunnlaget kan ikke ha {verdi!r}, JSON har det ikke")
        return verdi
    raise UgyldigKIRad(f"grunnlaget kan ikke skrives som JSON: {verdi!r}")


def _tine(verdi):
    """Motsatt av _frys: vanlige dict og list, for json.dumps."""
    if isinstance(verdi, Mapping):
        return {n: _tine(v) for n, v in verdi.items()}
    if isinstance(verdi, tuple):
        return [_tine(v) for v in verdi]
    return verdi


@dataclass(frozen=True)
class KIRad:
    """En rad i KI-loggen, med feltene i FR-604 og FR-605.

    De felles feltene (story 4.2) er datoen (i emnet), modellen,
    promptversjonen, hva regelen sa og hva KI la til. grunnlag er det modellen
    faktisk fikk (story 10.1), og tekst er det den svarte. besto sier om
    teksten besto kontrollen i FR-603. Gjorde den ikke det, eller feilet
    modellen, sier grunn hvorfor, og da finnes raden likevel (FR-604, NFR-04).
    Feilet modellen, har raden ingen tekst (modellen_feilet).

    tjeneste, modell_id, seed, temperatur, maskinvare og ollama_versjon er
    tilleggene 05.10 i FR-604 og FR-605. Det som ikke kan vites, er None.
    maskinvare og ollama_versjon gjelder bare den lokale modellen.

    Raden kan hashes, uten grunnlaget, som ikke kan det (BH9).
    """

    emne: Emne
    grunnlag: Mapping[str, object] = field(hash=False)
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
        if not isinstance(self.grunnlag, Mapping):
            raise UgyldigKIRad(f"grunnlag maa vaere en mapping, fikk {self.grunnlag!r}")
        object.__setattr__(self, "grunnlag", _frys(self.grunnlag))
        _tekst("regelen", self.regelen)
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
        if self.seed is not None:
            if not isinstance(self.seed, int) or isinstance(self.seed, bool):
                raise UgyldigKIRad(f"seed maa vaere et heltall eller None, fikk {self.seed!r}")
            if not -_STOERSTE_SEED <= self.seed < _STOERSTE_SEED:
                raise UgyldigKIRad(f"seed maa ligge innenfor 64 bit, fikk {self.seed!r}")
        if self.temperatur is not None:
            if isinstance(self.temperatur, bool) or not isinstance(self.temperatur, (int, float)):
                raise UgyldigKIRad(f"temperatur maa vaere et tall eller None, fikk {self.temperatur!r}")
            try:
                temperatur = float(self.temperatur)
            except OverflowError as feil:
                raise UgyldigKIRad(f"temperatur er for stor: {self.temperatur!r}") from feil
            if not math.isfinite(temperatur) or temperatur < 0:
                raise UgyldigKIRad(f"temperatur maa vaere endelig og ikke negativ, fikk {self.temperatur!r}")
            object.__setattr__(self, "temperatur", temperatur)
        if self.maskinvare is not None and self.maskinvare not in MASKINVARE:
            raise UgyldigKIRad(f"maskinvare maa vaere en av {MASKINVARE} eller None, fikk {self.maskinvare!r}")
        if self.tjeneste != LOKAL and (self.maskinvare is not None or self.ollama_versjon is not None):
            raise UgyldigKIRad("maskinvare og ollama_versjon gjelder bare den lokale modellen (FR-605)")

    @property
    def modellen_feilet(self) -> bool:
        """Modellen ga ingen tekst (FR-604, NFR-04). En tekst som ikke besto
        kontrollen, har tekst og grunn."""
        return self.tekst is None

    def grunnlag_som_json(self) -> str:
        """Grunnlaget som JSON, med noeklene sortert, for adapteren i 4.3."""
        return json.dumps(_tine(self.grunnlag), ensure_ascii=False, sort_keys=True, allow_nan=False)


@runtime_checkable
class KILogg(Protocol):
    """Porten for KI-loggen - AD-3, AD-7. Bare skriv og lesemetoder.

    Det finnes med vilje ingen slett og ingen endre. Fravaeret er invarianten
    (AD-7), og testen ser paa protokollen, ikke paa en implementasjon.
    """

    def skriv(self, rad: KIRad) -> bool:
        """Skriv raden. Returnerer om den ble skrevet.

        Datoen i emnet maa vaere inneveerende boersdag i Europe/Oslo, regnet
        fra loggens klokke. En annen dato reiser IkkeInnevaerendeBoersdag, og
        da skrives ingenting. Finnes en rad for emnet (hele emnet er
        noekkelen), staar den, ogsaa naar modellen feilet: skriv gir False
        uten aa reise, saa hentingen gaar videre (FR-604, svar 2 kl. 15:53).
        """

    def les(self, emne: Emne) -> KIRad | None:
        """Raden for emnet. None hvis den ikke finnes."""

    def les_alle(self) -> list[KIRad]:
        """Alle radene, av alle slag, ordnet etter dato og saa rekkefoelgen
        de ble skrevet i."""
