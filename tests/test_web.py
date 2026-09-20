"""The page must not carry its own copy of any number: it renders what build/ contains."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = json.loads((ROOT / "build" / "site.json").read_text())
APP = (ROOT / "web" / "app.js").read_text()
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def data_values():
    """Every figure a reader could see, as strings."""
    vals = set()
    for scope in SITE["scopes"].values():
        for s in scope["scenes"]:
            vals |= {str(s["central"]), str(s["low"]), str(s["high"])}
        for c in scope["characters"]:
            vals.add(str(c["central"]))
            if c["rate_per_100"]:
                vals.add(str(round(c["rate_per_100"]["central"], 1)))
        for f in scope["films"]:
            vals.add(str(f["central"]))
    return {v for v in vals if v not in {"0", "0.0", "1", "1.0", "2", "2.0", "3", "3.0"}}


def test_renderer_hardcodes_no_data_value():
    """A number that belongs to the dataset must never be typed into the renderer."""
    literals = set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])", APP))
    leaked = sorted(literals & data_values())
    assert leaked == [], f"app.js hardcodes dataset values: {leaked}"


def test_renderer_reads_every_board_from_the_build():
    for key in ["scenes", "characters", "films", "rank_stability"]:
        assert key in APP, f"app.js never reads {key} from the build"
    assert "window.FF_DATA" in APP


def test_data_js_matches_site_json():
    js = (ROOT / "web" / "data.js").read_text()
    payload = js.split("window.FF_DATA = ", 1)[1].rsplit(";", 1)[0]
    assert json.loads(payload) == SITE, "web/data.js is stale: run scripts/build.py"


@pytest.mark.skipif(not Path(CHROME).exists(), reason="Chrome not installed")
def test_rendered_dom_shows_the_built_numbers(tmp_path):
    """Render the page and check the top scene's value and the event count came from the data."""
    port = "8791"
    server = subprocess.Popen(
        ["python3", "-m", "http.server", port, "--directory", str(ROOT / "web")],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        dom = subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--virtual-time-budget=6000",
             "--dump-dom", f"http://127.0.0.1:{port}/index.html"],
            capture_output=True, text=True, timeout=120,
        ).stdout
    finally:
        server.terminate()
    top = SITE["scopes"]["all"]["scenes"][0]
    expected = ("≥" if top["lower_bound"] else "") + str(round(top["central"], 1)).rstrip("0").rstrip(".")
    assert top["title"] in dom, "top scene title missing from the rendered page"
    assert expected in dom, f"top scene value {expected} missing from the rendered page"
    assert f"{len(SITE['events'])} SCORED EVENTS" in dom
