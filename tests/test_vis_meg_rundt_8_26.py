"""Story 8.26: «Vis meg rundt» spiller av siden, knappene øverst og funnene
fra demoprøven (gruppens svar 11.11 kl. 16:58, 17:06, 17:12, 17:21, 17:44,
17:47, 17:48 og 17:53).

Spesifikasjonen er spec-8-26-vis-meg-rundt-spiller-av-siden.md, med delene.
Demoen lages i en midlertidig mappe, og den ekte versjonen fra en testbase
under tmp_path (regel 22). Ingen nettkall (AD-8).
"""

import html
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

import app as app_modul
import demo
import hjelpetekster as ht
from lagring_sqlite import demo_sti

ROT = Path(__file__).resolve().parents[1]
SKRIPTET = ROT / "src" / "static" / "hjelp.js"
NODE = shutil.which("node")


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
    monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


@pytest.fixture
def ekte(tmp_path, monkeypatch):
    """Den ekte versjonen, fra en testbase under tmp_path."""
    import lagring_sqlite
    from test_fetch_prices import OEYEBLIKK_22_09, kjoer_23

    raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
    kjoer_23(raa, base, OEYEBLIKK_22_09)
    monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
    monkeypatch.delenv(app_modul.I_DEMO, raising=False)
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


def _side(klient, adresse: str) -> str:
    svar = klient.get(adresse)
    assert svar.status_code == 200, adresse
    return svar.data.decode("utf-8")


def _raden(side: str) -> str:
    return side[side.index('<nav class="rad sider"') : side.index("</nav>")]


class _Node:
    def _kjoer(self, uttrykk: str):
        kode = f"const o = require({json.dumps(str(SKRIPTET))}); console.log(JSON.stringify({uttrykk}));"
        svar = subprocess.run([NODE, "-e", kode], capture_output=True, text=True, timeout=60)
        assert svar.returncode == 0, svar.stderr
        return json.loads(svar.stdout)


# --- 1) «Vis meg rundt» spiller av siden, og knappene øverst ------------------


class TestKnappeneOeverst:
    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    def test_begge_knappene_i_raden_med_ikon(self, versjon, request):
        """Svaret kl. 17:06: ville feilet hvis «Vis meg rundt» og «Spill av
        omvisningen» ikke sto i raden øverst etter «Innstillinger», som
        sideknapper med hvert sitt ikon, eller raden under demolinja sto
        igjen. Likt i demoen og i den ekte versjonen."""
        k = request.getfixturevalue(versjon)
        side = _side(k, "/")
        etter = _raden(side).split("Innstillinger</a>", 1)[1]
        knappene = re.findall(
            r'<button type="button" class="sideknapp ([\w-]+)"[^>]*hidden>(<svg class="ikon".*?</svg>)', etter
        )
        assert [k for k, _ in knappene] == ["vis-meg-rundt", "spill-av"]
        assert knappene[0][1] != knappene[1][1], "samme ikon på begge"
        assert "rundtur-rad" not in side and "<details" not in side.split("</header>")[0]

    def test_stegene_paa_knappen_er_sidens(self, klient):
        """Svaret kl. 16:58: ville feilet hvis «Vis meg rundt» hadde andre steg
        enn sidens egne i hjelpetekster.py."""
        side = _side(klient, "/boersometer")
        m = re.search(r'class="sideknapp vis-meg-rundt" data-steg="([^"]*)"', side)
        stegene = json.loads(html.unescape(m.group(1)))
        assert [s["anker"] for s in stegene] == [s.anker for s in ht.rundturer()["boersometer"]]


@pytest.mark.skipif(NODE is None, reason="Node finnes ikke på maskinen")
class TestBoksenForSiden(_Node):
    def test_sidens_steg_blir_paa_siden(self):
        """Svaret kl. 16:58: ville feilet hvis et steg fra «Vis meg rundt»
        sendte brukeren til en annen side, eller ikke ble hoppet over når
        delen mangler, som i omvisningen."""
        liste = '[{"anker":"a","tittel":"A","tekst":"x"},{"anker":"b","tittel":"B","tekst":"y"}]'
        steg = self._kjoer(f"o.sidensSteg({liste})")
        assert {s["side"] for s in steg} == {"siden"}
        assert self._kjoer(f"o.nesteSteg(o.sidensSteg({liste}), 0, 1, o.SIDEN, (a) => a !== 'a')") == 1
        assert self._kjoer(f"o.knappene(o.sidensSteg({liste}), 1, o.SIDEN, () => true)") == {
            "tilbake": True,
            "ferdig": True,
        }
        assert self._kjoer("o.sidensSteg('feil')") == []

    def test_siste_steg_har_lenken_til_hele_omvisningen(self):
        """Svaret kl. 16:58: ville feilet hvis siste steg med «Vis meg rundt»
        manglet «Ferdig» og lenken «Spill av hele omvisningen», eller den
        sto i hele omvisningen også."""
        skriptet = SKRIPTET.read_text(encoding="utf-8")
        vis = skriptet[skriptet.index("  function vis(j) {") :]
        vis = vis[: vis.index("\n  }\n")]
        assert 'knapp(siste ? "Ferdig" : "Neste"' in vis
        assert "if (siste && aktive !== steg) {" in vis
        assert '"Spill av hele omvisningen"' in vis

    def test_hele_omvisningen_lukker_boksen_for_siden_foerst(self):
        """Gjennomgangen (ECH1, BH4): ville feilet hvis «Spill av omvisningen»
        mens boksen fra «Vis meg rundt» er åpen, spilte bare siden. ECH2: og
        hvis en side fra hurtigbufferen beholdt stegene for siden."""
        skriptet = SKRIPTET.read_text(encoding="utf-8")
        start = skriptet[skriptet.index("  function start() {") :]
        start = start[: start.index("\n  }\n")]
        assert "if (aktive !== steg) avslutt();" in start
        assert start.index("avslutt();") < start.index("gaaTil(0, 1);")
        oppstart = skriptet[skriptet.index("  function oppstart() {") :]
        oppstart = oppstart[: oppstart.index("\n  }\n")]
        assert "aktive = steg;" in oppstart and "stedet = SIDE;" in oppstart

    def test_vis_meg_rundt_lagrer_ingen_omvisning(self):
        """Ville feilet hvis «Vis meg rundt» lagret steget som omvisningen
        fortsetter fra på neste side, så en annen side åpnet boksen."""
        skriptet = SKRIPTET.read_text(encoding="utf-8")
        assert (
            "if (aktive === steg) skriv(sessionStorage, OMVISNING.STEGET, OMVISNING.tilstand(j, 1, her()));" in skriptet
        )
        assert 'document.querySelectorAll("button.vis-meg-rundt[hidden]")' in skriptet


# --- 2) Funnene fra demoprøven ----------------------------------------------

STIL = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")


def _regel(velger: str) -> str:
    m = re.search(r"(?:^|[}\s,])" + re.escape(velger) + r"\s*\{([^}]*)\}", STIL)
    assert m, velger
    return m.group(1)


class TestFunnene:
    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    def test_hjelpevinduet_sier_hvordan_det_lukkes(self, versjon, request):
        """Ville feilet hvis et hjelpevindu ikke sa at det også lukkes med et
        nytt trykk på samme «?»."""
        side = _side(request.getfixturevalue(versjon), "/")
        vinduer = side.count('class="hjelpevindu" popover>')
        assert vinduer > 0
        assert side.count('<p class="lukkes">Lukk med «Lukk», Esc eller et nytt trykk på samme «?».</p>') == vinduer

    def test_brikkene_staar_innenfor_ruta(self):
        """Ville feilet hvis feltet med de tre brikkene i «Slik leser du
        tabellen» var låst til 36 px, så brikkene sto utenfor den grå ruta og
        inntil overskriften."""
        regel = _regel(":where(.side-oversikt) .symbolfelt:has(> .utslagsfelt)")
        assert "height: auto" in regel and "padding: 6px 0" in regel

    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    def test_hovedindeksen_sier_hvilken_indeks(self, versjon, request):
        """Svaret kl. 17:06: ville feilet hvis «?» ved Hovedindeksen ikke sa
        først hvilken indeks det er, med den samme teksten i begge versjonene."""
        side = _side(request.getfixturevalue(versjon), "/")
        vindu = side.split('id="hjelp-hovedindeks"', 1)[1].split('<p class="lukkes">', 1)[0]
        tekster = re.findall(r"<p>(?:<strong>[^<]*</strong> )?([^<]*)</p>", vindu)
        assert tekster[0] == "OSEBX er hovedindeksen på Oslo Børs. I demoen heter den oppdiktede indeksen DEMIX."

    def test_dine_egne_aksjer_som_oversikten(self, klient):
        """Svaret kl. 17:12: ville feilet hvis «Dine egne aksjer» hadde egen
        bransjekolonne, ikke hadde ticker og bransjeikon under navnet som på
        oversikten, eller «Angre» ikke var en liten knapp."""
        import sqlite3

        t = sqlite3.connect(demo_sti())
        with t:
            t.execute(
                "INSERT INTO oenske (handling, symbol, navn, sektor, laget) VALUES "
                "('folg', 'XTEST', 'Eksempelselskap', 'Energi', '2026-10-13T12:00:00+00:00')"
            )
        t.close()
        egne = _side(klient, "/").split('id="dine-egne-aksjer"', 1)[1].split("</section>", 1)[0]
        assert "<th>Selskap</th><th>Status</th>" in egne and "<th>Bransje</th>" not in egne
        rad = egne.split('<tr class="egen-rad">', 1)[1].split("</tr>", 1)[0]
        assert re.search(r'<td class="selskap">Eksempelselskap <span class="egenmerke">Egen</span>', rad)
        assert '<span class="linje">XTEST · <svg class="bransjesymbol"' in rad
        assert '<button type="submit" class="knapp liten">Angre</button>' in rad

    def test_full_liste_er_ikke_roed(self):
        """Svaret kl. 17:12: ville feilet hvis beskjeden om full liste sto i
        rødt (--ned), som betyr negativ."""
        regel = _regel(":where(.side-oversikt) .full")
        assert "var(--ned)" not in regel and "color: var(--tekst)" in regel
        assert ".full" not in _regel(":where(.side-oversikt) .feil")

    def test_ki_bryterne_er_oransje_og_merket_graatt(self):
        """Svaret kl. 17:21: ville feilet hvis bryteren ved «Børsdagen kort
        fortalt» eller på aksjesiden ikke var oransje med blekk-knott som i
        Innstillinger, eller «Laget av KI» ikke sto grått."""
        for side, velger in ((".side-oversikt", ".dagsbryter"), (".side-aksje", ".ki-bryter")):
            paa = f':where({side}) {velger} [aria-checked="true"] .spor'
            assert "background: var(--oransje)" in _regel(paa)
            assert "background: var(--blekk)" in _regel(paa + "::after")
        assert "color: var(--dempet)" in _regel(":where(.side-oversikt) .boersdagen .merke-ki")
        assert "color: var(--dempet)" in _regel(":where(.side-aksje) .ki .merke-ki")


# --- 6) Tillegg 4: filteret og lenken «Den ekte versjonen» --------------------


def _radene(side: str) -> list[str]:
    tabell = side.split('id="aksjene"', 1)[1].split("</table>", 1)[0]
    return re.findall(r'<a href="/aksje/([A-Z0-9-]+)"', tabell)


class TestFilteretOgLenken:
    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    # Tillegg 9 (gruppens svar 11.11 kl. 20:04): også «Alle» i Min liste.
    @pytest.mark.parametrize("sti", ["/", "/min-liste", "/?vis=min", "/min-liste?vis=alle"])
    def test_filteret_er_borte(self, versjon, sti, request):
        """Ønsket kl. 17:48: ville feilet hvis raden «Alle», «3 av 3 positiv»
        og «3 av 3 negativ», linja om filteret eller lenken til 2 av 3 sto
        igjen, eller «Alle | Min liste» forsvant med den."""
        k = request.getfixturevalue(versjon)
        side = _side(k, sti)
        assert 'class="signalfilter"' not in side and 'class="filtertekst"' not in side
        assert "3 av 3 positiv" not in side and "3 av 3 negativ" not in side
        assert "Filteret viser" not in side and "signal=" not in side

    def test_alle_og_min_liste_staar(self, klient):
        side = _side(klient, "/")
        knappene = re.findall(r'<a class="visknapp" href="[^"]*"[^>]*>(Alle|Min liste) <span class="antall">', side)
        assert knappene == ["Alle", "Min liste"]

    @pytest.mark.parametrize("verdi", ["positiv", "negativ", "positiv-2"])
    def test_signal_i_adressen_filtrerer_ikke(self, klient, verdi):
        """Ville feilet hvis en gammel adresse med ?signal= fortsatt skjulte
        rader."""
        assert _radene(_side(klient, f"/?signal={verdi}")) == _radene(_side(klient, "/"))

    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    def test_nfr_06_staar_synlig_paa_oversikten(self, versjon, request):
        """NFR-06: ville feilet hvis at signalet ikke er et råd om å kjøpe
        eller selge, ble borte fra oversikten med filteret."""
        side = _side(request.getfixturevalue(versjon), "/")
        innledning = side.split('<p class="innledning">', 1)[1].split("</p>", 1)[0]
        assert "ikke hva du bør kjøpe eller selge" in innledning

    def test_den_ekte_versjonen_i_en_ny_fane(self, klient):
        """Ønsket kl. 17:53: ville feilet hvis lenken i demolinja åpnet GitHub
        i samme fane, så demoen forsvant, eller manglet pila og teksten for
        skjermlesere som lenken til investorsiden har."""
        demo_linja = _side(klient, "/").split('<p class="eksempeltall">', 1)[1].split("</p>", 1)[0]
        lenke = re.search(r'<a href="([^"]+)"([^>]*)>(.*?)</a>', demo_linja)
        assert lenke.group(1) == app_modul.EKTE_VERSJONEN_URL
        assert lenke.group(2) == ' target="_blank" rel="noreferrer"'
        assert lenke.group(3) == (
            'Den ekte versjonen<span class="pil" aria-hidden="true"> ↗</span>'
            '<span class="skjult"> (åpnes i en ny fane)</span>'
        )

    def test_teksten_for_skjermlesere_er_skjult_i_demolinja(self):
        """Ville feilet hvis «(åpnes i en ny fane)» sto synlig i demolinja,
        fordi stilen bare skjuler .skjult der den har en egen regel."""
        regel = _regel("header.stripe .eksempeltall .skjult")
        assert "position: absolute" in regel and "clip: rect(0 0 0 0)" in regel

    def test_alle_lenker_ut_av_appen_i_ny_fane(self):
        """Ville feilet hvis en annen lenke ut av appen i malene åpnet i samme
        fane."""
        for mal in (ROT / "src" / "templates").glob("*.html"):
            tekst = mal.read_text(encoding="utf-8")
            for lenke in re.findall(r"<a [^>]*>", tekst):
                if "http" in lenke or "ekte_versjonen_url" in lenke or "{{ adresse }}" in lenke:
                    assert 'target="_blank"' in lenke and 'rel="noreferrer"' in lenke, (mal.name, lenke)


