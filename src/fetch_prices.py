"""Henter sluttkurser for OSE Signal sitt aksjeunivers fra EODHD.

Dette scriptet er det eneste stedet i prosjektet som bruker API-kvote.
Ett kall per symbol. Gratisnivaaet gir 20 kall i doegnet, saa kjoer det
bevisst - ikke i loekke, og ikke fra websiden.

Raadata lagres slik de kom fra API-et, saa vi kan analysere paa nytt uten
aa bruke flere kall.
"""

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

# Fem likvide aksjer fra ulike sektorer. Navnene er hardkodet fordi
# /api/eod ikke returnerer selskapsnavn, og et oppslag for aa hente dem
# ville kostet ekstra kall uten aa gi noe vi ikke allerede vet.
AKSJER = {
    "EQNR.OL": "Equinor",
    "DNB.OL": "DNB Bank",
    "TEL.OL": "Telenor",
    "YAR.OL": "Yara International",
    "NHY.OL": "Norsk Hydro",
}

PROSJEKTROT = Path(__file__).resolve().parent.parent
DATA_KATALOG = PROSJEKTROT / "data"
BASE_URL = "https://eodhd.com/api/eod"


def hent_api_nokkel() -> str:
    load_dotenv(PROSJEKTROT / ".env")
    nokkel = os.getenv("EODHD_API_KEY")
    if not nokkel:
        sys.exit("EODHD_API_KEY mangler. Legg den i .env i prosjektroten.")
    return nokkel


def hent_ett_symbol(symbol: str, api_nokkel: str) -> list[dict]:
    """Ett API-kall. Henter de siste ukene, ikke hele historikken."""
    fra_dato = date.today() - timedelta(days=14)
    svar = requests.get(
        f"{BASE_URL}/{symbol}",
        params={
            "api_token": api_nokkel,
            "fmt": "json",
            "period": "d",
            "from": fra_dato.isoformat(),
        },
        timeout=30,
    )
    svar.raise_for_status()
    return svar.json()


def main() -> None:
    api_nokkel = hent_api_nokkel()
    DATA_KATALOG.mkdir(exist_ok=True)

    kall_brukt = 0
    resultat: dict[str, list[dict]] = {}

    for symbol in AKSJER:
        try:
            rader = hent_ett_symbol(symbol, api_nokkel)
            kall_brukt += 1
        except requests.HTTPError as feil:
            # Stopp heller enn aa proeve paa nytt - kvoten er for liten
            # til aa brenne kall paa en feil vi ikke har forstaatt.
            sys.exit(f"{symbol} feilet: {feil}. Stopper etter {kall_brukt} kall.")

        if not rader:
            print(f"  {symbol}: ingen data")
            continue

        resultat[symbol] = rader
        print(f"  {symbol}: {len(rader)} dager, siste {rader[-1]['date']}")

    fil = DATA_KATALOG / "sluttkurser.json"
    fil.write_text(
        json.dumps(
            {"hentet": date.today().isoformat(), "aksjer": resultat},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"\nLagret {fil.relative_to(PROSJEKTROT)}")
    print(f"API-kall brukt: {kall_brukt}")


if __name__ == "__main__":
    main()
