"""Story 8.6: børsometeret (FR-106, avgjørelsen 22.10 kl. 23:19).

Basene lages bare i tmp_path (regel 22), og ingen test går på nett (AD-8).
Hvert kontrollpunkt er prøvd med en mutant (spesifikasjonen, Mutantene).
"""

import ast
import re
import shutil
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

import app as app_modul
import boersometer
import demo
import lagring_sqlite
from boersometer import (
    BRANSJER,
    GUL,
    HOEY,
    LAV,
    MOERK,
    UTEN_DATA,
    VANLIG,
    Rute,
    bygg_boersometer,
    bygg_rute,
    ramme,
    snitt,
    stoerrelse,
)
from kursdata import Aksje, Kursrad
from lagring_sqlite import SqliteOversiktsleser, demo_sti
from markedsoversikt import IKKE_VURDERT
from signalberegning import INGEN, POSITIV, STANDARD
from vurderingsdata import Vurdering

SRC = Path(boersometer.__file__).resolve().parent
IDAG = date(2026, 10, 13)


def _aksje(symbol: str, sektor: str) -> Aksje:
    return Aksje(symbol, f"{symbol}.OL", f"Selskap {symbol}", sektor)


def _rute(symbol: str, sektor: str, endring: float | None, styrke: int | None = None) -> Rute:
    return Rute(aksje=_aksje(symbol, sektor), endring=endring, volumforhold=None, styrke=styrke, tekst=None)


def _vurdering(styrke: int, volumforhold: float | None) -> Vurdering:
    sjekker = [1] * styrke + [0] * (3 - styrke)
    return Vurdering(
        styrke=styrke,
        retning=POSITIV if styrke else INGEN,
        trend=sjekker[0],
        bevegelse=sjekker[1],
        interesse=sjekker[2],
        slutt=101.0,
        justert_slutt=101.0,
        trend_avvik=0.03 if sjekker[0] else 0.0,
        dagens_endring=0.01,
        standardavvik=0.002 if sjekker[1] else 0.02,
        volumforhold=volumforhold,
    )


KURSER = [
    Kursrad(dato=date(2026, 10, 8), slutt=100.0, justert_slutt=100.0, volum=1000),
    Kursrad(dato=date(2026, 10, 9), slutt=101.0, justert_slutt=101.0, volum=2000),
]


# --- Logikken ---------------------------------------------------------------


class TestSnittet:
    def test_snittet_er_av_endringen_for_alle_aksjene_i_bransjen(self):
        """Ville feilet hvis snittet var av bare én aksje, den første eller
        den siste (mutant 1), eller summen."""
        bransje = bygg_boersometer([_rute("A", "Energi", 1.0), _rute("B", "Energi", 2.0), _rute("C", "Energi", 6.0)])[0]
        assert bransje.snitt == pytest.approx(3.0)

    def test_en_aksje_uten_endring_teller_ikke(self):
        """Ville feilet hvis en aksje uten endring talte som 0 i snittet."""
        assert snitt([_rute("A", "Energi", 4.0), _rute("B", "Energi", None)]) == pytest.approx(4.0)

    def test_uten_endringer_er_det_ikke_noe_snitt(self):
        """Ville feilet med 0,00 % for en bransje der ingen aksje har kurs."""
        assert snitt([_rute("A", "Konsum", None)]) is None


