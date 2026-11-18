"""Story 9.22: morgensjekken uten falske alarmer.

Instruksjonen 18.11 kl. 21:41 i docs/ai-prompts/2026-11-18.md. Delene av
.github/scripts/morgensjekk.py kjøres med exec, som i
tests/test_ryddighet.py, med en falsk git der delen trenger den, så testene
ikke avhenger av historikken eller taggene i klonen. Verdier som ligner
nøkler, er skrevet i to deler, så morgensjekken ikke finner dem i denne fila.
"""

import re
from datetime import date, datetime, timedelta
from pathlib import Path, PurePosixPath

import pytest

ROT = Path(__file__).resolve().parent.parent
SKRIPTET = ROT / ".github" / "scripts" / "morgensjekk.py"
DAGSFILENE = ROT / "docs" / "ai-prompts"


def _kilde() -> str:
    return SKRIPTET.read_text(encoding="utf-8")


def _del(nr: int) -> str:
    """Koden for del nr, fra «# nr. » til neste del."""
    return "# " + _kilde().split(f"\n# {nr}. ", 1)[1].split(f"\n# {nr + 1}. ", 1)[0]


def _hjelperne() -> dict:
    kilde = _kilde()
    g = {"re": re, "date": date, "IDAG": date(2026, 11, 18)}
    exec(kilde[kilde.index("def utenfor_blokker") : kilde.index("\ndef dato_i")], g)
    return g


def _dagsfil_status() -> dict:
    """Del 2 uten utskriften, så dagsfil_status kan kalles alene."""
    g = _hjelperne()
    exec(_del(2).split('print("\\n== 2 DAGSFILENE")', 1)[0], g)
    return g


def _antall(status):
    ut = {}
    for _, s in status:
        ut[s] = ut.get(s, 0) + 1
    return ut


# Telt for hånd 18.11 kl. 22:00: hver «## »-overskrift utenfor kodeblokkene, og
# om seksjonen har sin egen Utført-linje eller nevnes av en annen.
# - 10.11: 11 overskrifter, ti «## HH:MM, …» og «## 11:20» alene, hver med sin egen
#   «**Utført:**».
# - 16.11: 7. Utført-linja under kl. 11:20 nevner instruksjonen kl. 09:52 og svaret
#   kl. 11:20; de fem andre har sin egen.
# - 17.11: 12. Linja under kl. 13:19 nevner kl. 12:32, 12:41 og 13:19; linja under
#   kl. 14:16 nevner «instruksjonen om rettingene», og linja under kl. 16:21 også;
#   linja under kl. 18:27 nevner «instruksjonen om grensen»; de to linjene under
#   kl. 22:50 nevner kl. 22:18 og 22:50 og «instruksjonen om PRD-en».
# - 18.11 før instruksjonen kl. 21:41: 6. Beskjeden kl. 22:50 17.11 er limt inn på
#   nytt og ikke ført på nytt. Linja under tillegget nevner «instruksjonen kl. 16:03
#   og tillegget». Begge er limt inn kl. 16:03, og tillegget er nevnt med første ord,
#   så klokkeslettet gjelder oppføringen for 16.11.
FOR_HAAND = {
    "2026-11-10.md": (11, {"utført": 11}),
    "2026-11-16.md": (7, {"utført": 7}),
    "2026-11-17.md": (12, {"utført": 12}),
    "2026-11-18.md": (6, {"utført": 5, "limt inn på nytt": 1}),
}
DENNE_INSTRUKSJONEN = "\n## Oppgavene for brukertest 2 og tre små rettinger\n"


def _dagsfila(navn: str) -> str:
    tekst = (DAGSFILENE / navn).read_text(encoding="utf-8")
    return tekst.split(DENNE_INSTRUKSJONEN, 1)[0] if navn == "2026-11-18.md" else tekst


