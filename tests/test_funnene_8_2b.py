"""Story 8.2b: funnene fra UX-loggen som gruppen valgte 03.11 kl. 22:01
(spesifikasjonen spec-8-2b-funnene-fra-ux-loggen.md).

Testene bruker demobasen, laget i tmp_path av fixturen i conftest.py, som
flytter BASE_STI. Ingen nett og ingen henting.
"""

import re
import shutil
from datetime import date, datetime, timedelta, timezone
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
    """Innholdet i alle @media-blokkene med betingelsen, med klammene talt,
    så en blokk på én linje ikke tar med resten av fila."""
    blokker = []
    for treff in re.finditer(r"@media \(" + re.escape(betingelse) + r"\) \{", STIL):
        dybde, i = 1, treff.end()
        while dybde:
            dybde += {"{": 1, "}": -1}.get(STIL[i], 0)
            i += 1
        blokker.append(STIL[treff.end() : i - 1])
    assert blokker, betingelse
    return "\n".join(blokker)


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
    # Tekstene var 44 og 78 ord før 8.2b (talt på a6d59bb).
    # Gjennomgangen (VG2): bare lengden, så fakta kan stå (regel 13).
    assert len(tekster["hovedindeksen"].tekst.split()) < 44
    assert len(tekster["soeylene"].tekst.split()) < 78
    assert "med kurs samme dag" in tekster["hovedindeksen"].tekst
    assert "grå ved 0,00" in tekster["soeylene"].tekst


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


# b) Aksjesiden, småting.


def _stripa(html: str) -> str:
    return html.split('<header class="stripe">', 1)[1].split("</header>", 1)[0]


def test_aksjesiden_hoerer_til_markedsoversikt_i_stripa(klient):
    """U2. Ville feilet hvis ingen knapp i stripa var merket på aksjesiden,
    hvis den var fylt som siden man står på, eller hvis oversikten ikke
    lenger hadde aria-current="page"."""
    for sti in ("/aksje/BRFE", "/aksje/MTFJ"):
        # Gruppens svar 04.11 kl. 22:23, 4: ikonene står foran navnet.
        stripa = re.sub(r'<svg class="ikon".*?</svg>', "", _stripa(_html(klient, sti)), flags=re.S)
        assert '<a class="sideknapp" href="/" aria-current="true">Markedsoversikt</a>' in stripa, sti
        assert 'aria-current="page"' not in stripa and stripa.count("aria-current") == 1, sti
    oversikten = re.sub(r'<svg class="ikon".*?</svg>', "", _stripa(_html(klient, "/")), flags=re.S)
    assert '<a class="sideknapp" href="/" aria-current="page">Markedsoversikt</a>' in oversikten
    kant = _regel('header.stripe a.sideknapp[aria-current="true"]')
    assert "border: 2px solid" in kant and "background" not in kant


def test_demoen_sier_at_ki_teksten_bare_er_for_siste_boersdag(klient):
    """U6. Ville feilet hvis demoen ga grunnen fra den ekte versjonen («KI
    var slått av …») for en tidligere dag, eller sa det for siste børsdag.
    Den ekte versjonen står i test_ki_visning.py."""
    tidligere = _html(klient, "/aksje/KVST?periode=velg&dag=2026-10-08")
    assert (
        '<p class="uten">Ingen KI-tekst for denne dagen: demoen har KI-tekst bare for siste børsdag.</p>' in tidligere
    )
    assert "KI var slått av" not in tidligere
    assert "demoen har KI-tekst bare" not in _html(klient, "/aksje/BRFE")


def test_ingressen_i_historikken_er_kort(klient):
    """U16. Ville feilet med «lest fra basen og aldri regnet på nytt» eller
    «signalstyrke 2 eller mer» i ingressen, eller hvis det sto i verken
    ingressen eller hjelpen."""
    html = _html(klient, "/aksje/BRFE")
    ingress = re.search(r'<p class="ingress">(.*?)</p>', html, flags=re.DOTALL).group(1)
    assert "lest fra basen" not in ingress and "eller mer" not in ingress
    # Ingressen var 60 ord før 8.2b, med navnet for BRFE.
    assert len(ingress.split()) <= 25, ingress
    vinduet = _vindu(html, "hjelp-historikk")
    assert "lest fra basen og aldri regnet på nytt" in vinduet and "signalstyrke 2 eller mer" in vinduet


def test_endringen_har_alltid_ukedagen_og_datoen(klient):
    """U31. Ville feilet hvis kortet bare hadde ukedagene når ingen børsdag
    ligger mellom de to dagene."""
    endring = _html(klient, "/aksje/BRFE").split('<div class="noekkeltall endring">', 1)[1].split("</div>", 1)[0]
    assert re.search(r'<span class="forklaring">fra torsdag 08\.10 til fredag 09\.10</span>', endring), endring


def test_periodeknappene_og_velg_dag_er_like_hoeye():
    """U37. Ville feilet hvis lenkene og knappen hadde ulik høyde, eller
    teksten ikke sto midt i dem."""
    regel = _regel("nav.periodevalg a, nav.periodevalg button")
    for del_ in ("display: inline-flex", "align-items: center", "box-sizing: border-box", "min-height: 36px"):
        assert del_ in regel, del_
    assert "padding: 0 12px" in regel
    assert "min-height: 36px" in _regel('nav.periodevalg input[type="date"]')
    assert "align-items: center" in _regel("nav.periodevalg ul")


def test_overskriften_sier_dagene_naar_serien_er_kortere(klient):
    """U39. Varde Systemer er nylig notert. Ville feilet hvis overskriften
    sa «6 måneder fram til» en dag serien ikke går tilbake til."""
    html = _html(klient, "/aksje/VRDS")
    tittel = re.search(rf'<h2 id="{app_modul.GRAFANKER}">(.*?)<button', html, flags=re.DOTALL).group(1).strip()
    assert re.fullmatch(r"Kursutvikling fra \d\d\.\d\d til 09\.10", tittel), tittel
    assert "6 måneder" not in tittel
    lang = re.search(rf'<h2 id="{app_modul.GRAFANKER}">(.*?)<button', _html(klient, "/aksje/BRFE"), flags=re.DOTALL)
    assert lang.group(1).startswith("Kursutvikling, 6 måneder")


def _svg(html: str) -> str:
    return html.split('<svg class="graf"', 1)[1].split("</svg>", 1)[0]


def test_grafen_har_felt_til_tallene_datoene_og_navnene(klient):
    """U41 og U47. Ville feilet hvis en linje gikk inn der navnene står, hvis
    tallene eller datoene sto inne i tegneflaten, eller hvis den stiplede
    linja ikke hadde navnet «Hovedindeksen» i Dempet."""
    svg = _svg(_html(klient, "/aksje/BRFE"))
    xer = [
        float(par.split(",")[0])
        for linje in re.findall(r'<polyline class="[a-z0-9]+" points="([^"]*)"', svg)
        for par in linje.split()
    ]
    navn = dict(re.findall(r'<text class="linjenavn (\w+)" x="([\d.]+)"', svg))
    assert set(navn) == {"kurs", "snitt", "indeks"}
    assert min(float(x) for x in navn.values()) > max(xer)
    assert re.search(r'<text class="linjenavn indeks" [^>]*>Hovedindeksen</text>', svg)
    assert "var(--dempet)" in _regel(".linjenavn.indeks")
    venstre = min(xer)
    for x in re.findall(r'<text class="rutetekst" text-anchor="end" x="([\d.]+)"', svg):
        assert float(x) < venstre
    assert len(re.findall(r'class="rutetekst"', svg)) == 3
    bunn = max(float(y) for y in re.findall(r'<line class="maanedsstrek"[^>]*y2="([\d.]+)"', svg))
    for y in re.findall(r'<text class="maanedstekst"[^>]*y="([\d.]+)"', svg):
        assert float(y) > bunn


def test_maanedspilene_er_knapper_med_kant(klient):
    """U44 og U68 (c). Ville feilet med understreket tekst, under 44 px, eller
    uten kanten rundt månedsvelgeren, som er én knapp med pilene på hver side."""
    regel = _regel(".maanedspiler a.pil")
    assert "text-decoration: none" in regel and "min-height: 44px" in regel
    assert "underline" not in regel
    assert "border: 1px solid" in _regel(".maanedspiler")
    assert re.search(r'<a class="pil" href="[^"]*">‹ ', _html(klient, "/aksje/BRFE"))


