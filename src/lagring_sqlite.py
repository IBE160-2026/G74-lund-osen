"""SQLite-adapterne for kursdata og vurderinger - story 1.3 og 1.6, FR-406,
FR-408, AD-4, AD-5 og AD-7.

Skall: dette er en av filene som kjenner teknologi. Kjernen ser bare
portene, Kurslager med Kursrad og Vurderingslager med Vurdering og Grunn.

Adapteren tar en aapen tilkobling, ikke en filsti. Basen aapnes ett sted,
aapne_base (story 2.1b): den lager mappa, kobler til og kjoerer migrer(). Hvor
fila ligger, staar i BASE_STI. Hentekommandoen bruker aapne_base, og
webserveren skal gjoere det samme (2.2). Migrasjoner er ikke et eget steg.
Adapteren kjoerer ikke migrasjoner selv, men den nekter aa jobbe mot en base
som ikke staar paa siste versjon i MIGRASJONSKATALOG (story 1.5b, c). Den sjekker bare
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
from kursdata import AKSJEUNIVERS, Aksje, Kursrad, kontroller_skriving
from lagring_fil import DATA_KATALOG
from migrering import MigrasjonsFeil, migrer, siste_versjon, versjon
from oversiktsdata import Oversiktspost
from vurderingsdata import Grunn, Vurdering

MIGRASJONSKATALOG = Path(__file__).resolve().parent / "migrasjoner"

# Story 2.1b: basen ligger i data/db/, oeyeblikksbildene i data/raa/ (se
# lagring_fil.RAA_KATALOG). Ingen annen kode skriver stiene.
BASE_STI = DATA_KATALOG / "db" / "ose.db"

# Story 3.4 (FR-411): demobasen er merket med PRAGMA application_id. Bare
# demokommandoen (src/demo.py) setter merket. Webserveren viser
# «Eksempeltall» naar basen har det, og hentingen nekter en base med det.
# 0x4F534544 er «OSED» i ASCII.
DEMOMERKE = 0x4F534544


def demo_sti() -> Path:
    """Demobasen ligger ved siden av den ekte basen, i data/db/demo.db.

    Regnes fra BASE_STI ved hvert kall, saa fixturen i tests/conftest.py,
    som flytter BASE_STI, ogsaa flytter demobasen.
    """
    return Path(BASE_STI).with_name("demo.db")


def les_merket(tilkobling: sqlite3.Connection) -> int:
    """application_id i basen. 0 naar den ikke er satt."""
    return tilkobling.execute("PRAGMA application_id").fetchone()[0]


def er_demobase(sti: Path) -> bool:
    """Om fila er en demobase. Leser bare, og lager aldri fila.

    En base som ikke finnes eller ikke kan leses, er ikke en demobase, saa
    hentingen gaar videre som foer (story 3.4).
    """
    sti = Path(sti)
    if not sti.is_file():
        return False
    try:
        tilkobling = aapne_base(sti, kjoer_migrasjoner=False, skrivebeskyttet=True)
        try:
            return les_merket(tilkobling) == DEMOMERKE
        finally:
            tilkobling.close()
    except (sqlite3.Error, OSError):
        return False

# Hvor lenge en tilkobling venter paa en laas foer den gir opp (story 2.2,
# BH7 i 2.1b). 5 sekunder er standarden i sqlite3, skrevet ut her saa den er et
# valg og ikke en tilfeldighet. Hentingen og webserveren kan naa bruke basen
# samtidig.
VENTETID_SEKUNDER = 5.0


def aapne_base(
    sti: Path, *, kjoer_migrasjoner: bool = True, skrivebeskyttet: bool = False
) -> sqlite3.Connection:
    """Den ene aapningen av basen - story 2.1b og 2.2.

    Med kjoer_migrasjoner (standard) lages mappa, basen kobles til og
    migrer() kjoeres mot MIGRASJONSKATALOG, saa basen staar paa siste versjon
    naar kalleren faar den. Det gjoer hentingen, og webserveren gjoer det en
    gang per prosess (story 2.2).

    Uten kjoer_migrasjoner aapnes en base som finnes, med mode=rw: en fil som
    mangler, gir sqlite3.OperationalError i stedet for en ny, tom fil, og ingen
    mappe lages. Det bruker webserveren for hver forespoersel, fordi migrer()
    alltid tar skrivelaas. Versjonen kontrolleres av adapterne
    (_krev_siste_versjon).

    Feiler migreringen, lukkes tilkoblingen, og feilen gaar videre. Ingen
    annen kode i src/ kobler til basen selv. Kalleren eier tilkoblingen og
    lukker den.
    """
    sti = Path(sti)
    if not kjoer_migrasjoner:
        # Story 3.4: skrivebeskyttet aapner med mode=ro. Det bruker
        # er_demobase, som bare leser merket.
        modus = "ro" if skrivebeskyttet else "rw"
        return sqlite3.connect(
            sti.resolve().as_uri() + f"?mode={modus}", uri=True, timeout=VENTETID_SEKUNDER
        )
    if skrivebeskyttet:
        raise ValueError("skrivebeskyttet krever kjoer_migrasjoner=False")
    sti.parent.mkdir(parents=True, exist_ok=True)
    tilkobling = sqlite3.connect(sti, timeout=VENTETID_SEKUNDER)
    try:
        migrer(tilkobling, MIGRASJONSKATALOG)
    except BaseException:
        tilkobling.close()
        raise
    return tilkobling


def har_kurser(tilkobling: sqlite3.Connection) -> bool:
    """Om basen har minst en serie i kursserie - story 2.2.

    Webserveren viser den tomme tilstanden naar svaret er nei, i stedet for
    en oversikt uten rader.
    """
    return tilkobling.execute("SELECT 1 FROM kursserie LIMIT 1").fetchone() is not None


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

    def __init__(self, tilkobling: sqlite3.Connection, univers: tuple[Aksje, ...] = AKSJEUNIVERS):
        _krev_siste_versjon(tilkobling)
        self._tilkobling = tilkobling
        self._univers = univers

    def erstatt_serie(self, symbol: str, rader: list[Kursrad], hentet: datetime) -> None:
        rader = list(rader)
        tid = kontroller_skriving(symbol, rader, hentet, self._univers)
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

# Maalingene fra 0004 (story 2.1c) staar her, saa _UPSERT, skriv og les tar
# dem med uten egen kode.
VURDERINGSKOLONNER = (
    "styrke", "retning", "trend", "bevegelse", "interesse", "slutt", "justert_slutt",
    "trend_avvik", "dagens_endring", "standardavvik", "volumforhold",
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


def _kontroller_noekkel(symbol: str, dato: date, symboler: frozenset[str] = SYMBOLER) -> None:
    if not isinstance(dato, date) or isinstance(dato, datetime):
        raise TypeError(f"dato maa vaere datetime.date, fikk {dato!r}")
    if symbol not in symboler:
        raise ValueError(
            f"{symbol!r} er ikke et symbol i "
            f"{'AKSJEUNIVERS' if symboler is SYMBOLER else 'lista som skrives'}. Symbolet er "
            "formen NewsWeb bruker (EQNR), ikke tickeren (EQNR.OL)"
        )


class SqliteVurderingslager:
    """Vurderingslager i SQLite - story 1.6, AD-7, AD-18, AD-20.

    Tar en aapen tilkobling og en klokke. Klokka leses ved hvert kall til
    skriv, ikke naar lageret lages, og testene injiserer den. Dagen regnes i
    Europe/Oslo (norsk_dato), og bare inneveerende boersdag godtas. En eldre
    rad kan leses, men aldri skrives om gjennom porten.

    Det finnes ingen minneutgave. Testene bruker en base i minnet, og
    story 2.5 aapner basen med aapne_base.
    """

    def __init__(
        self,
        tilkobling: sqlite3.Connection,
        klokke: Callable[[], datetime],
        univers: tuple[Aksje, ...] = AKSJEUNIVERS,
    ):
        _krev_siste_versjon(tilkobling)
        self._tilkobling = tilkobling
        self._klokke = klokke
        # Story 3.4: lista som skrives, med AKSJEUNIVERS som standard.
        self._symboler = (
            SYMBOLER if univers is AKSJEUNIVERS
            else frozenset(aksje.symbol for aksje in univers)
        )

    def skriv(self, symbol: str, dato: date, innhold: Vurdering | Grunn) -> bool:
        _kontroller_noekkel(symbol, dato, self._symboler)
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
        # Samme kontroll som skriv: en ticker eller et tidspunkt ville ellers
        # gitt None, som leses som at kommandoen ikke ble kjoert (FR-409).
        _kontroller_noekkel(symbol, dato, self._symboler)
        rad = self._tilkobling.execute(
            "SELECT " + ", ".join(VURDERINGSKOLONNER) + ", grunn FROM vurdering "
            "WHERE symbol = ? AND dato = ?",
            (symbol, dato.isoformat()),
        ).fetchone()
        if rad is None:
            return None
        *felt, grunn = rad
        return _innhold(felt, grunn)


def _innhold(felt, grunn) -> Vurdering | Grunn:
    """Raden i vurdering som Vurdering eller Grunn, ett sted for begge
    adapterne som leser den."""
    if grunn is not None:
        return Grunn(grunn)
    return Vurdering(**dict(zip(VURDERINGSKOLONNER, felt)))


# Spoerringen med join for oversikten - story 2.2b. En rad per aksje i aksje,
# i rowid-rekkefoelge. Alle koblingene er LEFT JOIN, saa en aksje uten kurser
# kommer med og kan navngis under tabellen. Forrige kurs er den nyeste foer
# nyeste, og vurderingen er raden for datoen til nyeste kurs (FR-101, FR-408).
_KURSFELT = "dato, slutt, justert_slutt, volum"
_OVERSIKT = (
    "SELECT a.symbol, a.ticker, a.navn, a.sektor, ks.hentet, "
    + ", ".join(f"n.{k}" for k in _KURSFELT.split(", ")) + ", "
    + ", ".join(f"f.{k}" for k in _KURSFELT.split(", ")) + ", "
    + ", ".join(f"v.{k}" for k in VURDERINGSKOLONNER) + ", v.grunn "
    "FROM aksje a "
    "LEFT JOIN kursserie ks ON ks.symbol = a.symbol "
    "LEFT JOIN kurs n ON n.symbol = a.symbol "
    "AND n.dato = (SELECT MAX(dato) FROM kurs WHERE symbol = a.symbol) "
    "LEFT JOIN kurs f ON f.symbol = a.symbol "
    "AND f.dato = (SELECT MAX(dato) FROM kurs WHERE symbol = a.symbol AND dato < n.dato) "
    "LEFT JOIN vurdering v ON v.symbol = a.symbol AND v.dato = n.dato "
)


def _kursrad(dato, slutt, justert_slutt, volum) -> Kursrad | None:
    if dato is None:
        return None
    return Kursrad(
        dato=date.fromisoformat(dato), slutt=slutt, justert_slutt=justert_slutt, volum=volum
    )


class SqliteOversiktsleser:
    """Oversiktsleser i SQLite - story 2.2b, merknaden under AD-3.

    Bare lesemetoder. Leser aksje, kursserie, kurs og vurdering i en
    spoerring, og skriver aldri. Selskapene kommer fra aksje, ikke fra
    AKSJEUNIVERS (merknaden 2026-10-03 under AD-21).
    """

    def __init__(self, tilkobling: sqlite3.Connection):
        _krev_siste_versjon(tilkobling)
        self._tilkobling = tilkobling

    def oversikt(self) -> list[Oversiktspost]:
        return [
            _post(rad)
            for rad in self._tilkobling.execute(_OVERSIKT + "ORDER BY a.rowid")
        ]

    def post(self, symbol: str) -> Oversiktspost | None:
        rad = self._tilkobling.execute(
            _OVERSIKT + "WHERE a.symbol = ?", (symbol,)
        ).fetchone()
        return _post(rad) if rad is not None else None


def _post(rad) -> Oversiktspost:
    symbol, ticker, navn, sektor, hentet = rad[:5]
    nyeste = _kursrad(*rad[5:9])
    forrige = _kursrad(*rad[9:13])
    *felt, grunn = rad[13:]
    har_rad = grunn is not None or felt[0] is not None
    return Oversiktspost(
        aksje=Aksje(symbol, ticker, navn, sektor),
        nyeste=nyeste,
        forrige=forrige,
        hentet=datetime.fromisoformat(hentet) if hentet is not None else None,
        innhold=_innhold(felt, grunn) if har_rad else None,
    )
