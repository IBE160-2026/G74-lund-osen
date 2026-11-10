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
from markedsoversikt import SJEKKBOKSTAVER, endring_i_prosent
from notater import Notat, TenktKjoep
from tallformat import fortegn
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
# Gjennomgangen (BH8): en indeks som ikke kunne leses, er ikke en indeks som
# ikke er hentet (NFR-08).
INDEKSEN_KUNNE_IKKE_LESES = "hovedindeksen kunne ikke leses"
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
    *,
    indeks_feilet: bool = False,
) -> Etterpaa:
    """«Etterpå» for et notat. Ren logikk: serien, indeksen ({dato: justert
    slutt}) og radene i vurdering kommer inn som argumenter, og signalet
    regnes aldri (AD-7). indeks er None når basen ikke har en indeks, eller
    når den ikke kunne leses (indeks_feilet), og vurderinger None når de
    ikke kunne leses."""
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
        indeksen, indeksen_grunn = None, INDEKSEN_KUNNE_IKKE_LESES if indeks_feilet else INGEN_INDEKS
    else:
        indeksen = endring(indeks, notat.dato, sist)
        indeksen_grunn = None if indeksen is not None else INDEKSEN_MANGLER_DAGEN
    return Etterpaa(notat.dato, sist, aksjen, aksjen_grunn, indeksen, indeksen_grunn, paa_dagen, dag(sist))


# --- Tillegget kl. 14:44: tenkte kjøp og salg --------------------------------


@dataclass(frozen=True)
class Handelen:
    """Det som står ved et tenkt kjøp (spørsmål 15-19).

    kjoepsdag og salgsdag er den første dagen i serien etter kjoep_etter og
    salg_etter, eller None mens sluttkursen ikke er hentet. aksjen og
    indeksen er endringen i prosent fra kjøpsdagen til salgsdagen, eller til
    siste dag med kurser mens kjøpet er åpent (til). dager er børsdagene med
    kurs fra kjøpet til salget. Bare prosent, ingen kronebeløp."""

    kjoep: TenktKjoep
    kjoepsdag: date | None
    salgsdag: date | None
    til: date | None
    aksjen: float | None
    indeksen: float | None
    indeksen_grunn: str | None
    dager: int | None

    @property
    def venter_paa_kjoepet(self) -> bool:
        return self.kjoepsdag is None

    @property
    def venter_paa_salget(self) -> bool:
        return self.kjoep.solgt is not None and self.salgsdag is None

    @property
    def kan_selges(self) -> bool:
        return self.kjoep.aapent and self.kjoepsdag is not None


def brikkene(sjekker: tuple[int, int, int] | None) -> tuple[tuple[str, str, str], ...]:
    """T, B og I som i historikken, fra sjekkene som ble lagret ved trykket."""
    if sjekker is None:
        return ()
    return tuple((bokstav, felt, fortegn(verdi)) for (bokstav, felt), verdi in zip(SJEKKBOKSTAVER, sjekker))


def _foerste_etter(serie: list[Kursrad], dag: date | None) -> date | None:
    if dag is None:
        return None
    return next((rad.dato for rad in serie if rad.dato > dag), None)


def bygg_handelen(
    kjoep: TenktKjoep, serie: list[Kursrad], indeks: dict[date, float] | None, *, indeks_feilet: bool = False
) -> Handelen:
    """Kjøpet og salget slik serien er nå: kursen leses ved hver visning og
    lagres aldri, så prosenten følger serien når den hentes på nytt eller
    justeres (spørsmål 15). Ren logikk."""
    kjoepsdag = _foerste_etter(serie, kjoep.kjoep_etter)
    salgsdag = _foerste_etter(serie, kjoep.salg_etter)
    if kjoepsdag is None:
        return Handelen(kjoep, None, salgsdag, None, None, None, None, None)
    if kjoep.solgt is not None:
        til = salgsdag
    else:
        til = serie[-1].dato if serie and serie[-1].dato > kjoepsdag else None
    if til is None:
        return Handelen(kjoep, kjoepsdag, salgsdag, None, None, None, None, None)
    aksjen = endring({rad.dato: float(rad.justert_slutt) for rad in serie}, kjoepsdag, til)
    if indeks is None:
        indeksen, grunn = None, INDEKSEN_KUNNE_IKKE_LESES if indeks_feilet else INGEN_INDEKS
    else:
        indeksen = endring(indeks, kjoepsdag, til)
        grunn = None if indeksen is not None else INDEKSEN_MANGLER_DAGEN
    dager = sum(1 for rad in serie if kjoepsdag < rad.dato <= til) if kjoep.solgt is not None else None
    return Handelen(kjoep, kjoepsdag, salgsdag, til, aksjen, indeksen, grunn, dager)
