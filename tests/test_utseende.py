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
        tag, start, pakket, hel, _ = struct.unpack(">4sIIII", data[44 + 20 * i : 64 + 20 * i])
        raa = data[start : start + pakket]
        tabeller[tag.decode("ascii")] = zlib.decompress(raa) if pakket < hel else raa
    return tabeller


def _funksjoner(gsub: bytes) -> set[str]:
    """OpenType-funksjonene i FeatureList i GSUB, som «tnum» og «ss01»."""
    liste = struct.unpack(">H", gsub[6:8])[0]
    antall = struct.unpack(">H", gsub[liste : liste + 2])[0]
    return {gsub[liste + 2 + 6 * i : liste + 6 + 6 * i].decode("ascii") for i in range(antall)}


def _glyfer(cmap: bytes, tegn: range) -> list[int]:
    """Glyfnumrene for tegnene, fra cmap format 4 (Windows Unicode)."""
    for i in range(struct.unpack(">H", cmap[2:4])[0]):
        plattform, koding, start = struct.unpack(">HHI", cmap[4 + 8 * i : 12 + 8 * i])
        if (plattform, koding) in ((3, 1), (0, 3)) and struct.unpack(">H", cmap[start : start + 2])[0] == 4:
            t = cmap[start:]
            dobbel = struct.unpack(">H", t[6:8])[0]
            n = dobbel // 2
            slutt = struct.unpack(f">{n}H", t[14 : 14 + dobbel])
            begynn = struct.unpack(f">{n}H", t[16 + dobbel : 16 + 2 * dobbel])
            delta = struct.unpack(f">{n}h", t[16 + 2 * dobbel : 16 + 3 * dobbel])
            fra = 16 + 3 * dobbel
            forskyvning = struct.unpack(f">{n}H", t[fra : fra + dobbel])
            glyfer = []
            for c in tegn:
                k = next((k for k in range(n) if begynn[k] <= c <= slutt[k]), None)
                assert k is not None, hex(c)
                if forskyvning[k] == 0:
                    glyfer.append((c + delta[k]) & 0xFFFF)
                else:
                    p = fra + 2 * k + forskyvning[k] + 2 * (c - begynn[k])
                    g = struct.unpack(">H", t[p : p + 2])[0]
                    glyfer.append((g + delta[k]) & 0xFFFF if g else 0)
            return glyfer
    raise AssertionError("ingen cmap i format 4")


