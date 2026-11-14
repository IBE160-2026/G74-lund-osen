"""Story 8.29: «Din egen liste: kom i gang» som tavla, og investorknappen 44 px.

Gruppens svar 13.11 kl. 10:32-10:54, med tavla «Min liste» 13.10, og tillegg 1
(svarene kl. 10:59-11:02): én overskrift, titlene og teksten i kortene med
linjehøyde, brikkene i steg 3, setningen i steg 2, delen uten ramme, egen
bakgrunn og luft på sidene, bransjekortene stablet i kolonner, og knappen til
investorsiden minst 44 px høy. Spesifikasjonen er
spec-8-29-din-egen-liste-kom-i-gang.md. Demoen og den ekte versjonen bygges
under tmp_path (regel 22), og ingen test gjør nettkall (AD-8).

Gjennomgangen (ECH1): klient setter OSE_DEMO og ekte tar den bort, så en test
ber om bare én av dem, med request.getfixturevalue.
"""

import os
import re
from pathlib import Path

import pytest

from test_historikken import base  # noqa: F401  (fiksturen, gjennomgangen VG1)
from test_hjelpefeltet import NETTLESER, _kjoer
from test_vis_meg_rundt_8_26 import ekte, klient, mal  # noqa: F401  (fiksturene)

ROT = Path(__file__).resolve().parents[1]
STIL = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
I_NETTLESER = pytest.mark.skipif(NETTLESER is None and not os.environ.get("CI"), reason="ingen Edge eller Chrome")
SETNINGEN = (
    "Nøkkelen står på kontosiden hos EODHD. Startskriptet til den ekte versjonen spør etter den første gang,"
    " og den lagres bare på denne maskinen."
)
VERSJONENE = pytest.mark.parametrize("hvilken", ("klient", "ekte"))


def _side(k, adresse: str) -> str:
    svar = k.get(adresse)
    assert svar.status_code == 200, adresse
    return svar.get_data(as_text=True)


def _delen(side: str) -> str:
    return side.split('<section class="egne" id="din-egen-liste"', 1)[1].split("</ol>", 1)[0]


def _versjonen(request, hvilken: str):
    """Klienten for demoen eller den ekte versjonen, og bare den (ECH1)."""
    k = request.getfixturevalue(hvilken)
    side = _side(k, "/min-liste")
    assert ("Eksempeltall" in side) == (hvilken == "klient"), "feil versjon"
    return k, side


class TestOverskriften:
    @VERSJONENE
    def test_en_h2_med_id_en_delen_viser_til(self, request, hvilken):
        """Ville feilet hvis delen hadde mer enn én h2, overskriften ikke var
        «Din egen liste: kom i gang» med id-en i aria-labelledby, eller
        overskriften «Din egen liste» og setningen under sto igjen."""
        _, side = _versjonen(request, hvilken)
        delen = _delen(side)
        assert 'aria-labelledby="egen-liste-tittel"' in side
        assert re.findall(r"<h2[^>]*>(.*?)</h2>", delen) == ["Din egen liste: kom i gang"]
        assert '<h2 id="egen-liste-tittel">Din egen liste: kom i gang</h2>' in delen
        assert not re.search(r">\s*Din egen liste\s*<", side)
        assert "<h3>Din egen liste: kom i gang</h3>" not in side
        assert "Vil du følge helt andre aksjer" not in side
        assert "Appen kjører på din egen maskin, så det finnes ingen innlogging hos oss." in delen

    @VERSJONENE
    def test_overskriftene_gaar_h2_h3_h4(self, request, hvilken):
        """Gjennomgangen (BH1). Ville feilet hvis titlene i stegkortene hoppet
        fra h2 til h4."""
        _, side = _versjonen(request, hvilken)
        assert re.findall(r'<span class="stegnummer" aria-hidden="true">\d</span><(h\d)>', _delen(side)) == ["h3"] * 3

    def test_overskriften_i_stilen(self):
        """Ville feilet hvis overskriften ikke var 32 px med vekt 500 (Newsreader
        kommer fra h2 i hele appen)."""
        assert ":where(.side-oversikt) #din-egen-liste > h2 { margin: 0; font-size: 32px; font-weight: 500; }" in STIL
        assert 'h1, h2 { font-family: "Newsreader", Georgia, serif; font-weight: 500; }' in STIL


