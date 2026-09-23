"""Signalberegningen - FR-701 til FR-705.

Ren logikk. Denne filen gjoer ingen API-kall og leser ingen filer, saa den
kan testes i sin helhet uten aa bruke av kvoten.

Alle beregninger bruker utbyttejustert kurs (FR-701), slik at et ordinaert
utbytte ikke feiltolkes som kursfall.

Terskel, volumfaktor og noytralsone er LAAST 21.09.2026, etter en test mot
199 handelsdager - 2985 aksjedager - der alle tre verdiene holdt uendret.
Metode og tall i malinger.md §7.4.

Vinduene paa 20 dager i bevegelse og interesse ble maalt 22.09.2026 mot like
mange aksjedager, 2985, i et vindu forskjoevet en handelsdag (til og med 21.09,
ikke 18.09), se malinger.md §9. Alle fem parametrene er dermed laast med
maaling bak seg.
"""

from dataclasses import dataclass
from statistics import median, stdev

MA_VINDU = 50

# Laast 21.09.2026 mot 199 handelsdager, se malinger.md §7.4.
NOYTRALSONE = 0.02   # +/-1 % gir bare 5,6 % styrke 0, +/-4 % gir 25,7 %
VOLUMFAKTOR = 1.5    # 1,25x utloeser nesten alltid, 2,0x toemmer terskel 3
TERSKEL = 2          # gir 4,6 av 15 per dag; terskel 3 gir 1,1 og 87 tomme dager

# Maalt 22.09.2026 mot 2985 aksjedager til og med 21.09, se malinger.md §9. Alt
# mellom 15 og 30 oppfoerer seg tilnaermet likt; under 15 blir valget ustabilt.
VOLATILITET_VINDU = 20
VOLUM_VINDU = 20

POSITIV = "Positiv"
NEGATIV = "Negativ"
BLANDET = "Blandet"
INGEN = "Ingen"


@dataclass(frozen=True)
class Parametre:
    """Samlet slik at testene kan bruke korte vinduer paa haandlagde serier.

    Standardverdiene er de som gjelder i applikasjonen.
    """

    ma_vindu: int = MA_VINDU
    noytralsone: float = NOYTRALSONE
    volatilitet_vindu: int = VOLATILITET_VINDU
    volum_vindu: int = VOLUM_VINDU
    volumfaktor: float = VOLUMFAKTOR
    terskel: int = TERSKEL


STANDARD = Parametre()


@dataclass(frozen=True)
class Sjekk:
    """En av de tre sjekkene, med verdien den ga i dag.

    FR-706 krever at hver sjekk vises ved navn med sin egen verdi, ikke bare
    den samlede styrken. Derfor baerer hver sjekk navnet sitt hit ut.
    """

    navn: str
    verdi: int
    forklaring: str


@dataclass(frozen=True)
class Signal:
    styrke: int
    retning: str
    sjekker: tuple[Sjekk, ...]
    skiller_seg_ut: bool


def _justerte_kurser(rader: list[dict]) -> list[float]:
    """adjusted_close naar den finnes, ellers close.

    EODHD regner adjusted_close om bakover ved hvert nytt utbytte. Det er
    grunnen til at beregningsgrunnlaget lastes ned i sin helhet ved hver
    henting (FR-406) og aldri skjoetes paa.
    """
    return [float(rad.get("adjusted_close") or rad["close"]) for rad in rader]


def _volumer(rader: list[dict]) -> list[float]:
    return [float(rad.get("volume") or 0) for rad in rader]


def _endringer(kurser: list[float]) -> list[float]:
    """Relative endringer fra dag til dag. Ett element kortere enn serien."""
    return [(ny - gammel) / gammel for gammel, ny in zip(kurser, kurser[1:]) if gammel]


def _fortegn(tall: float) -> int:
    if tall > 0:
        return 1
    if tall < 0:
        return -1
    return 0


def _nodvendige_dager(p: Parametre) -> int:
    """Lengste vinduet pluss dagen som maales mot det."""
    return max(p.ma_vindu, p.volatilitet_vindu + 1, p.volum_vindu) + 1


