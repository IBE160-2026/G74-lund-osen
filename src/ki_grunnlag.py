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

Story 10.2e, prompten versjon 3 (gruppens svar 21.10 kl. 22:57 og 23:51 og
24.10 kl. 16:15): med dagen faar grunnlaget ogsaa dagene, retningen paa
hovedindeksen, hvor mange aksjer i lista som steg og falt, og retningen paa
bransjen. Det er fortegn og antall, regnet her av kursene og vurderingene,
og ingen kurs, prosent eller forholdstall sendes. Retningen er fortegnet paa
endringen slik den vises (tallformat.avrundet), som streken paa grafen og
fargene i boersometeret, saa teksten og siden sier det samme.

Fjerde forsoek (gruppens svar 25.10 kl. 00:51): modellen faar ikke dagene.
Dagsbildet teller dem fortsatt (tell_dagene, flyttet til dagene.py), men
grunnlaget har ikke dager eller dager_merke. Appen skriver dagene selv, i en
setning under KI-teksten paa aksjesiden.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType

from dagene import tell_dagene
from hovedindeks import indeksendring
from kursdata import Aksje, Kursrad
from markedsoversikt import endring_i_prosent
from signalberegning import BLANDET, INGEN, NEGATIV, POSITIV, Signal, finn_retning, finn_styrke
from tallformat import avrundet
from vurderingsdata import Grunn, Vurdering

RETNINGER = (POSITIV, NEGATIV, BLANDET, INGEN)
SJEKKENE = ("trend", "bevegelse", "interesse")
UTENFOR_MAALINGEN = "Utenfor målingen"
NOEKLENE = frozenset((*SJEKKENE, "styrke", "retning"))

# Story 10.2e: retningen paa hovedindeksen og bransjen. Merket paa dagene
# («minst») er tatt bort med dagene (svaret 25.10 kl. 00:51).
STEG, FALT, UENDRET = "steg", "falt", "uendret"
BEVEGELSER = (STEG, FALT, UENDRET)
# Feltene med dagen. hovedindeksen og bransjen kan mangle. Svaret 25.10 kl.
# 00:51: dagene er ikke med, og et grunnlag med dager eller dager_merke avvises.
DAGNOEKLENE = frozenset(("aksjer_steg", "aksjer_falt"))
VALGFRIE = frozenset(("merke", "hovedindeksen", "bransjen"))
# Antallene i grunnlaget. Kontrollen i FR-603 godtar bare disse og regelens
# faste tall (punkt 2). Fortegnene er ikke antall.
ANTALLENE = ("styrke", "aksjer_steg", "aksjer_falt")


@dataclass(frozen=True)
class Dagsbilde:
    """Det grunnlaget faar om dagen i versjon 3. hovedindeksen og bransjen
    er None naar de ikke kan regnes, og da faar grunnlaget ikke feltet."""

    dager: int
    dager_minst: bool
    hovedindeksen: str | None
    aksjer_steg: int
    aksjer_falt: int
    bransjen: str | None


def bevegelse(endring: float | None) -> str | None:
    """steg, falt eller uendret etter endringen slik den vises, eller None."""
    if endring is None:
        return None
    vist = avrundet(endring, "endring")
    return STEG if vist > 0 else FALT if vist < 0 else UENDRET


def _endringen(serie: list[Kursrad], dag: date) -> float | None:
    """Endringen for dag som i boersometeret (bygg_rute): de to siste
    radene til og med dag, og None uten kurs paa dag."""
    til = [rad for rad in serie if rad.dato <= dag]
    if not til or til[-1].dato != dag:
        return None
    return endring_i_prosent(til[-2:])


def lag_dagsbilde(
    aksje: Aksje,
    dag: date,
    vurdering: Vurdering,
    tidligere: Mapping[date, Vurdering | Grunn],
    lista: tuple[Aksje, ...],
    serier: Mapping[str, list[Kursrad]],
    indeksserie: list[Kursrad] | None,
) -> Dagsbilde:
    """Dagsbildet for aksjen paa dag. serier er kursene for aksjene i lista,
    og indeksserie hovedindeksen, eller None naar basen ikke har en."""
    dager, minst = tell_dagene(dag, vurdering, tidligere)
    endringer = {a.symbol: _endringen(serier.get(a.symbol, []), dag) for a in lista}
    retninger = [bevegelse(e) for e in endringer.values()]
    i_bransjen = [endringer[a.symbol] for a in lista if a.sektor == aksje.sektor and endringer[a.symbol] is not None]
    indeks = None
    if indeksserie:
        til = [rad for rad in indeksserie if rad.dato <= dag]
        if til and til[-1].dato == dag:
            indeks = bevegelse(indeksendring(til))
    return Dagsbilde(
        dager=dager,
        dager_minst=minst,
        hovedindeksen=indeks,
        aksjer_steg=retninger.count(STEG),
        aksjer_falt=retninger.count(FALT),
        bransjen=bevegelse(sum(i_bransjen) / len(i_bransjen)) if i_bransjen else None,
    )


