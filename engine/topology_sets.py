"""Smart-device topology operations and survey inclusion-exclusion."""

from __future__ import annotations

from collections.abc import Mapping
from math import gcd
from typing import Any


class SmartGridTopology:
    """Store and query smart-grid devices.

    Supply the exact ten records from the syllabus table as ``devices``. Each
    mapping value must contain Name, Room, Status (ON/OFF), and kWh. The class
    deliberately does not invent syllabus-specific readings or room names.
    """

    def __init__(self, devices: Mapping[Any, Mapping[str, Any]]) -> None:
        if not isinstance(devices, Mapping):
            raise TypeError("devices must be a mapping keyed by Device_ID")
        self.devices: dict[Any, dict[str, Any]] = {}
        required = {"Name", "Room", "Status", "kWh"}
        for device_id, details in devices.items():
            missing = required - details.keys()
            if missing:
                raise ValueError(f"device {device_id!r} missing fields: {sorted(missing)}")
            status = str(details["Status"]).upper()
            if status not in {"ON", "OFF"}:
                raise ValueError(f"device {device_id!r} has invalid Status {details['Status']!r}")
            kwh = float(details["kWh"])
            if kwh < 0:
                raise ValueError(f"device {device_id!r} kWh must be non-negative")
            self.devices[device_id] = {
                "Name": str(details["Name"]),
                "Room": str(details["Room"]),
                "Status": status,
                "kWh": kwh,
            }

    def filter_by_room(self, room_name: str = "Living Room") -> dict[Any, dict[str, Any]]:
        """Return matching device records for a room (case-insensitive)."""
        return {
            device_id: details.copy()
            for device_id, details in self.devices.items()
            if details["Room"].casefold() == room_name.casefold()
        }

    def get_active_devices(self) -> dict[Any, dict[str, Any]]:
        """Return devices whose power status is ON."""
        return {
            device_id: details.copy()
            for device_id, details in self.devices.items()
            if details["Status"] == "ON"
        }

    def calculate_total_energy(self) -> float:
        """Return the sum of all recorded device energy values."""
        return sum(details["kWh"] for details in self.devices.values())

    def calculate_active_energy(self) -> float:
        """Return the sum of kWh values for devices whose status is ON."""
        return sum(details["kWh"] for details in self.devices.values() if details["Status"] == "ON")

    def get_max_energy_device(self) -> tuple[Any, dict[str, Any]] | None:
        """Return ``(device_id, record)`` for the largest kWh, or None if empty."""
        if not self.devices:
            return None
        device_id = max(self.devices, key=lambda key: self.devices[key]["kWh"])
        return device_id, self.devices[device_id].copy()

    def update_power_status(self, device_id: Any, new_status: str) -> dict[str, Any]:
        """Set a device status and return its updated record."""
        if device_id not in self.devices:
            raise KeyError(f"unknown device_id: {device_id!r}")
        if not isinstance(new_status, str) or new_status.upper() not in {"ON", "OFF"}:
            raise ValueError("new_status must be 'ON' or 'OFF'")
        self.devices[device_id]["Status"] = new_status.upper()
        return self.devices[device_id].copy()


def solve_student_survey(total: int = 500) -> dict[str, Any]:
    """Calculate sport-set regions from the supplied survey percentages.

    Percentages are converted to counts using ``total``. Counts must be
    integral; inconsistent resulting regions raise ValueError.
    """
    if isinstance(total, bool) or not isinstance(total, int) or total < 0:
        raise ValueError("total must be a non-negative integer")
    counts = {
        "football": 0.49 * total,
        "hockey": 0.53 * total,
        "basketball": 0.62 * total,
        "football_hockey": 0.27 * total,
        "basketball_hockey": 0.29 * total,
        "football_basketball": 0.28 * total,
        "none": 0.05 * total,
    }
    if any(value != int(value) for value in counts.values()):
        raise ValueError("total must yield whole-number counts for the supplied percentages")
    counts = {key: int(value) for key, value in counts.items()}
    union = total - counts["none"]
    all_three = (
        union
        - counts["football"]
        - counts["hockey"]
        - counts["basketball"]
        + counts["football_hockey"]
        + counts["basketball_hockey"]
        + counts["football_basketball"]
    )
    only_football = counts["football"] - counts["football_hockey"] - counts["football_basketball"] + all_three
    only_hockey = counts["hockey"] - counts["football_hockey"] - counts["basketball_hockey"] + all_three
    only_basketball = counts["basketball"] - counts["football_basketball"] - counts["basketball_hockey"] + all_three
    exactly_one = only_football + only_hockey + only_basketball
    at_least_two = union - exactly_one
    regions = (all_three, only_football, only_hockey, only_basketball, exactly_one, at_least_two)
    if any(value < 0 for value in regions):
        raise ValueError("the supplied percentages imply an inconsistent survey")
    divisor = gcd(only_football, only_hockey) or 1
    ratio = (only_football // divisor, only_hockey // divisor)
    return {
        "all_three_sports": all_three,
        "only_football": only_football,
        "only_hockey": only_hockey,
        "only_basketball": only_basketball,
        "only_football_to_only_hockey_ratio": ratio,
        "exactly_one_sport": exactly_one,
        "at_least_two_sports": at_least_two,
        "none": counts["none"],
        "union": union,
    }


def solve_survey_venn(total: int = 500) -> dict[str, Any]:
    """Return the same set analysis with the scheme terminology in the contract."""
    result = solve_student_survey(total)
    return {
        **result,
        "subscribed_to_all_three": result["all_three_sports"],
        "exactly_one_scheme": result["exactly_one_sport"],
        "at_least_two_schemes": result["at_least_two_sports"],
        "solely_solar": result["only_football"],
        "solely_wind": result["only_hockey"],
        "solely_solar_to_solely_wind_ratio": result["only_football_to_only_hockey_ratio"],
    }


if __name__ == "__main__":
    demo_devices = {
        "D1": {"Name": "Smart Light", "Room": "Living Room", "Status": "ON", "kWh": 0.4},
        "D2": {"Name": "Smart TV", "Room": "Living Room", "Status": "OFF", "kWh": 1.2},
        "D3": {"Name": "Smart AC", "Room": "Bedroom", "Status": "ON", "kWh": 2.8},
        "D4": {"Name": "Smart Fan", "Room": "Bedroom", "Status": "ON", "kWh": 0.7},
        "D5": {"Name": "Smart Fridge", "Room": "Kitchen", "Status": "ON", "kWh": 3.1},
        "D6": {"Name": "Smart Oven", "Room": "Kitchen", "Status": "OFF", "kWh": 1.9},
        "D7": {"Name": "Smart Speaker", "Room": "Living Room", "Status": "ON", "kWh": 0.2},
        "D8": {"Name": "Smart Washer", "Room": "Utility", "Status": "OFF", "kWh": 1.6},
        "D9": {"Name": "Smart Heater", "Room": "Bedroom", "Status": "OFF", "kWh": 2.2},
        "D10": {"Name": "Smart Camera", "Room": "Entry", "Status": "ON", "kWh": 0.3},
    }
    topology = SmartGridTopology(demo_devices)  # Replace with exact syllabus table values.
    print("Active devices:", topology.get_active_devices())
    print("Total energy:", topology.calculate_total_energy())
    print("Maximum-energy device:", topology.get_max_energy_device())
    print("Survey analysis:", solve_student_survey())
