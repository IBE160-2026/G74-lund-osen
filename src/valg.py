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
- Bransjen er den faste i ferdige_lister.BRANSJE, og brukeren velger den ikke
  selv (story 8.22, svaret 10.11 kl. 13:38, som erstatter svaret 08.11 kl. 11:57).
- Omsetningen er den siste målingen i omsetning (2.13). Under GRENSE_MNOK,
  eller ikke målt, er aksjen «Utenfor målingen» (spørsmål 7).
"""

import json
import sqlite3
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from kursdata import Aksje
from tallformat import tall

TAK = 18
# Story 8.26 (gruppens svar 11.11 kl. 17:47, tillegg 3): der «lista» betydde
# alle aksjene appen følger, sies det slik, og ikke i rødt. Var «Lista er
# full. Fjern en aksje for å følge en annen.» og «… for å angre dette.».
FULL = f"Appen følger allerede {TAK} aksjer, som er taket. Fjern en for å følge en annen."
FULL_ANGRE = f"Appen følger allerede {TAK} aksjer, som er taket. Fjern en for å angre dette."
# Dagskvoten hos EODHD (gratisnivået) og kallet til hovedindeksen.
KVOTE = 20
INDEKSKALL = 1
# Story 8.23 (gjennomgangen, BH15): hver aksje bruker ett kall om dagen.
KALL_PER_AKSJE = 1
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
OSLO = ZoneInfo("Europe/Oslo")


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


def utenfor_tekst(median_nok: float | None, maalt: date | None, *, kursene: bool = False) -> str:
    """Teksten bak merket «Utenfor målingen» (utdraget 08.11 §2). Story
    8.11c: er medianen regnet av kursene i appen, som i de ferdige listene,
    står dagen som den siste dagen med kurser."""
    if median_nok is None or maalt is None:
        return "Omsetningen er ikke målt ennå. Signalet er målt på aksjer som omsettes for over 32 MNOK om dagen."
    # Gjennomgangen av 8.11c (BH5): tallet med tall(), som på «Følg en aksje» (regel 21).
    mnok = tall(median_nok / 1_000_000, "mnok")
    kilde = f"regnet av kursene til {maalt:%d.%m.%Y}" if kursene else f"målt {maalt:%d.%m.%Y}"
    return (
        f"Median daglig omsetning de 3 siste månedene er {mnok} MNOK, {kilde}. Signalet er målt på "
        "aksjer som omsettes for over 32 MNOK om dagen, og er ikke prøvd på en aksje som omsettes så lite."
    )


def kallene(i_lista: int, folg: int, fjern: int) -> tuple[int, int, int]:
    """(siste henting, neste henting, igjen til nye forsøk) i kall, med
    hovedindeksen, som teksten i dialogen (utdraget §1)."""
    sist = i_lista * KALL_PER_AKSJE + INDEKSKALL
    neste = (i_lista + folg - fjern) * KALL_PER_AKSJE + INDEKSKALL
    return sist, neste, KVOTE - neste


@dataclass(frozen=True)
class SisteHenting:
    """Story 8.22, tillegg 4 (svaret 10.11 kl. 22:50): dagen for den siste
    hentingen og seriene som ble lagret den dagen. Hver serie er ett kall,
    så serier er det minste antallet kall hentingen brukte."""

    dag: date
    serier: int


def siste_henting(tilkobling: sqlite3.Connection) -> SisteHenting | None:
    """Den siste hentingen, regnet av basen alene: uten kall og uten å lese
    .env (AD-10). Dagen er den siste i kursserie.hentet og
    indeksserie.hentet, i Europe/Oslo, og serier er seriene som sist ble
    hentet den dagen. Kallene var minst så mange (gjennomgangen, BH2, ECH3):
    et kall som feilet, et nytt forsøk, målingen med bonuskvoten og en serie
    som ble hentet to ganger samme dag, telles ikke. En verdi som ikke kan
    leses, hoppes over (ECH4). Feil i basen går til kalleren, som skjuler
    delen som før. None: ingen henting har lagret en serie."""
    hentet = []
    for tabell in ("kursserie", "indeksserie"):
        for (verdi,) in tilkobling.execute(f"SELECT hentet FROM {tabell}"):
            try:
                hentet.append(datetime.fromisoformat(verdi).astimezone(OSLO).date())
            except (ValueError, TypeError):
                continue
    if not hentet:
        return None
    dag = max(hentet)
    return SisteHenting(dag, sum(d == dag for d in hentet))


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
        som er i lista eller venter på å bli fulgt. Gjennomgangen (ECH6): %
        og _ i teksten er vanlige tegn, ikke jokertegn."""
        tekst = (tekst or "").strip()
        if not tekst:
            return []
        opptatt = {a.symbol for a in self.i_lista()} | {o.symbol for o in self.ventende() if o.handling == FOLG}
        moenster = "%" + tekst.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        rader = self._t.execute(
            "SELECT kode, navn FROM boersliste WHERE kode LIKE ? ESCAPE '\\' OR navn LIKE ? ESCAPE '\\' ORDER BY kode",
            (moenster, moenster),
        )
        return [Boersaksje(*r) for r in rader if r[0] not in opptatt][:grense]

    def omsetning(self, symbol: str) -> tuple[float | None, date | None]:
        """Den siste målingen i omsetning (2.13): (median i NOK, dagen den ble
        målt i Oslo), eller (None, None). Gjennomgangen (ECH7): har den siste
        målingen feil, er medianen None, og en eldre måling brukes ikke."""
        rad = self._t.execute(
            "SELECT median_omsetning, maalt FROM omsetning WHERE symbol = ? ORDER BY maalt DESC LIMIT 1",
            (symbol,),
        ).fetchone()
        if rad is None:
            return None, None
        maalt = datetime.fromisoformat(rad[1]).astimezone(OSLO).date()
        return (float(rad[0]) if rad[0] is not None else None), maalt

    # --- Skriving (bare oenske) ----------------------------------------

    @contextmanager
    def _laas(self):
        """Gjennomgangen (BH2): sjekken av taket og skrivingen i én
        transaksjon med skrivelås, så to forespørsler samtidig ikke begge
        kommer under taket."""
        if self._t.in_transaction:
            self._t.commit()
        self._t.execute("BEGIN IMMEDIATE")
        try:
            yield
        except BaseException:
            self._t.rollback()
            raise
        self._t.commit()

    def folg(self, kode: str, sektor: str, bytt_ut: str | None = None) -> None:
        """Ønsket om å følge kode, med bransjen brukeren valgte. Med bytt_ut
        er det et bytte: de to ønskene lages i samme transaksjon og peker på
        hverandre (par), så de angres sammen (gjennomgangen, BH3, ECH2)."""
        aksje = self.boersaksje(kode)
        if aksje is None:
            raise UgyldigValg("koden står ikke i lista over Oslo Børs")
        if sektor not in BRANSJENE:
            raise UgyldigValg("bransjen er ikke en av de 13")
        laget = self._klokke().isoformat()
        with self._laas():
            if kode in {a.symbol for a in self.i_lista()} or any(
                o.symbol == kode and o.handling == FOLG for o in self.ventende()
            ):
                raise UgyldigValg("aksjen følges alt")
            if bytt_ut is not None:
                self._kan_fjernes(bytt_ut)
            elif self.antall() >= TAK:
                raise ListaErFull(FULL)
            folg_id = self._t.execute(
                "INSERT INTO oenske (handling, symbol, navn, sektor, laget) VALUES ('folg', ?, ?, ?, ?)",
                (kode, aksje.navn, sektor, laget),
            ).lastrowid
            # Story 8.26 (gruppens svar 11.11 kl. 17:47, tillegg 3): aksjen får
            # stjerne og står i Min liste med en gang, i samme transaksjon som
            # ønsket. Triggeren i 0013 godtar et symbol som venter.
            self._t.execute("INSERT INTO min_liste (symbol) VALUES (?) ON CONFLICT (symbol) DO NOTHING", (kode,))
            self._rydd_stjernene()
            if bytt_ut is not None:
                fjern_id = self._t.execute(
                    "INSERT INTO oenske (handling, symbol, laget, par) VALUES ('fjern', ?, ?, ?)",
                    (bytt_ut, laget, folg_id),
                ).lastrowid
                self._t.execute("UPDATE oenske SET par = ? WHERE id = ?", (fjern_id, folg_id))

    def bruk_liste(self, aksjer: list[tuple[str, str]]) -> None:
        """Story 8.11: en ferdig liste, [(kode, bransje)], blir lista ved
        neste henting. Ønskene som venter, slettes (de er ikke tatt i bruk),
        hver aksje i lista som ikke er i den ferdige, får et ønske om å
        fjernes, og hver i den ferdige som ikke er i lista, et ønske om å
        følges. Alt i én transaksjon med skrivelås, så lista aldri får mer
        enn TAK (spørsmål 2 i spec-8-11-ferdige-lister.md)."""
        if len(aksjer) > TAK or len({k for k, _ in aksjer}) != len(aksjer):
            raise ListaErFull("En ferdig liste har opptil 18 aksjer.")
        laget = self._klokke().isoformat()
        with self._laas():
            self._t.execute("DELETE FROM oenske WHERE tatt_i_bruk IS NULL AND avvist IS NULL")
            # Før de nye ønskene, så en gammel stjerne ikke følger med en aksje
            # fra den ferdige lista (gjennomgangen, BH2, ECH5).
            self._rydd_stjernene()
            lista = [a.symbol for a in self.i_lista()]
            maal = {k for k, _ in aksjer}
            for symbol in lista:
                if symbol not in maal:
                    self._t.execute(
                        "INSERT INTO oenske (handling, symbol, laget) VALUES ('fjern', ?, ?)", (symbol, laget)
                    )
            for kode, sektor in aksjer:
                if kode in lista:
                    continue
                aksje = self.boersaksje(kode)
                if aksje is None or sektor not in BRANSJENE:
                    raise UgyldigValg("en aksje i lista står ikke i lista over Oslo Børs")
                self._t.execute(
                    "INSERT INTO oenske (handling, symbol, navn, sektor, laget) VALUES ('folg', ?, ?, ?, ?)",
                    (kode, aksje.navn, sektor, laget),
                )

    def _rydd_stjernene(self) -> None:
        """Gjennomgangen av 8.26 (BH2, ECH5): en stjerne fra «Følg» på en aksje
        som verken står i aksje eller venter (ønsket ble slettet eller avvist),
        tas bort, så den ikke dukker opp hvis aksjen kommer inn senere.
        Triggeren fra 0013 lar ingen andre stjerner stå uten aksjen."""
        self._t.execute(
            "DELETE FROM min_liste WHERE symbol NOT IN (SELECT symbol FROM aksje) AND symbol NOT IN "
            "(SELECT symbol FROM oenske WHERE handling = 'folg' AND tatt_i_bruk IS NULL AND avvist IS NULL)"
        )

    def _kan_fjernes(self, symbol: str) -> None:
        if symbol not in {a.symbol for a in self.i_lista()}:
            raise UgyldigValg("aksjen er ikke i lista")
        if any(o.symbol == symbol and o.handling == FJERN for o in self.ventende()):
            raise UgyldigValg("aksjen fjernes alt ved neste henting")

    def fjern(self, symbol: str) -> None:
        with self._laas():
            self._kan_fjernes(symbol)
            self._t.execute(
                "INSERT INTO oenske (handling, symbol, laget) VALUES ('fjern', ?, ?)",
                (symbol, self._klokke().isoformat()),
            )

    def angre(self, oenske_id: int) -> None:
        """Sletter et ønske som ikke er tatt i bruk, og den andre halvdelen av
        et bytte. Et ønske som er tatt i bruk eller avvist, står (det er
        historikken for lista). Gjennomgangen (BH1, ECH1, VG1): å angre et
        ønske om å fjerne avvises når lista da ville fått mer enn TAK."""
        with self._laas():
            rad = self._t.execute(
                "SELECT handling, par FROM oenske WHERE id = ? AND tatt_i_bruk IS NULL AND avvist IS NULL",
                (oenske_id,),
            ).fetchone()
            if rad is None:
                raise UgyldigValg("ønsket finnes ikke, eller er alt tatt i bruk")
            handling, par = rad
            if handling == FJERN and par is None and self.antall() + 1 > TAK:
                raise ListaErFull(FULL_ANGRE)
            # Story 8.26 (tillegg 3, forslaget i spørsmål 7): «Angre» tar også
            # bort stjernen som «Følg» satte, så Min liste ikke har en aksje
            # appen ikke følger.
            self._t.execute(
                "DELETE FROM min_liste WHERE symbol IN (SELECT symbol FROM oenske WHERE id IN (?, ?) "
                "AND handling = 'folg' AND tatt_i_bruk IS NULL AND avvist IS NULL)",
                (oenske_id, par if par is not None else oenske_id),
            )
            self._t.execute(
                "DELETE FROM oenske WHERE id IN (?, ?) AND tatt_i_bruk IS NULL AND avvist IS NULL",
                (oenske_id, par if par is not None else oenske_id),
            )
            self._rydd_stjernene()


