"""Story 8.2a: seks funn fra gruppens prøve av demoen 24.10 (svarene kl.
11:21–11:49, spesifikasjonen spec-8-2a-funn-fra-proeven-av-demoen.md).

Testene bruker demobasen, laget i tmp_path av fixturen i conftest.py, som
flytter BASE_STI. Ingen nett og ingen henting.
"""

import re
import shutil
import sqlite3
from datetime import datetime, timezone

import pytest

import app as app_modul
import demo
from lagring_sqlite import demo_sti


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    # Som i test_demo.py: datoene på sidene avhenger ikke av året testen kjøres.
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))


@pytest.fixture(scope="module")
def mal(tmp_path_factory):
    sti = tmp_path_factory.mktemp("demomal") / "demo.db"
    demo.lag_demobase(sti, skriv=lambda _: None)
    return sti


@pytest.fixture
def klient(mal, monkeypatch):
    sti = demo_sti()
    sti.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(mal, sti)
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    return app_modul.app.test_client()


def _html(klient, sti: str) -> str:
    svar = klient.get(sti)
    assert svar.status_code == 200, sti
    return svar.get_data(as_text=True)


# a) Siden holder plassen (U35, U36, kl. 11:21).


def test_periodeknappene_og_velg_dag_gaar_til_kursgrafen(klient):
    """Ville feilet hvis en periodeknapp eller «Velg dag» lastet siden uten
    anker, så man havnet øverst, eller ankeret ikke fantes på siden."""
    html = _html(klient, "/aksje/KVST")
    lenker = re.findall(r'href="(/aksje/KVST\?periode=[^"]*)"', html)
    assert len(lenker) >= 6, lenker
    assert all(lenke.endswith(f"#{app_modul.GRAFANKER}") for lenke in lenker), lenker
    skjema = re.search(
        r'<form method="get" action="([^"]*)">\s*<input type="hidden" name="periode" value="velg">', html
    )
    assert skjema and skjema.group(1) == f"/aksje/KVST#{app_modul.GRAFANKER}"
    assert re.search(rf'<h2 id="{app_modul.GRAFANKER}">Kursutvikling', html)
    assert html.count(f'id="{app_modul.GRAFANKER}"') == 1


def test_velg_dag_har_ankeret_ogsaa_med_en_valgt_dag(klient):
    """Ville feilet hvis ankeret bare sto på siden for siste børsdag."""
    html = _html(klient, "/aksje/KVST?periode=velg&dag=2026-10-01")
    assert f'action="/aksje/KVST#{app_modul.GRAFANKER}"' in html
    assert f'id="{app_modul.GRAFANKER}"' in html


@pytest.mark.parametrize(
    ("tilbake", "maal"),
    [
        ("/aksje/KVST", "/aksje/KVST#ki-teksten"),
        ("/aksje/KVST?dag=2026-10-01", "/aksje/KVST?dag=2026-10-01#ki-teksten"),
        ("https://annen.side/", "/"),
        ("/aksje/KVST#annet", "/"),
    ],
)
def test_ki_bryteren_sender_tilbake_til_ki_teksten(klient, tilbake, maal):
    """Ville feilet hvis bryteren sendte tilbake uten anker, så man havnet
    øverst (U35), eller la ankeret på en adresse som ikke godtas."""
    for til in (app_modul.PAA, app_modul.AV):
        svar = klient.post("/ki", data={"til": til, "tilbake": tilbake})
        assert svar.status_code == 303
        assert svar.headers["Location"] == maal


def test_ankeret_for_ki_teksten_finnes_med_bryteren_av_og_paa(klient):
    """Ville feilet hvis ankeret bare fantes med KI-teksten på, så bryteren
    sendte til et anker som ikke er der når teksten skjules, eller fantes
    to ganger."""
    # Bryteren er på uten informasjonskapsel (FR-601).
    paa = _html(klient, "/aksje/KVST")
    assert re.search(rf'<section class="ki" id="{app_modul.KI_ANKER}"', paa)
    klient.set_cookie(app_modul.KAPSEL, app_modul.AV)
    av = _html(klient, "/aksje/KVST")
    assert re.search(rf'<form class="ki-bryter" id="{app_modul.KI_ANKER}"', av)
    for html in (av, paa):
        assert html.count(f'id="{app_modul.KI_ANKER}"') == 1