# --- 4) Tillegg 2: «uten data» sier hvorfor ---------------------------------


class TestIngenKurserEnnaa:
    """Tillegg 2 og tillegg 8 (gruppens ønske 11.11 kl. 19:51): de samme ordene
    og den samme forklaringen overalt der det sto «uten data»."""

    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    def test_ingen_side_sier_uten_data(self, versjon, request):
        """Ville feilet hvis en side fortsatt sa «uten data» uten å si hvorfor."""
        k = request.getfixturevalue(versjon)
        for sti in ("/", "/min-liste?vis=alle", "/boersometer"):
            assert not re.search(r"[Uu]ten data", _side(k, sti)), sti

    def test_alle_stedene_sier_det_samme(self, klient):
        """Tillegg 8: ville feilet hvis ett av stedene for MTFJ i demoen sa
        noe annet enn UTEN_DATA_TEKST: raden på oversikten og i Min liste,
        ruta og begge kolonnene i tabellen på børsometeret, aksjesiden og
        hjelpen bak «?» ved «Oppdatert»."""
        import boersometer
        import demo
        from markedsoversikt import UTEN_DATA_TEKST

        ordene = UTEN_DATA_TEKST.lower()
        assert demo.UTEN_KURSER == "MTFJ" and ordene == "ingen kurser ennå"
        funnet = {}
        for sti in ("/", "/min-liste?vis=alle"):
            rad = _side(klient, sti).split('<a href="/aksje/MTFJ">', 1)[1].split("</tr>", 1)[0]
            funnet[sti] = re.search(r'<span class="merke mangler">([^<]+)</span>', rad).group(1)
        side = _side(klient, "/boersometer")
        rute = side.split('href="/aksje/MTFJ"', 1)[1].split("</a>", 1)[0]
        funnet["ruta"] = re.search(r'<span class="endring">([^<]+)</span>', rute).group(1)
        funnet["title"] = re.search(r'title="MTFJ: ([^"]+)"', side).group(1)
        tabell = side.split("<table", 1)[1].split("</table>", 1)[0]
        rad = tabell.split("MTFJ", 1)[1].split("</tr>", 1)[0]
        cellene = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", rad, re.S)]
        funnet["tabellen, endring"], funnet["tabellen, styrke"] = cellene[0], cellene[-1]
        aksjesiden = _side(klient, "/aksje/MTFJ")
        funnet["aksjesiden"] = re.search(r'<p class="ingen-kurser">\s*<strong>([^<]+)</strong>', aksjesiden).group(1)
        vindu = _side(klient, "/").split('id="hjelp-hentet"', 1)[1].split('<p class="lukkes">', 1)[0]
        funnet["hjelpen"] = re.search(r"<strong>(Ingen[^<]*):</strong>", vindu).group(1)
        assert {navn: tekst.lower() for navn, tekst in funnet.items()} == {navn: ordene for navn in funnet}, funnet
        assert boersometer.UTEN_DATA.lower() == ordene

    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    def test_hvorfor_staar_bak_spoersmaalstegnet_og_paa_aksjesiden(self, versjon, request):
        """Tillegg 8: ville feilet hvis «?» ved «Oppdatert» eller aksjesiden
        ikke sa hvorfor, med den samme forklaringen."""
        hvorfor = ht.UTEN_KURSER_HVORFOR
        # Tillegg 22 (svaret 12.11 kl. 10:16, spørsmål 10): ikke «nettopp er
        # lagt til», og EODHD, ikke «kilden» (tillegg 18).
        assert "nettopp er lagt til" not in hvorfor
        assert hvorfor.startswith("EODHD har ikke gitt kurser for aksjen.")
        k = request.getfixturevalue(versjon)
        vindu = _side(k, "/").split('id="hjelp-hentet"', 1)[1].split('<p class="lukkes">', 1)[0]
        assert hvorfor in html.unescape(vindu)
        if versjon == "klient":
            assert hvorfor in html.unescape(_side(k, "/aksje/MTFJ"))

    def test_demoen_sier_hvilken_aksje_med_vilje(self, klient):
        """Tillegg 8: ville feilet hvis demoen ikke sa at den oppdiktede aksjen
        med vilje er uten kurser, med navnet fra demodataene, eller den ekte
        versjonen sa det."""
        import demo

        navn = next(a.navn for a in demo.DEMOUNIVERS if a.symbol == demo.UTEN_KURSER)
        setningen = f"I demoen er {navn} med vilje uten kurser, så du ser hvordan det ser ut."
        assert ht.DEMO_UTEN_KURSER == setningen
        assert setningen in html.unescape(_side(klient, "/").split('id="hjelp-hentet"', 1)[1])
        assert setningen in html.unescape(_side(klient, "/aksje/MTFJ"))

    def test_den_ekte_versjonen_sier_ikke_demoen(self, ekte):
        """Ville feilet hvis den ekte versjonen sa noe om demoen bak «?»."""
        assert "I demoen er" not in _side(ekte, "/")

    def test_bare_en_aksje_uten_kurser_sier_ennaa(self):
        """Gjennomgangen (ECH4, VG5): ville feilet hvis en aksje med kurser,
        men uten kurs på dagen, sto med «Ingen kurser ennå»."""
        from datetime import date

        import boersometer
        from kursdata import Aksje
        from test_boersometer import KURSER

        aksje = Aksje("A", "A.OL", "A ASA", "Energi")
        senere = date(2030, 1, 2)
        med = boersometer.bygg_rute(aksje, KURSER, None, senere, senere)
        uten = boersometer.bygg_rute(aksje, [], None, senere, senere)
        assert med.uten_data and not med.aldri_kurs
        assert uten.uten_data and uten.aldri_kurs
        mal = (ROT / "src" / "templates" / "boersometer.html").read_text(encoding="utf-8")
        assert "uten_kurs_kort if rute.aldri_kurs else 'Ingen kurs den dagen'" in mal

    def test_en_rute_uten_kurser_er_ikke_stor(self):
        """Ville feilet hvis grensen for store ruter regnet med en kortere
        tekst enn den ruta viser, så teksten ble for bred for en stor rute."""
        import boersometer

        bredde = boersometer.stor_bredde("AKRBP", None, False, boersometer.UTEN_DATA)
        assert bredde > boersometer.STOR[0]

    def test_ukjent_forklares_bak_spoersmaalstegnet(self):
        """Ville feilet hvis «Ukjent» bak «?» ved Retning ikke sa at det også
        gjelder en aksje uten kurser."""
        tekst = ht.hjelpetekster()["ukjent"].tekst
        assert "eller aksjen har ingen kurser ennå" in tekst
        assert ht.hjelpetekster()["uten_data"].tittel == "Ingen kurser ennå:"


# --- 3) Tillegg 1: fotnoten og de løse tekstene -----------------------------


class TestFotnotenOgDeLoeseTekstene:
    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    @pytest.mark.parametrize("sti", ["/", "/min-liste?vis=alle"])
    def test_fotnoten_er_borte_og_forbeholdet_staar(self, versjon, sti, request):
        """Ønsket kl. 17:44: ville feilet hvis fotnoten «Sluttkursen er den
        ujusterte kursen …» sto igjen under tabellen, eller at signalstyrken
        ikke er et råd om å kjøpe eller selge, ikke sto synlig i innledningen
        (NFR-06)."""
        side = _side(request.getfixturevalue(versjon), sti)
        assert "Sluttkursen er den ujusterte kursen" not in side
        innledning = side.split('<p class="innledning">', 1)[1].split("</p>", 1)[0]
        assert re.search(r"(ikke hva du bør kjøpe eller selge|ikke om du bør kjøpe eller selge)\.", innledning)

    def test_det_fotnoten_sa_staar_bak_spoersmaalstegnene(self):
        """Ville feilet hvis «?» ved Sluttkurs, Endring eller Signalstyrke ikke
        sa det fotnoten sa: ujustert sluttkurs, endringen på utbyttejustert
        kurs, og hvor mange sjekker som slo ut, ikke et råd."""
        tekster = ht.hjelpetekster()
        assert "uten utbyttejustering" in tekster["sluttkurs"].tekst
        endring = " ".join(t.tekst for n, t in tekster.items() if n in ("endring", "utbyttejustert"))
        assert "justert for utbytte" in endring and "kursfall" in endring
        styrke = " ".join(t.tekst for t in tekster.values() if "sjekkene som slo ut" in t.tekst or "råd" in t.tekst)
        assert "hvor mange av de 3 sjekkene som slo ut" in styrke and "ikke et råd om å kjøpe eller selge" in styrke

    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    def test_innledningen_paa_aksjesiden_er_borte(self, versjon, request):
        """Forslaget i spesifikasjonen: ville feilet hvis innledningen «Siden
        viser sjekkene for …» sto igjen på aksjesiden."""
        k = request.getfixturevalue(versjon)
        side = _side(k, "/aksje/BRFE" if versjon == "klient" else "/aksje/EQNR")
        assert "Siden viser sjekkene for" not in side and "Siden viser kursgrafen for" not in side


# --- 5) Tillegg 3: stjernen ved «Følg», aksjene som venter, og «lista» ------


def _foelg_i_demoen(klient) -> str:
    """Følger den første aksjen på «Følg en aksje» i demoen og gir koden."""
    kode = re.search(r'href="/folg\?kode=([A-Z0-9-]+)"', _side(klient, "/folg")).group(1)
    svar = klient.post("/folg", data={"kode": kode})
    assert svar.status_code == 303 and "feil=" not in svar.headers["Location"], svar.headers["Location"]
    return kode


