"""Story 8.23: funnene fra brukertesten 10.11 (del A), med tilleggene 1–3 og
tillegget om demoen. Spesifikasjonen er spec-8-23-funnene-fra-brukertesten.md.

Testene bruker demobasen, laget i tmp_path, som test_funnene_8_2b.py, og alt
skal kunne ses i demoen (tillegget om demoen, gruppens svar kl. 15:57).
"""

import re
import shutil
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

import app as app_modul
import demo
import historikk
import valg
from boersometer import stoerrelse, vis_volumforhold
from dagene import Dagsbilde, setning_om_samme_dag
from historikk import AlleSjekkene, alle_sjekkene_det_siste_aaret
from lagring_sqlite import demo_sti
from vurderingsdata import Grunn

ROT = Path(__file__).resolve().parent.parent
STIL = (ROT / "src" / "static" / "stil.css").read_text(encoding="utf-8")


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


def _html(klient, sti: str) -> str:
    svar = klient.get(sti)
    assert svar.status_code == 200, sti
    return svar.get_data(as_text=True)


def _merk(klient, symbol, til, tilbake):
    return klient.post("/min-liste/merk", data={"symbol": symbol, "til": til, "tilbake": tilbake})


def _radene(html: str) -> list[str]:
    """Symbolene i tabellen, i rekkefølgen de står."""
    tabell = html.split('id="aksjene"', 1)[1].split("</table>", 1)[0]
    return re.findall(r'<form id="rad-([A-Z]+)"', tabell)


def _thead(html: str) -> str:
    return html.split("<thead>", 1)[1].split("</thead>", 1)[0]


class TestSorteringenBlirVedTabellen:
    """A2: sorteringen ved klikk i kolonneraden blir stående ved tabellen."""

    @pytest.mark.parametrize("sti", ["/", "/min-liste", "/min-liste?vis=alle", "/?vis=min"])
    def test_lenkene_i_kolonneraden_gaar_til_tabellen(self, klient, sti):
        """Ville feilet hvis en lenke i kolonneraden gikk til toppen av siden,
        så man måtte rulle ned til tabellen igjen etter hvert klikk."""
        lenker = re.findall(r'<a class="sorter[^"]*" href="([^"]+)"', _thead(_html(klient, sti)))
        assert len(lenker) == 5
        assert all(lenke.endswith("#aksjene") for lenke in lenker), lenker

    def test_standard_rekkefoelge_og_filteret_gaar_til_tabellen(self, klient):
        """Ville feilet hvis «Standard rekkefølge» eller knappene i filteret
        sendte til toppen."""
        html = _html(klient, "/min-liste?sorter=kurs&orden=synkende")
        assert '<a href="/min-liste#aksjene">Standard rekkefølge</a>' in html
        nav = html.split('<nav class="signalfilter"', 1)[1].split("</nav>", 1)[0]
        assert all(h.endswith("#aksjene") for h in re.findall(r'href="([^"]+)"', nav))


