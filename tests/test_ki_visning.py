"""Story 10.3: KI-teksten i aksjedetaljen - FR-601, FR-602, NFR-04, NFR-06, AD-10.

KI-radene skrives rett i testbasen med SQL, fordi testseriene ikke ligger paa
inneveerende boersdag og KILogg.skriv avviser alle andre dager.
"""

import sqlite3
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

import app as app_modul
import lagring_sqlite
from ki_visning import (
    BESTO_IKKE,
    INGEN_FOR_AKSJEN,
    INGEN_RAD,
    KAPSEL,
    MODELLEN_FEILET,
    STEMMER_IKKE,
    STOPPET_AV_VAKTEN,
    UKJENT,
    VIST,
    bygg_ki_visning,
    ki_paa,
    prikkede_tall,
)
from kilogg import Emne, KIRad, UgyldigKIRad
from lagring_sqlite import aapne_base
from test_app import HENTET, serie, skriv_serie, skriv_vurdering
from vurderingsdata import Grunn, Vurdering

VURDERING = Vurdering(
    styrke=2,
    retning="Blandet",
    trend=1,
    bevegelse=0,
    interesse=-1,
    slutt=100.0,
    justert_slutt=100.0,
    trend_avvik=0.031,
    dagens_endring=-0.035,
    standardavvik=0.011,
    volumforhold=4.95,
)
GRUNNLAG = {"trend": 1, "bevegelse": 0, "interesse": -1, "styrke": 2, "retning": "Blandet"}
TEKST = "Kursen ligger over snittet, men det ble handlet mye på en dag kursen falt."


def kirad(dato=date(2026, 10, 31), **endret) -> KIRad:
    felt = dict(
        emne=Emne.aksje("EQNR", dato),
        grunnlag=GRUNNLAG,
        regelen="r",
        tekst=TEKST,
        besto=True,
        grunn=None,
        promptversjon="1",
        tjeneste="lokal",
        modell="gemma4:e4b",
    )
    felt.update(endret)
    return KIRad(**felt)


def skriv_kirad(rad: KIRad) -> None:
    """Rett i basen, med adapterens egen INSERT, uten datokontrollen."""
    tilkobling = aapne_base(lagring_sqlite.BASE_STI)
    try:
        tilkobling.execute(
            lagring_sqlite._KI_SKRIV,
            (
                rad.emne.slag,
                rad.emne.dato.isoformat(),
                rad.emne.symbol,
                rad.emne.melding_id,
                rad.grunnlag_som_json(),
                rad.regelen,
                rad.tekst,
                int(rad.besto),
                rad.grunn,
                rad.promptversjon,
                rad.tjeneste,
                rad.modell,
                None,
                None,
                None,
                None,
                None,
            ),
        )
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
        assert bygg_ki_visning(None, VURDERING, andre_har_rader=False).tilstand == INGEN_RAD

    def test_vist_med_modellnavnet_og_tjenesten(self):
        """FR-602: «gemma4:e4b, lokal»."""
        ki = bygg_ki_visning(kirad(), VURDERING, andre_har_rader=False)
        assert (ki.tilstand, ki.tekst, ki.modell) == (VIST, TEKST, "gemma4:e4b, lokal")

    def test_modellen_feilet(self):
        ki = bygg_ki_visning(kirad(tekst=None, besto=False, grunn="modellen feilet"), VURDERING, andre_har_rader=False)
        assert ki.tilstand == MODELLEN_FEILET and ki.grunn

    def test_besto_ikke(self):
        ki = bygg_ki_visning(kirad(besto=False, grunn="3: «kjøp»"), VURDERING, andre_har_rader=False)
        assert ki.tilstand == BESTO_IKKE and ki.tekst is None

    @pytest.mark.parametrize(
        "endret",
        [
            dict(trend=0, bevegelse=0, interesse=-1, styrke=1, retning="Negativ"),
            dict(trend=1, bevegelse=1, interesse=-1, styrke=3, retning="Blandet"),
            dict(trend=1, bevegelse=0, interesse=1, styrke=2, retning="Positiv"),
            # Gjennomgangen (VG1): samme styrke og retning, men andre fortegn.
            dict(trend=-1, bevegelse=0, interesse=1, styrke=2, retning="Blandet"),
        ],
    )
    def test_grunnlaget_stemmer_ikke_med_vurderingen(self, endret):
        """FR-602 og svar 3: en vurdering skrevet paa nytt samme dag."""
        annen = Vurdering(**{**VURDERING.__dict__, **endret})
        assert bygg_ki_visning(kirad(), annen, andre_har_rader=False).tilstand == STEMMER_IKKE

    def test_en_grunn_i_stedet_for_vurdering(self):
        """Gjennomgangen (BH5): ingen vurdering aa forklare, ikke «skrevet paa nytt»."""
        assert bygg_ki_visning(kirad(), Grunn.KURS_IKKE_FRA_DAGEN, andre_har_rader=False).tilstand == UKJENT

    @pytest.mark.parametrize(
        "ord_",
        [
            "Kjøp",
            "selger",
            "anbefales",
            "KJØPSSIGNAL",
            "salgssignal",
            "salgsanbefaling",
            "aksjekjøp",
            "kj\u00adøpssignal",
            "solgt",
            "tilrådd",
            "kjop",
        ],
    )
    def test_vakten_stopper_raad(self, ord_):
        """NFR-06: vakten paa vaar side, ogsaa for en tekst som besto."""
        ki = bygg_ki_visning(kirad(tekst=f"Signalet er et {ord_}."), VURDERING, andre_har_rader=False)
        assert ki.tilstand == STOPPET_AV_VAKTEN and ki.tekst is None

    def test_bryteren_er_paa_uten_kapsel(self):
        assert ki_paa(None) and ki_paa("paa") and not ki_paa("av")


