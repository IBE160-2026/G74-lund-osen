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
        delen = skriptet[skriptet.index("// Story 8.27 (gruppens svar") :]
        assert "mal.content.cloneNode(true)" in delen
        assert "fetch(" not in delen and "innerHTML" not in delen

    def test_skriptet_og_stilen(self):
        """Ville feilet hvis panelet åpnet seg smalere enn 1056 px, ikke
        husket valgene i localStorage, eller siden ikke ga plass. Selve
        oppførselen er prøvd i Edge (bildene i PR-en)."""
        skriptet = (ROT / "src" / "static" / "hjelp.js").read_text(encoding="utf-8")
        delen = skriptet[skriptet.index("// Story 8.27 (gruppens svar") :]
        assert 'matchMedia("(min-width: 1056px)")' in delen
        assert '"ose-notatpanel"' in skriptet and '"ose-notatpanel-side"' in skriptet
        assert "localStorage" in delen and "sessionStorage" not in delen
        assert "const fraSkjema = location.hash === P.ANKER;" in delen
        stilen = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
        blokk = stilen[stilen.index("/* Story 8.27") :]
        blokk = blokk[blokk.index("@media (min-width: 1056px)") :]
        assert ".notatpanel-aapent body { padding-right: var(--notatpanel); }" in blokk
        assert ".notatpanel-aapent.panel-venstre body { padding-right: 0; padding-left: var(--notatpanel); }" in blokk
        assert ".notatpanel { display: none; }" in stilen


class TestRaden:
    """Gruppens svar 13.11 kl. 10:18: de sju knappene står på én rad ved
    1280 px med mindre luft, og klikkflaten blir ikke lavere. Bredden er målt
    i Edge (998 av 1008 px); her prøves regelen."""

    def test_mindre_luft_fra_1056_px_og_samme_hoeyde(self):
        """Ville feilet hvis knappene hadde mindre luft også på smal skjerm,
        mer luft enn det som ble målt, mindre luft mellom radene når raden
        brytes, en lavere klikkflate, eller en senere regel tok luften
        tilbake."""
        stilen = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
        start = stilen.index("/* Story 8.27, raden")
        blokk = stilen[start:]
        blokk = blokk[: blokk.index("\n}") + 2]
        media = blokk[blokk.index("@media (min-width: 1056px) {") :]
        assert "header.stripe .sider { column-gap: 6px; }" in media
        assert "header.stripe .sideknapp { padding: 0 8px; }" in media
        assert "min-height" not in media and "row-gap" not in media
        assert "header.stripe .sider { flex-wrap: wrap; gap: 8px; padding-bottom: 12px; }" in stilen
        assert "min-height: 44px; padding: 0 16px;" in stilen
        etter = stilen[start + len(blokk) :]
        assert not re.search(r"\.sideknapp\s*\{[^}]*padding|\.sider\s*\{[^}]*gap", etter)

    def test_raden_har_sju_knapper(self, klient, versjon):
        """Ville feilet hvis raden hadde en annen knapp enn de sju som ble
        målt, i demoen eller i den ekte versjonen."""
        for adresse in SIDENE:
            side = _side(klient, adresse)
            raden = side[side.index('aria-label="Sidene"') :]
            raden = raden[: raden.index("</nav>")]
            assert len(re.findall(r'class="sideknapp\b', raden)) == 7, adresse


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
        svar = klient.post("/notat", data={"symbol": AKSJE, "tekst": "bare notat", "tilbake": "/"})
        assert svar.status_code == 303 and svar.headers["Location"] == "/#notatpanel"
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


# --- F) Steget i omvisningen (tillegg 2) -------------------------------------


def _vis_meg_rundt(side: str) -> list[dict] | None:
    """Stegene i «Vis meg rundt» på siden (_rundtur.html), eller None."""
    import html
    import json

    treff = re.search(r'class="sideknapp vis-meg-rundt" data-steg="([^"]*)"', side)
    return json.loads(html.unescape(treff.group(1))) if treff else None


