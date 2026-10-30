"""Markedsoversikten - FR-101 til FR-103, FR-409.

Ren logikk. Faar en Oversiktspost per aksje fra Oversiktsleser og viser
vurderingen som er lagret, gjennom tilstand() (story 2.2b). Signalet regnes
aldri her: hentekommandoen regnet det og skrev det i vurdering (AD-17), og
siden og historikken skal aldri si hver sin ting. Gjoer ingen API-kall,
leser ingen filer og kjenner ingen HTML. Derfor kan hele fila testes uten
nett, og visningen kan byttes uten at noe her endres.

Kolonnene er de fem i FR-101 og ikke flere: selskap, sluttkurs, endring,
signalstyrke og retning. Hvor gamle dataene er, staar over tabellen og, for en
rad som er eldre enn de andre, under selskapsnavnet (story 1.4c).
"""

from dataclasses import dataclass, replace
from datetime import date, datetime
from zoneinfo import ZoneInfo

from boersdag import UtenforKalenderen
from kursdata import Aksje, Kursrad
from oversiktsdata import Oversiktspost
from signalberegning import BLANDET, INGEN, NEGATIV, POSITIV, STANDARD, Parametre, nodvendige_dager
from tallformat import dato, fortegn, tall, ukedag
from tilstand import Art, Tilstand, tilstand
from vurderingsdata import Grunn, Vurdering


@dataclass(frozen=True)
class Retningsvisning:
    """De tre kanalene i FR-103.

    Alle tre er obligatoriske. Teksten baerer, symbol og farge forsterker.
    Farge alene utelukker fargeblinde, og blandet lar seg ikke uttrykke
    lesbart i farge i det hele tatt.
    """

    tekst: str
    symbol: str
    klasse: str


# Visningen bruker FR-704s ordforraad uendret. Det fantes en oversettelse her
# - Positiv ble vist som "Opp" - og den er fjernet, ikke dokumentert.
#
# Grunnen: "Opp" og "Ned" staar rett ved siden av kolonnen Endring og inviterer
# til aa lese pilen som kursbevegelse. Retningen sier noe annet - hva de tre
# sjekkene peker mot. Briefen slaar fast at signalstyrke ikke er en anbefaling
# om kjoep eller salg, og Opp/Ned lener seg mot nettopp den lesningen.
#
# Teksten bygges derfor AV konstanten, ikke ved siden av den. Da kan de to
# ikke drive fra hverandre senere.
_SYMBOL_OG_KLASSE: dict[str, tuple[str, str]] = {
    POSITIV: ("↑", "opp"),
    NEGATIV: ("↓", "ned"),
    BLANDET: ("↔", "blandet"),
    INGEN: ("–", "ingen"),
}

RETNINGSVISNING: dict[str, Retningsvisning] = {
    retning: Retningsvisning(retning, symbol, klasse) for retning, (symbol, klasse) in _SYMBOL_OG_KLASSE.items()
}

# Ikke en retning, men fravaeret av en vurdering. Se FR-101 og FR-102 om
# aksjer uten gyldig signal.
UKJENT_RETNING = Retningsvisning("Ukjent", "–", "ukjent")

# Tekstene under «–» naar raden ikke har en vurdering (story 2.2b, FR-409,
# NFR-08). Godkjent 03.10 kl. 22:30.
GRUNNTEKST: dict[Grunn, str] = {
    Grunn.SYMBOL_FEILET: "hentingen feilet",
    Grunn.KURS_IKKE_FRA_DAGEN: "ingen kurs fra dagen",
    Grunn.SIGNAL_IKKE_REGNET: "signalet kunne ikke regnes",
}
IKKE_VURDERT = "ikke vurdert"
IKKE_BOERSDAG = "ikke børsdag"
UTENFOR_KALENDEREN = "utenfor børskalenderen"
# Datoen til nyeste kurs er etter dagens dato. Skjer bare med en klokke eller
# en kilde som tar feil, og vises da i stedet for en feilside.
ETTER_I_DAG = "datoen er etter i dag"


