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
    @pytest.mark.parametrize("sti", ["/", "/min-liste", "/?vis=min"])
    def test_filteret_er_borte(self, versjon, sti, request):
        """Ønsket kl. 17:48: ville feilet hvis raden «Alle», «3 av 3 positiv»
        og «3 av 3 negativ», linja om filteret eller lenken til 2 av 3 sto
        igjen, eller «Alle | Min liste» forsvant med den."""
        k = request.getfixturevalue(versjon)
        side = _side(k, sti)
        assert 'class="signalfilter"' not in side and 'class="filtertekst"' not in side
        assert "3 av 3 positiv" not in side and "Filteret viser" not in side and "signal=" not in side

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
    @pytest.mark.parametrize("versjon", ["klient", "ekte"])
    def test_ingen_side_sier_uten_data(self, versjon, request):
        """Ønsket kl. 17:44: ville feilet hvis en side fortsatt sa «uten data»
        uten å si hvorfor."""
        k = request.getfixturevalue(versjon)
        for sti in ("/", "/min-liste?vis=alle", "/boersometer"):
            assert not re.search(r"[Uu]ten data", _side(k, sti)), sti

    def test_raden_uten_kurser_sier_det(self, klient):
        """Ville feilet hvis raden for en aksje uten en eneste kurs (MTFJ i
        demoen) ikke sa «ingen kurser ennå» under «–», som «for kort
        historikk» sier sitt, eller båndet ikke talte dem som «uten kurser»."""
        side = _side(klient, "/")
        rad = side.split('<a href="/aksje/MTFJ">', 1)[1].split("</tr>", 1)[0]
        assert '– <span class="merke mangler">ingen kurser ennå</span>' in rad
        assert "Ukjent" in rad
        assert re.search(r"og 1 uten kurser</span>", side)

    def test_boersometeret_sier_ingen_kurs(self, klient):
        """Ville feilet hvis ruta sa «Uten data», eller tabellen under kartet
        ikke sa «Ingen kurser ennå»."""
        import boersometer

        side = _side(klient, "/boersometer")
        rute = side.split('href="/aksje/MTFJ"', 1)[1].split("</a>", 1)[0]
        assert boersometer.UTEN_DATA == "Ingen kurs"
        assert '<span class="endring">Ingen kurs</span>' in rute
        assert 'title="MTFJ: ingen kurser ennå"' in side
        tabell = side.split("<table", 1)[1].split("</table>", 1)[0]
        assert "Ingen kurser ennå" in tabell

    def test_ingen_kurs_faar_plass_i_en_stor_rute(self):
        """Ville feilet hvis den nye teksten gjorde en stor rute for smal, så
        grensen for store ruter (STOR) ikke lenger gjaldt."""
        import boersometer

        bredde = boersometer.stor_bredde("AKRBP", None, False, boersometer.UTEN_DATA)
        assert bredde <= boersometer.STOR[0]

    def test_ukjent_forklares_bak_spoersmaalstegnet(self):
        """Ville feilet hvis «Ukjent» bak «?» ved Retning ikke sa at det også
        gjelder en aksje uten kurser."""
        tekst = ht.hjelpetekster()["ukjent"].tekst
        assert "eller aksjen har ingen kurser ennå" in tekst
        assert ht.hjelpetekster()["uten_data"].tittel == "Ingen kurser ennå:"
