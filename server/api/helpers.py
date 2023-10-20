import json
from flask_sqlalchemy import SQLAlchemy
from server.database.models import PricingParams, Quote, State, CoverageType


def db_seed(db: SQLAlchemy):
    """This helper function allows us to seed the database with state pricing based on the prompt

    Args:
        db (SQLAlchemy): takes in a databse instance as a parameter. This allows us to use it in
        testing via a fixture
    """
    pricing_params = PricingParams.query.all()
    pricing_params_states = [pricing.state.value for pricing in pricing_params]
    with open("seed.json") as json_file:
        seed_data = json.load(json_file)
        for pricing_param in seed_data:
            valid, error = validate_pricing_data(pricing_param)
            # here we check if the state already exists, if so we dont add the seed vals
            if valid and pricing_param["state"] not in pricing_params_states:
                new_pricing = PricingParams(
                    state=pricing_param["state"],
                    tax=pricing_param["tax"],
                    coverage_type_prices=pricing_param["coverage_type_prices"],
                    extras=pricing_param["extras"],
                )
                db.session.add(new_pricing)
        db.session.commit()


def validate_pricing_data(data) -> (bool, str):
    """This helper function allows us to validate the pricing data.
    It ensures:
    1. It's a valid state
    2. It has the valid coverage types (basic, premium) and the values are floats
    3. It validates the extras such as (dog, flood)
    4. It ensures the tax amount is a float

    Args:
        data (json): data needed to be validated

    Returns:
        bool: Returns True is data is valid else False
        str: If data is not valid, it returns the error str
    """
    # validate that the state name is in our enum
    states = [state.value for state in State]
    if data["state"] not in states:
        return False, "invalid state"
    # validate that we have base values for coverage types
    status, err = validate_coverage(data["coverage_type_prices"])
    if not status:
        return False, f"coverage_type_prices{err}"
    # validate extras
    status, err = validate_extras(data["extras"])
    if not status:
        return False, f"extras{err}"
    # validate tax info
    if not is_float(data["tax"]):
        return False, f"tax should be a float"

    return True, None


def validate_coverage(data) -> (bool, str):
    """Validates coverages, ensures that we have both basic and premium andthe values are floats

    Args:
        data (json): data needed to be validated

    Returns:
        bool: Returns True is data is valid else False
        str: If data is not valid, it returns the error str
    """
    coverage_types = set([coverage_type.value for coverage_type in CoverageType])
    if set(data.keys()) != coverage_types:
        return False, "[coverage_name]"
    for val in data.values():
        if not is_float(val):
            return False, "[value]"
    return True, None


def validate_extras(data) -> (bool, str):
    """Validates extras, ensures that:
    1. That we name, type and value are in the json
    2. ensures that the type is either add or multiply
    3. Ensures that the value is a float

    Args:
        data (json): data needed to be validated

    Returns:
        bool: Returns True is data is valid else False
        str: If data is not valid, it returns the error str
    """
    # validate extra types
    valid_extra_types = {"add", "multiply"}
    for extra in data:
        if "name" not in extra or "type" not in extra or "value" not in extra:
            return False, " key missing, ensure you have name, type, and value"
        if extra["type"] not in valid_extra_types:
            return False, "[type]"
        if not is_float(extra["value"]):
            return False, "[value]"
    return True, None


def validate_quotes_data(data) -> (bool, str):
    """Validates the json to ensure that:
    1. It has firstname, lastname, state and coverage_type
    2. Ensures that state is a valid state
    3. Ensures that coverage type a type that is supported (for now basic and premium)

    Args:
        data (json): data needed to be validated

    Returns:
        bool: Returns True is data is valid else False
        str: If data is not valid, it returns the error str
    """
    if (
        "firstname" not in data
        or "lastname" not in data
        or "state" not in data
        or "coverage_type" not in data
    ):
        return False, "missing quote key"
    states = [state.value for state in State]
    if data["state"] not in states:
        return False, "invalid state"
    coverage_types = set([coverage_type.value for coverage_type in CoverageType])
    if data["coverage_type"] not in coverage_types:
        return False, "invalid coverage_type"
    return True, None


def calculate_pricing(quote: Quote, pricing_params: PricingParams) -> dict:
    """This Helper function takes a quote and calculates the cost based on the params.
    It calculates the cost based on all the extras in the pricing params (not just the dog and the flood additive)
    It ensures that the extras in the quote are valid extras.
    This performs all additive operations first, then the multiplier ones (i.e: dog first then flood)

    Args:
        quote (Quote): The quote we want to calculate the cost for
        pricing_params (PricingParams): The pricing params we want to use to calculate the pricing

    Returns:
        dict: With pricing (id, monthly_subtotal, monthly_tax ,monthly_total)
    """
    # Get the base pricing (basic or premium)
    amount = pricing_params.coverage_type_prices[quote.coverage_type]

    # Get the possible additive extras based on the pricing params
    additive_names = [
        extra["name"] for extra in pricing_params.extras if extra["type"] == "add"
    ]
    # Get the possible multiplier extras based on the pricing params
    mul_names = [
        extra["name"] for extra in pricing_params.extras if extra["type"] == "multiply"
    ]
    # list of multipliers that will happen at the end, thsi is because we should do
    # all additive extras first
    quote_multipliers = []
    # create a dictinary to easily retrieve the value of the extra
    extra_name_to_value = {
        extra["name"]: extra["value"] for extra in pricing_params.extras
    }

    # we look through all the quote extras
    # we ensure that they are valid ones (i.e in the pricing params) and True
    for extra in quote.extras:
        # if they are additive we simply add the value
        if extra["name"] in additive_names and extra["value"]:
            amount += extra_name_to_value[extra["name"]]
        # if they are multipliers we add to the multipier list to do at the end
        if extra["name"] in mul_names and extra["value"]:
            quote_multipliers.append(extra_name_to_value[extra["name"]])
    # we take care of the multipliers
    for val in quote_multipliers:
        amount *= 1 + val
    # result
    result = {
        "id": quote.id,
        "monthly_subtotal": format_float(amount),
        "monthly_tax": format_float(amount * pricing_params.tax),
        "monthly_total": format_float(amount * (1 + pricing_params.tax)),
    }
    return result


def format_float(float_val, digits=2) -> float:
    """This helper is needed so that we can truncate floats to two decimal places. We dont want to use
    the round method because based on the example Quote 1, the monthly taxes are $0.408 which
    rounds to $0.41 and the solution says it should be $0.40 therefore truncating not rounding

    Args:
        float_val (float): Float we want to perform this operation on
        digits (int, optional): Determines the number of numbers after the decimal. Defaults to 2.

    Returns:
        float: floast truncated after 2 decimal places
    """
    fnum = str(float_val)
    return float(fnum[: fnum.find(".") + digits + 1])


def is_float(string) -> bool:
    """This checks if a value can be casted to a float, this is used for validation

    Args:
        string (value): that might be casted to float

    Returns:
        bool: Returns True if the value can be casted to a float, False otherwise
    """
    try:
        float(string)
        return True
    except ValueError:
        return False
