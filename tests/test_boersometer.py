"""Story 8.6: børsometeret (FR-106, avgjørelsen 22.10 kl. 23:19).

Basene lages bare i tmp_path (regel 22), og ingen test går på nett (AD-8).
Hvert kontrollpunkt er prøvd med en mutant (spesifikasjonen, Mutantene).
"""

import ast
import random
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
    BRED,
    GUL,
    HOEY,
    KANT,
    LAV,
    LYS_NED,
    LYS_OPP,
    MINSTE_RUTE,
    MINSTE_VEKT,
    MOERK,
    NOEYTRAL,
    OVERSKRIFT,
    SMAL,
    STERK_NED,
    STERK_OPP,
    STOERSTE_VEKT,
    UTEN_DATA,
    VANLIG,
    Rute,
    bygg_boersometer,
    bygg_rute,
    dagen_foer,
    fargetrinn,
    indeks_for_dagen,
    kart,
    ramme,
    rekkefoelge,
    snitt,
    squarify,
    stoerrelse,
    tekstnivaa,
    vekt,
    vis_volumforhold,
)
from kursdata import Aksje, Kursrad
from lagring_sqlite import SqliteIndekslager, SqliteOversiktsleser, demo_sti
from markedsoversikt import IKKE_VURDERT
from signalberegning import INGEN, POSITIV, STANDARD
from tallformat import avrundet, tall
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
        # Gruppens svar 26.10 kl. 13:00 (a): kartet står ikke lenger i §4-rekkefølgen.
        energi = re.search(
            r'<section class="bransje"(?:(?!</section>).)*?Energi</span>.*?</section>', html, re.S
        ).group(0)
        endringer = [
            float(e.replace(",", ".").replace(" %", ""))
            for e in re.findall(r'<span class="endring">([^<]+)</span>', energi)
        ]
        assert len(endringer) == 4
        vist = re.search(r'<span class="snitt [a-z]+">([^<]+)</span>', energi).group(1)
        # Fra de avrundede endringene kan snittet avvike med en halv hundredel.
        assert abs(float(vist.replace(",", ".").replace(" %", "")) - sum(endringer) / 4) <= 0.006

    def test_1_aksje_der_bransjen_har_en(self, klient):
        """Ville feilet med «1 aksjer», eller uten merket. Gruppens svar
        26.10 kl. 13:00 (b): antallet står i tabellen, ikke i overskriften."""
        html = _side(klient)
        overskrifter = _overskrifter(html)
        assert overskrifter["Industri"].endswith("1 aksje")
        assert "aksjer" not in overskrifter["Energi"]
        assert "Energi (4 aksjer, snitt" in html
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
            # Story 8.2a, f: linja begynner ikke lenger med «Bare».
            linja = re.search(r'<p class="alle-sjekkene">(.*?)</p>', oversikt, re.S).group(1)
            assert navn in re.search(r"</span> (.*?) fikk utslag på alle", linja).group(1)

    def test_arealet_foelger_volumforholdet_i_tabellen(self, klient):
        """Story 8.6b, d erstatter testen for de tre faste størrelsene: arealet
        av ruta følger vekten, volumforholdet i tabellen mellom MINSTE_VEKT og
        STOERSTE_VEKT. Ville feilet hvis arealet ikke fulgte volumforholdet i
        tabellen (mutant 2, arealet uten vekten)."""
        html = _side(klient)
        tabell = html.split('<table class="boersometertabell">')[1]
        rader = re.findall(r'href="/aksje/([A-Z0-9]+)">.*?</td>\s*<td>[^<]*</td>\s*<td>([^<]*)</td>', tabell, re.S)
        assert len(rader) == 15
        vekter = {}
        for symbol, volum in rader:
            treff = re.match(r"([0-9]+,[0-9]+)", volum)
            forhold = float(treff.group(1).replace(",", ".")) if treff else 1.0
            vekter[symbol] = min(max(forhold, MINSTE_VEKT), STOERSTE_VEKT)
        assert len({round(v, 2) for v in vekter.values()}) > 5
        for felt in _kartet(html)["felt"]:
            if len(felt["ruter"]) < 2:
                continue
            for navn in ("bred", "smal"):
                arealer = {sym: r[navn][2] * r[navn][3] for sym, r in felt["ruter"].items()}
                sum_a, sum_v = sum(arealer.values()), sum(vekter[sym] for sym in arealer)
                for sym, areal in arealer.items():
                    # Tabellen viser volumforholdet med to desimaler, derfor 1 %.
                    assert areal / sum_a == pytest.approx(vekter[sym] / sum_v, rel=1e-2), (navn, sym)

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

    def test_linja_mot_boersen_staar_over_rutene(self, klient):
        """Story 8.6b, b erstatter testen for hovedindeksen over rutene:
        hovedindeksen står som et tall i linja «Mål mot børsen» (avgjørelsen
        24.10 kl. 11:54). Ville feilet hvis linja manglet eller sto under
        rutene."""
        html = _side(klient)
        assert html.index('<section class="maal"') < html.index('<section class="bransje"')

    def test_ingen_raad_og_ingen_ki(self, klient):
        """NFR-06. Ville feilet med kjøp eller selg på siden utenom hjelpen,
        eller med KI-tekst (gjennomgangen, VG11)."""
        html = _side(klient)
        # Story 8.6b, a: forklaringen sier at bildet ikke er et råd, med
        # «kjøpe eller selge». Den setningen tas ut, og resten prøves.
        html = html.replace(FORKLARINGEN, "")
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
        """Gjennomgangen (VG6), med kartet fra 8.6b, d: kartet er så bredt som
        siden og har plassen i prosent, så det ruller ikke vannrett. Ville
        feilet med en fast bredde i px på kartet eller rutene, tabellen uten
        rullboksen, eller rutene uten fokus, skjult navn og tabellen uten
        caption og scope."""
        stil = (SRC / "static" / "stil.css").read_text(encoding="utf-8")
        kartregel = re.search(r"\.kart \{([^}]*)\}", stil).group(1)
        assert "aspect-ratio: var(--forhold-bred)" in kartregel and "width:" not in kartregel
        # 1 px er teksten som skjules for øyet.
        assert not re.search(r"\.rute[^{]*\{[^}]*width: (?!1px)\d+px", stil)
        assert re.search(r"\.rute:focus-visible \{[^}]*outline", stil)
        # Gjennomgangen 26.10 (BH, ECH): ville feilet med outline-offset: 0, der
        # ringen ligger inntil den mørke rammen og bare ser ut som en tykkere ramme.
        assert re.search(r"\.rute:focus-visible \{[^}]*outline-offset: 2px", stil)
        html = _side(klient)
        assert (
            '<div class="tabellboks boersometerboks" role="region" aria-label="Børsometeret som tabell" tabindex="0">'
            in html
        )
        assert "<caption>Børsometeret 09.10 som tabell</caption>" in html and html.count('scope="col"') >= 5
        assert '<span class="skjult">, Brattfjell Energi, volum høyt</span>' in html

    def test_tabellen_er_lukket_bak_se_tallene_som_tabell(self, klient):
        """Gruppens svar 26.10 kl. 15:21 (f): tabellen under kartet er lukket
        som standard, bak «Se tallene som tabell», og skjermleseren finner
        knappen. Ville feilet med tabellen åpen, uten summary, med tabellen
        utenfor details, eller med fotnoten inne i den lukkede delen."""
        for adresse in ("/boersometer", "/boersometer?dag=2026-10-08", "/boersometer?dag=2026-09-18"):
            html = _side(klient, adresse)
            details = re.findall(r"<details[^>]*>", html)
            assert details == ['<details class="tallene">'], (adresse, details)
            tallene = html.split('<details class="tallene">', 1)[1].split("</details>", 1)
            assert tallene[0].lstrip().startswith("<summary>Se tallene som tabell</summary>")
            assert '<table class="boersometertabell">' in tallene[0] and "</table>" in tallene[0]
            assert html.count('<table class="boersometertabell">') == 1
            assert "fotnote" not in tallene[0]
            # Kartet og «Hva fargene betyr» står over, utenfor details.
            assert html.index('<section class="fargene"') < html.index('<details class="tallene">')
        fotnote = _side(klient, "/boersometer?dag=2026-09-18")
        assert _fotnoten(fotnote) and fotnote.index("</details>") < fotnote.index('<p class="fotnote">')
        stil = (SRC / "static" / "stil.css").read_text(encoding="utf-8")
        assert re.search(r"details\.tallene > summary:focus-visible \{[^}]*outline", stil)
        assert "display: none" not in re.search(r"details\.tallene > summary \{([^}]*)\}", stil).group(1)

    def test_tabellen_er_aapen_naar_den_staar_alene(self, klient, monkeypatch):
        """Gruppens svar 26.10 kl. 15:21 (f), med NFR-03: får rutene ikke
        plass, står tabellen alene og er åpen. Ville feilet hvis siden da
        bare viste en lukket knapp."""
        monkeypatch.setattr(app_modul, "kart", lambda bransjer: boersometer.kart([]))
        html = _side(klient)
        assert '<details class="tallene" open>' in html

    def test_hjelpen_sier_det_om_tabellen(self):
        """Regel 19: ville feilet hvis docs/hjelp.md ikke sa at tabellen står
        bak «Se tallene som tabell» og er lukket (svaret kl. 15:21, f)."""
        hjelp = (Path(__file__).resolve().parents[1] / "docs" / "hjelp.md").read_text(encoding="utf-8")
        avsnitt = hjelp.split("### Hva viser børsometeret?", 1)[1].split("###", 1)[0]
        assert "bak «Se tallene som tabell». Den er lukket til du åpner den" in avsnitt

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
            # Story 8.2a, c: symbolene over søylene er også lenker, så ruta
            # letes etter under søylene.
            ruter = html.split("</figure>", 1)[-1]
            rute = re.search(rf'<span class="ticker">{symbol}</span>.*?</a>', ruter, re.S).group(0)
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

    def test_hjelpen_sier_det_fotnoten_sier(self):
        """Gjennomgangen av 3.4d 23.10 (VG2): docs/hjelp.md følger fotnoten
        (regel 19). Ville feilet uten kvelder uten henting, eller uten
        børsometeret blant sidene med fotnoten."""
        hjelp = (Path(__file__).resolve().parents[1] / "docs" / "hjelp.md").read_text(encoding="utf-8")
        assert (
            "I den ekte versjonen lagres signalet bare den kvelden kursene hentes, og regnes aldri ut "
            "bakover. Det gjelder dagene før første henting, kvelder uten henting, og dager der kursene "
            "er lest inn med `--les-inn`."
        ) in hjelp
        assert "Står «ikke vurdert» på oversikten, aksjesiden eller børsometeret, sier en fotnote hvorfor" in hjelp


