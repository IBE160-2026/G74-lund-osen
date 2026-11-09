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
from datetime import date

from omsetningsregning import regn_ut, vindu
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


def _aksjene_i_lista(tilkobling: sqlite3.Connection) -> tuple[set[str], list[tuple[str, str, float, str]]]:
    """Story 8.11b (svaret 08.11 kl. 22:06): aksjene appen foelger eller har
    fulgt, de 15 og de egne, maales ikke i 2.13. Medianen regnes her, naar
    siden vises, av kursene i basen med samme vindu og utregning som 2.13
    (omsetningsregning), til den siste dagen med kurser i basen. Gjennomgangen
    (ECH1): ogsaa en aksje som er tatt ut av lista, saa den ikke faller ut av
    bransjelistene foer 2.13 har maalt den. Bransjen er den i aksje, og bare
    aksjer som staar i boersliste er med. Gir symbolene som er regnet her, og
    [(symbol, navn, median, bransje)] for dem som fikk en median."""
    # Gjennomgangen av 8.11b (BH4, ECH4): den siste dagen leses med
    # primaernoekkelen (symbol, dato) for hver aksje, ikke ved aa lese hele kurs.
    siste = tilkobling.execute(
        "SELECT max(m) FROM (SELECT (SELECT max(dato) FROM kurs WHERE symbol = a.symbol) AS m FROM aksje a)"
    ).fetchone()[0]
    try:
        fra, til = vindu(date.fromisoformat(siste))
    except (TypeError, ValueError):
        # Ingen kurser, eller en dato som ikke kan leses (BH5): ingen lister herfra.
        return set(), []
    dag = til.isoformat()
    lista = tilkobling.execute(
        "SELECT a.symbol, b.navn, a.sektor, (a.inn IS NULL OR a.inn <= ?) AND (a.ut IS NULL OR a.ut > ?) "
        "FROM aksje a JOIN boersliste b ON b.kode = a.symbol",
        (dag, dag),
    ).fetchall()
    # Gjennomgangen av 8.11b (BH4, ECH4): kursene i vinduet for alle aksjene
    # i én spoerring, ikke én per aksje. CROSS JOIN holder rekkefoelgen, saa
    # kurs leses med primaernoekkelen (symbol, dato) for hver aksje og ikke
    # gaas gjennom i sin helhet (gjennomgangen av 9.10, ECH2).
    kursene: dict[str, list[dict]] = {}
    for symbol, dato, slutt, volum in tilkobling.execute(
        "SELECT k.symbol, k.dato, k.slutt, k.volum FROM aksje a JOIN boersliste b ON b.kode = a.symbol "
        "CROSS JOIN kurs k ON k.symbol = a.symbol WHERE k.dato BETWEEN ? AND ?",
        (fra.isoformat(), til.isoformat()),
    ):
        kursene.setdefault(symbol, []).append({"date": dato, "close": slutt, "volume": volum})
    ut = []
    for symbol, navn, sektor, _ in lista:
        median = regn_ut(symbol, kursene.get(symbol, []), fra, til).median
        if median is not None:
            ut.append((symbol, navn, median, sektor))
    # En aksje i lista bruker aldri en eldre maaling (BH3); en som er tatt ut
    # og ikke har kurser i vinduet, kan ha en nyere maaling fra 2.13.
    return {symbol for symbol, _, _, i_lista in lista if i_lista} | {symbol for symbol, *_ in ut}, ut


def lister(tilkobling: sqlite3.Connection | None) -> dict[str, list[Ferdigaksje]]:
    """{bransje: opptil TAK aksjer}, med høyest omsetning først, i
    rekkefølgen bransjene har i BRANSJENE. En bransje uten målte aksjer har
    ingen liste. Bare lesing. Mangler tabellene, er det ingen lister.
    Story 8.11b: aksjene i lista er med, med medianen regnet av kursene."""
    if tilkobling is None:
        return {}
    try:
        maalte = tilkobling.execute(
            "SELECT o.symbol, b.navn, o.median_omsetning FROM omsetning o JOIN boersliste b ON b.kode = o.symbol "
            "WHERE o.maalt = (SELECT max(maalt) FROM omsetning WHERE symbol = o.symbol) "
            "AND o.median_omsetning IS NOT NULL"
        ).fetchall()
        regnet, i_lista = _aksjene_i_lista(tilkobling)
        sektorer = dict(tilkobling.execute("SELECT symbol, sektor FROM aksje").fetchall())
    except sqlite3.Error:
        return {}
    # Story 8.11b: for en aksje appen har kurser for, gjelder medianen regnet
    # av kursene, ogsaa om den har en eldre maaling i omsetning (spoersmaal 4).
    # Gjennomgangen (BH3, VG1): ogsaa naar den ikke fikk en median i vinduet.
    # En maalt aksje appen har fulgt, men som ikke staar i BRANSJE (de 15),
    # faar bransjen i aksje (gjennomgangen, ECH1, sektorer over).
    rader = [(s, n, float(m), BRANSJE.get(s) or sektorer.get(s)) for s, n, m in maalte if s not in regnet]
    rader += [(s, n, float(m), b) for s, n, m, b in i_lista]
    rader.sort(key=lambda r: (-r[2], r[0]))
    etter_bransje: dict[str, list[Ferdigaksje]] = {}
    for symbol, navn, median, bransje in rader:
        if bransje not in BRANSJENE:
            continue
        liste = etter_bransje.setdefault(bransje, [])
        if len(liste) < TAK:
            liste.append(Ferdigaksje(symbol, navn, float(median)))
    return {b: etter_bransje[b] for b in BRANSJENE if b in etter_bransje}
