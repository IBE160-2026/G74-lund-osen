"""Story 2.19: hoey og lav mot sluttkursen.

Gruppens svar 19.11 kl. 18:47 paa spoersmaal 2 i 2.10 (ECH3), ført i
docs/ai-prompts/2026-11-19.md. En rad der lav er over sluttkursen, eller hoey
er under den, lagres uten hoey og lav, som en rad som mangler dem. Hentingen
stopper ikke, og den sier hvor mange rader det gjaldt. Ville feilet hvis en
slik rad ble lagret med hoey og lav, eller stoppet hentingen.

Alle basene er testbaser i tmp_path (regel 22). Ingen tall her er kursdata
fra en kilde.
"""

import math
from datetime import date, datetime, timedelta, timezone

import pytest

import eodhd
import fetch_prices as fp
from eodhd import kursrad_fra_eodhd
from indeksdata import HOVEDINDEKS
from kursdata import AKSJEUNIVERS, UgyldigKursrad
from lagring_sqlite import aapne_base

HENTET = datetime(2026, 9, 22, 20, 0, tzinfo=timezone.utc)
TIRSDAG = date(2026, 9, 22)
MERKNAD = "uten høy og lav (passet ikke med sluttkursen)"


def _rad(**felt) -> dict:
    rad = {"date": "2026-09-21", "close": 100.0, "adjusted_close": 98.0, "volume": 1000, "high": 101.5, "low": 97.25}
    rad.update(felt)
    return rad


def _uten(felt: str) -> dict:
    rad = _rad()
    del rad[felt]
    return rad


class TestAdapteren:
    @pytest.mark.parametrize(
        ("high", "low"),
        [(101.5, 100.5), (99.5, 97.25), (99.0, 98.0), (102.0, 101.0)],
        ids=["lav-over", "hoey-under", "begge-under", "begge-over"],
    )
    def test_utenfor_sluttkursen_gir_ingen_av_dem(self, high, low):
        """Kontrollen i storyen: ville feilet hvis raden ble lagret med dem."""
        rad = kursrad_fra_eodhd(_rad(high=high, low=low))
        assert (rad.hoey, rad.lav) == (None, None)
        assert (rad.slutt, rad.justert_slutt, rad.volum) == (100.0, 98.0, 1000)

    @pytest.mark.parametrize(("high", "low"), [(100.0, 97.25), (101.5, 100.0), (100.0, 100.0), (100, 99)])
    def test_lik_sluttkursen_beholdes(self, high, low):
        rad = kursrad_fra_eodhd(_rad(high=high, low=low))
        assert (rad.hoey, rad.lav) == (float(high), float(low))

    def test_innenfor_beholdes(self):
        rad = kursrad_fra_eodhd(_rad())
        assert (rad.hoey, rad.lav) == (101.5, 97.25)

    @pytest.mark.parametrize(
        "rad",
        [
            _rad(high=99.0, low=None),
            {k: v for k, v in _rad(high=99.0).items() if k != "low"},
            _rad(high="NA", low=101.0),
            {k: v for k, v in _rad(low=101.0).items() if k != "high"},
        ],
        ids=["hoey-under-lav-null", "hoey-under-lav-mangler", "lav-over-hoey-tekst", "lav-over-hoey-mangler"],
    )
    def test_bare_en_av_dem_paa_feil_side_gir_ingen_av_dem(self, rad):
        """Svaret: «lagres uten høy og lav», også når bare én av dem finnes."""
        assert (kursrad_fra_eodhd(rad).hoey, kursrad_fra_eodhd(rad).lav) == (None, None)

    @pytest.mark.parametrize("felt", ["high", "low"])
    def test_bare_en_av_dem_paa_riktig_side_beholdes(self, felt):
        rad = kursrad_fra_eodhd(_uten("low" if felt == "high" else "high"))
        assert (rad.hoey, rad.lav) == ((101.5, None) if felt == "high" else (None, 97.25))

    def test_sluttkursen_er_close_og_ikke_den_justerte(self):
        """Sluttkursen er close, som gir slutt i Kursrad. Ville feilet hvis
        sjekken brukte adjusted_close."""
        rad = kursrad_fra_eodhd(_rad(close=100.0, adjusted_close=80.0))
        assert (rad.hoey, rad.lav) == (101.5, 97.25)

    @pytest.mark.parametrize("close", ["100", None, math.nan, 0, True, 10**400])
    def test_en_sluttkurs_som_ikke_kan_brukes_avvises_som_foer(self, close):
        """Sjekken gjør ingenting med en close som ikke er et tall, og Kursrad
        avviser raden som før. Ville feilet med TypeError fra sammenligningen."""
        with pytest.raises(UgyldigKursrad):
            kursrad_fra_eodhd(_rad(close=close))


# (rad, om tellingen skal ta den med). Den samme regelen som adapteren.
TILFELLER = [
    (_rad(date="2026-09-14"), False),
    (_rad(date="2026-09-15", low=100.5), True),
    (_rad(date="2026-09-16", high=99.5), True),
    (_rad(date="2026-09-17", high=97.0, low=101.0), True),
    (_rad(date="2026-09-18", high=None, low=None), False),
    (_rad(date="2026-09-21", high=99.0, low="NA"), True),
    (_rad(date="2026-09-22", high=100.0, low=100.0), False),
    (_rad(date="2026-09-23", high=0, low=-1), False),
]


