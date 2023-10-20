# Sure Application
The goal of this app is to implement a pricing algorithm 
## How to run
1. Make sure you have docker installed
2. Build app `docker compose up -d --build` this hsould take a minute or so the first time you build
3. Seed the database with information about the pricing, this was given to us bythe prompt
    a. `docker compose exec web python app.py create_db`
4. You should be ready to go. To test that everything is running do a GET command to get the entries in the database we just added
    a. `http://127.0.0.1:5001/api/pricing_params/get_all`

## Run Test
1. To run tests do `pytest`

