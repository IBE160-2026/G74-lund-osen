"""Story 2.9, PR 3 for hovedindeksen: tallene over tabellen - FR-104.

Kontrollen under story 2.9 i epics.md. Datoene er ekte boersdager i 2026:
fredag 09.10 og torsdag 08.10, med onsdag 07.10 foer dem.
"""

from datetime import date, datetime, timedelta, timezone

import pytest

from hovedindeks import (
    aksjeendring,
    bygg_hovedindeks,
    er_bedre,
    forrige_boersdag,
    indeksendring,
    sammenlign,
)
from indeksdata import MinneIndekslager
from kursdata import Kursrad
from lagring_sqlite import SqliteIndekslager, aapne_base
from tallformat import avrundet, tall

ONSDAG = date(2026, 10, 7)
TORSDAG = date(2026, 10, 8)
FREDAG = date(2026, 10, 9)


def rad(dag: date, kurs: float) -> Kursrad:
    return Kursrad(dato=dag, slutt=kurs, justert_slutt=kurs, volum=1000)


def med_endring(prosent: float, dag: date = FREDAG, foer: date = TORSDAG) -> list[Kursrad]:
    """En serie med to rader, der siste dag har endringen prosent."""
    return [rad(foer, 100.0), rad(dag, 100.0 * (1 + prosent / 100))]


class TestEndringen:
    def test_mot_forrige_boersdag(self):
        assert forrige_boersdag(FREDAG) == TORSDAG
        assert forrige_boersdag(date(2026, 10, 12)) == FREDAG  # mandag
        assert indeksendring([rad(TORSDAG, 1000.0), rad(FREDAG, 1010.0)]) == pytest.approx(1.0)

    def test_et_hull_foer_indeksens_dato_gir_ingen_endring(self):
        """Raden for torsdag mangler. Ville feilet med endringen mot forrige
        rad (mutant H2): da var den regnet mot onsdag."""
        assert indeksendring([rad(ONSDAG, 1000.0), rad(FREDAG, 1010.0)]) is None
        visning = bygg_hovedindeks("OSEBX", [rad(ONSDAG, 1000.0), rad(FREDAG, 1010.0)],
                                   [("A", med_endring(5.0))])
        assert visning.endring is None and visning.sammenligning is None
        assert visning.verdi == 1010.0 and visning.dato == FREDAG

    def test_en_dag_indeksen_har_og_kalenderen_ikke_hopper_ikke_over_boersdagen(self):
        """§14 i malinger.md: indeksen har stengte dager aksjene ikke har.
        En rad for en stengt dag mellom gir ikke endringen mot den."""
        langfredag, skjaertorsdag, onsdag = date(2026, 4, 3), date(2026, 4, 2), date(2026, 4, 1)
        tirsdag_etter = date(2026, 4, 7)
        assert forrige_boersdag(tirsdag_etter) == onsdag
        serie = [rad(onsdag, 1000.0), rad(skjaertorsdag, 990.0), rad(langfredag, 980.0), rad(tirsdag_etter, 1020.0)]
        assert indeksendring(serie) == pytest.approx(2.0)

    def test_forrige_boersdag_utenfor_kalenderen_gir_ingen_endring(self):
        """2. januar 2026 er foerste boersdag i aaret, og 2025 ligger utenfor
        DEKKEDE_AAR."""
        assert forrige_boersdag(date(2026, 1, 2)) is None
        assert indeksendring([rad(date(2025, 12, 30), 1000.0), rad(date(2026, 1, 2), 1010.0)]) is None


