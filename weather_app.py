import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

API_TOKEN = ""
API_KEY = ""

app = Flask(__name__)


def get_weather(location: str, date: str):
    url = "http://api.weatherapi.com/v1/history.json"
    
    parameters = {
        "key":API_KEY,
        "q":location,
        "dt":date
    }

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload, params=parameters)
    return json.loads(response.text)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA HW1: Python Saas.</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["POST"],
)
def weather_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    location = ""
    if json_data.get("location"):
        location = json_data.get("location")
    
    date = ""
    if json_data.get("date"):
        date = json_data.get("date")

    weather = get_weather(location, date)

    end_dt = dt.datetime.now()

    result = {
        "event_start_datetime": start_dt.isoformat(),
        "event_finished_datetime": end_dt.isoformat(),
        "event_duration": str(end_dt - start_dt),
        "weather": weather,
    }

    return result
