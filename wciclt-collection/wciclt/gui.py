from __future__ import annotations

import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

from .generate import discover_categories, generate_week, sync_categories_across
from .models import SERVICE_DROPDOWN, Service, ServiceType, WeekPlan, service_type_from_value
from .paths import DEFAULT_ANALYSIS_NAME, ROOT_DIR


def _sunday_on_or_after(day: date) -> date:
    return day + timedelta(days=(6 - day.weekday()) % 7)


def launch() -> int:
    app = Path(__file__).with_name("streamlit_app.py")
        return subprocess.call(
            [sys.executable, "-m", "streamlit", "run", str(app), "--server.headless", "true"],
            cwd=str(ROOT_DIR),
        )


def default_week_end() -> date:
    return _sunday_on_or_after(date.today())


def services_from_rows(rows: list[dict]) -> list[Service]:
    services: list[Service] = []
    for row in rows:
        if not row.get("include", True):
            continue
        stype = row["service_type"]
        if not isinstance(stype, ServiceType):
            stype = service_type_from_value(str(stype))
        services.append(
            Service(
                service_date=row["service_date"],
                service_type=stype,
                details=row.get("details") or "",
                recorded_by=row.get("recorded_by") or "",
                session_suffix=row.get("session_suffix") or "",
            )
        )
    return services


def run_from_gui_state(
    week_end: date,
    week_start: date | None,
    rows: list[dict],
    categories: list[str],
    analysis_path: Path,
    output_dir: Path,
    write_report: bool = True,
    write_analysis: bool = True,
    sync_existing: bool = False,
):
    plan = WeekPlan(
        week_end=week_end,
        week_start=week_start,
        services=services_from_rows(rows),
    )
    return generate_week(
        plan,
        analysis_path=analysis_path,
        output_dir=output_dir,
        categories=categories,
        write_report=write_report,
        write_analysis=write_analysis,
        sync_existing_tabs=sync_existing,
    )


def sync_only(analysis_path: Path, categories: list[str]):
    return sync_categories_across(analysis_path, categories)


def load_categories(analysis_path: Path) -> list[str]:
    return discover_categories(analysis_path if analysis_path.exists() else None)


def default_paths() -> tuple[Path, Path]:
    output = ROOT_DIR / "output"
    return output / DEFAULT_ANALYSIS_NAME, output
