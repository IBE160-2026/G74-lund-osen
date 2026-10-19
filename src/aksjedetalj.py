"""Aksjedetaljen - FR-201, FR-202, FR-204 og FR-706.

Ren logikk. Ingen API-kall, ingen filer, ingen HTML. Grafen tegnes av serien
i kurs. Sjekkene og maalingene kommer fra raden i vurdering for datoen til
nyeste kurs, gjennom tilstand(), som i markedsoversikten (story 2.2b).
Signalet regnes aldri her.

Avgrenset til forklaringsdelen. Boersmeldinger (FR-203) og kommende
hendelser (FR-301) er ikke med: Euronext ga ikke tillatelse innen fristen, saa
plan B gjelder fra 28.09 (Epic 10 i epics.md). KI-forklaringen av signalet
(FR-602) kommer med Epic 10.

Forklarbarhet er hele poenget. En bruker skal kunne lese seg fram til hvorfor
styrken ble 2 og ikke 1, uten aa kjenne formelen paa forhaand. Derfor baerer
hver sjekk maalingen sin hit ut, ikke bare fortegnet den endte paa.
"""

import math
from dataclasses import dataclass
from datetime import date, timedelta

from boersdag import UtenforKalenderen, er_boersdag
from kursdata import Aksje, Kursrad
from markedsoversikt import (
    IKKE_VURDERT,
    RETNINGSVISNING,
    SJEKKBOKSTAVER,
    UKJENT_RETNING,
    Retningsvisning,
    endring_i_prosent,
    les_tilstand,
)
from oversiktsdata import Oversiktspost
from perioder import SEKS_MND, startdag
from signalberegning import NEGATIV, POSITIV, STANDARD, Parametre, bevegelsesdesimaler, nodvendige_dager, sjekker_fra
from tallformat import desimaler_uten_null, fortegn, tall
from tilstand import Art, Tilstand
from vurderingsdata import Grunn, Vurdering

# FR-201 og story 8.16: grafen starter paa startdagen fra perioder.startdag,
# 6 mnd naar ingen periode er valgt. Regnet etter kalenderen fra siste dag i
# grafen, ikke i antall rader (designregler.md §2).

# Story 8.0c: ordet ved 0 i Ga-kolonnen. «Ingen» er en retning (FR-704), ikke
# det en sjekk ga, saa ordet er et eget.
INGEN_UTSLAG = "ingen utslag"

# Story 8.0d, PR 3 (utdraget §8, svar 20): skalaen i sjekkortene går til tre
# ganger grensen på hver side for trend og bevegelse, og fra 0 til fire
# ganger volumfaktoren for interesse (0 til 6 × med 1,5 ×).
SKALA_GANGER = 3
SKALA_INTERESSE_GANGER = 4


@dataclass(frozen=True)
class Skala:
    """Det grå feltet i et sjekkort, i prosent av bredden (0-100).

    felt_fra og felt_til er feltet der sjekken gir 0. prikk er målingen,
    lagt ved enden når den er utenfor skalaen (svar 20), og None når
    målingen mangler. Tekstene er grensene over feltet. Skalaen er bare
    for synet: teksten i kortet sier det samme (aria-hidden i malen)."""

    felt_fra: float
    felt_til: float
    prikk: float | None
    lav_tekst: str
    hoy_tekst: str


def _andel(verdi: float, lav: float, hoy: float) -> float:
    """Plassen til verdi mellom lav og hoy, i prosent og innenfor 0-100."""
    return max(0.0, min(100.0, (verdi - lav) / (hoy - lav) * 100))


def _prikk(maaling: float | None, lav: float, hoy: float) -> float | None:
    """Prikken, eller None naar maalingen mangler eller ikke er et tall
    (gjennomgangen, ECH4): da tegnes ingen prikk, og teksten sier resten."""
    if maaling is None or not math.isfinite(maaling):
        return None
    return _andel(maaling, lav, hoy)


