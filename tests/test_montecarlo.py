import pytest

from ff_magic.dataset import load_dataset
from ff_magic.montecarlo import simulate


@pytest.fixture
def ds(fixture_dir):
    return load_dataset(fixture_dir)


def test_reproducible(ds):
    a = simulate(ds, scope="all", draws=500)
    b = simulate(ds, scope="all", draws=500)
    assert a == b


def test_capped_event_always_first(ds):
    r = simulate(ds, scope="all", draws=2000)
    top = r["scenes"]["ev-fa-02"]
    assert top["p_rank"][1] == 1.0
    assert top["median_rank"] == 1


def test_draws_stay_inside_envelope(ds):
    r = simulate(ds, scope="all", draws=2000)
    s = r["scenes"]["ev-fa-01"]
    assert 3 <= s["p10"] <= s["p50"] <= s["p90"] <= 7


def test_tiers(ds):
    r = simulate(ds, scope="all", draws=2000)
    # ev-fa-02 (>=13) always beats the rest, so it sits alone in tier 1.
    assert r["scenes"]["ev-fa-02"]["tier"] == 1
    # ev-fa-01 (3..7) and ev-fb-01 (4..6) overlap heavily, so they share a tier.
    assert r["scenes"]["ev-fa-01"]["tier"] == r["scenes"]["ev-fb-01"]["tier"] == 2


def test_rate_stability_only_for_eligible(tmp_data):
    from ff_magic.dataset import load_dataset
    d, mutate = tmp_data
    # make every fixture character board-eligible by lowering thresholds
    import yaml
    cfg = yaml.safe_load((d / "config.yaml").read_text())
    cfg["board_min_events"] = 1
    cfg["board_min_minutes"] = 1
    (d / "config.yaml").write_text(yaml.safe_dump(cfg))
    r = simulate(load_dataset(d), scope="all", draws=1000)
    assert set(r["rates"]) == {"dom", "brian", "hobbs"}
    # dom: >=19 MU over 80 min is far above brian's 5 MU over 48 min
    assert r["rates"]["dom"]["median_rank"] == 1
    assert r["rates_note"].startswith("per-character minutes drawn uniformly")


def test_rate_stability_empty_when_nobody_eligible(ds):
    r = simulate(ds, scope="all", draws=200)
    assert r["rates"] == {}
