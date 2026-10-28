"""Story 3.1: Dockerfile, .dockerignore og compose.yaml.

Testene leser de tre filene som tekst og trenger verken Docker eller nett.
Selve imaget proeves i jobben docker i .github/workflows/tester.yml: ingen
data i imaget, Python 3.13, Oslo-tid, webserveren uten nett og hentingen uten
noekkel. Hvert kontrollpunkt er proevd med en mutant (spesifikasjonen,
Verification).

compose.yaml leses med en liten parser for akkurat denne fila, saa testene
ikke trenger en YAML-pakke. Den kjenner bare innrykk paa to og fire mellomrom
og lister med "- ".
"""

import re
import tomllib
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
DOCKERFILE = ROT / "Dockerfile"
DOCKERIGNORE = ROT / ".dockerignore"
COMPOSE = ROT / "compose.yaml"
CI = ROT / ".github" / "workflows" / "tester.yml"


def _linjer(sti: Path) -> list[str]:
    """Linjene uten kommentarer og tomme linjer, med innrykket."""
    ut = []
    for linje in sti.read_text(encoding="utf-8").splitlines():
        uten = linje.split(" #")[0].rstrip() if not linje.lstrip().startswith("#") else ""
        if uten.strip():
            ut.append(uten)
    return ut


def _instruksjoner() -> list[tuple[str, str]]:
    """Dockerfile som (INSTRUKSJON, resten), med linjer som fortsetter slaatt sammen."""
    samlet, ut = "", []
    for linje in _linjer(DOCKERFILE):
        samlet += linje.strip()
        if samlet.endswith("\\"):
            samlet = samlet[:-1] + " "
            continue
        navn, _, resten = samlet.partition(" ")
        ut.append((navn.upper(), resten.strip()))
        samlet = ""
    # En siste linje som slutter med \ ville ellers forsvunnet uten at noen
    # test saa den (ECH10).
    assert not samlet, f"Dockerfile slutter midt i en instruksjon: {samlet!r}"
    return ut


def _blokk(linjer: list[str], innrykk: int) -> dict[str, list[str]]:
    """Deler linjene i blokker etter noekler med akkurat dette innrykket."""
    blokker: dict[str, list[str]] = {}
    navn = None
    for linje in linjer:
        rom = len(linje) - len(linje.lstrip())
        if rom == innrykk:
            navn = linje.strip().split(":")[0]
            blokker[navn] = [linje]
        elif rom > innrykk and navn is not None:
            blokker[navn].append(linje)
        elif rom < innrykk:
            navn = None
    return blokker


def _toppnivaa() -> dict[str, list[str]]:
    return _blokk(_linjer(COMPOSE), 0)


def _tjenester() -> dict[str, dict[str, list[str]]]:
    tjenester = _blokk(_toppnivaa()["services"][1:], 2)
    return {navn: _blokk(linjer[1:], 4) for navn, linjer in tjenester.items()}


def _apptjenester() -> dict[str, dict[str, list[str]]]:
    """Tjenestene som kjoerer appen fra imaget ose-signal. Story 10.2 la til
    ollama, et ferdig image med sine egne regler (TestOllama)."""
    return {navn: felt for navn, felt in _tjenester().items() if navn != "ollama"}


def _verdier(felt: list[str]) -> list[str]:
    """Verdien til et felt: listepunktene under det, eller verdien paa samme linje."""
    hode = felt[0].split(":", 1)[1].strip()
    punkter = [l.strip()[2:].strip().strip('"') for l in felt[1:] if l.strip().startswith("- ")]
    return punkter or ([hode] if hode else [])


class TestImaget:
    def test_python_er_313_som_ci(self):
        """Ville feilet hvis imaget brukte en annen Python enn CI."""
        fra = [r for i, r in _instruksjoner() if i == "FROM"]
        assert len(fra) == 1
        assert re.fullmatch(r"python:3\.13\.\d+-slim", fra[0]), fra
        assert re.search(r'python-version:\s*"3\.13"', CI.read_text(encoding="utf-8"))

    def test_avhengighetene_kommer_fra_uv_lock_uten_dev(self):
        """Ville feilet hvis imaget installerte pytest, eller ikke krevde at
        uv.lock stemmer."""
        kjoer = " ".join(r for i, r in _instruksjoner() if i == "RUN")
        assert "uv sync --locked --no-dev" in kjoer

    def test_uv_laster_aldri_ned_en_egen_python(self):
        """Ville feilet hvis uv kunne hente en annen Python under byggingen.
        Med python:3.12-slim lastet uv ned 3.13, og imaget kjoerte en Python
        Dockerfile ikke styrer (mutanten I5)."""
        miljoe = " ".join(r for i, r in _instruksjoner() if i == "ENV")
        assert "UV_PYTHON_DOWNLOADS=never" in miljoe

    def test_bare_koden_kopieres(self):
        """Ville feilet hvis hele mappa ble kopiert. Da er .dockerignore eneste
        vakt mot data/ og .env i imaget."""
        kopier = [r for i, r in _instruksjoner() if i == "COPY" and not r.startswith("--from")]
        assert kopier == ["pyproject.toml uv.lock ./", "src/ src/"]

    def test_ingen_noekkel_i_imaget(self):
        """AD-12: noekkelen kommer bare fra miljoeet naar hent kjoeres."""
        for instruksjon, resten in _instruksjoner():
            if instruksjon in ("ENV", "ARG", "LABEL"):
                assert "EODHD" not in resten.upper() and "KEY" not in resten.upper(), resten
        assert ".env" not in " ".join(r for i, r in _instruksjoner() if i in ("COPY", "ADD"))

    def test_ikke_root(self):
        """Ville feilet med USER root, USER 0 eller USER root:root (ECH9)."""
        bruker = [r for i, r in _instruksjoner() if i == "USER"]
        assert bruker and bruker[-1].split(":")[0] not in ("root", "0")

    def test_mappene_til_volumene_eies_av_brukeren(self):
        """Et nytt navngitt volum faar eieren fra mappa i imaget. Ville feilet
        hvis data/raa manglet eller ikke ble eid av ose. Da kunne hent bruke
        dagens kall og saa feile naar oeyeblikksbildet skrives (VG2)."""
        kjoer = " ".join(r for i, r in _instruksjoner() if i == "RUN")
        assert "mkdir -p data/db data/raa" in kjoer
        assert re.search(r"chown -R ose:ose data(\s|$)", kjoer), kjoer
        assert [r for i, r in _instruksjoner() if i == "USER"][-1] == "ose"

    def test_webserveren_er_waitress_uten_debug(self):
        """Svar 1 fra gruppen 08.10: waitress, aldri Flasks egen server og
        aldri debug. Ville feilet med flask run eller app.run."""
        cmd = [r for i, r in _instruksjoner() if i == "CMD"]
        assert len(cmd) == 1
        assert cmd[0] == '["waitress-serve", "--listen=0.0.0.0:8000", "--threads=8", "app:app"]'
        hele = "\n".join(_linjer(DOCKERFILE)).lower()
        assert "flask run" not in hele and "debug" not in hele

    def test_waitress_er_en_avhengighet_ikke_dev(self):
        prosjekt = tomllib.loads((ROT / "pyproject.toml").read_text(encoding="utf-8"))
        assert any(a.startswith("waitress") for a in prosjekt["project"]["dependencies"])

    def test_ingen_migrering_i_eget_steg(self):
        """Ville feilet hvis migrasjonene ble lagt i en egen kommando. Det ville
        sett ut som ryddig ansvarsdeling og brutt suksessmaalet «Drift»
        (story 3.1, 2.1b): begge inngangene migrerer gjennom aapne_base."""
        for instruksjon, resten in _instruksjoner():
            if instruksjon in ("RUN", "CMD", "ENTRYPOINT"):
                assert not re.search(r"migr|aapne_base", resten, re.I), resten
        assert "ENTRYPOINT" not in [i for i, _ in _instruksjoner()]
        # Story 3.3, svar 2: hent har entrypoint. Ingen entrypoint eller
        # command i compose-fila migrerer.
        for navn, felt in _tjenester().items():
            for noekkel in ("entrypoint", "command"):
                linjer = felt.get(noekkel, [f"{noekkel}:"])
                verdi = " ".join([linjer[0].split(":", 1)[1], *linjer[1:]])
                assert not re.search(r"migr|aapne_base", verdi, re.I), (navn, noekkel, verdi)


class TestDockerignore:
    def test_data_noekler_og_lokale_baser_holdes_ute(self):
        """AD-9: ville feilet hvis data/ eller en base kunne komme med."""
        moenstre = set(_linjer(DOCKERIGNORE))
        for krav in ("data/", ".env", ".env.*", "_privat/", ".git", "*.db", "*-raa-*.json"):
            assert krav in moenstre, krav

    def test_filmoenstrene_gjelder_ogsaa_under_src(self):
        """Et moenster uten **/ gjelder bare roten av konteksten, og
        COPY src/ src/ tar med alt under src/. Ville feilet hvis en base,
        en raadatafil eller __pycache__ under src/ kunne komme med (ECH1)."""
        moenstre = set(_linjer(DOCKERIGNORE))
        for krav in (
            "**/.env",
            "**/*.db",
            "**/*-raa-*.json",
            "**/*-raw-*.json",
            "**/raadata-*.json",
            "**/newsweb-*.json",
            "**/__pycache__/",
        ):
            assert krav in moenstre, krav

    def test_env_example_er_unntaket(self):
        moenstre = _linjer(DOCKERIGNORE)
        assert "!.env.example" in moenstre
        assert moenstre.index("!.env.example") > moenstre.index(".env.*")


class TestCompose:
    def test_alle_tjenestene_fra_samme_image(self):
        """Story 3.4 la til demo-lag og demo, fra samme image. Story 10.2 la
        til ollama, fra sitt eget image (TestOllama)."""
        assert set(_tjenester()) == {"app", "hent", "demo-lag", "demo", "ollama"}
        for navn, felt in _apptjenester().items():
            assert _verdier(felt["image"]) == ["ose-signal"], navn

    def test_begge_bygger_fra_repoet_og_henter_aldri_imaget(self):
        """Ville feilet hvis hent manglet build. Da ville docker compose run
        --rm hent paa en ny maskin hentet et image som heter ose-signal fra et
        register, og gitt det .env med noekkelen (BH2, ECH6)."""
        for navn, felt in _apptjenester().items():
            assert _verdier(felt["build"]) == ["."], navn
            assert _verdier(felt["pull_policy"]) == ["build"], navn

    def test_init_som_pid_1(self):
        """Ville feilet uten init. Da venter docker compose stop i 10 sekunder
        og dreper waitress midt i en forespoersel (ECH8)."""
        for navn, felt in _tjenester().items():
            assert _verdier(felt["init"]) == ["true"], navn

    def test_app_er_standard_og_hent_ligger_i_profilen(self):
        """Svar 2 og 3 fra gruppen 08.10: docker compose up starter bare
        webserveren. Ville feilet hvis hent startet med up og brukte kall."""
        tjenester = _tjenester()
        assert "profiles" not in tjenester["app"]
        assert "command" not in tjenester["app"]
        assert tjenester["hent"]["profiles"][0].split(":", 1)[1].strip() == '["hent"]'

    def test_hent_kjoerer_hentekommandoen(self):
        """Hentekommandoen kjoerer hentingen, uten ny kode (svar 2 og 3 i 3.1).
        Story 3.3, svar 2: som entrypoint og uten command, saa flagg legges
        til. Ville feilet med command, der flagget erstatter kommandoen (ECH7)."""
        hent = _tjenester()["hent"]
        assert hent["entrypoint"][0].split(":", 1)[1].strip() == '["python", "src/fetch_prices.py"]'
        assert "command" not in hent

    def test_bare_hent_har_noekkelen(self):
        """Svar 2 og 3: app har ingen noekkel og ingen env_file. hent har .env.
        Ville feilet hvis webserveren fikk noekkelen."""
        tjenester = _tjenester()
        assert "env_file" not in tjenester["app"] and "environment" not in tjenester["app"]
        for navn in ("demo-lag", "demo"):
            assert "env_file" not in tjenester[navn], navn
        assert _verdier(tjenester["hent"]["env_file"]) == [".env"]
        # Story 10.2 (svar 8): bare adressen til Ollama, ingen noekkel.
        assert [l.strip() for l in tjenester["hent"]["environment"][1:]] == ["OSE_KI_OLLAMA_URL: http://ollama:11434"]
        assert "env_file" not in tjenester["ollama"] and "environment" not in tjenester["ollama"]
        assert "EODHD" not in "\n".join(_linjer(COMPOSE)).upper()

    def test_porten_er_den_samme_overalt_og_ikke_5000(self):
        """Story 3.2b (gruppens svar 18.10 kl. 17:40): AirPlay-mottakeren på
        Mac bruker port 5000, så appen bruker 8000. Porten er den samme i
        Dockerfile, compose.yaml (begge tjenestene, inne og ute), app.run i
        src/app.py, CI og README-en. Ville feilet hvis 5000 sto igjen i en av
        dem, eller to av dem sa forskjellige porter.

        Gjennomgangen (BH3, ECH2): ogsaa docs/hjelp.md (svaret 18.10 kl.
        18:58 tok ut setningen om AirPlay). Fra 3.3h har hjelpen ingen
        Rettet-linjer, saa 5000 staar ingen steder i den. Alle port-linjene i
        compose telles (BH5), og adresser med localhost leses ogsaa (BH7)."""
        from urllib.parse import urlsplit

        from ki_lokal import STANDARD_URL

        dockerfile = (ROT / "Dockerfile").read_text(encoding="utf-8")
        compose = COMPOSE.read_text(encoding="utf-8")
        app_py = (ROT / "src" / "app.py").read_text(encoding="utf-8")
        ci = CI.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        hjelp = _hjelp()
        # Adressen til Ollama (STANDARD_URL i ki_lokal.py) er en annen tjeneste (BH6).
        ollama = str(urlsplit(STANDARD_URL).port)
        assert ollama != "8000"

        def adressene(tekst: str) -> list[str]:
            return [p for p in re.findall(r"http://(?:127\.0\.0\.1|localhost):(\d+)", tekst) if p != ollama]

        porter = {
            "EXPOSE": re.findall(r"^EXPOSE (\d+)$", dockerfile, re.MULTILINE),
            "waitress": re.findall(r"--listen=0\.0\.0\.0:(\d+)", dockerfile),
            "app.run": re.findall(r"app\.run\([^)]*port=(\d+)", app_py),
        }
        for tjeneste in ("app", "demo"):
            porter[f"compose {tjeneste}"] = []
            for verdi in _verdier(_tjenester()[tjeneste]["ports"]):
                treff = re.fullmatch(r"127\.0\.0\.1:(\d+):(\d+)", verdi)
                assert treff, (tjeneste, verdi)
                porter[f"compose {tjeneste}"] += list(treff.groups())
        porter["CI"] = adressene(ci)
        porter["README, adressene"] = adressene(readme)
        porter["README, Serving on"] = re.findall(r"Serving on http://0\.0\.0\.0:(\d+)", readme)
        porter["compose, kommentarene"] = adressene(compose)
        porter["hjelp, adressene"] = adressene(hjelp)
        porter["hjelp, Serving on"] = re.findall(r"Serving on http://0\.0\.0\.0:(\d+)", hjelp)
        for sted, funnet in porter.items():
            assert funnet, sted
        alle = {p for funnet in porter.values() for p in funnet}
        assert alle == {"8000"}, porter
        for navn, tekst in (
            ("Dockerfile", dockerfile),
            ("compose.yaml", compose),
            ("src/app.py", app_py),
            ("CI", ci),
            ("README.md", readme),
            ("docs/hjelp.md", hjelp),
        ):
            assert "5000" not in tekst, navn

    def test_porten_er_bare_paa_maskinen(self):
        """Betingelsen fra EODHD 21.09: lokalt, ikke publisert. Ville feilet
        med "8000:8000", som binder til alle adresser."""
        tjenester = _tjenester()
        porter = _verdier(tjenester["app"]["ports"])
        assert porter == ["127.0.0.1:8000:8000"]
        assert "ports" not in tjenester["hent"]
        # Story 3.4: demoen har samme port, saa app og demo kan ikke kjoere samtidig.
        assert _verdier(tjenester["demo"]["ports"]) == porter
        assert "ports" not in tjenester["demo-lag"]

    def test_navngitte_volumer_aldri_data_paa_maskinen(self):
        """Regel 22 og AD-11: ose-db og ose-raa er navngitte og atskilte. Ville
        feilet med ./data:/app/data, som rorer data/db/ose.db."""
        tjenester = _tjenester()
        assert _verdier(tjenester["hent"]["volumes"]) == ["ose-db:/app/data/db", "ose-raa:/app/data/raa"]
        assert _verdier(tjenester["app"]["volumes"]) == ["ose-db:/app/data/db"]
        toppvolumer = _blokk(_toppnivaa()["volumes"][1:], 2)
        assert set(toppvolumer) == {"ose-db", "ose-raa", "ose-demo", "ose-ki-ollama"}
        assert all(len(linjer) == 1 for linjer in toppvolumer.values()), "volumene skal ikke ha name:"

    def test_webserveren_har_ikke_oeyeblikksbildene(self):
        """Svar 1 i 3.2: app leser ikke ose-raa, saa den skal heller ikke kunne
        skrive der. Ville feilet hvis app fikk ose-raa tilbake."""
        assert not any("ose-raa" in v for v in _verdier(_tjenester()["app"]["volumes"]))

    def test_volumene_overlapper_ikke(self):
        """Story 3.2 og AD-11: ett volum over hele data/ tar med seg baade det
        som kan bygges opp igjen og det uerstattelige. Ville feilet med
        ose-data:/app/data, eller med to volumer paa samme mappe."""
        for navn, felt in _apptjenester().items():
            maal = [v.split(":")[1] for v in _verdier(felt["volumes"])]
            assert len(set(maal)) == len(maal), (navn, maal)
            for m in maal:
                assert m.rstrip("/") not in ("/app", "/app/data"), (navn, m)
                assert m.startswith("/app/data/"), (navn, m)
                andre = [a for a in maal if a != m]
                assert not any(a.startswith(m.rstrip("/") + "/") for a in andre), (navn, maal)

    def test_skrivebeskyttet_rot_med_tmp_som_tmpfs(self):
        """Svar 2 i 3.2: bare volumene og /tmp kan skrives. Ville feilet uten
        read_only, eller uten /tmp, som waitress trenger for svar over
        outbuf_overflow."""
        for navn, felt in _apptjenester().items():
            assert _verdier(felt["read_only"]) == ["true"], navn
            assert _verdier(felt["tmpfs"]) == ["/tmp"], navn

    def test_ci_proever_hent_med_de_samme_innstillingene(self):
        """Svar 2 i 3.2: prøven med skrivebeskyttet rot i CI bruker det
        compose.yaml gir hent. Ville feilet hvis compose-fila fikk en annen
        tmpfs, eller CI-steget mistet --read-only eller --tmpfs /tmp."""
        hent = _tjenester()["hent"]
        ci = CI.read_text(encoding="utf-8")
        steg = ci.split("- name: Hentingen med skrivebeskyttet rot", 1)[1].split("- name:", 1)[0]
        kjoeringer = [k for k in steg.split("docker run ")[1:] if "ose-signal:ci" in k]
        assert len(kjoeringer) == 2, len(kjoeringer)
        assert _verdier(hent["read_only"]) == ["true"]
        for kjoering in kjoeringer:
            flagg = kjoering.split("ose-signal:ci", 1)[0]
            assert "--read-only" in flagg
            for monteringspunkt in _verdier(hent["tmpfs"]):
                assert re.search(rf"--tmpfs {re.escape(monteringspunkt)}(\s|$)", flagg), monteringspunkt
            # Hvert volum i compose paa sin egen mappe, med samme navn bak ose-ci-ro-.
            for volum in _verdier(hent["volumes"]):
                navn, maal = volum.split(":")
                del_ = navn.removeprefix("ose-")
                assert re.search(rf"-v ose-ci-ro-{re.escape(del_)}:{re.escape(maal)}(\s|$)", flagg), volum

    def test_advarslene_om_basen_og_down_v(self):
        """Svar 3 i 3.2 og AD-7: «du kan slette basen» er feil raad. Ville
        feilet hvis kommentaren ved ose-db eller advarselen om down -v ble
        fjernet."""
        tekst = COMPOSE.read_text(encoding="utf-8")
        foer_db = tekst.split("\nvolumes:\n", 1)[1].split("\n  ose-db:", 1)[0]
        assert "vurdering" in foer_db and "AD-7" in foer_db
        assert "docker compose down -v" in tekst and "aldri -v" in tekst

    def test_demoen_har_bare_sitt_eget_volum(self):
        """Story 3.4: demoen roerer aldri den ekte basen eller oeyeblikksbildene.
        Ville feilet hvis demo eller demo-lag fikk ose-db eller ose-raa, eller
        ose-demo laa paa en annen mappe enn basen, der demo_sti() peker."""
        import lagring_sqlite

        assert lagring_sqlite.demo_sti().parent == Path(lagring_sqlite.BASE_STI).parent
        tjenester = _tjenester()
        mappe = _verdier(tjenester["app"]["volumes"])[0].split(":")[1]
        assert mappe == "/app/data/db"
        for navn in ("demo-lag", "demo"):
            assert _verdier(tjenester[navn]["volumes"]) == [f"ose-demo:{mappe}"], navn
        for navn in ("app", "hent"):
            assert not any("ose-demo" in v for v in _verdier(tjenester[navn]["volumes"])), navn

    def test_demoen_ligger_i_profilen_og_lager_basen_foerst(self):
        """Story 3.4: docker compose up starter ikke demoen, og demo venter til
        demo-lag har laget demobasen. Ville feilet uten profilen, eller med
        depends_on uten betingelsen, som starter demo foer basen finnes."""
        tjenester = _tjenester()
        for navn in ("demo-lag", "demo"):
            assert tjenester[navn]["profiles"][0].split(":", 1)[1].strip() == '["demo"]', navn
        avhengig = [l.strip() for l in tjenester["demo"]["depends_on"][1:]]
        assert avhengig == ["demo-lag:", "condition: service_completed_successfully"]
        assert "depends_on" not in tjenester["demo-lag"]

    def test_demo_lag_kjoerer_demokommandoen_og_demo_har_bryteren(self):
        """demo-lag kjoerer src/demo.py, og demo er webserveren med OSE_DEMO=1.
        Ville feilet hvis demo ikke hadde bryteren, og viste den ekte basen."""
        import app

        tjenester = _tjenester()
        assert tjenester["demo-lag"]["entrypoint"][0].split(":", 1)[1].strip() == '["python", "src/demo.py"]'
        assert "command" not in tjenester["demo-lag"]
        miljoe = [l.strip() for l in tjenester["demo"]["environment"][1:]]
        assert miljoe == [f'{app.I_DEMO}: "1"']
        assert "entrypoint" not in tjenester["demo"] and "command" not in tjenester["demo"]


class TestOllama:
    """Story 10.2, PR F: Ollama i compose som et eget valg (beslutningen
    05.10 kl. 16:53, svar 1 og 8 kl. 15:53). Erstatter testen fra 3.1 om at
    Ollama ikke var med ennaa."""

    def test_eget_valg_i_profilen_ki(self):
        """Ville feilet hvis docker compose up startet modellen."""
        ollama = _tjenester()["ollama"]
        assert ollama["profiles"][0].split(":", 1)[1].strip() == '["ki"]'

    def test_porten_bare_paa_maskinen(self):
        """Svar 8: porten publiseres bare paa 127.0.0.1."""
        assert _verdier(_tjenester()["ollama"]["ports"]) == ["127.0.0.1:11434:11434"]

    def test_modellen_i_eget_volum_aldri_i_imaget(self):
        """AD-9: modellen ligger i ose-ki-ollama."""
        ollama = _tjenester()["ollama"]
        assert _verdier(ollama["volumes"]) == ["ose-ki-ollama:/root/.ollama"]
        assert "build" not in ollama

    def test_versjonen_er_laast(self):
        """FR-605: Ollama-versjonen foeres i raden. Ville feilet med latest
        eller uten tag, saa versjonen kunne skifte uten at noen visste det."""
        bilde = _verdier(_tjenester()["ollama"]["image"])[0]
        assert re.fullmatch(r"ollama/ollama:\d+\.\d+\.\d+", bilde), bilde

    def test_grafikkortet(self):
        """Svar 1: alltid med grafikkort."""
        tekst = "\n".join(_tjenester()["ollama"]["deploy"])
        assert "driver: nvidia" in tekst and "capabilities: [gpu]" in tekst

    def test_hent_naar_ollama_paa_tjenestenavnet(self):
        miljoe = [l.strip() for l in _tjenester()["hent"]["environment"][1:]]
        assert miljoe == ["OSE_KI_OLLAMA_URL: http://ollama:11434"]

    def test_readme_lover_0_kall_bare_naar_basen_har_kursene(self):
        """Instruksjonen kl. 23:58: README-en sier det samme som utskriften
        fra hentingen, 0 kall bare naar basen har dagens kurs for alle."""
        tekst = README.read_text(encoding="utf-8")
        modell = tekst.split("<summary>Den lokale modellen for KI-teksten (valgfri)</summary>", 1)[1].split(
            "</details>", 1
        )[0]
        assert "uten nye kall til EODHD" not in modell
        assert "Har basen dagens kurs for alle aksjene, gir det 0 kall til EODHD." in modell
        assert (
            "Mangler noen aksjer dagens kurs, gjør samme kommando et nytt forsøk for dem, og det bruker kall." in modell
        )

    def test_ingen_noekkel_i_compose(self):
        """Gjennomgangen (BH7): ingen variabel i compose utenom adressen."""
        tekst = "\n".join(l for l in _linjer(COMPOSE) if not l.lstrip().startswith("#")).upper()
        for ord_ in ("EODHD", "NOEKKEL", "NØKKEL", "KEY", "TOKEN"):
            assert ord_ not in tekst, ord_
        for navn, felt in _tjenester().items():
            miljoe = [l.strip() for l in felt.get("environment", ["environment:"])[1:]]
            assert all(m.split(":", 1)[0] in ("OSE_DEMO", "OSE_KI_OLLAMA_URL") for m in miljoe), (navn, miljoe)


README = ROT / "README.md"
# Spoersmaal og svar til «Kom i gang», flyttet fra README-en 11.10 kl. 22:32.
HJELP = ROT / "docs" / "hjelp.md"


def _hjelp() -> str:
    return HJELP.read_text(encoding="utf-8")


# Story 3.5f (gruppens svar 25.10 kl. 11:32): overskriften har fått
# «nedlasting og installasjon», og ankeret kom-i-gang staar paa linja over.
KOM_I_GANG = "## Kom i gang: nedlasting og installasjon"


def _kom_i_gang() -> str:
    tekst = README.read_text(encoding="utf-8")
    return tekst.split(f"\n{KOM_I_GANG}\n", 1)[1].split("\n## ", 1)[0]


def _blokkene(tekst: str) -> list[tuple[str, str]]:
    """Kodeblokkene i teksten som (spraak, innhold). En blokk uten spraak er
    kommandoer. ```text er det terminalen viser (story 3.4, PR 3)."""
    return re.findall(r"^```(\w*)\n(.*?)^```$", tekst, re.MULTILINE | re.DOTALL)


def _kommandoene() -> list[str]:
    """Hver kommando i kodeblokkene uten spraak i «Kom i gang». Fra PR 3 har
    ingen linje kommentar med #, og testen for det staar for seg."""
    return [l.strip() for spraak, b in _blokkene(_kom_i_gang()) if not spraak for l in b.splitlines() if l.strip()]


