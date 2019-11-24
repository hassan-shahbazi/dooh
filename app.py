from flask import Flask, render_template, jsonify, request
import requests
import os
import json

# Statics
app = Flask(__name__)
API_KEY = "68590775e423441297d3af35eaaefc1f"

# Helper functions
def get_null_parameter():
    return jsonify({ "error": "parameters cannot be null" }), 400

def get_location_name(latitude, longitude):
    req = requests.get("https://api.opencagedata.com/geocode/v1/json?key=" + API_KEY + "&q=" + latitude  + "%2C" + longitude)
    resp = req.json()

    return jsonify({ "country": resp["results"][0]["components"]["country"]})

# Getting country from latitude and longitude
@app.route("/get_location", methods=['GET'])
def mock_route():
    latitude = request.args.get("lat", default = None)
    longitude = request.args.get("long", default = None)

    if latitude is None or longitude is None:
        return get_null_parameter()
    return get_location_name(latitude, longitude)

# Getting ads according to the country's name
@app.route("/get_ads", methods=['GET'])
def get_ads():
    country = request.args.get("country", default = None)

    if country is None:
        return get_null_parameter()
    return jsonify({ "results": ["ad_1", "ad_2"] })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
