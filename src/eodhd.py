"""Oversetteren fra EODHDs feltnavn til Kursrad - story 1.5, AD-19.

Kildens feltnavn stopper her. Formatet er EODHDs og ikke filens: radene kommer
fra oeyeblikksbildet (lagring_fil.SnapshotLeser) og, fra story 1.8, fra
API-svaret i hentekommandoen (fetch_prices.hent_universet). Derfor egen modul,
og ikke i lagring_fil.py, som hentekommandoen ellers maatte importert for aa
oversette et API-svar.

Modulen gjoer ingen I/O.
"""

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


def kursrad_fra_eodhd(rad: object) -> Kursrad:
    """Oversett en EODHD-rad til Kursrad. Det eneste stedet det skjer - AD-19.

    adjusted_close gir justert_slutt og close gir slutt, uten fallback mellom
    dem: en justert kurs som mangler, er en KeyError, ikke close. Fallbacken
    ville gitt et tall som ser riktig ut, men er regnet paa feil serie.

    Verdiene sjekkes ikke her; det gjoer Kursrad. En rad som ikke er et
    objekt, og en dato som ikke er streng YYYY-MM-DD, gir UgyldigKursrad.
    Et felt som mangler, gir KeyError. Hentingen og SnapshotLeser kaller
    den ikke selv, men gjennom serie_fra_eodhd (story 1.8).
    """
    if not isinstance(rad, dict):
        raise UgyldigKursrad(f"En EODHD-rad maa vaere et objekt, fikk {type(rad).__name__}")
    return Kursrad(
        dato=_dato_fra_tekst(rad["date"]),
        slutt=rad["close"],
        justert_slutt=rad["adjusted_close"],
        volum=rad["volume"],
    )


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
