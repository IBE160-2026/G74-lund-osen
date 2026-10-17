"""Hovedindeksen over tabellen paa forsiden - story 2.9, FR-104.

Ren logikk. Faar serien for indeksen og seriene for aksjene gjennom portene,
gjoer ingen nettkall (AD-10) og kjenner ingen HTML.

- Verdien er slutt for indeksens siste rad.
- Endringen regnes mot forrige boersdag etter kalenderen, ikke mot forrige
  rad, fordi indeksen kan ha datoer aksjene ikke har (malinger.md §14).
  Mangler raden for forrige boersdag, eller ligger dagen utenfor kalenderen,
  vises ingen endring.
- N er aksjene med kurs for indeksens dato, telt fra lista, aldri et fast
  antall (foeringen 30.09 under AD-21). En aksje som ikke er med, navngis.
- En aksjes endring for datoen er endringen fra FR-101, kursen den dagen mot
  raden foer, som i tabellen.
- «Bedre» avgjoeres paa endringene slik de vises (tallformat.avrundet), og
  lik er ikke bedre.
- Har ingen aksje kurs for indeksens dato, eller har indeksen ingen endring,
  er det ingen sammenligning.

Story 2.9b (FR-105): én soeyle per aksje med endringen for indeksens dato,
fra stoerst fall til stoerst stigning. Antallet telles. En aksje med kurs,
men uten rad foer dagen, faar ingen soeyle og navngis. Hoeyden og plassen
til indekslinja regnes her, i prosent av feltet, med null midt i det og den
stoerste endringen av soeylene og indeksen paa halve hoeyden.
"""

from dataclasses import dataclass
from datetime import date, timedelta

from boersdag import UtenforKalenderen, er_boersdag
from kursdata import Aksje, Kursrad
from markedsoversikt import endring_i_prosent
from tallformat import avrundet

# Hoeyst saa mange dager tilbake leter forrige_boersdag. Den lengste stengte
# perioden ved Oslo Boers er paaskeuka med helgene rundt, under ti dager.
LETEDAGER = 14


@dataclass(frozen=True)
class Sammenligning:
    """«x av N gikk bedre enn indeksen», og aksjene som ikke er med."""

    bedre: int
    med: int
    uten: tuple[str, ...]


@dataclass(frozen=True)
class Soeyle:
    """En aksje under indeksen. endring er i prosent, uavrundet. hoeyde er
    lengden i prosent av feltet, fra null-linja midt i det."""

    symbol: str
    navn: str
    bransje: str
    endring: float
    tre_av_tre: bool
    hoeyde: float


@dataclass(frozen=True)
class Soeyler:
    """Soeylene under indeksen, fra stoerst fall til stoerst stigning.
    linje er toppen av den stiplede linja i prosent av feltet, og None naar
    indeksen ikke har en endring. uten_endring er aksjene med kurs for
    dagen, men uten rad foer den."""

    soeyler: tuple[Soeyle, ...]
    linje: float | None
    uten_endring: tuple[str, ...]


@dataclass(frozen=True)
class Hovedindeksvisning:
    """Det forsiden viser om indeksen. endring er i prosent, uavrundet, og
    None naar den ikke kan regnes. sammenligning er None naar den ikke vises."""

    symbol: str
    dato: date
    verdi: float
    endring: float | None
    sammenligning: Sammenligning | None
    soeyler: Soeyler | None = None


def forrige_boersdag(dag: date) -> date | None:
    """Boersdagen foer dag etter kalenderen, eller None naar den ligger
    utenfor aarene kalenderen dekker."""
    for tilbake in range(1, LETEDAGER + 1):
        foer = dag - timedelta(days=tilbake)
        try:
            if er_boersdag(foer):
                return foer
        except UtenforKalenderen:
            return None
    return None


def indeksendring(serie: list[Kursrad]) -> float | None:
    """Endringen i prosent for siste rad mot forrige boersdag, paa justert
    kurs som for aksjene. None uten rad for forrige boersdag."""
    if not serie:
        return None
    siste = serie[-1]
    foer = forrige_boersdag(siste.dato)
    if foer is None:
        return None
    paa_dag = {rad.dato: rad for rad in serie}
    if foer not in paa_dag:
        return None
    return endring_i_prosent([paa_dag[foer], siste])


