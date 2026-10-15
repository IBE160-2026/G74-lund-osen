"""Grunnlaget som sendes til modellen - story 10.1, plan B, betingelse 4.

Én ren funksjon bestemmer hva modellen faar, saa ingen kan sende raadata ved
et uhell. Modellen faar bare vaare egne resultater: fortegnet for hver av de
tre sjekkene, styrken og retningen (prd.md §4.6, avgjort 2026-10-04). Ingen
kurser, volumer, prosenter eller forholdstall, og ingen maalinger. «Antall»
gjelder dagsteksten i 10.6, ikke grunnlaget for én aksje (svar 10 kl. 15:53).

En aksje utenfor de 15 (FR-412) faar de samme verdiene og merket
«Utenfor målingen», saa teksten kan si at grensene ikke er maalt paa den.

Grunnlaget er en dict med tekst som noekler og bare heltall, tekst fra en
lukket liste og True eller False som verdier. Det er det KIRad.grunnlag
lagrer (story 4.2), og det 10.3 sammenligner med vurderingen (FR-602).
"""

from signalberegning import BLANDET, INGEN, NEGATIV, POSITIV, Signal
from vurderingsdata import Vurdering

RETNINGER = (POSITIV, NEGATIV, BLANDET, INGEN)
SJEKKENE = ("trend", "bevegelse", "interesse")
UTENFOR_MAALINGEN = "Utenfor målingen"


def ki_grunnlag(kilde: Signal | Vurdering, *, utenfor_maalingen: bool = False) -> dict[str, object]:
    """Fortegnene, styrken og retningen, og ingenting annet.

    kilde er signalet fra signalberegning eller vurderingen fra basen. Begge
    har de samme tre fortegnene, styrken og retningen.
    """
    if isinstance(kilde, Signal):
        fortegn = {sjekk.navn.lower(): sjekk.verdi for sjekk in kilde.sjekker}
    elif isinstance(kilde, Vurdering):
        fortegn = {navn: getattr(kilde, navn) for navn in SJEKKENE}
    else:
        raise TypeError(f"kilde maa vaere Signal eller Vurdering, fikk {type(kilde).__name__}")
    if not isinstance(utenfor_maalingen, bool):
        raise TypeError(f"utenfor_maalingen maa vaere True eller False, fikk {utenfor_maalingen!r}")
    if set(fortegn) != set(SJEKKENE):
        raise ValueError(f"sjekkene maa vaere {SJEKKENE}, fikk {tuple(fortegn)}")

    grunnlag: dict[str, object] = {navn: int(fortegn[navn]) for navn in SJEKKENE}
    grunnlag["styrke"] = int(kilde.styrke)
    grunnlag["retning"] = kilde.retning
    if utenfor_maalingen:
        grunnlag["merke"] = UTENFOR_MAALINGEN
    _kontroller(grunnlag)
    return grunnlag


def _kontroller(grunnlag: dict[str, object]) -> None:
    """Siste vakt: bare heltall -1 til 3 og tekst fra den lukkede lista."""
    for navn in SJEKKENE:
        if grunnlag[navn] not in (-1, 0, 1):
            raise ValueError(f"{navn} maa vaere -1, 0 eller 1, fikk {grunnlag[navn]!r}")
    if grunnlag["styrke"] not in (0, 1, 2, 3):
        raise ValueError(f"styrke maa vaere 0-3, fikk {grunnlag['styrke']!r}")
    if grunnlag["retning"] not in RETNINGER:
        raise ValueError(f"retning maa vaere en av {RETNINGER}, fikk {grunnlag['retning']!r}")
