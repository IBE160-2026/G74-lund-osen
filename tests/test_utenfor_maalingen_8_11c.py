"""Story 8.11c: «Utenfor målingen» med samme median som bransjelistene.

Spørsmål 9 i 8.11b, gruppens svar 09.11 kl. 10:23 og 10:47. Spesifikasjonen
er spec-8-11c-utenfor-maalingen.md. Hver test lager sin egen base under
tmp_path (regel 22), og ingen test gjør nettkall (AD-8). Kursene er
oppdiktet, ingen tall fra kildene (regel 16).
"""

import re
import sqlite3
from datetime import date, datetime, timedelta

import pytest

import app as app_modul
import ferdige_lister
import lagring_sqlite
import valg
from lagring_sqlite import aapne_base
from test_ferdige_lister import maal
from test_ferdige_lister_8_11b import base  # noqa: F401 (fixturen)
from test_fetch_prices import OEYEBLIKK_22_09, kjoer_23
from test_valg import BOERSEN, lager, med_boersen

MERKET = re.compile(
    r'<a href="/aksje/NYA">Ny Aksje ASA</a> <span class="egenmerke">Egen</span>( <span class="utenformerke")?'
)


def _sql(sti, sql, *argumenter):
    t = sqlite3.connect(sti)
    try:
        with t:
            t.execute(sql, argumenter)
    finally:
        t.close()


@pytest.fixture
def egen(tmp_path, monkeypatch):
    """NYA følges fra siden og er hentet to kvelder, som i test_valg."""
    raa, sti = tmp_path / "raa", tmp_path / "db" / "ose.db"
    kjoer_23(raa, sti, OEYEBLIKK_22_09 - timedelta(days=1))
    med_boersen(sti, [*BOERSEN, ("DNB", "DnB ASA")])
    l = lager(sti)
    l.folg("NYA", "Kraft")
    l._t.close()
    kjoer_23(raa, sti, OEYEBLIKK_22_09)
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", sti)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 23, 12, 0).astimezone())
    app_modul.app.config["TESTING"] = True
    return sti


def _side(sti="/"):
    return app_modul.app.test_client().get(sti).data.decode("utf-8")


class TestMedianene:
    def test_de_samme_som_i_de_ferdige_listene(self, base):  # noqa: F811
        """Del A: ville feilet hvis merket og de ferdige listene fikk hver
        sin median for en aksje som regnes av kursene, eller dagen ikke var
        den siste dagen med kurser."""
        t = aapne_base(base)
        try:
            medianene = ferdige_lister.medianene(t)
            listene = ferdige_lister.lister(t)
        finally:
            t.close()
        i_listene = {a.symbol: a.median for liste in listene.values() for a in liste}
        assert {"EQNR", "DNB"} <= set(medianene)
        for symbol in ("EQNR", "DNB"):
            assert medianene[symbol] == (i_listene[symbol], date(2026, 10, 22))

    def test_en_maalt_aksje_uten_kurser_er_ikke_med(self, base):  # noqa: F811
        """Del A: ville feilet hvis en aksje som bare er målt i 2.13, fikk en
        median herfra i stedet for målingen."""
        med_boersen(base, [("ANNEN", "Annen ASA")])
        maal(base, [("ANNEN", 40e6)])
        t = aapne_base(base)
        try:
            assert "ANNEN" not in ferdige_lister.medianene(t)
        finally:
            t.close()

    def test_en_base_uten_tabellene_gir_ingen_medianer(self, tmp_path):
        """Gjennomgangen (VG4): ville feilet hvis en base uten tabellene, som
        en base fra før migreringen, ga en feil i stedet for ingen medianer."""
        t = sqlite3.connect(tmp_path / "tom.db")
        try:
            assert ferdige_lister.medianene(t) == {}
        finally:
            t.close()

    def test_uten_basen_og_uten_kurser_er_den_tom(self, tmp_path):
        """Ville feilet hvis en base uten kurser eller uten tilkobling ga en
        feil i stedet for ingen medianer."""
        assert ferdige_lister.medianene(None) == {}
        sti = tmp_path / "ose.db"
        aapne_base(sti).close()
        t = aapne_base(sti)
        try:
            assert ferdige_lister.medianene(t) == {}
        finally:
            t.close()


class TestMerket:
    def test_kursene_gaar_foran_en_hoey_maaling(self, egen):
        """Del B: ville feilet hvis merket for en egen aksje som er hentet,
        fulgte målingen i 2.13 og ikke medianen av kursene, som de ferdige
        listene."""
        maal(egen, [("NYA", 500e6)])
        side = _side()
        treff = MERKET.search(side)
        assert treff and treff.group(1), "NYA skulle hatt merket"
        assert "regnet av kursene til 22.09.2026" in side

    def test_kursene_gaar_foran_en_lav_maaling(self, egen):
        """Del B: ville feilet hvis en lav måling i 2.13 ga merket når
        medianen av kursene er over 32 MNOK."""
        maal(egen, [("NYA", 1e6)])
        _sql(egen, "UPDATE kurs SET volum = 1000000000 WHERE symbol = 'NYA'")
        treff = MERKET.search(_side())
        assert treff and not treff.group(1), "NYA skulle vært uten merket"

    def test_merket_og_den_ferdige_lista_er_enige(self, egen):
        """Del B: ville feilet hvis en aksje sto med merket i tabellen og uten
        det i den ferdige lista, eller omvendt (ECH2 i 8.11b)."""
        maal(egen, [("NYA", 500e6)])
        side = _side("/min-liste")
        ferdig = re.search(
            r"NYA</span>( <span class=\"utenformerke\">Utenfor målingen)?", side.split("Start fra en ferdig liste")[1]
        )
        assert ferdig and ferdig.group(1), "NYA skulle hatt merket i den ferdige lista"
        treff = MERKET.search(_side())
        assert treff and treff.group(1), "NYA skulle hatt merket i tabellen"


