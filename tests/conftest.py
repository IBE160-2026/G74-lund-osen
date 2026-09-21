"""Felles oppsett for alle tester.

Sperrer utgaaende nettverk under hele testkjoeringen.

Grunnen er konkret, ikke prinsipiell: EODHD-kvoten er 20 kall i doegnet. En
test som ved et uhell kaller et ekte endepunkt, kan spise en dags maaling -
og i CI ville den gjort det paa hver eneste push. README lover at testene
ikke bruker API-kall. Denne fila gjoer loeftet til noe som haandheves i stedet
for noe vi husker paa.

Sperren ligger paa socket.connect, altsaa under requests og under alt annet
som maatte finne paa aa aapne en forbindelse. Loopback slippes gjennom, fordi
den ikke kan naa en leverandoer.
"""

import socket

import pytest

_ekte_connect = socket.socket.connect
_ekte_connect_ex = socket.socket.connect_ex

LOOPBACK = {"127.0.0.1", "::1", "localhost"}


class NettverkISTest(AssertionError):
    """Reises naar en test proever aa naa noe utenfor maskinen."""


def _er_loopback(adresse) -> bool:
    if isinstance(adresse, tuple) and adresse:
        return str(adresse[0]) in LOOPBACK
    return False


def _sperret(navn, ekte):
    def erstatning(self, adresse, *resten):
        if _er_loopback(adresse):
            return ekte(self, adresse, *resten)
        raise NettverkISTest(
            f"socket.{navn} mot {adresse!r} ble blokkert.\n"
            "Testene skal ikke bruke nett. Injiser hentefunksjonen i stedet - "
            "se hent_universet i src/fetch_prices.py."
        )

    return erstatning


@pytest.fixture(autouse=True)
def ingen_nettverk(monkeypatch):
    """Autouse: gjelder hver test, ogsaa de som ikke vet at de finnes."""
    monkeypatch.setattr(socket.socket, "connect", _sperret("connect", _ekte_connect))
    monkeypatch.setattr(
        socket.socket, "connect_ex", _sperret("connect_ex", _ekte_connect_ex)
    )
