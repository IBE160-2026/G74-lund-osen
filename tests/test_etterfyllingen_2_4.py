"""Story 2.4: etterfylling av hull i kursserien (ekstravinduet 09.11).

Spesifikasjonen er spec-2-4-etterfylling-av-hull-i-kursserien.md. Hullet fylles ved neste
henting med de samme kallene som ellers (AD-5), og prøves bare på testbaser
under tmp_path (regel 22). Ingen nettkall (AD-8): hentefunksjonen er falsk,
og kursene er oppdiktet (regel 16). Fire dagers opphold med 16 kall står
alt i K9 i test_fetch_prices.py (2.1b); her er resten av kontrollen.
"""

from datetime import date, datetime, timedelta, timezone

import pytest
import requests

import fetch_prices as fp
from indeksdata import HOVEDINDEKS
from kursdata import AKSJEUNIVERS
from lagring_sqlite import SqliteIndekslager, SqliteKurslager, SqliteVurderingslager, aapne_base
from test_fetch_prices import NOEKKEL, nok_kvote, serie_til
from vurderingsdata import Grunn

MANDAG = date(2026, 9, 21)
TIRSDAG = date(2026, 9, 22)
FREDAG = date(2026, 9, 25)
HULLET = {date(2026, 9, d) for d in (22, 23, 24)}


def _kl_22(dag: date) -> datetime:
    """Kl. 22:00 i Oslo om sommeren, i UTC."""
    return datetime(dag.year, dag.month, dag.day, 20, 0, tzinfo=timezone.utc)


@pytest.fixture
def stier(tmp_path):
    return tmp_path / "data" / "raa", tmp_path / "data" / "db" / "ose.db"


def _hent(siste: date, kall: list | None = None, endret: bool = False):
    """En falsk henter. Med endret har kildene justert de eldre kursene (for
    eksempel for et utbytte) og har ikke lenger den eldste dagen."""

    def hent(ticker, _noekkel, fra, til):
        if kall is not None:
            kall.append((ticker, fra, til))
        serie = serie_til(siste, dager=64)
        if endret:
            serie = [{**rad, "adjusted_close": rad["adjusted_close"] - 1.0} for rad in serie[1:]]
        return serie

    return hent


def _kjoer(raa, base, dag: date, hent) -> None:
    fp.kjoer(raa, base, _kl_22(dag), NOEKKEL, hent, lambda _: None, les_kvote=nok_kvote)


class TestSerienByttesIHelhet:
    """Serien erstattes i sin helhet ved neste henting, den skjøtes ikke."""

    def test_eldre_rader_er_kildens_nye(self, stier):
        """Ville feilet hvis hentingen bare la til dagene som manglet: da sto
        de gamle justerte kursene og den eldste dagen igjen etter hullet."""
        raa, base = stier
        _kjoer(raa, base, MANDAG, _hent(MANDAG))
        _kjoer(raa, base, FREDAG, _hent(FREDAG, endret=True))
        ventet = serie_til(FREDAG, dager=64)[1:]
        t = aapne_base(base)
        try:
            lager = SqliteKurslager(t)
            for aksje in AKSJEUNIVERS:
                serie = lager.serie(aksje.symbol)
                assert [r.dato.isoformat() for r in serie] == [r["date"] for r in ventet], aksje.symbol
                assert [r.justert_slutt for r in serie] == [r["adjusted_close"] - 1.0 for r in ventet]
        finally:
            t.close()

    def test_hullet_i_hovedindeksen_fylles_ogsaa(self, stier):
        """Ville feilet hvis bare aksjene ble fylt, og hovedindeksen sto med
        hullet, så grafen og søylene manglet indeksen de dagene, eller
        indeksserien ble skjøtet og ikke byttet (gjennomgangen, BH5, VG1)."""
        raa, base = stier
        _kjoer(raa, base, MANDAG, _hent(MANDAG))
        _kjoer(raa, base, FREDAG, _hent(FREDAG, endret=True))
        ventet = {date.fromisoformat(r["date"]): r["adjusted_close"] - 1.0 for r in serie_til(FREDAG, dager=64)[1:]}
        t = aapne_base(base)
        try:
            serie = SqliteIndekslager(t).serie(HOVEDINDEKS.symbol)
        finally:
            t.close()
        assert HULLET | {FREDAG} <= {r.dato for r in serie}
        # Bare kildens nye rader: ingen eldre dag og ingen gammel justert kurs.
        assert all(ventet.get(r.dato) == r.justert_slutt for r in serie), serie[:3]

    def test_en_uke_med_helgen(self, stier):
        """Gjennomgangen (BH4): ville feilet hvis en hel uke borte, over en
        helg, ikke ble fylt av den første hentingen etter."""
        raa, base = stier
        forrige_mandag = MANDAG - timedelta(days=7)
        _kjoer(raa, base, forrige_mandag, _hent(forrige_mandag))
        _kjoer(raa, base, MANDAG, _hent(MANDAG))
        uka = {forrige_mandag + timedelta(days=d) for d in range(1, 5)} | {MANDAG}
        t = aapne_base(base)
        try:
            lager = SqliteKurslager(t)
            for aksje in AKSJEUNIVERS:
                assert uka <= {r.dato for r in lager.serie(aksje.symbol)}, aksje.symbol
        finally:
            t.close()