class TestFilteretMedAntallet:
    """A8: antallet står på knappene, og ved 0 står hvor mange som fikk 2 av 3
    i samme retning, med en lenke."""

    @pytest.mark.parametrize("sti", ["/", "/min-liste"])
    @pytest.mark.parametrize("retning", ["positiv", "negativ"])
    def test_antallet_paa_knappen_er_radene_filteret_gir(self, klient, sti, retning):
        """Ville feilet hvis antallet på knappen var et annet enn radene man
        får ved å trykke på den, eller talte aksjer utenfor lista som vises."""
        html = _html(klient, sti)
        nav = html.split('<nav class="signalfilter"', 1)[1].split("</nav>", 1)[0]
        antall = int(re.search(rf"3 av 3 {retning} \((\d+)\)", nav).group(1))
        filtrert = _html(klient, f"{sti}?signal={retning}")
        assert len(_radene(filtrert)) == antall

    def test_ved_0_staar_2_av_3_med_lenke(self, klient):
        """Ville feilet hvis et tomt filter bare sa «Ingen», eller lenken viste
        andre enn dem som fikk 2 av 3 i samme retning."""
        # I Min liste i demoen fikk bare BRFE 3 av 3 negativ, og NLYS 2 av 3
        # negativ (gjennomgangen, BH7, VG5: ingen tidlig retur).
        _merk(klient, "BRFE", "fjern", "/min-liste")
        html = _html(klient, "/min-liste?signal=negativ&sorter=kurs&orden=synkende")
        tekst = html.split('<p class="filtertekst">', 1)[1].split("</p>", 1)[0]
        assert "Ingen av aksjene her fikk det." in tekst
        treff = re.search(r'(\d+) fikk 2 av 3 negativ: <a href="([^"]+)">se (?:den|dem)</a>', tekst)
        assert treff, tekst
        antall, adresse = int(treff.group(1)), treff.group(2).replace("&amp;", "&")
        assert (
            "signal=negativ-2" in adresse and "sorter=kurs&orden=synkende" in adresse and adresse.endswith("#aksjene")
        )
        neste = _html(klient, adresse.removesuffix("#aksjene"))
        assert _radene(neste) == ["NLYS"] and antall == 1
        assert "Bare aksjene som fikk 2 av 3 med retning negativ." in neste

    def test_antallet_med_min_liste_paa_oversikten(self, klient):
        """Gjennomgangen (VG5): ville feilet hvis antallet på oversikten med
        «Min liste» talte alle aksjene, ikke de som vises."""
        html = _html(klient, "/?vis=min")
        nav = html.split('<nav class="signalfilter"', 1)[1].split("</nav>", 1)[0]
        for retning in ("positiv", "negativ"):
            antall = int(re.search(rf"3 av 3 {retning} \((\d+)\)", nav).group(1))
            assert len(_radene(_html(klient, f"/?vis=min&signal={retning}"))) == antall

    def test_ingen_tekst_om_2_av_3_naar_filteret_gir_noe(self, klient):
        """Ville feilet hvis lenken til 2 av 3 sto også når 3 av 3 ga rader."""
        html = _html(klient, "/?signal=positiv")
        assert _radene(html)
        assert "fikk 2 av 3" not in html.split('<p class="filtertekst">', 1)[1].split("</p>", 1)[0]


class TestOverskriftenIMinListe:
    """Tillegg 1 (gruppens funn kl. 14:15): overskriften stemmer med tabellen."""

    def test_med_alle_staar_begge_tallene(self, klient):
        """Ville feilet hvis overskriften med «Alle» bare talte Min liste, mens
        tabellen viser alle. BRFE skilte seg ut og er i lista i demoen."""
        assert '<h1 class="overskrift"><mark>7 av 15</mark> skilte seg ut fredag, 3 av dem i Min liste</h1>' in _html(
            klient, "/min-liste?vis=alle"
        )
        _merk(klient, "BRFE", "fjern", "/min-liste?vis=alle")
        assert "<mark>7 av 15</mark> skilte seg ut fredag, 2 av dem i Min liste" in _html(klient, "/min-liste?vis=alle")

    def test_med_min_liste_som_foer(self, klient):
        """Ville feilet hvis overskriften med «Min liste» ble endret."""
        assert '<h1 class="overskrift"><mark>3 av 5 i Min liste</mark> skilte seg ut fredag</h1>' in _html(
            klient, "/min-liste"
        )


