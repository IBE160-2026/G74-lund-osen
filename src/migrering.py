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

Story 1.5b herdet loeperen foer 0002 skrives:
- skjema_versjon lagrer filnavn og sha256 av filteksten (med LF), og en
  anvendt migrasjon som har faatt nytt navn eller nytt innhold, avvises.
- Versjonen leses inne i en BEGIN IMMEDIATE-transaksjon, saa to prosesser som
  migrerer samtidig, ikke kjoerer samme migrasjon to ganger.
- En migrasjonsfil kan ikke styre transaksjonen selv: en setning som begynner
  med BEGIN, COMMIT, END, ROLLBACK, SAVEPOINT eller RELEASE, avvises foer noe
  kjoeres.
- Katalogen velges likt paa Linux og Windows, og 0000, feil filendelse og en
  tom katalog gir egne feilmeldinger.
"""

import hashlib
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

FILNAVN = re.compile(r"^(\d{4})_.+\.sql$")

# Foerste ord i en setning som ville avsluttet eller nestet loeperens
# transaksjon. Ord midt i en setning teller ikke, saa CREATE TRIGGER ... BEGIN
# ... END; er lov.
TRANSAKSJONSORD = {"BEGIN", "COMMIT", "END", "ROLLBACK", "SAVEPOINT", "RELEASE"}
_KOMMENTAR_ELLER_MELLOMROM = re.compile(r"\s+|--[^\n]*(\n|$)|/\*.*?(\*/|$)", re.S)


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

    # En migrasjon per transaksjon. Versjonen og de anvendte filene leses paa
    # nytt inne i hver transaksjon, etter BEGIN IMMEDIATE, saa en annen
    # tilkobling som har migrert i mellomtiden, blir sett.
    while True:
        try:
            tilkobling.execute("BEGIN IMMEDIATE")
        except sqlite3.Error as feil:
            raise MigrasjonsFeil(f"Fikk ikke startet migreringen: {feil}") from feil
        try:
            anvendt = _anvendte(tilkobling)
            _kontroller(anvendt, filer, katalog)
            if len(anvendt) == len(filer):
                tilkobling.execute("COMMIT")
                return len(anvendt)
            _kjoer(tilkobling, *filer[len(anvendt)])
            tilkobling.execute("COMMIT")
        except BaseException:
            if tilkobling.in_transaction:
                tilkobling.execute("ROLLBACK")
            raise


def _migrasjoner(katalog: Path) -> list[tuple[int, Path]]:
    """Migrasjonsfilene sortert paa nummer, 1, 2, 3 ... uten hull.

    Andre filer enn .sql ignoreres. En .sql-fil med feil navn er en feil -
    en migrasjon som stille hoppes over er verre enn en som stopper.
    """
    if not katalog.is_dir():
        raise MigrasjonsFeil(f"Fant ikke migrasjonskatalogen {katalog}")

    # Filendelsen sammenliknes her i Python, ikke i et glob-moenster. glob
    # skiller store og smaa bokstaver paa Linux, men ikke paa Windows, og da
    # ble 0002_ny.SQL hoppet stille over paa den ene plattformen og avvist paa
    # den andre.
    etter_nummer: dict[int, Path] = {}
    for sti in sorted(katalog.iterdir()):
        if not sti.is_file() or sti.suffix.lower() != ".sql":
            continue
        if sti.suffix != ".sql":
            raise MigrasjonsFeil(
                f"{sti.name} har filendelsen {sti.suffix}. En migrasjon skal "
                "ha .sql med smaa bokstaver (NNNN_navn.sql)"
            )
        treff = FILNAVN.match(sti.name)
        if not treff:
            raise MigrasjonsFeil(
                f"{sti.name} er ikke navngitt som en migrasjon (NNNN_navn.sql)"
            )
        nummer = int(treff.group(1))
        if nummer == 0:
            raise MigrasjonsFeil(
                f"{sti.name}: 0000 er ikke et gyldig nummer, foerste migrasjon er 0001"
            )
        if nummer in etter_nummer:
            raise MigrasjonsFeil(
                f"To migrasjoner har nummer {nummer:04d}: "
                f"{etter_nummer[nummer].name} og {sti.name}"
            )
        etter_nummer[nummer] = sti

    if not etter_nummer:
        raise MigrasjonsFeil(f"Ingen migrasjoner i {katalog}")

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


def _tekst(sti: Path) -> str:
    """Filteksten med LF. En utsjekking med core.autocrlf=true gir CRLF paa
    Windows og LF paa Linux, og samme fil skal gi samme hash begge steder."""
    return sti.read_text(encoding="utf-8").replace("\r\n", "\n")


def _sha256(sti: Path) -> str:
    return hashlib.sha256(_tekst(sti).encode("utf-8")).hexdigest()


def _anvendte(tilkobling: sqlite3.Connection) -> list[tuple[int, str, str]]:
    """(versjon, fil, sha256) for hver anvendt migrasjon, sortert paa versjon.

    En skjema_versjon uten sha256 er fra foer 1.5b. Den oppgraderes ikke
    stille, fordi en oppgradering maatte stolt paa filene slik de er naa, og
    det er nettopp endrede filer hashen skal avsloere.
    """
    kolonner = {
        rad[1] for rad in tilkobling.execute("PRAGMA table_info(skjema_versjon)")
    }
    if not kolonner:
        return []
    if "sha256" not in kolonner:
        raise MigrasjonsFeil(
            "skjema_versjon mangler kolonnen sha256: basen er laget foer 1.5b. "
            "Bygg den paa nytt fra raadatafilene (AD-6) i stedet for aa "
            "oppgradere den."
        )
    return tilkobling.execute(
        "SELECT versjon, fil, sha256 FROM skjema_versjon ORDER BY versjon"
    ).fetchall()


def _kontroller(
    anvendt: list[tuple[int, str, str]], filer: list[tuple[int, Path]], katalog
) -> None:
    """Basen og katalogen skal beskrive samme historikk."""
    if len(anvendt) > len(filer):
        raise MigrasjonsFeil(
            f"Basen er paa versjon {len(anvendt)}, men {katalog} har bare "
            f"{len(filer)} migrasjoner. Basen er migrert av en nyere utgave av koden."
        )
    for (versjon_nr, fil, sha), (_, sti) in zip(anvendt, filer):
        if fil != sti.name:
            raise MigrasjonsFeil(
                f"Migrasjon {versjon_nr:04d} ble kjoert som {fil}, men {katalog} "
                f"har {sti.name}. Et anvendt nummer har faatt nytt filnavn."
            )
        if sha != _sha256(sti):
            raise MigrasjonsFeil(
                f"{fil} er endret etter at den ble kjoert. En kjoert migrasjon "
                "endres ikke; skriv en ny."
            )


def _forhaandssjekk(setninger: list[str], sti: Path) -> None:
    """Avvis fila hvis en setning begynner med et transaksjonsord.

    Sjekken maa skje foer noe kjoeres: en COMMIT midt i fila ville ha
    committet setningene foer den, og da er basen halvveis migrert uansett hva
    loeperen gjoer etterpaa. Mellomrom og kommentarer foran ordet hoppes over.
    """
    for nummer, setning in enumerate(setninger, 1):
        pos = 0
        while treff := _KOMMENTAR_ELLER_MELLOMROM.match(setning, pos):
            if treff.end() == pos:
                break
            pos = treff.end()
        ord_ = re.match(r"[A-Za-z]+", setning[pos:])
        if ord_ and ord_.group(0).upper() in TRANSAKSJONSORD:
            raise MigrasjonsFeil(
                f"{sti.name}, setning {nummer}, begynner med {ord_.group(0)}. "
                "Loeperen styrer transaksjonen selv, og en migrasjonsfil kan "
                "ikke inneholde transaksjonskontroll."
            )


def _kjoer(tilkobling: sqlite3.Connection, nummer: int, sti: Path) -> None:
    """En migrasjon og dens versjonsrad, i transaksjonen migrer() har aapnet."""
    tekst = _tekst(sti)
    setninger = _setninger(tekst)
    _forhaandssjekk(setninger, sti)
    try:
        tilkobling.execute(
            "CREATE TABLE IF NOT EXISTS skjema_versjon ("
            "versjon INTEGER PRIMARY KEY, fil TEXT NOT NULL, "
            "sha256 TEXT NOT NULL, anvendt TEXT NOT NULL)"
        )
        for i, setning in enumerate(setninger, 1):
            tilkobling.execute(setning)
            # Ekstra sikring bak forhaandssjekken: er transaksjonen borte, er
            # resten av fila i ferd med aa kjoeres uten den.
            if not tilkobling.in_transaction:
                raise MigrasjonsFeil(
                    f"{sti.name}, setning {i}, avsluttet transaksjonen. "
                    "Migreringen er stoppet."
                )
        tilkobling.execute(
            "INSERT INTO skjema_versjon (versjon, fil, sha256, anvendt) "
            "VALUES (?, ?, ?, ?)",
            (nummer, sti.name, hashlib.sha256(tekst.encode("utf-8")).hexdigest(),
             datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )
    except sqlite3.Error as feil:
        if tilkobling.in_transaction:
            tilkobling.execute("ROLLBACK")
        raise MigrasjonsFeil(
            f"{sti.name} feilet og er rullet tilbake: {feil}. "
            f"Basen staar paa versjon {versjon(tilkobling)}."
        ) from feil