def les_tilstand(innhold: Vurdering | Grunn | None, dato: date, idag: date) -> tuple[Tilstand | None, str | None]:
    """Tilstanden for raden, og teksten som vises under «–».

    Teksten er None bare for en vurdering, ogsaa med styrke 0. En dato
    tilstand() ikke kan svare paa, gir ingen tilstand, bare teksten: en dato
    etter i dag sjekkes her foer kallet, og UtenforKalenderen fanges for seg.
    Andre feil fra tilstand() slipper gjennom.
    """
    if dato > idag:
        return None, ETTER_I_DAG
    try:
        utfall = tilstand(innhold, dato, idag)
    except UtenforKalenderen:
        return None, UTENFOR_KALENDEREN
    if utfall.art is Art.SVAR:
        return utfall, None
    if utfall.art is Art.GRUNN:
        return utfall, GRUNNTEKST[utfall.innhold]
    if utfall.art is Art.IKKE_KJOERT:
        return utfall, IKKE_VURDERT
    return utfall, IKKE_BOERSDAG


def grunn_med_tall(
    utfall: Tilstand | None, tekst: str | None, antall_dager: int | None, p: Parametre = STANDARD
) -> str | None:
    """Teksten under «–», med tallene når kursserien er for kort - story
    8.2a, d (gruppens svar 24.10 kl. 11:29).

    Raden og ruta i børsometeret sier hvorfor signalet ikke kunne regnes,
    med samme tall som aksjesiden: dagene serien har til og med dagen, og
    dagene signalet trenger (for_kort_serie i aksjedetalj.py). Bare når
    grunnen er «signalet kunne ikke regnes» og serien er kortere; ellers
    står teksten som før. Tallene formes av tall() i tallformat.py (regel 21).
    """
    trenger = nodvendige_dager(p)
    if (
        utfall is not None
        and utfall.art is Art.GRUNN
        and utfall.innhold is Grunn.SIGNAL_IKKE_REGNET
        and antall_dager is not None
        and antall_dager < trenger
    ):
        return f"for kort historikk: {tall(antall_dager, 'heltall')} av {tall(trenger, 'heltall')} dager"
    return tekst


# Bokstaven og feltet i Vurdering for hver sjekk, i samme rekkefoelge som
# paa aksjesiden (story 8.0e). Feltnavnet er ogsaa navnet som vises.
SJEKKBOKSTAVER = (("T", "trend"), ("B", "bevegelse"), ("I", "interesse"))


@dataclass(frozen=True)
class Rad:
    """En rad i markedsoversikten.

    tilstand er utfallet av tilstand() for datoen til nyeste kurs (FR-409).
    Har raden ingen vurdering, staar teksten under «–», og raden vises
    fortsatt - NFR-03 sier at manglende data for en aksje ikke skal stoppe
    hovedflyten.

    sist_hentet er naar symbolets serie sist ble hentet, i UTC (AD-20), fra
    kursserie gjennom Oversiktsleser (story 2.2b). erstatt_serie skriver kurs
    og kursserie i samme transaksjon (AD-5), saa en aksje med kurser har ogsaa
    en tid. None er den bare naar posten er laget uten tid, som i en test.
    """

    aksje: Aksje
    dato: date
    sluttkurs: float | None
    endring_prosent: float | None
    tilstand: Tilstand | None
    tekst: str | None
    skiller_seg_ut: bool = False
    sist_hentet: datetime | None = None
    # Story 8.17a: fra er dagen endringen for en periode er regnet fra, naar
    # serien ikke har startdagen. annen_dag er en dag valgt med «Velg dag»,
    # og tre_av_tre_siste er 3 av 3 paa siste boersdag, som gir gult ogsaa
    # da (designregler.md §3).
    fra: date | None = None
    annen_dag: bool = False
    tre_av_tre_siste: bool = False

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
    def ikke_vurdert(self) -> bool:
        return self.tekst == IKKE_VURDERT

    @property
    def sjekker(self) -> tuple[tuple[str, str, str], ...]:
        """T, B og I under «N av 3» (story 8.0e): bokstaven, navnet og
        verdien med fortegn, som «T +1». Lest fra den lagrede vurderingen,
        aldri regnet paa nytt (FR-101, AD-7). Tom uten vurdering, saa en rad
        med en grunn ikke viser noen."""
        if not self.vurdering:
            return ()
        return tuple((bokstav, felt, fortegn(getattr(self.vurdering, felt))) for bokstav, felt in SJEKKBOKSTAVER)