def _omvisningen(side: str) -> list[dict]:
    """Stegene i den hele omvisningen, fra rammen (8.25)."""
    import html
    import json

    treff = re.search(r'<div id="omvisning" hidden data-side="[^"]*" data-steg="([^"]*)"', side)
    assert treff, "omvisningen mangler"
    return json.loads(html.unescape(treff.group(1)))


NOTATSTEGET = (
    "Mine notater åpner et panel i kanten av siden med alle notatene dine, og et skjema for et nytt notat. "
    "Panelet kan flyttes til venstre eller høyre. Notatene lagres på denne maskinen."
)
NOTATSTEGET_DEMO = NOTATSTEGET[:-1] + ", i demoen til den startes på nytt."


class TestSteget:
    """Tillegg 2 (gruppens svar 11.11 kl. 22:20), etter forslaget i spørsmål
    13, godtatt 12.11 kl. 10:16."""

    def test_sist_i_vis_meg_rundt_for_min_liste(self, klient, versjon):
        """Ville feilet hvis steget manglet i «Vis meg rundt» for Min liste,
        ikke sto sist der, pekte på noe annet enn knappen øverst, eller hadde
        feil tekst i demoen eller i den ekte versjonen."""
        side = _side(klient, "/min-liste")
        stegene = _vis_meg_rundt(side)
        assert stegene is not None
        assert stegene[-1] == {
            "anker": "notatknapp",
            "tittel": "Mine notater",
            "tekst": NOTATSTEGET_DEMO if versjon == "demo" else NOTATSTEGET,
        }
        assert [s["anker"] for s in stegene].count("notatknapp") == 1
        # Ankeret er knappen øverst, så skriptet finner den.
        assert 'id="notatknapp"' in _knappen(side)

    def test_i_omvisningen_etter_min_liste_og_foer_foelg_en_aksje(self, klient, versjon):
        """Ville feilet hvis steget manglet i den hele omvisningen, sto på en
        annen side enn Min liste, eller ikke sto rett før «Følg en aksje»."""
        stegene = _omvisningen(_side(klient, "/"))
        sidene = [s["side"] for s in stegene]
        i = [s["anker"] for s in stegene].index("notatknapp")
        assert stegene[i]["side"] == "min_liste"
        assert sidene[i + 1] == "folg" and sidene[i - 1] == "min_liste"
        assert stegene[i]["tekst"] == (NOTATSTEGET_DEMO if versjon == "demo" else NOTATSTEGET)
        assert [s["anker"] for s in stegene].count("notatknapp") == 1

    @pytest.mark.parametrize("adresse", ["/", "/boersometer", f"/aksje/{AKSJE}", "/innstillinger", "/folg"])
    def test_ikke_paa_de_andre_sidene(self, klient, adresse):
        """Ville feilet hvis steget sto i «Vis meg rundt» på en annen side enn
        Min liste, så lista der ble lengre."""
        stegene = _vis_meg_rundt(_side(klient, adresse))
        assert stegene is not None, adresse
        assert "notatknapp" not in [s["anker"] for s in stegene]

    def test_borte_naar_bryteren_er_av(self, klient):
        """Ville feilet hvis steget sto i «Vis meg rundt» eller i omvisningen
        med «Notater» av, der knappen er borte og telleren ville telt et steg
        som ikke vises."""
        _bryteren_av(klient)
        side = _side(klient, "/min-liste")
        assert "notatknapp" not in [s["anker"] for s in _vis_meg_rundt(side) or []]
        assert "notatknapp" not in [s["anker"] for s in _omvisningen(side)]
        assert "notatknapp" not in [s["anker"] for s in _omvisningen(_side(klient, "/"))]

    def test_ingen_raad_i_teksten(self):
        """NFR-06: ville feilet hvis steget sa kjøp, selg eller anbefal."""
        for tekst in (NOTATSTEGET, NOTATSTEGET_DEMO):
            assert not re.search(r"(kjøp|selg|anbefal)", tekst.lower())


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


# --- Gjennomgangen ------------------------------------------------------------


