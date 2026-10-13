"""Billing, asset depreciation, series, and server-alert helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def energy_charge(units: float) -> float:
    """Return a progressive energy charge in rupees for non-negative units."""
    units = float(units)
    if units < 0:
        raise ValueError("units must be non-negative")
    first = min(units, 100) * 4
    second = min(max(units - 100, 0), 100) * 6
    third = max(units - 200, 0) * 8
    return first + second + third


def fixed_charge(connection_type: str) -> float:
    """Return the fixed connection charge for Domestic or Commercial service."""
    if not isinstance(connection_type, str):
        raise TypeError("connection_type must be a string")
    charges = {"domestic": 100.0, "commercial": 250.0}
    try:
        return charges[connection_type.strip().casefold()]
    except KeyError as exc:
        raise ValueError("connection_type must be 'Domestic' or 'Commercial'") from exc


def calculate_electricity_bill(units: float, connection_type: str) -> dict[str, Any]:
    """Return an itemized bill; discount is applied before 12% GST."""
    energy = energy_charge(units)
    fixed = fixed_charge(connection_type)
    subtotal = energy + fixed
    discount_rate = 0.10 if subtotal > 1000 else 0.05 if subtotal > 500 else 0.0
    discount = subtotal * discount_rate
    taxable_amount = subtotal - discount
    gst_rate = 0.12
    gst = taxable_amount * gst_rate
    return {
        "units": float(units),
        "connection_type": connection_type.strip().title(),
        "energy_charge": round(energy, 2),
        "fixed_charge": round(fixed, 2),
        "subtotal": round(subtotal, 2),
        "discount_rate": discount_rate,
        "discount": round(discount, 2),
        "taxable_amount": round(taxable_amount, 2),
        "gst_rate": gst_rate,
        "gst": round(gst, 2),
        "total": round(taxable_amount + gst, 2),
    }


def calculate_depreciation(original_price: float, age_years: float) -> float:
    """Return book value after declining-balance depreciation by year band.

    Depreciation rates are 20% in year 1, 10% in years 2–5, and 5% after
    year 5. A fractional final year is prorated at that year's rate.
    """
    price = float(original_price)
    age = float(age_years)
    if price < 0 or age < 0:
        raise ValueError("original_price and age_years must be non-negative")
    remaining = price
    whole_years = int(age)
    for year in range(1, whole_years + 1):
        rate = 0.20 if year == 1 else 0.10 if year <= 5 else 0.05
        remaining *= 1 - rate
    fraction = age - whole_years
    if fraction:
        next_year = whole_years + 1
        rate = 0.20 if next_year == 1 else 0.10 if next_year <= 5 else 0.05
        remaining *= 1 - rate * fraction
    return remaining


def alternating_harmonic_loss(n: int) -> int:
    """Return 1 - 2 + 3 - 4 + ... through the positive integer n."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    return sum(i if i % 2 else -i for i in range(1, n + 1))


def reciprocal_product_loss(n: int) -> float:
    """Return sum(1 / (i * (i + 1))) for i from 1 through n."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    return sum(1 / (i * (i + 1)) for i in range(1, n + 1))


def parse_server_alerts(file_path: str | Path) -> tuple[list[str], int]:
    """Extract @rknec.edu sender addresses from lines beginning with ``From ``."""
    path = Path(file_path)
    senders: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            words = line.split()
            if len(words) >= 2 and words[0] == "From":
                email = words[1]
                local, separator, domain = email.rpartition("@")
                if separator and local and domain.casefold() == "rknec.edu":
                    senders.append(email)
    return senders, len(senders)


def alternating_series(n: int) -> int:
    """Contract-compatible name for the alternating harmonic sum."""
    return alternating_harmonic_loss(n)


def parse_mail_alerts(file_path: str | Path) -> tuple[list[str], int]:
    """Contract-compatible name for parsing institutional mail alerts."""
    return parse_server_alerts(file_path)


if __name__ == "__main__":
    print("Bill:", calculate_electricity_bill(250, "Domestic"))
    print("Book value after 6 years:", calculate_depreciation(100_000, 6))
    print("Alternating series (n=5):", alternating_harmonic_loss(5))
    print("Reciprocal product sum (n=5):", reciprocal_product_loss(5))
    alerts_file = Path(__file__).resolve().parents[1] / "data" / "server_alerts.txt"
    if alerts_file.exists():
        print("Valid alert senders:", parse_server_alerts(alerts_file))
    else:
        print(f"Alert sample not found: {alerts_file}")
