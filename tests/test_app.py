"""Tester for Flask-ruta. Ingen nettverk, og ingen avhengighet til data/.

data/ er gitignorert, saa den finnes ikke i et ferskt klon. Testene monterer
derfor sitt eget oeyeblikksbilde i stedet for aa lese fra katalogen. Det er en
ekte SnapshotKilde med EODHDs feltnavn, saa appen proeves gjennom den samme
oversettelsen til Kursrad (SnapshotLeser) som i drift.
"""

from datetime import date, timedelta

import pytest

import app as app_modul
from kursdata import Kursrad, SnapshotKilde

HENTET = "2026-09-21T15:40:00+00:00"


@pytest.fixture
def klient():
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


def serie(kurser, volumer=None):
    volumer = volumer or [1000] * len(kurser)
    return [
        Kursrad(
            dato=date(2026, 9, 1) + timedelta(days=i),
            slutt=kurs,
            justert_slutt=kurs,
            volum=volum,
        )
        for i, (kurs, volum) in enumerate(zip(kurser, volumer))
    ]


def eodhd(rad: Kursrad) -> dict:
    """Raden slik den staar i oeyeblikksbildet, med EODHDs feltnavn."""
    return {
        "date": rad.dato.isoformat(),
        "close": rad.slutt,
        "adjusted_close": rad.justert_slutt,
        "volume": rad.volum,
    }


def snapshot(serier: dict[str, list], hentet: str | None = HENTET) -> SnapshotKilde:
    """Et oeyeblikksbilde i minnet. Kursrad skrives som EODHD-rader, og en
    rad som allerede er en dict, staar urort - slik kan en test legge inn en
    rad oversettelsen ikke godtar."""
    return SnapshotKilde(
        hentet=hentet,
        serier={
            symbol: [eodhd(r) if isinstance(r, Kursrad) else r for r in rader]
            for symbol, rader in serier.items()
        },
    )


def monter(monkeypatch, kilde):
    monkeypatch.setattr(app_modul, "hent_kilde", lambda: kilde)


def test_uten_kilde_viser_beskjed_i_stedet_for_aa_feile(klient, monkeypatch):
    monter(monkeypatch, None)

    svar = klient.get("/")

    assert svar.status_code == 200
    assert "Ingen kursdata" in svar.data.decode("utf-8")


def test_tom_kilde_gir_ogsaa_beskjed(klient, monkeypatch):
    monter(monkeypatch, snapshot({}))

    svar = klient.get("/")

    assert svar.status_code == 200
    assert "Ingen kursdata" in svar.data.decode("utf-8")


def test_viser_selskapsnavn_og_de_fem_kolonnene(klient, monkeypatch):
    lang = serie([100.0] * 60 + [104.0])
    monter(monkeypatch, snapshot({"EQNR": lang}))

    html = klient.get("/").data.decode("utf-8")

    for overskrift in ("Selskap", "Sluttkurs", "Endring", "Signalstyrke", "Retning"):
        assert f"<th>{overskrift}</th>" in html or f">{overskrift}</th>" in html
    assert "Equinor" in html


def test_retningen_vises_med_baade_tekst_og_symbol(klient, monkeypatch):
    """FR-103: symbolet staar ved siden av teksten, ikke i stedet for den.

    Teksten er FR-704s ord uendret - Positiv, ikke Opp.
    """
    stigende = serie([100.0] * 60 + [110.0])
    monter(monkeypatch, snapshot({"EQNR": stigende}))

    html = klient.get("/").data.decode("utf-8")

    assert "Positiv" in html
    assert "↑" in html
    assert ">Opp<" not in html


def test_symbolet_er_skjult_for_skjermlesere(klient, monkeypatch):
    """Teksten er den baerende kanalen. Pilen skal ikke leses opp i tillegg."""
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [110.0])}))

    html = klient.get("/").data.decode("utf-8")

    assert 'aria-hidden="true"' in html


def test_aksje_uten_data_navngis_i_fotnoten(klient, monkeypatch):
    """Brukeren skal faa vite at oversikten er ufullstendig, ikke bare se faerre rader."""
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [101.0])}))

    html = klient.get("/").data.decode("utf-8")

    assert "Uten data i denne kilden" in html
    assert "DNB Bank" in html


