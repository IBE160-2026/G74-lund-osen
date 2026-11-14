"""Story 2.17: signalet regnet i ettertid for børsdager uten lagret vurdering.

Gruppens svar 2026-11-14 kl. 05:41-05:49 og tillegg 1 (kontrollisten). Hver
test sier hva den ville feilet på. Ingen nettverkskall (AD-8): hentingen får
en falsk henter, og kvoten en falsk /api/user.
"""

import re
import shutil
import sqlite3
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

import app as app_modul
import demo
import fetch_prices as fp
import lagring_sqlite
from boersdag import er_boersdag
from ettertid import fyll_i_ettertid, regn_i_ettertid
from kursdata import AKSJEUNIVERS, Kursrad
from lagring_sqlite import (
    MIGRASJONSKATALOG,
    SqliteEttertidslager,
    SqliteKurslager,
    SqliteVurderingslager,
    aapne_base,
)
from migrering import migrer
from signalberegning import nodvendige_dager, vurder
from test_fetch_prices import NOEKKEL, nok_kvote, serie_til
from test_ki_tekst import FalskModell
from tilstand import Art, tilstand
from vurderingsdata import Grunn, Vurdering, kveldsradene

OSLO = ZoneInfo("Europe/Oslo")
TIRSDAG = date(2026, 9, 22)
ONSDAG = date(2026, 9, 23)
TIRSDAG_KL_22 = datetime(2026, 9, 22, 20, 0, tzinfo=timezone.utc)
ONSDAG_KL_22 = datetime(2026, 9, 23, 20, 0, tzinfo=timezone.utc)


def _klokke(dag: date, time: int = 22, minutt: int = 30):
    oeyeblikk = datetime(dag.year, dag.month, dag.day, time, minutt, tzinfo=OSLO)
    return lambda: oeyeblikk


def _boersdager(fra: date, til: date) -> list[date]:
    dager, d = [], fra
    while d <= til:
        if er_boersdag(d):
            dager.append(d)
        d += timedelta(days=1)
    return dager


def _serie(dager: list[date]) -> list[Kursrad]:
    """En serie med variasjon, så sjekkene slår ut ulikt fra dag til dag."""
    return [
        Kursrad(dato=d, slutt=100 + (i * 7) % 13, justert_slutt=100 + (i * 7) % 13, volum=1000 + (i * 37) % 900)
        for i, d in enumerate(dager)
    ]


def _ny_base():
    t = sqlite3.connect(":memory:")
    migrer(t, MIGRASJONSKATALOG)
    return t


def _kolonner_foer_0014(t) -> list[str]:
    return [r[1] for r in t.execute("PRAGMA table_info(vurdering)") if r[1] != "regnet"]


def _kveldsradene(t) -> list[tuple]:
    k = _kolonner_foer_0014(t)
    return t.execute(f"SELECT {', '.join(k)} FROM vurdering WHERE regnet = 'kveld' ORDER BY symbol, dato").fetchall()


def _hent(siste: date, dager: int = 80):
    def hent(_ticker, *_):
        return serie_til(siste, dager=dager)

    return hent


def _kjoer(raa, base, oeyeblikk, hent, **kw):
    linjer, kall = [], []

    def tell(ticker, *a):
        kall.append(ticker)
        return hent(ticker, *a)

    kode = 0
    try:
        fp.kjoer(raa, base, oeyeblikk, NOEKKEL, tell, linjer.append, les_kvote=nok_kvote, **kw)
    except SystemExit as slutt:
        kode = slutt.code
    return kode, kall, "\n".join(linjer)


@pytest.fixture
def stier(tmp_path):
    return tmp_path / "raa", tmp_path / "db" / "ose.db"


