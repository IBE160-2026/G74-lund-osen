"""Story 8.17b: periodevalget i Min liste («Sammenlign med») og i børsometeret.

Kontrollpunktene i spesifikasjonen
spec-8-17b-periodevalget-i-min-liste-og-boersometeret.md. Ingen nettverk
(AD-8): basen ligger i tmp_path (conftest.py), og demobasen lages der den
også. Seriene og de håndregnede tallene er de fra 8.17a
(test_periodevalget_oversikten.py): EQNR er 110 siste børsdag 09.10, 80
fredag 02.10 (1 uke), 50 onsdag 09.09 (1 mnd) og 100 onsdag 07.10, med
sluttkursen 105 den dagen. AKRBP begynner mandag 05.10 med 200 og er 210
siste børsdag.
"""

import re
from datetime import date, datetime
from pathlib import Path

import pytest

import app as app_modul
from boersometer import BRANSJER, Rute, bygg_boersometer, kart, med_perioden
from kursdata import Aksje, Kursrad
from test_app import HENTET, _boersdager_til, _synlig, fotnoten, skriv_serie
from test_demo import demobase, mal  # noqa: F401 - fiksturer
from test_hjelpefeltet import _kjoer
from test_periodevalget_oversikten import (  # noqa: F401 - fiksturer
    BREDDEN,
    FREDAG_02_10,
    MANDAG_05_10,
    TORSDAG_08_10,
    _basen,
    _rad,
    fast_klokke,
    utenfor_docker,
)


@pytest.fixture
def klient():
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


def _side(klient, adresse: str) -> str:
    svar = klient.get(adresse)
    assert svar.status_code == 200, adresse
    return svar.data.decode("utf-8")


def _under(html: str, symbol: str) -> tuple[str, str] | None:
    """Den synlige teksten og html-en i linja under raden for symbolet, eller
    None når raden ikke har en."""
    deler = re.split(r"(?=<tr[ >])", html)
    for i, del_ in enumerate(deler):
        if '<td class="selskap">' in del_ and f'href="/aksje/{symbol}"' in del_:
            neste = deler[i + 1] if i + 1 < len(deler) else ""
            if neste.startswith('<tr class="sammenligning">'):
                linja = neste.split("</tr>", 1)[0]
                return re.sub(r"[ \t\r\n]+", " ", _synlig(linja)).strip(), linja
            return None
    raise AssertionError(f"ingen rad for {symbol}")