def _bredder(tabeller: dict[str, bytes], glyfer: list[int]) -> list[int]:
    """Bredden hver glyf rykker fram, fra hmtx."""
    metrikker = struct.unpack(">H", tabeller["hhea"][34:36])[0]
    hmtx = tabeller["hmtx"]
    return [struct.unpack(">H", hmtx[4 * min(g, metrikker - 1) : 4 * min(g, metrikker - 1) + 2])[0] for g in glyfer]


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
    ("blekk", "bakgrunn", 4.5),
    ("blekk", "kort", 4.5),
    ("tekst", "bakgrunn", 4.5),
    ("tekst", "kort", 4.5),
    ("dempet", "bakgrunn", 4.5),
    ("dempet", "kort", 4.5),
    ("dempet-2", "kort", 4.5),
    ("opp", "kort", 4.5),
    ("opp", "opp-bakgrunn", 4.5),
    ("ned", "kort", 4.5),
    ("ned", "ned-bakgrunn", 4.5),
    ("blandet", "blandet-bakgrunn", 4.5),
    ("dempet", "ingen-bakgrunn", 4.5),
    ("blekk", "baand-ut", 4.5),
    ("tekst", "baand-oevrige", 4.5),
    ("brun", "hjelp-bakgrunn", 4.5),
    ("kurs", "kort", 4.5),
    ("snitt", "kort", 4.5),
    ("stripe-tekst", "blekk", 4.5),
    ("stripe-tekst-2", "blekk", 4.5),
    ("kort", "fyll", 4.5),
    ("hvit", "blekk", 4.5),
    # Gjennomgangen (ECH6, BH5): tabellen og grafen står også på bakgrunnen.
    ("blandet", "kort", 4.5),
    ("opp", "bakgrunn", 4.5),
    ("ned", "bakgrunn", 4.5),
    ("blandet", "bakgrunn", 4.5),
    ("kurs", "bakgrunn", 4.5),
    ("snitt", "bakgrunn", 4.5),
    # Story 8.0d, PR 2 (designregler §3, 14.10): ringen og strekene i
    # oransje trenger ikke 3:1 mot hvitt og bakgrunnen, fordi teksten sier
    # det samme (FR-103) og pillen har svart fyll. Parene for den gule
    # ringen mot hvitt og bakgrunnen er tatt ut med den grunnen. Ringen mot
    # fyllet og fokus på blekk står.
    ("oransje", "fyll", 3.0),
    ("oransje", "blekk", 3.0),
    # Teksten i båndet, pillene, markeringen, «NOK» og brikken i kortet.
    ("brun", "baand-ut", 4.5),
    ("hvit", "brun", 4.5),
    ("hvit", "tekst", 4.5),
    ("blekk", "lys-oransje", 4.5),
    ("kolonne-tekst-2", "blekk", 4.5),
    ("hvit", "opp", 4.5),
    # Story 8.0d, PR 3: brikken for -1 og den hvite pillen ved 2 av 3.
    # Resultatpillene i sjekkortene bruker parene for retningen over.
    ("hvit", "ned", 4.5),
    ("blekk", "hvit", 4.5),
    ("dempet-2", "hvit", 4.5),
    # Gjennomgangen av PR 3 (VG8): det grå feltet mot sporet (del 5, 3,23:1).
    ("felt", "spor", 3.0),
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

        r, g, b_ = (int(farge[i : i + 2], 16) for i in (0, 2, 4))
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b_)

    hoey, lav = sorted((lys(a), lys(b)), reverse=True)
    return (hoey + 0.05) / (lav + 0.05)


@pytest.fixture
def sidene(klient, monkeypatch, demobase):
    """Hver side som finnes, i hver tilstand: {navn: html}."""
    sider = {"tom base": klient.get("/").data.decode("utf-8")}
    monter(
        monkeypatch,
        snapshot(
            {
                "EQNR": serie([100.0] * 60 + [104.0], [1000] * 60 + [5000]),
                "DNB": serie([100.0] * 61),
            }
        ),
    )
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
        """Ville feilet hvis blekk ble byttet til en lys farge. Ringen er
        tavlas #F2B53A siden PR 2 (designregler §3, 14.10), og står mot fyllet."""
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
                # Story 8.15: sorteringen er en parameter på /.
                assert (
                    href == "/"
                    or re.fullmatch(r"/aksje/[A-Z0-9]+", href)
                    or re.fullmatch(r"/\?sorter=(kurs|endring|signal|retning)&amp;orden=(synkende|stigende)", href)
                ), (navn, href)

    def test_tabelltall_i_tallcellene(self, sidene):
        """Ville feilet hvis tabular-nums ble fjernet fra tallcellene."""
        oversikt = _stil(sidene["oversikten"])
        for velger in ("td.tall", ".styrke"):
            assert "tabular-nums" in _regel(oversikt, velger), velger
        aksje = _stil(sidene["aksjesiden"])
        # Story 8.0d, PR 3: resultatpillen i sjekkortene erstatter Ga-cellen.
        for velger in (".noekkeltall .verdi", ".sjekkort .resultat", ".sjekkort .regnestykke", ".brikke"):
            assert "tabular-nums" in _regel(aksje, velger), velger

    def test_fokus_i_blekk_paa_lys_bakgrunn_og_lys_gul_i_stripa(self, sidene):
        """Ville feilet med gult fokus på lys bakgrunn (1,64:1).

        PR 2: fargen heter oransje. Regelen for kolonneraden i oversikten
        står sammen med stripa (BH1 i gjennomgangen)."""
        for navn, html in sidene.items():
            stil = _stil(html)
            assert "outline: 3px solid var(--blekk)" in _regel(stil, "*:focus-visible"), navn
            assert "var(--oransje)" in _regel(stil, "header.stripe *:focus-visible"), navn
            for velger, regel in re.findall(r"([^{}]*focus-visible[^{}]*)\{([^}]*)\}", stil):
                # Story 8.15: lenkene i kolonneraden står på blekk, som stripa.
                # Gjennomgangen (BH6): bare akkurat den regelen.
                if "stripe" not in velger and velger.strip() != ".tabellboks thead a.sorter:focus-visible":
                    assert not re.search(r"gul|oransje|currentColor", regel), (navn, velger)

    def test_stripa_og_bunnlinja_paa_alle_sidene(self, sidene):
        for navn, html in sidene.items():
            stripe = _stripa(html)
            assert "OSE Signal" in stripe and 'aria-hidden="true"' in stripe, navn
            assert html.index("</header>") < html.index("<main>") < html.index('<footer class="bunnlinje">'), navn
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


