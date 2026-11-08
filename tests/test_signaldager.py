"""Story 8.8: Signaldager i kursgrafen - FR-206, FR-408, FR-409, AD-7, NFR-06.

Spesifikasjonen er spec-8-8-signaldager-i-kursgrafen.md. Testbasen ligger i
tmp_path (conftest.py, regel 22), og ingen test gjør nettkall (AD-8).
"""

import re
from datetime import date, datetime

import pytest

import app as app_modul
from graf import bygg_graf
from test_app import HENTET, serie, skriv_serie, skriv_vurdering
from test_ki_visning import VURDERING
from vurderingsdata import Grunn, Vurdering


def vurdering(styrke: int, retning: str) -> Vurdering:
    fortegn = {
        (3, "Positiv"): (1, 1, 1),
        (2, "Blandet"): (1, -1, 0),
        (1, "Positiv"): (1, 0, 0),
        (2, "Negativ"): (-1, -1, 0),
    }[(styrke, retning)]
    trend, bevegelse, interesse = fortegn
    return Vurdering(
        **{
            **VURDERING.__dict__,
            "styrke": styrke,
            "retning": retning,
            "trend": trend,
            "bevegelse": bevegelse,
            "interesse": interesse,
        }
    )


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 12, 31, 12, 0).astimezone())


@pytest.fixture
def klient():
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


@pytest.fixture
def aksjen():
    """EQNR med 61 dager fra 01.09 til 31.10, og fire lagrede dager: 3 av 3,
    2 av 3 blandet, 2 av 3 negativ, 1 av 3, og en grunn. Signalet er lagret fra 20.10."""
    rader = serie([100.0 + i for i in range(61)])
    skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET), vurdert=False)
    skriv_vurdering("EQNR", date(2026, 10, 20), Grunn.SYMBOL_FEILET)
    skriv_vurdering("EQNR", date(2026, 10, 21), vurdering(3, "Positiv"))
    skriv_vurdering("EQNR", date(2026, 10, 22), vurdering(2, "Blandet"))
    skriv_vurdering("EQNR", date(2026, 10, 26), vurdering(1, "Positiv"))
    skriv_vurdering("EQNR", date(2026, 10, 23), vurdering(2, "Negativ"))
    return rader


def _prikker(html: str) -> list[str]:
    graf = html.split('<svg class="graf"', 1)[1].split("</svg>", 1)[0]
    return re.findall(r'<(?:circle|rect|polygon) class="signaldag ([a-z ]+)"', graf)


