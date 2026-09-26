"""Scene, character, and film totals. Character totals give full credit to every credited
character, so they are an additive absurdity index and do not sum to scene totals."""
from collections import defaultdict
from statistics import median

from .dataset import CATEGORIES, Dataset

SCOPES = ("all", "saga")


def _films_in_scope(ds: Dataset, scope: str) -> set[str]:
    if scope not in SCOPES:
        raise ValueError(f"scope must be one of {SCOPES}, got {scope!r}")
    return {f.id for f in ds.films if scope == "all" or not f.spinoff}


def mode_of(category: str, role: str) -> str:
    if category == "coincidence":
        return "luck"
    if category == "skill" or (category == "physics" and role == "controller"):
        return "caused"
    return "endured"  # survival, or riding along as a physics occupant


def event_totals(ds: Dataset, scope: str) -> list[dict]:
    keep = _films_in_scope(ds, scope)
    out = []
    for fid, e in ds.events:
        if fid not in keep:
            continue
        cat = {k: 0.0 for k in CATEGORIES}
        for c in e.components:
            cat[c.category] += c.mu.central
        out.append({
            "id": e.id,
            "film": fid,
            "title": e.title,
            "low": sum(c.mu.low for c in e.components),
            "central": sum(c.mu.central for c in e.components),
            "high": sum(c.mu.high for c in e.components),
            "lower_bound": any(c.capped for c in e.components),
            "n_capped": sum(c.capped for c in e.components),
            "by_category": cat,
            "primary_category": max(cat, key=cat.get),
            "characters": sorted({k.character for c in e.components for k in c.credits}),
        })
    out.sort(key=lambda x: (-x["central"], -x["high"], x["id"]))
    return out


def screen_time(ds: Dataset, scope: str) -> dict[str, dict]:
    keep = _films_in_scope(ds, scope)
    cfg = ds.config
    raw = defaultdict(float)
    films = defaultdict(set)
    for log in ds.presence:
        if log.film not in keep:
            continue
        for s in log.scenes:
            for c in s.characters:
                raw[c] += s.end - s.start
                films[c].add(log.film)
    return {
        c: {
            "low": round(m * cfg.presence_low_factor, 6),
            "central": round(m * cfg.presence_central_factor, 6),
            "high": round(m * cfg.presence_high_factor, 6),
            "films": len(films[c]),
        }
        for c, m in raw.items()
    }


def character_totals(ds: Dataset, scope: str) -> list[dict]:
    keep = _films_in_scope(ds, scope)
    cfg = ds.config
    st = screen_time(ds, scope)
    names = {c.id: c.name for c in ds.characters}
    acc: dict[str, dict] = {}
    for fid, e in ds.events:
        if fid not in keep:
            continue
        for c in e.components:
            for k in c.credits:
                a = acc.setdefault(k.character, {
                    "low": 0.0, "central": 0.0, "high": 0.0, "lower_bound": False,
                    "by_category": {x: 0.0 for x in CATEGORIES},
                    "by_mode": {"caused": 0.0, "endured": 0.0, "luck": 0.0},
                    "events": defaultdict(float), "films": set(),
                })
                a["low"] += c.mu.low
                a["central"] += c.mu.central
                a["high"] += c.mu.high
                a["lower_bound"] |= c.capped
                a["by_category"][c.category] += c.mu.central
                a["by_mode"][mode_of(c.category, k.role)] += c.mu.central
                a["events"][e.id] += c.mu.central
                a["films"].add(fid)
    pap = defaultdict(int)
    for p in ds.plot_armor:
        if p.film in keep:
            for c in p.characters:
                pap[c] += p.level
    out = []
    for cid, a in acc.items():
        t = st.get(cid)
        n_events = len(a["events"])
        reasons = []
        if n_events < cfg.board_min_events:
            reasons.append(f"{n_events} events < {cfg.board_min_events}")
        if t is None or t["central"] < cfg.board_min_minutes:
            reasons.append(f"{0 if t is None else t['central']:.0f} min < {cfg.board_min_minutes:.0f}")
        rate = None
        if t is not None and t["low"] > 0:
            rate = {
                "low": a["low"] / t["high"] * 100,
                "central": a["central"] / t["central"] * 100,
                "high": a["high"] / t["low"] * 100,
            }
        sig = max(a["events"].items(), key=lambda kv: (kv[1], kv[0]))[0]
        out.append({
            "id": cid, "name": names[cid],
            "low": a["low"], "central": a["central"], "high": a["high"], "lower_bound": a["lower_bound"],
            "by_category": a["by_category"], "by_mode": a["by_mode"],
            "n_events": n_events, "n_films": len(a["films"]),
            "signature_event": sig,
            "minutes": t, "rate_per_100": rate,
            "plot_armor": pap.get(cid, 0),
            "board_eligible": not reasons,
            "ineligible_reason": "; ".join(reasons),
        })
    out.sort(key=lambda x: (-x["central"], x["id"]))
    return out


def film_totals(ds: Dataset, scope: str) -> list[dict]:
    keep = _films_in_scope(ds, scope)
    evs = event_totals(ds, scope)
    out = []
    for f in sorted(ds.films, key=lambda f: f.release_order):
        if f.id not in keep:
            continue
        mine = [e for e in evs if e["film"] == f.id]
        cat = {k: sum(e["by_category"][k] for e in mine) for k in CATEGORIES}
        central = sum(e["central"] for e in mine)
        out.append({
            "id": f.id, "title": f.title, "year": f.year, "release_order": f.release_order, "spinoff": f.spinoff,
            "runtime_min": f.runtime_min,
            "low": sum(e["low"] for e in mine), "central": central, "high": sum(e["high"] for e in mine),
            "lower_bound": any(e["lower_bound"] for e in mine),
            "n_events": len(mine),
            "per_minute": central / f.runtime_min,
            "median_event": median(e["central"] for e in mine) if mine else 0.0,
            "max_event": mine[0]["id"] if mine else None,
            "by_category": cat,
            "plot_armor": sum(p.level for p in ds.plot_armor if p.film == f.id),
            "n_rejected": sum(1 for x in ds.rejected if x.film == f.id),
            "n_single_source": sum(1 for x in ds.rejected if x.film == f.id and x.reason == "insufficient_sources"),
        })
    return out
