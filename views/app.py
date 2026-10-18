from pathlib import Path

import streamlit as st

from views.ui_components import icon_svg

ROOT = Path(__file__).resolve().parents[1]
st.set_page_config(page_title="VoltaIQ | Campus Energy", page_icon="assets/favicon.ico", layout="wide")

css_path = ROOT / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.sidebar.markdown(
    f'<div class="vq-brand"><div class="vq-brand-mark">{icon_svg("grid", 20)}</div>'
    '<div><div class="vq-brand-name">VOLTAIQ</div><div class="vq-brand-sub">CAMPUS ENERGY WORKBENCH</div></div></div>',
    unsafe_allow_html=True,
)

pages = {
    "Overview": "views.tab_overview",
    "Data & Quality": "views.tab_data_quality",
    "Energy Insights": "views.tab_energy_insights",
    "Cost Estimate": "views.tab_cost_estimate",
    "Sources": "views.tab_scraper",
    "Practical Lab": "views.tab_practical_lab",
    "Privacy Policy": "views.privacy_policy",
    "Terms & Conditions": "views.terms_conditions",
}
nav_labels = [
    "⌂  Overview",
    "▤  Data & Quality",
    "◉  Energy Insights",
    "₹  Cost Estimate",
    "↗  Sources",
    "⚙  Practical Lab",
    "§  Privacy Policy",
    "¶  Terms & Conditions",
]
selection = st.sidebar.radio("WORKSPACE", nav_labels, key="workspace_nav", label_visibility="visible")
page_name = selection.split("  ", 1)[1]

st.markdown(
    '<div class="vq-kicker">CAMPUS FACILITIES / ENERGY DECISION SUPPORT</div>'
    '<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">'
    '<div style="font-size:12px;color:#4B5D73">VoltaIQ · Meter-data analysis prototype</div>'
    '<div class="vq-status"><span class="vq-dot"></span> UPLOAD / DEMO DATA · NOT LIVE GRID DATA</div></div>',
    unsafe_allow_html=True,
)
st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="vq-note">Use meter readings to understand energy patterns and estimate costs. '
    'This educational prototype does not connect to or control physical grid equipment.</div>',
    unsafe_allow_html=True,
)

module = __import__(pages[page_name], fromlist=["render"])
module.render()

st.markdown('<div class="vq-footer">VOLTAIQ &nbsp; / &nbsp; CAMPUS ENERGY WORKBENCH &nbsp; / &nbsp; EDUCATIONAL PROTOTYPE</div>', unsafe_allow_html=True)
