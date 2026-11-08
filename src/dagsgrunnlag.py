"""Grunnlaget for KI-teksten om dagen - story 10.6, FR-607, FR-412.

Én ren funksjon regner grunnlaget for hele boersdagen, av de lagrede
vurderingene, kursene og hovedindeksen. Hentingen sender det til modellen
(ki_dagen.py), og webserveren regner det paa nytt av det siden viser og
sammenligner (FR-607: teksten vises bare naar grunnlaget stemmer med det
siden viser). Derfor heter fila ikke ki_*: webserveren importerer aldri
KI-laget (AD-10).

Grunnlaget er bare antall og retninger, som FR-607 sier etter rettingen
05.10: hvor mange som skilte seg ut, retningene blant dem, hvor mange som
gikk bedre enn hovedindeksen, retningen paa hovedindeksen og hvor mange som
steg i hver bransje. Ingen kurs, prosent, volum eller forholdstall
(beslutningen 04.10). Antallet aksjer er lista som er aktiv, ikke 15
(tillegget 08.10, FR-412).

Spesifikasjonen spec-10-6-ki-teksten-om-dagen-paa-forsiden.md, spoersmaal
2-4: retningene gjelder dem som skilte seg ut, bransjene er de med minst
MINST_I_BRANSJEN aksjer med en endring, og ukedagen er med.
"""

from collections.abc import Mapping
from datetime import date
from types import MappingProxyType

from dagene import MINST_I_BRANSJEN, STEG, _endringen, _retningen_paa_dagen, bevegelse
from hovedindeks import indeksendring, sammenlign
from kursdata import Aksje, Kursrad
from signalberegning import BLANDET, NEGATIV, POSITIV, TERSKEL
from tallformat import ukedag
from vurderingsdata import Grunn, Vurdering

RETNINGENE = (POSITIV, NEGATIV, BLANDET)
# Feltene for retningene blant dem som skilte seg ut, i samme rekkefoelge.
SKILTE_SEG_UT = "skilte_seg_ut"
RETNINGSFELTENE = {POSITIV: "skilte_seg_ut_positiv", NEGATIV: "skilte_seg_ut_negativ", BLANDET: "skilte_seg_ut_blandet"}


def _indeksen_paa(serie: list[Kursrad], dag: date) -> float | None:
    """Endringen i hovedindeksen for dag, som paa forsiden (bygg_hovedindeks)."""
    til = [rad for rad in serie if rad.dato <= dag]
    if not til or til[-1].dato != dag:
        return None
    return indeksendring(til)


def dagsgrunnlag(
    dag: date,
    lista: tuple[Aksje, ...],
    vurderinger: Mapping[str, Vurdering | Grunn | None],
    serier: Mapping[str, list[Kursrad]],
    indeksserie: list[Kursrad] | None,
    terskel: int = TERSKEL,
) -> MappingProxyType | None:
    """Grunnlaget for dag, eller None naar ingen aksje i lista er vurdert den
    dagen: da er det ingenting aa si om dagen.

    vurderinger er den lagrede vurderingen for dag per symbol, eller en grunn
    eller None. serier er kursene for aksjene i lista, og indeksserie
    hovedindeksen, eller None naar basen ikke har den.
    """
    vurderte = [v for a in lista if isinstance(v := vurderinger.get(a.symbol), Vurdering)]
    if not vurderte:
        return None
    grunnlag: dict[str, object] = {"aksjer": len(lista), "ukedag": ukedag(dag)}
    indeksserie = indeksserie or []
    retning = _retningen_paa_dagen(indeksserie, dag)
    if retning is not None:
        grunnlag["hovedindeksen"] = retning
    sammenligning = sammenlign(
        dag, _indeksen_paa(indeksserie, dag), [(a.navn, list(serier.get(a.symbol, []))) for a in lista]
    )
    if sammenligning is not None:
        grunnlag["bedre_enn_indeksen"] = sammenligning.bedre
        grunnlag["med_kurs"] = sammenligning.med
    ut = [v for v in vurderte if v.styrke >= terskel]
    grunnlag[SKILTE_SEG_UT] = len(ut)
    for navn, felt in RETNINGSFELTENE.items():
        grunnlag[felt] = sum(1 for v in ut if v.retning == navn)
    bransjer: dict[str, dict[str, int]] = {}
    for sektor in dict.fromkeys(a.sektor for a in lista):
        endringer = [_endringen(list(serier.get(a.symbol, [])), dag) for a in lista if a.sektor == sektor]
        med = [e for e in endringer if e is not None]
        if len(med) < MINST_I_BRANSJEN:
            continue
        bransjer[sektor] = {"steg": sum(1 for e in med if bevegelse(e) == STEG), "med_endring": len(med)}
    if bransjer:
        grunnlag["bransjer"] = bransjer
    return MappingProxyType(grunnlag)


def som_vanlig(grunnlag: Mapping[str, object] | None) -> dict | None:
    """Grunnlaget som vanlige dict, saa to grunnlag kan sammenlignes, ogsaa
    et som er lest fra loggen (MappingProxyType paa alle nivaaer)."""
    if grunnlag is None:
        return None
    return {n: som_vanlig(v) if isinstance(v, Mapping) else v for n, v in grunnlag.items()}
