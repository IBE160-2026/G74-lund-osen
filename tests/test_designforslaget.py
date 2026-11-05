"""Gruppens svar 04.11 kl. 22:23: fire ting som i designforslaget
(spesifikasjonen spec-8-2b-som-designforslaget.md). Designforslaget ligger
ikke i repoet, så tallene er de i svaret og i instruksjonen 05.11 kl. 11:50.

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


def _regel(velger: str) -> str:
    treff = re.search(r"(?:^|\n)\s*(?::where\(\.side-[a-z]+\) )?" + re.escape(velger) + r"\s*\{([^}]*)\}", STIL)
    assert treff, f"ingen regel for {velger}"
    return treff.group(1)


def _px(regel: str, egenskap: str) -> float:
    return float(re.search(egenskap + r": ([\d.]+)px", regel).group(1))


# --- Svar 1: store ruter i børsometeret ---------------------------------------

KLASSENE = ("bredest", "bred", "smal", "smalest")


def test_grensen_for_store_ruter_er_regnet_fra_stilen():
    """Svar 1: STOR er regnet som NIVAA_3 og STYRKE, med tallene i stil.css:
    rammen, luften 10 og 12 px, symbolet 22 px, navnet 12,5 px og endringen
    28 px, og i bredden AKRBP med «ikke vurdert» ved siden av og «Uten data» i
    28 px. Ville feilet med en grense der symbolet, styrken eller endringen
    kunne gå utenfor ruta, eller hvis stilen fikk andre tall enn koden."""
    import boersometer as b

    for klasse in KLASSENE:
        stor = _regel(f".rute.nivaa-{klasse}-4")
        assert tuple(int(v) for v in re.search(r"padding: (\d+)px (\d+)px", stor).groups()) == b.STORLUFT
        assert re.search(r"gap: 0 (\d+)px", stor).group(1) == str(b.STORMELLOM)
        assert _px(_regel(f".rute.nivaa-{klasse}-4 > .ticker"), "font-size") == b.STORSYMBOL
        assert _px(_regel(f".rute.nivaa-{klasse}-4 > .endring"), "font-size") == b.STORENDRING
    navn = _regel(".rute .navn")
    assert _px(navn, "font-size") == b.STORNAVN and _px(navn, "margin-top") == b.STORGAP
    rute = re.search(r"side-oversikt\) \.rute \{([^}]*)\}", STIL).group(1)
    linje = float(re.search(r"line-height: ([\d.]+)", rute).group(1))
    ramme = int(
        re.search(r"border: (\d+)px solid", _regel(".rute.ramme-gul, :where(.side-oversikt) .proeve.ramme-gul")).group(
            1
        )
    )
    luft_h, luft_b = b.STORLUFT
    hoeyde = 2 * ramme + 2 * luft_h + (b.STORSYMBOL + b.STORNAVN + b.STORENDRING) * linje + b.STORGAP
    halvfet = 0.62
    topp = 2 * ramme + 2 * luft_b + halvfet * b.STORSYMBOL * len("AKRBP") + b.STORMELLOM
    topp += b.EM_PER_TEGN * b.RUTESKRIFT * len("ikke vurdert")
    bunn = 2 * ramme + 2 * luft_b + halvfet * b.STORENDRING * len("Uten data")
    assert b.STOR[1] >= hoeyde and b.STOR[0] >= max(topp, bunn), (b.STOR, hoeyde, topp, bunn)
    assert b.STOR[0] > b.NIVAA_3[0] and b.STOR[1] >= b.NIVAA_3[1]


@pytest.mark.parametrize(("b", "h", "ventet"), [(193, 107, True), (192, 107, False), (193, 106, False)])
def test_storplass(b, h, ventet):
    """Svar 1. Ville feilet hvis grensen ikke var STOR, (193, 107)."""
    from boersometer import storplass

    assert storplass(b, h) is ventet


def _rute(**kw):
    from boersometer import Rute
    from kursdata import Aksje

    verdier = {"aksje": Aksje("LKSV", "LKSV.OL", "Laksevik Sjømat", "Sjømat"), "endring": -2.26, "volumforhold": 1.0}
    verdier |= {"styrke": None, "tekst": None}
    return Rute(**(verdier | kw))


def test_merket_og_grunnen_der_de_faar_plass():
    """Svar 1: merket og grunnen står mellom navnet og endringen der de får
    plass, merket først. En annen dag står styrken i en gul rute bare med
    merket (svaret 04.11 kl. 20:53 og 20:56, 1). Ville feilet hvis merket
    eller grunnen sto i en rute uten plass, eller styrken uten merket."""
    from boersometer import STOR, Flate, _nivaa_ved

    flate = Flate("prove", 100, 1, 100, (("prove", 100),))
    gul = _rute(styrke=1, siste_styrke=3, er_siste=False)
    # Bare plass til grunnoppsettet: verken merket eller styrken.
    assert _nivaa_ved(flate, 100, STOR[0] + 4, STOR[1] + 4, gul) == (4, False, False, False)
    # Plass til merket på to linjer (16,8 px hver og 2 px over).
    assert _nivaa_ved(flate, 100, STOR[0] + 4, STOR[1] + 4 + 36, gul) == (4, True, False, True)
    # Siste børsdag trenger ikke merket.
    siste = _rute(styrke=3, siste_styrke=3)
    assert _nivaa_ved(flate, 100, STOR[0] + 4, STOR[1] + 4, siste) == (4, True, False, False)


def test_en_stor_rute_i_demoen(klient):
    """Svar 1: i demoen er KVST stor ved 1280 px, siste børsdag, målt i
    Edge. Navnet står i ruta for øyet og er skjult for skjermleseren, som
    leser det i linja under. Ville feilet uten nivå 4, uten navnet eller med
    navnet to ganger for skjermleseren."""
    html = _html(klient, "/boersometer")
    klasser, innhold = re.search(
        r'<a class="rute ([^"]*)"[^>]*>\s*<span class="ticker">KVST</span>(.*?)</a>', html, re.S
    ).groups()
    assert "nivaa-bredest-4" in klasser.split(), klasser
    assert '<span class="navn" aria-hidden="true">Kvitstein Mineral</span>' in innhold
    assert innhold.count("Kvitstein Mineral") == 2


def test_store_ruter_i_stilen():
    """Svar 1: nivå 4 er et rutenett med symbolet og styrken øverst, navnet
    under, merket og grunnen og endringen nederst, i hver av de fire
    klassene. Navnet er skjult ellers, så små ruter er som før, og kuttes
    med «…». Ville feilet hvis navnet sto i små ruter, ikke ble kuttet, eller
    endringen ikke sto nederst."""
    assert "display: none" in _regel(".rute .navn")
    navn = _regel(".rute .navn")
    assert "text-overflow: ellipsis" in navn and "white-space: nowrap" in navn and "overflow: hidden" in navn
    for klasse in KLASSENE:
        stor = _regel(f".rute.nivaa-{klasse}-4")
        assert '"ticker styrke" "navn navn" "merke merke" "tekst tekst" "endring endring"' in stor
        assert "align-self: end" in _regel(f".rute.nivaa-{klasse}-4 > .endring")
        assert "font-weight: 600" in _regel(f".rute.nivaa-{klasse}-4 > .ticker")
        skjul = re.search(
            re.escape(f".rute.nivaa-{klasse}-4:not(.styrke-{klasse}) > .styrke") + r"[^{]*\{([^}]*)\}", STIL
        )
        assert skjul and "clip: rect(0 0 0 0)" in skjul.group(1)
        assert f".rute.nivaa-{klasse}-4:not(.merke-{klasse}) > .merke" in STIL
        assert f".rute.nivaa-{klasse}-4:not(.grunn-{klasse}) > .tekst" in STIL


# --- Svar 2: lenken til børsometeret under søylene ----------------------------


def _soeylefot(html: str) -> str:
    return html.split('<div class="soeylefot">', 1)[1].split("</div>", 1)[0]


@pytest.mark.parametrize(
    ("oversikt", "boersometer"),
    [
        ("/", "/boersometer?periode=siste"),
        ("/?periode=1-mnd", "/boersometer?periode=1-mnd"),
        ("/?periode=velg&dag=2026-10-05", "/boersometer?periode=velg&amp;dag=2026-10-05"),
    ],
)
def test_lenken_til_boersometeret_har_samme_periode(klient, oversikt, boersometer):
    """Svar 2: under søylene, til høyre for «Stiplet linje: hovedindeksen»,
    står «Se perioden i Børsometer ›» med samme periode eller dag. Ville
    feilet uten lenken, med lenken foran forklaringen, eller med en annen
    periode eller dag i adressen."""
    fot = _soeylefot(_html(klient, oversikt))
    lenke = f'<a class="til-boersometer" href="{boersometer}">Se perioden i Børsometer <span aria-hidden="true">›</span></a>'
    assert lenke in fot, fot
    assert fot.index("Stiplet linje: hovedindeksen") < fot.index(lenke)


@pytest.mark.parametrize(
    ("oversikt", "ventet"),
    [
        ("/?periode=1-mnd", 'href="/boersometer?periode=1-mnd" aria-current="true"'),
        ("/?periode=velg&dag=2026-10-05", "mandag 05.10"),
    ],
)
def test_lenken_aapner_boersometeret_med_samme_periode(klient, oversikt, ventet):
    """Svar 2: lenken åpner børsometeret med perioden eller dagen fra
    oversikten. Ville feilet hvis børsometeret viste siste børsdag i stedet."""
    adresse = re.search(r'class="til-boersometer" href="([^"]+)"', _html(klient, oversikt)).group(1)
    assert ventet in _html(klient, adresse.replace("&amp;", "&"))


def test_lenken_er_halvfet():
    """Svar 2: lenken står i halvfet skrift, til høyre. Ville feilet med
    vanlig skrift eller uten margin-left: auto."""
    regel = _regel(".soeyler .soeylefot .til-boersometer")
    assert "font-weight: 600" in regel and "auto" in regel
    assert "justify-content: space-between" in _regel(".soeyler .soeylefot")


# --- Svar 3: «<navnet> kort fortalt» på aksjesiden ----------------------------


def test_ki_delen_heter_navnet_kort_fortalt(klient):
    """Svar 3: overskriften er «<navnet> kort fortalt» med «?», og «Laget av
    KI» står som før. Ville feilet med «Med KI-ens ord», uten navnet, uten
    «?» eller uten merket."""
    html = _html(klient, "/aksje/BRFE")
    ki = html.split('<section class="ki"', 1)[1].split("</section>", 1)[0]
    assert 'aria-labelledby="ki-tittel"' in ki.split(">", 1)[0]
    tittel = ki.split("<h2>", 1)[1].split("</h2>", 1)[0]
    assert tittel.startswith('<span id="ki-tittel">Brattfjell Energi kort fortalt</span> ')
    assert 'popovertarget="hjelp-ki"' in tittel
    assert '<p class="merke-ki">Laget av KI · ' in ki
    assert "Med KI-ens ord" not in html
    assert 'id="hjelp-ki"' in html


def test_overskriften_er_i_newsreader():
    """Svar 3: overskriften står i Newsreader, som de andre. Ville feilet
    hvis KI-delen fikk en annen skrift."""
    assert re.search(r'(?:^|\n)h1, h2 \{ font-family: "Newsreader"', STIL)
    assert "font-family" not in _regel(".ki h2")


def test_hjelpen_ved_ki_delen():
    """Svar 3: hjelpen sier hva teksten er, hva modellen fikk, slått opp i
    ki_grunnlag.py, at tallene med prikket strek er sjekket, og at den ikke
    gir råd. Ville feilet hvis en av de fire delene manglet, eller hjelpen
    sa at modellen fikk kurser."""
    from hjelpetekster import KI_GRUNNLAG, hjelpetekster

    tekst = hjelpetekster()["ki_kort_fortalt"]
    for del_ in ("skrevet av en språkmodell", "«Laget av KI»", "Modellen fikk bare", "prikket strek er sjekket"):
        assert del_ in tekst.tekst, del_
    assert "gir ikke råd" in tekst.tekst and "ingen kurser, prosenter eller volumer" in tekst.tekst
    assert any(fil == KI_GRUNNLAG for fil, _ in tekst.kilder)
    hjelp = (Path(__file__).resolve().parent.parent / "docs" / "hjelp.md").read_text(encoding="utf-8")
    avsnitt = hjelp.split("### Hva er «kort fortalt» på aksjesiden?")[1].split("\n#")[0]
    assert "prikket strek er sjekket" in avsnitt and "gir ikke råd" in avsnitt


# --- Svar 4: ikonene i menyknappene -------------------------------------------


@pytest.mark.parametrize(
    ("sti", "navn", "del_"),
    [
        ("/", "Markedsoversikt", '<rect x="2" y="2.5" width="12" height="11" rx="1.5"/>'),
        ("/", "Børsometer", '<path d="M2 12a6 6 0 0 1 12 0"/><path d="M8 12l3-4"/>'),
        ("/", "Min liste", '<path d="M8 1.8l1.9 4'),
        ("/boersometer", "Børsometer", '<path d="M2 12a6 6 0 0 1 12 0"/>'),
    ],
)
def test_hver_menyknapp_har_sitt_ikon(klient, sti, navn, del_):
    """Svar 4: en tabell, en måler (halvsirkel med viser) og en stjerne, foran
    navnet og skjult for skjermleseren, på alle sidene. Ville feilet uten
    ikonet, med ikonet i feil knapp eller med ikonet synlig for skjermleseren."""
    meny = _html(klient, sti).split('<nav class="rad sider"', 1)[1].split("</nav>", 1)[0]
    knapp = re.search(r'<a class="sideknapp"[^>]*>(<svg class="ikon"[^>]*>.*?</svg>)' + navn + "</a>", meny)
    assert knapp, navn
    assert 'aria-hidden="true" focusable="false"' in knapp.group(1) and del_ in knapp.group(1)
    assert len(re.findall(r'<svg class="ikon"', meny)) == 3


def test_ikonene_er_16_px_med_strek_2_i_tekstfargen():
    """Svar 4: 16 px med strek 2 i tekstfargen. Ville feilet med en annen
    størrelse, en annen strek eller en fast farge, som ikke følger knappen
    som er valgt."""
    regel = _regel("header.stripe a.sideknapp .ikon")
    for del_ in ("width: 16px", "height: 16px", "stroke: currentColor", "stroke-width: 2", "fill: none"):
        assert del_ in regel, del_