# c) Aksjesiden som på designtavla.


def test_ki_teksten_staar_etter_grafen_foer_historikken(klient):
    """U66. Ville feilet med KI-teksten før grafen, eller etter historikken.
    Story 3.4h: boblen til investorsiden står nederst, etter historikken, og
    ikke lenger mellom grafen og KI-teksten."""
    html = _html(klient, "/aksje/BRFE")
    assert html.index("Hvorfor signalet ble") < html.index('<svg class="graf"') < html.index('<section class="ki"')
    assert html.index('<section class="ki"') < html.index('<section class="historikk"')
    assert html.index('<section class="historikk"') < html.index('class="investorboble"')


def test_bryteren_staar_i_rammen_som_en_bryter(klient):
    """U33, U46 og U67 (delvis). Ville feilet med knappen under rammen, uten
    role="switch", uten «På» og «Av», eller med gult i bryteren."""
    html = _html(klient, "/aksje/BRFE")
    ki = html.split('<section class="ki"', 1)[1].split("</section>", 1)[0]
    topp = ki.split('<div class="ki-topp">', 1)[1].split("</form>", 1)[0]
    # Story 10.9, del C: rammen heter «Signalet forklart».
    assert "Signalet forklart</span>" in topp and 'role="switch" aria-checked="true"' in topp
    assert '<span class="navn">KI-tekst</span>' in topp and '<span class="verdi" aria-hidden="true">På</span>' in topp
    assert html.count('class="ki-bryter"') == 1
    # Gjennomgangen (VG1): gult heter også oransje og baand-ut i stilen.
    regler = re.findall(r"\.ki-bryter[^{]*\{([^}]*)\}", STIL)
    assert len(regler) >= 5
    for regel in regler:
        for farge in ("gul", "oransje", "baand-ut", "hjelp-bakgrunn"):
            assert farge not in regel, (farge, regel)
    assert "var(--blekk)" in _regel('.ki-bryter [aria-checked="true"] .spor')
    assert "border-radius: 16px" in _regel(".ki") and "font-size: 17px" in _regel(".ki p.ki-tekst")


def test_med_ki_av_staar_bare_bryteren(klient):
    """U33 og svaret 25.10 kl. 00:51 (VG11): med KI av står bryteren og
    setningen om dagene. Story 10.9, del C (gruppens svar 06.11 kl. 22:23):
    rammen «Signalet forklart» står også med KI av, med appens setninger og
    bryteren fast øverst, uten KI-tekst. Navnet på testen står fra 8.2b.
    Ville feilet hvis KI-teksten sto med KI av, eller rammen manglet."""
    klient.set_cookie(app_modul.KAPSEL, "av")
    html = _html(klient, "/aksje/BRFE")
    ki = html.split(f'<section class="ki" id="{app_modul.KI_ANKER}"', 1)[1].split("</section>", 1)[0]
    assert "Signalet forklart</span>" in ki and '<p class="dagene">' in ki and 'class="ki-tekst"' not in ki
    assert re.search(r'<form class="ki-bryter"[^>]*>', ki)
    assert 'role="switch" aria-checked="false"' in html and '<span class="verdi" aria-hidden="true">Av</span>' in html


def test_tallene_i_ki_teksten_har_prikket_strek():
    """U67 (delvis, designregler §4). Ville feilet hvis et tall ikke var
    markert, hvis tallene ble delt på en annen måte enn kontrollen deler dem
    (gjennomgangen, VG5), hvis et tegn i teksten ble endret, eller hvis &
    ble en del av et tall."""
    from ki_kontroll import _SIFFER
    from ki_visning import prikkede_tall

    tekst = "Trend ga +1 og 3 av 3 slo ut 2 dager, 1 234 og MA50 08.10, og R&D & 2."
    ut = str(prikkede_tall(tekst))
    markert = re.findall(r'<span class="tall">([^<]*)</span>', ut)
    assert markert == [treff.group(0) for treff in _SIFFER.finditer(tekst)]
    assert markert == ["1", "3", "3", "2", "1", "234", "50", "08.10", "2"]
    assert re.sub(r"<[^>]+>", "", ut) == tekst.replace("&", "&amp;")
    assert "&#" not in ut
    assert str(prikkede_tall("<b>3</b>")) == '&lt;b&gt;<span class="tall">3</span>&lt;/b&gt;'
    assert "underline dotted currentColor" in _regel(".ki .tall")


def test_innledningen_under_tittelen(klient):
    """U62. Ville feilet uten innledning, med den et annet sted, eller med
    en som sa sjekkene på en side uten sjekker."""
    html = _html(klient, "/aksje/BRFE")
    assert '<p class="innledning">Siden viser sjekkene for Brattfjell Energi med tallene bak' in html
    assert html.index('<p class="meta">') < html.index('<p class="innledning">') < html.index('class="sammendrag"')
    assert '<p class="innledning">Siden viser kursgrafen for Varde Systemer' in _html(klient, "/aksje/VRDS")


def test_kortet_retning_sier_hva_sjekkene_ga(klient):
    """U63. BRFE fikk -1 på alle tre, og LKSV -1 på trend og +1 på de andre.
    Ville feilet uten forklaringen, eller med sjekkene gruppert feil."""
    retning = _html(klient, "/aksje/BRFE").split("Hjelp: retning", 1)[1].split("</div>", 1)[0]
    assert '<span class="forklaring">Trend, bevegelse og interesse ga -1. </span>' in retning
    blandet = _html(klient, "/aksje/LKSV").split("Hjelp: retning", 1)[1].split("</div>", 1)[0]
    forklaring = re.search(r'<span class="forklaring">([^<]*)</span>', blandet).group(1).strip()
    assert forklaring == "Bevegelse og interesse ga +1. Trend ga -1.", forklaring


def test_summen_under_sjekkene(klient):
    """U64 og gruppens svar 04.11 kl. 09:48. Ville feilet uten raden, med en
    annen styrke eller retning enn kortene over, eller med T, B og I foran
    styrken, der tabellen har styrken først (8.0e)."""
    html = _html(klient, "/aksje/BRFE")
    rad = re.search(r'<p class="sumrad">(.*?)</p>', html, flags=re.DOTALL).group(1)
    assert _synlig(rad) == "Sum 3 av 3 T -1 B -1 I -1 ↓Negativ", _synlig(rad)
    assert 'class="pille tre-av-tre"' in rad
    # Story 8.20a (del A): fotnoten under summen er flyttet, så summen står
    # foran grafen.
    assert html.index('class="sjekkort-rad"') < html.index('class="sumrad"') < html.index("<figure>")


def test_historikken_er_en_kompakt_tabell(klient):
    """U68. Ville feilet uten kolonnenavnene, med summen under uka i stedet
    for i en egen kolonne, eller med ukedagen borte for skjermleseren.
    Story 8.20a (del B, spørsmål 6 i 8.20): «Velg dag» øverst er borte, og
    datovelgeren står bare ved grafen."""
    html = _html(klient, "/aksje/BRFE")
    del_ = html.split('<section class="historikk"', 1)[1].split("</section>", 1)[0]
    hode = re.search(r'<div class="ukehode" aria-hidden="true">(.*?)</div>', del_).group(1)
    assert re.findall(r"<span>([^<]*)</span>", hode) == ["Uke", "Man", "Tir", "Ons", "Tor", "Fre", "Uka"]
    assert "grid-column: 7" in _regel(".ukesum")
    topp = del_.split('<div class="historikktopp">', 1)[1].split("</div>", 1)[0]
    assert "Signalet dag for dag" in topp
    assert "<form" not in del_ and 'name="dag"' not in del_
    assert re.search(
        r'<a class="dato" href="/aksje/BRFE\?dag=2026-10-09"><span class="ukedag">fredag</span> 09\.10</a>', del_
    )
    assert "clip: rect(0 0 0 0)" in _regel("li.dag .ukedag")
    assert "display: none" in _regel(".ukehode", _media("max-width: 760px"))


