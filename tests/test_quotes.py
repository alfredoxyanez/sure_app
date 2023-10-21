import json
from server.database.models import PricingParams, Quote


def test_quote_1(client, app):
    """test case 1 used for validation"""
    input_json = {
        "firstname": "Name",
        "lastname": "Lastname",
        "state": "california",
        "coverage_type": "basic",
        "extras": [{"name": "pet", "value": True}, {"name": "flood", "value": True}],
    }
    # input_json = json.dumps(input_json)
    response = client.post("/api/quote/", json=input_json)
    assert response.status_code == 201
    with app.app_context():
        assert response.json["monthly_subtotal"] == 40.80
        assert response.json["monthly_tax"] == 0.40
        assert response.json["monthly_total"] == 41.20


def test_quote_2(client, app):
    """test case 2 used for validation"""
    input_json = {
        "firstname": "Name",
        "lastname": "Lastname",
        "state": "california",
        "coverage_type": "premium",
        "extras": [{"name": "pet", "value": True}, {"name": "flood", "value": True}],
    }
    # input_json = json.dumps(input_json)
    response = client.post("/api/quote/", json=input_json)
    assert response.status_code == 201
    with app.app_context():
        assert response.json["monthly_subtotal"] == 61.20
        assert response.json["monthly_tax"] == 0.61
        assert response.json["monthly_total"] == 61.81


def test_quote_3(client, app):
    """test case 3 used for validation"""
    input_json = {
        "firstname": "Name",
        "lastname": "Lastname",
        "state": "new_york",
        "coverage_type": "premium",
        "extras": [{"name": "pet", "value": True}, {"name": "flood", "value": False}],
    }
    # input_json = json.dumps(input_json)
    response = client.post("/api/quote/", json=input_json)
    assert response.status_code == 201
    with app.app_context():
        assert response.json["monthly_subtotal"] == 60.00
        assert response.json["monthly_tax"] == 1.20
        assert response.json["monthly_total"] == 61.20


def test_quote_4(client, app):
    """test case 4 used for validation"""
    input_json = {
        "firstname": "Name",
        "lastname": "Lastname",
        "state": "texas",
        "coverage_type": "basic",
        "extras": [{"name": "pet", "value": False}, {"name": "flood", "value": True}],
    }
    # input_json = json.dumps(input_json)
    response = client.post("/api/quote/", json=input_json)
    assert response.status_code == 201
    with app.app_context():
        assert response.json["monthly_subtotal"] == 30.00
        assert response.json["monthly_tax"] == 0.15
        assert response.json["monthly_total"] == 30.15


def test_quote_5(client, app):
    """test case with a maxed out new york quote"""
    input_json = {
        "firstname": "Name",
        "lastname": "Lastname",
        "state": "new_york",
        "coverage_type": "premium",
        "extras": [{"name": "pet", "value": True}, {"name": "flood", "value": True}],
    }
    # input_json = json.dumps(input_json)
    response = client.post("/api/quote/", json=input_json)
    assert response.status_code == 201
    with app.app_context():
        assert response.json["monthly_subtotal"] == 66.0
        assert response.json["monthly_tax"] == 1.32
        assert response.json["monthly_total"] == 67.32


def test_quote_6(client, app):
    """test case with a maxed out texas quote"""
    input_json = {
        "firstname": "Name",
        "lastname": "Lastname",
        "state": "texas",
        "coverage_type": "premium",
        "extras": [{"name": "pet", "value": True}, {"name": "flood", "value": True}],
    }
    # input_json = json.dumps(input_json)
    response = client.post("/api/quote/", json=input_json)
    assert response.status_code == 201
    with app.app_context():
        assert response.json["monthly_subtotal"] == 90.0
        assert response.json["monthly_tax"] == 0.45
        assert response.json["monthly_total"] == 90.45


def test_quote_after_adding_extra(client, app):
    """test case with a maxed out texas quote and adding the extra fire"""
    input_json = {
        "firstname": "Name",
        "lastname": "Lastname",
        "state": "texas",
        "coverage_type": "premium",
        "extras": [{"name": "pet", "value": True}, {"name": "flood", "value": True}],
    }
    # input_json = json.dumps(input_json)
    response = client.post("/api/quote/", json=input_json)
    assert response.status_code == 201
    with app.app_context():
        assert response.json["monthly_subtotal"] == 90.0
        assert response.json["monthly_tax"] == 0.45
        assert response.json["monthly_total"] == 90.45
    # Add new extra to state pricing params
    new_extra = {"name": "fire", "type": "add", "value": 10}
    add_response = client.post(
        f'/api/pricing_params/add_or_update_extras?state={input_json["state"]}',
        json=new_extra,
    )
    assert add_response.status_code == 200
    # check to see if the previous quote price changes based on the fact that we add the new extra
    new_extra = {"name": "fire", "value": True}
    response_new_extra = client.post(
        f'/api/quote/add_extra?id={response.json["id"]}', json=new_extra
    )

    assert response_new_extra.status_code == 200
    updated_quote_price = client.get(f'/api/quote/price?id={response.json["id"]}')

    # here we check that the price being calculated is done so with the new fire extra in place
    # Premium (40) + Pet (20) + Fire (10) + Flood (50%) = 105
    assert updated_quote_price.json["monthly_subtotal"] == 105.0
    assert updated_quote_price.json["monthly_tax"] == 0.52
    assert updated_quote_price.json["monthly_total"] == 105.52
