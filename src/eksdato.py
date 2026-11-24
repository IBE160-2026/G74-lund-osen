"""Eks.datoer foert inn for haand - story 2.14, FR-414 (gruppens svar 24.11
kl. 13:05).

uv run python src/eksdato.py <symbol> <eks.dato> --sjekket <dato> --kilde <adresse>

Kommandoen tar en kommende eks.dato for ett symbol, lest av en av oss paa
selskapets egen side, og lagrer den i tabellen eksdato (0016) med datoen den
ble sjekket og adressen den ble lest paa. Den gjoer ingen nettkall: siden
hentes aldri av programmet. Datoene staar bare i basen, aldri i en sporet
fil (regel 16).

Et symbol faar ingen dato foer vilkaarene for nettstedet er lest og foert i
docs/kilder-og-rettigheter.md, i tabellen under «Selskapenes egne sider
(eks.datoer)». Kommandoen leser tabellen og avviser et symbol uten en rad med
nettsted, datoen vilkaarene ble lest, og vurderingen «ja». Kilden maa vaere en
adresse paa det nettstedet.

En ny sjekk av samme dato oppdaterer datoen den ble sjekket. En flyttet dato
erstatter den gamle. En eldre sjekk skriver ikke over en nyere. Kommandoen er
eneste skriver av tabellen; webserveren skriver den aldri (AD-3, AD-10).
Kodene er 0 (lagret), 1 (avvist, eller basen kan ikke brukes) og 2 (feil i
argumentene, fra argparse).
"""

import argparse
import re
import sqlite3
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit

import lagring_sqlite
from boersdag import norsk_dato
from lagring_sqlite import aapne_base
from migrering import MigrasjonsFeil

VILKAAR = Path(__file__).resolve().parents[1] / "docs" / "kilder-og-rettigheter.md"
OVERSKRIFT = "## Selskapenes egne sider (eks.datoer)"
KOLONNER = ("Symbol", "Nettsted", "Vilkår lest", "Vurdering")
JA = "ja"

_SYMBOL = re.compile(r"[A-Z0-9]{1,12}")
_NETTSTED = re.compile(r"(?=.{4,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}")
_DATO = re.compile(r"\d{4}-\d{2}-\d{2}")


class Avvist(ValueError):
    """Datoen ble ikke lagret. Meldingen sier hvorfor."""


def _dato(tekst: str, hva: str) -> date:
    """En ISO-dato som finnes, skrevet AAAA-MM-DD."""
    if not _DATO.fullmatch(tekst):
        raise Avvist(f"{hva} må skrives som ÅÅÅÅ-MM-DD.")
    try:
        return date.fromisoformat(tekst)
    except ValueError:
        raise Avvist(f"{hva} er ikke en dato som finnes.") from None


def les_vilkaar(fil: Path, idag: date) -> dict[str, str]:
    """Symbolene vilkaarene er foert for, med nettstedet - story 2.14.

    Leser tabellen under OVERSKRIFT i docs/kilder-og-rettigheter.md. En rad
    teller naar symbolet og nettstedet har riktig form, «Vilkår lest» er en
    dato som finnes og ikke er etter i dag, og vurderingen begynner med
    «ja». Alt annet, ogsaa en fil eller en del som mangler, gir ingen
    symboler: da faar ingen en dato (NFR-08). Bare lesing."""
    try:
        tekst = fil.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}
    linjer = tekst.splitlines()
    try:
        start = next(i for i, linje in enumerate(linjer) if linje.strip() == OVERSKRIFT)
    except StopIteration:
        return {}
    godtatt: dict[str, str] = {}
    forkastet: set[str] = set()
    for linje in linjer[start + 1 :]:
        if linje.startswith("## "):
            break
        if not linje.lstrip().startswith("|"):
            continue
        celler = [celle.strip().strip("`") for celle in linje.strip().strip("|").split("|")]
        if len(celler) != len(KOLONNER) or tuple(celler) == KOLONNER or set(celler[0]) <= set("-: "):
            continue
        symbol, nettsted, lest, vurdering = celler
        if not _SYMBOL.fullmatch(symbol):
            continue
        try:
            lest_dato = _dato(lest, "Vilkår lest")
        except Avvist:
            lest_dato = None
        i_orden = (
            _NETTSTED.fullmatch(nettsted) is not None
            and lest_dato is not None
            and lest_dato <= idag
            and re.match(rf"{JA}\b", vurdering, flags=re.IGNORECASE) is not None
        )
        # To rader for samme symbol der en av dem ikke er i orden: ingen dato.
        if not i_orden or symbol in godtatt and godtatt[symbol] != nettsted:
            forkastet.add(symbol)
            continue
        godtatt[symbol] = nettsted
    return {symbol: nettsted for symbol, nettsted in godtatt.items() if symbol not in forkastet}


def _paa_nettstedet(kilde: str, nettsted: str) -> bool:
    """Om kilde er en adresse paa nettstedet, eller et underdomene av det."""
    try:
        deler = urlsplit(kilde)
        vert = (deler.hostname or "").lower().rstrip(".")
    except ValueError:
        return False
    return deler.scheme in ("http", "https") and (vert == nettsted or vert.endswith("." + nettsted))


