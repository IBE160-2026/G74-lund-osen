"""Felles oppsett for alle tester.

Sperrer utgaaende nettverk under hele testkjoeringen, og peker stiene til
data/raa/ og data/db/ mot tmp_path (story 2.1b, nederst).

Rettet 2026-10-03 (D10 i kontrollen 26.09): her sto "under hele
testkjoeringen". Til story 4.0 var sperren en autouse-fixture med
funksjonsscope, saa den gjaldt inne i testfunksjonene, ikke i fixturer med
module-scope eller under innsamlingen.

Story 4.0 (2026-10-15): socket-sperren settes i pytest_configure og fjernes i
pytest_unconfigure, saa den gjelder hele testkjoeringen i denne prosessen,
ogsaa fixturer med module- og session-scope og importen av testmodulene under
innsamlingen. Fixturen ingen_nettverk beholdes for proxyvariablene.

Grunnen er konkret, ikke prinsipiell: EODHD-kvoten er 20 kall i doegnet. En
test som ved et uhell kaller et ekte endepunkt, kan spise en dags maaling -
og i CI ville den gjort det paa hver eneste push. README lover at testene
ikke bruker API-kall. Denne fila gjoer loeftet til noe som haandheves i stedet
for noe vi husker paa.

Sperren ligger paa socket.connect og connect_ex, og paa sendto og sendmsg for
UDP, altsaa under requests og under alt annet som maatte finne paa aa aapne en
forbindelse. Paa Windows kobler asyncio til med ConnectEx uten aa gaa gjennom
socket.connect, saa IocpProactor.connect sperres ogsaa.

Loopback: til story 4.0 ble all loopback sluppet gjennom, fordi den ikke kan
naa en leverandoer - med ett unntak: en proxy paa loopback sender trafikken
videre ut. Oppdaget 2026-09-23: med HTTPS_PROXY=http://127.0.0.1:9 gikk
requests forbi sperren og stoppet foerst hos proxyen. Derfor fjernes
proxyvariablene, og getproxies i requests og urllib erstattes med en funksjon
som alltid gir {}. Det siste dekker ogsaa proxy fra Windows-registeret og en
variabel som settes inne i en test, etter at fixturen har kjoert. Fra story
4.0 slippes loopback bare gjennom til en port som en aapen socket i samme
prosess lytter paa, med samme familie og bundet til loopback eller alle
adresser (socket.socket.listen pakkes inn). Da stoppes en proxy paa loopback
uansett bibliotek, og en test kan ikke naa en Ollama eller en annen tjeneste
som kjoerer paa maskinen.

DNS er sperret paa samme maate: getaddrinfo, gethostbyname, gethostbyname_ex,
gethostbyaddr, getnameinfo og getfqdn avviser alt utenom loopback. Testene
gjoer dermed ingen navneoppslag, og sperren virker likt med og uten nett - et
oppslag som ellers ville feilet paa en maskin uten nett, og lyktes paa en med,
stoppes her foer det skjer. getfqdn() uten navn slaar opp maskinens eget navn
og sperres. Det rammer ogsaa standardbiblioteket der det kaller getfqdn() selv,
som email.utils.make_msgid() uten domene og smtplib. http.server bundet til
127.0.0.1 virker, fordi navnet da er loopback.

Grensene (gjennomgangen av 4.0): sperren gjelder denne prosessen. En
underprosess som en test starter, faar den ikke, og ingen test i dag starter
en underprosess som bruker nett (test_lagring_sqlite.py starter en som leser
to konstanter). Kode som kjoerer naar denne fila importeres, kjoerer foer
pytest_configure. En debugger som kobler seg til en port i en annen prosess
(for eksempel debugpy), stoppes ogsaa.
"""

import ipaddress
import socket
import sys
import threading
import urllib.request
import weakref

import pytest
import requests.utils

_ekte_connect = socket.socket.connect
_ekte_connect_ex = socket.socket.connect_ex
_ekte_sendto = socket.socket.sendto
_ekte_sendmsg = getattr(socket.socket, "sendmsg", None)
_ekte_getaddrinfo = socket.getaddrinfo
_ekte_gethostbyname = socket.gethostbyname
_ekte_gethostbyname_ex = socket.gethostbyname_ex
_ekte_gethostbyaddr = socket.gethostbyaddr
_ekte_getnameinfo = socket.getnameinfo
_ekte_listen = socket.socket.listen

# Socketene i denne prosessen som har kalt listen. En lukket socket teller
# ikke, saa en port som er sluppet, er sperret igjen. Laasen gjoer at en
# traad som lytter, ikke endrer mengden mens en annen leser den.
_lyttere: "weakref.WeakSet[socket.socket]" = weakref.WeakSet()
_lyttere_laas = threading.Lock()

LOOPBACK = {"127.0.0.1", "::1", "localhost"}
_ALLE_ADRESSER = {"0.0.0.0", "::", ""}

_PROXYVARIABLER = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY")


class NettverkISTest(AssertionError):
    """Reises naar en test proever aa naa noe utenfor maskinen."""


def _navnet(vert):
    return vert.decode() if isinstance(vert, bytes) else vert


def _er_loopbacknavn(vert) -> bool:
    """localhost (uansett store bokstaver og punktum til slutt) eller en
    loopbackadresse som 127.0.0.2 og ::1 (gjennomgangen av 4.0, BH13)."""
    navn = _navnet(vert)
    if not isinstance(navn, str):
        return False
    if navn.lower().rstrip(".") == "localhost":
        return True
    try:
        return ipaddress.ip_address(navn.split("%", 1)[0]).is_loopback
    except ValueError:
        return False


