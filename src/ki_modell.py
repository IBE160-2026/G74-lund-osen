"""Porten Modell og teksten som lages av den - story 10.2, FR-603, FR-604,
FR-605, FR-608, AD-2, AD-8.

Hver modelltjeneste er en egen kilde med én hentefunksjon i sin egen
skallfil (ki_lokal.py for Ollama, i PR F). Alle oppfyller porten Modell, og
funksjonen injiseres (AD-2). Testene bruker en falsk modell (AD-8), og ingen
test kaller en ekte tjeneste.

lag_ki_rad er det hentekommandoen gjoer for én aksje (PR F kobler den inn):
den lager prompten av grunnlaget, kaller modellen, kontrollerer teksten mot
grunnlaget (FR-603) og gir raden som skal i KILogg (FR-604). Alt som gaar
galt hos modellen, gir en rad uten tekst og med grunnen: ModellFeilet, et
svar som ikke er et Modellsvar, en tom tekst, og et svar med verdier KIRad
ikke godtar. Da reises ingenting, og hentingen gaar videre (NFR-04). En feil
i grunnlaget eller emnet er en feil i koden vaar, og reises foer modellen
kalles, saa ingen kall gaar tapt.
"""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ki_kontroll import kontroller
from ki_prompt import PROMPTVERSJON, lag_prompt
from kilogg import AKSJE, Emne, KIRad, UgyldigKIRad

# Grunnen fra en feil hos modellen havner i loggen. Den kortes av, og noe som
# ser ut som en noekkel, fjernes (regel 10).
_LENGSTE_GRUNN = 200
_NOEKKEL = re.compile(r"(?i)((?:api[_-]?)?key|token|n(?:oe|ø)kkel|secret|passord)(\s*[=:]\s*)\S+")


class ModellFeilet(Exception):
    """Modellen ga ingen tekst: tidsavbrudd, feil fra tjenesten, eller at den
    ikke kjoerer. Adapteren gjoer alle feil hos tjenesten om til denne."""


@dataclass(frozen=True)
class Modellsvar:
    """Det modellen svarte, med det FR-604 og FR-605 krever om kjoeringen."""

    tekst: str
    modell: str
    modell_id: str | None = None
    seed: int | None = None
    temperatur: float | None = None
    maskinvare: str | None = None
    ollama_versjon: str | None = None


@runtime_checkable
class Modell(Protocol):
    """Porten for en modelltjeneste (AD-2). tjeneste er navnet i FR-608, og
    modell er modellnavnet som brukes naar tjenesten ikke svarer. lag_tekst
    reiser ModellFeilet for alt som gaar galt hos tjenesten."""

    tjeneste: str
    modell: str

    def lag_tekst(self, prompt: str) -> Modellsvar:
        """Teksten for prompten. Reiser ModellFeilet naar det ikke blir noen."""


def _grunn(tekst: str) -> str:
    tekst = _NOEKKEL.sub(r"\1\2***", " ".join(str(tekst).split()))
    return "modellen feilet" + (f": {tekst[:_LENGSTE_GRUNN]}" if tekst else "")


def _uten_tekst(emne, grunnlag, regelen, modell, grunn) -> KIRad:
    return KIRad(
        emne=emne, grunnlag=grunnlag, regelen=regelen, tekst=None, besto=False, grunn=grunn,
        promptversjon=PROMPTVERSJON, tjeneste=modell.tjeneste, modell=modell.modell,
    )


def lag_ki_rad(emne: Emne, grunnlag: Mapping[str, object], regelen: str, modell: Modell) -> KIRad:
    """Kall modellen én gang og gi raden for KILogg.

    Raden har alltid promptversjonen og modellen (FR-605). Besto teksten ikke
    kontrollen, har raden teksten og grunnene, og den vises ikke (FR-603).
    """
    if not isinstance(emne, Emne) or emne.slag != AKSJE:
        raise ValueError("lag_ki_rad gjelder én aksje og én dag (emnet aksje)")
    if type(grunnlag.get("styrke")) is not int or type(grunnlag.get("retning")) is not str:
        raise ValueError("grunnlaget maa ha styrke og retning, som fra ki_grunnlag")
    try:
        svar = modell.lag_tekst(lag_prompt(grunnlag))
    except ModellFeilet as feil:
        return _uten_tekst(emne, grunnlag, regelen, modell, _grunn(str(feil)))
    if not isinstance(svar, Modellsvar):
        return _uten_tekst(emne, grunnlag, regelen, modell, _grunn("svaret var ikke et Modellsvar"))
    tekst = svar.tekst.strip() if isinstance(svar.tekst, str) else ""
    kjoering = dict(
        promptversjon=PROMPTVERSJON, tjeneste=modell.tjeneste, modell=svar.modell,
        modell_id=svar.modell_id, seed=svar.seed, temperatur=svar.temperatur,
        maskinvare=svar.maskinvare, ollama_versjon=svar.ollama_versjon,
    )
    try:
        if not tekst:
            return KIRad(emne=emne, grunnlag=grunnlag, regelen=regelen, tekst=None, besto=False,
                         grunn=_grunn("tom tekst"), **kjoering)
        kontroll = kontroller(tekst, grunnlag)
        return KIRad(emne=emne, grunnlag=grunnlag, regelen=regelen, tekst=tekst,
                     besto=kontroll.besto, grunn=kontroll.grunn, **kjoering)
    except UgyldigKIRad:
        return _uten_tekst(emne, grunnlag, regelen, modell, _grunn("ugyldige verdier i svaret"))
