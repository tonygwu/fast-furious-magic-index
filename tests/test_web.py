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


def test_films_carry_their_single_source_count():
    """The coverage note must count candidates held back for want of a second source, not every rejection."""
    for f in SITE["scopes"]["all"]["films"]:
        expected = sum(1 for r in SITE["rejected"] if r["film"] == f["id"] and r["reason"] == "insufficient_sources")
        assert f.get("n_single_source") == expected, f"{f['id']}: n_single_source should be {expected}"


@pytest.mark.skipif(not Path(CHROME).exists(), reason="Chrome not installed")
def test_coverage_note_states_the_single_source_count():
    port = "8792"
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
    note = re.search(r'id="films-note"[^>]*>(.*?)</p>', dom, re.S).group(1)
    films = SITE["scopes"]["all"]["films"]
    top = max(sum(1 for r in SITE["rejected"] if r["film"] == f["id"] and r["reason"] == "insufficient_sources")
              for f in films)
    worst = [f["title"] for f in films
             if sum(1 for r in SITE["rejected"] if r["film"] == f["id"] and r["reason"] == "insufficient_sources") == top]
    assert f"{top} candidates held back for want of a second source" in note, note
    for t in worst:
        assert t.replace("&", "&amp;") in note or t in note, f"{t} missing from: {note}"
    assert "most for want" not in note


def _dom(query=""):
    port = "8793"
    server = subprocess.Popen(
        ["python3", "-m", "http.server", port, "--directory", str(ROOT / "web")],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        return subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--virtual-time-budget=6000",
             "--dump-dom", f"http://127.0.0.1:{port}/index.html{query}"],
            capture_output=True, text=True, timeout=120,
        ).stdout
    finally:
        server.terminate()


@pytest.mark.skipif(not Path(CHROME).exists(), reason="Chrome not installed")
def test_tabs_split_scenes_and_people():
    dom = _dom()
    for t in ["scenes", "people", "films", "method"]:
        assert f'id="tab-{t}"' in dom, f"tab {t} missing"
    assert re.search(r'id="panel-scenes"(?![^>]*hidden)', dom), "scenes panel should show by default"
    assert re.search(r'id="panel-people"[^>]*hidden', dom), "people panel should start hidden"
    dom = _dom("#people")
    assert re.search(r'id="panel-people"(?![^>]*hidden)', dom), "#people should open the people tab"


@pytest.mark.skipif(not Path(CHROME).exists(), reason="Chrome not installed")
def test_scene_rows_show_probability_characters_and_mix():
    dom = _dom()
    top = SITE["scopes"]["all"]["scenes"][0]
    assert top["p"] in dom, f"probability {top['p']} missing"
    row = re.search(r'data-id="%s".*?</button>' % re.escape(top["id"]), dom, re.S).group(0)
    for cid in top["characters"]:
        assert SITE["characters"][cid]["aliases"][0] in row, f"{cid} missing from the top row"
    for cat, v in top["by_category"].items():
        if v > 0:
            assert f'data-cat="{cat}"' in row, f"{cat} segment missing from the top row"


@pytest.mark.skipif(not Path(CHROME).exists(), reason="Chrome not installed")
def test_character_deep_link_lists_their_scenes():
    dom = _dom("?who=dom#people")
    assert 'id="who-dom"' in dom, "?who=dom should expand Dom's scene list"
    box = dom.split('id="who-dom"', 1)[1].split('class="cbar', 1)[0]
    dom_row = next(c for c in SITE["scopes"]["all"]["characters"] if c["id"] == "dom")
    for p in dom_row["scenes"]:
        title = SITE["events"][p["id"]]["title"].replace("&", "&amp;")
        assert title in box, f"{title} missing from Dom's list"


@pytest.mark.skipif(not Path(CHROME).exists(), reason="Chrome not installed")
def test_film_chart_names_each_film():
    dom = _dom("#films")
    chart = re.search(r'id="films".*?</section>', dom, re.S).group(0)
    for f in SITE["films"]:
        assert f["short"].replace("&", "&amp;") in chart, f"{f['short']} missing from the film chart"


@pytest.mark.skipif(not Path(CHROME).exists(), reason="Chrome not installed")
def test_scope_and_theme_are_two_state_switches():
    """Each control is one role=switch whose aria-checked follows the scope or theme in force."""
    def switch(dom, sid):
        return re.search(r'<button[^>]*id="%s"[^>]*>' % sid, dom).group(0)
    dom = _dom("?theme=light")
    for sid in ["scope-switch", "theme-switch"]:
        assert 'role="switch"' in switch(dom, sid), f"{sid} is not a switch"
    assert 'aria-checked="false"' in switch(dom, "scope-switch"), "default scope should be saga + H&S"
    assert 'aria-checked="false"' in switch(dom, "theme-switch"), "?theme=light should leave the switch off"
    assert 'id="scope-all"' not in dom and 'id="theme"' not in dom, "old buttons still present"
    dom = _dom("?scope=saga&theme=dark")
    assert 'aria-checked="true"' in switch(dom, "scope-switch"), "?scope=saga should turn the scope switch on"
    assert 'aria-checked="true"' in switch(dom, "theme-switch"), "?theme=dark should turn the theme switch on"