def _heltall(verdi) -> bool:
    return type(verdi) is int


def ki_grunnlag(
    kilde: Signal | Vurdering, *, utenfor_maalingen: bool, dagen: Dagsbilde | None = None
) -> MappingProxyType:
    """Fortegnene, styrken og retningen, og med dagen feltene fra versjon 3.

    kilde er signalet fra signalberegning eller vurderingen fra basen. Begge
    har de samme tre fortegnene, styrken og retningen. Et Signal kontrolleres
    ikke naar det lages, saa her sjekkes det at styrken og retningen er de
    sjekkene gir, slik Vurdering gjoer.
    """
    if type(utenfor_maalingen) is not bool:
        raise TypeError("utenfor_maalingen maa vaere True eller False")
    if dagen is not None and not isinstance(dagen, Dagsbilde):
        raise TypeError(f"dagen maa vaere et Dagsbilde, fikk {type(dagen).__name__}")
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
    if dagen is not None:
        if dagen.hovedindeksen is not None:
            grunnlag["hovedindeksen"] = dagen.hovedindeksen
        grunnlag["aksjer_steg"] = dagen.aksjer_steg
        grunnlag["aksjer_falt"] = dagen.aksjer_falt
        if dagen.bransjen is not None:
            grunnlag["bransjen"] = dagen.bransjen
    _kontroller(grunnlag)
    if isinstance(kilde, Signal):
        _samsvar(kilde)
    return MappingProxyType(grunnlag)


def _kontroller(grunnlag: dict[str, object]) -> None:
    """Siste vakt: noeklene, og bare heltall og tekst fra de lukkede listene."""
    noekler = set(grunnlag) - VALGFRIE
    if noekler not in (NOEKLENE, NOEKLENE | DAGNOEKLENE):
        raise ValueError("grunnlaget har andre noekler enn fortegnene, styrken, retningen og dagen")
    if noekler == NOEKLENE and set(grunnlag) & (VALGFRIE - {"merke"}):
        raise ValueError("hovedindeksen og bransjen kommer bare med dagen")
    if grunnlag.get("merke", UTENFOR_MAALINGEN) != UTENFOR_MAALINGEN:
        raise ValueError("merke kan bare vaere «Utenfor målingen»")
    for navn in SJEKKENE:
        if not _heltall(grunnlag[navn]) or grunnlag[navn] not in (-1, 0, 1):
            raise ValueError(f"{navn} maa vaere heltallet -1, 0 eller 1, fikk {type(grunnlag[navn]).__name__}")
    if not _heltall(grunnlag["styrke"]) or grunnlag["styrke"] not in (0, 1, 2, 3):
        raise ValueError(f"styrke maa vaere et heltall fra 0 til 3, fikk {type(grunnlag['styrke']).__name__}")
    if type(grunnlag["retning"]) is not str or grunnlag["retning"] not in RETNINGER:
        raise ValueError(f"retning maa vaere en av {RETNINGER}")
    if "aksjer_steg" in grunnlag:
        for navn in ("aksjer_steg", "aksjer_falt"):
            if not _heltall(grunnlag[navn]) or grunnlag[navn] < 0:
                raise ValueError(f"{navn} maa vaere et heltall fra 0, fikk {type(grunnlag[navn]).__name__}")
    for navn in ("hovedindeksen", "bransjen"):
        if navn in grunnlag and (type(grunnlag[navn]) is not str or grunnlag[navn] not in BEVEGELSER):
            raise ValueError(f"{navn} maa vaere en av {BEVEGELSER}")


def _samsvar(signal: Signal) -> None:
    if signal.styrke != finn_styrke(signal.sjekker) or signal.retning != finn_retning(signal.sjekker):
        raise ValueError("styrken eller retningen stemmer ikke med sjekkene")
