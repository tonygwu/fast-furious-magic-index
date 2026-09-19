"""Generate docs/scene-notes.md from built site data. Never hand-edit the output."""


def _fmt(x: float) -> str:
    return f"{x:g}"


def scene_notes(site: dict) -> str:
    films = {f["id"]: f for f in site["films"]}
    srcs = site["sources"]
    lines = ["# Scene notes (GENERATED from data/ by scripts/build.py; do not edit)", ""]
    ranked = site["scopes"]["all"]["scenes"]
    for rank, t in enumerate(ranked, 1):
        e = site["events"][t["id"]]
        f = films[e["film"]]
        ge = "≥ " if t["lower_bound"] else ""
        lines += [
            f"## {rank}. {e['title']} — {f['title']} ({f['year']})",
            f"`{e['id']}` · {ge}{_fmt(t['central'])} MU (envelope {_fmt(t['low'])}–{_fmt(t['high'])}) · {t['odds']} · confidence {e['confidence']}",
            "",
            f"**Depicted.** {e['depicted']}",
        ]
        if e["inferred"]:
            lines.append(f"**Inferred.** {e['inferred']}")
        if e["in_universe_excuse"]:
            lines.append(f"**In-universe excuse (ignored for scoring).** {e['in_universe_excuse']}")
        if e["visually_unverified"]:
            lines.append("**Visually unverified:** " + "; ".join(e["visually_unverified"]))
        lines += ["", "| # | Category | Claim | Evidence | MU low / central / high | Credited |", "|---|---|---|---|---|---|"]
        for c in e["components"]:
            cap = " (cap, lower bound)" if c["capped"] else ""
            cred = ", ".join(f"{k['character']} ({k['role']})" for k in c["credits"])
            m = c["mu"]
            lines.append(f"| {c['id']} | {c['category']} | {c['claim']} | {c['evidence']} | "
                         f"{_fmt(m['low'])} / {_fmt(m['central'])} / {_fmt(m['high'])}{cap} | {cred} |")
        lines.append("")
        for c in e["components"]:
            lines.append(f"- **{c['id']}** {c['reasoning']} *Dependence:* {c['dependence']}")
        lines += ["", "Sources: " + ", ".join(f"[{srcs[s]['title']}]({srcs[s]['url']})" for s in e["plot_sources"]), ""]
    return "\n".join(lines) + "\n"