class TestTellingen:
    def test_teller_radene_adapteren_tok_dem_bort_fra(self):
        assert eodhd.hoey_og_lav_mot_slutt([r for r, _ in TILFELLER]) == sum(m for _, m in TILFELLER)

    @pytest.mark.parametrize(("rad", "med"), TILFELLER)
    def test_samme_regel_som_adapteren(self, rad, med):
        """En rad telles hvis og bare hvis den hadde høy eller lav som kunne
        brukes, og adapteren ga den uten begge."""
        kurs = kursrad_fra_eodhd(rad)
        brukbare = eodhd._valgfri_kurs(rad.get("high")) is not None or eodhd._valgfri_kurs(rad.get("low")) is not None
        assert (brukbare and (kurs.hoey, kurs.lav) == (None, None)) == med
        assert eodhd.hoey_og_lav_mot_slutt([rad]) == int(med)

    def test_en_tom_serie_gir_null(self):
        assert eodhd.hoey_og_lav_mot_slutt([]) == 0


def _serie(siste: date, utenfor: set[int], dager: int = 60) -> list[dict]:
    """En serie hentingen godtar. Radene med nummer i utenfor har lav over
    sluttkursen; de andre har høy og lav rundt den."""
    rader = []
    for i in range(dager):
        slutt = 100.0 + i
        rader.append(
            {
                "date": (siste - timedelta(days=dager - 1 - i)).isoformat(),
                "close": slutt,
                "adjusted_close": slutt,
                "volume": 1000,
                "high": slutt + 1.0,
                "low": slutt + 0.5 if i in utenfor else slutt - 1.0,
            }
        )
    return rader


class TestHentingen:
    def test_hentingen_stopper_ikke_og_sier_hvor_mange(self, tmp_path):
        """Kontrollen i storyen: alle aksjene og hovedindeksen lagres, radene
        utenfor sluttkursen uten høy og lav, og linja for symbolet sier hvor
        mange det gjaldt. Like mange kall som før."""
        raa, base = tmp_path / "data" / "raa", tmp_path / "data" / "db" / "ose.db"
        # Hver andre aksje har hver tredje rad utenfor (20 av 60), de andre ingen.
        utenfor = {a.ticker: set(range(0, 60, 3)) if i % 2 == 0 else set() for i, a in enumerate(AKSJEUNIVERS)}
        utenfor[HOVEDINDEKS.ticker] = {59}
        kall = []

        def hent(ticker, *_):
            kall.append(ticker)
            return _serie(TIRSDAG, utenfor[ticker])

        utskrift = []
        fp.kjoer(
            raa,
            base,
            HENTET,
            "FALSK-NOEKKEL-123456",
            hent,
            utskrift.append,
            les_kvote=lambda _: {
                "apiRequests": 0,
                "apiRequestsDate": "2026-01-01",
                "dailyRateLimit": 20,
                "extraLimit": 0,
            },
        )
        assert len(kall) == len(AKSJEUNIVERS) + 1
        linjer = "\n".join(utskrift).splitlines()
        t = aapne_base(base)
        try:
            tall = {
                s: (n, h, lv)
                for s, n, h, lv in t.execute(
                    "SELECT symbol, count(*), count(hoey), count(lav) FROM kurs GROUP BY symbol"
                )
            }
            indeksen = t.execute(
                "SELECT count(*), count(hoey), count(lav) FROM indeks WHERE symbol = ?", (HOVEDINDEKS.symbol,)
            ).fetchone()
            vurderinger = t.execute("SELECT count(*) FROM vurdering WHERE regnet = 'kveld'").fetchone()[0]
        finally:
            t.close()
        assert set(tall) == {a.symbol for a in AKSJEUNIVERS}, utskrift
        for aksje in AKSJEUNIVERS:
            antall = len(utenfor[aksje.ticker])
            assert tall[aksje.symbol] == (60, 60 - antall, 60 - antall), aksje.symbol
            linja = [linje for linje in linjer if linje.startswith(f"  {aksje.symbol}: 60 dager")]
            assert len(linja) == 1, (aksje.symbol, linjer)
            if antall:
                assert f", {antall} rader {MERKNAD}" in linja[0], linja
            else:
                assert "høy og lav" not in linja[0], linja
        # Indeksen lagres bare for børsdagene (bare_boersdager), og rad 59 er
        # tirsdagen, en børsdag.
        assert indeksen[0] > 0 and indeksen[1:] == (indeksen[0] - 1, indeksen[0] - 1), indeksen
        navn = f"  {HOVEDINDEKS.symbol} ({HOVEDINDEKS.navn.lower()}): 60 dager"
        linja = [linje for linje in linjer if linje.startswith(navn)]
        assert len(linja) == 1 and linja[0].endswith(f", 1 rad {MERKNAD}"), linjer
        assert vurderinger == len(AKSJEUNIVERS)
