"""Story 8.22, del D: «Din egen liste» som tre stegkort - utdraget 08.11 §2, AD-10.

Spesifikasjonen er spec-8-22-foelg-en-aksje-og-min-liste.md, spørsmål 9 og
10, og tillegget 10.11 kl. 17:16 om demoen. Hver test lager sin egen base
under tmp_path (regel 22), og ingen test gjør nettkall (AD-8).
"""

import re
import shutil
from datetime import datetime

import app as app_modul
from test_valg import BOERSEN, faste_bransjer, klient, stier  # noqa: F401  (fiksturene)


def _delen(html: str) -> str:
    return html.split('<section class="egne" id="din-egen-liste"', 1)[1].split("</section>", 1)[0]


def _kortene(html: str) -> list[str]:
    return re.findall(r'<li class="kort-steg">(.*?)</li>\s*(?=<li class="kort-steg">|</ol>)', _delen(html), re.S)


def test_tre_stegkort_i_rekkefoelgen_fra_utdraget(klient):  # noqa: F811
    """Ville feilet hvis stegene ikke var tre kort, i rekkefølgen konto,
    nøkkel og aksjer, med nummeret i kortet."""
    kortene = _kortene(klient.get("/min-liste").data.decode("utf-8"))
    assert [re.search(r"<h4>(.*?)</h4>", k).group(1) for k in kortene] == [
        "Lag en gratis konto hos EODHD",
        "Lim inn nøkkelen din",
        "Velg aksjene dine",
    ]
    assert [re.search(r'<span class="stegnummer" aria-hidden="true">(\d)</span>', k).group(1) for k in kortene] == [
        "1",
        "2",
        "3",
    ]
    assert "Adressen er eodhd.com." in kortene[0]


def test_noekkelen_har_ikke_noe_felt(klient):  # noqa: F811
    """AD-10 og svaret 08.11 kl. 12:39: ville feilet hvis siden fikk et felt
    for nøkkelen, eller steg 2 ikke sa at den limes inn ved oppstart."""
    html = klient.get("/min-liste").data.decode("utf-8")
    andre = _kortene(html)[1]
    assert "startskriptet spør etter den" in andre and "<input" not in andre
    assert not re.search(r'<input[^>]*type="(text|password)"', _delen(html))
    assert "Demoen trenger ingen nøkkel" not in andre


def test_kallene_og_knappene_i_steg_3(klient):  # noqa: F811
    """Spørsmål 10: ville feilet hvis kallene i steg 3 ikke var regnet av
    lista, eller knappen til «Følg en aksje» manglet."""
    html = klient.get("/min-liste").data.decode("utf-8")
    tredje = _kortene(html)[2]
    assert "<li>15 kall: de 15 aksjene</li>" in tredje and "<li>4 kall: margin</li>" in tredje
    assert '<a class="knapp hoved" href="/folg">+ Følg en aksje</a>' in tredje
    # Kallene står bare ett sted.
    assert _delen(html).count("kall: hovedindeksen") == 1


def test_full_liste_i_steg_3(klient):  # noqa: F811
    """Ville feilet hvis steg 3 viste knappen når lista er full."""
    for kode, _ in BOERSEN[:3]:
        klient.post("/folg", data={"kode": kode})
    tredje = _kortene(klient.get("/min-liste").data.decode("utf-8"))[2]
    assert "Lista er full. Fjern en aksje for å følge en annen." in tredje and 'href="/folg"' not in tredje


def test_demoen_viser_kortene_og_trenger_ingen_noekkel(tmp_path, monkeypatch):
    """Tillegget 10.11 kl. 17:16: ville feilet hvis stegkortene manglet i
    demoen, eller steg 2 ikke sa at demoen ikke trenger nøkkel, eller
    knappen til bransjelistene manglet der det er ferdige lister."""
    import demo
    from lagring_sqlite import demo_sti

    mal = tmp_path / "demo.db"
    demo.lag_demobase(mal, skriv=lambda _: None)
    sti = demo_sti()
    sti.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(mal, sti)
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0).astimezone())
    html = app_modul.app.test_client().get("/min-liste").data.decode("utf-8")
    kortene = _kortene(html)
    assert len(kortene) == 3
    assert "Demoen trenger ingen nøkkel. Den viser oppdiktede selskaper og henter aldri." in kortene[1]
    assert '<a class="knapp" href="#ferdige-lister">Velg en bransjeliste</a>' in kortene[2]
    assert 'id="ferdige-lister"' in html