class TestMinListePaaOversikten:
    """Tillegg 2 (B7): «Min liste» over «Aksjene» filtrerer tabellen på
    oversikten og beholder perioden og sorteringen."""

    def test_bare_de_merkede_paa_oversikten(self, klient):
        """Ville feilet hvis valget sendte til siden Min liste, eller viste
        andre enn de merkede."""
        html = _html(klient, "/?vis=min")
        assert set(_radene(html)) == set(demo.MERKET_I_DEMOEN)
        assert '<div class="aksjetopp">' in html and '<section class="hovedindeks"' in html
        topp = html.split('<div class="aksjetopp">', 1)[1].split("</nav>", 1)[0]
        assert re.search(r'href="/\?vis=min#aksjene" aria-current="true">Min liste', topp)

    def test_beholder_perioden_og_sorteringen(self, klient):
        """Ville feilet hvis sorteringen, perioden eller «Standard rekkefølge»
        mistet valget."""
        html = _html(klient, "/?vis=min&periode=1-uke&sorter=kurs&orden=stigende")
        assert set(_radene(html)) == set(demo.MERKET_I_DEMOEN)
        lenker = re.findall(r'<a class="sorter[^"]*" href="([^"]+)"', _thead(html))
        assert all("vis=min" in h and "periode=1-uke" in h for h in lenker), lenker
        assert '<a href="/?vis=min&amp;periode=1-uke#aksjene">Standard rekkefølge</a>' in html
        assert '<input type="hidden" name="vis" value="min">' in html

    def test_stjernen_sender_tilbake_til_valget(self, klient):
        """Ville feilet hvis stjernen tok valget bort, eller sendte til en rad
        som ikke står der lenger."""
        svar = _merk(klient, "BRFE", "fjern", "/?vis=min&sorter=kurs&orden=stigende")
        assert svar.status_code == 303
        assert svar.headers["Location"].endswith("/?vis=min&sorter=kurs&orden=stigende#aksjene")

    def test_knappen_i_stripa_gaar_til_siden(self, klient):
        """Ville feilet hvis knappen «Min liste» i stripa ble et filter."""
        stripa = _html(klient, "/").split('<nav class="rad sider"', 1)[1].split("</nav>", 1)[0]
        assert 'href="/min-liste"' in stripa


def _regel(velger: str) -> str:
    treff = re.search(r"(?:^|\n)\s*(?::where\(\.side-[a-z]+\) )?" + re.escape(velger) + r"\s*\{([^}]*)\}", STIL)
    assert treff, f"ingen regel for {velger}"
    return treff.group(1)


def _demobasen():
    return sqlite3.connect(demo_sti())


class TestDineEgneAksjer:
    """A1: «Dine egne aksjer» har samme utseende som radene i tabellen, med
    et lite bransjeikon."""

    def test_radene_er_en_tabell_som_tabellen_over(self, klient):
        """Ville feilet hvis radene var en liste med en annen stil enn
        tabellen, eller bransjeikonet manglet. I demoen følges BRFE som egen."""
        with _demobasen() as t:
            t.execute(
                "INSERT INTO oenske (handling, symbol, navn, sektor, laget) VALUES "
                "('folg', 'XTEST', 'Eksempelselskap', 'Energi', '2026-10-13T12:00:00+00:00')"
            )
        html = _html(klient, "/")
        egne = html.split('id="dine-egne-aksjer"', 1)[1].split("</section>", 1)[0]
        assert '<div class="tabellboks egnetabell"' in egne and "<thead>" in egne
        rad = egne.split('<tr class="egen-rad">', 1)[1].split("</tr>", 1)[0]
        assert '<td class="bransje"><svg class="bransjesymbol"' in rad and "Energi" in rad
        assert "Venter på henting i kveld etter kl. 22." in rad and "Angre" in rad


