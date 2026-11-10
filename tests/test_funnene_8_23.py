"""Story 8.23: funnene fra brukertesten 10.11 (del A), med tilleggene 1–3 og
tillegget om demoen. Spesifikasjonen er spec-8-23-funnene-fra-brukertesten.md.

Testene bruker demobasen, laget i tmp_path, som test_funnene_8_2b.py, og alt
skal kunne ses i demoen (tillegget om demoen, gruppens svar kl. 15:57).
"""

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

import app as app_modul
import demo
from lagring_sqlite import demo_sti

ROT = Path(__file__).resolve().parent.parent
STIL = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))


@pytest.fixture(scope="module")
def mal(tmp_path_factory):
    sti = tmp_path_factory.mktemp("demomal") / "demo.db"
    demo.lag_demobase(sti, skriv=lambda _: None)
    return sti


@pytest.fixture
def klient(mal, monkeypatch):
    sti = demo_sti()
    sti.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(mal, sti)
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    return app_modul.app.test_client()


def _html(klient, sti: str) -> str:
    svar = klient.get(sti)
    assert svar.status_code == 200, sti
    return svar.get_data(as_text=True)


def _merk(klient, symbol, til, tilbake):
    return klient.post("/min-liste/merk", data={"symbol": symbol, "til": til, "tilbake": tilbake})


def _radene(html: str) -> list[str]:
    """Symbolene i tabellen, i rekkefølgen de står."""
    tabell = html.split('id="aksjene"', 1)[1].split("</table>", 1)[0]
    return re.findall(r'<form id="rad-([A-Z]+)"', tabell)


def _thead(html: str) -> str:
    return html.split("<thead>", 1)[1].split("</thead>", 1)[0]


class TestSorteringenBlirVedTabellen:
    """A2: sorteringen ved klikk i kolonneraden blir stående ved tabellen."""

    @pytest.mark.parametrize("sti", ["/", "/min-liste", "/min-liste?vis=alle", "/?vis=min"])
    def test_lenkene_i_kolonneraden_gaar_til_tabellen(self, klient, sti):
        """Ville feilet hvis en lenke i kolonneraden gikk til toppen av siden,
        så man måtte rulle ned til tabellen igjen etter hvert klikk."""
        lenker = re.findall(r'<a class="sorter[^"]*" href="([^"]+)"', _thead(_html(klient, sti)))
        assert len(lenker) == 5
        assert all(lenke.endswith("#aksjene") for lenke in lenker), lenker

    def test_standard_rekkefoelge_og_filteret_gaar_til_tabellen(self, klient):
        """Ville feilet hvis «Standard rekkefølge» eller knappene i filteret
        sendte til toppen."""
        html = _html(klient, "/min-liste?sorter=kurs&orden=synkende")
        assert '<a href="/min-liste#aksjene">Standard rekkefølge</a>' in html
        nav = html.split('<nav class="signalfilter"', 1)[1].split("</nav>", 1)[0]
        assert all(h.endswith("#aksjene") for h in re.findall(r'href="([^"]+)"', nav))


class TestFilteretMedAntallet:
    """A8: antallet står på knappene, og ved 0 står hvor mange som fikk 2 av 3
    i samme retning, med en lenke."""

    @pytest.mark.parametrize("sti", ["/", "/min-liste"])
    @pytest.mark.parametrize("retning", ["positiv", "negativ"])
    def test_antallet_paa_knappen_er_radene_filteret_gir(self, klient, sti, retning):
        """Ville feilet hvis antallet på knappen var et annet enn radene man
        får ved å trykke på den, eller talte aksjer utenfor lista som vises."""
        html = _html(klient, sti)
        nav = html.split('<nav class="signalfilter"', 1)[1].split("</nav>", 1)[0]
        antall = int(re.search(rf"3 av 3 {retning} \((\d+)\)", nav).group(1))
        filtrert = _html(klient, f"{sti}?signal={retning}")
        assert len(_radene(filtrert)) == antall

    def test_ved_0_staar_2_av_3_med_lenke(self, klient):
        """Ville feilet hvis et tomt filter bare sa «Ingen», eller lenken viste
        andre enn dem som fikk 2 av 3 i samme retning."""
        # I Min liste i demoen fikk bare KVST 3 av 3 positiv; uten den er filteret tomt.
        _merk(klient, "KVST", "fjern", "/min-liste")
        html = _html(klient, "/min-liste?signal=positiv")
        tekst = html.split('<p class="filtertekst">', 1)[1].split("</p>", 1)[0]
        assert "Ingen av aksjene her fikk det." in tekst
        treff = re.search(r'(\d+) fikk 2 av 3 positiv: <a href="([^"]+)">se (?:den|dem)</a>', tekst)
        if treff is None:
            assert "Ingen fikk 2 av 3 positiv heller." in tekst
            return
        antall, adresse = int(treff.group(1)), treff.group(2).replace("&amp;", "&")
        assert "signal=positiv-2" in adresse and adresse.endswith("#aksjene")
        neste = _html(klient, adresse.removesuffix("#aksjene"))
        assert len(_radene(neste)) == antall > 0
        assert "Bare aksjene som fikk 2 av 3 med retning positiv." in neste

    def test_ingen_tekst_om_2_av_3_naar_filteret_gir_noe(self, klient):
        """Ville feilet hvis lenken til 2 av 3 sto også når 3 av 3 ga rader."""
        html = _html(klient, "/?signal=positiv")
        assert _radene(html)
        assert "fikk 2 av 3" not in html.split('<p class="filtertekst">', 1)[1].split("</p>", 1)[0]


