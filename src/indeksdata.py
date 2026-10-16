"""Porten for hovedindeksen: typene og kontrakten, uten I/O - story 2.8,
FR-410, AD-3, AD-5, AD-21 med foeringen 2026-10-01.

Indeksen er ikke en aksje. Den staar ikke i AKSJEUNIVERS, og den lagres i
tabellen indeks fra 0006, aldri i aksje, kurs, kursserie eller vurdering.
Porten har samme form som Kursleser og Kurslager: Indeksleser leser, og
Indekslager bytter ut hele serien i ett (AD-5). En dag er en Kursrad, fordi
indeksen har de samme feltene for en dag.

Bare boersdager i aarene DEKKEDE_AAR dekker, lagres. Serien fra EODHD gaar
ett aar bakover, og indeksen har dager aksjene ikke har (malinger.md §14).
Porten tar dem bort foer noe lagres, uten feil, og leser aarene fra
boersdag.py naar serien skrives, saa koden har ikke noe fast aarstall.

Adapteren i basen er SqliteIndekslager i lagring_sqlite.py. Kallet i
hentingen kommer i PR 2.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

import boersdag
from kursdata import AKSJEUNIVERS, Kursrad


@dataclass(frozen=True)
class Indeks:
    """En indeks: symbolet uten .OL, tickeren hos EODHD og navnet som vises."""

    symbol: str
    ticker: str
    navn: str


HOVEDINDEKS = Indeks("OSEBX", "OSEBX.OL", "Hovedindeksen")


def bare_boersdager(rader: list[Kursrad]) -> list[Kursrad]:
    """Radene for boersdager i aarene DEKKEDE_AAR dekker. De andre tas bort
    uten feil: en dag i et annet aar kan ikke slaas opp i kalenderen, og en
    stengt dag er ikke en dag aksjene har kurs."""
    return [
        rad for rad in rader
        if rad.dato.year in boersdag.DEKKEDE_AAR and boersdag.er_boersdag(rad.dato)
    ]


@runtime_checkable
class Indeksleser(Protocol):
    """Lesesiden av indeksporten. Samme kontrakt som Kursleser:
    sist_hentet(s) er None hvis og bare hvis serie(s) er tom."""

    def serie(self, symbol: str) -> list[Kursrad]:
        """Kronologiske rader, nyeste sist. Tom liste hvis vi mangler."""

    def sist_hentet(self, symbol: str) -> datetime | None:
        """Naar indeksens serie sist ble erstattet, i UTC. None hvis aldri."""


@runtime_checkable
class Indekslager(Indeksleser, Protocol):
    """Porten for indeksen. Indeksleser pluss erstatt_serie. Det finnes ingen
    legg_til_rad: serien skjoetes aldri paa (AD-5)."""

    def erstatt_serie(self, symbol: str, rader: list[Kursrad], hentet: datetime) -> None:
        """Bytt ut hele indeksens serie, og sett sist_hentet, i ett.

        Dager som ikke er boersdager i DEKKEDE_AAR, tas bort foerst. Et symbol
        som ikke er en kjent indeks, en serie som er tom etter det, en feil
        radtype, to rader med samme dato eller en tid uten sone avvises, og
        da endres ingenting.
        """


def kontroller_indeksskriving(
    symbol: str,
    rader: list[Kursrad],
    hentet: datetime,
    indekser: tuple[Indeks, ...] = (HOVEDINDEKS,),
) -> tuple[list[Kursrad], datetime]:
    """Felles kontroll for alle Indekslager. Gir radene som skal lagres og
    hentet i UTC. Kjoeres foer noe lagres, saa en avvist skriving etterlater
    lageret slik det var. Like datoer kontrolleres ikke her, men av
    primaernoekkelen i SQLite og av MinneIndekslager, som for kursene."""
    # En aksje er aldri en indeks, ogsaa naar kalleren gir en Indeks med
    # symbolet til en aksje (gjennomgangen av 2.8a, ECH).
    if symbol in {aksje.symbol for aksje in AKSJEUNIVERS}:
        raise ValueError(f"{symbol!r} er en aksje i AKSJEUNIVERS og lagres i kurs, ikke her (AD-21)")
    if symbol not in {indeks.symbol for indeks in indekser}:
        raise ValueError(
            f"{symbol!r} er ikke en kjent indeks. Symbolet er uten .OL (OSEBX), "
            "og en aksje lagres i kurs, ikke her (AD-21)"
        )
    for rad in rader:
        if not isinstance(rad, Kursrad):
            raise TypeError(f"Indekslager tar Kursrad, fikk {type(rad).__name__}")
    if not isinstance(hentet, datetime):
        raise TypeError(f"hentet maa vaere datetime, fikk {hentet!r}")
    if hentet.tzinfo is None or hentet.utcoffset() is None:
        raise ValueError(f"hentet maa ha tidssone (AD-20), fikk {hentet!r}")
    beholdt = bare_boersdager(list(rader))
    if not beholdt:
        # AD-5: en tom serie ville slettet historikken og satt et ferskt
        # tidsstempel paa ingenting.
        raise ValueError("Tom serie avvises: ingen boersdager i aarene kalenderen dekker")
    return beholdt, hentet.astimezone(timezone.utc)


@dataclass
class MinneIndekslager:
    """Indekslager i minnet, for testene. Samme kontrakt som SQLite-adapteren."""

    indekser: tuple[Indeks, ...] = (HOVEDINDEKS,)
    _serier: dict[str, tuple[Kursrad, ...]] = field(default_factory=dict)
    _hentet: dict[str, datetime] = field(default_factory=dict)

    def erstatt_serie(self, symbol: str, rader: list[Kursrad], hentet: datetime) -> None:
        beholdt, tid = kontroller_indeksskriving(symbol, list(rader), hentet, self.indekser)
        datoer = [rad.dato for rad in beholdt]
        if len(set(datoer)) != len(datoer):
            raise ValueError(f"To rader med samme dato for {symbol}")
        self._serier[symbol] = tuple(sorted(beholdt, key=lambda rad: rad.dato))
        self._hentet[symbol] = tid

    def serie(self, symbol: str) -> list[Kursrad]:
        return list(self._serier.get(symbol, ()))

    def sist_hentet(self, symbol: str) -> datetime | None:
        return self._hentet.get(symbol)
