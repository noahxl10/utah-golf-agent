import requests
import json
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode
import os


def get_foreup_teetimes(
    schedule_id: int,
    date_str: str = None,
    time: str = "all",
    holes: str = "all", 
    players: int = 0,
    booking_class: int = 49991,
    specials_only: int = 0,
    api_key: str = "no_limits",
    timeout: int = 10
) -> Optional[dict]:
    """
    Get tee times from ForeUp API
    
    Args:
        schedule_id: Primary schedule ID for the course
        date_str: Date in MM-DD-YYYY format (defaults to today)
        time: Time filter ("all", "morning", "afternoon", "evening", or specific time)
        holes: Hole filter ("all", "9", "18")
        players: Number of players (0 for any)
        booking_class: Booking class ID
        specials_only: 1 for specials only, 0 for all
        api_key: API key (default: "no_limits")
        timeout: Request timeout in seconds
    
    Returns:
        JSON response data or None if error
    """
    if date_str is None:
        date_str = date.today().strftime("%m-%d-%Y")

    base_url = os.environ["FOREUP_ENDPOINT"]

    # Build query parameters
    params = {
        'time': time,
        'date': date_str,
        'holes': holes,
        'players': players,
        'booking_class': booking_class,
        'schedule_id': schedule_id,
        'schedule_ids[]': schedule_id,  # Array format
        'specials_only': specials_only,
        'api_key': api_key
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Golf Tee Time Scraper)',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://app.foreupsoftware.com/'
    }
    
    try:
        print(f"Requesting ForeUp tee times for schedule {schedule_id} on {date_str}")
        print(f"URL: {base_url}?{urlencode(params, doseq=True)}")
        
        response = requests.get(base_url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        tee_count = len(data) if isinstance(data, list) else len(data.get('times', []))
        print(f"✅ Success! Found {tee_count} tee times")
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


def get_multiple_schedules(
    schedule_ids: List[int],
    date_str: str = None,
    **kwargs
) -> Dict[int, Optional[dict]]:
    """
    Get tee times for multiple schedule IDs
    
    Args:
        schedule_ids: List of schedule IDs to query
        date_str: Date in MM-DD-YYYY format
        **kwargs: Additional parameters to pass to get_foreup_teetimes
    
    Returns:
        Dictionary mapping schedule_id to response data
    """
    results = {}
    
    for schedule_id in schedule_ids:
        print(f"\n📅 Getting times for schedule {schedule_id}")
        data = get_foreup_teetimes(
            schedule_id=schedule_id,
            date_str=date_str,
            **kwargs
        )
        results[schedule_id] = data
        
        # Be respectful - add delay between requests
        import time
        time.sleep(1)
    
    return results

def search_date_range(
    schedule_id: int,
    days_ahead: int = 7,
    **kwargs
) -> Dict[str, Optional[dict]]:
    """
    Search multiple dates for a given schedule
    
    Args:
        schedule_id: Schedule ID to search
        days_ahead: Number of days ahead to search
        **kwargs: Additional parameters to pass to get_foreup_teetimes
    
    Returns:
        Dictionary mapping date to response data
    """
    results = {}
    
    for i in range(days_ahead):
        search_date = (datetime.now() + timedelta(days=i)).strftime("%m-%d-%Y")
        print(f"\n📅 Searching for {search_date}")
        
        data = get_foreup_teetimes(
            schedule_id=schedule_id,
            date_str=search_date,
            **kwargs
        )
        
        if data:
            results[search_date] = data
        
        # Be respectful - add delay between requests
        import time
        time.sleep(1)
    
    return results


def parse_foreup_teetimes(data: Any) -> List[Dict[str, Any]]:
    """
    Parse ForeUp tee time data into a standardized format
    
    Args:
        data: Raw JSON response from ForeUp API
    
    Returns:
        List of parsed tee time dictionaries
    """
    parsed_times = []
    
    # Handle different response formats
    if isinstance(data, list):
        times_list = data
    elif isinstance(data, dict):
        times_list = data.get('times', data.get('data', []))
    else:
        return parsed_times
    
    for tee_time in times_list:
        if isinstance(tee_time, dict):
            parsed_time = {
                'time': tee_time.get('time'),
                'date': tee_time.get('date'),
                'available_spots': tee_time.get('available_spots', tee_time.get('spots')),
                'price': tee_time.get('price', tee_time.get('green_fee')),
                'holes': tee_time.get('holes'),
                'course_name': tee_time.get('course_name', tee_time.get('course')),
                'booking_url': tee_time.get('booking_url'),
                'special': tee_time.get('special', False),
                'restrictions': tee_time.get('restrictions', []),
                'raw_data': tee_time  # Keep original for debugging
            }
            parsed_times.append(parsed_time)
    
    return parsed_times


def display_foreup_times(tee_times: List[Dict[str, Any]]) -> None:
    """Display ForeUp tee times in a nice formatted way"""
    if not tee_times:
        print("No tee times found.")
        return
    
    print(f"\n{'='*80}")
    print(f"{'FOREUP GOLF TEE TIMES':^80}")
    print(f"{'='*80}")
    
    if tee_times:
        print(f"Date: {tee_times[0].get('date', 'Unknown')}")
    print(f"{'='*80}")
    
    # Header
    print(f"{'Time':<10} {'Holes':<8} {'Price':<12} {'Spots':<8} {'Course':<20} {'Special':<10}")
    print(f"{'-'*10} {'-'*8} {'-'*12} {'-'*8} {'-'*20} {'-'*10}")
    
    # Sort by time
    sorted_times = sorted(tee_times, key=lambda x: x.get('time', ''))
    
    for tee_time in sorted_times:
        time = tee_time.get('time', 'N/A')
        holes = str(tee_time.get('holes', 'N/A'))
        price = f"${tee_time.get('price', 0):.0f}" if tee_time.get('price') else 'N/A'
        spots = str(tee_time.get('available_spots', 'N/A'))
        course = (tee_time.get('course_name', 'Unknown') or 'Unknown')[:18]
        special = "⭐ Yes" if tee_time.get('special') else "No"
        
        print(f"{time:<10} {holes:<8} {price:<12} {spots:<8} {course:<20} {special:<10}")
    
    # Summary
    available_count = sum(1 for t in tee_times if t.get('available_spots', 0) > 0)
    special_count = sum(1 for t in tee_times if t.get('special'))
    
    print(f"\n{'='*80}")
    print(f"Summary: {available_count}/{len(tee_times)} tee times available")
    print(f"Special offers: {special_count}")
    if available_count > 0:
        prices = [t.get('price', 0) for t in tee_times if t.get('price') and t.get('available_spots', 0) > 0]
        if prices:
            avg_price = sum(prices) / len(prices)
            print(f"Average price: ${avg_price:.0f}")
    print(f"{'='*80}\n")


def find_available_foreup_times(
    schedule_id: int,
    date_str: str = None,
    min_spots: int = 1,
    max_price: float = None,
    holes_filter: str = "all",
    specials_only: bool = False
) -> List[Dict[str, Any]]:
    """
    Find available ForeUp tee times matching criteria
    
    Args:
        schedule_id: Schedule ID to search
        date_str: Date in MM-DD-YYYY format
        min_spots: Minimum available spots required
        max_price: Maximum price filter
        holes_filter: Hole count filter ("9", "18", or "all")
        specials_only: Only return special offers
    
    Returns:
        List of matching tee times
    """
    data = get_foreup_teetimes(
        schedule_id=schedule_id,
        date_str=date_str,
        holes=holes_filter,
        specials_only=1 if specials_only else 0
    )
    
    if not data:
        return []
    
    parsed_times = parse_foreup_teetimes(data)
    
    # Filter results
    filtered_times = []
    for tee_time in parsed_times:
        spots = tee_time.get('available_spots', 0)
        price = tee_time.get('price', 0)
        
        # Check criteria
        if spots >= min_spots:
            if max_price is None or price <= max_price:
                filtered_times.append(tee_time)
    
    return filtered_times

# Golf course database (expand as needed)
FOREUP_COURSES = {
    "example_course": {
        "schedule_id": 674,
        "booking_class": 49991,
        "name": "Example Golf Course"
    },
    # Add more courses here...
}


def search_by_course_name(course_name: str, **kwargs):
    """Search by course name instead of schedule ID"""
    if course_name.lower() in FOREUP_COURSES:
        course_info = FOREUP_COURSES[course_name.lower()]
        return get_foreup_teetimes(
            schedule_id=course_info["schedule_id"],
            booking_class=course_info.get("booking_class", 49991),
            **kwargs
        )
    else:
        print(f"⚠️  Course '{course_name}' not found in database")
        return None

# Example usage
if __name__ == "__main__":
    # Example from the URL you provided
    schedule_id = 674
    booking_class = 49991
    
    print("=" * 50)
    print("EXAMPLE 1: Basic Search")
    print("=" * 50)
    
    # Get tee times using the parameters from your URL
    data = get_foreup_teetimes(
        schedule_id=schedule_id,
        date_str="08-28-2025",
        booking_class=booking_class
    )
    
    if data:
        # Print raw JSON
        print("\nRaw JSON Response:")
        print(json.dumps(data, indent=2))
        
        # Parse and display nicely
        parsed_times = parse_foreup_teetimes(data)
        display_foreup_times(parsed_times)
    
    print("\n" + "=" * 50)
    print("EXAMPLE 2: Find Available Times")
    print("=" * 50)
    
    # Find available times under $75
    available_times = find_available_foreup_times(
        schedule_id=schedule_id,
        date_str="08-28-2025",
        max_price=75.0,
        min_spots=2
    )
    
    if available_times:
        print(f"Found {len(available_times)} available times under $75:")
        for time_slot in available_times:
            print(f"  {time_slot['time']} - ${time_slot['price']} ({time_slot['available_spots']} spots)")
    
    print("\n" + "=" * 50)
    print("EXAMPLE 3: Search Date Range")
    print("=" * 50)
    
    # Search next 3 days
    date_results = search_date_range(
        schedule_id=schedule_id,
        days_ahead=3,
        booking_class=booking_class
    )
    
    for date_str, result in date_results.items():
        if result:
            parsed = parse_foreup_teetimes(result)
            available_count = sum(1 for t in parsed if t.get('available_spots', 0) > 0)
            print(f"{date_str}: {available_count} available slots")