# d) Forsiden og Min liste.


def test_oversikten_har_aksjene_med_antallet_og_valget(klient):
    """U59. Ville feilet uten overskriften «Aksjene» med antallet over
    tabellen, eller uten valget «Alle / Min liste», med «Alle» valgt og
    perioden med i lenken til Min liste."""
    html = _html(klient, "/?periode=1-uke")
    topp = html.split('<div class="aksjetopp">', 1)[1].split("</nav>", 1)[0]
    assert re.search(r'<h2 class="aksjetittel">Aksjene <span class="antall">15</span></h2>', topp)
    # Story 8.23 (tillegg 2, B7): «Min liste» filtrerer tabellen på
    # oversikten (?vis=min), og begge lenkene går til tabellen.
    assert re.search(
        r'<a class="visknapp" href="/\?periode=1-uke#aksjene" aria-current="true">Alle <span class="antall">15</span></a>',
        topp,
    )
    assert re.search(
        r'<a class="visknapp" href="/\?vis=min&amp;periode=1-uke#aksjene">Min liste <span class="antall">5</span></a>',
        topp,
    )
    assert html.index('<div class="aksjetopp">') < html.index('class="tabellboks"')
    assert html.index('<section class="hovedindeks"') < html.index('<div class="aksjetopp">')
    assert '<div class="aksjetopp">' not in _html(klient, "/min-liste")


def test_min_liste_har_tittelen_med_antallet(klient):
    """U69. Demoen har fem merket, og tre av dem skilte seg ut. Ville feilet
    med tittelen «Min liste» når noe er merket og vurdert, med et annet
    antall, eller med valget før tittelen."""
    html = _html(klient, "/min-liste")
    topp = html.split('<div class="listetopp">', 1)[1].split("</nav>", 1)[0]
    assert '<h1 class="overskrift"><mark>3 av 5 i Min liste</mark> skilte seg ut fredag</h1>' in topp
    assert topp.index("<h1") < topp.index('<nav class="visvalg"')
    assert "justify-content: space-between" in _regel(".listetopp, :where(.side-oversikt) .aksjetopp")
    # Ville feilet hvis tittelen talte en aksje som ikke er merket: under
    # «Alle» står alle sju som skilte seg ut (mutanten Md1). Story 8.23
    # (tillegg 1): med «Alle» sier tittelen begge tallene.
    assert '<h1 class="overskrift"><mark>7 av 15</mark> skilte seg ut fredag, 3 av dem i Min liste</h1>' in _html(
        klient, "/min-liste?vis=alle"
    )
    _merk(klient, "BRFE", "fjern", "/min-liste")
    assert "<mark>2 av 4 i Min liste</mark>" in _html(klient, "/min-liste")
    for symbol in demo.MERKET_I_DEMOEN:
        _merk(klient, symbol, "fjern", "/min-liste")
    assert '<h1 class="overskrift">Min liste</h1>' in _html(klient, "/min-liste")


# Gjennomgangen av 8.2b.


def test_velg_dag_i_historikken_godtar_bare_dager_siden_viser(klient):
    """BH1, ECH2. Ville feilet hvis feltet godtok seriens første dag, som
    siden avviser, eller sendte til toppen av siden.
    Story 8.20a (del B, spørsmål 6 i 8.20): feltet i historikken er borte, så
    testen gjelder feltet ved grafen, det eneste på siden, som sender til
    grafen. Navnet står, fordi docs/kvalitetssikring.md viser til det."""
    html = _html(klient, "/aksje/VRDS")
    assert html.count('type="date"') == 1
    skjema = html.split('<nav class="periodevalg"', 1)[1].split("</form>", 1)[0]
    velg = re.search(r'<input type="date" id="velg-dag"[^>]*min="([^"]+)"', skjema).group(1)
    # Den første dagen feltet godtar, viser siden, og dagen før avvises.
    assert 'class="periodebeskjed"' not in _html(klient, f"/aksje/VRDS?dag={velg}")
    foer = (date.fromisoformat(velg) - timedelta(days=1)).isoformat()
    assert 'class="periodebeskjed"' in _html(klient, f"/aksje/VRDS?dag={foer}")
    assert 'action="/aksje/VRDS#kursgrafen"' in skjema


def test_demogrunnen_ikke_for_siste_dag(klient, monkeypatch):
    """BH3, ECH3. En demobase uten KI-tekst for siste dag, som når
    demo_ki_tekster.json ikke kan leses. Ki_logg kan ikke slettes fra (AD-7),
    så loggen svarer at raden mangler. Ville feilet hvis siden sa at demoen
    har KI-tekst bare for siste børsdag, på den dagen."""
    from ki_visning import INGEN_RAD, KIVisning

    monkeypatch.setattr(app_modul, "bygg_ki_visning", lambda *a, **k: KIVisning(INGEN_RAD))
    html = _html(klient, "/aksje/BRFE")
    assert "demoen har KI-tekst bare" not in html
    assert "Ingen KI-tekst for denne dagen" in html
    # Story 3.7 (gjennomgangen, VG4): linja om modellen og lenken står bare i
    # den ekte versjonen. Ville feilet hvis demoen fikk dem.
    assert "på en maskin med en språkmodell" not in html and app_modul.KI_TEKSTEN_URL not in html


def test_tittelen_i_min_liste_bare_med_en_vurdert_merket(klient):
    """BH2, ECH8, VG6. Bare Matfjord, uten kurser, er merket. Ville feilet
    med «0 av 1 i Min liste skilte seg ut»."""
    for symbol in demo.MERKET_I_DEMOEN:
        _merk(klient, symbol, "fjern", "/min-liste")
    _merk(klient, "MTFJ", "merk", "/min-liste")
    html = _html(klient, "/min-liste")
    assert '<h1 class="overskrift">Min liste</h1>' in html and "i Min liste</mark>" not in html


def test_valget_paa_oversikten_beholder_sorteringen(klient):
    """BH7, ECH7. Ville feilet hvis «Alle» eller «Min liste» mistet
    sorteringen."""
    topp = _html(klient, "/?sorter=kurs&orden=stigende").split('<div class="aksjetopp">', 1)[1].split("</nav>", 1)[0]
    assert 'href="/?sorter=kurs&amp;orden=stigende#aksjene" aria-current="true">Alle' in topp
    # Story 8.23 (tillegg 2, B7): «Min liste» filtrerer på oversikten.
    assert 'href="/?vis=min&amp;sorter=kurs&amp;orden=stigende#aksjene">Min liste' in topp


def test_de_nye_radene_brytes_paa_smal_skjerm():
    """VG3: 390 px uten vannrett rulling. Hver ny rad med flere deler
    brytes heller enn å gå ut av siden. Sjekket også i Edge med en ramme på
    390 px (spesifikasjonen)."""
    for velger in (
        ".listetopp, :where(.side-oversikt) .aksjetopp",
        "p.sumrad",
        ".maanedspiler",
        ".historikktopp",
        ".ki .ki-topp",
        ".soeyler .linjeforklaring",
    ):
        assert "flex-wrap: wrap" in _regel(velger), velger
    assert "min-width: 0" in _regel(".listetopp h1")
    assert "max-width: 100%" in _regel(".maanedspiler")


def test_bryteren_har_kant_med_hoey_kontrast():
    """ECH9. Ville feilet hvis sporet bare var bakgrunn, som forsvinner med
    høy kontrast."""
    assert "border: 1px solid CanvasText" in _regel(".ki-bryter .spor", _media("forced-colors: active"))


# Gruppens svar 04.11 kl. 09:48, 09:58, 10:01 og 10:04.


def _kontrast(a: str, b: str) -> float:
    def lys(farge: str) -> float:
        kanaler = [int(farge.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4)]
        kanaler = [k / 12.92 if k <= 0.03928 else ((k + 0.055) / 1.055) ** 2.4 for k in kanaler]
        return 0.2126 * kanaler[0] + 0.7152 * kanaler[1] + 0.0722 * kanaler[2]

    hoey, lav = sorted((lys(a), lys(b)), reverse=True)
    return (hoey + 0.05) / (lav + 0.05)


