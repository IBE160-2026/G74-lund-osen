"""Morgensjekk for G74-lund-osen. Leser bare, og skriver ingenting til repoet.

Bruk: python3 morgensjekk.py <repo> [naa, f.eks. 2026-09-26T06:54]
"""
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path, PurePosixPath
from zoneinfo import ZoneInfo

OSLO = ZoneInfo("Europe/Oslo")
REPO = Path(sys.argv[1]).resolve()
NAA = (datetime.fromisoformat(sys.argv[2]).replace(tzinfo=OSLO)
       if len(sys.argv) > 2 else datetime.now(OSLO))
IDAG = NAA.date()
IGAAR = IDAG - timedelta(days=1)
FRA = NAA - timedelta(hours=24)
UKE = IDAG.isocalendar()[1]
BRIEF = "_bmad-output/planning-artifacts/product-brief.md"
BRIEF_FRIST = date(2026, 9, 27)
KJENTE_TAGGER = {
    "arbeidskrav-product-brief": "c7416ee",
    "arbeidskrav-product-brief-v2": "f08c801",
    "arbeidskrav-product-brief-v3": "783644a",
    "arbeidskrav-product-brief-v4": "85eee2b",
    "arbeidskrav-product-brief-v5": "16e6f23",
    "arbeidskrav-product-brief-v6": "a5c4052",
    "arbeidskrav-product-brief-v7": "e62ea77",
}
MILJO = dict(os.environ, TZ="Europe/Oslo", LC_ALL="C.UTF-8")


def git(*args):
    r = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=MILJO)
    return r.returncode, r.stdout


def les(rel):
    p = REPO / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else None


def utenfor_blokker(tekst):
    """(linjenummer, linje) for linjer utenfor ```-blokker."""
    inne, gjerde = False, ""
    for nr, linje in enumerate(tekst.splitlines(), 1):
        m = re.match(r"^(`{3,})", linje)
        if not inne and m:
            inne, gjerde = True, m.group(1)
            continue
        if inne and linje.strip() == gjerde:
            inne = False
            continue
        if not inne:
            yield nr, linje


def dato_i(tekst):
    """Alle datoer i teksten, som date. ISO, DD.MM.YYYY og DD.MM (dette aaret)."""
    funn = []
    for m in re.finditer(r"\b(20\d\d)-(\d\d)-(\d\d)\b", tekst):
        funn.append((int(m[1]), int(m[2]), int(m[3])))
    for m in re.finditer(r"\b(\d{1,2})\.(\d{1,2})\.(20\d\d)\b", tekst):
        funn.append((int(m[3]), int(m[2]), int(m[1])))
    for m in re.finditer(r"(?<![\d.])(\d{1,2})\.(\d{2})(?!\d|\.\d)", tekst):
        funn.append((IDAG.year, int(m[2]), int(m[1])))
    ut = []
    for a, mnd, d in funn:
        try:
            ut.append(date(a, mnd, d))
        except ValueError:
            pass
    return ut


print(f"== MORGENSJEKK {IDAG.isoformat()} (uke {UKE}), kjoert {NAA:%H:%M} norsk tid")
_, head = git("log", "-1", "--format=%h %ad %s", "--date=format-local:%d.%m %H:%M")
print(f"HEAD paa GitHub: {head.strip()}")

# 1. Commits siste doegn, delt i kode og dokumenter
print("\n== 1 COMMITS SISTE DOEGN")
_, logg = git("log", f"--since={FRA.isoformat()}", f"--until={NAA.isoformat()}",
              "--format=%x1e%h|%an|%ad|%s", "--date=format-local:%d.%m %H:%M", "--name-only")
commits = []
for blokk in logg.split("\x1e")[1:]:
    linjer = [l for l in blokk.splitlines() if l.strip()]
    h, forf, tid, emne = linjer[0].split("|", 3)
    filer = linjer[1:]
    kode = any(f.startswith(("src/", "tests/", ".github/")) or f in ("pyproject.toml", "uv.lock")
               for f in filer)
    commits.append((h, forf, tid, emne, kode))
