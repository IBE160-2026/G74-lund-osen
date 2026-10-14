"""Tester for utseendet - story 8.0d, designregler §1 og §5.

Skriftfilene leses med standardbiblioteket alene: WOFF 1.0 er tabellene fra
OpenType, hver pakket med zlib. Ingen test henter noe fra nettet (AD-8).
"""

import struct
import zlib
from pathlib import Path

import pytest

FONTS = Path(__file__).resolve().parent.parent / "src" / "static" / "fonts"

# Filene i designregler §1 og §5, med vekten @font-face gir dem.
SKRIFTFILENE = {
    "ibm-plex-sans/IBMPlexSans-Regular.woff": 400,
    "ibm-plex-sans/IBMPlexSans-Medium.woff": 500,
    "ibm-plex-sans/IBMPlexSans-SemiBold.woff": 600,
    "ibm-plex-sans/IBMPlexSans-Bold.woff": 700,
    "newsreader/Newsreader16pt-Medium.woff": 500,
    "newsreader/Newsreader16pt-SemiBold.woff": 600,
    # Story 8.0d, PR 2: de store overskriftene (svar 1 på planen 14.10).
    "newsreader/Newsreader72pt-Medium.woff": 500,
}


def _tabeller(data: bytes) -> dict[str, bytes]:
    """Tabellene i en WOFF 1.0-fil, pakket ut."""
    assert data[:4] == b"wOFF", data[:4]
    antall = struct.unpack(">H", data[12:14])[0]
    tabeller = {}
    for i in range(antall):
        tag, start, pakket, hel, _ = struct.unpack(">4sIIII", data[44 + 20 * i:64 + 20 * i])
        raa = data[start:start + pakket]
        tabeller[tag.decode("ascii")] = zlib.decompress(raa) if pakket < hel else raa
    return tabeller


def _funksjoner(gsub: bytes) -> set[str]:
    """OpenType-funksjonene i FeatureList i GSUB, som «tnum» og «ss01»."""
    liste = struct.unpack(">H", gsub[6:8])[0]
    antall = struct.unpack(">H", gsub[liste:liste + 2])[0]
    return {gsub[liste + 2 + 6 * i:liste + 6 + 6 * i].decode("ascii") for i in range(antall)}


def _glyfer(cmap: bytes, tegn: range) -> list[int]:
    """Glyfnumrene for tegnene, fra cmap format 4 (Windows Unicode)."""
    for i in range(struct.unpack(">H", cmap[2:4])[0]):
        plattform, koding, start = struct.unpack(">HHI", cmap[4 + 8 * i:12 + 8 * i])
        if (plattform, koding) in ((3, 1), (0, 3)) and struct.unpack(">H", cmap[start:start + 2])[0] == 4:
            t = cmap[start:]
            dobbel = struct.unpack(">H", t[6:8])[0]
            n = dobbel // 2
            slutt = struct.unpack(f">{n}H", t[14:14 + dobbel])
            begynn = struct.unpack(f">{n}H", t[16 + dobbel:16 + 2 * dobbel])
            delta = struct.unpack(f">{n}h", t[16 + 2 * dobbel:16 + 3 * dobbel])
            fra = 16 + 3 * dobbel
            forskyvning = struct.unpack(f">{n}H", t[fra:fra + dobbel])
            glyfer = []
            for c in tegn:
                k = next((k for k in range(n) if begynn[k] <= c <= slutt[k]), None)
                assert k is not None, hex(c)
                if forskyvning[k] == 0:
                    glyfer.append((c + delta[k]) & 0xFFFF)
                else:
                    p = fra + 2 * k + forskyvning[k] + 2 * (c - begynn[k])
                    g = struct.unpack(">H", t[p:p + 2])[0]
                    glyfer.append((g + delta[k]) & 0xFFFF if g else 0)
            return glyfer
    raise AssertionError("ingen cmap i format 4")


def _bredder(tabeller: dict[str, bytes], glyfer: list[int]) -> list[int]:
    """Bredden hver glyf rykker fram, fra hmtx."""
    metrikker = struct.unpack(">H", tabeller["hhea"][34:36])[0]
    hmtx = tabeller["hmtx"]
    return [struct.unpack(">H", hmtx[4 * min(g, metrikker - 1):4 * min(g, metrikker - 1) + 2])[0]
            for g in glyfer]