# --- Gruppens svar 23.10 kl. 11:44 (b) -------------------------------------


def _fotnoten(html: str) -> str | None:
    """Fotnoten for «ikke vurdert», uten taggene og med ett mellomrom mellom
    ordene, eller None når den ikke står."""
    treff = re.search(r'<p class="fotnote">\s*«Ikke vurdert»(.*?)</p>', html, re.DOTALL)
    if not treff:
        return None
    return "«Ikke vurdert»" + re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", treff.group(1))).rstrip()


class TestFotnoten:
    """Story 3.4d: fotnoten står også på børsometeret når en rute sier «ikke
    vurdert», med samme tekster som på aksjesiden og oversikten."""

    DEMOTEKST = (
        "«Ikke vurdert»: i demoen starter vurderingene mandag 21.09, slik den ekte versjonen har signal fra "
        "første henting."
    )
    EKTE_TEKST = (
        "«Ikke vurdert»: signalet lagres bare den kvelden kursene hentes, og regnes aldri ut bakover. Det gjelder "
        "dagene før første henting, kvelder uten henting, og dager der kursene er lest inn med --les-inn."
    )

    def test_demoen_foer_startdagen_har_fotnoten(self, klient):
        """Ville feilet hvis fotnoten var borte fra børsometeret (M2 i 3.4d c)."""
        html = _side(klient, "/boersometer?dag=2026-09-18")
        assert f'<span class="tekst">{IKKE_VURDERT}</span>' in html
        assert _fotnoten(html) == self.DEMOTEKST

    def test_ingen_fotnote_uten_en_rute_som_sier_ikke_vurdert(self, klient):
        """Siste demodag har vurdering for alle aksjene med kurs, og MTFJ sier
        «Uten data». Ville feilet hvis fotnoten sto på hver side."""
        html = _side(klient)
        assert f'<span class="tekst">{IKKE_VURDERT}</span>' not in html
        assert _fotnoten(html) is None

    def test_den_ekte_versjonen_har_den_ekte_teksten(self, monkeypatch, basemal):
        """Ville feilet med demoteksten i den ekte versjonen, eller uten
        fotnoten på børsometeret."""
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
        html = _side(app_modul.app.test_client(), "/boersometer?dag=2026-09-18")
        assert _fotnoten(html) == self.EKTE_TEKST

    def test_datoen_i_fotnoten_kommer_fra_startdag(self, klient, monkeypatch):
        """Gjennomgangen av 3.4d (VG1). Ville feilet med datoen skrevet fast i
        malen i stedet for STARTDAG (M1 i 3.4d c)."""
        monkeypatch.setattr(app_modul, "STARTDAG", date(2026, 9, 29))
        html = _side(klient, "/boersometer?dag=2026-09-18")
        assert "i demoen starter vurderingene tirsdag 29.09," in _fotnoten(html)


class TestFotnotenEtterStartdagen:
    """Story 3.4e: demoteksten bare for en dag før STARTDAG, og setningen om
    i dag på børsometeret."""

    @staticmethod
    def _uten_vurdering(sti: Path, symbol: str, dato: str) -> None:
        tilkobling = sqlite3.connect(sti)
        try:
            tilkobling.execute("DELETE FROM vurdering WHERE symbol = ? AND dato = ?", (symbol, dato))
            tilkobling.commit()
        finally:
            tilkobling.close()

    def test_demoen_etter_startdagen_har_den_ekte_teksten(self, klient):
        """KVST uten vurdering 08.10, etter STARTDAG. Ville feilet hvis
        demoteksten sto for alle dager i demoen (M1 i 3.4e c)."""
        self._uten_vurdering(demo_sti(), "KVST", "2026-10-08")
        html = _side(klient, "/boersometer?dag=2026-10-08")
        assert _fotnoten(html) == TestFotnoten.EKTE_TEKST

    def test_setningen_om_i_dag(self, monkeypatch, basemal):
        """Den ekte versjonen, KVST uten vurdering 09.10, og klokka er 09.10
        kl. 20 i Oslo. Ville feilet hvis setningen om i dag manglet, eller
        sto en annen dag (M2 i 3.4e c)."""
        sti = Path(lagring_sqlite.BASE_STI)
        sti.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(basemal, sti)
        tilkobling = sqlite3.connect(sti)
        try:
            tilkobling.execute("PRAGMA application_id = 0")
            tilkobling.commit()
        finally:
            tilkobling.close()
        self._uten_vurdering(sti, "KVST", "2026-10-09")
        monkeypatch.delenv(app_modul.I_DEMO, raising=False)
        monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
        klient = app_modul.app.test_client()
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 9, 18, 0, tzinfo=timezone.utc))
        setningen = " Signalet for denne dagen kan fortsatt lagres hvis hentingen kjøres ferdig før neste børsdag."
        assert _fotnoten(_side(klient)) == TestFotnoten.EKTE_TEKST + setningen
        # Gjennomgangen 23.10 kveld (BH6, VG2): fredagen lest lørdag, etter
        # svaret kl. 19:10. Ville feilet hvis børsometeret bare ga setningen i dag.
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc))
        assert _fotnoten(_side(klient)) == TestFotnoten.EKTE_TEKST + setningen
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc))
        assert _fotnoten(_side(klient)) == TestFotnoten.EKTE_TEKST


# --- Story 8.6b: børsometeret som tavla ------------------------------------

FORKLARINGEN = (
    "Hver rute er en aksje, samlet etter bransje. Fargen viser endringen fra børsdagen før, og jo større ruta "
    "er, jo mer ble aksjen omsatt sammenlignet med vanlig. Klikk på en rute for å se aksjen. Bildet viser hva "
    "som skjedde, ikke hva du bør kjøpe eller selge."
)


class TestForklaringen:
    """8.6b, a (avgjørelsen 24.10 kl. 11:54)."""

    def test_forklaringen_staar_oeverst(self, klient):
        """Ville feilet hvis forklaringen manglet, var endret, eller sto under
        rutene."""
        html = _side(klient)
        assert f'<p class="innledning">{FORKLARINGEN}</p>' in html
        assert html.index(FORKLARINGEN) < html.index('<section class="bransje"')
        # Også en annen dag.
        assert FORKLARINGEN in _side(klient, "/boersometer?dag=2026-09-18")