class TestMerketEtterGjennomgangen:
    def test_en_aksje_i_lista_uten_kurser_bruker_ikke_maalingen(self, egen):
        """Spørsmål 5 (gjennomgangen, VG2): ville feilet hvis en egen aksje i
        lista uten kurser i vinduet fikk medianen fra en eldre måling, så
        merket og den ferdige lista, der den ikke står, var uenige."""
        _sql(egen, "DELETE FROM kurs WHERE symbol = 'NYA'")
        maal(egen, [("NYA", 500e6)])
        assert 'class="utenformerke" title="Omsetningen er ikke målt ennå.' in _side()

    def test_begge_uten_merket(self, egen):
        """Gjennomgangen (BH10): ville feilet hvis tabellen eller den ferdige
        lista ga merket når medianen av kursene er over 32 MNOK."""
        maal(egen, [("NYA", 1e6)])
        _sql(egen, "UPDATE kurs SET volum = 1000000000 WHERE symbol = 'NYA'")
        treff = MERKET.search(_side())
        assert treff and not treff.group(1), "NYA skulle vært uten merket i tabellen"
        ferdig = re.search(
            r"NYA</span>( <span class=\"utenformerke\">Utenfor målingen)?",
            _side("/min-liste").split("Start fra en ferdig liste")[1],
        )
        assert ferdig and not ferdig.group(1), "NYA skulle vært uten merket i den ferdige lista"


class TestFoelgSiden:
    def test_en_aksje_som_er_tatt_ut_viser_kursene(self, egen):
        """Del C: ville feilet hvis «Følg en aksje» viste målingen i 2.13 for
        en aksje som regnes av kursene, så siden og merket sa noe ulikt."""
        _sql(egen, "UPDATE aksje SET ut = '2026-09-23' WHERE symbol = 'DNB'")
        maal(egen, [("DNB", 500e6)])
        side = _side("/folg?kode=DNB")
        # Gjennomgangen (VG1, VG3): tallet uten fortegn og %, og begge linjene.
        assert "ca. 0,1 MNOK om dagen, regnet av kursene til 22.09." in side
        assert "omsetning de 3 siste månedene er 0,1 MNOK, regnet av kursene til 22.09." in side
        assert "så den merkes «Utenfor målingen»" in side
        assert "MNOK om dagen, regnet av kursene til 22.09</span>" in _side("/folg?q=DnB")

    def test_dagen_er_aksjens_siste_dag_med_kurser(self, egen):
        """Gjennomgangen (BH1, ECH1, BH10): ville feilet hvis teksten sa den
        siste dagen med kurser i basen om en aksje som er tatt ut og har sin
        siste kurs en dag før."""
        _sql(egen, "UPDATE aksje SET ut = '2026-09-22' WHERE symbol = 'DNB'")
        _sql(egen, "DELETE FROM kurs WHERE symbol = 'DNB' AND dato = '2026-09-22'")
        side = _side("/folg?kode=DNB")
        assert "regnet av kursene til 21.09." in side and "til 22.09." not in side

    def test_en_aksje_uten_kurser_viser_maalingen(self, egen):
        """Del C: ville feilet hvis en aksje appen aldri har hentet, mistet
        målingen fra 2.13 i søket."""
        maal(egen, [("NYB", 40e6)])
        assert "ca. 40,0 MNOK om dagen, målt 22.10</span>" in _side("/folg?q=NYB")


class TestTeksten:
    def test_kursene_eller_maalingen(self):
        """Del D: ville feilet hvis teksten bak merket sa «målt» om en median
        regnet av kursene, eller omvendt."""
        dag = date(2026, 10, 22)
        assert "regnet av kursene til 22.10.2026." in valg.utenfor_tekst(5e6, dag, kursene=True)
        assert "målt 22.10.2026." in valg.utenfor_tekst(5e6, dag)
        assert valg.utenfor_tekst(None, dag, kursene=True).startswith("Omsetningen er ikke målt ennå.")


class TestEnGangPerSide:
    def test_listene_og_medianene_regnes_en_gang_per_side(self, egen, monkeypatch):
        """Gjennomgangen (BH4, ECH2): ville feilet hvis oversikten regnet
        medianene og de ferdige listene flere ganger per side, fordi _egne()
        kjøres både i ruta og i context processoren."""
        kall = []
        ekte = ferdige_lister._aksjene_i_lista

        def tell(t):
            kall.append(1)
            return ekte(t)

        monkeypatch.setattr(ferdige_lister, "_aksjene_i_lista", tell)
        _side()
        assert len(kall) == 2, kall


def test_teksten_med_tusenskille():
    """Gjennomgangen (BH5): ville feilet hvis teksten bak merket regnet tallet
    selv, uten tusenskille, i stedet for med tall() (regel 21)."""
    tekst = valg.utenfor_tekst(1_234_560_000, date(2026, 10, 22), kursene=True)
    assert "er 1\u00a0234,6 MNOK, regnet av kursene til 22.10.2026." in tekst