class TestBoersometeret:
    """A4 og A5 med tillegg 3."""

    def test_alle_rutene_har_symbolet_endringen_og_styrken_i_lappen(self, klient):
        """Ville feilet hvis en liten rute ikke viste endringen og styrken
        noe sted, også de minste, som bare viser fargen."""
        html = _html(klient, "/boersometer")
        ruter = re.findall(r'<a class="rute [^"]*" href="[^"]+" title="([^"]+)">', html)
        assert len(ruter) == 15
        assert all(re.fullmatch(r"[A-Z]+: ([+-]?[\d,]+\xa0%|uten data|–)(, .+)?", r) for r in ruter), ruter
        assert any(re.search(r", \d av 3$", r) for r in ruter)

    def test_smaa_ruter_viser_endringen_og_styrken(self):
        """Ville feilet hvis nivå 1 skjulte endringen, som før brukertesten.
        Gjennomgangen (BH3, ECH3): styrken står i lappen der den ikke får
        plass, og på nivå 2 skjules den uten styrke-N, som svaret 04.11 sa."""
        for b in ("bredest", "bred", "smal", "smalest"):
            skjult = STIL.split(f".rute.nivaa-{b}-0 > .ticker", 1)[1].split("{", 1)[0]
            assert f"nivaa-{b}-1 > .endring" not in skjult and f"nivaa-{b}-1 > .styrke" in skjult, b
            assert f"nivaa-{b}-2:not(.styrke-{b}) > .styrke" in skjult, b
            vis = STIL.split(f".rute.nivaa-{b}-1 > .endring {{", 1)[1].split("}", 1)[0]
            assert "font-size: 11px" in vis and "display: block" in vis, b

    def test_forklaringen_sier_hva_ring_og_ramme_er(self, klient):
        """Ville feilet hvis «Rammen» ikke sa hva ringen og den tykke rammen
        betyr."""
        html = _html(klient, "/boersometer")
        rammen = html.split("<strong>Rammen</strong>", 1)[1].split("</li>", 1)[0]
        assert "tykke rammen rundt ruta" in rammen and "Ringen rundt styrken" in rammen

    @pytest.mark.parametrize(
        ("forhold", "vist"),
        [
            (1.4996, "1,50"),
            (1.0004, "1,00"),
            (1.5004, "1,51"),
            (0.998, "0,99"),
            (1.0, "1,00"),
            (1.5, "1,50"),
            (2.345, "2,35"),
            (0.5, "0,50"),
        ],
    )
    def test_volum_mot_vanlig_med_to_desimaler(self, forhold, vist):
        """Ville feilet med flere enn to desimaler, eller hvis et tall like ved
        en grense ble rundet over den, så tallet og ordet sa ulikt."""
        tekst = vis_volumforhold(forhold)
        assert tekst == vist
        tilbake = float(tekst.replace(",", "."))
        # Gjennomgangen (BH7, BH11, ECH5): ordet for tallet som vises, er ordet for målingen.
        assert stoerrelse(tilbake) == stoerrelse(forhold)

    def test_tabellen_er_aapen_og_har_hjelp_ved_kolonnene(self, klient):
        """Tillegg 3: ville feilet hvis tabellen var lukket fra start, eller
        «?» manglet ved «Endring» og «Volum mot vanlig»."""
        html = _html(klient, "/boersometer")
        assert '<details class="tallene" open>' in html
        thead = html.split('<table class="boersometertabell">', 1)[1].split("</thead>", 1)[0]
        assert 'popovertarget="hjelp-tabell-endring"' in thead and 'popovertarget="hjelp-tabell-volum"' in thead
        vindu = html.split('id="hjelp-tabell-volum"', 1)[1][:3000]
        assert "Lavt er under 1, vanlig fra 1 til og med 1,5, og høyt over 1,5" in vindu
        endring = html.split('id="hjelp-tabell-endring"', 1)[1][:3000]
        assert "gjennomsnittet av endringen for aksjene i bransjen som har kurs, uten vekt" in endring

    def test_knappen_ser_ut_som_en_knapp(self):
        """Ville feilet hvis «Se tallene som tabell» sto som vanlig tekst."""
        regler = STIL.split("details.tallene > summary {")[1].split("}", 1)[0]
        assert "border-radius: 999px" in regler and "min-height: 44px" in regler


class TestOransje:
    """A6: bryterne er oransje når de er på, og siden man er på er oransje i toppen."""

    @pytest.mark.parametrize(
        "velger",
        [
            '.innstillingsbryter[aria-checked="true"] .spor',
        ],
    )
    def test_bryterne(self, velger):
        """Ville feilet hvis en bryter i Innstillinger som er på, var svart som før."""
        assert "background: var(--oransje)" in _regel(velger)

    def test_bryteren_ved_ki_teksten_er_i_blekk(self):
        """Hele settet, del 3: ville feilet hvis bryterne ved KI-teksten og ved
        «Børsdagen kort fortalt» ble oransje, mot spørsmål 5 i 8.2b (blekk)."""
        for velger in ('.dagsbryter [aria-checked="true"] .spor', '.ki-bryter [aria-checked="true"] .spor'):
            assert "background: var(--blekk)" in _regel(velger), velger

    def test_siden_man_er_paa(self):
        """Ville feilet hvis knappen for siden man er på, var hvit som før."""
        assert "background: var(--oransje)" in _regel('header.stripe a.sideknapp[aria-current="page"]')
        assert "var(--oransje)" in _regel('header.stripe a.sideknapp[aria-current="true"]')


