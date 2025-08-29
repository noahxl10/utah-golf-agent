import requests
from datetime import date
import json
from typing import List, Dict, Any
from src.config import courses
import os
import traceback
import subprocess
# import ....static.config.config as C
from src.scraper.apis.chronogolf import V1, V2
from src.scraper.apis.eaglewood import Eaglewood
from src.scraper.apis.foreup import Foreup
from src._typing.structs import (
    Course,
    TeeTimeParameter,
)

def chronogolf_v2_api(tee_time_parameter):
    v2 = V2(tee_time_parameter.course)
    tee_times = v2.get_tee_times(tee_time_parameter)
    return tee_times


def chronogolf_v1_api(tee_time_parameter):
    v1 = V1(tee_time_parameter.course)
    tee_times = v1.get_tee_times(tee_time_parameter)
    return tee_times


def chronogolf_tee_times(date):

    all_tee_times = []

    for course_name in courses:
        try:
            course_details = courses.get(course_name)
            sub_details = course_details.get("config")
            print(sub_details)

            # add date to booking url for specific click-search
            booking_url = f"{sub_details.get('booking_url')}?date={date}"
            course = Course(
                name=course_name,
                booking_url=booking_url,
                club_id=sub_details.get("club_id", None),
                course_ids=sub_details.get("course_ids", None)
            )

            ttp = TeeTimeParameter(
                endpoint=os.environ[sub_details.get("endpoint_env_var")],
                date=date,
                num_players=3,
                holes=[18],
                course=course,
            )

            tee_times = []
            if course_details.get("provider") == "chronogolf":
                if sub_details.get("version") == "marketplaceV1":
                    tee_times.extend(chronogolf_v1_api(ttp))

                elif sub_details.get("version") == "marketplaceV2":
                    tee_times.extend(chronogolf_v2_api(ttp))

            all_tee_times.extend(tee_times)
        except Exception as e:
            print(traceback.format_exc())

    return all_tee_times


def eaglewood_tee_times(date):
    eaglewood = Eaglewood()

    course = Course(
        name="Eaglewood Golf Course"
    )

    ttp = TeeTimeParameter(
        endpoint="",
        date=date,
        num_players=2,
        holes=[18],
        course=course,
    )
    tee_times = eaglewood.get_tee_times(ttp)
    return tee_times


def foreup_tee_times(date):

    all_tee_times = []

    for course_name in courses:

        course_details = courses.get(course_name)

        course = Course(
            name=course_name,
        )

        ttp = TeeTimeParameter(
            endpoint="", # os.environ[sub_details.get("endpoint_env_var")]"",
            date=date,
            num_players=3,
            holes=[18],
            course=course,
        )

        foreup = Foreup(course)

        tee_times = []
        if course_details.get("provider") == "foreup":
            tee_times.extend(foreup.get_tee_times(ttp))

        all_tee_times.extend(tee_times)

    return all_tee_times
