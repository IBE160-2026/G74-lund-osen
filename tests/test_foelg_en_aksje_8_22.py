"""Story 8.22, del C: «Følg en aksje» med alle som kan følges - NFR-06, AD-3, AD-10.

Spesifikasjonen er spec-8-22-foelg-en-aksje-og-min-liste.md, spørsmål 4-8.
Hver test lager sin egen base under tmp_path (regel 22), og ingen test gjør
nettkall (AD-8). Omsetningene er oppdiktet, ingen tall fra kildene (regel 16).
"""

import re
from datetime import date
from pathlib import Path

import ferdige_lister
from ferdige_lister import Foelgbar, filtrer, forslagene
from test_ferdige_lister import maal
from test_valg import faste_bransjer, klient, lager, med_boersen, stier  # noqa: F401  (fiksturene)

ROT = Path(__file__).resolve().parent.parent


def _side(klient, adresse="/folg"):  # noqa: F811
    return klient.get(adresse).data.decode("utf-8")


def _rader(html: str, synlige: bool = True) -> list[str]:
    """Tickerne i hele lista (id foelgbare), i rekkefølgen de står."""
    lista = html.split('<ul class="foelgbare" id="foelgbare">', 1)[1].split("</ul>", 1)[0]
    ut = []
    for li in re.findall(r"<li class=\"foelgbar\"[^>]*>.*?</li>", lista, re.S):
        if synlige and " hidden>" in li.split("\n", 1)[0]:
            continue
        ut.append(re.search(r'href="/folg\?kode=([A-Z0-9]+)', li).group(1))
    return ut


def _forslagene(html: str) -> list[str]:
    """Tickerne i forslagskortet som vises. Gjennomgangen (BH10): et skjult
    forslag telles ikke."""
    del_ = html.split('<section class="forslagene"', 1)[1].split("</section>", 1)[0]
    return [
        re.search(r'href="/folg\?kode=([A-Z0-9]+)', li).group(1)
        for li in re.findall(r"<li class=\"foelgbar\"[^>]*>.*?</li>", del_, re.S)
        if " hidden>" not in li.split("\n", 1)[0]
    ]


class TestLista:
    def test_alle_som_kan_foelges_med_antallet_ordnet_etter_navnet(self, klient, stier):  # noqa: F811
        """Ville feilet hvis lista bare viste søketreff, tok med en aksje uten
        bransje (MULTI), eller var ordnet etter omsetningen i stedet for
        navnet (spørsmål 5, NFR-06)."""
        med_boersen(stier[1], [("MULTI", "Aaa Multi ASA")])
        maal(stier[1], [("NYD", 90e6), ("NYA", 10e6)])
        html = _side(klient)
        assert '<span id="antall-alle">4</span> aksjer på Oslo Børs kan følges.' in html
        assert _rader(html) == ["NYA", "NYB", "NYC", "NYD"]
        assert "MULTI" not in html.split("<main>", 1)[1]

    def test_en_aksje_i_lista_eller_som_venter_staar_ikke(self, klient, stier):  # noqa: F811
        """Ville feilet hvis en aksje som alt følges eller venter, kunne
        følges igjen fra lista."""
        l = lager(stier[1])
        l.folg("NYB", "Helse")
        l._t.close()
        html = _side(klient)
        assert _rader(html) == ["NYA", "NYC", "NYD"] and "EQNR" not in _rader(html)

    def test_foelg_paa_hver_rad_og_ikke_maalt_enna(self, klient, stier):  # noqa: F811
        """Spørsmål 4: ville feilet hvis en rad manglet «Følg», knappen ikke
        gikk til «Følge …?», eller en aksje uten måling ikke var merket
        «ikke målt ennå»."""
        maal(stier[1], [("NYA", 50e6), ("NYB", 10e6)])
        html = _side(klient)
        rad_c = html.split('data-kode="nyc" data-navn="ny c asa"', 1)[1].split("</li>", 1)[0]
        assert "ikke målt ennå" in rad_c and '<a class="knapp" href="/folg?kode=NYC"' in rad_c
        assert ">Følg</a>" in rad_c
        rad_a = html.split('data-kode="nya" data-navn="ny aksje asa"', 1)[1].split("</li>", 1)[0]
        assert "ca. 50,0 MNOK om dagen, målt 22.10</span>" in rad_a and "Utenfor målingen" not in rad_a
        rad_b = html.split('data-kode="nyb" data-navn="ny b asa"', 1)[1].split("</li>", 1)[0]
        assert "Utenfor målingen" in rad_b and "</svg>Helse</span>" in rad_b

    def test_bytt_ut_bruker_den_samme_lista(self, klient, stier):  # noqa: F811
        """Ville feilet hvis «Bytt ut» mistet byttet i en rad, i forslagene
        eller i filterskjemaet (gjennomgangen, VG10)."""
        maal(stier[1], [("NYA", 50e6)])
        html = _side(klient, "/folg?bytt=DNB&bransje=Kraft")
        assert '<a class="knapp" href="/folg?kode=NYA&amp;bytt=DNB" aria-label="Bytt inn Ny Aksje ASA">' in html
        forslag = html.split('<section class="forslagene"', 1)[1].split("</section>", 1)[0]
        assert 'href="/folg?kode=NYA&amp;bytt=DNB"' in forslag
        skjema = html.split('<form class="folgfilter"', 1)[1].split("</form>", 1)[0]
        assert '<input type="hidden" name="bytt" value="DNB">' in skjema

    def test_hjelpen_ved_spoersmaalstegnet(self, klient):  # noqa: F811
        """Ville feilet hvis «?» manglet, eller hjelpen ikke sa at forslagene
        aldri er ordnet etter kursen eller signalet."""
        html = _side(klient)
        assert 'popovertarget="hjelp-folg"' in html and '<div id="hjelp-folg" class="hjelpevindu" popover>' in html
        assert "aldri etter kursen eller signalet" in html.split('<div id="hjelp-folg"', 1)[1]


