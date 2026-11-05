"""Hvor lenge signalet har vaert slik - story 10.2e, gruppens svar 25.10 kl. 00:51,
med ordlyden fra svarene kl. 12:12 og 12:19.

Ren logikk. Tellingen er fra svaret 24.10 kl. 16:15 a): boersdager paa rad
med samme retning og styrke, til og med dagen. Den laa i ki_grunnlag.py, men
modellen faar ikke lenger dagene, og appen skriver dem selv i en setning
under KI-teksten paa aksjesiden. Modulen er utenfor ki_*, saa webserveren
ikke importerer noe fra KI-laget (AD-10).

Story 10.2i, gruppens svar 5.11 kl. 19:13 og 23:36: appen skriver ogsaa
setningen om hva hovedindeksen, bransjen og antallene gjorde samme dag
(setning_om_samme_dag), under KI-teksten som setningen om dagene, og
modellen skriver ikke om dagen. Dagsbildet ble derfor flyttet hit fra
ki_grunnlag.py, saa siden og grunnlaget til modellen regnes av den samme
funksjonen (lag_dagsbilde), og webserveren fortsatt ikke importerer KI-laget.
Setningen sier aldri at dagen forklarer signalet (BH7 i PR #113).
"""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date

from boersdag import UtenforKalenderen, forrige_boersdag
from hovedindeks import indeksendring
from kursdata import Aksje, Kursrad
from markedsoversikt import endring_i_prosent
from tallformat import avrundet, tall
from vurderingsdata import Grunn, Vurdering

# Story 10.2e: retningen paa hovedindeksen og bransjen.
STEG, FALT, UENDRET = "steg", "falt", "uendret"
BEVEGELSER = (STEG, FALT, UENDRET)

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


@dataclass(frozen=True)
class Dagsbilde:
    """Dagen rundt aksjen. hovedindeksen og bransjen er None naar de ikke
    kan regnes, og da sier verken grunnlaget eller setningen noe om dem."""

    dager: int
    dager_minst: bool
    hovedindeksen: str | None
    aksjer_steg: int
    aksjer_falt: int
    bransjen: str | None


def bevegelse(endring: float | None) -> str | None:
    """steg, falt eller uendret etter endringen slik den vises, eller None."""
    if endring is None:
        return None
    vist = avrundet(endring, "endring")
    return STEG if vist > 0 else FALT if vist < 0 else UENDRET


def _endringen(serie: list[Kursrad], dag: date) -> float | None:
    """Endringen for dag som i boersometeret (bygg_rute): de to siste
    radene til og med dag, og None uten kurs paa dag."""
    til = [rad for rad in serie if rad.dato <= dag]
    if not til or til[-1].dato != dag:
        return None
    return endring_i_prosent(til[-2:])


def lag_dagsbilde(
    aksje: Aksje,
    dag: date,
    vurdering: Vurdering,
    tidligere: Mapping[date, Vurdering | Grunn],
    lista: tuple[Aksje, ...],
    serier: Mapping[str, list[Kursrad]],
    indeksserie: list[Kursrad] | None,
) -> Dagsbilde:
    """Dagsbildet for aksjen paa dag. serier er kursene for aksjene i lista,
    og indeksserie hovedindeksen, eller None naar basen ikke har en."""
    dager, minst = tell_dagene(dag, vurdering, tidligere)
    endringer = {a.symbol: _endringen(serier.get(a.symbol, []), dag) for a in lista}
    retninger = [bevegelse(e) for e in endringer.values()]
    i_bransjen = [endringer[a.symbol] for a in lista if a.sektor == aksje.sektor and endringer[a.symbol] is not None]
    indeks = None
    if indeksserie:
        til = [rad for rad in indeksserie if rad.dato <= dag]
        if til and til[-1].dato == dag:
            indeks = bevegelse(indeksendring(til))
    return Dagsbilde(
        dager=dager,
        dager_minst=minst,
        hovedindeksen=indeks,
        aksjer_steg=retninger.count(STEG),
        aksjer_falt=retninger.count(FALT),
        bransjen=bevegelse(sum(i_bransjen) / len(i_bransjen)) if i_bransjen else None,
    )


# Verbet og det som staar etter subjektet: «steg», «falt», «var … uendret».
_VERBET = {STEG: ("steg", ""), FALT: ("falt", ""), UENDRET: ("var", " uendret")}


def setning_om_samme_dag(bildet: Dagsbilde) -> str:
    """Setningen under KI-teksten om hva hovedindeksen, bransjen og antallene
    gjorde samme dag (gruppens svar 5.11 kl. 19:13 og 23:36). Av de samme
    verdiene som grunnlaget, og uten det som mangler. «Samme dag» passer
    baade i dag og for en valgt dag. Setningen nevner ikke signalet og sier
    ingen grunn, saa den ikke kan leses som at dagen forklarer det (BH7).
    Tallene vises etter regel 21 (tallformat.tall)."""
    for verdi in (bildet.hovedindeksen, bildet.bransjen):
        if verdi is not None and verdi not in BEVEGELSER:
            raise ValueError(f"hovedindeksen og bransjen maa vaere en av {BEVEGELSER} eller None")
    for antall in (bildet.aksjer_steg, bildet.aksjer_falt):
        if type(antall) is not int or antall < 0:
            raise ValueError("antallene maa vaere heltall fra 0")
    deler: list[tuple[str, str, str]] = []
    if bildet.hovedindeksen is not None:
        verb, hale = _VERBET[bildet.hovedindeksen]
        deler.append((verb, "hovedindeksen", hale))
    if bildet.bransjen is not None:
        verb, hale = _VERBET[bildet.bransjen]
        deler.append((verb, "bransjen", hale + " i snitt"))
    aksjer = "aksje" if bildet.aksjer_steg == 1 else "aksjer"
    deler.append(
        (
            "steg",
            f"{tall(bildet.aksjer_steg, 'heltall')} {aksjer} i lista",
            f" og {tall(bildet.aksjer_falt, 'heltall')} falt",
        )
    )
    # Foerste ledd med verbet foerst etter «Samme dag», de andre som vanlig.
    ledd = [f"{v} {s}{h}" if i == 0 else f"{s} {v}{h}" for i, (v, s, h) in enumerate(deler)]
    if len(ledd) == 1:
        return f"Samme dag {ledd[0]}."
    return f"Samme dag {', '.join(ledd[:-1])}, og {ledd[-1]}."
