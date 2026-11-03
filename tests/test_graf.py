"""Tester for koordinatregningen. En linje som ligger galt, ser riktig ut."""

from datetime import date, timedelta

import pytest

from aksjedetalj import Punkt

# Story 8.2b, b (U41, U47): tegneflaten har felt til venstre, nederst og til
# hoeyre, saa grensene er VENSTRE, BREDDE - HOEYRE og HOYDE - BUNN.
from graf import BREDDE, BUNN, HOEYRE, HOYDE, MARG_Y, NAVNEMARG, VENSTRE, bygg_graf, indeksverdier


def punkter(kurser, ma50=None):
    ma50 = ma50 or [None] * len(kurser)
    return tuple(
        Punkt(dato=date(2026, 1, 1) + timedelta(days=i), kurs=k, ma50=m) for i, (k, m) in enumerate(zip(kurser, ma50))
    )


def koordinater(linje):
    return [tuple(float(d) for d in par.split(",")) for par in linje.split()]


class TestTomtGrunnlag:
    def test_none_uten_punkter(self):
        assert bygg_graf(()) is None

    def test_none_med_bare_ett_punkt(self):
        """En linje trenger to punkter."""
        assert bygg_graf(punkter([100.0])) is None


class TestSkalering:
    def test_hoyeste_kurs_havner_oeverst(self):
        graf = bygg_graf(punkter([100.0, 200.0]))
        forste, siste = koordinater(graf.kurslinje)

        assert siste[1] < forste[1], "hoeyere kurs skal ha lavere y i SVG"

    def test_linja_holder_seg_innenfor_tegneflaten(self):
        graf = bygg_graf(punkter([50.0, 300.0, 120.0, 90.0]))

        for x, y in koordinater(graf.kurslinje):
            assert VENSTRE <= x <= BREDDE - HOEYRE
            assert MARG_Y <= y <= HOYDE - BUNN

    def test_foerste_og_siste_punkt_ligger_i_hver_sin_ende(self):
        graf = bygg_graf(punkter([100.0, 110.0, 120.0]))
        punkt = koordinater(graf.kurslinje)

        assert punkt[0][0] == pytest.approx(VENSTRE)
        assert punkt[-1][0] == pytest.approx(BREDDE - HOEYRE)

    def test_flat_serie_deler_ikke_paa_null(self):
        graf = bygg_graf(punkter([100.0, 100.0, 100.0]))

        assert graf is not None
        assert graf.lav < graf.hoy
        for _, y in koordinater(graf.kurslinje):
            assert MARG_Y <= y <= HOYDE - BUNN


class TestMa50:
    def test_snittet_faar_egen_linje(self):
        graf = bygg_graf(punkter([100.0, 110.0, 120.0], [99.0, 100.0, 101.0]))

        assert graf.har_ma50
        assert len(koordinater(graf.ma50linje)) == 3

    def test_uten_snitt_er_linja_tom(self):
        graf = bygg_graf(punkter([100.0, 110.0]))

        assert graf.ma50linje == ""
        assert graf.har_ma50 is False

    def test_snittet_er_med_i_skalaen(self):
        """Var snittet utenfor regnestykket, kunne MA50-linja havnet utenfor
        flaten uten at noe feilet - og sjekk 1 ville blitt usynlig."""
        graf = bygg_graf(punkter([100.0, 101.0], [40.0, 41.0]))

        for _, y in koordinater(graf.ma50linje):
            assert MARG_Y <= y <= HOYDE - BUNN
        assert graf.lav < 40.0

    def test_hull_i_snittet_hoppes_over(self):
        """MA50 mangler i starten av en kort serie. Linja skal begynne der
        snittet begynner, ikke klaske ned i null."""
        graf = bygg_graf(punkter([100.0, 110.0, 120.0], [None, 100.0, 105.0]))

        assert len(koordinater(graf.ma50linje)) == 2

    def test_ett_enkelt_snittpunkt_gir_ingen_linje(self):
        graf = bygg_graf(punkter([100.0, 110.0, 120.0], [None, None, 105.0]))
        assert graf.ma50linje == ""


class TestRutenett:
    def test_tre_linjer_fra_lav_til_hoy(self):
        graf = bygg_graf(punkter([100.0, 200.0]))

        assert len(graf.rutenett) == 3
        assert graf.rutenett[0].verdi == pytest.approx(graf.lav)
        assert graf.rutenett[-1].verdi == pytest.approx(graf.hoy)

    def test_datoene_kommer_fra_ytterpunktene(self):
        graf = bygg_graf(punkter([100.0, 110.0, 120.0]))

        assert graf.forste_dato == date(2026, 1, 1)
        assert graf.siste_dato == date(2026, 1, 3)


