"""Tester for deduplisering og kategorifilter - FR-501 til FR-503.

Meldingene er skrevet for haand. NewsWeb koster ingen kvote, men testdata
som hentes er testdata som endrer seg, og da tester vi boersen i stedet for
koden vaar.
"""

from meldinger import (
    ENGELSK,
    FILTRERES_BORT,
    KI_AVGJOER,
    NORSK,
    SLIPPER_GJENNOM,
    UAVKLART,
    UKJENT,
    UTBYTTEMERKING,
    Melding,
    boette,
    dedupliser,
    filtrer,
    gjett_spraak,
    til_ki_vurdering,
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


class TestSpraakgjetning:
    """FR-501 sier «behold den norske». Uten en spraakkode fra NewsWeb er
    kravet uimplementerbart som skrevet, og heuristikken paa tittelen er det
    som faktisk lar seg bygge. Om NewsWeb har et spraakfelt, kontrolleres
    21.09 - det koster ingen kvote."""

    def test_ae_oe_aa_avgjoer_alene(self):
        assert gjett_spraak("Innkalling til ekstraordinær generalforsamling") == NORSK
        assert gjett_spraak("Tildeling av kontrakt i Nordsjøen") == NORSK
        assert gjett_spraak("Årsresultat 2026") == NORSK

    def test_norske_ord_uten_saertegn_gjenkjennes(self):
        assert gjett_spraak("Resultat for tredje kvartal") == NORSK
        assert gjett_spraak("Utbytte vedtatt av styret") == NORSK

    def test_engelske_titler_gjenkjennes(self):
        assert gjett_spraak("Notice of annual general meeting") == ENGELSK
        assert gjett_spraak("Results for the third quarter") == ENGELSK

    def test_tittel_uten_holdepunkter_er_uavklart(self):
        """Vi gjetter ikke naar vi ikke vet. Da gjelder foerstemann-regelen."""
        assert gjett_spraak("Q3 2026") == UAVKLART
        assert gjett_spraak("EQNR ASA") == UAVKLART


class TestDedupliseringUtenSpraakkode:
    """Samme regel som over, men gjennom dedupliseringen."""

    def test_norsk_tittel_vinner_over_engelsk(self):
        norsk = melding(id="no-1", tittel="Tildeling av kontrakt i Nordsjøen", spraak="")
        engelsk = melding(id="en-1", tittel="Contract awarded in the North Sea", spraak="")

        assert dedupliser([engelsk, norsk])[0].id == "no-1"

    def test_spraakkoden_gaar_foran_tittelen(self):
        """Finnes feltet, er det feltet som gjelder - ikke gjetningen."""
        norsk = melding(id="no-1", tittel="Q3 2026", spraak="no")
        engelsk = melding(id="en-1", tittel="Resultat for tredje kvartal", spraak="en")

        assert dedupliser([engelsk, norsk])[0].id == "no-1"

    def test_uavklart_beholder_foerstemann(self):
        foerste = melding(id="a", tittel="Q3 2026", spraak="")
        andre = melding(id="b", tittel="EQNR ASA", spraak="")

        assert dedupliser([foerste, andre])[0].id == "a"


class TestUkjentKategoriGaarIkkeTilKi:
    """Prompten er skrevet for samlekategorien. En ukjent kategori ville blitt
    gjettet paa av en modell som ikke er kalibrert for den."""

    def test_ukjent_kategori_havner_ikke_i_ki_boetta(self):
        sortert = filtrer([melding(kategori="Noe helt nytt fra boersen")])

        assert til_ki_vurdering(sortert) == []
        assert len(sortert[UKJENT]) == 1

    def test_bare_samlekategorien_gaar_til_ki(self):
        meldinger = [
            melding(id="a", kategori="Ikke-informasjonspliktige pressemeldinger"),
            melding(id="b", kategori="Innsideinformasjon"),
            melding(id="c", kategori="Noe helt nytt fra boersen"),
            melding(id="d", kategori="Renteregulering"),
        ]

        assert [m.id for m in til_ki_vurdering(filtrer(meldinger))] == ["a"]
