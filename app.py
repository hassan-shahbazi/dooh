from flask import Flask, render_template, jsonify, request
import requests
import os
import json
from db_manager import DatabaseManager

# Statics
app = Flask(__name__)
db = DatabaseManager()

# Helper functions
def null_parameter():
    return jsonify({ "error": "parameters cannot be null" }), 400
def check_country(code):
    return 1 <= int(code) <= 3
def invalid_country_code():
    return jsonify({ "error": "country code is not valid"}), 400
def check_screen(type):
    return type in ["billboard", "standing", "small"]
def invalid_screen_type():
    return jsonify({ "error": "screen type is not valid"}), 400

# login to the system
@app.route("/login", methods=['POST'])
def login():
    username = request.args.get("username", default = None)
    password = request.args.get("password", default = None)
    country = request.args.get("country_code", default = 1)

    if username is None or password is None:
        return null_parameter()
    if not check_country(country):
        return invalid_country_code()
    return db.get_agency(username, password, country)

# signup a new agency
@app.route("/sign_up", methods=['POST'])
def signup():
    username = request.args.get("username", default = None)
    password = request.args.get("password", default = None)
    country = request.args.get("country_code", default = 1)

    if username is None or password is None:
        return null_parameter()
    if not check_country(country):
        return invalid_country_code()
    db.update_agency(username, password, country)
    return ('', 200)

# make a new order
@app.route("/new_order", methods=['POST'])
def new_order():
    screen_id = request.args.get("screen_id", default = None)
    country = request.args.get("country_code", default = None)
    duration = request.args.get("duration", default = 0)
    repeat = request.args.get("number_of_repeat", default = 0)
    price = request.args.get("price", default = 0)
    agency_id = request.args.get("agency_id", default = None)
    screen_type = request.args.get("screen_type", default = "standing")
    city_id = request.args.get("city_id", default = None)

    if screen_id is None or country is None or agency_id is None or city_id is None:
        return null_parameter()
    if not check_screen(screen_type):
        return invalid_screen_type()
    if not check_country(country):
        return invalid_country_code()
    db.make_order(screen_id, agency_id, duration, repeat, price, country, screen_type, city_id)
    return ('', 200) 

# get all screens depending on the passed paramters
@app.route("/screens", methods=['GET'])
def screens():
    city = request.args.get("city_id", default = None)
    country = request.args.get("country_code", default = None)
    screen_type = request.args.get("screen_type", default = None)

    if city is not None and country is None and screen_type is None:
        return db.get_screens(city)
    if city is None and country is not None and screen_type is None:
        if not check_country(country):
            return invalid_country_code()
        return db.get_screens_by_country(country)
    if city is None and country is not None and screen_type is not None:
        if not check_screen(screen_type):
            return invalid_screen_type()
        if not check_country(country):
            return invalid_country_code()
        return db.get_screens_by_type(country, screen_type)
    return db.get_screens_list() # all paramters are null

# get all cities
@app.route("/cities", methods=['GET'])
def cities():
    return db.get_city_list()

@app.route("/orders", methods=['GET'])
def orders():
    agency = request.args.get("agency_id", default = None)
    city = request.args.get("city_id", default = None)
    country = request.args.get("country_code", default = None)

    if agency is None:
        return null_parameter()
    if country is None and city is not None:
        return db.get_orders_by_agency(agency, city)
    if country is not None and city is None:
        return db.get_orders_by_agency_country(agency, country)
    return null_parameter() # both city and country cannot be null

# run the application
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
