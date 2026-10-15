"""Den lokale modellen: Gemma i Ollama - story 10.2, PR F, FR-604, FR-605,
FR-608, AD-2, AD-8.

Skall: én hentefunksjon mot Ollama, http, og den injiseres (AD-2). Testene gir
en falsk http, og nettsperren i conftest.py stopper en ekte (story 4.0).
Ingen test kaller Ollama.

Kallet er /api/generate med think: false, temperatur 0 og en fast seed, som i
malinger.md §19. Etter teksten leses /api/version (Ollama-versjonen),
/api/tags (modell-ID-en, de 12 foerste tegnene i digest) og /api/ps (om
modellen ligger paa grafikkortet), fordi FR-604 og FR-605 krever dem i
raden. Feiler en av de tre, blir feltet None, og teksten staar.

Alt som gaar galt med selve teksten, gir ModellFeilet (ki_modell.py), med en
kort grunn uten adressen, saa ingenting fra .env havner i loggen.
"""

from collections.abc import Callable

import requests

from ki_modell import ModellFeilet, Modellsvar

STANDARD_URL = "http://127.0.0.1:11434"
MODELL = "gemma4:e4b"
SEED = 42
TEMPERATUR = 0.0
# Den foerste teksten laster modellen og tok 79,9 s med grafikkort i §19.
TIDSFRIST = 180

Http = Callable[[str, str, dict | None, float], tuple[int, object]]


def http(metode: str, url: str, json: dict | None, tidsfrist: float) -> tuple[int, object]:
    """Den ene hentefunksjonen mot Ollama (AD-2). Gir status og JSON-svaret."""
    svar = requests.request(metode, url, json=json, timeout=tidsfrist)
    try:
        innhold = svar.json()
    except ValueError:
        innhold = None
    return svar.status_code, innhold


class OllamaModell:
    """Modell (porten i ki_modell.py) mot Ollama, tjenesten «lokal»."""

    tjeneste = "lokal"

    def __init__(self, url: str = STANDARD_URL, modell: str = MODELL, hent: Http = http,
                 seed: int = SEED, temperatur: float = TEMPERATUR, tidsfrist: float = TIDSFRIST):
        self.url = url.rstrip("/")
        self.modell = modell
        self._hent = hent
        self._seed = seed
        self._temperatur = temperatur
        self._tidsfrist = tidsfrist

    def _kall(self, metode: str, sti: str, json: dict | None = None, tidsfrist: float = 10):
        return self._hent(metode, self.url + sti, json, tidsfrist)

    def lag_tekst(self, prompt: str) -> Modellsvar:
        kropp = {
            "model": self.modell, "prompt": prompt, "stream": False, "think": False,
            "options": {"temperature": self._temperatur, "seed": self._seed},
        }
        try:
            status, svar = self._kall("POST", "/api/generate", kropp, self._tidsfrist)
        except requests.Timeout as feil:
            raise ModellFeilet(f"tidsavbrudd etter {self._tidsfrist:g} s") from feil
        except requests.ConnectionError as feil:
            raise ModellFeilet("Ollama svarer ikke (kjoerer den?)") from feil
        except requests.RequestException as feil:
            raise ModellFeilet(type(feil).__name__) from feil
        if status == 404:
            # Ollama svarer 404 naar modellen ikke er hentet (gjennomgangen, BH8).
            raise ModellFeilet(f"modellen er ikke hentet (ollama pull {self.modell})")
        if status != 200:
            raise ModellFeilet(f"Ollama svarte HTTP {status}")
        if not isinstance(svar, dict) or not isinstance(svar.get("response"), str):
            raise ModellFeilet("svaret fra Ollama hadde ingen tekst")
        return Modellsvar(
            tekst=svar["response"], modell=self.modell, modell_id=self._modell_id(),
            seed=self._seed, temperatur=self._temperatur, maskinvare=self._maskinvare(),
            ollama_versjon=self._versjon(),
        )

    def sjekk(self) -> str | None:
        """Svar c kl. 23:32: svarer Ollama, og har den modellen? Gir grunnen
        naar ikke, uten adressen, ellers None. Kalles foer foerste tekst."""
        try:
            status, svar = self._kall("GET", "/api/tags")
        except requests.RequestException:
            return "Ollama svarer ikke (kjoerer den?)"
        if status != 200 or not isinstance(svar, dict):
            return f"Ollama svarte HTTP {status} paa listen over modeller"
        modeller = svar.get("models")
        navn = {m.get("name") for m in modeller if isinstance(m, dict)} if isinstance(modeller, list) else set()
        if self.modell not in navn:
            return f"modellen {self.modell} er ikke hentet (ollama pull {self.modell})"
        return None

    def _les(self, sti: str):
        try:
            status, svar = self._kall("GET", sti)
        except requests.RequestException:
            return None
        return svar if status == 200 and isinstance(svar, dict) else None

    def _versjon(self) -> str | None:
        svar = self._les("/api/version")
        versjon = svar.get("version") if svar else None
        return versjon if isinstance(versjon, str) and versjon.strip() else None

    def _modeller(self, sti: str) -> list:
        modeller = (self._les(sti) or {}).get("models")
        return modeller if isinstance(modeller, list) else []

    def _modell_id(self) -> str | None:
        for modell in self._modeller("/api/tags"):
            if isinstance(modell, dict) and modell.get("name") == self.modell:
                digest = modell.get("digest")
                kort = digest.split(":")[-1] if isinstance(digest, str) else ""
                if len(kort) >= 12:
                    return kort[:12]
        return None

    def _maskinvare(self) -> str | None:
        """gpu naar hele modellen ligger paa grafikkortet, cpu naar ingenting
        gjoer det, og None naar den er delt eller ikke kan leses."""
        for modell in self._modeller("/api/ps"):
            if isinstance(modell, dict) and modell.get("name") == self.modell:
                stoerrelse, vram = modell.get("size"), modell.get("size_vram")
                if not isinstance(stoerrelse, int) or not isinstance(vram, int) or stoerrelse <= 0:
                    return None
                if vram >= stoerrelse:
                    return "gpu"
                if vram == 0:
                    return "cpu"
                return None
        return None
