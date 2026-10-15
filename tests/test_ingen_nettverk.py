"""Kontroll av at nettsperren i conftest.py faktisk virker.

En sperre ingen tester, er en sperre vi bare tror paa.
"""

import asyncio
import http.server
import socket
import threading

import pytest
import requests

import conftest
from conftest import NettverkISTest


def test_socket_mot_internett_blokkeres():
    with pytest.raises(NettverkISTest):
        socket.socket().connect(("eodhd.com", 443))


def test_requests_blokkeres_ogsaa():
    """requests gaar gjennom socket, saa sperren ligger under biblioteket."""
    with pytest.raises(NettverkISTest):
        requests.get("https://eodhd.com/api/user", timeout=5)


def test_proxy_paa_loopback_slipper_ikke_forbi(monkeypatch):
    """Oppdaget 2026-09-23: med HTTPS_PROXY paa loopback gikk requests forbi
    sperren og stoppet foerst hos proxyen. Variabelen settes her, inne i
    testen - etter at fixturen har fjernet den - og requests skal likevel
    stoppes av sperren, ikke av proxyen."""
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9")

    with pytest.raises(NettverkISTest):
        requests.get("https://eodhd.com/api/user", timeout=5)


def test_dns_oppslag_blokkeres():
    """Ingen navneoppslag i testene, saa sperren virker likt med og uten nett."""
    with pytest.raises(NettverkISTest):
        socket.getaddrinfo("eodhd.com", 443)


def test_dns_for_loopback_slippes_gjennom():
    assert socket.getaddrinfo("localhost", 80)


def test_loopback_slippes_gjennom():
    """Loopback til en port en socket i samme prosess lytter paa, slippes
    gjennom. Rettet i story 4.0: her sto at Flask-testklienten kan trenge
    loopback. Kontrollpunktet for 4.0 i epics.md sier at den ikke bruker
    socket (kontrollert 24.09: ingen socket.connect-kall fra
    test_client().get("/")), og test_rutene_gjoer_ingen_nettverkskall i
    test_app.py viser at rutene virker uten nett."""
    lytter = socket.socket()
    lytter.bind(("127.0.0.1", 0))
    lytter.listen(1)
    port = lytter.getsockname()[1]

    klient = socket.socket()
    try:
        klient.connect(("127.0.0.1", port))
    finally:
        klient.close()
        lytter.close()


# Story 4.0: sperren gjelder hele testkjoeringen.
#
# Testene som skal fange en sperre som mangler, proever loopback til en port
# ingen lytter paa, eller sjekker at funksjonen er byttet ut foer den kalles.
# Da gaar ingenting ut av maskinen, heller ikke naar sperren er borte, som
# under mutantene (gjennomgangen av 4.0, BH10).


def _ledig_port(familie=socket.AF_INET, vert="127.0.0.1"):
    sock = socket.socket(familie)
    sock.bind((vert, 0))
    port = sock.getsockname()[1]
    sock.close()
    assert not conftest._lytter_paa(familie, port), "en lytter fra en annen test holder porten"
    return port


def _proev(funksjon):
    """Det sperren gjorde, som verdi, saa en fixture kan gi det videre."""
    try:
        funksjon()
    except NettverkISTest as feil:
        return feil
    except OSError as feil:
        return feil
    return None


def _koble_til_loopback_uten_lytter():
    sock = socket.socket()
    sock.settimeout(1)
    try:
        sock.connect(("127.0.0.1", _ledig_port()))
    finally:
        sock.close()


# Kjoerer naar modulen importeres under innsamlingen (gjennomgangen, VG1).
_VED_INNSAMLINGEN = (
    _proev(_koble_til_loopback_uten_lytter),
    socket.getaddrinfo is conftest._sperret_getaddrinfo,
)


def test_innsamlingen_er_sperret():
    """Ville feilet hvis sperren foerst ble satt i en fixture."""
    tilkobling, dns_sperret = _VED_INNSAMLINGEN
    assert isinstance(tilkobling, NettverkISTest), tilkobling
    assert dns_sperret


@pytest.fixture(scope="module")
def forsoek_i_modulfixture():
    """En fixture med module-scope kjoerer utenfor testfunksjonen."""
    return (
        _proev(_koble_til_loopback_uten_lytter),
        socket.getaddrinfo is conftest._sperret_getaddrinfo,
    )


@pytest.fixture(scope="session")
def forsoek_i_oekta():
    return _proev(_koble_til_loopback_uten_lytter)


def test_fixture_med_module_scope_er_sperret(forsoek_i_modulfixture):
    """Ville feilet hvis en fixture med module-scope kunne naa nettet."""
    tilkobling, dns_sperret = forsoek_i_modulfixture
    assert isinstance(tilkobling, NettverkISTest), tilkobling
    assert dns_sperret


def test_fixture_med_session_scope_er_sperret(forsoek_i_oekta):
    assert isinstance(forsoek_i_oekta, NettverkISTest), forsoek_i_oekta


def test_connect_ex_blokkeres():
    sock = socket.socket()
    try:
        with pytest.raises(NettverkISTest):
            sock.connect_ex(("127.0.0.1", _ledig_port()))
    finally:
        sock.close()


@pytest.mark.parametrize("vert", ["127.0.0.1", "localhost"])
def test_loopback_uten_lytter_blokkeres(vert):
    """En proxy eller en Ollama paa loopback naas ikke, uansett bibliotek."""
    port = _ledig_port()
    sock = socket.socket()
    try:
        with pytest.raises(NettverkISTest):
            sock.connect((vert, port))
        with pytest.raises(NettverkISTest):
            sock.connect_ex((vert, port))
    finally:
        sock.close()