def bygg_skala(navn: str, maaling: float | None, grense: float | None, p: Parametre = STANDARD) -> Skala | None:
    """Skalaen for en sjekk, regnet fra målingen og grensen i den lagrede
    vurderingen og Parametre. Signalet regnes ikke på nytt (FR-101). None
    når grensen ikke er et positivt tall, så skalaen ikke kan tegnes."""
    if navn == "Interesse":
        if p.volumfaktor <= 0:
            return None
        hoy = p.volumfaktor * SKALA_INTERESSE_GANGER
        return Skala(
            felt_fra=0.0,
            felt_til=_andel(p.volumfaktor, 0.0, hoy),
            prikk=_prikk(maaling, 0.0, hoy),
            lav_tekst="0",
            hoy_tekst=f"{tall(p.volumfaktor, 'faktor')} ×",
        )
    grense = p.noytralsone if navn == "Trend" else grense
    if grense is None or grense <= 0:
        return None
    lav, hoy = -grense * SKALA_GANGER, grense * SKALA_GANGER
    # Svar 30 (15.10, ECH3): grensene for bevegelse viser samme tall som
    # standardavviket i teksten i kortet, og aldri 0,0.
    antall = 1
    if navn == "Bevegelse":
        if maaling is not None:
            antall = bevegelsesdesimaler(maaling, grense)
        else:
            antall = desimaler_uten_null(grense * 100)
    tekst = tall(grense * 100, "maaling", antall, fortegn=False)
    return Skala(
        felt_fra=_andel(-grense, lav, hoy),
        felt_til=_andel(grense, lav, hoy),
        prikk=_prikk(maaling, lav, hoy),
        lav_tekst="-" + tekst,
        hoy_tekst="+" + tekst,
    )


def hva_den_maaler(navn: str, p: Parametre = STANDARD) -> str:
    """Kort om hva sjekken måler, med vinduene fra Parametre."""
    return {
        "Trend": f"Sluttkursen mot snittet av de siste {p.ma_vindu} børsdagene.",
        "Bevegelse": f"Dagens endring mot hvor mye aksjen har svingt de siste {p.volatilitet_vindu} børsdagene.",
        "Interesse": f"Dagens volum mot medianvolumet de siste {p.volum_vindu} børsdagene.",
    }[navn]


def regelen(navn: str, p: Parametre = STANDARD) -> str:
    """Regelen nederst i sjekkortet, med grensene fra Parametre."""
    return {
        "Trend": f"Mer enn {tall(p.noytralsone * 100, 'grense')} over snittet gir +1, og mer enn "
        f"{tall(p.noytralsone * 100, 'grense')} under gir -1.",
        "Bevegelse": "En endring større enn ett standardavvik gir +1 eller -1, etter retningen.",
        "Interesse": f"Mer enn {tall(p.volumfaktor, 'faktor')} × medianen gir +1 eller -1, etter dagens kursendring.",
    }[navn]


@dataclass(frozen=True)
class Punkt:
    """Ett punkt i grafen. ma50 er None foer snittet har nok historikk."""

    dato: date
    kurs: float
    ma50: float | None


@dataclass(frozen=True)
class SjekkVisning:
    """En sjekk slik den vises: navn, fortegn, og maalingen bak fortegnet.

    FR-706 krever navn og verdi. Maalingen er tatt med i tillegg, fordi
    verdien alene ikke forklarer noe: at trend ga +1 sier ikke hvor mye over
    snittet kursen laa, og da kan brukeren ikke etterproeve summen.
    """

    navn: str
    verdi: int
    maaling: str
    # Story 8.0d, PR 3: kortet med det grå feltet (utdraget §8).
    nummer: int = 0
    skala: Skala | None = None
    maaler: str = ""
    regel: str = ""

    @property
    def fortegn(self) -> str:
        return fortegn(self.verdi)

    @property
    def ord(self) -> str:
        """Ordet ved tallet i Ga-kolonnen (story 8.0c), som retningen: bygget
        av konstantene i signalberegning.py, aldri «opp» eller «ned»."""
        if self.verdi > 0:
            return POSITIV.lower()
        if self.verdi < 0:
            return NEGATIV.lower()
        return INGEN_UTSLAG

    @property
    def klasse(self) -> str:
        if self.verdi > 0:
            return "opp"
        if self.verdi < 0:
            return "ned"
        return "ingen"

    @property
    def bidro(self) -> bool:
        """Talte denne sjekken med i styrken?"""
        return self.verdi != 0


