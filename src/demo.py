"""Demoversjonen - story 3.4, FR-411.

Lager demobasen data/db/demo.db med 15 oppdiktede selskaper, kurser etter
regelen under, og en vurdering per aksje og boersdag. Kommandoen gjoer ingen
nettkall, leser ingen noekkel og importerer verken requests, eodhd eller
fetch_prices.

    uv run python src/demo.py

Regelen for kursene (spesifikasjonen til 3.4, Boundaries):
- 195 handelsdager fra 2026-01-02 til SLUTTDATO, fredag 2026-10-09, etter
  boersdag.er_boersdag. Kalenderen dekker 2026.
- Hver aksje har sitt eget frø, FROE * 100 + nummeret i DEMOUNIVERS, og sin
  egen random.Random. Python lover bare at random() gir samme rekke med samme
  frø paa tvers av versjoner, saa normalfordelingen lages her med Box-Muller
  paa random(), ikke med gauss() eller normalvariate().
- Daglig logavkastning er drift + volatilitet * z, med drift og volatilitet
  etter sektor. Volumet er et nivaa per aksje ganger exp(0,3 * z), og med
  sannsynlighet 0,04 tre ganger det. adjusted_close er lik close. Kursene
  avrundes til to desimaler og volumet til heltall.
- Siste dag faller Brattfjell Energi 6 % med tre ganger volumet, saa minst en
  aksje skiller seg ut.
- Varde Systemer har bare de siste 30 dagene (nylig notert), og Matfjord
  Merkevarer har ingen kurser. Da viser sidene ogsaa «signalet kunne ikke
  regnes», «Trenger 51 dager» og «Uten data». (En aksje uten siste dag ble
  tatt ut 10.10: den flyttet datoen over tabellen til dagen foer, se Spec
  Change Log i spesifikasjonen.)

Vurderingene: for hver boersdag og hver aksje er raden det vurder() gir for
serien fram til dagen, skrevet med SqliteVurderingslager.skriv uendret og
lagerets klokke stilt paa dagen (AD-7, merknaden 2026-10-03).

Merket: PRAGMA application_id = DEMOMERKE. Bare denne kommandoen setter det.
Kommandoen nekter en fil uten merket, ogsaa en tom fil, og lager en demobase
paa nytt fra bunnen. Hentingen nekter en base med merket.
"""

import argparse
import math
import os
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import lagring_sqlite
from boersdag import er_boersdag
from kursdata import Aksje, Kursrad
from lagring_sqlite import (
    DEMOMERKE,
    SqliteKurslager,
    SqliteVurderingslager,
    aapne_base,
    les_merket,
)
from signalberegning import vurder

OSLO = ZoneInfo("Europe/Oslo")

# Kommandoen den tomme siden viser naar demobasen mangler (story 3.4). README
# faar den i PR 2, og da kommer testen som holder dem like.
DEMOKOMMANDO = "uv run python src/demo.py"

FROE = 20261009
FOERSTE_DAG = date(2026, 1, 2)
SLUTTDATO = date(2026, 10, 9)
NYLIG_NOTERT_DAGER = 30

# Navnene og tickerne er kontrollert for haand: Joakim mot lista over aksjer
# i Oslo hos Euronext 10.10 kl. 12:25, og raadet med et soek paa nettet
# samme dag (spesifikasjonen til 3.4). Programmet henter aldri lista.
DEMOUNIVERS: tuple[Aksje, ...] = (
    Aksje("BRFE", "BRFE.OL", "Brattfjell Energi", "Energi"),
    Aksje("HVDO", "HVDO.OL", "Havdyp Olje", "Energi"),
    Aksje("NLYS", "NLYS.OL", "Nordlysfeltet", "Energi"),
    Aksje("SLVP", "SLVP.OL", "Sølvbank Petroleum", "Energi"),
    Aksje("FJSB", "FJSB.OL", "Fjellheim Sparebank", "Finans"),
    Aksje("TRHF", "TRHF.OL", "Trygghavn Forsikring", "Finans"),
    Aksje("VRDS", "VRDS.OL", "Varde Systemer", "Industri"),
    Aksje("KVST", "KVST.OL", "Kvitstein Mineral", "Materialer"),
    Aksje("JGRD", "JGRD.OL", "Jordgrøde Gjødsel", "Materialer"),
    Aksje("BLGT", "BLGT.OL", "Bølgetopp Tankers", "Shipping"),
    Aksje("LSTF", "LSTF.OL", "Lastfjord Container", "Shipping"),
    Aksje("SGNT", "SGNT.OL", "Signalnett", "Telekom"),
    Aksje("LKSV", "LKSV.OL", "Laksevik Sjømat", "Sjømat"),
    Aksje("TROY", "TROY.OL", "Tareøy Havbruk", "Sjømat"),
    Aksje("MTFJ", "MTFJ.OL", "Matfjord Merkevarer", "Konsum"),
)

