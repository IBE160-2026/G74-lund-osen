"""Maalingen av omsetning - story 2.13, FR-413, NFR-01, AD-6, AD-16.

Et eget valg i hentekommandoen: fetch_prices.py --maal-omsetning. Jobben fra
2.3d kjoerer det etter hentingen hver kveld (avgjoerelsen 28.10 kl. 22:17).
Det maaler median omsetning for de neste aksjene i lista over Oslo Boers
(malinger.md §40) med alle kallene som er igjen av dagens i GMT, og bruker
aldri bonuskvoten (NFR-01, beslutningen 08.10 kl. 08:06).

Utvalget og rekkefoelgen er de fra §50-§52: «Common Stock» i lista, i
rekkefoelgen i fila, som ikke er maalt, og uten aksjene i appens liste. Naar
alle er maalt, kommer den eldste maalingen foerst (avgjoerelsen kl. 22:17, c).
Maalt er en aksje med en rad i tabellen omsetning, eller en av de 214 som
er rangert i malinger.md (MAALT_I_MALINGER).

Hentingen og nye forsoek faar kallene foerst (b): mangler en aksje i lista
kursen for boersdagen, stopper valget med 0 kall, saa kallene staar til et
nytt forsoek. Paa en boersdag foer hentingen er det dagens kurs som mangler.

Kvoten leses med /api/user (gratis) foer og etter hvert kall, som i §51.
Valget stopper hvis extraLimit endrer seg, hvis apiRequestsDate ikke er
dagens dato i GMT etter et kall, eller hvis datoen i GMT skifter underveis.
Foer foerste kall er en tidligere dato 0 brukt i dag (regel 15), saa valget
ogsaa gaar paa dager uten henting.

Denne modulen gjoer ingen nettkall selv. hent og les_kvote gis inn av main i
fetch_prices.py, som har de to nettfunksjonene (AD-2), og testene gir falske
(AD-8). Raadataene skrives til data/raa/ foer radene i basen (AD-6), og
utskriften har verken kurser, volumer eller medianene.
"""

import calendar
import json
import math
import statistics
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable

import lagring_sqlite
from boersdag import UtenforKalenderen, innevaerende_boersdag, norsk_dato
from fetch_prices import BASEFEIL, UlesbarKvote, _uten_noekkel, les_kvotetall, manglende_i_basen, nekt_demobase
from kursdata import AKSJEUNIVERS, Aksje
from lagring_fil import PROSJEKTROT

# Lista over aksjene paa Oslo Boers fra §40, lest lokalt uten kall. Fila er
# raadata og spores ikke (regel 10).
LISTEFIL = PROSJEKTROT / "data" / "proever" / "symbolliste-OL-2026-10-22.json"
AKSJETYPE = "Common Stock"

PREFIKS = "omsetning"
MAANEDER = 3