def test_soeylene_er_lyse_og_moerke(klient):
    """Svaret kl. 09:58. Ville feilet hvis en søyle fra 2 % opp eller ned
    ikke var mørk, en under var mørk, grensen ikke var den fra børsometeret,
    eller forklaringen under søylene manglet."""
    from boersometer import GRENSE_STERK
    from tallformat import avrundet

    figur = _figur(_html(klient, "/"))
    klasser = re.findall(r'<span class="stolpe (opp|ned|null) (lys|sterk)" style=', figur)
    endringer = re.findall(r"<li>[^<]*\): ([^<]+?%)[,.]", figur)
    assert len(klasser) == len(endringer) >= 10
    tall_ = [float(e.replace(" ", "").replace("%", "").replace(",", ".")) for e in endringer]
    assert [k[1] for k in klasser] == ["sterk" if abs(avrundet(t, "endring")) >= GRENSE_STERK else "lys" for t in tall_]
    assert {k[1] for k in klasser} == {"lys", "sterk"}
    forklaring = re.search(r'<p class="soeylefarger" aria-hidden="true">(.*?)</p>', figur, flags=re.DOTALL).group(1)
    ventet = "Lys søyle: under 2 %, opp eller ned Mørk søyle: 2 % eller mer, opp eller ned"
    assert _synlig(forklaring) == ventet, _synlig(forklaring)
    assert figur.index('class="felt"') < figur.index('class="soeylefarger"')
    assert "Lys søyle" not in re.sub(r'<p class="soeylefarger".*?</p>', "", figur, flags=re.DOTALL)


@pytest.mark.parametrize(("endring", "ventet"), [(1.994, "lys"), (1.995, "sterk"), (-2.0, "sterk"), (-1.99, "lys")])
def test_grensen_for_moerk_soeyle_er_tallet_slik_det_vises(endring, ventet):
    """Svaret kl. 09:58, som fargetrinn i børsometeret. Ville feilet hvis
    1,995 %, som vises som 2,00 %, var lys."""
    assert app_modul.soeylestyrke(endring) == ventet


def test_de_lyse_soeylene_kan_ses():
    """Svaret kl. 09:58 og designregler §5 (kontrast). Søylene har ingen
    tekst, så også de lyse har minst 3:1 mot kortet og bakgrunnen. Ville
    feilet med de lyse trinnene fra børsometeret, som er om lag 1,4:1, eller
    med lys lik mørk."""
    rot = dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", _regel(":root")))
    for lys, moerk in (("soeyle-lys-opp", "opp"), ("soeyle-lys-ned", "ned")):
        for bak in ("kort", "bakgrunn"):
            assert _kontrast(rot[lys], rot[bak]) >= 3.0, (lys, bak)
        assert _kontrast(rot[lys], rot["kort"]) < _kontrast(rot[moerk], rot["kort"]) - 1
    assert "var(--soeyle-lys-opp)" in _regel(".soeyler .stolpe.opp")
    assert "var(--opp)" in _regel(".soeyler .stolpe.opp.sterk")
    assert "var(--ned)" in _regel(".soeyler .stolpe.ned.sterk")


def _ruter(html: str) -> dict[str, str]:
    """Ruta i børsometeret per ticker, uten den skjulte teksten."""
    return {
        m.group(1): m.group(0)
        for m in re.finditer(
            r'<a class="rute [^"]*"[^>]*>\s*<span class="ticker">([A-Z0-9]+)</span>.*?</a>', html, re.S
        )
    }


def test_styrken_staar_i_rutene_som_i_tabellen(klient):
    """Svarene kl. 10:01 og 10:04. Ville feilet hvis 3 av 3 og 2 av 3 ikke
    hadde ringen fra tabellen siste børsdag, hvis 1 av 3 og 0 av 3 hadde
    ring, eller hvis en rute med styrke manglet den."""
    ruter = _ruter(_html(klient, "/boersometer"))
    assert len(ruter) == 15
    sett = set()
    for symbol, rute in ruter.items():
        styrke = re.search(r'<span class="(styrke[^"]*)">(\d) av 3</span>', rute)
        if "ramme-gul" in rute:
            assert styrke.groups() == ("styrke pille tre-av-tre", "3"), symbol
        elif "ramme-moerk" in rute:
            assert styrke.groups() == ("styrke pille to-av-tre", "2"), symbol
        elif styrke:
            assert styrke.group(1) == "styrke" and styrke.group(2) in "01", symbol
        else:
            assert 'class="tekst"' in rute or "Uten data" in rute, symbol
        sett.add(styrke.group(2) if styrke else None)
    assert {"3", "2"} <= sett and sett & {"1", "0"}, sett
    assert 'class="merke"' not in "".join(ruter.values())


def test_en_annen_dag_er_styrken_tekst_og_merket_star(klient):
    """Svarene kl. 10:01 og 10:04, med designregler §3: ringen står bare for
    siste børsdag, og gul ramme sier fortsatt 3 av 3 siste børsdag. Ville
    feilet med ringen en annen dag, eller uten merket."""
    ruter = _ruter(_html(klient, "/boersometer?periode=velg&dag=2026-10-01"))
    gule = [r for r in ruter.values() if "ramme-gul" in r]
    assert gule and all(
        '<span class="merke"><span class="skjult">, </span>3 av 3 siste børsdag</span>' in r for r in gule
    )
    assert "pille" not in "".join(ruter.values())
    # Gjennomgangen (BH3): styrken for dagen står også, som tekst.
    assert all(re.search(r'<span class="styrke">\d av 3</span>', r) for r in gule)


def test_skriften_og_rammen_i_boersometeret():
    """Svarene kl. 10:01 og 10:04. Ville feilet med teksten i rutene eller ved
    bransjenavnene under 14 px, «Mål mot børsen» under 16 px, eller uten
    rammen rundt bransjen. Story 8.20b: «Mål mot børsen» er et kort med
    overskriften i 24 px, og «Hva fargene betyr» er kortet «Slik leser du
    børsometeret», i stilen fra oversikten."""
    assert "font-size: 14px" in re.search(r"side-oversikt\) \.rute \{([^}]*)\}", STIL).group(1)
    for velger in (".rute .merke", ".rute .styrke", ".rute .tekst"):
        assert "font-size: 14px" in _regel(velger), velger
    assert "font-size: 14px" in re.search(r"\.kart section\.bransje h2 \{([^}]*)\}", STIL).group(1)
    assert "font-size: 16px" in _regel("section.maal")
    assert "font-size: 24px" in _regel("section.maal h2")
    assert "section.fargene" not in STIL
    assert any(
        "box-shadow: inset 0 0 0 1px var(--strek-2)" in r
        for r in re.findall(r"\.kart section\.bransje \{([^}]*)\}", STIL)
    )


@pytest.mark.parametrize(
    ("sti", "vindu"),
    [("/", "hjelp-perioden"), ("/min-liste", "hjelp-sammenlign"), ("/boersometer", "hjelp-perioden")],
)
def test_spoersmaalstegnet_for_periodene_staar_foerst(klient, sti, vindu):
    """Svaret kl. 10:04. Ville feilet med «?» etter knappene, som før, eller
    uten «?» i raden."""
    rad = _html(klient, sti).split('<div class="periodehode">', 1)[1].split("</nav>", 1)[0]
    assert rad.lstrip().startswith(f'<button type="button" class="hjelpeknapp" popovertarget="{vindu}"'), rad[:120]
    assert rad.index(f'popovertarget="{vindu}"') < rad.index("<nav")


