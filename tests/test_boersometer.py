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
    vis_volumforhold,
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
        """Ville feilet hvis rutene i en bransje ble sortert på nytt."""
        ruter = [_rute("B", "Energi", 1.0), _rute("A", "Energi", 2.0)]
        assert [r.aksje.symbol for r in bygg_boersometer(ruter)[0].ruter] == ["B", "A"]


class TestRammen:
    @pytest.mark.parametrize(("styrke", "ventet"), [(3, GUL), (2, MOERK), (1, None), (0, None), (None, None)])
    def test_gult_bare_ved_3_av_3(self, styrke, ventet):
        """Ville feilet med gult ved 2 av 3 (mutant 2), eller med ramme ved 1
        og 0."""
        assert ramme(styrke) == ventet

    @pytest.mark.parametrize(
        ("styrke", "siste", "ventet"),
        [(3, 3, GUL), (1, 3, GUL), (3, 2, None), (2, 2, None), (None, 3, GUL), (None, 2, None), (0, None, None)],
    )
    def test_en_annen_dag_foelger_gult_siste_boersdag(self, styrke, siste, ventet):
        """Designregler §3: gult betyr 3 av 3 på siste børsdag og står også en
        annen dag, også en dag uten vurdering (gruppens svar 23.10 kl. 09:24,
        a), og 2 av 3 merkes bare for siste børsdag (gjennomgangen, VG1).
        Ville feilet med rammen fra dagen som vises."""
        rute = Rute(
            aksje=_aksje("A", "Energi"),
            endring=1.0,
            volumforhold=None,
            styrke=styrke,
            tekst=None,
            siste_styrke=siste,
            er_siste=False,
        )
        assert rute.ramme == ventet


class TestStoerrelsen:
    @pytest.mark.parametrize(
        ("forhold", "ventet"),
        [
            (None, VANLIG),
            (0.5, LAV),
            (0.99, LAV),
            (1.0, VANLIG),
            (1.49, VANLIG),
            (1.5, VANLIG),
            (1.5001, HOEY),
            (4.0, HOEY),
        ],
    )
    def test_stoerrelsen_foelger_volumforholdet(self, forhold, ventet):
        """Høy er over volumfaktoren (1,5), med «>» som interesse-sjekken i
        signalberegning (gjennomgangen, BH1). Ville feilet med samme størrelse
        for alle, med en annen grense, eller med «>=»."""
        assert STANDARD.volumfaktor == 1.5
        assert stoerrelse(forhold) == ventet

    def test_samme_grense_som_interesse_sjekken(self):
        """Ville feilet hvis en stor rute kunne stå ved en aksje der
        interesse ikke slo ut på volumet, eller omvendt."""
        from signalberegning import interesse

        for forhold in (1.4999, 1.5, 1.5001):
            volumer = [1000] * STANDARD.volum_vindu + [round(1000 * forhold * 10_000) / 10_000]
            kurser = [100.0] * STANDARD.volum_vindu + [101.0]
            slo_ut = interesse(kurser, volumer, STANDARD).verdi != 0
            assert (stoerrelse(volumer[-1] / 1000) == HOEY) == slo_ut, forhold


class TestVolumtallet:
    @pytest.mark.parametrize(
        ("forhold", "vist"),
        [(1.4996, "1,4996"), (1.5004, "1,5004"), (1.5, "1,50"), (0.998, "0,998"), (2.0, "2,00")],
    )
    def test_tallet_skilles_fra_grensene(self, forhold, vist):
        """Gjennomgangen (BH2, ECH4): ville feilet med «1,50 (vanlig)» og
        «1,50 (høyt)» ved siden av hverandre, eller «1,00 (lavt)»."""
        assert vis_volumforhold(forhold) == vist


class TestRuta:
    def test_med_vurdering_har_ruta_styrken_og_volumforholdet(self):
        """Ville feilet hvis styrken eller volumforholdet ikke kom fra
        vurderingen for dagen."""
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
    return re.findall(r'<a class="rute [^"]*" href="/aksje/([A-Z0-9]+)(?:\?dag=[0-9-]+)?"', html)