def endring_i_prosent(rader: list[Kursrad]) -> float | None:
    """Endring fra forrige boersdag, regnet paa utbyttejustert kurs (FR-101).

    Et ordinaert utbytte skal ikke se ut som et kursfall. Derfor justert kurs
    her, mens sluttkursen som vises er den ujusterte - det er den kursen
    aksjen faktisk omsettes til.
    """
    if len(rader) < 2:
        return None
    fra = rader[-2].justert_slutt
    til = rader[-1].justert_slutt
    return (til - fra) / fra * 100


def periodeendring(serie: list[Kursrad], start: date, slutt: date) -> tuple[float, date] | None:
    """Endringen i prosent fra startdagen til slutt, paa justert kurs som
    endringen for én dag (FR-101) - story 8.17a.

    Grunnlaget er raden paa startdagen. Har serien den ikke, er det foerste
    rad etter startdagen og foer slutt. Den andre verdien er dagen serien
    begynner, naar den begynner etter startdagen, saa raden kan si det, og
    ellers None: et hull i en lengre serie er ikke en kortere serie
    (gjennomgangen, ECH1 og ECH3). Er startdagen slutt, som I aar paa aarets
    foerste boersdag, er endringen 0 (ECH2). None naar serien ikke har
    slutt, eller ingen rad mellom."""
    paa_slutt = next((rad for rad in serie if rad.dato == slutt), None)
    if paa_slutt is None:
        return None
    if start == slutt:
        return 0.0, None
    fra = next((rad for rad in serie if start <= rad.dato < slutt), None)
    if fra is None:
        return None
    return endring_i_prosent([fra, paa_slutt]), (fra.dato if serie[0].dato > start else None)


def med_perioden(rader: list[Rad], serier: dict[str, list[Kursrad]], start: date) -> list[Rad]:
    """Radene med endringen for perioden, sortert etter FR-102 paa nytt -
    story 8.17a. start er startdagen fra perioder.startdag, regnet fra
    sidens siste boersdag, den samme for alle radene og linja over tabellen
    (gjennomgangen, BH3 og ECH5). Endringen gaar til radens siste boersdag.
    Sluttkursen, signalet og «skiller seg ut» gjelder fortsatt siste
    boersdag (gruppens svar 23.10 kl. 12:35, a)."""
    nye = []
    for rad in rader:
        utfall = periodeendring(serier.get(rad.aksje.symbol, []), start, rad.dato)
        endring, fra = utfall if utfall is not None else (None, None)
        nye.append(replace(rad, endring_prosent=endring, fra=fra))
    return sorted(nye, key=_sorteringsnokkel)


