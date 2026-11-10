"""Story 8.21: egne notater på aksjesiden - AD-3, AD-7, AD-10, AD-16, NFR-06,
NFR-08 (gruppens svar 10.11 kl. 14:32).

Spesifikasjonen er spec-8-21-egne-notater-paa-aksjesiden.md, med delene A-D.
Testbasene ligger i tmp_path (conftest.py, regel 22), og ingen test gjør
nettkall (AD-8).
"""

import re
import shutil
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

import app as app_modul
import demo
import lagring_sqlite
from etterpaa import INDEKSEN_MANGLER_DAGEN, INGEN_INDEKS, INGEN_KURS_PAA_NOTATDAGEN, bygg_etterpaa, endring
from kursdata import Kursrad
from lagring_sqlite import SqliteNotatlager, aapne_base, demo_sti
from notater import MAKS_TEGN, MinneNotatlager, Notat, Notatlager, UgyldigNotat, rens
from vurderingsdata import Grunn, Vurdering

ROT = Path(__file__).resolve().parents[1]
LAGET = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)
# Demobasen har kurser fra 02.01 til fredag 09.10 (demo.py).
SISTE = date(2026, 10, 9)
TIDLIGERE = date(2026, 10, 1)
AKSJE = "BRFE"
ANNEN = "KVST"


@pytest.fixture(scope="module")
def mal(tmp_path_factory):
    sti = tmp_path_factory.mktemp("demomal") / "demo.db"
    demo.lag_demobase(sti, skriv=lambda _: None)
    return sti


@pytest.fixture
def demobase(mal):
    sti = demo_sti()
    sti.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(mal, sti)
    return sti


@pytest.fixture
def klient(demobase, monkeypatch):
    """Demoen, med bryteren på, som brukeren starter den."""
    monkeypatch.setenv(app_modul.I_DEMO, "1")
    monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
    monkeypatch.setattr(app_modul, "naa", lambda: LAGET)
    app_modul.app.config["TESTING"] = True
    return app_modul.app.test_client()


def _rader(sti: Path, tabell: str = "notat") -> list:
    c = sqlite3.connect(sti)
    try:
        return c.execute(f"SELECT * FROM {tabell} ORDER BY rowid").fetchall()
    finally:
        c.close()


