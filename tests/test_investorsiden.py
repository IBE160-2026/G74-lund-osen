"""Story 10.5: lenken til selskapets investorside i aksjedetaljen.

Adressene er de gruppen godkjente 19.10 kl. 16:03, med de tre norske sidene
fra svaret kl. 19:49 (under story 10.5 i epics.md). Appen lenker aldri til
Euronexts nettsteder (rettingen 06.10), og ingen kode henter fra adressene
(AD-2). Ingen test her gaar paa nett: sidene lages med testklienten, og
basen ligger i tmp_path (conftest.py).
"""

import re
import shutil
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

import pytest

import app as app_modul
import demo
import lagring_sqlite
from kursdata import AKSJEUNIVERS, INVESTORSIDER, Kursrad, investorside
from lagring_sqlite import SqliteKurslager, aapne_base

ROT = Path(__file__).resolve().parent.parent
EPICS = ROT / "_bmad-output" / "planning-artifacts" / "epics.md"
EUROPEISKE = ("newsweb.oslobors.no", "oslobors.no", "live.euronext.com")


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 12, 31, 12, 0, tzinfo=timezone.utc))


@pytest.fixture
def klient(monkeypatch):
    monkeypatch.delenv(app_modul.I_DEMO, raising=False)
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


@pytest.fixture
def ekte_base():
    """De 15 i den ekte basen i tmp_path, med 61 kursdager hver."""
    rader = [
        Kursrad(dato=date(2026, 9, 1) + timedelta(days=i), slutt=100.0, justert_slutt=100.0, volum=1000)
        for i in range(61)
    ]
    tilkobling = aapne_base(lagring_sqlite.BASE_STI)
    try:
        lager = SqliteKurslager(tilkobling)
        for aksje in AKSJEUNIVERS:
            lager.erstatt_serie(aksje.symbol, rader, datetime(2026, 11, 1, tzinfo=timezone.utc))
    finally:
        tilkobling.close()


@pytest.fixture(scope="module")
def demomal(tmp_path_factory):
    sti = tmp_path_factory.mktemp("demomal") / "demo.db"
    demo.lag_demobase(sti, skriv=lambda _: None)
    return sti


@pytest.fixture
def demoklient(klient, demomal, monkeypatch):
    sti = lagring_sqlite.demo_sti()
    sti.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(demomal, sti)
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    return klient


class _Lenker(HTMLParser):
    """Hver <a href> på siden, og lenkene og teksten i avsnittet med klassen
    investorside."""

    def __init__(self):
        super().__init__()
        self.alle: list[str] = []
        self.i_avsnittet = False
        self.i_lenken = False
        self.avsnittet: list[str] = []
        self.lenker: list[tuple[str, str]] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.alle.append(a["href"])
            if self.i_avsnittet:
                self.i_lenken = True
                self.lenker.append((a["href"], ""))
        if tag == "p" and "investorside" in (a.get("class") or "").split():
            self.i_avsnittet = True

    def handle_endtag(self, tag):
        if tag == "a":
            self.i_lenken = False
        if tag == "p":
            self.i_avsnittet = False

    def handle_data(self, data):
        if self.i_avsnittet:
            self.avsnittet.append(data)
            if self.i_lenken:
                href, tekst = self.lenker[-1]
                self.lenker[-1] = (href, tekst + data)


def _les(html: str) -> _Lenker:
    p = _Lenker()
    p.feed(html)
    return p


def _adressene_i_epics() -> dict[str, str]:
    """Adressene i linjene kl. 16:03 og 19:49 under story 10.5, der linja
    kl. 19:49 bytter tre av dem."""
    tekst = EPICS.read_text(encoding="utf-8")
    story = tekst.split("### Story 10.5:", 1)[1].split("\n### ", 1)[0]
    adresser: dict[str, str] = {}
    for start in ("*Avgjort 2026-10-19 kl. 16:03 (gruppens svar):*", "*Avgjort 2026-10-19 kl. 19:49 (gruppens svar):*"):
        linja = next(l for l in story.split("\n") if l.startswith(start))
        adresser.update(re.findall(r"\b([A-Z]{2,5}) (https://[^\s,]+?)(?=[,.]?(?:\s|$))", linja))
    return adresser


def test_hver_av_de_15_har_adressen_fra_svarene():
    """Ville feilet hvis en adresse var en annen enn i linjene kl. 16:03 og
    19:49, for eksempel den engelske siden for AKRBP, VAR eller GJF, hvis en
    av de 15 manglet, eller hvis adressen var knyttet til tickeren hos EODHD
    (EQNR.OL) i stedet for symbolet."""
    fra_epics = _adressene_i_epics()
    assert len(fra_epics) == 15, fra_epics
    assert INVESTORSIDER == fra_epics
    assert list(INVESTORSIDER) == [a.symbol for a in AKSJEUNIVERS]
    for aksje in AKSJEUNIVERS:
        assert investorside(aksje.symbol) == fra_epics[aksje.symbol]
        assert investorside(aksje.ticker) is None
    # Svaret kl. 19:49: de tre norske sidene.
    assert INVESTORSIDER["AKRBP"] == "https://akerbp.com/investor/"
    assert INVESTORSIDER["VAR"] == "https://varenergi.no/no/investor/"
    assert INVESTORSIDER["GJF"] == "https://www.gjensidige.com/no/investorinformasjon"


