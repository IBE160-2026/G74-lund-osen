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

Ukedagen skal vaere grunnlagets, og «i dag», «i går» og «i kveld» stoppes,
fordi teksten ogsaa leses senere (spoersmaal 4).
"""

import json
import re
from collections.abc import Mapping

from ki_kontroll import (
    _EGET_MOENSTER,
    _ENHETER,
    _FELTNAVN,
    _GJETNING,
    _RAAD,
    _SIFFER,
    _TALLORD_I_TEKST,
    ANTALLORD,
    Kontrollsvar,
    normaliser,
)
from ki_modell import Modell, ModellFeilet, Modellsvar, _grunn
from kilogg import DAG, Emne, KIRad, UgyldigKIRad

DAGSPROMPTVERSJON = "dag-1"

REGLER_DAGEN = """Du skriver noen korte setninger på norsk om hele børsdagen på Oslo Børs, for en som ikke kjenner reglene i appen.
Appen gir hver aksje et regelbasert signal. En aksje skilte seg ut når minst to av de tre sjekkene i signalet ga utslag.

Opplysningene under er regnet ut av appen for én børsdag og for aksjene i lista:
- aksjer: hvor mange aksjer lista har.
- ukedag: hvilken dag i uka børsdagen var.
- hovedindeksen: om hovedindeksen på Oslo Børs steg, falt eller var uendret. Feltet kan mangle.
- bedre_enn_indeksen og med_kurs: hvor mange av aksjene med kurs den dagen som gjorde det bedre enn hovedindeksen. Feltene kan mangle.
- skilte_seg_ut: hvor mange aksjer som skilte seg ut. skilte_seg_ut_positiv, skilte_seg_ut_negativ og skilte_seg_ut_blandet: hvor mange av dem som hadde positiv, negativ og blandet retning.
- bransjer: for hver bransje, steg er hvor mange aksjer som steg, og med_endring hvor mange som hadde en endring den dagen. Feltet kan mangle.

Regler for teksten:
- Skriv tre til fem setninger, med disse formene. Sett inn tallene og ordene for feltene i ‹ ›:
  - «Hovedindeksen steg ‹ukedag›.», «Hovedindeksen falt ‹ukedag›.» eller «Hovedindeksen var uendret ‹ukedag›.», etter feltet hovedindeksen.
  - «‹bedre_enn_indeksen› av ‹med_kurs› aksjer gjorde det bedre enn indeksen.»
  - «‹skilte_seg_ut› skilte seg ut: ‹skilte_seg_ut_positiv› med positiv retning, ‹skilte_seg_ut_negativ› negativ og ‹skilte_seg_ut_blandet› blandet.» Ta bare med retningene som har minst én aksje. Er skilte_seg_ut 0, skriver du «Ingen aksjer skilte seg ut.»
  - «I ‹bransje› steg ‹steg› av ‹med_endring› aksjer.», med navnet på bransjen med små bokstaver. Nevn høyst to bransjer.
- Mangler et felt, skriver du ikke setningen for det.
- Skriv tallene som i opplysningene. Ikke nevn andre tall, prosenter, kurser eller beløp.
- Ikke si noe om hovedindeksen, bransjene, retningene eller hvor mange som steg eller falt utenom formene.
- Ikke skriv «i dag», «i går» eller «i kveld». Bruk ukedagen.
- Ikke gi råd om å kjøpe, selge eller holde, og ikke si noe om hva som vil skje.
- Ikke gjett på årsaker, som nyheter, resultater, renter eller oljeprisen.
- Ikke finn mønstre selv, og ikke sammenlign bransjene med hverandre.
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
    for navn, b in (grunnlag.get("bransjer") or {}).items():
        deler.append(f"{navn}: steg {b['steg']} av {b['med_endring']}.")
    return " ".join(deler)


# --- Kontrollen (FR-603) -----------------------------------------------------

_N = r"(\d{1,6}|" + "|".join(sorted(ANTALLORD, key=len, reverse=True)) + r")(?![\w-])"
_UKEDAG = r"(mandag|tirsdag|onsdag|torsdag|fredag|lørdag|søndag)"
_F_INDEKSEN = re.compile(
    r"(?<![\w-])hovedindeksen\s+(steg|falt|var\s+uendret)(?:\s+(?:på\s+)?" + _UKEDAG + r")?(?![\w-])", re.IGNORECASE
)
_F_BEDRE = re.compile(
    r"(?<![\w-])" + _N + r"\s+av\s+(?:de\s+)?" + _N + r"\s+aksjer(?:ne)?\s+(?:gjorde\s+det|gikk)\s+bedre\s+enn\s+"
    r"(?:hoved)?indeksen(?![\w-])",
    re.IGNORECASE,
)
_F_SKILTE = re.compile(r"(?<![\w-])" + _N + r"\s+(?:aksjer\s+)?skilte\s+seg\s+ut(?![\w-])", re.IGNORECASE)
_F_RETNING = re.compile(
    r"(?<![\w-])" + _N + r"\s+(?:med\s+)?(positiv|negativ|blandet)(?:e|t)?(?:\s+retning)?(?![\w-])", re.IGNORECASE
)
_F_BRANSJE = re.compile(
    r"(?<![\w-])i\s+([a-zæøå]+(?:[\s-]+(?:og\s+)?[a-zæøå]+)?)\s+steg\s+"
    + _N
    + r"\s+av\s+(?:de\s+)?"
    + _N
    + r"(?:\s+aksjer(?:ne)?)?(?![\w-])",
    re.IGNORECASE,
)
_RETNINGSFELT = {
    "positiv": "skilte_seg_ut_positiv",
    "negativ": "skilte_seg_ut_negativ",
    "blandet": "skilte_seg_ut_blandet",
}
_VERBET = {"steg": "steg", "falt": "falt", "var uendret": "uendret"}

# Utenfor formene: ord kontrollen ikke kan lese (punkt 1).
_UTENFOR = re.compile(
    r"(?<![\w-])((?:hoved)?indeks\w*|børsen|markedet|steg|falt|uendret|stigning\w*|oppgang\w*|nedgang\w*"
    r"|positiv\w*|negativ\w*|blandet|bedre|dårligere|svakere|sterkere|skilte\s+seg\s+ut)(?![\w-])",
    re.IGNORECASE,
)
_UKEDAGENE = re.compile(r"(?<![\w-])" + _UKEDAG + r"(?![\w-])", re.IGNORECASE)
_NAA = re.compile(r"(?<![\w-])(i\s+dag|i\s+går|i\s+kveld|i\s+morgen|dagens|gårsdagens)(?![\w-])", re.IGNORECASE)


def _antall(ord_: str) -> int | None:
    ord_ = ord_.lower()
    if ord_.isdecimal():
        return int(ord_)
    return ANTALLORD.get(ord_)


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

    # Det som er igjen, leses uten formene.
    for treff in _UTENFOR.finditer(tekst):
        grunner.append(f"1: «{treff.group(0)}» utenfor formene")
    for navn in bransjer:
        for treff in re.finditer(r"(?<![\w-])" + re.escape(navn) + r"(?![\w-])", tekst, re.IGNORECASE):
            grunner.append(f"1: bransjen «{treff.group(0)}» utenfor formen")
    for treff in _UKEDAGENE.finditer(normaliser(tekst)):
        if treff.group(1).lower() != grunnlag.get("ukedag"):
            grunner.append(f"1: ukedagen «{treff.group(0)}», grunnlaget sier {grunnlag.get('ukedag')}")
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