class TestLinjaUnder:
    def test_1_uke_og_1_mnd_mot_den_haandregnede_serien(self, klient):
        """Linja under er dagen den første kursen i perioden er fra: 80 fredag
        02.10 for 1 uke og 50 onsdag 09.09 for 1 mnd, med endringen derfra
        til siste børsdag, 110 mot 80 og 110 mot 50. Øverst står siste
        børsdag som før. Ville feilet hvis linja var regnet fra dagen før
        startdagen (100, så +10,00 %), eller øverste linje viste perioden."""
        _basen()
        uke = _side(klient, "/min-liste?vis=alle&periode=1-uke")
        tekst, _ = _under(uke, "EQNR")
        assert tekst.startswith(
            "Equinor, sammenlignet med fredag 02.10 80,00 +37,50 % til siste børsdag – ikke vurdert"
        ), tekst
        assert "+11,11 %" in _rad(uke, "EQNR")[1]
        mnd = _side(klient, "/min-liste?vis=alle&periode=1-mnd")
        tekst, _ = _under(mnd, "EQNR")
        assert tekst.startswith("Equinor, sammenlignet med onsdag 09.09 50,00 +120,00 % til siste børsdag"), tekst

    def test_en_kortere_serie(self, klient):
        """AKRBP begynner mandag 05.10, etter startdagen for 1 uke, så linja
        under er den dagen: 200 og +5,00 % til 210. Ville feilet hvis linja
        sa startdagen, eller var «–» fordi serien mangler den."""
        _basen()
        tekst, _ = _under(_side(klient, "/min-liste?vis=alle&periode=1-uke"), "AKRBP")
        assert f"sammenlignet med mandag {MANDAG_05_10:%d.%m} 200,00 +5,00 %" in tekst, tekst

    def test_signalet_er_det_som_er_lagret_for_dagen(self, klient):
        """AD-7: linja under har vurderingen som er lagret for dagen, aldri
        regnet på nytt. Fredag 02.10 har ingen, så «ikke vurdert». Onsdag
        07.10 har EQNR 2 av 3 (T +1 B +1 I 0) og DNB 3 av 3, som tekst uten
        pille og uten 2 av 3-merking (§3). Øverst står siste børsdag: EQNR 3
        av 3. Ville feilet hvis signalet ble regnet for dagen, eller linja
        under viste siste børsdag."""
        _basen()
        tekst, _ = _under(_side(klient, "/min-liste?vis=alle&periode=1-uke"), "EQNR")
        assert tekst.endswith("– ikke vurdert"), tekst
        dag = _side(klient, "/min-liste?vis=alle&periode=velg&dag=2026-10-07")
        eqnr, eqnr_html = _under(dag, "EQNR")
        assert eqnr.startswith(
            "Equinor, sammenlignet med onsdag 07.10 105,00 +10,00 % til siste børsdag 2 av 3 T +1 B +1 I 0"
        ), eqnr
        dnb, dnb_html = _under(dag, "DNB")
        assert "3 av 3" in dnb
        for linja in (eqnr_html, dnb_html):
            assert 'class="pille' not in linja and "skiller seg ut" not in linja and 'class="gul' not in linja
        assert "3 av 3" in _rad(dag, "EQNR")[1] and _rad(dag, "EQNR")[0] == "utslag alle"
        assert "ikke vurdert" not in eqnr
        # Fotnoten for «ikke vurdert» står når linja under sier det.
        assert fotnoten(_side(klient, "/min-liste?vis=alle&periode=1-uke"))

    def test_siste_boersdag_har_ingen_linje_under(self, klient):
        """Siden åpner med siste børsdag, uten noe å sammenligne med. Ville
        feilet med en linje under uten periode."""
        _basen()
        html = _side(klient, "/min-liste?vis=alle")
        assert '<tr class="sammenligning">' not in html
        assert 'aria-current="true">Fredag</a>' in html

    def test_en_dag_uten_kurs_for_aksjen(self, klient):
        """«Velg dag» har ikke unntaket: AKRBP har ingen kurs onsdag 30.09,
        så linja under har «–» og grunnen. Ville feilet med kursen fra en
        annen dag."""
        _basen()
        tekst, _ = _under(_side(klient, "/min-liste?vis=alle&periode=velg&dag=2026-09-30"), "AKRBP")
        assert tekst.endswith("onsdag 30.09 – – – ingen kurs fra dagen"), tekst


class TestDemoen:
    def test_velg_dag_foer_vurderingene_i_demoen(self, klient, demobase, monkeypatch):  # noqa: F811
        """Demoen har vurderinger fra mandag 21.09. «Velg dag» fredag 18.09
        gir «ikke vurdert» i hver linje under og ingen signal, og fotnoten
        står. Ville feilet hvis et signal ble regnet for dagen.

        Rettet 2026-11-14 (story 2.17, gruppens svar kl. 05:41-05:49): 18.09
        har signalet regnet i ettertid, merket «i ettertid» i hver linje, og
        ingen fotnote. Fredag 06.03 har for få kurser og er «ikke vurdert»,
        med fotnoten. Ville feilet hvis 18.09 sto uten merket, eller 06.03 fikk
        et signal."""
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        html = _side(klient, "/min-liste?periode=velg&dag=2026-09-18")
        linjene = re.findall(r'<tr class="sammenligning">(.*?)</tr>', html, re.S)
        assert len(linjene) == 5, len(linjene)
        for linja in linjene:
            tekst = _synlig(linja)
            assert "fredag 18.09" in tekst and "i ettertid" in tekst and "av 3" in tekst, tekst
        html = _side(klient, "/min-liste?periode=velg&dag=2026-03-06")
        linjene = re.findall(r'<tr class="sammenligning">(.*?)</tr>', html, re.S)
        assert len(linjene) == 5, len(linjene)
        for linja in linjene:
            tekst = _synlig(linja)
            assert "fredag 06.03" in tekst and "ikke vurdert" in tekst and "av 3" not in tekst, tekst
        assert fotnoten(html)

    def test_boersometeret_i_demoen_ved_en_periode(self, klient, demobase, monkeypatch):  # noqa: F811
        """Ville feilet hvis demoen ikke hadde knappene i børsometeret, eller
        siden ikke sa at rutene er like store."""
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        html = _side(klient, "/boersometer?periode=1-mnd")
        assert 'aria-current="true">1 mnd</a>' in html
        assert "rutene er like store, fordi volumet mot vanlig gjelder én dag" in html