class TestGjennomgangen:
    def test_en_basefeil_i_panelet_gir_siden_uten_notater(self, klient, monkeypatch):
        """BH2: ville feilet hvis en basefeil mens panelet ble laget, ga 500."""

        def feil(*_a, **_k):
            raise sqlite3.OperationalError("database is locked")

        monkeypatch.setattr(app_modul, "_alle_notatene", feil)
        side = _side(klient, "/boersometer")
        assert "Notatene kan ikke leses fra basen nå." in _tekst(_malen(side))
        assert '<form class="nytt-notat"' not in _malen(side)

    def test_stien_kommer_tilbake_som_den_var(self):
        """BH4: ville feilet hvis en sti med mellomrom eller æøå ga en
        tilbake-adresse appen avviser, så svaret gikk til aksjesiden."""
        for sti, sporsmaal in (("/folg", "q=a%20b"), ("/a b", ""), ("/børs", "x=1")):
            with app_modul.app.test_request_context(sti, query_string=sporsmaal):
                her = app_modul._her()
                assert app_modul._panelsiden(her) == her, her
                assert " " not in her

    def test_vis_alle_er_aapen_etter_et_trykk_paa_et_notat_der(self, klient, base):
        """BH5: ville feilet hvis «Vis alle» var lukket etter et trykk på et
        notat under den, eller åpen etter et trykk på et av de to nyeste."""
        for i, dag in enumerate((date(2026, 10, 1), date(2026, 10, 2), date(2026, 10, 5))):
            _notat(base, AKSJE, dag, f"n{i}")
        delen = _delen(_side(klient, f"/aksje/{AKSJE}"))
        nede = delen[delen.index('<details class="alle-notater"') :]
        slett = re.search(r'<form class="slett-notat".*?</form>', nede, re.S).group(0)
        felt = dict(re.findall(r'name="(id|vis|alle)" value="([^"]*)"', slett))
        assert felt["alle"] == "1"
        svar = klient.post(f"/aksje/{AKSJE}/notat/slett", data=felt)
        assert svar.headers["Location"] == f"/aksje/{AKSJE}?alle=1#mine-notater"
        assert '<details class="alle-notater" open>' not in _side(klient, f"/aksje/{AKSJE}")
        _notat(base, AKSJE, date(2026, 10, 6), "n3")
        assert '<details class="alle-notater" open>' in _side(klient, f"/aksje/{AKSJE}?alle=1")
        oppe = _delen(_side(klient, f"/aksje/{AKSJE}")).split('<details class="alle-notater"')[0]
        assert 'name="alle"' not in oppe

    def test_navnene_sorteres_som_i_norsk(self):
        """BH12: ville feilet hvis æ, ø og å ikke kom etter z, eller en
        bokstav med aksent kom etter å."""
        navn = ["Åker", "Ørje", "Élkem", "Zeta", "Ærfugl", "alfa", "Ünder"]
        assert sorted(navn, key=app_modul._navnenoekkel) == ["alfa", "Élkem", "Ünder", "Zeta", "Ærfugl", "Ørje", "Åker"]


# --- Gjennomgangen: Edge Case Hunter og Verification Gap -----------------------

NODE = shutil.which("node")
SKRIPTET = ROT / "src" / "static" / "hjelp.js"


