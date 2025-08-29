from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import sys
import os
from src.scraper import scraper
from src import test
# from util.traffic import (
#     rate_limiter,
# )
# from typing.errors import (
#     RequestError
# )
# from typing.structs import (
#     Result
# )

# Add parent directory to path so we can import our golf modules
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # Import our golf API modules
# try:
#     from v2_api import get_chronogolf_teetimes
#     from foreup import get_foreup_teetimes, parse_foreup_teetimes
#     from eaglewood import get_eaglewood_teetimes, parse_eaglewood_teetimes
#     from stonebridge import get_stonebridge_teetimes, parse_stonebridge_teetimes
#     from stonebridge_auth import get_bearer_token
# except ImportError as e:
# print(f"Warning: Could not import golf modules: {e}")

app = Flask(__name__)

# Configuration
# app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]
app.config['DEBUG'] = True


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
    print(tee_times[0])
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
    print(response)
    return response