class TestEgenDag:
    @staticmethod
    def _basen_med_en_eldre_dag():
        """KOG har siste kurs torsdag 08.10, en dag før siden."""
        _basen()
        rader = [Kursrad(dato=d, slutt=50.0, justert_slutt=50.0, volum=1) for d in _boersdager_til(TORSDAG_08_10, 70)]
        skriv_serie("KOG", rader, datetime.fromisoformat(HENTET), vurdert=False)

    def test_raden_viser_datoen_sin_i_oversikten_og_min_liste(self, klient):
        """Gruppens svar 03.11 kl. 14:28: en rad med eldre dag enn sidens
        viser datoen sin, i oversikten og i Min liste, også ved en periode.
        Ville feilet hvis raden viste sidens dato (09.10), eller hvis en rad
        med sidens dag også fikk datoen."""
        self._basen_med_en_eldre_dag()
        for adresse in ("/", "/?periode=1-uke", "/min-liste?vis=alle", "/min-liste?vis=alle&periode=1-uke"):
            html = _side(klient, adresse)
            assert "siste kurs torsdag 08.10" in _rad(html, "KOG")[1], adresse
            assert "siste kurs" not in _rad(html, "EQNR")[1], adresse
            assert "siste kurs fredag 09.10" not in html, adresse

    def test_ikke_ved_velg_dag_i_oversikten(self, klient):
        """Ved «Velg dag» er hver rad dagen. Ville feilet med «siste kurs»."""
        self._basen_med_en_eldre_dag()
        assert "siste kurs" not in _side(klient, "/?periode=velg&dag=2026-10-07")


