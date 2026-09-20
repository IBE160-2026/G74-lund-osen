"""Tester for deduplisering og kategorifilter - FR-501 til FR-503.

Meldingene er skrevet for haand. NewsWeb koster ingen kvote, men testdata
som hentes er testdata som endrer seg, og da tester vi boersen i stedet for
koden vaar.
"""

from meldinger import (
    FILTRERES_BORT,
    KI_AVGJOER,
    SLIPPER_GJENNOM,
    UKJENT,
    UTBYTTEMERKING,
    Melding,
    boette,
    dedupliser,
    filtrer,
)


def melding(
    id: str = "1",
    issuer: str = "EQNR",
    kategori: str = "Innsideinformasjon",
    publisert: str = "2026-09-18T08:30:00",
    tittel: str = "Tittel",
    spraak: str = "no",
) -> Melding:
    return Melding(id, issuer, kategori, publisert, tittel, spraak)


class TestDeduplisering:
    """FR-501. 32 av 121 meldinger var samme melding paa to spraak."""

    def test_samme_utsteder_kategori_og_minutt_er_en_dublett(self):
        norsk = melding(id="no-1", tittel="Kontrakt tildelt", spraak="no")
        engelsk = melding(id="en-1", tittel="Contract awarded", spraak="en")

        beholdt = dedupliser([norsk, engelsk])

        assert len(beholdt) == 1

    def test_den_norske_beholdes(self):
        norsk = melding(id="no-1", tittel="Kontrakt tildelt", spraak="no")
        engelsk = melding(id="en-1", tittel="Contract awarded", spraak="en")

        assert dedupliser([norsk, engelsk])[0].id == "no-1"

    def test_den_norske_beholdes_ogsaa_naar_engelsk_kom_foerst(self):
        """Rekkefoelgen fra API-et skal ikke avgjoere spraaket."""
        norsk = melding(id="no-1", spraak="no")
        engelsk = melding(id="en-1", spraak="en")

        assert dedupliser([engelsk, norsk])[0].id == "no-1"

    def test_bare_engelsk_beholdes_naar_norsk_ikke_finnes(self):
        engelsk = melding(id="en-1", spraak="en")

        beholdt = dedupliser([engelsk])

        assert [m.id for m in beholdt] == ["en-1"]

    def test_ulik_minutt_er_ikke_dublett(self):
        tidlig = melding(id="a", publisert="2026-09-18T08:30:00")
        sent = melding(id="b", publisert="2026-09-18T08:31:00")

        assert len(dedupliser([tidlig, sent])) == 2

    def test_ulik_utsteder_er_ikke_dublett(self):
        equinor = melding(id="a", issuer="EQNR")
        dnb = melding(id="b", issuer="DNB")

        assert len(dedupliser([equinor, dnb])) == 2

    def test_ulik_kategori_er_ikke_dublett(self):
        innside = melding(id="a", kategori="Innsideinformasjon")
        flagging = melding(id="b", kategori="Flagging")

        assert len(dedupliser([innside, flagging])) == 2

    def test_sekunder_teller_ikke(self):
        """To oversettelser legges ut samtidig, men ikke i samme sekund."""
        norsk = melding(id="no-1", publisert="2026-09-18T08:30:04", spraak="no")
        engelsk = melding(id="en-1", publisert="2026-09-18T08:30:41", spraak="en")

        beholdt = dedupliser([norsk, engelsk])

        assert [m.id for m in beholdt] == ["no-1"]


class TestKategorifilter:
    """FR-502. Hver kategori hoerer til noeyaktig en boette."""

    def test_renteregulering_slipper_ikke_gjennom(self):
        assert boette(melding(kategori="Renteregulering")) == FILTRERES_BORT

    def test_innsideinformasjon_slipper_gjennom(self):
        assert boette(melding(kategori="Innsideinformasjon")) == SLIPPER_GJENNOM

    def test_tilbakekjoep_slipper_ikke_gjennom(self):
        """Stoerste stoeykilden: 35 av 121 meldinger over fire uker."""
        kategori = "Utsteders meldeplikt ved handel i egne aksjer"
        assert boette(melding(kategori=kategori)) == FILTRERES_BORT

    def test_samlekategorien_gaar_til_ki(self):
        kategori = "Ikke-informasjonspliktige pressemeldinger"
        assert boette(melding(kategori=kategori)) == KI_AVGJOER

    def test_eks_dato_gaar_til_utbyttemerking_ikke_til_lista(self):
        """FR-503: eks.dato vises ikke som melding, men forkastes ikke."""
        assert boette(melding(kategori="EKS.DATO")) == UTBYTTEMERKING

    def test_kategorinavn_er_ufoelsomt_for_store_bokstaver(self):
        assert boette(melding(kategori="INNSIDEINFORMASJON")) == SLIPPER_GJENNOM
        assert boette(melding(kategori="innsideinformasjon")) == SLIPPER_GJENNOM

    def test_ukjent_kategori_forsvinner_ikke_stille(self):
        """En ny meldingstype paa boersen skal oppdages, ikke filtreres bort."""
        assert boette(melding(kategori="Noe helt nytt")) == UKJENT


class TestFilterSortering:
    def test_alle_boetter_returneres_ogsaa_de_tomme(self):
        """Kallende kode skal kunne telle hva som ble sortert vekk."""
        resultat = filtrer([melding(kategori="Innsideinformasjon")])

        assert set(resultat) == {
            SLIPPER_GJENNOM,
            KI_AVGJOER,
            FILTRERES_BORT,
            UTBYTTEMERKING,
            UKJENT,
        }
        assert len(resultat[SLIPPER_GJENNOM]) == 1
        assert resultat[FILTRERES_BORT] == []

    def test_dedupliseringen_kjoeres_foer_filteret(self):
        """FR-501. Motsatt rekkefoelge teller dubletter to ganger.

        To spraakversjoner av samme innsidemelding skal gi en melding
        gjennom filteret, ikke to.
        """
        norsk = melding(id="no-1", spraak="no")
        engelsk = melding(id="en-1", spraak="en")

        resultat = filtrer(dedupliser([norsk, engelsk]))

        assert [m.id for m in resultat[SLIPPER_GJENNOM]] == ["no-1"]