class TestRegelen:
    """Steg 2 i instruksjonen: regelen i ettertid.py og lageret."""

    def test_likt_det_som_regnes_med_kursene_etter_dagen_fjernet(self):
        """Ville feilet hvis en dag ble regnet med kurser etter dagen (å se
        framover), eller med en annen regel enn kvelden."""
        dager = _boersdager(date(2026, 6, 1), date(2026, 9, 22))
        serie = _serie(dager)
        radene = regn_i_ettertid(serie, set(), date(2026, 9, 23))
        assert radene
        for dag, vurdering in radene:
            uten_etter = [r for r in serie if r.dato <= dag]
            assert vurdering == Vurdering(**{**vurder(uten_etter, dag).__dict__, "ettertid": True}), dag
            # Kursen etter dagen endret til noe helt annet gir samme rad.
            endret = uten_etter + [
                Kursrad(dato=r.dato, slutt=1.0, justert_slutt=1.0, volum=1) for r in serie if r.dato > dag
            ]
            assert dict(regn_i_ettertid(endret, set(), date(2026, 9, 23)))[dag] == vurdering

    def test_ingen_dag_uten_nok_kurser(self):
        """Ville feilet hvis en dag med færre kursdager enn kvelden krever
        (MINST_HANDELSDAGER), fikk en rad, eller den første med nok ikke fikk."""
        assert nodvendige_dager() == fp.MINST_HANDELSDAGER
        dager = _boersdager(date(2026, 6, 1), date(2026, 9, 22))
        radene = dict(regn_i_ettertid(_serie(dager), set(), date(2026, 9, 23)))
        assert dager[fp.MINST_HANDELSDAGER - 2] not in radene
        assert dager[fp.MINST_HANDELSDAGER - 1] in radene
        assert len(radene) == len(dager) - (fp.MINST_HANDELSDAGER - 1)

    def test_aldri_inneveerende_boersdag_eller_en_dag_med_rad(self):
        """Ville feilet hvis inneværende børsdag, en dag etter den, eller en
        dag som har en rad, ble regnet i ettertid."""
        dager = _boersdager(date(2026, 6, 1), date(2026, 9, 25))
        dagens = date(2026, 9, 23)
        har_rad = {date(2026, 9, 21)}
        radene = dict(regn_i_ettertid(_serie(dager), har_rad, dagens))
        assert max(radene) == date(2026, 9, 22)
        assert date(2026, 9, 21) not in radene and dagens not in radene

    def test_ingen_dag_foer_boerskalenderen(self):
        """Spørsmål 4: ville feilet hvis en dag i 2025 fikk en rad, eller
        regelen reiste UtenforKalenderen for den."""
        dager = [d for d in (date(2025, 9, 1) + timedelta(days=i) for i in range(160)) if d.weekday() < 5]
        radene = dict(regn_i_ettertid(_serie(dager), set(), date(2026, 3, 2)))
        assert radene and min(radene).year == 2026

    def test_bare_vurderinger_aldri_en_grunn(self):
        """Ville feilet hvis en dag der signalet ikke kunne regnes, fikk en
        rad med grunn i ettertid."""
        dager = _boersdager(date(2026, 6, 1), date(2026, 9, 22))
        serie = [Kursrad(dato=d, slutt=100.0, justert_slutt=100.0, volum=0) for d in dager]
        for _, vurdering in regn_i_ettertid(serie, set(), date(2026, 9, 23)):
            assert isinstance(vurdering, Vurdering) and vurdering.ettertid


