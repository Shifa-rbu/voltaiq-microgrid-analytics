import pandas as pd
import streamlit as st

from engine.billing_depr import calculate_electricity_bill
from views.ui_components import page_heading


def render():
    page_heading(
        "bolt",
        "STEP 3 / ESTIMATE COST",
        "Cost Estimate",
        "Apply the project's example tariff to a selected building and meter-reading period.",
    )
    data = st.session_state.get("meter_readings")
    if data is None or data.empty:
        st.info("No meter data loaded yet. Go to **Data & Quality** to upload readings or load the clearly labeled demo data.")
        return

    buildings = sorted(data["building"].dropna().astype(str).unique().tolist())
    selected_building = st.selectbox("Building or site", buildings)
    start_min, end_max = data["timestamp"].min().date(), data["timestamp"].max().date()
    date_range = st.date_input("Period to estimate", value=(start_min, end_max), min_value=start_min, max_value=end_max)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range
    connection = st.selectbox("Example connection tariff", ["Domestic", "Commercial"])

    reading_days = data["timestamp"].dt.date
    selected = data[(data["building"] == selected_building) & (reading_days >= start_date) & (reading_days <= end_date)]
    if selected.empty:
        st.warning("No valid readings match this building and date range.")
        return

    energy_units = float(selected["energy_kwh"].sum())
    bill = calculate_electricity_bill(energy_units, connection)
    st.markdown(
        f'<div class="energy-bill"><div><span>ESTIMATED COST · {selected_building}</span>'
        f'<small>{start_date:%d %b %Y} – {end_date:%d %b %Y} · {len(selected):,} valid readings</small></div>'
        f'<strong>₹{bill["total"]:,.2f}</strong></div>',
        unsafe_allow_html=True,
    )
    st.metric("Energy in selected period", f"{energy_units:,.2f} kWh")
    rows = [
        ("Progressive energy charge", bill["energy_charge"]),
        ("Fixed connection charge", bill["fixed_charge"]),
        ("Subtotal", bill["subtotal"]),
        (f"Discount ({bill['discount_rate']:.0%})", -bill["discount"]),
        ("Taxable amount", bill["taxable_amount"]),
        (f"GST ({bill['gst_rate']:.0%})", bill["gst"]),
        ("Estimated total", bill["total"]),
    ]
    breakdown = pd.DataFrame(rows, columns=["Charge component", "Amount (₹)"])
    breakdown["Amount (₹)"] = breakdown["Amount (₹)"].map(lambda value: f"−₹{abs(value):,.2f}" if value < 0 else f"₹{value:,.2f}")
    st.dataframe(breakdown, hide_index=True, use_container_width=True)

    with st.expander("Tariff assumptions and limitations"):
        st.markdown(
            "- Energy charge: ₹4 per kWh for the first 100 units, ₹6 for the next 100, and ₹8 thereafter.\n"
            "- Fixed charge: ₹100 for Domestic or ₹250 for Commercial.\n"
            "- The example backend applies its configured discount thresholds and 12% GST.\n"
            "- The selected date range is treated as **one billing period and one connection**. This estimate does not model time-of-use rates, demand charges, meter-specific fees, or a utility's official billing rules.\n"
            "- Replace the example tariff with a verified applicable tariff before using this for any real decision."
        )
    st.warning("This is an estimate based on the prototype tariff—not an official bill or a utility quote.")