class TestKortene:
    @VERSJONENE
    def test_setningen_i_steg_2_og_ingen_felt(self, request, hvilken):
        """Ville feilet hvis steg 2 ikke sa at startskriptet spør etter
        nøkkelen, sa den gamle setningen, eller fikk et felt (AD-10)."""
        _, side = _versjonen(request, hvilken)
        delen = _delen(side)
        assert SETNINGEN in delen
        assert "EODHD. Den lagres bare på denne maskinen." not in delen
        assert "<input" not in delen and "<form" not in delen

    def test_titlene_teksten_og_kortene_i_stilen(self):
        """Ville feilet hvis titlene ikke var 21 px med linjehøyde 1,2, teksten
        16 px med 1,5 (ikke avsnittet med knappen, ECH5), eller stegkortene ikke
        hadde luften, hjørnene og avstanden fra tavla."""
        for regel in (
            "#din-egen-liste .kort-steg .steg-topp h3 { font-size: 21px; line-height: 1.2; }",
            "#din-egen-liste .kort-steg p:not(.handling) { font-size: 16px; line-height: 1.5; }",
            "#din-egen-liste .stegkort { gap: 14px; }",
            "#din-egen-liste .kort-steg { padding: 18px 18px 20px; border-radius: 14px; }",
        ):
            assert f":where(.side-oversikt) {regel}" in STIL, regel

    def test_brikkene_i_stilen(self):
        """Ville feilet hvis brikkene i steg 3 ikke var minst 30 px høye, med
        12 px luft, 13 px tekst med vekt 600, 6 px mellom og ikonet 13 px, eller
        hadde en fast høyde teksten kunne gå ut av (BH2, ECH2)."""
        brikken = re.search(r":where\(\.side-oversikt\) #din-egen-liste \.ferdigknapp \{([^}]*)\}", STIL).group(1)
        for del_ in ("min-height: 30px", "padding: 0 12px", "font-size: 13px", "font-weight: 600", "gap: 6px"):
            assert del_ in brikken, del_
        assert not re.search(r"(?<!min-)height:", brikken)
        assert ":where(.side-oversikt) #din-egen-liste .ferdige-knapper { gap: 6px; }" in STIL
        assert (
            ":where(.side-oversikt) #din-egen-liste .ferdigknapp .bransjesymbol { width: 13px; height: 13px; }" in STIL
        )

    def test_delen_uten_ramme_bakgrunn_og_luft_paa_sidene(self):
        """Tillegg 1. Ville feilet hvis delen hadde ramme, egen bakgrunn eller
        luft på sidene, eller «Dine egne aksjer» på oversikten mistet kortet."""
        assert (
            ":where(.side-oversikt) #din-egen-liste { padding: 21px 0; background: none; border: none; border-radius: 0; }"
            in STIL
        )
        assert ":where(.side-oversikt) .egne { margin: 40px 0 8px; padding: 20px 22px; background: var(--kort);" in STIL

    def test_bransjekortene_i_kolonner(self):
        """Tillegg 1. Ville feilet hvis kortene sto i rader med hull, kunne
        deles mellom to kolonner, eller kolonnene var smalere enn 260 px."""
        assert ":where(.side-oversikt) .bransjekort { columns: 3 260px; column-gap: 16px; }" in STIL
        kortet = re.search(r":where\(\.side-oversikt\) \.bransjekortet \{([^}]*)\}", STIL).group(1)
        assert "break-inside: avoid" in kortet and "margin: 0 0 16px" in kortet
        assert ":where(.side-oversikt) .bransjekortet:last-child { margin-bottom: 0; }" in STIL
        assert "grid-template-columns: repeat(3" not in STIL.split(".bransjekort {", 1)[1].split("}", 1)[0]