def bygg_rad_for_dag(
    post: Oversiktspost,
    serie: list[Kursrad],
    dag: date,
    innhold: Vurdering | Grunn | None,
    idag: date,
    tre_av_tre_siste: bool,
    p: Parametre = STANDARD,
) -> Rad:
    """Raden for en dag valgt med «Velg dag» - story 8.17a.

    Sluttkursen og endringen er dagens, fra kursserien, og vurderingen er
    raden i vurdering for dagen, eller teksten for hvorfor den mangler.
    Signalet regnes aldri (AD-7). 2 av 3 merkes ikke for en annen dag enn
    siste boersdag, saa skiller_seg_ut er usann, og gult kommer fra siste
    boersdag (designregler.md §3)."""
    foer = [rad for rad in serie if rad.dato <= dag]
    paa_dagen = foer[-1] if foer and foer[-1].dato == dag else None
    utfall, tekst = les_tilstand(innhold, dag, idag)
    tekst = grunn_med_tall(utfall, tekst, len(foer), p)
    # Gjennomgangen (ECH7, BH2): en boersdag uten kurs for aksjen, for
    # eksempel foer serien begynner, er ikke «ikke vurdert», men uten kurs.
    if paa_dagen is None and utfall is not None and utfall.art is Art.IKKE_KJOERT:
        tekst = GRUNNTEKST[Grunn.KURS_IKKE_FRA_DAGEN]
    return Rad(
        aksje=post.aksje,
        dato=dag,
        sluttkurs=float(paa_dagen.slutt) if paa_dagen else None,
        endring_prosent=endring_i_prosent(foer[-2:]) if paa_dagen else None,
        tilstand=utfall,
        tekst=tekst,
        sist_hentet=post.hentet,
        annen_dag=True,
        tre_av_tre_siste=tre_av_tre_siste,
    )


def bygg_rad(post: Oversiktspost, idag: date, p: Parametre = STANDARD, antall_dager: int | None = None) -> Rad | None:
    """En rad for en aksje. None bare naar aksjen ikke har en eneste kursrad.

    En aksje uten vurdering gir en rad UTEN styrke, ikke ingen rad. Brukeren
    skal se at aksjen finnes og at vurderingen mangler, ikke at aksjen er
    borte. Endringen regnes av de to siste kursene (FR-101). Signalet regnes
    ikke: styrken og retningen er radens, og «skiller seg ut» er den lagrede
    styrken mot terskelen (FR-705).

    antall_dager er dagene i kursserien. Story 8.2a, d: med dem sier raden
    hvorfor signalet ikke kunne regnes, som aksjesiden (grunn_med_tall).
    """
    siste = post.nyeste
    if siste is None:
        return None

    utfall, tekst = les_tilstand(post.innhold, siste.dato, idag)
    tekst = grunn_med_tall(utfall, tekst, antall_dager, p)
    rader = [r for r in (post.forrige, siste) if r is not None]
    styrke = utfall.innhold.styrke if utfall is not None and utfall.art is Art.SVAR else None
    return Rad(
        aksje=post.aksje,
        dato=siste.dato,
        sluttkurs=float(siste.slutt),
        endring_prosent=endring_i_prosent(rader),
        tilstand=utfall,
        tekst=tekst,
        skiller_seg_ut=styrke is not None and styrke >= p.terskel,
        sist_hentet=post.hentet,
    )


def _sorteringsnokkel(rad: Rad) -> tuple[int, float]:
    """FR-102: signalstyrke fallende, absolutt kursendring som andrekriterium.

    Rader uten vurdering sorteres sist, ogsaa bak styrke 0. FR-102 sier det
    selv: «Aksjer uten gyldig signal sorteres sist, uansett kursendring.»
    (Raadet 03.10: her sto at FR-102 ikke sa hvor de hoerer hjemme.)
    """
    styrke = rad.styrke if rad.styrke is not None else -1
    endring = abs(rad.endring_prosent) if rad.endring_prosent is not None else -1.0
    return (-styrke, -endring)


def sorter_fr102(rader: list[Rad]) -> list[Rad]:
    """Radene i FR-102-rekkefoelgen, som bygg_oversikt - story 8.17a, for
    radene for en dag valgt med «Velg dag»."""
    return sorted(rader, key=_sorteringsnokkel)


def bygg_oversikt(
    poster: list[Oversiktspost], idag: date, p: Parametre = STANDARD, antall_dager: dict[str, int] | None = None
) -> list[Rad]:
    """Alle radene, sortert etter FR-102.

    Aksjer uten kurser faller ut, og navngis av uten_kurser. Hver rad faar
    symbolets egen sist_hentet (FR-101, AD-15). Antallet er det som staar i
    aksje i basen, aldri et fast tall. antall_dager er dagene i kursserien
    per symbol, for grunnen med tall (story 8.2a, d).
    """
    dager = antall_dager or {}
    rader = [
        rad for rad in (bygg_rad(post, idag, p, dager.get(post.aksje.symbol)) for post in poster) if rad is not None
    ]
    return sorted(rader, key=_sorteringsnokkel)