class TestAdressen:
    def test_perioden_i_adressen_i_min_liste(self, klient):
        """Perioden og dagen står i lenkene for periodene, «Alle / Min
        liste», sorteringen og merkingen, og «Alle» følger med knappene.
        Ville feilet hvis et klikk mistet perioden eller «Alle»."""
        _basen()
        html = _side(klient, "/min-liste?vis=alle&periode=1-uke&sorter=kurs&orden=synkende")
        assert '<a href="/min-liste?vis=alle&amp;periode=1-mnd#perioden">1 mnd</a>' in html
        assert '<a href="/min-liste?vis=alle&amp;periode=1-uke#perioden" aria-current="true">1 uke</a>' in html
        assert '<input type="hidden" name="vis" value="alle">' in html
        assert 'href="/min-liste?vis=alle&amp;periode=1-uke&amp;sorter=kurs&amp;orden=synkende#visvalget"' in html
        assert 'href="/min-liste?periode=1-uke&amp;sorter=kurs&amp;orden=synkende#visvalget"' in html
        assert 'name="tilbake" value="/min-liste?vis=alle&amp;periode=1-uke&amp;sorter=kurs&amp;orden=synkende"' in html
        assert "periode=1-uke&amp;sorter=endring" in html
        dag = _side(klient, "/min-liste?vis=alle&periode=velg&dag=2026-10-07")
        # Story 8.20a (del B): dagen står i feltet, og knappen heter «Vis dagen».
        assert 'required value="2026-10-07"' in dag and 'aria-current="true">Vis dagen</button>' in dag
        assert app_modul.tilbake_etter_merking("/min-liste?periode=velg&dag=2026-10-07") == (
            "/min-liste?periode=velg&dag=2026-10-07"
        )

    def test_en_feil_i_adressen_gir_siste_boersdag(self, klient):
        """Ville feilet med en feilside, eller uten beskjeden."""
        _basen()
        html = _side(klient, "/min-liste?vis=alle&periode=tull")
        assert "Perioden «tull» finnes ikke, så Min liste viser siste børsdag." in html
        assert '<tr class="sammenligning">' not in html

    def test_perioden_i_adressen_i_boersometeret(self, klient):
        """Ville feilet hvis børsometeret ikke leste perioden, eller «Velg
        dag» ikke ga dagen som før."""
        _basen()
        html = _side(klient, "/boersometer?periode=1-uke")
        assert '<a href="/boersometer?periode=1-uke#perioden" aria-current="true">1 uke</a>' in html
        assert 'aria-current="true">Fredag</a>' in _side(klient, "/boersometer")
        dag = _side(klient, "/boersometer?periode=velg&dag=2026-10-07")
        # Story 8.20a (del B): dagen står i feltet, og knappen heter «Vis dagen».
        assert 'required value="2026-10-07"' in dag and 'aria-current="true">Vis dagen</button>' in dag
        assert "Mandag" not in dag.split('class="meta"', 1)[1].split("</p>", 1)[0]
        assert "onsdag 07.10" in dag.split('class="meta"', 1)[1].split("</p>", 1)[0]


def _aksje(symbol: str) -> Aksje:
    return Aksje(symbol, f"{symbol}.OL", f"Selskap {symbol}", BRANSJER[0])


class TestRutene:
    def test_like_store_ruter_ved_en_periode(self):
        """Gruppens svar 23.10 kl. 12:35 (b): ved en periode er rutene like
        store, fordi volumet mot vanlig gjelder én dag. Ville feilet hvis
        rutene fulgte volumforholdet også ved en periode."""
        serie = [
            Kursrad(dato=FREDAG_02_10, slutt=80.0, justert_slutt=80.0, volum=1),
            Kursrad(dato=date(2026, 10, 9), slutt=110.0, justert_slutt=110.0, volum=1),
        ]
        ruter = [
            Rute(aksje=_aksje(s), endring=1.0, volumforhold=v, styrke=1, tekst=None)
            for s, v in (("A", 0.5), ("B", 1.0), ("C", 2.9))
        ]
        foer = kart(bygg_boersometer(ruter))
        assert len({kr.vekt for kr in foer.felt[0].ruter}) == 3
        perioden = [med_perioden(r, serie, FREDAG_02_10, date(2026, 10, 9)) for r in ruter]
        etter = kart(bygg_boersometer(perioden))
        assert {kr.vekt for kr in etter.felt[0].ruter} == {1.0}
        for flate in ("bred", "smal"):
            arealer = [kr.plass[flate].b * kr.plass[flate].h for kr in etter.felt[0].ruter]
            assert max(arealer) == pytest.approx(min(arealer), rel=1e-6), (flate, arealer)
        assert [r.endring for r in perioden] == pytest.approx([37.5] * 3)
        assert all(r.volumforhold is not None for r in perioden)

    def test_fargen_er_endringen_for_perioden(self, klient):
        """Fargen og tallet i ruta er endringen for perioden, 110 mot 80, og
        siste børsdag ser ut som før, 110 mot 99. Ville feilet hvis ruta
        viste dagens endring ved en periode."""
        _basen()
        perioden = _side(klient, "/boersometer?periode=1-uke")
        siste = _side(klient, "/boersometer")
        rute = re.compile(
            r'<a class="(rute [^"]*)" href="/aksje/EQNR"[^>]*>.*?<span class="endring">(.*?)</span>', re.S
        )
        klasse, tall = rute.search(perioden).groups()
        assert tall == "+37,50 %" and "trinn-opp" in klasse
        assert rute.search(siste).group(2) == "+11,11 %"
        # Story 8.20b (spørsmål 14 b): kortet «Mål mot børsen» sier perioden
        # og at rutene er like store, og for én dag at størrelsen følger volumet.
        maal = " ".join(_synlig(perioden.split('class="maal"')[1].split("</section>")[0]).split())
        assert "1 uke, fra 02.10 til" in maal
        assert "endringen for 1 uke, og rutene er like store, fordi volumet mot vanlig gjelder én dag" in maal
        en_dag = " ".join(_synlig(siste.split('class="maal"')[1].split("</section>")[0]).split())
        assert "jo mer det ble handlet enn vanlig, jo større rute" in en_dag and "like store" not in en_dag

    def test_rammen_er_signalet_siste_boersdag_ved_en_periode(self, klient):
        """§3: gult ved 3 av 3 siste børsdag og mørk ved 2 av 3, også ved en
        periode, fordi signalet er siste børsdag. Ville feilet uten rammen."""
        _basen()
        html = _side(klient, "/boersometer?periode=1-mnd")
        assert re.search(r'<a class="rute [^"]*ramme-gul[^"]*" href="/aksje/EQNR"', html)
        assert re.search(r'<a class="rute [^"]*ramme-moerk[^"]*" href="/aksje/DNB"', html)


