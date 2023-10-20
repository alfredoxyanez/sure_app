import os
import json
from flask import Blueprint, request, jsonify, abort
from server.api.db import db
from server.database.models import PricingParams, Quote, State
from server.api.helpers import validate_quotes_data, calculate_pricing


quotes_blueprint = Blueprint("quote", __name__)


@quotes_blueprint.route("/", methods=["GET", "POST"])
def quote():
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
            return jsonify(pricing)

        else:
            return f"Data formated incorrectly: {error}", 422


@quotes_blueprint.route("/price", methods=["GET"])
def get_quote_price():
    if request.method == "GET":
        args = request.args
        quote = Quote.query.filter_by(id=args.get("id")).first_or_404()
        state_pricing = PricingParams.query.filter_by(state=quote.state).first_or_404()
        pricing = calculate_pricing(quote, state_pricing)
        return jsonify(pricing)
