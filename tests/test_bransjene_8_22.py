"""Story 8.22, del A: faste bransjer - svaret 10.11 kl. 13:38, 14:43 og 15:22.

Spesifikasjonen er spec-8-22-foelg-en-aksje-og-min-liste.md. Hver test lager
sin egen base under tmp_path (regel 22), og ingen test gjør nettkall (AD-8).
"""

import hashlib
from collections import Counter
from datetime import datetime

import app as app_modul
import ferdige_lister
import valg
from lagring_sqlite import aapne_base
from test_fetch_prices import OEYEBLIKK_22_09, kjoer_23
from test_valg import FASTE, faste_bransjer, klient, lager, med_boersen, stier  # noqa: F401  (fiksturene)

DEMOEN = {"HVLK": "Kraft", "NRDE": "Eiendom"}
ANTALLET = {
    "Energi": 57,
    "Finans": 50,
    "Industri": 34,
    "Teknologi": 32,
    "Shipping": 27,
    "Helse": 21,
    "Sjømat": 20,
    "Materialer": 17,
    "Forbruk": 15,
    "Kraft": 9,
    "Eiendom": 7,
    "Konsum": 4,
    "Telekom": 2,
}
SHA256 = "302e28433bf582ec9abad65ffde06c2dbcd533cd6130713990e2fa3ed0c6dec9"


def _ekte() -> dict[str, str]:
    """BRANSJE uten demoen og de oppdiktede tickerne fiksturen legger til."""
    return {k: v for k, v in ferdige_lister.BRANSJE.items() if k not in DEMOEN and k not in FASTE}


class TestTabellen:
    def test_de_295_med_antallet_og_sha256_fra_instruksjonen(self):
        """Ville feilet hvis en aksje manglet, en bransje var endret, eller
        en aksje var lagt til, etter kontrollsjekken 10.11 kl. 14:43 og 15:22."""
        ekte = _ekte()
        assert len(ekte) == 295
        assert Counter(ekte.values()) == ANTALLET
        linjer = "".join(sorted(f"{k};{v}\n" for k, v in ekte.items()))
        assert hashlib.sha256(linjer.encode("utf-8")).hexdigest() == SHA256

    def test_multi_og_scoin_er_ute_og_demoen_staar_som_foer(self):
        """Svaret kl. 14:43 (MULTI, fusjon) og kl. 15:22 (SCOIN, under
        avvikling). Ville feilet hvis en av dem kunne følges, eller linjene
        for demoen var endret."""
        assert "MULTI" not in ferdige_lister.BRANSJE and "SCOIN" not in ferdige_lister.BRANSJE
        assert {k: ferdige_lister.BRANSJE[k] for k in DEMOEN} == DEMOEN
        assert ferdige_lister.fast_bransje("SKRH") == "Helse"

    def test_de_15_har_samme_bransje_som_i_lista(self):
        """Svar 2 kl. 16:25: de 15 har bransjen fra designregler.md §4. Ville
        feilet hvis en av dem fikk en annen bransje enn i AKSJEUNIVERS."""
        from kursdata import AKSJEUNIVERS

        assert all(ferdige_lister.BRANSJE[a.symbol] == a.sektor for a in AKSJEUNIVERS)


