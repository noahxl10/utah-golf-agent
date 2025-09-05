import requests
import json
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import subprocess
from src.config import courses as CONFIG
from datetime import datetime, timedelta
from src._typing.structs import (
    TeeTime, 
    TeeTimeParameter,
    Course,
)
from src.misc import request_builder
from src.request_logger import RequestLogger, RequestTimer


class Eaglewood:

    def __init__(self, course: Course):
        self.course = course
        # self.course_config = CONFIG[self.course.name]
        # self.sub_config = self.course_config["config"]
        # self.endpoint = os.environ[self.sub_config["endpoint_env_var"]]


    # def convert_time(self, minutes: int) -> str:
        # """Convert minutes since midnight to a formatted time string."""
        # midnight = datetime.strptime("00:00", "%H:%M")
        # time_obj = midnight + timedelta(minutes=minutes)
        # return time_obj.strftime("%I:%M %p").lstrip("0")  # strip leading zero


    def convert_time(self, minutes: int) -> str:
        """Convert minutes since midnight to a formatted time string."""
        midnight = datetime.strptime("00:00", "%H:%M")
        time_obj = midnight + timedelta(minutes=minutes)
        return time_obj.strftime("%H:%M")  # Military time format


    def get_tee_time_from_response(self, r):
        # if r.get("isBackNine")
        booking_not_allowed = r.get("bookingNotAllowed", "")
        max_num_players = 4 - r.get("playerCount")
        min_num_players = r.get("minimumNumberOfPlayers")
        price = float(r.get("price"))
        is_back_nine_only = r.get("isBackNine")

        holes = []
        if price == 60.0:
            holes = [9, 18]
        if is_back_nine_only or price == 30.0:
            holes = [9]

        is_available = False
        if not booking_not_allowed and max_num_players > 0:
            is_available = True

        return TeeTime(
            start_time_unf = self.convert_time(r.get("teeTime")),
            date = self.tee_time_parameter.date,
            course_name = self.course.name,
            booking_url = self.course.booking_url,
            holes = holes,
            provider="membersports",
            is_available=is_available,
            green_fee=price,
            price=price,
            subtotal=price,
            min_num_players=min_num_players,
            max_num_players=max_num_players,
            raw_json_response=r,
        )


    def _hit_endpoint_with_curl(self) -> dict:
        with RequestTimer() as timer:
            try:
                cmd = request_builder.ew_curl(self.tee_time_parameter)
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode != 0:
                    error_msg = f"Curl command failed: {result.stderr}"
                    RequestLogger.log_error(
                        provider="eaglewood",
                        endpoint=self.tee_time_parameter.endpoint,
                        error=error_msg,
                        course=self.course.name,
                        duration_ms=timer.get_duration()
                    )
                    raise Exception(error_msg)
                
                data = json.loads(result.stdout)
                
                # Log successful request
                RequestLogger.log_success(
                    provider="eaglewood",
                    endpoint=self.tee_time_parameter.endpoint,
                    response=data,
                    course=self.course.name,
                    duration_ms=timer.get_duration()
                )
                
                return data
                
            except Exception as e:
                if "json.loads" in str(e):
                    error_msg = f"Invalid JSON response: {result.stdout[:200] if 'result' in locals() else 'Unknown'}"
                else:
                    error_msg = str(e)
                    
                RequestLogger.log_error(
                    provider="eaglewood",
                    endpoint=self.tee_time_parameter.endpoint,
                    error=error_msg,
                    course=self.course.name,
                    duration_ms=timer.get_duration()
                )
                raise
        # for tee_time_dict in data:
        #     tee_time_minutes = tee_time_dict.get("teeTime")

        #     tee_time_specs = tee_time_dict.get("items")
        #     if tee_time_specs:
        #         tee_time_specs = tee_time_specs[0]


    def get_tee_times(self, tee_time_parameter):

        self.tee_time_parameter = tee_time_parameter

        tee_times = []

        response = self._hit_endpoint_with_curl()

        for resp_tee_time in response:
            print(resp_tee_time)
            resp_tee_time_specs = resp_tee_time.get("items")
            if resp_tee_time_specs:
                tee_times.append(
                    self.get_tee_time_from_response(
                        resp_tee_time_specs[0]
                    )
                )

        return tee_times