class TestOverskriftenIMinListe:
    """Tillegg 1 (gruppens funn kl. 14:15): overskriften stemmer med tabellen."""

    def test_med_alle_staar_begge_tallene(self, klient):
        """Ville feilet hvis overskriften med «Alle» bare talte Min liste, mens
        tabellen viser alle. BRFE skilte seg ut og er i lista i demoen."""
        assert '<h1 class="overskrift"><mark>7 av 15</mark> skilte seg ut fredag, 3 av dem i Min liste</h1>' in _html(
            klient, "/min-liste?vis=alle"
        )
        _merk(klient, "BRFE", "fjern", "/min-liste?vis=alle")
        assert "<mark>7 av 15</mark> skilte seg ut fredag, 2 av dem i Min liste" in _html(klient, "/min-liste?vis=alle")

    def test_med_min_liste_som_foer(self, klient):
        """Ville feilet hvis overskriften med «Min liste» ble endret."""
        assert '<h1 class="overskrift"><mark>3 av 5 i Min liste</mark> skilte seg ut fredag</h1>' in _html(
            klient, "/min-liste"
        )


class TestMinListePaaOversikten:
    """Tillegg 2 (B7): «Min liste» over «Aksjene» filtrerer tabellen på
    oversikten og beholder perioden og sorteringen."""

    def test_bare_de_merkede_paa_oversikten(self, klient):
        """Ville feilet hvis valget sendte til siden Min liste, eller viste
        andre enn de merkede."""
        html = _html(klient, "/?vis=min")
        assert set(_radene(html)) == set(demo.MERKET_I_DEMOEN)
        assert '<div class="aksjetopp">' in html and '<section class="hovedindeks"' in html
        topp = html.split('<div class="aksjetopp">', 1)[1].split("</nav>", 1)[0]
        assert re.search(r'href="/\?vis=min#aksjene" aria-current="true">Min liste', topp)

    def test_beholder_perioden_og_sorteringen(self, klient):
        """Ville feilet hvis sorteringen, perioden eller «Standard rekkefølge»
        mistet valget."""
        html = _html(klient, "/?vis=min&periode=1-uke&sorter=kurs&orden=stigende")
        assert set(_radene(html)) == set(demo.MERKET_I_DEMOEN)
        lenker = re.findall(r'<a class="sorter[^"]*" href="([^"]+)"', _thead(html))
        assert all("vis=min" in h and "periode=1-uke" in h for h in lenker), lenker
        assert '<a href="/?vis=min&amp;periode=1-uke#aksjene">Standard rekkefølge</a>' in html
        assert '<input type="hidden" name="vis" value="min">' in html

    def test_stjernen_sender_tilbake_til_valget(self, klient):
        """Ville feilet hvis stjernen tok valget bort, eller sendte til en rad
        som ikke står der lenger."""
        svar = _merk(klient, "BRFE", "fjern", "/?vis=min&sorter=kurs&orden=stigende")
        assert svar.status_code == 303
        assert svar.headers["Location"].endswith("/?vis=min&sorter=kurs&orden=stigende#aksjene")

    def test_knappen_i_stripa_gaar_til_siden(self, klient):
        """Ville feilet hvis knappen «Min liste» i stripa ble et filter."""
        stripa = _html(klient, "/").split('<nav class="rad sider"', 1)[1].split("</nav>", 1)[0]
        assert 'href="/min-liste"' in stripa
