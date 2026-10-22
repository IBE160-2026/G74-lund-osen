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
# Endret 17.10 (alle 10 kombinasjonene, spesifikasjonen under story 3.4): tre
# rader paa SLUTTDATO er nye. Foer var det 73c277d2...dbdec16.
FINGERAVTRYKK_KURS = "e92012b8df47f6b0e00b7cae9c0a833956da3c90d668f7ac58173410c44159dc"
# Tabellen uten de tre radene for SISTE_DAG paa SLUTTDATO, og vurderingene foer
# SLUTTDATO, regnet med koden foer (src/demo.py paa main, 43de066, som ga det
# gamle FINGERAVTRYKK_KURS) og etter 17.10: like, saa froeet og de andre dagene
# staar som foer (gjennomgangen, BH5).
FINGERAVTRYKK_KURS_UTEN_SISTE_DAG = "f3bb1e35ae082562dafb38e0aa5667fede6cf9d8dc296d6ac73d55b57a762e02"
# Story 3.4c: vurderingene bare fra STARTDAG, 21.09, saa radene foer siste dag
# er faerre. Var 74aaaa15....
FINGERAVTRYKK_VURDERING_FOER_SISTE_DAG = "ee1488d3b8c771514ed2fb065c6126e4ccf4e1e30ab4ebab447a5361b1f5cf55"


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    """Story 8.0c: datoene paa sidene viser aaret naar det er et annet enn i
    dag. Uten fast klokke ville demotestene feilet fra 01.01.2027 (VG1)."""
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))


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
        ut = {
            t: c.execute(f"SELECT * FROM {t} ORDER BY rowid").fetchall()
            for t in ("aksje", "kurs", "kursserie", "vurdering", "indeks", "indeksserie")
        }
        # Tidspunktet migrasjonen ble kjoert, er ikke data. Resten av raden skal
        # vaere lik.
        ut["skjema_versjon"] = c.execute("SELECT versjon, fil, sha256 FROM skjema_versjon ORDER BY versjon").fetchall()
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
                "SELECT symbol, dato, slutt, justert_slutt, volum FROM kurs ORDER BY symbol, dato"
            ).fetchall()
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
        dagen. Ville feilet hvis en rad ble regnet paa en annen maate.

        Story 3.4c: bare fra STARTDAG, og ingen rad foer."""
        c = aapne_base(mal, kjoer_migrasjoner=False, skrivebeskyttet=True)
        try:
            kurslager = SqliteKurslager(c, demo.DEMOUNIVERS)
            lager = SqliteVurderingslager(c, lambda: datetime.now(timezone.utc), demo.DEMOUNIVERS)
            antall = c.execute("SELECT COUNT(*) FROM vurdering").fetchone()[0]
            dager = [d for d in demo.handelsdager() if d >= demo.STARTDAG]
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
            sist_dato = {
                s: date.fromisoformat(d)
                for s, d in c.execute("SELECT symbol, MAX(dato) FROM kurs GROUP BY symbol").fetchall()
            }
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
            sti.name for sti in SRC.glob("*.py") if "PRAGMA application_id =" in sti.read_text(encoding="utf-8")
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
                tmp_path / "raa",
                base,
                datetime(2026, 10, 9, 22, 30),
                "noekkel",
                lambda *a: kall.append(a) or [],
                ut.append,
                les_kvote=lambda _: kall.append("kvote"),
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
        # Story 8.0c (4a): linja over tabellen sier ikke «Oslo Børs», og
        # merket har «Demoversjon.» foran. Story 8.0e, svar 1: linja sier
        # «Demo Børs», som endrer beslutning 3 i 8.0c.
        # Story 8.0d, PR 2b: alle de 15 aksjene, også den uten kurser (14.10).
        assert "Demo Børs · 09.10 · 15 aksjer" in oversikt
        assert "Oslo Børs · " not in oversikt
        assert f"Demoversjon. {app_modul.EKSEMPELTALL_MERKE}" in oversikt
        assert f"Demoversjon. {app_modul.EKSEMPELTALL_MERKE}" in detalj
        for tekst in ("Brattfjell Energi", "skiller seg ut", "signalet kunne ikke regnes", "Matfjord Merkevarer"):
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

    def test_hjelpen_virker_ogsaa_i_demoen(self, klient, monkeypatch, demobase):
        """Story 8.0b: «?» og tekstene vises ogsaa med demobasen, ved siden
        av «Eksempeltall». Ville feilet hvis hjelpen var skjult i demoen."""
        from hjelpetekster import hjelpetekster

        tekster = hjelpetekster()
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        for adresse, vinduer, noekler in (
            # Story 8.0c: hvert «?» ved det det forklarer.
            ("/", ("hjelp-signalstyrke", "hjelp-retning"), ("signalstyrke", "ukjent")),
            ("/aksje/BRFE", ("hjelp-graf", "hjelp-trend", "hjelp-retning-aksje"), ("grafen", "trend", "ukjent_aksje")),
            ("/aksje/VRDS", ("hjelp-sjekkene", "hjelp-retning-aksje"), ("antall_dager", "ukjent_aksje")),
        ):
            html = klient.get(adresse).data.decode("utf-8")
            assert "Eksempeltall" in html, adresse
            for vindu in vinduer:
                # «?»-knappen, ikke lukkeknappen inne i vinduet, som ogsaa har
                # popovertarget (mutant M12).
                assert f'class="hjelpeknapp" popovertarget="{vindu}"' in html, (adresse, vindu)
                assert f'<div id="{vindu}" class="hjelpevindu" popover>' in html, (adresse, vindu)
            for noekkel in noekler:
                assert tekster[noekkel].tekst in html, (adresse, noekkel)

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
        for verdi, forventet in (("1", demo.DEMOKOMMANDO_DOCKER), ("0", demo.DEMOKOMMANDO), ("", demo.DEMOKOMMANDO)):
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
        # Story 8.0c: «Demoversjon.» og linja nederst ogsaa paa feilsiden.
        html = svar.data.decode("utf-8")
        # Story 8.0d: merket staar som egen rad i stripa ogsaa her.
        stripe = html.split('<header class="stripe">', 1)[1].split("</header>", 1)[0]
        # Story 3.3i (U51): lenken til den ekte versjonen etter merket.
        assert f'<p class="eksempeltall">Demoversjon. {app_modul.EKSEMPELTALL_MERKE} Ekte kurser' in stripe
        assert f"Demoversjon. {app_modul.EKSEMPELTALL_MERKE}" in html
        assert app_modul.UNDER_ARBEID_TEKST in html

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
        # Story 8.0d, PR 2 (VG8): én h1, «Markedsoversikt» (svar 3).
        assert html.count("<h1") == 1 and '<h1 class="overskrift">Markedsoversikt</h1>' in html
        # VG1 i gjennomgangen av PR 2: i Docker er det Docker-kommandoen ogsaa her.
        monkeypatch.setenv(app_modul.I_DOCKER, "1")
        html = klient.get("/").data.decode("utf-8")
        assert f"<code>{demo.DEMOKOMMANDO_DOCKER}</code>" in html
        assert demo.DEMOKOMMANDO not in html and app_modul.HENTEKOMMANDO_DOCKER not in html


class TestStory80cIDemoen:
    """FR-411, tverrgaaende fra 8.0c: det storyen viser, vises ogsaa med
    demobasen."""

    def test_merkingen_og_ordene_i_demoen(self, klient, monkeypatch, demobase):
        import re

        from test_hjelpetekster import VALGT_BORT, synlig_tekst

        monkeypatch.setenv(app_modul.I_DEMO, "1")
        oversikt = klient.get("/").data.decode("utf-8")
        detalj = klient.get("/aksje/BRFE").data.decode("utf-8")
        assert re.search(r'<span class="pille[^"]*">\d av 3</span>', oversikt)
        assert '<tr class="utslag">' in oversikt
        assert re.search(r'<span class="ord">(positiv|negativ|ingen utslag)</span>', detalj)
        assert "Signalstyrken sier ikke om du bør kjøpe eller selge." in detalj
        # Story 3.4b (gruppens svar 18.10 kl. 20:08): ordlista gjelder vår
        # tekst, ikke KI-teksten, til prompten faar den i versjon 3. Bare
        # avsnittet med modellens ord tas ut. «Laget av KI» og resten av
        # delen sjekkes som foer.
        # Gjennomgangen, ECH2: BRFE har teksten bare naar raden besto (FR-604).
        from demo_ki import les_radene

        vist = sum(1 for r in les_radene() if r.emne.symbol == "BRFE" and r.besto)
        assert detalj.count('<p class="ki-tekst">') == vist
        detalj = re.sub(r'<p class="ki-tekst">.*?</p>', "", detalj, flags=re.DOTALL)
        for html in (oversikt, detalj):
            assert app_modul.UNDER_ARBEID_TEKST in html
            assert f"Demoversjon. {app_modul.EKSEMPELTALL_MERKE}" in html
            assert "popovertarget=" in html
            for ord_ in VALGT_BORT:
                assert not re.search(ord_, synlig_tekst(html), re.IGNORECASE), ord_

    def test_setningene_om_ingen_utslag_i_demoen(self, klient, monkeypatch, demobase):
        """Svar 3 paa BH1/ECH2 med demobasen (FR-411). Demobasen har aksjer
        som skiller seg ut, saa testen tar bort de vurderingene i kopien i
        tmp (regel 22). VRDS har ingen vurdering, saa begge setningene staar."""
        import re
        import sqlite3

        monkeypatch.setenv(app_modul.I_DEMO, "1")
        foer = klient.get("/").data.decode("utf-8")
        assert "Ingen aksjer skilte seg ut" not in foer and "ble vurdert." not in foer
        tilkobling = sqlite3.connect(demo_sti())
        with tilkobling:
            siste = tilkobling.execute("SELECT MAX(dato) FROM vurdering").fetchone()[0]
            tilkobling.execute(
                "DELETE FROM vurdering WHERE dato = ? AND styrke >= ?", (siste, app_modul.STANDARD.terskel)
            )
        tilkobling.close()
        html = klient.get("/").data.decode("utf-8")
        assert "Ingen aksjer skilte seg ut: ingen fikk 2 av 3 eller mer." in html
        treff = re.search(r"(\d+) av (\d+) aksjer ble vurdert\.", html)
        assert treff and int(treff.group(1)) < int(treff.group(2)), treff

    def test_ingen_synlig_iso_dato_i_demoen(self, klient, monkeypatch, demobase):
        """Beslutning 12 med demobasen (FR-411)."""
        import re

        from test_hjelpetekster import synlig_tekst

        monkeypatch.setenv(app_modul.I_DEMO, "1")
        for sti in ("/", "/aksje/BRFE", "/aksje/VRDS"):
            tekst = synlig_tekst(klient.get(sti).data.decode("utf-8"))
            assert not re.search(r"\b\d{4}-\d{2}-\d{2}\b", tekst), sti
        assert re.search(r'<text class="maanedstekst"', klient.get("/aksje/BRFE").data.decode("utf-8"))


class TestStory80eIDemoen:
    """FR-411: tabellen fra 8.0e vises ogsaa med demobasen."""

    def test_t_b_og_i_og_de_to_delene_i_demoen(self, klient, monkeypatch, demobase):
        import re

        from test_app import _deler, _regel, _stil, _tabell

        monkeypatch.setenv(app_modul.I_DEMO, "1")
        html = klient.get("/").data.decode("utf-8")
        tabell = _tabell(html)
        assert tabell.deler == ["Skilte seg ut", "Øvrige aksjer"]
        deler = _deler(html)
        assert deler["Skilte seg ut"] and deler["Øvrige aksjer"]
        vurdert = [rad[3] for rad in tabell.rader if rad[3][0].isdigit()]
        assert vurdert
        for celle in vurdert:
            assert re.fullmatch(r"\d av 3 T (\+1|0|-1) B (\+1|0|-1) I (\+1|0|-1)( skiller seg ut)?", celle), celle
        assert "background: var(--fyll)" in _regel(_stil(html), ".pille.tre-av-tre")
        # BH5 og ECH1 i gjennomgangen: pillen med fyll staar ogsaa i demoen.
        assert '<span class="pille tre-av-tre">3 av 3</span>' in html


class TestStory80eTekstIDemoen:
    """FR-411 og svar 1: teksten over tabellen ogsaa med demobasen, med
    «Demo Børs» der den ekte versjonen sier «Oslo Børs»."""

    def test_teksten_over_tabellen_i_demoen(self, klient, monkeypatch, demobase):
        from test_app import _synlig

        monkeypatch.setenv(app_modul.I_DEMO, "1")
        html = klient.get("/").data.decode("utf-8")
        tekst = _synlig(html)
        # Story 8.0d, PR 2b: M er alle de 15 aksjene i lista (14.10).
        # 17.10: 7 med alle 10 kombinasjonene (spesifikasjonen under story 3.4).
        assert "7 av 15 aksjer skilte seg ut fredag" in tekst
        assert "OSE Signal er et regelbasert signal for aksjer på Demo Børs: 3 faste sjekker" in tekst
        assert "Hos disse" in tekst or "Hos 1 aksje" in tekst
        assert "fikk utslag på alle 3 sjekkene." in tekst
        assert "Slik leser du tabellen" in tekst
        # Merket sier «ikke data fra Oslo Børs», og det staar. Innledningen og
        # linja over tabellen sier «Demo Børs».
        assert "aksjer på Oslo Børs" not in tekst and "Oslo Børs ·" not in tekst


class TestAlleTiKombinasjonene:
    """Beslutningen 16.10 kl. 21:49 under story 2.12: alle 10
    fargekombinasjonene av de tre sjekkene paa siste demodag, fra 3 groenne til
    3 graa. Lest fra vurdering i demobasen, ikke regnet paa nytt. Mutantene
    staar i spesifikasjonen under story 3.4."""

    @staticmethod
    def _siste_dag(mal):
        c = sqlite3.connect(mal)
        try:
            return {
                s: (t, b, i, styrke, grunn)
                for s, t, b, i, styrke, grunn in c.execute(
                    "SELECT symbol, trend, bevegelse, interesse, styrke, grunn FROM vurdering WHERE dato = ?",
                    (demo.SLUTTDATO.isoformat(),),
                )
            }
        finally:
            c.close()

    def test_alle_ti_kombinasjonene_paa_sluttdato(self, mal):
        """Ville feilet hvis en av reglene i SISTE_DAG ble tatt bort (mutantene
        R1-R3): da mangler 3 groenne, 2 groenne og 1 roed, eller 1 groenn og 2
        graa."""
        rader = self._siste_dag(mal)
        kombinasjoner = {
            (sum(v == 1 for v in r[:3]), sum(v == -1 for v in r[:3]), sum(v == 0 for v in r[:3]))
            for r in rader.values()
            if r[4] is None
        }
        alle = {(g, r, 3 - g - r) for g in range(4) for r in range(4 - g)}
        assert len(alle) == 10
        assert kombinasjoner == alle, sorted(alle - kombinasjoner)

    def test_de_to_med_grunn_og_brattfjell_staar(self, mal):
        rader = self._siste_dag(mal)
        assert rader[demo.NYLIG_NOTERT][4] == Grunn.SIGNAL_IKKE_REGNET.value
        assert rader[demo.UTEN_KURSER][4] == Grunn.KURS_IKKE_FRA_DAGEN.value
        assert rader[demo.SKILLER_SEG_UT][3] >= 2
        assert sum(1 for r in rader.values() if r[4] is None) == 13

    def test_minst_sju_av_tretten_skiller_seg_ut(self, mal):
        """7 av de 10 kombinasjonene har minst to sjekker som slaar ut."""
        rader = self._siste_dag(mal)
        assert sum(1 for r in rader.values() if r[4] is None and r[3] >= 2) >= 7

    def test_de_tre_reglene_gir_kombinasjonen_de_lover(self, mal):
        """Kommentaren ved hver regel i SISTE_DAG stemmer med basen."""
        rader = self._siste_dag(mal)
        assert rader["KVST"][:3] == (1, 1, 1)
        assert rader["LKSV"][:3] == (-1, 1, 1)
        assert rader["LSTF"][:3] == (0, 1, 0)

    def test_reglene_gjelder_ikke_aksjene_med_egen_regel(self):
        """Gjennomgangen, BH1 og ECH2-3: en regel i SISTE_DAG for Brattfjell
        Energi eller en av de to med grunn ville skrevet over eller blitt borte."""
        assert not set(demo.SISTE_DAG) & {demo.SKILLER_SEG_UT, demo.NYLIG_NOTERT, demo.UTEN_KURSER}

    def test_froeet_og_de_andre_dagene_staar_som_foer(self, mal):
        """Ville feilet hvis en ny regel endret en annen dag eller en annen
        aksje. Et tall mindre fra froeet paa SLUTTDATO kan ingen test se, fordi
        det er siste dag (gjennomgangen, VG1)."""
        c = sqlite3.connect(mal)
        try:
            kurs = c.execute(
                "SELECT symbol, dato, slutt, justert_slutt, volum FROM kurs ORDER BY symbol, dato"
            ).fetchall()
            vurdering = c.execute(
                "SELECT * FROM vurdering WHERE dato < ? ORDER BY symbol, dato", (demo.SLUTTDATO.isoformat(),)
            ).fetchall()
        finally:
            c.close()
        uten = [r for r in kurs if not (r[1] == demo.SLUTTDATO.isoformat() and r[0] in demo.SISTE_DAG)]
        assert len(kurs) - len(uten) == len(demo.SISTE_DAG) == 3
        assert hashlib.sha256(repr(uten).encode()).hexdigest() == FINGERAVTRYKK_KURS_UTEN_SISTE_DAG
        assert hashlib.sha256(repr(vurdering).encode()).hexdigest() == FINGERAVTRYKK_VURDERING_FOER_SISTE_DAG


class TestHovedindeksenIDemoen:
    """Story 2.9: demoen viser demoindeksen som den ekte versjonen viser
    OSEBX. Matfjord Merkevarer har ingen kurser og navngis."""

    def test_demix_og_matfjord_navngis(self, klient, monkeypatch, demobase):
        import re

        from test_app import _synlig

        monkeypatch.setenv(app_modul.I_DEMO, "1")
        html = klient.get("/").data.decode("utf-8")
        delen = html.split('<section class="hovedindeks"', 1)[1].split("</section>", 1)[0]
        tekst = _synlig(delen)
        # Gjennomgangen, BH17: OSEBX sjekkes bare i delen.
        assert "Hovedindeksen DEMIX" in tekst and "OSEBX" not in delen
        assert re.search(r"\d+ av 14 gikk bedre enn indeksen\.", tekst), tekst
        assert "Ikke med, uten kurs 09.10: Matfjord Merkevarer." in tekst
        assert 'class="indeksdato"' not in delen


class TestSoeyleneIDemoen:
    """Story 2.9b: demoen viser søylene mot DEMIX, som den ekte versjonen
    viser dem mot OSEBX. Matfjord Merkevarer har ingen kurser og får ingen
    søyle."""

    def _figur(self, klient, monkeypatch):
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        html = klient.get("/").data.decode("utf-8")
        delen = html.split('<section class="hovedindeks"', 1)[1].split("</section>", 1)[0]
        return html, delen.split('<figure class="soeyler">', 1)[1].split("</figure>", 1)[0]

    def test_soeylene_mot_demix(self, klient, monkeypatch, demobase):
        import re

        from test_app import _synlig

        _, figur = self._figur(klient, monkeypatch)
        tickere = re.findall(r'<span class="ticker">([^<]+)</span>', figur)
        assert len(tickere) == 14 and "MTFJ" not in tickere
        assert len(re.findall(r'<span class="indekslinje (?:opp|ned|null)"', figur)) == 1
        assert "Søyler for 14 aksjer 09.10, fra størst fall til størst stigning." in _synlig(figur)

    def test_soeylene_staar_fra_stoerst_fall_som_tallene_for_skjermleser(self, klient, monkeypatch, demobase):
        """Endringene i lista for skjermleser står i samme rekkefølge som
        søylene, og stiger fra venstre."""
        import re

        _, figur = self._figur(klient, monkeypatch)
        liste = figur.split('<ol class="skjult">', 1)[1].split("</ol>", 1)[0]
        tall = [
            float(t.replace(" ", "").replace(",", ".").replace("%", ""))
            for t in re.findall(r"\): ([+-]?\d+,\d+ %)", liste)
        ]
        assert len(tall) == 14
        assert tall == sorted(tall)

    def test_gult_bransjesymbol_der_tabellen_har_3_av_3(self, klient, monkeypatch, demobase):
        """Designregler §3: gult ved 3 av 3 på siste børsdag. Ville feilet
        hvis 3 av 3 ble regnet et annet sted enn i tabellen."""
        import re

        html, figur = self._figur(klient, monkeypatch)
        tabell = html.split('class="tabellboks"', 1)[1]
        i_tabellen = set()
        for rad in re.findall(r"<tr [^>]*>.*?</tr>", tabell, re.DOTALL):
            if 'class="pille tre-av-tre"' in rad:
                i_tabellen.add(re.search(r'href="/aksje/([^"]+)"', rad).group(1))
        gule = set(
            re.findall(r'<span class="etikett tre-av-tre">.*?<span class="ticker">([^<]+)</span>', figur, re.DOTALL)
        )
        assert i_tabellen and gule == i_tabellen
        # Gjennomgangen (BH2): «3 av 3» står også i lista for skjermleser.
        liste = figur.split('<ol class="skjult">', 1)[1].split("</ol>", 1)[0]
        for symbol in i_tabellen:
            assert re.search(rf"\({symbol}, [^)]*\): [^<]*, 3 av 3\.</li>", liste), symbol
        # Gjennomgangen (VG2): fargen på det gule symbolet er Gult symbol.
        from test_app import _regel, _stil

        assert "color: var(--gul-symbol)" in _regel(_stil(html), ".soeyler .etikett.tre-av-tre .bransjesymbol")


class TestIndekslinjaIDemoen:
    """Story 2.9c: aksjesiden i demoen viser DEMIX som stiplet linje."""

    def test_demix_i_kursgrafen(self, klient, monkeypatch, demobase):
        import re

        from test_app import _synlig

        monkeypatch.setenv(app_modul.I_DEMO, "1")
        html = klient.get("/aksje/BRFE").data.decode("utf-8")
        indeks = re.search(r'<polyline class="indekslinje" points="([^"]*)">', html).group(1).split()
        kurs = re.search(r'<polyline class="kurslinje" points="([^"]*)">', html).group(1).split()
        assert indeks[0] == kurs[0] and len(indeks) > 20
        # Gjennomgangen (BH15): linja er innenfor tegneflaten og flytter seg.
        from graf import HOYDE, MARG_Y

        y = [float(par.split(",")[1]) for par in indeks]
        assert all(MARG_Y - 0.05 <= v <= HOYDE - MARG_Y + 0.05 for v in y)
        assert y[-1] != y[0]
        assert "Den stiplede linja er hovedindeksen DEMIX" in _synlig(html)
        # «?» forklarer linja.
        vinduet = html.split('<div id="hjelp-graf"', 1)[1].split('<div id="hjelp-', 1)[0]
        assert "Den stiplede linja:" in vinduet


class TestKlokkeslettetSomDenEkte:
    """Story 2.3, hentingen fra kl. 22:00 fra 20.10 (gruppens svar 19.10
    kl. 22:19): demoen er lik den ekte (beslutningen 16.10 kl. 11:46), saa
    hentingen i demobasen er kl. 22:15 og vurderingene kl. 22:30, som foer
    19.10. 19.10 var de kl. 21:15 og 21:30.
    Fingeravtrykkene av demobasen endres ikke: kurs og vurdering har ingen
    klokkeslett, og FINGERAVTRYKK_KURS og FINGERAVTRYKK_VURDERING_FOER_SISTE_DAG
    staar. Avtrykkene bak de to bildene i test_docker.py endres, fordi stripa
    sier kl. 22.15 (gjennomgangen 20.10, BH9)."""

    def test_hentet_er_kl_22_15_i_oslo(self, mal):
        c = sqlite3.connect(mal)
        try:
            tider = {
                datetime.fromisoformat(h)
                for (h,) in c.execute("SELECT hentet FROM kursserie UNION SELECT hentet FROM indeksserie")
            }
        finally:
            c.close()
        ventet = datetime(2026, 10, 9, 22, 15, tzinfo=demo.OSLO)
        assert tider == {ventet}
        # Gjennomgangen, ECH4: hentingen i demoen er ogsaa etter grensen.
        import fetch_prices

        assert ventet.timetz().replace(tzinfo=None) >= fetch_prices.TIDSGRENSE

    def test_vurderingene_er_etter_tidsgrensen(self):
        """Klokka vurderingene skrives med, er etter grensen i hentingen, som
        en kveldshenting. Ville feilet med 21:30 igjen, eller med en tid foer
        grensen."""
        import fetch_prices

        oeyeblikk = demo._klokke_for(demo.SLUTTDATO)()
        assert oeyeblikk == datetime(2026, 10, 9, 22, 30, tzinfo=demo.OSLO)
        assert oeyeblikk.timetz().replace(tzinfo=None) >= fetch_prices.TIDSGRENSE


class TestLenkenTilDenEkteVersjonen:
    """Story 3.3i (U51): demolinja øverst lenker til «Den ekte versjonen» i
    README-en på GitHub. Den ekte versjonen har ingen slik lenke."""

    LENKEN = f'<a href="{app_modul.EKTE_VERSJONEN_URL}">Den ekte versjonen</a>'

    def test_lenken_staar_i_demoen(self, klient, monkeypatch, demobase):
        """Ville feilet hvis lenken manglet på en av sidene i demoen, sto
        utenfor stripa øverst, eller ikke sa at det trengs en nøkkel."""
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        for adresse in ("/", "/aksje/BRFE", "/min-liste"):
            html = klient.get(adresse).data.decode("utf-8")
            stripe = html.split('<header class="stripe">', 1)[1].split("</header>", 1)[0]
            assert self.LENKEN in stripe, adresse
            assert "gratis nøkkel fra EODHD" in stripe, adresse

    def test_lenken_gaar_til_ankeret_i_readme(self):
        """Ville feilet hvis adressen gikk til et annet repo enn README-en
        lenker til, eller til et anker README-en ikke har."""
        readme = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
        repo, anker = app_modul.EKTE_VERSJONEN_URL.split("#", 1)
        assert f"]({repo})" in readme
        assert f'<a name="{anker}"></a>' in readme

    def test_ingen_lenke_i_den_ekte_versjonen(self, klient):
        """Ville feilet hvis lenken sto også i den ekte versjonen (M1)."""
        aapne_base(Path(lagring_sqlite.BASE_STI)).close()
        for adresse in ("/", "/min-liste"):
            html = klient.get(adresse).data.decode("utf-8")
            assert "Eksempeltall" not in html, adresse
            assert app_modul.EKTE_VERSJONEN_URL not in html and "Den ekte versjonen" not in html, adresse
