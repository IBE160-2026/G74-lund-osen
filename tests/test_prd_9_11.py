"""Story 9.11: PRD-en etter tilbakemeldingen fra faglærer 12.11.

Gruppens svar 12.11 kl. 18:00: prd.md får én gjeldende tekst per krav, og de
daterte linjene flyttes ordrett til prd-endringslogg.md i samme mappe. Taggen
prd-vurdert-2026-11-12 har PRD-en slik den var før omskrivingen.

CI henter ikke taggene, så tallene og ID-ene fra taggen står her som
konstanter. test_konstantene_stemmer_med_taggen sjekker dem mot taggen når
git og taggen finnes, som i arbeidskopien vår.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parent.parent
MAPPA = ROT / "_bmad-output" / "planning-artifacts" / "prds" / "prd-G74-lund-osen-2026-09-20"
PRD = MAPPA / "prd.md"
ENDRINGSLOGGEN = MAPPA / "prd-endringslogg.md"
TAGGEN = "prd-vurdert-2026-11-12"
TAGGENS_STI = "_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md"

# «Rettet» og «Lagt til», også med liten forbokstav, slik de står i taggen.
HISTORIKK = re.compile(r"(?i)\b(rettet|lagt til)\b")
TAGGENS_ANTALL = 275
# Nye daterte linjer etter omskrivingen står under denne overskriften.
NYE_LINJER = "\n## Endringer etter 12.11\n"
# Andre daterte merker fra taggen, og storynummer og commiter (4.4).
ANDRE_MERKER = re.compile(
    r"\*\(?(Endret|Avgjort|Presisert|Skrevet inn|Skrevet om|Skjerpet|Merknad|Tillegg|Flyttet til v1|"
    r"Delvis flyttet|Tatt inn i v1|Ute av v1|Utenfor v1|Frist endret|Utvidet|Lukket|Talt på nytt)\b"
)
STORY_ELLER_COMMIT = re.compile(r"(?i)\bstory \d|`[0-9a-f]{7,8}`|\bbygget per\b")
# Hver FR- og NFR-ID som står i taggen.
TAGGENS_ID = (
    "FR-101",
    "FR-102",
    "FR-103",
    "FR-104",
    "FR-105",
    "FR-106",
    "FR-107",
    "FR-108",
    "FR-109",
    "FR-110",
    "FR-201",
    "FR-202",
    "FR-203",
    "FR-204",
    "FR-205",
    "FR-206",
    "FR-207",
    "FR-301",
    "FR-302",
    "FR-303",
    "FR-401",
    "FR-402",
    "FR-403",
    "FR-404",
    "FR-405",
    "FR-406",
    "FR-407",
    "FR-408",
    "FR-409",
    "FR-410",
    "FR-411",
    "FR-412",
    "FR-413",
    "FR-414",
    "FR-501",
    "FR-502",
    "FR-503",
    "FR-601",
    "FR-602",
    "FR-602A",
    "FR-603",
    "FR-603A",
    "FR-604",
    "FR-604A",
    "FR-605",
    "FR-606",
    "FR-606A",
    "FR-607",
    "FR-608",
    "FR-701",
    "FR-702",
    "FR-703",
    "FR-704",
    "FR-705",
    "FR-706",
    "NFR-01",
    "NFR-02",
    "NFR-03",
    "NFR-04",
    "NFR-05",
    "NFR-06",
    "NFR-07",
    "NFR-08",
)
# Ankrene i taggen: overskriftene og <a name>, uten frontmatteren.
TAGGENS_ANKRE = (
    "1-bakgrunn-og-mål",
    "2-omfang",
    "3-aksjeuniverset",
    "4-funksjonelle-krav",
    "41-markedsoversikten",
    "42-aksjedetaljen",
    "43-kommende-finansielle-hendelser",
    "44-datahenting-og-oppdatering",
    "45-meldingsfilter-og-deduplisering",
    "46-ki-laget-og-grensen-mot-regelbasert-kode",
    "46a-plan-a-ki-laget-over-meldinger-utenfor-v1",
    "47-signalstyrke-og-retning",
    "5-tverrgående-krav",
    "6-datakilder",
    "7-suksessmål",
    "8-åpne-punkter",
    "fr-101--fem-kolonner",
    "fr-102--standard-sortering",
    "fr-103--retning-vises-i-tre-redundante-kanaler",
    "fr-104--hovedindeksen-i-markedsoversikten",
    "fr-105--søylene-under-hovedindeksen",
    "fr-106--børsometeret",
    "fr-107--endret-signalstyrke-siden-forrige-børsdag",
    "fr-108--filter-på-signalet",
    "fr-109--hjelpen-på-sidene",
    "fr-110--innstillinger",
    "fr-201--kursgraf-med-seks-måneders-historikk",
    "fr-202--ma50-linjen-tegnes-oppå-kursen",
    "fr-203--øvrig-innhold",
    "fr-204--aksjedetaljen-for-en-aksje-uten-gyldig-signal",
    "fr-205--se-nærmere",
    "fr-206--signaldager-i-kursgrafen",
    "fr-207--kommende-eksdato-i-kursgrafen",
    "fr-301--kilde-og-kobling-til-selskap",
    "fr-302--hvilke-hendelser-og-hvor-langt-frem",
    "fr-303--når-kalenderen-ikke-svarer",
    "fr-401--henting-utløses-eksplisitt-aldri-av-en-oppstart",
    "fr-402--kontroll-mot-forventet-børsdag-ikke-mot-klokkeslett",
    "fr-403--etterfylling-av-kurser-etter-dager-uten-bruk",
    "fr-404--etterfylling-av-børsmeldinger",
    "fr-405--avkorting-ved-lange-meldingsintervaller",
    "fr-406--to-lagre-for-kursdata-med-hvert-sitt-ansvar",
    "fr-407--merking-av-utbyttedager",
    "fr-408--dagens-vurdering-lagres-per-aksje",
    "fr-409--de-tre-tilstandene-skal-være-skillbare-i-lageret",
    "fr-410--hovedindeksen-hentes-i-samme-kjøring",
    "fr-411--demoversjonen-har-oppdiktede-tall-i-en-egen-base",
    "fr-412--lista-over-aksjer",
    "fr-413--måling-av-omsetning",
    "fr-414--eksdatoer-ført-for-hånd",
    "fr-501--deduplisering-av-språkdubletter",
    "fr-502--kategorifilter-i-tre-bøtter",
    "fr-503--eksdato-som-datakilde-for-utbyttemerking",
    "fr-601--avpå-bryteren-er-brukersynlig",
    "fr-602--visningen-når-ki-laget-er-av",
    "fr-602a--visningen-når-ki-laget-er-av",
    "fr-603--ki-teksten-sier-ikke-mer-enn-grunnlaget",
    "fr-603a--usikkerhet-vises-som-forbehold-ikke-som-rekkefølge",
    "fr-604--logging-av-ki-bidraget-fra-første-kjøring",
    "fr-604a--logging-av-ki-bidraget-fra-første-kjøring",
    "fr-605--promptversjon-og-modell-lagres-med-hver-ki-tekst",
    "fr-606--relevansskalaen",
    "fr-606a--relevansskalaen",
    "fr-607--ki-teksten-om-dagen-på-forsiden",
    "fr-608--valg-av-tjeneste",
    "fr-701--tre-navngitte-sjekker",
    "fr-702--nøytralsone-i-trendsjekken",
    "fr-703--signalstyrke",
    "fr-704--retning",
    "fr-705--terskel-for-at-en-aksje-skiller-seg-ut",
    "fr-706--synlig-begrunnelse-i-aksjedetaljen",
    "hvis-vi-rekker",
    "hvor-gamle-dataene-er",
    "hvorfor-målingen-må-med",
    "inne-i-v1",
    "kort-fortalt",
    "kriterium",
    "lukket",
    "minste-historikk-175-handelsdager",
    "motmål",
    "må-avgjøres-før-arbeidet-går-videre",
    "må-følges-opp",
    "navigasjon-til-aksjedetaljen",
    "nfr-01--daglig-drift-skal-holde-seg-innenfor-api-kvoten",
    "nfr-02--brukeren-venter-aldri-på-en-henting",
    "nfr-03--manglende-data-stopper-ikke-hovedflyten",
    "nfr-04--ki-laget-skal-ikke-kunne-ta-ned-hovedflyten",
    "nfr-05--norsk-i-grensesnitt-og-forklaringer",
    "nfr-06--løsningen-gir-ikke-investeringsråd",
    "nfr-07--rådata-bevares-fra-første-kjøring",
    "nfr-08--bare-tall-vi-kan-stå-for",
    "prd--ose-signal",
    "resultat-av-filteret",
    "universet",
    "utenfor-v1",
    "utsatte-vurderinger",
    "v11--vurderes-etter-at-v1-er-kontrollert",
    "vurderinger-etterfylles-ikke-og-det-er-med-vilje",
)
ID = re.compile(r"\bN?FR-\d{3}A?\b|\bNFR-\d\d\b")
# Gruppens svar 12.11 kl. 20:04 (spørsmål 14): Min liste får eget krav.
NYE_KRAV = ("FR-111",)
KRAVOVERSKRIFT = re.compile(r"^(#{3,4}) ((?:FR-\d{3}A?|NFR-\d\d)) — .+$", re.MULTILINE)


def _prd() -> str:
    return PRD.read_text(encoding="utf-8")


def _uten_frontmatter(tekst: str) -> str:
    return tekst.split("\n---\n", 1)[1] if tekst.startswith("---\n") else tekst


def _anker(overskrift: str) -> str:
    """Ankeret GitHub lager av en overskrift, som _anker i test_docker.py."""
    return re.sub(r"[^\w\- ]", "", overskrift.strip().lower()).replace(" ", "-")


def _ankrene(tekst: str) -> set[str]:
    uten = re.sub(r"`[^`\n]*`", "", _uten_frontmatter(tekst))
    funnet = re.findall(r'^#+ (.+)$|<a name="([^"]+)"></a>', uten, re.MULTILINE)
    return {_anker(o) if o else navn for o, navn in funnet}


def _kravene(tekst: str) -> dict[str, str]:
    """ID -> teksten under overskriften, til neste overskrift."""
    treff = list(KRAVOVERSKRIFT.finditer(tekst))
    ut = {}
    for i, m in enumerate(treff):
        slutt = treff[i + 1].start() if i + 1 < len(treff) else len(tekst)
        del_ = tekst[m.end() : slutt]
        neste = re.search(r"^#{1,4} ", del_, re.MULTILINE)
        ut[m.group(2)] = del_[: neste.start()] if neste else del_
    return ut


def test_ingen_rettet_eller_lagt_til_i_prd():
    """4.1 i tilbakemeldingen. Ville feilet hvis en datert «Rettet»- eller
    «Lagt til»-linje, eller ordet, sto igjen i prd.md."""
    assert HISTORIKK.findall(_prd()) == []


def test_ingen_andre_daterte_merker_storynummer_eller_navn_i_prd():
    """4.1 og 4.4, og regel 20. Ville feilet hvis et annet datert merke fra
    taggen, som «Presisert» eller «Ute av v1», et storynummer, en commit,
    «bygget per», eller et navn utenom gruppelinja sto i prd.md."""
    tekst = _prd()
    assert ANDRE_MERKER.findall(tekst) == []
    assert STORY_ELLER_COMMIT.findall(tekst) == []
    uten_gruppelinja = "\n".join(linje for linje in tekst.splitlines() if not linje.startswith("**Gruppe:**"))
    assert re.findall(r"\b(Marian|Joakim)\b", uten_gruppelinja) == []


def test_brukerreisen_og_ordlista():
    """4.3. Ville feilet hvis UJ-1 manglet climax eller edge, eller ordlista
    ikke hadde 8–10 ord."""
    tekst = _prd()
    uj = tekst.split("### Brukerreisen UJ-1\n", 1)[1].split("\n### ", 1)[0]
    assert "**UJ-1." in uj and "*Climax:*" in uj and "*Edge:*" in uj
    ordlista = tekst.split("### Ordliste\n", 1)[1].split("\n---\n", 1)[0]
    rader = [r for r in ordlista.splitlines() if r.startswith("| **")]
    assert 8 <= len(rader) <= 10, len(rader)


def test_endringsloggen_har_like_mange_linjer_som_taggen():
    """Ingenting går tapt: hver «Rettet» og «Lagt til» i taggen står i
    endringsloggen. Ville feilet hvis en linje falt ut, eller en ble skrevet
    to ganger. Nye linjer etter 12.11 står under NYE_LINJER og telles
    ikke (regel 19)."""
    fra_taggen = ENDRINGSLOGGEN.read_text(encoding="utf-8").split(NYE_LINJER, 1)[0]
    assert len(HISTORIKK.findall(fra_taggen)) == TAGGENS_ANTALL


def test_hvert_krav_har_konsekvenser():
    """4.2. Ville feilet hvis et FR eller NFR i prd.md, også i vedlegg A,
    manglet «*Konsekvenser:*», eller konsekvensen var tom."""
    uten = [k for k, tekst in _kravene(_prd()).items() if "*Konsekvenser:*" not in tekst]
    assert uten == []
    for k, tekst in _kravene(_prd()).items():
        etter = tekst.split("*Konsekvenser:*", 1)[1].split("\n\n", 1)[0]
        assert len(etter.split()) >= 5, k


def test_hver_id_i_taggen_har_en_overskrift_i_prd():
    """De samme ID-ene. Ville feilet hvis et krav fra taggen manglet som
    overskrift i prd.md, eller et nytt krav var kommet til uten at NYE_KRAV
    ble endret. FR-111 (Min liste) kom til etter svaret 12.11 kl. 20:04."""
    assert sorted(_kravene(_prd())) == sorted(TAGGENS_ID + NYE_KRAV)


def test_hvert_sm_har_id_og_krav():
    """§5 i tilbakemeldingen. Ville feilet hvis et suksessmål manglet ID,
    ID-ene ikke gikk fra SM-1 uten hull, eller et mål ikke viste til et krav
    som finnes."""
    tekst = _prd()
    del7 = tekst.split("\n## 7. Suksessmål\n", 1)[1].split("\n## 8.", 1)[0]
    rader = [r for r in del7.splitlines() if r.startswith("| SM-")]
    assert len(rader) >= 9
    kravene = set(_kravene(tekst))
    for nr, rad in enumerate(rader, start=1):
        celler = [c.strip() for c in rad.strip().strip("|").split("|")]
        assert celler[0] == f"SM-{nr}", rad
        krav = ID.findall(celler[-1])
        assert krav, rad
        assert set(krav) <= kravene, rad


def test_tabellen_over_omfanget_har_hvert_fr():
    """4.5. Ville feilet hvis et FR manglet i tabellen «Kjerne, ekstra og
    senere», en rad hadde en annen status enn kjerne, ekstra eller senere,
    eller noe annet enn ja eller nei under «Bygget?», eller tabellen hadde et
    FR som ikke finnes."""
    tekst = _prd()
    del2 = tekst.split("### Kjerne, ekstra og senere\n", 1)[1].split("\n### ", 1)[0]
    rader = [r for r in del2.splitlines() if r.startswith("| FR-")]
    dekket = set()
    for rad in rader:
        fr, _, status, bygget = [c.strip() for c in rad.strip().strip("|").split("|")]
        assert status in ("kjerne", "ekstra", "senere"), rad
        assert bygget in ("ja", "nei"), rad
        for bit in fr.split(", "):
            ender = ID.findall(bit)
            if "–" in bit and len(ender) == 2:
                fra, til = (int(re.search(r"\d{3}", e).group()) for e in ender)
                suffiks = "A" if ender[0].endswith("A") else ""
                dekket |= {f"FR-{n}{suffiks}" for n in range(fra, til + 1)}
            else:
                dekket |= set(ender)
    fr_id = {i for i in TAGGENS_ID + NYE_KRAV if i.startswith("FR-")}
    assert dekket == fr_id, (sorted(fr_id - dekket), sorted(dekket - fr_id))


def test_ankrene_fra_taggen_finnes():
    """Endres en overskrift, står det gamle ankeret. Ville feilet hvis en
    lenke i en eldre fil til et anker i prd.md ikke lenger virket."""
    assert sorted(set(TAGGENS_ANKRE) - _ankrene(_prd())) == []


def test_alle_lenker_til_ankre_i_prd_virker():
    """Ville feilet hvis en lenke inne i prd.md, eller en lenke til prd.md
    fra README-en, docs/ eller _bmad-output/, pekte på et anker som ikke
    finnes."""
    egne = _ankrene(_prd())
    brutt = [a for a in re.findall(r"\]\(#([^)\s]+)\)", _prd()) if a not in egne]
    filene = [ROT / "README.md", *(ROT / "docs").rglob("*.md"), *(ROT / "_bmad-output").rglob("*.md")]
    for fil in filene:
        for anker in re.findall(r"(?<![\w-])prd\.md#([^)\s>\]]+)", fil.read_text(encoding="utf-8")):
            if anker not in egne:
                brutt.append(f"{fil.relative_to(ROT)}: {anker}")
    assert brutt == []


def test_endringsloggen_lenkes_oeverst():
    """Ville feilet hvis lenken til endringsloggen ikke sto før «Kort
    fortalt», eller endringsloggen manglet en rad for et punkt i
    tilbakemeldingen."""
    tekst = _prd()
    assert tekst.index("](prd-endringslogg.md)") < tekst.index("\n## Kort fortalt\n")
    logg = ENDRINGSLOGGEN.read_text(encoding="utf-8")
    tabellen = logg.split("## Tilbakemeldingen 12.11 og hva som er gjort\n", 1)[1].split("\n## ", 1)[0]
    for punkt in ("| 4.1 ", "| 4.2 ", "| 4.3 ", "| 4.4 ", "| 4.5 ", "| §5 "):
        assert punkt in tabellen, punkt


def _taggens_prd() -> str | None:
    if shutil.which("git") is None or not (ROT / ".git").exists():
        return None
    svar = subprocess.run(
        ["git", "-C", str(ROT), "show", f"{TAGGEN}:{TAGGENS_STI}"], capture_output=True, text=True, encoding="utf-8"
    )
    return svar.stdout if svar.returncode == 0 else None


def test_konstantene_stemmer_med_taggen():
    """Ville feilet hvis konstantene over var regnet feil, eller en bit i
    endringsloggen ikke sto ordrett i taggen. Hoppes over uten taggen, som i
    CI, der checkout ikke henter taggene."""
    tag = _taggens_prd()
    if tag is None:
        pytest.skip(f"taggen {TAGGEN} finnes ikke her")
    assert len(HISTORIKK.findall(tag)) == TAGGENS_ANTALL
    assert sorted(set(ID.findall(tag))) == sorted(TAGGENS_ID)
    assert _ankrene(tag) == set(TAGGENS_ANKRE)
    logg = ENDRINGSLOGGEN.read_text(encoding="utf-8")
    linjene = logg.split("## Linjene, ordnet etter krav og dato\n", 1)[1].split("\n## Kommentaren om status", 1)[0]
    biter = re.split(r"\n\nLinje \d+ i taggen[^\n]*:\n\n", linjene)[1:]
    assert len(biter) > 200
    for bit in biter:
        bit = re.split(r"\n\n### ", bit, maxsplit=1)[0].rstrip()
        assert bit in tag, bit[:80]


# Gruppens svar 12.11 kl. 20:09 og 20:10: de åtte står som «senere».
SENERE = (
    ("FR-101", "Endringen i kroner under prosenten"),
    ("FR-107", "Merket for endret signalstyrke"),
    ("FR-109", "«Lær noe nytt»"),
    ("FR-203", "Høy og lav og endringen i kroner"),
    ("FR-205", "«Se nærmere»"),
    ("FR-207", "Kommende eks.dato i kursgrafen"),
    ("FR-414", "Eks.datoer ført for hånd"),
    ("FR-608", "ChatGPT med «Sign in with ChatGPT»"),
)


def test_de_aatte_som_ikke_er_i_v1_staar_som_senere():
    """Gruppens svar 12.11 kl. 20:09 og 20:10. Ville feilet hvis en av de åtte
    sto som ekstra eller kjerne i tabellen i §2, manglet i tabellen eller i
    lista under «v1.1» i §8, eller kravteksten ikke sa at den ikke er i v1.
    Ekstra er det som er bygget utover briefen, så det feiler også hvis en
    annen ekstra-rad enn filteret i FR-108 sto uten «ja», også «De 15 mest
    omsatte», som er flettet med 8.28. Filteret ble tatt bort 11.11 (8.26), så
    raden skal si det og ha «nei» (tillegg 6)."""
    tekst = _prd()
    del2 = tekst.split("### Kjerne, ekstra og senere\n", 1)[1].split("\n### ", 1)[0]
    status = {}
    for rad in del2.splitlines():
        if rad.startswith("| FR-"):
            fr, krav, s, _ = [c.strip() for c in rad.strip().strip("|").split("|")]
            status[(fr, krav)] = s
    v11 = tekst.split("### v1.1 — vurderes etter at v1 er kontrollert\n", 1)[1].split("\n---\n", 1)[0]
    kravene = _kravene(tekst)
    for fr, krav in SENERE:
        assert status.get((fr, krav)) == "senere", (fr, krav, status.get((fr, krav)))
        assert f"({fr})" in v11, fr
        assert "ikke i v1" in " ".join(kravene[fr].split()).lower(), fr
    ekstra_uten_bygg = [
        k for k, s in status.items() if s == "ekstra" and k != ("FR-108", "Filter på signalet, tatt bort 11.11")
    ]
    del2_rader = {
        (r.split("|")[1].strip(), r.split("|")[2].strip()): r.split("|")[4].strip()
        for r in del2.splitlines()
        if r.startswith("| FR-")
    }
    assert [k for k in ekstra_uten_bygg if del2_rader[k] != "ja"] == []
    assert del2_rader[("FR-108", "Filter på signalet, tatt bort 11.11")] == "nei"
