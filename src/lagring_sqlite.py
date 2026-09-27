"""SQLite-adapterne for kursdata og vurderinger - story 1.3 og 1.6, FR-406,
FR-408, AD-4, AD-5 og AD-7.

Skall: dette er en av filene som kjenner teknologi. Kjernen ser bare
portene, Kurslager med Kursrad og Vurderingslager med Vurdering og Grunn.

Adapteren tar en aapen tilkobling, ikke en filsti. Hvem som aapner basen og
hvor fila ligger, avgjoeres i skallet (story 1.5, 2.2 og 3.1). Den kjoerer
heller ikke migrasjoner selv - hvem som kaller migrer(), er story 3.1s
avgjoerelse - men den nekter aa jobbe mot en base som ikke staar paa siste
versjon i MIGRASJONSKATALOG (story 1.5b, c). Den sjekker bare
versjonsnummeret, og bare naar den lages. Filnavn, innhold og en
skjema_versjon fra foer 1.5b kontrolleres av migrer(), som skal ha kjoert
foer adapteren tas i bruk.

Oversettelsen skjer her og ingen andre steder: dato er date inne i systemet og
"YYYY-MM-DD" i basen, hentet er datetime i UTC inne og ISO 8601 med
UTC-offset i basen. Ingen tekst slipper ut av porten.
"""

import sqlite3
from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path

from boersdag import innevaerende_boersdag, norsk_dato
from kursdata import AKSJEUNIVERS, Kursrad, kontroller_skriving
from migrering import MigrasjonsFeil, siste_versjon, versjon
from vurderingsdata import Grunn, Vurdering

MIGRASJONSKATALOG = Path(__file__).resolve().parent / "migrasjoner"


def _krev_siste_versjon(tilkobling: sqlite3.Connection) -> None:
    """Felles for begge adapterne: basen skal staa paa siste versjon.

    Story 1.5b, c: ikke bare vaere migrert en gang. Med 0002 ville en base paa
    versjon 1 ellers blitt godtatt og lest med et skjema den ikke har.
    """
    try:
        siste = siste_versjon(MIGRASJONSKATALOG)
    except MigrasjonsFeil as feil:
        raise RuntimeError(
            f"Migrasjonskatalogen {MIGRASJONSKATALOG} er ikke i orden: {feil}"
        ) from feil
    naa = versjon(tilkobling)
    if naa < siste:
        raise RuntimeError(
            f"Basen er ikke migrert til siste versjon: den staar paa "
            f"versjon {naa}, og {MIGRASJONSKATALOG} har {siste} "
            "migrasjoner. Kjoer migrer() mot katalogen foer adapteren "
            "tas i bruk."
        )
    if naa > siste:
        raise RuntimeError(
            f"Basen er nyere enn koden: den staar paa versjon {naa}, og "
            f"{MIGRASJONSKATALOG} har bare {siste} migrasjoner. Den er "
            "migrert av en nyere utgave av koden, og migrer() avviser den "
            "ogsaa."
        )


class SqliteKurslager:
    """Kurslager i SQLite. Oppfyller samme kontrakt som MinneKurslager.

    erstatt_serie sletter symbolets rader, setter inn de nye og oppdaterer
    kursserie i EN transaksjon (AD-5). Feiler noe underveis - for eksempel to
    rader med samme dato, som primaernoekkelen stopper etter at DELETE alt er
    kjoert - rulles alt tilbake, og symbolet har gammel serie og gammel tid.
    """

    def __init__(self, tilkobling: sqlite3.Connection):
        _krev_siste_versjon(tilkobling)
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


SYMBOLER = frozenset(aksje.symbol for aksje in AKSJEUNIVERS)

VURDERINGSKOLONNER = (
    "styrke", "retning", "trend", "bevegelse", "interesse", "slutt", "justert_slutt",
)

