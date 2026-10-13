from pathlib import Path
import streamlit as st
from views.ui_components import icon_svg

ROOT = Path(__file__).resolve().parents[1]
st.set_page_config(page_title="VoltaIQ Console", page_icon="assets/favicon.ico", layout="wide")

css_path = ROOT / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.sidebar.markdown(
    f'<div class="vq-brand"><div class="vq-brand-mark">{icon_svg("grid", 20)}</div>'
    '<div><div class="vq-brand-name">VOLTAIQ</div><div class="vq-brand-sub">MICROGRID ANALYTICS</div></div></div>',
    unsafe_allow_html=True,
)

pages = {
    "Financial & Tariff Terminal": ("Financial & Tariff Terminal", "views.tab_finance"),
    "Telemetry Queue & Topology": ("Telemetry Queue & Topology", "views.tab_dispatch"),
    "Matrix Stability Engine": ("Matrix Stability Engine", "views.tab_grid"),
    "Environmental Diagnostics & Correlation": ("Environmental Diagnostics & Correlation", "views.tab_analytics"),
    "Privacy Policy": ("Privacy Policy", "views.privacy_policy"),
    "Terms & Conditions": ("Terms & Conditions", "views.terms_conditions"),
}
nav_labels = [
    "▥  Financial & Tariff Terminal",
    "⌘  Telemetry Queue & Topology",
    "▦  Matrix Stability Engine",
    "◉  Environmental Diagnostics & Correlation",
    "§  Privacy Policy",
    "¶  Terms & Conditions",
]
selection = st.sidebar.radio("WORKSPACE", nav_labels, label_visibility="visible")
page_name = selection.split("  ", 1)[1]

st.markdown(
    '<div class="vq-kicker">SHRI RAMDEOBABA COLLEGE OF ENGINEERING AND MANAGEMENT</div>'
    '<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">'
    '<div style="font-size:12px;color:#475569">Institutional node: rknec.edu</div>'
    '<div class="vq-status"><span class="vq-dot"></span> LOCAL / SAMPLE-DATA MODE</div></div>',
    unsafe_allow_html=True,
)
st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
st.markdown('<div class="vq-note">VoltaIQ is an educational analytics interface. It processes entered or sample data and does not control physical grid equipment.</div>', unsafe_allow_html=True)

module_name = pages[page_name][1]
module = __import__(module_name, fromlist=["render"])
module.render()

st.markdown('<div class="vq-footer">VOLTAIQ CONSOLE &nbsp; / &nbsp; EDUCATIONAL ANALYTICS</div>', unsafe_allow_html=True)
