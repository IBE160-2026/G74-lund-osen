"""Gruppens svar 04.11 kl. 22:23: fire ting som i designforslaget
(spesifikasjonen spec-8-2b-som-designforslaget.md). Designforslaget ligger
ikke i repoet, så tallene er de i svaret og i instruksjonen 05.11 kl. 11:50.

Testene bruker demobasen, laget i tmp_path av fixturen i conftest.py, som
flytter BASE_STI. Ingen nett og ingen henting.
"""

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

import app as app_modul
import demo
from lagring_sqlite import demo_sti

STIL = (Path(__file__).resolve().parent.parent / "src" / "static" / "stil.css").read_text(encoding="utf-8")


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


def _regel(velger: str) -> str:
    treff = re.search(r"(?:^|\n)\s*(?::where\(\.side-[a-z]+\) )?" + re.escape(velger) + r"\s*\{([^}]*)\}", STIL)
    assert treff, f"ingen regel for {velger}"
    return treff.group(1)


def _px(regel: str, egenskap: str) -> float:
    return float(re.search(egenskap + r": ([\d.]+)px", regel).group(1))


# --- Svar 1: store ruter i børsometeret ---------------------------------------

KLASSENE = ("bredest", "bred", "smal", "smalest")


def test_grensen_for_store_ruter_er_regnet_fra_stilen():
    """Svar 1: STOR er regnet som NIVAA_3 og STYRKE, med tallene i stil.css:
    rammen, luften 10 og 12 px, symbolet 22 px, navnet 12,5 px og endringen
    28 px, og i bredden AKRBP med «ikke vurdert» ved siden av og «Uten data» i
    28 px. Ville feilet med en grense der symbolet, styrken eller endringen
    kunne gå utenfor ruta, eller hvis stilen fikk andre tall enn koden.
    Gjennomgangen av svar 4 (ECH1): symbolet regnes med STORSYMBOL_EM, 0,75 em,
    målt i Edge til opptil 0,721 em (MOWI). Gjennomgangen (VG2): ringen i
    stor_bredde, PILLELUFT og PILLEKANT, er den i stil.css, og styrken står i
    14 px. Ville også feilet hvis ringen fikk mer luft eller tykkere kant i
    stilen uten at koden fulgte med."""
    import boersometer as b

    for klasse in KLASSENE:
        stor = _regel(f".rute.nivaa-{klasse}-4")
        assert tuple(int(v) for v in re.search(r"padding: (\d+)px (\d+)px", stor).groups()) == b.STORLUFT
        assert re.search(r"gap: 0 (\d+)px", stor).group(1) == str(b.STORMELLOM)
        assert _px(_regel(f".rute.nivaa-{klasse}-4 > .ticker"), "font-size") == b.STORSYMBOL
        assert _px(_regel(f".rute.nivaa-{klasse}-4 > .endring"), "font-size") == b.STORENDRING
    navn = _regel(".rute .navn")
    assert _px(navn, "font-size") == b.STORNAVN and _px(navn, "margin-top") == b.STORGAP
    rute = re.search(r"side-oversikt\) \.rute \{([^}]*)\}", STIL).group(1)
    linje = float(re.search(r"line-height: ([\d.]+)", rute).group(1))
    ramme = int(
        re.search(r"border: (\d+)px solid", _regel(".rute.ramme-gul, :where(.side-oversikt) .proeve.ramme-gul")).group(
            1
        )
    )
    luft_h, luft_b = b.STORLUFT
    hoeyde = 2 * ramme + 2 * luft_h + (b.STORSYMBOL + b.STORNAVN + b.STORENDRING) * linje + b.STORGAP
    halvfet = 0.62
    assert b.HALVFET_EM == halvfet and b.STORSYMBOL_EM >= 0.721
    topp = 2 * ramme + 2 * luft_b + b.STORSYMBOL_EM * b.STORSYMBOL * len("AKRBP") + b.STORMELLOM
    topp += b.EM_PER_TEGN * b.RUTESKRIFT * len("ikke vurdert")
    bunn = 2 * ramme + 2 * luft_b + halvfet * b.STORENDRING * len("Uten data")
    assert b.STOR[1] >= hoeyde and b.STOR[0] >= max(topp, bunn), (b.STOR, hoeyde, topp, bunn)
    assert b.STOR[0] > b.NIVAA_3[0] and b.STOR[1] >= b.NIVAA_3[1]
    pille = _regel(".pille")
    assert float(re.search(r"padding: [\d.]+rem ([\d.]+)rem", pille).group(1)) * 16 == b.PILLELUFT
    kanter = [float(k) for k in re.findall(r"\.pille\.(?:tre|to)-av-tre \{ border: ([\d.]+)px", STIL)]
    assert kanter and max(kanter) == b.PILLEKANT, kanter
    assert _px(_regel(".rute .styrke"), "font-size") == b.RUTESKRIFT


