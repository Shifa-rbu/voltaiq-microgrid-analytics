import streamlit as st
from views.ui_components import page_heading


def render():
    page_heading("shield", "GOVERNANCE", "Privacy Policy", "Data handling boundaries for this educational analytics application.")
    st.write("VoltaIQ is an academic microgrid analytics demonstration. Data entered or uploaded is processed by the running application to display requested calculations.")
    st.write("Do not upload confidential, personal, or operationally sensitive data. The hosting environment may process application requests and uploaded files; retention depends on the deployment configuration and should be reviewed by the project administrator.")
    st.write("The mail-alert exercise parser extracts sender addresses ending in @rknec.edu from the supplied sample log. It does not send messages or contact those addresses.")
    st.write("This interface does not connect to or control physical electrical equipment.")
