"""Story 8.0b: hjelpetekstene bak «?».

Hvert kontrollpunkt i storyen har sin test, og hver test er proevd med en
mutant (spesifikasjonen, Verification).
"""

import re
import shutil
import sqlite3
from pathlib import Path

import pytest

import app as app_modul
import demo
import lagring_sqlite
from hjelpetekster import MAALTE_GRENSER, Hjelp, hjelpetekster
from markedsoversikt import RETNINGSVISNING
from signalberegning import BLANDET, INGEN, NEGATIV, POSITIV, STANDARD, Parametre, interesse, trend
from tallformat import HARDT_MELLOMROM as NB
from tallformat import tall
from test_app import _stil, _uten_hjelpeskriptet

ROT = Path(__file__).resolve().parent.parent

# Tallene med dagens parametre, slik de staar i tekstene.
STANDARDTALL = (
    f"mer enn 2{NB}%",
    "de siste 50 børsdagene",
    "de 20 børsdagene før",
    "1,5 ganger",
    "trenger 51 børsdager",
    "styrke 2 eller mer",
)

ANDRE = Parametre(
    ma_vindu=40,
    noytralsone=0.03,
    volatilitet_vindu=15,
    volum_vindu=25,
    volumfaktor=2.5,
    terskel=3,
)


def _alt(tekster, uten=()) -> str:
    return "\n".join(f"{t.tittel} {t.tekst}" for n, t in tekster.items() if n not in uten)


class TestTalleneFraParametre:
    def test_dagens_tall_staar_i_tekstene(self):
        alt = _alt(hjelpetekster())
        for tekst in STANDARDTALL:
            assert tekst in alt, tekst

    def test_andre_parametre_gir_andre_tall(self):
        """Kontrollpunktet: tallene hentes fra Parametre. Ville feilet hvis
        50 dager eller 1,5 ganger var skrevet fast i en tekst."""
        # grensene sier hva som ble maalt, og staar for seg (TestGrensene).
        alt = _alt(hjelpetekster(ANDRE), uten=("grensene",))
        for tekst in STANDARDTALL:
            assert tekst not in alt, tekst
        for tekst in (
            f"mer enn 3{NB}%",
            f"innenfor 3{NB}%",
            "de siste 40 børsdagene",
            "de 15 børsdagene før",
            "de 25 børsdagene før",
            "2,5 ganger",
            "trenger 41 børsdager",
            "styrke 3 eller mer",
        ):
            assert tekst in alt, tekst

    @pytest.mark.parametrize(
        "verdi, slag",
        [
            (STANDARD.noytralsone * 100, "grense"),
            (STANDARD.volumfaktor, "faktor"),
            (STANDARD.ma_vindu, "heltall"),
            (STANDARD.volatilitet_vindu, "heltall"),
            (STANDARD.volum_vindu, "heltall"),
            (STANDARD.terskel, "heltall"),
        ],
    )
    def test_tallet_som_vises_er_parameteren(self, verdi, slag):
        """Ville feilet hvis en parameter ble rundet av der den vises,
        for eksempel en volumfaktor paa 1,25 vist som «1,3»."""
        vist = tall(verdi, slag).replace(NB, "").removesuffix("%").replace(",", ".")
        assert float(vist) == pytest.approx(verdi, abs=1e-12)

    @pytest.mark.parametrize("p", [Parametre(volumfaktor=1.25), Parametre(noytralsone=0.025)])
    def test_en_parameter_som_maatte_rundes_av_stopper(self, p):
        """Gjennomgangen av 8.0b: en volumfaktor paa 1,25 ville staatt som
        «1,2» med én desimal. Da feiler tekstene i stedet for aa vise et
        annet tall enn koden bruker."""
        with pytest.raises(ValueError, match="Rett desimalene"):
            hjelpetekster(p)


class TestGrensene:
    def test_standard_er_grensene_som_ble_maalt(self):
        """Teksten om maalingen gjelder grensene i malinger.md §7.4 og §9.
        Ville feilet hvis en grense i Parametre ble endret uten ny maaling."""
        for felt in ("noytralsone", "volumfaktor", "volatilitet_vindu", "volum_vindu", "terskel"):
            assert getattr(STANDARD, felt) == getattr(MAALTE_GRENSER, felt), felt

    def test_teksten_om_maalingen_nevner_de_maalte_grensene(self):
        forventet = (
            f"2{NB}%, 1,5 ganger, de to vinduene på 20 børsdager og terskelen 2 "
            f"ble kontrollert mot 15 aksjer på Oslo Børs over 199 børsdager"
        )
        assert forventet in hjelpetekster()["grensene"].tekst
        assert forventet in hjelpetekster(ANDRE)["grensene"].tekst


