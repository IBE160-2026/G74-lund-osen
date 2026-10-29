"""Story 8.17a: periodevalget i oversikten, med søylene og indekslinja.

Kontrollpunktene i spesifikasjonen spec-8-17a-periodevalget-i-oversikten.md.
Ingen nettverk (AD-8): basen ligger i tmp_path (conftest.py), og demobasen
lages der den også. Tallene er regnet for hånd fra seriene under.
"""

import re
import shutil
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

import app as app_modul
import demo
import lagring_sqlite
from kursdata import Kursrad
from markedsoversikt import periodeendring
from perioder import EN_MND, EN_UKE, startdag
from test_app import (
    FREDAG_09_10,
    HENTET,
    _boersdager_til,
    _indeks,
    _legg_inn_indeks,
    _synlig,
    skriv_serie,
    skriv_vurdering,
)
from vurderingsdata import Vurdering

ONSDAG_09_09 = date(2026, 9, 9)
FREDAG_02_10 = date(2026, 10, 2)
MANDAG_05_10 = date(2026, 10, 5)
ONSDAG_07_10 = date(2026, 10, 7)
TORSDAG_08_10 = date(2026, 10, 8)

# Den justerte kursen de dagene som teller. Alle andre dager er 100.
# Siste børsdag 09.10: 110 mot 99 dagen før gir +11,11 %. 1 uke starter
# fredag 02.10 (80), så +37,50 %. 1 mnd starter onsdag 09.09 (50), så
# +120,00 %. Sluttkursen 09.10 er 120, ikke 110, så den ujusterte vises.
JUSTERT = {ONSDAG_09_09: 50.0, FREDAG_02_10: 80.0, ONSDAG_07_10: 100.0, TORSDAG_08_10: 99.0, FREDAG_09_10: 110.0}


@pytest.fixture
def klient():
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc))


@pytest.fixture(autouse=True)
def utenfor_docker(monkeypatch):
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    monkeypatch.delenv(app_modul.I_DEMO, raising=False)


def _eqnr() -> list[Kursrad]:
    return [
        Kursrad(
            dato=d,
            slutt=120.0 if d == FREDAG_09_10 else JUSTERT.get(d, 100.0),
            justert_slutt=JUSTERT.get(d, 100.0),
            volum=1000,
        )
        for d in _boersdager_til(FREDAG_09_10, 70)
    ]


def _kort() -> list[Kursrad]:
    """En serie som begynner mandag 05.10: 200 og så 210 siste børsdag."""
    dager = [d for d in _boersdager_til(FREDAG_09_10, 5) if d >= MANDAG_05_10]
    return [
        Kursrad(
            dato=d,
            slutt=210.0 if d == FREDAG_09_10 else 200.0,
            justert_slutt=210.0 if d == FREDAG_09_10 else 200.0,
            volum=1,
        )
        for d in dager
    ]


def _vurdering(trend: int, bevegelse: int, interesse: int, slutt: float = 100.0) -> Vurdering:
    utslag = [v for v in (trend, bevegelse, interesse) if v]
    retning = (
        "Ingen"
        if not utslag
        else "Positiv"
        if all(v > 0 for v in utslag)
        else "Negativ"
        if all(v < 0 for v in utslag)
        else "Blandet"
    )
    return Vurdering(
        styrke=len(utslag),
        retning=retning,
        trend=trend,
        bevegelse=bevegelse,
        interesse=interesse,
        slutt=slutt,
        justert_slutt=slutt,
        trend_avvik=0.0,
        dagens_endring=0.0,
        standardavvik=0.01,
        volumforhold=1.0,
    )


