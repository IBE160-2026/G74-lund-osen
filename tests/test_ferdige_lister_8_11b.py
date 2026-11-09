"""Story 8.11b: de 15 i bransjelistene - FR-108, FR-412, FR-413, AD-10.

Spesifikasjonen er spec-8-11b-de-15-i-bransjelistene.md. Hver test lager sin
egen base under tmp_path (regel 22), og ingen test gjør nettkall (AD-8).
Kursene er oppdiktet her, ingen tall fra kildene (regel 16).
"""

import ast
import inspect
import sqlite3
import statistics

import pytest

import ferdige_lister
import omsetning
import omsetningsregning
from lagring_sqlite import aapne_base
from test_ferdige_lister import maal
from test_valg import med_boersen

SISTE = "2026-10-22"
# I vinduet, 2026-07-22 til 2026-10-22 (vindu i omsetningsregning).
EQNR_RADER = [("2026-08-03", 10.0, 100), ("2026-09-01", 20.0, 100), ("2026-10-22", 30.0, 100)]
DNB_RADER = [("2026-08-03", 5.0, 10), ("2026-10-22", 5.0, 30)]
# Utenfor vinduet: så stor at den ville blitt medianen hvis den var med.
GAMMEL = ("2026-06-01", 1e9, 1_000_000)


def _kurser(base, symbol, rader):
    t = sqlite3.connect(base)
    try:
        with t:
            t.executemany(
                "INSERT INTO kurs (symbol, dato, slutt, justert_slutt, volum) VALUES (?, ?, ?, ?, ?)",
                [(symbol, d, s, s, v) for d, s, v in rader],
            )
    finally:
        t.close()


@pytest.fixture
def base(tmp_path, monkeypatch):
    sti = tmp_path / "db" / "ose.db"
    med_boersen(sti, [("EQNR", "Equinor ASA"), ("DNB", "DnB ASA")])
    _kurser(sti, "EQNR", [*EQNR_RADER, GAMMEL])
    _kurser(sti, "DNB", DNB_RADER)
    _kurser(sti, "KOG", EQNR_RADER)
    monkeypatch.setattr(ferdige_lister, "BRANSJE", {})
    return sti


def _lister(base):
    t = aapne_base(base)
    try:
        return ferdige_lister.lister(t)
    finally:
        t.close()


def _median(rader):
    return statistics.median(s * v for _, s, v in rader)


