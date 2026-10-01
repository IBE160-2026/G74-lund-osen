"""Vurderingslageret - story 1.6, FR-408, AD-7, AD-18, punkt 24 i prd.md §8.

Porten og SQLite-adapteren proeves sammen. Det finnes med vilje ikke noe
minnelager: reglene for overskriving skal staa ett sted, i upserten, og
testene bruker SQLite i minnet (spesifikasjonen, Beslutninger).

Klokka injiseres, saa ingen test avhenger av dagen den kjoeres. Hver test
lager sin egen base, i minnet eller under tmp_path. Ingen nett (AD-8).
"""

import dataclasses
import itertools
import math
import sqlite3
from datetime import date, datetime, timedelta, timezone

import pytest

import signalberegning
from boersdag import UtenforKalenderen
from kursdata import Kursrad
from lagring_sqlite import (
    MIGRASJONSKATALOG,
    VURDERINGSKOLONNER,
    SqliteKurslager,
    SqliteVurderingslager,
)
from migrering import migrer, versjon
from vurderingsdata import (
    RETNINGER,
    Grunn,
    UgyldigVurdering,
    Vurdering,
    Vurderingslager,
)

VURDERINGSFELT = (
    "styrke", "retning", "trend", "bevegelse", "interesse", "slutt", "justert_slutt",
)

# Story 2.1c, 0004. volumforhold kan mangle naar interesse er 0, de tre andre
# aldri i en vurdering.
MAALINGER = ("trend_avvik", "dagens_endring", "standardavvik", "volumforhold")
PAAKREVDE_MAALINGER = ("trend_avvik", "dagens_endring", "standardavvik")

# Torsdag 24.09.2026 kl. 22:30 UTC er fredag 25.09 kl. 00:30 i Oslo (sommertid).
SOMMER_0030 = "2026-09-24T22:30:00+00:00"
# Torsdag 10.12.2026 kl. 23:30 UTC er fredag 11.12 kl. 00:30 i Oslo (vintertid).
VINTER_0030 = "2026-12-10T23:30:00+00:00"
# Onsdag 23.09.2026 midt paa dagen.
ONSDAG = "2026-09-23T10:00:00+00:00"


def klokke(tidspunkt: str):
    oeyeblikk = datetime.fromisoformat(tidspunkt)
    return lambda: oeyeblikk


def vurdering(**endret) -> Vurdering:
    felt = dict(styrke=2, retning="Positiv", trend=1, bevegelse=1, interesse=0,
                slutt=300.0, justert_slutt=290.0, trend_avvik=0.035,
                dagens_endring=0.021, standardavvik=0.012, volumforhold=1.2)
    felt.update(endret)
    return Vurdering(**felt)


def rader(tilkobling) -> list[tuple]:
    return tilkobling.execute(
        "SELECT symbol, dato, styrke, grunn FROM vurdering ORDER BY symbol, dato"
    ).fetchall()


@pytest.fixture
def tilkobling():
    tilkobling = sqlite3.connect(":memory:")
    migrer(tilkobling, MIGRASJONSKATALOG)
    yield tilkobling
    tilkobling.close()


def lager(tilkobling, tidspunkt: str = ONSDAG) -> SqliteVurderingslager:
    return SqliteVurderingslager(tilkobling, klokke(tidspunkt))


