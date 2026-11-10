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
def demomal(tmp_path_factory):
    """Demobasen slik demokommandoen lager den, med eksemplene (tillegg 2)."""
    sti = tmp_path_factory.mktemp("demomal") / "demo.db"
    demo.lag_demobase(sti, skriv=lambda _: None)
    return sti


@pytest.fixture(scope="module")
def mal(demomal, tmp_path_factory):
    """Demobasen uten eksemplene, så testene begynner uten notater.
    Triggeren i 0012 sletter de tenkte kjøpene med notatene."""
    sti = tmp_path_factory.mktemp("tommal") / "demo.db"
    shutil.copy(demomal, sti)
    c = sqlite3.connect(sti)
    c.execute("DELETE FROM notat")
    c.commit()
    c.close()
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
            # Gjennomgangen (BH4): en dato som ikke finnes, og et tidspunkt som
            # ikke kan leses.
            (AKSJE, "2026-13-45", "x"),
            (AKSJE, "2026-02-30", "x"),
            (AKSJE, "2026-10-01", "x", "x"),
        ],
    )
    def test_tabellen_avviser(self, mal, tmp_path, verdier):
        """Ville feilet hvis tabellen godtok et ukjent symbol, en tom tekst,
        over 280 tegn, en dato som ikke finnes eller er på en annen form enn
        ÅÅÅÅ-MM-DD, eller et tidspunkt som ikke kan leses. Hver rad er gyldig
        utenom den ene verdien."""
        if len(verdier) == 3:
            verdier = (*verdier, LAGET.isoformat())
        sti = tmp_path / "demo.db"
        shutil.copy(mal, sti)
        t = sqlite3.connect(sti)
        try:
            with pytest.raises(sqlite3.IntegrityError):
                t.execute("INSERT INTO notat (symbol, dato, tekst, laget) VALUES (?, ?, ?, ?)", verdier)
        finally:
            t.close()

    def test_en_gyldig_rad_godtas(self, mal, tmp_path):
        """Ville feilet hvis CHECK-ene avviste en gyldig rad, så testen over
        bare viste at alt avvises."""
        sti = tmp_path / "demo.db"
        shutil.copy(mal, sti)
        t = sqlite3.connect(sti)
        try:
            t.execute(
                "INSERT INTO notat (symbol, dato, tekst, laget) VALUES (?, ?, ?, ?)",
                (AKSJE, "2026-10-01", "x", LAGET.isoformat()),
            )
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
        # Tillegget kl. 14:44: også de tenkte kjøpene og bryteren «Notater».
        assert set(re.findall(r"^CREATE (?:UNIQUE )?(?:TABLE|INDEX|TRIGGER) (\w+)", sql, re.M)) == {
            "notat",
            "notat_symbol",
            "notat_kjent_aksje_insert",
            "notat_kjent_aksje_update",
            "tenkt_kjoep",
            "tenkt_kjoep_ett_aapent",
            "tenkt_kjoep_notat_insert",
            "tenkt_kjoep_notat_update",
            "notat_slett_tenkt_kjoep",
            "notatvalg",
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
    # Gjennomgangen (BH9, ECH5): også bare tegn uten bredde.
    @pytest.mark.parametrize("tekst", ["", "   ", "\n\t", "\u200b", "\u200b \u2060", "x" * (MAKS_TEGN + 1), None, 5])
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
        vis = re.search(r'<form class="nytt-notat".*?name="vis" value="([^"]*)"', side, re.S).group(1)
        svar = klient.post(f"/aksje/{AKSJE}/notat", data={"dag": skjemadag, "vis": vis, "tekst": "Et notat"})
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
        klient.post(f"/aksje/{AKSJE}/notat/slett", data={"id": rad[0]})
        assert _alle_andre_tabeller(demobase) == foer

    def test_slett_sender_tilbake_til_samme_dag(self, klient, demobase):
        """Spørsmål 7: ville feilet hvis notatet ikke ble slettet, eller et
        notat for en annen aksje kunne slettes fra denne siden."""
        klient.post(f"/aksje/{ANNEN}/notat", data={"dag": "2026-10-09", "tekst": "annen"})
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-01", "tekst": "mitt"})
        annen_id, mitt_id = (rad[0] for rad in _rader(demobase))
        assert klient.post(f"/aksje/{AKSJE}/notat/slett", data={"id": annen_id}).status_code == 303
        assert len(_rader(demobase)) == 2
        svar = klient.post(f"/aksje/{AKSJE}/notat/slett", data={"id": mitt_id, "vis": "dag=2026-10-01"})
        assert svar.headers["Location"] == f"/aksje/{AKSJE}?dag=2026-10-01#mine-notater"
        assert [rad[3] for rad in _rader(demobase)] == ["annen"]

    # Gjennomgangen (BH3, ECH3): også en id SQLite ikke kan ta.
    @pytest.mark.parametrize("notat_id", ["", "x", "-1", "1.0", "²", "9" * 30])
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
# Tillegget kl. 14:44: også gevinst, tap og vant. «Noter et tenkt kjøp» og
# «tenkt salg» er navnet på knappene og er lov; «kjøp» alene som oppfordring
# er det ikke (NFR-06), så «tenkt(e) kjøp» tas bort før ordene telles.
ORDENE = (
    "riktig",
    "galt",
    "feil",
    "traff",
    "bom",
    "kjøp",
    "kjøpe",
    "selg",
    "selge",
    "bør",
    "gevinst",
    "tap",
    "vant",
)


def _uten_navnene(tekst: str) -> str:
    return re.sub(r"\btenkte? kjøp(et)?\b", "", tekst, flags=re.I)


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
        """Ville feilet hvis endringen på siden ikke var regnet fra kolonnen
        justert_slutt i basen på de to dagene. Demoen har justert lik slutt
        (gjennomgangen, VG2), så justert mot ujustert kurs dekkes av
        test_endringen_er_paa_justert_kurs."""
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
        tekst = _uten_navnene(tekst)
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
        # Punktene i «Status» er fulle (høyst 20 ord, og ordene testene krever),
        # så README-en nevner «Mine notater» ved bildene i knappen (flettingen
        # av main med «Status» 10.11), og hjelpen har et eget avsnitt.
        readme = (ROT / "README.md").read_text(encoding="utf-8")
        assert "«Mine notater» på aksjesiden" in readme and "Notatene samlet nederst i Min liste" in readme
        assert "### Hva er «Mine notater»?" in (ROT / "docs" / "hjelp.md").read_text(encoding="utf-8")

    def test_testene_begynner_uten_notater(self, demobase):
        """Malen for testene har ikke eksemplene fra demokommandoen."""
        assert _rader(demobase) == [] and _rader(demobase, "tenkt_kjoep") == []


# --- Etter gjennomgangen ------------------------------------------------------


def _skjemaet(side: str) -> dict:
    skjema = re.search(r'<form class="nytt-notat".*?</form>', side, re.S).group(0)
    return dict(re.findall(r'name="(dag|vis)" value="([^"]*)"', skjema))


class TestEtterGjennomgangen:
    @pytest.mark.parametrize(
        "adresse",
        [f"/aksje/{AKSJE}?periode=1-mnd", f"/aksje/{AKSJE}?dag=2026-10-09", f"/aksje/{AKSJE}?periode=3-mnd"],
    )
    def test_tilbake_til_samme_visning(self, klient, demobase, adresse):
        """ECH2, BH7, VG4: ville feilet hvis svaret etter lagring og sletting
        ikke gikk tilbake til samme periode eller dag."""
        felt = _skjemaet(klient.get(adresse).data.decode("utf-8"))
        svar = klient.post(f"/aksje/{AKSJE}/notat", data={**felt, "tekst": "x"})
        assert svar.headers["Location"] == adresse + "#mine-notater"
        (rad,) = _rader(demobase)
        svar = klient.post(f"/aksje/{AKSJE}/notat/slett", data={"id": rad[0], "vis": felt["vis"]})
        assert svar.headers["Location"] == adresse + "#mine-notater"

    @pytest.mark.parametrize("vis", ["periode=velg", "periode=ukjent", "dag=2026-02-30", "https://ond.example", "x"])
    def test_ukjent_visning_gir_standardvisningen(self, klient, demobase, vis):
        svar = klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-09", "vis": vis, "tekst": "x"})
        assert svar.headers["Location"] == f"/aksje/{AKSJE}#mine-notater"

    def test_dag_uten_kurs_har_ikke_skjemaet(self, klient, demobase):
        """ECH1: ville feilet hvis skjemaet sto på en dag uten kurs for aksjen,
        der lagringen ville blitt avvist."""
        delen = _delen(klient.get(f"/aksje/{AKSJE}?dag=2026-10-03").data.decode("utf-8"))
        assert 'class="nytt-notat"' not in delen
        assert "har ingen kurs for" in _tekst(delen)

    def test_etterpaa_med_vis_dagen_gaar_til_siste_dag(self, klient, demobase):
        """BH2: ville feilet hvis «Etterpå» på siden for en tidligere dag
        sluttet på den dagen i stedet for siste dag med kurser."""
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-09-01", "tekst": "x"})
        tekst = _tekst(_delen(klient.get(f"/aksje/{AKSJE}?dag=2026-10-01").data.decode("utf-8")))
        assert "Aksjen fra tirsdag 01.09 til fredag 09.10:" in tekst
        assert re.search(r"Hovedindeksen \(DEMIX\) samme dager: [+-]?[0-9]+,[0-9]{2} %", tekst)

    def test_signalet_paa_siden_er_det_som_er_lagret(self, klient, demobase):
        """BH11: ville feilet hvis siden viste en annen styrke eller retning
        enn raden i vurdering for dagene."""
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-01", "tekst": "x"})
        c = sqlite3.connect(demobase)
        try:
            lagret = {
                d: c.execute(
                    "SELECT styrke, retning FROM vurdering WHERE symbol = ? AND dato = ?", (AKSJE, d)
                ).fetchone()
                for d in ("2026-10-01", "2026-10-09")
            }
        finally:
            c.close()
        tekst = _tekst(_delen(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8")))
        for dag, navn in (("2026-10-01", "torsdag 01.10"), ("2026-10-09", "fredag 09.10")):
            styrke, retning = lagret[dag]
            assert re.search(rf"Signalet {navn}: \S+ {retning} .*? {styrke} av 3", tekst), (dag, tekst)

    def test_indeksen_som_ikke_kunne_leses_har_egen_grunn(self):
        """BH8: ville feilet hvis en indeks som ikke kunne leses, fikk grunnen
        for en indeks som ikke er hentet."""
        from etterpaa import INDEKSEN_KUNNE_IKKE_LESES

        serie = _serie((D1, 100.0, 100.0), (D2, 100.0, 100.0))
        etter = bygg_etterpaa(Notat(1, AKSJE, D1, "x", LAGET), serie, None, {}, D3, 2, indeks_feilet=True)
        assert etter.indeksen_grunn == INDEKSEN_KUNNE_IKKE_LESES

    def test_aksje_tatt_ut_paa_siden(self, klient, demobase):
        """VG3, spørsmål 10: ville feilet hvis en aksje som er tatt ut, fikk
        skjemaet eller nye notater, eller notatene ikke kunne slettes."""
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-01", "tekst": "før"})
        c = sqlite3.connect(demobase)
        c.execute("UPDATE aksje SET ut = ? WHERE symbol = ?", ("2026-10-12", AKSJE))
        c.commit()
        c.close()
        delen = _delen(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8"))
        assert 'class="nytt-notat"' not in delen and "før" in _tekst(delen)
        assert klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-09", "tekst": "x"}).status_code == 400
        (rad,) = _rader(demobase)
        assert klient.post(f"/aksje/{AKSJE}/notat/slett", data={"id": rad[0]}).status_code == 303
        assert _rader(demobase) == []

    def test_demobase_fra_foer_0012_vises_ikke(self, klient, demobase):
        """VG3, spørsmål 9: ville feilet hvis en demobase fra før 0012 ga en
        side med notater eller 500, ikke siden som ber om en ny demobase."""
        c = sqlite3.connect(demobase)
        c.execute("DROP TABLE notat")
        c.execute("DELETE FROM skjema_versjon WHERE versjon = 12")
        c.commit()
        c.close()
        svar = klient.get(f"/aksje/{AKSJE}")
        assert svar.status_code == 503
        assert "uv run python src/demo.py" in svar.data.decode("utf-8")
        assert klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-09", "tekst": "x"}).status_code == 503

    def test_notatene_som_ikke_kan_leses(self, klient, demobase, monkeypatch):
        """VG5: ville feilet hvis en feil i notatene tok ned hele siden."""

        def feiler(self, symbol):
            raise sqlite3.OperationalError("låst")

        monkeypatch.setattr(SqliteNotatlager, "notater", feiler)
        svar = klient.get(f"/aksje/{AKSJE}")
        assert svar.status_code == 200
        side = svar.data.decode("utf-8")
        assert "Notatene kan ikke leses fra basen nå." in side and "Signalet dag for dag" in side

    def test_ingen_raad_i_tekstene_for_grunnene(self):
        """VG1: ville feilet hvis en av tekstene delen kan vise når en kurs,
        indeksen eller signalet mangler, eller teksten i malen, brukte et av
        ordene i spørsmål 6."""
        import etterpaa
        from markedsoversikt import GRUNNTEKST, IKKE_BOERSDAG, IKKE_I_LISTA, IKKE_VURDERT

        mal = (ROT / "src" / "templates" / "aksje.html").read_text(encoding="utf-8")
        delen = mal[mal.index("{#- Story 8.21") : mal.index("{#- Story 2.7b (avgjørelsen")]
        # Tillegget kl. 14:44: notatet står i delmalen _notat.html.
        delen += (ROT / "src" / "templates" / "_notat.html").read_text(encoding="utf-8")
        tekster = [
            etterpaa.INGEN_KURS_PAA_NOTATDAGEN,
            etterpaa.INGEN_INDEKS,
            etterpaa.INDEKSEN_MANGLER_DAGEN,
            etterpaa.INDEKSEN_KUNNE_IKKE_LESES,
            IKKE_VURDERT,
            IKKE_I_LISTA,
            IKKE_BOERSDAG,
            *GRUNNTEKST.values(),
            re.sub(r"\{#.*?#\}", "", delen, flags=re.S),
        ]
        for tekst in tekster:
            for ord_ in ORDENE:
                assert not re.search(rf"\b{ord_}\b", _uten_navnene(tekst), re.I), (ord_, tekst[:80])

    def test_siste_dag_sier_at_det_ikke_er_dager_etter(self, klient, demobase):
        """Spørsmål 5 på siden: ville feilet hvis linja manglet."""
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-09", "tekst": "x"})
        tekst = _tekst(_delen(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8")))
        assert "Ingen børsdager med kurs etter notatdagen ennå." in tekst


# --- Tillegget kl. 14:44 (del E-G) og tillegg 2 kl. 15:57 (del H) -------------


def _kjoepsknapp(side: str) -> dict:
    """Feltene i skjemaet «Noter et tenkt kjøp» for det første notatet som har det."""
    treff = re.search(r'<form method="post" action="/aksje/[A-Z]+/notat/kjoep">(.*?)</form>', side, re.S)
    return dict(re.findall(r'name="(id|dag|vis)" value="([^"]*)"', treff.group(1))) if treff else {}


def _salgsknapp(side: str) -> dict:
    treff = re.search(r'<form method="post" action="/aksje/[A-Z]+/notat/salg">(.*?)</form>', side, re.S)
    return dict(re.findall(r'name="(id|dag|vis)" value="([^"]*)"', treff.group(1))) if treff else {}


def _vurdering_i_basen(sti: Path, symbol: str, dag: str):
    c = sqlite3.connect(sti)
    try:
        return c.execute(
            "SELECT trend, bevegelse, interesse FROM vurdering WHERE symbol = ? AND dato = ? AND grunn IS NULL",
            (symbol, dag),
        ).fetchone()
    finally:
        c.close()


class TestBryteren:
    def test_bryteren_staar_i_innstillinger_med_hjelpen(self, klient, demobase):
        """Del E: ville feilet hvis «Notater» manglet i Innstillinger, ikke var
        på fra start, eller sto uten «?» og teksten under."""
        side = klient.get("/innstillinger").data.decode("utf-8")
        assert 'value="vis_notater"' in side and "Vis notater" in side
        assert re.search(r'name="navn" value="vis_notater">\s*<input type="hidden" name="til" value="av">', side)
        assert 'popovertarget="hjelp-notatene"' in side and 'id="hjelp-notatene"' in side
        assert "Appen sier aldri om noe var riktig." in _tekst(side)

    def test_av_skjuler_notatene_og_sletter_ingenting(self, klient, demobase):
        """Del E: ville feilet hvis bryteren av viste notatene på aksjesiden
        eller i Min liste, eller slettet noe."""
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-09", "tekst": "x"})
        assert klient.post("/innstillinger", data={"navn": "vis_notater", "til": "av"}).status_code == 303
        assert 'class="notater"' not in klient.get(f"/aksje/{AKSJE}").data.decode("utf-8")
        assert 'id="mine-notater"' not in klient.get("/min-liste").data.decode("utf-8")
        assert len(_rader(demobase)) == 1
        klient.post("/innstillinger", data={"navn": "vis_notater", "til": "paa"})
        assert "x" in _tekst(_delen(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8")))

    def test_bryteren_lagres_i_notatvalg(self, klient, demobase):
        """Del E: ville feilet hvis valget ikke sto i basen."""
        klient.post("/innstillinger", data={"navn": "vis_notater", "til": "av"})
        assert _rader(demobase, "notatvalg") == [("vis_notater", 0)]


class TestMinListe:
    def test_alle_notatene_samlet_nyeste_foerst_med_lenke(self, klient, demobase):
        """Del F: ville feilet hvis Min liste ikke viste notatene for alle
        aksjene, nyeste først, med lenke til aksjen, eller hadde skjemaene."""
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-01", "tekst": "ELDST"})
        klient.post(f"/aksje/{ANNEN}/notat", data={"dag": "2026-10-09", "tekst": "NYEST"})
        side = klient.get("/min-liste").data.decode("utf-8")
        start = side.index('<section class="notater" id="mine-notater"')
        delen = side[start : side.index("</section>", start)]
        assert delen.index("NYEST") < delen.index("ELDST")
        assert f'href="/aksje/{ANNEN}"' in delen and f'href="/aksje/{AKSJE}"' in delen
        assert "<form" not in delen
        assert "Etterpå" in _tekst(delen)

    def test_menyen_faar_ingen_ny_knapp(self, klient, demobase):
        """Del F: ville feilet hvis stripa øverst fikk en knapp for notatene."""
        side = klient.get("/min-liste").data.decode("utf-8")
        stripa = side[: side.index("</nav>")]
        assert "otater" not in stripa


class TestTenkteKjoep:
    def _notat(self, klient, symbol=AKSJE, dag="2026-10-09"):
        klient.post(f"/aksje/{symbol}/notat", data={"dag": dag, "tekst": "x"})
        return _kjoepsknapp(klient.get(f"/aksje/{symbol}").data.decode("utf-8"))

    def test_kjoepet_lagrer_sjekkene_paa_siden_og_venter(self, klient, demobase):
        """Del G: ville feilet hvis kjøpet ikke lagret sjekkene slik de sto på
        siden, eller ikke sa at det venter, og at demoen ikke henter kurser."""
        felt = self._notat(klient)
        assert felt["dag"] == "2026-10-09"
        assert klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=felt).status_code == 303
        (rad,) = _rader(demobase, "tenkt_kjoep")
        assert rad[5:8] == _vurdering_i_basen(demobase, AKSJE, "2026-10-09")
        tekst = _tekst(_delen(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8")))
        assert "venter på sluttkursen. Demoen henter ikke kurser, så den kommer ikke her." in tekst

    def test_kjoep_bare_fra_siste_dag(self, klient, demobase):
        """Del G: ville feilet hvis et kjøp kunne noteres fra siden for en
        tidligere dag, med sjekkene for en annen dag."""
        felt = self._notat(klient)
        assert not _kjoepsknapp(klient.get(f"/aksje/{AKSJE}?dag=2026-10-01").data.decode("utf-8"))
        assert klient.post(f"/aksje/{AKSJE}/notat/kjoep", data={**felt, "dag": "2026-10-08"}).status_code == 400
        assert _rader(demobase, "tenkt_kjoep") == []

    def test_hoeyst_ett_aapent_kjoep_per_aksje(self, klient, demobase):
        """Del G: ville feilet hvis en aksje kunne få to åpne tenkte kjøp."""
        foerste = self._notat(klient)
        klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=foerste)
        klient.post(f"/aksje/{AKSJE}/notat", data={"dag": "2026-10-09", "tekst": "y"})
        side = klient.get(f"/aksje/{AKSJE}").data.decode("utf-8")
        assert not _kjoepsknapp(side)
        andre = max(rad[0] for rad in _rader(demobase))
        svar = klient.post(f"/aksje/{AKSJE}/notat/kjoep", data={"id": andre, "dag": "2026-10-09"})
        assert svar.status_code == 400
        assert len(_rader(demobase, "tenkt_kjoep")) == 1

    def test_salget_foerst_naar_kjoepet_har_sluttkursen(self, klient, demobase):
        """Del G: ville feilet hvis et salg kunne noteres før kjøpet hadde
        fått sluttkursen."""
        felt = self._notat(klient)
        klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=felt)
        assert not _salgsknapp(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8"))
        assert klient.post(f"/aksje/{AKSJE}/notat/salg", data=felt).status_code == 400

    def test_en_aksje_som_er_tatt_ut_faar_ikke_kjoep(self, klient, demobase):
        felt = self._notat(klient)
        c = sqlite3.connect(demobase)
        c.execute("UPDATE aksje SET ut = ? WHERE symbol = ?", ("2026-10-12", AKSJE))
        c.commit()
        c.close()
        assert klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=felt).status_code == 400
        assert _rader(demobase, "tenkt_kjoep") == []

    def test_slettes_notatet_slettes_kjoepet(self, klient, demobase):
        """Spørsmål 17: ville feilet hvis et tenkt kjøp ble liggende uten
        notatet, eller knappen ikke sa at kjøpet slettes med."""
        felt = self._notat(klient)
        klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=felt)
        assert "Slett notatet og det tenkte kjøpet" in klient.get(f"/aksje/{AKSJE}").data.decode("utf-8")
        klient.post(f"/aksje/{AKSJE}/notat/slett", data={"id": felt["id"]})
        assert _rader(demobase) == [] and _rader(demobase, "tenkt_kjoep") == []

    def test_tabellen_har_ingen_kurs(self, mal, tmp_path):
        """Spørsmål 15: ville feilet hvis kursen ble lagret ved trykket, så
        prosenten ikke fulgte serien når den hentes på nytt eller justeres."""
        c = sqlite3.connect(mal)
        try:
            kolonnene = {rad[1] for rad in c.execute("PRAGMA table_info(tenkt_kjoep)")}
        finally:
            c.close()
        assert not any("kurs" in k or "slutt" in k or "pris" in k for k in kolonnene), kolonnene


def _kjoep(etter: date, salg_etter: date | None = None):
    from notater import TenktKjoep

    return TenktKjoep(
        1,
        1,
        AKSJE,
        LAGET,
        etter,
        (1, 0, 0),
        LAGET if salg_etter else None,
        salg_etter,
        (0, -1, 0) if salg_etter else None,
    )


D4, D5 = date(2026, 10, 8), date(2026, 10, 9)


class TestHandelen:
    def test_kursen_er_den_foerste_etter_trykket(self):
        """Spørsmål 15: ville feilet hvis kjøpet fikk kursen fra dagen for
        trykket eller en senere dag enn den første etter."""
        from etterpaa import bygg_handelen

        serie = _serie((D1, 1.0, 100.0), (D2, 1.0, 110.0), (D3, 1.0, 121.0))
        h = bygg_handelen(_kjoep(D1), serie, {D2: 10.0, D3: 11.0})
        assert (h.kjoepsdag, h.til) == (D2, D3)
        assert h.aksjen == pytest.approx(10.0) and h.indeksen == pytest.approx(10.0)
        assert h.kan_selges and h.dager is None

    def test_salget_og_dagene(self):
        """Del G: ville feilet hvis endringen etter salget ikke gikk fra
        kjøpsdagen til salgsdagen, eller dagene var talt feil."""
        from etterpaa import bygg_handelen

        serie = _serie((D1, 1.0, 100.0), (D2, 1.0, 100.0), (D3, 1.0, 105.0), (D4, 1.0, 120.0), (D5, 1.0, 130.0))
        h = bygg_handelen(_kjoep(D1, D3), serie, None)
        assert (h.kjoepsdag, h.salgsdag, h.til, h.dager) == (D2, D4, D4, 2)
        assert h.aksjen == pytest.approx(20.0) and h.indeksen is None

    def test_venter_og_justert_serie(self):
        """Spørsmål 15: ville feilet hvis kjøpet hadde en kurs før serien har
        en dag etter trykket, eller prosenten ikke fulgte en justert serie."""
        from etterpaa import bygg_handelen

        serie = _serie((D1, 1.0, 100.0), (D2, 1.0, 110.0))
        assert bygg_handelen(_kjoep(D2), serie, None).venter_paa_kjoepet
        justert = _serie((D1, 1.0, 50.0), (D2, 1.0, 50.0), (D3, 1.0, 60.5))
        assert bygg_handelen(_kjoep(D1), justert, None).aksjen == pytest.approx(21.0)

    def test_sjekkene_som_brikker(self):
        from etterpaa import brikkene

        assert brikkene((1, 0, -1)) == (("T", "trend", "+1"), ("B", "bevegelse", "0"), ("I", "interesse", "-1"))
        assert brikkene(None) == ()


class TestFjern:
    def test_fjern_sier_foerst_at_kursene_stopper(self, klient, demobase):
        """Del G: ville feilet hvis en aksje med et åpent tenkt kjøp ble tatt
        ut av lista uten at appen først sa at kursene for den stopper."""
        felt = TestTenkteKjoep()._notat(klient)
        klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=felt)
        foer = _rader(demobase, "oenske")
        svar = klient.post("/fjern", data={"symbol": AKSJE, "tilbake": "oversikten"})
        assert svar.status_code == 200
        assert "hentes ingen kurser for den fra og med hentingen i kveld" in _tekst(svar.data.decode("utf-8"))
        assert _rader(demobase, "oenske") == foer
        svar = klient.post("/fjern", data={"symbol": AKSJE, "tilbake": "oversikten", "bekreftet": "1"})
        assert svar.status_code == 303 and len(_rader(demobase, "oenske")) == len(foer) + 1

    def test_bytt_ut_sier_det_ogsaa(self, klient, demobase):
        felt = TestTenkteKjoep()._notat(klient)
        klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=felt)
        assert "har et åpent tenkt kjøp" in klient.get(f"/folg?bytt={AKSJE}").data.decode("utf-8")


class TestDemoen:
    @pytest.fixture
    def demoklient(self, demomal, monkeypatch):
        sti = demo_sti()
        sti.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(demomal, sti)
        monkeypatch.setenv(app_modul.I_DEMO, "1")
        monkeypatch.delenv(app_modul.I_DOCKER, raising=False)
        monkeypatch.setattr(app_modul, "naa", lambda: LAGET)
        return app_modul.app.test_client()

    def test_eksemplene_har_tall_og_ett_aapent_og_ett_avsluttet_kjoep(self, demoklient, demomal):
        """Tillegg 2: ville feilet hvis demoen manglet notater fra tidligere
        dager med tall under «Etterpå», eller ett åpent og ett avsluttet tenkt
        kjøp med sjekkene begge gangene."""
        kjoepene = _rader(demomal, "tenkt_kjoep")
        aapne = [k for k in kjoepene if k[8] is None]
        lukkede = [k for k in kjoepene if k[8] is not None]
        assert len(aapne) == 1 and len(lukkede) == 1
        assert all(k[5] is not None for k in kjoepene) and lukkede[0][10] is not None
        for symbol in {rad[1] for rad in _rader(demomal)}:
            tekst = _tekst(_delen(demoklient.get(f"/aksje/{symbol}").data.decode("utf-8")))
            assert re.search(r"Aksjen fra .* til fredag 09\.10: [+-]?[0-9]+,[0-9]{2} %", tekst), symbol
            assert "Eksempeltall" in tekst
        side = _tekst(demoklient.get(f"/aksje/{AKSJE}").data.decode("utf-8"))
        assert re.search(r"Salgsdag .*\d+ børsdager etter\. Sjekkene på siden da salget ble notert: T", side)
        assert "Aksjen fra kjøpet til salget:" in side

    def test_eksemplene_gir_ingen_raad(self, demomal):
        """Tillegg 2, NFR-06: ville feilet hvis en eksempeltekst brukte et av
        ordene i spørsmål 6 og tillegget, og alle er merket som eksempel."""
        for rad in _rader(demomal):
            tekst = _uten_navnene(rad[3])
            assert tekst.startswith("Eksempel:")
            for ord_ in ORDENE:
                assert not re.search(rf"\b{ord_}\b", tekst, re.I), (ord_, rad[3])

    def test_notatene_samlet_i_min_liste_i_demoen(self, demoklient, demomal):
        side = demoklient.get("/min-liste").data.decode("utf-8")
        assert side.count('<li class="notat">') == len(_rader(demomal))

    def test_ingen_kronebeloep(self, demoklient):
        """Tillegget kl. 14:44: ville feilet hvis notatene viste et kronebeløp."""
        for adresse in (f"/aksje/{AKSJE}", "/min-liste"):
            side = demoklient.get(adresse).data.decode("utf-8")
            start = side.index('<section class="notater"')
            delen = _tekst(side[start : side.index("</section>", start)])
            assert not re.search(r"\b(kr|NOK|kroner)\b", delen), adresse


# --- Etter gjennomgangen av tilleggene ---------------------------------------


MAN, TIR, ONS, FRE, LOER = (
    date(2026, 10, 12),
    date(2026, 10, 13),
    date(2026, 10, 14),
    date(2026, 10, 9),
    date(2026, 10, 10),
)


class TestSluttkursenEtter:
    @pytest.mark.parametrize(
        "siste_kurs, i_dag, etter",
        [
            # Tirsdag før kveldshentingen: tirsdagens sluttkurs.
            (MAN, TIR, MAN),
            # Tirsdag etter kveldshentingen: onsdagens.
            (TIR, TIR, TIR),
            # Mandag, med fredag som siste kurs: mandagens.
            (FRE, MAN, FRE),
            # Lørdag: mandagens.
            (FRE, LOER, FRE),
            # Hentingen henger etter: aldri en dag før børsdagen før trykket.
            (FRE, ONS, TIR),
        ],
    )
    def test_regelen_for_neste_sluttkurs(self, siste_kurs, i_dag, etter):
        """VG1, BH1, spørsmål 15: ville feilet hvis dagen sluttkursen må være
        etter, var dagen for trykket, en dag før børsdagen før trykket, eller
        ikke den siste dagen med kurs."""
        assert app_modul._sluttkursen_etter([date(2026, 10, 1), siste_kurs], i_dag) == etter

    def test_ruta_lagrer_dagen(self, klient, demobase):
        """VG1: ville feilet hvis ruta lagret en annen dag enn regelen gir.
        Klokka i testen er tirsdag 13.10, og demoserien slutter fredag 09.10."""
        felt = TestTenkteKjoep()._notat(klient)
        klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=felt)
        (rad,) = _rader(demobase, "tenkt_kjoep")
        assert rad[4] == "2026-10-12"


def _kjoep_i_basen(sti: Path, notat_id: int, etter: str) -> None:
    """Et tenkt kjøp med en dag i demoserien, som om det var notert før."""
    c = sqlite3.connect(sti)
    c.execute(
        "INSERT INTO tenkt_kjoep (notat, symbol, kjoept, kjoep_etter, kjoep_trend, kjoep_bevegelse, kjoep_interesse)"
        " VALUES (?, ?, ?, ?, 1, 0, 0)",
        (notat_id, AKSJE, LAGET.isoformat(), etter),
    )
    c.commit()
    c.close()


class TestSalgetGjennomRuta:
    def test_salget_lagrer_sjekkene_og_dagen(self, klient, demobase):
        """VG2, BH2: ville feilet hvis knappen for salget manglet når kjøpet
        har sluttkursen, eller salget lagret kjøpets sjekker eller en annen
        dag enn regelen gir."""
        felt = TestTenkteKjoep()._notat(klient)
        _kjoep_i_basen(demobase, int(felt["id"]), "2026-10-07")
        salget = _salgsknapp(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8"))
        assert salget and salget["id"] == felt["id"]
        assert klient.post(f"/aksje/{AKSJE}/notat/salg", data=salget).status_code == 303
        (rad,) = _rader(demobase, "tenkt_kjoep")
        assert rad[9] == "2026-10-12"
        assert rad[10:13] == _vurdering_i_basen(demobase, AKSJE, "2026-10-09")
        tekst = _tekst(_delen(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8")))
        assert "Tenkt salg notert" in tekst and "venter på sluttkursen" in tekst

    def test_dobbeltklikk_skriver_ikke_to_ganger(self, klient, demobase):
        """ECH3: ville feilet hvis et nytt trykk på samme knapp ga 400 eller en
        ny rad."""
        felt = TestTenkteKjoep()._notat(klient)
        assert klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=felt).status_code == 303
        assert klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=felt).status_code == 303
        assert len(_rader(demobase, "tenkt_kjoep")) == 1


class TestFjernesIKveld:
    def test_ingen_kjoep_for_en_aksje_som_fjernes(self, klient, demobase):
        """ECH1, BH3: ville feilet hvis et kjøp kunne noteres for en aksje som
        tas ut før kursene hentes i kveld."""
        felt = TestTenkteKjoep()._notat(klient)
        assert klient.post("/fjern", data={"symbol": AKSJE, "tilbake": "oversikten"}).status_code == 303
        side = klient.get(f"/aksje/{AKSJE}").data.decode("utf-8")
        assert not _kjoepsknapp(side) and "fjernes fra lista ved hentingen i kveld" in _tekst(side)
        assert klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=felt).status_code == 400
        assert _rader(demobase, "tenkt_kjoep") == []

    def test_bekreftelsen_sier_fra_og_med_i_kveld(self, klient, demobase):
        """ECH1, BH7: ville feilet hvis siden sa at kjøpet får kursen."""
        felt = TestTenkteKjoep()._notat(klient)
        klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=felt)
        tekst = _tekst(klient.post("/fjern", data={"symbol": AKSJE, "tilbake": "oversikten"}).data.decode("utf-8"))
        assert "fra og med hentingen i kveld" in tekst and "får aldri sluttkursen" in tekst

    def test_de_ferdige_listene_sier_det(self, klient, demobase):
        """VG3, BH13: ville feilet hvis en ferdig liste som tar ut en aksje med
        et åpent kjøp, ikke sa fra før knappen."""
        felt = TestTenkteKjoep()._notat(klient)
        klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=felt)
        assert f"{AKSJE} har et åpent tenkt kjøp. Når den fjernes" in _tekst(
            klient.get("/min-liste").data.decode("utf-8")
        )


class TestEtterGjennomgangenAvTilleggene:
    def test_bryteren_sletter_ikke_kjoepene(self, klient, demobase):
        """VG4: ville feilet hvis bryteren av slettet et tenkt kjøp."""
        felt = TestTenkteKjoep()._notat(klient)
        klient.post(f"/aksje/{AKSJE}/notat/kjoep", data=felt)
        klient.post("/innstillinger", data={"navn": "vis_notater", "til": "av"})
        assert len(_rader(demobase, "tenkt_kjoep")) == 1

    def test_delen_staar_under_grafen_og_over_historikken(self, klient, demobase):
        """VG7, spørsmål 13: ville feilet hvis «Mine notater» sto et annet sted."""
        side = klient.get(f"/aksje/{AKSJE}").data.decode("utf-8")
        assert side.index('id="ki-tittel"') < side.index('id="mine-notater"') < side.index('id="signalet-dag-for-dag"')

    def test_base_uten_notatvalg(self, klient, demobase):
        """VG7: ville feilet hvis bryteren kunne trykkes, eller lagringen ga
        500, i en base uten tabellen."""
        c = sqlite3.connect(demobase)
        c.execute("DROP TABLE notatvalg")
        c.commit()
        c.close()
        side = klient.get("/innstillinger").data.decode("utf-8")
        assert re.search(r'<span class="navn">Vis notater</span>', side)
        knapp = re.search(r'value="vis_notater">.*?<button([^>]*)>', side, re.S).group(1)
        assert "disabled" in knapp
        assert klient.post("/innstillinger", data={"navn": "vis_notater", "til": "av"}).status_code == 404

    def test_kolonnene_i_tenkt_kjoep(self, mal):
        """BH12, spørsmål 15: ville feilet med en kolonne for kursen eller en
        verdi ved trykket."""
        c = sqlite3.connect(mal)
        try:
            kolonnene = {rad[1] for rad in c.execute("PRAGMA table_info(tenkt_kjoep)")}
        finally:
            c.close()
        assert kolonnene == {
            "id",
            "notat",
            "symbol",
            "kjoept",
            "kjoep_etter",
            "kjoep_trend",
            "kjoep_bevegelse",
            "kjoep_interesse",
            "solgt",
            "salg_etter",
            "salg_trend",
            "salg_bevegelse",
            "salg_interesse",
        }

    def test_ordene_med_kjoep_og_salg_paa_siden(self, klient, demobase):
        """BH14: ville feilet hvis tekstene ved et kjøp og et salg på siden
        brukte et av ordene."""
        felt = TestTenkteKjoep()._notat(klient)
        _kjoep_i_basen(demobase, int(felt["id"]), "2026-10-07")
        klient.post(f"/aksje/{AKSJE}/notat/salg", data=_salgsknapp(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8")))
        tekst = _uten_navnene(_tekst(_delen(klient.get(f"/aksje/{AKSJE}").data.decode("utf-8"))).replace(" x ", " "))
        for ord_ in ORDENE:
            assert not re.search(rf"\b{ord_}\b", tekst, re.I), ord_

    def test_demoeksemplene_er_notert_etter_hentingen(self, demomal):
        """ECH2, BH8: ville feilet hvis et eksempel var notert før kursen for
        dagen var hentet, så dagen ikke stemte med regelen for neste sluttkurs."""
        for rad in _rader(demomal, "tenkt_kjoep"):
            kjoept = datetime.fromisoformat(rad[3])
            assert (kjoept.hour, kjoept.minute) >= (22, 30) and rad[4] == kjoept.date().isoformat()
            if rad[8]:
                solgt = datetime.fromisoformat(rad[8])
                assert (solgt.hour, solgt.minute) >= (22, 30) and rad[9] == solgt.date().isoformat()
