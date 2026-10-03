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

from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

from boersdag import UtenforKalenderen
from kursdata import Aksje, Kursrad
from oversiktsdata import Oversiktspost
from signalberegning import BLANDET, INGEN, NEGATIV, POSITIV, Parametre, STANDARD
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
    retning: Retningsvisning(retning, symbol, klasse)
    for retning, (symbol, klasse) in _SYMBOL_OG_KLASSE.items()
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


def les_tilstand(
    innhold: Vurdering | Grunn | None, dato: date, idag: date
) -> tuple[Tilstand | None, str | None]:
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
    sluttkurs: float
    endring_prosent: float | None
    tilstand: Tilstand | None
    tekst: str | None
    skiller_seg_ut: bool = False
    sist_hentet: datetime | None = None

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


def bygg_rad(post: Oversiktspost, idag: date, p: Parametre = STANDARD) -> Rad | None:
    """En rad for en aksje. None bare naar aksjen ikke har en eneste kursrad.

    En aksje uten vurdering gir en rad UTEN styrke, ikke ingen rad. Brukeren
    skal se at aksjen finnes og at vurderingen mangler, ikke at aksjen er
    borte. Endringen regnes av de to siste kursene (FR-101). Signalet regnes
    ikke: styrken og retningen er radens, og «skiller seg ut» er den lagrede
    styrken mot terskelen (FR-705).
    """
    siste = post.nyeste
    if siste is None:
        return None

    utfall, tekst = les_tilstand(post.innhold, siste.dato, idag)
    rader = [r for r in (post.forrige, siste) if r is not None]
    styrke = (
        utfall.innhold.styrke if utfall is not None and utfall.art is Art.SVAR else None
    )
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


def bygg_oversikt(
    poster: list[Oversiktspost], idag: date, p: Parametre = STANDARD
) -> list[Rad]:
    """Alle radene, sortert etter FR-102.

    Aksjer uten kurser faller ut, og navngis av uten_kurser. Hver rad faar
    symbolets egen sist_hentet (FR-101, AD-15). Antallet er det som staar i
    aksje i basen, aldri et fast tall.
    """
    rader = [rad for rad in (bygg_rad(post, idag, p) for post in poster) if rad is not None]
    return sorted(rader, key=_sorteringsnokkel)


def uten_kurser(poster: list[Oversiktspost]) -> list[str]:
    """Navnene paa aksjene i aksje som ikke har en eneste kursrad (FR-101)."""
    return [post.aksje.navn for post in poster if post.nyeste is None]


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


def eldre_enn_nyeste(rader: list[Rad]) -> set[str]:
    """Symbolene som skal vise sitt eget tidsstempel under selskapsnavnet.

    Det er radene som er eldre enn den nyeste. Er alle like ferske, er
    mengden tom, og bare sidens tidsstempel vises.
    """
    tider = [rad.sist_hentet for rad in rader if rad.sist_hentet is not None]
    if not tider:
        return set()
    nyeste = max(tider)
    return {
        rad.aksje.symbol
        for rad in rader
        if rad.sist_hentet is not None and rad.sist_hentet < nyeste
    }


NORSK_TID = ZoneInfo("Europe/Oslo")


def norsk_tid(tid: datetime) -> str:
    """Et tidspunkt som ÅÅÅÅ-MM-DD kl. TT.MM i norsk tid (AD-20).

    Modellen har UTC; soneskiftet skjer foerst her, i visningen. Europe/Oslo
    og ikke en fast forskyvning, saa sommer- og vintertid begge blir riktige.
    """
    lokal = tid.astimezone(NORSK_TID)
    return lokal.strftime("%Y-%m-%d kl. %H.%M")
