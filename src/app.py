"""Markedsoversikten for OSE Signal.

Leser kun fra data/. Denne filen gjoer aldri API-kall, saa en
nettleseroppdatering kan ikke bruke av kvoten. Nye kurser hentes ved
aa kjoere fetch_prices.py.

Alt av regning ligger i markedsoversikt.py, og all lesing gaar gjennom
Kurskilde. Denne fila velger bare hvilken kilde som skal brukes og sender
resultatet til malen - byttes fila ut med en database i arkitekturfasen, er
det bare linjen under som endres.
"""

from flask import Flask, render_template

from kursdata import AKSJEUNIVERS, SnapshotKilde, nyeste_snapshot
from markedsoversikt import bygg_oversikt

app = Flask(__name__)


def hent_kilde() -> SnapshotKilde | None:
    """Nyeste oeyeblikksbilde i data/, eller None hvis ingen finnes."""
    fil = nyeste_snapshot()
    return SnapshotKilde.fra_fil(fil) if fil else None


@app.route("/")
def markedsoversikt():
    kilde = hent_kilde()
    if kilde is None:
        return render_template("index.html", rader=[], hentet=None, mangler=[])

    rader = bygg_oversikt(kilde)
    vist = {rad.aksje.symbol for rad in rader}
    mangler = [a.navn for a in AKSJEUNIVERS if a.symbol not in vist]

    return render_template(
        "index.html",
        rader=rader,
        hentet=kilde.tidsstempel(),
        mangler=mangler,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
