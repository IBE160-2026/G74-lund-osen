"""Gemini med egen noekkel - story 10.7, FR-604, FR-605, FR-608, AD-2, AD-8,
AD-12.

Skall: én hentefunksjon mot Gemini, injisert (AD-2), som standard http i
ki_sky.py. Testene gir en falsk, og nettsperren i conftest.py stopper en
ekte (story 4.0). Ingen test kaller Gemini.

Kallet er Interactions API, med noekkelen i headeren x-goog-api-key og
store: false, som dokumentasjonen viser (spesifikasjonen 10.7, «Kallene,
slik dokumentasjonen sier»). Noekkelen staar aldri i adressen. Modellen er
Gemini 3.5 Flash-Lite (avgjoerelsen 04.10).

Bare status completed gir en tekst. incomplete betyr at teksten ble kortet
av, og den lagres ikke som en hel tekst (gjennomgangen, ECH4, BH2). Alt som
gaar galt, gir ModellFeilet med en kort grunn uten noekkelen (ki_sky.py).
"""

import ki_sky
from ki_modell import ModellFeilet, Modellsvar

NAVN = "Gemini"
NOEKKEL_VARIABEL = "OSE_KI_GEMINI_NOKKEL"
ADRESSE = "https://generativelanguage.googleapis.com/v1beta/interactions"
MODELL = "gemini-3.5-flash-lite"
LENGSTE_SVAR = 1024
TIDSFRIST = 60


def _deler(svar: dict) -> list:
    """Tekstdelene i stegene med type model_output."""
    steg = svar.get("steps")
    if not isinstance(steg, list):
        return []
    return [
        del_.get("text")
        for s in steg
        if isinstance(s, dict) and s.get("type") == "model_output" and isinstance(s.get("content"), list)
        for del_ in s["content"]
        if isinstance(del_, dict) and del_.get("type") == "text"
    ]


class GeminiModell:
    """Modell (porten i ki_modell.py) mot Gemini, tjenesten «gemini»."""

    tjeneste = "gemini"

    def __init__(
        self, noekkel: str | None, modell: str = MODELL, hent: ki_sky.Http | None = None, tidsfrist: float = TIDSFRIST
    ):
        self._noekkel = (noekkel or "").strip()
        self.modell = modell
        # Slaas opp ved kallet naar ingen er gitt, saa en test kan bytte den.
        self._hent = hent
        self._tidsfrist = tidsfrist

    def __repr__(self) -> str:
        return f"GeminiModell(modell={self.modell!r})"

    def lag_tekst(self, prompt: str) -> Modellsvar:
        ki_sky.sjekk_noekkel(self._noekkel, NOEKKEL_VARIABEL)
        headere = {"Content-Type": "application/json", "x-goog-api-key": self._noekkel}
        kropp = {
            "model": self.modell,
            "input": prompt,
            "store": False,
            "generation_config": {"max_output_tokens": LENGSTE_SVAR},
        }
        svar = ki_sky.kall(NAVN, self._hent or ki_sky.http, ADRESSE, headere, kropp, self._tidsfrist)
        status = svar.get("status")
        if status == "incomplete":
            raise ModellFeilet(f"svaret fra {NAVN} ble kortet av")
        if status != "completed":
            raise ModellFeilet(f"{NAVN} ga ingen ferdig tekst")
        return Modellsvar(
            tekst=ki_sky.tekst_fra(NAVN, _deler(svar)),
            modell=self.modell,
            modell_id=ki_sky.modell_id(svar, self.modell),
        )