class TestDatoavvisning:
    """K1: skriv avviser enhver dato som ikke er inneveerende boersdag (AD-7)."""

    def test_dagens_boersdag_godtas(self, tilkobling):
        assert lager(tilkobling).skriv("EQNR", date(2026, 9, 23), vurdering()) is True
        assert lager(tilkobling).les("EQNR", date(2026, 9, 23)) == vurdering()

    @pytest.mark.parametrize("dato", [date(2026, 9, 22), date(2026, 9, 24)],
                             ids=["i_gaar", "i_morgen"])
    def test_i_gaar_og_i_morgen_reiser(self, tilkobling, dato):
        with pytest.raises(ValueError, match="inneveerende boersdag"):
            lager(tilkobling).skriv("EQNR", dato, vurdering())
        assert rader(tilkobling) == []

    def test_eldre_rad_kan_ikke_skrives_om_neste_dag(self, tilkobling):
        """Klokka leses ved hvert kall, ikke naar lageret lages: gaarsdagens rad
        er utilgjengelig gjennom porten fra dagen etter."""
        naa = [datetime.fromisoformat("2026-09-22T10:00:00+00:00")]
        vurderinger = SqliteVurderingslager(tilkobling, lambda: naa[0])
        vurderinger.skriv("EQNR", date(2026, 9, 22), vurdering())
        naa[0] = datetime.fromisoformat(ONSDAG)
        with pytest.raises(ValueError, match="inneveerende boersdag"):
            vurderinger.skriv("EQNR", date(2026, 9, 22), vurdering(styrke=3, interesse=1))
        assert vurderinger.les("EQNR", date(2026, 9, 22)) == vurdering()

    @pytest.mark.parametrize("tidspunkt, godtatt, avvist", [
        (SOMMER_0030, date(2026, 9, 25), date(2026, 9, 24)),
        (VINTER_0030, date(2026, 12, 11), date(2026, 12, 10)),
    ], ids=["sommertid", "vintertid"])
    def test_0030_norsk_tid_er_dagen_i_oslo(self, tilkobling, tidspunkt, godtatt, avvist):
        """Ville feilet hvis datogrensen ble regnet i UTC: da er 00:30 norsk tid
        fortsatt dagen foer, og kjoeringen skrev paa gaarsdagen."""
        vurderinger = lager(tilkobling, tidspunkt)
        assert vurderinger.skriv("EQNR", godtatt, vurdering()) is True
        with pytest.raises(ValueError, match="inneveerende boersdag"):
            vurderinger.skriv("EQNR", avvist, vurdering())
        assert [r[1] for r in rader(tilkobling)] == [godtatt.isoformat()]

    def test_en_loerdag_er_fredagen_inneveerende_boersdag(self, tilkobling):
        vurderinger = lager(tilkobling, "2026-09-26T12:00:00+00:00")
        assert vurderinger.skriv("EQNR", date(2026, 9, 25), vurdering()) is True
        with pytest.raises(ValueError, match="inneveerende boersdag"):
            vurderinger.skriv("EQNR", date(2026, 9, 26), vurdering())

    def test_klokke_uten_sone_reiser(self, tilkobling):
        vurderinger = SqliteVurderingslager(tilkobling, lambda: datetime(2026, 9, 23, 10))
        with pytest.raises(ValueError, match="tidssone"):
            vurderinger.skriv("EQNR", date(2026, 9, 23), vurdering())
        assert rader(tilkobling) == []

    def test_dag_utenfor_kalenderen_reiser(self, tilkobling):
        """Punkt 25 i prd.md §8: fra 2027-01-01 reiser skriv til dagene for
        2027 er foert inn. Den gjetter ikke paa en boersdag."""
        vurderinger = lager(tilkobling, "2027-01-04T10:00:00+00:00")
        with pytest.raises(UtenforKalenderen):
            vurderinger.skriv("EQNR", date(2027, 1, 4), vurdering())
        assert rader(tilkobling) == []

    def test_tidspunkt_som_dato_reiser(self, tilkobling):
        with pytest.raises(TypeError, match="date"):
            lager(tilkobling).skriv("EQNR", datetime(2026, 9, 23, 10, tzinfo=timezone.utc),
                                    vurdering())
        assert rader(tilkobling) == []


