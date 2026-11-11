"""Story 3.4h: investorsidene i demoen, og boblen nederst på aksjesiden.

Etter spec-3-4h-investorsidene-i-demoen.md, med svaret 07.11 kl. 10:33 (alle
ti forslagene godtatt), svaret kl. 08:57 under story 3.4h i epics.md og
docs/bilder/investorsider/LESMEG.md. Ingen test går på nett: sidene lages med
testklienten, basen ligger i tmp_path (conftest.py), og nettleseren får
ingenting utenfra (test_hjelpefeltet.py).
"""

import hashlib
import os
import re
import struct
import zlib
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import pytest

import demo
import investorsider
import lagring_sqlite
from dokumentene import installasjonen
from investorsider import BREDDE, HOYDE, SKRIFTER, Skrift
from kursdata import AKSJEUNIVERS, INVESTORSIDER
from lagring_sqlite import SqliteKurslager, aapne_base
from test_hjelpefeltet import NETTLESER, _kjoer
from test_investorsiden import RADENE, demoklient, demomal, ekte_base, fast_klokke, klient  # noqa: F401

ROT = Path(__file__).resolve().parent.parent
GODKJENT = ROT / "docs" / "bilder" / "investorsider"
KOPIENE = ROT / "src" / "static" / "investorsider"
FONTS = ROT / "src" / "static" / "fonts"
STIL = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
KILDER = (ROT / "docs" / "kilder-og-rettigheter.md").read_text(encoding="utf-8")
NEDERST = (
    "Oppdiktet selskap i demoen. I den ekte versjonen åpner lenken på aksjesiden "
    "selskapets egen investorside i en ny fane."
)
# Del D: snittene i tabellen i LESMEG.md, med familien og stilen @font-face
# gir dem. IBM Plex Sans og Newsreader fantes fra før.
NYE_SKRIFTFILER = {
    "inter-display/InterDisplay-ExtraLight.woff": ("Inter Display", 200, "normal"),
    "inter-display/InterDisplay-Bold.woff": ("Inter Display", 700, "normal"),
    "inter-display/InterDisplay-ExtraBoldItalic.woff": ("Inter Display", 800, "italic"),
    "inter-display/InterDisplay-Black.woff": ("Inter Display", 900, "normal"),
    "lora/Lora-Regular.woff": ("Lora", 400, "normal"),
    "lora/Lora-Medium.woff": ("Lora", 500, "normal"),
    "lora/Lora-SemiBoldItalic.woff": ("Lora", 600, "italic"),
    "lora/Lora-Bold.woff": ("Lora", 700, "normal"),
    "liberation-mono/LiberationMono-Regular.woff": ("Liberation Mono", 400, "normal"),
    "liberation-mono/LiberationMono-Bold.woff": ("Liberation Mono", 700, "normal"),
}
# Snittene som fantes i appen før 3.4h (spesifikasjonen, «Slått opp»).
FANTES = {
    ("IBM Plex Sans", 400),
    ("IBM Plex Sans", 500),
    ("IBM Plex Sans", 600),
    ("Newsreader", 600),
    ("Newsreader 72", 500),
}


class _Side(HTMLParser):
    """Teksten i hvert element med en av klassene, og attributtene."""

    KLASSER = ("tilbake", "boble", "ki-merke", "oppdiktet", "investorboble", "skjult", "pil")

    def __init__(self):
        super().__init__()
        self.stakk: list[tuple[str, set[str]]] = []
        self.tekst: dict[str, str] = {}
        self.attr: dict[str, dict] = {}
        self.h1 = ""
        self.lenker: list[dict] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        klasser = set((a.get("class") or "").split())
        if tag == "a":
            self.lenker.append(a)
        for k in klasser & set(self.KLASSER):
            self.attr.setdefault(k, a)
            self.tekst.setdefault(k, "")
        if tag == "img":
            self.attr.setdefault("img", a)
        if tag not in (
            "img",
            "polygon",
            "polyline",
            "ellipse",
            "path",
            "circle",
            "rect",
            "meta",
            "link",
            "input",
            "br",
        ):
            self.stakk.append((tag, klasser))

    def handle_endtag(self, tag):
        while self.stakk:
            t, _ = self.stakk.pop()
            if t == tag:
                break

    def handle_data(self, data):
        for _, klasser in self.stakk:
            for k in klasser & set(self.KLASSER):
                self.tekst[k] += data
        if any(t == "h1" for t, _ in self.stakk):
            self.h1 += data