@dataclass(frozen=True)
class Detalj:
    """Aksjedetaljen. tilstand og tekst er som i markedsoversikten: tekst er
    None bare naar raden har en vurdering. sjekker er tom naar den ikke har
    det, og da staar tekst i stedet (FR-204)."""

    aksje: Aksje
    dato: date
    # Story 8.16b: None for en valgt dag uten kurs, som en loerdag.
    sluttkurs: float | None
    tilstand: Tilstand | None
    tekst: str | None
    sjekker: tuple[SjekkVisning, ...]
    punkter: tuple[Punkt, ...]
    antall_dager: int = 0
    noedvendige_dager: int = 0
    # Story 8.0d, PR 3: endringen som fjerde nøkkeltall, med dagen før, og
    # terskelen for overskriften (beslutning 7).
    endring: float | None = None
    forrige_dato: date | None = None
    # Svar 29 (15.10, BH6 og ECH2): datoene står ved ukedagene når det
    # ligger en børsdag mellom de to kursradene.
    endring_med_datoer: bool = False
    terskel: int = STANDARD.terskel

    @property
    def vurdering(self) -> Vurdering | None:
        if self.tilstand is not None and self.tilstand.art is Art.SVAR:
            return self.tilstand.innhold
        return None

    @property
    def styrke(self) -> int | None:
        return self.vurdering.styrke if self.vurdering else None

    @property
    def retning(self) -> Retningsvisning:
        if not self.vurdering:
            return UKJENT_RETNING
        return RETNINGSVISNING.get(self.vurdering.retning, UKJENT_RETNING)

    @property
    def skilte_seg_ut(self) -> bool:
        """Styrken er på terskelen eller over (beslutning 7)."""
        return self.styrke is not None and self.styrke >= self.terskel

    @property
    def sjekkbrikker(self) -> tuple[tuple[str, str, str], ...]:
        """T, B og I som i oversikten (story 8.0d, PR 3), lest fra den
        lagrede vurderingen. Tom uten vurdering."""
        if not self.vurdering:
            return ()
        return tuple((bokstav, felt, fortegn(getattr(self.vurdering, felt))) for bokstav, felt in SJEKKBOKSTAVER)

    @property
    def for_kort_serie(self) -> bool:
        """Raden har grunnen signal_ikke_regnet, og serien er kortere enn
        signalet trenger. Bare da sier siden antallet dager (FR-204).
        vurder() gir samme grunn naar porten ikke godtar tallene, eller ved
        ArithmeticError, paa en serie som er lang nok (raadet 03.10)."""
        return (
            self.tilstand is not None
            and self.tilstand.innhold is Grunn.SIGNAL_IKKE_REGNET
            and self.antall_dager < self.noedvendige_dager
        )

    @property
    def ikke_vurdert(self) -> bool:
        return self.tekst == IKKE_VURDERT

    @property
    def bidragsytere(self) -> tuple[SjekkVisning, ...]:
        """De sjekkene som faktisk ga utslag. Summen av dem er styrken."""
        return tuple(s for s in self.sjekker if s.bidro)


def glidende_snitt(kurser: list[float], vindu: int) -> list[float | None]:
    """Snitt over de siste `vindu` verdiene, None foer det finnes nok."""
    ut: list[float | None] = []
    for i in range(len(kurser)):
        if i + 1 < vindu:
            ut.append(None)
        else:
            ut.append(sum(kurser[i + 1 - vindu : i + 1]) / vindu)
    return ut


def bygg_punkter(
    rader: list[Kursrad], p: Parametre = STANDARD, start: date | None = None, slutt: date | None = None
) -> tuple[Punkt, ...]:
    """Grafpunktene fra start til og med slutt, med MA50 oppaa (FR-202).

    Story 8.16: slutt er siste dag i grafen, som standard siste rad, og
    start er startdagen for perioden, som standard 6 mnd fra perioder.startdag
    regnet fra siste rad paa eller foer slutt.

    Kursen og snittet tegnes fra SAMME serie - den utbyttejusterte. Tegnet
    vi slutt mot et snitt regnet paa justert_slutt, ville de to ligget paa
    hver sin skala, og avstanden mellom dem ville vaert stoerst for aksjene
    som betaler mest utbytte. Linja skal vise sjekk 1, ikke et utbytte.

    Snittet regnes paa HELE serien og klippes etterpaa. Ellers ville de
    foerste 50 dagene i vinduet mistet snittet sitt uten grunn.
    """
    kurser = [float(rad.justert_slutt) for rad in rader]
    snitt = glidende_snitt(kurser, p.ma_vindu)
    if slutt is not None:
        antall = sum(1 for rad in rader if rad.dato <= slutt)
        rader, kurser, snitt = rader[:antall], kurser[:antall], snitt[:antall]
    if not rader:
        return ()
    if start is None:
        start = startdag(SEKS_MND, rader[-1].dato)

    return tuple(
        Punkt(dato=rad.dato, kurs=kurs, ma50=ma) for rad, kurs, ma in zip(rader, kurser, snitt) if rad.dato >= start
    )


def boersdag_mellom(fra: date, til: date) -> bool:
    """Om det ligger en børsdag mellom fra og til, uten dem selv (svar 29).

    Fredag til mandag har ingen, og heller ikke en uke med bare stengte
    dager. Kan kalenderen ikke avgjøre det (UtenforKalenderen), gis True,
    så datoene står og siden ikke feiler. Lørdag og søndag er aldri
    børsdager og slås ikke opp, så en helg i et år kalenderen ikke dekker,
    gir ukedagene (gjennomgangen av svarene 15.10, ECH2 og BH6).
    """
    dagene = (fra + timedelta(days=i) for i in range(1, (til - fra).days))
    try:
        return any(dag.weekday() < 5 and er_boersdag(dag) for dag in dagene)
    except UtenforKalenderen:
        return True