def uten_kurser(poster: list[Oversiktspost]) -> list[Aksje]:
    """Aksjene i aksje som ikke har en eneste kursrad (FR-101). Siden viser
    navnet med lenke til aksjesiden (gruppens svar 23.10 kl. 09:24, b)."""
    return [post.aksje for post in poster if post.nyeste is None]


# Story 8.2a, b (U23, gruppens svar 24.10 kl. 11:34 og 11:35): teksten under
# «–» i raden for en aksje uten en eneste kurs.
# Gjennomgangen 24.10 (BH13): et annet navn enn UTEN_DATA i boersometer.py,
# som har stor forbokstav.
UTEN_DATA_TEKST = "uten data"


@dataclass(frozen=True)
class RadUtenData:
    """Raden for en aksje uten en eneste kurs - story 8.2a, b (U23).

    Hver aksje i lista har en rad, så tallet i overskriften stemmer med
    tabellen. Raden står nederst, som Varde Systemer i demoen: navnet som
    lenke, «–» i hver kolonne og «uten data». Den har de feltene malen og
    sorteringen leser, uten verdier, så den står sist i FR-102 og i hver
    sortering på en kolonne med tall. Den har ingen dato og ingen tid, og
    er derfor ikke med blant radene datoen og tidspunktet på siden regnes av.
    """

    aksje: Aksje
    tekst: str = UTEN_DATA_TEKST
    sluttkurs: None = None
    endring_prosent: None = None
    tilstand: None = None
    dato: None = None
    sist_hentet: None = None
    skiller_seg_ut: bool = False
    vurdering: None = None
    styrke: None = None
    ikke_vurdert: bool = False
    sjekker: tuple = ()
    retning: Retningsvisning = UKJENT_RETNING


def rader_uten_data(poster: list[Oversiktspost]) -> list[RadUtenData]:
    """En RadUtenData per aksje uten kurser, i rekkefølgen i lista."""
    return [RadUtenData(aksje) for aksje in uten_kurser(poster)]


def sidens_tidsstempel(rader: list[Rad]) -> datetime | None:
    """Det eldste sist_hentet blant radene som vises (FR-101).

    Det eldste og ikke det nyeste: med en fersk rad og fjorten foreldede
    ville det nyeste faatt hele siden til aa se fersk ut. None uten rader.
    """
    tider = [rad.sist_hentet for rad in rader if rad.sist_hentet is not None]
    return min(tider) if tider else None


def sidens_dato(rader: list[Rad]) -> date | None:
    """Den eldste datoen blant radene som vises (story 8.0).

    Samme prinsipp som sidens_tidsstempel og FR-101 («Hvor gamle dataene
    er»): siden skal aldri se ferskere ut enn den er, og datoen skal ikke
    avhenge av sorteringen. Foer 8.0 sto datoen til den foerste raden, altsaa
    den med sterkest signal. None uten rader.
    """
    return min((rad.dato for rad in rader), default=None)


def ingen_skilte_seg_ut(rader: list[Rad]) -> bool:
    """Skal oversikten si at ingen aksjer skilte seg ut? - story 8.0c.

    Ja naar minst én rad har en vurdering og ingen rad har styrke paa
    terskelen eller mer (FR-705). Uten en eneste vurdering sier setningen
    ingenting sant, og da staar den ikke (tillegget 05.10).
    """
    vurdert = [rad for rad in rader if rad.styrke is not None]
    return bool(vurdert) and not any(rad.skiller_seg_ut for rad in vurdert)


