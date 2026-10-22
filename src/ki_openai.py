"""OpenAI API med egen noekkel - story 10.7, FR-604, FR-605, FR-608, AD-2,
AD-8, AD-12.

Skall: én hentefunksjon mot OpenAI, injisert (AD-2), som standard http i
ki_sky.py. Testene gir en falsk, og nettsperren i conftest.py stopper en
ekte (story 4.0). Ingen test kaller OpenAI.

Kallet er Responses API, med noekkelen i headeren Authorization: Bearer og
store: false, som dokumentasjonen viser (spesifikasjonen 10.7, «Kallene,
slik dokumentasjonen sier»). Noekkelen staar aldri i adressen.

Bare status completed gir en tekst. incomplete betyr at teksten ble kortet
av, og en del med type refusal er et avslag (gjennomgangen, ECH3, ECH4,
BH8). Alt som gaar galt, gir ModellFeilet med en kort grunn uten noekkelen
(ki_sky.py).
"""

import ki_sky
from ki_modell import ModellFeilet, Modellsvar

NAVN = "OpenAI"
NOEKKEL_VARIABEL = "OSE_KI_OPENAI_NOKKEL"
ADRESSE = "https://api.openai.com/v1/responses"
MODELL = "gpt-6-luna"
LENGSTE_SVAR = 1024
TIDSFRIST = 60


def _innhold(svar: dict) -> list:
    """Delene i meldingene i output."""
    utdata = svar.get("output")
    if not isinstance(utdata, list):
        return []
    return [
        del_
        for melding in utdata
        if isinstance(melding, dict) and melding.get("type") == "message" and isinstance(melding.get("content"), list)
        for del_ in melding["content"]
        if isinstance(del_, dict)
    ]


class OpenAIModell:
    """Modell (porten i ki_modell.py) mot OpenAI API, tjenesten «openai»."""

    tjeneste = "openai"

    def __init__(
        self, noekkel: str | None, modell: str = MODELL, hent: ki_sky.Http | None = None, tidsfrist: float = TIDSFRIST
    ):
        self._noekkel = (noekkel or "").strip()
        self.modell = modell
        # Slaas opp ved kallet naar ingen er gitt, saa en test kan bytte den.
        self._hent = hent
        self._tidsfrist = tidsfrist

    def __repr__(self) -> str:
        return f"OpenAIModell(modell={self.modell!r})"

    def sjekk(self) -> str | None:
        """Grunnen naar noekkelen mangler eller ikke kan sendes, ellers None,
        uten kall. lag_ki_tekster kaller den foer foerste tekst, som for
        Ollama, og sier den nei, skrives ingen rader (spesifikasjonen 10.7b)."""
        return ki_sky.noekkel_feil(self._noekkel, NOEKKEL_VARIABEL)

    def lag_tekst(self, prompt: str) -> Modellsvar:
        ki_sky.sjekk_noekkel(self._noekkel, NOEKKEL_VARIABEL)
        headere = {"Content-Type": "application/json", "Authorization": f"Bearer {self._noekkel}"}
        kropp = {"model": self.modell, "input": prompt, "store": False, "max_output_tokens": LENGSTE_SVAR}
        svar = ki_sky.kall(NAVN, self._hent or ki_sky.http, ADRESSE, headere, kropp, self._tidsfrist)
        status = svar.get("status")
        if status == "incomplete":
            raise ModellFeilet(f"svaret fra {NAVN} ble kortet av")
        if status != "completed":
            raise ModellFeilet(f"{NAVN} ga ingen ferdig tekst")
        innhold = _innhold(svar)
        if any(del_.get("type") == "refusal" for del_ in innhold):
            raise ModellFeilet(f"{NAVN} avslo")
        return Modellsvar(
            tekst=ki_sky.tekst_fra(NAVN, [d.get("text") for d in innhold if d.get("type") == "output_text"]),
            modell=self.modell,
            modell_id=ki_sky.modell_id(svar, self.modell),
        )