class TestSiden:
    def test_ki_teksten_under_regelforklaringen(self, klient, aksje):
        """Ville feilet hvis KI-teksten sto foer regelforklaringen (V1).
        Story 8.2b, c (U66): etter grafen og foer historikken."""
        skriv_kirad(kirad(aksje))
        html = side(klient)
        assert html.index("Hvorfor signalet ble") < html.index("Kursutvikling") < html.index("Signalet forklart")
        assert html.index("Signalet forklart") < html.index("Signalet dag for dag")
        assert TEKST in html
        # Story 8.20a (del D): modellen i en liten linje under teksten.
        assert "Laget av KI." in html and '<p class="modell">Modell: gemma4:e4b, lokal</p>' in html

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
        assert (
            '<p class="uten">Ingen KI-tekst for denne dagen: KI var slått av, eller modellen svarte ikke da hentingen gikk.</p>'
            in html
        )

    @pytest.mark.parametrize(
        "endret, ord_",
        [
            (dict(tekst=None, besto=False, grunn="modellen feilet"), "modellen svarte ikke"),
            (dict(besto=False, grunn="1: retningen"), "teksten sa mer enn regelen"),
        ],
    )
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
        assert "kort fortalt" not in av and TEKST not in av
        # Story 8.2b, c (U33): en bryter med «KI-tekst» og «Av» eller «På».
        assert 'role="switch" aria-checked="false"' in av and '<span class="verdi" aria-hidden="true">Av</span>' in av
        paa = side(klient, "paa")
        assert 'role="switch" aria-checked="true"' in paa and '<span class="verdi" aria-hidden="true">På</span>' in paa

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
        assert "kort fortalt" not in html and "ki-bryter" not in html.split("</head>", 1)[1]

    def test_en_logg_som_ikke_kan_leses_gir_en_dag_uten_tekst(self, klient, aksje, monkeypatch):
        """NFR-04: for eksempel en base fra foer 0005."""

        def feil(*_a, **_k):
            raise RuntimeError("Basen er ikke migrert til siste versjon")

        monkeypatch.setattr(app_modul, "SqliteKILogg", feil)
        html = side(klient)
        assert '<p class="uten">Ingen KI-tekst for denne dagen.</p>' in html and "KI var slått av" not in html


class TestBryteren:
    def test_post_setter_kapselen_og_gaar_tilbake(self, klient):
        svar = klient.post("/ki", data={"til": "av", "tilbake": "/aksje/EQNR"})
        # Story 8.2a, a (U35): tilbake til ankeret ved KI-teksten.
        assert svar.status_code == 303 and svar.headers["Location"].endswith("/aksje/EQNR#ki-teksten")
        kapsel = svar.headers["Set-Cookie"]
        assert kapsel.startswith(f"{KAPSEL}=av") and "HttpOnly" in kapsel and "SameSite=Lax" in kapsel

    @pytest.mark.parametrize(
        "tilbake",
        [
            "https://eksempel.no",
            "//eksempel.no",
            "/\\\\eksempel.no",
            "aksje",
            "/\t/eksempel.no",
            "/\n/eksempel.no",
            "/%2F/eksempel.no",
            "/aksje/EQNR\r\nSet-Cookie: x=1",
            # Story 10.6: «/» går nå til «Børsdagen kort fortalt» på
            # oversikten (test_bryteren_sender_tilbake_til_delen i
            # test_ki_dagen.py). En annen adresse på oversikten avvises.
            "/?periode=1-uke&x=1",
            "/aksje/",
        ],
    )
    def test_bare_en_sti_paa_samme_side(self, klient, tilbake):
        svar = klient.post("/ki", data={"til": "paa", "tilbake": tilbake})
        assert svar.headers["Location"] in ("/", "http://localhost/")

    def test_ukjent_verdi_gir_paa(self, klient):
        svar = klient.post("/ki", data={"til": "kanskje", "tilbake": "/"})
        assert svar.headers["Set-Cookie"].startswith(f"{KAPSEL}=paa")


def test_webserveren_importerer_ingen_modell():
    """AD-10: siden kaller aldri en modell, og demoen heller ikke (FR-411)."""
    src = Path(app_modul.__file__).resolve().parent
    kode = (
        "import sys; sys.path.insert(0, sys.argv[1]); import app; "
        "print(sorted(m for m in ('ki_modell', 'ki_lokal', 'ki_tekst', 'ki_kontroll', 'ki_prompt') "
        "if m in sys.modules))"
    )
    ut = subprocess.run([sys.executable, "-c", kode, str(src)], capture_output=True, text=True, check=True)
    assert ut.stdout.strip() == "[]"


