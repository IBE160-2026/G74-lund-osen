"""Tester for datalaget. Ingen nettverk, ingen API-kall.

Filtestene skriver til tmp_path, ikke til data/.
"""

import json
from datetime import date

import pytest

from kursdata import (
    AKSJEUNIVERS,
    KURSPREFIKS,
    SnapshotKilde,
    nyeste_snapshot,
)


def test_universet_har_femten_aksjer():
    assert len(AKSJEUNIVERS) == 15


def test_universet_dekker_minst_atte_sektorer():
    """Kriteriet fra PRD-en, kontrollert i kode i stedet for i en tabell."""
    sektorer = {aksje.sektor for aksje in AKSJEUNIVERS}
    assert len(sektorer) >= 8


def test_symbol_og_ticker_holdes_fra_hverandre():
    """issuerSign-formen og EODHD-formen er ikke den samme strengen."""
    for aksje in AKSJEUNIVERS:
        assert aksje.ticker == f"{aksje.symbol}.OL"
        assert not aksje.symbol.endswith(".OL")


def test_symbolene_er_unike():
    symboler = [aksje.symbol for aksje in AKSJEUNIVERS]
    assert len(set(symboler)) == len(symboler)


def test_snapshotkilde_leser_formatet_signaltesten_skrev(tmp_path):
    fil = tmp_path / "signaltest-raa-2026-09-21.json"
    fil.write_text(
        json.dumps(
            {
                "hentet": "2026-09-21T15:40:00+00:00",
                "serier": {"DNB": [{"date": "2026-09-18", "close": 250.0}]},
            }
        ),
        encoding="utf-8",
    )

    kilde = SnapshotKilde.fra_fil(fil)

    assert kilde.tidsstempel() == "2026-09-21T15:40:00+00:00"
    assert kilde.serie("DNB")[0]["close"] == 250.0
    assert kilde.serie("MANGLER") == []


def test_snapshotkilde_taaler_fil_uten_serier(tmp_path):
    fil = tmp_path / "tom.json"
    fil.write_text(json.dumps({"hentet": "2026-09-21"}), encoding="utf-8")

    kilde = SnapshotKilde.fra_fil(fil)
    assert kilde.serie("EQNR") == []


def test_nyeste_snapshot_velger_siste_dato(tmp_path):
    for navn in ("signaltest-raa-2026-09-19.json", "signaltest-raa-2026-09-21.json"):
        (tmp_path / navn).write_text("{}", encoding="utf-8")
    (tmp_path / "noe-annet.json").write_text("{}", encoding="utf-8")

    assert nyeste_snapshot(tmp_path).name == "signaltest-raa-2026-09-21.json"


def test_nyeste_snapshot_er_none_naar_katalogen_er_tom(tmp_path):
    assert nyeste_snapshot(tmp_path) is None


def test_nyeste_snapshot_lar_ikke_prefikset_slaa_datoen(tmp_path):
    """Eldre fil med prefiks som sorterer sist, skal fortsatt tape.

    "volumsjekk-" er alfabetisk siste prefiks i data/ og to dager eldre enn
    kursfila. Sorteres navnet foer datoen, vinner den.
    """
    (tmp_path / "kurser-raa-2026-09-22.json").write_text("{}", encoding="utf-8")
    (tmp_path / "volumsjekk-raa-2026-09-20.json").write_text("{}", encoding="utf-8")

    assert nyeste_snapshot(tmp_path).name == "kurser-raa-2026-09-22.json"


def test_nyeste_snapshot_velger_kursfila_ved_lik_dato(tmp_path):
    """Selve tiebreaket: samme dato, ulikt prefiks.

    Dette er tilfellet den gamle `max` over (dato, sti) tok feil. Ved lik dato
    falt den tilbake paa stien, og "signaltest-" vant fordi s kommer etter k.
    """
    (tmp_path / "kurser-raa-2026-09-22.json").write_text("{}", encoding="utf-8")
    (tmp_path / "signaltest-raa-2026-09-22.json").write_text("{}", encoding="utf-8")

    assert nyeste_snapshot(tmp_path).name == "kurser-raa-2026-09-22.json"


def test_nyeste_snapshot_ved_lik_dato_uten_kursfil_er_forutsigbar(tmp_path):
    """Uten kursfil avgjoer alfabetet - men det skal svare likt hver gang.

    Regelen er skrevet ned nettopp fordi katalogrekkefoelge ellers kunne
    avgjort det, og da ville feilen vaert usynlig i en test som denne.
    """
    for navn in ("signaltest-raa-2026-09-22.json", "nyhetstest-raa-2026-09-22.json"):
        (tmp_path / navn).write_text("{}", encoding="utf-8")

    assert nyeste_snapshot(tmp_path).name == "nyhetstest-raa-2026-09-22.json"


def test_filnavn_og_nyeste_snapshot_deler_prefiks():
    """De to maa ikke kunne gli fra hverandre.

    nyeste_snapshot lar KURSPREFIKS vinne ved lik dato. Skriver fetch_prices
    et annet prefiks, taper dagens kurser mot et gammelt eksperiment.
    """
    import fetch_prices

    assert fetch_prices.filnavn(date(2026, 9, 22)).startswith(f"{KURSPREFIKS}-raa-")


@pytest.mark.parametrize("aksje", AKSJEUNIVERS, ids=lambda a: a.symbol)
def test_hver_aksje_har_navn_og_sektor(aksje):
    assert aksje.navn.strip()
    assert aksje.sektor.strip()
