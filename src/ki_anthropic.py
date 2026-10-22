"""Anthropic API med egen noekkel - story 10.7, FR-604, FR-605, FR-608, AD-2,
AD-8, AD-12.

Skall: én hentefunksjon mot Anthropic, injisert (AD-2), som standard http i
ki_sky.py. Testene gir en falsk, og nettsperren i conftest.py stopper en
ekte (story 4.0). Ingen test kaller Anthropic.

Kallet er Messages API, med noekkelen i headeren x-api-key og
anthropic-version 2023-06-01, som dokumentasjonen viser (spesifikasjonen
10.7, «Kallene, slik dokumentasjonen sier»). Noekkelen staar aldri i
adressen. Ingen temperatur: nyere modeller avviser den.

stop_reason refusal er et avslag, og max_tokens betyr at teksten ble kortet
av. Ingen av dem gir en tekst (gjennomgangen, ECH4, BH2). Alt som gaar
galt, gir ModellFeilet med en kort grunn uten noekkelen (ki_sky.py).
"""

import ki_sky
from ki_modell import ModellFeilet, Modellsvar

NAVN = "Anthropic"
NOEKKEL_VARIABEL = "OSE_KI_ANTHROPIC_NOKKEL"
ADRESSE = "https://api.anthropic.com/v1/messages"
VERSJON = "2023-06-01"
MODELL = "claude-haiku-5-5"
LENGSTE_SVAR = 1024
TIDSFRIST = 60


def _deler(svar: dict) -> list:
    """Tekstdelene i blokkene med type text."""
    innhold = svar.get("content")
    if not isinstance(innhold, list):
        return []
    return [blokk.get("text") for blokk in innhold if isinstance(blokk, dict) and blokk.get("type") == "text"]


class AnthropicModell:
    """Modell (porten i ki_modell.py) mot Anthropic API, tjenesten «anthropic»."""

    tjeneste = "anthropic"

    def __init__(
        self, noekkel: str | None, modell: str = MODELL, hent: ki_sky.Http | None = None, tidsfrist: float = TIDSFRIST
    ):
        self._noekkel = (noekkel or "").strip()
        self.modell = modell
        # Slaas opp ved kallet naar ingen er gitt, saa en test kan bytte den.
        self._hent = hent
        self._tidsfrist = tidsfrist

    def __repr__(self) -> str:
        return f"AnthropicModell(modell={self.modell!r})"

    def sjekk(self) -> str | None:
        """Grunnen naar noekkelen mangler eller ikke kan sendes, ellers None,
        uten kall. lag_ki_tekster kaller den foer foerste tekst, som for
        Ollama, og sier den nei, skrives ingen rader (spesifikasjonen 10.7b)."""
        return ki_sky.noekkel_feil(self._noekkel, NOEKKEL_VARIABEL)

    def lag_tekst(self, prompt: str) -> Modellsvar:
        ki_sky.sjekk_noekkel(self._noekkel, NOEKKEL_VARIABEL)
        headere = {"content-type": "application/json", "x-api-key": self._noekkel, "anthropic-version": VERSJON}
        kropp = {
            "model": self.modell,
            "max_tokens": LENGSTE_SVAR,
            "messages": [{"role": "user", "content": prompt}],
        }
        svar = ki_sky.kall(NAVN, self._hent or ki_sky.http, ADRESSE, headere, kropp, self._tidsfrist)
        if svar.get("stop_reason") == "refusal":
            raise ModellFeilet(f"{NAVN} avslo")
        if svar.get("stop_reason") == "max_tokens":
            raise ModellFeilet(f"svaret fra {NAVN} ble kortet av")
        return Modellsvar(
            tekst=ki_sky.tekst_fra(NAVN, _deler(svar)),
            modell=self.modell,
            modell_id=ki_sky.modell_id(svar, self.modell),
        )
