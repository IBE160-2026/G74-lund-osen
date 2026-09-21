"""Markedsoversikten - FR-101 til FR-103.

Ren logikk. Leser gjennom Kurskilde og regner med signalberegning. Gjoer ingen
API-kall, leser ingen filer og kjenner ingen HTML. Derfor kan hele fila testes
uten nett, og visningen kan byttes uten at noe her endres.

Kolonnene er de fem i FR-101 og ikke flere: selskap, sluttkurs, endring,
signalstyrke og retning.
"""

from dataclasses import dataclass

from kursdata import AKSJEUNIVERS, Aksje, Kurskilde
from signalberegning import (
    BLANDET,
    INGEN,
    NEGATIV,
    POSITIV,
    Parametre,
    STANDARD,
    Signal,
    beregn_signal,
)


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


# FR-704 navngir retningene Positiv, Negativ, Blandet og Ingen. FR-103 viser
# dem som Opp, Ned, Blandet og Ingen utslag. Det er to ordforraad for det
# samme, og oversettelsen hoerer hjemme her - i visningen - ikke i modellen.
RETNINGSVISNING: dict[str, Retningsvisning] = {
    POSITIV: Retningsvisning("Opp", "↑", "opp"),
    NEGATIV: Retningsvisning("Ned", "↓", "ned"),
    BLANDET: Retningsvisning("Blandet", "↔", "blandet"),
    INGEN: Retningsvisning("Ingen utslag", "–", "ingen"),
}

UKJENT_RETNING = Retningsvisning("Ukjent", "–", "ukjent")


@dataclass(frozen=True)
class Rad:
    """En rad i markedsoversikten.

    signal er None naar serien er for kort til aa regne. Da staar mangler med
    grunnen, og raden vises fortsatt - NFR-03 sier at manglende data for en
    aksje ikke skal stoppe hovedflyten.
    """

    aksje: Aksje
    dato: str
    sluttkurs: float
    endring_prosent: float | None
    signal: Signal | None
    mangler: str | None

    @property
    def styrke(self) -> int | None:
        return self.signal.styrke if self.signal else None

    @property
    def retning(self) -> Retningsvisning:
        if not self.signal:
            return UKJENT_RETNING
        return RETNINGSVISNING.get(self.signal.retning, UKJENT_RETNING)

    @property
    def skiller_seg_ut(self) -> bool:
        return bool(self.signal and self.signal.skiller_seg_ut)


def _justert(rad: dict) -> float | None:
    verdi = rad.get("adjusted_close") or rad.get("close")
    return float(verdi) if verdi else None


def endring_i_prosent(rader: list[dict]) -> float | None:
    """Endring fra forrige boersdag, regnet paa utbyttejustert kurs (FR-101).

    Et ordinaert utbytte skal ikke se ut som et kursfall. Derfor justert kurs
    her, mens sluttkursen som vises er den ujusterte - det er den kursen
    aksjen faktisk omsettes til.
    """
    if len(rader) < 2:
        return None
    fra = _justert(rader[-2])
    til = _justert(rader[-1])
    if not fra or til is None:
        return None
    return (til - fra) / fra * 100


def bygg_rad(aksje: Aksje, rader: list[dict], p: Parametre = STANDARD) -> Rad | None:
    """En rad for en aksje. None bare naar vi ikke har en eneste kursrad.

    En for kort serie gir en rad UTEN signal, ikke ingen rad. Brukeren skal
    se at aksjen finnes og at signalet mangler, ikke at aksjen er borte.
    """
    if not rader:
        return None

    siste = rader[-1]
    signal: Signal | None = None
    mangler: str | None = None
    try:
        signal = beregn_signal(rader, p)
    except ValueError as feil:
        mangler = str(feil)

    return Rad(
        aksje=aksje,
        dato=siste["date"],
        sluttkurs=float(siste["close"]),
        endring_prosent=endring_i_prosent(rader),
        signal=signal,
        mangler=mangler,
    )


def _sorteringsnokkel(rad: Rad) -> tuple[int, float]:
    """FR-102: signalstyrke fallende, absolutt kursendring som andrekriterium.

    Rader uten signal sorteres sist. FR-102 sier ikke hvor de hoerer hjemme -
    se aapent punkt om hull i kravene. Valget her er at en rad vi ikke kan
    vurdere, ikke skal legge seg foran en vi kan.
    """
    styrke = rad.styrke if rad.styrke is not None else -1
    endring = abs(rad.endring_prosent) if rad.endring_prosent is not None else -1.0
    return (-styrke, -endring)


def bygg_oversikt(
    kilde: Kurskilde,
    univers: tuple[Aksje, ...] = AKSJEUNIVERS,
    p: Parametre = STANDARD,
) -> list[Rad]:
    """Alle radene, sortert etter FR-102.

    Aksjer kilden ikke har data for, faller ut. De telles av kallende kode
    saa brukeren kan faa vite at oversikten er ufullstendig.
    """
    rader = [
        rad
        for rad in (bygg_rad(aksje, kilde.serie(aksje.symbol), p) for aksje in univers)
        if rad is not None
    ]
    return sorted(rader, key=_sorteringsnokkel)