def _basen(med_indeks: bool = False) -> None:
    """EQNR med den håndregnede serien og 3 av 3 siste børsdag, men 2 av 3
    onsdag 07.10. DNB med samme serie, 2 av 3 siste børsdag og 3 av 3
    onsdag 07.10. AKRBP med den korte serien."""
    hentet = datetime.fromisoformat(HENTET)
    skriv_serie("EQNR", _eqnr(), hentet, vurdert=False)
    skriv_serie("DNB", _eqnr(), hentet, vurdert=False)
    skriv_serie("AKRBP", _kort(), hentet, vurdert=False)
    skriv_vurdering("EQNR", FREDAG_09_10, _vurdering(1, 1, 1, 120.0))
    skriv_vurdering("EQNR", ONSDAG_07_10, _vurdering(1, 1, 0))
    skriv_vurdering("DNB", FREDAG_09_10, _vurdering(1, 1, 0, 120.0))
    skriv_vurdering("DNB", ONSDAG_07_10, _vurdering(1, 1, 1))
    if med_indeks:
        # 1 uke: 1000 fredag 02.10 og 1100 siste børsdag, så +10,00 %. Siste
        # børsdag mot torsdag: 0,00 %. Onsdag 07.10 mot tirsdag: +5,00 %.
        _legg_inn_indeks(
            _indeks(
                [
                    (FREDAG_02_10, 1000.0),
                    (date(2026, 10, 6), 1000.0),
                    (ONSDAG_07_10, 1050.0),
                    (TORSDAG_08_10, 1100.0),
                    (FREDAG_09_10, 1100.0),
                ]
            )
        )


def _rad(html: str, symbol: str) -> tuple[str, str]:
    """Klassen og den synlige teksten i raden for symbolet i tabellen."""
    for klasse, innhold in re.findall(
        r"<tr ?(?: class=\"([^\"]*)\")?>\s*<td class=\"selskap\">(.*?)</tr>", html, re.DOTALL
    ):
        if f'href="/aksje/{symbol}"' in innhold:
            return klasse, _synlig(innhold)
    raise AssertionError(f"ingen rad for {symbol}")


def _rad_html(html: str, symbol: str) -> str:
    for innhold in re.findall(r"<td class=\"selskap\">(.*?)</tr>", html, re.DOTALL):
        if f'href="/aksje/{symbol}"' in innhold:
            return innhold
    raise AssertionError(symbol)


def _soeylelista(html: str) -> str:
    return _synlig(html.split('<figure class="soeyler">', 1)[1].split("</figure>", 1)[0])


class TestEndringenForPerioden:
    def test_startdagene_er_regelen_fra_8_16(self):
        """Ville feilet hvis oversikten hadde en egen regel for startdagen."""
        assert startdag(EN_UKE, FREDAG_09_10) == FREDAG_02_10
        assert startdag(EN_MND, FREDAG_09_10) == ONSDAG_09_09

    def test_1_uke_og_1_mnd_mot_den_haandregnede_serien(self):
        """110 mot 80 og 110 mot 50. Ville feilet hvis endringen ble regnet
        fra dagen før (11,11 %) eller på den ujusterte kursen (120)."""
        serie = _eqnr()
        uke, fra_uke = periodeendring(serie, FREDAG_02_10, FREDAG_09_10)
        mnd, fra_mnd = periodeendring(serie, ONSDAG_09_09, FREDAG_09_10)
        assert uke == pytest.approx(37.5) and fra_uke == FREDAG_02_10
        assert mnd == pytest.approx(120.0) and fra_mnd == ONSDAG_09_09

    def test_1_uke_og_1_mnd_paa_siden(self, klient):
        """Ville feilet hvis tabellen viste endringen fra dagen før ved en
        periode, eller ikke sa hvilken periode kolonnen gjelder."""
        _basen()
        siste = _rad(klient.get("/").data.decode("utf-8"), "EQNR")[1]
        uke_html = klient.get("/?periode=1-uke").data.decode("utf-8")
        mnd_html = klient.get("/?periode=1-mnd").data.decode("utf-8")
        assert "+11,11 %" in siste
        assert "+37,50 %" in _rad(uke_html, "EQNR")[1]
        assert "+120,00 %" in _rad(mnd_html, "EQNR")[1]
        assert "Endringen gjelder 1 uke, fra 02.10 til 09.10." in _synlig(uke_html)
        assert "Endringen gjelder 1 mnd, fra 09.09 til 09.10." in _synlig(mnd_html)

    def test_en_kortere_serie_regnes_fra_foerste_dag_og_sier_det(self, klient):
        """AKRBP begynner 05.10: 210 mot 200 er +5,00 %, og raden sier «fra
        05.10». Ville feilet hvis aksjen fikk «–», eller tallet sto uten
        datoen."""
        _basen()
        html = klient.get("/?periode=1-mnd").data.decode("utf-8")
        tekst = _rad(html, "AKRBP")[1]
        assert "+5,00 %" in tekst and "fra 05.10" in tekst
        assert 'class="fra"' not in _rad_html(html, "EQNR")

    def test_sluttkursen_og_signalet_gjelder_siste_boersdag(self, klient):
        """Svar a kl. 12:35. Ville feilet hvis sluttkursen eller signalet
        fulgte perioden: sluttkursen 09.10 er 120,00, og signalet 3 av 3."""
        _basen()
        html = klient.get("/?periode=1-uke").data.decode("utf-8")
        klasse, tekst = _rad(html, "EQNR")
        assert "120,00" in tekst and "3 av 3" in tekst
        assert klasse == "utslag alle"
        assert "Sluttkursen og signalet gjelder siste børsdag." in _synlig(html)