def boersdagspunkter(fra: date, til: date, uten=()):
    """Et punkt per boersdag fra og med fra til og med til, som serien i
    appen har, uten dagene i uten."""
    from boersdag import er_boersdag

    dager = []
    dag = fra
    while dag <= til:
        if er_boersdag(dag) and dag not in uten:
            dager.append(dag)
        dag += timedelta(days=1)
    return tuple(Punkt(dato=d, kurs=100.0 + i, ma50=None) for i, d in enumerate(dager))


class TestMaanedsmerker:
    """Story 8.0c, beslutning 13."""

    def test_merket_staar_paa_samme_x_som_punktet_for_dagen(self):
        """Ville feilet hvis merkene ble spredd etter kalenderen (M7) eller sto
        én dag feil (M8): linja har lik avstand per boersdag."""
        ps = boersdagspunkter(date(2026, 9, 15), date(2026, 11, 10))
        graf = bygg_graf(ps)
        x_per_dato = {p.dato: x for p, (x, _) in zip(ps, koordinater(graf.kurslinje))}
        assert [m.navn for m in graf.maanedsmerker] == ["oktober", "november"]
        assert graf.maanedsmerker[0].x == pytest.approx(x_per_dato[date(2026, 10, 1)], abs=0.06)
        assert graf.maanedsmerker[1].x == pytest.approx(x_per_dato[date(2026, 11, 2)], abs=0.06)

    def test_mangler_foerste_boersdag_faar_maaneden_ikke_merke(self):
        ps = boersdagspunkter(date(2026, 9, 15), date(2026, 11, 10), uten={date(2026, 10, 1)})
        assert [m.navn for m in bygg_graf(ps).maanedsmerker] == ["november"]

    def test_foerste_maaned_i_vinduet_faar_ikke_merke_naar_dagen_er_foer_vinduet(self):
        ps = boersdagspunkter(date(2026, 9, 15), date(2026, 9, 30))
        assert bygg_graf(ps).maanedsmerker == ()

    def test_utenfor_kalenderen_gir_ingen_merker(self):
        """boersdag dekker bare 2026. En maaned utenfor kan ikke avgjoeres."""
        ps = tuple(Punkt(dato=date(2025, 12, 1) + timedelta(days=i), kurs=100.0, ma50=None) for i in range(20))
        assert bygg_graf(ps).maanedsmerker == ()


class TestMaanedsmerkerEtterGjennomgangen:
    def test_mai_starter_paa_foerste_boersdag_etter_helligdagen(self):
        """VG5: 01.05.2026 er en ukedag uten handel, saa merket staar ved 04.05."""
        ps = boersdagspunkter(date(2026, 4, 15), date(2026, 5, 15))
        graf = bygg_graf(ps)
        x_per_dato = {p.dato: x for p, (x, _) in zip(ps, koordinater(graf.kurslinje))}
        assert [m.navn for m in graf.maanedsmerker] == ["mai"]
        assert graf.maanedsmerker[0].x == pytest.approx(x_per_dato[date(2026, 5, 4)], abs=0.06)

    def test_merket_ved_hoeyre_kant_kuttes_ikke(self):
        """ECH1: navnet kuttes ikke naar maaneden starter paa et av de siste
        punktene. Story 8.2b, b: tegneflaten slutter HOEYRE foer kanten, saa
        navnet faar plass til hoeyre for streken, i feltet nederst, og kommer
        ikke borti navnet ved merket foer (som «september» og «oktober» i
        demoen)."""
        from graf import NAVNEBREDDE

        ps = boersdagspunkter(date(2026, 9, 1), date(2026, 10, 1))
        merker = bygg_graf(ps).maanedsmerker
        assert merker[-1].navn == "oktober" and not merker[-1].til_venstre
        assert merker[-1].x + 3 + NAVNEBREDDE <= BREDDE
        assert merker[-1].x - merker[-2].x >= NAVNEBREDDE

    def test_merket_langt_fra_kanten_staar_til_hoeyre(self):
        ps = boersdagspunkter(date(2026, 9, 15), date(2026, 11, 10))
        assert not bygg_graf(ps).maanedsmerker[0].til_venstre


