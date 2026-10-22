"""Story 10.7: egen noekkel til Gemini, Anthropic og OpenAI - FR-604, FR-605,
FR-608, AD-2, AD-8, AD-12.

Hver tjeneste faar en falsk hentefunksjon (AD-8). Ingen test kaller en ekte
tjeneste, og den siste testen viser at nettsperren i conftest.py stopper
den ekte hentefunksjonen (story 4.0). Noekkelen i testene er oppdiktet.
"""

import sqlite3
from datetime import datetime

import pytest
import requests

import app as app_modul
import ki_anthropic
import ki_gemini
import ki_lokal
import ki_openai
import ki_tekst
from conftest import NettverkISTest
from ki_anthropic import AnthropicModell
from ki_gemini import GeminiModell
from ki_modell import Modell, Modellsvar, lag_ki_rad
from ki_openai import OpenAIModell
from ki_prompt import lag_prompt
from ki_tekst import ki_innstillinger, velg_modell
from kilogg import Emne
from test_app import HENTET, serie, skriv_serie, skriv_vurdering
from test_ki_tekst import TIRSDAG, kjoer, radene
from test_ki_visning import GRUNNLAG, VURDERING, side, skriv_kirad

NOEKKEL = "oppdiktet-noekkel-1234567890abcdef"
TEKST = "Kursen ligger over snittet, men det ble handlet mye på en dag kursen falt."
EMNE = Emne.aksje("EQNR", TIRSDAG)
REGELEN = "Trend +1, bevegelse 0, interesse -1. Styrke 2, retning Blandet."


def gemini_svar(tekst=TEKST, modell="gemini-3.5-flash-lite"):
    return {
        "model": modell,
        "status": "completed",
        "steps": [{"type": "model_output", "content": [{"type": "text", "text": tekst}]}],
    }


def anthropic_svar(tekst=TEKST, modell="claude-haiku-5-5"):
    return {"model": modell, "content": [{"type": "text", "text": tekst}], "stop_reason": "end_turn"}


def openai_svar(tekst=TEKST, modell="gpt-6-luna"):
    return {
        "model": modell,
        "status": "completed",
        "output": [{"type": "message", "content": [{"type": "output_text", "text": tekst}]}],
    }


# Tjenesten, klassen, modulen, svaret dokumentasjonen viser, og headeren med
# noekkelen (spesifikasjonen 10.7, «Kallene, slik dokumentasjonen sier»).
TJENESTENE = {
    "gemini": (GeminiModell, ki_gemini, gemini_svar, ("x-goog-api-key", NOEKKEL)),
    "anthropic": (AnthropicModell, ki_anthropic, anthropic_svar, ("x-api-key", NOEKKEL)),
    "openai": (OpenAIModell, ki_openai, openai_svar, ("Authorization", f"Bearer {NOEKKEL}")),
}


class FalskHent:
    """Svarer som tjenesten, eller reiser feilen, og husker kallene."""

    def __init__(self, svar=None, status=200, feil=None):
        self.svar, self.status, self.feil = svar, status, feil
        self.kall: list[tuple] = []

    def __call__(self, url, headere, json, tidsfrist):
        self.kall.append((url, headere, json, tidsfrist))
        if self.feil is not None:
            raise self.feil
        return self.status, self.svar


def modell_for(tjeneste, hent, noekkel=NOEKKEL):
    klasse = TJENESTENE[tjeneste][0]
    return klasse(noekkel, hent=hent)


def rad_for(modell):
    return lag_ki_rad(EMNE, GRUNNLAG, REGELEN, modell)


@pytest.fixture(params=sorted(TJENESTENE))
def tjeneste(request):
    return request.param


@pytest.fixture
def stier(tmp_path):
    return tmp_path / "raa", tmp_path / "db" / "ose.db"


@pytest.fixture
def klient(monkeypatch):
    """Som i test_ki_visning.py: klokka fast etter siste dag."""
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 12, 31, 12, 0).astimezone())
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