def aksjeendring(serie: list[Kursrad], dag: date) -> float | None:
    """Endringen fra FR-101 for dag: kursen den dagen mot raden foer. None
    naar aksjen ikke har kurs for dagen, eller ingen rad foer den."""
    for i, rad in enumerate(serie):
        if rad.dato == dag:
            return endring_i_prosent(serie[i - 1 : i + 1]) if i > 0 else None
    return None


def er_bedre(aksje: float | None, indeks: float) -> bool:
    """Om aksjens endring slik den vises er stoerre enn indeksens. Lik er
    ikke bedre, og en aksje uten endring er ikke bedre."""
    return aksje is not None and avrundet(aksje, "endring") > avrundet(indeks, "endring")


def sammenlign(dag: date, indeks: float | None, aksjer: list[tuple[str, list[Kursrad]]]) -> Sammenligning | None:
    """«x av N» for dag. aksjer er (navn, serie) for hver aksje i lista, i
    lista sin rekkefoelge. None naar indeksen ikke har en endring, eller
    ingen aksje har kurs for dagen."""
    if indeks is None:
        return None
    med = [(navn, serie) for navn, serie in aksjer if any(rad.dato == dag for rad in serie)]
    if not med:
        return None
    uten = tuple(navn for navn, serie in aksjer if not any(rad.dato == dag for rad in serie))
    bedre = sum(1 for _, serie in med if er_bedre(aksjeendring(serie, dag), indeks))
    return Sammenligning(bedre=bedre, med=len(med), uten=uten)


def bygg_soeyler(dag: date, indeks: float | None, aksjer: list[tuple[Aksje, list[Kursrad], bool]]) -> Soeyler | None:
    """Soeylene for dag. aksjer er (aksje, serie, 3 av 3) for hver aksje i
    lista, i lista sin rekkefoelge. None naar ingen aksje har kurs for dagen."""
    med_kurs = [(aksje, serie, tre) for aksje, serie, tre in aksjer if any(rad.dato == dag for rad in serie)]
    if not med_kurs:
        return None
    endringer = [(aksje, aksjeendring(serie, dag), tre) for aksje, serie, tre in med_kurs]
    uten_endring = tuple(aksje.navn for aksje, endring, _ in endringer if endring is None)
    med = [(aksje, endring, tre) for aksje, endring, tre in endringer if endring is not None]
    # sorted er stabil, saa like endringer staar i rekkefoelgen fra lista.
    med.sort(key=lambda par: par[1])
    skala = max([abs(endring) for _, endring, _ in med] + [abs(indeks or 0.0)]) or 1.0
    soeyler = tuple(
        Soeyle(
            symbol=aksje.symbol,
            navn=aksje.navn,
            bransje=aksje.sektor,
            endring=endring,
            tre_av_tre=tre,
            hoeyde=abs(endring) / skala * 50,
        )
        for aksje, endring, tre in med
    )
    linje = None if indeks is None else 50 - indeks / skala * 50
    return Soeyler(soeyler=soeyler, linje=linje, uten_endring=uten_endring)


def bygg_hovedindeks(
    symbol: str,
    serie: list[Kursrad],
    aksjer: list[tuple[str, list[Kursrad]]],
    soeylegrunnlag: list[tuple[Aksje, list[Kursrad], bool]] | None = None,
) -> Hovedindeksvisning | None:
    """Det forsiden viser, eller None naar indeksen ikke har en eneste rad.
    soeylegrunnlag er (aksje, serie, 3 av 3) for soeylene (story 2.9b), og
    uten det er det ingen soeyler."""
    if not serie:
        return None
    siste = serie[-1]
    endring = indeksendring(serie)
    return Hovedindeksvisning(
        symbol=symbol,
        dato=siste.dato,
        verdi=float(siste.slutt),
        endring=endring,
        sammenligning=sammenlign(siste.dato, endring, aksjer),
        soeyler=bygg_soeyler(siste.dato, endring, soeylegrunnlag) if soeylegrunnlag is not None else None,
    )