def _tabellene(sti) -> dict[str, int]:
    import sqlite3

    t = sqlite3.connect(sti)
    try:
        navn = [n for (n,) in t.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
        return {n: t.execute(f'SELECT COUNT(*) FROM "{n}"').fetchone()[0] for n in navn}
    finally:
        t.close()


class TestStjernenOgDeSomVenter:
    def test_foelg_gir_stjerne_og_rad_i_min_liste(self, klient):
        """Svaret kl. 17:47: ville feilet hvis en aksje fulgt med «Følg» ikke
        fikk stjerne og sto i Min liste med en gang, med «venter på henting»
        nederst i tabellen, uten lenke til en aksjeside som ikke finnes."""
        kode = _foelg_i_demoen(klient)
        for sti in ("/?vis=min", "/min-liste", "/"):
            side = _side(klient, sti)
            assert f'id="rad-{kode}"' in side, sti
            rad = side.split(f'id="rad-{kode}"', 1)[1].split("</tr>", 1)[0]
            assert 'class="stjerneknapp merket" aria-pressed="true"' in rad, sti
            assert '– <span class="merke mangler">venter på henting</span>' in rad, sti
            assert f'href="/aksje/{kode}"' not in rad and '<span class="egenmerke">Egen</span>' in rad, sti
        side = _side(klient, "/")
        assert "og 1 venter på henting</span>" in side

    def test_bare_oensket_og_stjernen_skrives(self, klient):
        """Regel 22, AD-3: ville feilet hvis «Følg» skrev noe annet enn
        ønsket og stjernen."""
        foer = _tabellene(demo_sti())
        _foelg_i_demoen(klient)
        etter = _tabellene(demo_sti())
        endret = {n for n in foer if foer[n] != etter[n]}
        assert endret == {"oenske", "min_liste"}, endret
        assert etter["oenske"] == foer["oenske"] + 1 and etter["min_liste"] == foer["min_liste"] + 1

    def test_stjernen_kan_tas_bort_og_settes_igjen(self, klient):
        """Ville feilet hvis stjernen på en aksje som venter, ikke kunne tas
        bort som før, eller ikke settes igjen."""
        kode = _foelg_i_demoen(klient)
        klient.post("/min-liste/merk", data={"symbol": kode, "til": "fjern", "tilbake": "/"})
        assert f'id="rad-{kode}"' not in _side(klient, "/min-liste")
        assert f'id="rad-{kode}"' in _side(klient, "/")
        klient.post("/min-liste/merk", data={"symbol": kode, "til": "merk", "tilbake": "/"})
        assert f'id="rad-{kode}"' in _side(klient, "/min-liste")

    def test_angre_tar_bort_stjernen(self, klient):
        """Forslaget i spørsmål 7: ville feilet hvis «Angre» lot stjernen stå,
        så Min liste hadde en aksje appen ikke følger."""
        kode = _foelg_i_demoen(klient)
        oenske = re.search(r'name="id" value="(\d+)"', _side(klient, "/").split('id="dine-egne-aksjer"', 1)[1]).group(1)
        klient.post("/angre", data={"id": oenske, "tilbake": "oversikten"})
        assert f'id="rad-{kode}"' not in _side(klient, "/") and f'id="rad-{kode}"' not in _side(klient, "/min-liste")
        assert _tabellene(demo_sti())["min_liste"] == len(demo.MERKET_I_DEMOEN)

    def test_tallene_teller_dem_som_venter_som_radene(self, klient):
        """Forslaget i spørsmål 7, etter gjennomgangen (ECH3, VG4): ville
        feilet hvis «N av M aksjer», «Alle» eller «Øvrige aksjer» sa noe annet
        enn radene i tabellen og «appen følger», så tallene sprikte."""

        def tallene(side):
            return (
                int(re.search(r"av (\d+) aksjer</mark>", side).group(1)),
                int(re.search(r'>Alle <span class="antall">(\d+)</span>', side).group(1)),
                int(re.search(r'Øvrige aksjer <span class="antall">(\d+)</span>', side).group(1)),
            )

        foer = tallene(_side(klient, "/"))
        _foelg_i_demoen(klient)
        side = _side(klient, "/")
        assert tallene(side) == tuple(n + 1 for n in foer)
        assert len(re.findall(r'<form id="rad-', side)) == foer[1] + 1

    def test_velg_dag_viser_ikke_dem_som_venter(self, klient):
        """Gjennomgangen (ECH7): ville feilet hvis en dag valgt med «Velg dag»
        viste en aksje appen ikke fulgte den dagen."""
        kode = _foelg_i_demoen(klient)
        assert f'id="rad-{kode}"' not in _side(klient, "/?periode=velg&dag=2026-10-01")

    def test_angre_i_et_bytte_tar_bort_stjernen(self, klient):
        """Gjennomgangen (VG3): ville feilet hvis «Angre» på halvdelen av et
        bytte som fjerner, lot stjernen på aksjen som skulle følges, stå."""
        import lagring_sqlite
        import valg

        kode = re.search(r'href="/folg\?kode=([A-Z0-9-]+)"', _side(klient, "/folg")).group(1)
        t = lagring_sqlite.aapne_base(demo_sti(), kjoer_migrasjoner=False)
        try:
            lager = valg.Valglager(t, lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))
            lager.folg(kode, "Energi", bytt_ut="BRFE")
            fjern_id = t.execute("SELECT id FROM oenske WHERE handling = 'fjern' AND symbol = 'BRFE'").fetchone()[0]
            assert t.execute("SELECT 1 FROM min_liste WHERE symbol = ?", (kode,)).fetchone()
            lager.angre(fjern_id)
            assert not t.execute("SELECT 1 FROM min_liste WHERE symbol = ?", (kode,)).fetchone()
            assert not t.execute("SELECT 1 FROM oenske WHERE symbol IN (?, 'BRFE')", (kode,)).fetchone()
        finally:
            t.close()

    def test_den_ekte_versjonen_viser_dem_som_venter(self, ekte, tmp_path):
        """Likt i den ekte versjonen: ville feilet hvis en aksje som venter,
        ikke fikk stjerne og rad der."""
        import sqlite3

        import lagring_sqlite
        import valg

        t = sqlite3.connect(lagring_sqlite.BASE_STI)
        with t:
            t.execute("INSERT INTO boersliste (kode, navn) VALUES ('NYA', 'Ny A ASA')")
        t.close()
        t = lagring_sqlite.aapne_base(lagring_sqlite.BASE_STI, kjoer_migrasjoner=False)
        try:
            valg.Valglager(t, lambda: datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc)).folg("NYA", "Energi")
        finally:
            t.close()
        rad = _side(ekte, "/min-liste").split('id="rad-NYA"', 1)[1].split("</tr>", 1)[0]
        assert "merket" in rad and "venter på henting" in rad


class TestRyddingen:
    def test_en_stjerne_uten_aksje_og_oenske_tas_bort(self, klient):
        """Gjennomgangen (BH2, ECH5): ville feilet hvis stjernen fra «Følg»
        ble liggende etter at ønsket ble avvist, og dukket opp igjen når
        aksjen kom inn via en ferdig liste."""

        import lagring_sqlite
        import valg

        kode = _foelg_i_demoen(klient)
        t = lagring_sqlite.aapne_base(demo_sti(), kjoer_migrasjoner=False)
        try:
            with t:
                t.execute("UPDATE oenske SET avvist = 'x' WHERE symbol = ?", (kode,))
            assert t.execute("SELECT 1 FROM min_liste WHERE symbol = ?", (kode,)).fetchone()
            lager = valg.Valglager(t, lambda: datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc))
            lager.bruk_liste([(kode, "Energi")])
            assert not t.execute("SELECT 1 FROM min_liste WHERE symbol = ?", (kode,)).fetchone()
            # De merkede aksjene i lista står.
            assert t.execute("SELECT COUNT(*) FROM min_liste").fetchone()[0] > 0
        finally:
            t.close()


class TestTriggerenFra0013:
    def test_et_ukjent_symbol_avvises_fortsatt(self, tmp_path):
        """0013: ville feilet hvis triggeren godtok et symbol som verken står
        i aksje eller venter etter «Følg»."""
        import sqlite3

        from lagring_sqlite import MIGRASJONSKATALOG
        from migrering import migrer

        t = sqlite3.connect(tmp_path / "b.db")
        try:
            assert migrer(t, MIGRASJONSKATALOG) == 13
            with pytest.raises(sqlite3.IntegrityError, match="ukjent aksje i min_liste"):
                t.execute("INSERT INTO min_liste (symbol) VALUES ('UKJENT')")
            t.execute(
                "INSERT INTO oenske (handling, symbol, navn, sektor, laget) VALUES ('folg', 'NYA', 'Ny A', 'Energi', 'x')"
            )
            t.execute("INSERT INTO min_liste (symbol) VALUES ('NYA')")
            # Gjennomgangen (VG2, BH8): et ønske som er avvist eller tatt i
            # bruk, og et ønske om å fjerne, gir ikke stjerne uten aksjen.
            t.execute("DELETE FROM min_liste WHERE symbol = 'NYA'")
            t.execute("UPDATE oenske SET avvist = 'x' WHERE symbol = 'NYA'")
            t.execute(
                "INSERT INTO oenske (handling, symbol, navn, sektor, laget, tatt_i_bruk) "
                "VALUES ('folg', 'NYC', 'Ny C', 'Energi', 'x', 'y')"
            )
            t.execute("INSERT INTO oenske (handling, symbol, laget) VALUES ('fjern', 'NYD', 'x')")
            for symbol in ("NYA", "NYC", "NYD"):
                with pytest.raises(sqlite3.IntegrityError, match="ukjent aksje i min_liste"):
                    t.execute("INSERT INTO min_liste (symbol) VALUES (?)", (symbol,))
            t.execute(
                "INSERT INTO oenske (handling, symbol, navn, sektor, laget) VALUES ('folg', 'NYE', 'Ny E', 'Energi', 'x')"
            )
            t.execute("INSERT INTO min_liste (symbol) VALUES ('NYE')")
            with pytest.raises(sqlite3.IntegrityError, match="ukjent aksje i min_liste"):
                t.execute("UPDATE min_liste SET symbol = 'NYA' WHERE symbol = 'NYE'")
        finally:
            t.close()


class TestOrdeneOmLista:
    def test_appen_foelger(self, klient):
        """Svaret kl. 17:47, del 2: ville feilet hvis siden sa «N av 18 aksjer
        i lista» der «lista» betyr alle aksjene appen følger."""
        side = _side(klient, "/")
        assert re.search(r"\d+ egne · appen følger \d+ av 18</p>", side)
        assert "aksjer i lista</p>" not in side
        # Tillegg 14 og 15: med «, som er taket.» eller de ledige plassene.
        assert re.search(
            r'<p class="antall-egne">Appen følger \d+ av 18(, som er taket\.|, \d+ plass(er)? ledige\.)</p>',
            _side(klient, "/min-liste"),
        )

    def test_full_sier_taket(self, klient, monkeypatch):
        """Ville feilet hvis beskjeden sa «Lista er full …» i stedet for at
        appen følger så mange aksjer den kan."""
        import valg

        assert valg.FULL == "Appen følger allerede 18 aksjer, som er taket. Fjern en for å følge en annen."
        monkeypatch.setattr(valg, "TAK", 0)
        side = _side(klient, "/")
        assert f'<p class="full">{valg.FULL}</p>' in side and "Lista er full" not in side


# --- 7) Tillegg 6: siden står i ro ved et trykk på en periode ----------------


class TestSidenStaarIRo:
    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    @pytest.mark.parametrize("sti", ["/", "/?vis=min", "/min-liste?vis=alle", "/boersometer"])
    def test_periodevalget_har_ankeret(self, versjon, sti, request):
        """Ønsket kl. 19:36: ville feilet hvis en periode, en pil eller «Vis
        dagen» på oversikten, i Min liste eller på børsometeret lastet siden
        uten ankeret, så den hoppet til toppen, eller ankeret ikke fantes."""
        side = _side(request.getfixturevalue(versjon), sti)
        valget = side.split('<nav class="periodevalg"', 1)[1].split("</nav>", 1)[0]
        lenkene = re.findall(r'<a (?:class="pil" )?href="([^"]+)"', valget)
        assert lenkene and all(lenke.endswith("#perioden") for lenke in lenkene), lenkene
        assert re.search(r'<form method="get" action="[^"#]*#perioden">', valget)
        assert side.count('id="perioden"') == 1
        assert re.search(r'<div class="periodehode" id="perioden">', side)

    def test_aksjesiden_holder_plassen_som_foer(self, klient):
        """8.2a (U36): ville feilet hvis aksjesiden mistet ankeret til
        kursgrafen."""
        valget = _side(klient, "/aksje/BRFE").split('<nav class="periodevalg"', 1)[1].split("</nav>", 1)[0]
        assert all(h.endswith("#kursgrafen") for h in re.findall(r'<a (?:class="pil" )?href="([^"]+)"', valget))

    def test_filteret_i_foelg_en_aksje_holder_plassen(self, klient):
        """Ville feilet hvis en brikke, en omsetning, en sortering, «Vis»
        eller «Alle» i «Følg en aksje» lastet siden uten ankeret."""
        side = _side(klient, "/folg?bransje=Kraft")
        assert '<form class="folgfilter" id="filteret" method="get" action="/folg#filteret">' in side
        alle = re.search(r'<a class="valgbrikke[^"]*" href="([^"]+)"[^>]*>Alle</a>', side).group(1)
        assert alle.endswith("#filteret")

    @pytest.mark.parametrize(
        "navn, anker", [("vis_hjelp", "hjelp-valget"), ("vis_ki_tekst", "ki-valget"), ("vis_notater", "notater-valget")]
    )
    def test_bryterne_i_innstillinger_sender_tilbake_til_bryteren(self, klient, navn, anker):
        """Ville feilet hvis en bryter i Innstillinger sendte til toppen av
        siden, eller ankeret ikke fantes."""
        svar = klient.post("/innstillinger", data={"navn": navn, "til": "av"})
        assert svar.status_code == 303 and svar.headers["Location"].endswith(f"/innstillinger#{anker}")
        assert f'id="{anker}"' in _side(klient, "/innstillinger")

    def test_omvisningen_ser_bort_fra_ankeret(self):
        """Ville feilet hvis omvisningen sammenlignet adressen med ankeret, så
        den lukket seg etter et trykk på en periode."""
        skriptet = SKRIPTET.read_text(encoding="utf-8")
        assert "return window.location.pathname + window.location.search;" in skriptet


