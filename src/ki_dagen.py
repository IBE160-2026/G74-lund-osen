"""KI-teksten om dagen: prompten, kontrollen og raden - story 10.6, FR-603,
FR-604, FR-605, FR-607, NFR-06.

Grunnlaget regnes i dagsgrunnlag.py, som webserveren ogsaa bruker. Her er
det bare hentingen som kommer: prompten, kontrollen i FR-603 og raden i
KI-loggen. Webserveren importerer aldri denne fila (AD-10).

Prompten har sin egen versjon, DAGSPROMPTVERSJON, saa teksten om dagen og
teksten om én aksje ikke kan blandes i loggen (FR-605, spoersmaal 6 i
spesifikasjonen). Som i 10.9 gir prompten én fast form for hvert faktum, og
kontrollen leser tallene bare i formene, ved feltet sitt (spoersmaal 5).

Kontrollen har alle fire punktene i FR-603:

1. Retning. Det teksten sier om hovedindeksen og retningene blant dem som
   skilte seg ut, skal stemme med grunnlaget, og mangler feltet, stoppes
   utsagnet. Utenfor formene stoppes ord om hovedindeksen, boersen, markedet,
   bransjene, retningene og om noe steg eller falt, fordi kontrollen ikke kan
   lese dem.
2. Tallene. Et tall er lov bare i formene, ved feltet sitt, ogsaa skrevet med
   ord. Prosent, desimaltall, beloep og mengder stoppes.
3. Raad, med lista fra kontrollen for én aksje (RAAD).
4. Gjetning og aarsaker, med listene GJETNING og AARSAKER, og ord som sier at
   modellen fant et moenster selv.

Ukedagen skal vaere grunnlagets, og «i dag», «i går», «i kveld», «i morgen»,
«dagens» og «gårsdagens» stoppes, fordi teksten ogsaa leses senere
(spoersmaal 4). Etter gjennomgangen kan resten av teksten, naar formene er
tatt ut, bare vaere bindeordene i BINDEORD og tegnsetting.

Story 10.10, promptversjon dag-2 (gruppens svar 10.11 kl. 16:18): teksten
faar navnene paa aksjene som skilte seg ut, med styrken og retningen for
hver, 3 av 3 foerst, hoeyst fem navn og resten som antall, og bransjen som i
snitt steg mest og den som i snitt falt mest, regnet som snittet paa
Boersometeret (dagsgrunnlag.py). Appen regner ut alt, og modellen skriver
det i faste former. Kontrollen leser hvert navn med styrken og retningen
ved navnet, og bransjene ved feltet sitt. Et navn som ikke staar i
grunnlaget, blir staaende igjen naar formene er tatt ut, og stoppes som
resten. Ord som «bør», «verdt å følge», «følg med» og «vil» stoppes under
punkt 3 og 4 (NFR-06, lista i ki_kontroll.py).
"""

import json
import re
from collections.abc import Mapping

from dagsgrunnlag import ANDRE, MEST_NED, MEST_OPP, NAVNENE
from ki_kontroll import (
    _EGET_MOENSTER,
    _ENHETER,
    _FELTNAVN,
    _GJETNING,
    _RAAD,
    _SIFFER,
    _TALLORD_I_TEKST,
    Kontrollsvar,
    normaliser,
)
from ki_modell import Modell, ModellFeilet, Modellsvar, _grunn
from kilogg import DAG, Emne, KIRad, UgyldigKIRad

DAGSPROMPTVERSJON = "dag-2"

