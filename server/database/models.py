import enum
import json
from datetime import datetime
from dataclasses import dataclass
from sqlalchemy import Enum, Integer, String, Float, DateTime
from sqlalchemy_json import NestedMutableJson
from server.api.db import db


class State(str, enum.Enum):
    """State Enum
    ***NOTE*** I'm happy to talk the trade offs of why this is an enum and not another database table or
    something that would not require a deployment to add more of
    """

    CALIFORNIA = "california"
    NEW_YORK = "new_york"
    TEXAS = "texas"


class CoverageType(str, enum.Enum):
    """CoverageType Enum"""

    BASIC = "basic"
    PREMIUM = "premium"


@dataclass
class Quote(db.Model):
    """The Quote table has needed columns including the extras column that is used to calculate price"""

    id: int = db.Column(Integer, primary_key=True)
    created_at: datetime = db.Column(DateTime(), default=datetime.utcnow)
    firstname: str = db.Column(String)
    lastname: str = db.Column(String)
    state: State = db.Column(Enum(State))
    coverage_type: CoverageType = db.Column(Enum(CoverageType))
    extras: json = db.Column(NestedMutableJson)


@dataclass
class PricingParams(db.Model):
    """The PricingParams table that are "static values that are used to calculate the price for a particular quote" """

    id: int = db.Column(Integer, primary_key=True)
    created_at: datetime = db.Column(DateTime(), default=datetime.utcnow)
    state: State = db.Column(Enum(State), unique=True)
    tax: float = db.Column(Float)
    coverage_type_prices: json = db.Column(NestedMutableJson)
    extras: json = db.Column(NestedMutableJson)
