from __future__ import annotations

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
ROOT_DIR = PACKAGE_DIR.parent
TEMPLATES_DIR = ROOT_DIR / "templates"
DATA_DIR = ROOT_DIR / "data"
DEFAULT_CATEGORIES_JSON = DATA_DIR / "categories.json"
ANALYSIS_TEMPLATE = TEMPLATES_DIR / "analysis_tab_template.xlsx"
DEFAULT_ANALYSIS_NAME = "2026-Collection Analysis.xlsx"


def ensure_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR
