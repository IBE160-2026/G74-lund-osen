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
import re
from dataclasses import dataclass
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


def foerste_kursdag(serier, start: date, slutt: date) -> date | None:
    """Dagen den foerste kursen i perioden er fra: den tidligste datoen fra
    og med start til og med slutt i seriene (rader med .dato), eller None.

    Story 8.17a (gruppens svar 30.10 kl. 10:45, ECH1): linja over tabellen
    og soeylene sier denne dagen, ikke startdagen, saa ingen stengt dag
    utenfor boerskalenderen nevnes. Kalenderen faar ikke 2025."""
    return min((rad.dato for serie in serier for rad in serie if start <= rad.dato <= slutt), default=None)


# Overskriften over grafen for hver periode (FR-201). Siste boersdag og
# «Velg dag» faar dagen etter seg i malen: «6 måneder fram til fredag 09.10».
OVERSKRIFT = {
    SISTE: "6 måneder fram til",
    EN_UKE: "1 uke",
    EN_MND: "1 måned",
    TRE_MND: "3 måneder",
    SEKS_MND: "6 måneder",
    I_AAR: "i år",
    ETT_AAR: "1 år",
    VELG: "6 måneder fram til",
}

# Merkene paa aksen: dagene for 1 uke, foerste dag serien har i hver uke for
# 1 mnd (ogsaa den foerste, avkortede uka), og maanedene ellers. Med flere
# enn 8 maaneder, som 1 aar og I aar fra september, faar annenhver maaned
# navn, saa navnene faar plass (graf.aksemerker).
DAGER, UKER, MAANEDSNAVN, ANNENHVER_MAANED = "dager", "uker", "maaneder", "annenhver"
AKSEMERKER = {EN_UKE: DAGER, EN_MND: UKER, ETT_AAR: ANNENHVER_MAANED}

UKEDAGER = ("Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag")

# Lengste del av en feil verdi som gjentas i beskjeden.
_LENGSTE_I_BESKJED = 20

# Bare ÅÅÅÅ-MM-DD med sifrene 0-9. date.fromisoformat godtar ogsaa
# ukedatoer som 2026-W41-5.
_DATO = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def foerste_knapp(siste: date, idag: date) -> str:
    """Navnet paa den foerste knappen (designregler.md §2): «I dag» naar
    siste boersdag i dataene er i dag, «I går» naar den var i gaar, og ellers
    ukedagen, som «Fredag» paa en mandag."""
    if siste == idag:
        return "I dag"
    if siste == idag - timedelta(days=1):
        return "I går"
    return UKEDAGER[siste.weekday()]


def knappene(siste: date, idag: date) -> tuple[tuple[str, str], ...]:
    """(kode, navn) for knappene foran «Velg dag», i rekkefoelgen i §2."""
    return ((SISTE, foerste_knapp(siste, idag)),) + tuple((kode, NAVN[kode]) for kode in PERIODENE[1:-1])


@dataclass(frozen=True)
class Valg:
    """Perioden i adressen, lest. dag er dagen for «Velg dag». beskjed er en
    kort tekst naar adressen hadde en feil, og da er perioden 6 mnd."""

    periode: str
    dag: date | None = None
    beskjed: str | None = None


def _gjentatt(verdi: str) -> str:
    verdi = " ".join(verdi.split())
    return verdi if len(verdi) <= _LENGSTE_I_BESKJED else verdi[:_LENGSTE_I_BESKJED] + "…"


# Story 8.17a: siden som leser adressen. Kursgrafen aapner med 6 mnd, og
# oversikten med siste boersdag (designregler.md §2). Tekstene sier hva siden
# viser naar adressen hadde en feil, og naar «Velg dag» mangler dagen.
GRAFEN = "grafen"
OVERSIKTEN = "oversikten"
_STANDARD = {GRAFEN: SEKS_MND, OVERSIKTEN: SISTE}
_VISER = {GRAFEN: "grafen viser 6 mnd", OVERSIKTEN: "oversikten viser siste børsdag"}
_VELG_TEKST = {
    GRAFEN: "Velg en dag i feltet, så viser grafen 6 mnd fram til den.",
    OVERSIKTEN: "Velg en dag i feltet, så viser oversikten den dagen.",
}


def les_valg(
    periode: str | None, dag: str | None, foerste: date, idag: date, siste: date | None = None, side: str = GRAFEN
) -> Valg:
    """Perioden og dagen fra adressen, eller standardperioden med en kort
    beskjed: 6 mnd for grafen og siste boersdag for oversikten (8.17a).

    foerste og siste er foerste og siste dag i kursserien. En dag i adressen
    gir «Velg dag», ogsaa uten periode. En feil gir aldri en feilside: ukjent
    periode, en dato som ikke kan leses, en dato fram i tid, etter siste dag
    i serien eller paa eller foer seriens foerste dag gir 6 mnd og en
    beskjed. Seriens foerste dag ville gitt en graf med ett punkt
    (gjennomgangen, BH3), og en dag etter siste dag en graf som slutter foer
    dagen (BH1). Datoen i beskjeden er paa formen 09.10.2026."""
    standard, viser = _STANDARD[side], _VISER[side]
    if dag:
        try:
            if not _DATO.fullmatch(dag):
                raise ValueError(dag)
            valgt = date.fromisoformat(dag)
        except ValueError:
            return Valg(standard, beskjed=f"Datoen «{_gjentatt(dag)}» kunne ikke leses, så {viser}.")
        if valgt > idag:
            return Valg(standard, beskjed=f"{valgt:%d.%m.%Y} er fram i tid, så {viser}.")
        if valgt <= foerste:
            return Valg(
                standard,
                beskjed=f"Kursserien begynner {foerste:%d.%m.%Y}, så {viser}.",
            )
        if siste is not None and valgt > siste:
            return Valg(standard, beskjed=f"Kursserien slutter {siste:%d.%m.%Y}, så {viser}.")
        return Valg(VELG, dag=valgt)
    if not periode:
        return Valg(standard)
    if periode == VELG:
        return Valg(standard, beskjed=_VELG_TEKST[side])
    if periode in PERIODENE:
        return Valg(periode)
    return Valg(standard, beskjed=f"Perioden «{_gjentatt(periode)}» finnes ikke, så {viser}.")
