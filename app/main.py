from flask import Flask
from app.api.v1 import api_v1
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")
    app.register_blueprint(api_v1)
    return app

if __name__ == '__main__':
    create_app().run(debug=True, port=5000)
