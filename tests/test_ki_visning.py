"""Story 10.3: KI-teksten i aksjedetaljen - FR-601, FR-602, NFR-04, NFR-06, AD-10.

KI-radene skrives rett i testbasen med SQL, fordi testseriene ikke ligger paa
inneveerende boersdag og KILogg.skriv avviser alle andre dager.
"""

import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

import pytest

import app as app_modul
import lagring_sqlite
from ki_visning import (
    BESTO_IKKE, INGEN_RAD, KAPSEL, MODELLEN_FEILET, STEMMER_IKKE, STOPPET_AV_VAKTEN, VIST,
    bygg_ki_visning, ki_paa,
)
from kilogg import Emne, KIRad
from lagring_sqlite import aapne_base
from test_app import HENTET, serie, skriv_serie, skriv_vurdering
from vurderingsdata import Grunn, Vurdering

VURDERING = Vurdering(
    styrke=2, retning="Blandet", trend=1, bevegelse=0, interesse=-1,
    slutt=100.0, justert_slutt=100.0, trend_avvik=0.031,
    dagens_endring=-0.035, standardavvik=0.011, volumforhold=4.95,
)
GRUNNLAG = {"trend": 1, "bevegelse": 0, "interesse": -1, "styrke": 2, "retning": "Blandet"}
TEKST = "Kursen ligger over snittet, men det ble handlet mye på en dag kursen falt."


def kirad(dato=date(2026, 10, 31), **endret) -> KIRad:
    felt = dict(emne=Emne.aksje("EQNR", dato), grunnlag=GRUNNLAG, regelen="r", tekst=TEKST, besto=True,
                grunn=None, promptversjon="1", tjeneste="lokal", modell="gemma4:e4b")
    felt.update(endret)
    return KIRad(**felt)


def skriv_kirad(rad: KIRad) -> None:
    """Rett i basen, med adapterens egen INSERT, uten datokontrollen."""
    tilkobling = aapne_base(lagring_sqlite.BASE_STI)
    try:
        tilkobling.execute(lagring_sqlite._KI_SKRIV, (
            rad.emne.slag, rad.emne.dato.isoformat(), rad.emne.symbol, rad.emne.melding_id,
            rad.grunnlag_som_json(), rad.regelen, rad.tekst, int(rad.besto), rad.grunn,
            rad.promptversjon, rad.tjeneste, rad.modell, None, None, None, None, None,
        ))
        tilkobling.commit()
    finally:
        tilkobling.close()


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 12, 31, 12, 0).astimezone())


@pytest.fixture
def klient():
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


@pytest.fixture
def aksje():
    """EQNR med 61 dager og vurderingen for siste dag (31.10)."""
    rader = serie([100.0] * 61)
    skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET), vurdert=False)
    skriv_vurdering("EQNR", rader[-1].dato, VURDERING)
    return rader[-1].dato


def side(klient, kapsel=None) -> str:
    if kapsel is not None:
        klient.set_cookie(KAPSEL, kapsel)
    svar = klient.get("/aksje/EQNR")
    assert svar.status_code == 200
    return svar.data.decode("utf-8")


class TestVisningen:
    def test_ingen_rad(self):
        assert bygg_ki_visning(None, VURDERING).tilstand == INGEN_RAD

    def test_vist_med_modellnavnet_og_tjenesten(self):
        """FR-602: «gemma4:e4b, lokal»."""
        ki = bygg_ki_visning(kirad(), VURDERING)
        assert (ki.tilstand, ki.tekst, ki.modell) == (VIST, TEKST, "gemma4:e4b, lokal")

    def test_modellen_feilet(self):
        ki = bygg_ki_visning(kirad(tekst=None, besto=False, grunn="modellen feilet"), VURDERING)
        assert ki.tilstand == MODELLEN_FEILET and ki.grunn

    def test_besto_ikke(self):
        ki = bygg_ki_visning(kirad(besto=False, grunn="3: «kjøp»"), VURDERING)
        assert ki.tilstand == BESTO_IKKE and ki.tekst is None

    @pytest.mark.parametrize("endret", [
        dict(trend=0, bevegelse=0, interesse=-1, styrke=1, retning="Negativ"),
        dict(trend=1, bevegelse=1, interesse=-1, styrke=3, retning="Blandet"),
        dict(trend=1, bevegelse=0, interesse=1, styrke=2, retning="Positiv"),
    ])
    def test_grunnlaget_stemmer_ikke_med_vurderingen(self, endret):
        """FR-602 og svar 3: en vurdering skrevet paa nytt samme dag."""
        annen = Vurdering(**{**VURDERING.__dict__, **endret})
        assert bygg_ki_visning(kirad(), annen).tilstand == STEMMER_IKKE

    def test_en_grunn_i_stedet_for_vurdering(self):
        assert bygg_ki_visning(kirad(), Grunn.KURS_IKKE_FRA_DAGEN).tilstand == STEMMER_IKKE

    @pytest.mark.parametrize("ord_", ["Kjøp", "selger", "anbefales", "KJØPSSIGNAL"])
    def test_vakten_stopper_raad(self, ord_):
        """NFR-06: vakten paa vaar side, ogsaa for en tekst som besto."""
        ki = bygg_ki_visning(kirad(tekst=f"Signalet er et {ord_}."), VURDERING)
        assert ki.tilstand == STOPPET_AV_VAKTEN and ki.tekst is None

    def test_bryteren_er_paa_uten_kapsel(self):
        assert ki_paa(None) and ki_paa("paa") and not ki_paa("av")