@pytest.mark.parametrize(("b", "h", "ventet"), [(166.4, 107, True), (166.3, 107, False), (166.4, 106.9, False)])
def test_storplass_regnes_for_hver_rute(b, h, ventet):
    """Gruppens svar 05.11 kl. 14:29, 4: grensen regnes for hver rute. HVDO
    i demoen, 2 av 3 i ringen og -1,67 %: øverst 32 + 0,75 × 22 × 4 + 8 +
    0,5 × 14 × 6 + ringen 2 × 2 + 2 × 7,2 = 166,4 px, og nederst 32 +
    0,62 × 28 × 7 = 153,52 px, så HVDO (175 px ved 1280 px) er stor fra
    166,4 px, ikke fra den faste grensen.
    Ville feilet med den faste grensen STOR, eller uten ringen eller
    endringen i bredden."""
    from boersometer import MOERK, _stor_bredde, storplass

    hvdo = _rute(aksje=_aksje("HVDO", "Havdyp Olje"), styrke=2, siste_styrke=2, endring=-1.67, er_siste=True)
    assert hvdo.ramme == MOERK
    assert _stor_bredde(hvdo) == pytest.approx(166.4)
    assert storplass(hvdo, b, h) is ventet


def test_stor_den_bredeste_er_stor_bredde():
    """Svar 4: STOR[0] er den største bredden en rute med en endring på
    høyst ni tegn kan trenge, AKRBP med «ikke vurdert», og ringen gjør
    ikke en rute bredere enn det. Ville feilet hvis stor_bredde og STOR
    regnet ulikt."""
    from boersometer import STOR, stor_bredde

    # Gjennomgangen (BH5): en rute uten data har ingen styrke, så den bredeste
    # er AKRBP med «ikke vurdert» og en endring på ni tegn.
    bredest = stor_bredde("AKRBP", "ikke vurdert", False, "+12,34 %")
    assert bredest > stor_bredde("AKRBP", None, False, "Uten data")
    assert bredest <= STOR[0] < bredest + 1
    assert stor_bredde("AKRBP", "3 av 3", True, "-12,34 %") < bredest


def _aksje(symbol, navn):
    from kursdata import Aksje

    return Aksje(symbol, f"{symbol}.OL", navn, "Energi")


def _rute(**kw):
    from boersometer import Rute
    from kursdata import Aksje

    verdier = {"aksje": Aksje("LKSV", "LKSV.OL", "Laksevik Sjømat", "Sjømat"), "endring": -2.26, "volumforhold": 1.0}
    verdier |= {"styrke": None, "tekst": None}
    return Rute(**(verdier | kw))