class TestFoelg:
    def test_en_aksje_uten_bransje_avvises_med_grunnen(self, klient, stier):  # noqa: F811
        """Spørsmål 1: ville feilet hvis en aksje som ikke står i BRANSJE,
        som MULTI, kunne følges med en bransje fra skjemaet."""
        med_boersen(stier[1], [("MULTI", "Multi ASA")])
        side = klient.get("/folg?kode=MULTI").data.decode("utf-8")
        assert "har ingen bransje i lista over Oslo Børs, så den kan ikke følges." in side
        assert 'action="/folg"' not in side.split("<main>")[1]
        svar = klient.post("/folg", data={"kode": "MULTI", "sektor": "Finans"})
        assert svar.status_code == 303 and "ingen+bransje" in svar.headers["Location"]
        t = aapne_base(stier[1])
        try:
            assert t.execute("SELECT count(*) FROM oenske").fetchone()[0] == 0
        finally:
            t.close()

    def test_en_aksje_appen_har_fulgt_beholder_bransjen_i_aksje(self, stier, monkeypatch):  # noqa: F811
        """Spørsmål 1: ville feilet hvis en aksje som er tatt ut og ikke står
        i BRANSJE, ikke kunne følges igjen."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        monkeypatch.setattr(ferdige_lister, "BRANSJE", {})
        t = aapne_base(base)
        try:
            assert ferdige_lister.bransjen(t, "DNB") == "Finans"
            assert ferdige_lister.bransjen(t, "FINNES_IKKE") is None
            assert ferdige_lister.bransjen(None, "DNB") is None
        finally:
            t.close()


class TestHentingen:
    def test_et_gammelt_oenske_om_multi_avvises(self, stier, monkeypatch):  # noqa: F811
        """Gjennomgangen (BH3, ECH3, ECH4): ville feilet hvis et ønske fra før
        8.22 om å følge MULTI ble tatt inn med bransjen brukeren valgte, eller
        MULTI kunne følges med en bransje i aksje."""
        from datetime import date

        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        med_boersen(base, [("MULTI", "Multi ASA")])
        t = aapne_base(base)
        try:
            with t:
                t.execute(
                    "INSERT INTO oenske (handling, symbol, navn, sektor, laget) "
                    "VALUES ('folg', 'MULTI', 'Multi ASA', 'Finans', '2026-11-09T12:00:00+00:00')"
                )
            linjer = valg.ta_i_bruk(t, date(2026, 9, 23))
            assert "MULTI er ikke tatt inn: aksjen kan ikke følges." in linjer
            assert t.execute("SELECT count(*) FROM aksje WHERE symbol = 'MULTI'").fetchone()[0] == 0
            assert "kan ikke følges" in t.execute("SELECT avvist FROM oenske WHERE symbol = 'MULTI'").fetchone()[0]
            monkeypatch.setattr(ferdige_lister, "BRANSJE", {})
            assert ferdige_lister.bransjen(t, "MULTI") is None
            t.execute(
                "INSERT INTO aksje (symbol, ticker, navn, sektor) VALUES ('MULTI', 'MULTI.OL', 'Multi ASA', 'Finans')"
            )
            assert ferdige_lister.bransjen(t, "MULTI") is None
            assert "MULTI" not in {a.kode for a in ferdige_lister.foelgbare(t, set(), {})}
        finally:
            t.close()

    def test_oensket_tas_i_bruk_med_den_faste_bransjen(self, stier):  # noqa: F811
        """Spørsmål 3: ville feilet hvis hentingen skrev bransjen fra ønsket,
        også for et ønske som ble laget før 8.22, med en annen bransje."""
        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        med_boersen(base)
        l = lager(base)
        l.folg("NYB", "Kraft")  # NYB er Helse i FASTE
        l._t.close()
        t = aapne_base(base)
        try:
            from datetime import date

            valg.ta_i_bruk(t, date(2026, 9, 23))
            assert t.execute("SELECT sektor FROM aksje WHERE symbol = 'NYB'").fetchone() == ("Helse",)
        finally:
            t.close()

    def test_en_egen_aksje_i_lista_faar_den_faste_bransjen(self, stier, monkeypatch):  # noqa: F811
        """Spørsmål 3: ville feilet hvis en egen aksje som alt var tatt inn
        med en annen bransje, beholdt den, eller hvis en av de 15 ble rørt."""
        from datetime import date

        raa, base = stier
        kjoer_23(raa, base, OEYEBLIKK_22_09)
        med_boersen(base)
        l = lager(base)
        l.folg("NYA", "Kraft")
        l._t.close()
        t = aapne_base(base)
        try:
            valg.ta_i_bruk(t, date(2026, 9, 23))
            monkeypatch.setitem(ferdige_lister.BRANSJE, "NYA", "Teknologi")
            monkeypatch.setitem(ferdige_lister.BRANSJE, "DNB", "Teknologi")
            linjer = valg.ta_i_bruk(t, date(2026, 9, 24))
            assert t.execute("SELECT sektor FROM aksje WHERE symbol = 'NYA'").fetchone() == ("Teknologi",)
            assert t.execute("SELECT sektor FROM aksje WHERE symbol = 'DNB'").fetchone() == ("Finans",)
            assert linjer == ["NYA har fått bransjen Teknologi fra kontrollsjekken (var Kraft)."]
            assert valg.ta_i_bruk(t, date(2026, 9, 25)) == []
            # Gjennomgangen (VG5): en egen aksje som er tatt ut, røres ikke.
            t.execute("UPDATE aksje SET ut = '2026-09-26' WHERE symbol = 'NYA'")
            monkeypatch.setitem(ferdige_lister.BRANSJE, "NYA", "Helse")
            assert valg.ta_i_bruk(t, date(2026, 9, 27)) == []
            assert t.execute("SELECT sektor FROM aksje WHERE symbol = 'NYA'").fetchone() == ("Teknologi",)
        finally:
            t.close()


def test_siden_viser_den_faste_bransjen_for_et_oenske_som_venter(klient, stier, monkeypatch):  # noqa: F811
    """Spørsmål 3: ville feilet hvis «Dine egne aksjer» viste bransjen fra
    et ønske laget før 8.22 i stedet for den faste."""
    l = lager(stier[1])
    l.folg("NYB", "Kraft")
    l._t.close()
    side = klient.get("/").data.decode("utf-8")
    rad = side.split('<li class="egen-rad">')[1].split("</li>")[0]
    assert "</svg>Helse</span>" in rad and "Kraft" not in rad


def test_demoen_foelger_med_den_faste_bransjen(tmp_path, monkeypatch):
    """Spørsmål 2: ville feilet hvis de tre oppdiktede uten linje i BRANSJE
    ikke kunne følges i demoen."""
    import shutil

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
    klient_ = app_modul.app.test_client()
    for kode, bransje in (("SKRH", "Helse"), ("TNDT", "Teknologi"), ("VKVF", "Forbruk"), ("HVLK", "Kraft")):
        assert f"</svg>{bransje}</p>" in klient_.get(f"/folg?kode={kode}").data.decode("utf-8"), kode
    assert klient_.post("/folg", data={"kode": "TNDT"}).status_code == 303
    t = aapne_base(sti)
    try:
        assert t.execute("SELECT sektor FROM oenske WHERE symbol = 'TNDT'").fetchone() == ("Teknologi",)
    finally:
        t.close()