class TestEtterGjennomgangen:
    @pytest.mark.parametrize("tekst", ["Trenden er positiv.", "Selskapet hadde en stor dag.", "Retningen er blandet."])
    def test_vakten_slipper_en_vanlig_forklaring(self, tekst):
        """BH13: vakten stopper ikke alt. «Selskapet» er ikke «selg»."""
        assert bygg_ki_visning(kirad(tekst=tekst), VURDERING, andre_har_rader=False).tilstand == VIST

    def test_skjemaet_paa_siden_snur_bryteren(self, klient, aksje):
        """VG2: verdiene skjemaet sender, ikke bare teksten paa knappen."""
        skriv_kirad(kirad(aksje))
        paa = side(klient, "paa")
        assert 'name="til" value="av"' in paa and 'name="tilbake" value="/aksje/EQNR"' in paa
        # Story 8.2b, c (U33): en bryter, med aria-checked.
        assert 'aria-checked="true"' in paa
        av = side(klient, "av")
        assert 'name="til" value="paa"' in av and 'aria-checked="false"' in av

    def test_en_runde_med_bryteren(self, klient, aksje):
        """VG2: av og paa igjen gjennom skjemaet, slik nettleseren gjoer."""
        skriv_kirad(kirad(aksje))
        assert TEKST in side(klient)
        svar = klient.post("/ki", data={"til": "av", "tilbake": "/aksje/EQNR"})
        assert svar.status_code == 303
        assert TEKST not in klient.get("/aksje/EQNR").data.decode("utf-8")
        klient.post("/ki", data={"til": "paa", "tilbake": "/aksje/EQNR"})
        assert TEKST in klient.get("/aksje/EQNR").data.decode("utf-8")

    def test_en_annen_side_kan_ikke_slaa_bryteren(self, klient):
        """BH2, ECH: Origin fra en annen side gir 403."""
        svar = klient.post("/ki", data={"til": "av", "tilbake": "/"}, headers={"Origin": "https://eksempel.no"})
        assert svar.status_code == 403 and "Set-Cookie" not in svar.headers
        svar = klient.post("/ki", data={"til": "av", "tilbake": "/"}, headers={"Origin": "http://localhost"})
        assert svar.status_code == 303

    def test_siden_varierer_med_kapselen(self, klient, aksje):
        """BH10: en mellomlagring skal ikke gi siden med KI paa til en med KI av."""
        assert "Cookie" in klient.get("/aksje/EQNR").headers.get("Vary", "")

    def test_demoen_viser_ki_teksten(self, klient, tmp_path, monkeypatch):
        """VG3 og svar 7: demoen hadde ingen KI-rader foer 3.4b, og sa det.
        Story 3.4b: demoen viser KI-teksten fra demo_ki_tekster.json. Het
        test_demoen_viser_ingen_ki_tekst til 3.4b."""
        from demo import lag_demobase
        from lagring_sqlite import demo_sti

        lag_demobase(demo_sti(), skriv=lambda *a: None)
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        oversikt = klient.get("/").data.decode("utf-8")
        import re

        assert re.search(r'href="/aksje/([A-Z]+)"', oversikt)
        # Gjennomgangen, ECH2: en aksje med en tekst som besto (FR-604).
        from demo_ki import les_radene

        symbol = next(r.emne.symbol for r in les_radene() if r.besto)
        html = klient.get(f"/aksje/{symbol}").data.decode("utf-8")
        assert "Eksempeltall" in html
        assert "Laget av KI." in html and '<p class="ki-tekst">' in html
        assert "Ingen KI-tekst for denne dagen" not in html


def test_webserveren_importerer_ingen_modell_heller_ikke_under_en_forespoersel(tmp_path):
    """BH14: ogsaa naar en side vises, og uansett hva en ny modellfil heter.
    Underprosessen faar en testbase i tmp_path (regel 22)."""
    src = Path(app_modul.__file__).resolve().parent
    kode = (
        "import sys, pathlib; sys.path.insert(0, sys.argv[1]); import lagring_sqlite; "
        "lagring_sqlite.BASE_STI = pathlib.Path(sys.argv[2]) / 'db' / 'ose.db'; import app; "
        "app.app.config['TESTING'] = True; app.app.test_client().get('/aksje/EQNR'); "
        "print(sorted(m for m in sys.modules if m.startswith('ki_') and m != 'ki_visning'))"
    )
    ut = subprocess.run(
        [sys.executable, "-c", kode, str(src), str(tmp_path)], capture_output=True, text=True, check=True
    )
    assert ut.stdout.strip().splitlines()[-1] == "[]"


DAGEN = "Ingen KI-tekst for denne dagen: KI var slått av, eller modellen svarte ikke da hentingen gikk."
AKSJEN = "Ingen KI-tekst for denne aksjen: teksten ble ikke laget i hentingen."


