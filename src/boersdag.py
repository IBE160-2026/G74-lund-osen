"""Boersdagene paa Oslo Boers - story 1.6, punkt 3 i prd.md §8, AD-20.

Ren logikk. Ingen API-kall, ingen filer. Dagen kommer inn som argument, og
funksjonen leser aldri klokka selv, saa testene ikke avhenger av dagen de
kjoeres.

Inneveerende boersdag er siste boersdag paa eller foer dagens dato i
Europe/Oslo. En boersdag er mandag-fredag som ikke staar i STENGT. Halve
handelsdager er boersdager. Dagens dato i Oslo regnes av norsk_dato, fra et
tidspunkt med sone. Brukes av Vurderingslager (FR-408, AD-7), og
senere av de tre tilstandene (1.7, FR-409) og kontrollen mot forventet
boersdag (2.3, FR-402).
"""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

OSLO = ZoneInfo("Europe/Oslo")

# Aarene STENGT dekker. Et nytt aar legges til, og de gamle blir staaende:
# 2027-01-01 er stengt og maa slaa opp 2026-12-31 og 2026-12-30.
DEKKEDE_AAR = frozenset({2026})

# Dagene Oslo Boers er stengt i 2026, alle hverdager. Foert for haand fra
# Euronexts egen kalender, se docs/kilder-og-rettigheter.md, seksjonen
# Handelskalenderen. 2026-04-01 er halv handelsdag og regnes som boersdag, saa
# den staar ikke her. Dagene for 2027 foeres inn naar Euronext publiserer dem,
# og 2027 legges til i DEKKEDE_AAR samtidig.
STENGT = frozenset({
    date(2026, 1, 1),
    date(2026, 4, 2),
    date(2026, 4, 3),
    date(2026, 4, 6),
    date(2026, 5, 1),
    date(2026, 5, 14),
    date(2026, 5, 25),
    date(2026, 12, 24),
    date(2026, 12, 25),
    date(2026, 12, 31),
})


class UtenforKalenderen(ValueError):
    """Funksjonen maatte slaa opp en dag lista ikke dekker.

    Den gjetter ikke: en helligdag i 2027 som ikke er foert inn, ville ellers
    blitt regnet som boersdag uten at noen merket det.
    """


def innevaerende_boersdag(dag: date) -> date:
    """Siste boersdag paa eller foer dag.

    Reiser UtenforKalenderen bare naar en dag funksjonen faktisk maa slaa
    opp, ligger utenfor DEKKEDE_AAR. 2026-01-02 er boersdag og gis tilbake, mens
    2026-01-01 er stengt og krever 2025-12-31.
    """
    if not isinstance(dag, date) or isinstance(dag, datetime):
        raise TypeError(f"dag maa vaere datetime.date, fikk {dag!r}")
    oppslag = dag
    while True:
        if oppslag.year not in DEKKEDE_AAR:
            hva = dag.isoformat()
            if oppslag != dag:
                hva += f" krever {oppslag.isoformat()}, og"
            else:
                hva += ":"
            raise UtenforKalenderen(
                f"{hva} lista over stengte dager dekker bare {sorted(DEKKEDE_AAR)}"
            )
        if oppslag.weekday() < 5 and oppslag not in STENGT:
            return oppslag
        oppslag -= timedelta(days=1)


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
