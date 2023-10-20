import pytest
import json
from server.database.models import PricingParams
from server.api.index import create_app
from server.api.db import db
from server.api.helpers import db_seed


@pytest.fixture()
def app():
    """This fixture is used for testing and it creates tghe app, the database and seeds it"""
    app = create_app("sqlite://")
    with app.app_context():
        db.create_all()
        db_seed(db)
    yield app


@pytest.fixture()
def client(app):
    """Creates a test client used for testing"""
    return app.test_client()