class TestGrunnenPaaSiden:
    """Svar kl. 23:57 15.10: siden sier hvorfor med det loggen kan vise (FR-601)."""

    def test_uten_rad_og_uten_andre_rader(self):
        ki = bygg_ki_visning(None, VURDERING, andre_har_rader=False)
        assert ki.tilstand == INGEN_RAD and ki.grunn == DAGEN

    def test_uten_rad_men_med_andre_rader(self):
        ki = bygg_ki_visning(None, VURDERING, andre_har_rader=True)
        assert ki.tilstand == INGEN_FOR_AKSJEN and ki.grunn == AKSJEN

    def test_ingen_rader_for_dagen_paa_siden(self, klient, aksje):
        assert f'<p class="uten">{DAGEN}</p>' in side(klient)

    def test_rader_for_andre_aksjer_men_ikke_denne(self, klient, aksje):
        """Ville feilet hvis siden ga grunnen for dagen (B1)."""
        skriv_kirad(kirad(aksje, emne=Emne.aksje("DNB", aksje)))
        html = side(klient)
        assert f'<p class="uten">{AKSJEN}</p>' in html and DAGEN not in html

    def test_en_rad_for_en_annen_dag_teller_ikke(self, klient, aksje):
        """Bare rader for samme dag sier at hentingen laget tekster den dagen."""
        skriv_kirad(kirad(aksje - timedelta(days=1), emne=Emne.aksje("DNB", aksje - timedelta(days=1))))
        assert f'<p class="uten">{DAGEN}</p>' in side(klient)

    def test_dagsteksten_teller_ikke_som_en_aksje(self, klient, aksje):
        """En rad for dagen (10.6) er ikke en tekst for en aksje."""
        skriv_kirad(kirad(aksje, emne=Emne.dagen(aksje)))
        assert f'<p class="uten">{DAGEN}</p>' in side(klient)

    def test_rader_som_foer(self, klient, aksje):
        skriv_kirad(kirad(aksje))
        skriv_kirad(kirad(aksje, emne=Emne.aksje("DNB", aksje)))
        html = side(klient)
        assert TEKST in html and DAGEN not in html and AKSJEN not in html

    def test_bryteren_av_viser_ingen_grunn(self, klient, aksje):
        skriv_kirad(kirad(aksje, emne=Emne.aksje("DNB", aksje)))
        html = side(klient, "av")
        assert DAGEN not in html and AKSJEN not in html and "kort fortalt" not in html

    def test_siden_leser_bare(self, klient, aksje):
        """AD-10: aksjesiden skriver ingenting i KI-loggen."""
        skriv_kirad(kirad(aksje, emne=Emne.aksje("DNB", aksje)))
        tilkobling = aapne_base(lagring_sqlite.BASE_STI)
        try:
            foer = tilkobling.execute("SELECT * FROM ki_logg ORDER BY nr").fetchall()
        finally:
            tilkobling.close()
        side(klient)
        tilkobling = aapne_base(lagring_sqlite.BASE_STI)
        try:
            assert tilkobling.execute("SELECT * FROM ki_logg ORDER BY nr").fetchall() == foer
            assert tilkobling.total_changes == 0
        finally:
            tilkobling.close()

    def test_en_melding_teller_ikke_som_en_aksje(self, klient, aksje):
        """VG1: bare rader for andre aksjer gir grunnen for aksjen."""
        skriv_kirad(kirad(aksje, emne=Emne.melding("x", aksje)))
        assert f'<p class="uten">{DAGEN}</p>' in side(klient)

    def test_en_rad_som_ikke_kan_leses_endrer_ikke_svaret(self, klient, aksje, monkeypatch):
        """BH2, ECH, VG2: radene for andre aksjer og dager tolkes ikke."""
        skriv_kirad(kirad(aksje, emne=Emne.aksje("DNB", aksje)))
        skriv_kirad(kirad(aksje - timedelta(days=1), emne=Emne.aksje("DNB", aksje - timedelta(days=1))))

        def ugyldig(_rad):
            raise UgyldigKIRad("raden kan ikke leses")

        # Ingen rad i loggen kan tolkes. Basen stopper ugyldig JSON (CHECK),
        # saa feilen settes inn der radene tolkes.
        monkeypatch.setattr(lagring_sqlite, "_kirad", ugyldig)
        assert f'<p class="uten">{AKSJEN}</p>' in side(klient)

    def test_sjekken_av_andre_kjoeres_bare_uten_egen_rad(self, klient, aksje, monkeypatch):
        """BH7, BH15, VG2: med en rad for aksjen sjekkes ikke de andre."""
        kall = []
        monkeypatch.setattr(app_modul, "andre_aksjer_har_ki_rad", lambda *a: kall.append(a) or True)
        skriv_kirad(kirad(aksje))
        assert TEKST in side(klient) and kall == []

    def test_en_feil_i_sjekken_av_andre_gir_ingen_grunn(self, klient, aksje, monkeypatch):
        """VG2: en feil i sjekken gir 200 og ingen grunn, ikke 500."""

        def feil(*_a):
            raise sqlite3.OperationalError("no such table: ki_logg")

        monkeypatch.setattr(app_modul, "andre_aksjer_har_ki_rad", feil)
        html = side(klient)
        assert '<p class="uten">Ingen KI-tekst for denne dagen.</p>' in html and DAGEN not in html


class TestStory816bDenValgteDagen:
    """Story 8.16b (gruppens svar 19.10 kl. 00:00): med «Velg dag» er
    KI-teksten raden i KI-loggen for dagen, og bryteren tar deg tilbake til
    dagen. Mutantene står i spesifikasjonen 8.16b."""

    DAGEN_TEKST = "Teksten for torsdag 22.10, ikke for siste dag."

    @pytest.fixture
    def dag(self, aksje):
        """Torsdag 22.10 har samme vurdering som siste dag (31.10), så en
        KI-rad for siste dag ville stemt mot den og blitt vist."""
        dag = aksje - timedelta(days=9)
        skriv_vurdering("EQNR", dag, VURDERING)
        skriv_kirad(kirad(aksje))
        return dag

    def test_ki_teksten_for_den_valgte_dagen(self, klient, dag):
        """Ville feilet hvis KI-teksten ble lest for siste børsdag med en
        valgt dag."""
        skriv_kirad(kirad(dag, tekst=self.DAGEN_TEKST))
        html = klient.get(f"/aksje/EQNR?dag={dag.isoformat()}").data.decode("utf-8")
        # Story 8.2b, c (U67): tallene i teksten har prikket strek.
        assert prikkede_tall(self.DAGEN_TEKST) in html and TEKST not in html
        assert TEKST in side(klient)

    def test_en_dag_uten_ki_rad(self, klient, dag):
        """Ville feilet hvis dagen uten KI-rad viste teksten for siste dag,
        eller ikke teksten appen har for en dag uten KI-tekst."""
        html = klient.get(f"/aksje/EQNR?dag={dag.isoformat()}").data.decode("utf-8")
        assert f'<p class="uten">{DAGEN}</p>' in html
        assert TEKST not in html

    def test_ki_teksten_proeves_mot_vurderingen_for_dagen(self, klient, aksje):
        """Ville feilet hvis KI-raden for dagen ble prøvd mot vurderingen for
        siste dag: grunnlaget stemmer med dagen, ikke med siste dag."""
        dag = aksje - timedelta(days=9)
        from dataclasses import replace

        annen = replace(VURDERING, trend=0, styrke=1, retning="Negativ")
        skriv_vurdering("EQNR", dag, annen)
        grunnlag = {"trend": 0, "bevegelse": 0, "interesse": -1, "styrke": 1, "retning": "Negativ"}
        skriv_kirad(kirad(dag, grunnlag=grunnlag, tekst=self.DAGEN_TEKST))
        html = klient.get(f"/aksje/EQNR?dag={dag.isoformat()}").data.decode("utf-8")
        assert prikkede_tall(self.DAGEN_TEKST) in html

    def test_knappen_beholder_dagen(self, klient, dag):
        """Ville feilet hvis bryteren sendte deg til siste børsdag fra en
        valgt dag."""
        adresse = f"/aksje/EQNR?dag={dag.isoformat()}"
        html = klient.get(adresse).data.decode("utf-8")
        assert f'<input type="hidden" name="tilbake" value="{adresse}">' in html
        svar = klient.post("/ki", data={"til": "av", "tilbake": adresse})
        # Story 8.2a, a (U35): med ankeret ved KI-teksten.
        maal = f"{adresse}#ki-teksten"
        assert svar.status_code == 303 and svar.headers["Location"] in (maal, f"http://localhost{maal}")
        # Uten en valgt dag er adressen den samme som før.
        assert '<input type="hidden" name="tilbake" value="/aksje/EQNR">' in side(klient)

    @pytest.mark.parametrize(
        "tilbake",
        [
            "/aksje/EQNR?dag=2026-10-22&x=1",
            "/aksje/EQNR?periode=1-uke",
            "/aksje/EQNR?dag=//eksempel.no",
            "/aksje/EQNR?dag=2026-10-22\r\nSet-Cookie: x=1",
            "/aksje/EQNR?dag=2026-10-2",
        ],
    )
    def test_bryteren_godtar_bare_dagen_i_adressen(self, klient, tilbake):
        """Ville feilet hvis bryteren godtok noe annet enn ?dag= med en dato
        etter stien, for eksempel en annen side eller et linjeskift."""
        svar = klient.post("/ki", data={"til": "paa", "tilbake": tilbake})
        assert svar.headers["Location"] in ("/", "http://localhost/")