def foer_inn(
    tilkobling: sqlite3.Connection,
    symbol: str,
    eks_dato: str,
    sjekket: str,
    kilde: str,
    vilkaar: dict[str, str],
    idag: date,
) -> str:
    """Lagrer en kommende eks.dato for symbol, eller reiser Avvist med
    grunnen. Gir linja til utskriften. Ingen nettkall."""
    symbol = symbol.strip().upper()
    kilde = kilde.strip()
    if not _SYMBOL.fullmatch(symbol):
        raise Avvist("Symbolet har ikke formen til et symbol i lista.")
    eks = _dato(eks_dato, "Eks.datoen")
    sjekk = _dato(sjekket, "Datoen for sjekken")
    if sjekk > idag:
        raise Avvist("Datoen for sjekken er etter i dag.")
    if eks < sjekk:
        raise Avvist("Eks.datoen er før dagen den ble sjekket, så den er ikke en kommende dato.")
    if not kilde or len(kilde) > 500:
        raise Avvist("Kilden mangler, eller er lengre enn 500 tegn.")
    i_lista = tilkobling.execute("SELECT 1 FROM aksje WHERE symbol = ? AND ut IS NULL", (symbol,)).fetchone()
    if i_lista is None:
        raise Avvist(f"{symbol} står ikke i lista appen følger.")
    nettsted = vilkaar.get(symbol)
    if nettsted is None:
        raise Avvist(
            f"Vilkårene for nettstedet til {symbol} er ikke ført i docs/kilder-og-rettigheter.md, "
            f"under «{OVERSKRIFT.removeprefix('## ')}». Les vilkårene og før raden først (FR-414)."
        )
    if not _paa_nettstedet(kilde, nettsted):
        raise Avvist(f"Kilden er ikke en adresse på {nettsted}, som er nettstedet vilkårene er ført for.")
    with tilkobling:
        gammel = tilkobling.execute("SELECT eks_dato, sjekket FROM eksdato WHERE symbol = ?", (symbol,)).fetchone()
        if gammel is not None and gammel[1] > sjekk.isoformat():
            raise Avvist(f"{symbol} har alt en dato som er sjekket senere, {gammel[1]}. Ingenting er endret.")
        tilkobling.execute(
            "INSERT INTO eksdato (symbol, eks_dato, sjekket, kilde) VALUES (?, ?, ?, ?) "
            "ON CONFLICT (symbol) DO UPDATE SET eks_dato = excluded.eks_dato, sjekket = excluded.sjekket, "
            "kilde = excluded.kilde",
            (symbol, eks.isoformat(), sjekk.isoformat(), kilde),
        )
    if gammel is None:
        return f"{symbol}: eks.datoen {eks.isoformat()} er lagret, sjekket {sjekk.isoformat()}."
    if gammel[0] == eks.isoformat():
        return f"{symbol}: eks.datoen {eks.isoformat()} står, og er nå sjekket {sjekk.isoformat()}."
    return f"{symbol}: eks.datoen er flyttet fra {gammel[0]} til {eks.isoformat()}, sjekket {sjekk.isoformat()}."


def kjoer(
    base_sti: Path,
    symbol: str,
    eks_dato: str,
    sjekket: str,
    kilde: str,
    idag: date,
    skriv: Callable[[str], None] = print,
    vilkaarsfil: Path = VILKAAR,
) -> int:
    """Kommandoen mot en base. Gir utgangskoden: 0 lagret, 1 ellers."""
    if lagring_sqlite.er_demobase(base_sti):
        skriv(f"{Path(base_sti).name} er en demobase med oppdiktede tall. Eks.datoer føres ikke inn der.")
        return 1
    if not Path(base_sti).exists():
        skriv(f"Basen {Path(base_sti).name} finnes ikke. Hent kursene først.")
        return 1
    try:
        tilkobling = aapne_base(base_sti)
    except (sqlite3.Error, OSError, RuntimeError, MigrasjonsFeil) as feil:
        skriv(f"Basen {Path(base_sti).name} kunne ikke åpnes ({type(feil).__name__}). Ingenting er lagret.")
        return 1
    try:
        skriv(foer_inn(tilkobling, symbol, eks_dato, sjekket, kilde, les_vilkaar(vilkaarsfil, idag), idag))
    except Avvist as grunn:
        skriv(f"Ikke lagret: {grunn}")
        return 1
    except sqlite3.Error as feil:
        skriv(f"Ikke lagret: basen avviste raden ({type(feil).__name__}).")
        return 1
    finally:
        tilkobling.close()
    return 0


def main(argv: list[str] | None = None) -> None:
    tolker = argparse.ArgumentParser(
        description="Fører inn en kommende eks.dato for ett symbol, lest for hånd på selskapets egen side. "
        "Ingen nettkall."
    )
    tolker.add_argument("symbol", help="symbolet i lista, for eksempel slik det står i tabellen på oversikten")
    tolker.add_argument("eks_dato", metavar="eks.dato", help="eks.datoen, ÅÅÅÅ-MM-DD")
    tolker.add_argument("--sjekket", required=True, metavar="DATO", help="dagen datoen ble lest på siden, ÅÅÅÅ-MM-DD")
    tolker.add_argument("--kilde", required=True, metavar="ADRESSE", help="adressen til siden datoen ble lest på")
    valg = tolker.parse_args(argv)
    idag = norsk_dato(datetime.now(timezone.utc))
    sys.exit(
        kjoer(lagring_sqlite.BASE_STI, valg.symbol, valg.eks_dato, valg.sjekket, valg.kilde, idag, vilkaarsfil=VILKAAR)
    )


if __name__ == "__main__":
    main()
