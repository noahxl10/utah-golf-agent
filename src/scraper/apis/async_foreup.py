import aiohttp
import asyncio
import json
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode
import os
import subprocess
from src._typing.structs import (
    TeeTime, 
    TeeTimeParameter,
    Course,
)
from src.misc import request_builder


class AsyncForeup:

    def __init__(self, course):
        self.course = course
        self.course_name = self.course.name

    def get_tee_time_from_response(self, r):
        """
        format: 
        {
            "time": "2025-08-29 07:39",
            "start_front": 202507290739,
            "course_id": 22130,
            "course_name": "Stonebridge Golf Club (UT)",
            "schedule_id": 9912,
            "teesheet_id": 9912,
            "schedule_name": "Stonebridge Golf Club",
            "require_credit_card": true,
            "teesheet_holes": 27,
            "teesheet_side_id": 10954,
            "teesheet_side_name": "Creekside",
            "teesheet_side_order": 1,
            "reround_teesheet_side_id": 10955,
            "reround_teesheet_side_name": "Sunrise",
            "available_spots": 2,
            "available_spots_9": 0,
            "available_spots_18": 2,
            "maximum_players_per_booking": "4",
            "minimum_players": "1",
            "allowed_group_sizes": [
                "1",
                "2",
                "3",
                "4"
            ],
            "holes": 18,
            "has_special": false,
            "special_id": false,
            "special_discount_percentage": 0,
            "group_id": false,
            "booking_class_id": 13900,
            "booking_fee_required": false,
            "booking_fee_price": false,
            "booking_fee_per_person": false,
            "foreup_trade_discount_rate": 25,
            "trade_min_players": 2,
            "trade_cart_requirement": "both",
            "trade_hole_requirement": "all",
            "trade_available_players": 1,
            "green_fee_tax_rate": false,
            "green_fee_tax": 0,
            "green_fee_tax_9": 0,
            "green_fee_tax_18": 0,
            "guest_green_fee_tax_rate": false,
            "guest_green_fee_tax": 0,
            "guest_green_fee_tax_9": 0,
            "guest_green_fee_tax_18": 0,
            "cart_fee_tax_rate": false,
            "cart_fee_tax": 0,
            "cart_fee_tax_9": 0,
            "cart_fee_tax_18": 0,
            "guest_cart_fee_tax_rate": false,
            "guest_cart_fee_tax": 0,
            "guest_cart_fee_tax_9": 0,
            "guest_cart_fee_tax_18": 0,
            "foreup_discount": false,
            "pay_online": "no",
            "green_fee": 36,
            "green_fee_9": 0,
            "green_fee_18": 36,
            "guest_green_fee": 36,
            "guest_green_fee_9": 0,
            "guest_green_fee_18": 36,
            "cart_fee": 20,
            "cart_fee_9": 0,
            "cart_fee_18": 20,
            "guest_cart_fee": 20,
            "guest_cart_fee_9": 0,
            "guest_cart_fee_18": 20,
            "rate_type": "both",
            "special_was_price": null,
            "cart_fee_18_hole": 20,
            "cart_fee_9_hole": 10,
            "teesheet_logo": null,
            "teesheet_color": "",
            "teesheet_initials": "SG"
        }
        """

        max_num_players = r.get("available_spots")
        min_num_players = r.get("minimum_players")
        price = float(r.get("green_fee_18"))
        cart_fee = float(r.get("cart_fee"))

        is_back_nine_only = r.get("isBackNine")

        datetime = r.get("time") # "2025-08-29 07:39"
        date = datetime[0:10]
        time = datetime[-5:]

        holes = []
        if r.get("available_spots_9") > 0:
            holes.append(9)
        if r.get("available_spots_18") > 0:
            holes.append(18)

        is_available = False
        if max_num_players > 0:
            is_available = True

        return TeeTime(
            start_time_unf = time,
            date = date,
            course_name = self.course.name,
            booking_url = self.course.booking_url,
            holes = holes,
            provider="foreup",
            is_available=is_available,
            green_fee=price,
            price=price,
            subtotal=price,
            half_cart=cart_fee,
            min_num_players=min_num_players,
            max_num_players=max_num_players,
        )

    async def _hit_endpoint_with_curl(self) -> dict:
        if self.course.name == "Stonebridge Golf Club":
            cmd = request_builder.ew_curl(self.tee_time_parameter)
        elif self.course.name == "Bountiful Ridge Golf Course":
            cmd = request_builder.stonebridge_curl(self.tee_time_parameter)

        # Run subprocess in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(cmd, shell=True, capture_output=True, text=True)
        )

        data = json.loads(result.stdout)
        return data

    async def get_tee_times(self, tee_time_parameter):

        self.tee_time_parameter = tee_time_parameter

        tee_times = []

        response = await self._hit_endpoint_with_curl()

        for resp_tee_time in response:
            tee_times.append(
                self.get_tee_time_from_response(
                    resp_tee_time
                )
            )

        return tee_times