class TestDagsfilene:
    @pytest.mark.parametrize("navn", sorted(FOR_HAAND))
    def test_tallene_stemmer_med_tellingen_for_haand(self, navn):
        """Ville feilet med sjekken før 9.22, som bare kjente «## HH:MM» alene
        og «**Utført:**», og fant 0 instruksjoner fra 11.11."""
        status = _dagsfil_status()["dagsfil_status"](_dagsfila(navn))
        assert (len(status), _antall(status)) == FOR_HAAND[navn], status

    def test_de_fire_utfallene(self):
        """Ville feilet hvis en linje ikke dekket dem den nevner, med
        klokkeslett, «om …» eller et storynummer, hvis en som er limt inn på
        nytt og ikke ført på nytt, trengte Utført, eller hvis noe sjekken ikke
        kan avgjøre, sto som «mangler» i stedet for «uklart». Gjennomgangen av
        9.22: ville også feilet hvis en linje med etikett ga seksjonen den står
        under, Utført når den bare nevner en annen (ECH1), hvis et klokkeslett to
        seksjoner har, dekket begge (ECH2), hvis en dato ble tatt for et
        storynummer eller et vanlig første ord dekket overskriften (ECH3), eller
        hvis «limt inn på nytt» alene var nok (ECH4). En overskrift i en
        kodeblokk teller ikke."""
        tekst = "\n".join(
            [
                "# Instruksjoner",
                "## 10:00, den første",
                "**Utført:** ferdig.",
                "## 11:00, den andre",
                "## 11:05, et tillegg til den andre",
                "**Utført (instruksjonen kl. 11:00 og tillegget kl. 11:05):** ferdig.",
                "## Rettingene i appen",
                "## 12:00, en beskjed",
                "**Utført (beskjeden kl. 12:00, og resten av instruksjonen om rettingene):** ferdig.",
                "## Bildene av appen",
                "## 13:00, beskjeden kl. 09:00, limt inn på nytt",
                "Ordrett lik, og ikke ført på nytt.",
                "## 13:30, beskjeden kl. 10:00, limt inn på nytt",
                "## Story 9.22 på grenen",
                "## 14:00, noe annet",
                "**Utført, 9.22:** ferdig.",
                "## 15:00, kontrollen av lista",
                "**Utført (det meste av bildene):** delvis.",
                "## Oppføringen om A",
                "Limt inn kl. 16:03.",
                "**Utført (instruksjonen kl. 16:03):** ferdig.",
                "## Oppføringen om B",
                "Limt inn kl. 16:03.",
                "## Notatene fra 16.11",
                "## 16:40, svarene om dagen",
                "**Utført, 16.11:** ferdig.",
                "**Utført (om svarene):** ferdig.",
                "## 17:00, en siste",
                "```text",
                "## 17:30, inne i en blokk",
                "**Utført:** teller ikke",
                "```",
            ]
        )
        assert _dagsfil_status()["dagsfil_status"](tekst) == [
            ("10:00, den første", "utført"),
            ("11:00, den andre", "utført"),
            ("11:05, et tillegg til den andre", "utført"),
            ("Rettingene i appen", "utført"),
            ("12:00, en beskjed", "utført"),
            ("Bildene av appen", "uklart"),
            ("13:00, beskjeden kl. 09:00, limt inn på nytt", "limt inn på nytt"),
            ("13:30, beskjeden kl. 10:00, limt inn på nytt", "uklart"),
            ("Story 9.22 på grenen", "utført"),
            # «Utført, 9.22» nevner bare storyen over, og neste seksjon har sin egen linje.
            ("14:00, noe annet", "uklart"),
            ("15:00, kontrollen av lista", "utført"),
            ("Oppføringen om A", "utført"),
            ("Oppføringen om B", "uklart"),
            ("Notatene fra 16.11", "uklart"),
            ("16:40, svarene om dagen", "utført"),
            ("17:00, en siste", "mangler"),
        ]

    def test_en_linje_som_nevner_en_annen_dekker_ikke_der_den_staar(self):
        """Gjennomgangen av 9.22 (ECH1), med dagsfila for 17.11: uten linja
        «**Utført (beskjedene kl. 22:18 og 22:50):**» mangler kl. 22:18 og
        22:50, selv om linja om PRD-en står under kl. 22:50."""
        linjer = _dagsfila("2026-11-17.md").split("\n")
        tekst = "\n".join(l for l in linjer if not l.startswith("**Utført (beskjedene kl. 22:18 og 22:50)"))
        status = _dagsfil_status()["dagsfil_status"](tekst)
        assert [h[:5] for h, s in status if s != "utført"] == ["22:18", "22:50"], status

    def test_utskriften_av_del_2(self, capsys):
        """Ville feilet hvis del 2 skrev «0 instruksjoner» for dagsfilene, som
        før 9.22, eller ikke sa hvilken som mangler."""
        filene = {
            "docs/ai-prompts/2026-11-17.md": _dagsfila("2026-11-17.md"),
            "docs/ai-prompts/2026-11-18.md": _dagsfila("2026-11-18.md") + DENNE_INSTRUKSJONEN + "\nLimt inn.\n",
        }
        g = _hjelperne()
        g.update(IGAAR=date(2026, 11, 17), IDAG=date(2026, 11, 18), les=filene.get, commits=[])
        exec(_del(2), g)
        linjer = [linje.strip() for linje in capsys.readouterr().out.splitlines() if linje.strip()]
        assert linjer[1:] == [
            "docs/ai-prompts/2026-11-17.md: 12 instruksjoner og beskjeder, 12 med Utført",
            "docs/ai-prompts/2026-11-18.md: 7 instruksjoner og beskjeder, 5 med Utført, 1 limt inn på nytt; "
            "mangler Utført: Oppgavene for brukertest 2 og tre små rettinger",
        ], linjer


