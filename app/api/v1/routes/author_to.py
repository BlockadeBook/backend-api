from flask import Blueprint, current_app, jsonify, make_response
import httpx

author_to_api = Blueprint("author_to_api", __name__, url_prefix='/author')

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

def _author_get(author_id: int) -> tuple[dict | None, int, Exception | None]:
    return _get_json(f"authors/{author_id}")

def return_response(data, status_code, error):
    if not data:
        return make_response(jsonify({"error": str(error)}), status_code)
    return make_response(jsonify(data), 200)

def _author_to_field(field: str, author_id: int):
    data, status_code, error = _author_get(author_id)
    if not data:
        return make_response(jsonify({"error": str(error)}), status_code)
    return make_response(jsonify(data[field]), 200)

def get_request(url: str):
    return return_response(*_get_json(url))

@author_to_api.route('/<int:author_id>', methods=['GET'])
def single_author(author_id: int):
    return get_request(f"authors/{author_id}")

@author_to_api.route('/social_classes/<int:author_id>', methods=['GET'])
def author_to_social_classes(author_id: int):
    return _author_to_field("social_classes", author_id)


@author_to_api.route('/nationalities/<int:author_id>', methods=['GET'])
def author_to_nationalities(author_id: int):
    return _author_to_field("nationalities", author_id)


@author_to_api.route('/education/<int:author_id>', methods=['GET'])
def author_to_education(author_id: int):
    return _author_to_field("education", author_id)


@author_to_api.route('/occupation/<int:author_id>', methods=['GET'])
def author_to_occupation(author_id: int):
    return _author_to_field("occupation", author_id)


@author_to_api.route('/cards/<int:author_id>', methods=['GET'])
def author_to_cards(author_id: int):
    return _author_to_field("cards", author_id)


@author_to_api.route('/religions/<int:author_id>', methods=['GET'])
def author_to_religions(author_id: int):
    return _author_to_field("religions", author_id)


@author_to_api.route('/political_parties/<int:author_id>', methods=['GET'])
def author_to_political_parties(author_id: int):
    return _author_to_field("political_parties", author_id)


@author_to_api.route('/family_status/<int:family_status_id>', methods=['GET'])
def family_status_id_to_name(family_status_id: int):
    db_url = current_app.config['DATABASE_URL']
    full_url = f"{db_url}/authors/family_status/{family_status_id}"
    try:
        response = httpx.get(full_url, timeout=10)
        response.raise_for_status()
        return response.json(), 200, None
    except httpx.RequestError as exc:
        return None, 503, exc
    except httpx.HTTPStatusError as exc:
        return None, exc.response.status_code, exc

@author_to_api.route('/all', methods=['GET'])
def all_authors():
    return get_request("authors/")

@author_to_api.route('/greet', methods=['GET'])
def greeting():
    return "Hi!"