class TestSisteVinner:
    """K2 og K6: en rad per (symbol, dato), og en grunn skriver aldri over en
    vurdering (punkt 24)."""

    def test_to_skriv_gir_en_rad_og_den_siste_vinner(self, tilkobling):
        vurderinger = lager(tilkobling)
        vurderinger.skriv("EQNR", date(2026, 9, 23), vurdering())
        assert vurderinger.skriv(
            "EQNR", date(2026, 9, 23), vurdering(styrke=3, interesse=1)
        ) is True
        assert rader(tilkobling) == [("EQNR", "2026-09-23", 3, None)]
        assert vurderinger.les("EQNR", date(2026, 9, 23)) == vurdering(styrke=3, interesse=1)

    def test_grunn_over_vurdering_ignoreres_og_gir_false(self, tilkobling):
        vurderinger = lager(tilkobling)
        vurderinger.skriv("EQNR", date(2026, 9, 23), vurdering())
        assert vurderinger.skriv("EQNR", date(2026, 9, 23), Grunn.SYMBOL_FEILET) is False
        assert vurderinger.les("EQNR", date(2026, 9, 23)) == vurdering()

    def test_vurdering_over_grunn_skriver_over(self, tilkobling):
        vurderinger = lager(tilkobling)
        vurderinger.skriv("EQNR", date(2026, 9, 23), Grunn.KURS_IKKE_FRA_DAGEN)
        assert vurderinger.skriv("EQNR", date(2026, 9, 23), vurdering()) is True
        assert vurderinger.les("EQNR", date(2026, 9, 23)) == vurdering()

    def test_grunn_over_grunn_skriver_over(self, tilkobling):
        vurderinger = lager(tilkobling)
        vurderinger.skriv("EQNR", date(2026, 9, 23), Grunn.SYMBOL_FEILET)
        assert vurderinger.skriv("EQNR", date(2026, 9, 23), Grunn.SIGNAL_IKKE_REGNET) is True
        assert vurderinger.les("EQNR", date(2026, 9, 23)) is Grunn.SIGNAL_IKKE_REGNET
        assert len(rader(tilkobling)) == 1

    def test_andre_symboler_roeres_ikke(self, tilkobling):
        vurderinger = lager(tilkobling)
        vurderinger.skriv("EQNR", date(2026, 9, 23), vurdering())
        vurderinger.skriv("DNB", date(2026, 9, 23), Grunn.SYMBOL_FEILET)
        assert vurderinger.les("EQNR", date(2026, 9, 23)) == vurdering()
        assert vurderinger.les("DNB", date(2026, 9, 23)) is Grunn.SYMBOL_FEILET


class TestLes:
    def test_ingen_rad_gir_none(self, tilkobling):
        assert lager(tilkobling).les("EQNR", date(2026, 9, 23)) is None

    def test_ticker_i_stedet_for_symbol_reiser(self, tilkobling):
        """None ville blitt lest som at kommandoen ikke ble kjoert (FR-409)."""
        with pytest.raises(ValueError, match="EQNR.OL"):
            lager(tilkobling).les("EQNR.OL", date(2026, 9, 23))

    def test_tidspunkt_som_dato_reiser(self, tilkobling):
        with pytest.raises(TypeError, match="date"):
            lager(tilkobling).les("EQNR", datetime(2026, 9, 23, 10, tzinfo=timezone.utc))

    @pytest.mark.parametrize("kurs", [2**53 + 1, 10**20], ids=["2**53+1", "10**20"])
    def test_store_heltall_leses_tilbake_like(self, tilkobling, kurs):
        """ECH1 og ECH2: et heltall blir float i Vurdering, som i REAL-kolonnen."""
        vurderinger = lager(tilkobling)
        vurderinger.skriv("EQNR", date(2026, 9, 23), vurdering(justert_slutt=kurs))
        assert vurderinger.les("EQNR", date(2026, 9, 23)) == vurdering(justert_slutt=kurs)

    def test_eldre_rader_kan_leses(self, tilkobling):
        SqliteVurderingslager(tilkobling, klokke("2026-09-22T10:00:00+00:00")).skriv(
            "EQNR", date(2026, 9, 22), vurdering()
        )
        assert lager(tilkobling).les("EQNR", date(2026, 9, 22)) == vurdering()

    def test_grunn_leses_som_grunn(self, tilkobling):
        vurderinger = lager(tilkobling)
        vurderinger.skriv("EQNR", date(2026, 9, 23), Grunn.SYMBOL_FEILET)
        assert isinstance(vurderinger.les("EQNR", date(2026, 9, 23)), Grunn)

    def test_rad_med_grunn_har_ingen_kurs(self, tilkobling):
        lager(tilkobling).skriv("EQNR", date(2026, 9, 23), Grunn.KURS_IKKE_FRA_DAGEN)
        assert tilkobling.execute(
            "SELECT slutt, justert_slutt FROM vurdering"
        ).fetchone() == (None, None)