def _serie(siste: float, n: int = 22) -> list[float]:
    return [100.0] * (n - 1) + [siste]


class TestTekstenSierDetKodenGjoer:
    """Gjennomgangen av 8.0b (Verification Gap): setningene om fortegn og
    sone bindes til det koden gjoer, ikke bare til tallene."""

    @pytest.mark.parametrize(
        "siste, verdi, setning",
        [(103.0, 1, "+1 en dag kursen steg"), (97.0, -1, "-1 en dag den falt"), (100.0, 0, "0 når kursen var uendret")],
    )
    def test_interesse(self, siste, verdi, setning):
        volumer = [100.0] * 21 + [200.0]
        assert interesse(_serie(siste), volumer).verdi == verdi
        assert setning in hjelpetekster()["interesse"].tekst

    @pytest.mark.parametrize(
        "siste, verdi, setning",
        [(110.0, 1, "Over gir +1"), (90.0, -1, "under gir -1"), (100.5, 0, f"innenfor 2{NB}% gir 0")],
    )
    def test_trend(self, siste, verdi, setning):
        assert trend(_serie(siste, 50)).verdi == verdi
        assert setning in hjelpetekster()["trend"].tekst

    @pytest.mark.parametrize("siste, verdi, setning", [(110.0, 1, "+1 når kursen steg"), (90.0, -1, "-1 når den falt")])
    def test_bevegelse(self, siste, verdi, setning):
        """VG8 i gjennomgangen av PR #35: setningen om fortegnet i bevegelse
        er bundet til koden, som trend og interesse."""
        from signalberegning import bevegelse

        kurser = [100.0 + (i % 2) for i in range(30)] + [siste]
        assert bevegelse(kurser).verdi == verdi
        assert setning in hjelpetekster()["bevegelse"].tekst

    def test_endringen_sier_hvor_datoene_staar(self):
        """Svar 32 i 8.0d (rettet kl. 13:05): én tekst for oversikten og
        aksjesiden, som sier det samme som endringskortet etter svar 29.
        Ville feilet med «fra børsdagen før»."""
        tekst = hjelpetekster()["endring"]
        assert (tekst.tittel, tekst.tekst) == (
            "Endring:",
            "endringen i prosent fra forrige dag med kurs, regnet på utbyttejustert kurs. "
            "Mangler kilden kurser for noen børsdager, står datoene ved endringen på aksjesiden.",
        )


class TestRetningen:
    @pytest.mark.parametrize(
        "noekkel, retning",
        [("positiv", POSITIV), ("negativ", NEGATIV), ("blandet", BLANDET), ("ingen", INGEN)],
    )
    def test_ordet_og_symbolet_er_fr_704_sine(self, noekkel, retning):
        """Kontrollpunktet: retningen forklares med ordene i FR-704, bygget
        av de samme konstantene som tabellen viser."""
        visning = RETNINGSVISNING[retning]
        assert hjelpetekster()[noekkel].tittel == f"{visning.symbol} {visning.tekst}:"

    def test_ikke_opp_og_ned_som_navn(self):
        """FR-103, endret 21.09: «Opp» og «Ned» er fjernet som ord for
        retningen. Som verb i bevegelse («Opp gir +1») er de ikke navn paa
        en retning, saa testen ser paa titlene og ordene i anfoerselstegn."""
        for tekst in hjelpetekster().values():
            assert not re.search(r"\b(Opp|Ned)\b", tekst.tittel, re.IGNORECASE), tekst.tittel
            assert not re.search(r"«(Opp|Ned)»", tekst.tekst, re.IGNORECASE), tekst.tekst

    def test_ingen_og_ukjent_forklares_hver_for_seg(self):
        """Kontrollpunktet: «Ingen» og «Ukjent» forklares hver for seg.
        Ville feilet hvis de to sto som én tekst."""
        tekster = hjelpetekster()
        ingen, ukjent = tekster["ingen"], tekster["ukjent"]
        assert ingen.tittel == "– Ingen:" and ukjent.tittel == "– Ukjent:"
        assert "styrken er 0" in ingen.tekst
        assert "ingen vurdering" in ukjent.tekst
        assert "styrken er 0" not in ukjent.tekst
        assert "ingen vurdering" not in ingen.tekst