def test_nivaa_3_har_plass_til_det_lengste():
    """Gjennomgangen av 8.2b (BH2, ECH2, VG1). Det lengste på nivå 3 er en gul
    ramme en annen dag: navnet, endringen, styrken og merket «3 av 3 siste
    børsdag» på to linjer, regnet med tallene i stil.css. Ville feilet med
    grensen 112 × 103, der merket kunne kuttes."""
    from boersometer import NIVAA_3

    rute = re.search(r"side-oversikt\) \.rute \{([^}]*)\}", STIL).group(1)
    skrift = int(re.search(r"font-size: (\d+)px", rute).group(1))
    linje = skrift * float(re.search(r"line-height: ([\d.]+)", rute).group(1))
    gap = int(re.search(r"gap: (\d+)px", rute).group(1))
    luft = [int(v) for v in re.search(r"padding: (\d+)px (\d+)px", rute).groups()]
    ramme = int(
        re.search(r"border: (\d+)px solid", _regel(".rute.ramme-gul, :where(.side-oversikt) .proeve.ramme-gul")).group(
            1
        )
    )
    hoeyde = 2 * ramme + 2 * luft[0] + 5 * linje + 3 * gap
    bredde = 2 * ramme + 2 * luft[1] + 0.62 * skrift * len("3 av 3 siste")
    assert NIVAA_3[1] >= hoeyde and NIVAA_3[0] >= bredde, (NIVAA_3, hoeyde, bredde)


def test_hjelpen_i_docs_sier_samme_grense_som_koden():
    """Gjennomgangen av 8.2b (VG5): docs/hjelp.md skriver grensen for mørk
    søyle som tekst. Ville feilet hvis GRENSE_STERK ble endret uten hjelpen."""
    from boersometer import GRENSE_STERK
    from tallformat import tall

    hjelp = (Path(__file__).resolve().parent.parent / "docs" / "hjelp.md").read_text(encoding="utf-8")
    grense = tall(GRENSE_STERK, "grense").replace(" ", " ")
    assert f"En søyle er mørk fra {grense} opp eller ned" in hjelp


# --- Rettet 04.11 kl. 19:21 (gruppens svar) -----------------------------------


def test_styrkens_grense_er_regnet_fra_stilen():
    """Svaret kl. 19:21, 1: styrken har sin egen, lavere grense, regnet for
    14 px med ringen og rammen: den gule rammen, luften, symbolet, endringen
    og «3 av 3» i pillen med kanten, med tallene i stil.css. Teksten er regnet
    med 0,5 em per tegn; i Edge er «3 av 3» 38,78 px, 0,46 em per tegn
    (spesifikasjonen 8.2b, «Rettet 04.11 kl. 19:21»). Ville feilet med en
    grense der ringen kunne kuttes, eller med en grense som ikke er lavere
    enn nivå 3."""
    from boersometer import NIVAA_3, STYRKE

    rute = re.search(r"side-oversikt\) \.rute \{([^}]*)\}", STIL).group(1)
    skrift = int(re.search(r"font-size: (\d+)px", rute).group(1))
    linje = skrift * float(re.search(r"line-height: ([\d.]+)", rute).group(1))
    gap = int(re.search(r"gap: (\d+)px", rute).group(1))
    luft = [int(v) for v in re.search(r"padding: (\d+)px (\d+)px", rute).groups()]
    ramme = int(
        re.search(r"border: (\d+)px solid", _regel(".rute.ramme-gul, :where(.side-oversikt) .proeve.ramme-gul")).group(
            1
        )
    )
    # Gjennomgangen av rettingen (VG4): styrken har sin egen skriftstørrelse.
    styrke = int(re.search(r"font-size: (\d+)px", _regel(".rute .styrke")).group(1))
    assert styrke == skrift, (styrke, skrift)
    pille = _regel(".pille")
    pluft = [float(v) * 16 for v in re.search(r"padding: ([\d.]+)rem ([\d.]+)rem", pille).groups()]
    pkant = float(re.search(r"border: ([\d.]+)px solid", _regel(".pille.tre-av-tre")).group(1))
    ring = linje + 2 * pluft[0] + 2 * pkant
    hoeyde = 2 * ramme + 2 * luft[0] + 2 * linje + ring + 2 * gap
    bredde = 2 * ramme + 2 * luft[1] + 2 * pkant + 2 * pluft[1] + 0.5 * skrift * len("3 av 3")
    assert STYRKE[1] >= hoeyde and STYRKE[0] >= bredde, (STYRKE, hoeyde, bredde)
    assert STYRKE[0] < NIVAA_3[0] and STYRKE[1] < NIVAA_3[1]


@pytest.mark.parametrize(
    ("b", "h", "ventet"),
    [(81, 75, True), (80, 75, False), (81, 74, False), (125, 105, True)],
)
def test_styrkeplass(b, h, ventet):
    """Svaret kl. 19:21, 1. Ville feilet hvis grensen ikke var STYRKE,
    (81, 75)."""
    from boersometer import styrkeplass

    assert styrkeplass(b, h) is ventet


def test_troy_viser_2_av_3_ved_1280_px(klient):
    """Svaret kl. 19:21, 1: i demoen er TROY 86 × 191 px ved 1280 px, målt
    i Edge, på nivå 2 i kartet på 1008 px. Ville feilet med den gamle
    grensen, der styrken bare sto på nivå 3, eller uten velgeren som lar
    styrken stå på nivå 2."""
    html = _html(klient, "/boersometer")
    klasser, rute = re.search(
        r'<a class="rute ([^"]*)"[^>]*>\s*<span class="ticker">TROY</span>(.*?)</a>', html, re.S
    ).groups()
    assert "nivaa-bredest-2" in klasser.split() and "styrke-bredest" in klasser.split(), klasser
    assert '<span class="styrke pille to-av-tre">2 av 3</span>' in rute
    blokk = _media("width > 760px").split("@container (width >= 1008px) {", 1)[1].split("}", 1)[0]
    assert ".rute.nivaa-bredest-2:not(.styrke-bredest) > .styrke" in blokk
    assert ".rute.nivaa-bredest-2 > .styrke" not in blokk


def test_merket_og_teksten_staar_fortsatt_paa_nivaa_3():
    """Svaret kl. 19:21, 1: merket for en annen dag og teksten står som før.
    Ville feilet hvis klassen styrke-N også viste merket eller teksten på
    nivå 2."""
    for klasse in ("bredest", "bred", "smal", "smalest"):
        for element in (".merke", ".tekst"):
            assert f".rute.nivaa-{klasse}-2 > {element}" in STIL, (klasse, element)
        assert f"styrke-{klasse}) > .merke" not in STIL and f"styrke-{klasse}) > .tekst" not in STIL


def test_spoersmaalstegnet_staar_midt_paa_den_foerste_knappen():
    """Svaret kl. 19:21, 2: «?» foran periodeknappene står midt på høyden av
    knappene, på oversikten, i Min liste og i børsometeret, også ved 390 px,
    målt i Edge (spesifikasjonen 8.2b). Regnet med tallene i stil.css:
    midten av sirkelen, margin-top og halve klikkflaten, er midten av den
    første knappen. Ville feilet med «?» øverst i raden, som før (7 px for
    høyt), eller hvis periodevalget brøt til linja under «?» på smal skjerm."""
    knapp = _regel("nav.periodevalg a, nav.periodevalg button")
    knapphoeyde = int(re.search(r"min-height: (\d+)px", knapp).group(1))
    hjelp = _regel("button.hjelpeknapp")
    flate = int(re.search(r"(?<![-\w])height: (\d+)px", hjelp).group(1))
    hode = _regel(".periodehode > button.hjelpeknapp")
    topp = int(re.search(r"margin-top: (-?\d+)px", hode).group(1))
    assert topp + flate / 2 == knapphoeyde / 2, (topp, flate, knapphoeyde)
    assert "align-items: flex-start" in _regel(".periodehode")
    nav = _regel(".periodehode > nav.periodevalg")
    assert "flex: 1 1 0" in nav and "min-width: 0" in nav, nav
    # Gjennomgangen av rettingen (VG2): ingen annen regel, heller ikke i en
    # @media-blokk, gir raden en annen oppstilling.
    assert STIL.count(".periodehode") == 4


def test_aksjesiden_har_ingen_egen_spoersmaalstegn_for_periodene(klient):
    """Svaret kl. 19:21, 3 (gjennomgangen, VG3): «?» ved «Kursutvikling»
    forklarer både grafen og periodene. Ville feilet med en egen «?» for
    periodene på aksjesiden, eller uten «?» ved overskriften."""
    html = _html(klient, "/aksje/BRFE")
    assert 'class="periodehode"' not in html and 'popovertarget="hjelp-perioden"' not in html
    overskrift = re.search(r"<h2 id=\"[^\"]*\">Kursutvikling.*?</h2>", html, re.S).group(0)
    assert 'popovertarget="hjelp-graf"' in overskrift, overskrift