print(f"antall={len(commits)} kode={sum(c[4] for c in commits)} "
      f"bare_dokumenter={sum(not c[4] for c in commits)}")
for h, forf, tid, emne, kode in commits[:25]:
    print(f"  {h} {tid} {forf}: {emne} [{'kode' if kode else 'dok'}]")
if len(commits) > 25:
    print(f"  ... og {len(commits) - 25} eldre")

# 2. Dagsfilene (regel 18): hver '## HH:MM' skal ha en '**Utfoert:**'-linje
print("\n== 2 DAGSFILENE")
for d in (IGAAR, IDAG):
    rel = f"docs/ai-prompts/{d.isoformat()}.md"
    tekst = les(rel)
    if tekst is None:
        if d == IGAAR:
            print(f"  {rel}: finnes ikke paa GitHub")
        continue
    seksjoner, naavaerende = [], None
    for _, linje in utenfor_blokker(tekst):
        if re.match(r"^## \d\d:\d\d\s*$", linje):
            naavaerende = [linje[3:].strip(), False]
            seksjoner.append(naavaerende)
        elif naavaerende and linje.startswith("**Utført:**"):
            naavaerende[1] = True
    mangler = [s[0] for s in seksjoner if not s[1]]
    print(f"  {rel}: {len(seksjoner)} instruksjoner, {len(seksjoner) - len(mangler)} med Utført"
          + (f"; mangler Utført: {', '.join(mangler)}" if mangler else ""))
if commits and les(f"docs/ai-prompts/{IGAAR.isoformat()}.md") is None \
        and les(f"docs/ai-prompts/{IDAG.isoformat()}.md") is None:
    print("  MERK: commits siste doegn, men ingen dagsfil for i gaar eller i dag")

# 3. Refleksjonsloggen, per del
print("\n== 3 REFLEKSJONSLOGGEN")
logg_tekst = les("docs/reflection-log.md") or ""
del_ = "Marian"
oppf = {"Marian": [], "Joakim": []}
for _, linje in utenfor_blokker(logg_tekst):
    if linje.startswith("# Joakims oppføringer"):
        del_ = "Joakim"
    m = re.match(r"^## (\d\d)\.(\d\d)\.(\d{4})\b", linje)
    if m:
        oppf[del_].append(date(int(m[3]), int(m[2]), int(m[1])))
for navn, datoer in oppf.items():
    i_gaar = sum(d == IGAAR for d in datoer)
    siste7 = sum(IDAG - timedelta(days=7) <= d <= IDAG for d in datoer)
    siste = max(datoer).strftime("%d.%m") if datoer else "ingen"
    print(f"  {navn}: {i_gaar} oppfoeringer datert i gaar, {siste7} siste 7 dager, "
          f"{len(datoer)} totalt, siste {siste}")

# 4. Sprintstatus
print("\n== 4 SPRINTSTATUS")
ss = les("_bmad-output/implementation-artifacts/sprint-status.yaml") or ""
status = {}
inne = False
for linje in ss.splitlines():
    if linje.startswith("development_status:"):
        inne = True
        continue
    if inne:
        m = re.match(r"^\s+([^\s#:][^:]*):\s*([a-z-]+)\s*(#.*)?$", linje)
        if m:
            status[m[1]] = m[2]
        elif linje.strip() and not linje.startswith((" ", "#")):
            inne = False
storyer = {k: v for k, v in status.items()
           if not k.startswith("epic-") and "retrospective" not in k}
teller = {}
for v in storyer.values():
    teller[v] = teller.get(v, 0) + 1
print(f"  storyer: {teller}")
for k, v in storyer.items():
    if v in ("in-progress", "review", "ready-for-dev"):
        print(f"  {v}: {k}")
neste = [k for k, v in storyer.items() if v == "backlog"][:3]
print(f"  neste i backlog: {', '.join(neste) if neste else 'ingen'}")
aktive_nr = {re.match(r"^(\d+[-.]\d+[a-z]?)", k)[1].replace("-", ".")
             for k, v in storyer.items()
             if (v != "done" and v != "backlog") or k in neste
             if re.match(r"^\d+[-.]\d+", k)}
