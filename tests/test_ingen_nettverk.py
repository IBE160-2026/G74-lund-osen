"""Kontroll av at nettsperren i conftest.py faktisk virker.

En sperre ingen tester, er en sperre vi bare tror paa.
"""

import socket

import pytest
import requests

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
    loopback. Den bruker ikke socket (kontrollert 24.09: ingen
    socket.connect-kall fra test_client().get("/"))."""
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

UTENFOR = ("192.0.2.1", 9)  # TEST-NET-1, brukes aldri paa nettet


def _proev(funksjon):
    """Det sperren gjorde, som verdi, saa en fixture kan gi det videre."""
    try:
        funksjon()
    except NettverkISTest as feil:
        return feil
    except OSError as feil:
        return feil
    return None


def _koble_til():
    sock = socket.socket()
    sock.settimeout(1)
    try:
        sock.connect(UTENFOR)
    finally:
        sock.close()


@pytest.fixture(scope="module")
def forsoek_i_modulfixture():
    """En fixture med module-scope kjoerer utenfor testfunksjonen."""
    return _proev(_koble_til), _proev(lambda: socket.getaddrinfo("eodhd.com", 443))


@pytest.fixture(scope="session")
def forsoek_i_oekta():
    return _proev(_koble_til)


def test_fixture_med_module_scope_er_sperret(forsoek_i_modulfixture):
    """Ville feilet hvis en fixture med module-scope kunne naa nettet."""
    tilkobling, oppslag = forsoek_i_modulfixture
    assert isinstance(tilkobling, NettverkISTest), tilkobling
    assert isinstance(oppslag, NettverkISTest), oppslag


def test_fixture_med_session_scope_er_sperret(forsoek_i_oekta):
    assert isinstance(forsoek_i_oekta, NettverkISTest), forsoek_i_oekta


def test_connect_ex_mot_internett_blokkeres():
    sock = socket.socket()
    try:
        with pytest.raises(NettverkISTest):
            sock.connect_ex(UTENFOR)
    finally:
        sock.close()


def _ledig_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


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


def test_requests_mot_loopback_uten_lytter_blokkeres():
    with pytest.raises(NettverkISTest):
        requests.get(f"http://127.0.0.1:{_ledig_port()}/api/generate", timeout=5)


@pytest.mark.parametrize("funksjon", ["gethostbyname", "gethostbyname_ex", "getfqdn"])
def test_navneoppslag_blokkeres(funksjon):
    with pytest.raises(NettverkISTest):
        getattr(socket, funksjon)("eodhd.com")


def test_getfqdn_uten_navn_blokkeres():
    """getfqdn() slaar opp maskinens eget navn."""
    with pytest.raises(NettverkISTest):
        socket.getfqdn()


def test_navneoppslag_paa_loopback_slippes_gjennom():
    assert socket.gethostbyname("localhost")
    assert socket.gethostbyname_ex("localhost")
    assert socket.getfqdn("localhost")


def test_getaddrinfo_med_navngitte_argumenter():
    assert socket.getaddrinfo(host="localhost", port=80, family=socket.AF_INET)
    with pytest.raises(NettverkISTest):
        socket.getaddrinfo(host="eodhd.com", port=443)


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
