import streamlit as st

from views.ui_components import page_heading


def render():
    page_heading(
        "matrix",
        "ACADEMIC METHODS / SEPARATE FROM ENERGY WORKFLOW",
        "Practical Lab",
        "Access the original programming exercises here; they are tools and demonstrations, not live campus operations.",
    )
    st.markdown(
        '<div class="energy-lab-note">These exercises are retained for coursework and assessment. '
        'Only the meter-data workflow on Overview, Data &amp; Quality, Energy Insights, and Cost Estimate is presented as the product path.</div>',
        unsafe_allow_html=True,
    )
    chosen = st.selectbox(
        "Choose a practical area",
        ["Billing, depreciation & series", "Queue, sets & topology", "Matrix and grid-math exercises", "General CSV/Excel workbench"],
    )
    st.divider()
    if chosen == "Billing, depreciation & series":
        from views.tab_finance import render
    elif chosen == "Queue, sets & topology":
        from views.tab_dispatch import render
    elif chosen == "Matrix and grid-math exercises":
        from views.tab_grid import render
    else:
        from views.tab_analytics import render
    render()