def _les(html: str) -> _Side:
    p = _Side()
    p.feed(html)
    return p


def _ren(tekst: str) -> str:
    return " ".join(tekst.split())


def _hoved(html: str) -> str:
    return html.split("<main>", 1)[1].split("</main>", 1)[0]


# --- A og B: siden for hvert av de 15, og ruta ----------------------------


@pytest.mark.parametrize("aksje", demo.DEMOUNIVERS, ids=lambda a: a.symbol)
def test_hvert_av_de_15_har_sin_side_i_demoen(demoklient, aksje):  # noqa: F811
    """Del A. Ville feilet hvis en av de 15 manglet en side, lenken tilbake
    manglet eller gikk til en annen aksje, navnet sto med små bokstaver i
    HTML-en, tegningen var en annen fil eller manglet alt, KI-merket eller
    teksten nederst manglet, eller siden ikke hadde stripa med
    «Eksempeltall»."""
    svar = demoklient.get(f"/investorside/{aksje.symbol}")
    assert svar.status_code == 200, aksje.symbol
    html = svar.get_data(as_text=True)
    side = _les(html)
    assert side.attr["tilbake"]["href"] == f"/aksje/{aksje.symbol}"
    assert _ren(side.tekst["tilbake"]) == f"Tilbake til {aksje.navn}"
    assert _ren(side.h1) == aksje.navn and aksje.navn[0].isupper()
    assert side.attr["img"]["src"] == f"/static/investorsider/{aksje.symbol.lower()}.svg"
    desc = re.search(
        r"<desc[^>]*>(.*?)</desc>", (KOPIENE / f"{aksje.symbol.lower()}.svg").read_text(encoding="utf-8"), re.S
    )
    assert side.attr["img"]["alt"] == _ren(desc.group(1)) != ""
    assert _ren(side.tekst["ki-merke"]) == "Illustrasjon laget av KI"
    assert _ren(side.tekst["oppdiktet"]) == NEDERST
    assert f"{aksje.sektor} · Demo Børs" in html
    assert "Eksempeltall" in html


def test_ruta_svarer_404_i_den_ekte_versjonen(klient, ekte_base):  # noqa: F811
    """Del B, spørsmål 1. Ville feilet hvis ruta svarte 200 i den ekte
    versjonen, for et demoselskap eller en ekte aksje."""
    for symbol in [a.symbol for a in demo.DEMOUNIVERS] + [a.symbol for a in AKSJEUNIVERS]:
        assert klient.get(f"/investorside/{symbol}").status_code == 404, symbol


def test_en_ukjent_ticker_gir_ingen_side(demoklient):  # noqa: F811
    """Del B. Ville feilet hvis et symbol utenfor de 15, en ekte aksje i
    demoen eller en ticker med .OL ga en side."""
    for symbol in ("FINNESIKKE", "EQNR", "BRFE.OL", "BRF"):
        assert demoklient.get(f"/investorside/{symbol}").status_code == 404, symbol
    # Symbolet leses som i aksjesiden, med store bokstaver.
    assert demoklient.get("/investorside/brfe").status_code == 200


