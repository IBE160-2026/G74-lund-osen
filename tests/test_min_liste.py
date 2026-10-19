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
from test_app import _deler_i_rekkefoelge, _regel, _stil
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
        """Ville feilet uten triggeren i 0007: en INSERT eller UPDATE utenom
        porten med et symbol som ikke står i aksje, stoppes av basen."""
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
        assert svar.headers["Location"] == tilbake
        assert "HVDO" in _merket(demo.get("/").data.decode("utf-8"))
        svar = _merk(demo, "HVDO", til="fjern", tilbake="/?sorter=kurs&orden=stigende")
        assert svar.status_code == 303 and svar.headers["Location"] == "/?sorter=kurs&orden=stigende"
        assert "HVDO" not in _merket(demo.get("/").data.decode("utf-8"))

    def test_en_post_fra_en_annen_side_gir_403(self, demo):
        """Ville feilet uten Origin-sjekken: en annen side kunne merket for
        brukeren. Ingenting er skrevet etter 403."""
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
        assert svar.headers["Location"] == forventet

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
        merkede, i samme rekkefølge innenfor hver del."""
        valg = f"sorter={kolonne}&orden={orden}"
        ut, oevrige = _deler_i_rekkefoelge(demo.get(f"/?{valg}").data.decode("utf-8"))
        l_ut, l_oevrige = _deler_i_rekkefoelge(demo.get(f"/min-liste?{valg}").data.decode("utf-8"))
        assert l_ut == [s for s in ut if s in MERKET_I_DEMOEN]
        assert l_oevrige == [s for s in oevrige if s in MERKET_I_DEMOEN]
        assert _deler_i_rekkefoelge(demo.get(f"/min-liste?vis=alle&{valg}").data.decode("utf-8")) == (ut, oevrige)

    def test_den_fylte_knappen_paa_hver_side(self, demo):
        """Ville feilet hvis knappen for siden man står på, ikke var fylt,
        eller en knapp var fylt på aksjesiden."""
        forventet = {"/": "Markedsoversikt", "/min-liste": "Min liste", "/min-liste?vis=alle": "Min liste"}
        for adresse, fylt in forventet.items():
            stripa = demo.get(adresse).data.decode("utf-8").split("</header>", 1)[0]
            assert re.findall(r'class="sideknapp" href="[^"]*" aria-current="page">([^<]+)<', stripa) == [fylt]
            assert stripa.count('class="sideknapp"') == 2
        aksjesiden = demo.get("/aksje/KVST").data.decode("utf-8")
        stripa = aksjesiden.split("</header>", 1)[0]
        assert stripa.count('class="sideknapp"') == 2 and 'aria-current="page"' not in stripa
        # Aksjesiden beholder veien tilbake.
        assert '<a class="tilbake" href="/">Markedsoversikt</a>' in aksjesiden

    def test_knapperaden_ogsaa_paa_feilsiden(self, demo):
        """Ville feilet hvis knapperaden bare sto på sidene med tabell."""
        demo_sti().write_bytes(b"ikke en sqlite-base" * 10)
        svar = demo.get("/min-liste")
        assert svar.status_code == 503
        stripa = svar.data.decode("utf-8").split("</header>", 1)[0]
        assert stripa.count('class="sideknapp"') == 2

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
            for rad in re.findall(r"<tr (?:class=\"utslag[^\"]*\")?\s*>(.*?)</tr>", html, re.S):
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
        assert re.search(r'aria-current="page">Min liste <span class="antall">5</span>', html)
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
        fylt (WCAG 1.4.11). Ville feilet med den lyse oransje, som har 1,9:1."""
        stil = _stil(demo.get("/").data.decode("utf-8"))
        farger = _farger(stil)
        omriss = re.search(r"stroke: var\(--([a-z0-9-]+)\)", _regel(stil, "button.stjerneknapp svg"))
        fylt = _regel(stil, "button.stjerneknapp.merket svg")
        fyll = re.search(r"fill: var\(--([a-z0-9-]+)\)", fylt).group(1)
        strek = re.search(r"stroke: var\(--([a-z0-9-]+)\)", fylt).group(1)
        for farge in (omriss.group(1), fyll, strek):
            for bakgrunn in ("kort", "bakgrunn"):
                assert _kontrast(farger[farge], farger[bakgrunn]) >= 3.0, (farge, bakgrunn)