# Ord som kan leses som et raad (NFR-06). Bare ikke_raad kan si kjoepe og
# selge, fordi den sier at signalet ikke er et raad.
RAADSORD = (
    r"\bbør\b",
    r"\banbefal",
    r"\bkjøp",
    r"\bselg",
    r"\blønn",
    r"\bmulighet",
    r"\btips",
    r"\bvil stige",
    r"\bvil falle",
    r"\bkurspotensial",
    r"\bgevinst",
    r"\bsalg",
    r"\bhandl",
    r"\binvester",
    r"\bverdt å",
)


class TestIkkeRaad:
    def test_ingen_tekst_kan_leses_som_et_raad(self):
        """Ville feilet hvis en tekst sa noe som kan leses som et raad."""
        for noekkel, tekst in hjelpetekster().items():
            if noekkel == "ikke_raad":
                continue
            for ord_ in RAADSORD:
                assert not re.search(ord_, f"{tekst.tittel} {tekst.tekst}", re.IGNORECASE), (noekkel, ord_)

    def test_hjelpen_sier_at_signalet_ikke_er_et_raad(self):
        tekst = hjelpetekster()["ikke_raad"].tekst
        assert "ikke en spådom" in tekst
        assert "ikke et råd om å kjøpe eller selge" in tekst


class TestKildene:
    def test_hver_tekst_har_en_kilde_som_finnes(self):
        """Kontrollpunktet: teksten sier ikke noe som ikke staar i en kilde.
        Hver tekst viser til en fil, og stedet staar ordrett i den. Ville
        feilet hvis en tekst manglet kilde, eller kilden var flyttet."""
        for noekkel, tekst in hjelpetekster().items():
            assert tekst.kilder, noekkel
            for fil, sted in tekst.kilder:
                sti = ROT / fil
                assert sti.is_file(), (noekkel, fil)
                assert sted in sti.read_text(encoding="utf-8"), (noekkel, fil, sted)


class TestHjelp:
    def test_en_ukjent_noekkel_feiler_med_navnet(self):
        with pytest.raises(KeyError, match="'finnes_ikke'"):
            Hjelp(hjelpetekster()).tekst("finnes_ikke")

    def test_en_kjent_noekkel_gir_teksten(self):
        assert Hjelp(hjelpetekster()).tekst("trend") == hjelpetekster()["trend"]


# --- Sidene (del c) --------------------------------------------------------


@pytest.fixture(scope="module")
def basemal(tmp_path_factory):
    """En base uten demomerket, med demoens kurser og vurderinger. Lages i
    tmp_path (regel 22), og merket nulles, saa sidene leser den som en ekte
    base uten «Eksempeltall»."""
    sti = tmp_path_factory.mktemp("hjelpemal") / "ose.db"
    demo.lag_demobase(sti, skriv=lambda _: None)
    tilkobling = sqlite3.connect(sti)
    try:
        tilkobling.execute("PRAGMA application_id = 0")
        tilkobling.commit()
    finally:
        tilkobling.close()
    return sti


@pytest.fixture
def klient(monkeypatch):
    monkeypatch.delenv(app_modul.I_DEMO, raising=False)
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


@pytest.fixture
def base(basemal):
    sti = Path(lagring_sqlite.BASE_STI)
    sti.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(basemal, sti)
    return sti


# Story 8.6: børsometeret har sin egen tekst.
SIDENE = ("/", "/boersometer", "/aksje/BRFE", "/aksje/VRDS")


def _side(klient, adresse: str) -> str:
    svar = klient.get(adresse)
    assert svar.status_code == 200, adresse
    return svar.data.decode("utf-8")


