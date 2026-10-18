import pandas as pd
import streamlit as st

from engine.meter_analytics import summarize_meter_readings
from views.ui_components import page_heading


def _active_data():
    data = st.session_state.get("meter_readings")
    if data is None or data.empty:
        st.info("No meter data loaded yet. Go to **Data & Quality** to upload a CSV/Excel file or load the clearly labeled demo data.")
        return None
    return data.copy()


def render():
    page_heading(
        "chart",
        "STEP 2 / UNDERSTAND USAGE",
        "Energy Insights",
        "Compare daily kWh, identify high-use periods, and see how consumption differs by building.",
    )
    data = _active_data()
    if data is None:
        return

    sites = sorted(data["building"].dropna().astype(str).unique().tolist())
    site_options = ["All buildings"] + sites
    selected_site = st.selectbox("Building or site", site_options)
    min_date = data["timestamp"].min().date()
    max_date = data["timestamp"].max().date()
    date_range = st.date_input("Analysis date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range
    days = data["timestamp"].dt.date
    filtered = data[(days >= start_date) & (days <= end_date)].copy()
    if selected_site != "All buildings":
        filtered = filtered[filtered["building"] == selected_site]
    if filtered.empty:
        st.warning("No readings match this site and date range.")
        return

    summary = summarize_meter_readings(filtered)
    daily = filtered.assign(day=filtered["timestamp"].dt.date).groupby("day")["energy_kwh"].sum().sort_index()
    peak_day = daily.idxmax()
    m1, m2, m3 = st.columns(3)
    m1.metric("Energy in selected range", f"{summary['total_kwh']:,.1f} kWh")
    m2.metric("Average daily use", f"{daily.mean():,.1f} kWh/day")
    m3.metric("Highest-use day", f"{peak_day:%d %b}", f"{daily.max():,.1f} kWh")

    st.subheader("Daily consumption")
    st.line_chart(daily.rename("Energy (kWh)"), height=320)
    if selected_site == "All buildings" and filtered["building"].nunique() > 1:
        st.subheader("Consumption by building")
        by_building_day = filtered.assign(day=filtered["timestamp"].dt.date).pivot_table(
            index="day", columns="building", values="energy_kwh", aggfunc="sum", fill_value=0
        )
        st.line_chart(by_building_day, height=320)
        totals = filtered.groupby("building")["energy_kwh"].sum().sort_values(ascending=False)
        st.bar_chart(totals, height=260)

    st.subheader("Highest individual meter readings")
    top = filtered.nlargest(10, "energy_kwh")[['timestamp', 'building', 'meter_id', 'energy_kwh']].copy()
    top["timestamp"] = top["timestamp"].dt.strftime("%Y-%m-%d %H:%M UTC")
    st.dataframe(top, hide_index=True, use_container_width=True)
    st.caption("A high reading is a prompt to investigate, not by itself proof of a fault or waste.")
