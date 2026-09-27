"""De tre tilstandene - story 1.7, FR-409, punkt 24 i prd.md §8, AD-7.

Ren logikk. Ingen API-kall, ingen filer, og klokka leses aldri her: dagens
dato kommer inn som argument, som dag i boersdag.innevaerende_boersdag.

Vurderingslager.les gir None baade for en boersdag uten rad og for en dag som
ikke finnes. De to maa ikke forveksles: det foerste er et hull i vaar egen
drift, det andre er ingenting. tilstand skiller dem med boersdag.er_boersdag,
samme liste over stengte dager som 1.6, og gir en av fire verdier, aldri
None. Den fjerde er raden med grunn fra punkt 24: kommandoen kjoerte, men
kunne ikke vurdere aksjen.

Enhver visning, kommando eller spoerring som senere leser historikken, skal
bevare skillet (FR-409). Ingen kaller i produksjonskoden ennaa (punkt 20).
"""

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from boersdag import er_boersdag
from vurderingsdata import Grunn, Vurdering


class Art(StrEnum):
    SVAR = "svar"                    # rad med vurdering, ogsaa styrke 0
    GRUNN = "grunn"                  # rad med grunn (punkt 24)
    IKKE_KJOERT = "ikke_kjoert"      # ingen rad, og dagen var boersdag
    IKKE_BOERSDAG = "ikke_boersdag"  # ingen rad, og dagen var ikke boersdag


@dataclass(frozen=True)
class Tilstand:
    """Utfallet for en aksje en dag. innhold er raden, None naar den mangler."""

    art: Art
    innhold: Vurdering | Grunn | None = None


def _kontroller_dag(navn: str, verdi) -> None:
    if not isinstance(verdi, date) or isinstance(verdi, datetime):
        raise TypeError(f"{navn} maa vaere datetime.date, fikk {verdi!r}")


def tilstand(innhold: Vurdering | Grunn | None, dato: date, idag: date) -> Tilstand:
    """Tilstanden for det Vurderingslager.les ga for dato, sett fra idag.

    idag er dagens dato i Oslo (boersdag.norsk_dato). Grensen er dagens dato og
    ikke inneveerende boersdag, saa en loerdag selv er en dag som ikke finnes,
    ikke fremtid. En dato etter idag reiser ValueError: den er verken ikke
    kjoert eller ikke boersdag.

    Typene kontrolleres foerst, saa feil innhold alltid gir TypeError.
    Deretter datoen: en dato etter idag reiser ogsaa naar raden finnes. Finnes
    raden, er utfallet raden, uten oppslag i kalenderen. Mangler den, avgjoer
    er_boersdag, og en dag utenfor lista reiser UtenforKalenderen i stedet for
    aa gjette.

    IKKE_KJOERT er ikke et endelig hull saa lenge dato er inneveerende
    boersdag. Raden kan skrives helt til neste boersdag begynner, saa
    fredagens rad kan komme paa loerdag. Hullet er endelig foerst naar dato
    ikke lenger er inneveerende boersdag (AD-7). Boersdager foer foerste
    kjoering er ogsaa IKKE_KJOERT: startdatoen lagres ikke, og trengs den, er
    den datoen til foerste rad i tabellen.
    """
    if innhold is not None and not isinstance(innhold, (Vurdering, Grunn)):
        raise TypeError(
            f"innhold maa vaere Vurdering, Grunn eller None, fikk {type(innhold).__name__}"
        )
    _kontroller_dag("dato", dato)
    _kontroller_dag("idag", idag)
    if dato > idag:
        raise ValueError(
            f"{dato.isoformat()} er etter i dag ({idag.isoformat()}): dagen har "
            "ikke vaert, og er verken ikke kjoert eller ikke boersdag"
        )
    if isinstance(innhold, Vurdering):
        return Tilstand(Art.SVAR, innhold)
    if isinstance(innhold, Grunn):
        return Tilstand(Art.GRUNN, innhold)
    if er_boersdag(dato):
        return Tilstand(Art.IKKE_KJOERT)
    return Tilstand(Art.IKKE_BOERSDAG)
