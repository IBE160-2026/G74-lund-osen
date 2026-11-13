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

Story 10.11, promptversjon dag-3 (gruppens svar 11.11 kl. 22:04, funn 4 fra
demoproeven): formene med «mest» sier «av bransjene med minst to aksjer»
(AV_BRANSJENE), fordi snittet bare regnes for bransjer med minst
MINST_I_BRANSJEN aksjer med en endring, og leseren ellers ser en bransje med
én aksje som falt mer paa Boersometeret. Kontrollen godtar bare de nye
formene for «mest». Grunnlaget og tallene er de samme som i dag-2.
"""

import json
import re
from collections.abc import Mapping

from dagene import MINST_I_BRANSJEN
from dagsgrunnlag import ANDRE, MEST_NED, MEST_OPP, MOT_VANLIG, NAVNENE, UKA, VANLIG
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

DAGSPROMPTVERSJON = "dag-3"

# Story 10.11: det formene med «mest» slutter med, regnet av grensen for
# bransjene, saa formen foelger MINST_I_BRANSJEN (spoersmaal 1).
_SOM_ORD = {2: "to", 3: "tre", 4: "fire", 5: "fem"}
AV_BRANSJENE = f"av bransjene med minst {_SOM_ORD[MINST_I_BRANSJEN]} aksjer"

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
- bransje_mest_opp og bransje_mest_ned: {av_bransjene}, bransjen der aksjene i snitt steg mest, og bransjen der de i snitt falt mest, regnet ut av appen. Feltene kan mangle.
- skilte_seg_ut_vanlig og skilte_seg_ut_mot_vanlig: snittet av hvor mange som skilte seg ut de siste 20 børsdagene, som et helt tall, og om det var flere, færre eller like mange denne dagen. Feltene kan mangle.
- hovedindeksen_uka: om hovedindeksen steg, falt eller var uendret de siste fem børsdagene. Feltet kan mangle.

Regler for teksten:
- Skriv tre til ni korte setninger, med disse formene og i denne rekkefølgen. Sett inn tallene og ordene for feltene i ‹ ›:
  - «Hovedindeksen steg ‹ukedag›.», «Hovedindeksen falt ‹ukedag›.» eller «Hovedindeksen var uendret ‹ukedag›.», etter feltet hovedindeksen.
  - «De siste fem børsdagene steg hovedindeksen.», «De siste fem børsdagene falt hovedindeksen.» eller «De siste fem børsdagene var hovedindeksen uendret.», etter feltet hovedindeksen_uka.
  - «‹bedre_enn_indeksen› av ‹med_kurs› aksjer gjorde det bedre enn indeksen.»
  - «‹skilte_seg_ut› skilte seg ut: ‹skilte_seg_ut_positiv› med positiv retning, ‹skilte_seg_ut_negativ› negativ og ‹skilte_seg_ut_blandet› blandet.» Ta bare med retningene som har minst én aksje. Er skilte_seg_ut 0, skriver du «Ingen aksjer skilte seg ut.»
  - «Det var flere enn vanlig: snittet de siste 20 børsdagene er ‹skilte_seg_ut_vanlig›.», med «flere enn», «færre enn» eller «like mange som» etter feltet skilte_seg_ut_mot_vanlig.
  - Om navnene skriver du formen for navnene denne dagen, som står under opplysningene, ordrett og som én setning, når den står der. Den har formen «Blant dem var ‹navn› (‹styrke› av 3, ‹retning›), ‹navn› (‹styrke› av 3, ‹retning›) og ‹skilte_seg_ut_andre› andre.»
  - «I snitt steg ‹bransje_mest_opp› mest {av_bransjene}.» og «I snitt falt ‹bransje_mest_ned› mest {av_bransjene}.», med navnet på bransjen med små bokstaver.
{bransjeformen}- Mangler et felt, skriver du ikke setningen for det.
- Skriv tallene som i opplysningene. Ikke nevn andre tall, prosenter, kurser eller beløp.
- Ikke si noe om hovedindeksen, bransjene, retningene eller hvor mange som steg eller falt utenom formene.
- Ikke skriv «i dag», «i går» eller «i kveld». Bruk ukedagen.
- Ikke gi råd om å kjøpe, selge eller holde, ikke skriv «bør», «verdt å følge» eller «følg med», og ikke si noe om hva som vil skje.
- Ikke gjett på årsaker, som nyheter, resultater, renter eller oljeprisen.
- Ikke finn mønstre selv, og ikke sammenlign aksjene eller bransjene med hverandre utover formene.
- Skriv aldri navnet på et felt eller tegnene ‹ › i teksten.
"""
# Gjennomgangen av 10.11 (BH2, ECH1, VG2): prompten faar AV_BRANSJENE herfra,
# saa prompten, kontrollen og eksempelskriveren sier det samme om grensen.
REGLER_DAGEN = REGLER_DAGEN.replace("{av_bransjene}", AV_BRANSJENE)