class TestGrafen:
    def test_bare_dagene_som_skilte_seg_ut(self, klient, aksjen):
        """Ville feilet hvis en dag med grunn, uten rad eller med styrke under
        terskelen ble markert, eller 3 av 3 ikke hadde ringen."""
        side = klient.get("/aksje/EQNR?periode=3-mnd").data.decode("utf-8")
        assert _prikker(side) == ["positiv alle", "blandet", "negativ"]

    def test_retningen_har_en_form(self, klient, aksjen):
        """Gjennomgangen (BH2, ECH7, VG2): ville feilet hvis retningen bare
        ble vist med farge."""
        side = klient.get("/aksje/EQNR?periode=3-mnd").data.decode("utf-8")
        graf = side.split('<svg class="graf"', 1)[1].split("</svg>", 1)[0]
        assert '<circle class="signaldag positiv alle"' in graf
        assert '<polygon class="signaldag blandet"' in graf and '<rect class="signaldag negativ"' in graf
        assert "Rund prikk er positiv, firkant negativ og rute blandet." in side

    def test_prikkene_tegnes_over_siste_punktet(self, klient, aksjen):
        """Gjennomgangen (ECH2, VG3): ville feilet hvis siste-punktet dekket prikken."""
        side = klient.get("/aksje/EQNR?periode=3-mnd").data.decode("utf-8")
        graf = side.split('<svg class="graf"', 1)[1].split("</svg>", 1)[0]
        assert graf.index('class="sistepunkt"') < graf.index('class="signaldag')

    def test_lista_er_skjult_og_antallet_staar(self, klient, aksjen):
        """Gjennomgangen (BH3, ECH1, VG1): ville feilet hvis lista over dagene
        sto synlig under grafen."""
        from pathlib import Path

        css = (Path(app_modul.__file__).parent / "static" / "stil.css").read_text(encoding="utf-8")
        assert re.search(r":where\(\.side-aksje\) figcaption \.skjult \{ position: absolute;", css)
        side = klient.get("/aksje/EQNR?periode=3-mnd").data.decode("utf-8")
        assert '3 dager i grafen<span class="skjult">: 21.10' in side

    def test_datoen_markeringene_starter(self, klient, aksjen):
        """Ville feilet hvis grafen ikke sa datoen, eller hadde markeringer før den."""
        side = klient.get("/aksje/EQNR?periode=3-mnd").data.decode("utf-8")
        assert "viser dagene med signalstyrke 2 eller mer, fra 20.10" in side
        assert "før den dagen er det ikke lagret noe signal" in side
        assert "21.10 (positiv, 3 av 3), 22.10 (blandet, 2 av 3), 23.10 (negativ, 2 av 3)" in side

    def test_uten_setningen_naar_grafen_starter_etter(self, klient, aksjen):
        """VG5: ville feilet hvis «før den dagen» sto når grafen starter etter den."""
        side = klient.get("/aksje/EQNR?periode=1-uke").data.decode("utf-8")
        assert "fra 20.10." in side and "før den dagen" not in side

    def test_velg_dag_foer_signalet(self, klient, aksjen):
        """Gjennomgangen (BH6, ECH4, VG4): ville feilet hvis teksten sa en
        startdato etter grafen som om den var i den."""
        side = klient.get("/aksje/EQNR?periode=velg&dag=2026-10-05").data.decode("utf-8")
        assert "Signalet er lagret fra 20.10, etter den siste dagen i grafen, så grafen har ingen prikker." in side
        assert _prikker(side) == []

    def test_uten_lagret_signal_ingen_prikker(self, klient):
        rader = serie([100.0 + i for i in range(61)])
        skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET), vurdert=False)
        side = klient.get("/aksje/EQNR?periode=3-mnd").data.decode("utf-8")
        assert _prikker(side) == [] and "Prikkene på kurslinja" not in side

    def test_markeringene_leses_og_regnes_aldri(self, aksjen):
        """Ville feilet hvis markeringene ble regnet av kursene: grafen får
        bare det den gis, og en dag uten i signal får ingen prikk."""
        punkter = tuple(type("P", (), {"dato": r.dato, "kurs": r.slutt, "ma50": None})() for r in aksjen)
        graf = bygg_graf(punkter, signal={date(2026, 10, 21): (3, "Positiv")}, alle=3)
        assert [s.dato for s in graf.signaldager] == [date(2026, 10, 21)]
        assert bygg_graf(punkter).signaldager == ()

    def test_den_smale_grafen_har_dem_ogsaa(self, klient, aksjen):
        side = klient.get("/aksje/EQNR?periode=3-mnd").data.decode("utf-8")
        smal = side.split('<svg class="graf smal"', 1)[1].split("</svg>", 1)[0]
        assert len(re.findall(r'<(?:circle|rect|polygon) class="signaldag', smal)) == 3

    def test_en_dag_utenfor_perioden_faar_ingen_prikk(self, klient, aksjen):
        """VG6: og teksten sier at ingen av dagene i grafen hadde det."""
        side = klient.get("/aksje/EQNR?periode=1-uke").data.decode("utf-8")
        assert _prikker(side) == []
        assert "Ingen av dagene i grafen hadde signalstyrke 2 eller mer." in side


def test_hjelpen_sier_det():
    """Regel 19: ville feilet hvis docs/hjelp.md ikke forklarte prikkene."""
    from pathlib import Path

    hjelp = (Path(__file__).resolve().parent.parent / "docs" / "hjelp.md").read_text(encoding="utf-8")
    assert "prikkene på kurslinja" in hjelp.lower()
