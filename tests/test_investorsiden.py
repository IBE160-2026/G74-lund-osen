"""Story 10.5: lenken til selskapets investorside i aksjedetaljen.

Adressene er de gruppen godkjente 19.10 kl. 16:03, med de tre norske sidene
fra svaret kl. 19:49 (under story 10.5 i epics.md). Appen lenker aldri til
Euronexts nettsteder (rettingen 06.10), og ingen kode henter fra adressene
(AD-2). Ingen test her gaar paa nett: sidene lages med testklienten, og
basen ligger i tmp_path (conftest.py).
"""

import ast
import re
import shutil
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

import pytest

import app as app_modul
import demo
import kursdata
import lagring_sqlite
from kursdata import AKSJEUNIVERS, INVESTORSIDER, Kursrad, investorside
from lagring_sqlite import SqliteKurslager, aapne_base
from signalberegning import vurder
from vurderingsdata import Vurdering

ROT = Path(__file__).resolve().parent.parent
EPICS = ROT / "_bmad-output" / "planning-artifacts" / "epics.md"
EURONEXT = ("newsweb.oslobors.no", "oslobors.no", "live.euronext.com")
# Demoselskapet uten kurser (U3 i docs/ux-logg.md). Siden svarer 200 med en
# beskjed og uten graf, og dermed uten avsnittet om investorsiden (gruppens
# svar 23.10 kl. 09:24, b; før 404).
DEMO_UTEN_KURSER = {"MTFJ"}
# 61 kursdager, saa det er nok til en vurdering, og en dag midt i serien.
RADENE = [
    Kursrad(dato=date(2026, 9, 1) + timedelta(days=i), slutt=100.0 + i % 7, justert_slutt=100.0 + i % 7, volum=1000)
    for i in range(61)
]
VALGT_DAG = RADENE[45].dato


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
    """De 15 i den ekte basen i tmp_path (conftest.py), med kursene og
    vurderingen for siste dag, slik hentingen skriver dem, saa siden har
    kortene og sjekkene (gjennomgangen, ECH2)."""
    tilkobling = aapne_base(lagring_sqlite.BASE_STI)
    try:
        lager = SqliteKurslager(tilkobling)
        for aksje in AKSJEUNIVERS:
            lager.erstatt_serie(aksje.symbol, RADENE, datetime(2026, 11, 1, tzinfo=timezone.utc))
            innhold = vurder(RADENE, RADENE[-1].dato)
            assert isinstance(innhold, Vurdering)
            verdier = (*(getattr(innhold, k) for k in lagring_sqlite.VURDERINGSKOLONNER), None)
            with tilkobling:
                tilkobling.execute(lagring_sqlite._UPSERT, (aksje.symbol, RADENE[-1].dato.isoformat(), *verdier))
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
    """Hver adresse i href, src og action på siden, og lenkene og teksten i
    avsnittet med klassen investorside."""

    def __init__(self):
        super().__init__()
        self.alle: list[str] = []
        self.i_avsnittet = False
        self.i_lenken = False
        self.avsnittet: list[str] = []
        self.lenker: list[tuple[str, str]] = []
        self.attributter: list[dict] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.alle += [v for k, v in attrs if k in ("href", "src", "action") and v]
        if tag == "a" and a.get("href") and self.i_avsnittet:
            self.i_lenken = True
            self.lenker.append((a["href"], ""))
            self.attributter.append(a)
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


def _tekst(sider: _Lenker) -> str:
    return " ".join("".join(sider.avsnittet).split())


