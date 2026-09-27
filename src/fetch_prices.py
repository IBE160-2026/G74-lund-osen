"""Henter sluttkurser for OSE Signal sitt aksjeunivers fra EODHD.

Dette scriptet er det eneste stedet i prosjektet som bruker API-kvote.
Ett kall per symbol, 15 symboler, altsaa 15 kall per kjoering. Gratisnivaaet
gir 20 kall i doegnet, saa det er plass til EN kjoering per dag og litt til.
Kjoer det bevisst - ikke i loekke, og aldri fra websiden.

Hvert kall henter et helt aar. Det koster noeyaktig det samme som aa hente
fjorten dager - ett kall per symbol uansett intervallengde, maalt og foert i
malinger.md §2 - og MA50 trenger 51 handelsdager foer signalet i det hele tatt
kan regnes. Aa hente kort ville derfor kostet like mye og gitt en tom
signalkolonne.

Resultatet skrives som et tidsstemplet oeyeblikksbilde som aldri skrives om
(FR-406, NFR-07), i formatet visningen leser gjennom lagring_fil.SnapshotLeser.
"""

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable
from urllib.parse import quote, quote_plus

import requests
from dotenv import load_dotenv

from eodhd import UgyldigSerie, serie_fra_eodhd
from kursdata import AKSJEUNIVERS
from lagring_fil import DATA_KATALOG, KURSPREFIKS, PROSJEKTROT

BASE_URL = "https://eodhd.com/api/eod"

# Gratisnivaaet gir ett aars historikk. 364 dager holder seg innenfor med en
# dags margin - det var intervallet som faktisk svarte 2026-09-21, og det ga
# 249 handelsdager per symbol.
DAGER_TILBAKE = 364

# MA50 spiser 50 dager. Under dette kan ingen aksje faa et signal.
MINST_HANDELSDAGER = 51


@dataclass
class Resultat:
    """Hva en kjoering endte med. Kallene telles uansett om de lyktes."""

    serier: dict[str, list[dict]] = field(default_factory=dict)
    feil: dict[str, str] = field(default_factory=dict)
    kall_brukt: int = 0


def hent_api_nokkel() -> str:
    load_dotenv(PROSJEKTROT / ".env")
    nokkel = os.getenv("EODHD_API_KEY")
    if not nokkel:
        sys.exit("EODHD_API_KEY mangler. Legg den i .env i prosjektroten.")
    return nokkel


def bygg_intervall(i_dag: date | None = None) -> tuple[str, str]:
    """Fra- og til-dato for hentingen. Begge inklusive, jf. malinger.md §2."""
    i_dag = i_dag or date.today()
    return (i_dag - timedelta(days=DAGER_TILBAKE)).isoformat(), i_dag.isoformat()


def hent_ett_symbol(ticker: str, api_nokkel: str, fra: str, til: str) -> list[dict]:
    """Ett API-kall. Eneste funksjonen i prosjektet som roerer nettet.

    Noekkelen gaar som api_token i adressen, og requests tar med hele
    adressen i teksten til sine feil. Enhver feil fra kallet og
    raise_for_status() blir derfor en ny feil med en tekst uten adressen
    (story 2.0): statuskode og aarsak for en HTTP-feil, bare typenavnet for
    resten. from None kutter kjeden, saa heller ikke en traceback viser den
    gamle teksten. Den nye HTTPError faar ingen response, fordi response.url
    ogsaa har noekkelen. svar.json() ligger utenfor: en feil der er om
    innholdet, ikke adressen, og andre lag i hent_universet fanger resten.
    """
    try:
        svar = requests.get(
            f"{BASE_URL}/{ticker}",
            params={
                "api_token": api_nokkel,
                "fmt": "json",
                "period": "d",
                "from": fra,
                "to": til,
            },
            timeout=60,
        )
        svar.raise_for_status()
    except requests.HTTPError as feil:
        r = feil.response
        tekst = f"HTTP {r.status_code} {r.reason or ''}".strip() if r is not None else "HTTPError"
        raise requests.HTTPError(tekst) from None
    except requests.RequestException as feil:
        raise type(feil)(type(feil).__name__) from None
    return svar.json()


def _uten_noekkel(tekst: str, api_nokkel: str) -> str:
    """Noekkelen byttet med *** - andre lag, for feil som ikke kom fra requests.

    Ogsaa slik den ser ut URL-kodet, fordi requests koder params."""
    if not api_nokkel:
        return tekst
    for form in {api_nokkel, quote(api_nokkel, safe=""), quote_plus(api_nokkel)}:
        tekst = tekst.replace(form, "***")
    return tekst