@pytest.fixture
def aksje():
    """EQNR med 61 dager og vurderingen for siste dag, som i test_ki_visning.py."""
    rader = serie([100.0] * 61)
    skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET), vurdert=False)
    skriv_vurdering("EQNR", rader[-1].dato, VURDERING)
    return rader[-1].dato


class TestKallet:
    def test_kallet_slik_dokumentasjonen_sier(self, tjeneste):
        """Adressen, headerne og kroppen er de dokumentasjonen viser, og
        prompten er den samme som for den lokale modellen. Ville feilet hvis
        adressen, headeren med noekkelen, modellen eller prompten var en
        annen, eller hvis store manglet hos Gemini og OpenAI."""
        klasse, modul, svar, (header, verdi) = TJENESTENE[tjeneste]
        hent = FalskHent(svar())
        rad_for(klasse(NOEKKEL, hent=hent))
        assert len(hent.kall) == 1
        url, headere, kropp, _ = hent.kall[0]
        assert url == modul.ADRESSE
        assert url.startswith("https://") and "?" not in url
        assert headere[header] == verdi
        assert kropp["model"] == modul.MODELL
        prompt = lag_prompt(GRUNNLAG)
        if tjeneste == "anthropic":
            assert kropp["messages"] == [{"role": "user", "content": prompt}]
            assert headere["anthropic-version"] == "2023-06-01"
            assert kropp["max_tokens"] == 1024 and "temperature" not in kropp
        else:
            assert kropp["input"] == prompt
            assert kropp["store"] is False

    def test_modellene(self):
        """Gemini 3.5 Flash-Lite fra avgjoerelsen 04.10, og modellene i
        spesifikasjonen for de to andre. Ville feilet hvis en modell ble
        byttet uten at spesifikasjonen og README-en fulgte."""
        assert ki_gemini.MODELL == "gemini-3.5-flash-lite"
        assert ki_anthropic.MODELL == "claude-haiku-5-5"
        assert ki_openai.MODELL == "gpt-6-luna"

    def test_porten(self, tjeneste):
        modell = modell_for(tjeneste, FalskHent())
        assert isinstance(modell, Modell)
        assert modell.tjeneste == tjeneste


class TestSvaret:
    def test_svaret_blir_et_modellsvar_med_tjeneste_og_modell(self, tjeneste):
        """Ville feilet hvis teksten ble lest fra feil sted i svaret, eller
        raden manglet tjenesten eller modellen (FR-605)."""
        _, modul, svar, _ = TJENESTENE[tjeneste]
        modell = modell_for(tjeneste, FalskHent(svar(modell=modul.MODELL + "-001")))
        modellsvar = modell.lag_tekst("p")
        assert modellsvar == Modellsvar(tekst=TEKST, modell=modul.MODELL, modell_id=modul.MODELL + "-001")
        rad = rad_for(modell_for(tjeneste, FalskHent(svar())))
        assert (rad.tekst, rad.besto, rad.grunn) == (TEKST, True, None)
        assert (rad.tjeneste, rad.modell, rad.modell_id) == (tjeneste, modul.MODELL, modul.MODELL)
        assert (rad.seed, rad.temperatur, rad.maskinvare, rad.ollama_versjon) == (None, None, None, None)

    @pytest.mark.parametrize("hva", ["tomt", "ikke_dict", "uten_tekst"])
    def test_svar_uten_tekst(self, tjeneste, hva):
        """Ville feilet hvis et svar uten tekst ga en tekst eller reiste
        noe annet enn ModellFeilet."""
        svar = {"tomt": {}, "ikke_dict": [1], "uten_tekst": TJENESTENE[tjeneste][2]("")}[hva]
        if hva == "uten_tekst":
            svar = {k: v for k, v in svar.items() if k == "model"}
        rad = rad_for(modell_for(tjeneste, FalskHent(svar)))
        assert rad.tekst is None and rad.grunn.startswith("modellen feilet")

    def test_avslag_gir_ingen_tekst(self):
        svar = anthropic_svar() | {"stop_reason": "refusal"}
        rad = rad_for(AnthropicModell(NOEKKEL, hent=FalskHent(svar)))
        assert rad.tekst is None and "avslo" in rad.grunn