def _maal(html: str) -> list[str]:
    """Punktene i linja «Mål mot børsen», uten taggene. Bare vanlige
    mellomrom slås sammen, så det harde mellomrommet foran % står (regel 21)."""
    linja = re.search(r'<section class="maal".*?</section>', html, re.S).group(0)
    punkter = re.findall(r"<li>(.*?)</li>", linja, re.S)
    return [re.sub(r"[ \t\r\n]+", " ", re.sub(r"<[^>]+>", "", li)).strip() for li in punkter]


def _demoindeksen() -> list[Kursrad]:
    tilkobling = sqlite3.connect(demo_sti())
    try:
        lager = SqliteIndekslager(tilkobling)
        return lager.serie(lager.symboler()[0])
    finally:
        tilkobling.close()


class TestLinjaMotBoersen:
    """8.6b, b (avgjørelsen 24.10 kl. 11:54)."""

    def test_de_tre_punktene(self, klient):
        """09.10 er en fredag, og børsdagen før er torsdag. Ville feilet med
        en annen ukedag, et annet vindu enn de 20 børsdagene før, eller uten
        hovedindeksen."""
        punkter = _maal(_side(klient))
        assert STANDARD.volum_vindu == 20
        assert punkter[:2] == ["Farge · endring fra torsdag", "Størrelse · volum mot medianen for de 20 børsdagene før"]
        assert punkter[2].startswith("Hovedindeksen · ")
        assert len(punkter) == 3
        # Mandag 05.10: børsdagen før er fredag.
        assert _maal(_side(klient, "/boersometer?dag=2026-10-05"))[0] == "Farge · endring fra fredag"

    @pytest.mark.parametrize("dag", [None, "2026-10-08", "2026-09-18"])
    def test_tallet_i_linja_er_endringen_den_dagen(self, klient, dag):
        """Tallet med fortegn og farge for dagen som vises. Ville feilet med
        endringen for siste børsdag på en annen dag, uten fortegn, eller med
        feil farge."""
        html = _side(klient, f"/boersometer?dag={dag}" if dag else "/boersometer")
        dagen = date.fromisoformat(dag) if dag else date(2026, 10, 9)
        endring = indeks_for_dagen(_demoindeksen(), dagen)
        assert endring is not None
        assert _maal(html)[2] == f"Hovedindeksen · {tall(endring, 'endring')}"
        vist = avrundet(endring, "endring")
        farge = "opp" if vist > 0 else "ned" if vist < 0 else "null"
        assert f'<span class="indeksendring {farge}">{tall(endring, "endring")}</span>' in html
        assert tall(endring, "endring")[0] in "+-" or vist == 0

    def test_tallene_er_ulike_dag_for_dag(self, klient):
        """Ville feilet hvis linja viste samme tall for hver dag, som når den
        bare hadde siste børsdag."""
        tallene = {_maal(_side(klient, f"/boersometer?dag=2026-10-0{d}"))[2] for d in (5, 6, 7, 8, 9)}
        assert len(tallene) > 1

    def test_strek_naar_indeksen_mangler_dagen(self, klient):
        """Ville feilet med et tall fra en annen dag, eller en feilside, når
        indeksen ikke har en rad for dagen."""
        tilkobling = sqlite3.connect(demo_sti())
        try:
            tilkobling.execute("DELETE FROM indeks WHERE dato = '2026-10-08'")
            tilkobling.commit()
        finally:
            tilkobling.close()
        assert _maal(_side(klient, "/boersometer?dag=2026-10-08"))[2] == "Hovedindeksen · –"
        # 09.10 mangler nå børsdagen før, og har heller ingen endring.
        assert _maal(_side(klient))[2] == "Hovedindeksen · –"

    def test_strek_uten_indeks_i_basen(self, klient):
        """Ville feilet med en feilside når basen ikke har en indeks."""
        tilkobling = sqlite3.connect(demo_sti())
        try:
            tilkobling.execute("DELETE FROM indeks")
            tilkobling.execute("DELETE FROM indeksserie")
            tilkobling.commit()
        finally:
            tilkobling.close()
        assert _maal(_side(klient))[2] == "Hovedindeksen · –"

    def test_strek_naar_indeksen_ikke_kan_leses(self, klient, monkeypatch):
        """NFR-03: ville feilet med en feilside når indeksen ikke kan leses."""

        def feil(*_a, **_k):
            raise sqlite3.OperationalError("låst")

        monkeypatch.setattr(SqliteIndekslager, "symboler", feil)
        html = _side(klient)
        assert _maal(html)[2] == "Hovedindeksen · –" and '<section class="bransje"' in html

    def test_ingen_soeyler_paa_boersometeret(self, klient):
        """Søylene og _hovedindeks.html er tatt ut av børsometeret, ikke av
        oversikten. Ville feilet med søylene eller delen for hovedindeksen på
        børsometeret, eller uten dem på oversikten."""
        for adresse in ("/boersometer", "/boersometer?dag=2026-10-08"):
            html = _side(klient, adresse)
            assert '<figure class="soeyler"' not in html and '<section class="hovedindeks"' not in html, adresse
            assert 'id="hjelp-hovedindeks"' not in html
        oversikt = _side(klient, "/")
        assert '<section class="hovedindeks"' in oversikt and '<figure class="soeyler"' in oversikt
        mal = (SRC / "templates" / "boersometer.html").read_text(encoding="utf-8")
        assert "_hovedindeks.html" not in mal

    def test_dagen_foer(self):
        """Ville feilet med dagen selv, en dag etter, eller en dag uten kurs."""
        datoer = [date(2026, 10, 1), date(2026, 10, 2), date(2026, 10, 5)]
        assert dagen_foer(datoer, date(2026, 10, 5)) == date(2026, 10, 2)
        assert dagen_foer(datoer, date(2026, 10, 1)) is None

    @pytest.mark.parametrize(
        ("foer", "ventet"),
        [
            (date(2026, 10, 8), "torsdag"),
            (date(2026, 10, 3), "lørdag"),
            (date(2026, 10, 2), "02.10"),
            (date(2025, 9, 26), "26.09.2025"),
            (None, "børsdagen før"),
        ],
    )
    def test_datoen_naar_dagen_foer_er_mer_enn_6_dager_foer(self, foer, ventet):
        """Gjennomgangen 26.10 (ECH4): ville feilet hvis linja sa ukedagen for
        en dag mer enn 6 dager før, som ville sett ut som dagen i samme uke."""
        assert boersometer.vis_dagen_foer(foer, date(2026, 10, 9), 2026) == ventet

    def test_datoen_i_linja_paa_siden(self, klient, monkeypatch):
        """Gjennomgangen 26.10 (ECH4): ville feilet hvis siden skrev ukedagen
        når børsdagen før er 10 dager før dagen som vises."""
        monkeypatch.setattr(app_modul, "dagen_foer", lambda datoer, dag: date(2026, 9, 29))
        assert _maal(_side(klient))[0] == "Farge · endring fra 29.09"

    def test_foerste_dag_uten_dag_foer(self, klient):
        """Ville feilet med en tom ukedag den første dagen med kurs."""
        assert _maal(_side(klient, "/boersometer?dag=1990-01-01"))[0] == "Farge · endring fra børsdagen før"

    def test_hjelpen_sier_det(self):
        """Regel 19: ville feilet hvis hjelpen i appen eller docs/hjelp.md
        ikke nevnte linja, eller sa at søylene sto på børsometeret."""
        from hjelpetekster import hjelpetekster

        tekst = hjelpetekster(STANDARD)["boersometeret"].tekst
        assert "linja «Mål mot børsen» har endringen i hovedindeksen den dagen" in tekst
        hjelp = (Path(__file__).resolve().parents[1] / "docs" / "hjelp.md").read_text(encoding="utf-8")
        avsnitt = hjelp.split("### Hva viser børsometeret?", 1)[1].split("###", 1)[0]
        assert "Linja «Mål mot børsen»" in avsnitt and "Søylene står bare på oversikten." in avsnitt


def _rot(stil: str) -> dict[str, str]:
    """Navnene i :root i stil.css med verdien."""
    rot = re.search(r":root\s*\{(.*?)\}", stil, re.S).group(1)
    return {navn: verdi.strip() for navn, verdi in re.findall(r"(--[\w-]+):\s*([^;]+);", rot)}


def _kontrast(a: str, b: str) -> float:
    """Kontrasten mellom to farger etter WCAG 2.x."""

    def lys(farge: str) -> float:
        kanaler = [int(farge.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4)]
        kanaler = [k / 12.92 if k <= 0.03928 else ((k + 0.055) / 1.055) ** 2.4 for k in kanaler]
        return 0.2126 * kanaler[0] + 0.7152 * kanaler[1] + 0.0722 * kanaler[2]

    lyse, moerke = sorted((lys(a), lys(b)), reverse=True)
    return (lyse + 0.05) / (moerke + 0.05)


