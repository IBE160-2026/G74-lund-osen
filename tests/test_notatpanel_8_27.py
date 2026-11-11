"""Story 8.27: «Mine notater» i et panel fra en knapp øverst, og tillegg 1,
plassen på aksjesiden (gruppens svar 11.11 kl. 21:09–21:20 og 21:36).

Spesifikasjonen er spec-8-27-mine-notater-i-panel.md, med delene A-E. Hver
test kjøres i demoen og i den ekte versjonen. Den ekte versjonen er en kopi av
demobasen uten demomerket, så appen viser den som den ekte; ingen ekte tall.
Testbasene ligger i tmp_path (conftest.py, regel 22), og ingen test gjør
nettkall (AD-8).
"""

import re
import shutil
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

import app as app_modul
import demo
import lagring_sqlite
from lagring_sqlite import SqliteKurslager, SqliteNotatlager, demo_sti

ROT = Path(__file__).resolve().parents[1]
LAGET = datetime(2026, 11, 11, 21, 0, tzinfo=timezone.utc)
# Demobasen har kurser fra 02.01 til fredag 09.10 (demo.py).
SISTE = date(2026, 10, 9)
TIDLIGERE = date(2026, 10, 1)
AKSJE = "BRFE"
ANNEN = "KVST"
SIDENE = ("/", "/min-liste", "/boersometer", f"/aksje/{AKSJE}", "/innstillinger", "/folg")
VERSJONENE = ("demo", "ekte")


@pytest.fixture(scope="module")
def mal(tmp_path_factory):
    """Demobasen uten eksemplene, så testene begynner uten notater."""
    sti = tmp_path_factory.mktemp("panelmal") / "demo.db"
    demo.lag_demobase(sti, skriv=lambda _: None)
    c = sqlite3.connect(sti)
    c.execute("DELETE FROM notat")
    c.commit()
    c.close()
    return sti


@pytest.fixture(params=VERSJONENE)
def versjon(request):
    return request.param


@pytest.fixture
def base(mal, versjon, monkeypatch):
    """Demobasen i demoen, eller en kopi uten merket som ose.db for den ekte
    versjonen. Begge i tmp_path fra conftest.py."""
    if versjon == "demo":
        sti = demo_sti()
        sti.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(mal, sti)
        monkeypatch.setenv(app_modul.I_DEMO, "1")
    else:
        sti = Path(lagring_sqlite.BASE_STI)
        sti.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(mal, sti)
        c = sqlite3.connect(sti)
        c.execute("PRAGMA application_id = 0")
        c.commit()
        c.close()
        monkeypatch.delenv(app_modul.I_DEMO, raising=False)
    return sti


@pytest.fixture
def klient(base, monkeypatch):
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    monkeypatch.setattr(app_modul, "naa", lambda: LAGET)
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


def _side(klient, adresse: str) -> str:
    svar = klient.get(adresse)
    assert svar.status_code == 200, adresse
    return svar.data.decode("utf-8")


