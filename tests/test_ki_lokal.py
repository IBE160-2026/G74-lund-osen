"""Story 10.2, PR F: OllamaModell mot en falsk http (AD-2, AD-8).

Ingen test kaller Ollama. Den siste testen viser at nettsperren stopper den
ekte http-funksjonen mot standardadressen (story 4.0).
"""

import pytest
import requests

import ki_lokal
from conftest import NettverkISTest
from ki_lokal import MODELL, STANDARD_URL, OllamaModell, http
from ki_modell import Modell, ModellFeilet

DIGEST = "dc35e8d9c6061234567890abcdef"


class FalskOllama:
    """Svarer som Ollama, og husker kallene."""

    def __init__(self, tekst="En tekst.", status=200, feil=None, ps="gpu", versjon="0.35.1", tags=True):
        self.tekst, self.status, self.feil = tekst, status, feil
        self.ps, self.versjon, self.tags = ps, versjon, tags
        self.kall: list[tuple] = []

    def __call__(self, metode, url, json, tidsfrist):
        self.kall.append((metode, url, json, tidsfrist))
        if url.endswith("/api/generate"):
            if self.feil is not None:
                raise self.feil
            return self.status, ({"response": self.tekst} if self.tekst is not None else {"done": True})
        if url.endswith("/api/version"):
            return (200, {"version": self.versjon}) if self.versjon else (500, None)
        if url.endswith("/api/tags"):
            return 200, {"models": [{"name": MODELL, "digest": f"sha256:{DIGEST}"}] if self.tags else []}
        if url.endswith("/api/ps"):
            stoerrelse = 9_000_000_000
            vram = {"gpu": stoerrelse, "cpu": 0, "delt": 4_000_000_000}.get(self.ps)
            if vram is None:
                raise requests.ConnectionError("borte")
            return 200, {"models": [{"name": MODELL, "size": stoerrelse, "size_vram": vram}]}
        return 404, None


class TestKallet:
    def test_oppfyller_porten(self):
        assert isinstance(OllamaModell(hent=FalskOllama()), Modell)
        assert OllamaModell(hent=FalskOllama()).tjeneste == "lokal"

    def test_generate_med_think_av_temperatur_0_og_seed(self):
        """Som i malinger.md §19 (FR-605)."""
        falsk = FalskOllama()
        OllamaModell(url="http://ollama:11434/", hent=falsk).lag_tekst("prompten")
        metode, url, kropp, tidsfrist = falsk.kall[0]
        assert (metode, url) == ("POST", "http://ollama:11434/api/generate")
        assert kropp == {"model": "gemma4:e4b", "prompt": "prompten", "stream": False, "think": False,
                         "options": {"temperature": 0.0, "seed": 42}}
        assert tidsfrist == ki_lokal.TIDSFRIST

    def test_standardadressen_er_loopback(self):
        """Svar 8 kl. 15:53."""
        assert STANDARD_URL == "http://127.0.0.1:11434"
        assert OllamaModell().url == STANDARD_URL

    def test_svaret_med_det_raden_trenger(self):
        """FR-604 og FR-605: modell-ID, seed, temperatur, maskinvare og versjon."""
        svar = OllamaModell(hent=FalskOllama()).lag_tekst("p")
        assert (svar.tekst, svar.modell, svar.modell_id, svar.seed, svar.temperatur, svar.maskinvare,
                svar.ollama_versjon) == ("En tekst.", "gemma4:e4b", "dc35e8d9c606", 42, 0.0, "gpu", "0.35.1")

    @pytest.mark.parametrize("ps, maskinvare", [("gpu", "gpu"), ("cpu", "cpu"), ("delt", None), ("borte", None)])
    def test_maskinvaren_fra_api_ps(self, ps, maskinvare):
        assert OllamaModell(hent=FalskOllama(ps=ps)).lag_tekst("p").maskinvare == maskinvare

    def test_felt_som_ikke_kan_leses_blir_none_og_teksten_staar(self):
        svar = OllamaModell(hent=FalskOllama(versjon=None, tags=False, ps="borte")).lag_tekst("p")
        assert svar.tekst == "En tekst."
        assert (svar.modell_id, svar.ollama_versjon, svar.maskinvare) == (None, None, None)


