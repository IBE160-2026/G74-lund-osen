"""Markedsoversikten for OSE Signal.

Leser kun fra data/. Denne filen gjoer aldri API-kall, saa en
nettleseroppdatering kan ikke bruke av kvoten. Nye kurser hentes ved
aa kjoere fetch_prices.py.

Alt av regning ligger i markedsoversikt.py og aksjedetalj.py, og de leser
Kursrad gjennom Kursleser (AD-3, AD-19). Denne fila velger bare hvilket
oeyeblikksbilde som skal brukes, pakker det i en SnapshotLeser og sender
resultatet til malen. Tidsstemplene er sist_hentet per symbol fra
Kursleser, i UTC, og blir norsk tid foerst i malen (filteret norsk_tid,
AD-20). Sidens tidsstempel er det eldste blant radene som vises (story 1.4c).
"""

from flask import Flask, abort, render_template

from aksjedetalj import bygg_detalj, finn_aksje
from graf import bygg_graf
from kursdata import AKSJEUNIVERS, Kursleser, SnapshotKilde, SnapshotLeser, nyeste_snapshot
from markedsoversikt import bygg_oversikt, eldre_enn_nyeste, norsk_tid, sidens_tidsstempel

app = Flask(__name__)
app.jinja_env.filters["norsk_tid"] = norsk_tid


def hent_kilde() -> SnapshotKilde | None:
    """Nyeste oeyeblikksbilde i data/, eller None hvis ingen finnes."""
    fil = nyeste_snapshot()
    return SnapshotKilde.fra_fil(fil) if fil else None


def hent_leser() -> Kursleser | None:
    """Kursleseren sidene leser gjennom, eller None hvis ingen data finnes.

    Pakker hent_kilde() i en SnapshotLeser. Egen funksjon, saa en test kan
    montere en hvilken som helst Kursleser, for eksempel et MinneKurslager
    med ulike tider per symbol.
    """
    kilde = hent_kilde()
    return SnapshotLeser(kilde) if kilde is not None else None


@app.route("/")
def markedsoversikt():
    leser = hent_leser()
    if leser is None:
        return render_template("index.html", rader=[], hentet=None, mangler=[], eget=set())

    rader = bygg_oversikt(leser)
    vist = {rad.aksje.symbol for rad in rader}
    mangler = [a.navn for a in AKSJEUNIVERS if a.symbol not in vist]

    return render_template(
        "index.html",
        rader=rader,
        hentet=sidens_tidsstempel(rader),
        eget=eldre_enn_nyeste(rader),
        mangler=mangler,
    )


@app.route("/aksje/<symbol>")
def aksjedetalj(symbol: str):
    """Forklaringsdelen av aksjedetaljen.

    Meldinger, KI-forklaring og kommende hendelser mangler med vilje - de
    krever kilder som ligger bak aapent punkt 1, 3 og 12.
    """
    aksje = finn_aksje(symbol, AKSJEUNIVERS)
    if aksje is None:
        abort(404)

    leser = hent_leser()
    if leser is None:
        abort(404)

    detalj = bygg_detalj(aksje, leser)
    if detalj is None:
        abort(404)

    return render_template(
        "aksje.html",
        detalj=detalj,
        graf=bygg_graf(detalj.punkter),
        hentet=leser.sist_hentet(aksje.symbol),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
