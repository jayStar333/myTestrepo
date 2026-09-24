from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def isolate_category_json(tmp_path, monkeypatch):
    json_path = tmp_path / "categories.json"
    monkeypatch.setattr("wciclt.paths.DEFAULT_CATEGORIES_JSON", json_path)
    monkeypatch.setattr("wciclt.generate.DEFAULT_CATEGORIES_JSON", json_path)
    monkeypatch.setattr("wciclt.categories.DEFAULT_CATEGORIES_JSON", json_path)