def _demotekst(navn: str) -> str:
    return (
        f"Børsmeldingene står på NewsWeb. {navn} er oppdiktet og har ingen investorside. "
        "I den ekte versjonen står lenken til selskapets investorside her."
    )


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
    manglet navnet i lenketeksten, lenket til NewsWeb, manglet på siden med
    en vurdering eller med «Velg dag» (gjennomgangen, ECH2 og ECH3), eller
    åpnet i en ny fane eller sendte adressen til appen videre (ECH7)."""
    for sti in (f"/aksje/{aksje.symbol}", f"/aksje/{aksje.symbol}?periode=velg&dag={VALGT_DAG.isoformat()}"):
        svar = klient.get(sti)
        assert svar.status_code == 200, sti
        html = svar.get_data(as_text=True)
        # Siste dag har vurderingen, så siden har kortene og sjekkene.
        assert ("periode=velg" in sti) or 'class="sjekkort' in html, sti
        sider = _les(html)
        assert sider.lenker == [(INVESTORSIDER[aksje.symbol], f"investorsiden til {aksje.navn}")], sti
        assert sider.attributter[0].get("rel") == "noreferrer" and "target" not in sider.attributter[0], sti
        assert _tekst(sider) == f"Børsmeldingene står på NewsWeb og ofte også på investorsiden til {aksje.navn}.", sti
        for symbol, adresse in INVESTORSIDER.items():
            if symbol != aksje.symbol:
                assert adresse not in html, (sti, symbol)


@pytest.mark.usefixtures("ekte_base")
def test_en_ekte_aksje_uten_adresse_faar_setningen_uten_lenke(klient, monkeypatch):
    """Gjennomgangen, ECH5. Ville feilet hvis en aksje i den ekte versjonen
    uten adresse fikk demoteksten om et oppdiktet selskap, en lenke, eller
    ingen setning om børsmeldingene."""
    monkeypatch.delitem(kursdata.INVESTORSIDER, "EQNR")
    sider = _les(klient.get("/aksje/EQNR").get_data(as_text=True))
    assert sider.lenker == []
    assert _tekst(sider) == "Børsmeldingene står på NewsWeb og ofte også på selskapets investorside."


def test_demoen_viser_teksten_og_ingen_lenke(demoklient):
    """Svaret kl. 19:49. Ville feilet hvis et demoselskap viste en lenke til
    en investorside, eller ikke sa at selskapet er oppdiktet og at lenken
    står her i den ekte versjonen (gjennomgangen, BH9 og VG8: alle)."""
    for aksje in demo.DEMOUNIVERS:
        svar = demoklient.get(f"/aksje/{aksje.symbol}")
        if aksje.symbol in DEMO_UTEN_KURSER:
            assert svar.status_code == 200
            assert _les(svar.get_data(as_text=True)).lenker == []
            continue
        assert svar.status_code == 200, aksje.symbol
        html = svar.get_data(as_text=True)
        assert "Eksempeltall" in html
        sider = _les(html)
        assert sider.lenker == [], aksje.symbol
        assert _tekst(sider) == _demotekst(aksje.navn), aksje.symbol
        for adresse in INVESTORSIDER.values():
            assert adresse not in html


def test_en_demobase_der_den_ekte_skal_ligge_viser_demoteksten(klient, demomal):
    """Gjennomgangen, ECH4. En demobase i stedet for den ekte basen, uten
    bryteren, viser «Eksempeltall» og demoteksten. Ville feilet hvis
    teksten fulgte bryteren og ikke merket."""
    Path(lagring_sqlite.BASE_STI).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(demomal, lagring_sqlite.BASE_STI)
    html = klient.get("/aksje/KVST").get_data(as_text=True)
    assert "Eksempeltall" in html
    sider = _les(html)
    assert sider.lenker == []
    assert _tekst(sider) == _demotekst("Kvitstein Mineral")


def test_navnet_escapes_i_avsnittet():
    """Gjennomgangen, ECH6. Ville feilet hvis navnet i avsnittet ble vist
    uten escaping (|safe), så et navn med & eller < ga feil HTML."""
    mal = (ROT / "src" / "templates" / "aksje.html").read_text(encoding="utf-8")
    avsnittet = mal.split("Story 10.5", 1)[1].split("{% endif %}", 1)[0]
    assert "detalj.aksje.navn" in avsnittet
    assert "|safe" not in avsnittet and "autoescape" not in mal


def _lenker_til_euronext(adresser) -> list[str]:
    return [h for h in adresser if any(d in h.lower() for d in EURONEXT)]


def test_ingen_mal_lenker_til_euronext():
    """Rettingen 06.10. Ville feilet hvis en mal fikk en adresse til
    newsweb.oslobors.no, oslobors.no eller live.euronext.com, med eller uten
    anførselstegn (gjennomgangen, BH6)."""
    for mal in (ROT / "src" / "templates").glob("*.html"):
        tekst = mal.read_text(encoding="utf-8").lower()
        for domene in EURONEXT:
            assert domene not in tekst, (mal.name, domene)


@pytest.mark.usefixtures("ekte_base")
def test_ingen_side_som_vises_lenker_til_euronext(klient):
    """Ville feilet hvis en side som vises, lenket til et av Euronexts
    nettsteder i href, src eller action, også en adresse laget i koden og
    ikke i malen, og også med «Velg dag» og 404 (gjennomgangen, BH7, VG7)."""
    stiene = ["/", "/min-liste", "/min-liste?vis=alle", "/aksje/FINNESIKKE"]
    for a in AKSJEUNIVERS:
        stiene += [f"/aksje/{a.symbol}", f"/aksje/{a.symbol}?periode=velg&dag={VALGT_DAG.isoformat()}"]
    for sti in stiene:
        svar = klient.get(sti)
        assert svar.status_code == (404 if "FINNESIKKE" in sti else 200), sti
        html = svar.get_data(as_text=True)
        assert not _lenker_til_euronext(_les(html).alle), sti
        assert not any(d in html.lower() for d in EURONEXT), sti


def test_ingen_demoside_lenker_til_euronext(demoklient):
    """Som over, for demoen. MTFJ har ingen kurser og svarer 200 med en
    beskjed (U3, gruppens svar 23.10 kl. 09:24, b; før 404)."""
    for sti in ("/", "/min-liste", *(f"/aksje/{a.symbol}" for a in demo.DEMOUNIVERS)):
        svar = demoklient.get(sti)
        assert svar.status_code == 200, sti
        html = svar.get_data(as_text=True)
        assert not _lenker_til_euronext(_les(html).alle), sti
        assert not any(d in html.lower() for d in EURONEXT), sti


def test_ingen_kode_i_src_kaller_adressene():
    """AD-2. Ville feilet hvis en modul i src/ annet enn kursdata.py og
    app.py brukte adressene, hvis app.py gjorde noe annet med dem enn å gi
    adressen til malen, eller hvis kursdata.py, der de står, importerte noe
    som kan hente fra nettet, eller brukte tabellen annet enn i oppslaget
    (gjennomgangen, BH2 og VG6)."""
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
    # kursdata.py: bare standardbiblioteket uten nett, og tabellen brukes
    # bare i oppslaget.
    tre = ast.parse((ROT / "src" / "kursdata.py").read_text(encoding="utf-8"))
    moduler = set()
    for node in ast.walk(tre):
        if isinstance(node, ast.Import):
            moduler |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            moduler.add((node.module or "").split(".")[0])
    assert moduler <= {"math", "dataclasses", "datetime", "typing"}, moduler
    bruk_i_kursdata = [
        n for n in ast.walk(tre) if isinstance(n, ast.Name) and n.id == "INVESTORSIDER" and isinstance(n.ctx, ast.Load)
    ]
    oppslaget = next(n for n in tre.body if isinstance(n, ast.FunctionDef) and n.name == "investorside")
    assert len(bruk_i_kursdata) == 1
    assert bruk_i_kursdata[0] in list(ast.walk(oppslaget))