class TestEtterGjennomgangenAvTillegg6Og8:
    def test_ruta_for_en_aksje_med_eldre_kurser_sier_ingen_kurs(self, klient, monkeypatch):
        """ECH1, BH1, VG1, VG3: ville feilet hvis ruta, title eller tabellen på
        børsometeret sa «Ingen kurser ennå» om en aksje som har kurser, men
        ikke den dagen."""
        import dataclasses

        ekte_bygg = app_modul.bygg_rute

        def bygg(aksje, *a, **k):
            rute = ekte_bygg(aksje, *a, **k)
            return dataclasses.replace(rute, aldri_kurs=False) if aksje.symbol == "MTFJ" else rute

        monkeypatch.setattr(app_modul, "bygg_rute", bygg)
        side = _side(klient, "/boersometer")
        rute = side.split('href="/aksje/MTFJ"', 1)[1].split("</a>", 1)[0]
        assert '<span class="endring">Ingen kurs</span>' in rute
        assert 'title="MTFJ: ingen kurs den dagen"' in side
        rad = side.split("<table", 1)[1].split("MTFJ", 1)[1].split("</tr>", 1)[0]
        assert "Ingen kurs den dagen" in rad and "Ingen kurser ennå" not in rad

    def test_ankrene_i_innstillinger_folger_valgene(self):
        """ECH3, VG4: ville feilet hvis et valg på siden manglet et anker."""
        import innstillinger

        assert set(app_modul.INNSTILLINGSANKER) == set(innstillinger.PAA_SIDEN)

    def test_demosetningen_bare_paa_siden_for_aksjen(self):
        """BH4: ville feilet hvis setningen om Matfjord Merkevarer sto på siden
        for en annen aksje uten kurser i demoen."""
        mal = (ROT / "src" / "templates" / "aksje_uten_kurser.html").read_text(encoding="utf-8")
        assert "{% if eksempeltall and aksje.symbol == demo_uten_kurser_symbol %}{{ demo_uten_kurser }}" in mal
        assert app_modul.app.jinja_env.globals["demo_uten_kurser_symbol"] == demo.UTEN_KURSER

    def test_alle_og_min_liste_i_min_liste_holder_plassen(self, klient):
        """ECH7: ville feilet hvis «Alle» og «Min liste» i Min liste sendte
        til toppen av siden."""
        side = _side(klient, "/min-liste")
        nav = side.split('<nav class="visvalg" id="visvalget"', 1)[1].split("</nav>", 1)[0]
        lenkene = re.findall(r'<a class="visknapp" href="([^"]+)"', nav)
        assert len(lenkene) == 2 and all(lenke.endswith("#visvalget") for lenke in lenkene)


# --- 8) Tillegg 10: lenkene har samme farge før og etter besøk ---------------


class TestLenkene:
    def test_en_felles_regel_for_lenkene(self):
        """Ønsket kl. 20:06: ville feilet hvis lenkene ikke hadde en felles
        regel som gir samme farge før og etter besøk, så navnet i et notat
        sto blått og så lilla, eller regelen overstyrte lenker med egen farge."""
        regel = _regel("a")
        assert "color: inherit" in regel
        assert "text-underline-offset: 4px" in regel

    def test_ingen_regel_gir_lenker_nettleserens_farger(self):
        """Ville feilet hvis en regel ga en lenke blått eller lilla, eller
        :visited fikk en egen farge."""
        for velger, innhold in re.findall(r"([^{}]*:visited[^{]*)\{([^}]*)\}", STIL):
            assert "color: inherit" in innhold, velger
        assert not re.search(r"color:\s*(blue|purple|#00e|#551a8b)", STIL, re.I)

    def test_lenkene_i_notatene_har_ingen_egen_farge(self, klient):
        """Ville feilet hvis navnet i et notat fikk en egen farge i stedet for
        den felles regelen."""
        notatene = _side(klient, "/min-liste").split('id="mine-notater"', 1)[1]
        assert re.search(r'<a href="/aksje/[A-Z]+">', notatene)


# --- 9) Tillegg 12: «Din egen liste» som på tavla, og siden i demoen --------


def _stegene(side: str) -> list[str]:
    delen = side.split('id="din-egen-liste"', 1)[1].split("</ol>", 1)[0]
    return re.findall(r'<li class="kort-steg">(.*?)</li>\s*(?=<li class="kort-steg">|$)', delen, re.S)


class TestDinEgenListeSomTavla:
    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    def test_tre_kort_med_tittelen_ved_tallet_og_en_handling(self, versjon, request):
        """Svaret kl. 20:28: ville feilet hvis et kort ikke hadde tallet og
        tittelen i samme topp, eller ikke hadde handlingen nederst."""
        k = request.getfixturevalue(versjon)
        if versjon == "ekte":
            k.post("/min-liste/merk", data={"symbol": "EQNR", "til": "merk", "tilbake": "/"})
        kortene = _stegene(_side(k, "/min-liste"))
        assert len(kortene) == 3
        for nummer, kort in enumerate(kortene, 1):
            assert re.search(
                rf'<div class="steg-topp"><span class="stegnummer" aria-hidden="true">{nummer}</span><h4>', kort
            ), nummer
            assert kort.rstrip().endswith("</p>") and '<p class="handling">' in kort, nummer
        assert "kort-steg .handling { margin-top: auto;" in STIL

    def test_demoen_lenker_aldri_til_eodhd(self, klient):
        """Ville feilet hvis demoen lenket til eodhd.com, i stedet for siden
        i demoen, eller sa at nøkkelen virket."""
        for sti in ("/", "/min-liste", "/min-liste?vis=alle", "/eodhd-demo", "/folg"):
            assert "eodhd.com/register" not in _side(klient, sti), sti
        kortene = _stegene(_side(klient, "/min-liste"))
        assert '<a class="knapp" href="/eodhd-demo">Åpne eodhd.com</a>' in kortene[0]
        assert '<span class="hake" aria-hidden="true">✓</span> Demoen trenger ingen nøkkel.</span>' in kortene[1]

    def test_den_ekte_versjonen_lenker_til_registreringen(self, ekte):
        """Ville feilet hvis den ekte versjonen ikke åpnet registreringen hos
        EODHD i en ny fane, med samme adresse som startskriptet, eller hadde
        siden fra demoen."""
        ekte.post("/min-liste/merk", data={"symbol": "EQNR", "til": "merk", "tilbake": "/"})
        kortene = _stegene(_side(ekte, "/min-liste"))
        assert (
            f'<a class="knapp" href="{app_modul.EODHD_REGISTRERING}" target="_blank" rel="noreferrer">Åpne eodhd.com'
            '<span class="pil" aria-hidden="true"> ↗</span><span class="skjult"> (åpnes i en ny fane)</span></a>'
        ) in kortene[0]
        for skript in ("start/start.ps1", "start/start.sh"):
            assert app_modul.EODHD_REGISTRERING in (ROT / skript).read_text(encoding="utf-8"), skript
        assert ekte.get("/eodhd-demo").status_code == 404

    def test_kallene_og_noekkelen_bak_spoersmaalstegnet(self, klient):
        """Ville feilet hvis kallene, regnet av lista, bransjelistene eller
        «Slik bytter du nøkkel» sto i kortene i stedet for bak «?»."""
        side = _side(klient, "/min-liste")
        kortene = _stegene(side)
        assert 'popovertarget="hjelp-noekkel"' in kortene[1] and "Slik bytter du nøkkel" not in kortene[1]
        assert 'popovertarget="hjelp-kallene"' in kortene[2] and "kall: margin" not in kortene[2]
        vindu = side.split('id="hjelp-kallene"', 1)[1].split('<p class="lukkes">', 1)[0]
        assert (
            re.search(r"<li>\d+ kall: margin</li>", vindu)
            and "mest omsatte aksjene på børsen eller i bransjen" in vindu
        )  # 8.28
        assert 'id="ferdige-lister"' in kortene[2] and 'class="knapp ferdigknapp"' in kortene[2]

    def test_siden_i_demoen(self, klient):
        """Ville feilet hvis siden i demoen manglet lenken tilbake, tegningen,
        boblen, KI-merket eller teksten nederst, eller boblen sa noe om kurser
        eller kjøp og salg (NFR-06)."""
        from investorsider import EODHD_BOBLE
        from test_hjelpetekster import RAADSORD

        side = _side(klient, "/eodhd-demo")
        assert '<a class="tilbake" href="/min-liste#din-egen-liste">Tilbake til Min liste</a>' in side
        assert '<img src="/static/demo/eodhd.svg" width="560" height="400"' in side
        assert '<p class="boble"' in side and EODHD_BOBLE in html.unescape(side)
        assert '<figcaption class="ki-merke">Illustrasjon laget av KI</figcaption>' in side
        assert "så ingen konto trengs" in side and "registreringen hos EODHD i en ny fane" in side
        for ord_ in RAADSORD:
            assert not re.search(ord_, EODHD_BOBLE, re.IGNORECASE), ord_
        assert not re.search(r"kurs|kjøp|selg|salg", EODHD_BOBLE, re.IGNORECASE)
        tegningen = (ROT / "src" / "static" / "demo" / "eodhd.svg").read_text(encoding="utf-8")
        assert "<title" in tegningen and "<desc" in tegningen and "http" not in tegningen.split("xmlns=", 1)[1][60:]


class TestEtterGjennomgangenAvTillegg12:
    def test_med_hjelpen_av_staar_det_i_kortene(self, klient):
        """ECH1, BH2, VG1: ville feilet hvis byttet av nøkkel og kallene
        forsvant fra siden med «Vis hjelp» av, eller statusen viste til en
        «?» som ikke finnes."""
        klient.post("/innstillinger", data={"navn": "vis_hjelp", "til": "av"})
        side = _side(klient, "/min-liste")
        kortene = _stegene(side)
        assert "popovertarget" not in "".join(kortene)
        assert "Slik bytter du nøkkel:</strong> Slett det som står etter EODHD_API_KEY=" in kortene[1]
        assert re.search(r"<li>\d+ kall: margin</li>", kortene[2])
        assert "bak «?»" not in side.split('id="din-egen-liste"', 1)[1]

    def test_dagens_tall_er_lista(self, klient):
        """BH3, ECH2: ville feilet hvis steg 3 sa «dagens 15» fast, i stedet
        for antallet appen følger."""
        mal = (ROT / "src" / "templates" / "_egne.html").read_text(encoding="utf-8")
        # Story 8.28: setningen nevner «De 15 mest omsatte» først, og bransjene ellers.
        assert "Start med dagens {{ egne.antall }}{% if egne.mest_omsatte %}" in mal


# Tillegg 17 (gruppens svar 11.11 kl. 22:04): brikkene i «Følg en aksje»,
# overskriften med «Vis dagen», «3 av 3» uten vurderinger og «Oppdatert».


def _bransjebrikkene(side: str) -> str:
    start = side.index('<fieldset class="bransjefilter">')
    return side[start : side.index("</fieldset>", start)]


def _synlige(side: str) -> list[str]:
    return [
        rad.split('data-kode="')[1].split('"')[0]
        for rad in re.findall(r'<tr class="foelgbar"[^>]*>', side)
        if " hidden>" not in rad
    ]


class TestBrikkeneIFoelg:
    def test_hver_bransje_har_antallet_og_tom_er_graa(self, klient):
        """Ville feilet hvis brikkene ikke viste antallet, eller en bransje
        uten aksjer kunne velges og gi en tom liste (7 av 13 i demoen)."""
        side = _side(klient, "/folg")
        brikkene = _bransjebrikkene(side)
        antall = re.findall(r'value="([^"]+)"([^>]*)>.*?<span class="antall">(\d+)</span>', brikkene)
        assert len(antall) == 13
        rader = re.findall(r'<tr class="foelgbar"[^>]*data-bransje="([^"]+)"', side)
        for bransje, attr, n in antall:
            assert int(n) == rader.count(bransje), bransje
            assert ("disabled" in attr) == (n == "0"), bransje
        tomme = sum(n == "0" for _, _, n in antall)
        assert tomme > 0
        assert brikkene.count("valgbrikke tom") == tomme

    def test_alle_radene_staar_i_siden_og_filteret_skjuler(self, klient):
        """Ville feilet hvis serveren bare sendte radene i filteret, så
        skriptet ikke kunne vise de andre ved et klikk på en annen brikke."""
        alle = _side(klient, "/folg")
        kraft = _side(klient, "/folg?bransje=Kraft")
        assert alle.count('<tr class="foelgbar"') == kraft.count('<tr class="foelgbar"')
        synlige = _synlige(kraft)
        bransjer = {
            rad.split('data-bransje="')[1].split('"')[0]
            for rad in re.findall(r'<tr class="foelgbar"[^>]*>', kraft)
            if " hidden>" not in rad
        }
        assert synlige and bransjer == {"Kraft"}
        n = len(synlige)
        assert f'<span id="antall-vist">{n}</span> av <span id="antall-filtrert">{n}</span>' in kraft

    def test_radene_har_dataene_skriptet_trenger(self, klient):
        """Ville feilet hvis en rad manglet bransjen, omsetningen, medianen
        eller rangen, så skriptet ikke kunne filtrere og sortere."""
        side = _side(klient, "/folg")
        for rad in re.findall(r'<tr class="foelgbar"[^>]*>', side):
            for felt in ("data-bransje", "data-omsetning", "data-median", "data-rang"):
                assert felt + '="' in rad, (felt, rad)
            assert re.search(r'data-omsetning="(over|under|ikke)"', rad)

    def test_samme_i_den_ekte_versjonen(self, ekte):
        """Ville feilet hvis antallet og den grå brikken bare fantes i demoen."""
        side = _side(ekte, "/folg")
        assert _bransjebrikkene(side).count('<span class="antall">') == 13
        assert 'id="antall-filtrert"' in side

    @pytest.mark.skipif(NODE is None, reason="trenger node")
    def test_skriptet_filtrerer_og_sorterer_som_serveren(self, klient):
        """Ville feilet hvis FOLGLISTA i hjelp.js ga en annen rekkefølge
        eller andre rader enn ferdige_lister.filtrer og .sorter."""
        side = _side(klient, "/folg")
        rader = [
            {k: html.unescape(v) for k, v in re.findall(r'data-([a-z]+)="([^"]*)"', rad)}
            for rad in re.findall(r'<tr class="foelgbar"([^>]*)>', side)
        ]
        data = json.dumps(rader)
        node = _Node()
        for sortering in ("omsatt", "navn", "bransje"):
            server = [
                rad.split('data-kode="')[1].split('"')[0]
                for rad in re.findall(r'<tr class="foelgbar"[^>]*>', _side(klient, f"/folg?sorter={sortering}"))
            ]
            js = node._kjoer(
                f"{data}.sort((a, b) => o.FOLGLISTA.sammenlign(a, b, {json.dumps(sortering)})).map((r) => r.kode)"
            )
            assert js == server, sortering
        for omsetning in ("over", "under", "ikke"):
            server = _synlige(_side(klient, f"/folg?omsetning={omsetning}&bransje=Kraft&bransje=Helse"))
            js = node._kjoer(
                f"{data}.filter((r) => o.FOLGLISTA.passer(r, '', ['Kraft', 'Helse'], {json.dumps(omsetning)})).map((r) => r.kode)"
            )
            assert sorted(js) == sorted(server), omsetning
        server = _synlige(_side(klient, "/folg?q=FJORD"))
        js = node._kjoer(f"{data}.filter((r) => o.FOLGLISTA.passer(r, 'FJORD', [], '')).map((r) => r.kode)")
        assert sorted(js) == sorted(server)

    def test_vis_skjules_av_skriptet_og_klikk_sender_ikke_skjemaet(self):
        """Ville feilet hvis «Vis» sto med skriptet, eller et klikk på en
        brikke fortsatt sendte skjemaet og lastet siden."""
        kilde = SKRIPTET.read_text(encoding="utf-8")
        blokk = kilde[kilde.index("// Story 8.22 (spørsmål 8): søket i «Følg en aksje»") :]
        assert 'querySelectorAll("button[type=submit]")) knapp.hidden = true' in blokk
        assert "form.submit()" not in blokk
        assert 'skjema.addEventListener("change", oppdater)' in blokk
        assert "e.preventDefault()" in blokk