class TestVelgDag:
    def test_dagen_viser_det_som_er_lagret(self, klient):
        """Onsdag 07.10: EQNR har 2 av 3 lagret, og endringen den dagen er
        0,00 % (100 mot 100). Ville feilet hvis siden viste signalet for
        siste børsdag."""
        _basen()
        tekst = _rad(klient.get("/?periode=velg&dag=2026-10-07").data.decode("utf-8"), "EQNR")[1]
        assert "2 av 3" in tekst and "0,00 %" in tekst and "100,00" in tekst
        assert "3 av 3 siste børsdag" in tekst

    def test_en_dag_uten_rad_og_en_dag_som_ikke_er_boersdag(self, klient):
        """Tirsdag 06.10 har ingen rad i vurdering, og lørdag 03.10 er ikke
        børsdag. Ville feilet hvis signalet ble regnet på nytt (AD-7)."""
        _basen()
        tirsdag = _rad(klient.get("/?periode=velg&dag=2026-10-06").data.decode("utf-8"), "DNB")[1]
        loerdag = _rad(klient.get("/?periode=velg&dag=2026-10-03").data.decode("utf-8"), "DNB")[1]
        assert "– ikke vurdert" in tirsdag and "av 3" not in tirsdag
        assert "– ikke børsdag" in loerdag

    def test_foer_vurderingene_i_demoen_uten_signal(self, klient, monkeypatch):
        """Demoen har vurderinger fra 21.09. Ville feilet hvis «Velg dag»
        15.09 viste et signal, for eksempel ett regnet av kursene."""
        sti = lagring_sqlite.demo_sti()
        sti.parent.mkdir(parents=True, exist_ok=True)
        mal = sti.with_name("demomal.db")
        demo.lag_demobase(mal, skriv=lambda _: None, med_ki=False)
        shutil.copy(mal, sti)
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        html = klient.get("/?periode=velg&dag=2026-09-15").data.decode("utf-8")
        rader = re.findall(r"<td class=\"selskap\">(.*?)</tr>", html, re.DOTALL)
        assert len(rader) == 15
        for rad in rader:
            tekst = _synlig(rad).replace("3 av 3 siste børsdag", "")
            assert "av 3" not in tekst, tekst
            assert "ikke vurdert" in tekst or "uten data" in tekst, tekst
        assert "Tabellen viser tirsdag 15.09" in _synlig(html)


