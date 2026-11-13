"""Story 3.4h: sidene for de 15 oppdiktede selskapene i demoen.

Tegningene og bobler.json i static/investorsider/ er kopier av filene i
docs/bilder/investorsider/, godkjent 24.10 kl. 13:43, og en test krever at
de er byte for byte like. Skriften per selskap er tabellen i LESMEG.md der.
Ingenting hentes fra nettet (AD-2), og siden har ingen kurs, ingen endring
og ingen tekst om kjøp eller salg (NFR-06).
"""

import json
import re
from dataclasses import dataclass
from functools import cache
from html import unescape
from pathlib import Path

from demo import DEMOUNIVERS

MAPPE = Path(__file__).resolve().parent / "static" / "investorsider"
# Tegningen er 560 × 400 px, og plassen i bobler.json er piksler fra
# tegningens øvre venstre hjørne (LESMEG.md).
BREDDE = 560
HOYDE = 400


@dataclass(frozen=True)
class Skrift:
    """Skriften i navnet og symbolet i logoen. store: skriften viser navnet
    med store bokstaver, men det står med stor forbokstav i HTML-en
    (gruppens svar 24.10 kl. 13:03). sperring er i px."""

    familie: str
    vekt: int
    kursiv: bool = False
    store: bool = False
    sperring: int = 0
    kapiteler: bool = False


# Familiene har hver sin klasse i stil.css, så malen ikke skriver navnet på
# skriften.
KLASSER = {
    "Inter Display": "skrift-inter",
    "Lora": "skrift-lora",
    "Liberation Mono": "skrift-mono",
    "IBM Plex Sans": "skrift-plex",
    "Newsreader": "skrift-newsreader",
    "Newsreader 72": "skrift-newsreader-72",
}

# Tabellen «De 15» i docs/bilder/investorsider/LESMEG.md.
SKRIFTER = {
    "BRFE": Skrift("Inter Display", 900, store=True),
    "HVDO": Skrift("Lora", 700),
    "NLYS": Skrift("Inter Display", 200, store=True, sperring=3),
    "SLVP": Skrift("Newsreader", 600),
    "FJSB": Skrift("Lora", 500, kapiteler=True),
    "TRHF": Skrift("IBM Plex Sans", 600),
    "VRDS": Skrift("Liberation Mono", 700),
    "KVST": Skrift("Lora", 400, store=True, sperring=4),
    "JGRD": Skrift("IBM Plex Sans", 500),
    "BLGT": Skrift("Inter Display", 800, kursiv=True),
    "LSTF": Skrift("Liberation Mono", 400, store=True),
    "SGNT": Skrift("Inter Display", 700),
    "LKSV": Skrift("Lora", 600, kursiv=True),
    "TROY": Skrift("IBM Plex Sans", 400, store=True, sperring=2),
    "MTFJ": Skrift("Newsreader 72", 500),
}


@dataclass(frozen=True)
class Demoside:
    symbol: str
    navn: str
    bransje: str
    skrift: Skrift
    slagord: str
    # Teksten i <desc> i tegningen, som alt (spørsmål 6).
    beskrivelse: str
    tegning: str
    # Boblen i prosent av tegningen, så den følger tegningen (del C).
    venstre: float
    topp: float
    bredde: float
    # Halen i tegningens piksler, til points= i en SVG med samme mål.
    flate: str
    strek: str

    @property
    def klasser(self) -> str:
        s = self.skrift
        return " ".join(
            [KLASSER[s.familie]]
            + (["kursiv"] if s.kursiv else [])
            + (["store"] if s.store else [])
            + (["kapiteler"] if s.kapiteler else [])
        )

    @property
    def stil(self) -> str:
        return f"--vekt: {self.skrift.vekt}; --sperring: {self.skrift.sperring}px;"

    @property
    def boblestil(self) -> str:
        return f"--venstre: {self.venstre:.4f}%; --topp: {self.topp:.4f}%; --bredde: {self.bredde:.4f}%;"


@cache
def _bobler() -> dict:
    return json.loads((MAPPE / "bobler.json").read_text(encoding="utf-8"))["selskaper"]


def _beskrivelse(fil: Path) -> str:
    treff = re.search(r"<desc[^>]*>(.*?)</desc>", fil.read_text(encoding="utf-8"), re.DOTALL)
    return " ".join(unescape(treff.group(1)).split()) if treff else ""


def _punkter(punkter: list[list[float]]) -> str:
    return " ".join(f"{x:g},{y:g}" for x, y in punkter)


def demoside(symbol: str) -> Demoside | None:
    """Siden for et av de 15 i demoen, eller None for et annet symbol."""
    aksje = next((a for a in DEMOUNIVERS if a.symbol == symbol), None)
    if aksje is None:
        return None
    boble = _bobler()[symbol]
    fil = MAPPE / f"{symbol.lower()}.svg"
    return Demoside(
        symbol=aksje.symbol,
        navn=aksje.navn,
        bransje=aksje.sektor,
        skrift=SKRIFTER[symbol],
        slagord=boble["slagord"],
        beskrivelse=_beskrivelse(fil),
        tegning=f"/static/investorsider/{fil.name}",
        venstre=100 * boble["boble"]["venstre"] / BREDDE,
        topp=100 * boble["boble"]["topp"] / HOYDE,
        bredde=100 * boble["boble"]["bredde"] / BREDDE,
        flate=_punkter(boble["hale"]["flate"]),
        strek=_punkter(boble["hale"]["strek"]),
    )


# Story 8.26 (gruppens svar 11.11 kl. 20:28, tillegg 12): siden for «Åpne
# eodhd.com» i demoen, med tegningen i static/demo/ og boblen etter det første
# forslaget i spesifikasjonen. Plassen er piksler i tegningen, som i bobler.json.
EODHD_BOBLE = "Nøkkelen? Den ligger under matta, sammen med de 20 kallene."
EODHD_TEGNING = Path(__file__).resolve().parent / "static" / "demo" / "eodhd.svg"


@dataclass(frozen=True)
class EodhdDemoside:
    boble: str
    beskrivelse: str
    venstre: float
    topp: float
    bredde: float
    flate: str
    strek: str

    @property
    def boblestil(self) -> str:
        return f"--venstre: {self.venstre:.4f}%; --topp: {self.topp:.4f}%; --bredde: {self.bredde:.4f}%;"


def eodhd_demoside() -> EodhdDemoside:
    """Siden knappen i steg 1 går til i demoen."""
    return EodhdDemoside(
        boble=EODHD_BOBLE,
        beskrivelse=_beskrivelse(EODHD_TEGNING),
        venstre=100 * 284 / BREDDE,
        topp=100 * 4 / HOYDE,
        bredde=100 * 270 / BREDDE,
        flate=_punkter([[378, 112], [396, 160], [414, 112]]),
        strek=_punkter([[378, 116.3], [396, 160], [414, 116.3]]),
    )