class TestFeil:
    @pytest.mark.parametrize("noekkel", [None, "", "   "])
    def test_noekkelen_mangler(self, tjeneste, noekkel):
        """Story 10.7: ingen tekst og en rad med grunnen, og tjenesten
        kalles ikke. Ville feilet hvis tjenesten ble kalt uten noekkel, eller
        raden ikke sa hvilken variabel som mangler."""
        _, modul, _, _ = TJENESTENE[tjeneste]
        hent = FalskHent(TJENESTENE[tjeneste][2]())
        rad = rad_for(modell_for(tjeneste, hent, noekkel))
        assert hent.kall == []
        assert rad.tekst is None and not rad.besto
        assert rad.grunn == f"modellen feilet: {modul.NOEKKEL_VARIABEL} mangler i .env"
        assert (rad.tjeneste, rad.modell) == (tjeneste, modul.MODELL)

    @pytest.mark.parametrize("status", [400, 401, 403, 429, 500, 503])
    def test_tjenesten_svarer_med_feil(self, tjeneste, status):
        """Ville feilet hvis en feil fra tjenesten ga en tekst, eller raden
        ikke sa statusen."""
        _, modul, _, _ = TJENESTENE[tjeneste]
        rad = rad_for(modell_for(tjeneste, FalskHent({"error": {"message": "nei"}}, status=status)))
        assert rad.tekst is None and rad.grunn == f"modellen feilet: {modul.NAVN} svarte HTTP {status}"

    @pytest.mark.parametrize(
        "feil, grunn",
        [
            (requests.Timeout(), "tidsavbrudd etter 60 s"),
            (requests.ConnectionError(), "svarer ikke"),
            (requests.exceptions.InvalidHeader(), "InvalidHeader"),
        ],
    )
    def test_ingen_forbindelse(self, tjeneste, feil, grunn):
        rad = rad_for(modell_for(tjeneste, FalskHent(feil=feil)))
        assert rad.tekst is None and grunn in rad.grunn


