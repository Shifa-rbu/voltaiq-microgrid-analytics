"""Validation and aggregation helpers for uploaded campus meter readings."""
from __future__ import annotations

from typing import Any

import pandas as pd


REQUIRED_CANONICAL_COLUMNS = ["timestamp", "building", "meter_id", "energy_kwh"]


def prepare_meter_readings(
    frame: pd.DataFrame,
    timestamp_column: str,
    building_column: str,
    energy_column: str,
    meter_column: str | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Map chosen input fields to canonical columns and report quality issues.

    Invalid timestamps, non-numeric energy readings, and negative energy values
    are excluded from the returned analysis frame and counted in the quality report.
    Missing building or meter labels remain usable as ``Unassigned``.
    """
    required = [timestamp_column, building_column, energy_column]
    missing_columns = [column for column in required if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"Selected columns are missing from the file: {', '.join(missing_columns)}")
    if meter_column and meter_column not in frame.columns:
        raise ValueError(f"Selected meter column '{meter_column}' is missing from the file.")

    raw_timestamp = frame[timestamp_column]
    parsed_timestamp = pd.to_datetime(raw_timestamp, errors="coerce", utc=True)
    raw_energy = frame[energy_column]
    numeric_energy = pd.to_numeric(raw_energy, errors="coerce")
    building = frame[building_column].astype("string").str.strip()
    building_missing = building.isna() | building.eq("")
    building = building.mask(building_missing, "Unassigned").astype(str)

    if meter_column:
        meter = frame[meter_column].astype("string").str.strip()
        meter_missing = meter.isna() | meter.eq("")
        meter = meter.mask(meter_missing, "Unassigned").astype(str)
    else:
        meter = pd.Series(["Not provided"] * len(frame), index=frame.index, dtype="string")
        meter_missing = pd.Series([True] * len(frame), index=frame.index)

    timestamp_valid = parsed_timestamp.notna()
    energy_valid = numeric_energy.notna() & numeric_energy.ge(0)
    valid = timestamp_valid & energy_valid
    normalized = pd.DataFrame(
        {
            "timestamp": parsed_timestamp[valid],
            "building": building[valid],
            "meter_id": meter[valid].astype(str),
            "energy_kwh": numeric_energy[valid].astype(float),
        }
    ).reset_index(drop=True)
    normalized = normalized.sort_values("timestamp", kind="stable").reset_index(drop=True)

    invalid_numeric_energy = numeric_energy.isna() & raw_energy.notna() & raw_energy.astype(str).str.strip().ne("")
    negative_energy = numeric_energy.lt(0).fillna(False)
    report = {
        "input_rows": int(len(frame)),
        "valid_rows": int(valid.sum()),
        "invalid_timestamp_rows": int((~timestamp_valid).sum()),
        "missing_or_invalid_energy_rows": int((numeric_energy.isna()).sum()),
        "non_numeric_energy_rows": int(invalid_numeric_energy.sum()),
        "negative_energy_rows": int(negative_energy.sum()),
        "missing_building_labels": int(building_missing.sum()),
        "missing_meter_labels": int(meter_missing.sum()),
        "duplicate_readings": int(normalized.duplicated(["timestamp", "building", "meter_id"]).sum()),
    }
    return normalized[REQUIRED_CANONICAL_COLUMNS], report


def summarize_meter_readings(frame: pd.DataFrame) -> dict[str, Any]:
    """Summarize an already validated meter-data slice."""
    if frame.empty:
        return {"reading_count": 0, "total_kwh": 0.0, "mean_kwh": 0.0, "peak_kwh": 0.0, "peak_timestamp": None}
    peak_index = frame["energy_kwh"].idxmax()
    return {
        "reading_count": int(len(frame)),
        "total_kwh": float(frame["energy_kwh"].sum()),
        "mean_kwh": float(frame["energy_kwh"].mean()),
        "peak_kwh": float(frame.loc[peak_index, "energy_kwh"]),
        "peak_timestamp": frame.loc[peak_index, "timestamp"],
    }
