import requests
import json
from datetime import date, datetime, timedelta
from typing import List, Optional
from urllib.parse import urlencode
import os


def get_chronogolf_teetimes(
    course_ids: List[str],
    start_date: str = None,
    holes: List[int] = [9, 18],
    page: int = 1,
    timeout: int = 10
) -> Optional[dict]:
    """
    Get tee times from ChronoGolf API for multiple courses
    
    Args:
        course_ids: List of course UUIDs
        start_date: Date in YYYY-MM-DD format (defaults to today)
        holes: List of hole counts to search for [9, 18]
        page: Page number for pagination
        timeout: Request timeout in seconds
    
    Returns:
        JSON response data or None if error
    """
    if start_date is None:
        start_date = date.today().strftime("%Y-%m-%d")
    
    base_url = os.environ["CHRONOGOLF_V2_ENDPOINT"]
    
    # Build query parameters
    params = {
        'start_date': start_date,
        'course_ids': ','.join(course_ids),
        'holes': ','.join(map(str, holes)),
        'page': page
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Golf Tee Time Scraper)',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        print(f"Requesting tee times for {len(course_ids)} courses on {start_date}")
        print(f"URL: {base_url}?{urlencode(params)}")
        
        response = requests.get(base_url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Success! Found {len(data.get('data', []))} tee times")
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


def search_multiple_courses():
    """Example: Search multiple courses"""
    course_ids = [
        "79c03256-be52-4e3d-aba8-9c64df6e12b2",  # Course 1
        "026599af-6569-4b0f-aaf9-aefedc607e3c",  # Course 2
    ]
    
    data = get_chronogolf_teetimes(
        course_ids=course_ids,
        start_date="2025-08-29",
        holes=[9, 18]
    )
    
    if data:
        print(json.dumps(data, indent=2))
        return data
    return None

def search_single_course():
    """Example: Search single course"""
    course_id = "79c03256-be52-4e3d-aba8-9c64df6e12b2"
    
    data = get_chronogolf_teetimes(
        course_ids=[course_id],
        start_date="2025-08-29"
    )
    
    if data:
        print(json.dumps(data, indent=2))
        return data
    return None

def search_date_range(course_ids: List[str], days_ahead: int = 7):
    """Search multiple dates for given courses"""
    results = {}
    
    for i in range(days_ahead):
        search_date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        print(f"\n📅 Searching for {search_date}")
        
        data = get_chronogolf_teetimes(
            course_ids=course_ids,
            start_date=search_date
        )
        
        if data:
            results[search_date] = data
        
        # Be respectful - add delay between requests
        import time
        time.sleep(1)
    
    return results

def search_with_pagination(course_ids: List[str], max_pages: int = 5):
    """Search with pagination to get all results"""
    all_results = []
    
    for page in range(1, max_pages + 1):
        print(f"\n📄 Page {page}")
        
        data = get_chronogolf_teetimes(
            course_ids=course_ids,
            page=page
        )
        
        if not data or not data.get('data'):
            print("No more data found")
            break
            
        all_results.extend(data['data'])
        
        # Check if there are more pages
        if len(data['data']) == 0:
            break
    
    print(f"\n🏌️ Total tee times found: {len(all_results)}")
    return all_results

# Golf course database (you'd want to expand this)
GOLF_COURSES = {
    "bonneville": "79c03256-be52-4e3d-aba8-9c64df6e12b2",
    "riverside": "026599af-6569-4b0f-aaf9-aefedc607e3c",
    # Add more courses here...
}

def search_by_course_name(course_names: List[str]):
    """Search by course name instead of UUID"""
    course_ids = []
    
    for name in course_names:
        if name.lower() in GOLF_COURSES:
            course_ids.append(GOLF_COURSES[name.lower()])
        else:
            print(f"⚠️  Course '{name}' not found in database")
    
    if course_ids:
        return get_chronogolf_teetimes(course_ids=course_ids)
    return None

def find_available_times(course_ids: List[str], max_price: float = None):
    """Find available tee times under a certain price"""
    data = get_chronogolf_teetimes(course_ids=course_ids)
    
    if not data:
        return []
    
    available_times = []
    
    for tee_time in data.get('data', []):
        # Check if tee time is available (not full)
        if not tee_time.get('out_of_capacity', True):
            price = None
            green_fees = tee_time.get('green_fees', [])
            if green_fees:
                price = green_fees[0].get('subtotal', 0)
            
            # Filter by price if specified
            if max_price is None or (price and price <= max_price):
                available_times.append({
                    'time': tee_time.get('start_time'),
                    'date': tee_time.get('date'),
                    'price': price,
                    'course_id': tee_time.get('course_id'),
                    'id': tee_time.get('id')
                })
    
    return available_times

# Example usage
if __name__ == "__main__":
    # Example 1: Search multiple courses
    print("=" * 50)
    print("EXAMPLE 1: Multiple Courses")
    print("=" * 50)
    search_multiple_courses()
    
    # Example 2: Search by course name
    print("\n" + "=" * 50)
    print("EXAMPLE 2: Search by Name")
    print("=" * 50)
    search_by_course_name(["bonneville", "riverside"])
    
    # Example 3: Find available times under $70
    print("\n" + "=" * 50)
    print("EXAMPLE 3: Available Times Under $70")
    print("=" * 50)
    course_ids = ["79c03256-be52-4e3d-aba8-9c64df6e12b2"]
    available = find_available_times(course_ids, max_price=70.0)
    for time_slot in available:
        print(f"{time_slot['date']} at {time_slot['time']} - ${time_slot['price']}")
    
    # Example 4: Search next 3 days
    print("\n" + "=" * 50)
    print("EXAMPLE 4: Next 3 Days")
    print("=" * 50)
    search_date_range(course_ids, days_ahead=3)