class TestFargetrinnene:
    """8.6b, c (avgjørelsen 24.10 kl. 11:54)."""

    @pytest.mark.parametrize(
        ("endring", "ventet"),
        [
            (None, None),
            (0.0, NOEYTRAL),
            (-0.004, NOEYTRAL),
            (0.4949, NOEYTRAL),
            (-0.4949, NOEYTRAL),
            (0.4951, LYS_OPP),
            (0.5, LYS_OPP),
            (-0.5, LYS_NED),
            (-0.4951, LYS_NED),
            (1.99, LYS_OPP),
            (1.9949, LYS_OPP),
            (-1.9949, LYS_NED),
            (1.9951, STERK_OPP),
            (2.0, STERK_OPP),
            (-2.0, STERK_NED),
            (-1.9951, STERK_NED),
            (12.0, STERK_OPP),
            (-12.0, STERK_NED),
        ],
    )
    def test_hvert_trinn_ved_grensene(self, endring, ventet):
        """Etter tallet slik det vises, med to desimaler: 0,4951 vises som
        0,50 % og er lys, og 1,9951 vises som 2,00 % og er sterk. Ville
        feilet med grensen 0,5 flyttet til 1 (mutant 1), med «>» i stedet for
        «>=» ved grensene, eller med trinnet fra tallet før avrundingen."""
        assert fargetrinn(endring) == ventet

    def test_hver_rute_har_trinnet_for_tallet_den_viser(self, klient):
        """Ville feilet hvis en rute hadde et annet trinn enn tallet i ruta,
        eller hvis demoen ikke hadde minst tre av trinnene."""
        sett = set()
        for adresse in ("/boersometer", "/boersometer?dag=2026-10-08", "/boersometer?dag=2026-10-05"):
            html = _side(klient, adresse)
            ruter = re.findall(
                r'<a class="rute [^"]*trinn-([a-z-]+)[^"]*"[^>]*>\s*<span class="ticker">([A-Z0-9]+)</span>\s*'
                r'<span class="endring">([^<]+)</span>',
                html,
            )
            assert len(ruter) == 15, adresse
            for trinn, symbol, endring in ruter:
                ventet = "ingen" if endring in ("Uten data", "–") else fargetrinn(_tall(endring))
                assert trinn == ventet, (adresse, symbol, endring)
                sett.add(trinn)
        assert len(sett - {"ingen"}) >= 3, sett

    def test_fargene_er_navn_i_root(self):
        """Ville feilet hvis en av de fem fargene sto rett i en regel og ikke
        som navn i :root, eller hadde en annen verdi."""
        stil = (SRC / "static" / "stil.css").read_text(encoding="utf-8")
        rot = _rot(stil)
        assert rot["--trinn-noeytral"].upper() == "#E9E7E1"
        assert rot["--trinn-lys-opp"].upper() == "#B4E2C4"
        assert rot["--trinn-lys-ned"].upper() == "#F6C2BB"
        for trinn, navn in (
            ("noeytral", "--trinn-noeytral"),
            ("lys-opp", "--trinn-lys-opp"),
            ("lys-ned", "--trinn-lys-ned"),
            ("opp", "--opp"),
            ("ned", "--ned"),
        ):
            regel = re.search(rf"\.trinn-{trinn} \{{([^}}]*)\}}", stil).group(1)
            assert f"background: var({navn})" in regel, trinn
        for trinn in ("opp", "ned"):
            assert "color: var(--hvit)" in re.search(rf"\.trinn-{trinn} \{{([^}}]*)\}}", stil).group(1)
        for farge in ("#E9E7E1", "#B4E2C4", "#F6C2BB"):
            assert stil.upper().count(farge) == 1, farge

    def test_kontrasten(self):
        """Hvit tekst på --opp og --ned og blekk på de lyse trinnene har
        minst 4,5:1, og rammene har minst 3:1 mot hvitt, som er det de grenser
        mot (spesifikasjonen, «Kontrasten mot ruta»). Ville feilet med en
        farge som ikke leses, eller en ramme uten den hvite linja innenfor."""
        stil = (SRC / "static" / "stil.css").read_text(encoding="utf-8")
        rot = _rot(stil)
        for navn in ("--opp", "--ned"):
            assert _kontrast(rot["--hvit"], rot[navn]) >= 4.5, navn
        for navn in ("--trinn-noeytral", "--trinn-lys-opp", "--trinn-lys-ned"):
            assert _kontrast(rot["--blekk"], rot[navn]) >= 4.5, navn
        for navn in ("--blekk", "--gul-symbol"):
            assert _kontrast(rot[navn], rot["--hvit"]) >= 3, navn
        regel = re.search(r"\.rute\.ramme-gul, [^{]*\{([^}]*)\}", stil).group(1)
        assert "border: 4px solid" in regel and "box-shadow: inset 0 0 0 2px var(--hvit)" in regel
        assert re.search(r"\.rute\.ramme-gul, [^{]*\{ border-color: var\(--gul-symbol\); \}", stil)

    def test_rammen_staar_ogsaa_uten_data(self):
        """Rammen kommer etter regelen for en rute uten endring og har like
        høy spesifisitet, så gult står også på en rute med «Uten data»
        (svarene 23.10 kl. 09:24). Ville feilet hvis den grå kanten
        vant over rammen."""
        stil = (SRC / "static" / "stil.css").read_text(encoding="utf-8")
        assert stil.index(".rute.trinn-ingen {") < stil.index(".rute.ramme-gul, ")

    def test_hvert_tall_i_forklaringen_er_prosent(self):
        """Gjennomgangen 26.10 (BH7), regel 21: begge grensene er prosent og
        formateres med samme type. Ville feilet hvis den lyse grensen ble
        formatert som «faktor», uten %."""
        for _, tekst in boersometer.trinnforklaringer():
            tallene = re.findall(r"\d+(?:,\d+)?(\S?)", tekst.replace("\u00a0%", "%"))
            assert tallene and all(etter == "%" for etter in tallene), tekst

    def test_hva_fargene_betyr(self, klient):
        """Under rutene, med de fem trinnene fra fall til stigning og de to
        rammene. Ville feilet hvis forklaringen manglet, sto over rutene, eller
        hadde et annet tall enn grensene."""
        html = _side(klient)
        del_ = re.search(r'<section class="fargene".*?</section>', html, re.S).group(0)
        assert "<h2" in del_ and "Hva fargene betyr</h2>" in del_
        punkter = re.findall(r'<li><span class="proeve ([a-z-]+)" aria-hidden="true"></span>([^<]+)</li>', del_)
        assert punkter == [
            ("trinn-ned", "Ned 2 % eller mer"),
            ("trinn-lys-ned", "Ned fra 0,5 % til under 2 %"),
            ("trinn-noeytral", "Under ±0,5 %"),
            ("trinn-lys-opp", "Opp fra 0,5 % til under 2 %"),
            ("trinn-opp", "Opp 2 % eller mer"),
            ("ramme-moerk", "Mørk ramme: 2 av 3 på siste børsdag"),
            ("ramme-gul", "Gul ramme: 3 av 3 på siste børsdag"),
        ]
        assert html.rindex('<section class="bransje"') < html.index('<section class="fargene"')
        assert html.index('<section class="fargene"') < html.index('<table class="boersometertabell">')

    def test_hjelpen_sier_det(self):
        """Regel 19: ville feilet hvis hjelpen sa to farger, eller manglet
        trinnene og rammen."""
        from hjelpetekster import hjelpetekster

        assert "som farge i fem trinn" in hjelpetekster(STANDARD)["boersometeret"].tekst
        hjelp = (Path(__file__).resolve().parents[1] / "docs" / "hjelp.md").read_text(encoding="utf-8")
        avsnitt = hjelp.split("### Hva viser børsometeret?", 1)[1].split("###", 1)[0]
        assert "Fargen har fem trinn" in avsnitt and "Grønn rute steg og rød falt" not in avsnitt
        assert "Rammen er tykk med en hvit linje innenfor" in avsnitt


_PLASS = r"--x-{n}: ([0-9.]+)%; --y-{n}: ([0-9.]+)%; --b-{n}: ([0-9.]+)%; --h-{n}: ([0-9.]+)%;"


def _plass(stil: str) -> dict[str, tuple[float, ...]]:
    return {n: tuple(map(float, re.search(_PLASS.format(n=n), stil).groups())) for n in ("bred", "smal")}