class TestKalleneRegnesAvLista:
    """A7: tallene i «Følg flere aksjer» regnes av kvoten, taket og lista."""

    def test_tallene_foelger_konstantene(self, klient, monkeypatch):
        """Ville feilet hvis 20, 18 eller 1 sto skrevet for hånd."""
        monkeypatch.setattr(valg, "KVOTE", 25)
        monkeypatch.setattr(valg, "TAK", 20)
        html = _html(klient, "/min-liste")
        avsnitt = html.split("<h3>Følg flere aksjer</h3>", 1)[1].split("</p>", 1)[0]
        assert "Lista kan ha opptil 20 aksjer" in avsnitt and "av de 25 kallene" in avsnitt
        assert "med 20 aksjer er 4 igjen" in avsnitt
        treff = re.search(r"Med (\d+) aksjer etter neste henting er (\d+) kall igjen", avsnitt)
        antall, igjen = int(treff.group(1)), int(treff.group(2))
        assert igjen == 25 - antall * valg.KALL_PER_AKSJE - valg.INDEKSKALL
        assert "Gratiskontoen gir 25 kall i døgnet" in html


class TestNullbrikken:
    """Tillegg 2: «Slik leser du tabellen» viser +1, 0 og -1."""

    def test_tre_brikker(self, klient):
        """Ville feilet uten den blanke 0-brikken."""
        html = _html(klient, "/")
        felt = html.split('<span class="utslagsfelt">', 1)[1].split("</span></span>", 1)[0]
        assert re.findall(r'<span class="(\w+)">', felt) == ["pluss", "null", "minus"]
        assert "border: 1px solid var(--strek-2)" in _regel(".utslagsfelt .null")


class TestTekstenUnderGrafen:
    """Tillegg 2: en kort forklaring, og detaljene bak «Mer om grafen»."""

    def test_kort_og_resten_bak_mer_om_grafen(self, klient):
        """Ville feilet hvis alt sto i liten skrift, eller detaljene ikke
        lenger fantes."""
        html = _html(klient, "/aksje/BRFE")
        fig = html.split("<figcaption>", 1)[1].split("</figcaption>", 1)[0]
        kort = fig.split('<p class="graf-kort">', 1)[1].split("</p>", 1)[0]
        assert kort.startswith("Linjene er kursen og 50-dagers snittet")
        detaljer = fig.split('<details class="mer-om-grafen"><summary>Mer om grafen</summary>', 1)[1]
        assert "Det lyse båndet er sjekk 2" in detaljer and "Den stiplede linja er hovedindeksen" in detaljer
        assert "font-size: 1rem" in _regel("figcaption .graf-kort")


class TestSignaletForklart:
    """Tillegg 2: setningen sier hvilken liste tallene gjelder."""

    def test_med_antallet_i_lista(self):
        """Ville feilet hvis setningen bare sa «13 aksjer i lista»."""
        bildet = Dagsbilde(dager=1, dager_minst=False, hovedindeksen=None, aksjer_steg=13, aksjer_falt=2, bransjen=None)
        assert setning_om_samme_dag(bildet, 15) == "Samme dag steg 13 av de 15 aksjene i lista og 2 falt."
        assert setning_om_samme_dag(bildet) == "Samme dag steg 13 aksjer i lista og 2 falt."

    def test_paa_aksjesiden(self, klient):
        """Ville feilet hvis aksjesiden ikke ga antallet i lista."""
        html = _html(klient, "/aksje/BRFE")
        assert re.search(r"\d+ av de 15 aksjene i lista", html.split('class="samme-dag"', 1)[1].split("</p>", 1)[0])


