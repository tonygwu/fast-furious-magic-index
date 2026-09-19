import pytest

from ff_magic.dataset import load_dataset
from ff_magic.aggregate import event_totals, character_totals, film_totals, screen_time


@pytest.fixture
def ds(fixture_dir):
    return load_dataset(fixture_dir)


def test_event_totals_sum_components(ds):
    t = {e["id"]: e for e in event_totals(ds, scope="all")}
    assert (t["ev-fa-01"]["low"], t["ev-fa-01"]["central"], t["ev-fa-01"]["high"]) == (3, 5, 7)
    assert t["ev-fa-01"]["lower_bound"] is False
    assert (t["ev-fa-02"]["low"], t["ev-fa-02"]["central"], t["ev-fa-02"]["high"]) == (13, 14, 15)
    assert t["ev-fa-02"]["lower_bound"] is True
    assert t["ev-fa-01"]["by_category"] == {"physics": 3, "survival": 2, "skill": 0, "coincidence": 0}


def test_scope_excludes_spinoff(ds):
    ids = {e["id"] for e in event_totals(ds, scope="saga")}
    assert ids == {"ev-fa-01", "ev-fa-02"}
    with pytest.raises(ValueError):
        event_totals(ds, scope="everything")


def test_character_full_credit_and_buckets(ds):
    c = {r["id"]: r for r in character_totals(ds, scope="all")}
    assert c["dom"]["central"] == 19
    assert c["dom"]["by_category"] == {"physics": 15, "survival": 2, "skill": 2, "coincidence": 0}
    assert c["dom"]["by_mode"] == {"caused": 17, "endured": 2, "luck": 0}
    assert c["dom"]["lower_bound"] is True
    assert c["brian"]["central"] == 5
    assert c["brian"]["by_mode"] == {"caused": 0, "endured": 5, "luck": 0}
    assert c["hobbs"]["central"] == 5
    assert c["dom"]["n_events"] == 2
    assert c["dom"]["signature_event"] == "ev-fa-02"


def test_character_totals_not_additive_across_characters(ds):
    # Shared components credit every character in full, so the character sum exceeds the scene sum.
    ev = sum(e["central"] for e in event_totals(ds, scope="all"))
    ch = sum(r["central"] for r in character_totals(ds, scope="all"))
    assert ch > ev


def test_saga_scope_character(ds):
    c = {r["id"]: r for r in character_totals(ds, scope="saga")}
    assert "hobbs" not in c


def test_screen_time_and_rate(ds):
    st = screen_time(ds, scope="all")
    assert st["dom"] == {"low": 60.0, "central": 80.0, "high": 100.0, "films": 1}
    c = {r["id"]: r for r in character_totals(ds, scope="all")}
    assert c["dom"]["rate_per_100"]["central"] == pytest.approx(19 / 80 * 100)
    # rate low = MU low / minutes high; rate high = MU high / minutes low
    assert c["dom"]["rate_per_100"]["low"] == pytest.approx(c["dom"]["low"] / 100 * 100)
    assert c["dom"]["rate_per_100"]["high"] == pytest.approx(c["dom"]["high"] / 60 * 100)


def test_board_eligibility(ds):
    c = {r["id"]: r for r in character_totals(ds, scope="all")}
    assert c["dom"]["board_eligible"] is False  # only 2 events in the fixture
    assert "events" in c["dom"]["ineligible_reason"]


def test_film_totals(ds):
    f = {r["id"]: r for r in film_totals(ds, scope="all")}
    assert f["fa"]["central"] == 19
    assert f["fa"]["n_events"] == 2
    assert f["fa"]["per_minute"] == pytest.approx(0.19)
    assert f["fa"]["median_event"] == pytest.approx(9.5)
    assert f["fb"]["central"] == 5
    assert f["fa"]["n_rejected"] == 1