def test_merket_og_grunnen_der_de_faar_plass():
    """Svar 1: merket og grunnen står mellom navnet og endringen der de får
    plass, merket først (gjennomgangen, ECH1). En annen dag står styrken i
    en gul rute bare med merket (svaret 04.11 kl. 20:53 og 20:56, 1).
    Gruppens svar 05.11 kl. 14:29, 1: uten plass til merket under navnet
    står merket og styrken i stedet for navnet, og uten plass der heller er
    ruta ikke stor. Gjennomgangen (VG1, BH13): grunnen med og uten merket,
    og høydene regnet fra konstantene. Ville feilet hvis merket eller
    grunnen sto i en rute uten plass, styrken sto uten merket, en stor gul
    rute en annen dag sto uten merket, navnet sto sammen med et merke som
    ikke fikk plass under det, eller grunnen sto under et merke som ikke
    fikk plass."""
    import boersometer as bm
    from boersometer import KANT, STOR, Flate, _nivaa_ved

    flate = Flate("prove", 100, 1, 100, (("prove", 100),))
    linje = bm.RUTESKRIFT * bm.RUTELINJE
    navnet = bm.STORNAVN * bm.RUTELINJE + bm.STORGAP
    # Ved 193 px er merket to linjer i halvfet skrift. Bredden er fast, så
    # testen ikke følger STOR[0], som ble 207 etter gjennomgangen (ECH1).
    bredde = 193
    assert bm._linjer(bm.MERKET, bredde - 2 * bm.RUTERAMME - 2 * bm.STORLUFT[1], bm.HALVFET_EM) == 2
    merke = 2 * linje + bm.STORGAP
    # 0,001 px for avrundingen i flyttallene ved grensen.
    b, h = bredde + 2 * KANT, STOR[1] + 2 * KANT + 0.001
    gul = _rute(styrke=1, siste_styrke=3, er_siste=False)
    # Ikke plass til merket, heller ikke i stedet for navnet: ruta er ikke stor.
    assert _nivaa_ved(flate, 100, b, h, gul) == (3, False, False, False, False)
    assert _nivaa_ved(flate, 100, b, h + merke - navnet - 0.01, gul)[0] == 3
    # Plass i stedet for navnet: merket og styrken, uten navnet.
    assert _nivaa_ved(flate, 100, b, h + merke - navnet, gul) == (4, True, False, True, False)
    assert _nivaa_ved(flate, 100, b, h + merke - 0.01, gul) == (4, True, False, True, False)
    # Plass under navnet: alt (gjennomgangen, BH8: kommentaren sto over feil linje).
    assert _nivaa_ved(flate, 100, b, h + merke, gul) == (4, True, False, True, True)
    # Siste børsdag trenger ikke merket.
    siste = _rute(styrke=3, siste_styrke=3)
    assert _nivaa_ved(flate, 100, b, h, siste) == (4, True, False, False, True)
    # Grunnen, «for kort historikk: 24 av 51 dager», er tre linjer ved 161 px.
    grunn = "for kort historikk: 24 av 51 dager"
    linjer = bm._linjer(grunn, bredde - 2 * bm.RUTERAMME - 2 * bm.STORLUFT[1])
    trengs = linjer * linje + bm.STORGAP
    uten = _rute(tekst=grunn)
    assert uten.grunn and uten.uten_styrke
    assert _nivaa_ved(flate, 100, b, h + trengs - 1, uten) == (4, True, False, False, True)
    assert _nivaa_ved(flate, 100, b, h + trengs, uten) == (4, True, True, False, True)
    # En gul rute en annen dag: grunnen bare under merket.
    gul_grunn = _rute(tekst=grunn, siste_styrke=3, er_siste=False)
    assert _nivaa_ved(flate, 100, b, h + trengs, gul_grunn)[2] is False
    assert _nivaa_ved(flate, 100, b, h + merke + trengs, gul_grunn) == (4, True, True, True, True)