REGLER_DAGEN = """Du skriver noen korte setninger på norsk om hele børsdagen på Oslo Børs, for en som ikke kjenner reglene i appen.
Appen gir hver aksje et regelbasert signal. En aksje skilte seg ut når minst to av de tre sjekkene i signalet ga utslag.

Opplysningene under er regnet ut av appen for én børsdag og for aksjene i lista:
- aksjer: hvor mange aksjer lista har.
- ukedag: hvilken dag i uka børsdagen var.
- hovedindeksen: om hovedindeksen på Oslo Børs steg, falt eller var uendret. Feltet kan mangle.
- bedre_enn_indeksen og med_kurs: hvor mange av aksjene med kurs den dagen som gjorde det bedre enn hovedindeksen. Feltene kan mangle.
- skilte_seg_ut: hvor mange aksjer som skilte seg ut. skilte_seg_ut_positiv, skilte_seg_ut_negativ og skilte_seg_ut_blandet: hvor mange av dem som hadde positiv, negativ og blandet retning.
- skilte_seg_ut_navn: navnene på aksjene som skilte seg ut, høyst fem, med styrken (3 eller 2 av 3) og retningen for hver. De med 3 av 3 står først. Feltet kan mangle.
- skilte_seg_ut_andre: hvor mange flere som skilte seg ut, utenom navnene. Feltet kan mangle.
- bransjer: for hver bransje, steg er hvor mange aksjer som steg, og med_endring hvor mange som hadde en endring den dagen. Feltet kan mangle.
- bransje_mest_opp og bransje_mest_ned: bransjen der aksjene i snitt steg mest, og bransjen der de i snitt falt mest, regnet ut av appen. Feltene kan mangle.

Regler for teksten:
- Skriv tre til sju korte setninger, med disse formene. Sett inn tallene og ordene for feltene i ‹ ›:
  - «Hovedindeksen steg ‹ukedag›.», «Hovedindeksen falt ‹ukedag›.» eller «Hovedindeksen var uendret ‹ukedag›.», etter feltet hovedindeksen.
  - «‹bedre_enn_indeksen› av ‹med_kurs› aksjer gjorde det bedre enn indeksen.»
  - «‹skilte_seg_ut› skilte seg ut: ‹skilte_seg_ut_positiv› med positiv retning, ‹skilte_seg_ut_negativ› negativ og ‹skilte_seg_ut_blandet› blandet.» Ta bare med retningene som har minst én aksje. Er skilte_seg_ut 0, skriver du «Ingen aksjer skilte seg ut.»
  - «Blant dem var ‹navn› (‹styrke› av 3, ‹retning›), ‹navn› (‹styrke› av 3, ‹retning›) og ‹navn› (‹styrke› av 3, ‹retning›).», med alle navnene i skilte_seg_ut_navn, i den rekkefølgen de står, og skrevet som der. Med skilte_seg_ut_andre slutter setningen med «og ‹skilte_seg_ut_andre› andre.»
  - «I ‹bransje› steg ‹steg› av ‹med_endring› aksjer.», med navnet på bransjen med små bokstaver. Nevn høyst to bransjer.
  - «I snitt steg ‹bransje_mest_opp› mest.» og «I snitt falt ‹bransje_mest_ned› mest.», med navnet på bransjen med små bokstaver.
- Mangler et felt, skriver du ikke setningen for det.
- Skriv tallene som i opplysningene. Ikke nevn andre tall, prosenter, kurser eller beløp.
- Ikke si noe om hovedindeksen, bransjene, retningene eller hvor mange som steg eller falt utenom formene.
- Ikke skriv «i dag», «i går» eller «i kveld». Bruk ukedagen.
- Ikke gi råd om å kjøpe, selge eller holde, ikke skriv «bør», «verdt å følge» eller «følg med», og ikke si noe om hva som vil skje.
- Ikke gjett på årsaker, som nyheter, resultater, renter eller oljeprisen.
- Ikke finn mønstre selv, og ikke sammenlign aksjene eller bransjene med hverandre utover formene.
- Skriv aldri navnet på et felt eller tegnene ‹ › i teksten.
"""


def lag_dagsprompt(grunnlag: Mapping[str, object]) -> str:
    """Reglene og grunnlaget som JSON. Ingenting annet kommer med."""
    return (
        REGLER_DAGEN + "\nOpplysningene:\n" + json.dumps(_vanlig(grunnlag), ensure_ascii=False, sort_keys=True) + "\n"
    )


def _vanlig(verdi):
    if isinstance(verdi, Mapping):
        return {n: _vanlig(v) for n, v in verdi.items()}
    return verdi


