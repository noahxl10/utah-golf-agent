import requests
from datetime import date
import json
from typing import List, Dict, Any
import os


def get_bonneville_tee_times(day: str = None):
    if day is None:
        day = date.today().strftime("%Y-%m-%d")

    # one person
    url = os.environ["CHRONOGOLF_V1_ENDPOINT"]

    params = {
        "date": day,
        "holes": 18,
        "lang": "en"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    # response = requests.get(url, params=params, headers=headers)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    print(json.dumps(data, indent=2))

    # Parse the JSON data (assuming it's tee time data)
    if isinstance(data, list):
        tee_times = data
    else:
        tee_times = data.get('data', data)  # Handle different response formats

    # Parse and display the tee times nicely
    parsed_times = parse_tee_times(tee_times)
    # display_tee_times(parsed_times)

    return parsed_times


def parse_tee_times(tee_times_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse tee time JSON data into a clean format"""
    parsed_times = []

    for tee_time in tee_times_data:
        # Extract basic tee time info
        tee_info = {
            'id': tee_time.get('id'),
            'start_time': tee_time.get('start_time'),
            'date': tee_time.get('date'),
            'hole': tee_time.get('hole'),
            'round': tee_time.get('round'),
            'format': tee_time.get('format'),
            'available': not tee_time.get('out_of_capacity', True),
            'frozen': tee_time.get('frozen', False),
        }
        
        # Extract pricing information
        green_fees = tee_time.get('green_fees', [])
        if green_fees:
            fee_info = green_fees[0]  # Take first fee option
            tee_info.update({
                'green_fee': fee_info.get('green_fee', 0),
                'half_cart': fee_info.get('half_cart', 0),
                'subtotal': fee_info.get('subtotal', 0),
            })
        
        parsed_times.append(tee_info)
    
    return parsed_times


def display_tee_times(tee_times: List[Dict[str, Any]]) -> None:
    """Display tee times in a nice formatted way"""
    if not tee_times:
        print("No tee times found.")
        return
    
    print(f"\n{'='*80}")
    print(f"{'GOLF TEE TIMES':^80}")
    print(f"{'='*80}")
    print(f"Date: {tee_times[0].get('date', 'Unknown')}")
    print(f"{'='*80}")
    
    # Header
    print(f"{'Time':<8} {'Hole':<6} {'Green Fee':<12} {'Cart':<8} {'Total':<10} {'Status':<12}")
    print(f"{'-'*8} {'-'*6} {'-'*12} {'-'*8} {'-'*10} {'-'*12}")
    
    # Sort by start time
    sorted_times = sorted(tee_times, key=lambda x: x.get('start_time', ''))
    
    for tee_time in sorted_times:
        time = tee_time.get('start_time', 'N/A')
        hole = tee_time.get('hole', 'N/A')
        green_fee = f"${tee_time.get('green_fee', 0):.0f}"
        cart = f"${tee_time.get('half_cart', 0):.0f}"
        total = f"${tee_time.get('subtotal', 0):.0f}"
        
        # Determine status
        if tee_time.get('available', False):
            status = "✅ Available"
        else:
            status = "❌ Full"
            
        if tee_time.get('frozen', False):
            status += " (Frozen)"
        
        print(f"{time:<8} {hole:<6} {green_fee:<12} {cart:<8} {total:<10} {status:<12}")
    
    # Summary
    available_count = sum(1 for t in tee_times if t.get('available', False))
    total_count = len(tee_times)
    
    print(f"\n{'='*80}")
    print(f"Summary: {available_count}/{total_count} tee times available")
    if available_count > 0:
        avg_price = sum(t.get('subtotal', 0) for t in tee_times if t.get('available', False)) / available_count
        print(f"Average price for available slots: ${avg_price:.0f}")
    print(f"{'='*80}\n")


def test_with_sample_data():
    """Test the parser with the provided sample JSON data"""
    sample_data = [
        {'id': 446281294, 'course_id': 16298, 'start_time': '07:00', 'date': '2025-09-01', 'event_id': None, 'hole': 1, 'round': 1, 'format': 'normal', 'departure': None, 'restrictions': [], 'out_of_capacity': True, 'frozen': False, 'green_fees': [{'player_type_id': 57662, 'green_fee': 46.0, 'half_cart': 20.0, 'one_person_cart': None, 'subtotal': 66.0, 'teetime_id': 446281294, 'affiliation_type_id': 57662, 'price': 46.0, 'one_person_cart_price': None, 'half_cart_price': 20.0}]},
        {'id': 446281295, 'course_id': 16298, 'start_time': '07:10', 'date': '2025-09-01', 'event_id': None, 'hole': 1, 'round': 1, 'format': 'normal', 'departure': None, 'restrictions': [], 'out_of_capacity': True, 'frozen': False, 'green_fees': [{'player_type_id': 57662, 'green_fee': 46.0, 'half_cart': 20.0, 'one_person_cart': None, 'subtotal': 66.0, 'teetime_id': 446281295, 'affiliation_type_id': 57662, 'price': 46.0, 'one_person_cart_price': None, 'half_cart_price': 20.0}]},
        {'id': 446281296, 'course_id': 16298, 'start_time': '07:20', 'date': '2025-09-01', 'event_id': None, 'hole': 1, 'round': 1, 'format': 'normal', 'departure': None, 'restrictions': [], 'out_of_capacity': True, 'frozen': False, 'green_fees': [{'player_type_id': 57662, 'green_fee': 46.0, 'half_cart': 20.0, 'one_person_cart': None, 'subtotal': 66.0, 'teetime_id': 446281296, 'affiliation_type_id': 57662, 'price': 46.0, 'one_person_cart_price': None, 'half_cart_price': 20.0}]},
        {'id': 446281297, 'course_id': 16298, 'start_time': '07:30', 'date': '2025-09-01', 'event_id': None, 'hole': 1, 'round': 1, 'format': 'normal', 'departure': None, 'restrictions': [], 'out_of_capacity': True, 'frozen': False, 'green_fees': [{'player_type_id': 57662, 'green_fee': 46.0, 'half_cart': 20.0, 'one_person_cart': None, 'subtotal': 66.0, 'teetime_id': 446281297, 'affiliation_type_id': 57662, 'price': 46.0, 'one_person_cart_price': None, 'half_cart_price': 20.0}]}
    ]

    print("Testing with sample golf tee time data:")
    parsed_times = parse_tee_times(sample_data)
    display_tee_times(parsed_times)
    return parsed_times

if __name__ == "__main__":
    # Test with sample data first
    # print("\n" + "="*50)
    # print("TESTING WITH SAMPLE DATA")
    # print("="*50)
    # test_with_sample_data()

    # Uncomment below to test with live API
    print("\n" + "="*50)
    print("TESTING WITH LIVE API")
    print("="*50)
    day = "2025-09-01"  # example date
    get_bonneville_tee_times(day)