class TestLageret:
    """Den egne veien: SqliteEttertidslager, og porten for kvelden."""

    def _med_kveldsrader(self):
        t = _ny_base()
        dager = _boersdager(date(2026, 6, 1), date(2026, 9, 22))
        serie = _serie(dager)
        SqliteKurslager(t).erstatt_serie("EQNR", serie, datetime(2026, 9, 22, 20, 15, tzinfo=timezone.utc))
        SqliteKurslager(t).erstatt_serie("DNB", serie, datetime(2026, 9, 22, 20, 15, tzinfo=timezone.utc))
        # To kveldsrader: en vurdering 21.09 og en grunn 18.09.
        SqliteVurderingslager(t, _klokke(date(2026, 9, 21))).skriv(
            "EQNR", date(2026, 9, 21), vurder(serie[:-1], date(2026, 9, 21))
        )
        SqliteVurderingslager(t, _klokke(date(2026, 9, 18))).skriv("EQNR", date(2026, 9, 18), Grunn.SYMBOL_FEILET)
        return t, serie

    def test_en_kveldsrad_ogsaa_med_grunn_overskrives_aldri(self):
        """Ville feilet hvis en rad fra kvelden, også en med grunn, ble skrevet
        over av en rad i ettertid."""
        t, _ = self._med_kveldsrader()
        foer = _kveldsradene(t)
        lager = SqliteEttertidslager(t, _klokke(date(2026, 9, 23)))
        fylt = fyll_i_ettertid(SqliteKurslager(t), lager, AKSJEUNIVERS, date(2026, 9, 23))
        assert fylt.antall > 0
        assert _kveldsradene(t) == foer
        les = SqliteVurderingslager(t, _klokke(date(2026, 9, 23)))
        assert les.les("EQNR", date(2026, 9, 18)) is Grunn.SYMBOL_FEILET
        # Rett mot lageret: en rad i ettertid for en dag med kveldsrad skrives ikke.
        rad = regn_i_ettertid(SqliteKurslager(t).serie("EQNR"), set(), date(2026, 9, 23))
        skrevet = lager.skriv("EQNR", [(d, v) for d, v in rad if d in (date(2026, 9, 18), date(2026, 9, 21))])
        assert skrevet == 0 and _kveldsradene(t) == foer

    def test_kveldsporten_ser_ikke_radene_i_ettertid(self):
        """Ville feilet hvis les eller les_periode uten med_ettertid ga en rad
        i ettertid (hentingen og KI-laget leser slik), eller med den ikke ga den."""
        t, _ = self._med_kveldsrader()
        fyll_i_ettertid(SqliteKurslager(t), SqliteEttertidslager(t, _klokke(ONSDAG)), AKSJEUNIVERS, ONSDAG)
        port = SqliteVurderingslager(t, _klokke(ONSDAG))
        assert port.les("EQNR", date(2026, 9, 17)) is None
        assert port.les("EQNR", date(2026, 9, 17), med_ettertid=True).ettertid
        kveld = port.les_periode("EQNR", date(2026, 9, 1), TIRSDAG)
        alle = port.les_periode("EQNR", date(2026, 9, 1), TIRSDAG, med_ettertid=True)
        assert set(kveld) == {date(2026, 9, 18), date(2026, 9, 21)}
        assert set(alle) > set(kveld) and kveldsradene(alle) == kveld

    def test_ny_utregning_og_sletting_roerer_bare_radene_i_ettertid(self):
        """Ville feilet hvis slett eller --regn-ettertid-paa-nytt slettet eller
        endret en kveldsrad."""
        t, _ = self._med_kveldsrader()
        lager = SqliteEttertidslager(t, _klokke(ONSDAG))
        fyll_i_ettertid(SqliteKurslager(t), lager, AKSJEUNIVERS, ONSDAG)
        foer, antall = _kveldsradene(t), lager.antall()
        assert lager.slett("DNB") > 0 and _kveldsradene(t) == foer
        assert lager.slett() > 0 and lager.antall() == 0 and _kveldsradene(t) == foer
        fyll_i_ettertid(SqliteKurslager(t), lager, AKSJEUNIVERS, ONSDAG)
        assert lager.antall() == antall and _kveldsradene(t) == foer

    def test_basen_avviser_at_en_kveldsrad_blir_en_rad_i_ettertid(self):
        """Ville feilet uten triggeren i 0014, eller med en rad i ettertid med grunn."""
        t, _ = self._med_kveldsrader()
        with pytest.raises(sqlite3.IntegrityError, match="kveldsrad"):
            t.execute("UPDATE vurdering SET regnet = 'ettertid' WHERE symbol = 'EQNR' AND dato = '2026-09-21'")
        with pytest.raises(sqlite3.IntegrityError):
            t.execute("UPDATE vurdering SET regnet = 'ettertid' WHERE grunn IS NOT NULL")
        with pytest.raises(sqlite3.IntegrityError):
            t.execute(
                "INSERT INTO vurdering (symbol, dato, grunn, regnet) VALUES ('DNB', '2026-09-10', 'symbol_feilet', 'ettertid')"
            )

    def test_lageret_avviser_inneveerende_boersdag_og_kveldsporten_avviser_ettertid(self):
        """Ville feilet hvis lageret for ettertid godtok inneværende børsdag,
        eller porten for kvelden godtok en vurdering merket ettertid."""
        t, serie = self._med_kveldsrader()
        rad = vurder(serie, TIRSDAG)
        i_ettertid = Vurdering(**{**rad.__dict__, "ettertid": True})
        with pytest.raises(ValueError, match="foer inneveerende boersdag"):
            SqliteEttertidslager(t, _klokke(TIRSDAG)).skriv("DNB", [(TIRSDAG, i_ettertid)])
        with pytest.raises(TypeError):
            SqliteEttertidslager(t, _klokke(ONSDAG)).skriv("DNB", [(TIRSDAG, rad)])
        with pytest.raises(TypeError):
            SqliteVurderingslager(t, _klokke(TIRSDAG)).skriv("DNB", TIRSDAG, i_ettertid)

    def test_tilstanden_er_en_egen(self):
        """Ville feilet hvis en rad i ettertid fikk samme tilstand som en
        kveldsrad, eller mistet signalet."""
        t, serie = self._med_kveldsrader()
        rad = vurder(serie, TIRSDAG)
        utfall = tilstand(Vurdering(**{**rad.__dict__, "ettertid": True}), TIRSDAG, ONSDAG)
        assert utfall.art is Art.ETTERTID and utfall.ettertid and utfall.vurdering is not None
        assert tilstand(rad, TIRSDAG, ONSDAG).art is Art.SVAR


