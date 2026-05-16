from __future__ import annotations

from typing import Any


def filter_response(
    items: list[dict[str, Any]],
    filters: dict[str, list[int]],
    list_fields: set[str],
) -> list[dict[str, Any]]:
    """Filter a list of dicts by query parameters.

    Args:
        items: Raw JSON items from database-core.
        filters: Mapping of field name → list of accepted values.
                 Empty list means "no filter on this field".
        list_fields: Fields where the value is a list of dicts with an "id" key.
                     For these, the filter checks if any item.id matches.
                     For non-list fields, the filter checks direct equality.

    Logic:
        - Each field in filters is OR (any value matches).
        - Across fields is AND (all must match).
        - If no filters provided, returns items unchanged.
    """
    if not filters:
        return items

    active = {k: v for k, v in filters.items() if v}
    if not active:
        return items

    result = []
    for item in items:
        match = True
        for field, values in active.items():
            if field in list_fields:
                item_ids = {entry["id"] for entry in item.get(field, [])}
                if not item_ids.intersection(values):
                    match = False
                    break
            else:
                if item.get(field) not in values:
                    match = False
                    break
        if match:
            result.append(item)
    return result