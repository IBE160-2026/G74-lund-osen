"""Story 8.11: Ferdige lister og filter på signalet - FR-108, FR-412, FR-102, AD-3, AD-10.

Spesifikasjonen er spec-8-11-ferdige-lister.md. Hver test lager sin egen base
under tmp_path (regel 22), og ingen test gjør nettkall (AD-8).
"""

import inspect
import re
import sqlite3
from datetime import datetime, timezone

import pytest

import app as app_modul
import ferdige_lister
from lagring_sqlite import aapne_base
from test_valg import klient, lager, med_boersen, stier  # noqa: F401  (fiksturene)
from valg import BRANSJENE, TAK, ListaErFull

NITTEN = [(f"T{i:02d}", f"Test {i} ASA") for i in range(1, 20)]


def maal(base, rader):
    """rader: [(symbol, median eller None)], målt samme dag."""
    t = sqlite3.connect(base)
    try:
        with t:
            t.executemany(
                "INSERT INTO omsetning (symbol, maalt, fra, til, handelsdager, dager_uten_volum, rader_uten_tall, "
                "median_omsetning, feil) VALUES (?, '2026-10-22T20:00:00+00:00', '2026-07-22', '2026-10-22', 60, 0, "
                "0, ?, ?)",
                [(s, m, None if m is not None else "ingen kurser") for s, m in rader],
            )
    finally:
        t.close()


@pytest.fixture
def nitten(tmp_path, monkeypatch):
    base = tmp_path / "ose.db"
    med_boersen(base, NITTEN)
    monkeypatch.setattr(ferdige_lister, "BRANSJE", {k: "Kraft" for k, _ in NITTEN} | {"T19": "Helse"})
    maal(base, [(k, 1e6 * (100 - i)) for i, (k, _) in enumerate(NITTEN)])
    return base


class TestListene:
    def test_aldri_mer_enn_18(self, tmp_path, monkeypatch):
        """Ville feilet hvis en ferdig liste hadde 19 aksjer."""
        base = tmp_path / "ose.db"
        med_boersen(base, NITTEN)
        monkeypatch.setattr(ferdige_lister, "BRANSJE", {k: "Kraft" for k, _ in NITTEN})
        maal(base, [(k, 1e6 * (100 - i)) for i, (k, _) in enumerate(NITTEN)])
        lister = ferdige_lister.lister(aapne_base(base))
        assert [a.symbol for a in lister["Kraft"]] == [k for k, _ in NITTEN[:TAK]]

    def test_bare_maalte_med_tall(self, tmp_path, monkeypatch):
        """Ville feilet hvis en aksje som ikke er målt, eller ble målt med
        feil, sto i en ferdig liste."""
        base = tmp_path / "ose.db"
        med_boersen(base, NITTEN[:3])
        monkeypatch.setattr(ferdige_lister, "BRANSJE", {k: "Kraft" for k, _ in NITTEN[:3]})
        maal(base, [("T01", 5e6), ("T02", None)])
        assert [a.symbol for a in ferdige_lister.lister(aapne_base(base))["Kraft"]] == ["T01"]

    def test_hoeyest_omsetning_foerst_og_en_bransje_uten_maalte_har_ingen(self, nitten):
        lister = ferdige_lister.lister(aapne_base(nitten))
        assert list(lister) == ["Helse", "Kraft"]  # rekkefølgen i BRANSJENE
        assert lister["Helse"][0].symbol == "T19"
        assert [a.median for a in lister["Kraft"]] == sorted((a.median for a in lister["Kraft"]), reverse=True)

    def test_ett_sted_i_koden_og_bransjene_er_de_13(self):
        assert set(ferdige_lister.BRANSJE.values()) <= set(BRANSJENE)
        kilde = inspect.getsource(app_modul)
        assert "BRANSJE = {" not in kilde and "BRANSJE: dict" not in kilde


class TestBrukeLista:
    def test_lista_blir_den_ferdige_ved_neste_henting(self, nitten):
        """Ville feilet hvis lista kunne få mer enn 18, eller en ferdig liste
        skrev noe annet enn ønsker (AD-3)."""
        l = lager(nitten)
        l.folg("T19", "Helse")
        aksjer = l._t.execute("SELECT count(*) FROM aksje").fetchone()[0]
        kraft = ferdige_lister.lister(l._t)["Kraft"]
        l.bruk_liste([(a.symbol, "Kraft") for a in kraft])
        assert l._t.execute("SELECT count(*) FROM aksje").fetchone()[0] == aksjer
        assert l.antall() == TAK
        ventende = l.ventende()
        assert {o.symbol for o in ventende if o.handling == "folg"} == {a.symbol for a in kraft}
        assert len([o for o in ventende if o.handling == "fjern"]) == len(l.i_lista())

    def test_mer_enn_18_avvises(self, nitten):
        with pytest.raises(ListaErFull):
            lager(nitten).bruk_liste([(k, "Kraft") for k, _ in NITTEN])


