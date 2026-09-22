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
(FR-406, NFR-07), i samme format som kursdata.SnapshotKilde leser.
"""

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

import requests
from dotenv import load_dotenv

from kursdata import AKSJEUNIVERS, DATA_KATALOG, KURSPREFIKS, PROSJEKTROT

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
    """Ett API-kall. Eneste funksjonen i prosjektet som roerer nettet."""
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
    return svar.json()


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
            resultat.feil[aksje.symbol] = f"{type(feil).__name__}: {feil}"
            skriv(f"  {aksje.symbol}: FEIL {feil}")
            continue

        if not rader:
            resultat.feil[aksje.symbol] = "tomt svar"
            skriv(f"  {aksje.symbol}: ingen data")
            continue

        resultat.serier[aksje.symbol] = rader
        merknad = "" if len(rader) >= MINST_HANDELSDAGER else "  ← for kort for MA50"
        skriv(f"  {aksje.symbol}: {len(rader)} dager, siste {rader[-1]['date']}{merknad}")

    return resultat


def lag_oyeblikksbilde(resultat: Resultat, fra: str, til: str, naa: str) -> dict:
    """Formatet kursdata.SnapshotKilde leser. Skrives aldri om etterpaa."""
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

    Prefikset kommer fra kursdata og skrives ikke av her. nyeste_snapshot lar
    nettopp dette prefikset vinne ved lik dato, saa de to maa ikke kunne gli
    fra hverandre.
    """
    return f"{KURSPREFIKS}-raa-{(i_dag or date.today()).isoformat()}.json"


def main() -> None:
    api_nokkel = hent_api_nokkel()
    DATA_KATALOG.mkdir(exist_ok=True)

    fra, til = bygg_intervall()
    print(f"Henter {len(AKSJEUNIVERS)} symboler, {fra} til {til}.")
    print(f"Dette koster {len(AKSJEUNIVERS)} av dagskvoten paa 20.\n")

    resultat = hent_universet(api_nokkel, fra, til)

    naa = datetime.now(timezone.utc).isoformat()
    fil = DATA_KATALOG / filnavn()
    fil.write_text(
        json.dumps(lag_oyeblikksbilde(resultat, fra, til, naa), ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nLagret {fil.relative_to(PROSJEKTROT)}")
    print(f"API-kall brukt: {resultat.kall_brukt}")
    if resultat.feil:
        print(f"Symboler uten data: {', '.join(sorted(resultat.feil))}")


if __name__ == "__main__":
    main()