class TestTilgjengelig:
    def test_skjermleseren_hoerer_hva_linja_under_gjelder(self, klient):
        """Linja under sier med ord hvilken aksje og dag den gjelder, og
        valget har en overskrift og et navn. Ville feilet hvis
        skjermleseren bare fikk tallene."""
        _basen()
        html = _side(klient, "/min-liste?vis=alle&periode=velg&dag=2026-10-07")
        assert '<h2 class="sammenlign-tittel" id="sammenlign-med">Sammenlign siste børsdag med</h2>' in html
        assert '<nav class="periodevalg" aria-label="Sammenlign siste børsdag med">' in html
        # Story 8.20c (U101, spørsmål 19 i 8.20). Ville feilet hvis det gamle
        # navnet sto igjen på siden eller i hjelpen.
        assert "Sammenlign med" not in _synlig(html)
        assert 'aria-label="Hjelp: sammenlign siste børsdag med"' in html
        assert 'sammenlign med"' not in html.lower()
        assert "«Sammenlign med»" not in (Path(__file__).resolve().parent.parent / "docs" / "hjelp.md").read_text(
            encoding="utf-8"
        )
        assert '<span class="skjult">Equinor, sammenlignet med </span>onsdag 07.10' in html
        assert '<span class="skjult"> til siste børsdag</span>' in html
        assert "Linja under er onsdag 07.10" in _synlig(html)

    @pytest.mark.parametrize(
        "adresse",
        [
            "/min-liste?vis=alle&periode=1-uke",
            "/min-liste?vis=alle&periode=velg&dag=2026-10-07",
            "/boersometer?periode=1-uke",
            "/boersometer?periode=velg&dag=2026-10-07",
        ],
    )
    def test_ingen_vannrett_rulling_paa_390_px(self, klient, tmp_path, adresse):
        """Ville feilet hvis Min liste eller børsometeret fikk vannrett
        rulling på 390 px med periodevalget og linja under."""
        _basen()
        html = _side(klient, adresse)
        assert 'class="periodehode"' in html
        r = _kjoer(html, tmp_path, 390, BREDDEN)
        assert r == {"rull": 390, "brede": []}, r


