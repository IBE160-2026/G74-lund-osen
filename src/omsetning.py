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
Fra kl. 23:45 i Oslo, jobbens siste kjoering, gaar maalingen likevel med
kallene som er igjen etter de nye forsoekene (avgjoerelsen kl. 23:19, d).

Kvoten leses med /api/user (gratis) foer og etter hvert kall, som i §51.
Valget stopper hvis extraLimit endrer seg, hvis apiRequestsDate ikke er
dagens dato i GMT etter et kall, eller hvis datoen i GMT skifter underveis.
Foer foerste kall er en tidligere dato 0 brukt i dag (regel 15), saa valget
ogsaa gaar paa dager uten henting.

Denne modulen gjoer ingen nettkall selv. hent og les_kvote gis inn av main i
fetch_prices.py, som har de to nettfunksjonene (AD-2), og testene gir falske
(AD-8). Raadataene skrives til data/raa/ foer radene i basen (AD-6), og
utskriften har verken kurser, volumer eller medianene.

Story 2.13b (gruppens svar 10.11 kl. 13:48 og 16:31): med med_bonus maales
bare aksjene uten en rad i tabellen omsetning, i samme rekkefoelge, med
kallene som er igjen av dagens og saa bonuskvoten, og valget stopper foer
extraLimit blir under BONUSGULV. De 214 i malinger.md har ingen tall i basen
og regnes da ikke som maalt. Uten med_bonus er alt som foer, og bonuskvoten
brukes aldri.
"""

import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Callable

import lagring_sqlite
from boersdag import OSLO, UtenforKalenderen, innevaerende_boersdag, norsk_dato
from fetch_prices import (
    BASEFEIL,
    UlesbarKvote,
    _uten_noekkel,
    les_kvotetall,
    lista_fra_basen,
    manglende_i_basen,
    nekt_demobase,
)
from kursdata import AKSJEUNIVERS, Aksje
from lagring_fil import PROSJEKTROT

# Story 8.11b: utregningen staar i omsetningsregning.py, saa webserveren kan
# bruke den uten aa importere fetch_prices (AD-10). Navnene importeres her
# som foer.
from omsetningsregning import MAANEDER, Maaling, _tall, regn_ut, vindu  # noqa: F401

# Lista over aksjene paa Oslo Boers fra §40, lest lokalt uten kall. Fila er
# raadata og spores ikke (regel 10).
LISTEFIL = PROSJEKTROT / "data" / "proever" / "symbolliste-OL-2026-10-22.json"
AKSJETYPE = "Common Stock"

PREFIKS = "omsetning"

# Jobbens siste kjoering. Fra da stopper ikke en manglende kurs maalingen
# (avgjoerelsen 28.10 kl. 23:19, d).
KL_23_45 = time(23, 45)

# Story 2.13b: saa mange kall staar alltid igjen i bonuskvoten med med_bonus.
BONUSGULV = 200
# Story 2.13b (gjennomgangen, ECH1): startes valget foer kl. 06:00 i Oslo,
# gjelder boersdagen foer, saa kjoeringen etter midnatt maaler til kvelden foer.
KL_06 = time(6, 0)
# Story 2.13b (gjennomgangen, ECH2): saa mange feil paa rad som ikke er 404,
# stopper valget, saa bonuskvoten ikke brukes paa kall som feiler.
FEIL_PAA_RAD = 3

# De 214 som er rangert i malinger.md: paragrafen, datoen i overskriften til
# paragrafen og symbolene som ble maalt der («Maalt i» i «Alle 206, rangert»
# i §50, og tabellene i §51 og §52). tests/test_omsetning.py holder dem like.
MAALT_I_MALINGER: dict[int, tuple[date, tuple[str, ...]]] = {
    15: (date(2026, 10, 2), ("AKER", "BWLPG", "KMAR", "STB", "SUBC")),
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
        ("AKRBP", "DNB", "DNO", "EQNR", "FRO", "GJF", "KOG", "MOWI", "MPCC", "NHY", "ORK", "SALM", "TEL", "VAR", "YAR"),
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
    20: (date(2026, 10, 5), ("AUSS", "BAKKA", "GSF", "LSG", "SALME")),
    21: (date(2026, 10, 6), ("AFK", "AKBM", "BONHR", "NORBT", "ODF")),
    23: (date(2026, 10, 7), ("B2I", "ELO", "HSHP", "SATS", "SNTIA")),
    24: (date(2026, 10, 8), ("BWO", "LINK", "PEXIP", "PLSV", "RING")),
    26: (date(2026, 10, 9), ("ENH", "KCC", "MORG", "SOAG", "SOFF")),
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
    28: (date(2026, 10, 12), ("CLOUD", "MULTI", "NEL", "OKEA", "SNM")),
    29: (date(2026, 10, 14), ("ABG", "ACR", "BOHUS", "CAMBI", "VTURA")),
    30: (date(2026, 10, 15), ("AKAST", "ANDF", "CRNA", "GENO", "ROGS")),
    33: (date(2026, 10, 16), ("BRUT", "POL", "SBO")),
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
    41: (date(2026, 10, 23), ("2020", "5PG", "AASB", "ABS")),
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
    51: (date(2026, 10, 26), ("GOLDR", "GRONG", "GYL", "HAV")),
    52: (date(2026, 10, 28), ("HAVI", "HBC", "HDLY", "HERMA")),
}


def maalt_i_malingene() -> dict[str, date]:
    """Datoen hver av de 214 ble maalt i malinger.md."""
    return {symbol: dato for dato, symboler in MAALT_I_MALINGER.values() for symbol in symboler}


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


# Gjennomgangen (BH3, ECH1): bare et svar som sier at tickeren ikke finnes,
# er en varig feil som lagres som maalt. En annen feil (tidsavbrudd, 5xx,
# 429) gir ingen rad, saa aksjen staar foerst ogsaa neste gang.
VARIG_FEIL = "HTTP 404"


def _lagre(
    data_katalog: Path,
    base_sti: Path,
    bilde: dict,
    boersdag: date,
    maalt: str,
    fra: date,
    til: date,
    maalinger: list[Maaling],
    skriv: Callable[[str], None],
) -> int:
    """Raadataene foerst (AD-6), saa radene. 0 naar alt er lagret, ellers 1.

    Gjennomgangen (ECH8): finnes navnet naar fila aapnes, proeves neste n.
    """
    try:
        data_katalog.mkdir(parents=True, exist_ok=True)
        while True:
            fil = raafil(data_katalog, boersdag)
            try:
                with fil.open("x", encoding="utf-8") as ut:
                    json.dump(bilde, ut, ensure_ascii=False)
                break
            except FileExistsError:
                continue
    except OSError as feil:
        skriv(f"Rådataene kunne ikke skrives ({type(feil).__name__}). Ingen rader i basen.")
        return 1
    if maalinger:
        try:
            skriv_radene(base_sti, maalt, fra, til, maalinger)
        except BASEFEIL as feil:
            skriv(f"Basen feilet ({type(feil).__name__}). Rådataene står i {fil.name}.")
            return 1
    skriv(f"Rådataene står i {fil.name}, og {len(maalinger)} rader er lagt til i omsetning.")
    return 0


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
    lista: tuple[Aksje, ...] | None = None,
    med_bonus: bool = False,
) -> int:
    """Maalingen. Gir 0 naar den er ferdig eller ingen kall er igjen, og 1
    naar den stoppet. Stopper den etter et kall, eller avbrytes den, lagres
    det som er maalt (gjennomgangen, ECH3).

    hent, les_kvote og klokke har ingen standardverdi, saa en test som
    glemmer dem, feiler i stedet for aa gaa mot nettet (AD-8). Klokka leses
    rett foer hvert kall (gjennomgangen, ECH6).

    Med med_bonus (story 2.13b) maales bare aksjene uten en rad i omsetning,
    og kallene etter dagens tas fra bonuskvoten til BONUSGULV staar igjen.
    """
    nekt_demobase(base_sti, skriv)
    start = klokke().astimezone(timezone.utc)
    i_dag_gmt = start.date()
    # Story 2.13b (gjennomgangen, ECH1): med valget etter midnatt i Oslo gjelder
    # kvelden foer, som om klokka var 23:45 eller senere.
    natt = med_bonus and start.astimezone(OSLO).time() < KL_06
    try:
        dag = norsk_dato(start)
        boersdag = innevaerende_boersdag(dag - timedelta(days=1) if natt else dag)
    except UtenforKalenderen as feil:
        skriv(f"{feil}. Målingen gjetter ikke på børsdagen (NFR-08). 0 kall brukt.")
        return 1
    # Story 2.11 (gjennomgangen, VG1): lista i basen paa boersdagen, som
    # hentingen bruker.
    if lista is None:
        lista = lista_fra_basen(base_sti, boersdag)
    try:
        mangler = manglende_i_basen(base_sti, boersdag, lista)
    except BASEFEIL as feil:
        skriv(f"Basen kan ikke leses ({type(feil).__name__}). Målingen venter. 0 kall brukt.")
        return 1
    # En base som ikke finnes, er ingen henting, og venter ogsaa etter 23:45
    # (gjennomgangen 29.10, BH4 og ECH6: med egen grunn i utskriften).
    if mangler and not base_sti.exists():
        skriv(
            f"Basen finnes ikke, så ingen henting er gjort for {boersdag.isoformat()}. Målingen venter. 0 kall brukt."
        )
        return 1
    if mangler and not natt and start.astimezone(OSLO).time() < KL_23_45:
        skriv(
            f"{', '.join(mangler)} mangler kursen for {boersdag.isoformat()}. Hentingen og nye forsøk får "
            "kallene først, så målingen venter. 0 kall brukt."
        )
        return 1
    if mangler:
        skriv(
            f"{len(mangler)} av de {len(lista)} i lista mangler kursen for {boersdag.isoformat()} "
            f"({', '.join(mangler)}). Klokka er 23:45 i Oslo eller senere, så målingen går med kallene "
            "som er igjen etter nye forsøk."
        )
    try:
        lista_over_boersen = les_lista(listefil)
    except (OSError, ValueError) as feil:
        skriv(
            f"Lista over aksjene på Oslo Børs, {Path(listefil).name}, kan ikke leses "
            f"({type(feil).__name__}). 0 kall brukt."
        )
        return 1
    try:
        i_basen = sist_maalt_i_basen(base_sti)
        plan = rekkefoelge(lista_over_boersen, i_basen, lista)
    except (*BASEFEIL, ValueError) as feil:
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
    if med_bonus:
        # Story 2.13b: bare aksjene uten en rad i omsetning, i samme rekkefoelge.
        uten_maaling = [kode for kode in plan if kode not in i_basen]
        plan = uten_maaling[: igjen + max(bonus - BONUSGULV, 0)]
        # Gjennomgangen (BH1, ECH7): hver grunn for seg.
        if not uten_maaling:
            skriv("Ingen aksje i lista over Oslo Børs mangler en måling i basen. 0 kall brukt.")
            return 0
        if not plan:
            skriv(
                f"Ingen kall igjen av dagens {grense} i GMT, og bonuskvoten har {bonus}, ikke over "
                f"{BONUSGULV}. {len(uten_maaling)} aksjer uten måling venter. 0 kall brukt."
            )
            return 0
    else:
        plan = plan[:igjen]
        if not plan:
            skriv(f"Ingen kall igjen av dagens {grense} i GMT, eller ingen aksje å måle. 0 kall brukt.")
            return 0

    fra, til = vindu(boersdag)
    if med_bonus:
        av_dagens = min(len(plan), igjen)
        skriv(
            f"Måler omsetningen for {len(plan)} av de {len(uten_maaling)} aksjene uten måling i basen, med "
            f"{av_dagens} av de {igjen} kallene som er igjen av dagens og inntil {len(plan) - av_dagens} fra "
            f"bonuskvoten, som har {bonus}, fra {fra.isoformat()} til {til.isoformat()}. Målingen stopper før "
            f"bonuskvoten er under {BONUSGULV}."
            + (
                ""
                if len(plan) == len(uten_maaling)
                else f" {len(uten_maaling) - len(plan)} aksjer uten måling venter til en senere kjøring."
            )
        )
    else:
        rest = igjen - len(plan)
        skriv(
            f"Måler omsetningen for {len(plan)} aksjer med {len(plan)} av de {igjen} kallene som er igjen av "
            f"dagens, fra {fra.isoformat()} til {til.isoformat()}. Bonuskvoten brukes aldri. "
            + ("Ingen kall blir igjen i dag." if rest == 0 else f"{rest} kall blir igjen i dag.")
        )

    serier: dict[str, object] = {}
    feil_ved: dict[str, str] = {}
    maalinger: list[Maaling] = []
    kall = 0
    fra_bonus = 0
    feil_paa_rad = 0
    kode = 0
    etter: tuple[int, int, int, date] | None = None
    avbrutt: BaseException | None = None
    try:
        for symbol in plan:
            brukt, grense_naa, bonus_naa, dato = _les(les_kvote, nokkel)
            if not med_bonus and bonus_naa != bonus:
                raise Stopp(f"extraLimit er endret fra {bonus} til {bonus_naa}, så bonuskvoten kan være brukt.")
            if dato > i_dag_gmt or (kall and dato != i_dag_gmt):
                raise Stopp(f"Kvoten står på {dato.isoformat()}, ikke {i_dag_gmt.isoformat()} i GMT.")
            # Gjennomgangen (BH10, ECH10): den laveste grensen som er lest.
            grense = min(grense, grense_naa)
            fra_bonusen = dato == i_dag_gmt and brukt >= grense
            if fra_bonusen and not med_bonus:
                raise Stopp(f"Alle de {grense} kallene i dag er brukt. Kall nummer {grense + 1} går fra bonuskvoten.")
            # Story 2.13b: ingen kall fra bonusen naar extraLimit da ville blitt
            # under BONUSGULV. Et kall av dagens trekker ikke fra den.
            if med_bonus and fra_bonusen and bonus_naa - 1 < BONUSGULV:
                raise Stopp(f"extraLimit er {bonus_naa}, og neste kall ville gitt under {BONUSGULV} i bonuskvoten.")
            bonus_foer = bonus_naa
            if klokke().astimezone(timezone.utc).date() != i_dag_gmt:
                raise Stopp(f"Datoen i GMT er ikke lenger {i_dag_gmt.isoformat()}.")
            try:
                svar = hent(f"{symbol}.OL", nokkel, fra.isoformat(), til.isoformat())
            except Exception as feil:
                svar = None
                feil_ved[symbol] = _uten_noekkel(str(feil) or type(feil).__name__, nokkel)
            kall += 1
            if symbol not in feil_ved:
                serier[symbol] = svar
                try:
                    maaling = regn_ut(symbol, svar, fra, til)
                except (ArithmeticError, TypeError, ValueError) as feil:
                    maaling = Maaling(symbol, 0, 0, 0, None, f"radene kunne ikke regnes ut ({type(feil).__name__})")
            elif feil_ved[symbol].startswith(VARIG_FEIL):
                maaling = Maaling(symbol, 0, 0, 0, None, feil_ved[symbol])
            else:
                maaling = None
                skriv(f"{symbol}: kallet feilet ({feil_ved[symbol]}). Ingen rad, så den måles først neste gang.")
            # Gjennomgangen (ECH2): feil paa rad som ikke er 404, telles.
            feil_paa_rad = feil_paa_rad + 1 if maaling is None else 0
            if maaling is not None:
                maalinger.append(maaling)
                if maaling.feil:
                    skriv(f"{symbol}: ingen måling ({maaling.feil}).")
                else:
                    skriv(f"{symbol}: {maaling.handelsdager} handelsdager, {maaling.dager_uten_volum} uten volum.")
            etter = brukt, grense_naa, bonus_naa, dato = _les(les_kvote, nokkel)
            if dato != i_dag_gmt:
                raise Stopp(f"Kvoten står på {dato.isoformat()} etter kallet, ikke {i_dag_gmt.isoformat()} i GMT.")
            if med_bonus:
                # Gjennomgangen (BH3, ECH6): det extraLimit sank under kallet.
                fra_bonus += max(bonus_foer - bonus_naa, 0)
                # Sank extraLimit under BONUSGULV under kallet, har noe annet
                # brukt bonusen, og valget stopper.
                if bonus_naa < min(BONUSGULV, bonus_foer):
                    raise Stopp(f"extraLimit er {bonus_naa} etter kallet, under {BONUSGULV}.")
                if feil_paa_rad >= FEIL_PAA_RAD:
                    raise Stopp(f"{feil_paa_rad} kall på rad feilet uten svar om at tickeren ikke finnes.")
            elif bonus_naa != bonus:
                raise Stopp(f"extraLimit er endret fra {bonus} til {bonus_naa}, så bonuskvoten kan være brukt.")
            elif brukt > min(grense, grense_naa):
                raise Stopp(f"apiRequests er {brukt}, over dagens {min(grense, grense_naa)}.")
    except Stopp as stopp:
        skriv(f"STOPP: {stopp}")
        kode = 1
    except BaseException as feil:
        avbrutt = feil
        kode = 1

    if serier or feil_ved:
        bilde = {
            "hentet": start.isoformat(),
            "boersdag": boersdag.isoformat(),
            "fra": fra.isoformat(),
            "til": til.isoformat(),
            "serier": serier,
            "feil": feil_ved,
        }
        kode = _lagre(data_katalog, base_sti, bilde, boersdag, start.isoformat(), fra, til, maalinger, skriv) or kode
    skriv(f"API-kall brukt: {kall}.")
    if med_bonus and etter is not None:
        skriv(f"Kall fra bonuskvoten: {fra_bonus}.")
    if etter is not None:
        skriv(f"Kvoten etter: {etter[0]} av {etter[1]} brukt {etter[3].isoformat()} i GMT, extraLimit {etter[2]}.")
    if avbrutt is not None:
        raise avbrutt
    return kode
