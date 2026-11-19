"""Oversetteren fra EODHDs feltnavn til Kursrad - story 1.5, AD-19.

Kildens feltnavn stopper her. Formatet er EODHDs og ikke filens: radene kommer
fra oeyeblikksbildet (lagring_fil.SnapshotLeser) og, fra story 1.8, fra
API-svaret i hentekommandoen (fetch_prices.hent_universet). Derfor egen modul,
og ikke i lagring_fil.py, som hentekommandoen ellers maatte importert for aa
oversette et API-svar.

Modulen gjoer ingen I/O.
"""

import math
from datetime import date

from kursdata import Kursrad, UgyldigKursrad


def _dato_fra_tekst(tekst: object) -> date:
    """Streng YYYY-MM-DD. Godtas bare hvis dato.isoformat() er lik teksten.

    date.fromisoformat alene godtar "20260921" og "2026-W39-1", og
    strptime("%Y-%m-%d") godtar "2026-9-1". En umulig dato som "2026-09-31"
    feiler allerede i parsingen.
    """
    if not isinstance(tekst, str):
        raise UgyldigKursrad(f"date maa vaere tekst YYYY-MM-DD, fikk {tekst!r}")
    try:
        dato = date.fromisoformat(tekst)
    except ValueError as feil:
        raise UgyldigKursrad(f"date er ikke en gyldig dato: {tekst!r}") from feil
    if dato.isoformat() != tekst:
        raise UgyldigKursrad(f"date maa ha formen YYYY-MM-DD, fikk {tekst!r}")
    return dato


def _valgfri_kurs(verdi: object) -> float | None:
    """high eller low fra EODHD, eller None - story 2.10.

    None naar feltet mangler, er null, ikke er et tall, ikke er endelig eller
    ikke er over null. Feltene brukes ikke av signalet, saa en verdi som ikke
    kan brukes, skal aldri avvise raden eller serien.
    """
    if isinstance(verdi, bool) or not isinstance(verdi, (int, float)):
        return None
    try:
        endelig = math.isfinite(verdi)
    except OverflowError:
        return None
    return float(verdi) if endelig and verdi > 0 else None


def _utenfor_slutt(slutt: object, hoey: float | None, lav: float | None) -> bool:
    """Om lav er over sluttkursen eller hoey under den - story 2.19.

    ECH3 i gjennomgangen av 2.10, gruppens svar 19.11 kl. 18:47. Sluttkursen
    er close, som gir slutt i Kursrad. Lik sluttkursen godtas. Er close ikke
    et tall, er svaret nei, og Kursrad avviser raden som foer.
    """
    if isinstance(slutt, bool) or not isinstance(slutt, (int, float)):
        return False
    return (lav is not None and lav > slutt) or (hoey is not None and hoey < slutt)


def _hoey_og_lav(rad: dict) -> tuple[float | None, float | None, bool]:
    """hoey og lav for raden, og om de ble tatt bort fordi de ikke passet med
    sluttkursen (story 2.19). Den eneste regelen for begge, saa adapteren og
    tellingen ikke kan faa hver sin."""
    hoey, lav = _valgfri_kurs(rad.get("high")), _valgfri_kurs(rad.get("low"))
    if _utenfor_slutt(rad.get("close"), hoey, lav):
        return None, None, True
    if hoey is not None and lav is not None and hoey < lav:
        return None, None, False
    return hoey, lav, False


def kursrad_fra_eodhd(rad: object) -> Kursrad:
    """Oversett en EODHD-rad til Kursrad. Det eneste stedet det skjer - AD-19.

    adjusted_close gir justert_slutt og close gir slutt, uten fallback mellom
    dem: en justert kurs som mangler, er en KeyError, ikke close. Fallbacken
    ville gitt et tall som ser riktig ut, men er regnet paa feil serie.

    Story 2.10: high gir hoey og low gir lav. De er valgfrie: en verdi som
    mangler eller ikke kan brukes, blir None (_valgfri_kurs), og er high under
    low, blir begge None, fordi det ikke kan avgjoeres hvilken som er feil.
    Story 2.19: det samme naar low er over close eller high under close
    (_hoey_og_lav). Resten av raden leses som foer, saa hentingen ikke
    stopper.

    De fire andre verdiene sjekkes ikke her; det gjoer Kursrad. En rad som
    ikke er et objekt, og en dato som ikke er streng YYYY-MM-DD, gir
    UgyldigKursrad. Mangler date, close, adjusted_close eller volume, gir
    det KeyError (gjennomgangen av 2.10, BH3). Hentingen og SnapshotLeser kaller
    den ikke selv, men gjennom serie_fra_eodhd (story 1.8).
    """
    if not isinstance(rad, dict):
        raise UgyldigKursrad(f"En EODHD-rad maa vaere et objekt, fikk {type(rad).__name__}")
    hoey, lav, _ = _hoey_og_lav(rad)
    return Kursrad(
        dato=_dato_fra_tekst(rad["date"]),
        slutt=rad["close"],
        justert_slutt=rad["adjusted_close"],
        volum=rad["volume"],
        hoey=hoey,
        lav=lav,
    )


def hoey_og_lav_mot_slutt(raa: list) -> int:
    """Hvor mange rader i en serie adapteren ga uten hoey og lav fordi de
    ikke passet med sluttkursen - story 2.19.

    Hentingen kaller den etter serie_fra_eodhd, saa hver rad er et objekt.
    En rad der high er under low, telles ogsaa, fordi en av dem da alltid
    ligger paa feil side av sluttkursen."""
    return sum(1 for rad in raa if _hoey_og_lav(rad)[2])


class UgyldigSerie(ValueError):
    """En serie fra EODHD som ikke kan leses - story 1.8.

    Den eneste feilen serie_fra_eodhd reiser. Hentingen og leseren fanger
    denne og ingenting annet, saa de avviser det samme.
    """


def serie_fra_eodhd(raa: object) -> list[Kursrad]:
    """Oversett en hel EODHD-serie til Kursrad, nyeste sist - story 1.8.

    Eneste regel for om en serie kan leses. SnapshotLeser og
    fetch_prices.hent_universet bruker begge denne, saa en aksje hentingen
    melder som hentet, ogsaa kan leses. Foer 1.8 hadde hentingen sin egen,
    svakere kontroll (G1 i kodegjennomgangen av Epic 1).

    UgyldigSerie hvis serien ikke er en liste, hvis en rad ikke kan
    oversettes (UgyldigKursrad eller KeyError fra kursrad_fra_eodhd), eller
    hvis to rader har samme dato: hvilken av dem som er riktig, kan ikke
    avgjoeres uten aa gjette. En tom liste gir en tom liste, ikke en feil,
    saa hentingen kan skille «tomt svar» fra «svar med feil form».
    """
    if not isinstance(raa, list):
        raise UgyldigSerie(f"En EODHD-serie maa vaere en liste, fikk {type(raa).__name__}")
    try:
        rader = [kursrad_fra_eodhd(r) for r in raa]
    except UgyldigKursrad as feil:
        raise UgyldigSerie(str(feil)) from feil
    except KeyError as feil:
        raise UgyldigSerie(f"En rad mangler feltet {feil}") from feil
    if len({r.dato for r in rader}) != len(rader):
        raise UgyldigSerie("To rader har samme dato")
    return sorted(rader, key=lambda r: r.dato)