class TestReadme:
    """Story 3.3: «Kom i gang» med Docker foerst og uv som alternativ."""

    def test_dockerfile_setter_variabelen_appen_leser(self):
        """Svar 1: ville feilet hvis Dockerfile ikke satte OSE_I_DOCKER=1, saa
        den tomme siden i containeren viste uv-kommandoen."""
        import app

        miljoe = " ".join(r for i, r in _instruksjoner() if i == "ENV")
        assert f"{app.I_DOCKER}=1" in miljoe

    def test_docker_foerst_og_uv_som_alternativ(self):
        """Rettelsen 05.10 og svaret fra hjelpelaereren. Ville feilet hvis uv
        kom foerst, eller en av kommandoene manglet."""
        del_ = _kom_i_gang()
        # Fra 3.4 PR 3 hentes koden med «Download ZIP», ikke git clone (svar 1 11.10).
        for kommando in (
            "«Download ZIP»",
            "cp .env.example .env",
            "docker compose up --build",
            "http://127.0.0.1:8000",
            "docker compose run --rm hent",
            "docker compose down",
        ):
            assert kommando in del_, kommando
        assert del_.index("docker compose up --build") < del_.index("uv run python src/app.py")

    def test_tjenestene_i_readme_finnes_i_compose(self):
        """Ville feilet hvis README-en viste en tjeneste compose.yaml ikke har."""
        # README-en og docs/hjelp.md, der demo-lag staar fra 22:32.
        tekst = README.read_text(encoding="utf-8") + _hjelp()
        # [\w-], saa demo-lag ikke leses som demo (story 3.4).
        brukt = set(re.findall(r"docker compose run --rm ([\w-]+)", tekst))
        brukt |= set(re.findall(r"docker compose up --build ([\w-]+)", tekst))
        assert {"hent", "demo-lag", "demo"} <= brukt
        assert brukt <= set(_tjenester())

    def test_advarselen_om_down_v_og_basen(self):
        """Story 3.2, svar 3, og AD-7: ville feilet hvis README-en ikke advarte
        mot docker compose down -v, eller sa at basen kan slettes."""
        del_ = _kom_i_gang()
        assert "**Skriv aldri `docker compose down -v`.**" in del_
        assert "vurderingene kan ikke lages på nytt" in del_
        # Detaljene om volumene staar i docs/hjelp.md fra 22:32.
        hjelp = _hjelp()
        assert "Bruk aldri `docker compose down -v`" in hjelp
        assert "ose-raa" in hjelp and "ose-db" in hjelp
        assert "Basen kan heller ikke slettes og bygges opp igjen" in hjelp

    def test_raadet_om_tidspunkt_uten_flagget(self):
        """Svar 3: README-en raader til kveld paa en boersdag eller helg, og
        viser ikke flagget som slipper forbi tidskontrollen, som kan laase
        dagen. Fra 19.10 heter det --uten-tidskontroll. Grensen var kl. 21
        19.10 (beslutningen 16.10 kl. 21:09) og er kl. 22 fra 20.10 (gruppens
        svar 19.10 kl. 22:19). Det gamle navnet staar heller ikke. Fra 3.3h
        (gruppens svar 20.10 kl. 16:19) er docs/hjelp.md et levende dokument,
        og svaret «Når kan jeg hente?» sier selv timen fra TIDSGRENSE."""
        import fetch_prices

        tekst = README.read_text(encoding="utf-8")
        for flagg in ("--uten-tidskontroll", "--hent-foer-kl-22"):
            assert flagg not in tekst and flagg not in _hjelp(), flagg
        # Gjennomgangen, BH5 og ECH3: tekstene sier hele timer, saa grensen
        # maa vaere en hel time, og timen staar med ordgrense.
        grense = fetch_prices.TIDSGRENSE
        assert grense.minute == 0
        assert re.search(rf"etter kl\. {grense.hour}\b(?![:.]\d)", _kom_i_gang()) and "helgen" in _hjelp()
        # BH4: bare tidspunktet for hentingen, ikke andre klokkeslett.
        for gammel in (r"etter kl\. 21\b(?![:.]\d)", r"før kl\. 21\b(?![:.]\d)"):
            assert not re.search(gammel, tekst), gammel
        # Gjennomgangen 20.10, BH4 og VG3: hjelpen foelger TIDSGRENSE, og
        # ingen linje i den sier den gamle timen. Story 3.3h: i selve svaret.
        hjelp = _hjelp()
        svar = hjelp.split("### Når kan jeg hente?\n\n", 1)[1].split("\n\n", 1)[0]
        assert svar.startswith(f"Hent etter kl. {grense.hour} og før midnatt på en børsdag."), svar[:80]
        assert f"Før kl. {grense.hour} en børsdag stopper hentingen med 0 kall og sier hvorfor" in svar
        for gammel in (r"etter kl\. 21\b(?![:.]\d)", r"før kl\. 21\b(?![:.]\d)", r"kl\. 21 og 22"):
            assert not re.search(gammel, hjelp), gammel

    def test_du_trenger_versjonene(self):
        """3.3b, punkt e: Docker Desktop slik den er prøvd (spesifikasjonen
        for 3.4, 10.10), Python i imaget fra Dockerfile, at Mac ikke er
        prøvd (svar 3 11.10), og Python for veien uten Docker fra
        pyproject.toml."""
        trenger = [a for a in _kom_i_gang().split("\n\n") if a.startswith("**Du trenger**")]
        assert len(trenger) == 1
        trenger = trenger[0]
        assert "Vi prøvde 10.10 med Docker Desktop 4.91.0 (motor 29.8.0, Compose v5.5.1) på Windows" in trenger
        bilde = re.search(r"python:(\d+\.\d+\.\d+)-slim", (README.parent / "Dockerfile").read_text(encoding="utf-8"))
        assert bilde, "fant ikke python-imaget i Dockerfile"
        assert f"imaget bruker Python {bilde.group(1)}" in trenger
        assert "Mac er ikke prøvd ennå" in trenger
        # uv henter Python, så de to avsnittene sier det samme (BH1, ECH).
        assert f"bare [uv](https://docs.astral.sh/uv/), som henter Python {_python_krav()} eller nyere" in trenger
        assert "«Uten Docker, med uv»" in trenger
        assert f"<summary>{UV_PIL}</summary>" in _kom_i_gang()

    def test_demoen_paa_dagtid_og_helgen_i_steg_8(self):
        """3.3b, punkt d: på dagtid en børsdag er demoen veien for å se appen
        med en gang, og steg 8 og raden «Klar» nevner helgen, slik
        docs/hjelp.md gjør. Ville feilet hvis helgen falt ut av steg 8.

        Story 2.3c (avgjørelsen 21.10 kl. 23:33, U53 og U54): første henting
        går når som helst, og før kl. 22 en børsdag gir den forrige børsdag,
        så demoen er ikke lenger eneste vei på dagtid. Ville feilet hvis
        README-en sa at første henting på dagtid gir dagens kurs, eller at
        man må vente til kvelden."""
        # Story 3.5g: tabellen staar i pila «Demoen og den ekte versjonen».
        # Gruppens svar 28.10 kl. 11:19 og 11:23 (e): tabellen staar oeverst,
        # og avsnittet i pila.
        topp = _seksjon("Demoen og den ekte versjonen") + _tabellen()
        assert "Første gang før kl. 22 henter den forrige børsdag, så du ser kursene og signalet med en gang." in topp
        assert "er demoen veien for å se appen med en gang" not in topp
        klar = [l for l in topp.splitlines() if l.startswith("| Klar |")]
        assert len(klar) == 1 and "når som helst" in klar[0] and "etter kl. 22" in klar[0]
        assert "Før kl. 22 på en børsdag gir den forrige børsdag" in klar[0]
        steg8 = _steg("Den ekte versjonen", 8)
        assert "Første gang går det når som helst; før kl. 22 en børsdag gir den forrige børsdag." in steg8
        assert "når basen er tom, kan du også hente på dagtid og i helgen" in _hjelp()

    def test_demoen_foerst_og_zip_foer_kommandoene(self):
        """Story 3.3c: demoen står foerst, fordi faglaerer proever den (gruppen
        16.10 kl. 21:16, svarene kl. 21:25). Det snur rekkefoelgen fra 11.10
        kl. 22:32. Story 3.3g (svaret 19.10 kl. 14:46): README-en anbefaler
        demoen for faglaerer og sensor. Demoen virker uten .env. Koden hentes med «Download ZIP»
        foer den foerste kommandoen, ikke med git clone (svar 1 11.10). Het
        test_ekte_versjonen_foerst_og_zip_foer_kommandoene fra 11.10 til 3.3c.
        Ville feilet hvis den ekte versjonen kom foer demoen igjen."""
        del_ = _kom_i_gang()
        kommandoer = _kommandoene()
        assert kommandoer[0] == "docker compose up --build demo"
        assert del_.index("«Download ZIP»") < del_.index("docker compose up --build demo")
        overskrifter = re.findall(r"^### (.+)$", del_, re.MULTILINE)
        # Story 3.3h: demoen og den ekte versjonen står bak hver sin pil
        # mellom de felles stegene og «Står du fast?», demoen først. Story
        # 3.5f: dobbeltklikket står foran, og de felles stegene heter «Med
        # Docker Desktop».
        # Story 3.5g (gruppens svar 26.10 kl. 23:00): Docker og «Står du
        # fast?» staar bak hver sin pil, i den rekkefoelgen, og overskriftene
        # er dobbeltklikket og «Mer for den som vil».
        assert overskrifter == [DOBBELTKLIKKET, "Mer for den som vil"], overskrifter
        docker = '<summary><a name="med-docker-desktop"></a>Med Docker Desktop</summary>'
        staar = '<summary><a name="står-du-fast"></a>Står du fast?</summary>'
        assert (
            del_.index(docker)
            < del_.index('<a name="demoen">')
            < del_.index('<a name="den-ekte-versjonen">')
            < del_.index(staar)
        )
        topp = del_.split(docker, 1)[0]
        assert "Vi anbefaler demoen for faglærer og sensor" in topp
        assert "Demoen står først i stegene for Docker og uv, fordi den er raskest." in topp
        assert "git clone" not in del_.split(staar, 1)[0]
        demo = _seksjon("Demoen")
        assert "docker compose up --build demo" in demo and "http://127.0.0.1:8000" in demo
        assert "Eksempeltall" in demo and ".env" not in demo

    def test_kommandoene_er_de_samme_som_i_koden_og_compose(self):
        """Story 3.4, PR 2: kommandoene siden viser, finnes i README-en, og
        flagget og profilen README-en bruker, finnes i koden og compose.yaml.
        Ville feilet hvis en av dem ble endret bare ett sted."""
        import app
        import demo

        tekst = README.read_text(encoding="utf-8")
        # Hele linjer i kodeblokkene, ikke bare tekst et sted (VG3).
        kommandoer = _kommandoene()
        for kommando in (app.HENTEKOMMANDO, app.HENTEKOMMANDO_DOCKER, demo.DEMOKOMMANDO):
            assert kommando in kommandoer, kommando
        # Kommandoen siden viser naar demobasen mangler, staar i docs/hjelp.md fra 22:32.
        assert f"`{demo.DEMOKOMMANDO_DOCKER}`" in _hjelp()
        # demo-lag kjoerer det DEMOKOMMANDO kjoerer, i containeren.
        lag = _tjenester()["demo-lag"]["entrypoint"][0].split(":", 1)[1].strip()
        assert lag == '["' + '", "'.join(demo.DEMOKOMMANDO.split()[2:]) + '"]'
        assert demo.DEMOKOMMANDO_DOCKER == "docker compose run --rm demo-lag"
        # Profilene README-en bruker, finnes i compose.yaml.
        profiler = {
            f[0].split(":", 1)[1].strip().strip('[]"')
            for f in (felt.get("profiles") for felt in _tjenester().values())
            if f
        }
        # Ogsaa docs/hjelp.md, der stoppkommandoen for demoen staar (VG).
        brukt = set(re.findall(r"docker compose --profile ([\w-]+)", tekst + _hjelp()))
        # Story 10.2: profilen ki for Ollama.
        assert brukt == {"demo", "ki"} and brukt <= profiler

    def test_uv_med_demo_flagget_som_appen_leser(self, monkeypatch):
        """uv-veien: README-en viser --demo, og det er flagget les_flagg kjenner."""
        import app

        tekst = _kom_i_gang()
        flagg = re.findall(r"uv run python src/app\.py (--[\w-]+)", tekst)
        assert flagg == ["--demo"]
        # setenv foerst, ellers lekker bryteren til testene etter (som i test_demo.py).
        monkeypatch.setenv(app.I_DEMO, "0")
        app.les_flagg(flagg)
        assert app.demo_paa()
        assert tekst.index("uv run python src/demo.py") < tekst.index("uv run python src/app.py --demo")

    def test_stoppkommandoen_for_demoen(self):
        """Proeven 10.10 med Compose v5.5.1: docker compose down uten profilen
        stopper ikke demoen. Ville feilet hvis README-en ga docker compose
        down som stoppkommando for demoen, eller CI proevde en annen kommando
        enn README-en viser."""
        demo = _seksjon("Demoen")
        bytte = _detaljer(_kom_i_gang())["Bytte mellom demoen og den ekte versjonen"]
        for avsnitt in (demo, bytte):
            assert "docker compose --profile demo down" in avsnitt
        assert "`docker compose down` stopper ikke demoen" in bytte
        steg = CI.read_text(encoding="utf-8").split("- name: Demoen med compose", 1)[1].split("- name:", 1)[0]
        assert "docker compose -f $f --profile demo down\n" in steg
        assert "docker compose -f $f up -d --build demo;" in steg
        # Ikke -p: med -p stopper docker compose down ogsaa demoen (proevd 10.10).
        assert "-p $p" not in steg and "docker compose -f $f down\n" in steg

    def test_tallene_om_demoen_er_de_samme_som_i_koden(self):
        """VG7: ville feilet hvis demo.py fikk en annen sluttdato eller et annet
        antall selskaper uten at README-en ble rettet."""
        import demo

        maaneder = (
            "januar",
            "februar",
            "mars",
            "april",
            "mai",
            "juni",
            "juli",
            "august",
            "september",
            "oktober",
            "november",
            "desember",
        )
        dag = demo.SLUTTDATO
        ukedag = ("mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag")[dag.weekday()]
        # «Hva er demoen?» staar i docs/hjelp.md fra 22:32.
        tekst = _hjelp()
        assert f"{len(demo.DEMOUNIVERS)} oppdiktede selskaper" in tekst
        assert f"til {ukedag} {dag.day}. {maaneder[dag.month - 1]} {dag.year}" in tekst
        assert "`ose-demo`" in tekst and "ose-demo" in _blokk(_toppnivaa()["volumes"][1:], 2)

    def test_readme_proeven_har_hver_kommando(self):
        """VG6: §9 i docs/kvalitetssikring.md sier at lista rettes naar
        README-en endres. Ville feilet hvis en kommando i «Kom i gang» manglet
        i tabellen for README-proeven. Fra PR 3 teller bare radene."""
        import demo

        tabell = _proevetabellen()
        for kommando in [*_kommandoene(), demo.DEMOKOMMANDO_DOCKER]:
            assert f"`{kommando}`" in tabell, kommando

    def test_siden_lastes_paa_nytt_etter_hentingen(self):
        """Story 3.4, PR 2: siden oppdateres ikke av seg selv."""
        assert "Last siden på nytt når hentingen er ferdig" in _steg("Den ekte versjonen", 8)

    def test_testene_uten_docker(self):
        """3.3b, punkt c: hvordan testene kjøres på en ren maskin uten Docker,
        med Python-versjonen fra pyproject.toml, og hva man skal se. Ikke et
        fast testtall, som blir usant ved neste story."""
        tester = README.read_text(encoding="utf-8").split("\n## Tester\n", 1)[1].split("\n## ", 1)[0]
        assert f"Python {_python_krav()} eller nyere" in tester and "`requires-python`" in tester
        # Én rekkefølge: uv sync, så uv run pytest, og ingen annen blokk
        # foran (gjennomgangen, BH2). Story 3.3e (svaret 18.10 kl. 20:39):
        # installasjonen av uv for Windows og Mac kommer foerst.
        blokker = [b.strip() for _, b in _blokkene(tester)]
        assert blokker == [UV_WINDOWS, UV_MAC, "uv sync", "uv run pytest"], blokker
        assert "uten Docker" in tester and "Alle testene skal bestå" in tester
        # Grunnene for det som hoppes over, slik testene sier dem (VG4).
        for grunn in ("time.tzset", "Unix-sokler", "`::1`", "uten git"):
            assert grunn in tester, grunn
        assert "hoppes over" in tester and "Windows" in tester
        # Ikke et fast testtall (gjennomgangen, BH3, VG3).
        assert not re.search(r"\b\d+\s+(tester|testene|hoppes|hoppet|består|bestått|passed|skipped)\b", tester)
        assert not re.search(r"\b(alle|de)\s+\d+\b", tester, re.IGNORECASE)

    def test_forklaringen_i_tester_staar_bak_en_knapp(self):
        """Story 3.3d, punkt d: kommandoene, «Alle testene skal bestå»,
        punktene og setningen om kvalitetssikringen står synlig, og
        forklaringen om testene som hoppes over, står bak knappen «Hvorfor
        hoppes noen over?», som de andre knappene. Ville feilet hvis
        forklaringen sto utenfor knappen."""
        tester = README.read_text(encoding="utf-8").split("\n## Tester\n", 1)[1].split("\n## ", 1)[0]
        knapper = _detaljer(tester)
        # Story 3.3h: installasjonen av uv staar bak sin egen pil, foerst.
        assert list(knapper) == [UV_PILA, "Hvorfor hoppes noen over?"], list(knapper)
        forklaring = knapper["Hvorfor hoppes noen over?"]
        synlig = re.sub(r"<details>.*?</details>", "", tester, flags=re.DOTALL)
        for grunn in ("time.tzset", "Unix-sokler", "`::1`", "uten git", "`-rs`"):
            assert grunn in forklaring and grunn not in synlig, grunn
        assert "Alle testene skal bestå." in synlig
        assert [b.strip() for _, b in _blokkene(synlig)] == ["uv sync", "uv run pytest"]
        assert "- Ingen nettkall:" in synlig and "- CI kjører" in synlig
        assert "](docs/kvalitetssikring.md)" in synlig
        # Gjennomgangen, BH10 og ECH7: indeksene i samme tekst, og knappen
        # rett etter «Alle testene skal bestå», foer punktene.
        hvorfor = tester.index("<details>\n<summary>Hvorfor hoppes noen over?</summary>")
        assert tester.index("uv run pytest") < tester.index("Alle testene skal bestå.") < hvorfor
        assert tester.rindex("</details>") < tester.index("\n- Ingen nettkall:")
        # 21.10: en kort innledning foer punktene, saa de ikke ser ut som
        # svaret i pila «Hvorfor hoppes noen over?». Ville feilet hvis
        # punktene kom rett etter </details>.
        assert "\n</details>\n\nSlik er testene satt opp:\n\n- Ingen nettkall:" in tester
        assert "Alle testene skal bestå. Noen hoppes over, og knappen under sier hvorfor.\n\n<details>" in tester
        assert not _blokkene(forklaring), forklaring

    def test_bildene_er_de_tre_fra_gjennomgangen_og_ci_merket(self):
        """Story 3.3: skjermbilder med ekte data publiserer dataene. Regelen
        står i dokumentene: bilder i README-en kommer bare fra
        docs/bilder/readme/ og viser aldri den ekte versjonen (svar 4 11.10,
        regelen 25.09 under story 3.3).

        Story 3.3c (instruksjonen 18.10 kl. 12:23): de tre skjermbildene fra
        gruppens gjennomgang 16.10 står i steg 1, 2 og 4, hvert med alt-tekst
        og en kort tekst under, og CI-merket står øverst (utsatt fra PR #54).
        Ingen av dem viser appen. Story 3.3e: og bildet av oversikten i demoen
        under «Til faglærer», som viser demoen, aldri den ekte versjonen.
        Ville feilet med et bilde til, et bilde uten alt-tekst eller utenfor
        docs/bilder/readme/, eller uten CI-merket.

        Story 3.3f (gruppens svar 18.10 kl. 23:03): bildene av appen, av
        oversikten og aksjesiden i demoen, ligger i docs/appen/ og står i
        knappen «Bilder av appen (demoen)», ikke under «Til faglærer»."""
        tekst = README.read_text(encoding="utf-8")
        bilder = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", tekst)
        merket = [b for _, b in bilder if b.endswith("/actions/workflows/tester.yml/badge.svg")]
        assert merket == ["https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml/badge.svg"]
        andre = [(alt, b) for alt, b in bilder if b not in merket]
        # Story 3.3e: og bildet av oversikten under «Til faglærer».
        assert sorted(b for _, b in andre) == sorted(
            [*(f"docs/bilder/readme/{navn}" for navn in BILDENE.values()), SKJERMBILDET, AKSJESIDEBILDET]
        )
        for alt, sti in andre:
            assert alt.strip(), sti
            assert (ROT / sti).is_file(), sti
        # Hvert bilde i sitt steg i «Felles for begge».
        for nummer, navn in BILDENE.items():
            assert f"](docs/bilder/readme/{navn})" in _steg("Med Docker Desktop", nummer), navn
        # Ogsaa HTML-bilder og bilder med referanse (BH7).
        assert "<img" not in tekst.lower()
        assert not re.search(r"!\[[^\]]*\]\[", tekst)

    def test_teksten_under_hvert_bilde(self):
        """Svar 2 kl. 14:48: teksten under et bilde telles for seg, høyst 25
        ord. Under bildet i steg 4 står at stien blir en annen, men at
        mappenavnet skal stå foran >. Ville feilet hvis et bilde sto uten
        tekst under, eller teksten ble for lang.

        Story 3.5f: ordene telles slik leseren ser dem, med lenketeksten og
        uten adressen bak, som i stegene (svaret 13.10 kl. 23:50). Teksten
        under bildet i steg 2 har den direkte lenken til ZIP-fila."""
        for nummer, navn in BILDENE.items():
            under = _bildetekst(_steg("Med Docker Desktop", nummer), navn)
            assert under, navn
            assert len(re.findall(r"\w+", re.sub(r"\]\([^)]*\)", "]", under))) <= 25, (navn, under)
        assert "Stien blir en annen hos deg, men mappenavnet skal stå foran `>` (`%` på Mac)." in _bildetekst(
            _steg("Med Docker Desktop", 4), BILDENE[4]
        )

    def test_mappestrukturen_nevner_bildene(self):
        """Regel 19: «Mappestruktur» nevner docs/bilder/readme/ og hvert bilde."""
        mappestruktur = README.read_text(encoding="utf-8").split("\n## Mappestruktur\n", 1)[1].split("\n## ", 1)[0]
        assert "`docs/bilder/readme/`" in mappestruktur
        for navn in BILDENE.values():
            assert f"`{navn}`" in mappestruktur, navn
        # Story 3.3e (gjennomgangen, VG4): og bildet av oversikten.
        assert f"`{SKJERMBILDET.rsplit('/', 1)[1]}`" in mappestruktur
        # Story 3.3f (gjennomgangen, VG3 og ECH7): docs/appen/ og begge bildene
        # av appen, i punktet for mappa.
        punkt = next(l for l in mappestruktur.splitlines() if l.startswith("- [`docs/appen/`](docs/appen/)"))
        for sti in (SKJERMBILDET, AKSJESIDEBILDET):
            assert f"[`{sti.rsplit('/', 1)[1]}`]({sti})" in punkt, sti


BILDEFILER = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
# Story 3.3c: skjermbildene fra gruppens gjennomgang 16.10, per steg i
# «Felles for begge».
BILDENE = {1: "engine-running.png", 2: "github-download-zip.png", 4: "powershell-mappa.png"}
# Story 3.4 (godkjent 24.10 kl. 13:43): én tegning og én forhåndsvisning per
# oppdiktet selskap i docs/bilder/investorsider/.
INVESTORSIDENE = (
    "blgt",
    "brfe",
    "fjsb",
    "hvdo",
    "jgrd",
    "kvst",
    "lksv",
    "lstf",
    "mtfj",
    "nlys",
    "sgnt",
    "slvp",
    "trhf",
    "troy",
    "vrds",
)

# Story 3.3e (gruppens svar 18.10 kl. 00:20): bildet av oversikten i demoen,
# tatt etter «Bildet» i spesifikasjonen 3.3b. Filene under bestemmer det
# bildet viser: malene oversikten bygges av, med stilarket (foer 2.7a i <style> i
# _ramme.html), skriftene i src/static/, demodataene og modulene som lager
# tallene og tekstene. Endres en av dem, tas bildet paa nytt og avtrykket
# oppdateres i samme commit (spesifikasjonen 3.3e, «Avgjort»).
# Story 3.3f (gruppens svar 18.10 kl. 23:03): i docs/appen/, mappa for bilder
# og video av appen, bare av demoen.
# Story 2.7a: stilarket staar i src/static/stil.css, ikke i <style> i
# _ramme.html. Det er med i begge avtrykkene, fordi .css er med i
# SKRIFTFILER. Bildene ble tatt paa nytt og var like byte for byte.
SKJERMBILDET = "docs/appen/oversikten-demo.png"
# Story 3.3e (svaret 18.10 kl. 20:39): installasjonen av uv i «Tester», fra
# https://docs.astral.sh/uv/getting-started/installation/.
UV_WINDOWS = 'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
UV_MAC = "curl -LsSf https://astral.sh/uv/install.sh | sh"
# Story 3.3h: pila under «Tester» med installasjonen av uv og tipset.
UV_PILA = "Installere uv, og når uv ikke blir funnet"
# Gjennomgangen av 3.3e (BH6, VG1, ECH1-ECH3): ogsaa signalberegningen,
# hjelpetekstene, boersdagene, indeksen og aksjene demoen bygges av, og hver
# delmal (_*.html), saa en ny delmal kommer med. Fra src/static/ bare
# skriftene, ikke OFL.txt eller filer Windows legger der. Merket
# «Eksempeltall» i app.py er med som tekst, ikke hele app.py.
MALENE_BAK_BILDET = (
    "src/demo.py",
    "src/markedsoversikt.py",
    "src/oversiktsdata.py",
    "src/hovedindeks.py",
    "src/tallformat.py",
    "src/signalberegning.py",
    "src/hjelpetekster.py",
    "src/boersdag.py",
    "src/indeksdata.py",
    "src/kursdata.py",
    "src/templates/index.html",
)
# Story 8.0f: ogsaa hjelpeskriptet (.js), som lastes paa begge sidene.
SKRIFTFILER = {".woff", ".woff2", ".ttf", ".otf", ".css", ".js"}
# Svaret 18.10 kl. 21:42: bildet er saa hoeyt at det slutter etter den siste
# raden under «Skilte seg ut», foer «Øvrige aksjer», saa signalstyrken og
# fargene per aksje er med.
# Story 8.3: 1630, fordi knapperaden i stripa skyver tabellen ned. Var 1573.
HOEYDE_PAA_BILDET = 1630
# Story 2.3, kl. 22 fra 20.10: stripa sier kl. 22.15 igjen, ikke 21.15.
# Story 10.5: investorsidene i kursdata.py. Bildet ble tatt på nytt og er
# byte for byte det samme. Avtrykket er av kildefilene, ikke av PNG-en.
# Story 2.7b: hjelpen til Sluttkurs og historikken i hjelpetekster.py. Bildet
# ble tatt på nytt og er byte for byte det samme.
# Story 3.3i (U51): lenken til den ekte versjonen i demolinja i _ramme.html,
# og fargen paa den i stil.css. Bildet ble tatt paa nytt, med samme hoeyde,
# fordi linja fortsatt er én linje i 1280 px.
# Story 3.4c: vurderingene i demo.py fra STARTDAG, og meldingen om en demobase
# fra foer i index.html. Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 2.3c: forrige_boersdag i boersdag.py. Bildet ble tatt paa nytt og
# er byte for byte det samme. Ogsaa etter gjennomgangen av 2.3c (VG11).
# Flettingen av main inn i grenen for 2.3c (22.10 kl. 23:30): kildene fra 3.4c
# og 2.3c sammen, saa avtrykket er regnet paa nytt (instruksjonen kl. 23:29).
# Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.6: knappen «Børsometer» i stripa, hovedindeksen flyttet til delmalen
# _hovedindeks.html og hjelpen til børsometeret. Bildet ble tatt paa nytt med
# samme hoeyde, og viser den nye knappen.
# Testene for 8.6 b: en aksje uten kurser har ingen lenke i børsometeret,
# i stil.css. Bildet ble tatt paa nytt og er byte for byte det samme.
# Gjennomgangen av 8.6: rammen, lenkene og hjelpen til børsometeret, og
# teksten om en hovedindeks som ikke kan leses i _hovedindeks.html. Bildet
# ble tatt paa nytt og er byte for byte det samme.
# Gruppens svar 23.10 kl. 09:24 (a): gult i børsometeret en dag uten
# vurdering, i hjelpetekster.py. Bildet ble tatt på nytt og er byte for byte det samme.
# Gruppens svar 23.10 kl. 09:24 (b): aksjesiden for en aksje uten kurser, og
# lenkene dit. Bildet ble tatt på nytt og er byte for byte det samme.
# Story 3.4d: fotnoten for «ikke vurdert» i index.html. Bildet er byte for byte det samme.
# Flettingen av main inn i grenen for 3.4d (23.10): kildene fra 8.6 og 3.4d
# sammen, saa avtrykket er regnet paa nytt. Bildet ble tatt paa nytt og er byte
# for byte det samme.
# Story 3.4d b: fotnoten for «ikke vurdert» i delmalen _fotnote_ikke_vurdert.html,
# med den ekte teksten fra 22.10 kl. 23:19. Bildet ble tatt paa nytt og er byte
# for byte det samme.
# Story 3.4e a: demoteksten i fotnoten bare før STARTDAG, i app.py og
# _fotnote_ikke_vurdert.html. Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 3.4e b: setningen om i dag i fotnoten, i app.py og
# _fotnote_ikke_vurdert.html. Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 3.4e a etter svaret 23.10 kl. 19:10: setningen i fotnoten for inneværende
# børsdag, i app.py og _fotnote_ikke_vurdert.html. Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.2a a: ankeret ved kursgrafen i delmalen _perioder.html. Bildet ble
# tatt paa nytt og er byte for byte det samme.
# Story 8.2a b: raden uten data i index.html og markedsoversikt.py, og
# hjelpeteksten i hjelpetekster.py. Bildet ble tatt paa nytt og er byte for byte
# det samme, fordi raden staar under «Øvrige aksjer».
# Story 8.2a c: symbolene over søylene er lenker, i _hovedindeks.html, stil.css
# og hjelpetekster.py. Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.2a d: grunnen med tall i markedsoversikt.py og hjelpetekster.py.
# Bildet ble tatt paa nytt med samme hoeyde. Det er ikke byte for byte det
# samme, men viser de samme radene og tallene.
# Story 8.2a e: én liste når man sorterer, i index.html og markedsoversikt.py.
# Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.2a f: linja om 3 av 3 uten «Bare» i index.html. Bildet ble tatt paa
# nytt med samme hoeyde, og viser linja uten ordet.
# Gjennomgangen av 8.2a 24.10: båndet, sorteringen, kommentaren i
# _hovedindeks.html og hjelpeteksten. Bildet ble tatt paa nytt og er byte for
# byte det samme.
# Story 3.5d b: æ, ø og å i meldingene fra demo.py. Bildet ble tatt paa nytt
# og er byte for byte det samme.
# Story 10.2e: valgt_indeks flyttet fra app.py til hovedindeks.py. Bildet ble
# tatt paa nytt og er byte for byte det samme.
# Story 8.6b b: linja «Mål mot børsen» i stil.css og hjelpetekster.py, og
# _hovedindeks.html bare paa oversikten. Bildet ble tatt paa nytt og er byte
# for byte det samme.
# Story 8.6b c: fargetrinnene og rammene i stil.css, og hjelpen i
# hjelpetekster.py. Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.6b d: kartet i stil.css og hjelpen i hjelpetekster.py. Bildet ble
# tatt paa nytt og er byte for byte det samme.
# Story 8.6b, svaret 26.10 kl. 13:00 (a): rekkefoelgen i kartet og hjelpen i
# hjelpetekster.py. Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.6b, svaret 26.10 kl. 13:00 (b): overskriften i feltet i stil.css og
# hjelpen i hjelpetekster.py. Bildet ble tatt paa nytt og er byte for byte det
# samme.
# Story 8.6b, svarene 26.10 kl. 13:00 (c) og 13:07 (e): tekstnivået i stil.css.
# Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.6b, svaret 26.10 kl. 15:21 (f): tabellen bak «Se tallene som tabell»
# i stil.css og hjelpen i hjelpetekster.py. Bildet ble tatt paa nytt og er byte
# for byte det samme.
# Gjennomgangen av 8.6b 26.10 (BH, ECH): tekstnivået med @container i stil.css.
# Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.0f: hjelpeskriptet, lenken i _ramme.html og feltet i stil.css.
# Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.0f, b: knappen som flytter feltet. Bildet ble tatt paa nytt og er
# byte for byte det samme.
# Gjennomgangen av 8.0f: grensen 1056 px og rettelsene i hjelp.js. Bildet
# ble tatt paa nytt og er byte for byte det samme.
AVTRYKK_BAK_BILDET = "661c42525c0f38a92933edb7e847f93dc86f41518320fd3898f3d273e04d3b56"
SLIK_TAS_BILDET = (
    "Oversikten er endret, så skjermbildet viser noe annet enn demoen. Ta "
    f"{SKJERMBILDET} på nytt etter «Bildet» i spesifikasjonen 3.3b: demobasen i en "
    "midlertidig mappe (lagring_sqlite.BASE_STI dit), OSE_DEMO=1, waitress på en "
    "ledig port, og msedge --headless --disable-gpu --hide-scrollbars "
    f"--window-size=1280,{HOEYDE_PAA_BILDET} med egen --user-data-dir. Bildet skal slutte "
    "etter den siste raden under «Skilte seg ut», før «Øvrige aksjer»: mål bunnen av "
    "den raden og endre HOEYDE_PAA_BILDET hvis den har flyttet seg. Oppdater så "
    "AVTRYKK_BAK_BILDET til {avtrykk} i samme commit."
)