NYLIG_NOTERT = "VRDS"
UTEN_KURSER = "MTFJ"
SKILLER_SEG_UT = "BRFE"

# Daglig drift og volatilitet i logavkastningen, etter sektor.
SEKTOR = {
    "Energi": (0.0002, 0.018),
    "Finans": (0.0003, 0.012),
    "Industri": (0.0006, 0.020),
    "Materialer": (0.0001, 0.016),
    "Shipping": (0.0001, 0.022),
    "Telekom": (0.0, 0.010),
    "Sjømat": (0.0002, 0.017),
    "Konsum": (0.0001, 0.009),
}

# Startkurs og volumnivaa per aksje, i samme rekkefoelge som DEMOUNIVERS.
START = (
    (212.0, 3_200_000), (148.5, 1_100_000), (36.4, 2_600_000), (88.0, 900_000),
    (174.2, 1_800_000), (205.0, 600_000), (61.5, 400_000), (119.0, 1_500_000),
    (402.0, 700_000), (164.0, 1_200_000), (27.9, 2_100_000), (131.5, 1_000_000),
    (226.0, 800_000), (79.4, 500_000), (102.0, 300_000),
)


def handelsdager() -> list[date]:
    """Boersdagene fra FOERSTE_DAG til SLUTTDATO, etter kalenderen."""
    dager, dag = [], FOERSTE_DAG
    while dag <= SLUTTDATO:
        if er_boersdag(dag):
            dager.append(dag)
        dag += timedelta(days=1)
    return dager


def _normal(rng: random.Random) -> float:
    """Standard normalfordelt tall med Box-Muller paa random()."""
    u1 = 1.0 - rng.random()  # i (0, 1], saa log(u1) er endelig
    u2 = rng.random()
    return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


def serie(nummer: int, aksje: Aksje, dager: list[date]) -> list[Kursrad]:
    """Kursene for en aksje etter regelen i modulens docstring."""
    rng = random.Random(FROE * 100 + nummer)
    drift, volatilitet = SEKTOR[aksje.sektor]
    kurs, volumnivaa = START[nummer]
    rader = []
    for i, dag in enumerate(dager):
        z, z_volum = _normal(rng), _normal(rng)
        topp = rng.random() < 0.04
        if i > 0:
            kurs *= math.exp(drift + volatilitet * z)
        volum = volumnivaa * math.exp(0.3 * z_volum) * (3 if topp else 1)
        if aksje.symbol == SKILLER_SEG_UT and dag == SLUTTDATO:
            kurs *= 0.94
            volum = volumnivaa * 3
        slutt = round(kurs, 2)
        rader.append(Kursrad(dato=dag, slutt=slutt, justert_slutt=slutt, volum=int(round(volum))))
    if aksje.symbol == NYLIG_NOTERT:
        rader = rader[-NYLIG_NOTERT_DAGER:]
    elif aksje.symbol == UTEN_KURSER:
        rader = []
    return rader


def _klokke_for(dag: date):
    oeyeblikk = datetime(dag.year, dag.month, dag.day, 22, 30, tzinfo=OSLO)
    return lambda: oeyeblikk


class IkkeEnDemobase(Exception):
    """Fila finnes og har ikke demomerket. Demokommandoen roerer den ikke."""


