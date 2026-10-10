"""Story 3.4: demoversjonen (FR-411).

Demobasene lages bare i tmp_path (regel 22). conftest flytter BASE_STI dit,
og demo_sti() ligger ved siden av. Hvert kontrollpunkt er proevd med en
mutant (spesifikasjonen, Verification).
"""

import ast
import dataclasses
import hashlib
import shutil
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

import app as app_modul
import demo
import fetch_prices
import lagring_sqlite
from aksjedetalj import bygg_detalj
from kursdata import AKSJEUNIVERS
from lagring_sqlite import (
    DEMOMERKE,
    SqliteKurslager,
    SqliteOversiktsleser,
    SqliteVurderingslager,
    aapne_base,
    demo_sti,
    er_demobase,
)
from signalberegning import nodvendige_dager, vurder
from vurderingsdata import Grunn

SRC = Path(demo.__file__).resolve().parent

# sha256 av repr() av kurs-tabellen, sortert, regnet paa Windows med Python
# 3.13 10.10. CI kjoerer paa Linux, saa testen viser om kursene blir like paa
# tvers av plattformene (gjennomgangen av PR 1, BH11).
FINGERAVTRYKK_KURS = "73c277d2007d448f19ed95bd58ae30fac9bb7f43d60234455496aa1e0dbdec16"


@pytest.fixture(scope="module")
def mal(tmp_path_factory):
    """En demobase, laget en gang for modulen og kopiert av testene som trenger den."""
    sti = tmp_path_factory.mktemp("demomal") / "demo.db"
    demo.lag_demobase(sti, skriv=lambda _: None)
    return sti


@pytest.fixture
def demobase(mal):
    """Demobasen der webserveren leter med bryteren paa: demo_sti()."""
    sti = demo_sti()
    sti.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(mal, sti)
    return sti


@pytest.fixture
def klient(monkeypatch):
    monkeypatch.delenv(app_modul.I_DEMO, raising=False)
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    return app_modul.app.test_client()


def _tabeller(sti: Path) -> dict:
    c = sqlite3.connect(sti)
    try:
        ut = {t: c.execute(f"SELECT * FROM {t} ORDER BY rowid").fetchall()
              for t in ("aksje", "kurs", "kursserie", "vurdering")}
        # Tidspunktet migrasjonen ble kjoert, er ikke data. Resten av raden skal
        # vaere lik.
        ut["skjema_versjon"] = c.execute(
            "SELECT versjon, fil, sha256 FROM skjema_versjon ORDER BY versjon").fetchall()
        ut["application_id"] = c.execute("PRAGMA application_id").fetchone()[0]
        return ut
    finally:
        c.close()


def _sha(sti: Path) -> str:
    return hashlib.sha256(sti.read_bytes()).hexdigest()