class TestProtokollen:
    """K3: ingen slett og ingen endre, kontrollert paa protokollen (AD-7)."""

    @staticmethod
    def _offentlige(klasse) -> set[str]:
        # dir og ikke vars, saa en slett arvet fra en baseklasse ogsaa sees.
        return {navn for navn in dir(klasse) if not navn.startswith("_")}

    def test_porten_har_bare_skriv_og_les(self):
        assert self._offentlige(Vurderingslager) == {"skriv", "les"}

    def test_adapteren_har_bare_skriv_og_les(self):
        assert self._offentlige(SqliteVurderingslager) == {"skriv", "les"}

    def test_adapteren_oppfyller_porten(self, tilkobling):
        assert isinstance(lager(tilkobling), Vurderingslager)


class TestSymbol:
    def test_ticker_i_stedet_for_symbol_avvises(self, tilkobling):
        with pytest.raises(ValueError, match="EQNR.OL"):
            lager(tilkobling).skriv("EQNR.OL", date(2026, 9, 23), vurdering())
        assert rader(tilkobling) == []

    def test_feil_innhold_avvises(self, tilkobling):
        with pytest.raises(TypeError, match="Vurdering eller Grunn"):
            lager(tilkobling).skriv("EQNR", date(2026, 9, 23), "symbol_feilet")
        assert rader(tilkobling) == []

    def test_feil_i_basen_rulles_tilbake(self, tilkobling):
        """En feil midt i skrivingen etterlater ingen aapen transaksjon, og
        lageret kan brukes etterpaa."""
        tilkobling.execute(
            "CREATE TEMP TRIGGER stopp BEFORE INSERT ON vurdering "
            "BEGIN SELECT RAISE(ABORT, 'stoppet av testen'); END"
        )
        vurderinger = lager(tilkobling)
        with pytest.raises(sqlite3.IntegrityError, match="stoppet av testen"):
            vurderinger.skriv("EQNR", date(2026, 9, 23), vurdering())
        assert not tilkobling.in_transaction
        tilkobling.execute("DROP TRIGGER stopp")
        assert vurderinger.skriv("EQNR", date(2026, 9, 23), vurdering()) is True

    def test_aapen_transaksjon_hos_kalleren_avvises(self, tilkobling):
        """Samme regel som i SqliteKurslager: adapteren eier transaksjonen."""
        tilkobling.execute("BEGIN")
        with pytest.raises(RuntimeError, match="aapen transaksjon"):
            lager(tilkobling).skriv("EQNR", date(2026, 9, 23), vurdering())
        tilkobling.execute("ROLLBACK")
        assert rader(tilkobling) == []


class TestErstattSerie:
    """K4: vurderingen overlever erstatt_serie paa samme symbol (AD-18)."""

    def test_vurderingen_og_kursen_i_den_er_uendret(self, tilkobling):
        vurderinger = lager(tilkobling)
        vurderinger.skriv("EQNR", date(2026, 9, 23), vurdering())
        SqliteKurslager(tilkobling).erstatt_serie(
            "EQNR",
            [Kursrad(dato=date(2026, 9, 23), slutt=1.0, justert_slutt=1.0, volum=1)],
            datetime(2026, 9, 23, 16, tzinfo=timezone.utc),
        )
        assert vurderinger.les("EQNR", date(2026, 9, 23)) == vurdering()

    def test_ingen_fremmednoekkel_til_kurs(self, tilkobling):
        assert tilkobling.execute("PRAGMA foreign_key_list(vurdering)").fetchall() == []


class TestOverleverOmstart:
    def test_vurderingen_finnes_etter_ny_tilkobling(self, tmp_path):
        sti = tmp_path / "ose.db"
        foerste = sqlite3.connect(sti)
        migrer(foerste, MIGRASJONSKATALOG)
        lager(foerste).skriv("EQNR", date(2026, 9, 23), vurdering())
        foerste.close()

        andre = sqlite3.connect(sti)
        try:
            assert lager(andre).les("EQNR", date(2026, 9, 23)) == vurdering()
        finally:
            andre.close()


