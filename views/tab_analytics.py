from pathlib import Path
from io import BytesIO
import pandas as pd
import streamlit as st
from engine.telemetry_pd import (
    load_and_clean_telemetry,
    impute_missing_telemetry,
    engineer_features,
    manual_pearson_r,
    scipy_pearson_r,
    verify_correlation_parity,
)
from views.ui_components import page_heading


def render():
    page_heading("chart", "TELEMETRY / PRACTICAL 6", "Environmental Diagnostics & Correlation", "Clean the Iris telemetry sample, engineer features, and compare Pearson correlation methods.")
    default_path = Path(__file__).resolve().parents[1] / "data" / "Iris_data_sample.csv"
    uploaded = st.file_uploader("Load telemetry CSV", type=["csv"])
    if uploaded is not None:
        csv_bytes = uploaded.getvalue()
        raw = pd.read_csv(BytesIO(csv_bytes)).replace({"??": pd.NA, "##": pd.NA})
        cleaned, missing = load_and_clean_telemetry(BytesIO(csv_bytes))
    elif default_path.exists():
        raw = pd.read_csv(default_path).replace({"??": pd.NA, "##": pd.NA})
        cleaned, missing = load_and_clean_telemetry(default_path)
    else:
        st.warning("Upload a telemetry CSV or add data/Iris_data_sample.csv.")
        return

    st.subheader("Missing values before imputation")
    st.dataframe(missing.rename("Missing count").to_frame(), use_container_width=True)
    st.subheader("Raw and cleaned data")
    left, right = st.columns(2)
    left.caption("Raw input")
    left.dataframe(raw.head(20), use_container_width=True)
    right.caption("Loaded/cleaned (Id removed if present)")
    right.dataframe(cleaned.head(20), use_container_width=True)

    try:
        filled = impute_missing_telemetry(cleaned)
        featured, highest_species, top_five = engineer_features(filled)
    except (KeyError, ValueError) as exc:
        st.error(f"The CSV needs compatible Iris columns: {exc}")
        return
    st.subheader("Imputation and derived feature")
    st.write("Highest mean Petal_Area species:", highest_species)
    st.dataframe(top_five, use_container_width=True)
    st.write("Missing values after imputation:")
    st.dataframe(featured.isna().sum().rename("Missing count").to_frame(), use_container_width=True)

    numeric = list(featured.select_dtypes(include="number").columns)
    if len(numeric) < 2:
        st.info("At least two numeric columns are needed for correlation analysis.")
        return
    st.subheader("Pearson correlation")
    corr = featured[numeric].corr(numeric_only=True)
    st.dataframe(corr, use_container_width=True)
    c1, c2 = st.columns(2)
    col1 = c1.selectbox("First numeric column", numeric, index=0)
    col2 = c2.selectbox("Second numeric column", numeric, index=min(1, len(numeric)-1))
    if st.button("Run correlation analysis"):
        pair = featured[[col1, col2]].dropna()
        manual = manual_pearson_r(pair[col1], pair[col2])
        scipy = scipy_pearson_r(pair[col1], pair[col2])
        st.write({"Manual Pearson r": manual, "SciPy Pearson r": scipy, "Parity": verify_correlation_parity(pair, col1, col2)})
        st.scatter_chart(pair, x=col1, y=col2)
