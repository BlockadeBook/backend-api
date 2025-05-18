from flask import Blueprint

author_to_api = Blueprint("author_to_api", __name__)


@author_to_api.route('/greet', methods=['GET'])
def greeting():
    return "Hi!"