def test_merket_i_stedet_for_navnet_som_lksv_18_09():
    """Gruppens svar 05.11 kl. 14:29, 1: LKSV 18.09 er 231 × 123 px ved
    1280 px i demoen. Der er merket én linje i halvfet skrift, og det får
    plass i stedet for navnet, men ikke under det. Ville feilet hvis ruta
    viste navnet uten merket og styrken, som før svaret."""
    import boersometer as bm
    from boersometer import KANT, Flate, _nivaa_ved

    flate = Flate("prove", 100, 1, 100, (("prove", 100),))
    assert bm._linjer(bm.MERKET, 231 - 2 * bm.RUTERAMME - 2 * bm.STORLUFT[1], bm.HALVFET_EM) == 1
    gul = _rute(siste_styrke=3, er_siste=False)
    assert _nivaa_ved(flate, 100, 231 + 2 * KANT, 123 + 2 * KANT, gul) == (4, True, False, True, False)


def test_merket_er_det_malen_skriver():
    """Gjennomgangen (VG3): høyden for merket regnes med MERKET, så teksten
    må være den malen skriver. Ville feilet hvis malen fikk en annen tekst."""
    import boersometer as bm

    mal = (Path(__file__).resolve().parent.parent / "src" / "templates" / "boersometer.html").read_text(
        encoding="utf-8"
    )
    assert "{{ antall_sjekker }} av {{ antall_sjekker }} siste børsdag</span>" in mal
    assert bm.MERKET == f"{bm.ANTALL_SJEKKER} av {bm.ANTALL_SJEKKER} siste børsdag"


def test_navnet_staar_bare_med_navn_klassen():
    """Gruppens svar 05.11 kl. 14:29, 1: navnet står bare i klassene i
    Kartrute.navn, og malen skriver navn-N. Ville feilet hvis navnet sto i
    en stor rute der merket står i stedet, eller malen mistet klassen."""
    mal = (Path(__file__).resolve().parent.parent / "src" / "templates" / "boersometer.html").read_text(
        encoding="utf-8"
    )
    assert "{% for navn in kartrute.navn|sort %} navn-{{ navn }}{% endfor %}" in mal
    for klasse in KLASSENE:
        assert "display: block" in _regel(f".rute.nivaa-{klasse}-4.navn-{klasse} > .navn")
        assert f".rute.nivaa-{klasse}-4 > .navn {{" not in STIL


def test_lksv_18_09_viser_merket_i_stedet_for_navnet(klient):
    """Gruppens svar 05.11 kl. 14:29, 1, i demoen ved 1280 px: en gul rute en
    annen dag er stor, med merket og styrken, men uten navn-bredest. Story
    8.20b (U97): med to linjer i bransjeoverskriften er LKSV 18.09 ikke
    lenger stor, og BRFE 06.10 er dagen i demoen som viser det. Navnet på
    testen står, fordi docs/kvalitetssikring.md viser til det. Ville feilet
    hvis ruta var stor uten merket, eller hadde både navnet og merket."""
    html = _html(klient, "/boersometer?periode=velg&dag=2026-10-06")
    klasser = re.search(r'<a class="rute ([^"]*)"[^>]*>\s*<span class="ticker">BRFE</span>', html).group(1).split()
    assert {"nivaa-bredest-4", "merke-bredest", "styrke-bredest"} <= set(klasser), klasser
    assert "navn-bredest" not in klasser, klasser


@pytest.mark.parametrize(("endring", "stor"), [(-2.26, True), (1234.56, False)])
def test_endringen_maa_faa_plass_i_28_px(endring, stor):
    """Gjennomgangen (BH3, ECH3): STOR er regnet for ni tegn, og en endring
    over en periode kan ha flere, som «+1 234,56 %». Da blir ruta ikke stor.
    Ville feilet hvis en endring bredere enn ruta sto i 28 px."""
    from boersometer import KANT, STOR, Flate, _nivaa_ved

    flate = Flate("prove", 100, 1, 100, (("prove", 100),))
    nivaa = _nivaa_ved(flate, 100, STOR[0] + 2 * KANT, STOR[1] + 2 * KANT, _rute(styrke=3, endring=endring))[0]
    assert (nivaa == 4) is stor