ANNEN = Vurdering(
    styrke=1,
    retning="Positiv",
    trend=1,
    bevegelse=0,
    interesse=0,
    slutt=100.0,
    justert_slutt=100.0,
    trend_avvik=0.031,
    dagens_endring=0.001,
    standardavvik=0.011,
    volumforhold=1.0,
)


class TestSetningenOmDagene:
    """Gruppens svar 25.10 kl. 00:51: appen skriver dagene i en setning rett
    under KI-teksten, ogsaa naar KI er av eller teksten er stoppet, med
    tellingen fra svaret 24.10 kl. 16:15 a) og ordlyden fra svarene kl. 12:12
    og 12:19. Klokka staar paa 31.10, siste dag i serien, saa dagen siden
    viser er i dag."""

    @pytest.fixture(autouse=True)
    def klokka_paa_siste_dag(self, monkeypatch):
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 31, 12, 0).astimezone())

    @pytest.mark.parametrize(
        "dager, minst, annen, setning",
        [
            # I dag (svaret kl. 12:12 a). Story 10.9, del A: med datoen for
            # den foerste dagen i rekka, og med «minst» bare «minst siden»
            # (spoersmaal 2, svaret 07.11 kl. 08:58).
            (1, False, False, "Signalet ble slik i dag."),
            (4, False, False, "Signalet har vært slik i 4 børsdager på rad, siden tirsdag 03.11."),
            (12, True, False, "Signalet har vært slik minst siden tirsdag 03.11."),
            (1, True, False, "Signalet har vært slik minst siden tirsdag 03.11."),
            (1234, False, False, "Signalet har vært slik i 1 234 børsdager på rad, siden tirsdag 03.11."),
            (1234, True, False, "Signalet har vært slik minst siden tirsdag 03.11."),
            # En dag som ikke er i dag (svarene kl. 12:12 a) og c) og 12:19 d).
            (1, False, True, "Signalet ble slik denne dagen."),
            (4, False, True, "Denne dagen hadde signalet vært slik i 4 børsdager på rad, siden tirsdag 03.11."),
            (12, True, True, "Denne dagen hadde signalet vært slik minst siden tirsdag 03.11."),
            (1, True, True, "Denne dagen hadde signalet vært slik minst siden tirsdag 03.11."),
            (1234, False, True, "Denne dagen hadde signalet vært slik i 1 234 børsdager på rad, siden tirsdag 03.11."),
            (1234, True, True, "Denne dagen hadde signalet vært slik minst siden tirsdag 03.11."),
        ],
    )
    def test_setningen(self, dager, minst, annen, setning):
        """Ville feilet hvis setningen ikke fulgte gruppens ordlyd for 1 dag,
        flere dager og minst, ogsaa entall, i dag og en annen dag, eller
        tallet ikke fulgte regel 21. Story 10.9, del A: ville ogsaa feilet
        hvis datoen manglet, eller «minst» sto med et antall eller som
        «siden minst»."""
        from dagene import setning_om_dagene

        assert setning_om_dagene(dager, minst, annen_dag=annen, fra=date(2026, 11, 3), i_aar=2026) == setning

    def test_aaret_staar_naar_datoen_er_fra_et_annet_aar(self):
        """Story 10.9, del A: datoen vises som de andre paa siden
        (tallformat.dato). Ville feilet hvis aaret manglet for en dag i fjor."""
        from dagene import setning_om_dagene

        setning = setning_om_dagene(3, False, fra=date(2025, 12, 30), i_aar=2026)
        assert setning == "Signalet har vært slik i 3 børsdager på rad, siden tirsdag 30.12.2025."

    @pytest.mark.parametrize(
        "dag, dager, fra",
        [
            (date(2026, 11, 5), 1, date(2026, 11, 5)),
            (date(2026, 11, 5), 4, date(2026, 11, 2)),
            # Over helga: fredag 30.10 til torsdag 05.11 er fem boersdager.
            (date(2026, 11, 5), 5, date(2026, 10, 30)),
        ],
    )
    def test_foerste_dag_i_rekka(self, dag, dager, fra):
        """Story 10.9, del A: den foerste boersdagen i rekka, som tell_dagene
        teller. Ville feilet hvis datoen var dagen foer rekka, eller helga
        ble talt med."""
        from dagene import foerste_dag_i_rekka

        assert foerste_dag_i_rekka(dag, dager) == fra

    @pytest.mark.parametrize("annen", [False, True])
    @pytest.mark.parametrize("minst", [False, True])
    @pytest.mark.parametrize("dager", [1, 2, 4, 12, 1234])
    def test_aldri_for_foerste_gang_og_aldri_har_vaert_en_annen_dag(self, dager, minst, annen):
        """Svaret kl. 12:12 a): tellingen gjelder dagene paa rad, saa ingen
        setning sier «for første gang». Svarene kl. 12:12 c) og 12:19 d): en
        dag som ikke er i dag, faar «denne dagen» og aldri «Signalet har
        vært». Ville feilet hvis en av setningene sa noe av det."""
        from dagene import setning_om_dagene

        setning = setning_om_dagene(dager, minst, annen_dag=annen, fra=date(2026, 11, 3), i_aar=2026)
        assert "første gang" not in setning
        if annen:
            assert "Signalet har vært" not in setning and "denne dagen" in setning.lower()
        else:
            assert "denne dagen" not in setning.lower() and "hadde" not in setning

    @pytest.mark.parametrize("dager", [0, True, 2.0])
    def test_ugyldige_dager_avvises(self, dager):
        """Ville feilet hvis 0, en bool eller et flyttall ga en setning
        (gjennomgangen, VG13)."""
        from dagene import setning_om_dagene

        with pytest.raises(ValueError):
            setning_om_dagene(dager, False, fra=date(2026, 11, 3), i_aar=2026)

    def test_flere_dager_paa_siden_foerst_i_rammen(self, klient, aksje):
        """Fire boersdager med samme retning og styrke, og en annen foer.
        Ville feilet hvis setningen manglet, eller tellingen ikke leste
        basen. Story 10.9, del C: ville ogsaa feilet hvis KI-teksten sto foer
        appens setninger i rammen «Signalet forklart»."""
        for dato in (date(2026, 10, 28), date(2026, 10, 29), date(2026, 10, 30)):
            skriv_vurdering("EQNR", dato, VURDERING)
        skriv_vurdering("EQNR", date(2026, 10, 27), ANNEN)
        skriv_kirad(kirad(aksje))
        html = side(klient)
        setning = '<p class="dagene">Signalet har vært slik i 4 børsdager på rad, siden onsdag 28.10.</p>'
        assert setning in html
        # Story 8.2b, c (U46): bryteren står øverst i rammen. Story 10.9:
        # appens setninger før KI-teksten.
        assert html.index("Signalet forklart") < html.index("ki-bryter") < html.index(setning) < html.index(TEKST)

    def test_en_dag_paa_siden(self, klient, aksje):
        """Ville feilet hvis en annen vurdering dagen foer ikke ga «Signalet
        ble slik i dag.» (svaret kl. 12:12 a)."""
        skriv_vurdering("EQNR", date(2026, 10, 30), ANNEN)
        assert '<p class="dagene">Signalet ble slik i dag.</p>' in side(klient)

    def test_minst_paa_siden(self, klient, aksje):
        """Uten rad for boersdagen foer er antallet det minste det kan vaere.
        Ville feilet hvis siden sa et eksakt antall."""
        assert '<p class="dagene">Signalet har vært slik minst siden lørdag 31.10.</p>' in side(klient)

    @pytest.mark.parametrize(
        "kapsel, endret",
        [
            ("av", {}),
            (None, dict(besto=False, grunn="1: dagene «i dag for første gang», modellen nevner ikke dagene")),
            (None, dict(tekst=None, besto=False, grunn="modellen feilet")),
            (None, None),
        ],
    )
    def test_ogsaa_uten_ki_tekst(self, klient, aksje, kapsel, endret):
        """KI av, teksten stoppet, modellen feilet, og ingen rad. Ville feilet
        hvis setningen bare sto naar KI-teksten ble vist."""
        skriv_vurdering("EQNR", date(2026, 10, 30), ANNEN)
        if endret is not None:
            skriv_kirad(kirad(aksje, **endret))
        html = side(klient, kapsel)
        assert TEKST not in html
        assert '<p class="dagene">Signalet ble slik i dag.</p>' in html

    def test_ingen_setning_uten_vurdering(self, klient):
        """En dag med en grunn har ikke noe signal. Ville feilet hvis siden
        likevel skrev dagene."""
        rader = serie([100.0] * 61)
        skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET), vurdert=False)
        skriv_vurdering("EQNR", rader[-1].dato, Grunn.KURS_IKKE_FRA_DAGEN)
        assert 'class="dagene"' not in side(klient)

    def test_en_valgt_dag(self, klient, aksje):
        """«Velg dag» 30.10, med en annen vurdering 29.10. Ville feilet hvis
        siden sa «i dag» om en tidligere dag."""
        skriv_vurdering("EQNR", date(2026, 10, 30), VURDERING)
        skriv_vurdering("EQNR", date(2026, 10, 29), ANNEN)
        html = klient.get("/aksje/EQNR?dag=2026-10-30").get_data(as_text=True)
        assert '<p class="dagene">Signalet ble slik denne dagen.</p>' in html

    def test_en_valgt_dag_med_flere_dager(self, klient, aksje):
        """Svaret kl. 12:19 d): «Velg dag» 30.10 med tre dager paa rad. Ville
        feilet hvis siden sa «Signalet har vært» om en tidligere dag."""
        for dato in (date(2026, 10, 28), date(2026, 10, 29), date(2026, 10, 30)):
            skriv_vurdering("EQNR", dato, VURDERING)
        skriv_vurdering("EQNR", date(2026, 10, 27), ANNEN)
        html = klient.get("/aksje/EQNR?dag=2026-10-30").get_data(as_text=True)
        assert (
            '<p class="dagene">Denne dagen hadde signalet vært slik i 3 børsdager på rad, siden onsdag 28.10.</p>'
            in html
        )

    def test_siste_dag_som_ikke_er_i_dag(self, klient, aksje, monkeypatch):
        """Gjennomgangen, BH1, ECH6, VG1: i helga og foer kveldshentingen er
        siste boersdag ikke i dag. Ville feilet hvis siden sa «i dag» om den."""
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 11, 2, 12, 0).astimezone())
        skriv_vurdering("EQNR", date(2026, 10, 30), ANNEN)
        assert '<p class="dagene">Signalet ble slik denne dagen.</p>' in side(klient)

    def test_minst_paa_siste_dag_som_ikke_er_i_dag(self, klient, aksje, monkeypatch):
        """Svarene kl. 12:12 c) og 12:19 d): ogsaa uten «Velg dag». aksje
        skriver bare vurderingen for siste dag (31.10), saa boersdagen foer
        mangler og gir «minst». Ville feilet hvis siden sa «Signalet har vært
        slik i minst» om siste boersdag foer kveldshentingen (gjennomgangen
        kl. 13, BH6)."""
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 11, 2, 12, 0).astimezone())
        assert '<p class="dagene">Denne dagen hadde signalet vært slik minst siden lørdag 31.10.</p>' in side(klient)

    @pytest.mark.parametrize(
        "naa, setning",
        [
            (datetime(2026, 10, 31, 12, 0), "Signalet ble slik i dag."),
            (datetime(2026, 12, 31, 12, 0), "Signalet ble slik denne dagen."),
        ],
    )
    def test_velg_dag_paa_siste_dag(self, klient, aksje, monkeypatch, naa, setning):
        """Gjennomgangen, VG2, BH16: «Velg dag» paa siste dag i serien. Ville
        feilet hvis «i dag» fulgte valget av dag, og ikke datoen."""
        monkeypatch.setattr(app_modul, "naa", lambda: naa.astimezone())
        skriv_vurdering("EQNR", date(2026, 10, 30), ANNEN)
        html = klient.get("/aksje/EQNR?dag=2026-10-31").get_data(as_text=True)
        assert f'<p class="dagene">{setning}</p>' in html

    @pytest.mark.parametrize("feil", [sqlite3.OperationalError("database is locked"), RuntimeError("versjonen")])
    def test_uten_setning_naar_dagene_ikke_kan_leses(self, klient, aksje, monkeypatch, feil):
        """Gjennomgangen, VG4, BH7, ECH11: ville feilet hvis siden feilet,
        eller skrev en setning, naar lesingen av dagene feilet."""
        ekte = lagring_sqlite.SqliteVurderingslager.les_periode

        def les(self, symbol, fra, til):
            if fra == date.min:
                raise feil
            return ekte(self, symbol, fra, til)

        monkeypatch.setattr(lagring_sqlite.SqliteVurderingslager, "les_periode", les)
        skriv_kirad(kirad(aksje))
        html = side(klient)
        assert 'class="dagene"' not in html and TEKST in html


