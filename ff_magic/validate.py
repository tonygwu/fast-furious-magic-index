"""Rule checks over a loaded dataset. Returns every failure; never stops at the first."""
from collections import Counter
from dataclasses import dataclass, field

from .dataset import Dataset
from .magic import on_grid

ALLOWED_ROLES = {
    "physics": {"controller", "occupant"},
    "survival": {"survivor"},
    "skill": {"performer"},
    "coincidence": {"controller", "occupant", "performer", "survivor", "beneficiary"},
}
PLOT_KINDS = {"plot", "screenplay", "bts", "analysis"}  # any independent account of what is on screen


@dataclass
class Report:
    n_checks: int = 0
    failures: list[str] = field(default_factory=list)

    def check(self, ok: bool, msg: str):
        self.n_checks += 1
        if not ok:
            self.failures.append(msg)


def _dupes(ids):
    return [k for k, v in Counter(ids).items() if v > 1]


def validate(ds: Dataset) -> Report:
    r = Report()
    cfg = ds.config
    films = {f.id for f in ds.films}
    chars = {c.id for c in ds.characters}
    sources = {s.id: s for s in ds.sources}
    refs = {x.id for x in ds.references}

    for name, ids in [
        ("film", [f.id for f in ds.films]),
        ("character", [c.id for c in ds.characters]),
        ("source", list(s.id for s in ds.sources)),
        ("reference", [x.id for x in ds.references]),
        ("event", [e.id for _, e in ds.events]),
        ("plot_armor", [p.id for p in ds.plot_armor]),
        ("rejected", [x.id for x in ds.rejected]),
        ("event file", [f.film for f in ds.event_files]),
        ("presence log", [p.film for p in ds.presence]),
    ]:
        r.check(not _dupes(ids), f"duplicate {name} ids: {_dupes(ids)}")

    for x in ds.references:
        r.check(x.source in sources, f"reference {x.id}: unknown source {x.source}")

    r.check({f.film for f in ds.event_files} == films, f"event files {sorted(f.film for f in ds.event_files)} != films {sorted(films)}")

    for fid, ev in ds.events:
        w = ev.id
        r.check(fid in films, f"{w}: unknown film {fid}")
        r.check(ev.id.startswith(f"ev-{fid}-"), f"{w}: id must start with ev-{fid}-")
        for p in ev.participants:
            r.check(p in chars, f"{w}: unknown character {p} in participants")
        for s in ev.plot_sources:
            r.check(s in sources, f"{w}: unknown source {s}")
        plot_srcs = {s for s in ev.plot_sources if s in sources and sources[s].kind in PLOT_KINDS}
        r.check(len(plot_srcs) >= cfg.min_plot_sources_ranked,
                f"{w}: needs >= {cfg.min_plot_sources_ranked} independent plot sources, has {len(plot_srcs)}")
        r.check(not _dupes([c.id for c in ev.components]), f"{w}: duplicate component ids")
        central = 0.0
        for c in ev.components:
            cw = f"{w}/{c.id}"
            m = c.mu
            central += m.central
            for v in (m.low, m.central, m.high):
                r.check(on_grid(v, cfg.mu_step), f"{cw}: MU {v} is off the {cfg.mu_step} grid")
            r.check(0 <= m.low <= m.central <= m.high, f"{cw}: need 0 <= low <= central <= high, got {m}")
            r.check(m.high <= cfg.record_horizon_mu, f"{cw}: exceeds record horizon {cfg.record_horizon_mu}")
            if c.capped:
                r.check(m.low == m.central == m.high == cfg.record_horizon_mu,
                        f"{cw}: capped components must sit exactly at the record horizon")
                # A cap asserts a measured hard limit, so it must name the quantity it measured.
                r.check(len(c.references) > 0, f"{cw}: capped component must cite at least one reference")
            else:
                # The cap, not the evidence label, is what claims impossibility. Uncapped reasoning
                # may not argue a hard limit: either cap it, or state the margin as a judgment.
                claim_text = c.reasoning.lower().replace("not a hard limit", "").replace("not hard-limited", "")
                r.check("hard limit" not in claim_text,
                        f"{cw}: uncapped component argues a hard limit; cap it or reword")
            if c.evidence == "E4":
                r.check(m.high <= cfg.judgment_cap_mu, f"{cw}: E4 exceeds judgment cap {cfg.judgment_cap_mu}")
            r.check(bool(c.reasoning.strip()), f"{cw}: empty reasoning")
            r.check(bool(c.dependence.strip()), f"{cw}: empty dependence note")
            r.check(bool(c.subtype.startswith(c.category + ".")), f"{cw}: subtype {c.subtype} not under {c.category}")
            for ref in c.references:
                r.check(ref in refs, f"{cw}: unknown reference {ref}")
            r.check(len(c.credits) > 0, f"{cw}: no credited character")
            r.check(not _dupes([k.character for k in c.credits]), f"{cw}: character credited twice")
            for k in c.credits:
                r.check(k.character in chars, f"{cw}: unknown character {k.character}")
                r.check(k.character in ev.participants, f"{cw}: {k.character} is not a participant")
                r.check(k.role in ALLOWED_ROLES[c.category], f"{cw}: role {k.role} not allowed for {c.category}")
        r.check(central >= cfg.event_threshold_mu, f"{w}: central {central} below event threshold {cfg.event_threshold_mu}")

    for p in ds.plot_armor:
        r.check(p.film in films, f"{p.id}: unknown film")
        r.check(len(p.sources) >= 1 and all(s in sources for s in p.sources), f"{p.id}: bad sources")
        for c in p.characters:
            r.check(c in chars, f"{p.id}: unknown character {c}")
        r.check(bool(p.justification.strip()), f"{p.id}: empty justification")

    event_ids = {e.id for _, e in ds.events}
    for x in ds.rejected:
        r.check(x.film in films, f"{x.id}: unknown film")
        if x.reason == "merged":
            r.check(x.merged_into in event_ids, f"{x.id}: merged_into {x.merged_into} is not an event")

    r.check({p.film for p in ds.presence} == films, f"presence logs {sorted(p.film for p in ds.presence)} != films")
    for log in ds.presence:
        if log.film not in films:
            continue
        runtime = ds.film(log.film).runtime_min
        sc = sorted(log.scenes, key=lambda s: s.start)
        r.check(sc[0].start == 0, f"presence {log.film}: first scene must start at 0")
        for a, b in zip(sc, sc[1:]):
            r.check(a.end == b.start, f"presence {log.film}: scenes {a.n}->{b.n} not contiguous ({a.end} vs {b.start})")
        for s in sc:
            r.check(s.end > s.start, f"presence {log.film}: scene {s.n} has non-positive length")
            for c in s.characters:
                r.check(c in chars, f"presence {log.film}: unknown character {c} in scene {s.n}")
        r.check(abs(sc[-1].end - runtime) <= cfg.runtime_tolerance * runtime,
                f"presence {log.film}: log ends at {sc[-1].end}, runtime {runtime}")
    return r