class TestSammenligningen:
    def test_n_er_aksjene_med_kurs_og_en_uten_navngis(self):
        """En kortere liste enn 15, og Gamma har ikke kurs for fredag. Ville
        feilet med N som et fast 15 (mutant H1)."""
        aksjer = [("Alfa", med_endring(2.0)), ("Beta", med_endring(-1.0)),
                  ("Gamma", [rad(ONSDAG, 50.0), rad(TORSDAG, 51.0)])]
        s = sammenlign(FREDAG, 0.5, aksjer)
        assert (s.bedre, s.med, s.uten) == (1, 2, ("Gamma",))

    def test_lik_er_ikke_bedre(self):
        """Ville feilet med lik regnet som bedre (mutant H3)."""
        assert not er_bedre(1.0, 1.0)
        s = sammenlign(FREDAG, 1.0, [("Alfa", med_endring(1.0))])
        assert s.bedre == 0 and s.med == 1

    def test_like_foerst_etter_avrundingen_er_ikke_bedre(self):
        """1,2349 % og 1,231 % vises begge som «+1,23 %». Ville feilet med
        «bedre» avgjort foer avrundingen (mutant H4)."""
        assert tall(1.2349, "endring") == tall(1.231, "endring")
        assert avrundet(1.2349, "endring") == avrundet(1.231, "endring") == 1.23
        assert not er_bedre(1.2349, 1.231)
        assert er_bedre(1.236, 1.231)
        s = sammenlign(FREDAG, 1.231, [("Alfa", med_endring(1.2349))])
        assert s.bedre == 0

    def test_ingen_aksje_med_kurs_for_dagen_gir_ingen_sammenligning(self):
        assert sammenlign(FREDAG, 0.5, [("Alfa", [rad(TORSDAG, 10.0)]), ("Beta", [])]) is None

    def test_en_aksje_uten_rad_foer_dagen_er_med_men_ikke_bedre(self):
        """En nylig notert aksje med bare fredagen: med i N, men den har ingen
        endring aa sammenligne."""
        assert aksjeendring([rad(FREDAG, 10.0)], FREDAG) is None
        s = sammenlign(FREDAG, -5.0, [("Ny", [rad(FREDAG, 10.0)])])
        assert (s.bedre, s.med) == (0, 1)

    def test_aksjens_endring_er_den_i_tabellen(self):
        """Endringen fra FR-101: dagen mot raden foer, ogsaa naar raden foer
        er eldre enn forrige boersdag."""
        serie = [rad(ONSDAG, 100.0), rad(FREDAG, 103.0)]
        assert aksjeendring(serie, FREDAG) == pytest.approx(3.0)


class TestEnDagBak:
    def test_indeksen_en_dag_bak_aksjene_sammenlignes_paa_sin_egen_dato(self):
        """Aksjene har fredag, indeksen bare torsdag. Sammenligningen gjelder
        torsdag, med aksjenes endring den dagen."""
        aksje = [rad(ONSDAG, 100.0), rad(TORSDAG, 102.0), rad(FREDAG, 90.0)]
        visning = bygg_hovedindeks("OSEBX", [rad(ONSDAG, 1000.0), rad(TORSDAG, 1010.0)], [("Alfa", aksje)])
        assert visning.dato == TORSDAG
        assert visning.endring == pytest.approx(1.0)
        assert visning.sammenligning.bedre == 1 and visning.sammenligning.med == 1


class TestPorten:
    @pytest.fixture(params=["minne", "sqlite"])
    def lager(self, request, tmp_path):
        if request.param == "minne":
            yield MinneIndekslager()
        else:
            tilkobling = aapne_base(tmp_path / "lager.db")
            yield SqliteIndekslager(tilkobling)
            tilkobling.close()

    def test_symboler_tom_uten_serie(self, lager):
        assert lager.symboler() == ()

    def test_symboler_gir_indeksen_basen_har(self, lager):
        lager.erstatt_serie("OSEBX", [rad(FREDAG, 1000.0)], datetime(2026, 10, 9, 20, 15, tzinfo=timezone.utc))
        assert lager.symboler() == ("OSEBX",)

    def test_sist_hentet_foerst(self, tmp_path):
        """To indekser: den sist hentede foerst, ogsaa naar tidene har ulik sone."""
        from indeksdata import Indeks

        a, b = Indeks("AAA", "AAA.OL", "A"), Indeks("BBB", "BBB.OL", "B")
        tilkobling = aapne_base(tmp_path / "to.db")
        try:
            lager = SqliteIndekslager(tilkobling, (a, b))
            tid = datetime(2026, 10, 9, 20, 0, tzinfo=timezone.utc)
            lager.erstatt_serie("AAA", [rad(FREDAG, 1.0)], tid)
            lager.erstatt_serie("BBB", [rad(FREDAG, 1.0)], tid + timedelta(minutes=1))
            assert lager.symboler() == ("BBB", "AAA")
        finally:
            tilkobling.close()