class TestBransjene:
    def test_rekkefoelgen_er_den_i_designreglene(self):
        """Ville feilet hvis bransjene sto i den rekkefølgen aksjene kom, eller
        alfabetisk."""
        ruter = [_rute("K", "Konsum", 1.0), _rute("E", "Energi", 1.0), _rute("S", "Sjømat", 1.0)]
        assert [b.navn for b in bygg_boersometer(ruter)] == ["Energi", "Sjømat", "Konsum"]

    def test_de_13_bransjene_fra_designreglene(self):
        """Ville feilet hvis en bransje manglet eller sto to ganger."""
        assert len(BRANSJER) == len(set(BRANSJER)) == 13

    @pytest.mark.parametrize("antall", [1, 2, 4, 15])
    def test_antallet_bransjer_og_aksjer_telles_fra_lista(self, antall):
        """En kortere liste enn 15 gir færre bransjer. Ville feilet med et
        fast antall bransjer eller aksjer (mutant 3)."""
        ruter = [_rute(f"S{i}", BRANSJER[i % 5], 1.0) for i in range(antall)]
        bransjer = bygg_boersometer(ruter)
        assert len(bransjer) == min(antall, 5)
        assert sum(b.antall for b in bransjer) == antall

    def test_en_ukjent_bransje_staar_sist(self):
        """Ville feilet hvis en aksje med en bransje utenfor de 13 forsvant."""
        bransjer = bygg_boersometer([_rute("X", "Romfart", 1.0), _rute("E", "Energi", 1.0)])
        assert [b.navn for b in bransjer] == ["Energi", "Romfart"]

    def test_aksjene_staar_i_lista_sin_rekkefoelge_i_bransjen(self):
        ruter = [_rute("B", "Energi", 1.0), _rute("A", "Energi", 2.0)]
        assert [r.aksje.symbol for r in bygg_boersometer(ruter)[0].ruter] == ["B", "A"]


class TestRammen:
    @pytest.mark.parametrize(("styrke", "ventet"), [(3, GUL), (2, MOERK), (1, None), (0, None), (None, None)])
    def test_gult_bare_ved_3_av_3(self, styrke, ventet):
        """Ville feilet med gult ved 2 av 3 (mutant 2), eller med ramme ved 1
        og 0."""
        assert ramme(styrke) == ventet


class TestStoerrelsen:
    @pytest.mark.parametrize(
        ("forhold", "ventet"),
        [(None, VANLIG), (0.5, LAV), (0.99, LAV), (1.0, VANLIG), (1.49, VANLIG), (1.5, HOEY), (4.0, HOEY)],
    )
    def test_stoerrelsen_foelger_volumforholdet(self, forhold, ventet):
        """Grensen for høy er volumfaktoren (1,5), den samme som gir utslag på
        interesse. Ville feilet med samme størrelse for alle, eller med en
        annen grense."""
        assert STANDARD.volumfaktor == 1.5
        assert stoerrelse(forhold) == ventet


class TestRuta:
    def test_med_vurdering_har_ruta_styrken_og_volumforholdet(self):
        rute = bygg_rute(_aksje("A", "Energi"), KURSER, _vurdering(3, 2.0), date(2026, 10, 9), IDAG)
        assert (rute.styrke, rute.ramme, rute.stoerrelse) == (3, GUL, HOEY)
        assert rute.endring == pytest.approx(1.0)
        assert rute.tekst is None

    def test_ingen_ramme_en_dag_uten_vurdering(self):
        """Ville feilet hvis ruta fikk ramme, eller styrke, uten vurdering."""
        rute = bygg_rute(_aksje("A", "Energi"), KURSER, None, date(2026, 10, 9), IDAG)
        assert (rute.styrke, rute.ramme, rute.volumforhold) == (None, None, None)
        assert rute.tekst == IKKE_VURDERT
        assert rute.endring == pytest.approx(1.0)

    def test_uten_kurs_paa_dagen_er_det_uten_data(self):
        """Ville feilet hvis en aksje uten kurs den dagen fikk endringen fra
        en annen dag."""
        rute = bygg_rute(_aksje("A", "Energi"), KURSER[:1], _vurdering(3, 2.0), date(2026, 10, 9), IDAG)
        assert rute.uten_data and rute.tekst == UTEN_DATA
        assert (rute.endring, rute.ramme) == (None, None)


# --- Siden ------------------------------------------------------------------


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))


@pytest.fixture(scope="module")
def basemal(tmp_path_factory):
    """Demoens kurser og vurderinger, laget i tmp_path (regel 22)."""
    sti = tmp_path_factory.mktemp("boersometermal") / "demo.db"
    demo.lag_demobase(sti, skriv=lambda _: None)
    return sti


