"""Story 8.10b: «Vis KI-tekst» i Innstillinger - FR-110, FR-601, AD-3, AD-10.

Spesifikasjonen er spec-8-10b-vis-ki-tekst-i-innstillinger.md. Testbasen
ligger i tmp_path (conftest.py, regel 22), og ingen test gjør nettkall (AD-8).
"""

import re
import sqlite3
from datetime import datetime

import pytest

import app as app_modul
import lagring_sqlite
from ki_visning import KAPSEL
from test_fetch_prices import OEYEBLIKK_22_09, kjoer_23


@pytest.fixture
def klient(tmp_path, monkeypatch):
    raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
    kjoer_23(raa, base, OEYEBLIKK_22_09)
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 23, 12, 0).astimezone())
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


def ki_i_innstillinger(klient) -> str:
    side = klient.get("/innstillinger").data.decode("utf-8")
    knapp = re.search(
        r'<input type="hidden" name="navn" value="vis_ki_tekst">.*?aria-checked="(true|false)"', side, re.S
    )
    return knapp.group(1)


def ki_ved_teksten(klient) -> str:
    side = klient.get("/aksje/EQNR").data.decode("utf-8")
    knapp = re.search(r'<form class="ki-bryter".*?aria-checked="(true|false)"', side, re.S)
    return knapp.group(1)


def raden(base):
    t = sqlite3.connect(base)
    try:
        return t.execute("SELECT verdi FROM innstilling WHERE navn = 'vis_ki_tekst'").fetchone()
    finally:
        t.close()


class TestSammeValg:
    def test_teksten_fra_utdraget(self, klient):
        side = klient.get("/innstillinger").data.decode("utf-8")
        assert "<h2>KI-tekst</h2>" in side and "Vis KI-tekst" in side
        assert (
            "Noen setninger om dagen og om hver aksje, skrevet av en språkmodell når kursene hentes. Merket «Laget av "
            "KI». Hver KI-tekst har også sin egen bryter." in side
        )

    def test_innstillinger_slaar_av_bryteren_ved_teksten(self, klient):
        """Ville feilet hvis bryteren ved KI-teksten og Innstillinger kunne vise
        hver sin verdi."""
        assert ki_i_innstillinger(klient) == ki_ved_teksten(klient) == "true"
        svar = klient.post("/innstillinger", data={"navn": "vis_ki_tekst", "til": "av"})
        assert svar.status_code == 303 and raden(lagring_sqlite.BASE_STI) == (0,)
        assert ki_i_innstillinger(klient) == ki_ved_teksten(klient) == "false"

    def test_bryteren_ved_teksten_slaar_av_innstillinger(self, klient):
        """Ville feilet hvis bryteren ved teksten bare satte kapselen, så
        Innstillinger viste noe annet."""
        klient.post("/ki", data={"til": "av", "tilbake": "/aksje/EQNR"})
        assert raden(lagring_sqlite.BASE_STI) == (0,)
        klient.delete_cookie(KAPSEL)
        assert ki_i_innstillinger(klient) == ki_ved_teksten(klient) == "false"
        klient.post("/ki", data={"til": "paa", "tilbake": "/aksje/EQNR"})
        # Gjennomgangen (BH8, VG5): raden også ved «på».
        assert raden(lagring_sqlite.BASE_STI) == (1,)
        klient.delete_cookie(KAPSEL)
        assert ki_i_innstillinger(klient) == ki_ved_teksten(klient) == "true"

    def test_raden_gaar_foran_kapselen(self, klient):
        """Spørsmål 1: ville feilet hvis en gammel kapsel kunne vise noe annet
        enn raden i basen."""
        klient.post("/innstillinger", data={"navn": "vis_ki_tekst", "til": "paa"})
        klient.set_cookie(KAPSEL, "av")
        assert ki_i_innstillinger(klient) == ki_ved_teksten(klient) == "true"

    def test_uten_rad_gjelder_kapselen_som_foer(self, klient):
        """Spørsmål 1: ville feilet hvis et valg fra før 8.10b gikk tapt."""
        klient.set_cookie(KAPSEL, "av")
        assert raden(lagring_sqlite.BASE_STI) is None
        assert ki_i_innstillinger(klient) == ki_ved_teksten(klient) == "false"

    def test_ingen_kall(self):
        """AD-10: ville feilet hvis rutene hentet noe."""
        import inspect

        kilde = inspect.getsource(app_modul.ki_bryter) + inspect.getsource(app_modul._lagre_ki)
        for ord_ in ("requests", "urlopen", "hent_", "fetch_prices", "eodhd"):
            assert ord_ not in kilde, ord_


class TestEtterGjennomgangen:
    def test_innstillinger_setter_kapselen_ogsaa(self, klient):
        """VG2: ville feilet hvis valget fra Innstillinger ikke satte kapselen,
        som gjelder når raden mangler (en ny demobase)."""
        svar = klient.post("/innstillinger", data={"navn": "vis_ki_tekst", "til": "av"})
        assert f"{KAPSEL}=av" in svar.headers["Set-Cookie"]

    def test_uten_tabellen_virker_bryteren_med_kapselen(self, klient, monkeypatch):
        """VG1: ville feilet hvis /ki ga en feil i en base fra før 0011."""
        import innstillinger

        monkeypatch.setattr(innstillinger, "har_tabellen", lambda _t: False)
        svar = klient.post("/ki", data={"til": "av", "tilbake": "/aksje/EQNR"})
        assert svar.status_code == 303 and f"{KAPSEL}=av" in svar.headers["Set-Cookie"]

    def test_kan_valget_ikke_skrives_endres_ingenting(self, klient, monkeypatch):
        """BH1, ECH1, ECH2: ville feilet hvis bryteren satte kapselen når raden
        ikke kunne skrives, så de to viste hver sin verdi."""
        import innstillinger

        klient.post("/ki", data={"til": "av", "tilbake": "/aksje/EQNR"})

        def laast(*_a):
            raise sqlite3.OperationalError("database is locked")

        monkeypatch.setattr(innstillinger, "sett", laast)
        svar = klient.post("/ki", data={"til": "paa", "tilbake": "/aksje/EQNR"})
        assert svar.status_code == 503 and "Set-Cookie" not in svar.headers
        assert raden(lagring_sqlite.BASE_STI) == (0,)