class TestNavneneVedEnden:
    """Story 8.0d, PR 3 (svar 19, gjennomgangen VG2, BH2 og ECH1): navnene
    staar ved enden av linjene, den hoeyeste over og den laveste under,
    innenfor tegneflaten og over maanedsnavnene."""

    @staticmethod
    def _punkter(kurser, snitt):
        start = date(2026, 1, 5)
        return tuple(
            Punkt(dato=start + timedelta(days=i), kurs=k, ma50=s) for i, (k, s) in enumerate(zip(kurser, snitt))
        )

    def test_navnene_staar_ved_enden_og_kursen_over_naar_den_er_hoeyest(self):
        graf = bygg_graf(self._punkter([100, 110, 120], [100, 100, 100]))
        assert graf.kursnavn.x == graf.snittnavn.x == BREDDE - HOEYRE + NAVNEMARG
        assert graf.kursnavn.y < graf.snittnavn.y

    def test_prikken_staar_paa_det_siste_kurspunktet(self):
        """Gjennomgangen 15.10 (VG4): prikken ved enden følger kurslinja, ikke
        det første punktet eller snittet."""
        graf = bygg_graf(self._punkter([100, 110, 120], [100, 100, 100]))
        x, y = graf.kurslinje.split()[-1].split(",")
        assert (graf.siste.x, graf.siste.y) == (float(x), float(y))
        assert graf.siste.x == BREDDE - HOEYRE
        assert graf.siste.y != float(graf.ma50linje.split()[-1].split(",")[1])

    def test_snittet_over_naar_kursen_er_lavest(self):
        graf = bygg_graf(self._punkter([120, 110, 100], [110, 110, 110]))
        assert graf.snittnavn.y < graf.kursnavn.y

    def test_navnene_holder_seg_innenfor_og_over_maanedsnavnene(self):
        """Kursen ender helt nederst: begge navnene staar over bunnen der
        maanedsnavnene staar, og minst NAVNEAVSTAND fra hverandre."""
        from graf import NAVNEAVSTAND

        graf = bygg_graf(self._punkter([120, 119, 50], [120, 119.5, 119]))
        for navn in (graf.kursnavn, graf.snittnavn):
            assert MARG_Y <= navn.y <= HOYDE - BUNN
        assert abs(graf.kursnavn.y - graf.snittnavn.y) >= NAVNEAVSTAND

    def test_uten_snitt_bare_kursnavnet(self):
        graf = bygg_graf(self._punkter([100, 110], [None, None]))
        assert graf.kursnavn is not None and graf.snittnavn is None


class TestIndekslinja:
    """Story 2.9c: hovedindeksen som stiplet linje i kursgrafen. Kontrollen
    under storyen i epics.md. Mutantene står i spesifikasjonen 2.9c."""

    def _punkter(self, kurser):
        start = date(2026, 1, 1)
        return tuple(Punkt(dato=start + timedelta(days=i), kurs=k, ma50=None) for i, k in enumerate(kurser))

    def test_linja_starter_paa_aksjens_kurs_og_foelger_indeksen(self):
        """Indeksen 1000, 1100 og 1050 med aksjen på 50 første dag gir 50, 55
        og 52,5. Ville feilet hvis indeksen ble tegnet i sine egne poeng
        (mutant C1)."""
        ps = self._punkter([50.0, 60.0, 40.0])
        indeks = {p.dato: v for p, v in zip(ps, (1000.0, 1100.0, 1050.0))}
        assert indeksverdier(ps, indeks) == pytest.approx({ps[0].dato: 50.0, ps[1].dato: 55.0, ps[2].dato: 52.5})
        graf = bygg_graf(ps, indeks=indeks)
        # Første punkt på den stiplede linja er første punkt på kurslinja.
        assert koordinater(graf.indekslinje)[0] == koordinater(graf.kurslinje)[0]
        assert graf.indeksstart == ps[0].dato and graf.har_indeks

    def test_startdagen_er_grafens_foerste_dag_ikke_indeksens(self):
        """Indeksen har dager før grafen. Ville feilet med indeksens første
        dag, eller den siste, som startdag (mutant C2)."""
        ps = self._punkter([50.0, 60.0, 40.0])
        indeks = {ps[0].dato - timedelta(days=1): 500.0}
        indeks.update({p.dato: v for p, v in zip(ps, (1000.0, 1100.0, 1050.0))})
        assert indeksverdier(ps, indeks)[ps[0].dato] == pytest.approx(50.0)
        assert indeksverdier(ps, indeks)[ps[2].dato] == pytest.approx(52.5)

    def test_bare_dager_indeksen_har(self):
        """Dag 2 mangler i indeksen: den får ikke noe punkt, og linja har to."""
        ps = self._punkter([50.0, 60.0, 40.0])
        indeks = {ps[0].dato: 1000.0, ps[2].dato: 1100.0}
        assert set(indeksverdier(ps, indeks)) == {ps[0].dato, ps[2].dato}
        assert len(koordinater(bygg_graf(ps, indeks=indeks).indekslinje)) == 2

    def test_uten_indeks_ingen_linje(self):
        """Ville feilet hvis en linje ble tegnet uten indeks (mutant C3)."""
        ps = self._punkter([50.0, 60.0, 40.0])
        for indeks in (None, {}, {ps[1].dato: 1000.0}):
            graf = bygg_graf(ps, indeks=indeks)
            assert graf.indekslinje == "" and not graf.har_indeks and graf.indeksstart is None

    def test_indeksen_faar_plass_paa_skalaen(self):
        """Indeksen stiger mer enn aksjen: skalaen tar den med, så linja
        ikke går utenfor tegneflaten."""
        ps = self._punkter([50.0, 50.0, 50.0])
        indeks = {p.dato: v for p, v in zip(ps, (1000.0, 1500.0, 2000.0))}
        graf = bygg_graf(ps, indeks=indeks)
        assert graf.hoy >= 100.0
        assert all(MARG_Y - 0.05 <= y <= graf.hoyde - BUNN + 0.05 for _, y in koordinater(graf.indekslinje))

    def test_uten_grafens_foerste_dag_starter_linja_paa_den_neste(self):
        """Gjennomgangen (VG1): indeksen har bare dag 2 og 3. Startdagen er
        dag 2, og linja starter på aksjens kurs den dagen."""
        ps = self._punkter([50.0, 60.0, 40.0])
        indeks = {ps[1].dato: 1000.0, ps[2].dato: 1100.0}
        assert indeksverdier(ps, indeks) == pytest.approx({ps[1].dato: 60.0, ps[2].dato: 66.0})
        graf = bygg_graf(ps, indeks=indeks)
        assert graf.indeksstart == ps[1].dato and graf.indeksslutt == ps[2].dato
        assert koordinater(graf.indekslinje)[0] == koordinater(graf.kurslinje)[1]


