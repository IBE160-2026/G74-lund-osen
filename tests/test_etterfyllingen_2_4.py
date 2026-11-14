"""Story 2.4: etterfylling av hull i kursserien (ekstravinduet 09.11).

Spesifikasjonen er spec-2-4-etterfylling-av-hull-i-kursserien.md. Hullet fylles ved neste
henting med de samme kallene som ellers (AD-5), og prøves bare på testbaser
under tmp_path (regel 22). Ingen nettkall (AD-8): hentefunksjonen er falsk,
og kursene er oppdiktet (regel 16). Fire dagers opphold med 16 kall står
alt i K9 i test_fetch_prices.py (2.1b); her er resten av kontrollen.
"""

import json
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256

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
        # Rettet 2026-11-14 (story 2.17, gruppens svar kl. 05:41-05:49): testen
        # gjelder kveldsradene. Dagene i hullet får signalet regnet i ettertid,
        # merket i basen, og det testes i tests/test_ettertid_2_17.py.
        raa, base = stier
        _kjoer(raa, base, MANDAG, _hent(MANDAG))
        _kjoer(raa, base, FREDAG, _hent(FREDAG))
        t = aapne_base(base)
        try:
            datoer = {d for (d,) in t.execute("SELECT DISTINCT dato FROM vurdering WHERE regnet = 'kveld'")}
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


LOERDAG_KL_12 = datetime(2026, 9, 26, 10, 0, tzinfo=timezone.utc)


def _uten_indeksen(siste: date, ellers=None):
    """En falsk henter der hovedindeksen feiler, og ellers som _hent."""
    ekte = ellers or _hent(siste)

    def hent(ticker, *resten):
        if ticker == HOVEDINDEKS.ticker:
            raise requests.ConnectionError("ConnectionError")
        return ekte(ticker, *resten)

    return hent


def _kjoering(raa, base, oeyeblikk: datetime, hent, les_kvote=nok_kvote) -> tuple[int, list[str], str]:
    """(kode, kallene, utskriften). Kode 0 når kjoer kom tilbake."""
    kall, linjer = [], []

    def tell(ticker, *resten):
        kall.append(ticker)
        return hent(ticker, *resten)

    try:
        fp.kjoer(raa, base, oeyeblikk, NOEKKEL, tell, linjer.append, les_kvote=les_kvote)
        kode = 0
    except SystemExit as slutt:
        kode = slutt.code
    return kode, kall, "\n".join(linjer)


def _indeksdatoer(base) -> set[date]:
    t = aapne_base(base)
    try:
        return {r.dato for r in SqliteIndekslager(t).serie(HOVEDINDEKS.symbol)}
    finally:
        t.close()


def _tabellene(base) -> tuple[list, list]:
    t = aapne_base(base)
    try:
        return (
            t.execute("SELECT * FROM kurs ORDER BY symbol, dato").fetchall(),
            t.execute("SELECT * FROM vurdering ORDER BY symbol, dato").fetchall(),
        )
    finally:
        t.close()


