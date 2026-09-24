from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import streamlit as st

from wciclt.generate import discover_categories, generate_week, sync_categories_across
from wciclt.gui import default_paths, default_week_end
from wciclt.models import SERVICE_DROPDOWN, Service, ServiceType, WeekPlan

st.set_page_config(page_title="WCICLT Collection Utility", layout="wide")
st.title("WCICLT Collection & Report")
st.caption("Create Analysis tabs and a weekly Collection Report. Categories stay in sync.")

default_analysis, default_output = default_paths()

with st.sidebar:
    st.header("Files")
    analysis_path = Path(st.text_input("Analysis workbook", value=str(default_analysis)))
    output_dir = Path(st.text_input("Report output folder", value=str(default_output)))
    sync_existing = st.checkbox("Also rewrite categories on existing analysis tabs", value=False)

if "categories" not in st.session_state:
    st.session_state.categories = discover_categories(analysis_path if analysis_path.exists() else None)

if "services" not in st.session_state:
    week_end0 = default_week_end()
    st.session_state.services = [
        {
            "service_date": week_end0 - timedelta(days=4),
            "service_type": ServiceType.MIDWEEK,
            "details": "",
            "recorded_by": "",
            "session_suffix": "",
        },
        {
            "service_date": week_end0,
            "service_type": ServiceType.SUNDAY,
            "details": "",
            "recorded_by": "",
            "session_suffix": "",
        },
    ]

col_week, col_cats = st.columns([1.4, 1])

with col_week:
    st.subheader("Week")
    week_end = st.date_input("Week ending (usually Sunday)", value=default_week_end())
    use_custom_start = st.checkbox("Set week start for the report title", value=False)
    week_start = None
    if use_custom_start:
        week_start = st.date_input("Week start", value=week_end - timedelta(days=6))

    st.subheader("Services")
    dropdown_labels = list(SERVICE_DROPDOWN.values())
    label_to_type = {v: k for k, v in SERVICE_DROPDOWN.items()}

    remove_at = None
    for i, row in enumerate(st.session_state.services):
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 1.4, 0.4])
            row["service_date"] = c1.date_input("Date", value=row["service_date"], key=f"d{i}")
            current_label = SERVICE_DROPDOWN.get(row["service_type"], SERVICE_DROPDOWN[ServiceType.OTHER])
            chosen = c2.selectbox("Service type", dropdown_labels, index=dropdown_labels.index(current_label), key=f"t{i}")
            row["service_type"] = label_to_type[chosen]
            if c3.button("Remove", key=f"rm{i}"):
                remove_at = i
            if row["service_type"] == ServiceType.OTHER:
                row["details"] = st.text_input("Other service details", value=row.get("details") or "", key=f"det{i}")
            else:
                row["details"] = ""
            row["recorded_by"] = st.text_input("Recorded By", value=row.get("recorded_by") or "", key=f"rb{i}")
            row["session_suffix"] = st.text_input(
                "Tab suffix (optional AM/PM)",
                value=row.get("session_suffix") or "",
                key=f"sx{i}",
                help="Used when two services share a date, matching tabs like Fri-04.03.2026 - PM",
            )

    if remove_at is not None:
        st.session_state.services.pop(remove_at)
        st.rerun()

    if st.button("Add service"):
        last = st.session_state.services[-1]["service_date"] if st.session_state.services else week_end
        st.session_state.services.append(
            {
                "service_date": last + timedelta(days=1),
                "service_type": ServiceType.SUNDAY,
                "details": "",
                "recorded_by": "",
                "session_suffix": "",
            }
        )
        st.rerun()

with col_cats:
    st.subheader("Categories")
    st.caption("Shared by the Analysis workbook and the weekly report. Add or remove here, then Sync or Generate.")
    edited = st.data_editor(
        [{"category": name} for name in st.session_state.categories],
        num_rows="dynamic",
        use_container_width=True,
        key="cat_editor",
        hide_index=True,
    )
    st.session_state.categories = [r["category"] for r in edited if str(r.get("category") or "").strip()]

    if st.button("Reload categories from analysis workbook"):
        st.session_state.categories = discover_categories(analysis_path if analysis_path.exists() else None)
        st.rerun()

st.divider()
b1, b2, b3, b4 = st.columns(4)
do_all = b1.button("Generate week", type="primary")
do_analysis = b2.button("Analysis tabs only")
do_report = b3.button("Report only")
do_sync = b4.button("Sync categories")

def _plan() -> WeekPlan:
    services = []
    for row in st.session_state.services:
        services.append(
            Service(
                service_date=row["service_date"],
                service_type=row["service_type"],
                details=row.get("details") or "",
                recorded_by=row.get("recorded_by") or "",
                session_suffix=row.get("session_suffix") or "",
            )
        )
    return WeekPlan(week_end=week_end, week_start=week_start, services=services)

if do_sync:
    cats = sync_categories_across(analysis_path, st.session_state.categories)
    st.success(f"Synced {len(cats)} categories to {analysis_path}")

if do_all or do_analysis or do_report:
    try:
        result = generate_week(
            _plan(),
            analysis_path=analysis_path,
            output_dir=output_dir,
            categories=st.session_state.categories,
            write_report=do_all or do_report,
            write_analysis=do_all or do_analysis,
            sync_existing_tabs=sync_existing,
        )
        if result.tabs:
            st.success("Analysis tabs: " + ", ".join(result.tabs))
            st.write(result.analysis_path)
        if result.report_path:
            st.success(f"Weekly report: {result.report_path}")
    except Exception as exc:
        st.error(str(exc))