def lag_demobase(sti: Path, skriv=print) -> None:
    """Lager demobasen i sti. En demobase som finnes, lages paa nytt.

    Reiser IkkeEnDemobase hvis fila finnes uten merket, ogsaa naar den er tom,
    foer noe er skrevet (FR-411, AD-7).

    Basen bygges i en egen fil ved siden av (demo.db.ny) og byttes inn med
    os.replace foerst naar alt er skrevet. En byggingen som stopper halvveis,
    etterlater aldri en halv demobase med merket der webserveren leter
    (gjennomgangen av PR 1, BH2 og ECH5).
    """
    sti = Path(sti)
    if sti.exists() and not lagring_sqlite.er_demobase(sti):
        raise IkkeEnDemobase(
            f"{sti.name} finnes og er ikke en demobase. Demokommandoen skriver "
            "aldri til en base uten demomerket (FR-411)."
        )
    ny = sti.with_name(sti.name + ".ny")
    for rest in _med_hjelpefiler(ny):
        rest.unlink(missing_ok=True)
    try:
        _bygg(ny)
    except BaseException:
        for rest in _med_hjelpefiler(ny):
            rest.unlink(missing_ok=True)
        raise
    for rest in _med_hjelpefiler(sti)[1:]:
        rest.unlink(missing_ok=True)
    os.replace(ny, sti)
    dager = handelsdager()
    skriv(
        f"Laget {sti.name}: {len(DEMOUNIVERS)} oppdiktede selskaper, "
        f"{len(dager)} handelsdager fra {dager[0]} til {dager[-1]}. Eksempeltall, "
        "ikke data fra Oslo Børs. Ingen nettkall."
    )


def _med_hjelpefiler(sti: Path) -> list[Path]:
    """Basen og hjelpefilene SQLite kan legge ved siden av den."""
    return [sti, *(sti.with_name(sti.name + ending) for ending in ("-journal", "-wal", "-shm"))]


def _bygg(sti: Path) -> None:
    """Skriver hele demobasen i sti, som ikke finnes fra foer."""
    tilkobling = aapne_base(sti)
    try:
        tilkobling.execute(f"PRAGMA application_id = {DEMOMERKE}")
        # Demobasen kan alltid lages paa nytt, saa den skrives uten fsync per
        # transaksjon. Det gjelder bare denne tilkoblingen.
        tilkobling.execute("PRAGMA synchronous = OFF")
        assert les_merket(tilkobling) == DEMOMERKE
        # AD-21: de 15 fra 0003 har ingen rader og kan slettes. aksje faar
        # DEMOUNIVERS i samme rekkefoelge.
        with tilkobling:
            tilkobling.execute("DELETE FROM aksje")
            tilkobling.executemany(
                "INSERT INTO aksje (symbol, ticker, navn, sektor) VALUES (?, ?, ?, ?)",
                [(a.symbol, a.ticker, a.navn, a.sektor) for a in DEMOUNIVERS],
            )

        dager = handelsdager()
        serier = {a.symbol: serie(n, a, dager) for n, a in enumerate(DEMOUNIVERS)}
        hentet = datetime(SLUTTDATO.year, SLUTTDATO.month, SLUTTDATO.day, 22, 15, tzinfo=OSLO)
        kurslager = SqliteKurslager(tilkobling, DEMOUNIVERS)
        for symbol, rader in serier.items():
            if rader:
                kurslager.erstatt_serie(symbol, rader, hentet)

        for dag in dager:
            lager = SqliteVurderingslager(tilkobling, _klokke_for(dag), DEMOUNIVERS)
            for aksje in DEMOUNIVERS:
                fram_til = [r for r in serier[aksje.symbol] if r.dato <= dag]
                lager.skriv(aksje.symbol, dag, vurder(fram_til, dag))
    finally:
        tilkobling.close()


def main(argv: list[str] | None = None) -> None:
    argparse.ArgumentParser(
        description="Lager demobasen data/db/demo.db med oppdiktede tall (FR-411)."
    ).parse_args(argv)
    sti = lagring_sqlite.demo_sti()
    try:
        lag_demobase(sti)
    except IkkeEnDemobase as feil:
        print(f"{feil} Ingenting er skrevet.")
        sys.exit(1)
    except OSError as feil:
        print(f"{sti.name} kunne ikke lages: {type(feil).__name__}. Er den aapen i "
              "et annet program, for eksempel webserveren?")
        sys.exit(1)


if __name__ == "__main__":
    main()