def del_i_to(rader: list[Rad]) -> tuple[list[Rad], list[Rad]]:
    """Radene som skilte seg ut, og de oevrige - story 8.0e.

    Delingen er skiller_seg_ut, altsaa den lagrede styrken mot terskelen i
    Parametre (FR-705). Rekkefoelgen fra bygg_oversikt beholdes, saa hver del
    er sortert etter FR-102. Rader uten vurdering havner i de oevrige.
    """
    ut = [rad for rad in rader if rad.skiller_seg_ut]
    oevrige = [rad for rad in rader if not rad.skiller_seg_ut]
    return ut, oevrige


# Story 8.15: kolonnene som kan sorteres ved klikk, med navnet i linja over
# tabellen («Sortert på endring, synkende») og retningen ved første klikk.
# Svar 1: synkende først, størst først. Svar 2: Retning er en gruppering i
# alfabetisk rekkefølge, A til Å først, ikke en rangering (NFR-06).
# Story 8.15b (gruppens svar 18.10 kl. 22:06): Selskap sorteres A til Å
# først, i den norske rekkefølgen fra _navn.
SYNKENDE = "synkende"
STIGENDE = "stigende"
SORTERBARE: dict[str, tuple[str, str]] = {
    "selskap": ("selskap", STIGENDE),
    "kurs": ("sluttkurs", SYNKENDE),
    "endring": ("endring", SYNKENDE),
    "signal": ("signalstyrke", SYNKENDE),
    "retning": ("retning", STIGENDE),
}
RETNINGSGRUPPER = tuple(sorted((POSITIV, NEGATIV, BLANDET, INGEN)))


@dataclass(frozen=True)
class Sortering:
    """Kolonnen og retningen fra adressen - story 8.15.

    fra_adressen gir None for alt den ikke kjenner, også en kolonne uten
    retning. Da gjelder FR-102, og siden feiler ikke."""

    kolonne: str
    orden: str

    def __post_init__(self) -> None:
        # Gjennomgangen (BH9): en Sortering laget direkte, for eksempel i
        # Min liste (8.3), kan ikke ha en kolonne navn og neste_orden ikke
        # kjenner.
        if self.kolonne not in SORTERBARE or self.orden not in (SYNKENDE, STIGENDE):
            raise ValueError(f"ukjent sortering: {self.kolonne!r}, {self.orden!r}")

    @classmethod
    def fra_adressen(cls, kolonne: str | None, orden: str | None) -> "Sortering | None":
        if kolonne in SORTERBARE and orden in (SYNKENDE, STIGENDE):
            return cls(kolonne, orden)
        return None

    @property
    def navn(self) -> str:
        return SORTERBARE[self.kolonne][0]


def neste_orden(kolonne: str, valgt: Sortering | None) -> str:
    """Retningen et klikk på kolonnen gir: den motsatte når kolonnen er
    valgt, ellers første klikk (svar 1 og 2)."""
    if valgt is not None and valgt.kolonne == kolonne:
        return STIGENDE if valgt.orden == SYNKENDE else SYNKENDE
    return SORTERBARE[kolonne][1]


def _verdi(rad: Rad, kolonne: str) -> float | int | str | None:
    """Verdien raden sorteres på, eller None når den mangler. Endring er i
    prosent med fortegn (FR-101, svar 1). Retning er plassen i alfabetet, og
    Ukjent har ingen. Selskap er navnet i norsk rekkefølge (story 8.15b)."""
    if kolonne == "selskap":
        return _navn(rad)
    if kolonne == "kurs":
        return rad.sluttkurs
    if kolonne == "endring":
        return rad.endring_prosent
    if kolonne == "signal":
        return rad.styrke
    if rad.vurdering is None or rad.vurdering.retning not in RETNINGSGRUPPER:
        return None
    return RETNINGSGRUPPER.index(rad.vurdering.retning)


# Gjennomgangen (ECH4): navnet ved lik verdi sorteres i norsk alfabet, med
# Æ, Ø og Å etter Z, og uten forskjell på store og små bokstaver.
_NORSK = str.maketrans({"æ": "{", "ø": "|", "å": "}"})


