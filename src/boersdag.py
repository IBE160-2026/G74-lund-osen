"""Boersdagene paa Oslo Boers - story 1.6, punkt 3 i prd.md §8, AD-20.

Ren logikk. Ingen API-kall, ingen filer. Dagen kommer inn som argument, og
funksjonen leser aldri klokka selv, saa testene ikke avhenger av dagen de
kjoeres.

Inneveerende boersdag er siste boersdag paa eller foer dagens dato i
Europe/Oslo. En boersdag er mandag-fredag som ikke staar i stengte_dager for
aaret. Halve handelsdager er boersdager. Dagens dato i Oslo regnes av
norsk_dato, fra et tidspunkt med sone. er_boersdag sier om en gitt dag var
boersdag.
Brukes av Vurderingslager (FR-408, AD-7) og de tre tilstandene i tilstand.py
(1.7, FR-409), og senere av kontrollen mot forventet boersdag (2.3, FR-402).

Story 2.16 (gruppens svar 07.11 kl. 11:05): de stengte hverdagene regnes ut
for hvert aar etter reglene Oslo Boers foelger, med paasken regnet ut, i
stedet for en liste foert for haand per aar. Listene fra Euronext for 2026 og
2027 (docs/kilder-og-rettigheter.md, Handelskalenderen) er tester regelen maa
stemme med.
"""

from datetime import date, datetime, time, timedelta
from functools import cache
from zoneinfo import ZoneInfo

OSLO = ZoneInfo("Europe/Oslo")

# Story 8.19: grensen for hentingen staar her, saa webserveren kan si naar
# nye kurser tidligst kan hentes uten aa importere fetch_prices, som laster
# KI-laget (AD-10). fetch_prices importerer den herfra, og navnet
# fetch_prices.TIDSGRENSE gjelder som foer. Kl. 22:00 fra 20.10 (story 2.3,
# gruppens svar 19.10 kl. 22:19).
TIDSGRENSE = time(22, 0)

# Foerste aar kalenderen dekker, og den dekker hvert aar etter. 2025 er ikke
# med (gruppens svar 30.10 kl. 10:45 under 8.17: «Børskalenderen får ikke
# 2025»), og det staar til gruppen har svart paa spoersmaal 1 i
# spesifikasjonen for 2.16. Leses fra modulen naar det trengs, saa en test
# kan bytte det ut.
FOERSTE_AAR = 2026


class UtenforKalenderen(ValueError):
    """Funksjonen maatte slaa opp en dag foer FOERSTE_AAR.

    Den gjetter ikke: reglene er ikke sjekket for aarene foer, og en
    helligdag der ville ellers blitt regnet som boersdag uten at noen merket
    det.
    """


def dekker(aar: int) -> bool:
    """Om kalenderen dekker aar: FOERSTE_AAR og hvert aar etter."""
    return aar >= FOERSTE_AAR