def test_ingen_kurs_prosent_eller_kjoep_og_salg(demoklient):  # noqa: F811
    """NFR-06. Ville feilet hvis siden for et selskap viste en kurs, en
    prosent, et signal eller et ord om kjøp eller salg."""
    for aksje in demo.DEMOUNIVERS:
        hoved = _hoved(demoklient.get(f"/investorside/{aksje.symbol}").get_data(as_text=True))
        tekst = _ren(re.sub(r"<[^>]+>", " ", hoved)).lower()
        # Slagordet til JGRD er «Laster … 99 % grønt.», godkjent 24.10.
        tekst = tekst.replace("99 % grønt", "")
        assert "%" not in tekst, aksje.symbol
        # Hele ord, så «Signalnett» og «rekursjon» ikke teller.
        treff = re.findall(r"\b(kjøp\w*|selg\w*|salg\w*|kurs\w*|signal|signalet|anbefal\w*|råd)\b", tekst)
        assert treff == [], (aksje.symbol, treff)


def test_skriften_er_den_i_lesmeg():
    """Del B. Ville feilet hvis skriften, vekten, kursiv, store bokstaver,
    sperringen eller kapitélene for et selskap var en annen enn i tabellen i
    LESMEG.md, eller hvis et selskap manglet."""
    tabell = (GODKJENT / "LESMEG.md").read_text(encoding="utf-8").split("## De 15", 1)[1]
    fra_lesmeg = {}
    for rad in re.findall(r"^\| ([A-Z]{4}) \| [^|]+ \| [^|]+ \| ([^|]+) \|", tabell, re.M):
        symbol, skrift = rad[0], rad[1].strip()
        familie, vekt, rest = re.match(r"(.+?)(?: 72pt)? (\d{3})(.*)", skrift).groups()
        if "72pt" in skrift:
            familie = "Newsreader 72"
        fra_lesmeg[symbol] = Skrift(
            familie,
            int(vekt),
            kursiv="kursiv" in rest,
            store="store bokstaver" in rest,
            sperring=int(re.search(r"sperret (\d+) px", rest).group(1)) if "sperret" in rest else 0,
            kapiteler="kapitéler" in rest,
        )
    assert fra_lesmeg == SKRIFTER
    assert set(SKRIFTER) == {a.symbol for a in demo.DEMOUNIVERS}


# --- C: boblen og halen ------------------------------------------------------


def test_slagordet_er_vanlig_tekst_og_halen_pynt(demoklient):  # noqa: F811
    """Del C, spørsmål 6 og 7. Ville feilet hvis slagordet bare fantes i en
    SVG eller i alt, var et annet enn i bobler.json, halen ikke var skjult
    for skjermleseren, eller plassen ikke kom fra bobler.json."""
    bobler = investorsider._bobler()
    for aksje in demo.DEMOUNIVERS:
        html = demoklient.get(f"/investorside/{aksje.symbol}").get_data(as_text=True)
        side = _les(html)
        b = bobler[aksje.symbol]
        assert _ren(side.tekst["boble"]) == b["slagord"]
        assert side.attr["img"]["alt"] != b["slagord"]
        hale = re.search(r'<svg class="hale"[^>]*>(.*?)</svg>', html, re.S)
        assert 'aria-hidden="true"' in hale.group(0) and "<text" not in hale.group(1)
        stil = side.attr["boble"]["style"]
        verdier = {k: float(v) for k, v in re.findall(r"--(venstre|topp|bredde): ([\d.]+)%", stil)}
        assert verdier["venstre"] == pytest.approx(100 * b["boble"]["venstre"] / BREDDE, abs=1e-3)
        assert verdier["topp"] == pytest.approx(100 * b["boble"]["topp"] / HOYDE, abs=1e-3)
        assert verdier["bredde"] == pytest.approx(100 * b["boble"]["bredde"] / BREDDE, abs=1e-3)
        flate = " ".join(f"{x:g},{y:g}" for x, y in b["hale"]["flate"])
        assert f'points="{flate}"' in hale.group(1)


