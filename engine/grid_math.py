"""NumPy helpers for matrices, random marks, and rainfall summaries."""

from __future__ import annotations

from typing import Any

import numpy as np


def _array_with_shape(value: Any, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = np.asarray(value)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}; got {array.shape}")
    return array


def matrix_basic_operations(m1: Any, m2: Any) -> dict[str, np.ndarray]:
    """Return element-wise arithmetic for matching 3x3 or 4x4 matrices."""
    left = np.asarray(m1)
    right = np.asarray(m2)
    if left.shape not in {(3, 3), (4, 4)} or right.shape != left.shape:
        raise ValueError(f"m1 and m2 must have matching 3x3 or 4x4 shapes; got {left.shape} and {right.shape}")
    with np.errstate(divide="ignore", invalid="ignore"):
        division = np.divide(left, right)
    return {
        "addition": np.add(left, right),
        "subtraction": np.subtract(left, right),
        "multiplication": np.multiply(left, right),
        "division": division,
    }


def matrix_advanced_products(m1: Any, m2: Any) -> dict[str, np.ndarray]:
    """Return dot, inner, outer, and cross products for two 3x3 matrices."""
    left = _array_with_shape(m1, (3, 3), "m1")
    right = _array_with_shape(m2, (3, 3), "m2")
    with np.errstate(divide="ignore", invalid="ignore"):
        division = np.divide(left, right)
    return {
        "addition": np.add(left, right),
        "subtraction": np.subtract(left, right),
        "multiplication": np.multiply(left, right),
        "division": division,
        "dot": np.dot(left, right),
        "inner": np.inner(left, right),
        "outer": np.outer(left, right),
        "cross": np.cross(left, right),
    }


def matrix_inversion_and_eigen(matrix_3x3: Any) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """Return determinant, inverse, eigenvalues, and eigenvectors of a 3x3 matrix."""
    matrix = _array_with_shape(matrix_3x3, (3, 3), "matrix_3x3").astype(float)
    determinant = float(np.linalg.det(matrix))
    inverse = np.linalg.inv(matrix)
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    return determinant, inverse, eigenvalues, eigenvectors


def generate_checkerboard(n: int) -> np.ndarray:
    """Return an n-by-n array of alternating zeros and ones."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError("n must be a non-negative integer")
    return np.indices((n, n)).sum(axis=0) % 2


def generate_student_percentiles(seed: int | None = None) -> dict[str, Any]:
    """Generate the two mark samples and report their requested percentiles.

    ``seed`` is optional and makes the generated exercise data reproducible.
    """
    rng = np.random.default_rng(seed)
    first_marks = rng.integers(30, 96, size=100)
    second_marks = rng.integers(40, 96, size=80)
    return {
        "marks_100": first_marks,
        "percentile_60_for_100": float(np.percentile(first_marks, 60)),
        "marks_80": second_marks,
        "percentile_70_for_80": float(np.percentile(second_marks, 70)),
    }


def feeder_stress_test(seed: int | None = None) -> dict[str, Any]:
    """Generate 100 marks in [30, 95] and report summary statistics."""
    rng = np.random.default_rng(seed)
    marks = rng.integers(30, 96, size=100)
    return {
        "marks": marks,
        "mean": float(np.mean(marks)),
        "variance": float(np.var(marks)),
        "standard_deviation": float(np.std(marks)),
        "percentile_60": float(np.percentile(marks, 60)),
        "percentile_70": float(np.percentile(marks, 70)),
    }


def make_checkerboard(n: int) -> np.ndarray:
    """Contract-compatible name for generating an n-by-n checkerboard."""
    return generate_checkerboard(n)


def analyze_weather_rainfall(rainfall_matrix: Any) -> dict[str, Any]:
    """Summarize a 5-city x 7-day rainfall matrix, preserving row/column order."""
    rainfall = _array_with_shape(rainfall_matrix, (5, 7), "rainfall_matrix").astype(float)
    if not np.isfinite(rainfall).all():
        raise ValueError("rainfall_matrix must contain only finite values")
    city_totals = rainfall.sum(axis=1)
    daily_averages = rainfall.mean(axis=0)
    highest_city_index = int(np.argmax(city_totals))
    return {
        "city_totals": city_totals,
        "daily_averages": daily_averages,
        "highest_rainfall_city_index": highest_city_index,
        "highest_rainfall_city_total": float(city_totals[highest_city_index]),
        "values_above_20mm": rainfall[rainfall > 20],
        "minimum": float(rainfall.min()),
        "maximum": float(rainfall.max()),
    }


if __name__ == "__main__":
    first = np.arange(1, 17).reshape(4, 4)
    second = np.arange(16, 0, -1).reshape(4, 4)
    print("Basic 4x4 operations:", matrix_basic_operations(first, second))
    left = np.arange(1, 10).reshape(3, 3)
    right = np.arange(9, 0, -1).reshape(3, 3)
    print("Advanced 3x3 products:", matrix_advanced_products(left, right))
    print("Inversion/eigen:", matrix_inversion_and_eigen(np.eye(3)))
    print("Checkerboard:\n", generate_checkerboard(6))
    print("Student percentiles:", generate_student_percentiles(seed=7))
    demo_rainfall = np.arange(35, dtype=float).reshape(5, 7)
    print("Rainfall summary:", analyze_weather_rainfall(demo_rainfall))
