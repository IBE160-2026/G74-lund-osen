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


# Gjennomgangen (BH3, VG6): også «Følg en aksje» og «Alle» i Min liste.
SIDENE = ("/", "/min-liste", "/min-liste?vis=alle", "/boersometer", "/aksje/EQNR", "/folg", "/innstillinger")


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
        # Gjennomgangen (VG7): hele teksten, ordrett fra utdraget §4.
        assert "<h2>Hjelp</h2>" in side and "Vis hjelp" in side
        assert (
            "Faste forklaringer som vi har skrevet og sjekket: hva tallene, bokstavene og fargene betyr. "
            "Lik for alle aksjer hver dag, og uten KI." in side
        )
        assert "Valgene gjelder alle sidene og lagres på denne maskinen." in side

    def test_vis_hjelp_av_tar_bort_hjelpen_paa_alle_sidene(self, klient):
        """Ville feilet hvis en side viste «?» med hjelpen av, eller valget
        gjaldt bare én side."""
        for adresse in ("/", "/min-liste", "/boersometer", "/aksje/EQNR"):
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


def _valget(base):
    """Raden i fila, lest med en egen tilkobling, som etter en omstart."""
    t = sqlite3.connect(base)
    try:
        return t.execute("SELECT verdi FROM innstilling WHERE navn = 'vis_hjelp'").fetchone()
    finally:
        t.close()


class TestEtterGjennomgangen:
    """Funnene fra gjennomgangen av 8.10."""

    def test_valget_staar_i_fila_og_ikke_i_okta(self, klient):
        """VG2, VG8: ville feilet hvis valget lå i prosessen eller i en
        informasjonskapsel, ikke i basen."""
        svar = klient.post("/innstillinger", data={"navn": "vis_hjelp", "til": "av"})
        assert "Set-Cookie" not in svar.headers
        assert _valget(lagring_sqlite.BASE_STI) == (0,)
        ny = app_modul.app.test_client()
        assert 'class="hjelpeknapp"' not in ny.get("/").data.decode("utf-8")

    def test_en_post_skriver_bare_innstilling(self, klient):
        """VG3: ville feilet hvis lagringen endret en annen tabell, eller
        GET skrev noe."""

        def tellinger():
            t = sqlite3.connect(lagring_sqlite.BASE_STI)
            try:
                return {
                    tab: t.execute(f"SELECT count(*) FROM {tab}").fetchone()[0]
                    for tab in ("aksje", "kurs", "vurdering", "min_liste", "oenske", "innstilling")
                }
            finally:
                t.close()

        foer = tellinger()
        klient.get("/innstillinger")
        assert tellinger() == foer
        klient.post("/innstillinger", data={"navn": "vis_hjelp", "til": "av"})
        etter = tellinger()
        assert etter["innstilling"] == foer["innstilling"] + 1
        assert {k: v for k, v in etter.items() if k != "innstilling"} == {
            k: v for k, v in foer.items() if k != "innstilling"
        }

    def test_bare_webserveren_skriver_tabellen(self):
        """VG3: ville feilet hvis en annen modul skrev innstilling."""
        import re
        from pathlib import Path

        src = Path(__file__).resolve().parent.parent / "src"
        skrivere = sorted(
            p.name
            for p in src.glob("*.py")
            if re.search(r"(INSERT INTO|UPDATE|DELETE FROM)\s+innstilling\b", p.read_text(encoding="utf-8"))
        )
        assert skrivere == ["innstillinger.py"]

    def test_ruta_henter_aldri(self):
        """VG4: ville feilet hvis ruta som lagrer, hentet noe."""
        import inspect

        kilde = inspect.getsource(app_modul.lagre_innstilling) + inspect.getsource(app_modul.innstillinger_side)
        for ord_ in ("requests", "urlopen", "hent_", "fetch_prices", "eodhd"):
            assert ord_ not in kilde, ord_

    @pytest.mark.parametrize("data", [{"navn": "vis_ki_tekst", "til": "av"}, {"navn": "vis_hjelp", "til": "x"}])
    def test_et_avvist_valg_endrer_ingenting(self, klient, data):
        """BH7, ECH3, BH8: ville feilet hvis 8.10 lagret «Vis KI-tekst», eller
        et avvist valg endret noe."""
        assert klient.post("/innstillinger", data=data).status_code == 400
        assert (
            klient.post(
                "/innstillinger", data={"navn": "vis_hjelp", "til": "av"}, headers={"Origin": "https://annen.no"}
            ).status_code
            == 403
        )
        assert _valget(lagring_sqlite.BASE_STI) is None

    def test_i_demoen(self, tmp_path, monkeypatch):
        """VG5: ville feilet hvis valget ikke kunne lagres i demobasen."""
        import shutil

        import demo
        from lagring_sqlite import demo_sti

        mal = tmp_path / "demo.db"
        demo.lag_demobase(mal, skriv=lambda _: None)
        sti = demo_sti()
        sti.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(mal, sti)
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0).astimezone())
        k = app_modul.app.test_client()
        assert k.post("/innstillinger", data={"navn": "vis_hjelp", "til": "av"}).status_code == 303
        assert 'class="hjelpeknapp"' not in k.get("/aksje/KVST").data.decode("utf-8")