class TestSetningenOmSammeDag:
    """Story 10.2i, gruppens svar 5.11 kl. 19:13 og 23:36: appen skriver hva
    hovedindeksen, bransjen og antallene gjorde samme dag, for seg selv under
    KI-teksten som setningen om dagene (BH6), og setningen sier aldri at
    dagen forklarer signalet (BH7)."""

    @pytest.fixture
    def akrbp(self):
        """Svaret 6.11 kl. 11:15, 1: bransjen staar bare naar minst to aksjer
        i bransjen har en endring, saa AKRBP, ogsaa i Energi, har den samme
        kursen hver dag som EQNR."""
        rader = serie([200.0] * 61)
        # Gjennomgangen (BH11): AKRBP har kurs den samme dagen som EQNR i aksje.
        assert rader[-1].dato == serie([100.0] * 61)[-1].dato
        skriv_serie("AKRBP", rader, datetime.fromisoformat(HENTET), vurdert=False)

    @staticmethod
    def _bildet(hovedindeksen="steg", bransjen="falt", steg=9, falt=5):
        from dagene import Dagsbilde

        return Dagsbilde(
            dager=1,
            dager_minst=False,
            hovedindeksen=hovedindeksen,
            aksjer_steg=steg,
            aksjer_falt=falt,
            bransjen=bransjen,
        )

    @pytest.mark.parametrize(
        "hovedindeksen, bransjen, steg, falt, setning",
        [
            (
                "steg",
                "falt",
                9,
                5,
                "Samme dag steg hovedindeksen, bransjen falt i snitt, og 9 aksjer i lista steg og 5 falt.",
            ),
            (
                "falt",
                "steg",
                5,
                9,
                "Samme dag falt hovedindeksen, bransjen steg i snitt, og 5 aksjer i lista steg og 9 falt.",
            ),
            # Gjennomgangen (BH5, VG3, ECH10): 0 og 0 staar ikke, fordi kursene
            # ofte mangler da.
            ("uendret", "uendret", 0, 0, "Samme dag var hovedindeksen uendret, og bransjen var uendret i snitt."),
            (None, None, 0, 3, "Samme dag steg 0 aksjer i lista og 3 falt."),
            (None, "steg", 1, 14, "Samme dag steg bransjen i snitt, og 1 aksje i lista steg og 14 falt."),
            ("falt", None, 7, 7, "Samme dag falt hovedindeksen, og 7 aksjer i lista steg og 7 falt."),
            (None, None, 3, 12, "Samme dag steg 3 aksjer i lista og 12 falt."),
            # Regel 21: tusenskille som i setningen om dagene.
            (None, None, 1234, 0, "Samme dag steg 1 234 aksjer i lista og 0 falt."),
        ],
    )
    def test_setningen(self, hovedindeksen, bransjen, steg, falt, setning):
        """Ville feilet hvis setningen sa noe annet enn verdiene i
        dagsbildet, tok med et felt som mangler (None), eller ikke fulgte
        regel 21. Blant dem byttede retninger og byttede antall: steg og
        falt for hovedindeksen og bransjen, og 9 og 5 mot 5 og 9."""
        from dagene import setning_om_samme_dag

        assert setning_om_samme_dag(self._bildet(hovedindeksen, bransjen, steg, falt)) == setning

    def test_ingen_setning_uten_noe_aa_si(self):
        """Gjennomgangen (BH5, VG3, ECH10): ville feilet hvis en dag uten
        hovedindeksen, bransjen og antallene ga «0 aksjer i lista steg og 0
        falt» i stedet for ingen setning."""
        from dagene import setning_om_samme_dag

        assert setning_om_samme_dag(self._bildet(None, None, 0, 0)) is None

    @pytest.mark.parametrize("hovedindeksen", ["steg", "falt", "uendret", None])
    @pytest.mark.parametrize("bransjen", ["steg", "falt", "uendret", None])
    def test_sier_aldri_at_dagen_forklarer_signalet(self, hovedindeksen, bransjen):
        """BH7: ville feilet hvis setningen nevnte signalet, en grunn eller
        en sammenheng, som «fordi», «derfor», «preget» eller «forklar»."""
        from dagene import setning_om_samme_dag

        setning = setning_om_samme_dag(self._bildet(hovedindeksen, bransjen)).lower()
        for ord_ in ("signal", "fordi", "derfor", "preget", "forklar", "grunn", "på grunn av", "så "):
            assert ord_ not in setning, (ord_, setning)

    @pytest.mark.parametrize(
        "endret",
        [
            dict(hovedindeksen="opp"),
            dict(bransjen="Positiv"),
            dict(steg=-1),
            dict(falt=True),
            dict(steg=2.0),
        ],
    )
    def test_ugyldige_verdier_avvises(self, endret):
        """Ville feilet hvis en verdi utenfor de lukkede listene, et negativt
        antall, en bool eller et flyttall ga en setning."""
        from dagene import setning_om_samme_dag

        with pytest.raises(ValueError):
            setning_om_samme_dag(self._bildet(**endret))

    def test_paa_siden_rett_under_setningen_om_dagene(self, klient, aksje, akrbp):
        """Ville feilet hvis setningen manglet, sto et annet sted enn rett
        under setningen om dagene, eller ikke var regnet av lag_dagsbilde med
        lista, kursene og indeksen i basen. EQNR og AKRBP har samme kurs hver
        dag, og basen har ingen indeks, saa hovedindeksen mangler. Story
        10.9, del C: begge setningene foer KI-teksten i rammen."""
        skriv_kirad(kirad(aksje))
        html = side(klient)
        setning = '<p class="samme-dag">Samme dag var bransjen uendret i snitt.</p>'
        assert setning in html
        assert html.index('<p class="dagene">') < html.index(setning) < html.index(TEKST)
        assert "hovedindeksen" not in setning

    @pytest.mark.parametrize("kapsel", ["av", None])
    def test_ogsaa_med_ki_av(self, klient, aksje, akrbp, kapsel):
        """Som setningen om dagene: ogsaa med KI av og uten KI-rad. Ville
        feilet hvis setningen bare sto naar KI-teksten ble vist."""
        html = side(klient, kapsel)
        assert TEKST not in html and '<p class="samme-dag">Samme dag ' in html

    def test_ingen_setning_uten_vurdering(self, klient):
        """En dag med en grunn har ikke noe signal. Ville feilet hvis siden
        likevel skrev dagen."""
        rader = serie([100.0] * 61)
        skriv_serie("EQNR", rader, datetime.fromisoformat(HENTET), vurdert=False)
        skriv_vurdering("EQNR", rader[-1].dato, Grunn.KURS_IKKE_FRA_DAGEN)
        assert 'class="samme-dag"' not in side(klient)

    def test_uten_setning_naar_lista_ikke_kan_leses(self, klient, aksje, monkeypatch):
        """Ville feilet hvis siden feilet, eller skrev antall den ikke har
        lest, naar lista ikke kan leses. Setningen om dagene staar."""

        def feiler(self):
            raise sqlite3.OperationalError("database is locked")

        monkeypatch.setattr(lagring_sqlite.SqliteOversiktsleser, "oversikt", feiler)
        html = side(klient)
        assert 'class="samme-dag"' not in html and '<p class="dagene">' in html

    @pytest.mark.parametrize("feil", [ZeroDivisionError("kurs 0"), ValueError("verdi")])
    def test_uten_setning_naar_dagen_ikke_kan_regnes(self, klient, aksje, monkeypatch, feil):
        """Gjennomgangen (BH10, ECH12): ville feilet hvis siden ga 500 naar
        dagsbildet ikke kunne regnes, i stedet for siden med setningen om
        dagene og uten setningen om samme dag."""

        def lag(*_):
            raise feil

        monkeypatch.setattr(app_modul, "lag_dagsbilde", lag)
        html = side(klient)
        assert '<p class="dagene">' in html and 'class="samme-dag"' not in html

    def test_med_setning_naar_indeksen_ikke_kan_leses(self, klient, aksje, akrbp, monkeypatch):
        """Gjennomgangen (BH9): ville feilet hvis en RuntimeError fra
        indeksen ga 500 i stedet for setningen uten hovedindeksen."""

        def symboler(self):
            raise RuntimeError("versjonen")

        monkeypatch.setattr(lagring_sqlite.SqliteIndekslager, "symboler", symboler)
        html = side(klient)
        assert '<p class="samme-dag">Samme dag var bransjen uendret i snitt.</p>' in html

    def test_uten_bransjen_naar_bare_aksjen_har_endring(self, klient, aksje):
        """Svaret 6.11 kl. 11:15, 1 (BH1, ECH1, BH2): AKRBP er i Energi, men
        har ingen kurs paa dagen, saa bare EQNR har en endring. Ville feilet
        hvis siden skrev «bransjen ... i snitt» av EQNR alene. EQNR var
        uendret, og basen har ingen indeks, saa uten bransjen er det ingen
        setning; med AKRBP paa dagen staar den (testen over)."""
        rader = serie([200.0] * 60)
        assert rader[-1].dato < aksje
        skriv_serie("AKRBP", rader, datetime.fromisoformat(HENTET), vurdert=False)
        html = side(klient)
        assert '<p class="dagene">' in html and 'class="samme-dag"' not in html
