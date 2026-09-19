"""Rank stability. Each component MU is drawn from a triangular distribution on [low, high]
with mode = central; capped components stay at the cap (they are lower bounds)."""
import numpy as np

from .aggregate import _films_in_scope, character_totals
from .dataset import Dataset


def _draw(rng, low, mode, high, n):
    if low == high:
        return np.full(n, float(low))
    return rng.triangular(low, mode, high, n)


def _ranks(mat):
    # mat: items x draws. Rank 1 = largest. Ties broken by item order (stable).
    order = np.argsort(-mat, axis=0, kind="stable")
    ranks = np.empty_like(order)
    rows = np.arange(mat.shape[0])[:, None]
    ranks[order, np.arange(mat.shape[1])] = rows + 1
    return ranks


def _summarize(ids, mat, cfg):
    ranks = _ranks(mat)
    central_order = np.argsort(-np.median(mat, axis=1), kind="stable")
    out = {}
    for i, iid in enumerate(ids):
        r = ranks[i]
        out[iid] = {
            "p10": float(np.percentile(mat[i], 10)),
            "p50": float(np.percentile(mat[i], 50)),
            "p90": float(np.percentile(mat[i], 90)),
            "median_rank": int(np.median(r)),
            "p_rank": {int(k): round(float(np.mean(r == k)), 4) for k in range(1, min(3, len(ids)) + 1)},
            "p_top3": round(float(np.mean(r <= 3)), 4),
            "p_top10": round(float(np.mean(r <= 10)), 4),
        }
    tier = 1
    prev = None
    for idx in central_order:
        if prev is not None:
            p_beat = float(np.mean(mat[prev] > mat[idx]))
            out[ids[prev]]["p_beats_next"] = round(p_beat, 4)
            if p_beat >= cfg.tier_break_prob:
                tier += 1
        out[ids[idx]]["tier"] = tier
        prev = idx
    return out


def simulate(ds: Dataset, scope: str, draws: int | None = None) -> dict:
    cfg = ds.config
    n = draws or cfg.mc_draws
    rng = np.random.default_rng(cfg.mc_seed)
    keep = _films_in_scope(ds, scope)
    ev_ids, ev_rows = [], []
    char_acc: dict[str, np.ndarray] = {}
    for fid, e in ds.events:
        if fid not in keep:
            continue
        total = np.zeros(n)
        for c in e.components:
            d = _draw(rng, c.mu.low, c.mu.central, c.mu.high, n)
            total += d
            for k in c.credits:
                char_acc[k.character] = char_acc.get(k.character, np.zeros(n)) + d
        ev_ids.append(e.id)
        ev_rows.append(total)
    char_ids = sorted(char_acc)
    elig = {c["id"]: c["minutes"]["central"] for c in character_totals(ds, scope) if c["board_eligible"]}
    rate_ids = sorted(elig)
    e = cfg.presence_char_error
    rates = (_summarize(rate_ids, np.array([
        char_acc[c] / (elig[c] * rng.uniform(1 - e, 1 + e, n)) * 100 for c in rate_ids]), cfg)
        if rate_ids else {})
    return {
        "draws": n,
        "seed": cfg.mc_seed,
        "scenes": _summarize(ev_ids, np.array(ev_rows), cfg),
        "characters": _summarize(char_ids, np.array([char_acc[c] for c in char_ids]), cfg),
        "rates": rates,
        "rates_note": f"per-character minutes drawn uniformly within +/-{cfg.presence_char_error:.0%} of central, independently",
    }
