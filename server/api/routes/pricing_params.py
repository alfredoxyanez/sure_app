import os
import json
from flask import Blueprint, request, jsonify, abort
from server.api.db import db
from server.database.models import PricingParams, State
from server.api.helpers import validate_pricing_data, validate_extras

pricing_params_blueprint = Blueprint("pricing_params", __name__)


@pricing_params_blueprint.route("/", methods=["GET", "POST"])
def pricing():
    if request.method == "GET":
        args = request.args
        pricing = PricingParams.query.filter_by(id=args.get("id")).first_or_404()
        return jsonify(pricing)

    if request.method == "POST":
        data = request.json
        valid, error = validate_pricing_data(data)
        if valid:
            new_pricing = PricingParams(
                state=data["state"],
                tax=data["tax"],
                coverage_type_prices=data["coverage_type_prices"],
                extras=data["extras"],
            )
            db.session.add(new_pricing)
            db.session.commit()
            return "Success", 201
        else:
            return f"Data formated incorrectly: {error}", 422


@pricing_params_blueprint.route("/get_all", methods=["GET"])
def get_all_pricing():
    if request.method == "GET":
        pricings = PricingParams.query.all()
        return jsonify(pricings)


@pricing_params_blueprint.route("/add_or_update_coverage", methods=["POST"])
def add_or_update_coverage():
    if request.method == "POST":
        args = request.args
        pricing = PricingParams.query.filter_by(
            state=State[str(request.args.get("state")).upper()]
        ).first_or_404()
        data = request.json
        for k, v in data.items():
            if k in pricing.coverage_type_prices:
                pricing.coverage_type_prices[k] = v
        db.session.commit()
        return "Success", 200


@pricing_params_blueprint.route("/add_or_update_extras", methods=["POST"])
def add_or_update_extras():
    if request.method == "POST":
        args = request.args
        pricing = PricingParams.query.filter_by(
            state=State[str(request.args.get("state")).upper()]
        ).first_or_404()
        data = request.json
        valid, err = validate_extras([data])
        extras = [extra["name"] for extra in pricing.extras]
        print(extras)
        if valid:
            if data["name"] in extras:
                for extra in pricing.extras:
                    if data["name"] == extra["name"]:
                        if "type" in data:
                            extra["type"] = data["type"]
                        if "value" in data:
                            extra["value"] = data["value"]
                        break
            else:
                pricing.extras.append(data)
            db.session.commit()
            return "Success", 200

        else:
            return f"Data formated incorrectly: {err}", 422
