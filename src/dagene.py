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

Gruppens svar 6.11 kl. 09:55, 1 (BH4, ECH9 i PR #113): retningen paa aksjen
selv regnes som i tabellen, mot forrige rad, ogsaa paa en dag med hull, med
den samme endringen som antallene (_endringen). Hovedindeksen regnes
fortsatt mot forrige boersdag.

Gruppens svar 6.11 kl. 09:55, 2 (ECH6, BH11 i PR #113): bransjen staar bare
naar den har minst to aksjer i lista (MINST_I_BRANSJEN). Med én aksje ville
«bransjen i snitt» bare si hva aksjen selv gjorde. Snittet er det samme som i
boersometeret: endringen for aksjene i bransjen som har en endring.

Gruppens svar 6.11 kl. 11:15, 1 (BH1, ECH1, BH2 i PR #113): bransjen staar
bare naar minst to aksjer i bransjen har en endring den dagen. Med to i lista,
der bare én har endring, ville snittet ogsaa bare si hva den ene gjorde.

Gruppens svar 6.11 kl. 11:15, 2 (BH3, ECH2, VG2 i PR #113): aksjen regnes
fortsatt som i tabellen, men samme_periode sier om aksjens forrige rad er
forrige boersdag, den dagen hovedindeksen regnes mot. Bare da faar grunnlaget
hovedindeksen, og dermed ordlyden om aksjen gikk samme vei (ki_grunnlag.py),
saa teksten aldri sammenligner to ulike perioder.

Story 10.9, del A (gruppens svar 06.11 kl. 20:35, og spoersmaal 2 med
svaret 07.11 kl. 08:58): setningen om dagene faar datoen for den foerste
dagen i rekka (foerste_dag_i_rekka), vist som de andre datoene paa siden.
Med «minst» er dagen foer rekka ikke lagret, saa datoen signalet skiftet er
ukjent, og setningen sier «minst siden» den foerste lagrede dagen i rekka,
uten antallet. Appen skriver setningen, og modellen faar ikke datoen.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date

from boersdag import UtenforKalenderen, forrige_boersdag
from hovedindeks import forrige_boersdag as indeksens_forrige_boersdag
from hovedindeks import indeksendring
from kursdata import Aksje, Kursrad
from markedsoversikt import endring_i_prosent
from tallformat import avrundet, dato, tall, ukedag
from vurderingsdata import Grunn, Vurdering, kveldsradene

# Story 10.2e: retningen paa hovedindeksen og bransjen.
STEG, FALT, UENDRET = "steg", "falt", "uendret"
BEVEGELSER = (STEG, FALT, UENDRET)
# Svaret 6.11 kl. 09:55, 2: bransjen staar bare med minst to aksjer i lista.
# Svaret 6.11 kl. 11:15, 1: minst to av dem med en endring den dagen.
MINST_I_BRANSJEN = 2

# Uten «for første gang», fordi tellingen gjelder dagene paa rad (gruppens
# svar 25.10 kl. 12:12 a), gjennomgangen kl. 11, BH2, ECH7).
DAGENE_EN = "Signalet ble slik i dag."
# Story 10.9, del A: med datoen for den foerste dagen i rekka. Med «minst»
# staar datoen uten antallet (spoersmaal 2, svaret 07.11 kl. 08:58).
DAGENE_PAA_RAD = "Signalet har vært slik i {dager} børsdager på rad, siden {fra}."
DAGENE_MINST = "Signalet har vært slik minst siden {fra}."
# For en dag som ikke er i dag passer ikke «i dag» eller «har vært»: en dag
# valgt med «Velg dag», og siste boersdag i helga eller foer kveldshentingen
# (svarene kl. 12:12 c) og 12:19 d), gjennomgangen kl. 11, BH1, BH5).
DAGENE_EN_ANNEN = "Signalet ble slik denne dagen."
DAGENE_PAA_RAD_ANNEN = "Denne dagen hadde signalet vært slik i {dager} børsdager på rad, siden {fra}."
DAGENE_MINST_ANNEN = "Denne dagen hadde signalet vært slik minst siden {fra}."


def tell_dagene(dag: date, vurdering: Vurdering, tidligere: Mapping[date, Vurdering | Grunn]) -> tuple[int, bool]:
    """Boersdager paa rad til og med dag med samme retning og styrke, og om
    rekka er «minst» (gruppens svar 24.10 kl. 16:15, a).

    tidligere er de lagrede radene for aksjen foer dag. Rekka stopper ved en
    annen retning eller styrke eller en grunn, og da er antallet kjent. En
    boersdag uten rad, ogsaa foer foerste lagrede vurdering, eller en dag
    utenfor kalenderen, gir «minst»: hvordan signalet var foer, er ukjent.

    Story 2.17: bare kveldsradene telles. En dag med signalet regnet i
    ettertid er her som en dag uten rad, saa setningen er som foer storyen.
    """
    tidligere = kveldsradene(tidligere)
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


def foerste_dag_i_rekka(dag: date, dager: int) -> date:
    """Story 10.9, del A: den foerste boersdagen i rekka paa dager boersdager
    til og med dag, som tell_dagene teller dem. Med «minst» er det den
    foerste lagrede dagen i rekka, ikke dagen signalet skiftet."""
    if type(dager) is not int or dager < 1:
        raise ValueError("dager maa vaere et heltall fra 1")
    fra = dag
    for _ in range(dager - 1):
        fra = forrige_boersdag(fra)
    return fra


def setning_om_dagene(dager: int, minst: bool, annen_dag: bool = False, *, fra: date, i_aar: int) -> str:
    """Setningen i rammen «Signalet forklart». minst er True naar dagene
    foer ikke er lagret, saa antallet er det minste det kan vaere. annen_dag
    er True naar dagen siden viser, ikke er i dag. fra er den foerste dagen i
    rekka (foerste_dag_i_rekka), vist med ukedagen og datoen som ellers paa
    siden, med aaret bare naar det er et annet enn i_aar. Tallet vises etter
    regel 21 (tallformat.tall)."""
    if type(dager) is not int or dager < 1:
        raise ValueError("dager maa vaere et heltall fra 1")
    fra_tekst = f"{ukedag(fra)} {dato(fra, i_aar)}"
    if minst:
        return (DAGENE_MINST_ANNEN if annen_dag else DAGENE_MINST).format(fra=fra_tekst)
    if dager == 1:
        return DAGENE_EN_ANNEN if annen_dag else DAGENE_EN
    flere = DAGENE_PAA_RAD_ANNEN if annen_dag else DAGENE_PAA_RAD
    return flere.format(dager=tall(dager, "heltall"), fra=fra_tekst)


@dataclass(frozen=True)
class Dagsbilde:
    """Dagen rundt aksjen. hovedindeksen og bransjen er None naar de ikke
    kan regnes, og da sier verken grunnlaget eller setningen noe om dem.
    bransjen er ogsaa None naar faerre enn MINST_I_BRANSJEN aksjer i
    bransjen har en endring den dagen (svarene 6.11 kl. 09:55, 2 og
    kl. 11:15, 1)."""

    dager: int
    dager_minst: bool
    hovedindeksen: str | None
    aksjer_steg: int
    aksjer_falt: int
    bransjen: str | None
    # Story 10.2i (svarene 5.11 kl. 19:13 og 23:36): retningen paa aksjen selv
    # den dagen. Svaret 6.11 kl. 09:55, 1: regnet som i tabellen, mot forrige
    # rad (_endringen), ikke som hovedindeksen.
    aksjen: str | None = None
    # Svaret 6.11 kl. 11:15, 2: om aksjens forrige rad er forrige boersdag, saa
    # aksjen og hovedindeksen er regnet over den samme dagen. False uten det,
    # ogsaa naar aksjen mangler, saa ingen ordlyd gis uten at det er sjekket.
    samme_periode: bool = False


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


def _samme_periode(serie: list[Kursrad], dag: date) -> bool:
    """Svaret 6.11 kl. 11:15, 2: om aksjen har rad paa dag og forrige rad er
    forrige boersdag, den dagen hovedindeksen regnes mot (indeksendring).
    False ogsaa naar forrige boersdag ligger utenfor kalenderen."""
    til = [rad.dato for rad in serie if rad.dato <= dag]
    if len(til) < 2 or til[-1] != dag:
        return False
    return til[-2] == indeksens_forrige_boersdag(dag)


def _retningen_paa_dagen(serie: list[Kursrad], dag: date) -> str | None:
    """steg, falt eller uendret for hovedindeksen paa dag: indeksendring paa
    radene til og med dag, mot forrige boersdag. None uten rad paa dag eller
    paa forrige boersdag."""
    til = [rad for rad in serie if rad.dato <= dag]
    if not til or til[-1].dato != dag:
        return None
    return bevegelse(indeksendring(til))


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
    # Svaret 6.11 kl. 11:15, 1: ingen bransje med faerre enn to aksjer med en
    # endring den dagen, ogsaa naar bransjen har flere i lista.
    if len(i_bransjen) < MINST_I_BRANSJEN:
        i_bransjen = []
    indeks = _retningen_paa_dagen(indeksserie or [], dag)
    return Dagsbilde(
        dager=dager,
        dager_minst=minst,
        hovedindeksen=indeks,
        aksjer_steg=retninger.count(STEG),
        aksjer_falt=retninger.count(FALT),
        bransjen=bevegelse(sum(i_bransjen) / len(i_bransjen)) if i_bransjen else None,
        # Svaret 6.11 kl. 09:55, 1: aksjen som i tabellen og antallene, mot
        # forrige rad, ogsaa paa en dag med hull.
        aksjen=bevegelse(_endringen(serier.get(aksje.symbol, []), dag)),
        samme_periode=_samme_periode(serier.get(aksje.symbol, []), dag),
    )


# Verbet og det som staar etter subjektet: «steg», «falt», «var … uendret».
_VERBET = {STEG: ("steg", ""), FALT: ("falt", ""), UENDRET: ("var", " uendret")}


def setning_om_samme_dag(bildet: Dagsbilde, i_lista: int | None = None) -> str | None:
    """Setningen under KI-teksten om hva hovedindeksen, bransjen og antallene
    gjorde samme dag (gruppens svar 5.11 kl. 19:13 og 23:36). Av de samme
    verdiene som grunnlaget, og uten det som mangler. «Samme dag» passer
    baade i dag og for en valgt dag. Setningen nevner ikke signalet og sier
    ingen grunn, saa den ikke kan leses som at dagen forklarer det (BH7).
    Tallene vises etter regel 21 (tallformat.tall).

    Gjennomgangen (BH5, VG3, ECH10): naar ingen aksje steg eller falt, er
    antallene ofte ikke regnet, fordi kursene mangler, og da staar de ikke.
    Uten noe aa si er det ingen setning (None).

    Story 8.23 (tillegg 2, gruppens svar kl. 14:53 og 14:59): i_lista er
    antallet aksjer i lista den dagen. Med det sier setningen hvilken liste
    tallene gjelder: «13 av de 15 aksjene i lista steg og 2 falt». Det står
    ikke i Dagsbildet, saa grunnlaget for KI-teksten er som foer."""
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
    if bildet.aksjer_steg or bildet.aksjer_falt:
        if i_lista and i_lista > 1:
            hvem = f"{tall(bildet.aksjer_steg, 'heltall')} av de {tall(i_lista, 'heltall')} aksjene i lista"
        else:
            aksjer = "aksje" if bildet.aksjer_steg == 1 else "aksjer"
            hvem = f"{tall(bildet.aksjer_steg, 'heltall')} {aksjer} i lista"
        deler.append(("steg", hvem, f" og {tall(bildet.aksjer_falt, 'heltall')} falt"))
    if not deler:
        return None
    # Foerste ledd med verbet foerst etter «Samme dag», de andre som vanlig.
    ledd = [f"{v} {s}{h}" if i == 0 else f"{s} {v}{h}" for i, (v, s, h) in enumerate(deler)]
    if len(ledd) == 1:
        return f"Samme dag {ledd[0]}."
    return f"Samme dag {', '.join(ledd[:-1])}, og {ledd[-1]}."
