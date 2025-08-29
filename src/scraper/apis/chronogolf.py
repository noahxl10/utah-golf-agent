import requests
import os
import json
import subprocess
from pydantic import ValidationError

from src.config import courses as CONFIG
from typing import Optional, Generic, TypeVar, Union, List, Dict, Any
from src._typing.structs import (
    TeeTime, 
    TeeTimeParameter,
    Course,
)
from src.misc import request_builder


class CourseAPI:

    def __init__(self, course: Course):
        self.course = course
        self.course_config = CONFIG[self.course.name]
        self.sub_config = self.course_config["config"]
        print(self.course_config)
        print(self.sub_config)
        self.endpoint = os.environ[self.sub_config["endpoint_env_var"]]


class V1(CourseAPI):

    def __init__(self, course: Course):
        super().__init__(course)

    # def convert_start_time_to

    def get_tee_time_from_response(self, r):
        """
            r: response_tee_time
        """

        # Extract pricing information
        is_available = False
        green_fees = r.get('green_fees', [])
        fee_info = {}
        if green_fees:
            is_available = True
            fee_info = green_fees[0]  # Take first fee option

        return TeeTime(
            start_time = r.get('start_time'),
            date = r.get('date'),
            course_name = self.course.name,
            holes = [18], # r.get('hole')
            restrictions = r.get('restrictions'),
            provider = self.course_config.get("provider", ""),
            booking_url = self.course.booking_url,
            is_available = is_available,
            green_fee = fee_info.get('green_fee', 0),
            price = fee_info.get('price', 0),
            half_cart = fee_info.get('half_cart_price', 0),
            subtotal = fee_info.get('subtotal', 0)
        )

    def _hit_endpoint_with_requests(self, tee_time_parameter: TeeTimeParameter):

        response = requests.get(
            tee_time_parameter.endpoint,
            headers = tee_time_parameter.headers
        )

        response.raise_for_status()

        data = response.json()

        # Parse the JSON data (assuming it's tee time data)
        if isinstance(data, list):
            tee_times = data
        else:
            tee_times = data.get('data', data)  # Handle different response formats

        return data

    def _hit_endpoint_with_curl(self, tee_time_parameter: TeeTimeParameter):
        cmd = request_builder.cg_v1(tee_time_parameter)

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        data = json.loads(result.stdout)
        return data

    def get_tee_times(self, tee_time_parameter: TeeTimeParameter) -> List[TeeTime]: #  
        tee_times = []

        response = self._hit_endpoint_with_curl(tee_time_parameter)
        for resp_tee_time in response:
            tee_times.append(self.get_tee_time_from_response(resp_tee_time))

        return tee_times


class V2(CourseAPI):

    def __init__(self, course: Course):
        super().__init__(course)

    def get_tee_time_from_response(self, r):
        """
            r: response_tee_time
        """

        # Extract pricing information
        response_data = r
        if not response_data:
            return None

        # Extract nested data safely to avoid KeyErrors
        course_info = response_data.get("course", {})
        price_info = response_data.get("default_price", {})

        # --- Field Mapping ---

        # Create a list of restrictions based on available data
        restrictions = []
        min_players = response_data.get("min_player_size")
        if min_players and min_players > 1:
            restrictions.append(f"Minimum {min_players} players required.")

        # The API indicates availability by having a max_player_size > 0
        is_available = response_data.get("max_player_size", 0) > 0

        # Construct the data dictionary for Pydantic validation
        tee_time_data = {
            "start_time": response_data.get("starts_at"),  # UTC time
            "date": response_data.get("date"),
            "course_name": self.course.name,
            "booking_url": self.course.booking_url,
            "holes": [price_info.get("bookable_holes", course_info.get("holes", 18))],
            "special_offer": response_data.get("has_deal", False),
            "restrictions": restrictions,
            "provider": "chronogolf_v2",
            "is_available": is_available,
            "green_fee": price_info.get("green_fee", 0.0),
            "price": price_info.get("subtotal", 0.0),  # Using subtotal as the main price
            "half_cart": price_info.get("half_cart", 0.0),
            "subtotal": price_info.get("subtotal", 0.0)
        }
        # print(tee_time_data)

        # Validate and create the TeeTime model
        tee_time_obj = TeeTime(**tee_time_data)
        return tee_time_obj


# @exponential_backoff
    def _hit_endpoint_with_requests(self, tee_time_parameter: TeeTimeParameter):
        response = requests.get(
            tee_time_parameter.endpoint,
            headers = tee_time_parameter.headers
        )

        response.raise_for_status()

        data = response.json()
        # print(json.dumps(data, indent=2))

        # Parse the JSON data (assuming it's tee time data)
        if isinstance(data, list):
            tee_times = data
        else:
            tee_times = data.get('data', data)  # Handle different response formats

        return data

    def _hit_endpoint_with_curl(self, tee_time_parameter: TeeTimeParameter):
        cmd = request_builder.cg_v2(tee_time_parameter)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        # print(data)
        data = data.get("teetimes", [])
        # print(json.dumps(data, indent=2))
        return data

    def get_tee_times(self, tee_time_parameter: TeeTimeParameter) -> List[TeeTime]: #  
        tee_times = []

        response = self._hit_endpoint_with_curl(tee_time_parameter)
        for resp_tee_time in response:
            tee_times.append(self.get_tee_time_from_response(resp_tee_time))

        return tee_times