class TestEndringerSomVenter:
    """Tillegg 2 og tillegget om demoen: meldingen øverst."""

    def test_i_demoen_et_eksempel_merket_eksempeltall(self, klient):
        """Ville feilet hvis meldingen ikke kunne ses i demoen."""
        for sti in ("/", "/min-liste"):
            html = _html(klient, sti)
            assert '<p class="venter-melding demo">Eksempeltall:' in html, sti

    def test_med_en_endring_som_venter(self, klient):
        """Ville feilet hvis en endring som venter, ikke ga meldingen øverst."""
        with _demobasen() as t:
            t.execute(
                "INSERT INTO oenske (handling, symbol, laget) VALUES ('fjern', 'BRFE', '2026-10-13T12:00:00+00:00')"
            )
        for sti in ("/", "/min-liste"):
            html = _html(klient, sti)
            melding = html.split('<p class="venter-melding" role="status">', 1)[1].split("</p>", 1)[0]
            assert melding.startswith("Eksempeltall: 1 endring i lista tas i bruk ved hentingen etter kl. 22."), sti
            assert "Demoen henter ikke, så den tas ikke i bruk her." in melding
            assert html.index("venter-melding") < html.index('class="tabellboks"')

    def test_to_endringer(self, klient):
        """Gjennomgangen (VG3): ville feilet med entall ved to, eller med bare
        egne aksjer talt."""
        with _demobasen() as t:
            for symbol in ("BRFE", "KVST"):
                t.execute(
                    "INSERT INTO oenske (handling, symbol, laget) VALUES ('fjern', ?, '2026-10-13T12:00:00+00:00')",
                    (symbol,),
                )
        melding = _html(klient, "/").split('<p class="venter-melding" role="status">', 1)[1].split("</p>", 1)[0]
        assert melding == (
            "Eksempeltall: 2 endringer i lista tas i bruk ved hentingen etter kl. 22. "
            "Demoen henter ikke, så de tas ikke i bruk her."
        )


class TestTreAvTreDetSisteAaret:
    """Tillegg 2: hvor ofte aksjen fikk 3 av 3 det siste året, og sist."""

    def test_regnet_av_radene_som_er_lagret(self):
        """Ville feilet hvis en dag med grunn telte, eller en dag eldre enn et
        år var med."""
        assert alle_sjekkene_det_siste_aaret(None, date(2026, 10, 9), 3) is None
        assert alle_sjekkene_det_siste_aaret({}, date(2026, 10, 9), 3) is None
        bare_grunn = {date(2026, 10, 8): Grunn.SIGNAL_IKKE_REGNET}
        assert alle_sjekkene_det_siste_aaret(bare_grunn, date(2026, 10, 9), 3) == AlleSjekkene(
            0, None, date(2026, 10, 8)
        )

    def test_aaret_og_grensen(self, monkeypatch):
        """Gjennomgangen (BH7, VG2): ville feilet hvis en dag eldre enn et år
        telte, dagen et år før ikke telte, en dag med 2 av 3 telte, eller
        «siden» sto når det er lagret mer enn et år."""

        class Vurdering:
            def __init__(self, styrke):
                self.styrke = styrke

        monkeypatch.setattr(historikk, "Vurdering", Vurdering)
        til = date(2026, 10, 9)
        radene = {
            date(2025, 10, 8): Vurdering(3),  # eldre enn et år
            date(2025, 10, 9): Vurdering(3),  # samme dato året før: med
            date(2026, 3, 2): Vurdering(2),
            date(2026, 10, 1): Vurdering(3),
            date(2026, 10, 9): Grunn.SIGNAL_IKKE_REGNET,
        }
        assert alle_sjekkene_det_siste_aaret(radene, til, 3) == AlleSjekkene(2, date(2026, 10, 1), None)
        uten_den_eldste = {d: v for d, v in radene.items() if d.year == 2026}
        assert alle_sjekkene_det_siste_aaret(uten_den_eldste, til, 3) == AlleSjekkene(
            1, date(2026, 10, 1), date(2026, 3, 2)
        )

    def test_paa_aksjesiden_i_demoen(self, klient):
        """Ville feilet hvis antallet eller den siste dagen ikke var de som er
        lagret. Demoen har vurderinger fra 21.09, så serien er kortere enn et år."""
        with _demobasen() as t:
            dager = [
                d for (d,) in t.execute("SELECT dato FROM vurdering WHERE symbol = 'KVST' AND styrke = 3 ORDER BY dato")
            ]
            foerste = t.execute("SELECT min(dato) FROM vurdering WHERE symbol = 'KVST'").fetchone()[0]
        assert dager
        linje = _html(klient, "/aksje/KVST").split('<p class="alle-sjekkene-aaret">', 1)[1].split("</p>", 1)[0]
        antall = "én gang" if len(dager) == 1 else f"{len(dager)} ganger"
        sist = date.fromisoformat(dager[-1]).strftime("%d.%m")
        fra = date.fromisoformat(foerste).strftime("%d.%m")
        assert f"</span> {antall} siden {fra}, sist {sist}." in linje


