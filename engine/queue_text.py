"""Queue, text, tuple, and small inventory calculations."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from typing import Any


def analyze_telemetry_batches(
    processed_orders: Sequence[Any], returned_orders: Sequence[Any]
) -> dict[str, Any]:
    """Summarize two order-ID batches and split processed IDs into two chunks.

    The 50th combined ID is one-based (the element at sorted index 49). If the
    inputs contain fewer than 50 IDs, ``fiftieth_order_id`` is None.
    """
    processed = list(processed_orders)
    returned = list(returned_orders)
    combined_sorted = sorted(processed + returned)
    fiftieth = combined_sorted[49] if len(combined_sorted) >= 50 else None
    midpoint = (len(processed) + 1) // 2
    first_chunk = processed[:midpoint]
    second_chunk = processed[midpoint:]
    source = None
    if fiftieth is not None:
        source = {
            "processed": fiftieth in processed,
            "returned": fiftieth in returned,
        }
    return {
        "total_order_count": len(processed) + len(returned),
        "fiftieth_order_id": fiftieth,
        "fiftieth_order_membership": source,
        "last_processed_id": processed[-1] if processed else None,
        "first_four_processed_ids": processed[:4],
        "reversed_processed_chunks": [first_chunk[::-1], second_chunk[::-1]],
    }


def rotate_generator_queue(gen_list: Sequence[Any], k: int) -> list[Any]:
    """Left-rotate a queue by k places; non-positive k leaves it unchanged."""
    items = list(gen_list)
    if k <= 0 or not items:
        return items
    offset = k % len(items)
    return items[offset:] + items[:offset]


_PUNCTUATION_TO_REMOVE = "!()-[]{};:'\\\",<>./?@#$%^&*_~"


def sanitize_technician_log(raw_text: str) -> str:
    """Remove the punctuation characters listed in the practical."""
    if not isinstance(raw_text, str):
        raise TypeError("raw_text must be a string")
    return raw_text.translate(str.maketrans("", "", _PUNCTUATION_TO_REMOVE))


def tokenize_word_frequencies(cleaned_text: str) -> dict[str, int]:
    """Return case-insensitive word counts from already-cleaned text."""
    if not isinstance(cleaned_text, str):
        raise TypeError("cleaned_text must be a string")
    return dict(Counter(cleaned_text.casefold().split()))


def sum_third_elements_of_tuples(tuples_list: Sequence[Sequence[Any]]) -> Any:
    """Sum index-2 values, validating that each row has five elements."""
    total: Any = 0
    for index, row in enumerate(tuples_list):
        if len(row) != 5:
            raise ValueError(f"row {index} must contain exactly 5 elements")
        total += row[2]
    return total


def evaluate_ecommerce_inventory(
    number_list: Sequence[float], price_list: Sequence[float]
) -> dict[str, Any]:
    """Compute product counts and revenue from aligned quantities and prices.

    Each position represents one product. ``costliest_item_index`` is the
    zero-based position of its highest-priced product (first on ties).
    """
    quantities = list(number_list)
    prices = list(price_list)
    if len(quantities) != len(prices):
        raise ValueError("number_list and price_list must have equal lengths")
    if any(quantity < 0 for quantity in quantities) or any(price < 0 for price in prices):
        raise ValueError("quantities and prices must be non-negative")
    product_count = len(quantities)
    total_sold = sum(quantities)
    average_price = sum(prices) / product_count if product_count else 0.0
    highest_index = max(range(product_count), key=prices.__getitem__) if product_count else None
    return {
        "distinct_products": product_count,
        "total_sold": total_sold,
        "average_price": average_price,
        "costliest_item_index": highest_index,
        "costliest_item_price": prices[highest_index] if highest_index is not None else None,
        "total_revenue": sum(price * quantity for quantity, price in zip(quantities, prices)),
        "products_above_average_price": sum(price > average_price for price in prices),
    }


def analyze_batches(processed_list: Sequence[Any], returned_list: Sequence[Any]) -> dict[str, Any]:
    """Contract-compatible name for processing the two order batches."""
    return analyze_telemetry_batches(processed_list, returned_list)


def rotate_generators(gen_list: Sequence[Any], k: int) -> list[Any]:
    """Contract-compatible name for left-rotating generator dispatch order."""
    return rotate_generator_queue(gen_list, k)


def clean_log_text(raw_text: str) -> dict[str, int]:
    """Strip the specified punctuation and return case-insensitive word counts."""
    return tokenize_word_frequencies(sanitize_technician_log(raw_text))


if __name__ == "__main__":
    processed = list(range(1, 64))
    returned = list(range(64, 130))
    print("Telemetry summary:", analyze_telemetry_batches(processed, returned))
    print("Rotated queue:", rotate_generator_queue(["solar", "wind", "battery"], 1))
    clean = sanitize_technician_log("Voltage! alert: feeder-2 is stable.")
    print("Cleaned log:", clean)
    print("Word frequencies:", tokenize_word_frequencies(clean))
    print("Tuple sum:", sum_third_elements_of_tuples([(1, 2, 3, 4, 5)]))
    print("Inventory:", evaluate_ecommerce_inventory([4, 7, 2], [10, 8, 25]))
