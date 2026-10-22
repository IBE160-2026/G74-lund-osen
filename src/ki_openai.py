"""OpenAI API med egen noekkel - story 10.7, FR-604, FR-605, FR-608, AD-2,
AD-8, AD-12.

Skall: én hentefunksjon mot OpenAI, http, og den injiseres (AD-2). Testene
gir en falsk http, og nettsperren i conftest.py stopper en ekte (story 4.0).
Ingen test kaller OpenAI.

Kallet er Responses API, med noekkelen i headeren Authorization: Bearer og
store: false, som dokumentasjonen viser (spesifikasjonen 10.7, «Kallene,
slik dokumentasjonen sier»). Noekkelen staar aldri i adressen.

Alt som gaar galt, gir ModellFeilet (ki_modell.py) med en kort grunn: HTTP-
statusen, tidsavbruddet eller typen paa feilen. Teksten fra tjenesten og
feilmeldingen fra requests kommer aldri med, fordi de kan inneholde
noekkelen eller adressen.
"""

from collections.abc import Callable

import requests

from ki_modell import ModellFeilet, Modellsvar

NAVN = "OpenAI"
NOEKKEL_VARIABEL = "OSE_KI_OPENAI_NOKKEL"
ADRESSE = "https://api.openai.com/v1/responses"
MODELL = "gpt-6-luna"
LENGSTE_SVAR = 1024
TIDSFRIST = 60

Http = Callable[[str, dict[str, str], dict, float], tuple[int, object]]


def http(url: str, headere: dict[str, str], json: dict, tidsfrist: float) -> tuple[int, object]:
    """Den ene hentefunksjonen mot OpenAI (AD-2). Gir status og JSON-svaret."""
    svar = requests.post(url, headers=headere, json=json, timeout=tidsfrist)
    try:
        innhold = svar.json()
    except ValueError:
        innhold = None
    return svar.status_code, innhold


def _tekst(svar: dict) -> str | None:
    """Teksten i meldingene med output_text, eller None. Et avslag har ingen."""
    utdata = svar.get("output")
    if not isinstance(utdata, list):
        return None
    deler = [
        del_["text"]
        for melding in utdata
        if isinstance(melding, dict) and melding.get("type") == "message" and isinstance(melding.get("content"), list)
        for del_ in melding["content"]
        if isinstance(del_, dict) and del_.get("type") == "output_text" and isinstance(del_.get("text"), str)
    ]
    return "".join(deler) if deler else None


class OpenAIModell:
    """Modell (porten i ki_modell.py) mot OpenAI API, tjenesten «openai»."""

    tjeneste = "openai"

    def __init__(self, noekkel: str | None, modell: str = MODELL, hent: Http = http, tidsfrist: float = TIDSFRIST):
        self._noekkel = (noekkel or "").strip()
        self.modell = modell
        self._hent = hent
        self._tidsfrist = tidsfrist

    def __repr__(self) -> str:
        return f"OpenAIModell(modell={self.modell!r})"

    def lag_tekst(self, prompt: str) -> Modellsvar:
        if not self._noekkel:
            raise ModellFeilet(f"{NOEKKEL_VARIABEL} mangler i .env")
        headere = {"Content-Type": "application/json", "Authorization": f"Bearer {self._noekkel}"}
        kropp = {"model": self.modell, "input": prompt, "store": False, "max_output_tokens": LENGSTE_SVAR}
        try:
            status, svar = self._hent(ADRESSE, headere, kropp, self._tidsfrist)
        # from None: feilen fra requests kan ha adressen og headerne i seg.
        except requests.Timeout:
            raise ModellFeilet(f"tidsavbrudd etter {self._tidsfrist:g} s") from None
        except requests.ConnectionError:
            raise ModellFeilet(f"{NAVN} svarer ikke") from None
        except requests.RequestException as feil:
            raise ModellFeilet(type(feil).__name__) from None
        if status != 200:
            raise ModellFeilet(f"{NAVN} svarte HTTP {status}")
        if not isinstance(svar, dict):
            raise ModellFeilet(f"svaret fra {NAVN} kunne ikke leses")
        if svar.get("status") == "failed":
            raise ModellFeilet(f"{NAVN} ga ingen tekst")
        tekst = _tekst(svar)
        if tekst is None:
            raise ModellFeilet(f"svaret fra {NAVN} hadde ingen tekst")
        svart = svar.get("model")
        return Modellsvar(
            tekst=tekst,
            modell=self.modell,
            modell_id=svart if isinstance(svart, str) and svart.strip() else None,
        )