class TestHentingen:
    """Til slutt i hver henting, og kommandoene."""

    def test_hentingen_regner_dagene_foer_og_aksjer_utenfor_lista_roeres_ikke(self, stier):
        """Ville feilet hvis hentingen ikke regnet dagene før i ettertid, regnet
        inneværende børsdag, eller ga en aksje utenfor lista en rad."""
        raa, base = stier
        kode, kall, ut = _kjoer(raa, base, TIRSDAG_KL_22, _hent(TIRSDAG))
        assert kode == 0 and len(kall) == len(AKSJEUNIVERS) + 1
        t = aapne_base(base)
        try:
            # DNB tas ut av lista før neste henting, og har kurser som ikke er vurdert.
            t.execute("DELETE FROM vurdering WHERE symbol = 'DNB' AND regnet = 'ettertid'")
            t.execute("UPDATE aksje SET ut = '2026-09-23' WHERE symbol = 'DNB'")
            t.commit()
            ettertid = t.execute("SELECT DISTINCT dato FROM vurdering WHERE regnet = 'ettertid'").fetchall()
        finally:
            t.close()
        assert ettertid and max(d for (d,) in ettertid) < TIRSDAG.isoformat()
        assert "Signalet er regnet i ettertid for" in ut
        _kjoer(raa, base, ONSDAG_KL_22, _hent(ONSDAG))
        t = aapne_base(base)
        try:
            dnb = t.execute("SELECT count(*) FROM vurdering WHERE symbol = 'DNB' AND regnet = 'ettertid'").fetchone()[0]
            onsdag = t.execute(
                "SELECT count(*) FROM vurdering WHERE dato = ? AND regnet = 'ettertid'", (ONSDAG.isoformat(),)
            ).fetchone()[0]
        finally:
            t.close()
        assert dnb == 0 and onsdag == 0

    def test_ingen_nettverkskall_og_samme_kall_som_foer(self, stier):
        """Ville feilet hvis steget i ettertid gjorde et kall, eller en henting
        der basen alt har dagen brukte et kall."""
        raa, base = stier
        _kjoer(raa, base, TIRSDAG_KL_22, _hent(TIRSDAG))
        t = aapne_base(base)
        try:
            t.execute("DELETE FROM vurdering WHERE regnet = 'ettertid'")
            t.commit()
        finally:
            t.close()

        def ingen_kall(*_):
            pytest.fail("ingen kall")

        kode, kall, ut = _kjoer(raa, base, TIRSDAG_KL_22 + timedelta(minutes=30), ingen_kall)
        assert kode == 0 and kall == []
        assert "Signalet er regnet i ettertid for" in ut

    def test_en_feil_stopper_ikke_kvelden_og_utskriften_har_ingen_kurser(self, stier, monkeypatch):
        """Ville feilet hvis en feil i ettertid endret utgangskoden, stoppet
        kveldens rader eller skrev en kurs eller en melding med tall ut."""
        raa, base = stier
        import ettertid as ettertid_modul

        def feiler(*_a, **_k):
            raise ValueError("slutt maa vaere et endelig tall over null, fikk 123.45")

        monkeypatch.setattr(fp, "fyll_i_ettertid", feiler)
        kode, kall, ut = _kjoer(raa, base, TIRSDAG_KL_22, _hent(TIRSDAG))
        assert ettertid_modul.fyll_i_ettertid is not feiler
        assert kode == 0 and len(kall) == len(AKSJEUNIVERS) + 1
        assert "Signalet i ettertid kunne ikke regnes (ValueError)" in ut
        assert "123" not in ut.split("Signalet i ettertid", 1)[1]
        t = aapne_base(base)
        try:
            assert t.execute(
                "SELECT count(*) FROM vurdering WHERE dato = ? AND regnet = 'kveld'", (TIRSDAG.isoformat(),)
            ).fetchone()[0] == len(AKSJEUNIVERS)
        finally:
            t.close()

    def test_kommandoene_roerer_bare_radene_i_ettertid(self, stier, monkeypatch):
        """Ville feilet hvis --slett-ettertid eller --regn-ettertid-paa-nytt
        endret en kveldsrad, gjorde et kall eller leste nøkkelen."""
        raa, base = stier
        _kjoer(raa, base, TIRSDAG_KL_22, _hent(TIRSDAG))
        monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
        monkeypatch.setattr(fp, "naa", lambda: datetime(2026, 9, 23, 10, 0, tzinfo=timezone.utc))
        monkeypatch.setattr(fp, "hent_api_nokkel", lambda: pytest.fail("nøkkelen leses ikke"))
        t = aapne_base(base)
        try:
            foer = _kveldsradene(t)
            antall = t.execute("SELECT count(*) FROM vurdering WHERE regnet = 'ettertid'").fetchone()[0]
        finally:
            t.close()
        for flagg, ventet in (("--slett-ettertid", 0), ("--regn-ettertid-paa-nytt", antall)):
            with pytest.raises(SystemExit) as slutt:
                fp.main([flagg])
            assert slutt.value.code == 0
            t = aapne_base(base)
            try:
                assert t.execute("SELECT count(*) FROM vurdering WHERE regnet = 'ettertid'").fetchone()[0] == ventet
                assert _kveldsradene(t) == foer
            finally:
                t.close()

    def test_kommandoene_nekter_en_demobase_og_andre_valg(self, tmp_path, monkeypatch, capsys):
        """Ville feilet hvis kommandoen rørte en demobase, eller kunne kombineres
        med --les-inn."""
        sti = tmp_path / "db" / "ose.db"
        sti.parent.mkdir(parents=True)
        demo.lag_demobase(sti, skriv=lambda _: None, med_ki=False)
        monkeypatch.setattr(lagring_sqlite, "BASE_STI", sti)
        foer = sti.read_bytes()
        with pytest.raises(SystemExit) as slutt:
            fp.main(["--slett-ettertid"])
        assert slutt.value.code == 1 and sti.read_bytes() == foer
        with pytest.raises(SystemExit) as slutt:
            fp.main(["--slett-ettertid", "--les-inn", "x.json"])
        assert slutt.value.code == 2


