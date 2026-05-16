# Query Filtering on Gateway

## Problem

Frontend needs server-side filtering on list endpoints. Database-core has no filtering — returns full collections. Filtering must be implemented in backend-api.

## Approach

Post-fetch filtering: gateway fetches full list from database-core, filters JSON in-process, returns subset.

## Endpoints & Parameters

### GET /notes/

| Parameter | Type | Filter logic |
|---|---|---|
| `tag_id` | int (repeatable) | `tag_id in note.tags[].id` |
| `note_type_id` | int (repeatable) | `note.note_type_id == value` |
| `temporality_id` | int (repeatable) | `note.temporality_id == value` |

### GET /points/

| Parameter | Type | Filter logic |
|---|---|---|
| `point_type_id` | int (repeatable) | `point.point_type_id == value` |
| `point_subtype_id` | int (repeatable) | `point.point_subtype_id == value` |
| `point_subsubtype_id` | int (repeatable) | `point.point_subsubtype_id == value` |

### GET /authors/

| Parameter | Type | Filter logic |
|---|---|---|
| `family_status_id` | int | `author.family_status_id == value` |
| `social_class_id` | int (repeatable) | `value in author.social_classes[].id` |
| `nationality_id` | int (repeatable) | `value in author.nationalities[].id` |
| `religion_id` | int (repeatable) | `value in author.religions[].id` |
| `education_id` | int (repeatable) | `value in author.education[].id` |
| `occupation_id` | int (repeatable) | `value in author.occupation[].id` |
| `political_party_id` | int (repeatable) | `value in author.political_parties[].id` |
| `card_id` | int (repeatable) | `value in author.cards[].id` |

## Rules

- All parameters optional
- Multiple values via repeated params: `?tag_id=1&tag_id=2`
- Multiple different params = AND logic
- Multiple values of same param = OR within that field
- No pagination in this iteration

## Implementation

1. Add `filter_response()` helper in `app/api/proxy.py`
2. Accept query params via `Depends(FilterParams)` or direct `Query()` on list endpoints
3. Filter returned JSON before response model validation