class TestFeil:
    @pytest.mark.parametrize("feil, grunn", [
        (requests.Timeout(), "tidsavbrudd"),
        (requests.ConnectTimeout(), "tidsavbrudd"),
        (requests.ConnectionError("http://127.0.0.1:11434 nede"), "Ollama svarer ikke"),
        (requests.RequestException(), "RequestException"),
    ])
    def test_feil_i_kallet_gir_modellfeilet(self, feil, grunn):
        with pytest.raises(ModellFeilet) as svar:
            OllamaModell(hent=FalskOllama(feil=feil)).lag_tekst("p")
        assert grunn in str(svar.value)
        assert "127.0.0.1" not in str(svar.value)

    def test_status_som_ikke_er_200(self):
        with pytest.raises(ModellFeilet, match="500"):
            OllamaModell(hent=FalskOllama(status=500)).lag_tekst("p")

    def test_404_er_at_modellen_ikke_er_hentet(self):
        """Gjennomgangen (BH8): grunnen sier hva som mangler."""
        with pytest.raises(ModellFeilet, match=r"modellen er ikke hentet \(ollama pull gemma4:e4b\)"):
            OllamaModell(hent=FalskOllama(status=404)).lag_tekst("p")

    @pytest.mark.parametrize("models", [5, "x", {"a": 1}, None])
    def test_models_som_ikke_er_en_liste(self, models):
        """Gjennomgangen (ECH): feltene blir None, og teksten staar."""
        falsk = FalskOllama()

        def hent(metode, url, json, tidsfrist):
            if url.endswith(("/api/tags", "/api/ps")):
                return 200, {"models": models}
            return falsk(metode, url, json, tidsfrist)

        svar = OllamaModell(hent=hent).lag_tekst("p")
        assert svar.tekst == "En tekst." and svar.modell_id is None and svar.maskinvare is None

    @pytest.mark.parametrize("digest", ["sha256:abc", "sha256:", "abcdef"])
    def test_kort_digest_gir_ingen_modell_id(self, digest):
        """Gjennomgangen (BH9, ECH): lengden sjekkes etter «sha256:»."""
        falsk = FalskOllama()

        def hent(metode, url, json, tidsfrist):
            if url.endswith("/api/tags"):
                return 200, {"models": [{"name": MODELL, "digest": digest}]}
            return falsk(metode, url, json, tidsfrist)

        assert OllamaModell(hent=hent).lag_tekst("p").modell_id is None

    def test_svar_uten_tekst(self):
        with pytest.raises(ModellFeilet):
            OllamaModell(hent=FalskOllama(tekst=None)).lag_tekst("p")


class TestHttp:
    def test_gir_status_og_json(self, monkeypatch):
        class Svar:
            status_code = 200

            def json(self):
                return {"response": "x"}

        kall = []
        monkeypatch.setattr(ki_lokal.requests, "request",
                            lambda *a, **k: kall.append((a, k)) or Svar())
        assert http("POST", "http://ollama:11434/api/generate", {"a": 1}, 5) == (200, {"response": "x"})
        assert kall == [(("POST", "http://ollama:11434/api/generate"), {"json": {"a": 1}, "timeout": 5})]

    def test_svar_som_ikke_er_json(self, monkeypatch):
        class Svar:
            status_code = 502

            def json(self):
                raise ValueError("ikke json")

        monkeypatch.setattr(ki_lokal.requests, "request", lambda *a, **k: Svar())
        assert http("GET", "http://x/api/ps", None, 5) == (502, None)

    def test_nettsperren_stopper_den_ekte_mot_ollama(self):
        """Story 4.0: ingen test kan naa en Ollama som kjoerer paa maskinen."""
        with pytest.raises(NettverkISTest):
            OllamaModell().lag_tekst("p")
