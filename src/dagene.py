"""Hvor lenge signalet har vaert slik - story 10.2e, gruppens svar 25.10 kl. 00:51,
med ordlyden fra svarene kl. 12:12 og 12:19.

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

# Uten «for første gang», fordi tellingen gjelder dagene paa rad (gruppens
# svar 25.10 kl. 12:12 a), gjennomgangen kl. 11, BH2, ECH7).
DAGENE_EN = "Signalet ble slik i dag."
DAGENE_PAA_RAD = "Signalet har vært slik i {dager} børsdager på rad."
DAGENE_MINST_EN = "Signalet har vært slik i minst 1 børsdag."
DAGENE_MINST = "Signalet har vært slik i minst {dager} børsdager."
# For en dag som ikke er i dag passer ikke «i dag» eller «har vært»: en dag
# valgt med «Velg dag», og siste boersdag i helga eller foer kveldshentingen
# (svarene kl. 12:12 c) og 12:19 d), gjennomgangen kl. 11, BH1, BH5).
DAGENE_EN_ANNEN = "Signalet ble slik denne dagen."
DAGENE_PAA_RAD_ANNEN = "Denne dagen hadde signalet vært slik i {dager} børsdager på rad."
DAGENE_MINST_EN_ANNEN = "Denne dagen hadde signalet vært slik i minst 1 børsdag."
DAGENE_MINST_ANNEN = "Denne dagen hadde signalet vært slik i minst {dager} børsdager."


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
        en, flere = (DAGENE_MINST_EN_ANNEN, DAGENE_MINST_ANNEN) if annen_dag else (DAGENE_MINST_EN, DAGENE_MINST)
    else:
        en, flere = (DAGENE_EN_ANNEN, DAGENE_PAA_RAD_ANNEN) if annen_dag else (DAGENE_EN, DAGENE_PAA_RAD)
    return en if dager == 1 else flere.format(dager=tall(dager, "heltall"))