def test_kartet_og_siden_har_merket_i_en_stor_rute():
    """Gjennomgangen (VG3): kart() fyller Kartrute.merke, og malen skriver
    merke-N. En gul rute en annen dag alene i kartet er stor og har plass til
    merket. Ville feilet hvis kart() eller malen mistet merket, så stilen
    skjulte det mens styrken sto."""
    from boersometer import bygg_boersometer, kart

    k = kart(bygg_boersometer([_rute(styrke=1, siste_styrke=3, er_siste=False)]))
    rute = k.felt[0].ruter[0]
    assert rute.nivaa["bredest"] == 4 and "bredest" in rute.merke and "bredest" in rute.styrke
    mal = (Path(__file__).resolve().parent.parent / "src" / "templates" / "boersometer.html").read_text(
        encoding="utf-8"
    )
    assert "{% for navn in kartrute.merke|sort %} merke-{{ navn }}{% endfor %}" in mal


def test_fotnoten_for_en_annen_grunn_paa_nivaa_4():
    """Gjennomgangen (VG2): en stor rute med en annen grunn viser «ikke
    vurdert» øverst når den har styrke-N, og da står fotnoten for øyet i den
    klassen. Ville feilet hvis annen_grunn_i_kartet bare regnet nivå 2 og 3."""
    from boersometer import Bransje, Kart, Kartfelt, Kartrute, annen_grunn_i_kartet

    rute = _rute(tekst="for kort historikk: 24 av 51 dager")
    nivaa = {"bredest": 4, "bred": 4, "smal": 2, "smalest": 1}
    kartrute = Kartrute(rute, 1.0, {}, nivaa, styrke=frozenset({"bredest"}))
    felt = Kartfelt(Bransje("Sjømat", (rute,)), 1.0, {}, {}, (kartrute,))
    assert annen_grunn_i_kartet(Kart((felt,), {})) == frozenset({"bredest"})


def _container_blokker() -> list[tuple[str, str, str]]:
    """(media, container, innhold) for hver @container i stil.css, med
    klammene talt."""
    ut = []
    for m in re.finditer(r"@media \(([^)]*)\) \{", STIL):
        dybde, i = 1, m.end()
        while dybde:
            dybde += {"{": 1, "}": -1}.get(STIL[i], 0)
            i += 1
        media = STIL[m.end() : i - 1]
        for c in re.finditer(r"@container \(([^)]*)\) \{", media):
            d, k = 1, c.end()
            while d:
                d += {"{": 1, "}": -1}.get(media[k], 0)
                k += 1
            ut.append((m.group(1), c.group(1), media[c.end() : k - 1]))
    return ut


def test_nivaa_4_staar_i_grensen_klassen_er_regnet_for():
    """Gjennomgangen (VG4, BH9): reglene for nivå 4 i hver klasse står bare i
    den @container-grensen klassen er regnet for (Flate.tekst), som for nivå
    0–3. Ville feilet hvis to klasser byttet blokk."""
    from boersometer import BRED, SMAL

    grenser = {
        "bredest": ("width > 760px", f"width >= {BRED.tekst[1][1]:.0f}px"),
        "bred": ("width > 760px", f"width < {BRED.tekst[1][1]:.0f}px"),
        "smal": ("width <= 760px", f"width >= {SMAL.tekst[0][1]:.0f}px"),
        "smalest": ("width <= 760px", f"width < {SMAL.tekst[0][1]:.0f}px"),
    }
    for klasse, (media, container) in grenser.items():
        der = [(m, c) for m, c, innhold in _container_blokker() if f".rute.nivaa-{klasse}-4" in innhold]
        assert der == [(media, container)], (klasse, der)


