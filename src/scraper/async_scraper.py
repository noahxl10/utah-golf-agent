from datetime import date
import json
from typing import List, Dict, Any
from src.config import courses
import os
import traceback
import asyncio
from src.scraper.apis.async_chronogolf import AsyncV1, AsyncV2
from src.scraper.apis.async_eaglewood import AsyncEaglewood
from src.scraper.apis.async_foreup import AsyncForeup
from src._typing.structs import (
    Course,
    TeeTimeParameter,
    TeeTime,
)


async def chronogolf_v2_api(tee_time_parameter):
    tee_times = []
    try:
        v2 = AsyncV2(tee_time_parameter.course)
        tee_times = await v2.get_tee_times(tee_time_parameter)
    except Exception as e:
        print(e)
    return tee_times


async def chronogolf_v1_api(tee_time_parameter):
    tee_times = []
    try:
        v1 = AsyncV1(tee_time_parameter.course)
        tee_times.extend(await v1.get_tee_times(tee_time_parameter))
        return tee_times
    except Exception as e:
        print(e)
    return tee_times


async def chronogolf_tee_times(date):

    all_tee_times = []
    tasks = []

    for course_name in courses:
        try:
            course_details = courses.get(course_name)
            sub_details = course_details.get("config")

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

            if course_details.get("provider") == "chronogolf":
                if sub_details.get("version") == "marketplaceV1":
                    tasks.append(chronogolf_v1_api(ttp))
                elif sub_details.get("version") == "marketplaceV2":
                    tasks.append(chronogolf_v2_api(ttp))
                    
        except Exception as e:
            print(traceback.format_exc())

    # Run all chronogolf requests concurrently
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                all_tee_times.extend(result)

    return all_tee_times


async def eaglewood_tee_times(date):
    tee_times = []
    try:
        course_name = "Eaglewood Golf Course"
        course_details = courses.get(course_name)
        sub_details = course_details.get("config")
        print(sub_details)

        # add date to booking url for specific click-search
        booking_url = sub_details.get('booking_url') # f"{sub_details.get('booking_url')}?date={date}"

        course = Course(
            name=course_name,
            booking_url=booking_url,
        )

        ttp = TeeTimeParameter(
            endpoint="",
            date=date,
            num_players=2,
            holes=[18],
            course=course,
        )
        eaglewood = AsyncEaglewood(course)
        tee_times.extend(await eaglewood.get_tee_times(ttp))
    except Exception as e:
        print(e)

    return tee_times


async def foreup_tee_times(date):

    all_tee_times = []
    tasks = []

    for course_name in courses:
        try:

            course_details = courses.get(course_name)

            if course_details.get("provider") == "foreup":

                sub_details = course_details.get("config")
                course = Course(
                    name=course_name,
                    booking_url=sub_details.get("booking_url")
                )

                ttp = TeeTimeParameter(
                    endpoint="", # os.environ[sub_details.get("endpoint_env_var")]"",
                    date=date,
                    num_players=3,
                    holes=[18],
                    course=course,
                )

                foreup = AsyncForeup(course)
                tasks.append(foreup.get_tee_times(ttp))

        except Exception as e:
            print(traceback.format_exc())

    # Run all foreup requests concurrently
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                all_tee_times.extend(result)

    return all_tee_times


def order_tee_times(tee_times: List[TeeTime]) -> List[TeeTime]:
    """
    Sorts a list of TeeTime objects.
    
    The primary sort key is 'start_time' (earliest to latest).
    The secondary sort key for breaking ties is 'course_name' (alphabetical).

    Args:
        tee_times: A list of TeeTime objects.
        
    Returns:
        A new list containing the sorted TeeTime objects.
    """
    # The sorted() function creates a new sorted list.
    # The key is a lambda function that returns a tuple of the properties to sort by.
    # Python will automatically sort by the first element of the tuple,
    # and then use the second element to resolve any ties.
    return sorted(tee_times, key=lambda tee_time: (tee_time.start_time, tee_time.course_name))


def sort_tee_times_in_place(tee_times: List[TeeTime]) -> None:
    """
    Sorts a list of TeeTime objects in-place (modifies the original list).
    
    The primary sort key is 'start_time', and the secondary is 'course_name'.
    """
    # The .sort() method sorts the list directly without creating a new one.
    tee_times.sort(key=lambda tee_time: (tee_time.start_time, tee_time.course_name))


async def get_all_tee_times(date):

    # Run all API calls concurrently
    foreup_task = foreup_tee_times(date)
    eaglewood_task = eaglewood_tee_times(date)
    chronogolf_task = chronogolf_tee_times(date)
    
    results = await asyncio.gather(foreup_task, eaglewood_task, chronogolf_task)
    
    all_times = []
    for result in results:
        all_times.extend(result)

    all_times_ordered = order_tee_times(all_times)

    return all_times_ordered


# Example usage:
# async def main():
#     x = await get_all_tee_times("2025-09-03")
#     print(x)

# if __name__ == "__main__":
#     asyncio.run(main())