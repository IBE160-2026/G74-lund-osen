"""Tester for Min liste - story 8.3, FR-101, FR-102, AD-3, AD-10, AD-16, AD-21.

Merkingen er et eget datasett, tabellen min_liste fra 0007, med porten
Minlistelager og webserveren som eneste skriver. Testene bruker basen i
tmp_path (conftest.py) og demobasen fra test_demo, aldri data/db/ (regel 22).
"""

import re
import sqlite3
from pathlib import Path

import pytest

import app as app_modul
import lagring_sqlite
from lagring_sqlite import SqliteMinlistelager, aapne_base, demo_sti
from markedsoversikt import SORTERBARE, STIGENDE, SYNKENDE
from minliste import Minlistelager, MinneMinlistelager, UkjentAksje
from test_app import _deler_i_rekkefoelge, _regel, _stil, fyll_basen, serie
from test_demo import demobase, fast_klokke, klient, mal  # noqa: F401
from test_utseende import _farger, _kontrast

ROT = Path(__file__).resolve().parent.parent
MIGRASJONEN = ROT / "src" / "migrasjoner" / "0007_min_liste.sql"
MERKET_I_DEMOEN = ("BRFE", "KVST", "NLYS", "LSTF", "SGNT")


@pytest.fixture
def demo(klient, demobase, fast_klokke, monkeypatch):  # noqa: F811 - fiksturer fra test_demo
    """Klienten mot demobasen, med de fem som er merket når demoen starter."""
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    return klient


def _base(tmp_path: Path, navn: str = "ose.db") -> Path:
    sti = tmp_path / navn
    aapne_base(sti).close()
    return sti


def _merk(k, symbol, til="merk", tilbake="/", **hoder):
    return k.post("/min-liste/merk", data={"symbol": symbol, "til": til, "tilbake": tilbake}, headers=hoder or None)


def _merket(html: str) -> list[str]:
    """Symbolene med fylt stjerne, i rekkefølgen radene står."""
    return re.findall(r'name="symbol" value="([A-Z0-9]+)"><input type="hidden" name="til" value="fjern"', html)


def _rekkefoelge(html: str) -> list[str]:
    ut, oevrige = _deler_i_rekkefoelge(html)
    return ut + oevrige


def _i_fila(sti: Path) -> set[str]:
    """Symbolene i min_liste, lest rett fra fila uten porten (mutanten M1)."""
    c = sqlite3.connect(f"file:{sti.as_posix()}?mode=ro", uri=True)
    try:
        return {s for (s,) in c.execute("SELECT symbol FROM min_liste")}
    finally:
        c.close()


def _lagret_for(symboler: list[str]) -> None:
    """Kurser i den ekte basen i tmp_path for symbolene, så de har en rad."""
    fyll_basen({s: serie([100.0] * 60 + [101.0]) for s in symboler})