def egne_i_lista(tilkobling: sqlite3.Connection) -> frozenset[str]:
    """Aksjene i lista (ut er ikke satt) med et ønske om å følge som er tatt i
    bruk. En aksje som er tatt ut, har ut satt, så den er ikke med."""
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
    """Ønskene som venter, for børsdagen dato: først ønskene om å fjerne, så
    ønskene om å følge, i den rekkefølgen de ble laget.

    Å fjerne setter ut = dato, så kveldens henting ikke henter aksjen. Har
    aksjen alt kurs eller vurdering for dato, eller kom den inn samme dag,
    blir ut dagen etter, så det som er lagret for dato, står i lista den
    dagen. Ingen rad i aksje slettes (gjennomgangen, BH4, ECH4, AD-7).

    Å følge legger aksjen inn med inn = dato, eller tar den inn igjen (ut blir
    NULL). Gjennomgangen (BH1, VG1): har lista alt TAK aksjer, avvises ønsket
    med grunnen. Gir linjene til utskriften.

    Story 8.22 (spørsmål 3): bransjen er den faste i ferdige_lister.BRANSJE
    når aksjen står der, ikke den i ønsket, og en egen aksje i lista med en
    annen bransje i aksje får den faste. De 15 og aksjer som er tatt ut,
    røres ikke. Et ønske om å følge MULTI eller SCOIN avvises (gjennomgangen, ECH4)."""
    # Inne i funksjonen, fordi ferdige_lister importerer valg.
    from ferdige_lister import UTE, fast_bransje

    linjer: list[str] = []
    dag = dato.isoformat()
    neste = (dato + timedelta(days=1)).isoformat()
    with tilkobling:
        ventende = tilkobling.execute(
            "SELECT id, handling, symbol, navn, sektor FROM oenske "
            "WHERE tatt_i_bruk IS NULL AND avvist IS NULL ORDER BY handling = 'folg', id"
        ).fetchall()
        for id_, handling, symbol, navn, sektor in ventende:
            sektor = fast_bransje(symbol) or sektor
            rad = tilkobling.execute("SELECT inn, ut FROM aksje WHERE symbol = ?", (symbol,)).fetchone()
            if handling == FJERN:
                if rad is None or rad[1] is not None:
                    tilkobling.execute("UPDATE oenske SET avvist = ? WHERE id = ?", (f"{dag}: ikke i lista", id_))
                    continue
                har_dagen = tilkobling.execute(
                    "SELECT EXISTS(SELECT 1 FROM kurs WHERE symbol = ? AND dato = ?) "
                    "OR EXISTS(SELECT 1 FROM vurdering WHERE symbol = ? AND dato = ?)",
                    (symbol, dag, symbol, dag),
                ).fetchone()[0]
                ut = neste if har_dagen or (rad[0] is not None and rad[0] >= dag) else dag
                tilkobling.execute("UPDATE aksje SET ut = ? WHERE symbol = ?", (ut, symbol))
                linjer.append(f"{symbol} er tatt ut av lista fra {ut}. Det som er lagret, står.")
            else:
                # Gjennomgangen av 8.22 (ECH4): et ønske fra før 8.22 om å
                # følge en aksje gruppen har tatt ut, avvises med grunnen.
                if symbol in UTE:
                    tilkobling.execute(
                        "UPDATE oenske SET avvist = ? WHERE id = ?", (f"{dag}: kan ikke følges (story 8.22)", id_)
                    )
                    linjer.append(f"{symbol} er ikke tatt inn: aksjen kan ikke følges.")
                    continue
                i_lista = tilkobling.execute("SELECT count(*) FROM aksje WHERE ut IS NULL").fetchone()[0]
                if i_lista >= TAK:
                    tilkobling.execute(
                        "UPDATE oenske SET avvist = ? WHERE id = ?", (f"{dag}: lista har {TAK} aksjer", id_)
                    )
                    linjer.append(f"{symbol} er ikke tatt inn: lista har alt {TAK} aksjer.")
                    continue
                if rad is None:
                    tilkobling.execute(
                        "INSERT INTO aksje (symbol, ticker, navn, sektor, inn) VALUES (?, ?, ?, ?, ?)",
                        (symbol, f"{symbol}.OL", navn, sektor, dag),
                    )
                elif rad[1] is not None:
                    tilkobling.execute("UPDATE aksje SET ut = NULL, sektor = ? WHERE symbol = ?", (sektor, symbol))
                linjer.append(f"{symbol} er tatt inn i lista fra {dag}.")
            tilkobling.execute("UPDATE oenske SET tatt_i_bruk = ? WHERE id = ?", (dag, id_))
        for symbol in sorted(egne_i_lista(tilkobling)):
            fast = fast_bransje(symbol)
            gammel = tilkobling.execute("SELECT sektor FROM aksje WHERE symbol = ?", (symbol,)).fetchone()[0]
            if fast is not None and fast != gammel:
                tilkobling.execute("UPDATE aksje SET sektor = ? WHERE symbol = ?", (fast, symbol))
                linjer.append(f"{symbol} har fått bransjen {fast} fra kontrollsjekken (var {gammel}).")
    return linjer


