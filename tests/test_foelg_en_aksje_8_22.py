"""Story 8.22, del C: «Følg en aksje» med alle som kan følges - NFR-06, AD-3, AD-10.

Spesifikasjonen er spec-8-22-foelg-en-aksje-og-min-liste.md, spørsmål 4-8, og
tillegg 3 (svarene 10.11 kl. 22:44): sorteringen i stedet for de tre forslagene.
Hver test lager sin egen base under tmp_path (regel 22), og ingen test gjør
nettkall (AD-8). Omsetningene er oppdiktet, ingen tall fra kildene (regel 16).
"""

import re
from datetime import date
from pathlib import Path

import ferdige_lister
from ferdige_lister import Foelgbar, filtrer, sorter
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


class TestLista:
    def test_alle_som_kan_foelges_med_antallet(self, klient, stier):  # noqa: F811
        """Ville feilet hvis lista bare viste søketreff, eller tok med en
        aksje uten bransje (MULTI). Tillegg 3: «Mest omsatt først» er valgt
        fra start, og de som ikke er målt, står sist etter navnet."""
        med_boersen(stier[1], [("MULTI", "Aaa Multi ASA")])
        maal(stier[1], [("NYD", 90e6), ("NYA", 10e6)])
        html = _side(klient)
        assert '<span id="antall-alle">4</span> aksjer på Oslo Børs kan følges.' in html
        assert _rader(html) == ["NYD", "NYA", "NYB", "NYC"]
        assert _rader(_side(klient, "/folg?sorter=navn")) == ["NYA", "NYB", "NYC", "NYD"]
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
        """Ville feilet hvis «Bytt ut» mistet byttet i en rad eller i
        filterskjemaet (gjennomgangen, VG10)."""
        maal(stier[1], [("NYA", 50e6)])
        html = _side(klient, "/folg?bytt=DNB&bransje=Kraft")
        assert '<a class="knapp" href="/folg?kode=NYA&amp;bytt=DNB" aria-label="Bytt inn Ny Aksje ASA">' in html
        skjema = html.split('<form class="folgfilter"', 1)[1].split("</form>", 1)[0]
        assert '<input type="hidden" name="bytt" value="DNB">' in skjema

    def test_hjelpen_ved_spoersmaalstegnet(self, klient):  # noqa: F811
        """Ville feilet hvis «?» manglet, eller hjelpen ikke sa at «Mest omsatt
        først» ikke er en rangering etter kursen (tillegg 3, NFR-06)."""
        html = _side(klient)
        assert 'popovertarget="hjelp-folg"' in html and '<div id="hjelp-folg" class="hjelpevindu" popover>' in html
        assert "ingen rangering etter kursen eller signalet" in html.split('<div id="hjelp-folg"', 1)[1]


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
        assert re.search(
            r'<input type="checkbox" name="bransje" value="Helse" checked> <svg class="bransjesymbol"', html
        )
        assert _rader(_side(klient, "/folg?bransje=Tull")) == ["NYA", "NYB", "NYC", "NYD"]

    def test_flere_bransjer_samtidig_og_med_omsetningen(self, klient, stier):  # noqa: F811
        """Tillegg 3: ville feilet hvis bare den siste bransjen i adressen
        gjaldt, hvis omsetningen ikke gjaldt i tillegg, eller hvis begge
        bransjene ikke var krysset av og sto i overskriften."""
        maal(stier[1], [("NYA", 50e6), ("NYB", 10e6), ("NYC", 40e6)])
        html = _side(klient, "/folg?bransje=Kraft&bransje=Helse&sorter=navn")
        assert _rader(html) == ["NYA", "NYB", "NYC", "NYD"]
        for b in ("Helse", "Kraft"):
            assert f'<input type="checkbox" name="bransje" value="{b}" checked>' in html
        assert '<h2 class="alle-tittel">Alle som kan følges i Helse og Kraft</h2>' in html
        assert _rader(_side(klient, "/folg?bransje=Kraft&bransje=Helse&omsetning=under")) == ["NYB"]
        assert _rader(_side(klient, "/folg?bransje=Helse&bransje=Tull")) == ["NYB"]

    def test_alle_tar_bort_bransjene_og_beholder_resten(self, klient):  # noqa: F811
        """Tillegg 3: ville feilet hvis «Alle» ikke var merket uten valgt
        bransje, var merket med en bransje valgt, eller mistet søket,
        omsetningen, sorteringen eller byttet."""
        html = _side(klient)
        assert '<a class="valgbrikke valgt" href="/folg" aria-current="true">Alle</a>' in html
        html = _side(klient, "/folg?q=ny&bransje=Kraft&omsetning=over&sorter=navn&bytt=DNB&bransje=Helse")
        assert (
            '<a class="valgbrikke" href="/folg?q=ny&amp;omsetning=over&amp;sorter=navn&amp;bytt=DNB">Alle</a>' in html
        )

    def test_det_valgte_er_oransje_med_et_merke(self):
        """Tillegg 3: ville feilet hvis det valgte ikke var oransje som
        bryterne i Innstillinger, var gult («skilte seg ut»), eller bare
        hadde fargen, uten hakemerket."""
        css = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")
        valgt = ":where(.side-oversikt) .valgbrikke:has(input:checked), :where(.side-oversikt) .valgbrikke.valgt {"
        regel = css.split(valgt, 1)[1].split("}", 1)[0]
        assert "background: var(--oransje)" in regel and "gul" not in regel
        assert '.innstillingsbryter[aria-checked="true"] .spor { background: var(--oransje); }' in css
        merke = css.split(".valgbrikke.valgt::before {", 1)[1].split("}", 1)[0]
        assert 'content: "✓"' in merke

    def test_maalt_omsetning(self, klient, stier):  # noqa: F811
        """Spørsmål 6: ville feilet hvis «Over 32 MNOK», «Under 32 MNOK» eller
        «Ikke målt ennå» viste feil aksjer. NYC er målt med feil, og regnes
        som ikke målt, som i Valglager.omsetning."""
        maal(stier[1], [("NYA", 50e6), ("NYB", 10e6), ("NYC", None)])
        assert _rader(_side(klient, "/folg?omsetning=over")) == ["NYA"]
        assert _rader(_side(klient, "/folg?omsetning=under")) == ["NYB"]
        assert _rader(_side(klient, "/folg?omsetning=ikke")) == ["NYC", "NYD"]


