from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from openpyxl import load_workbook

from wciclt.categories import normalize_list
from wciclt.generate import discover_categories, generate_week, sync_categories_across
from wciclt.models import Service, ServiceType, WeekPlan, service_type_from_value


@pytest.fixture
def tmp_paths(tmp_path: Path):
    analysis = tmp_path / "2026-Collection Analysis.xlsx"
    output = tmp_path / "reports"
    output.mkdir()
    return analysis, output


def _week_two_services() -> WeekPlan:
    return WeekPlan(
        week_end=date(2026, 9, 27),
        services=[
            Service(date(2026, 9, 23), ServiceType.MIDWEEK, recorded_by="Bro Ernest, Sis Sandra"),
            Service(date(2026, 9, 27), ServiceType.SUNDAY, recorded_by="Bro Ernest, Sis Sandra"),
        ],
    )


def test_other_requires_details():
    plan = WeekPlan(
        week_end=date(2026, 9, 27),
        services=[Service(date(2026, 9, 24), ServiceType.OTHER)],
    )
    with pytest.raises(ValueError, match="details"):
        plan.validate()


def test_generate_two_service_week(tmp_paths):
    analysis, output = tmp_paths
    result = generate_week(_week_two_services(), analysis, output)
    assert result.tabs == ["Wed-09.23.2026", "Sun-09.27.2026"]
    assert result.report_path and result.report_path.exists()

    wb = load_workbook(analysis)
    assert "_Categories" in wb.sheetnames
    assert wb["_Categories"].sheet_state == "hidden"
    sun = wb["Sun-09.27.2026"]
    assert sun["C2"].value == "09/27/2026 - Sunday Service"
    assert sun["B1"].value == "WINNERS CHAPEL CARLOTTE"
    assert sun["B2"].value == "COLLECTIONS/DEPOSIT RECON"
    assert sun["K9"].value == "=SUM(I9*J9)"
    assert sun["E32"].value == "=SUM(E7:E31)"
    assert sun["B35"].value == "Offering"
    assert "TOTAL COLLECTIONS ANALYSIS" in [sun.cell(r, 2).value for r in range(35, 60)]
    wb.close()

    report = load_workbook(result.report_path)
    ws = report.active
    assert ws.title == "09.27.26"
    assert "Collection Report as at" in ws["A2"].value
    assert ws["A4"].value == "Date:09.23.2026"
    assert ws["B4"].value == "Midweek Service"
    assert ws["D4"].value == "Date:09.27.2026"
    assert ws["E4"].value == "Sunday Service"
    assert ws["B12"].value == "=SUM(B7:B9)"
    assert ws["A15"].value == "Offering"
    assert ws["D15"].value == "=A15"
    assert ws["B4"].value == "Midweek Service"
    assert ws["C4"].value == "Midweek Service"
    assert ws["E4"].value == "Sunday Service"
    assert ws["F4"].value == "Sunday Service"
    assert ws.row_dimensions[4].height == 117.0
    spacer_color = ws["C4"].font.color
    assert spacer_color is not None and spacer_color.theme == 1
    fill_rgb = getattr(ws["C4"].fill.fgColor, "rgb", None)
    assert fill_rgb is None or not str(fill_rgb).startswith("00")
    last_cat = 14 + len(result.categories)
    assert ws.cell(last_cat + 1, 1).value == "TOTAL"
    assert "SUM(B15:" in str(ws.cell(last_cat + 1, 2).value)
    report.close()


def test_generate_variable_service_count(tmp_paths):
    analysis, output = tmp_paths
    plan = WeekPlan(
        week_end=date(2026, 9, 6),
        services=[
            Service(date(2026, 9, 2), ServiceType.WOSE_DAY_1),
            Service(date(2026, 9, 3), ServiceType.WOSE_DAY_2),
            Service(date(2026, 9, 4), ServiceType.WOSE_DAY_3),
            Service(date(2026, 9, 6), ServiceType.SUNDAY),
            Service(date(2026, 9, 5), ServiceType.OTHER, details="Youth Night"),
        ],
    )
    result = generate_week(plan, analysis, output)
    assert len(result.tabs) == 5
    assert "Fri-09.04.2026" in result.tabs
    wb = load_workbook(result.report_path)
    ws = wb.active
    labels = [ws.cell(4, 2 + i * 3).value for i in range(5)]
    assert labels == [
        "WOSE Day 1",
        "WOSE Day 2",
        "WOSE Day 3",
        "Sunday Service",
        "Youth Night",
    ]
    wb.close()