class TestDeFemten:
    def test_en_aksje_i_lista_er_med_med_medianen_av_kursene(self, base):
        """Del A: ville feilet hvis aksjene i lista ikke var med i
        bransjelistene, eller fikk en annen median enn utregningen i 2.13."""
        lister = _lister(base)
        assert [(a.symbol, a.median) for a in lister["Energi"]] == [("EQNR", _median(EQNR_RADER))]
        assert [(a.symbol, a.median) for a in lister["Finans"]] == [("DNB", _median(DNB_RADER))]
        assert lister["Energi"][0].navn == "Equinor ASA"

    def test_vinduet_er_tre_maaneder_til_siste_kursdag(self, base):
        """Del B: ville feilet hvis en kurs mer enn tre måneder før den siste
        dagen med kurser i basen var med i medianen."""
        assert _lister(base)["Energi"][0].median == _median(EQNR_RADER) != _median([*EQNR_RADER, GAMMEL])

    def test_kursene_gaar_foran_en_eldre_maaling(self, base):
        """Del C: ville feilet hvis en eldre rad i omsetning for en aksje i
        lista ble brukt i stedet for medianen av kursene."""
        maal(base, [("EQNR", 1e12)])
        assert _lister(base)["Energi"][0].median == _median(EQNR_RADER)

    def test_bare_aksjer_i_boerslista(self, base):
        """Del D: ville feilet hvis en aksje i lista som ikke står i lista
        over Oslo Børs (KOG her), kom i en ferdig liste."""
        alle = {a.symbol for liste in _lister(base).values() for a in liste}
        assert "KOG" not in alle and {"EQNR", "DNB"} <= alle

    def test_en_aksje_som_er_tatt_ut_er_med_saa_lenge_den_har_kurser(self, base):
        """Gjennomgangen (ECH1): ville feilet hvis en aksje som er tatt ut av
        lista, falt ut av bransjelistene mens den har kurser i vinduet, før
        2.13 har målt den."""
        t = sqlite3.connect(base)
        with t:
            t.execute("UPDATE aksje SET ut = '2026-10-01' WHERE symbol = 'DNB'")
        t.close()
        assert [(a.symbol, a.median) for a in _lister(base)["Finans"]] == [("DNB", _median(DNB_RADER))]

    def test_en_aksje_tatt_ut_uten_kurser_i_vinduet_bruker_maalingen(self, base):
        """Gjennomgangen (ECH1): ville feilet hvis en aksje som er tatt ut og
        ikke har kurser i vinduet, mistet en måling fra 2.13."""
        t = sqlite3.connect(base)
        with t:
            t.execute("UPDATE aksje SET ut = '2026-06-01' WHERE symbol = 'DNB'")
            t.execute("DELETE FROM kurs WHERE symbol = 'DNB'")
        t.close()
        maal(base, [("DNB", 7e6)])
        assert [(a.symbol, a.median) for a in _lister(base)["Finans"]] == [("DNB", 7e6)]

    def test_en_aksje_i_lista_uten_kurser_i_vinduet_bruker_ikke_en_eldre_maaling(self, base):
        """Gjennomgangen (BH3, VG1): ville feilet hvis en aksje i lista uten
        kurser i vinduet ble vist med en eldre måling (spørsmål 4)."""
        t = sqlite3.connect(base)
        with t:
            t.execute("DELETE FROM kurs WHERE symbol = 'DNB'")
        t.close()
        maal(base, [("DNB", 7e6)])
        assert "Finans" not in _lister(base)

    def test_vinduet_tar_med_den_foerste_dagen(self, base):
        """Gjennomgangen (BH6): ville feilet hvis dagen vinduet begynner, var
        utenfor, eller dagen før var innenfor."""
        _kurser(base, "DNB", [("2026-07-22", 100.0, 100), ("2026-07-21", 1e9, 1_000_000)])
        assert _lister(base)["Finans"][0].median == _median([*DNB_RADER, ("2026-07-22", 100.0, 100)])

    def test_en_dato_som_ikke_kan_leses_gir_ingen_feil(self, base):
        """Gjennomgangen (BH5): ville feilet hvis en dato i kurs som ikke kan
        leses, ga en feil på siden i stedet for ingen lister herfra."""
        _kurser(base, "EQNR", [("ikke en dato", 1.0, 1)])
        maal(base, [("NHY", 9e6)])
        assert _lister(base) == {}

    def test_ingen_kurser_gir_ingen_lister_fra_lista(self, tmp_path, monkeypatch):
        """Ville feilet hvis en base uten kurser ga en feil eller en liste."""
        sti = tmp_path / "db" / "ose.db"
        med_boersen(sti, [("EQNR", "Equinor ASA")])
        monkeypatch.setattr(ferdige_lister, "BRANSJE", {})
        assert _lister(sti) == {}

    def test_bare_lesing(self, base):
        """AD-10: ville feilet hvis lister skrev noe i basen."""
        t = aapne_base(base)
        try:
            foer = t.total_changes
            ferdige_lister.lister(t)
            assert t.total_changes == foer
        finally:
            t.close()


class TestSammeUtregning:
    def test_maalingen_og_listene_bruker_samme_funksjoner(self):
        """Ville feilet hvis 2.13 og 8.11b regnet medianen hver sin måte."""
        assert omsetning.regn_ut is omsetningsregning.regn_ut is ferdige_lister.regn_ut
        assert omsetning.vindu is omsetningsregning.vindu is ferdige_lister.vindu

    def test_webserveren_henter_aldri(self):
        """AD-10: ville feilet hvis listene eller utregningen importerte
        hentingen eller nettet."""
        for modul in (ferdige_lister, omsetningsregning):
            treet = ast.parse(inspect.getsource(modul))
            importert = {a.name for n in ast.walk(treet) if isinstance(n, ast.Import) for a in n.names}
            importert |= {n.module for n in ast.walk(treet) if isinstance(n, ast.ImportFrom)}
            assert not importert & {"fetch_prices", "omsetning", "requests", "eodhd", "urllib.request"}, importert