BRED = r"""
const q = (s) => document.querySelector(s).getBoundingClientRect();
const img = q('.flate img'), boble = q('p.boble'), ki = q('figcaption.ki-merke');
const r = {img: [img.left, img.top, img.width, img.height],
           boble: [boble.left - img.left, boble.top - img.top, boble.width, boble.height]};
const over = (a, b) => a.left < b.right - 0.5 && a.right > b.left + 0.5 && a.top < b.bottom - 0.5 && a.bottom > b.top + 0.5;
r.dekker = [['header', q('header.selskap')], ['ki', ki], ['nederst', q('p.oppdiktet')], ['tilbake', q('a.tilbake')]]
  .filter(([, b]) => over(boble, b)).map(([n]) => n);
r.kiUnder = ki.top - img.bottom;
r.hale = getComputedStyle(document.querySelector('svg.hale')).display;
r.rulling = document.documentElement.scrollWidth > document.documentElement.clientWidth;
r.lastet = [...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family.replace(/"/g, '') + ' ' + f.weight + ' ' + f.style);
const h1 = getComputedStyle(document.querySelector('h1'));
r.h1 = [h1.fontFamily.split(',')[0].replace(/"/g, ''), h1.fontWeight, h1.fontStyle, h1.fontSize];
ferdig(r);
"""

SMAL = r"""
const q = (s) => document.querySelector(s).getBoundingClientRect();
const img = q('.flate img'), boble = q('p.boble'), ki = q('figcaption.ki-merke');
ferdig({rulling: document.documentElement.scrollWidth > document.documentElement.clientWidth,
        bilde: [img.left, img.width, document.querySelector('main').clientWidth],
        rekkefoelge: [ki.top - img.bottom, boble.top - ki.bottom],
        hale: getComputedStyle(document.querySelector('svg.hale')).display,
        h1: q('h1').right <= document.documentElement.clientWidth + 0.5});
"""

# Gjennomgangen av 8.20b (VG1): i CI feiler testene når nettleseren mangler.
I_NETTLESER = pytest.mark.skipif(NETTLESER is None and not os.environ.get("CI"), reason="ingen Edge eller Chrome")


@I_NETTLESER
@pytest.mark.parametrize("aksje", demo.DEMOUNIVERS, ids=lambda a: a.symbol)
def test_boblen_ved_1280_px(demoklient, tmp_path, aksje):  # noqa: F811
    """Del C, målt i nettleseren som tests/test_kursgrafen_smal.py. Ville
    feilet hvis boblen dekket overskriften, lenken tilbake, KI-merket eller
    teksten nederst, sto et annet sted eller var en annen bredde enn
    bobler.json sier, var så høy at halen ikke møtte den, tegningen ikke var
    560 × 400 px på samme sted som på de andre sidene, KI-merket ikke sto rett
    under tegningen, eller selskapets skrift ikke ble lastet og brukt."""
    html = demoklient.get(f"/investorside/{aksje.symbol}").get_data(as_text=True)
    r = _kjoer(html, tmp_path, 1280, BRED)
    b = investorsider._bobler()[aksje.symbol]["boble"]
    assert r["dekker"] == [] and r["rulling"] is False and r["hale"] != "none", r
    venstre, topp, bredde, hoeyde = r["boble"]
    assert (venstre, topp, bredde) == (
        pytest.approx(b["venstre"], abs=1),
        pytest.approx(b["topp"], abs=1),
        pytest.approx(b["bredde"], abs=1),
    ), r
    # Halen begynner inne i den nederste kanten, og flaten dekker den.
    assert hoeyde == pytest.approx(b["hoyde"], abs=3), r
    assert r["img"][2:] == [BREDDE, HOYDE], r
    assert r["img"][:2] == pytest.approx(_PLASSEN, abs=0.5), r
    assert 0 <= r["kiUnder"] <= 16, r
    s = SKRIFTER[aksje.symbol]
    stil = "italic" if s.kursiv else "normal"
    assert r["h1"][:3] == [s.familie, str(s.vekt), stil], r
    assert f"{s.familie} {s.vekt} {stil}" in r["lastet"], r


# Tegningen står på samme sted på alle sidene (gruppens svar 24.10 kl. 13:02):
# venstre kant og toppen ved 1280 px, målt på BRFE. Måles den på nytt, skal
# alle 15 ha samme tall.
_PLASSEN = [136, 371]