class TestSkriftfilene:
    """Designregler §1 og §5: filene ligger i appen med lisensen, og
    tallene står rett under hverandre."""

    @pytest.mark.parametrize("fil", sorted(SKRIFTFILENE))
    def test_sifrene_er_like_brede(self, fil):
        """Tabelltall. Ville feilet med en fil der 1 er smalere enn 0."""
        tabeller = _tabeller((FONTS / fil).read_bytes())
        bredder = _bredder(tabeller, _glyfer(tabeller["cmap"], range(0x30, 0x3A)))
        assert len(set(bredder)) == 1, bredder

    @pytest.mark.parametrize("fil", sorted(SKRIFTFILENE))
    def test_tnum_der_filen_har_proporsjonale_sifre_som_valg(self, fil):
        """§1 sier tnum. IBM Plex Sans har ikke funksjonen, men sifrene er
        like brede uten den (målt 14.10, §5). Har filen pnum, skal den også
        ha tnum, så tabular-nums i stilen gir tabelltall."""
        gsub = _tabeller((FONTS / fil).read_bytes()).get("GSUB")
        funksjoner = _funksjoner(gsub) if gsub else set()
        if "pnum" in funksjoner:
            assert "tnum" in funksjoner
        if fil.startswith("newsreader/"):
            assert "tnum" in funksjoner, fil

    def test_hele_filer_med_stilvariantene(self):
        """§1: hele filer, ikke split, så ss01 og ss02 er med (IBM/plex
        issue 162)."""
        for fil in SKRIFTFILENE:
            if fil.startswith("ibm-plex-sans/"):
                funksjoner = _funksjoner(_tabeller((FONTS / fil).read_bytes())["GSUB"])
                assert {"ss01", "ss02"} <= funksjoner, fil

    def test_lisensen_ligger_ved_filene(self):
        for familie in ("ibm-plex-sans", "newsreader"):
            lisens = (FONTS / familie / "OFL.txt").read_text(encoding="utf-8")
            assert "SIL Open Font License, Version 1.1" in lisens, familie

    def test_bare_filene_som_brukes(self):
        filer = {p.relative_to(FONTS).as_posix() for p in FONTS.rglob("*") if p.is_file()}
        assert filer == set(SKRIFTFILENE) | {"ibm-plex-sans/OFL.txt", "newsreader/OFL.txt"}


# Sidene i alle tilstandene: den ekte versjonen med og uten kurser, demoen
# og feilsiden (FR-411, designregler §5). Fixturene er demotestenes.
import re  # noqa: E402

import app as app_modul  # noqa: E402
from lagring_sqlite import demo_sti  # noqa: E402
from test_app import _regel, _stil, monter, serie, snapshot  # noqa: E402
from test_demo import demobase, fast_klokke, klient, mal  # noqa: E402,F401

# Fargene i designregler §5 som maa holde kontrasten: forgrunn, bakgrunn og
# minste forhold. 4,5 for tekst og 3 for streker, ringen og fokus.
KONTRAST = [
    ("blekk", "bakgrunn", 4.5), ("blekk", "kort", 4.5),
    ("tekst", "bakgrunn", 4.5), ("tekst", "kort", 4.5),
    ("dempet", "bakgrunn", 4.5), ("dempet", "kort", 4.5), ("dempet-2", "kort", 4.5),
    ("opp", "kort", 4.5), ("opp", "opp-bakgrunn", 4.5),
    ("ned", "kort", 4.5), ("ned", "ned-bakgrunn", 4.5),
    ("blandet", "blandet-bakgrunn", 4.5), ("dempet", "ingen-bakgrunn", 4.5),
    ("blekk", "baand-ut", 4.5), ("tekst", "baand-oevrige", 4.5),
    ("brun", "hjelp-bakgrunn", 4.5), ("kurs", "kort", 4.5), ("snitt", "kort", 4.5),
    ("stripe-tekst", "blekk", 4.5), ("stripe-tekst-2", "blekk", 4.5),
    ("kort", "fyll", 4.5), ("hvit", "blekk", 4.5),
    # Gjennomgangen (ECH6, BH5): tabellen og grafen står også på bakgrunnen.
    ("blandet", "kort", 4.5), ("opp", "bakgrunn", 4.5), ("ned", "bakgrunn", 4.5),
    ("blandet", "bakgrunn", 4.5), ("kurs", "bakgrunn", 4.5), ("snitt", "bakgrunn", 4.5),
    # Story 8.0d, PR 2 (designregler §3, 14.10): ringen og strekene i
    # oransje trenger ikke 3:1 mot hvitt og bakgrunnen, fordi teksten sier
    # det samme (FR-103) og pillen har svart fyll. Parene for den gule
    # ringen mot hvitt og bakgrunnen er tatt ut med den grunnen. Ringen mot
    # fyllet og fokus på blekk står.
    ("oransje", "fyll", 3.0), ("oransje", "blekk", 3.0),
    # Teksten i båndet, pillene, markeringen, «NOK» og brikken i kortet.
    ("brun", "baand-ut", 4.5), ("hvit", "brun", 4.5), ("hvit", "tekst", 4.5),
    ("blekk", "lys-oransje", 4.5), ("kolonne-tekst-2", "blekk", 4.5), ("hvit", "opp", 4.5),
]


