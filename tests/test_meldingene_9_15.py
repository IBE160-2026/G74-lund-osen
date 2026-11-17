"""Story 9.15: meldingene etter v1.1 og det som ikke brukes.

D1-D4 (spoersmaal 10 i 9.14): meldingene fra hentingen og docstringen i
tilstand.py sa at en dag uten kveldsrad ikke regnes paa nytt. Fra 2.17 regner
siste steg i en henting signalet i ettertid for en dag som ikke lenger er
inneveerende boersdag (regn_signalet_i_ettertid i finally i kjoer). Hver test
feilet mot teksten foer rettingen.

D5 og D6 (spoersmaal 11 i 9.14): to navn som ingenting brukte, er tatt bort.
Ingen kall, ingen noekkel, og bare testbaser i tmp_path (regel 22).
"""

import re
from datetime import date

import pytest

import dagsgrunnlag
import fetch_prices as fp
import notater
import tilstand
from test_fetch_prices import OEYEBLIKK_22_09, lag_bilde, stier, uten_noekkel_og_nett  # noqa: F401

DATO = date(2026, 9, 22)


class TestMeldingene:
    def test_d1_stoppet_ved_midnatt_sier_at_dagen_faar_signalet_i_ettertid(self):
        """Ville feilet med «datoen regnes ikke paa nytt» fra foer 2.17."""
        ut = []
        fp._stoppet_ved_midnatt(DATO, 3, ut.append)
        tekst = " ".join(ut)
        assert "regnes ikke på nytt" not in tekst
        assert "etter 3 rader" in tekst and "ingen kveldsrad i denne kjøringen" in tekst
        assert "i ettertid" in tekst

    def test_d2_kan_skrives_til_gjelder_kveldsraden(self):
        """Ville feilet med «En rad for ... kan bare skrives» uten et ord om
        signalet i ettertid."""
        tekst = fp._kan_skrives_til(DATO)
        assert tekst.startswith(f"Kveldsraden for {DATO.isoformat()} kan bare skrives")
        assert "AD-7" in tekst and "i ettertid" in tekst and "uten KI-tekst" in tekst
        # Gjennomgangen (ECH1): forbeholdet fra regn_i_ettertid og docs/hjelp.md.
        assert "for aksjene i lista som har nok kurser i basen til og med dagen" in tekst

    def test_d3_tilstand_sier_ikke_at_hullet_er_endelig(self):
        """Ville feilet med «Hullet er endelig foerst naar dato ikke lenger er
        inneveerende boersdag» fra foer 2.17."""
        doc = tilstand.tilstand.__doc__
        assert "Hullet er endelig foerst" not in doc
        assert "ETTERTID" in doc and "regn_signalet_i_ettertid" in doc

    def test_d4_les_inn_sier_at_dagene_faar_signalet_ved_neste_henting(self, stier, uten_noekkel_og_nett):  # noqa: F811
        """Ville feilet fordi utskriften fra --les-inn ikke sa noe om
        vurderingene. Ingen kurser i utskriften (regel 16)."""
        raa, base = stier
        fil = lag_bilde(raa, OEYEBLIKK_22_09)
        ut = []
        fp.les_inn(fil, base, ut.append)
        tekst = "\n".join(ut)
        assert "Innlesingen skriver ingen vurderinger (AD-7)" in tekst
        assert "signalet regnet i ettertid ved neste henting" in tekst
        assert "for aksjene i lista som har nok kurser i basen til og med dagen" in tekst
        # Gjennomgangen (VG2): ingen kurs med desimaler i utskriften, bare
        # antall, symboler, datoer og tidspunktet fila ble hentet. Storynumrene,
        # som «story 2.17», tas ut foerst.
        assert not re.search(r"\d[.,]\d", re.sub(r"story \d+\.\d+", "", tekst))

    def test_d4_ingen_linje_om_ettertid_naar_basen_feilet(self, stier, uten_noekkel_og_nett, monkeypatch):  # noqa: F811
        """Gjennomgangen (VG2): skrev basen ingenting, sier innlesingen ikke
        noe om signalet i ettertid, og ender med kode 1."""
        raa, base = stier
        fil = lag_bilde(raa, OEYEBLIKK_22_09)
        monkeypatch.setattr(fp, "skriv_til_basen", lambda *a, **k: None)
        ut = []
        with pytest.raises(SystemExit) as stopp:
            fp.les_inn(fil, base, ut.append)
        assert stopp.value.code == 1
        assert not any("i ettertid" in linje for linje in ut)


class TestDetSomIkkeBrukes:
    def test_d5_minnenotatlager_med_kjoep_er_tatt_bort(self):
        """Ville feilet foer 9.15: klassen fantes, men ingenting brukte den."""
        assert not hasattr(notater, "MinneNotatlagerMedKjoep")
        assert hasattr(notater, "MinneNotatlager")

    def test_d6_retningene_er_tatt_bort(self):
        """Ville feilet foer 9.15: konstanten fantes, men ingenting brukte den."""
        assert not hasattr(dagsgrunnlag, "RETNINGENE")
        assert hasattr(dagsgrunnlag, "RETNINGSFELTENE")