class TestKIGrunnlaget:
    """Svaret kl. 05:49: KI-grunnlaget leser bare kveldsradene."""

    class Opptak(FalskModell):
        def __init__(self):
            super().__init__()
            self.promptene = []

        def lag_tekst(self, prompt):
            self.promptene.append(prompt)
            return super().lag_tekst(prompt)

    def _promptene(self, tmp_path, navn, monkeypatch, med_ettertid: bool):
        raa, base = tmp_path / navn / "raa", tmp_path / navn / "db" / "ose.db"
        if not med_ettertid:
            monkeypatch.setattr(fp, "regn_signalet_i_ettertid", lambda *a, **k: None)
        _kjoer(raa, base, TIRSDAG_KL_22, _hent(TIRSDAG), modell=FalskModell())
        monkeypatch.undo()
        opptak = self.Opptak()
        _kjoer(raa, base, ONSDAG_KL_22, _hent(ONSDAG), modell=opptak)
        t = aapne_base(base)
        try:
            ettertid = t.execute("SELECT count(*) FROM vurdering WHERE regnet = 'ettertid'").fetchone()[0]
            ki_datoer = {d for (d,) in t.execute("SELECT DISTINCT dato FROM ki_logg")}
        finally:
            t.close()
        return opptak.promptene, ettertid, ki_datoer

    def test_promptene_er_like_med_og_uten_radene_i_ettertid(self, tmp_path, monkeypatch):
        """Ville feilet hvis grunnlaget for KI-teksten (dagene, mønstrene,
        dagsbildet eller teksten om dagen) leste en rad i ettertid, eller en
        rad i ettertid fikk en KI-tekst."""
        uten, _, _ = self._promptene(tmp_path, "uten", monkeypatch, med_ettertid=False)
        med, antall, ki_datoer = self._promptene(tmp_path, "med", monkeypatch, med_ettertid=True)
        assert antall > 0 and med and med == uten
        assert ki_datoer == {TIRSDAG.isoformat(), ONSDAG.isoformat()}