def _farger(stil: str) -> dict[str, str]:
    return dict(re.findall(r"--([a-z0-9-]+):\s*#([0-9a-fA-F]{6})", _regel(stil, ":root")))


def _stripa(html: str) -> str:
    return html.split('<header class="stripe">', 1)[1].split("</header>", 1)[0]


def _kontrast(a: str, b: str) -> float:
    def lys(farge):
        def lin(c):
            c = c / 255
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b_ = (int(farge[i:i + 2], 16) for i in (0, 2, 4))
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b_)
    hoey, lav = sorted((lys(a), lys(b)), reverse=True)
    return (hoey + 0.05) / (lav + 0.05)


@pytest.fixture
def sidene(klient, monkeypatch, demobase):
    """Hver side som finnes, i hver tilstand: {navn: html}."""
    sider = {"tom base": klient.get("/").data.decode("utf-8")}
    monter(monkeypatch, snapshot({
        "EQNR": serie([100.0] * 60 + [104.0], [1000] * 60 + [5000]),
        "DNB": serie([100.0] * 61),
    }))
    sider["oversikten"] = klient.get("/").data.decode("utf-8")
    sider["aksjesiden"] = klient.get("/aksje/EQNR").data.decode("utf-8")
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    sider["oversikten i demoen"] = klient.get("/").data.decode("utf-8")
    sider["aksjesiden i demoen"] = klient.get("/aksje/BRFE").data.decode("utf-8")
    demo_sti().write_bytes(b"ikke en sqlite-base" * 10)
    svar = klient.get("/")
    assert svar.status_code == 503
    sider["feilsiden"] = svar.data.decode("utf-8")
    return sider


