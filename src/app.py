"""Markedsoversikten for OSE Signal.

Leser kun fra data/. Denne filen gjoer aldri API-kall, saa en
nettleseroppdatering kan ikke bruke av kvoten. Nye kurser hentes ved
aa kjoere fetch_prices.py.
"""

import json
from pathlib import Path

from flask import Flask, render_template

from fetch_prices import AKSJER

PROSJEKTROT = Path(__file__).resolve().parent.parent
DATAFIL = PROSJEKTROT / "data" / "sluttkurser.json"

app = Flask(__name__)


def beregn_rad(symbol: str, rader: list[dict]) -> dict:
    """Siste sluttkurs og endring fra dagen foer.

    Endringen regnes paa utbyttejustert kurs, slik at et ordinaert utbytte
    ikke ser ut som et kursfall. Sluttkursen vi viser er den ujusterte,
    fordi det er den kursen aksjen faktisk omsettes til.
    """
    siste = rader[-1]
    forrige = rader[-2] if len(rader) > 1 else None

    endring_prosent = None
    if forrige:
        fra = forrige.get("adjusted_close") or forrige["close"]
        til = siste.get("adjusted_close") or siste["close"]
        if fra:
            endring_prosent = (til - fra) / fra * 100

    return {
        "symbol": symbol,
        "navn": AKSJER.get(symbol, symbol),
        "dato": siste["date"],
        "sluttkurs": siste["close"],
        "endring_prosent": endring_prosent,
    }


@app.route("/")
def markedsoversikt():
    if not DATAFIL.exists():
        return render_template("index.html", rader=[], hentet=None)

    lagret = json.loads(DATAFIL.read_text(encoding="utf-8"))
    rader = [
        beregn_rad(symbol, kursrader)
        for symbol, kursrader in lagret["aksjer"].items()
        if kursrader
    ]
    return render_template("index.html", rader=rader, hentet=lagret.get("hentet"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