class TestMigrasjonen:
    def test_paa_en_kopi_av_en_gammel_base_og_paa_en_ny(self, tmp_path):
        """Ville feilet hvis 0014 endret en kveldsrad, ikke ga dem «kveld»,
        eller ikke virket på en ny base."""
        gammel = tmp_path / "gammel.db"
        katalog = tmp_path / "migrasjoner"
        katalog.mkdir()
        for fil in sorted(MIGRASJONSKATALOG.glob("*.sql")):
            if not fil.name.startswith("0014"):
                shutil.copy(fil, katalog / fil.name)
        t = sqlite3.connect(gammel)
        assert migrer(t, katalog) == 13
        t.execute(
            "INSERT INTO vurdering (symbol, dato, styrke, retning, trend, bevegelse, interesse, slutt, justert_slutt, "
            "trend_avvik, dagens_endring, standardavvik, volumforhold) VALUES "
            "('EQNR', '2026-09-22', 1, 'Positiv', 1, 0, 0, 300.0, 290.0, 0.035, 0.001, 0.012, 1.2)"
        )
        t.execute("INSERT INTO vurdering (symbol, dato, grunn) VALUES ('DNB', '2026-09-22', 'symbol_feilet')")
        t.commit()
        foer = t.execute("SELECT * FROM vurdering ORDER BY symbol").fetchall()
        t.close()
        kopi = tmp_path / "kopi.db"
        shutil.copy(gammel, kopi)
        t = sqlite3.connect(kopi)
        assert migrer(t, MIGRASJONSKATALOG) == 14
        assert _kveldsradene(t) == [r for r in foer]
        assert {r for (r,) in t.execute("SELECT regnet FROM vurdering")} == {"kveld"}
        t.close()
        ny = _ny_base()
        assert "regnet" in [r[1] for r in ny.execute("PRAGMA table_info(vurdering)")]