# De 214 som er rangert i malinger.md: paragrafen, datoen i overskriften til
# paragrafen og symbolene som ble maalt der («Maalt i» i «Alle 206, rangert»
# i §50, og tabellene i §51 og §52). tests/test_omsetning.py holder dem like.
MAALT_I_MALINGER: dict[int, tuple[date, tuple[str, ...]]] = {
    15: (
        date(2026, 10, 2),
        (
            "AKER",
            "BWLPG",
            "KMAR",
            "STB",
            "SUBC",
        ),
    ),
    16: (
        date(2026, 10, 3),
        (
            "AUTO",
            "BNOR",
            "CMBTO",
            "DOFG",
            "HAFNI",
            "HAUTO",
            "MING",
            "NAS",
            "NOD",
            "OET",
            "PROT",
            "SB1NO",
            "SBNOR",
            "SPOL",
            "TGS",
            "TOM",
            "VEI",
            "VEND",
            "WAWI",
            "WWI",
        ),
    ),
    17: (
        date(2026, 10, 3),
        (
            "AKRBP",
            "DNB",
            "DNO",
            "EQNR",
            "FRO",
            "GJF",
            "KOG",
            "MOWI",
            "MPCC",
            "NHY",
            "ORK",
            "SALM",
            "TEL",
            "VAR",
            "YAR",
        ),
    ),
    18: (
        date(2026, 10, 4),
        (
            "AFG",
            "AKSO",
            "ATEA",
            "BORR",
            "BRG",
            "BWE",
            "CADLR",
            "CAPT",
            "COSH",
            "ELK",
            "ENTRA",
            "EPR",
            "KIT",
            "NONG",
            "NORCO",
            "ODL",
            "SCATC",
            "SNI",
            "SOMA",
            "SWON",
        ),
    ),
    20: (
        date(2026, 10, 5),
        (
            "AUSS",
            "BAKKA",
            "GSF",
            "LSG",
            "SALME",
        ),
    ),
    21: (
        date(2026, 10, 6),
        (
            "AFK",
            "AKBM",
            "BONHR",
            "NORBT",
            "ODF",
        ),
    ),
    23: (
        date(2026, 10, 7),
        (
            "B2I",
            "ELO",
            "HSHP",
            "SATS",
            "SNTIA",
        ),
    ),
    24: (
        date(2026, 10, 8),
        (
            "BWO",
            "LINK",
            "PEXIP",
            "PLSV",
            "RING",
        ),
    ),
    26: (
        date(2026, 10, 9),
        (
            "ENH",
            "KCC",
            "MORG",
            "SOAG",
            "SOFF",
        ),
    ),
    27: (
        date(2026, 10, 10),
        (
            "AKVA",
            "BEWI",
            "BOUV",
            "ELMRA",
            "ENDUR",
            "GKP",
            "HELG",
            "HEX",
            "KID",
            "MAS",
            "MEDI",
            "MORLD",
            "NAPA",
            "NSKOG",
            "PARB",
            "PEN",
            "SEA1",
            "SMOP",
            "ZAP",
        ),
    ),
    28: (
        date(2026, 10, 12),
        (
            "CLOUD",
            "MULTI",
            "NEL",
            "OKEA",
            "SNM",
        ),
    ),
    29: (
        date(2026, 10, 14),
        (
            "ABG",
            "ACR",
            "BOHUS",
            "CAMBI",
            "VTURA",
        ),
    ),
    30: (
        date(2026, 10, 15),
        (
            "AKAST",
            "ANDF",
            "CRNA",
            "GENO",
            "ROGS",
        ),
    ),
    33: (
        date(2026, 10, 16),
        (
            "BRUT",
            "POL",
            "SBO",
        ),
    ),
    35: (
        date(2026, 10, 17),
        (
            "AGLX",
            "ARCH",
            "BINT",
            "DVD",
            "ENVIP",
            "HUNT",
            "INSTA",
            "IWS",
            "KOA",
            "NOL",
            "NORAM",
            "NORDH",
            "NRC",
            "OMC",
            "OTL",
            "PLT",
            "REACH",
            "SKUE",
            "TRMED",
            "ZAL",
        ),
    ),
    36: (
        date(2026, 10, 18),
        (
            "APR",
            "BMA",
            "DFENS",
            "ISLAX",
            "JACK",
            "JAREN",
            "MDATA",
            "MGN",
            "NKR",
            "NOAP",
            "NOHAL",
            "NTI",
            "OTEC",
            "PHO",
            "PNOR",
            "PRS",
            "PYRUM",
            "SNOR",
            "SPOG",
            "TEKNA",
        ),
    ),
    41: (
        date(2026, 10, 23),
        (
            "2020",
            "5PG",
            "AASB",
            "ABS",
        ),
    ),
    42: (
        date(2026, 10, 24),
        (
            "ABTEC",
            "ACED",
            "ADS",
            "AFISH",
            "AIX",
            "AKOBO",
            "ALNG",
            "AQUA",
            "ARR",
            "ASA",
            "AURG",
            "AZT",
            "BALT",
            "BARRA",
            "BCS",
            "BIEN",
            "BOR",
            "BSP",
            "CAPSL",
            "CAVEN",
        ),
    ),
    50: (
        date(2026, 10, 25),
        (
            "CODE",
            "CONTX",
            "CYVIZ",
            "DDRIL",
            "DELIA",
            "DSRT",
            "EAM",
            "EIOF",
            "ELABS",
            "ELOO",
            "ENERG",
            "ENSU",
            "EQVA",
            "EXTX",
            "FFSB",
            "GEM",
            "GENT",
            "GEOS",
            "GIGA",
            "GOD",
        ),
    ),
    51: (
        date(2026, 10, 26),
        (
            "GOLDR",
            "GRONG",
            "GYL",
            "HAV",
        ),
    ),
    52: (
        date(2026, 10, 28),
        (
            "HAVI",
            "HBC",
            "HDLY",
            "HERMA",
        ),
    ),
}


def maalt_i_malingene() -> dict[str, date]:
    """Datoen hver av de 214 ble maalt i malinger.md."""
    return {symbol: dato for dato, symboler in MAALT_I_MALINGER.values() for symbol in symboler}