@I_NETTLESER
@pytest.mark.parametrize("bredde", (390, 320))
@pytest.mark.parametrize("aksje", demo.DEMOUNIVERS, ids=lambda a: a.symbol)
def test_smal_skjerm_uten_vannrett_rulling(demoklient, tmp_path, aksje, bredde):  # noqa: F811
    """Del F. Ville feilet hvis en av de 15 sidene rullet vannrett ved 390
    eller 320 px, tegningen ikke var i full bredde, boblen sto over
    tegningen eller over KI-merket, halen ble vist, eller navnet gikk ut av
    siden."""
    html = demoklient.get(f"/investorside/{aksje.symbol}").get_data(as_text=True)
    r = _kjoer(html, tmp_path, bredde, SMAL)
    assert r["rulling"] is False and r["hale"] == "none" and r["h1"] is True, r
    venstre, bilde, main = r["bilde"]
    assert bilde == pytest.approx(main - 32, abs=1), r
    assert all(avstand >= 0 for avstand in r["rekkefoelge"]), r


# --- D: skriftene og lisensene ----------------------------------------------


def _woff_tabeller(data: bytes) -> list[tuple[str, int, bytes]]:
    assert data[:4] == b"wOFF", data[:4]
    antall = struct.unpack(">H", data[12:14])[0]
    ut = []
    for i in range(antall):
        tag, start, pakket, hel, sjekk = struct.unpack(">4sIIII", data[44 + 20 * i : 64 + 20 * i])
        raa = data[start : start + pakket]
        ut.append((tag.decode("ascii"), sjekk, zlib.decompress(raa) if pakket < hel else raa))
    return ut


def _sjekksum(data: bytes) -> int:
    data += b"\0" * (-len(data) % 4)
    return sum(struct.unpack(f">{len(data) // 4}I", data)) & 0xFFFFFFFF


# Gjennomgangen av 3.4h (BH3): sjekksummen i WOFF-fila skrives på nytt av et
# verktøy som kutter eller endrer skriften, så den alene viser ikke at fila er
# den samme. Filene ble kontrollert 07.11 tabell for tabell mot TTF-filene i
# kildearkivene (spesifikasjonen, «Skriftene»), og sha256 for de kontrollerte
# filene står her.
KONTROLLERTE_SKRIFTFILER = {
    "inter-display/InterDisplay-Black.woff": "938eff658d35bc8502d078897dfe5a642b36432d7c01c5b112b92164434960dd",
    "inter-display/InterDisplay-Bold.woff": "5748ee2c61b02afb06931ad098343b91b2be4fc92026de3f9fa5679f22451f5d",
    "inter-display/InterDisplay-ExtraBoldItalic.woff": "9e0072ec1d466914071aeb9421d32949b4cc8a58a7c2d615826d17fd08ad6ebd",
    "inter-display/InterDisplay-ExtraLight.woff": "7f48b9e2f9cea703dbf17d88e8722ff9aa4f62a5f919b8500a3f2c91db64b6af",
    "lora/Lora-Bold.woff": "474d215e3e9cc5ff5d278594dbdf31f01d34cff0be81d2af8232bfd078f4f08b",
    "lora/Lora-Medium.woff": "53aa828e82c94ad3773f6c4698a032c54dc3d328cc272c0ec34ccda6fbd129ae",
    "lora/Lora-Regular.woff": "41187a1a52141e0c94a588835bfb5fc215ee45a8a144448683caca8b44554b2f",
    "lora/Lora-SemiBoldItalic.woff": "54efd3e95ec2c9c779728a7f8cb879b78cf086b252dd139f52c4649b3ef26475",
    "liberation-mono/LiberationMono-Bold.woff": "a73f276d05da760764fede1f47388382f69daf558c0e96462838653c703e0ca5",
    "liberation-mono/LiberationMono-Regular.woff": "6690a1fef4524bdd1ee0f3388af7342969275f993f830e867a6717eecfee3de7",
}


