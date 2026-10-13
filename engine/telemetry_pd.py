"""Pandas cleaning, feature engineering, and Pearson correlation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import pearsonr


def load_and_clean_telemetry(csv_path: str | Path) -> tuple[pd.DataFrame, pd.Series]:
    """Load CSV, replace the practical's abnormal markers, and count nulls.

    Returns ``(cleaned_dataframe, missing_counts_by_column)``. Counts are
    computed after dropping the optional ``Id`` column.
    """
    frame = pd.read_csv(csv_path)
    frame = frame.replace({"??": np.nan, "##": np.nan})
    if "Id" in frame.columns:
        frame = frame.drop(columns="Id")
    missing_counts = frame.isna().sum()
    return frame, missing_counts


def impute_missing_telemetry(df: pd.DataFrame) -> pd.DataFrame:
    """Fill Petal Width with its mean and Sepal Length with its mode."""
    required = {"Petal Width", "Sepal Length"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"missing required columns: {sorted(missing)}")
    result = df.copy()
    petal_width = pd.to_numeric(result["Petal Width"], errors="coerce")
    mean_value = petal_width.mean()
    if pd.isna(mean_value) and petal_width.isna().any():
        raise ValueError("Petal Width has no non-missing numeric values to compute its mean")
    result["Petal Width"] = petal_width.fillna(mean_value)
    sepal_length = pd.to_numeric(result["Sepal Length"], errors="coerce")
    modes = sepal_length.mode(dropna=True)
    if modes.empty and sepal_length.isna().any():
        raise ValueError("Sepal Length has no non-missing numeric values to compute its mode")
    if not modes.empty:
        result["Sepal Length"] = sepal_length.fillna(modes.iloc[0])
    return result


def engineer_features(df: pd.DataFrame) -> tuple[pd.DataFrame, Any, pd.DataFrame]:
    """Add Petal_Area and return (frame, highest-mean species, top 5 rows)."""
    required = {"Petal Length", "Petal Width"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"missing required columns: {sorted(missing)}")
    species_column = next((name for name in ("Species", "species") if name in df.columns), None)
    if species_column is None:
        raise KeyError("a 'Species' or 'species' column is required")
    result = df.copy()
    result["Petal_Area"] = (
        pd.to_numeric(result["Petal Length"], errors="coerce")
        * pd.to_numeric(result["Petal Width"], errors="coerce")
    )
    means = result.groupby(species_column, dropna=True)["Petal_Area"].mean()
    if means.empty:
        return result, None, result.head(0).copy()
    highest_species = means.idxmax()
    top_five = result.nlargest(5, "Petal_Area").copy()
    return result, highest_species, top_five


def manual_pearson_r(x: Any, y: Any) -> float:
    """Compute Pearson's r from raw summations; return NaN for zero variance."""
    x_values = np.asarray(x, dtype=float).ravel()
    y_values = np.asarray(y, dtype=float).ravel()
    if x_values.size != y_values.size:
        raise ValueError("x and y must contain the same number of values")
    if x_values.size < 2:
        raise ValueError("at least two paired observations are required")
    if not np.isfinite(x_values).all() or not np.isfinite(y_values).all():
        raise ValueError("x and y must contain only finite values")
    n = x_values.size
    sum_x = x_values.sum()
    sum_y = y_values.sum()
    sum_xy = np.dot(x_values, y_values)
    numerator = n * sum_xy - sum_x * sum_y
    x_term = n * np.dot(x_values, x_values) - sum_x**2
    y_term = n * np.dot(y_values, y_values) - sum_y**2
    denominator = np.sqrt(max(x_term, 0.0) * max(y_term, 0.0))
    if denominator == 0:
        return float("nan")
    return float(numerator / denominator)


def scipy_pearson_r(x: Any, y: Any) -> float:
    """Compute Pearson's r with SciPy and return the coefficient only."""
    x_values = np.asarray(x, dtype=float).ravel()
    y_values = np.asarray(y, dtype=float).ravel()
    if x_values.size != y_values.size:
        raise ValueError("x and y must contain the same number of values")
    if x_values.size < 2:
        raise ValueError("at least two paired observations are required")
    with np.errstate(invalid="ignore"):
        return float(pearsonr(x_values, y_values)[0])


def verify_correlation_parity(df: pd.DataFrame, col1: str, col2: str) -> bool:
    """Return whether the manual and SciPy coefficients are numerically equal."""
    manual_value = manual_pearson_r(df[col1], df[col2])
    scipy_value = scipy_pearson_r(df[col1], df[col2])
    return bool(np.isclose(manual_value, scipy_value, equal_nan=True))


if __name__ == "__main__":
    csv_path = Path(__file__).resolve().parents[1] / "data" / "Iris_data_sample.csv"
    if csv_path.exists():
        cleaned, missing = load_and_clean_telemetry(csv_path)
        print("Missing values before imputation:\n", missing)
        imputed = impute_missing_telemetry(cleaned)
        featured, top_species, top_rows = engineer_features(imputed)
        print("Species with highest mean Petal_Area:", top_species)
        print("Top five rows:\n", top_rows)
        numeric_columns = featured.select_dtypes(include="number").columns
        if len(numeric_columns) >= 2:
            print("Correlation parity:", verify_correlation_parity(featured, numeric_columns[0], numeric_columns[1]))
    else:
        print(f"Dataset not found at {csv_path}; copy Iris_data_sample.csv into data/ to run the CSV workflow.")
        demo = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 6, 8]})
        print("Correlation parity demo:", verify_correlation_parity(demo, "x", "y"))
