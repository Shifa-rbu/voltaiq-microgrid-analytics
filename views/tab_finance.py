from pathlib import Path
import streamlit as st
from engine.billing_depr import (
    calculate_electricity_bill,
    calculate_depreciation,
    alternating_series,
    reciprocal_product_loss,
    parse_mail_alerts,
)
from views.ui_components import page_heading


def render():
    page_heading("bolt", "FINANCE / PRACTICALS 1 & 4", "Financial & Tariff Terminal", "Tariff calculations, asset valuation, series, and institutional alert parsing.")
    bill_tab, asset_tab, series_tab, alerts_tab = st.tabs(["Electricity bill", "Asset depreciation", "Series", "Mail alerts"])

    with bill_tab:
        left, right = st.columns(2)
        units = left.number_input("Energy consumed (units)", min_value=0.0, value=100.0, step=1.0)
        connection = right.selectbox("Connection type", ["Domestic", "Commercial"])
        if st.button("Calculate bill", type="primary"):
            bill = calculate_electricity_bill(units, connection)
            st.dataframe({"Invoice item": ["Energy charge", "Fixed charge", "Subtotal", "Discount", "GST", "Total payable"], "Amount (₹)": [bill["energy_charge"], bill["fixed_charge"], bill["subtotal"], bill["discount"], bill["gst"], bill["total"]]}, hide_index=True, use_container_width=True)
            st.metric("Total payable", f"₹{bill['total']:,.2f}")
        st.caption("Uses the tariff and discount rules implemented in the engine.")

    with asset_tab:
        c1, c2 = st.columns(2)
        price = c1.number_input("Original equipment cost (₹)", min_value=0.0, value=100000.0, step=1000.0)
        years = c2.number_input("Age (years)", min_value=0.0, value=1.0, step=1.0)
        value = calculate_depreciation(price, years)
        st.metric("Estimated remaining book value", f"₹{value:,.2f}")
        st.caption("Declining-balance rates: year 1 at 20%, years 2-5 at 10% per year, then 5% per year.")

    with series_tab:
        n = st.slider("Series terms (n)", min_value=1, max_value=50, value=10)
        st.metric("Alternating series", alternating_series(n))
        st.metric("Reciprocal-product sum", f"{reciprocal_product_loss(n):.6f}")
        st.caption("Only series implemented in the backend are displayed here.")

    with alerts_tab:
        alert_path = Path(__file__).resolve().parents[1] / "data" / "server_alerts.txt"
        if alert_path.exists():
            st.code(alert_path.read_text(encoding="utf-8"), language="text")
            if st.button("Parse mail alerts"):
                senders, count = parse_mail_alerts(alert_path)
                st.metric("Valid @rknec.edu senders", count)
                st.write(senders)
        else:
            st.warning("data/server_alerts.txt was not found in the project.")