class TestNoekkelen:
    """Noekkelen staar aldri i grunnen, loggen, utskriften eller paa en
    side, heller ikke naar feilen fra tjenesten inneholder den (story 10.7,
    AD-12)."""

    FEIL = [
        requests.HTTPError(f"401 Client Error for url ...?key={NOEKKEL}"),
        requests.ConnectionError(f"Max retries exceeded with url: /v1?key={NOEKKEL}"),
        requests.Timeout(f"Read timed out {NOEKKEL}"),
        requests.exceptions.InvalidHeader(f"Invalid leading whitespace in header value {NOEKKEL!r}"),
    ]

    @pytest.mark.parametrize("feil", FEIL, ids=lambda f: type(f).__name__)
    def test_ikke_i_grunnen_naar_feilen_har_den(self, tjeneste, feil):
        """Ville feilet hvis teksten i feilen fra requests kom med i grunnen."""
        rad = rad_for(modell_for(tjeneste, FalskHent(feil=feil)))
        assert rad.tekst is None and NOEKKEL not in rad.grunn

    @pytest.mark.parametrize("status", [200, 401])
    def test_ikke_i_grunnen_naar_svaret_har_den(self, tjeneste, status):
        """Et feilsvar som gjentar noekkelen. Ville feilet hvis kroppen i
        svaret kom med i grunnen."""
        svar = {"error": {"message": f"API key not valid: {NOEKKEL}"}, "status": f"failed {NOEKKEL}"}
        rad = rad_for(modell_for(tjeneste, FalskHent(svar, status=status)))
        assert rad.tekst is None and NOEKKEL not in rad.grunn

    def test_ikke_i_repr(self, tjeneste):
        modell = modell_for(tjeneste, FalskHent())
        assert NOEKKEL not in repr(modell) and NOEKKEL not in str(modell)

    def test_ikke_i_loggen_eller_utskriften(self, tjeneste, stier, capsys):
        """Hele hentingen med en falsk EODHD og en tjeneste som feiler med
        noekkelen i feilen. Ville feilet hvis noekkelen sto i en rad i
        KI-loggen, i utskriften eller paa stderr."""
        raa, base = stier
        modell = modell_for(tjeneste, FalskHent(feil=requests.HTTPError(f"url?key={NOEKKEL}")))
        kode, _, utskrift = kjoer(raa, base, modell)
        assert kode == 0
        rader = [r for r in radene(base).values() if r is not None]
        assert rader and all(r.tekst is None and r.tjeneste == tjeneste for r in rader)
        tilkobling = sqlite3.connect(base)
        try:
            alt = "\n".join(str(r) for r in tilkobling.execute("SELECT * FROM ki_logg"))
        finally:
            tilkobling.close()
        fanget = capsys.readouterr()
        for tekst in (alt, utskrift, fanget.out, fanget.err):
            assert NOEKKEL not in tekst

    def test_ikke_paa_siden(self, tjeneste, klient, aksje):
        """Raden fra en tjeneste som feilet med noekkelen i feilen, paa
        aksjesiden. Ville feilet hvis siden viste grunnen fra raden."""
        rad = lag_ki_rad(
            Emne.aksje("EQNR", aksje),
            GRUNNLAG,
            REGELEN,
            modell_for(tjeneste, FalskHent(feil=requests.HTTPError(f"url?key={NOEKKEL}"))),
        )
        skriv_kirad(rad)
        html = side(klient)
        assert "Ingen KI-tekst for denne dagen" in html
        assert NOEKKEL not in html

    def test_ikke_i_utskriften_naar_den_mangler_eller_finnes(self, tjeneste):
        _, modul, _, _ = TJENESTENE[tjeneste]
        for noekkel in ("", NOEKKEL):
            linjer: list[str] = []
            velg_modell({"OSE_KI_TJENESTE": tjeneste, modul.NOEKKEL_VARIABEL: noekkel}, linjer.append)
            assert NOEKKEL not in "\n".join(linjer)
            assert bool(linjer) == (noekkel == "")


class TestValget:
    def test_tjenesten_og_noekkelen(self, tjeneste):
        """FR-608: OSE_KI_TJENESTE velger, og noekkelen er den ene variabelen
        for tjenesten. Ville feilet hvis en tjeneste fikk en annen sin noekkel."""
        klasse, modul, svar, (header, verdi) = TJENESTENE[tjeneste]
        innstillinger = {"OSE_KI_TJENESTE": f" {tjeneste.upper()} "}
        for andre in TJENESTENE.values():
            innstillinger[andre[1].NOEKKEL_VARIABEL] = "feil-" + andre[1].NOEKKEL_VARIABEL
        innstillinger[modul.NOEKKEL_VARIABEL] = f" {NOEKKEL} "
        modell = velg_modell(innstillinger, lambda _: None)
        assert type(modell) is klasse
        hent = FalskHent(svar())
        modell._hent = hent
        rad_for(modell)
        assert hent.kall[0][1][header] == verdi

    def test_noeklene_fra_miljoeet_og_env(self, tmp_path):
        """Som de to OSE_KI-variablene: miljoeet foerst, saa .env, per noekkel.
        Ville feilet hvis noeklene ikke ble lest fra .env."""
        env = tmp_path / ".env"
        env.write_text(
            "EODHD_API_KEY=hemmelig\nOSE_KI_TJENESTE=gemini\nOSE_KI_GEMINI_NOKKEL=fra-fila\n"
            "OSE_KI_OPENAI_NOKKEL=o\nOSE_KI_ANTHROPIC_NOKKEL=a\n",
            encoding="utf-8",
        )
        assert ki_innstillinger(env, {}) == {
            "OSE_KI_TJENESTE": "gemini",
            "OSE_KI_GEMINI_NOKKEL": "fra-fila",
            "OSE_KI_ANTHROPIC_NOKKEL": "a",
            "OSE_KI_OPENAI_NOKKEL": "o",
        }
        assert ki_innstillinger(env, {"OSE_KI_GEMINI_NOKKEL": "fra-miljoeet"})["OSE_KI_GEMINI_NOKKEL"] == "fra-miljoeet"

    def test_lokal_og_av_som_foer(self):
        """Ville feilet hvis lokal eller av endret seg med noeklene."""
        alle = {m.NOEKKEL_VARIABEL: NOEKKEL for _, m, _, _ in TJENESTENE.values()}
        assert type(velg_modell(alle)) is ki_lokal.OllamaModell
        assert type(velg_modell({"OSE_KI_TJENESTE": "lokal"} | alle)) is ki_lokal.OllamaModell
        assert velg_modell({"OSE_KI_TJENESTE": "av"} | alle) is None


