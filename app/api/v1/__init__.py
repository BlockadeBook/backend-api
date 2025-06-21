from flask import Blueprint
from app.api.v1.loader.api import loader_api
from app.api.v1.routes.author_to import author_to_api
from app.api.v1.routes.notes_to_api import note_to_api

api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")

api_v1.register_blueprint(loader_api, url_prefix="/loader")
api_v1.register_blueprint(author_to_api, url_prefix="/author")
api_v1.register_blueprint(note_to_api, url_prefix="/note")