def _kartet(html: str) -> dict:
    """Kartet slik malen skriver det: forholdet, og for hvert felt plassen,
    overskriften og rutene med plassen, alt i prosent."""
    kartet = re.search(r'<div class="kart" style="([^"]*)">(.*?)\n    </div>', html, re.S)
    forhold = {n: float(v) for n, v in re.findall(r"--forhold-(\w+): ([0-9.]+);", kartet.group(1))}
    felt = []
    for stil, innhold in re.findall(
        r'<section class="bransje"[^>]*style="([^"]*)">(.*?)</section>', kartet.group(2), re.S
    ):
        ruter = {
            symbol: _plass(rstil)
            for rstil, symbol in re.findall(
                r'<li style="([^"]*)"><a class="rute [^"]*"[^>]*>\s*<span class="ticker">([A-Z0-9]+)</span>', innhold
            )
        }
        topp = {n: float(v) for n, v in re.findall(r"--topp-(\w+): ([0-9.]+)%;", stil)}
        felt.append({"plass": _plass(stil), "topp": topp, "ruter": ruter})
    return {"forhold": forhold, "felt": felt}


def _dekker(rektangler: list[tuple[float, ...]], b: float, h: float, eps: float | None = None) -> None:
    """Rektanglene ligger i (0, 0, b, h), overlapper ikke, og dekker alt.
    eps er avrundingen som tåles, som tre desimaler i malen."""
    eps = 1e-6 * max(b, h) if eps is None else eps
    for x, y, rb, rh in rektangler:
        assert x >= -eps and y >= -eps and x + rb <= b + eps and y + rh <= h + eps
    for i, (x1, y1, b1, h1) in enumerate(rektangler):
        for x2, y2, b2, h2 in rektangler[i + 1 :]:
            bredde = min(x1 + b1, x2 + b2) - max(x1, x2)
            hoeyde = min(y1 + h1, y2 + h2) - max(y1, y2)
            assert bredde <= eps or hoeyde <= eps, ((x1, y1, b1, h1), (x2, y2, b2, h2))
    assert sum(rb * rh for _, _, rb, rh in rektangler) == pytest.approx(b * h, rel=1e-9 if eps < 1e-3 else 1e-3)


def _ruter_med(volumforhold: list[float | None], bransjer: list[str] | None = None) -> list[Rute]:
    bransjer = bransjer or [BRANSJER[i % 5] for i in range(len(volumforhold))]
    return [
        Rute(aksje=_aksje(f"S{i}", b), endring=1.0, volumforhold=v, styrke=None, tekst=None)
        for i, (v, b) in enumerate(zip(volumforhold, bransjer, strict=True))
    ]