@pytest.mark.skipif(NODE is None, reason="Node finnes ikke på maskinen")
class TestPanelskriptetMedNode:
    """VG2 og VG3: avgjørelsene i panelet (NOTATPANEL i hjelp.js), kjørt med
    Node uten en side, som omvisningen i 8.25."""

    def _kjoer(self, uttrykk: str):
        import json
        import subprocess

        kode = f"const P = require({json.dumps(str(SKRIPTET))}).NOTATPANEL; console.log(JSON.stringify({uttrykk}));"
        svar = subprocess.run([NODE, "-e", kode], capture_output=True, text=True, timeout=60)
        assert svar.returncode == 0, svar.stderr
        return json.loads(svar.stdout)

    def test_bare_fra_1056_px_og_bare_aapent(self):
        """Ville feilet hvis panelet sto smalere enn 1056 px, eller uten å
        være åpent."""
        uttrykk = "[P.synlig(true, true), P.synlig(true, false), P.synlig(false, true)]"
        assert self._kjoer(uttrykk) == [True, False, False]

    def test_husket_som_aapent_eller_fra_et_skjema(self):
        """Ville feilet hvis valget ikke ble lest ved start, eller panelet
        ikke sto åpent etter lagring (#notatpanel)."""
        uttrykk = (
            '[P.aapentVedStart("ja", ""), P.aapentVedStart(null, "#notatpanel"), P.aapentVedStart(null, ""), '
            'P.aapentVedStart("nei", "#annet")]'
        )
        assert self._kjoer(uttrykk) == [True, True, False, False]

    def test_knappen_og_flytt_lagrer_valgene(self):
        """Ville feilet hvis knappen ikke lagret at panelet er åpent, eller
        «Flytt» ikke byttet side og tekst."""
        assert self._kjoer("[P.etterKnappen(true), P.etterKnappen(false)]") == ["ja", None]
        uttrykk = '[P.flytt(false), P.flytt(true), P.venstre("venstre"), P.venstre("hoeyre"), P.venstre(null)]'
        assert self._kjoer(uttrykk) == ["venstre", "hoeyre", True, False, False]
        assert self._kjoer("[P.flyttTekst(true), P.flyttTekst(false)]") == ["Flytt til høyre", "Flytt til venstre"]
        assert self._kjoer("[P.AAPENT, P.SIDEN, P.ANKER]") == ["ose-notatpanel", "ose-notatpanel-side", "#notatpanel"]

    def test_esc_lukker_bare_den_oeverste(self):
        """ECH4: ville feilet hvis Esc lukket panelet mens hjelpen eller
        omvisningen var åpen, når fokus ikke var i panelet, eller når en
        annen kontroll hadde brukt tasten."""
        uttrykk = (
            '[P.escLukker("Escape", false, false, true, false), P.escLukker("Escape", false, false, true, true), '
            'P.escLukker("Escape", false, false, false, false), P.escLukker("Escape", true, false, true, false), '
            'P.escLukker("Escape", false, true, true, false), P.escLukker("Enter", false, false, true, false)]'
        )
        assert self._kjoer(uttrykk) == [True, False, False, False, False, False]

    def test_skriptet_bruker_avgjoerelsene(self):
        """Ville feilet hvis skriptet for siden gikk forbi avgjørelsene over,
        eller lyttet etter Esc etter hjelpen (ECH4)."""
        skriptet = SKRIPTET.read_text(encoding="utf-8")
        delen = skriptet[skriptet.index("// Story 8.27 (gruppens svar") :]
        for bruk in (
            "P.synlig(aapen, BRED.matches)",
            "P.aapentVedStart(les(P.AAPENT)",
            "P.etterKnappen(panel.hidden)",
            "P.flytt(rot.classList.contains",
            "P.escLukker(e.key",
        ):
            assert bruk in delen, bruk
        assert re.search(r"P\.escLukker\(.*?\)\) \{\s*lukk\(\);\s*\}\s*\},\s*true,", delen, re.S)


class TestStilen:
    def test_hjelpen_staar_over_panelet(self):
        """Spørsmål 1, VG3: ville feilet hvis hjelpen åpnet seg på den andre
        siden mens panelet er åpent, siden ga plass til to felt, eller «Flytt»
        i hjelpen sto."""
        stilen = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
        blokk = stilen[stilen.index("/* Story 8.27") :]
        for regel in (
            ".hjelpefelt.notatpanel-aapent .hjelpevindu { inset: 16px 16px 16px auto; }",
            ".hjelpefelt.notatpanel-aapent.panel-venstre .hjelpevindu { inset: 16px auto 16px 16px; }",
            ".hjelpefelt.notatpanel-aapent body:has(.hjelpevindu:popover-open) "
            "{ padding-right: var(--notatpanel); padding-left: 0; }",
            ".hjelpefelt.notatpanel-aapent .hjelpevindu button.flytt { display: none; }",
        ):
            assert regel in blokk, regel
        # Reglene står etter reglene for hjelpefeltet, så de vinner.
        foerst = stilen.index(".hjelpefelt.felt-venstre .hjelpevindu")
        assert foerst < stilen.index(".hjelpefelt.notatpanel-aapent .hjelpevindu")