def trend(kurser: list[float], p: Parametre = STANDARD) -> Sjekk:
    """Sjekk 1: sluttkurs mot glidende snitt, med noytralsone (FR-702).

    Noytralsonen er obligatorisk, ikke kosmetikk. Uten den kan signalstyrke 0
    ikke forekomme - en aksje ligger alltid enten over eller under sitt eget
    snitt - og 64 % av aksjedagene havner paa styrke 1.
    """
    snitt = sum(kurser[-p.ma_vindu :]) / p.ma_vindu
    avvik = (kurser[-1] - snitt) / snitt

    # Grensen hoerer til sonen: noeyaktig 2 % over snittet gir 0, ikke +1.
    verdi = 0 if abs(avvik) <= p.noytralsone else _fortegn(avvik)
    return Sjekk(
        navn="Trend",
        verdi=verdi,
        forklaring=f"{avvik * 100:+.1f} % mot MA{p.ma_vindu}",
    )


def bevegelse(kurser: list[float], p: Parametre = STANDARD) -> Sjekk:
    """Sjekk 2: dagens endring mot aksjens egen volatilitet.

    Historikken regnes uten dagens endring. Ellers ville en stor bevegelse
    vaere med paa aa heve terskelen den selv skal maales mot, og store dager
    ville systematisk undervurdere seg selv.
    """
    endringer = _endringer(kurser)
    dagens = endringer[-1]
    historikk = endringer[-(p.volatilitet_vindu + 1) : -1]
    avvik = stdev(historikk)

    verdi = _fortegn(dagens) if abs(dagens) > avvik else 0
    return Sjekk(
        navn="Bevegelse",
        verdi=verdi,
        forklaring=f"{dagens * 100:+.1f} % mot {avvik * 100:.1f} % standardavvik",
    )


def interesse(kurser: list[float], volumer: list[float], p: Parametre = STANDARD) -> Sjekk:
    """Sjekk 3: dagens volum mot eget medianvolum.

    Volum har ingen retning i seg selv, saa fortegnet foelger dagens
    kursendring: hoeyt volum paa en oppgangsdag gir +1, paa en nedgangsdag -1.
    """
    dagens_volum = volumer[-1]
    median_volum = median(volumer[-(p.volum_vindu + 1) : -1])
    dagens_endring = _endringer(kurser)[-1]

    slaar_ut = median_volum > 0 and dagens_volum > p.volumfaktor * median_volum
    verdi = _fortegn(dagens_endring) if slaar_ut else 0
    return Sjekk(
        navn="Interesse",
        verdi=verdi,
        forklaring=f"volum {dagens_volum:.0f} mot median {median_volum:.0f}",
    )


def finn_retning(sjekker: tuple[Sjekk, ...]) -> str:
    """Retningen leses av fortegnene til de sjekkene som ga utslag (FR-704).

    Blandet er et gyldig og informativt svar, ikke en feiltilstand.
    """
    utslag = [sjekk.verdi for sjekk in sjekker if sjekk.verdi != 0]
    if not utslag:
        return INGEN
    if all(verdi > 0 for verdi in utslag):
        return POSITIV
    if all(verdi < 0 for verdi in utslag):
        return NEGATIV
    return BLANDET


def beregn_signal(rader: list[dict], p: Parametre = STANDARD) -> Signal:
    """Tre sjekker, hver +1, 0 eller -1. Ingen vekting og ingen fjerde sjekk.

    Radene er kronologiske med nyeste sist, slik EODHD leverer dem.

    Serier som er for korte gir ValueError i stedet for et tall som ser
    plausibelt ut. Kallende kode avgjoer hva som vises - NFR-03 sier at
    manglende data ikke skal stoppe hovedflyten.
    """
    nodvendig = _nodvendige_dager(p)
    if len(rader) < nodvendig:
        raise ValueError(
            f"Trenger {nodvendig} dager for aa regne signal, fikk {len(rader)}"
        )

    kurser = _justerte_kurser(rader)
    volumer = _volumer(rader)

    sjekker = (
        trend(kurser, p),
        bevegelse(kurser, p),
        interesse(kurser, volumer, p),
    )

    styrke = sum(abs(sjekk.verdi) for sjekk in sjekker)
    return Signal(
        styrke=styrke,
        retning=finn_retning(sjekker),
        sjekker=sjekker,
        skiller_seg_ut=styrke >= p.terskel,
    )