def _innhold(html: str, start: str) -> str:
    """Det som står inne i elementet som begynner med start, til den
    tilhørende sluttaggen (gjennomgangen, VG1 og BH7)."""
    i = html.index(start)
    tagg = start[1:].split()[0].rstrip(">")
    dybde, j = 0, i
    for m in re.finditer(rf"<(/?){tagg}\b", html[i:]):
        dybde += -1 if m.group(1) else 1
        if dybde == 0:
            j = i + m.start()
            break
    return html[i:j]


def _synlig(html: str) -> str:
    html = re.sub(r"<style>.*?</style>", "", html, flags=re.DOTALL)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


class TestOversikten:
    """Story 8.0d, PR 2: oversikten fra designforslaget (spesifikasjonen,
    beslutning 11-17, og designregler del 5)."""

    OVERSIKTENE = ("oversikten", "oversikten i demoen")

    def test_kortet_slik_leser_staar_ved_siden_av_overskriften(self, sidene):
        """Beslutning 11: kortet til høyre for overskriften og innledningen,
        og under dem på smal skjerm. Ville feilet med kortet under tabellen."""
        stil = _stil(sidene["oversikten"])
        assert "390px" in _regel(stil, ".topp-del")
        brudd = re.search(
            r"@media \(max-width: (\d+)px\) \{ \.topp-del \{ grid-template-columns: minmax\(0, 1fr\);", stil
        )
        # VG2: kortet går under før de to kolonnene (390 + 36 px og tekst
        # like bred som kortet) blir for brede.
        assert brudd and int(brudd.group(1)) >= 390 + 36 + 390, brudd
        kort = _regel(stil, "section.slik-leser")
        assert "border-radius: 16px" in kort and "border: 1px solid var(--strek)" in kort
        for navn in self.OVERSIKTENE:
            html = sidene[navn]
            topp = html.index('<div class="topp-del">')
            assert (
                topp
                < html.index("<h1")
                < html.index('class="innledning"')
                < html.index('<section class="slik-leser"')
                < html.index('<div class="tabellboks"')
            ), navn
            # VG1: kortet står inne i rutenettet, ikke etter det.
            rutenett = _innhold(html, '<div class="topp-del">')
            assert '<section class="slik-leser"' in rutenett and "<h1" in rutenett, navn

    def test_symbolene_i_kortet_er_skjult_og_ingen_pil_ved_navnet(self, sidene):
        """Beslutning 11: et symbol for signalstyrken, de tre retningssymbolene
        og en musepeker, alle aria-hidden. Ville feilet uten aria-hidden, eller
        med en pil ved navnet (pilene er bare for retning, FR-103)."""
        html = sidene["oversikten"]
        kortet = html.split('<section class="slik-leser"', 1)[1].split("</section>", 1)[0]
        felt = re.findall(r'<span class="symbolfelt"([^>]*)>(.*?)</span><span><strong>', kortet, re.DOTALL)
        assert len(felt) == 3
        for attributter, _ in felt:
            assert 'aria-hidden="true"' in attributter
        brikke, retning, peker = (innhold for _, innhold in felt)
        # Svaret kl. 12:15 (15.10, BH20): en grønn +1 over en rød -1, med en
        # egen klasse, så regelen for brikkene i rammen ikke virker inn.
        assert '<span class="utslagsfelt"><span class="pluss">+1</span><span class="minus">-1</span></span>' in brikke
        assert "brikke" not in kortet
        stil = _stil(html)
        assert "flex-direction: column" in _regel(stil, ".utslagsfelt")
        assert "background: var(--opp)" in _regel(stil, ".utslagsfelt .pluss")
        assert "background: var(--ned)" in _regel(stil, ".utslagsfelt .minus")
        assert "color: var(--hvit)" in _regel(stil, ".utslagsfelt span")
        assert [s for s in "↑↔↓" if s in retning] == list("↑↔↓")
        assert '<svg class="peker"' in peker
        assert not re.search("[←→↑↓↔↗↘↖↙›»]", peker), peker

    def test_hjelpeknappen_er_hvit_paa_blekk_med_oransje_fokus(self, sidene):
        """«?» i stripa og kolonneraden er en hvit sirkel med blekk «?», og
        fokus er oransje som i stripa. Ville feilet med en sort sirkel på
        blekk, eller fokus i blekk på blekk."""
        stil = _stil(sidene["oversikten"])
        farger = _farger(stil)
        blekk = _regel(stil, "header.stripe button.hjelpeknapp, .tabellboks thead button.hjelpeknapp")
        sirkel = re.search(r"radial-gradient\(circle, var\(--([a-z-]+)\) 10\.5px", blekk).group(1)
        tegn = re.search(r"(?<!-)color: var\(--([a-z-]+)\)", blekk).group(1)
        assert _kontrast(farger[sirkel], farger["blekk"]) >= 3.0, sirkel
        assert _kontrast(farger[tegn], farger[sirkel]) >= 4.5, (tegn, sirkel)
        fokus = _regel(
            stil, "header.stripe button.hjelpeknapp:focus-visible, .tabellboks thead button.hjelpeknapp:focus-visible"
        )
        ring = re.findall(r"var\(--([a-z-]+)\) 1[3-6](?:\.5)?px", fokus)
        assert ring and all(_kontrast(farger[f], farger["blekk"]) >= 3.0 for f in ring), ring
        # VG7: ingen outline rundt klikkflaten her heller.
        assert "outline" not in fokus
        # VG3 og BH6: kolonneraden er blekk, med navnene i hvitt, og kortet
        # har svart topp.
        kolonner = _regel(stil, "thead th")
        assert "background: var(--blekk)" in kolonner and "color: var(--hvit)" in kolonner
        assert "border-top-color: var(--blekk)" in _regel(stil, ".tabellboks")
        assert "<thead>" in _innhold(sidene["oversikten"], '<div class="tabellboks"')
        # BH1: den hvite sirkelen gjelder bare kolonneraden i tabellboksen.
        # Tabellen på aksjesiden har lys kolonnerad og en svart sirkel.
        for navn, html in sidene.items():
            for velger in re.findall(r"([^{}]*thead button\.hjelpeknapp[^{}]*)\{", _stil(html)):
                for del_ in velger.split(","):
                    if "thead" in del_:
                        assert del_.strip().startswith(".tabellboks thead"), (navn, del_)
        aksje = sidene["aksjesiden i demoen"]
        assert 'class="tabellboks"' not in aksje
        # Story 8.0d, PR 3: aksjesiden har sjekkort og ingen kolonnerad, og
        # «?» ved Ga står i det første kortet med den svarte sirkelen.
        assert "<thead>" not in aksje and 'popovertarget="hjelp-ga"' in aksje
        stripa = _stripa(sidene["oversikten"])
        assert 'popovertarget="hjelp-hentet"' in stripa

    def test_fokusringen_staar_rundt_sirkelen(self, sidene):
        """Ringen fulgte klikkflaten på 44 px og dekket en del av «Selskap».
        Nå står den 2 px utenfor sirkelen på 22 px og er 3 px bred. Ville
        feilet med vanlig outline på knappen."""
        stil = _stil(sidene["oversikten"])
        fokus = _regel(stil, "button.hjelpeknapp:focus-visible")
        assert "outline: none" in fokus
        stopp = [float(x) for x in re.findall(r"([\d.]+)px", fokus)]
        assert stopp[0] == 10.5 and max(stopp) <= 17, stopp
        assert "var(--blekk) 13.5px, var(--blekk) 16px" in fokus
        assert re.search(
            r"@media \(forced-colors: active\) \{\s*button\.hjelpeknapp:focus-visible \{ outline: 3px solid; \}", stil
        )

    def test_tabellen_ruller_i_sin_egen_boks(self, sidene):
        """Avvik 8: ved 390 px ruller tabellen i en boks, ikke siden. Ville
        feilet uten overflow-x."""
        for navn in self.OVERSIKTENE:
            html = sidene[navn]
            boksen = _regel(_stil(html), ".tabellboks")
            assert "overflow-x: auto" in boksen, navn
            # Den skjulte teksten «skiller seg ut» er position: absolute. Uten
            # en posisjonert boks rundt gjorde den siden 409 px bred ved 390.
            assert "position: relative" in boksen, navn
            # BH7: tabellen står inne i boksen.
            boks = _innhold(html, '<div class="tabellboks" role="region" aria-label="Aksjene" tabindex="0">')
            assert "<table>" in boks and "</table>" in boks, navn

    def test_strekene_og_ringen_i_oransje_bare_ved_2_og_3_av_3(self, sidene):
        """Designregler §3 (14.10): sterk oransje ved 3 av 3, lys oransje ved
        2 av 3, og ingen strek ved 1 og 0. Ville feilet med sterk oransje ved
        2 av 3, eller strek ved 1 av 3."""
        stil = _stil(sidene["oversikten i demoen"])
        assert "inset 4px 0 0 var(--oransje)" in _regel(stil, "tr.utslag.alle td:first-child")
        assert "inset 4px 0 0 var(--lys-oransje)" in _regel(stil, "tr.utslag td:first-child")
        assert len(re.findall(r"inset 4px", stil)) == 2
        # Gjennomgangen: radene uten strek skrives «<tr >».
        sett = set()
        for rad in re.findall(
            r"<tr ?( class=\"[^\"]*\")?>\s*<td class=\"selskap\">(.*?)</tr>", sidene["oversikten i demoen"], re.DOTALL
        ):
            klasse, innhold = rad
            styrke = re.search(r"(\d) av 3</span>", innhold)
            if not styrke:
                continue
            forventet = {"3": ' class="utslag alle"', "2": ' class="utslag"'}.get(styrke.group(1), "")
            assert klasse == forventet, (styrke.group(1), klasse)
            sett.add(styrke.group(1))
        assert {"0", "1", "2", "3"} <= sett, sett

    def test_markeringen_under_tallene_i_overskriften(self, sidene):
        """Designregler §4 (14.10): lys oransje markering fra 60 % av høyden
        under «N av M aksjer», uten fet skrift. Ville feilet uten markeringen.
        Oversikten uten demoen har ingen vurdering i fixturen og heter
        «Markedsoversikt» (test_en_h1_paa_hver_side_og_ikke_i_stripa)."""
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", sidene["oversikten i demoen"], re.DOTALL).group(1)
        assert re.fullmatch(r"<mark>\d+ av \d+ aksjer</mark> skilte seg ut [a-zø]+", h1.strip()), h1
        assert "<strong>" not in h1
        stil = _stil(sidene["oversikten"])
        mark = _regel(stil, "h1.overskrift mark")
        assert "linear-gradient(transparent 60%, var(--lys-oransje) 60%)" in mark
        overskrift = _regel(stil, "h1.overskrift")
        assert '"Newsreader 72"' in overskrift
        # VG5 og BH12: ikke fet, og teksten i blekk, som paret i KONTRAST.
        assert "font-weight: 500" in overskrift and "font-weight" not in mark
        assert "color: var(--blekk)" in overskrift
        assert re.search(
            r'@font-face \{ font-family: "Newsreader 72"; font-weight: 500;[^}]*Newsreader72pt-Medium\.woff', stil
        )

    def test_fargene_fra_beslutningen(self, sidene):
        """VG4: fargene i beslutning 12 (designregler del 5, 14.10). Ville
        feilet med sterk oransje i variabelen for lys oransje, eller det
        gamle grå båndet."""
        stil = _stil(sidene["oversikten"])
        farger = {k: v.upper() for k, v in _farger(stil).items()}
        assert farger["oransje"] == "F2B53A" and farger["lys-oransje"] == "F8DE9C"
        assert farger["baand-ut"] == "FFF6DC" and farger["baand-ut-kant"] == "F0E3BD"
        assert farger["brun"] == "6B4E00" and farger["kolonne-tekst-2"] == "B9BDC5"
        baand = _regel(stil, "tr.del.ut th")
        assert "background: var(--baand-ut)" in baand and "color: var(--brun)" in baand

    def test_tidspunktet_staar_en_gang(self, sidene):
        """BH2 og svar 5: «Oppdatert …» i stripa, og ikke «data hentet» under
        overskriften. Ville feilet med tidspunktet to ganger."""
        for navn in self.OVERSIKTENE:
            html = sidene[navn]
            tid = re.search(r"Oppdatert [a-zø]+ (\d\d\.\d\d kl\. \d\d\.\d\d)", _stripa(html)).group(1)
            assert _synlig(html).count(tid) == 1, navn
            assert "data hentet" not in html, navn
            assert re.search(
                r'<div id="hjelp-hentet" class="hjelpevindu" popover>.*?<h2>Oppdatert</h2>', html, re.DOTALL
            )

    def test_en_h1_paa_hver_side_og_ikke_i_stripa(self, sidene):
        """BH7 og svar 3: «OSE Signal» er logoen i stripa og ikke en
        overskrift. Ville feilet med to h1."""
        for navn, html in sidene.items():
            assert html.count("<h1") == 1, navn
            assert "<h1" not in _stripa(html), navn
        assert "<h1>Siden kan ikke vises</h1>" in sidene["feilsiden"]
        assert '<h1 class="overskrift">Markedsoversikt</h1>' in sidene["tom base"]

    def test_de_smaa_overskriftene_er_i_plex(self, sidene):
        """Utdraget §3: «Slik leser du tabellen» i IBM Plex Sans 12,5 px og 700,
        ikke Newsreader fra regelen for h2 i rammen."""
        regel = _regel(_stil(sidene["oversikten"]), "section.slik-leser h2")
        assert '"IBM Plex Sans"' in regel and "Newsreader" not in regel
        assert "font-size: 12.5px" in regel and "font-weight: 700" in regel and "uppercase" in regel

    def test_baandene_med_antallet_og_grensen_fra_parametre(self, sidene):
        """Designregler del 5 (14.10): antallet i en pille og grensen etter,
        med tallene fra Parametre. Merket «skiller seg ut» er skjult for
        synet, men står i cellen (svar 4)."""
        from signalberegning import Parametre

        terskel = Parametre().terskel
        html = sidene["oversikten i demoen"]
        ut = re.search(
            r'<tr class="del ut"><th[^>]*>Skilte seg ut <span class="antall">(\d+)</span>'
            r' <span class="bak">([^<]+)</span>',
            html,
        )
        assert ut and ut.group(2) == f"signalstyrke {terskel} eller mer"
        assert int(ut.group(1)) == html.count('<span class="merke skjult">skiller seg ut</span>')
        oevrige = re.search(
            r'<tr class="del oevrige"><th[^>]*>Øvrige aksjer <span class="antall">\d+</span>'
            r' <span class="bak">([^<]+)</span>',
            html,
        )
        # Story 8.0d, PR 3: «og N uten signal» når rader uten signal står der.
        uten = html.count('<span class="merke mangler">')
        assert oevrige and oevrige.group(1) == "signalstyrke 0 eller 1" + (f" og {uten} uten signal" if uten else "")
        stil = _stil(html)
        assert "var(--brun)" in _regel(stil, "tr.del.ut .antall")
        skjult = _regel(stil, ".merke.skjult")
        assert "clip-path: inset(50%)" in skjult
        # VG6: skjult for synet, ikke for skjermlesere.
        assert not re.search(r"display:\s*none|visibility:\s*hidden", skjult)
        assert not re.search(r'<span class="merke skjult"[^>]*aria-hidden', html)
        # BH3: ord og tall i båndet står med mellomrom, ikke bare marg.
        uten_tagger = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html))
        assert re.search(r"Skilte seg ut \d+ signalstyrke", uten_tagger)

    def test_ticker_og_bransje_med_symbol_under_navnet(self, sidene):
        """Avvik 11 og utdraget §12: ticker og bransje under navnet, med
        symbolet for hver bransje i lista og i demoen."""
        from demo import DEMOUNIVERS
        from kursdata import AKSJEUNIVERS

        mal = (Path(__file__).resolve().parent.parent / "src" / "templates" / "_bransjer.html").read_text(
            encoding="utf-8"
        )
        symboler = set(re.findall(r"^  '([^']+)': '", mal, re.M))
        assert len(symboler) == 13
        assert {a.sektor for a in AKSJEUNIVERS} | {a.sektor for a in DEMOUNIVERS} <= symboler
        html = sidene["oversikten"]
        assert re.search(
            r'<span class="linje">EQNR · <svg class="bransjesymbol"[^>]*aria-hidden="true"[^>]*>.*?</svg>Energi</span>',
            html,
            re.DOTALL,
        )
        assert '<span class="under">NOK</span>' in html
        assert html.count('class="under"') == 1


