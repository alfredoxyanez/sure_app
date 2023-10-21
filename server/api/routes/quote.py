import os
import json
from flask import Blueprint, request, jsonify, abort
from server.api.db import db
from server.database.models import PricingParams, Quote, State
from server.api.helpers import validate_quotes_data, calculate_pricing, validate_extra


quotes_blueprint = Blueprint("quote", __name__)


@quotes_blueprint.route("/", methods=["GET", "POST"])
def quote():
    """GET and POST methods for quote
    GET fetches Quote by id
    POST creates Quote with JSON as input

    Returns:
        Response with pricing calculation and quote id as JSON
    """
    if request.method == "GET":
        args = request.args
        quote = Quote.query.filter_by(id=args.get("id")).first_or_404()
        return jsonify(quote)
    if request.method == "POST":
        data = request.json
        valid, error = validate_quotes_data(data)
        if valid:
            state_pricing = PricingParams.query.filter_by(
                state=State[str(data["state"]).upper()]
            ).first_or_404()
            quote = Quote(
                firstname=data["firstname"],
                lastname=data["lastname"],
                state=data["state"],
                coverage_type=data["coverage_type"],
                extras=data["extras"],
            )
            db.session.add(quote)
            db.session.commit()
            pricing = calculate_pricing(quote, state_pricing)
            return jsonify(pricing), 201

        else:
            return f"Data formated incorrectly: {error}", 422


@quotes_blueprint.route("/price", methods=["GET"])
def get_quote_price():
    """GET function that calculates quote price for quote with id (parameter)

    Returns:
        Response
    """
    if request.method == "GET":
        args = request.args
        quote = Quote.query.filter_by(id=args.get("id")).first_or_404()
        state_pricing = PricingParams.query.filter_by(state=quote.state).first_or_404()
        pricing = calculate_pricing(quote, state_pricing)
        return jsonify(pricing)


@quotes_blueprint.route("/add_extra_or_update", methods=["POST"])
def add_extra():
    """POST function that adds or updates extra to existing quote

    Returns:
        Response
    """
    if request.method == "POST":
        args = request.args
        data = request.json
        quote = Quote.query.filter_by(id=args.get("id")).first_or_404()
        valid, err = validate_extra(data)
        # we create a dictionary of extra name to its iindex to easily update JSON
        extras = {extra["name"]: i for i, extra in enumerate(quote.extras)}
        if valid:
            # if we are updating an existing extra
            if data["name"] in extras:
                quote.extras[extras[data["name"]]] = data
                # new extra
            else:
                quote.extras.append(data)
            db.session.commit()
            return "Success", 200
        else:
            return f"Data formated incorrectly: {err}", 422
