"""Sjekken foer steg 3 i kveldsjobben - story 2.3d, gruppens svar 05.11
kl. 12:33 og 19:33 (forslag a).

uv run python src/dagen_ferdig.py ser i basen om boersdagen hentingen gjelder
(innevaerende_boersdag fra norsk dato, som kjoer i fetch_prices.py) er ferdig:
hver av de 15 har kurs og rad i vurdering (manglende_i_basen og
manglende_vurderinger, de samme funksjonene som hentingen), hovedindeksen har
raden i indeks, og hver aksje med en vurdering har raden i KI-loggen, slik
lag_ki_tekster regner det. Da starter jobben verken Docker eller Ollama, men
kjoerer hentingen (0 kall) og maalingen som foer.

Basen aapnes bare for lesing (_aapne_for_sjekken). Ingen .env, ingen noekkel
og ingen kall. Kodene er 0 (ferdig, med FERDIG foerst paa linja), 1 (noe
mangler) og 2 (sjekken feilet). Jobben hopper bare over steg 3 paa kode 0
med FERDIG; alt annet gir kjoeringen som foer. Utskriften har symboler og
datoer, aldri tall fra kildene (regel 16).
"""

import sys
from datetime import date, datetime
from pathlib import Path

import lagring_sqlite
from boersdag import innevaerende_boersdag, norsk_dato
from fetch_prices import _aapne_for_sjekken, manglende_i_basen, manglende_vurderinger, naa
from indeksdata import HOVEDINDEKS
from kilogg import Emne
from kursdata import AKSJEUNIVERS, Aksje
from lagring_sqlite import SqliteIndekslager, SqliteKILogg, SqliteVurderingslager
from vurderingsdata import Vurdering

FERDIG = "FERDIG"


def mangler_for_dagen(
    base_sti: Path, oeyeblikk: datetime, lista: tuple[Aksje, ...] = AKSJEUNIVERS
) -> tuple[date, list[str]]:
    """Boersdagen og det som mangler for den. Tom liste betyr ferdig.

    En base som ikke kan aapnes eller leses, gir en feil, ikke en tom liste.
    """
    dato = innevaerende_boersdag(norsk_dato(oeyeblikk))
    if not base_sti.exists():
        return dato, ["basen"]
    mangler = [f"kurs {symbol}" for symbol in manglende_i_basen(base_sti, dato, lista)]
    mangler += [f"vurdering {symbol}" for symbol in manglende_vurderinger(base_sti, dato, lista)]
    tilkobling = _aapne_for_sjekken(base_sti)
    try:
        indeks = SqliteIndekslager(tilkobling).serie(HOVEDINDEKS.symbol)
        if not any(rad.dato == dato for rad in indeks):
            mangler.append(f"indeks {HOVEDINDEKS.symbol}")
        vurderinger = SqliteVurderingslager(tilkobling, lambda: oeyeblikk, lista, godta_en_versjon_bak=True)
        logg = SqliteKILogg(tilkobling, lambda: oeyeblikk)
        for aksje in lista:
            if not isinstance(vurderinger.les(aksje.symbol, dato), Vurdering):
                continue
            if logg.les(Emne.aksje(aksje.symbol, dato)) is None:
                mangler.append(f"KI-tekst {aksje.symbol}")
    finally:
        tilkobling.close()
    return dato, mangler


def main(base_sti: Path | None = None, oeyeblikk: datetime | None = None) -> int:
    try:
        dato, mangler = mangler_for_dagen(base_sti or lagring_sqlite.BASE_STI, oeyeblikk or naa())
    except Exception as feil:
        print(f"Sjekken feilet ({type(feil).__name__}). Kjøringen går som før.")
        return 2
    if mangler:
        print(f"Børsdagen {dato.isoformat()} mangler {len(mangler)}: {', '.join(mangler)}.")
        return 1
    print(
        f"{FERDIG} {dato.isoformat()}: kursene og vurderingene for de {len(AKSJEUNIVERS)}, hovedindeksen og KI-tekstene."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