class TestHovedindeksenAlene:
    """Gruppens svar 10.11 kl. 15:30 (spørsmål 6): mangler bare hovedindeksen
    den siste børsdagen, henter en senere kjøring samme kveld eller i helgen
    den alene med ett kall, med kall som er igjen av dagens."""

    @staticmethod
    def _kvelden_uten_indeksen(stier, dag: date = FREDAG) -> None:
        raa, base = stier
        _kjoer(raa, base, MANDAG, _hent(MANDAG))
        kode, kall, _ = _kjoering(raa, base, _kl_22(dag), _uten_indeksen(dag))
        assert kode == fp.KODE_BARE_INDEKSEN and len(kall) == len(AKSJEUNIVERS) + 1
        assert dag not in _indeksdatoer(base)

    def test_en_senere_kjoering_samme_kveld_henter_den_med_ett_kall(self, stier):
        """Ville feilet hvis indeksen ikke ble hentet når bare den manglet,
        som før 10.11, eller kjøringen tok aksjene på nytt, skrev vurderinger
        eller rørte kursfila (AD-6)."""
        raa, base = stier
        self._kvelden_uten_indeksen(stier)
        kursfil = raa / fp.filnavn(FREDAG)
        foer, tabellene = sha256(kursfil.read_bytes()).hexdigest(), _tabellene(base)
        kode, kall, ut = _kjoering(raa, base, _kl_22(FREDAG) + timedelta(minutes=30), _hent(FREDAG))
        assert kode == 0 and kall == [HOVEDINDEKS.ticker]
        assert "mangler den dagen. Den hentes alene, med ett kall" in ut
        assert HULLET | {FREDAG} <= _indeksdatoer(base)
        assert sha256(kursfil.read_bytes()).hexdigest() == foer
        assert _tabellene(base) == tabellene
        bilde = json.loads((raa / f"forsoek2-raa-{FREDAG.isoformat()}.json").read_text(encoding="utf-8"))
        assert bilde["serier"] == {} and set(bilde["indeks"]["serier"]) == {HOVEDINDEKS.symbol}
        # Etterpå er det ingenting å hente.
        kode, kall, ut = _kjoering(raa, base, _kl_22(FREDAG) + timedelta(minutes=60), _hent(FREDAG))
        assert kode == 0 and kall == [] and "Ingenting å hente" in ut

    def test_i_helgen(self, stier):
        """Ville feilet hvis indeksen bare ble hentet på selve børsdagen."""
        raa, base = stier
        self._kvelden_uten_indeksen(stier)
        kode, kall, _ = _kjoering(raa, base, LOERDAG_KL_12, _hent(FREDAG))
        assert kode == 0 and kall == [HOVEDINDEKS.ticker]
        assert FREDAG in _indeksdatoer(base)

    def test_bonuskvoten_brukes_aldri(self, stier):
        """Ville feilet hvis indeksen alene ble hentet med bonuskvoten når
        dagens kall er brukt (NFR-01)."""
        raa, base = stier
        self._kvelden_uten_indeksen(stier)

        def brukt_opp(_noekkel):
            return {"apiRequests": 20, "apiRequestsDate": "2026-09-25", "dailyRateLimit": 20, "extraLimit": 463}

        kode, kall, ut = _kjoering(raa, base, _kl_22(FREDAG) + timedelta(minutes=30), _hent(FREDAG), brukt_opp)
        assert kode == fp.KODE_BARE_INDEKSEN and kall == []
        assert "hentes aldri med bonuskvoten" in ut and "0 kall brukt" in ut

    def test_kvoten_som_ikke_kan_leses_gir_0_kall(self, stier):
        """Ville feilet hvis indeksen ble hentet uten at kvoten var lest."""
        raa, base = stier
        self._kvelden_uten_indeksen(stier)

        def ulesbar(_noekkel):
            raise requests.ConnectionError("ConnectionError")

        kode, kall, _ = _kjoering(raa, base, _kl_22(FREDAG) + timedelta(minutes=30), _hent(FREDAG), ulesbar)
        assert kode == fp.KODE_BARE_INDEKSEN and kall == []

    def test_ikke_fra_kl_23_50(self, stier):
        """Ville feilet hvis indeksen ble hentet fra kl. 23:50 i Oslo, som et
        nytt forsøk ikke gjør (2.3b, svar 4)."""
        raa, base = stier
        self._kvelden_uten_indeksen(stier)
        kl_23_55 = datetime(2026, 9, 25, 21, 55, tzinfo=timezone.utc)
        kode, kall, ut = _kjoering(raa, base, kl_23_55, _hent(FREDAG))
        assert kode == fp.KODE_BARE_INDEKSEN and kall == [] and "23:50" in ut

    def test_feiler_den_igjen_gir_kode_3(self, stier):
        """Ville feilet hvis en indeks som feilet igjen, ga kode 0."""
        raa, base = stier
        self._kvelden_uten_indeksen(stier)
        kode, kall, _ = _kjoering(raa, base, _kl_22(FREDAG) + timedelta(minutes=30), _uten_indeksen(FREDAG))
        assert kode == fp.KODE_BARE_INDEKSEN and kall == [HOVEDINDEKS.ticker]
        assert FREDAG not in _indeksdatoer(base)

    def test_svaret_uten_dagen_gir_kode_3(self, stier):
        """Ville feilet hvis et svar uten børsdagen ble regnet som hentet."""
        raa, base = stier
        self._kvelden_uten_indeksen(stier)
        torsdag = FREDAG - timedelta(days=1)
        kode, kall, ut = _kjoering(raa, base, _kl_22(FREDAG) + timedelta(minutes=30), _hent(torsdag))
        assert kode == fp.KODE_BARE_INDEKSEN and kall == [HOVEDINDEKS.ticker]
        assert "Svaret har ikke hovedindeksen for børsdagen 2026-09-25" in ut

    def test_mangler_ogsaa_en_aksje_tar_forsoeket_bare_aksjen(self, stier):
        """Ville feilet hvis indeksen ble hentet før aksjene var på plass:
        forsøket for aksjen tar bare aksjen, og først kjøringen etter tar
        indeksen."""
        raa, base = stier
        _kjoer(raa, base, MANDAG, _hent(MANDAG))
        feilet = AKSJEUNIVERS[1]
        begge = TestNaarHentingenFeiler._feiler(feilet.ticker)
        kode, _, _ = _kjoering(raa, base, _kl_22(FREDAG), _uten_indeksen(FREDAG, begge))
        assert kode == 1
        kode, kall, _ = _kjoering(raa, base, _kl_22(FREDAG) + timedelta(minutes=30), _hent(FREDAG))
        assert kode == fp.KODE_BARE_INDEKSEN and kall == [feilet.ticker]
        kode, kall, _ = _kjoering(raa, base, _kl_22(FREDAG) + timedelta(minutes=60), _hent(FREDAG))
        assert kode == 0 and kall == [HOVEDINDEKS.ticker]


