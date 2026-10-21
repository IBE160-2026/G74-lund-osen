"""Story 2.7 (2.7b): historikken, «Signalet dag for dag», på aksjesiden.

Innholdet er avgjørelsen 2026-10-21 under story 2.7: månedsvisningen fra
tavla, med piler så langt kursserien går tilbake, og målingene på siden for
dagen (8.16b), som hver dag lenker til. Radene i vurdering skrives rett med
upserten, slik hentingen skrev dem de dagene, fordi porten bare godtar
inneværende børsdag (AD-7). Ingen test her går på nett: sidene lages med
testklienten, og basen ligger i tmp_path (conftest.py).
"""

import ast
import re
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

import app as app_modul
import lagring_sqlite
from boersdag import UtenforKalenderen, er_boersdag
from historikk import bygg_maaned, les_maaned
from kursdata import AKSJEUNIVERS, Kursrad
from lagring_sqlite import SqliteKurslager, SqliteVurderingslager, aapne_base
from vurderingsdata import Grunn, Vurdering, Vurderingslager

ROT = Path(__file__).resolve().parent.parent
SYMBOL = "EQNR"
NAVN = next(aksje.navn for aksje in AKSJEUNIVERS if aksje.symbol == SYMBOL)
FOERSTE = date(2025, 12, 1)
SISTE = date(2026, 10, 9)
# Klokka står på onsdag 21.10.2026, så dagene fra 12.10 er etter siste kursrad.
NAA = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)


def _boersdag(dag: date) -> bool:
    try:
        return er_boersdag(dag)
    except UtenforKalenderen:
        return dag.weekday() < 5


DATOENE = [
    FOERSTE + timedelta(days=i) for i in range((SISTE - FOERSTE).days + 1) if _boersdag(FOERSTE + timedelta(days=i))
]


def _vurdering(trend: int, bevegelse: int, interesse: int) -> Vurdering:
    sjekker = (trend, bevegelse, interesse)
    utslag = [v for v in sjekker if v]
    retning = (
        "Ingen"
        if not utslag
        else "Positiv"
        if all(v > 0 for v in utslag)
        else "Negativ"
        if all(v < 0 for v in utslag)
        else "Blandet"
    )
    return Vurdering(
        styrke=sum(abs(v) for v in sjekker),
        retning=retning,
        trend=trend,
        bevegelse=bevegelse,
        interesse=interesse,
        slutt=100.0,
        justert_slutt=100.0,
        trend_avvik=0.0,
        dagens_endring=0.0,
        standardavvik=0.01,
        volumforhold=1.0,
    )


# Radene i vurdering i oktober. 07.10 mangler, og 13.10 er etter siste
# kursrad, med en grunn fordi hentingen feilet.
RADENE = {
    date(2026, 10, 1): _vurdering(1, 1, 1),
    date(2026, 10, 2): _vurdering(0, 0, 0),
    date(2026, 10, 5): Grunn.SYMBOL_FEILET,
    date(2026, 10, 6): _vurdering(1, -1, 0),
    date(2026, 10, 8): _vurdering(0, 0, -1),
    date(2026, 10, 9): _vurdering(-1, -1, 0),
    date(2026, 10, 13): Grunn.SYMBOL_FEILET,
}


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    monkeypatch.setattr(app_modul, "naa", lambda: NAA)


@pytest.fixture
def klient(monkeypatch):
    monkeypatch.delenv(app_modul.I_DEMO, raising=False)
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


def _skriv_rad(tilkobling, symbol: str, dag: date, innhold) -> None:
    if isinstance(innhold, Vurdering):
        verdier = (*(getattr(innhold, k) for k in lagring_sqlite.VURDERINGSKOLONNER), None)
    else:
        verdier = (*(None for _ in lagring_sqlite.VURDERINGSKOLONNER), innhold.value)
    with tilkobling:
        tilkobling.execute(lagring_sqlite._UPSERT, (symbol, dag.isoformat(), *verdier))


@pytest.fixture
def base():
    """EQNR med kurser fra 01.12.2025 til 09.10.2026 og radene over, og DNB
    med en rad 06.10 som ikke skal komme med på siden for EQNR."""
    tilkobling = aapne_base(lagring_sqlite.BASE_STI)
    try:
        lager = SqliteKurslager(tilkobling)
        rader = [
            Kursrad(dato=d, slutt=100.0 + i % 9, justert_slutt=100.0 + i % 9, volum=1000) for i, d in enumerate(DATOENE)
        ]
        lager.erstatt_serie(SYMBOL, rader, datetime(2026, 10, 9, 20, 15, tzinfo=timezone.utc))
        lager.erstatt_serie("DNB", rader, datetime(2026, 10, 9, 20, 15, tzinfo=timezone.utc))
        for dag, innhold in RADENE.items():
            _skriv_rad(tilkobling, SYMBOL, dag, innhold)
        _skriv_rad(tilkobling, "DNB", date(2026, 10, 7), _vurdering(1, 1, 1))
    finally:
        tilkobling.close()


