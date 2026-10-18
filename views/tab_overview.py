from pathlib import Path

import streamlit as st

from views.ui_components import page_heading


def render():
    page_heading(
        "bolt",
        "CAMPUS ENERGY WORKBENCH",
        "Understand where campus energy goes",
        "Explore meter readings, identify high-use periods, and estimate costs from stated tariff assumptions.",
    )
    data = st.session_state.get("meter_readings")
    source = st.session_state.get("meter_source")

    if data is None or data.empty:
        st.markdown(
            '<div class="energy-welcome"><div class="energy-welcome-kicker">START WITH METER READINGS</div>'
            '<h3>Bring your own energy data</h3>'
            '<p>Load a CSV or Excel workbook in <strong>Data &amp; Quality</strong>. Map its date/time, building, and kWh columns; '
            'then review usage patterns and an estimated bill.</p></div>',
            unsafe_allow_html=True,
        )
        st.subheader("What the workflow answers")
        cols = st.columns(3)
        cards = [
            ("01", "Is the data usable?", "Check missing timestamps, invalid readings, and meter labels before analysis."),
            ("02", "Where and when is use highest?", "Compare daily kWh across buildings or meters and identify peak readings."),
            ("03", "What might it cost?", "Apply a stated sample tariff to the selected building and date range."),
        ]
        for col, (number, title, detail) in zip(cols, cards):
            col.markdown(
                f'<div class="energy-step"><span>{number}</span><strong>{title}</strong><p>{detail}</p></div>',
                unsafe_allow_html=True,
            )
        st.info("Use the optional demonstration dataset only to preview the workflow. It is synthetic—not campus meter data.")
        return

    total_kwh = float(data["energy_kwh"].sum())
    buildings = int(data["building"].nunique())
    readings = len(data)
    min_day = data["timestamp"].min().strftime("%d %b %Y")
    max_day = data["timestamp"].max().strftime("%d %b %Y")
    st.caption(f"Active dataset: {source or 'uploaded meter data'} · {min_day} — {max_day}")
    m1, m2, m3 = st.columns(3)
    m1.metric("Valid readings", f"{readings:,}")
    m2.metric("Buildings", f"{buildings:,}")
    m3.metric("Energy in selected file", f"{total_kwh:,.1f} kWh")

    st.subheader("Your analysis workflow")
    cols = st.columns(3)
    cards = [
        ("Data & Quality", "Review which rows were usable and how the fields were mapped."),
        ("Energy Insights", "Compare daily consumption and identify the highest-use days."),
        ("Cost Estimate", "Estimate cost for one building and date range using the project's example tariff."),
    ]
    for col, (title, detail) in zip(cols, cards):
        col.markdown(
            f'<div class="energy-step"><strong>{title}</strong><p>{detail}</p></div>',
            unsafe_allow_html=True,
        )

    if source and "synthetic" in source.casefold():
        st.warning("This is synthetic demonstration data. Do not present it as actual campus consumption.")