# Story 10.10: Gemma satte punktum foer «og 2 andre» (11.11), saa appen gir
# setningen med navnene ferdig, som setningen om de siste 20 boersdagene for
# én aksje. Kontrollen leser den som foer, navn for navn.
SETNINGEN_NAVN = "\nFormen for navnene denne dagen er «{setning}»\n"


def setning_om_navnene(grunnlag: Mapping[str, object]) -> str | None:
    """«Blant dem var …» med navnene i grunnlaget og resten som antall, eller
    None uten navn."""
    deler = [f"{n['navn']} ({n['styrke']} av 3, {n['retning']})" for n in grunnlag.get(NAVNENE) or ()]
    if not deler:
        return None
    if grunnlag.get(ANDRE):
        deler.append(f"{grunnlag[ANDRE]} andre")
    oppramsing = deler[0] if len(deler) == 1 else ", ".join(deler[:-1]) + " og " + deler[-1]
    return f"Blant dem var {oppramsing}."


# Svaret 11.11 kl. 19:30: formen med antallet i én bransje er med i reglene
# bare naar verken bransjen som steg mest eller den som falt mest kan staa,
# fordi modellen ellers valgte to bransjer selv.
BRANSJEFORMEN = (
    "  - «I ‹bransje› steg ‹steg› av ‹med_endring› aksjer.», med navnet på bransjen med små bokstaver. "
    "Nevn høyst to bransjer.\n"
)


def reglene(grunnlag: Mapping[str, object]) -> str:
    """Reglene for dagen, med formen for én bransje bare uten «mest»."""
    uten_mest = MEST_OPP not in grunnlag and MEST_NED not in grunnlag
    return REGLER_DAGEN.replace("{bransjeformen}", BRANSJEFORMEN if uten_mest else "")


def lag_dagsprompt(grunnlag: Mapping[str, object]) -> str:
    """Reglene, grunnlaget som JSON og setningen med navnene. Ingenting annet
    kommer med."""
    prompt = (
        reglene(grunnlag)
        + "\nOpplysningene:\n"
        + json.dumps(_vanlig(grunnlag), ensure_ascii=False, sort_keys=True)
        + "\n"
    )
    setning = setning_om_navnene(grunnlag)
    if setning:
        prompt += SETNINGEN_NAVN.format(setning=setning)
    return prompt


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
    if VANLIG in grunnlag:
        deler.append(f"Mot vanlig: {grunnlag[MOT_VANLIG]}, snittet {grunnlag[VANLIG]}.")
    if UKA in grunnlag:
        deler.append(f"Hovedindeksen siste fem børsdager: {grunnlag[UKA]}.")
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
# Story 10.11: formen slutter med AV_BRANSJENE. Uten den leses formen
# likevel, saa kontrollen kan si hvorfor den stoppes (spoersmaal 2).
_F_MEST = re.compile(
    r"(?<![\w-])i\s+snitt\s+(steg|falt)\s+([a-zæøå]+(?:[\s-]+(?:og\s+)?[a-zæøå]+)?)\s+mest"
    r"(\s+" + r"\s+".join(AV_BRANSJENE.split()) + r")?(?![\w-])",
    re.IGNORECASE,
)
_MEST_FELT = {"steg": MEST_OPP, "falt": MEST_NED}
# Tillegget kl. 17:21 (spoersmaal 11 og 12).
_F_VANLIG = re.compile(
    r"(?<![\w-])det\s+var\s+(flere\s+enn|færre\s+enn|like\s+mange\s+som)\s+vanlig\s*:\s*snittet\s+de\s+siste\s+20\s+"
    r"børsdagene\s+er\s+" + _N,
    re.IGNORECASE,
)
_MOT = {"flere enn": "flere", "færre enn": "færre", "like mange som": "like mange"}
_F_UKA = re.compile(
    r"(?<![\w-])de\s+siste\s+fem\s+børsdagene\s+(?:(steg|falt)\s+hovedindeksen|var\s+hovedindeksen\s+(uendret))(?![\w-])",
    re.IGNORECASE,
)
_ORD = re.compile(r"[\w-]+")
# Tegnsettingen som kan staa mellom formene.
_TEGN = frozenset(" \t\n.,:;")
_NAA = re.compile(r"(?<![\w-])(i\s+dag|i\s+går|i\s+kveld|i\s+morgen|dagens|gårsdagens)(?![\w-])", re.IGNORECASE)


