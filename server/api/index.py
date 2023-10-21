from dotenv import load_dotenv

load_dotenv()
import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask.json.provider import DefaultJSONProvider

from server.api.db import db
from server.api.routes.pricing_params import pricing_params_blueprint
from server.api.routes.quote import quotes_blueprint


def create_app(database_uri=None):
    """This created the main app and to create the app for testing

    Args:
        database_uri (str, optional): Database URI, this is used in our app and also to test. Defaults to None.

    Returns:
        app(Flask):  the app
    """
    app = Flask(__name__)
    uri = database_uri if database_uri else os.environ["SQLALCHEMY_DATABASE_URI"]
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    # Adds CORS
    cors = CORS(app)
    # Attaches DB to app
    db.init_app(app)
    # Add blueprints
    app.register_blueprint(pricing_params_blueprint, url_prefix="/api/pricing_params")
    app.register_blueprint(quotes_blueprint, url_prefix="/api/quote")
    return app
