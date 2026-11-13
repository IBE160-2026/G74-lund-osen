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
    # Story 8.29 (gjennomgangen, BH1): titlene er h3.
    assert [re.search(r"<h3>(.*?)</h3>", k).group(1) for k in kortene] == [
        "Lag en gratis konto hos EODHD",
        "Lim inn nøkkelen din",
        "Velg aksjene dine",
    ]
    assert [re.search(r'<span class="stegnummer" aria-hidden="true">(\d)</span>', k).group(1) for k in kortene] == [
        "1",
        "2",
        "3",
    ]
    # Story 8.26 (tillegg 12): knappen til registreringen hos EODHD i en ny
    # fane, i stedet for adressen som tekst (spørsmål 9 er rettet).
    assert (
        '<a class="knapp" href="https://eodhd.com/register" target="_blank" rel="noreferrer">Åpne eodhd.com'
        in kortene[0]
    )


def test_noekkelen_har_ikke_noe_felt(klient):  # noqa: F811
    """AD-10 og svaret 08.11 kl. 12:39, som står etter tillegg 4: ville feilet
    hvis siden fikk et felt eller en knapp for nøkkelen, eller steg 2 ikke
    sa hvordan nøkkelen byttes med startskriptet."""
    html = klient.get("/min-liste").data.decode("utf-8")
    andre = _kortene(html)[1]
    # Story 8.26 (tillegg 12): bare «?» er en knapp i steg 2.
    uten_hjelp = re.sub(r'<button type="button" class="hjelpeknapp"[^>]*>\?</button>', "", andre)
    assert "<input" not in andre and "<button" not in uten_hjelp and "Sjekk nøkkelen" not in andre
    assert not re.search(r'<input[^>]*type="(text|password)"', _delen(html))
    assert "Demoen trenger ingen nøkkel" not in andre
    # Story 8.26 (tillegg 12): «Slik bytter du nøkkel» står bak «?».
    assert 'popovertarget="hjelp-noekkel"' in andre
    assert (
        "Neste gang den ekte versjonen startes med startskriptet, spør det etter nøkkelen og lagrer den nye."
        in html.split('id="hjelp-noekkel"', 1)[1]
    )
    # Story 8.29 (gruppens svar 13.11): setningen sier at startskriptet spør etter nøkkelen.
    assert (
        "Nøkkelen står på kontosiden hos EODHD. Startskriptet til den ekte versjonen spør etter den første gang,"
        " og den lagres bare på denne maskinen." in andre
    )


def test_kallene_og_knappene_i_steg_3(klient):  # noqa: F811
    """Spørsmål 10: ville feilet hvis kallene i steg 3 ikke var regnet av
    lista, eller knappen til «Følg en aksje» manglet."""
    html = klient.get("/min-liste").data.decode("utf-8")
    tredje = _kortene(html)[2]
    # Story 8.26 (tillegg 12): kallene, regnet av lista, står bak «?».
    vindu = html.split('id="hjelp-kallene"', 1)[1].split('<p class="lukkes">', 1)[0]
    assert "<li>15 kall: de 15 aksjene</li>" in vindu and "<li>4 kall: margin</li>" in vindu
    assert 'popovertarget="hjelp-kallene"' in tredje
    assert '<a class="knapp hoved" href="/folg">+ Følg en aksje</a>' in tredje
    # Kallene står bare ett sted.
    assert html.count("kall: hovedindeksen") == 1