class TestReglerIPanelet:
    def test_ingen_kjoep_naar_siden_viser_en_tidligere_dag(self, klient, base):
        """ECH1, VG4: ville feilet hvis panelet hadde «Noter et tenkt kjøp» på
        en side for en tidligere dag, som aksjesiden og Min liste ikke har."""
        _notat(base, AKSJE, SISTE, "k")
        assert "/notat/kjoep" in _panelet(klient, f"/aksje/{AKSJE}")
        for adresse in (f"/aksje/{AKSJE}?dag=2026-10-01", "/min-liste?dag=2026-10-01"):
            panelet = _panelet(klient, adresse)
            assert "/notat/kjoep" not in panelet, adresse
            assert "knappene står når siden viser siste børsdag" in _tekst(panelet)

    def test_ingen_kjoep_for_en_aksje_som_er_tatt_ut(self, klient, base):
        """VG4, VG9: ville feilet hvis panelet tillot et kjøp eller et nytt
        notat for en aksje som er tatt ut."""
        _notat(base, ANNEN, SISTE, "ut")
        c = sqlite3.connect(base)
        c.execute("UPDATE aksje SET ut = '2026-10-01' WHERE symbol = ?", (ANNEN,))
        c.commit()
        c.close()
        assert f"/aksje/{ANNEN}/notat/kjoep" not in _panelet(klient, "/")
        panelet = _panelet(klient, f"/aksje/{ANNEN}")
        assert '<form class="nytt-notat"' not in panelet
        assert "er tatt ut av lista" in _tekst(panelet)

    def test_en_aksje_uten_kurser(self, klient, base):
        """ECH3, VG6: ville feilet hvis panelet på siden for en aksje uten
        kurser bød fram valget, eller /notat skrev et notat for den."""
        c = sqlite3.connect(base)
        c.execute("DELETE FROM kurs WHERE symbol = ?", (ANNEN,))
        c.commit()
        c.close()
        panelet = _panelet(klient, f"/aksje/{ANNEN}")
        assert "<select" not in panelet and '<form class="nytt-notat"' not in panelet
        assert "har ingen kurser ennå" in _tekst(panelet)
        assert f'<option value="{ANNEN}">' not in _panelet(klient, "/")
        assert klient.post("/notat", data={"symbol": ANNEN, "tekst": "x"}).status_code == 400
        assert _notatene(base) == []

    @pytest.mark.parametrize("tilbake", ["//ondt.example", "http://ondt.example", "/a\tb", "/" + "a" * 2048])
    def test_ugyldig_tilbake_ved_slett_gir_den_gamle_veien(self, klient, base, tilbake):
        """VG7: ville feilet hvis «Slett» godtok en adresse utenfor appen."""
        _notat(base, AKSJE, SISTE, "s")
        notat_id = str(_id(base))
        svar = klient.post(f"/aksje/{AKSJE}/notat/slett", data={"id": notat_id, "vis": "min-liste", "tilbake": tilbake})
        assert svar.headers["Location"] == "/min-liste#mine-notater"

    def test_en_gyldig_tilbake_gaar_foran_min_liste(self, klient, base):
        """VG7: ville feilet hvis vis=min-liste gikk foran siden man sto på."""
        _notat(base, AKSJE, SISTE, "s")
        data = {"id": str(_id(base)), "vis": "min-liste", "tilbake": "/boersometer"}
        svar = klient.post(f"/aksje/{AKSJE}/notat/slett", data=data)
        assert svar.headers["Location"] == "/boersometer#notatpanel"


def _id(base: Path) -> int:
    c = sqlite3.connect(base)
    try:
        return c.execute("SELECT id FROM notat").fetchone()[0]
    finally:
        c.close()
