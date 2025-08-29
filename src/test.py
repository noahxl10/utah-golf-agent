from src._typing.structs import (
    TeeTime, 
    TeeTimeParameter,
    Course,
)

def get_mock_tee_times():
    """
    Creates a sample list of TeeTime objects for demonstration.
    In a real application, this data would come from your API parsers.
    """
    tee_times = [
        TeeTime(
            start_time="2025-08-30T14:00:00Z",
            date="2025-08-30",
            course_name="South Mountain 18 Holes",
            holes=[18],
            booking_url="https://www.chronogolf.com/club/south-mountain-slco",
            provider="chronogolf_v2",
            is_available=True,
            green_fee=55.0,
            half_cart=20.0,
            subtotal=75.0,
            price=75.0,
            restrictions=["Minimum 2 players"]
        ),
        TeeTime(
            start_time="2025-08-30T14:10:00Z",
            date="2025-08-30",
            course_name="South Mountain 18 Holes",
            holes=[18],
            provider="chronogolf_v2",
            booking_url="https://www.chronogolf.com/club/south-mountain-slco",
            is_available=False,
            green_fee=55.0,
            half_cart=20.0,
            subtotal=75.0,
            price=75.0,
            special_offer=True
        ),
        TeeTime(
            start_time="2025-08-30T09:20:00Z",
            date="2025-08-30",
            course_name="Stonebridge Golf Club",
            holes=[9],
            booking_url="https://www.chronogolf.com/club/south-mountain-slco",
            provider="foreup",
            is_available=True,
            green_fee=25.0,
            half_cart=10.0,
            subtotal=35.0,
            price=35.0
        )
    ]
    return tee_times