class TestSidene:
    def test_hver_tekst_malene_ber_om_finnes(self, klient, base):
        """Kontrollpunktet: en test sjekker at hver tekst malene ber om,
        finnes i fila. hjelp.tekst() feiler paa en noekkel som mangler, og
        med TESTING slipper feilen gjennom her."""
        for adresse in SIDENE:
            _side(klient, adresse)

    def test_hver_tekst_i_fila_brukes_av_en_mal(self, klient, base, monkeypatch):
        """Ingen tekst blir liggende uten at en side viser den."""
        bedt_om: set[str] = set()

        class Opptak(Hjelp):
            def tekst(self, noekkel):
                bedt_om.add(noekkel)
                return super().tekst(noekkel)

        monkeypatch.setattr(app_modul, "Hjelp", Opptak)
        for adresse in SIDENE:
            _side(klient, adresse)
        assert bedt_om == set(hjelpetekster())

    def test_hvert_spoersmaalstegn_staar_ved_det_det_forklarer(self, klient, base):
        """Story 8.0c, den nye delen 2 (godkjent 13.10 kl. 15:36): «?» ved
        hver kolonne og ved «data hentet» i oversikten, og ved nøkkeltallene,
        grafen, «Hvorfor signalet ble …», hver sjekk, Ga og Målt mot paa
        aksjesiden. Ingen «?» ved overskriften lenger. Ville feilet hvis et
        «?» sto et annet sted enn ved det det forklarer."""
        knapp = r'<button type="button" class="hjelpeknapp" popovertarget="{}"'
        oversikt = _side(klient, "/")
        # Story 8.15: navnet er en lenke som sorterer, og «?» står etter den.
        lenke = (
            r'<a class="sorter[^"]*" href="[^"]*">{}<span class="skjult">[^<]*</span><svg[^>]*><path[^>]*/></svg></a> '
        )
        for tekst, vindu in (
            # Story 8.15b: Selskap er en sorteringslenke, og «?» staar etter den.
            (r"<th[^>]*>" + lenke.format("Selskap"), "hjelp-selskap"),
            (r'<th class="tall"[^>]*>' + lenke.format("Sluttkurs"), "hjelp-sluttkurs"),
            (r'<th class="tall"[^>]*>' + lenke.format("Endring"), "hjelp-endring"),
            (r'<th class="tall"[^>]*>' + lenke.format("Signalstyrke"), "hjelp-signalstyrke"),
            (r"<th[^>]*>" + lenke.format("Retning"), "hjelp-retning"),
        ):
            assert re.search(tekst + knapp.format(vindu), oversikt), vindu
        # Story 2.9: «?» ved overskriften til hovedindeksen.
        assert re.search(
            r'<h2><span id="hovedindeks-tittel">Hovedindeksen</span>(\s*<span class="indekssymbol">[^<]*</span>)? '
            + knapp.format("hjelp-hovedindeks"),
            oversikt,
        )
        # Story 8.0d, PR 2: tidspunktet står bare i stripa, som «Oppdatert»,
        # med «?» ved siden av (BH2, svar 5).
        stripa = oversikt.split('<header class="stripe">', 1)[1].split("</header>", 1)[0]
        assert re.search(r"Oppdatert [^<]+</span>\s*" + knapp.format("hjelp-hentet"), stripa)
        assert "data hentet" not in oversikt
        detalj = _side(klient, "/aksje/BRFE")
        for tekst, vindu in (
            ('<span class="etikett">Sluttkurs ', "hjelp-kurs"),
            ('<span class="etikett">Signalstyrke ', "hjelp-styrke"),
            ('<span class="etikett">Retning ', "hjelp-retning-aksje"),
            ('<span class="etikett">Endring ', "hjelp-endring"),
            ('<h2 id="kursgrafen">Kursutvikling, 6 måneder ', "hjelp-graf"),
            # Story 8.0d, PR 3 (svar 22): i sjekkortene.
            ('<span class="ga">Ga ', "hjelp-ga"),
            ('<p class="maalt">Målt mot ', "hjelp-maalt"),
            ("<h3>Trend ", "hjelp-trend"),
            ("<h3>Bevegelse ", "hjelp-bevegelse"),
            ("<h3>Interesse ", "hjelp-interesse"),
        ):
            assert re.search(re.escape(tekst) + knapp.format(vindu), detalj), vindu
        assert re.search(r"<h2>Hvorfor signalet ble [^<]* " + knapp.format("hjelp-sjekkene"), detalj)
        assert "Tallene og signalet" not in oversikt + detalj
        # Story 8.0d, PR 3: «?» ved «Oppdatert» i stripa også på aksjesiden,
        # og hvert vindu har én knapp.
        stripa = detalj.split('<header class="stripe">', 1)[1].split("</header>", 1)[0]
        assert re.search(r"Oppdatert [^<]+</span>\s*" + knapp.format("hjelp-hentet"), stripa)
        for vindu in ("hjelp-ga", "hjelp-maalt"):
            assert detalj.count(f'class="hjelpeknapp" popovertarget="{vindu}"') == 1, vindu

    def test_hvert_vindu_har_bare_sine_tekster(self, klient, base):
        """Den nye delen 2: vinduene og tekstene i dem, i rekkefoelge. «Ikke et
        raad» staar i vinduet for signalstyrken paa begge sidene, og skjevhet
        i vinduet for retning paa aksjesiden."""
        tekster = hjelpetekster()

        from markupsafe import escape

        def vindu(html, id_):
            del_ = (
                html.split(f'<div id="{id_}" class="hjelpevindu" popover>', 1)[1]
                .split('<div id="hjelp-')[0]
                .split("</body>")[0]
            )
            avsnitt = re.findall(r"<p>(.*?)</p>", del_, flags=re.DOTALL)
            funnet = []
            for p_ in avsnitt:
                treff = [n for n, t in tekster.items() if t.tekst and str(escape(t.tekst)) in p_]
                assert len(treff) == 1, (id_, p_)
                funnet.append(treff[0])
            return funnet

        forventet = {
            "/": {
                # Story 2.9: delen over tabellen.
                # Story 2.9b: søylene i samme vindu.
                "hjelp-hovedindeks": ["hovedindeksen", "soeylene"],
                "hjelp-selskap": ["selskap"],
                "hjelp-sluttkurs": ["sluttkurs"],
                "hjelp-endring": ["endring", "utbyttejustert"],
                "hjelp-signalstyrke": ["signalstyrke", "uten_styrke", "ikke_raad"],
                "hjelp-retning": ["retning", "positiv", "negativ", "blandet", "ingen", "ukjent"],
                "hjelp-hentet": ["data_hentet", "uten_data"],
            },
            "/aksje/BRFE": {
                # Story 8.0d, PR 3: «data hentet» står ved «Oppdatert» i stripa,
                # og endringen er et eget nøkkeltall.
                "hjelp-hentet": ["data_hentet_aksje"],
                # U5 (story 2.7b): sluttkursen for dagen siden viser.
                "hjelp-kurs": ["sluttkurs_aksje", "utbyttejustert"],
                "hjelp-endring": ["endring", "utbyttejustert"],
                # Story 2.9c: den stiplede linja, når basen har indeksen.
                # Story 8.16: periodene i samme vindu som grafen.
                "hjelp-graf": ["grafen", "indekslinja", "perioden"],
                "hjelp-styrke": ["signalstyrke", "ikke_raad"],
                "hjelp-retning-aksje": [
                    "retning",
                    "positiv",
                    "negativ",
                    "blandet",
                    "ingen",
                    "ukjent_aksje",
                    "skjevhet",
                ],
                "hjelp-sjekkene": ["hvorfor_tre", "antall_dager"],
                # Story 2.7b: historikken nederst på siden.
                "hjelp-historikk": ["historikken"],
                "hjelp-trend": ["trend"],
                "hjelp-bevegelse": ["bevegelse"],
                "hjelp-interesse": ["interesse"],
                "hjelp-ga": ["ga"],
                "hjelp-maalt": ["maalt_mot", "grensene"],
            },
        }
        for adresse, vinduer in forventet.items():
            html = _side(klient, adresse)
            assert set(re.findall(r'<div id="(hjelp-[a-z-]+)" class="hjelpevindu"', html)) == set(vinduer), adresse
            for id_, noekler in vinduer.items():
                assert vindu(html, id_) == noekler, (adresse, id_)

    def test_spoersmaalstegn_ved_signalstyrke_i_oversikten(self, klient, base):
        """Tillegget 05.10: «?» ved overskriften Signalstyrke, med teksten
        om styrken. Det er fortsatt fem kolonner (FR-101)."""
        html = _side(klient, "/")
        assert re.search(
            r'<th class="tall"><a class="sorter" href="[^"]*">Signalstyrke<span class="skjult">[^<]*</span><svg[^>]*><path[^>]*/></svg></a> '
            r'<button type="button" class="hjelpeknapp" popovertarget="hjelp-signalstyrke"[^>]*>\?</button></th>',
            html,
        )
        thead = html.split("<thead>")[1].split("</thead>")[0]
        assert thead.count("<th") == 5
        vindu = html.split('<div id="hjelp-signalstyrke"')[1].split("</body>")[0]
        assert "<h2>Signalstyrke</h2>" in vindu
        for noekkel in ("signalstyrke", "uten_styrke", "ikke_raad"):
            assert hjelpetekster()[noekkel].tekst in vindu, noekkel

    def test_ingen_skript_og_ingenting_fra_nettet(self, klient, base):
        """Kontrollpunktet: uten nettkall. Ville feilet hvis en side hentet
        et skript, et stilark eller en skrift fra nettet. Story 8.0f: det
        ene skriptet er hjelpen fra /static/."""
        for adresse in SIDENE:
            html = _side(klient, adresse)
            assert "<script" not in _uten_hjelpeskriptet(html).lower(), adresse
            assert not re.search(r'(src|href)\s*=\s*"(https?:)?//', html), adresse
            # Story 8.0d: skriften ligger i appen, saa url( er lov bare til
            # /static/ (designregler §1).
            adresser = re.findall(r"""url\(\s*["']?([^"')]+)""", html)
            assert all(u.startswith("/static/") for u in adresser), adresse
            assert "@import" not in html, adresse

    def test_hver_knapp_aapner_et_vindu_paa_samme_side(self, klient, base):
        """Ville feilet hvis knappen pekte paa et id som ikke finnes, og
        vinduet aldri aapnet seg, eller et vindu sto uten «?» som aapner det.
        Bare «?»-knappene teller: lukkeknappen inne i vinduet peker ogsaa paa
        vinduet (mutant M12)."""
        for adresse in SIDENE:
            html = _side(klient, adresse)
            maal = set(re.findall(r'class="hjelpeknapp" popovertarget="([^"]+)"', html))
            vinduer = set(re.findall(r'<div id="([^"]+)" class="hjelpevindu" popover>', html))
            assert maal and maal == vinduer, adresse

    def test_knappen_virker_med_tastatur_og_skjermleser(self, klient, base):
        """En <button> kan naas med Tab og aapnes med Enter, og popover
        lukkes med Esc. Knappen har et navn, og vinduet en lukkeknapp."""
        for adresse in SIDENE:
            html = _side(klient, adresse)
            for knapp in re.findall(r'<button type="button" class="hjelpeknapp"[^>]*>', html):
                assert 'aria-label="Hjelp: ' in knapp
            for vindu in re.findall(r'<div id="([^"]+)" class="hjelpevindu" popover>', html):
                assert f'popovertarget="{vindu}" popovertargetaction="hide">Lukk</button>' in html

    def test_vinduet_passer_paa_en_telefon(self, klient, base):
        html = _side(klient, "/")
        # Story 8.0d: hoeyst 440 px bred (utdraget §7), og aldri bredere enn
        # skjermen minus 2rem.
        # Story 2.7a: stilen står i stilarket.
        assert "width: min(440px, calc(100vw - 2rem)); max-height: 80vh; overflow: auto;" in _stil(html)

    def test_grafen_og_tabellen_forklares_bare_naar_de_vises(self, klient, base):
        """Gjennomgangen av 8.0b: VRDS har for kort serie til signal og
        snitt, saa hjelpen forklarer verken den stiplede linja eller
        kolonnene Ga og Maalt mot."""
        tekster = hjelpetekster()
        brfe = _side(klient, "/aksje/BRFE")
        vrds = _side(klient, "/aksje/VRDS")
        for noekkel in ("grafen", "ga", "maalt_mot"):
            assert tekster[noekkel].tekst in brfe, noekkel
            assert tekster[noekkel].tekst not in vrds, noekkel

    def test_tom_base_har_ingen_hjelp(self, klient):
        """Story 8.0c: uten kurser er det ingen tabell og ingen tall aa
        forklare, saa det staar ingen «?» og ingen vinduer."""
        html = _side(klient, "/")
        assert "popovertarget" not in html
        assert 'class="hjelpevindu"' not in html