def test_hoeye_smale_ruter_er_store_i_demoen(klient):
    """Gruppens svar 05.11 kl. 14:29, 4: HVDO og BRFE er 175 og 173 px brede
    ved 1280 px, siste børsdag, og blir store når alt deres får plass. Svar 2:
    store ruter bare fra 1079 px, så KVST er ikke stor i klassen bred, selv
    om bredden for KVST er under 160 px. Ville feilet med den faste grensen
    193 px, eller med store ruter under 1079 px."""
    from boersometer import STORE_KLASSER

    assert STORE_KLASSER == frozenset({"bredest"})
    html = _html(klient, "/boersometer")
    klasser = dict(
        (s, k.split())
        for k, s in re.findall(r'<a class="rute ([^"]*)"[^>]*>\s*<span class="ticker">([A-Z]+)</span>', html)
    )
    for symbol in ("HVDO", "BRFE", "KVST"):
        assert "nivaa-bredest-4" in klasser[symbol], (symbol, klasser[symbol])
        # Gjennomgangen (VG1): navnet står i de store rutene på siste børsdag.
        assert "navn-bredest" in klasser[symbol], (symbol, klasser[symbol])
    assert not [s for s, k in klasser.items() if {f"nivaa-{n}-4" for n in ("bred", "smal", "smalest")} & set(k)]


def test_en_stor_rute_i_demoen(klient):
    """Svar 1: i demoen er KVST stor ved 1280 px, siste børsdag, målt i
    Edge. Navnet står i ruta for øyet og er skjult for skjermleseren, som
    leser det i linja under. Ville feilet uten nivå 4, uten navnet eller med
    navnet to ganger for skjermleseren."""
    html = _html(klient, "/boersometer")
    klasser, innhold = re.search(
        r'<a class="rute ([^"]*)"[^>]*>\s*<span class="ticker">KVST</span>(.*?)</a>', html, re.S
    ).groups()
    assert "nivaa-bredest-4" in klasser.split(), klasser
    assert '<span class="navn" aria-hidden="true">Kvitstein Mineral</span>' in innhold
    assert innhold.count("Kvitstein Mineral") == 2


def test_store_ruter_i_stilen():
    """Svar 1: nivå 4 er et rutenett med symbolet og styrken øverst, navnet
    under, merket og grunnen og endringen nederst, i hver av de fire
    klassene. Navnet er skjult ellers, så små ruter er som før, og kuttes
    med «…». Ville feilet hvis navnet sto i små ruter, ikke ble kuttet, eller
    endringen ikke sto nederst."""
    assert "display: none" in _regel(".rute .navn")
    navn = _regel(".rute .navn")
    assert "text-overflow: ellipsis" in navn and "white-space: nowrap" in navn and "overflow: hidden" in navn
    for klasse in KLASSENE:
        stor = _regel(f".rute.nivaa-{klasse}-4")
        assert '"ticker styrke" "navn navn" "merke merke" "tekst tekst" "endring endring"' in stor
        assert "align-self: end" in _regel(f".rute.nivaa-{klasse}-4 > .endring")
        assert "font-weight: 600" in _regel(f".rute.nivaa-{klasse}-4 > .ticker")
        skjul = re.search(
            re.escape(f".rute.nivaa-{klasse}-4:not(.styrke-{klasse}) > .styrke") + r"[^{]*\{([^}]*)\}", STIL
        )
        assert skjul and "clip: rect(0 0 0 0)" in skjul.group(1)
        assert f".rute.nivaa-{klasse}-4:not(.merke-{klasse}) > .merke" in STIL
        assert f".rute.nivaa-{klasse}-4:not(.grunn-{klasse}) > .tekst" in STIL


# --- Svar 2: lenken til børsometeret under søylene ----------------------------


def _soeylefot(html: str) -> str:
    return html.split('<div class="soeylefot">', 1)[1].split("</div>", 1)[0]


