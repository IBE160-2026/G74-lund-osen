"""Tidssonedataene finnes - AD-20.

Windows har ingen tidssonedatabase, og da reiser ZoneInfo("Europe/Oslo")
ZoneInfoNotFoundError. Proevd 24.09 foer tzdata ble lagt inn. 1.4c, 1.6 og 2.1
trenger Europe/Oslo, saa det skal feile her og ikke der.
"""

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

SRC = Path(__file__).resolve().parent.parent / "src"

# Kall som leser maskinens lokale sone (story 2.1, svar A 29.09).
# datetime.now(timezone.utc) og astimezone(OSLO) er lov: der er sonen sagt.
LOKAL_SONE = re.compile(r"date\.today\(|datetime\.now\(\s*\)|\.astimezone\(\s*\)")


def test_europe_oslo_kan_aapnes():
    ZoneInfo("Europe/Oslo")


def test_europe_oslo_har_sommertid_og_vintertid():
    """At sonen aapnes, er ikke nok: dataene maa ogsaa gi riktig forskyvning."""
    oslo = ZoneInfo("Europe/Oslo")

    assert datetime(2026, 9, 24, 12, tzinfo=oslo).utcoffset() == timedelta(hours=2)
    assert datetime(2026, 12, 10, 12, tzinfo=oslo).utcoffset() == timedelta(hours=1)


def test_00_30_i_oslo_er_dagen_foer_i_utc():
    """Feilvinduet i 1.6 og 2.1: datoen skifter ulikt i de to sonene."""
    oslo = datetime(2026, 9, 25, 0, 30, tzinfo=ZoneInfo("Europe/Oslo"))

    assert oslo.astimezone(timezone.utc) == datetime(2026, 9, 24, 22, 30, tzinfo=timezone.utc)


def test_ingen_kode_i_src_leser_maskinens_sone():
    """Strengvakten fra story 2.1 (AD-20): ingen date.today(), ingen
    datetime.now() uten sone og ingen astimezone() uten argument i src/.

    Kjoeres ogsaa paa Windows, der TZ-testene i test_fetch_prices hoppes over.
    Ville feilet hvis kjoer regnet dagen med oeyeblikk.astimezone().date() (M6).
    """
    filer = sorted(SRC.rglob("*.py"))
    assert filer, f"fant ingen .py-filer under {SRC}"
    treff = [
        f"{fil.relative_to(SRC.parent)}:{nr}: {linje.strip()}"
        for fil in filer
        for nr, linje in enumerate(fil.read_text(encoding="utf-8").splitlines(), 1)
        if LOKAL_SONE.search(linje)
    ]
    assert treff == [], "leser maskinens sone:\n" + "\n".join(treff)


def test_strengvakten_kjenner_igjen_formene():
    """Vakten maa treffe det den skal, og slippe det som er lov."""
    for forbudt in ("date.today()", "datetime.now()", "datetime.now( )", "t.astimezone()"):
        assert LOKAL_SONE.search(forbudt), forbudt
    for lov in ("datetime.now(timezone.utc)", "t.astimezone(OSLO)", "t.astimezone(timezone.utc)"):
        assert not LOKAL_SONE.search(lov), lov
