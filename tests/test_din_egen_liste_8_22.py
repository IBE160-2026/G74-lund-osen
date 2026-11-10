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
    """AD-10 og svaret 08.11 kl. 12:39, som står etter tillegg 4: ville feilet
    hvis siden fikk et felt eller en knapp for nøkkelen, eller steg 2 ikke
    sa hvordan nøkkelen byttes med startskriptet."""
    html = klient.get("/min-liste").data.decode("utf-8")
    andre = _kortene(html)[1]
    assert "<input" not in andre and "<button" not in andre and "Sjekk nøkkelen" not in andre
    assert not re.search(r'<input[^>]*type="(text|password)"', _delen(html))
    assert "Demoen trenger ingen nøkkel" not in andre
    assert "<h5>Slik bytter du nøkkel</h5>" in andre
    assert "Neste gang den ekte versjonen startes, spør startskriptet etter nøkkelen og lagrer den nye." in andre
    assert "Nøkkelen står på kontosiden hos EODHD. Den lagres bare på denne maskinen." in andre


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


def test_kallene_i_steg_3_er_regnet_av_lista(klient, stier):  # noqa: F811
    """Gjennomgangen (VG4): ville feilet hvis kallene i steg 3 sto fast i
    malen. Med én egen aksje tatt inn er det 1 kall til den og 3 i margin."""
    from datetime import date

    import valg
    from lagring_sqlite import aapne_base
    from test_valg import lager

    l = lager(stier[1])
    l.folg("NYA", "Kraft")
    l._t.close()
    t = aapne_base(stier[1])
    try:
        valg.ta_i_bruk(t, date(2026, 9, 23))
    finally:
        t.close()
    tredje = _kortene(klient.get("/min-liste").data.decode("utf-8"))[2]
    assert "<li>15 kall: de 15 aksjene</li>" in tredje and "<li>1 kall: din egen aksje</li>" in tredje
    assert "<li>3 kall: margin</li>" in tredje


# Tillegg 4 (svaret 10.11 kl. 22:50): steg 2 som på designtavla, uten felt.
# Der tavla har feltet og «Sjekk nøkkelen», står statusen regnet av siste
# henting, uten kall og uten å lese .env.


def _klient_med_henting(stier, monkeypatch):  # noqa: F811
    """Som klient i test_valg, men med kallene fra hentingen talt."""
    import lagring_sqlite
    from test_fetch_prices import OEYEBLIKK_22_09, kjoer_23
    from test_valg import med_boersen

    raa, base = stier
    _, kall, _ = kjoer_23(raa, base, OEYEBLIKK_22_09)
    med_boersen(base)
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 23, 12, 0).astimezone())
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client(), kall


def test_statusen_er_kallene_hentingen_brukte(stier, monkeypatch):  # noqa: F811
    """Ville feilet hvis statusen i steg 2 ikke var kallene den siste
    hentingen faktisk brukte, talt i hentingen selv, med dagen."""
    k, kall = _klient_med_henting(stier, monkeypatch)
    andre = _kortene(k.get("/min-liste").data.decode("utf-8"))[1]
    assert kall
    assert (
        f'<p class="noekkelstatus virker">Nøkkelen virker: siste henting 22.09 brukte {len(kall)} av 20 kall.</p>'
        in andre
    )
    assert "Ingen henting har gått ennå" not in andre


def test_uten_henting_staar_hva_man_gjoer(klient, stier):  # noqa: F811
    """Ville feilet hvis steg 2 sa at nøkkelen virker uten at noen henting
    har gått, eller ikke sa hva man gjør."""
    from lagring_sqlite import aapne_base

    t = aapne_base(stier[1])
    try:
        with t:
            t.execute("DELETE FROM kursserie")
            t.execute("DELETE FROM indeksserie")
    finally:
        t.close()
    andre = _kortene(klient.get("/min-liste").data.decode("utf-8"))[1]
    assert "Nøkkelen virker" not in andre
    assert (
        "Ingen henting har gått ennå. Start den ekte versjonen med startskriptet: første gang spør det etter "
        "nøkkelen, og du limer den inn der. Aksjene hentes ved neste henting etter kl. 22."
    ) in andre


def test_statusen_leser_aldri_noekkelen(klient, monkeypatch):  # noqa: F811
    """AD-10: ville feilet hvis siden leste nøkkelen fra miljøet eller .env,
    eller viste den."""
    import os

    hemmelig = "IKKE-EN-EKTE-NOEKKEL-8-22"
    monkeypatch.setenv("EODHD_API_KEY", hemmelig)
    lest = []
    ekte_getenv = os.getenv
    monkeypatch.setattr(os, "getenv", lambda n, *a: lest.append(n) or ekte_getenv(n, *a))
    html = klient.get("/min-liste").data.decode("utf-8")
    assert hemmelig not in html and "EODHD_API_KEY" not in lest
    import valg

    assert "environ" not in valg.siste_henting.__code__.co_names
    assert ".env" not in valg.siste_henting.__code__.co_consts


def test_siste_henting_er_dagen_i_oslo(tmp_path):
    """Ville feilet hvis dagen ble regnet i UTC, eller kallene fra en eldre
    henting ble talt med. 23:30 UTC 09.11 er 10.11 i Oslo."""
    from datetime import date

    import valg
    from lagring_sqlite import aapne_base

    base = tmp_path / "db" / "ose.db"
    base.parent.mkdir(parents=True)
    t = aapne_base(base)
    try:
        assert valg.siste_henting(t) is None
        with t:
            t.executemany(
                "INSERT INTO kursserie (symbol, hentet) VALUES (?, ?)",
                [
                    ("AAA", "2026-11-09T23:30:00+00:00"),
                    ("BBB", "2026-11-09T23:31:00+00:00"),
                    ("CCC", "2026-11-09T21:00:00+00:00"),
                ],
            )
            t.execute("INSERT INTO indeksserie (symbol, hentet) VALUES (?, ?)", ("OSEBX", "2026-11-09T23:32:00+00:00"))
        assert valg.siste_henting(t) == valg.SisteHenting(date(2026, 11, 10), 3)
    finally:
        t.close()


def test_demoen_har_det_samme_kortet(tmp_path, monkeypatch):
    """Tillegg 4: ville feilet hvis steg 2 i demoen var et annet kort enn i
    den ekte versjonen, eller sa noe om nøkkelen virker."""
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
    andre = _kortene(app_modul.app.test_client().get("/min-liste").data.decode("utf-8"))[1]
    assert (
        '<p class="noekkelstatus">Demoen trenger ingen nøkkel. Den viser oppdiktede selskaper og henter aldri.</p>'
        in andre
    )
    assert "Nøkkelen virker" not in andre and "Ingen henting har gått ennå" not in andre
    assert "<h5>Slik bytter du nøkkel</h5>" in andre and "<input" not in andre