# Siste vinner, med ett unntak: en grunn skriver aldri over en vurdering
# samme dag (punkt 24). WHERE-leddet gjoer da upserten til ingenting, og
# rowcount blir 0. Reglene for overskriving staar her og ingen andre steder.
_UPSERT = (
    "INSERT INTO vurdering (symbol, dato, " + ", ".join(VURDERINGSKOLONNER) + ", grunn) "
    "VALUES (" + ", ".join("?" * (len(VURDERINGSKOLONNER) + 3)) + ") "
    "ON CONFLICT (symbol, dato) DO UPDATE SET "
    + ", ".join(f"{k} = excluded.{k}" for k in (*VURDERINGSKOLONNER, "grunn"))
    + " WHERE excluded.grunn IS NULL OR vurdering.grunn IS NOT NULL"
)


class SqliteVurderingslager:
    """Vurderingslager i SQLite - story 1.6, AD-7, AD-18, AD-20.

    Tar en aapen tilkobling og en klokke. Klokka leses ved hvert kall til
    skriv, ikke naar lageret lages, og testene injiserer den. Dagen regnes i
    Europe/Oslo (norsk_dato), og bare inneveerende boersdag godtas. En eldre
    rad kan leses, men aldri skrives om gjennom porten.

    Det finnes ingen minneutgave. Testene og story 2.5 bruker
    sqlite3.connect(":memory:").
    """

    def __init__(self, tilkobling: sqlite3.Connection, klokke: Callable[[], datetime]):
        _krev_siste_versjon(tilkobling)
        self._tilkobling = tilkobling
        self._klokke = klokke

    def skriv(self, symbol: str, dato: date, innhold: Vurdering | Grunn) -> bool:
        if not isinstance(dato, date) or isinstance(dato, datetime):
            raise TypeError(f"dato maa vaere datetime.date, fikk {dato!r}")
        if symbol not in SYMBOLER:
            raise ValueError(
                f"{symbol!r} er ikke et symbol i AKSJEUNIVERS. Symbolet er "
                "formen NewsWeb bruker (EQNR), ikke tickeren (EQNR.OL)"
            )
        if isinstance(innhold, Vurdering):
            verdier = (*(getattr(innhold, k) for k in VURDERINGSKOLONNER), None)
        elif isinstance(innhold, Grunn):
            verdier = (*(None for _ in VURDERINGSKOLONNER), innhold.value)
        else:
            raise TypeError(
                f"innhold maa vaere Vurdering eller Grunn, fikk {type(innhold).__name__}"
            )
        dagens = innevaerende_boersdag(norsk_dato(self._klokke()))
        if dato != dagens:
            raise ValueError(
                f"{dato.isoformat()} er ikke inneveerende boersdag "
                f"({dagens.isoformat()}). En eldre rad skrives aldri om (AD-7)."
            )
        if self._tilkobling.in_transaction:
            raise RuntimeError(
                "Tilkoblingen har en aapen transaksjon. Adapteren styrer "
                "transaksjonen selv - avslutt kallerens foerst."
            )

        try:
            self._tilkobling.execute("BEGIN")
            skrevet = self._tilkobling.execute(
                _UPSERT, (symbol, dato.isoformat(), *verdier)
            ).rowcount
            self._tilkobling.execute("COMMIT")
        except BaseException:
            if self._tilkobling.in_transaction:
                self._tilkobling.execute("ROLLBACK")
            raise
        return skrevet > 0

    def les(self, symbol: str, dato: date) -> Vurdering | Grunn | None:
        if not isinstance(dato, date) or isinstance(dato, datetime):
            raise TypeError(f"dato maa vaere datetime.date, fikk {dato!r}")
        rad = self._tilkobling.execute(
            "SELECT " + ", ".join(VURDERINGSKOLONNER) + ", grunn FROM vurdering "
            "WHERE symbol = ? AND dato = ?",
            (symbol, dato.isoformat()),
        ).fetchone()
        if rad is None:
            return None
        *felt, grunn = rad
        if grunn is not None:
            return Grunn(grunn)
        return Vurdering(**dict(zip(VURDERINGSKOLONNER, felt)))
