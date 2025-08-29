from flask import Flask, Response, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import sys
import os

from src.scraper import scraper
from src import test

app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})
CORS(app, origins="*")
# Configuration
# app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]
app.config['DEBUG'] = True


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint for deployment monitoring"""
    return jsonify({"status": "healthy", "message": "Utah Golf Booking API is running"})


@app.route('/api/eaglewood_teetimes', methods=['GET'])
def get_eaglewood_tee_times():
    date = "2025-09-01"
    tee_times = scraper.eaglewood_tee_times(date)
    # print(tee_times[0])
    data_to_return = [tee_time.model_dump() for tee_time in tee_times]

    # Step 3: Use Flask's jsonify to create a proper JSON response
    # jsonify handles setting the correct Content-Type header (application/json)
    return jsonify(data_to_return)


@app.route('/api/foreup_teetimes', methods=['GET'])
def get_foreup_tee_times():
    date = "2025-09-01"
    tee_times = scraper.foreup_tee_times(date)
    # print(tee_times[0])
    data_to_return = [tee_time.model_dump() for tee_time in tee_times]

    # Step 3: Use Flask's jsonify to create a proper JSON response
    # jsonify handles setting the correct Content-Type header (application/json)
    return jsonify(data_to_return)


# @log_request
# @rate_limiter
@app.route('/api/teetimes', methods=['GET'])
def get_all_tee_times():
    date = "2025-09-01"
    tee_times = scraper.chronogolf_tee_times(date)
    # print(tee_times[0])
    data_to_return = [tee_time.model_dump() for tee_time in tee_times]

    return jsonify(data_to_return)


@app.route('/test_api/teetimes', methods=['GET'])
def test_get_all_tee_times():
    """
    This endpoint fetches a list of TeeTime objects and returns them as a JSON array.
    """

    tee_times_list = test.get_mock_tee_times()

    data_to_return = [tee_time.model_dump() for tee_time in tee_times_list]
    response = jsonify(data_to_return)

    return response