def _kvote(brukt: int, dato: str = "2026-09-25", bonus: int = 463):
    def les(_noekkel):
        return {"apiRequests": brukt, "apiRequestsDate": dato, "dailyRateLimit": 20, "extraLimit": bonus}

    return les


class TestHovedindeksenAleneEtterGjennomgangen:
    """Gjennomgangen 10.11 av svaret kl. 15:30 (Blind Hunter, Edge Case
    Hunter og Verification Gap)."""

    _kvelden_uten_indeksen = staticmethod(TestHovedindeksenAlene._kvelden_uten_indeksen)
    SENERE = _kl_22(FREDAG) + timedelta(minutes=30)

    def test_ett_kall_igjen_holder(self, stier):
        """BH12: ville feilet hvis det trengtes mer enn ett kall igjen av
        dagens (for eksempel igjen < 2)."""
        raa, base = stier
        self._kvelden_uten_indeksen(stier)
        kode, kall, _ = _kjoering(raa, base, self.SENERE, _hent(FREDAG), _kvote(19))
        assert kode == 0 and kall == [HOVEDINDEKS.ticker]

    def test_noekkelen_som_funksjon(self, stier):
        """VG1: main gir nøkkelen som en funksjon. Ville feilet hvis den ikke
        ble kalt før kvoten og kallet."""
        raa, base = stier
        self._kvelden_uten_indeksen(stier)
        sett = []

        def les(noekkel):
            sett.append(noekkel)
            return nok_kvote(noekkel)

        def hent(ticker, noekkel, *resten):
            sett.append(noekkel)
            return _hent(FREDAG)(ticker, noekkel, *resten)

        fp.kjoer(raa, base, self.SENERE, lambda: NOEKKEL, hent, lambda _: None, les_kvote=les)
        assert sett == [NOEKKEL, NOEKKEL]
        assert FREDAG in _indeksdatoer(base)

    def test_kvoten_fra_gaarsdagen_er_0_brukt_i_dag(self, stier):
        """VG2 og regel 15: lørdag står apiRequestsDate på fredag med 20
        brukt, og det er 0 brukt i dag i GMT. Ville feilet hvis datoen ikke
        ble regnet i GMT for dagen kjøringen gjelder."""
        raa, base = stier
        self._kvelden_uten_indeksen(stier)
        kode, kall, _ = _kjoering(raa, base, LOERDAG_KL_12, _hent(FREDAG), _kvote(20, "2026-09-25"))
        assert kode == 0 and kall == [HOVEDINDEKS.ticker]

    @pytest.mark.parametrize(
        "feilen",
        [
            requests.HTTPError("HTTP 401 Unauthorized"),
            requests.HTTPError("HTTP 500 Internal Server Error"),
            fp.UlesbarKvote("dailyRateLimit mangler"),
        ],
        ids=["401", "500", "ulesbar"],
    )
    def test_kvoten_som_ikke_kan_leses_gir_0_kall_og_ingen_krasj(self, stier, feilen):
        """VG5: ville feilet hvis en avvist nøkkel, en annen HTTP-feil eller et
        svar som ikke kan leses, ga et kall eller en krasj."""
        raa, base = stier
        self._kvelden_uten_indeksen(stier)

        def les(_noekkel):
            raise feilen

        kode, kall, ut = _kjoering(raa, base, self.SENERE, _hent(FREDAG), les)
        assert kode == fp.KODE_BARE_INDEKSEN and kall == [] and "0 kall brukt" in ut

    def test_raadet_foelger_grunnen(self, stier):
        """BH3: ville feilet hvis utskriften ba om en ny kjøring når klokka
        eller kvoten sa nei, eller ikke ba om den når kallet feilet."""
        raa, base = stier
        self._kvelden_uten_indeksen(stier)
        _, _, ut = _kjoering(raa, base, self.SENERE, _hent(FREDAG), _kvote(20))
        assert fp.VENT_PAA_INDEKSEN in ut and fp.PROEV_INDEKSEN_IGJEN not in ut
        _, _, ut = _kjoering(raa, base, self.SENERE, _uten_indeksen(FREDAG))
        assert fp.PROEV_INDEKSEN_IGJEN in ut and fp.VENT_PAA_INDEKSEN not in ut
        assert "i kveld" not in fp.PROEV_INDEKSEN_IGJEN + fp.VENT_PAA_INDEKSEN

    def test_ki_tekstene_etter_indeksen_ogsaa_naar_den_stopper(self, tmp_path, monkeypatch):
        """VG3 og ECH2: ville feilet hvis KI-tekstene ble laget før indeksen
        var hentet, eller ikke ble laget når nøkkelen mangler og hentingen av
        indeksen stopper kjøringen."""
        raa, base = tmp_path / "a" / "raa", tmp_path / "a" / "ose.db"
        self._kvelden_uten_indeksen((raa, base))
        kalt = []
        monkeypatch.setattr(fp, "lag_ki_tekster", lambda b, d, *_a, **_k: kalt.append(FREDAG in _indeksdatoer(b)))
        _kjoering(raa, base, self.SENERE, _hent(FREDAG))
        assert kalt == [True]

        def uten_noekkel():
            sys.exit("EODHD_API_KEY mangler")

        raa, base = tmp_path / "b" / "raa", tmp_path / "b" / "ose.db"
        self._kvelden_uten_indeksen((raa, base))
        kalt.clear()
        with pytest.raises(SystemExit):
            fp.kjoer(raa, base, self.SENERE, uten_noekkel, _hent(FREDAG), lambda _: None, les_kvote=nok_kvote)
        assert kalt == [False]

    def test_en_fil_som_ikke_kan_skrives_gir_kode_3(self, stier, monkeypatch):
        """ECH2: ville feilet hvis en OSError fra fila stoppet kjøringen med
        en krasj i stedet for kode 3."""
        raa, base = stier
        self._kvelden_uten_indeksen(stier)

        def feiler(*_a, **_k):
            raise PermissionError("nei")

        monkeypatch.setattr(fp, "forsoeksfil", feiler)
        kode, kall, ut = _kjoering(raa, base, self.SENERE, _hent(FREDAG))
        assert kode == fp.KODE_BARE_INDEKSEN and kall == [HOVEDINDEKS.ticker]
        assert "kunne ikke skrives" in ut

    def test_basen_som_feiler_gir_ikke_hentet(self, stier, monkeypatch):
        """VG4: ville feilet hvis hent_bare_indeksen sa at indeksen var hentet
        når basen ikke kunne skrives, også når basen har en eldre rad for
        dagen."""
        raa, base = stier
        _kjoer(raa, base, FREDAG, _hent(FREDAG))
        monkeypatch.setattr(fp, "skriv_indeksen_til_basen", lambda *_a, **_k: False)
        raad = fp.hent_bare_indeksen(
            raa,
            base,
            self.SENERE,
            FREDAG,
            FREDAG,
            NOEKKEL,
            _hent(FREDAG),
            lambda _: None,
            lambda: self.SENERE,
            nok_kvote,
        )
        assert raad == fp.PROEV_INDEKSEN_IGJEN

    def test_en_base_uten_tabellen_indeks(self, tmp_path):
        """VG6: ville feilet hvis en base uten tabellen indeks ga et kall for
        indeksen ved hver kjøring."""
        base = tmp_path / "gammel.db"
        t = sqlite3.connect(base)
        t.execute("CREATE TABLE kurs (symbol TEXT)")
        t.commit()
        t.close()
        assert fp.indeksen_mangler(base, FREDAG) is False
        assert fp.indeksen_mangler(tmp_path / "finnes-ikke.db", FREDAG) is False
