"""Story 8.11 (FR-108, FR-412): de ferdige listene, ett sted i koden.

En ferdig liste er en bransje: de opptil 18 aksjene i bransjen med høyest
median omsetning i den siste målingen i omsetning (2.13), bare aksjer som er
målt med et tall og står i lista over Oslo Børs (boersliste). Rekkefølgen
regnes når siden vises, så en ny måling gir nye lister uten at koden endres.
Ingen tall herfra står i koden (regel 16), bare bransjen for hver aksje.

BRANSJE er Claude Codes forslag 08.11, ut fra navnet og det vi vet om
selskapet, sjekket av gruppen: godtatt kl. 22:01 (spørsmål 1), og kl. 22:03
ble VOIM Energi, NOSN, NTG og MVW Industri, PLCAN Shipping og NORTH Finans,
og SCOIN er tatt ut, fordi selskapet er under avvikling. En målt aksje som
ikke står her, kommer ikke i noen liste.
"""

import sqlite3
from dataclasses import dataclass

from valg import BRANSJENE, TAK

# Sjekket av gruppen 08.11 kl. 22:01 og 22:03. Bransjene er de 13 i designregler.md §4.
BRANSJE: dict[str, str] = {
    "AKER": "Finans",
    "STB": "Finans",
    "SUBC": "Energi",
    "BWLPG": "Shipping",
    "KMAR": "Industri",
    "VLCC": "Shipping",
    "OUTLT": "Forbruk",
    "PUBLI": "Eiendom",
    "WWIB": "Shipping",
    "NYKD": "Helse",
    "XPLRA": "Teknologi",
    "VOW": "Industri",
    "ZENA": "Energi",
    "NORSE": "Forbruk",
    "ODFB": "Shipping",
    "SOFTX": "Helse",
    "NOM": "Materialer",
    "LOKO": "Teknologi",
    "ONCIN": "Helse",
    "QEC": "Energi",
    "LIFE": "Helse",
    "TECH": "Teknologi",
    "NBX": "Finans",
    "SCANA": "Industri",
    "STECH": "Energi",
    "ZLNA": "Helse",
    "IDEX": "Teknologi",
    "PPG": "Eiendom",
    "QGAS": "Energi",
    "IOX": "Energi",
    "OMDA": "Helse",
    "KOMPL": "Forbruk",
    "OBSRV": "Helse",
    "HPUR": "Industri",
    "NAVA": "Helse",
    "OTOVO": "Energi",
    "HYPRO": "Energi",
    "JIN": "Shipping",
    "WEST": "Shipping",
    "VOIM": "Energi",
    "STST": "Shipping",
    "NCOD": "Sjømat",
    "VISTN": "Helse",
    "STRO": "Teknologi",
    "PSE": "Energi",
    "MPCES": "Kraft",
    "OCEAN": "Industri",
    "HUDL": "Teknologi",
    "WSTEP": "Teknologi",
    "LYTIX": "Helse",
    "PLGC": "Finans",
    "NEXT": "Teknologi",
    "NORTH": "Finans",
    "KRAB": "Finans",
    "PLCAN": "Shipping",
    "VVL": "Finans",
    "ITERA": "Teknologi",
    "KLDVK": "Sjømat",
    "PROXI": "Sjømat",
    "HKY": "Forbruk",
    "SOGN": "Finans",
    "INDCT": "Teknologi",
    "SKAND": "Kraft",
    "NOFIN": "Finans",
    "ROMER": "Finans",
    "SAGA": "Finans",
    "NTG": "Industri",
    "TINDE": "Finans",
    "KING": "Sjømat",
    "OSUN": "Energi",
    "POLAR": "Materialer",
    "LUMI": "Forbruk",
    "MVW": "Industri",
    "HGSB": "Finans",
    "HSPG": "Finans",
    "MELG": "Finans",
    "ININ": "Industri",
    "NOSN": "Industri",
    "REFL": "Energi",
    "SB68": "Finans",
    "TRSB": "Finans",
    "INIFY": "Helse",
    "NISB": "Finans",
    "SDSD": "Energi",
    "ROM": "Eiendom",
    "HYN": "Energi",
    "RIVER": "Teknologi",
    # Demoen: to av de oppdiktede selskapene som er målt (demo.DEMOMAALT).
    "HVLK": "Kraft",
    "NRDE": "Eiendom",
}
assert set(BRANSJE.values()) <= set(BRANSJENE)


@dataclass(frozen=True)
class Ferdigaksje:
    symbol: str
    navn: str
    median: float


def lister(tilkobling: sqlite3.Connection | None) -> dict[str, list[Ferdigaksje]]:
    """{bransje: opptil TAK aksjer}, med høyest omsetning først, i
    rekkefølgen bransjene har i BRANSJENE. En bransje uten målte aksjer har
    ingen liste. Bare lesing. Mangler tabellene, er det ingen lister."""
    if tilkobling is None:
        return {}
    try:
        rader = tilkobling.execute(
            "SELECT o.symbol, b.navn, o.median_omsetning FROM omsetning o JOIN boersliste b ON b.kode = o.symbol "
            "WHERE o.maalt = (SELECT max(maalt) FROM omsetning WHERE symbol = o.symbol) "
            "AND o.median_omsetning IS NOT NULL ORDER BY o.median_omsetning DESC, o.symbol"
        ).fetchall()
    except sqlite3.Error:
        return {}
    etter_bransje: dict[str, list[Ferdigaksje]] = {}
    for symbol, navn, median in rader:
        bransje = BRANSJE.get(symbol)
        if bransje is None:
            continue
        liste = etter_bransje.setdefault(bransje, [])
        if len(liste) < TAK:
            liste.append(Ferdigaksje(symbol, navn, float(median)))
    return {b: etter_bransje[b] for b in BRANSJENE if b in etter_bransje}
