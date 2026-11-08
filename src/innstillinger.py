"""Innstillinger øverst - story 8.10, FR-110, AD-3, AD-10, AD-16.

Valgene står i tabellen innstilling (0011), én rad per valg. Ingen rad
betyr på. Webserveren er eneste skriver, som for Min liste, og henter aldri
noe. En base uten tabellen, en versjon bak, gir standardvalgene, og da kan
ingenting lagres.
"""

import sqlite3

VIS_HJELP = "vis_hjelp"
# Story 8.10b: KI-teksten, i samme tabell.
VIS_KI_TEKST = "vis_ki_tekst"
NAVNENE = (VIS_HJELP, VIS_KI_TEKST)
# Valgene siden «Innstillinger» viser og kan lagre. Story 8.10b: også KI-teksten.
PAA_SIDEN = (VIS_HJELP, VIS_KI_TEKST)


def har_tabellen(tilkobling: sqlite3.Connection | None) -> bool:
    if tilkobling is None:
        return False
    try:
        return (
            tilkobling.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'innstilling'").fetchone()
            is not None
        )
    except sqlite3.Error:
        return False


def les(tilkobling: sqlite3.Connection | None) -> dict[str, bool]:
    """Valgene, med på for et valg uten rad, og for en base uten tabellen."""
    valgene = dict.fromkeys(NAVNENE, True)
    if not har_tabellen(tilkobling):
        return valgene
    try:
        for navn, verdi in tilkobling.execute("SELECT navn, verdi FROM innstilling"):
            if navn in valgene:
                valgene[navn] = verdi == 1
    except sqlite3.Error:
        pass
    return valgene


def les_rader(tilkobling: sqlite3.Connection | None) -> dict[str, bool]:
    """Bare valgene som har en rad. Story 8.10b: uten raden for KI-teksten
    leses informasjonskapselen fra før (spørsmål 1 i 8.10b)."""
    if not har_tabellen(tilkobling):
        return {}
    try:
        return {navn: verdi == 1 for navn, verdi in tilkobling.execute("SELECT navn, verdi FROM innstilling")}
    except sqlite3.Error:
        return {}


def sett(tilkobling: sqlite3.Connection, navn: str, paa: bool) -> None:
    """Lagrer valget. Et navn som ikke er et valg, avvises."""
    if navn not in NAVNENE:
        raise ValueError("ukjent innstilling")
    with tilkobling:
        tilkobling.execute(
            "INSERT INTO innstilling (navn, verdi) VALUES (?, ?) ON CONFLICT (navn) DO UPDATE SET verdi = excluded.verdi",
            (navn, 1 if paa else 0),
        )
