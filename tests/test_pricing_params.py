import json
from server.database.models import PricingParams, Quote, State


def test_creating_pricing_params(basic_client, basic_app):
    """test the basic app fixture to ensure we can create a PricingParams"""
    input_json = {
        "state": "california",
        "tax": 0.01,
        "coverage_type_prices": {"basic": 20, "premium": 40},
        "extras": [
            {"name": "pet", "type": "add", "value": 20},
            {"name": "flood", "type": "multiply", "value": 0.02},
        ],
    }
    response = basic_client.post("/api/pricing_params/", json=input_json)
    assert response.status_code == 201
    with basic_app.app_context():
        count = PricingParams.query.count()
        assert count == 1


def test_creating_pricing_params_1(basic_client, basic_app):
    """test that we get an error when trying to create a PricingParams without the basic coverage type"""
    input_json = {
        "state": "california",
        "tax": 0.01,
        "coverage_type_prices": {"premium": 40},
        "extras": [
            {"name": "pet", "type": "add", "value": 20},
            {"name": "flood", "type": "multiply", "value": 0.02},
        ],
    }
    response = basic_client.post("/api/pricing_params/", json=input_json)

    assert response.status_code == 422
    assert "coverage_type_prices[coverage_name]" in response.text


def test_creating_pricing_params_2(basic_client, basic_app):
    """test that we get an error when trying to create a PricingParams with a state that is not allowed"""
    input_json = {
        "state": "nevada",
        "tax": 0.01,
        "coverage_type_prices": {"basic": 20, "premium": 40},
        "extras": [
            {"name": "pet", "type": "add", "value": 20},
            {"name": "flood", "type": "multiply", "value": 0.02},
        ],
    }
    response = basic_client.post("/api/pricing_params/", json=input_json)
    assert response.status_code == 422
    assert "invalid state" in response.text


def test_creating_pricing_params_3(basic_client, basic_app):
    """test that we get an error when trying to create a PricingParams where the extra is not add or multiply"""
    input_json = {
        "state": "california",
        "tax": 0.01,
        "coverage_type_prices": {"basic": 20, "premium": 40},
        "extras": [
            {"name": "pet", "type": "subtract", "value": 20},
            {"name": "flood", "type": "multiply", "value": 0.02},
        ],
    }
    response = basic_client.post("/api/pricing_params/", json=input_json)
    assert response.status_code == 422
    assert "extras[type]" in response.text


def test_creating_pricing_params_4(basic_client, basic_app):
    """test that we get an error when trying to create a PricingParams where the cost of the basic
    plan cannot be parsed to a float
    """
    input_json = {
        "state": "california",
        "tax": 0.01,
        "coverage_type_prices": {"basic": "abc", "premium": 40},
        "extras": [
            {"name": "pet", "type": "add", "value": 20},
            {"name": "flood", "type": "multiply", "value": 0.02},
        ],
    }
    response = basic_client.post("/api/pricing_params/", json=input_json)
    assert response.status_code == 422
    assert "coverage_type_prices[value]" in response.text


def test_creating_pricing_params_get_all(client, app):
    """test the /api/pricing_params/get_all method"""
    response = client.get("/api/pricing_params/get_all")
    assert response.status_code == 200
    resp_json = json.loads(response.text)
    assert len(resp_json) == 3


def test_creating_pricing_params_add_or_update_coverage(basic_client, basic_app):
    """test the /api/pricing_params/add_or_update_coverage method"""
    input_json = {
        "state": "california",
        "tax": 0.01,
        "coverage_type_prices": {"basic": 20, "premium": 40},
        "extras": [
            {"name": "flood", "type": "multiply", "value": 0.02},
        ],
    }
    # first we add the PricingParam
    response = basic_client.post("/api/pricing_params/", json=input_json)
    assert response.status_code == 201
    # here we update the premium cost to 45
    update_coverage = {"premium": 45}
    response = basic_client.post(
        f'/api/pricing_params/add_or_update_coverage?state={input_json["state"]}',
        json=update_coverage,
    )
    assert response.status_code == 200
    # check to see if the price in the DB is the updated price (45)
    with basic_app.app_context():
        pricing_param = PricingParams.query.filter_by(
            state=State[str(input_json["state"]).upper()]
        ).first()
        assert (
            pricing_param.coverage_type_prices["premium"] == update_coverage["premium"]
        )


def test_creating_pricing_params_add_or_update_extras_add(basic_client, basic_app):
    """test the /api/pricing_params/add_or_update_extras method by adding"""
    input_json = {
        "state": "california",
        "tax": 0.01,
        "coverage_type_prices": {"basic": 20, "premium": 40},
        "extras": [
            {"name": "flood", "type": "multiply", "value": 0.02},
        ],
    }
    # first we add the PricingParam
    response = basic_client.post("/api/pricing_params/", json=input_json)
    assert response.status_code == 201
    # here we add a new extra
    new_extra = {"name": "pet", "type": "add", "value": 20}
    response = basic_client.post(
        f'/api/pricing_params/add_or_update_extras?state={input_json["state"]}',
        json=new_extra,
    )
    assert response.status_code == 200
    # check to see the new extra is in the DB
    with basic_app.app_context():
        pricing_param = PricingParams.query.filter_by(
            state=State[str(input_json["state"]).upper()]
        ).first()
        assert len(pricing_param.extras) == 2


def test_creating_pricing_params_add_or_update_extras_update(basic_client, basic_app):
    """test the /api/pricing_params/add_or_update_extras method by updating"""
    input_json = {
        "state": "california",
        "tax": 0.01,
        "coverage_type_prices": {"basic": 20, "premium": 40},
        "extras": [
            {"name": "flood", "type": "multiply", "value": 0.02},
        ],
    }
    # first we add the PricingParam
    response = basic_client.post("/api/pricing_params/", json=input_json)
    assert response.status_code == 201
    # here we update the existing extra
    new_extra = {"name": "flood", "type": "add", "value": 20}
    response = basic_client.post(
        f'/api/pricing_params/add_or_update_extras?state={input_json["state"]}',
        json=new_extra,
    )
    assert response.status_code == 200
    # check to see the updated extra is in the DB
    with basic_app.app_context():
        pricing_param = PricingParams.query.filter_by(
            state=State[str(input_json["state"]).upper()]
        ).first()
        assert len(pricing_param.extras) == 1
        assert pricing_param.extras[0]["name"] == new_extra["name"]
        assert pricing_param.extras[0]["type"] == new_extra["type"]
        assert pricing_param.extras[0]["value"] == new_extra["value"]
