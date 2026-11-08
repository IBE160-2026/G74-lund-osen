"""Å velge og bytte aksjer - story 2.12, FR-412, AD-3, AD-7, AD-10, AD-21.

Webserveren skriver bare ønsket, i tabellen oenske (0010), gjennom
Valglager. Kveldens henting tar ønskene i bruk med ta_i_bruk før den leser
lista (2.11), og er fortsatt eneste skriver av aksje, kurser og vurderinger
(AD-3). Ingen kall går herfra, og webserveren henter aldri (AD-10).

Spesifikasjonen er spec-2-12-velge-og-bytte-aksjer.md:
- En egen aksje er en aksje som er tatt inn i lista fra et ønske på siden
  (spørsmål 1), i den ekte versjonen og i demoen.
- Lista over Oslo Børs er tabellen boersliste, fylt med les_boerslista av
  fila fra malinger.md §40, uten kall (spørsmål 2).
- Taket er TAK aksjer: lista, pluss ønskene om å følge, minus ønskene om å
  fjerne (spørsmål 5, avgjørelsen 21.10 kl. 16:47).
- Brukeren velger bransjen blant de 13 (spørsmål 4, svaret 08.11 kl. 11:57).
- Omsetningen er den siste målingen i omsetning (2.13). Under GRENSE_MNOK,
  eller ikke målt, er aksjen «Utenfor målingen» (spørsmål 7).
"""

import json
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from kursdata import Aksje

TAK = 18
# Dagskvoten hos EODHD (gratisnivået) og kallet til hovedindeksen.
KVOTE = 20
INDEKSKALL = 1
# Signalet er målt på aksjer som omsettes for over 32 MNOK om dagen (utdraget
# 08.11 §1, malinger.md §36).
GRENSE_MNOK = 32.0
BRANSJENE = (
    "Energi",
    "Finans",
    "Industri",
    "Materialer",
    "Shipping",
    "Telekom",
    "Sjømat",
    "Konsum",
    "Forbruk",
    "Teknologi",
    "Helse",
    "Eiendom",
    "Kraft",
)
FOLG = "folg"
FJERN = "fjern"
AKSJETYPE = "Common Stock"


class UgyldigValg(ValueError):
    """Et valg siden ikke godtar: en kode som ikke er på Oslo Børs, en
    bransje utenfor de 13, eller en aksje som alt følges eller ikke er i lista."""


class ListaErFull(ValueError):
    """Lista har alt TAK aksjer, regnet med ønskene."""


@dataclass(frozen=True)
class Oenske:
    id: int
    handling: str
    symbol: str
    navn: str | None
    sektor: str | None
    laget: str


@dataclass(frozen=True)
class Boersaksje:
    kode: str
    navn: str


def utenfor_maalingen(median_nok: float | None) -> bool:
    """Spørsmål 7: under 32 MNOK, eller ikke målt."""
    return median_nok is None or median_nok < GRENSE_MNOK * 1_000_000


def kallene(i_lista: int, folg: int, fjern: int) -> tuple[int, int, int]:
    """(siste henting, neste henting, igjen til nye forsøk) i kall, med
    hovedindeksen, som teksten i dialogen (utdraget §1)."""
    sist = i_lista + INDEKSKALL
    neste = i_lista + folg - fjern + INDEKSKALL
    return sist, neste, KVOTE - neste


def har_tabellene(tilkobling: sqlite3.Connection) -> bool:
    """Har basen tabellene fra 0010? En base en versjon bak har dem ikke, og
    da viser siden ikke valget. En base som ikke kan leses, gir False."""
    try:
        return (
            tilkobling.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'oenske'").fetchone()
            is not None
        )
    except sqlite3.Error:
        return False


