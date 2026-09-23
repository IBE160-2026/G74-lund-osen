"""SQLite-adapteren for kursdata - story 1.3, FR-406, AD-4 og AD-5.

Skall: dette er en av filene som kjenner teknologi. Kjernen ser bare
Kurslager-porten og Kursrad.

Adapteren tar en aapen tilkobling, ikke en filsti. Hvem som aapner basen og
hvor fila ligger, avgjoeres i skallet (story 1.5, 2.2 og 3.1). Den kjoerer
heller ikke migrasjoner selv - hvem som kaller migrer(), er story 3.1s
avgjoerelse - men den nekter aa jobbe mot en base som ikke er migrert.

Oversettelsen skjer her og ingen andre steder: dato er date inne i systemet og
"YYYY-MM-DD" i basen, hentet er datetime i UTC inne og ISO 8601 med
UTC-offset i basen. Ingen tekst slipper ut av porten.
"""

import sqlite3
from datetime import date, datetime
from pathlib import Path

from kursdata import Kursrad, kontroller_skriving
from migrering import versjon

MIGRASJONSKATALOG = Path(__file__).resolve().parent / "migrasjoner"


class SqliteKurslager:
    """Kurslager i SQLite. Oppfyller samme kontrakt som MinneKurslager.

    erstatt_serie sletter symbolets rader, setter inn de nye og oppdaterer
    kursserie i EN transaksjon (AD-5). Feiler noe underveis - for eksempel to
    rader med samme dato, som primaernoekkelen stopper etter at DELETE alt er
    kjoert - rulles alt tilbake, og symbolet har gammel serie og gammel tid.
    """

    def __init__(self, tilkobling: sqlite3.Connection):
        if versjon(tilkobling) < 1:
            raise RuntimeError(
                "Basen er ikke migrert. Kjoer migrer() mot "
                f"{MIGRASJONSKATALOG} foer adapteren tas i bruk."
            )
        self._tilkobling = tilkobling

    def erstatt_serie(self, symbol: str, rader: list[Kursrad], hentet: datetime) -> None:
        rader = list(rader)
        tid = kontroller_skriving(rader, hentet)
        if self._tilkobling.in_transaction:
            raise RuntimeError(
                "Tilkoblingen har en aapen transaksjon. Adapteren styrer "
                "transaksjonen selv - avslutt kallerens foerst."
            )

        try:
            self._tilkobling.execute("BEGIN")
            self._tilkobling.execute("DELETE FROM kurs WHERE symbol = ?", (symbol,))
            self._tilkobling.executemany(
                "INSERT INTO kurs (symbol, dato, slutt, justert_slutt, volum) "
                "VALUES (?, ?, ?, ?, ?)",
                [
                    (symbol, rad.dato.isoformat(), rad.slutt, rad.justert_slutt, rad.volum)
                    for rad in rader
                ],
            )
            self._tilkobling.execute(
                "INSERT INTO kursserie (symbol, hentet) VALUES (?, ?) "
                "ON CONFLICT (symbol) DO UPDATE SET hentet = excluded.hentet",
                (symbol, tid.isoformat()),
            )
            self._tilkobling.execute("COMMIT")
        except sqlite3.IntegrityError as feil:
            self._rull_tilbake()
            raise ValueError(
                f"Serien for {symbol} ble avvist og rullet tilbake: {feil}"
            ) from feil
        except BaseException:
            self._rull_tilbake()
            raise

    def serie(self, symbol: str) -> list[Kursrad]:
        return [
            Kursrad(
                dato=date.fromisoformat(dato),
                slutt=slutt,
                justert_slutt=justert_slutt,
                volum=volum,
            )
            for dato, slutt, justert_slutt, volum in self._tilkobling.execute(
                "SELECT dato, slutt, justert_slutt, volum FROM kurs "
                "WHERE symbol = ? ORDER BY dato",
                (symbol,),
            )
        ]

    def sist_hentet(self, symbol: str) -> datetime | None:
        rad = self._tilkobling.execute(
            "SELECT hentet FROM kursserie WHERE symbol = ?", (symbol,)
        ).fetchone()
        return datetime.fromisoformat(rad[0]) if rad else None

    def _rull_tilbake(self) -> None:
        if self._tilkobling.in_transaction:
            self._tilkobling.execute("ROLLBACK")