def test_category_sync_add_remove(tmp_paths):
    analysis, output = tmp_paths
    generate_week(_week_two_services(), analysis, output)
    cats = discover_categories(analysis)
    cats.append("Mission Seed")
    cats = [c for c in cats if c != "Chairs"]
    sync_categories_across(analysis, cats)
    wb = load_workbook(analysis)
    names = [wb["_Categories"].cell(r, 1).value for r in range(2, 30) if wb["_Categories"].cell(r, 1).value]
    assert "Mission Seed" in names
    assert "Chairs" not in names
    sun = wb["Sun-09.27.2026"]
    col_b = [sun.cell(r, 2).value for r in range(35, 55)]
    assert "Mission Seed" in col_b
    assert "Chairs" not in col_b
    wb.close()


def test_cdot_and_shiloh_labels(tmp_paths):
    analysis, output = tmp_paths
    plan = WeekPlan(
        week_end=date(2026, 12, 14),
        services=[
            Service(date(2026, 12, 9), ServiceType.SHILOH_OPENING),
            Service(date(2026, 12, 10), ServiceType.SHILOH_HOUR),
            Service(date(2026, 12, 11), ServiceType.SHILOH_ENCOUNTER),
            Service(date(2026, 12, 12), ServiceType.SHILOH_IMPARTATION),
            Service(date(2026, 12, 14), ServiceType.CDOT),
        ],
    )
    result = generate_week(plan, analysis, output)
    wb = load_workbook(analysis)
    assert wb["Wed-12.09.2026"]["C2"].value == "12/09/2026 - Shiloh Opening Night"
    assert wb["Mon-12.14.2026"]["C2"].value == "12/14/2026 - CDOT"
    wb.close()
    assert result.report_path.exists()


def test_communion_is_midweek():
    assert service_type_from_value("MIDWEEK COMMUNION SVC") == ServiceType.MIDWEEK
    assert service_type_from_value("Communion") == ServiceType.MIDWEEK


def test_thanksgiving_is_one_shared_name():
    names = normalize_list(
        ["July End of Month Thanks-Giving", "Thanksgiving April", "Offering", "End of Month Thanks-Giving"]
    )
    assert names.count("End of Month Thanks-Giving") == 1
    assert "July End of Month Thanks-Giving" not in names


def test_same_date_gets_dash_suffix_and_never_overwrites(tmp_paths):
    analysis, output = tmp_paths
    plan = WeekPlan(
        week_end=date(2026, 4, 5),
        services=[
            Service(date(2026, 4, 3), ServiceType.SHILOH_HOUR),
            Service(date(2026, 4, 3), ServiceType.SHILOH_ENCOUNTER),
        ],
    )
    first = generate_week(plan, analysis, output)
    assert first.tabs == ["Fri-04.03.2026", "Fri-04.03.2026 -2"]
    wb = load_workbook(analysis)
    wb["Fri-04.03.2026"]["C2"] = "04/03/2026 - Shiloh Hour Of Visitation"
    wb["Fri-04.03.2026"]["G35"] = 111
    wb.save(analysis)
    wb.close()

    second = generate_week(plan, analysis, output)
    assert second.tabs == ["Fri-04.03.2026", "Fri-04.03.2026 -2"]
    wb = load_workbook(analysis)
    assert [n for n in wb.sheetnames if n.startswith("Fri-04.03.2026")] == [
        "Fri-04.03.2026",
        "Fri-04.03.2026 -2",
    ]
    assert wb["Fri-04.03.2026"]["G35"].value == 111
    wb.close()


def test_report_pulls_analysis_amounts(tmp_paths):
    analysis, output = tmp_paths
    plan = _week_two_services()
    generate_week(plan, analysis, output, write_report=False)
    wb = load_workbook(analysis)
    sun = wb["Sun-09.27.2026"]
    sun["G35"] = 385
    sun["G36"] = 1843.68
    wed = wb["Wed-09.23.2026"]
    wed["G35"] = 28
    wb.save(analysis)
    wb.close()

    result = generate_week(plan, analysis, output, write_analysis=False)
    report = load_workbook(result.report_path)
    ws = report.active
    assert ws["B15"].value == 28
    assert ws["E15"].value == 385
    assert ws["E16"].value == 1843.68
    report.close()


def test_report_other_service_name_uses_details(tmp_paths):
    analysis, output = tmp_paths
    plan = WeekPlan(
        week_end=date(2026, 9, 27),
        services=[Service(date(2026, 9, 24), ServiceType.OTHER, details="Youth Night")],
    )
    result = generate_week(plan, analysis, output)
    ws = load_workbook(result.report_path).active
    assert ws["B4"].value == "Youth Night"
    assert ws["C4"].value == "Youth Night"
