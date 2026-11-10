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
from valg import BRANSJENE, TAK, ListaErFull, UgyldigValg

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


class TestValideringenIBrukListe:
    """VG6 i gjennomgangen, rettet etter gruppens svar 08.11 kl. 22:06:
    valideringen i bruk_liste prøvd direkte, ikke bare gjennom ruta. Et
    avvist valg skal ikke endre noe, så ønsket som venter, står etterpå."""

    @staticmethod
    def _oenskene(l):
        return l._t.execute("SELECT handling, symbol FROM oenske ORDER BY id").fetchall()

    def test_samme_aksje_to_ganger_avvises(self, nitten):
        """Ville feilet hvis en ferdig liste med samme kode to ganger ble
        tatt i bruk."""
        l = lager(nitten)
        l.folg("T19", "Helse")
        foer = self._oenskene(l)
        with pytest.raises(ListaErFull):
            l.bruk_liste([("T01", "Kraft"), ("T01", "Kraft")])
        assert self._oenskene(l) == foer

    def test_en_bransje_utenfor_de_13_avvises(self, nitten):
        """Ville feilet hvis bruk_liste godtok en bransje som ikke er blant
        de 13 i designregler.md §4, eller skrev noe før den avviste."""
        l = lager(nitten)
        l.folg("T19", "Helse")
        foer = self._oenskene(l)
        assert "Ukjent" not in BRANSJENE
        with pytest.raises(UgyldigValg):
            l.bruk_liste([("T01", "Kraft"), ("T02", "Ukjent")])
        assert self._oenskene(l) == foer

    def test_en_kode_utenfor_boerslista_avvises(self, nitten):
        """Ville feilet hvis bruk_liste godtok en kode som ikke står i lista
        over Oslo Børs (boersliste), eller skrev noe før den avviste."""
        l = lager(nitten)
        l.folg("T19", "Helse")
        foer = self._oenskene(l)
        with pytest.raises(UgyldigValg):
            l.bruk_liste([("T01", "Kraft"), ("FINNESIKKE", "Kraft")])
        assert self._oenskene(l) == foer


class TestSiden:
    def test_ferdige_lister_i_min_liste(self, klient, monkeypatch):  # noqa: F811
        """Ville feilet hvis siden viste en liste vi ikke har målt."""
        import lagring_sqlite

        maal(lagring_sqlite.BASE_STI, [("NYA", 50e6), ("NYB", 2e6)])
        monkeypatch.setattr(ferdige_lister, "BRANSJE", {"NYA": "Kraft", "NYB": "Kraft", "NYC": "Helse"})
        side = klient.get("/min-liste").data.decode("utf-8")
        assert "Start fra en ferdig liste" in side
        assert re.search(r"Kraft <span class=\"antall\">2</span>", side) and "Helse <span" not in side
        ferdig = side.split('id="ferdige-lister"', 1)[1]
        # Gjennomgangen (BH9): merket står ved NYB, som er under 32 MNOK, og ikke ved NYA.
        assert re.search(r"NYB</span> <span class=\"utenformerke\">Utenfor målingen", ferdig)
        assert not re.search(r"NYA</span> <span class=\"utenformerke\">", ferdig)
        # BH3: hva knappen gjør, før den trykkes.
        assert "Lista di blir disse 2 aksjene ved neste henting, og 15 aksjer som er i lista nå, fjernes." in ferdig
        assert "er ikke et råd om hva du bør følge" in ferdig
        svar = klient.post("/ferdig-liste", data={"bransje": "Kraft"})
        assert svar.status_code == 303
        t = sqlite3.connect(lagring_sqlite.BASE_STI)
        oensker = t.execute("SELECT handling, symbol FROM oenske WHERE tatt_i_bruk IS NULL ORDER BY id").fetchall()
        t.close()
        assert [s for h, s in oensker if h == "folg"] == ["NYA", "NYB"] and len(oensker) == 17
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
        assert (
            f"Bare aksjene som fikk 3 av 3 med retning {retning}. Filteret viser hva sjekkene ga, og er ikke et "
            "råd om å kjøpe eller selge." in filtrert
        )

    def test_filteret_med_sortering(self, demoklient):
        """Gjennomgangen (BH9): ville feilet hvis filteret ikke gjaldt den
        sorterte lista, eller endret rekkefølgen i den."""
        side, base = demoklient
        sortert = _symbolene(side.get("/?sorter=endring&orden=synkende").data.decode("utf-8"))
        filtrert = _symbolene(side.get("/?sorter=endring&orden=synkende&signal=negativ").data.decode("utf-8"))
        assert filtrert and filtrert == [s for s in sortert if s in set(filtrert)]
        assert set(filtrert) == set(_symbolene(side.get("/?signal=negativ").data.decode("utf-8")))

    def test_bare_innenfor_lista_som_vises(self, demoklient):
        """Ville feilet hvis filteret i Min liste viste aksjer som ikke er merket."""
        side, _ = demoklient
        merket = _symbolene(side.get("/min-liste").data.decode("utf-8"))
        alle_negative = set(_symbolene(side.get("/?signal=negativ").data.decode("utf-8")))
        # BH9: nøyaktig de merkede blant dem med 3 av 3 negativ, i samme rekkefølge.
        assert _symbolene(side.get("/min-liste?signal=negativ").data.decode("utf-8")) == [
            s for s in merket if s in alle_negative
        ]
        assert set(_symbolene(side.get("/min-liste?signal=positiv").data.decode("utf-8"))) <= set(merket)

    def test_en_annen_verdi_filtrerer_ikke(self, demoklient):
        side, _ = demoklient
        assert _symbolene(side.get("/?signal=kjop").data.decode("utf-8")) == _symbolene(
            side.get("/").data.decode("utf-8")
        )


