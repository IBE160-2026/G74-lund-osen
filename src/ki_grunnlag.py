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

Story 10.2i (gruppens svar 5.11 kl. 19:13): Dagsbilde, lag_dagsbilde og
bevegelse ligger i dagene.py, saa appen skriver setningen om samme dag av de
samme verdiene som grunnlaget. De importeres her, saa ingenting annet endres.

Story 10.2i, gruppens svar 5.11 kl. 19:13 og 23:36: modellen skriver ikke om
dagen. Grunnlaget faar retningen paa aksjen selv den dagen (aksjen), regnet
som for hovedindeksen (fra svaret 6.11 kl. 09:55 som i tabellen, se under), og mister bransjen og antallene, som appen skriver selv
under teksten (setning_om_samme_dag i dagene.py). Hovedindeksen staar, saa
prompten kan gi ferdig ordlyd om aksjen gikk samme vei som den.

Gruppens svar 6.11 kl. 09:55, 1 (BH4, ECH9 i PR #113): aksjen regnes som i
tabellen, mot forrige rad, ogsaa paa en dag med hull, ikke som hovedindeksen
(lag_dagsbilde i dagene.py).

Gruppens svar 6.11 kl. 11:15, 2 (BH3, ECH2, VG2 i PR #113): hovedindeksen er
med bare naar aksjen er regnet over den samme dagen (Dagsbilde.samme_periode),
fordi feltet bare er med for ordlyden om aksjen gikk samme vei
(ordlyd_om_hovedindeksen i ki_prompt.py). Paa en dag med hull faar grunnlaget
aksjen, men ikke hovedindeksen, og dermed ingen ordlyd.

Story 10.9 (gruppens svar 06.11 kl. 20:38 og 22:05, og 07.11 kl. 08:58):
grunnlaget faar antallene i de tre moenstrene appen regner ut
(moenstrene.py), naar de gis. Det er antall dager, regnet av vaare lagrede
vurderinger og av retningen aksjen og hovedindeksen gikk, saa det holder seg
innenfor beslutningen 04.10 (del H i spesifikasjonen). Del F sier at antallene
legges til ANTALLENE. Etter gjennomgangen (BH2, ECH5) er de ikke der: da var de
lovlige tall hvor som helst i teksten. Kontrollen i FR-603 leser dem bare i
formene i setningen om moenstrene, ved feltet sitt.
"""

from types import MappingProxyType

from dagene import BEVEGELSER, FALT, STEG, UENDRET, Dagsbilde, bevegelse, lag_dagsbilde
from moenstrene import MINST, MINST_TELT, MINST_VURDERTE, VINDU_RETNINGEN, VINDU_SAMME_VEI, Moenstrene
from signalberegning import BLANDET, INGEN, NEGATIV, POSITIV, Signal, finn_retning, finn_styrke
from vurderingsdata import Vurdering

__all__ = [
    "BEVEGELSER",
    "FALT",
    "STEG",
    "UENDRET",
    "Dagsbilde",
    "bevegelse",
    "ki_grunnlag",
    "lag_dagsbilde",
]

RETNINGER = (POSITIV, NEGATIV, BLANDET, INGEN)
SJEKKENE = ("trend", "bevegelse", "interesse")
UTENFOR_MAALINGEN = "Utenfor målingen"
NOEKLENE = frozenset((*SJEKKENE, "styrke", "retning"))

# Feltene med dagen, som begge kan mangle. Svaret 25.10 kl. 00:51: dagene er
# ikke med, og et grunnlag med dager eller dager_merke avvises. Story 10.2i:
# bransjen, aksjer_steg og aksjer_falt er tatt ut, og aksjen er med.
DAGFELTENE = ("hovedindeksen", "aksjen")
VALGFRIE = frozenset(("merke", *DAGFELTENE))
# Antallene i grunnlaget. Kontrollen i FR-603 godtar bare disse og regelens
# faste tall (punkt 2). Fortegnene er ikke antall. Story 10.2i: bare styrken.
# Story 10.9: antallene i moenstrene er ikke her. Kontrollen leser dem bare i
# formene for moenstrene, ved feltet sitt (gjennomgangen, BH2, ECH5).
ANTALLENE = ("styrke",)

# Story 10.9: feltene med de tre moenstrene. Hvert moenster er med helt eller
# ikke i det hele tatt. Navnene sier vinduet, og ikke «mønster», som
# kontrollen stopper i teksten.
MOENSTER_1 = ("siste_20_vurdert", "siste_20_positiv", "siste_20_negativ", "siste_20_blandet", "siste_20_ingen")
MOENSTER_2 = ("siste_5_kunne_telles", "siste_5_samme_vei")
MOENSTER_3 = ("siste_måned_skift",)
MOENSTER_3_MERKE = "siste_måned_merke"
MOENSTERANTALLENE = (*MOENSTER_1, *MOENSTER_2, *MOENSTER_3)
VALGFRIE = VALGFRIE | frozenset((*MOENSTERANTALLENE, MOENSTER_3_MERKE))


def _heltall(verdi) -> bool:
    return type(verdi) is int


def ki_grunnlag(
    kilde: Signal | Vurdering,
    *,
    utenfor_maalingen: bool,
    dagen: Dagsbilde | None = None,
    moenstrene: Moenstrene | None = None,
) -> MappingProxyType:
    """Fortegnene, styrken og retningen, og med dagen hovedindeksen og aksjen.

    kilde er signalet fra signalberegning eller vurderingen fra basen. Begge
    har de samme tre fortegnene, styrken og retningen. Et Signal kontrolleres
    ikke naar det lages, saa her sjekkes det at styrken og retningen er de
    sjekkene gir, slik Vurdering gjoer.
    """
    if type(utenfor_maalingen) is not bool:
        raise TypeError("utenfor_maalingen maa vaere True eller False")
    if dagen is not None and not isinstance(dagen, Dagsbilde):
        raise TypeError(f"dagen maa vaere et Dagsbilde, fikk {type(dagen).__name__}")
    if moenstrene is not None and not isinstance(moenstrene, Moenstrene):
        raise TypeError(f"moenstrene maa vaere Moenstrene, fikk {type(moenstrene).__name__}")
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
        for felt in DAGFELTENE:
            # Svaret 6.11 kl. 11:15, 2: hovedindeksen bare over samme periode.
            if felt == "hovedindeksen" and not dagen.samme_periode:
                continue
            if getattr(dagen, felt) is not None:
                grunnlag[felt] = getattr(dagen, felt)
    if moenstrene is not None:
        # Story 10.9: bare moenstrene som gis (moenstrene.py).
        # Story 10.10 (versjon 6): tall som er 0, sendes ikke, saa modellen
        # ikke kan skrive dem. Gemma skrev «negativt 0» i 7 av 13 demotekster
        # selv om prompten ba om det motsatte (11.11).
        if moenstrene.retningene is not None:
            grunnlag.update(
                (navn, n) for navn, n in zip(MOENSTER_1, moenstrene.retningene) if n or navn == MOENSTER_1[0]
            )
        if moenstrene.samme_vei is not None and moenstrene.samme_vei[1]:
            grunnlag.update(zip(MOENSTER_2, moenstrene.samme_vei))
        if moenstrene.skiftene is not None and moenstrene.skiftene[0]:
            skift, minst = moenstrene.skiftene
            grunnlag[MOENSTER_3[0]] = skift
            if minst:
                grunnlag[MOENSTER_3_MERKE] = MINST
    _kontroller(grunnlag)
    if isinstance(kilde, Signal):
        _samsvar(kilde)
    return MappingProxyType(grunnlag)


def _kontroller(grunnlag: dict[str, object]) -> None:
    """Siste vakt: noeklene, og bare heltall og tekst fra de lukkede listene."""
    if set(grunnlag) - VALGFRIE != NOEKLENE:
        raise ValueError("grunnlaget har andre noekler enn fortegnene, styrken, retningen og dagen")
    if grunnlag.get("merke", UTENFOR_MAALINGEN) != UTENFOR_MAALINGEN:
        raise ValueError("merke kan bare vaere «Utenfor målingen»")
    for navn in SJEKKENE:
        if not _heltall(grunnlag[navn]) or grunnlag[navn] not in (-1, 0, 1):
            raise ValueError(f"{navn} maa vaere heltallet -1, 0 eller 1, fikk {type(grunnlag[navn]).__name__}")
    if not _heltall(grunnlag["styrke"]) or grunnlag["styrke"] not in (0, 1, 2, 3):
        raise ValueError(f"styrke maa vaere et heltall fra 0 til 3, fikk {type(grunnlag['styrke']).__name__}")
    if type(grunnlag["retning"]) is not str or grunnlag["retning"] not in RETNINGER:
        raise ValueError(f"retning maa vaere en av {RETNINGER}")
    for navn in DAGFELTENE:
        if navn in grunnlag and (type(grunnlag[navn]) is not str or grunnlag[navn] not in BEVEGELSER):
            raise ValueError(f"{navn} maa vaere en av {BEVEGELSER}")
    _kontroller_moenstrene(grunnlag)


def _kontroller_moenstrene(grunnlag: dict[str, object]) -> None:
    """Story 10.9: hvert moenster helt eller ikke, bare heltall fra 0, og
    antallene innenfor vinduet og grensene i spoersmaal 3 og 4. Story 10.10:
    retningene i moenster 1 som er 0, er ikke med, men vurdert er alltid med."""
    for felter in (MOENSTER_2, MOENSTER_3):
        med = [navn in grunnlag for navn in felter]
        if any(med) and not all(med):
            raise ValueError(f"moensteret med {felter[0]} maa ha alle feltene sine")
    if any(navn in grunnlag for navn in MOENSTER_1[1:]) and MOENSTER_1[0] not in grunnlag:
        raise ValueError(f"moensteret med {MOENSTER_1[0]} maa ha antallet vurderte dager")
    for navn in MOENSTERANTALLENE:
        if navn in grunnlag and (not _heltall(grunnlag[navn]) or grunnlag[navn] < 0):
            raise ValueError(f"{navn} maa vaere et heltall fra 0")
    if MOENSTER_1[0] in grunnlag:
        vurdert, *antall = (grunnlag.get(navn, 0) for navn in MOENSTER_1)
        if not MINST_VURDERTE <= vurdert <= VINDU_RETNINGEN or sum(antall) != vurdert:
            raise ValueError("moenster 1 maa ha 10 til 20 vurderte dager, fordelt paa de fire retningene")
    if MOENSTER_2[0] in grunnlag:
        telt, samme = (grunnlag[navn] for navn in MOENSTER_2)
        if not MINST_TELT <= telt <= VINDU_SAMME_VEI or samme > telt:
            raise ValueError("moenster 2 maa ha 3 til 5 dager som kunne telles, og ikke flere samme vei")
    # Gjennomgangen (BH11): maaneden har hoeyst 23 boersdager, saa hoeyst 22 skift.
    if MOENSTER_3[0] in grunnlag and grunnlag[MOENSTER_3[0]] > 22:
        raise ValueError("siste_måned_skift kan ikke vaere flere enn 22")
    if MOENSTER_3_MERKE in grunnlag and (MOENSTER_3[0] not in grunnlag or grunnlag[MOENSTER_3_MERKE] != MINST):
        raise ValueError("siste_måned_merke kan bare vaere «minst», og bare med siste_måned_skift")


def _samsvar(signal: Signal) -> None:
    if signal.styrke != finn_styrke(signal.sjekker) or signal.retning != finn_retning(signal.sjekker):
        raise ValueError("styrken eller retningen stemmer ikke med sjekkene")
