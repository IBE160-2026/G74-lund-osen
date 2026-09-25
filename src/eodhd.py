"""Oversetteren fra EODHDs feltnavn til Kursrad - story 1.5, AD-19.

Kildens feltnavn stopper her. Formatet er EODHDs og ikke filens: i dag kommer
radene fra oeyeblikksbildet (lagring_fil.SnapshotLeser), og i Epic 2 fra
API-svaret i hentekommandoen. Derfor egen modul, og ikke i lagring_fil.py,
som hentekommandoen ellers maatte importert for aa oversette et API-svar.

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
    Et felt som mangler, gir KeyError. Epic 2 bruker samme funksjon naar
    hentingen skriver til basen.
    """
    if not isinstance(rad, dict):
        raise UgyldigKursrad(f"En EODHD-rad maa vaere et objekt, fikk {type(rad).__name__}")
    return Kursrad(
        dato=_dato_fra_tekst(rad["date"]),
        slutt=rad["close"],
        justert_slutt=rad["adjusted_close"],
        volum=rad["volume"],
    )
