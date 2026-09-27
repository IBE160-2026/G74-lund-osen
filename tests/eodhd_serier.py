"""Seriene fra EODHD som ikke kan leses - story 1.8.

Testene for leseren (test_snapshotleser.py) og hentingen (test_fetch_prices.py)
tar seriene herfra, saa de to ikke kan faa hver sin regel uten at en test
feiler. Hver serie her avvises av serie_fra_eodhd. Den tomme serien er med
vilje ikke med: den gir «tomt svar» i hentingen og proeves for seg.

Tilfellene er de test_snapshotleser.py proevde foer 1.8, de fem fra proeven
27.09 (G1 i kodegjennomgangen av Epic 1) og de fem svarene TestSvarMedFeilForm
proevde i story 2.0. Ingen tall her er kursdata fra en kilde.
"""


def rad(dato: str = "2026-09-21", close=100.0, adjusted_close=98.0, volume=1000) -> dict:
    return {"date": dato, "open": 99.0, "high": 101.0, "low": 97.0,
            "close": close, "adjusted_close": adjusted_close, "volume": volume}


def _uten(felt: str) -> dict:
    r = rad()
    del r[felt]
    return r


def _med_foran(daarlig) -> list:
    """En gyldig rad foer den daarlige, saa det ikke er foerste rad som avgjoer."""
    return [rad("2026-09-18"), daarlig]


# (id, serie). Rekkefoelgen er den id-ene faar i testrapporten.
AVVISTE_SERIER: list[tuple[str, object]] = [
    # Fra test_snapshotleser.py foer 1.8
    ("mangler-adjusted_close", _med_foran(_uten("adjusted_close"))),
    ("close-nan", _med_foran(rad(close=float("nan")))),
    ("justert-None", _med_foran(rad(adjusted_close=None))),
    ("close-tekst", _med_foran(rad(close="100"))),
    ("close-0", _med_foran(rad(close=0))),
    ("volum-negativt", _med_foran(rad(volume=-1))),
    ("close-for-stort", _med_foran(rad(close=10**400))),
    ("dato-uten-nuller", _med_foran(rad(dato="2026-9-1"))),
    ("dato-uten-streker", _med_foran(rad(dato="20260921"))),
    ("dato-ukedato", _med_foran(rad(dato="2026-W39-1"))),
    ("dato-umulig", _med_foran(rad(dato="2026-09-31"))),
    ("dato-tall", _med_foran(rad(dato=20260921))),
    ("rad-liste", _med_foran([])),
    ("rad-tall", _med_foran(1)),
    ("rad-None", _med_foran(None)),
    ("dato-igjen", [rad("2026-09-21", close=100.0), rad("2026-09-21", close=101.0)]),
    ("serie-None", None),
    ("serie-tall", 1),
    ("serie-tekst", "tekst"),
    ("serie-objekt", {}),
    # Proeven 27.09 (close 0 og en dato som gaar igjen staar over)
    ("close-None", _med_foran(rad(close=None))),
    ("volum-flyttall", _med_foran(rad(volume=1000.0))),
    ("dato-2026-9-24", _med_foran(rad(dato="2026-9-24"))),
    # TestSvarMedFeilForm i story 2.0 (None staar over)
    ("rad-uten-date", [_uten("date")]),
    ("rad-bare-date", [{"date": "2026-09-22"}]),
    ("feilobjekt", {"code": 403, "message": "Forbidden"}),
    ("liste-uten-rader", ["2026-09-22"]),
]

AVVISTE_IDER = [navn for navn, _ in AVVISTE_SERIER]
AVVISTE = [serie for _, serie in AVVISTE_SERIER]