class TestSiden:
    def test_ki_teksten_under_regelforklaringen(self, klient, aksje):
        """Ville feilet hvis KI-teksten sto foer regelforklaringen (V1)."""
        skriv_kirad(kirad(aksje))
        html = side(klient)
        assert html.index("Hvorfor signalet ble") < html.index("Med KI-ens ord") < html.index("Kursutvikling")
        assert TEKST in html
        assert "Laget av KI · gemma4:e4b, lokal." in html

    def test_regelforklaringen_staar_alltid(self, klient, aksje):
        skriv_kirad(kirad(aksje))
        for kapsel in (None, "av"):
            assert "Hvorfor signalet ble 2" in side(klient, kapsel)

    def test_vises_ikke_naar_grunnlaget_ikke_stemmer(self, klient, aksje):
        """Ville feilet hvis teksten ble vist mot en annen vurdering (V2)."""
        skriv_kirad(kirad(aksje, grunnlag={**GRUNNLAG, "trend": 0, "styrke": 1}))
        html = side(klient)
        assert TEKST not in html
        assert "vurderingen er skrevet på nytt" in html

    def test_en_dag_uten_rad_sier_det(self, klient, aksje):
        """Ville feilet med et tomt felt (V3)."""
        html = side(klient)
        assert '<p class="uten">Ingen KI-tekst for denne dagen.</p>' in html

    @pytest.mark.parametrize("endret, ord_", [
        (dict(tekst=None, besto=False, grunn="modellen feilet"), "modellen svarte ikke"),
        (dict(besto=False, grunn="1: retningen"), "teksten sa mer enn regelen"),
    ])
    def test_grunnen_naar_teksten_ikke_vises(self, klient, aksje, endret, ord_):
        skriv_kirad(kirad(aksje, **endret))
        html = side(klient)
        assert ord_ in html and TEKST not in html

    def test_vakten_paa_siden(self, klient, aksje):
        """Ville feilet hvis vakten ikke stoppet teksten (V4)."""
        skriv_kirad(kirad(aksje, tekst="Dette er et kjøpssignal."))
        html = side(klient)
        assert "kjøpssignal" not in html and "kunne leses som et råd" in html

    def test_med_ki_av_ingen_ki_tekst_og_bryteren_sier_vis(self, klient, aksje):
        """FR-601: av og paa kan sammenlignes, og bryteren er synlig."""
        skriv_kirad(kirad(aksje))
        av = side(klient, "av")
        assert "Med KI-ens ord" not in av and TEKST not in av
        assert ">Vis KI-teksten</button>" in av
        paa = side(klient, "paa")
        assert ">Skjul KI-teksten</button>" in paa

    def test_med_ki_av_er_siden_lik_med_og_uten_rad(self, klient, aksje):
        """FR-601: med KI av sier siden ingenting om KI-raden. Ville feilet
        hvis noe fra raden slapp gjennom med bryteren av."""
        foer = side(klient, "av")
        skriv_kirad(kirad(aksje))
        assert side(klient, "av") == foer

    def test_ingen_bryter_uten_vurdering(self, klient):
        rader = serie([100.0] * 61)
        skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET), vurdert=False)
        skriv_vurdering("EQNR", rader[-1].dato, Grunn.KURS_IKKE_FRA_DAGEN)
        html = side(klient)
        assert "Med KI-ens ord" not in html and "ki-bryter" not in html.split("</style>", 1)[1]

    def test_en_logg_som_ikke_kan_leses_gir_en_dag_uten_tekst(self, klient, aksje, monkeypatch):
        """NFR-04: for eksempel en base fra foer 0005."""
        def feil(*_a, **_k):
            raise RuntimeError("Basen er ikke migrert til siste versjon")

        monkeypatch.setattr(app_modul, "SqliteKILogg", feil)
        assert '<p class="uten">Ingen KI-tekst for denne dagen.</p>' in side(klient)


class TestBryteren:
    def test_post_setter_kapselen_og_gaar_tilbake(self, klient):
        svar = klient.post("/ki", data={"til": "av", "tilbake": "/aksje/EQNR"})
        assert svar.status_code == 303 and svar.headers["Location"].endswith("/aksje/EQNR")
        kapsel = svar.headers["Set-Cookie"]
        assert kapsel.startswith(f"{KAPSEL}=av") and "HttpOnly" in kapsel and "SameSite=Lax" in kapsel

    @pytest.mark.parametrize("tilbake", ["https://eksempel.no", "//eksempel.no", "/\\\\eksempel.no", "aksje"])
    def test_bare_en_sti_paa_samme_side(self, klient, tilbake):
        svar = klient.post("/ki", data={"til": "paa", "tilbake": tilbake})
        assert svar.headers["Location"] in ("/", "http://localhost/")

    def test_ukjent_verdi_gir_paa(self, klient):
        svar = klient.post("/ki", data={"til": "kanskje", "tilbake": "/"})
        assert svar.headers["Set-Cookie"].startswith(f"{KAPSEL}=paa")


def test_webserveren_importerer_ingen_modell():
    """AD-10: siden kaller aldri en modell, og demoen heller ikke (FR-411)."""
    src = Path(app_modul.__file__).resolve().parent
    kode = ("import sys; sys.path.insert(0, sys.argv[1]); import app; "
            "print(sorted(m for m in ('ki_modell', 'ki_lokal', 'ki_tekst', 'ki_kontroll', 'ki_prompt') "
            "if m in sys.modules))")
    ut = subprocess.run([sys.executable, "-c", kode, str(src)], capture_output=True, text=True, check=True)
    assert ut.stdout.strip() == "[]"
