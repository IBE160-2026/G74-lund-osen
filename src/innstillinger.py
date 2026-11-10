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
# Story 8.21 (tillegget 10.11 kl. 14:44): «Notater», i tabellen notatvalg fra
# 0012, fordi CHECK i innstilling (0011) bare godtar de to valgene der.
VIS_NOTATER = "vis_notater"
NAVNENE = (VIS_HJELP, VIS_KI_TEKST, VIS_NOTATER)
# Valgene siden «Innstillinger» viser og kan lagre. Story 8.10b: også KI-teksten.
PAA_SIDEN = (VIS_HJELP, VIS_KI_TEKST, VIS_NOTATER)
# Tabellen for hvert valg.
TABELL = {VIS_HJELP: "innstilling", VIS_KI_TEKST: "innstilling", VIS_NOTATER: "notatvalg"}


def har_tabellen(tilkobling: sqlite3.Connection | None, tabell: str = "innstilling") -> bool:
    if tilkobling is None:
        return False
    try:
        return (
            tilkobling.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (tabell,)).fetchone()
            is not None
        )
    except sqlite3.Error:
        return False


def _rader(tilkobling: sqlite3.Connection | None) -> dict[str, bool]:
    rader: dict[str, bool] = {}
    for tabell in ("innstilling", "notatvalg"):
        if not har_tabellen(tilkobling, tabell):
            continue
        try:
            rader.update({navn: verdi == 1 for navn, verdi in tilkobling.execute(f"SELECT navn, verdi FROM {tabell}")})
        except sqlite3.Error:
            pass
    return rader


def les(tilkobling: sqlite3.Connection | None) -> dict[str, bool]:
    """Valgene, med på for et valg uten rad, og for en base uten tabellen."""
    valgene = dict.fromkeys(NAVNENE, True)
    valgene.update({navn: paa for navn, paa in _rader(tilkobling).items() if navn in valgene})
    return valgene


def les_rader(tilkobling: sqlite3.Connection | None) -> dict[str, bool]:
    """Bare valgene som har en rad. Story 8.10b: uten raden for KI-teksten
    leses informasjonskapselen fra før (spørsmål 1 i 8.10b)."""
    return _rader(tilkobling)


def sett(tilkobling: sqlite3.Connection, navn: str, paa: bool) -> None:
    """Lagrer valget. Et navn som ikke er et valg, avvises."""
    if navn not in NAVNENE:
        raise ValueError("ukjent innstilling")
    # Story 8.21: «Notater» står i notatvalg. SQL-en står ordrett for hver
    # tabell, så testen som ser etter skriverne, finner dem.
    if TABELL[navn] == "notatvalg":
        sql = (
            "INSERT INTO notatvalg (navn, verdi) VALUES (?, ?) ON CONFLICT (navn) DO UPDATE SET verdi = excluded.verdi"
        )
    else:
        sql = "INSERT INTO innstilling (navn, verdi) VALUES (?, ?) ON CONFLICT (navn) DO UPDATE SET verdi = excluded.verdi"
    with tilkobling:
        tilkobling.execute(sql, (navn, 1 if paa else 0))
