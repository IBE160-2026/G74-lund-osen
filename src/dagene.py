"""Hvor lenge signalet har vaert slik - story 10.2e, gruppens svar 25.10 kl. 00:51.

Ren logikk. Tellingen er fra svaret 24.10 kl. 16:15 a): boersdager paa rad
med samme retning og styrke, til og med dagen. Den laa i ki_grunnlag.py, men
modellen faar ikke lenger dagene, og appen skriver dem selv i en setning
under KI-teksten paa aksjesiden. Modulen er utenfor ki_*, saa webserveren
ikke importerer noe fra KI-laget (AD-10).
"""

from collections.abc import Mapping
from datetime import date

from boersdag import UtenforKalenderen, forrige_boersdag
from tallformat import tall
from vurderingsdata import Grunn, Vurdering

DAGENE_FOERSTE = "Signalet er slik i dag for første gang."
# For en dag som ikke er i dag passer ikke «i dag»: en dag valgt med «Velg
# dag», og siste boersdag i helga eller foer kveldshentingen. Datoen staar
# oeverst paa siden (gruppens svar 25.10 kl. 11:04 b), gjennomgangen, BH1).
DAGENE_FOERSTE_VALGT = "Signalet ble slik denne dagen for første gang."
DAGENE_PAA_RAD = "Signalet har vært slik i {dager} børsdager på rad."
DAGENE_MINST_EN = "Signalet har vært slik i minst 1 børsdag."
DAGENE_MINST = "Signalet har vært slik i minst {dager} børsdager."


def tell_dagene(dag: date, vurdering: Vurdering, tidligere: Mapping[date, Vurdering | Grunn]) -> tuple[int, bool]:
    """Boersdager paa rad til og med dag med samme retning og styrke, og om
    rekka er «minst» (gruppens svar 24.10 kl. 16:15, a).

    tidligere er de lagrede radene for aksjen foer dag. Rekka stopper ved en
    annen retning eller styrke eller en grunn, og da er antallet kjent. En
    boersdag uten rad, ogsaa foer foerste lagrede vurdering, eller en dag
    utenfor kalenderen, gir «minst»: hvordan signalet var foer, er ukjent.
    """
    dager = 1
    naa = dag
    while True:
        try:
            naa = forrige_boersdag(naa)
        except UtenforKalenderen:
            return dager, True
        rad = tidligere.get(naa)
        if rad is None:
            return dager, True
        if not isinstance(rad, Vurdering) or (rad.retning, rad.styrke) != (vurdering.retning, vurdering.styrke):
            return dager, False
        dager += 1


def setning_om_dagene(dager: int, minst: bool, annen_dag: bool = False) -> str:
    """Setningen under KI-teksten. minst er True naar dagene foer ikke er
    lagret, saa antallet er det minste det kan vaere. annen_dag er True naar
    dagen siden viser, ikke er i dag. Tallet vises etter regel 21
    (tallformat.tall)."""
    if type(dager) is not int or dager < 1:
        raise ValueError("dager maa vaere et heltall fra 1")
    if minst:
        return DAGENE_MINST_EN if dager == 1 else DAGENE_MINST.format(dager=tall(dager, "heltall"))
    if dager == 1:
        return DAGENE_FOERSTE_VALGT if annen_dag else DAGENE_FOERSTE
    return DAGENE_PAA_RAD.format(dager=tall(dager, "heltall"))
