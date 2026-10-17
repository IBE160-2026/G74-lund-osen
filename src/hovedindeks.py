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
"""

from dataclasses import dataclass
from datetime import date, timedelta

from boersdag import UtenforKalenderen, er_boersdag
from kursdata import Kursrad
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
class Hovedindeksvisning:
    """Det forsiden viser om indeksen. endring er i prosent, uavrundet, og
    None naar den ikke kan regnes. sammenligning er None naar den ikke vises."""

    symbol: str
    dato: date
    verdi: float
    endring: float | None
    sammenligning: Sammenligning | None


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


def sammenlign(
    dag: date, indeks: float | None, aksjer: list[tuple[str, list[Kursrad]]]
) -> Sammenligning | None:
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


def bygg_hovedindeks(
    symbol: str, serie: list[Kursrad], aksjer: list[tuple[str, list[Kursrad]]]
) -> Hovedindeksvisning | None:
    """Det forsiden viser, eller None naar indeksen ikke har en eneste rad."""
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
    )