# Taggene slik «git for-each-ref» viste dem 18.11 kl. 21:59.
TAGGENE = [
    "arbeidskrav-product-brief|c7416ee4|5c7658c9|2026-09-24 21:46:52 +0200",
    "arbeidskrav-product-brief-v2|f08c8017|4454cb8b|2026-09-24 21:58:32 +0200",
    "arbeidskrav-product-brief-v3|783644aa|6b2898f2|2026-09-24 22:54:47 +0200",
    "arbeidskrav-product-brief-v4|85eee2b5|0984a464|2026-09-24 23:07:10 +0200",
    "arbeidskrav-product-brief-v5|16e6f23f|87794b0f|2026-09-24 23:14:08 +0200",
    "arbeidskrav-product-brief-v6|a5c4052f|fd581a8f|2026-09-25 00:27:28 +0200",
    "arbeidskrav-product-brief-v7|e62ea777|4917f989|2026-09-25 00:36:00 +0200",
    "arbeidskrav-product-brief-v8|52023c9a|ce5c2572|2026-10-06 23:01:44 +0200",
]


def _del_7(taggene, capsys) -> list[str]:
    kilde = _kilde()
    kjente = eval(kilde.split("KJENTE_TAGGER = ", 1)[1].split("\n}\n", 1)[0] + "\n}")

    def git(*args):
        return (0, "\n".join(taggene) + "\n") if args[0] == "for-each-ref" else (0, "")

    exec(
        _del(7),
        {
            "re": re,
            "git": git,
            "KJENTE_TAGGER": kjente,
            "BRIEF": "x",
            "BRIEF_FRIST": date(2026, 9, 27),
            "IDAG": date(2026, 11, 18),
        },
    )
    return [linje.strip() for linje in capsys.readouterr().out.splitlines() if linje.strip()]


class TestTaggene:
    def test_v8_er_kjent(self, capsys):
        """Ville feilet hvis v8 (06.10, story 9.6) ble merket som ny tag og som
        en endring etter fristen hver morgen, som før 9.22."""
        linjer = _del_7(TAGGENE, capsys)
        assert not [linje for linje in linjer if "ny tag" in linje or "MERK" in linje], linjer
        assert "briefen er uendret siden arbeidskrav-product-brief-v8 (52023c9)" in linjer

    def test_en_ny_tag_merkes_fortsatt(self, capsys):
        """Ville feilet hvis en ny tag etter fristen ikke ble merket."""
        linjer = _del_7([*TAGGENE, "arbeidskrav-product-brief-v9|1234567a|7654321b|2026-11-19 10:00:00 +0100"], capsys)
        assert "ny tag: arbeidskrav-product-brief-v9 -> 1234567 (2026-11-19 10:00)" in linjer
        assert "MERK: endring etter innleveringsfristen 27.09" in linjer