@pytest.fixture
def klient(monkeypatch, basemal):
    """Demoen, med demobasen der webserveren leter med bryteren på."""
    sti = demo_sti()
    sti.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(basemal, sti)
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


def _side(klient, adresse: str = "/boersometer") -> str:
    svar = klient.get(adresse)
    assert svar.status_code == 200, adresse
    return svar.data.decode("utf-8")


def _overskrifter(html: str) -> dict[str, str]:
    """Bransjen og teksten i overskriften, uten tagger."""
    ut = {}
    for h2 in re.findall(r'<section class="bransje".*?<h2[^>]*>(.*?)</h2>', html, re.S):
        tekst = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h2)).strip()
        ut[tekst.split(" ")[0]] = tekst
    return ut


def _ruter(html: str) -> list[tuple[str, str]]:
    """Klassene og symbolet for hver rute, med eller uten lenke."""
    return re.findall(r'<(?:a|div) class="(rute [^"]*)"[^>]*>\s*<span class="ticker">([A-Z0-9]+)</span>', html)


def _lenker(html: str) -> list[str]:
    return re.findall(r'<a class="rute [^"]*" href="/aksje/([A-Z0-9]+)"', html)


class TestSiden:
    def test_knappen_i_stripa_er_fylt_paa_siden(self, klient):
        """Ville feilet hvis knappen manglet, sto et annet sted enn mellom
        «Markedsoversikt» og «Min liste», eller ikke var fylt."""
        html = _side(klient)
        knapper = re.findall(r'<a class="sideknapp" href="([^"]+)"( aria-current="page")?>([^<]+)</a>', html)
        assert [(href, tekst) for href, _, tekst in knapper] == [
            ("/", "Markedsoversikt"),
            ("/boersometer", "Børsometer"),
            ("/min-liste", "Min liste"),
        ]
        assert [tekst for _, fylt, tekst in knapper if fylt] == ["Børsometer"]
        assert 'href="/boersometer">Børsometer</a>' in _side(klient, "/")

    def test_snittet_i_overskriften_er_snittet_av_rutene(self, klient):
        """Energi har fire aksjer i demoen. Ville feilet med snittet av bare
        én av dem (mutant 1)."""
        html = _side(klient)
        energi = re.search(r'<section class="bransje".*?</section>', html, re.S).group(0)
        endringer = [
            float(e.replace(",", ".").replace(" %", ""))
            for e in re.findall(r'<span class="endring">([^<]+)</span>', energi)
        ]
        assert len(endringer) == 4
        vist = re.search(r'<span class="snitt [a-z]+">([^<]+)</span>', energi).group(1)
        # Fra de avrundede endringene kan snittet avvike med en halv hundredel.
        assert abs(float(vist.replace(",", ".").replace(" %", "")) - sum(endringer) / 4) <= 0.006

    def test_1_aksje_der_bransjen_har_en(self, klient):
        """Ville feilet med «1 aksjer», eller uten merket."""
        overskrifter = _overskrifter(_side(klient))
        assert overskrifter["Industri"].endswith("1 aksje")
        assert overskrifter["Energi"].endswith("4 aksjer")
        assert not any(t.endswith("1 aksjer") for t in overskrifter.values())

    def test_antallet_telles_fra_lista(self, klient):
        """Demoen har 15 aksjer i 8 bransjer. Ville feilet med 13 bransjer
        eller et fast antall."""
        html = _side(klient)
        assert "15 aksjer i 8 bransjer" in html
        assert len(_overskrifter(html)) == 8 and len(_ruter(html)) == 15

    def test_en_kortere_liste_gir_faerre_bransjer_og_ruter(self, klient, monkeypatch):
        """Lista fra porten kortes til de 4 første. Ville feilet med et fast
        antall bransjer (mutant 3) eller aksjer."""
        hele = SqliteOversiktsleser.oversikt
        monkeypatch.setattr(SqliteOversiktsleser, "oversikt", lambda self: hele(self)[:4])
        html = _side(klient)
        bransjer = {post.aksje.sektor for post in hele(SqliteOversiktsleser(sqlite3.connect(demo_sti())))[:4]}
        assert len(_ruter(html)) == 4
        assert len(_overskrifter(html)) == len(bransjer) < 8
        assert f"4 aksjer i {len(bransjer)} bransjer" in html

    def test_gul_ramme_bare_ved_3_av_3(self, klient):
        """Rammene på siden er de samme som styrken i tabellen under. Ville
        feilet med gult ved 2 av 3 (mutant 2)."""
        html = _side(klient)
        rammer = {symbol: re.search(r"ramme-(\w+)", klasser) for klasser, symbol in _ruter(html)}
        gule = {s for s, r in rammer.items() if r and r.group(1) == "gul"}
        moerke = {s for s, r in rammer.items() if r and r.group(1) == "moerk"}
        assert gule == {"BRFE", "KVST", "LKSV", "TRHF"}
        assert moerke and not gule & moerke
        # De samme fire som linja om 3 av 3 på oversikten.
        oversikt = _side(klient, "/")
        for symbol in gule:
            navn = re.search(rf'href="/aksje/{symbol}">([^<]+)</a>', oversikt).group(1)
            assert navn in re.search(r"Bare (.*?) fikk utslag på alle", oversikt).group(1)

    def test_stoerrelsen_foelger_volumforholdet_i_tabellen(self, klient):
        """Ville feilet hvis ruta hadde en annen størrelse enn volumforholdet
        i tabellen sier."""
        html = _side(klient)
        tabell = html.split('<table class="boersometertabell">')[1]
        ord_ = {"lavt": LAV, "vanlig": VANLIG, "høyt": HOEY}
        rader = re.findall(r'href="/aksje/([A-Z0-9]+)">.*?</td>\s*<td>[^<]*</td>\s*<td>([^<]*)</td>', tabell, re.S)
        # MTFJ har ingen kurser og ingen lenke i tabellen.
        assert len(rader) == 14
        stoerrelser = {symbol: re.search(r"stoerrelse-(\w+)", klasser).group(1) for klasser, symbol in _ruter(html)}
        sett = set()
        for symbol, volum in rader:
            treff = re.search(r"\((lavt|vanlig|høyt)\)", volum)
            ventet = ord_[treff.group(1)] if treff else VANLIG
            assert stoerrelser[symbol] == ventet, (symbol, volum)
            sett.add(ventet)
        assert sett == {LAV, VANLIG, HOEY}

    def test_ingen_ramme_en_dag_uten_vurdering(self, klient):
        """18.09 er før vurderingene i demoen starter (STARTDAG 21.09). Ville
        feilet med ramme eller styrke den dagen."""
        html = _side(klient, "/boersometer?dag=2026-09-18")
        assert "fredag 18.09" in html
        ruter = _ruter(html)
        assert len(ruter) == 15 and not any("ramme-" in klasser for klasser, _ in ruter)
        assert html.count(f'<span class="tekst">{IKKE_VURDERT}</span>') == 14
        assert "av 3</span>" not in html

    def test_en_dag_uten_kurs_gir_boersdagen_foer(self, klient):
        html = _side(klient, "/boersometer?dag=2026-09-19")
        assert "fredag 18.09" in html and "19.09 har ingen kurs" in html

    @pytest.mark.parametrize("dag", ["tull", "2026-13-40", "2026-09-18x"])
    def test_en_ugyldig_dato_gir_siste_boersdag(self, klient, dag):
        html = _side(klient, f"/boersometer?dag={dag}")
        assert "fredag 09.10" in html and "Datoen kunne ikke leses" in html

    def test_aksjen_uten_kurser_staar_med_uten_data(self, klient):
        html = _side(klient)
        rute = re.search(
            r'<div class="rute [^"]*uten-data[^"]*">\s*<span class="ticker">MTFJ</span>.*?</div>', html, re.S
        )
        assert rute and "Uten data" in rute.group(0)

    def test_hver_rute_lenker_til_aksjesiden(self, klient):
        """Hver aksje med kurser lenker til aksjesiden. MTFJ har ingen kurser
        og ingen aksjeside (FR-204), så ruta er ikke en lenke. Ville feilet
        med en lenke som gir 404."""
        html = _side(klient)
        lenker = _lenker(html)
        assert len(lenker) == 14 and "MTFJ" not in lenker
        for symbol in lenker:
            assert klient.get(f"/aksje/{symbol}").status_code == 200
        assert klient.get("/aksje/MTFJ").status_code == 404
        # Også en dag aksjen ikke hadde kurs, når den har kurser senere.
        assert "VRDS" in _lenker(_side(klient, "/boersometer?dag=2026-08-03"))

    def test_hovedindeksen_staar_over_rutene(self, klient):
        html = _side(klient)
        assert html.index('<section class="hovedindeks"') < html.index('<section class="bransje"')
        # En annen dag: indeksen står med datoen sin, som på oversikten.
        assert '<span class="indeksdato">09.10</span>' in _side(klient, "/boersometer?dag=2026-09-18")

    def test_ingen_raad(self, klient):
        """NFR-06. Ville feilet med kjøp eller selg på siden utenom hjelpen."""
        tekst = re.sub(r"<[^>]+>", " ", _side(klient).split("<main", 1)[1]).lower()
        assert not re.search(r"\b(kjøp|selg|anbefal)", tekst)


