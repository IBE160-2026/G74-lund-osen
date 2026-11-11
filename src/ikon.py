"""Ikonet til appen - story 3.6 (del C, gruppens svar 10.11 kl. 14:07).

De tre søylene fra logoen i toppen (_ramme.html), hvite og den høyeste
oransje, på blekk, som stripa. Filene lages med bare standardbiblioteket
(zlib og struct), uten nye avhengigheter i appen, og ligger i src/static:

- ikon.svg, som fanen i nettleseren bruker
- ikon-<n>.png i de vanlige størrelsene (IKON_STOERRELSER)
- ikon.ico med 16, 32, 48 og 256 px, til snarveien i Windows

Kjør `uv run python src/ikon.py` for å lage filene på nytt. Tegningen er
den samme hver gang, så filene i repoet er byte for byte det modulen lager
(tests/test_ikonet_og_snarveien_3_6.py).
"""

import struct
import zlib
from pathlib import Path

STATIC = Path(__file__).resolve().parent / "static"

# Logoen i _ramme.html: viewBox 0 0 28 24, (x, y, bredde, høyde, hjørne, høy).
SOEYLENE = (
    (1.0, 14.0, 6.5, 9.0, 1.6, False),
    (10.75, 8.0, 6.5, 15.0, 1.6, False),
    (20.5, 1.0, 6.5, 22.0, 1.6, True),
)
LOGO_BREDDE, LOGO_HOEYDE = 28.0, 24.0
# Fargene fra stil.css: --blekk, --hvit og --oransje.
BLEKK = (0x16, 0x18, 0x1D)
HVIT = (0xFF, 0xFF, 0xFF)
ORANSJE = (0xF2, 0xB5, 0x3A)
# Bakgrunnen er et avrundet kvadrat, og logoen står midt i med luft rundt.
HJOERNE = 0.18
LUFT = 0.16
IKON_STOERRELSER = (16, 32, 48, 180, 192, 512)
ICO_STOERRELSER = (16, 32, 48, 256)
# Hvor mange punkter per piksel i hver retning når kantene glattes.
UTJEVNING = 4


def _inni_avrundet(px: float, py: float, x: float, y: float, b: float, h: float, r: float) -> bool:
    if not (x <= px <= x + b and y <= py <= y + h):
        return False
    cx = min(max(px, x + r), x + b - r)
    cy = min(max(py, y + r), y + h - r)
    return (px - cx) ** 2 + (py - cy) ** 2 <= r * r


def _farge_i(px: float, py: float, n: int) -> tuple[int, int, int, int]:
    """Fargen i punktet (px, py) på et ikon som er n piksler bredt."""
    if not _inni_avrundet(px, py, 0, 0, n, n, HJOERNE * n):
        return (0, 0, 0, 0)
    skala = n * (1 - 2 * LUFT) / LOGO_BREDDE
    x0 = (n - LOGO_BREDDE * skala) / 2
    y0 = (n - LOGO_HOEYDE * skala) / 2
    for x, y, b, h, r, hoey in SOEYLENE:
        if _inni_avrundet(px, py, x0 + x * skala, y0 + y * skala, b * skala, h * skala, r * skala):
            return (*(ORANSJE if hoey else HVIT), 255)
    return (*BLEKK, 255)


def tegn(n: int) -> bytes:
    """RGBA-pikslene for et ikon på n × n, rad for rad, med glattede kanter."""
    rader = bytearray()
    steg = 1 / UTJEVNING
    for j in range(n):
        for i in range(n):
            sum_ = [0, 0, 0, 0]
            for dj in range(UTJEVNING):
                for di in range(UTJEVNING):
                    r, g, b, a = _farge_i(i + (di + 0.5) * steg, j + (dj + 0.5) * steg, n)
                    sum_[0] += r * a
                    sum_[1] += g * a
                    sum_[2] += b * a
                    sum_[3] += a
            a = sum_[3]
            if a == 0:
                rader += bytes(4)
            else:
                rader += bytes((round(sum_[0] / a), round(sum_[1] / a), round(sum_[2] / a), round(a / UTJEVNING**2)))
    return bytes(rader)


def png(n: int) -> bytes:
    """Ikonet som PNG, n × n, RGBA, uten tidsstempel, så det blir likt hver gang."""
    piksler = tegn(n)
    raa = b"".join(b"\x00" + piksler[j * n * 4 : (j + 1) * n * 4] for j in range(n))

    def bit(art: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + art + data + struct.pack(">I", zlib.crc32(art + data) & 0xFFFFFFFF)

    return (
        b"\x89PNG\r\n\x1a\n"
        + bit(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 6, 0, 0, 0))
        + bit(b"IDAT", zlib.compress(raa, 9))
        + bit(b"IEND", b"")
    )


def ico() -> bytes:
    """ikon.ico med PNG-bildene i ICO_STOERRELSER (Windows Vista og nyere)."""
    bildene = [png(n) for n in ICO_STOERRELSER]
    hode = struct.pack("<HHH", 0, 1, len(bildene))
    plass = 6 + 16 * len(bildene)
    oppslag = b""
    for n, data in zip(ICO_STOERRELSER, bildene, strict=True):
        oppslag += struct.pack("<BBBBHHII", n % 256, n % 256, 0, 0, 1, 32, len(data), plass)
        plass += len(data)
    return hode + oppslag + b"".join(bildene)


def svg() -> str:
    """Ikonet som SVG, med de samme søylene som logoen."""
    n = 64
    skala = n * (1 - 2 * LUFT) / LOGO_BREDDE
    x0 = (n - LOGO_BREDDE * skala) / 2
    y0 = (n - LOGO_HOEYDE * skala) / 2

    def tall(v: float) -> str:
        return f"{v:.3f}".rstrip("0").rstrip(".")

    hex_ = "#{:02X}{:02X}{:02X}".format
    deler = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}">',
        f'<rect width="{n}" height="{n}" rx="{tall(HJOERNE * n)}" fill="{hex_(*BLEKK)}"/>',
    ]
    for x, y, b, h, r, hoey in SOEYLENE:
        deler.append(
            f'<rect x="{tall(x0 + x * skala)}" y="{tall(y0 + y * skala)}" width="{tall(b * skala)}" '
            f'height="{tall(h * skala)}" rx="{tall(r * skala)}" fill="{hex_(*(ORANSJE if hoey else HVIT))}"/>'
        )
    deler.append("</svg>")
    # Én linje uten linjeskift, så fila er lik byte for byte også med autocrlf i Windows.
    return "".join(deler)


def filene() -> dict[str, bytes]:
    """Navnet i src/static og innholdet for hver fil."""
    ut = {"ikon.svg": svg().encode("utf-8"), "ikon.ico": ico()}
    for n in IKON_STOERRELSER:
        ut[f"ikon-{n}.png"] = png(n)
    return ut


def main() -> None:
    for navn, data in filene().items():
        (STATIC / navn).write_bytes(data)
        print(f"{navn}: {len(data)} byte")


if __name__ == "__main__":
    main()