def test_klassen_for_styrken_bare_paa_ruter_med_styrke(klient):
    """Gjennomgangen av rettingen 04.11 (ECH5): ville feilet hvis en rute uten
    linja for styrken fikk klassen styrke-N. Rettet 05.11 (gruppens svar
    04.11 kl. 20:53 og 20:56, 2): en rute med kurs, men uten styrke, har
    «ikke vurdert» på linja og kan få klassen; en rute med «Uten data» har
    ingen linje og får den aldri (gjennomgangen av svar 2, BH1)."""
    for adresse in ("/boersometer", "/boersometer?periode=velg&dag=2026-10-01"):
        ruter = _ruter(_html(klient, adresse))
        for symbol, rute in ruter.items():
            if not re.search(r'<span class="styrke[^"]*">(\d av 3|ikke vurdert)</span>', rute):
                assert "styrke-" not in rute, (adresse, symbol)
        assert any("styrke-" in r for r in ruter.values())


# --- Gruppens svar 04.11 kl. 20:53 og 20:56 -----------------------------------


def test_styrkelinje_en_annen_dag_med_gul_ramme():
    """Svar 1: en annen dag viser en rute med gul ramme styrken bare når
    merket «3 av 3 siste børsdag» også får plass, og merket står bare på
    nivå 3. Ville feilet hvis en gul rute en annen dag fikk styrken på nivå 2,
    eller hvis siste børsdag og ruter uten gul ramme mistet den."""
    from boersometer import Rute, styrkelinje
    from kursdata import Aksje

    aksje = Aksje("KVST", "KVST.OL", "Kvist", "Industri")
    annen_dag = Rute(aksje, 1.0, 1.0, 1, None, siste_styrke=3, er_siste=False)
    assert annen_dag.ramme == "gul"
    assert not styrkelinje(annen_dag, 125, 105)
    assert styrkelinje(Rute(aksje, 1.0, 1.0, 3, None, siste_styrke=3), 125, 105)
    assert styrkelinje(Rute(aksje, 1.0, 1.0, 1, None, siste_styrke=2, er_siste=False), 125, 105)
    assert not styrkelinje(Rute(aksje, 1.0, 1.0, 3, None, siste_styrke=3), 80, 105)


def test_styrkelinje_uten_styrke_og_uten_data():
    """Svar 2 (gjennomgangen, VG2 og VG4): en rute uten styrke har sin egen
    grense, IKKE_VURDERT_PLASS, og en rute uten data har ingen linje. Ville
    feilet hvis «ikke vurdert» brukte grensen for styrken (90 × 80 er nok for
    «3 av 3», ikke for «ikke vurdert»), eller hvis en rute uten data fikk
    linja."""
    from boersometer import Rute, styrkelinje
    from kursdata import Aksje

    aksje = Aksje("VRDS", "VRDS.OL", "Varde", "Industri")
    uten_styrke = Rute(aksje, 1.0, None, None, "signalet kunne ikke regnes")
    assert uten_styrke.uten_styrke == "ikke vurdert"
    assert not styrkelinje(uten_styrke, 90, 80)
    assert styrkelinje(uten_styrke, 104, 69)
    assert styrkelinje(Rute(aksje, 1.0, 1.0, 1, None), 90, 80)
    uten_data = Rute(aksje, None, None, None, "Uten data", uten_data=True)
    assert uten_data.uten_styrke is None and not styrkelinje(uten_data, 200, 200)
    # Spørsmål til gruppen (gjennomgangen, VG3 og ECH4): en annen dag gjelder
    # svar 1 også «ikke vurdert» i en gul rute, så linja står der på nivå 3,
    # med merket.
    gul = Rute(aksje, 1.0, None, None, "ikke vurdert", siste_styrke=3, er_siste=False)
    assert not styrkelinje(gul, 110, 80)


def test_gul_rute_en_annen_dag_uten_plass_til_merket_viser_ikke_styrken(klient):
    """Svar 1, i demoen 21.09: KVST har gul ramme og står på nivå 2 ved
    1280 px. Før svaret fikk den styrke-bredest, så styrken sto uten merket.
    Ville feilet hvis en gul rute en annen dag fikk styrke-N der den står på
    nivå 2, eller hvis styrken og merket ikke sto i ruta for skjermleseren."""
    ruter = _ruter(_html(klient, "/boersometer?periode=velg&dag=2026-09-21"))
    paa_nivaa_2 = 0
    for symbol, rute in ruter.items():
        klasser = re.search(r'<a class="rute ([^"]*)"', rute).group(1).split()
        if "ramme-gul" not in klasser:
            continue
        assert re.search(r'<span class="styrke">\d av 3</span>', rute), symbol
        assert "3 av 3 siste børsdag" in rute, symbol
        for klasse in ("bredest", "bred", "smal", "smalest"):
            if f"nivaa-{klasse}-2" in klasser:
                paa_nivaa_2 += 1
                assert f"styrke-{klasse}" not in klasser, (symbol, klasse)
    klasser = re.search(r'<a class="rute ([^"]*)"', ruter["KVST"]).group(1).split()
    assert "ramme-gul" in klasser and "nivaa-bredest-2" in klasser, klasser
    assert paa_nivaa_2 >= 4, paa_nivaa_2


def test_vrds_viser_ikke_vurdert_ved_1280_px(klient):
    """Svar 2: VRDS i demoen har kurs, men ingen styrke. Story 8.20b (U97):
    med to linjer i bransjeoverskriften er feltet lavere, og VRDS har plass
    til «ikke vurdert» på nivå 2 i den smale flaten, ikke lenger ved 1280 px.
    Ville feilet uten «ikke vurdert» på linja der styrken ellers står, eller
    uten klassen som lar linja stå på nivå 2."""
    html = _html(klient, "/boersometer")
    klasser, rute = re.search(
        r'<a class="rute ([^"]*)"[^>]*>\s*<span class="ticker">VRDS</span>(.*?)</a>', html, re.S
    ).groups()
    assert "nivaa-smal-2" in klasser.split() and "styrke-smal" in klasser.split(), klasser
    assert re.search(
        r'<span class="endring">[^<]*</span>\s*<span class="skjult">, </span>'
        r'<span class="styrke ikke-vurdert">ikke vurdert</span>',
        rute,
    ), rute
    # Grunnen står under, som før, og vises på nivå 3.
    assert '<span class="tekst">for kort historikk:' in rute


def test_grensen_for_ikke_vurdert_er_regnet_fra_stilen():
    """Svar 2: grensen for «ikke vurdert» er regnet for 14 px som STYRKE: den
    gule rammen, luften, symbolet, endringen og teksten, uten ring, med
    0,5 em per tegn. I Edge er «ikke vurdert» 74,83 px, 0,45 em per tegn
    (spesifikasjonen 8.2b). Ville feilet med en grense der teksten kunne
    kuttes, med en annen skrift enn ruta, eller med en grense som ikke er
    lavere enn nivå 3."""
    from boersometer import IKKE_VURDERT_PLASS, NIVAA_3
    from markedsoversikt import IKKE_VURDERT

    rute = re.search(r"side-oversikt\) \.rute \{([^}]*)\}", STIL).group(1)
    skrift = int(re.search(r"font-size: (\d+)px", rute).group(1))
    linje = skrift * float(re.search(r"line-height: ([\d.]+)", rute).group(1))
    gap = int(re.search(r"gap: (\d+)px", rute).group(1))
    luft = [int(v) for v in re.search(r"padding: (\d+)px (\d+)px", rute).groups()]
    ramme = int(
        re.search(r"border: (\d+)px solid", _regel(".rute.ramme-gul, :where(.side-oversikt) .proeve.ramme-gul")).group(
            1
        )
    )
    assert int(re.search(r"font-size: (\d+)px", _regel(".rute .styrke")).group(1)) == skrift
    linja = _regel(".rute .styrke.ikke-vurdert")
    assert "font-size" not in linja and "padding" not in linja and "border" not in linja, linja
    hoeyde = 2 * ramme + 2 * luft[0] + 3 * linje + 2 * gap
    bredde = 2 * ramme + 2 * luft[1] + 0.5 * skrift * len(IKKE_VURDERT)
    assert IKKE_VURDERT_PLASS[1] >= hoeyde and IKKE_VURDERT_PLASS[0] >= bredde, (IKKE_VURDERT_PLASS, hoeyde, bredde)
    assert IKKE_VURDERT_PLASS[0] < NIVAA_3[0] and IKKE_VURDERT_PLASS[1] < NIVAA_3[1]


