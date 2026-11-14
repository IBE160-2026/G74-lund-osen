"""De tre tilstandene - story 1.7, FR-409, punkt 24 i prd.md §8, AD-7.

Ren logikk. Ingen API-kall, ingen filer, og klokka leses aldri her: dagens
dato kommer inn som argument, som dag i boersdag.innevaerende_boersdag.

Vurderingslager.les gir None baade for en boersdag uten rad og for en dag som
ikke finnes. De to maa ikke forveksles: det foerste er et hull i vaar egen
drift, det andre er ingenting. tilstand skiller dem med boersdag.er_boersdag,
samme liste over stengte dager som 1.6, og gir en av fire verdier, aldri
None. Den fjerde er raden med grunn fra punkt 24: kommandoen kjoerte, men
kunne ikke vurdere aksjen.

Story 2.17 (gruppens svar 2026-11-14 kl. 05:41-05:49): en rad med vurdering
regnet i ettertid, av kursene for en tidligere boersdag uten kveldsrad, er en
egen tilstand, ETTERTID. Den har et signal, som SVAR, og MED_SIGNAL er de to.
Visningene merker den med «i ettertid».

Enhver visning, kommando eller spoerring som senere leser historikken, skal
bevare skillet (FR-409). Kalleren i produksjonskoden er sidene: fra story
2.2b viser oversikten og aksjedetaljen raden for datoen til nyeste kurs
gjennom tilstand (markedsoversikt.les_tilstand). Historikken i punkt 20
kommer i story 2.7.
"""

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from boersdag import er_boersdag
from vurderingsdata import Grunn, Vurdering


class Art(StrEnum):
    SVAR = "svar"  # rad med vurdering, ogsaa styrke 0
    # Story 2.17: rad med vurdering regnet i ettertid, ikke av kveldens henting.
    ETTERTID = "ettertid"
    GRUNN = "grunn"  # rad med grunn (punkt 24)
    IKKE_KJOERT = "ikke_kjoert"  # ingen rad, og dagen var boersdag
    IKKE_BOERSDAG = "ikke_boersdag"  # ingen rad, og dagen var ikke boersdag
    # Story 2.11: ingen rad, og aksjen var tatt ut av lista den dagen.
    IKKE_I_LISTA = "ikke_i_lista"


# Story 2.17: tilstandene med et signal. En visning som sjekker «har raden en
# vurdering», sjekker disse to, og merker ETTERTID.
MED_SIGNAL = frozenset({Art.SVAR, Art.ETTERTID})


@dataclass(frozen=True)
class Tilstand:
    """Utfallet for en aksje en dag. innhold er raden, None naar den mangler."""

    art: Art
    innhold: Vurdering | Grunn | None = None

    @property
    def vurdering(self) -> Vurdering | None:
        """Vurderingen naar raden har et signal (MED_SIGNAL), ellers None."""
        return self.innhold if self.art in MED_SIGNAL else None

    @property
    def ettertid(self) -> bool:
        """Story 2.17: signalet er regnet i ettertid."""
        return self.art is Art.ETTERTID


def _kontroller_dag(navn: str, verdi) -> None:
    if not isinstance(verdi, date) or isinstance(verdi, datetime):
        raise TypeError(f"{navn} maa vaere datetime.date, fikk {verdi!r}")


def tilstand(innhold: Vurdering | Grunn | None, dato: date, idag: date, ut: date | None = None) -> Tilstand:
    """Tilstanden for det Vurderingslager.les ga for dato, sett fra idag.

    idag er dagens dato i Oslo (boersdag.norsk_dato). Grensen er dagens dato og
    ikke inneveerende boersdag, saa en loerdag selv er en dag som ikke finnes,
    ikke fremtid. En dato etter idag reiser ValueError: den er verken ikke
    kjoert eller ikke boersdag.

    Typene kontrolleres foerst, saa feil innhold alltid gir TypeError.
    Deretter datoen: en dato etter idag reiser ogsaa naar raden finnes. Finnes
    raden, er utfallet raden, uten oppslag i kalenderen. Mangler den, avgjoer
    er_boersdag, og en dag foer FOERSTE_AAR reiser UtenforKalenderen i stedet for
    aa gjette.

    IKKE_KJOERT er ikke et endelig hull saa lenge dato er inneveerende
    boersdag. Raden kan skrives helt til neste boersdag begynner, saa
    fredagens rad kan komme paa loerdag. Hullet er endelig foerst naar dato
    ikke lenger er inneveerende boersdag (AD-7). Boersdager foer foerste
    kjoering er ogsaa IKKE_KJOERT: startdatoen lagres ikke, og trengs den, er
    den datoen til foerste rad i tabellen.
    """
    if innhold is not None and not isinstance(innhold, (Vurdering, Grunn)):
        raise TypeError(f"innhold maa vaere Vurdering, Grunn eller None, fikk {type(innhold).__name__}")
    _kontroller_dag("dato", dato)
    _kontroller_dag("idag", idag)
    if dato > idag:
        raise ValueError(
            f"{dato.isoformat()} er etter i dag ({idag.isoformat()}): dagen har "
            "ikke vaert, og er verken ikke kjoert eller ikke boersdag"
        )
    if isinstance(innhold, Vurdering):
        return Tilstand(Art.ETTERTID if innhold.ettertid else Art.SVAR, innhold)
    if isinstance(innhold, Grunn):
        return Tilstand(Art.GRUNN, innhold)
    # Story 2.11: ut er den foerste dagen aksjen ikke er i lista. En boersdag
    # uten rad fra og med den er «ikke i lista», ikke en dag vi ikke kjoerte.
    if ut is not None:
        _kontroller_dag("ut", ut)
        if dato >= ut and er_boersdag(dato):
            return Tilstand(Art.IKKE_I_LISTA)
    if er_boersdag(dato):
        return Tilstand(Art.IKKE_KJOERT)
    return Tilstand(Art.IKKE_BOERSDAG)
