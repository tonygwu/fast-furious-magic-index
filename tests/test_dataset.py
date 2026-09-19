import pytest

from ff_magic.config import load_config, ConfigError
from ff_magic.dataset import load_dataset, DataError
from ff_magic.validate import validate


def test_fixture_loads_and_validates(fixture_dir):
    ds = load_dataset(fixture_dir)
    report = validate(ds)
    assert report.failures == [], report.failures
    assert report.n_checks > 20


def test_missing_config_key_raises(tmp_path, fixture_dir):
    text = (fixture_dir / "config.yaml").read_text().replace("mc_seed", "mc_sead")
    p = tmp_path / "config.yaml"
    p.write_text(text)
    with pytest.raises(ConfigError):
        load_config(p)


def test_unknown_field_in_event_raises(tmp_data):
    d, mutate = tmp_data
    mutate("events/fa.yaml", lambda doc: doc["events"][0].update({"vibes": "great"}))
    with pytest.raises(DataError):
        load_dataset(d)


def _fail_substrings(d):
    return " | ".join(validate(load_dataset(d)).failures)


def _comp(doc, e=0, c=0):
    return doc["events"][e]["components"][c]


@pytest.mark.parametrize(
    "mutation,expect",
    [
        (lambda doc: _comp(doc)["mu"].update(central=3.3), "grid"),
        (lambda doc: _comp(doc)["mu"].update(low=5), "low <= central <= high"),
        (lambda doc: _comp(doc)["mu"].update(high=13), "record horizon"),
        (lambda doc: _comp(doc, 1, 1)["mu"].update(high=4), "judgment cap"),
        (lambda doc: _comp(doc, 1, 0)["mu"].update(low=11), "capped"),
        (lambda doc: _comp(doc)["credits"].append({"character": "ghost", "role": "occupant"}), "unknown character"),
        (lambda doc: _comp(doc)["credits"].append({"character": "hobbs", "role": "occupant"}), "not a participant"),
        (lambda doc: _comp(doc, 1, 1)["credits"].append({"character": "brian", "role": "occupant"}), "role"),
        (lambda doc: doc["events"][0].update(plot_sources=["s1"]), "plot sources"),
        (lambda doc: doc["events"][1].update(id="ev-fa-01"), "duplicate"),
        (lambda doc: _comp(doc).update(references=["r-nope"]), "unknown reference"),
        (lambda doc: _comp(doc).update(dependence=""), "dependence"),
        (lambda doc: doc["events"][0]["components"].pop(1) and _comp(doc)["mu"].update(low=1, central=1.5, high=2), "threshold"),
    ],
)
def test_validation_catches(tmp_data, mutation, expect):
    d, mutate = tmp_data
    mutate("events/fa.yaml", mutation)
    assert expect in _fail_substrings(d)


def test_presence_log_must_cover_runtime(tmp_data):
    d, mutate = tmp_data
    mutate("screen_time/fb.yaml", lambda doc: doc["scenes"][0].update(end=80))
    assert "runtime" in _fail_substrings(d)


def test_presence_log_rejects_overlap(tmp_data):
    d, mutate = tmp_data
    mutate("screen_time/fa.yaml", lambda doc: doc["scenes"][1].update(start=50))
    assert "contiguous" in _fail_substrings(d)