class TestIngenKallOgIngenTabell:
    def test_siden_endrer_ikke_basen(self, klient):
        """Ville feilet hvis siden skrev til basen eller laget en ny tabell."""
        foer = lagring_sqlite_skjema(demo_sti())
        innhold = demo_sti().read_bytes()
        _side(klient)
        _side(klient, "/boersometer?dag=2026-09-18")
        assert lagring_sqlite_skjema(demo_sti()) == foer
        assert demo_sti().read_bytes() == innhold

    def test_migrasjonene_er_de_samme(self):
        """Ingen ny tabell: ingen migrasjon er lagt til for børsometeret."""
        migrasjoner = sorted(p.name for p in (SRC / "migrasjoner").glob("*.sql"))
        assert not any("boersometer" in navn for navn in migrasjoner)
        assert "CREATE TABLE" not in (SRC / "boersometer.py").read_text(encoding="utf-8")

    def test_logikken_importerer_ingen_henting(self):
        """AD-10: webserveren henter aldri. Ville feilet hvis boersometer.py
        importerte hentingen eller kilden."""
        tre = ast.parse((SRC / "boersometer.py").read_text(encoding="utf-8"))
        moduler = {n.module for n in ast.walk(tre) if isinstance(n, ast.ImportFrom)}
        moduler |= {a.name for n in ast.walk(tre) if isinstance(n, ast.Import) for a in n.names}
        assert not moduler & {"eodhd", "fetch_prices", "lagring_fil", "requests", "urllib", "ki", "ki_visning"}

    def test_ruta_kaller_ikke_hentingen(self, klient, monkeypatch):
        """Ville feilet hvis siden hentet kurser eller laget KI-tekst."""
        import eodhd

        def stopp(*_a, **_k):
            raise AssertionError("kall fra børsometeret")

        for navn in dir(eodhd):
            if callable(getattr(eodhd, navn)) and not navn.startswith("_") and navn[0].islower():
                monkeypatch.setattr(eodhd, navn, stopp)
        _side(klient)


def lagring_sqlite_skjema(sti: Path) -> set:
    tilkobling = sqlite3.connect(sti)
    try:
        return set(tilkobling.execute("SELECT type, name, sql FROM sqlite_master"))
    finally:
        tilkobling.close()


def test_demomerket_er_paa_siden(klient):
    """Demoen viser det samme med demoselskapene, merket «Eksempeltall»."""
    assert lagring_sqlite.er_demobase(demo_sti())
    assert "Eksempeltall" in _side(klient)