class Valglager:
    """Ønskene og lista over Oslo Børs i SQLite (0010). Bare oenske skrives.

    tilkobling er basen siden leser, migrert til siste versjon. klokke gir
    tiden ønsket lages."""

    def __init__(self, tilkobling: sqlite3.Connection, klokke: Callable[[], datetime]):
        self._t = tilkobling
        self._klokke = klokke

    # --- Lesing --------------------------------------------------------

    def egne(self) -> frozenset[str]:
        """Spørsmål 1: aksjene i lista som er tatt inn fra et ønske på siden."""
        return egne_i_lista(self._t)

    def i_lista(self) -> list[Aksje]:
        """Aksjene i lista nå (ut er ikke satt), i rowid-rekkefølge."""
        return [
            Aksje(*rad)
            for rad in self._t.execute("SELECT symbol, ticker, navn, sektor FROM aksje WHERE ut IS NULL ORDER BY rowid")
        ]

    def ventende(self) -> list[Oenske]:
        return [
            Oenske(*rad)
            for rad in self._t.execute(
                "SELECT id, handling, symbol, navn, sektor, laget FROM oenske "
                "WHERE tatt_i_bruk IS NULL AND avvist IS NULL ORDER BY id"
            )
        ]

    def antall(self) -> int:
        """Lista med ønskene: TAK er grensen for dette."""
        ventende = self.ventende()
        return (
            len(self.i_lista()) + sum(o.handling == FOLG for o in ventende) - sum(o.handling == FJERN for o in ventende)
        )

    def boersaksje(self, kode: str) -> Boersaksje | None:
        rad = self._t.execute("SELECT kode, navn FROM boersliste WHERE kode = ?", (kode,)).fetchone()
        return Boersaksje(*rad) if rad else None

    def sok(self, tekst: str, grense: int = 20) -> list[Boersaksje]:
        """Aksjene på Oslo Børs der koden eller navnet har teksten, uten dem
        som er i lista eller venter på å bli fulgt."""
        tekst = (tekst or "").strip()
        if not tekst:
            return []
        opptatt = {a.symbol for a in self.i_lista()} | {o.symbol for o in self.ventende() if o.handling == FOLG}
        moenster = f"%{tekst}%"
        rader = self._t.execute(
            "SELECT kode, navn FROM boersliste WHERE kode LIKE ? OR navn LIKE ? ORDER BY kode",
            (moenster, moenster),
        )
        return [Boersaksje(*r) for r in rader if r[0] not in opptatt][:grense]

    def omsetning(self, symbol: str) -> tuple[float | None, date | None]:
        """Den siste målingen med et tall i omsetning (2.13): (median i NOK,
        dagen den ble målt), eller (None, None)."""
        rad = self._t.execute(
            "SELECT median_omsetning, maalt FROM omsetning WHERE symbol = ? AND median_omsetning IS NOT NULL "
            "ORDER BY maalt DESC LIMIT 1",
            (symbol,),
        ).fetchone()
        if rad is None:
            return None, None
        return float(rad[0]), datetime.fromisoformat(rad[1]).date()

    # --- Skriving (bare oenske) ----------------------------------------

    def folg(self, kode: str, sektor: str, bytt_ut: str | None = None) -> None:
        """Ønsket om å følge kode, med bransjen brukeren valgte. Med bytt_ut
        er det et bytte: ønsket om å fjerne den kommer i samme transaksjon,
        og taket regnes med begge."""
        aksje = self.boersaksje(kode)
        if aksje is None:
            raise UgyldigValg("koden står ikke i lista over Oslo Børs")
        if sektor not in BRANSJENE:
            raise UgyldigValg("bransjen er ikke en av de 13")
        if kode in {a.symbol for a in self.i_lista()} or any(
            o.symbol == kode and o.handling == FOLG for o in self.ventende()
        ):
            raise UgyldigValg("aksjen følges alt")
        if bytt_ut is not None:
            self._kan_fjernes(bytt_ut)
        if bytt_ut is None and self.antall() >= TAK:
            raise ListaErFull("Lista er full. Fjern en aksje for å følge en annen.")
        laget = self._klokke().isoformat()
        with self._t:
            if bytt_ut is not None:
                self._t.execute("INSERT INTO oenske (handling, symbol, laget) VALUES ('fjern', ?, ?)", (bytt_ut, laget))
            self._t.execute(
                "INSERT INTO oenske (handling, symbol, navn, sektor, laget) VALUES ('folg', ?, ?, ?, ?)",
                (kode, aksje.navn, sektor, laget),
            )

    def _kan_fjernes(self, symbol: str) -> None:
        if symbol not in {a.symbol for a in self.i_lista()}:
            raise UgyldigValg("aksjen er ikke i lista")
        if any(o.symbol == symbol and o.handling == FJERN for o in self.ventende()):
            raise UgyldigValg("aksjen fjernes alt ved neste henting")

    def fjern(self, symbol: str) -> None:
        self._kan_fjernes(symbol)
        with self._t:
            self._t.execute(
                "INSERT INTO oenske (handling, symbol, laget) VALUES ('fjern', ?, ?)",
                (symbol, self._klokke().isoformat()),
            )

    def angre(self, oenske_id: int) -> None:
        """Sletter et ønske som ikke er tatt i bruk. Et ønske som er tatt i
        bruk eller avvist, står (det er historikken for lista)."""
        with self._t:
            slettet = self._t.execute(
                "DELETE FROM oenske WHERE id = ? AND tatt_i_bruk IS NULL AND avvist IS NULL", (oenske_id,)
            ).rowcount
        if not slettet:
            raise UgyldigValg("ønsket finnes ikke, eller er alt tatt i bruk")


def egne_i_lista(tilkobling: sqlite3.Connection) -> frozenset[str]:
    """Aksjene i lista (ut er ikke satt) med et ønske om å følge som er tatt i
    bruk, og ikke et senere ønske om å fjerne som er tatt i bruk."""
    return frozenset(
        s
        for (s,) in tilkobling.execute(
            "SELECT a.symbol FROM aksje a WHERE a.ut IS NULL AND EXISTS (SELECT 1 FROM oenske o "
            "WHERE o.symbol = a.symbol AND o.handling = 'folg' AND o.tatt_i_bruk IS NOT NULL)"
        )
    )


