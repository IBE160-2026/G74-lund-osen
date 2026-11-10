"""Justeringsdagene, regnet av kursserien alene (story 2.6 og 8.14, FR-407).

Kilden regner de eldre kursene om bakover når en aksje justeres, for
eksempel ved et utbytte eller en splitt. Den dagen spriker endringen i
sluttkursen og endringen i den justerte kursen, mens de er like ellers
(begrunnelser.md §11). Metoden ser justeringer, ikke hva som ble justert, så
sidene sier «justeringsdag». Ingen melding og ingen ekstra kall: bare de to
kolonnene i kurs (AD-5, AD-19). Den er etterpåklok: en dag kan bare merkes
når den har en rad før seg.
"""

from datetime import date

from kursdata import Kursrad

# Prosentpoeng mellom endringen i sluttkursen og i den justerte kursen.
# Målingen 21.09 (begrunnelser.md §11) fant det samme antallet, 38, fra
# 0,05 til 0,5 pp. 0,1 pp ligger inne i det spennet, med margin til støyen
# under 0,05 (én hendelse til ved 0,01).
TERSKEL_PP = 0.1


def aaret_foer(til: date) -> date:
    """«Det siste året» (FR-407, story 8.14) begynner på samme dato året
    før, som «1 år» i kursgrafen (perioder.startdag). Gjennomgangen (ECH1,
    BH11): her sto 365 dager, som mistet den første dagen i grafen og en dag
    over 29. februar. 29. februar blir 28. februar året før."""
    try:
        return til.replace(year=til.year - 1)
    except ValueError:
        return til.replace(year=til.year - 1, day=28)


def _endring(fra: float, til: float) -> float:
    """Endringen i prosent. Kursrad godtar bare kurser over null."""
    return (til - fra) / fra * 100


def er_justeringsdag(forrige: Kursrad, rad: Kursrad) -> bool:
    """Om rad er en justeringsdag: endringen fra forrige rad i sluttkursen og
    i den justerte kursen spriker mer enn TERSKEL_PP."""
    ujustert = _endring(forrige.slutt, rad.slutt)
    justert = _endring(forrige.justert_slutt, rad.justert_slutt)
    return abs(ujustert - justert) > TERSKEL_PP


def justeringsdager(serie: list[Kursrad], til: date | None = None) -> tuple[date, ...]:
    """Justeringsdagene i serien, eldst først. Med til bare det siste året,
    fra aaret_foer(til) til og med til. Serien er sortert på dato, som
    lagrene gir den."""
    dager = tuple(rad.dato for forrige, rad in zip(serie, serie[1:], strict=False) if er_justeringsdag(forrige, rad))
    if til is None:
        return dager
    return tuple(d for d in dager if aaret_foer(til) <= d <= til)