# Målt i nettleseren, med siden fra appen og stilen fra static/ (test_hjelpefeltet).
MAAL_DELEN = r"""
const s = document.querySelector('#din-egen-liste');
const r = (e) => e.getBoundingClientRect();
const cs = getComputedStyle(s), h2 = s.querySelector('h2'), h2s = getComputedStyle(h2);
const naboen = document.querySelector('#mine-notater') || document.querySelector('main table');
const titler = [...s.querySelectorAll('.steg-topp h3')].map((h) => [parseFloat(getComputedStyle(h).lineHeight), r(h).height]);
const brikker = [...s.querySelectorAll('.ferdigknapp')].map((b) => [r(b).height, b.scrollHeight <= b.clientHeight + 1]);
const kort = [...s.querySelectorAll('.bransjekortet')].map((k) => [Math.round(r(k).left), r(k).top, r(k).bottom]);
const hvite = [...s.querySelectorAll('.kort-steg, .bransjekortet')].every((k) => getComputedStyle(k).backgroundColor === 'rgb(255, 255, 255)');
const rekkefoelgen = [...s.querySelectorAll('.bransjekortet h4')].map((h) => h.textContent.trim());
const kolonne = s.querySelector('.bransjekort');
// Målt før fokus, som ruller siden.
const under = kolonne ? Math.round(r(kolonne).bottom - Math.max(...kort.map((k) => k[2]))) : null;
const delen = [Math.round(r(s).left), Math.round(r(s).right)];
let fokus = null;
const knapp = s.querySelector('.ferdigknapp') || s.querySelector('.handling .knapp');
if (knapp) { knapp.focus(); const f = getComputedStyle(knapp); fokus = [knapp.matches(':focus-visible'), f.outlineStyle, f.outlineWidth]; }
ferdig({h2: s.querySelectorAll('h2').length, h2stil: [h2s.fontSize, h2s.fontWeight, h2s.fontFamily.split(',')[0]],
        bakgrunn: cs.backgroundColor, kant: cs.borderTopWidth,
        delen,
        naboen: naboen ? [Math.round(r(naboen).left), Math.round(r(naboen).right)] : null,
        titler, brikker, kort, hvite, rekkefoelgen, fokus,
        under,
        rulling: document.documentElement.scrollWidth > document.documentElement.clientWidth});
"""


@I_NETTLESER
@VERSJONENE
@pytest.mark.parametrize("bredde,kolonner", ((1280, 3), (700, 2), (390, 1)))
def test_delen_i_nettleseren(request, tmp_path, hvilken, bredde, kolonner):
    """Ville feilet hvis delen hadde mer enn én h2 eller ikke var 32 px med
    vekt 500 i Newsreader, hadde en ramme eller egen bakgrunn, ikke sto i
    linje med tabellen eller «Mine notater» (136-1144 px ved 1280 px), kortene
    ikke var hvite, en tittel som brytes ble skrevet oppå seg selv (linjehøyde
    1,2), en brikke var lavere enn 24 px eller teksten gikk ut av den (WCAG
    2.5.8), fokusringen manglet, bransjekortene ikke sto i tre kolonner ved
    1280 px, to ved 700 og én ved 390, et kort ikke startet 16 px under kortet
    over i samme kolonne, det var luft under det siste kortet, eller
    rekkefølgen i HTML-en var en annen. Med testdataene (BH5): demoen har åtte
    bransjekort og den ekte versjonen like mange, nok til tre kolonner."""
    k, side = _versjonen(request, hvilken)
    rekkefoelgen = [
        re.sub(r"\s+\d+$", "", re.sub(r"<[^>]+>", "", h).strip())
        for h in re.findall(r'<h4 id="flere-\d+">(.*?)</h4>', side, re.S)
    ]
    r = _kjoer(side, tmp_path, bredde, MAAL_DELEN)
    assert r["h2"] == 1 and r["h2stil"] == ["32px", "500", "Newsreader"], r["h2stil"]
    assert r["kant"] == "0px" and r["bakgrunn"] == "rgba(0, 0, 0, 0)" and r["hvite"], r
    assert not r["rulling"]
    assert r["naboen"] and abs(r["delen"][0] - r["naboen"][0]) <= 1 and abs(r["delen"][1] - r["naboen"][1]) <= 1, r
    if bredde == 1280:
        assert r["delen"] == [136, 1144], r["delen"]
    for linje, hoeyde in r["titler"]:
        assert linje == pytest.approx(25.2, abs=0.1)
        assert hoeyde == pytest.approx(linje * round(hoeyde / linje), abs=1)  # hele linjer
    assert all(h >= 24 and h == pytest.approx(30, abs=0.5) and inne for h, inne in r["brikker"]), r["brikker"]
    assert hvilken == "ekte" or r["brikker"]
    assert r["fokus"] and r["fokus"][0] and r["fokus"][1] == "solid" and r["fokus"][2] == "3px", r["fokus"]
    venstre = sorted({k[0] for k in r["kort"]})
    assert len(venstre) == kolonner, r["kort"]
    for kol in venstre:
        i_kol = sorted((k for k in r["kort"] if k[0] == kol), key=lambda k: k[1])
        for over, under in zip(i_kol, i_kol[1:]):
            assert under[1] - over[2] == pytest.approx(16, abs=1), (over, under)
    assert r["under"] == 0, r["under"]
    assert rekkefoelgen and [re.sub(r"\s+\d+$", "", t) for t in r["rekkefoelgen"]] == rekkefoelgen