def test_ollamaporten_paa_loopback_blokkeres():
    """Porten Ollama bruker som standard (svar 8 kl. 15:53)."""
    sock = socket.socket()
    try:
        with pytest.raises(NettverkISTest):
            sock.connect(("127.0.0.1", 11434))
    finally:
        sock.close()


def test_lukket_lytter_slipper_ikke_gjennom():
    lytter = socket.socket()
    lytter.bind(("127.0.0.1", 0))
    lytter.listen(1)
    port = lytter.getsockname()[1]
    lytter.close()

    sock = socket.socket()
    try:
        with pytest.raises(NettverkISTest):
            sock.connect(("127.0.0.1", port))
    finally:
        sock.close()


def test_lytter_i_en_annen_familie_slipper_ikke_gjennom():
    """En lytter paa ::1 aapner ikke 127.0.0.1 paa samme port (BH5, ECH1)."""
    lytter = socket.socket(socket.AF_INET6)
    try:
        lytter.bind(("::1", 0))
    except OSError:
        lytter.close()
        pytest.skip("::1 finnes ikke paa maskinen")
    lytter.listen(1)
    port = lytter.getsockname()[1]
    sock = socket.socket()
    try:
        with pytest.raises(NettverkISTest):
            sock.connect(("127.0.0.1", port))
    finally:
        sock.close()
        lytter.close()


def test_requests_mot_loopback_uten_lytter_blokkeres():
    with pytest.raises(NettverkISTest):
        requests.get(f"http://127.0.0.1:{_ledig_port()}/api/generate", timeout=5)


def test_asyncio_blokkeres():
    """Paa Windows kobler asyncio til med ConnectEx, utenom socket.connect
    (gjennomgangen, BH4, ECH5, VG2)."""

    async def koble():
        await asyncio.open_connection("127.0.0.1", _ledig_port())

    with pytest.raises(NettverkISTest):
        asyncio.run(koble())


def test_udp_blokkeres():
    """sendto trenger ingen connect (gjennomgangen, BH3)."""
    assert socket.socket.sendto is conftest._sperret_sendto
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        with pytest.raises(NettverkISTest):
            sock.sendto(b"x", ("127.0.0.1", _ledig_port()))
        with pytest.raises(NettverkISTest):
            sock.sendto(b"x", 0, ("127.0.0.1", _ledig_port()))
    finally:
        sock.close()


@pytest.mark.parametrize("funksjon", [
    "gethostbyname", "gethostbyname_ex", "gethostbyaddr", "getfqdn",
])
def test_navneoppslag_blokkeres(funksjon):
    """Funksjonen sjekkes foer den kalles, saa en sperre som mangler, ikke
    gir et ekte oppslag."""
    assert getattr(socket, funksjon) is not getattr(conftest, f"_ekte_{funksjon}", None)
    assert getattr(socket, funksjon).__module__ == "conftest"
    with pytest.raises(NettverkISTest):
        getattr(socket, funksjon)("192.0.2.1" if funksjon == "gethostbyaddr" else "eodhd.com")


def test_getnameinfo_blokkeres():
    assert socket.getnameinfo is conftest._sperret_getnameinfo
    with pytest.raises(NettverkISTest):
        socket.getnameinfo(("192.0.2.1", 80), 0)


def test_getfqdn_uten_navn_blokkeres():
    """getfqdn() slaar opp maskinens eget navn."""
    assert socket.getfqdn is conftest._sperret_getfqdn
    with pytest.raises(NettverkISTest):
        socket.getfqdn()


def test_navneoppslag_paa_loopback_slippes_gjennom():
    assert socket.gethostbyname("localhost")
    assert socket.gethostbyname_ex("localhost")
    assert socket.getfqdn("localhost") == "localhost"
    assert socket.getfqdn("127.0.0.1") == "localhost"


@pytest.mark.parametrize("vert", ["LOCALHOST", "localhost.", "127.0.0.2", "::1"])
def test_andre_skrivemaater_for_loopback(vert):
    """Gjennomgangen (BH13): ingen av dem er et oppslag paa nettet."""
    assert conftest._er_loopbacknavn(vert)


def test_getaddrinfo_med_navngitte_argumenter():
    assert socket.getaddrinfo(host="localhost", port=80, family=socket.AF_INET)
    with pytest.raises(NettverkISTest):
        socket.getaddrinfo(host="eodhd.com", port=443)


def test_http_server_paa_loopback_virker():
    """En falsk tjeneste i en test (som en falsk Ollama) kan lytte paa
    127.0.0.1 og naas derfra (gjennomgangen, BH6). server_bind kaller
    getfqdn med adressen."""

    class Svar(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *args):
            pass

    tjener = http.server.HTTPServer(("127.0.0.1", 0), Svar)
    traad = threading.Thread(target=tjener.handle_request)
    traad.start()
    try:
        svar = requests.get(f"http://127.0.0.1:{tjener.server_address[1]}/", timeout=5)
        assert svar.text == "ok"
    finally:
        traad.join(timeout=5)
        tjener.server_close()


@pytest.mark.skipif(not hasattr(socket, "AF_UNIX"), reason="AF_UNIX finnes ikke i Python paa Windows")
def test_af_unix_slippes_gjennom(tmp_path):
    sti = str(tmp_path / "s")
    lytter = socket.socket(socket.AF_UNIX)
    lytter.bind(sti)
    lytter.listen(1)
    klient = socket.socket(socket.AF_UNIX)
    try:
        klient.connect(sti)
    finally:
        klient.close()
        lytter.close()