class TestSnittetIGrafen:
    def test_ma_vinduet_kommer_fra_parametre(self, klient, base, monkeypatch):
        """Svar 4 11.10: «50-dagers snitt» i aksje.html hentes fra Parametre.
        Ville feilet hvis 50 sto fast i malen."""
        assert "50-dagers snitt (sjekk 1)" in _side(klient, "/aksje/BRFE")
        monkeypatch.setattr(app_modul, "STANDARD", Parametre(ma_vindu=40))
        html = _side(klient, "/aksje/BRFE")
        assert "40-dagers snitt (sjekk 1)" in html
        # Story 8.0d, PR 3 (svar 19): etiketten for skjermleseren.
        assert "den tynne er 40-dagers snitt (sjekk 1)" in html
        assert "50-dagers" not in html
        # Hjelpen foelger samme parametre som navnet paa linja i grafen.
        assert "snittet av de siste 40 børsdagene" in html
        # Story 10.2e: KI-teksten i demoen er laget med regelens 50 og staar
        # fast (demo_ki_tekster.json), saa den tas ut her. Testen gjelder malen
        # og hjelpen.
        uten_ki = re.sub(r'<section class="ki".*?</section>', "", html, flags=re.S)
        assert "de siste 50 børsdagene" not in uten_ki


