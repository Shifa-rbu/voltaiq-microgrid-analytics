import numpy as np
import pandas as pd
import streamlit as st
from engine.grid_math import (
    matrix_basic_operations,
    matrix_advanced_products,
    matrix_inversion_and_eigen,
    feeder_stress_test,
    make_checkerboard,
    analyze_weather_rainfall,
)
from views.ui_components import page_heading


def _parse_matrix(text, shape):
    values = np.fromstring(text.replace(",", " "), sep=" ")
    if values.size != shape[0] * shape[1]:
        raise ValueError(f"Enter exactly {shape[0] * shape[1]} numeric values.")
    return values.reshape(shape)


def render():
    page_heading("matrix", "GRID MATH / PRACTICAL 5", "Matrix Stability Engine", "Matrix operations, stability diagnostics, statistical samples, and rainfall analysis.")
    arithmetic_tab, stability_tab, stress_tab, rainfall_tab = st.tabs(["Matrix operations", "Stability", "Stress test & mask", "Rainfall"])
    with arithmetic_tab:
        shape_choice = st.radio("Matrix dimensions", ["3 x 3", "4 x 4"], horizontal=True)
        n = int(shape_choice[0])
        default_a = "1 2 3 4 5 6 7 8 9" if n == 3 else "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16"
        default_b = "9 8 7 6 5 4 3 2 1" if n == 3 else "16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1"
        c1, c2 = st.columns(2)
        text_a = c1.text_area("M1 values, row-major", default_a)
        text_b = c2.text_area("M2 values, row-major", default_b)
        if st.button("Run matrix operations", type="primary"):
            try:
                a, b = _parse_matrix(text_a, (n, n)), _parse_matrix(text_b, (n, n))
                results = matrix_basic_operations(a, b)
                st.subheader("Element-wise operations")
                for name, value in results.items():
                    st.write(name.title())
                    st.dataframe(pd.DataFrame(value), hide_index=True, use_container_width=True)
                if n == 3:
                    st.subheader("Matrix products")
                    for name, value in matrix_advanced_products(a, b).items():
                        st.write(name.title())
                        st.dataframe(pd.DataFrame(value), hide_index=True, use_container_width=True)
            except ValueError as exc:
                st.error(str(exc))

    with stability_tab:
        matrix_text = st.text_area("3 x 3 impedance matrix, 9 row-major values", "4 1 0 1 3 1 0 1 2")
        if st.button("Analyze stability matrix"):
            try:
                matrix = _parse_matrix(matrix_text, (3, 3))
                determinant, inverse, values, vectors = matrix_inversion_and_eigen(matrix)
                st.metric("Determinant", f"{determinant:.6g}")
                c1, c2 = st.columns(2)
                c1.write("Inverse")
                c1.dataframe(pd.DataFrame(inverse), hide_index=True)
                c2.write("Eigenvalues")
                c2.write(values)
                st.write("Eigenvectors")
                st.dataframe(pd.DataFrame(vectors), hide_index=True)
            except (ValueError, np.linalg.LinAlgError) as exc:
                st.error(f"Matrix could not be analyzed: {exc}")

    with stress_tab:
        if st.button("Generate feeder stress sample"):
            data = feeder_stress_test()
            st.write({key: data[key] for key in ["mean", "variance", "standard_deviation", "percentile_60", "percentile_70"]})
            st.bar_chart(pd.Series(data["marks"]).value_counts().sort_index())
        n = st.slider("Checkerboard dimension", min_value=2, max_value=20, value=8)
        st.dataframe(pd.DataFrame(make_checkerboard(n)), hide_index=True, use_container_width=True)

    with rainfall_tab:
        st.caption("Enter 35 observed readings in city-row/day-column order (5 rows x 7 days).")
        rainfall_text = st.text_area("Rainfall values (mm)", "0 0 0 0 0 0 0\n0 0 0 0 0 0 0\n0 0 0 0 0 0 0\n0 0 0 0 0 0 0\n0 0 0 0 0 0 0")
        if st.button("Analyze rainfall"):
            try:
                values = _parse_matrix(rainfall_text, (5, 7))
                summary = analyze_weather_rainfall(values)
                st.write("City totals (rows):", summary["city_totals"])
                st.write("Daily averages (columns):", summary["daily_averages"])
                st.write("Highest-total city row (0-based):", summary["highest_rainfall_city_index"])
                st.write("Readings above 20 mm:", summary["values_above_20mm"])
                st.write(f"Min: {summary['minimum']} mm | Max: {summary['maximum']} mm")
            except ValueError as exc:
                st.error(str(exc))
