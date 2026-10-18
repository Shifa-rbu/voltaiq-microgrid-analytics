import pandas as pd
import streamlit as st

from engine.web_scraping import scrape_public_tables
from views.ui_components import page_heading


@st.cache_data(ttl=600, show_spinner=False)
def _scrape_cached(url: str):
    return scrape_public_tables(url)


def render():
    page_heading(
        "network",
        "SOURCES / PUBLIC WEB DATA",
        "Public Source Explorer",
        "Inspect a permitted public HTML table as contextual reference data; it is not automatically mixed into meter totals.",
    )
    st.markdown(
        '<div class="vq-scrape-guidance">Use only public pages you are allowed to access. Respect the source site’s terms, robots.txt, and request limits. '
        'This demo fetches HTML tables; it does not bypass logins, paywalls, or access controls.</div>',
        unsafe_allow_html=True,
    )
    with st.form("scrape_public_table_form"):
        url = st.text_input(
            "Public webpage URL",
            value="https://en.wikipedia.org/wiki/List_of_countries_by_electricity_consumption",
            help="Standard HTTP/HTTPS webpages only. Private or local network addresses are blocked.",
        )
        submitted = st.form_submit_button("Fetch and analyze tables", type="primary")

    if submitted:
        if not url.strip():
            st.error("Enter a public webpage URL first.")
        else:
            try:
                with st.spinner("Fetching the permitted public page and extracting tables…"):
                    tables, final_url, fetched_at = _scrape_cached(url.strip())
                st.session_state["scraped_table_result"] = {
                    "tables": tables,
                    "source_url": final_url,
                    "fetched_at": fetched_at,
                    "requested_url": url.strip(),
                }
            except Exception as exc:
                st.error(str(exc))
                st.session_state.pop("scraped_table_result", None)

    result = st.session_state.get("scraped_table_result")
    if not result:
        st.info("Enter a permitted public webpage containing a data table, then select Fetch and analyze tables.")
        return

    st.caption(f"Source: {result['source_url']}  ·  Fetched (UTC): {result['fetched_at']}  ·  Tables found: {len(result['tables'])}")
    if len(result["tables"]) > 1:
        index = st.selectbox("Choose a table", list(range(len(result["tables"]))), format_func=lambda value: f"Table {value + 1}")
    else:
        index = 0
    frame = result["tables"][index].copy()

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Rows extracted", f"{len(frame):,}")
    metric2.metric("Columns extracted", f"{len(frame.columns):,}")
    missing = int(frame.isna().sum().sum())
    metric3.metric("Blank cells", f"{missing:,}")

    data_tab, analysis_tab = st.tabs(["Scraped table", "Quick analysis"])
    with data_tab:
        st.dataframe(frame.head(200), use_container_width=True, height=380)
        st.download_button(
            "Download scraped table as CSV",
            data=frame.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"scraped_table_{index + 1}.csv",
            mime="text/csv",
        )
    with analysis_tab:
        numeric = frame.select_dtypes(include="number").columns.tolist()
        categorical = frame.select_dtypes(exclude="number").columns.tolist()
        if numeric:
            selected = st.selectbox("Numeric column to summarize", numeric)
            values = pd.to_numeric(frame[selected], errors="coerce").dropna()
            if not values.empty:
                c1, c2, c3 = st.columns(3)
                c1.metric("Mean", f"{values.mean():,.3f}")
                c2.metric("Minimum", f"{values.min():,.3f}")
                c3.metric("Maximum", f"{values.max():,.3f}")
                st.bar_chart(values.reset_index(drop=True), height=280)
        if categorical:
            category = st.selectbox("Category frequency", categorical)
            counts = frame[category].fillna("(blank)").astype(str).value_counts().head(15)
            st.bar_chart(counts, height=260)
        if not numeric and not categorical:
            st.info("The extracted table has no analyzable columns.")