def _tekst(html: str) -> str:
    return re.sub(r"[ \t\r\n]+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _knappen(side: str) -> str | None:
    treff = re.search(r'<a class="sideknapp notatknapp"[^>]*>.*?</a>', side, re.S)
    return treff.group(0) if treff else None


def _malen(side: str) -> str:
    """Innholdet i panelet: <template> i rammen, som skriptet viser."""
    start = side.index('<template id="notatpanel-mal">')
    return side[start : side.index("</template>", start)]


def _panelet(klient, adresse: str = "/") -> str:
    """Innholdet i panelet slik det står på siden."""
    return _malen(_side(klient, adresse))


def _delen(side: str) -> str:
    """«Mine notater» nederst på siden, uten panelet."""
    start = side.index('<section class="notater" id="mine-notater"')
    return side[start : side.index("</section>", start)]


def _notat(base: Path, symbol: str, dag: date, tekst: str) -> None:
    c = sqlite3.connect(base)
    try:
        SqliteNotatlager(c).skriv(symbol, dag, tekst, LAGET)
        c.commit()
    finally:
        c.close()


def _notatene(base: Path) -> list[tuple]:
    c = sqlite3.connect(base)
    try:
        return c.execute("SELECT symbol, dato, tekst FROM notat ORDER BY rowid").fetchall()
    finally:
        c.close()


def _andre_tabeller(base: Path) -> dict:
    c = sqlite3.connect(base)
    try:
        navn = [n for (n,) in c.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name <> 'notat'")]
        return {n: c.execute(f"SELECT * FROM {n} ORDER BY rowid").fetchall() for n in navn}
    finally:
        c.close()


def _bryteren_av(klient) -> None:
    assert klient.post("/innstillinger", data={"navn": "vis_notater", "til": "av"}).status_code in (302, 303)


def _siste_kursdag(base: Path, symbol: str) -> date:
    c = sqlite3.connect(base)
    try:
        return SqliteKurslager(c).serie(symbol)[-1].dato
    finally:
        c.close()


# --- A) Knappen øverst --------------------------------------------------------


class TestKnappen:
    @pytest.mark.parametrize("adresse", SIDENE)
    def test_etter_min_liste_med_ikon_paa_hver_side(self, klient, adresse):
        """Ville feilet hvis knappen manglet på en side, sto et annet sted enn
        rett etter «Min liste», manglet ikonet eller gikk et annet sted enn til
        notatene i Min liste."""
        side = _side(klient, adresse)
        knappen = _knappen(side)
        assert knappen is not None
        assert 'href="/min-liste#mine-notater"' in knappen
        assert '<svg class="ikon"' in knappen and _tekst(knappen) == "Mine notater"
        raden = side[side.index('<nav class="rad sider"') : side.index("</nav>")]
        lenkene = re.findall(r'<a class="sideknapp[^"]*" href="([^"]+)"', raden)
        assert lenkene.index("/min-liste#mine-notater") == lenkene.index("/min-liste") + 1

    @pytest.mark.parametrize("adresse", SIDENE)
    def test_borte_naar_bryteren_er_av(self, klient, adresse):
        """Ville feilet hvis knappen eller panelet sto med «Notater» av."""
        _bryteren_av(klient)
        side = _side(klient, adresse)
        assert _knappen(side) is None
        assert 'id="notatpanel"' not in side


# --- B) Panelet ---------------------------------------------------------------


class TestPanelet:
    @pytest.mark.parametrize("adresse", SIDENE)
    def test_skallet_er_skjult_med_siden_man_staar_paa(self, klient, adresse):
        """Ville feilet hvis panelet sto synlig uten skriptet, eller ikke
        visste hvilken side det skal sende tilbake til."""
        side = _side(klient, adresse)
        skallet = re.search(r'<aside class="notatpanel"[^>]*>', side).group(0)
        assert " hidden" in skallet and 'tabindex="-1"' in skallet
        assert re.search(r'<div class="notatpanel-innhold"></div>\s*<template id="notatpanel-mal">', side)
        assert 'class="panelflytt">Flytt til venstre</button>' in side
        assert 'class="panellukk">Lukk</button>' in side

    def test_alle_notatene_nyeste_foerst_som_i_min_liste(self, klient, base):
        """Ville feilet hvis panelet manglet et notat, hadde en annen
        rekkefølge enn «Mine notater» i Min liste, eller navnet ikke gikk til
        aksjesiden."""
        _notat(base, AKSJE, TIDLIGERE, "eldst")
        _notat(base, ANNEN, SISTE, "nyest")
        _notat(base, AKSJE, date(2026, 10, 5), "midten")
        panelet = _panelet(klient, "/boersometer")
        listen = _side(klient, "/min-liste")
        delen = listen[listen.index('<section class="notater" id="mine-notater"') :]
        delen = delen[: delen.index("</section>")]

        def tekstene(html):
            return re.findall(r'<p class="notattekst">([^<]*)</p>', html)

        assert tekstene(panelet) == ["nyest", "midten", "eldst"] == tekstene(delen)
        assert f'<a href="/aksje/{ANNEN}">' in panelet and f'<a href="/aksje/{AKSJE}">' in panelet
        # Det samme som i Min liste: «Etterpå» og knappene ved hvert notat.
        assert panelet.count('<p class="etterpaa-tittel">Etterpå</p>') == 3
        assert panelet.count('class="slett-notat"') == 3

    def test_uten_notater(self, klient):
        """Ville feilet hvis et tomt panel ikke sa det."""
        assert "Ingen notater ennå." in _tekst(_panelet(klient))

    def test_aa_hente_panelet_skriver_ingenting(self, klient, base):
        """AD-3, AD-10: ville feilet hvis innholdet skrev noe i basen."""
        _notat(base, AKSJE, SISTE, "les")
        foer = (_notatene(base), _andre_tabeller(base))
        for adresse in SIDENE:
            _panelet(klient, adresse)
        assert (_notatene(base), _andre_tabeller(base)) == foer

    @pytest.mark.parametrize("adresse", ["/", "/boersometer?periode=1m", f"/aksje/{AKSJE}?dag=2026-10-01"])
    def test_skjemaene_sender_med_siden_man_staar_paa(self, klient, base, adresse):
        """Ville feilet hvis skjemaene i panelet sendte med en annen side enn
        den man står på, med spørsmålet."""
        _notat(base, AKSJE, SISTE, "x")
        verdiene = set(re.findall(r'name="tilbake" value="([^"]*)"', _panelet(klient, adresse)))
        assert {v.replace("&amp;", "&") for v in verdiene} == {adresse}

    def test_skriptet_henter_ingenting(self):
        """Ville feilet hvis panelet hentet innholdet med fetch eller satte
        det inn som tekst, i stedet for å klone malen fra siden."""
        skriptet = (ROT / "src" / "static" / "hjelp.js").read_text(encoding="utf-8")
        delen = skriptet[skriptet.index("// Story 8.27") :]
        assert "mal.content.cloneNode(true)" in delen
        assert "fetch(" not in delen and "innerHTML" not in delen

    def test_skriptet_og_stilen(self):
        """Ville feilet hvis panelet åpnet seg smalere enn 1056 px, ikke
        husket valgene i localStorage, eller siden ikke ga plass. Selve
        oppførselen er prøvd i Edge (bildene i PR-en)."""
        skriptet = (ROT / "src" / "static" / "hjelp.js").read_text(encoding="utf-8")
        delen = skriptet[skriptet.index("// Story 8.27") :]
        assert 'matchMedia("(min-width: 1056px)")' in delen
        assert '"ose-notatpanel"' in delen and '"ose-notatpanel-side"' in delen
        assert "localStorage" in delen and "sessionStorage" not in delen
        assert 'location.hash === "#notatpanel"' in delen
        stilen = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
        blokk = stilen[stilen.index("/* Story 8.27") :]
        blokk = blokk[blokk.index("@media (min-width: 1056px)") :]
        assert ".notatpanel-aapent body { padding-right: var(--notatpanel); }" in blokk
        assert ".notatpanel-aapent.panel-venstre body { padding-right: 0; padding-left: var(--notatpanel); }" in blokk
        assert ".notatpanel { display: none; }" in stilen


# --- C) Skjemaet i panelet ----------------------------------------------------


class TestSkjemaet:
    def test_paa_aksjesiden_for_aksjen_og_dagen_siden_viser(self, klient, base):
        """Ville feilet hvis notatet fra panelet på aksjesiden fikk en annen
        aksje eller dag, eller svaret gikk til en annen side."""
        side = f"/aksje/{AKSJE}?dag={TIDLIGERE.isoformat()}"
        panelet = _panelet(klient, side)
        skjemaet = re.search(r'<form class="nytt-notat".*?</form>', panelet, re.S).group(0)
        assert f'action="/aksje/{AKSJE}/notat"' in skjemaet
        assert "<select" not in skjemaet
        felt = dict(re.findall(r'name="(dag|vis|tilbake)" value="([^"]*)"', skjemaet))
        assert felt["dag"] == TIDLIGERE.isoformat()
        assert felt["tilbake"].replace("&amp;", "&") == side
        svar = klient.post(f"/aksje/{AKSJE}/notat", data={**felt, "tilbake": side, "tekst": "fra panelet"})
        assert svar.status_code == 303
        assert svar.headers["Location"] == side + "#notatpanel"
        assert _notatene(base) == [(AKSJE, TIDLIGERE.isoformat(), "fra panelet")]

    def test_en_dag_uten_kurs_gir_ikke_skjemaet(self, klient):
        """Som delen nederst: ville feilet hvis panelet tilbød et notat for en
        dag uten kurs (lørdag 03.10)."""
        panelet = _panelet(klient, f"/aksje/{AKSJE}?dag=2026-10-03")
        assert '<form class="nytt-notat"' not in panelet
        assert "har ingen kurs for" in _tekst(panelet)

    def test_utenfor_aksjesiden_med_valget(self, klient, base):
        """Ville feilet hvis valget manglet en aksje i lista med kurser, hadde
        en annen rekkefølge enn navnet, eller notatet fikk en annen aksje
        eller dag enn siste dag med kurs."""
        panelet = _panelet(klient, "/boersometer?periode=1m")
        skjemaet = re.search(r'<form class="nytt-notat".*?</form>', panelet, re.S).group(0)
        assert 'action="/notat"' in skjemaet
        valget = re.findall(r'<option value="([^"]+)">([^<]+)</option>', skjemaet)
        c = sqlite3.connect(base)
        forventet = [
            (s, n)
            for s, n in c.execute("SELECT symbol, navn FROM aksje WHERE ut IS NULL")
            if c.execute("SELECT 1 FROM kurs WHERE symbol = ? LIMIT 1", (s,)).fetchone()
        ]
        c.close()
        assert sorted(valget) == sorted(forventet)
        assert valget == sorted(valget, key=lambda a: app_modul._navnenoekkel(a[1]))
        tilbake = re.search(r'name="tilbake" value="([^"]*)"', skjemaet).group(1)
        svar = klient.post("/notat", data={"symbol": ANNEN, "tekst": "valgt", "tilbake": tilbake})
        assert svar.status_code == 303
        assert svar.headers["Location"] == "/boersometer?periode=1m#notatpanel"
        assert _notatene(base) == [(ANNEN, _siste_kursdag(base, ANNEN).isoformat(), "valgt")]

    def test_skriver_bare_notatet(self, klient, base):
        """AD-3: ville feilet hvis ruta skrev i en annen tabell."""
        foer = _andre_tabeller(base)
        klient.post("/notat", data={"symbol": AKSJE, "tekst": "bare notat", "tilbake": "/"})
        assert _andre_tabeller(base) == foer
        assert len(_notatene(base)) == 1

    @pytest.mark.parametrize(
        ("felt", "kode"),
        [
            ({"tekst": "x"}, 400),
            ({"symbol": "", "tekst": "x"}, 400),
            ({"symbol": "FINNESIKKE", "tekst": "x"}, 404),
            ({"symbol": AKSJE, "tekst": ""}, 400),
            ({"symbol": AKSJE, "tekst": "x" * 281}, 400),
        ],
    )
    def test_ugyldig_gir_feil_og_skriver_ingenting(self, klient, base, felt, kode):
        """Ville feilet hvis et tomt eller ukjent valg, eller en tekst
        notatene ikke godtar, ble skrevet."""
        assert klient.post("/notat", data=felt).status_code == kode
        assert _notatene(base) == []

    def test_en_aksje_som_er_tatt_ut_gir_400(self, klient, base):
        """Som skjemaet på aksjesiden: ville feilet hvis en aksje som er tatt
        ut, kunne få et nytt notat, eller sto i valget."""
        c = sqlite3.connect(base)
        c.execute("UPDATE aksje SET ut = '2026-10-01' WHERE symbol = ?", (ANNEN,))
        c.commit()
        c.close()
        assert klient.post("/notat", data={"symbol": ANNEN, "tekst": "x"}).status_code == 400
        assert f'<option value="{ANNEN}">' not in _panelet(klient, "/boersometer")
        assert _notatene(base) == []

    @pytest.mark.parametrize("tilbake", ["//ondt.example", "/\\ondt.example", "http://ondt.example", "/a\nb"])
    def test_en_adresse_utenfor_appen_gir_aksjesiden(self, klient, base, tilbake):
        """Ville feilet hvis svaret kunne gå til en annen vert."""
        svar = klient.post("/notat", data={"symbol": AKSJE, "tekst": "x", "tilbake": tilbake})
        assert svar.headers["Location"] == f"/aksje/{AKSJE}#mine-notater"

    def test_knappene_ved_notatene_sender_tilbake_til_siden(self, klient, base):
        """Spørsmål 2: ville feilet hvis «Slett» eller et tenkt kjøp i panelet
        sendte til en annen side enn den man sto på, eller uten panelet."""
        _notat(base, AKSJE, SISTE, "kjøp")
        panelet = _panelet(klient, "/min-liste")
        kjoep = re.search(r'<form method="post" action="/aksje/BRFE/notat/kjoep">.*?</form>', panelet, re.S).group(0)
        felt = dict(re.findall(r'name="(id|dag|vis|tilbake)" value="([^"]*)"', kjoep))
        assert felt["tilbake"] == "/min-liste"
        svar = klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=felt)
        assert svar.headers["Location"] == "/min-liste#notatpanel"
        svar = klient.post(f"/aksje/{AKSJE}/notat/slett", data={"id": felt["id"], "tilbake": "/folg"})
        assert svar.headers["Location"] == "/folg#notatpanel"
        assert _notatene(base) == []

    def test_rutene_er_skrivere(self):
        """AD-3: ville feilet hvis ruta ikke var med blant dem som skriver."""
        assert "skriv_notat_valgt" in app_modul._SKRIVERE
        assert "skriv_notat_valgt" in app_modul._RUTER_MED_BASE


# --- D) Demoen ----------------------------------------------------------------


class TestDemoen:
    def test_linja_om_demoen(self, klient, versjon):
        """Ville feilet hvis linja manglet i demoen eller sto i den ekte."""
        linja = "I demoen står notatene til demoen startes på nytt, fordi demobasen lages på nytt da."
        assert (linja in _tekst(_panelet(klient))) == (versjon == "demo")


# --- E) Plassen på aksjesiden (tillegg 1) -------------------------------------


class TestPlassenPaaAksjesiden:
    def test_nederst_etter_historikken_og_investorsiden(self, klient, versjon):
        """Ville feilet hvis «Mine notater» sto over «Signalet dag for dag»
        eller boblen til investorsiden."""
        side = _side(klient, f"/aksje/{AKSJE}")
        notatene = side.index('<section class="notater" id="mine-notater"')
        assert side.index('id="signalet-dag-for-dag"') < notatene
        # Boblen står når aksjen har en investorside, som BRFE i demoen.
        if versjon == "demo":
            assert 'class="investorboble"' in side
        if 'class="investorboble"' in side:
            assert side.index('class="investorboble"') < notatene

    def test_de_to_nyeste_og_vis_alle(self, klient, base):
        """Ville feilet hvis delen viste mer eller mindre enn de to nyeste
        først, eller «Vis alle (N)» manglet et notat."""
        for i, dag in enumerate((date(2026, 10, 1), date(2026, 10, 2), date(2026, 10, 5), date(2026, 10, 6))):
            _notat(base, AKSJE, dag, f"n{i}")
        delen = _delen(_side(klient, f"/aksje/{AKSJE}"))
        foer, _, resten = delen.partition('<details class="alle-notater">')
        assert re.findall(r'<p class="notattekst">([^<]*)</p>', foer) == ["n3", "n2"]
        assert "<summary>Vis alle (4)</summary>" in resten
        assert re.findall(r'<p class="notattekst">([^<]*)</p>', resten) == ["n1", "n0"]
        assert '<form class="nytt-notat"' in foer

    def test_uten_vis_alle_med_to_notater(self, klient, base):
        """Spørsmål 8: ville feilet hvis «Vis alle» sto uten flere notater."""
        _notat(base, AKSJE, TIDLIGERE, "a")
        _notat(base, AKSJE, SISTE, "b")
        delen = _delen(_side(klient, f"/aksje/{AKSJE}"))
        assert "alle-notater" not in delen
        assert delen.count('<p class="notattekst">') == 2