class TestSorteringen:
    """Tillegg 3 (svarene 10.11 kl. 22:44): kortet «Mest omsatt» er borte, og
    lista sorteres «Mest omsatt først», «A–Å» eller «Bransje»."""

    def test_de_tre_sorteringene(self, klient, stier):  # noqa: F811
        """Ville feilet hvis «Mest omsatt først» var ordnet etter noe annet
        enn omsetningen, eller satte en som ikke er målt, foran en målt, eller
        hvis «A–Å» eller «Bransje» ga en annen rekkefølge. Bransjene står i
        samme rekkefølge som filteret (Helse foran Kraft)."""
        maal(stier[1], [("NYA", 20e6), ("NYC", 80e6), ("NYB", 50e6)])
        assert _rader(_side(klient)) == ["NYC", "NYB", "NYA", "NYD"]
        assert _rader(_side(klient, "/folg?sorter=omsatt")) == ["NYC", "NYB", "NYA", "NYD"]
        assert _rader(_side(klient, "/folg?sorter=navn")) == ["NYA", "NYB", "NYC", "NYD"]
        assert _rader(_side(klient, "/folg?sorter=bransje")) == ["NYB", "NYA", "NYC", "NYD"]
        assert _rader(_side(klient, "/folg?sorter=tull")) == ["NYC", "NYB", "NYA", "NYD"]

    def test_valget_staar_i_skjemaet_med_filteret(self, klient):  # noqa: F811
        """Ville feilet hvis sorteringen ikke sto som brikker i samme skjema
        som filteret, så et filter mistet sorteringen, eller den valgte ikke
        var merket."""
        html = _side(klient, "/folg?sorter=bransje&bransje=Kraft")
        skjema = html.split('<form class="folgfilter"', 1)[1].split("</form>", 1)[0]
        sortering = skjema.split('<fieldset class="sorteringen">', 1)[1].split("</fieldset>", 1)[0]
        assert "<legend>Sorter</legend>" in sortering
        assert '<input type="radio" name="sorter" value="bransje" checked> Bransje</label>' in sortering
        assert '<input type="radio" name="sorter" value="omsatt"> Mest omsatt først</label>' in sortering
        assert '<input type="radio" name="sorter" value="navn"> A–Å</label>' in sortering

    def test_kortet_er_borte_og_ingen_rangering(self, klient, stier):  # noqa: F811
        """NFR-06: ville feilet hvis kortet «Mest omsatt» eller «høyst tre»
        sto igjen, hvis linja om at omsetningen ikke er kursen manglet ved
        «Mest omsatt først» eller sto ved en annen sortering, eller hvis siden
        brukte ord som «ukens beste» eller «anbefal»."""
        maal(stier[1], [("NYA", 50e6)])
        html = _side(klient)
        assert 'class="forslagene"' not in html and "høyst tre" not in html
        linja = "Ordnet etter median omsetning de 3 siste månedene, ikke etter kursen eller signalet."
        assert linja in html.split('<p class="antall-vist">', 1)[1].split("</p>", 1)[0]
        assert linja not in _side(klient, "/folg?sorter=navn")
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
        assert filtrer(rader, "CÆS", (), "") == [self.C]
        assert filtrer(rader, "", ("Kraft",), "under") == [self.B]
        assert filtrer(rader, "", (), "ikke") == [self.C]
        assert filtrer(rader, " ", (), "") == rader
        # Gjennomgangen (BH5, ECH7): ticker og navn hver for seg, som skriptet.
        assert filtrer(rader, "a al", (), "") == []
        # Tillegg 3: flere bransjer samtidig, og omsetningen i tillegg.
        assert filtrer(rader, "", ("Kraft", "Helse"), "") == rader
        assert filtrer(rader, "", ("Helse", "Kraft"), "over") == [self.A]

    def test_grensen_er_32_mnok_som_merket(self):
        """Gjennomgangen (BH6, VG7): ville feilet hvis en aksje på nøyaktig 32
        MNOK sto under «Over» med merket, eller filteret og merket regnet
        grensen ulikt."""
        paa = Foelgbar("PP", "På grensen", "Kraft", 32e6, date(2026, 10, 22), False)
        under = Foelgbar("UU", "Under", "Kraft", 32e6 - 1, date(2026, 10, 22), False)
        assert filtrer([paa, under], "", (), "over") == [paa] and not paa.utenfor
        assert filtrer([paa, under], "", (), "under") == [under] and under.utenfor

    def test_norsk_alfabet(self):
        """Gjennomgangen (ECH8): ville feilet hvis Å sto foran Æ og Ø, eller
        Æ, Ø og Å foran Z."""
        from ferdige_lister import _norsk

        assert sorted(["Å", "Ø", "Z", "Æ", "A"], key=_norsk) == ["A", "Z", "Æ", "Ø", "Å"]

    def test_sorter(self):
        """Tillegg 3: ville feilet hvis en som ikke er målt, sto foran en
        målt i «Mest omsatt først», eller hvis like omsetninger ikke ble
        ordnet etter navnet."""
        lik = Foelgbar("DD", "Delta", "Kraft", 50e6, date(2026, 10, 22), False)
        assert sorter([self.C, self.B, lik, self.A], "omsatt") == [self.A, lik, self.B, self.C]
        assert sorter([self.C, self.B, self.A], "navn") == [self.A, self.B, self.C]
        assert sorter([self.A, self.B, self.C], "bransje") == [self.C, self.A, self.B]


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

    def test_lista_filtrene_og_sorteringen_i_demoen(self, tmp_path, monkeypatch):
        """Ville feilet hvis demoen hadde for få oppdiktede selskaper til at
        antallet, filtrene, sorteringen og «ikke målt ennå» kunne ses, eller
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
        assert _rader(kraft) == ["HVLK", "BRKR", "STRM", "LYSV"]
        assert _rader(_side(k, "/folg?bransje=Kraft&sorter=navn")) == ["BRKR", "HVLK", "LYSV", "STRM"]
        assert _rader(_side(k, "/folg?omsetning=under")) == ["STRM", "NRDE"]
        assert set(_rader(_side(k, "/folg?omsetning=ikke"))) == {"LYSV", "SKRH", "TNDT", "VKVF"}
        assert _rader(_side(k, "/folg?q=fjord")) == ["FJHE"]

    def test_bare_oppdiktede_selskaper_i_demoen(self, tmp_path, monkeypatch):
        """Ville feilet hvis en ekte ticker fra BRANSJE, eller navnet på en av
        de 15 ekte aksjene, sto i «Følg en aksje», de ferdige
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