MAAL_KNAPPEN = r"""
const a = document.querySelector('p.investorboble a');
const b = a.getBoundingClientRect();
a.focus();
const f = getComputedStyle(a);
ferdig({hoeyde: b.height, linjer: Math.round((b.height - 25) / 22), fokus: [a.matches(':focus-visible'), f.outlineWidth],
        rulling: document.documentElement.scrollWidth > document.documentElement.clientWidth});
"""


def test_knappen_i_stilen():
    """Ville feilet hvis knappen til investorsiden ikke hadde minst 44 px."""
    regel = re.search(r"p\.investorboble a \{([^}]*)\}", STIL).group(1)
    assert "min-height: 44px" in regel and "padding: 11px 20px" in regel and "line-height: 22px" in regel


@I_NETTLESER
@VERSJONENE
@pytest.mark.parametrize("bredde,brytes", ((1280, False), (320, True)))
def test_knappen_44_px_ogsaa_naar_teksten_brytes(request, tmp_path, hvilken, bredde, brytes):
    """Ville feilet hvis knappen til investorsiden var lavere enn 44 px, på én
    linje eller når et langt navn brytes på smal skjerm, i en av versjonene,
    fokusringen manglet, eller pila og den nye fanen sto i demoen og ikke i den
    ekte versjonen (VG7)."""
    k, side = _versjonen(request, hvilken)
    symbol = re.search(r'href="/aksje/([A-Z0-9.]+)"', side).group(1)
    html = _side(k, f"/aksje/{symbol}")
    boblen = html.split('<p class="investorboble">', 1)[1].split("</p>", 1)[0]
    ekte_ = hvilken == "ekte"
    assert ("↗" in boblen) == ekte_ and ('target="_blank"' in boblen) == ekte_
    assert ("(åpnes i en ny fane)" in boblen) == ekte_
    navn = re.search(r">Investorsiden til ([^<]+)<", boblen).group(1)
    if brytes:
        html = html.replace(f"Investorsiden til {navn}<", f"Investorsiden til {navn} Holding og Kraftselskap ASA<", 1)
    r = _kjoer(html, tmp_path, bredde, MAAL_KNAPPEN)
    assert r["hoeyde"] >= 44 and not r["rulling"], r
    assert (r["linjer"] > 1) == brytes, r
    assert r["fokus"] == [True, "3px"], r["fokus"]


# Tillegg 2 (gruppens ønske 13.11 kl. 20:35): styrken for én dag vises likt
# overalt, med regelen fra tabellen på oversikten (index.html og skiller_seg_ut
# i markedsoversikt.py): 3 av 3 som pille tre-av-tre, fra terskelen som pille
# to-av-tre, og under terskelen som tekst uten pille. Gjelder notatene
# (_notat.html: Min liste, aksjesiden og panelet) og «Signalet dag for dag».

STYRKEN = re.compile(r'<span class="([^"]*)">(\d) av 3</span>')


def _terskel() -> int:
    from signalberegning import STANDARD

    return STANDARD.terskel


def _ventet(styrke: int) -> str:
    if styrke == 3:
        return "pille tre-av-tre"
    return "pille to-av-tre" if styrke >= _terskel() else "styrketall"


def _dagen(styrke: int):
    from types import SimpleNamespace

    retning = SimpleNamespace(klasse="blandet", symbol="↔", tekst="Blandet")
    return SimpleNamespace(
        vurdering=SimpleNamespace(styrke=styrke), retning=retning, brikker=[("T", "Trend", "+1")], tekst=""
    )