@dataclass(frozen=True)
class Maaling:
    """En rad i omsetning. median er NOK, uavrundet (regel 21), eller None med
    feil."""

    symbol: str
    handelsdager: int
    dager_uten_volum: int
    rader_uten_tall: int
    median: float | None
    feil: str | None


def vindu(boersdag: date) -> tuple[date, date]:
    """Tre maaneder til og med boersdagen, som i §40 (2026-07-22-2026-10-22).

    Finnes ikke dagen tre maaneder foer, er det siste dag i den maaneden.
    """
    aar, maaned = divmod(boersdag.year * 12 + boersdag.month - 1 - MAANEDER, 12)
    dager = calendar.monthrange(aar, maaned + 1)[1]
    return date(aar, maaned + 1, min(boersdag.day, dager)), boersdag


def _tall(verdi: object) -> bool:
    return isinstance(verdi, (int, float)) and not isinstance(verdi, bool) and math.isfinite(verdi) and verdi >= 0


def regn_ut(symbol: str, rader: object, fra: date, til: date) -> Maaling:
    """Median av volume x close per rad i vinduet, som i §3 og §42.

    En rad med volum 0 er med, med omsetning 0. En rad uten tall for close
    eller volume er ikke med, men telles.
    """
    if not isinstance(rader, list):
        return Maaling(symbol, 0, 0, 0, None, "svaret er ikke en liste med rader")
    omsetning, uten_tall = [], 0
    for rad in rader:
        try:
            dag = date.fromisoformat(rad["date"])
        except (TypeError, KeyError, ValueError):
            uten_tall += 1
            continue
        if not fra <= dag <= til:
            continue
        if not (_tall(rad.get("close")) and _tall(rad.get("volume"))):
            uten_tall += 1
            continue
        omsetning.append(rad["volume"] * rad["close"])
    if not omsetning:
        return Maaling(symbol, 0, 0, uten_tall, None, "ingen rader med tall i vinduet")
    uten_volum = sum(1 for verdi in omsetning if verdi == 0)
    return Maaling(symbol, len(omsetning), uten_volum, uten_tall, float(statistics.median(omsetning)), None)


def les_lista(sti: Path) -> list[str]:
    """Kodene med typen «Common Stock», i rekkefoelgen i fila, uten doble."""
    rader = json.loads(Path(sti).read_text(encoding="utf-8"))
    if not isinstance(rader, list):
        raise ValueError("lista er ikke en liste")
    koder = []
    for rad in rader:
        if isinstance(rad, dict) and rad.get("Type") == AKSJETYPE and isinstance(rad.get("Code"), str):
            if rad["Code"] and rad["Code"] not in koder:
                koder.append(rad["Code"])
    return koder


def sist_maalt_i_basen(base_sti: Path) -> dict[str, datetime]:
    """Siste maaling per symbol i omsetning. Basen migreres (AD-16)."""
    tilkobling = lagring_sqlite.aapne_base(base_sti)
    try:
        return {
            symbol: datetime.fromisoformat(maalt)
            for symbol, maalt in tilkobling.execute("SELECT symbol, MAX(maalt) FROM omsetning GROUP BY symbol")
        }
    finally:
        tilkobling.close()


def rekkefoelge(
    lista_over_boersen: list[str],
    i_basen: dict[str, datetime],
    lista: tuple[Aksje, ...] = AKSJEUNIVERS,
) -> list[str]:
    """Aksjene i den rekkefoelgen de skal maales - avgjoerelsen kl. 22:17.

    Foerst de som aldri er maalt, i rekkefoelgen i lista over Oslo Boers.
    Saa de som er maalt, eldste maaling foerst, og ved lik dato plassen i
    lista. En aksje i appens liste er aldri med.
    """
    i_appen = {aksje.symbol for aksje in lista}
    fra_malingene = maalt_i_malingene()
    kandidater = [kode for kode in lista_over_boersen if kode not in i_appen]
    plass = {kode: i for i, kode in enumerate(kandidater)}

    def sist(kode: str) -> datetime:
        datoer = [i_basen[kode]] if kode in i_basen else []
        if kode in fra_malingene:
            datoer.append(datetime.combine(fra_malingene[kode], datetime.min.time(), timezone.utc))
        return max(datoer)

    aldri = [kode for kode in kandidater if kode not in i_basen and kode not in fra_malingene]
    maalt = sorted((kode for kode in kandidater if kode not in aldri), key=lambda kode: (sist(kode), plass[kode]))
    return aldri + maalt


