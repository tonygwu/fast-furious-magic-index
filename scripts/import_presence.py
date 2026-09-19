"""Convert the presence-log table in research/<film>.md into data/screen_time/<film>.yaml.

Names are mapped through characters.yaml aliases. Untracked names must appear in IGNORE; any other
name raises, so a typo cannot silently drop a character's minutes. Group labels are expanded by
explicit per-film rules below (each one is a judgment call, listed here so it can be reviewed)."""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

FILM_OVERRIDES = {
    "ff06": {"Shaw": ["owen"]},
    "hs": {"Shaw": ["deckard"]},
    "ff07": {"same five": ["dom", "brian", "letty", "roman", "tej"]},
    "ff05": {"heist team": ["roman", "tej", "han", "gisele"]},
    "ff09": {"Full main cast": ["dom", "letty", "mia", "roman", "tej", "ramsey", "han", "elle"]},
}
IGNORE = {
    "none", "—", "crew", "mercenary crew", "Hobbs family", "unnamed trucker", "unnamed rival drivers", "police",
    "unnamed henchmen", "unnamed racers", "Verone's men", "Kamata's men", "Han's old crew", "mechanic",
    "unnamed FBI/henchmen", "unnamed police", "judge", "background racers", "Jakande's mercenaries", "Otto's men",
    "unnamed flight attendant", "unnamed MI6 team", "unnamed Eteon guards", "unnamed Hobbs relatives",
    "unnamed Eteon soldiers", "in the post-credits scene", "Full main cast", "same five", "heist team",
    # named but untracked (never credited with a scored component)
    "Agent Markham", "Agent Bilkins", "Bilkins", "Enrique", "Edwin", "Tanner", "Stasiak", "Michael Stasiak",
    "David Park", "Zizi", "Diogo", "Jack", "Hector", "Orange Julius", "Agent Dunn", "Detective Whitworth",
    "Lt. Boswell", "Morimoto", "Kamata", "Penning", "Dwight Mueller", "Adolfson", "Sam", "Locke",
    "Andreiko", "Sefina", "Jonah", "Danny", "Clay", "Cindy", "Sean's mother", "Cara", "Trinh", "Alex",
    "Fusco", "Wilkes", "Macroy", "Chato", "Kara", "young Dom Toretto", "young Jakob Toretto", "Kenny Linder",
    "Buddy", "Abuelita Toretto", "Bowie", "Loeb", "Dinkley", "Madam M", "Fernando", "Raldo", "Hobbs's daughter",
}


# Cross-cut sequences the research logged as overlapping rows. Judgment: split the overlap evenly.
# ff09 rows 16 (Tbilisi ground, 104-124) and 17 (space, ~112-~130) overlap for 12 minutes.
CROSSCUT_SPLITS = {
    ("ff09", 16): [(104, 118)],
    ("ff09", 17): [(118, 130)],
}


def parse_time(s: str) -> float:
    s = s.strip().lstrip("~").strip()
    parts = s.split(":")
    if len(parts) == 1:
        return float(parts[0])
    if len(parts) == 2:  # h:mm
        return int(parts[0]) * 60 + float(parts[1])
    if len(parts) == 3:  # h:mm:ss
        return int(parts[0]) * 60 + int(parts[1]) + float(parts[2]) / 60
    raise ValueError(f"bad time {s!r}")


def split_names(cell: str) -> list[str]:
    cell = re.sub(r"\([^)]*\)", "", cell)
    out = []
    for n in re.split(r",|;| and |\bplus\b", cell):
        n = n.strip(" .*")
        if n:
            out.append(n)
    return out


def convert(film: str) -> dict:
    alias = {}
    for c in yaml.safe_load((ROOT / "data" / "characters.yaml").read_text()):
        for a in c["aliases"]:
            alias[a] = [c["id"]]
    alias.update(FILM_OVERRIDES.get(film, {}))
    text = (ROOT / "research" / f"{film}.md").read_text()
    sec = text.split("## Presence log", 1)[1]
    rows = [l for l in sec.splitlines() if l.startswith("|") and not set(l) <= set("|-: ")][1:]
    scenes = []
    for r in rows:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        n, start, end, title, who = cells[0], cells[1], cells[2], " | ".join(cells[3:-1]), cells[-1]
        if not re.search(r"\d", start) or not re.search(r"\d", end):
            print(f"WARNING {film} scene {n}: untimed row excluded from minutes: {title!r} [{who}]")
            continue
        ids = []
        for name in split_names(who):
            if name in alias:
                ids += [i for i in alias[name] if i not in ids]
            elif name not in IGNORE:
                raise SystemExit(f"{film} scene {n}: unmapped name {name!r} (add an alias or IGNORE entry)")
        spans = CROSSCUT_SPLITS.get((film, int(n)), [(parse_time(start), parse_time(end))])
        for a, b in spans:
            scenes.append({"n": int(n), "start": round(a, 2), "end": round(b, 2), "title": title, "characters": ids})
    return {"film": film,
            "anchors": [f"research/{film}.md presence log (proportional estimate unless the research file lists hard anchors)"],
            "scenes": scenes}


if __name__ == "__main__":
    for film in sys.argv[1:]:
        doc = convert(film)
        out = ROOT / "data" / "screen_time" / f"{film}.yaml"
        out.write_text(f"# GENERATED from research/{film}.md by scripts/import_presence.py\n"
                       + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=200))
        print(f"{film}: {len(doc['scenes'])} scenes, ends at {doc['scenes'][-1]['end']} min")