# --- Hentekommandoen --------------------------------------------------------


def les_boerslista(tilkobling: sqlite3.Connection, fil: Path) -> int:
    """Fyller boersliste med typen «Common Stock» fra fila (malinger.md §40),
    uten kall (spørsmål 2). Lista byttes helt. Gir antallet."""
    rader = json.loads(Path(fil).read_text(encoding="utf-8"))
    if not isinstance(rader, list):
        raise ValueError("lista er ikke en liste")
    aksjer: dict[str, str] = {}
    for rad in rader:
        if not isinstance(rad, dict) or rad.get("Type") != AKSJETYPE:
            continue
        kode, navn = rad.get("Code"), rad.get("Name")
        if isinstance(kode, str) and isinstance(navn, str) and kode.strip() and navn.strip():
            aksjer.setdefault(kode.strip().upper(), navn.strip())
    with tilkobling:
        tilkobling.execute("DELETE FROM boersliste")
        tilkobling.executemany("INSERT INTO boersliste (kode, navn) VALUES (?, ?)", sorted(aksjer.items()))
    return len(aksjer)


def ta_i_bruk(tilkobling: sqlite3.Connection, dato: date) -> list[str]:
    """Ønskene som venter, i den rekkefølgen de ble laget, for børsdagen dato.

    Å følge legger aksjen inn i aksje med inn = dato, eller tar den inn igjen
    (ut blir NULL). Å fjerne setter ut = dato, så kveldens henting ikke henter
    den. Kom aksjen inn samme dag (inn = dato), kan ut ikke være dato, og da
    slettes raden i stedet, fordi den ikke har kurser ennå. Gir linjene til
    utskriften."""
    linjer: list[str] = []
    dag = dato.isoformat()
    with tilkobling:
        for id_, handling, symbol, navn, sektor in tilkobling.execute(
            "SELECT id, handling, symbol, navn, sektor FROM oenske "
            "WHERE tatt_i_bruk IS NULL AND avvist IS NULL ORDER BY id"
        ).fetchall():
            rad = tilkobling.execute("SELECT inn, ut FROM aksje WHERE symbol = ?", (symbol,)).fetchone()
            if handling == FOLG:
                if rad is None:
                    tilkobling.execute(
                        "INSERT INTO aksje (symbol, ticker, navn, sektor, inn) VALUES (?, ?, ?, ?, ?)",
                        (symbol, f"{symbol}.OL", navn, sektor, dag),
                    )
                elif rad[1] is not None:
                    tilkobling.execute("UPDATE aksje SET ut = NULL, sektor = ? WHERE symbol = ?", (sektor, symbol))
                linjer.append(f"{symbol} er tatt inn i lista fra {dag}.")
            else:
                if rad is None or rad[1] is not None:
                    tilkobling.execute("UPDATE oenske SET avvist = ? WHERE id = ?", (f"{dag}: ikke i lista", id_))
                    continue
                if rad[0] is not None and rad[0] >= dag:
                    tilkobling.execute("DELETE FROM aksje WHERE symbol = ?", (symbol,))
                else:
                    tilkobling.execute("UPDATE aksje SET ut = ? WHERE symbol = ?", (dag, symbol))
                linjer.append(f"{symbol} er tatt ut av lista fra {dag}. Det som er lagret, står.")
            tilkobling.execute("UPDATE oenske SET tatt_i_bruk = ? WHERE id = ?", (dag, id_))
    return linjer


def uten_rader(tilkobling: sqlite3.Connection, dato: date) -> list[str]:
    """Spørsmål 6: en egen aksje som kom inn før dato og ikke har fått en
    eneste kurs, tas ut fra dato, og ønsket merkes avvist. Det sjekkes
    kvelden etter, så et nytt forsøk samme kveld fortsatt kan hente den.
    Radene i vurdering står (AD-7). Gir linjene til utskriften."""
    dag = dato.isoformat()
    linjer = []
    with tilkobling:
        for symbol, inn in tilkobling.execute(
            "SELECT symbol, inn FROM aksje WHERE inn IS NOT NULL AND inn < ? AND ut IS NULL "
            "AND NOT EXISTS (SELECT 1 FROM kurs WHERE kurs.symbol = aksje.symbol)",
            (dag,),
        ).fetchall():
            if symbol not in egne_i_lista(tilkobling):
                continue
            tilkobling.execute("UPDATE aksje SET ut = ? WHERE symbol = ?", (dag, symbol))
            tilkobling.execute(
                "UPDATE oenske SET tatt_i_bruk = NULL, avvist = ? WHERE symbol = ? AND handling = 'folg' "
                "AND tatt_i_bruk = ?",
                (f"{dag}: ga ingen kurser", symbol, inn),
            )
            linjer.append(f"{symbol} ga ingen kurser etter at den ble valgt, og er tatt ut av lista igjen.")
    return linjer