def raafil(katalog: Path, boersdag: date) -> Path:
    """omsetning<n>-raa-<boersdag>.json med foerste n fra 1 som ikke finnes.

    Datoen er boersdagen, ikke kjoeredagen, saa fila aldri er nyere enn
    kursfila, og ved lik dato vinner kursfila (nyeste_snapshot, AD-6).
    """
    n = 1
    while (katalog / f"{PREFIKS}{n}-raa-{boersdag.isoformat()}.json").exists():
        n += 1
    return katalog / f"{PREFIKS}{n}-raa-{boersdag.isoformat()}.json"


def skriv_radene(base_sti: Path, maalt: str, fra: date, til: date, maalinger: list[Maaling]) -> None:
    """Radene i omsetning, i en transaksjon."""
    tilkobling = lagring_sqlite.aapne_base(base_sti)
    try:
        with tilkobling:
            tilkobling.executemany(
                "INSERT INTO omsetning (symbol, maalt, fra, til, handelsdager, dager_uten_volum, "
                "rader_uten_tall, median_omsetning, feil) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        m.symbol,
                        maalt,
                        fra.isoformat(),
                        til.isoformat(),
                        m.handelsdager,
                        m.dager_uten_volum,
                        m.rader_uten_tall,
                        m.median,
                        m.feil,
                    )
                    for m in maalinger
                ],
            )
    finally:
        tilkobling.close()


class Stopp(Exception):
    """Valget stopper. Teksten er det utskriften sier."""


def _les(les_kvote: Callable[[str], object], nokkel: str) -> tuple[int, int, int, date]:
    """(apiRequests, dailyRateLimit, extraLimit, apiRequestsDate) uten aa
    nullstille, saa datoen kan sjekkes. les_kvotetall kontrollerer feltene.
    Reiser Stopp."""
    try:
        svar = les_kvote(nokkel)
        brukt, grense, bonus = les_kvotetall(svar, date.min)
        return brukt, grense, bonus, date.fromisoformat(svar["apiRequestsDate"])
    except UlesbarKvote as feil:
        raise Stopp(f"Kvoten kan ikke leses: {feil}.") from None
    except Exception as feil:
        raise Stopp(f"Kvoten kan ikke leses: {_uten_noekkel(str(feil), nokkel)}") from None