class TestFilteret:
    def test_soeket_uten_skript(self, klient):  # noqa: F811
        """Spørsmål 8: ville feilet hvis knappen «Vis» ikke filtrerte på
        serveren, så siden uten skript viste alle."""
        html = _side(klient, "/folg?q=ny+b")
        assert _rader(html) == ["NYB"] and _rader(html, synlige=False) == ["NYA", "NYB", "NYC", "NYD"]
        assert '<span id="antall-vist">1</span> av 4 vises.' in html
        assert 'id="ingen-treff" hidden' in html
        html = _side(klient, "/folg?q=zzz")
        assert _rader(html) == [] and 'id="ingen-treff">' in html

    def test_bransjen_med_symbolet(self, klient):  # noqa: F811
        """Ville feilet hvis filteret på bransje manglet, var uten symbol,
        eller et ukjent valg i adressen ga en tom liste."""
        html = _side(klient, "/folg?bransje=Helse")
        assert _rader(html) == ["NYB"]
        assert re.search(r'<input type="radio" name="bransje" value="Helse" checked> <svg class="bransjesymbol"', html)
        assert _rader(_side(klient, "/folg?bransje=Tull")) == ["NYA", "NYB", "NYC", "NYD"]

    def test_maalt_omsetning(self, klient, stier):  # noqa: F811
        """Spørsmål 6: ville feilet hvis «Over 32 MNOK», «Under 32 MNOK» eller
        «Ikke målt ennå» viste feil aksjer. NYC er målt med feil, og regnes
        som ikke målt, som i Valglager.omsetning."""
        maal(stier[1], [("NYA", 50e6), ("NYB", 10e6), ("NYC", None)])
        assert _rader(_side(klient, "/folg?omsetning=over")) == ["NYA"]
        assert _rader(_side(klient, "/folg?omsetning=under")) == ["NYB"]
        assert _rader(_side(klient, "/folg?omsetning=ikke")) == ["NYC", "NYD"]

    def test_forslagene_skjules_ikke_av_soeket_eller_omsetningen(self, klient, stier):  # noqa: F811
        """Gjennomgangen (BH1, ECH1, VG7): ville feilet hvis forslagene i valgt
        bransje ble skjult av et søk eller et filter på omsetning, så kortet
        sto med overskriften og uten aksjer."""
        maal(stier[1], [("NYA", 50e6), ("NYC", 40e6), ("NYD", 20e6)])
        for adresse in (
            "/folg?bransje=Kraft&q=zzz",
            "/folg?bransje=Kraft&omsetning=ikke",
            "/folg?bransje=Kraft&omsetning=under",
        ):
            assert _forslagene(_side(klient, adresse)) == ["NYA", "NYC", "NYD"], adresse