# Story 8.0c: hoeyst 3 setninger per tekst, og ordene ordlista har valgt bort
# (designregler.md §4, rettet 13.10).
UNNTAK_LENGDE = {"grensene", "skjevhet"}
VALGT_BORT = (
    r"peker opp",
    r"peker ned",
    r"peker hver sin vei",
    r"\bspriker\b",
    r"\balle tre\b",
    r"\bde tre\b",
    r"hvor kraftig",
    r"summen av tallene",
    r"\bkroner\b",
    r"\bkr\b",
    r"v1\.1",
    r"\(idé\)",
    r"lys bakgrunn",
)


def synlig_tekst(html: str) -> str:
    """Teksten paa siden uten <style> og tagger, med mellomrom slaatt sammen,
    saa et ord som er delt over to linjer i malen ogsaa blir funnet (ECH3), og
    et klassenavn i CSS ikke gir treff (ECH4). Story 2.7a: sidene har ingen
    <style> lenger, saa det er bare en sikring."""
    html = re.sub(r"<style>.*?</style>", " ", html, flags=re.DOTALL)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _setninger(tekst: str) -> int:
    """Setninger som slutter med punktum, spoersmaalstegn eller utropstegn."""
    return len(re.findall(r"[.?!][»)\"]*(?=\s|$)", tekst.strip()))