@pytest.mark.parametrize(
    ("b", "h", "ventet"),
    [(104, 69, True), (103, 69, False), (104, 68, False), (125, 105, True)],
)
def test_ikke_vurdert_plass(b, h, ventet):
    """Svar 2. Ville feilet hvis grensen ikke var IKKE_VURDERT_PLASS, (104, 69)."""
    from boersometer import ikke_vurdert_plass

    assert ikke_vurdert_plass(b, h) is ventet


@pytest.mark.parametrize(
    "adresse",
    [
        "/boersometer",
        "/boersometer?periode=velg&dag=2026-10-01",
        "/boersometer?periode=velg&dag=2026-09-18",
        "/boersometer?periode=1-uke",
    ],
)
def test_ikke_vurdert_staar_en_gang_og_uten_data_er_som_foer(klient, adresse):
    """Svar 2: en rute med kurs, men uten styrke, har «ikke vurdert» på linja
    for styrken én gang, også en dag der grunnen er «ikke vurdert» (18.09,
    før vurderingene starter). En rute uten data er som før. Ville feilet med
    «ikke vurdert» to ganger i ruta, uten linja, eller med linja eller
    styrke-N i en rute uten data."""
    ruter = _ruter(_html(klient, adresse))
    assert len(ruter) == 15
    uten_styrke = 0
    for symbol, rute in ruter.items():
        # Story 8.23 (A4): lappen (title) gjentar styrken; testen teller teksten i ruta.
        rute = re.sub(r' title="[^"]*"', "", rute)
        if "uten-data" in re.search(r'<a class="rute ([^"]*)"', rute).group(1).split():
            assert "ikke vurdert" not in rute and "styrke" not in rute, (adresse, symbol)
            assert '<span class="endring">Uten data</span>' in rute
            continue
        if re.search(r'<span class="styrke[^"]*">\d av 3</span>', rute):
            assert "ikke vurdert" not in rute, (adresse, symbol)
            continue
        uten_styrke += 1
        assert rute.count("ikke vurdert") == 1, (adresse, symbol)
        assert '<span class="styrke ikke-vurdert">ikke vurdert</span>' in rute, (adresse, symbol)
    assert uten_styrke >= 1
    if adresse.endswith("2026-09-18"):
        assert uten_styrke == 14


def test_grunnplass_er_regnet_fra_stilen():
    """Gjennomgangen av svar 2 (ECH1): tallene grunnplass regner med, er de i
    stil.css. Ville feilet hvis skriften, linjehøyden, mellomrommet, luften
    eller rammen i ruta ble endret uten grunnplass."""
    import boersometer

    rute = re.search(r"side-oversikt\) \.rute \{([^}]*)\}", STIL).group(1)
    assert int(re.search(r"font-size: (\d+)px", rute).group(1)) == boersometer.RUTESKRIFT
    assert float(re.search(r"line-height: ([\d.]+)", rute).group(1)) == boersometer.RUTELINJE
    assert int(re.search(r"gap: (\d+)px", rute).group(1)) == boersometer.RUTEGAP
    luft = tuple(int(v) for v in re.search(r"padding: (\d+)px (\d+)px", rute).groups())
    assert luft == boersometer.RUTELUFT
    gul = _regel(".rute.ramme-gul, :where(.side-oversikt) .proeve.ramme-gul")
    assert int(re.search(r"border: (\d+)px solid", gul).group(1)) == boersometer.RUTERAMME
    assert int(re.search(r"font-size: (\d+)px", _regel(".rute .tekst")).group(1)) == boersometer.RUTESKRIFT


@pytest.mark.parametrize(
    ("tekst", "bredde", "ventet"),
    [("hentingen feilet", 200, 1), ("hentingen feilet", 100, 2), ("for kort historikk: 24 av 51 dager", 112, 3)],
)
def test_linjer(tekst, bredde, ventet):
    """Gjennomgangen av svar 2 (ECH1): ord for ord, 7 px per tegn. Ville
    feilet hvis teksten ble regnet uten å brytes, eller midt i et ord."""
    from boersometer import _linjer

    assert _linjer(tekst, bredde) == ventet


def test_grunnplass():
    """Gjennomgangen av svar 2 (ECH1): en gul rute en annen dag uten styrke,
    med «hentingen feilet», har symbolet, endringen, «ikke vurdert», merket
    på to linjer og grunnen: 8 + 8 + 6 × 16,8 + 5 = 121,8 px. Ved 126 × 106,
    den minste ruta på nivå 3, ble grunnen kuttet. Ville feilet hvis grunnen
    sto der den ikke får plass, eller manglet der den gjør det."""
    from boersometer import Rute, grunnplass
    from kursdata import Aksje

    aksje = Aksje("VRDS", "VRDS.OL", "Varde", "Industri")
    gul = Rute(aksje, 1.0, None, None, "hentingen feilet", siste_styrke=3, er_siste=False)
    assert gul.grunn == "hentingen feilet"
    assert not grunnplass(gul, 126, 106)
    assert not grunnplass(gul, 300, 121)
    assert grunnplass(gul, 300, 122)
    vanlig = Rute(aksje, 1.0, None, None, "for kort historikk: 24 av 51 dager")
    assert grunnplass(vanlig, 132, 199)
    assert not grunnplass(Rute(aksje, 1.0, None, None, "ikke vurdert"), 300, 300)


def test_grunnen_staar_paa_nivaa_3_bare_med_plass(klient):
    """Gjennomgangen av svar 2 (ECH1): på nivå 3 skjuler stilen grunnen for
    øyet uten klassen grunn-N, i alle fire spennene. VRDS 01.10 er 132 × 199 px
    ved 1280 px og har plass. Story 8.20b (U97): med to linjer i
    bransjeoverskriften står VRDS ikke lenger på nivå 3. Ville feilet uten
    regelen, eller hvis ingen rute med grunn på nivå 3 hadde plass til den."""
    for klasse in ("bredest", "bred", "smal", "smalest"):
        assert f".rute.nivaa-{klasse}-3:not(.grunn-{klasse}) > .tekst" in STIL, klasse
    # Story 8.20b (U97): VRDS 01.10 står ikke lenger på nivå 3, så testen
    # leter etter en rute med grunn på nivå 3 en av de første dagene i demoen.
    med_grunn = []
    for dag in ("2026-09-21", "2026-09-22", "2026-09-23", "2026-10-01"):
        html = _html(klient, f"/boersometer?periode=velg&dag={dag}")
        for klasser in re.findall(r'<a class="rute ([^"]*)"[^>]*>(?:(?!</a>).)*<span class="tekst">', html, re.S):
            klasser = klasser.split()
            nivaa_3 = [k[6:-2] for k in klasser if k.startswith("nivaa-") and k.endswith("-3")]
            med_grunn += [f"grunn-{klasse}" in klasser for klasse in nivaa_3]
    assert med_grunn and any(med_grunn), med_grunn


# --- Gruppens svar 05.11 kl. 09:34 --------------------------------------------

ANNEN_GRUNN = "«Ikke vurdert» kan også ha en annen grunn, som for kort kurshistorikk."
GAMMEL_FOTNOTE = "«Ikke vurdert»: "


def _fotnoter(html: str) -> list[str]:
    return [re.sub(r"\s+", " ", f).strip() for f in re.findall(r'<p class="fotnote">(.*?)</p>', html, re.S)]