def _tall(tekst: str) -> float:
    return float(tekst.replace(",", ".").replace("\u00a0%", "").replace("\u2212", "-"))


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
        assert f"4 aksjer i {len(bransjer)} {'bransje' if len(bransjer) == 1 else 'bransjer'}</p>" in html

    def test_gul_ramme_bare_ved_3_av_3(self, klient):
        """Gul ramme ved de fire med 3 av 3 i demoen, de samme som linja om
        3 av 3 på oversikten. Ville feilet med gult ved 2 av 3 (mutant 2)."""
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
        # MTFJ har ingen kurser og ingen volumtall, men lenke (gruppens svar
        # 23.10 kl. 09:24, b), så den hoppes over her.
        rader = [(symbol, volum) for symbol, volum in rader if symbol != "MTFJ"]
        assert len(rader) == 14
        stoerrelser = {symbol: re.search(r"stoerrelse-(\w+)", klasser).group(1) for klasser, symbol in _ruter(html)}
        sett = set()
        for symbol, volum in rader:
            treff = re.search(r"\((lavt|vanlig|høyt)\)", volum)
            ventet = ord_[treff.group(1)] if treff else VANLIG
            assert stoerrelser[symbol] == ventet, (symbol, volum)
            sett.add(ventet)
        assert sett == {LAV, VANLIG, HOEY}

    def test_gult_en_dag_uten_vurdering(self, klient):
        """18.09 er før vurderingene i demoen starter (STARTDAG 21.09). Gult
        står ved de fire med 3 av 3 på siste børsdag, uten mørk ramme og uten
        styrke for dagen (gruppens svar 23.10 kl. 09:24, a). Ville feilet uten
        gult den dagen, eller med styrke eller mørk ramme."""
        html = _side(klient, "/boersometer?dag=2026-09-18")
        assert "fredag 18.09" in html
        ruter = _ruter(html)
        rammer = {symbol: re.search(r"ramme-(\w+)", klasser) for klasser, symbol in ruter}
        assert len(ruter) == 15
        assert {s for s, r in rammer.items() if r and r.group(1) == "gul"} == {"BRFE", "KVST", "LKSV", "TRHF"}
        assert not any(r and r.group(1) == "moerk" for r in rammer.values())
        assert html.count(f'<span class="tekst">{IKKE_VURDERT}</span>') == 14
        assert html.count("3 av 3 siste børsdag</span>") == 4 and "2 av 3</span>" not in html
        tabell = html.split('<table class="boersometertabell">')[1]
        assert "av 3</td>" not in tabell

    def test_en_dag_uten_kurs_gir_boersdagen_foer(self, klient):
        """Ville feilet hvis en lørdag ga en feilside eller siste børsdag."""
        html = _side(klient, "/boersometer?dag=2026-09-19")
        assert "fredag 18.09" in html and "19.09 har ingen kurs" in html

    def test_en_dag_foer_foerste_kurs_sier_at_siden_viser_en_senere_dag(self, klient):
        """Gjennomgangen (BH3, VG3, ECH1): ville feilet med «børsdagen før»
        om en dag som kommer etter."""
        html = _side(klient, "/boersometer?dag=1990-01-01")
        assert "er før første kurs, så siden viser første børsdag med kurs" in html
        assert "har ingen kurs, så siden viser børsdagen før" not in html

    def test_gult_en_annen_dag_er_3_av_3_paa_siste_boersdag(self, klient):
        """08.10 har vurderinger. Gult står ved de fire med 3 av 3 på siste
        børsdag, og ingen ruter har mørk ramme (designregler §3, VG1). Ville
        feilet med rammen fra 08.10."""
        html = _side(klient, "/boersometer?dag=2026-10-08")
        rammer = {symbol: re.search(r"ramme-(\w+)", klasser) for klasser, symbol in _ruter(html)}
        assert {s for s, r in rammer.items() if r and r.group(1) == "gul"} == {"BRFE", "KVST", "LKSV", "TRHF"}
        assert not any(r and r.group(1) == "moerk" for r in rammer.values())
        assert "3 av 3 siste børsdag" in html and "Gul ramme betyr 3 av 3 på siste børsdag, 09.10" in html

    def test_lenkene_har_dagen_som_vises(self, klient):
        """Gjennomgangen (BH4, ECH2): ville feilet hvis en rute for 08.10
        lenket til aksjesiden for siste børsdag."""
        html = _side(klient, "/boersometer?dag=2026-10-08")
        assert 'href="/aksje/BRFE?dag=2026-10-08"' in html
        assert 'href="/aksje/BRFE"' in _side(klient)
        assert "08.10" in _side(klient, "/aksje/BRFE?dag=2026-10-08")

    @pytest.mark.parametrize("dag", ["tull", "2026-13-40", "2026-09-18x"])
    def test_en_ugyldig_dato_gir_siste_boersdag(self, klient, dag):
        """Ville feilet med en feilside, eller uten meldingen."""
        html = _side(klient, f"/boersometer?dag={dag}")
        assert "fredag 09.10" in html and "Datoen kunne ikke leses" in html

    def test_aksjen_uten_kurser_staar_med_uten_data(self, klient):
        """Ville feilet hvis MTFJ, uten kurser, sto uten merket."""
        html = _side(klient)
        rute = re.search(
            r'<a class="rute [^"]*uten-data[^"]*" href="/aksje/MTFJ">\s*<span class="ticker">MTFJ</span>.*?</a>',
            html,
            re.S,
        )
        assert rute and "Uten data" in rute.group(0)

    def test_hver_rute_lenker_til_aksjesiden(self, klient):
        """Hver rute lenker til aksjesiden, også MTFJ uten kurser, som svarer
        200 (gruppens svar 23.10 kl. 09:24, b; før 404 etter FR-204). Ville
        feilet med en rute uten lenke, eller en lenke som gir 404."""
        html = _side(klient)
        lenker = _lenker(html)
        assert len(lenker) == 15 and "MTFJ" in lenker
        for symbol in lenker:
            assert klient.get(f"/aksje/{symbol}").status_code == 200
        assert '<a href="/aksje/MTFJ">Matfjord Merkevarer</a>' in html
        # Også en dag aksjen ikke hadde kurs, når den har kurser senere.
        assert "VRDS" in _lenker(_side(klient, "/boersometer?dag=2026-08-03"))

    def test_hovedindeksen_staar_over_rutene(self, klient):
        """Ville feilet hvis hovedindeksen manglet eller sto under rutene."""
        html = _side(klient)
        assert html.index('<section class="hovedindeks"') < html.index('<section class="bransje"')
        # En annen dag: indeksen står med datoen sin, som på oversikten.
        assert '<span class="indeksdato">09.10</span>' in _side(klient, "/boersometer?dag=2026-09-18")

    def test_ingen_raad_og_ingen_ki(self, klient):
        """NFR-06. Ville feilet med kjøp eller selg på siden utenom hjelpen,
        eller med KI-tekst (gjennomgangen, VG11)."""
        html = _side(klient)
        tekst = re.sub(r"<[^>]+>", " ", html.split("<main", 1)[1]).lower()
        assert not re.search(r"\b(kjøp|selg|anbefal)", tekst)
        assert 'class="ki' not in html and "KI-tekst" not in html

    def test_ordet_er_bransje_og_hver_bransje_har_symbolet(self, klient):
        """Linja 13.10 under story 8.6 (gjennomgangen, VG4): ville feilet hvis
        siden sa «sektor», eller en bransje i §4 sto uten symbol."""
        html = _side(klient)
        assert "sektor" not in re.sub(r"<[^>]+>", " ", html.split("<main", 1)[1]).lower()
        for h2 in re.findall(r'<section class="bransje".*?<h2[^>]*>(.*?)</h2>', html, re.S):
            assert "<svg" in h2, h2[:80]

    def test_tabellen_har_de_samme_tallene_som_rutene(self, klient):
        """Gjennomgangen (VG5): ville feilet hvis endringen eller styrken i
        tabellen var en annen enn i ruta."""
        html = _side(klient)
        tabell = html.split('<table class="boersometertabell">')[1]
        rader = re.findall(
            r"<tr>\s*<td>[^<]*</td>\s*<td>(?:<a [^>]*>)?([^<]+)(?:</a>)?</td>\s*<td>([^<]*)</td>\s*<td>[^<]*</td>\s*<td>([^<]*)</td>",
            tabell,
        )
        assert len(rader) == 15
        navn_til_symbol = {
            f"{n}": s
            for s, n in re.findall(
                r'<span class="ticker">([A-Z0-9]+)</span>.*?<span class="skjult">, ([^,<]+)', html, re.S
            )
        }
        endringer = dict(
            re.findall(r'<span class="ticker">([A-Z0-9]+)</span>\s*<span class="endring">([^<]+)</span>', html)
        )
        merker = dict(
            re.findall(
                r'<span class="ticker">([A-Z0-9]+)</span>\s*<span class="endring">[^<]+</span>\s*<span class="merke">([^<]+)</span>',
                html,
            )
        )
        for navn, endring, styrke in rader:
            symbol = navn_til_symbol[navn]
            assert endringer[symbol] == endring, symbol
            if styrke in ("3 av 3", "2 av 3"):
                assert merker[symbol] == styrke, symbol
            else:
                assert symbol not in merker, symbol

    def test_390_px_uten_vannrett_rulling_og_med_tastatur(self, klient):
        """Gjennomgangen (VG6). Edge målte 390 px uten vannrett rulling 23.10;
        denne testen holder det som gjorde det mulig. Ville feilet med en rute
        bredere enn 390 px minus margene, rutene uten bryting, tabellen uten
        rullboksen, eller rutene uten fokus, skjult navn og tabellen uten
        caption og scope."""
        stil = (SRC / "static" / "stil.css").read_text(encoding="utf-8")
        assert re.search(r"ul\.ruter \{[^}]*flex-wrap: wrap", stil)
        for bredde in re.findall(r"\.rute\.stoerrelse-\w+ \{ width: (\d+)px", stil):
            assert int(bredde) <= 390 - 2 * 16, bredde
        assert re.search(r"\.rute:focus-visible \{ outline", stil)
        html = _side(klient)
        assert (
            '<div class="tabellboks boersometerboks" role="region" aria-label="Børsometeret som tabell" tabindex="0">'
            in html
        )
        assert "<caption>Børsometeret 09.10 som tabell</caption>" in html and html.count('scope="col"') >= 5
        assert '<span class="skjult">, Brattfjell Energi, volum høyt</span>' in html

    def test_bøyningen_i_linja_over(self, klient, monkeypatch):
        """Gjennomgangen (BH8): ville feilet med «1 aksjer i 1 bransjer»."""
        hele = SqliteOversiktsleser.oversikt
        monkeypatch.setattr(SqliteOversiktsleser, "oversikt", lambda self: hele(self)[:1])
        assert "1 aksje i 1 bransje</p>" in _side(klient)


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
        """Ingen ny tabell. Ville feilet med en migrasjon for børsometeret,
        eller en tabell laget i logikken."""
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
    """Demoen viser det samme med demoselskapene. Ville feilet uten merket
    «Eksempeltall»."""
    assert lagring_sqlite.er_demobase(demo_sti())
    assert "Eksempeltall" in _side(klient)