class TestIngenOvergang:
    """Story 10.7, «Ville feilet hvis»: appen gikk over til en annen tjeneste
    da den valgte feilet. Da sendes grunnlaget til en tjeneste brukeren ikke
    har valgt."""

    @pytest.fixture
    def andre_kalt(self, monkeypatch):
        """Hver annen modell og hentefunksjon husker om den ble kalt."""
        kalt: list[str] = []

        def husk(navn):
            def kall(*_a, **_k):
                kalt.append(navn)
                return Modellsvar(tekst=TEKST, modell=navn)

            return kall

        monkeypatch.setattr(ki_lokal.OllamaModell, "lag_tekst", husk("lokal"))
        monkeypatch.setattr(ki_lokal.OllamaModell, "sjekk", lambda self: None)
        monkeypatch.setattr(ki_lokal, "http", husk("lokal-http"))
        for navn, (_, modul, _, _) in TJENESTENE.items():
            monkeypatch.setattr(modul, "http", husk(f"{navn}-http"))
        return kalt

    @pytest.mark.parametrize("feil", ["noekkel", "status", "forbindelse"])
    def test_en_valgt_tjeneste_som_feiler_gir_ingen_tekst_fra_en_annen(self, tjeneste, feil, stier, andre_kalt):
        raa, base = stier
        hent = {
            "noekkel": FalskHent(),
            "status": FalskHent({}, status=500),
            "forbindelse": FalskHent(feil=requests.ConnectionError()),
        }[feil]
        modell = modell_for(tjeneste, hent, "" if feil == "noekkel" else NOEKKEL)
        kode, _, utskrift = kjoer(raa, base, modell)
        assert kode == 0
        rader = [r for r in radene(base).values() if r is not None]
        assert len(rader) == 15
        assert all(r.tekst is None and r.tjeneste == tjeneste for r in rader)
        assert andre_kalt == []
        assert len(hent.kall) == (0 if feil == "noekkel" else 1)
        assert f"({tjeneste}, " in utskrift

    def test_valget_uten_noekkel_gir_den_valgte(self, tjeneste):
        """Ville feilet hvis en noekkel som mangler ga lokal, eller ingen modell."""
        linjer: list[str] = []
        modell = velg_modell({"OSE_KI_TJENESTE": tjeneste}, linjer.append)
        assert type(modell) is TJENESTENE[tjeneste][0]
        assert TJENESTENE[tjeneste][1].NOEKKEL_VARIABEL in linjer[0]

    def test_ingen_reserve_i_valget(self):
        """Valget har én modell per tjeneste og ingen liste over reserver."""
        assert set(ki_tekst.MED_NOEKKEL) == set(TJENESTENE)


def test_nettsperren_stopper_den_ekte_hentefunksjonen(tjeneste):
    """Story 4.0 og AD-8: ingen test kan naa tjenesten. Ville feilet hvis
    den ekte hentefunksjonen kom gjennom nettsperren."""
    with pytest.raises(NettverkISTest):
        TJENESTENE[tjeneste][0](NOEKKEL).lag_tekst("p")