def _innhold(sti: Path) -> dict[str, list]:
    """Hver tabell i basen utenom min_liste, rad for rad, og skjemaet."""
    c = sqlite3.connect(f"file:{sti.as_posix()}?mode=ro", uri=True)
    try:
        tabeller = [t for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")]
        ut = {t: c.execute(f'SELECT * FROM "{t}" ORDER BY rowid').fetchall() for t in tabeller if t != "min_liste"}
        ut["sqlite_master"] = c.execute("SELECT type, name, sql FROM sqlite_master ORDER BY name").fetchall()
        ut["application_id"] = c.execute("PRAGMA application_id").fetchall()
        return ut
    finally:
        c.close()


class TestLagringen:
    """Punkt a: tabellen, triggeren og porten."""

    def test_tabellen_har_bare_symbolet(self, tmp_path):
        """Ville feilet hvis min_liste fikk en kolonne for antall, beløp eller
        kurs: da er det en personlig portefølje, som er utenfor v1."""
        c = sqlite3.connect(_base(tmp_path))
        try:
            kolonner = [k[1] for k in c.execute("PRAGMA table_info(min_liste)")]
        finally:
            c.close()
        assert kolonner == ["symbol"]
        tekst = MIGRASJONEN.read_text(encoding="utf-8").lower()
        skjema = tekst.split("create table min_liste", 1)[1].split(");", 1)[0]
        for ord_ in ("antall", "beloep", "beløp", "kurs", "pris", "verdi"):
            assert ord_ not in skjema, ord_

    def test_merkingen_overlever_en_omstart(self, tmp_path):
        """Ville feilet hvis merkingen bare lå i minnet: en ny tilkobling, som
        etter en omstart, ser den samme lista."""
        sti = _base(tmp_path)
        c = aapne_base(sti)
        try:
            SqliteMinlistelager(c).merk("EQNR")
            SqliteMinlistelager(c).merk("MOWI")
            SqliteMinlistelager(c).fjern("MOWI")
        finally:
            c.close()
        c = aapne_base(sti, kjoer_migrasjoner=False, skrivebeskyttet=True)
        try:
            assert SqliteMinlistelager(c).merkede() == {"EQNR"}
        finally:
            c.close()
        # Mutanten M1: porten kunne husket lista i prosessen. Fila har den.
        assert _i_fila(sti) == {"EQNR"}

    def test_merkingen_overlever_en_omstart_av_webserveren(self, klient, monkeypatch):  # noqa: F811
        """Ville feilet hvis stjernen bare ble husket i prosessen: etter at
        webserveren har glemt basen, er aksjen fortsatt merket."""
        monkeypatch.delenv(app_modul.I_DEMO, raising=False)
        assert _merk(klient, "DNB").status_code == 303
        monkeypatch.setattr(app_modul, "_migrerte", set())
        ny = app_modul.app.test_client()
        assert _i_fila(lagring_sqlite.BASE_STI) == {"DNB"}
        assert ny.get("/min-liste").status_code == 200
        # Gjennomgangen (BH12, VG10): og siden viser den, med fylt stjerne.
        _lagret_for(["DNB", "EQNR"])
        assert _merket(ny.get("/min-liste?vis=alle").data.decode("utf-8")) == ["DNB"]

    @pytest.mark.parametrize("symbol", ["XXX", "EQNR.OL", "eqnr", "", "EQNR "])
    def test_et_ukjent_symbol_avvises_i_porten(self, tmp_path, symbol):
        """Ville feilet hvis porten skrev et symbol som ikke står i lista, også
        tickeren og små bokstaver."""
        c = aapne_base(_base(tmp_path))
        try:
            lager = SqliteMinlistelager(c)
            with pytest.raises(UkjentAksje):
                lager.merk(symbol)
            with pytest.raises(UkjentAksje):
                lager.fjern(symbol)
            assert c.execute("SELECT COUNT(*) FROM min_liste").fetchone()[0] == 0
        finally:
            c.close()
        minne = MinneMinlistelager(["EQNR", "DNB"])
        with pytest.raises(UkjentAksje):
            minne.merk(symbol)
        assert minne.merkede() == frozenset()

    def test_et_ukjent_symbol_avvises_i_basen(self, tmp_path):
        """En INSERT eller UPDATE utenom porten med et symbol som ikke står i
        aksje, stoppes av basen. Ville feilet hvis triggerne i 0007 manglet."""
        c = sqlite3.connect(_base(tmp_path), isolation_level=None)
        try:
            with pytest.raises(sqlite3.IntegrityError, match="ukjent aksje i min_liste"):
                c.execute("INSERT INTO min_liste (symbol) VALUES ('XXX')")
            with pytest.raises(sqlite3.IntegrityError, match="ukjent aksje i min_liste"):
                c.execute("INSERT INTO min_liste (symbol) VALUES (NULL)")
            c.execute("INSERT INTO min_liste (symbol) VALUES ('EQNR')")
            with pytest.raises(sqlite3.IntegrityError, match="ukjent aksje i min_liste"):
                c.execute("UPDATE min_liste SET symbol = 'XXX'")
            assert c.execute("SELECT symbol FROM min_liste").fetchall() == [("EQNR",)]
        finally:
            c.close()

    def test_lista_er_en_parameter_ogsaa_med_faerre_enn_15(self, tmp_path):
        """Føringen 30.09 under AD-21: koden antar aldri at det er 15. Ville
        feilet hvis porten slo opp i AKSJEUNIVERS i stedet for i aksje i
        basen, eller i lista minneutgaven får."""
        sti = _base(tmp_path)
        c = sqlite3.connect(sti, isolation_level=None)
        try:
            c.execute("DELETE FROM aksje WHERE symbol NOT IN ('EQNR', 'DNB', 'KOG')")
        finally:
            c.close()
        c = aapne_base(sti)
        try:
            lager = SqliteMinlistelager(c)
            lager.merk("KOG")
            with pytest.raises(UkjentAksje):
                lager.merk("MOWI")
            assert lager.merkede() == {"KOG"}
        finally:
            c.close()
        minne = MinneMinlistelager(["A", "B"])
        minne.merk("B")
        minne.merk("B")
        assert minne.merkede() == {"B"}
        minne.fjern("B")
        minne.fjern("B")
        assert minne.merkede() == frozenset()
        with pytest.raises(UkjentAksje):
            minne.merk("EQNR")

    def test_begge_lagrene_oppfyller_porten(self, tmp_path):
        """AD-3: én port per datasett, med samme kontrakt i minnet og i SQLite."""
        c = aapne_base(_base(tmp_path))
        try:
            assert isinstance(SqliteMinlistelager(c), Minlistelager)
        finally:
            c.close()
        assert isinstance(MinneMinlistelager(["EQNR"]), Minlistelager)

    def test_bare_0007_lager_tabellen(self):
        """AD-16: tabellen lages av en nummerert migrasjon, ikke i koden."""
        filer = sorted(p.name for p in MIGRASJONEN.parent.glob("*.sql") if "min_liste" in p.read_text(encoding="utf-8"))
        assert filer == ["0007_min_liste.sql"]
        assert "CREATE TABLE" not in (ROT / "src" / "lagring_sqlite.py").read_text(encoding="utf-8")

    def test_demoen_merker_fem_fra_begge_delene(self, demo):
        """Svaret kl. 10:29: demoen starter med fem merket. Ville feilet hvis
        alle fem sto i samme del av tabellen."""
        html = demo.get("/").data.decode("utf-8")
        ut, oevrige = _deler_i_rekkefoelge(html)
        merket = _merket(html)
        assert sorted(merket) == sorted(MERKET_I_DEMOEN)
        assert set(merket) & set(ut) and set(merket) & set(oevrige)

    def test_den_ekte_basen_starter_med_en_tom_liste(self, klient, monkeypatch):  # noqa: F811
        """Svaret kl. 10:29: den ekte starter tom. Ville feilet hvis 0007 la
        inn rader, eller demoens fem fulgte med."""
        monkeypatch.delenv(app_modul.I_DEMO, raising=False)
        klient.get("/")
        c = aapne_base(lagring_sqlite.BASE_STI, kjoer_migrasjoner=False, skrivebeskyttet=True)
        try:
            assert c.execute("SELECT COUNT(*) FROM min_liste").fetchone()[0] == 0
        finally:
            c.close()


class TestMerkingen:
    """Punkt b: POST-en, som bryteren for KI-teksten."""

    def test_merk_og_fjern_med_303_til_samme_side_med_sorteringen(self, demo):
        """Ville feilet hvis merkingen sendte til en annen side, mistet
        sorteringen eller svarte noe annet enn 303."""
        tilbake = "/min-liste?vis=alle&sorter=signal&orden=synkende"
        svar = _merk(demo, "HVDO", tilbake=tilbake)
        assert svar.status_code == 303
        # Gjennomgangen (BH5): tilbake til raden, med ankeret.
        assert svar.headers["Location"] == tilbake + "#rad-HVDO"
        assert 'id="rad-HVDO"' in demo.get(tilbake).data.decode("utf-8")
        assert "HVDO" in _merket(demo.get("/").data.decode("utf-8"))
        svar = _merk(demo, "HVDO", til="fjern", tilbake="/?sorter=kurs&orden=stigende")
        assert svar.status_code == 303 and svar.headers["Location"] == "/?sorter=kurs&orden=stigende#rad-HVDO"
        assert "HVDO" not in _merket(demo.get("/").data.decode("utf-8"))

    def test_en_post_fra_en_annen_side_gir_403(self, demo):
        """Ingenting er skrevet etter 403. Ville feilet hvis Origin-sjekken
        manglet, så en annen side kunne merket for brukeren."""
        foer = _innhold(demo_sti()), _merket(demo.get("/").data.decode("utf-8"))
        for opphav in ("http://evil.example", "http://localhost.evil.example", "null"):
            assert _merk(demo, "HVDO", Origin=opphav).status_code == 403, opphav
        assert (_innhold(demo_sti()), _merket(demo.get("/").data.decode("utf-8"))) == foer
        assert _merk(demo, "HVDO", Origin="http://localhost").status_code == 303

    @pytest.mark.parametrize(
        ("tilbake", "forventet"),
        [
            ("https://evil.example/", "/"),
            ("//evil.example/", "/"),
            ("/\t/evil.example", "/"),
            ("/\\evil.example", "/"),
            ("/aksje/EQNR", "/"),
            ("/min-liste/merk", "/"),
            ("javascript:alert(1)", "/"),
            ("", "/"),
            ("/?sorter=ukjent&orden=synkende", "/"),
            ("/?vis=alle", "/"),
            ("/min-liste?vis=alle", "/min-liste?vis=alle"),
            ("/min-liste?sorter=retning&orden=stigende", "/min-liste?sorter=retning&orden=stigende"),
            ("/min-liste?sorter=signal&sorter=kurs&orden=stigende", "/min-liste"),
        ],
    )
    def test_bare_egne_stier_tilbake(self, demo, tilbake, forventet):
        """Ville feilet hvis en fremmed adresse, en annen side eller et ukjent
        valg kom gjennom til Location."""
        svar = _merk(demo, "HVDO", tilbake=tilbake)
        assert svar.status_code == 303
        assert svar.headers["Location"] == forventet + "#rad-HVDO"

    def test_et_ukjent_symbol_eller_valg_gir_400(self, demo):
        """Ville feilet hvis ruta skrev et symbol som ikke står i aksje, eller
        tolket et ukjent «til» som merk."""
        foer = _innhold(demo_sti())
        assert _merk(demo, "EQNR").status_code == 400
        assert _merk(demo, "HVDO", til="slett").status_code == 400
        assert _innhold(demo_sti()) == foer

    def test_under_en_merking_skrives_bare_den_nye_tabellen(self, demo):
        """AD-3 og AD-10: webserveren skriver bare min_liste. Ville feilet hvis
        merkingen rørte en annen tabell, skjemaet eller merket i demobasen."""
        foer = _innhold(demo_sti())
        assert _merk(demo, "HVDO").status_code == 303
        assert _merk(demo, "BRFE", til="fjern").status_code == 303
        assert _innhold(demo_sti()) == foer
        c = sqlite3.connect(f"file:{demo_sti().as_posix()}?mode=ro", uri=True)
        try:
            assert {s for (s,) in c.execute("SELECT symbol FROM min_liste")} == (set(MERKET_I_DEMOEN) - {"BRFE"}) | {
                "HVDO"
            }
        finally:
            c.close()

    def test_sidene_skriver_aldri(self, demo):
        """Ville feilet hvis en GET skrev til basen, for eksempel ved å merke
        noe når siden vises."""
        foer = demo_sti().read_bytes()
        for adresse in ("/", "/min-liste", "/min-liste?vis=alle", "/aksje/KVST"):
            assert demo.get(adresse).status_code == 200, adresse
        assert demo_sti().read_bytes() == foer

    def test_ruta_henter_aldri(self):
        """AD-10: ruta som skriver, importerer og kaller ingenting som henter."""
        kilde = (ROT / "src" / "app.py").read_text(encoding="utf-8")
        ruta = kilde.split('@app.post("/min-liste/merk")', 1)[1].split("\n\n\n", 1)[0]
        for ord_ in ("requests", "fetch_prices", "eodhd", "urlopen", "hent_"):
            assert ord_ not in ruta, ord_


class TestSidene:
    """Punkt c: knapperaden, stjernen og Min liste."""

    def test_filteret_endrer_ikke_rekkefoelgen(self, demo):
        """FR-102: Min liste har samme rekkefølge som oversikten. Ville feilet
        hvis Min liste sorterte radene på nytt, eller «Alle» ga en annen
        rekkefølge. Mutanten M2: de fem i demoen står tilfeldigvis i
        alfabetisk rekkefølge i hver del, så Havdyp Olje og Trygghavn
        Forsikring merkes også, og da gir navnet en annen rekkefølge."""
        for symbol in ("HVDO", "TRHF"):
            assert _merk(demo, symbol).status_code == 303
        merket = (*MERKET_I_DEMOEN, "HVDO", "TRHF")
        oversikten = _rekkefoelge(demo.get("/").data.decode("utf-8"))
        alle = _rekkefoelge(demo.get("/min-liste?vis=alle").data.decode("utf-8"))
        lista = _rekkefoelge(demo.get("/min-liste").data.decode("utf-8"))
        assert alle == oversikten
        assert lista == [s for s in oversikten if s in merket]
        assert sorted(lista) == sorted(merket)
        navnene = re.findall(r'<a href="/aksje/[A-Z0-9]+">([^<]+)</a>', demo.get("/min-liste").data.decode("utf-8"))
        assert navnene != sorted(navnene), "testen må ha en liste der navnet gir en annen rekkefølge"

    @pytest.mark.parametrize("kolonne", sorted(SORTERBARE))
    @pytest.mark.parametrize("orden", [SYNKENDE, STIGENDE])
    def test_filteret_endrer_ikke_rekkefoelgen_sortert(self, demo, kolonne, orden):
        """Story 8.15: også sortert er Min liste oversikten med bare de
        merkede, i samme rekkefølge innenfor hver del. Ville feilet hvis Min
        liste eller «Alle» sorterte på noe annet enn oversikten."""
        valg = f"sorter={kolonne}&orden={orden}"
        ut, oevrige = _deler_i_rekkefoelge(demo.get(f"/?{valg}").data.decode("utf-8"))
        l_ut, l_oevrige = _deler_i_rekkefoelge(demo.get(f"/min-liste?{valg}").data.decode("utf-8"))
        assert l_ut == [s for s in ut if s in MERKET_I_DEMOEN]
        assert l_oevrige == [s for s in oevrige if s in MERKET_I_DEMOEN]
        assert _deler_i_rekkefoelge(demo.get(f"/min-liste?vis=alle&{valg}").data.decode("utf-8")) == (ut, oevrige)

    def test_den_fylte_knappen_paa_hver_side(self, demo):
        """Ville feilet hvis knappen for siden man står på, ikke var fylt,
        eller en knapp var fylt på aksjesiden. Story 8.6: tre knapper, med
        «Børsometer» i midten."""
        forventet = {
            "/": "Markedsoversikt",
            "/boersometer": "Børsometer",
            "/min-liste": "Min liste",
            "/min-liste?vis=alle": "Min liste",
        }
        for adresse, fylt in forventet.items():
            stripa = demo.get(adresse).data.decode("utf-8").split("</header>", 1)[0]
            assert re.findall(r'class="sideknapp" href="[^"]*" aria-current="page">([^<]+)<', stripa) == [fylt]
            assert stripa.count('class="sideknapp"') == 3
        aksjesiden = demo.get("/aksje/KVST").data.decode("utf-8")
        stripa = aksjesiden.split("</header>", 1)[0]
        assert stripa.count('class="sideknapp"') == 3 and 'aria-current="page"' not in stripa
        # Aksjesiden beholder veien tilbake.
        assert '<a class="tilbake" href="/">Markedsoversikt</a>' in aksjesiden
        # Gjennomgangen 23.10 (BH8): også siden for en aksje uten kurser.
        uten = demo.get("/aksje/MTFJ").data.decode("utf-8")
        stripa = uten.split("</header>", 1)[0]
        assert stripa.count('class="sideknapp"') == 3 and 'aria-current="page"' not in stripa
        assert '<a class="tilbake" href="/">Markedsoversikt</a>' in uten

    def test_knapperaden_ogsaa_paa_feilsiden(self, demo):
        """Ville feilet hvis knapperaden bare sto på sidene med tabell."""
        demo_sti().write_bytes(b"ikke en sqlite-base" * 10)
        svar = demo.get("/min-liste")
        assert svar.status_code == 503
        stripa = svar.data.decode("utf-8").split("</header>", 1)[0]
        assert stripa.count('class="sideknapp"') == 3

    def test_stjernen_er_en_knapp_med_aria_pressed_og_navnet(self, demo):
        """Ville feilet hvis stjernen bare var et tegn, eller skjermleseren
        ikke hørte hvilken aksje den gjelder og om den er merket."""
        html = demo.get("/").data.decode("utf-8")
        celler = re.findall(r'<td class="selskap">(.*?)</td>', html, re.S)
        assert len(celler) == 14  # Matfjord Merkevarer har ingen kurser
        for celle in celler:
            navn = re.search(r'<a href="/aksje/[A-Z0-9]+">([^<]+)</a>', celle).group(1)
            assert celle.index("stjerneknapp") < celle.index('<a href="/aksje/')
            knapp = re.search(
                r'<button type="submit" class="stjerneknapp( merket)?" aria-pressed="(true|false)">', celle
            )
            assert knapp and (knapp.group(1) is not None) == (knapp.group(2) == "true")
            assert f'<span class="skjult">Min liste: {navn}</span>' in celle

    def test_fem_kolonner_og_forklaringen_under_selskap(self, demo):
        """FR-101: stjernen står i cellen for Selskap, så tabellen har fem
        kolonner. Ville feilet med en egen kolonne for stjernen."""
        for adresse in ("/", "/min-liste"):
            html = demo.get(adresse).data.decode("utf-8")
            thead = html.split("<thead>", 1)[1].split("</thead>", 1)[0]
            assert thead.count("<th") == 5
            assert '<span class="under">★ = Min liste</span></th>' in thead.split("</th>", 1)[0] + "</th>"
            rader = [r for r in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S) if '<td class="selskap">' in r]
            assert len(rader) == len(_rekkefoelge(html)) > 0
            for rad in rader:
                assert rad.count("<td") == 5

    def test_min_liste_har_overskriften_teksten_og_knappen_med_antallet(self, demo):
        """Ville feilet uten overskriften, teksten om at det er uten kall,
        eller antallet i «Alle / Min liste»."""
        html = demo.get("/min-liste").data.decode("utf-8")
        assert '<h1 class="overskrift">Min liste</h1>' in html
        assert html.count("<h1") == 1
        assert "Stjernen foran et selskap legger aksjen i lista" in html
        assert "koster ingen API-kall" in html
        assert re.search(r'Alle <span class="antall">15</span>', html)
        assert re.search(r'aria-current="true">Min liste <span class="antall">5</span>', html)
        assert "<title>Min liste — OSE Signal</title>" in html

    def test_den_tomme_lista_sier_hvordan_man_merker(self, demo):
        """Ville feilet hvis en tom liste viste en tom tabell uten forklaring."""
        for symbol in MERKET_I_DEMOEN:
            assert _merk(demo, symbol, til="fjern").status_code == 303
        html = demo.get("/min-liste").data.decode("utf-8")
        assert "Ingen aksjer i Min liste ennå" in html
        assert "Trykk på stjernen" in html
        assert "<table" not in html
        assert 'Min liste <span class="antall">0</span>' in html
        # Under «Alle» står tabellen, så man kan merke der.
        alle = demo.get("/min-liste?vis=alle").data.decode("utf-8")
        assert "<table" in alle and "Ingen aksjer i Min liste ennå" not in alle

    def test_min_liste_uten_kurser_i_basen(self, klient, monkeypatch):  # noqa: F811
        """En tom base gir beskjeden om hentingen, én h1 og ingen feil."""
        monkeypatch.delenv(app_modul.I_DEMO, raising=False)
        svar = klient.get("/min-liste")
        assert svar.status_code == 200
        html = svar.data.decode("utf-8")
        assert html.count("<h1") == 1 and "Ingen kurser i basen ennå" in html

    def test_kontrasten_til_stjernen(self, demo):
        """Stjernen er grafikk og trenger 3:1 mot kortet, både med omriss og
        fylt (WCAG 1.4.11). Ville feilet hvis stjernen fikk den lyse oransje,
        som har 1,9:1. Alle radene har kortet som bakgrunn."""
        stil = _stil(demo.get("/").data.decode("utf-8"))
        farger = _farger(stil)
        omriss = re.search(r"stroke: var\(--([a-z0-9-]+)\)", _regel(stil, "button.stjerneknapp svg"))
        fylt = _regel(stil, "button.stjerneknapp.merket svg")
        fyll = re.search(r"fill: var\(--([a-z0-9-]+)\)", fylt).group(1)
        strek = re.search(r"stroke: var\(--([a-z0-9-]+)\)", fylt).group(1)
        for farge in (omriss.group(1), fyll, strek):
            for bakgrunn in ("kort", "bakgrunn"):
                assert _kontrast(farger[farge], farger[bakgrunn]) >= 3.0, (farge, bakgrunn)