class TestSorteringen:
    """Story 8.15: vinklene og fokus i den svarte kolonneraden (svar 4)."""

    def test_vinkelen_er_en_svg_dempet_eller_hvit(self, sidene):
        """Ville feilet med ↑ eller ↓ som vinkel (S8), eller med den dempede
        vinkelen i hvitt (S13)."""
        html = sidene["oversikten"]
        thead = html.split("<thead>", 1)[1].split("</thead>", 1)[0]
        lenker = re.findall(r'<a class="sorter[^"]*"[^>]*>(.*?)</a>', thead, re.DOTALL)
        assert len(lenker) == 4
        for lenke in lenker:
            assert re.search(r'<svg class="vinkel"[^>]*aria-hidden="true"', lenke), lenke
            assert not re.search("[←→↑↓↔↗↘↖↙▲▼]", lenke), lenke
        stil = _stil(html)
        assert "color: var(--kolonne-tekst-2)" in _regel(stil, ".tabellboks thead a.sorter .vinkel")
        assert "color: var(--hvit)" in _regel(stil, ".tabellboks thead a.sorter.valgt .vinkel")
        assert re.search(r"--kolonne-tekst-2:\s*#B9BDC5", stil, re.I)

    def test_fokus_er_oransje_paa_blekk_og_klikkflaten_44_px(self, sidene):
        """Ville feilet med fokus i blekk på blekk (S9)."""
        regel = _regel(_stil(sidene["oversikten"]), ".tabellboks thead a.sorter:focus-visible")
        assert "outline: 3px solid var(--oransje)" in regel
        assert "min-height: 44px" in _regel(_stil(sidene["oversikten"]), ".tabellboks thead a.sorter")

    def test_lenken_standard_rekkefoelge_er_i_blekk(self, sidene):
        """Svar 5: lenken over tabellen har en farge fra designreglene, ikke
        nettleserens blå (designregler §5, ingen farge skrevet fast)."""
        assert "color: var(--blekk)" in _regel(_stil(sidene["oversikten"]), "p.sortert a")

    def test_sorteringen_virker_i_demoen(self, klient, demobase, monkeypatch):
        """FR-411: samme rute og mal i demoen, med merket som før."""
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        html = klient.get("/?sorter=endring&orden=stigende").data.decode("utf-8")
        assert '<p class="sortert">Sortert på endring, stigende, innenfor hver del.' in html
        assert "Eksempeltall" in html