# b) Hver aksje i lista har en rad (U23, kl. 11:34 og 11:35).


def _radene(html: str) -> list[str]:
    """Radene i tabellen, uten radene med delenes overskrift."""
    tabell = html.split("<table>", 1)[1].split("</table>", 1)[0]
    return [rad for rad in re.findall(r"<tr[ >].*?</tr>", tabell, re.S) if '<td class="selskap">' in rad]


def _synlig(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def test_aksjen_uten_kurser_har_en_rad_nederst_og_ingen_fotnote(klient):
    """Ville feilet hvis Matfjord Merkevarer bare sto i fotnoten (U72), raden
    manglet lenken, «–» eller «uten data», eller ikke sto nederst."""
    html = _html(klient, "/")
    radene = _radene(html)
    assert "Uten data i denne kilden" not in html
    siste = radene[-1]
    assert '<a href="/aksje/MTFJ">Matfjord Merkevarer</a>' in siste
    celler = re.findall(r"<td[^>]*>(.*?)</td>", siste, re.S)
    assert len(celler) == 5
    assert [_synlig(celle) for celle in celler[1:3]] == ["–", "–"]
    assert _synlig(celler[3]) == "– uten data"
    assert _synlig(celler[4]).startswith("–")
    assert sum("Matfjord Merkevarer" in rad for rad in radene) == 1


def test_tallet_i_overskriften_og_linja_under_er_antallet_rader(klient):
    """Ville feilet hvis «7 av 15» talte en aksje som ikke hadde en rad, så
    tabellen hadde 14 rader (U23)."""
    html = _html(klient, "/")
    antall = len(_radene(html))
    assert antall == 15
    assert f"av {antall} aksjer</mark> skilte seg ut" in html
    assert f"· {antall} aksjer</p>" in html


def test_tallet_foelger_lista_naar_en_aksje_legges_til(klient):
    """Ville feilet hvis tallet var fast, så en aksje lagt til lista (2.12)
    ikke fikk en rad eller ikke ble talt."""
    tilkobling = sqlite3.connect(demo_sti())
    try:
        with tilkobling:
            tilkobling.execute(
                "INSERT INTO aksje (symbol, ticker, navn, sektor) VALUES ('NYTT', 'NYTT.OL', 'Nytt Selskap', 'Industri')"
            )
    finally:
        tilkobling.close()
    html = _html(klient, "/")
    radene = _radene(html)
    assert len(radene) == 16 and "av 16 aksjer</mark>" in html and "· 16 aksjer</p>" in html
    assert '<a href="/aksje/NYTT">Nytt Selskap</a>' in "".join(radene[-2:])


def test_aksjen_uten_kurser_har_en_rad_i_min_liste(klient):
    """Ville feilet hvis en merket aksje uten kurser bare sto i en fotnote i
    Min liste, eller ikke ble talt på knappen."""
    foer = _html(klient, "/min-liste")
    antall = int(re.search(r'Min liste <span class="antall">(\d+)</span>', foer).group(1))
    svar = klient.post("/min-liste/merk", data={"symbol": "MTFJ", "til": "merk", "tilbake": "/min-liste"})
    assert svar.status_code == 303
    html = _html(klient, "/min-liste")
    assert f'Min liste <span class="antall">{antall + 1}</span>' in html
    assert '<a href="/aksje/MTFJ">Matfjord Merkevarer</a>' in _radene(html)[-1]
    assert "Uten data i denne kilden" not in html


# c) Symbolene over søylene lenker til aksjesiden (U20, kl. 11:23).


@pytest.mark.parametrize("side", ["/", "/boersometer"])
def test_symbolene_over_soeylene_lenker_til_aksjesiden(klient, side):
    """Ville feilet hvis symbolet over en søyle ikke var en lenke, lenket et
    annet sted enn til aksjen sin, eller lenkene lå i en del som er skjult
    for skjermleseren."""
    html = _html(klient, side)
    figur = html.split('<figure class="soeyler">', 1)[1].split("</figure>", 1)[0]
    etiketter = figur.split('<div class="etiketter">', 1)[1].split("</div>", 1)[0]
    lenker = re.findall(r'<a class="etikett[^"]*" href="/aksje/([A-Z0-9]+)" aria-label="([^"]+)">', etiketter)
    symboler = re.findall(r'<span class="ticker">([A-Z0-9]+)</span>', etiketter)
    assert len(lenker) == len(symboler) == 14
    assert [symbol for symbol, _ in lenker] == symboler
    for symbol, navn in lenker:
        assert navn.endswith(f"({symbol})")
        assert klient.get(f"/aksje/{symbol}").status_code == 200
    foer_etikettene = figur.split('<div class="etiketter">', 1)[0]
    assert 'aria-hidden="true"' not in foer_etikettene.split("</figcaption>", 1)[1]
    assert '<div class="felt" aria-hidden="true">' in figur


# d) Grunnen der signalet ikke kunne regnes (kl. 11:29).


def _tallene_paa_aksjesiden(html: str) -> tuple[str, str]:
    """(fikk, trenger) fra «Trenger M dager for å regne signal, fikk N»."""
    funnet = re.search(r"Trenger (\d+) dager\s+for å regne signal, fikk (\d+)\.", html)
    assert funnet, "aksjesiden sier ikke hvor mange dager"
    return funnet.group(2), funnet.group(1)


@pytest.mark.parametrize("side", ["/", "/min-liste?vis=alle"])
def test_raden_sier_hvorfor_med_samme_tall_som_aksjesiden(klient, side):
    """Ville feilet hvis raden for Varde Systemer bare sa «signalet kunne
    ikke regnes» (U71), eller tallene sprikte fra aksjesiden."""
    fikk, trenger = _tallene_paa_aksjesiden(_html(klient, "/aksje/VRDS"))
    rad = next(rad for rad in _radene(_html(klient, side)) if '<a href="/aksje/VRDS">' in rad)
    celler = re.findall(r"<td[^>]*>(.*?)</td>", rad, re.S)
    assert _synlig(celler[3]) == f"– for kort historikk: {fikk} av {trenger} dager"


@pytest.mark.parametrize("dag", [None, "2026-09-30"])
def test_ruta_i_boersometeret_sier_hvorfor_med_samme_tall(klient, dag):
    """Ville feilet hvis ruta ikke sa hvorfor, eller tallene for en valgt dag
    var de for siste børsdag, ikke de aksjesiden viser for dagen."""
    aksjesiden = "/aksje/VRDS" + (f"?periode=velg&dag={dag}" if dag else "")
    fikk, trenger = _tallene_paa_aksjesiden(_html(klient, aksjesiden))
    html = _html(klient, "/boersometer" + (f"?dag={dag}" if dag else ""))
    ruter = html.split("</figure>", 1)[-1]
    rute = re.search(r'<span class="ticker">VRDS</span>.*?</a>', ruter, re.S).group(0)
    assert f"for kort historikk: {fikk} av {trenger} dager" in _synlig(rute)
    if dag:
        assert int(fikk) < 30


def test_andre_grunner_staar_som_foer():
    """Ville feilet hvis en annen grunn, eller en serie som er lang nok, fikk
    tallene (for_kort_serie på aksjesiden sier dem bare da)."""
    from markedsoversikt import GRUNNTEKST, grunn_med_tall
    from signalberegning import nodvendige_dager
    from tilstand import Art, Tilstand
    from vurderingsdata import Grunn

    trenger = nodvendige_dager()
    ikke_regnet = Tilstand(Art.GRUNN, Grunn.SIGNAL_IKKE_REGNET)
    tekst = GRUNNTEKST[Grunn.SIGNAL_IKKE_REGNET]
    assert grunn_med_tall(ikke_regnet, tekst, trenger - 1) == f"for kort historikk: {trenger - 1} av {trenger} dager"
    assert grunn_med_tall(ikke_regnet, tekst, trenger) == tekst
    assert grunn_med_tall(ikke_regnet, tekst, None) == tekst
    feilet = Tilstand(Art.GRUNN, Grunn.SYMBOL_FEILET)
    assert grunn_med_tall(feilet, GRUNNTEKST[Grunn.SYMBOL_FEILET], 3) == GRUNNTEKST[Grunn.SYMBOL_FEILET]
    assert grunn_med_tall(None, "ikke vurdert", 3) == "ikke vurdert"


# e) Én liste når man sorterer (kl. 11:39).


def _symbolene(html: str) -> list[str]:
    return [re.search(r'<span class="linje">([A-Z0-9]+)', rad).group(1) for rad in _radene(html)]


@pytest.mark.parametrize("orden", ["synkende", "stigende"])
def test_sortert_er_hele_lista_en_liste_uten_delene(klient, orden):
    """Ville feilet hvis sorteringen gjaldt innenfor hver del (U73), så en
    rad under «Øvrige aksjer» med større endring sto under en som skilte
    seg ut, eller raden uten data ikke sto sist."""
    html = _html(klient, f"/?sorter=endring&orden={orden}")
    tabell = html.split("<table>", 1)[1].split("</table>", 1)[0]
    assert "Skilte seg ut" not in tabell and "Øvrige aksjer" not in tabell
    assert tabell.count("<tbody>") == 1
    radene = _radene(html)
    assert len(radene) == 15 and _symbolene(html)[-1] == "MTFJ"
    endringer = [
        float(_synlig(re.findall(r"<td[^>]*>(.*?)</td>", rad, re.S)[2]).replace("%", "").strip().replace(",", "."))
        for rad in radene[:-1]
    ]
    assert endringer == sorted(endringer, reverse=orden == "synkende")
    assert f"Sortert på endring, {orden}, i én liste." in html
    assert "innenfor hver del" not in html


def test_de_som_skilte_seg_ut_beholder_kanten(klient):
    """Ville feilet hvis kanten fulgte delen, så den forsvant i én liste."""
    standard = _html(klient, "/")
    sortert = _html(klient, "/?sorter=kurs&orden=synkende")
    med_kant = lambda html: {
        re.search(r'<span class="linje">([A-Z0-9]+)', rad).group(1)
        for rad in _radene(html)
        if re.match(r'<tr class="utslag', rad)
    }
    assert len(med_kant(standard)) == 7
    assert med_kant(sortert) == med_kant(standard)


def test_standardrekkefoelgen_har_delene_som_foer(klient):
    """Ville feilet hvis delene forsvant også uten en valgt kolonne."""
    html = _html(klient, "/")
    assert "Skilte seg ut" in html and "Øvrige aksjer" in html
    assert '<p class="sortert">' not in html


def test_min_liste_sortert_er_en_liste_med_bare_de_merkede(klient):
    """Ville feilet hvis Min liste sorterte innenfor hver del, eller viste
    aksjer som ikke er merket når lista er sortert."""
    standard = _html(klient, "/min-liste")
    merkede = set(_symbolene(standard))
    html = _html(klient, "/min-liste?sorter=selskap&orden=stigende")
    tabell = html.split("<table>", 1)[1].split("</table>", 1)[0]
    assert "Skilte seg ut" not in tabell and "Øvrige aksjer" not in tabell
    assert set(_symbolene(html)) == merkede
    navn = [re.search(r'<a href="/aksje/[A-Z0-9]+">([^<]+)</a>', rad).group(1) for rad in _radene(html)]
    assert navn == sorted(navn, key=lambda n: n.casefold().translate(str.maketrans({"æ": "{", "ø": "|", "å": "}"})))
    alle = _html(klient, "/min-liste?vis=alle&sorter=endring&orden=synkende")
    assert len(_radene(alle)) == 15 and _symbolene(alle)[-1] == "MTFJ"
