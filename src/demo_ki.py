"""KI-tekstene i demoen - story 3.4b, FR-411, FR-602-FR-605, AD-8, AD-9.

Demobasen ligger aldri i repoet (AD-9), saa KI-radene for demoen ligger
ferdige i FIL, og demokommandoen skriver dem inn i demobasen. Da viser demoen
KI-teksten uten Ollama og uten nett.

Radene lages én gang med Gemma i Ollama, gjennom den samme veien som
hentingen bruker (lag_ki_tekster i ki_tekst.py: grunnlaget, prompten,
kontrollen og raden), for siste demodag og med klokka satt til den dagen:

    uv run python src/demo_ki.py

Kommandoen lager en demobase uten KI-rader i en midlertidig mappe, og roerer
verken data/db/ose.db eller data/db/demo.db (regel 22). Den kaller ikke
EODHD. Ingen ny runde for aa faa en bedre tekst (FR-604): bestaar en tekst
ikke kontrollen, staar raden som den ble.

Hver rad har et avtrykk av grunnlaget (sha256 av grunnlaget som JSON med
sorterte noekler). Avtrykket viser at grunnlaget ikke er endret i fila, og
testene krever at grunnlaget stemmer med demodagen, saa en endret demo gjoer
testene roede til tekstene lages paa nytt.

Lesingen og skrivingen i demobasen importerer verken requests, ki_lokal
eller ki_tekst. De importeres bare inne i lag_tekstene.
"""

import hashlib
import json
import sqlite3
import sys
import tempfile
import time
from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path

from kilogg import AKSJE, Emne, KIRad
from lagring_sqlite import SqliteKILogg

FIL = Path(__file__).with_name("demo_ki_tekster.json")
FORMAT = 1

# Feltene i KIRad, utenom emnet og grunnlaget, i den rekkefoelgen fila har dem.
FELTENE = (
    "regelen",
    "tekst",
    "besto",
    "grunn",
    "promptversjon",
    "tjeneste",
    "modell",
    "modell_id",
    "seed",
    "temperatur",
    "maskinvare",
    "ollama_versjon",
)


class UgyldigDemoKI(ValueError):
    """Fila med KI-radene kan ikke brukes: feil format, eller et avtrykk som
    ikke stemmer med grunnlaget."""


def avtrykk(rad: KIRad) -> str:
    """sha256 av grunnlaget som JSON med sorterte noekler."""
    return hashlib.sha256(rad.grunnlag_som_json().encode("utf-8")).hexdigest()


def til_json(rad: KIRad) -> dict:
    if rad.emne.slag != AKSJE:
        raise UgyldigDemoKI(f"bare rader for en aksje, fikk {rad.emne.slag!r}")
    return {
        "dato": rad.emne.dato.isoformat(),
        "symbol": rad.emne.symbol,
        "grunnlag": json.loads(rad.grunnlag_som_json()),
        "avtrykk": avtrykk(rad),
        **{felt: getattr(rad, felt) for felt in FELTENE},
    }


def fra_json(verdi: dict) -> KIRad:
    if not isinstance(verdi, dict):
        raise UgyldigDemoKI(f"en rad maa vaere et objekt, fikk {verdi!r}")
    ventet = {"dato", "symbol", "grunnlag", "avtrykk", *FELTENE}
    if set(verdi) != ventet:
        raise UgyldigDemoKI(f"feltene i raden stemmer ikke: {sorted(set(verdi) ^ ventet)}")
    try:
        dato = date.fromisoformat(verdi["dato"])
    except (TypeError, ValueError) as feil:
        raise UgyldigDemoKI(f"datoen kan ikke leses: {verdi['dato']!r}") from feil
    rad = KIRad(emne=Emne.aksje(verdi["symbol"], dato), grunnlag=verdi["grunnlag"], **{f: verdi[f] for f in FELTENE})
    if avtrykk(rad) != verdi["avtrykk"]:
        raise UgyldigDemoKI(f"avtrykket stemmer ikke med grunnlaget for {rad.emne.symbol}")
    return rad


def les_radene(fil: Path = FIL) -> list[KIRad]:
    """Radene i fila, i den rekkefoelgen de ble laget."""
    innhold = json.loads(Path(fil).read_text(encoding="utf-8"))
    if not isinstance(innhold, dict) or innhold.get("format") != FORMAT or not isinstance(innhold.get("radene"), list):
        raise UgyldigDemoKI(f"{Path(fil).name} har ikke format {FORMAT} med en liste radene")
    return [fra_json(verdi) for verdi in innhold["radene"]]


def skriv_radene(tilkobling: sqlite3.Connection, radene: list[KIRad], klokke: Callable[[], datetime]) -> int:
    """Skriver radene i KI-loggen i demobasen, med klokka satt til dagen de
    gjelder (AD-7). Gir hvor mange som ble skrevet."""
    logg = SqliteKILogg(tilkobling, klokke)
    return sum(1 for rad in radene if logg.skriv(rad))


class _MedTid:
    """Modellen, med tiden for hver tekst. Alt annet gaar rett gjennom."""

    def __init__(self, modell):
        self._modell = modell
        self.tider: list[float] = []

    def __getattr__(self, navn):
        return getattr(self._modell, navn)

    def lag_tekst(self, prompt: str):
        start = time.perf_counter()
        try:
            return self._modell.lag_tekst(prompt)
        finally:
            self.tider.append(time.perf_counter() - start)


def lag_tekstene(modell, fil: Path = FIL, skriv: Callable[[str], None] = print) -> list[KIRad]:
    """Lager KI-radene for siste demodag og skriver dem i fil. Gir radene.

    modell er porten i ki_modell.py. Kommandoen gir OllamaModell, og testene
    en falsk. Demobasen lages uten KI-rader i en midlertidig mappe.
    """
    import demo
    from ki_tekst import lag_ki_tekster

    dag = demo.SLUTTDATO
    klokke = demo._klokke_for(dag)
    med_tid = _MedTid(modell)
    with tempfile.TemporaryDirectory() as mappe:
        base = Path(mappe) / "demo.db"
        demo.lag_demobase(base, skriv=lambda _: None)
        lag_ki_tekster(base, dag, klokke, med_tid, skriv, lista=demo.DEMOUNIVERS)
        tilkobling = sqlite3.connect(base)
        try:
            radene = [r for r in SqliteKILogg(tilkobling, klokke).les_alle() if r.emne.dato == dag]
        finally:
            tilkobling.close()
    innhold = {"format": FORMAT, "radene": [til_json(rad) for rad in radene]}
    Path(fil).write_text(json.dumps(innhold, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if med_tid.tider:
        skriv(
            f"{len(radene)} rader i {Path(fil).name}: {sum(r.besto for r in radene)} besto kontrollen. "
            f"Tiden per tekst: {min(med_tid.tider):.1f}-{max(med_tid.tider):.1f} s, "
            f"i alt {sum(med_tid.tider):.1f} s."
        )
    return radene


def main(argv: list[str] | None = None) -> None:
    import argparse

    from ki_lokal import OllamaModell

    argparse.ArgumentParser(
        description="Lager KI-tekstene i demoen med Gemma i Ollama, én gang, i src/demo_ki_tekster.json."
    ).parse_args(argv)
    modell = OllamaModell()
    if grunn := modell.sjekk():
        print(f"Ingen KI-tekster: {grunn}. Fila er ikke endret.")
        sys.exit(1)
    lag_tekstene(modell)


if __name__ == "__main__":
    main()
