from flask import Blueprint

from app.api.v1.routes.utils import get_request

note_to_api = Blueprint("note_to_api", __name__, url_prefix='/note')


@note_to_api.route('/<int:note_id>', methods=['GET'])
def get_note(note_id: int):
    return get_request(f"notes/{note_id}")

@note_to_api.route('/detailed/<int:note_id>', methods=['GET'])
def detailed_note(note_id: int):
    return get_request(f"notes/detailed/{note_id}")