def _lytter_paa(familie, port) -> bool:
    """En aapen socket i prosessen lytter paa porten, med samme familie, og
    er bundet til loopback eller alle adresser (gjennomgangen, BH5, ECH1)."""
    with _lyttere_laas:
        lyttere = list(_lyttere)
    for lytter in lyttere:
        if lytter.fileno() == -1 or lytter.family != familie:
            continue
        if lytter.family not in (socket.AF_INET, socket.AF_INET6):
            continue
        try:
            vert, lytteport = lytter.getsockname()[:2]
        except (OSError, ValueError):
            continue
        if lytteport == port and (vert in _ALLE_ADRESSER or _er_loopbacknavn(vert)):
            return True
    return False


def _er_loopback(familie, adresse) -> bool:
    """Loopback til en port en socket i samme prosess lytter paa (story 4.0)."""
    if isinstance(adresse, tuple) and len(adresse) >= 2:
        return _er_loopbacknavn(adresse[0]) and _lytter_paa(familie, adresse[1])
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
        if _er_unix(self) or _er_loopback(self.family, adresse):
            return ekte(self, adresse, *resten)
        raise _blokkert(f"socket.{navn} mot {adresse!r}")

    return erstatning


def _sperret_sendto(self, data, *resten):
    """sendto(data, adresse) eller sendto(data, flagg, adresse)."""
    adresse = resten[-1] if resten else None
    if _er_unix(self) or _er_loopback(self.family, adresse):
        return _ekte_sendto(self, data, *resten)
    raise _blokkert(f"socket.sendto mot {adresse!r}")


def _sperret_sendmsg(self, buffere, *resten):
    """sendmsg uten adresse gaar til en tilkoblet socket, som er sjekket."""
    if len(resten) < 3 or resten[2] is None or _er_unix(self) or _er_loopback(self.family, resten[2]):
        return _ekte_sendmsg(self, buffere, *resten)
    raise _blokkert(f"socket.sendmsg mot {resten[2]!r}")


def _lytt(self, *resten):
    resultat = _ekte_listen(self, *resten)
    with _lyttere_laas:
        _lyttere.add(self)
    return resultat


def _sperret_getaddrinfo(host, port, *resten, **navngitt):
    navn = _navnet(host)
    if navn is None or navn == "" or _er_loopbacknavn(navn):
        return _ekte_getaddrinfo(host, port, *resten, **navngitt)
    raise _blokkert(f"DNS-oppslag paa {navn!r}")


def _sperret_oppslag(funksjonen, ekte):
    def erstatning(vert, *resten, **navngitt):
        if _er_loopbacknavn(vert):
            return ekte(vert, *resten, **navngitt)
        raise _blokkert(f"socket.{funksjonen} paa {vert!r}")

    return erstatning


def _sperret_getnameinfo(adresse, flagg):
    if isinstance(adresse, tuple) and adresse and _er_loopbacknavn(adresse[0]):
        return _ekte_getnameinfo(adresse, flagg)
    raise _blokkert(f"socket.getnameinfo paa {adresse!r}")


def _sperret_getfqdn(name=""):
    """getfqdn() uten navn slaar opp maskinens eget navn, saa det sperres
    ogsaa. Et loopbacknavn gir localhost uten oppslag (gjennomgangen, ECH9)."""
    if _er_loopbacknavn(name):
        return "localhost"
    raise _blokkert(f"socket.getfqdn paa {name!r}")


def _sperret_proactor_connect(ekte):
    """Windows: asyncio kobler til med ConnectEx, ikke socket.connect."""

    def erstatning(self, conn, address):
        if _er_loopback(conn.family, address):
            return ekte(self, conn, address)
        raise _blokkert(f"asyncio-tilkobling mot {address!r}")

    return erstatning


_sperren = None


def pytest_configure(config):
    """Story 4.0: socket-sperren gjelder hele testkjoeringen."""
    global _sperren
    _sperren = pytest.MonkeyPatch()
    _sperren.setattr(socket, "getaddrinfo", _sperret_getaddrinfo)
    _sperren.setattr(socket, "gethostbyname", _sperret_oppslag("gethostbyname", _ekte_gethostbyname))
    _sperren.setattr(socket, "gethostbyname_ex", _sperret_oppslag("gethostbyname_ex", _ekte_gethostbyname_ex))
    _sperren.setattr(socket, "gethostbyaddr", _sperret_oppslag("gethostbyaddr", _ekte_gethostbyaddr))
    _sperren.setattr(socket, "getnameinfo", _sperret_getnameinfo)
    _sperren.setattr(socket, "getfqdn", _sperret_getfqdn)
    _sperren.setattr(socket.socket, "listen", _lytt)
    _sperren.setattr(socket.socket, "connect", _sperret("connect", _ekte_connect))
    _sperren.setattr(socket.socket, "connect_ex", _sperret("connect_ex", _ekte_connect_ex))
    _sperren.setattr(socket.socket, "sendto", _sperret_sendto)
    if _ekte_sendmsg is not None:
        _sperren.setattr(socket.socket, "sendmsg", _sperret_sendmsg)
    if sys.platform == "win32":
        from asyncio import windows_events

        _sperren.setattr(
            windows_events.IocpProactor, "connect",
            _sperret_proactor_connect(windows_events.IocpProactor.connect),
        )


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
def ki_av(monkeypatch):
    """Story 10.2: KI-laget er av i testene, saa main aldri velger Ollama og
    aldri leser .env for OSE_KI_TJENESTE. En test som proever KI-laget, setter
    variabelen selv eller gir kjoer en falsk modell."""
    monkeypatch.setenv("OSE_KI_TJENESTE", "av")
    monkeypatch.delenv("OSE_KI_OLLAMA_URL", raising=False)


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