def dagsregel(grunnlag: Mapping[str, object]) -> str:
    """Det appen regnet ut om dagen, som tekst til feltet regelen (FR-604)."""
    deler = [f"Aksjer {grunnlag['aksjer']}, {grunnlag['ukedag']}."]
    if "hovedindeksen" in grunnlag:
        deler.append(f"Hovedindeksen {grunnlag['hovedindeksen']}.")
    if "bedre_enn_indeksen" in grunnlag:
        deler.append(f"Bedre enn indeksen {grunnlag['bedre_enn_indeksen']} av {grunnlag['med_kurs']}.")
    deler.append(
        f"Skilte seg ut {grunnlag['skilte_seg_ut']}: positiv {grunnlag['skilte_seg_ut_positiv']}, "
        f"negativ {grunnlag['skilte_seg_ut_negativ']}, blandet {grunnlag['skilte_seg_ut_blandet']}."
    )
    navnene = grunnlag.get(NAVNENE) or ()
    if navnene:
        oppramsing = ", ".join(f"{n['navn']} ({n['styrke']} av 3, {n['retning']})" for n in navnene)
        andre = f", og {grunnlag[ANDRE]} andre" if ANDRE in grunnlag else ""
        deler.append(f"Navnene: {oppramsing}{andre}.")
    for navn, b in (grunnlag.get("bransjer") or {}).items():
        deler.append(f"{navn}: steg {b['steg']} av {b['med_endring']}.")
    if MEST_OPP in grunnlag:
        deler.append(f"Høyest snitt: {grunnlag[MEST_OPP]}.")
    if MEST_NED in grunnlag:
        deler.append(f"Lavest snitt: {grunnlag[MEST_NED]}.")
    return " ".join(deler)


# --- Kontrollen (FR-603) -----------------------------------------------------

# Gjennomgangen av 10.6 (BH1-BH3, ECH2-ECH9, VG1, VG2): kontrollen leser
# formene i prompten, og naar de er tatt ut, kan resten av teksten bare vaere
# bindeordene i BINDEORD og tegnsetting. En nektelse («steg ikke»), et
# synonym («gikk opp»), et selskap, en bransje utenfor formen eller et ord om
# hvor kraftig noe var, stoppes da uten at ordet maa staa i en liste.
# Tallene i formene staar med sifre, som i opplysningene, saa hvert tall som
# vises, har prikket strek (spoersmaal 8). Bare «Ingen aksjer skilte seg ut»
# har et antall med ord.
BINDEORD = frozenset(("og", "men"))
_N = r"(\d{1,4})(?![\w-])"
_UKEDAG = r"(mandag|tirsdag|onsdag|torsdag|fredag|lørdag|søndag)"
_F_INDEKSEN = re.compile(
    r"(?<![\w-])hovedindeksen\s+(steg|falt|var\s+uendret)(?:\s+(?:på\s+)?" + _UKEDAG + r")?(?![\w-])", re.IGNORECASE
)
_F_BEDRE = re.compile(
    r"(?<![\w-])" + _N + r"\s+av\s+(?:de\s+)?" + _N + r"\s+aksje(?:r|ne)?\s+(?:gjorde\s+det|gikk)\s+bedre\s+enn\s+"
    r"(?:hoved)?indeksen(?![\w-])",
    re.IGNORECASE,
)
_F_SKILTE = re.compile(r"(?<![\w-])(\d{1,4}|ingen)\s+(?:aksjer?\s+)?skilte\s+seg\s+ut(?![\w-])", re.IGNORECASE)
_F_RETNING = re.compile(
    r"(?<![\w-])" + _N + r"\s+(?:med\s+)?(positiv|negativ|blandet)(?:\s+retning)?(?![\w-])", re.IGNORECASE
)
_F_BRANSJE = re.compile(
    r"(?<![\w-])i\s+([a-zæøå]+(?:[\s-]+(?:og\s+)?[a-zæøå]+)?)\s+steg\s+"
    + _N
    + r"\s+av\s+(?:de\s+)?"
    + _N
    + r"(?:\s+aksje(?:r|ne)?)?(?![\w-])",
    re.IGNORECASE,
)
_RETNINGSFELT = {
    "positiv": "skilte_seg_ut_positiv",
    "negativ": "skilte_seg_ut_negativ",
    "blandet": "skilte_seg_ut_blandet",
}
_VERBET = {"steg": "steg", "falt": "falt", "var uendret": "uendret"}
# Story 10.10: formene for navnene og bransjene med hoeyest og lavest snitt.
# Navnet leses ordrett fra grunnlaget (_navnet), med styrken og retningen i
# parentesen etter.
_I_PARENTES = r"\s*\(\s*(\d{1,4})\s+av\s+3\s*,\s*(positiv|negativ|blandet)\s*\)"
_F_BLANT = re.compile(r"(?<![\w-])blant\s+dem\s+var(?![\w-])", re.IGNORECASE)
_F_ANDRE = re.compile(r"(?<![\w-])" + _N + r"\s+andre(?![\w-])", re.IGNORECASE)
_F_MEST = re.compile(
    r"(?<![\w-])i\s+snitt\s+(steg|falt)\s+([a-zæøå]+(?:[\s-]+(?:og\s+)?[a-zæøå]+)?)\s+mest(?![\w-])",
    re.IGNORECASE,
)
_MEST_FELT = {"steg": MEST_OPP, "falt": MEST_NED}
_ORD = re.compile(r"[\w-]+")
# Tegnsettingen som kan staa mellom formene.
_TEGN = frozenset(" \t\n.,:;")
_NAA = re.compile(r"(?<![\w-])(i\s+dag|i\s+går|i\s+kveld|i\s+morgen|dagens|gårsdagens)(?![\w-])", re.IGNORECASE)


