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
sorterte noekler). Avtrykket fanger et grunnlag som er endret ved et uhell,
ikke et som er endret med vilje: avtrykket kan regnes paa nytt, og det dekker
ikke teksten (gjennomgangen, BH6 og ECH4). Det som binder radene til demoen,
er testene: grunnlaget maa stemme med demodagen, saa en endret demo gjoer
testene roede til tekstene lages paa nytt, og kontrollen kjoeres paa nytt paa
hver tekst som er merket bestaatt.

Story 10.2g (gruppens svar 25.10 kl. 19:54 og 19:56 c): hver rad har ogsaa
promptens avtrykk, promptavtrykk, ved promptversjonen. Det er sha256 av det
samme som avtrykket for versjonen i testene dekker: reglene, merket og koden
i lag_prompt. Versjonen alene skiller ikke tekster fra to prompter med samme
versjon (VG1, ECH2 og BH13 i 10.2f). les_radene krever feltet, som 64 tegn
i hex, og med prompt=promptavtrykk() avvises en rad med et annet avtrykk.
Testene leser fila slik, saa en endret prompt gjoer testene roede til
tekstene lages paa nytt. Demokommandoen og webserveren sammenligner ikke med
prompten, fordi webserveren ikke importerer ki_prompt (AD-10,
test_webserveren_importerer_ingen_modell i test_ki_visning.py).

Gir kommandoen ikke en hel kjoering, én rad per aksje med vurdering og ingen
der modellen feilet, skrives fila ikke, og den gamle staar. Fila skrives til
en egen fil og byttes inn med os.replace (gjennomgangen, BH4, ECH1 og VG4).

