"""Utregningen av median omsetning - story 2.13 (FR-413), flyttet hit i 8.11b.

Ren regning uten nett, basen eller fetch_prices, saa baade maalingen i
omsetning.py og de ferdige listene paa siden (ferdige_lister.py, AD-10)
bruker den samme. Ingen tall fra kildene staar her (regel 16).
"""

import calendar
import math
import statistics
from dataclasses import dataclass
from datetime import date

MAANEDER = 3


@dataclass(frozen=True)
class Maaling:
    """En rad i omsetning. median er NOK, uavrundet (regel 21), eller None med
    feil."""

    symbol: str
    handelsdager: int
    dager_uten_volum: int
    rader_uten_tall: int
    median: float | None
    feil: str | None


def vindu(boersdag: date) -> tuple[date, date]:
    """Tre maaneder til og med boersdagen, som i §40 (2026-07-22-2026-10-22).

    Finnes ikke dagen tre maaneder foer, er det siste dag i den maaneden.
    """
    aar, maaned = divmod(boersdag.year * 12 + boersdag.month - 1 - MAANEDER, 12)
    dager = calendar.monthrange(aar, maaned + 1)[1]
    return date(aar, maaned + 1, min(boersdag.day, dager)), boersdag


def _tall(verdi: object) -> bool:
    """Et endelig tall som ikke er negativt. Gjennomgangen (ECH3): et heltall
    for stort for float gir OverflowError i isfinite, og er ikke et tall her."""
    if isinstance(verdi, bool) or not isinstance(verdi, (int, float)):
        return False
    try:
        return math.isfinite(verdi) and verdi >= 0
    except OverflowError:
        return False


def regn_ut(symbol: str, rader: object, fra: date, til: date) -> Maaling:
    """Median av volume x close per rad i vinduet, som i §3 og §42.

    En rad med volum 0 er med, med omsetning 0, og telles i dager_uten_volum.
    En rad uten tall for close eller volume er ikke med, men telles.
    """
    if not isinstance(rader, list):
        return Maaling(symbol, 0, 0, 0, None, "svaret er ikke en liste med rader")
    omsetning, uten_volum, uten_tall = [], 0, 0
    for rad in rader:
        try:
            dag = date.fromisoformat(rad["date"])
        except (TypeError, KeyError, ValueError):
            uten_tall += 1
            continue
        if not fra <= dag <= til:
            continue
        if not (_tall(rad.get("close")) and _tall(rad.get("volume"))):
            uten_tall += 1
            continue
        # Gjennomgangen (BH9): volum 0, ikke omsetning 0, saa en kurs paa 0
        # ikke telles som en dag uten volum.
        uten_volum += rad["volume"] == 0
        omsetning.append(float(rad["volume"]) * float(rad["close"]))
    if not omsetning:
        return Maaling(symbol, 0, 0, uten_tall, None, "ingen rader med tall i vinduet")
    median = float(statistics.median(omsetning))
    if not math.isfinite(median):
        return Maaling(symbol, 0, 0, uten_tall, None, "medianen er ikke et endelig tall")
    return Maaling(symbol, len(omsetning), uten_volum, uten_tall, median, None)
