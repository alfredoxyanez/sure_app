import json
from server.database.models import PricingParams, Quote


def test_quote_1(client, app):
    input_json = {
        "firstname": "Name",
        "lastname": "Lastname",
        "state": "california",
        "coverage_type": "basic",
        "extras": [{"name": "pet", "value": True}, {"name": "flood", "value": True}],
    }
    # input_json = json.dumps(input_json)
    response = client.post("/api/quote/", json=input_json)
    with app.app_context():
        assert response.json["monthly_subtotal"] == 40.80
        assert response.json["monthly_tax"] == 0.40
        assert response.json["monthly_total"] == 41.20


def test_quote_2(client, app):
    input_json = {
        "firstname": "Name",
        "lastname": "Lastname",
        "state": "california",
        "coverage_type": "premium",
        "extras": [{"name": "pet", "value": True}, {"name": "flood", "value": True}],
    }
    # input_json = json.dumps(input_json)
    response = client.post("/api/quote/", json=input_json)
    with app.app_context():
        assert response.json["monthly_subtotal"] == 61.20
        assert response.json["monthly_tax"] == 0.61
        assert response.json["monthly_total"] == 61.81


def test_quote_3(client, app):
    input_json = {
        "firstname": "Name",
        "lastname": "Lastname",
        "state": "new_york",
        "coverage_type": "premium",
        "extras": [{"name": "pet", "value": True}, {"name": "flood", "value": False}],
    }
    # input_json = json.dumps(input_json)
    response = client.post("/api/quote/", json=input_json)
    with app.app_context():
        assert response.json["monthly_subtotal"] == 60.00
        assert response.json["monthly_tax"] == 1.20
        assert response.json["monthly_total"] == 61.20


def test_quote_4(client, app):
    input_json = {
        "firstname": "Name",
        "lastname": "Lastname",
        "state": "texas",
        "coverage_type": "basic",
        "extras": [{"name": "pet", "value": False}, {"name": "flood", "value": True}],
    }
    # input_json = json.dumps(input_json)
    response = client.post("/api/quote/", json=input_json)
    with app.app_context():
        assert response.json["monthly_subtotal"] == 30.00
        assert response.json["monthly_tax"] == 0.15
        assert response.json["monthly_total"] == 30.15
