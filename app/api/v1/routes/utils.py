import httpx
from flask import current_app, make_response, jsonify


def _get_json(url_in_db) -> tuple[dict | None, int, Exception | None]:
    db_url = current_app.config['DATABASE_URL']
    full_url = f"{db_url}/{url_in_db}"
    try:
        response = httpx.get(full_url, timeout=10)
        response.raise_for_status()
        return response.json(), 200, None
    except httpx.RequestError as exc:
        return None, 503, exc
    except httpx.HTTPStatusError as exc:
        return None, exc.response.status_code, exc


def return_response(data, status_code, error):
    if not data:
        return make_response(jsonify({"error": str(error)}), status_code)
    return make_response(jsonify(data), 200)


def get_request(url: str):
    return return_response(*_get_json(url))