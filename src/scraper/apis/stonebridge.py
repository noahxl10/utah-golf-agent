import requests
import json
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode
import os


def get_stonebridge_teetimes(
    schedule_id: int = 9912,
    date_str: str = None,
    time: str = "all",
    holes: str = "all", 
    players: int = 0,
    booking_class: int = 13900,
    specials_only: int = 0,
    api_key: str = "no_limits",
    bearer_token: str = None,
    cookie: str = None,
    timeout: int = 10
) -> Optional[dict]:
    """
    Get tee times from ForeUp API for Stonebridge Golf Club
    
    Args:
        schedule_id: Schedule ID for the course (default: 9912 for Stonebridge)
        date_str: Date in MM-DD-YYYY format (defaults to today)
        time: Time filter ("all", "morning", "afternoon", "evening")
        holes: Hole filter ("all", "9", "18")
        players: Number of players (0 for any)
        booking_class: Booking class ID (default: 13900 for Stonebridge)
        specials_only: 1 for specials only, 0 for all
        api_key: API key (default: "no_limits")
        bearer_token: Bearer token for authentication
        cookie: Session cookie (if needed)
        timeout: Request timeout in seconds
    
    Returns:
        JSON response data or None if error
    """
    if date_str is None:
        date_str = date.today().strftime("%m-%d-%Y")
    
    base_url = os.environ["STONEBRIDGE_ENDPOINT_TIMES"]
    
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

    # Set correct referer URL
    referer = os.environ["STONEBRIDGE_REFERER"]

    headers = {
        # Standard headers
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        
        # Context headers
        'Referer': referer,
        'Origin': 'https://foreupsoftware.com',
        'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        
        # ForeUp specific headers
        'X-Requested-With': 'XMLHttpRequest',
        'X-Fu-Golfer-Location': 'foreup',
        'Api-Key': api_key,
        'Priority': 'u=1, i'
    }
    
    # Add Authorization header if bearer token is provided
    if bearer_token:
        headers['X-Authorization'] = f'Bearer {bearer_token}'
    
    # Add cookie if provided
    if cookie:
        headers['Cookie'] = cookie
    
    try:
        print(f"Requesting Stonebridge tee times for {date_str}")
        print(f"URL: {base_url}?{urlencode(params, doseq=True)}")
        
        response = requests.get(base_url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        tee_count = len(data) if isinstance(data, list) else 0
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


def parse_stonebridge_teetimes(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse Stonebridge tee time data into a standardized format
    
    Args:
        data: Raw JSON response from ForeUp API
    
    Returns:
        List of parsed tee time dictionaries
    """
    parsed_times = []
    
    if not isinstance(data, list):
        print("Expected a list of tee times, got something else.")
        return parsed_times
    
    for tee_time in data:
        # Extract time
        time_str = tee_time.get('time', '')
        time_only = time_str.split(' ')[1] if ' ' in time_str else time_str
        
        # Extract course info
        course_name = tee_time.get('course_name', 'Unknown')
        side_name = tee_time.get('teesheet_side_name', '')
        if side_name:
            full_course_name = f"{course_name} - {side_name}"
        else:
            full_course_name = course_name
            
        # Parse holes and pricing
        holes_count = tee_time.get('holes', 0)
        has_9_holes = tee_time.get('available_spots_9', 0) > 0
        has_18_holes = tee_time.get('available_spots_18', 0) > 0
        
        green_fee = 0
        cart_fee = 0
        total_fee = 0
        
        if holes_count == 9 or has_9_holes:
            green_fee = float(tee_time.get('green_fee_9', 0))
            cart_fee = float(tee_time.get('cart_fee_9', 0))
        elif holes_count == 18 or has_18_holes:
            green_fee = float(tee_time.get('green_fee_18', 0))
            cart_fee = float(tee_time.get('cart_fee_18', 0))
        else:
            green_fee = float(tee_time.get('green_fee', 0))
            cart_fee = float(tee_time.get('cart_fee', 0))
            
        total_fee = green_fee + cart_fee
        
        # Special offer info
        has_special = tee_time.get('has_special', False)
        special_discount = tee_time.get('special_discount_percentage', 0)
        original_price = tee_time.get('special_was_price')
        
        # Group size info
        allowed_sizes = tee_time.get('allowed_group_sizes', [])
        min_players = int(tee_time.get('minimum_players', 1))
        max_players = int(tee_time.get('maximum_players_per_booking', 4))
        available_spots = tee_time.get('available_spots', 0)
        
        # Create parsed tee time
        parsed_time = {
            'time': time_only,
            'date': date_str,
            'course_name': full_course_name,
            'holes': holes_count,
            'available_spots': available_spots,
            'available_9_holes': tee_time.get('available_spots_9', 0),
            'available_18_holes': tee_time.get('available_spots_18', 0),
            'green_fee': green_fee,
            'cart_fee': cart_fee,
            'total_fee': total_fee,
            'has_special': has_special,
            'special_discount': special_discount,
            'original_price': original_price,
            'min_players': min_players,
            'max_players': max_players,
            'allowed_group_sizes': allowed_sizes,
            'schedule_id': tee_time.get('schedule_id'),
            'course_id': tee_time.get('course_id'),
            'require_credit_card': tee_time.get('require_credit_card', False),
            'booking_class_id': tee_time.get('booking_class_id'),
            'raw_data': tee_time  # Keep original for debugging
        }
        parsed_times.append(parsed_time)
    
    return parsed_times


def display_stonebridge_times(tee_times: List[Dict[str, Any]], date_str: str = None) -> None:
    """Display Stonebridge tee times in a nice formatted way"""
    if not tee_times:
        print("No tee times found.")
        return
    
    print(f"\n{'='*100}")
    print(f"{'STONEBRIDGE GOLF CLUB TEE TIMES':^100}")
    print(f"{'='*100}")
    
    if date_str:
        print(f"Date: {date_str}")
    print(f"{'='*100}")
    
    # Header
    print(f"{'Time':<8} {'Course':<30} {'Holes':<7} {'Price':<12} {'Cart':<8} {'Total':<8} {'Spots':<7} {'Special':<10}")
    print(f"{'-'*8} {'-'*30} {'-'*7} {'-'*12} {'-'*8} {'-'*8} {'-'*7} {'-'*10}")
    
    # Sort by time
    sorted_times = sorted(tee_times, key=lambda x: x.get('time', ''))
    
    for tee_time in sorted_times:
        time = tee_time.get('time', 'N/A')
        course = (tee_time.get('course_name', 'Unknown') or 'Unknown')[:28]
        holes = str(tee_time.get('holes', 'N/A'))
        
        green_fee = f"${tee_time.get('green_fee', 0):.0f}"
        cart_fee = f"${tee_time.get('cart_fee', 0):.0f}"
        total = f"${tee_time.get('total_fee', 0):.0f}"
        
        available = str(tee_time.get('available_spots', 0))
        
        # Special offer indicator
        if tee_time.get('has_special', False):
            original = tee_time.get('original_price')
            discount = tee_time.get('special_discount', 0)
            if original and discount:
                special = f"⭐ {discount}% off"
            else:
                special = "⭐ Yes"
        else:
            special = ""
        
        print(f"{time:<8} {course:<30} {holes:<7} {green_fee:<12} {cart_fee:<8} {total:<8} {available:<7} {special:<10}")
    
    # Summary
    available_9_holes = sum(t.get('available_9_holes', 0) > 0 for t in tee_times)
    available_18_holes = sum(t.get('available_18_holes', 0) > 0 for t in tee_times)
    special_count = sum(1 for t in tee_times if t.get('has_special', False))
    
    print(f"\n{'='*100}")
    print(f"Summary: {len(tee_times)} total tee times")
    print(f"Available for 9 holes: {available_9_holes}")
    print(f"Available for 18 holes: {available_18_holes}")
    print(f"Special offers: {special_count}")
    
    # Price ranges
    prices = [t.get('total_fee', 0) for t in tee_times if t.get('total_fee', 0) > 0]
    if prices:
        min_price = min(prices)
        max_price = max(prices)
        print(f"Price range: ${min_price:.0f} - ${max_price:.0f}")
    
    print(f"{'='*100}\n")


def search_stonebridge_date_range(
    days_ahead: int = 7,
    **kwargs
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Search multiple dates for Stonebridge tee times
    
    Args:
        days_ahead: Number of days ahead to search
        **kwargs: Additional parameters to pass to get_stonebridge_teetimes
    
    Returns:
        Dictionary mapping date to parsed tee times
    """
    results = {}
    
    for i in range(days_ahead):
        search_date = (datetime.now() + timedelta(days=i)).strftime("%m-%d-%Y")
        print(f"\n📅 Searching for {search_date}")
        
        data = get_stonebridge_teetimes(
            date_str=search_date,
            **kwargs
        )
        
        if data:
            parsed_times = parse_stonebridge_teetimes(data)
            results[search_date] = parsed_times
            display_stonebridge_times(parsed_times, search_date)
        
        # Be respectful - add delay between requests
        import time
        time.sleep(1)
    
    return results


def find_best_stonebridge_times(
    date_str: str = None,
    max_price: float = None,
    min_spots: int = 1,
    preferred_time: str = None,
    holes_preference: int = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Find the best Stonebridge tee times based on criteria
    
    Args:
        date_str: Date to search (MM-DD-YYYY format)
        max_price: Maximum total price willing to pay
        min_spots: Minimum number of spots needed
        preferred_time: Preferred time (HH:MM format)
        holes_preference: Preferred hole count (9 or 18)
        **kwargs: Additional parameters to pass to get_stonebridge_teetimes
    
    Returns:
        List of best matching tee times
    """
    data = get_stonebridge_teetimes(
        date_str=date_str,
        **kwargs
    )
    
    if not data:
        return []
    
    all_times = parse_stonebridge_teetimes(data)
    
    # Filter by basic criteria
    filtered_times = []
    for tee_time in all_times:
        spots = tee_time.get('available_spots', 0)
        price = tee_time.get('total_fee', 0)
        holes = tee_time.get('holes', 0)
        
        # Check basic criteria
        if spots >= min_spots:
            if max_price is None or price <= max_price:
                if holes_preference is None or holes == holes_preference:
                    filtered_times.append(tee_time)
    
    # If no preferred time, return all filtered times
    if not preferred_time or not filtered_times:
        return filtered_times
    
    # Sort by proximity to preferred time
    def time_proximity(t):
        t_time = t.get('time', '00:00')
        
        # Convert both to minutes for comparison
        pref_parts = preferred_time.split(':')
        pref_minutes = int(pref_parts[0]) * 60 + int(pref_parts[1]) if len(pref_parts) >= 2 else 0
        
        t_parts = t_time.split(':')
        t_minutes = int(t_parts[0]) * 60 + int(t_parts[1]) if len(t_parts) >= 2 else 0
        
        return abs(pref_minutes - t_minutes)
    
    return sorted(filtered_times, key=time_proximity)

# Example usage
# Example bearer token from your request headers
DEFAULT_BEARER_TOKEN = os.environ["STONEBRIDGE_BEARER"]

# Example cookie from your request headers
DEFAULT_COOKIE = os.environ["STONEBRIDGE_DEFAULT_COOKIE"]

if __name__ == "__main__":
    # Prepare date string
    date_str = "08-28-2025"
    
    print("=" * 50)
    print("EXAMPLE 1: Basic Search With Authentication")
    print("=" * 50)
    
    # Get tee times using the parameters from your URL and including authentication
    data = get_stonebridge_teetimes(
        schedule_id=9912,
        date_str=date_str,
        booking_class=13900,
        bearer_token=DEFAULT_BEARER_TOKEN,
        cookie=DEFAULT_COOKIE
    )
    
    if data:
        # Print raw JSON for first item
        print("\nRaw JSON Response (first item):")
        if len(data) > 0:
            print(json.dumps(data[0], indent=2))
        
        # Parse and display nicely
        parsed_times = parse_stonebridge_teetimes(data)
        display_stonebridge_times(parsed_times, date_str)
    
    print("\n" + "=" * 50)
    print("EXAMPLE 2: Find Best Times")
    print("=" * 50)
    
    # Find best times around 10:00 AM under $40
    best_times = find_best_stonebridge_times(
        date_str=date_str,
        max_price=40.0,
        preferred_time="10:00",
        min_spots=2,
        bearer_token=DEFAULT_BEARER_TOKEN,
        cookie=DEFAULT_COOKIE
    )
    
    if best_times:
        print(f"Found {len(best_times)} good tee times under $40 near 10:00 AM:")
        for i, time_slot in enumerate(best_times[:5]):  # Show top 5
            print(f"  {i+1}. {time_slot['time']} - {time_slot['course_name']} - ${time_slot['total_fee']:.0f} ({time_slot['available_spots']} spots)")
    else:
        print("No suitable tee times found matching criteria")
    
    print("\n" + "=" * 50)
    print("EXAMPLE 3: Search Multiple Days")
    print("=" * 50)
    
    # search_stonebridge_date_range(
    #     days_ahead=3,
    #     bearer_token=DEFAULT_BEARER_TOKEN,
    #     cookie=DEFAULT_COOKIE
    # )
    