class TestSiden:
    def test_ferdige_lister_i_min_liste(self, klient, monkeypatch):  # noqa: F811
        """Ville feilet hvis siden viste en liste vi ikke har målt."""
        import lagring_sqlite

        maal(lagring_sqlite.BASE_STI, [("NYA", 50e6), ("NYB", 2e6)])
        monkeypatch.setattr(ferdige_lister, "BRANSJE", {"NYA": "Kraft", "NYB": "Kraft", "NYC": "Helse"})
        side = klient.get("/min-liste").data.decode("utf-8")
        assert "Start fra en ferdig liste" in side
        assert re.search(r"Kraft <span class=\"antall\">2</span>", side) and "Helse <span" not in side
        assert side.count("Utenfor målingen</span>") >= 1
        svar = klient.post("/ferdig-liste", data={"bransje": "Kraft"})
        assert svar.status_code == 303
        assert klient.post("/ferdig-liste", data={"bransje": "Helse"}).status_code == 400
        assert (
            klient.post("/ferdig-liste", data={"bransje": "Kraft"}, headers={"Origin": "https://annen.no"}).status_code
            == 403
        )

    def test_ingen_kall(self):
        """AD-10: ville feilet hvis ruta eller listene hentet noe."""
        kilde = inspect.getsource(app_modul.bruk_ferdig_liste) + inspect.getsource(ferdige_lister)
        for ord_ in ("requests", "urlopen", "hent_", "fetch_prices", "eodhd"):
            assert ord_ not in kilde.lower(), ord_


def _symbolene(side: str) -> list[str]:
    tabell = side.split('id="aksjene"', 1)[1].split("</table>", 1)[0] if 'id="aksjene"' in side else ""
    return re.findall(r'<a href="/aksje/([A-Z0-9-]+)"', tabell)


@pytest.fixture
def demoklient(tmp_path, monkeypatch):
    """Demobasen som vanlig base: den har aksjer med 3 av 3 i begge retninger."""
    import demo
    import lagring_sqlite

    base = tmp_path / "db" / "ose.db"
    base.parent.mkdir(parents=True)
    demo.lag_demobase(base, skriv=lambda _: None)
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))
    monkeypatch.delenv(app_modul.I_DEMO, raising=False)
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client(), base


class TestFilteret:
    @pytest.mark.parametrize("retning", ["positiv", "negativ"])
    def test_bare_3_av_3_i_retningen_og_i_samme_rekkefoelge(self, demoklient, retning):
        """FR-102: ville feilet hvis filteret viste noe annet enn 3 av 3 i
        retningen, eller endret rekkefølgen."""
        side, base = demoklient
        t = sqlite3.connect(base)
        alle = _symbolene(side.get("/").data.decode("utf-8"))
        ventet = set()
        for s in alle:
            rad = t.execute(
                "SELECT styrke, retning FROM vurdering WHERE symbol = ? ORDER BY dato DESC LIMIT 1", (s,)
            ).fetchone()
            if rad and rad[0] == 3 and rad[1] == retning.capitalize():
                ventet.add(s)
        t.close()
        assert ventet, "demobasen skal ha minst én"
        filtrert = side.get(f"/?signal={retning}").data.decode("utf-8")
        assert _symbolene(filtrert) == [s for s in alle if s in ventet]
        assert "er ikke et råd om å kjøpe eller selge" in filtrert

    def test_bare_innenfor_lista_som_vises(self, demoklient):
        """Ville feilet hvis filteret i Min liste viste aksjer som ikke er merket."""
        side, _ = demoklient
        merket = set(_symbolene(side.get("/min-liste").data.decode("utf-8")))
        assert set(_symbolene(side.get("/min-liste?signal=negativ").data.decode("utf-8"))) <= merket
        assert set(_symbolene(side.get("/min-liste?signal=positiv").data.decode("utf-8"))) <= merket

    def test_en_annen_verdi_filtrerer_ikke(self, demoklient):
        side, _ = demoklient
        assert _symbolene(side.get("/?signal=kjop").data.decode("utf-8")) == _symbolene(
            side.get("/").data.decode("utf-8")
        )
