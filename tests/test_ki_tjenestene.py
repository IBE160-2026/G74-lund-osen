"""Story 10.7: egen noekkel til Gemini, Anthropic og OpenAI - FR-604, FR-605,
FR-608, AD-2, AD-8, AD-12.

Hver tjeneste faar en falsk hentefunksjon (AD-8). Ingen test kaller en ekte
tjeneste, og den siste testen viser at nettsperren i conftest.py stopper
den ekte hentefunksjonen (story 4.0). Noeklene i testene er oppdiktet, i
samme form som ekte noekler (gjennomgangen, BH7).
"""

import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path

import pytest
import requests

import app as app_modul
import ki_anthropic
import ki_gemini
import ki_lokal
import ki_openai
import ki_sky
from conftest import NettverkISTest
from ki_anthropic import AnthropicModell
from ki_gemini import GeminiModell
from ki_modell import Modell, ModellFeilet, Modellsvar, lag_ki_rad
from ki_openai import OpenAIModell
from ki_prompt import lag_prompt
from ki_tekst import ki_innstillinger, velg_modell
from kilogg import Emne
from kursdata import AKSJEUNIVERS
from test_app import HENTET, serie, skriv_serie, skriv_vurdering
from test_ki_tekst import TIRSDAG, kjoer, radene
from test_ki_visning import GRUNNLAG, VURDERING, side, skriv_kirad

ROT = Path(__file__).resolve().parent.parent
TEKST = "Kursen ligger over snittet, men det ble handlet mye på en dag kursen falt."
EMNE = Emne.aksje("EQNR", TIRSDAG)
REGELEN = "Trend +1, bevegelse 0, interesse -1. Styrke 2, retning Blandet."


def gemini_svar(tekst=TEKST, modell="gemini-3.5-flash-lite", status="completed"):
    return {
        "model": modell,
        "status": status,
        "steps": [{"type": "model_output", "content": [{"type": "text", "text": tekst}]}],
    }


def anthropic_svar(tekst=TEKST, modell="claude-haiku-5-5", stopp="end_turn"):
    return {"model": modell, "content": [{"type": "text", "text": tekst}], "stop_reason": stopp}


def openai_svar(tekst=TEKST, modell="gpt-6-luna", status="completed"):
    return {
        "model": modell,
        "status": status,
        "output": [{"type": "message", "content": [{"type": "output_text", "text": tekst}]}],
    }


# Tjenesten: klassen, modulen, svaret dokumentasjonen viser, en oppdiktet
# noekkel i samme form som en ekte, og adressen og headeren med noekkelen
# som i dokumentasjonen (spesifikasjonen 10.7, «Kallene, slik
# dokumentasjonen sier»). Adressene staar her som tekst, ikke som
# konstantene, saa en skrivefeil i en konstant fanges (VG3).
TJENESTENE = {
    "gemini": (
        GeminiModell,
        ki_gemini,
        gemini_svar,
        "AIzaSyOppdiktet0123456789abcdefghijklmn",
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        "x-goog-api-key",
        "",
    ),
    "anthropic": (
        AnthropicModell,
        ki_anthropic,
        anthropic_svar,
        "sk-ant-api03-oppdiktet0123456789abcdefghij",
        "https://api.anthropic.com/v1/messages",
        "x-api-key",
        "",
    ),
    "openai": (
        OpenAIModell,
        ki_openai,
        openai_svar,
        "sk-proj-oppdiktet0123456789abcdefghijklmn",
        "https://api.openai.com/v1/responses",
        "Authorization",
        "Bearer ",
    ),
}


def noekkel_for(tjeneste):
    return TJENESTENE[tjeneste][3]


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


def modell_for(tjeneste, hent, noekkel=None):
    klasse = TJENESTENE[tjeneste][0]
    return klasse(noekkel_for(tjeneste) if noekkel is None else noekkel, hent=hent)


def rad_for(modell):
    return lag_ki_rad(EMNE, GRUNNLAG, REGELEN, modell)