def paaskedag(aar: int) -> date:
    """1. paaskedag i den gregorianske kalenderen (den anonyme algoritmen,
    ogsaa kalt Meeus/Jones/Butcher)."""
    a = aar % 19
    b, c = divmod(aar, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    maaned, dag = divmod(h + l - 7 * m + 114, 31)
    return date(aar, maaned, dag + 1)


def stengte_dager(aar: int) -> frozenset[date]:
    """Hverdagene Oslo Boers er stengt i aar - story 2.16.

    Reglene fra gruppens svar 07.11 kl. 11:05: 1. januar, skjaertorsdag,
    langfredag, 2. paaskedag, 1. mai, 17. mai, Kristi himmelfartsdag,
    2. pinsedag, julaften, 1. og 2. juledag og nyttaarsaften. En dag som
    faller paa en helg, er ikke med, fordi helgen ikke er boersdag uansett.
    Halve handelsdager, som onsdagen foer skjaertorsdag, er boersdager og
    staar ikke her. Reiser UtenforKalenderen for et aar foer FOERSTE_AAR.
    """
    if not dekker(aar):
        raise UtenforKalenderen(f"{aar}: børskalenderen begynner i {FOERSTE_AAR}")
    return _regn_ut(aar)


@cache
def _regn_ut(aar: int) -> frozenset[date]:
    """Dagene etter reglene, uten grensen. Grensen sjekkes foer cachen, saa
    et flyttet FOERSTE_AAR gjelder ogsaa et aar som er regnet ut foer
    (gjennomgangen, BH7 og ECH3)."""
    paaske = paaskedag(aar)
    dager = {
        date(aar, 1, 1),
        paaske - timedelta(days=3),  # skjaertorsdag
        paaske - timedelta(days=2),  # langfredag
        paaske + timedelta(days=1),  # 2. paaskedag
        date(aar, 5, 1),
        date(aar, 5, 17),
        paaske + timedelta(days=39),  # Kristi himmelfartsdag
        paaske + timedelta(days=50),  # 2. pinsedag
        date(aar, 12, 24),
        date(aar, 12, 25),
        date(aar, 12, 26),
        date(aar, 12, 31),
    }
    return frozenset(dag for dag in dager if dag.weekday() < 5)


def _sjekk_dag(dag) -> None:
    if not isinstance(dag, date) or isinstance(dag, datetime):
        raise TypeError(f"dag maa vaere datetime.date, fikk {dag!r}")


def innevaerende_boersdag(dag: date) -> date:
    """Siste boersdag paa eller foer dag.

    Reiser UtenforKalenderen bare naar en dag funksjonen faktisk maa slaa
    opp, ligger foer FOERSTE_AAR. 2026-01-02 er boersdag og gis tilbake, mens
    2026-01-01 er stengt og krever 2025-12-31.
    """
    _sjekk_dag(dag)
    oppslag = dag
    while True:
        if not dekker(oppslag.year):
            hva = dag.isoformat()
            if oppslag != dag:
                hva += f" krever {oppslag.isoformat()}, og"
            else:
                hva += ":"
            raise UtenforKalenderen(f"{hva} børskalenderen begynner i {FOERSTE_AAR}")
        if oppslag.weekday() < 5 and oppslag not in stengte_dager(oppslag.year):
            return oppslag
        oppslag -= timedelta(days=1)


def forrige_boersdag(dag: date) -> date:
    """Siste boersdag foer dag, ikke paa den - story 2.3c.

    Foerste henting paa dagtid naar basen er tom, henter denne dagen: siste
    fullfoerte boersdag foer TIDSGRENSE paa en boersdag. Samme regel og samme
    feil som inneveerende_boersdag. Ikke det samme som forrige_boersdag i
    hovedindeks.py, som gir None utenfor kalenderen (gjennomgangen, VG11).
    """
    _sjekk_dag(dag)
    return innevaerende_boersdag(dag - timedelta(days=1))


def er_boersdag(dag: date) -> bool:
    """Om dag er en boersdag: mandag-fredag som ikke staar i stengte_dager.

    Story 1.7, FR-409. Samme regel som inneveerende_boersdag, ingen ny. Reiser
    UtenforKalenderen bare naar dag selv ligger foer FOERSTE_AAR, fordi ingen
    annen dag slaas opp. 2026-01-01 gir False og reiser ikke.
    """
    _sjekk_dag(dag)
    if not dekker(dag.year):
        raise UtenforKalenderen(f"{dag.isoformat()}: børskalenderen begynner i {FOERSTE_AAR}")
    return dag.weekday() < 5 and dag not in stengte_dager(dag.year)


def norsk_dato(oeyeblikk: datetime) -> date:
    """Kalenderdatoen i Oslo for et tidspunkt med sone (AD-20).

    00:30 norsk tid er dagen foer i UTC, saa datoen maa regnes her og ikke av
    tidspunktets egen sone.
    """
    if not isinstance(oeyeblikk, datetime):
        raise TypeError(f"oeyeblikk maa vaere datetime, fikk {oeyeblikk!r}")
    if oeyeblikk.tzinfo is None or oeyeblikk.utcoffset() is None:
        raise ValueError(f"oeyeblikk maa ha tidssone (AD-20), fikk {oeyeblikk!r}")
    return oeyeblikk.astimezone(OSLO).date()


# --- Story 8.19: neste henting i stripa ---------------------------------------


def neste_boersdag(dag: date) -> date:
    """Foerste boersdag etter dag. Reiser UtenforKalenderen naar kalenderen
    ikke dekker aaret den maa slaa opp (NFR-08: ingen gjetning)."""
    _sjekk_dag(dag)
    neste = dag + timedelta(days=1)
    while not er_boersdag(neste):
        neste += timedelta(days=1)
    return neste


def neste_henting(kursdag: date, naa: datetime) -> date | None:
    """Dagen nye kurser tidligst kan hentes, fra TIDSGRENSE, eller None naar
    de kan hentes naa. kursdag er den siste kursdagen i basen, den eldste
    blant aksjene i lista (spoersmaal 10, svaret 12.11 kl. 20:42), ikke
    tidspunktet for hentingen. Den sier aldri at en henting kommer, bare naar
    hentingen i fetch_prices tidligst ville faatt nye kurser: paa en
    boersdag foer TIDSGRENSE henter den ingenting, og ellers henter den
    inneverende boersdag naar den er nyere enn kursdag."""
    idag = norsk_dato(naa)
    if er_boersdag(idag) and naa.astimezone(OSLO).time() < TIDSGRENSE:
        return idag
    if innevaerende_boersdag(idag) > kursdag:
        return None
    return neste_boersdag(idag)