class TestSjekkortene:
    """Tillegg 2: tykk kant i fargen for resultatet."""

    def test_kortene_har_klassen_og_kanten(self, klient):
        """Ville feilet hvis kortet ikke fikk fargen, eller merket forsvant."""
        html = _html(klient, "/aksje/BRFE")
        kort = re.findall(r'<section class="sjekkort (opp|ned|ingen)', html)
        assert len(kort) == 3
        assert html.count('class="resultat ') >= 3
        assert "4px solid var(--opp)" in _regel(".sjekkort.opp")
        assert "4px solid var(--ned)" in _regel(".sjekkort.ned")
        assert "4px solid var(--dempet-2)" in _regel(".sjekkort.ingen")


class TestEtterGjennomgangen:
    """Gjennomgangen 10.11 (Blind Hunter, Edge Case Hunter og Verification Gap)."""

    def test_overskriften_paa_oversikten_gjelder_alle_ogsaa_med_min_liste(self, klient):
        """ECH1, BH2, VG1: ville feilet hvis «Min liste» på oversikten endret
        overskriften og linja om 3 av 3, ikke bare tabellen."""
        foer = _html(klient, "/")
        etter = _html(klient, "/?vis=min")
        for start, slutt in (('<h1 class="overskrift">', "</h1>"), ('<p class="alle-sjekkene">', "</p>")):
            assert foer.split(start, 1)[1].split(slutt, 1)[0] == etter.split(start, 1)[1].split(slutt, 1)[0], start

    def test_min_liste_paa_oversikten_uten_merkede(self, klient):
        """ECH2, VG4: ville feilet hvis siden sto uten tabell og uten
        forklaring, eller uten ankeret stjernen sender til."""
        for symbol in demo.MERKET_I_DEMOEN:
            svar = _merk(klient, symbol, "fjern", "/?vis=min")
        assert svar.headers["Location"].endswith("/?vis=min#aksjene")
        html = _html(klient, "/?vis=min")
        assert '<p class="tom-min-liste" id="aksjene">Ingen aksjer i Min liste ennå.' in html
        assert html.count('id="aksjene"') == 1

    def test_bryteren_for_ki_teksten_beholder_valget(self, klient):
        """ECH6: ville feilet hvis bryteren for KI-teksten sendte tilbake til «Alle»."""
        html = _html(klient, "/?vis=min")
        verdier = re.findall(r'name="tilbake" value="([^"]*)"', html.split('class="boersdagen', 1)[1])
        assert verdier and "vis=min" in verdier[0]

    def test_navnet_og_symbolet_skilles(self, klient):
        """BH16: ville feilet hvis skjermleseren fikk navnet og symbolet i ett ord."""
        with _demobasen() as t:
            t.execute(
                "INSERT INTO oenske (handling, symbol, navn, sektor, laget) VALUES "
                "('folg', 'XTEST', 'Eksempelselskap', 'Energi', '2026-10-13T12:00:00+00:00')"
            )
        assert 'Eksempelselskap<span class="skjult">, </span><span class="egen-dag">XTEST</span>' in _html(klient, "/")

    def test_en_aksje_i_lista(self):
        """ECH11: ville feilet med «1 av de 1 aksjene»."""
        bildet = Dagsbilde(dager=1, dager_minst=False, hovedindeksen=None, aksjer_steg=1, aksjer_falt=0, bransjen=None)
        assert setning_om_samme_dag(bildet, 1) == "Samme dag steg 1 aksje i lista og 0 falt."