m = re.search(r"last_updated:\s*(.*)", ss)
print(f"  sist oppdatert: {m[1] if m else 'ukjent'}")

# 5. Aapne punkter i PRD-en som haster
print("\n== 5 AAPNE PUNKTER I PRD-EN SOM HASTER")
prd = les("_bmad-output/planning-artifacts/prds/prd-G74-lund-osen-2026-09-20/prd.md") or ""
del8 = prd.split("## 8. Åpne punkter", 1)[-1].split("### Lukket", 1)[0]
hode, antall_hastende, antall_alle = None, 0, 0
for linje in del8.splitlines():
    if not linje.startswith("|"):
        hode = None if not linje.strip() else hode
        continue
    celler = [c.strip() for c in linje.strip().strip("|").split("|")]
    if celler[0] == "#":
        hode = celler
        continue
    if not hode or set(celler[0]) <= {"-", ":"}:
        continue
    rad = dict(zip(hode, celler))
    frist = re.sub(r"\([^)]*\)", "", re.sub(r"\*", "", rad.get("Frist", "")))
    eier = re.sub(r"[*‹›]", "", rad.get("Eier", "")).strip()
    eier = "ingen eier" if not eier or "fylles inn" in eier else eier
    punkt = re.sub(r"\*", "", rad.get("Punkt", ""))[:90]
    antall_alle += 1
    grunn = []
    for d in dato_i(frist):
        if d < IDAG:
            grunn.append(f"frist {d:%d.%m} er passert")
        elif d <= IDAG + timedelta(days=7):
            grunn.append(f"frist {d:%d.%m}")
    m = re.search(r"[Uu]ke (\d+)(?:\s*[–-]\s*(\d+))?", frist)
    if m:
        u1, u2 = int(m[1]), int(m[2] or m[1])
        if UKE > u2:
            grunn.append(f"uke {u2} er passert")
        elif u1 <= UKE + 1:
            grunn.append(f"uke {u1}-{u2}, naa uke {UKE}")
    m = re.search(r"[Ff]ør story (\d+\.\d+[a-z]?)", frist)
    if m and m[1] in aktive_nr:
        grunn.append(f"foer story {m[1]}, som er blant de neste")
    if grunn:
        antall_hastende += 1
        print(f"  #{rad.get('#')} | {eier} | {frist} | {punkt} -> {'; '.join(grunn)}")
print(f"  ({antall_hastende} av {antall_alle} aapne punkter haster)")

# 6. Frister i dokumentene de neste 7 dagene
print("\n== 6 FRISTER I DOKUMENTENE, NESTE 7 DAGER")
frister = {}
for rel in ("docs/innlevering.md", "docs/epost-til-euronext.md", "docs/epost-til-eodhd.md",
            "docs/kilder-og-rettigheter.md", "CLAUDE.md"):
    for nr, linje in utenfor_blokker(les(rel) or ""):
        if re.match(r"^\s*\*(Rettet|Presisering|Lagt til)", linje):
            continue
        if not re.search(r"frist|innen|avgjør|beslutning|lever", linje, re.I):
            continue
        for d in dato_i(linje):
            if IDAG <= d <= IDAG + timedelta(days=7):
                frister.setdefault(d, []).append(f"{rel}:{nr}: {linje.strip()[:110]}")
for d in sorted(frister):
    dag = ["man", "tir", "ons", "tor", "fre", "loer", "soen"][d.weekday()]
    print(f"  {dag} {d:%d.%m} (om {(d - IDAG).days} dager): {len(frister[d])} treff, f.eks. {frister[d][0]}")
eur = les("docs/epost-til-euronext.md") or ""
m = re.search(r"^\*\*Status:.*$", eur, re.M)
if m:
    print(f"  Euronext: {m[0].strip('* ')}")
    frist_eur = [d for d in dato_i(m[0]) if d >= date(2026, 9, 22)]
    if "avventes" in m[0].lower() and frist_eur and IDAG >= max(frist_eur):
        print(f"  MERK: beslutningsdatoen {max(frist_eur):%d.%m} er naadd, og svaret avventes fortsatt")

