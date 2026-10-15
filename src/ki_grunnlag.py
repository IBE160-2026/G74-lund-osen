"""Grunnlaget som sendes til modellen - story 10.1, plan B, betingelse 4.

Én ren funksjon bestemmer hva modellen faar, saa ingen kan sende raadata ved
et uhell. Modellen faar bare vaare egne resultater: fortegnet for hver av de
tre sjekkene, styrken og retningen (prd.md §4.6, avgjort 2026-10-04). Ingen
kurser, volumer, prosenter eller forholdstall, og ingen maalinger. «Antall»
gjelder dagsteksten i 10.6, ikke grunnlaget for én aksje (svar 10 kl. 15:53).

En aksje utenfor de 15 (FR-412) faar de samme verdiene og merket
«Utenfor målingen», saa teksten kan si at grensene ikke er maalt paa den.
Kalleren maa si fra hver gang, saa merket ikke kan glemmes.

Grunnlaget er en mapping som ikke kan endres, med tekst som noekler og bare
heltall og tekst fra en lukket liste som verdier. Det er det KIRad.grunnlag
lagrer (story 4.2), og det 10.3 sammenligner med vurderingen (FR-602).

Ingenting gjoeres om: et tall som ikke allerede er et heltall i omraadet,
avvises, i stedet for aa bli rundet av til noe som ser gyldig ut. Feilene
nevner bare feltet og typen, aldri verdien, saa en raa verdi ikke havner i
en logg (regel 16, gjennomgangen av 10.1).
"""

from types import MappingProxyType

from signalberegning import BLANDET, INGEN, NEGATIV, POSITIV, Signal, finn_retning, finn_styrke
from vurderingsdata import Vurdering

RETNINGER = (POSITIV, NEGATIV, BLANDET, INGEN)
SJEKKENE = ("trend", "bevegelse", "interesse")
UTENFOR_MAALINGEN = "Utenfor målingen"
NOEKLENE = frozenset((*SJEKKENE, "styrke", "retning"))


def _heltall(verdi) -> bool:
    return type(verdi) is int


def ki_grunnlag(kilde: Signal | Vurdering, *, utenfor_maalingen: bool) -> MappingProxyType:
    """Fortegnene, styrken og retningen, og ingenting annet.

    kilde er signalet fra signalberegning eller vurderingen fra basen. Begge
    har de samme tre fortegnene, styrken og retningen. Et Signal kontrolleres
    ikke naar det lages, saa her sjekkes det at styrken og retningen er de
    sjekkene gir, slik Vurdering gjoer.
    """
    if type(utenfor_maalingen) is not bool:
        raise TypeError("utenfor_maalingen maa vaere True eller False")
    if isinstance(kilde, Signal):
        navn = [sjekk.navn for sjekk in kilde.sjekker]
        if navn != [s.capitalize() for s in SJEKKENE]:
            raise ValueError("sjekkene maa vaere Trend, Bevegelse og Interesse, én av hver")
        fortegn = {s: sjekk.verdi for s, sjekk in zip(SJEKKENE, kilde.sjekker)}
    elif isinstance(kilde, Vurdering):
        fortegn = {s: getattr(kilde, s) for s in SJEKKENE}
    else:
        raise TypeError(f"kilde maa vaere Signal eller Vurdering, fikk {type(kilde).__name__}")

    grunnlag: dict[str, object] = dict(fortegn)
    grunnlag["styrke"] = kilde.styrke
    grunnlag["retning"] = kilde.retning
    if utenfor_maalingen:
        grunnlag["merke"] = UTENFOR_MAALINGEN
    _kontroller(grunnlag)
    if isinstance(kilde, Signal):
        _samsvar(kilde)
    return MappingProxyType(grunnlag)


def _kontroller(grunnlag: dict[str, object]) -> None:
    """Siste vakt: noeklene, og bare heltall og tekst fra de lukkede listene."""
    if set(grunnlag) - {"merke"} != NOEKLENE:
        raise ValueError("grunnlaget har andre noekler enn fortegnene, styrken og retningen")
    if grunnlag.get("merke", UTENFOR_MAALINGEN) != UTENFOR_MAALINGEN:
        raise ValueError("merke kan bare vaere «Utenfor målingen»")
    for navn in SJEKKENE:
        if not _heltall(grunnlag[navn]) or grunnlag[navn] not in (-1, 0, 1):
            raise ValueError(f"{navn} maa vaere heltallet -1, 0 eller 1, fikk {type(grunnlag[navn]).__name__}")
    if not _heltall(grunnlag["styrke"]) or grunnlag["styrke"] not in (0, 1, 2, 3):
        raise ValueError(f"styrke maa vaere et heltall fra 0 til 3, fikk {type(grunnlag['styrke']).__name__}")
    if type(grunnlag["retning"]) is not str or grunnlag["retning"] not in RETNINGER:
        raise ValueError(f"retning maa vaere en av {RETNINGER}")


def _samsvar(signal: Signal) -> None:
    if signal.styrke != finn_styrke(signal.sjekker) or signal.retning != finn_retning(signal.sjekker):
        raise ValueError("styrken eller retningen stemmer ikke med sjekkene")
