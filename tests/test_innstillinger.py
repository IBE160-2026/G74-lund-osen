"""Story 8.10: Innstillinger øverst, med «Vis hjelp» - FR-110, AD-3, AD-10, AD-16.

Spesifikasjonen er spec-8-10-innstillinger-oeverst.md. Testbasen ligger i
tmp_path (conftest.py, regel 22), og ingen test gjør nettkall (AD-8).
"""

import sqlite3
from datetime import datetime

import pytest

import app as app_modul
import innstillinger
import lagring_sqlite
from lagring_sqlite import aapne_base
from test_fetch_prices import OEYEBLIKK_22_09, kjoer_23


@pytest.fixture
def klient(tmp_path, monkeypatch):
    raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
    kjoer_23(raa, base, OEYEBLIKK_22_09)
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 23, 12, 0).astimezone())
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


SIDENE = ("/", "/min-liste", "/boersometer", "/aksje/EQNR", "/innstillinger")


class TestTabellen:
    def test_valget_overlever_en_omstart(self, tmp_path):
        """Ville feilet hvis valget ikke sto i basen, eller en ny tilkobling
        (en omstart) ikke så det."""
        base = tmp_path / "ose.db"
        t = aapne_base(base)
        innstillinger.sett(t, innstillinger.VIS_HJELP, False)
        t.close()
        t = aapne_base(base)
        try:
            assert innstillinger.les(t)[innstillinger.VIS_HJELP] is False
        finally:
            t.close()

    @pytest.mark.parametrize(
        "sql", ["INSERT INTO innstilling VALUES ('noe', 1)", "INSERT INTO innstilling VALUES ('vis_hjelp', 2)"]
    )
    def test_tabellen_godtar_bare_valgene(self, tmp_path, sql):
        t = aapne_base(tmp_path / "ose.db")
        try:
            with pytest.raises(sqlite3.IntegrityError):
                t.execute(sql)
        finally:
            t.close()

    def test_uten_tabell_er_alt_paa(self):
        assert innstillinger.les(None) == {"vis_hjelp": True, "vis_ki_tekst": True}


class TestSiden:
    def test_knappen_staar_i_stripa_paa_alle_sidene(self, klient):
        """Utdraget §4: ville feilet hvis en side manglet knappen."""
        for adresse in SIDENE:
            side = klient.get(adresse).data.decode("utf-8")
            assert 'href="/innstillinger"' in side and ">Innstillinger</a>" in side, adresse

    def test_siden_har_teksten_fra_utdraget(self, klient):
        side = klient.get("/innstillinger").data.decode("utf-8")
        assert "Vis hjelp" in side and "Faste forklaringer som vi har skrevet og sjekket" in side
        assert "Valgene gjelder alle sidene og lagres på denne maskinen." in side

    def test_vis_hjelp_av_tar_bort_hjelpen_paa_alle_sidene(self, klient):
        """Ville feilet hvis en side viste «?» med hjelpen av, eller valget
        gjaldt bare én side."""
        for adresse in SIDENE[:4]:
            assert 'class="hjelpeknapp"' in klient.get(adresse).data.decode("utf-8"), adresse
        svar = klient.post("/innstillinger", data={"navn": "vis_hjelp", "til": "av"})
        assert svar.status_code == 303
        for adresse in SIDENE:
            side = klient.get(adresse).data.decode("utf-8")
            assert 'class="hjelpeknapp"' not in side and 'class="hjelpevindu"' not in side, adresse
        assert 'aria-checked="false"' in klient.get("/innstillinger").data.decode("utf-8")
        klient.post("/innstillinger", data={"navn": "vis_hjelp", "til": "paa"})
        assert 'class="hjelpeknapp"' in klient.get("/").data.decode("utf-8")

    @pytest.mark.parametrize("data", [{"navn": "noe", "til": "av"}, {"navn": "vis_hjelp", "til": "kanskje"}])
    def test_ugyldige_valg(self, klient, data):
        assert klient.post("/innstillinger", data=data).status_code == 400

    def test_en_annen_side_kan_ikke_endre(self, klient):
        svar = klient.post(
            "/innstillinger", data={"navn": "vis_hjelp", "til": "av"}, headers={"Origin": "https://annen.no"}
        )
        assert svar.status_code == 403

    def test_ingen_kall(self):
        """AD-10: ville feilet hvis innstillinger.py hentet noe."""
        import inspect

        kilde = inspect.getsource(innstillinger)
        assert "requests" not in kilde and "eodhd" not in kilde.lower() and "fetch_prices" not in kilde