# 7. Briefen og taggene
print("\n== 7 BRIEFEN OG TAGGENE")
_, tagger = git("for-each-ref", "refs/tags/arbeidskrav-product-brief*",
                "--format=%(refname:short)|%(*objectname:short)|%(objectname:short)|%(taggerdate:iso8601)")
funnet = {}
for linje in tagger.splitlines():
    navn, peeled, obj, tid = linje.split("|")
    funnet[navn] = ((peeled or obj)[:7], tid[:16])
for navn, commit in KJENTE_TAGGER.items():
    if navn not in funnet:
        print(f"  MERK: {navn} finnes ikke lenger")
    elif funnet[navn][0] != commit:
        print(f"  MERK: {navn} peker paa {funnet[navn][0]}, ikke {commit} som foer")
nye = [n for n in funnet if n not in KJENTE_TAGGER]
for n in nye:
    print(f"  ny tag: {n} -> {funnet[n][0]} ({funnet[n][1]})")
ver = lambda n: int(re.search(r"-v(\d+)$", n)[1]) if re.search(r"-v(\d+)$", n) else 1
siste = max(funnet, key=ver) if funnet else None
if siste:
    kode, _ = git("diff", "--quiet", siste, "HEAD", "--", BRIEF)
    if kode == 0:
        print(f"  briefen er uendret siden {siste} ({funnet[siste][0]})")
    else:
        _, endr = git("log", "--format=%h %ad %s", "--date=format-local:%d.%m %H:%M",
                      f"{siste}..HEAD", "--", BRIEF)
        print(f"  MERK: briefen er endret etter {siste}: {endr.strip() or 'endret'}")
    if IDAG > BRIEF_FRIST and (kode != 0 or any(funnet[n][1][:10] > BRIEF_FRIST.isoformat() for n in nye)):
        print("  MERK: endring etter innleveringsfristen 27.09")
igjen = (BRIEF_FRIST - IDAG).days
print(f"  innleveringsfrist {BRIEF_FRIST:%d.%m}: "
      + (f"{igjen} dager igjen" if igjen > 0 else "i dag" if igjen == 0 else "passert, briefen skal ikke endres"))

# 8. README-lenkene (samme logikk som tests/test_readme.py)
print("\n== 8 README-LENKENE")
readme = les("README.md") or ""
lenker = re.findall(r"\]\(([^)\s]+)\)", readme)
lokale = [l for l in lenker if not l.startswith(("http://", "https://", "mailto:", "#"))]
brutt = [l for l in lokale if not (REPO / l.split("#", 1)[0]).exists()]
print(f"  {len(lokale)} lokale lenker, {len(brutt)} peker paa noe som ikke finnes"
      + (f": {brutt}" if brutt else ""))

# 9. Lekkasjesjekk: filer som ikke skal vaere der, og noekler i innhold
print("\n== 9 LEKKASJESJEKK")
_, filer = git("ls-files")
filer = filer.splitlines()
feil_filer = []
for f in filer:
    p = PurePosixPath(f)
    if p.name == ".env" or (p.name.startswith(".env.") and p.name != ".env.example"):
        feil_filer.append(f)
    elif f.startswith(("data/", "_privat/")):
        feil_filer.append(f)
    elif p.suffix in (".db", ".sqlite", ".sqlite3", ".parquet", ".pkl", ".xlsx"):
        feil_filer.append(f)
    elif p.suffix in (".csv", ".json", ".jsonl") and not f.startswith((".agents/", ".claude/", "_bmad/")):
        feil_filer.append(f)