@pytest.mark.parametrize("fil", sorted(NYE_SKRIFTFILER))
def test_skriften_er_bare_komprimert(fil):
    """Del D og OFL-FAQ 2.2.1: en WOFF-fil regnes ikke som en endret
    versjon når fontdataene er uendret utenom komprimeringen og
    WOFF-metadata er utelatt. Ville feilet hvis fila hadde metadata eller en
    privat blokk, en tabell ikke stemte med sjekksummen i fila, eller fila
    ikke var den som ble kontrollert mot kilden 07.11 (BH3)."""
    data = (FONTS / fil).read_bytes()
    assert hashlib.sha256(data).hexdigest() == KONTROLLERTE_SKRIFTFILER[fil], fil
    meta, metalengde, _, privat, privatlengde = struct.unpack(">IIIII", data[24:44])
    assert (meta, metalengde, privat, privatlengde) == (0, 0, 0, 0)
    for tag, sjekk, raa in _woff_tabeller(data):
        if tag == "head":
            raa = raa[:8] + b"\0\0\0\0" + raa[12:]
        assert _sjekksum(raa) == sjekk, (fil, tag)


def test_hver_skrift_har_lisensen_raden_og_font_face():
    """Del D. Ville feilet hvis en ny skrift manglet lisensfila med OFL 1.1,
    raden i docs/kilder-og-rettigheter.md, sin @font-face, eller hvis en fil
    lå i mappa uten å brukes, eller en skrift ble lastet fra nettet."""
    for familie in ("inter-display", "lora", "liberation-mono"):
        lisens = (FONTS / familie / "OFL.txt").read_text(encoding="utf-8")
        assert "SIL OPEN FONT LICENSE Version 1.1" in lisens, familie
        filer = {p.relative_to(FONTS).as_posix() for p in (FONTS / familie).iterdir()}
        assert filer == {f for f in NYE_SKRIFTFILER if f.startswith(familie + "/")} | {f"{familie}/OFL.txt"}
    for fil, (familie, vekt, stil) in NYE_SKRIFTFILER.items():
        regel = re.search(
            rf'@font-face \{{ font-family: "{familie}"; font-weight: {vekt}; font-style: {stil};[^}}]*url\("/static/fonts/{re.escape(fil)}"\) format\("woff"\); \}}',
            STIL,
        )
        assert regel, fil
    for navn in ("Inter Display", "Lora", "Liberation Mono"):
        rad = next((linje for linje in KILDER.splitlines() if linje.startswith(f"| {navn} ")), None)
        assert rad and "OFL" in rad and "src/static/fonts/" in rad, navn
    assert not re.search(r"@import|url\(\s*[\"']?https?:", STIL)


def test_hvert_snitt_i_lesmeg_finnes_i_appen():
    """Del D. Ville feilet hvis en skrift i tabellen hadde et snitt appen
    ikke har en fil for, så nettleseren lagde et falskt fett eller kursivt
    snitt."""
    finnes = FANTES | {(f, v) for f, v, _ in NYE_SKRIFTFILER.values()}
    for symbol, s in SKRIFTER.items():
        assert (s.familie, s.vekt) in finnes, symbol
        if s.kursiv:
            assert (s.familie, s.vekt, "italic") in NYE_SKRIFTFILER.values(), symbol


# --- G: kopiene ----------------------------------------------------------------


def test_kopiene_er_byte_for_byte_de_godkjente():
    """Del G og spørsmål 2. Ville feilet hvis en kopi i src/static/investorsider/
    var endret i forhold til den godkjente fila i docs/bilder/investorsider/,
    eller en av de 15 manglet. Da viser appen noe gruppen ikke har godkjent."""
    godkjente = {p.name: p for p in (GODKJENT / "svg").glob("*.svg")} | {"bobler.json": GODKJENT / "bobler.json"}
    kopier = {p.name: p for p in KOPIENE.iterdir()}
    assert set(kopier) == set(godkjente) and len(godkjente) == 16
    assert {f"{a.symbol.lower()}.svg" for a in demo.DEMOUNIVERS} | {"bobler.json"} == set(kopier)
    for navn, fil in godkjente.items():
        lf = lambda p: p.read_bytes().replace(b"\r\n", b"\n")  # noqa: E731
        assert hashlib.sha256(lf(kopier[navn])).hexdigest() == hashlib.sha256(lf(fil)).hexdigest(), navn