def _side(klient, adresse: str) -> str:
    svar = klient.get(adresse)
    assert svar.status_code == 200, adresse
    return svar.get_data(as_text=True)


def _synlig(html: str) -> str:
    html = re.sub(r"<(style|script|template)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


@pytest.fixture
def ekte(stier, monkeypatch):
    """Den ekte versjonen med én henting 22.09: kveldsrader 22.09, og
    signalet i ettertid for dagene før med nok kurser."""
    raa, base = stier
    _kjoer(raa, base, TIRSDAG_KL_22, _hent(TIRSDAG))
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    monkeypatch.delenv(app_modul.I_DEMO, raising=False)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc))
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


@pytest.fixture
def demoen(tmp_path, monkeypatch):
    """Demoen, med demobasen der webserveren leter."""
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", tmp_path / "db" / "ose.db")
    sti = lagring_sqlite.demo_sti()
    sti.parent.mkdir(parents=True, exist_ok=True)
    demo.lag_demobase(sti, skriv=lambda _: None)
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


VERSJONENE = pytest.mark.parametrize(
    "hvilken, symbol, dag, maaned",
    [("ekte", "EQNR", "2026-09-21", "2026-09"), ("demoen", "KVST", "2026-09-18", "2026-09")],
)


class TestVisningen:
    """Steg 3 i instruksjonen, i begge versjonene."""

    @VERSJONENE
    def test_signalet_dag_for_dag_merker_dagen_og_teller_dem(self, request, hvilken, symbol, dag, maaned):
        """Ville feilet hvis en dag i ettertid manglet stiplet kant eller
        teksten «i ettertid», en kveldsdag fikk merket, eller uka og måneden
        ikke sa hvor mange som er i ettertid."""
        klient = request.getfixturevalue(hvilken)
        html = _side(klient, f"/aksje/{symbol}?maaned={maaned}")
        historikken = html.split('id="signalet-dag-for-dag"', 1)[1].split("</section>", 1)[0]
        dagene = re.findall(r'<li class="dag([^"]*)">(.*?)</li>', historikken, flags=re.DOTALL)
        merket = [(k, innhold) for k, innhold in dagene if "ettertid" in k]
        assert merket
        for klasser, innhold in dagene:
            har_merket = '<span class="ettertid-merke">i ettertid</span>' in innhold
            assert ("ettertid" in klasser.split()) == har_merket, innhold
        assert re.search(r"\d+ av \d+ dag(er)? skilte seg ut, \d+ i ettertid", _synlig(historikken))
        assert re.search(r"skilte seg ut \d+ av \d+ børsdager, \d+ i ettertid\.", _synlig(historikken))

    @VERSJONENE
    def test_aksjesiden_for_dagen_sier_det_under_datoen_og_om_ki_teksten(self, request, hvilken, symbol, dag, maaned):
        """Ville feilet hvis siden for en dag i ettertid ikke sa det under
        datoen, «Signalet forklart» ikke sa at KI-teksten bare lages samme
        kveld, eller setningen om dagene sto."""
        klient = request.getfixturevalue(hvilken)
        html = _side(klient, f"/aksje/{symbol}?dag={dag}")
        assert '<p class="ettertid-linje" role="note">' in html
        meta = html.split('<p class="meta">', 1)[1]
        assert meta.index("ettertid-linje") < meta.index("noekkeltallene")
        ki = html.split('id="ki-tittel"', 1)[1].split("</section>", 1)[0]
        assert "KI-teksten lages bare samme kveld som kursene hentes" in _synlig(ki)
        assert '<p class="dagene">' not in ki and '<p class="ki-tekst">' not in ki

    @VERSJONENE
    def test_grafen_boersometeret_og_oversikten_merker_dagen(self, request, hvilken, symbol, dag, maaned):
        """Ville feilet hvis grafen, børsometeret eller oversikten for en
        tidligere dag med signalet regnet i ettertid viste signalet uten merket."""
        klient = request.getfixturevalue(hvilken)
        html = _side(klient, f"/aksje/{symbol}?dag={dag}")
        figuren = html.split("<figure>", 1)[1].split("</figure>", 1)[0]
        if 'class="signaldag' in figuren:
            assert re.search(r'class="signaldag [a-z]+( alle)? ettertid"', figuren)
            assert "i ettertid" in _synlig(figuren)
        oversikten = _side(klient, f"/?periode=velg&dag={dag}")
        assert '<span class="ettertid-merke">i ettertid</span>' in oversikten
        boersometeret = _side(klient, f"/boersometer?periode=velg&dag={dag}")
        assert re.search(r'class="rute [^"]*ettertid', boersometeret)
        tabellen = boersometeret.split("<table", 1)[1]
        assert '<span class="ettertid-merke">i ettertid</span>' in tabellen

    def test_en_kveldsdag_har_ikke_merket(self, ekte):
        """Ville feilet hvis siste børsdag, en kveldsrad, fikk merket."""
        html = _side(ekte, "/aksje/EQNR")
        assert "ettertid-linje" not in html
        assert "ettertid-merke" not in _side(ekte, "/").split("<tbody", 1)[1].split("</tbody>", 1)[0]

    def test_stilen_kanten_kontrasten_og_hoey_kontrast(self):
        """Ville feilet hvis kanten var under 3:1 mot bakgrunnen, regelen for
        forced-colors manglet, eller merket bare var en kant uten tekst."""
        stil = (app_modul.STILARK).read_text(encoding="utf-8")
        assert re.search(r"\.ettertid-merke \{[^}]*border: 1\.5px dashed var\(--dempet-2\)", stil)
        assert re.search(r"li\.dag\.ettertid \{ border: 1\.5px dashed var\(--dempet-2\)", stil)
        tvunget = re.findall(r"@media \(forced-colors: active\) \{(.*?)\n\}", stil, flags=re.DOTALL)
        assert any(".ettertid-merke { border-color: CanvasText; }" in d for d in tvunget)

        def lyshet(h):
            c = [int(h[i : i + 2], 16) / 255 for i in (1, 3, 5)]
            c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
            return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

        farge = re.search(r"--dempet-2:\s*(#[0-9A-Fa-f]{6})", stil).group(1)
        bakgrunn = re.search(r"--bakgrunn:\s*(#[0-9A-Fa-f]{6})", stil).group(1)
        a, b = sorted((lyshet(farge), lyshet(bakgrunn)), reverse=True)
        assert (a + 0.05) / (b + 0.05) >= 3
        brikker = app_modul.app.root_path + "/templates/_brikker.html"
        assert '<span class="ettertid-merke">i ettertid</span>' in open(brikker, encoding="utf-8").read()


class TestDemoen:
    def test_radene_foer_startdagen_og_ingen_kveldsrad_eller_ki_tekst_endret(self, tmp_path):
        """Ville feilet hvis demoen ikke fikk radene før startdagen, fikk en
        rad i ettertid fra startdagen, eller en kveldsrad eller KI-rad endret seg."""
        sti = tmp_path / "demo.db"
        demo.lag_demobase(sti, skriv=lambda _: None)
        t = sqlite3.connect(sti)
        try:
            foerste, siste = t.execute(
                "SELECT min(dato), max(dato) FROM vurdering WHERE regnet = 'ettertid'"
            ).fetchone()
            kveld_foer = t.execute(
                "SELECT count(*) FROM vurdering WHERE regnet = 'kveld' AND dato < ?", (demo.STARTDAG.isoformat(),)
            ).fetchone()[0]
            ki = t.execute("SELECT DISTINCT dato FROM ki_logg").fetchall()
        finally:
            t.close()
        assert foerste and siste < demo.STARTDAG.isoformat() and kveld_foer == 0
        assert ki == [(demo.SLUTTDATO.isoformat(),)]
        assert not demo.gammel_demobase(sqlite3.connect(sti))