class TestGjennomgangen:
    """Rettingene etter gjennomgangen av 8.3 (triagen i spesifikasjonen)."""

    def test_alle_er_samme_tabell_ogsaa_naar_ingen_skilte_seg_ut(self, demo, monkeypatch):
        """BH7, ECH1. Ville feilet hvis «Alle» i Min liste mistet setningen
        om at ingen skilte seg ut, som oversikten har."""
        monkeypatch.setattr(app_modul, "del_i_to", lambda rader: ([], list(rader)))
        monkeypatch.setattr(app_modul, "ingen_skilte_seg_ut", lambda rader: True)
        setningen = "Ingen aksjer skilte seg ut"
        oversikten = demo.get("/").data.decode("utf-8")
        alle = demo.get("/min-liste?vis=alle").data.decode("utf-8")
        assert setningen in oversikten and setningen in alle
        assert setningen not in demo.get("/min-liste").data.decode("utf-8")
        assert _deler_i_rekkefoelge(alle) == _deler_i_rekkefoelge(oversikten)

    def test_antallet_teller_bare_merkede_med_en_rad(self, demo):
        """BH8, ECH2. Ville feilet hvis knappen talte en merket aksje som
        ikke har en rad i tabellen, så antallet og tabellen sprikte."""
        assert _merk(demo, "MTFJ").status_code == 303  # uten kurser
        html = demo.get("/min-liste").data.decode("utf-8")
        assert 'Min liste <span class="antall">5</span>' in html
        for symbol in MERKET_I_DEMOEN:
            assert _merk(demo, symbol, til="fjern").status_code == 303
        html = demo.get("/min-liste").data.decode("utf-8")
        assert 'Min liste <span class="antall">0</span>' in html
        assert "Ingen aksjer i Min liste ennå" in html and "<table" not in html
        # Og den kan tas ut igjen.
        assert _merk(demo, "MTFJ", til="fjern").status_code == 303

    def test_en_rad_for_en_aksje_som_er_tatt_ut_kan_fjernes(self, tmp_path):
        """ECH3, BH16. Ville feilet hvis fjern bare godtok symbolene i aksje:
        da ble raden liggende og aksjen merket igjen hvis den kom tilbake."""
        sti = _base(tmp_path)
        c = aapne_base(sti)
        try:
            SqliteMinlistelager(c).merk("AKRBP")
            c.execute("DELETE FROM aksje WHERE symbol = 'AKRBP'")
            c.commit()
            lager = SqliteMinlistelager(c)
            assert lager.merkede() == frozenset()
            lager.fjern("AKRBP")
            with pytest.raises(UkjentAksje):
                lager.merk("AKRBP")
        finally:
            c.close()
        assert _i_fila(sti) == set()
        minne = MinneMinlistelager(["A"])
        with pytest.raises(UkjentAksje):
            minne.fjern("B")

    def test_porten_avviser_selv_uten_triggeren(self, tmp_path):
        """VG3. Ville feilet hvis porten slo opp i AKSJEUNIVERS og lot
        triggeren gjøre jobben: uten triggeren avviser porten likevel et
        symbol som ikke står i aksje i basen."""
        sti = _base(tmp_path)
        c = sqlite3.connect(sti, isolation_level=None)
        try:
            c.execute("DROP TRIGGER min_liste_kjent_aksje_insert")
            c.execute("DELETE FROM aksje WHERE symbol = 'MOWI'")
        finally:
            c.close()
        c = aapne_base(sti)
        try:
            for symbol in ("MOWI", "XXX"):
                with pytest.raises(UkjentAksje):
                    SqliteMinlistelager(c).merk(symbol)
        finally:
            c.close()
        assert _i_fila(sti) == set()

    def test_sidene_med_faerre_enn_15_aksjer(self, klient, monkeypatch):  # noqa: F811
        """VG3, føringen 30.09 under AD-21. Ville feilet hvis sidene antok 15
        aksjer i antallet eller tabellen."""
        monkeypatch.delenv(app_modul.I_DEMO, raising=False)
        aapne_base(lagring_sqlite.BASE_STI).close()
        c = sqlite3.connect(lagring_sqlite.BASE_STI, isolation_level=None)
        try:
            c.execute("DELETE FROM aksje WHERE symbol NOT IN ('EQNR', 'DNB', 'KOG')")
        finally:
            c.close()
        _lagret_for(["EQNR", "DNB", "KOG"])
        assert _merk(klient, "KOG").status_code == 303
        html = klient.get("/min-liste").data.decode("utf-8")
        assert 'Alle <span class="antall">3</span>' in html
        assert 'Min liste <span class="antall">1</span>' in html
        assert _rekkefoelge(html) == ["KOG"]
        alle = klient.get("/min-liste?vis=alle").data.decode("utf-8")
        assert sorted(_rekkefoelge(alle)) == ["DNB", "EQNR", "KOG"]

    def test_merkingen_naar_demobasen_mangler_gir_404(self, demo):
        """ECH4. Ville feilet hvis ruta prøvde å skrive uten tilkobling og
        ga 500."""
        demo_sti().unlink()
        assert _merk(demo, "BRFE").status_code == 404
        assert not demo_sti().exists()

    def test_oevrige_har_overskriften_naar_bare_de_er_merket(self, demo):
        """ECH5. Ville feilet hvis «Øvrige aksjer» mistet overskriften i Min
        liste når ingen av de merkede skilte seg ut."""
        for symbol in ("BRFE", "KVST", "NLYS"):
            assert _merk(demo, symbol, til="fjern").status_code == 303
        html = demo.get("/min-liste").data.decode("utf-8")
        assert "Skilte seg ut <span" not in html
        assert "Øvrige aksjer <span" in html
        assert _rekkefoelge(html) == ["LSTF", "SGNT"]

    def test_lenkene_og_skjemaet_i_min_liste_beholder_valgene(self, demo):
        """VG1, ECH6. Ville feilet hvis skjemaet sendte tilbake til / eller
        uten sorteringen, eller lenkene mistet «Alle» eller sorteringen."""
        html = demo.get("/min-liste?vis=alle&sorter=kurs&orden=synkende").data.decode("utf-8")
        tilbake = set(re.findall(r'name="tilbake" value="([^"]*)"', html))
        assert tilbake == {"/min-liste?vis=alle&amp;sorter=kurs&amp;orden=synkende"}
        assert '<a href="/min-liste?vis=alle">Standard rekkefølge</a>' in html
        assert re.search(r'class="visknapp" href="/min-liste\?sorter=kurs&amp;orden=synkende">Min liste', html)
        assert re.search(
            r'class="visknapp" href="/min-liste\?vis=alle&amp;sorter=kurs&amp;orden=synkende" aria-current', html
        )
        sorterlenker = re.findall(r'<a class="sorter[^"]*" href="([^"]*)"', html)
        assert len(sorterlenker) == 5
        assert all(h.startswith("/min-liste?vis=alle&amp;sorter=") for h in sorterlenker)
        lista = demo.get("/min-liste?sorter=signal&orden=stigende").data.decode("utf-8")
        assert set(re.findall(r'name="tilbake" value="([^"]*)"', lista)) == {
            "/min-liste?sorter=signal&amp;orden=stigende"
        }
        assert '<a href="/min-liste">Standard rekkefølge</a>' in lista

    def test_fotnotene_i_min_liste_gjelder_bare_lista(self, demo):
        """ECH7, BH9. Ville feilet hvis Min liste viste fotnoten om en aksje
        uten kurser som ikke er merket, eller fotnoter under en tom liste."""
        # Navnet lenker til aksjesiden (gruppens svar 23.10 kl. 09:24, b).
        uten = 'Uten data i denne kilden: <a href="/aksje/MTFJ">Matfjord Merkevarer</a>'
        assert uten in demo.get("/").data.decode("utf-8")
        assert uten in demo.get("/min-liste?vis=alle").data.decode("utf-8")
        assert uten not in demo.get("/min-liste").data.decode("utf-8")
        for symbol in MERKET_I_DEMOEN:
            _merk(demo, symbol, til="fjern")
        tom = demo.get("/min-liste").data.decode("utf-8")
        assert 'class="fotnote"' not in tom
        assert "Stjernen foran et selskap legger aksjen i lista" in tom

    def test_i_den_ekte_basen_skriver_merkingen_bare_min_liste(self, klient, monkeypatch):  # noqa: F811
        """VG9, AD-7. Ville feilet hvis merkingen eller en side rørte en annen
        tabell i den ekte basen, som åpnes for skriving for alle rutene."""
        monkeypatch.delenv(app_modul.I_DEMO, raising=False)
        _lagret_for(["EQNR", "DNB"])
        klient.get("/")
        foer = _innhold(lagring_sqlite.BASE_STI)
        for adresse in ("/", "/min-liste", "/aksje/EQNR"):
            assert klient.get(adresse).status_code == 200
        assert _merk(klient, "EQNR").status_code == 303
        assert _merk(klient, "DNB").status_code == 303
        assert _merk(klient, "DNB", til="fjern").status_code == 303
        assert _innhold(lagring_sqlite.BASE_STI) == foer
        assert _i_fila(lagring_sqlite.BASE_STI) == {"EQNR"}

    def test_bare_webserveren_og_demoen_skriver_min_liste(self):
        """VG8, AD-3. Ville feilet hvis en annen modul i src/, for eksempel
        hentingen, tok i bruk porten eller skrev tabellen."""
        brukere = set()
        for fil in (ROT / "src").glob("*.py"):
            tekst = fil.read_text(encoding="utf-8")
            if "SqliteMinlistelager(" in tekst or re.search(r"(INSERT INTO|DELETE FROM|UPDATE) min_liste", tekst):
                brukere.add(fil.name)
        assert brukere == {"app.py", "demo.py", "lagring_sqlite.py"}

    def test_den_fylte_knappen_er_fylt_i_stilen_og_raden_brytes(self):
        """VG5, VG2. Ville feilet hvis regelen som fyller knappen for siden
        man står på, ble borte, eller knapperaden ikke kunne brytes på en
        smal skjerm (390 px, målt i spesifikasjonen)."""
        stil = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
        fylt = re.search(r'header\.stripe a\.sideknapp\[aria-current="page"\] \{([^}]*)\}', stil).group(1)
        assert "background: var(--hvit)" in fylt and "color: var(--blekk)" in fylt
        assert "flex-wrap: wrap" in re.search(r"header\.stripe \.sider \{([^}]*)\}", stil).group(1)
        valgt = re.search(r'a\.visknapp\[aria-current="true"\] \{([^}]*)\}', stil).group(1)
        assert "background: var(--fyll)" in valgt
