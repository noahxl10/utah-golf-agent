import sys
import json
from datetime import datetime, timedelta
from stonebridge_auth import get_bearer_token, get_auth_headers
from stonebridge import get_stonebridge_teetimes, parse_stonebridge_teetimes, display_stonebridge_times
import os


def search_tee_times_with_auth(
    date_str: str = None,
    days_ahead: int = 0,
    force_refresh_token: bool = False,
    time_filter: str = "all",
    holes_filter: str = "all",
    players: int = 0
):
    """
    Search for tee times with automatic authentication
    
    Args:
        date_str: Date in MM-DD-YYYY format (defaults to today + days_ahead)
        days_ahead: Days to add to today's date (ignored if date_str is provided)
        force_refresh_token: Force a new login even if cached token exists
        time_filter: Time filter ("all", "morning", "afternoon", "evening")
        holes_filter: Hole filter ("all", "9", "18")
        players: Number of players (0 for any)
    """
    # Get authentication headers
    print("Getting authentication headers...")
    auth_headers = get_auth_headers(force_refresh=force_refresh_token)
    
    if not auth_headers:
        print("❌ Authentication failed. Cannot proceed.")
        return
    
    bearer_token = auth_headers.get('X-Authorization', '').replace('Bearer ', '')
    cookie = auth_headers.get('Cookie', '')
    
    # Calculate date if not provided
    if not date_str:
        target_date = datetime.now() + timedelta(days=days_ahead)
        date_str = target_date.strftime("%m-%d-%Y")
    
    print(f"\nSearching for tee times on {date_str}...")
    
    # Get tee times
    data = get_stonebridge_teetimes(
        date_str=date_str,
        bearer_token=bearer_token,
        cookie=cookie,
        time=time_filter,
        holes=holes_filter,
        players=players
    )
    
    if not data:
        print("❌ No tee times found or API request failed.")
        return
    
    # Parse and display
    parsed_times = parse_stonebridge_teetimes(data)
    display_stonebridge_times(parsed_times, date_str)
    
    return parsed_times


def search_next_days(num_days: int = 7, **kwargs):
    """
    Search for tee times over the next several days
    
    Args:
        num_days: Number of days to search
        **kwargs: Additional search parameters
    """
    print(f"Searching for tee times over the next {num_days} days")
    print("=" * 60)
    
    results = {}
    
    for i in range(num_days):
        target_date = datetime.now() + timedelta(days=i)
        date_str = target_date.strftime("%m-%d-%Y")
        day_name = target_date.strftime("%A")
        
        print(f"\n{'='*60}")
        print(f"DAY {i+1}: {day_name.upper()} - {date_str}")
        print(f"{'='*60}")
        
        parsed_times = search_tee_times_with_auth(
            date_str=date_str,
            force_refresh_token=(i == 0),  # Only force refresh on first day
            **kwargs
        )
        
        results[date_str] = parsed_times
        
        # Don't hammer the API - add a delay between requests
        if i < num_days - 1:
            import time
            print("Waiting before next request...")
            time.sleep(2)
    
    return results


def find_best_deals(results, max_price=None, min_spots=1):
    """Find the best deals across all search results"""
    best_deals = []
    
    for date_str, times in results.items():
        if not times:
            continue
            
        # Filter by criteria
        for tee_time in times:
            price = tee_time.get('total_fee', 0)
            spots = tee_time.get('available_spots', 0)
            special = tee_time.get('has_special', False)
            
            if spots >= min_spots:
                if max_price is None or price <= max_price:
                    # Add date to the tee time object for reference
                    tee_time_with_date = tee_time.copy()
                    tee_time_with_date['date_str'] = date_str
                    best_deals.append(tee_time_with_date)
    
    # Sort by price, then by date, then by time
    sorted_deals = sorted(best_deals, key=lambda x: (
        x.get('total_fee', 0),
        x.get('date_str', ''),
        x.get('time', '')
    ))
    
    return sorted_deals


