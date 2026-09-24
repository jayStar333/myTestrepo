from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum


class ServiceType(str, Enum):
    WOSE_DAY_1 = "wose_day_1"
    WOSE_DAY_2 = "wose_day_2"
    WOSE_DAY_3 = "wose_day_3"
    MIDWEEK = "midweek"
    SUNDAY = "sunday"
    CDOT = "cdot"
    SHILOH_OPENING = "shiloh_opening"
    SHILOH_HOUR = "shiloh_hour"
    SHILOH_ENCOUNTER = "shiloh_encounter"
    SHILOH_IMPARTATION = "shiloh_impartation"
    OTHER = "other"


SERVICE_DROPDOWN: dict[ServiceType, str] = {
    ServiceType.WOSE_DAY_1: "Week Of Spiritual Emphasis Day 1",
    ServiceType.WOSE_DAY_2: "Week Of Spiritual Emphasis Day 2",
    ServiceType.WOSE_DAY_3: "Week Of Spiritual Emphasis Day 3",
    ServiceType.MIDWEEK: "Midweek Service",
    ServiceType.SUNDAY: "Sunday Service",
    ServiceType.CDOT: "Covenant Day Of Trumpet",
    ServiceType.SHILOH_OPENING: "Shiloh Opening Night",
    ServiceType.SHILOH_HOUR: "Shiloh Hour Of Visitation",
    ServiceType.SHILOH_ENCOUNTER: "Shiloh Encounter Night",
    ServiceType.SHILOH_IMPARTATION: "Shiloh Impartation Night",
    ServiceType.OTHER: "Other service (enter details)",
}

SERVICE_SHORT_LABEL: dict[ServiceType, str] = {
    ServiceType.WOSE_DAY_1: "WOSE Day 1",
    ServiceType.WOSE_DAY_2: "WOSE Day 2",
    ServiceType.WOSE_DAY_3: "WOSE Day 3",
    ServiceType.MIDWEEK: "Midweek Service",
    ServiceType.SUNDAY: "Sunday Service",
    ServiceType.CDOT: "CDOT",
    ServiceType.SHILOH_OPENING: "Shiloh Opening Night",
    ServiceType.SHILOH_HOUR: "Shiloh Hour Of Visitation",
    ServiceType.SHILOH_ENCOUNTER: "Shiloh Encounter Night",
    ServiceType.SHILOH_IMPARTATION: "Shiloh Impartation Night",
    ServiceType.OTHER: "Other",
}

DOW_ABBREV = ["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"]

DEFAULT_CATEGORIES = [
    "Offering",
    "Tithe",
    "Kingdom care Seed",
    "Sacrifice Seed",
    "SHILOH SACRIFICE",
    "End of Month Thanks-Giving",
    "Evangelism",
    "Building",
    "Welfare",
    "Chairs",
    "Bookstore",
    "Children's Dept",
    "Prophetic Offering",
    "Transportation",
    "Misc:",
]

ANALYSIS_ORG = "WINNERS CHAPEL CARLOTTE"
REPORT_ORG = "Winners Chapel International, Charlotte"
DEFAULT_PREPARED_BY = "Deacon Patrick Godia"
CURRENCY_FORMAT = '_("$"* #,##0.00_);_("$"* \\(#,##0.00\\);_("$"* "-"??_);_(@_)'
CATEGORIES_SHEET = "_Categories"

# Rows that are labels, not collection categories, when inferring from analysis col B.
ANALYSIS_NON_CATEGORY = {
    "total collections",
    "collection analysis",
    "total collections analysis",
    "minister:",
    "minister",
    "prepared by :",
    "prepared by:",
    "approved by:",
    "comments:",
    "balancing control",
}

ATTENDANCE_ROWS = [
    (7, "Men"),
    (8, "Women"),
    (9, "Children"),
    (10, "First Timer"),
    (11, "New Convert"),
]


def service_type_from_value(value: str) -> ServiceType:
    key = (value or "").strip()
    for item in ServiceType:
        if item.value == key or SERVICE_DROPDOWN[item] == key or SERVICE_SHORT_LABEL[item] == key:
            return item
    return ServiceType.OTHER


@dataclass
class Service:
    service_date: date
    service_type: ServiceType
    details: str = ""
    recorded_by: str = ""
    session_suffix: str = ""  # e.g. AM / PM when two services share a date

    def display_label(self) -> str:
        if self.service_type == ServiceType.OTHER:
            text = (self.details or "").strip()
            if not text:
                raise ValueError("Other service requires details.")
            return text
        return SERVICE_SHORT_LABEL[self.service_type]

    def analysis_c2(self) -> str:
        return f"{self.service_date.strftime('%m/%d/%Y')} - {self.display_label()}"

    def analysis_tab_name(self) -> str:
        dow = DOW_ABBREV[self.service_date.weekday()]
        stamp = self.service_date.strftime("%m.%d.%Y")
        name = f"{dow}-{stamp}"
        suffix = (self.session_suffix or "").strip()
        if suffix:
            name = f"{name} - {suffix}"
        return name[:31]

    def report_date_label(self) -> str:
        return f"Date:{self.service_date.strftime('%m.%d.%Y')}"


@dataclass
class WeekPlan:
    week_end: date
    services: list[Service] = field(default_factory=list)
    week_start: date | None = None
    recorded_by_default: str = ""

    def start(self) -> date:
        if self.week_start:
            return self.week_start
        if self.services:
            return min(s.service_date for s in self.services)
        return self.week_end - timedelta(days=6)

    def title_range(self) -> str:
        start = self.start()
        end = self.week_end
        return f"{start.strftime('%m/%d')} - {end.strftime('%m/%d/%Y')}"

    def report_title(self) -> str:
        return f"{REPORT_ORG}  Collection Report as at   {self.title_range()}"

    def report_sheet_name(self) -> str:
        return self.week_end.strftime("%m.%d.%y")

    def report_filename(self) -> str:
        return f"Collection Report {self.week_end.strftime('%m.%d.%Y')}.xlsx"

    def validate(self) -> None:
        if not self.services:
            raise ValueError("Add at least one service.")
        for service in self.services:
            if service.service_type == ServiceType.OTHER and not (service.details or "").strip():
                raise ValueError("Other service (enter details) needs the details filled in.")
