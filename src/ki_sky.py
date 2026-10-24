"""Det de tre tjenestene med egen noekkel har felles - story 10.7, FR-604,
AD-2, AD-12.

ki_gemini.py, ki_anthropic.py og ki_openai.py har hver sin adresse, sine
headere og sin form paa svaret. Her er hentefunksjonen de bruker som
standard, og kallet rundt den, som gjoer alt som gaar galt om til
ModellFeilet (ki_modell.py). Hver adapter faar fortsatt sin egen
hentefunksjon injisert (AD-2), og testene gir en falsk.

Noekkelen (gjennomgangen av 10.7):
- sendes bare i headeren adapteren gir, og hentefunksjonen foelger ingen
  videresending, saa den ikke gaar videre til en annen vert (BH4, VG5)
- sjekkes foer kallet: et tegn som ikke kan staa i en header, gir en grunn
  i stedet for en feil som stopper steget (ECH1, BH6, VG4). Fra 10.7b
  sjekkes den foer foerste aksje, og mangler den eller har slike tegn,
  skrives ingen rader (gruppens svar 22.10 kl. 14:38)
- kommer aldri med i grunnen. Grunnen har bare tjenesten, HTTP-statusen,
  tidsavbruddet eller typen paa feilen, og ModellFeilet reises utenfor
  except-blokken, saa feilen fra requests ikke henger ved den (BH5, ECH10)
"""

from collections.abc import Callable

import requests

from ki_modell import ModellFeilet

# Det lengste modellnavnet fra svaret som lagres i modell_id (ECH5).
LENGSTE_MODELLNAVN = 100

Http = Callable[[str, dict[str, str], dict, float], tuple[int, object]]


def http(url: str, headere: dict[str, str], json: dict, tidsfrist: float) -> tuple[int, object]:
    """Standard hentefunksjon (AD-2): POST med JSON, uten videresending. Gir
    status og JSON-svaret."""
    svar = requests.post(url, headers=headere, json=json, timeout=tidsfrist, allow_redirects=False)
    try:
        innhold = svar.json()
    except ValueError:
        innhold = None
    return svar.status_code, innhold


def noekkel_feil(noekkel: str, variabel: str) -> str | None:
    """Grunnen naar noekkelen mangler eller har et tegn som ikke kan sendes i
    en header, ellers None. Grunnen nevner variabelen, aldri noekkelen. Ingen
    kall: sjekk i adapterne bruker den foer foerste kall (spesifikasjonen 10.7b)."""
    if not noekkel:
        return f"{variabel} mangler"
    if not (noekkel.isascii() and noekkel.isprintable()) or " " in noekkel:
        return f"{variabel} har tegn som ikke kan sendes, lim den inn på nytt"
    return None


def sjekk_noekkel(noekkel: str, variabel: str) -> None:
    """Reiser ModellFeilet med grunnen fra noekkel_feil, saa en adapter som
    kalles uten sjekken, aldri sender uten noekkel."""
    if grunn := noekkel_feil(noekkel, variabel):
        raise ModellFeilet(grunn)


def kall(navn: str, hent: Http, url: str, headere: dict[str, str], kropp: dict, tidsfrist: float) -> dict:
    """Ett kall til tjenesten. Gir svaret naar statusen er 200 og svaret er
    et JSON-objekt, ellers ModellFeilet med en kort grunn."""
    grunn = None
    try:
        status, svar = hent(url, headere, kropp, tidsfrist)
    except requests.Timeout:
        grunn = f"tidsavbrudd etter {tidsfrist:g} s"
    except requests.ConnectionError:
        grunn = f"{navn} svarer ikke"
    except (requests.RequestException, UnicodeError) as feil:
        grunn = type(feil).__name__
    if grunn is not None:
        raise ModellFeilet(grunn)
    if status != 200:
        raise ModellFeilet(f"{navn} svarte HTTP {status}")
    if not isinstance(svar, dict):
        raise ModellFeilet(f"svaret fra {navn} kunne ikke leses")
    return svar


def tekst_fra(navn: str, deler: list) -> str:
    """Tekstdelene satt sammen, eller ModellFeilet naar det ikke er noen,
    eller naar teksten har tegn som ikke kan lagres (ECH13). En tekst med
    bare mellomrom gaar videre: lag_ki_rad gir den grunnen «tom tekst»."""
    if not deler or not all(isinstance(d, str) for d in deler):
        raise ModellFeilet(f"svaret fra {navn} hadde ingen tekst")
    tekst = "".join(deler)
    try:
        tekst.encode("utf-8")
    except UnicodeEncodeError:
        raise ModellFeilet(f"svaret fra {navn} hadde tegn som ikke kan lagres") from None
    return tekst


def modell_id(svar: dict, modell: str) -> str | None:
    """Modellen tjenesten sier svarte, naar den er et navn paa modellen som
    ble bedt om, ellers None. Saa havner ikke hva som helst fra svaret i
    loggen (ECH5)."""
    svart = svar.get("model")
    if not isinstance(svart, str):
        return None
    svart = svart.strip()
    if not svart.startswith(modell) or len(svart) > LENGSTE_MODELLNAVN:
        return None
    try:
        svart.encode("utf-8")
    except UnicodeEncodeError:
        return None
    return svart
