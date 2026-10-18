"""Periodene i periodevalget og regelen for startdagen - story 8.16, FR-201,
designregler.md §2, NFR-08.

Ren logikk. Ingen API-kall, ingen filer og ingen klokke: dagene kommer inn
som argumenter. Regelen staar i designregler.md §2, og startdag() er den
eneste funksjonen som regner den, saa kursgrafen og periodevalget i
oversikten (8.17) bruker samme startdag.

1 uke, 1 mnd, 3 mnd, 6 mnd og 1 aar regnes bakover fra siste dag i grafen
etter kalenderen. En dato maaneden ikke har, blir maanedens siste dag.
Startdagen er foerste boersdag paa eller etter den datoen. I aar starter paa
aarets foerste boersdag. Ligger datoen i et aar boerskalenderen ikke dekker,
er startdagen foerste hverdag paa eller etter den.
"""

import calendar
from datetime import date, timedelta

from boersdag import UtenforKalenderen, er_boersdag

# Kodene i adressen, i rekkefoelgen i designregler.md §2.
SISTE = "siste"
EN_UKE = "1-uke"
EN_MND = "1-mnd"
TRE_MND = "3-mnd"
SEKS_MND = "6-mnd"
I_AAR = "i-aar"
ETT_AAR = "1-aar"
VELG = "velg"

PERIODENE = (SISTE, EN_UKE, EN_MND, TRE_MND, SEKS_MND, I_AAR, ETT_AAR, VELG)

# Navnet paa knappen. Den foerste heter etter dagen (foerste_knapp), og
# «Velg dag» viser dagen naar den er valgt.
NAVN = {
    EN_UKE: "1 uke",
    EN_MND: "1 mnd",
    TRE_MND: "3 mnd",
    SEKS_MND: "6 mnd",
    I_AAR: "I år",
    ETT_AAR: "1 år",
    VELG: "Velg dag",
}

# Maaneder bakover for periodene som regnes i maaneder.
MAANEDER = {EN_MND: 1, TRE_MND: 3, SEKS_MND: 6, ETT_AAR: 12}


def maaneder_tilbake(dag: date, antall: int) -> date:
    """Samme dato antall maaneder foer. En dato maaneden ikke har, blir
    maanedens siste dag: 31.03 minus 1 mnd er 28.02."""
    maaned = dag.month - 1 - antall
    aar = dag.year + maaned // 12
    maaned = maaned % 12 + 1
    return date(aar, maaned, min(dag.day, calendar.monthrange(aar, maaned)[1]))


def foerste_boersdag_fra(dag: date) -> date:
    """Foerste boersdag paa eller etter dag. Utenfor boerskalenderen
    (UtenforKalenderen) er det foerste hverdag paa eller etter dag."""
    while True:
        try:
            if er_boersdag(dag):
                return dag
        except UtenforKalenderen:
            if dag.weekday() < 5:
                return dag
        dag += timedelta(days=1)


def startdag(periode: str, siste: date) -> date:
    """Startdagen for perioden, med siste som siste dag i grafen.

    Siste boersdag og «Velg dag» viser 6 mnd fram til dagen, og regnes som 6
    mnd. Reiser ValueError for en periode som ikke finnes."""
    if periode == EN_UKE:
        return foerste_boersdag_fra(siste - timedelta(days=7))
    if periode in MAANEDER:
        return foerste_boersdag_fra(maaneder_tilbake(siste, MAANEDER[periode]))
    if periode == I_AAR:
        # 1. januar er alltid stengt (STENGT), ogsaa utenfor kalenderen.
        return foerste_boersdag_fra(date(siste.year, 1, 2))
    if periode in (SISTE, VELG):
        return startdag(SEKS_MND, siste)
    raise ValueError(f"ukjent periode: {periode!r}")