MOENSTRE = {
    "EODHD_API_KEY med verdi": r"EODHD_API_KEY\s*=\s*[\"']?[A-Za-z0-9._-]{8,}",
    "api_token med verdi": r"api_token=(?!demo\b)[A-Za-z0-9._-]{8,}",
    "EODHD-noekkelformat": r"\b[0-9a-f]{12,16}\.[0-9]{6,10}\b",
    "Anthropic-noekkel": r"sk-ant-[A-Za-z0-9_-]{20,}",
    "OpenAI-noekkel": r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}",
    "AWS-noekkel": r"\bAKIA[0-9A-Z]{16}\b",
    "GitHub-token": r"\bgh[pousr]_[A-Za-z0-9]{36,}\b",
    "Google-noekkel": r"\bAIza[0-9A-Za-z_-]{35}\b",
}
treff = []
for f in filer:
    p = REPO / f
    try:
        if p.stat().st_size > 2_000_000:
            continue
        tekst = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        continue
    for navn, m in MOENSTRE.items():
        for t in re.finditer(m, tekst):
            treff.append(f"{f}:{tekst.count(chr(10), 0, t.start()) + 1} ({navn})")
_, diff = git("log", "-p", f"--since={FRA.isoformat()}", "--format=@@%h", "--no-color")
commit, fil = "", ""
for linje in diff.splitlines():
    if linje.startswith("@@") and not linje.startswith("@@ "):
        commit = linje[2:]
    elif linje.startswith("+++ "):
        fil = linje[6:] if linje.startswith("+++ b/") else linje[4:]
    elif linje.startswith("+") and not linje.startswith("+++"):
        for navn, m in MOENSTRE.items():
            if re.search(m, linje):
                treff.append(f"commit {commit}, {fil} ({navn}, lagt til siste doegn)")
print(f"  {len(filer)} sporede filer; {len(feil_filer)} som ikke skal vaere der; "
      f"{len(treff)} mulige noekler")
for f in feil_filer[:20]:
    print(f"  FIL: {f}")
for t in treff[:20]:
    print(f"  NOEKKEL?: {t}")

# 10. Aktivitet siste 7 dager
print("\n== 10 AKTIVITET SISTE 7 DAGER")
_, sl = git("shortlog", "-sn", f"--since={(NAA - timedelta(days=7)).isoformat()}", "HEAD")
print("  commits per forfatter: " + ("; ".join(" ".join(l.split()[1:]) + " " + l.split()[0]
                                            for l in sl.splitlines()) or "ingen"))
_, med = git("log", f"--since={(NAA - timedelta(days=7)).isoformat()}",
             "--format=%(trailers:key=Co-authored-by,valueonly)")
for navn in ("Joakim Lund", "Marian Osen"):
    print(f"  commits med {navn} som medforfatter (regel 20): "
          f"{sum(navn in l for l in med.splitlines())}")

# 11. Tall i gaarsdagens dokumentendringer, til kontrollregning
print("\n== 11 LINJER MED TALL LAGT TIL I .md SISTE DOEGN (til kontrollregning)")
_, diff = git("log", "-p", "--reverse", f"--since={FRA.isoformat()}", "--format=@@%h", "--no-color",
              "--", "*.md", ":(exclude)docs/ai-prompts/*")
fil, nr, vist, rettet, sett = "", 0, 0, 0, set()
for linje in diff.splitlines():
    if linje.startswith("+++ "):
        fil = linje[6:]
    elif linje.startswith("@@ "):
        nr = int(re.search(r"\+(\d+)", linje)[1]) - 1
    elif linje.startswith("+") and not linje.startswith("+++"):
        nr += 1
        innhold = linje[1:]
        if re.search(r"\*Rettet \d{4}-\d\d-\d\d", innhold):
            rettet += 1
        tall = re.findall(r"(?<![\w.-])\d+(?:[.,]\d+)?\s*%?", re.sub(r"`[^`]*`|\d{4}-\d\d-\d\d|\d\d?\.\d\d?\.\d{4}", "", innhold))
        if len(tall) >= 2 and vist < 120 and (fil, innhold.strip()) not in sett:
            sett.add((fil, innhold.strip()))
            print(f"  {fil}:{nr}: {innhold.strip()[:220]}")
            vist += 1
    elif not linje.startswith("-"):
        nr += 1 if linje.startswith(" ") else 0
print(f"  ({vist} linjer vist; {rettet} nye «Rettet»-merknader siste doegn)")
