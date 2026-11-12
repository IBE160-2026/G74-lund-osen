"""Story 8.28: «De 15 mest omsatte» som ferdig liste (FR-412).

Gruppens svar 12.11 kl. 20:04 (spørsmål 15 i 9.11): lista står i FR-412 og
bygges som egen story. De mest omsatte på hele børsen, fra den samme målingen
som bransjelistene (ferdige_lister.py), bare målte aksjer, og uten kravet om
åtte bransjer. Hver test lager sin egen base under tmp_path (regel 22), og
ingen test gjør nettkall (AD-8).
"""

import re
import sqlite3

import ferdige_lister
from lagring_sqlite import aapne_base
from test_ferdige_lister import demoklient, maal  # noqa: F401  (fiksturen)
from test_valg import klient, med_boersen, stier  # noqa: F401  (fiksturene)
from valg import BRANSJENE

TJUE = [(f"M{i:02d}", f"Målt {i} ASA") for i in range(1, 21)]


def _base(tmp_path, monkeypatch):
    """20 målte aksjer i fire bransjer, med M01 høyest, og M20 uten bransje."""
    base = tmp_path / "ose.db"
    med_boersen(base, TJUE)
    bransjer = ("Energi", "Finans", "Sjømat", "Kraft")
    monkeypatch.setattr(ferdige_lister, "BRANSJE", {k: bransjer[i % 4] for i, (k, _) in enumerate(TJUE) if k != "M20"})
    maal(base, [(k, 1e6 * (100 - i)) for i, (k, _) in enumerate(TJUE)])
    return base


class TestLista:
    def test_de_15_med_hoeyest_omsetning_paa_hele_boersen(self, tmp_path, monkeypatch):
        """Ville feilet hvis lista hadde flere eller færre enn 15 når flere er
        målt, ikke sto med høyest omsetning først, bare hadde én bransje, eller
        en aksje sto uten sin egen bransje."""
        lista = ferdige_lister.mest_omsatte(aapne_base(_base(tmp_path, monkeypatch)))
        assert [a.symbol for a in lista] == [k for k, _ in TJUE[:15]]
        assert [a.median for a in lista] == sorted((a.median for a in lista), reverse=True)
        assert len({a.bransje for a in lista}) == 4
        assert all(a.bransje in BRANSJENE and a.bransje == ferdige_lister.BRANSJE[a.symbol] for a in lista)
        assert ferdige_lister.MEST_OMSATTE_ANTALL == 15 and ferdige_lister.MEST_OMSATTE == "De 15 mest omsatte"

    def test_bare_maalte_med_tall_og_en_bransje(self, tmp_path, monkeypatch):
        """Ville feilet hvis en aksje som ikke er målt, ble målt med feil,
        eller ikke har en bransje (og derfor ikke kan følges), sto i lista."""
        base = tmp_path / "ose.db"
        med_boersen(base, TJUE[:4])
        monkeypatch.setattr(ferdige_lister, "BRANSJE", {"M01": "Kraft", "M02": "Kraft", "M03": "Kraft"})
        maal(base, [("M01", 5e6), ("M02", None), ("M04", 9e6)])
        assert [a.symbol for a in ferdige_lister.mest_omsatte(aapne_base(base))] == ["M01"]

    def test_samme_maaling_som_bransjelistene(self, tmp_path, monkeypatch):
        """Ville feilet hvis lista regnet omsetningen på en annen måte enn
        bransjelistene: hver aksje har samme median i begge."""
        tilkobling = aapne_base(_base(tmp_path, monkeypatch))
        i_bransjene = {a.symbol: a.median for liste in ferdige_lister.lister(tilkobling).values() for a in liste}
        for a in ferdige_lister.mest_omsatte(tilkobling):
            assert i_bransjene[a.symbol] == a.median

    def test_uten_base_eller_tabeller_er_lista_tom(self, tmp_path):
        """Ville feilet hvis en base uten tabellene ga en feil i stedet for
        ingen liste."""
        assert ferdige_lister.mest_omsatte(None) == []
        assert ferdige_lister.mest_omsatte(sqlite3.connect(tmp_path / "tom.db")) == []