@pytest.mark.parametrize(
    ("oversikt", "boersometer", "ord_"),
    [
        ("/", "/boersometer?periode=siste", "dagen"),
        ("/?periode=siste", "/boersometer?periode=siste", "dagen"),
        ("/?periode=1-mnd", "/boersometer?periode=1-mnd", "perioden"),
        ("/?periode=1-uke", "/boersometer?periode=1-uke", "perioden"),
        # Gjennomgangen (VG4): alle periodene.
        ("/?periode=3-mnd", "/boersometer?periode=3-mnd", "perioden"),
        ("/?periode=6-mnd", "/boersometer?periode=6-mnd", "perioden"),
        ("/?periode=i-aar", "/boersometer?periode=i-aar", "perioden"),
        ("/?periode=1-aar", "/boersometer?periode=1-aar", "perioden"),
        ("/?periode=velg&dag=2026-10-05", "/boersometer?periode=velg&amp;dag=2026-10-05", "dagen"),
    ],
)
def test_lenken_til_boersometeret_har_samme_periode(klient, oversikt, boersometer, ord_):
    """Svar 2: under søylene, til høyre for «Stiplet linje: hovedindeksen»,
    står lenken med samme periode eller dag. Gruppens svar 05.11 kl. 14:29,
    3: «Se dagen i Børsometer ›» ved én dag og «Se perioden i Børsometer ›»
    ved en periode. Ville feilet uten lenken, med lenken foran forklaringen,
    med en annen periode eller dag i adressen, eller med «perioden» ved én
    dag eller «dagen» ved en periode."""
    fot = _soeylefot(_html(klient, oversikt))
    lenke = (
        f'<a class="til-boersometer" href="{boersometer}">Se {ord_} i Børsometer <span aria-hidden="true">›</span></a>'
    )
    assert lenke in fot, fot
    assert fot.index("Stiplet linje: hovedindeksen") < fot.index(lenke)


@pytest.mark.parametrize(
    ("oversikt", "ventet"),
    [
        ("/?periode=1-mnd", 'href="/boersometer?periode=1-mnd#perioden" aria-current="true"'),
        ("/?periode=velg&dag=2026-10-05", "mandag 05.10"),
    ],
)
def test_lenken_aapner_boersometeret_med_samme_periode(klient, oversikt, ventet):
    """Svar 2: lenken åpner børsometeret med perioden eller dagen fra
    oversikten. Ville feilet hvis børsometeret viste siste børsdag i stedet."""
    adresse = re.search(r'class="til-boersometer" href="([^"]+)"', _html(klient, oversikt)).group(1)
    assert ventet in _html(klient, adresse.replace("&amp;", "&"))


def test_lenken_er_halvfet():
    """Svar 2: lenken står i halvfet skrift, til høyre. Ville feilet med
    vanlig skrift eller uten margin-left: auto."""
    regel = _regel(".soeyler .soeylefot .til-boersometer")
    assert "font-weight: 600" in regel and "auto" in regel
    assert "justify-content: space-between" in _regel(".soeyler .soeylefot")


# --- Svar 3: «<navnet> kort fortalt» på aksjesiden ----------------------------


def test_ki_delen_heter_navnet_kort_fortalt(klient):
    """Svar 3: overskriften har «?», og «Laget av KI» står som før. Story
    10.9, del C (gruppens svar 06.11 kl. 22:23): rammen heter «Signalet
    forklart» og erstatter «<navnet> kort fortalt». Navnet på testen står,
    fordi docs/kvalitetssikring.md og spesifikasjonen 8.2b viser til det.
    Ville feilet med «kort fortalt», uten «?» eller uten merket."""
    html = _html(klient, "/aksje/BRFE")
    ki = html.split('<section class="ki"', 1)[1].split("</section>", 1)[0]
    assert 'aria-labelledby="ki-tittel"' in ki.split(">", 1)[0]
    tittel = ki.split("<h2>", 1)[1].split("</h2>", 1)[0]
    assert tittel.startswith('<span id="ki-tittel">Signalet forklart</span> ')
    # Story 8.26 (tillegg 20): stegene i omvisningen står i data-steg på alle sidene.
    assert "kort fortalt" not in re.sub(r' data-steg="[^"]*"', "", html)
    assert 'popovertarget="hjelp-ki"' in tittel
    # Story 8.20a (del D): modellen står i en egen linje under teksten.
    assert '<p class="merke-ki">Laget av KI.' in ki
    assert "Med KI-ens ord" not in html
    assert 'id="hjelp-ki"' in html