# --- E: boblen nederst på aksjesiden -----------------------------------------


def _boblen(html: str) -> _Side:
    deler = re.findall(r'<p class="investorboble">.*?</p>', html, re.S)
    assert len(deler) <= 1, deler
    return _les(deler[0]) if deler else None


def test_boblen_i_demoen(demoklient):  # noqa: F811
    """Del E. Ville feilet hvis boblen i demoen hadde pil, åpnet i en ny
    fane, gikk et annet sted enn til siden for selskapet, manglet på siden
    uten kurser (spørsmål 5), sto før «Signalet dag for dag», eller hvis
    «NewsWeb» sto på aksjesiden."""
    for aksje in demo.DEMOUNIVERS:
        html = demoklient.get(f"/aksje/{aksje.symbol}").get_data(as_text=True)
        boble = _boblen(html)
        assert boble is not None, aksje.symbol
        lenke = boble.lenker[0]
        assert lenke == {"href": f"/investorside/{aksje.symbol}"}, lenke
        assert _ren(boble.tekst["investorboble"]) == f"Investorsiden til {aksje.navn}"
        # Story 8.26 (tillegg 4): lenken «Den ekte versjonen» i demolinja har
        # pila; boblen har den ikke.
        assert (
            "pil" not in boble.tekst
            and "↗" not in html.split('<p class="eksempeltall">', 1)[0] + html.split("</header>", 1)[1]
        )
        assert "newsweb" not in html.lower()
        if 'id="signalet-dag-for-dag"' in html:
            assert html.index('class="investorboble"') > html.index(
                "</section>", html.index('id="signalet-dag-for-dag"')
            )
        else:
            assert aksje.symbol == "MTFJ"


@pytest.mark.usefixtures("ekte_base")
@pytest.mark.parametrize("aksje", AKSJEUNIVERS, ids=lambda a: a.symbol)
def test_boblen_i_den_ekte_versjonen(klient, aksje):  # noqa: F811
    """Del E. Ville feilet hvis boblen åpnet i samme fane, manglet
    rel="noreferrer", gikk til en annen adresse enn i INVESTORSIDER, pila
    ikke var skjult for skjermleseren, den skjulte teksten ikke sa at
    lenken åpnes i en ny fane, eller «NewsWeb» sto på siden."""
    for sti in (f"/aksje/{aksje.symbol}", f"/aksje/{aksje.symbol}?dag=2026-10-15"):
        html = klient.get(sti).get_data(as_text=True)
        boble = _boblen(html)
        # Gjennomgangen (ECH5): en melding, ikke AttributeError.
        assert boble is not None, sti
        lenke = boble.lenker[0]
        assert lenke["href"] == INVESTORSIDER[aksje.symbol], sti
        assert lenke["target"] == "_blank" and lenke["rel"] == "noreferrer", lenke
        assert _ren(boble.tekst["investorboble"]) == f"Investorsiden til {aksje.navn} ↗ (åpnes i en ny fane)"
        assert boble.attr["pil"]["aria-hidden"] == "true" and _ren(boble.tekst["pil"]) == "↗"
        assert _ren(boble.tekst["skjult"]) == "(åpnes i en ny fane)"
        assert "newsweb" not in html.lower(), sti