class TestGjennomgangen:
    """Gjennomgangen 03.11 av dc8a5b0..7844af6 (spesifikasjonen, «Gjennomgangen»)."""

    def test_hovedindeksen_for_perioden_i_boersometeret(self, klient):
        """VG1, BH11: «Mål mot børsen» har indeksens endring for perioden,
        1000 fredag 02.10 mot 1100 siste børsdag, +10,00 %, ikke dagens
        0,00 %. ECH1: begynner indeksen etter starten, står «–», som
        indekslinja i oversikten. Ville feilet med dagens endring, eller
        med endringen over en kortere tid."""
        _basen(med_indeks=True)

        def maal(adresse):
            # Story 8.20b: tallet for hovedindeksen i kortet «Mål mot børsen».
            seksjon = _side(klient, adresse).split('class="maal"')[1].split("</section>")[0]
            return _synlig(re.search(r'<span class="indeksendring[^"]*">(.*?)</span>', seksjon).group(1)).strip()

        assert maal("/boersometer?periode=1-uke") == "+10,00 %"
        assert maal("/boersometer") == "0,00 %"
        assert maal("/boersometer?periode=1-mnd") == "–"

    def test_en_kortere_serie_i_boersometeret(self, klient):
        """VG2: AKRBP begynner mandag 05.10, så ruta har +5,00 %, og tabellen
        sier «fra 05.10». Ville feilet uten «fra», eller med «–»."""
        _basen()
        html = _side(klient, "/boersometer?periode=1-uke")
        tabell = html.split('<table class="boersometertabell">')[1]
        rad = next(r for r in tabell.split("<tr>") if "Aker BP" in r)
        assert "+5,00 % fra 05.10" in _synlig(rad)

    def test_en_kortere_serie_telles_ikke_mot_indeksen(self, klient):
        """Gjennomgangen av 8.20b (BH1, ECH2): AKRBP begynner 05.10, så
        endringen gjelder et annet tidsrom enn indeksen, og aksjen telles ikke
        i «N av M gikk bedre enn indeksen». Ville feilet med AKRBP i M."""
        _basen(med_indeks=True)
        html = _side(klient, "/boersometer?periode=1-uke")
        kortet = html.split('class="maal"')[1].split("</section>")[0]
        m = int(re.search(r"<strong>\d+ av (\d+)</strong>", kortet).group(1))
        tabell = html.split('<table class="boersometertabell">')[1]
        med_fra = tabell.count('<span class="fra">fra ')
        endringer = len(re.findall(r'<td class="tall"><span class="(?:opp|ned|null)">', tabell))
        assert med_fra >= 1 and m == endringer - med_fra

    def test_linja_under_for_en_rad_med_eldre_dag(self, klient):
        """VG3: linja under går til radens egen siste dag, 08.10 for KOG,
        med 50 begge dagene, så 0,00 %. Ville feilet med «–» hvis sidens
        dag ble brukt som slutt."""
        TestEgenDag._basen_med_en_eldre_dag()
        tekst, _ = _under(_side(klient, "/min-liste?vis=alle&periode=1-uke"), "KOG")
        assert "fredag 02.10 50,00 0,00 %" in tekst, tekst

    def test_fargen_i_linja_under(self, klient):
        """VG4: endringen i linja under har fargen etter tallet. Ville
        feilet uten klassen opp."""
        _basen()
        _, linja = _under(_side(klient, "/min-liste?vis=alle&periode=1-uke"), "EQNR")
        assert '<td class="tall opp">' in linja

    def test_kolonneraden_i_min_liste_er_siste_boersdag(self, klient):
        """Funnet i bildene: øverste linje i Min liste er siste børsdag, så
        kolonneraden sier ikke perioden eller dagen under «Endring». Ville
        feilet med «1 uke» eller «07.10» under kolonnenavnet."""
        _basen()
        for adresse in ("/min-liste?vis=alle&periode=1-uke", "/min-liste?vis=alle&periode=velg&dag=2026-10-07"):
            hode = _side(klient, adresse).split("<thead>")[1].split("</thead>")[0]
            assert "1 uke" not in hode and "07.10" not in hode, adresse
        assert '<span class="under">1 uke</span>' in _side(klient, "/?periode=1-uke")
