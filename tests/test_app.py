"""Tester for Flask-ruta. Ingen nettverk, og ingen avhengighet til data/.

data/ er gitignorert, saa den finnes ikke i et ferskt klon. Testene monterer
derfor sin egen kilde i stedet for aa lese fra katalogen.
"""

import pytest

import app as app_modul
from kursdata import MinneKilde


@pytest.fixture
def klient():
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


def serie(kurser, volumer=None):
    volumer = volumer or [1000] * len(kurser)
    return [
        {
            "date": f"2026-09-{1 + i:02d}",
            "close": kurs,
            "adjusted_close": kurs,
            "volume": volum,
        }
        for i, (kurs, volum) in enumerate(zip(kurser, volumer))
    ]


def monter(monkeypatch, kilde):
    monkeypatch.setattr(app_modul, "hent_kilde", lambda: kilde)


def test_uten_kilde_viser_beskjed_i_stedet_for_aa_feile(klient, monkeypatch):
    monter(monkeypatch, None)

    svar = klient.get("/")

    assert svar.status_code == 200
    assert "Ingen kursdata" in svar.data.decode("utf-8")


def test_tom_kilde_gir_ogsaa_beskjed(klient, monkeypatch):
    monter(monkeypatch, MinneKilde({}))

    svar = klient.get("/")

    assert svar.status_code == 200
    assert "Ingen kursdata" in svar.data.decode("utf-8")


def test_viser_selskapsnavn_og_de_fem_kolonnene(klient, monkeypatch):
    lang = serie([100.0] * 60 + [104.0])
    monter(monkeypatch, MinneKilde({"EQNR": lang}, hentet="2026-09-21T15:40:00+00:00"))

    html = klient.get("/").data.decode("utf-8")

    for overskrift in ("Selskap", "Sluttkurs", "Endring", "Signalstyrke", "Retning"):
        assert f"<th>{overskrift}</th>" in html or f">{overskrift}</th>" in html
    assert "Equinor" in html


def test_retningen_vises_med_baade_tekst_og_symbol(klient, monkeypatch):
    """FR-103: symbolet staar ved siden av teksten, ikke i stedet for den."""
    stigende = serie([100.0] * 60 + [110.0])
    monter(monkeypatch, MinneKilde({"EQNR": stigende}))

    html = klient.get("/").data.decode("utf-8")

    assert "Opp" in html
    assert "↑" in html


def test_symbolet_er_skjult_for_skjermlesere(klient, monkeypatch):
    """Teksten er den baerende kanalen. Pilen skal ikke leses opp i tillegg."""
    monter(monkeypatch, MinneKilde({"EQNR": serie([100.0] * 60 + [110.0])}))

    html = klient.get("/").data.decode("utf-8")

    assert 'aria-hidden="true"' in html


def test_aksje_uten_data_navngis_i_fotnoten(klient, monkeypatch):
    """Brukeren skal faa vite at oversikten er ufullstendig, ikke bare se faerre rader."""
    monter(monkeypatch, MinneKilde({"EQNR": serie([100.0] * 60 + [101.0])}))

    html = klient.get("/").data.decode("utf-8")

    assert "Uten data i denne kilden" in html
    assert "DNB Bank" in html


def test_ruta_gjoer_ingen_nettverkskall(klient, monkeypatch):
    """Vakt mot at visningen en dag begynner aa hente selv og spiser kvoten."""
    import requests

    def eksploder(*_args, **_kwargs):
        raise AssertionError("Visningen skal aldri gjoere API-kall")

    monkeypatch.setattr(requests, "get", eksploder)
    monter(monkeypatch, MinneKilde({"EQNR": serie([100.0] * 60 + [101.0])}))

    assert klient.get("/").status_code == 200