class TestDemokommandoen:
    def test_lages_uten_nett_og_uten_noekkel(self, tmp_path, monkeypatch):
        """Nettsperren er paa (AD-8), og EODHD_API_KEY finnes ikke. Ville
        feilet hvis demokommandoen gjorde et kall eller leste noekkelen."""
        monkeypatch.delenv("EODHD_API_KEY", raising=False)
        demo.lag_demobase(tmp_path / "demo.db", skriv=lambda _: None)
        assert er_demobase(tmp_path / "demo.db")

    def test_importerer_ikke_hentingen(self):
        """Ville feilet hvis demo.py importerte requests, eodhd eller fetch_prices."""
        tre = ast.parse((SRC / "demo.py").read_text(encoding="utf-8"))
        moduler = {a.name.split(".")[0] for n in ast.walk(tre) if isinstance(n, ast.Import) for a in n.names}
        moduler |= {n.module.split(".")[0] for n in ast.walk(tre) if isinstance(n, ast.ImportFrom) and n.module}
        assert not moduler & {"requests", "eodhd", "fetch_prices", "lagring_fil"}

    def test_samme_froe_gir_like_baser(self, tmp_path, mal):
        """Ville feilet med et frø som endret seg mellom kjoeringene."""
        ny = tmp_path / "demo.db"
        demo.lag_demobase(ny, skriv=lambda _: None)
        assert _tabeller(ny) == _tabeller(mal)

    def test_kursene_har_samme_fingeravtrykk_paa_alle_plattformer(self, mal):
        """BH11: samme frø gir samme kurser ogsaa paa Linux i CI og i Docker.
        Ville feilet hvis libm eller Python ga andre tall enn paa Windows."""
        c = sqlite3.connect(mal)
        try:
            rader = c.execute(
                "SELECT symbol, dato, slutt, justert_slutt, volum FROM kurs ORDER BY symbol, dato").fetchall()
        finally:
            c.close()
        assert hashlib.sha256(repr(rader).encode()).hexdigest() == FINGERAVTRYKK_KURS

    def test_normalfordelingen_bruker_bare_random(self):
        """Python lover bare at random() er lik paa tvers av versjoner. Ville
        feilet med gauss() eller normalvariate()."""
        tre = ast.parse((SRC / "demo.py").read_text(encoding="utf-8"))
        kalt = {n.func.attr for n in ast.walk(tre) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        assert not kalt & {"gauss", "normalvariate", "lognormvariate", "expovariate", "choice", "uniform"}
        assert "random" in kalt

    def test_serien_er_lang_nok_for_grafen_og_ma50(self, mal):
        """FR-201, FR-202 og FR-406: minst 175 handelsdager, og MA50 fra grafens
        foerste punkt. Ville feilet med en kortere serie."""
        dager = demo.handelsdager()
        assert len(dager) >= 175 and dager[0] == date(2026, 1, 2) and dager[-1] == demo.SLUTTDATO
        c = aapne_base(mal, kjoer_migrasjoner=False, skrivebeskyttet=True)
        try:
            post = SqliteOversiktsleser(c).post("BRFE")
            detalj = bygg_detalj(post, SqliteKurslager(c, demo.DEMOUNIVERS).serie("BRFE"), demo.SLUTTDATO)
        finally:
            c.close()
        assert len(detalj.punkter) > 100
        assert all(p.ma50 is not None for p in detalj.punkter)

    def test_ingen_symboler_fra_den_ekte_lista(self):
        """FR-411: navnene er oppdiktet. Ville feilet med et symbol, en ticker
        eller et navn fra AKSJEUNIVERS."""
        for felt in ("symbol", "ticker", "navn"):
            ekte = {getattr(a, felt) for a in AKSJEUNIVERS}
            assert not ekte & {getattr(a, felt) for a in demo.DEMOUNIVERS}, felt
        assert len({a.symbol for a in demo.DEMOUNIVERS}) == 15

    def test_aksje_er_lik_demounivers(self, mal):
        """AD-21: de 15 fra 0003 er fjernet, og aksje er DEMOUNIVERS i samme
        rekkefoelge. Ville feilet hvis de ekte selskapene ble staaende."""
        c = sqlite3.connect(mal)
        try:
            rader = c.execute("SELECT symbol, ticker, navn, sektor FROM aksje ORDER BY rowid").fetchall()
        finally:
            c.close()
        assert rader == [dataclasses.astuple(a) for a in demo.DEMOUNIVERS]

    def test_hver_vurdering_er_det_vurder_gir(self, mal):
        """AD-7: én rad per aksje og boersdag, lik vurder() for serien fram til
        dagen. Ville feilet hvis en rad ble regnet paa en annen maate."""
        c = aapne_base(mal, kjoer_migrasjoner=False, skrivebeskyttet=True)
        try:
            kurslager = SqliteKurslager(c, demo.DEMOUNIVERS)
            lager = SqliteVurderingslager(c, lambda: datetime.now(timezone.utc), demo.DEMOUNIVERS)
            antall = c.execute("SELECT COUNT(*) FROM vurdering").fetchone()[0]
            dager = demo.handelsdager()
            assert antall == len(dager) * len(demo.DEMOUNIVERS)
            for aksje in demo.DEMOUNIVERS:
                serie = kurslager.serie(aksje.symbol)
                for dag in dager:
                    forventet = vurder([r for r in serie if r.dato <= dag], dag)
                    assert lager.les(aksje.symbol, dag) == forventet, (aksje.symbol, dag)
        finally:
            c.close()

    def test_tilstandene_siste_dag(self, mal):
        """Demoen viser tilstandene sidene har: en som skiller seg ut, en for
        kort serie og en uten kurser. Alle med kurser har siste dag, saa
        datoen over tabellen er SLUTTDATO."""
        c = aapne_base(mal, kjoer_migrasjoner=False, skrivebeskyttet=True)
        try:
            lager = SqliteVurderingslager(c, lambda: datetime.now(timezone.utc), demo.DEMOUNIVERS)
            siste = {a.symbol: lager.les(a.symbol, demo.SLUTTDATO) for a in demo.DEMOUNIVERS}
            antall_kurs = dict(c.execute("SELECT symbol, COUNT(*) FROM kurs GROUP BY symbol").fetchall())
            sist_dato = {s: date.fromisoformat(d) for s, d in c.execute(
                "SELECT symbol, MAX(dato) FROM kurs GROUP BY symbol").fetchall()}
        finally:
            c.close()
        assert siste["BRFE"].styrke >= 2
        assert all(d == demo.SLUTTDATO for d in sist_dato.values()), sist_dato
        assert siste["VRDS"] == Grunn.SIGNAL_IKKE_REGNET
        assert antall_kurs["VRDS"] == demo.NYLIG_NOTERT_DAGER < nodvendige_dager()
        assert "MTFJ" not in antall_kurs

    def test_merket_er_satt(self, mal):
        assert _tabeller(mal)["application_id"] == DEMOMERKE

    def test_bare_demokommandoen_setter_merket(self):
        """Ville feilet hvis hentingen eller webserveren satte application_id."""
        setter = sorted(
            sti.name for sti in SRC.glob("*.py")
            if "PRAGMA application_id =" in sti.read_text(encoding="utf-8")
        )
        assert setter == ["demo.py"]


class TestVaktene:
    def test_demokommandoen_nekter_en_ekte_base(self, tmp_path):
        """FR-411: ville feilet hvis demokommandoen skrev over en base uten merket."""
        sti = tmp_path / "demo.db"
        aapne_base(sti).close()
        foer = _sha(sti)
        with pytest.raises(demo.IkkeEnDemobase):
            demo.lag_demobase(sti, skriv=lambda _: None)
        assert _sha(sti) == foer

    def test_demokommandoen_nekter_en_tom_fil(self, tmp_path):
        sti = tmp_path / "demo.db"
        sti.write_bytes(b"")
        with pytest.raises(demo.IkkeEnDemobase):
            demo.lag_demobase(sti, skriv=lambda _: None)
        assert sti.read_bytes() == b""

    def test_main_gir_kode_1_og_skriver_ingenting(self, capsys):
        sti = demo_sti()
        aapne_base(sti).close()
        foer = _sha(sti)
        with pytest.raises(SystemExit) as slutt:
            demo.main([])
        assert slutt.value.code == 1 and _sha(sti) == foer
        assert "ikke en demobase" in capsys.readouterr().out

    def test_en_bygging_som_feiler_etterlater_ingen_halv_demobase(self, tmp_path, monkeypatch, mal):
        """BH2 og ECH5: stopper byggingen halvveis, finnes det ingen demo.db med
        merket der webserveren leter, og en demobase som fantes, staar."""
        sti = tmp_path / "demo.db"
        kall = []

        def feiler(rader, dag):
            kall.append(dag)
            if len(kall) > 100:
                raise RuntimeError("stopper halvveis")
            return vurder(rader, dag)

        monkeypatch.setattr(demo, "vurder", feiler)
        with pytest.raises(RuntimeError):
            demo.lag_demobase(sti, skriv=lambda _: None)
        assert not sti.exists() and not (tmp_path / "demo.db.ny").exists()

        shutil.copy(mal, sti)
        foer = _sha(sti)
        kall.clear()
        with pytest.raises(RuntimeError):
            demo.lag_demobase(sti, skriv=lambda _: None)
        assert _sha(sti) == foer

    def test_main_tar_ingen_ukjente_argumenter(self):
        with pytest.raises(SystemExit) as slutt:
            demo.main(["--ukjent"])
        assert slutt.value.code == 2 and not demo_sti().exists()

    def test_en_demobase_lages_paa_nytt(self, demobase, mal):
        demo.lag_demobase(demobase, skriv=lambda _: None)
        assert _tabeller(demobase) == _tabeller(mal)

    def test_hentingen_nekter_en_demobase_foer_alt_annet(self, tmp_path, mal):
        """AD-7: ville feilet hvis hentingen skrev kurser eller vurderinger i en
        demobase. Oeyeblikket mangler sone, saa en sjekk etter klokka ville
        reist ValueError i stedet."""
        base = tmp_path / "ose.db"
        shutil.copy(mal, base)
        foer = _sha(base)
        kall, ut = [], []
        with pytest.raises(SystemExit) as slutt:
            fetch_prices.kjoer(
                tmp_path / "raa", base, datetime(2026, 10, 9, 22, 30), "noekkel",
                lambda *a: kall.append(a) or [], ut.append, les_kvote=lambda _: kall.append("kvote"),
            )
        assert slutt.value.code == 1 and kall == [] and _sha(base) == foer
        assert "demobase" in ut[0] and "0 kall" in ut[0]

    def test_les_inn_nekter_en_demobase(self, tmp_path, mal):
        base = tmp_path / "ose.db"
        shutil.copy(mal, base)
        foer = _sha(base)
        ut = []
        with pytest.raises(SystemExit) as slutt:
            fetch_prices.les_inn(tmp_path / "finnes-ikke.json", base, ut.append)
        assert slutt.value.code == 1 and _sha(base) == foer and "demobase" in ut[0]

    def test_en_base_som_mangler_eller_ikke_kan_leses_er_ikke_en_demobase(self, tmp_path):
        """Hentingen gaar videre som foer. Ville feilet hvis en ulesbar base
        stoppet hentingen."""
        assert not er_demobase(tmp_path / "finnes-ikke.db")
        soeppel = tmp_path / "soeppel.db"
        soeppel.write_bytes(b"ikke en sqlite-base" * 10)
        assert not er_demobase(soeppel)
        ekte = tmp_path / "ose.db"
        aapne_base(ekte).close()
        assert not er_demobase(ekte)
        fetch_prices.nekt_demobase(soeppel, lambda _: None)
        fetch_prices.nekt_demobase(tmp_path / "finnes-ikke.db", lambda _: None)


class TestSidene:
    def test_bryteren_uten_demobase_viser_kommandoen(self, klient, monkeypatch):
        """FR-411: webserveren lager aldri demobasen. Ville feilet hvis den
        laget en tom base og viste hentekommandoen."""
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        html = klient.get("/").data.decode("utf-8")
        assert f"<code>{demo.DEMOKOMMANDO}</code>" in html
        assert not demo_sti().exists()
        assert "Eksempeltall" not in html
        assert klient.get("/aksje/BRFE").status_code == 404

    def test_bryteren_med_demobase_viser_eksempeltall(self, klient, monkeypatch, demobase):
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        oversikt = klient.get("/").data.decode("utf-8")
        detalj = klient.get("/aksje/BRFE").data.decode("utf-8")
        assert "Eksempeltall" in oversikt and "Eksempeltall" in detalj
        assert "Oslo Børs · 2026-10-09 · 14 aksjer" in oversikt
        for tekst in ("Brattfjell Energi", "skiller seg ut",
                      "signalet kunne ikke regnes", "Matfjord Merkevarer"):
            assert tekst in oversikt, tekst
        assert "Trenger 51 dager" in klient.get("/aksje/VRDS").data.decode("utf-8")
        assert not Path(lagring_sqlite.BASE_STI).exists()

    def test_merket_foelger_basen_ikke_bryteren(self, klient, monkeypatch, mal):
        """FR-411 og NFR-08: ville feilet hvis «Eksempeltall» fulgte bryteren.
        En demobase uten bryter viser merket, og en ekte base med bryter
        viser det ikke."""
        ekte = Path(lagring_sqlite.BASE_STI)
        ekte.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(mal, ekte)
        assert "Eksempeltall" in klient.get("/").data.decode("utf-8")

        ekte.unlink()
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        aapne_base(demo_sti()).close()
        assert "Eksempeltall" not in klient.get("/").data.decode("utf-8")

    def test_den_ekte_basen_uten_bryter_har_ikke_merket(self, klient):
        aapne_base(Path(lagring_sqlite.BASE_STI)).close()
        html = klient.get("/").data.decode("utf-8")
        assert "Eksempeltall" not in html and app_modul.HENTEKOMMANDO in html

    def test_bare_verdien_1_slaar_paa_bryteren(self, monkeypatch):
        for verdi, forventet in (("1", True), ("0", False), ("", False)):
            monkeypatch.setenv(app_modul.I_DEMO, verdi)
            assert app_modul.demo_paa() is forventet, verdi

    def test_demo_flagget_setter_bryteren(self, monkeypatch):
        """--demo til python src/app.py setter OSE_DEMO, saa kommandoen er lik i
        PowerShell og bash. Ville feilet hvis flagget ikke slo paa bryteren."""
        # setenv foerst, saa monkeypatch fjerner variabelen etterpaa, ogsaa
        # naar les_flagg har satt den (ellers lekker den til neste test).
        monkeypatch.setenv(app_modul.I_DEMO, "0")
        app_modul.les_flagg([])
        assert not app_modul.demo_paa()
        app_modul.les_flagg(["--demo"])
        assert app_modul.demo_paa()
        kilde = (SRC / "app.py").read_text(encoding="utf-8")
        hoved = kilde.split('if __name__ == "__main__":', 1)[1]
        assert hoved.index("les_flagg(sys.argv[1:])") < hoved.index("app.run(")

    def test_ulesbar_demobase_gir_503_med_navnet_og_kommandoen(self, klient, monkeypatch):
        """VG1: med bryteren og en demo.db som ikke kan leses, svarer begge
        sidene 503, nevner demo.db og viser kommandoen som lager den paa nytt."""
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        sti = demo_sti()
        sti.parent.mkdir(parents=True, exist_ok=True)
        sti.write_bytes(b"ikke en sqlite-base" * 10)
        for rute in ("/", "/aksje/BRFE"):
            svar = klient.get(rute)
            html = svar.data.decode("utf-8")
            assert svar.status_code == 503, rute
            assert "<code>demo.db</code>" in html and demo.DEMOKOMMANDO in html, rute

    def test_i_docker_viser_sidene_docker_kommandoen_for_demobasen(self, klient, monkeypatch):
        """PR 2, ECH7: med OSE_I_DOCKER=1, som Dockerfile setter, viser siden og
        feilsiden kommandoen som lager demobasen i volumet ose-demo. Ville
        feilet hvis containeren viste uv-kommandoen, som ikke finnes der."""
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        monkeypatch.setenv(app_modul.I_DOCKER, "1")
        html = klient.get("/").data.decode("utf-8")
        assert f"<code>{demo.DEMOKOMMANDO_DOCKER}</code>" in html
        assert demo.DEMOKOMMANDO not in html
        sti = demo_sti()
        sti.parent.mkdir(parents=True, exist_ok=True)
        sti.write_bytes(b"ikke en sqlite-base" * 10)
        for rute in ("/", "/aksje/BRFE"):
            svar = klient.get(rute)
            html = svar.data.decode("utf-8")
            assert svar.status_code == 503, rute
            assert f"<code>{demo.DEMOKOMMANDO_DOCKER}</code>" in html, rute
            assert demo.DEMOKOMMANDO not in html, rute

    def test_bare_verdien_1_gir_docker_kommandoen_for_demobasen(self, monkeypatch):
        """Som hentekommandoen: ville feilet hvis enhver verdi ga Docker-kommandoen."""
        for verdi, forventet in (("1", demo.DEMOKOMMANDO_DOCKER), ("0", demo.DEMOKOMMANDO),
                                 ("", demo.DEMOKOMMANDO)):
            monkeypatch.setenv(app_modul.I_DOCKER, verdi)
            assert app_modul.demokommando() == forventet, verdi
        monkeypatch.delenv(app_modul.I_DOCKER)
        assert app_modul.demokommando() == demo.DEMOKOMMANDO

    def test_feilsiden_har_eksempeltall_for_en_demobase(self, klient, monkeypatch, demobase):
        """VG2: feiler lesingen etter at en demobase er aapnet, har feilsiden
        ogsaa «Eksempeltall»."""
        import sqlite3 as sql

        monkeypatch.setenv(app_modul.I_DEMO, "1")

        def feiler():
            raise sql.OperationalError("disk I/O error")

        monkeypatch.setattr(app_modul, "hent_oversiktsleser", feiler)
        svar = klient.get("/")
        assert svar.status_code == 503 and "Eksempeltall" in svar.data.decode("utf-8")

    def test_en_demobase_som_ose_db_migreres_ikke(self, klient, mal, monkeypatch):
        """BH6: uten bryteren, med en demobase der den ekte skal ligge, viser
        webserveren den med «Eksempeltall» og skriver ingenting til den. En
        migrering av en base paa siste versjon endrer ingen byte, saa testen
        ser ogsaa paa kallene: ingen migrering og bare skrivebeskyttet
        aapning (mutanten M20)."""
        ekte = Path(lagring_sqlite.BASE_STI)
        ekte.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(mal, ekte)
        foer = _sha(ekte)
        migrert, aapninger = [], []
        ekte_aapne = app_modul.aapne_base
        monkeypatch.setattr(app_modul, "_migrer_en_gang", migrert.append)

        def aapne(sti, **kw):
            aapninger.append(kw)
            return ekte_aapne(sti, **kw)

        monkeypatch.setattr(app_modul, "aapne_base", aapne)
        assert "Eksempeltall" in klient.get("/").data.decode("utf-8")
        assert _sha(ekte) == foer
        assert migrert == []
        assert aapninger and all(kw.get("skrivebeskyttet") for kw in aapninger)

    def test_demobase_uten_kurser_viser_demokommandoen(self, klient, monkeypatch, mal):
        """ECH6: med bryteren og en demobase uten kurser viser siden
        demokommandoen, ikke hentekommandoen, som skriver til ose.db."""
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        sti = demo_sti()
        sti.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(mal, sti)
        c = sqlite3.connect(sti)
        with c:
            c.execute("DELETE FROM vurdering")
            c.execute("DELETE FROM kurs")
            c.execute("DELETE FROM kursserie")
        c.close()
        html = klient.get("/").data.decode("utf-8")
        assert demo.DEMOKOMMANDO in html and app_modul.HENTEKOMMANDO not in html
        # VG1 i gjennomgangen av PR 2: i Docker er det Docker-kommandoen ogsaa her.
        monkeypatch.setenv(app_modul.I_DOCKER, "1")
        html = klient.get("/").data.decode("utf-8")
        assert f"<code>{demo.DEMOKOMMANDO_DOCKER}</code>" in html
        assert demo.DEMOKOMMANDO not in html and app_modul.HENTEKOMMANDO_DOCKER not in html
