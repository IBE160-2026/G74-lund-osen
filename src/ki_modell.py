"""Porten Modell og teksten som lages av den - story 10.2, FR-603, FR-604,
FR-605, FR-608, AD-2, AD-8.

Hver modelltjeneste er en egen kilde med én hentefunksjon i sin egen
skallfil (ki_lokal.py for Ollama, i PR F). Alle oppfyller porten Modell, og
funksjonen injiseres (AD-2). Testene bruker en falsk modell (AD-8), og ingen
test kaller en ekte tjeneste.

lag_ki_rad er det hentekommandoen gjoer for én aksje (PR F kobler den inn):
den lager prompten av grunnlaget, kaller modellen, kontrollerer teksten mot
grunnlaget (FR-603) og gir raden som skal i KILogg (FR-604). Feiler modellen,
blir det en rad uten tekst og med grunnen, og ingenting reises videre, saa
hentingen gaar videre (NFR-04).
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ki_kontroll import kontroller
from ki_prompt import PROMPTVERSJON, lag_prompt
from kilogg import Emne, KIRad


class ModellFeilet(Exception):
    """Modellen ga ingen tekst: tidsavbrudd, feil fra tjenesten, eller at den
    ikke kjoerer. Meldingen havner i KIRad.grunn, saa den skal ikke ha noekler."""


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
    modell er modellnavnet som brukes naar tjenesten ikke svarer."""

    tjeneste: str
    modell: str

    def lag_tekst(self, prompt: str) -> Modellsvar:
        """Teksten for prompten. Reiser ModellFeilet naar det ikke blir noen."""


def lag_ki_rad(emne: Emne, grunnlag: Mapping[str, object], regelen: str, modell: Modell) -> KIRad:
    """Kall modellen én gang og gi raden for KILogg.

    Raden har alltid promptversjonen og modellen (FR-605). Besto teksten ikke
    kontrollen, har raden teksten og grunnene, og den vises ikke (FR-603).
    """
    try:
        svar = modell.lag_tekst(lag_prompt(grunnlag))
    except ModellFeilet as feil:
        return KIRad(
            emne=emne, grunnlag=grunnlag, regelen=regelen, tekst=None, besto=False,
            grunn=f"modellen feilet: {feil}".strip(), promptversjon=PROMPTVERSJON,
            tjeneste=modell.tjeneste, modell=modell.modell,
        )
    tekst = svar.tekst.strip() if isinstance(svar.tekst, str) else ""
    if not tekst:
        return KIRad(
            emne=emne, grunnlag=grunnlag, regelen=regelen, tekst=None, besto=False,
            grunn="modellen feilet: tom tekst", promptversjon=PROMPTVERSJON,
            tjeneste=modell.tjeneste, modell=svar.modell, modell_id=svar.modell_id,
            seed=svar.seed, temperatur=svar.temperatur, maskinvare=svar.maskinvare,
            ollama_versjon=svar.ollama_versjon,
        )
    kontroll = kontroller(tekst, grunnlag)
    return KIRad(
        emne=emne, grunnlag=grunnlag, regelen=regelen, tekst=tekst, besto=kontroll.besto,
        grunn=kontroll.grunn, promptversjon=PROMPTVERSJON, tjeneste=modell.tjeneste,
        modell=svar.modell, modell_id=svar.modell_id, seed=svar.seed,
        temperatur=svar.temperatur, maskinvare=svar.maskinvare,
        ollama_versjon=svar.ollama_versjon,
    )