class TestFeltetTilHoeyre:
    """Story 8.2b, b (U41, U47): navnene står i feltet til høyre, ved enden
    av linjene, og den stiplede linja har navn."""

    @staticmethod
    def _graf(kurser, snitt, indeks):
        start = date(2026, 1, 5)
        ps = tuple(Punkt(dato=start + timedelta(days=i), kurs=k, ma50=s) for i, (k, s) in enumerate(zip(kurser, snitt)))
        return bygg_graf(ps, indeks={p.dato: v for p, v in zip(ps, indeks)})

    def test_ingen_linje_naar_inn_i_feltet_med_navnene(self):
        """Ville feilet hvis en linje gikk forbi kanten der navnene begynner,
        så den krysset et navn, eller navnene sto inne i tegneflaten."""
        graf = self._graf([100, 110, 120], [100, 105, 110], [1000, 1050, 1080])
        kant = max(x for linje in (graf.kurslinje, graf.ma50linje, graf.indekslinje) for x, _ in koordinater(linje))
        assert kant == pytest.approx(graf.hoeyre) == BREDDE - HOEYRE
        for navn in (graf.kursnavn, graf.snittnavn, graf.indeksnavn):
            assert navn.x > kant

    def test_tre_navn_i_rekkefoelgen_linjene_ender(self):
        """Ville feilet uten navn på den stiplede linja (U47), eller hvis to
        navn lå oppå hverandre."""
        from graf import NAVNEAVSTAND

        graf = self._graf([100, 110, 120], [100, 104, 108], [1000, 1110, 1150])
        ender = {
            navn: koordinater(linje)[-1][1]
            for navn, linje in (("kurs", graf.kurslinje), ("snitt", graf.ma50linje), ("indeks", graf.indekslinje))
        }
        navn = {"kurs": graf.kursnavn.y, "snitt": graf.snittnavn.y, "indeks": graf.indeksnavn.y}
        assert sorted(ender, key=ender.get) == sorted(navn, key=navn.get)
        ys = sorted(navn.values())
        assert all(b - a >= NAVNEAVSTAND for a, b in zip(ys, ys[1:]))
        assert all(MARG_Y <= y <= HOYDE - BUNN for y in ys)

    def test_tallene_og_datoene_har_egne_felt(self):
        """Ville feilet hvis rutenettet eller merkene sto der tallene og
        datoene står, så linjene krysset dem."""
        graf = self._graf([100, 110, 120], [100, 104, 108], [1000, 1110, 1150])
        assert graf.venstre == VENSTRE and graf.bunn == HOYDE - BUNN and graf.topp == MARG_Y
        assert all(MARG_Y <= r.y <= HOYDE - BUNN for r in graf.rutenett)
        assert all(VENSTRE <= m.x <= BREDDE - HOEYRE for m in graf.maanedsmerker)