class TestStory80c:
    def test_setningstelleren(self):
        assert _setninger("En. To? Tre!") == 3
        assert _setninger("1,5 ganger og 2 %.") == 1
        assert _setninger("Slutt.» Ny. (Se FR-703.)") == 3

    @pytest.mark.parametrize("p", [STANDARD, ANDRE], ids=["standard", "andre"])
    def test_hoeyst_tre_setninger_per_tekst(self, p):
        """Svar 6 og 2: hoeyst 3 setninger, utenom grensene og skjevhet, som
        forklarer en maaling. Ville feilet med signalstyrke paa 4 setninger,
        som foer 8.0c."""
        for noekkel, tekst in hjelpetekster(p).items():
            if noekkel in UNNTAK_LENGDE:
                continue
            assert _setninger(tekst.tekst) <= 3, (noekkel, tekst.tekst)

    def test_ingen_tekst_har_ord_ordlista_har_valgt_bort(self):
        """Ville feilet med «peker opp» i hjelpen for retning, som foer 8.0c."""
        for noekkel, tekst in hjelpetekster().items():
            for ord_ in VALGT_BORT:
                assert not re.search(ord_, f"{tekst.tittel} {tekst.tekst}", re.IGNORECASE), (noekkel, ord_)

    def test_ingen_side_har_ord_ordlista_har_valgt_bort(self, klient, base):
        """Malene ogsaa: fotnotene sa «hvor kraftig» og «summen av tallene»
        foer 8.0c. Sidene leses med testbasen her og med demobasen i
        test_demo.py."""
        for adresse in SIDENE:
            # Story 3.4b (gruppens svar 18.10 kl. 20:08): ordlista gjelder vaar
            # tekst, ikke KI-teksten, til prompten faar den i versjon 3. Bare
            # avsnittet med modellens ord tas ut.
            side = _side(klient, adresse)
            # Gjennomgangen, BH11: hoeyst ett avsnitt, og bare paa aksjesiden.
            assert side.count('<p class="ki-tekst">') <= (1 if adresse.startswith("/aksje/") else 0), adresse
            html = re.sub(r'<p class="ki-tekst">.*?</p>', "", side, flags=re.DOTALL)
            tekst = synlig_tekst(html)
            for ord_ in VALGT_BORT:
                assert not re.search(ord_, tekst, re.IGNORECASE), (adresse, ord_)

    def test_hver_sjekk_har_en_noekkel_som_gir_en_gyldig_id(self):
        """ECH6: «?» per sjekk bruker navnet med smaa bokstaver som id og som
        noekkel. Ville feilet med et navn med mellomrom eller æøå, eller et
        som kolliderer med et fast vindu."""
        import aksjedetalj  # noqa: F401
        from signalberegning import beregn_signal

        faste = {"kurs", "graf", "styrke", "retning-aksje", "sjekkene", "ga", "maalt"}
        from datetime import date, timedelta

        from kursdata import Kursrad

        rader = [
            Kursrad(dato=date(2026, 9, 1) + timedelta(days=i), slutt=k, justert_slutt=k, volum=1000)
            for i, k in enumerate([100.0] * 60 + [104.0])
        ]
        signal = beregn_signal(rader)
        tekster = hjelpetekster()
        for sjekk in signal.sjekker:
            noekkel = sjekk.navn.lower()
            assert re.fullmatch(r"[a-z]+", noekkel), sjekk.navn
            assert noekkel in tekster and noekkel not in faste, noekkel

    def test_antall_sjekker_er_antallet_i_koden(self):
        """ECH7: «N av 3» og den gule ringen bygger paa ANTALL_SJEKKER. Ville
        feilet hvis en fjerde sjekk kom til uten at konstanten ble rettet."""
        from datetime import date, timedelta

        from hjelpetekster import ANTALL_SJEKKER
        from kursdata import Kursrad
        from signalberegning import beregn_signal

        rader = [
            Kursrad(dato=date(2026, 9, 1) + timedelta(days=i), slutt=k, justert_slutt=k, volum=1000)
            for i, k in enumerate([100.0] * 60 + [104.0])
        ]
        signal = beregn_signal(rader)
        assert len(signal.sjekker) == ANTALL_SJEKKER