def _navnet(navn: str) -> re.Pattern[str]:
    """Navnet ordrett, med hvilket som helst mellomrom der navnet har et
    (ogsaa et hardt), og styrken og retningen i parentesen etter."""
    deler = [re.escape(del_) for del_ in str(navn).split()]
    return re.compile(r"(?<![\w-])" + r"\s+".join(deler) + _I_PARENTES, re.IGNORECASE)


def _antall(ord_: str) -> int:
    return 0 if ord_.lower() == "ingen" else int(ord_)


def _ta_ut(tekst: str, treff: re.Match) -> str:
    """Formen tas ut av teksten, saa resten leses uten den."""
    return tekst[: treff.start()] + " " * (treff.end() - treff.start()) + tekst[treff.end() :]


def kontroller_dagen(tekst: str, grunnlag: Mapping[str, object]) -> Kontrollsvar:
    """De fire punktene i FR-603 for teksten om dagen. Gir alle grunnene."""
    if not isinstance(tekst, str):
        raise TypeError("tekst maa vaere en tekst")
    tekst = normaliser(tekst)
    grunner: list[str] = []
    bransjer = {navn.lower(): verdi for navn, verdi in (grunnlag.get("bransjer") or {}).items()}

    def ved_feltet(funnet: str, felt: str, form: str) -> None:
        if felt not in grunnlag:
            grunner.append(f"1: «{form}», men {felt} mangler i grunnlaget")
        elif _antall(funnet) != grunnlag[felt]:
            grunner.append(f"2: tallet «{funnet}» ved {felt}")

    # Story 10.10: navnene foerst, fordi et navn kan ha ord og tegn som de
    # andre formene ellers ville lest.
    for oppfoering in grunnlag.get(NAVNENE) or ():
        navn = oppfoering["navn"]
        alle = list(_navnet(navn).finditer(tekst))
        if len(alle) > 1:
            grunner.append(f"1: navnet «{navn}» står {len(alle)} ganger")
        for treff in alle:
            if int(treff.group(1)) != oppfoering["styrke"]:
                grunner.append(f"2: tallet «{treff.group(1)}» ved styrken for {navn}")
            if treff.group(2).lower() != oppfoering["retning"]:
                grunner.append(f"1: retningen «{treff.group(2)}» for {navn}, grunnlaget sier {oppfoering['retning']}")
            tekst = _ta_ut(tekst, treff)
    for treff in list(_F_BLANT.finditer(tekst)):
        if not grunnlag.get(NAVNENE):
            grunner.append(f"1: «{treff.group(0)}», men {NAVNENE} mangler i grunnlaget")
        tekst = _ta_ut(tekst, treff)
    for treff in list(_F_ANDRE.finditer(tekst)):
        ved_feltet(treff.group(1), ANDRE, treff.group(0))
        tekst = _ta_ut(tekst, treff)
    for treff in list(_F_MEST.finditer(tekst)):
        felt = _MEST_FELT[treff.group(1).lower()]
        navn = " ".join(treff.group(2).lower().split())
        if felt not in grunnlag:
            grunner.append(f"1: «{treff.group(0)}», men {felt} mangler i grunnlaget")
        elif navn != str(grunnlag[felt]).lower():
            grunner.append(f"1: «{treff.group(0)}», grunnlaget sier {grunnlag[felt]}")
        tekst = _ta_ut(tekst, treff)
    for treff in list(_F_BEDRE.finditer(tekst)):
        ved_feltet(treff.group(1), "bedre_enn_indeksen", treff.group(0))
        ved_feltet(treff.group(2), "med_kurs", treff.group(0))
        tekst = _ta_ut(tekst, treff)
    for treff in list(_F_SKILTE.finditer(tekst)):
        ved_feltet(treff.group(1), "skilte_seg_ut", treff.group(0))
        tekst = _ta_ut(tekst, treff)
    for treff in list(_F_RETNING.finditer(tekst)):
        ved_feltet(treff.group(1), _RETNINGSFELT[treff.group(2).lower()], treff.group(0))
        tekst = _ta_ut(tekst, treff)
    for treff in list(_F_BRANSJE.finditer(tekst)):
        navn = " ".join(treff.group(1).lower().split())
        if navn not in bransjer:
            grunner.append(f"1: bransjen «{treff.group(1)}» står ikke i grunnlaget")
        else:
            for funnet, felt in ((treff.group(2), "steg"), (treff.group(3), "med_endring")):
                if _antall(funnet) != bransjer[navn][felt]:
                    grunner.append(f"2: tallet «{funnet}» ved {felt} for {navn}")
        tekst = _ta_ut(tekst, treff)
    for treff in list(_F_INDEKSEN.finditer(tekst)):
        verb = _VERBET[" ".join(treff.group(1).lower().split())]
        if "hovedindeksen" not in grunnlag:
            grunner.append(f"1: «{treff.group(0)}», men hovedindeksen mangler i grunnlaget")
        elif verb != grunnlag["hovedindeksen"]:
            grunner.append(f"1: «{treff.group(0)}», grunnlaget sier {grunnlag['hovedindeksen']}")
        if treff.group(2) and treff.group(2).lower() != grunnlag.get("ukedag"):
            grunner.append(f"1: ukedagen «{treff.group(2)}», grunnlaget sier {grunnlag.get('ukedag')}")
        tekst = _ta_ut(tekst, treff)

    # Det som er igjen: grunnene med navn foerst, saa alt annet enn bindeord
    # og tegnsetting.
    for treff in _NAA.finditer(tekst):
        grunner.append(f"1: «{treff.group(0)}», teksten leses også senere")
    for treff in _SIFFER.finditer(tekst):
        grunner.append(f"2: tallet «{treff.group(0)[:7]}» utenfor formene")
    if "%" in tekst or "‰" in tekst:
        grunner.append("2: en prosent")
    for treff in _ENHETER.finditer(tekst):
        grunner.append(f"2: «{treff.group(0)}»")
    for treff in _TALLORD_I_TEKST.finditer(tekst):
        grunner.append(f"2: tallet «{treff.group(0)}» utenfor formene")
    for treff in _FELTNAVN.finditer(tekst):
        grunner.append(f"2: «{treff.group(0)}» er et feltnavn eller en plassholder")
    for treff in _RAAD.finditer(tekst):
        grunner.append(f"3: «{treff.group(0)}»")
    for treff in _GJETNING.finditer(tekst):
        grunner.append(f"4: «{treff.group(0)}»")
    for treff in _EGET_MOENSTER.finditer(tekst):
        grunner.append(f"4: «{treff.group(0)}», modellen finner ikke mønstre selv")
    andre = [o for o in _ORD.findall(tekst) if o.lower() not in BINDEORD]
    if andre:
        grunner.append(f"1: «{' '.join(andre[:8])}» utenfor formene")
    tegn = sorted({t for t in _ORD.sub("", tekst) if t not in _TEGN})
    if tegn:
        grunner.append(f"1: tegnene «{''.join(tegn)}» utenfor formene")
    return Kontrollsvar(besto=not grunner, grunner=tuple(grunner))