class TestNaarHentingenFeiler:
    """Gjennomgangen (ECH1, ECH2, VG2): det som feiler i hentingen etter
    hullet, står med hullet, som hjelpen sier."""

    @staticmethod
    def _feiler(ticker_som_feiler):
        ekte = _hent(FREDAG)

        def hent(ticker, *resten):
            if ticker == ticker_som_feiler:
                raise requests.ConnectionError("ConnectionError")
            return ekte(ticker, *resten)

        return hent

    def test_en_aksje_som_feiler_staar_med_hullet(self, stier):
        """Ville feilet hvis en aksje som feilet, fikk serien sin rørt, eller
        de andre ikke ble fylt fordi én feilet (AD-15)."""
        raa, base = stier
        _kjoer(raa, base, MANDAG, _hent(MANDAG))
        feilet = AKSJEUNIVERS[1]
        with pytest.raises(SystemExit) as slutt:
            _kjoer(raa, base, FREDAG, self._feiler(feilet.ticker))
        assert slutt.value.code == 1
        t = aapne_base(base)
        try:
            lager = SqliteKurslager(t)
            assert not HULLET & {r.dato for r in lager.serie(feilet.symbol)}
            for aksje in AKSJEUNIVERS:
                if aksje is not feilet:
                    assert HULLET <= {r.dato for r in lager.serie(aksje.symbol)}, aksje.symbol
        finally:
            t.close()

    def test_hovedindeksen_som_feiler_staar_med_hullet(self, stier):
        """Ville feilet hvis hovedindeksen ble fylt uten å være hentet, eller
        aksjene ikke ble fylt fordi indeksen feilet."""
        raa, base = stier
        _kjoer(raa, base, MANDAG, _hent(MANDAG))
        with pytest.raises(SystemExit) as slutt:
            _kjoer(raa, base, FREDAG, self._feiler(HOVEDINDEKS.ticker))
        assert slutt.value.code == fp.KODE_BARE_INDEKSEN
        t = aapne_base(base)
        try:
            assert not HULLET & {r.dato for r in SqliteIndekslager(t).serie(HOVEDINDEKS.symbol)}
            assert HULLET <= {r.dato for r in SqliteKurslager(t).serie(AKSJEUNIVERS[0].symbol)}
        finally:
            t.close()


class TestDeSammeKallene:
    """Etterfyllingen koster de samme kallene som en vanlig kveld."""

    def test_samme_kall_etter_et_hull_som_dagen_etter(self, tmp_path):
        """Ville feilet hvis hullet ble hentet med ett kall per dag som
        manglet, eller med et annet intervall enn en vanlig kveld."""
        vanlig, etter_hullet = [], []
        for navn, dag, kall in (("vanlig", TIRSDAG, vanlig), ("hull", FREDAG, etter_hullet)):
            raa, base = tmp_path / navn / "raa", tmp_path / navn / "db" / "ose.db"
            _kjoer(raa, base, MANDAG, _hent(MANDAG))
            _kjoer(raa, base, dag, _hent(dag, kall))
        assert len(vanlig) == len(etter_hullet) == len(AKSJEUNIVERS) + 1
        assert [k[0] for k in vanlig] == [k[0] for k in etter_hullet]
        # Intervallet er et år til dagen, for begge (DAGER_TILBAKE).
        assert {k[1:] for k in etter_hullet} == {
            ((FREDAG - timedelta(days=fp.DAGER_TILBAKE)).isoformat(), FREDAG.isoformat())
        }
        assert {k[1:] for k in vanlig} == {
            ((TIRSDAG - timedelta(days=fp.DAGER_TILBAKE)).isoformat(), TIRSDAG.isoformat())
        }


class TestIngenVurderingerEtterfylles:
    """Kurser kan etterfylles, vurderinger kan ikke (AD-7)."""

    def test_bare_kveldens_vurdering_skrives(self, stier):
        """Ville feilet hvis hentingen etter hullet skrev vurderinger for
        dagene i hullet: de ville vært regnet av en serie som ikke fantes
        de kveldene."""
        raa, base = stier
        _kjoer(raa, base, MANDAG, _hent(MANDAG))
        _kjoer(raa, base, FREDAG, _hent(FREDAG))
        t = aapne_base(base)
        try:
            datoer = {d for (d,) in t.execute("SELECT DISTINCT dato FROM vurdering")}
        finally:
            t.close()
        assert datoer == {MANDAG.isoformat(), FREDAG.isoformat()}

    def test_ad7_stopper_et_forsoek_paa_aa_etterfylle(self, stier):
        """Ville feilet hvis noen kunne etterfylle en vurdering for en dag i
        hullet: lageret godtar bare inneværende børsdag (AD-7)."""
        raa, base = stier
        _kjoer(raa, base, MANDAG, _hent(MANDAG))
        _kjoer(raa, base, FREDAG, _hent(FREDAG))
        t = aapne_base(base)
        try:
            lager = SqliteVurderingslager(t, lambda: _kl_22(FREDAG))
            for dag in sorted(HULLET):
                with pytest.raises(ValueError, match="ikke inneveerende boersdag"):
                    lager.skriv(AKSJEUNIVERS[0].symbol, dag, Grunn.SIGNAL_IKKE_REGNET)
                assert lager.les(AKSJEUNIVERS[0].symbol, dag) is None
        finally:
            t.close()