class TestSkjemaet:
    """K5 og K6: tabellen lages av 0002 (AD-16), og basen haandhever
    enten/eller og grunnene selv, ogsaa utenom porten."""

    def test_0002_finnes_og_lager_vurdering_og_grunn(self):
        tekst = (MIGRASJONSKATALOG / "0002_vurdering.sql").read_text(encoding="utf-8")
        assert "CREATE TABLE vurdering" in tekst
        assert "CREATE TABLE grunn" in tekst

    def test_migrer_lager_tabellene_foer_noen_adapter_finnes(self, tilkobling):
        tabeller = {
            navn for (navn,) in tilkobling.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        assert {"vurdering", "grunn"} <= tabeller

    def test_adapteren_lager_ingenting(self, tilkobling):
        foer = tilkobling.execute("SELECT type, name FROM sqlite_master").fetchall()
        lager(tilkobling)
        assert tilkobling.execute("SELECT type, name FROM sqlite_master").fetchall() == foer

    def test_base_paa_versjon_1_avvises(self, tmp_path):
        katalog = tmp_path / "bare_0001"
        katalog.mkdir()
        (katalog / "0001_kurs.sql").write_bytes(
            (MIGRASJONSKATALOG / "0001_kurs.sql").read_bytes()
        )
        tilkobling = sqlite3.connect(":memory:")
        try:
            assert migrer(tilkobling, katalog) == 1
            with pytest.raises(RuntimeError, match="versjon 1"):
                lager(tilkobling)
            assert versjon(tilkobling) == 1
        finally:
            tilkobling.close()

    def test_grunn_i_basen_er_grunn_i_porten(self, tilkobling):
        assert {navn for (navn,) in tilkobling.execute("SELECT navn FROM grunn")} == {
            grunn.value for grunn in Grunn
        }

    def _sett_inn(self, tilkobling, **felt):
        kolonner = ", ".join(["symbol", "dato", *felt])
        plasser = ", ".join("?" * (len(felt) + 2))
        tilkobling.execute(
            f"INSERT INTO vurdering ({kolonner}) VALUES ({plasser})",
            ("EQNR", "2026-09-23", *felt.values()),
        )

    GYLDIG = dict(styrke=2, retning="Positiv", trend=1, bevegelse=1, interesse=0,
                  slutt=300.0, justert_slutt=290.0, trend_avvik=0.035,
                dagens_endring=0.021, standardavvik=0.012, volumforhold=1.2)

    def test_gyldige_rader_godtas_av_basen(self, tilkobling):
        self._sett_inn(tilkobling, **self.GYLDIG)
        tilkobling.execute(
            "INSERT INTO vurdering (symbol, dato, grunn) VALUES ('DNB', '2026-09-23', ?)",
            (Grunn.SYMBOL_FEILET.value,),
        )

    def test_baade_vurdering_og_grunn_stoppes(self, tilkobling):
        with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
            self._sett_inn(tilkobling, **self.GYLDIG, grunn=Grunn.SYMBOL_FEILET.value)

    def test_verken_vurdering_eller_grunn_stoppes(self, tilkobling):
        with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
            self._sett_inn(tilkobling)

    @pytest.mark.parametrize("felt", VURDERINGSFELT)
    def test_et_vurderingsfelt_som_mangler_stoppes(self, tilkobling, felt):
        uten = {navn: verdi for navn, verdi in self.GYLDIG.items() if navn != felt}
        with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
            self._sett_inn(tilkobling, **uten)

    @pytest.mark.parametrize("felt", VURDERINGSFELT)
    def test_et_vurderingsfelt_ved_siden_av_grunn_stoppes(self, tilkobling, felt):
        with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
            self._sett_inn(tilkobling, grunn=Grunn.SYMBOL_FEILET.value,
                           **{felt: self.GYLDIG[felt]})

    @pytest.mark.parametrize("felt", PAAKREVDE_MAALINGER)
    def test_en_maaling_som_mangler_stoppes(self, tilkobling, felt):
        """Story 2.1c, matrisen: en vurdering uten en maaling avvises av
        basen, ikke bare av porten."""
        uten = {navn: verdi for navn, verdi in self.GYLDIG.items() if navn != felt}
        with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
            self._sett_inn(tilkobling, **uten)

    @pytest.mark.parametrize("felt", MAALINGER)
    def test_en_maaling_ved_siden_av_grunn_stoppes(self, tilkobling, felt):
        with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
            self._sett_inn(tilkobling, grunn=Grunn.SYMBOL_FEILET.value,
                           **{felt: self.GYLDIG[felt]})

    def test_volumforhold_kan_mangle_med_interesse_0(self, tilkobling):
        self._sett_inn(tilkobling, **dict(self.GYLDIG, volumforhold=None))
        assert tilkobling.execute("SELECT volumforhold FROM vurdering").fetchone() == (None,)

    @pytest.mark.parametrize("interesse", [1, -1])
    def test_volumforhold_mangler_med_interesse_stoppes(self, tilkobling, interesse):
        with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
            self._sett_inn(tilkobling, **dict(self.GYLDIG, interesse=interesse,
                                              volumforhold=None))

    @pytest.mark.parametrize("felt", ["standardavvik", "volumforhold"])
    def test_negativ_maaling_stoppes(self, tilkobling, felt):
        """Tillegget 01.10: standardavvik og forholdstall er aldri negative."""
        with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
            self._sett_inn(tilkobling, **dict(self.GYLDIG, **{felt: -0.001}))

    def test_null_godtas_som_standardavvik_og_forholdstall(self, tilkobling):
        self._sett_inn(tilkobling, **dict(self.GYLDIG, standardavvik=0.0, volumforhold=0.0))

    def test_negativt_avvik_og_negativ_endring_godtas(self, tilkobling):
        self._sett_inn(tilkobling, **dict(self.GYLDIG, trend_avvik=-0.05,
                                          dagens_endring=-0.03))

    def test_ukjent_grunn_stoppes_ved_insert(self, tilkobling):
        with pytest.raises(sqlite3.IntegrityError, match="ukjent grunn"):
            self._sett_inn(tilkobling, grunn="noe_annet")

    def test_ukjent_grunn_stoppes_ved_update(self, tilkobling):
        self._sett_inn(tilkobling, grunn=Grunn.SYMBOL_FEILET.value)
        with pytest.raises(sqlite3.IntegrityError, match="ukjent grunn"):
            tilkobling.execute("UPDATE vurdering SET grunn = 'noe_annet'")

    def test_ukjent_grunn_stoppes_via_upsert(self, tilkobling):
        """Det er INSERT-triggeren som stopper upserten: SQLite kjoerer den
        foer konflikten oppdages. UPDATE-triggeren proeves av testen over."""
        self._sett_inn(tilkobling, grunn=Grunn.SYMBOL_FEILET.value)
        with pytest.raises(sqlite3.IntegrityError, match="ukjent grunn"):
            tilkobling.execute(
                "INSERT INTO vurdering (symbol, dato, grunn) VALUES ('EQNR', '2026-09-23', "
                "'noe_annet') ON CONFLICT (symbol, dato) DO UPDATE SET grunn = excluded.grunn"
            )

    def test_en_grunn_slettes_ikke(self, tilkobling):
        with pytest.raises(sqlite3.IntegrityError, match="slettes ikke"):
            tilkobling.execute("DELETE FROM grunn WHERE navn = 'symbol_feilet'")

    def test_en_grunn_endres_ikke(self, tilkobling):
        with pytest.raises(sqlite3.IntegrityError, match="endres ikke"):
            tilkobling.execute(
                "UPDATE grunn SET navn = 'noe_annet' WHERE navn = 'symbol_feilet'"
            )

    def test_kolonne_for_meldinger_krever_ingen_ombygging(self, tilkobling):
        """Beslutningen: «Relevante meldinger» kan komme som en kolonne som kan
        vaere tom. Radene staar, og CHECK og triggere virker etterpaa."""
        lager(tilkobling).skriv("EQNR", date(2026, 9, 23), vurdering())
        tilkobling.execute("ALTER TABLE vurdering ADD COLUMN meldinger TEXT")
        assert tilkobling.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert lager(tilkobling).les("EQNR", date(2026, 9, 23)) == vurdering()
        assert tilkobling.execute("SELECT meldinger FROM vurdering").fetchone() == (None,)
        with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
            self._sett_inn(tilkobling,
                           **self.GYLDIG, grunn=Grunn.SYMBOL_FEILET.value)
        with pytest.raises(sqlite3.IntegrityError, match="ukjent grunn"):
            tilkobling.execute(
                "INSERT INTO vurdering (symbol, dato, grunn) VALUES ('DNB', '2026-09-23', 'x')"
            )

    def test_ny_grunn_er_en_insert(self, tilkobling):
        """Beslutningen: en ny grunn krever ingen ombygging av vurdering."""
        tilkobling.execute("INSERT INTO grunn (navn) VALUES ('ny_grunn')")
        self._sett_inn(tilkobling, grunn="ny_grunn")


class TestVurdering:
    def test_retningene_er_signalberegningens(self):
        assert set(RETNINGER) == {
            signalberegning.POSITIV, signalberegning.NEGATIV,
            signalberegning.BLANDET, signalberegning.INGEN,
        }

    def test_tre_grunner(self):
        assert len(Grunn) == 3

    @pytest.mark.parametrize("sjekker", list(itertools.product((-1, 0, 1), repeat=3)))
    def test_retningen_er_den_finn_retning_gir(self, sjekker):
        """Alle 27 kombinasjonene: porten godtar bare retningen kjernen gir."""
        riktig = signalberegning.finn_retning(tuple(
            signalberegning.Sjekk(navn="", verdi=verdi, forklaring="") for verdi in sjekker
        ))
        trend, bevegelse, interesse = sjekker
        felt = dict(styrke=sum(map(abs, sjekker)), trend=trend, bevegelse=bevegelse,
                    interesse=interesse)
        vurdering(retning=riktig, **felt)
        for annen in set(RETNINGER) - {riktig}:
            with pytest.raises(UgyldigVurdering, match="stemmer ikke"):
                vurdering(retning=annen, **felt)

    @pytest.mark.parametrize("sjekker", list(itertools.product((-1, 0, 1), repeat=3)))
    def test_styrken_er_den_finn_styrke_gir(self, sjekker):
        """Story 1.8 (G5), som testen for retningen over: alle 27
        kombinasjonene, og porten godtar bare styrken kjernen gir."""
        som_sjekker = tuple(
            signalberegning.Sjekk(navn="", verdi=verdi, forklaring="") for verdi in sjekker
        )
        riktig = signalberegning.finn_styrke(som_sjekker)
        retning = signalberegning.finn_retning(som_sjekker)
        trend, bevegelse, interesse = sjekker
        felt = dict(retning=retning, trend=trend, bevegelse=bevegelse, interesse=interesse)
        vurdering(styrke=riktig, **felt)
        for annen in set(range(4)) - {riktig}:
            with pytest.raises(UgyldigVurdering, match="stemmer ikke"):
                vurdering(styrke=annen, **felt)

    @pytest.mark.parametrize("endret", [
        dict(styrke=4, trend=1, bevegelse=1, interesse=1),
        dict(styrke=-1),
        dict(styrke=True, trend=1, bevegelse=0, interesse=0),
        dict(styrke=2.0),
        dict(styrke=1),
        dict(retning="positiv"),
        dict(retning=None),
        dict(trend=2, styrke=3),
        dict(bevegelse=-2),
        dict(interesse=True),
        dict(slutt=0.0),
        dict(slutt=-1.0),
        dict(slutt=math.nan),
        dict(justert_slutt=math.inf),
        dict(justert_slutt="290"),
        dict(slutt=True),
        dict(slutt=10**400),
        dict(trend_avvik=math.nan),
        dict(dagens_endring=math.inf),
        dict(standardavvik=-math.inf),
        dict(volumforhold=math.nan),
        dict(trend_avvik=None),
        dict(dagens_endring=True),
        dict(standardavvik="0.012"),
        dict(volumforhold="1.2"),
        dict(trend_avvik=10**400),
        dict(standardavvik=-0.001),
        dict(volumforhold=-0.001),
        dict(volumforhold=None, interesse=1, styrke=3),
        dict(volumforhold=None, interesse=-1, styrke=3, retning="Blandet"),
    ], ids=repr)
    def test_ugyldige_verdier_avvises(self, endret):
        with pytest.raises(UgyldigVurdering):
            vurdering(**endret)

    def test_heltall_godtas_som_kurs(self):
        assert vurdering(slutt=300, justert_slutt=290) == vurdering()

    def test_heltall_blir_float_i_maalingene(self):
        heltall = vurdering(trend_avvik=0, dagens_endring=-1, standardavvik=0, volumforhold=2)
        for felt in MAALINGER:
            assert type(getattr(heltall, felt)) is float, felt
        assert heltall == vurdering(trend_avvik=0.0, dagens_endring=-1.0,
                                    standardavvik=0.0, volumforhold=2.0)

    def test_volumforhold_kan_mangle_med_interesse_0(self):
        assert vurdering(volumforhold=None).volumforhold is None

    def test_porten_sjekker_ikke_fortegnet_mot_maalingen(self):
        """Spesifikasjonen: fortegnet mot maalingen er kjernens regel, og
        porten importerer ikke kjernen."""
        godtatt = vurdering(trend=1, trend_avvik=-0.5, bevegelse=1, dagens_endring=-0.5)
        assert godtatt.trend_avvik == -0.5
        assert godtatt.dagens_endring == -0.5

    def test_kolonnene_er_feltene_i_vurdering(self):
        """Ville feilet hvis en maaling manglet i VURDERINGSKOLONNER, saa
        upserten og les ikke tok den med."""
        assert VURDERINGSKOLONNER == tuple(f.name for f in dataclasses.fields(Vurdering))

    def test_styrke_null_med_retning_ingen(self):
        vurdering(styrke=0, retning="Ingen", trend=0, bevegelse=0, interesse=0)


class TestMaalingeneRundt:
    """Story 2.1c, kriteriet: en Vurdering med maalingene fra et Signal fra
    beregn_signal skrives og leses tilbake med de fire flyttallene noeyaktig
    like. Omformingen fra Signal til Vurdering bygges i 2.5; her lages den i
    testen."""

    @staticmethod
    def fra_signal(rader: list[Kursrad]) -> Vurdering:
        signal = signalberegning.beregn_signal(rader)
        trend, bevegelse, interesse = signal.sjekker
        return Vurdering(
            styrke=signal.styrke, retning=signal.retning,
            trend=trend.verdi, bevegelse=bevegelse.verdi, interesse=interesse.verdi,
            slutt=rader[-1].slutt, justert_slutt=rader[-1].justert_slutt,
            trend_avvik=trend.maaling, dagens_endring=bevegelse.maaling,
            standardavvik=bevegelse.grense, volumforhold=interesse.maaling,
        )

    @staticmethod
    def rader(volumer: list[int]) -> list[Kursrad]:
        # Ujevne kurser, saa ingen maaling blir et rundt tall. Oppdiktet.
        kurser = [100.0 + (nummer * 7 % 11) * 0.37 + nummer * 0.13 for nummer in range(61)]
        start = date(2026, 6, 1)
        return [
            Kursrad(dato=start + timedelta(days=nummer), slutt=kurs + 1.0,
                    justert_slutt=kurs, volum=volum)
            for nummer, (kurs, volum) in enumerate(zip(kurser, volumer))
        ]

    @pytest.mark.parametrize("volumer", [
        [1_000 + nummer * 37 % 501 for nummer in range(60)] + [2_345],
        [0] * 60 + [2_345],
    ], ids=["vanlig dag", "medianvolum 0"])
    def test_de_fire_flyttallene_er_noeyaktig_like(self, tilkobling, volumer):
        skrevet = self.fra_signal(self.rader(volumer))
        assert lager(tilkobling).skriv("EQNR", date(2026, 9, 23), skrevet) is True

        lest = lager(tilkobling).les("EQNR", date(2026, 9, 23))

        assert lest == skrevet
        for felt in MAALINGER:
            assert getattr(lest, felt) == getattr(skrevet, felt), felt
            assert type(getattr(lest, felt)) is type(getattr(skrevet, felt)), felt