# --- Raden (FR-604, FR-605) --------------------------------------------------


def _uten_tekst(emne: Emne, grunnlag, modell: Modell, grunn: str) -> KIRad:
    return KIRad(
        emne=emne,
        grunnlag=grunnlag,
        regelen=dagsregel(grunnlag),
        tekst=None,
        besto=False,
        grunn=grunn,
        promptversjon=DAGSPROMPTVERSJON,
        tjeneste=modell.tjeneste,
        modell=modell.modell,
    )


def dagsrad_uten_kall(emne: Emne, grunnlag: Mapping[str, object], modell: Modell, foerste: str) -> KIRad:
    """Raden naar modellen feilet for en aksje samme kveld: den kalles ikke
    for dagen, og raden sier hvorfor (som _rad_uten_kall i ki_tekst.py)."""
    return _uten_tekst(
        emne, grunnlag, modell, f"modellen feilet: ikke kalt, fordi den feilet for {foerste} i samme kjøring"
    )


def lag_dagsrad(emne: Emne, grunnlag: Mapping[str, object], modell: Modell) -> KIRad:
    """Kall modellen én gang for dagen og gi raden for KILogg, som
    lag_ki_rad i ki_modell.py gjoer for én aksje."""
    if not isinstance(emne, Emne) or emne.slag != DAG:
        raise ValueError("lag_dagsrad gjelder én børsdag (emnet dag)")
    if type(grunnlag.get("aksjer")) is not int or type(grunnlag.get("skilte_seg_ut")) is not int:
        raise ValueError("grunnlaget maa vaere fra dagsgrunnlag")
    try:
        svar = modell.lag_tekst(lag_dagsprompt(grunnlag))
    except ModellFeilet as feil:
        return _uten_tekst(emne, grunnlag, modell, _grunn(str(feil)))
    if not isinstance(svar, Modellsvar):
        return _uten_tekst(emne, grunnlag, modell, _grunn("svaret var ikke et Modellsvar"))
    tekst = svar.tekst.strip() if isinstance(svar.tekst, str) else ""
    kjoering = dict(
        promptversjon=DAGSPROMPTVERSJON,
        tjeneste=modell.tjeneste,
        modell=svar.modell,
        modell_id=svar.modell_id,
        seed=svar.seed,
        temperatur=svar.temperatur,
        maskinvare=svar.maskinvare,
        ollama_versjon=svar.ollama_versjon,
    )
    try:
        if not tekst:
            return KIRad(
                emne=emne,
                grunnlag=grunnlag,
                regelen=dagsregel(grunnlag),
                tekst=None,
                besto=False,
                grunn=_grunn("tom tekst"),
                **kjoering,
            )
        kontroll = kontroller_dagen(tekst, grunnlag)
        return KIRad(
            emne=emne,
            grunnlag=grunnlag,
            regelen=dagsregel(grunnlag),
            tekst=tekst,
            besto=kontroll.besto,
            grunn=kontroll.grunn,
            **kjoering,
        )
    except UgyldigKIRad:
        return _uten_tekst(emne, grunnlag, modell, _grunn("ugyldige verdier i svaret"))
