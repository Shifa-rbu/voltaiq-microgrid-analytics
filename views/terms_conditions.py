import streamlit as st
from views.ui_components import page_heading


def render():
    page_heading("document", "GOVERNANCE", "Terms & Conditions", "Educational scope, limitations, and responsible use.")
    st.write("This project is provided for educational demonstration and academic evaluation. Results depend on the supplied inputs, sample data, and implementation assumptions.")
    st.write("Calculations are illustrative and are not engineering, billing, safety, financial, or operational advice. Do not use the output to operate a real grid, set customer tariffs, or make safety-critical decisions.")
    st.write("The project team should document the applicable source-code license and follow the institution's academic integrity and evaluation requirements. No commercial or operational warranty is provided.")