def hent_universet(
    api_nokkel: str,
    fra: str,
    til: str,
    hent: Callable[[str, str, str, str], list[dict]] = hent_ett_symbol,
    skriv: Callable[[str], None] = print,
) -> Resultat:
    """Ett kall per aksje i universet. Stopper aldri paa en enkelt feil.

    Hentingen er injisert saa testene kan kjoere hele loekka uten nett.

    Et symbol som feiler gir ingen ny sjanse - det ville kostet et kall til,
    og kvoten er for liten til aa brenne kall paa en feil vi ikke har
    forstaatt. De andre symbolene hentes likevel: en halv oversikt er bedre
    enn ingen, og NFR-03 sier at manglende data for en aksje ikke skal stoppe
    hovedflyten.
    """
    resultat = Resultat()

    for aksje in AKSJEUNIVERS:
        try:
            rader = hent(aksje.ticker, api_nokkel, fra, til)
            resultat.kall_brukt += 1
        except Exception as feil:  # noqa: BLE001 - alt som feiler har kostet kallet
            resultat.kall_brukt += 1
            resultat.feil[aksje.symbol] = _uten_noekkel(
                f"{type(feil).__name__}: {feil}", api_nokkel
            )
            skriv(f"  {aksje.symbol}: FEIL {_uten_noekkel(str(feil), api_nokkel)}")
            continue

        # Story 2.0, valg A: et svar med feil form skal ikke stoppe hele
        # hentingen etter at kallene er brukt (AD-15, NFR-03). Formen sjekkes
        # foerst, saa et tomt objekt eller None ikke fores som «tomt svar».
        # Story 1.8: formen er det SnapshotLeser kan lese, avgjort av samme
        # funksjon. En serie leseren ville droppet, lagres ikke som hentet.
        try:
            serie = serie_fra_eodhd(rader)
        except UgyldigSerie:
            resultat.feil[aksje.symbol] = "svar med feil form"
            skriv(f"  {aksje.symbol}: svar med feil form")
            continue

        if not serie:
            resultat.feil[aksje.symbol] = "tomt svar"
            skriv(f"  {aksje.symbol}: ingen data")
            continue

        # Raadataene lagres uendret. Oversettelsen er bare kontrollen.
        resultat.serier[aksje.symbol] = rader
        merknad = "" if len(serie) >= MINST_HANDELSDAGER else "  ← for kort for MA50"
        skriv(
            f"  {aksje.symbol}: {len(serie)} dager, "
            f"siste {serie[-1].dato.isoformat()}{merknad}"
        )

    return resultat


def lag_oyeblikksbilde(resultat: Resultat, fra: str, til: str, naa: str) -> dict:
    """Formatet visningen leser gjennom lagring_fil.SnapshotLeser. Skrives
    aldri om etterpaa."""
    return {
        "hentet": naa,
        "from": fra,
        "to": til,
        "kilde": "EODHD /api/eod",
        "serier": resultat.serier,
        "feil": resultat.feil,
    }


def filnavn(i_dag: date | None = None) -> str:
    """Datoen staar i navnet, saa oeyeblikksbilder aldri overskriver hverandre.

    Prefikset kommer fra lagring_fil og skrives ikke av her. nyeste_snapshot lar
    nettopp dette prefikset vinne ved lik dato, saa de to maa ikke kunne gli
    fra hverandre.
    """
    return f"{KURSPREFIKS}-raa-{(i_dag or date.today()).isoformat()}.json"


def kjoer(
    data_katalog: Path,
    i_dag: date,
    api_nokkel: str,
    hent: Callable[[str, str, str, str], list[dict]] = hent_ett_symbol,
    skriv: Callable[[str], None] = print,
) -> Path | None:
    """En henting. Returnerer fila som ble skrevet, eller None hvis dagens fil
    fantes fra foer.

    Et oeyeblikksbilde skrives aldri om (AD-6, story 2.0). Finnes dagens fil,
    stopper kjoeringen foer foerste kall. Det er ingen feil. Fila skrives med
    modus "x", saa en fil som dukker opp mens kjoeringen paagaar, heller ikke
    skrives over. Da er kallene brukt og ingenting lagret, og kjoeringen
    avslutter med kode 1. Story 2.3 bygger videre paa dette med forventet
    boersdag.
    """
    data_katalog.mkdir(parents=True, exist_ok=True)
    fil = data_katalog / filnavn(i_dag)
    if fil.exists():
        skriv(
            f"Dagens oeyeblikksbilde {fil.name} finnes allerede. Hentingen er "
            "stoppet foer noe kall er brukt (AD-6). 0 kall brukt."
        )
        return None

    fra, til = bygg_intervall(i_dag)
    skriv(f"Henter {len(AKSJEUNIVERS)} symboler, {fra} til {til}.")
    skriv(f"Dette koster {len(AKSJEUNIVERS)} av dagskvoten paa 20.\n")

    resultat = hent_universet(api_nokkel, fra, til, hent, skriv)

    naa = datetime.now(timezone.utc).isoformat()
    tekst = json.dumps(lag_oyeblikksbilde(resultat, fra, til, naa), ensure_ascii=False)
    try:
        with open(fil, "x", encoding="utf-8") as ut:
            ut.write(tekst)
    except FileExistsError:
        skriv(
            f"{fil.name} dukket opp mens hentingen paagikk, og er ikke skrevet "
            f"over (AD-6). {resultat.kall_brukt} kall er brukt, og ingenting er lagret."
        )
        sys.exit(1)

    skriv(f"\nLagret {fil.name} i {data_katalog.name}/")
    skriv(f"API-kall brukt: {resultat.kall_brukt}")
    if resultat.feil:
        skriv(f"Symboler uten data: {', '.join(sorted(resultat.feil))}")
    return fil


def main() -> None:
    kjoer(DATA_KATALOG, date.today(), hent_api_nokkel())


if __name__ == "__main__":
    main()