class TestGultOgToAvTre:
    def test_gult_fra_siste_boersdag_ogsaa_en_annen_dag(self, klient):
        """Designregler §3. 07.10 har DNB 3 av 3 og EQNR 2 av 3, mens siste
        børsdag har EQNR 3 av 3 og DNB 2 av 3. Ville feilet hvis gult kom
        fra dagen som vises, eller 2 av 3 ble merket en annen dag."""
        _basen()
        html = klient.get("/?periode=velg&dag=2026-10-07").data.decode("utf-8")
        eqnr_klasse, eqnr = _rad(html, "EQNR")
        dnb_klasse, dnb = _rad(html, "DNB")
        assert eqnr_klasse == "gul" and "3 av 3 siste børsdag" in eqnr
        assert dnb_klasse == "" and "siste børsdag" not in dnb and "3 av 3" in dnb
        for symbol in ("EQNR", "DNB"):
            celle = _rad_html(html, symbol)
            assert "tre-av-tre" not in celle and "to-av-tre" not in celle and "skiller seg ut" not in celle

    def test_ved_en_periode_merkes_2_av_3_som_paa_siste_boersdag(self, klient):
        """Ved en periode gjelder signalet siste børsdag, så 2 av 3 merkes.
        Ville feilet hvis perioden tok bort merkingen."""
        _basen()
        html = klient.get("/?periode=1-uke").data.decode("utf-8")
        assert _rad(html, "EQNR")[0] == "utslag alle"
        assert _rad(html, "DNB")[0] == "utslag"
        assert "pille to-av-tre" in _rad_html(html, "DNB")


class TestSoeyleneOgLinja:
    def test_soeylene_og_linja_foelger_perioden(self, klient):
        """1 uke: EQNR +37,50 % og indeksen +10,00 %. Ville feilet hvis
        søylene viste endringen for siste børsdag mens tabellen viste en uke."""
        _basen(med_indeks=True)
        html = klient.get("/?periode=1-uke").data.decode("utf-8")
        lista = _soeylelista(html)
        eqnr = re.search(r"\(EQNR[^)]*\): ([^.]*)", lista).group(1)
        assert eqnr.startswith("+37,50 %"), lista
        assert "Indeksen, den stiplede linja: +10,00 %." in lista
        assert "Endring per aksje 1 uke, fra 02.10 til 09.10" in lista
        assert "Regnet fra første dag serien har, fordi den ikke går tilbake til 02.10:" in lista

    def test_soeylene_paa_siste_boersdag_og_en_valgt_dag(self, klient):
        """Siste børsdag: EQNR +11,11 % og indeksen 0,00 %. Onsdag 07.10:
        EQNR 0,00 % og indeksen +5,00 %. Ville feilet hvis søylene ikke
        fulgte «Velg dag»."""
        _basen(med_indeks=True)
        siste = _soeylelista(klient.get("/").data.decode("utf-8"))
        dagen = _soeylelista(klient.get("/?periode=velg&dag=2026-10-07").data.decode("utf-8"))
        assert re.search(r"\(EQNR[^)]*\): \+11,11 %", siste)
        assert "Indeksen, den stiplede linja: 0,00 %." in siste
        assert re.search(r"\(EQNR[^)]*\): 0,00 %", dagen)
        assert "Indeksen, den stiplede linja: +5,00 %." in dagen
        assert "Endring per aksje 07.10" in dagen

    def test_bransjesymbolet_er_gult_ved_3_av_3_siste_boersdag(self, klient):
        """Som før (FR-105): EQNR har 3 av 3 siste børsdag og DNB 2 av 3,
        også med en valgt dag der det er omvendt."""
        _basen(med_indeks=True)
        html = klient.get("/?periode=velg&dag=2026-10-07").data.decode("utf-8")
        etiketter = {s: k for k, s in re.findall(r'<a class="etikett( tre-av-tre)?" href="/aksje/([A-Z]+)"', html)}
        assert etiketter["EQNR"] == " tre-av-tre" and etiketter["DNB"] == ""