EODHD = "EODHD_API_KEY" + "="
OPPDIKTET_ANTHROPIC = "sk-ant-" + "api03-oppdiktet0123456789abcdefghij"


class TestLekkasjesjekken:
    def _kjoer(self, tmp_path, capsys, filene: dict, diff: str = "") -> list[str]:
        for sti, innhold in filene.items():
            (tmp_path / sti).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / sti).write_text(innhold, encoding="utf-8")

        def git(*args):
            if args[0] == "ls-files":
                return 0, "\n".join(filene) + "\n"
            return 0, diff

        exec(
            _del(9),
            {"re": re, "git": git, "REPO": tmp_path, "PurePosixPath": PurePosixPath, "FRA": datetime(2026, 11, 18)},
        )
        return [linje.strip() for linje in capsys.readouterr().out.splitlines() if linje.strip()]

    def test_de_kjente_merkes_ikke_men_nye_merkes(self, tmp_path, capsys):
        """Ville feilet hvis de fire kjente .json-filene eller plassholderne i
        testfilene ble merket, som før 9.22, eller hvis en ny .json-fil, en
        ekte verdi i en kjent fil eller en kjent verdi i en annen fil ikke ble
        merket. Unntaket gjelder verdien, ikke linjenummeret."""
        filene = {
            "src/demo_ki_tekster.json": "{}",
            "src/demo_ki_dagen.json": "{}",
            "tests/demo_ki_tekster_versjon_2.json": "{}",
            "docs/bilder/investorsider/bobler.json": "{}",
            "src/static/investorsider/bobler.json": "{}",
            "src/ny.json": "{}",
            "tests/test_ki_tekst.py": f"\n\n{EODHD}hemmelig\n{EODHD}ekte0123456789\n",
            "tests/test_ki_tjenestene.py": f"x = '{OPPDIKTET_ANTHROPIC}'\n",
            "tests/annen.py": f"x = '{OPPDIKTET_ANTHROPIC}'\n",
        }
        diff = "\n".join(
            [
                "@@abc1234",
                "+++ b/tests/test_ki_tekst.py",
                f"+{EODHD}hemmelig",
                f"+{EODHD}nyekte12345",
                "+++ b/tests/annen.py",
                f"+x = '{OPPDIKTET_ANTHROPIC}'",
                "",
            ]
        )
        linjer = self._kjoer(tmp_path, capsys, filene, diff)
        assert [linje for linje in linjer if linje.startswith("FIL:")] == ["FIL: src/ny.json"], linjer
        assert sorted(linje for linje in linjer if linje.startswith("NOEKKEL?:")) == sorted(
            [
                "NOEKKEL?: tests/test_ki_tekst.py:4 (EODHD_API_KEY med verdi)",
                "NOEKKEL?: tests/annen.py:1 (Anthropic-noekkel)",
                "NOEKKEL?: tests/annen.py:1 (OpenAI-noekkel)",
                "NOEKKEL?: commit abc1234, tests/test_ki_tekst.py (EODHD_API_KEY med verdi, lagt til siste doegn)",
                "NOEKKEL?: commit abc1234, tests/annen.py (Anthropic-noekkel, lagt til siste doegn)",
                "NOEKKEL?: commit abc1234, tests/annen.py (OpenAI-noekkel, lagt til siste doegn)",
            ]
        ), linjer

    def test_de_tolv_treffene_i_de_fire_testfilene_er_borte(self, tmp_path, capsys):
        """Gjennomgangen av 9.22 (VG2): ville feilet hvis en av de tolv
        plassholderne i de fire ekte testfilene ble merket, for eksempel
        verdien med anførselstegn foran i test_din_egen_liste_8_22.py, eller
        hvis .json-filene i repoet ble merket."""
        navnene = [
            "tests/test_din_egen_liste_8_22.py",
            "tests/test_ki_tekst.py",
            "tests/test_ki_tjenestene.py",
            "tests/test_snarveien_foer_nettleseren_3_7.py",
            "src/demo_ki_tekster.json",
            "src/demo_ki_dagen.json",
            "tests/demo_ki_tekster_versjon_2.json",
            "docs/bilder/investorsider/bobler.json",
            "src/static/investorsider/bobler.json",
        ]
        filene = {n: (ROT / n).read_text(encoding="utf-8") for n in navnene}
        linjer = self._kjoer(tmp_path, capsys, filene)
        assert linjer[1:] == [f"{len(navnene)} sporede filer; 0 som ikke skal vaere der; 0 mulige noekler"], linjer

    def test_unntakene_finnes_og_har_en_grunn(self):
        """Ville feilet hvis et unntak sto uten grunn, eller pekte på en fil
        eller en verdi som ikke lenger finnes, så lista ble gammel. Fem
        .json-filer, fire nye og den fra 3.4b, og verdiene bak de tolv treffene i
        fire testfiler, 18.11."""
        g = {"re": re}
        kode = _del(9).split('print("\\n== 9 LEKKASJESJEKK")', 1)[0]
        exec(kode, g)
        filene, verdiene = g["KJENTE_FILER"], g["KJENTE_PLASSHOLDERE"]
        assert len(filene) == 5 and len(verdiene) == 7
        assert {f for f, _ in verdiene} == {
            "tests/test_din_egen_liste_8_22.py",
            "tests/test_ki_tekst.py",
            "tests/test_ki_tjenestene.py",
            "tests/test_snarveien_foer_nettleseren_3_7.py",
        }
        for fil, grunn in filene.items():
            assert (ROT / fil).is_file() and len(grunn) > 20, fil
        for (fil, verdi), grunn in verdiene.items():
            assert verdi in (ROT / fil).read_text(encoding="utf-8") and len(grunn) > 20, (fil, verdi)


