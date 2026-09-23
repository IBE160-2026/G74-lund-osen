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
    """Loopback kan ikke naa en leverandoer, og Flask-testklienten kan trenge den."""
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