# Story 8.0f: hjelpen ved «?» som ett fast felt, med src/static/hjelp.js.
HJELPESKRIPTET = ROT / "src" / "static" / "hjelp.js"
STILARKET = ROT / "src" / "static" / "stil.css"


class TestHjelpefeltet:
    def test_skriptet_er_lenket_med_avtrykket(self, klient, base):
        """Ville feilet hvis en side manglet skriptet, lenket det to ganger,
        eller lenket en gammel utgave, saa nettleseren brukte den."""
        import hashlib

        avtrykk = hashlib.sha256(HJELPESKRIPTET.read_bytes()).hexdigest()[:16]
        lenke = f'<script src="/static/hjelp.js?v={avtrykk}" defer></script>'
        for adresse in SIDENE:
            assert _side(klient, adresse).count(lenke) == 1, adresse
        svar = klient.get("/static/hjelp.js")
        assert svar.status_code == 200
        svar.close()

    def test_uten_skriptet_er_hjelpen_som_foer(self, klient, base):
        """Kontrollpunktet: uten JavaScript virker hjelpen som i dag. Ville
        feilet hvis vinduene var manual i HTML-en, saa Esc og et klikk utenfor
        ikke lukket uten skriptet, eller stilen for feltet gjaldt uten
        klassen skriptet setter."""
        for adresse in SIDENE:
            html = _side(klient, adresse)
            assert 'popover="manual"' not in html and 'popovertargetaction="show"' not in html, adresse
            assert 'class="hjelpefelt"' not in html, adresse
        stil = STILARKET.read_text(encoding="utf-8")
        flyttet = [
            velger.strip()
            for velger, kropp in re.findall(r"([^{};]*\.hjelpevindu[^{]*)\{([^}]*)\}", stil)
            if re.search(r"\b(position|inset)\s*:", kropp)
        ]
        assert flyttet and all(v.startswith(".hjelpefelt ") for v in flyttet), flyttet
        assert re.search(r"\.hjelpefelt body:has\(\.hjelpevindu:popover-open\)", stil)
        assert "margin: auto" in _regel_i(stil, ".hjelpevindu")

    def test_skriptet_henter_ingenting(self):
        """Ville feilet hvis skriptet hentet noe fra nettet eller lastet et
        annet skript."""
        kode = HJELPESKRIPTET.read_text(encoding="utf-8")
        for ord_ in ("http", "fetch(", "XMLHttpRequest", "import", "eval(", "innerHTML"):
            assert ord_ not in kode, ord_


def _regel_i(stil: str, velger: str) -> str:
    """Kroppen til den første regelen med akkurat denne velgeren."""
    treff = re.search(r"(?m)^" + re.escape(velger) + r"\s*\{([^}]*)\}", stil)
    assert treff, velger
    return treff.group(1)