# Story 3.3f (gruppens svar 18.10 kl. 23:03): aksjesiden for KVST i demoen,
# med grafen og KI-teksten, tatt med samme fremgangsmaate som oversikten.
# Filene under bestemmer det bildet viser: malen og delmalene, skriftene,
# demodataene med KI-tekstene, og modulene som lager tallene, grafen og
# tekstene. Hele app.py er med, fordi ruta bygger siden der.
# Story 10.2e, gruppens svar 24.10 kl. 23:23 (b): teksten for KVST ble stoppet
# igjen, saa bildet viser BRFE, en demoaksje der KI-teksten besto. Var KVST.
AKSJESIDEBILDET = "docs/appen/aksjesiden-brfe-demo.png"
FILENE_BAK_AKSJESIDEN = (
    "src/app.py",
    "src/aksjedetalj.py",
    "src/graf.py",
    "src/perioder.py",
    "src/ki_visning.py",
    "src/kilogg.py",
    "src/demo.py",
    "src/demo_ki.py",
    "src/demo_ki_tekster.json",
    "src/markedsoversikt.py",
    "src/oversiktsdata.py",
    "src/hovedindeks.py",
    "src/indeksdata.py",
    "src/tallformat.py",
    "src/signalberegning.py",
    "src/hjelpetekster.py",
    "src/boersdag.py",
    "src/kursdata.py",
    "src/tilstand.py",
    "src/vurderingsdata.py",
    # Story 2.7b: historikken nederst paa aksjesiden.
    "src/historikk.py",
    # Story 10.2e (svaret 25.10 kl. 00:51): setningen om dagene under KI-teksten.
    "src/dagene.py",
    "src/templates/aksje.html",
    # Gjennomgangen (BH1, ECH1): lagringslaget som leser det siden viser, og
    # skjemaet demobasen lages med.
    "src/lagring_sqlite.py",
    "src/migrering.py",
    # Story 8.3: porten for Min liste, som lagring_sqlite importerer.
    "src/minliste.py",
    *sorted(p.relative_to(ROT).as_posix() for p in (ROT / "src" / "migrasjoner").glob("*.sql")),
)
# Moduler appen og demoen importerer, men som ikke lager noe aksjesiden viser:
# lagring_sqlite henter DATA_KATALOG fra lagring_fil, som importerer eodhd.
# Story 8.6: boersometer.py bygger bare børsometeret.
IKKE_BAK_AKSJESIDEN = {"src/lagring_fil.py", "src/eodhd.py", "src/boersometer.py"}
# Bildet er saa hoeyt at grafen, som staar under KI-teksten, er med til bunnen.
# Story 8.3: 1872 med knapperaden i stripa. Var 1816.
# Story 10.2e, rettingen etter gruppens svar 24.10 kl. 21:49: teksten for KVST
# ble stoppet av kontrollen, og feltet sier at den ikke ble vist. Grafen
# slutter da ved 1827, maalt i Edge uten vindu. Var 1872.
# Story 10.2e, gruppens svar 24.10 kl. 23:23: bildet viser BRFE med KI-teksten,
# og grafen slutter ved 1872, maalt i Edge uten vindu. Var 1827.
# Story 10.2e, gruppens svar 25.10 kl. 00:51: setningen om dagene under
# KI-teksten, og en lengre tekst for BRFE. Grafen slutter ved 1934. Var 1872.
# Story 10.2g, gruppens svar 25.10 kl. 19:54 og 19:56: en kortere tekst for
# BRFE. Grafen slutter ved 1894, maalt i Edge uten vindu. Var 1934.
HOEYDE_PAA_AKSJESIDEN = 1894
# Story 2.3, kl. 22 fra 20.10: stripa sier kl. 22.15 igjen, ikke 21.15.
# Story 10.5: lenken til investorsiden står under grafen, ved 1980 px målt i
# Edge uten vindu, så bildet, som slutter ved bunnen av grafen (1872 px), ble
# byte for byte det samme da det ble tatt på nytt. Avtrykket er sha256 av
# kildefilene bak bildet, ikke av PNG-en, så det er nytt (gjennomgangen, BH11).
# Story 2.7b: historikken står nederst, under avsnittet om investorsiden, og
# bildet ble byte for byte det samme da det ble tatt på nytt.
# Story 3.3i (U51): lenken i demolinja. Bildet ble tatt på nytt, med samme
# høyde, fordi grafen slutter på samme sted.
# Story 3.4c: vurderingene i demo.py fra STARTDAG, og meldingen om en demobase
# fra før i app.py. Bildet ble tatt på nytt og er byte for byte det samme.
# Gjennomgangen av 3.4c (BH1): sjekken av en gammel demobase ogsaa der den ekte
# skal ligge, i app.py. Bildet er byte for byte det samme.
# Story 2.3c: forrige_boersdag i boersdag.py og foerste_dag i lagrene i
# lagring_sqlite.py. Bildet ble tatt på nytt og er byte for byte det samme.
# Også etter gjennomgangen av 2.3c (BH4, VG11).
# Flettingen av main inn i grenen for 2.3c (22.10 kl. 23:30): kildene fra 3.4c
# og 2.3c sammen, saa avtrykket er regnet paa nytt (instruksjonen kl. 23:29).
# Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.6: knappen «Børsometer» i stripa, og ruta og hjelpen til
# børsometeret i app.py og hjelpetekster.py. Bildet ble tatt på nytt med
# samme høyde, og viser den nye knappen.
# Testene for 8.6 b: en aksje uten kurser har ingen lenke i børsometeret,
# i app.py. Bildet ble tatt på nytt og er byte for byte det samme.
# Gjennomgangen av 8.6: ruta for børsometeret i app.py og hjelpen i
# hjelpetekster.py. Bildet ble tatt på nytt og er byte for byte det samme.
# Gruppens svar 23.10 kl. 09:24 (a): gult i børsometeret en dag uten
# vurdering, i hjelpetekster.py. Bildet ble tatt på nytt og er byte for byte det samme.
# Gruppens svar 23.10 kl. 09:24 (b): aksjesiden for en aksje uten kurser, og
# lenkene dit. Bildet ble tatt på nytt og er byte for byte det samme.
# Gjennomgangen 23.10: gult fra sidens siste børsdag (ECH1) og kommentarene om
# aksjesiden uten kurser i app.py. Bildet ble tatt på nytt og er byte for byte det samme.
# Story 3.4d: fotnoten i aksje.html og demo_startdag i app.py. Bildet er byte
# for byte det samme.
# Flettingen av main inn i grenen for 3.4d (23.10): kildene fra 8.6 og 3.4d
# sammen, saa avtrykket er regnet paa nytt. Bildet ble tatt paa nytt og er byte
# for byte det samme.
# Story 3.4d, VG2: demo_startdag i app.py med ukedag og dato fra tallformat.py.
# Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 3.4d b: fotnoten for «ikke vurdert» i delmalen _fotnote_ikke_vurdert.html,
# med den ekte teksten fra 22.10 kl. 23:19. Bildet ble tatt paa nytt og er byte
# for byte det samme.
# Story 3.4d d: kommentaren om FR-204 i app.py viser til Rettet-linja i prd.md.
# Bildet ble tatt paa nytt og er byte for byte det samme.
# Gjennomgangen av 3.4d 23.10 (BH1, ECH1): aaret i demo_startdag i app.py fra
# idag(). Bildet ble tatt paa nytt og er byte for byte det samme.
# Gjennomgangen 23.10 (VG6): 3.4d b endret ogsaa aksje.html, som tar inn
# delmalen, og ikke_vurdert for børsometeret i app.py. aksje_uten_kurser.html
# fra 3.4d d er ikke bak bildet.
# Story 3.4e a: demoteksten i fotnoten bare før STARTDAG, i app.py og
# _fotnote_ikke_vurdert.html. Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 3.4e b: setningen om i dag i fotnoten, i app.py og
# _fotnote_ikke_vurdert.html. Bildet ble tatt paa nytt og er byte for byte det samme.
# Gjennomgangen av 3.4e: _fotnoten i app.py med samme i_dag som siden, uten
# setningen om i dag i demoen. Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 3.4e a etter svaret 23.10 kl. 19:10: setningen i fotnoten for inneværende
# børsdag, i app.py og _fotnote_ikke_vurdert.html. Bildet ble tatt paa nytt og er byte for byte det samme.
# Gjennomgangen 23.10 kveld (ECH4): docstringen i _fotnoten i app.py.
# Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.2a a: ankerne ved kursgrafen og KI-teksten, i app.py, aksje.html og
# _perioder.html. Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.2a b: raden uten data i app.py, markedsoversikt.py og
# hjelpetekster.py. Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.2a c: stil.css og hjelpetekster.py. Bildet ble tatt paa nytt og er
# byte for byte det samme.
# Story 8.2a d: app.py, markedsoversikt.py og hjelpetekster.py. Bildet ble
# tatt paa nytt og er byte for byte det samme.
# Story 8.2a e: app.py og markedsoversikt.py. Bildet ble tatt paa nytt og er
# byte for byte det samme.
# Gjennomgangen av 8.2a 24.10: app.py, markedsoversikt.py og hjelpetekster.py.
# Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 3.5d b: æ, ø og å i meldingene fra demo.py. Bildet ble tatt paa nytt
# og er byte for byte det samme.
# Story 10.2e: KI-tekstene i demoen laget paa nytt med prompten versjon 3, og
# valgt_indeks flyttet fra app.py til hovedindeks.py. Bildet ble tatt paa nytt
# med samme hoeyde og viser den nye teksten for KVST.
# Story 10.2e, rettingen etter gruppens svar 24.10 kl. 21:49: KI-tekstene laget
# paa nytt med prompten versjon 3 rettet. Teksten for KVST ble stoppet, og
# bildet ble tatt paa nytt med hoeyden 1827.
# Story 10.2e, gruppens svar 24.10 kl. 23:23: KI-tekstene laget paa nytt med
# ferdig ordlyd for dagene. KVST ble stoppet igjen, og bildet viser BRFE.
# Story 10.2e, gruppens svar 25.10 kl. 00:51: modellen nevner ikke dagene, og
# setningen om dagene staar under KI-teksten (src/dagene.py). Bildet viser
# fortsatt BRFE, med hoeyden 1934.
# Story 10.2e, gruppens svar 25.10 kl. 12:12 og 12:19: setningen uten «for
# første gang», og «denne dagen» for en dag som ikke er i dag. Bildet viser
# fortsatt BRFE, med hoeyden 1934.
# Story 10.2f, gruppens svar 25.10 kl. 18:34 og 18:35: KI-tekstene laget paa
# nytt med den nye grunnen i prompten. Bildet viser fortsatt BRFE, der teksten
# besto, med hoeyden 1934.
# Story 10.2g, gruppens svar 25.10 kl. 19:54 og 19:56: KI-tekstene laget paa
# nytt med regelen for retningen Ingen, og hver rad har promptens avtrykk
# (demo_ki.py). Bildet viser fortsatt BRFE, der teksten besto, med hoeyden 1894.
# Gjennomgangen av 10.2g (BH1): til_json faar avtrykket fra lag_tekstene.
# Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 10.2h, gruppens svar 25.10 kl. 20:54: KI-tekstene laget paa nytt med
# ordstillingen etter «fordi» og rekkefoelgen paa sjekkene i prompten. Teksten
# for BRFE besto og er den samme, og bildet ble tatt paa nytt og er byte for
# byte det samme, med hoeyden 1894.
# Story 8.6b b: linja «Mål mot børsen» i stil.css og hjelpetekster.py. Bildet
# ble tatt paa nytt og er byte for byte det samme.
# Story 8.6b c: fargetrinnene og rammene i stil.css, og hjelpen i
# hjelpetekster.py. Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.6b d: kartet i stil.css og hjelpen i hjelpetekster.py. Bildet ble
# tatt paa nytt og er byte for byte det samme.
# Story 8.6b, svaret 26.10 kl. 13:00 (a): rekkefoelgen i kartet og hjelpen i
# hjelpetekster.py. Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.6b, svaret 26.10 kl. 13:00 (b): overskriften i feltet i stil.css og
# hjelpen i hjelpetekster.py. Bildet ble tatt paa nytt og er byte for byte det
# samme.
# Story 8.6b, svarene 26.10 kl. 13:00 (c) og 13:07 (e): tekstnivået i stil.css.
# Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.6b, svaret 26.10 kl. 15:21 (f): tabellen bak «Se tallene som tabell»
# i stil.css og hjelpen i hjelpetekster.py. Bildet ble tatt paa nytt og er byte
# for byte det samme.
# Gjennomgangen av 8.6b 26.10 (ECH4): datoen for børsdagen før i app.py. Bildet
# ble tatt paa nytt og er byte for byte det samme.
# Gjennomgangen av 8.6b 26.10 (BH, ECH): tekstnivået med @container i stil.css.
# Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.0f: hjelpeskriptet, lenken i _ramme.html og feltet i stil.css.
# Bildet ble tatt paa nytt og er byte for byte det samme.
# Story 8.0f, b: knappen som flytter feltet. Bildet ble tatt paa nytt og er
# byte for byte det samme.
# Gjennomgangen av 8.0f: grensen 1056 px og rettelsene i hjelp.js. Bildet
# ble tatt paa nytt og er byte for byte det samme.
AVTRYKK_BAK_AKSJESIDEN = "22006ee8710d6b633f2b2988f46ea672cfdfc29fd89874adb69b619f789bade2"
SLIK_TAS_AKSJESIDEN = (
    "Aksjesiden er endret, så bildet av den viser noe annet enn demoen. Ta "
    f"{AKSJESIDEBILDET} på nytt med fremgangsmåten i spesifikasjonen 3.3b, mot /aksje/BRFE: "
    "demobasen i en midlertidig mappe (lagring_sqlite.BASE_STI dit), OSE_DEMO=1, "
    "waitress på en ledig port, og msedge --headless --disable-gpu --hide-scrollbars "
    f"--window-size=1280,{HOEYDE_PAA_AKSJESIDEN} med egen --user-data-dir. Bildet skal slutte "
    "ved bunnen av grafen (figure), under KI-teksten: mål den og endre "
    "HOEYDE_PAA_AKSJESIDEN hvis den har flyttet seg. Oppdater så "
    "AVTRYKK_BAK_AKSJESIDEN til {avtrykk} i samme commit."
)


def _avtrykk_bak_bildet(filene: tuple[str, ...] = MALENE_BAK_BILDET) -> str:
    """sha256 av stien og innholdet, med LF, for hver fil bak bildet, og av
    merket «Eksempeltall» fra app.py. Story 3.3f: filene er et argument, så
    aksjesiden har sitt eget avtrykk."""
    import hashlib

    import app as app_modul

    filer = list(filene)
    filer += [p.relative_to(ROT).as_posix() for p in (ROT / "src" / "templates").glob("_*.html")]
    filer += [
        p.relative_to(ROT).as_posix()
        for p in (ROT / "src" / "static").rglob("*")
        if p.is_file() and p.suffix.lower() in SKRIFTFILER
    ]
    sum_ = hashlib.sha256()
    for fil in sorted(set(filer)):
        sum_.update(fil.encode("utf-8") + b"\0" + (ROT / fil).read_bytes().replace(b"\r\n", b"\n") + b"\0")
    sum_.update(b"EKSEMPELTALL_MERKE\0" + app_modul.EKSEMPELTALL_MERKE.encode("utf-8"))
    return sum_.hexdigest()