def _side(klient, adresse: str) -> str:
    svar = klient.get(adresse)
    assert svar.status_code == 200, (adresse, svar.status_code)
    return svar.get_data(as_text=True)


def _avsnittet(html: str) -> str:
    return html.split('id="signalet-dag-for-dag"', 1)[1].split("</section>", 1)[0]


def _tekst(html: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", html).split())


def _dagene(html: str) -> dict[str, tuple[str, str, str]]:
    """Datoen slik den står («01.10») -> (klassene, teksten, del-HTML)."""
    dager = {}
    for klasser, inni in re.findall(r'<li class="dag([^"]*)"[^>]*>(.*?)</li>', _avsnittet(html), flags=re.DOTALL):
        tekst = _tekst(inni)
        if tekst:
            dager[tekst.split()[1]] = (klasser.split(), tekst, inni)
    return dager


def _ukesummene(html: str) -> list[str]:
    return [_tekst(s) for s in re.findall(r'<p class="ukesum">(.*?)</p>', _avsnittet(html), flags=re.DOTALL)]


class TestTilstandene:
    def test_hver_tilstand_ser_ulik_ut(self, klient, base):
        """Ville feilet hvis styrke 0, en grunn, en manglende rad, en dag som
        ikke er børsdag og en dag utenfor børskalenderen så like ut, eller
        en manglende rad ble vist som styrke 0."""
        oktober = _dagene(_side(klient, f"/aksje/{SYMBOL}"))
        mai = _dagene(_side(klient, f"/aksje/{SYMBOL}?maaned=2026-05"))
        desember = _dagene(_side(klient, f"/aksje/{SYMBOL}?maaned=2025-12"))
        tekstene = {
            "styrke 0": oktober["02.10"][1],
            "grunn": oktober["05.10"][1],
            "manglende rad": oktober["07.10"][1],
            "ikke børsdag": mai["14.05"][1],
            "utenfor kalenderen": desember["02.12.2025"][1],
        }
        assert tekstene == {
            "styrke 0": "fredag 02.10 – Ingen T 0 B 0 I 0 0 av 3",
            "grunn": "mandag 05.10 – hentingen feilet",
            "manglende rad": "onsdag 07.10 – ikke vurdert",
            "ikke børsdag": "torsdag 14.05 – ikke børsdag",
            "utenfor kalenderen": "tirsdag 02.12.2025 – utenfor børskalenderen",
        }
        uten_dato = [" ".join(t.split()[2:]) for t in tekstene.values()]
        assert len(set(uten_dato)) == len(uten_dato)

    def test_vurderingen_har_retningen_sjekkene_og_styrken(self, klient, base):
        """Ville feilet hvis en dag manglet retningen, T, B, I eller styrken."""
        oktober = _dagene(_side(klient, f"/aksje/{SYMBOL}"))
        assert oktober["06.10"][1] == "tirsdag 06.10 ↔ Blandet T +1 B -1 I 0 2 av 3"
        assert oktober["08.10"][1] == "torsdag 08.10 ↓ Negativ T 0 B 0 I -1 1 av 3"

    def test_3_av_3_merkes_som_i_oversikten_og_2_av_3_ikke(self, klient, base):
        """Ville feilet hvis 3 av 3 ikke fikk pillen og streken fra
        designregler.md §3, eller 2 av 3 ble merket i historikken."""
        oktober = _dagene(_side(klient, f"/aksje/{SYMBOL}"))
        klasser, _, inni = oktober["01.10"]
        assert "alle" in klasser
        assert '<span class="pille tre-av-tre">3 av 3</span>' in inni
        for dag in ("06.10", "09.10"):
            klasser, _, inni = oktober[dag]
            assert "alle" not in klasser and "tre-av-tre" not in inni, dag
            assert '<span class="pille">2 av 3</span>' in inni, dag


class TestTallene:
    def test_tallene_for_ukene(self, klient, base):
        """Ville feilet hvis uka talte en dag uten vurdering, en grunn eller
        en dag i en annen måned, eller ukene etter siste kursrad fikk en
        tekst som ser ut som et hull."""
        html = _side(klient, f"/aksje/{SYMBOL}")
        assert re.findall(r'<p class="ukenummer">Uke (\d+)</p>', _avsnittet(html)) == ["40", "41", "42", "43", "44"]
        assert _ukesummene(html) == [
            "1 av 2 dager skilte seg ut",
            "2 av 3 dager skilte seg ut",
            "Ingen dager med vurdering",
        ]

    def test_tallene_for_maaneden(self, klient, base):
        """Ville feilet hvis måneden talte noe annet enn dagene med en
        vurdering, eller sjekkene ble talt feil."""
        tekst = _tekst(_avsnittet(_side(klient, f"/aksje/{SYMBOL}")))
        assert (
            f"Oktober samlet: {NAVN} skilte seg ut 3 av 5 børsdager. "
            "Trend slo ut 3 dager, bevegelse 3 og interesse 2." in tekst
        )

    def test_en_maaned_uten_vurdering(self, klient, base):
        tekst = _tekst(_avsnittet(_side(klient, f"/aksje/{SYMBOL}?maaned=2026-05")))
        assert f"Mai samlet: {NAVN} har ingen dager med vurdering." in tekst
        assert "slo ut" not in tekst

    def test_en_annen_aksje_kommer_ikke_med(self, klient, base):
        """Ville feilet hvis lesingen tok med radene for alle aksjene."""
        assert _dagene(_side(klient, f"/aksje/{SYMBOL}"))["07.10"][1] == "onsdag 07.10 – ikke vurdert"
        assert "1 av 1 dag skilte seg ut" in _ukesummene(_side(klient, "/aksje/DNB"))


class TestLenken:
    def test_hver_dag_med_kurs_lenker_til_siden_for_dagen(self, klient, base):
        """Ville feilet hvis en dag med kurs ikke lenket til siden for dagen,
        eller lenket til en annen aksje eller dag."""
        oktober = _dagene(_side(klient, f"/aksje/{SYMBOL}"))
        for dag in ("01.10", "02.10", "05.10", "07.10", "09.10"):
            iso = f"2026-10-{dag[:2]}"
            assert f'<a class="dato" href="/aksje/{SYMBOL}?dag={iso}">' in oktober[dag][2], dag
        tekst = _tekst(_side(klient, f"/aksje/{SYMBOL}?dag=2026-10-06"))
        assert "Siden viser tirsdag 06.10, ikke siste børsdag." in tekst

    def test_dager_uten_kurs_og_seriens_foerste_dag_har_ingen_lenke(self, klient, base):
        """Seriens første dag gir 6 mnd i les_valg (8.16, BH3), så den lenker
        ikke. Ville feilet med en lenke som gir en annen side enn dagen."""
        mai = _dagene(_side(klient, f"/aksje/{SYMBOL}?maaned=2026-05"))
        desember = _dagene(_side(klient, f"/aksje/{SYMBOL}?maaned=2025-12"))
        assert "<a " not in mai["14.05"][2]
        assert "<a " not in desember["01.12.2025"][2]
        assert "<a " in desember["02.12.2025"][2]


class TestPilene:
    def test_siste_maaned_har_bare_pila_bakover(self, klient, base):
        """Ville feilet hvis pila gikk forbi siste kursrad."""
        avsnittet = _avsnittet(_side(klient, f"/aksje/{SYMBOL}"))
        piler = re.findall(r'<a class="pil" href="([^"]+)">([^<]+)</a>', avsnittet)
        assert piler == [(f"/aksje/{SYMBOL}?maaned=2026-09#signalet-dag-for-dag", "‹ september 2026")]
        assert '<span class="maaned">Oktober 2026</span>' in avsnittet

    def test_foerste_maaned_har_bare_pila_framover(self, klient, base):
        """Ville feilet hvis pila gikk forbi første kursrad."""
        avsnittet = _avsnittet(_side(klient, f"/aksje/{SYMBOL}?maaned=2025-12"))
        piler = re.findall(r'<a class="pil" href="([^"]+)">([^<]+)</a>', avsnittet)
        assert piler == [(f"/aksje/{SYMBOL}?maaned=2026-01#signalet-dag-for-dag", "januar 2026 ›")]

    def test_pilene_beholder_dagen_eller_perioden(self, klient, base):
        """Ville feilet hvis en pil tok bort dagen eller perioden siden viser."""
        avsnittet = _avsnittet(_side(klient, f"/aksje/{SYMBOL}?dag=2026-05-13"))
        assert '<span class="maaned">Mai 2026</span>' in avsnittet
        assert f'href="/aksje/{SYMBOL}?maaned=2026-04&amp;dag=2026-05-13#signalet-dag-for-dag"' in avsnittet
        assert f'href="/aksje/{SYMBOL}?maaned=2026-06&amp;dag=2026-05-13#signalet-dag-for-dag"' in avsnittet
        avsnittet = _avsnittet(_side(klient, f"/aksje/{SYMBOL}?periode=1-mnd&maaned=2026-03"))
        assert f'href="/aksje/{SYMBOL}?maaned=2026-02&amp;periode=1-mnd#signalet-dag-for-dag"' in avsnittet
        # En periode som ikke finnes, følger ikke med.
        avsnittet = _avsnittet(_side(klient, f"/aksje/{SYMBOL}?periode=tull"))
        assert f'href="/aksje/{SYMBOL}?maaned=2026-09#signalet-dag-for-dag"' in avsnittet

    def test_maaneden_er_den_for_dagen_siden_viser(self, klient, base):
        """Ville feilet hvis historikken viste siste måned for en valgt dag."""
        assert "07.05" in _dagene(_side(klient, f"/aksje/{SYMBOL}?dag=2026-05-07"))
        assert '<span class="maaned">Mai 2026</span>' in _side(klient, f"/aksje/{SYMBOL}?dag=2026-05-07")

    @pytest.mark.parametrize(
        "verdi, beskjed",
        [
            ("2026-13", "Måneden «2026-13» kunne ikke leses, så historikken viser oktober 2026."),
            ("tull", "Måneden «tull» kunne ikke leses, så historikken viser oktober 2026."),
            ("2025-11", "Kursserien går fra desember 2025 til oktober 2026, så historikken viser oktober 2026."),
            ("2026-11", "Kursserien går fra desember 2025 til oktober 2026, så historikken viser oktober 2026."),
        ],
    )
    def test_en_ugyldig_maaned_gir_maaneden_for_dagen_og_en_beskjed(self, klient, base, verdi, beskjed):
        """Ville feilet med en feilside, eller uten beskjeden."""
        avsnittet = _avsnittet(_side(klient, f"/aksje/{SYMBOL}?maaned={verdi}"))
        assert f'<p class="periodebeskjed" role="status">{beskjed}</p>' in avsnittet
        assert '<span class="maaned">Oktober 2026</span>' in avsnittet

    def test_en_ugyldig_maaned_med_en_valgt_dag(self, klient, base):
        avsnittet = _avsnittet(_side(klient, f"/aksje/{SYMBOL}?dag=2026-05-07&maaned=x"))
        assert '<span class="maaned">Mai 2026</span>' in avsnittet
        assert "så historikken viser mai 2026." in avsnittet


class TestEtterSisteKursrad:
    def test_dagene_etter_siste_kursrad_er_tomme(self, klient, base):
        """Ville feilet hvis en rad som ikke er skrevet ennå, ble vist som
        «– ikke vurdert», som et hull."""
        oktober = _dagene(_side(klient, f"/aksje/{SYMBOL}"))
        for dag in ("12.10", "14.10", "15.10", "16.10", "19.10", "21.10", "30.10"):
            klasser, tekst, inni = oktober[dag]
            assert "tom" in klasser, dag
            assert len(tekst.split()) == 2 and "<a " not in inni, (dag, tekst)

    def test_en_rad_som_er_skrevet_vises_likevel(self, klient, base):
        """En grunn etter siste kursrad er skrevet, og er ikke et hull."""
        klasser, tekst, _ = _dagene(_side(klient, f"/aksje/{SYMBOL}"))["13.10"]
        assert "tom" not in klasser
        assert tekst == "tirsdag 13.10 – hentingen feilet"


class TestLesingen:
    def test_porten_har_lesemetoden_og_ingen_slette_eller_endremetode(self):
        """Ville feilet hvis porten eller adapteren fikk en slett eller en
        endre (AD-7), eller mistet les_periode."""
        for klasse in (Vurderingslager, SqliteVurderingslager):
            offentlige = {navn for navn in dir(klasse) if not navn.startswith("_")}
            assert offentlige == {"skriv", "les", "les_periode"}, klasse

    def test_les_periode_gir_radene_i_perioden_i_en_spoerring(self, base):
        """Ville feilet hvis lesingen tok en spørring per dag, eller tok med
        dager utenfor perioden eller en annen aksje."""
        tilkobling = aapne_base(lagring_sqlite.BASE_STI)
        try:
            lager = SqliteVurderingslager(tilkobling, lambda: NAA)
            spoerringer = []
            tilkobling.set_trace_callback(spoerringer.append)
            radene = lager.les_periode(SYMBOL, date(2026, 10, 2), date(2026, 10, 8))
            tilkobling.set_trace_callback(None)
        finally:
            tilkobling.close()
        assert radene == {d: r for d, r in RADENE.items() if date(2026, 10, 2) <= d <= date(2026, 10, 8)}
        assert len([s for s in spoerringer if s.lstrip().upper().startswith("SELECT")]) == 1

    def test_les_periode_kontrollerer_noekkelen_som_les(self, base):
        tilkobling = aapne_base(lagring_sqlite.BASE_STI)
        try:
            lager = SqliteVurderingslager(tilkobling, lambda: NAA)
            with pytest.raises(ValueError, match="EQNR.OL"):
                lager.les_periode("EQNR.OL", date(2026, 10, 1), date(2026, 10, 31))
            with pytest.raises(TypeError):
                lager.les_periode(SYMBOL, datetime(2026, 10, 1), date(2026, 10, 31))
        finally:
            tilkobling.close()

    def test_siden_leser_en_gang_per_maaned(self, klient, base, monkeypatch):
        """Ville feilet hvis siden leste historikken dag for dag."""
        kall = []
        ekte = SqliteVurderingslager.les_periode

        def tell(self, *argumenter):
            kall.append(argumenter)
            return ekte(self, *argumenter)

        monkeypatch.setattr(SqliteVurderingslager, "les_periode", tell)
        monkeypatch.setattr(SqliteVurderingslager, "les", lambda *a: pytest.fail("les per dag"))
        _side(klient, f"/aksje/{SYMBOL}")
        assert kall == [(SYMBOL, date(2026, 10, 1), date(2026, 10, 31))]


class TestVurderKallesIkke:
    def test_siden_regner_aldri_signalet(self, klient, base, monkeypatch):
        """Ville feilet hvis historikken ble regnet med vurder: da viser den
        dagens parametre, ikke det løsningen sa (AD-7)."""

        def stopp(*_a, **_k):
            raise AssertionError("vurder ble kalt")

        for modul in list(sys.modules.values()):
            if (
                getattr(modul, "vurder", None) is not None
                and getattr(modul, "__file__", "")
                and "src" in Path(modul.__file__).parts
            ):
                monkeypatch.setattr(modul, "vurder", stopp)
        for adresse in (f"/aksje/{SYMBOL}", f"/aksje/{SYMBOL}?maaned=2026-05", f"/aksje/{SYMBOL}?dag=2026-10-06"):
            _side(klient, adresse)

    def test_historikk_py_importerer_ikke_signalberegningen(self):
        """Ville feilet hvis historikk.py importerte vurder eller noe annet
        fra signalberegning, som regner signalet."""
        tre = ast.parse((ROT / "src" / "historikk.py").read_text(encoding="utf-8"))
        for node in ast.walk(tre):
            if isinstance(node, ast.ImportFrom):
                assert node.module != "signalberegning", node.module
            if isinstance(node, ast.Import):
                assert all(n.name != "signalberegning" for n in node.names)


class TestRenLogikk:
    def test_les_maaned_uten_verdi_er_maaneden_for_dagen(self):
        assert les_maaned(None, date(2026, 5, 7), FOERSTE, SISTE) == (date(2026, 5, 1), None)

    def test_en_uke_over_aarsskiftet_har_iso_nummeret(self):
        """Uka med 01.01.2027 er uke 53 i 2026 etter ISO 8601."""
        maaned = bygg_maaned(date(2027, 1, 1), [date(2026, 12, 1), date(2027, 1, 29)], {}, date(2027, 2, 1), 2)
        assert maaned.uker[0].nummer == 53
        assert [d.dato if d else None for d in maaned.uker[0].dager] == [None, None, None, None, date(2027, 1, 1)]

    def test_en_basefeil_gir_ikke_en_feilside_uten_svar(self, klient, base, monkeypatch):
        """Leses ikke vurdering, svarer siden som ved andre basefeil."""

        def feil(*_a):
            raise sqlite3.OperationalError("disk I/O error")

        monkeypatch.setattr(SqliteVurderingslager, "les_periode", feil)
        assert klient.get(f"/aksje/{SYMBOL}").status_code in (500, 503)