def test_full_liste_i_steg_3(klient):  # noqa: F811
    """Ville feilet hvis steg 3 viste knappen når lista er full."""
    for kode, _ in BOERSEN[:3]:
        klient.post("/folg", data={"kode": kode})
    tredje = _kortene(klient.get("/min-liste").data.decode("utf-8"))[2]
    assert (
        "Appen følger allerede 18 aksjer, som er taket. Fjern en for å følge en annen." in tredje
        and 'href="/folg"' not in tredje
    )


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
    # Story 8.26 (tillegg 12): én linje med ✓, de ferdige listene som brikker
    # i steg 3, og «Åpne eodhd.com» til siden i demoen.
    assert '<span class="hake" aria-hidden="true">✓</span> Demoen trenger ingen nøkkel.</span>' in kortene[1]
    assert 'id="ferdige-lister"' in kortene[2] and 'class="knapp ferdigknapp"' in kortene[2]
    assert '<a class="knapp" href="/eodhd-demo">Åpne eodhd.com</a>' in kortene[0] and "eodhd.com/register" not in html


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
    # Story 8.26 (tillegg 12): bak «?» i steg 3.
    side = klient.get("/min-liste").data.decode("utf-8")
    vindu = side.split('id="hjelp-kallene"', 1)[1].split('<p class="lukkes">', 1)[0]
    assert "<li>15 kall: de 15 aksjene</li>" in vindu and "<li>1 kall: din egen aksje</li>" in vindu
    assert "<li>3 kall: margin</li>" in vindu


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
    hentingen brukte, talt i hentingen selv, med dagen og kvoten fra
    valg.KVOTE (gjennomgangen, BH1, BH2, BH3)."""
    import valg

    k, kall = _klient_med_henting(stier, monkeypatch)
    andre = _kortene(k.get("/min-liste").data.decode("utf-8"))[1]
    assert kall
    assert (
        f'<span class="hake" aria-hidden="true">✓</span> Nøkkelen virket ved siste henting 22.09, som brukte minst '
        f"{len(kall)} av {valg.KVOTE} kall.</span>"
    ) in andre
    assert "Ingen henting har lagret kurser ennå" not in andre
    monkeypatch.setattr(valg, "KVOTE", 25)
    assert f"minst {len(kall)} av 25 kall." in _kortene(k.get("/min-liste").data.decode("utf-8"))[1]


def test_to_hentinger_samme_dag_gir_minst(stier, monkeypatch):  # noqa: F811
    """Gjennomgangen (ECH3, VG2): ville feilet hvis en serie som ble hentet
    to ganger samme dag, ble talt to ganger, eller tallet ble mer enn
    kallene. Seriene er det minste antallet kall."""
    from test_fetch_prices import OEYEBLIKK_22_09, kjoer_23

    k, kall = _klient_med_henting(stier, monkeypatch)
    _, kall2, _ = kjoer_23(stier[0], stier[1], OEYEBLIKK_22_09)
    andre = _kortene(k.get("/min-liste").data.decode("utf-8"))[1]
    tall = int(re.search(r"som brukte minst (\d+) av", andre).group(1))
    assert 0 < tall <= len(kall) + len(kall2)


def test_et_kall_som_feiler_og_proeves_igjen_gir_minst(stier, monkeypatch):  # noqa: F811
    """Spørsmål 14 (VG2 i gjennomgangen av tillegg 4, svaret 11.11 kl. 14:29):
    ett kall feiler i kveldens henting og prøves igjen i et nytt forsøk (2.3b)
    samme kveld. Kallene telles i begge kjøringene, og seriene i basen.
    Ville feilet hvis statusen talte kallene eller størrelsen på lista i
    stedet for seriene (etter feilen er det 15 serier, men 16 kall og 16 i
    lista), hvis den mistet «minst», eller hvis det nye forsøket ikke ble
    talt med samme dag (gjennomgangen av svarene, BH1, BH2, VG1, VG6)."""
    import lagring_sqlite
    import valg
    from test_fetch_prices import (
        ETTER_30_MIN,
        KALL,
        OEYEBLIKK_22_09,
        TIRSDAG_22_09,
        kjoer_23,
        kjoer_23_kode,
        serie_til,
    )
    from test_valg import med_boersen

    def hent(ticker, *_):
        if ticker == "DNB.OL":
            raise RuntimeError("nei")
        return serie_til(TIRSDAG_22_09)

    raa, base = stier
    kode, kall1, _ = kjoer_23_kode(raa, base, OEYEBLIKK_22_09, hent)
    assert kode == 1 and len(kall1) == KALL and "DNB.OL" in kall1
    med_boersen(base)
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 23, 12, 0).astimezone())
    monkeypatch.setitem(app_modul.app.config, "TESTING", True)

    def status() -> str:
        andre = _kortene(app_modul.app.test_client().get("/min-liste").data.decode("utf-8"))[1]
        return re.search(r'<span class="hake" aria-hidden="true">✓</span> (.*?)</span>', andre).group(1)

    # Etter feilen: 15 serier er lagret, men hentingen brukte 16 kall.
    assert status() == f"Nøkkelen virket ved siste henting 22.09, som brukte minst {KALL - 1} av {valg.KVOTE} kall."
    fil, kall2, _ = kjoer_23(raa, base, ETTER_30_MIN)
    assert fil is not None and kall2 == ["DNB.OL"]
    # Etter det nye forsøket: 16 serier, og 17 kall til sammen.
    assert status() == f"Nøkkelen virket ved siste henting 22.09, som brukte minst {KALL} av {valg.KVOTE} kall."
    assert KALL < len(kall1) + len(kall2)


def test_uten_henting_staar_hva_man_gjoer(klient, monkeypatch):  # noqa: F811
    """Ville feilet hvis steg 2 sa at nøkkelen virket uten at noen henting
    har lagret kurser, eller ikke pekte på byttet når hentingen har feilet
    (gjennomgangen, ECH2). Uten serier i basen viser Min liste ikke delen,
    så siste_henting gir None her; at den gir None uten serier, står i
    test_siste_henting_er_dagen_i_oslo."""
    import valg

    monkeypatch.setattr(valg, "siste_henting", lambda _t: None)
    andre = _kortene(klient.get("/min-liste").data.decode("utf-8"))[1]
    assert "Nøkkelen virket" not in andre
    assert (
        "Ingen henting har lagret kurser ennå. Startes den ekte versjonen med startskriptet, spør det etter "
        "nøkkelen første gang, og hentingen går med en gang. Har den feilet, kan nøkkelen være feil: se "
        "«Slik bytter du nøkkel» bak «?».</span>"
    ) in andre


def test_byttet_staar_ogsaa_for_docker(klient, monkeypatch):  # noqa: F811
    """Gjennomgangen (ECH1, VG3): ville feilet hvis «Slik bytter du nøkkel»
    bare gjaldt startskriptet, også når appen kjører i Docker."""
    monkeypatch.setenv(app_modul.I_DOCKER, "1")
    side = klient.get("/min-liste").data.decode("utf-8")
    # Story 8.26 (tillegg 12): bak «?» i steg 2.
    assert (
        "Med Docker, eller uten startskriptet, skriver du den nye nøkkelen etter EODHD_API_KEY= "
        "selv og starter appen på nytt."
    ) in side.split('id="hjelp-noekkel"', 1)[1]


def test_statusen_leser_aldri_noekkelen(klient, monkeypatch, tmp_path):  # noqa: F811
    """AD-10 (gjennomgangen, VG1): ville feilet hvis siden leste nøkkelen fra
    miljøet, på noen måte, eller åpnet en fil som heter .env."""
    import builtins
    import os
    import pathlib

    class Spion(dict):
        lest: list = []

        def __getitem__(self, n):
            Spion.lest.append(n)
            return super().__getitem__(n)

        def get(self, n, *a):
            Spion.lest.append(n)
            return super().get(n, *a)

    (tmp_path / ".env").write_text("EODHD_API_KEY=IKKE-EN-EKTE-NOEKKEL-8-22", encoding="utf-8")
    monkeypatch.setattr(os, "environ", Spion(os.environ, EODHD_API_KEY="IKKE-EN-EKTE-NOEKKEL-8-22"))
    aapnet = []
    ekte_open, ekte_path_open = builtins.open, pathlib.Path.open
    monkeypatch.setattr(builtins, "open", lambda f, *a, **k: aapnet.append(str(f)) or ekte_open(f, *a, **k))
    monkeypatch.setattr(
        pathlib.Path, "open", lambda self, *a, **k: aapnet.append(str(self)) or ekte_path_open(self, *a, **k)
    )
    monkeypatch.chdir(tmp_path)
    html = klient.get("/min-liste").data.decode("utf-8")
    assert "IKKE-EN-EKTE-NOEKKEL-8-22" not in html
    assert "EODHD_API_KEY" not in Spion.lest
    assert not [f for f in aapnet if f.endswith(".env")]
    assert "Nøkkelen virket ved siste henting" in html


def test_siste_henting_er_dagen_i_oslo(tmp_path):
    """Ville feilet hvis dagen ble regnet i UTC, seriene fra en eldre
    henting ble talt med, eller én verdi som ikke kan leses, gjorde hele
    statusen tom (gjennomgangen, ECH4). 23:30 UTC 09.11 er 10.11 i Oslo."""
    from datetime import date

    import valg
    from kursdata import AKSJEUNIVERS
    from lagring_sqlite import aapne_base

    # kursserie godtar bare aksjer i aksje, så de fire er fra de 15.
    a, b, c, d = (aksje.symbol for aksje in AKSJEUNIVERS[:4])
    base = tmp_path / "db" / "ose.db"
    base.parent.mkdir(parents=True)
    t = aapne_base(base)
    try:
        assert valg.siste_henting(t) is None
        with t:
            t.executemany(
                "INSERT INTO kursserie (symbol, hentet) VALUES (?, ?)",
                [
                    (a, "2026-11-09T23:30:00+00:00"),
                    (b, "2026-11-09T23:31:00+00:00"),
                    (c, "2026-11-09T21:00:00+00:00"),
                    (d, "ikke en dato"),
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
    assert '<span class="hake" aria-hidden="true">✓</span> Demoen trenger ingen nøkkel.</span>' in andre
    assert "Nøkkelen virket" not in andre and "Ingen henting har lagret kurser ennå" not in andre
    assert 'popovertarget="hjelp-noekkel"' in andre and "<input" not in andre
