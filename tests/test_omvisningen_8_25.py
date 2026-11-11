"""Story 8.25: «Spill av omvisningen» ved «Vis meg rundt» (gruppens svar
10.11 kl. 22:59).

Spesifikasjonen er spec-8-25-spill-av-omvisningen.md, med delene A-D.
Testbasene ligger i tmp_path (conftest.py, regel 22), og ingen test gjør
nettkall (AD-8). Logikken i skriptet kjøres med Node når Node finnes, og
testene for den hoppes ellers over.
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
from hjelpetekster import OMVISNINGEN_SIDER, omvisningen, rundturer
from lagring_sqlite import demo_sti
from test_hjelpetekster import RAADSORD

ROT = Path(__file__).resolve().parents[1]
SKRIPTET = ROT / "src" / "static" / "hjelp.js"
NODE = shutil.which("node")
SIDENE = {
    "oversikt": "/",
    "aksje": "/aksje/BRFE",
    "boersometer": "/boersometer",
    "min_liste": "/min-liste?vis=alle",
    "innstillinger": "/innstillinger",
}


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


def _dataene(side: str) -> tuple[str, list]:
    m = re.search(r'<div id="omvisning" hidden data-side="([^"]*)" data-steg="([^"]*)"></div>', side)
    assert m, "dataene for omvisningen mangler"
    return m.group(1), json.loads(html.unescape(m.group(2)))


# --- A) Knappen og rekkefølgen ------------------------------------------------


class TestKnappenOgRekkefoelgen:
    def test_knappen_staar_ved_vis_meg_rundt(self, klient):
        """Del A: ville feilet hvis knappen manglet ved «Vis meg rundt», eller
        lista fra 8.9 ble borte."""
        for adresse in SIDENE.values():
            side = klient.get(adresse).data.decode("utf-8")
            rundtur = side[side.index('<div class="rad rundtur-rad">') :]
            rundtur = rundtur[: rundtur.index("</div>")]
            assert '<button type="button" class="spill-av" hidden>Spill av omvisningen</button>' in rundtur, adresse
            assert '<ol class="rundtur-steg">' in rundtur, adresse

    def test_sidene_i_fast_rekkefoelge(self, klient):
        """Del A: ville feilet hvis omvisningen gikk gjennom sidene i en annen
        rekkefølge enn oversikten, en aksjeside, børsometeret, Min liste og
        Innstillinger."""
        assert OMVISNINGEN_SIDER == ("oversikt", "aksje", "boersometer", "min_liste", "innstillinger")
        _, steg = _dataene(klient.get("/").data.decode("utf-8"))
        rekkefoelgen = list(dict.fromkeys(s["side"] for s in steg))
        assert rekkefoelgen == list(OMVISNINGEN_SIDER)
        skriptet = SKRIPTET.read_text(encoding="utf-8")
        assert 'SIDENE: ["oversikt", "aksje", "boersometer", "min_liste", "innstillinger"]' in skriptet

    def test_hver_side_vet_hvilken_side_den_er(self, klient):
        """Del A: ville feilet hvis en side ga skriptet feil navn, så steget
        for siden ble hoppet over eller sendte til en annen side."""
        for navn, adresse in SIDENE.items():
            side, _ = _dataene(klient.get(adresse).data.decode("utf-8"))
            assert side == navn, adresse

    def test_hvert_steg_peker_paa_en_del_som_finnes(self, klient):
        """Del B: ville feilet hvis et steg pekte på en del som ikke finnes på
        siden sin i demoen, så omvisningen hoppet over den."""
        for navn, adresse in SIDENE.items():
            side = klient.get(adresse).data.decode("utf-8")
            _, steg = _dataene(side)
            mangler = [s["anker"] for s in steg if s["side"] == navn and f'id="{s["anker"]}"' not in side]
            assert not mangler, (adresse, mangler)


# --- B) Stegene, tastaturet og skjermleseren ---------------------------------


class TestStegene:
    def test_tekstene_er_de_samme_som_vis_meg_rundt(self):
        """Del B: ville feilet hvis omvisningen hadde egne tekster, ikke de
        samme som «Vis meg rundt» i hjelpetekster.py."""
        sider = rundturer()
        venta = [(side, s.anker, s.tittel, s.tekst) for side in OMVISNINGEN_SIDER for s in sider[side]]
        assert [(s["side"], s["anker"], s["tittel"], s["tekst"]) for s in omvisningen()] == venta

    def test_skriptet_har_knappene_tastaturet_og_rollen(self):
        """Del B: ville feilet hvis steget manglet «Tilbake», «Neste» eller
        «Lukk», Esc ikke lukket, fokus ikke ble flyttet til steget, eller
        skjermleseren ikke fikk rollen dialog med tittelen."""
        skriptet = SKRIPTET.read_text(encoding="utf-8")
        for bit in (
            'knapp("Tilbake"',
            '"Neste"',
            'knapp("Lukk"',
            'e.key === "Escape"',
            'setAttribute("role", "dialog")',
            'setAttribute("aria-labelledby", "omvisning-tittel")',
            "boksen.focus()",
            'classList.add("omvisning-merket")',
        ):
            assert bit in skriptet, bit

    def test_uten_skriptet_er_knappen_skjult(self, klient):
        """Del B: ville feilet hvis knappen sto synlig uten skriptet, der den
        ikke gjør noe."""
        side = klient.get("/").data.decode("utf-8")
        assert re.search(r'<button type="button" class="spill-av" hidden>', side)
        assert '<div id="omvisning" hidden' in side

    def test_vis_hjelp_av_tar_bort_omvisningen(self, klient):
        """Del B: ville feilet hvis omvisningen sto med «Vis hjelp» av, som tar
        bort «Vis meg rundt»."""
        klient.post("/innstillinger", data={"navn": "vis_hjelp", "til": "av"})
        side = klient.get("/").data.decode("utf-8")
        assert 'id="omvisning"' not in side and "Spill av omvisningen" not in side


@pytest.mark.skipif(NODE is None, reason="Node finnes ikke på maskinen")
class TestLogikkenMedNode:
    def _kjoer(self, uttrykk: str):
        kode = f"const o = require({json.dumps(str(SKRIPTET))}); console.log(JSON.stringify({uttrykk}));"
        svar = subprocess.run([NODE, "-e", kode], capture_output=True, text=True, timeout=60)
        assert svar.returncode == 0, svar.stderr
        return json.loads(svar.stdout)

    STEG = (
        '[{"side":"oversikt","anker":"a"},{"side":"oversikt","anker":"b"},'
        '{"side":"aksje","anker":"c"},{"side":"oversikt","anker":"d"}]'
    )

    def test_et_steg_uten_delen_hoppes_over(self):
        """Del B: ville feilet hvis omvisningen stoppet ved et steg uten delen
        på siden, i stedet for å gå videre i samme retning."""
        assert self._kjoer(f"o.nesteSteg({self.STEG}, 0, 1, 'oversikt', (a) => a !== 'a')") == 1
        assert self._kjoer(f"o.nesteSteg({self.STEG}, 1, -1, 'oversikt', (a) => a !== 'b')") == 0

    def test_et_steg_paa_en_annen_side_gis_tilbake(self):
        """Del A: ville feilet hvis et steg på neste side ble hoppet over fordi
        delen ikke finnes på denne siden."""
        assert self._kjoer(f"o.nesteSteg({self.STEG}, 1, 1, 'oversikt', () => false)") == 2

    def test_ingen_flere_steg(self):
        assert self._kjoer(f"o.nesteSteg({self.STEG}, 3, 1, 'oversikt', () => false)") == -1
        assert self._kjoer(f"o.nesteSteg({self.STEG}, 4, 1, 'oversikt', () => true)") == -1

    def test_adressene(self):
        """Del A: ville feilet hvis en side fikk feil adresse, eller aksjesiden
        ble gjettet når den ikke er kjent."""
        assert self._kjoer("o.adresse('oversikt', null)") == "/"
        assert self._kjoer("o.adresse('min_liste', null)") == "/min-liste?vis=alle"
        assert self._kjoer("o.adresse('aksje', null)") is None
        assert self._kjoer("o.adresse('aksje', '/aksje/BRFE')") == "/aksje/BRFE"
        assert self._kjoer("o.teller(2, 21)") == "Steg 3 av 21"


# --- C) Første gang ------------------------------------------------------------


class TestFoersteGang:
    def test_tilbudet_og_svaret_huskes_i_nettleseren(self):
        """Del C: ville feilet hvis tilbudet kom på andre sider enn
        oversikten, ikke hadde «Nei takk», eller svaret ikke ble husket."""
        skriptet = SKRIPTET.read_text(encoding="utf-8")
        assert "OMVISNING.skalTilby(SIDE, les(localStorage, OMVISNING.SVARET))" in skriptet
        assert 'knapp("Nei takk"' in skriptet
        assert 'skriv(localStorage, OMVISNING.SVARET, "nei")' in skriptet
        assert 'skriv(localStorage, OMVISNING.SVARET, "ja")' in skriptet

    def test_ingen_migrasjon(self):
        """Spørsmål 3: ville feilet hvis svaret ble lagret i basen, med en
        migrasjon som bare kan flettes kl. 23:50-23:58. Gjennomgangen (VG4,
        BH14): ser etter omvisningen i migrasjonene, ikke etter nummeret."""
        for fil in (ROT / "src" / "migrasjoner").glob("*.sql"):
            assert "omvisning" not in fil.read_text(encoding="utf-8").lower(), fil.name


# --- D) Ingen råd, og lik i begge versjonene ---------------------------------


class TestRaadOgVersjonene:
    def test_ingen_tekst_gir_raad(self):
        """Del D, NFR-06: ville feilet hvis et steg eller tilbudet ga råd eller
        sa noe om hva kursen vil gjøre."""
        skriptet = SKRIPTET.read_text(encoding="utf-8")
        tilbudet = re.search(r'tekst\.textContent = "([^"]+)"', skriptet).group(1)
        for tekst in [*(f"{s['tittel']} {s['tekst']}" for s in omvisningen()), tilbudet]:
            for ord_ in RAADSORD:
                assert not re.search(ord_, tekst, re.IGNORECASE), (ord_, tekst)

    def test_lik_i_demoen_og_den_ekte_versjonen(self, klient, tmp_path, monkeypatch):
        """Del D: ville feilet hvis omvisningen var en annen i den ekte
        versjonen enn i demoen."""
        import lagring_sqlite
        from test_fetch_prices import OEYEBLIKK_22_09, kjoer_23

        _, demoen = _dataene(klient.get("/").data.decode("utf-8"))
        raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
        monkeypatch.delenv(app_modul.I_DEMO, raising=False)
        _, ekte = _dataene(app_modul.app.test_client().get("/").data.decode("utf-8"))
        assert ekte == demoen


class TestEtterBygget:
    def test_et_tomt_anker_merker_delen_etter(self):
        """Del B: ville feilet hvis omvisningen merket et tomt merke fra 8.9,
        som <span id="noekkeltallene">, i stedet for delen etter det."""
        skriptet = SKRIPTET.read_text(encoding="utf-8")
        assert "anker.nextElementSibling" in skriptet
        assert "const del = delen(document.getElementById(s.anker));" in skriptet

    def test_readme_og_hjelpen_nevner_omvisningen(self):
        """Regel 19: ville feilet hvis README-en eller hjelpen ikke nevnte
        omvisningen."""
        assert "en omvisning gjennom fem av sidene" in (ROT / "README.md").read_text(encoding="utf-8")
        hjelpen = (ROT / "docs" / "hjelp.md").read_text(encoding="utf-8")
        assert "«Spill av omvisningen»" in hjelpen and "«Nei takk»" in hjelpen


@pytest.mark.skipif(NODE is None, reason="Node finnes ikke på maskinen")
class TestOppfoerselenMedNode(TestLogikkenMedNode):
    """Gjennomgangen (VG1, BH14): det skriptet gjør, kjørt med Node, ikke bare
    søkt etter i teksten."""

    def test_fortsetter_bare_paa_adressen_omvisningen_gikk_til(self):
        """BH1, ECH1, ECH2: ville feilet hvis omvisningen fortsatte på en side
        brukeren gikk til selv, eller på en feilside, og sendte brukeren
        tilbake."""
        lagret = "o.tilstand(6, -1, '/aksje/BRFE')"
        assert self._kjoer(f"o.fortsett({lagret}, '/aksje/BRFE', 21)") == {"i": 6, "retning": -1}
        assert self._kjoer(f"o.fortsett({lagret}, '/folg', 21)") is None
        assert self._kjoer(f"o.fortsett({lagret}, '/', 21)") is None

    def test_en_gammel_eller_oedelagt_tilstand_fortsetter_ikke(self):
        """ECH5, BH6: ville feilet hvis en indeks utenfor stegene, eller tekst
        som ikke kan leses, startet omvisningen."""
        assert self._kjoer("o.fortsett(o.tilstand(30, 1, '/'), '/', 21)") is None
        assert self._kjoer("o.fortsett('6', '/', 21)") is None
        assert self._kjoer("o.fortsett('{', '/', 21)") is None

    def test_retningen_tas_med_til_neste_side(self):
        """BH2, ECH3: ville feilet hvis «Tilbake» over en side fortsatte
        framover på den nye siden."""
        assert self._kjoer("o.fortsett(o.tilstand(5, -1, '/'), '/', 21).retning") == -1
        assert self._kjoer("o.fortsett(o.tilstand(5, 1, '/'), '/', 21).retning") == 1

    def test_tilbake_og_ferdig_foelger_stegene_som_finnes(self):
        """BH3, ECH4: ville feilet hvis «Tilbake» virket uten et steg før, eller
        «Neste» sto der det ikke er flere steg."""
        steg = self.STEG
        assert self._kjoer(f"o.knappene({steg}, 1, 'oversikt', (a) => a !== 'a')") == {
            "tilbake": False,
            "ferdig": False,
        }
        assert self._kjoer(f"o.knappene({steg}, 3, 'oversikt', () => true)") == {"tilbake": True, "ferdig": True}

    def test_esc_lukker_men_ikke_over_et_hjelpevindu(self):
        """Del B, BH9: ville feilet hvis Esc ikke lukket omvisningen, eller
        lukket den når et hjelpevindu var åpent."""
        assert self._kjoer("o.skalLukke('Escape', false)") is True
        assert self._kjoer("o.skalLukke('Escape', true)") is False
        assert self._kjoer("o.skalLukke('Enter', false)") is False

    def test_tilbudet_foerste_gang_og_et_nei(self):
        """Del C: ville feilet hvis tilbudet kom etter et svar, også et nei,
        eller på en annen side enn oversikten."""
        assert self._kjoer("o.skalTilby('oversikt', null)") is True
        assert self._kjoer("o.skalTilby('oversikt', 'nei')") is False
        assert self._kjoer("o.skalTilby('oversikt', 'ja')") is False
        assert self._kjoer("o.skalTilby('min_liste', null)") is False

    def test_skriptet_bruker_funksjonene(self):
        """Ville feilet hvis siden ikke brukte funksjonene testene kjører."""
        skriptet = SKRIPTET.read_text(encoding="utf-8")
        for bit in (
            "OMVISNING.fortsett(lagret, her(), steg.length)",
            "OMVISNING.knappene(steg, j, SIDE, finnes)",
            "OMVISNING.skalLukke(e.key,",
            "OMVISNING.skalTilby(SIDE,",
            'document.addEventListener("keydown", tast)',
            'window.addEventListener("pageshow"',
        ):
            assert bit in skriptet, bit