def _navnet(navn: str) -> re.Pattern[str]:
    """Navnet ordrett, med store og smaa bokstaver som i grunnlaget og
    hvilket som helst mellomrom der navnet har et (ogsaa et hardt), og
    styrken og retningen i parentesen etter. Navnet normaliseres som
    teksten (gjennomgangen, ECH5, VG6)."""
    deler = [re.escape(del_) for del_ in normaliser(str(navn)).split()]
    return re.compile(r"(?<![\w-])(?-i:" + r"\s+".join(deler) + ")" + _I_PARENTES, re.IGNORECASE)


def _navnene(tekst: str, grunnlag: Mapping[str, object]) -> tuple[str, list[str]]:
    """Setningen med navnene (story 10.10). Gir teksten uten formen, og
    grunnene.

    Gjennomgangen (BH1, ECH1, BH7, ECH2-ECH4): bruker teksten navnene, skal
    alle navnene i grunnlaget staa der, i rekkefoelgen der, i én setning
    etter «Blant dem var», med «og ‹N› andre» bare naar feltet er der. Det
    lengste navnet leses foerst, saa «BP» ikke finnes inne i «Aker BP», og
    to aksjer med samme navn leses som to oppfoeringer."""
    grunner: list[str] = []
    oppfoeringer = list(grunnlag.get(NAVNENE) or ())
    funnet: list[tuple[int, int]] = []
    for navn in sorted({normaliser(str(o["navn"])) for o in oppfoeringer}, key=len, reverse=True):
        ventet = [(i, o) for i, o in enumerate(oppfoeringer) if normaliser(str(o["navn"])) == navn]
        alle = list(_navnet(navn).finditer(tekst))
        if len(alle) > len(ventet):
            grunner.append(f"1: navnet «{navn}» står {len(alle)} ganger")
        igjen = list(ventet)
        for treff in alle:
            styrke, retning = int(treff.group(1)), treff.group(2).lower()
            passer = next((p for p in igjen if (p[1]["styrke"], p[1]["retning"]) == (styrke, retning)), None)
            if passer is None:
                oppfoering = (igjen or ventet)[0][1]
                if styrke != oppfoering["styrke"]:
                    grunner.append(f"2: tallet «{treff.group(1)}» ved styrken for {navn}")
                if retning != oppfoering["retning"]:
                    grunner.append(
                        f"1: retningen «{treff.group(2)}» for {navn}, grunnlaget sier {oppfoering['retning']}"
                    )
                passer = igjen[0] if igjen else None
            if passer is not None:
                igjen.remove(passer)
                funnet.append((treff.start(), passer[0]))
            tekst = _ta_ut(tekst, treff)
    blant = list(_F_BLANT.finditer(tekst))
    andre = list(_F_ANDRE.finditer(tekst))
    for treff in blant:
        if not oppfoeringer:
            grunner.append(f"1: «{treff.group(0)}», men {NAVNENE} mangler i grunnlaget")
    for treff in andre:
        if ANDRE not in grunnlag:
            grunner.append(f"1: «{treff.group(0)}», men {ANDRE} mangler i grunnlaget")
        elif _antall(treff.group(1)) != grunnlag[ANDRE]:
            grunner.append(f"2: tallet «{treff.group(1)}» ved {ANDRE}")
    if oppfoeringer and (funnet or blant or andre):
        if len(blant) != 1:
            grunner.append("1: «Blant dem var» skal stå én gang foran navnene")
        if len(funnet) != len(oppfoeringer):
            grunner.append(f"1: setningen med navnene har {len(funnet)} av {len(oppfoeringer)} navn")
        if len(andre) > 1 or (ANDRE in grunnlag) != bool(andre):
            grunner.append(f"1: «og ‹N› andre» skal stå én gang bare når {ANDRE} er i grunnlaget")
        rekkefoelgen = [i for _start, i in sorted(funnet)]
        if rekkefoelgen != sorted(rekkefoelgen):
            grunner.append("1: navnene står ikke i rekkefølgen i grunnlaget")
        if len(blant) == 1:
            start = blant[0].end()
            slutt = max([s for s, _i in funnet] + [t.start() for t in andre] + [start])
            if any(s < blant[0].start() for s, _i in funnet) or re.search(r"[.!?]", tekst[start:slutt]):
                grunner.append("1: navnene står ikke i setningen etter «Blant dem var»")
    for treff in blant + andre:
        tekst = _ta_ut(tekst, treff)
    return tekst, grunner


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
    tekst, navnegrunner = _navnene(tekst, grunnlag)
    grunner += navnegrunner
    # Tillegget kl. 17:21: antallet mot vanlig og hovedindeksen siste uke,
    # foer formene for hovedindeksen, saa ordene der ikke leses to ganger.
    # Gjennomgangen av tillegget (ECH1): hver form én gang.
    for form, navn in ((_F_VANLIG, "antallet mot vanlig"), (_F_UKA, "hovedindeksen siste fem børsdager")):
        if len(form.findall(tekst)) > 1:
            grunner.append(f"1: setningen om {navn} står mer enn én gang")
    for treff in list(_F_VANLIG.finditer(tekst)):
        mot = _MOT[" ".join(treff.group(1).lower().split())]
        if VANLIG not in grunnlag:
            grunner.append(f"1: «{treff.group(0)}», men {VANLIG} mangler i grunnlaget")
        else:
            if mot != grunnlag[MOT_VANLIG]:
                grunner.append(f"1: «{treff.group(0)}», grunnlaget sier {grunnlag[MOT_VANLIG]}")
            if _antall(treff.group(2)) != grunnlag[VANLIG]:
                grunner.append(f"2: tallet «{treff.group(2)}» ved {VANLIG}")
        tekst = _ta_ut(tekst, treff)
    for treff in list(_F_UKA.finditer(tekst)):
        verb = (treff.group(1) or treff.group(2)).lower()
        if UKA not in grunnlag:
            grunner.append(f"1: «{treff.group(0)}», men {UKA} mangler i grunnlaget")
        elif verb != grunnlag[UKA]:
            grunner.append(f"1: «{treff.group(0)}», grunnlaget sier {grunnlag[UKA]}")
        tekst = _ta_ut(tekst, treff)
    mest = list(_F_MEST.finditer(tekst))
    # Gjennomgangen (ECH4): hver bransje én gang.
    for verb in ("steg", "falt"):
        if sum(1 for t in mest if t.group(1).lower() == verb) > 1:
            grunner.append(f"1: «I snitt {verb} … mest» står mer enn én gang")
    for treff in mest:
        felt = _MEST_FELT[treff.group(1).lower()]
        navn = " ".join(treff.group(2).lower().split())
        if felt not in grunnlag:
            grunner.append(f"1: «{treff.group(0)}», men {felt} mangler i grunnlaget")
        elif navn != str(grunnlag[felt]).lower():
            grunner.append(f"1: «{treff.group(0)}», grunnlaget sier {grunnlag[felt]}")
        if treff.group(3) is None:
            grunner.append(f"1: «{treff.group(0)}» sier ikke «{AV_BRANSJENE}»")
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
        # Svaret 11.11 kl. 19:30: med «mest» i grunnlaget står ikke formen.
        if MEST_OPP in grunnlag or MEST_NED in grunnlag:
            grunner.append(f"1: «{treff.group(0)}», formen står ikke når bransjen som steg eller falt mest kan stå")
        elif navn not in bransjer:
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
