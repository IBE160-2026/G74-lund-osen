"""Felles oppsett for alle tester.

Sperrer utgaaende nettverk inne i hver test, og peker stiene til
data/raa/ og data/db/ mot tmp_path (story 2.1b, nederst).

Rettet 2026-10-03 (D10 i kontrollen 26.09): her sto "under hele
testkjoeringen". Sperren er en autouse-fixture med funksjonsscope, saa den
gjelder inne i testfunksjonene, ikke i fixturer med module-scope eller under
innsamlingen. Story 4.0 utvider den til hele testkjoeringen.

Story 4.0 (2026-10-15): socket-sperren settes naa i pytest_configure og
fjernes i pytest_unconfigure, saa den gjelder hele testkjoeringen, ogsaa
fixturer med module- og session-scope og innsamlingen. Fixturen under
beholdes for proxyvariablene. Loopback slippes bare gjennom til en port som
en socket i samme prosess lytter paa (socket.socket.listen pakkes inn). Da
stoppes en proxy paa loopback uansett bibliotek, og en test kan ikke naa en
Ollama eller en annen tjeneste som kjoerer paa maskinen.

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
lyktes paa en med, stoppes her foer det skjer. Fra story 4.0 gjelder det
ogsaa gethostbyname, gethostbyname_ex og getfqdn.
"""

import socket
import urllib.request
import weakref

import pytest
import requests.utils

_ekte_connect = socket.socket.connect
_ekte_connect_ex = socket.socket.connect_ex
_ekte_getaddrinfo = socket.getaddrinfo
_ekte_gethostbyname = socket.gethostbyname
_ekte_gethostbyname_ex = socket.gethostbyname_ex
_ekte_getfqdn = socket.getfqdn
_ekte_listen = socket.socket.listen

# Socketene i denne prosessen som har kalt listen. En lukket socket teller
# ikke, saa en port som er sluppet, er sperret igjen.
_lyttere: "weakref.WeakSet[socket.socket]" = weakref.WeakSet()

LOOPBACK = {"127.0.0.1", "::1", "localhost"}

_PROXYVARIABLER = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY")


class NettverkISTest(AssertionError):
    """Reises naar en test proever aa naa noe utenfor maskinen."""


def _lytter_paa(port) -> bool:
    for lytter in list(_lyttere):
        if lytter.fileno() == -1:
            continue
        try:
            if lytter.getsockname()[1] == port:
                return True
        except OSError:
            continue
    return False


def _er_loopback(adresse) -> bool:
    """Loopback til en port en socket i samme prosess lytter paa (story 4.0)."""
    if isinstance(adresse, tuple) and len(adresse) >= 2:
        return str(adresse[0]) in LOOPBACK and _lytter_paa(adresse[1])
    return False


def _er_unix(sock) -> bool:
    """AF_UNIX gaar til en fil paa maskinen, ikke til nettet (story 4.0)."""
    familie = getattr(socket, "AF_UNIX", None)
    return familie is not None and sock.family == familie


def _blokkert(hva: str) -> NettverkISTest:
    return NettverkISTest(
        f"{hva} ble blokkert.\n"
        "Testene skal ikke bruke nett. Injiser hentefunksjonen i stedet - "
        "se hent_universet i src/fetch_prices.py."
    )


def _sperret(navn, ekte):
    def erstatning(self, adresse, *resten):
        if _er_unix(self) or _er_loopback(adresse):
            return ekte(self, adresse, *resten)
        raise _blokkert(f"socket.{navn} mot {adresse!r}")

    return erstatning


def _lytt(self, *resten):
    resultat = _ekte_listen(self, *resten)
    _lyttere.add(self)
    return resultat


def _navnet(vert):
    return vert.decode() if isinstance(vert, bytes) else vert


def _sperret_getaddrinfo(host, port, *resten, **navngitt):
    navn = _navnet(host)
    if navn is None or navn == "" or navn in LOOPBACK:
        return _ekte_getaddrinfo(host, port, *resten, **navngitt)
    raise _blokkert(f"DNS-oppslag paa {navn!r}")


def _sperret_oppslag(funksjonen, ekte):
    def erstatning(vert, *resten, **navngitt):
        if _navnet(vert) in LOOPBACK:
            return ekte(vert, *resten, **navngitt)
        raise _blokkert(f"socket.{funksjonen} paa {vert!r}")

    return erstatning


def _sperret_getfqdn(name=""):
    """getfqdn() uten navn slaar opp maskinens eget navn, saa det sperres ogsaa."""
    if _navnet(name) in LOOPBACK:
        return _ekte_getfqdn(name)
    raise _blokkert(f"socket.getfqdn paa {name!r}")


_sperren = None


def pytest_configure(config):
    """Story 4.0: socket-sperren gjelder hele testkjoeringen."""
    global _sperren
    _sperren = pytest.MonkeyPatch()
    _sperren.setattr(socket, "getaddrinfo", _sperret_getaddrinfo)
    _sperren.setattr(socket, "gethostbyname", _sperret_oppslag("gethostbyname", _ekte_gethostbyname))
    _sperren.setattr(socket, "gethostbyname_ex", _sperret_oppslag("gethostbyname_ex", _ekte_gethostbyname_ex))
    _sperren.setattr(socket, "getfqdn", _sperret_getfqdn)
    _sperren.setattr(socket.socket, "listen", _lytt)
    _sperren.setattr(socket.socket, "connect", _sperret("connect", _ekte_connect))
    _sperren.setattr(socket.socket, "connect_ex", _sperret("connect_ex", _ekte_connect_ex))


def pytest_unconfigure(config):
    global _sperren
    if _sperren is not None:
        _sperren.undo()
        _sperren = None


def _ingen_proxy():
    return {}


@pytest.fixture(autouse=True)
def ingen_nettverk(monkeypatch):
    """Autouse: gjelder hver test, ogsaa de som ikke vet at de finnes.

    Fra story 4.0 bare proxyen. Socket-sperren settes i pytest_configure.
    """
    for navn in _PROXYVARIABLER:
        monkeypatch.delenv(navn, raising=False)
        monkeypatch.delenv(navn.lower(), raising=False)
    monkeypatch.setattr(requests.utils, "getproxies", _ingen_proxy)
    monkeypatch.setattr(urllib.request, "getproxies", _ingen_proxy)


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


def _avtrykk(sti):
    import hashlib

    if not sti.exists():
        return None
    return hashlib.sha256(sti.read_bytes()).hexdigest(), sti.stat().st_mtime_ns


@pytest.fixture(autouse=True, scope="session")
def den_ekte_basen_er_uroert():
    """Regel 22 i CLAUDE.md: ingen test roerer data/db/ose.db.

    Fixturen over flytter BASE_STI, men den virker bare saa lenge koden slaar
    opp lagring_sqlite.BASE_STI naar den kalles. Denne ser paa selve fila:
    innholdet og mtime foer og etter hele kjoeringen. Finnes ikke fila, som i
    CI, er det ingenting aa sjekke. Lagt til etter gjennomgangen av 2.3 (VG4).
    """
    from pathlib import Path

    ekte = Path(__file__).resolve().parent.parent / "data" / "db" / "ose.db"
    foer = _avtrykk(ekte)
    yield
    assert _avtrykk(ekte) == foer, f"{ekte} ble endret av testkjoeringen (regel 22)"