def maal_omsetning(
    data_katalog: Path,
    base_sti: Path,
    listefil: Path,
    api_nokkel: Callable[[], str],
    *,
    hent: Callable[[str, str, str, str], object],
    les_kvote: Callable[[str], object],
    klokke: Callable[[], datetime],
    skriv: Callable[[str], None] = print,
    lista: tuple[Aksje, ...] = AKSJEUNIVERS,
) -> int:
    """Maalingen. Gir 0 naar den er ferdig eller ingen kall er igjen, og 1
    naar den stoppet. Stopper den etter et kall, lagres det som er maalt.

    hent, les_kvote og klokke har ingen standardverdi, saa en test som
    glemmer dem, feiler i stedet for aa gaa mot nettet (AD-8). Klokka leses
    foer og etter hvert kall.
    """
    nekt_demobase(base_sti, skriv)
    start = klokke().astimezone(timezone.utc)
    i_dag_gmt = start.date()
    try:
        boersdag = innevaerende_boersdag(norsk_dato(start))
    except UtenforKalenderen as feil:
        skriv(f"{feil}. Målingen gjetter ikke på børsdagen (NFR-08). 0 kall brukt.")
        return 1
    try:
        mangler = manglende_i_basen(base_sti, boersdag, lista)
    except BASEFEIL as feil:
        skriv(f"Basen kan ikke leses ({type(feil).__name__}). Målingen venter. 0 kall brukt.")
        return 1
    if mangler:
        skriv(
            f"{', '.join(mangler)} mangler kursen for {boersdag.isoformat()}. Hentingen og nye forsøk får "
            "kallene først, så målingen venter. 0 kall brukt."
        )
        return 1
    try:
        lista_over_boersen = les_lista(listefil)
    except (OSError, ValueError) as feil:
        skriv(
            f"Lista over aksjene på Oslo Børs, {Path(listefil).name}, kan ikke leses ({type(feil).__name__}). 0 kall brukt."
        )
        return 1
    try:
        plan = rekkefoelge(lista_over_boersen, sist_maalt_i_basen(base_sti), lista)
    except BASEFEIL as feil:
        skriv(f"Basen kan ikke leses ({type(feil).__name__}). 0 kall brukt.")
        return 1

    nokkel = api_nokkel()
    try:
        brukt, grense, bonus, dato = _les(les_kvote, nokkel)
    except Stopp as stopp:
        skriv(f"{stopp} 0 kall brukt.")
        return 1
    if dato > i_dag_gmt:
        skriv(f"Kvoten står på {dato.isoformat()}, etter dagens dato i GMT, {i_dag_gmt.isoformat()}. 0 kall brukt.")
        return 1
    if dato < i_dag_gmt:
        brukt = 0
    igjen = max(grense - brukt, 0)
    plan = plan[:igjen]
    if not plan:
        skriv(f"Ingen kall igjen av dagens {grense} i GMT, eller ingen aksje å måle. 0 kall brukt.")
        return 0

    fra, til = vindu(boersdag)
    skriv(
        f"Måler omsetningen for {len(plan)} aksjer med {len(plan)} av de {igjen} kallene som er igjen av dagens, "
        f"fra {fra.isoformat()} til {til.isoformat()}. Bonuskvoten brukes aldri, og ingen kall blir igjen i dag."
    )

    serier: dict[str, object] = {}
    feil_ved: dict[str, str] = {}
    maalinger: list[Maaling] = []
    kall = 0
    kode = 0
    try:
        for symbol in plan:
            if klokke().astimezone(timezone.utc).date() != i_dag_gmt:
                raise Stopp(f"Datoen i GMT er ikke lenger {i_dag_gmt.isoformat()}.")
            brukt, _, bonus_naa, dato = _les(les_kvote, nokkel)
            if bonus_naa != bonus:
                raise Stopp(f"extraLimit er endret fra {bonus} til {bonus_naa}, så bonuskvoten kan være brukt.")
            if dato > i_dag_gmt or (kall and dato != i_dag_gmt):
                raise Stopp(f"Kvoten står på {dato.isoformat()}, ikke {i_dag_gmt.isoformat()} i GMT.")
            if dato == i_dag_gmt and brukt >= grense:
                raise Stopp(f"Alle de {grense} kallene i dag er brukt. Kall nummer {grense + 1} går fra bonuskvoten.")
            try:
                svar = hent(f"{symbol}.OL", nokkel, fra.isoformat(), til.isoformat())
            except Exception as feil:
                svar = None
                feil_ved[symbol] = _uten_noekkel(str(feil) or type(feil).__name__, nokkel)
            kall += 1
            if symbol in feil_ved:
                maaling = Maaling(symbol, 0, 0, 0, None, feil_ved[symbol])
            else:
                serier[symbol] = svar
                maaling = regn_ut(symbol, svar, fra, til)
            maalinger.append(maaling)
            if maaling.feil:
                skriv(f"{symbol}: ingen måling ({maaling.feil}).")
            else:
                skriv(f"{symbol}: {maaling.handelsdager} handelsdager, {maaling.dager_uten_volum} uten volum.")
            brukt, _, bonus_naa, dato = _les(les_kvote, nokkel)
            if dato != i_dag_gmt:
                raise Stopp(f"Kvoten står på {dato.isoformat()} etter kallet, ikke {i_dag_gmt.isoformat()} i GMT.")
            if bonus_naa != bonus:
                raise Stopp(f"extraLimit er endret fra {bonus} til {bonus_naa}, så bonuskvoten kan være brukt.")
            if brukt > grense:
                raise Stopp(f"apiRequests er {brukt}, over dagens {grense}.")
    except Stopp as stopp:
        skriv(f"STOPP: {stopp}")
        kode = 1

    if maalinger:
        fil = raafil(data_katalog, boersdag)
        bilde = {
            "hentet": start.isoformat(),
            "boersdag": boersdag.isoformat(),
            "fra": fra.isoformat(),
            "til": til.isoformat(),
            "serier": serier,
            "feil": feil_ved,
        }
        try:
            fil.parent.mkdir(parents=True, exist_ok=True)
            with fil.open("x", encoding="utf-8") as ut:
                json.dump(bilde, ut, ensure_ascii=False)
        except OSError as feil:
            skriv(f"Rådataene kunne ikke skrives ({type(feil).__name__}). Ingen rader i basen.")
            return 1
        try:
            skriv_radene(base_sti, start.isoformat(), fra, til, maalinger)
        except BASEFEIL as feil:
            skriv(f"Basen feilet ({type(feil).__name__}). Rådataene står i {fil.name}.")
            return 1
        skriv(f"Rådataene står i {fil.name}, og {len(maalinger)} rader er lagt til i omsetning.")
    skriv(f"API-kall brukt: {kall}.")
    return kode
