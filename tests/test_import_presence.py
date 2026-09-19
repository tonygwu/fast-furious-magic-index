import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("import_presence", ROOT / "scripts" / "import_presence.py")
ip = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ip)


@pytest.mark.parametrize("s,expect", [("16", 16), ("~1:52", 112), ("1:39:42", 99.7), ("0:07", 7)])
def test_parse_time(s, expect):
    assert ip.parse_time(s) == pytest.approx(expect)


def test_split_names_strips_parentheticals():
    assert ip.split_names("Dom, Letty (driver) and Roman; Tej plus Kiet") == ["Dom", "Letty", "Roman", "Tej", "Kiet"]


def test_crosscut_split_is_contiguous_and_even():
    doc = ip.convert("ff09")
    spans = [(s["start"], s["end"]) for s in doc["scenes"] if s["n"] in (16, 17)]
    assert spans == [(104, 118), (118, 130)]


def test_unmapped_name_raises(monkeypatch):
    real = ip.IGNORE
    monkeypatch.setattr(ip, "IGNORE", real - {"Fernando"})
    with pytest.raises(SystemExit, match="Fernando"):
        ip.convert("ff08")


def test_generated_logs_match_research():
    import yaml
    for p in sorted((ROOT / "data" / "screen_time").glob("*.yaml")):
        film = p.stem
        assert yaml.safe_load(p.read_text()) == ip.convert(film), f"{p} is stale; rerun scripts/import_presence.py {film}"
