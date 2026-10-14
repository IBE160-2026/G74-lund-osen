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
                k = next(k for k in range(n) if begynn[k] <= c <= slutt[k])
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
        funksjoner = _funksjoner(_tabeller((FONTS / fil).read_bytes())["GSUB"])
        if "pnum" in funksjoner:
            assert "tnum" in funksjoner

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
