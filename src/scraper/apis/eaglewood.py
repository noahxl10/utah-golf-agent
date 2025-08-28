import requests
import json
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
import os


def get_eaglewood_teetimes(
    golf_club_id: int = 15391,
    golf_course_id: int = 18901,
    date_str: str = None,
    configuration_type_id: int = 0,
    golf_club_group_id: int = 0,
    group_sheet_type_id: int = 0,
    timeout: int = 10
) -> Optional[dict]:
    """
    Get tee times from MemberSports API (Eaglewood format)
    
    Args:
        golf_club_id: Golf club ID (default: 15391 for Eaglewood)
        golf_course_id: Golf course ID (default: 18901)
        date_str: Date in YYYY-MM-DD format (defaults to today)
        configuration_type_id: Configuration type (default: 0)
        golf_club_group_id: Golf club group ID (default: 0)
        group_sheet_type_id: Group sheet type ID (default: 0)
        timeout: Request timeout in seconds
    
    Returns:
        JSON response data or None if error
    """
    if date_str is None:
        date_str = date.today().strftime("%Y-%m-%d")
    
    base_url = os.environ["EAGLEWOOD_ENDPOINT"]
    
    # Build payload
    payload = {
        "configurationTypeId": configuration_type_id,
        "date": date_str,
        "golfClubGroupId": golf_club_group_id,
        "golfClubId": golf_club_id,
        "golfCourseId": golf_course_id,
        "groupSheetTypeId": group_sheet_type_id
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Golf Tee Time Scraper)',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        print(f"Requesting Eaglewood tee times for club {golf_club_id} on {date_str}")
        print(f"URL: {base_url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(base_url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        tee_count = len([slot for slot in data if slot.get('items')])
        print(f"✅ Success! Found {tee_count} tee time slots")
        return data
        
    except requests.Timeout:
        print(f"❌ Timeout after {timeout} seconds")
        return None
    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return None


def convert_tee_time_minutes(minutes: int) -> str:
    """
    Convert tee time from minutes since midnight to HH:MM format
    
    Args:
        minutes: Minutes since midnight (e.g., 420 = 7:00 AM)
    
    Returns:
        Time string in HH:MM format
    """
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def parse_eaglewood_teetimes(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse Eaglewood tee time data into a standardized format
    
    Args:
        data: Raw JSON response from MemberSports API
    
    Returns:
        List of parsed tee time dictionaries
    """
    parsed_times = []
    
    for tee_slot in data:
        tee_time_minutes = tee_slot.get('teeTime', 0)
        tee_time_formatted = convert_tee_time_minutes(tee_time_minutes)
        
        items = tee_slot.get('items', [])
        
        if not items:
            # Empty slot - still show it as unavailable
            parsed_times.append({
                'time': tee_time_formatted,
                'time_minutes': tee_time_minutes,
                'available': False,
                'available_count': 0,
                'player_count': 0,
                'price': 0,
                'course_name': 'No availability',
                'holes': 0,
                'is_back_nine': False,
                'allows_singles': False,
                'minimum_players': 0,
                'booking_allowed': False,
                'cart_required': False,
                'tee_time_id': None,
                'raw_data': tee_slot
            })
        else:
            # Process each item in the slot
            for item in items:
                parsed_time = {
                    'time': tee_time_formatted,
                    'time_minutes': tee_time_minutes,
                    'available': item.get('availableCount', 0) > 0,
                    'available_count': item.get('availableCount', 0),
                    'player_count': item.get('playerCount', 0),
                    'price': float(item.get('price', 0)),
                    'course_name': item.get('name', 'Unknown'),
                    'holes': item.get('golfCourseNumberOfHoles', 18),
                    'is_back_nine': item.get('isBackNine', False),
                    'allows_singles': item.get('allowSinglesToBookOnline', False),
                    'minimum_players': item.get('minimumNumberOfPlayers', 1),
                    'booking_allowed': not item.get('bookingNotAllowed', True),
                    'booking_not_allowed_reason': item.get('bookingNotAllowedReason'),
                    'cart_required': item.get('cartRequirementTypeId', 0) > 0,
                    'premium_charge': float(item.get('premiumCharge', 0)),
                    'tax_rate': float(item.get('golfTaxRate', 0)),
                    'tee_time_id': item.get('teeTimeId'),
                    'golf_club_id': item.get('golfClubId'),
                    'golf_course_id': item.get('golfCourseId'),
                    'raw_data': item
                }
                parsed_times.append(parsed_time)
    
    return parsed_times


def display_eaglewood_times(tee_times: List[Dict[str, Any]]) -> None:
    """Display Eaglewood tee times in a nice formatted way"""
    if not tee_times:
        print("No tee times found.")
        return
    
    print(f"\n{'='*100}")
    print(f"{'EAGLEWOOD GOLF TEE TIMES':^100}")
    print(f"{'='*100}")
    
    # Header
    print(f"{'Time':<8} {'Course':<25} {'Holes':<7} {'Price':<10} {'Avail':<7} {'Players':<9} {'Singles':<9} {'Status':<15}")
    print(f"{'-'*8} {'-'*25} {'-'*7} {'-'*10} {'-'*7} {'-'*9} {'-'*9} {'-'*15}")
    
    # Sort by time
    sorted_times = sorted(tee_times, key=lambda x: x.get('time_minutes', 0))
    
    for tee_time in sorted_times:
        time = tee_time.get('time', 'N/A')
        course = (tee_time.get('course_name', 'Unknown') or 'Unknown')[:23]
        holes = str(tee_time.get('holes', 'N/A'))
        if tee_time.get('is_back_nine'):
            holes += " (Back 9)"
        
        price = f"${tee_time.get('price', 0):.0f}"
        if tee_time.get('premium_charge', 0) > 0:
            price += f"+${tee_time.get('premium_charge', 0):.0f}"
        
        available = str(tee_time.get('available_count', 0))
        players = f"{tee_time.get('player_count', 0)}/{4}"  # Assume max 4 players
        singles = "✅" if tee_time.get('allows_singles') else "❌"
        
        # Determine status
        if not tee_time.get('booking_allowed', True):
            status = "🚫 Not allowed"
        elif tee_time.get('available_count', 0) > 0:
            status = "✅ Available"
        elif tee_time.get('player_count', 0) > 0:
            status = "⚠️  Partially full"
        else:
            status = "❌ Full"
        
        print(f"{time:<8} {course:<25} {holes:<7} {price:<10} {available:<7} {players:<9} {singles:<9} {status:<15}")
    
    # Summary
    available_count = sum(1 for t in tee_times if t.get('available_count', 0) > 0)
    total_count = len([t for t in tee_times if t.get('tee_time_id')])  # Only count actual tee times
    singles_allowed = sum(1 for t in tee_times if t.get('allows_singles'))
    
    print(f"\n{'='*100}")
    print(f"Summary: {available_count}/{total_count} tee times available")
    print(f"Singles allowed: {singles_allowed}/{total_count}")
    
    if available_count > 0:
        available_times = [t for t in tee_times if t.get('available_count', 0) > 0]
        prices = [t.get('price', 0) for t in available_times if t.get('price', 0) > 0]
        if prices:
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            print(f"Price range: ${min_price:.0f} - ${max_price:.0f} (avg: ${avg_price:.0f})")
    
    print(f"{'='*100}\n")


def find_available_eaglewood_times(
    golf_club_id: int = 15391,
    golf_course_id: int = 18901,
    date_str: str = None,
    min_available: int = 1,
    max_price: float = None,
    allow_back_nine: bool = True,
    singles_only: bool = False
) -> List[Dict[str, Any]]:
    """
    Find available Eaglewood tee times matching criteria
    
    Args:
        golf_club_id: Golf club ID
        golf_course_id: Golf course ID  
        date_str: Date in YYYY-MM-DD format
        min_available: Minimum available spots required
        max_price: Maximum price filter
        allow_back_nine: Include back 9 tee times
        singles_only: Only return times that allow singles
    
    Returns:
        List of matching tee times
    """
    data = get_eaglewood_teetimes(
        golf_club_id=golf_club_id,
        golf_course_id=golf_course_id,
        date_str=date_str
    )
    
    if not data:
        return []
    
    parsed_times = parse_eaglewood_teetimes(data)
    
    # Filter results
    filtered_times = []
    for tee_time in parsed_times:
        available = tee_time.get('available_count', 0)
        price = tee_time.get('price', 0)
        is_back_nine = tee_time.get('is_back_nine', False)
        allows_singles = tee_time.get('allows_singles', False)
        booking_allowed = tee_time.get('booking_allowed', False)
        
        # Check criteria
        if (available >= min_available and 
            booking_allowed and
            (max_price is None or price <= max_price) and
            (allow_back_nine or not is_back_nine) and
            (not singles_only or allows_singles)):
            filtered_times.append(tee_time)
    
    return filtered_times


def search_eaglewood_date_range(
    golf_club_id: int = 15391,
    golf_course_id: int = 18901,
    days_ahead: int = 7,
    **kwargs
) -> Dict[str, Optional[dict]]:
    """
    Search multiple dates for Eaglewood tee times
    
    Args:
        golf_club_id: Golf club ID
        golf_course_id: Golf course ID
        days_ahead: Number of days ahead to search
        **kwargs: Additional parameters to pass to get_eaglewood_teetimes
    
    Returns:
        Dictionary mapping date to response data
    """
    results = {}
    
    for i in range(days_ahead):
        search_date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        print(f"\n📅 Searching for {search_date}")
        
        data = get_eaglewood_teetimes(
            golf_club_id=golf_club_id,
            golf_course_id=golf_course_id,
            date_str=search_date,
            **kwargs
        )
        
        if data:
            results[search_date] = data
        
        # Be respectful - add delay between requests
        import time
        time.sleep(1)
    
    return results

# Golf course database for MemberSports API
MEMBER_SPORTS_COURSES = {
    "eaglewood": {
        "golf_club_id": os.environ["EAGLEWOOD_CLUB_ID"],
        "golf_course_id": os.environ["EAGLEWOOD_COURSE_ID"],
        "name": "Eaglewood Golf Club"
    },
    # Add more courses here...
}


def search_by_course_name(course_name: str, **kwargs):
    """Search by course name instead of IDs"""
    if course_name.lower() in MEMBER_SPORTS_COURSES:
        course_info = MEMBER_SPORTS_COURSES[course_name.lower()]
        return get_eaglewood_teetimes(
            golf_club_id=course_info["golf_club_id"],
            golf_course_id=course_info["golf_course_id"],
            **kwargs
        )
    else:
        print(f"⚠️  Course '{course_name}' not found in database")
        return None


def test_with_sample_data():
    """Test with sample data structure"""
    sample_data = [
        {
            "teeTime": 420,
            "items": [
                {
                    "allowSinglesToBookOnline": True,
                    "availableCount": 0,
                    "backNinePlayerCount": 3,
                    "bookingNotAllowed": False,
                    "bookingNotAllowedReason": None,
                    "cartRequirementTypeId": 1,
                    "configurationTypeId": 0,
                    "golfClubId": 15391,
                    "golfCourseId": 18901,
                    "golfCourseNumberOfHoles": 18,
                    "golfTaxRate": 0.0,
                    "minimumNumberOfPlayers": 2,
                    "name": "Eaglewood",
                    "playerCount": 3,
                    "price": 60.0000,
                    "teeTime": 420,
                    "teeTimeId": 9028166
                }
            ]
        },
        {
            "teeTime": 430,
            "items": []
        },
        {
            "teeTime": 460,
            "items": [
                {
                    "allowSinglesToBookOnline": True,
                    "availableCount": 0,
                    "isBackNine": True,
                    "minimumNumberOfPlayers": 2,
                    "name": "Eaglewood Back Nine",
                    "playerCount": 0,
                    "price": 30.0000,
                    "teeTime": 460,
                    "teeTimeId": 9028175
                }
            ]
        }
    ]
    
    print("Testing with sample Eaglewood data:")
    parsed_times = parse_eaglewood_teetimes(sample_data)
    display_eaglewood_times(parsed_times)
    return parsed_times

# Example usage
if __name__ == "__main__":
    # Test with sample data first
    print("=" * 50)
    print("TESTING WITH SAMPLE DATA")
    print("=" * 50)
    test_with_sample_data()
    
    print("\n" + "=" * 50)
    print("EXAMPLE 1: Live API Call")
    print("=" * 50)
    
    # Get tee times using the parameters from your example
    data = get_eaglewood_teetimes(
        golf_club_id=15391,
        golf_course_id=18901,
        date_str="2025-09-03"
    )
    
    if data:
        # Print raw JSON (first few items)
        print("\nRaw JSON Response (sample):")
        print(json.dumps(data[:2], indent=2))
        
        # Parse and display nicely
        parsed_times = parse_eaglewood_teetimes(data)
        display_eaglewood_times(parsed_times)
    
    print("\n" + "=" * 50)
    print("EXAMPLE 2: Find Available Times")
    print("=" * 50)
    
    # Find available times under $50 that allow singles
    available_times = find_available_eaglewood_times(
        date_str="2025-09-03",
        max_price=50.0,
        singles_only=True
    )
    
    if available_times:
        print(f"Found {len(available_times)} available times under $50 for singles:")
        for time_slot in available_times:
            course_type = " (Back 9)" if time_slot['is_back_nine'] else ""
            print(f"  {time_slot['time']} - ${time_slot['price']:.0f}{course_type} ({time_slot['available_count']} spots)")
    else:
        print("No available times found matching criteria")
    
    print("\n" + "=" * 50)
    print("EXAMPLE 3: Search Date Range")
    print("=" * 50)
    
    # Search next 3 days
    date_results = search_eaglewood_date_range(days_ahead=3)
    
    for date_str, result in date_results.items():
        if result:
            parsed = parse_eaglewood_teetimes(result)
            available_count = sum(1 for t in parsed if t.get('available_count', 0) > 0)
            total_slots = len([t for t in parsed if t.get('tee_time_id')])
            print(f"{date_str}: {available_count}/{total_slots} available slots")