def _del_10(logg: str, capsys) -> list[str]:
    def git(*args):
        if args[0] == "shortlog":
            return 0, ""
        # Gjennomgangen av 9.22 (VG1): forfatteren med .mailmap (%aN), committeren
        # (%cn), foreldrene og medforfatterne, skilt med tegn som ikke står i navn.
        assert args[0] == "log" and args[-1].startswith("--format="), args
        for felt in ("%h", "%aN", "%cn", "%p", "trailers:key=Co-authored-by,valueonly,separator=%x1d"):
            assert felt in args[-1], (felt, args)
        return 0, logg

    exec(_del(10), {"git": git, "NAA": datetime(2026, 11, 18, 21, 47), "timedelta": timedelta})
    return [linje.strip() for linje in capsys.readouterr().out.splitlines() if linje.strip()]


def _commit(h, forf, committer, foreldre, medforf=""):
    return "\x1e" + "\x1f".join([h, forf, committer, foreldre, medforf]) + "\n"


class TestRegel20:
    def test_bare_gruppens_commits_telles(self, capsys):
        """Ville feilet hvis faglærers commits og merge-commits fra GitHub ble
        telt som commits uten medforfatter, som de 226 av 229 før 9.22, eller
        hvis en commit av Joakim med Marian som medforfatter ikke ble telt."""
        joakim, marian = "Joakim Lund <joakim.lund@himolde.no>", "Marian Osen <marian.osen@himolde.no>"
        logg = "".join(
            [
                _commit("aaaaaaa1", "Marian Osen", "Marian Osen", "p1", f"{joakim}\x1dClaude"),
                _commit("aaaaaaa2", "Joakim Lund", "Joakim Lund", "p2", marian),
                _commit("aaaaaaa3", "Marian Osen", "Marian Osen", "p3"),
                _commit("bbbbbbb1", "Bård Pettersen", "Bård Pettersen", "p4", "Claude"),
                _commit("ccccccc1", "Marian Osen", "GitHub", "p5 p6"),
            ]
        )
        linjer = _del_10(logg, capsys)
        assert linjer[2:] == [
            "regel 20: 3 av gruppens commits, 2 med den andre som medforfatter; uten: aaaaaaa3",
            "utenfor gruppen, for seg (faglaerer og andre): 1 (bbbbbbb1 Bård Pettersen)",
            "merge-commits fra GitHub, for seg: 1 (ccccccc1)",
        ], linjer