def feilen(modell) -> ModellFeilet:
    """Feilen fra adapteren selv, foer _grunn i ki_modell.py har vasket den (BH7)."""
    with pytest.raises(ModellFeilet) as info:
        modell.lag_tekst("p")
    return info.value


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
        adressen, headeren med noekkelen, modellen, prompten, grensen paa
        1024 tokens eller tidsfristen var en annen, eller hvis store manglet
        hos Gemini og OpenAI (VG2, VG3, ECH8)."""
        klasse, modul, svar, noekkel, adresse, header, foran = TJENESTENE[tjeneste]
        hent = FalskHent(svar())
        rad_for(klasse(noekkel, hent=hent))
        assert len(hent.kall) == 1
        url, headere, kropp, tidsfrist = hent.kall[0]
        assert url == adresse
        assert headere[header] == foran + noekkel
        assert tidsfrist == 60
        assert kropp["model"] == modul.MODELL
        prompt = lag_prompt(GRUNNLAG)
        if tjeneste == "anthropic":
            assert headere == {
                "content-type": "application/json",
                "x-api-key": noekkel,
                "anthropic-version": "2023-06-01",
            }
            assert kropp == {
                "model": modul.MODELL,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            }
        elif tjeneste == "gemini":
            assert headere == {"Content-Type": "application/json", "x-goog-api-key": noekkel}
            assert kropp == {
                "model": modul.MODELL,
                "input": prompt,
                "store": False,
                "generation_config": {"max_output_tokens": 1024},
            }
        else:
            assert headere == {"Content-Type": "application/json", "Authorization": f"Bearer {noekkel}"}
            assert kropp == {"model": modul.MODELL, "input": prompt, "store": False, "max_output_tokens": 1024}

    def test_noekkelen_bare_i_den_ene_headeren(self, tjeneste):
        """Ville feilet hvis noekkelen ogsaa sto i adressen, i kroppen eller
        i en annen header (M2, ECH7)."""
        hent = FalskHent(TJENESTENE[tjeneste][2]())
        noekkel = noekkel_for(tjeneste)
        rad_for(modell_for(tjeneste, hent))
        url, headere, kropp, _ = hent.kall[0]
        assert noekkel not in url
        assert noekkel not in json.dumps(kropp)
        assert [n for n, v in headere.items() if noekkel in v] == [TJENESTENE[tjeneste][5]]

    def test_grunnlaget_er_det_eneste_fra_aksjen(self, tjeneste):
        """Det som sendes, er prompten med grunnlaget, uten symbol eller navn
        paa aksjen. Ville feilet hvis noe om aksjen utover grunnlaget kom med
        i kroppen (BH9)."""
        hent = FalskHent(TJENESTENE[tjeneste][2]())
        rad_for(modell_for(tjeneste, hent))
        sendt = json.dumps(hent.kall[0][2], ensure_ascii=False)
        for aksje in AKSJEUNIVERS:
            assert aksje.symbol not in sendt and aksje.navn not in sendt

    def test_modellene(self):
        """Gemini 3.5 Flash-Lite fra avgjoerelsen 04.10, og modellene i
        spesifikasjonen for de to andre. Ville feilet hvis en modell ble
        byttet uten at README-en fulgte (VG6)."""
        assert ki_gemini.MODELL == "gemini-3.5-flash-lite"
        assert ki_anthropic.MODELL == "claude-haiku-5-5"
        assert ki_openai.MODELL == "gpt-6-luna"
        readme = _readme_avsnittet()
        for modul in (ki_gemini, ki_anthropic, ki_openai):
            assert f"`{modul.MODELL}`" in readme and f"`{modul.NOEKKEL_VARIABEL}`" in readme

    def test_porten(self, tjeneste):
        """Ville feilet hvis en adapter ikke oppfylte porten Modell, eller
        hadde et annet tjenestenavn enn FR-608."""
        modell = modell_for(tjeneste, FalskHent())
        assert isinstance(modell, Modell)
        assert modell.tjeneste == tjeneste

    def test_hentefunksjonen_foelger_ingen_videresending(self, monkeypatch):
        """Ville feilet hvis den ekte hentefunksjonen fulgte en videresending,
        som sender x-api-key og x-goog-api-key videre til en annen vert (BH4)."""
        fanget = {}

        class Svar:
            status_code = 307

            def json(self):
                raise ValueError

        def post(url, **navngitt):
            fanget.update(navngitt, url=url)
            return Svar()

        monkeypatch.setattr(ki_sky.requests, "post", post)
        assert ki_sky.http("https://x", {"a": "b"}, {}, 5) == (307, None)
        assert fanget["allow_redirects"] is False and fanget["timeout"] == 5


class TestSvaret:
    def test_svaret_blir_et_modellsvar_med_tjeneste_og_modell(self, tjeneste):
        """Ville feilet hvis teksten ble lest fra feil sted i svaret, eller
        raden manglet tjenesten eller modellen (FR-605)."""
        _, modul, svar, *_ = TJENESTENE[tjeneste]
        modell = modell_for(tjeneste, FalskHent(svar(modell=modul.MODELL + "-001")))
        assert modell.lag_tekst("p") == Modellsvar(tekst=TEKST, modell=modul.MODELL, modell_id=modul.MODELL + "-001")
        rad = rad_for(modell_for(tjeneste, FalskHent(svar())))
        assert (rad.tekst, rad.besto, rad.grunn) == (TEKST, True, None)
        assert (rad.tjeneste, rad.modell, rad.modell_id) == (tjeneste, modul.MODELL, modul.MODELL)
        assert (rad.seed, rad.temperatur, rad.maskinvare, rad.ollama_versjon) == (None, None, None, None)

    @pytest.mark.parametrize("hva", ["tomt", "ikke_dict", "uten_tekst", "null", "tall", "liste"])
    def test_svar_uten_tekst(self, tjeneste, hva):
        """Ville feilet hvis et svar uten tekst, eller med en tekst som ikke
        er en streng, ga en tekst, eller reiste noe annet enn ModellFeilet,
        som ville stoppet steget uten rader (ECH6)."""
        lag = TJENESTENE[tjeneste][2]
        svar = {
            "tomt": {},
            "ikke_dict": [1],
            "uten_tekst": {k: v for k, v in lag().items() if k in ("model", "status", "stop_reason")},
            "null": lag(tekst=None),
            "tall": lag(tekst=5),
            "liste": lag(tekst=["a"]),
        }[hva]
        rad = rad_for(modell_for(tjeneste, FalskHent(svar)))
        assert rad.tekst is None and rad.grunn.startswith("modellen feilet")

    @pytest.mark.parametrize("tekst", ["", "   "])
    def test_tom_tekst(self, tjeneste, tekst):
        """En tom tekst gir ingen tekst, men grunnen «tom tekst» fra
        lag_ki_rad. Ville feilet hvis den ble lagret som en tekst som besto (BH1)."""
        rad = rad_for(modell_for(tjeneste, FalskHent(TJENESTENE[tjeneste][2](tekst=tekst))))
        assert (rad.tekst, rad.besto, rad.grunn) == (None, False, "modellen feilet: tom tekst")

    def test_tegn_som_ikke_kan_lagres(self, tjeneste):
        """Ville feilet hvis en tekst med et ensomt surrogat gikk til basen og
        stoppet steget (ECH13)."""
        rad = rad_for(modell_for(tjeneste, FalskHent(TJENESTENE[tjeneste][2](tekst="a\ud800b"))))
        assert rad.tekst is None and "ikke kan lagres" in rad.grunn

    @pytest.mark.parametrize("tjeneste_", ["gemini", "openai"])
    def test_kortet_av_hos_gemini_og_openai(self, tjeneste_):
        """Ville feilet hvis en tekst som ble kortet av, ble lagret som hel (ECH4, BH2)."""
        rad = rad_for(modell_for(tjeneste_, FalskHent(TJENESTENE[tjeneste_][2](status="incomplete"))))
        assert rad.tekst is None and "kortet av" in rad.grunn

    def test_kortet_av_hos_anthropic(self):
        """Ville feilet hvis stop_reason max_tokens ga en tekst (ECH4, BH2)."""
        rad = rad_for(modell_for("anthropic", FalskHent(anthropic_svar(stopp="max_tokens"))))
        assert rad.tekst is None and "kortet av" in rad.grunn

    @pytest.mark.parametrize("tjeneste_", ["gemini", "openai"])
    @pytest.mark.parametrize("status", ["failed", "cancelled", "in_progress", "queued", None, 7])
    def test_bare_completed_gir_tekst(self, tjeneste_, status):
        """Svaret har teksten, men statusen er ikke completed. Ville feilet
        hvis statusen ikke ble sjekket (VG1, ECH2, ECH3)."""
        rad = rad_for(modell_for(tjeneste_, FalskHent(TJENESTENE[tjeneste_][2](status=status))))
        assert rad.tekst is None and rad.grunn.startswith("modellen feilet")

    def test_avslag_hos_anthropic(self):
        """Ville feilet hvis et avslag ga en tekst."""
        rad = rad_for(modell_for("anthropic", FalskHent(anthropic_svar(stopp="refusal"))))
        assert rad.tekst is None and "avslo" in rad.grunn

    def test_avslag_hos_openai(self):
        """En del med type refusal. Ville feilet hvis avslaget ga en tekst,
        eller grunnen ikke sa at det var et avslag (BH8, VG11)."""
        svar = openai_svar()
        svar["output"][0]["content"].append({"type": "refusal", "refusal": "nei"})
        rad = rad_for(modell_for("openai", FalskHent(svar)))
        assert rad.tekst is None and "avslo" in rad.grunn

    @pytest.mark.parametrize(
        "svart, forventet",
        [
            (" {m} ", "{m}"),
            ("{m}-2026", "{m}-2026"),
            ("en-annen-modell", None),
            ("{m}" + "x" * 200, None),
            (None, None),
            ("", None),
            (5, None),
        ],
    )
    def test_modell_id_fra_svaret(self, tjeneste, svart, forventet):
        """Bare et navn paa modellen som ble bedt om, og ikke for langt.
        Ville feilet hvis hva som helst fra svaret havnet i modell_id (ECH5)."""
        modul = TJENESTENE[tjeneste][1]
        if isinstance(svart, str):
            svart = svart.format(m=modul.MODELL)
        if forventet is not None:
            forventet = forventet.format(m=modul.MODELL)
        svar = TJENESTENE[tjeneste][2]()
        svar["model"] = svart
        assert modell_for(tjeneste, FalskHent(svar)).lag_tekst("p").modell_id == forventet


class TestFeil:
    @pytest.mark.parametrize("noekkel", ["", "   "])
    def test_noekkelen_mangler(self, tjeneste, noekkel):
        """Adapteren alene, uten sjekken foer foerste kall: ingen tekst og en
        rad med grunnen, og tjenesten kalles ikke. I hentingen stopper sjekken
        steget foer dette, uten rader (10.7b). Ville feilet hvis tjenesten ble
        kalt uten noekkel, eller raden ikke sa hvilken variabel som mangler."""
        modul = TJENESTENE[tjeneste][1]
        hent = FalskHent(TJENESTENE[tjeneste][2]())
        rad = rad_for(modell_for(tjeneste, hent, noekkel))
        assert hent.kall == []
        assert rad.tekst is None and not rad.besto
        assert rad.grunn == f"modellen feilet: {modul.NOEKKEL_VARIABEL} mangler"
        assert (rad.tjeneste, rad.modell) == (tjeneste, modul.MODELL)
        assert str(feilen(TJENESTENE[tjeneste][0](None, hent=hent))) == f"{modul.NOEKKEL_VARIABEL} mangler"

    @pytest.mark.parametrize("tegn", ["​", "…", "æ", "\n", "\t", " "])
    def test_tegn_som_ikke_kan_sendes(self, tjeneste, tegn):
        """En noekkel limt inn med et tegn som ikke kan staa i en header.
        Ville feilet hvis den ga en feil som stoppet steget uten rad, eller
        tjenesten ble kalt (ECH1, BH6, VG4)."""
        hent = FalskHent(TJENESTENE[tjeneste][2]())
        noekkel = noekkel_for(tjeneste)
        rad = rad_for(modell_for(tjeneste, hent, noekkel[:10] + tegn + noekkel[10:]))
        assert hent.kall == []
        assert rad.tekst is None and "har tegn som ikke kan sendes" in rad.grunn
        assert noekkel[:10] not in rad.grunn

    @pytest.mark.parametrize("status", [301, 307, 400, 401, 403, 429, 500, 503])
    def test_tjenesten_svarer_med_feil(self, tjeneste, status):
        """Ville feilet hvis en feil fra tjenesten ga en tekst, eller raden
        ikke sa statusen."""
        modul = TJENESTENE[tjeneste][1]
        rad = rad_for(modell_for(tjeneste, FalskHent({"error": {"message": "nei"}}, status=status)))
        assert rad.tekst is None and rad.grunn == f"modellen feilet: {modul.NAVN} svarte HTTP {status}"

    @pytest.mark.parametrize(
        "feil, grunn",
        [
            (requests.Timeout(), "tidsavbrudd etter 60 s"),
            (requests.ConnectionError(), "svarer ikke"),
            (requests.exceptions.InvalidHeader(), "InvalidHeader"),
            (UnicodeEncodeError("latin-1", "x", 0, 1, "nei"), "UnicodeEncodeError"),
        ],
    )
    def test_ingen_forbindelse(self, tjeneste, feil, grunn):
        """Ville feilet hvis en feil fra requests eller i headeren stoppet
        steget i stedet for aa gi en rad med grunnen (VG4)."""
        rad = rad_for(modell_for(tjeneste, FalskHent(feil=feil)))
        assert rad.tekst is None and grunn in rad.grunn


class TestNoekkelen:
    """Noekkelen staar aldri i grunnen, loggen, utskriften eller paa en
    side, heller ikke naar feilen fra tjenesten inneholder den (story 10.7,
    AD-12)."""

    @staticmethod
    def feilene(noekkel):
        return [
            requests.HTTPError(f"401 Client Error for url https://x/?key={noekkel}"),
            requests.ConnectionError(f"Max retries exceeded with url: /v1/{noekkel}"),
            requests.Timeout(f"Read timed out {noekkel}"),
            requests.exceptions.InvalidHeader(f"Invalid leading whitespace in header value {noekkel!r}"),
            UnicodeEncodeError("latin-1", noekkel, 0, 1, noekkel),
        ]

    @pytest.mark.parametrize("nr", range(5))
    def test_ikke_i_feilen_eller_grunnen_naar_feilen_har_den(self, tjeneste, nr):
        """Feilen fra adapteren, foer _grunn har vasket den, og grunnen i
        raden. Ville feilet hvis teksten i feilen fra requests kom med, eller
        hvis feilen hang ved ModellFeilet som __context__ eller __cause__ (M3,
        BH5, BH7, ECH10)."""
        noekkel = noekkel_for(tjeneste)
        modell = modell_for(tjeneste, FalskHent(feil=self.feilene(noekkel)[nr]))
        modellfeil = feilen(modell)
        assert noekkel not in str(modellfeil)
        assert modellfeil.__context__ is None and modellfeil.__cause__ is None
        rad = rad_for(modell)
        assert rad.tekst is None and noekkel not in rad.grunn

    @pytest.mark.parametrize("status", [200, 401])
    def test_ikke_i_grunnen_naar_svaret_har_den(self, tjeneste, status):
        """Et svar som gjentar noekkelen, ogsaa i modellnavnet. Ville feilet
        hvis noe fra kroppen i svaret kom med i grunnen eller modell_id (ECH5)."""
        noekkel = noekkel_for(tjeneste)
        svar = {"error": {"message": f"API key not valid: {noekkel}"}, "status": f"failed {noekkel}", "model": noekkel}
        assert noekkel not in str(feilen(modell_for(tjeneste, FalskHent(svar, status=status))))
        med_tekst = TJENESTENE[tjeneste][2](modell=noekkel)
        assert modell_for(tjeneste, FalskHent(med_tekst)).lag_tekst("p").modell_id is None

    def test_ikke_i_repr(self, tjeneste):
        """Ville feilet hvis noekkelen sto i repr, som en traceback kan vise."""
        modell = modell_for(tjeneste, FalskHent())
        assert noekkel_for(tjeneste) not in repr(modell) and noekkel_for(tjeneste) not in str(modell)

    def test_ikke_i_loggen_eller_utskriften(self, tjeneste, stier, capsys):
        """Hele hentingen med en falsk EODHD og en tjeneste som feiler med
        noekkelen i feilen. Ville feilet hvis noekkelen sto i en rad i
        KI-loggen, i utskriften eller paa stderr."""
        raa, base = stier
        noekkel = noekkel_for(tjeneste)
        modell = modell_for(tjeneste, FalskHent(feil=requests.HTTPError(f"url?key={noekkel}")))
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
            assert noekkel not in tekst

    def test_ikke_paa_siden(self, tjeneste, klient, aksje):
        """Raden fra en tjeneste som feilet med noekkelen i feilen, paa
        aksjesiden. Ville feilet hvis siden viste grunnen fra raden."""
        noekkel = noekkel_for(tjeneste)
        rad = lag_ki_rad(
            Emne.aksje("EQNR", aksje),
            GRUNNLAG,
            REGELEN,
            modell_for(tjeneste, FalskHent(feil=requests.HTTPError(f"url?key={noekkel}"))),
        )
        skriv_kirad(rad)
        html = side(klient)
        assert "Ingen KI-tekst for denne dagen" in html
        assert noekkel not in html

    def test_utskriften_naar_tjenesten_velges(self, tjeneste):
        """Utskriften sier at grunnlaget sendes til tjenesten, eller at
        noekkelen mangler, og har aldri noekkelen. Ville feilet hvis
        noekkelen ble skrevet ut, eller hentingen ikke sa at noe sendes ut (BH8)."""
        modul = TJENESTENE[tjeneste][1]
        noekkel = noekkel_for(tjeneste)
        for verdi in ("", noekkel):
            linjer: list[str] = []
            velg_modell({"OSE_KI_TJENESTE": tjeneste, modul.NOEKKEL_VARIABEL: verdi}, linjer.append)
            assert len(linjer) == 1 and noekkel not in linjer[0]
            if verdi:
                assert f"KI-teksten lages av {tjeneste} ({modul.MODELL})" in linjer[0] and "sendes dit" in linjer[0]
            else:
                # 10.7b: valget lover ingenting om radene (VG1, BH2, ECH3).
                assert f"{modul.NOEKKEL_VARIABEL} mangler" in linjer[0]
                assert "KI-teksten lages ikke før den er lagt inn." in linjer[0]
                assert "Raden i KI-loggen" not in linjer[0] and "rader" not in linjer[0]


class TestValget:
    def test_tjenesten_og_noekkelen(self, tjeneste):
        """FR-608: OSE_KI_TJENESTE velger, og noekkelen er den ene variabelen
        for tjenesten. Ville feilet hvis en tjeneste fikk en annen sin noekkel,
        eller mellomrom rundt noekkelen ble sendt med (ECH9)."""
        klasse, modul, svar, noekkel, _, header, foran = TJENESTENE[tjeneste]
        innstillinger = {"OSE_KI_TJENESTE": f" {tjeneste.upper()} "}
        for andre in TJENESTENE.values():
            innstillinger[andre[1].NOEKKEL_VARIABEL] = "feil" + andre[1].NOEKKEL_VARIABEL
        innstillinger[modul.NOEKKEL_VARIABEL] = f" {noekkel} "
        modell = velg_modell(innstillinger, lambda _: None)
        assert type(modell) is klasse
        hent = FalskHent(svar())
        modell._hent = hent
        rad_for(modell)
        assert hent.kall[0][1][header] == foran + noekkel

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
        alle = {t[1].NOEKKEL_VARIABEL: t[3] for t in TJENESTENE.values()}
        assert type(velg_modell(alle)) is ki_lokal.OllamaModell
        assert type(velg_modell({"OSE_KI_TJENESTE": "lokal"} | alle)) is ki_lokal.OllamaModell
        assert velg_modell({"OSE_KI_TJENESTE": "av"} | alle) is None


class TestIngenOvergang:
    """Story 10.7, «Ville feilet hvis»: appen gikk over til en annen tjeneste
    da den valgte feilet. Da sendes grunnlaget til en tjeneste brukeren ikke
    har valgt."""

    @pytest.mark.parametrize("feil", ["noekkel", "status", "forbindelse"])
    def test_en_valgt_tjeneste_som_feiler_gir_ingen_tekst_fra_en_annen(self, tjeneste, feil, stier, monkeypatch):
        """Hver annen modell husker om den ble kalt, saa en overgang synes uten
        aa gaa via nettsperren (VG8). Ville feilet hvis en annen tjeneste, den
        lokale eller en av de andre med noekkel, ble kalt eller ga en tekst (M1)."""
        kalt: list[str] = []

        def husk(navn):
            def kall(*_a, **_k):
                kalt.append(navn)
                return Modellsvar(tekst=TEKST, modell=navn)

            return kall

        monkeypatch.setattr(ki_lokal.OllamaModell, "lag_tekst", husk("lokal"))
        monkeypatch.setattr(ki_lokal.OllamaModell, "sjekk", lambda self: None)
        monkeypatch.setattr(ki_sky, "http", husk("http"))
        for navn, (klasse, *_) in TJENESTENE.items():
            if navn != tjeneste:
                monkeypatch.setattr(klasse, "lag_tekst", husk(navn))
        raa, base = stier
        hent = {
            "noekkel": FalskHent(),
            "status": FalskHent({}, status=500),
            "forbindelse": FalskHent(feil=requests.ConnectionError()),
        }[feil]
        modell = modell_for(tjeneste, hent, "" if feil == "noekkel" else None)
        kode, _, utskrift = kjoer(raa, base, modell)
        assert kode == 0
        rader = [r for r in radene(base).values() if r is not None]
        # 10.7b: en noekkel som mangler, gir ingen rader (gruppens svar 22.10 kl. 14:38).
        assert len(rader) == (0 if feil == "noekkel" else 15)
        assert all(r.tekst is None and r.tjeneste == tjeneste for r in rader)
        assert kalt == []
        assert len(hent.kall) == (0 if feil == "noekkel" else 1)
        if feil != "noekkel":
            assert f"({tjeneste}, " in utskrift
        else:
            # Steget stoppet foer foerste kall (BH5), se TestNoekkelenFoerKallet.
            assert "Ingen rader er skrevet i KI-loggen" in utskrift

    def test_valget_uten_noekkel_gir_den_valgte(self, tjeneste):
        """Ville feilet hvis en noekkel som mangler ga lokal, eller ingen modell."""
        linjer: list[str] = []
        modell = velg_modell({"OSE_KI_TJENESTE": tjeneste}, linjer.append)
        assert type(modell) is TJENESTENE[tjeneste][0]
        assert TJENESTENE[tjeneste][1].NOEKKEL_VARIABEL in linjer[0]


def uten_noekkel(tjeneste, hva):
    """En noekkel som mangler, eller som har et usynlig tegn fra kopieringen,
    et mellomrom eller en tabulator inne i seg (BH4)."""
    noekkel = noekkel_for(tjeneste)
    tegn = {"tegn": chr(0x200B), "mellomrom": " ", "tab": "\t"}
    return "" if hva == "mangler" else noekkel[:10] + tegn[hva] + noekkel[10:]


class TestNoekkelenFoerKallet:
    """10.7b, gruppens svar 22.10 kl. 14:38: mangler noekkelen eller har tegn
    som ikke kan sendes, skrives ingen rader, som naar Ollama ikke kjoerer, og
    den kan legges inn og hentingen kjoeres igjen samme kveld. En feil hos
    tjenesten etter kallet gir fortsatt en rad med grunnen."""

    @pytest.mark.parametrize("hva", ["mangler", "tegn", "mellomrom", "tab"])
    def test_sjekk_uten_kall(self, tjeneste, hva):
        """Ville feilet hvis sjekken kalte tjenesten, sa ja til en noekkel som
        ikke kan sendes, eller nei til en som kan."""
        modul = TJENESTENE[tjeneste][1]
        hent = FalskHent(TJENESTENE[tjeneste][2]())
        grunn = modell_for(tjeneste, hent, uten_noekkel(tjeneste, hva)).sjekk()
        forventet = "mangler" if hva == "mangler" else "har tegn som ikke kan sendes, lim den inn på nytt"
        assert grunn == f"{modul.NOEKKEL_VARIABEL} {forventet}"
        assert modell_for(tjeneste, hent).sjekk() is None
        assert hent.kall == []

    @pytest.mark.parametrize("hva", ["mangler", "tegn", "mellomrom", "tab"])
    def test_ingen_rader_og_ingen_kall(self, tjeneste, hva, stier, capsys):
        """Hele hentingen med en falsk EODHD. Ville feilet hvis rader ble
        skrevet naar noekkelen mangler (M1), tjenesten ble kalt uten noekkel
        (M2), utskriften ikke sa variabelen og hva man gjoer, eller noekkelen
        sto i utskriften."""
        modul = TJENESTENE[tjeneste][1]
        raa, base = stier
        hent = FalskHent(TJENESTENE[tjeneste][2]())
        kode, _, utskrift = kjoer(raa, base, modell_for(tjeneste, hent, uten_noekkel(tjeneste, hva)))
        assert kode == 0
        assert hent.kall == []
        assert all(r is None for r in radene(base).values())
        assert f"ennå: {modul.NOEKKEL_VARIABEL} " in utskrift
        assert "Ingen rader er skrevet i KI-loggen, og 15 aksjer venter på teksten." in utskrift
        assert "Legg nøkkelen inn eller rett den i .env, eller i miljøet, som går foran" in utskrift
        assert "kjør samme kommando igjen før midnatt. Det gir 0 kall til EODHD." in utskrift
        fanget = capsys.readouterr()
        noekkel = noekkel_for(tjeneste)
        for tekst in (utskrift, fanget.out, fanget.err):
            assert noekkel[:10] not in tekst and noekkel[10:] not in tekst

    @pytest.mark.parametrize("hva", ["mangler", "tegn", "mellomrom", "tab"])
    def test_samme_kveld_med_noekkelen(self, tjeneste, hva, stier):
        """Foerst uten noekkel, saa med: samme kommando lager tekstene, med 0
        kall til EODHD. Ville feilet hvis den foerste hentingen hadde skrevet
        rader, for da sto de, og ingen aksje fikk tekst den dagen (FR-604)."""
        raa, base = stier
        foerste = FalskHent(TJENESTENE[tjeneste][2]())
        kjoer(raa, base, modell_for(tjeneste, foerste, uten_noekkel(tjeneste, hva)))
        assert foerste.kall == []
        hent = FalskHent(TJENESTENE[tjeneste][2]())
        kode, kall, _ = kjoer(raa, base, modell_for(tjeneste, hent))
        assert (kode, kall, len(hent.kall)) == (0, [], 15)
        rader = list(radene(base).values())
        assert len(rader) == 15
        assert all(r is not None and r.tekst == TEKST and r.tjeneste == tjeneste for r in rader)
        assert not any(r.modellen_feilet for r in rader)

    def test_en_feil_hos_tjenesten_gir_fortsatt_en_rad(self, tjeneste, stier):
        """En noekkel som kan sendes, men som tjenesten avviser. Ville feilet
        hvis sjekken ogsaa stoppet dette uten rader, eller raden ikke sa
        grunnen."""
        modul = TJENESTENE[tjeneste][1]
        raa, base = stier
        hent = FalskHent({}, status=401)
        kode, _, _ = kjoer(raa, base, modell_for(tjeneste, hent))
        assert kode == 0 and len(hent.kall) == 1
        rader = list(radene(base).values())
        assert len(rader) == 15 and all(r is not None and r.tekst is None for r in rader)
        assert sum(r.grunn == f"modellen feilet: {modul.NAVN} svarte HTTP 401" for r in rader) == 1
        assert sum("ikke kalt" in r.grunn for r in rader) == 14

    def test_utskriften_naar_noekkelen_ikke_kan_sendes(self, tjeneste):
        """Ville feilet hvis valget sa at teksten lages med noekkelen, eller
        skrev ut noekkelen."""
        modul = TJENESTENE[tjeneste][1]
        noekkel = noekkel_for(tjeneste)
        linjer: list[str] = []
        velg_modell(
            {"OSE_KI_TJENESTE": tjeneste, modul.NOEKKEL_VARIABEL: uten_noekkel(tjeneste, "tegn")}, linjer.append
        )
        assert len(linjer) == 1
        assert f"{modul.NOEKKEL_VARIABEL} har tegn som ikke kan sendes" in linjer[0]
        assert "KI-teksten lages ikke før den er rettet." in linjer[0] and "lages av" not in linjer[0]
        assert noekkel[:10] not in linjer[0] and noekkel[10:] not in linjer[0]


def _readme_avsnittet() -> str:
    readme = (ROT / "README.md").read_text(encoding="utf-8")
    start = "<summary>Egen nøkkel til Gemini, Anthropic eller OpenAI (valgfri)</summary>"
    return readme.split(start, 1)[1].split("</details>", 1)[0]


def test_readme_sier_det_instruksjonen_krever():
    """Punkt b: grunnlaget sendes til tjenesten man har valgt, det kan koste,
    noekkelen skal aldri deles, og man maa ikke ha sagt ja til trening. Og at
    én feil gir ingen tekst for resten av aksjene den kvelden. Ville feilet
    hvis et av punktene falt ut av README-en (VG6, BH3)."""
    tekst = re.sub(r"\s+", " ", _readme_avsnittet())
    for krav in (
        "Grunnlaget sendes til tjenesten du har valgt.",
        "Det kan koste hos dem.",
        "Nøkkelen skal aldri deles.",
        "Du må ikke ha sagt ja til at tjenesten trener på innholdet.",
        "resten av aksjene den kvelden",
        "skrives ingen rader i KI-loggen",
        "Legg den inn og kjør samme kommando igjen samme kveld, før midnatt",
        "kilder-og-rettigheter.md",
    ):
        assert krav in tekst, krav


def test_hjelpen_sier_at_en_noekkel_som_mangler_ikke_gir_rader():
    """10.7b i docs/hjelp.md. Ville feilet hvis hjelpen gikk tilbake til at
    en noekkel som mangler, gir ingen tekst den dagen (VG2)."""
    hjelp = (ROT / "docs" / "hjelp.md").read_text(encoding="utf-8")
    svar = re.sub(r"\s+", " ", hjelp.split("Kan KI-teksten lages uten grafikkort?", 1)[1].split("###", 1)[0])
    assert "skrives ingen rader" in svar
    assert "legg den inn og hent igjen samme kveld, før midnatt" in svar


def test_nettsperren_stopper_den_ekte_hentefunksjonen(tjeneste):
    """Story 4.0 og AD-8: ingen test kan naa tjenesten. Ville feilet hvis
    den ekte hentefunksjonen kom gjennom nettsperren."""
    with pytest.raises(NettverkISTest):
        TJENESTENE[tjeneste][0](noekkel_for(tjeneste)).lag_tekst("p")
