"""Migrasjonsloeperen - AD-16, story 1.1.

Skjemaet endres bare gjennom nummererte SQL-filer, 0001_navn.sql, 0002_navn.sql
og saa videre, kjoert i rekkefoelge. Anvendt versjon staar i tabellen
skjema_versjon, en rad per migrasjon med tidspunktet den ble kjoert.

Hver migrasjon kjoeres i EN transaksjon sammen med sin rad i skjema_versjon.
Feiler en setning, rulles begge tilbake, og basen staar paa versjonen fra
foer - ikke halvveis endret.

Det er grunnen til at executescript() ikke brukes. Den gjoer en implisitt
COMMIT foer den kjoerer noe, og hver setning i skriptet blir staaende for seg.
Feilen er stille: skjemaet er halvveis endret mens versjonsraden sier at
ingenting skjedde, og neste kjoering proever samme migrasjon paa nytt mot en
base som alt er delvis migrert. Loeperen deler derfor fila i setninger selv og
styrer transaksjonen selv.

Loeperen tar en tilkobling og en katalog, og gjoer resten. Hvem som kaller
den - hentekommandoen, webserverens oppstart eller begge - avgjoeres naar
Dockerfilen skrives (story 3.1), ikke her.

Med vilje finnes ingen DROP TABLE-hjelper, ingen "rebuild table"-mekanikk og
ingen unntaksvei for lagrene AD-7 verner. Trengs det, er det en beslutning som
skal tas synlig, i en egen migrasjon.
"""

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

FILNAVN = re.compile(r"^(\d{4})_.+\.sql$")


class MigrasjonsFeil(Exception):
    """En migrasjon kunne ikke kjoeres, eller katalogen er ikke i orden."""


def versjon(tilkobling: sqlite3.Connection) -> int:
    """Hoeyeste anvendte migrasjon. 0 for en base som aldri er migrert.

    Leser bare - en tom base forblir tom.
    """
    finnes = tilkobling.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'skjema_versjon'"
    ).fetchone()
    if not finnes:
        return 0
    return tilkobling.execute(
        "SELECT COALESCE(MAX(versjon), 0) FROM skjema_versjon"
    ).fetchone()[0]


def migrer(tilkobling: sqlite3.Connection, katalog: Path) -> int:
    """Kjoer alle migrasjoner basen ikke har faatt. Returnerer ny versjon.

    Hele katalogen kontrolleres foer noe kjoeres: to filer med samme nummer
    eller et hull i rekka stopper alt, fordi begge betyr at to utgaver av
    skjemaet er i omloep.

    Tilkoblingen maa ikke ha en aapen transaksjon. Loeperen eier
    transaksjonen, og en COMMIT herfra ville tatt med seg kallerens endringer.
    """
    if tilkobling.in_transaction:
        raise MigrasjonsFeil(
            "Tilkoblingen har en aapen transaksjon. Loeperen styrer "
            "transaksjonen selv - avslutt kallerens foerst."
        )

    filer = _migrasjoner(Path(katalog))
    naa = versjon(tilkobling)
    if naa > len(filer):
        raise MigrasjonsFeil(
            f"Basen er paa versjon {naa}, men {katalog} har bare {len(filer)} "
            "migrasjoner. Basen er migrert av en nyere utgave av koden."
        )

    for nummer, sti in filer[naa:]:
        _kjoer(tilkobling, nummer, sti)

    return versjon(tilkobling)


def _migrasjoner(katalog: Path) -> list[tuple[int, Path]]:
    """Migrasjonsfilene sortert paa nummer, 1, 2, 3 ... uten hull.

    Andre filer enn .sql ignoreres. En .sql-fil med feil navn er en feil -
    en migrasjon som stille hoppes over er verre enn en som stopper.
    """
    if not katalog.is_dir():
        raise MigrasjonsFeil(f"Fant ikke migrasjonskatalogen {katalog}")

    etter_nummer: dict[int, Path] = {}
    for sti in sorted(katalog.glob("*.sql")):
        treff = FILNAVN.match(sti.name)
        if not treff:
            raise MigrasjonsFeil(
                f"{sti.name} er ikke navngitt som en migrasjon (NNNN_navn.sql)"
            )
        nummer = int(treff.group(1))
        if nummer in etter_nummer:
            raise MigrasjonsFeil(
                f"To migrasjoner har nummer {nummer:04d}: "
                f"{etter_nummer[nummer].name} og {sti.name}"
            )
        etter_nummer[nummer] = sti

    for forventet in range(1, len(etter_nummer) + 1):
        if forventet not in etter_nummer:
            raise MigrasjonsFeil(f"Migrasjon {forventet:04d} mangler i {katalog}")

    return sorted(etter_nummer.items())


def _setninger(sql: str) -> list[str]:
    """Del en SQL-fil i enkeltsetninger.

    sqlite3.complete_statement avgjoer hvor en setning slutter, saa semikolon
    inne i strenger og kommentarer ikke deler den.
    """
    setninger: list[str] = []
    buffer = ""
    for bit in sql.split(";"):
        buffer += bit + ";"
        if sqlite3.complete_statement(buffer):
            setninger.append(buffer)
            buffer = ""
    # Det som staar igjen, er det etter siste semikolon: whitespace,
    # kommentarer eller en setning uten avsluttende semikolon.
    rest = buffer[:-1]
    if rest.strip():
        setninger.append(rest)
    return setninger


def _kjoer(tilkobling: sqlite3.Connection, nummer: int, sti: Path) -> None:
    """En migrasjon og dens versjonsrad, i en transaksjon."""
    setninger = _setninger(sti.read_text(encoding="utf-8"))
    try:
        tilkobling.execute("BEGIN")
        tilkobling.execute(
            "CREATE TABLE IF NOT EXISTS skjema_versjon ("
            "versjon INTEGER PRIMARY KEY, fil TEXT NOT NULL, anvendt TEXT NOT NULL)"
        )
        for setning in setninger:
            tilkobling.execute(setning)
        tilkobling.execute(
            "INSERT INTO skjema_versjon (versjon, fil, anvendt) VALUES (?, ?, ?)",
            (nummer, sti.name, datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )
        tilkobling.execute("COMMIT")
    except sqlite3.Error as feil:
        if tilkobling.in_transaction:
            tilkobling.execute("ROLLBACK")
        raise MigrasjonsFeil(
            f"{sti.name} feilet og er rullet tilbake: {feil}. "
            f"Basen staar paa versjon {nummer - 1}."
        ) from feil