def test_demoselskapene_har_ingen_adresse():
    """Ville feilet hvis et oppdiktet selskap fikk en adresse."""
    for aksje in demo.DEMOUNIVERS:
        assert investorside(aksje.symbol) is None, aksje.symbol


@pytest.mark.usefixtures("ekte_base")
@pytest.mark.parametrize("aksje", AKSJEUNIVERS, ids=lambda a: a.symbol)
def test_lenken_paa_siden_gaar_til_aksjen_siden_viser(klient, aksje):
    """Ville feilet hvis lenken gikk til en annen aksje enn den siden viser,
    manglet navnet i lenketeksten, eller lenket til NewsWeb."""
    svar = klient.get(f"/aksje/{aksje.symbol}")
    assert svar.status_code == 200
    html = svar.get_data(as_text=True)
    sider = _les(html)
    assert sider.lenker == [(INVESTORSIDER[aksje.symbol], f"investorsiden til {aksje.navn}")]
    tekst = " ".join("".join(sider.avsnittet).split())
    assert tekst == f"Børsmeldingene står på NewsWeb og ofte også på investorsiden til {aksje.navn}."
    # De andre adressene står ikke på siden.
    for symbol, adresse in INVESTORSIDER.items():
        if symbol != aksje.symbol:
            assert adresse not in html, symbol


def test_demoen_viser_teksten_og_ingen_lenke(demoklient):
    """Svaret kl. 19:49. Ville feilet hvis demoen viste en lenke til en
    investorside, eller ikke sa at selskapet er oppdiktet og at lenken står
    her i den ekte versjonen."""
    for aksje in demo.DEMOUNIVERS[:3]:
        html = demoklient.get(f"/aksje/{aksje.symbol}").get_data(as_text=True)
        assert "Eksempeltall" in html
        sider = _les(html)
        assert sider.lenker == []
        tekst = " ".join("".join(sider.avsnittet).split())
        assert tekst == (
            "Børsmeldingene står på NewsWeb og ofte også på selskapets investorside. "
            f"{aksje.navn} er oppdiktet og har ingen investorside. I den ekte versjonen står lenken her."
        )
        for adresse in INVESTORSIDER.values():
            assert adresse not in html


def _lenker_til_euronext(hrefs) -> list[str]:
    return [h for h in hrefs if any(d in h.lower() for d in EUROPEISKE)]


def test_ingen_mal_lenker_til_euronext():
    """Rettingen 06.10. Ville feilet hvis en mal fikk en lenke til
    newsweb.oslobors.no, oslobors.no eller live.euronext.com."""
    for mal in (ROT / "src" / "templates").glob("*.html"):
        hrefs = re.findall(r"""href\s*=\s*["']([^"']*)["']""", mal.read_text(encoding="utf-8"))
        assert not _lenker_til_euronext(hrefs), mal.name


@pytest.mark.usefixtures("ekte_base")
def test_ingen_side_som_vises_lenker_til_euronext(klient):
    """Ville feilet hvis en side som vises, lenket til et av Euronexts
    nettsteder, også en lenke laget i koden og ikke i malen."""
    for sti in ("/", "/min-liste", "/min-liste?vis=alle", *(f"/aksje/{a.symbol}" for a in AKSJEUNIVERS)):
        svar = klient.get(sti)
        assert svar.status_code == 200, sti
        assert not _lenker_til_euronext(_les(svar.get_data(as_text=True)).alle), sti


def test_ingen_demoside_lenker_til_euronext(demoklient):
    """Som over, for demoen. Et demoselskap uten kurser, som MTFJ (U3 i
    docs/ux-logg.md), gir 404 og har ingen side å sjekke."""
    vist = 0
    for sti in ("/", "/min-liste", *(f"/aksje/{a.symbol}" for a in demo.DEMOUNIVERS)):
        svar = demoklient.get(sti)
        if svar.status_code == 404 and sti.startswith("/aksje/"):
            continue
        assert svar.status_code == 200, sti
        vist += 1
        assert not _lenker_til_euronext(_les(svar.get_data(as_text=True)).alle), sti
    assert vist >= len(demo.DEMOUNIVERS), vist


def test_ingen_kode_i_src_kaller_adressene():
    """AD-2. Ville feilet hvis en modul i src/ annet enn kursdata.py og
    app.py brukte adressene, eller hvis app.py gjorde noe annet med dem enn å
    gi adressen til malen, for eksempel hentet siden."""
    for fil in (ROT / "src").rglob("*.py"):
        tekst = fil.read_text(encoding="utf-8")
        navn = fil.relative_to(ROT).as_posix()
        if navn == "src/kursdata.py":
            continue
        for adresse in INVESTORSIDER.values():
            assert adresse not in tekst, (navn, adresse)
        if navn != "src/app.py":
            assert not re.search(r"\b(?:INVESTORSIDER|investorside)\b", tekst), navn
    app_tekst = (ROT / "src" / "app.py").read_text(encoding="utf-8")
    bruk = re.findall(r"^.*\b(?:INVESTORSIDER|investorside)\b.*$", app_tekst, re.MULTILINE)
    assert [b.strip() for b in bruk if not b.strip().startswith("#")] == [
        "from kursdata import Kursleser, investorside",
        "investorside=investorside(post.aksje.symbol),",
    ], bruk