class TestForslagene:
    def test_de_tre_mest_omsatte_i_valgt_bransje_utenfor_lista(self, klient, stier):  # noqa: F811
        """Spørsmål 7: ville feilet hvis forslagene var ordnet etter noe annet
        enn omsetningen, tok med en aksje i en annen bransje eller en som
        venter, eller var flere enn tre."""
        med_boersen(stier[1], [("NYE", "Ny E ASA"), ("NYF", "Ny F ASA")])
        for kode in ("NYE", "NYF"):
            ferdige_lister.BRANSJE[kode] = "Kraft"
        try:
            maal(stier[1], [("NYA", 20e6), ("NYC", 80e6), ("NYD", 40e6), ("NYE", 60e6), ("NYF", 90e6), ("NYB", 99e6)])
            l = lager(stier[1])
            l.folg("NYF", "Kraft")
            l._t.close()
            html = _side(klient, "/folg?bransje=Kraft")
            assert _forslagene(html) == ["NYC", "NYE", "NYD"]
            assert "Mest omsatt i " in html and "ikke etter kursen eller signalet" in html
        finally:
            for kode in ("NYE", "NYF"):
                ferdige_lister.BRANSJE.pop(kode, None)

    def test_ingen_forslag_uten_bransje_og_aldri_ukens_beste(self, klient, stier):  # noqa: F811
        """NFR-06: ville feilet hvis siden foreslo aksjer uten valgt bransje,
        eller brukte ord som «ukens beste» eller «anbefal»."""
        maal(stier[1], [("NYA", 50e6)])
        html = _side(klient)
        assert _forslagene(html) == []
        assert "Velg en bransje, så står de mest omsatte du ikke følger, her, høyst tre." in html
        for ord_ in ("ukens beste", "anbefal", "beste aksje", "vinner"):
            assert ord_ not in html.lower()


class TestFunksjonene:
    A = Foelgbar("AA", "Alfa", "Kraft", 50e6, date(2026, 10, 22), False)
    B = Foelgbar("BB", "Beta", "Kraft", 10e6, date(2026, 10, 22), False)
    C = Foelgbar("CC", "Cæsar", "Helse", None, None, False)

    def test_filtrer(self):
        """Ville feilet hvis søket skilte på store og små bokstaver, eller
        filtrene ga noe annet enn de fire valgene sier."""
        rader = [self.A, self.B, self.C]
        assert filtrer(rader, "CÆS", "", "") == [self.C]
        assert filtrer(rader, "", "Kraft", "under") == [self.B]
        assert filtrer(rader, "", "", "ikke") == [self.C]
        assert filtrer(rader, " ", "", "") == rader
        # Gjennomgangen (BH5, ECH7): ticker og navn hver for seg, som skriptet.
        assert filtrer(rader, "a al", "", "") == []

    def test_grensen_er_32_mnok_som_merket(self):
        """Gjennomgangen (BH6, VG7): ville feilet hvis en aksje på nøyaktig 32
        MNOK sto under «Over» med merket, eller filteret og merket regnet
        grensen ulikt."""
        paa = Foelgbar("PP", "På grensen", "Kraft", 32e6, date(2026, 10, 22), False)
        under = Foelgbar("UU", "Under", "Kraft", 32e6 - 1, date(2026, 10, 22), False)
        assert filtrer([paa, under], "", "", "over") == [paa] and not paa.utenfor
        assert filtrer([paa, under], "", "", "under") == [under] and under.utenfor

    def test_norsk_alfabet(self):
        """Gjennomgangen (ECH8): ville feilet hvis Å sto foran Æ og Ø, eller
        Æ, Ø og Å foran Z."""
        from ferdige_lister import _norsk

        assert sorted(["Å", "Ø", "Z", "Æ", "A"], key=_norsk) == ["A", "Z", "Æ", "Ø", "Å"]

    def test_forslagene_uten_bransje_er_ingen(self):
        """Spørsmål 7: ville feilet hvis det var forslag uten valgt bransje,
        eller en aksje uten måling ble foreslått (VG10)."""
        assert forslagene([self.A, self.B, self.C], "") == []
        assert forslagene([self.A, self.B, self.C], "Kraft") == [self.A, self.B]