class TestSkjermbildet:
    """3.3b, punkt b, tilbake i 3.3e: skjermbildet av oversikten i demoen,
    under «Til faglærer», 1280 px bredt, med en alt-tekst som sier at det er
    demoen. Regelen fra 25.09: bildet viser bare demoen. Story 3.3f: i
    docs/appen/ og i knappen «Bilder av appen (demoen)»."""

    def _bildet(self) -> tuple[str, str]:
        tekst = README.read_text(encoding="utf-8")
        treff = [(a, s) for a, s in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", tekst) if s == SKJERMBILDET]
        assert len(treff) == 1, treff
        return treff[0]

    def test_fila_finnes_og_er_1280_px_bred_og_1573_px_hoey(self):
        """Svaret 18.10 kl. 21:42: 1280 x 1573, til bunnen av «Skilte seg ut».
        Ville feilet med bildet fra 3.3b (1280 x 1000), eller et bilde i en
        annen hoeyde enn HOEYDE_PAA_BILDET. Story 8.3: hoeyden er 1630 med
        knapperaden, og navnet paa testen staar, fordi kvalitetssikringen
        viser til det."""
        data = (ROT / SKJERMBILDET).read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert int.from_bytes(data[16:20], "big") == 1280
        assert int.from_bytes(data[20:24], "big") == HOEYDE_PAA_BILDET == 1630

    def test_bildet_har_ingen_tekstfelt(self):
        """Regel 16 (gjennomgangen av 3.3e, BH8 og ECH10): ingen sti eller
        brukernavn i metadataene. Ville feilet med et bilde tatt med et
        verktoey som skriver tEXt, iTXt, zTXt eller eXIf."""
        data = (ROT / SKJERMBILDET).read_bytes()
        i, biter = 8, []
        while i < len(data):
            lengde = int.from_bytes(data[i : i + 4], "big")
            biter.append(data[i + 4 : i + 8].decode("latin-1"))
            i += 12 + lengde
        assert biter[0] == "IHDR" and biter[-1] == "IEND", biter
        assert not {"tEXt", "iTXt", "zTXt", "eXIf"} & set(biter), biter

    def test_teksten_under_bildet_sier_at_det_er_demoen(self):
        """Alt-teksten vises ikke naar bildet lastes (3.3b, BH6)."""
        tekst = README.read_text(encoding="utf-8")
        etter = tekst.split(SKJERMBILDET + ")\n", 1)[1].split("\n", 1)[0]
        assert etter == "*Oversikten i demoen, med oppdiktede selskaper og kurser («Eksempeltall»).*"

    def test_bildet_tas_paa_nytt_naar_oversikten_endres(self):
        """Ville feilet hvis en mal, stilarket, en skrift, demodataene eller en
        modul bak oversikten ble endret uten at bildet ble tatt paa nytt.
        Feilmeldingen sier hvordan."""
        avtrykk = _avtrykk_bak_bildet()
        assert avtrykk == AVTRYKK_BAK_BILDET, SLIK_TAS_BILDET.format(avtrykk=avtrykk)

    def test_alt_teksten_sier_at_det_er_demoen(self):
        alt, _ = self._bildet()
        assert "demoen" in alt and "Eksempeltall" in alt and "ikke data fra Oslo Børs" in alt

    def test_bildet_staar_i_knappen_og_ikke_under_til_faglaerer(self):
        """Story 3.3f: bildet står i knappen «Bilder av appen (demoen)» før
        «Innhold», og ikke lenger under «Til faglærer». Ville feilet med
        bildet der det sto før."""
        tekst = README.read_text(encoding="utf-8")
        knappen = tekst.split("<summary>Bilder av appen (demoen)</summary>", 1)[1].split("</details>", 1)[0]
        assert SKJERMBILDET in knappen
        assert tekst.index(SKJERMBILDET) < tekst.index("**Innhold:**") < tekst.index("Til faglærer:")


class TestAksjesidebildet:
    """Story 3.3f, punkt b: bildet av aksjesiden i demoen, for BRFE fra 25.10
    (gruppens svar 24.10 kl. 23:23, b). Var KVST."""

    def test_fila_er_1280_px_bred_og_like_hoey_som_maalt(self):
        """Ville feilet med et bilde i en annen bredde, eller en annen høyde
        enn den målt til bunnen av grafen."""
        data = (ROT / AKSJESIDEBILDET).read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert int.from_bytes(data[16:20], "big") == 1280
        assert int.from_bytes(data[20:24], "big") == HOEYDE_PAA_AKSJESIDEN

    def test_bildet_har_ingen_tekstfelt(self):
        """Regel 16: ingen sti eller brukernavn i metadataene. Ville feilet
        med tEXt, iTXt, zTXt eller eXIf i fila."""
        data = (ROT / AKSJESIDEBILDET).read_bytes()
        i, biter = 8, []
        while i < len(data):
            lengde = int.from_bytes(data[i : i + 4], "big")
            biter.append(data[i + 4 : i + 8].decode("latin-1"))
            i += 12 + lengde
        assert biter[0] == "IHDR" and biter[-1] == "IEND", biter
        assert not {"tEXt", "iTXt", "zTXt", "eXIf"} & set(biter), biter

    def test_bildet_tas_paa_nytt_naar_aksjesiden_endres(self):
        """Ville feilet hvis malen, en delmal, en skrift, demodataene eller en
        modul bak aksjesiden ble endret uten at bildet ble tatt på nytt.
        Feilmeldingen sier hvordan."""
        avtrykk = _avtrykk_bak_bildet(FILENE_BAK_AKSJESIDEN)
        assert avtrykk == AVTRYKK_BAK_AKSJESIDEN, SLIK_TAS_AKSJESIDEN.format(avtrykk=avtrykk)


VIDEOFILER = {".mp4", ".webm", ".mov"}
# Filer Utforsker og Finder legger i en mappe, som ikke er bilder av appen.
SYSTEMFILER = {"Thumbs.db", ".DS_Store", "desktop.ini"}


def _knappen_med_bildene() -> str:
    """Innholdet i knappen «Bilder av appen (demoen)», mellom <summary> og
    </details>."""
    tekst = README.read_text(encoding="utf-8")
    deler = tekst.split("<summary>Bilder av appen (demoen)</summary>\n", 1)
    assert len(deler) == 2, "knappen «Bilder av appen (demoen)» mangler"
    return deler[1].split("</details>", 1)[0]


class TestBildeneAvAppen:
    """Story 3.3f (gruppens svar 18.10 kl. 23:03): bildene av appen står bak
    en knapp rett under beskrivelsen, i docs/appen/, bare av demoen."""

    def test_knappen_staar_rett_under_beskrivelsen_og_er_lukket(self):
        """Ville feilet hvis knappen sto et annet sted, hadde et annet navn,
        eller var åpen som standard (<details open>)."""
        tekst = README.read_text(encoding="utf-8")
        beskrivelse = next(a for a in tekst.split("\n\n") if a.startswith("OSE Signal viser"))
        etter = tekst.split(beskrivelse + "\n\n", 1)[1]
        assert etter.startswith("<details>\n<summary>Bilder av appen (demoen)</summary>\n\n"), etter[:80]
        assert etter.split("</details>\n\n", 1)[1].startswith("**Innhold:** ")
        # Lukket som de andre knappene: ingen <details> i README-en er åpen.
        assert re.findall(r"<details[^>]*>", tekst) == ["<details>"] * tekst.count("<details")

    def test_begge_bildene_ligger_i_docs_appen_med_alt_tekst_og_teksten_under(self):
        """Ville feilet hvis et bilde lå utenfor docs/appen/, manglet
        alt-tekst eller teksten under, eller ikke sa at det er demoen med
        oppdiktede tall."""
        knappen = _knappen_med_bildene()
        bilder = re.findall(r"^!\[([^\]]*)\]\(([^)]+)\)\n(.*)$", knappen, re.MULTILINE)
        assert [sti for _, sti, _ in bilder] == [SKJERMBILDET, AKSJESIDEBILDET]
        for alt, sti, under in bilder:
            assert sti.startswith("docs/appen/") and (ROT / sti).is_file(), sti
            assert "i demoen" in alt and "«Eksempeltall»" in alt and "ikke data fra Oslo Børs" in alt, alt
            assert under.startswith("*") and under.endswith("*"), under
            assert "i demoen" in under and "oppdiktede" in under and "«Eksempeltall»" in under, under
        # Ingen andre bilder i knappen, og ingen andre ord enn bildene.
        rest = re.sub(r"^!\[[^\]]*\]\([^)]+\)\n\*[^\n]*\*$", "", knappen, flags=re.MULTILINE)
        assert rest.strip() == "", rest

    def test_bildene_av_appen_staar_bare_i_knappen(self):
        """Ville feilet med et bilde fra docs/appen/ et annet sted i
        README-en, for eksempel under «Til faglærer» som før."""
        tekst = README.read_text(encoding="utf-8")
        uten_knappen = tekst.replace(_knappen_med_bildene(), "")
        assert "docs/appen/" in uten_knappen.split("\n## Mappestruktur\n", 1)[1]
        assert "](docs/appen/" not in uten_knappen.split("\n## Mappestruktur\n", 1)[0]

    def test_mappa_har_bare_bilder_og_video_av_appen(self):
        """Regel 16: bare bilder og video av demoen. Ville feilet med en annen
        fil i docs/appen/, en undermappe, eller et bilde i mappa som ikke står
        i knappen."""
        mappe = ROT / "docs" / "appen"
        filer = [p for p in mappe.rglob("*") if p.name not in SYSTEMFILER]
        assert all(p.is_file() and p.parent == mappe for p in filer), filer
        assert all(p.suffix.lower() in (BILDEFILER | VIDEOFILER) - {".svg"} for p in filer), filer
        bildene = sorted(p.relative_to(ROT).as_posix() for p in filer if p.suffix.lower() in BILDEFILER)
        assert bildene == sorted([SKJERMBILDET, AKSJESIDEBILDET]), bildene

    def test_avtrykket_dekker_modulene_appen_og_demoen_importerer(self):
        """Gjennomgangen (BH1, ECH1): lista over filene bak aksjesiden er ført
        for hånd. Ville feilet hvis appen eller demoen fikk en ny modul i src/
        som verken var med eller unntatt med grunn i IKKE_BAK_AKSJESIDEN."""
        import subprocess
        import sys

        skript = (
            "import sys; from pathlib import Path; src = Path('src').resolve(); sys.path.insert(0, str(src)); "
            "import app, demo; "
            "print('\\n'.join(sorted('src/' + Path(m.__file__).resolve().relative_to(src).as_posix() "
            "for m in list(sys.modules.values()) if getattr(m, '__file__', None) "
            "and Path(m.__file__).resolve().is_relative_to(src))))"
        )
        ut = subprocess.run([sys.executable, "-c", skript], cwd=ROT, capture_output=True, text=True, check=True)
        moduler = set(ut.stdout.split())
        assert "src/app.py" in moduler and "src/aksjedetalj.py" in moduler, moduler
        mangler = moduler - set(FILENE_BAK_AKSJESIDEN) - IKKE_BAK_AKSJESIDEN
        assert not mangler, mangler
        assert IKKE_BAK_AKSJESIDEN <= moduler

    def test_hvert_bilde_har_sitt_eget_avtrykk(self):
        """Ville feilet hvis aksjesiden brukte avtrykket for oversikten, så en
        endret mal bak aksjesiden ikke ga rød test."""
        assert _avtrykk_bak_bildet() == AVTRYKK_BAK_BILDET
        assert _avtrykk_bak_bildet(FILENE_BAK_AKSJESIDEN) == AVTRYKK_BAK_AKSJESIDEN
        assert AVTRYKK_BAK_BILDET != AVTRYKK_BAK_AKSJESIDEN
        assert "src/templates/aksje.html" in FILENE_BAK_AKSJESIDEN
        assert "src/templates/index.html" in MALENE_BAK_BILDET


def _python_krav() -> str:
    """Versjonen i requires-python i pyproject.toml, for eksempel «3.13»."""
    import tomllib

    krav = tomllib.loads((README.parent / "pyproject.toml").read_text(encoding="utf-8"))["project"]["requires-python"]
    treff = re.fullmatch(r">=(\d+\.\d+)", krav)
    assert treff, f"requires-python har en form testene ikke kjenner: {krav}"
    return treff.group(1)


class TestBildeneIDocs:
    def test_bare_de_tre_bildene_i_docs_bilder(self):
        """Gruppen 16.10 kl. 21:38: skjermbildet av oversikten er tatt ut, så
        ingen bilder med ekte data blir liggende. Story 3.3c: under
        docs/bilder/ ligger bare de tre skjermbildene i «Kom i gang», i
        docs/bilder/readme/. Story 3.3e: og bildet av oversikten i demoen.
        Ville feilet med et bilde til, eller et av de fire et annet sted.
        Story 3.3f: bildet av oversikten ligger i docs/appen/, så her er det
        de tre."""
        mappe = README.parent / "docs" / "bilder"
        # Bare bildefiler: Thumbs.db og .DS_Store fra Utforsker og Finder
        # skal ikke felle testen hos sensor (gjennomgangen av 3.3b, BH4, ECH).
        filer = sorted(
            p.relative_to(README.parent).as_posix()
            for p in mappe.rglob("*")
            if p.is_file() and p.suffix.lower() in BILDEFILER
        )
        # Story 3.3e: og bildet av oversikten i demoen. Story 3.3f: det ligger
        # i docs/appen/.
        ventet = [f"docs/bilder/readme/{navn}" for navn in BILDENE.values()]
        # Story 3.4 (godkjent 24.10 kl. 13:43): tegningene til investorsidene
        # i demoen, oppdiktede selskaper uten kurser.
        ventet += [f"docs/bilder/investorsider/svg/{navn}.svg" for navn in INVESTORSIDENE]
        ventet += [f"docs/bilder/investorsider/forhandsvisning/{navn}.png" for navn in INVESTORSIDENE]
        assert filer == sorted(ventet), filer


def _proevetabellen(proeve: str | None = None) -> str:
    """Radene i tabellene i §9, uten linjene under dem. Den daterte linja
    nevner kommandoer som ikke lenger er rader (gjennomgangen av PR 3, VG).
    Med proeve: bare tabellen under «### proeve» (Proeve 2 kom 13.10)."""
    kvalitet = (ROT / "docs" / "kvalitetssikring.md").read_text(encoding="utf-8")
    seksjon = kvalitet.split("## 9. README-prøven", 1)[1].split("\n## ", 1)[0]
    if proeve is not None:
        seksjon = seksjon.split(f"\n### {proeve}\n", 1)[1].split("\n### ", 1)[0]
    return "\n".join(l for l in seksjon.splitlines() if l.startswith("|"))


# Story 3.3h (gruppens svar 20.10 kl. 10:14-10:19): etter de felles stegene
# kommer linja «Velg vei», og demoen og den ekte versjonen staar bak hver sin
# pil, med ankeret i pila.
# Story 3.5f: «Velg vei» heter «Velg versjon», fordi «Velg vei etter hva du
# har» staar under tabellen.
VELG_VEI = "**Velg versjon.**"
# Story 3.5f: dobbeltklikket er en egen del foerst i «Kom i gang», og pila
# til uv har et anker, saa «Velg vei etter hva du har» kan lenke rett inn.
DOBBELTKLIKKET = "Enklest: dobbeltklikk (anbefalt)"
# Story 3.5g: overskriften het «Enklest: dobbeltklikk, uten Docker» til 3.5g.
# Ankeret staar paa linja over, saa lenkene til det virker som foer.
DOBBELTKLIKK_ANKER = "enklest-dobbeltklikk-uten-docker"
# Lenketeksten i «Til faglærer» og «Velg vei».
DOBBELTKLIKK_LENKE = "Enklest: dobbeltklikk"
UV_PIL = '<a name="uten-docker-med-uv"></a>Uten Docker, med uv'
ZIP_LENKEN = "https://github.com/IBE160-2026/G74-lund-osen/archive/refs/heads/main.zip"
PILENE = {"Demoen": "demoen", "Den ekte versjonen": "den-ekte-versjonen"}


def _pil(navn: str) -> str:
    """Innholdet i pila for demoen eller den ekte versjonen i «Kom i gang»."""
    treff = re.search(
        rf'^<details>\n<summary><a name="{PILENE[navn]}"></a>{re.escape(navn)}: [^\n]*</summary>\n\n'
        r"(.*?)\n\n</details>$",
        _kom_i_gang(),
        re.MULTILINE | re.DOTALL,
    )
    assert treff, navn
    return treff.group(1)


def _pilene(tekst: str) -> list[tuple[str, str]]:
    """Pilene paa oeverste nivaa i teksten som (summary uten anker, innhold),
    i rekkefoelgen de staar. Story 3.5g: «Står du fast?» har pilene til
    spoersmaalene inni, saa </details> telles mot <details>, og en pil inni
    en annen hoerer til innholdet."""
    pilene, dybde, start, summary = [], 0, 0, ""
    linjer = tekst.split("\n")
    for i, linje in enumerate(linjer):
        if linje == "<details>":
            if dybde == 0:
                start = i
                # Gjennomgangen av 3.5g (ECH10): en melding, ikke IndexError.
                assert i + 1 < len(linjer), "<details> er siste linje"
                treff = re.fullmatch(r"<summary>(.+)</summary>", linjer[i + 1])
                assert treff, linjer[i + 1]
                summary = re.sub(ANKER_I_PIL, "", treff.group(1))
            dybde += 1
        elif linje == "</details>":
            dybde -= 1
            assert dybde >= 0, i
            if dybde == 0:
                innhold = "\n".join(linjer[start + 2 : i])
                assert innhold.startswith("\n") and innhold.endswith("\n"), summary
                pilene.append((summary, innhold[1:-1]))
    assert dybde == 0
    # Gjennomgangen av 3.5g (ECH11): to piler med samme navn ville gjort at
    # _seksjon leste feil pil.
    navnene = [s for s, _ in pilene]
    assert len(navnene) == len(set(navnene)), navnene
    return pilene


# Story 3.5g (gruppens svar 26.10 kl. 23:00): alt i «Kom i gang» utenom de fem
# stegene og de to linjene under staar bak disse pilene, i denne rekkefoelgen.
# Pilene til demoen og den ekte versjonen staar rett etter Docker, med
# advarselen mot down -v under, og ikke inni pila til Docker, saa ankrene i
# <summary> synes (spesifikasjonen 3.5g).
PILENE_I_KOM_I_GANG = (
    "Demoen og den ekte versjonen",
    "Du trenger",
    "Med Docker Desktop",
    "Demoen: anbefalt for faglærer og sensor, uten nøkkel",
    "Den ekte versjonen: kurser fra EODHD, med egen nøkkel",
    "Uten Docker, med uv",
    "Slik virker dobbeltklikket",
    "Står du fast?",
)


# Gruppens svar 28.10 kl. 11:19 og 11:23 (e): tabellen «Demoen og den ekte
# versjonen» staar uten pil under «Innhold», foer «Til faglærer».
TABELLEN = '<a name="demoen-og-den-ekte-versjonen"></a>\n\n**Demoen og den ekte versjonen:**\n\n'


def _tabellen() -> str:
    """Tabellen «Demoen og den ekte versjonen» oeverst i README-en, med
    ankeret og linja over, til «Til faglærer»."""
    tekst = README.read_text(encoding="utf-8")
    assert tekst.count(TABELLEN) == 1, "tabellen mangler eller staar to ganger"
    resten = tekst.split(TABELLEN, 1)[1]
    # Gjennomgangen etter cc7f587 (ECH1): uten «Til faglærer» etter tabellen
    # ville resten av README-en blitt lest som tabellen.
    assert "\n\nTil faglærer:\n" in resten, "«Til faglærer» mangler etter tabellen"
    return resten.split("\n\nTil faglærer:\n", 1)[0]


def _seksjon(navn: str) -> str:
    """Delen under «### navn» i «Kom i gang», til neste ### eller «Velg vei».
    Fra 3.3h er demoen og den ekte versjonen innholdet i pila. Fra 3.5g er
    resten av «Kom i gang» innholdet i hver sin pil, og dobbeltklikket er
    delen under overskriften til den foerste pila."""
    if navn in PILENE:
        return _pil(navn)
    pilene = dict(_pilene(_kom_i_gang()))
    if navn in pilene:
        return pilene[navn].split(f"\n{VELG_VEI}", 1)[0]
    del_ = _kom_i_gang().split(f"### {navn}\n", 1)[1].split("\n### ", 1)[0]
    return del_.split("\n<details>\n", 1)[0] if navn == DOBBELTKLIKKET else del_


SEKSJONENE = {"Med Docker Desktop": [1, 2, 3, 4], "Den ekte versjonen": [5, 6, 7, 8, 9], "Demoen": [5, 6, 7]}


# Story 3.3c (svar 2 18.10 kl. 14:48): avsnittet som forklarer hvordan en
# kommando kopieres, staar én gang, sist i «Felles for begge», og hoerer ikke
# til steg 4.
KOPIERINGEN = "**Slik limer du inn en kommando.**"


def _steg(seksjon: str, nummer: int) -> str:
    """Steg nummer i seksjonen, med boksene som hoerer til det."""
    deler = re.split(r"^(\d+)\. ", _seksjon(seksjon).split(f"\n{KOPIERINGEN}", 1)[0], flags=re.MULTILINE)
    return dict(zip(deler[1::2], deler[2::2]))[str(nummer)]


def _detaljer(tekst: str) -> dict[str, str]:
    """Hver <details> i teksten som {summary: svar}. Tomme linjer rundt svaret
    kreves, ellers viser ikke GitHub markdown i det."""
    return dict(re.findall(r"<details>\n<summary>(.+?)</summary>\n\n(.*?)\n\n</details>", tekst, re.DOTALL))


# Story 3.3g: setningen om regelen kl. 14:48 (svaret 19.10 under
# «Prioritering» i epics.md), rett under listene i «Status».
REGELEN_FOR_EKSTRA = (
    "Det som står under «Ekstra», er ikke lovet i briefen og kommer bare med hvis det er ferdig og testet "
    "før README-prøven, senest én uke før innleveringen."
)


def _statuslister(status: str) -> dict[str, list[str]]:
    """Listene i «Status» som {navn: punkter}, story 3.3d. En liste er en
    linje i fet skrift alene, en tom linje, og så linjer som begynner med
    «- », til neste tomme linje. Et punkt over flere linjer, eller noe annet
    enn punkter mellom overskriften og den tomme linja, faar testen til aa
    feile."""
    lister = {}
    for navn, kropp in re.findall(r"^\*\*([^*\n]+)\*\*\n\n((?:.+\n?)+)", status, re.MULTILINE):
        linjer = kropp.rstrip("\n").split("\n")
        assert all(l.startswith("- ") for l in linjer), (navn, linjer)
        lister[navn] = [l[2:] for l in linjer]
    return lister


def _faq() -> str:
    return _seksjon("Står du fast?")


def _anker(overskrift: str) -> str:
    """Ankeret GitHub lager av en overskrift: smaa bokstaver, mellomrom blir
    bindestrek, og tegn som ikke er bokstav, tall, bindestrek eller
    understrek, faller bort."""
    return re.sub(r"[^\w\- ]", "", overskrift.strip().lower()).replace(" ", "-")


def _uten_bokser(tekst: str) -> str:
    return re.sub(r"^```.*?^```$", "", tekst, flags=re.MULTILINE | re.DOTALL)


# Et bilde paa egen linje, og teksten under i kursiv som eget avsnitt, med
# minst én tom linje imellom (gjennomgangen av 3.3c, BH12, ECH6).
BILDE_MED_TEKST = r"^!\[[^\]]*\]\([^)]+\)[ \t]*\n(?:(?:[ \t]*\n)+\*[^*\n][^\n]*\*[ \t]*(?:\n|$))?"


def _uten_bilder(tekst: str) -> str:
    """Teksten uten bildene og teksten under dem, som telles for seg (svar 2
    18.10 kl. 14:48)."""
    return re.sub(BILDE_MED_TEKST, "", tekst, flags=re.MULTILINE)


def _bildetekst(tekst: str, navn: str) -> str:
    """Teksten i kursiv i avsnittet rett under bildet navn, uten stjernene.
    Tom hvis avsnittet under ikke er i kursiv."""
    treff = re.search(
        rf"^!\[[^\]]*\]\([^)]*/{re.escape(navn)}\)[ \t]*\n(?:[ \t]*\n)+\*([^*\n][^\n]*)\*[ \t]*$",
        tekst,
        re.MULTILINE,
    )
    return treff.group(1) if treff else ""


# Story 3.3h: ankeret i en pil, som GitHub beholder med «user-content-» foran.
ANKER_I_PIL = r'<a name="([^"]+)"></a>'


def _alle_ankrene(tekst: str) -> list[str]:
    """Ankrene i den rekkefoelgen de staar, ogsaa de like: overskriftene og,
    fra 3.3h, ankrene i pilene, utenom kode (gjennomgangen av 3.3h, ECH6)."""
    uten = re.sub(r"`[^`\n]*`", "", _uten_bokser(tekst))
    ankrene = []
    for overskrift, navn in re.findall(rf"^#+ (.+)$|{ANKER_I_PIL}", uten, re.MULTILINE):
        ankrene.append(_anker(overskrift) if overskrift else navn)
    return ankrene


def _git_sporet() -> list[str] | None:
    """Filene git sporer, eller None uten git (ZIP-fila)."""
    import shutil
    import subprocess

    if shutil.which("git") is None or not (ROT / ".git").exists():
        return None
    svar = subprocess.run(["git", "-C", str(ROT), "ls-files", "-z"], capture_output=True, text=True)
    assert svar.returncode == 0, svar.stderr
    return [f for f in svar.stdout.split("\0") if f]


def _ankrene(tekst: str) -> set[str]:
    return set(_alle_ankrene(tekst))


# Spoersmaalene i «Står du fast?» foer 22:32 (76b68cb), og punktene under den
# ekte versjonen som ble flyttet til docs/hjelp.md.
TEMAENE = (
    "Må jeg logge inn eller lage konto?",
    "Hvilken Docker Desktop skal jeg velge?",
    "Hva skjer under installasjonen?",
    "Installasjonen ber om administrator.",
    "Docker Desktop sier at virtualisering mangler.",
    "Docker Desktop ber om å oppdatere WSL (Windows).",
    "Det står ikke «Engine running» etter noen minutter.",
    "ZIP-fila ser ut som en vanlig mappe.",
    "Det er to mapper med samme navn.",
    "Jeg finner ikke ZIP-fila på Mac.",
    "Jeg har fått koden fra før.",
    "Mappa finnes fra før.",
    "Hvilket vindu skal jeg åpne?",
    "Ingenting skjer når jeg limer inn.",
    "Hva betyr cd, og hvordan ser jeg at det gikk?",
    "Mappa lar seg ikke dra inn i vinduet.",
    "Stien har mellomrom og fikk ikke anførselstegn.",
    "Terminal spør om tilgang til Nedlastinger (Mac).",
    "Hva skal jeg se etter i vinduet?",
    "«docker» er ikke gjenkjent, eller «command not found: docker».",
    "«Cannot connect to the Docker daemon», «error during connect» eller «dockerDesktopLinuxEngine».",
    "To kommandoer havnet på samme linje.",
    "«no configuration file provided: not found».",
    "«toomanyrequests» fra Docker Hub.",
    "«port is already allocated», «address already in use» eller «ports are not available».",
    "Siden åpnes ikke.",
    "Hva er demoen?",
    "Hvordan starter jeg neste gang?",
    "Hva med nøkkelen?",
    "Når kan jeg hente?",
    "Oversikten er tom.",
    "Hvor ligger dataene?",
    "Kan appen nås fra nettet?",
)


# Story 3.3d: spoersmaalene som ble tatt ut av «Står du fast?», med svaret
# README-en hadde. docs/hjelp.md har minst det samme svaret (punkt b).
UTE_AV_README = {
    "Mappa lar seg ikke dra inn i vinduet.": (
        "PowerShell er trolig åpnet som administrator, og da sperrer Windows dra og slipp. Lukk vinduet "
        "og åpne PowerShell på vanlig måte (steg 3 med Docker)."
    ),
    "Ingenting skjer når jeg limer inn.": (
        "Kommandoene skrives i PowerShell eller Terminal, ikke i Docker Desktop. Docker Desktop skal "
        "bare være åpent, og du skriver ingenting i det. Ledetekst (Command Prompt) på Windows virker "
        "også for demoen, men stegene er skrevet for PowerShell, og den ekte versjonen trenger "
        "PowerShell.\n\nKopier kommandoen med ikonet til høyre i den grå boksen i README-en. Ikonet synes "
        "først når musa er over boksen. Du kan også markere kommandoen og trykke Ctrl+C (Cmd+C på Mac), "
        "eller skrive den inn. Lim den inn i PowerShell-vinduet fra steg 4 med Ctrl+V (Cmd+V på Mac), og "
        "trykk Enter."
    ),
    "«Cannot connect to the Docker daemon», «error during connect» eller «dockerDesktopLinuxEngine».": (
        "Docker Desktop er ikke startet, eller motoren er ikke klar. Start Docker Desktop, vent til det "
        "står «Engine running» (steg 1 med Docker), og prøv kommandoen igjen."
    ),
    # Story 3.2b: porten er 8000, som i docs/hjelp.md. Setningen om AirPlay,
    # som bruker 5000, er tatt ut (gruppens svar 18.10 kl. 18:58). Fra 3.3h
    # står den bare i git, fordi hjelpen er et levende dokument.
    "«port is already allocated», «address already in use» eller «ports are not available».": (
        "Noe annet bruker port 8000. Kjører den andre versjonen, stopper du den først (se «Bytte mellom "
        "demoen og den ekte versjonen» under «Mer for den som vil»)."
    ),
    "Oversikten er tom.": (
        "Uten henting starter appen med tom oversikt og viser kommandoen som henter. Hent kursene med "
        "steg 8 i den ekte versjonen, og last siden på nytt."
    ),
}
# Raadets forslag (instruksjonen 18.10 kl. 17:04), i rekkefoelgen i README-en.
# Gruppens svar 18.10 kl. 17:40: «Engine running» og «Cannot connect to the
# Docker daemon» er ett spoersmaal, fordi grunnen er den samme. Det staar
# ikke i docs/hjelp.md, der de to spoersmaalene staar hver for seg.
SAMMENSLAATT = (
    "«Engine running» kommer ikke, eller det står «Cannot connect to the Docker daemon» eller «error during connect»."
)
# Story 3.3j: ett spoersmaal for begge meldingene etter cd i steg 4.
CD_SPOERSMAALET = (
    "«is not recognized as the name of a cmdlet» eller «Cannot find path … because it does not exist» etter cd."
)
BEHOLDT_I_README = [
    SAMMENSLAATT,
    "ZIP-fila ser ut som en vanlig mappe.",
    # Story 3.3j (gruppens svar 22.10 kl. 17:42): de to svarene om cd er ett.
    CD_SPOERSMAALET,
    # Story 3.3i (U13): lagt inn foran «no configuration file provided».
    "Nettleseren sier at 127.0.0.1 nektet å koble til.",
    "«no configuration file provided: not found».",
]


class TestReadmeForNybegynnere:
    """Story 3.4, PR 3: «Kom i gang» for en som aldri har brukt Docker eller
    et terminalvindu. Formen fra 11.10 kl. 22:32: to versjoner i en tabell,
    felles steg 1-4, den ekte versjonen (anbefalt til 3.3g) og demoen fra steg 5,
    høyst 8 spørsmål, og resten i docs/hjelp.md."""

    def test_ingen_kommentar_paa_kommandolinjene(self):
        """Linjene skal virke ogsaa i Ledetekst, der # ikke er en kommentar."""
        for _spraak, blokk in _blokkene(_kom_i_gang()):
            assert "#" not in blokk, blokk

    def test_en_kommando_per_boks(self):
        """En av oss fikk to kommandoer paa samme linje 11.10."""
        for _spraak, blokk in _blokkene(_kom_i_gang()):
            assert len([l for l in blokk.splitlines() if l.strip()]) == 1, blokk

    def test_bare_kommandoer_i_kom_i_gang(self):
        """En blokk med spraak slapp unna testene for # og én kommando. I
        «Kom i gang» er alle blokker kommandoer, og linja fra terminalen
        staar i docs/hjelp.md."""
        assert {spraak for spraak, _ in _blokkene(_kom_i_gang())} == {""}

    def test_ingen_bokser_testene_ikke_ser(self):
        """GitHub viser ogsaa ~~~ og ``` med innrykk som bokser."""
        for linje in _kom_i_gang().splitlines():
            assert not re.match(r"^ +```|^ *~~~", linje), linje

    def test_tabellen_nevner_begge_og_hvilken_som_er_anbefalt(self):
        """Kl. 22:21: to versjoner med forskjellen forklart. Story 3.3g
        (svaret 19.10 kl. 14:46): vi anbefaler demoen, ikke den ekte, og
        tabellen merker ingen av dem. Ville feilet hvis tabellen manglet en
        versjon, eller anbefalte den ekte."""
        # Story 3.5g: tabellen staar i pila «Demoen og den ekte versjonen», og
        # anbefalingen er den foerste setningen i «Kom i gang».
        topp = _kom_i_gang().split('<summary><a name="med-docker-desktop"></a>', 1)[0]
        # Svarene 28.10 kl. 11:19 og 11:23 (e): tabellen staar oeverst.
        hode = [l for l in _tabellen().splitlines() if l.startswith("|")][0]
        assert "Den ekte versjonen" in hode and "| Demoen |" in hode
        # Story 3.3c: demoen i første kolonne, som i stegene.
        assert hode == "| | Demoen | Den ekte versjonen |", hode
        assert "Vi anbefaler demoen for faglærer og sensor" in topp
        assert "Vi anbefaler den ekte versjonen" not in topp

    def test_stegene_er_nummerert_og_har_hoeyst_65_ord(self):
        """Felles 1-4, så 5-9 i den ekte versjonen og 5-7 i demoen, hvert
        med hoeyst 65 ord utenom boksene og en sjekk paa at det gikk bra.

        Rettet 2026-10-13 (story 8.0e PR 2, svaret kl. 23:50): ordene telles
        slik leseren ser dem, med lenketeksten og uten adressen bak, og
        grensen er 65, ikke 60. Setningen fra docs/hjelp.md i steg 2 gjorde
        steget til 70 ord, 8 av dem i adressen til GitHub.

        Story 3.3c (svar 2 18.10 kl. 14:48): grensen gjelder teksten i
        steget. Bildet og teksten under det telles for seg, i
        test_teksten_under_hvert_bilde."""
        for seksjon, numre in SEKSJONENE.items():
            funnet = [int(n) for n in re.findall(r"^(\d+)\. ", _seksjon(seksjon), re.MULTILINE)]
            assert funnet == numre, (seksjon, funnet)
            for n in numre:
                tekst = re.sub(r"\]\([^)]*\)", "]", _uten_bilder(_uten_bokser(_steg(seksjon, n))))
                assert len(re.findall(r"\w+", tekst)) <= 65, (seksjon, n)
                assert "klar" in tekst.lower() or "Øverst står" in tekst, (seksjon, n)

    def test_steg_4_mappa_ikke_zip_fila(self):
        """Story 3.3c, rettelse a: i gjennomgangen 16.10 ble ZIP-fila dratt
        inn i stedet for mappa. Steg 4 sier mappa fra steg 2 (ikke ZIP-fila),
        og lenker til svaret om .zip til slutt i linja i docs/hjelp.md, som
        sier Esc (svar 2 kl. 14:48: detaljene i docs/hjelp.md når steget
        ellers blir over 65 ord). Ville feilet hvis .zip-sjekken falt bort
        fra steg 4."""
        steg = _steg("Med Docker Desktop", 4)
        assert "dra mappa `G74-lund-osen-main` fra steg 2 (ikke ZIP-fila), der README og compose ligger" in steg
        sporsmaal = "Står det .zip til slutt i linja."
        assert f"[Står det `.zip` til slutt?](docs/hjelp.md#{_anker(sporsmaal)})" in steg
        steg4 = _hjelp().split("\n## Steg 4: mappa\n", 1)[1].split("\n## ", 1)[0]
        svar = steg4.split(f"### {sporsmaal}\n\n", 1)[1].split("\n\n", 1)[0]
        assert "Dra mappa du pakket ut i steg 2, ikke ZIP-fila." in svar
        assert "Står det `.zip` til slutt i linja" in svar and "trykker du Esc" in svar
        # Gjennomgangen, VG8 og ECH1: Esc tømmer linja i PowerShell, men ikke
        # i Terminal på Mac, der Ctrl+U gjør det.
        assert "trykker du Esc (Windows) eller Ctrl+U (Mac), så linja blir tom" in svar

    def test_svaret_om_mellomrommet_etter_cd(self):
        """Story 3.3c, rettelse b: i gjennomgangen 16.10 ga `cd"C:\\..."`
        feilen «The term 'cdC:\\...' is not recognized as the name of a
        cmdlet». Spoersmaalet staar under «Står du fast?» og i docs/hjelp.md
        under «Steg 4: mappa», med samme svar. Ville feilet hvis svaret om
        mellomrommet falt bort.

        Story 3.3j: svaret er foerste avsnitt i spoersmaalet for begge
        meldingene etter cd."""
        sporsmaal = CD_SPOERSMAALET
        svar = _detaljer(_faq())[sporsmaal].strip().split("\n\n", 1)[0]
        assert svar.startswith("Kommer «is not recognized as the name of a cmdlet»: Det mangler mellomrom etter `cd`.")
        assert "(steg 4 med Docker)" in svar
        steg4 = _hjelp().split("\n## Steg 4: mappa\n", 1)[1].split("\n## ", 1)[0]
        assert re.search(rf"^### {re.escape(sporsmaal)}$", steg4, re.MULTILINE)
        i_hjelp = steg4.split(f"### {sporsmaal}\n\n", 1)[1].split("\n\n", 1)[0]
        assert i_hjelp.startswith(svar.strip())
        # Gjennomgangen, BH6: svaret i README-en sier ogsaa hva 'docker' i
        # meldingen betyr. «docker» er ikke gjenkjent har sitt eget svar, som står.
        assert "Står det `'docker'` i meldingen, er Docker Desktop ikke installert" in svar
        # Story 3.3e (gjennomgangen, ECH8): og 'uv', som står under «Tester».
        assert "Står det `'uv'` i meldingen, er uv ikke installert" in svar and "«Tester»" in svar
        assert "### «docker» er ikke gjenkjent, eller «command not found: docker»." in _hjelp()

    def test_svaret_om_cannot_find_path(self):
        """Story 3.3c, rettelse c: «Cannot find path» hadde ikke noe svar i
        gjennomgangen 16.10. Spoersmaalet staar under «Står du fast?» og i
        docs/hjelp.md under «Steg 4: mappa», med samme svar. Ville feilet
        hvis svaret falt bort, eller ikke sa at mappa skal dras paa nytt.

        Story 3.3j: svaret er andre avsnitt i spoersmaalet for begge
        meldingene etter cd."""
        sporsmaal = CD_SPOERSMAALET
        # Gjennomgangen av 3.3j (ECH3): andre avsnitt paa begge sider.
        svar = _detaljer(_faq())[sporsmaal].strip().split("\n\n")[1]
        assert svar.startswith(
            "Kommer «Cannot find path … because it does not exist»: Mappa ligger ikke der stien sier,"
        )
        assert "flyttet" in svar and "ZIP-fila ble dratt inn" in svar
        assert "dra mappa inn i vinduet på nytt (steg 4 med Docker)" in svar
        steg4 = _hjelp().split("\n## Steg 4: mappa\n", 1)[1].split("\n## ", 1)[0]
        i_hjelp = steg4.split(f"### {sporsmaal}\n\n", 1)[1].split("\n\n")[1]
        assert i_hjelp.startswith(svar.strip())

    def test_kopieringen_forklares_en_gang_og_hvert_steg_sier_hvor(self):
        """Story 3.3c, rettelse d, med svar 2 kl. 14:48: det var uklart hvor
        kommandoen limes inn og hvor kopi-ikonet er. Forklaringen staar én
        gang, rett foer det foerste steget med en kommando, og hvert steg med
        en kommando sier at den limes inn i PowerShell-vinduet fra steg 4.
        «Serving on» betyr bare at appen kjoerer. Ville feilet hvis et steg
        med en boks ikke sa hvor kommandoen limes inn, eller forklaringen
        manglet en av de tre maatene aa kopiere paa.

        Gjennomgangen av 3.3c: avsnittet er kort, hoeyst 65 ord som et steg
        (VG6, ECH2), og sier at ikonet er knappen stegene nevner (BH3,
        ECH12). «Serving on» forklares i stegene der linja staar, ikke i
        avsnittet. Steg 8 bruker et nytt vindu, saa det sier «det nye
        PowerShell-vinduet», ikke «fra steg 4» (BH1). Svaret under «Står du
        fast?» har ogsaa kopieringen (VG7)."""
        del_ = _kom_i_gang()
        assert del_.count(KOPIERINGEN) == 1
        avsnitt = del_.split(KOPIERINGEN, 1)[1].split("\n\n", 1)[0]
        for innhold in (
            "Kopier kommandoen med ikonet til høyre i den grå boksen.",
            "Ikonet, som stegene kaller knappen, synes først når musa er over boksen.",
            "markere den og trykke Ctrl+C eller Cmd+C",
            "eller skrive den inn.",
            "Lim den inn i PowerShell-vinduet fra steg 4 (Terminal på Mac)",
        ):
            assert innhold in avsnitt, innhold
        assert len(re.findall(r"\w+", KOPIERINGEN + avsnitt)) <= 65
        # Rett foer det foerste steget med en kommando, og etter steg 4.
        foerste_boks = re.search(r"^```", del_, re.MULTILINE).start()
        # Story 3.3h: rett foer «Velg vei» og pilene.
        # Story 3.5g: steg 4 i Docker, ikke steg 4 i dobbeltklikket.
        assert del_.index("\n4. **Skriv `cd`") < del_.index(KOPIERINGEN) < del_.index(f"\n{VELG_VEI}") < foerste_boks
        assert del_[del_.index(KOPIERINGEN) :].split("\n\n", 1)[1].startswith(VELG_VEI)
        # Hvert steg med en boks sier hvor den limes inn.
        for seksjon, numre in SEKSJONENE.items():
            for n in numre:
                steg = _steg(seksjon, n)
                if not _blokkene(steg):
                    continue
                if (seksjon, n) == ("Den ekte versjonen", 8):
                    assert "lim inn denne i det nye PowerShell-vinduet." in steg
                    assert "nye PowerShell-vinduet fra steg 4" not in steg
                else:
                    assert "i PowerShell-vinduet fra steg 4" in steg, (seksjon, n)
        # BH11: demoen slutter i steg 7 og sier hvor den ekte versjonen
        # begynner. Fra 3.3h med lenken til pila.
        assert (
            "Vil du også prøve den ekte versjonen, går du videre til steg 5 i "
            "[den ekte versjonen](#den-ekte-versjonen) og klikker på pila." in _steg("Demoen", 7)
        )
        # VG7: svaret om innlimingen har kopieringen. Fra 3.3d står det bare i
        # docs/hjelp.md, som sjekkes under.
        # Linja i steg 7 og steg 5 i demoen sier hva den betyr.
        assert "som bare betyr at appen kjører" in _steg("Den ekte versjonen", 7)
        assert "Den linja betyr bare at demoen kjører." in _steg("Demoen", 5)
        # Og docs/hjelp.md der svaret staar.
        innliming = _hjelp().split("### Ingenting skjer når jeg limer inn.\n\n", 1)[1].split("\n### ", 1)[0]
        assert "ikonet til høyre i den grå boksen" in innliming and "Ctrl+C" in innliming
        assert "skrive den inn" in innliming and "PowerShell-vinduet fra steg 4" in innliming
        vinduet = _hjelp().split("### Hva skal jeg se etter i vinduet?\n\n", 1)[1].split("\n### ", 1)[0]
        assert "«Serving on http://0.0.0.0:8000» betyr bare at appen kjører." in vinduet

    def test_stegene_nevner_powershell_og_terminal(self):
        steg = _steg("Med Docker Desktop", 3)
        assert "PowerShell" in steg and "Terminal" in steg and "ikke ISE" in steg

    def test_zip_fila_maa_pakkes_ut(self):
        steg = _steg("Med Docker Desktop", 2)
        assert "«Download ZIP»" in steg and "«Pakk ut alle»" in steg
        # Story 8.0e PR 2: setningen fra «Jeg har fått koden fra før» i
        # docs/hjelp.md staar ordrett til slutt i steg 2.
        svar = _hjelp().split("### Jeg har fått koden fra før.", 1)[1].strip().split("\n\n", 1)[0]
        assert svar == "Har du fått koden som mappe eller ZIP-fil, pakker du den ut og går til steg 3."
        assert _uten_bilder(steg).strip().endswith(svar)
        assert (
            _uten_bilder(_steg("Med Docker Desktop", 4))
            .strip()
            .endswith("Har mappa et annet navn, drar du den mappa der README og compose ligger.")
        )
        assert "Du må pakke ut" in _detaljer(_faq())["ZIP-fila ser ut som en vanlig mappe."]

    def test_advarselen_mot_down_v_staar_synlig(self):
        """22:32: rett under stoppet i den ekte versjonen, synlig og ikke
        lukket. Fra 3.3h (gruppens svar 20.10 kl. 20:20) står den uendret
        rett under pila til den ekte versjonen, utenfor alle piler, så den
        kommer rett etter steg 9 når pila er åpen, og synes for alle når den
        er lukket. Ville feilet hvis advarselen sto i en pil, ikke kom rett
        etter pila til den ekte versjonen, eller var endret."""
        tekst = _kom_i_gang()
        advarsel = ADVARSELEN_MOT_DOWN_V.split(".**", 1)[0] + ".**"
        assert tekst.count(advarsel) == 1
        assert advarsel not in _pil("Den ekte versjonen")
        assert ADVARSELEN_MOT_DOWN_V in _utenfor_pilene(tekst)
        assert _pil("Den ekte versjonen").endswith("```\ndocker compose down\n```")
        etter_pila = tekst.split('<a name="den-ekte-versjonen"></a>', 1)[1].split("\n</details>\n\n", 1)[1]
        assert etter_pila.split("\n\n", 1)[0] == ADVARSELEN_MOT_DOWN_V

    def test_staar_du_fast_har_hoeyst_5_spoersmaal(self):
        """22:32: FAQ-en var for lang. Hoeyst 8 spoersmaal, hvert som
        <details> med <summary>, og en lenke til docs/hjelp.md.

        Story 3.3c (svar 1 18.10 kl. 14:48): hoeyst 10, for svarene om
        mellomrommet etter cd og «Cannot find path» fra gjennomgangen 16.10.

        Story 3.3d (beslutningen 16.10 kl. 21:53-21:58, svarene 18.10 kl.
        15:37): hoeyst 5. Hvilke fem er raadets forslag, ikke avgjort 16.10.
        Het test_staar_du_fast_har_hoeyst_8_spoersmaal til 3.3c, og
        test_staar_du_fast_har_hoeyst_10_spoersmaal til 3.3d.

        Story 3.3i (instruksjonen 22.10 kl. 16:06, U13): hoeyst 6, for svaret
        paa at 127.0.0.1 nektet aa koble til. Navnet staar, fordi
        docs/vurderingsmatrise.md og vedlegget i docs/kvalitetssikring.md
        nevner testen.

        Story 3.3j (gruppens svar 22.10 kl. 17:42): hoeyst 5 igjen, som
        avgjort 16.10. De to svarene om cd i steg 4 er ett spoersmaal. Ville
        feilet med et sjette spoersmaal (M1)."""
        faq = _faq()
        sporsmaal = _detaljer(faq)
        assert 1 <= len(sporsmaal) <= 5
        assert list(sporsmaal) == BEHOLDT_I_README, list(sporsmaal)
        assert faq.count("<details>") == faq.count("</details>") == faq.count("<summary>") == len(sporsmaal)
        rest = re.sub(r"<details>.*?</details>", "", faq, flags=re.DOTALL)
        assert [l for l in rest.splitlines() if l.strip()] == [
            "Klikk på spørsmålet som passer.",
            "Flere spørsmål og svar står i [docs/hjelp.md](docs/hjelp.md).",
        ]

    def test_hvert_tema_staar_i_readme_eller_hjelp(self):
        """Ingenting falt bort da FAQ-en ble kortere: hvert spoersmaal fra
        «Står du fast?» og hvert punkt under den ekte versjonen foer 22:32
        staar som spoersmaal i README-en eller som overskrift i docs/hjelp.md."""
        i_readme = set(_detaljer(_faq()))
        i_hjelp = set(re.findall(r"^### (.+)$", _hjelp(), re.MULTILINE))
        for tema in TEMAENE:
            assert tema in i_readme or tema in i_hjelp, tema

    def test_lenkene_virker(self):
        """Lenker til en fil eller et avsnitt, i README-en og docs/hjelp.md."""
        readme = README.read_text(encoding="utf-8")
        for tekst, mappe, egne in ((readme, ROT, _ankrene(readme)), (_hjelp(), HJELP.parent, _ankrene(_hjelp()))):
            for maal in re.findall(r"\]\(([^)\s]+)\)", tekst):
                if maal.startswith(("http://", "https://", "mailto:")):
                    continue
                fil, _, anker = maal.partition("#")
                if fil:
                    assert (mappe / fil).exists(), maal
                if anker:
                    ankre = egne if not fil else _ankrene((mappe / fil).read_text(encoding="utf-8"))
                    assert anker in ankre, maal
        assert "](#står-du-fast)" in readme and "](docs/hjelp.md)" in _faq()

    def test_hjelp_har_frontmatter_og_er_nevnt_i_readme(self):
        """Regel 4 og 19."""
        topp = _hjelp().split("---\n", 2)[1]
        for felt in ("title:", "status: aktiv", "created: 2026-10-11", "updated: "):
            assert felt in topp, felt
        readme = README.read_text(encoding="utf-8")
        mappestruktur = readme.split("## Mappestruktur", 1)[1]
        assert "docs/hjelp.md" in mappestruktur
        dokumentene = readme.split("## Dokumentene", 1)[1].split("\n## ", 1)[0]
        assert "](docs/hjelp.md)" in dokumentene

    def test_merket_i_demoen_er_det_samme_som_i_malene(self):
        """Regel 19: 8.0c kan ikke endre merket uten at README-en rettes.
        Fra 8.0c staar merket ett sted, EKSEMPELTALL_MERKE i app.py, med
        «Demoversjon.» foran i malene (tillegget 11.10). Sitatet i README-en
        staar fortsatt ordrett oeverst paa siden."""
        import app as app_modul

        sitert = _steg("Demoen", 6).split("Øverst står «", 1)[1].split("»", 1)[0]
        assert sitert == app_modul.EKSEMPELTALL_MERKE
        # Story 8.0d: merket staar i rammen, som alle tre malene bruker.
        ramme = (ROT / "src" / "templates" / "_ramme.html").read_text(encoding="utf-8")
        # Story 3.3i (U51): lenken til den ekte versjonen i README-en staar
        # etter merket, i samme avsnitt.
        assert re.findall(r'<p class="eksempeltall">(.+?)</p>', ramme) == [
            "Demoversjon. {{ eksempeltall_merke }} Ekte kurser trenger en gratis nøkkel fra EODHD: se "
            '<a href="{{ ekte_versjonen_url }}">Den ekte versjonen</a>.'
        ]
        for mal in ("index.html", "aksje.html", "basefeil.html"):
            tekst = (ROT / "src" / "templates" / mal).read_text(encoding="utf-8")
            assert tekst.startswith('{% extends "_ramme.html" %}'), mal

    def test_linja_som_viser_at_appen_er_klar(self):
        """Linja er kopiert fra en kjoering 11.10. Ville feilet hvis porten i
        Dockerfile ble endret, eller app eller demo fikk egen command."""
        kommando = dict(_instruksjoner())["CMD"]
        lytter = re.search(r"--listen=([\d.]+:\d+)", kommando).group(1)
        for tjeneste in ("app", "demo"):
            felt = _tjenester()[tjeneste]
            assert "command" not in felt and "entrypoint" not in felt, tjeneste
        assert f"`Serving on http://{lytter}`" in _steg("Demoen", 5)
        assert f"`Serving on http://{lytter}`" in _steg("Den ekte versjonen", 7)
        tekst = [b for spraak, b in _blokkene(_hjelp()) if spraak == "text"]
        assert len(tekst) == 1
        assert tekst[0].strip() == f"demo-1  | INFO:waitress:Serving on http://{lytter}"

    def test_henvisningene_og_proevetabellen(self):
        """Hver «steg N» peker paa et steg som finnes, og §9 har stegene i
        rekkefoelge for begge versjonene (VG i gjennomgangen av PR 3)."""
        tekst = _kom_i_gang() + _hjelp()
        for n in re.findall(r"[Ss]teg (\d+)", tekst):
            assert 1 <= int(n) <= 9, n
        # «steg N i demoen» og «steg N i den ekte versjonen» peker paa et steg
        # som finnes i den versjonen (VG).
        for n in re.findall(r"steg (\d+) i demoen", tekst):
            assert int(n) in SEKSJONENE["Demoen"], n
        for n in re.findall(r"steg (\d+) i den ekte versjonen", tekst):
            assert int(n) in SEKSJONENE["Den ekte versjonen"], n
        tabell = _proevetabellen("Prøve 1")
        # Story 3.5f: hovedveien, dobbeltklikket, står først, i en egen tabell
        # med radene D1-D6, og Docker og uv er reserven under.
        linjer = tabell.splitlines()
        assert linjer[0] == "| # | Steg i README-en | Det som skjedde | Tid (min) |", linjer[0]
        assert re.findall(r"^\| (D\d+) \|", tabell, re.MULTILINE) == [f"D{n}" for n in range(1, 7)]
        reserven = "| # | Kommando eller steg i README-en | Det som skjedde | Tid (min) |"
        assert linjer.count(reserven) == 1
        assert tabell.index("| D6 |") < tabell.index(reserven)
        assert "«Download ZIP»" in tabell.split("| D2 |", 1)[0] and "«Start demoen»" in tabell.split("| D4 |", 1)[0]
        tabell = tabell[tabell.index(reserven) :]
        # Story 3.3c: demoen foer den ekte versjonen, som i README-en, og en
        # kolonne for tiden hvert steg tok.
        assert tabell.splitlines()[0] == reserven
        # Gjennomgangen, BH7: byttet begynner med den ekte versjonen, som kjoerte sist.
        bytte = [l for l in tabell.splitlines() if "| Byttet" in l]
        assert len(bytte) == 1
        assert bytte[0].startswith(
            "| 16 | Byttet, fra den ekte versjonen til demoen og tilbake: "
            "`docker compose up --build`, så `docker compose down`"
        ), bytte[0]
        assert tabell.index("| Demoen, steg 7:") < tabell.index("| Den ekte versjonen, steg 5:")
        assert [int(n) for n in re.findall(r"^\| (\d+) \|", tabell, re.MULTILINE)] == list(range(1, 24))
        assert [int(n) for n in re.findall(r"\| Steg (\d+):", tabell)] == [1, 2, 3, 4]
        assert [int(n) for n in re.findall(r"\| Den ekte versjonen, steg (\d+):", tabell)] == [5, 6, 7, 8, 9]
        assert [int(n) for n in re.findall(r"\| Demoen, steg (\d+):", tabell)] == [5, 6, 7]
        # Proeve 2 (13.10) er den ekte versjonen med egen noekkel, steg 5-9.
        tabell = _proevetabellen("Prøve 2: den ekte versjonen med egen nøkkel")
        assert re.findall(r"\| Steg (\d+):|\| Demoen, steg (\d+):", tabell) == []
        assert [int(n) for n in re.findall(r"\| Den ekte versjonen, steg (\d+):", tabell)] == [5, 6, 7, 8, 9]

    def test_stopp_i_begge_versjonene(self):
        assert [b.strip() for _, b in _blokkene(_steg("Den ekte versjonen", 9))] == ["docker compose down"]
        assert [b.strip() for _, b in _blokkene(_steg("Demoen", 7))] == ["docker compose --profile demo down"]
        assert "Ctrl+C" in _steg("Demoen", 7) and "Ctrl+C" in _steg("Den ekte versjonen", 9)

    def test_installasjonen_av_uv_staar_foer_uv_sync(self):
        """Story 3.3e, punkt b (gruppens svar 18.10 kl. 20:39): «Tester» har
        installasjonen av uv foer uv sync, én boks for Windows (PowerShell) og
        én for Mac (Terminal), og hva man gjoer naar uv ikke blir funnet.
        «Uten Docker, med uv» viser dit og har ingen egen kopi, og
        docs/hjelp.md har samme svar. Ville feilet hvis en av boksene manglet,
        sto etter uv sync, eller sto ogsaa i «Uten Docker, med uv»."""
        tester = README.read_text(encoding="utf-8").split("\n## Tester\n", 1)[1].split("\n## ", 1)[0]
        assert "](https://docs.astral.sh/uv/getting-started/installation/)" in tester
        assert f"Windows (PowerShell):\n\n```\n{UV_WINDOWS}\n```" in tester
        assert f"Mac (Terminal):\n\n```\n{UV_MAC}\n```" in tester
        assert tester.index(UV_WINDOWS) < tester.index(UV_MAC) < tester.index("```\nuv sync\n```")
        funnet = "lukker du vinduet, åpner et nytt og går til mappa, som i steg 4"
        assert "«The term 'uv' is not recognized» eller «command not found: uv»" in tester and funnet in tester
        assert "Første `uv sync` laster ned Python og pakkene" in tester
        # Gjennomgangen (BH1, VG2, ECH5): tidene som staar i dagsfila 18.10,
        # 219-424 s, i hele minutter. 424 s er kjoeringen for 3.3e. Fra 21.10
        # tidene i Utført-linjene 20.10, 307,84-579,47 s.
        assert "Hele testsettet tok mellom 5 og 10 minutter på maskinen vår 20.10." in tester
        uv = _seksjon("Uten Docker, med uv")
        assert "[«Tester»](#tester)" in uv
        assert UV_WINDOWS not in uv and UV_MAC not in uv and "install.ps1" not in uv and "install.sh" not in uv
        sporsmaal = "«The term 'uv' is not recognized» eller «command not found: uv»."
        svar = _hjelp().split(f"### {sporsmaal}\n\n", 1)[1].split("\n\n", 1)[0]
        assert funnet in svar and "](../README.md#tester)" in svar

    def test_variablene_i_tabellen_er_de_i_env_example(self):
        """Story 3.3e, punkt c: tabellen under «Variablene i .env» har de
        samme variablene som .env.example, og hver av dem leses i src/.
        Testen leser .env.example, aldri .env. Ville feilet med en variabel i
        .env.example som ikke stod i tabellen, eller en i tabellen som koden
        ikke leser."""
        eksempel = (ROT / ".env.example").read_text(encoding="utf-8")
        # Ogsaa «export NAVN=» og mellomrom foer =, som dotenv godtar (ECH6).
        i_fila = set(re.findall(r"^#?\s*(?:export\s+)?([A-Z][A-Z0-9_]+)\s*=", eksempel, re.MULTILINE))
        knapp = _detaljer(_seksjon("Mer for den som vil"))["Variablene i .env"]
        rader = [l for l in knapp.splitlines() if l.startswith("| `")]
        i_tabellen = [re.match(r"\| `([A-Z0-9_]+)` \|", l).group(1) for l in rader]
        assert len(i_tabellen) == len(set(i_tabellen)) and set(i_tabellen) == i_fila, (i_tabellen, i_fila)
        for rad in rader:
            assert len([c for c in rad.strip("|").split("|")]) == 4, rad
        kilde = "\n".join(p.read_text(encoding="utf-8") for p in sorted((ROT / "src").glob("*.py")))
        for navn in i_tabellen:
            assert f'"{navn}"' in kilde, navn
        assert "`OSE_DEMO` og `OSE_I_DOCKER` settes av `compose.yaml` og `Dockerfile`" in knapp
        # Steg 6 viser dit.
        assert "[`.env`](#mer-for-den-som-vil)" in _steg("Den ekte versjonen", 6)

    def test_standardene_i_tabellen_er_de_i_koden(self):
        """Gjennomgangen av 3.3e (BH2, BH3, VG5): standardene i tabellen er
        de koden, .env.example, compose.yaml og Dockerfile bruker. Ville
        feilet hvis standardadressen til Ollama, adressen i compose,
        OSE_KI_TJENESTE=av i .env.example eller lokal uten variabelen ble
        endret uten at tabellen fulgte, eller OSE_DEMO og OSE_I_DOCKER ikke
        ble satt der tabellen sier."""
        from ki_lokal import STANDARD_URL
        from ki_tekst import AV, LOKAL

        knapp = _detaljer(_seksjon("Mer for den som vil"))["Variablene i .env"]
        rader = {re.match(r"\| `([A-Z0-9_]+)` \|", l).group(1): l for l in knapp.splitlines() if l.startswith("| `")}
        assert f"`{STANDARD_URL}`" in rader["OSE_KI_OLLAMA_URL"]
        ollama_i_compose = [l.strip() for l in _tjenester()["hent"]["environment"]]
        assert "OSE_KI_OLLAMA_URL: http://ollama:11434" in ollama_i_compose, ollama_i_compose
        assert "`http://ollama:11434` i Docker" in rader["OSE_KI_OLLAMA_URL"]
        eksempel = (ROT / ".env.example").read_text(encoding="utf-8")
        assert re.search(rf"^OSE_KI_TJENESTE={AV}$", eksempel, re.MULTILINE)
        assert f"`{AV}` etter steg 6" in rader["OSE_KI_TJENESTE"]
        assert f"gjelder `{LOKAL}`" in rader["OSE_KI_TJENESTE"]
        assert 'OSE_DEMO: "1"' in COMPOSE.read_text(encoding="utf-8")
        assert "OSE_I_DOCKER=1" in (ROT / "Dockerfile").read_text(encoding="utf-8")
        assert "Med uv slås demoen på med `--demo`." in knapp

    def test_mer_for_den_som_vil_er_lukket(self):
        """22:32: Bytte og uv staar, lukket i <details> under én overskrift."""
        mer = _seksjon("Mer for den som vil")
        # Story 10.2: den lokale modellen, ogsaa lukket. Story 3.3e:
        # variablene i .env.
        # Story 3.5f: uv med ankeret, saa «Velg vei» kan lenke rett inn. Fra
        # 3.5g (gruppens svar 26.10 kl. 23:00) staar uv i sin egen pil foer
        # «Slik virker dobbeltklikket», og ikke her.
        assert set(_detaljer(mer)) == {
            "Bytte mellom demoen og den ekte versjonen",
            "Variablene i .env",
            "Den lokale modellen for KI-teksten (valgfri)",
            # Story 10.7: egen noekkel, ogsaa lukket.
            "Egen nøkkel til Gemini, Anthropic eller OpenAI (valgfri)",
            # Story 2.3d: hentingen hver kveld, ogsaa lukket, med ankeret
            # docs/hjelp.md lenker til.
            '<a name="hentingen-hver-kveld"></a>Hentingen hver kveld med Oppgaveplanlegging (Windows, valgfri)',
            # Story 3.5a: start med dobbeltklikk sto her, lukket, til gruppen
            # valgte hovedvei. Fra 3.5f (svaret 25.10 kl. 11:32) er den en
            # egen del foerst i «Kom i gang».
        }
        assert not any("uv" in s for s in _detaljer(mer))

    def test_uv_delen_er_to_nummererte_lister(self):
        """Story 3.3d, punkt c: uv-delen under «Mer for den som vil» er to
        korte nummererte lister, «Demoen» og «Den ekte versjonen», med én
        linje før hver boks. Kommandoene er de samme som før 3.3d. Ville
        feilet hvis en liste manglet, et punkt fikk mer enn én linje, eller
        en kommando ble endret."""
        uv = _seksjon("Uten Docker, med uv")
        forventet = {
            "Demoen": ["uv sync", "uv run python src/demo.py", "uv run python src/app.py --demo"],
            "Den ekte versjonen": [
                "cp .env.example .env",
                "uv run python src/fetch_prices.py",
                "uv run python src/app.py",
            ],
        }
        assert uv.index("**Demoen**\n\n") < uv.index("**Den ekte versjonen**\n\n")
        demo, ekte = uv.split("**Demoen**\n\n", 1)[1].split("**Den ekte versjonen**\n\n", 1)
        ekte, etter = ekte.split("\n\nBasen, demobasen", 1)
        # Gjennomgangen, ECH6: setningene foer og etter listene staar.
        # Story 3.3e: installasjonen av uv står bare under «Tester».
        assert uv.startswith(
            "Med Python 3.13 og [uv](https://docs.astral.sh/uv/). Installasjonen av uv står under "
            "[«Tester»](#tester). Først demoen.\n\n**Demoen**"
        )
        assert etter.startswith(" og øyeblikksbildene ligger da i `data/` i mappa. Uten `--demo` åpner")
        for navn, liste in (("Demoen", demo), ("Den ekte versjonen", ekte)):
            punkter = re.findall(r"^(\d+)\. ([^\n]+)\n\n```\n([^\n]+)\n```$", liste, re.MULTILINE)
            assert [int(n) for n, _, _ in punkter] == list(range(1, len(forventet[navn]) + 1)), (navn, punkter)
            assert [k for _, _, k in punkter] == forventet[navn], navn
            assert all(linje.endswith(":") for _, linje, _ in punkter), navn
            # Ingenting annet i lista enn punktene og boksene.
            rest = re.sub(r"^\d+\. [^\n]+\n\n```\n[^\n]+\n```$", "", liste, flags=re.MULTILINE)
            assert not rest.strip(), (navn, rest)

    def test_svarene_beholdt_innholdet(self):
        """Gjennomgangen 11.10 (VG): bare overskriftene ble sjekket etter
        flyttingen. Innholdet fra svarene foer 22:32 staar i README-en eller
        docs/hjelp.md. Ville feilet hvis et svar ble tomt eller mistet en del."""
        tekst = _faq() + _hjelp()
        for innhold in (
            "wsl --update",
            "Quit Docker Desktop",
            "hvalen ved klokka",
            "AMD64",
            "Apple Silicon",
            "Safari",
            "administrator, og da sperrer Windows dra og slipp",
            "`.env` med nøkkelen",
            "port 8000",
            "Ledetekst",
            "Ikke velg «Windows PowerShell ISE»",
            "filene README og compose",
            "uten filendelsen",
            "virtualisering",
            "toomanyrequests",
            "samme IP-adresse",
            "Dataene ligger i to Docker-volumer",
            "20 kall i døgnet",
            "notepad .env",
            "open -e .env",
            "nano .env",
            "før midnatt",
            "helgen",
            "Appen kan ikke nås fra nettet",
            "lim inn stoppkommandoen",
            "Cmd+mellomrom",
            "Svar OK",
            "Pakk ut alle",
            "glidelås",
        ):
            assert innhold in tekst, innhold

    def test_spoersmaalene_som_ble_tatt_ut_staar_i_hjelp(self):
        """Story 3.3d, punkt b: hvert spoersmaal som ble tatt ut av «Står du
        fast?», staar i docs/hjelp.md med minst det samme svaret som
        README-en hadde. Ville feilet hvis et av dem ble tatt ut av README-en
        uten aa staa i docs/hjelp.md."""
        i_hjelp = dict(re.findall(r"^### ([^\n]+)\n\n(.*?)(?=\n\n### |\n\n## |\Z)", _hjelp(), re.MULTILINE | re.DOTALL))
        i_readme = _detaljer(_faq())
        for sporsmaal, svar in UTE_AV_README.items():
            assert sporsmaal not in i_readme, sporsmaal
            assert sporsmaal in i_hjelp, sporsmaal
            assert i_hjelp[sporsmaal].strip().startswith(svar), sporsmaal

    def test_det_foerste_spoersmaalet_er_at_docker_ikke_kjoerer(self):
        """Gruppens svar 18.10 kl. 17:40: det første spørsmålet under «Står du
        fast?» er ett spørsmål om at Docker ikke kjører, med begge meldingene
        i overskriften. Svaret har det som sto i begge svarene i
        docs/hjelp.md, som står hver for seg. Ville feilet hvis det første
        spørsmålet ikke nevnte både «Engine running» og «Cannot connect to the
        Docker daemon», eller svaret mistet noe fra et av de to."""
        sporsmaal = list(_detaljer(_faq()))
        assert "«Engine running»" in sporsmaal[0] and "«Cannot connect to the Docker daemon»" in sporsmaal[0]
        assert "«error during connect»" in sporsmaal[0]
        svar = _detaljer(_faq())[sporsmaal[0]]
        i_hjelp = dict(re.findall(r"^### ([^\n]+)\n\n(.*?)(?=\n\n### |\n\n## |\Z)", _hjelp(), re.MULTILINE | re.DOTALL))
        ikke_startet = i_hjelp[
            "«Cannot connect to the Docker daemon», «error during connect» eller «dockerDesktopLinuxEngine»."
        ]
        engine = i_hjelp["Det står ikke «Engine running» etter noen minutter."]
        assert svar.startswith(ikke_startet.strip())
        # «Avslutt Docker Desktop helt:» er blitt «avslutter du Docker Desktop
        # helt:» i samme setning. Resten står ordrett.
        assert engine.startswith("Avslutt Docker Desktop helt: ")
        assert "avslutter du Docker Desktop helt: " + engine.split("helt: ", 1)[1].strip() in svar

    def test_like_spoersmaal_har_samme_svar(self):
        """Et spoersmaal som staar baade i README-en og i docs/hjelp.md, har
        samme svar begge steder. Svaret i docs/hjelp.md kan ha mer etter."""
        i_hjelp = dict(re.findall(r"^### ([^\n]+)\n\n(.*?)(?=\n\n### |\n\n## |\Z)", _hjelp(), re.MULTILINE | re.DOTALL))
        # Mutanten H13 overlevde foerst: (.+) med DOTALL slukte resten av fila,
        # saa bare ett spoersmaal ble lest, og ingen ble sammenlignet.
        assert len(i_hjelp) == len(re.findall(r"^### ", _hjelp(), re.MULTILINE))
        felles = [s for s in _detaljer(_faq()) if s in i_hjelp]
        # Story 3.3d: alle i README-en står også i docs/hjelp.md, utenom det
        # sammenslåtte spørsmålet (svaret kl. 17:40), som har sin egen test.
        assert len(felles) == len(_detaljer(_faq())) - 1 and SAMMENSLAATT not in felles, felles
        for sporsmaal, svar in _detaljer(_faq()).items():
            if sporsmaal in i_hjelp:
                assert i_hjelp[sporsmaal].strip().startswith(svar.strip()), sporsmaal

    def test_boksene_i_hjelp_foelger_de_samme_reglene(self):
        """Gjennomgangen 11.10 (VG): docs/hjelp.md har ogsaa kommandoer.
        Ingen #, én kommando per boks, bare blokker uten spraak eller text, og
        ingen ~~~ eller ``` med innrykk."""
        hjelp = _hjelp()
        for spraak, blokk in _blokkene(hjelp):
            assert spraak in ("", "text"), spraak
            if not spraak:
                assert "#" not in blokk and len([l for l in blokk.splitlines() if l.strip()]) == 1, blokk
        for linje in hjelp.splitlines():
            assert not re.match(r"^ +```|^ *~~~", linje), linje

    def test_til_faglaerer_og_kom_i_gang_foer_status(self):
        """Kl. 23:41: beskrivelsen, så «Til faglærer», så «Kom i gang»,
        så «Status». Ville feilet hvis «Status» kom foerst igjen, eller noe
        kom mellom beskrivelsen og «Til faglærer», utenom bildene, «Innhold»
        og tabellen «Demoen og den ekte versjonen» (svarene 28.10 kl. 11:19
        og 11:23, e)."""
        tekst = README.read_text(encoding="utf-8")
        # Story 3.5f: ankeret kom-i-gang staar paa linja over overskriften.
        kom_i_gang = f'\n<a name="kom-i-gang"></a>\n\n{KOM_I_GANG}\n'
        for del_ in ("Til faglærer:", kom_i_gang, "\n## Status\n", "\n## Tester\n"):
            assert del_ in tekst, del_
        assert (
            tekst.index("Til faglærer:")
            < tekst.index(kom_i_gang)
            < tekst.index("\n## Status\n")
            < tekst.index("\n## Tester\n")
        )
        topp = tekst.split(kom_i_gang, 1)[0]
        # Story 3.3f: knappen med bildene telles som ett avsnitt.
        topp = re.sub(r"<details>.*?</details>", "<details>", topp, flags=re.DOTALL)
        avsnitt = [a.strip() for a in topp.split("\n\n") if a.strip()]
        # Gruppen 16.10 kl. 21:38: skjermbildet under «Til faglærer» er tatt
        # ut, så «Til faglærer» er igjen siste avsnitt før «Kom i gang».
        # Story 3.3e (gruppens svar 18.10 kl. 00:20): bildet av oversikten
        # står igjen rett under «Til faglærer», som i 3.3b. Story 3.3f
        # (gruppens svar 18.10 kl. 23:03): bildene står i knappen rett under
        # beskrivelsen, og «Til faglærer» er igjen siste avsnitt.
        assert avsnitt[-1].startswith("Til faglærer:"), avsnitt[-1]
        assert SKJERMBILDET not in avsnitt[-1]
        # Gruppens svar 28.10 kl. 11:19 og 11:23 (e): tabellen «Demoen og den
        # ekte versjonen» står mellom «Innhold» og «Til faglærer», med
        # ankeret og linja over.
        assert avsnitt[-2].startswith("| | Demoen | Den ekte versjonen |"), avsnitt[-2]
        assert avsnitt[-3] == "**Demoen og den ekte versjonen:**", avsnitt[-3]
        assert avsnitt[-4] == '<a name="demoen-og-den-ekte-versjonen"></a>', avsnitt[-4]
        # Story 3.3d, punkt f: «Innhold» står rett under beskrivelsen, og fra
        # 3.3f rett under knappen.
        assert avsnitt[-5].startswith("**Innhold:** "), avsnitt[-5]
        assert avsnitt[-6] == "<details>", avsnitt[-6]
        assert avsnitt[-7].startswith("OSE Signal viser"), avsnitt[-7]
        assert "\n## " not in topp

    def test_status_uten_storynumre_og_uten_kommando(self):
        """Kl. 23:41: «Status» i vanlige ord, uten storynumre og uten
        kommandoen, som sto uten stegene foer den. Datoer som «13.–16.10» er
        lov, storynumre i alle formene vi har brukt er ikke det."""
        tekst = README.read_text(encoding="utf-8")
        assert "\n## Status\n" in tekst
        status = tekst.split("\n## Status\n", 1)[1].split("\n## ", 1)[0]
        assert not re.search(r"\(\s*\d{1,2}[AB]?\.\d", status), status
        assert not re.search(r"\b\d{1,2}[AB]?\.\d{1,2}[a-z]\b", status), status
        assert not re.search(r"\b\d{1,2}-\d{1,2}[a-z]?\b", status), status
        assert not re.search(r"\b[Ss]tor(y|ies|yen)\b|PR #\d", status), status
        assert "```" not in status and "~~~" not in status and "`" not in status
        assert not re.search(r"docker[ -]compose|uv run", status, re.IGNORECASE)
        # Story 3.3g: «Status» begynner med at prosjektet er under utvikling.
        assert status.startswith(
            "\nProsjektet er under utvikling. Listene under viser hva som er ferdig på main, og hva som gjenstår.\n"
        ), status[:200]
        for innhold in (
            "hentingen",
            "Docker",
            "demoen",
            "README-en",
            "kallene som er igjen",
            "hjelp bak «?»",
            "tydeligere merking",
            "utseendet fra designforslaget",
            "KI-teksten",
            "Euronext",
            "fra en lokal modell",
            "bare tekster som besto kontrollen",
            "](_bmad-output/implementation-artifacts/sprint-status.yaml)",
        ):
            # Story 3.3d: punktene i listene begynner med stor bokstav.
            assert innhold.lower() in status.lower(), innhold
        # Story 3.3d (beslutningen 16.10 kl. 21:53-21:58): to lister, «Ferdig»
        # og «Neste», med ett punkt per linje og hoeyst 8 punkter hver. Het
        # «Flettet til main:» og «Neste:» i ett avsnitt til 3.3d.
        # Gjennomgangen av flettingen 12.10 (VG): hver sak staar i riktig liste.
        # Ville feilet hvis noe som ikke er flettet, sto under «Ferdig», slik
        # grenen 8-0b sa om 2.3b.
        assert "Flettet til main" not in status.split("«Ferdig» betyr flettet til main.", 1)[0]
        lister = _statuslister(status)
        # Story 3.3g (svaret 19.10 kl. 14:48): «Neste» er delt i det briefen
        # lover og det ekstra.
        assert list(lister) == ["Ferdig", "Neste i v1", "Ekstra, hvis tiden rekker"], list(lister)
        for navn, punkter in lister.items():
            assert 1 <= len(punkter) <= 8, (navn, len(punkter))
        # Story 3.3h (gruppens svar 20.10 kl. 10:14-10:19): «Ferdig» er en
        # kort liste over det appen kan, og hvert punkt er kort. Høyst 20
        # ord fra 20.10, da signalet kom først i lista og demoen fikk tilbake
        # «av de tre sjekkene» (rådets funn), innenfor 8 punkter. Var 16.
        for punkt in lister["Ferdig"]:
            assert len(re.findall(r"\w+", punkt)) <= 20, punkt
        # Gjennomgangen, ECH2: listene staar samlet, uten tomme linjer inni,
        # saa et punkt etter en tom linje ikke slipper unna grensen. Etter
        # listene kommer setningen om regelen kl. 14:48 (3.3g).
        samlet = "\n\n".join(
            f"**{navn}**\n\n" + "\n".join(f"- {p}" for p in punkter) for navn, punkter in lister.items()
        )
        assert samlet + "\n\n" + REGELEN_FOR_EKSTRA + "\n\n«Ferdig» betyr flettet til main." in status
        ferdig = "\n".join(lister["Ferdig"]).lower()
        neste_punkter = lister["Neste i v1"] + lister["Ekstra, hvis tiden rekker"]
        neste = "\n".join(neste_punkter).lower()
        # Story 3.3h: det appen kan, med det samme som er flettet som før,
        # kortere sagt.
        for sak in (
            "hentingen",
            "kallene som er igjen",
            "docker for begge versjonene",
            "demoen",
            "hjelp bak «?»",
            "tydeligere merking",
            "datoene og månedsmerkene",
            # Story 10.5: lenken til investorsiden er flettet.
            "lenken til investorsiden",
            # Story 2.7b: historikken på aksjesiden.
            "signalet dag for dag",
            "oversikten og utseendet fra designforslaget",
            "sortering ved klikk i kolonneraden",
            "ki-teksten fra en lokal modell på aksjesiden",
            # Gjennomgangen av 3.3h (BH1, ECH3, VG3): at bare tekster som
            # besto kontrollen vises, og kontrollen av børsdagen, står.
            "bare tekster som besto kontrollen",
            "med bryter",
            "med børsdagskontroll",
            "kursene og hovedindeksen",
            "over tabellen på forsiden",
            # 2.9b og 2.9c (instruksjonen 18.10 kl. 17:04).
            "søylene",
            "stiplet linje i kursgrafen",
            # Gjennomgangen, VG1: resten av det som er flettet.
            # Story 2.3c: første gang går hentingen også på dagtid, så punktet
            # sier «fra kl. 22», og «på børsdager» er tatt ut for å holde
            # punktet på høyst 20 ord. Var «fra kl. 22 på børsdager».
            "fra kl. 22",
            # Story 3.4b: KI-teksten i demoen er flettet.
            # Rådets funn 20.10: demoen viser kombinasjonene av de tre sjekkene.
            "alle 10 fargekombinasjonene av de tre sjekkene og ki-tekst laget med gemma",
            # Story 8.16: periodene i kursgrafen er flettet.
            "periodene i kursgrafen med «velg dag»",
            # Story 8.3: Min liste er flettet.
            "min liste, med stjernen foran hvert selskap",
            # Story 8.6: børsometeret er flettet.
            "og børsometeret",
            # Story 10.7: egne nøkler er flettet.
            "eller med egen nøkkel",
            # Story 2.3c: første henting på dagtid er flettet.
            "første gang på dagtid",
        ):
            assert sak in ferdig, sak
        # Story 3.3h: det rundt appen står i én setning under listene, ikke
        # i «Ferdig».
        rundt = (
            "Rundt appen er dette også ferdig: README-en med bilder i «Kom i gang» og demoen først, ruff i CI og "
            "i testene, den oppdaterte kvalitetssikringen og et ryddigere repo uten kopien av BMAD-skillene."
        )
        assert rundt in status
        for sak in ("readme-en", "ruff", "kvalitetssikringen", "bmad"):
            assert sak not in ferdig, sak
        assert "resten av KI-laget" not in status and "Selve teksten lages ikke ennå" not in status
        # «Neste» foelger rekkefoelgen under «Prioritering» i epics.md etter
        # svarene 18.10 kl. 00:39 og 11:20, med KI-tekstene i demoen og Min
        # liste foerst. Ett punkt per sak, i den rekkefoelgen.
        # Story 3.4b: KI-tekstene i demoen er flyttet til «Ferdig».
        # Story 3.3g: historikken og signaldagene er delt, NewsWeb er tatt ut
        # av lenkene, og fra signaldagene staar resten under «Ekstra».
        # Story 8.3: Min liste er flyttet til «Ferdig».
        # Story 10.5: lenken til investorsiden er flyttet til «Ferdig».
        # Story 2.7b: historikken er flyttet til «Ferdig».
        # Story 10.7: egne nøkler er flyttet til «Ferdig», og README-rettingen
        # er neste (svarene 21.10 kl. 22:51 og 22.10 kl. 00:09).
        # Story 3.3i: README-rettingen er flettet, og første henting på
        # dagtid (2.3c, avgjørelsen 21.10 kl. 23:33) er neste.
        # Story 2.3c: første henting på dagtid er flyttet til «Ferdig», og
        # prøven på en ren maskin er neste (avgjørelsen 21.10 kl. 18:33).
        saker = (
            "prøven av readme-en på en ren maskin",
            "signaldagene i kursgrafen",
            "«vis ki-tekst»",
            # Story 8.16: periodene i kursgrafen er flyttet til «Ferdig».
            "på forsiden periodevalget",
            "velge og bytte aksjer",
        )
        assert len(neste_punkter) == len(saker), neste_punkter
        for punkt, sak in zip(neste_punkter, saker):
            assert sak in punkt.lower(), (sak, punkt)
            assert sak not in ferdig, sak
        for sak in ("utseendet fra designforslaget", "hovedindeksen", "sortering ved klikk i kolonneraden", "søylene"):
            assert sak not in neste, sak
        # Setningene om begge versjonene, boersmeldingene og detaljene staar
        # under listene.
        etter = status.split("**Ekstra, hvis tiden rekker**", 1)[1].split("\n\n", 2)[2]
        for setning in (
            # Gjennomgangen, ECH1: hva «Ferdig» betyr, fordi sprintstatusen kan
            # si review for noe som er flettet.
            "«Ferdig» betyr flettet til main.",
            "Det som bygges etter demoen, skal vises i begge versjonene.",
            "Børsmeldinger er ikke med i v1, fordi Euronext ikke ga tillatelse til automatisert henting (plan B).",
            "Detaljene står i [sprintstatusen](",
        ):
            assert setning in etter, setning

    def test_lenken_til_staar_du_fast_sier_lenger_ned(self):
        """Kl. 23:46: «se «Står du fast?» lenger ned»."""
        assert "se [«Står du fast?»](#står-du-fast) lenger ned." in _kom_i_gang()

    def test_beskrivelsen_foelger_koden_og_gir_ikke_raad(self):
        """Beskrivelsen som ble godkjent 11.10 kl. 23:50. Antallet aksjer er
        lengden av AKSJEUNIVERS, og antallet sjekker og navnene deres er de i
        signalberegning.py, saa README-en maa foelge naar lista endres (2.11
        og 2.12). Den sier at appen ikke gir raad (NFR-06)."""
        import kursdata

        tekst = README.read_text(encoding="utf-8")
        # Story 3.3d: «Innhold» står mellom beskrivelsen og «Til faglærer».
        beskrivelse = [a for a in tekst.split("Til faglærer:", 1)[0].split("\n\n") if a.startswith("OSE Signal viser")]
        assert len(beskrivelse) == 1
        beskrivelse = beskrivelse[0]
        assert beskrivelse.startswith("OSE Signal viser")
        assert f"viser {len(kursdata.AKSJEUNIVERS)} aksjer på Oslo Børs" in beskrivelse
        # Antallet sjekker telles fra navnene i koden, ikke fra returtypen til
        # sjekker_fra, som kan skrives tuple[Sjekk, ...] uten at noe endres
        # (gjennomgangen 12.10).
        navn = re.findall(r'navn="(\w+)"', (ROT / "src" / "signalberegning.py").read_text(encoding="utf-8"))
        navn = list(dict.fromkeys(navn))
        antall = len(navn)
        tall = {2: "To", 3: "Tre", 4: "Fire"}
        assert antall in tall, navn
        assert f"{tall[antall]} enkle sjekker" in beskrivelse
        # Styrken er summen av sjekkene uten fortegn (FR-703), saa den hoeyeste er antallet.
        assert f"signalstyrke fra 0 til {antall}" in beskrivelse
        # Story 3.3g: «interesse (handelsvolum)». Forklaringen er lov bare
        # rett etter det siste navnet (gjennomgangen, BH8).
        siste = navn[antall - 1].lower()
        assert "– " + ", ".join(n.lower() for n in navn[: antall - 1]) + f" og {siste} –" in beskrivelse.replace(
            f" og {siste} (handelsvolum) –", f" og {siste} –"
        )
        assert beskrivelse.count("(handelsvolum)") <= 1
        assert "Appen gir ikke råd om å kjøpe eller selge." in beskrivelse
        # 12.10 kl. 11:12: at appen er under utvikling, staar ogsaa oeverst,
        # ikke bare i «Status» etter hele «Kom i gang».
        # Rett etter setningen om raad, som instruksjonen kl. 11:15 sier (VG 12.10).
        assert "selge. Den er under utvikling og ikke ferdig." in beskrivelse

    def test_hvorfor_bare_15_aksjer(self):
        """12.10 kl. 10:22: spoersmaalet staar i docs/hjelp.md under
        «Den ekte versjonen», rett etter «Hva med nøkkelen?». Tallet er
        lengden av AKSJEUNIVERS, saa hjelpen maa foelge naar lista endres
        (2.11 og 2.12)."""
        import kursdata

        antall = len(kursdata.AKSJEUNIVERS)
        hjelp = _hjelp()
        # Story 3.3c: «Demoen» foer «Den ekte versjonen», som i README-en.
        assert (
            hjelp.index("\n## Steg 4: mappa\n")
            < hjelp.index("\n## Demoen\n")
            < hjelp.index("\n## Den ekte versjonen\n")
        )
        ekte = hjelp.split("\n## Den ekte versjonen\n", 1)[1].split("\n## ", 1)[0]
        overskrifter = re.findall(r"^### (.+)$", ekte, re.MULTILINE)
        sporsmaal = f"Hvorfor bare {antall} aksjer?"
        assert sporsmaal in overskrifter, overskrifter
        assert overskrifter.index(sporsmaal) == overskrifter.index("Hva med nøkkelen?") + 1
        svar = ekte.split(f"### {sporsmaal}\n\n", 1)[1].split("\n\n", 1)[0]
        assert f"med {antall} aksjer" in svar
        assert "20 kall i døgnet" in svar and "opptil 18" in svar
        # Gjennomgangen av PR #31, punkt 3 (12.10 kl. 10:38): svaret
        # rett over sier hvor mange kall en henting bruker, og det tallet
        # foelger ogsaa lista.
        nokkel = ekte.split("### Hva med nøkkelen?\n\n", 1)[1].split("\n\n", 1)[0]
        # Ordgrense etter tallet, saa 1 ikke godtar «15» (Verification Gap 12.10).
        # Story 2.8: en henting er aksjene og hovedindeksen.
        assert re.search(rf"en henting bruker {antall + 1}\b", nokkel), nokkel

    def test_innhold_lenker_til_hovedoverskriftene(self):
        """Story 3.3d, punkt f (beslutningen 16.10 kl. 21:53-21:58): én linje
        «Innhold» rett under beskrivelsen, med lenker til hovedoverskriftene
        fra «Kom i gang» til «Medlemmer», i den rekkefølgen. Ville feilet med
        en lenke til en overskrift som ikke finnes, eller en som mangler."""
        tekst = README.read_text(encoding="utf-8")
        innhold = [l for l in tekst.splitlines() if l.startswith("**Innhold:** ")]
        assert len(innhold) == 1
        lenker = re.findall(r"\[([^\]]+)\]\(#([^)]+)\)", innhold[0])
        hoved = re.findall(r"^## (.+)$", _uten_bokser(tekst), re.MULTILINE)
        # Story 3.5f: «Kom i gang: nedlasting og installasjon» staar som «Kom
        # i gang» i «Innhold», og ankeret kom-i-gang er beholdt paa linja over.
        hoved = hoved[hoved.index(KOM_I_GANG[3:]) : hoved.index("Medlemmer") + 1]
        assert hoved[0] == KOM_I_GANG[3:] and lenker[0] == ("Kom i gang", "kom-i-gang"), lenker
        hoved[0] = "Kom i gang"
        assert [t for t, _ in lenker] == hoved, lenker
        # Gjennomgangen, ECH5: hvert anker finnes én gang, ellers gir GitHub
        # den neste «-1», og lenken gaar til den foerste.
        alle = _alle_ankrene(tekst)
        for tittel, anker in lenker:
            assert anker == _anker(tittel) and alle.count(anker) == 1, anker
        assert f'<a name="kom-i-gang"></a>\n\n{KOM_I_GANG}\n' in tekst
        assert innhold[0] == "**Innhold:** " + " · ".join(f"[{t}](#{a})" for t, a in lenker)

    def test_mappestrukturen_lenker_til_stier_i_repoet(self):
        """Story 3.3d, punkt f: hver mappe og fil i «Mappestruktur» er en
        relativ lenke med samme tekst som stien, og peker på noe som finnes
        og ikke holdes ute av .gitignore. Det som ikke er i repoet, blir ikke
        lenker. Ville feilet med en lenke til data/."""
        from test_ryddighet import ignorert

        gitignore = (ROT / ".gitignore").read_text(encoding="utf-8")
        del_ = README.read_text(encoding="utf-8").split("\n## Mappestruktur\n", 1)[1].split("\n## ", 1)[0]
        punkter = [l for l in del_.splitlines() if l.startswith("- ")]
        # Story 3.3f: 8 med docs/appen/. Story 3.5a: 9 med start/ og
        # .gitattributes. Story 3.4 (24.10): 10 med docs/bilder/investorsider/.
        # Story 3.5f: 15 med filene i rota. Gruppens svar 27.10 kl. 06:31:
        # 16 med .logs/.
        assert len(punkter) == 16, punkter
        for punkt in punkter:
            # Hver sti i kodeformat i punktet er en lenke, ogsaa etter
            # tankestreken (gjennomgangen, BH3 og ECH4).
            assert "`" not in re.sub(r"\[`[^`]+`\]\([^)]+\)", "", punkt), punkt
        lenker = re.findall(r"\[`([^`]+)`\]\(([^)]+)\)", del_)
        # Alle lenkene, ogsaa uten kodeformat, er de i kodeformat.
        # Story 3.3e: 16 med bildet av oversikten. Story 3.3f: 18 med docs/appen/
        # og bildet av aksjesiden.
        # Story 3.5a: 20 med start/ og .gitattributes.
        # Story 3.4 (24.10): 23 med docs/bilder/investorsider/, LESMEG.md og
        # bobler.json.
        # Story 3.5f: 30 med README.md, CLAUDE.md, pyproject.toml, uv.lock,
        # .env.example, .gitignore og .mailmap. Gruppens svar 27.10 kl. 06:31:
        # 31 med .logs/.
        assert len(re.findall(r"\]\(", del_)) == len(lenker) == 31, lenker
        sporet = _git_sporet()
        for tekst, maal in lenker:
            # Maalet er stien i teksten, relativ og uten «..» (BH4, ECH3).
            # Bildene staar med filnavnet, som foer 3.3d, etter mappa de ligger i.
            # Story 3.3f: bildet av oversikten etter docs/appen/.
            filnavn = {navn: f"docs/bilder/readme/{navn}" for navn in BILDENE.values()}
            filnavn[SKJERMBILDET.rsplit("/", 1)[1]] = SKJERMBILDET
            filnavn[AKSJESIDEBILDET.rsplit("/", 1)[1]] = AKSJESIDEBILDET
            # Story 3.4: filene etter docs/bilder/investorsider/.
            for navn in ("LESMEG.md", "bobler.json"):
                filnavn[navn] = f"docs/bilder/investorsider/{navn}"
            assert maal == tekst or filnavn.get(tekst) == maal, (
                tekst,
                maal,
            )
            assert not re.match(r"[a-zA-Z]+:|/|#", maal) and ".." not in maal.split("/"), maal
            sti = maal.rstrip("/")
            assert (ROT / sti).exists(), maal
            if sporet is not None:
                # Store og smaa bokstaver som i git, og noe er sporet (ECH3).
                assert any(f == sti or f.startswith(sti + "/") for f in sporet), maal
            # ignorert() leser stien som en fil, og «data/» i .gitignore
            # gjelder bare mapper, saa en mappe sjekkes med en fil inni (mutant
            # N6 overlevde foerst).
            if maal.endswith("/") or (ROT / sti).is_dir():
                sti = f"{sti}/x"
            assert not ignorert(gitignore, sti), maal
        # Linja om det som ikke er i repoet, har ingen lenker.
        ikke = [l for l in del_.splitlines() if l.startswith("Ikke i repoet:")]
        assert len(ikke) == 1 and "](" not in ikke[0]

    def test_til_faglaerer_begynner_med_demoen_den_ekte_versjonen_og_testene(self):
        """Story 3.3d, punkt e (beslutningen 16.10 kl. 21:16, med svarene kl.
        21:25 og 21:57, og svaret 18.10 kl. 15:37): først under «Til
        faglærer» kommer tre lenker, hver med en kort forklaring foran, til
        demoen, den ekte versjonen og «Tester». Ville feilet med en lenke til
        en overskrift som ikke finnes."""
        tekst = README.read_text(encoding="utf-8")
        lista = tekst.split("Til faglærer:\n", 1)[1].split("\n\n", 1)[0].splitlines()
        forventet = [
            # Story 3.5f: foerst dobbeltklikket, saa Docker.
            (
                "Se appen med oppdiktede tall, uten konto og nøkkel, med et dobbeltklikk på «Start demoen»",
                # Story 3.5g: lenketeksten uten «(anbefalt)», og ankeret fra
                # foer, paa linja over overskriften.
                DOBBELTKLIKK_LENKE,
                DOBBELTKLIKK_ANKER,
            ),
            # Gjennomgangen, BH2: demolenken sier ogsaa hvor steg 1-4 staar.
            (
                "Eller med Docker Desktop, etter [steg 1–4](#med-docker-desktop)",
                "demoen",
                _anker("Demoen"),
            ),
            # Story 3.3i (U52): en invitasjon til den ekte versjonen, etter
            # demoen. Var «Ekte kurser, med en gratis nøkkel fra EODHD».
            (
                "Demoen viser så mye som mulig. Prøv gjerne også ekte kurser etterpå, med en gratis nøkkel fra EODHD",
                "den ekte versjonen",
                _anker("Den ekte versjonen"),
            ),
            # Story 3.3e (gjennomgangen, VG7): uv installeres foerst.
            ("De automatiske testene, med to kommandoer etter at uv er installert", "Tester", _anker("Tester")),
        ]
        alle = _alle_ankrene(tekst)
        for linje, (forklaring, lenketekst, anker_) in zip(lista[:4], forventet, strict=True):
            treff = re.fullmatch(r"- (.+): \[([^\]]+)\]\(#([^)]+)\)", linje)
            assert treff, linje
            assert treff.group(1) == forklaring and treff.group(2) == lenketekst, linje
            assert treff.group(3) == anker_, linje
            # Hvert anker finnes én gang (ECH5).
            for anker in [treff.group(3), *re.findall(r"\]\(#([^)]+)\)", treff.group(1))]:
                assert alle.count(anker) == 1, (anker, linje)
        assert _anker("Med Docker Desktop") == "med-docker-desktop"
        assert f'<a name="{DOBBELTKLIKK_ANKER}"></a>\n\n### {DOBBELTKLIKKET}\n' in tekst

    def test_til_faglaerer_lenker_til_briefen_med_gjeldende_tag(self):
        """12.10 kl. 12:12: briefen var gjemt langt nede. Lista under
        «Til faglærer:» lenker til den, og taggen er den CLAUDE.md sier er
        gjeldende (regel 17). Ville feilet med en eldre tag i lista."""
        tekst = README.read_text(encoding="utf-8")
        claude = (ROT / "CLAUDE.md").read_text(encoding="utf-8")
        # Regel 17 kan bryte linja mellom «er nå» og taggen.
        gjeldende = re.findall(r"[Gg]jeldende tag er(?:\s+nå)?\s+`([^`]+)`", claude)[-1]
        lista = tekst.split("Til faglærer:\n", 1)[1].split("\n\n", 1)[0]
        assert all(l.startswith("- ") for l in lista.splitlines()), lista
        brief = [l for l in lista.splitlines() if "](_bmad-output/planning-artifacts/product-brief.md)" in l]
        assert len(brief) == 1, lista
        assert re.findall(r"arbeidskrav-product-brief-v\d+", brief[0]) == [gjeldende], brief[0]


# Story 3.3g: det under «Ekstra», ordene i hvert punkt, i den rekkefoelgen
# README-en har dem. Briefen v8 lover ikke noe av det. Gjennomgangen (BH11,
# VG2, ECH5): alle sakene i punktet, og stammen «signaldag», saa ogsaa
# «signaldager» fanges.
EKSTRA = (
    ("signaldag",),
    ("«vis ki-tekst»",),
    # Story 8.6: børsometeret er flyttet til «Ferdig».
    ("periodevalget", "ki-teksten om dagen"),
    ("velge og bytte aksjer",),
)


def _uten_daterte_linjer(tekst: str) -> str:
    """Teksten uten de daterte linjene (*Lagt til …* og *Rettet …*), som er
    historikk og kan sitere det gamle."""
    return "\n".join(l for l in tekst.splitlines() if not re.match(r"\*(Lagt til|Rettet) ", l))


class TestReadmeDemoenAnbefales:
    """Story 3.3g, punkt d (gruppens svar 19.10 kl. 14:46, 14:48 og 16:12):
    README-en anbefaler demoen for faglaerer og sensor, som briefen v8 og
    tilbakemeldingen 06.10 sier, den lokale modellen er valgfri, og «Neste i
    v1» har bare det briefen lover."""

    def test_kom_i_gang_anbefaler_demoen_for_faglaerer_og_sensor(self):
        """Ville feilet hvis «Vi anbefaler den ekte versjonen» kom tilbake,
        også med en annen ordlyd («Likevel anbefaler vi …», «… anbefales»,
        «Anbefalt» i tabellen), eller hvis «Kom i gang» ikke begynte med
        anbefalingen av demoen (gjennomgangen, ECH1 og ECH2)."""
        tekst = README.read_text(encoding="utf-8")
        foerste = _kom_i_gang().lstrip("\n").split("\n\n", 1)[0]
        anbefalingen = (
            "Vi anbefaler demoen for faglærer og sensor, fordi den ikke trenger nøkkel og viser "
            "hovedfunksjonene med faste eksempeldata, også KI-teksten."
        )
        # Story 3.5g (gruppens svar 26.10 kl. 23:00): «Kom i gang» begynner med
        # én setning, anbefalingen, og resten av avsnittet staar først i pila
        # «Demoen og den ekte versjonen».
        assert foerste == anbefalingen, foerste
        assert _seksjon("Demoen og den ekte versjonen").startswith(
            "Den ekte versjonen er for å prøve løsningen med kurser fra EODHD."
        )
        # «anbefal» står bare i den ene setningen, i hele README-en og i
        # hjelpen. Fra 3.3h også i pila til demoen, og hjelpen har ingen
        # daterte linjer lenger (gjennomgangen av 3.3h, BH12). Story 3.5f:
        # og ved dobbeltklikket i «Velg vei etter hva du har», som veien.
        # Story 3.5g: og i overskriften til dobbeltklikket.
        assert re.findall(r"anbefal\w*", tekst, re.IGNORECASE) == [
            "anbefaler",
            "anbefalt",
            "anbefalt",
            "anbefalt",
        ], re.findall(r"\w*anbefal\w*", tekst)
        assert f"[{DOBBELTKLIKK_LENKE}](#{DOBBELTKLIKK_ANKER}) (anbefalt):" in tekst
        assert '<a name="demoen"></a>Demoen: anbefalt for faglærer og sensor' in tekst
        assert re.search(r"anbefal", _uten_daterte_linjer(_hjelp()), re.IGNORECASE) is None

    def test_ingen_anbefalt_ved_den_ekte_versjonen(self):
        """Ville feilet hvis «(anbefalt)» sto igjen ved den ekte versjonen, i
        overskriften eller tabellen, eller hvis en lenke gikk til det gamle
        ankeret."""
        tekst = README.read_text(encoding="utf-8")
        # Story 3.5f: «(anbefalt)» står bare ved dobbeltklikket, som er veien,
        # ikke versjonen. Story 3.5g: i overskriften og i «Velg vei».
        assert tekst.count("(anbefalt)") == 2
        assert f"\n### {DOBBELTKLIKKET}\n" in tekst
        assert f"[{DOBBELTKLIKK_LENKE}](#{DOBBELTKLIKK_ANKER}) (anbefalt):" in tekst
        # Story 3.3h: pila til den ekte versjonen, med ankeret.
        assert '<summary><a name="den-ekte-versjonen"></a>Den ekte versjonen: ' in tekst
        assert "](#den-ekte-versjonen)" in tekst
        assert _alle_ankrene(tekst).count("den-ekte-versjonen") == 1
        # Gjennomgangen (BH1, ECH4): ingen lenke til det gamle ankeret, heller
        # ikke fra dokumentene, utenom dagsfilene, som lagrer instruksjonene
        # ordrett.
        for sti in [README, *ROT.glob("docs/**/*.md"), *ROT.glob("_bmad-output/**/*.md")]:
            if "ai-prompts" in sti.parts:
                continue
            assert "#den-ekte-versjonen-anbefalt" not in sti.read_text(encoding="utf-8"), sti

    def test_delen_om_den_lokale_modellen_sier_at_den_er_valgfri(self):
        """Ville feilet hvis «valgfri» ble tatt bort fra overskriften eller
        første setning, eller hvis innholdet under falt ut."""
        knappene = _detaljer(_seksjon("Mer for den som vil"))
        modell = [s for s in knappene if s.startswith("Den lokale modellen")]
        assert modell == ["Den lokale modellen for KI-teksten (valgfri)"], list(knappene)
        tekst = knappene[modell[0]]
        assert tekst.startswith(
            "Den lokale modellen er valgfri og trengs verken for demoen eller for å vurdere appen, "
            "fordi demoen har ferdig KI-tekst og bare trenger Docker. "
        ), tekst[:200]
        # Innholdet står.
        assert "docker compose exec ollama ollama pull gemma4:e4b" in tekst
        assert "Slå av KI-teksten: sett `OSE_KI_TJENESTE=av` i `.env`." in tekst

    def test_interesse_handelsvolum_oeverst(self):
        """Ville feilet hvis beskrivelsen øverst sa «interesse» uten
        forklaringen, eller hvis forklaringen sto et annet sted enn i
        beskrivelsen (gjennomgangen, BH7 og VG3)."""
        tekst = README.read_text(encoding="utf-8")
        beskrivelse = [a for a in tekst.split("Til faglærer:", 1)[0].split("\n\n") if a.startswith("OSE Signal viser")]
        assert len(beskrivelse) == 1
        assert "trend, bevegelse og interesse (handelsvolum)" in beskrivelse[0]
        assert tekst.count("(handelsvolum)") == 1

    def test_ingen_av_de_ekstra_staar_under_neste_i_v1(self):
        """Svaret kl. 14:48: det briefen ikke lover, står under «Ekstra,
        hvis tiden rekker». Svaret kl. 16:12: egen nøkkel er v1. Ville feilet
        hvis et ekstra punkt ble flyttet til «Neste i v1», eller NewsWeb kom
        tilbake i punktet om lenkene. Story 8.3: Min liste er flyttet til
        «Ferdig», og «Neste i v1» har de tre som er igjen. Story 10.5: lenken
        til investorsiden er flyttet til «Ferdig», og to står igjen. Story
        2.7b: historikken er flyttet til «Ferdig», og én står igjen. Story
        10.7: egen nøkkel er flyttet til «Ferdig», og README-rettingen står
        igjen (svarene 21.10 kl. 22:51 og 22.10 kl. 00:09)."""
        tekst = README.read_text(encoding="utf-8")
        status = tekst.split("\n## Status\n", 1)[1].split("\n## ", 1)[0]
        lister = _statuslister(status)
        v1 = [p.lower() for p in lister["Neste i v1"]]
        ekstra = [p.lower() for p in lister["Ekstra, hvis tiden rekker"]]
        assert sum("min liste" in p.lower() for p in lister["Ferdig"]) == 1, lister["Ferdig"]
        for saker in EKSTRA:
            for sak in saker:
                assert not any(sak in p for p in v1), (sak, v1)
        assert len(ekstra) == len(EKSTRA), ekstra
        for punkt, saker in zip(ekstra, EKSTRA, strict=True):
            for sak in saker:
                assert sak in punkt, (sak, punkt)
        # Gjennomgangen (BH2, VG1): lenken går til selskapets investorside,
        # som i briefen v8 og story 10.5 etter 06.10.
        for sak in ("prøven av readme-en på en ren maskin",):
            assert sum(sak in p for p in v1) == 1, (sak, v1)
        assert not any("egen nøkkel" in p for p in v1), v1
        assert not any("min liste" in p or "investorside" in p or "historikk" in p for p in v1), v1
        assert sum("lenken til investorsiden" in p.lower() for p in lister["Ferdig"]) == 1, lister["Ferdig"]
        assert len(v1) == 1, v1
        assert "newsweb" not in "\n".join(v1 + ekstra)
        assert REGELEN_FOR_EKSTRA in status


# Story 3.3h (gruppens svar 20.10 kl. 10:14-10:19): det README-en hadde foer
# pilene kom, telt i README-en paa main foer grenen (013be41). Stegene med
# tittelen i fet skrift, eller hele linja i lista for uv, kommandoene i
# boksene uten spraak og maalene for lenkene, med antallet.
# Story 3.5g (gruppens svar 26.10 kl. 23:00): de fem nummererte stegene i
# dobbeltklikket, med tittelen i fet skrift.
STEGENE_I_DOBBELTKLIKKET = (
    "1. **Last ned koden**",
    "2. **Pakk ut.**",
    "3. **Åpne `G74-lund-osen-main` og dobbeltklikk «Start demoen».**",
    "4. **Svar `j`**",
    "5. **Lukk vinduet**",
)
STEGENE_FOER_3_3H = (
    "1. **Installer og start Docker Desktop**",
    "2. **Last ned koden.**",
    "3. **Åpne PowerShell**",
    "4. **Skriv `cd` og et mellomrom**",
    "5. **Start demoen.**",
    "6. **Åpne http://127.0.0.1:8000**",
    "7. **Stopp**",
    "5. **Hent en nøkkel.**",
    "6. **Legg inn nøkkelen, bare første gang.**",
    "7. **Start appen.**",
    "8. **Hent kursene**",
    "9. **Stopp**",
    "1. Installer avhengighetene:",
    "2. Lag demobasen, `data/db/demo.db`:",
    "3. Start demoen på http://127.0.0.1:8000:",
    "1. Bare første gang: kopier malen, og fyll inn `EODHD_API_KEY` i `.env`:",
    "2. Hent kurser:",
    "3. Start webserveren på http://127.0.0.1:8000:",
)
KOMMANDOENE_FOER_3_3H = {
    "docker compose up --build demo": 2,
    "docker compose --profile demo down": 2,
    "cp .env.example .env": 2,
    "notepad .env": 1,
    "open -e .env": 1,
    "docker compose up --build": 2,
    "docker compose run --rm hent": 1,
    "docker compose down": 1,
    "uv sync": 2,
    "uv run python src/demo.py": 1,
    "uv run python src/app.py --demo": 1,
    "uv run python src/fetch_prices.py": 1,
    "uv run python src/app.py": 1,
    "docker compose --profile ki up -d ollama": 2,
    "docker compose exec ollama ollama pull gemma4:e4b": 1,
    "docker compose --profile ki down": 1,
    'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"': 1,
    "curl -LsSf https://astral.sh/uv/install.sh | sh": 1,
    "uv run pytest": 1,
}
LENKENE_FOER_3_3H = {
    "https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml/badge.svg": 1,
    "https://github.com/IBE160-2026/G74-lund-osen/actions/workflows/tester.yml": 1,
    "docs/appen/oversikten-demo.png": 2,
    # Story 10.2e (svaret 24.10 kl. 23:23, b): bildet viser BRFE. Var KVST.
    "docs/appen/aksjesiden-brfe-demo.png": 2,
    "#kom-i-gang": 1,
    "#status": 1,
    "#tester": 3,
    "#dokumentene": 1,
    "#mappestruktur": 1,
    "#medlemmer": 1,
    # Story 3.5f: «Felles for begge» heter «Med Docker Desktop».
    "#med-docker-desktop": 1,
    "#demoen": 1,
    "#den-ekte-versjonen": 1,
    "_bmad-output/planning-artifacts/product-brief.md": 2,
    "_bmad-output/planning-artifacts/tilbakemelding-product-brief.md": 2,
    "_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md": 1,
    "_bmad-output/planning-artifacts/architecture/architecture-G74-lund-osen-2026-09-22/ARCHITECTURE-SPINE.md": 2,
    "_bmad-output/planning-artifacts/epics.md": 3,
    "docs/innlevering.md": 2,
    "docs/kvalitetssikring.md": 3,
    "docs/reflection-log.md": 2,
    "docs/ai-prompts/": 2,
    "docs/vurderingsmatrise.md": 2,
    "https://docs.astral.sh/uv/": 3,
    "#står-du-fast": 1,
    "https://www.docker.com/products/docker-desktop/": 1,
    "docs/bilder/readme/engine-running.png": 2,
    "https://github.com/IBE160-2026/G74-lund-osen": 1,
    "docs/bilder/readme/github-download-zip.png": 2,
    "docs/hjelp.md#står-det-zip-til-slutt-i-linja": 1,
    "docs/bilder/readme/powershell-mappa.png": 2,
    "https://eodhd.com/register": 1,
    "#mer-for-den-som-vil": 1,
    "docs/hjelp.md": 3,
    "_bmad-output/implementation-artifacts/sprint-status.yaml": 1,
    "https://docs.astral.sh/uv/getting-started/installation/": 1,
    "_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/": 1,
    "_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/relevanseksperiment.md": 1,
    "_bmad-output/planning-artifacts/designregler.md": 1,
    "_bmad-output/planning-artifacts/designutdrag-2026-10-13.md": 1,
    "_bmad-output/planning-artifacts/sprint-change-proposal-2026-09-28.md": 1,
    "_bmad-output/planning-artifacts/sprint-change-proposal-2026-10-08.md": 1,
    "_bmad-output/planning-artifacts/sprint-change-proposal-2026-10-13.md": 1,
    "_bmad-output/planning-artifacts/sprint-change-proposal-2026-10-19.md": 1,
    "docs/kilder-og-rettigheter.md": 1,
    "docs/epost-til-eodhd.md": 1,
    "docs/epost-til-euronext.md": 1,
    "_bmad-output/implementation-artifacts/": 1,
    "docs/ux-logg.md": 1,
    "docs/kontroll-2026-09-22.md": 1,
    "docs/kontroll-2026-09-22-plan.md": 1,
    "docs/kontroll-2026-09-26.md": 1,
    "src/": 1,
    "tests/": 1,
    "docs/": 1,
    "docs/bilder/readme/": 1,
    "docs/appen/": 1,
    "_bmad-output/": 1,
    ".github/": 1,
    "Dockerfile": 1,
    "compose.yaml": 1,
    ".dockerignore": 1,
    "_bmad/": 1,
    ".claude/skills/": 1,
}

# Gjennomgangen av 3.3h (ECH2): sha256 av innholdet i hver pil, det samme
# som delen under overskriften paa main foer grenen (013be41).
# Story 3.3i (U55): den ekte versjonen fikk avsnittet om at appen er gratis,
# og hva gratiskontoen og et betalt abonnement hos EODHD gir, foer steg 5.
# Stegene staar uendret. Var fd359e96... (spesifikasjonen 3.3i).
# Gjennomgangen av 3.3i: demoen sier i steg 6 at demolinja har en lenke til
# den ekte versjonen (VG8), og pila til den ekte versjonen at de 4 kallene som
# er igjen, gaar til nye forsoek (BH5). Var b3f50242... og 36cc2505....
# Story 2.3c: steg 8 sier at foerste henting gaar naar som helst, og at den
# foer kl. 22 en boersdag gir forrige boersdag. Var 542c8991....
# Story 8.1 (instruksjonen 23.10 kl. 14:38, gruppens svar kl. 15:52): lenken
# til skjemaet docs/brukertest.md i «Dokumentene» (regel 19). Var d05514d3....
# Story 3.5a: start/ og .gitattributes i «Mappestruktur» (regel 19). Var
# d157a170....
# Story 3.4 (godkjent 24.10 kl. 13:43): docs/bilder/investorsider/ i
# «Mappestruktur» (regel 19). Var 0d1a51a6....
# Story 10.2e (gruppens svar 24.10 kl. 23:23, b): bildet av aksjesiden i
# «Mappestruktur» er BRFE (regel 19). Var 852cb13b....
# Story 3.5f: hver fil og mappe i rota i «Mappestruktur» (regel 19). Var
# 7ed8bbe8....
# Gruppens svar 27.10 kl. 06:31: .logs/ og skillen sesjonslogg fra faglærer
# i «Mappestruktur» (regel 19). Var a363fbd7....
# Story 2.3d: jobben som henter hver kveld i punktet om start/ i
# «Mappestruktur» (regel 19). Var 0fe44843....
AVTRYKK_I_PILENE = {
    "Demoen": "f124a92b1c64eeb0ea5e7141976ff85de68df49004a22d5874a4a257aaf89b55",
    "Den ekte versjonen": "3bb398cd1be31a43abe09b7261456646b6dc03047e20f1aa57ab665a768cfd78",
    "Dokumentene": "409a3f8b38d4247df41e3eb5062ad439aa160e7fd1c0b49e0fd44f262eb2d77c",
    "Mappestruktur": "677fa094d2584edaa15eb9e156e7905b6679565e319717eb9cf19f4058ce53cd",
}

# Story 3.5g (gruppens svar 26.10 kl. 23:00): sha256 av innholdet i de nye
# pilene i «Kom i gang». «Du trenger», «Uten Docker, med uv», «Slik virker
# dobbeltklikket» og «Står du fast?» er det samme som delen under
# overskriften (eller avsnittet «Du trenger») på main foer grenen (54d4714),
# byte for byte, regnet av `git show 54d4714:README.md` (spesifikasjonen
# 3.5g). «Demoen og den ekte versjonen» er resten av det foerste avsnittet,
# tabellen og «Velg vei», der lenketeksten til dobbeltklikket er «Enklest:
# dobbeltklikk», uv ikke lenger staar «under «Mer for den som vil»», og
# demoen staar først «i stegene for Docker og uv», ikke «i stegene under».
# «Med Docker Desktop» var også lik til gjennomgangen av 3.5g (BH2, ECH6,
# VG4): «Tabellen over» er «Tabellen i pila «Demoen og den ekte versjonen»».
# Var 386c91b5... og dc27ef47.... Pilene til demoen og den ekte versjonen
# har sine avtrykk i AVTRYKK_I_PILENE, uendret. Gruppens svar 27.10 kl.
# 06:09, b (ECH7): hver henvisning til et steg i «Står du fast?» sier at den
# gjelder Docker, som «steg 4 med Docker». Var 26143167.... Svarene 28.10
# kl. 11:19 og 11:23 (e): tabellen er tatt ut av pila «Demoen og den ekte
# versjonen» og står øverst, og pila til Docker lenker dit. Var d9bc0617...
# og 44485fc5....
AVTRYKK_I_KOM_I_GANG = {
    "Demoen og den ekte versjonen": "aa69940997c10246503b38bad1da10dc53afea965745fefbd33e75eaea4e23b4",
    "Du trenger": "edb9feeacf0f246bf416ab859f08e196d6ec92a0a44e8da9e371325c9680917b",
    "Med Docker Desktop": "bed9f253f46f680c10ff969a60a0e2ce0508da9bcec668598c343994331c3453",
    "Uten Docker, med uv": "2efeb5262b38f15a7fa04bc9715e149cbd053c7c45c193c9e0c048bab02dfc13",
    "Slik virker dobbeltklikket": "9066cc123fbc8efda0833fefdadec7f4f6fe039909f3bfaa498db2748b022d80",
    "Står du fast?": "c75b3ea0c4d84655d313b1002cf5845f2321e140fd737a8ac9df20d0de68c2ea",
}

# Svaret 20.10 kl. 20:20: advarselen staar rett under pila til den ekte
# versjonen, uendret fra 22:32.
ADVARSELEN_MOT_DOWN_V = "**Skriv aldri `docker compose down -v`.** Det sletter kursene og vurderingene, og vurderingene kan ikke lages på nytt."

# Paa GitHub vises markdown i en pil bare med en tom linje etter </summary>
# og foer </details>. <summary> staar paa linja under <details>, paa én linje,
# uten markdown, som GitHub ikke viser der.
PIL = re.compile(r"^<details>\n<summary>([^\n]+)</summary>\n\n(.*?)\n\n</details>$", re.MULTILINE | re.DOTALL)


def _utenfor_pilene(tekst: str) -> str:
    """Teksten med hver pil tatt bort, slik den synes foer noe er åpnet. Fra
    3.5g kan en pil ha piler inni, saa </details> telles mot <details>."""
    synlig, dybde = [], 0
    for linje in tekst.split("\n"):
        if linje == "<details>":
            dybde += 1
        elif linje == "</details>":
            dybde -= 1
            # Gjennomgangen av 3.5g (BH9, ECH9): en </details> uten par.
            assert dybde >= 0, "</details> uten <details>"
        elif dybde == 0:
            synlig.append(linje)
    assert dybde == 0, "<details> uten </details>"
    return "\n".join(synlig)


def _seksjonen(tekst: str, overskrift: str) -> str:
    return tekst.split(f"\n## {overskrift}\n", 1)[1].split("\n## ", 1)[0]


class TestReadmeBakPiler:
    """Story 3.3h (gruppens svar 20.10 kl. 10:14, 10:15, 10:18 og 10:19, og
    kl. 16:19): README-en er kortere å lese, med mer bak en pil, og
    docs/hjelp.md er et levende dokument."""

    def test_demoen_den_ekte_versjonen_dokumentlista_og_mappestrukturen_bak_hver_sin_pil(self):
        """Ville feilet hvis demoen, den ekte versjonen, dokumentlista eller
        mappestrukturen sto åpent, eller hvis overskriften til dokumentlista
        eller mappestrukturen sto inne i pila."""
        tekst = README.read_text(encoding="utf-8")
        synlig = _utenfor_pilene(tekst)
        for navn in PILENE:
            innhold = _pil(navn)
            assert innhold and innhold not in synlig, navn
        assert "**Start demoen.**" not in synlig and "**Hent en nøkkel.**" not in synlig
        for overskrift, summary in (
            ("Dokumentene", "Dokumentlista: plan og krav, arbeidsprosess og kvalitet"),
            ("Mappestruktur", "Mappene og filene i repoet"),
        ):
            assert f"\n## {overskrift}\n" in synlig, overskrift
            seksjon = _seksjonen(tekst, overskrift).strip("\n")
            treff = PIL.fullmatch(seksjon)
            assert treff, overskrift
            assert treff.group(1) == summary, treff.group(1)
        assert "**Plan og krav**" not in synlig and "[`src/`](src/)" not in synlig
        # «Velg vei» står rett etter de felles stegene og sier hvor forskjellen står.
        # Story 3.5g: i pila til Docker, ikke synlig.
        # Gjennomgangen av 3.5g (BH2, ECH6, VG4): tabellen står i en annen pil.
        # Svarene 28.10 kl. 11:19 og 11:23 (e): tabellen står øverst.
        velg = (
            f"{VELG_VEI} Klikk på pila for den versjonen du vil prøve. [Tabellen «Demoen og den ekte "
            "versjonen»](#demoen-og-den-ekte-versjonen) øverst viser forskjellen."
        )
        assert velg in dict(_pilene(_kom_i_gang()))["Med Docker Desktop"] and velg not in synlig

    def test_innholdet_i_pilene_er_det_samme_som_foer(self):
        """Gjennomgangen av 3.3h (ECH2, BH5): stegene, bildene og advarselen
        står uendret i pilene. Ville feilet hvis en setning i demoen, den
        ekte versjonen, dokumentlista eller mappestrukturen ble endret eller
        tatt bort, eller et steg ble flyttet til den andre pila. Avtrykket er
        sha256 av delen under overskriften på main foer grenen (013be41), for
        demoen uten linja om den ekte versjonen, som fikk lenken. Fra svaret
        20.10 kl. 20:20 står advarselen mot down -v rett under pila til den
        ekte versjonen, så den regnes med etter pila. Endres innholdet
        senere, settes avtrykket på nytt i samme commit."""
        import hashlib

        tekst = README.read_text(encoding="utf-8")
        innhold = {
            "Demoen": _pil("Demoen").rsplit("\n\n", 1)[0],
            "Den ekte versjonen": _pil("Den ekte versjonen") + "\n\n" + ADVARSELEN_MOT_DOWN_V,
            "Dokumentene": PIL.fullmatch(_seksjonen(tekst, "Dokumentene").strip("\n")).group(2),
            "Mappestruktur": PIL.fullmatch(_seksjonen(tekst, "Mappestruktur").strip("\n")).group(2),
        }
        avtrykk = {navn: hashlib.sha256(del_.encode("utf-8")).hexdigest() for navn, del_ in innhold.items()}
        assert avtrykk == AVTRYKK_I_PILENE, avtrykk

    def test_det_som_er_flyttet_bak_pilene_er_det_samme_som_foer(self):
        """Story 3.5g: teksten er flyttet bak pilene, ikke skrevet om. Ville
        feilet hvis en setning, et steg, et bilde, en kommando eller et
        spørsmål i en av pilene ble endret eller tatt bort. Endres innholdet
        senere, settes avtrykket på nytt i samme commit."""
        import hashlib

        pilene = dict(_pilene(_kom_i_gang()))
        avtrykk = {navn: hashlib.sha256(pilene[navn].encode("utf-8")).hexdigest() for navn in AVTRYKK_I_KOM_I_GANG}
        assert avtrykk == AVTRYKK_I_KOM_I_GANG, avtrykk

    def test_de_felles_stegene_staar_ikke_bak_en_pil(self):
        """Ville feilet hvis de felles stegene 1–4, bildene eller avsnittet
        om å lime inn sto bak en pil.

        Story 3.5g (gruppens svar 26.10 kl. 23:00): de står samlet bak pila
        «Med Docker Desktop», og ingen av dem synes før den er åpnet. Navnet
        står, fordi kvalitetssikringen nevner testen (M1 i 3.3h). Ville
        feilet hvis et av stegene, et bilde eller avsnittet om å lime inn sto
        utenfor pila, eller pila hadde en annen pil inni."""
        synlig = _utenfor_pilene(_kom_i_gang())
        docker = dict(_pilene(_kom_i_gang()))["Med Docker Desktop"]
        assert "<details>" not in docker
        assert '<summary><a name="med-docker-desktop"></a>Med Docker Desktop</summary>' in _kom_i_gang()
        for steg in STEGENE_FOER_3_3H[:4]:
            assert f"\n{steg}" in "\n" + docker and steg not in synlig, steg
        for bilde in BILDENE.values():
            assert f"docs/bilder/readme/{bilde})" in docker and bilde not in synlig, bilde
        for avsnitt in (KOPIERINGEN, VELG_VEI):
            assert avsnitt in docker and avsnitt not in synlig, avsnitt

    def test_ferdig_begynner_med_signalet(self):
        """Rådets funn 20.10: «Ferdig» manglet selve signalet. Ville feilet
        hvis det første punktet ikke nevnte de tre sjekkene trend, bevegelse
        og interesse, styrken for hver aksje hver børsdag og
        regelforklaringen på aksjesiden, eller hvis demolinja ikke sa «av de
        tre sjekkene». Ordene er de koden bruker: sjekkene i aksjedetalj.py og
        «Signalstyrke» og regelforklaringen på aksjesiden."""
        status = _seksjonen(README.read_text(encoding="utf-8"), "Status")
        ferdig = _statuslister(status)["Ferdig"]
        foerste = ferdig[0].lower()
        for ord_ in ("de tre sjekkene", "trend", "bevegelse", "interesse", "styrken for hver aksje", "hver børsdag"):
            assert ord_ in foerste, ord_
        assert "regelforklaringen på aksjesiden" in foerste
        assert any("demoen med alle 10 fargekombinasjonene av de tre sjekkene" in p for p in ferdig), ferdig
        aksjedetalj = (ROT / "src" / "aksjedetalj.py").read_text(encoding="utf-8")
        for navn in ("Trend", "Bevegelse", "Interesse"):
            assert f'"{navn}": f"' in aksjedetalj, navn
        mal = (ROT / "src" / "templates" / "aksje.html").read_text(encoding="utf-8")
        assert "Signalstyrke" in mal and "Regelforklaringen" in mal

    def test_pila_til_demoen_sier_at_den_er_anbefalt_for_faglaerer_og_sensor(self):
        """Svaret 19.10 kl. 14:46. Ville feilet hvis «anbefalt» falt ut av pila
        til demoen, eller kom i pila til den ekte versjonen."""
        tekst = _kom_i_gang()
        # Story 3.5g: «Står du fast?» har piler inni, så summary leses linje
        # for linje.
        pilene = {
            re.sub(ANKER_I_PIL, "", s): (re.search(ANKER_I_PIL, s) or [None, None])[1]
            for s in re.findall(r"^<summary>(.+)</summary>$", tekst, re.MULTILINE)
        }
        assert pilene.get("Demoen: anbefalt for faglærer og sensor, uten nøkkel") == "demoen", pilene
        assert pilene.get("Den ekte versjonen: kurser fra EODHD, med egen nøkkel") == "den-ekte-versjonen", pilene
        assert "anbefal" not in _pil("Den ekte versjonen").lower()

    def test_under_tester_staar_kommandoene_og_lenken_synlig(self):
        """Ville feilet hvis uv sync, uv run pytest eller lenken til
        kvalitetssikringen sto bak en pil, eller installasjonen av uv sto
        åpent."""
        tester = _seksjonen(README.read_text(encoding="utf-8"), "Tester")
        synlig = _utenfor_pilene(tester)
        assert [b.strip() for _, b in _blokkene(synlig)] == ["uv sync", "uv run pytest"]
        assert "[`docs/kvalitetssikring.md`](docs/kvalitetssikring.md)" in synlig
        for punkt in ("- Ingen nettkall:", "- `data/` røres ikke:", "- CI kjører", "- ruff kjøres før en commit:"):
            assert punkt in synlig, punkt
        uv = _detaljer(tester)[UV_PILA]
        for innhold in (UV_WINDOWS, UV_MAC, "«The term 'uv' is not recognized»", "**På en ren maskin uten Docker**"):
            assert innhold in uv and innhold not in synlig, innhold
        assert tester.index("bak pila under") < tester.index(UV_PILA) < tester.index("```\nuv sync\n```")

    def test_hvert_steg_hver_kommando_og_hver_lenke_fra_foer_finnes(self):
        """Ville feilet hvis et steg, en kommando eller en lenke fra
        README-en foer pilene falt ut, i pilene eller utenfor dem."""
        from collections import Counter

        tekst = README.read_text(encoding="utf-8")
        steg = []
        for linje in re.findall(r"^\d+\. .*$", tekst, re.MULTILINE):
            tittel = re.match(r"^(\d+\. \*\*[^*]+\*\*)", linje)
            steg.append(tittel.group(1) if tittel else linje)
        # Story 3.5g: de fem stegene i dobbeltklikket står først.
        assert steg == [*STEGENE_I_DOBBELTKLIKKET, *STEGENE_FOER_3_3H], steg
        kommandoer = Counter(b.strip() for spraak, b in _blokkene(tekst) if not spraak)
        assert not Counter(KOMMANDOENE_FOER_3_3H) - kommandoer, Counter(KOMMANDOENE_FOER_3_3H) - kommandoer
        lenker = Counter(re.findall(r"\]\(([^)\s]+)\)", tekst))
        assert not Counter(LENKENE_FOER_3_3H) - lenker, Counter(LENKENE_FOER_3_3H) - lenker
        # Ankrene lenkene går til, finnes én gang.
        alle = _alle_ankrene(tekst)
        for maal in LENKENE_FOER_3_3H:
            if maal.startswith("#"):
                assert alle.count(maal[1:]) == 1, maal

    def test_hjelpen_sier_klokkeslettet_fra_tidsgrensen_og_har_ingen_daterte_linjer(self):
        """Gruppens svar kl. 16:19: hjelpen rettes der teksten står, og
        historikken ligger i git. Ville feilet med en linje som begynner med
        *Rettet eller *Lagt til, eller hvis svaret om når man kan hente, sa
        en annen time enn TIDSGRENSE."""
        import fetch_prices

        hjelp = _hjelp()
        # Gjennomgangen av 3.3h (ECH5): også de andre formene repoet bruker.
        daterte = re.findall(
            r"^\s*[*_]+(?:Rettet|Lagt til|Avgjort|Presisert|Skrevet|Ferdig)\b.*$", hjelp, re.MULTILINE | re.IGNORECASE
        )
        assert not daterte, daterte
        grense = fetch_prices.TIDSGRENSE
        svar = hjelp.split("### Når kan jeg hente?\n\n", 1)[1].split("\n### ", 1)[0]
        assert svar.startswith(f"Hent etter kl. {grense.hour} og før midnatt på en børsdag.")
        timer = set(re.findall(r"\bkl\. (\d{1,2})\b(?![:.]\d)", svar))
        assert timer == {str(grense.hour)}, timer

    def test_markdown_inne_i_pilene_vises_riktig_paa_github(self):
        """Ville feilet hvis en pil i README-en eller docs/hjelp.md manglet
        den tomme linja etter </summary> eller foer </details>, hadde
        <summary> på flere linjer eller med markdown, lå inni en annen pil,
        eller hadde en boks som ikke var lukket.

        Story 3.5g (gruppens svar 26.10 kl. 23:00): «Står du fast?» står bak
        en pil, med pilene til spørsmålene inni. Det er den eneste pila som
        kan ha piler inni, og bare ett nivå. Ville feilet med en pil inni en
        annen pil et annet sted, eller to nivåer inni «Står du fast?»."""
        for navn, tekst in (("README.md", README.read_text(encoding="utf-8")), ("docs/hjelp.md", _hjelp())):
            aapne = re.findall(r"<details\b", tekst)
            assert len(aapne) == tekst.count("</details>") == tekst.count("<summary>"), (navn, len(aapne))
            hele = []
            for summary, innhold in _pilene(tekst):
                hele.append((summary, innhold))
                if "<details" in innhold:
                    assert (navn, summary) == ("README.md", "Står du fast?"), (navn, summary)
                    indre = _pilene(innhold)
                    assert indre and all("<details" not in i for _, i in indre), summary
                    hele += indre
            assert len(hele) == len(aapne), (navn, len(hele), len(aapne))
            for summary, innhold in hele:
                assert not re.search(r"[*_`]|\]\(", re.sub(ANKER_I_PIL, "", summary)), (navn, summary)
                assert len(re.findall(r"^```", innhold, re.MULTILINE)) % 2 == 0, (navn, summary)
                # Fire mellomrom foran gjør en linje til kode på GitHub.
                assert not re.search(r"^ {4,}\S", _uten_bokser(innhold), re.MULTILINE), (navn, summary)
            # <details> og </details> står alene på linja.
            for linje in tekst.splitlines():
                if "details>" in linje:
                    assert linje in ("<details>", "</details>"), (navn, linje)


class TestReadmeEtterDemoen:
    """Story 3.3i: README-rettingen etter gruppens gjennomgang av demoen
    21.10 (U13 og U55 i docs/ux-logg.md)."""

    SPOERSMAALET = "Nettleseren sier at 127.0.0.1 nektet å koble til."

    def test_err_connection_refused_under_staar_du_fast(self):
        """U13: meldingen fra nettleseren står ordrett, så den kan søkes opp.
        Ville feilet hvis spørsmålet falt ut av «Står du fast?», eller
        meldingen falt ut av svaret i README-en eller i docs/hjelp.md."""
        svar = _detaljer(_faq())
        assert self.SPOERSMAALET in svar, list(svar)
        assert "`ERR_CONNECTION_REFUSED`" in svar[self.SPOERSMAALET]
        assert "«Serving on»" in svar[self.SPOERSMAALET]
        i_hjelp = _hjelp().split(f"### {self.SPOERSMAALET}\n\n", 1)[1].split("\n\n### ", 1)[0]
        assert "`ERR_CONNECTION_REFUSED`" in i_hjelp

    def test_tallene_20_og_16_stemmer_med_koden(self, tmp_path):
        """U55: kallene i døgnet og kallene per henting, slik README-en sier
        dem i pila til den ekte versjonen. 16 er kallene en henting gjør mot
        en falsk EODHD, og 20 er tallet øverst i fetch_prices.py, som med 16
        gir de kallene til nye forsøk som docs/hjelp.md sier. Ville feilet
        hvis README-en sa 15 kall per henting, eller et annet tall enn koden."""
        import fetch_prices as fp
        from kursdata import AKSJEUNIVERS
        from test_ki_tekst import kjoer

        pila = re.sub(r"\s+", " ", _pil("Den ekte versjonen"))
        treff = re.search(r"gir (\d+) kall i døgnet og kurser ett år tilbake, og en henting bruker (\d+):", pila)
        assert treff, pila[:300]
        i_doegnet, per_henting = int(treff.group(1)), int(treff.group(2))
        assert f"appen bruker ikke flere enn {per_henting} per henting" in pila
        _, kall, _ = kjoer(tmp_path / "raa", tmp_path / "db" / "ose.db", None)
        assert per_henting == len(kall) == len(AKSJEUNIVERS) + 1
        assert i_doegnet == int(re.search(r"Gratisnivaaet gir (\d+) kall i doegnet", fp.__doc__).group(1))
        hjelp = re.sub(r"\s+", " ", _hjelp())
        til_overs, aksjer = map(int, re.search(r"altså (\d+) med de (\d+)", hjelp).groups())
        assert aksjer == len(AKSJEUNIVERS)
        assert f"og de {til_overs} som er igjen, går til nye forsøk samme kveld" in pila
        assert fp.kall_til_nye_forsoek(i_doegnet, i_doegnet, per_henting) == til_overs


class TestFemSpoersmaal:
    """Story 3.3j (gruppens svar 22.10 kl. 17:42): de to svarene om cd i
    steg 4 er ett spoersmaal, med begge meldingene ordrett, saa «Står du
    fast?» har fem spoersmaal. Grensen paa 5 staar i
    test_staar_du_fast_har_hoeyst_5_spoersmaal (gjennomgangen, BH5)."""

    MELDINGENE = ("«is not recognized as the name of a cmdlet»", "«Cannot find path … because it does not exist»")
    # Gjennomgangen (ECH2): uten anfoerselstegn, saa en gammel overskrift i
    # en annen form ogsaa fanges. «The term 'uv' is not recognized» er sitt eget.
    BARE_ORDENE = ("is not recognized as the name of a cmdlet", "Cannot find path")

    def test_begge_meldingene_i_samme_spoersmaal(self):
        """Ville feilet hvis en av meldingene falt ut av spoersmaalet (M2),
        sto i et eget spoersmaal, eller ikke hadde sitt svar under det."""
        svar = _detaljer(_faq())
        med = [s for s in svar if any(m in s for m in self.MELDINGENE)]
        assert med == [CD_SPOERSMAALET], med
        for melding in self.MELDINGENE:
            assert melding in CD_SPOERSMAALET, melding
            assert f"Kommer {melding}: " in svar[CD_SPOERSMAALET], melding

    def test_det_samme_spoersmaalet_i_hjelpen(self):
        """Ville feilet hvis docs/hjelp.md fortsatt hadde de to som hvert sitt
        spoersmaal, ogsaa i en annen form, det nye sto utenfor «Steg 4:
        mappa», eller et av svarene manglet under det (BH4, ECH2)."""
        steg4 = _hjelp().split("\n## Steg 4: mappa\n", 1)[1].split("\n## ", 1)[0]
        overskrifter = re.findall(r"^### (.+)$", _hjelp(), re.MULTILINE)
        med = [o for o in overskrifter if any(m in o for m in self.BARE_ORDENE)]
        assert med == [CD_SPOERSMAALET], med
        assert f"### {CD_SPOERSMAALET}\n" in steg4
        under = steg4.split(f"### {CD_SPOERSMAALET}\n\n", 1)[1].split("\n### ", 1)[0]
        for melding in self.MELDINGENE:
            assert f"Kommer {melding}: " in under, melding


def _velg_vei() -> list[tuple[str, str, str]]:
    """Punktene under «Velg vei etter hva du har» som (lenketekst, anker,
    resten av linja)."""
    del_ = _kom_i_gang().split("\n**Velg vei etter hva du har:**\n\n", 1)[1].split("\n\n", 1)[0]
    punkter = []
    for linje in del_.splitlines():
        treff = re.fullmatch(r"- \[([^\]]+)\]\(#([^)]+)\)(.*)", linje)
        assert treff, linje
        punkter.append(treff.groups())
    return punkter


def _dobbeltklikket() -> str:
    """Delen «Enklest: dobbeltklikk (anbefalt)» i «Kom i gang», til den
    første pila. Het «Enklest: dobbeltklikk, uten Docker» til 3.5g."""
    return _seksjon(DOBBELTKLIKKET)


def _ord(tekst: str) -> int:
    """Ordene slik leseren ser dem, med lenketeksten og uten adressen bak
    (svaret 13.10 kl. 23:50)."""
    return len(re.findall(r"\w+", re.sub(r"\]\([^)]*\)", "]", tekst)))


LINUX_LINJA = "**Linux:** bruk [Docker](#med-docker-desktop) eller [uv](#uten-docker-med-uv), under."


class TestHovedveien:
    """Story 3.5f (gruppens svar 25.10 kl. 11:32 og innspillet kl. 11:26):
    dobbeltklikket er den anbefalte hovedveien og en egen del foerst i «Kom i
    gang», Docker den andre og uv i terminalen den tredje. Story 3.5g
    (gruppens svar 26.10 kl. 23:00): dobbeltklikket er fem korte nummererte
    steg, og resten står bak piler."""

    def test_dobbeltklikket_staar_foerst_og_ikke_bak_en_pil(self):
        """Story 3.5g: «Kom i gang» er én setning, overskriften med ankeret
        fra før, de fem stegene, linja om advarselen, linja om den ekte
        versjonen og linja om Linux (gruppens svar 27.10 kl. 06:09, a), og så
        pilene i rekkefølgen i instruksjonen. Ville feilet
        hvis stegene ikke sto først, et steg manglet, sto i en annen
        rekkefølge eller hadde mer enn 25 ord, noe annet sto synlig før
        pilene, en pil manglet eller sto i en annen rekkefølge, eller
        dobbeltklikket sto igjen under «Mer for den som vil»."""
        del_ = _kom_i_gang()
        overskrifter = re.findall(r"^### (.+)$", _utenfor_pilene(del_), re.MULTILINE)
        assert overskrifter == [DOBBELTKLIKKET, "Mer for den som vil"], overskrifter
        foer = del_.split("\n<details>\n", 1)[0].strip("\n")
        avsnitt = [a for a in foer.split("\n\n") if a.strip()]
        assert len(avsnitt) == 7, avsnitt
        anbefalingen, anker, overskrift, stegene, advarselen, ekte, linux = avsnitt
        assert anbefalingen.startswith("Vi anbefaler demoen for faglærer og sensor") and "\n" not in anbefalingen
        assert len(re.findall(r"[.!?](?:\s|$)", anbefalingen)) == 1, anbefalingen
        assert anker == f'<a name="{DOBBELTKLIKK_ANKER}"></a>' and overskrift == f"### {DOBBELTKLIKKET}"
        linjene = stegene.splitlines()
        assert [int(re.match(r"(\d+)\. ", l).group(1)) for l in linjene] == [1, 2, 3, 4, 5], linjene
        for linje, tittel in zip(linjene, STEGENE_I_DOBBELTKLIKKET, strict=True):
            assert linje.startswith(tittel), (linje, tittel)
            assert _ord(linje.split(". ", 1)[1]) <= 25, linje
        steg = dict(zip(range(1, 6), linjene))
        assert f"[den direkte lenken]({ZIP_LENKEN})" in steg[1]
        assert "«Pakk ut alle»" in steg[2] and "Mac: dobbeltklikk fila" in steg[2]
        assert "`G74-lund-osen-main`" in steg[3] and "«Start demoen»" in steg[3] and "innerste" in steg[3]
        # Gjennomgangen av 3.5g (BH14, ECH2, ECH3, VG3): de vanligste feilene
        # står synlig: å starte inne i ZIP-fila og å ta .command på Windows.
        assert "Ikke start fra inne i ZIP-fila." in steg[2]
        assert "På Windows: den uten `.command`." in steg[3]
        assert "`j`" in steg[4] and "uv" in steg[4] and "Nettleseren åpner appen" in steg[4]
        assert "**Lukk vinduet**" in steg[5] and "stoppe" in steg[5]
        # Linja om advarselen lenker til svarene for Windows og Mac.
        assert advarselen.startswith("**Første gang**") and "\n" not in advarselen
        hjelp = _ankrene(_hjelp())
        lenkene = re.findall(r"\[([^\]]+)\]\(docs/hjelp\.md#([^)]+)\)", advarselen)
        assert lenkene == [("Windows", "windows-advarer-mot-fila"), ("Mac", "mac-sier-at-fila-ikke-kan-åpnes")]
        for _, maal in lenkene:
            assert maal in hjelp, maal
        assert ekte.startswith("**Ekte kurser:**") and "«Start den ekte versjonen»" in ekte and "\n" not in ekte
        assert "nøkkel fra EODHD" in ekte
        # Gjennomgangen av 3.5g (BH5, ECH4): vernet mot .git står synlig.
        assert "bare i en kopi fra ZIP-fila, ikke i en klon" in ekte
        assert linux == LINUX_LINJA
        assert [s for s, _ in _pilene(del_)][: len(PILENE_I_KOM_I_GANG)] == list(PILENE_I_KOM_I_GANG)
        assert not any("dobbeltklikk" in s.lower() for s in _detaljer(_seksjon("Mer for den som vil")))

    def test_tabellen_staar_uten_pil_foer_til_faglaerer(self):
        """Gruppens svar 28.10 kl. 11:19 og 11:23 (e): veiene står hver for
        seg, som i 3.5g, men tabellen «Demoen og den ekte versjonen» står
        uten pil under «Innhold», før «Til faglærer», så de to versjonene og
        hva som er laget, synes med en gang. Svaret kl. 11:23 gjelder, ikke
        «etter stegene» kl. 11:19. Ville feilet hvis tabellen sto bak en pil,
        sto etter «Til faglærer» eller etter stegene, sto to ganger, manglet
        en rad, eller hvis lenken fra pila til Docker ikke gikk til den."""
        tekst = README.read_text(encoding="utf-8")
        tabellen = _tabellen()
        rader = [l.split(" | ", 1)[0] for l in tabellen.splitlines() if l.startswith("| ")]
        assert rader == ["|", "| Kurser", "| Trenger", "| Klar"], rader
        assert tabellen.splitlines()[0] == "| | Demoen | Den ekte versjonen |"
        # Gjennomgangen etter cc7f587 (ECH2): uten skillelinja, eller med feil
        # antall kolonner, viser GitHub ikke tabellen som tabell.
        assert tabellen.splitlines()[1] == "|---|---|---|"
        assert all(l.count("|") == 4 for l in tabellen.splitlines()), tabellen
        synlig = _utenfor_pilene(tekst)
        assert TABELLEN + tabellen in synlig
        i = tekst.index(TABELLEN)
        assert tekst.index("**Innhold:**") < i < tekst.index("\nTil faglærer:\n") < tekst.index("\n## Kom i gang")
        assert tekst.count("| | Demoen | Den ekte versjonen |") == 1
        assert not any("| Klar |" in innhold for _, innhold in _pilene(_kom_i_gang()))
        lenke = "](#demoen-og-den-ekte-versjonen)"
        assert lenke in dict(_pilene(_kom_i_gang()))["Med Docker Desktop"]
        assert tekst.count('<a name="demoen-og-den-ekte-versjonen"></a>') == 1

    def test_hvert_steg_under_staar_du_fast_sier_hvilken_vei(self):
        """Gruppens svar 27.10 kl. 06:09, b (ECH7 i triagen til 3.5g): hver
        henvisning til et steg under «Står du fast?» sier hvilken vei den
        gjelder, som «steg 4 med Docker», fordi dobbeltklikket også har
        nummererte steg. De samme svarene i docs/hjelp.md sier det samme.
        Ville feilet hvis et «steg» med tall under «Står du fast?», eller i
        svarene i hjelpen som står der også, ikke ble fulgt av «med Docker»,
        eller hvis det ikke var noen henvisninger å sjekke."""
        # Gjennomgangen etter cc7f587 (BH6, ECH3): også «Steg 4», tall med to
        # sifre og «steg 3 og 4» eller «steg 1–4».
        mønster = r"\b[Ss]teg (\d+)(?:\s*(?:–|og)\s*\d+)?\b( med Docker)?"
        faq = _faq()
        henvisninger = re.findall(mønster, faq)
        assert len(henvisninger) == 5, henvisninger
        assert all(med for _, med in henvisninger), henvisninger
        i_hjelp = dict(re.findall(r"^### ([^\n]+)\n\n(.*?)(?=\n\n### |\n\n## |\Z)", _hjelp(), re.MULTILINE | re.DOTALL))
        felles = [s for s in _detaljer(faq) if s in i_hjelp]
        # Gjennomgangen etter cc7f587 (ECH4): fire av de fem spørsmålene står
        # likt i hjelpen; det femte er det sammenslåtte (SAMMENSLAATT).
        assert len(felles) == 4, felles
        # Og svarene i hjelpen med en henvisning til et steg i Docker-veien
        # som ikke står under en overskrift «Steg N» (BH5, ECH6, VG).
        felles += [
            "«Cannot connect to the Docker daemon», «error during connect» eller «dockerDesktopLinuxEngine».",
            "«docker» er ikke gjenkjent, eller «command not found: docker».",
            "Mappa lar seg ikke dra inn i vinduet.",
            "«The term 'uv' is not recognized» eller «command not found: uv».",
            "Jeg lukket vinduet før jeg stoppet.",
        ]
        for sporsmaal in felles:
            assert sporsmaal in i_hjelp, sporsmaal
            for _, med in re.findall(mønster, i_hjelp[sporsmaal]):
                assert med, sporsmaal

    def test_linja_om_linux_lenker_til_docker_og_uv(self):
        """Gruppens svar 27.10 kl. 06:09, a (BH3 i triagen til 3.5g): en
        tredje kort linje under stegene, «Linux: bruk Docker eller uv,
        under.», med lenker til pilene for Docker og uv. Ville feilet hvis
        linja manglet, sto et annet sted enn rett etter linja om den ekte
        versjonen, sto bak en pil, eller lenket til et anker som ikke finnes."""
        del_ = _kom_i_gang()
        foer = del_.split("\n<details>\n", 1)[0]
        assert foer.count(LINUX_LINJA) == 1
        assert not any(LINUX_LINJA in innhold for _, innhold in _pilene(del_))
        avsnitt = [a.strip() for a in foer.split("\n\n") if a.strip()]
        assert avsnitt[-2].startswith("**Ekte kurser:**") and avsnitt[-1] == LINUX_LINJA
        assert re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", LINUX_LINJA) == "**Linux:** bruk Docker eller uv, under."
        lenkene = re.findall(r"\]\(#([^)]+)\)", LINUX_LINJA)
        assert lenkene == ["med-docker-desktop", "uten-docker-med-uv"]
        tekst = README.read_text(encoding="utf-8")
        for maal in lenkene:
            assert f'<a name="{maal}"></a>' in tekst, maal

    def test_resten_av_dobbeltklikket_staar_bak_pila(self):
        """Story 3.5g: teksten som sto under dobbeltklikket, står uendret i
        pila «Slik virker dobbeltklikket». Ville feilet hvis et av de fire
        punktene, advarselen, godkjenningen, vernet mot .git, nøkkelen eller
        skriptene med porten falt ut."""
        slik = _seksjon("Slik virker dobbeltklikket")
        assert slik.startswith("Docker trengs ikke, og du skriver ingen kommandoer.")
        punktene = [l for l in slik.split("\n\n") if l.startswith("- **")][0].splitlines()
        assert [re.match(r"- \*\*([^*]+)\*\*", l).group(1) for l in punktene] == [
            "Last ned koden",
            "Pakk ut.",
            "Finn de fire filene",
            "Dobbeltklikk «Start demoen».",
        ], punktene
        assert "«Code»" in punktene[0] and "«Download ZIP»" in punktene[0] and f"]({ZIP_LENKEN})" in punktene[0]
        assert "«Pakk ut alle»" in punktene[1] and "`G74-lund-osen-main`" in punktene[1]
        # Gjennomgangen av 3.5f (BH1, ECH1): den innerste mappa etter «Pakk ut alle».
        assert "`Start demoen` og `Start den ekte versjonen`" in punktene[2]
        assert "øverst i den innerste `G74-lund-osen-main`" in punktene[2]
        assert "ikke «Start demoen.command»" in punktene[2] and "Pakk ut først" in punktene[1]
        for setning in (
            "Når vinduet er åpent:",
            "Skriv `j` og trykk Enter. Det er den offisielle installasjonen fra astral.sh",
            "Stopp appen ved å lukke vinduet, eller med Ctrl+C.",
            "**Advarselen fra Windows.**",
            "**Godkjenningen på Mac.**",
            "**Den ekte versjonen** starter bare i en kopi fra «Download ZIP»",
            "Den ekte versjonen spør etter nøkkelen fra EODHD første gang.",
            "Skriptene står i [`start/`](start/)",
            "Den bruker port 8000, som Docker.",
        ):
            assert setning in slik, setning
        assert "<details>" not in slik

    def test_overskriftene_fra_foer_finnes(self):
        """Story 3.5g: hver overskrift som sto i «Kom i gang» før, står som
        overskrift eller som pil, og hvert anker lenkene bruker, finnes én
        gang. Ville feilet hvis en av dem falt ut, eller et anker ble borte
        eller sto to ganger."""
        tekst = README.read_text(encoding="utf-8")
        del_ = _kom_i_gang()
        overskrifter = set(re.findall(r"^### (.+)$", del_, re.MULTILINE))
        pilene = {re.sub(ANKER_I_PIL, "", s) for s in re.findall(r"^<summary>(.+)</summary>$", del_, re.MULTILINE)}
        for gammel in ("Med Docker Desktop", "Står du fast?", "Mer for den som vil", "Uten Docker, med uv"):
            assert gammel in overskrifter | pilene, gammel
        assert DOBBELTKLIKKET in overskrifter
        alle = _alle_ankrene(tekst)
        for anker in (
            "kom-i-gang",
            DOBBELTKLIKK_ANKER,
            "med-docker-desktop",
            "demoen",
            "den-ekte-versjonen",
            "uten-docker-med-uv",
            "står-du-fast",
            "slik-virker-dobbeltklikket",
            "mer-for-den-som-vil",
            "tester",
        ):
            assert alle.count(anker) == 1, anker

    def test_velg_vei_lenker_rett_inn_i_rekkefoelgen(self):
        """Ville feilet hvis lista under tabellen manglet, en vei sto i en
        annen rekkefølge, eller en lenke gikk til et anker som ikke finnes
        eller finnes to ganger."""
        # Story 3.5g: lista står under tabellen i pila «Demoen og den ekte
        # versjonen», og «Du trenger» i pila etter. Svarene 28.10 kl. 11:19
        # og 11:23 (e): tabellen står øverst, og lista står i pila.
        topp = _seksjon("Demoen og den ekte versjonen")
        assert "| Klar |" not in topp and "**Velg vei etter hva du har:**" in topp
        assert "| Klar |" in _tabellen()
        assert _seksjon("Du trenger").startswith("**Du trenger**")
        punkter = _velg_vei()
        assert [t for t, _, _ in punkter] == [DOBBELTKLIKK_LENKE, "Med Docker Desktop", "Uten Docker, med uv"]
        assert [a for _, a, _ in punkter] == [
            "enklest-dobbeltklikk-uten-docker",
            "med-docker-desktop",
            "uten-docker-med-uv",
        ]
        alle = _alle_ankrene(README.read_text(encoding="utf-8"))
        for _, anker, _ in punkter:
            assert alle.count(anker) == 1, anker
        assert punkter[1][1] == _anker(punkter[1][0])
        assert punkter[0][2].startswith(" (anbefalt): ")
        # Story 3.5g: uv står ikke lenger under «Mer for den som vil».
        assert punkter[2][2].startswith(": kommandoene i et terminalvindu.")
        # Ankeret til uv står i pila.
        assert f"<summary>{UV_PIL}</summary>" in _kom_i_gang()

    def test_docker_veien_har_stegene_bildene_og_kommandoene(self):
        """Ville feilet hvis Docker-veien eller en kommando manglet i «Kom i
        gang», eller hvis «Velg vei» i Docker-delen ikke het «Velg versjon»."""
        # Story 3.5g: fra pila til Docker til pila til uv, med pilene til
        # demoen og den ekte versjonen og advarselen mot down -v imellom.
        start = '<summary><a name="med-docker-desktop"></a>Med Docker Desktop</summary>'
        docker = _kom_i_gang().split(start, 1)[1].split(f"<summary>{UV_PIL}</summary>", 1)[0]
        assert [s for s, _ in _pilene(_kom_i_gang())][2:5] == list(PILENE_I_KOM_I_GANG[2:5])
        assert [int(n) for n in re.findall(r"^(\d+)\. ", docker, re.MULTILINE)] == [1, 2, 3, 4, 5, 6, 7, 5, 6, 7, 8, 9]
        for bilde in BILDENE.values():
            assert f"](docs/bilder/readme/{bilde})" in docker, bilde
        assert KOPIERINGEN in docker and f"\n{VELG_VEI} Klikk på pila" in docker
        assert "**Velg vei.**" not in README.read_text(encoding="utf-8")
        assert '<a name="demoen"></a>' in docker and '<a name="den-ekte-versjonen"></a>' in docker
        kommandoene = [l.strip() for spraak, b in _blokkene(docker) if not spraak for l in b.splitlines()]
        assert kommandoene == [
            "docker compose up --build demo",
            "docker compose --profile demo down",
            "cp .env.example .env",
            "notepad .env",
            "open -e .env",
            "docker compose up --build",
            "docker compose run --rm hent",
            "docker compose down",
        ], kommandoene
        assert ADVARSELEN_MOT_DOWN_V in docker

    def test_zip_lenken_gaar_til_main_i_dette_repoet(self):
        """Ville feilet hvis den direkte lenken gikk til en annen gren eller
        et annet repo enn GitHub-siden README-en lenker til, eller ikke sto
        både i dobbeltklikket og i steg 2. Mappa GitHub pakker ut, heter
        repoet og grenen, G74-lund-osen-main, som stegene sier."""
        tekst = README.read_text(encoding="utf-8")
        repoet = "https://github.com/IBE160-2026/G74-lund-osen"
        assert f"[GitHub-siden]({repoet})" in tekst
        assert f"{repoet}/actions/workflows/tester.yml" in tekst
        zip_lenker = re.findall(r"\]\((https://[^)]*\.zip)\)", tekst)
        # Story 3.5g: i steg 1 i dobbeltklikket, i pila «Slik virker
        # dobbeltklikket» og i steg 2 i Docker.
        assert zip_lenker == [ZIP_LENKEN, ZIP_LENKEN, ZIP_LENKEN], zip_lenker
        assert ZIP_LENKEN == f"{repoet}/archive/refs/heads/main.zip"
        assert f"]({ZIP_LENKEN})" in _dobbeltklikket() and f"]({ZIP_LENKEN})" in _steg("Med Docker Desktop", 2)
        assert f"]({ZIP_LENKEN})" in _seksjon("Slik virker dobbeltklikket")
        mappa = f"{repoet.rsplit('/', 1)[1]}-{ZIP_LENKEN.rsplit('/', 1)[1].removesuffix('.zip')}"
        assert mappa == "G74-lund-osen-main"
        assert f"`{mappa}`" in _dobbeltklikket() and f"`{mappa}`" in _steg("Med Docker Desktop", 2)

    def test_tabellen_og_du_trenger_sier_ikke_at_docker_trengs(self):
        """Ville feilet hvis raden «Trenger» eller «Du trenger» sa at Docker
        trengs, eller hvis «Du trenger» ikke sa at Docker trengs bare for
        Docker-veien."""
        # Story 3.5g: tabellen og «Du trenger» står i hver sin pil. Svarene
        # 28.10 kl. 11:19 og 11:23 (e): tabellen står øverst, uten pil.
        topp = _tabellen()
        trenger = [l for l in topp.splitlines() if l.startswith("| Trenger |")]
        assert trenger == ["| Trenger | Ingen konto og ingen nøkkel | En gratis nøkkel fra EODHD |"], trenger
        du_trenger = [a for a in _seksjon("Du trenger").split("\n\n") if a.startswith("**Du trenger**")][0]
        # Gjennomgangen (BH3, ECH4): den ekte versjonen trenger en konto hos
        # EODHD, saa bare demoen er uten konto.
        assert "men verken git eller Docker, og demoen trenger ingen konto" in du_trenger
        assert "Bare Docker" not in du_trenger and "Med Docker trenger du Docker Desktop" in du_trenger

    def test_til_faglaerer_viser_foerst_til_dobbeltklikket_og_saa_til_docker(self):
        """Ville feilet hvis «Til faglærer» viste til Docker foer
        dobbeltklikket."""
        lista = README.read_text(encoding="utf-8").split("Til faglærer:\n", 1)[1].split("\n\n", 1)[0]
        assert lista.index("](#enklest-dobbeltklikk-uten-docker)") < lista.index("](#med-docker-desktop)")
        assert lista.index("](#med-docker-desktop)") < lista.index("](#demoen)")

    def test_mappestrukturen_forklarer_alt_i_rota(self):
        """Ville feilet hvis en fil eller mappe i rota som git sporer, ikke
        sto i «Mappestruktur» med en forklaring. De fire startfilene står med
        navnet uten filendelsen, og .cmd og .command forklares. Uten git
        (ZIP-fila) hoppes testen over, fordi rota der også har det som ikke
        er sporet."""
        import pytest

        sporet = _git_sporet()
        if sporet is None:
            pytest.skip("ingen git her (for eksempel ZIP-fila som leveres)")
        rota = sorted({f.split("/", 1)[0] for f in sporet})
        del_ = README.read_text(encoding="utf-8").split("\n## Mappestruktur\n", 1)[1].split("\n## ", 1)[0]
        punkter = [l for l in del_.splitlines() if l.startswith("- ")]
        for punkt in punkter:
            assert " — " in punkt and punkt.split(" — ", 1)[1].strip(), punkt
        lenket = {maal.rstrip("/").split("/", 1)[0] for _, maal in re.findall(r"\[`([^`]+)`\]\(([^)]+)\)", del_)}
        startfilene = [f for f in rota if f.startswith("Start ")]
        assert sorted(startfilene) == [
            "Start demoen.cmd",
            "Start demoen.command",
            "Start den ekte versjonen.cmd",
            "Start den ekte versjonen.command",
        ]
        # Gjennomgangen (BH14, VG3): startfilene forklares i punktet om start/.
        start = [p for p in punkter if p.startswith("- [`start/`](start/)")]
        assert len(start) == 1, punkter
        for navn in startfilene:
            assert navn.rsplit(".", 1)[0] in start[0], navn
        assert "for Windows og Mac" in start[0]
        mangler = [f for f in rota if f not in startfilene and f not in lenket]
        assert not mangler, mangler
        for navn in ("CLAUDE.md", "pyproject.toml", "uv.lock"):
            assert f"[`{navn}`]({navn})" in del_, navn

    def test_hjelpen_har_dobbeltklikket_foerst(self):
        """Regel 19: docs/hjelp.md følger hovedveien. Ville feilet hvis
        dobbeltklikket sto etter Docker-stegene, lenken gikk til den gamle
        pila, eller «neste gang» bare nevnte Docker."""
        hjelp = _hjelp()
        deler = re.findall(r"^## (.+)$", hjelp, re.MULTILINE)
        assert deler[:2] == ["Start med dobbeltklikk", "Steg 1: Docker Desktop"], deler
        # Gjennomgangen (BH8, ECH3): svar for de vanligste feilene på hovedveien.
        dobbeltklikk = hjelp.split("\n## Start med dobbeltklikk\n", 1)[1].split("\n## ", 1)[0]
        for sporsmaal in (
            "Jeg finner ikke de fire filene.",
            "Vinduet lukkes med en gang.",
            "Det er to filer som heter «Start demoen».",
        ):
            assert f"### {sporsmaal}\n" in dobbeltklikk, sporsmaal
        assert "Dobbeltklikket står først, som i README-en." in hjelp
        assert "«Start med dobbeltklikk, uten Docker»" not in hjelp
        # Story 3.5g: avsnittet om advarselen står i pila «Slik virker
        # dobbeltklikket». Gjennomgangen (BH7, ECH1, VG2): lenken går til
        # ankeret i den pila, ikke til de fem stegene.
        assert "«Slik virker dobbeltklikket» i [README-en](../README.md#slik-virker-dobbeltklikket)" in hjelp
        assert '<summary><a name="slik-virker-dobbeltklikket"></a>Slik virker dobbeltklikket</summary>' in (
            README.read_text(encoding="utf-8")
        )
        neste = hjelp.split("### Hvordan starter jeg neste gang?\n\n", 1)[1]
        assert neste.startswith("Med dobbeltklikket: ") and "\n\nMed Docker: " in neste
