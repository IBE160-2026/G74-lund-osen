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
    with pytest.raises(Exception) as feil:
        requests.get("https://eodhd.com/api/user", timeout=5)

    assert "blokkert" in str(feil.value) or isinstance(feil.value, NettverkISTest)


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