class TestSidene:
    @staticmethod
    def _maalt(monkeypatch):
        import lagring_sqlite

        maal(lagring_sqlite.BASE_STI, [("NYA", 50e6), ("NYB", 2e6)])
        monkeypatch.setattr(ferdige_lister, "BRANSJE", {"NYA": "Kraft", "NYB": "Helse"})
        return lagring_sqlite.BASE_STI

    def test_knappen_staar_foerst_med_antallet(self, klient, monkeypatch):  # noqa: F811
        """Ville feilet hvis knappen manglet, ikke sto først blant de ferdige
        listene, eller ikke hadde navnet og antallet."""
        self._maalt(monkeypatch)
        side = klient.get("/min-liste").data.decode("utf-8")
        delen = side.split('<h3 id="ferdige-lister">Start fra en ferdig liste</h3>', 1)[1].split("</ul>", 1)[0]
        knappene = re.findall(r'<a class="knapp ferdigknapp" href="([^"]+)"', delen)
        assert knappene[0] == "/ferdig-liste?liste=mest-omsatte"
        assert (
            '<a class="knapp ferdigknapp" href="/ferdig-liste?liste=mest-omsatte">De 15 mest omsatte '
            '<span class="antall">2</span><span class="skjult"> aksjer</span></a>'
        ) in delen

    def test_er_du_sikker_og_hver_aksje_med_sin_bransje(self, klient, monkeypatch):  # noqa: F811
        """Ville feilet hvis siden ikke sa hele børsen, ikke viste bransjen
        ved hver aksje, skrev før skjemaet ble sendt, eller hvis «Bruk denne
        lista» fulgte aksjene med en annen bransje enn deres egen."""
        sti = self._maalt(monkeypatch)
        foer = sti.read_bytes()
        html = klient.get("/ferdig-liste?liste=mest-omsatte").data.decode("utf-8")
        assert sti.read_bytes() == foer
        assert "Lista di blir de 2 mest omsatte aksjene på hele børsen ved neste henting" in html
        assert "<title>Er du sikker? De 15 mest omsatte — OSE Signal</title>" in html
        assert re.search(r"NYB · <svg[^>]*>.*?</svg>Helse</span> <span class=\"utenformerke\">", html, re.S)
        assert "er ikke et råd om hva du bør følge" in html
        assert '<input type="hidden" name="liste" value="mest-omsatte">' in html
        assert klient.post("/ferdig-liste", data={"liste": "mest-omsatte"}).status_code == 303
        t = sqlite3.connect(sti)
        folg = t.execute("SELECT symbol, sektor FROM oenske WHERE handling = 'folg' ORDER BY id").fetchall()
        t.close()
        assert folg == [("NYA", "Kraft"), ("NYB", "Helse")]

    def test_uten_maalte_aksjer_gir_404_og_400(self, klient):  # noqa: F811
        """Ville feilet hvis en tom liste ga en side med en knapp, eller kunne
        brukes."""
        assert klient.get("/ferdig-liste?liste=mest-omsatte").status_code == 404
        assert klient.post("/ferdig-liste", data={"liste": "mest-omsatte"}).status_code == 400

    def test_demoen_har_lista(self, demoklient):  # noqa: F811
        """Likt i demoen og den ekte versjonen: ville feilet hvis demoen ikke
        hadde lista med 15 aksjer, eller siden for den ikke virket."""
        side, _ = demoklient
        html = side.get("/min-liste").data.decode("utf-8")
        assert re.search(r'De 15 mest omsatte <span class="antall">15</span>', html)
        assert side.get("/ferdig-liste?liste=mest-omsatte").status_code == 200
