"""Story 8.2b: funnene fra UX-loggen som gruppen valgte 03.11 kl. 22:01
(spesifikasjonen spec-8-2b-funnene-fra-ux-loggen.md).

Testene bruker demobasen, laget i tmp_path av fixturen i conftest.py, som
flytter BASE_STI. Ingen nett og ingen henting.
"""

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

import app as app_modul
import demo
from hjelpetekster import hjelpetekster
from lagring_sqlite import demo_sti

STIL = (Path(__file__).resolve().parent.parent / "src" / "static" / "stil.css").read_text(encoding="utf-8")


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    # Som i test_demo.py: datoene på sidene avhenger ikke av året testen kjøres.
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


def _regel(velger: str, stil: str = STIL) -> str:
    treff = re.search(r"(?:^|\n)\s*(?::where\(\.side-[a-z]+\) )?" + re.escape(velger) + r"\s*\{([^}]*)\}", stil)
    assert treff, f"ingen regel for {velger}"
    return treff.group(1)


def _media(betingelse: str) -> str:
    treff = re.search(r"@media \(" + re.escape(betingelse) + r"\) \{(.*?)\n\}", STIL, flags=re.DOTALL)
    assert treff, betingelse
    return treff.group(1)


def _synlig(html: str) -> str:
    return re.sub(r"[ \t\r\n]+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def _figur(html: str) -> str:
    return html.split('<figure class="soeyler">', 1)[1].split("</figure>", 1)[0]


def _vindu(html: str, id_: str) -> str:
    return html.split(f'<div id="{id_}" class="hjelpevindu" popover>', 1)[1].split('<div id="hjelp-', 1)[0]


# a) Oversikten.


def test_tickerne_er_13_px_og_vannrette_paa_bred_skjerm(klient):
    """U20 og U57 (delvis). Ville feilet hvis tickeren fortsatt var 11 px,
    eller sto på høykant også i et bredt vindu, eller ikke lenger sto på
    høykant på smal skjerm, der 15 søyler skal få plass ved 390 px."""
    smal = _regel(".soeyler .ticker")
    assert "font-size: 13px" in smal and "writing-mode: vertical-rl" in smal
    bred = _regel(".soeyler .ticker", _media("min-width: 900px"))
    assert "writing-mode: horizontal-tb" in bred and "transform: none" in bred
    assert len(re.findall(r'<span class="ticker">', _figur(_html(klient, "/")))) == 14


def test_feltet_er_200_px_og_linja_3_px(klient):
    """U21 og U22. Ville feilet med feltet på 140 px eller linja på 2 px."""
    assert "height: 200px" in _regel(".soeyler .felt")
    assert "border-top: 3px dashed" in _regel(".soeyler .indekslinje")


def test_forklaringen_av_linja_staar_under_soeylene(klient):
    """U57 (delvis) og U22. Ville feilet hvis forklaringen manglet, sto over
    søylene, hadde en annen endring enn linja, eller ble lest to ganger av
    skjermleseren."""
    figur = _figur(_html(klient, "/"))
    klasse = re.search(r'<span class="indekslinje (\w+)"', figur).group(1)
    linja = re.search(r'<p class="skjult">Indeksen, den stiplede linja: ([^<]+)\.</p>', figur).group(1)
    forklaring = re.search(r'<p class="linjeforklaring" aria-hidden="true">(.*?)</p>', figur, flags=re.DOTALL)
    assert forklaring, figur
    assert f'<span class="linjeprove {klasse}"></span>' in forklaring.group(1)
    assert _synlig(forklaring.group(1)) == f"Stiplet linje: hovedindeksen {linja}"
    assert figur.index('class="felt"') < figur.index('class="linjeforklaring"')
    assert "border-top: 3px dashed" in _regel(".soeyler .linjeprove")


def test_hver_setning_i_slik_leser_staar_paa_egen_linje(klient):
    """U24. Ville feilet hvis setningene i et punkt sto etter hverandre i
    samme linje, eller linjeavstanden var endret."""
    del_ = _html(klient, "/").split('<section class="slik-leser"', 1)[1].split("</section>", 1)[0]
    punkter = re.findall(r"<li>(.*?)</li>", del_, flags=re.DOTALL)
    setninger = [re.findall(r'<span class="setning">([^<]*)</span>', p) for p in punkter]
    assert [len(s) for s in setninger] == [3, 3, 1], setninger
    assert all(s.endswith(".") for punkt in setninger for s in punkt)
    assert "display: block" in _regel("section.slik-leser .setning")
    assert "line-height" not in _regel("section.slik-leser .setning")


def test_symbolene_i_slik_leser_er_stoerre_i_samme_felt():
    """U25. Ville feilet med +1 og -1 på 10 px, pilene på 12 px eller
    musepekeren på 18 px, eller et større felt."""
    assert "font-size: 12px" in _regel(".utslagsfelt span")
    assert "font-size: 16px" in _regel(".symbolfelt .pil")
    assert "width: 22px; height: 22px" in _regel(".symbolfelt svg")
    assert "width: 36px; height: 36px" in _regel(".symbolfelt")


def test_hovedindeksen_og_soeylene_har_hvert_sitt_vindu(klient):
    """U26. Ville feilet hvis søylene sto i vinduet for hovedindeksen, hvis
    søylene ikke hadde sitt eget «?», eller hvis tekstene var like lange
    som før."""
    html = _html(klient, "/")
    indeks = _vindu(html, "hjelp-hovedindeks")
    soeyler = _vindu(html, "hjelp-soeylene")
    tekster = hjelpetekster()
    assert tekster["hovedindeksen"].tekst in indeks and "Søylene:" not in indeks
    assert tekster["soeylene"].tekst in soeyler and "Hovedindeksen:" not in soeyler
    tittel = re.search(r'<figcaption class="soeyletittel">(.*?)</figcaption>', _figur(html), flags=re.DOTALL).group(1)
    assert 'popovertarget="hjelp-soeylene"' in tittel
    assert html.count('popovertarget="hjelp-soeylene" aria-label') == 1
    # Tekstene var 45 og 68 ord før 8.2b.
    assert len(tekster["hovedindeksen"].tekst.split()) < 30
    assert len(tekster["soeylene"].tekst.split()) < 50
    assert "i stedet for tallet" not in tekster["hovedindeksen"].tekst
    assert "grå ved" not in tekster["soeylene"].tekst


def _merk(klient, symbol, til, tilbake):
    return klient.post("/min-liste/merk", data={"symbol": symbol, "til": til, "tilbake": tilbake})


@pytest.mark.parametrize(
    ("til", "tilbake", "anker"),
    [
        # Raden er borte, så stjernen sender til tabellen.
        ("fjern", "/min-liste", "#aksjene"),
        ("fjern", "/min-liste?periode=1-uke&sorter=kurs&orden=stigende", "#aksjene"),
        # Raden står fortsatt, så stjernen sender til raden som før.
        ("fjern", "/min-liste?vis=alle", "#rad-BRFE"),
        ("fjern", "/", "#rad-BRFE"),
        ("merk", "/min-liste", "#rad-HVDO"),
    ],
)
def test_stjernen_sender_til_tabellen_naar_raden_er_borte(klient, til, tilbake, anker):
    """U29. Ville feilet hvis stjernen i Min liste sendte til en rad som
    ikke finnes lenger, så siden sto øverst, eller hvis den sendte til
    tabellen også når raden står."""
    symbol = "HVDO" if til == "merk" else "BRFE"
    svar = _merk(klient, symbol, til, tilbake)
    assert svar.status_code == 303
    adresse, _, ankeret = svar.headers["Location"].partition("#")
    assert "#" + ankeret == anker
    html = _html(klient, adresse)
    assert html.count(f'id="{ankeret}"') == 1


def test_stjernen_sender_til_teksten_naar_lista_blir_tom(klient):
    """U29. Ville feilet hvis ankeret manglet når den siste aksjen er tatt ut
    og tabellen er borte."""
    for symbol in demo.MERKET_I_DEMOEN:
        svar = _merk(klient, symbol, "fjern", "/min-liste")
    assert svar.headers["Location"] == "/min-liste#aksjene"
    html = _html(klient, "/min-liste")
    assert '<p class="tom-liste" id="aksjene">' in html and 'class="tabellboks"' not in html
