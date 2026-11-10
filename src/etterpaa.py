"""«Etterpå» under hvert notat i «Mine notater» - story 8.21, AD-7, NFR-06,
NFR-08 (gruppens svar 10.11 kl. 14:32).

Bare fakta: endringen i aksjen og i hovedindeksen fra notatdagen til siste
dag med kurser, på justert kurs (FR-101), og signalet som er lagret for de to
dagene, som i «Signalet dag for dag». Signalet leses og regnes aldri (AD-7).
Appen sier aldri om et notat var riktig eller galt, og gir ingen råd (NFR-06).

Ren logikk. Ingen API-kall, ingen filer og ingen klokke: serien, indeksen og
radene i vurdering kommer inn som argumenter.
"""

from dataclasses import dataclass
from datetime import date

from historikk import Dag, _dag
from kursdata import Kursrad
from markedsoversikt import endring_i_prosent
from notater import Notat
from vurderingsdata import Grunn, Vurdering


@dataclass(frozen=True)
class Etterpaa:
    """Det som står under et notat (spørsmål 4-6).

    siste er siste dag med kurser for aksjen, eller None når aksjen ikke har
    kurs etter notatdagen. aksjen og indeksen er endringen i prosent fra
    notatdagen til siste, eller None når en av kursene mangler, med grunnen i
    aksjen_grunn og indeksen_grunn (NFR-08). paa_dagen og paa_siste er
    signalet som er lagret for dagene, som i «Signalet dag for dag», og None
    når vurderingene ikke kunne leses.
    """

    notatdag: date
    siste: date | None
    aksjen: float | None
    aksjen_grunn: str | None
    indeksen: float | None
    indeksen_grunn: str | None
    paa_dagen: Dag | None
    paa_siste: Dag | None


INGEN_KURS_PAA_NOTATDAGEN = "aksjen har ingen kurs fra notatdagen"
INGEN_INDEKS = "hovedindeksen er ikke hentet"
INDEKSEN_MANGLER_DAGEN = "hovedindeksen har ingen kurs fra en av dagene"


@dataclass(frozen=True)
class _Kurs:
    justert_slutt: float


def endring(kurser: dict[date, float], fra: date, til: date) -> float | None:
    """Endringen i prosent på justert kurs fra fra til til, regnet med
    endring_i_prosent i markedsoversikt.py (FR-101). None når en av dagene
    mangler, eller kursen på fra er 0."""
    paa_fra, paa_til = kurser.get(fra), kurser.get(til)
    if paa_fra is None or paa_til is None or paa_fra == 0:
        return None
    return endring_i_prosent([_Kurs(paa_fra), _Kurs(paa_til)])


def bygg_etterpaa(
    notat: Notat,
    serie: list[Kursrad],
    indeks: dict[date, float] | None,
    vurderinger: dict[date, Vurdering | Grunn] | None,
    idag: date,
    terskel: int,
    ut: date | None = None,
) -> Etterpaa:
    """«Etterpå» for et notat. Ren logikk: serien, indeksen ({dato: justert
    slutt}) og radene i vurdering kommer inn som argumenter, og signalet
    regnes aldri (AD-7). indeks er None når basen ikke har en indeks, og
    vurderinger None når de ikke kunne leses."""
    kursdager = frozenset(rad.dato for rad in serie)
    foerste = serie[0].dato if serie else notat.dato
    sist = serie[-1].dato if serie else notat.dato

    def dag(dato: date) -> Dag | None:
        if vurderinger is None:
            return None
        return _dag(dato, kursdager, foerste, sist, vurderinger, idag, terskel, ut)

    paa_dagen = dag(notat.dato)
    if not serie or sist <= notat.dato:
        return Etterpaa(notat.dato, None, None, None, None, None, paa_dagen, None)
    aksjen = endring({rad.dato: float(rad.justert_slutt) for rad in serie}, notat.dato, sist)
    aksjen_grunn = None if aksjen is not None else INGEN_KURS_PAA_NOTATDAGEN
    if indeks is None:
        indeksen, indeksen_grunn = None, INGEN_INDEKS
    else:
        indeksen = endring(indeks, notat.dato, sist)
        indeksen_grunn = None if indeksen is not None else INDEKSEN_MANGLER_DAGEN
    return Etterpaa(notat.dato, sist, aksjen, aksjen_grunn, indeksen, indeksen_grunn, paa_dagen, dag(sist))
