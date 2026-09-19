import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_script", ROOT / "scripts" / "build.py")
build_script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_script)


def test_build_outputs_consistent(fixture_dir, tmp_path):
    js = tmp_path / "data.js"
    notes = tmp_path / "notes.md"
    build_script.build(fixture_dir, tmp_path / "build", js, notes)
    site = json.loads((tmp_path / "build" / "site.json").read_text())
    assert js.read_text().count("window.FF_DATA") == 1
    for scope in ("all", "saga"):
        s = site["scopes"][scope]
        # every scene total equals the sum of its components in the detail record
        for t in s["scenes"]:
            comps = site["events"][t["id"]]["components"]
            assert t["central"] == sum(c["mu"]["central"] for c in comps)
        # every character total equals the sum of components crediting them
        for ch in s["characters"]:
            tot = sum(c["mu"]["central"] for eid in {x["id"] for x in s["scenes"]}
                      for c in site["events"][eid]["components"]
                      if any(k["character"] == ch["id"] for k in c["credits"]))
            assert ch["central"] == tot
        assert sum(f["central"] for f in s["films"]) == sum(t["central"] for t in s["scenes"])
    assert "ev-fa-02" in notes.read_text()


def test_build_refuses_invalid_data(tmp_data, tmp_path):
    d, mutate = tmp_data
    mutate("events/fa.yaml", lambda doc: doc["events"][0]["components"][0]["mu"].update(central=3.3))
    with pytest.raises(SystemExit):
        build_script.build(d, tmp_path / "b", None, None)


def test_committed_outputs_match_fresh_build(tmp_path):
    """build/, web/data.js and docs/scene-notes.md are committed; they must equal a fresh build of data/."""
    js, notes = tmp_path / "data.js", tmp_path / "scene-notes.md"
    build_script.build(ROOT / "data", tmp_path / "build", js, notes)
    assert js.read_bytes() == (ROOT / "web" / "data.js").read_bytes(), "web/data.js is stale: run scripts/build.py"
    assert notes.read_bytes() == (ROOT / "docs" / "scene-notes.md").read_bytes(), "docs/scene-notes.md is stale"
    for p in sorted((tmp_path / "build").rglob("*.json")):
        rel = p.relative_to(tmp_path / "build")
        assert p.read_bytes() == (ROOT / "build" / rel).read_bytes(), f"build/{rel} is stale"