class TestRammen:
    """Designregler §5: samme ramme på alle sidene, også i demoen."""

    def test_kontrasten_regnet_fra_fargene_i_stilen(self, sidene):
        """Ville feilet hvis blekk ble byttet til en lys farge, eller ringen
        fikk tavlas #F2B53A (1,83:1 mot hvitt)."""
        for navn, html in sidene.items():
            farger = _farger(_stil(html))
            for forgrunn, bakgrunn, minst in KONTRAST:
                forhold = _kontrast(farger[forgrunn], farger[bakgrunn])
                assert forhold >= minst, (navn, forgrunn, bakgrunn, round(forhold, 2))

    def test_ingen_farge_skrevet_fast_i_en_side(self, sidene):
        """Fargene står som navn i rammen, og sidene bruker navnene."""
        for navn, html in sidene.items():
            stil = _stil(html)
            utenom_rot = stil.replace(_regel(stil, ":root"), "")
            fast = re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}\b", utenom_rot)
            assert not fast, (navn, fast)
            # rgba() bare i skyggene fra utdraget (utdraget §5 og §7).
            for regel in re.findall(r"[^;{}]*rgba?\([^;{}]*", utenom_rot):
                assert "box-shadow" in regel or regel.strip().startswith("0 2px"), (navn, regel)
            assert not re.search(r'(?:style|fill|stroke)="[^"]*#', html), navn

    def test_ingenting_fra_nettet(self, sidene):
        """Ville feilet med skrift eller stil fra Google Fonts, et skript,
        eller en adresse med http."""
        for navn, html in sidene.items():
            assert "<script" not in html.lower(), navn
            assert "@import" not in html, navn
            assert not re.search(r"https?:|//[a-z]", _stil(html)), navn
            for verdi in re.findall(r'(?:src|href)="([^"]*)"', html):
                assert not re.match(r"(https?:)?//", verdi), (navn, verdi)
            for adresse in re.findall(r"""url\(\s*["']?([^"')]+)""", html):
                assert adresse.startswith("/static/fonts/"), (navn, adresse)

    def test_skriften_er_den_i_appen(self, sidene):
        for navn, html in sidene.items():
            stil = _stil(html)
            assert '"IBM Plex Sans"' in _regel(stil, "body"), navn
            assert '"Newsreader"' in _regel(stil, "h1, h2"), navn
            for fil in SKRIFTFILENE:
                assert f'url("/static/fonts/{fil}")' in stil, (navn, fil)

    def test_hver_lenke_gaar_til_en_side_som_finnes(self, sidene):
        """Ville feilet med en lenke til /min-liste før 8.3."""
        for navn, html in sidene.items():
            for href in re.findall(r'href="([^"]*)"', html):
                assert href == "/" or re.fullmatch(r"/aksje/[A-Z0-9]+", href), (navn, href)

    def test_tabelltall_i_tallcellene(self, sidene):
        """Ville feilet hvis tabular-nums ble fjernet fra tallcellene."""
        oversikt = _stil(sidene["oversikten"])
        for velger in ("td.tall", ".styrke"):
            assert "tabular-nums" in _regel(oversikt, velger), velger
        aksje = _stil(sidene["aksjesiden"])
        for velger in (".noekkeltall .verdi", "td.fortegn", ".regnestykke"):
            assert "tabular-nums" in _regel(aksje, velger), velger

    def test_fokus_i_blekk_paa_lys_bakgrunn_og_lys_gul_i_stripa(self, sidene):
        """Ville feilet med gult fokus på lys bakgrunn (1,64:1).

        PR 2: fargen heter oransje, og kolonneraden er blekk som stripa."""
        for navn, html in sidene.items():
            stil = _stil(html)
            assert "outline: 3px solid var(--blekk)" in _regel(stil, "*:focus-visible"), navn
            assert "var(--oransje)" in _regel(stil, "header.stripe *:focus-visible"), navn
            for velger, regel in re.findall(r"([^{}]*focus-visible[^{}]*)\{([^}]*)\}", stil):
                if "stripe" not in velger and "thead" not in velger:
                    assert not re.search(r"gul|oransje|currentColor", regel), (navn, velger)

    def test_stripa_og_bunnlinja_paa_alle_sidene(self, sidene):
        for navn, html in sidene.items():
            stripe = _stripa(html)
            assert "OSE Signal" in stripe and 'aria-hidden="true"' in stripe, navn
            assert (html.index("</header>") < html.index("<main>")
                    < html.index('<footer class="bunnlinje">')), navn
        # VG1: hele teksten, også på aksjesiden. HENTET er 15.40 UTC
        # mandag 21.09, 17.40 i Norge.
        for navn in ("oversikten", "aksjesiden"):
            assert "Oppdatert mandag 21.09 kl. 17.40" in _stripa(sidene[navn]), navn
        assert "Oppdatert " not in _stripa(sidene["tom base"])
        # BH10: meldingen på feilsiden står i et kort.
        assert '<div class="kort">' in sidene["feilsiden"]

    def test_merket_staar_i_stripa_i_demoen(self, sidene):
        """FR-411 og svar 3: hele merket som egen rad i stripa, uten det gule
        banneret. Ville feilet hvis merket ble borte fra stripa."""
        merket = f'<p class="eksempeltall">Demoversjon. {app_modul.EKSEMPELTALL_MERKE}</p>'
        # Feilsiden her har en demo.db som ikke kan leses, og ingen kan si at
        # den er en demobase. Feilsiden for en demobase har merket
        # (test_demo.py, test_feilsiden_har_eksempeltall_for_en_demobase).
        for navn in ("oversikten i demoen", "aksjesiden i demoen"):
            assert merket in _stripa(sidene[navn]), navn
        for navn in ("oversikten", "aksjesiden", "tom base"):
            assert "eksempeltall" not in _stripa(sidene[navn]), navn
        for html in sidene.values():
            assert "#fff3cd" not in html.lower() and "#c9a227" not in html.lower()

    def test_hjelpeknappen_og_vinduet(self, sidene):
        """Utdraget §7: svart sirkel på 22 px i en klikkflate på 44 px, og
        vinduet med merket «Hjelp» og tittelen i Newsreader."""
        stil = _stil(sidene["oversikten"])
        knapp = _regel(stil, "button.hjelpeknapp")
        assert "width: 44px; height: 44px" in knapp
        assert "radial-gradient(circle, var(--blekk) 10.5px" in knapp
        assert '"Newsreader"' in _regel(stil, ".hjelpevindu h2")
        for navn in ("oversikten", "oversikten i demoen"):
            assert '<span class="hjelpemerke">Hjelp</span>' in sidene[navn], navn