class TestBrikkene:
    """Story 8.0d, PR 3: T, B og I som brikker og retningen i en pille, i
    oversikten og på aksjesiden (utdraget §6, designregler del 5)."""

    KLASSE = {"+1": "pluss", "-1": "minus", "0": "null"}

    def test_brikkene_har_klassen_etter_verdien(self, sidene):
        """Ville feilet hvis brikken for 0 fikk grønt fyll, eller en brikke
        sto uten klasse."""
        # «oversikten» har ingen vurdering i fiksturen, så demoen brukes.
        for navn in ("oversikten i demoen", "aksjesiden i demoen"):
            brikker = re.findall(
                r'<span class="sjekk brikke ([a-z]+)"><abbr title="[a-z]+">[TBI]</abbr> ([+-]?\d)</span>', sidene[navn]
            )
            assert brikker, navn
            for klasse, verdi in brikker:
                assert klasse == self.KLASSE[verdi], (navn, klasse, verdi)
        stil = _stil(sidene["oversikten i demoen"])
        assert "background: var(--opp)" in _regel(stil, ".brikke.pluss")
        assert "background: var(--ned)" in _regel(stil, ".brikke.minus")
        null = _regel(stil, ".brikke.null")
        assert "background: var(--hvit)" in null and "var(--dempet-2)" in null and "var(--strek-2)" in null
        assert "border-radius: 6px" in _regel(stil, ".brikke")

    def test_retningen_staar_i_en_pille(self, sidene):
        """Utdraget §6 og svar 6: pillen har symbolet først og fargen etter
        retningen. «Ukjent» står som tekst uten pille, i Dempet."""
        for navn in ("oversikten", "oversikten i demoen"):
            celler = re.findall(r'<td class="retning">(.*?)</td>', sidene[navn], re.DOTALL)
            assert celler, navn
            for celle in celler:
                assert re.fullmatch(
                    r'<span class="retningspille (opp|ned|blandet|ingen)"><span class="symbol" aria-hidden="true">[↑↓↔–]</span>(Positiv|Negativ|Blandet|Ingen)</span>'
                    r'|<span class="retningstekst ukjent"><span class="symbol" aria-hidden="true">–</span> Ukjent</span>',
                    celle.strip(),
                ), celle
        stil = _stil(sidene["oversikten i demoen"])
        assert "border-radius: 999px" in _regel(stil, ".retningspille")
        assert "background: var(--opp-bakgrunn)" in _regel(stil, ".retningspille.opp")
        assert "var(--dempet)" in _regel(stil, ".retningstekst.ukjent")
        assert "background" not in _regel(stil, ".retningstekst.ukjent")

    def test_to_av_tre_er_en_hvit_pille_og_en_av_tre_er_tekst(self, sidene):
        """Gruppen 14.10 kl. 19:59: hvit pille med kant i blekk ved 2 av 3,
        uten ring. 1 og 0 av 3 står uten pille. Ville feilet hvis «2 av 3»
        mistet pillen."""
        html = sidene["oversikten i demoen"]
        assert '<span class="pille to-av-tre">2 av 3</span>' in html
        assert not re.search(r'<span class="pille[^"]*">[01] av 3</span>', html)
        assert re.search(r'<span class="styrketall">[01] av 3</span>', html)
        assert "oransje" not in _regel(_stil(html), ".pille.to-av-tre")
