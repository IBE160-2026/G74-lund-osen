"""Gjoer utskriften fra morgensjekk.py om til en kommentar i saken «Morgensjekk».

Bruk: python3 morgenrapport.py <brukernavn> <lenke til kjoeringen> < utskrift.txt

Bare standardbiblioteket. Seksjon 11 tas ikke med: den er grunnlaget for
kontrollregningen, som bare Claude-kjoeringen gjoer.
"""
import re
import sys
from datetime import date

UKEDAGER = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
MERKER = ("MERK:", "FIL:", "NOEKKEL?:")

brukernavn, kjoering = sys.argv[1], sys.argv[2]
sys.stdin.reconfigure(encoding="utf-8")
linjer = sys.stdin.read().splitlines()

# Datoen staar i foerste linje: «== MORGENSJEKK 2026-09-26 (uke 39), ...»
m = re.search(r"(\d{4})-(\d\d)-(\d\d)", linjer[0]) if linjer else None
if not m:
    sys.exit("Fant ingen dato i foerste linje av utskriften")
dag = date(int(m[1]), int(m[2]), int(m[3]))

merket = [l.strip() for l in linjer if l.lstrip().startswith(MERKER)]
tittel = f"Morgensjekk {UKEDAGER[dag.weekday()]} {dag:%d.%m}: " + (
    f"{len(merket)} ting å se på" if merket else "alt i orden")

# Seksjon 1 til 10. Fra seksjon 1 bare overskriften og tellelinja, ikke
# commitlista.
blokk, seksjon = [], None
for linje in linjer:
    m = re.match(r"^== (\d+) ", linje)
    if m:
        seksjon = int(m[1])
    elif linje.startswith("== "):
        seksjon = None
    if seksjon is None or seksjon > 10:
        continue
    if seksjon == 1 and linje.strip() and not linje.startswith(("== ", "antall=")):
        continue
    blokk.append(linje)
while blokk and not blokk[-1].strip():
    blokk.pop()

# Gjerdet er lengre enn den lengste rekka av backticks i innholdet.
lengste = max((len(r) for r in re.findall(r"`+", "\n".join(blokk))), default=0)
gjerde = "`" * max(3, lengste + 1)

ut = [tittel, ""]
if merket:
    ut += merket + [""]
ut += [f"{gjerde}text", *blokk, gjerde, ""]
# Nevningen staar utenfor tekstblokken, ellers varsler ikke GitHub.
ut += [f"@{brukernavn} Kontrollregningen og forslaget til dagens hovedoppgave "
       f"står i Claude-kjøringen.", "", f"Kjøringen på GitHub: {kjoering}"]
sys.stdout.reconfigure(encoding="utf-8")
print("\n".join(ut))
