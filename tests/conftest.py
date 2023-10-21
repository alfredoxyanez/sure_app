import pytest
import json
from server.database.models import PricingParams
from server.api.index import create_app
from server.api.db import db
from server.api.helpers import db_seed


@pytest.fixture()
def basic_app():
    """This fixture is used for testing and it creates the app, the database"""
    basic_app = create_app("sqlite://")
    with basic_app.app_context():
        db.create_all()
    yield basic_app


@pytest.fixture()
def basic_client(basic_app):
    """Creates a test client used for testing requiring the basic app"""
    return basic_app.test_client()


@pytest.fixture()
def app():
    """This fixture is used for testing and it creates the app, the database and seeds it"""
    app = create_app("sqlite://")
    with app.app_context():
        db.create_all()
        db_seed(db)
    yield app


@pytest.fixture()
def client(app):
    """Creates a test client used for testing requiring the app that has been seeded"""
    return app.test_client()