class TestAdressen:
    def test_siste_boersdag_er_valgt_naar_siden_aapnes(self, klient):
        """Designregler §2. Ville feilet hvis oversikten åpnet med 6 mnd som
        kursgrafen."""
        _basen()
        html = klient.get("/").data.decode("utf-8")
        valgt = re.findall(r'<a href="/\?periode=([a-z0-9-]+)" aria-current="true">', html)
        assert valgt == ["siste"]
        assert 'aria-label="Periode for oversikten"' in html

    def test_perioden_og_dagen_staar_i_adressen_ved_sortering(self, klient):
        """Ville feilet hvis et klikk i kolonneraden tok bort perioden eller
        dagen, eller «Standard rekkefølge» og stjernen gikk til siste børsdag."""
        _basen()
        uke = klient.get("/?periode=1-uke").data.decode("utf-8")
        assert 'href="/?periode=1-uke&amp;sorter=endring&amp;orden=synkende"' in uke
        sortert = klient.get("/?periode=1-uke&sorter=endring&orden=synkende").data.decode("utf-8")
        assert re.findall(r'<a href="/\?periode=([a-z0-9-]+)" aria-current="true">', sortert) == ["1-uke"]
        assert "+37,50 %" in _rad(sortert, "EQNR")[1]
        assert 'href="/?periode=1-uke">Standard rekkefølge</a>' in sortert
        assert 'name="tilbake" value="/?periode=1-uke&amp;sorter=endring&amp;orden=synkende"' in sortert
        dagen = klient.get("/?periode=velg&dag=2026-10-07").data.decode("utf-8")
        assert 'href="/?periode=velg&amp;dag=2026-10-07&amp;sorter=endring&amp;orden=synkende"' in dagen

    def test_merkingen_sender_tilbake_med_perioden(self, klient):
        """Ville feilet hvis stjernen sendte tilbake til siste børsdag, eller
        godtok en ukjent periode."""
        assert app_modul.tilbake_etter_merking("/?periode=1-uke&sorter=kurs&orden=stigende") == (
            "/?periode=1-uke&sorter=kurs&orden=stigende"
        )
        assert app_modul.tilbake_etter_merking("/?periode=velg&dag=2026-10-07") == "/?periode=velg&dag=2026-10-07"
        assert app_modul.tilbake_etter_merking("/?periode=tull") == "/"
        assert app_modul.tilbake_etter_merking("/min-liste?periode=1-uke") == "/min-liste"

    def test_en_feil_i_adressen_gir_siste_boersdag_med_en_beskjed(self, klient):
        """Ville feilet med en feilside, eller med 6 mnd som i kursgrafen."""
        _basen()
        html = klient.get("/?periode=tull").data.decode("utf-8")
        assert "Perioden «tull» finnes ikke, så oversikten viser siste børsdag." in html
        assert "+11,11 %" in _rad(html, "EQNR")[1]

    def test_min_liste_har_ikke_periodevalget(self, klient):
        """8.17b tar Min liste. Ville feilet hvis Min liste fikk knappene nå."""
        _basen()
        html = klient.get("/min-liste?vis=alle&periode=1-uke").data.decode("utf-8")
        assert 'class="periodevalg"' not in html


class TestTilgjengelig:
    def test_knappene_brytes_paa_smal_skjerm_og_har_fokus(self, klient):
        """390 px uten vannrett rulling: knappene brytes, og fokus er synlig.
        Ville feilet hvis raden med knappene ikke kunne brytes."""
        css = (Path(__file__).parent.parent / "src" / "static" / "stil.css").read_text(encoding="utf-8")
        assert "nav.periodevalg ul { display: flex; flex-wrap: wrap;" in css
        assert re.search(r"\.periodehode \{[^}]*flex-wrap: wrap", css)
        assert "nav.periodevalg a:focus-visible" in css

    def test_skjermleseren_hoerer_perioden_og_dagen(self, klient):
        """Ville feilet hvis skjermleseren bare fikk tallene uten å høre hva
        de gjelder: linja over tabellen sier det med ord."""
        _basen()
        html = klient.get("/?periode=velg&dag=2026-10-07").data.decode("utf-8")
        assert '<label class="skjult" for="velg-dag">Velg dag</label>' in html
        assert "Tabellen viser onsdag 07.10" in _synlig(html)
        assert 'aria-current="true">07.10</button>' in html
