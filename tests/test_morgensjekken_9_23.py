"""Story 9.23: klokkeslettene fra git i morgensjekken står i norsk tid, også på Windows.

Spørsmål 2 fra 9.22 (svaret 19.11 kl. 09:59) og instruksjonen 19.11 kl. 10:40 i
docs/ai-prompts/2026-11-19.md. På Windows virker ikke TZ i miljøet for git, så
«HEAD paa GitHub» viste UTC lokalt. Skriptet kjøres her med exec, som i
tests/test_morgensjekken_9_22.py, mot et lite repo i en midlertidig mappe, med
TZ satt både til Europe/Oslo, som på GitHub, og til UTC, som gir det samme som
Windows. Begge skal gi norsk tid, også om sommeren.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parent.parent
SKRIPTET = ROT / ".github" / "scripts" / "morgensjekk.py"
BRIEF = "_bmad-output/planning-artifacts/product-brief.md"


def _repo(tmp_path: Path) -> tuple[Path, str, str]:
    """To commits og en tag med faste tider i UTC: briefen 06.10 kl. 20:00, taggen
    v9 kl. 21:01 samme kveld (sommertid, 23:01 i Oslo), og en endring i briefen
    18.11 kl. 20:44 (vintertid, 21:44 i Oslo)."""
    rot = tmp_path / "repo"
    (rot / BRIEF).parent.mkdir(parents=True)
    miljo = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Test Person",
        "GIT_AUTHOR_EMAIL": "test@example.invalid",
        "GIT_COMMITTER_NAME": "Test Person",
        "GIT_COMMITTER_EMAIL": "test@example.invalid",
    }

    def git(*args, dato=None):
        env = dict(miljo, GIT_AUTHOR_DATE=dato, GIT_COMMITTER_DATE=dato) if dato else miljo
        r = subprocess.run(["git", "-C", str(rot), *args], env=env, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        return r.stdout.strip()

    git("init", "-q")
    (rot / BRIEF).write_text("versjon 9\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "Briefen", dato="2026-10-06T20:00:00+00:00")
    foer = git("log", "-1", "--format=%h")
    git("tag", "-a", "arbeidskrav-product-brief-v9", "-m", "v9", dato="2026-10-06T21:01:00+00:00")
    (rot / BRIEF).write_text("versjon 9, endret\n", encoding="utf-8")
    git("commit", "-q", "-am", "Briefen etter taggen", dato="2026-11-18T20:44:00+00:00")
    return rot, foer, git("log", "-1", "--format=%h")


def _kjoer(tmp_path, capsys, monkeypatch, tz: str) -> tuple[list[str], str, str]:
    """Starten, del 1 og del 7, med TZ i miljøet for git satt til tz."""
    rot, foer, etter = _repo(tmp_path)
    kilde = SKRIPTET.read_text(encoding="utf-8")
    assert kilde.count('TZ="Europe/Oslo"') == 1
    kilde = kilde.replace('TZ="Europe/Oslo"', f'TZ="{tz}"')
    monkeypatch.setattr(sys, "argv", [str(SKRIPTET), str(rot), "2026-11-18T22:00"])
    g = {"__name__": "morgensjekk"}
    exec(kilde.split("\n# 2. ", 1)[0], g)
    exec("# 7. " + kilde.split("\n# 7. ", 1)[1].split("\n# 8. ", 1)[0], g)
    return capsys.readouterr().out.splitlines(), foer, etter


@pytest.mark.parametrize("tz", ["Europe/Oslo", "UTC"])
class TestNorskTid:
    def test_head_paa_github(self, tmp_path, capsys, monkeypatch, tz):
        """Ville feilet med TZ=UTC, og på Windows også med TZ=Europe/Oslo: git
        ga 20:44, ikke 21:44."""
        linjer, _, etter = _kjoer(tmp_path, capsys, monkeypatch, tz)
        assert f"HEAD paa GitHub: {etter} 18.11 21:44 Briefen etter taggen" in linjer, linjer

    def test_commitene_siste_doegn(self, tmp_path, capsys, monkeypatch, tz):
        linjer, _, etter = _kjoer(tmp_path, capsys, monkeypatch, tz)
        assert f"  {etter} 18.11 21:44 Test Person: Briefen etter taggen [dok]" in linjer, linjer

    def test_briefen_endret_etter_taggen(self, tmp_path, capsys, monkeypatch, tz):
        linjer, _, etter = _kjoer(tmp_path, capsys, monkeypatch, tz)
        assert (
            f"  MERK: briefen er endret etter arbeidskrav-product-brief-v9: {etter} 18.11 21:44 Briefen etter taggen"
            in linjer
        ), linjer

    def test_taggen_med_sommertid(self, tmp_path, capsys, monkeypatch, tz):
        """Taggen er laget 06.10 kl. 21:01 UTC, som er 23:01 i Oslo om sommeren.
        Ville feilet før 9.23, fordi tiden ble skrevet slik den var lagret."""
        linjer, foer, _ = _kjoer(tmp_path, capsys, monkeypatch, tz)
        assert f"  ny tag: arbeidskrav-product-brief-v9 -> {foer} (2026-10-06 23:01)" in linjer, linjer


def test_skriptet_bruker_ikke_tiden_git_skriver_lokalt():
    """Tidene kommer fra git som sekunder (%at og taggerdate:unix) og regnes om
    med OSLO i Python, så TZ ikke må virke for git."""
    kilde = SKRIPTET.read_text(encoding="utf-8")
    assert "format-local" not in kilde
    assert "%ad" not in kilde
    assert "taggerdate:iso8601" not in kilde