def _alle_andre_tabeller(sti: Path) -> dict:
    c = sqlite3.connect(sti)
    try:
        navn = [n for (n,) in c.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name <> 'notat'")]
        return {n: c.execute(f"SELECT * FROM {n} ORDER BY rowid").fetchall() for n in navn}
    finally:
        c.close()


def _delen(side: str) -> str:
    start = side.index('<section class="notater"')
    return side[start : side.index("</section>", start)]


def _tekst(html: str) -> str:
    # Bare vanlige mellomrom og linjeskift, så det harde mellomrommet foran %
    # står (regel 21).
    return re.sub(r"[ \t\r\n]+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _vurdering(trend: int, bevegelse: int, interesse: int, kurs: float = 100.0) -> Vurdering:
    sjekker = (trend, bevegelse, interesse)
    utslag = [v for v in sjekker if v]
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
        styrke=sum(abs(v) for v in sjekker),
        retning=retning,
        trend=trend,
        bevegelse=bevegelse,
        interesse=interesse,
        slutt=kurs,
        justert_slutt=kurs,
        trend_avvik=0.0,
        dagens_endring=0.0,
        standardavvik=0.01,
        volumforhold=1.0 if interesse == 0 else 2.0,
    )


# --- A) Tabellen notat og porten ---------------------------------------------


class TestTabellen:
    def test_notatet_overlever_en_omstart(self, mal, tmp_path):
        """Ville feilet hvis notatet ikke sto i basen, eller en ny
        tilkobling (en omstart) ikke så det."""
        sti = tmp_path / "demo.db"
        shutil.copy(mal, sti)
        t = aapne_base(sti, kjoer_migrasjoner=False)
        SqliteNotatlager(t).skriv(AKSJE, TIDLIGERE, "Første notat", LAGET)
        t.close()
        t = aapne_base(sti, kjoer_migrasjoner=False)
        try:
            (notat,) = SqliteNotatlager(t).notater(AKSJE)
        finally:
            t.close()
        assert (notat.symbol, notat.dato, notat.tekst, notat.laget) == (AKSJE, TIDLIGERE, "Første notat", LAGET)

    @pytest.mark.parametrize(
        "verdier",
        [
            ("UKJENT", "2026-10-01", "x"),
            (AKSJE, "2026-10-01", ""),
            (AKSJE, "2026-10-01", "   "),
            (AKSJE, "2026-10-01", "x" * (MAKS_TEGN + 1)),
            (AKSJE, "01.10.2026", "x"),
            (AKSJE, "2026-10-1", "x"),
        ],
    )
    def test_tabellen_avviser(self, mal, tmp_path, verdier):
        """Ville feilet hvis tabellen godtok et ukjent symbol, en tom tekst,
        over 280 tegn eller en dato på en annen form enn ÅÅÅÅ-MM-DD."""
        sti = tmp_path / "demo.db"
        shutil.copy(mal, sti)
        t = sqlite3.connect(sti)
        try:
            with pytest.raises(sqlite3.IntegrityError):
                t.execute("INSERT INTO notat (symbol, dato, tekst, laget) VALUES (?, ?, ?, 'x')", verdier)
        finally:
            t.close()

    def test_280_tegn_er_lov(self, mal, tmp_path):
        """Ville feilet hvis grensen i 0012 var lavere enn MAKS_TEGN."""
        sti = tmp_path / "demo.db"
        shutil.copy(mal, sti)
        t = aapne_base(sti, kjoer_migrasjoner=False)
        try:
            assert len(SqliteNotatlager(t).skriv(AKSJE, SISTE, "x" * MAKS_TEGN, LAGET).tekst) == MAKS_TEGN
        finally:
            t.close()

    def test_0012_lager_bare_notat(self):
        """AD-16: ville feilet hvis migrasjonen endret en tabell eller
        trigger som finnes."""
        sql = (ROT / "src" / "migrasjoner" / "0012_notat.sql").read_text(encoding="utf-8")
        setninger = [s for s in re.findall(r"^(CREATE|ALTER|DROP|INSERT|UPDATE|DELETE)\b.*$", sql, re.M)]
        assert setninger and all(s == "CREATE" for s in setninger)
        assert set(re.findall(r"^CREATE (?:TABLE|INDEX|TRIGGER) (\w+)", sql, re.M)) == {
            "notat",
            "notat_symbol",
            "notat_kjent_aksje_insert",
            "notat_kjent_aksje_update",
        }


@pytest.fixture(params=["minne", "sqlite"])
def lager(request, mal, tmp_path):
    """Samme kontrakt for begge adapterne (AD-3)."""
    if request.param == "minne":
        yield MinneNotatlager([AKSJE, ANNEN])
        return
    sti = tmp_path / "demo.db"
    shutil.copy(mal, sti)
    t = aapne_base(sti, kjoer_migrasjoner=False)
    yield SqliteNotatlager(t)
    t.close()


class TestPorten:
    def test_er_porten(self, lager):
        assert isinstance(lager, Notatlager)

    def test_nyeste_notatdag_foerst(self, lager):
        """Spørsmål 1: ville feilet hvis notatene sto i en annen rekkefølge."""
        lager.skriv(AKSJE, TIDLIGERE, "eldst", LAGET)
        lager.skriv(AKSJE, SISTE, "nyest", LAGET)
        lager.skriv(AKSJE, SISTE, "nyest, lagret sist", LAGET.replace(hour=13))
        assert [n.tekst for n in lager.notater(AKSJE)] == ["nyest, lagret sist", "nyest", "eldst"]

    def test_slett_sletter_ikke_for_en_annen_aksje(self, lager):
        """Ville feilet hvis slett kunne slette et notat for en annen aksje."""
        notat = lager.skriv(AKSJE, SISTE, "mitt", LAGET)
        assert lager.slett(ANNEN, notat.id) is False
        assert [n.tekst for n in lager.notater(AKSJE)] == ["mitt"]
        assert lager.slett(AKSJE, notat.id) is True
        assert lager.notater(AKSJE) == []
        assert lager.slett(AKSJE, notat.id) is False

    def test_ukjent_aksje_avvises(self, lager):
        with pytest.raises(UgyldigNotat):
            lager.skriv("UKJENT", SISTE, "x", LAGET)

    def test_teksten_renskes(self, lager):
        """Spørsmål 2: ville feilet hvis mellomrom og linjeskift ble lagret."""
        assert lager.skriv(AKSJE, SISTE, "  to\n\nlinjer  ", LAGET).tekst == "to linjer"


class TestRens:
    @pytest.mark.parametrize("tekst", ["", "   ", "\n\t", "x" * (MAKS_TEGN + 1), None, 5])
    def test_avviser(self, tekst):
        with pytest.raises(UgyldigNotat):
            rens(tekst)

    def test_grensen_gjelder_teksten_etter_rensingen(self):
        assert rens("  " + "x" * MAKS_TEGN + "  ") == "x" * MAKS_TEGN


def test_en_aksje_som_er_tatt_ut_faar_ikke_nye_notater(mal, tmp_path):
    """Spørsmål 10: ville feilet hvis en aksje som er tatt ut, fikk nye notater."""
    sti = tmp_path / "demo.db"
    shutil.copy(mal, sti)
    t = aapne_base(sti, kjoer_migrasjoner=False)
    try:
        t.execute("UPDATE aksje SET ut = ? WHERE symbol = ?", (SISTE.isoformat(), AKSJE))
        t.commit()
        with pytest.raises(UgyldigNotat):
            SqliteNotatlager(t).skriv(AKSJE, TIDLIGERE, "x", LAGET)
    finally:
        t.close()


# --- B) Skjemaet og slettingen på aksjesiden ---------------------------------


class TestSkjemaet:
    @pytest.mark.parametrize(
        "adresse, dag", [(f"/aksje/{AKSJE}", SISTE), (f"/aksje/{AKSJE}?dag=2026-10-01", TIDLIGERE)]
    )
    def test_notatet_faar_dagen_siden_viser(self, klient, demobase, adresse, dag):
        """Spørsmål 3: ville feilet hvis notatet fikk en annen dag enn siden
        viste, eller skjemaet ikke sa dagen."""
        side = klient.get(adresse).data.decode("utf-8")
        skjemadag = re.search(r'<form class="nytt-notat".*?name="dag" value="([0-9-]+)"', side, re.S).group(1)
        assert skjemadag == dag.isoformat()
        assert "Notatet får datoen" in _tekst(_delen(side))
        svar = klient.post(f"/aksje/{AKSJE}/notat", data={"dag": skjemadag, "tekst": "Et notat"})
        assert svar.status_code == 303
        assert svar.headers["Location"] == adresse + "#mine-notater"
        assert [(s, d, t) for _, s, d, t, _ in _rader(demobase)] == [(AKSJE, dag.isoformat(), "Et notat")]

    @pytest.mark.parametrize(
        "data",
        [
            {"dag": "2026-10-03", "tekst": "lørdag"},
            {"dag": "2026-10-12", "tekst": "etter siste kurs"},
            {"dag": "2025-12-31", "tekst": "før første kurs"},
            {"dag": "2026-13-01", "tekst": "ingen dato"},
            {"dag": "", "tekst": "uten dag"},
            {"tekst": "uten dag"},
            {"dag": "2026-10-09", "tekst": ""},
            {"dag": "2026-10-09", "tekst": "x" * (MAKS_TEGN + 1)},
        ],
    )
    def test_avvist_skjema_skriver_ingenting(self, klient, demobase, data):
        """Ville feilet hvis en dag uten kurs for aksjen, en tom tekst eller
        en for lang tekst ble godtatt."""
        assert klient.post(f"/aksje/{AKSJE}/notat", data=data).status_code == 400
        assert _rader(demobase) == []

    def test_ukjent_aksje_gir_404(self, klient, demobase):
        assert klient.post("/aksje/UKJENT/notat", data={"dag": "2026-10-09", "tekst": "x"}).status_code == 404
        assert _rader(demobase) == []

    def test_en_annen_side_kan_ikke_skrive_eller_slette(self, klient, demobase):
        """Ville feilet hvis en annen side kunne skrive eller slette."""
        ond = {"Origin": "http://ond.example"}
        data = {"dag": "2026-10-09", "tekst": "x"}
        assert klient.post(f"/aksje/{AKSJE}/notat", data=data, headers=ond).status_code == 403
        assert _rader(demobase) == []
        assert (
            klient.post(f"/aksje/{AKSJE}/notat", data=data, headers={"Origin": "http://localhost"}).status_code == 303
        )
        (rad,) = _rader(demobase)
        assert klient.post(f"/aksje/{AKSJE}/notat/slett", data={"id": rad[0]}, headers=ond).status_code == 403
        assert len(_rader(demobase)) == 1

    def test_get_endrer_ingenting_og_post_bare_notat(self, klient, demobase):
        """AD-3: ville feilet hvis en GET endret noe, eller skjemaet skrev en
        annen tabell enn notat."""
        foer = _alle_andre_tabeller(demobase)
        klient.get(f"/aksje/{AKSJE}")
        assert _rader(demobase) == []
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-09", "tekst": "x"})
        (rad,) = _rader(demobase)
        klient.post(f"/aksje/{AKSJE}/notat/slett", data={"id": rad[0], "dag": "2026-10-09"})
        assert _alle_andre_tabeller(demobase) == foer

    def test_slett_sender_tilbake_til_samme_dag(self, klient, demobase):
        """Spørsmål 7: ville feilet hvis notatet ikke ble slettet, eller et
        notat for en annen aksje kunne slettes fra denne siden."""
        klient.post(f"/aksje/{ANNEN}/notat", data={"dag": "2026-10-09", "tekst": "annen"})
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-01", "tekst": "mitt"})
        annen_id, mitt_id = (rad[0] for rad in _rader(demobase))
        assert klient.post(f"/aksje/{AKSJE}/notat/slett", data={"id": annen_id}).status_code == 303
        assert len(_rader(demobase)) == 2
        svar = klient.post(f"/aksje/{AKSJE}/notat/slett", data={"id": mitt_id, "dag": "2026-10-01"})
        assert svar.headers["Location"] == f"/aksje/{AKSJE}?dag=2026-10-01#mine-notater"
        assert [rad[3] for rad in _rader(demobase)] == ["annen"]

    @pytest.mark.parametrize("notat_id", ["", "x", "-1", "1.0", "²"])
    def test_slett_med_ugyldig_id_gir_400(self, klient, demobase, notat_id):
        assert klient.post(f"/aksje/{AKSJE}/notat/slett", data={"id": notat_id}).status_code == 400

    def test_virker_i_den_ekte_versjonen(self, tmp_path, monkeypatch):
        """Ville feilet hvis notatene bare virket i demoen."""
        from test_fetch_prices import OEYEBLIKK_22_09, kjoer_23

        raa, base = tmp_path / "raa", tmp_path / "db" / "ose.db"
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        monkeypatch.setattr(lagring_sqlite, "BASE_STI", base)
        monkeypatch.delenv(app_modul.I_DEMO, raising=False)
        monkeypatch.setattr(app_modul, "naa", lambda: datetime(2026, 9, 23, 12, 0).astimezone())
        k = app_modul.app.test_client()
        side = k.get("/aksje/EQNR").data.decode("utf-8")
        dag = re.search(r'<form class="nytt-notat".*?name="dag" value="([0-9-]+)"', side, re.S).group(1)
        assert k.post("/aksje/EQNR/notat", data={"dag": dag, "tekst": "ekte"}).status_code == 303
        assert "ekte" in _tekst(_delen(k.get("/aksje/EQNR").data.decode("utf-8")))


# --- C) «Etterpå» under hvert notat ------------------------------------------


def _serie(*dager_og_kurser) -> list[Kursrad]:
    return [Kursrad(dato=d, slutt=s, justert_slutt=j, volum=1000) for d, s, j in dager_og_kurser]


D1, D2, D3 = date(2026, 10, 5), date(2026, 10, 6), date(2026, 10, 7)


class TestEtterpaa:
    def test_endringen_er_paa_justert_kurs(self):
        """FR-101: ville feilet hvis endringen var regnet på sluttkursen i
        stedet for den justerte."""
        serie = _serie((D1, 100.0, 80.0), (D2, 100.0, 90.0), (D3, 100.0, 88.0))
        etter = bygg_etterpaa(Notat(1, AKSJE, D1, "x", LAGET), serie, {D1: 200.0, D3: 210.0}, {}, D3, 2)
        assert etter.siste == D3
        assert etter.aksjen == pytest.approx(10.0)
        assert etter.indeksen == pytest.approx(5.0)
        assert endring({D1: 80.0, D3: 88.0}, D1, D3) == pytest.approx(10.0)

    def test_signalet_leses_og_regnes_aldri(self):
        """AD-7: ville feilet hvis «Etterpå» regnet signalet på nytt i stedet
        for å vise det som er lagret. Kursene her ville aldri gitt 3 av 3."""
        lagret = _vurdering(1, 1, 1)
        serie = _serie((D1, 100.0, 100.0), (D2, 100.0, 100.0), (D3, 100.0, 100.0))
        etter = bygg_etterpaa(
            Notat(1, AKSJE, D1, "x", LAGET), serie, None, {D1: lagret, D3: Grunn.SYMBOL_FEILET}, D3, 2
        )
        assert etter.paa_dagen.vurdering is lagret
        assert etter.paa_siste.vurdering is None and etter.paa_siste.tekst == "hentingen feilet"

    def test_notatdagen_er_siste_dag(self):
        """Spørsmål 5: ville feilet hvis siden viste en endring når det ikke
        finnes en dag med kurs etter notatdagen."""
        serie = _serie((D1, 100.0, 100.0), (D2, 100.0, 100.0))
        etter = bygg_etterpaa(Notat(1, AKSJE, D2, "x", LAGET), serie, {D2: 1.0}, {}, D3, 2)
        assert (etter.siste, etter.aksjen, etter.indeksen, etter.paa_siste) == (None, None, None, None)

    def test_grunnene_naar_en_kurs_mangler(self):
        """NFR-08: ville feilet hvis en manglende kurs ga et tall, ikke «–»
        med grunnen."""
        serie = _serie((D2, 100.0, 100.0), (D3, 100.0, 110.0))
        uten_dagen = bygg_etterpaa(Notat(1, AKSJE, D1, "x", LAGET), serie, {D1: 1.0, D3: 1.0}, {}, D3, 2)
        assert (uten_dagen.aksjen, uten_dagen.aksjen_grunn) == (None, INGEN_KURS_PAA_NOTATDAGEN)
        mangler = bygg_etterpaa(Notat(1, AKSJE, D2, "x", LAGET), serie, {D2: 1.0}, {}, D3, 2)
        assert (mangler.aksjen, mangler.indeksen, mangler.indeksen_grunn) == (
            pytest.approx(10.0),
            None,
            INDEKSEN_MANGLER_DAGEN,
        )
        uten_indeks = bygg_etterpaa(Notat(1, AKSJE, D2, "x", LAGET), serie, None, {}, D3, 2)
        assert uten_indeks.indeksen_grunn == INGEN_INDEKS

    def test_uten_vurderingene_staar_ingen_signal(self):
        """Ville feilet hvis vurderinger som ikke kunne leses, ble vist som
        «ikke vurdert»."""
        serie = _serie((D1, 100.0, 100.0), (D2, 100.0, 100.0))
        etter = bygg_etterpaa(Notat(1, AKSJE, D1, "x", LAGET), serie, None, None, D3, 2)
        assert etter.paa_dagen is None and etter.paa_siste is None


# Spørsmål 6: ord som sier at et notat traff eller bommet, eller som er råd.
ORDENE = ("riktig", "galt", "feil", "traff", "bom", "kjøp", "kjøpe", "selg", "selge", "bør")


class TestSiden:
    def test_etterpaa_paa_siden(self, klient, demobase):
        """Spørsmål 4: ville feilet hvis siden ikke viste endringen i aksjen
        og hovedindeksen og signalet for de to dagene."""
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-01", "tekst": "Notatet"})
        tekst = _tekst(_delen(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8")))
        assert "Etterpå" in tekst
        assert re.search(r"Aksjen fra torsdag 01\.10 til fredag 09\.10: [+-]?[0-9]+,[0-9]{2} %", tekst)
        assert re.search(r"Hovedindeksen \(DEMIX\) samme dager: [+-]?[0-9]+,[0-9]{2} %", tekst)
        assert re.search(r"Signalet torsdag 01\.10: .* [0-3] av 3", tekst)
        assert re.search(r"Signalet fredag 09\.10: .* [0-3] av 3", tekst)

    def test_samme_tall_som_basen(self, klient, demobase):
        """Ville feilet hvis endringen på siden ikke var regnet fra den
        justerte kursen i basen på de to dagene."""
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-01", "tekst": "Notatet"})
        c = sqlite3.connect(demobase)
        try:
            fra, til = (
                c.execute("SELECT justert_slutt FROM kurs WHERE symbol = ? AND dato = ?", (AKSJE, d)).fetchone()[0]
                for d in ("2026-10-01", "2026-10-09")
            )
        finally:
            c.close()
        forventet = app_modul.tall((til - fra) / fra * 100, "endring")
        assert f"til fredag 09.10: {forventet}" in _tekst(_delen(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8")))

    def test_ingen_ord_om_riktig_eller_galt_og_ingen_raad(self, klient, demobase):
        """NFR-06: ville feilet hvis delen brukte et av ordene i spørsmål 6.
        Notatet selv er brukerens tekst og telles ikke."""
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-01", "tekst": "NOTATTEKST"})
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-09", "tekst": "NOTATTEKST"})
        tekst = _tekst(_delen(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8"))).replace("NOTATTEKST", "")
        for ord_ in ORDENE:
            assert not re.search(rf"\b{ord_}\b", tekst, re.I), ord_

    def test_notatet_vises_som_tekst(self, klient, demobase):
        """Ville feilet hvis notatet ble vist som HTML."""
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-09", "tekst": "<b>fet</b>"})
        delen = _delen(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8"))
        assert "&lt;b&gt;fet&lt;/b&gt;" in delen and "<b>fet</b>" not in delen

    def test_uten_notater(self, klient, demobase):
        tekst = _tekst(_delen(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8")))
        assert "Ingen notater for" in tekst and "Etterpå" not in tekst


# --- D) Demoen, README-en og hjelpen ------------------------------------------


class TestDokumentene:
    def test_readme_og_hjelpen_nevner_notatene(self):
        """Regel 19: ville feilet hvis README-en eller hjelpen ikke nevnte
        notatene."""
        # Punktet i «Status» har høyst 20 ord (test_docker), så README-en sier
        # «notater» om aksjesiden, og hjelpen har navnet på delen.
        assert re.search(r"^- Aksjesiden: .*\bnotater$", (ROT / "README.md").read_text(encoding="utf-8"), re.M)
        assert "### Hva er «Mine notater»?" in (ROT / "docs" / "hjelp.md").read_text(encoding="utf-8")

    def test_demokommandoen_skriver_ingen_notater(self, demobase):
        """Spørsmål 9: ville feilet hvis demobasen kom med notater."""
        assert _rader(demobase) == []