def _ren(tekst: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", tekst)).strip()


def _overskriften(side: str) -> str:
    return _ren(re.search(r'<h1 class="overskrift">(.*?)</h1>', side, re.S).group(1))


def _tre_av_tre(side: str) -> str | None:
    m = re.search(r'<p class="alle-sjekkene">(.*?)</p>', side, re.S)
    return _ren(m.group(1)) if m else None


class TestOverskriftenMedVisDagen:
    def test_dagen_tabellen_viser(self, klient):
        """Ville feilet hvis overskriften sa siste børsdag (fredag) over
        tabellen for tirsdag 06.10."""
        assert _overskriften(_side(klient, "/")).endswith("fredag")
        assert _overskriften(_side(klient, "/?periode=velg&dag=2026-10-06")).endswith("tirsdag")
        assert _overskriften(_side(klient, "/?periode=velg&dag=2026-10-07")).endswith("onsdag")

    def test_antallet_og_linja_er_dagens(self, klient):
        """Ville feilet hvis «N av 15» og linja om 3 av 3 var fra siste
        børsdag og ikke fra radene den valgte dagen. Demoen har ulike tall
        de to dagene (2 og 3, Lastfjord Container og Brattfjell Energi)."""
        tirsdag = _side(klient, "/?periode=velg&dag=2026-10-06")
        onsdag = _side(klient, "/?periode=velg&dag=2026-10-07")
        assert _overskriften(tirsdag).startswith("2 av 15")
        assert _overskriften(onsdag).startswith("3 av 15")
        assert "Lastfjord Container" in _tre_av_tre(tirsdag)
        assert "Brattfjell Energi" in _tre_av_tre(onsdag)
        assert _tre_av_tre(tirsdag) != _tre_av_tre(onsdag)

    def test_periode_og_siste_boersdag_som_foer(self, klient):
        """Ville feilet hvis en periode fikk overskriften for en annen dag."""
        siste = _side(klient, "/")
        uke = _side(klient, "/?periode=1-uke")
        assert _overskriften(uke) == _overskriften(siste)
        assert _tre_av_tre(uke) == _tre_av_tre(siste)


class TestTreAvTreUtenVurdering:
    def test_varde_systemer_sier_hvorfor(self, klient):
        """Ville feilet hvis en aksje uten en eneste vurdering fortsatt fikk
        «3 av 3 aldri siden …» i «Signalet dag for dag»."""
        side = _side(klient, "/aksje/VRDS")
        tekst = _ren(re.search(r'<p class="alle-sjekkene-aaret">(.*?)</p>', side, re.S).group(1))
        assert "aldri" not in tekst
        assert tekst.startswith("Signalet er ikke regnet ennå: Trenger")
        assert "dager for å regne signal" in tekst

    def test_en_aksje_med_vurderinger_som_foer(self, klient):
        """Ville feilet hvis linja om 3 av 3 forsvant for en vurdert aksje."""
        m = re.search(r'<p class="alle-sjekkene-aaret">(.*?)</p>', _side(klient, "/aksje/BRFE"), re.S)
        assert m and "3 av 3" in m.group(1)

    def test_vurdert_skiller_grunn_fra_vurdering(self):
        """Ville feilet hvis vurdert var sann for en aksje med bare grunner."""
        from datetime import date

        from historikk import alle_sjekkene_det_siste_aaret
        from vurderingsdata import Grunn

        dag = date(2026, 10, 9)
        svar = alle_sjekkene_det_siste_aaret({dag: next(iter(Grunn))}, dag, 3)
        assert svar is not None and svar.vurdert is False and svar.antall == 0


SIDENE_UTEN_EGET_TIDSPUNKT = [
    "/folg",
    "/folg?kode=BRFE",
    "/innstillinger",
    "/investorside/BRFE",
    "/aksje/MTFJ",
    "/eodhd-demo",
]


def _tidspunktet(side: str) -> str:
    return re.search(r"<span>Oppdatert ([^<]+)</span>", side).group(1)


class TestOppdatertOveralt:
    @pytest.mark.parametrize("adresse", SIDENE_UTEN_EGET_TIDSPUNKT)
    def test_linja_staar_paa_siden(self, klient, adresse):
        """Ville feilet hvis linja «Oppdatert …» bare sto på oversikten og
        aksjesidene med kurser."""
        assert '<div class="rad oppdatert">' in _side(klient, adresse), adresse

    def test_samme_tidspunkt_som_oversikten(self, klient):
        """Ville feilet hvis sidene uten eget tidspunkt viste et annet enn
        oversikten (det eldste, FR-101)."""
        oversikten = _tidspunktet(_side(klient, "/"))
        for adresse in ("/folg", "/innstillinger"):
            assert _tidspunktet(_side(klient, adresse)) == oversikten, adresse

    def test_ogsaa_i_den_ekte_versjonen(self, ekte):
        """Ville feilet hvis linja bare kom i demoen."""
        for adresse in ("/folg", "/innstillinger"):
            assert '<div class="rad oppdatert">' in _side(ekte, adresse), adresse


# Tillegg 18 (ønsket 11.11 kl. 22:09): bryteren «Vis KI-tekst» som bryterne i Innstillinger.

_BRYTERNE = (
    (".side-oversikt", ".innstillingsbryter", ""),
    (".side-oversikt", ".dagsbryter", " button"),
    (".side-aksje", ".ki-bryter", " button"),
)


def _stilen(side: str, bryter: str, del_: str) -> dict[str, str]:
    stil = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
    regel = re.search(r":where\(" + re.escape(side) + r"\) " + re.escape(bryter + del_) + r" \{([^}]*)\}", stil).group(
        1
    )
    return dict((n.strip(), v.strip()) for n, v in (d.split(":", 1) for d in regel.split(";") if ":" in d))


class TestKIBryterenSomInnstillinger:
    def test_samme_skrift_og_stoerrelse(self):
        """Ville feilet hvis bryteren ved «Børsdagen kort fortalt» eller på
        aksjesiden hadde en annen skrift, høyde eller kant enn bryterne i
        Innstillinger (14 px før tillegg 18)."""
        felles = ("min-height", "padding", "border", "border-radius", "background", "color", "font-weight", "gap")
        inn = _stilen(*_BRYTERNE[0])
        assert "font-size" not in inn
        for side, bryter, del_ in _BRYTERNE[1:]:
            stil = _stilen(side, bryter, del_)
            assert "font-size" not in stil, bryter
            for egenskap in felles:
                assert stil[egenskap] == inn[egenskap], (bryter, egenskap)

    def test_samme_knott_og_farger(self):
        """Ville feilet hvis sporet eller knotten hadde en annen størrelse
        eller farge, av eller på."""
        stil = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
        for side, bryter, _ in _BRYTERNE:
            paa = "" if bryter == ".innstillingsbryter" else " "
            for del_, ord_ in (
                (" .spor", ("width: 36px", "height: 20px", "background: var(--strek-2)")),
                (" .spor::after", ("width: 16px", "height: 16px", "background: var(--hvit)")),
                (paa + '[aria-checked="true"] .spor', ("background: var(--oransje)",)),
                (paa + '[aria-checked="true"] .spor::after', ("left: 18px", "background: var(--blekk)")),
            ):
                regel = re.search(
                    r":where\(" + re.escape(side) + r"\) " + re.escape(bryter + del_) + r" \{([^}]*)\}", stil
                )
                assert regel, (bryter, del_)
                for o in ord_:
                    assert o in regel.group(1), (bryter, del_, o)

    @pytest.mark.parametrize("adresse,form", [("/", "dagsbryter"), ("/aksje/BRFE", "ki-bryter")])
    def test_samme_navn_og_paa_av(self, klient, adresse, form):
        """Ville feilet hvis bryteren het noe annet enn «Vis KI-tekst», som i
        Innstillinger, eller manglet «På» og «Av»."""
        side = _side(klient, adresse)
        bryter = side.split(f'<form class="{form}"', 1)[1].split("</form>", 1)[0]
        assert '<span class="navn">Vis KI-tekst</span>' in bryter
        assert re.search(r'<span class="verdi" aria-hidden="true">(På|Av)</span>', bryter)
        assert 'role="switch"' in bryter


# Tillegg 19 (gruppens svar 11.11 kl. 22:17): eksempelboksen i demoen er borte.


class TestEksempelboksenBorte:
    @pytest.mark.parametrize("adresse", ["/", "/min-liste"])
    def test_ikke_i_demoen(self, klient, adresse):
        """Ville feilet hvis eksempelboksen «Eksempeltall: når en endring i
        lista venter …» fortsatt sto øverst i demoen."""
        side = _side(klient, adresse)
        assert "når en endring i lista venter" not in side
        assert 'class="venter-melding demo"' not in side

    def test_malen_har_ikke_eksempelet(self):
        """Ville feilet hvis grenen med eksempelet bare var skjult, ikke borte."""
        mal = (ROT / "src" / "templates" / "index.html").read_text(encoding="utf-8")
        assert "venter-melding demo" not in mal
        assert "{% elif eksempeltall and egne %}" not in mal

    def test_den_ekte_beskjeden_naar_en_endring_venter(self, ekte):
        """Ville feilet hvis den ekte versjonen mistet beskjeden når en endring
        venter, eller viste den uten."""
        import sqlite3

        import lagring_sqlite

        assert 'class="venter-melding"' not in _side(ekte, "/")
        with sqlite3.connect(lagring_sqlite.BASE_STI) as t:
            symbol = t.execute("SELECT symbol FROM min_liste LIMIT 1").fetchone()
            symbol = symbol[0] if symbol else t.execute("SELECT symbol FROM aksje LIMIT 1").fetchone()[0]
            t.execute(
                "INSERT INTO oenske (handling, symbol, laget) VALUES ('fjern', ?, '2026-10-13T12:00:00+00:00')",
                (symbol,),
            )
        side = _side(ekte, "/")
        melding = side.split('<p class="venter-melding" role="status">', 1)[1].split("</p>", 1)[0]
        assert melding == "1 endring i lista tas i bruk ved hentingen etter kl. 22."


# Tillegg 18, steg 3 (gruppens svar 11.11 kl. 22:13): stegene om styrken og
# retningen merker bare kolonnen.


class TestKolonnestegene:
    def test_stegene_peker_paa_kolonnene(self):
        """Ville feilet hvis «Signalstyrken» eller «Retningen» fortsatt pekte
        på hele tabellen (aksjene) på oversikten eller i Min liste."""
        sider = ht.rundturer()
        for side in ("oversikt", "min_liste"):
            ankre = {s.tittel: s.anker for s in sider[side]}
            assert ankre["Signalstyrken"] == "kolonne-signal", side
            assert ankre["Retningen"] == "kolonne-retning", side

    @pytest.mark.parametrize("adresse", ["/", "/min-liste"])
    def test_overskriftene_har_ankrene(self, klient, adresse):
        """Ville feilet hvis kolonneoverskriftene manglet id-ene, så stegene
        ble hoppet over."""
        side = _side(klient, adresse)
        assert re.search(r'<th class="tall" id="kolonne-signal"[^>]*>', side)
        assert re.search(r'<th id="kolonne-retning"[^>]*>', side)

    def test_skriptet_merker_kolonnen_og_flytter_boksen(self):
        """Ville feilet hvis skriptet merket hele tabellen for en
        kolonneoverskrift, tok med flere enn de første radene, eller lot
        boksen dekke det som er merket."""
        kilde = SKRIPTET.read_text(encoding="utf-8")
        assert "const RADENE_I_KOLONNEN = 3;" in kilde
        assert 'if (del.tagName === "TH") {' in kilde and "kolonnen = merkKolonnen(del);" in kilde
        assert 'c.classList.add("omvisning-kolonne")' in kilde
        assert 'if (dekker()) boksen.classList.add("til-venstre");' in kilde
        assert 'boksen.classList.add("oeverst")' in kilde
        stil = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
        assert ".omvisning.til-venstre { right: auto; left: 16px; }" in stil
        assert re.search(r"td\.omvisning-kolonne \{ background-color:", stil)
        # Overskriften beholder den mørke bakgrunnen, så teksten kan leses.
        assert not re.search(r"th\.omvisning-kolonne \{[^}]*background", stil)


# Tillegg 20 (gruppens svar 11.11 kl. 22:20): KI-tekstene i omvisningen, den
# hele omvisningen uten stegene som gjentas, og README-en.


class TestKIStegene:
    def test_stegene_finnes_paa_sidene(self):
        """Ville feilet hvis «Børsdagen kort fortalt» eller «Signalet
        forklart» manglet som steg, eller pekte på feil del."""
        sider = ht.rundturer()
        oversikt = {s.tittel: s.anker for s in sider["oversikt"]}
        aksje = {s.tittel: s.anker for s in sider["aksje"]}
        assert oversikt["Børsdagen kort fortalt"] == "boersdagen-kort-fortalt"
        assert aksje["Signalet forklart"] == app_modul.KI_ANKER == ht.KI_ANKER
        for side in sider.values():
            assert len(side) <= ht.MAKS_STEG

    def test_teksten(self):
        """Ville feilet hvis steget ikke sa at teksten er skrevet av en
        språkmodell, merket «Laget av KI», bare fra det appen har regnet ut,
        og at bryteren slår den av og på."""
        for ord_ in ("språkmodell", "«Laget av KI»", "det appen har regnet ut", "Bryteren slår den av og på"):
            assert ord_ in ht.KI_STEGET
        assert len(ht.KI_STEGET.split()) <= 30

    def test_rekkefoelgen_paa_aksjesiden(self):
        """Ville feilet hvis steget om «Signalet forklart» sto i en annen
        rekkefølge enn delen på siden (mellom grafen og dag for dag)."""
        titler = [s.tittel for s in ht.rundturer()["aksje"]]
        assert titler.index("Kursgrafen") < titler.index("Signalet forklart") < titler.index("Dag for dag")

    def test_delene_har_ankrene_naar_de_vises(self, klient):
        """Ville feilet hvis ankeret manglet når delen vises, så steget ble
        hoppet over."""
        assert 'id="boersdagen-kort-fortalt"' in _side(klient, "/")
        assert f'id="{ht.KI_ANKER}"' in _side(klient, "/aksje/BRFE")


class TestOmvisningenUtenGjentakelser:
    def test_hopper_over_stegene_som_gjentas(self):
        """Ville feilet hvis den hele omvisningen hadde «Dagen og perioden»
        på børsometeret eller «Signalstyrken» og «Retningen» i Min liste."""
        steg = {(s["side"], s["tittel"]) for s in ht.omvisningen()}
        for par in (
            ("boersometer", "Dagen og perioden"),
            ("min_liste", "Signalstyrken"),
            ("min_liste", "Retningen"),
        ):
            assert par not in steg
        assert ("oversikt", "Signalstyrken") in steg and ("oversikt", "Dagen og perioden") in steg

    def test_vis_meg_rundt_har_dem(self):
        """Ville feilet hvis «Vis meg rundt» på sidene mistet stegene."""
        sider = ht.rundturer()
        assert "Dagen og perioden" in [s.tittel for s in sider["boersometer"]]
        assert {"Signalstyrken", "Retningen"} <= {s.tittel for s in sider["min_liste"]}

    def test_telleren_foelger_det_som_spilles(self):
        """Ville feilet hvis antallet steg i omvisningen talte med stegene som
        hoppes over (telleren regnes av lista, OMVISNING.teller)."""
        sider = ht.rundturer()
        alle = sum(len(sider[s]) for s in ht.OMVISNINGEN_SIDER)
        assert len(ht.omvisningen()) == alle - len(ht.GJENTATT_I_OMVISNINGEN)


class TestReadmeOmvisningen:
    def test_setningen_etter_dobbeltklikket(self):
        """Ville feilet hvis «Kom i gang» ikke sa rett etter dobbeltklikket at
        appen tilbyr omvisningen, «Spill av omvisningen» og «Vis meg rundt».
        Setningen står i avsnittet «Første gang», fordi «Kom i gang» har fem
        avsnitt (3.5i)."""
        readme = (ROT / "README.md").read_text(encoding="utf-8")
        etter = readme[readme.index("5. **Lukk vinduet** for å stoppe appen.") :]
        neste = etter.split("\n\n", 2)[1]
        assert neste.startswith("**Første gang**")
        # Tillegg 21 (svaret 12.11 kl. 09:58): første gang tilbys «Vis meg
        # rundt» på oversikten, ikke hele omvisningen.
        assert "Første gang tilbyr appen «Vis meg rundt» på oversikten." in neste
        assert "en omvisning av seks av sidene" not in neste
        assert "«Spill av omvisningen» øverst viser alle sidene" in neste
        assert "«Vis meg rundt» viser siden du står på" in neste

    def test_linja_under_ekstra(self):
        """Ville feilet hvis linja under «Ekstra, ferdig» fortsatt sa «ved
        «Vis meg rundt»», som før knappene kom i raden øverst, eller ikke sa
        at «Vis meg rundt» tilbys første gang på oversikten (tillegg 21)."""
        readme = (ROT / "README.md").read_text(encoding="utf-8")
        assert "«Spill av omvisningen» ved «Vis meg rundt»" not in readme
        linja = "- «Vis meg rundt» for siden du står på, første gang på oversikten, og «Spill av omvisningen» gjennom seks av sidene"
        assert linja in readme

    def test_hjelpen_om_tilbudet_og_ferdig(self):
        """Tillegg 21, steg 3: ville feilet hvis hjelpen fortsatt sa at
        omvisningen tilbys første gang, eller ikke sa hvor «Ferdig» går."""
        hjelpen = (ROT / "docs" / "hjelp.md").read_text(encoding="utf-8")
        assert "tilbys «Vis meg rundt» for oversikten øverst på den, ikke hele omvisningen" in hjelpen
        assert "tilbys omvisningen øverst" not in hjelpen
        assert "«Ferdig» går dit, med det første navnet valgt" in hjelpen
        assert "går «Ferdig» til tabellen" in hjelpen


# Tillegg 5 (gruppens svar 11.11 kl. 18:09): den første knappen i periodevalget.


def _vinduet(side: str, id_: str) -> str:
    return side.split(f'<div id="{id_}" class="hjelpevindu"', 1)[1].split('class="lukkes"', 1)[0]


class TestFoersteKnappen:
    @pytest.mark.parametrize(
        "adresse,vindu",
        [
            ("/", "hjelp-perioden"),
            ("/min-liste", "hjelp-sammenlign"),
            ("/boersometer", "hjelp-perioden"),
        ],
    )
    def test_setningen_overalt_og_demoen(self, klient, adresse, vindu):
        """Ville feilet hvis «?» ved periodevalget på en av sidene ikke sa
        hvorfor den første knappen heter som den gjør, eller demoen ikke sa
        at det er fredag 09.10."""
        tekst = _vinduet(_side(klient, adresse), vindu)
        assert ht.FOERSTE_KNAPP in tekst
        assert "I demoen er det fredag 09.10, den siste dagen med oppdiktede kurser." in tekst

    def test_ikke_demosetningen_i_den_ekte_versjonen(self, ekte):
        """Ville feilet hvis den ekte versjonen sa noe om demoen."""
        side = _side(ekte, "/")
        assert ht.FOERSTE_KNAPP in side
        assert ht.DEMO_FOERSTE_KNAPP not in side

    def test_dagen_fra_demodataene(self):
        """Ville feilet hvis dagen og datoen var skrevet inn for hånd og ikke
        regnet av SLUTTDATO i demo.py."""
        from perioder import UKEDAGER

        dag = UKEDAGER[demo.SLUTTDATO.weekday()].lower()
        assert ht.DEMO_FOERSTE_KNAPP.startswith(f"I demoen er det {dag} {demo.SLUTTDATO:%d.%m},")
        kilde = (ROT / "src" / "hjelpetekster.py").read_text(encoding="utf-8")
        assert "{UKEDAGER[SLUTTDATO.weekday()].lower()} {SLUTTDATO:%d.%m}" in kilde
        assert "fredag 09.10" not in kilde

    def test_knappen_heter_fredag_i_demoen(self, klient):
        """Ville feilet hvis den første knappen i demoen het noe annet enn
        «Fredag»."""
        assert re.search(r">\s*Fredag\s*<", _side(klient, "/").split('class="periodevalg"', 1)[1])


# Tillegg 7 (gruppens svar 11.11 kl. 19:48): «Uten ramme: 0 eller 1 av 3.»


class TestUtenRamme:
    def test_boersometeret(self, klient):
        """Ville feilet hvis forklaringen på børsometeret manglet prøven uten
        ramme eller setningen."""
        side = _side(klient, "/boersometer")
        rammen = side.split('class="symbolfelt rammefelt"', 1)[1].split("</li>", 1)[0]
        assert '<span class="proeve uten-ramme"></span>' in rammen
        assert "Uten ramme: 0 eller 1 av 3." in rammen

    @pytest.mark.parametrize(
        "adresse,vindu",
        [("/", "hjelp-signalstyrke"), ("/min-liste", "hjelp-signalstyrke"), ("/aksje/BRFE", "hjelp-styrke")],
    )
    def test_ringen_med_de_samme_ordene(self, klient, adresse, vindu):
        """Ville feilet hvis oversikten, Min liste eller aksjesiden ikke sa
        hva som er uten ring, med de samme ordene som børsometeret."""
        side = _side(klient, adresse)
        assert f'<div id="{vindu}" class="hjelpevindu"' in side, adresse
        assert "Uten ring: 0 eller 1 av 3." in _vinduet(side, vindu)

    def test_ogsaa_i_den_ekte_versjonen(self, ekte):
        """Ville feilet hvis setningene bare sto i demoen."""
        assert "Uten ramme: 0 eller 1 av 3." in _side(ekte, "/boersometer")
        assert "Uten ring: 0 eller 1 av 3." in _side(ekte, "/")

    def test_regnet_av_terskelen(self):
        """Ville feilet hvis «0 eller 1» var skrevet for hånd og ikke fulgte
        terskelen i Parametre."""
        from signalberegning import STANDARD

        assert ht.UNDER_TERSKELEN == " eller ".join(str(n) for n in range(STANDARD.terskel))


# Tillegg 13 (gruppens svar 11.11 kl. 20:33): de ferdige listene bare i steg 3.


class TestFerdigeListerBareISteg3:
    def test_bare_i_steg_3_med_ankeret(self, klient):
        """Ville feilet hvis «Start fra en ferdig liste» sto under «Følg flere
        aksjer», eller ankeret #ferdige-lister ikke var i steg 3."""
        side = _side(klient, "/min-liste")
        assert side.count('id="ferdige-lister"') == 1
        steg3 = side.split("Velg aksjene dine</h4>", 1)[1].split("</li>\n  </ol>", 1)[0]
        assert 'id="ferdige-lister"' in steg3
        flere = side.split('id="folg-flere"', 1)[1]
        assert "ferdig-liste?bransje=" not in flere.split("</section>", 1)[0]
        assert "<h4>Start fra en ferdig liste</h4>" not in side

    def test_avbryt_gaar_til_ankeret(self, klient):
        """Ville feilet hvis «Avbryt» på «Er du sikker?» pekte et annet sted."""
        side = _side(klient, "/ferdig-liste?bransje=Kraft")
        assert 'href="/min-liste#ferdige-lister">Avbryt</a>' in side


# Tillegg 14 og 15 (gruppens svar 11.11 kl. 20:39 og forslaget kl. 20:44):
# «Følg flere aksjer» som rådet tegnet.


def _flere(side: str) -> str:
    return side.split('<div class="flere-topp">', 1)[1].split('<p class="demoboks">', 1)[0]


def _foelg_i_demobasen(antall: int) -> None:
    """Legger inn ønsker om å følge til lista har antall aksjer."""
    import sqlite3

    with sqlite3.connect(demo_sti()) as t:
        i_lista = t.execute("SELECT COUNT(*) FROM aksje WHERE ut IS NULL").fetchone()[0]
        venter = "tatt_i_bruk IS NULL AND avvist IS NULL"
        i_lista += t.execute(f"SELECT COUNT(*) FROM oenske WHERE handling = 'folg' AND {venter}").fetchone()[0]
        i_lista -= t.execute(f"SELECT COUNT(*) FROM oenske WHERE handling = 'fjern' AND {venter}").fetchone()[0]
        for n in range(antall - i_lista):
            t.execute(
                "INSERT INTO oenske (handling, symbol, navn, sektor, laget) VALUES ('folg', ?, ?, 'Kraft', ?)",
                (f"TEST{n}", f"Testaksje {n}", "2026-10-13T12:00:00+00:00"),
            )


class TestFoelgFlereAksjer:
    def test_toppen_naar_lista_ikke_er_full(self, klient):
        """Ville feilet hvis tallet, de ledige plassene, rutene eller
        setningen og knappen fra forslaget kl. 20:44 manglet."""
        side = _side(klient, "/min-liste")
        flere = _flere(side)
        m = re.search(r'<p class="antall-egne">Appen følger (\d+) av 18, (\d+) plass(?:er)? ledige\.</p>', flere)
        assert m and int(m.group(1)) + int(m.group(2)) == 18
        assert 'popovertarget="hjelp-flere"' in flere
        strek = flere.split('<span class="plassstrek" aria-hidden="true">', 1)[1].split("</span></span>", 1)[0]
        assert strek.count('class="brukt"') == int(m.group(1))
        assert strek.count('class="ledig"') == int(m.group(2))
        assert "Følg en aksje til, eller bytt ut en. Endringen skjer ved neste henting." in flere
        assert '<a class="knapp hoved" href="/folg">+ Følg en aksje</a>' in flere

    def test_toppen_naar_lista_er_full(self, klient):
        """Ville feilet hvis en full liste ikke sa «, som er taket.» og
        setningen om å bytte, eller fortsatt hadde «+ Følg en aksje»."""
        _foelg_i_demobasen(18)
        flere = _flere(_side(klient, "/min-liste"))
        assert '<p class="antall-egne">Appen følger 18 av 18, som er taket.</p>' in flere
        assert "Bytt ut en aksje for å følge en annen. Byttet skjer ved neste henting." in flere
        assert 'class="ledig"' not in flere and flere.count('class="brukt"') == 18
        assert "+ Følg en aksje" not in flere

    def test_kortene_etter_bransje_i_rekkefoelgen_paa_boersometeret(self, klient):
        """Ville feilet hvis aksjene ikke sto i kort per bransje, i
        rekkefølgen på børsometeret, med antallet og lenken til aksjesiden."""
        from boersometer import BRANSJER

        flere = _flere(_side(klient, "/min-liste"))
        kortene = re.findall(r'<section class="bransjekortet"[^>]*>\s*<h4[^>]*>(.*?)</h4>(.*?)</section>', flere, re.S)
        assert kortene
        navn = [re.sub(r"<[^>]+>", "", h).split()[0] for h, _ in kortene]
        assert navn == sorted(navn, key=BRANSJER.index)
        for h, innhold in kortene:
            antall = int(re.search(r'<span class="antall">(\d+)</span>', h).group(1))
            assert innhold.count("<li>") == antall
            assert re.search(r'<a class="navn" href="/aksje/[A-Z0-9]+">', innhold)
            assert re.search(r'<a class="knapp liten" href="/folg\?bytt=', innhold)

    def test_kallene_bak_spoersmaalstegnet(self, klient):
        """Ville feilet hvis teksten om kallene og gratiskontoen sto i siden
        og ikke bak «?»."""
        side = _side(klient, "/min-liste")
        vinduet = _vinduet(side, "hjelp-flere")
        assert "Appen kan følge opptil 18 aksjer" in vinduet and "gratiskonto" in vinduet
        assert "Hver bruker har sin egen gratiskonto" not in _flere(side)

    def test_stilen_tre_kolonner_og_en_ved_390(self):
        """Ville feilet hvis kortene ikke sto i tre kolonner på bred skjerm og
        én ved 390 px, eller streken ikke var skjult for skjermlesere."""
        stil = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
        assert ".bransjekort { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));" in stil
        assert re.search(
            r"@media \(max-width: 600px\) \{\s*:where\(\.side-oversikt\) \.bransjekort \{ grid-template-columns: 1fr; \}",
            stil,
        )

    def test_den_ekte_versjonen(self, ekte):
        """Ville feilet hvis utformingen bare var i demoen, eller boksen om
        demoen sto i den ekte versjonen."""
        side = _side(ekte, "/min-liste")
        if 'id="folg-flere"' in side:
            assert 'class="bransjekortet"' in side
            assert 'class="demoboks"' not in side


# Gjennomgangen av tilleggene 5–20 (Verification Gap).


class TestGjennomgangenAvTilleggene:
    def test_hjelpetekstene_hoeyst_50_ord_uten_interne_ord(self):
        """VG4 (tillegg 18): ville feilet hvis en tekst i hjelpetekster() hadde
        over 50 ord, telt med \\w+, eller ordene «basen», «kilden»,
        «kontrollsjekken» eller «lest fra»."""
        for noekkel, tekst in ht.hjelpetekster().items():
            hele = f"{tekst.tittel} {tekst.tekst}"
            assert len(re.findall(r"\w+", hele)) <= 50, noekkel
            for ord_ in ("basen", "kilden", "kontrollsjekken", "lest fra"):
                assert ord_ not in hele, (noekkel, ord_)

    def test_tallet_paa_brikkene_staar_fast(self, klient):
        """VG5: ville feilet hvis tallet på en brikke fulgte omsetningen eller
        søket og ikke var alle som kan følges i bransjen."""

        def tallene(side):
            return re.findall(r'value="([^"]+)"[^>]*>.*?<span class="antall">(\d+)</span>', _bransjebrikkene(side))

        assert tallene(_side(klient, "/folg?omsetning=ikke&q=a")) == tallene(_side(klient, "/folg"))

    def test_en_valgt_tom_bransje_kan_velges_bort(self, klient):
        """VG5: ville feilet hvis en bransje med 0 som står i adressen, ble
        grå og låst, så den ikke kunne velges bort."""
        brikkene = _bransjebrikkene(_side(klient, "/folg"))
        tom = re.search(r'value="([^"]+)" disabled', brikkene).group(1)
        valgt = _bransjebrikkene(_side(klient, f"/folg?bransje={tom}"))
        assert f'value="{tom}" checked>' in valgt
        assert f'value="{tom}" checked disabled' not in valgt

    def test_oppdatert_paa_er_du_sikker(self, klient):
        """VG8: ville feilet hvis «Er du sikker?» manglet linja «Oppdatert …»."""
        side = _side(klient, "/min-liste")
        adresse = re.search(r'href="(/ferdig-liste\?bransje=[^"]+)"', side).group(1).replace("&amp;", "&")
        assert '<div class="rad oppdatert">' in _side(klient, adresse)

    def test_ferdige_lister_ikke_i_noe_kort(self, klient):
        """VG12: ville feilet hvis en ferdig liste sto i et av kortene under
        «Følg flere aksjer», ikke bare det første."""
        side = _side(klient, "/min-liste")
        assert "ferdig-liste?bransje=" not in _flere(side)

    def test_min_liste_med_vis_dagen_som_foer(self, klient):
        """VG12 (spørsmål 13): ville feilet hvis overskriften i Min liste med
        «Vis dagen» ikke lenger sa siste børsdag, der radene står."""
        assert _overskriften(_side(klient, "/min-liste?periode=velg&dag=2026-10-06")).endswith("fredag")

    def test_ki_steget_sier_med_ki_paa(self):
        """BH8: ville feilet hvis steget sa at teksten alltid er skrevet av KI,
        også når KI er av og bare appens setninger står."""
        assert ht.KI_STEGET.startswith("Med KI på står en tekst skrevet av en språkmodell")

    @pytest.mark.skipif(NODE is None, reason="trenger node")
    def test_sorteringen_som_serveren_med_aa(self):
        """ECH1: ville feilet hvis skriptet sorterte «Aasen» blant Å-navnene,
        som localeCompare i nb gjør, og ikke som ferdige_lister._norsk."""
        rader = [
            {"navn": "ålesund", "kode": "x", "median": "1", "rang": "0"},
            {"navn": "aasen sparebank", "kode": "aasb", "median": "1", "rang": "0"},
            {"navn": "zeta", "kode": "z", "median": "1", "rang": "0"},
        ]
        js = _Node()._kjoer(
            f"{json.dumps(rader)}.sort((a, b) => o.FOLGLISTA.sammenlign(a, b, 'navn')).map((r) => r.kode)"
        )
        assert js == ["aasb", "z", "x"]

    def test_uten_hjelp_staar_kallene_i_siden(self, klient):
        """ECH3: ville feilet hvis teksten om kallene og gratiskontoen
        forsvant helt med «Vis hjelp» av."""
        klient.post("/innstillinger", data={"navn": "vis_hjelp", "til": "av"})
        side = _side(klient, "/min-liste")
        assert 'id="hjelp-flere"' not in side
        assert "Hver bruker har sin egen gratiskonto hos EODHD" in _flere(side)


# Tillegg 21 (gruppens svar 12.11 kl. 09:58, «Brukerutfall» i §7 i PRD-en):
# tilbudet første gang starter «Vis meg rundt» for oversikten, og det siste
# steget der viser vei til navnene under «Skilte seg ut».


def _funksjonen(navn: str) -> str:
    skriptet = SKRIPTET.read_text(encoding="utf-8")
    start = skriptet.index(f"  function {navn}(")
    return skriptet[start : skriptet.index("\n  }\n", start)]


def _del_ut(side: str) -> str | None:
    """tbody-en med raden «Skilte seg ut» i tabellen #aksjene, eller None."""
    tabellen = side[side.index('id="aksjene"') :]
    for tbody in tabellen.split("<tbody>")[1:]:
        tbody = tbody.split("</tbody>", 1)[0]
        if '<tr class="del ut">' in tbody:
            return tbody
    return None


class TestTilbudetOgVeienVidere:
    def test_tilbudet_starter_vis_meg_rundt_for_oversikten(self):
        """Tillegg 21, steg 1: ville feilet hvis ja i tilbudet første gang
        startet hele omvisningen på 23 steg, og ikke «Vis meg rundt» for
        oversikten, eller teksten ikke sa hva brukeren får."""
        tilby = _funksjonen("tilby")
        assert 'knapp("Vis meg rundt", "omvisning-ja"' in tilby
        assert "visSiden(sidensListe)" in tilby and "start()" not in tilby
        assert 'skriv(localStorage, OMVISNING.SVARET, "ja")' in tilby
        assert 'knapp("Nei takk"' in tilby
        assert "tekst.textContent = OMVISNING.TILBUDET" in tilby

    @pytest.mark.skipif(NODE is None, reason="trenger node")
    def test_teksten_i_tilbudet(self):
        """Tillegg 21, steg 1: ville feilet hvis tilbudet fortsatt sa at
        omvisningen viser sidene i appen."""
        tekst = _Node()._kjoer("o.TILBUDET")
        assert tekst == "Første gang her? «Vis meg rundt» viser deg denne siden, ett steg om gangen."

    @pytest.mark.skipif(NODE is None, reason="trenger node")
    def test_linja_bare_paa_oversikten_med_vis_meg_rundt(self):
        """Tillegg 21, steg 2: ville feilet hvis linja sto i hele omvisningen,
        som går videre til aksjesiden selv, eller i «Vis meg rundt» på en
        annen side enn oversikten."""
        n = _Node()
        ut = n._kjoer("o.videre('oversikt', true, true)")
        assert ut == {
            "linje": "Klikk så et navn under «Skilte seg ut» for å se hvorfor aksjen skilte seg ut.",
            "maal": "ut",
        }
        assert n._kjoer("o.videre('oversikt', false, true)") is None
        for side in ("min_liste", "boersometer", "aksje", "folg", "innstillinger"):
            assert n._kjoer(f"o.videre('{side}', true, true)") is None, side

    @pytest.mark.skipif(NODE is None, reason="trenger node")
    def test_linja_naar_ingen_aksje_staar_der(self):
        """Tillegg 21, steg 2: ville feilet hvis linja pekte på «Skilte seg ut»
        også når ingen aksje står der, eller «Ferdig» ikke gikk til tabellen."""
        ingen = _Node()._kjoer("o.videre('oversikt', true, false)")
        assert ingen == {"linje": "Klikk så et navn i tabellen for å se sjekkene for aksjen.", "maal": "tabellen"}

    def test_linja_bare_paa_det_siste_steget_og_ikke_et_eget_steg(self):
        """Tillegg 21, steg 2: ville feilet hvis linja sto på andre steg enn
        det siste, over knappene, eller var et eget steg, så MAKS_STEG = 7
        ikke lenger holdt."""
        vis = _funksjonen("vis")
        assert "const videre = siste ? OMVISNING.videre(SIDE, aktive !== steg, foersteNavn() !== null) : null;" in vis
        assert vis.index("boksen.append(linja)") < vis.index("boksen.append(knappene)") < vis.index("omvisning-hele")
        stegene = ht.rundturer()["oversikt"]
        assert len(stegene) <= ht.MAKS_STEG == 7
        assert not any("Klikk så et navn" in s.tekst for s in stegene)

    def test_ferdig_gaar_til_skilte_seg_ut(self):
        """Tillegg 21, steg 2: ville feilet hvis «Ferdig» bare lukket boksen,
        og ikke ga fokus til det første navnet under «Skilte seg ut», eller
        til tabellen når ingen aksje står der."""
        vis = _funksjonen("vis")
        assert "const ferdig = videre ? () => tilNavnene(videre.maal) : avslutt;" in vis
        assert "siste ? ferdig() : gaaTil(j + 1, 1)" in vis
        foerste = _funksjonen("foersteNavn")
        assert 'document.querySelector("#aksjene tr.del.ut")' in foerste
        assert 'a[href^="/aksje/"]' in foerste
        til = _funksjonen("tilNavnene")
        assert til.index("avslutt();") < til.index("navnet.focus(")
        assert 'document.getElementById("aksjene")' in til and "tabellen.focus(" in til

    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    def test_siden_har_det_skriptet_leter_etter(self, versjon, request):
        """Tillegg 21: ville feilet hvis oversikten ikke hadde raden «Skilte
        seg ut» med en lenke til en aksjeside i samme del av tabellen #aksjene,
        som skriptet gir fokus til, eller hadde den med en sortering, der
        «Ferdig» skal gå til tabellen. Likt i demoen og i den ekte versjonen."""
        k = request.getfixturevalue(versjon)
        delen = _del_ut(_side(k, "/"))
        assert delen is not None and 'href="/aksje/' in delen
        sortert = _side(k, "/?sorter=signal&orden=synkende")
        assert 'id="aksjene"' in sortert and _del_ut(sortert) is None

    def test_uten_vis_meg_rundt_kommer_ikke_tilbudet(self):
        """Tillegg 21: ville feilet hvis tilbudet kom uten knappen «Vis meg
        rundt» på siden, der ja ikke ville gjort noe."""
        oppstart = _funksjonen("oppstart")
        assert "sidensListe &&" in oppstart


# Tillegg 22 (gruppens svar 12.11 kl. 10:16, spørsmål 10): hvorfor en aksje er
# uten kurser, uten «nettopp er lagt til», og hva neste henting gjør.


class TestUtenKurserEtterSvaret:
    def test_ikke_venter_paa_hentingen_som_grunn(self):
        """Ville feilet hvis forklaringen fortsatt ga «nettopp er lagt til og
        venter på hentingen» som grunn, når en aksje som venter, står med
        «venter på henting»."""
        hvorfor = ht.UTEN_KURSER_HVORFOR
        assert "nettopp" not in hvorfor and "venter på hentingen" not in hvorfor
        assert "EODHD har ikke gitt kurser for aksjen." in hvorfor

    def test_sier_hva_neste_henting_gjoer_som_koden(self):
        """Ville feilet hvis forklaringen ikke sa hva som skjer når EODHD heller
        ikke gir kurser ved neste henting, eller sa noe annet enn
        valg.uten_rader gjør: bare en aksje brukeren har valgt selv, tas ut."""
        import valg

        assert "Gir EODHD ingen kurser ved neste henting heller, slutter appen å følge en aksje du har valgt selv." in (
            ht.UTEN_KURSER_HVORFOR
        )
        kilden = Path(valg.__file__).read_text(encoding="utf-8")
        funksjonen = kilden[kilden.index("def uten_rader(") :].split(chr(10) + "def ", 1)[0]
        assert "egne_i_lista(tilkobling)" in funksjonen and "UPDATE aksje SET ut = ?" in funksjonen

    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    def test_hjelpen_begynner_med_ordene_fra_raden(self, versjon, request):
        """Ville feilet hvis hjelpeteksten bak «?» ved «Oppdatert» begynte med
        «Uten data», ikke «Ingen kurser ennå» som raden, eller hadde over tre
        setninger (8.0c). Likt i demoen og i den ekte versjonen."""
        k = request.getfixturevalue(versjon)
        vindu = html.unescape(_side(k, "/").split('id="hjelp-hentet"', 1)[1].split('<p class="lukkes">', 1)[0])
        assert "<strong>Ingen kurser ennå:</strong> EODHD har ikke gitt kurser for aksjen." in vindu
        assert "Uten data" not in vindu
        tekst = ht.hjelpetekster()["uten_data"].tekst
        assert len(re.findall(r"[.!?](?:\s|$)", tekst)) <= 3, tekst

    def test_matfjord_i_demoen_som_foer(self, klient):
        """Ville feilet hvis linja om Matfjord Merkevarer i demoen var endret
        eller borte."""
        vindu = html.unescape(_side(klient, "/").split('id="hjelp-hentet"', 1)[1])
        assert "I demoen er Matfjord Merkevarer med vilje uten kurser, så du ser hvordan det ser ut." in vindu

    def test_hjelpen_i_docs_foelger(self):
        """Regel 19: ville feilet hvis docs/hjelp.md fortsatt ga «nettopp er
        lagt til og venter på hentingen» som grunn."""
        hjelpen = (ROT / "docs" / "hjelp.md").read_text(encoding="utf-8")
        assert "fordi den nettopp er lagt til og venter på hentingen om kvelden" not in hjelpen
        assert "«?» ved «Oppdatert» sier hvorfor: EODHD har ikke gitt kurser for aksjen." in hjelpen
        assert "slutter appen å følge en aksje du har valgt selv" in hjelpen


def _til_faglaerer() -> list[str]:
    """Linjene under «Til faglærer:» i README-en, til første tomme linje."""
    tekst = (ROT / "README.md").read_text(encoding="utf-8")
    return tekst.split("Til faglærer:\n", 1)[1].split("\n\n", 1)[0].splitlines()


class TestTilFaglaererEtterSvaret:
    """Tillegg 23 (gruppens svar 12.11 kl. 16:23): README-en er inngangen for
    faglærer. Rett etter «Prøv appen» står hovedflyten i demoen og
    brukertesten, som underpunkter, så de fire punktene fra svaret 29.10
    kl. 19:36 står."""

    def test_hovedflyten_rett_etter_proev_appen(self):
        """Ville feilet hvis linja om hovedflyten manglet, ikke sto rett etter
        «Prøv appen», eller brukte andre ord enn appen."""
        linjene = _til_faglaerer()
        assert linjene[0].startswith("- Prøv appen: ")
        assert linjene[1].startswith("  - Hovedflyten i demoen: "), linjene[1]
        linja = linjene[1]
        for ord_ in (
            "øverst i tabellen på oversikten, under «Skilte seg ut»",
            "«Hvorfor signalet ble …»",
            "«Signalet forklart»",
            "«Vis meg rundt» viser siden du står på",
            "«Spill av omvisningen» alle sidene",
        ):
            assert ord_ in linja, ord_

    def test_ordene_finnes_i_appen(self):
        """Ville feilet hvis en overskrift eller knapp linja nevner, het noe
        annet i malene."""
        maler = ROT / "src" / "templates"
        index = (maler / "index.html").read_text(encoding="utf-8")
        aksje = (maler / "aksje.html").read_text(encoding="utf-8")
        rundtur = (maler / "_rundtur.html").read_text(encoding="utf-8")
        assert '<tr class="del ut"><th colspan="5" scope="rowgroup">Skilte seg ut <span' in index
        assert "<h2>Hvorfor signalet ble {%" in aksje
        assert '<span id="ki-tittel">Signalet forklart</span>' in aksje
        assert "</svg>Vis meg rundt</button>" in rundtur and "</svg>Spill av omvisningen</button>" in rundtur

    def test_hovedflyten_i_demoen_har_aksjer_under_skilte_seg_ut(self, klient):
        """Ville feilet hvis demoen ikke hadde noen aksje under «Skilte seg
        ut», så linja viste til en tom del, eller delen ikke sto først i
        tabellen."""
        side = _side(klient, "/")
        tabellen = side.split('id="aksjene"', 1)[1]
        assert tabellen.index('<tr class="del') == tabellen.index('<tr class="del ut">')
        ut = tabellen.split('<tr class="del ut">', 1)[1].split("</tbody>", 1)[0]
        assert 'href="/aksje/' in ut

    def test_brukertesten_med_lenke(self):
        """Ville feilet hvis linja om brukertesten manglet, ikke sto etter
        hovedflyten, ikke lenket til docs/brukertest.md, eller ikke sa målet
        om under 5 minutter og hva som tok tid 10.11."""
        linja = _til_faglaerer()[2]
        assert linja.startswith("  - Brukertesten: målet i PRD-en er "), linja
        assert linja.endswith("[brukertesten](docs/brukertest.md)"), linja
        assert "på under 5 minutter" in linja and "10.11 tok det over 5 minutter" in linja
        assert "Etter det har appen fått " in linja
        assert (ROT / "docs" / "brukertest.md").exists()
        # Målet står i PRD-en, og at testen tok over 5 minutter i brukertesten.
        prd = (
            ROT / "_bmad-output" / "planning-artifacts" / "prds" / "prd-G74-lund-osen-2026-09-20" / "prd.md"
        ).read_text(encoding="utf-8")
        assert "| Brukerutfall | En person utenfor gruppen" in prd and "under 5 minutter" in prd
        brukertest = (ROT / "docs" / "brukertest.md").read_text(encoding="utf-8")
        assert "| Tiden fra oversikten ble vist til forklaringen | Over 5 minutter" in brukertest
        assert "gikk seg vill på noen sider" in brukertest


class TestReadmenSierAtV1ErFerdig:
    """Tillegg 23, steg 2: README-en sier ikke lenger at appen er under
    utvikling, og linja i «Status» om endringer i lista følger tillegg 19."""

    def test_status_om_endringer_i_lista_i_demoen(self):
        """Ville feilet hvis «Status» fortsatt sa at demoen viser et eksempel
        på meldingen, som tillegg 19 tok bort, eller hvis malen ikke lenger
        sa at demoen ikke tar endringen i bruk."""
        readme = (ROT / "README.md").read_text(encoding="utf-8")
        status = readme.split("\n## Status\n", 1)[1].split("\n## ", 1)[0]
        assert "viser et eksempel på meldingen" not in readme
        assert (
            "Bare i den ekte versjonen tas endringer i lista i bruk ved hentingen etter kl. 22; demoen henter "
            "ikke, og sier at en endring ikke tas i bruk der." in status
        )
        index = (ROT / "src" / "templates" / "index.html").read_text(encoding="utf-8")
        assert "Demoen henter ikke, så {{" in index and "ikke i bruk her." in index

    def test_ingen_linje_sier_under_utvikling(self):
        """Ville feilet hvis README-en noe sted sa at appen eller prosjektet er
        under utvikling."""
        readme = (ROT / "README.md").read_text(encoding="utf-8")
        assert "under utvikling" not in readme
        assert readme.count("Versjon 1 er ferdig") == 2


def _tabellraden(navn: str) -> list[str]:
    """Cellene i raden navn i tabellen «Demoen og den ekte versjonen»."""
    tekst = (ROT / "README.md").read_text(encoding="utf-8")
    tabellen = tekst.split("**Demoen og den ekte versjonen:**", 1)[1].split("\n\nTil faglærer:\n", 1)[0]
    rader = [r for r in tabellen.splitlines() if r.startswith(f"| {navn} |")]
    assert len(rader) == 1, navn
    return [c.strip() for c in rader[0].strip("|").split("|")]


class TestTabellenOmForskjellene:
    """Tillegg 23, steg 4 (ønsket 12.11 kl. 16:24): radene for forskjellene
    mellom demoen og den ekte versjonen, med ordene sjekket mot koden og
    docs/installasjon.md."""

    def test_ki_teksten(self):
        """Ville feilet hvis raden sa noe annet enn at demoen har ferdige
        tekster, og at den ekte står på med Gemma eller egen nøkkel, eller hvis
        .env.example ikke lenger hadde KI på (lokal), startskriptet ikke tilbød
        Gemma og egen nøkkel, eller aksjesiden ikke hadde lenken uten modell.
        Rettet i story 3.7 (tillegg 1 og 5): .env.example har lokal, ikke av."""
        _, demoen, ekte = _tabellraden("KI-tekst")
        assert demoen == "Ferdige tekster for siste dag, laget én gang med Gemma"
        assert ekte == (
            "På: Gemma på maskinen, som vinduet i Windows tilbyr å hente første gang, eller en egen nøkkel "
            "til en KI-tjeneste. Uten modell lages ingen tekst, og siden sier hvordan den slås på"
        )
        assert "OSE_KI_TJENESTE=lokal" in (ROT / ".env.example").read_text(encoding="utf-8")
        tilbudet = (ROT / "start" / "ki-modell.ps1").read_text(encoding="utf-8")
        assert "function Ki-HentGemma" in tilbudet and "function Ki-EgenNoekkel" in tilbudet
        assert "Slik slår du den på" in (ROT / "src" / "templates" / "aksje.html").read_text(encoding="utf-8")
        assert "laget én gang med Gemma" in (ROT / "src" / "demo.py").read_text(encoding="utf-8")
        installasjonen = (ROT / "docs" / "installasjon.md").read_text(encoding="utf-8")
        assert "Ingen nøkkel følger med appen eller repoet." in installasjonen

    def test_dagen(self):
        """Ville feilet hvis demoens siste dag ikke var fredag 09.10.2026."""
        _, demoen, ekte = _tabellraden("Dagen")
        assert demoen == "Fast: fredag 09.10.2026"
        assert demo.SLUTTDATO == datetime(2026, 10, 9).date() and demo.SLUTTDATO.weekday() == 4
        assert ekte == "Den siste børsdagen som er hentet"

    def test_endringer_i_lista(self):
        """Ville feilet hvis raden sa at demoen tar endringer i bruk."""
        _, demoen, ekte = _tabellraden("Endringer i lista")
        assert demoen == "Tas ikke i bruk, fordi demoen ikke henter"
        assert ekte == "Tas i bruk ved hentingen etter kl. 22"

    def test_notatene(self):
        """Ville feilet hvis startskriptene ikke lenger lagde demobasen på
        nytt ved hver start, så raden om notatene ikke stemte."""
        _, demoen, ekte = _tabellraden("Notatene")
        assert demoen == "Bare til demoen startes på nytt, fordi demobasen lages på nytt ved hver start"
        assert ekte == "Lagres i basen på maskinen"
        assert "uv run python src/demo.py" in (ROT / "start" / "start.ps1").read_text(encoding="utf-8")
        assert "uv run python src/demo.py ||" in (ROT / "start" / "start.sh").read_text(encoding="utf-8")
        assert 'entrypoint: ["python", "src/demo.py"]' in (ROT / "compose.yaml").read_text(encoding="utf-8")

    def test_anbefalingen_som_foer(self):
        """Ville feilet hvis «Prøv appen» ikke lenger anbefalte demoen først og
        den ekte etterpå."""
        linja = _til_faglaerer()[0]
        assert linja.index("demoen med oppdiktede tall") < linja.index("Prøv gjerne ekte kurser etterpå")