class TestStyrkenSomTabellen:
    @VERSJONENE
    @pytest.mark.parametrize("styrke", (0, 1, 2, 3))
    def test_i_notatet(self, request, hvilken, styrke):
        """Ville feilet hvis et notat viste 0 eller 1 av 3 i en pille, 2 av 3
        uten den hvite pillen eller 3 av 3 uten den oransje, i en av versjonene."""
        from flask import render_template_string

        import app as app_modul

        _versjonen(request, hvilken)
        with app_modul.app.test_request_context("/min-liste"):
            html = render_template_string(
                '{% from "_notat.html" import signalet with context %}{{ signalet(dag) }}', dag=_dagen(styrke)
            )
            # Gjennomgangen (BH2): malene får samme terskel som _ventet.
            assert render_template_string("{{ parametre.terskel }}") == str(_terskel())
        assert STYRKEN.findall(html) == [(_ventet(styrke), str(styrke))], html

    @VERSJONENE
    @pytest.mark.parametrize("styrke", (0, 1, 2, 3))
    def test_i_signalet_dag_for_dag(self, request, hvilken, styrke):
        """Ville feilet hvis en dag i «Signalet dag for dag» viste styrken på
        en annen måte enn tabellen, i en av versjonene."""
        from flask import render_template_string

        import app as app_modul

        _versjonen(request, hvilken)
        aksjemal = (ROT / "src" / "templates" / "aksje.html").read_text(encoding="utf-8")
        treff = re.search(r"\{% if dag\.vurdering %\}(.*?)\{% elif not dag\.tom %\}", aksjemal, flags=re.S)
        assert treff, "cellen i «Signalet dag for dag» er flyttet (gjennomgangen, VG3)"
        cellen = treff.group(1)
        with app_modul.app.test_request_context("/"):
            # Rettet 2026-11-14 (story 2.17): cellen har også merket «i ettertid».
            html = render_template_string(
                '{% from "_brikker.html" import brikker, ettertid, retningspille, styrke %}' + cellen,
                dag=_dagen(styrke),
            )
        assert STYRKEN.findall(html) == [(_ventet(styrke), str(styrke))], html

    @VERSJONENE
    def test_paa_sidene(self, request, hvilken):
        """Ville feilet hvis en dag i «Signalet dag for dag» eller et notat på
        sidene viste styrken på en annen måte enn tabellen. I demoen skal
        historikken ha alle fire, så regelen er prøvd for hver. Den ekte
        versjonen med 0-3 og notater står i TestStyrkenIDenEkteVersjonen."""
        k, side = _versjonen(request, hvilken)
        symbolene = sorted(set(re.findall(r'href="/aksje/([A-Z]+)"', _side(k, "/"))))
        sett = set()
        for symbol in symbolene:
            aksjeside = _side(k, f"/aksje/{symbol}")
            if '<section class="historikk"' not in aksjeside:
                continue
            historikken = aksjeside.split('<section class="historikk"', 1)[1].split("</section>", 1)[0]
            for klasse, tall in STYRKEN.findall(historikken):
                assert klasse == _ventet(int(tall)), (symbol, klasse, tall)
                sett.add(int(tall))
        for klasse, tall in _i_notatene(side):
            assert klasse == _ventet(int(tall)), (klasse, tall)
        assert sett, "ingen dager i historikken"
        if hvilken == "klient":
            assert sett == {0, 1, 2, 3}, sett

    def test_summen_og_kortet_staar_som_foer(self):
        """Ville feilet hvis summen under sjekkene eller kortet «Signalstyrke»
        fikk regelen for én dag i stedet for ringen fra siste børsdag."""
        aksjemal = (ROT / "src" / "templates" / "aksje.html").read_text(encoding="utf-8")
        assert '<span class="pille{% if ringen %} {{ ringen }}{% endif %}">{{ detalj.styrke }}' in aksjemal
        assert '<span class="styrken{% if ringen %} pille {{ ringen }}{% endif %}">' in aksjemal

    def test_stilen_for_notatene_og_historikken(self):
        """Ville feilet hvis den hvite pillen eller teksten uten pille manglet
        stil i notatene eller i «Signalet dag for dag»."""
        for del_ in (
            "\n.etterpaa .pille.to-av-tre { border: 1.5px solid var(--blekk); background: var(--hvit);",
            "\n.etterpaa .styrketall { font-weight: 700;",
            "\n:where(.side-aksje) .historikk .pille.to-av-tre { border: 1.5px solid var(--blekk); background: var(--hvit);",
            "\n:where(.side-aksje) .historikk .styrketall { font-weight: 700;",
        ):
            # Gjennomgangen (VG4): hele selektoren fra linjestart, så et annet
            # omfang ikke teller. Notatene er uten omfang, fordi panelet står
            # på alle sidene.
            assert del_ in STIL.replace("\r\n", "\n"), del_


