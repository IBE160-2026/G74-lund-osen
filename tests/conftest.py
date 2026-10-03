"""Felles oppsett for alle tester.

Sperrer utgaaende nettverk inne i hver test, og peker stiene til
data/raa/ og data/db/ mot tmp_path (story 2.1b, nederst).

Rettet 2026-10-03 (D10 i kontrollen 26.09): her sto "under hele
testkjoeringen". Sperren er en autouse-fixture med funksjonsscope, saa den
gjelder inne i testfunksjonene, ikke i fixturer med module-scope eller under
innsamlingen. Story 4.0 utvider den til hele testkjoeringen.

Grunnen er konkret, ikke prinsipiell: EODHD-kvoten er 20 kall i doegnet. En
test som ved et uhell kaller et ekte endepunkt, kan spise en dags maaling -
og i CI ville den gjort det paa hver eneste push. README lover at testene
ikke bruker API-kall. Denne fila gjoer loeftet til noe som haandheves i stedet
for noe vi husker paa.

Sperren ligger paa socket.connect, altsaa under requests og under alt annet
som maatte finne paa aa aapne en forbindelse. Loopback slippes gjennom, fordi
den ikke kan naa en leverandoer - med ett unntak: en proxy paa loopback sender
trafikken videre ut. Oppdaget 2026-09-23: med HTTPS_PROXY=http://127.0.0.1:9
gikk requests forbi sperren og stoppet foerst hos proxyen. Derfor fjernes
proxyvariablene, og getproxies i requests og urllib erstattes med en funksjon
som alltid gir {}. Det siste dekker ogsaa proxy fra Windows-registeret og en
variabel som settes inne i en test, etter at fixturen har kjoert.

DNS er sperret paa samme maate: socket.getaddrinfo avviser alle navn utenom
loopback. Testene gjoer dermed ingen navneoppslag, og sperren virker likt med
og uten nett - et oppslag som ellers ville feilet paa en maskin uten nett, og
lyktes paa en med, stoppes her foer det skjer.
"""

import socket
import urllib.request

import pytest
import requests.utils

_ekte_connect = socket.socket.connect
_ekte_connect_ex = socket.socket.connect_ex
_ekte_getaddrinfo = socket.getaddrinfo

LOOPBACK = {"127.0.0.1", "::1", "localhost"}

_PROXYVARIABLER = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY")


class NettverkISTest(AssertionError):
    """Reises naar en test proever aa naa noe utenfor maskinen."""


def _er_loopback(adresse) -> bool:
    if isinstance(adresse, tuple) and adresse:
        return str(adresse[0]) in LOOPBACK
    return False


def _blokkert(hva: str) -> NettverkISTest:
    return NettverkISTest(
        f"{hva} ble blokkert.\n"
        "Testene skal ikke bruke nett. Injiser hentefunksjonen i stedet - "
        "se hent_universet i src/fetch_prices.py."
    )


def _sperret(navn, ekte):
    def erstatning(self, adresse, *resten):
        if _er_loopback(adresse):
            return ekte(self, adresse, *resten)
        raise _blokkert(f"socket.{navn} mot {adresse!r}")

    return erstatning


def _sperret_getaddrinfo(vert, *resten, **navngitt):
    navn = vert.decode() if isinstance(vert, bytes) else vert
    if navn is None or navn == "" or navn in LOOPBACK:
        return _ekte_getaddrinfo(vert, *resten, **navngitt)
    raise _blokkert(f"DNS-oppslag paa {navn!r}")


def _ingen_proxy():
    return {}


@pytest.fixture(autouse=True)
def ingen_nettverk(monkeypatch):
    """Autouse: gjelder hver test, ogsaa de som ikke vet at de finnes."""
    for navn in _PROXYVARIABLER:
        monkeypatch.delenv(navn, raising=False)
        monkeypatch.delenv(navn.lower(), raising=False)
    monkeypatch.setattr(requests.utils, "getproxies", _ingen_proxy)
    monkeypatch.setattr(urllib.request, "getproxies", _ingen_proxy)

    monkeypatch.setattr(socket, "getaddrinfo", _sperret_getaddrinfo)
    monkeypatch.setattr(socket.socket, "connect", _sperret("connect", _ekte_connect))
    monkeypatch.setattr(
        socket.socket, "connect_ex", _sperret("connect_ex", _ekte_connect_ex)
    )


@pytest.fixture(autouse=True)
def stiene_i_tmp_path(monkeypatch, tmp_path):
    """Autouse, story 2.1b: ingen test roerer data/.

    RAA_KATALOG pekes mot tmp_path/raa og BASE_STI mot tmp_path/db/ose.db.
    Koden slaar dem opp naar den kalles (nyeste_snapshot, nyeste_leser og
    fetch_prices.main), saa dette flytter ogsaa standardstiene. Mappene lages
    ikke her, saa tmp_path er tom naar testen starter, og en test kan se at
    koden lager dem.

    DATA_KATALOG pekes i tillegg mot tmp_path/data. Ingen kode skal bruke
    den til aa lese eller skrive, men gjoer en feil det likevel, havner det
    i tmp_path og ikke i data/.
    """
    import lagring_fil
    import lagring_sqlite

    monkeypatch.setattr(lagring_fil, "DATA_KATALOG", tmp_path / "data")
    monkeypatch.setattr(lagring_fil, "RAA_KATALOG", tmp_path / "raa")
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", tmp_path / "db" / "ose.db")