Lesingen og skrivingen i demobasen importerer verken requests, ki_lokal,
ki_tekst eller ki_prompt. De importeres bare inne i lag_tekstene og
promptavtrykk.
"""

import hashlib
import json
import os
import re
import sqlite3
import sys
import tempfile
import time
from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path

from kilogg import AKSJE, Emne, KIRad
from lagring_sqlite import SqliteKILogg, aapne_base

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


_SHA256 = re.compile(r"[0-9a-f]{64}")


def promptavtrykk() -> str:
    """sha256 av prompten slik den er naa: reglene, merket og koden i
    lag_prompt (inspect leser kildeteksten med LF), det samme som avtrykket
    for versjonen i tests/test_ki_modell.py dekker. ki_prompt importeres her,
    ikke oeverst, saa webserveren ikke laster den (AD-10)."""
    import inspect

    import ki_prompt

    tekst = ki_prompt.REGLER + ki_prompt.UTENFOR + inspect.getsource(ki_prompt.lag_prompt)
    return hashlib.sha256(tekst.encode("utf-8")).hexdigest()


def til_json(rad: KIRad, prompt: str) -> dict:
    """Raden slik fila har den. prompt er avtrykket av prompten teksten ble
    laget med, og staar rett etter promptversjonen (gjennomgangen av 10.2g,
    BH1, BH14 og ECH2)."""
    if rad.emne.slag != AKSJE:
        raise UgyldigDemoKI(f"bare rader for en aksje, fikk {rad.emne.slag!r}")
    feltene = {felt: getattr(rad, felt) for felt in FELTENE}
    etter = FELTENE.index("promptversjon") + 1
    return {
        "dato": rad.emne.dato.isoformat(),
        "symbol": rad.emne.symbol,
        "grunnlag": json.loads(rad.grunnlag_som_json()),
        "avtrykk": avtrykk(rad),
        **{felt: feltene[felt] for felt in FELTENE[:etter]},
        "promptavtrykk": prompt,
        **{felt: feltene[felt] for felt in FELTENE[etter:]},
    }


def fra_json(verdi: dict, prompt: str | None = None) -> KIRad:
    """Raden fra fila. Med prompt, avtrykket av prompten, avvises en rad
    laget med en annen prompt (story 10.2g)."""
    if not isinstance(verdi, dict):
        raise UgyldigDemoKI(f"en rad maa vaere et objekt, fikk {verdi!r}")
    ventet = {"dato", "symbol", "grunnlag", "avtrykk", "promptavtrykk", *FELTENE}
    if set(verdi) != ventet:
        raise UgyldigDemoKI(f"feltene i raden stemmer ikke: {sorted(set(verdi) ^ ventet)}")
    try:
        dato = date.fromisoformat(verdi["dato"])
    except (TypeError, ValueError) as feil:
        raise UgyldigDemoKI(f"datoen kan ikke leses: {verdi['dato']!r}") from feil
    rad = KIRad(emne=Emne.aksje(verdi["symbol"], dato), grunnlag=verdi["grunnlag"], **{f: verdi[f] for f in FELTENE})
    if avtrykk(rad) != verdi["avtrykk"]:
        raise UgyldigDemoKI(f"avtrykket stemmer ikke med grunnlaget for {rad.emne.symbol}")
    if not isinstance(verdi["promptavtrykk"], str) or not _SHA256.fullmatch(verdi["promptavtrykk"]):
        raise UgyldigDemoKI(f"promptavtrykket for {rad.emne.symbol} er ikke en sha256: {verdi['promptavtrykk']!r}")
    if prompt is not None and verdi["promptavtrykk"] != prompt:
        raise UgyldigDemoKI(
            f"teksten for {rad.emne.symbol} er laget med en annen prompt enn den i ki_prompt.py "
            "(promptavtrykket stemmer ikke). Lag tekstene paa nytt med uv run python src/demo_ki.py"
        )
    return rad


def les_radene(fil: Path = FIL, prompt: str | None = None) -> list[KIRad]:
    """Radene i fila, i den rekkefoelgen de ble laget. Med prompt avvises en
    rad med et annet avtrykk av prompten (fra_json)."""
    # utf-8-sig, saa en BOM fra en editor ikke stopper demoen (ECH5).
    innhold = json.loads(Path(fil).read_text(encoding="utf-8-sig"))
    format_ = innhold.get("format") if isinstance(innhold, dict) else None
    # type(...) is int, saa true og 1.0 ikke godtas som 1 (ECH5).
    if type(format_) is not int or format_ != FORMAT or not isinstance(innhold.get("radene"), list):
        raise UgyldigDemoKI(f"{Path(fil).name} har ikke format {FORMAT} med en liste radene")
    return [fra_json(verdi, prompt) for verdi in innhold["radene"]]


def sjekk_radene(radene: list[KIRad], dag: date, symboler: set[str]) -> None:
    """Hver rad gjelder dag og en aksje i demoen, og ingen aksje har to.
    Reiser UgyldigDemoKI ellers (gjennomgangen, BH3, ECH3 og ECH5)."""
    sett: set[str] = set()
    for rad in radene:
        if rad.emne.dato != dag:
            raise UgyldigDemoKI(f"raden for {rad.emne.symbol} gjelder {rad.emne.dato}, ikke {dag}")
        if rad.emne.symbol not in symboler:
            raise UgyldigDemoKI(f"{rad.emne.symbol} er ikke en aksje i demoen")
        if rad.emne.symbol in sett:
            raise UgyldigDemoKI(f"{rad.emne.symbol} har to rader")
        sett.add(rad.emne.symbol)


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
    from lagring_sqlite import SqliteVurderingslager
    from vurderingsdata import Vurdering

    dag = demo.SLUTTDATO
    klokke = demo._klokke_for(dag)
    # Avtrykket av prompten foer det foerste kallet, og sjekket igjen etter
    # det siste, saa raden faar prompten teksten ble laget med (BH1).
    prompt = promptavtrykk()
    med_tid = _MedTid(modell)
    with tempfile.TemporaryDirectory() as mappe:
        base = Path(mappe) / "demo.db"
        demo.lag_demobase(base, skriv=lambda _: None, med_ki=False)
        klar = lag_ki_tekster(base, dag, klokke, med_tid, skriv, lista=demo.DEMOUNIVERS)
        tilkobling = aapne_base(base)
        try:
            lager = SqliteVurderingslager(tilkobling, klokke, demo.DEMOUNIVERS)
            ventet = {a.symbol for a in demo.DEMOUNIVERS if isinstance(lager.les(a.symbol, dag), Vurdering)}
            # Bare rader for en aksje paa dagen (gjennomgangen, BH5).
            radene = [
                r for r in SqliteKILogg(tilkobling, klokke).les_alle() if r.emne.dato == dag and r.emne.slag == AKSJE
            ]
        finally:
            tilkobling.close()
    tider = ""
    if med_tid.tider:
        tider = (
            f"Tiden per tekst: {min(med_tid.tider):.1f}-{max(med_tid.tider):.1f} s, i alt {sum(med_tid.tider):.1f} s."
        )
    feilet = [r.emne.symbol for r in radene if r.modellen_feilet]
    if not klar or {r.emne.symbol for r in radene} != ventet or feilet:
        grunn = f"ikke en hel kjoering: {len(radene)} rader av {len(ventet)}"
        if feilet:
            grunn += f", og modellen feilet for {', '.join(feilet)}"
        raise UgyldigDemoKI(f"{grunn}. {Path(fil).name} er ikke endret. {tider}".rstrip())
    if promptavtrykk() != prompt:
        raise UgyldigDemoKI(f"prompten ble endret underveis. {Path(fil).name} er ikke endret.")
    innhold = {"format": FORMAT, "radene": [til_json(rad, prompt) for rad in radene]}
    ny = Path(fil).with_name(Path(fil).name + ".ny")
    ny.write_text(json.dumps(innhold, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(ny, fil)
    skriv(f"{len(radene)} rader i {Path(fil).name}: {sum(r.besto for r in radene)} besto kontrollen. {tider}".rstrip())
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
    try:
        lag_tekstene(modell)
    except UgyldigDemoKI as feil:
        print(f"Ingen nye KI-tekster: {feil}")
        sys.exit(1)


if __name__ == "__main__":
    main()