def _h1(side: str) -> str:
    return re.sub(r"<[^>]+>", "", side.split("<h1", 1)[1].split("</h1>", 1)[0]).split(">", 1)[1].strip()


class TestEtterGjennomgangen:
    def test_overskriften_endres_ikke_av_filteret(self, demoklient):
        """ECH1, VG1: ville feilet hvis filteret endret «N av M skilte seg ut»."""
        side, _ = demoklient
        for sti in ("/", "/min-liste"):
            uten = side.get(sti).data.decode("utf-8")
            for retning in ("positiv", "negativ"):
                med = side.get(f"{sti}?signal={retning}").data.decode("utf-8")
                assert _h1(med) == _h1(uten), (sti, retning)

    def test_min_liste_viser_bare_de_merkede(self, demoklient):
        """VG2, ECH2: ville feilet hvis filteret i Min liste viste en aksje
        som ikke er merket, eller sa at lista er tom."""
        side, base = demoklient
        negative = _symbolene(side.get("/?signal=negativ").data.decode("utf-8"))
        t = sqlite3.connect(base)
        with t:
            t.execute("DELETE FROM min_liste WHERE symbol IN (%s)" % ",".join("?" * len(negative)), negative)
        t.close()
        min_liste = side.get("/min-liste?signal=negativ").data.decode("utf-8")
        assert _symbolene(min_liste) == []
        assert "Ingen av aksjene her fikk det." in min_liste
        assert "Ingen aksjer i Min liste ennå" not in min_liste

    def test_knappene_og_lenkene(self, demoklient):
        """VG7: ville feilet hvis knappene fikk andre ord, eller lenkene mistet
        resten av adressen."""
        side, _ = demoklient
        html = side.get("/min-liste?sorter=endring&orden=synkende&signal=positiv").data.decode("utf-8")
        nav = html.split('<nav class="signalfilter"', 1)[1].split("</nav>", 1)[0]
        assert re.findall(r">([^<]+)</a>", nav) == ["Alle", "3 av 3 positiv", "3 av 3 negativ"]
        assert 'href="/min-liste?sorter=endring&amp;orden=synkende&amp;signal=positiv" aria-current="true"' in nav
        assert 'href="/min-liste?sorter=endring&amp;orden=synkende">Alle' in nav

    def test_demoen_har_kraft_og_eiendom(self, demoklient):
        """VG10: hjelpen og README-en sier det. Story 8.11b (spørsmål 8):
        demoen har også listene for bransjene til de 15 oppdiktede
        selskapene, i rekkefølgen fra designregler.md §4."""
        side, _ = demoklient
        html = side.get("/min-liste").data.decode("utf-8").split('id="ferdige-lister"', 1)[1]
        navn = re.findall(r"</svg>(\w+) <span class=\"antall\">", html)
        assert {"Eiendom", "Kraft"} <= set(navn) and len(navn) == 9
        assert navn == [b for b in BRANSJENE if b in navn]


def test_bare_siste_maaling_og_bare_boerslista(tmp_path, monkeypatch):
    """VG3: ville feilet hvis en eldre måling ble brukt når den siste har
    feil, eller en aksje som ikke står i lista over Oslo Børs, kom med."""
    base = tmp_path / "ose.db"
    med_boersen(base, NITTEN[:2])
    monkeypatch.setattr(ferdige_lister, "BRANSJE", {"T01": "Kraft", "T02": "Kraft", "T99": "Kraft"})
    maal(base, [("T01", 5e6), ("T02", 6e6), ("T99", 7e6)])
    t = sqlite3.connect(base)
    with t:
        t.execute(
            "INSERT INTO omsetning (symbol, maalt, fra, til, handelsdager, dager_uten_volum, rader_uten_tall, "
            "median_omsetning, feil) VALUES ('T02', '2026-10-29T20:00:00+00:00', '2026-07-29', '2026-10-29', 0, 0, "
            "0, NULL, 'ingen kurser')"
        )
    t.close()
    assert [a.symbol for a in ferdige_lister.lister(aapne_base(base))["Kraft"]] == ["T01"]