class TestDenEkteVersjonen:
    """Gjennomgangen (VG9): uten demo, med en base uten demomerket."""

    @pytest.fixture
    def ekte(self, monkeypatch, basemal):
        sti = Path(lagring_sqlite.BASE_STI)
        sti.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(basemal, sti)
        tilkobling = sqlite3.connect(sti)
        try:
            tilkobling.execute("PRAGMA application_id = 0")
            tilkobling.commit()
        finally:
            tilkobling.close()
        monkeypatch.delenv(app_modul.I_DEMO, raising=False)
        monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
        app_modul.app.config["TESTING"] = True
        return app_modul.app.test_client()

    def test_den_ekte_viser_det_samme_uten_merket(self, ekte):
        """Ville feilet hvis siden bare virket i demoen."""
        html = _side(ekte)
        assert "Eksempeltall" not in html and "Oslo Børs · fredag 09.10 · 15 aksjer i 8 bransjer" in html
        assert len(_ruter(html)) == 15

    def test_aksjesiden_uten_kurser_sier_ikke_demo(self, ekte):
        """Gjennomgangen 23.10 (VG8). Ville feilet med «Demo Børs» eller
        setningen om demoen i den ekte versjonen."""
        html = _side(ekte, "/aksje/MTFJ")
        assert "Det finnes ingen kurser for Matfjord Merkevarer ennå" in html
        assert "Oslo Børs" in html and "Demo Børs" not in html and "I demoen" not in html

    def test_uten_base_viser_siden_hentekommandoen(self, monkeypatch):
        """Ville feilet med en feilside før første henting."""
        monkeypatch.delenv(app_modul.I_DEMO, raising=False)
        monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
        html = _side(app_modul.app.test_client())
        assert "Ingen kurser i basen ennå" in html and '<section class="bransje"' not in html