def test_skriptet_filtrerer_paa_det_samme_som_serveren():
    """Spørsmål 8: ville feilet hvis skriptet lette i noe annet enn data-kode
    og data-navn hver for seg (små bokstaver, som serveren lager), ikke
    filtrerte mens man skriver, ikke skjulte radene, eller sendte skjemaet
    ved et piltrykk (gjennomgangen, BH4, ECH2, VG1). Det kjøres ikke i en
    nettleser i testene; bildene er tatt med skriptet i Edge."""
    js = (ROT / "src" / "static" / "hjelp.js").read_text(encoding="utf-8")
    del_ = js.split("Story 8.22", 1)[1]
    assert 'querySelector("input[data-folgsok]")' in del_
    assert "rad.dataset.kode.includes(tekst) || rad.dataset.navn.includes(tekst)" in del_
    assert 'felt.addEventListener("input", filtrer)' in del_ and "rad.hidden = !med" in del_
    assert "toLowerCase()" in del_ and 'getElementById("antall-vist")' in del_
    assert 'addEventListener("pointerdown"' in del_ and "if (klikk) felt.form.submit()" in del_
    assert 'addEventListener("keydown"' in del_ and "requestSubmit" not in del_
    mal = (ROT / "src" / "templates" / "folg.html").read_text(encoding="utf-8")
    assert 'data-kode="{{ a.kode|lower }}" data-navn="{{ a.navn|lower }}"' in mal and "data-folgsok" in mal


class TestDemoen:
    """Tillegget 10.11 kl. 17:16 (svaret kl. 15:57): alt nytt kan ses i
    demoen uten nøkkel, bare med oppdiktede selskaper merket «Eksempeltall»."""

    @staticmethod
    def _klient(tmp_path, monkeypatch):
        import shutil
        from datetime import datetime

        import app as app_modul
        import demo
        from lagring_sqlite import demo_sti

        mal = tmp_path / "demo.db"
        demo.lag_demobase(mal, skriv=lambda _: None)
        sti = demo_sti()
        sti.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(mal, sti)
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 10, 13, 12, 0).astimezone())
        return app_modul.app.test_client()

    def test_lista_filtrene_og_forslagene_i_demoen(self, tmp_path, monkeypatch):
        """Ville feilet hvis demoen hadde for få oppdiktede selskaper til at
        antallet, filtrene, forslagene og «ikke målt ennå» kunne ses, eller
        siden manglet merket «Eksempeltall»."""
        import demo

        k = self._klient(tmp_path, monkeypatch)
        html = _side(k)
        alle = _rader(html)
        assert len(alle) == len(demo.DEMOBOERSEN) == 12
        assert f'<span id="antall-alle">{len(alle)}</span> aksjer på Demo Børs kan følges.' in html
        assert 'class="eksempeltall"' in html and "Eksempeltall: oppdiktede selskaper" in html
        assert "ikke målt ennå" in html
        kraft = _side(k, "/folg?bransje=Kraft")
        assert _forslagene(kraft) == ["HVLK", "BRKR", "STRM"]
        assert _rader(kraft) == ["BRKR", "HVLK", "LYSV", "STRM"]
        assert _rader(_side(k, "/folg?omsetning=under")) == ["NRDE", "STRM"]
        assert set(_rader(_side(k, "/folg?omsetning=ikke"))) == {"LYSV", "SKRH", "TNDT", "VKVF"}
        assert _rader(_side(k, "/folg?q=fjord")) == ["FJHE"]

    def test_bare_oppdiktede_selskaper_i_demoen(self, tmp_path, monkeypatch):
        """Ville feilet hvis en ekte ticker fra BRANSJE, eller navnet på en av
        de 15 ekte aksjene, sto i «Følg en aksje», forslagene, de ferdige
        listene eller «Dine egne aksjer» i demoen (gjennomgangen, VG3)."""
        import demo
        from kursdata import AKSJEUNIVERS

        oppdiktet = {s for s, _ in demo.DEMOBOERSEN} | {a.symbol for a in demo.DEMOUNIVERS}
        ekte = set(ferdige_lister.BRANSJE) - oppdiktet
        k = self._klient(tmp_path, monkeypatch)
        sidene = ("/folg", "/folg?bransje=Kraft", "/folg?omsetning=ikke", "/folg?kode=HVLK", "/min-liste", "/")
        for adresse in sidene:
            html = k.get(adresse).data.decode("utf-8").split("<main>", 1)[1]
            for aksje in AKSJEUNIVERS:
                assert aksje.navn not in html, (adresse, aksje.symbol)
            # Bekreftelsen har koden i det skjulte feltet, ikke i en lenke.
            koder = (
                set(re.findall(r"kode=([A-Z0-9]+)", html))
                | set(re.findall(r'<span class="linje">([A-Z0-9]+)', html))
                | set(re.findall(r'name="kode" value="([A-Z0-9]+)"', html))
            )
            assert koder and koder <= oppdiktet and not koder & ekte, adresse
            if "kode=" in adresse:
                assert "Aksje på Demo Børs · HVLK · " in html and "Oslo Børs" not in html, adresse