def _navn(rad: Rad) -> str:
    return rad.aksje.navn.casefold().translate(_NORSK)


def sorter(rader: list[Rad], sortering: Sortering | None) -> list[Rad]:
    """Radene sortert på kolonnen - story 8.15.

    Først FR-102 og så navnet, så lik verdi alltid står likt. Så kolonnen,
    der bare den snus. Rader uten verdi står sist i begge retninger. Uten
    sortering er rekkefølgen den samme som før, FR-102 fra bygg_oversikt.
    Story 8.2a, e (gruppens svar 24.10 kl. 11:39): ruten kaller den for hele
    lista, med radene uten data, så tabellen er én liste uten delene. Før
    kalte den den for hver del etter del_i_to (tillegget 13.10)."""
    if sortering is None:
        return list(rader)
    grunn = sorted(rader, key=lambda rad: (_sorteringsnokkel(rad), _navn(rad)))
    med = [rad for rad in grunn if _verdi(rad, sortering.kolonne) is not None]
    # Gjennomgangen 24.10 (ECH3): radene uten data sist blant dem uten verdi,
    # også når en rad med kurs har samme nøkkel i FR-102.
    uten = sorted(
        (rad for rad in grunn if _verdi(rad, sortering.kolonne) is None), key=lambda rad: isinstance(rad, RadUtenData)
    )
    # Gjennomgangen (BH8): sort er stabil også med reverse=True, så lik
    # verdi beholder rekkefølgen fra grunn, FR-102 og navnet, i begge
    # retninger. Snus grunn eller nøkkelen i stedet, går det tapt.
    med.sort(key=lambda rad: _verdi(rad, sortering.kolonne), reverse=sortering.orden == SYNKENDE)
    return med + uten


def antall_vurdert(rader: list[Rad]) -> int:
    """Hvor mange rader som har en vurdering - story 8.0c, svar 3 paa
    BH1/ECH2. Siden sier «N av M aksjer ble vurdert.» naar det er faerre
    enn alle."""
    return sum(1 for rad in rader if rad.styrke is not None)


def eldre_enn_nyeste(rader: list[Rad]) -> set[str]:
    """Symbolene som skal vise sitt eget tidsstempel under selskapsnavnet.

    Det er radene som er eldre enn den nyeste. Er alle like ferske, er
    mengden tom, og bare sidens tidsstempel vises.
    """
    tider = [rad.sist_hentet for rad in rader if rad.sist_hentet is not None]
    if not tider:
        return set()
    nyeste = max(tider)
    return {rad.aksje.symbol for rad in rader if rad.sist_hentet is not None and rad.sist_hentet < nyeste}


NORSK_TID = ZoneInfo("Europe/Oslo")


def norsk_tid(tid: datetime, i_aar: int) -> str:
    """Et tidspunkt som «24.09 kl. 20.05» i norsk tid (AD-20, story 8.0c).

    Modellen har UTC; soneskiftet skjer foerst her, i visningen. Europe/Oslo
    og ikke en fast forskyvning, saa sommer- og vintertid begge blir riktige.
    Datoen formes av dato() i tallformat.py (regel 21), med aar bare naar
    aaret er et annet enn i_aar, aaret i dag fra app.idag(). i_aar er
    paakrevd, saa en kaller ikke kan miste aaret uten aa merke det.
    """
    lokal = tid.astimezone(NORSK_TID)
    return f"{dato(lokal.date(), i_aar)} kl. {lokal:%H.%M}"


def oppdatert(tid: datetime, i_aar: int) -> str:
    """Tidspunktet i stripa: «tirsdag 13.10 kl. 22.15» - story 8.0d.

    Ukedagen er dagen i norsk tid, som datoen og klokkeslettet fra
    norsk_tid. En henting kl. 22.30 UTC en torsdag om sommeren er fredag i
    Norge, og ukedagen sier fredag.
    """
    return f"{ukedag(tid.astimezone(NORSK_TID).date())} {norsk_tid(tid, i_aar)}"