def test_overskriften_er_i_newsreader():
    """Svar 3: overskriften står i Newsreader, som de andre. Ville feilet
    hvis KI-delen fikk en annen skrift."""
    assert re.search(r'(?:^|\n)h1, h2 \{ font-family: "Newsreader"', STIL)
    assert "font-family" not in _regel(".ki h2")


def test_hjelpen_ved_ki_delen():
    """Svar 3: hjelpen sier hva teksten er, hva modellen fikk, slått opp i
    ki_grunnlag.py, og at tallene med prikket strek er sjekket. Story 10.9,
    del D (spørsmål 10): bare det, og at teksten ikke gir råd, står i
    docs/hjelp.md. Ville feilet hvis en av delene manglet, eller hjelpen sa
    at modellen fikk kurser."""
    from hjelpetekster import KI_GRUNNLAG, hjelpetekster

    tekst = hjelpetekster()["signalet_forklart"]
    for del_ in ("en språkmodell", "«Laget av KI»", "bare fikk det appen har regnet ut", "prikket strek er sjekket"):
        assert del_ in tekst.tekst, del_
    assert "aldri kurser, prosenter eller volumer" in tekst.tekst
    assert any(fil == KI_GRUNNLAG for fil, _ in tekst.kilder)
    hjelp = (Path(__file__).resolve().parent.parent / "docs" / "hjelp.md").read_text(encoding="utf-8")
    avsnitt = hjelp.split("### Hva er «Signalet forklart» på aksjesiden?")[1].split("\n#")[0]
    assert "prikket strek er sjekket" in avsnitt and "gir ikke råd" in avsnitt


# --- Svar 4: ikonene i menyknappene -------------------------------------------


@pytest.mark.parametrize(
    ("sti", "navn", "del_"),
    [
        ("/", "Markedsoversikt", '<rect x="2" y="2.5" width="12" height="11" rx="1.5"/>'),
        ("/", "Børsometer", '<path d="M2 12a6 6 0 0 1 12 0"/><path d="M8 12l3-4"/>'),
        ("/", "Min liste", '<path d="M8 1.8l1.9 4'),
        ("/boersometer", "Børsometer", '<path d="M2 12a6 6 0 0 1 12 0"/>'),
    ],
)
def test_hver_menyknapp_har_sitt_ikon(klient, sti, navn, del_):
    """Svar 4: en tabell, en måler (halvsirkel med viser) og en stjerne, foran
    navnet og skjult for skjermleseren, på alle sidene. Ville feilet uten
    ikonet, med ikonet i feil knapp eller med ikonet synlig for skjermleseren."""
    meny = _html(klient, sti).split('<nav class="rad sider"', 1)[1].split("</nav>", 1)[0]
    knapp = re.search(r'<a class="sideknapp"[^>]*>(<svg class="ikon"[^>]*>.*?</svg>)' + navn + "</a>", meny)
    assert knapp, navn
    assert 'aria-hidden="true" focusable="false"' in knapp.group(1) and del_ in knapp.group(1)
    # Story 8.10: og tannhjulet for «Innstillinger», den fjerde knappen.
    # Story 8.26: knappene «Vis meg rundt» og «Spill av omvisningen» står også
    # i raden, med sine ikoner (test_vis_meg_rundt_8_26.py), men er ikke sider.
    assert len(re.findall(r'<a class="sideknapp"[^>]*><svg class="ikon"', meny)) == 4


def test_ikonene_er_16_px_med_strek_2_i_tekstfargen():
    """Svar 4: 16 px med strek 2 i tekstfargen. Ville feilet med en annen
    størrelse, en annen strek eller en fast farge, som ikke følger knappen
    som er valgt."""
    # Story 8.26: regelen gjelder også knappene i raden, så den heter .sideknapp.
    regel = _regel("header.stripe .sideknapp .ikon")
    for del_ in ("width: 16px", "height: 16px", "stroke: currentColor", "stroke-width: 2", "fill: none"):
        assert del_ in regel, del_