def bygg_detalj(
    post: Oversiktspost,
    rader: list[Kursrad],
    idag: date,
    p: Parametre = STANDARD,
    start: date | None = None,
    slutt: date | None = None,
    *,
    dag: date | None = None,
    innhold: Vurdering | Grunn | None = None,
) -> Detalj | None:
    """Detaljen for en aksje, eller None hvis den ikke har en eneste kursrad.

    post er aksjen og raden i vurdering fra Oversiktsleser, rader er serien i
    kurs. Grafen tegnes av serien. Sjekkene kommer fra raden, med
    forklaringene laget av maalingene der (FR-706). Har raden ingen
    vurdering, er sjekkene tomme og teksten sier hvorfor (FR-204).

    Story 8.16b (gruppens svar 19.10 kl. 00:00): med dag er det dagen som
    vises, og innhold er raden i vurdering for dagen, None uten rad.
    Sluttkursen og endringen er fra kursraden for dagen, og None naar serien
    ikke har dagen, som en loerdag. Signalet regnes aldri her (AD-7).
    """
    if not rader or post.nyeste is None:
        return None

    if dag is None:
        dato, innhold, serie = post.nyeste.dato, post.innhold, rader
        sluttkurs: float | None = float(post.nyeste.slutt)
        har_kurs = True
    else:
        dato, serie = dag, [rad for rad in rader if rad.dato <= dag]
        har_kurs = bool(serie) and serie[-1].dato == dag
        sluttkurs = float(serie[-1].slutt) if har_kurs else None

    utfall, tekst = les_tilstand(innhold, dato, idag)
    sjekker: tuple[SjekkVisning, ...] = ()
    if utfall is not None and utfall.art is Art.SVAR:
        sjekker = tuple(
            SjekkVisning(
                navn=s.navn,
                verdi=s.verdi,
                maaling=s.forklaring,
                nummer=i,
                skala=bygg_skala(s.navn, s.maaling, s.grense, p),
                maaler=hva_den_maaler(s.navn, p),
                regel=regelen(s.navn, p),
            )
            for i, s in enumerate(sjekker_fra(utfall.innhold, p), start=1)
        )

    to_rader = har_kurs and len(serie) >= 2
    return Detalj(
        aksje=post.aksje,
        dato=dato,
        sluttkurs=sluttkurs,
        tilstand=utfall,
        tekst=tekst,
        sjekker=sjekker,
        punkter=bygg_punkter(rader, p, start, slutt),
        antall_dager=len(serie),
        noedvendige_dager=nodvendige_dager(p),
        endring=endring_i_prosent(serie) if har_kurs else None,
        forrige_dato=serie[-2].dato if to_rader else None,
        endring_med_datoer=to_rader and boersdag_mellom(serie[-2].dato, dato),
        terskel=p.terskel,
    )


def normaliser_symbol(symbol: str) -> str:
    """Symbolet i ruta slik aksje har det: uten mellomrom, med store
    bokstaver. En ticker som EQNR.OL blir ikke et symbol."""
    return symbol.strip().upper()


@dataclass(frozen=True)
class Dagen:
    """Dagen som er merket i grafen for siste boersdag og «Velg dag» (story
    8.16, gruppens svar 18.10 kl. 21:50): endringen den dagen og signalet som
    er lagret for den. tilstand og tekst er som i oversikten, fra
    les_tilstand: tekst er None bare for en vurdering. Signalet regnes
    aldri her (AD-7)."""

    dato: date
    endring: float | None
    tilstand: Tilstand | None
    tekst: str | None

    @property
    def vurdering(self) -> Vurdering | None:
        if self.tilstand is not None and self.tilstand.art is Art.SVAR:
            return self.tilstand.innhold
        return None

    @property
    def retning(self) -> Retningsvisning:
        if not self.vurdering:
            return UKJENT_RETNING
        return RETNINGSVISNING.get(self.vurdering.retning, UKJENT_RETNING)


def bygg_dagen(rader: list[Kursrad], dag: date, innhold: Vurdering | Grunn | None, idag: date) -> Dagen:
    """Dagen med endringen fra kursserien og den lagrede raden i vurdering.
    Endringen er None naar serien ikke har dagen eller dagen foer."""
    foer = [rad for rad in rader if rad.dato <= dag]
    endring = endring_i_prosent(foer) if foer and foer[-1].dato == dag else None
    tilstand_, tekst = les_tilstand(innhold, dag, idag)
    return Dagen(dato=dag, endring=endring, tilstand=tilstand_, tekst=tekst)