class TestKartet:
    """8.6b, d (avgjørelsen 24.10 kl. 11:54)."""

    @pytest.mark.parametrize(
        "vekter", [[1.0], [3.0, 1.0], [1.0] * 7, [3.0, 0.5, 0.5, 2.0, 1.2, 0.7, 0.5, 2.9, 1.0], [0.5] * 3 + [3.0] * 3]
    )
    @pytest.mark.parametrize(("b", "h"), [(729, 364.5), (358, 429.6), (100, 400)])
    def test_squarify_dekker_feltet_uten_overlapp_med_areal_etter_vekten(self, vekter, b, h):
        """Ville feilet med rektangler som overlappet, gikk utenfor feltet,
        lot noe stå tomt, eller hadde et annet areal enn vekten sier."""
        rektangler = squarify(vekter, 0, 0, b, h)
        assert len(rektangler) == len(vekter)
        _dekker(rektangler, b, h)
        for (_, _, rb, rh), v in zip(rektangler, vekter, strict=True):
            assert rb * rh / (b * h) == pytest.approx(v / sum(vekter), rel=1e-9)

    def test_squarify_med_minstemaal(self):
        """Også med minstemålet dekker rektanglene feltet med areal etter
        vekten. Ville feilet hvis regelen for minstemålet ga hull eller
        overlapp."""
        vekter = [3.0, 1.0, 0.5, 0.5, 0.6, 2.0]
        rektangler = squarify(vekter, 0, 0, 358, 300, 48)
        _dekker(rektangler, 358, 300)
        for (_, _, rb, rh), v in zip(rektangler, vekter, strict=True):
            assert rb * rh / (358 * 300) == pytest.approx(v / sum(vekter), rel=1e-9)

    @pytest.mark.parametrize(
        ("forhold", "ventet"), [(None, 1.0), (0.0, 0.5), (0.49, 0.5), (0.5, 0.5), (1.7, 1.7), (3.0, 3.0), (8.4, 3.0)]
    )
    def test_vekten(self, forhold, ventet):
        """Ville feilet uten gulvet og taket, eller uten vekten 1 for en
        aksje uten volumforhold."""
        assert vekt(_ruter_med([forhold])[0]) == ventet

    def test_feltene_og_rutene_dekker_kartet_med_areal_etter_vekten(self):
        """Begge nivåene og begge flatene. Ville feilet hvis et felt eller en
        rute overlappet, kartet ikke var dekket, eller arealet ikke fulgte
        summen av vektene og vekten (mutant 2, arealet uten vekten)."""
        ruter = _ruter_med([0.6, 2.4, 1.0, None, 0.8, 1.9, 0.5, 3.0, 1.1, 1.4])
        bransjer = bygg_boersometer(ruter)
        k = kart(bransjer)
        for navn in ("bred", "smal"):
            felt = [f.plass[navn] for f in k.felt]
            _dekker([(p.x, p.y, p.b, p.h) for p in felt], 100, 100)
            totalt = sum(f.vekt for f in k.felt)
            for f in k.felt:
                assert f.plass[navn].b * f.plass[navn].h / 1e4 == pytest.approx(f.vekt / totalt, rel=1e-9)
                assert f.vekt == pytest.approx(sum(vekt(r) for r in f.bransje.ruter))
                _dekker([(p.x, p.y, p.b, p.h) for p in (kr.plass[navn] for kr in f.ruter)], 100, 100)
                for kr in f.ruter:
                    assert kr.plass[navn].b * kr.plass[navn].h / 1e4 == pytest.approx(kr.vekt / f.vekt, rel=1e-9)

    def test_en_rute_per_aksje(self):
        """Ville feilet hvis en aksje manglet eller sto to ganger i kartet."""
        ruter = _ruter_med([1.0] * 11)
        k = kart(bygg_boersometer(ruter))
        symboler = [kr.rute.aksje.symbol for f in k.felt for kr in f.ruter]
        assert sorted(symboler) == sorted(r.aksje.symbol for r in ruter)

    def test_tab_foelger_rekkefoelgen_kartet_legges_i(self):
        """Gruppens svar 26.10 kl. 13:00 (a), gjennomgangen BH2: feltene og
        rutene står i den rekkefølgen squarify legger dem, på begge flatene.
        Ville feilet hvis kartet sto i rekkefølgen i designregler §4, eller
        rutene i et felt i lista sin rekkefølge."""
        rng = random.Random(3)
        for _ in range(40):
            forhold = [rng.lognormvariate(0, 0.8) for _ in range(15)]
            bransjer = bygg_boersometer(_ruter_med(forhold, [BRANSJER[i % 8] for i in range(15)]))
            k = kart(bransjer)
            vekter = [sum(vekt(r) for r in b.ruter) for b in bransjer]
            assert [f.bransje.navn for f in k.felt] == [bransjer[i].navn for i in rekkefoelge(vekter)]
            for f in k.felt:
                assert [kr.vekt for kr in f.ruter] == sorted((kr.vekt for kr in f.ruter), reverse=True)
            for navn in ("bred", "smal"):
                # Den første squarify legger, står øverst til venstre, i kartet og i feltet.
                assert (k.felt[0].plass[navn].x, k.felt[0].plass[navn].y) == (0, 0)
                for f in k.felt:
                    assert (f.ruter[0].plass[navn].x, f.ruter[0].plass[navn].y) == pytest.approx((0, 0), abs=1e-9)

    def test_tab_paa_siden_foelger_kartet_og_tabellen_designreglene(self, klient):
        """Gruppens svar 26.10 kl. 13:00 (a): i HTML-en kommer det største
        feltet og den største ruta først, og tabellen under har rekkefølgen
        i designregler §4. Ville feilet hvis malen skrev kartet i
        §4-rekkefølgen, eller tabellen fulgte kartet."""
        for adresse in ("/boersometer", "/boersometer?dag=2026-10-08"):
            html = _side(klient, adresse)
            kartet = _kartet(html)
            for navn in ("bred", "smal"):
                arealer = [f["plass"][navn][2] * f["plass"][navn][3] for f in kartet["felt"]]
                assert all(a >= b * 0.999 for a, b in zip(arealer, arealer[1:], strict=False)), (adresse, navn, arealer)
                assert kartet["felt"][0]["plass"][navn][:2] == (0, 0)
                for f in kartet["felt"]:
                    ruter = [p[navn][2] * p[navn][3] for p in f["ruter"].values()]
                    assert all(a >= b * 0.999 for a, b in zip(ruter, ruter[1:], strict=False)), (adresse, navn, ruter)
            i_kartet = list(_overskrifter(html))
            tabell = html.split('<table class="boersometertabell">', 1)[1]
            i_tabellen = list(dict.fromkeys(re.findall(r"<tr>\s*<td>([A-ZÆØÅa-zæøå]+)", tabell)))
            assert sorted(i_kartet) == sorted(i_tabellen)
            assert i_tabellen == sorted(i_tabellen, key=BRANSJER.index)
            assert i_kartet != i_tabellen, "demoen skal vise at kartet ikke følger §4"

    def test_hjelpen_sier_rekkefoelgen(self):
        """Regel 19: ville feilet hvis hjelpen ved «?» eller docs/hjelp.md
        ikke sa at Tab følger kartet (gruppens svar 26.10 kl. 13:00, a)."""
        from hjelpetekster import hjelpetekster

        tekst = hjelpetekster(STANDARD)["boersometeret"].tekst
        assert "med Tab går du fra det største feltet og den største ruta, slik kartet legger dem." in tekst
        hjelp = (Path(__file__).resolve().parents[1] / "docs" / "hjelp.md").read_text(encoding="utf-8")
        avsnitt = hjelp.split("### Hva viser børsometeret?", 1)[1].split("###", 1)[0]
        assert "Med Tab går du gjennom kartet fra det største feltet" in avsnitt
        assert "tabellen har bransjene i fast rekkefølge" in avsnitt

    def test_ingen_plass_er_negativ(self):
        """Gjennomgangen 26.10 (ECH): ville feilet med y = -2,6e-14 for den
        første raden i et felt, som malen skrev som «-0.000%». Dagene er
        faste, og med den gamle regningen hadde 109 plasser på 300 slike
        dager et lite negativt tall."""
        rng = random.Random(1)
        for _ in range(60):
            forhold = [rng.lognormvariate(0, 0.8) for _ in range(15)]
            k = kart(bygg_boersometer(_ruter_med(forhold, [BRANSJER[i % 8] for i in range(15)])))
            for f in k.felt:
                for p in [*f.plass.values(), *(q for kr in f.ruter for q in kr.plass.values())]:
                    assert p.x >= 0 and p.y >= 0, p

    def test_tomt_kart(self):
        """Ville feilet med en feil når lista er tom."""
        assert kart([]).felt == ()

    def test_tabellen_staar_naar_rutene_ikke_faar_plass(self, klient, monkeypatch):
        """Gjennomgangen 26.10 (BH, ECH): ville feilet med 500 hvis kart()
        ga opp, i stedet for at tabellen sto alene."""

        def gir_opp(bransjer):
            if bransjer:
                raise ValueError("ingen plass")
            return kart(bransjer)

        monkeypatch.setattr(app_modul, "kart", gir_opp)
        html = _side(klient)
        assert '<section class="bransje"' not in html
        assert html.count('<a href="/aksje/') >= 15

    @pytest.mark.parametrize("forhold", [[1.0] * 15, [3.0] + [0.5] * 14, [0.5, 3.0] * 7 + [1.0]])
    def test_ingen_rute_under_44_px_i_761_px_med_rullefelt(self, forhold):
        """Gjennomgangen 26.10 (ECH): @media regner med rullefeltet, så et
        vindu 761 px bredt med et rullefelt på 17 px har 712 px innhold. Ville
        feilet hvis den brede flaten var regnet ved 729 px."""
        ruter = _ruter_med(forhold, [BRANSJER[i % 8] for i in range(len(forhold))])
        k = kart(bygg_boersometer(ruter))
        bredde = 761 - 17 - 2 * 16
        hoeyde = bredde * k.forhold["bred"]
        for f in k.felt:
            fb, fh = f.plass["bred"].b / 100 * bredde, f.plass["bred"].h / 100 * hoeyde
            kropp = fh * (1 - f.topp["bred"] / 100)
            for kr in f.ruter:
                rb, rh = kr.plass["bred"].b / 100 * fb, kr.plass["bred"].h / 100 * kropp
                assert rb - 2 * KANT >= MINSTE_RUTE - 1e-9 and rh - 2 * KANT >= MINSTE_RUTE - 1e-9, (rb, rh)

    @pytest.mark.parametrize(
        "forhold",
        [
            [1.0] * 15,
            [3.0] + [0.5] * 14,
            [0.5, 3.0] * 7 + [1.0],
            [None] * 15,
            [0.6, 2.4, 1.0, 0.7, 0.8, 1.9, 0.5, 3.0, 1.1, 1.4, 0.9, 2.2, 0.55, 1.3, 2.7],
        ],
    )
    def test_ingen_rute_under_44_px_i_390_px(self, forhold):
        """Med 16 px på hver side er kartet 358 px bredt i et vindu 390 px
        bredt. Ville feilet med en rute under 44 × 44 px der, uten de 2 px
        hvitt på hver side."""
        ruter = _ruter_med(forhold, [BRANSJER[i % 8] for i in range(len(forhold))])
        k = kart(bygg_boersometer(ruter))
        assert SMAL.bredde == 390 - 2 * 16
        bredde = SMAL.bredde
        hoeyde = bredde * k.forhold["smal"]
        for f in k.felt:
            fb, fh = f.plass["smal"].b / 100 * bredde, f.plass["smal"].h / 100 * hoeyde
            kropp = fh - OVERSKRIFT
            assert f.topp["smal"] / 100 * fh == pytest.approx(OVERSKRIFT)
            for kr in f.ruter:
                rb, rh = kr.plass["smal"].b / 100 * fb, kr.plass["smal"].h / 100 * kropp
                assert rb - 2 * KANT >= MINSTE_RUTE - 1e-9 and rh - 2 * KANT >= MINSTE_RUTE - 1e-9, (rb, rh)

    def test_ingen_rute_under_44_px_paa_siden(self, klient):
        """Det malen skriver, for siste børsdag og 08.10 og 18.09. Ville
        feilet hvis malen skrev en annen plass enn kartet regnet."""
        for adresse in ("/boersometer", "/boersometer?dag=2026-10-08", "/boersometer?dag=2026-09-18"):
            kartet = _kartet(_side(klient, adresse))
            assert sum(len(f["ruter"]) for f in kartet["felt"]) == 15, adresse
            bredde = 358
            hoeyde = bredde / kartet["forhold"]["smal"]
            for f in kartet["felt"]:
                fb, fh = f["plass"]["smal"][2] / 100 * bredde, f["plass"]["smal"][3] / 100 * hoeyde
                kropp = fh * (1 - f["topp"]["smal"] / 100)
                for symbol, p in f["ruter"].items():
                    rb, rh = p["smal"][2] / 100 * fb, p["smal"][3] / 100 * kropp
                    assert min(rb, rh) - 2 * KANT >= MINSTE_RUTE - 0.01, (adresse, symbol, rb, rh)

    @pytest.mark.parametrize(
        "forhold",
        [
            [1.0] * 15,
            [3.0] + [0.5] * 14,
            [0.5, 3.0] * 7 + [1.0],
            [0.05] + [12.0] * 14,
            [0.6, 2.4, 1.0, 0.7, 0.8, 1.9, 0.5, 3.0, 1.1, 1.4, 0.9, 2.2, 0.55, 1.3, 2.7],
        ],
    )
    def test_ingen_rute_under_24_px_i_320_px(self, forhold):
        """Gruppens svar 26.10 kl. 08:43 (c), WCAG 2.2, 2.5.8: i et vindu 320
        px bredt er kartet 288 px bredt, og prosentene krymper med det, men
        ikke de 2 px hvitt rundt ruta. Ville feilet hvis en rute ble mindre
        enn 24 × 24 px der."""
        ruter = _ruter_med(forhold, [BRANSJER[i % 8] for i in range(len(forhold))])
        k = kart(bygg_boersometer(ruter))
        bredde = 320 - 2 * 16
        hoeyde = bredde * k.forhold["smal"]
        for f in k.felt:
            fb, fh = f.plass["smal"].b / 100 * bredde, f.plass["smal"].h / 100 * hoeyde
            kropp = fh * (1 - f.topp["smal"] / 100)
            for kr in f.ruter:
                rb, rh = kr.plass["smal"].b / 100 * fb, kr.plass["smal"].h / 100 * kropp
                assert rb - 2 * KANT >= 24 and rh - 2 * KANT >= 24, (rb, rh)

    def test_kartet_paa_siden_dekker_feltene(self, klient):
        """Ville feilet hvis feltene eller rutene i malen overlappet eller lot
        noe stå tomt."""
        kartet = _kartet(_side(klient))
        for navn in ("bred", "smal"):
            _dekker([f["plass"][navn] for f in kartet["felt"]], 100, 100, eps=0.002)
            for f in kartet["felt"]:
                _dekker(list(p[navn] for p in f["ruter"].values()), 100, 100, eps=0.002)

    @pytest.mark.parametrize(
        ("b", "h", "symbol", "ventet"),
        [
            (40, 60, "BRFE", 0),
            (46, 60, "BRFE", 1),
            (100, 39, "BRFE", 0),
            (73, 100, "BRFE", 1),
            (74, 60, "BRFE", 2),
            (95, 100, "BRFE", 2),
            (96, 88, "BRFE", 3),
            (54, 60, "NORSE", 0),
            (55, 60, "NORSE", 1),
        ],
    )
    def test_navnet_staar_paa_ruter_som_er_store_nok(self, b, h, symbol, ventet):
        """Ville feilet hvis navnet sto på en rute det ikke får plass i, eller
        manglet på en som er stor nok."""
        assert tekstnivaa(b, h, symbol) == ventet

    def test_tekstnivaaet_er_regnet_for_den_synlige_ruta_ved_den_minste_bredden(self):
        """Gjennomgangen 26.10 (VG, ECH, BH): den smale flaten brukes ned til
        288 px, og ruta er 2 px mindre enn plassen på hver side. Ville feilet
        hvis nivået ble regnet ved 358 px, for plassen med kanten, eller for
        feltet i stedet for ruta."""
        ruter = _ruter_med([0.6, 2.4, 1.0, 0.7, 0.8, 1.9, 0.5, 3.0, 1.1, 1.4, 0.9, 2.2, 0.55, 1.3, 2.7])
        k = kart(bygg_boersometer(ruter))
        assert (BRED.minste, SMAL.minste) == (761 - 17 - 2 * 16, 320 - 2 * 16)
        # Gruppens svar 26.10 kl. 13:00 (c) og 13:07 (e): en klasse per spenn.
        for flate in (BRED, SMAL):
            for klasse, bredde in flate.tekst:
                hoeyde = bredde * k.forhold[flate.navn]
                for f in k.felt:
                    fb, fh = f.plass[flate.navn].b / 100 * bredde, f.plass[flate.navn].h / 100 * hoeyde
                    kropp = fh * (1 - f.topp[flate.navn] / 100)
                    for kr in f.ruter:
                        rb, rh = kr.plass[flate.navn].b / 100 * fb, kr.plass[flate.navn].h / 100 * kropp
                        ventet = tekstnivaa(rb - 2 * KANT, rh - 2 * KANT, kr.rute.aksje.symbol)
                        assert kr.nivaa[klasse] == ventet, (klasse, kr.rute.aksje.symbol, rb, rh)

    def test_tekstnivaaet_paa_siden_er_det_kartet_regnet(self, klient):
        """Gjennomgangen 26.10 (VG): ville feilet hvis malen sluttet å skrive
        nivaa-bred-N og nivaa-smal-N, skrev et annet nivå enn plassen gir,
        eller alle rutene fikk samme nivå."""
        html = _side(klient)
        kartet = _kartet(html)
        klasser = {
            symbol: k
            for k, symbol in re.findall(
                r'<a class="rute ([^"]*)"[^>]*>\s*<span class="ticker">([A-Z0-9]+)</span>', html
            )
        }
        assert len(klasser) == 15
        sett = set()
        for flate in (BRED, SMAL):
            n = flate.navn
            for klasse, bredde in flate.tekst:
                hoeyde = bredde / kartet["forhold"][n]
                for f in kartet["felt"]:
                    fb, fh = f["plass"][n][2] / 100 * bredde, f["plass"][n][3] / 100 * hoeyde
                    kropp = fh * (1 - f["topp"][n] / 100)
                    for symbol, p in f["ruter"].items():
                        rb, rh = p[n][2] / 100 * fb, p[n][3] / 100 * kropp
                        ventet = tekstnivaa(rb - 2 * KANT, rh - 2 * KANT, symbol)
                        funnet = re.findall(rf"\bnivaa-{klasse}-(\d)\b", klasser[symbol])
                        assert funnet == [str(ventet)], (klasse, symbol, rb, rh)
                        sett.add((klasse, ventet))
        assert len(sett) > 4, sett

    def test_tekstnivaaet_fra_360_og_1080_px(self, klient):
        """Gruppens svar 26.10 kl. 13:00 (c) og 13:07 (e): fra 1080 px regnes
        teksten ved 1008 px, full bredde, mellom 761 og 1080 px ved 712 px,
        fra 360 px ved 328 px og under 360 px ved 288 px, og stilen velger
        klassen med @container etter bredden på kartet. Ville feilet hvis
        teksten fortsatt ble regnet ved 712 px fra 1080 px eller ved 288 px
        fra 360 px, hvis grensen ikke var bredden teksten er regnet ved, eller
        hvis en regel for å skjule et element manglet."""
        side = 16
        stil = (SRC / "static" / "stil.css").read_text(encoding="utf-8")
        # main er høyst 65rem, 1040 px, med 16 px på hver side.
        assert re.search(r"max-width: 65rem", stil)
        assert dict(BRED.tekst) == {"bred": 761 - 17 - 2 * side, "bredest": 65 * 16 - 2 * side}
        assert dict(SMAL.tekst) == {"smal": 360 - 2 * side, "smalest": 320 - 2 * side}
        # Gjennomgangen 26.10 (BH, ECH, VG): @container på kartet, med grensen
        # fra Flate.tekst, uten hull mellom spennene og med hele lista av
        # elementer som skjules for hvert nivå.
        kartregel = re.search(r"\.kart \{([^}]*)\}", stil).group(1)
        assert "container-type: inline-size" in kartregel
        skjult = {
            0: [".ticker", ".endring", ".merke", ".tekst"],
            1: [".endring", ".merke", ".tekst"],
            2: [".merke", ".tekst"],
        }
        for media, flate in (("(width > 760px)", BRED), ("(width <= 760px)", SMAL)):
            del_ = stil.split(f"@media {media} {{\n", 1)[1].split("\n}\n", 1)[0]
            blokker = dict(re.findall(r"@container (\([^)]*\)) \{\n(.*?)\n  \}", del_, re.S))
            (stor, stor_b), (liten, liten_b) = sorted(flate.tekst, key=lambda t: -t[1])
            assert set(blokker) == {f"(width >= {stor_b}px)", f"(width < {stor_b}px)"}, blokker.keys()
            for grense, klasse in ((f"(width >= {stor_b}px)", stor), (f"(width < {stor_b}px)", liten)):
                velgere = re.findall(r"\.rute\.nivaa-([a-z]+)-(\d) > (\.[a-z]+)", blokker[grense])
                assert sorted(velgere) == sorted((klasse, str(n), e) for n, el in skjult.items() for e in el), (
                    grense,
                    velgere,
                )
            assert liten_b < stor_b
        # I demoen viser noen ruter mer ved 1008 og 328 px enn ved 712 og 288 px.
        klasser = re.findall(r'<a class="rute ([^"]*)"', _side(klient))
        nivaa = [{k: int(v) for k, v in re.findall(r"nivaa-([a-z]+)-(\d)", kl)} for kl in klasser]
        assert len(nivaa) == 15 and all(len(n) == 4 for n in nivaa)
        assert all(n["bredest"] >= n["bred"] and n["smal"] >= n["smalest"] for n in nivaa)
        assert any(n["bredest"] > n["bred"] for n in nivaa) and any(n["smal"] > n["smalest"] for n in nivaa)

    def test_hjelpen_sier_det_om_teksten_i_rutene(self):
        """Regel 19: ville feilet hvis docs/hjelp.md ikke sa at et bredt
        vindu gir tekst på flere ruter (gruppens svar 26.10 kl. 13:00, c, og
        13:07, e)."""
        hjelp = (Path(__file__).resolve().parents[1] / "docs" / "hjelp.md").read_text(encoding="utf-8")
        avsnitt = hjelp.split("### Hva viser børsometeret?", 1)[1].split("###", 1)[0]
        assert "i et bredt vindu får flere ruter plass til teksten" in avsnitt

    def test_navnet_i_overskriften_kuttes_med_tre_prikker(self, klient):
        """Gjennomgangen 26.10 (BH, ECH): spesifikasjonen sier at overskriften
        kuttes med «…». Ville feilet uten text-overflow: ellipsis på navnet,
        som er et eget element i en flex-boks."""
        stil = (SRC / "static" / "stil.css").read_text(encoding="utf-8")
        regel = re.search(r"\.kart section\.bransje h2 \.bransjenavn \{([^}]*)\}", stil).group(1)
        assert "text-overflow: ellipsis" in regel and "overflow: hidden" in regel
        assert re.search(r"min-width: (\d+)px", regel)
        assert _side(klient).count('<span class="bransjenavn">') == 8

    def test_overskriften_er_navnet_og_snittet_eller_1_aksje(self, klient):
        """Gruppens svar 26.10 kl. 13:00 (b): som på tavla, navnet og
        «snitt» med tallet, eller «1 aksje» ved én aksje. Ville feilet med
        antallet i overskriften, uten «snitt», med snittet ved én aksje,
        eller med tillegget foran navnet."""
        for adresse in ("/boersometer", "/boersometer?dag=2026-10-08"):
            html = _side(klient, adresse)
            kartet = html.split('<div class="kart"', 1)[1].split('<section class="fargene"', 1)[0]
            h2 = re.findall(r"<h2 id=\"bransje-\d+\">(.*?)</h2>", kartet, re.S)
            assert len(h2) == 8
            for innhold in h2:
                linje = re.fullmatch(
                    r'<span class="linje"><span class="navnet"><svg [^>]*>.*?</svg><span class="bransjenavn">([^<]+)</span></span>\s*(.*)</span>',
                    innhold,
                    re.S,
                )
                assert linje, innhold
                navn, tillegg = linje.groups()
                rader = re.findall(rf"<td>{navn} \((\d+) aksjer?", html)
                assert len(rader) == 1, (navn, rader)
                if rader[0] == "1":
                    assert tillegg == '<span class="tillegg">1 aksje</span>', tillegg
                else:
                    assert re.fullmatch(
                        r'<span class="tillegg">snitt <span class="snitt (opp|ned|null)">[^<]+</span></span>', tillegg
                    ), tillegg

    def test_tillegget_skjules_for_oeyet_foer_navnet_kuttes(self):
        """Gruppens svar 26.10 kl. 13:00 (b): får ikke snittet eller «1 aksje»
        plass, brytes det til en linje som skjules av overflow, under en
        row-gap høyere enn linja. Navnet står først og kuttes med «…» først
        når det står alene. Ville feilet uten flex-wrap, med display: none,
        som skjuler tillegget for skjermleseren, eller med en row-gap som lot
        linje to synes."""
        stil = (SRC / "static" / "stil.css").read_text(encoding="utf-8")
        linje = re.search(r"\.kart section\.bransje h2 \.linje \{([^}]*)\}", stil).group(1)
        assert "flex-wrap: wrap" in linje and "overflow: hidden" in linje and "min-width: 0" in linje
        hoeyde = int(re.search(r"(?<![-\w])height: (\d+)px", linje).group(1))
        assert int(re.search(r"row-gap: (\d+)px", linje).group(1)) > hoeyde
        tillegg = re.search(r"\.kart section\.bransje h2 \.tillegg \{([^}]*)\}", stil).group(1)
        assert "display: none" not in tillegg and "flex: none" in tillegg
        navnet = re.search(r"\.kart section\.bransje h2 \.navnet \{([^}]*)\}", stil).group(1)
        assert "min-width: 0" in navnet and "max-width: 100%" in navnet
        assert "display: none" not in stil.split(".kart section.bransje h2", 1)[1].split("ul.ruter", 1)[0]

    def test_navnet_forsvinner_aldri_helt(self):
        """Gruppens svar 26.10 kl. 13:00 (b): hvert felt er så bredt, ved den
        minste bredden flaten brukes på, at overskriften har plass til
        symbolet og min-width for navnet. Ville feilet hvis et felt kunne bli
        så smalt at bare symbolet eller ingenting av navnet sto, eller hvis
        tallene i boersometer.py ikke var de i stil.css."""
        stil = (SRC / "static" / "stil.css").read_text(encoding="utf-8")
        regel = lambda velger: re.search(velger + r" \{([^}]*)\}", stil).group(1)  # noqa: E731
        assert f"min-width: {boersometer.MINSTE_NAVN}px" in regel(r"\.kart section\.bransje h2 \.bransjenavn")
        assert f"gap: {boersometer.MELLOMROM}px" in regel(r"\.kart section\.bransje h2 \.navnet")
        assert f"width: {boersometer.SYMBOL}px" in regel(r"\.kart section\.bransje h2 \.bransjesymbol")
        h2 = regel(r"\.kart section\.bransje h2")
        assert f"left: {boersometer.INNRYKK}px; right: {boersometer.INNRYKK}px" in h2
        rng = random.Random(5)
        dager = [[rng.lognormvariate(0, sigma) for _ in range(15)] for sigma in (0.5, 0.8, 1.2) for _ in range(30)]
        dager += [[3.0] * 14 + [0.05], [0.5] * 14 + [12.0], [1.0] * 15]
        for forhold in dager:
            k = kart(bygg_boersometer(_ruter_med(forhold, [BRANSJER[i % 8] for i in range(15)])))
            for flate in (BRED, SMAL):
                for f in k.felt:
                    synlig = f.plass[flate.navn].b / 100 * flate.minste
                    assert synlig >= boersometer.MINSTE_FELT - 1e-9, (flate.navn, f.bransje.navn, synlig)

    def test_hjelpen_sier_det_om_overskriften(self):
        """Regel 19: ville feilet hvis hjelpen ved «?» eller docs/hjelp.md
        ikke sa at bare navnet står når feltet er smalt, eller at antallet
        står i tabellen (gruppens svar 26.10 kl. 13:00, b)."""
        from hjelpetekster import hjelpetekster

        assert "eller bare navnet når feltet er smalt" in hjelpetekster(STANDARD)["boersometeret"].tekst
        hjelp = (Path(__file__).resolve().parents[1] / "docs" / "hjelp.md").read_text(encoding="utf-8")
        avsnitt = hjelp.split("### Hva viser børsometeret?", 1)[1].split("###", 1)[0]
        assert "eller «1 aksje» der det er én; antallet står i tabellen" in avsnitt
        assert "Er feltet for smalt, står bare navnet" in avsnitt

    def test_det_som_ikke_faar_plass_leses_av_skjermleseren(self):
        """Teksten som ikke får plass, skjules bare for øyet. Ville feilet med
        display: none, som også skjuler den for skjermleseren."""
        stil = (SRC / "static" / "stil.css").read_text(encoding="utf-8")
        for flate in ("bredest", "bred", "smal", "smalest"):
            regel = re.search(rf"\.rute\.nivaa-{flate}-2 > \.tekst \{{([^}}]*)\}}", stil).group(1)
            assert "clip: rect(0 0 0 0)" in regel and "display: none" not in regel
        assert "@media (max-width: 760px)" in stil

    def test_hjelpen_sier_det(self):
        """Regel 19: ville feilet hvis hjelpen fortsatt sa at ruta er større
        over 1,5 ganger vanlig, ikke sa at rutene er et fylt kart, eller ikke
        sa grensene for vekten (gruppens svar 26.10 kl. 08:43, b)."""
        from hjelpetekster import hjelpetekster

        tekst = hjelpetekster(STANDARD)["boersometeret"].tekst
        assert "Arealet av ruta følger volumet mot vanlig" in tekst and "1,5 ganger" not in tekst
        assert "ikke større over 3 ganger vanlig volum eller mindre under halvparten" in tekst
        assert "tabellen bak «Se tallene som tabell» har tallet" in tekst
        hjelp = (Path(__file__).resolve().parents[1] / "docs" / "hjelp.md").read_text(encoding="utf-8")
        avsnitt = hjelp.split("### Hva viser børsometeret?", 1)[1].split("###", 1)[0]
        assert "Rutene er et fylt kart" in avsnitt
        assert "ikke større over tre ganger vanlig volum eller mindre under halvparten" in avsnitt
        assert "tabellen under har det faktiske tallet" in avsnitt
        assert "Ruta er større når" not in avsnitt
        readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
        assert "og børsometeret som et kart, med knappene" in readme
