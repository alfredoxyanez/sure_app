import pytest
import json
from server.database.models import PricingParams
from server.api.index import create_app
from server.api.db import db
from server.api.helpers import db_seed


@pytest.fixture()
def app():
    app = create_app("sqlite://")
    with app.app_context():
        db.create_all()
        db_seed(db)

    print("CREATING DB")
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
