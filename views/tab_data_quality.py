from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from engine.meter_analytics import prepare_meter_readings
from views.ui_components import page_heading


def _read_table(uploaded, sheet_name: str | None = None) -> pd.DataFrame:
    contents = uploaded.getvalue()
    suffix = Path(uploaded.name).suffix.casefold()
    if suffix == ".csv":
        return pd.read_csv(BytesIO(contents))
    if suffix == ".xlsx":
        return pd.read_excel(BytesIO(contents), sheet_name=sheet_name or 0, engine="openpyxl")
    raise ValueError("Choose a CSV or Excel .xlsx file.")


def _default_column(columns, aliases, fallback=0):
    lookup = {str(column).strip().casefold().replace(" ", "_"): column for column in columns}
    for alias in aliases:
        if alias in lookup:
            return lookup[alias]
    return columns[min(fallback, len(columns) - 1)]


def _show_quality_report(report):
    cols = st.columns(3)
    cols[0].metric("Input rows", f"{report['input_rows']:,}")
    cols[1].metric("Usable readings", f"{report['valid_rows']:,}")
    cols[2].metric("Invalid timestamps", f"{report['invalid_timestamp_rows']:,}")
    checks = pd.DataFrame(
        {
            "Check": [
                "Missing / non-numeric energy",
                "Negative energy readings",
                "Missing building labels",
                "Missing meter labels",
                "Duplicate timestamp / building / meter rows",
            ],
            "Rows": [
                report["missing_or_invalid_energy_rows"],
                report["negative_energy_rows"],
                report["missing_building_labels"],
                report["missing_meter_labels"],
                report["duplicate_readings"],
            ],
        }
    )
    st.dataframe(checks, hide_index=True, use_container_width=True)


def render():
    page_heading(
        "chart",
        "STEP 1 / IMPORT AND VALIDATE",
        "Data & Quality",
        "Load meter records, map their fields, and see which readings are ready for analysis.",
    )
    st.markdown(
        '<div class="energy-schema"><strong>Expected concepts</strong> · date/time · building or site · '
        'energy reading in kWh · optional meter ID. Your column names can differ; map them below.</div>',
        unsafe_allow_html=True,
    )

    sample_path = Path(__file__).resolve().parents[1] / "data" / "sample_meter_readings.csv"
    if sample_path.exists():
        st.download_button(
            "Download sample CSV",
            data=sample_path.read_bytes(),
            file_name="sample_meter_readings.csv",
            mime="text/csv",
        )
        demo_col, note_col = st.columns([1, 2])
        if demo_col.button("Load synthetic demo readings", type="primary"):
            raw = pd.read_csv(sample_path)
            clean, report = prepare_meter_readings(raw, "timestamp", "building", "energy_kwh", "meter_id")
            st.session_state["meter_readings"] = clean
            st.session_state["meter_quality"] = report
            st.session_state["meter_source"] = "Synthetic demonstration data · sample_meter_readings.csv"
            st.success("Synthetic demonstration readings loaded. They are not real campus data.")
        note_col.caption("The bundled sample is synthetic and exists only to demonstrate the workflow.")

    uploaded = st.file_uploader("Upload meter readings", type=["csv", "xlsx"], key="meter_file_upload")
    if uploaded is not None:
        try:
            workbook = None
            sheet = None
            if Path(uploaded.name).suffix.casefold() == ".xlsx":
                workbook = pd.ExcelFile(BytesIO(uploaded.getvalue()), engine="openpyxl")
                if not workbook.sheet_names:
                    st.error("No worksheets found in this workbook.")
                    return
                sheet = st.selectbox("Worksheet containing meter readings", workbook.sheet_names, key="meter_sheet")
                raw_frame = _read_table(uploaded, sheet)
            else:
                raw_frame = _read_table(uploaded)
            if raw_frame.empty or len(raw_frame.columns) < 3:
                st.error("The selected sheet needs at least three columns and one data row.")
                return
            raw_frame.columns = [str(column).strip() or f"Column {index + 1}" for index, column in enumerate(raw_frame.columns)]
            columns = list(raw_frame.columns)
            timestamp_default = _default_column(columns, ["timestamp", "datetime", "date_time", "date", "time"], 0)
            building_default = _default_column(columns, ["building", "site", "location", "facility"], min(1, len(columns) - 1))
            energy_default = _default_column(columns, ["energy_kwh", "kwh", "consumption_kwh", "kwh_reading", "reading_kwh", "energy", "consumption", "usage", "reading"], len(columns) - 1)
            meter_choices = ["(not provided)"] + [str(column) for column in columns]
            mapped = st.columns(4)
            timestamp_column = mapped[0].selectbox("Date/time column", columns, index=columns.index(timestamp_default))
            building_column = mapped[1].selectbox("Building/site column", columns, index=columns.index(building_default))
            energy_column = mapped[2].selectbox("Energy (kWh) column", columns, index=columns.index(energy_default))
            meter_index = 0
            for candidate in ("meter_id", "meter", "meter_number"):
                for idx, name in enumerate(columns, start=1):
                    if str(name).strip().casefold().replace(" ", "_") == candidate:
                        meter_index = idx
                        break
                if meter_index != 1:
                    break
            meter_column_choice = mapped[3].selectbox("Meter ID (optional)", meter_choices, index=meter_index)
            st.caption("Preview before loading. Readings with invalid times, non-numeric kWh, or negative kWh are excluded from analysis and counted in the report.")
            st.dataframe(raw_frame.head(12), use_container_width=True)
            if st.button("Validate and load meter data", type="primary"):
                meter_column = None if meter_column_choice == "(not provided)" else meter_column_choice
                clean, report = prepare_meter_readings(raw_frame, timestamp_column, building_column, energy_column, meter_column)
                if clean.empty:
                    st.error("No valid meter readings were found. Check the selected columns and the data format.")
                else:
                    st.session_state["meter_readings"] = clean
                    st.session_state["meter_quality"] = report
                    st.session_state["meter_source"] = f"Uploaded data · {uploaded.name}" + (f" · {sheet}" if sheet else "")
                    st.success(f"Loaded {len(clean):,} valid meter readings for the energy workflow.")
        except Exception as exc:
            st.error(f"Could not read or validate this file: {exc}")

    current = st.session_state.get("meter_readings")
    report = st.session_state.get("meter_quality")
    if current is not None and report is not None:
        st.subheader("Quality report for the active dataset")
        _show_quality_report(report)
        st.caption("Unusable rows are excluded from insights and cost estimates. Duplicate rows are reported but retained; confirm with the source before removing them.")
        with st.expander("Canonical records used in analysis"):
            st.dataframe(current.head(100), use_container_width=True)
