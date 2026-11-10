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

Story 8.22 (gruppens svar 10.11 kl. 13:38, 14:43 og 15:22): BRANSJE har nå
alle aksjene i lista over Oslo Børs, utenom MULTI (en fusjon gjør det usikkert
hva som skjer) og SCOIN, og brukeren velger ikke bransjen selv. Kontrollsjekken
står i bransjesjekk-2026-11-10.md.
"""

import sqlite3
from dataclasses import dataclass
from datetime import date

from omsetningsregning import regn_ut, vindu
from valg import BRANSJENE, TAK

# Story 8.22 (gruppens svar 10.11 kl. 13:38, 14:43 og 15:22): alle aksjene i
# lista over Oslo Børs, utenom MULTI og SCOIN, med bransjen fra kontrollsjekken
# i bransjesjekk-2026-11-10.md, sortert etter tickeren. De 87 som ble sjekket
# 08.11 kl. 22:01 og 22:03, står med samme bransje som da. Bransjene er de 13
# i designregler.md §4.
BRANSJE: dict[str, str] = {
    "2020": "Shipping",
    "5PG": "Forbruk",
    "AASB": "Finans",
    "ABG": "Finans",
    "ABS": "Helse",
    "ABTEC": "Konsum",
    "ACED": "Teknologi",
    "ACR": "Finans",
    "ADS": "Shipping",
    "AFG": "Industri",
    "AFISH": "Sjømat",
    "AFK": "Finans",
    "AGLX": "Materialer",
    "AIX": "Teknologi",
    "AKAST": "Energi",
    "AKBM": "Konsum",
    "AKER": "Finans",
    "AKOBO": "Materialer",
    "AKRBP": "Energi",
    "AKSO": "Energi",
    "AKVA": "Industri",
    "ALNG": "Shipping",
    "ANDF": "Sjømat",
    "APR": "Teknologi",
    "AQUA": "Energi",
    "ARCH": "Energi",
    "ARR": "Teknologi",
    "ASA": "Sjømat",
    "ATEA": "Teknologi",
    "AURG": "Finans",
    "AUSS": "Sjømat",
    "AUTO": "Industri",
    "AZT": "Helse",
    "B2I": "Finans",
    "BAKKA": "Sjømat",
    "BALT": "Eiendom",
    "BARRA": "Sjømat",
    "BCS": "Materialer",
    "BEWI": "Materialer",
    "BIEN": "Finans",
    "BINT": "Finans",
    "BMA": "Industri",
    "BNOR": "Energi",
    "BOHUS": "Forbruk",
    "BONHR": "Kraft",
    "BOR": "Shipping",
    "BORR": "Energi",
    "BOUV": "Teknologi",
    "BRG": "Materialer",
    "BRUT": "Finans",
    "BSP": "Eiendom",
    "BWE": "Energi",
    "BWLPG": "Shipping",
    "BWO": "Energi",
    "CADLR": "Energi",
    "CAMBI": "Industri",
    "CAPSL": "Industri",
    "CAPT": "Shipping",
    "CAVEN": "Energi",
    "CLOUD": "Kraft",
    "CMBTO": "Shipping",
    "CODE": "Finans",
    "CONTX": "Helse",
    "COSH": "Energi",
    "CRNA": "Helse",
    "CYVIZ": "Teknologi",
    "DDRIL": "Energi",
    "DELIA": "Teknologi",
    "DFENS": "Industri",
    "DNB": "Finans",
    "DNO": "Energi",
    "DOFG": "Energi",
    "DSRT": "Materialer",
    "DVD": "Energi",
    "EAM": "Kraft",
    "EIOF": "Energi",
    "ELABS": "Teknologi",
    "ELK": "Materialer",
    "ELMRA": "Kraft",
    "ELO": "Materialer",
    "ELOO": "Materialer",
    "ENDUR": "Industri",
    "ENERG": "Kraft",
    "ENH": "Energi",
    "ENSU": "Teknologi",
    "ENTRA": "Eiendom",
    "ENVIP": "Industri",
    "EPR": "Forbruk",
    "EQNR": "Energi",
    "EQVA": "Industri",
    "EXTX": "Helse",
    "FFSB": "Finans",
    "FRO": "Shipping",
    "GEM": "Materialer",
    "GENO": "Industri",
    "GENT": "Helse",
    "GEOS": "Energi",
    "GIGA": "Sjømat",
    "GJF": "Finans",
    "GKP": "Energi",
    "GOD": "Industri",
    "GOLDR": "Materialer",
    "GRONG": "Finans",
    "GSF": "Sjømat",
    "GYL": "Forbruk",
    "HAFNI": "Shipping",
    "HAUTO": "Shipping",
    "HAV": "Industri",
    "HAVI": "Energi",
    "HBC": "Konsum",
    "HDLY": "Teknologi",
    "HELG": "Finans",
    "HERMA": "Finans",
    "HEX": "Industri",
    "HGSB": "Finans",
    "HKY": "Forbruk",
    "HPUR": "Industri",
    "HSHP": "Shipping",
    "HSPG": "Finans",
    "HUDL": "Teknologi",
    "HUNT": "Shipping",
    "HYN": "Energi",
    "HYPRO": "Energi",
    "IDEX": "Teknologi",
    "INDCT": "Teknologi",
    "INIFY": "Helse",
    "ININ": "Industri",
    "INSTA": "Finans",
    "IOX": "Energi",
    "ISLAX": "Sjømat",
    "ITERA": "Teknologi",
    "IWS": "Energi",
    "JACK": "Energi",
    "JAREN": "Finans",
    "JIN": "Shipping",
    "KCC": "Shipping",
    "KID": "Forbruk",
    "KING": "Sjømat",
    "KIT": "Industri",
    "KLDVK": "Sjømat",
    "KMAR": "Industri",
    "KOA": "Forbruk",
    "KOG": "Industri",
    "KOMPL": "Forbruk",
    "KRAB": "Finans",
    "LIFE": "Helse",
    "LINK": "Telekom",
    "LOKO": "Teknologi",
    "LSG": "Sjømat",
    "LUMI": "Forbruk",
    "LYTIX": "Helse",
    "MAS": "Sjømat",
    "MDATA": "Teknologi",
    "MEDI": "Helse",
    "MELG": "Finans",
    "MGN": "Kraft",
    "MING": "Finans",
    "MORG": "Finans",
    "MORLD": "Energi",
    "MOWI": "Sjømat",
    "MPCC": "Shipping",
    "MPCES": "Kraft",
    "MVW": "Industri",
    "NAPA": "Teknologi",
    "NAS": "Forbruk",
    "NAVA": "Helse",
    "NBX": "Finans",
    "NCOD": "Sjømat",
    "NEL": "Energi",
    "NEXT": "Teknologi",
    "NHY": "Materialer",
    "NISB": "Finans",
    "NKR": "Industri",
    "NOAP": "Sjømat",
    "NOD": "Teknologi",
    "NOFIN": "Finans",
    "NOHAL": "Sjømat",
    "NOL": "Energi",
    "NOM": "Materialer",
    "NONG": "Finans",
    "NORAM": "Energi",
    "NORBT": "Teknologi",
    "NORCO": "Industri",
    "NORDH": "Helse",
    "NORSE": "Forbruk",
    "NORTH": "Finans",
    "NOSN": "Industri",
    "NRC": "Industri",
    "NSKOG": "Materialer",
    "NTG": "Industri",
    "NTI": "Industri",
    "NYKD": "Helse",
    "OBSRV": "Helse",
    "OCEAN": "Industri",
    "ODF": "Shipping",
    "ODFB": "Shipping",
    "ODL": "Energi",
    "OET": "Shipping",
    "OKEA": "Energi",
    "OMC": "Shipping",
    "OMDA": "Helse",
    "ONCIN": "Helse",
    "ORK": "Konsum",
    "OSUN": "Energi",
    "OTEC": "Teknologi",
    "OTL": "Energi",
    "OTOVO": "Energi",
    "OUTLT": "Forbruk",
    "PARB": "Finans",
    "PEN": "Energi",
    "PEXIP": "Teknologi",
    "PHO": "Helse",
    "PLCAN": "Shipping",
    "PLGC": "Finans",
    "PLSV": "Energi",
    "PLT": "Teknologi",
    "PNOR": "Energi",
    "POL": "Forbruk",
    "POLAR": "Materialer",
    "PPG": "Eiendom",
    "PROT": "Finans",
    "PROXI": "Sjømat",
    "PRS": "Energi",
    "PSE": "Energi",
    "PUBLI": "Eiendom",
    "PYRUM": "Materialer",
    "QEC": "Energi",
    "QGAS": "Energi",
    "REACH": "Energi",
    "REFL": "Energi",
    "RING": "Finans",
    "RIVER": "Teknologi",
    "ROGS": "Finans",
    "ROM": "Eiendom",
    "ROMER": "Finans",
    "SAGA": "Finans",
    "SALM": "Sjømat",
    "SALME": "Sjømat",
    "SATS": "Forbruk",
    "SB1NO": "Finans",
    "SB68": "Finans",
    "SBNOR": "Finans",
    "SBO": "Eiendom",
    "SCANA": "Industri",
    "SCATC": "Kraft",
    "SDSD": "Energi",
    "SEA1": "Energi",
    "SKAND": "Kraft",
    "SKUE": "Finans",
    "SMOP": "Teknologi",
    "SNI": "Shipping",
    "SNM": "Energi",
    "SNOR": "Finans",
    "SNTIA": "Industri",
    "SOAG": "Finans",
    "SOFF": "Energi",
    "SOFTX": "Helse",
    "SOGN": "Finans",
    "SOMA": "Energi",
    "SPOG": "Finans",
    "SPOL": "Finans",
    "STB": "Finans",
    "STECH": "Energi",
    "STRO": "Teknologi",
    "STST": "Shipping",
    "SUBC": "Energi",
    "SWON": "Teknologi",
    "TECH": "Teknologi",
    "TEKNA": "Industri",
    "TEL": "Telekom",
    "TGS": "Energi",
    "TINDE": "Finans",
    "TOM": "Industri",
    "TRMED": "Helse",
    "TRSB": "Finans",
    "VAR": "Energi",
    "VEI": "Industri",
    "VEND": "Forbruk",
    "VISTN": "Helse",
    "VLCC": "Shipping",
    "VOIM": "Energi",
    "VOW": "Industri",
    "VTURA": "Energi",
    "VVL": "Finans",
    "WAWI": "Shipping",
    "WEST": "Shipping",
    "WSTEP": "Teknologi",
    "WWI": "Shipping",
    "WWIB": "Shipping",
    "XPLRA": "Teknologi",
    "YAR": "Materialer",
    "ZAL": "Teknologi",
    "ZAP": "Industri",
    "ZENA": "Energi",
    "ZLNA": "Helse",
    # Demoen: to av de oppdiktede selskapene som er målt (demo.DEMOMAALT).
    "HVLK": "Kraft",
    "NRDE": "Eiendom",
}
# Story 8.22 (spørsmål 2): de tre andre oppdiktede selskapene på «Demo Børs»
# (demo.DEMOBOERSEN), med bransjen som står i navnet. Ingen av dem er en
# ticker på Oslo Børs (CSV-fila 10.11).
DEMOBRANSJE: dict[str, str] = {"SKRH": "Helse", "TNDT": "Teknologi", "VKVF": "Forbruk"}
assert set(BRANSJE.values()) <= set(BRANSJENE)
assert set(DEMOBRANSJE.values()) <= set(BRANSJENE) and not set(DEMOBRANSJE) & set(BRANSJE)


def fast_bransje(kode: str) -> str | None:
    """Story 8.22: bransjen fra kontrollsjekken (BRANSJE), eller fra
    DEMOBRANSJE i demoen. Leses ved hvert kall, så en test kan bytte tabellen."""
    return BRANSJE.get(kode) or DEMOBRANSJE.get(kode)


def bransjen(tilkobling: sqlite3.Connection | None, kode: str) -> str | None:
    """Story 8.22 (spørsmål 1): bransjen en aksje følges med. Den faste
    bransjen, ellers bransjen i aksje for en aksje appen følger eller har
    fulgt (de 15 i demoen, en aksje som er tatt ut). None: aksjen kan ikke
    følges. Brukeren velger den aldri selv (svaret 10.11 kl. 13:38)."""
    fast = fast_bransje(kode)
    if fast is not None or tilkobling is None:
        return fast
    try:
        rad = tilkobling.execute("SELECT sektor FROM aksje WHERE symbol = ?", (kode,)).fetchone()
    except sqlite3.Error:
        return None
    return rad[0] if rad is not None and rad[0] in BRANSJENE else None


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
    # Story 8.22: den faste bransjen foerst, ogsaa for aksjene i lista (spoersmaal 3).
    rader = [(s, n, float(m), fast_bransje(s) or sektorer.get(s)) for s, n, m in maalte if s not in regnet]
    rader += [(s, n, float(m), fast_bransje(s) or b) for s, n, m, b in i_lista]
    rader.sort(key=lambda r: (-r[2], r[0]))
    etter_bransje: dict[str, list[Ferdigaksje]] = {}
    for symbol, navn, median, bransje in rader:
        if bransje not in BRANSJENE:
            continue
        liste = etter_bransje.setdefault(bransje, [])
        if len(liste) < TAK:
            liste.append(Ferdigaksje(symbol, navn, float(median)))
    return {b: etter_bransje[b] for b in BRANSJENE if b in etter_bransje}


def medianene(tilkobling: sqlite3.Connection | None) -> dict[str, tuple[float | None, date | None]]:
    """Story 8.11c (spoersmaal 9 i 8.11b): medianen lister() bruker for hver
    aksje som regnes av kursene i basen, med den siste dagen med kurser for
    aksjen: {symbol: (median i NOK eller None, dagen eller None)}. En aksje
    som ikke staar her, har bare den siste maalingen i omsetning (2.13), som
    foer. Merket «Utenfor målingen» bruker dette, saa merket og de ferdige
    listene regner likt. Bare lesing. Mangler tabellene, er den tom.
    Gjennomgangen (BH1, ECH1): dagen er aksjens egen siste dag med kurser,
    ikke basens, saa en aksje som er tatt ut, ikke staar med en dag den ikke
    har kurser for."""
    if tilkobling is None:
        return {}
    try:
        regnet, i_lista = _aksjene_i_lista(tilkobling)
        if not regnet:
            return {}
        plasser = ", ".join("?" * len(regnet))
        dagene = dict(
            tilkobling.execute(
                f"SELECT symbol, max(dato) FROM kurs WHERE symbol IN ({plasser}) GROUP BY symbol", tuple(regnet)
            ).fetchall()
        )
    except sqlite3.Error:
        return {}
    medianer = {symbol: median for symbol, _, median, _ in i_lista}
    ut = {}
    for symbol in regnet:
        try:
            dag = date.fromisoformat(dagene[symbol]) if dagene.get(symbol) else None
        except (TypeError, ValueError):
            dag = None
        ut[symbol] = (medianer.get(symbol), dag)
    return ut