def test_annen_grunn_bare_for_en_rute_med_kurs_og_en_annen_grunn():
    """Svar 1: fotnoten står når en rute sier «ikke vurdert» av en annen
    grunn enn at signalet ikke er lagret. Ville feilet hvis en rute med
    styrke, en rute med «ikke vurdert» som grunn eller en rute uten data
    ga fotnoten, eller hvis en rute med for kort historikk ikke ga den."""
    from boersometer import Rute
    from kursdata import Aksje

    aksje = Aksje("VRDS", "VRDS.OL", "Varde", "Industri")
    assert Rute(aksje, 1.0, None, None, "for kort historikk: 24 av 51 dager").annen_grunn
    assert Rute(aksje, 1.0, None, None, "hentingen feilet", siste_styrke=3, er_siste=False).annen_grunn
    assert not Rute(aksje, 1.0, None, None, "ikke vurdert").annen_grunn
    assert not Rute(aksje, None, None, None, "Uten data", uten_data=True).annen_grunn
    assert not Rute(aksje, 1.0, 1.0, 2, None).annen_grunn
    assert not Rute(aksje, 1.0, None, None, None).annen_grunn
    # Gjennomgangen (VG3): en rute med styrke gir den ikke, heller ikke med en tekst.
    assert not Rute(aksje, 1.0, 1.0, 2, "for kort historikk: 24 av 51 dager").annen_grunn


def test_fotnoten_for_en_annen_grunn_staar_med_vrds_i_demoen(klient):
    """Svar 1: siste demodag har VRDS for kort historikk og ingen dag uten
    lagret signal. Ville feilet uten den nye fotnoten, hvis den gamle sto
    alene for VRDS, eller hvis fotnoten sto over kartet eller over tabellen
    (gjennomgangen, BH3)."""
    html = _html(klient, "/boersometer")
    assert '<span class="ticker">VRDS</span>' in html
    fotnoter = _fotnoter(html)
    assert any(f.startswith(ANNEN_GRUNN) and "Grunnen står i tabellen og på aksjesiden." in f for f in fotnoter), (
        fotnoter
    )
    assert not any(f.startswith(GAMMEL_FOTNOTE) for f in fotnoter), fotnoter
    assert html.index(ANNEN_GRUNN) > html.index('<span class="ticker">VRDS</span>')
    assert html.index(ANNEN_GRUNN) > html.index("</details>")


def test_fotnoten_for_en_annen_grunn_foelger_ruta_som_viser_det(klient):
    """Gjennomgangen (ECH1): VRDS viser «ikke vurdert» for øyet bare i én
    klasse, og fotnoten har bare den, og stilen skjuler den for øyet i de
    andre klassene, med de samme grensene som rutene. Story 8.20b (U97): med
    to linjer i bransjeoverskriften er det den smale flaten (styrke-smal),
    ikke lenger den bredeste. Ville feilet hvis fotnoten sto for øyet der
    VRDS bare viser symbolet, eller uten reglene i stil.css."""
    html = _html(klient, "/boersometer")
    klasser = re.search(r'<div class="annen-grunn([^"]*)">', html).group(1).split()
    vrds = re.search(r'<a class="rute ([^"]*)"[^>]*>\s*<span class="ticker">VRDS</span>', html).group(1).split()
    assert klasser == [f"vis-{k.removeprefix('styrke-')}" for k in vrds if k.startswith("styrke-")], (klasser, vrds)
    assert klasser == ["vis-smal"], klasser
    assert ":where(.side-oversikt) .annen-grunn { container-type: inline-size; }" in STIL
    for klasse in ("bredest", "bred", "smal", "smalest"):
        assert f":where(.side-oversikt) .annen-grunn:not(.vis-{klasse}) > .fotnote {{ position: absolute;" in STIL


def test_klassene_for_fotnoten_er_der_ruta_viser_ikke_vurdert():
    """Gjennomgangen (ECH1), mutanten N5: en rute med en annen grunn viser
    «ikke vurdert» for øyet på nivå 3, og på nivå 2 bare med plass til
    linja (styrke). Ville feilet hvis nivå 2 uten plass, eller nivå 0 og 1,
    ga klassen, eller hvis nivå 3 ikke ga den."""
    from boersometer import Bransje, Kart, Kartfelt, Kartrute, Rute, annen_grunn_i_kartet
    from kursdata import Aksje

    rute = Rute(Aksje("VRDS", "VRDS.OL", "Varde", "Industri"), 1.0, 1.0, None, "for kort historikk: 24 av 51 dager")
    nivaa = {"bredest": 3, "bred": 2, "smal": 2, "smalest": 1}
    kartrute = Kartrute(rute, 1.0, {}, nivaa, styrke=frozenset({"smal"}))
    felt = Kartfelt(Bransje("Industri", (rute,)), 1.0, {}, {}, (kartrute,))
    assert annen_grunn_i_kartet(Kart((felt,), {})) == frozenset({"bredest", "smal"})


def test_ingen_fotnote_for_en_annen_grunn_uten_en_slik_rute_i_kartet(klient):
    """Gjennomgangen (VG1, ECH1): 18.09 sier VRDS «ikke vurdert» fordi
    signalet ikke er lagret, så bare den gamle fotnoten står, og et tomt kart
    gir ingen fotnote. Ville feilet hvis den nye fotnoten sto på hver side,
    eller sto når kartet ikke kunne regnes."""
    from boersometer import Rute, annen_grunn_i_kartet, bygg_boersometer, kart
    from kursdata import Aksje

    html = _html(klient, "/boersometer?periode=velg&dag=2026-09-18")
    assert ANNEN_GRUNN not in html and 'class="annen-grunn' not in html
    assert any(f.startswith(GAMMEL_FOTNOTE) for f in _fotnoter(html))
    assert annen_grunn_i_kartet(kart([])) is None
    aksje = Aksje("VRDS", "VRDS.OL", "Varde", "Industri")
    med_grunn = kart(bygg_boersometer([Rute(aksje, 1.0, 1.0, None, "for kort historikk: 24 av 51 dager")]))
    assert annen_grunn_i_kartet(med_grunn) is not None


def test_begge_fotnotene_naar_begge_grunnene_finnes(klient, monkeypatch):
    """Svar 1: ingen dag i demoen har begge grunnene (skannet 05.11, 97
    dager), så VRDS 18.09, før vurderingene starter, får en annen grunn her.
    Ville feilet hvis den nye fotnoten tok plassen til den gamle, eller ikke
    sto rett etter den (gjennomgangen, BH4 og VG4)."""
    import boersometer

    monkeypatch.setattr(boersometer.Rute, "annen_grunn", property(lambda rute: rute.aksje.symbol == "VRDS"))
    html = _html(klient, "/boersometer?periode=velg&dag=2026-09-18")
    fotnoter = _fotnoter(html)
    assert [f[:16] for f in fotnoter] == [GAMMEL_FOTNOTE[:16], ANNEN_GRUNN[:16]], fotnoter
    mellom = html[html.index(GAMMEL_FOTNOTE) : html.index(ANNEN_GRUNN)]
    assert re.fullmatch(r'[^<]*</p>\s*<div class="annen-grunn[^"]*">\s*<p class="fotnote">', mellom), mellom


def test_hjelpen_og_hjelp_md_sier_det_samme_om_fotnoten():
    """Svar 1: docs/hjelp.md sier at «ikke vurdert» kan ha en annen grunn,
    at en fotnote under kartet sier det, og at grunnen står i tabellen og på
    aksjesiden, og også at begge fotnotene kan stå. Story 8.20b (U102):
    fotnoten står, og hjelpen ved «?» sier det ikke lenger. Ville feilet hvis
    hjelp.md manglet en av delene (gjennomgangen, VG2), eller vinduet
    gjentok fotnoten."""
    deler = ("som for kort kurshistorikk", "fotnote under kartet", "tabellen og på aksjesiden")
    vinduet = hjelpetekster()["boersometeret"].tekst + hjelpetekster()["boersometeret_ruta"].tekst
    assert not any(del_ in vinduet for del_ in deler), vinduet
    hjelp = (Path(__file__).resolve().parent.parent / "docs" / "hjelp.md").read_text(encoding="utf-8")
    avsnitt = hjelp.split("### Hvorfor står det «ikke vurdert»?")[1].split("\n#")[0]
    assert all(del_ in avsnitt for del_ in deler) and "står begge fotnotene" in avsnitt
    boersometer = hjelp.split("### Hva viser børsometeret?")[1].split("\n#")[0]
    assert all(del_ in boersometer for del_ in deler)
