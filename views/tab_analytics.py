from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from engine.telemetry_pd import (
    engineer_features,
    impute_missing_telemetry,
    load_and_clean_telemetry,
    verify_correlation_parity,
)
from views.ui_components import page_heading


def _read_upload(file_bytes: bytes, filename: str, sheet_name: str | None = None) -> pd.DataFrame:
    suffix = Path(filename).suffix.casefold()
    if suffix == ".csv":
        return pd.read_csv(BytesIO(file_bytes))
    if suffix == ".xlsx":
        return pd.read_excel(BytesIO(file_bytes), sheet_name=sheet_name or 0, engine="openpyxl")
    raise ValueError("Upload a .csv or .xlsx file.")


def _numeric_summary(frame: pd.DataFrame) -> pd.DataFrame:
    numeric = frame.select_dtypes(include="number")
    if numeric.empty:
        return pd.DataFrame()
    return numeric.describe().T.rename_axis("Column").reset_index()


def render():
    page_heading(
        "chart",
        "TELEMETRY / DATA WORKBENCH",
        "File Analytics",
        "Explore CSV and Excel datasets with previews, quality checks, summaries, and charts.",
    )

    default_path = Path(__file__).resolve().parents[1] / "data" / "Iris_data_sample.csv"
    uploaded = st.file_uploader(
        "Upload a data file",
        type=["csv", "xlsx"],
        help="CSV and Excel .xlsx files are supported. Excel workbooks can contain multiple sheets.",
    )
    frame = None
    source_label = ""
    file_bytes = b""

    try:
        if uploaded is not None:
            file_bytes = uploaded.getvalue()
            source_label = uploaded.name
            if Path(uploaded.name).suffix.casefold() == ".xlsx":
                workbook = pd.ExcelFile(BytesIO(file_bytes), engine="openpyxl")
                if not workbook.sheet_names:
                    st.warning("This workbook contains no readable worksheets.")
                    return
                chosen_sheet = st.selectbox("Worksheet", workbook.sheet_names)
                frame = _read_upload(file_bytes, uploaded.name, chosen_sheet)
                source_label = f"{uploaded.name} · {chosen_sheet}"
            else:
                frame = _read_upload(file_bytes, uploaded.name)
        elif default_path.exists():
            file_bytes = default_path.read_bytes()
            frame = pd.read_csv(BytesIO(file_bytes))
            source_label = "Built-in Iris sample CSV"
        else:
            st.info("Upload a CSV or Excel workbook to begin analyzing a dataset.")
            return
    except Exception as exc:
        st.error(f"Could not read this file: {exc}")
        return

    if frame is None or frame.empty:
        st.warning("The selected file has no data rows to analyze.")
        return
    frame.columns = [str(column).strip() or f"Column {index + 1}" for index, column in enumerate(frame.columns)]
    st.caption(f"Source: {source_label}")

    total_cells = int(frame.shape[0] * frame.shape[1])
    missing_cells = int(frame.isna().sum().sum())
    missing_percent = 100 * missing_cells / total_cells if total_cells else 0.0
    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Rows", f"{len(frame):,}")
    metric2.metric("Columns", f"{len(frame.columns):,}")
    metric3.metric("Missing cells", f"{missing_cells:,}", f"{missing_percent:.1f}% of cells")

    preview_tab, quality_tab, summary_tab, charts_tab = st.tabs(
        ["Data preview", "Data quality", "Summaries", "Charts & correlation"]
    )
    with preview_tab:
        st.dataframe(frame.head(100), use_container_width=True, height=380)
        base_name = Path(uploaded.name).stem if uploaded else "iris_sample"
        st.download_button(
            "Download data as CSV",
            data=frame.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{base_name}_analysis.csv",
            mime="text/csv",
        )

    with quality_tab:
        quality = pd.DataFrame(
            {
                "Column": frame.columns,
                "Data type": [str(dtype) for dtype in frame.dtypes],
                "Missing values": [int(value) for value in frame.isna().sum()],
                "Missing %": [round(100 * value / len(frame), 2) for value in frame.isna().sum()],
                "Unique values": [int(frame[column].nunique(dropna=True)) for column in frame.columns],
            }
        )
        st.dataframe(quality, hide_index=True, use_container_width=True)
        st.metric("Duplicate rows", f"{int(frame.duplicated().sum()):,}")

    with summary_tab:
        numeric_summary = _numeric_summary(frame)
        if not numeric_summary.empty:
            st.subheader("Numeric columns")
            st.dataframe(numeric_summary, hide_index=True, use_container_width=True)
        categorical = frame.select_dtypes(exclude="number").columns.tolist()
        if categorical:
            st.subheader("Category breakdown")
            category = st.selectbox("Choose a category column", categorical)
            values = frame[category].fillna("(missing)").astype(str).value_counts().head(15)
            st.bar_chart(values, height=280)
            st.dataframe(values.rename("Rows").rename_axis(category).reset_index(), hide_index=True, use_container_width=True)
        if numeric_summary.empty and not categorical:
            st.info("No numeric or categorical columns were found to summarize.")

    with charts_tab:
        numeric_columns = frame.select_dtypes(include="number").columns.tolist()
        if numeric_columns:
            selected_numeric = st.selectbox("Numeric field to chart", numeric_columns)
            series = pd.to_numeric(frame[selected_numeric], errors="coerce").dropna().reset_index(drop=True)
            st.caption(f"Showing {len(series):,} valid observations for {selected_numeric}.")
            st.line_chart(series, height=280)
            if len(numeric_columns) >= 2:
                st.subheader("Correlation matrix")
                correlations = frame[numeric_columns].corr(numeric_only=True)
                st.dataframe(correlations, use_container_width=True)
                left, right = st.columns(2)
                x_col = left.selectbox("First field", numeric_columns, index=0, key="file_corr_x")
                y_col = right.selectbox("Second field", numeric_columns, index=1, key="file_corr_y")
                pair = frame[[x_col, y_col]].dropna()
                if len(pair) >= 2 and pair[x_col].nunique() > 1 and pair[y_col].nunique() > 1:
                    st.scatter_chart(pair, x=x_col, y=y_col)
                    st.metric("Pearson correlation", f"{pair[x_col].corr(pair[y_col]):.4f}")
                else:
                    st.info("Select fields with at least two valid, non-constant observations for a correlation.")
        else:
            st.info("No numeric columns are available for a numeric chart or correlation analysis.")

    # Keep the original practical available when the uploaded data has compatible Iris fields.
    normalized = {str(column).replace(" ", "").casefold() for column in frame.columns}
    expected = {"sepallengthcm", "sepalwidthcm", "petallengthcm", "petalwidthcm", "species"}
    if expected.issubset(normalized):
        with st.expander("Iris practical: imputation and Petal_Area feature"):
            try:
                iris_data, missing = load_and_clean_telemetry(BytesIO(file_bytes))
                st.write("Missing values before imputation")
                st.dataframe(missing.rename("Missing count").to_frame(), use_container_width=True)
                filled = impute_missing_telemetry(iris_data)
                featured, highest_species, top_five = engineer_features(filled)
                st.write("Species with highest mean Petal_Area:", highest_species)
                st.dataframe(top_five, use_container_width=True)
                st.write(
                    "Pearson implementation parity:",
                    verify_correlation_parity(featured, "Petal_Area", "Sepal Length" if "Sepal Length" in featured else "SepalLengthCm"),
                )
            except (KeyError, ValueError, TypeError) as exc:
                st.info(f"General analysis is available; Iris-specific analysis could not run: {exc}")