@pytest.mark.usefixtures("ekte_base")
def test_uten_adresse_ingen_boble(klient, monkeypatch):  # noqa: F811
    """Spørsmål 3. Ville feilet hvis en aksje uten adresse fikk en boble som
    ikke kan klikkes, eller en setning i stedet."""
    import kursdata

    # En kopi, så rekkefølgen i INVESTORSIDER står for de andre testene.
    monkeypatch.setattr(kursdata, "INVESTORSIDER", {s: a for s, a in INVESTORSIDER.items() if s != "EQNR"})
    html = klient.get("/aksje/EQNR").get_data(as_text=True)
    assert _boblen(html) is None
    assert "investorsiden til" not in html.lower()


def test_boblen_i_den_ekte_versjonen_uten_kurser(klient):  # noqa: F811
    """Spørsmål 5, gjennomgangen (VG1, BH4). Ville feilet hvis en aksje i den
    ekte versjonen med adresse, men uten en eneste kurs, ikke fikk boblen
    nederst, eller boblen der åpnet i samme fane."""
    tilkobling = aapne_base(lagring_sqlite.BASE_STI)
    try:
        lager = SqliteKurslager(tilkobling)
        for aksje in AKSJEUNIVERS:
            if aksje.symbol != "DNB":
                lager.erstatt_serie(aksje.symbol, RADENE, datetime(2026, 11, 1, tzinfo=timezone.utc))
    finally:
        tilkobling.close()
    svar = klient.get("/aksje/DNB")
    html = svar.get_data(as_text=True)
    assert svar.status_code == 200 and "ingen kursgraf og ingen sjekker for DNB Bank." in html
    boble = _boblen(html)
    assert boble is not None
    lenke = boble.lenker[0]
    assert lenke["href"] == INVESTORSIDER["DNB"]
    assert lenke["target"] == "_blank" and lenke["rel"] == "noreferrer", lenke
    assert boble.attr["pil"]["aria-hidden"] == "true"
    assert "newsweb" not in html.lower()


BOBLEN_SMAL = r"""
const a = document.querySelector('p.investorboble a').getBoundingClientRect();
ferdig({rulling: document.documentElement.scrollWidth > document.documentElement.clientWidth,
        inne: a.right <= document.documentElement.clientWidth + 0.5 && a.left >= 0});
"""


@I_NETTLESER
@pytest.mark.parametrize("bredde", (390, 320))
def test_boblen_paa_aksjesiden_ved_smal_skjerm(klient, ekte_base, tmp_path, bredde):  # noqa: F811
    """Del F. Ville feilet hvis boblen med det lengste navnet og pila gikk
    ut av siden ved 390 eller 320 px i stedet for å bryte teksten."""
    lengste = max(AKSJEUNIVERS, key=lambda a: len(a.navn))
    html = klient.get(f"/aksje/{lengste.symbol}").get_data(as_text=True)
    r = _kjoer(html, tmp_path, bredde, BOBLEN_SMAL)
    assert r == {"rulling": False, "inne": True}, r


# --- G: hjelpen og README-en ---------------------------------------------------


def test_hjelpen_sier_det_samme_som_sidene():
    """Del G og regel 19. Ville feilet hvis docs/hjelp.md fortsatt sa at
    lenken står under kursgrafen eller at demoselskapene ikke har en side,
    eller ikke nevnte siden i demoen og den nye fanen, eller steg 6 i
    «Demoen» i README-en ikke sa at boblen går til en side i appen
    (gjennomgangen, BH8)."""
    hjelp = (ROT / "docs" / "hjelp.md").read_text(encoding="utf-8")
    svar = hjelp.split("### Hvor finner jeg børsmeldingene?", 1)[1].split("\n### ", 1)[0]
    assert "Under kursgrafen" not in svar and "har ingen investorside" not in svar
    assert "«Investorsiden til ‹navn›»" in svar and "ny fane" in svar and "tegning laget av KI" in svar
    # Story 3.5i: «Demoen» staar i docs/installasjon.md.
    readme = installasjonen()
    steg6 = next(linje for linje in readme.splitlines() if linje.startswith("6. **Åpne http://127.0.0.1:8000**"))
    assert "boblen «Investorsiden til ‹navn›»" in steg6 and "en side i appen" in steg6 and "laget av KI" in steg6
