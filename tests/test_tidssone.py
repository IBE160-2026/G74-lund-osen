"""Tidssonedataene finnes - AD-20.

Windows har ingen tidssonedatabase, og da reiser ZoneInfo("Europe/Oslo")
ZoneInfoNotFoundError. Proevd 24.09 foer tzdata ble lagt inn. 1.4c, 1.6 og 2.1
trenger Europe/Oslo, saa det skal feile her og ikke der.
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


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