def _i_notatene(side: str) -> list[tuple[str, str]]:
    """Styrkene under «Etterpå» i notatene på en side (gjennomgangen, BH3)."""
    treff = []
    for blokk in side.split('<div class="etterpaa">')[1:]:
        treff += STYRKEN.findall(blokk.split("</div>", 1)[0])
    return treff


@pytest.fixture
def ekte_med_notater(base, monkeypatch):  # noqa: F811
    """Den ekte versjonen med basen fra test_historikken: EQNR med 3 av 3
    01.10, 0 av 3 02.10, 2 av 3 06.10 og 1 av 3 08.10 (siste dag 09.10 har
    2 av 3), og ett notat hver av de fire dagene (gjennomgangen, VG1 og VG2)."""
    from datetime import date, datetime, timezone

    import app as app_modul
    import lagring_sqlite
    import test_historikken as h

    monkeypatch.setattr(app_modul, "naa", lambda: h.NAA)
    monkeypatch.delenv(app_modul.I_DEMO, raising=False)
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    tilkobling = lagring_sqlite.aapne_base(lagring_sqlite.BASE_STI)
    try:
        lager = lagring_sqlite.SqliteNotatlager(tilkobling)
        for dag in (date(2026, 10, 1), date(2026, 10, 2), date(2026, 10, 6), date(2026, 10, 8)):
            lager.skriv(h.SYMBOL, dag, f"Notat {dag:%d.%m}", datetime(2026, 10, 9, 18, tzinfo=timezone.utc))
    finally:
        tilkobling.close()
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


class TestStyrkenIDenEkteVersjonen:
    def test_signalet_dag_for_dag_med_0_til_3(self, ekte_med_notater):
        """Ville feilet hvis en dag med 0, 1, 2 eller 3 av 3 i «Signalet dag for
        dag» i den ekte versjonen viste styrken på en annen måte enn tabellen
        (gjennomgangen, VG1)."""
        side = _side(ekte_med_notater, "/aksje/EQNR")
        assert "Eksempeltall" not in side
        historikken = side.split('<section class="historikk"', 1)[1].split("</section>", 1)[0]
        funnet = STYRKEN.findall(historikken)
        assert {int(t) for _, t in funnet} == {0, 1, 2, 3}, funnet
        assert all(klasse == _ventet(int(tall)) for klasse, tall in funnet), funnet

    @pytest.mark.parametrize("adresse", ("/min-liste", "/aksje/EQNR", "/"))
    def test_notatene_med_0_til_3(self, ekte_med_notater, adresse):
        """Ville feilet hvis et notat i Min liste, på aksjesiden eller i panelet
        (malen står på alle sidene, også oversikten) viste 0, 1, 2 eller 3 av
        3 på en annen måte enn tabellen, eller siden ikke kunne vises med
        notatene (gjennomgangen, BH1, VG2 og ECH3)."""
        funnet = _i_notatene(_side(ekte_med_notater, adresse))
        assert {int(t) for _, t in funnet} == {0, 1, 2, 3}, (adresse, funnet)
        assert all(klasse == _ventet(int(tall)) for klasse, tall in funnet), (adresse, funnet)

    def test_summen_og_kortet_en_tidligere_dag(self, ekte_med_notater):
        """Ville feilet hvis summen eller kortet «Signalstyrke» en tidligere dag
        med 2 av 3 fikk den hvite pillen fra «Signalet dag for dag» i den ekte
        versjonen (gjennomgangen, VG5)."""
        side = _side(ekte_med_notater, "/aksje/EQNR?dag=2026-10-06")
        summen = side.split('<p class="sumrad">', 1)[1].split("</p>", 1)[0]
        kortet = side.split('<span class="etikett">Signalstyrke', 1)[1].split("</div>", 1)[0]
        assert '<span class="pille">2 av 3</span>' in summen and "2 <span" in kortet
        assert "to-av-tre" not in summen + kortet