def display_best_deals(deals):
    """Display the best deals in a nice format"""
    if not deals:
        print("No deals found matching criteria.")
        return
        
    print("\n" + "=" * 100)
    print(f"{'BEST TEE TIME DEALS':^100}")
    print("=" * 100)
    
    # Header
    print(f"{'Rank':<6} {'Date':<12} {'Time':<8} {'Course':<30} {'Holes':<7} {'Price':<12} {'Spots':<7} {'Special':<10}")
    print(f"{'-'*6} {'-'*12} {'-'*8} {'-'*30} {'-'*7} {'-'*12} {'-'*7} {'-'*10}")
    
    # Display deals
    for i, deal in enumerate(deals):
        # Convert date from MM-DD-YYYY to a more readable format
        date_parts = deal.get('date_str', '').split('-')
        if len(date_parts) == 3:
            date_obj = datetime.strptime(deal.get('date_str', ''), '%m-%d-%Y')
            date_display = date_obj.strftime('%a, %b %d')  # e.g., "Mon, Aug 28"
        else:
            date_display = deal.get('date_str', '')
            
        rank = f"#{i+1}"
        time = deal.get('time', '')
        course = (deal.get('course_name', '')).strip()[:28]
        holes = str(deal.get('holes', ''))
        price = f"${deal.get('total_fee', 0):.0f}"
        spots = str(deal.get('available_spots', 0))
        special = "⭐ Yes" if deal.get('has_special', False) else ""
        
        print(f"{rank:<6} {date_display:<12} {time:<8} {course:<30} {holes:<7} {price:<12} {spots:<7} {special:<10}")
    
    print("=" * 100)

if __name__ == "__main__":
    print("=" * 60)
    print("STONEBRIDGE GOLF CLUB TEE TIME FINDER")
    print("=" * 60)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("\nUsage options:")
            print("  python stonebridge_integration.py [days] [max_price]")
            print("  python stonebridge_integration.py today")
            print("  python stonebridge_integration.py weekend")
            print("  python stonebridge_integration.py 7 50")
            print("\nExamples:")
            print("  python stonebridge_integration.py         # Search today")
            print("  python stonebridge_integration.py 3       # Search next 3 days")
            print("  python stonebridge_integration.py 7 40    # Search next 7 days, max $40")
            print("  python stonebridge_integration.py weekend # Search upcoming weekend")
            sys.exit(0)
        
        if sys.argv[1].lower() == "today":
            # Search just today
            search_tee_times_with_auth(days_ahead=0, force_refresh_token=True)
            sys.exit(0)
            
        if sys.argv[1].lower() == "weekend":
            # Find the next Saturday and Sunday
            today = datetime.now()
            days_to_saturday = (5 - today.weekday()) % 7
            if days_to_saturday == 0 and today.hour >= 12:
                # If it's already Saturday afternoon, start with next Saturday
                days_to_saturday = 7
                
            print("Searching for weekend tee times")
            results = {}
            
            # Saturday
            saturday = today + timedelta(days=days_to_saturday)
            saturday_str = saturday.strftime("%m-%d-%Y")
            print(f"\nSaturday: {saturday_str}")
            saturday_times = search_tee_times_with_auth(
                date_str=saturday_str,
                force_refresh_token=True
            )
            results[saturday_str] = saturday_times
            
            # Sunday
            sunday = today + timedelta(days=days_to_saturday + 1)
            sunday_str = sunday.strftime("%m-%d-%Y")
            print(f"\nSunday: {sunday_str}")
            sunday_times = search_tee_times_with_auth(
                date_str=sunday_str
            )
            results[sunday_str] = sunday_times
            
            # Find best deals across the weekend
            max_price = 100
            if len(sys.argv) > 2 and sys.argv[2].isdigit():
                max_price = int(sys.argv[2])
                
            best_deals = find_best_deals(results, max_price=max_price)
            display_best_deals(best_deals)
            
            sys.exit(0)
    
    # Default behavior - search multiple days
    days_to_search = 1  # Default to just today
    max_price = None
    
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        days_to_search = int(sys.argv[1])
        
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        max_price = int(sys.argv[2])
    
    # Run the search
    if days_to_search == 1:
        search_tee_times_with_auth(force_refresh_token=True)
    else:
        results = search_next_days(
            num_days=days_to_search,
            force_refresh_token=True
        )
        
        # Find and display best deals
        best_deals = find_best_deals(results, max_price=max_price)
        display_best_deals(best_deals)
