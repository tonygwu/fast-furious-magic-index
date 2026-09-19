import shutil
from pathlib import Path

import pytest
import yaml

FIXTURE = Path(__file__).parent / "fixtures" / "data"


@pytest.fixture
def fixture_dir():
    return FIXTURE


@pytest.fixture
def tmp_data(tmp_path):
    """A writable copy of the fixture dataset, plus a helper to mutate one YAML file."""
    dst = tmp_path / "data"
    shutil.copytree(FIXTURE, dst)

    def mutate(rel, fn):
        p = dst / rel
        doc = yaml.safe_load(p.read_text())
        fn(doc)
        p.write_text(yaml.safe_dump(doc, sort_keys=False))

    return dst, mutate
