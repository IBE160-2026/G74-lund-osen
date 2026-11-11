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

Story 10.10 (gruppens svar 10.11 kl. 16:18): grunnlaget har ogsaa navnene
paa aksjene som skilte seg ut, med styrken og retningen for hver, 3 av 3
foerst og hoeyst MEST_NAVN navn, og resten som antall, og bransjen med
hoeyest og lavest snitt, regnet som snittet paa Boersometeret (snitt i
boersometer.py: endringen for aksjene i bransjen som har en endring).
Bransjene er de samme som i feltet bransjer. Snittene sammenlignes slik de
vises, med to desimaler, og to like snitt gir ingen bransje (spoersmaal 1 og
2 i spec-10-10-rikere-ki-tekster.md). Navnene staar i rekkefoelgen styrke,
navn og symbol, ikke tabellens, fordi forsiden regner grunnlaget paa nytt
med sorteringen den har (spoersmaal 3). Ingen kurs, prosent eller
forholdstall: bare navn, antall og retninger, som foer.

Rader laget med promptversjon dag-1 har ikke de nye feltene.
for_promptversjon tar dem ut, saa forsiden kan sammenligne en gammel rad
med grunnlaget regnet naa (spoersmaal 5).
"""

from collections.abc import Mapping
from datetime import date
from types import MappingProxyType

from dagene import MINST_I_BRANSJEN, STEG, _endringen, _retningen_paa_dagen, bevegelse
from hovedindeks import indeksendring, sammenlign
from kursdata import Aksje, Kursrad
from signalberegning import BLANDET, NEGATIV, POSITIV, STANDARD
from tallformat import avrundet, ukedag
from vurderingsdata import Grunn, Vurdering

RETNINGENE = (POSITIV, NEGATIV, BLANDET)
# Feltene for retningene blant dem som skilte seg ut, i samme rekkefoelge.
SKILTE_SEG_UT = "skilte_seg_ut"
RETNINGSFELTENE = {POSITIV: "skilte_seg_ut_positiv", NEGATIV: "skilte_seg_ut_negativ", BLANDET: "skilte_seg_ut_blandet"}

# Story 10.10: navnene, resten som antall, og bransjene med hoeyest og lavest
# snitt. Feltene finnes bare naar de har noe aa si.
NAVNENE = "skilte_seg_ut_navn"
ANDRE = "skilte_seg_ut_andre"
MEST_OPP = "bransje_mest_opp"
MEST_NED = "bransje_mest_ned"
# Gjennomgangen (BH5): norsk alfabetisk rekkefoelge, Æ, Ø og Å sist, og uten
# hensyn til store og smaa bokstaver.
_NORSK = str.maketrans({"æ": "{", "ø": "|", "å": "}", "ä": "{", "ö": "|"})


def alfabetisk(navn: str) -> str:
    """Noekkelen for norsk alfabetisk rekkefoelge."""
    return navn.casefold().translate(_NORSK)


MEST_NAVN = 5
# Feltene promptversjon dag-1 ikke har (spoersmaal 5).
NYE_FELT = (NAVNENE, ANDRE, MEST_OPP, MEST_NED)
DAG_1 = "dag-1"


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
    terskel: int = STANDARD.terskel,
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
    # Story 10.10: navnene, 3 av 3 foerst. Vurderingen har ikke navnet, saa
    # det hentes fra aksjen i lista.
    utslag = sorted(
        (
            (v.styrke, a.navn, a.symbol, v.retning)
            for a in lista
            if isinstance(v := vurderinger.get(a.symbol), Vurdering) and v.styrke >= terskel
        ),
        key=lambda u: (-u[0], alfabetisk(u[1]), u[1], u[2]),
    )
    if utslag:
        grunnlag[NAVNENE] = [
            {"navn": navn, "styrke": styrke, "retning": retning.lower()}
            for styrke, navn, _symbol, retning in utslag[:MEST_NAVN]
        ]
        if len(utslag) > MEST_NAVN:
            grunnlag[ANDRE] = len(utslag) - MEST_NAVN
    bransjer: dict[str, dict[str, int]] = {}
    snitt: dict[str, float] = {}
    for sektor in dict.fromkeys(a.sektor for a in lista):
        endringer = [_endringen(list(serier.get(a.symbol, [])), dag) for a in lista if a.sektor == sektor]
        med = [e for e in endringer if e is not None]
        if len(med) < MINST_I_BRANSJEN:
            continue
        bransjer[sektor] = {"steg": sum(1 for e in med if bevegelse(e) == STEG), "med_endring": len(med)}
        snitt[sektor] = avrundet(sum(med) / len(med), "endring")
    if bransjer:
        grunnlag["bransjer"] = bransjer
    grunnlag.update(mest_opp_og_ned(snitt))
    return MappingProxyType(grunnlag)


def mest_opp_og_ned(snitt: Mapping[str, float]) -> dict[str, str]:
    """Bransjen med hoeyest snitt over 0 og den med lavest under 0, slik
    snittene vises (avrundet). To like snitt gir ingen for den siden
    (spoersmaal 2)."""
    ut: dict[str, str] = {}
    for felt, verdier in (
        (MEST_OPP, {n: v for n, v in snitt.items() if v > 0}),
        (MEST_NED, {n: -v for n, v in snitt.items() if v < 0}),
    ):
        if not verdier:
            continue
        stoerst = max(verdier.values())
        beste = [n for n, v in verdier.items() if v == stoerst]
        if len(beste) == 1:
            ut[felt] = beste[0]
    return ut


def for_promptversjon(grunnlag: Mapping[str, object] | None, promptversjon: str) -> Mapping[str, object] | None:
    """Grunnlaget slik en rad med promptversjonen har det: uten de nye
    feltene for dag-1 (story 10.10, spoersmaal 5), ellers urørt."""
    if grunnlag is None or promptversjon != DAG_1:
        return grunnlag
    return MappingProxyType({n: v for n, v in grunnlag.items() if n not in NYE_FELT})


def som_vanlig(grunnlag: Mapping[str, object] | None) -> dict | None:
    """Grunnlaget som vanlige dict, saa to grunnlag kan sammenlignes, ogsaa
    et som er lest fra loggen (MappingProxyType paa alle nivaaer)."""
    if grunnlag is None:
        return None
    return {n: som_vanlig(v) if isinstance(v, Mapping) else v for n, v in grunnlag.items()}
