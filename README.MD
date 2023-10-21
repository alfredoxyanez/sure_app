# Sure Application
The goal of this app is to implement a pricing algorithm given by the prompt
## How to run
1. Make sure you have [docker](https://docs.docker.com/engine/install/) installed
2. Build app `docker compose up -d --build` this should take a minute or so the first time you build
3. Seed the database with information about the pricing, this was given to us bythe prompt
    a. `docker compose exec web python app.py create_db`
4. You should be ready to go. To test that everything is running do a GET command (or go to that url on your browser) to get the entries in the database we just added
    - `http://127.0.0.1:5001/api/pricing_params/get_all`

## Run Tests
1. To run tests do `pytest` inside the `sure_app` folder should run 16 test (not exhustive)
2. you can also run individual test using the `pytest -k testname` command example: `pytest -k test_quote_1`
3. If you do not have pytest installed see  [this](https://docs.pytest.org/en/7.1.x/getting-started.html)

## Testing the price endpoint
To test the pricing endpoint you can do the following:
1. Create the quote by doing a POST call to the `http://127.0.0.1:5001/api/quote` with the quote data as JSON
example JSON (Test Case 1):
```
{
        "firstname": "Name",
        "lastname": "Lastname",
        "state": "california",
        "coverage_type": "basic",
        "extras": [{"name": "pet", "value": true}, {"name": "flood", "value": true}]
    }
```
The response should look like:
```
{
  "id": 1,
  "monthly_subtotal": 40.8,
  "monthly_tax": 0.4,
  "monthly_total": 41.2
}
```
You can also get the pricing for an existing quote using the quote id (for the example above)

GET `http://127.0.0.1:5001/api/quote/price?id=1` you should get the same output as above.

# Overview of the pricing_params endpoints

End Points    | Calls | Required Data/Params
------------- | ------------- | -----------
GET `api/pricing_params/`   | Fetches PricingParams by id parameter | id
POST `api/pricing_params/`  | Creates PricingParams with JSON as input | JSON: see test `test_creating_pricing_params` for example JSON
GET `api/pricing_params/get_all` | Fetches all PricingParams |
POST `api/pricing_params/add_or_update_coverage` | You can change the cost of both the basic and premium plans | JSON : `{"premium": 40}`
POST `api/pricing_params/add_or_update_extras` | you can chage or update an extra (example change the pet cost to 25 or add fire coverate) | JSON: `{"name": "fire", "type": "add", "value": 10}` if the value of name exist it will update the `type` and `value` if it does not it will add it to the list of possible extras a user has the option of picking

#  Comments on constraints given by prompt
1. [Q] We want to design this in a way that it will be easy to add more states. Eventually we want to add all 50 states, and want to make it easy to do so in the future.

    [A] To add another state we will have to update the enum in `/sure_app/server/database/models.py` to include the new state. I could have used a table to track states what we offer this service to (or check against the list of pricing param states)thus not requiring a new code deployment. I chose not to do this because I think the adding of a state should have a little more friction that just calling and endpoint to add said new state. Happy to talk about this further.

2. [Q] The pricing algorithm should be designed in a way to allows new variables to be easily added. For example, it should be easy to add in hurricane coverage.

    [A] The code currently allows us to do this using the `api/pricing_params/add_or_update_extras` endpoint. You can either modify existing extras or add a new one (see tests: `test_creating_pricing_params_add_or_update_extras_update` and `test_creating_pricing_params_add_or_update_extras_add` respectively)


3. [Q] The individual variables for the pricing algorithm should be easy to modify, ideally without changing or deploying new code. For example, updating flood coverage in New York from 10% to 20% should be a simple task.

    [A] See above, using the same endpoint you can modify the value for a already existing extra (see test: `test_creating_pricing_params_add_or_update_extras_update`)

4. [Q] Notable features ?

    [A] In the prompt the basic coverage, premium coverage, and pet coverage premium (extra) are constant for all states. The way I implemented the code it allows us to have different values per state (for example new york basic can cost $30 and premium $60) without any modifications needed and without the other state values changing. In the real world this most likely be the case because different states would have different costs.


# Requirements
- [x] We suggest Python 3 or later. [Python 3.9]
- [x] You may use any application frameworks or tools you’d like, though are not required to do so. If you choose to make use of specific tools, make sure to include any setup and usage instructions within your README that may be needed. [Taken care of by docker]
- [x]How you persist Quotes is up to you as long as they can be **stored** and **retrieved** for later usage i.e. pricing. [using postgres DB for "prod" using sqlite for testing]
- [x] Your solution should be appropriately unit tested and include any details on how to run automated tests. [test in the test dir]


# Directory Overview
1. `/server` is where to code for the api lives
    - `/server/routes` contains the routes code
    - `/server/database` contains the database models (I used mutable JSON to store the pricing params to more generalize the code and not have to migrate the database if we need to add a new param)
2. `/tests` contains the fixtures for running tests along with the tests themselves

3. `app.py` is the entry point into the flask API
4. `seed.json` contains the default prising parameters given by the prompt
5. `requirements.txt`contains library requirements
6. `.env` contains the enviroment variable(s)
7. `Dockerfile` instructions for docker regarding how to build the flask API container
8. `docker-compose.yaml` makes creating both the server and database container easy 
