from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path

from .generate import discover_categories, generate_week, sync_categories_across
from .models import SERVICE_DROPDOWN, Service, ServiceType, WeekPlan, service_type_from_value
from .paths import DEFAULT_ANALYSIS_NAME, ROOT_DIR


def _parse_date(text: str) -> date:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m.%d.%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"Unrecognized date: {text}")


def _parse_service(text: str) -> Service:
    # date:type[:details]
    parts = text.split(":", 2)
    if len(parts) < 2:
        raise argparse.ArgumentTypeError(
            "Service must be DATE:TYPE or DATE:TYPE:details "
            "(type is a dropdown code, e.g. sunday, midweek, wose_day_1, other)."
        )
    service_date = _parse_date(parts[0])
    service_type = service_type_from_value(parts[1])
    details = parts[2] if len(parts) > 2 else ""
    if service_type == ServiceType.OTHER and not details:
        raise argparse.ArgumentTypeError("Other service needs details after a second colon.")
    return Service(service_date=service_date, service_type=service_type, details=details)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wciclt",
        description="Create Collection Analysis tabs and weekly Collection Reports.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Create analysis tabs and/or a weekly report")
    gen.add_argument("--week-end", type=_parse_date, required=True, help="Week-ending date (usually Sunday)")
    gen.add_argument("--week-start", type=_parse_date, help="Optional week-start for the report title")
    gen.add_argument(
        "--service",
        action="append",
        required=True,
        type=_parse_service,
        help="Repeatable DATE:TYPE or DATE:other:details",
    )
    gen.add_argument("--analysis", type=Path, default=ROOT_DIR / "output" / DEFAULT_ANALYSIS_NAME)
    gen.add_argument("--output-dir", type=Path, default=ROOT_DIR / "output")
    gen.add_argument("--recorded-by", default="", help="Default Recorded By for report blocks")
    gen.add_argument("--report-only", action="store_true")
    gen.add_argument("--analysis-only", action="store_true")
    gen.add_argument("--sync-existing-tabs", action="store_true")

    sub.add_parser("service-types", help="List service dropdown codes")

    sync = sub.add_parser("sync-categories", help="Read/write the shared category list")
    sync.add_argument("--analysis", type=Path, default=ROOT_DIR / "output" / DEFAULT_ANALYSIS_NAME)
    sync.add_argument("--report", type=Path, help="Optional weekly report to read category names from")
    sync.add_argument("--add", action="append", default=[], help="Category name to add")
    sync.add_argument("--remove", action="append", default=[], help="Category name to remove")

    sub.add_parser("gui", help="Launch the Streamlit week builder")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "service-types":
        for code, label in SERVICE_DROPDOWN.items():
            print(f"{code.value:22} {label}")
        return 0

    if args.command == "gui":
        from .gui import launch

        return launch()

    if args.command == "sync-categories":
        cats = discover_categories(args.analysis, args.report)
        for name in args.add:
            if name not in cats:
                cats.append(name)
        remove = {n.casefold() for n in args.remove}
        cats = [c for c in cats if c.casefold() not in remove]
        sync_categories_across(args.analysis, cats, args.report)
        print("Categories:")
        for name in cats:
            print(f"  - {name}")
        print(f"Wrote {args.analysis}")
        return 0

    services: list[Service] = []
    for service in args.service:
        if args.recorded_by and not service.recorded_by:
            service.recorded_by = args.recorded_by
        services.append(service)
    plan = WeekPlan(week_end=args.week_end, services=services, week_start=args.week_start)
    result = generate_week(
        plan,
        analysis_path=args.analysis,
        output_dir=args.output_dir,
        write_report=not args.analysis_only,
        write_analysis=not args.report_only,
        sync_existing_tabs=args.sync_existing_tabs,
    )
    print(f"Categories ({len(result.categories)}): {', '.join(result.categories)}")
    if result.tabs:
        print("Analysis tabs:")
        for tab in result.tabs:
            print(f"  - {tab}")
        print(f"Analysis workbook: {result.analysis_path}")
    if result.report_path:
        print(f"Weekly report: {result.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
