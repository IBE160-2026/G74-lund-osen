"""De tre moenstrene appen regner ut - story 10.9, gruppens svar 06.11 kl.
20:38 og 22:05, med forslagene i spoersmaal 3-6 i spesifikasjonen (godtatt
07.11 kl. 08:58).

Ren logikk, utenfor ki_*, som dagene.py. Moenstrene regnes bare av det som
er lagret: vurderingene i basen og kursene. De regnes aldri bakover paa nytt
(AD-7). Modellen faar antallene i grunnlaget (ki_grunnlag.py) og skriver én
setning om dem. Den finner aldri moenstre selv (svaret kl. 20:38).

1. Retningen de siste 20 boersdagene: hvor mange av de vurderte boersdagene
   i vinduet signalet var Positiv, Negativ, Blandet og Ingen. En dag uten
   lagret vurdering, eller med en grunn, telles ikke (spoersmaal 3). Med
   faerre enn 10 vurderte dager gis ikke moensteret.
2. Samme vei som hovedindeksen de siste 5 boersdagene: en dag telles bare
   naar aksjens forrige rad er forrige boersdag, og naar baade aksjen og
   hovedindeksen steg eller falt, som ordlyden om hovedindeksen i versjon 4
   (spoersmaal 4). Kunne faerre enn 3 telles, gis ikke moensteret.
3. Skift i retningen den siste maaneden: fra samme dato én maaned foer, som
   perioden «1 mnd» (perioder.startdag). Et skift telles mellom to vurderte
   boersdager som foelger rett etter hverandre. En dag som ikke er vurdert,
   bryter rekka, og da er antallet «minst» (spoersmaal 5). Uten to vurderte
   boersdager paa rad gis ikke moensteret.

Antall, ikke prosent (spoersmaal 6): grunnlaget har bare heltall.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date

from boersdag import UtenforKalenderen, forrige_boersdag

# Retningen paa én dag regnes som paa siden og i grunnlaget (dagene.py), saa
# moenster 2 og ordlyden om hovedindeksen ikke kan si ulikt.
from dagene import FALT, STEG, _endringen, _retningen_paa_dagen, _samme_periode, bevegelse
from kursdata import Kursrad
from perioder import EN_MND, startdag
from signalberegning import BLANDET, INGEN, NEGATIV, POSITIV
from vurderingsdata import Grunn, Vurdering, kveldsradene

VINDU_RETNINGEN = 20
MINST_VURDERTE = 10
VINDU_SAMME_VEI = 5
MINST_TELT = 3
MINST = "minst"


@dataclass(frozen=True)
class Moenstrene:
    """De tre moenstrene for én aksje og én dag. Et moenster er None naar
    det ikke gis, og da har grunnlaget ikke feltene."""

    # Moenster 1: (vurderte, positiv, negativ, blandet, ingen).
    retningene: tuple[int, int, int, int, int] | None
    # Moenster 2: (kunne telles, samme vei).
    samme_vei: tuple[int, int] | None
    # Moenster 3: (skift, minst).
    skiftene: tuple[int, bool] | None


def boersdagene(dag: date, antall: int) -> list[date]:
    """antall boersdager til og med dag, den nyeste foerst. Faerre naar
    boerskalenderen slutter foer (UtenforKalenderen)."""
    dagene = [dag]
    while len(dagene) < antall:
        try:
            dagene.append(forrige_boersdag(dagene[-1]))
        except UtenforKalenderen:
            break
    return dagene


def retningene(dag: date, radene: Mapping[date, Vurdering | Grunn]) -> tuple[int, int, int, int, int] | None:
    """Moenster 1. radene er de lagrede radene for aksjen, med dag. Story
    2.17: bare kveldsradene."""
    radene = kveldsradene(radene)
    vurdert = [r.retning for d in boersdagene(dag, VINDU_RETNINGEN) if isinstance(r := radene.get(d), Vurdering)]
    if len(vurdert) < MINST_VURDERTE:
        return None
    return (len(vurdert), vurdert.count(POSITIV), vurdert.count(NEGATIV), vurdert.count(BLANDET), vurdert.count(INGEN))


def samme_vei(dag: date, serie: list[Kursrad], indeksserie: list[Kursrad] | None) -> tuple[int, int] | None:
    """Moenster 2. serie er kursene for aksjen og indeksserie hovedindeksen."""
    telt = samme = 0
    for d in boersdagene(dag, VINDU_SAMME_VEI):
        if not _samme_periode(serie, d):
            continue
        aksjen = bevegelse(_endringen(serie, d))
        indeksen = _retningen_paa_dagen(indeksserie or [], d)
        if aksjen in (STEG, FALT) and indeksen in (STEG, FALT):
            telt += 1
            samme += aksjen == indeksen
    return (telt, samme) if telt >= MINST_TELT else None


def skiftene(dag: date, radene: Mapping[date, Vurdering | Grunn]) -> tuple[int, bool] | None:
    """Moenster 3. Gir (skift, minst), eller None uten to vurderte
    boersdager paa rad i maaneden. Story 2.17: bare kveldsradene."""
    radene = kveldsradene(radene)
    fra = startdag(EN_MND, dag)
    dagene = [dag]
    minst = False
    while True:
        try:
            forrige = forrige_boersdag(dagene[-1])
        except UtenforKalenderen:
            # Kalenderen slutter inne i maaneden: dagene foer er ukjente.
            minst = True
            break
        if forrige < fra:
            break
        dagene.append(forrige)
    skift = par = 0
    for nyere, eldre in zip(dagene, dagene[1:]):
        a, b = radene.get(nyere), radene.get(eldre)
        if not (isinstance(a, Vurdering) and isinstance(b, Vurdering)):
            minst = True
            continue
        par += 1
        skift += a.retning != b.retning
    if not all(isinstance(radene.get(d), Vurdering) for d in dagene):
        minst = True
    return (skift, minst) if par else None


def lag_moenstrene(
    dag: date,
    vurdering: Vurdering,
    tidligere: Mapping[date, Vurdering | Grunn],
    serie: list[Kursrad],
    indeksserie: list[Kursrad] | None,
) -> Moenstrene:
    """De tre moenstrene for dag. tidligere er de lagrede radene for aksjen,
    som i tell_dagene. vurdering er raden for dag."""
    radene = {**tidligere, dag: vurdering}
    return Moenstrene(
        retningene=retningene(dag, radene),
        samme_vei=samme_vei(dag, serie, indeksserie),
        skiftene=skiftene(dag, radene),
    )
