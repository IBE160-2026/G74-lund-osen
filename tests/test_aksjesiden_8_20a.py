"""Story 8.20a: aksjesiden og periodevalget med datoen på alle sidene
(spesifikasjonen spec-8-20-ux-rettingene-etter-gjennomgangen-06-11.md, med
gruppens svar 07.11 kl. 10:33, 12:32 og 15:34).

Delene A-E og G, U88 for aksjesiden og periodevalget, og det som hører til
dem i J og K. Del G (hjelpefeltet) står som før og testes i
test_hjelpefeltet.py. Ingen nett: demobasen lages i tmp_path, som i
test_ki_teksten_forklarer.py.
"""

import re
import shutil
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

import app as app_modul
import demo
from dokumentene import installasjonen
from hjelpetekster import hjelpetekster
from ki_visning import KAPSEL, ki_tekst
from lagring_sqlite import demo_sti
from perioder import SEKS_MND, SISTE, VELG, dagen_i_feltet, pilene

ROT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def fast_klokke(monkeypatch):
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


def _side(klient, adresse: str) -> str:
    svar = klient.get(adresse)
    assert svar.status_code == 200, adresse
    return svar.get_data(as_text=True)


def _synlig(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _periodevalget(html: str) -> str:
    return html.split('<nav class="periodevalg"', 1)[1].split("</nav>", 1)[0]


def _siste_dag(html: str) -> date:
    return date.fromisoformat(re.search(r'max="(\d{4}-\d{2}-\d{2})"', _periodevalget(html)).group(1))


# --- Del A: toppen og summen -------------------------------------------------


class TestToppenOgSummen:
    def test_fotnoten_under_summen_er_flyttet_til_hjelpen(self, klient):
        """Del A (svaret 06.11 kl. 22:25, spørsmål 3): ville feilet hvis
        fotnoten sto igjen under summen, eller «ingen vekting» ikke sto i noe
        vindu på siden. Da er setningen borte, ikke flyttet."""
        html = _side(klient, "/aksje/BRFE")
        etter_summen = html.split('<p class="sumrad">', 1)[1].split("</p>", 1)[1]
        assert not etter_summen.lstrip().startswith('<p class="fotnote">')
        assert "Ingen vekting og ingen skjult formel" not in html
        vinduene = html.split('<div id="hjelp-', 1)[1]
        assert "uten vekting" in vinduene

    def test_to_av_tre_har_svart_ring_i_summen_og_kortet(self, klient):
        """Del A (spørsmål 13): ville feilet hvis 2 av 3 sto uten ring i
        summen eller i kortet «Signalstyrke», eller 3 av 3 fikk svart ring.
        Alle aksjene i demoen, og minst én med 2 av 3 og én med 3 av 3."""
        sett = set()
        symbolene = sorted(set(re.findall(r'href="/aksje/([A-Z]+)"', _side(klient, "/"))))
        for symbol in symbolene:
            html = klient.get(f"/aksje/{symbol}").get_data(as_text=True)
            if '<p class="sumrad">' not in html:
                continue
            summen = html.split('<p class="sumrad">', 1)[1].split("</p>", 1)[0]
            styrke = int(re.search(r'<span class="pille[^"]*">(\d) av 3</span>', summen).group(1))
            sett.add(styrke)
            kortet = html.split('<span class="etikett">Signalstyrke', 1)[1].split("</div>", 1)[0]
            if styrke == 2:
                assert '<span class="pille to-av-tre">2 av 3</span>' in summen
                assert 'class="styrken pille to-av-tre"' in kortet
            elif styrke == 3:
                assert '<span class="pille tre-av-tre">3 av 3</span>' in summen
                assert 'class="styrken pille tre-av-tre"' in kortet
            else:
                assert "to-av-tre" not in summen + kortet and "tre-av-tre" not in summen + kortet
        assert {2, 3} <= sett, (symbolene, sett)

    def test_to_av_tre_har_ingen_ring_en_tidligere_dag(self, klient):
        """Gjennomgangen av 8.20a (BH11, ECH1): designregler.md §3 merker 2 av 3
        bare for siste børsdag. Ville feilet hvis en tidligere dag med 2 av 3
        fikk svart ring."""
        for symbol in sorted(set(re.findall(r'href="/aksje/([A-Z]+)"', _side(klient, "/")))):
            historikken = _side(klient, f"/aksje/{symbol}").split('<section class="historikk"', 1)[1]
            for dag, celle in re.findall(r'href="/aksje/[A-Z]+\?dag=([\d-]+)">(.*?)</li>', historikken, flags=re.S):
                if '<span class="pille">2 av 3</span>' in celle:
                    html = _side(klient, f"/aksje/{symbol}?dag={dag}")
                    if 'class="tidligere-dag"' not in html:
                        continue
                    summen = html.split('<p class="sumrad">', 1)[1].split("</p>", 1)[0]
                    assert '<span class="pille">2 av 3</span>' in summen and "to-av-tre" not in html
                    return
        pytest.fail("ingen tidligere dag med 2 av 3 i demoen")

    def test_ringen_har_stil(self):
        stil = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
        assert ":where(.side-aksje) .sumrad .pille.to-av-tre { border: 1.5px solid var(--blekk);" in stil
        assert ":where(.side-aksje) .noekkeltall .styrken.to-av-tre { border: 2px solid var(--blekk);" in stil


# --- Del B: periodevalget og datoen på alle sidene ------------------------------

SIDENE = ("/aksje/BRFE", "/", "/min-liste?vis=alle", "/boersometer")


class TestDatoen:
    @pytest.mark.parametrize("side", SIDENE)
    def test_feltet_viser_dagen_ved_den_foerste_knappen(self, klient, side):
        """Del B (svarene 06.11 kl. 23:34 og 23:42): ville feilet hvis feltet
        var tomt ved den første knappen."""
        skille = "&" if "?" in side else "?"
        html = _side(klient, f"{side}{skille}periode={SISTE}")
        valget = _periodevalget(html)
        siste = _siste_dag(html)
        # Gjennomgangen av 8.20a (BH5): siste børsdag fra kortene på
        # aksjesiden, ikke bare max i det samme feltet.
        meta = re.search(r'<p class="meta">[^<]*· (\d{2})\.(\d{2})', _side(klient, "/aksje/BRFE"))
        assert (siste.day, siste.month) == (int(meta.group(1)), int(meta.group(2)))
        assert f'id="velg-dag" name="dag" required value="{siste.isoformat()}"' in valget
        # Neste er grå på siste dag, forrige er en lenke.
        assert re.search(
            r'<a class="pil" href="[^"]*periode=velg&amp;dag=\d{4}-\d{2}-\d{2}[^"]*" aria-label="Forrige børsdag',
            valget,
        )
        assert '<span class="pil av" aria-hidden="true">›</span>' in valget

    @pytest.mark.parametrize("side", SIDENE)
    def test_feltet_er_tomt_og_uten_piler_i_en_periode(self, klient, side):
        """Del B (svaret 07.11 kl. 10:33, 7): ville feilet hvis feltet viste
        en dato i en periode, eller pilene sto der."""
        skille = "&" if "?" in side else "?"
        valget = _periodevalget(_side(klient, f"{side}{skille}periode=1-uke"))
        assert 'name="dag" required value=' not in valget
        assert 'class="pil' not in valget

    @pytest.mark.parametrize("side", SIDENE)
    def test_en_valgt_dag_staar_i_feltet_med_pilene(self, klient, side):
        """Del B: ville feilet hvis en valgt dag ikke sto i feltet, knappen
        ikke het «Vis dagen», eller pilene ikke gikk til forrige og neste
        børsdag over helga."""
        siste = _siste_dag(_side(klient, side))
        dag = siste - timedelta(days=siste.weekday())
        if dag == siste:
            dag -= timedelta(days=7)
        skille = "&" if "?" in side else "?"
        valget = _periodevalget(_side(klient, f"{side}{skille}periode={VELG}&dag={dag.isoformat()}"))
        assert f'required value="{dag.isoformat()}"' in valget
        assert re.search(r'<button type="submit" aria-current="true">Vis dagen</button>', valget)
        # Dagen er en mandag, så forrige børsdag er fredagen før.
        assert f"dag={(dag - timedelta(days=3)).isoformat()}" in valget
        assert f"dag={(dag + timedelta(days=1)).isoformat()}" in valget

    @pytest.mark.parametrize("side", SIDENE)
    def test_ingen_velg_dag_igjen(self, klient, side):
        """Del B og J (spørsmål 5): ville feilet hvis «Velg dag» sto igjen på
        siden, eller feltet ikke het «Dagen siden viser»."""
        html = _side(klient, side)
        assert "Velg dag" not in _synlig(html)
        assert '<label class="skjult" for="velg-dag">Dagen siden viser</label>' in html

    def test_historikken_har_ingen_datovelger(self, klient):
        """Del B (spørsmål 6): ville feilet hvis «Velg dag» i «Signalet dag
        for dag» sto igjen. Dagene i tabellen er fortsatt lenker."""
        html = _side(klient, "/aksje/BRFE")
        historikken = html.split('<section class="historikk"', 1)[1].split("</section>", 1)[0]
        assert 'type="date"' not in historikken and "dagvalg" not in historikken
        assert re.search(r'<a class="dato" href="/aksje/BRFE\?dag=', historikken)
        assert html.count('type="date"') == 1

    def test_datoen_staar_paa_linja_med_knappene_og_bryter_samlet(self):
        """Del B (svarene 06.11 kl. 22:24, 23:23 og 23:30): datoen er et
        element i lista med knappene, så den står på samme linje når det er
        plass, og pilene, feltet og knappen bryter sammen. Ville feilet hvis
        datoen sto i en egen rad, eller kunne gå ut over skjermen ved 390 px."""
        mal = (ROT / "src" / "templates" / "_perioder.html").read_text(encoding="utf-8")
        lista = mal.split("<ul>", 1)[1].split("</ul>", 1)[0]
        assert '<li class="datoen">' in lista
        stil = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
        assert "nav.periodevalg ul { display: flex; flex-wrap: wrap;" in stil
        assert "max-width: 100%;" in stil.split('nav.periodevalg input[type="date"] {', 1)[1].split("}", 1)[0]


class TestPilene:
    def test_over_helga_og_ved_kantene(self):
        """Del B (spørsmål 7): ville feilet hvis pila gikk til en lørdag, eller
        var en lenke forbi første eller siste dag feltet godtar."""
        fredag, mandag = date(2026, 10, 9), date(2026, 10, 12)
        assert pilene(mandag, None, None) == (fredag, date(2026, 10, 13))
        assert pilene(mandag, mandag, None)[0] is None
        assert pilene(fredag, None, fredag)[1] is None
        assert pilene(None, None, None) == (None, None)

    def test_over_en_helligdag(self):
        """Ville feilet hvis pila gikk til julaften eller 2. juledag, som
        børsen har stengt."""
        assert pilene(date(2026, 12, 28), None, None)[0] == date(2026, 12, 23)

    def test_foer_2026_er_en_hverdag_en_boersdag(self):
        """Gjennomgangen av 8.20a (VG1): børskalenderen begynner i 2026, og før
        det er en hverdag en børsdag, som foerste_boersdag_fra. Ville feilet
        med UtenforKalenderen, som ga en feilside for en dag ved nyttår."""
        assert pilene(date(2026, 1, 2), None, None) == (date(2025, 12, 31), date(2026, 1, 5))
        assert pilene(date(2025, 12, 15), None, None) == (date(2025, 12, 12), date(2025, 12, 16))

    def test_med_kursdagene_hoppes_et_hull_over(self):
        """Gjennomgangen av 8.20a (ECH2): børsometeret viser nærmeste dag med
        kurs. Ville feilet hvis neste-pila gikk til hullet, som ga samme dag
        tilbake, eller forbi siste dag feltet godtar."""
        dagene = [date(2026, 10, 5), date(2026, 10, 7), date(2026, 10, 8)]
        assert pilene(date(2026, 10, 5), None, None, dagene) == (None, date(2026, 10, 7))
        assert pilene(date(2026, 10, 7), date(2026, 10, 6), date(2026, 10, 7), dagene) == (None, None)
        mal = (ROT / "src" / "templates" / "boersometer.html").read_text(encoding="utf-8")
        assert "kursdager=kursdager" in mal

    def test_dagen_i_feltet(self):
        siste, dag = date(2026, 10, 9), date(2026, 10, 1)
        assert dagen_i_feltet(SISTE, None, siste) == siste
        assert dagen_i_feltet(VELG, dag, siste) == dag
        assert dagen_i_feltet(SEKS_MND, None, siste) is None


# --- Del C: kursgrafen -------------------------------------------------------


class TestGrafen:
    def test_datoen_i_svart_lapp_og_uten_punktet(self, klient):
        """Del C (spørsmål 9, U89): ville feilet hvis streken ikke hadde
        datoen, eller punktet nederst sto igjen."""
        html = _side(klient, f"/aksje/BRFE?periode={SISTE}")
        siste = _siste_dag(html)
        figuren = html.split("<figure>", 1)[1].split("</figure>", 1)[0]
        assert figuren.count('class="daglapp"') == 2
        assert figuren.count('class="daglapptekst" text-anchor="middle"') == 2
        assert re.search(rf'class="daglapptekst"[^>]*>{siste:%d.%m}</text>', figuren)
        assert "dagpunkt" not in html

    def test_kurslinja_heter_kurs_justert_for_utbytte(self, klient):
        """Del C (spørsmål 10, U90): ville feilet hvis «Utbyttejustert kurs»
        sto igjen i grafen."""
        html = _side(klient, "/aksje/BRFE")
        assert "Kurs (justert for utbytte)" in html
        assert "Utbyttejustert kurs" not in html and "utbyttejustert kurs" not in html

    def test_lappen_ved_musepekeren_er_norsk_og_uten_skript(self, klient):
        """Del C (svaret 07.11 kl. 10:33, 12, U92): ville feilet hvis et tall i
        lappen hadde punktum, lappen var en <title>, eller siden fikk et
        skript utover hjelp.js."""
        html = _side(klient, "/aksje/BRFE")
        figuren = html.split("<figure>", 1)[1].split("</figure>", 1)[0]
        tallene = re.findall(r'<text class="lapptall"[^>]*>([^<]*)</text>', figuren)
        assert tallene and all(re.fullmatch(r"\d[\d ]*,\d{2}", t) for t in tallene), tallene[:5]
        assert "<title>" not in figuren
        assert re.findall(r"<script[^>]*>", html) == [re.search(r"<script[^>]*hjelp\.js[^>]*>", html).group()]
        dager = re.findall(r'<g class="musedag">', figuren)
        datoer = re.findall(r'<text class="lappdato"[^>]*>(\w+ \d{2}\.\d{2})</text>', figuren)
        assert len(dager) == len(datoer) > 100

    def test_lappen_dekker_aldri_punktet(self):
        """Gjennomgangen av 8.20a (ECH3): i den smale grafen får lappen ikke
        plass ved siden av punktet midt i. Ville feilet hvis den ble skjøvet
        inn over punktet den gjelder, eller ut av tegneflaten."""
        from aksjedetalj import Punkt
        from graf import LAPPBREDDE, LAPPHOYDE, MARG_Y, bygg_graf

        punkter = tuple(Punkt(date(2026, 1, 5) + timedelta(days=i), 100.0 + (i % 7) * 3, None) for i in range(60))
        for smal in (False, True):
            g = bygg_graf(punkter, smal=smal)
            for d in g.dager:
                assert not (d.lapp_x <= d.x <= d.lapp_x + LAPPBREDDE and d.lapp_y <= d.y <= d.lapp_y + LAPPHOYDE), d
                assert g.venstre <= d.lapp_x and d.lapp_x + LAPPBREDDE <= g.hoeyre + 0.01, d
                assert MARG_Y <= d.lapp_y and d.lapp_y + LAPPHOYDE <= g.bunn + 0.01, d

    def test_hjelpen_sier_snittet_og_streken_bare_naar_de_vises(self, klient):
        """Gjennomgangen av 8.20a (ECH4, VG2, ECH5): en dag uten vurdering har
        også snittlinja, og en periode har ingen strek. Ville feilet hvis
        hjelpen ikke nevnte snittet en dag uten sjekker, eller nevnte streken
        i en periode."""
        tekster = hjelpetekster()
        ikke_vurdert = _vinduene(_side(klient, "/aksje/BRFE?dag=2026-09-14"))["hjelp-graf"]
        assert "den tynne snittet" in ikke_vurdert
        assert tekster["streken"].tekst in ikke_vurdert
        uke = _vinduene(_side(klient, "/aksje/BRFE?periode=1-uke"))["hjelp-graf"]
        assert tekster["streken"].tekst not in uke and tekster["perioden"].tekst in uke

    def test_lappen_vises_bare_ved_musa(self):
        """Ville feilet hvis lappen var synlig uten musa, eller trengte et
        skript for å vises."""
        stil = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
        assert ":where(.side-aksje) .musefelt .lapp { visibility: hidden;" in stil
        assert ":where(.side-aksje) .musefelt .musedag:hover .lapp { visibility: visible; }" in stil
        assert "transition" not in stil.split(".musefelt .treff", 1)[1].split("/*", 1)[0]


# --- Del D: bunnen av aksjesiden ------------------------------------------------


class TestBunnen:
    @pytest.mark.parametrize("kapsel", [None, "av"])
    def test_linja_nederst_i_rammen_og_ingen_fotnote_to_ganger(self, klient, kapsel):
        """Del D (spørsmål 4): ville feilet hvis setningen om børsmeldinger og
        kommende hendelser forsvant, eller en fotnote sto både etter grafen og
        i rammen."""
        if kapsel:
            klient.set_cookie(KAPSEL, kapsel)
        html = _side(klient, "/aksje/BRFE")
        rammen = html.split('<section class="ki"', 1)[1].split("</section>", 1)[0]
        assert re.search(
            r'<p class="grunnlaget">[^<]*Børsmeldinger og kommende finansielle hendelser er ikke med', rammen
        )
        assert "ikke om du bør kjøpe eller selge" in rammen
        assert _synlig(html).count("Børsmeldinger og kommende finansielle hendelser") == 1
        assert "Signalstyrken sier ikke om du bør kjøpe eller selge." not in html

    def test_uten_sjekker_staar_fotnotene_som_foer(self, klient):
        """Del D: uten rammen står fotnotene etter grafen. Ville feilet hvis
        kravet forsvant på en side uten sjekker."""
        html = _side(klient, "/aksje/VRDS")
        assert '<section class="ki"' not in html
        assert "Børsmeldinger og kommende" in html and "Signalstyrken sier ikke om du bør kjøpe eller selge." in html

    def test_merket_og_modellen_under_teksten(self, klient):
        """Del D (spørsmål 11, U81): ville feilet hvis «Laget av KI» forsvant,
        eller modellnavnet ikke sto i en linje under teksten."""
        rammen = _side(klient, "/aksje/BRFE").split('<section class="ki"', 1)[1].split("</section>", 1)[0]
        assert "Laget av KI." in rammen
        assert rammen.index('<p class="ki-tekst">') < rammen.index('<p class="modell">Modell: ')

    def test_rekkefoelgen_etter_grafen(self, klient):
        html = _side(klient, "/aksje/BRFE")
        assert html.index("<figure>") < html.index('<section class="ki"') < html.index('<section class="historikk"')


# --- Del E: «?» og hjelpetekstene på aksjesiden -----------------------------------


def _vinduene(html: str) -> dict[str, str]:
    deler = re.findall(r'<div id="(hjelp-[a-z-]+)" class="hjelpevindu" popover>(.*?)\n</div>', html, flags=re.S)
    vinduene = {}
    for id_, innhold in deler:
        uten_topp = innhold.split("</div>", 1)[1]
        vinduene[id_] = _synlig(uten_topp.split('<p class="vist">')[0])
    return vinduene


class TestHjelpevinduene:
    @pytest.mark.parametrize("adresse", ["/aksje/BRFE", "/aksje/VRDS", f"/aksje/BRFE?periode={SISTE}"])
    @pytest.mark.parametrize("kapsel", [None, "av"])
    def test_hoeyst_60_ord_i_hvert_vindu(self, klient, adresse, kapsel):
        """Del E (svaret 06.11 kl. 23:07, spørsmål 1): hvert vindu på
        aksjesiden har høyst 60 ord, telt med \\w+ over overskriften og
        tekstene, uten linja «Siden viser». Utvidet fra vinduet ved rammen i
        10.9 til alle. Ville feilet med vinduet for retningen før 8.20a, som
        hadde 143 ord."""
        if kapsel:
            klient.set_cookie(KAPSEL, kapsel)
        vinduene = _vinduene(_side(klient, adresse))
        assert len(vinduene) >= 8
        for id_, tekst in vinduene.items():
            assert len(re.findall(r"\w+", tekst)) <= 60, (id_, tekst)

    def test_ett_spoersmaalstegn_per_kort_og_del(self, klient):
        """Del E: 4 kort, «Hvorfor signalet ble …», de tre sjekkene, grafen,
        «Signalet forklart» og «Signalet dag for dag», og «?» i stripa. Ville
        feilet med «?» ved «Ga» eller «Målt mot»."""
        html = _side(klient, "/aksje/BRFE")
        knappene = re.findall(r'popovertarget="(hjelp-[a-z-]+)" aria-label', html)
        assert sorted(knappene) == sorted(
            [
                "hjelp-hentet",
                "hjelp-kurs",
                "hjelp-endring",
                "hjelp-styrke",
                "hjelp-retning-aksje",
                "hjelp-sjekkene",
                "hjelp-trend",
                "hjelp-bevegelse",
                "hjelp-interesse",
                "hjelp-graf",
                "hjelp-ki",
                "hjelp-historikk",
            ]
        )

    def test_en_setning_om_hvorfor_retningen_oftere_er_positiv(self, klient):
        """Del E (svaret 07.11 kl. 10:33, 2): ville feilet hvis setningen var
        borte fra vinduet for retningen, eller målingen sto der i stedet for i
        docs/hjelp.md."""
        vinduet = _vinduene(_side(klient, "/aksje/BRFE"))["hjelp-retning-aksje"]
        assert hjelpetekster()["oftere_positiv"].tekst in vinduet
        assert "60,0" not in vinduet and "199" not in vinduet


# --- U88: de fete navnene på sjekkene i KI-teksten ---------------------------------


class TestFeteNavn:
    def test_hvert_navn_er_fett_foerste_gang(self):
        """U88 (svaret 07.11 kl. 12:32, 4): ville feilet hvis et navn ikke var
        fett, et navn var fett to ganger, eller et tall mistet prikket strek."""
        tekst = str(ki_tekst("Trenden ga 1. Bevegelsen ga 0, og trenden igjen. Interessen ga 0. Interessant."))
        assert tekst.count("<strong>") == 3
        assert "<strong>Trenden</strong>" in tekst and "<strong>Bevegelsen</strong>" in tekst
        assert "<strong>Interessen</strong>" in tekst and "og trenden igjen" in tekst
        assert '<span class="tall">1</span>' in tekst and "Interessant." in tekst

    def test_sjekken_i_navnet(self):
        """Gjennomgangen av 8.20a (ECH6): ville feilet hvis «trendsjekken» eller
        «Bevegelse-sjekken» ikke ble fett, eller bare en del av ordet."""
        tekst = str(ki_tekst("Trendsjekken ga 1. Bevegelse-sjekken ga 0."))
        assert "<strong>Trendsjekken</strong>" in tekst and "<strong>Bevegelse-sjekken</strong>" in tekst

    def test_teksten_escapes(self):
        assert "&lt;b&gt;" in str(ki_tekst("Trend <b> & 3"))

    def test_paa_siden(self, klient):
        rammen = _side(klient, "/aksje/BRFE").split('<p class="ki-tekst">', 1)[1].split("</p>", 1)[0]
        assert len(re.findall(r"<strong>\w+</strong>", rammen)) == 3, rammen


# --- BH10 fra 2.16: vinduet ved dobbeltklikket ----------------------------------


@pytest.mark.parametrize("skript", ["start.ps1", "start.sh"])
def test_dobbeltklikket_nevner_en_konto_fra_foer(skript):
    """BH10 i spesifikasjonen for 2.16: ville feilet hvis vinduet bare ba om
    en gratis konto, som før, og ikke sa hva man gjør med en konto fra før."""
    tekst = (ROT / "start" / skript).read_text(encoding="utf-8")
    assert "Har du en konto hos EODHD fra før, logger du inn." in tekst


# --- Del J: de gamle ordene ------------------------------------------------------


def test_de_gamle_ordene_staar_ikke_igjen(klient):
    """Del J: ville feilet hvis «Velg dag», «kort fortalt», «Utbyttejustert
    kurs» eller sitatet «skiller seg ut» sto igjen i hjelpen, README-en,
    hjelpetekstene eller på sidene etter at ordet på siden var endret."""
    gamle = ("Velg dag", "kort fortalt", "Utbyttejustert kurs", "«skiller seg ut»")
    tekster = " ".join(f"{t.tittel} {t.tekst}" for t in hjelpetekster().values())
    hjelpen = (ROT / "docs" / "hjelp.md").read_text(encoding="utf-8")
    readme = (ROT / "README.md").read_text(encoding="utf-8")
    sidene = " ".join(_synlig(_side(klient, s)) for s in SIDENE)
    for ord_ in gamle:
        for navn, tekst in (
            ("hjelpetekster", tekster),
            ("hjelp.md", hjelpen),
            ("README.md", readme),
            # Story 3.5i: og det som er flyttet til docs/installasjon.md.
            ("installasjon.md", installasjonen()),
            ("sidene", sidene),
        ):
            assert ord_ not in tekst, (ord_, navn)