# --- Gruppens svar 23.10 kl. 09:24 -----------------------------------------


class TestSvaretKl0924:
    """a) gult en dag uten vurdering, og b) aksjesiden for en aksje uten
    kurser."""

    @pytest.mark.parametrize(("siste", "ventet"), [(3, GUL), (2, None), (None, None)])
    def test_uten_kurs_en_annen_dag_har_gult_fra_siste_boersdag(self, siste, ventet):
        """a) Også en dag aksjen ikke hadde kurs. Ville feilet hvis en rute med
        «Uten data» mistet gult, eller fikk mørk ramme en annen dag."""
        rute = bygg_rute(
            _aksje("A", "Energi"), KURSER[:1], None, date(2026, 10, 9), IDAG, siste_styrke=siste, er_siste=False
        )
        assert rute.uten_data and rute.ramme == ventet

    @pytest.mark.parametrize("siste", [3, 2, None])
    def test_siste_boersdag_uten_vurdering_har_ingen_ramme(self, siste):
        """a) Siste børsdag følger rammen vurderingen for dagen, ikke
        siste_styrke (gjennomgangen 23.10, BH2, VG4). Ville feilet hvis gult
        fra siste_styrke sto siste børsdag uten vurdering."""
        rute = bygg_rute(_aksje("A", "Energi"), KURSER, None, date(2026, 10, 9), IDAG, siste_styrke=siste)
        assert rute.ramme is None

    def test_gult_en_dag_uten_vurdering_ogsaa_i_merket(self, klient):
        """a) 18.09 har ingen vurderinger i demoen. Ville feilet hvis gult
        forsvant den dagen (mutant N1), eller merket i ruta ikke sa «siste
        børsdag» (gjennomgangen 23.10, VG5)."""
        html = _side(klient, "/boersometer?dag=2026-09-18")
        gule = [symbol for klasser, symbol in _ruter(html) if "ramme-gul" in klasser]
        assert sorted(gule) == ["BRFE", "KVST", "LKSV", "TRHF"]
        for symbol in gule:
            rute = re.search(rf'<span class="ticker">{symbol}</span>.*?</a>', html, re.S).group(0)
            assert '<span class="merke">3 av 3 siste børsdag</span>' in rute, symbol
        assert "Gul ramme betyr 3 av 3 på siste børsdag, 09.10" in html

    def test_aksjesiden_uten_kurser_svarer_200_med_beskjed(self, klient):
        """b) MTFJ har ingen kurser i demoen. Ville feilet med 404 (mutant
        N2), uten navnet, bransjen eller beskjeden, eller med graf eller
        sjekker."""
        svar = klient.get("/aksje/MTFJ")
        assert svar.status_code == 200
        html = svar.data.decode("utf-8")
        assert '<h1 class="overskrift">Matfjord Merkevarer</h1>' in html
        assert '<span class="merke">MTFJ</span>' in html and "Konsum</span>" in html
        assert "Det finnes ingen kurser for Matfjord Merkevarer ennå" in html
        assert "I demoen mangler kursene med vilje." in html and "Eksempeltall" in html
        assert '<svg class="graf"' not in html and "Kursutvikling" not in html
        assert "sjekkort" not in html and "Signalet dag for dag" not in html

    def test_aksjesiden_uten_kurser_med_dag_i_adressen(self, klient):
        """b) Lenken fra børsometeret en annen dag har ?dag=. Ville feilet med
        en feilside for den adressen."""
        assert 'href="/aksje/MTFJ?dag=2026-10-08"' in _side(klient, "/boersometer?dag=2026-10-08")
        assert "Det finnes ingen kurser for Matfjord Merkevarer ennå" in _side(klient, "/aksje/MTFJ?dag=2026-10-08")

    def test_et_ukjent_symbol_gir_fortsatt_404(self, klient):
        """b) 404 er fortsatt forbeholdt et symbol som ikke er i lista.
        Ville feilet hvis alle symboler fikk siden uten kurser."""
        assert klient.get("/aksje/FINNESIKKE").status_code == 404

    def test_navnet_under_tabellen_lenker_til_aksjesiden(self, klient):
        """b) Oversikten og «Alle» i Min liste. Ville feilet hvis navnet sto
        uten lenke, eller lenket til en side som gir 404."""
        lenke = '<a href="/aksje/MTFJ">Matfjord Merkevarer</a>'
        assert lenke in _side(klient, "/")
        assert lenke in _side(klient, "/min-liste?vis=alle")

    def test_gult_bare_fra_sidens_siste_boersdag(self, klient):
        """Gjennomgangen 23.10 (ECH1): BRFE mangler kurs og vurdering 09.10,
        sidens siste børsdag, som når hentingen feilet for den, og får 3 av 3
        08.10 i kopien av demobasen. Ville feilet hvis gult kom fra aksjens
        egen siste kursdag og sto 08.10 eller 18.09."""
        tilkobling = sqlite3.connect(demo_sti())
        try:
            tilkobling.execute("DELETE FROM kurs WHERE symbol = 'BRFE' AND dato = '2026-10-09'")
            tilkobling.execute("DELETE FROM vurdering WHERE symbol = 'BRFE' AND dato = '2026-10-09'")
            tilkobling.execute(
                "UPDATE vurdering SET styrke = 3, retning = 'Negativ', trend = -1, bevegelse = -1, interesse = -1"
                " WHERE symbol = 'BRFE' AND dato = '2026-10-08'"
            )
            tilkobling.commit()
        finally:
            tilkobling.close()
        for adresse in ("/boersometer", "/boersometer?dag=2026-10-08", "/boersometer?dag=2026-09-18"):
            html = _side(klient, adresse)
            assert "fredag 09.10" in html or "?dag=" in adresse
            gule = {symbol for klasser, symbol in _ruter(html) if "ramme-gul" in klasser}
            assert gule == {"KVST", "LKSV", "TRHF"}, adresse

    def test_hjelpen_sier_det_samme(self):
        """Gjennomgangen 23.10 (VG3): hjelpen i appen og docs/hjelp.md følger
        svarene (regel 19). Ville feilet med den gamle teksten om ingen
        aksjeside, eller om ingen ramme en dag uten vurdering."""
        from hjelpetekster import hjelpetekster

        tekster = hjelpetekster(STANDARD)
        assert "også når du velger en annen dag" in tekster["boersometeret"].tekst
        assert "med lenke til aksjesiden" in tekster["uten_data"].tekst
        hjelp = (Path(__file__).resolve().parents[1] / "docs" / "hjelp.md").read_text(encoding="utf-8")
        assert "også en dag uten vurdering" in hjelp
        assert "For en aksje uten kurser sier aksjesiden at det ikke finnes kurser ennå" in hjelp
        assert "har ingen aksjeside" not in hjelp and "uten ramme" not in hjelp