def uten_rader(tilkobling: sqlite3.Connection, dato: date) -> list[str]:
    """Spørsmål 6: en egen aksje som kom inn før dato, ble forsøkt hentet (den
    har en rad i vurdering, med grunn) og ikke har fått en eneste kurs, tas
    ut fra dato, og det siste ønsket om å følge den merkes avvist. Det sjekkes
    kvelden etter, så et nytt forsøk samme kveld fortsatt kan hente den.
    Gjennomgangen (BH5): en aksje som aldri ble forsøkt, tas ikke ut. Radene i
    vurdering står (AD-7). Gir linjene til utskriften."""
    dag = dato.isoformat()
    linjer = []
    with tilkobling:
        for (symbol,) in tilkobling.execute(
            "SELECT symbol FROM aksje WHERE inn IS NOT NULL AND inn < ? AND ut IS NULL "
            "AND NOT EXISTS (SELECT 1 FROM kurs WHERE kurs.symbol = aksje.symbol) "
            "AND EXISTS (SELECT 1 FROM vurdering v WHERE v.symbol = aksje.symbol AND v.dato >= aksje.inn)",
            (dag,),
        ).fetchall():
            if symbol not in egne_i_lista(tilkobling):
                continue
            tilkobling.execute("UPDATE aksje SET ut = ? WHERE symbol = ?", (dag, symbol))
            tilkobling.execute(
                "UPDATE oenske SET avvist = ? WHERE id = (SELECT max(id) FROM oenske WHERE symbol = ? "
                "AND handling = 'folg' AND tatt_i_bruk IS NOT NULL)",
                (f"{dag}: ga ingen kurser", symbol),
            )
            linjer.append(f"{symbol} ga ingen kurser etter at den ble valgt, og er tatt ut av lista igjen.")
    return linjer