def test_uleselig_symbol_navngis_i_fotnoten(klient, monkeypatch):
    """Et symbol med en rad oversettelsen ikke godtar, er manglende (1.4a).
    De andre vises som vanlig, og det manglende navngis."""
    ugyldig = [eodhd(r) for r in serie([100.0] * 61)]
    del ugyldig[30]["adjusted_close"]
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [101.0]), "DNB": ugyldig}))

    html = klient.get("/").data.decode("utf-8")

    assert "Equinor" in html
    assert "Uten data i denne kilden" in html
    assert "DNB Bank" in html


def test_datoen_skrives_som_aaaa_mm_dd(klient, monkeypatch):
    """Datoen er en date i modellen, og malen skriver den som foer."""
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [101.0])}))

    html = klient.get("/").data.decode("utf-8")

    assert "Oslo Børs · 2026-10-31 ·" in html


def test_data_hentet_leses_fra_oeyeblikksbildet(klient, monkeypatch):
    """Sidens tidsstempel kommer fortsatt fra SnapshotKilde.tidsstempel()."""
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [101.0])}))

    html = klient.get("/").data.decode("utf-8")

    assert "data hentet 2026-09-21" in html


def test_ruta_gjoer_ingen_nettverkskall(klient, monkeypatch):
    """Vakt mot at visningen en dag begynner aa hente selv og spiser kvoten."""
    import requests

    def eksploder(*_args, **_kwargs):
        raise AssertionError("Visningen skal aldri gjoere API-kall")

    monkeypatch.setattr(requests, "get", eksploder)
    monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [101.0])}))

    assert klient.get("/").status_code == 200


class TestAksjedetalj:
    """Ruta /aksje/<symbol>. Egen kilde montert, aldri data/."""

    def test_ukjent_symbol_gir_404(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60)}))
        assert klient.get("/aksje/FINNESIKKE").status_code == 404

    def test_ticker_er_ikke_gyldig_i_ruta(self, klient, monkeypatch):
        """Ruta bruker vaart symbol, ikke EODHDs ticker."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60)}))
        assert klient.get("/aksje/EQNR.OL").status_code == 404

    def test_kjent_symbol_uten_data_gir_404(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({}))
        assert klient.get("/aksje/EQNR").status_code == 404

    def test_uten_kilde_gir_404(self, klient, monkeypatch):
        monter(monkeypatch, None)
        assert klient.get("/aksje/EQNR").status_code == 404

    def test_viser_de_tre_sjekkene_ved_navn(self, klient, monkeypatch):
        """FR-706: alle tre skal staa der, ogsaa de som ga 0."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        for navn in ("Trend", "Bevegelse", "Interesse"):
            assert navn in html

    def test_viser_maalingen_bak_hvert_fortegn(self, klient, monkeypatch):
        """Det som gjoer signalet etterproevbart: ikke bare +1, men mot hva."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "mot MA50" in html
        assert "standardavvik" in html
        assert "median" in html

    def test_tegner_baade_kurs_og_ma50(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0 + i for i in range(80)])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "kurslinje" in html
        assert "ma50linje" in html
        assert "<polyline" in html

    def test_kort_serie_viser_kurs_men_sier_at_signalet_mangler(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0, 101.0, 102.0])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert klient.get("/aksje/EQNR").status_code == 200
        assert "kunne ikke regnes" in html

    def test_sier_hva_som_mangler_i_skjermbildet(self, klient, monkeypatch):
        """Meldinger og KI er ikke med enda. Det skal staa, ikke bare utebli."""
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "Børsmeldinger" in html
        assert "ikke med" in html

    def test_oversikten_lenker_til_detaljen(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))

        html = klient.get("/").data.decode("utf-8")

        assert 'href="/aksje/EQNR"' in html

    def test_detaljen_skriver_datoene_som_aaaa_mm_dd(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0 + i for i in range(80)])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert "2026-11-19" in html
        assert "2026-09-01 til 2026-11-19" in html

    def test_uleselig_symbol_gir_404(self, klient, monkeypatch):
        ugyldig = [eodhd(r) for r in serie([100.0] * 61)]
        ugyldig[10]["date"] = "2026-9-11"
        monter(monkeypatch, snapshot({"EQNR": ugyldig}))

        assert klient.get("/aksje/EQNR").status_code == 404

    def test_detaljen_lenker_tilbake(self, klient, monkeypatch):
        monter(monkeypatch, snapshot({"EQNR": serie([100.0] * 60 + [104.0])}))

        html = klient.get("/aksje/EQNR").data.decode("utf-8")

        assert 'href="/"' in html
